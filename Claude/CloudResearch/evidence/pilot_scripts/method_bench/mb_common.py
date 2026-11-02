"""Method bench (outputs/preregistration_method_bench.md): shared paths, guards and statistics.

Development data only. The library (ProjectBranch/ClaudeFunctions), the fold module, the spatial-CV scripts and the Ida
test's files are imported or read, never edited. production.json is read-only (sha256 checked by every runner).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("MPLBACKEND", "Agg")
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
CR = PILOT.parents[1]                                   # CloudResearch/
SCV = PILOT / "spatial_cv"
IDA = PILOT / "ida_clear_view"
FIG = CR / "figures" / "method_bench"
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_cache")
IDA_BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/ida/ida_clear_view_cache")   # read-only
for _p in (LIB, str(HERE), str(SCV)):
    if _p not in sys.path:
        sys.path.append(_p)

SEED = 662
SEEDS = [662] + list(range(1, 21))
REGISTRY = Path("/Users/jusrogers/Masters/GGS662/ProjectBranch/Code/results/production.json")


def registry_hash():
    return hashlib.sha256(REGISTRY.read_bytes()).hexdigest()


def log(t0, *msg):
    print(f"[{time.strftime('%H:%M:%S')} {time.time() - t0:7.0f} s]", *msg, flush=True)


def plain(v):
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else float(f"{float(v):.6g}")
    if isinstance(v, np.ndarray):
        return plain(v.tolist())
    return v


def write_json(path, obj):
    tmp = Path(str(path) + ".writing")
    tmp.write_text(json.dumps(plain(obj), indent=1))
    tmp.replace(path)


def dev_guard_tiles(tile_ids):
    """Every tile must be a Louisiana-East train or val tile."""
    import pandas as pd
    idx = pd.read_csv("/Users/jusrogers/Masters/GGS662/ProjectBranch/Images/SN8_Louisiana-East_Ida2021_greyscale/tiles.csv")
    dev = set(idx.tile_id[idx.split.isin(["train", "val"])])
    assert len(dev) == 226
    bad = set(tile_ids) - dev
    assert not bad, f"non-development tiles requested: {sorted(bad)[:5]}"


# ---------------------------------------------------------------- block bootstrap (as spatial_cv_score.Boot)
class Boot:
    """Resamples of groups (3 x 3 blocks) of the units in msk: default_rng(662), one rng.integers(0, G, G) per
    resample, kept as a multiplicity matrix (spatial_cv_score.Boot, copied)."""

    def __init__(self, groups, msk, n=2000, seed=SEED):
        g = np.asarray(groups)[msk]
        uniq, self.gidx = np.unique(g, return_inverse=True)
        self.G = len(uniq)
        rng = np.random.default_rng(seed)
        self.M = np.zeros((n, self.G), np.int32)
        for b in range(n):
            self.M[b] = np.bincount(rng.integers(0, self.G, self.G), minlength=self.G)
        self.n_g = np.bincount(self.gidx, minlength=self.G)
        self.msk = msk

    def sums(self, v):
        return self.M @ np.bincount(self.gidx, weights=np.asarray(v, float), minlength=self.G)

    def mean(self, v):
        return self.sums(v) / (self.M @ self.n_g)


def mcnemar(ok_a, ok_b):
    from scipy.stats import binomtest
    fixed, broken = int((ok_a & ~ok_b).sum()), int((~ok_a & ok_b).sum())
    p = binomtest(fixed, fixed + broken, 0.5).pvalue if fixed + broken else 1.0
    return fixed, broken, float(p)


def paired_flood(call, base, y, msk, groups, n=2000):
    """Accuracy of call minus base on msk: gain, block-bootstrap 95% interval, fixed/broken, exact McNemar."""
    bt = Boot(groups, msk, n)
    ok, bk = call[msk] == y[msk], base[msk] == y[msk]
    d = bt.mean(ok) - bt.mean(bk)
    fixed, broken, p = mcnemar(ok, bk)
    return {"roads": int(msk.sum()), "acc": float(ok.mean()), "acc_base": float(bk.mean()),
            "gain": float(ok.mean() - bk.mean()), "ci": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "fixed": fixed, "broken": broken, "mcnemar_p": p}


def seed_avg(calls, bases, y, msk, groups, n=2000):
    """Seed-averaged accuracy gain (calls, bases: (n_seeds, n_roads)) with a block-bootstrap interval (the same
    resamples for every seed), plus seeds above / below."""
    bt = Boot(groups, msk, n)
    ok = (calls[:, msk] == y[msk]).astype(float)
    bk = (bases[:, msk] == y[msk]).astype(float)
    d = ok.mean(0) - bk.mean(0)
    dist = bt.mean(d)
    per_seed = ok.mean(1) - bk.mean(1)
    return {"roads": int(msk.sum()), "mean_gain": float(d.mean()),
            "ci": [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))],
            "acc_mean": float(ok.mean()), "acc_base_mean": float(bk.mean()),
            "seeds_better": int((per_seed > 1e-12).sum()), "seeds_worse": int((per_seed < -1e-12).sum()),
            "per_seed_gain": per_seed.tolist()}
