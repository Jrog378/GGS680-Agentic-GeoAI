"""Cloud spotting arms on the 120 HRC_WHU development images (outputs/preregistration_cloud_spotting_pipeline.md).
    python3 -I run_cv.py library      # arms 1-9 (library tools) + the fixed rules + the full-image check
    python3 -I run_cv.py benchmark    # arms 10-16 (DINOv3, research benchmark only)
Writes counts_<stage>.csv (confusion counts per arm, learner and image on the scored grid), maps_<stage>.npz (held-out
probability maps of barren_1 and vegetation_1) and, for library, fullimage_check.csv. Prints progress, no scores
except the preregistered full-image check of the fixed rules."""
import sys
import time

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
sys.path.append(HERE)

import numpy as np
import pandas as pd

from sn8_cloudref import hrc_image, hrc_images, mask_scores, single_date_masks
from sn8_cloudspot import DINOV2, LIBRARY_ARMS, TOOLS, cross_validate, grid_pixels, scores

FIGURE_IMAGES = ("barren_1", "vegetation_1")   # the first barren and first vegetation image in hrc_images order
V3 = [f"v3_pc{k}" for k in range(32)]
C = TOOLS["bright"] + TOOLS["dark"] + TOOLS["texture"]
BENCHMARK_ARMS = {   # research only, never chosen
    "DINOv3": V3,
    "DINOv2 + DINOv3": TOOLS["dinov2"] + V3,
    "classical + DINOv3": C + V3,
    "everything": C + TOOLS["dinov2"] + V3,
    "everything - bright": TOOLS["dark"] + TOOLS["texture"] + TOOLS["dinov2"] + V3,
    "everything - dark": TOOLS["bright"] + TOOLS["texture"] + TOOLS["dinov2"] + V3,
    "everything - texture": TOOLS["bright"] + TOOLS["dark"] + TOOLS["dinov2"] + V3,
}

stage = sys.argv[1]
names = hrc_images("train")
assert len(names) == 120 and len(set(names)) == 120, "the 120 development images"
assert names[0] == "barren_1" and [n for n in names if n.startswith("vegetation")][0] == "vegetation_1"
t0 = time.time()
log = lambda m: print(f"{time.time() - t0:7.0f} s  {m}", flush=True)

if stage == "library":
    counts, maps = cross_validate(LIBRARY_ARMS, {"v2": DINOV2}, full_maps=FIGURE_IMAGES, log=log)
    # preregistered check: the fixed rules on every pixel against the scored grid
    rows = []
    for name in names:
        im = hrc_image(name)
        m = single_date_masks(im["grey"])
        b, d = m["bright"], m["dark"]
        r, c = grid_pixels(im["grey"].shape)
        for rule, pred in (("rule: bright", b), ("rule: dark", d), ("rule: bright OR dark", b | d),
                           ("rule: bright AND dark", b & d)):
            full = mask_scores(pred, im["cloud"])
            rows.append({"arm": rule, "image": name, "pixels": "all", **{k: full[k] for k in ("TP", "FP", "FN", "TN")}})
    full = pd.DataFrame(rows)
    full.to_csv(f"{HERE}/fullimage_check.csv", index=False)
    for rule, g in full.groupby("arm", sort=False):
        a = scores(*g[["TP", "FP", "FN"]].sum().to_numpy())
        q = counts[counts.arm == rule]
        b = scores(*q[["TP", "FP", "FN"]].sum().to_numpy())
        print(f"check {rule}: F1 every pixel {a['F1']:.4f}, scored grid {b['F1']:.4f}", flush=True)
elif stage == "benchmark":
    from dinov3_source import DINOV3
    counts, maps = cross_validate(BENCHMARK_ARMS, {"v2": DINOV2, "v3": DINOV3}, full_maps=FIGURE_IMAGES, log=log)
    counts = counts[~counts.arm.str.startswith("rule: ")]
else:
    raise SystemExit("usage: run_cv.py library|benchmark")
counts.to_csv(f"{HERE}/counts_{stage}.csv", index=False)
np.savez_compressed(f"{HERE}/maps_{stage}.npz", **{"|".join(k): v for k, v in maps.items()})
log(f"saved counts_{stage}.csv ({len(counts)} rows) and maps_{stage}.npz ({len(maps)} maps)")
