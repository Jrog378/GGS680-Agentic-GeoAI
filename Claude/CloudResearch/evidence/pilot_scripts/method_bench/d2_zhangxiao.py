"""Arm D2: Zhang & Xiao (2014, IEEE TGRS 52:7264) rule-based cloud detection for RGB aerial photographs, with the
paper's fixed constants (handoff literature_fulltext/zhang2014_cloud_detection_rgb_aerial_photographs_TGRS.md, accepted
manuscript pp. 3-8; claim_checks_C Zhang & Xiao #3-7).

Steps: HSI (Eqs. 1-3); significance map W = (I + 1) / (H + 1) with I, H on [0, 1] (Eq. 4), bilateral-filtered and
rescaled to [0, 255]; coarse mask = W >= Otsu clamped to [100, 150] and 50 <= H <= 80 (Eqs. 5-7); detail map from an
iterated bilateral filter on I (M = 4, window 7, sigma_s,0 = 2, sigma_s,1 = sqrt(3) sigma_s,0, sigma_s,j =
2^(j-1) sigma_s,j-1, sigma_r = max(I) / 10), levels 2..M weighted by w_j = G_7 * exp(|D_j|) (Eqs. 8-15), dilated twice
(7 x 7), Otsu, low detail = cloud-like; R_finer = coarse AND low detail, median filter, components < 120 px dropped,
holes filled; guided feathering with the colour photo as guide (r = 60, eps = 1e-6, He et al. 2013 Eqs. 19-21), soft
output thresholded at 60/255.
Choices the paper leaves open (fixed in the plan before scoring): W's bilateral filter d = 7, sigma_color = 0.1 (W on
its [0.5, 2] scale), sigma_space = 2; I on [0, 1] inside the detail map (exp(|D|) needs it); the median filter 5 x 5;
the printed signed sum of D_j taken as |D_j| (the handoff: the paper's intent is the amount of detail).
"""
import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage.filters import threshold_otsu

S6 = np.sqrt(6.0)


def hsi(rgb):
    x = rgb.astype(np.float32)
    R, G, B = x[..., 0], x[..., 1], x[..., 2]
    I = (R + G + B) / 3
    V1 = -(S6 / 6) * R - (S6 / 6) * G + (S6 / 3) * B
    V2 = (1 / S6) * R - (2 / S6) * G
    H = (np.arctan2(V2, V1) + np.pi) * 255 / (2 * np.pi)
    return I, H


def colour_guided_filter(guide, p, r, eps):
    """He et al. 2013 Eqs. 19-21: guided filter with a 3-channel guide (H, W, 3) on [0, 1]; box windows of side 2r+1."""
    win = (2 * r + 1, 2 * r + 1)
    f = lambda a: cv2.blur(a.astype(np.float32), win)
    I = [guide[..., c].astype(np.float32) for c in range(3)]
    mI = [f(c) for c in I]
    mp = f(p)
    cov_Ip = [f(I[c] * p) - mI[c] * mp for c in range(3)]
    v = {}
    for a in range(3):
        for b in range(a, 3):
            v[a, b] = f(I[a] * I[b]) - mI[a] * mI[b] + (eps if a == b else 0)
    # inverse of the symmetric 3x3 [[v00 v01 v02],[v01 v11 v12],[v02 v12 v22]] per pixel
    a00, a01, a02, a11, a12, a22 = v[0, 0], v[0, 1], v[0, 2], v[1, 1], v[1, 2], v[2, 2]
    c00 = a11 * a22 - a12 * a12
    c01 = a02 * a12 - a01 * a22
    c02 = a01 * a12 - a02 * a11
    c11 = a00 * a22 - a02 * a02
    c12 = a01 * a02 - a00 * a12
    c22 = a00 * a11 - a01 * a01
    det = a00 * c00 + a01 * c01 + a02 * c02
    det = np.where(np.abs(det) < 1e-30, 1e-30, det)
    inv = [[c00, c01, c02], [c01, c11, c12], [c02, c12, c22]]
    a = [(inv[k][0] * cov_Ip[0] + inv[k][1] * cov_Ip[1] + inv[k][2] * cov_Ip[2]) / det for k in range(3)]
    b = mp - a[0] * mI[0] - a[1] * mI[1] - a[2] * mI[2]
    return f(a[0]) * I[0] + f(a[1]) * I[1] + f(a[2]) * I[2] + f(b)


def detail_map(I01, M=4, win=7, sigma_d=7):
    sr = float(I01.max()) / 10 if I01.max() > 0 else 0.1
    ss = [2.0, np.sqrt(3) * 2.0]
    for j in range(2, M + 1):
        ss.append(2 ** (j - 1) * ss[j - 1])
    prev = I01.astype(np.float32)
    D = []
    for j in range(1, M + 1):
        cur = cv2.bilateralFilter(prev, win, sr, ss[j])
        D.append(cur - prev)
        prev = cur
    num = np.zeros_like(I01, np.float32)
    den = np.zeros_like(I01, np.float32)
    for j in range(2, M + 1):                      # D_1 skipped (noise), levels 2..M
        d = np.abs(D[j - 1])
        w = cv2.GaussianBlur(np.exp(d), (0, 0), sigma_d)
        num += w * d
        den += w
    det = num / np.maximum(den, 1e-12)
    k = np.ones((7, 7), np.uint8)
    return cv2.dilate(det, k, iterations=2)


def zhang_xiao(rgb, return_soft=False):
    """The binary cloud mask (and optionally the soft feathered output on [0, 1])."""
    I, H = hsi(rgb)
    W = (I / 255 + 1.0) / (H / 255 + 1.0)
    Wf = cv2.bilateralFilter(W.astype(np.float32), 7, 0.1, 2)
    lo, hi = float(Wf.min()), float(Wf.max())
    W255 = (Wf - lo) / max(hi - lo, 1e-9) * 255
    t_glob = threshold_otsu(W255)
    t_opt = min(max(t_glob, 100.0), 150.0)
    coarse = (W255 >= t_opt) & (H >= 50) & (H <= 80)
    det = detail_map(I / 255)
    low_detail = det < threshold_otsu(det)
    finer = coarse & low_detail
    finer = cv2.medianBlur(finer.astype(np.uint8) * 255, 5) > 0
    lab, n = ndi.label(finer)
    if n:
        size = np.bincount(lab.ravel(), minlength=n + 1)
        keep = np.flatnonzero(size >= 120)
        finer = np.isin(lab, keep[keep > 0])
    finer = ndi.binary_fill_holes(finer)
    soft = colour_guided_filter(rgb.astype(np.float32) / 255, finer.astype(np.float32), 60, 1e-6)
    mask = soft >= 60 / 255
    return (mask, np.clip(soft, 0, 1)) if return_soft else mask
