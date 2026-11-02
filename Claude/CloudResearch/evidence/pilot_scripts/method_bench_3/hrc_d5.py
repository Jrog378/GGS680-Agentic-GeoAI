"""Arm D5 (He, Sun, Yan & Fu 2022, DABNet boundary-weighted loss; he2021_dabnet handoff section 5): the spotter's
training pixels weighted towards the HRC_WHU label edge. 120 development images only (the sealed 30 are never read).

  boundary B = pixels whose 3 x 3 neighbourhood holds both classes; d = Euclidean distance to the NEAREST boundary
  pixel (the printed eq. 10 sums over all boundary pixels and, with eq. 11's softmax, gives w ~ 1 everywhere: handoff
  coding warning); w = 1 + alpha exp(-d / sigma), alpha = 1, sigma = 8 px.
  D5a: w as sample_weight on D0's 1,000 training pixels per image.
  D5b: 1,000 pixels per image drawn with probability proportional to w (rng (662, i, 5)), unweighted fit.
Same unit as bench 1's run_hrc.py: StratifiedGroupKFold(5, shuffle, 662) by land cover, DINOv2 PCA fitted per training
fold, every-4th grid scored. D0 reproduced against cloud_spotting/counts_library.csv on fold 0 or the run stops.
Scores: pooled F1, paired per-image F1 vs D0 (sn8_cloudspot.paired_f1), and the same on the boundary band (grid pixels
with d <= 16 px) and the interior (d > 16 px).
    OMP_NUM_THREADS=2 nice -n 10 python3 -I hrc_d5.py > hrc_d5.log 2>&1
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b3_common as K

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

T0 = time.time()
ALPHA, SIGMA, BAND_PX = 1.0, 8.0, 16
EDGE_CACHE = K.BIG / "hrc_edge.npz"


def edge_maps(names):
    """Per image: d (distance to the nearest label-boundary pixel) at the training pixels, the grid and the D5b draw,
    plus the D5b pixels' classical cues (cached)."""
    if EDGE_CACHE.exists():
        z = np.load(EDGE_CACHE)
        return {k: z[k] for k in z.files}
    from sn8_cloudref import hrc_image
    from sn8_cloudspot import CUES, classical_cues, grid_pixels, train_pixels
    out = {}
    for i, name in enumerate(names):
        im = hrc_image(name)
        lab = im["cloud"]
        mx = ndi.maximum_filter(lab.astype(np.uint8), 3)
        mn = ndi.minimum_filter(lab.astype(np.uint8), 3)
        bnd = mx != mn
        d = ndi.distance_transform_edt(~bnd) if bnd.any() else np.full(lab.shape, 1e6)
        w = 1 + ALPHA * np.exp(-d / SIGMA)
        for part, (r, c) in (("train", train_pixels(i, lab.shape)), ("grid", grid_pixels(lab.shape))):
            out[f"{name}|{part}|d"] = d[r, c].astype(np.float32)
        prob = (w / w.sum()).ravel()
        flat = np.random.default_rng([662, i, 5]).choice(lab.size, 1000, replace=False, p=prob)
        r, c = np.unravel_index(flat, lab.shape)
        cues = classical_cues(im["grey"])
        out[f"{name}|d5b|r"], out[f"{name}|d5b|c"] = r.astype(np.int32), c.astype(np.int32)
        out[f"{name}|d5b|x"] = np.stack([cues[k][r, c] for k in CUES], 1).astype(np.float32)
        out[f"{name}|d5b|y"] = lab[r, c]
        if i % 20 == 0:
            K.log(T0, f"edge maps {i}/{len(names)}")
    K.atomic_npz(EDGE_CACHE, **out)
    return out


