"""Steps 3-5 (no DINOv2 except inside the spotter): NOAA reprojection, NOAA's own cloud/glare mask, grey, AROSICS-style
local co-registration, IR-MAD/PIF-style no-change selection and the frozen tone curve, the four arms and the regions.

Per kept tile (s1_coverage.csv, valid cover >= 50%), in this order (pre-registration + Revision 1 + the coordinator's
full-text corrections, 2026-10-29):
 1. NOAA RGBA of the chosen flight, area-averaged from full resolution onto the tile's 0.5 m UTM 15N grid; NOAA valid =
    alpha fully 255 after averaging, eroded 3 px.
 2. NOAA grey with the SpaceNet greyscale weights (0.299, 0.587, 0.114). NOAA cloud/glare = sn8_clouds.bright_mask on
    NOAA grey (grey > 200 and local std < 10 in 21 px), the plan's "bright rule"; masked before alignment and tone.
 3. Satellite: the three classical cloud masks (sn8_clouds.cloud_maps), two-date de-hazing
    (sn8_cloudsym.either_date_dehaze), He 2011 (sn8_clouds.dehaze); the spotter (sn8_cloudpipe.best_spotter, research
    only) on the tiles that get DINOv2 scoring (all cloudy + the fixed clear sample, see SAMPLE below); the spotter-gated
    two-date arm: the spotter mask kept in blobs of >= 2,500 m2 (as the dark-rise gate) as the gate of
    sn8_cloudsym._correct, after image against the before image, clear pixels = valid minus every gate + 10 m margin.
 4. Local co-registration, AROSICS-style (Scheffler et al. 2017; settings from literature_fulltext/
    scheffler2017_arosics_coregistration_RemoteSensing.md): 256 px windows every 128 px on gradient-magnitude images
    (sn8_coreg._gradient), windows with more than 30% bad data skipped (bad = satellite cloud of any mask + 10 m, NOAA
    cloud/glare, no-data); phase correlation; reject peak reliability R < 30 % (Eq. 3), shift > 5 px, or SSIM not
    improved by the shift; RANSAC affine over the surviving shifts with the inlier threshold tuned until 10 +- 2 % are
    outliers; the affine applied to NOAA (bicubic, clipped). Reference: the satellite after image; when fewer than
    MIN_WINDOWS windows survive there (cloud), thin cloud is allowed to carry tie points (only opaque cloud
    masked), flagged per tile. Residual: the same window matching rerun after the
    correction; RMS of the surviving residual shifts (internal residual, as AROSICS reports it). Drop when > 1 px or
    when alignment fails (< MIN_WINDOWS windows on either reference).
 5. Tone curve NOAA grey -> satellite after grey: sn8_refhaze.tone_curve (monotone quantile matching), fitted on
    clear-guard pixels valid in both, then refitted on IR-MAD-style no-change pixels: residual of 5 px box-smoothed
    images, keep |r - median| < 1.96 robust sigma (chi-square, 1 dof, no-change probability > 0.05), iterated to
    convergence (< 0.5 % of pixels change, max 10). Frozen for every arm.
Writes BIG/prep/<tile>.npz and s2_prep.csv.
    nice -n 10 python3 -I s2_prep.py [n_workers] > s2_prep.log 2>&1
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import cv2
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

WIN, STEP, MAX_BAD = 256, 128, 0.30
R_MIN, MAX_SHIFT_PX = 30.0, 5.0
MIN_WINDOWS = 4
OUTLIER_TARGET, OUTLIER_TOL = 0.10, 0.02
NOAA_ERODE = 3
PIF_SMOOTH, PIF_Z, PIF_MAXIT = 5, 1.96, 10
MAX_RESIDUAL_PX = 1.0
N_CLEAR_SAMPLE = 30                      # fixed before any comparison: clear tiles that also get DINOv2 scoring
PREP = C.BIG / "prep"


def sample_tiles(cov):
    """All kept cloudy tiles + N_CLEAR_SAMPLE kept clear tiles drawn with seed 662 (fixed before scoring)."""
    kept = cov[cov.kept_cover]
    clear = sorted(kept.tile_id[~kept.cloudy])
    rng = np.random.default_rng(C.SEED)
    pick = sorted(rng.choice(clear, size=min(N_CLEAR_SAMPLE, len(clear)), replace=False))
    return sorted(kept.tile_id[kept.cloudy]), pick


# ---------------- AROSICS-style matching ----------------
def _hann(n):
    return cv2.createHanningWindow((n, n), cv2.CV_32F)


def _reliability(a, b, win):
    """Peak reliability R (Scheffler et al. 2017, Eq. 3) of the normalised cross-power spectrum's inverse."""
    F, G = np.fft.fft2(a * win), np.fft.fft2(b * win)
    cps = F * np.conj(G)
    cps /= np.maximum(np.abs(cps), 1e-12)
    v = np.fft.fftshift(np.abs(np.fft.ifft2(cps)))          # |IFFT| as AROSICS's shifted cross-power spectrum
    i, j = np.unravel_index(np.argmax(v), v.shape)
    m = np.zeros(v.shape, bool)
    m[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2] = True
    mu_peak = v[m].mean()
    rest = v[~m]
    return float(100 - 100 * (rest.mean() + 3 * rest.std()) / max(mu_peak, 1e-12))


