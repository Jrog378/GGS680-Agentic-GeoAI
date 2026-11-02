"""The after-date half of production's 93 non-DINOv2 road features, for a corrected after image.

The before-date columns do not depend on the correction (they equal the raw table's), and the change columns are
after - before, so only the after date is recomputed. This file repeats, for the after date only, exactly what
sn8_roads.line_features, sn8_glcm.lines_glcm and sn8_texture.lines_texture do (their building blocks are imported:
canny, edge_input, hough_lines, ridge, _road_means, region_texture, quantize, cooccurrence, haralick). run_corr.py
checks the result against the library functions on real tiles before it is used.
"""
import cv2
import numpy as np
from scipy import ndimage as ndi
from skimage import exposure


def _after_grey_matched(p, valid):
    grey_b = p["before_grey"] / 255
    grey_a = p["after_grey"] / 255
    grey_a[valid] = exposure.match_histograms(grey_a[valid], grey_b[valid])
    return grey_a


def after_columns(tile_id, p, valid, seg, seg_angle, seg_road, roads, band_m):
    """{column: (n,)} for every *_after column of FEATURES, GLCM_FEATURES and TEXTURE_FEATURES, plus centre_px."""
    from sn8_glcm import cooccurrence, haralick, quantize
    from sn8_lines import canny, edge_input, hough_lines, ridge
    from sn8_roads import PARALLEL_DEG, RING_M, TEXTURE_WIN, _road_means
    from sn8_texture import region_texture
    from sn8_torchgeo import RES
    n = len(roads) - 1
    dist, (ni, nj) = ndi.distance_transform_edt(seg == 0, return_indices=True)
    dist = dist * RES
    owner = seg_road[seg[ni, nj]]
    near_angle = seg_angle[seg[ni, nj]]
    strip = (dist <= band_m) & valid
    ring = (dist > band_m) & (dist <= band_m + RING_M) & valid
    centre = (seg > 0) & valid
    out = {}
    g = _after_grey_matched(p, valid)
    # sn8_roads.line_features, after date
    edges = canny(edge_input(g, valid), valid)
    mean = cv2.blur(g, (TEXTURE_WIN, TEXTURE_WIN))
    texture = np.sqrt(np.maximum(cv2.blur(g * g, (TEXTURE_WIN, TEXTURE_WIN)) - mean * mean, 0))
    on_road = np.zeros(valid.shape, bool)
    for (x0, y0), (x1, y1) in hough_lines(edges):
        k = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        c = np.round(np.linspace(x0, x1, k)).astype(int)
        r = np.round(np.linspace(y0, y1, k)).astype(int)
        a = np.arctan2(y1 - y0, x1 - x0) % np.pi
        d = np.abs(a - near_angle[r, c])
        keep = strip[r, c] & (np.minimum(d, np.pi - d) <= np.radians(PARALLEL_DEG))
        on_road[r[keep], c[keep]] = True
    covered = ndi.distance_transform_edt(~on_road) * RES <= band_m if on_road.any() else np.zeros(valid.shape, bool)
    out["edge_after"] = _road_means(edges, owner, strip, n)
    out["grey_after"] = _road_means(g, owner, strip, n)
    out["contrast_after"] = out["grey_after"] - _road_means(g, owner, ring, n)
    out["texture_after"] = _road_means(texture, owner, strip, n)
    out["ridge_after"] = _road_means(ridge(g, valid), owner, strip, n)
    out["hough_after"] = _road_means(covered, owner, centre, n)
    # sn8_glcm.lines_glcm, after date (its own strip: owner within the band and valid)
    gstrip = np.where(strip, owner, 0)
    for prop, v in haralick(cooccurrence(quantize(p["after_grey"], valid), gstrip, n)).items():
        out[f"glcm_{prop}_after"] = v
    # sn8_texture.lines_texture, after date
    for m, v in region_texture(g.astype(np.float32), valid, gstrip, n).items():
        out[f"{m}_after"] = v
    out["_centre_px"] = np.bincount(np.where(centre, owner, 0).ravel(), minlength=n + 1)[1:]
    return out


def after_rows(tile_id, p, valid, band_m):
    """One dict per road (MIN_ROAD_PX rule, feature_table order): tile_id, road_id and every *_after column."""
    from sn8 import tile
    from sn8_roads import MIN_ROAD_PX, _road_lines
    seg, seg_angle, seg_road, roads = _road_lines(tile(tile_id)["label"], (p["x0"], p["y0"]), valid.shape)
    if len(roads) == 1:
        return []
    out = after_columns(tile_id, p, valid, seg, seg_angle, seg_road, roads, band_m)
    cp = out.pop("_centre_px")
    return [{"tile_id": tile_id, "road_id": roads[k + 1]["road_id"], **{c: float(v[k]) for c, v in out.items()}}
            for k in range(len(roads) - 1) if cp[k] >= MIN_ROAD_PX]
