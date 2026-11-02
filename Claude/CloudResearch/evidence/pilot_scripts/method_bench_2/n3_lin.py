"""Arm N3: Lin, Lin, Lee & Chen (2015, ISPRS JPRS 106:107) weighted-PCA invariant pixels, Du-style mean/SD map
(handoff literature_fulltext/lin2015_radiometric_normalization_cloud_detection_invariant_pixels_ISPRS.md section 1
steps 1-6, section 5; claim_checks_D1 Lin #1, #7). Also the selector for G2 (g2_lin_bluerise.py).

1. 256 x 256 scatterplot of before vs after over ALL valid pixels (no cloud or water mask, as the paper); points on the
   top border (after = 255) and right border (before = 255) removed ("generally belong to the clouds", p. 110).
2. Per pixel similarity from the two dates' multi-band vectors (eqs. 7-10): S_ED = ||x_a - x_b|| / Max_ED (Max_ED = the
   tile's maximum), S_SA = arccos(<x_a, x_b> / (|x_a| |x_b|)) in radians, S_SC = 0.5 (1 - corr(x_a, x_b)) across the
   bands (0.5 where a vector is constant), S = 1 - (S_ED + S_SA + S_SC) / 3.
3. Point weight = sum of S over the pixels on that scatterplot point, replaced by its empirical CDF (eq. 11).
4. Weighted PCA over the occupied points (eq. 12) -> major axis.
5. Invariant pixels = within +-d of the axis; d = the largest of 1..40 DN whose candidates correlate > 0.9 (p. 111).
6. Map = Du 2002 mean/SD matching on those PIFs (eqs. 1-3), before -> after scale.
Deviations: the axis on grey (the band C0 corrects) with S from RGB; one global fit per tile; the d grid is ours;
abstain (gate opaque) if no d passes or < 1,000 PIFs.
N3-bounded (amendment 2026-10-30, DEVIATION): also abstain if the gain is outside 0.1-10.
"""
import numpy as np

import b2_common as B

R_PIF = 0.9
D_GRID = np.arange(1, 41)


def similarity(rgb_b, rgb_a, m):
    xb = rgb_b.reshape(-1, 3)[m.ravel()].astype(np.float64)
    xa = rgb_a.reshape(-1, 3)[m.ravel()].astype(np.float64)
    ed = np.sqrt(((xa - xb) ** 2).sum(1))
    s_ed = ed / max(ed.max(), 1e-9)
    nb, na = np.linalg.norm(xb, axis=1), np.linalg.norm(xa, axis=1)
    cosang = np.where((nb > 0) & (na > 0), (xa * xb).sum(1) / np.maximum(nb * na, 1e-12), 1.0)
    s_sa = np.arccos(np.clip(cosang, -1, 1))
    cb, ca = xb - xb.mean(1, keepdims=True), xa - xa.mean(1, keepdims=True)
    den = np.sqrt((cb ** 2).sum(1) * (ca ** 2).sum(1))
    corr = np.where(den > 0, (cb * ca).sum(1) / np.maximum(den, 1e-12), 0.0)
    s_sc = 0.5 * (1 - corr)
    return 1 - (s_ed + s_sa + s_sc) / 3


def weighted_axis(xb, xa, S):
    """Weighted PCA over occupied scatterplot points (top/right borders removed). Returns axis tuple and info."""
    bi, ai = np.clip(np.rint(xb), 0, 255).astype(int), np.clip(np.rint(xa), 0, 255).astype(int)
    keep = (bi < 255) & (ai < 255)
    W = np.zeros((256, 256))
    np.add.at(W, (bi[keep], ai[keep]), S[keep])
    occ = np.argwhere(W > 0)
    wv = W[occ[:, 0], occ[:, 1]]
    order = np.argsort(wv)
    cdf = np.empty(len(wv))
    cdf[order] = np.arange(1, len(wv) + 1) / len(wv)          # empirical CDF of the point weights (eq. 11)
    mx, my, major, minor, ev = B.pca_axis(occ[:, 0].astype(float), occ[:, 1].astype(float), cdf)
    return (mx, my, major, minor), {"points": int(len(wv)), "axis_slope": float(major[1] / major[0]) if major[0] else
                                    float("inf"), "eig": ev.tolist()}


def select(xb, xa, S):
    """PIF indices (into xb/xa) and info, or (None, info)."""
    (mx, my, major, minor), info = weighted_axis(xb, xa, S)
    m = np.abs(B.minor_coord(xb, xa, mx, my, minor))
    order = np.argsort(m)
    ms = m[order]
    xs, ys = xb[order].astype(np.float64), xa[order].astype(np.float64)
    n = np.arange(1, len(xs) + 1)
    sx, sy = np.cumsum(xs), np.cumsum(ys)
    sxx, syy, sxy = np.cumsum(xs * xs), np.cumsum(ys * ys), np.cumsum(xs * ys)
    best, rbest = None, None
    for d in D_GRID:
        k = int(np.searchsorted(ms, d, side="right"))
        if k < 3:
            continue
        cov = sxy[k - 1] / k - sx[k - 1] / k * sy[k - 1] / k
        vx = sxx[k - 1] / k - (sx[k - 1] / k) ** 2
        vy = syy[k - 1] / k - (sy[k - 1] / k) ** 2
        r = cov / np.sqrt(max(vx * vy, 1e-12))
        if r > R_PIF:
            best, rbest = int(d), float(r)
    info.update(d=best, r=rbest)
    if best is None:
        info["abstain"] = "no d with r > 0.9"
        return None, info
    idx = order[: int(np.searchsorted(ms, best, side="right"))]
    info["pif_px"] = int(len(idx))
    if len(idx) < B.MIN_PIF:
        info["abstain"] = "PIF < 1000"
        return None, info
    return idx, info


def fit(xb, xa, S, bound=False):
    """(tone function or None, info) for one band pair."""
    idx, info = select(xb, xa, S)
    if idx is None:
        return None, info
    gain, off = B.meansd_map(xb[idx], xa[idx])
    info.update(gain=gain, offset=off)
    if not gain > 0:
        info["abstain"] = f"gain {gain}"
        return None, info
    if bound and B.out_of_bound(gain):
        info["abstain"] = f"gain {gain} outside {B.GAIN_BOUND}"
        return None, info
    return B.linear_tone(gain, off), info


def make_tone_fn(before_rgb, after_rgb, bound=False):
    """tone_fn for c_common.darkref_variant: the axis on grey over all valid pixels, S from RGB."""
    def tone_fn(before, after, clear, valid, b, a):
        S = similarity(before_rgb, after_rgb, valid)
        return fit(b[valid].astype(np.float64), a[valid].astype(np.float64), S, bound)
    return tone_fn


def correct(before, after, valid, before_rgb, after_rgb, gate=None, bound=False):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, tone_fn=make_tone_fn(before_rgb, after_rgb, bound), gate=gate)
