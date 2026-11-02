"""Shared setup for the pre-registered Ida clear-view test (outputs/preregistration_ida_clear_view.md, incl. Revision 1).

Development tiles only (Louisiana-East train + val, 226). Library modules in ProjectBranch/ClaudeFunctions are imported,
never edited; held-out tiles are never read (sn8_clouds._tile refuses them; allow_held_out is never passed).
NOAA NGS emergency-response aerial photos of Hurricane Ida (public domain) are read from the external drive.
CPU only while the DINOv3 GPU job runs (the DINOv2 backbone is loaded with MPS hidden; see cpu_backbone()).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.environ.setdefault("MPLBACKEND", "Agg")
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
CR = PILOT.parents[1]                                   # CloudResearch/
FIG = CR / "figures" / "ida_clear_view"
CACHE = HERE / "cache"                                  # small per-tile tables
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/ida/ida_clear_view_cache")   # per-tile arrays, tokens (internal disk is nearly full)
for _p in (LIB, str(HERE), str(PILOT / "spatial_cv")):
    if _p not in sys.path:
        sys.path.append(_p)

NOAA_DIR = Path("/Volumes/USB2025/GeoAI-Descriptions/data/ida/noaa_eri_ida2021")
CHECK = PILOT / "ida_noaa_check"
GREY_INDEX = Path("/Users/jusrogers/Masters/GGS662/ProjectBranch/Images/SN8_Louisiana-East_Ida2021_greyscale/tiles.csv")
FLIGHTS = ["20210830a", "20210830b", "20210831a", "20210902a"]   # date order (ties go to the earlier)
FLIGHT_DATE = {"20210830a": "2021-08-30", "20210830b": "2021-08-30", "20210831a": "2021-08-31", "20210902a": "2021-09-02"}
EPSG = 32615
RES = 0.5
MIN_COVER = 0.5                    # plan: at least 50% of the tile's valid post pixels covered by valid NOAA pixels
GREY_W = (0.299, 0.587, 0.114)     # the SpaceNet greyscale copy's weights (sn8_grey)
SEED = 662


def dev_tiles():
    t = pd.read_csv(GREY_INDEX)
    d = t[t.split.isin(["train", "val"])].reset_index(drop=True)
    assert len(d) == 226 and set(d.split) == {"train", "val"}
    return d


def cloudy_tiles():
    """The 56 tiles with cloudy roads (production gate), from the earlier coverage check."""
    c = pd.read_csv(CHECK / "noaa_ida_tile_cover.csv")
    return sorted(c.tile_id[c.has_cloudy_roads.astype(bool)])


def noaa_files():
    """{flight: [(local path, (w, s, e, n))]} for the 209 NOAA tiles that touch the area."""
    b = json.loads((CHECK / "noaa_ida_bounds.json").read_text())
    out = {f: [] for f in FLIGHTS}
    for key, bb in b.items():
        _, fl, name = key.split("/")
        f = fl.replace("_RGB", "")
        p = NOAA_DIR / fl / name
        out[f].append((p, tuple(bb)))
    return out


def sat_tile(tile_id):
    """sn8_clouds._tile (development tiles only): (pair dict, before, after, valid)."""
    from sn8_clouds import _tile
    return _tile(tile_id)


def tile_transform(p, shape):
    from rasterio.transform import from_origin
    return from_origin(p["x0"], p["y0"], RES, RES)


def tile_lonlat_bounds(p, shape):
    from pyproj import Transformer
    tr = Transformer.from_crs(EPSG, 4326, always_xy=True)
    h, w = shape
    xs = [p["x0"], p["x0"] + w * RES]
    ys = [p["y0"] - h * RES, p["y0"]]
    lon, lat = tr.transform([xs[0], xs[1], xs[0], xs[1]], [ys[0], ys[0], ys[1], ys[1]])
    return min(lon), min(lat), max(lon), max(lat)


def _overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def flight_sources(tile_id, p, shape):
    bb = tile_lonlat_bounds(p, shape)
    return {f: [path for path, nb in files if _overlaps(bb, nb)] for f, files in noaa_files().items()}


def reproject_flight(paths, p, shape, overview_level=None, resampling="average"):
    """The flight's NOAA tiles (RGBA) warped onto the satellite tile's 0.5 m UTM 15N grid. Returns float32 (H, W, 4):
    RGB and alpha (0-255, alpha averaged). Area averaging from full resolution unless overview_level is given."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
    h, w = shape
    dst_t = tile_transform(p, shape)
    rgb = np.zeros((4, h, w), np.float32)
    for path in paths:
        kw = {"overview_level": overview_level} if overview_level is not None else {}
        with rasterio.open(path, **kw) as src:
            arr = np.zeros((4, h, w), np.float32)
            reproject(source=rasterio.band(src, [1, 2, 3, 4]), destination=arr, dst_transform=dst_t,
                      dst_crs=f"EPSG:{EPSG}", resampling=getattr(Resampling, resampling), src_nodata=None,
                      dst_nodata=0, num_threads=2)
        take = arr[3] > rgb[3]                 # mosaic within a flight: the source with more alpha wins
        rgb[:, take] = arr[:, take]
    return np.moveaxis(rgb, 0, -1)