def _shift_img(img, dx, dy, interp=cv2.INTER_LINEAR):
    """Content moved back by (dx, dy) px (the measured offset of img relative to the reference)."""
    m = np.float32([[1, 0, -dx], [0, 1, -dy]])
    return cv2.warpAffine(img.astype(np.float32), m, img.shape[::-1], flags=interp, borderMode=cv2.BORDER_REFLECT)


def match_windows(ref_g, tgt_g, ref_grey, tgt_grey, good):
    """Tie points: list of dicts (row, col centre, dx, dy, R, ssim gain) that pass the AROSICS checks."""
    from skimage.metrics import structural_similarity as ssim
    h, w = good.shape
    win = _hann(WIN)
    out = []
    for r0 in range(0, h - WIN + 1, STEP):
        for c0 in range(0, w - WIN + 1, STEP):
            sl = (slice(r0, r0 + WIN), slice(c0, c0 + WIN))
            if 1 - good[sl].mean() > MAX_BAD:
                continue
            a, b = ref_g[sl].astype(np.float32), tgt_g[sl].astype(np.float32)
            if a.std() < 1e-3 or b.std() < 1e-3:
                continue
            (dx, dy), _ = cv2.phaseCorrelate(a, b, win)
            if np.hypot(dx, dy) > MAX_SHIFT_PX:
                continue
            R = _reliability(a, b, win)
            if R < R_MIN:
                continue
            ra, rb = ref_grey[sl], tgt_grey[sl]
            g = good[sl]
            rng = float(max(ra[g].max() - ra[g].min(), rb[g].max() - rb[g].min(), 1))
            s0 = ssim(ra, rb, data_range=rng)
            s1 = ssim(ra, _shift_img(tgt_grey, dx, dy)[sl], data_range=rng)
            if not s1 > s0:
                continue
            out.append({"row": r0 + WIN / 2, "col": c0 + WIN / 2, "dx": dx, "dy": dy, "R": R, "ssim_gain": s1 - s0})
    return out


def ransac_affine(pts):
    """Affine from tie points (target position = reference position + shift), RANSAC with the inlier threshold tuned
    until 10 +- 2 % of points are outliers. Returns (2x3 matrix mapping reference px -> target px, inlier mask)."""
    from skimage.measure import ransac
    from skimage.transform import AffineTransform
    src = np.array([[p["col"], p["row"]] for p in pts], float)
    dst = src + np.array([[p["dx"], p["dy"]] for p in pts], float)
    if len(pts) < 6:                        # too few for a stable affine: translation by the median
        d = np.median(dst - src, 0)
        M = np.float64([[1, 0, d[0]], [0, 1, d[1]]])
        return M, np.ones(len(pts), bool), "translation (median)"
    lo, hi = 0.01, 5.0
    best = None
    for _ in range(25):
        thr = (lo + hi) / 2
        model, inl = ransac((src, dst), AffineTransform, min_samples=3, residual_threshold=thr, max_trials=500,
                            rng=C.SEED)
        if model is None:
            lo = thr
            continue
        frac = 1 - inl.mean()
        best = (model, inl)
        if abs(frac - OUTLIER_TARGET) <= OUTLIER_TOL:
            break
        if frac > OUTLIER_TARGET:
            lo = thr
        else:
            hi = thr
    model, inl = best
    A = np.c_[src[inl], np.ones(inl.sum())]                     # least-squares affine on the inliers
    coef, *_ = np.linalg.lstsq(A, dst[inl], rcond=None)
    return coef.T, inl, "affine (RANSAC)"


