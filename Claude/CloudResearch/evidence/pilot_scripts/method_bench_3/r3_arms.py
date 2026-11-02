"""Phase R (RGB) arms (preregistration_method_bench_3.md, "Phase R").

R0     production's 93 non-DINOv2 road features per band (R, G, B each fed to the same code as its grey input):
       band_rows(). Before-date columns come from the same after-date code with the band matched to itself (an
       identity), checked against the road table on the grey band before use (run_bench3r.py check).
D1e    Chen et al. 2016 IHOT on RGB pairs (chen2016_ihot handoff section 5 arm D1e, Use B): ihot(); gate = EM/Bayes
       hysteresis + blob on iHOT (B1's code).
A2b    Zhang & Guindon 2003 HOT haze correction, lower-bound slope, two-date water proxy (zhang_guindon2003 handoff arm
       A2b): a2b().
ISFA   Wu, Du & Zhang 2014 iterative slow feature analysis (wu2014 handoff arm ISFA-RGB): isfa().
"""
import numpy as np
from scipy import ndimage as ndi

import b3_common as K

BANDS = ("R", "G", "B")


# ------------------------------------------------------------------ R0: per-band features
def band_rows(tid, p, valid, band_m, before_rgb, after_rgb):
    """{band: (before_rows, after_rows)} per road (after_rows order). Each row dict has every *_after column."""
    from after_features import after_rows
    out = {}
    for k, bnd in enumerate(BANDS):
        xb = before_rgb[..., k].astype(np.float32)
        xa = after_rgb[..., k].astype(np.float32)
        rb = after_rows(tid, {**p, "before_grey": xb, "after_grey": xb.copy()}, valid, band_m)
        ra = after_rows(tid, {**p, "before_grey": xb, "after_grey": xa}, valid, band_m)
        out[bnd] = (rb, ra)
    return out


def after_band_rows(tid, p, valid, band_m, before_rgb, corrected_rgb):
    """Per-band after rows of a corrected RGB (the before rows are R0's)."""
    from after_features import after_rows
    return {bnd: after_rows(tid, {**p, "before_grey": before_rgb[..., k].astype(np.float32),
                                  "after_grey": corrected_rgb[..., k].astype(np.float32)}, valid, band_m)
            for k, bnd in enumerate(BANDS)}


# ------------------------------------------------------------------ shared two-date pieces
def grey_fall(before_rgb, after_rgb, valid):
    """'Darkened' pixels: grey fall (before - after, BT.601), centred on the tile's median change (ours: the dates'
    tone curves differ), > 2 SD of the tile's grey change (handoff D1e step 3)."""
    gb, ga = K.grey601(before_rgb), K.grey601(after_rgb)
    fall = gb - ga
    f = fall[valid]
    return valid & ((fall - np.median(f)) > 2 * f.std()), gb, ga


def _ols(X, y):
    A = np.column_stack([X, np.ones(len(X))])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


# ------------------------------------------------------------------ D1e IHOT
def ihot(before_rgb, after_rgb, valid, bands=(0, 1, 2), step=16, max_iter=30, tol=1e-3):
    """Returns (iHOT map on the after tile, info). bands=(0, 2) is D1e-BR (red, blue)."""
    from d1_colour import clear_line
    from sn8_clouds import dark_channel
    xb = before_rgb.astype(np.float64)
    xa = after_rgb.astype(np.float64)
    okb = valid & (before_rgb.max(-1) < 250) & (before_rgb.min(-1) > 5)
    idx = np.flatnonzero(okb)[::step]
    k_cl, b_cl = clear_line(xb[..., 0].ravel()[idx], xb[..., 2].ravel()[idx])
    th = np.arctan(k_cl)
    hot0 = xa[..., 2] * np.sin(th) - xa[..., 0] * np.cos(th)
    fall, gb, ga = grey_fall(before_rgb, after_rgb, valid)
    db = dark_channel(gb.astype(np.float32), valid)
    sat = (after_rgb.max(-1) >= 250) | (before_rgb.max(-1) >= 250)
    F = valid & ~sat & ~fall & ~(db < np.percentile(db[valid], 5))
    fi = np.flatnonzero(F)[::step]
    if len(fi) < 500:
        return None, {"abstain": "fit mask < 500 px", "F_share": float(F[valid].mean())}
    D = (xa - xb).reshape(-1, 3)[:, bands]
    Ra = xa.reshape(-1, 3)[:, bands]
    Rb = xb.reshape(-1, 3)[:, bands]
    ih = hot0.ravel()
    C_prev = -np.inf
    it = 0
    c = 0.0
    for it in range(1, max_iter + 1):
        k1 = _ols(D[fi], ih[fi])                                  # eq. 3: iHOT ~ dR (THOT = fitted)
        thot = D @ k1[:-1] + k1[-1]
        c = k1[-1]                                               # THOT of a clear (dR = 0) pixel
        X2 = np.vstack([Ra[fi], Rb[fi]])
        y2 = np.concatenate([thot[fi], np.full(len(fi), c)])
        k2 = _ols(X2, y2)                                         # eq. 5: THOT (after) / c (before) ~ R
        ih_new = Ra @ k2[:-1] + k2[-1]
        Cc = float(np.corrcoef(thot[fi], ih_new[fi])[0, 1])
        ih = ih_new
        if abs(Cc - C_prev) < tol:
            break
        C_prev = Cc
    out = ih.reshape(valid.shape)
    blue255 = valid & (after_rgb[..., 2] >= 255)
    if blue255.any():
        out = np.where(blue255, out[valid].max(), out)
    return np.where(valid, out, np.nan).astype(np.float32), {
        "iterations": it, "corr": Cc, "k_prime": k2[:-1].tolist(), "c": float(c), "F_share": float(F[valid].mean()),
        "clear_line_k": k_cl}


