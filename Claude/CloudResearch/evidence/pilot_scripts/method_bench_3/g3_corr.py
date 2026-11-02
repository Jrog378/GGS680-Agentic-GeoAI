"""Phase G correction arms (preregistration_method_bench_3.md, "G-corr family"). Each replaces one step of C0.

All arms start from sn8_cloudedge.edge_parts (C0's gate, tone curve, grey airlight A, data t, signed distance). A new t
is used inside C0's gate and spread by C0's 20 m linear fade (sn8_cloudedge.spread_t "fade"); t < 0.2 is opaque (left
as is); J = (I - A) / t + A, clipped to [1, 255] (sn8_cloudedge.edge_dehaze's arithmetic, repeated here).

P1   Pan et al. 2015 eq. 12: t = (A - D_after) / (A - C), D = 15 x 15 minimum, C_tile = mean tone(D_before) over C0's
     clear pixels; guided filter r 20, eps 1e-3 (pan2015 handoff section 5 arm P1). P1w: C(x) = 61 x 61 box mean.
S1   Li, Hu & Ai 2019 eq. 17: t = 1 - 0.95 min_c(u_c - sigma) over 15 x 15, guided r 55, eps 1e-3; no homomorphic stage,
     no colour transfer (li_hu_ai2019 handoff arm S1). S1p: the sphere value in Pan's eq. 12 with a before-date C.
M1   Gibson et al. 2012 eqs. 10-11: theta = 11 x 11 median of I / A, t = 1 - 0.95 theta, no refinement.
L1   Lin et al. 2013 eq. 9 (Poisson, Perez 2003): C0's full-strength correction cloned into the after image over the
     gate dilated by 40 px; guidance across the gate edge dropped (DEVIATION, see the preregistration).
rgb=True runs the colour form (min over bands for P1/S1/M1; per band for L1) for Phase R.
"""
import numpy as np
from scipy import ndimage as ndi
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

import b3_common as K

T_MIN = 0.2
PAN_WIN, PAN_R, PAN_EPS, PAN_T0 = 15, 20, 1e-3, 0.1
S1_WIN, S1_W, S1_R, S1_EPS = 15, 0.95, 55, 1e-3
M1_WIN, M1_W = 11, 0.95
LOCAL_C_WIN = 61
FADE_PX = 40
CLEAR_MARGIN_PX = 20
ARMS = ["P1 Pan C tile", "P1w Pan C local", "S1 sphere DCP", "S1p sphere + Pan C", "M1 median DCP", "L1 Poisson seam"]


def _guide(after, valid):
    g = after if after.ndim == 2 else K.grey601(after)
    return np.where(valid, g, np.median(g[valid])).astype(np.float32) / 255


def _vbox(x, valid, win):
    v = valid.astype(np.float32)
    return K.box(np.where(valid, x, 0), win) / np.maximum(K.box(v, win), 1e-6)


def _minband(img):
    return img if img.ndim == 2 else img.min(-1)


def _apply(parts, after, valid, t_src, info):
    """C0's fade and arithmetic for a new t (grey or RGB after)."""
    from sn8_cloudedge import spread_t
    t, region = spread_t(parts, valid, np.clip(t_src, 0, 1), ("fade",))
    t = np.where(valid, t, 1).astype(np.float32)
    a = parts["airlight"]
    opaque = valid & (t < T_MIN)
    tt = t if after.ndim == 2 else t[..., None]
    op = opaque if after.ndim == 2 else opaque[..., None]
    corr = np.where(op, after, (after - a) / np.maximum(tt, T_MIN) + a)
    vv = valid if after.ndim == 2 else valid[..., None]
    return {"corrected": np.where(vv, np.clip(corr, 1, 255), 0).astype(np.float32), "t": t, "gate": parts["gate"],
            "opaque": opaque, "info": info}


def clear_of(parts, valid):
    return valid & ~ndi.binary_dilation(parts["gate"], iterations=CLEAR_MARGIN_PX)


