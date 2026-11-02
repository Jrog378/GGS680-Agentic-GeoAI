"""Spatial cross-validation of the DINOv3 research benchmark (Agent C), shared setup. Research only.

Plan: outputs/preregistration_spatial_cv.md, "Agent C" and "Decision rules" (written before any model was scored on
the new folds). Justin (2026-10-26): "can you do a cross validation so that you dont overfit".

DINOv3 (timm vit_large_patch16_dinov3.sat493m, Meta DINOv3 License) is a research benchmark only (Justin: "we will not
use dinov3 in the library, it is only for research and benchmarking our other models"). This file lives in the research
folder; nothing in ProjectBranch/ClaudeFunctions imports it, and nothing is written to production.json.

Development data only: the 186 train + 40 val tiles of Louisiana-East and their 1,037 touched roads. The folds are the
seed-662 spatial folds of evidence/pilot_scripts/spatial_cv/spatial_folds.py (3 x 3-tile blocks, purge route), imported
and not edited.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCV = HERE.parent / "spatial_cv"
for _p in (str(HERE), str(SCV)):
    if _p not in sys.path:
        sys.path.append(_p)
import dinov3_bench as d3            # puts ClaudeFunctions on sys.path (does not load the model on import)

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import matthews_corrcoef

from spatial_folds import (cell_folds, dev_roads, fold_table, nested_cell_folds, nested_spatial_folds, spatial_folds,
                           tile_folds)

SEED = 662
N_FOLDS = 5
OUT = HERE                                            # numbers, calls, logs, pictures: spatialcv_* files here
FOLD_DIR = HERE / "spatialcv_folds"                   # per-outer-fold outputs, written as each fold finishes
WEIGHTS = Path.home() / "Masters" / "models" / "finetuned" / "dinov3_sat493m" / "spatial_cv"
PROD = "base + DINOv2 cues (production)"
BEST = "base + DINOv2 cues + vector (best combo)"


def dev_split():
    """The 186 training and 40 validation tiles (sorted ids) and their tables. Splits are taken by name; the test and
    negative tables are dropped at once and never looked at."""
    from sn8_data import split_tables
    df, train, val, test, negative = split_tables()
    del df, test, negative
    assert len(train) == 186 and len(val) == 40
    return sorted(train.tile_id), sorted(val.tile_id), train, val


def tile_folds_662():
    """Tile-level folds from spatial_folds.fold_table(662) and nested_cell_folds over the 226 tile ids:
    (fold table, {tile: outer fold}, [{tile: inner fold} for each outer fold])."""
    ft = fold_table(SEED)
    assert len(ft) == 226 and set(ft.split) == {"train", "val"}
    ids = ft.tile_id.to_numpy()
    tile_fold = dict(zip(ft.tile_id, ft.fold.astype(int)))
    inner_of = []
    for k, (tr, te, inner) in enumerate(nested_cell_folds(ids, SEED)):
        assert all(tile_fold[t] == k for t in ids[te]) and all(tile_fold[t] != k for t in ids[tr])
        inner_of.append({t: j for j, (_, ite) in enumerate(inner) for t in ids[ite]})
        assert set(inner_of[-1]) == set(ids[tr])
    return ft, tile_fold, inner_of


def with_dino3_cached(roads):
    """dinov3_bench.with_dino3 from its cached files, without loading the DINOv3 model (for CPU-only processes).
    Exactly one cache file per split must exist; rows are checked against feature_table as dinov3_bench does."""
    from sn8_roads import feature_table
    parts = []
    for split in ("train", "val"):
        csv = sorted(d3.CACHE_DIR.glob(f"road_{d3.MODEL3}_{split}_*.csv"))
        npz = sorted(d3.CACHE_DIR.glob(f"road_{d3.MODEL3}_{split}_*.npz"))
        assert len(csv) == 1 and len(npz) == 1 and csv[0].stem == npz[0].stem, f"DINOv3 road cache for {split}"
        d = pd.read_csv(csv[0])
        ref = feature_table(split)
        assert d.tile_id.equals(ref.tile_id) and d.road_id.equals(ref.road_id)
        z = np.load(npz[0])
        parts.append(pd.concat([d, pd.DataFrame(z["after"] - z["before"], columns=d3.DINO3_VECTOR)], axis=1))
    d = pd.concat(parts, ignore_index=True)
    assert len(d) == len(roads) and d.tile_id.equals(roads.tile_id.reset_index(drop=True)) and \
        d.road_id.equals(roads.road_id.reset_index(drop=True))
    return pd.concat([roads.reset_index(drop=True), d[d3.DINO3_CUES + d3.DINO3_VECTOR]], axis=1)


def load_roads(gpu=False):
    """The 1,037 development roads (touched_roads(include_cloudy=True), unfiltered, the order of spatial_folds.dev_roads)
    with the DINOv2 and DINOv3 cues and vectors, plus the masks: production's cloud rule (the 798) and the tile rule
    (the 891). Returns (roads, rule798, rule891)."""
    from sn8_clouds import assessable
    from sn8_dino import with_dino
    from sn8_heldout import touched_roads
    from sn8_stages import production_cloud_rule
    r = with_dino(touched_roads(include_cloudy=True))
    r = d3.with_dino3(r) if gpu else with_dino3_cached(r)
    assert set(r.split) <= {"train", "val"}, "development roads only"
    d = dev_roads()
    assert r.tile_id.equals(d.tile_id) and r.road_id.equals(d.road_id) and len(r) == 1037
    assert (r.flooded.astype(bool).to_numpy() == d.flooded.to_numpy()).all()
    rule = np.asarray(assessable(r, production_cloud_rule()), bool)
    tile_rule = ~r.cloudy.astype(bool).to_numpy()
    assert (rule == d.production_rule.to_numpy()).all() and (tile_rule == d.tile_rule.to_numpy()).all()
    assert rule.sum() == 798 and tile_rule.sum() == 891
    return r, rule, tile_rule


def road_folds(roads):
    """The seed-662 nested spatial folds over the 1,037 roads: [(outer_train, outer_test, [(inner_train, inner_test),
    ...]), ...] (positions; purged, as spatial_folds does). Checked against spatial_folds."""
    nsf = nested_spatial_folds(roads, SEED)
    for (tr, te, _), (tr2, te2) in zip(nsf, spatial_folds(roads, SEED)):
        assert np.array_equal(tr, tr2) and np.array_equal(te, te2)
    return nsf


def subset_folds(roads, mask, scheme="S"):
    """Folds over the rows of roads[mask] (positions in that subset): "S" spatial (seed 662, purged), "T" the old tile
    folds split over the subset itself (as the logged arms were made). S folds are checked to be the 1,037's folds
    restricted to the subset."""
    sub = roads[mask].reset_index(drop=True)
    if scheme == "T":
        return sub, tile_folds(sub, SEED)
    folds = spatial_folds(sub, SEED)
    idx = np.flatnonzero(mask)
    for (tr, te), (tr8, te8) in zip(spatial_folds(roads, SEED), folds):
        assert np.array_equal(idx[te8], np.intersect1d(te, idx)) and np.array_equal(idx[tr8], np.intersect1d(tr, idx))
    return sub, folds


def limit_jobs(est, n):
    """Set every n_jobs parameter of an estimator (or pipeline) to n. A seeded random forest gives the same trees for
    any n_jobs; this only leaves the other agent its CPU cores."""
    params = {k: n for k in est.get_params(deep=True) if k.endswith("n_jobs")}
    return est.set_params(**params) if params else est


# ---------- scoring with block-resampled intervals ----------

def block_boot(blocks, n_boot, seed=SEED):
    """n_boot resamples of whole blocks (with replacement), as row-index arrays."""
    blocks = np.asarray(blocks)
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero(blocks == b) for b in np.unique(blocks)]
    return [np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))]) for _ in range(n_boot)]


def road_report(calls, y, blocks, n_boot=2000):
    """One row per arm ({name: 0/1 calls}): TP, FN, FP, TN, accuracy with a 95% block-resampled interval, precision,
    recall, specificity, F1, MCC. Always "flooded" is added."""
    y = np.asarray(y, int)
    boot = block_boot(blocks, n_boot)
    rows = []
    for name, p in {**calls, 'always "flooded"': np.ones(len(y), int)}.items():
        p = np.asarray(p, int)
        tp, fn = int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum())
        fp, tn = int(((y == 0) & (p == 1)).sum()), int(((y == 0) & (p == 0)).sum())
        acc = np.array([np.mean(y[i] == p[i]) for i in boot])
        rows.append({"arm": name, "TP": tp, "FN": fn, "FP": fp, "TN": tn, "accuracy": (tp + tn) / len(y),
                     "accuracy 95% CI": f"{np.percentile(acc, 2.5):.3f}-{np.percentile(acc, 97.5):.3f}",
                     "precision": tp / (tp + fp) if tp + fp else float("nan"), "recall": tp / (tp + fn),
                     "specificity": tn / (tn + fp) if tn + fp else float("nan"),
                     "F1": 2 * tp / (2 * tp + fp + fn) if tp else 0.0, "MCC": matthews_corrcoef(y, p)})
    return pd.DataFrame(rows)


def paired(cand, base, y, blocks, n_boot=5000):
    """Candidate minus baseline accuracy on the same roads: difference, 95% block-resampled interval (5,000 resamples,
    seed 662), roads fixed and broken, exact McNemar p (binomial test on the discordant roads)."""
    y = np.asarray(y, int)
    ok, ok0 = np.asarray(cand) == y, np.asarray(base) == y
    d = np.array([ok[i].mean() - ok0[i].mean() for i in block_boot(blocks, n_boot)])
    fixed, broken = int((ok & ~ok0).sum()), int((~ok & ok0).sum())
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    p = binomtest(fixed, fixed + broken, 0.5).pvalue if fixed + broken else 1.0
    gain = float(ok.mean() - ok0.mean())
    return {"difference": gain, "95% CI": f"{lo:+.3f} to {hi:+.3f}", "ci_low": float(lo), "ci_high": float(hi),
            "roads fixed": fixed, "roads broken": broken, "McNemar p": float(p),
            "beats": bool(gain > 0 and lo > 0 and p < 0.05),
            "verdict": ("beats" if gain > 0 and lo > 0 and p < 0.05 else
                        "worse" if gain < 0 and hi < 0 and p < 0.05 else "no detectable difference")}


def f1_of(y, called, w=None):
    y, called = np.asarray(y, int), np.asarray(called, bool)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    tp, fp, fn = w[(y == 1) & called].sum(), w[(y == 0) & called].sum(), w[(y == 1) & ~called].sum()
    return float(2 * tp / (2 * tp + fp + fn)) if tp else 0.0


def block_counts(blocks, n_boot, seed=SEED):
    """The same block resamples as block_boot (same generator, same draws), as (n_boot, n_blocks) counts of each block
    (np.unique order), plus each row's block index. For statistics that are sums over rows (cell F1)."""
    ub, inv = np.unique(np.asarray(blocks), return_inverse=True)
    rng = np.random.default_rng(seed)
    counts = np.stack([np.bincount(rng.integers(0, len(ub), len(ub)), minlength=len(ub)) for _ in range(n_boot)])
    return counts.astype(float), inv


