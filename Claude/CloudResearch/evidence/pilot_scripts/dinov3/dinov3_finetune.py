"""Phase 2 of the DINOv3 benchmark: fine-tuning DINOv3 (SAT-493M) on the 186 training tiles only. Research only.

Not part of the library (Justin, 2026-10-26: "we will not use dinov3 in the library, it is only for research and
benchmarking our other models"). Imports the library and dinov3_bench; nothing in the library imports it.
Checkpoints and caches go in ~/Masters/models/finetuned/dinov3_sat493m/, never in a repo.

Design (outputs/preregistration_dinov3_baseline.md, "Phase 2"):
- Frozen trunk: the first TRUNK_DEPTH = 20 of the 24 blocks run once per window (2 x 2 windows per date, as
  dinov3_bench.tokens3) and their outputs (class + 4 register + patch tokens) are cached (before image float32, after
  image float16). Only the blocks
  after the trunk and a head are trained, on the cached trunk outputs, so a training epoch is cheap on MPS. No image
  augmentation (the cached trunk outputs fix the view).
- Each date is read with its own valid mask (that date's no-data, eroded 6 px), so one before-image cache serves both
  tracks; Track B's strips stay on pixels valid on both dates, as the library's.
- Track A (finding roads): the last 4 blocks + LayerNorm trained ("A-ft") or frozen ("A-head"), then a linear head
  from each 16 px patch token to its 4 x 4 grid of 2 m cells (logits). Target: sn8_detect's cell labels (road within
  3.5 m of a labelled centreline, not road beyond 8 m, the rest and partly valid cells ignored), every labelled cell.
- Track B (flood per road): the same last blocks shared by both dates (siamese), the last 2 trained ("B-ft") or none
  ("B-head"), then an MLP on [before, after, after - before] per patch to its 4 x 4 cells. Target: each 2 m cell whose
  centre lies in a road strip (sn8_roads' strip, nearest road, both dates valid) takes that road's published flooded
  attribute; only the roads production's cloud rule assesses are targets, every other cell is ignored.
- Per-road cues from a probability grid, with the library's strip weights at 2 m cells: the strip-weighted mean, the
  max over cells holding at least a quarter cell of strip, and the strip share at p >= 0.5.
"""
import copy
import hashlib
import inspect
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))
import dinov3_bench as d3   # puts ClaudeFunctions on sys.path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import ndimage as ndi

from sn8 import tile
from sn8_data import guard_split
from sn8_detect import CELL_PX, NOT_ROAD_M, ROAD_HALF_M
from sn8_lines import NODATA_ERODE_PX, road_band, road_mask
from sn8_roads import MIN_ROAD_PX, _road_lines
from sn8_torchgeo import RES, tile_pair

FT_DIR = Path.home() / "Masters" / "models" / "finetuned" / "dinov3_sat493m"
TRUNK_DEPTH = 20
SUB = d3.PATCH3 // CELL_PX            # 4 x 4 cells of 2 m per 16 px patch
SEED = 662
MAX_CELL_SHARE = 0.25                 # cue max: cells holding at least this share of a cell of strip


def _src_hash(*fns):
    return hashlib.sha256("".join(inspect.getsource(f) for f in fns).encode()).hexdigest()[:12]


def _split_of(tile_id):
    from sn8_grey import GREY_DIR
    return next(GREY_DIR.glob(f"*/pre/{tile_id}.tif")).parents[1].name


def run_trunk(grey, valid, dtype=np.float16):
    """The first TRUNK_DEPTH blocks of the frozen DINOv3 on each window of one image: a list of (n_tokens, 1024)
    arrays (prefix tokens first) in `dtype`, plus the patch grid (n_rows, n_cols)."""
    model, device, mean, std = d3.backbone3()
    x = d3.normalised3(grey, valid, mean, std)
    n_r, n_c = x.shape[1] // d3.PATCH3, x.shape[2] // d3.PATCH3
    out = []
    with torch.inference_mode():
        for r, c in d3.windows3(n_r, n_c):
            win = x[:, r[0] * d3.PATCH3:(r[-1] + 1) * d3.PATCH3, c[0] * d3.PATCH3:(c[-1] + 1) * d3.PATCH3]
            h = model.patch_embed(torch.from_numpy(win[None]).to(device))
            h, rope = model._pos_embed(h)
            h = model.norm_pre(h)
            for blk in model.blocks[:TRUNK_DEPTH]:
                h = blk(h, rope=rope)
            h = h[0].float()
            assert torch.isfinite(h).all() and h.abs().max() < 6e4, "trunk output outside float16 range"
            out.append(h.cpu().numpy().astype(dtype))
    return out, (n_r, n_c)