def p1(parts, before, after, valid, local=False):
    A, tone = parts["airlight"], parts["tone"]
    da = K.erode_min(_minband(after), valid, PAN_WIN)
    db = tone(K.erode_min(_minband(before), valid, PAN_WIN))
    clear = clear_of(parts, valid)
    if local:
        C = _vbox(db, valid, LOCAL_C_WIN)
        c_info = {"C_median": float(np.median(C[valid]))}
    else:
        C = float(db[clear].mean())
        c_info = {"C_tile": C}
    den = A - C
    if np.min(den) <= 1:
        return None, {**c_info, "abstain": "A - C <= 1"}
    t = np.clip((A - da) / den, PAN_T0, 1)
    t = np.clip(K.guided(_guide(after, valid), t, PAN_R, PAN_EPS), 0, 1)
    return t, {**c_info, "A": A}


def _sphere(img, valid, A):
    """min_c (u_c - sigma) of I / A over 15 x 15 (sigma = mean of the band SDs), valid-normalised boxes."""
    x = img[..., None] if img.ndim == 2 else img
    us, ss = [], []
    for c in range(x.shape[-1]):
        n = x[..., c].astype(np.float32) / A
        u = _vbox(n, valid, S1_WIN)
        s = np.sqrt(np.maximum(_vbox(n * n, valid, S1_WIN) - u * u, 0))
        us.append(u)
        ss.append(s)
    sigma = np.mean(ss, 0)
    return np.min([u - sigma for u in us], 0)


def s1(parts, before, after, valid):
    A = parts["airlight"]
    m = _sphere(after, valid, A)
    t = np.clip(1 - S1_W * m, PAN_T0, 1)
    t = np.clip(K.guided(_guide(after, valid), t, S1_R, S1_EPS), 0, 1)
    return t, {"A": A, "sphere_median_gate": float(np.median(m[parts["gate"] & valid])) if parts["gate"].any() else None}


def s1p(parts, before, after, valid):
    A, tone = parts["airlight"], parts["tone"]
    Ds_a = A * _sphere(after, valid, A)
    Ds_b = tone(A * _sphere(before, valid, A))
    clear = clear_of(parts, valid)
    C = float(Ds_b[clear].mean())
    if A - C <= 1:
        return None, {"C_tile": C, "abstain": "A - C <= 1"}
    t = np.clip((A - Ds_a) / (A - C), PAN_T0, 1)
    t = np.clip(K.guided(_guide(after, valid), t, S1_R, S1_EPS), 0, 1)
    return t, {"C_tile": C, "A": A}


def m1(parts, before, after, valid):
    import cv2
    A = parts["airlight"]
    g = np.where(valid, np.clip(np.rint(_minband(after)), 0, 255), 255).astype(np.uint8)
    theta = cv2.medianBlur(g, M1_WIN).astype(np.float32) / A       # median of I/A = median(I)/A (A > 0 constant)
    t = np.clip(1 - M1_W * theta, 0.01, 1)
    return t, {"A": A}


def _poisson(after_band, valid, gate, c, omega):
    """Solve |N_p| h_p - sum_{q in N_p, q in omega} h_q = sum_{q in N_p, p and q in gate} (c_p - c_q) on omega, h = 0
    outside (f = after + h); no-data and the tile edge are Neumann (dropped)."""
    H, W = valid.shape
    pts = np.flatnonzero(omega)
    idx = -np.ones(H * W, np.int64)
    idx[pts] = np.arange(len(pts))
    rr, cc = np.divmod(pts, W)
    rows, cols, vals = [], [], []
    rhs = np.zeros(len(pts))
    diag = np.zeros(len(pts))
    gflat, cflat, vflat = gate.ravel(), c.ravel(), valid.ravel()
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        r2, c2 = rr + dr, cc + dc
        inside = (r2 >= 0) & (r2 < H) & (c2 >= 0) & (c2 < W)
        q = np.clip(r2, 0, H - 1) * W + np.clip(c2, 0, W - 1)
        nv = inside & vflat[q]
        diag += nv
        nb = idx[q]
        un = nv & (nb >= 0)
        rows.append(np.flatnonzero(un)); cols.append(nb[un]); vals.append(-np.ones(int(un.sum())))
        both = nv & gflat[pts] & gflat[q]
        rhs[both] += cflat[pts][both] - cflat[q][both]
    A = sp.csr_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(len(pts))]),
                                                       np.concatenate(cols + [np.arange(len(pts))]))),
                      shape=(len(pts), len(pts)))
    ok = diag > 0
    sol = np.zeros(len(pts))
    if ok.any():
        Ao = A[ok][:, ok].tocsc()
        sol[ok] = spsolve(Ao, rhs[ok])
        res = float(np.linalg.norm(Ao @ sol[ok] - rhs[ok]) / max(np.linalg.norm(rhs[ok]), 1e-12))
    else:
        res = 0.0
    h = np.zeros(H * W)
    h[pts] = sol
    return h.reshape(H, W), res


