"""Figures for evidence 23 (method bench 2; numbers paired with pictures). Reads the finished run's outputs
(bench2_numbers.json, ida_rows_*.csv); recomputes masks and corrected images for 3 development tiles only (no DINOv2
tokens, no GPU, single process). Nothing is scored here and no bench stage is rerun. Writes to figures/method_bench_2/.

  F1_ida_primary.png        DINOv2 feature distance to NOAA vs C0 per arm (54 tiles) + grey error under thin cloud
  F2_flood_seeds.png        21-seed flood-call gain vs production and vs C0 (block-bootstrap 95% intervals)
  F3_gates_ida.png          gate masks on 3 Ida tiles against the NOAA disagreement (hit / false alarm / missed)
  F4_before_after_<t>.png   before, as is, C0, N4 Song ridge, A1 Chavez k=0, NOAA, and |image - NOAA| maps

    cd evidence/pilot_scripts/method_bench_2
    OMP_NUM_THREADS=2 nice -n 10 python3 -I b2_figures.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_common as B

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, ORANGE, GREY, GREEN = "#2a78d6", "#eb6834", "#8a8a85", "#2f9e5b"
CREDIT = ("Satellite: SpaceNet 8 / Maxar (CC BY-SA 4.0). Aerial: NOAA NGS Hurricane Ida emergency response imagery "
          "(public domain).")
NUM = json.loads((B.HERE / "bench2_numbers.json").read_text())
GATE_TILES = ("0_13_5", "2_21_42", "2_23_44")      # largest and 2nd-largest thin area (no labels used) + smoke tile
PANEL_TILES = ("0_13_5", "2_21_42")
TOP2 = ("N4 Song ridge all", "A1 Chavez k=0.0")    # the only arms closer to NOAA than C0 (primary interval < 0)


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


def f1():
    pri, grey = NUM["ida_primary_vs_C0"], NUM["ida_grey_err_thin_vs_C0"]
    g = NUM["ida_guard_grey_change_mean"]
    arms = [a for a in pri if a != "as is"] + ["as is"]
    fig, axes = plt.subplots(1, 2, figsize=(17, 7.5), gridspec_kw={"width_ratios": [1.25, 1]})
    lab = [f"{a}  ({pri[a]['tiles']} tiles; guard {g.get(a, 0):.2f})" for a in arms]
    r = [pri[a] for a in arms]
    forest(axes[0], lab, [x["mean_diff"] for x in r], [x["ci"][0] for x in r], [x["ci"][1] for x in r],
           [colour_for(x["ci"][0], x["ci"][1], good_positive=False) for x in r],
           "Δ DINOv2 feature distance to NOAA vs C0 (< 0 = closer)", "PRIMARY: thin cloud (C0's gate, t ≥ 0.2)")
    r = [grey[a] for a in arms]
    forest(axes[1], [""] * len(arms), [x["mean_diff"] for x in r], [x["ci"][0] for x in r], [x["ci"][1] for x in r],
           [colour_for(x["ci"][0], x["ci"][1], good_positive=False) for x in r],
           "Δ grey error |arm − NOAA| vs C0 (grey levels; < 0 = closer)",
           "secondary: grey error, thin cloud (73 tiles; G arms fewer)")
    fig.suptitle("Method bench 2: correction arms against the NOAA aerial reference (per-tile pairs with C0; "
                 "95% interval from 3 × 3 tile-block resamples)", fontsize=11)
    fig.text(0.01, 0.01, "Green = closer to NOAA than C0 (interval below 0); orange = further (interval above 0); "
             "blue = includes 0. Primary stopped at its 3-hour budget after 54 of 73 tiles (largest thin area first). "
             "G corr-gate arms are paired only on tiles where their own mask is non-empty. Guard = mean |arm − as is| "
             "on clear ground (C0 1.11). " + CREDIT, fontsize=8, color=GREY, wrap=True)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(B.FIG / "F1_ida_primary.png", dpi=110)
    plt.close(fig)


def f2():
    sd, sc = NUM["seeds"], NUM["screen"]
    arms = list(sd)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.3, 1]})
    lab = [f"{a}  ({sd[a]['seeds_better']} better / {sd[a]['seeds_worse']} worse)" for a in arms]
    mid = [100 * sd[a]["mean_gain"] for a in arms]
    lo = [100 * sd[a]["ci"][0] for a in arms]
    hi = [100 * sd[a]["ci"][1] for a in arms]
    forest(axes[0], lab, mid, lo, hi, [colour_for(a, b) for a, b in zip(lo, hi)],
           "accuracy gain vs production (points; 21-seed mean)", "vs production")
    vc = [a for a in arms if "vs_C0" in sd[a]]
    forest(axes[1], vc, [100 * sd[a]["vs_C0"]["mean_gain"] for a in vc], [100 * sd[a]["vs_C0"]["ci"][0] for a in vc],
           [100 * sd[a]["vs_C0"]["ci"][1] for a in vc],
           [colour_for(100 * sd[a]["vs_C0"]["ci"][0], 100 * sd[a]["vs_C0"]["ci"][1]) for a in vc],
           "accuracy gain vs C0 (points)", "correction arms vs C0")
    out = [f"{a} {100 * sc[a]['paired_shared']['gain']:+.3f}" for a in sc if a not in sd]
    fig.suptitle("Flood calls under spatial folds S, 21 seeds (gate arms: roads both keep; correction arms: 798 roads; "
                 "95% block-bootstrap interval)", fontsize=11)
    fig.text(0.01, 0.01, "Not carried to 21 seeds (seed-662 gain < −0.5 points): " + "; ".join(out) +
             ". Green = interval above 0, orange = below 0, blue = includes 0.", fontsize=8, color=GREY, wrap=True)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    fig.savefig(B.FIG / "F2_flood_seeds.png", dpi=110)
    plt.close(fig)


def _tile_masks(t):
    import g2_lin_bluerise
    import run_bench2 as R
    import run_ida_helpers as H
    from sn8_clouds import _tile
    B.dev_guard_tiles([t])
    p, before, after, valid = _tile(t)
    masks, info = R.masks_for(p, before, after, valid, g2_lin_bluerise.threshold())
    z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
    dis, cut = R._noaa_disagreement(z, after, valid)
    return p, before, after, valid, masks, info, z, dis, cut


def f3():
    gat = pd.read_csv(B.HERE / "ida_rows_gates.csv")
    keys = ("rise", "G1", "G1b", "G1c", "G2")
    names = {"rise": "production dark rise", "G1": "G1 hysteresis", "G1b": "G1b + blob", "G1c": "G1c centred",
             "G2": "G2 blue rise"}
    fig, ax = plt.subplots(len(GATE_TILES), 2 + len(keys), figsize=(30, 4.6 * len(GATE_TILES)))
    for i, t in enumerate(GATE_TILES):
        p, before, after, valid, masks, info, z, dis, cut = _tile_masks(t)
        s = z["score"]
        ax[i, 0].imshow(np.where(s, after, 0), cmap="gray", vmin=0, vmax=255)
        ax[i, 0].set_title(f"{t}: after (satellite), score mask", fontsize=10)
        ax[i, 1].imshow(np.where(s, z["noaa"], 0), cmap="gray", vmin=0, vmax=255)
        ax[i, 1].contour(dis.astype(float), levels=[0.5], colors=[BLUE], linewidths=0.5)
        ax[i, 1].set_title(f"NOAA aerial; blue = |as is − NOAA| > {cut:.0f} ({dis.sum() / max(s.sum(), 1):.1%})",
                           fontsize=10)
        for j, k in enumerate(keys):
            m = masks[k] & s
            rgb = np.stack([np.where(s, after, 0) / 255.0] * 3, -1) * 0.6
            rgb[m & dis] = (0.18, 0.62, 0.36)          # hit: flagged and disagreeing
            rgb[m & ~dis] = (0.92, 0.41, 0.20)         # false alarm: flagged, agrees with NOAA
            rgb[~m & dis] = (0.16, 0.47, 0.84)         # missed: disagreeing, not flagged
            r = gat[(gat.tile_id == t) & (gat["mask"] == k)].iloc[0]
            ax[i, 2 + j].imshow(rgb)
            ax[i, 2 + j].set_title(f"{names[k]}: flags {m.sum() / max(s.sum(), 1):.1%}\nprecision {r.precision:.2f}, "
                                   f"recall {r.recall:.2f}", fontsize=10)
        for a_ in ax[i]:
            a_.axis("off")
    fig.suptitle("Gate masks on Ida tiles against the satellite–NOAA disagreement (green = hit, orange = flagged but "
                 "agrees with NOAA, blue = disagreement not flagged). Disagreement is not a cloud label: it also holds "
                 "0–2 days of real change, parallax and moving objects.", fontsize=12)
    pooled = NUM["ida_gates"]
    fig.text(0.5, 0.005, "Pooled over 132 Ida tiles: " + "; ".join(
        f"{names[k]} precision {pooled[k]['precision_pooled']:.2f}, recall {pooled[k]['recall_pooled']:.2f}"
        for k in keys) + ". " + CREDIT, ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(B.FIG / "F3_gates_ida.png", dpi=60)
    plt.close(fig)


def f4(t):
    import run_bench2 as R
    pri = pd.read_csv(B.HERE / "ida_rows_primary.csv")
    sec = pd.read_csv(B.HERE / "ida_rows_secondary.csv")
    p, before, after, valid, masks, info, z, dis, cut = _tile_masks(t)
    outs = R.arm_outputs(t, p, before, after, valid, masks, only=list(TOP2))
    c0 = outs["C0"]
    s, noaa = z["score"], z["noaa"]
    thin = s & c0["gate"] & ~c0["opaque"]
    imgs = {"as is": np.where(valid, after, 0).astype(np.float32), "C0": c0["corrected"],
            TOP2[0]: outs[TOP2[0]]["corrected"], TOP2[1]: outs[TOP2[1]]["corrected"]}

    def nums(arm):
        f = pri[(pri.tile_id == t) & (pri.arm == arm)].feat
        g = sec[(sec.tile_id == t) & (sec.arm == arm) & (sec.region == "thin")].grey_err
        return (f"feature dist {f.iloc[0]:.3f}" if len(f) and np.isfinite(f.iloc[0]) else "feature dist n/a") + \
               (f", grey err {g.iloc[0]:.1f}" if len(g) else "")

    n4i = outs[TOP2[0]].get("info") or {}
    n4note = f" (slope {n4i['slope']:.3f})" if "slope" in n4i else ""
    if n4i.get("abstain"):
        n4note += f" ABSTAINED: {n4i['abstain']}"
    fig, ax = plt.subplots(2, 6, figsize=(30, 10.5))
    lo, hi = np.percentile(noaa[s], [1, 99])
    panels = [("before (pre-storm)", before, "")] + [(k, v, nums(k)) for k, v in imgs.items()] + \
             [("NOAA aerial (aligned, tone-matched)", noaa, "")]
    for a_, (name, im, txt) in zip(ax[0], panels):
        a_.imshow(np.where(s, im, lo), cmap="gray", vmin=lo, vmax=hi)
        if not name.startswith("before"):
            a_.contour(thin.astype(float), levels=[0.5], colors=["#eda100"], linewidths=0.8)
        a_.set_title(name + (n4note if name == TOP2[0] else "") + ("\n" + txt if txt else ""), fontsize=10)
    for a_, (name, im) in zip(ax[1, 1:5], imgs.items()):
        e = np.where(s, np.abs(im - noaa), np.nan)
        h = a_.imshow(e, cmap="magma", vmin=0, vmax=100)
        a_.contour(thin.astype(float), levels=[0.5], colors=["#9fd3ff"], linewidths=0.6)
        a_.set_title(f"|{name} − NOAA|; thin mean {np.nanmean(e[thin]):.1f}", fontsize=10)
        plt.colorbar(h, ax=a_, fraction=0.04)
    ax[1, 0].imshow(c0["t"] if c0.get("t") is not None else np.zeros_like(after), cmap="viridis", vmin=0, vmax=1)
    ax[1, 0].set_title("C0 transmission t (shared by C0, N4 and A1)", fontsize=10)
    d = np.where(s, imgs[TOP2[0]] - imgs["C0"], np.nan)
    h = ax[1, 5].imshow(d, cmap="RdBu_r", vmin=-60, vmax=60)
    ax[1, 5].set_title("N4 − C0 (grey levels)", fontsize=10)
    plt.colorbar(h, ax=ax[1, 5], fraction=0.04)
    for a_ in ax.ravel():
        a_.axis("off")
    fig.suptitle(f"{t}: the two arms closer to NOAA than C0 on the primary (yellow = C0's thin-cloud pixels inside "
                 "the NOAA score mask). Per-tile feature distance from ida_rows_primary.csv (lower = closer).",
                 fontsize=12)
    fig.text(0.5, 0.01, CREDIT, ha="center", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(B.FIG / f"F4_before_after_{t}.png", dpi=60)
    plt.close(fig)


if __name__ == "__main__":
    h0 = B.registry_hash()
    f1()
    f2()
    f3()
    for t in PANEL_TILES:
        f4(t)
    assert B.registry_hash() == h0, "production.json changed"
    print("figures written to", B.FIG)
