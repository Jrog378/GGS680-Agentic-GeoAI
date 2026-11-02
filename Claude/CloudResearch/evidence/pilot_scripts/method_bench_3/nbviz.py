"""Plot helpers for the method-bench-3 notebooks. They only LOAD cached outputs (nb_cache.py, bench3_numbers.json,
bench3_kept_roads.csv) and plot; nothing heavy is recomputed. Images are shown at half resolution."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

HERE = Path(__file__).resolve().parent
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache")
NB = BIG / "nb"
SEEDS = [662] + list(range(1, 21))
KEPT_ALIAS = {"production": "production (refit)", "PUL": "production (refit)", "PULb binned c": "production (refit)"}
DS = 2                                           # display downsampling

# road outcome colours: not assessed, correct dry, correct flooded, false flood, missed flood
OUTCOME = {0: ("not assessed", "#9e9e9e"), 1: ("correct: not flooded", "#1b9e77"), 2: ("correct: flooded", "#2c7fb8"),
           3: ("false flood call", "#d7301f"), 4: ("missed flood", "#fdae61")}


def numbers(phase="G"):
    f = HERE / ("bench3_numbers.json" if phase == "G" else "bench3r_numbers.json")
    return json.loads(f.read_text())


def load(phase, tid):
    z = np.load(NB / f"{phase}_{tid}.npz")
    d = {k: z[k] for k in z.files}
    d["roads"] = pd.read_csv(NB / f"{phase}_{tid}_roads.csv")
    return d


def kept_table(phase="G"):
    fg, fr = HERE / "bench3_kept_roads.csv", HERE / "bench3r_kept_roads.csv"
    g = pd.read_csv(fg) if fg.exists() else None
    if phase == "G" or not fr.exists():
        return g
    r = pd.read_csv(fr)
    if g is not None:
        for c in g.columns:
            if c not in r.columns:
                r[c] = g[c].to_numpy()
    return r


def _ds(x):
    return x[::DS, ::DS]


def _show(ax, img, title, cmap="gray", vmin=0, vmax=255):
    ax.imshow(_ds(img), cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_title(title, fontsize=8)
    ax.axis("off")


def panel_images(d, arms, title=""):
    """Before, after and each arm's output side by side (grey), with C0 first."""
    items = [("before (clear, pre-storm)", d["before"]), ("after (as is)", d["after"]), ("C0 (current correction)", d["C0"])]
    items += [(a, d[f"img|{a}"]) for a in arms if f"img|{a}" in d]
    n = len(items)
    cols = min(n, 5)
    rows = int(np.ceil(n / cols))
    fig, ax = plt.subplots(rows, cols, figsize=(3.1 * cols, 3.1 * rows), squeeze=False)
    for k, (t, im) in enumerate(items):
        _show(ax.flat[k], im, t)
    for k in range(n, rows * cols):
        ax.flat[k].axis("off")
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    plt.show()


def panel_t(d, arms):
    """Transmission t of C0 and each correction (1 = untouched, dark = strong correction)."""
    items = [("t of C0", d["t_C0"])] + [(f"t of {a}", d[f"t|{a}"]) for a in arms if f"t|{a}" in d]
    fig, ax = plt.subplots(1, len(items), figsize=(2.6 * len(items), 2.8), squeeze=False)
    for k, (t, im) in enumerate(items):
        _show(ax[0, k], im, t, cmap="viridis")
    fig.tight_layout()
    plt.show()


def panel_masks(d, keys, labels=None):
    """The after image with each gate mask in red; the share of valid pixels flagged in the title."""
    v = d["valid"]
    fig, ax = plt.subplots(1, len(keys), figsize=(2.9 * len(keys), 3.0), squeeze=False)
    for k, key in enumerate(keys):
        m = d.get(f"mask|{key}")
        a = ax[0, k]
        a.imshow(_ds(d["after"]), cmap="gray", vmin=0, vmax=255)
        if m is not None:
            a.imshow(_ds(np.ma.masked_where(~m, m.astype(float))), cmap=ListedColormap(["#ff2d2d"]), alpha=0.45,
                     vmin=0, vmax=1)
            share = 100 * m[v].mean()
        else:
            share = float("nan")
        a.set_title(f"{(labels or {}).get(key, key)}: {share:.1f}%", fontsize=8)
        a.axis("off")
    fig.tight_layout()
    plt.show()


