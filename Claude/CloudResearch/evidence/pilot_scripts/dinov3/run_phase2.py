"""Phase 2 of the DINOv3 benchmark (outputs/preregistration_dinov3_baseline.md, "Phase 2: fine-tuning"): DINOv3
(SAT-493M) fine-tuned on the 186 training tiles only, scored once on the 40 validation tiles against frozen DINOv3 and
frozen DINOv2 on the same validation cells and roads. Research benchmark only.

Run from this folder, in the background:
    /opt/miniconda3/bin/python3 -I run_phase2.py trunk > trunk.log 2>&1   # the frozen-trunk cache only (no training)
    /opt/miniconda3/bin/python3 -I run_phase2.py > phase2.log 2>&1
Writes here: phase2_numbers.json, phase2_*.png, phase2_cues.csv. Checkpoints and the trunk cache go in
~/Masters/models/finetuned/dinov3_sat493m/. Nothing is written to ProjectBranch/Code/results."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
import os
SMOKE = os.environ.get("DINOV3_SMOKE") == "1"     # code check: 8 training + 3 validation tiles, RANDOM targets, 1 epoch
OUT = Path(os.environ["DINOV3_SMOKE_OUT"]) if SMOKE else HERE
sys.path.append(str(HERE))
import dinov3_bench as d3
import dinov3_finetune as ft
CKPT = OUT if SMOKE else ft.FT_DIR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

from sn8 import tile
from sn8_clouds import assessable
from sn8_cutoff import CUTS, _prf, cell_scores, weighted_f1
from sn8_data import split_tables
from sn8_detect import CELL_FEATURES, CELL_PX, tile_cells
from sn8_dino import DINO_CUES, with_dino
from sn8_dino_cells import DINO_CELL_FEATURES
from sn8_grey import GREY_DIR
from sn8_heldout import held_out_report, paired_report, touched_roads
from sn8_lines import draw_roads, road_band
from sn8_models import FLOOD_MODELS
from sn8_stages import production_cloud_rule, production_features, production_model
from sn8_torchgeo import tile_pair

SEED = 662
T0 = time.time()
TIMES, HISTORY = {}, {}
DEVICE = d3.backbone3()[1]
SETTINGS = {
    "trunk depth (frozen, cached)": ft.TRUNK_DEPTH,
    "A-ft": {"trained blocks": 2, "lr blocks": 2e-5, "lr head": 1e-3, "max epochs": 20, "patience": 4},
    "A-head": {"trained blocks": 0, "lr head": 1e-3, "max epochs": 12, "patience": 3},
    "B-ft": {"trained blocks": 2, "lr blocks": 1e-5, "lr head": 1e-3, "max epochs": 10, "patience": 3},
    "epoch": "one random window (of those holding target cells) from every fit tile; one optimiser step per tile",
    "per-epoch evaluation": "a fixed seeded subset of 2 target windows per inner-validation tile",
    "B-head": {"trained blocks": 0, "lr head": 1e-3, "batch (patches)": 256, "max epochs": 40, "patience": 3},
    "optimiser": "AdamW (weight decay 0.05 blocks, 1e-4 head), gradient norm clipped at 1, float32",
    "inner split": "train_test_split of the 186 training tiles, 20% inner-validation, stratified on flood class, seed 662",
    "cross-fit folds (Track B)": "StratifiedGroupKFold(5, shuffle=True, random_state=662) on the training roads by tile",
    "B-ft folds": "5, the same folds as B-head (amendment 03:12: the code check measured the GPU at full speed)",
}


def say(*a):
    print(f"[{time.time() - T0:7.0f} s]", *a, flush=True)


def timed(name, fn, *args, **kw):
    t = time.time()
    out = fn(*args, **kw)
    TIMES[name] = round(time.time() - t, 1)
    say(f"{name}: {TIMES[name]} s")
    return out


def tidy(df):
    return json.loads(df.to_json(orient="records", double_precision=4))


# ---------- data: training tiles to fit, validation tiles to score; nothing else ----------
df, train, val, test, negative = split_tables(SEED)
index = pd.read_csv(GREY_DIR / "tiles.csv")
assert len(train) == 186 and len(val) == 40
assert set(train.tile_id) == set(index.tile_id[index.split == "train"])
assert set(val.tile_id) == set(index.tile_id[index.split == "val"])
assert not (set(train.tile_id) | set(val.tile_id)) & (set(test.tile_id) | set(negative.tile_id))
del test, negative                       # never used below
TRAIN, VAL = list(train.tile_id), list(val.tile_id)
inner_fit, inner_val = train_test_split(train, test_size=0.2, stratify=train.flood_class, random_state=SEED)
INNER_FIT, INNER_VAL = sorted(inner_fit.tile_id), sorted(inner_val.tile_id)
if SMOKE:
    TRAIN, VAL, INNER_FIT, INNER_VAL = INNER_FIT[:6] + INNER_VAL[:2], VAL[:3], INNER_FIT[:6], INNER_VAL[:2]
    for name in SETTINGS:
        if isinstance(SETTINGS[name], dict) and "max epochs" in SETTINGS[name]:
            SETTINGS[name]["max epochs"] = 1
assert not set(INNER_FIT) & set(INNER_VAL) and set(INNER_FIT) | set(INNER_VAL) == set(TRAIN)
say(f"inner split: {len(INNER_FIT)} fit / {len(INNER_VAL)} inner-validation training tiles; {len(VAL)} validation tiles")

# ---------- the frozen trunk, cached ----------
for k, t in enumerate(TRAIN + VAL):
    for date in ("before", "after"):
        ft.trunk(t, date)
    if k % 20 == 0:
        say(f"trunk cache: {k + 1} of {len(TRAIN) + len(VAL)} tiles")
TIMES["trunk cache (s)"] = round(time.time() - T0, 1)
say("trunk cached in", ft.trunk_dir())
if len(sys.argv) > 1 and sys.argv[1] == "trunk":      # cache only (no training): run_phase2.py trunk
    sys.exit(0)

roads = d3.with_dino3(with_dino(touched_roads(include_cloudy=True)))
assert set(roads.split) <= {"train", "val"}
keep_rule = assessable(roads, production_cloud_rule())
keep_tile = ~roads.cloudy.astype(bool).to_numpy()
ROWS_OF = roads.groupby("tile_id", sort=False).indices          # each tile's rows, in feature_table order
_target = keep_rule & (roads.split == "train").to_numpy()
TARGET_ROADS = {t: {i for i, r in enumerate(ROWS_OF.get(t, [])) if _target[r]} for t in TRAIN}   # positions

# check: trunk (float16 cache) + the 4 frozen top blocks reproduce dinov3_bench.tokens3 on a training tile
from scipy import ndimage as ndi
from sn8_lines import NODATA_ERODE_PX
_p = tile_pair(TRAIN[0])
_ref = d3.tokens3(_p["before_grey"], ndi.binary_erosion(_p["before_grey"] > 0, iterations=NODATA_ERODE_PX))
_top = ft.Top(4).to(DEVICE).eval()
_tb = ft.trunk(TRAIN[0], "before")
_mine = np.zeros_like(_ref)
with torch.no_grad():
    for k, (r, c, _, _) in enumerate(ft.window_slices(_tb["grid"])):
        h = torch.from_numpy(_tb["windows"][k][None].astype(np.float32)).to(DEVICE)
        _mine[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = _top(h, (len(r), len(c)))[0].cpu().numpy().reshape(len(r), len(c), -1)
_cos = (_ref * _mine).sum(-1) / np.linalg.norm(_ref, axis=-1) / np.linalg.norm(_mine, axis=-1)
say(f"trunk reproduction on {TRAIN[0]}: cosine to tokens3 min {_cos.min():.5f}, mean {_cos.mean():.6f}")
assert _cos.min() > 0.99
TIMES["trunk reproduction cosine (min)"] = float(_cos.min())
del _p, _ref, _top, _tb, _mine

band = road_band()
LAYOUT = {t: ft.strip_layout(t, band) for t in TRAIN + VAL}
for t in TRAIN + VAL:   # the layout keeps the same roads, in the same order, as the roads table
    assert [r[1] for r in LAYOUT[t][0]] == roads.road_id.to_numpy()[ROWS_OF.get(t, [])].tolist(), t
GRID = {t: ft.trunk(t, "before")["grid"] for t in TRAIN + VAL}
A_TARGET = {t: ft.road_cell_grid(t, GRID[t]) for t in TRAIN}
B_TARGET = {t: ft.flood_cell_grid(LAYOUT[t], TARGET_ROADS[t]) for t in TRAIN}
say("targets built:", sum(int((A_TARGET[t] >= 0).sum()) for t in TRAIN), "labelled training cells (Track A);",
    sum(int((B_TARGET[t] >= 0).sum()) for t in TRAIN), "strip cells of", sum(len(v) for v in TARGET_ROADS.values()),
    "assessed training roads (Track B)")

# check: the Track A targets equal the library's cell labels at the validation-style sample of training cells
from sn8_detect import cell_table
ct = cell_table("train")
for t in TRAIN[:5]:
    c = ct[ct.tile_id == t]
    assert (A_TARGET[t][c.row.values, c.col.values] == c.label.values).all(), t
if SMOKE:   # no label information in a code check: random 0/1 where a target exists
    _rng = np.random.default_rng(0)
    for _g in list(A_TARGET.values()) + list(B_TARGET.values()):
        _g[_g >= 0] = _rng.integers(0, 2, int((_g >= 0).sum()))

# ---------- Track A ----------
def a_run(name, n_frozen, s):
    t = time.time()
    top, head, hist = ft.train_epochs("A", INNER_FIT, A_EVAL, A_TARGET, n_frozen, s["max epochs"],
                                      s.get("lr blocks", 0.0), s["lr head"], DEVICE, say, patience=s["patience"],
                                      ckpt=CKPT / f"trackA_{name}.pt")
    HISTORY[name] = hist
    TIMES[f"{name} training (s)"] = round(time.time() - t, 1)
    # cut-off: best F1 over every labelled cell of the inner-validation tiles (the natural road share)
    y, p = [], []
    for tid in INNER_VAL:
        g = ft.predict_grid(top, head, tid, "A", DEVICE)
        m = A_TARGET[tid] >= 0
        y.append(A_TARGET[tid][m])
        p.append(g[m])
    y, p = np.concatenate(y), np.concatenate(p)
    f1 = [weighted_f1(y, p >= c, np.ones(len(y))) for c in CUTS]
    cut = float(CUTS[int(np.argmax(f1))])
    return top, head, cut, max(f1)


phase1 = np.load(HERE / "phase1_trackA_val.npz")
cells_val = pd.DataFrame({"tile_id": phase1["tile_id"], "row": phase1["row"], "col": phase1["col"],
                          "label": phase1["label"]})
if SMOKE:
    cells_val = cells_val[cells_val.tile_id.isin(VAL)].reset_index(drop=True)
    _keep = np.flatnonzero(np.isin(phase1["tile_id"], VAL))
assert set(cells_val.tile_id) <= set(VAL)
A_MODELS, A_PROB, A_CUT = {}, {}, {}
A_EVAL = ft.eval_windows(INNER_VAL, A_TARGET)
for name, n_frozen in (("A-head", 4), ("A-ft", 2)):
    top, head, cut, inner_f1 = a_run(name, n_frozen, SETTINGS[name])
    A_CUT[name] = cut
    prob = np.zeros(len(cells_val), np.float32)
    for tid, idx in cells_val.groupby("tile_id", sort=False).indices.items():
        g = ft.predict_grid(top, head, tid, "A", DEVICE)
        prob[idx] = g[cells_val.row.values[idx], cells_val.col.values[idx]]
    A_PROB[name] = prob
    A_MODELS[name] = (top, head)
    say(f"{name}: inner-validation F1 {inner_f1:.3f} at cut-off {cut:.2f}")

yv, tv = cells_val.label.to_numpy(), cells_val.tile_id.to_numpy()
frozen_a = {str(n): (float(c), pr[_keep] if SMOKE else pr) for n, c, pr in zip(phase1["names"], phase1["cuts"], phase1["probs"])}
called = {f"{n} ({frozen_a[n][0]:.2f})": frozen_a[n][1] >= frozen_a[n][0] for n in
          ("classical", "classical + DINOv2", "DINOv2 only", "classical + DINOv3", "DINOv3 only")}
for name in ("A-head", "A-ft"):
    called[f"DINOv3 {'linear head on frozen tokens' if name == 'A-head' else 'fine-tuned (last 2 blocks + head)'} "
           f"({A_CUT[name]:.2f})"] = A_PROB[name] >= A_CUT[name]
lab = {k.rsplit(" (", 1)[0]: k for k in called}
track_a = cell_scores(yv, called, tv)
counts = [{"arm": k, "TP": int(((yv == 1) & c).sum()), "FN": int(((yv == 1) & ~c).sum()),
           "FP": int(((yv == 0) & c).sum()), "TN": int(((yv == 0) & ~c).sum())} for k, c in called.items()]
FT_A, HEAD_A = "DINOv3 fine-tuned (last 2 blocks + head)", "DINOv3 linear head on frozen tokens"
pairs_a = [(FT_A, "classical + DINOv2"), (FT_A, "DINOv2 only"), (FT_A, "DINOv3 only"), (FT_A, "classical + DINOv3"),
           (FT_A, HEAD_A), (HEAD_A, "DINOv3 only"), (HEAD_A, "classical + DINOv2")]
track_a_pairs = []
for cand, against in pairs_a:
    s = cell_scores(yv, {lab[against]: called[lab[against]], lab[cand]: called[lab[cand]]}, tv).iloc[1]
    track_a_pairs.append({"arm": lab[cand], "against": lab[against], "F1": s["F1"], "F1 difference": s.iloc[6],
                          "95% CI of the difference": s["95% CI of the difference"]})
track_a_pairs = pd.DataFrame(track_a_pairs)
say("Track A (validation cells)\n" + track_a.to_string() + "\n" + track_a_pairs.to_string())

# ---------- Track B ----------
train_roads = roads[roads.split == "train"].reset_index(drop=True)
fold_of_tile = {}
for f, (_, te) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=SEED).split(
        train_roads, train_roads.flooded.astype(int), groups=train_roads.tile_id)):
    for t in train_roads.tile_id.iloc[te].unique():
        fold_of_tile[t] = f
for t in TRAIN:
    fold_of_tile.setdefault(t, int(np.random.default_rng(SEED).integers(5)))   # tiles with no roads (no targets)


def cues_from_grids(grids, prefix):
    """Per-road cues in the roads table's row order (NaN for roads on tiles not in `grids`)."""
    out = pd.DataFrame(np.nan, index=roads.index, columns=[f"{prefix}_{s}" for s in ("mean", "max", "share")])
    for t, g in grids.items():
        cues = ft.road_cues(LAYOUT[t], g, prefix)
        rows = ROWS_OF.get(t, [])
        assert [c["road_id"] for c in cues] == roads.road_id.to_numpy()[rows].tolist(), t
        for r, c in zip(rows, cues):
            out.loc[r, list(out.columns)] = [c[col] for col in out.columns]
    return out


