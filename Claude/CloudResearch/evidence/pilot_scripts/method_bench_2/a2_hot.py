"""Arm A2: Zhang, Guindon & Cihlar (2002, RSE 82:173) HOT-level haze removal (handoff
literature_fulltext/zhang2002_haze_optimized_transformation_thin_cloud_landsat_RSE.md sections 1 and 5;
claim_checks_D1 Zhang #2, #5, #10).

NOT RUNNABLE ON SN8 YET: the paper's water mask is a near-IR threshold (TM4) and the project has no water mask; turbid
floodwater raises HOT (p. 179), so without one the arm would "dehaze" the flood. remove_haze() therefore REQUIRES a
water mask argument and raises if it is None. It is unit-tested on synthetic haze only (smoke_test.py).

1. Clear line (CL): red regressed on blue (least squares) over clear, non-water pixels (the paper: one visually chosen
   clear region per scene; ours: the after date's clear pixels, automatic). theta = atan(slope).
2. HOT = B sin(theta) - R cos(theta) (eq. 1), rounded to integer levels (the paper's increments of 1).
3. Per level h and band, lower bound = 1st percentile of the non-water pixels at that level (levels with < 100 pixels
   are interpolated from their neighbours); clear level h_c = the median HOT of the clear pixels.
4. Delta_b(h) = lowerbound_b(h) - lowerbound_b(h_c), forced monotone non-decreasing and >= 0 for h > h_c, 0 for
   h <= h_c (Fig. 9 is monotonic); subtract Delta_b(HOT(pixel)) from every pixel (sec. 5.4, p. 182).
"""
import numpy as np

import b2_common as B

LOW_PCT = 1.0
MIN_LEVEL_PX = 100


def clear_line(rgb, m):
    b, r = rgb[..., 2][m].astype(np.float64), rgb[..., 0][m].astype(np.float64)
    slope, icpt = np.polyfit(b, r, 1)
    return float(slope), float(icpt)


def hot(rgb, theta):
    return rgb[..., 2].astype(np.float64) * np.sin(theta) - rgb[..., 0].astype(np.float64) * np.cos(theta)


def remove_haze(rgb, valid, clear, water):
    """rgb (H, W, 3) 0-255; clear: pixels for the clear line and the clear level; water: REQUIRED boolean mask."""
    if water is None:
        raise ValueError("A2 needs a water mask (the paper uses a near-IR threshold); none exists in the project")
    use = valid & ~water
    cl = clear & use
    slope, icpt = clear_line(rgb, cl)
    theta = float(np.arctan(slope))
    H = hot(rgb, theta)
    Hi = np.rint(H).astype(int)
    h_c = int(np.rint(np.median(H[cl])))
    levels = np.arange(Hi[use].min(), Hi[use].max() + 1)
    out = rgb.astype(np.float64).copy()
    deltas = {}
    for band in range(3):
        x = rgb[..., band].astype(np.float64)
        lb = np.full(len(levels), np.nan)
        hv, xv = Hi[use], x[use]
        order = np.argsort(hv, kind="stable")
        hv, xv = hv[order], xv[order]
        starts = np.searchsorted(hv, levels, "left")
        ends = np.searchsorted(hv, levels, "right")
        for j, (s, e) in enumerate(zip(starts, ends)):
            if e - s >= MIN_LEVEL_PX:
                lb[j] = np.percentile(xv[s:e], LOW_PCT)
        ok = np.isfinite(lb)
        if ok.sum() < 2:
            deltas[band] = None
            continue
        lb = np.interp(levels, levels[ok], lb[ok])
        lb_c = float(np.interp(h_c, levels, lb))
        d = lb - lb_c
        above = levels > h_c
        d = np.where(above, np.maximum.accumulate(np.where(above, np.maximum(d, 0), 0)), 0.0)
        deltas[band] = d
        sub = np.interp(Hi, levels, d, left=0.0, right=float(d[-1]))
        out[..., band] = np.where(valid, x - sub, x)
    out = np.clip(out, 0, 255)
    return {"rgb": out, "hot": H, "theta": theta, "slope": slope, "intercept": icpt, "h_clear": h_c,
            "levels": levels, "deltas": deltas}
