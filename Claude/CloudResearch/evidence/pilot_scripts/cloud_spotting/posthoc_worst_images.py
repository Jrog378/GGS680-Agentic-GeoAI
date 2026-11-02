"""POST HOC (chosen after seeing the per-image scores): the chosen library spotter's two lowest per-image F1 images
(barren_15, snow_24), with the dark rule and DINOv3 alone. Each image is predicted by the model of the fold that held
it out, refitted here exactly as cross_validate does (same folds, same PCA sample, same learner and seed); the run
checks that the refitted model reproduces the image's counts in counts_library.csv / counts_benchmark.csv."""
import json
import sys

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
FIG = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/figures/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
sys.path.append(HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from sklearn.model_selection import StratifiedGroupKFold

import sn8_cloudspot as cs
from dinov3_source import DINOV3
from figures import HRC_CREDIT, outcome

from sn8_cloudref import hrc_image, hrc_images, single_date_masks

chosen = json.load(open(f"{HERE}/choice.json"))["chosen"]
counts = pd.concat([pd.read_csv(f"{HERE}/counts_library.csv"), pd.read_csv(f"{HERE}/counts_benchmark.csv")])
names = hrc_images("train")
types = np.array([n.split("_")[0] for n in names])
cues = cs._hrc_cues(names)
sources = {"v2": cs.DINOV2, "v3": DINOV3}
arms = {chosen: cs.LIBRARY_ARMS[chosen], "DINOv3": [f"v3_pc{k}" for k in range(cs.N_PCS)]}
folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=cs.SEED).split(names, types, groups=names))
for name in ("barren_15", "snow_24"):
    i = names.index(name)
    tr = next(tr for tr, te in folds if i in te)
    im = hrc_image(name)
    maps = {}
    for arm, cols in arms.items():
        all_cols, prefixes = cs._columns({arm: cols})
        k = [all_cols.index(c) for c in cols]
        bases = {p: cs.fit_basis(sources[p][0], [names[j] for j in tr]) for p in prefixes}
        x = np.concatenate([cs._features(names[j], j, "train", cues, sources, bases, prefixes) for j in tr])
        y = np.concatenate([cues[f"{names[j]}|train|y"] for j in tr])
        model = cs.forest().fit(x[:, k], y)
        grid = cs._features(name, i, "grid", cues, sources, bases, prefixes)
        got = cs._counts(model.predict_proba(grid[:, k])[:, 1] >= cs.CUT, cues[f"{name}|grid|y"])
        ref = counts[(counts.arm == arm) & (counts.learner == "random forest") & (counts.image == name)].iloc[0]
        assert all(got[c] == ref[c] for c in ("TP", "FP", "FN", "TN")), (name, arm, got, ref.to_dict())
        cm = cs.classical_cues(im["grey"])
        full = [np.stack([cm[c] for c in cs.CUES], -1)]
        full += [cs.pc_map(sources[p][0](name), bases[p], im["grey"].shape, sources[p][1]) for p in prefixes]
        full = np.concatenate(full, -1).reshape(-1, len(all_cols))[:, k]
        maps[arm] = model.predict_proba(full)[:, 1].reshape(im["grey"].shape) >= cs.CUT
        print(name, arm, "reproduces the CV counts", got, flush=True)
    g, truth = im["grey"], im["cloud"]
    fig, axes = plt.subplots(1, 5, figsize=(27, 4.6))
    axes[0].imshow(g, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title(f"{name} (grey)", fontsize=10)
    axes[1].imshow(g, cmap="gray", vmin=0, vmax=255)
    axes[1].imshow(np.ma.masked_where(~truth, truth), cmap=ListedColormap(["orange"]), alpha=0.5)
    axes[1].set_title(f"expert cloud mask: {100 * truth.mean():.0f}% of the image", fontsize=10)
    outcome(axes[2], g, single_date_masks(g)["dark"], truth, "dark rule (production, no learning)")
    outcome(axes[3], g, maps["DINOv3"], truth, "DINOv3 alone (benchmark, research only), held out")
    outcome(axes[4], g, maps[chosen], truth, f"chosen library spotter: {chosen}, held out")
    for ax in axes:
        ax.axis("off")
    fig.legend(handles=[Patch(color="limegreen", label="cloud found"), Patch(color="red", label="false alarm"),
                        Patch(color="dodgerblue", label="cloud missed")], loc="lower right", ncol=3, fontsize=9)
    fig.text(0.01, 0.02, HRC_CREDIT + ". POST HOC: the chosen spotter's lowest per-image F1 images. Held-out fold "
             "models, random forest, cloud at p >= 0.5.", fontsize=9)
    plt.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(f"{FIG}/posthoc_hrc_{name}_worst.png", dpi=110)
    plt.close(fig)
    print("saved", f"posthoc_hrc_{name}_worst.png", flush=True)