def warp_to_ref(img, M, interp):
    """Sample img (target) at M @ [x, y, 1] for every reference pixel: the target brought onto the reference."""
    h, w = img.shape[:2]
    return cv2.warpAffine(img.astype(np.float32), M.astype(np.float64), (w, h),
                          flags=interp | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


PRE_FACTOR, PRE_MAX_M = 4, 20.0
N_ITER = 5


def pre_shift(rg, tg):
    """Coarse whole-tile shift (px) by phase correlation of the gradient images block-averaged 4 x 4 (2 m), so the
    local windows' 5 px cap applies around it (AROSICS moves each window by its integer shift before the sub-pixel
    step; at 0.5 m a 5 px cap alone would be 2.5 m, finer than the photos' direct georeferencing)."""
    A = cv2.resize(rg, None, fx=1 / PRE_FACTOR, fy=1 / PRE_FACTOR, interpolation=cv2.INTER_AREA)
    B = cv2.resize(tg, None, fx=1 / PRE_FACTOR, fy=1 / PRE_FACTOR, interpolation=cv2.INTER_AREA)
    (dx, dy), resp = cv2.phaseCorrelate(A, B, cv2.createHanningWindow(A.shape[::-1], cv2.CV_32F))
    dx, dy = dx * PRE_FACTOR, dy * PRE_FACTOR
    if np.hypot(dx, dy) * C.RES > PRE_MAX_M:
        return 0.0, 0.0, float(resp)
    return float(dx), float(dy), float(resp)


def coregister(ref_grey, ref_valid, tgt_grey, tgt_good, sat_bad):
    from sn8_coreg import _gradient
    good = ref_valid & tgt_good & ~sat_bad
    if good.sum() < WIN * WIN:
        return None
    rg, tg = _gradient(ref_grey, good), _gradient(tgt_grey, good)
    pdx, pdy, presp = pre_shift(rg, tg)
    T = np.float64([[1, 0, pdx], [0, 1, pdy]])
    tgt1 = warp_to_ref(tgt_grey, T, cv2.INTER_LINEAR)
    good1 = good & (warp_to_ref(tgt_good.astype(np.float32), T, cv2.INTER_NEAREST) > 0.5)
    pts = match_windows(_gradient(ref_grey, good1), _gradient(tgt1, good1), np.where(good1, ref_grey, 0),
                        np.where(good1, tgt1, 0), good1)
    if len(pts) < MIN_WINDOWS:
        return {"n_windows": len(pts), "ok": False, "pre_dx_px": pdx, "pre_dy_px": pdy}
    for q in pts:                           # back to shifts relative to the original target
        q["dx"] += pdx
        q["dy"] += pdy
    M, inl, kind = ransac_affine(pts)

    def residual(M):
        tgt_al = warp_to_ref(tgt_grey, M, cv2.INTER_CUBIC)
        good_al = warp_to_ref(tgt_good.astype(np.float32), M, cv2.INTER_NEAREST) > 0.5
        g2 = ref_valid & good_al & ~sat_bad
        return match_windows(_gradient(ref_grey, g2), _gradient(tgt_al, g2), np.where(g2, ref_grey, 0),
                             np.where(g2, tgt_al, 0), g2) if g2.sum() >= WIN * WIN else []

    # iterate (AROSICS iterates each window's shift; OpenCV's sub-pixel centroid under-reads shifts): re-measure on the
    # corrected image, fit the residual affine (RANSAC) and compose, up to N_ITER times or until it is below 0.05 px
    n_iter = 0
    res = residual(M)
    for n_iter in range(1, N_ITER + 1):
        if len(res) < MIN_WINDOWS:
            break
        Rm, rin, _ = ransac_affine(res)
        step = np.hypot(np.median([q["dx"] for q in np.array(res)[rin]]), np.median([q["dy"] for q in np.array(res)[rin]]))
        M = np.c_[M[:, :2] @ Rm[:, :2], M[:, :2] @ Rm[:, 2] + M[:, 2]]
        res = residual(M)
        if step < 0.05:
            break
    rs = np.array([np.hypot(p["dx"], p["dy"]) for p in res]) if res else np.array([np.nan])
    rs_all = rs.copy()
    if len(res) >= 6:                       # AROSICS reports residuals after its RANSAC outlier removal (10 +- 2 %)
        rs = rs[ransac_affine(res)[1]]
    raw = np.array([np.hypot(p["dx"], p["dy"]) for p in pts])
    return {"ok": True, "M": M, "kind": kind, "iterations": n_iter, "pre_dx_px": pdx, "pre_dy_px": pdy, "pre_response": presp, "n_windows": len(pts), "n_inliers": int(inl.sum()),
            "raw_shift_median_px": float(np.median(raw)),
            "raw_dx_median_px": float(np.median([p["dx"] for p in pts])),
            "raw_dy_median_px": float(np.median([p["dy"] for p in pts])),
            "n_residual_windows": len(res), "residual_rms_px": float(np.sqrt(np.nanmean(rs ** 2))) if res else np.nan,
            "residual_median_px": float(np.nanmedian(rs)) if res else np.nan,
            "residual_rms_all_px": float(np.sqrt(np.nanmean(rs_all ** 2))) if res else np.nan, "pts": pts}


# ---------------- tone ----------------
def pif_tone(noaa, sat, sel):
    from sn8_refhaze import tone_curve
    ks = (PIF_SMOOTH, PIF_SMOOTH)
    keep = sel.copy()
    n0 = int(sel.sum())
    it = 0
    for it in range(1, PIF_MAXIT + 1):
        tone, _, _ = tone_curve(noaa, sat, keep)
        r = cv2.blur(tone(noaa).astype(np.float32), ks) - cv2.blur(sat.astype(np.float32), ks)
        rv = r[sel]
        med = np.median(rv)
        sig = 1.4826 * np.median(np.abs(rv - med))
        new = sel & (np.abs(r - med) < PIF_Z * max(sig, 1e-6))
        changed = (new != keep).sum() / max(n0, 1)
        keep = new
        if changed < 0.005:
            break
    tone, xb, ya = tone_curve(noaa, sat, keep)
    return tone, keep, {"pif_iterations": it, "pif_kept_share": float(keep.sum() / max(n0, 1)), "tone_px": int(keep.sum()),
                        "tone_x": xb.tolist(), "tone_y": ya.tolist()}


def buildings_mask(tile_id, p, shape):
    import json
    from rasterio.features import rasterize
    from shapely.geometry import shape as shp
    from shapely.ops import transform as stf
    from sn8 import tile
    from sn8_lines import _TO_UTM
    feats = json.load(open(tile(tile_id)["label"]))["features"]
    geoms = [stf(lambda x, y, z=None: _TO_UTM.transform(x, y), shp(f["geometry"])) for f in feats
             if (f.get("properties") or {}).get("building") and f.get("geometry")]
    if not geoms:
        return np.zeros(shape, bool)
    return rasterize(geoms, out_shape=shape, transform=C.tile_transform(p, shape)).astype(bool)


def _save(out_f, **arrays):
    """Atomic write (added 2026-10-30 after a truncated file: temp file, then rename). Contents unchanged."""
    tmp = out_f.with_suffix(".writing")
    with open(tmp, "wb") as fh:
        np.savez_compressed(fh, **arrays)
    tmp.replace(out_f)


def prep_one(tile_id, flight, second, with_spotter):
    out_f = PREP / f"{tile_id}.npz"
    if out_f.exists():
        z = np.load(out_f, allow_pickle=True)
        return dict(z["row"].item())
    t0 = time.time()
    from sn8_clouds import bright_mask, cloud_maps, dehaze
    from sn8_cloudsym import _correct, _keep_blobs, either_date_dehaze
    from sn8_refhaze import DARKREF_CLEAR_MARGIN_PX
    p, before, after, valid = C.sat_tile(tile_id)
    shape = valid.shape
    row = {"tile_id": tile_id, "flight": flight}
    # satellite masks and arms
    m = cloud_maps(tile_id)["masks"]
    see = either_date_dehaze(before, after, valid)
    he = dehaze(after, valid)[0]
    gate_td = see["rise"] | see["both"]
    spot = np.zeros(shape, bool)
    td_spot, t_spot = see["after corrected"], see["t after"]
    if with_spotter:
        from sn8_cloudpipe import best_spotter
        from sn8_cloudspot import CUT
        C.patch_tokens()
        C.cpu_backbone()
        prob = best_spotter().proba(after, valid)
        spot = (np.nan_to_num(prob) >= CUT) & valid
        sgate = _keep_blobs(spot)
        gates = sgate | see["rise"] | see["fall"] | see["both"]
        clear_s = valid & ~ndi.binary_dilation(gates, iterations=DARKREF_CLEAR_MARGIN_PX)
        from sn8_clouds import dark_channel
        db, da = dark_channel(before, valid), dark_channel(after, valid)
        fa, ta, oa, _ = _correct(before, after, db, da, valid, sgate, clear_s)
        td_spot = np.where(valid, np.where(oa, after, fa), 0).astype(np.float32)
        t_spot = ta
        row["spot_gate_share"] = float(sgate[valid].mean())
    sat_cloud = m["bright"] | m["dark"] | m["dark rise"] | see["rise"] | see["fall"] | see["both"] | spot
    sat_bad = ndi.binary_dilation(sat_cloud, iterations=DARKREF_CLEAR_MARGIN_PX)
    # NOAA
    src = C.flight_sources(tile_id, p, shape)

    def noaa(fl):
        rgba = C.reproject_flight(src[fl], p, shape)
        nv = ndi.binary_erosion(rgba[..., 3] >= 254.5, iterations=NOAA_ERODE)
        g = np.where(nv, C.grey_of(rgba), 0).astype(np.float32)
        nc = bright_mask(g) & nv
        return g, nv, nc, rgba[..., :3]

    ng, nv, nc, nrgb = noaa(flight)
    row.update(noaa_cloud_share=float(nc[nv & valid].mean()) if (nv & valid).any() else np.nan)
    # co-registration against the after image: every cloud mask (+10 m) excluded; when fewer than MIN_WINDOWS windows
    # survive, only opaque cloud is excluded (bright rule, t < 0.2, cannot assess; + 10 m) and thin cloud may carry
    # tie points (flagged). (The before image is no fallback: its own shift to the after image is often several m.)
    co = coregister(after, valid, ng, nv & ~nc, sat_bad)
    ref = "after, all cloud masked"
    if co is None or not co["ok"]:
        opaque_bad = ndi.binary_dilation(m["bright"] | see["cannot"] | (np.nan_to_num(see["t after"], nan=1) < 0.2),
                                         iterations=DARKREF_CLEAR_MARGIN_PX)
        row["after_windows"] = (co or {}).get("n_windows", 0)
        co, ref = coregister(after, valid, ng, nv & ~nc, opaque_bad), "after, thin cloud allowed"
    row["coreg_ref"] = ref
    if co is None or not co["ok"]:
        row.update(coreg_ok=False, n_windows=(co or {}).get("n_windows", 0), seconds=round(time.time() - t0))
        _save(out_f, row=np.array(row, dtype=object))
        return row
    M = co["M"]
    row.update({k: co[k] for k in ("kind", "pre_dx_px", "pre_dy_px", "pre_response", "iterations", "n_windows", "n_inliers", "raw_shift_median_px", "raw_dx_median_px",
                                   "raw_dy_median_px", "n_residual_windows", "residual_rms_px", "residual_median_px",
                                   "residual_rms_all_px")})
    row["M"] = M.round(5).tolist()
    row["coreg_ok"] = bool(np.isfinite(co["residual_rms_px"]) and co["residual_rms_px"] <= MAX_RESIDUAL_PX)
    ng_al = np.clip(warp_to_ref(ng, M, cv2.INTER_CUBIC), 0, 255)
    nv_al = warp_to_ref(nv.astype(np.float32), M, cv2.INTER_NEAREST) > 0.5
    nc_al = warp_to_ref(nc.astype(np.float32), M, cv2.INTER_NEAREST) > 0.5
    nrgb_al = np.stack([np.clip(warp_to_ref(nrgb[..., k], M, cv2.INTER_CUBIC), 0, 255) for k in range(3)], -1)
    nv_al = ndi.binary_erosion(nv_al, iterations=2)
    score = valid & nv_al & ~nc_al
    guard = score & ~sat_cloud
    tone, pif, info = pif_tone(ng_al, after, guard)
    noaa_t = np.where(nv_al, np.clip(tone(ng_al), 1, 255), 0).astype(np.float32)
    row.update({k: v for k, v in info.items() if not k.startswith("tone_")})
    row.update(score_px=int(score.sum()), guard_px=int(guard.sum()),
               thin_px=int((score & gate_td & ~see["cannot"] & (see["t after"] >= 0.2)).sum()),
               opaque_px=int((score & gate_td & (see["cannot"] | (see["t after"] < 0.2))).sum()))
    arrays = {"noaa": noaa_t, "noaa_raw": ng_al.astype(np.float32), "noaa_rgb": nrgb_al.astype(np.uint8),
              "noaa_valid": nv_al, "noaa_cloud": nc_al, "score": score, "guard": guard, "pif": pif,
              "before": before, "asis": after, "he": he, "td": see["after corrected"], "tdspot": td_spot,
              "t": see["t after"].astype(np.float32), "t_spot": np.asarray(t_spot, np.float32),
              "cannot": see["cannot"], "gate_td": gate_td, "fall": see["fall"], "bright": m["bright"],
              "dark": m["dark"], "darkrise": m["dark rise"], "spot": spot, "spotter_run": np.array(with_spotter),
              "buildings": buildings_mask(tile_id, p, shape), "valid": valid,
              "tone_x": np.array(info["tone_x"]), "tone_y": np.array(info["tone_y"])}
    # second flight (date-gap noise floor), aligned and tone-matched the same way
    if second:
        g2, v2, c2, _ = noaa(second)
        co2 = coregister(after, valid, g2, v2 & ~c2, sat_bad if ref.startswith("after, all") else opaque_bad)
        if co2 is not None and co2["ok"]:
            M2 = co2["M"]
            g2a = np.clip(warp_to_ref(g2, M2, cv2.INTER_CUBIC), 0, 255)
            v2a = ndi.binary_erosion(warp_to_ref(v2.astype(np.float32), M2, cv2.INTER_NEAREST) > 0.5, iterations=2)
            c2a = warp_to_ref(c2.astype(np.float32), M2, cv2.INTER_NEAREST) > 0.5
            tone2, _, info2 = pif_tone(g2a, after, guard & v2a & ~c2a)
            arrays["noaa2"] = np.where(v2a, np.clip(tone2(g2a), 1, 255), 0).astype(np.float32)
            arrays["noaa2_ok"] = v2a & ~c2a
            row.update(second_flight=second, second_residual_rms_px=co2["residual_rms_px"],
                       second_ok=bool(np.isfinite(co2["residual_rms_px"]) and co2["residual_rms_px"] <= MAX_RESIDUAL_PX))
        else:
            row.update(second_flight=second, second_ok=False)
    row["seconds"] = round(time.time() - t0)
    _save(out_f, row=np.array(row, dtype=object),
                        pts=np.array(co["pts"], dtype=object), **arrays)
    return row


def main():
    n_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    PREP.mkdir(parents=True, exist_ok=True)
    cov = pd.read_csv(C.HERE / "s1_coverage.csv")
    cloudy, clear_pick = sample_tiles(cov)
    scored = set(cloudy) | set(clear_pick)
    (C.HERE / "scored_tiles.txt").write_text("\n".join(sorted(scored)) + "\n")
    kept = cov[cov.kept_cover].copy()
    jobs = []
    for r in kept.itertuples():
        if only and r.tile_id not in only:
            continue
        covers = {f: getattr(r, f"cover_{f}") for f in C.FLIGHTS}
        others = [f for f in C.FLIGHTS if f != r.flight and covers[f] >= C.MIN_COVER]
        second = others[0] if others and r.tile_id in scored else None
        jobs.append((r.tile_id, r.flight, second, r.tile_id in scored))
    # cloudy tiles first
    jobs.sort(key=lambda j: (j[0] not in cloudy, j[0]))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(n_workers) as ex:
        futs = {ex.submit(prep_one, *j): j[0] for j in jobs}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                       # report, keep going
                r = {"tile_id": futs[f], "error": repr(e)}
            rows.append(r)
            print(f"{futs[f]}: ok={r.get('coreg_ok')} ref={r.get('coreg_ref')} win={r.get('n_windows')} "
                  f"res={r.get('residual_rms_px')} err={r.get('error', '')} {round(time.time() - t0)} s", flush=True)
    df = pd.DataFrame(rows).drop(columns=["M"], errors="ignore")
    if only is None:
        df.to_csv(C.HERE / "s2_prep.csv", index=False)
    print(df.drop(columns=[c for c in df.columns if c.startswith("tone")], errors="ignore").describe().T.to_string())


if __name__ == "__main__":
    main()