def main():
    from sklearn.model_selection import StratifiedGroupKFold
    from sn8_cloudref import hrc_images
    from sn8_cloudspot import (CUES, DINOV2, N_PCS, PATCH, _counts, _features, _hrc_cues, fit_basis, forest,
                               hrc_dinov2_tokens, paired_f1, pcs_at, pooled_table)
    h0 = K.registry_hash()
    names = hrc_images("train")
    assert len(names) == 120
    types = np.array([n.split("_")[0] for n in names])
    choice = json.loads((K.M1.PILOT / "cloud_spotting" / "choice.json").read_text())
    d0 = choice["columns"]
    assert choice["chosen"] == "classical + DINOv2 - dark"
    all_cols = list(CUES) + [f"v2_pc{k}" for k in range(N_PCS)]
    kk = [all_cols.index(c) for c in d0]
    cues = _hrc_cues(names)
    em = edge_maps(names)
    K.log(T0, "cues and edge maps ready")
    rows = []
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=K.M1.SEED).split(names, types, groups=names)
    for fold, (tr, te) in enumerate(folds):
        K.wait_for_memory(T0)
        bases = {"v2": fit_basis(hrc_dinov2_tokens, [names[i] for i in tr])}
        src = {"v2": DINOV2}
        x_tr = np.concatenate([_features(names[i], i, "train", cues, src, bases, ["v2"]) for i in tr])[:, kk]
        y_tr = np.concatenate([cues[f"{names[i]}|train|y"] for i in tr])
        w_tr = np.concatenate([1 + ALPHA * np.exp(-em[f"{names[i]}|train|d"] / SIGMA) for i in tr])
        tok = {i: hrc_dinov2_tokens(names[i]) for i in tr}
        xb = np.concatenate([np.concatenate([em[f"{names[i]}|d5b|x"],
                                             pcs_at(tok[i], bases["v2"], em[f"{names[i]}|d5b|r"],
                                                    em[f"{names[i]}|d5b|c"], PATCH).astype(np.float32)], 1)
                             for i in tr])[:, kk]
        yb = np.concatenate([em[f"{names[i]}|d5b|y"] for i in tr])
        x_te = {i: _features(names[i], i, "grid", cues, src, bases, ["v2"])[:, kk] for i in te}
        models = {}
        for arm in ("D0", "D5a weighted", "D5b edge-sampled"):
            m = forest()
            m.set_params(n_jobs=2)
            if arm == "D0":
                m.fit(x_tr, y_tr)
            elif arm == "D5a weighted":
                m.fit(x_tr, y_tr, sample_weight=w_tr)
            else:
                m.fit(xb, yb)
            models[arm] = m
        for i in te:
            yg = cues[f"{names[i]}|grid|y"]
            dg = em[f"{names[i]}|grid|d"]
            for arm, m in models.items():
                p = m.predict_proba(x_te[i])[:, 1] >= 0.5
                for scope, sel in (("all", np.ones(len(yg), bool)), ("band", dg <= BAND_PX), ("interior", dg > BAND_PX)):
                    rows.append({"arm": arm, "scope": scope, "learner": "random forest", "image": names[i],
                                 "type": types[i], "fold": fold, **_counts(p[sel], yg[sel])})
        if fold == 0:
            got = pd.DataFrame([r for r in rows if r["arm"] == "D0" and r["scope"] == "all"]).set_index("image")
            ref = pd.read_csv(K.M1.PILOT / "cloud_spotting" / "counts_library.csv")
            ref = ref[(ref.arm == "classical + DINOv2 - dark") & (ref.learner == "random forest")].set_index("image")
            for im in got.index:
                assert (got.loc[im, ["TP", "FP", "FN", "TN"]].to_numpy() ==
                        ref.loc[im, ["TP", "FP", "FN", "TN"]].to_numpy()).all(), f"STOP: D0 does not reproduce on {im}"
            K.log(T0, f"reproduction check passed on fold 0 ({len(got)} images)")
        K.log(T0, f"fold {fold} done")
    df = pd.DataFrame(rows)
    df.to_csv(K.HERE / "hrc_d5_counts.csv", index=False)
    num = {"alpha": ALPHA, "sigma_px": SIGMA, "band_px": BAND_PX}
    for scope in ("all", "band", "interior"):
        c = df[df.scope == scope].drop(columns="scope")
        num[f"pooled_{scope}"] = pooled_table(c).to_dict("records")
        num[f"paired_{scope}"] = [paired_f1(c, a, "D0") for a in ("D5a weighted", "D5b edge-sampled")]
        for r in num[f"paired_{scope}"]:
            K.log(T0, f"{scope:8s} {r['a']:18s} F1 a-b {r['F1 a - b']:+.4f} CI {r['95% CI']} "
                      f"images higher {r['images a higher']} lower {r['images b higher']}")
    K.write_json(K.HERE / "hrc_d5_numbers.json", num)
    assert K.registry_hash() == h0
    K.log(T0, "done")


if __name__ == "__main__":
    main()