# B-head: frozen DINOv3 final tokens of the strip patches, computed once
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


def patch_targets(t, idx):
    n_r, n_c = GRID[t]
    g = B_TARGET[t].reshape(n_r, ft.SUB, n_c, ft.SUB).transpose(0, 2, 1, 3).reshape(n_r * n_c, ft.SUB * ft.SUB)
    return g[idx]


t_tok = time.time()
frozen_top = ft.Top(4).to(DEVICE).eval()
STRIP = {t: strip_tokens(t, frozen_top) for t in TRAIN + VAL}
del frozen_top
TIMES["B-head strip tokens (s)"] = round(time.time() - t_tok, 1)
say("B-head strip tokens:", sum(len(v[0]) for v in STRIP.values()), "patches")


def head_data(tiles):
    xb = np.concatenate([STRIP[t][1] for t in tiles])
    xa = np.concatenate([STRIP[t][2] for t in tiles])
    y = np.concatenate([patch_targets(t, STRIP[t][0]) for t in tiles])
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


def train_head(fit_tiles, eval_tiles, epochs, patience, name):
    s = SETTINGS["B-head"]
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    head = ft.FloodHead().to(DEVICE)
    opt = torch.optim.AdamW(head.parameters(), lr=s["lr head"], weight_decay=1e-4)
    xb, xa, y = head_data(fit_tiles)
    ev = head_data(eval_tiles) if eval_tiles else None
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
                best, waited, best_state = row["eval loss"], 0, ({k: v.clone() for k, v in head.state_dict().items()}, epoch)
            else:
                waited += 1
                if waited >= patience:
                    break
    if best_state is not None:
        head.load_state_dict(best_state[0])
    HISTORY[name] = hist
    return head, (best_state[1] if best_state else epochs)


