"""Figures for evaluate_pipeline_factorial.py (preregistered: one chart of the 16 arms, mean shared-road accuracy over
the fold seeds with the seed spread; one chart of the main effects). Reads pipeline_factorial_numbers.json and
pipeline_factorial_seeds.csv from `src` (default: this folder) and writes PNGs to `dst` (default:
CloudResearch/figures/pipeline_factorial/)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parents[1] / "figures" / "pipeline_factorial"
DST.mkdir(parents=True, exist_ok=True)
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
GATE_COLOUR = {"a": "#2a78d6", "b": "#eb6834"}          # categorical slots 1 and 2 (reference palette)
GATE_LABEL = {"a": "production gate (dark-rise road rule)", "b": "spotter gate (bright + texture + DINOv2)"}
CUE = {"raw": "no de-hazing", "td": "two-date", "he": "He 2011", "both": "both cues + raw"}
FEAT = {"prod": "production features", "vec": "+ DINOv2 vector"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK, "text.color": INK, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE})

num = json.load(open(SRC / "pipeline_factorial_numbers.json"))
seeds = pd.read_csv(SRC / "pipeline_factorial_seeds.csv")
summ = num["across seeds (shared roads)"]
n_seeds = len(num["fold seeds"])
shared = num["roads"]["shared"]


def label(arm):
    g, c, f = arm.split("·")
    return f"{'spotter' if g == 'b' else 'production'} gate · {CUE[c]} · {FEAT[f]}"


def tidy(ax):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


# --- figure 1: the 16 arms -------------------------------------------------------------------------------------------
order = sorted(summ, key=lambda a: summ[a]["shared accuracy mean"])
fig, ax = plt.subplots(figsize=(11.5, 7.8))
prod_mean = 100 * summ["a·raw·prod"]["shared accuracy mean"]
ax.axvline(prod_mean, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
for yi, arm in enumerate(order):
    g = arm[0]
    s = summ[arm]
    acc = 100 * seeds.loc[seeds.arm == arm, "shared accuracy"].to_numpy()
    ax.plot([100 * s["shared accuracy min"], 100 * s["shared accuracy max"]], [yi, yi], color=GATE_COLOUR[g],
            linewidth=2, alpha=0.45, solid_capstyle="round", zorder=2)
    ax.scatter(acc, np.full(len(acc), yi) + np.linspace(-0.18, 0.18, len(acc)), s=9, color=GATE_COLOUR[g], alpha=0.45,
               linewidths=0, zorder=3)
    ax.scatter([100 * s["shared accuracy mean"]], [yi], s=70, color=GATE_COLOUR[g], edgecolors=SURFACE, linewidths=2,
               zorder=5)
    ax.scatter([100 * s["shared accuracy, seed 662"]], [yi], s=46, marker="D", facecolors="none",
               edgecolors=INK, linewidths=1.1, zorder=6)
    ax.text(100 * s["shared accuracy max"] + 0.15, yi,
            f"{100 * s['shared accuracy mean']:.1f}   beats production in {s['seeds above production']}/{n_seeds}"
            if arm != "a·raw·prod" else f"{100 * s['shared accuracy mean']:.1f}   production",
            va="center", ha="left", fontsize=8.5, color=INK2, zorder=7,
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.6))
ax.set_yticks(range(len(order)))
ax.set_yticklabels([label(a) for a in order])
for t, arm in zip(ax.get_yticklabels(), order):
    t.set_color(INK)
xmin = 100 * min(summ[a]["shared accuracy min"] for a in summ) - 0.5
xmax = 100 * max(summ[a]["shared accuracy max"] for a in summ) + 4.5
ax.set_xlim(xmin, xmax)
ax.set_xlabel(f"accuracy on the {shared} roads both gates keep (%)")
tidy(ax)
handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=8, color=GATE_COLOUR[g], label=GATE_LABEL[g])
           for g in ("a", "b")]
handles += [plt.Line2D([], [], marker="o", linestyle="", markersize=4, color=INK2, alpha=0.5,
                       label=f"one fold seed (bar = min to max, {n_seeds} seeds)"),
            plt.Line2D([], [], marker="D", linestyle="", markersize=6, markerfacecolor="none", color=INK,
                       label="primary fold seed 662"),
            plt.Line2D([], [], color=INK2, linestyle=(0, (4, 3)), label="production's mean")]
ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=8.5)
ax.set_title(f"16 pipeline arms: mean accuracy over {n_seeds} fold seeds (large dot), development roads only",
             loc="left", fontsize=11.5, color=INK)
fig.tight_layout()
fig.savefig(DST / "arms_shared_accuracy.png", dpi=170)
plt.close(fig)

# --- figure 2: main effects and the same effects within each gate -----------------------------------------------------
eff = num["contrasts"]["shared roads (accuracy)"]
acc = seeds.pivot(index="fold seed", columns="arm", values="shared accuracy")   # per-seed contrasts recomputed here


def contrast_values(terms):
    v = sum(w * acc[a] for a, w in terms.items())
    return 100 * v.to_numpy()


def avg_terms(pairs):
    out = {}
    for plus, minus in pairs:
        out[plus] = out.get(plus, 0) + 1 / len(pairs)
        out[minus] = out.get(minus, 0) - 1 / len(pairs)
    return out


G, C, F = ("a", "b"), ("raw", "td", "he", "both"), ("prod", "vec")
main = [("spotter gate (vs production gate)", "main: spotter gate (b - a)",
         avg_terms([(f"b·{c}·{f}", f"a·{c}·{f}") for c in C for f in F]))]
for k in ("td", "he", "both"):
    main.append((f"{CUE[k]} (vs no de-hazing)", f"main: {dict(td='two-date', he='He 2011', both='both cues + raw')[k]} (- raw)",
                 avg_terms([(f"{g}·{k}·{f}", f"{g}·raw·{f}") for g in G for f in F])))
main.append(("DINOv2 vector (vs production features)", "main: DINOv2 vector (vec - prod)",
             avg_terms([(f"{g}·{c}·vec", f"{g}·{c}·prod") for g in G for c in C])))
within = []
for title, key, _ in main[1:]:
    rows = []
    for g in G:
        if "vector" in title:
            terms = avg_terms([(f"{g}·{c}·vec", f"{g}·{c}·prod") for c in C])
            k2 = f"within gate {g}: DINOv2 vector"
        else:
            k = [x for x in ("td", "he", "both") if CUE[x] in title][0]
            terms = avg_terms([(f"{g}·{k}·{f}", f"{g}·raw·{f}") for f in F])
            k2 = f"within gate {g}: {dict(td='two-date', he='He 2011', both='both cues + raw')[k]} (- raw)"
        rows.append((g, k2, terms))
    within.append((title, rows))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 10.5), sharex=True, gridspec_kw={"height_ratios": [5, 8.4]})
fig.subplots_adjust(left=0.31, right=0.76, top=0.92, bottom=0.13, hspace=0.28)
for ax in (ax1, ax2):
    ax.axvline(0, color=INK2, linewidth=1)
for yi, (title, key, terms) in enumerate(main[::-1]):
    v = contrast_values(terms)
    e = eff[key]
    assert abs(v.mean() - 100 * e["seed mean"]) < 1e-3, key
    lo, hi = (100 * x for x in e["seed-averaged 95% CI"])
    ax1.plot([lo, hi], [yi, yi], color=INK2, linewidth=6, alpha=0.22, solid_capstyle="round", zorder=2)
    ax1.scatter(v, np.full(len(v), yi) + np.linspace(-0.22, 0.22, len(v)), s=10, color=INK2, alpha=0.55,
                linewidths=0, zorder=3)
    ax1.scatter([v.mean()], [yi], s=70, color=INK, edgecolors=SURFACE, linewidths=2, zorder=5)
    ax1.text(1.02, yi, f"{v.mean():+.2f} [{lo:+.2f}, {hi:+.2f}]\n{e['seeds > 0']} of {len(v)} seeds > 0",
             transform=ax1.get_yaxis_transform(), va="center", fontsize=8.5, color=INK2)
ax1.set_yticks(range(len(main)))
ax1.set_yticklabels([m[0] for m in main[::-1]])
ax1.set_title("Main effects: each option's gain over the baseline option, averaged over the other two stages",
              loc="left", fontsize=10.5)
tidy(ax1)
ys, ylab, yi = [], [], 0
for title, rows in within[::-1]:
    for g, k2, terms in rows[::-1]:
        v = contrast_values(terms)
        e = eff[k2]
        assert abs(v.mean() - 100 * e["seed mean"]) < 1e-3, k2
        lo, hi = (100 * x for x in e["seed-averaged 95% CI"])
        ax2.plot([lo, hi], [yi, yi], color=GATE_COLOUR[g], linewidth=6, alpha=0.28, solid_capstyle="round", zorder=2)
        ax2.scatter(v, np.full(len(v), yi) + np.linspace(-0.16, 0.16, len(v)), s=9, color=GATE_COLOUR[g],
                    alpha=0.55, linewidths=0, zorder=3)
        ax2.scatter([v.mean()], [yi], s=60, color=GATE_COLOUR[g], edgecolors=SURFACE, linewidths=2, zorder=5)
        ax2.text(1.02, yi, f"{v.mean():+.2f} [{lo:+.2f}, {hi:+.2f}]", transform=ax2.get_yaxis_transform(),
                 va="center", fontsize=8.5, color=INK2)
        ys.append(yi)
        ylab.append(f"{title.split(' (')[0]}, {'spotter' if g == 'b' else 'production'} gate")
        yi += 1
    yi += 0.7
ax2.set_yticks(ys)
ax2.set_yticklabels(ylab)
ax2.set_title("The same gains within each gate (the gap between a pair is the interaction)", loc="left", fontsize=10.5)
ax2.set_xlabel(f"accuracy gain on the {shared} shared roads (points)")
tidy(ax2)
handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=8, color=INK, label="mean over the fold seeds"),
           plt.Line2D([], [], marker="o", linestyle="", markersize=4, color=INK2, alpha=0.55, label="one fold seed"),
           plt.Line2D([], [], color=INK2, linewidth=6, alpha=0.3,
                      label="95% interval (seed-averaged, tiles resampled)")]
handles += [plt.Line2D([], [], marker="o", linestyle="", markersize=7, color=GATE_COLOUR[g], label=GATE_LABEL[g])
            for g in G]
fig.legend(handles=handles, loc="lower left", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.02, 0.005))
fig.suptitle(f"What each tool adds: {shared} shared roads, {n_seeds} fold seeds (development roads only)", x=0.02,
             ha="left", fontsize=12)
fig.savefig(DST / "main_effects.png", dpi=170)
plt.close(fig)
print("saved", DST / "arms_shared_accuracy.png", DST / "main_effects.png")

# --- figure 3 (added beyond the plan): the cloud groups, every arm, mean over the fold seeds --------------------------
groups = num["(iii) cloud groups"]
fig, axes = plt.subplots(1, 4, figsize=(15, 6.4), sharey=True)
fig.subplots_adjust(left=0.24, right=0.99, top=0.83, bottom=0.17, wspace=0.12)
arms = list(summ)[::-1]
what = {"found": "share called flooded (higher is better)", "called flooded": "share called flooded (labels untrusted)",
        "right": "share right", }
for ax, (gname, gr) in zip(axes, groups.items()):
    for yi, arm in enumerate(arms):
        r = gr["arms"][arm]
        g = arm[0]
        ax.plot([100 * r["seed min share"], 100 * r["seed max share"]], [yi, yi], color=GATE_COLOUR[g], linewidth=2,
                alpha=0.45, solid_capstyle="round", zorder=2)
        ax.scatter([100 * r["seed mean share"]], [yi], s=46, color=GATE_COLOUR[g], edgecolors=SURFACE, linewidths=1.5,
                   zorder=4)
    base = 100 * gr["arms"]["a·raw·prod"]["seed mean share"]
    ax.axvline(base, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    short = {"trusted flooded roads under thin cloud": "trusted flooded, thin cloud",
             "dry-labelled roads under thin cloud (labels untrusted)": "dry-labelled, thin cloud",
             "control: assessable roads on the same tiles": "control: clear roads, same tiles",
             "clear-sky benchmark: assessable flooded roads on the same tiles": "clear-sky benchmark: flooded,\n"
                                                                                 "clear, same tiles"}[gname]
    ax.set_title(f"{short}\n{gr['roads']} roads, {gr['tiles']} tiles", loc="left", fontsize=9.5)
    ax.set_xlabel(what[gr["measure"]] + " (%)", fontsize=8.5)
    tidy(ax)
axes[0].set_yticks(range(len(arms)))
axes[0].set_yticklabels([label(a) for a in arms], fontsize=8.5)
handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=7, color=GATE_COLOUR[g], label=GATE_LABEL[g])
           for g in ("a", "b")]
handles += [plt.Line2D([], [], color=INK2, linewidth=2, alpha=0.45, label=f"min to max over {n_seeds} fold seeds"),
            plt.Line2D([], [], color=INK2, linestyle=(0, (4, 3)), label="production's mean")]
fig.legend(handles=handles, loc="lower left", ncol=4, frameon=False, fontsize=8.5, bbox_to_anchor=(0.01, 0.0))
fig.suptitle("Cloud groups (production's road rule defines them): mean over the fold seeds; under the production gate "
             "these thin-cloud roads are 'cannot assess', so their calls show what it would say if forced",
             x=0.01, ha="left", fontsize=10.5)
fig.savefig(DST / "cloud_groups.png", dpi=170)
plt.close(fig)
print("saved", DST / "cloud_groups.png")
