"""Method bench 3 (outputs/preregistration_method_bench_3.md): paths, guards and the shared numerical pieces.

Benches 1 and 2 are imported read-only (b2_common sets the thread limits, the memory wait and sys.path for bench 1's
mb_common, c_common, after_features, run_ida, ida_score). Nothing in those folders is edited.
Development data only; production.json is read-only (sha256 checked by every runner).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MB2 = HERE.parent / "method_bench_2"
if str(MB2) not in sys.path:
    sys.path.insert(1, str(MB2))
import b2_common as B                          # noqa: E402  (forces 2 threads; adds bench 1 and the library)

import numpy as np                              # noqa: E402
from scipy import ndimage as ndi                # noqa: E402

M1 = B.M1
CR = B.CR
FIG = CR / "figures" / "method_bench_3"
NB = CR / "notebooks" / "method_bench_3"
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache")
SMOKE_TILES = ("2_23_44", "2_15_45", "2_19_55")
PROD_RISE = 71.36                               # production's dark-rise cut (sn8_clouds.cloud_thresholds), checked
EIGHT = np.ones((3, 3), bool)
BLOB_M2 = 2500.0

log, write_json, registry_hash, dev_guard_tiles = M1.log, M1.write_json, M1.registry_hash, M1.dev_guard_tiles
wait_for_memory, memory_ok, grey601 = B.wait_for_memory, B.memory_ok, B.grey601


def atomic_bytes(path, data):
    path = Path(path)
    tmp = path.with_name(path.name + ".writing")
    tmp.write_bytes(data)
    tmp.replace(path)


def atomic_npz(path, **arrays):
    path = Path(path)
    tmp = path.with_name(path.stem + "_writing.npz")
    np.savez_compressed(tmp, **arrays)
    tmp.replace(path)


def train_tiles():
    import pandas as pd
    idx = pd.read_csv("/Users/jusrogers/Masters/GGS662/ProjectBranch/Images/SN8_Louisiana-East_Ida2021_greyscale/tiles.csv")
    t = list(idx.tile_id[idx.split == "train"])
    dev_guard_tiles(t)
    return t


# ------------------------------------------------------------------ Otsu over integer levels (Otsu 1979 eqs. 17-19)
def otsu_int(values, lo=-255, hi=255):
    """k*, eta*, omega1, mu0, mu1 on the integer-level histogram lo..hi (values rounded and clipped)."""
    v = np.clip(np.rint(values), lo, hi).astype(int) - lo
    L = hi - lo + 1
    p = np.bincount(v, minlength=L).astype(np.float64)
    p /= p.sum()
    i = np.arange(L, dtype=np.float64)
    w = np.cumsum(p)
    mu = np.cumsum(i * p)
    mu_t = mu[-1]
    s_t = float(((i - mu_t) ** 2 * p).sum())
    ok = (w > 0) & (w < 1)                                   # the effective range S*
    sb = np.full(L, -np.inf)
    sb[ok] = (mu_t * w[ok] - mu[ok]) ** 2 / (w[ok] * (1 - w[ok]))    # eq. 18
    k = int(np.argmax(sb))                                   # eq. 19 (C0 = levels <= k)
    eta = float(sb[k] / s_t) if s_t > 0 else 0.0
    w0 = float(w[k])
    mu0 = float(mu[k] / w0) + lo
    mu1 = float((mu_t - mu[k]) / (1 - w0)) + lo
    return {"k_star": float(k + lo), "eta_star": eta, "omega1": 1 - w0, "mu0": mu0, "mu1": mu1}


# ------------------------------------------------------------------ two-Gaussian EM (Bruzzone & Fernandez Prieto 2000)
def _norm(x, m, s):
    return np.exp(-0.5 * ((x - m) / s) ** 2) / (np.sqrt(2 * np.pi) * s)


def em2(y, alpha=0.5, init=None, tol=1e-6, max_iter=100):
    """Two-Gaussian EM, eqs. 2-4 (variance with the current mean, as printed). init: None -> alpha around the midpoint
    of [p1, p99.9] (handoff step 2); or a cut value (S_n = y <= cut, S_c = y > cut). Returns dict or None."""
    y = np.asarray(y, np.float64)
    if init is None:
        lo, hi = np.percentile(y, [1, 99.9])
        M = (hi + lo) / 2                    # (max + min) / 2 (the printed formula equals it only when min = 0)
        sn, sc = y < M * (1 - alpha) if M > 0 else y < M * (1 + alpha), y > M * (1 + alpha) if M > 0 else y > M * (1 - alpha)
    else:
        sn, sc = y <= init, y > init
    if sn.sum() < 10 or sc.sum() < 10:
        return None
    pn, pc = sn.mean() / (sn.mean() + sc.mean()), sc.mean() / (sn.mean() + sc.mean())
    mn, mc = y[sn].mean(), y[sc].mean()
    vn, vc = max(y[sn].var(), 1e-6), max(y[sc].var(), 1e-6)
    ll_old = -np.inf
    it = 0
    for it in range(1, max_iter + 1):
        a, b = pn * _norm(y, mn, np.sqrt(vn)), pc * _norm(y, mc, np.sqrt(vc))
        tot = np.maximum(a + b, 1e-300)
        ll = float(np.log(tot).sum())
        wn, wc = a / tot, b / tot
        sw_n, sw_c = wn.sum(), wc.sum()
        if sw_n < 1e-9 or sw_c < 1e-9:
            break
        vn_new = max(float((wn * (y - mn) ** 2).sum() / sw_n), 1e-6)    # eq. 4 with mu^t
        vc_new = max(float((wc * (y - mc) ** 2).sum() / sw_c), 1e-6)
        mn, mc = float((wn * y).sum() / sw_n), float((wc * y).sum() / sw_c)   # eq. 3
        pn, pc = sw_n / len(y), sw_c / len(y)                               # eq. 2
        vn, vc = vn_new, vc_new
        if np.isfinite(ll_old) and abs(ll - ll_old) < tol * abs(ll_old):
            break
        ll_old = ll
    if mc < mn:                               # keep "c" as the higher-mean (changed) class
        pn, pc, mn, mc, vn, vc = pc, pn, mc, mn, vc, vn
    return {"P_n": float(pn), "P_c": float(pc), "mu_n": float(mn), "mu_c": float(mc), "sd_n": float(np.sqrt(vn)),
            "sd_c": float(np.sqrt(vc)), "iterations": it, "loglik": ll_old}


def posterior_c(y, e):
    a = e["P_n"] * _norm(y, e["mu_n"], e["sd_n"])
    b = e["P_c"] * _norm(y, e["mu_c"], e["sd_c"])
    return b / np.maximum(a + b, 1e-300)


def bayes_cut(e):
    """T_o: root of eq. 7 between mu_n and mu_c (P(c|T) = 0.5, eq. 6), or None. The log term enters with a PLUS sign:
    that is what eq. 6 (P_c p(T|c) = P_n p(T|n)) gives for Gaussians; the handoff's transcription of eq. 7 prints a
    minus, which does not satisfy eq. 6 (checked numerically on the smoke tile, deviation 1 of the preregistration)."""
    sn2, sc2 = e["sd_n"] ** 2, e["sd_c"] ** 2
    mn, mc, Pn, Pc = e["mu_n"], e["mu_c"], e["P_n"], e["P_c"]
    a = sn2 - sc2
    b = 2 * (mn * sc2 - mc * sn2)
    c = mc ** 2 * sn2 - mn ** 2 * sc2 + 2 * sn2 * sc2 * np.log(e["sd_c"] * Pn / (e["sd_n"] * Pc))
    roots = [-c / b] if abs(a) < 1e-12 else list(np.roots([a, b, c]))
    roots = [float(np.real(r)) for r in roots if abs(np.imag(r)) < 1e-9 and min(mn, mc) <= np.real(r) <= max(mn, mc)]
    return roots[0] if roots else None


def posterior_cut(e, p, lo, hi):
    """The y in [lo, hi] where P(c|y) = p (bisection; posterior rising there), or None."""
    f = lambda v: float(posterior_c(np.array([v]), e)[0]) - p
    if f(lo) > 0 or f(hi) < 0:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def em_abstain(e):
    """Handoff B1 step 3 (starting values): no cloud if P_c < 0.002, separation < 2 sd_n, or mu_c < 71.4 - 2 sd_n."""
    if e is None:
        return "EM failed"
    if e["P_c"] < 0.002:
        return "P(c) < 0.002"
    if (e["mu_c"] - e["mu_n"]) / e["sd_n"] < 2:
        return "(mu_c - mu_n)/sd_n < 2"
    if e["mu_c"] < PROD_RISE - 2 * e["sd_n"]:
        return "mu_c < 71.4 - 2 sd_n"
    return None


def em_cuts(e):
    t_l = bayes_cut(e)
    if t_l is None:
        return None, None
    t_h = posterior_cut(e, 0.9, t_l, e["mu_c"] + 6 * e["sd_c"])
    return t_l, t_h


# ------------------------------------------------------------------ masks
def hysteresis(y, valid, t_l, t_h):
    low = valid & (y > t_l)
    lab, n = ndi.label(low, structure=EIGHT)
    if n == 0:
        return np.zeros(y.shape, bool)
    seeded = np.zeros(n + 1, bool)
    seeded[np.unique(lab[valid & (y > t_h)])] = True
    seeded[0] = False
    return seeded[lab]


def blob(m, min_m2=BLOB_M2):
    """C0's minimum blob (4-connected, as sn8_refhaze.cloud_gate)."""
    if not m.any():
        return m
    from sn8_torchgeo import RES
    lab, n = ndi.label(m)
    area = ndi.sum(np.ones(lab.shape), lab, np.arange(1, n + 1)) * RES * RES
    return np.isin(lab, 1 + np.flatnonzero(area >= min_m2))