def panel_noaa(d, arms):
    """NOAA aerial view (tone-matched grey), and |image - NOAA| inside the Ida score mask for as is, C0 and the arms.
    The number in each title is the mean |difference| over C0's thin-cloud pixels (score & gate & not opaque)."""
    if "noaa" not in d:
        print("No NOAA view for this tile (it is not among the Ida prep tiles).")
        return
    s = d["noaa_score"]
    thin = s & d["c0_gate"] & ~d["c0_opaque"]
    noaa = d["noaa"].astype(float)
    items = [("as is", d["after"]), ("C0", d["C0"])] + [(a, d[f"img|{a}"]) for a in arms if f"img|{a}" in d]
    n = len(items) + 1
    fig, ax = plt.subplots(1, n, figsize=(2.7 * n, 3.0), squeeze=False)
    _show(ax[0, 0], d["noaa"], "NOAA aerial (grey)")
    for k, (t, im) in enumerate(items, 1):
        diff = np.where(s, np.abs(im.astype(float) - noaa), np.nan)
        val = np.nanmean(diff[thin]) if thin.sum() >= 50 else float("nan")
        _show(ax[0, k], diff, f"|{t} - NOAA|\nthin mean {val:.1f}", cmap="magma", vmin=0, vmax=120)
    fig.tight_layout()
    plt.show()


def outcome(call, label, kept):
    if not kept or call < 0:
        return 0
    if call == label:
        return 2 if label == 1 else 1
    return 3 if call == 1 else 4


def panel_calls(d, arms, kept=None, tid=None, phase="G"):
    """Flood calls at seed 662 against the published labels, drawn on the road strips (grey = not assessed by that
    arm's gate). Below each map: the share of the 21 seeds that call each road flooded is in the road table."""
    roads = d["roads"]
    strip = d["strip"]
    fig, ax = plt.subplots(1, len(arms), figsize=(3.1 * len(arms), 3.3), squeeze=False)
    cmap = ListedColormap([OUTCOME[k][1] for k in range(5)])
    for k, arm in enumerate(arms):
        lut = np.full(int(strip.max()) + 1, -1)
        for _, r in roads.iterrows():
            c = r.get(f"call662|{arm}", np.nan)
            if np.isnan(c):
                continue
            kp = True
            kc = KEPT_ALIAS.get(arm, arm)
            if kept is not None and kc in kept.columns:
                kp = bool(kept[kc].iloc[int(r.road_row)])
            lut[int(r.strip_id)] = outcome(int(c), int(r.flooded), kp)
        o = np.where(strip > 0, lut[strip], -1)
        a = ax[0, k]
        a.imshow(_ds(d["after"]), cmap="gray", vmin=0, vmax=255)
        a.imshow(_ds(np.ma.masked_where(o < 0, o)), cmap=cmap, vmin=-0.5, vmax=4.5, interpolation="nearest")
        a.set_title(arm[:34], fontsize=8)
        a.axis("off")
    handles = [plt.Rectangle((0, 0), 1, 1, color=OUTCOME[k][1]) for k in range(5)]
    fig.legend(handles, [OUTCOME[k][0] for k in range(5)], loc="lower center", ncol=5, fontsize=8)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    plt.show()


def road_table(d, arms, kept=None):
    roads = d["roads"]
    out = roads[["road_id", "flooded"]].copy()
    for a in arms:
        if f"call662|{a}" in roads:
            out[f"{a[:18]} call@662"] = roads[f"call662|{a}"]
            out[f"{a[:18]} flooded share (21 seeds)"] = roads[f"share21|{a}"].round(2)
            kc = KEPT_ALIAS.get(a, a)
            if kept is not None and kc in kept.columns:
                out[f"{a[:18]} assessed"] = [int(kept[kc].iloc[int(i)]) for i in roads.road_row]
    return out


def forest(rows, title, xlabel, ref=0.0):
    """rows: [(label, estimate, lo, hi)]. A forest plot, estimate with its 95% interval."""
    fig, ax = plt.subplots(figsize=(7.5, 0.34 * len(rows) + 1.2))
    for i, (lab, est, lo, hi) in enumerate(rows):
        colour = "#2c7fb8" if lo > ref else ("#d7301f" if hi < ref else "#444444")
        ax.plot([lo, hi], [i, i], color=colour, lw=2)
        ax.plot(est, i, "o", color=colour)
    ax.axvline(ref, color="k", lw=0.8, ls="--")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    plt.show()
