"""DINOv3 (SAT-493M) as a research benchmark for the library's models (DINOv2 + classical). Not part of the library.

Justin, 2026-10-26: "we will not use dinov3 in the library, it is only for research and benchmarking our other models".
This module lives in the research folder only. It imports the GeoAI-Roads library (ClaudeFunctions); nothing there
imports it. Caches go in this folder's .cache/, never in the repo.

    import sys; sys.path.append("/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/dinov3")
    from dinov3_bench import dino3_table, dino3_vectors, with_dino3, cell_dino3_table, DINO3_CUES, DINO3_VECTOR

    roads = with_dino3(with_dino(touched_roads(include_cloudy=True)))   # adds DINO3_CUES and the after - before vector
    cells = cell_dino3_table("train")    # sn8_detect.cell_table("train") with DINO3_CELL_FEATURES added

Mirrors sn8_dino (Track B) and sn8_dino_cells (Track A), with DINOv3 in place of DINOv2:
- Backbone: timm vit_large_patch16_dinov3.sat493m, DINOv3 ViT-L/16 (Simeoni et al., 2025, Meta), pretrained on the
  SAT-493M satellite set, read offline from ~/Masters/models/huggingface, run on the Mac GPU (MPS). Frozen. Licence:
  Meta's DINOv3 License (timm "dinov3-license"), not Apache-2.0 like the DINOv2 weights: research use here only.
- Input: the tile_pair greyscale repeated to 3 channels and normalised with the checkpoint's own timm data config
  (mean 0.430 / 0.411 / 0.296, std 0.213 / 0.156 / 0.143). No-data is filled with the date's valid mean. Each date runs
  as a 2 x 2 grid of windows (multiples of 16 px, about 688 x 608 px). A patch is 16 px = 8 m. The class token and the
  4 register tokens are dropped.
- Track B cues per road strip, as sn8_dino.lines_dino: dino3_change_pooled / _mean / _max and the pooled 1,024-d
  tokens of each date (their after - before difference is DINO3_VECTOR).
- Track A: before-image tokens reduced to 32 PCs fitted on 300 seeded patches per training tile (training tiles only),
  interpolated bilinearly to the 0.5 m grid and read at each 2 m cell centre, as sn8_dino_cells.
"""
import hashlib
import inspect
import json
import os
import sys
from functools import lru_cache
from pathlib import Path

FUNCS = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
if FUNCS not in sys.path:
    sys.path.append(FUNCS)

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

from sn8 import tile
from sn8_data import SPLIT_FINGERPRINT, guard_split
from sn8_detect import CELL_PX, cell_table
from sn8_dino import MAX_MIN_SHARE, MODELS_DIR, ReduceColumns, _cosine_change
from sn8_dino_cells import CELL_SAMPLE, DINO_CELL_PCS, SEED
from sn8_grey import GREY_DIR
from sn8_lines import NODATA_ERODE_PX, draw_roads, road_band
from sn8_roads import MIN_ROAD_PX, _road_lines, feature_table
from sn8_torchgeo import RES, tile_pair

MODEL3 = "vit_large_patch16_dinov3.sat493m"
LICENCE3 = "Meta DINOv3 License (timm license tag 'dinov3-license'); research use only here, not Apache-2.0"
PATCH3 = 16                       # 16 px = 8 m
WINDOWS3 = 2                      # windows per side (shrink the windows by raising this if MPS runs out of memory)
DIM3 = 1024
DINO3_CUES = ["dino3_change_pooled", "dino3_change_mean", "dino3_change_max"]
DINO3_VECTOR = [f"dino3_d{k}" for k in range(DIM3)]
DINO3_CELL_FEATURES = [f"dino3_pc{k}" for k in range(DINO_CELL_PCS)]
CREDIT3 = "Imagery: Maxar via SpaceNet 8 (SpaceNet LLC), CC BY-SA 4.0"
HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / ".cache"


