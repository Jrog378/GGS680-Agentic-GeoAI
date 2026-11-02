"""A-head on the spatial folds from cached frozen tokens (Agent C). Research only; DINOv3 never enters the library.

A-head is phase 2's linear head on frozen DINOv3 tokens: Top(4) (blocks 21-24 + final norm, all frozen, eval mode) then
a linear map from each 16 px token to its 4 x 4 cells. Its input tokens never change during training, so this script
computes them once per tile (the same Top(4) forward of each before-image window that dinov3_finetune.train_epochs runs
at every step) and caches them in the scratchpad. The training loop is dinov3_finetune.train_epochs("A", n_frozen=4)
line for line on those tokens: same seeds (torch.manual_seed(662), numpy default_rng(662)), the same tile permutation
and window draws (one random target window per tile per epoch), AdamW (lr 1e-3, weight decay 1e-4), gradient norm
clipped at 1, masked BCE, per-epoch loss on 2 seeded windows per inner-fold-1 tile, patience 3, at most 12 epochs, the
best epoch's weights kept. The cut-off and the held-out cells follow spatialcv_gpu.run_a exactly.

Written at 20:35 because B-ft (6 epochs chosen on inner fold 1, not phase 2's 3) took the GPU budget that the
on-the-fly A-head needed; a check below stops the script unless the cached tokens equal Top(4)'s on-the-fly output.

    TOP4_CACHE=<scratch dir> /opt/miniconda3/bin/python3 -I spatialcv_ahead_cached.py > spatialcv_ahead_cached.log 2>&1
"""
import copy
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import spatialcv_common as C
import dinov3_bench as d3
import dinov3_finetune as ft

import numpy as np
import torch

from sn8_cutoff import CUTS, weighted_f1
from sn8_detect import cell_table

torch.set_num_threads(1)
SEED = 662
say = C.Log()
CACHE = Path(os.environ["TOP4_CACHE"])
CACHE.mkdir(parents=True, exist_ok=True)
FOLD_DIR, WEIGHTS = C.FOLD_DIR, C.WEIGHTS
S = {"n_frozen": 4, "lr head": 1e-3, "max epochs": 12, "patience": 3}     # phase 2's A-head settings
TIMES_PATH = FOLD_DIR / "gpu_times_trackA.json"
TIMES = json.loads(TIMES_PATH.read_text()) if TIMES_PATH.exists() else {}
T0 = time.time()

TRAIN, VAL, train_tab, val_tab = C.dev_split()
DEV = sorted(TRAIN + VAL)
FT_TAB, TILE_FOLD, INNER_OF = C.tile_folds_662()
DEVICE = d3.backbone3()[1]
OTR = [sorted(t for t in DEV if TILE_FOLD[t] != k) for k in range(5)]
OTE = [sorted(t for t in DEV if TILE_FOLD[t] == k) for k in range(5)]
inner_tiles = lambda k, j: sorted(t for t in OTR[k] if INNER_OF[k][t] == j)
fit_tiles = lambda k, j: sorted(t for t in OTR[k] if INNER_OF[k][t] != j)
GRID = {t: tuple(int(v) for v in np.load(ft.trunk_dir() / f"{t}_before.npz")["grid"]) for t in DEV}
PIC_A = val_tab.nlargest(1, "roads").tile_id.iloc[0]

# ---------- targets (the library's cell labels) and the cells to score ----------
tpath = FOLD_DIR / "a_targets.npz"
if tpath.exists():
    z = np.load(tpath)
    A_TARGET = {t: z[t] for t in DEV}
else:
    A_TARGET = {t: ft.road_cell_grid(t, GRID[t]) for t in DEV}
    np.savez_compressed(tpath, **A_TARGET)
CELLS = {s: cell_table(s)[["tile_id", "row", "col", "label"]].reset_index(drop=True) for s in ("train", "val")}
for split, tiles in (("train", TRAIN[:5]), ("val", VAL[:5])):
    c = CELLS[split]
    for t in tiles:
        cc = c[c.tile_id == t]
        assert (A_TARGET[t][cc.row.values, cc.col.values] == cc.label.values).all(), t
say(f"targets for {len(DEV)} tiles ({time.time() - T0:.0f} s)")

