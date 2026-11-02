"""Spatial CV of the fine-tuned DINOv3 arms (Agent C, GPU). Research benchmark only; DINOv3 never enters the library.

Plan: outputs/preregistration_spatial_cv.md, "Agent C": the seed-662 spatial outer folds; one fine-tune (or head) per
outer fold on that fold's training blocks only; early stopping (and the Track A cut-off) on inner fold 1 of the nested
spatial folds in place of phase 2's random 20% tile split; Track B cross-fitting on that outer fold's 5 inner folds;
purged roads give no training target (their pixels may still be context). Phase 2's settings are kept unchanged
(last 2 of 24 blocks trained on the cached frozen 20-block trunk, one window per tile per epoch, AdamW, float32).

Order (the plan's, if GPU time runs short): B-head, B-ft, A-head, A-ft. Each outer fold's result is written to
spatialcv_folds/ as soon as it finishes, and a finished fold is skipped on a rerun.

    /opt/miniconda3/bin/python3 -I spatialcv_gpu.py > spatialcv_gpu.log 2>&1          (from this folder)
    SPATIALCV_SMOKE=1 SPATIALCV_SMOKE_OUT=<dir> ... spatialcv_gpu.py   # code check: tiny tile sets, RANDOM targets

Weights (trained parameters only, float16) go in ~/Masters/models/finetuned/dinov3_sat493m/spatial_cv/.
"""
import gc
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
import torch.nn.functional as F
from scipy import ndimage as ndi

from sn8_cutoff import CUTS, weighted_f1
from sn8_detect import cell_table
from sn8_lines import NODATA_ERODE_PX, road_band
from sn8_torchgeo import tile_pair

torch.set_num_threads(2)
SMOKE = os.environ.get("SPATIALCV_SMOKE") == "1"
FOLD_DIR = Path(os.environ["SPATIALCV_SMOKE_OUT"]) if SMOKE else C.FOLD_DIR
WEIGHTS = FOLD_DIR / "weights" if SMOKE else C.WEIGHTS
FOLD_DIR.mkdir(parents=True, exist_ok=True)
WEIGHTS.mkdir(parents=True, exist_ok=True)
STAGES = [s for s in sys.argv[1:]] or ["B-head", "B-ft", "A-head", "A-ft"]
BUDGET_S = float(os.environ.get("SPATIALCV_GPU_BUDGET_H", "7.25")) * 3600
SEED = 662
say = C.Log()
T_START = time.time()
SETTINGS = {   # phase 2's settings, unchanged (run_phase2.SETTINGS)
    "trunk depth (frozen, cached)": ft.TRUNK_DEPTH,
    "A-ft": {"trained blocks": 2, "n_frozen": 2, "lr blocks": 2e-5, "lr head": 1e-3, "max epochs": 20, "patience": 4},
    "A-head": {"trained blocks": 0, "n_frozen": 4, "lr head": 1e-3, "max epochs": 12, "patience": 3},
    "B-ft": {"trained blocks": 2, "n_frozen": 2, "lr blocks": 1e-5, "lr head": 1e-3, "max epochs": 10, "patience": 3},
    "B-head": {"trained blocks": 0, "lr head": 1e-3, "batch (patches)": 256, "max epochs": 40, "patience": 3},
    "epoch": "one random window (of those holding target cells) from every fit tile; one optimiser step per tile",
    "per-epoch evaluation": "a fixed seeded subset of 2 target windows per inner-fold-1 tile",
    "optimiser": "AdamW (weight decay 0.05 blocks, 1e-4 head), gradient norm clipped at 1, float32",
    "early stopping / cut-off tiles": "inner fold 1 of nested_spatial_folds / nested_cell_folds (seed 662) inside each "
                                      "outer-training fold; fit on the other 4 inner folds' tiles",
    "Track B cross-fitting": "the outer fold's 5 inner folds: model j is fit on the outer-training tiles outside inner "
                             "fold j (targets: inner-training roads, purged) and gives inner fold j's cues; held-out "
                             "roads take the mean of the 5 models' probability grids",
    "Track B targets": "the roads production's cloud rule assesses, among each model's (purged) training roads",
}
# a process that runs only the Track A stages (beside the Track B process) keeps its own times file
TIMES_PATH = FOLD_DIR / ("gpu_times_trackA.json" if set(STAGES) <= {"A-head", "A-ft"} else "gpu_times.json")
TIMES = json.loads(TIMES_PATH.read_text()) if TIMES_PATH.exists() else {}
NOT_RUN_PATH = FOLD_DIR / "not_run.json"