def grey_of(rgb):
    return (GREY_W[0] * rgb[..., 0] + GREY_W[1] * rgb[..., 1] + GREY_W[2] * rgb[..., 2]).astype(np.float32)


def cpu_backbone():
    """Load sn8_dino's frozen DINOv2 on the CPU (MPS hidden only while the model is built; the GPU is busy)."""
    import sn8_dino as D
    import torch
    orig = torch.backends.mps.is_available
    torch.backends.mps.is_available = lambda: False
    try:
        model, device = D.backbone()
    finally:
        torch.backends.mps.is_available = orig
    assert device == "cpu"
    torch.set_num_threads(int(os.environ.get("IDA_TORCH_THREADS", "4")))
    return model


def akey(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        a = np.ascontiguousarray(a)
        h.update(str(a.shape).encode()); h.update(str(a.dtype).encode()); h.update(a.tobytes())
    return h.hexdigest()[:20]


def cached_tokens(grey, valid):
    """sn8_dino.tokens, cached on disk by the exact image and valid mask (float16 to keep the cache small)."""
    import sn8_dino as D
    d = BIG / "tokens"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{akey(grey.astype(np.float32), valid.astype(bool))}.npy"
    if f.exists():
        return np.load(f).astype(np.float32)
    cpu_backbone()
    if _ORIG_TOKENS is None:
        patch_tokens()
    t = window_tokens(grey, valid).astype(np.float16)
    np.save(f, t)
    return t.astype(np.float32)          # always the float16-rounded tokens, cached or not


_ORIG_TOKENS = None


def patch_tokens():
    """Route sn8_dino.tokens (used inside lines_dino and the spotter) through the disk cache, in this process only."""
    global _ORIG_TOKENS
    import sn8_dino as D
    import sn8_cloudspot as CS
    if _ORIG_TOKENS is None:
        _ORIG_TOKENS = D.tokens
        D.tokens = cached_tokens
        if hasattr(CS, "tokens"):
            CS.tokens = cached_tokens


_WIN_CACHE = {}


def window_tokens(grey, valid):
    """sn8_dino.tokens, line for line, except that each of its 2 x 2 windows is looked up by the exact bytes of its
    normalised input first: DINOv2 runs on each window on its own, so a window whose input is identical (e.g. outside
    the two-date gate) gives identical tokens and is not recomputed. In-process cache of the last 48 windows."""
    import torch
    import sn8_dino as D
    model, device = D.backbone()
    PATCH = D.PATCH
    n_r, n_c = -(-grey.shape[0] // PATCH), -(-grey.shape[1] // PATCH)
    g = np.full((n_r * PATCH, n_c * PATCH), grey[valid].mean(), np.float32)
    g[: grey.shape[0], : grey.shape[1]] = np.where(valid, grey, grey[valid].mean())
    x = np.stack([(g / 255 - m) / s for m, s in zip(D.MEAN, D.STD)]).astype(np.float32)
    rows, cols = np.array_split(np.arange(n_r), D.WINDOWS), np.array_split(np.arange(n_c), D.WINDOWS)
    out = np.zeros((n_r, n_c, model.embed_dim), np.float32)
    with torch.inference_mode():
        for r in rows:
            for c in cols:
                win = np.ascontiguousarray(x[:, r[0] * PATCH:(r[-1] + 1) * PATCH, c[0] * PATCH:(c[-1] + 1) * PATCH])
                k = hashlib.sha256(win.tobytes()).hexdigest() + str(win.shape)
                if k not in _WIN_CACHE:
                    f = model.forward_features(torch.from_numpy(win[None]).to(device))[0, model.num_prefix_tokens:]
                    _WIN_CACHE[k] = f.float().cpu().numpy().reshape(len(r), len(c), -1)
                    while len(_WIN_CACHE) > 48:
                        _WIN_CACHE.pop(next(iter(_WIN_CACHE)))
                out[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = _WIN_CACHE[k]
    return out