# ---------- frozen Top(4) tokens of every before-image window, cached once ----------
TOP = ft.Top(S["n_frozen"]).to(DEVICE).eval()
t0 = time.time()
for t in DEV:
    p = CACHE / f"{t}.npz"
    if p.exists():
        continue
    tb = ft.trunk(t, "before")
    out = {}
    with torch.no_grad():
        for k, (r, c, _, _) in enumerate(ft.window_slices(tb["grid"])):
            h = torch.from_numpy(tb["windows"][k][None].astype(np.float32)).to(DEVICE)
            out[f"w{k}"] = TOP(h, (len(r), len(c)))[0].cpu().numpy()
    np.savez(p, **out)
TIMES["A-head (cached) token cache (s)"] = round(time.time() - t0, 1)
say(f"Top(4) tokens cached for {len(DEV)} tiles: {TIMES['A-head (cached) token cache (s)']} s")


def tokens(t):
    z = np.load(CACHE / f"{t}.npz")
    return [z[f"w{k}"] for k in range(len(z.files))]


# check: cached tokens through a head == dinov3_finetune.predict_grid(Top(4), head) on the fly
torch.manual_seed(0)
_head = ft.RoadHead().to(DEVICE).eval()
for t in (DEV[0], PIC_A):
    ref = ft.predict_grid(TOP, _head, t, "A", DEVICE)
    mine = np.zeros_like(ref)
    with torch.no_grad():
        for k, (r, c, rs, cs) in enumerate(ft.window_slices(GRID[t])):
            mine[rs, cs] = torch.sigmoid(ft.unpatch(_head(torch.from_numpy(tokens(t)[k]).to(DEVICE)),
                                                    len(r), len(c))).cpu().numpy()
    diff = float(np.abs(ref - mine).max())
    say(f"cached tokens vs on-the-fly Top(4) on {t}: max |difference| in probability {diff:.2e}")
    assert diff < 1e-5
    TIMES[f"A-head (cached) check max diff {t}"] = diff
del _head
TOP = None


def grid_prob(head, t):
    head.eval()
    prob = np.zeros((GRID[t][0] * ft.SUB, GRID[t][1] * ft.SUB), np.float32)
    tok = tokens(t)
    with torch.no_grad():
        for k, (r, c, rs, cs) in enumerate(ft.window_slices(GRID[t])):
            prob[rs, cs] = torch.sigmoid(ft.unpatch(head(torch.from_numpy(tok[k]).to(DEVICE)), len(r),
                                                    len(c))).cpu().numpy()
    return prob


def eval_loss(head, eval_win, targets):
    """dinov3_finetune.eval_loss for track A on the cached tokens."""
    total, n = 0.0, 0
    head.eval()
    with torch.no_grad():
        for tile_id, keep in eval_win.items():
            target = torch.from_numpy(targets[tile_id].astype(np.int64)).to(DEVICE)
            if not (target >= 0).any():
                continue
            tok = tokens(tile_id)
            for k, (r, c, rs, cs) in enumerate(ft.window_slices(GRID[tile_id])):
                tw = target[rs, cs]
                if k not in keep or not (tw >= 0).any():
                    continue
                loss, m = ft.masked_bce(ft.unpatch(head(torch.from_numpy(tok[k]).to(DEVICE)), len(r), len(c)), tw)
                total += float(loss)
                n += m
    return total / max(n, 1)


