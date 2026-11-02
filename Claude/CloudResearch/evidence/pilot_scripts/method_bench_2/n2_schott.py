"""Arms N2 / N2b: Schott, Salvaggio & Volchok (1988, RSE 26:1) pseudo-invariant features (handoff
literature_fulltext/schott1988_radiometric_scene_normalization_pseudoinvariant_features_RSE.md sections 1 and 5;
claim_checks_D1 Schott #1-3).

PIFs are man-made: "road surfaces, rooftops, parking lots" (p. 4). Map (eqs. 6-9): m = sd_after / sd_before,
b = mean_after - m mean_before over the PIFs, applied to the whole image. Segmentation check (eq. 10, pp. 7-8): the
histogram-matching transform of the PIF histograms against the linear one over the input range holding the central
90% of PIFs (DC5-DC95), eps_T = sqrt(mean (DC_i - DC'_i)^2); accepted if < 2 digital counts.
Deviations: Schott segments PIFs by a NIR/red ratio AND a SWIR threshold; we have neither, so the PIFs are the published
SN8 footprints used as masks (geometry only; the flood attribute is never read): N2 = buildings + road strips (the
road band of road_band()), N2b = buildings only. Then intersected with C0's clear pixels and not saturated. Per tile;
reference = after date. Abstain (gate opaque) if eps_T >= 2 or < 1,000 PIFs.
N2c (amendment 2026-10-30, DEVIATION): N2 without the eps_T < 2 DC acceptance (check=False).
Known risk (p. 14): the PIFs must be "reasonably dry"; the after date is post-hurricane.
"""
import json

import cv2
import numpy as np
from scipy import ndimage as ndi

import b2_common as B

EPS_T_MAX = 2.0


def footprints(tile_id, p, shape, valid):
    """(buildings, road strips) as boolean masks from the tile's SN8 label file (geometry only)."""
    from sn8 import tile
    from sn8_lines import road_band
    from sn8_roads import _TO_UTM, _road_lines
    from sn8_torchgeo import RES
    x0, y0 = p["x0"], p["y0"]
    with open(tile(tile_id)["label"]) as f:
        feats = json.load(f)["features"]
    bld = np.zeros(shape, np.uint8)
    for feat in feats:
        props, geom = feat.get("properties") or {}, feat.get("geometry")
        if not geom or not props.get("building"):
            continue
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"] if geom["type"] == \
            "MultiPolygon" else []
        for poly in polys:
            rings = []
            for ring in poly:
                lon, lat = np.array(ring)[:, :2].T
                x, y = _TO_UTM.transform(lon, lat)
                rings.append(np.stack([(x - x0) / RES, (y0 - y) / RES], 1).round().astype(np.int32))
            cv2.fillPoly(bld, rings[:1], 1)
            if len(rings) > 1:                                          # holes
                cv2.fillPoly(bld, rings[1:], 0)
    seg, _, _, _ = _road_lines(tile(tile_id)["label"], (x0, y0), shape)
    road = (ndi.distance_transform_edt(seg == 0) * RES <= road_band()) & valid if (seg > 0).any() else \
        np.zeros(shape, bool)
    return bld.astype(bool) & valid, road


def eps_t(xb, ya, gain, off):
    q = np.linspace(0, 1, 256)
    qb, qa = np.quantile(xb, q), np.quantile(ya, q)
    qb, first = np.unique(qb, return_index=True)
    qa = qa[first]
    lo, hi = np.percentile(xb, [5, 95])
    dc = np.arange(np.ceil(lo), np.floor(hi) + 1)
    if len(dc) == 0:
        return float("nan")
    return float(np.sqrt(np.mean((gain * dc + off - np.interp(dc, qb, qa)) ** 2)))


def make_tone_fn(pif_mask, check=True):
    def tone_fn(before, after, clear, valid, b, a):
        m = pif_mask & clear & (b <= B.SAT_DN) & (a <= B.SAT_DN)
        info = {"pif_px": int(m.sum()), "pif_share_of_clear": float(m.sum() / max(clear.sum(), 1))}
        if m.sum() < B.MIN_PIF:
            info["abstain"] = "PIF < 1000"
            return None, info
        xb, ya = b[m].astype(np.float64), a[m].astype(np.float64)
        gain, off = B.meansd_map(xb, ya)
        e = eps_t(xb, ya, gain, off)
        info.update(gain=gain, offset=off, eps_T=e)
        if check and not (e < EPS_T_MAX):
            info["abstain"] = "eps_T >= 2 DC"
            return None, info
        if not gain > 0:
            info["abstain"] = f"gain {gain}"
            return None, info
        return B.linear_tone(gain, off), info
    return tone_fn


def correct(tile_id, p, before, after, valid, roofs_only=False, gate=None, masks=None, check=True):
    from c_common import darkref_variant
    bld, road = footprints(tile_id, p, valid.shape, valid) if masks is None else masks
    pif = bld if roofs_only else (bld | road)
    return darkref_variant(before, after, valid, tone_fn=make_tone_fn(pif, check), gate=gate)
