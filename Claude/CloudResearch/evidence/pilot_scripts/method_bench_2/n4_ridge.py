"""Arms N4 / N4b: the Ridge Method as used by Song, Woodcock, Seto, Lenney & Macomber (2001, RSE 75:230) (handoff
literature_fulltext/song2001_classification_change_detection_landsat_atmospheric_correction_RSE.md sections 1 and 5;
claim_checks_D1 Song #3).

"DN values of all stable features form a 'ridge' with the straight line that passes along the ridge defining the
relationship between dates" (p. 235): a density plot of date-1 vs date-2 DN for all pixels, per band; the ridge line is
the map. The authors excluded "the area of substantial land-use change" when making the plots (p. 235).
Ours (the paper gives no fitting details): 256 x 256 density of before grey vs after grey, Gaussian-smoothed (sigma 1
bin); for each before column with >= 50 pixels, the after value of maximum density; a straight line through these
ridge points by least squares weighted by the column counts. N4 = all valid pixels; N4b = C0's clear pixels (the cloud
excluded as the paper excluded changed area). The flood cannot be excluded without labels. Abstain if slope <= 0.
N4-bounded (amendment 2026-10-30, DEVIATION): N4 (all pixels) that also abstains if the slope is outside 0.1-10.
"""
import numpy as np
from scipy import ndimage as ndi

import b2_common as B

SIGMA = 1.0
MIN_COL = 50


def ridge(xb, ya):
    bi, ai = np.clip(np.rint(xb), 0, 255).astype(int), np.clip(np.rint(ya), 0, 255).astype(int)
    H = np.zeros((256, 256))
    np.add.at(H, (bi, ai), 1)
    Hs = ndi.gaussian_filter(H, SIGMA)
    col = H.sum(1)
    cols = np.flatnonzero(col >= MIN_COL)
    modes = Hs[cols].argmax(1).astype(float)
    return cols.astype(float), modes, col[cols]


def fit(xb, ya, bound=False):
    x, y, w = ridge(xb, ya)
    info = {"ridge_points": int(len(x))}
    if len(x) < 3:
        info["abstain"] = "< 3 ridge points"
        return None, info
    W = np.sqrt(w)
    A = np.stack([x, np.ones_like(x)], 1) * W[:, None]
    slope, icpt = np.linalg.lstsq(A, y * W, rcond=None)[0]
    info.update(slope=float(slope), intercept=float(icpt))
    if not slope > 0:
        info["abstain"] = f"slope {slope}"
        return None, info
    if bound and B.out_of_bound(slope):
        info["abstain"] = f"slope {slope} outside {B.GAIN_BOUND}"
        return None, info
    return B.linear_tone(float(slope), float(icpt)), info


def make_tone_fn(clear_only, bound=False):
    def tone_fn(before, after, clear, valid, b, a):
        m = clear if clear_only else valid
        return fit(b[m].astype(np.float64), a[m].astype(np.float64), bound)
    return tone_fn


def correct(before, after, valid, clear_only=False, gate=None, bound=False):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, tone_fn=make_tone_fn(clear_only, bound), gate=gate)