def save_times():
    TIMES_PATH.write_text(json.dumps(TIMES, indent=1))


def cleanup():
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def mps_gb():
    return torch.mps.driver_allocated_memory() / 1e9 if torch.backends.mps.is_available() else 0.0


# ---------- data: the 226 development tiles; nothing else ----------
TRAIN, VAL, train_tab, val_tab = C.dev_split()
DEV = sorted(TRAIN + VAL)
FT_TAB, TILE_FOLD, INNER_OF = C.tile_folds_662()
assert set(FT_TAB.tile_id) == set(DEV)
DEVICE = d3.backbone3()[1]
missing = [(t, d) for t in DEV for d in ("before", "after") if not (ft.trunk_dir() / f"{t}_{d}.npz").exists()]
assert not missing, f"{len(missing)} trunk files missing; the cache from last night is reused, not rebuilt"
roads, RULE, TILE_RULE = C.load_roads(gpu=True)
NSF = C.road_folds(roads)
ROWS_OF = roads.groupby("tile_id", sort=False).indices
RULE_ROWS = set(np.flatnonzero(RULE).tolist())
ROAD_TILES = set(roads.tile_id)
RID = roads.road_id.to_numpy()
TID = roads.tile_id.to_numpy()
OTR = [sorted(t for t in DEV if TILE_FOLD[t] != k) for k in range(C.N_FOLDS)]
OTE = [sorted(t for t in DEV if TILE_FOLD[t] == k) for k in range(C.N_FOLDS)]


def inner_tiles(k, j):
    return sorted(t for t in OTR[k] if INNER_OF[k][t] == j)


def fit_tiles(k, j):
    return sorted(t for t in OTR[k] if INNER_OF[k][t] != j)


for k, (tr, te, inner) in enumerate(NSF):   # the road folds and the tile folds agree
    assert set(TID[te]) <= set(OTE[k]) and set(TID[tr]) <= set(OTR[k])
    assert not set(RID[tr]) & set(RID[te]), "purge: no training road shares an id with a held-out road"
    for j, (itr, ite) in enumerate(inner):
        assert set(TID[ite]) <= set(inner_tiles(k, j)) and set(TID[itr]) <= set(fit_tiles(k, j))
        assert set(itr) <= set(tr) and set(ite) <= set(tr)

PIC_B = val_tab.nlargest(1, "roads_flooded").tile_id.iloc[0]   # last night's fixed rules, same tiles
PIC_A = val_tab.nlargest(1, "roads").tile_id.iloc[0]
if SMOKE:   # code check: outer fold 0 only, a few tiles per set, 1 epoch, random targets
    _k = 0
    _rule_tiles = set(TID[RULE])
    OTE = [sorted([t for t in OTE[_k] if t in _rule_tiles][:3])] + [[] for _ in range(4)]
    _otr = sorted([t for t in OTR[_k] if t in _rule_tiles])
    _keep = set()
    for _j in range(5):
        _ok = set(TID[[r for r in NSF[_k][2][_j][1] if RULE[r]]])
        _keep |= set([t for t in _otr if INNER_OF[_k][t] == _j and t in _ok][:2])
    OTR = [sorted(_keep)] + [[] for _ in range(4)]
    INNER_OF[_k] = {t: INNER_OF[_k][t] for t in OTR[_k]}
    for name in ("A-ft", "A-head", "B-ft", "B-head"):
        SETTINGS[name]["max epochs"] = 1
    PIC_B, PIC_A = OTE[0][0], OTE[0][-1]
