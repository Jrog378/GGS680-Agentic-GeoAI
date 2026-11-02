"""Arm C3: the edge of the correction.
C3a fitted fade: per tile, the tone-matched dark-rise excess outside the gate in 1 m distance bins (0-60 m; plotted
     against log-distance in the figures); the fade width is the first bin whose median excess lies within one robust SD
     (1.4826 MAD) of the far-clear median (> 60 m from the gate), clipped to [5, 60] m (our rule; the literature says
     near-cloud brightening decays with distance, Koren 2007 / Varnai & Marshak 2009, evidence 10, and that fixed
     buffers are operational choices, claim_checks_A g1 #4, g2 #4).
C3b Poisson seam (Perez, Gangnet & Blake 2003, TOG 22:313, Eqs. 4-5, 7, p. 315; handoff
     literature_fulltext/perez2003_poisson_image_editing_TOG.md section 3): the correction field c = corrected - after at
     full strength inside the gate; on the 20 m margin band c~ solves the Laplace equation (4-neighbour) with c~ = c on
     the gate and 0 beyond the band (membrane interpolant of the mismatch); no-data are Neumann (left out).
Both use sn8_cloudedge.edge_parts (the C0 fit's gate, tone, airlight, data t, signed distance), imported.
"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

BIN_PX, MAX_PX, MIN_W_PX = 2, 120, 10


def fitted_width(parts, valid):
    sd, rise = parts["sd"], parts["rise"]
    far = valid & (sd > MAX_PX)
    if far.sum() < 1000:
        return 40, {"note": "too little far-clear ground; C0's 40 px"}
    e_inf = float(np.median(rise[far]))
    s = float(1.4826 * np.median(np.abs(rise[far] - e_inf)))
    prof = []
    width = MAX_PX
    for d0 in range(0, MAX_PX, BIN_PX):
        m = valid & (sd > d0) & (sd <= d0 + BIN_PX)
        med = float(np.median(rise[m])) if m.sum() >= 50 else np.nan
        prof.append((d0 + BIN_PX / 2, med, int(m.sum())))
        if np.isfinite(med) and med <= e_inf + s and width == MAX_PX:
            width = d0 + BIN_PX
    width = int(np.clip(width, MIN_W_PX, MAX_PX))
    return width, {"far_median": e_inf, "far_robust_sd": s, "profile": prof, "width_px": width}


def _apply(parts, after, valid, t):
    a = parts["airlight"]
    t = np.where(valid, t, 1).astype(np.float32)
    opaque = valid & (t < 0.2)
    corr = np.where(opaque, after, (after - a) / np.maximum(t, 0.2) + a)
    return {"corrected": np.where(valid, np.clip(corr, 1, 255), 0).astype(np.float32), "t": t, "opaque": opaque,
            "region": parts["gate"]}


def correct_fade(before, after, valid, parts):
    w, info = fitted_width(parts, valid)
    fade = np.clip(1 - np.maximum(parts["sd"], 0) / w, 0, 1)
    out = _apply(parts, after, valid, 1 - fade * (1 - parts["t_data"]))
    out["info"] = info
    return out


def correct_poisson(before, after, valid, parts, margin_px=40):
    gate, sd = parts["gate"], parts["sd"]
    full = _apply(parts, after, valid, np.where(gate, parts["t_data"], 1.0))
    c = np.where(gate & valid, full["corrected"] - after, 0.0)
    band = valid & ~gate & (sd > 0) & (sd <= margin_px)
    idx = -np.ones(gate.shape, np.int64)
    pts = np.flatnonzero(band)
    idx.ravel()[pts] = np.arange(len(pts))
    H, W = gate.shape
    rr, cc = np.divmod(pts, W)
    rows, cols, vals = [], [], []
    rhs = np.zeros(len(pts))
    diag = np.zeros(len(pts))
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        r2, c2 = rr + dr, cc + dc
        inside = (r2 >= 0) & (r2 < H) & (c2 >= 0) & (c2 < W)
        r2c, c2c = np.clip(r2, 0, H - 1), np.clip(c2, 0, W - 1)
        nv = inside & valid[r2c, c2c]                 # no-data and the tile edge: Neumann (term dropped)
        diag += nv
        nb = idx[r2c, c2c]
        un = nv & (nb >= 0)                           # unknown neighbour in the band
        rows.append(np.flatnonzero(un)); cols.append(nb[un]); vals.append(-np.ones(un.sum()))
        known = nv & (nb < 0)                         # Dirichlet: the gate (c) or beyond the band (0)
        rhs[known] += c[r2c[known], c2c[known]]
    A = sp.csr_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(len(pts))]),
                                                       np.concatenate(cols + [np.arange(len(pts))]))),
                      shape=(len(pts), len(pts)))
    ct = c.copy()
    if len(pts):
        ok = diag > 0
        sol = np.zeros(len(pts))
        sol[ok] = spsolve(A[ok][:, ok].tocsc(), rhs[ok])
        ct.ravel()[pts] = sol
    corr = np.where(valid, np.clip(after + ct, 1, 255), 0).astype(np.float32)
    return {"corrected": corr, "t": full["t"], "opaque": full["opaque"], "region": gate,
            "info": {"band_px": int(len(pts))}}
