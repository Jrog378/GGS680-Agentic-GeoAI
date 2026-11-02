"""Arm G1 / G1b: hysteresis cloud gate with Le Hegarat-Mascle & Andre (2009, ISPRS JPRS 64:351) thresholds.

Paper (handoff literature_fulltext/lehegaratmascle2009_markov_random_fields_cloud_shadow_detection_ISPRS.md section 1
steps 2-3; claim_checks_D1 #4; p. 357 read on the page image):
  - the pixel-level MRF's local minimum "corresponds ... to a threshold with hysteresis" (p. 354), 8-connected cliques;
  - "Let z_p be the p-percentile (i.e. P(y_diff <= z_p) = p/100). t_p is the z_p symmetric relative to the distribution
    mean (that is very close to 0). Then t_h = c_h * t_p and t_l = c_l * t_p", p = 0.1, c_h = 1.25, c_l = 0.95 (p. 357).
Deviations (preregistration_method_bench_2.md): the observation field is our two-date dark-channel rise (after - before,
sn8_clouds.dark_channel), not Green - a MIR - b (no MIR); thresholds per tile; the mean is used as printed.
G1 = hysteresis only; G1b = G1 then C0's 2,500 m^2 minimum blob (sn8_refhaze.cloud_gate's 4-connected blobs).
G1c (amendment 2026-10-30, DEVIATION): the field centred on its mean first (the paper's field is ~0-mean by
construction), so t_p = mean - z_p and the cuts are mean + 1.25 t_p and mean + 0.95 t_p.
"""
import numpy as np
from scipy import ndimage as ndi

P, C_H, C_L = 0.1, 1.25, 0.95
EIGHT = np.ones((3, 3), bool)


def thresholds(y, valid, centred=False):
    v = y[valid].astype(np.float64)
    z_p = float(np.percentile(v, P))          # P(y <= z_p) = p / 100
    mean = float(v.mean())
    if centred:                               # G1c: thresholds on y - mean, mapped back
        t_p = mean - z_p
        return {"z_p": z_p, "mean": mean, "median": float(np.median(v)), "t_p": t_p, "centred": True,
                "t_h": mean + C_H * t_p, "t_l": mean + C_L * t_p}
    t_p = 2 * mean - z_p                      # z_p reflected about the mean
    return {"z_p": z_p, "mean": mean, "median": float(np.median(v)), "t_p": t_p, "t_h": C_H * t_p, "t_l": C_L * t_p}


def hysteresis(y, valid, t_l, t_h):
    low = valid & (y > t_l)
    lab, n = ndi.label(low, structure=EIGHT)
    if n == 0:
        return np.zeros(y.shape, bool)
    seeded = np.zeros(n + 1, bool)
    seeded[np.unique(lab[valid & (y > t_h)])] = True
    seeded[0] = False
    return seeded[lab]


def gate(before, after, valid, blob_m2=None, centred=False):
    """(mask, info). blob_m2=None: G1; blob_m2=2500: G1b; centred=True: G1c."""
    from sn8_clouds import dark_channel
    db, da = dark_channel(before, valid), dark_channel(after, valid)
    y = da - db
    th = thresholds(y, valid, centred)
    if not th["t_p"] > 0:                       # degenerate: the reflected percentile is not a positive rise
        return np.zeros(valid.shape, bool), {**th, "abstain": "t_p <= 0", "gate_px": 0}
    m = hysteresis(y, valid, th["t_l"], th["t_h"])
    if blob_m2 is not None and m.any():
        from sn8_torchgeo import RES
        lab, n = ndi.label(m)                   # 4-connected, as sn8_refhaze.cloud_gate
        area = ndi.sum(np.ones(lab.shape), lab, np.arange(1, n + 1)) * RES * RES
        m = np.isin(lab, 1 + np.flatnonzero(area >= blob_m2))
    th["gate_px"] = int(m.sum())
    th["gate_share"] = float(m[valid].mean()) if valid.any() else float("nan")
    return m, th