def ihot_gate(field, valid):
    """EM/Bayes hysteresis + blob on iHOT (the paper gives no cut; B1's code). Abstain rules: P(c) < 0.002 or
    separation < 2 sd_n (B1's third rule is in dark-rise units and does not apply: deviation)."""
    if field is None:
        return np.zeros(valid.shape, bool), {"abstain": "no iHOT"}
    lo = float(np.percentile(field[valid], 1))
    y = np.where(valid, field, np.nanmedian(field[valid])) - lo   # ours: shift to start at 0, as the paper's |X_D|
    e = K.em2(y[valid][::4])
    info = {"em": e}
    if e is None or e["P_c"] < 0.002 or (e["mu_c"] - e["mu_n"]) / e["sd_n"] < 2:
        info["abstain"] = "EM failed" if e is None else ("P(c) < 0.002" if e["P_c"] < 0.002 else "separation < 2 sd_n")
        return np.zeros(valid.shape, bool), info
    t_l, t_h = K.em_cuts(e)
    if t_l is None or t_h is None:
        info["abstain"] = "no Bayes root"
        return np.zeros(valid.shape, bool), info
    info.update(t_l=t_l + lo, t_h=t_h + lo, shift=lo, abstain=None)
    return K.blob(K.hysteresis(y, valid, t_l, t_h)), info


# ------------------------------------------------------------------ A2b HOT haze correction
def a2b(before_rgb, after_rgb, valid, rise_mask, water=True, auto=False):
    """Returns (corrected RGB float32, cannot-assess mask (dHOT > 20), info) or (None, None, info) on abstain."""
    xb = before_rgb.astype(np.float64)
    xa = after_rgb.astype(np.float64)
    fall, gb, ga = grey_fall(before_rgb, after_rgb, valid)
    W = np.zeros(valid.shape, bool)
    clear0 = valid & ~rise_mask & (after_rgb.max(-1) < 250) & (ga > 5)
    # clear line on the after image's clear sample (outside W: iterate once, W needs theta for the before HOT)
    def line(m):
        i = np.flatnonzero(m)[::4]
        a, c = np.polyfit(xa[..., 2].ravel()[i], xa[..., 0].ravel()[i], 1)
        return float(a), float(c)
    a_, c_ = line(clear0)
    th = np.arctan(a_)
    if water:
        hot_b = xb[..., 2] * np.sin(th) - xb[..., 0] * np.cos(th)
        Wb = valid & (hot_b > np.percentile(hot_b[valid], 95)) & (gb < np.percentile(gb[valid], 20))
        W = ndi.binary_dilation(Wb | fall, iterations=4) & valid
        a_, c_ = line(clear0 & ~W)
        th = np.arctan(a_)
    hot = xa[..., 2] * np.sin(th) - xa[..., 0] * np.cos(th)
    dhot = hot + c_ * np.cos(th)
    dhot = _median61(dhot, valid)
    clear_s = clear0 & ~W
    lo = 2.0
    if auto:
        v = dhot[clear_s]
        lo = float(2 * 1.4826 * np.median(np.abs(v - np.median(v))))
    use = valid & ~W
    bins = np.rint(dhot).astype(int)
    s_b = []
    info = {"theta": th, "clear_line": [a_, c_], "W_share": float(W[valid].mean()), "lower_limit": lo}
    for k in range(3):
        xs, ys = [], []
        for h in range(int(np.floor(lo)) + 1, 21):
            m = use & (bins == h)
            if m.sum() >= 100:
                xs.append(h)
                ys.append(np.percentile(xa[..., k][m], 1))
        if len(xs) < 5:
            return None, None, {**info, "abstain": f"band {k}: {len(xs)} bins in ({lo:.1f}, 20]"}
        sl = float(np.polyfit(xs, ys, 1)[0])
        if sl < 0:
            return None, None, {**info, "abstain": f"band {k}: slope {sl:.3f} < 0"}
        s_b.append(sl)
    info["s_b"] = s_b
    corr = xa.copy()
    m = use & (dhot > lo) & (dhot <= 20)
    for k in range(3):
        corr[..., k] = np.where(m, xa[..., k] - s_b[k] * (dhot - lo), xa[..., k])
    cannot = valid & (dhot > 20)
    info["corrected_share"] = float(m[valid].mean())
    info["cannot_share"] = float(cannot[valid].mean())
    corr = np.where(valid[..., None], np.clip(corr, 0, 255), 0).astype(np.float32)
    return corr, cannot, info


