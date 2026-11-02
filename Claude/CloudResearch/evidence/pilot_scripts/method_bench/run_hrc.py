"""Detection arms on HRC_WHU's 120 development images (preregistration_method_bench.md, scoring (a)).

D0 (the chosen spotter, reproduced against cloud_spotting/counts_library.csv first), D1a-d and D1 (D0 + RGB colour cues),
D2 (Zhang & Xiao 2014 rule). Same unit as sn8_cloudspot.cross_validate: 1,000 training pixels per image, every-4th
grid scored, StratifiedGroupKFold(5, shuffle, 662) by land cover, DINOv2 PCA fitted in each training fold. The sealed
30 test images are never read (hrc_images("train") only). Writes BIG/hrc_counts.csv, BIG/hrc_proba.npz.
    nice -n 10 python3 -I run_hrc.py > run_hrc.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import json
import numpy as np
import pandas as pd

T0 = time.time()
COLOUR_CACHE = C.BIG / "hrc_colour.npz"


def colour_at_pixels(names):
    from sn8_cloudref import hrc_image
    from sn8_cloudspot import grid_pixels, train_pixels
    from d1_colour import colour_maps
    if COLOUR_CACHE.exists():
        z = np.load(COLOUR_CACHE)
        return {k: z[k] for k in z.files}
    out = {}
    for i, name in enumerate(names):
        im = hrc_image(name)
        rgb = im["rgb"]
        valid = np.ones(im["grey"].shape, bool)
        m = colour_maps(rgb, valid)
        for part, (r, c) in (("train", train_pixels(i, im["grey"].shape)), ("grid", grid_pixels(im["grey"].shape))):
            out[f"{name}|{part}|rgb"] = rgb[r, c].astype(np.uint8)
            out[f"{name}|{part}|c"] = np.stack([m[k][r, c] for k in ("whiteness", "dark_rgb", "gradratio")], 1)
        if i % 20 == 0:
            C.log(T0, f"colour cues {i}/{len(names)}")
    np.savez(COLOUR_CACHE, **out)
    return out


def main():
    from sklearn.model_selection import StratifiedGroupKFold
    from sn8_cloudref import hrc_image, hrc_images
    from sn8_cloudspot import (CUES, DINOV2, N_PCS, _counts, _features, _hrc_cues, fit_basis, forest, grid_pixels,
                               hrc_dinov2_tokens)
    from d1_colour import clear_line, hot
    from d2_zhangxiao import zhang_xiao
    h0 = C.registry_hash()
    names = hrc_images("train")
    assert len(names) == 120
    types = np.array([n.split("_")[0] for n in names])
    choice = json.loads((C.PILOT / "cloud_spotting" / "choice.json").read_text())
    d0 = choice["columns"]
    assert choice["chosen"] == "classical + DINOv2 - dark"
    colour = ["whiteness", "hot", "dark_rgb", "gradratio"]
    arms = {"D0": d0, "D1a whiteness": d0 + ["whiteness"], "D1b HOT": d0 + ["hot"], "D1c RGB dark": d0 + ["dark_rgb"],
            "D1d gradient ratio": d0 + ["gradratio"], "D1 all colour": d0 + colour}
    all_cols = list(CUES) + [f"v2_pc{k}" for k in range(N_PCS)] + colour
    index = {c: k for k, c in enumerate(all_cols)}
    cues = _hrc_cues(names)
    col = colour_at_pixels(names)
    C.log(T0, "cues ready")
    rows, proba = [], {}
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=C.SEED).split(names, types, groups=names)
    lines = {}
    for fold, (tr, te) in enumerate(folds):
        bases = {"v2": fit_basis(hrc_dinov2_tokens, [names[i] for i in tr])}
        src = {"v2": DINOV2}
        # the HOT clear line of this fold: the training images' expert-clear training pixels, not saturated/black
        rr, bb = [], []
        for i in tr:
            rgb = col[f"{names[i]}|train|rgb"]
            y = cues[f"{names[i]}|train|y"]
            ok = (~y) & (rgb.max(1) < 250) & (rgb.min(1) > 5)
            rr.append(rgb[ok, 0]); bb.append(rgb[ok, 2])
        k, c0 = clear_line(np.concatenate(rr), np.concatenate(bb))
        lines[fold] = (k, c0)

        def block(i, part):
            base = _features(names[i], i, part, cues, src, bases, ["v2"])
            rgb = col[f"{names[i]}|{part}|rgb"].astype(np.float32)[None]
            h = hot(rgb, k)[0][:, None]
            c3 = col[f"{names[i]}|{part}|c"]
            return np.concatenate([base, c3[:, :1], h, c3[:, 1:]], 1).astype(np.float32)   # whiteness, hot, dark, ratio

        x_tr = np.concatenate([block(i, "train") for i in tr])
        y_tr = np.concatenate([cues[f"{names[i]}|train|y"] for i in tr])
        x_te = {i: block(i, "grid") for i in te}
        for arm, cols in arms.items():
            kk = [index[c] for c in cols]
            model = forest()
            model.set_params(n_jobs=3)
            model.fit(x_tr[:, kk], y_tr)
            for i in te:
                p = model.predict_proba(x_te[i][:, kk])[:, 1]
                proba[f"{arm}|{names[i]}"] = p.astype(np.float16)
                rows.append({"arm": arm, "learner": "random forest", "image": names[i], "type": types[i], "fold": fold,
                             **_counts(p >= 0.5, cues[f"{names[i]}|grid|y"])})
            C.log(T0, f"fold {fold} {arm} done")
        if fold == 0:
            got = pd.DataFrame([r for r in rows if r["arm"] == "D0"]).set_index("image")
            ref = pd.read_csv(C.PILOT / "cloud_spotting" / "counts_library.csv")
            ref = ref[(ref.arm == "classical + DINOv2 - dark") & (ref.learner == "random forest")].set_index("image")
            for im in got.index:
                assert (got.loc[im, ["TP", "FP", "FN", "TN"]].to_numpy() == ref.loc[im, ["TP", "FP", "FN", "TN"]].to_numpy()).all(), \
                    f"STOP: D0 does not reproduce counts_library.csv on {im}"
            C.log(T0, f"reproduction check passed on fold 0 ({len(got)} images)")
    # D2: the rule, per image (no learning; fold kept for the table only)
    fold_of = {r["image"]: r["fold"] for r in rows}
    for i, name in enumerate(names):
        im = hrc_image(name)
        r, c = grid_pixels(im["grey"].shape)
        mask, soft = zhang_xiao(im["rgb"], return_soft=True)
        proba[f"D2 Zhang & Xiao|{name}"] = soft[r, c].astype(np.float16)
        rows.append({"arm": "D2 Zhang & Xiao", "learner": "none", "image": name, "type": types[i],
                     "fold": fold_of[name], **_counts(mask[r, c], cues[f"{name}|grid|y"])})
    C.log(T0, "D2 done")
    pd.DataFrame(rows).to_csv(C.HERE / "hrc_counts.csv", index=False)
    for i, name in enumerate(names):
        proba[f"y|{name}"] = cues[f"{name}|grid|y"]
        proba[f"fold|{name}"] = np.array([fold_of[name]])
    np.savez_compressed(C.BIG / "hrc_proba.npz", **proba)
    C.write_json(C.HERE / "hrc_lines.json", {str(k): v for k, v in lines.items()})
    assert C.registry_hash() == h0
    C.log(T0, "done")


if __name__ == "__main__":
    main()