def l1(parts, before, after, valid):
    """Returns the full output dict (not only t)."""
    gate = parts["gate"] & valid
    t = np.where(gate, parts["t_data"], 1.0).astype(np.float32)
    t = np.where(valid, t, 1).astype(np.float32)
    a = parts["airlight"]
    opaque = valid & (t < T_MIN)
    omega = valid & ndi.binary_dilation(gate, iterations=FADE_PX)
    bands = [after] if after.ndim == 2 else [after[..., k] for k in range(3)]
    outs, res = [], []
    for x in bands:
        full = np.where(opaque, x, (x - a) / np.maximum(t, T_MIN) + a)
        c = np.where(gate, np.clip(full, 1, 255) - x, 0.0)
        h, r = _poisson(x, valid, gate, c, omega)
        outs.append(np.where(valid, np.clip(x + h, 1, 255), 0))
        res.append(r)
    corr = outs[0] if after.ndim == 2 else np.stack(outs, -1)
    return {"corrected": corr.astype(np.float32), "t": t, "gate": parts["gate"], "opaque": opaque,
            "info": {"omega_px": int(omega.sum()), "rel_residual": max(res)}}


def outputs(before, after, valid, base=None, only=None, after_rgb=None, before_rgb=None):
    """{arm: output dict} for the Phase G corrections (grey). With after_rgb/before_rgb given (Phase R), the colour form:
    P1/S1/M1 from the minimum over bands, L1 per band; t from the grey parts (C0's gate/tone/airlight)."""
    from sn8_cloudedge import edge_parts
    from sn8_refhaze import dark_reference_dehaze
    base = dark_reference_dehaze(before, after, valid) if base is None else base
    if not base["gate"].any():
        return {}
    parts = edge_parts(before, after, valid, base)
    if parts is None:
        return {}
    want = (lambda a: True) if only is None else (lambda a: a in only)
    A_img = after if after_rgb is None else after_rgb.astype(np.float32)
    B_img = before if before_rgb is None else before_rgb.astype(np.float32)
    out = {}
    fns = {"P1 Pan C tile": lambda: p1(parts, B_img, A_img, valid),
           "P1w Pan C local": lambda: p1(parts, B_img, A_img, valid, local=True),
           "S1 sphere DCP": lambda: s1(parts, B_img, A_img, valid),
           "S1p sphere + Pan C": lambda: s1p(parts, B_img, A_img, valid),
           "M1 median DCP": lambda: m1(parts, B_img, A_img, valid)}
    for arm, fn in fns.items():
        if not want(arm):
            continue
        t, info = fn()
        if t is None:                                   # abstain: the gate cannot be assessed, image as is
            out[arm] = {"corrected": np.where(valid if A_img.ndim == 2 else valid[..., None], A_img, 0).astype(np.float32),
                        "t": np.ones(valid.shape, np.float32), "gate": parts["gate"], "opaque": parts["gate"] & valid,
                        "info": info}
        else:
            out[arm] = _apply(parts, A_img, valid, t, info)
    if want("L1 Poisson seam"):
        out["L1 Poisson seam"] = l1(parts, B_img, A_img, valid)
    return out