def _median61(x, valid):
    """61 x 61 median of a float field (on 0.5-level quantised uint16 via cv2 is not supported for k > 5, so a
    downsample-by-4 median of 15 x 15, upsampled back: an approximation of the 61 px median, logged as ours)."""
    import cv2
    xs = np.where(valid, x, np.nan)[::4, ::4]
    fill = np.nanmedian(xs)
    xs = np.where(np.isfinite(xs), xs, fill).astype(np.float32)
    med = ndi.median_filter(xs, size=15, mode="nearest")
    up = cv2.resize(med, (x.shape[1], x.shape[0]), interpolation=cv2.INTER_LINEAR)
    return up.astype(np.float64)


# ------------------------------------------------------------------ ISFA
def isfa(before_rgb, after_rgb, valid, rise_mask, step=8, max_iter=50, tol=1e-6):
    """Returns (IWD map, |SFA_1| map, info) or (None, None, info)."""
    from scipy.linalg import eigh
    from scipy.stats import chi2
    X = before_rgb.reshape(-1, 3).astype(np.float64)
    Y = after_rgb.reshape(-1, 3).astype(np.float64)
    fitm = (valid & ~rise_mask & (before_rgb.max(-1) < 250) & (after_rgb.max(-1) < 250)).ravel()
    fi = np.flatnonzero(fitm)[::step]
    if len(fi) < 1000:
        return None, None, {"abstain": "fit pixels < 1000"}
    x, y = X[fi], Y[fi]
    v = np.ones(len(fi))
    sl_prev = None
    it = 0
    try:
        for it in range(1, max_iter + 1):
            sw = v.sum()
            mx, my = (v[:, None] * x).sum(0) / sw, (v[:, None] * y).sum(0) / sw
            sx = np.sqrt((v[:, None] * (x - mx) ** 2).sum(0) / sw)
            sy = np.sqrt((v[:, None] * (y - my) ** 2).sum(0) / sw)
            xh, yh = (x - mx) / sx, (y - my) / sy
            dd = xh - yh
            A = (v[:, None, None] * dd[:, :, None] * dd[:, None, :]).sum(0) / sw
            Bm = ((v[:, None, None] * xh[:, :, None] * xh[:, None, :]).sum(0) +
                  (v[:, None, None] * yh[:, :, None] * yh[:, None, :]).sum(0)) / (2 * sw)
            lam, W = eigh(A, Bm)
            sfa = xh @ W - yh @ W
            T = (sfa ** 2 / np.sqrt(np.maximum(lam, 1e-12))).sum(1)
            v = chi2.sf(T, 3)
            sl = np.sqrt(np.maximum(lam, 0))
            if sl_prev is not None and np.abs(sl - sl_prev).max() < tol:
                break
            sl_prev = sl
            if v.sum() < 10:
                return None, None, {"abstain": "weights collapsed", "iterations": it}
    except Exception as e:                                      # singular B etc.: abstain (bench 1's C2 guard)
        return None, None, {"abstain": f"{type(e).__name__}", "iterations": it}
    if it >= max_iter:                                          # handoff step 2: not converged -> abstain
        return None, None, {"abstain": "not converged in 50 iterations", "iterations": it}
    XH, YH = (X - mx) / sx, (Y - my) / sy
    S = XH @ W - YH @ W
    iwd = (S ** 2 / np.sqrt(np.maximum(lam, 1e-12))).sum(1).reshape(valid.shape)
    s1 = np.abs(S[:, 0]).reshape(valid.shape)
    return np.where(valid, iwd, np.nan).astype(np.float32), np.where(valid, s1, np.nan).astype(np.float32), \
        {"iterations": it, "lambda": lam.tolist(), "converged": it < max_iter}


def sfa_grey(before, after, valid):
    """One-band SFA = |standardised difference| (handoff section 2: with one band SFA collapses to it)."""
    b, a = before[valid], after[valid]
    z = np.abs((after - a.mean()) / a.std() - (before - b.mean()) / b.std())
    return np.where(valid, z, np.nan).astype(np.float32)
