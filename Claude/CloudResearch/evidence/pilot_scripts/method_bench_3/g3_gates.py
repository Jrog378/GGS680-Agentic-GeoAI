"""Phase G gate arms (preregistration_method_bench_3.md, "G-gate family").

T1 / T1b  Otsu (1979) on the clipped grey rise, integer levels, eta* >= 0.65 accepted (the 0.65 is OURS, not Otsu's),
          otherwise the 99th percentile on production-clear pixels (otsu1979 handoff section 5, arm T1).
T1d       integer-level Otsu on the pooled dark rise: a check of production's 71.36 (arm only if it moves > 5 DN).
B1 / B1p  Bruzzone & Fernandez Prieto (2000) two-Gaussian EM on the dark rise, Bayes cut (eq. 7) as t_l, P(c|y) = 0.9 as
          t_h, 8-connected hysteresis + C0's 2,500 m^2 blob; per tile (B1) or pooled training fit (B1p).
B2-beta   the same EM estimates, ICM-MRF labels (eqs. 11-14), beta 1.3 / 1.6 / 1.8.
U1 cues   Zhang, Peng & Huang (2018): per road strip, cue 1 = share of pixels "changed" by EM on |after - tone(before)|,
          cue 2 = G-statistic of the before/after strip histograms (L = 32), per pixel. The FCM and Dempster fusion are
          done over all strips in the runner (u1_fuse).
"""
import json

import numpy as np
from scipy import ndimage as ndi

import b3_common as K

TH_FILE = K.BIG / "g_thresholds.json"
STEP = 16
GAIN_CLIP = (0.5, 2.0)
ETA_MIN = 0.65                     # OURS (from the SAR flood-thresholding work cited by the Tiampo handoff)
BETAS = (1.3, 1.6, 1.8)
EM_SUB = 4
U1_BINS = 32
U1_T = 0.75


def dark_rise(before, after, valid):
    from sn8_clouds import dark_channel
    return dark_channel(after, valid) - dark_channel(before, valid)


def grey_rise(before, after, valid):
    """after - (g before + o), mean/SD map over valid pixels, g clipped to [0.5, 2] (offset refitted on the means)."""
    xb, xa = before[valid].astype(np.float64), after[valid].astype(np.float64)
    g, o = K.B.meansd_map(xb, xa)
    clipped = not (GAIN_CLIP[0] <= g <= GAIN_CLIP[1])
    if clipped:
        g = float(np.clip(g, *GAIN_CLIP))
        o = float(xa.mean() - g * xb.mean())
    r = np.where(valid, np.clip(after - (g * before + o), -255, 255), 0).astype(np.float32)
    return r, {"gain": g, "offset": o, "gain_clipped": clipped}


def thresholds(t0=None):
    """Pooled training-tile fits (cached): T1's cut, T1d's check, B1p's EM and cuts."""
    if TH_FILE.exists():
        return json.loads(TH_FILE.read_text())
    from sn8_clouds import _maps, _tile, cloud_thresholds
    assert abs(cloud_thresholds()["dark rise"] - K.PROD_RISE) < 0.01
    tiles = K.train_tiles()
    gr, gr_clear, dr = [], [], []
    clipped = 0
    for i, tid in enumerate(tiles):
        K.wait_for_memory(t0)
        p, b, a, v = _tile(tid)
        r, info = grey_rise(b, a, v)
        clipped += info["gain_clipped"]
        rise_m = _maps(p, v)["masks"]["dark rise"]
        y = dark_rise(b, a, v)
        gr.append(r[v][::STEP])
        gr_clear.append(r[v & ~rise_m][::STEP])
        dr.append(y[v][::STEP])
        if t0 is not None and (i + 1) % 30 == 0:
            K.log(t0, f"thresholds: {i + 1}/{len(tiles)} training tiles")
    gr, gr_clear, dr = map(np.concatenate, (gr, gr_clear, dr))
    o = K.otsu_int(gr)
    p99 = float(np.percentile(gr_clear, 99))
    t1 = {**o, "p99_clear": p99, "accepted": o["eta_star"] >= ETA_MIN,
          "cut": o["k_star"] if o["eta_star"] >= ETA_MIN else p99, "tiles_gain_clipped": int(clipped)}
    od = K.otsu_int(dr)
    t1d = {**od, "prod_cut": K.PROD_RISE, "candidate": abs(od["k_star"] - K.PROD_RISE) > 5}
    e = K.em2(dr)
    ab = K.em_abstain(e)
    t_l, t_h = K.em_cuts(e) if ab is None else (None, None)
    b1p = {"em": e, "abstain": ab, "t_l": t_l, "t_h": t_h}
    out = {"tiles": len(tiles), "step": STEP, "T1": t1, "T1d": t1d, "B1p": b1p}
    K.BIG.mkdir(parents=True, exist_ok=True)
    TH_FILE.write_text(json.dumps(K.M1.plain(out), indent=1))
    return out


def b1_fit(y, valid):
    e = K.em2(y[valid][::EM_SUB])
    ab = K.em_abstain(e)
    info = {"em": e, "abstain": ab}
    if ab is None:
        t_l, t_h = K.em_cuts(e)
        if t_l is None or t_h is None:
            info["abstain"] = "no Bayes root"
        info.update(t_l=t_l, t_h=t_h)
    return info


