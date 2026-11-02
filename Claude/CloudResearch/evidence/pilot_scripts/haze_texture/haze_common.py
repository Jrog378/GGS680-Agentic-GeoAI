"""Sub-threshold haze and texture (evidence/20): continuous, threshold-free haze scores per road strip and per tile.

Justin (2026-10-29): "I think the misty clouds are messing with the texture of our imagery and isnt being detected by
our cloud detector since it doesnt look like a cloud, however this is clearly some form of noise in our image that can
throw off results especially texture results".

Development tiles only (train + val, through sn8_clouds._tile, which refuses held-out splits). Nothing in the library
is edited; its functions are imported. Scores, each computed on the AFTER image and, as a null reference, the same way
on the BEFORE image (the before images of the touched tiles are cloud-free: none has > 3% bright, smooth pixels):

  rise     dark channel of the after image minus the tone-matched dark channel of the before image
           (sn8_clouds.dark_channel, sn8_refhaze.tone_curve on the pixels no mask flags, 10 m margin), minus its
           median on the tile's no-mask pixels (so the two dates' versions are comparable). No gate.
           Null: fall = dark before minus the tone-matched dark after.
  atten    contrast attenuation: -log((std_after + 1) / (std_before + 1)) of the local standard deviation in an
           11 px (5.5 m) window, minus the tile's median of the same on pixels no mask flags. > 0 = the after image
           lost local contrast relative to the tile's typical change. (Null: its mirror, -atten.)
  hot      Haze Optimized Transform (Zhang, Guindon & Cihlar 2002, RSE 82: 173-187) on the ORIGINAL 3-band RGB
           (8-bit display product, not reflectance): clear line red = k blue + b fitted by least squares on the tile's
           least-hazy pixels (no mask, lowest quarter of `rise`, not saturated or near black), HOT = B sin(theta) -
           R cos(theta), theta = atan(k), minus its median on the fitting pixels. Null: HOT of the before image (its
           own line, its own least-hazy pixels by `fall`).
  spot     the HRC_WHU-trained spotter's cloud probability (sn8_cloudspot.CloudSpotter, LIBRARY_ARMS["classical"]:
           the chosen "classical + DINOv2 - dark" arm needs DINOv2 tokens of every SN8 tile, which are not cached and
           would need the GPU, so the CPU-only classical arm stands in). Null: the same on the before image.
Per road strip (sn8_cloudsym.road_strips, the strip of sn8_roads): median, 90th percentile and mean.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("MPLBACKEND", "Agg")
import sys
from pathlib import Path

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
HERE = Path(__file__).resolve().parent
SCV = HERE.parent / "spatial_cv"
FIG = HERE.parents[2] / "figures" / "haze_texture"
for _p in (LIB, str(HERE), str(SCV)):
    if _p not in sys.path:
        sys.path.append(_p)

import cv2
import numpy as np
from scipy import ndimage as ndi

STD_WIN = 11                  # local standard deviation window (5.5 m), as sn8_refhaze.local_contrast
CLEAR_MARGIN_PX = 20          # as sn8_refhaze.DARKREF_CLEAR_MARGIN_PX (10 m)
HOT_QUANTILE = 0.25           # least-hazy pixels: the lowest quarter of the dark-channel rise among no-mask pixels
HOT_SAMPLE = 50_000
SCORES = ["rise", "fall", "atten", "hot_post", "hot_pre", "spot_post", "spot_pre"]


def local_std(g, win=STD_WIN):
    m = cv2.blur(g, (win, win))
    return np.sqrt(np.maximum(cv2.blur(g * g, (win, win)) - m * m, 0))


def hot_map(rgb, fit_px, seed=662):
    """HOT of an RGB uint8 image with the clear line fitted on `fit_px` (bool). Returns (map, slope, n fit pixels)."""
    r, b = rgb[..., 0].astype(np.float32), rgb[..., 2].astype(np.float32)
    ok = fit_px & (rgb.max(-1) < 250) & (rgb.min(-1) > 5)
    idx = np.flatnonzero(ok)
    if len(idx) < 500:
        return np.full(r.shape, np.nan, np.float32), np.nan, len(idx)
    idx = np.random.default_rng(seed).choice(idx, min(HOT_SAMPLE, len(idx)), replace=False)
    k, c = np.polyfit(b.ravel()[idx], r.ravel()[idx], 1)
    th = np.arctan(k)
    h = b * np.sin(th) - r * np.cos(th)
    h -= np.median(h.ravel()[idx])
    return h.astype(np.float32), float(k), len(idx)


def tile_maps(tile_id, spotter=None):
    """Every score map on one development tile, plus the masks, the strip and the images."""
    from sn8_clouds import _maps, _tile
    from sn8_cloudsym import road_strips
    from sn8_refhaze import tone_curve
    p, before, after, valid = _tile(tile_id)
    m = _maps(p, valid)
    da, db = m["dark_after"], m["dark_before"]
    anymask = (m["masks"]["bright"] | m["masks"]["dark"] | m["masks"]["dark rise"]) & valid
    nomask = valid & ~anymask
    clear = valid & ~ndi.binary_dilation(anymask, iterations=CLEAR_MARGIN_PX) if anymask.any() else valid.copy()
    if clear.sum() < 1000:
        clear = nomask if nomask.sum() >= 1000 else valid
    f_ab, _, _ = tone_curve(before, after, clear)
    f_ba, _, _ = tone_curve(after, before, clear)
    rise = da - f_ab(db)
    fall = db - f_ba(da)
    ref = nomask if nomask.any() else valid       # centred on the tile's no-mask pixels, so rise and fall compare
    rise = np.where(valid, rise - np.median(rise[ref]), np.nan).astype(np.float32)
    fall = np.where(valid, fall - np.median(fall[ref]), np.nan).astype(np.float32)
    lr = np.log((local_std(after) + 1) / (local_std(before) + 1))
    base = np.median(lr[nomask]) if nomask.any() else np.median(lr[valid])
    atten = np.where(valid, -(lr - base), np.nan).astype(np.float32)
    q_a = np.quantile(rise[clear], HOT_QUANTILE)
    q_b = np.quantile(fall[clear], HOT_QUANTILE)
    hot_post, k_post, n_post = hot_map(p["after_rgb"], clear & (rise <= q_a))
    hot_pre, k_pre, n_pre = hot_map(p["before_rgb"], clear & (fall <= q_b))
    strip, centre, roads = road_strips(tile_id, p, valid)
    out = {"p": p, "before": before, "after": after, "valid": valid, "masks": m["masks"], "anymask": anymask,
           "rise": rise, "fall": fall, "atten": atten, "hot_post": np.where(valid, hot_post, np.nan),
           "hot_pre": np.where(valid, hot_pre, np.nan), "strip": strip, "centre": centre, "roads": roads,
           "hot_slope_post": k_post, "hot_slope_pre": k_pre, "hot_fit_px_post": n_post, "hot_fit_px_pre": n_pre,
           "raw_rise": np.where(valid, da - db, np.nan)}
    if spotter is not None:
        need = (strip > 0) | _grid(valid.shape)
        out["spot_post"] = spotter.proba(after, valid, need)
        out["spot_pre"] = spotter.proba(before, valid, need)
    return out


def _grid(shape):
    from sn8_cloudspot import grid_pixels
    g = np.zeros(shape, bool)
    r, c = grid_pixels(shape)
    g[r, c] = True
    return g


def tile_rows(tile_id, spotter):
    """One row per road (sn8_roads.feature_table order: roads with >= MIN_ROAD_PX valid centreline pixels) with the
    strip median / p90 / mean of every score, and one tile row."""
    from sn8_roads import MIN_ROAD_PX
    t = tile_maps(tile_id, spotter)
    strip, centre, roads, valid = t["strip"], t["centre"], t["roads"], t["valid"]
    n = len(roads) - 1
    flat = strip.ravel()
    order = np.argsort(flat, kind="stable")
    bounds = np.searchsorted(flat[order], np.arange(n + 2))
    rows = []
    for k in range(n):
        if centre[k] < MIN_ROAD_PX:
            continue
        px = order[bounds[k + 1]:bounds[k + 2]]
        row = {"tile_id": tile_id, "road_id": roads[k + 1]["road_id"], "strip_px": len(px)}
        for s in SCORES:
            v = t[s].ravel()[px]
            v = v[np.isfinite(v)]
            row[f"{s}_med"] = float(np.median(v)) if len(v) else np.nan
            row[f"{s}_p90"] = float(np.quantile(v, 0.9)) if len(v) else np.nan
            row[f"{s}_mean"] = float(v.mean()) if len(v) else np.nan
        rows.append(row)
    g = _grid(valid.shape) & valid
    tile_row = {"tile_id": tile_id, "valid_px": int(valid.sum()),
                "raw_rise_med": float(np.nanmedian(t["raw_rise"][valid])),
                "rise_p90": float(np.nanquantile(t["rise"][valid], 0.9)),
                "atten_med": float(np.nanmedian(t["atten"][valid])),
                "hot_post_p90": float(np.nanquantile(t["hot_post"][valid], 0.9)) if np.isfinite(t["hot_slope_post"]) else np.nan,
                "hot_pre_p90": float(np.nanquantile(t["hot_pre"][valid], 0.9)) if np.isfinite(t["hot_slope_pre"]) else np.nan,
                "spot_post_mean": float(np.nanmean(t["spot_post"][g])), "spot_pre_mean": float(np.nanmean(t["spot_pre"][g])),
                "hot_slope_post": t["hot_slope_post"], "hot_slope_pre": t["hot_slope_pre"],
                **{f"mask_{k.replace(' ', '_')}": float(v[valid].mean()) for k, v in t["masks"].items()}}
    return rows, tile_row


SPOTTER_PKL = HERE / "spotter_classical.joblib"


def load_spotter():
    import joblib
    if not SPOTTER_PKL.exists():
        from sn8_cloudspot import LIBRARY_ARMS, CloudSpotter
        s = CloudSpotter(LIBRARY_ARMS["classical"]).fit()
        joblib.dump(s, SPOTTER_PKL)
    s = joblib.load(SPOTTER_PKL)
    s.model_.set_params(n_jobs=1)
    return s