def head_grid(head, t):
    n_r, n_c = GRID[t]
    idx, fb, fa = STRIP[t]
    prob = np.full(n_r * n_c * ft.SUB * ft.SUB, np.nan, np.float32).reshape(n_r * n_c, ft.SUB * ft.SUB)
    if len(idx):
        head.eval()
        with torch.no_grad():
            prob[idx] = torch.sigmoid(head(torch.from_numpy(fb.astype(np.float32)).to(DEVICE),
                                           torch.from_numpy(fa.astype(np.float32)).to(DEVICE))).cpu().numpy()
    return prob.reshape(n_r, n_c, ft.SUB, ft.SUB).transpose(0, 2, 1, 3).reshape(n_r * ft.SUB, n_c * ft.SUB)


t_b = time.time()
_, E_HEAD = train_head(INNER_FIT, INNER_VAL, SETTINGS["B-head"]["max epochs"], SETTINGS["B-head"]["patience"],
                       "B-head inner")
say(f"B-head: {E_HEAD} epochs chosen on the inner-validation tiles")
head_grids, head_val = {}, {t: [] for t in VAL}
for f in range(5):
    fit = [t for t in TRAIN if fold_of_tile[t] != f]
    head, _ = train_head(fit, None, E_HEAD, None, f"B-head fold {f}")
    torch.save(head.state_dict(), CKPT / f"trackB_head_fold{f}.pt")
    for t in TRAIN:
        if fold_of_tile[t] == f:
            head_grids[t] = head_grid(head, t)
    for t in VAL:
        head_val[t].append(head_grid(head, t))