def icm(y, valid, e, beta, max_sweeps=30, stop_share=1e-4):
    """ICM on eq. 13 (data eq. 14; context -beta per agreeing 8-neighbour), 4-colour sweep order. Returns (mask, info)."""
    import cv2
    yv = np.where(valid, y, e["mu_n"]).astype(np.float64)
    U = []
    for m, s in ((e["mu_n"], e["sd_n"]), (e["mu_c"], e["sd_c"])):
        U.append((0.5 * np.log(2 * np.pi * s * s) + 0.5 * (yv - m) ** 2 / (s * s)).astype(np.float32))
    lab = (U[1] < U[0]) & valid                              # per-pixel Bayes start (min U_data)
    start = lab.copy()
    k = np.ones((3, 3), np.float32)
    k[1, 1] = 0
    rr, cc = np.indices(y.shape)
    colour = (rr % 2) * 2 + (cc % 2)
    n_valid = max(int(valid.sum()), 1)
    sweeps = 0
    for sweeps in range(1, max_sweeps + 1):
        changed = 0
        for col in range(4):
            same1 = cv2.filter2D((lab & valid).astype(np.float32), -1, k, borderType=cv2.BORDER_CONSTANT)
            same0 = cv2.filter2D((~lab & valid).astype(np.float32), -1, k, borderType=cv2.BORDER_CONSTANT)
            e0 = U[0] - beta * same0
            e1 = U[1] - beta * same1
            new = e1 < e0
            sel = (colour == col) & valid
            changed += int((new[sel] != lab[sel]).sum())
            lab = np.where(sel, new, lab)
        if changed < stop_share * n_valid:
            break
    lab = lab & valid
    return lab, {"sweeps": sweeps, "flipped_vs_bayes": int((lab != start).sum())}


# ------------------------------------------------------------------ small image helpers
def erode_min(img, valid, win):
    import cv2
    g = np.where(valid, img, 255).astype(np.float32)
    return cv2.erode(g, np.ones((win, win), np.uint8))


def box(x, win):
    import cv2
    return cv2.blur(x.astype(np.float32), (win, win))


def guided(guide, src, r, eps):
    from sn8_clouds import guided_filter
    return guided_filter(guide.astype(np.float32), src.astype(np.float32), r, eps)
