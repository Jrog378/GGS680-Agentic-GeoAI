"""Arm N1: Du, Teillet & Cihlar (2002, RSE 82:123) PCA-selected pseudo-invariant features, mean/SD matching
(handoff literature_fulltext/du2002_radiometric_normalization_multitemporal_quality_control_RSE.md sections 1 and 5;
claim_checks_D1 Du #1, #4-6: PCA SELECTS the PIFs and checks quality; the map is mean/SD matching, eq. 17; global).

Candidates: C0's clear pixels (cloud removed by the gate), not saturated on either date, WATER REMOVED FIRST (grey >=
WATER_DN on both dates; Du removes water by lower thresholds "because they can change quickly and independently",
p. 126), and |d - median(d)| < D, d = after - before (the difference limit; value not given in the paper, ours:
D0 = 2 MAD(d)). PCA of [before, after] -> major axis; keep |minor| < l; PCA again -> improved axis; PIFs = candidates
within l of the improved axis. Accept when r(PIFs) >= 0.9 (p. 127); else tighten D and l by 0.75 per pass, 5 passes at
most. l0 = 2.0 DN (Table 1d, bands 4-5). Map: gain = sd_after / sd_before, offset = mean_after - gain mean_before on the
PIFs. QC reported: r and |1 - SL|, SL = the major-axis slope of the normalised PIFs (pp. 127-128).
Deviations: per tile; reference = after date; WATER_DN = 40 is ours; 5-pass schedule replaces the analyst loop;
abstain (gate opaque) on failure or < 1,000 PIFs.
N1b (amendment 2026-10-30, DEVIATION): no water removal (water=False).
"""
import numpy as np

import b2_common as B

WATER_DN = 40.0
L0 = 2.0
R_MIN = 0.9
PASSES = 5
SHRINK = 0.75


def _pifs(x, y, l):
    mx, my, major, minor, _ = B.pca_axis(x, y)
    keep = np.abs(B.minor_coord(x, y, mx, my, minor)) < l
    if keep.sum() < 3:
        return keep
    mx, my, major, minor, _ = B.pca_axis(x[keep], y[keep])            # the improved axis
    return np.abs(B.minor_coord(x, y, mx, my, minor)) < l


def fit(xb, xa):
    """xb, xa: before/after values of the candidate pixels (water/saturation already removed). (tone or None, info)."""
    d = xa - xb
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med)))
    D0 = 2 * mad
    info = {"candidates": int(len(xb)), "D0": D0, "passes": []}
    for k in range(PASSES):
        D, l = D0 * SHRINK ** k, L0 * SHRINK ** k
        c = np.abs(d - med) < D
        x, y = xb[c], xa[c]
        if len(x) < 3:
            info["passes"].append({"D": D, "l": l, "cand": int(len(x))})
            continue
        p = _pifs(x, y, l)
        n = int(p.sum())
        r = float(np.corrcoef(x[p], y[p])[0, 1]) if n >= 3 else float("nan")
        info["passes"].append({"D": D, "l": l, "cand": int(len(x)), "pif": n, "r": r})
        if n >= 3 and r >= R_MIN:
            info.update(pass_ok=k, pif_px=n, r=r)
            if n < B.MIN_PIF:
                info["abstain"] = "PIF < 1000"
                return None, info
            gain, off = B.meansd_map(x[p], y[p])
            # QC (pp. 127-128). With two dates and the PIFs' own mean/SD, the major axis of the SAME normalised PIFs
            # has slope exactly 1 by construction (equal variances), so that SL is uninformative here (Du had three
            # images, each pair normalised to a shared reference). Reported instead: SL of the PIFs RE-SELECTED from
            # the normalised candidates (Du's re-run of the selection on normalised data), and SL over all candidates.
            xn = gain * x + off
            p2 = _pifs(xn, y, l)
            _, _, maj2, _, _ = B.pca_axis(xn[p2], y[p2]) if p2.sum() >= 3 else (0, 0, np.array([1.0, np.nan]), 0, 0)
            _, _, maj3, _, _ = B.pca_axis(xn, y)
            sl = float(maj2[1] / maj2[0])
            sl_all = float(maj3[1] / maj3[0])
            info.update(gain=gain, offset=off, SL_reselected=sl, abs_1_minus_SL=abs(1 - sl), SL_all_candidates=sl_all)
            if not gain > 0:
                info["abstain"] = f"gain {gain}"
                return None, info
            return B.linear_tone(gain, off), info
    info["abstain"] = "r < 0.9 after 5 passes"
    return None, info


def make_tone_fn(water=True):
    def tone_fn(before, after, clear, valid, b, a):
        m = clear & (b <= B.SAT_DN) & (a <= B.SAT_DN)
        if water:
            m &= (b >= WATER_DN) & (a >= WATER_DN)
        tone, info = fit(b[m].astype(np.float64), a[m].astype(np.float64))
        info["water_removed_share_of_clear"] = float(((b < WATER_DN) | (a < WATER_DN))[clear].mean())
        return tone, info
    return tone_fn


def correct(before, after, valid, gate=None, water=True):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, tone_fn=make_tone_fn(water), gate=gate)