head_grids.update({t: np.mean(g, 0) for t, g in head_val.items()})
TIMES["B-head training + cues (s)"] = round(time.time() - t_b, 1)
HEAD_CUES = cues_from_grids(head_grids, "d3head_flood")

# B-ft: last 2 blocks trained (shared by both dates) + head
t_b = time.time()
epoch_s = []
top, head, hist = ft.train_epochs("B", INNER_FIT, ft.eval_windows(INNER_VAL, B_TARGET), B_TARGET, 2,
                                  SETTINGS["B-ft"]["max epochs"],
                                  SETTINGS["B-ft"]["lr blocks"], SETTINGS["B-ft"]["lr head"], DEVICE, say,
                                  patience=SETTINGS["B-ft"]["patience"], ckpt=CKPT / "trackB_ft_inner.pt",
                                  epoch_seconds=epoch_s)
HISTORY["B-ft inner"] = hist
E_FT = int(np.argmin([h["eval loss"] for h in hist]) + 1)
N_FOLDS_FT = 5
say(f"B-ft: {E_FT} epochs chosen; mean epoch {np.mean(epoch_s):.0f} s; {N_FOLDS_FT} cross-fit folds")
del top, head
fold_ft = dict(fold_of_tile)
ft_grids, ft_val = {}, {t: [] for t in VAL}
for f in range(N_FOLDS_FT):
    fit = [t for t in TRAIN if fold_ft[t] != f]
    top, head, hist = ft.train_epochs("B", fit, None, B_TARGET, 2, E_FT, SETTINGS["B-ft"]["lr blocks"],
                                      SETTINGS["B-ft"]["lr head"], DEVICE, say, ckpt=CKPT / f"trackB_ft_fold{f}.pt")
    HISTORY[f"B-ft fold {f}"] = hist
    for t in TRAIN:
        if fold_ft[t] == f:
            ft_grids[t] = ft.predict_grid(top, head, t, "B", DEVICE)
    for t in VAL:
        ft_val[t].append(ft.predict_grid(top, head, t, "B", DEVICE))
    del top, head
