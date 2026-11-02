"""Arm G2: Lin et al. (2015) cloud test, a blue rise against a normalised clear reference (eq. 15, p. 112: Hagolle 2010's
test with the reference composed for the same date, so the time term drops); handoff
literature_fulltext/lin2015_radiometric_normalization_cloud_detection_invariant_pixels_ISPRS.md section 1 step 8, section 5.

Blue band: N3's selector (weighted-PCA invariant pixels over all valid pixels, S from RGB) on blue before vs blue
after; Du mean/SD map of the before blue onto the after scale; cloud = after_blue - map(before_blue) > T_blue per pixel.
No dilation, erosion or hole filling (p. 112).
Deviations: the reference is the before image (two dates; the paper composes it from 6-24 dates); the paper's 0.03 ToA
reflectance has no 8-bit display-DN equivalent, so T_blue = Otsu on the pooled training-tile blue rise (every 16th valid
pixel), production's own rule for the dark-rise cut (computed once by run_bench2.py stage 'thresholds' and cached);
Hagolle's snow test needs SWIR (dropped); the red/blue veto is bench 1's D3i (not repeated). If the selector abstains on
a tile, the tile's blue map falls back to mean/SD matching over all valid pixels (recorded) so the test still runs.
"""
import json

import numpy as np

import b2_common as B
import n3_lin

OTSU_STEP = 16
T_FILE = B.BIG / "g2_threshold.json"


def blue_rise(before_rgb, after_rgb, valid, S=None):
    S = n3_lin.similarity(before_rgb, after_rgb, valid) if S is None else S
    xb = before_rgb[..., 2][valid].astype(np.float64)
    xa = after_rgb[..., 2][valid].astype(np.float64)
    tone, info = n3_lin.fit(xb, xa, S)
    if tone is None:
        g, o = B.meansd_map(xb, xa)
        tone, info["fallback"] = B.linear_tone(g, o), "mean/SD over all valid pixels"
        info.update(gain=g, offset=o)
    rise = np.where(valid, after_rgb[..., 2].astype(np.float64) - tone(before_rgb[..., 2]), 0.0)
    return rise.astype(np.float32), info


def threshold(t0=None):
    """Otsu on the pooled training-tile blue rise (cached)."""
    if T_FILE.exists():
        return json.loads(T_FILE.read_text())["T_blue"]
    import pandas as pd
    from skimage.filters import threshold_otsu
    from sn8_clouds import _tile
    idx = pd.read_csv("/Users/jusrogers/Masters/GGS662/ProjectBranch/Images/SN8_Louisiana-East_Ida2021_greyscale/tiles.csv")
    train = list(idx.tile_id[idx.split == "train"])
    B.dev_guard_tiles(train)
    vals = []
    for i, tid in enumerate(train):
        B.wait_for_memory(t0)
        p, _, _, valid = _tile(tid)
        r, _ = blue_rise(p["before_rgb"], p["after_rgb"], valid)
        vals.append(r[valid][::OTSU_STEP])
        if t0 is not None and (i + 1) % 20 == 0:
            B.log(t0, f"G2 threshold: {i + 1}/{len(train)} training tiles")
    T = float(threshold_otsu(np.concatenate(vals)))
    B.BIG.mkdir(parents=True, exist_ok=True)
    T_FILE.write_text(json.dumps({"T_blue": T, "tiles": len(train), "step": OTSU_STEP,
                                  "rule": "Otsu on pooled training-tile blue rise (production's dark-rise rule)"}))
    return T


def gate(before_rgb, after_rgb, valid, T_blue):
    rise, info = blue_rise(before_rgb, after_rgb, valid)
    m = valid & (rise > T_blue)
    info.update(T_blue=T_blue, gate_px=int(m.sum()), gate_share=float(m[valid].mean()))
    return m, rise, info
