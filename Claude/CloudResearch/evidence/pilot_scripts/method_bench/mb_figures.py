"""Figures for evidence 22 (numbers with pictures). Reads the bench's saved outputs; recomputes only the corrected images
of ONE development tile (no DINOv2 tokens). Writes to figures/method_bench/.
  B1_flood_gains.png    21-seed flood-call gain vs production per arm and per combination (block-bootstrap 95% CI)
  B2_ida_primary.png    feature distance to NOAA vs C0 per correction arm, thin cloud and ring, + guard grey change
  B3_hrc_detection.png  paired F1 vs D0 per detection arm on HRC_WHU (image-resampled 95% CI)
  B4_tile_<id>.png      one tile: before, after, C0, C5a gamma 1.8, C1 He 2013, C3b Poisson, NOAA reference, and
                        feature-distance maps (as is, C0, C1) with the thin-cloud gate outlined
    nice -n 10 python3 -I mb_figures.py [tile]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY, GREEN = "#2a78d6", "#eb6834", "#8a8a85", "#2f9e5b"
CREDIT = ("Satellite: SpaceNet 8 / Maxar (CC BY-SA 4.0). Aerial: NOAA NGS Hurricane Ida emergency response imagery "
          "(public domain). HRC_WHU: Li et al. 2019 (academic use).")


def forest(ax, labels, mid, lo, hi, colours, xlabel, title):
    y = np.arange(len(labels))[::-1]
    for yi, m, a, b, c in zip(y, mid, lo, hi, colours):
        ax.plot([a, b], [yi, yi], color=c, lw=2)
        ax.plot(m, yi, "o", color=c, ms=6)
    ax.axvline(0, color=GREY, lw=1)
    ax.set_yticks(y, labels, fontsize=9)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=11)
    ax.grid(axis="x", color="#e8e8e4", lw=0.5)


def colour_for(lo, hi, good_positive=True):
    if (lo > 0 and good_positive) or (hi < 0 and not good_positive):
        return GREEN
    if (hi < 0 and good_positive) or (lo > 0 and not good_positive):
        return ORANGE
    return BLUE


def b1():
    n = json.loads((C.HERE / "flood_numbers.json").read_text())
    rows = [(k, v) for k, v in n["seeds"].items()] + [(k.replace("COMBO ", "combo: "), v) for k, v in n["combo"].items()]
    labels = [k for k, _ in rows]
    mid = [100 * v["mean_gain"] for _, v in rows]
    lo = [100 * v["ci"][0] for _, v in rows]
    hi = [100 * v["ci"][1] for _, v in rows]
    fig, ax = plt.subplots(figsize=(11, 7.5))
    forest(ax, labels, mid, lo, hi, [colour_for(a, b) for a, b in zip(lo, hi)],
           "accuracy gain vs production (points; 21-seed mean, 95% block CI)",
           "Flood calls, spatial folds S (798 roads)")
    screened_out = [k for k in n["screen"] if k not in n["seeds"]]
    fig.text(0.01, 0.01, "Not run at 21 seeds (seed-662 gain < -0.5 points): " + ", ".join(screened_out) +
             ". Green = interval above 0, orange = below 0, blue = includes 0.", fontsize=8, color=GREY, wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(C.FIG / "B1_flood_gains.png", dpi=120)
    plt.close(fig)


def b2():
    n = json.loads((C.HERE / "ida_numbers.json").read_text())
    arms = [a for a in n["primary_vs_C0"] if a != "as is"] + ["as is"]
    g = n["guard_grey_change_mean"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5), sharey=True)
    for ax, key, title in ((axes[0], "primary_vs_C0", "thin cloud (inside C0's gate, t >= 0.2)"),
                           (axes[1], "primary_ring_vs_C0", "ring (0-40 m outside the gate)")):
        r = [n[key][a] for a in arms]
        lab = [f"{a}  (guard grey {g.get(a, 0):.2f})" for a in arms]
        forest(ax, lab, [x["mean_diff"] for x in r], [x["ci"][0] for x in r], [x["ci"][1] for x in r],
               [colour_for(x["ci"][0], x["ci"][1], good_positive=False) for x in r],
               "Δ DINOv2 feature distance to NOAA vs C0 (per tile; < 0 = closer)", title)
    fig.suptitle(f"Correction arms against the NOAA aerial reference ({n['primary_vs_C0']['C0' if 'C0' in n['primary_vs_C0'] else arms[0]]['tiles']} tiles)",
                 fontsize=11)
    fig.text(0.01, 0.01, "Green = closer to NOAA than C0 (interval below 0); orange = further. Guard grey = mean "
             "|arm - as is| on clear ground (plan limit 1 grey level). " + CREDIT, fontsize=8, color=GREY, wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(C.FIG / "B2_ida_primary.png", dpi=120)
    plt.close(fig)


def b3():
    h = json.loads((C.HERE / "hrc_numbers.json").read_text())
    rows = [r for r in h["paired_vs_D0"] if r["scope"] == "all"]
    lab = [r["a"] for r in rows]
    mid = [r["F1 a - b"] for r in rows]
    lo = [r["ci_low"] for r in rows]
    hi = [r["ci_high"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    forest(ax, lab, mid, lo, hi, [colour_for(a, b) for a, b in zip(lo, hi)],
           "pixel F1 minus D0 (pooled; 95% CI from 2,000 image resamples within land cover)",
           "Detection arms on HRC_WHU, 120 development images (D0 F1 0.868)")
    fig.text(0.01, 0.01, CREDIT, fontsize=8, color=GREY)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(C.FIG / "B3_hrc_detection.png", dpi=120)
    plt.close(fig)


def b4(tile_id):
    from scipy import ndimage as ndi
    from sn8_clouds import _tile
    from sn8_refhaze import dark_reference_dehaze
    import c1_he2013, c3_seam, c5_gamma_band
    from sn8_cloudedge import edge_parts
    C.dev_guard_tiles([tile_id])
    p, before, after, valid = _tile(tile_id)
    base = dark_reference_dehaze(before, after, valid)
    parts = edge_parts(before, after, valid, base)
    imgs = {"C0 (current two-date)": base["corrected"],
            "C5a gamma 1.8": c5_gamma_band.correct_gamma(before, after, valid, 1.8)["corrected"],
            "C1 He 2013": c1_he2013.correct(before, after, valid, parts)["corrected"],
            "C3b Poisson seam": c3_seam.correct_poisson(before, after, valid, parts)["corrected"]}
    z = np.load(C.IDA_BIG / "prep" / f"{tile_id}.npz", allow_pickle=True)
    s = z["score"]
    noaa = z["noaa"]
    fm = np.load(C.BIG / "ida" / f"{tile_id}_feat.npz")
    gate = base["gate"]
    thin = s & gate & ~base["opaque"]
    lo, hi = np.percentile(noaa[s], [1, 99])
    fig, axes = plt.subplots(2, 5, figsize=(26, 11))
    ax = axes.ravel()
    panels = [("before (pre-storm)", before), ("after, as is", after)] + list(imgs.items()) + [("NOAA aerial (aligned, tone-matched)", noaa)]
    for a_, (t, im) in zip(ax[:7], panels):
        a_.imshow(np.where(s, im, lo), cmap="gray", vmin=lo, vmax=hi)
        if t != "before (pre-storm)":
            a_.contour(thin.astype(float), levels=[0.5], colors=["#eda100"], linewidths=0.8)
        a_.set_title(t, fontsize=10)
        a_.axis("off")
    vmax = 1.0
    for a_, key, name in ((ax[7], "as_is", "as is"), (ax[8], "C0", "C0"), (ax[9], "C1_He_2013", "C1 He 2013")):
        d = fm[key].astype(np.float32)
        m = d[thin].mean() if thin.any() else np.nan
        im = a_.imshow(np.where(s, d, np.nan), cmap="Blues", vmin=0, vmax=vmax)
        a_.contour(thin.astype(float), levels=[0.5], colors=["#eda100"], linewidths=0.8)
        a_.set_title(f"feature distance to NOAA, {name}; thin mean {m:.3f}", fontsize=10)
        a_.axis("off")
        plt.colorbar(im, ax=a_, fraction=0.04)
    fig.suptitle(f"{tile_id}: correction arms (yellow outline = C0's thin-cloud gate inside the NOAA score mask). "
                 "All grey panels share NOAA's display range.", fontsize=11)
    fig.text(0.5, 0.01, "Feature maps are zero outside the DINOv2 windows that hold thin or ring pixels (only those were "
             "computed). " + CREDIT, ha="center", fontsize=8, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(C.FIG / f"B4_tile_{tile_id}.png", dpi=80)
    plt.close(fig)


def main():
    C.FIG.mkdir(parents=True, exist_ok=True)
    h0 = C.registry_hash()
    b1(); b2(); b3()
    b4(sys.argv[1] if len(sys.argv) > 1 else "2_21_42")
    assert C.registry_hash() == h0
    print("figures written to", C.FIG)


if __name__ == "__main__":
    main()