ft_grids.update({t: np.mean(g, 0) for t, g in ft_val.items()})
TIMES["B-ft training + cues (s)"] = round(time.time() - t_b, 1)
FT_CUES = cues_from_grids(ft_grids, "d3ft_flood")

H3 = [f"d3head_flood_{s}" for s in ("mean", "max", "share")]
T3 = [f"d3ft_flood_{s}" for s in ("mean", "max", "share")]
for cues in (HEAD_CUES, FT_CUES):
    for col in cues.columns:
        roads[col] = cues[col].to_numpy()
pd.concat([roads[["tile_id", "road_id", "split", "flooded", "cloudy"]], roads[H3 + T3]], axis=1).to_csv(
    OUT / "phase2_cues.csv", index=False)

# the production random forest, fitted on training roads, scored once on validation roads
make = FLOOD_MODELS[production_model()]
base = [c for c in production_features() if c not in DINO_CUES]
assert len(base) == 93
B_ARMS = {"base (production without DINO)": base, "base + DINOv2 cues (production)": base + DINO_CUES,
          "base + DINOv3 cues (frozen)": base + d3.DINO3_CUES,
          "base + DINOv2 cues + DINOv3 head cues": base + DINO_CUES + H3,
          "base + DINOv2 cues + DINOv3 fine-tuned cues": base + DINO_CUES + T3,
          "base + DINOv3 head cues": base + H3, "base + DINOv3 fine-tuned cues": base + T3,
          "DINOv2 cues": DINO_CUES, "DINOv3 cues (frozen)": d3.DINO3_CUES, "DINOv3 head cues": H3,
          "DINOv3 fine-tuned cues": T3}