@lru_cache(maxsize=1)
def backbone3():
    """The frozen DINOv3 model on the Mac GPU (CPU if MPS is missing), from the local weights only, and the
    normalisation of its own timm data config. Returns (model, device, mean, std)."""
    os.environ.setdefault("HF_HOME", str(MODELS_DIR))
    os.environ["HF_HUB_OFFLINE"] = "1"
    import timm
    import torch
    weights = next((MODELS_DIR / "hub" / f"models--timm--{MODEL3}" / "snapshots").glob("*/model.safetensors"))
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    model = timm.create_model(MODEL3, pretrained=True, pretrained_cfg_overlay={"file": str(weights)}, num_classes=0,
                              dynamic_img_size=True)
    cfg = timm.data.resolve_data_config({}, model=model)
    return model.eval().to(device), device, tuple(cfg["mean"]), tuple(cfg["std"])


def normalised3(grey, valid, mean, std):
    """The greyscale image (0-255) padded at the bottom and right to whole 16 px patches (no-data and padding take the
    valid mean), repeated to 3 channels and normalised: a (3, n_rows * 16, n_cols * 16) float32 array."""
    n_r, n_c = -(-grey.shape[0] // PATCH3), -(-grey.shape[1] // PATCH3)
    g = np.full((n_r * PATCH3, n_c * PATCH3), grey[valid].mean(), np.float32)
    g[: grey.shape[0], : grey.shape[1]] = np.where(valid, grey, grey[valid].mean())
    return np.stack([(g / 255 - m) / s for m, s in zip(mean, std)]).astype(np.float32)


def windows3(n_r, n_c, windows=WINDOWS3):
    """The window grid over the patch grid: a list of (patch rows, patch cols) index arrays, as sn8_dino.tokens."""
    rows, cols = np.array_split(np.arange(n_r), windows), np.array_split(np.arange(n_c), windows)
    return [(r, c) for r in rows for c in cols]


def tokens3(grey, valid):
    """The patch tokens of one greyscale image (0-255) as an (n_rows, n_cols, 1024) float32 array, one per 16 px patch,
    from a WINDOWS3 x WINDOWS3 grid of windows."""
    import torch
    model, device, mean, std = backbone3()
    x = normalised3(grey, valid, mean, std)
    n_r, n_c = x.shape[1] // PATCH3, x.shape[2] // PATCH3
    out = np.zeros((n_r, n_c, model.embed_dim), np.float32)
    with torch.inference_mode():
        for r, c in windows3(n_r, n_c):
            win = x[:, r[0] * PATCH3:(r[-1] + 1) * PATCH3, c[0] * PATCH3:(c[-1] + 1) * PATCH3]
            f = model.forward_features(torch.from_numpy(win[None]).to(device))[0, model.num_prefix_tokens:]
            out[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = f.float().cpu().numpy().reshape(len(r), len(c), -1)
    return out


def strip_weights(seg, seg_road, roads, valid, band_m, n_c, n_patches, patch=PATCH3):
    """(n_roads, n_patches) strip-pixel counts of each road in each patch (the sn8_roads strip: within band_m of the
    road's centreline, nearest road, valid pixels), and each road's valid centreline pixels."""
    n = len(roads) - 1
    dist, (ni, nj) = ndi.distance_transform_edt(seg == 0, return_indices=True)
    owner = np.where((dist * RES <= band_m) & valid, seg_road[seg[ni, nj]], 0)
    rr, cc = np.nonzero(owner)
    weight = np.zeros((n + 1, n_patches))
    np.add.at(weight, (owner[rr, cc], (rr // patch) * n_c + cc // patch), 1.0)
    centre_px = np.bincount(np.where((seg > 0) & valid, seg_road[seg[ni, nj]], 0).ravel(), minlength=n + 1)[1:]
    return weight[1:], centre_px


def pooled_cues(tb, ta, weight, patch=PATCH3):
    """sn8_dino.lines_dino's pooling on any token grids: (pooled change, mean change, max change, pooled before,
    pooled after) per road, from the (n_roads, n_patches) strip weights."""
    fb, fa = tb.reshape(-1, tb.shape[-1]), ta.reshape(-1, ta.shape[-1])
    change = _cosine_change(fb, fa)
    total = weight.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        pooled_b, pooled_a = (weight @ fb) / total[:, None], (weight @ fa) / total[:, None]
        mean_change = (weight @ change) / total
    big = weight >= MAX_MIN_SHARE * patch * patch
    max_change = np.where(big.any(1), np.where(big, change[None, :], -np.inf).max(1), np.nan)
    return _cosine_change(pooled_b, pooled_a), mean_change, max_change, pooled_b, pooled_a


def lines_dino3(tile_id, p, valid, seg, seg_road, roads, band_m):
    """DINO3_CUES and the pooled tokens for any set of road lines on a tile_pair grid (the same roads in the same order
    as sn8_dino.lines_dino). Returns (rows, before, after)."""
    n = len(roads) - 1
    if n == 0:
        return [], np.zeros((0, DIM3), np.float32), np.zeros((0, DIM3), np.float32)
    tb, ta = tokens3(p["before_grey"], valid), tokens3(p["after_grey"], valid)
    weight, centre_px = strip_weights(seg, seg_road, roads, valid, band_m, tb.shape[1], tb.shape[0] * tb.shape[1])
    pooled, mean_change, max_change, pooled_b, pooled_a = pooled_cues(tb, ta, weight)
    keep = [k for k in range(n) if centre_px[k] >= MIN_ROAD_PX]
    rows = [{"tile_id": tile_id, "road_id": roads[k + 1]["road_id"], "dino3_change_pooled": float(pooled[k]),
             "dino3_change_mean": float(mean_change[k]), "dino3_change_max": float(max_change[k])} for k in keep]
    return rows, pooled_b[keep].astype(np.float32), pooled_a[keep].astype(np.float32)


def _hash(*functions):
    return [hashlib.sha256(inspect.getsource(f).encode()).hexdigest() for f in functions]


def _key(settings):
    return hashlib.sha256(json.dumps(settings).encode()).hexdigest()[:16]


def _model_settings():
    _, _, mean, std = backbone3()
    return [MODEL3, PATCH3, WINDOWS3, list(mean), list(std), NODATA_ERODE_PX,
            *_hash(normalised3, windows3, tokens3)]


def _road_paths(split):
    band = road_band()
    settings = [SPLIT_FINGERPRINT, split, band, *_model_settings(), MAX_MIN_SHARE, MIN_ROAD_PX,
                *_hash(strip_weights, pooled_cues, lines_dino3)]
    key = _key(settings)
    return band, CACHE_DIR / f"road_{MODEL3}_{split}_{key}.csv", CACHE_DIR / f"road_{MODEL3}_{split}_{key}.npz"


def _build(split, allow_held_out=False, progress=None):
    guard_split(split, allow_held_out)
    band, csv, npz = _road_paths(split)
    if not csv.exists():
        index = pd.read_csv(GREY_DIR / "tiles.csv")
        rows, before, after = [], [], []
        for k, tile_id in enumerate(index.tile_id[index.split == split]):
            p = tile_pair(tile_id, allow_held_out)
            valid = ndi.binary_erosion((p["before_grey"] > 0) & (p["after_grey"] > 0), iterations=NODATA_ERODE_PX)
            seg, _, seg_road, roads = _road_lines(tile(tile_id)["label"], (p["x0"], p["y0"]), valid.shape)
            r, b, a = lines_dino3(tile_id, p, valid, seg, seg_road, roads, band)
            rows += r
            before.append(b)
            after.append(a)
            if progress:
                progress(f"road tokens {split}: {k + 1} tiles")
        CACHE_DIR.mkdir(exist_ok=True)
        np.savez_compressed(npz, before=np.concatenate(before), after=np.concatenate(after))
        pd.DataFrame(rows).to_csv(csv, index=False)
    d = pd.read_csv(csv)
    roads = feature_table(split, allow_held_out)
    if not (d.tile_id.equals(roads.tile_id) and d.road_id.equals(roads.road_id)):
        raise ValueError(f"{csv.name} does not line up with feature_table('{split}'): delete it and rerun")
    return d, npz


def dino3_table(split, allow_held_out=False, progress=None):
    """DINO3_CUES per road, the same rows in the same order as sn8_roads.feature_table(split). Cached."""
    return _build(split, allow_held_out, progress)[0]


def dino3_vectors(split, allow_held_out=False):
    """The pooled before and after DINOv3 tokens per road, (n_roads, 1024) each, in dino3_table(split) row order."""
    z = np.load(_build(split, allow_held_out)[1])
    return z["before"], z["after"]


def with_dino3(roads):
    """touched_roads(include_cloudy=True) (unfiltered; training roads, then validation) with DINO3_CUES and the
    after - before DINO3_VECTOR columns added. Filter to the cloud-free roads afterwards, not before."""
    parts = []
    for split in ("train", "val"):
        before, after = dino3_vectors(split)
        parts.append(pd.concat([dino3_table(split), pd.DataFrame(after - before, columns=DINO3_VECTOR)], axis=1))
    d = pd.concat(parts, ignore_index=True)
    if not (len(d) == len(roads) and d.tile_id.equals(roads.tile_id.reset_index(drop=True))
            and d.road_id.equals(roads.road_id.reset_index(drop=True))):
        raise ValueError("with_dino3 needs touched_roads(include_cloudy=True), unfiltered")
    return pd.concat([roads.reset_index(drop=True), d[DINO3_CUES + DINO3_VECTOR]], axis=1)


class ReducePrefixed(ReduceColumns):
    """sn8_dino.ReduceColumns (PCA on `columns`, fitted inside each fold) with the components named `prefix`{k}, so
    two token vectors can be reduced side by side."""

    def __init__(self, columns, n=16, seed=662, prefix="dino3_pc"):
        super().__init__(columns, n, seed)
        self.prefix = prefix

    def transform(self, X):
        out = super().transform(X)
        return out.rename(columns={f"dino_pc{k}": f"{self.prefix}{k}" for k in range(self.n)})


# ---------- Track A: cells ----------

def _before_tokens3(tile_id, allow_held_out=False):
    """tokens3 of the tile's before image (valid = the before image's own no-data, eroded), computed in two parts:
    the first 20 blocks from dinov3_finetune's float32 trunk cache (made once, shared with phase 2), then the last 4
    blocks and the final norm, the same float32 operations as forward_features."""
    import torch
    from dinov3_finetune import TRUNK_DEPTH, trunk
    if allow_held_out:
        raise PermissionError("the DINOv3 benchmark never reads held-out tiles")
    model, device, _, _ = backbone3()
    z = trunk(tile_id, "before")
    n_r, n_c = z["grid"]
    out = np.zeros((n_r, n_c, model.embed_dim), np.float32)
    with torch.inference_mode():
        for (r, c), w in zip(windows3(n_r, n_c), z["windows"]):
            h = torch.from_numpy(w[None].astype(np.float32)).to(device)
            rope = model.rope.get_embed(shape=(len(r), len(c)))
            for blk in model.blocks[TRUNK_DEPTH:]:
                h = blk(h, rope=rope)
            f = model.norm(h)[0, model.num_prefix_tokens:]
            out[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = f.float().cpu().numpy().reshape(len(r), len(c), -1)
    return out, None             # (tokens, unused): callers take the tokens only


def _cell_settings():
    from dinov3_finetune import TRUNK_DEPTH, run_trunk, trunk, trunk_dir
    return [SPLIT_FINGERPRINT, *_model_settings(), DINO_CELL_PCS, CELL_SAMPLE, SEED,
            *_hash(_before_tokens3, run_trunk, trunk), TRUNK_DEPTH, trunk_dir().name]


def cell_basis3(progress=None):
    """The principal components of the training tiles' before-image DINOv3 tokens: (mean, components), cached. The
    same sampling as sn8_dino_cells.cell_basis (300 patches per training tile, one seeded generator, tile order)."""
    path = CACHE_DIR / f"cell_basis_{MODEL3}_{_key(_cell_settings())}.npz"
    if not path.exists():
        rng = np.random.default_rng(SEED)
        index = pd.read_csv(GREY_DIR / "tiles.csv")
        sample = []
        for k, tile_id in enumerate(index.tile_id[index.split == "train"]):
            t = _before_tokens3(tile_id)[0].reshape(-1, DIM3)
            sample.append(t[rng.choice(len(t), min(CELL_SAMPLE, len(t)), replace=False)])
            if progress:
                progress(f"cell basis: {k + 1} training tiles")
        x = np.concatenate(sample).astype(np.float64)
        mean = x.mean(0)
        _, s, vt = np.linalg.svd(x - mean, full_matrices=False)
        CACHE_DIR.mkdir(exist_ok=True)
        np.savez_compressed(path, mean=mean.astype(np.float32), components=vt[:DINO_CELL_PCS].astype(np.float32),
                            explained=(s ** 2 / (s ** 2).sum()).astype(np.float32))
    z = np.load(path)
    return z["mean"], z["components"]


def tile_cell_dino3(tile_id, rows, cols, basis, allow_held_out=False):
    """DINO3_CELL_FEATURES at the centres of the given 2 m cells of the tile's before image, as an (n, 32) array."""
    mean, comps = basis
    t, _ = _before_tokens3(tile_id, allow_held_out)
    pcs = ((t.reshape(-1, t.shape[-1]) - mean) @ comps.T).reshape(t.shape[0], t.shape[1], -1).astype(np.float32)
    up = np.stack([cv2.resize(pcs[..., k], (t.shape[1] * PATCH3, t.shape[0] * PATCH3), interpolation=cv2.INTER_LINEAR)
                   for k in range(pcs.shape[-1])], -1)
    r = np.asarray(rows) * CELL_PX + CELL_PX // 2
    c = np.asarray(cols) * CELL_PX + CELL_PX // 2
    return up[r, c]


def cell_dino3_table(split, allow_held_out=False, progress=None):
    """sn8_detect.cell_table(split) (same rows, same order) with DINO3_CELL_FEATURES added. Cached."""
    guard_split(split, allow_held_out)
    cells = cell_table(split, allow_held_out)
    basis = cell_basis3(progress)
    path = CACHE_DIR / f"cells_{MODEL3}_{split}_{_key([*_cell_settings(), split, len(cells), *_hash(tile_cell_dino3)])}.npz"
    if not path.exists():
        out = np.zeros((len(cells), DINO_CELL_PCS), np.float32)
        groups = cells.groupby("tile_id", sort=False).indices
        for k, (tile_id, idx) in enumerate(groups.items()):
            out[idx] = tile_cell_dino3(tile_id, cells.row.values[idx], cells.col.values[idx], basis, allow_held_out)
            if progress:
                progress(f"cell features {split}: {k + 1} of {len(groups)} tiles")
        CACHE_DIR.mkdir(exist_ok=True)
        np.savez_compressed(path, features=out, tile_id=cells.tile_id.to_numpy().astype(str),
                            row=cells.row.to_numpy(), col=cells.col.to_numpy())
    z = np.load(path)
    if not (np.array_equal(z["row"], cells.row.to_numpy()) and np.array_equal(z["tile_id"], cells.tile_id.astype(str))):
        raise ValueError(f"{path.name} does not line up with cell_table('{split}'): delete it and rerun")
    return pd.concat([cells.reset_index(drop=True), pd.DataFrame(z["features"], columns=DINO3_CELL_FEATURES)], axis=1)


# ---------- pictures ----------

def change_maps(tile_id):
    """Both models' patch change (1 - cosine, before against after) on one tile: (tile_pair, valid, DINOv2 map,
    DINOv3 map)."""
    from sn8_dino import tokens
    p = tile_pair(tile_id)
    valid = ndi.binary_erosion((p["before_grey"] > 0) & (p["after_grey"] > 0), iterations=NODATA_ERODE_PX)
    c2 = _cosine_change(tokens(p["before_grey"], valid), tokens(p["after_grey"], valid))
    c3 = _cosine_change(tokens3(p["before_grey"], valid), tokens3(p["after_grey"], valid))
    return p, valid, c2, c3


def show_change_pair(tile_id, path, note=""):
    """Before, after, the DINOv2 patch change (7 m) and the DINOv3 patch change (8 m), with the labelled roads (red
    flooded, cyan not), saved as a PNG. Each map is shown from 0 to its own 99th percentile."""
    from sn8_dino import PATCH
    p, valid, c2, c3 = change_maps(tile_id)
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    for ax, img, title in ((axes[0, 0], p["before_grey"], "before"), (axes[0, 1], p["after_grey"], "after")):
        ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"{tile_id} {title} (greyscale, what both models read)", fontsize=11)
    for ax, change, patch, name in ((axes[1, 0], c2, PATCH, "DINOv2 ViT-L/14 (LVD-142M), 7 m patches"),
                                    (axes[1, 1], c3, PATCH3, "DINOv3 ViT-L/16 (SAT-493M), 8 m patches")):
        extent = (0, change.shape[1] * patch, change.shape[0] * patch, 0)
        im = ax.imshow(change, cmap="magma", vmin=0, vmax=np.nanpercentile(change, 99), extent=extent)
        draw_roads(ax, tile(tile_id)["label"], (p["x0"], p["y0"]))
        ax.set_xlim(0, valid.shape[1])
        ax.set_ylim(valid.shape[0], 0)
        ax.set_title(f"{name}\npatch change, 1 - cosine; labelled roads (red flooded, cyan dry)", fontsize=11)
        plt.colorbar(im, ax=ax, fraction=0.04)
    for ax in axes.flat:
        ax.axis("off")
    fig.text(0.5, 0.01, f"{CREDIT3}. Both backbones frozen. {note}", ha="center", fontsize=10)
    plt.tight_layout(rect=(0, 0.025, 1, 1))
    fig.savefig(path, dpi=90)
    plt.close(fig)
    return c2, c3


def all_cells3(tile_id, basis2, basis3):
    """Every 2 m cell of the tile (sn8_detect.tile_cells) with the DINOv2 and DINOv3 cell features."""
    from sn8_detect import tile_cells
    from sn8_dino_cells import DINO_CELL_FEATURES, tile_cell_dino
    c = tile_cells(tile_id).reset_index(drop=True)
    c[DINO_CELL_FEATURES] = tile_cell_dino(tile_id, c.row.values, c.col.values, basis2)
    c[DINO3_CELL_FEATURES] = tile_cell_dino3(tile_id, c.row.values, c.col.values, basis3)
    return c


def show_cells_pair(tile_id, runs, cells, path):
    """sn8_dino_cells.show_cells_detection for (name, fitted model, columns, cut-off) runs, saved as a PNG: green
    found, red detected but not road, blue road missed (cells 3.5-8 m from a road are left out)."""
    from matplotlib.colors import ListedColormap
    p = tile_pair(tile_id)
    shape = (cells.row.max() + 1, cells.col.max() + 1)
    fig, axes = plt.subplots(1, len(runs), figsize=(8 * len(runs), 8.6), squeeze=False)
    lab = cells.label.to_numpy()
    for ax, (name, model, columns, cut) in zip(axes[0], runs):
        found = model.predict_proba(cells[columns])[:, 1] >= cut
        outcome = np.full(shape, np.nan)
        for value, m in ((0, (lab == 1) & found), (1, (lab == 0) & found), (2, (lab == 1) & ~found)):
            outcome[cells.row.values[m], cells.col.values[m]] = value
        tp, fp, fn = int(((lab == 1) & found).sum()), int(((lab == 0) & found).sum()), int(((lab == 1) & ~found).sum())
        ax.imshow(p["before_grey"], cmap="gray", vmin=0, vmax=255)
        ax.imshow(outcome, cmap=ListedColormap(["limegreen", "red", "dodgerblue"]), vmin=0, vmax=2, alpha=0.7,
                  extent=(0, shape[1] * CELL_PX, shape[0] * CELL_PX, 0))
        ax.set_xlim(0, p["before_grey"].shape[1])
        ax.set_ylim(p["before_grey"].shape[0], 0)
        ax.set_title(f"{tile_id}: {name}, cut-off {cut:.2f}\ngreen found {tp} | red not road {fp} | blue missed {fn} | "
                     f"precision {tp / max(tp + fp, 1):.2f}, recall {tp / max(tp + fn, 1):.2f}", fontsize=10)
        ax.axis("off")
    fig.text(0.5, 0.01, f"{CREDIT3}. All cells of one validation tile; detectors fitted on training cells only.",
             ha="center", fontsize=10)
    plt.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(path, dpi=80)
    plt.close(fig)