def train(fit, eval_win, targets, epochs, lr_head, patience, seed=SEED, windows_per_tile=1):
    """dinov3_finetune.train_epochs("A", ..., n_frozen=4) on the cached tokens (Top(4) has no trainable parameter and
    consumes no random numbers when it is built, so the head starts from the same weights)."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    head = ft.RoadHead().to(DEVICE)
    opt = torch.optim.AdamW([{"params": ft.trainable(head), "lr": lr_head, "weight_decay": 1e-4}])
    history, best, best_state, waited = [], np.inf, None, 0
    for epoch in range(1, epochs + 1):
        t = time.time()
        head.train()
        total, n_cells = 0.0, 0
        for tile_id in rng.permutation(fit):
            wins = ft.target_windows(tile_id, targets)
            if not wins:
                continue
            chosen = set(rng.choice(wins, min(windows_per_tile, len(wins)), replace=False).tolist())
            target = torch.from_numpy(targets[tile_id].astype(np.int64)).to(DEVICE)
            tok = tokens(tile_id)
            opt.zero_grad()
            slices = ft.window_slices(GRID[tile_id])
            denom = int(sum((target[slices[k][2], slices[k][3]] >= 0).sum() for k in chosen))
            for k, (r, c, rs, cs) in enumerate(slices):
                if k not in chosen:
                    continue
                tw = target[rs, cs]
                logit = head(torch.from_numpy(tok[k]).to(DEVICE))
                loss, n = ft.masked_bce(ft.unpatch(logit, len(r), len(c)), tw)
                (loss / denom).backward()
                total += float(loss.detach())
                n_cells += n
            torch.nn.utils.clip_grad_norm_(ft.trainable(head), 1.0)
            opt.step()
        row = {"epoch": epoch, "train loss": total / max(n_cells, 1), "seconds": round(time.time() - t, 1)}
        row["eval loss"] = eval_loss(head, eval_win, targets)
        history.append(row)
        say(f"A-head (cached) epoch {epoch}: train loss {row['train loss']:.4f}, eval loss {row['eval loss']:.4f}, "
            f"{row['seconds']} s")
        if row["eval loss"] < best:
            best, waited = row["eval loss"], 0
            best_state = (copy.deepcopy(head.state_dict()), epoch)
        else:
            waited += 1
            if waited >= patience:
                break
    head.load_state_dict(best_state[0])
    return head, history


for k in range(5):
    if (FOLD_DIR / f"A-head_outer{k}.npz").exists():
        continue
    t0 = time.time()
    fit, ev = fit_tiles(k, 0), inner_tiles(k, 0)
    head, hist = train(fit, ft.eval_windows(ev, A_TARGET), A_TARGET, S["max epochs"], S["lr head"], S["patience"])
    best_epoch = int(np.argmin([h["eval loss"] for h in hist]) + 1)
    y, p = [], []
    for t in ev:
        g = grid_prob(head, t)
        m = A_TARGET[t] >= 0
        y.append(A_TARGET[t][m])
        p.append(g[m])
    y, p = np.concatenate(y), np.concatenate(p)
    f1 = [weighted_f1(y, p >= c, np.ones(len(y))) for c in CUTS]
    cut = float(CUTS[int(np.argmax(f1))])
    arrays = {}
    for split in ("train", "val"):
        c = CELLS[split]
        idx = np.flatnonzero(c.tile_id.isin(OTE[k]).to_numpy())
        prob = np.zeros(len(idx), np.float32)
        sub = c.iloc[idx]
        for t, ii in sub.groupby("tile_id", sort=False).indices.items():
            g = grid_prob(head, t)
            prob[ii] = g[sub.row.values[ii], sub.col.values[ii]]
            if t == PIC_A:
                arrays[f"grid_{PIC_A}"] = g
        arrays[f"idx_{split}"], arrays[f"prob_{split}"] = idx, prob
    torch.save({"head": {q: v.cpu() for q, v in head.state_dict().items()}, "history": hist, "outer fold": k,
                "cut-off": cut, "best epoch": best_epoch, "model": d3.MODEL3, "licence": d3.LICENCE3},
               WEIGHTS / f"trackA_A-head_outer{k}.pt")
    sec = round(time.time() - t0, 1)
    np.savez_compressed(FOLD_DIR / f"A-head_outer{k}.npz", **arrays)
    (FOLD_DIR / f"A-head_outer{k}.json").write_text(json.dumps(
        {"cut-off (inner fold 1)": cut, "inner fold 1 F1": float(max(f1)), "best epoch": best_epoch,
         "epochs run": len(hist), "history": hist, "fit tiles": len(fit), "inner fold 1 tiles": len(ev),
         "held-out tiles": len(OTE[k]), "seconds": sec,
         "mean epoch, cached tokens (s)": float(np.mean([h["seconds"] for h in hist])),
         "implementation": "spatialcv_ahead_cached.py: train_epochs('A', n_frozen=4) on cached frozen Top(4) tokens"},
        indent=1, default=float))
    TIMES[f"A-head outer {k} (s)"] = sec
    TIMES_PATH.write_text(json.dumps(TIMES, indent=1))
    say(f"A-head outer fold {k + 1}: best epoch {best_epoch} of {len(hist)}, cut-off {cut:.2f} (inner F1 "
        f"{max(f1):.3f}), {sec} s")
TIMES["A-head (cached) total (s)"] = round(time.time() - T0, 1)
TIMES_PATH.write_text(json.dumps(TIMES, indent=1))
say("done")