PROD = "base + DINOv2 cues (production)"
B_PAIRS = [("base + DINOv2 cues + DINOv3 fine-tuned cues", PROD), ("base + DINOv2 cues + DINOv3 head cues", PROD),
           ("base + DINOv3 fine-tuned cues", PROD), ("base + DINOv3 fine-tuned cues", "base + DINOv3 cues (frozen)"),
           ("base + DINOv3 head cues", "base + DINOv3 cues (frozen)"), ("base + DINOv3 cues (frozen)", PROD),
           ("base + DINOv2 cues + DINOv3 fine-tuned cues", "base + DINOv2 cues + DINOv3 head cues"),
           ("DINOv3 fine-tuned cues", "DINOv2 cues"), ("DINOv3 fine-tuned cues", "DINOv3 cues (frozen)"),
           ("DINOv3 head cues", "DINOv3 cues (frozen)"), ("DINOv3 cues (frozen)", "DINOv2 cues")]


def confusion(preds, rs):
    r = held_out_report(preds, rs).set_index("features")
    r = r.loc[list(preds) + ['always "flooded"']].reset_index()
    r.insert(r.columns.get_loc("flooded found"), "precision", (r.TP / (r.TP + r.FP)).round(3))
    r.insert(r.columns.get_loc("dry kept dry") + 1, "F1", (2 * r.TP / (2 * r.TP + r.FP + r.FN)).round(3))
    return r.rename(columns={"flooded found": "recall"})


def paired(preds, rs, pairs):
    rows = []
    for cand, against in pairs:
        r = paired_report({against: preds[against], cand: preds[cand]}, against, rs).iloc[0].to_dict()
        rows.append({"arm": cand, "against": against, "accuracy difference": r[f"vs {against}"], "95% CI": r["95% CI"],
                     "roads fixed": r["roads fixed"], "roads broken": r["roads broken"], "McNemar p": r["McNemar p"]})
    return pd.DataFrame(rows)


B_TABLES, B_PRED = {}, {}
for set_name, keep in (("tile rule", keep_tile), ("production cloud rule", keep_rule)):
    rs = roads[keep]
    if SMOKE:
        rs = rs[rs.tile_id.isin(TRAIN + VAL)]
    tr, te = rs[rs.split == "train"], rs[rs.split == "val"].reset_index(drop=True)
    assert set(te.tile_id) <= set(VAL) and set(tr.tile_id) <= set(TRAIN)
    y_tr = tr.flooded.astype(int).to_numpy()
    if SMOKE:
        y_tr = np.random.default_rng(0).permutation(y_tr)    # code check only: no label information
    preds = {n: make().fit(tr[cols], y_tr).predict(te[cols]) for n, cols in B_ARMS.items()}
    B_PRED[set_name] = (te, preds)
    B_TABLES[set_name] = {"roads": {"train": len(tr), "validation": len(te), "validation tiles": te.tile_id.nunique()},
                          "confusion": confusion(preds, te), "paired": paired(preds, te, B_PAIRS)}
    say(f"Track B, {set_name}: {len(tr)} training roads -> {len(te)} validation roads\n"
        + B_TABLES[set_name]["confusion"].to_string() + "\n" + B_TABLES[set_name]["paired"].to_string())

