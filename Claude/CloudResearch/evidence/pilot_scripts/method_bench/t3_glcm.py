"""Arm T3: GLCM with equal-probability ("probability") quantising per road strip (Haralick 1979, Proc. IEEE 67:786,
p. 787: "To compensate for this, probability quantizing can be employed"; handoff
literature_fulltext/haralick1979_statistical_structural_texture_ProcIEEE.md; claim_checks_C Haralick #2-3: the
invariance needs distribution-tied quantising).
sn8_glcm's settings (32 levels, neighbours 1 m apart, 4 directions summed, symmetric; its cooccurrence() and haralick()
are imported) but the levels are cut from each road strip's own pixels per date instead of the whole tile.
15 columns glcmS_<prop>_{before,after,change}; replaces the 15 glcm_* columns.
"""
import numpy as np

PROPS = ["contrast", "homogeneity", "asm", "entropy", "correlation"]
COLUMNS = [f"glcmS_{p}_{d}" for p in PROPS for d in ("before", "after", "change")]


def strip_quantize(grey, region, n, levels):
    q = np.full(grey.shape, -1, np.int16)
    flat_r = region.ravel()
    order = np.argsort(flat_r, kind="stable")
    bounds = np.searchsorted(flat_r[order], np.arange(n + 2))
    gflat = grey.ravel()
    qf = q.ravel()
    for k in range(1, n + 1):
        px = order[bounds[k]:bounds[k + 1]]
        if len(px) == 0:
            continue
        v = gflat[px]
        cuts = np.quantile(v, np.arange(1, levels) / levels)
        qf[px] = np.searchsorted(cuts, v, side="right")
    return qf.reshape(grey.shape)


def glcm_features(grey_before, grey_after, valid, region, n):
    from sn8_glcm import GLCM_LEVELS, cooccurrence, haralick
    res = {}
    reg = np.where(valid, region, 0)
    for date, g in (("before", grey_before), ("after", grey_after)):
        q = strip_quantize(g, reg, n, GLCM_LEVELS)
        for prop, v in haralick(cooccurrence(q, reg, n)).items():
            res[f"glcmS_{prop}_{date}"] = v
    for prop in PROPS:
        res[f"glcmS_{prop}_change"] = res[f"glcmS_{prop}_after"] - res[f"glcmS_{prop}_before"]
    return res
