"""Arm C5 (OUR OWN TESTS; no full-text support for applying them to our data):
C5a gamma-linearisation: before and after mapped to 255 (x / 255)^gamma, gamma in {1.8, 2.2}; C0's arithmetic (tone,
     airlight, t, inversion) in that space; mapped back; the gate is unchanged (found on display values). Ju et al. 2018
     treat gamma as the dehazing operator, not as linearising a stretched input (claim_checks_C Ju 2018 #2).
C5b band-linked RGB: C0's t (after its fade) taken as the green band's; t_i = t_g^((lambda_g / lambda_i)^1) with
     lambda = 0.48, 0.545, 0.66 um (Ma et al. 2022 band link, pp. 14-15, gamma = 1 as their training; claim_checks_C
     TIIN #6); airlight per band = the band's maximum over C0's haziest pixels; each band corrected with C0's
     arithmetic; the grey copy changed by BT.601 of the RGB correction (so it is unchanged outside the gate).
"""
import numpy as np

GAMMAS = (1.8, 2.2)
LAMBDA = (0.48, 0.545, 0.66)       # blue, green, red (um), stored here in R, G, B order below
W601 = (0.299, 0.587, 0.114)


def correct_gamma(before, after, valid, gamma):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, gamma=gamma)


def correct_band(before, after, valid, after_rgb, c0):
    from sn8_clouds import AIRLIGHT_SHARE, dark_channel
    if not np.isfinite(c0["airlight"]):
        return c0
    da = dark_channel(after, valid)
    haziest = valid & (da >= np.quantile(da[valid], 1 - AIRLIGHT_SHARE))
    t_g = np.nan_to_num(c0["t"], nan=1.0)
    opaque = c0["opaque"]
    lam = {0: LAMBDA[2], 1: LAMBDA[1], 2: LAMBDA[0]}     # R, G, B
    rgb = after_rgb.astype(np.float32)
    out = np.empty_like(rgb)
    for i in range(3):
        A = float(rgb[..., i][haziest].max())
        t_i = t_g ** (LAMBDA[1] / lam[i])
        out[..., i] = np.where(opaque, rgb[..., i], (rgb[..., i] - A) / np.maximum(t_i, 0.2) + A)
    out = np.clip(out, 0, 255)
    dgrey = sum(w * (out[..., i] - rgb[..., i]) for i, w in enumerate(W601))
    corr = np.where(valid, np.clip(after + dgrey, 1, 255), 0).astype(np.float32)
    return {"corrected": corr, "t": c0["t"], "opaque": opaque, "gate": c0["gate"], "airlight": c0["airlight"],
            "info": {}}