def trunk_dir():
    _, _, mean, std = d3.backbone3()
    key = hashlib.sha256(json.dumps([d3.MODEL3, TRUNK_DEPTH, d3.WINDOWS3, list(mean), list(std), NODATA_ERODE_PX,
                                     _src_hash(run_trunk, d3.normalised3, d3.windows3),
                                     {k: np.dtype(v).name for k, v in TRUNK_DTYPE.items()}]).encode()).hexdigest()[:12]
    return FT_DIR / f"trunk{TRUNK_DEPTH}_{key}"


TRUNK_DTYPE = {"before": np.float32, "after": np.float16}   # before in float32: it also gives phase 1's exact tokens


def trunk(tile_id, date):
    """Cached trunk outputs of one date ("before" or "after") of a development tile: {"windows": [...], "grid":
    (n_r, n_c)}. The before image is kept in float32 (dinov3_bench's Track A tokens come from it exactly), the after
    image in float16. Test and negative tiles refuse (guard_split)."""
    guard_split(_split_of(tile_id))
    path = trunk_dir() / f"{tile_id}_{date}.npz"
    if not path.exists():
        p = tile_pair(tile_id)
        grey = p[f"{date}_grey"]
        valid = ndi.binary_erosion(grey > 0, iterations=NODATA_ERODE_PX)
        wins, grid = run_trunk(grey, valid, TRUNK_DTYPE[date])
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, grid=np.array(grid), **{f"w{k}": w for k, w in enumerate(wins)})
    z = np.load(path)
    n = sum(1 for k in z.files if k.startswith("w"))
    return {"windows": [z[f"w{k}"] for k in range(n)], "grid": tuple(int(v) for v in z["grid"])}


# ---------- targets (from the published labels only) ----------

