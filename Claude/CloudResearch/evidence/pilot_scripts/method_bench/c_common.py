"""Correction arms: C0 (the current two-date fit) re-implemented with hooks, so every arm shares its arithmetic.

darkref_variant() is sn8_refhaze.dark_reference_dehaze line for line (checked equal at the defaults by run_corr.py
before anything is scored), with four hooks: the gate's minimum blob (C4), a tone-curve function (C2), a gamma for the
arithmetic (C5a) and the fade width (C3a). The library is imported, never edited.
"""
import numpy as np
from scipy import ndimage as ndi

GATE_MARGIN_PX = 40               # sn8_refhaze.DARKREF_GATE_MARGIN_PX (20 m)
CLEAR_MARGIN_PX = 20              # sn8_refhaze.DARKREF_CLEAR_MARGIN_PX (10 m)
T_MIN = 0.2
MIN_CLEAR = 1000


def cloud_gate(before, after, valid, min_m2=2500.0):
    """sn8_refhaze.cloud_gate with the minimum blob as a parameter."""
    from sn8_clouds import cloud_thresholds, dark_channel
    from sn8_torchgeo import RES
    db, da = dark_channel(before, valid), dark_channel(after, valid)
    rise = valid & (da - db > cloud_thresholds()["dark rise"])
    lab, n = ndi.label(rise)
    if n == 0:
        return np.zeros(valid.shape, bool), db, da
    area = ndi.sum(np.ones(lab.shape), lab, np.arange(1, n + 1)) * RES * RES
    return np.isin(lab, 1 + np.flatnonzero(area >= min_m2)), db, da


def _lin(x, gamma):
    return x if gamma == 1.0 else (255.0 * (np.clip(x, 0, 255) / 255.0) ** gamma).astype(np.float32)


def _unlin(x, gamma):
    return x if gamma == 1.0 else (255.0 * (np.clip(x, 0, 255) / 255.0) ** (1.0 / gamma)).astype(np.float32)


def darkref_variant(before, after, valid, min_m2=2500.0, tone_fn=None, gamma=1.0, fade_px=GATE_MARGIN_PX, gate=None):
    """dark_reference_dehaze with hooks. tone_fn(before, after, clear, valid) -> (tone, info) or (None, info) to abstain.
    Returns corrected (no-data 0), t, gate, opaque, airlight, info."""
    from sn8_clouds import AIRLIGHT_SHARE, dark_channel
    from sn8_refhaze import tone_curve
    if gate is None:
        gate, _, _ = cloud_gate(before, after, valid, min_m2)        # the gate is found on display values
    clear = valid & ~ndi.binary_dilation(gate, iterations=CLEAR_MARGIN_PX)
    info = {}
    ones = np.where(valid, 1.0, np.nan)
    if clear.sum() < MIN_CLEAR:
        return {"corrected": np.where(valid, after, 0).astype(np.float32), "t": ones, "gate": gate,
                "opaque": gate & valid, "airlight": float("nan"), "info": {"abstain": "clear < 1000"}}
    b, a = _lin(before, gamma), _lin(after, gamma)
    db, da = dark_channel(b, valid), dark_channel(a, valid)
    if tone_fn is None:
        tone, _, _ = tone_curve(b, a, clear)
    else:
        tone, info = tone_fn(before, after, clear, valid, b, a)
        if tone is None:                                             # abstain: the whole gate cannot be assessed
            return {"corrected": np.where(valid, after, 0).astype(np.float32), "t": ones, "gate": gate,
                    "opaque": gate & valid, "airlight": float("nan"), "info": info}
    haziest = valid & (da >= np.quantile(da[valid], 1 - AIRLIGHT_SHARE))
    airlight = float(a[haziest].max())
    t = np.clip((airlight - da) / np.maximum(airlight - tone(db), 1), 0, 1)
    fade = np.clip(1 - ndi.distance_transform_edt(~gate) / fade_px, 0, 1) if gate.any() else np.zeros(gate.shape)
    t = (1 - fade * (1 - t)).astype(np.float32)
    t = np.where(valid, t, 1)
    opaque = valid & (t < T_MIN)
    corrected = np.where(opaque, a, (a - airlight) / np.maximum(t, T_MIN) + airlight)
    if gamma != 1.0:      # back to display values; untouched pixels (t = 1) stay bit-identical to the input
        corrected = np.where(t >= 1, after, _unlin(np.clip(corrected, 0, 255), gamma))
    return {"corrected": np.where(valid, np.clip(corrected, 1, 255), 0).astype(np.float32),
            "t": np.where(valid, t, np.nan), "gate": gate, "opaque": opaque, "airlight": airlight, "info": info}
