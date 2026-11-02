"""Method bench 2 (outputs/preregistration_method_bench_2.md): paths, guards, the machine-limit wait and shared helpers.

Bench 1's folder (../method_bench) is imported read-only for its statistics (mb_common), its C0-with-hooks
(c_common.darkref_variant) and its after-date features (after_features.after_rows). Nothing there is edited.
Development data only; production.json is read-only (sha256 checked by the runner).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"                       # machine limit: at most 2 threads (forced, not setdefault)
os.environ.setdefault("MPLBACKEND", "Agg")
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
MB1 = PILOT / "method_bench"                  # bench 1, read-only
for _p in (str(MB1),):
    if _p not in sys.path:
        sys.path.append(_p)
import mb_common as M1                       # noqa: E402  (adds the library and spatial_cv to sys.path)

CR = PILOT.parents[1]
FIG = CR / "figures" / "method_bench_2"
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_2_cache")
IDA_BIG = M1.IDA_BIG                          # read-only
SMOKE_TILES = ("2_23_44", "2_15_45", "2_19_55")
LAMBDA = {"blue": 0.48, "green": 0.545, "red": 0.66}   # WorldView-class band centres (um), as bench 1 C5b
W601 = (0.299, 0.587, 0.114)                  # R, G, B
MIN_PIF = 1000                                # bench 1's minimum invariant count (C2)
SAT_DN = 250                                  # saturated: excluded from every fit

log, write_json, registry_hash, dev_guard_tiles = M1.log, M1.write_json, M1.registry_hash, M1.dev_guard_tiles


# ------------------------------------------------------------------ machine limits
def memory_ok(min_free=30, max_swap_gb=4.0):
    """(ok, free %, swap GB) from memory_pressure and vm.swapusage."""
    try:
        mp = subprocess.run(["memory_pressure"], capture_output=True, text=True, timeout=60).stdout
        free = float(re.search(r"free percentage:\s*(\d+)", mp).group(1))
        sw = subprocess.run(["sysctl", "vm.swapusage"], capture_output=True, text=True).stdout
        used = re.search(r"used = ([\d.]+)([MG])", sw)
        swap = float(used.group(1)) / (1024 if used.group(2) == "M" else 1)
    except Exception:                          # if the probes fail, be conservative: wait
        return False, float("nan"), float("nan")
    return (free >= min_free and swap <= max_swap_gb), free, swap


def wait_for_memory(t0=None, poll_s=60):
    while True:
        ok, free, swap = memory_ok()
        if ok:
            return free, swap
        if t0 is not None:
            log(t0, f"waiting: free {free}% swap {swap:.2f} GB")
        time.sleep(poll_s)


# ------------------------------------------------------------------ small shared pieces
def grey601(rgb):
    x = rgb.astype(np.float32)
    return W601[0] * x[..., 0] + W601[1] * x[..., 1] + W601[2] * x[..., 2]


def pca_axis(x, y, w=None):
    """Major axis of the 2-D points (x, y) (optionally weighted): (mean_x, mean_y, unit major vector, unit minor vector,
    eigenvalues descending)."""
    w = np.ones(len(x)) if w is None else np.asarray(w, float)
    sw = w.sum()
    mx, my = (w * x).sum() / sw, (w * y).sum() / sw
    dx, dy = x - mx, y - my
    cov = np.array([[(w * dx * dx).sum(), (w * dx * dy).sum()], [(w * dx * dy).sum(), (w * dy * dy).sum()]]) / sw
    vals, vecs = np.linalg.eigh(cov)
    major, minor = vecs[:, 1], vecs[:, 0]
    if major[0] < 0:
        major = -major
    return mx, my, major, minor, vals[::-1]


def minor_coord(x, y, mx, my, minor):
    return (x - mx) * minor[0] + (y - my) * minor[1]


def meansd_map(xb, ya):
    """Du 2002 eq. 17 / Schott 1988 eq. 8 / Lin 2015 eqs. 1-3, before -> after scale: gain = sd_a / sd_b,
    offset = mean_a - gain * mean_b."""
    gain = float(np.std(ya) / max(np.std(xb), 1e-9))
    off = float(np.mean(ya) - gain * np.mean(xb))
    return gain, off


GAIN_BOUND = (0.1, 10.0)       # amendment 2026-10-30 (DEVIATION): "-bounded" variants of N3 and N4 abstain outside


def out_of_bound(gain):
    return not (GAIN_BOUND[0] <= gain <= GAIN_BOUND[1])


def linear_tone(gain, off):
    return lambda v: gain * np.asarray(v, np.float64) + off
