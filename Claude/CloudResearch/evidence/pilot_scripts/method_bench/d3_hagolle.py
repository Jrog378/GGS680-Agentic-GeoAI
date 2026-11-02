"""Arm D3: Hagolle et al. (2010, RSE 114:1747) multi-temporal vetoes applied to the production gate's dark-rise mask
(handoff literature_fulltext/hagolle2010_multitemporal_cloud_detection_RSE.md section 1 steps 6-7; claim_checks_A g2
#2, #6: the correlation test is a VETO, and a second veto, red rise > 1.5 x blue rise, means surface change).

  veto (i)   Delta_red > 1.5 Delta_blue (Eq. 2, l. 173-178), Delta_band = after - tone_band(before), the tone curve per
             band by quantile matching (sn8_refhaze.tone_curve) on clear pixels (valid, outside every production cloud
             mask + 10 m), both box-smoothed over 41 px (the dark channel's 20 m scale; Hagolle works at 100-240 m).
             The 1.5 is reflectance-based; used as published (no cloud labels on SN8 to learn it from).
  veto (ii)  local Pearson r of before vs after grey in 41 px windows >= r_clear, the tile's median local r on its clear
             pixels (the paper gives no window or threshold, l. 179-195; label-free and scene-adaptive here, our rule).
A vetoed dark-rise pixel is not cloud; the road rule (share of strip under the mask >= 0.2) is then applied as usual.
"""
import cv2
import numpy as np
from scipy import ndimage as ndi

WIN = 41
FACTOR = 1.5
CLEAR_MARGIN_PX = 20


def local_r(x, y, valid, win=WIN):
    w = valid.astype(np.float32)
    k = (win, win)
    sw = np.maximum(cv2.blur(w, k), 1e-6)
    mx, my = cv2.blur(w * x, k) / sw, cv2.blur(w * y, k) / sw
    vx = cv2.blur(w * x * x, k) / sw - mx * mx
    vy = cv2.blur(w * y * y, k) / sw - my * my
    cxy = cv2.blur(w * x * y, k) / sw - mx * my
    return cxy / np.sqrt(np.maximum(vx, 1e-6) * np.maximum(vy, 1e-6))


def vetoes(p, before, after, valid, masks):
    """(veto_i, veto_ii, info) on one tile; masks = sn8_clouds._maps(...)["masks"]."""
    from sn8_refhaze import tone_curve
    anym = masks["bright"] | masks["dark"] | masks["dark rise"]
    clear = valid & ~ndi.binary_dilation(anym, iterations=CLEAR_MARGIN_PX) if anym.any() else valid.copy()
    if clear.sum() < 1000:
        clear = valid & ~anym if (valid & ~anym).sum() >= 1000 else valid
    d = {}
    for i, band in ((0, "red"), (2, "blue")):
        b = p["before_rgb"][..., i].astype(np.float32)
        a = p["after_rgb"][..., i].astype(np.float32)
        tone, _, _ = tone_curve(b, a, clear)
        d[band] = cv2.blur(np.where(valid, a - tone(b), 0).astype(np.float32), (WIN, WIN))
    veto_i = valid & (d["red"] > FACTOR * d["blue"])
    r = local_r(before.astype(np.float32), after.astype(np.float32), valid)
    r_clear = float(np.median(r[clear]))
    veto_ii = valid & (r >= r_clear)
    return veto_i, veto_ii, {"r_clear": r_clear, "clear_px": int(clear.sum())}
