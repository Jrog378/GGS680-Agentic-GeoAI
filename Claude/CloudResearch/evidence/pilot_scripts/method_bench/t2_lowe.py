"""Arm T2: Lowe's (2004, IJCV 60:91) SIFT descriptor computed densely, without keypoints (handoff
literature_fulltext/lowe2004_sift_scale_invariant_keypoints_IJCV.md, section 6.1 p. 16; claim_checks_C Lowe #5: the
keypoint detector's absolute 0.03 contrast threshold drops hazy regions, so the descriptor is used on a grid).

Grey smoothed (Gaussian sigma 1 px), pixel-difference gradients, 8 signed orientation bins with linear interpolation
between bins, 4 x 4 px cells, a 16 x 16 px block of 4 x 4 cells at every cell (4 px stride), each cell weighted by a
Gaussian of sigma 8 px (half the block) at its centre's distance from the block centre (a cell-level approximation of
Lowe's per-sample weight; no trilinear spatial interpolation), 128-d, L2-Hys: unit length, clip at 0.2, renormalise.
North-up frame (no rotation to a dominant orientation; our choice for roads, as the handoff suggests).
Per road strip (blocks whose centre pixel lies in the strip):
  lowe_cos_pooled     1 - cosine of the before and after mean descriptors
  lowe_cos_mean       mean over the road's blocks of 1 - cosine of the before and after descriptors at the same place
  lowe_entropy_{before,after,change}   entropy of the 8 orientation bins summed over the road's normalised descriptors
  lowe_mag_{before,after,change}       mean gradient magnitude in the strip: the separate contrast channel
8 columns, added to production.
"""
import numpy as np
from scipy import ndimage as ndi

CELL, NCELL, BINS = 4, 4, 8
COLUMNS = (["lowe_cos_pooled", "lowe_cos_mean"] + [f"lowe_entropy_{d}" for d in ("before", "after", "change")]
           + [f"lowe_mag_{d}" for d in ("before", "after", "change")])


def gradients(g):
    L = ndi.gaussian_filter(g.astype(np.float32), 1.0)
    dx = np.zeros_like(L); dy = np.zeros_like(L)
    dx[:, 1:-1] = L[:, 2:] - L[:, :-2]
    dy[1:-1, :] = L[2:, :] - L[:-2, :]
    return np.hypot(dx, dy), np.mod(np.arctan2(dy, dx), 2 * np.pi)


def block_descriptors(g):
    """(descriptors (Hb, Wb, 128) L2-Hys, magnitude map); block (i, j) is centred at pixel (4 i + 8, 4 j + 8)."""
    m, th = gradients(g)
    H, W = (g.shape[0] // CELL) * CELL, (g.shape[1] // CELL) * CELL
    m, th = m[:H, :W], th[:H, :W]
    pos = th / (2 * np.pi / BINS)
    lo = np.floor(pos).astype(int) % BINS
    w_hi = (pos - np.floor(pos)).astype(np.float32)
    hi = (lo + 1) % BINS
    cells = np.zeros((H // CELL, W // CELL, BINS), np.float32)
    for b in range(BINS):
        v = m * ((lo == b) * (1 - w_hi) + (hi == b) * w_hi)
        cells[..., b] = v.reshape(H // CELL, CELL, W // CELL, CELL).sum((1, 3))
    off = (np.arange(NCELL) - (NCELL - 1) / 2) * CELL          # cell-centre offsets from the block centre (px)
    wgt = np.exp(-(off[:, None] ** 2 + off[None, :] ** 2) / (2 * 8.0 ** 2)).astype(np.float32)
    Hb, Wb = cells.shape[0] - NCELL + 1, cells.shape[1] - NCELL + 1
    d = np.zeros((Hb, Wb, NCELL, NCELL, BINS), np.float32)
    for a in range(NCELL):
        for b in range(NCELL):
            d[:, :, a, b] = cells[a:a + Hb, b:b + Wb] * wgt[a, b]
    d = d.reshape(Hb, Wb, -1)
    d /= np.linalg.norm(d, axis=-1, keepdims=True) + 1e-6
    d = np.minimum(d, 0.2)
    d /= np.linalg.norm(d, axis=-1, keepdims=True) + 1e-6
    return d, m


def lowe_features(g_before, g_after, valid, region, n):
    db, mb = block_descriptors(g_before)
    da, ma = block_descriptors(g_after)
    Hb, Wb = db.shape[:2]
    rc = (np.arange(Hb) * CELL + 2 * CELL)[:, None], (np.arange(Wb) * CELL + 2 * CELL)[None, :]
    owner = region[rc[0], rc[1]] * valid[rc[0], rc[1]]
    ok = owner > 0
    o = owner[ok] - 1
    cnt = np.maximum(np.bincount(o, minlength=n), 1)
    res = {}
    mean_desc = {}
    for date, d in (("before", db), ("after", da)):
        x = d[ok]
        s = np.zeros((n, x.shape[1]), np.float64)
        np.add.at(s, o, x)
        mean_desc[date] = s / cnt[:, None]
        hist = s.reshape(n, NCELL * NCELL, BINS).sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            p = hist / hist.sum(1, keepdims=True)
            res[f"lowe_entropy_{date}"] = -(p * np.log(np.where(p > 0, p, 1))).sum(1)
    xb, xa = mean_desc["before"], mean_desc["after"]
    with np.errstate(invalid="ignore", divide="ignore"):
        res["lowe_cos_pooled"] = 1 - (xb * xa).sum(1) / (np.linalg.norm(xb, axis=1) * np.linalg.norm(xa, axis=1))
    cb = 1 - (db[ok] * da[ok]).sum(1)
    res["lowe_cos_mean"] = np.bincount(o, weights=cb, minlength=n) / cnt
    has = np.bincount(o, minlength=n) > 0
    for k in list(res):
        res[k] = np.where(has, res[k], np.nan)
    msk = (region > 0) & valid
    rr = region[msk] - 1
    cpx = np.maximum(np.bincount(rr, minlength=n), 1)
    for date, m in (("before", mb), ("after", ma)):
        mm = np.zeros(region.shape, np.float32)
        mm[:m.shape[0], :m.shape[1]] = m
        res[f"lowe_mag_{date}"] = np.bincount(rr, weights=mm[msk], minlength=n) / cpx
    res["lowe_entropy_change"] = res["lowe_entropy_after"] - res["lowe_entropy_before"]
    res["lowe_mag_change"] = res["lowe_mag_after"] - res["lowe_mag_before"]
    return res