# ---------- pictures ----------
VAL_TILE_B = VAL[0] if SMOKE else val.nlargest(1, "roads_flooded").tile_id.iloc[0]
VAL_TILE_A = VAL[1] if SMOKE else val.nlargest(1, "roads").tile_id.iloc[0]
t_pic = time.time()
fig, ax = plt.subplots(1, 3, figsize=(20, 5))
for a, keys in zip(ax, (["A-head", "A-ft"], ["B-head inner"], ["B-ft inner"])):
    for k in keys:
        h = pd.DataFrame(HISTORY[k])
        a.plot(h.epoch, h["train loss"], "o-", label=f"{k}: training (inner-fit tiles)")
        a.plot(h.epoch, h["eval loss"], "s--", label=f"{k}: inner-validation tiles")
    a.set_xlabel("epoch")
    a.set_ylabel("masked BCE per cell")
    a.legend(fontsize=8)
for a, title in zip(ax, ("Track A: road cells", "Track B: flood head on frozen tokens", "Track B: last 2 blocks + head")):
    a.set_title(title)
fig.text(0.5, 0.005, "Training split only (186 tiles: inner fit / inner validation). Validation tiles not used here.",
         ha="center", fontsize=9)
plt.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "phase2_loss_curves.png", dpi=90)
plt.close(fig)

# Track B picture: before, after, frozen DINOv3 change, head and fine-tuned flood probability, labelled roads
p = tile_pair(VAL_TILE_B)
_, _, c2, c3 = d3.change_maps(VAL_TILE_B)
fig, axes = plt.subplots(2, 3, figsize=(24, 16))
axes[0, 0].imshow(p["before_grey"], cmap="gray", vmin=0, vmax=255)
axes[0, 0].set_title(f"{VAL_TILE_B} before (greyscale)")
axes[0, 1].imshow(p["after_grey"], cmap="gray", vmin=0, vmax=255)
axes[0, 1].set_title("after (greyscale)")
for a, ch, patch, title in ((axes[0, 2], c2, 14, "frozen DINOv2 patch change (7 m)"),
                            (axes[1, 0], c3, 16, "frozen DINOv3 patch change (8 m)")):
    im = a.imshow(ch, cmap="magma", vmin=0, vmax=np.nanpercentile(ch, 99),
                  extent=(0, ch.shape[1] * patch, ch.shape[0] * patch, 0))
    a.set_title(title + ", 1 - cosine")
    plt.colorbar(im, ax=a, fraction=0.04)
for a, g, title in ((axes[1, 1], head_grids[VAL_TILE_B], "DINOv3 head on frozen tokens: P(flooded), 2 m cells"),
                    (axes[1, 2], ft_grids[VAL_TILE_B], "DINOv3 fine-tuned (last 2 blocks + head): P(flooded)")):
    a.imshow(p["after_grey"], cmap="gray", vmin=0, vmax=255)
    im = a.imshow(np.ma.masked_invalid(np.where(LAYOUT[VAL_TILE_B][2] > 0, g, np.nan)), cmap="coolwarm", vmin=0,
                  vmax=1, extent=(0, g.shape[1] * CELL_PX, g.shape[0] * CELL_PX, 0), alpha=0.85)
    a.set_title(title + "\n(road strips only; mean of the 5 fold models, none saw this tile)")
    plt.colorbar(im, ax=a, fraction=0.04)
for a in axes.flat:
    draw_roads(a, tile(VAL_TILE_B)["label"], (p["x0"], p["y0"]))
    a.set_xlim(0, p["before_grey"].shape[1])
    a.set_ylim(p["before_grey"].shape[0], 0)
    a.axis("off")
fig.text(0.5, 0.01, f"{d3.CREDIT3}. Labelled roads: red flooded, cyan dry. Fixed rule: the validation tile with the "
         "most flooded roads.", ha="center", fontsize=11)
plt.tight_layout(rect=(0, 0.025, 1, 1))
fig.savefig(OUT / f"phase2_flood_maps_{VAL_TILE_B}.png", dpi=75)
plt.close(fig)

