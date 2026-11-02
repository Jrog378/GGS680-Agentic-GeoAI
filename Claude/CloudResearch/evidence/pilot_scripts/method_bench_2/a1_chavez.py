"""Arm A1-k: Chavez (1988, RSE 24:459) relative scattering model (power law lambda^-k) linking the airlight across
bands (handoff literature_fulltext/chavez1988_improved_dark_object_subtraction_RSE.md sections 1 and 5, arm 3-iv;
claim_checks_D1 Chavez #2, #4, #6).

Chavez predicts each band's haze from one starting band with factor_i = (lambda_i / lambda_start)^-k (Table 2), k from
0 ("complete scattering (e.g., complete cloud cover)") to 4 (p. 466); real clear atmospheres ~ k = 2 to 0.7.
Ours (the handoff's arm 3-iv): C0's gate, tone, t and fade unchanged; A_blue = the after blue maximum over C0's haziest
pixels (the 0.1% highest after dark channel, C0's rule); A_i = A_blue (lambda_i / lambda_blue)^-k; each band corrected
with C0's arithmetic (a_i - A_i) / t + A_i (opaque left as is); the grey copy changes by BT.601 of the RGB change (as
bench 1's C5b), so it is unchanged where t = 1.
Deviations: Chavez subtracts one constant per band over the whole image; equal band gains assumed (unknown on display
RGB; DN ordering can invert, p. 475); k swept over K instead of chosen from TM1 starting-haze classes (Table 5).
"""
import numpy as np

import b2_common as B

K = (0.0, 0.5, 0.7, 1.0, 2.0)
LAM_RGB = (B.LAMBDA["red"], B.LAMBDA["green"], B.LAMBDA["blue"])


def airlights(A_blue, k):
    return [A_blue * (lam / B.LAMBDA["blue"]) ** (-k) for lam in LAM_RGB]      # R, G, B


def correct(before, after, valid, after_rgb, c0, k):
    """c0 = C0's output dict (dark_reference_dehaze or darkref_variant). Returns an output dict like C0's."""
    from sn8_clouds import AIRLIGHT_SHARE, dark_channel
    if not np.isfinite(c0["airlight"]):
        return {**c0, "info": {"abstain": "C0 abstained"}}
    da = dark_channel(after, valid)
    haziest = valid & (da >= np.quantile(da[valid], 1 - AIRLIGHT_SHARE))
    rgb = after_rgb.astype(np.float32)
    A_b = float(rgb[..., 2][haziest].max())
    A = airlights(A_b, k)
    t = np.nan_to_num(c0["t"], nan=1.0)
    opaque = c0["opaque"]
    out = np.empty_like(rgb)
    for i in range(3):
        out[..., i] = np.where(opaque, rgb[..., i], (rgb[..., i] - A[i]) / np.maximum(t, 0.2) + A[i])
    out = np.clip(out, 0, 255)
    dgrey = sum(w * (out[..., i] - rgb[..., i]) for i, w in enumerate(B.W601))
    corr = np.where(valid, np.clip(after + dgrey, 1, 255), 0).astype(np.float32)
    return {"corrected": corr, "corrected_rgb": out, "t": c0["t"], "opaque": opaque, "gate": c0["gate"],
            "airlight": c0["airlight"], "info": {"k": k, "A_rgb": A, "A_grey_C0": c0["airlight"]}}
