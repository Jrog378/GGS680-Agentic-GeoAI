"""Arm D1: RGB colour cues for the cloud spotter (preregistration_method_bench.md, "Detection / gate").

  whiteness   Zhu & Woodcock 2012 (Fmask) Eq. 2, p. 85: sum_i |(B_i - MeanVis) / MeanVis|, MeanVis = (R + G + B) / 3,
              on 8-bit RGB (MeanVis floored at 1). Low = flat (white/grey) spectrum. Fmask ANDs it with SWIR/thermal
              tests; here the forest learns how to use it (claim_checks_C, Fmask #8).
  hot         Haze Optimized Transform as Fmask/Qiu use it (Zhang et al. 2002 via Zhu & Woodcock 2012 Eq. 3, p. 85):
              HOT = B sin(theta) - R cos(theta), theta = atan(k), with the clear line R = k B + b fitted on clear
              pixels (SN8: the BEFORE date; HRC_WHU: the training fold's expert-clear pixels).
  dark_rgb    He et al. 2011 Eq. 5: the dark channel over R, G, B (min over channels, then sn8_clouds.dark_channel's
              20 m minimum and box smoothing).
  gradratio   our adaptation of Shen et al. 2014's blue-vs-red gradient observation (their Eqs. 3-4 are scene means
              used to set cut-offs, claim_checks_C Shen #8): (mean Sobel |grad B| over 21 px + 1) / (same for R + 1).
"""
import cv2
import numpy as np

COLOUR = ["whiteness", "hot", "dark_rgb", "gradratio"]
WIN = 21                          # sn8_lines.CLOUD_WIN, the window of the spotter's texture cues


def whiteness(rgb):
    x = rgb.astype(np.float32)
    mv = np.maximum(x.mean(-1), 1.0)
    return np.abs((x - mv[..., None]) / mv[..., None]).sum(-1).astype(np.float32)


def dark_rgb(rgb, valid):
    from sn8_clouds import dark_channel
    return dark_channel(rgb.min(-1).astype(np.float32), valid)


def _grad(c):
    c = c.astype(np.float32)
    return np.hypot(cv2.Sobel(c, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(c, cv2.CV_32F, 0, 1, ksize=3))


def gradratio(rgb):
    gb = cv2.blur(_grad(rgb[..., 2]), (WIN, WIN))
    gr = cv2.blur(_grad(rgb[..., 0]), (WIN, WIN))
    return ((gb + 1) / (gr + 1)).astype(np.float32)


def clear_line(r, b):
    """Least-squares clear line r = k b + c over the given pixel values (saturated > 250 and near-black < 5 left out
    by the caller). Returns (k, c)."""
    k, c = np.polyfit(np.asarray(b, np.float64), np.asarray(r, np.float64), 1)
    return float(k), float(c)


def hot(rgb, k):
    th = np.arctan(k)
    return (rgb[..., 2].astype(np.float32) * np.sin(th) - rgb[..., 0].astype(np.float32) * np.cos(th)).astype(np.float32)


def colour_maps(rgb, valid, k=None):
    """whiteness, dark_rgb, gradratio (and hot if the clear-line slope k is given) as float32 maps."""
    out = {"whiteness": whiteness(rgb), "dark_rgb": dark_rgb(rgb, valid), "gradratio": gradratio(rgb)}
    if k is not None:
        out["hot"] = hot(rgb, k)
    return out


def sn8_before_line(before_rgb, clear, seed=662, n=50_000):
    """The clear line of a SN8 tile, fitted on the BEFORE image's clear pixels (not saturated or near black)."""
    ok = clear & (before_rgb.max(-1) < 250) & (before_rgb.min(-1) > 5)
    idx = np.flatnonzero(ok)
    if len(idx) < 500:
        return None
    idx = np.random.default_rng(seed).choice(idx, min(n, len(idx)), replace=False)
    return clear_line(before_rgb[..., 0].ravel()[idx], before_rgb[..., 2].ravel()[idx])