# Track A picture: every cell of the validation tile with the most labelled roads, fine-tuned DINOv3
from matplotlib.colors import ListedColormap
c = tile_cells(VAL_TILE_A).reset_index(drop=True)
p = tile_pair(VAL_TILE_A)
fig, axes = plt.subplots(1, 2, figsize=(16, 8.6))
for a, name in zip(axes, ("A-head", "A-ft")):
    g = ft.predict_grid(*A_MODELS[name], VAL_TILE_A, "A", DEVICE)
    found = g[c.row.values, c.col.values] >= A_CUT[name]
    labv = c.label.to_numpy()
    shape = (c.row.max() + 1, c.col.max() + 1)
    outcome = np.full(shape, np.nan)
    for v, m in ((0, (labv == 1) & found), (1, (labv == 0) & found), (2, (labv == 1) & ~found)):
        outcome[c.row.values[m], c.col.values[m]] = v
    tp, fp, fn = int(((labv == 1) & found).sum()), int(((labv == 0) & found).sum()), int(((labv == 1) & ~found).sum())
    a.imshow(p["before_grey"], cmap="gray", vmin=0, vmax=255)
    a.imshow(outcome, cmap=ListedColormap(["limegreen", "red", "dodgerblue"]), vmin=0, vmax=2, alpha=0.7,
             extent=(0, shape[1] * CELL_PX, shape[0] * CELL_PX, 0))
    a.set_title(f"{VAL_TILE_A}: {FT_A if name == 'A-ft' else HEAD_A}, cut-off {A_CUT[name]:.2f}\n"
                f"green found {tp} | red not road {fp} | blue missed {fn} | precision {tp / max(tp + fp, 1):.2f}, "
                f"recall {tp / max(tp + fn, 1):.2f}", fontsize=10)
    a.set_xlim(0, p["before_grey"].shape[1])
    a.set_ylim(p["before_grey"].shape[0], 0)
    a.axis("off")
fig.text(0.5, 0.01, f"{d3.CREDIT3}. Fixed rule: the validation tile with the most labelled roads.", ha="center",
         fontsize=10)
plt.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / f"phase2_cells_{VAL_TILE_A}.png", dpi=80)
plt.close(fig)
TIMES["pictures (s)"] = round(time.time() - t_pic, 1)

# ---------- log ----------
git = subprocess.run(["git", "-C", str(Path(d3.FUNCS).parent), "rev-parse", "--short", "HEAD"], capture_output=True,
                     text=True).stdout.strip()
numbers = {
    "run": time.strftime("%Y-%m-%dT%H:%M:%S"), "plan": "outputs/preregistration_dinov3_baseline.md (Phase 2)",
    "GeoAI-Roads commit": git, "model": d3.MODEL3, "licence": d3.LICENCE3, "settings": SETTINGS,
    "code hashes": {q.name: hashlib.sha256(q.read_bytes()).hexdigest()[:12]
                    for q in [*sorted(Path(d3.FUNCS).glob("sn8*.py")), HERE / "dinov3_bench.py",
                              HERE / "dinov3_finetune.py", Path(__file__)]},
    "data": {"inner fit tiles": len(INNER_FIT), "inner validation tiles": len(INNER_VAL), "validation tiles": len(VAL),
             "Track A labelled training cells": int(sum((A_TARGET[t] >= 0).sum() for t in TRAIN)),
             "Track B target strip cells": int(sum((B_TARGET[t] >= 0).sum() for t in TRAIN)),
             "Track B target roads": int(sum(len(v) for v in TARGET_ROADS.values()))},
    "chosen": {"A cut-offs (inner validation)": A_CUT, "B-head epochs": E_HEAD, "B-ft epochs": E_FT,
               "B-ft folds": N_FOLDS_FT},
    "times (s)": {**TIMES, "total": round(time.time() - T0, 1)},
    "loss curves": HISTORY,
    "Track A": {"validation cells": tidy(track_a), "counts": counts, "pairs": tidy(track_a_pairs)},
    "Track B": {k: {"roads": v["roads"], "confusion": tidy(v["confusion"]), "paired": tidy(v["paired"])}
                for k, v in B_TABLES.items()},
    "pictures": {"tile B": VAL_TILE_B, "tile A": VAL_TILE_A},
}
(OUT / "phase2_numbers.json").write_text(json.dumps(numbers, indent=1, default=float))
say("done; numbers in phase2_numbers.json")
