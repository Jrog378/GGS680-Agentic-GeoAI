"""Arm T1: multiresolution rotation-invariant uniform LBP (riu2) with the separate contrast measure VAR (Ojala,
Pietikainen & Maenpaa 2002, TPAMI 24:971; handoff literature_fulltext/ojala2002_lbp_rotation_invariant_TPAMI.md:
Eqs. 6-11, defaults (P, R) = (8, 1), (16, 2), (24, 3) p. 982; claim_checks_C Ojala #4-5).

Per road strip and scale, on the grey as sn8_texture reads it (after histogram-matched to before, 8-bit for the codes):
  lbpP_R_entropy_{before,after,change}   entropy of the P+2 riu2 code histogram
  lbpP_R_flat_{before,after,change}      share of code P (all neighbours >= centre: flat area or dark spot)
  lbpP_R_g                               two-sample G statistic between the before and after code histograms
                                         (log-likelihood ratio, as Ojala's G-statistic family, Eqs. 12-13)
  lbpP_R_var_{before,after,change}       mean VAR_{P,R} (Eq. 11): local contrast, kept separate so haze shows here
30 columns; replaces the 9 lbp_* columns of sn8_texture (LBP 8 neighbours at 2 px only).
"""
import numpy as np
from skimage.feature import local_binary_pattern

SCALES = ((8, 1), (16, 2), (24, 3))
COLUMNS = ([f"lbp{P}_{R}_{m}_{d}" for P, R in SCALES for m in ("entropy", "flat", "var") for d in ("before", "after", "change")]
           + [f"lbp{P}_{R}_g" for P, R in SCALES])


def _g_stat(a, b):
    """Two-sample G statistic of two histograms given as probabilities (n_regions, bins), each row summing to 1."""
    def xlogx(x):
        return np.where(x > 0, x * np.log(np.where(x > 0, x, 1)), 0.0)
    s = a + b
    return 2 * (xlogx(a).sum(1) + xlogx(b).sum(1) - xlogx(s).sum(1) + 2 * np.log(2))


def region_lbp(g8, valid, region, n):
    """{(P, R): (hist (n, P+2), var mean (n,))} for regions 1..n."""
    out = {}
    mask = region > 0
    cnt = np.maximum(np.bincount(region[mask], minlength=n + 1)[1:], 1)
    for P, R in SCALES:
        codes = local_binary_pattern(g8, P, R, method="uniform").astype(np.int64)
        var = local_binary_pattern(g8.astype(np.float64), P, R, method="var")
        var = np.nan_to_num(var, nan=0.0)
        k = P + 2
        ok = mask & valid
        h = np.bincount((region[ok] - 1) * k + codes[ok], minlength=n * k).reshape(n, k).astype(float)
        with np.errstate(invalid="ignore", divide="ignore"):
            h = h / h.sum(1, keepdims=True)
        v = np.bincount(region[ok] - 1, weights=var[ok], minlength=n) / np.maximum(np.bincount(region[ok] - 1, minlength=n), 1)
        out[P, R] = (h, v)
    return out


def lbp_features(g_before, g_after, valid, region, n):
    """g_*: float grey on [0, 1] (no-data filled). Returns {column: (n,)}."""
    res = {}
    per = {}
    for date, g in (("before", g_before), ("after", g_after)):
        g8 = np.round(np.clip(g, 0, 1) * 255).astype(np.uint8)
        per[date] = region_lbp(g8, valid, region, n)
    for P, R in SCALES:
        for date in ("before", "after"):
            h, v = per[date][P, R]
            with np.errstate(invalid="ignore", divide="ignore"):
                res[f"lbp{P}_{R}_entropy_{date}"] = -(h * np.log(np.where(h > 0, h, 1))).sum(1)
            res[f"lbp{P}_{R}_flat_{date}"] = h[:, P]
            res[f"lbp{P}_{R}_var_{date}"] = v
        for m in ("entropy", "flat", "var"):
            res[f"lbp{P}_{R}_{m}_change"] = res[f"lbp{P}_{R}_{m}_after"] - res[f"lbp{P}_{R}_{m}_before"]
        res[f"lbp{P}_{R}_g"] = _g_stat(per["before"][P, R][0], per["after"][P, R][0])
    return res
