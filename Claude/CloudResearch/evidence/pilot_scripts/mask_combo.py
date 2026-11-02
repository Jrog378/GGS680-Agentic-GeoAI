"""Both cloud masks together on HRC_WHU development images (Justin, 2026-10-25: "why cant we use both bright rule and
dark channel since they are flipped with recall and precision"). Written before running, 23:38 EDT. Primary: "grow",
the bright rule's cores as seeds, kept with every dark-channel blob (8-connected, of bright | dark) that touches one.
Also scored: either (OR) and both (AND). No settings are tuned here: the bright rule and the dark-channel cut are the
ones learned on SpaceNet 8. 120 development images only (the 30 test images are sealed). Pooled pixel scores, as on
slide 9."""
import sys
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
from multiprocessing import Pool
import numpy as np, pandas as pd
from scipy import ndimage as ndi
from sn8_cloudref import hrc_images, hrc_image, single_date_masks, mask_scores, pooled_scores


def one(name):
    im = hrc_image(name)
    m = single_date_masks(im["grey"])
    b, d = m["bright"], m["dark"]
    lab, n = ndi.label(b | d, structure=np.ones((3, 3)))
    keep = np.zeros(n + 1, bool); keep[np.unique(lab[b])] = True; keep[0] = False
    masks = {"bright": b, "dark": d, "either (OR)": b | d, "both (AND)": b & d, "grow: bright cores + dark blobs": keep[lab]}
    return [{"image": name, "type": im["type"], "mask": k, **mask_scores(v, im["cloud"])} for k, v in masks.items()]


if __name__ == "__main__":
    names = hrc_images("train")
    assert len(names) == 120, len(names)
    with Pool() as pool:
        rows = [r for rs in pool.map(one, names) for r in rs]
    t = pd.DataFrame(rows)
    t.to_csv("mask_combo.csv", index=False)
    print(pooled_scores(t).to_string(index=False))
    print(pooled_scores(t, ("mask", "type")).pivot(index="type", columns="mask", values="F1").to_string())