FOLDS_TO_RUN = [0] if SMOKE else list(range(C.N_FOLDS))
WORK = sorted(set(OTR[0]) | set(OTE[0])) if SMOKE else DEV      # tiles that need layouts, strip tokens, targets
say(f"{len(DEV)} dev tiles; outer folds hold out {[len(x) for x in OTE]} tiles; trunk cache {ft.trunk_dir().name}; "
    f"pictures: Track B {PIC_B} (outer fold {TILE_FOLD[PIC_B] + 1}), Track A {PIC_A} (outer fold {TILE_FOLD[PIC_A] + 1})")

# check: trunk cache + the 4 frozen top blocks reproduce dinov3_bench.tokens3 (as phase 2 checked)
_t = DEV[0]
_p = tile_pair(_t)
_ref = d3.tokens3(_p["before_grey"], ndi.binary_erosion(_p["before_grey"] > 0, iterations=NODATA_ERODE_PX))
_top = ft.Top(4).to(DEVICE).eval()
_tb = ft.trunk(_t, "before")
_mine = np.zeros_like(_ref)
with torch.no_grad():
    for _w, (r, c, _, _) in enumerate(ft.window_slices(_tb["grid"])):
        h = torch.from_numpy(_tb["windows"][_w][None].astype(np.float32)).to(DEVICE)
        _mine[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = _top(h, (len(r), len(c)))[0].cpu().numpy().reshape(len(r), len(c), -1)
_cos = (_ref * _mine).sum(-1) / np.linalg.norm(_ref, axis=-1) / np.linalg.norm(_mine, axis=-1)
say(f"trunk reproduction on {_t}: cosine to tokens3 min {_cos.min():.6f}")
assert _cos.min() > 0.99
TIMES["trunk reproduction cosine (min)"] = float(_cos.min())
del _p, _ref, _top, _tb, _mine
cleanup()
GRID = {t: tuple(int(v) for v in np.load(ft.trunk_dir() / f"{t}_before.npz")["grid"]) for t in DEV}


def mark_not_run(name, why):
    nr = json.loads(NOT_RUN_PATH.read_text()) if NOT_RUN_PATH.exists() else {}
    nr[name] = {"why": why, "when": time.strftime("%Y-%m-%d %H:%M:%S")}
    NOT_RUN_PATH.write_text(json.dumps(nr, indent=1))
    say(f"NOT RUN: {name}: {why}")


def save_ckpt(top, head, hist, name, extra=None):
    """Trained parameters only (the frozen blocks are the public checkpoint's), in float16 to spare the disk."""
    if C.free_gb() < 6:
        say(f"checkpoint {name} not saved: {C.free_gb():.1f} GB free")
        return
    st = {} if top is None else {k: (v.half() if v.is_floating_point() else v).cpu()
                                 for k, v in top.state_dict().items() if not k.startswith("frozen.")}
    torch.save({"top_trained": st, "head": {k: v.cpu() for k, v in head.state_dict().items()}, "history": hist,
                "dtype of top_trained": "float16", "model": d3.MODEL3, "trunk depth": ft.TRUNK_DEPTH,
                "licence": d3.LICENCE3, **(extra or {})}, WEIGHTS / name)


# ======================================================================================================================
# Track B
# ======================================================================================================================
LAYOUT = {}


def build_layout():
    if LAYOUT:
        return
    t0 = time.time()
    band = road_band()
    for t in WORK:
        LAYOUT[t] = ft.strip_layout(t, band)
        assert [r[1] for r in LAYOUT[t][0]] == RID[ROWS_OF.get(t, [])].tolist(), t
    TIMES["Track B strip layouts (s)"] = round(time.time() - t0, 1)
    say(f"strip layouts for {len(WORK)} tiles: {TIMES['Track B strip layouts (s)']} s")


_RNG_SMOKE = np.random.default_rng(0)


def b_targets(rows, tiles):
    """Track B target grids on `tiles`: the strip cells of the roads in `rows` (positions in the 1,037) that
    production's cloud rule assesses; every other cell -1. Code check: random 0 / 1 where a target exists."""
    allowed = set(int(r) for r in rows) & RULE_ROWS
    out = {}
    for t in tiles:
        pos = {i for i, r in enumerate(ROWS_OF.get(t, [])) if int(r) in allowed}
        g = ft.flood_cell_grid(LAYOUT[t], pos)
        if SMOKE:
            g[g >= 0] = _RNG_SMOKE.integers(0, 2, int((g >= 0).sum()))
        out[t] = g
    return out, len(allowed & set(int(r) for t in tiles for r in ROWS_OF.get(t, [])))


def b_specs(k):
    """Outer fold k's Track B models: the early-stopping model (fit on inner folds 2-5, evaluated on inner fold 1) and
    the 5 cross-fit models (fit outside inner fold j, predict inner fold j)."""
    tr, te, inner = NSF[k]
    held_ids = set(RID[te])
    es_fit, es_eval = fit_tiles(k, 0), inner_tiles(k, 0)
    t_fit, n_fit = b_targets(inner[0][0], es_fit)
    t_eval, n_eval = b_targets(inner[0][1], es_eval)
    cf = []
    for j, (itr, ite) in enumerate(inner):
        assert not set(RID[itr]) & held_ids
        fit = fit_tiles(k, j)
        tg, n = b_targets(itr, fit)
        cf.append({"fit": fit, "targets": tg, "n target roads": n, "held": [t for t in inner_tiles(k, j)
                                                                            if t in ROAD_TILES]})
    return {"es fit": es_fit, "es eval": es_eval, "es targets": {**t_fit, **t_eval}, "es target roads": n_fit,
            "es eval roads": n_eval, "cf": cf, "test": [t for t in OTE[k] if t in ROAD_TILES]}


def cues_from_grids(grids, prefix):
    """(1,037, 3) cues (strip-weighted mean, max, share >= 0.5) in road order; NaN for roads off `grids`."""
    out = np.full((len(roads), 3), np.nan)
    for t, g in grids.items():
        cues = ft.road_cues(LAYOUT[t], g, prefix)
        rows = ROWS_OF.get(t, [])
        assert [c["road_id"] for c in cues] == RID[rows].tolist(), t
        for r, c in zip(rows, cues):
            out[r] = [c[f"{prefix}_{s}"] for s in ("mean", "max", "share")]
    return out


# ---------- B-head: a flood head on frozen DINOv3 final tokens (copied from run_phase2.py, targets as an argument)
STRIP = {}


def strip_tokens(t, top):
    tb, ta = ft.trunk(t, "before"), ft.trunk(t, "after")
    n_r, n_c = GRID[t]
    owner = LAYOUT[t][2]
    has = (owner > 0).reshape(n_r, ft.SUB, n_c, ft.SUB).any(axis=(1, 3))
    idx, fb, fa = [], [], []
    with torch.no_grad():
        for k, (r, c, _, _) in enumerate(ft.window_slices((n_r, n_c))):
            sel = has[np.ix_(r, c)].ravel()
            if not sel.any():
                continue
            gi = (r[:, None] * n_c + c[None, :]).ravel()[sel]
            xb = top(torch.from_numpy(tb["windows"][k][None].astype(np.float32)).to(DEVICE), (len(r), len(c)))[0]
            xa = top(torch.from_numpy(ta["windows"][k][None].astype(np.float32)).to(DEVICE), (len(r), len(c)))[0]
            sel_t = torch.from_numpy(np.flatnonzero(sel)).to(DEVICE)
            idx.append(gi)
            fb.append(xb[sel_t].half().cpu().numpy())
            fa.append(xa[sel_t].half().cpu().numpy())
    if not idx:
        return np.zeros(0, int), np.zeros((0, d3.DIM3), np.float16), np.zeros((0, d3.DIM3), np.float16)
    return np.concatenate(idx), np.concatenate(fb), np.concatenate(fa)


def patch_targets(t, idx, grid):
    n_r, n_c = GRID[t]
    g = grid.reshape(n_r, ft.SUB, n_c, ft.SUB).transpose(0, 2, 1, 3).reshape(n_r * n_c, ft.SUB * ft.SUB)
    return g[idx]


def head_data(tiles, targets):
    xb = np.concatenate([STRIP[t][1] for t in tiles])
    xa = np.concatenate([STRIP[t][2] for t in tiles])
    y = np.concatenate([patch_targets(t, STRIP[t][0], targets[t]) for t in tiles])
    m = (y >= 0).any(1)
    return xb[m], xa[m], y[m]


def head_loss(head, xb, xa, y, bs=2048):
    head.eval()
    total, n = 0.0, 0
    with torch.no_grad():
        for s in range(0, len(y), bs):
            tb = torch.from_numpy(xb[s:s + bs].astype(np.float32)).to(DEVICE)
            ta = torch.from_numpy(xa[s:s + bs].astype(np.float32)).to(DEVICE)
            tt = torch.from_numpy(y[s:s + bs].astype(np.int64)).to(DEVICE)
            m = tt >= 0
            total += float(F.binary_cross_entropy_with_logits(head(tb, ta)[m], tt[m].float(), reduction="sum"))
            n += int(m.sum())
    return total / max(n, 1)


def train_head(fit_tiles_, eval_tiles, targets, epochs, patience):
    s = SETTINGS["B-head"]
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    head = ft.FloodHead().to(DEVICE)
    opt = torch.optim.AdamW(head.parameters(), lr=s["lr head"], weight_decay=1e-4)
    xb, xa, y = head_data(fit_tiles_, targets)
    ev = head_data(eval_tiles, targets) if eval_tiles else None
    hist, best, best_state, waited = [], np.inf, None, 0
    for epoch in range(1, epochs + 1):
        head.train()
        total, n = 0.0, 0
        order = rng.permutation(len(y))
        for s0 in range(0, len(y), s["batch (patches)"]):
            i = order[s0:s0 + s["batch (patches)"]]
            tt = torch.from_numpy(y[i].astype(np.int64)).to(DEVICE)
            m = tt >= 0
            logit = head(torch.from_numpy(xb[i].astype(np.float32)).to(DEVICE),
                         torch.from_numpy(xa[i].astype(np.float32)).to(DEVICE))
            loss = F.binary_cross_entropy_with_logits(logit[m], tt[m].float())
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * int(m.sum())
            n += int(m.sum())
        row = {"epoch": epoch, "train loss": total / max(n, 1)}
        if ev is not None:
            row["eval loss"] = head_loss(head, *ev)
        hist.append(row)
        if ev is not None:
            if row["eval loss"] < best:
                best, waited = row["eval loss"], 0
                best_state = ({k: v.clone() for k, v in head.state_dict().items()}, epoch)
            else:
                waited += 1
                if waited >= patience:
                    break
    if best_state is not None:
        head.load_state_dict(best_state[0])
    return head, (best_state[1] if best_state else epochs), hist


def head_grid(head, t):
    n_r, n_c = GRID[t]
    idx, fb, fa = STRIP[t]
    prob = np.full((n_r * n_c, ft.SUB * ft.SUB), np.nan, np.float32)
    if len(idx):
        head.eval()
        with torch.no_grad():
            prob[idx] = torch.sigmoid(head(torch.from_numpy(fb.astype(np.float32)).to(DEVICE),
                                           torch.from_numpy(fa.astype(np.float32)).to(DEVICE))).cpu().numpy()
    return prob.reshape(n_r, n_c, ft.SUB, ft.SUB).transpose(0, 2, 1, 3).reshape(n_r * ft.SUB, n_c * ft.SUB)


def fold_done(name, k):
    return (FOLD_DIR / f"{name}_outer{k}.npz").exists()


def save_fold(name, k, arrays, info):
    np.savez_compressed(FOLD_DIR / f"{name}_outer{k}.npz", **arrays)
    (FOLD_DIR / f"{name}_outer{k}.json").write_text(json.dumps(info, indent=1, default=float))


def run_b_head():
    build_layout()
    if not STRIP:
        t0 = time.time()
        top = ft.Top(4).to(DEVICE).eval()
        for t in WORK:
            STRIP[t] = strip_tokens(t, top)
        del top
        cleanup()
        TIMES["B-head strip tokens (s)"] = round(time.time() - t0, 1)
        say(f"B-head strip tokens: {sum(len(v[0]) for v in STRIP.values())} patches, {TIMES['B-head strip tokens (s)']} s")
    for k in FOLDS_TO_RUN:
        if fold_done("B-head", k):
            continue
        t0 = time.time()
        sp = b_specs(k)
        _, e_head, hist_es = train_head(sp["es fit"], sp["es eval"], sp["es targets"], SETTINGS["B-head"]["max epochs"],
                                        SETTINGS["B-head"]["patience"])
        grids, test_g, hists = {}, {t: [] for t in sp["test"]}, []
        for j, m in enumerate(sp["cf"]):
            head, _, h = train_head(m["fit"], None, m["targets"], e_head, None)
            hists.append(h)
            torch.save(head.state_dict(), WEIGHTS / f"trackB_head_outer{k}_inner{j}.pt")
            for t in m["held"]:
                grids[t] = head_grid(head, t)
            for t in test_g:
                test_g[t].append(head_grid(head, t))
            del head
        grids.update({t: np.mean(g, 0) for t, g in test_g.items()})
        cues = cues_from_grids(grids, "d3head_flood")
        arrays = {"cues": cues}
        if PIC_B in test_g:
            arrays[f"grid_{PIC_B}"] = grids[PIC_B]
        sec = round(time.time() - t0, 1)
        save_fold("B-head", k, arrays, {"epochs (chosen on inner fold 1)": e_head, "es history": hist_es,
                                        "cross-fit histories": hists, "seconds": sec,
                                        "es fit tiles": len(sp["es fit"]), "es eval tiles": len(sp["es eval"]),
                                        "es target roads": sp["es target roads"], "es eval roads": sp["es eval roads"],
                                        "cross-fit target roads": [m["n target roads"] for m in sp["cf"]],
                                        "cross-fit fit tiles": [len(m["fit"]) for m in sp["cf"]],
                                        "held-out road tiles": len(sp["test"])})
        TIMES[f"B-head outer {k} (s)"] = sec
        save_times()
        say(f"B-head outer fold {k + 1}: {e_head} epoch(s) chosen on inner fold 1; {sec} s")
        cleanup()


def run_b_ft():
    build_layout()
    for k in FOLDS_TO_RUN:
        if fold_done("B-ft", k):
            continue
        t0 = time.time()
        sp = b_specs(k)
        s = SETTINGS["B-ft"]
        epoch_s = []
        top, head, hist_es = ft.train_epochs("B", sp["es fit"], ft.eval_windows(sp["es eval"], sp["es targets"]),
                                             sp["es targets"], s["n_frozen"], s["max epochs"], s["lr blocks"],
                                             s["lr head"], DEVICE, say, patience=s["patience"], epoch_seconds=epoch_s)
        e_ft = int(np.argmin([h["eval loss"] for h in hist_es]) + 1)
        save_ckpt(top, head, hist_es, f"trackB_ft_outer{k}_es.pt", {"best epoch": e_ft, "outer fold": k})
        del top, head
        cleanup()
        say(f"B-ft outer fold {k + 1}: {e_ft} epochs chosen on inner fold 1 (mean epoch {np.mean(epoch_s):.0f} s); "
            f"MPS {mps_gb():.2f} GB")
        grids, test_g, hists = {}, {t: [] for t in sp["test"]}, []
        for j, m in enumerate(sp["cf"]):
            top, head, h = ft.train_epochs("B", m["fit"], None, m["targets"], s["n_frozen"], e_ft, s["lr blocks"],
                                           s["lr head"], DEVICE, say)
            hists.append(h)
            save_ckpt(top, head, h, f"trackB_ft_outer{k}_inner{j}.pt", {"outer fold": k, "inner fold": j})
            for t in m["held"]:
                grids[t] = ft.predict_grid(top, head, t, "B", DEVICE)
            for t in test_g:
                test_g[t].append(ft.predict_grid(top, head, t, "B", DEVICE))
            del top, head
            cleanup()
        grids.update({t: np.mean(g, 0) for t, g in test_g.items()})
        cues = cues_from_grids(grids, "d3ft_flood")
        arrays = {"cues": cues}
        if PIC_B in test_g:
            arrays[f"grid_{PIC_B}"] = grids[PIC_B]
        sec = round(time.time() - t0, 1)
        save_fold("B-ft", k, arrays, {"epochs (chosen on inner fold 1)": e_ft, "es history": hist_es,
                                      "cross-fit histories": hists, "seconds": sec,
                                      "es fit tiles": len(sp["es fit"]), "es eval tiles": len(sp["es eval"]),
                                      "es target roads": sp["es target roads"], "es eval roads": sp["es eval roads"],
                                      "cross-fit target roads": [m["n target roads"] for m in sp["cf"]],
                                      "cross-fit fit tiles": [len(m["fit"]) for m in sp["cf"]],
                                      "held-out road tiles": len(sp["test"])})
        TIMES[f"B-ft outer {k} (s)"] = sec
        save_times()
        say(f"B-ft outer fold {k + 1}: done in {sec} s")
        if k == 0 and not SMOKE:   # the first fine-tune: project the total and log it
            n_fit = float(np.mean([len(fit_tiles(q, 0)) for q in range(C.N_FOLDS)]))
            a_head = 5 * 473.0 * n_fit / 148 + 5 * 120
            a_ft = 5 * 1632.3 * n_fit / 148 + 5 * 120
            proj = (time.time() - T_START) + 4 * sec + a_head + a_ft
            TIMES["projection after B-ft outer fold 1 (s)"] = {"elapsed": round(time.time() - T_START),
                                                               "B-ft remaining": 4 * sec, "A-head (est.)": a_head,
                                                               "A-ft (est.)": a_ft, "total": round(proj)}
            save_times()
            say(f"PROJECTION after the first fine-tune: B-ft fold {sec:.0f} s; total GPU run ~{proj / 3600:.1f} h "
                f"(budget {BUDGET_S / 3600:.2f} h; A arms estimated from phase 2's times)")


# ======================================================================================================================
# Track A
# ======================================================================================================================
A_TARGET, CELLS = {}, {}


def build_a():
    if A_TARGET:
        return
    t0 = time.time()
    for t in WORK:
        A_TARGET[t] = ft.road_cell_grid(t, GRID[t])
    for split in ("train", "val"):
        c = cell_table(split)
        CELLS[split] = c[["tile_id", "row", "col", "label"]].reset_index(drop=True)
    for split, tiles in (("train", [t for t in TRAIN if t in A_TARGET][:5]),
                         ("val", [t for t in VAL if t in A_TARGET][:5])):   # targets = the library's cell labels
        c = CELLS[split]
        for t in tiles:
            cc = c[c.tile_id == t]
            assert (A_TARGET[t][cc.row.values, cc.col.values] == cc.label.values).all(), t
    if SMOKE:
        for g in A_TARGET.values():
            g[g >= 0] = _RNG_SMOKE.integers(0, 2, int((g >= 0).sum()))
    TIMES["Track A targets (s)"] = round(time.time() - t0, 1)
    say(f"Track A targets for {len(WORK)} tiles: {TIMES['Track A targets (s)']} s")


def run_a(name):
    build_a()
    s = SETTINGS[name]
    for k in FOLDS_TO_RUN:
        if fold_done(name, k):
            continue
        t0 = time.time()
        fit, ev = fit_tiles(k, 0), inner_tiles(k, 0)
        epoch_s = []
        top, head, hist = ft.train_epochs("A", fit, ft.eval_windows(ev, A_TARGET), A_TARGET, s["n_frozen"],
                                          s["max epochs"], s.get("lr blocks", 0.0), s["lr head"], DEVICE, say,
                                          patience=s["patience"], epoch_seconds=epoch_s)
        best_epoch = int(np.argmin([h["eval loss"] for h in hist]) + 1)
        y, p = [], []
        for t in ev:   # cut-off: best F1 over every labelled cell of the inner fold-1 tiles (natural road share)
            g = ft.predict_grid(top, head, t, "A", DEVICE)
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
                g = ft.predict_grid(top, head, t, "A", DEVICE)
                prob[ii] = g[sub.row.values[ii], sub.col.values[ii]]
                if t == PIC_A:
                    arrays[f"grid_{PIC_A}"] = g
            arrays[f"idx_{split}"], arrays[f"prob_{split}"] = idx, prob
        save_ckpt(top if s["n_frozen"] < 4 else None, head, hist, f"trackA_{name}_outer{k}.pt",
                  {"outer fold": k, "cut-off": cut, "best epoch": best_epoch})
        del top, head
        cleanup()
        sec = round(time.time() - t0, 1)
        save_fold(name, k, arrays, {"cut-off (inner fold 1)": cut, "inner fold 1 F1": float(max(f1)),
                                    "best epoch": best_epoch, "epochs run": len(hist), "history": hist,
                                    "fit tiles": len(fit), "inner fold 1 tiles": len(ev), "held-out tiles": len(OTE[k]),
                                    "seconds": sec, "mean epoch (s)": float(np.mean(epoch_s))})
        TIMES[f"{name} outer {k} (s)"] = sec
        save_times()
        say(f"{name} outer fold {k + 1}: best epoch {best_epoch} of {len(hist)}, cut-off {cut:.2f} (inner F1 "
            f"{max(f1):.3f}), {sec} s; MPS {mps_gb():.2f} GB")


def a_projection(name):
    """Seconds still needed for `name`, from the measured times of its finished folds (or of A-head's epochs)."""
    done = [TIMES[f"{name} outer {k} (s)"] for k in FOLDS_TO_RUN if f"{name} outer {k} (s)" in TIMES]
    todo = sum(1 for k in FOLDS_TO_RUN if not fold_done(name, k))
    if done:
        return todo * float(np.mean(done))
    if name == "A-ft":
        head_epochs = [json.loads((FOLD_DIR / f"A-head_outer{k}.json").read_text())["mean epoch (s)"]
                       for k in FOLDS_TO_RUN if (FOLD_DIR / f"A-head_outer{k}.json").exists()]
        per_epoch = (np.mean(head_epochs) * 68.0 / (473.0 / 12)) if head_epochs else 68.0
        return todo * (20 * per_epoch + 150)
    return todo * (12 * 40.0 + 120)


# ======================================================================================================================
for stage in STAGES:
    elapsed = time.time() - T_START
    if stage == "B-head":
        run_b_head()
    elif stage == "B-ft":
        run_b_ft()
    elif stage in ("A-head", "A-ft"):
        need = a_projection(stage)
        if not SMOKE and elapsed + need > BUDGET_S:
            mark_not_run(stage, f"projected {need / 3600:.2f} h more at {elapsed / 3600:.2f} h elapsed would pass the "
                                f"{BUDGET_S / 3600:.2f} h GPU budget (plan's order: B-head, B-ft, A-head, A-ft)")
            continue
        say(f"{stage}: projected {need / 3600:.2f} h at {elapsed / 3600:.2f} h elapsed")
        run_a(stage)
    TIMES[f"stage {stage} finished at (s since start)"] = round(time.time() - T_START, 1)
    save_times()

# frozen DINOv2 / DINOv3 patch change of the Track B picture tile (label-free; for the picture only)
pic = FOLD_DIR / f"change_maps_{PIC_B}.npz"
if not pic.exists():
    _, _, c2, c3 = d3.change_maps(PIC_B)
    np.savez_compressed(pic, dinov2=c2, dinov3=c3)
(FOLD_DIR / "gpu_settings.json").write_text(json.dumps(SETTINGS, indent=1))
TIMES["total this run (s)"] = round(time.time() - T_START, 1)
save_times()
say("done")