def masks(p, before, after, valid, TH):
    """{name: bool mask} for the production dark rise and every Phase G gate arm, plus info."""
    from sn8_clouds import _maps
    out = {"rise": _maps(p, valid)["masks"]["dark rise"]}
    info = {}
    r, info["T1"] = grey_rise(before, after, valid)
    out["T1"] = valid & (r > TH["T1"]["cut"])
    out["T1b"] = K.blob(out["T1"])
    y = dark_rise(before, after, valid)
    if TH["T1d"]["candidate"]:
        out["T1d"] = valid & (y > TH["T1d"]["k_star"])
    fit = b1_fit(y, valid)
    info["B1"] = fit
    if fit["abstain"] is None:
        out["B1"] = K.blob(K.hysteresis(y, valid, fit["t_l"], fit["t_h"]))
        for beta in BETAS:
            m, info[f"B2-{beta}"] = K.icm(y, valid, fit["em"], beta)
            out[f"B2-{beta}"] = m
    else:
        out["B1"] = np.zeros(valid.shape, bool)
        for beta in BETAS:
            out[f"B2-{beta}"] = np.zeros(valid.shape, bool)
    bp = TH["B1p"]
    out["B1p"] = K.blob(K.hysteresis(y, valid, bp["t_l"], bp["t_h"])) if bp["abstain"] is None else \
        np.zeros(valid.shape, bool)
    for k, m in out.items():
        info.setdefault("share", {})[k] = float(m[valid].mean())
    return out, info


# ------------------------------------------------------------------ U1 (Zhang, Peng & Huang 2018)
def g_stat(h1, h2):
    """G-test statistic of the 2 x L contingency table, divided by the pixel count (deviation: strips differ in size)."""
    O = np.stack([h1, h2]).astype(np.float64)
    n = O.sum()
    if n == 0:
        return np.nan
    E = O.sum(1, keepdims=True) * O.sum(0, keepdims=True) / n
    with np.errstate(divide="ignore", invalid="ignore"):
        g = 2 * np.nansum(np.where(O > 0, O * np.log(O / E), 0.0))
    return float(g / n)


def u1_cues(tid, p, before, after, valid, strip, roads, n, centre_px):
    """Per road (road_shares order): m1c (share of the strip changed by cue 1) and Gn (cue 2)."""
    from sn8_cloudspot import road_shares
    from sn8_refhaze import tone_curve
    from c_common import cloud_gate
    gate, _, _ = cloud_gate(before, after, valid)
    clear = valid & ~ndi.binary_dilation(gate, iterations=20)
    if clear.sum() < 1000:
        clear = valid
    tone, _, _ = tone_curve(before, after, clear)
    bt = np.where(valid, tone(before), 0).astype(np.float32)
    d = np.abs(after - bt)
    e = K.em2(d[valid][::EM_SUB])
    changed = (K.posterior_c(d, e) >= 0.5) & valid if e is not None else np.zeros(valid.shape, bool)
    rows = road_shares(tid, strip, roads, n, centre_px, {"u1_m1c": changed})
    edges = np.linspace(0, 256, U1_BINS + 1)
    from sn8_roads import MIN_ROAD_PX
    keep = [k for k in range(n) if centre_px[k] >= MIN_ROAD_PX]
    s = strip
    for row, k in zip(rows, keep):
        m = (s == k + 1)
        h1 = np.histogram(bt[m], edges)[0]
        h2 = np.histogram(after[m], edges)[0]
        row["u1_G"] = g_stat(h1, h2)
    return rows, {"em": e}


def fcm2(x, m=2.0, iters=200, tol=1e-9):
    """1-D fuzzy c-means, 2 clusters; returns membership of the higher-centre cluster and the centres."""
    x = np.asarray(x, np.float64)
    c = np.array([np.nanmin(x), np.nanmax(x)])
    u = None
    for _ in range(iters):
        d = np.abs(x[:, None] - c[None]) + 1e-12
        u = 1.0 / ((d[:, :, None] / d[:, None, :]) ** (2 / (m - 1))).sum(2)
        c_new = (u ** m * x[:, None]).sum(0) / (u ** m).sum(0)
        if np.abs(c_new - c).max() < tol:
            c = c_new
            break
        c = c_new
    hi = int(np.argmax(c))
    return u[:, hi], c


def u1_fuse(m1c, G):
    """Dempster's rule (singletons) of m1 = (m1c, 1 - m1c) and m2 = FCM(G); certain if max(P_c, P_u) >= 0.75."""
    g = np.where(np.isfinite(G), G, np.nanmedian(G))
    p2c, centres = fcm2(g)
    m1c = np.clip(m1c, 0, 1)
    num = m1c * p2c
    den = num + (1 - m1c) * (1 - p2c)
    pc = np.where(den > 0, num / np.maximum(den, 1e-12), 0.5)      # total conflict -> uncertain
    certain = (pc >= U1_T) | ((1 - pc) >= U1_T)
    return pc, certain, centres