def road_cell_grid(tile_id, grid):
    """Track A target on the padded cell grid (n_r * 4, n_c * 4): 1 road, 0 not road, -1 ignored (left-out band,
    partly valid cells, padding), as sn8_detect.tile_cells labels cells."""
    p = tile_pair(tile_id)
    valid = ndi.binary_erosion(p["before_grey"] > 0, iterations=NODATA_ERODE_PX)
    roads = road_mask(tile(tile_id)["label"], (p["x0"], p["y0"]), valid.shape)
    dist = ndi.distance_transform_edt(~roads) * RES if roads.any() else np.full(valid.shape, np.inf)
    n_rows, n_cols = valid.shape[0] // CELL_PX, valid.shape[1] // CELL_PX
    full = valid[: n_rows * CELL_PX, : n_cols * CELL_PX].reshape(n_rows, CELL_PX, n_cols, CELL_PX).all(axis=(1, 3))
    centre = dist[CELL_PX // 2::CELL_PX, CELL_PX // 2::CELL_PX][:n_rows, :n_cols]
    label = np.where(centre <= ROAD_HALF_M, 1, np.where(centre > NOT_ROAD_M, 0, -1))
    label[~full] = -1
    out = np.full((grid[0] * SUB, grid[1] * SUB), -1, np.int8)
    out[:n_rows, :n_cols] = label
    return out


def strip_layout(tile_id, band_m):
    """Road strips of a tile at 2 m cells: (rows of the tile's roads that the library keeps, in feature_table order,
    as (k, road_id, flooded)), the (n_kept, n_cells) strip weights, the centre-pixel owner of every cell (road index,
    0 none) and the cell grid's column count. Strip = sn8_roads' (within band_m of the nearest road's centreline,
    both dates valid)."""
    p = tile_pair(tile_id)
    valid = ndi.binary_erosion((p["before_grey"] > 0) & (p["after_grey"] > 0), iterations=NODATA_ERODE_PX)
    seg, _, seg_road, roads = _road_lines(tile(tile_id)["label"], (p["x0"], p["y0"]), valid.shape)
    n_r, n_c = -(-valid.shape[0] // d3.PATCH3), -(-valid.shape[1] // d3.PATCH3)
    cells_c, cells_r = n_c * SUB, n_r * SUB
    if len(roads) == 1:
        return [], np.zeros((0, cells_r * cells_c)), np.zeros((cells_r, cells_c), np.int64), cells_c
    weight, centre_px = d3.strip_weights(seg, seg_road, roads, valid, band_m, cells_c, cells_r * cells_c, patch=CELL_PX)
    dist, (ni, nj) = ndi.distance_transform_edt(seg == 0, return_indices=True)
    owner = np.where((dist * RES <= band_m) & valid, seg_road[seg[ni, nj]], 0)
    cell_owner = np.zeros((cells_r, cells_c), np.int64)
    centre = owner[CELL_PX // 2::CELL_PX, CELL_PX // 2::CELL_PX]
    cell_owner[: centre.shape[0], : centre.shape[1]] = centre
    keep = [k for k in range(len(roads) - 1) if centre_px[k] >= MIN_ROAD_PX]
    rows = [(k, roads[k + 1]["road_id"], bool(roads[k + 1]["flooded"])) for k in keep]
    return rows, weight[keep], cell_owner, cells_c


def flood_cell_grid(layout, targets):
    """Track B target on the padded cell grid: 1 / 0 (the owner road's flooded attribute) for cells whose centre lies
    in the strip of a kept road whose position in the layout's rows is in `targets` (positions, not road ids: one
    road id can occur twice on a tile), -1 elsewhere."""
    rows, _, cell_owner, _ = layout
    flooded = np.full(cell_owner.max() + 2, -1, np.int8)
    for i, (k, rid, f) in enumerate(rows):
        if i in targets:
            flooded[k + 1] = int(f)
    flooded[0] = -1
    return flooded[cell_owner]


def road_cues(layout, prob, prefix):
    """Per kept road of the tile: the strip-weighted mean of the cell probabilities, the max over cells holding at
    least a quarter cell of strip, and the strip share at p >= 0.5. `prob` is the padded cell grid (NaN allowed off
    the strips)."""
    rows, weight, _, _ = layout
    if not rows:
        return []
    p = np.nan_to_num(prob.ravel(), nan=0.0)
    total = weight.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = (weight @ p) / total
        high = (weight @ (p >= 0.5)) / total
    big = weight >= MAX_CELL_SHARE * CELL_PX * CELL_PX
    mx = np.where(big.any(1), np.where(big, p[None, :], -np.inf).max(1), np.nan)
    return [{"road_id": rid, f"{prefix}_mean": float(mean[i]), f"{prefix}_max": float(mx[i]),
             f"{prefix}_share": float(high[i])} for i, (_, rid, _) in enumerate(rows)]


# ---------- networks ----------

class Top(nn.Module):
    """The blocks after the trunk and the final LayerNorm, copied from the frozen model: the first `n_frozen` stay
    frozen, the rest train. Returns the patch tokens (prefix tokens dropped)."""

    def __init__(self, n_frozen):
        super().__init__()
        model = d3.backbone3()[0]
        blocks = list(model.blocks[TRUNK_DEPTH:])
        self.frozen = nn.ModuleList(copy.deepcopy(b) for b in blocks[:n_frozen])
        self.trained = nn.ModuleList(copy.deepcopy(b) for b in blocks[n_frozen:])
        self.norm = copy.deepcopy(model.norm)
        self.rope, self.npt = model.rope, model.num_prefix_tokens
        for prm in self.frozen.parameters():
            prm.requires_grad_(False)
        if not len(self.trained):
            for prm in self.norm.parameters():
                prm.requires_grad_(False)

    def forward(self, h, grid):
        rope = self.rope.get_embed(shape=grid)
        with torch.no_grad():
            for b in self.frozen:
                h = b(h, rope=rope)
        for b in self.trained:
            h = b(h, rope=rope)
        return self.norm(h)[:, self.npt:]


def unpatch(logits, n_r, n_c):
    """(n_r * n_c, 16) per-patch logits to the (n_r * 4, n_c * 4) cell grid."""
    return logits.reshape(n_r, n_c, SUB, SUB).permute(0, 2, 1, 3).reshape(n_r * SUB, n_c * SUB)


class RoadHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.lin = nn.Linear(d3.DIM3, SUB * SUB)

    def forward(self, tok):
        return self.lin(tok)


class FloodHead(nn.Module):
    def __init__(self, hidden=256, drop=0.1):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3 * d3.DIM3, hidden), nn.GELU(), nn.Dropout(drop), nn.Linear(hidden, SUB * SUB))

    def forward(self, tb, ta):
        return self.net(torch.cat([tb, ta, ta - tb], -1))


def trainable(*modules):
    return [p for m in modules for p in m.parameters() if p.requires_grad]


def window_slices(grid):
    return [(r, c, slice(r[0] * SUB, (r[-1] + 1) * SUB), slice(c[0] * SUB, (c[-1] + 1) * SUB))
            for r, c in d3.windows3(*grid)]


def predict_grid(top, head, tile_id, track, device):
    """The cell-probability grid of one tile from a top + head (eval mode, no grad)."""
    top.eval()
    head.eval()
    tb = trunk(tile_id, "before")
    ta = trunk(tile_id, "after") if track == "B" else None
    grid = tb["grid"]
    prob = np.zeros((grid[0] * SUB, grid[1] * SUB), np.float32)
    with torch.no_grad():
        for k, (r, c, rs, cs) in enumerate(window_slices(grid)):
            hb = torch.from_numpy(tb["windows"][k][None].astype(np.float32)).to(device)
            fb = top(hb, (len(r), len(c)))[0]
            if track == "A":
                logit = head(fb)
            else:
                ha = torch.from_numpy(ta["windows"][k][None].astype(np.float32)).to(device)
                logit = head(fb, top(ha, (len(r), len(c)))[0])
            prob[rs, cs] = torch.sigmoid(unpatch(logit, len(r), len(c))).cpu().numpy()
    return prob


def masked_bce(logit_grid, target):
    m = target >= 0
    if not m.any():
        return None, 0
    return F.binary_cross_entropy_with_logits(logit_grid[m], target[m].float(), reduction="sum"), int(m.sum())


def target_windows(tile_id, targets):
    """Indices of the tile's windows that hold at least one target cell."""
    grid = (targets[tile_id].shape[0] // SUB, targets[tile_id].shape[1] // SUB)
    return [k for k, (_, _, rs, cs) in enumerate(window_slices(grid)) if (targets[tile_id][rs, cs] >= 0).any()]


def eval_windows(tiles, targets, per_tile=2, seed=SEED):
    """A fixed, seeded subset of each tile's target windows for the per-epoch evaluation (up to `per_tile`)."""
    rng = np.random.default_rng(seed)
    out = {}
    for t in tiles:
        w = target_windows(t, targets)
        if w:
            out[t] = sorted(rng.choice(w, min(per_tile, len(w)), replace=False).tolist())
    return out


def train_epochs(track, fit_tiles, eval_win, targets, n_frozen, epochs, lr_blocks, lr_head, device, log,
                 patience=None, ckpt=None, seed=SEED, epoch_seconds=None, windows_per_tile=1):
    """Train a Top(n_frozen) + head on fit_tiles for up to `epochs` epochs. An epoch takes `windows_per_tile` random
    windows (of those holding target cells) from every fit tile, one optimiser step per tile with the loss averaged
    over the chosen windows' target cells (AdamW, gradient norm clipped at 1). After each epoch the masked BCE on the
    fixed evaluation windows `eval_win` ({tile: [window indices]}, or None) is logged; with `patience`, training stops
    after that many epochs without a lower evaluation loss and the best epoch's weights are kept. `targets[tile_id]` is
    the padded cell target grid. Returns (top, head, history)."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    top = Top(n_frozen).to(device)
    head = (RoadHead() if track == "A" else FloodHead()).to(device)
    groups = [{"params": trainable(head), "lr": lr_head, "weight_decay": 1e-4}]
    if trainable(top):
        groups.append({"params": trainable(top), "lr": lr_blocks, "weight_decay": 0.05})
    opt = torch.optim.AdamW(groups)
    history, best, best_state, waited = [], np.inf, None, 0
    for epoch in range(1, epochs + 1):
        t = time.time()
        top.train()
        head.train()
        top.frozen.eval()
        total, n_cells = 0.0, 0
        for tile_id in rng.permutation(fit_tiles):
            wins = target_windows(tile_id, targets)
            if not wins:
                continue
            chosen = set(rng.choice(wins, min(windows_per_tile, len(wins)), replace=False).tolist())
            target = torch.from_numpy(targets[tile_id].astype(np.int64)).to(device)
            tb = trunk(tile_id, "before")
            ta = trunk(tile_id, "after") if track == "B" else None
            opt.zero_grad()
            slices = window_slices(tb["grid"])
            denom = int(sum((target[slices[k][2], slices[k][3]] >= 0).sum() for k in chosen))
            for k, (r, c, rs, cs) in enumerate(slices):
                if k not in chosen:
                    continue
                tw = target[rs, cs]
                hb = torch.from_numpy(tb["windows"][k][None].astype(np.float32)).to(device)
                fb = top(hb, (len(r), len(c)))[0]
                if track == "A":
                    logit = head(fb)
                else:
                    ha = torch.from_numpy(ta["windows"][k][None].astype(np.float32)).to(device)
                    logit = head(fb, top(ha, (len(r), len(c)))[0])
                loss, n = masked_bce(unpatch(logit, len(r), len(c)), tw)
                (loss / denom).backward()
                total += float(loss.detach())
                n_cells += n
            torch.nn.utils.clip_grad_norm_(trainable(top, head), 1.0)
            opt.step()
        row = {"epoch": epoch, "train loss": total / max(n_cells, 1), "seconds": round(time.time() - t, 1)}
        if eval_win:
            row["eval loss"] = eval_loss(top, head, track, eval_win, targets, device)
        history.append(row)
        log(f"{track} n_frozen={n_frozen} epoch {epoch}: " + ", ".join(f"{k} {v:.4f}" if isinstance(v, float) else
                                                                       f"{k} {v}" for k, v in row.items()))
        if epoch_seconds is not None:
            epoch_seconds.append(row["seconds"])
        if patience is not None:
            if row["eval loss"] < best:
                best, waited = row["eval loss"], 0
                best_state = (copy.deepcopy(top.state_dict()), copy.deepcopy(head.state_dict()), epoch)
            else:
                waited += 1
                if waited >= patience:
                    break
    if best_state is not None:
        top.load_state_dict(best_state[0])
        head.load_state_dict(best_state[1])
    if ckpt is not None:
        ckpt.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"top_trained": {k: v for k, v in top.state_dict().items() if not k.startswith("frozen.")},
                    "head": head.state_dict(), "history": history, "n_frozen": n_frozen, "track": track,
                    "best epoch": best_state[2] if best_state else epochs, "model": d3.MODEL3,
                    "trunk depth": TRUNK_DEPTH}, ckpt)
    return top, head, history


def eval_loss(top, head, track, eval_win, targets, device):
    """Masked BCE per target cell over the windows {tile: [window indices]}."""
    total, n = 0.0, 0
    top.eval()
    head.eval()
    with torch.no_grad():
        for tile_id, keep in eval_win.items():
            target = torch.from_numpy(targets[tile_id].astype(np.int64)).to(device)
            if not (target >= 0).any():
                continue
            tb = trunk(tile_id, "before")
            ta = trunk(tile_id, "after") if track == "B" else None
            for k, (r, c, rs, cs) in enumerate(window_slices(tb["grid"])):
                tw = target[rs, cs]
                if k not in keep or not (tw >= 0).any():
                    continue
                hb = torch.from_numpy(tb["windows"][k][None].astype(np.float32)).to(device)
                fb = top(hb, (len(r), len(c)))[0]
                if track == "A":
                    logit = head(fb)
                else:
                    ha = torch.from_numpy(ta["windows"][k][None].astype(np.float32)).to(device)
                    logit = head(fb, top(ha, (len(r), len(c)))[0])
                loss, m = masked_bce(unpatch(logit, len(r), len(c)), tw)
                total += float(loss)
                n += m
    return total / max(n, 1)