def f1_boot(y, called, w, counts, inv):
    """Resampled F1 from per-block weighted TP / FP / FN sums."""
    y, called = np.asarray(y, int), np.asarray(called, bool)
    nb = counts.shape[1]
    tp = np.bincount(inv, weights=w * ((y == 1) & called), minlength=nb)
    fp = np.bincount(inv, weights=w * ((y == 0) & called), minlength=nb)
    fn = np.bincount(inv, weights=w * ((y == 1) & ~called), minlength=nb)
    TP, FP, FN = counts @ tp, counts @ fp, counts @ fn
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(TP > 0, 2 * TP / (2 * TP + FP + FN), 0.0)


def cell_report(y, calls, blocks, base_name, w=None, n_boot=2000):
    """Cells: {name: called} on the same cells. Precision, recall, F1 (weighted if w), each F1 with a 95% interval and
    each F1 minus base_name's with a 95% interval, all from resampling whole blocks (2,000, seed 662). No McNemar on
    cells (cells within a block are not independent), as the plan says."""
    y = np.asarray(y, int)
    w = np.ones(len(y)) if w is None else np.asarray(w, float)
    counts, inv = block_counts(blocks, n_boot)
    f1b = {n: f1_boot(y, c, w, counts, inv) for n, c in calls.items()}
    rows = []
    for n, c in calls.items():
        c = np.asarray(c, bool)
        tp, fp, fn = w[(y == 1) & c].sum(), w[(y == 0) & c].sum(), w[(y == 1) & ~c].sum()
        d = f1b[n] - f1b[base_name]
        f1, f1_0 = f1_of(y, c, w), f1_of(y, calls[base_name], w)
        lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
        rows.append({"arm": n, "TP": float(tp), "FN": float(fn), "FP": float(fp),
                     "precision": float(tp / (tp + fp)) if tp + fp else float("nan"),
                     "recall": float(tp / (tp + fn)) if tp + fn else float("nan"), "F1": f1,
                     "F1 95% CI": f"{np.percentile(f1b[n], 2.5):.3f}-{np.percentile(f1b[n], 97.5):.3f}",
                     f"F1 vs {base_name}": f1 - f1_0, "95% CI of the difference": f"{lo:+.3f} to {hi:+.3f}",
                     "diff_low": float(lo), "diff_high": float(hi),
                     "verdict": ("beats" if f1 > f1_0 and lo > 0 else "worse" if f1 < f1_0 and hi < 0 else
                                 "no detectable difference") if n != base_name else "-"})
    return pd.DataFrame(rows)


def tidy(df):
    return json.loads(df.to_json(orient="records", double_precision=4))


class Log:
    def __init__(self):
        self.t0 = time.time()

    def __call__(self, *a):
        print(f"[{time.strftime('%H:%M:%S')} {time.time() - self.t0:7.0f} s]", *a, flush=True)


def free_gb(path=Path.home()):
    import shutil
    return shutil.disk_usage(path).free / 1e9
