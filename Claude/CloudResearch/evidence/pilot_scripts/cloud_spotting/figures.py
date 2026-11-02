"""Pictures for evidence 12 (preregistered): two HRC_WHU development images chosen by rule (the first barren and the
first vegetation image in hrc_images order) and the SpaceNet 8 thin-cloud tile 2_23_44. Saves PNGs in
CloudResearch/figures/cloud_spotting/."""
import json
import sys

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
FIG = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/figures/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from sn8_cloudref import hrc_image, mask_scores, single_date_masks
from sn8_clouds import _maps, _tile
from sn8_cloudspot import CUT, LIBRARY_ARMS, CloudSpotter, _strip, tile_spot
from sn8_lines import road_band
from sn8_roads import MIN_ROAD_PX

HRC_CREDIT = "HRC_WHU (Li et al. 2019), academic use only"
SN8_CREDIT = "Imagery: Maxar via SpaceNet 8"
OUTCOME = ListedColormap(["limegreen", "red", "dodgerblue"])
chosen = json.load(open(f"{HERE}/choice.json"))["chosen"]


def outcome(ax, grey, pred, truth, title):
    o = np.full(pred.shape, np.nan)
    o[pred & truth], o[pred & ~truth], o[~pred & truth] = 0, 1, 2
    s = mask_scores(pred, truth)
    ax.imshow(grey, cmap="gray", vmin=0, vmax=255)
    ax.imshow(o, cmap=OUTCOME, vmin=0, vmax=2, alpha=0.55, interpolation="nearest")
    ax.set_title(f"{title}\nP {s['precision']:.2f}  R {s['recall']:.2f}  F1 {s['F1']:.2f}", fontsize=10)


def hrc_figures():
    lib, bench = np.load(f"{HERE}/maps_library.npz"), np.load(f"{HERE}/maps_benchmark.npz")
    for name in ("barren_1", "vegetation_1"):
        im = hrc_image(name)
        g, truth = im["grey"], im["cloud"]
        fig, axes = plt.subplots(1, 5, figsize=(27, 4.6))
        axes[0].imshow(g, cmap="gray", vmin=0, vmax=255)
        axes[0].set_title(f"{name} (grey, what every tool reads)", fontsize=10)
        axes[1].imshow(g, cmap="gray", vmin=0, vmax=255)
        axes[1].imshow(np.ma.masked_where(~truth, truth), cmap=ListedColormap(["orange"]), alpha=0.5)
        axes[1].set_title(f"expert cloud mask: {100 * truth.mean():.0f}% of the image", fontsize=10)
        outcome(axes[2], g, single_date_masks(g)["dark"], truth, "dark rule (production, no learning)")
        outcome(axes[3], g, bench[f"{name}|DINOv3|random forest"] >= 255 * CUT, truth,
                "DINOv3 alone (benchmark, research only), held out")
        outcome(axes[4], g, lib[f"{name}|{chosen}|random forest"] >= 255 * CUT, truth,
                f"chosen library spotter: {chosen}, held out")
        for ax in axes:
            ax.axis("off")
        fig.legend(handles=[Patch(color="limegreen", label="cloud found"), Patch(color="red", label="false alarm"),
                            Patch(color="dodgerblue", label="cloud missed")], loc="lower right", ncol=3, fontsize=9)
        fig.text(0.01, 0.02, HRC_CREDIT + ". Learned maps: each image's held-out fold (5 folds by image), random forest, "
                 "cloud at p >= 0.5.", fontsize=9)
        plt.tight_layout(rect=(0, 0.06, 1, 1))
        fig.savefig(f"{FIG}/hrc_{name}.png", dpi=110)
        plt.close(fig)
        print("saved", f"hrc_{name}.png", flush=True)



def sn8_gate_figure(tid, spotter, out, note=""):
    """Before, after, the dark-rise mask, the spotter mask and what each gate does to the tile's roads."""
    gate = pd.read_csv(f"{HERE}/gate_roads.csv")
    gate = gate[gate.tile_id == tid].reset_index(drop=True)
    _, prob, share = tile_spot(tid, spotter, full=True)
    p, before, after, valid = _tile(tid)
    rise = _maps(p, valid)["masks"]["dark rise"]
    spot = np.nan_to_num(prob, nan=0) >= CUT
    strip, roads, n, centre_px = _strip(tid, p, valid, road_band())
    kept = [k for k in range(n) if centre_px[k] >= MIN_ROAD_PX]
    assert len(kept) == len(gate) and [roads[k + 1]["road_id"] for k in kept] == gate.road_id.tolist()
    gp, gs = gate.filter(like="call: production").iloc[:, 0] >= 0, gate.filter(like="call: spotter").iloc[:, 0] >= 0
    status = np.where(gp & gs, 0, np.where(~gp & ~gs, 1, np.where(~gp, 2, 3)))
    road_map = np.full(strip.shape, np.nan)
    for j, k in enumerate(kept):
        road_map[strip == k + 1] = status[j]
    fig, axes = plt.subplots(1, 5, figsize=(28, 6.4))
    for ax, img, title in ((axes[0], before, f"{tid} before (grey)"), (axes[1], after, "after (grey)")):
        ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
        ax.set_title(title, fontsize=11)
    for ax, m, title in ((axes[2], rise, f"production road rule's mask: dark rise ({100 * rise[valid].mean():.0f}% of tile)"),
                         (axes[3], spot, f"chosen spotter: {chosen} ({100 * spot[valid].mean():.0f}% of tile)")):
        ax.imshow(np.where(valid, after, 0), cmap="gray", vmin=0, vmax=255)
        ax.imshow(np.ma.masked_where(~m, m), cmap=ListedColormap(["orange"]), alpha=0.45)
        ax.set_title(title, fontsize=11)
    axes[4].imshow(np.where(valid, after, 0), cmap="gray", vmin=0, vmax=255)
    axes[4].imshow(road_map, cmap=ListedColormap(["cyan", "red", "orange", "magenta"]), vmin=0, vmax=3,
                   interpolation="nearest")
    axes[4].set_title("roads: what each gate does", fontsize=11)
    axes[4].legend(handles=[Patch(color="cyan", label="kept by both"), Patch(color="red", label="set aside by both"),
                            Patch(color="orange", label="set aside by production only"),
                            Patch(color="magenta", label="set aside by spotter only")], loc="lower left", fontsize=9)
    for ax in axes:
        ax.axis("off")
    fig.text(0.01, 0.02, SN8_CREDIT + f". Spotter trained on HRC_WHU (Li et al. 2019), academic use only; cloud at "
             f"p >= {CUT}. A road is set aside when >= 20% of its strip is under the mask (tile rule applies to both). {note}",
             fontsize=9)
    plt.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print("saved", out, flush=True)


if __name__ == "__main__":
    hrc_figures()
    sn8_gate_figure("2_23_44", CloudSpotter(LIBRARY_ARMS[chosen]).fit(), f"{FIG}/sn8_2_23_44_gates.png")
