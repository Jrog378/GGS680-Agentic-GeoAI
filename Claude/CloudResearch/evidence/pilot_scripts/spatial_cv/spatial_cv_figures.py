"""Pictures for evidence/14_spatial_cv.md, from spatial_cv_numbers.json, spatial_cv_calls.csv, spatial_cv_seeds.csv
and spatial_cv_nested_picks.csv (no fitting). Writes figures/*.png next to this file:
  1 arms_T_vs_S.png            per-arm accuracy under tile folds (T) and spatial folds (S): seed range, mean, seed 662
  2 optimism_gap.png           T - S per arm; for (a) and (b) split into smaller training sets and leakage + nearness
  3 confusion_T_vs_S.png       production and the best S arm, under T and S (757 shared roads, seed 662)
  4 errors_map_correlogram.png production's held-out errors under S (seed 662) by tile and fold; residual correlogram
  5 nested_picks.png           the arm picked in each outer fold and seed
  6 trackA_T_vs_S.png          Track A F1 under T and S, and the nested cut-off per fold
Roads are drawn at tile level (counts per tile): road geometry would mean opening the label folder, which this study
does not read.
    /opt/miniconda3/bin/python3 -I spatial_cv_figures.py      (from this folder)
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

OUT = HERE / "figures"
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SURF = "#fcfcfb"
C_T, C_S = "#eb6834", "#2a78d6"            # categorical slots 2 and 1: tile folds orange, spatial folds blue
FOLD = ["#2a78d6", "#eda100", "#1baf7a", "#e87ba4", "#008300"]   # as fold_map.png, fold digits as the second code
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": BASE, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "figure.facecolor": "white",
                     "axes.facecolor": SURF, "axes.grid": False, "savefig.dpi": 180})

NUM = json.load(open(HERE / "spatial_cv_numbers.json"))
SEEDS_DF = pd.read_csv(HERE / "spatial_cv_seeds.csv")
CALLS = pd.read_csv(HERE / "spatial_cv_calls.csv")
NAMES = list(NUM["(c) pipeline factorial"]["arms"])
PROD = NAMES[0]
PRETTY_G = {"a": "production gate", "b": "spotter gate"}
PRETTY_C = {"raw": "no de-hazing", "td": "two-date", "he": "He 2011", "both": "both + raw"}
PRETTY_F = {"prod": "", "vec": " + vector"}


def pretty(n):
    g, c, f = n.split("·")
    return f"{PRETTY_G[g]} · {PRETTY_C[c]}{PRETTY_F[f]}"


def tidy(ax, grid_axis="x"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def seed_acc(section, arm, scheme, road_set=None):
    d = SEEDS_DF[(SEEDS_DF.section == section) & (SEEDS_DF.arm == arm) & (SEEDS_DF.scheme == scheme)]
    if road_set is not None:
        d = d[d["road set"] == road_set]
    return d.sort_values("seed", key=lambda s: s.map(lambda v: -1 if v == 662 else v)).accuracy.to_numpy() * 100


def fig1():
    rows = []
    a, b = NUM["(a) production"], NUM["(b) best combo so far"]
    rows.append(("(a) production — its 798 kept roads", seed_acc("(a)", "production on its 798 kept roads", "T"),
                 seed_acc("(a)", "production on its 798 kept roads", "S"), True))
    lab_b = "best combo so far (production + DINOv2 vector) on the 891 tile-rule roads"
    rows.append(("(b) best combo — the 891 tile-rule roads", seed_acc("(b)", lab_b, "T"), seed_acc("(b)", lab_b, "S"),
                 False))
    rows.append(None)
    fac = NUM["(c) pipeline factorial"]["arms"]
    order = sorted(NAMES, key=lambda n: -fac[n]["S shared accuracy over seeds"]["mean"])
    for n in order:
        rows.append((pretty(n) + (" (production)" if n == PROD else ""),
                     seed_acc("(c)", n, "T", "757 shared"), seed_acc("(c)", n, "S", "757 shared"), n == PROD))
    fig, ax = plt.subplots(figsize=(10.5, 9.2))
    yy = 0
    yt, yl = [], []
    for r in rows:
        if r is None:
            yy += 0.9
            ax.axhline(-(yy - 0.45), color=GRID, lw=0.8)
            ax.text(75.1, -(yy - 0.12), "(c) the 16 factorial arms — the 757 shared roads, ranked by S mean",
                    fontsize=8.5, color=INK2, va="bottom")
            continue
        label, T, Sv, is_prod = r
        for off, v, col in ((-0.17, T, C_T), (0.17, Sv, C_S)):
            yv = -(yy + off)
            ax.plot([v.min(), v.max()], [yv, yv], color=col, lw=2.4, alpha=0.45, solid_capstyle="round")
            ax.plot(v.mean(), yv, "o", color=col, ms=6.5, mec="white", mew=1.0, zorder=3)
            ax.plot(v[0], yv, "D", color=INK, ms=3.6, zorder=4)
        yt.append(-yy)
        yl.append(label)
        if is_prod:
            ax.axhspan(-yy - 0.45, -yy + 0.45, color="#f0efec", zorder=0)
        yy += 1
    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=8.3)
    for t, l_ in zip(ax.get_yticklabels(), yl):
        if "production" in l_ and ("(a)" in l_ or "(production)" in l_):
            t.set_fontweight("bold")
    ax.set_xlim(75, 87.5)
    ax.set_xlabel("held-out accuracy (%)")
    tidy(ax)
    h = [Line2D([], [], color=C_T, lw=2.4, alpha=0.45, label="tile folds (T): min–max over 21 seeds"),
         Line2D([], [], color=C_T, marker="o", lw=0, ms=6.5, label="T: mean"),
         Line2D([], [], color=C_S, lw=2.4, alpha=0.45, label="spatial folds (S): min–max over 21 seeds"),
         Line2D([], [], color=C_S, marker="o", lw=0, ms=6.5, label="S: mean"),
         Line2D([], [], color=INK, marker="D", lw=0, ms=4, label="seed 662"),
         Patch(facecolor="#f0efec", label="production")]
    ax.legend(handles=h, loc="upper left", bbox_to_anchor=(0.0, -0.07), fontsize=7.8, frameon=False, ncol=3)
    ax.set_title("Every arm loses accuracy when the held-out roads are far from the training roads\n"
                 "Held-out accuracy under tile folds (T, as logged) and spatial block folds (S), 21 fold seeds",
                 loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "arms_T_vs_S.png")
    plt.close(fig)


def fig2():
    fac = NUM["(c) pipeline factorial"]["arms"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.6), gridspec_kw={"width_ratios": [1.35, 1]})
    a, b = NUM["(a) production"], NUM["(b) best combo so far"]
    items = [("(a) production · 798", a["optimism gaps (accuracy, same roads)"]["T - S (optimism gap)"], True),
             ("(b) best combo · 891", b["optimism gaps (accuracy, same roads)"]["T - S (optimism gap)"], False)]
    order = sorted(NAMES, key=lambda n: -fac[n]["optimism gap seed mean"])
    for n in order:
        items.append((pretty(n) + " · 757", {"seed mean": fac[n]["optimism gap seed mean"],
                                             "seed-averaged 95% CI (blocks)": fac[n]["optimism gap seed-averaged 95% CI (blocks)"],
                                             "seed 662": fac[n]["optimism gap T - S, seed 662"]}, n == PROD))
    for i, (lab, g, is_prod) in enumerate(items):
        yv = -i - (0.6 if i >= 2 else 0)
        m, (lo, hi) = 100 * g["seed mean"], (100 * x for x in g["seed-averaged 95% CI (blocks)"])
        ax1.barh(yv, m, height=0.62, color=C_S if not is_prod else INK2, alpha=0.85)
        ax1.plot([lo, hi], [yv, yv], color=INK, lw=1.1)
        ax1.plot(100 * g["seed 662"], yv, "D", color=INK, ms=3.4)
        ax1.text(hi + 0.12, yv, f"{m:+.1f}", va="center", fontsize=7.5, color=INK2)
    ax1.set_yticks([-i - (0.6 if i >= 2 else 0) for i in range(len(items))])
    ax1.set_yticklabels([x[0] for x in items], fontsize=8)
    ax1.axvline(0, color=BASE, lw=0.8)
    ax1.set_xlabel("optimism gap: T accuracy − S accuracy (points; mean over 21 seeds, seed-averaged block 95% CI)")
    tidy(ax1)
    ax1.legend(handles=[Line2D([], [], color=INK, marker="D", lw=0, ms=4, label="seed 662")], frameon=False,
               loc="lower right", fontsize=8)
    ax1.set_title("Every arm's tile-fold accuracy is optimistic", loc="left", fontsize=10.5)
    parts = [("T − Tdev\n(own split vs\nsplit over 1,037)", "T - Tdev (own split vs split over the 1,037)", MUTED),
             ("Tdev − TM\nsmaller training\nsets", "Tdev - TM (smaller training sets)", C_T),
             ("TM − S\nleakage +\nnearness", "TM - S (leakage + nearness)", C_S)]
    x = np.arange(len(parts))
    for j, (lab, sec) in enumerate((("(a) production · 798", a), ("(b) best combo · 891", b))):
        for i, (_, key, col) in enumerate(parts):
            g = sec["optimism gaps (accuracy, same roads)"][key]
            m, (lo, hi) = 100 * g["seed mean"], (100 * v for v in g["seed-averaged 95% CI (blocks)"])
            xv = x[i] + (j - 0.5) * 0.36
            ax2.bar(xv, m, width=0.33, color=col, alpha=0.9 if j == 0 else 0.55, edgecolor="white", lw=0.8)
            ax2.plot([xv, xv], [lo, hi], color=INK, lw=1.1)
            ax2.text(xv, (hi if m >= 0 else lo) + (0.15 if m >= 0 else -0.35), f"{m:+.2f}", ha="center", fontsize=7.5,
                     color=INK2)
    ax2.set_xticks(x)
    ax2.set_xticklabels([p[0] for p in parts], fontsize=8)
    ax2.axhline(0, color=BASE, lw=0.8)
    ax2.set_ylabel("points of accuracy (mean over 21 seeds, seed-averaged block 95% CI)")
    ax2.set_ylim(-1.4, 6.6)
    tidy(ax2, "y")
    ax2.legend(handles=[Patch(facecolor=MUTED, alpha=0.9, label="(a) production (solid)"),
                        Patch(facecolor=MUTED, alpha=0.5, label="(b) best combo (pale)")], frameon=False, fontsize=8,
               loc="upper left")
    ax2.set_title("Where the gap comes from, (a) and (b)", loc="left", fontsize=10.5)
    fig.suptitle("Tile folds overstate accuracy by about 4 points; almost all of it is leakage and nearness, not "
                 "training-set size", x=0.01, ha="left", fontsize=11.5)
    fig.tight_layout()
    fig.savefig(OUT / "optimism_gap.png")
    plt.close(fig)


def fig3():
    best = NUM["(c) pipeline factorial"]["optimal combo (preregistered rule, block-resampled seed-averaged intervals)"]["S"]["top arm"]
    sh = CALLS["shared"].astype(bool).to_numpy()
    yv = CALLS.flooded.to_numpy()[sh]
    fig, axes = plt.subplots(2, 2, figsize=(9, 7.6))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("blue", ["#f0f5fc", "#86b6ef", "#2a78d6", "#104281"])
    for r, n in enumerate((PROD, best)):
        for c, sch in enumerate(("T", "S")):
            ax = axes[r, c]
            p = CALLS[f"(c) {n} · {sch} · call seed 662"].to_numpy()[sh]
            m = np.array([[((p == 1) & (yv == 1)).sum(), ((p == 0) & (yv == 1)).sum()],
                          [((p == 1) & (yv == 0)).sum(), ((p == 0) & (yv == 0)).sum()]])
            ax.imshow(m, cmap=cmap, vmin=0, vmax=460)
            for i in range(2):
                for j in range(2):
                    share = m[i, j] / m[i].sum()
                    ax.text(j, i, f"{m[i, j]}\n{100 * share:.1f}% of row", ha="center", va="center", fontsize=10,
                            color="white" if m[i, j] > 250 else INK)
            ax.set_xticks([0, 1])
            ax.set_xticklabels(["called flooded", "called dry"])
            ax.set_yticks([0, 1])
            ax.set_yticklabels(["flooded (label)", "dry (label)"])
            acc = (m[0, 0] + m[1, 1]) / m.sum()
            ax.set_title(f"{'production' if n == PROD else pretty(n)}\n{'tile folds (T)' if sch == 'T' else 'spatial folds (S)'}"
                         f": accuracy {100 * acc:.1f}%", fontsize=9.5, loc="left")
            for s in ax.spines.values():
                s.set_visible(False)
    fig.suptitle("Under spatial folds both models miss more floods and raise more false floods\n"
                 "757 shared roads (431 flooded, 326 dry), fold seed 662; best S arm = highest S mean accuracy",
                 x=0.02, ha="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "confusion_T_vs_S.png")
    plt.close(fig)


def fig4():
    from spatial_folds import _dev_tiles
    t = _dev_tiles()
    ka = CALLS["kept by production gate (a)"].astype(bool).to_numpy()
    d = CALLS[ka].copy()
    d["call"] = d["(a) production · S · call seed 662"]
    d["FN"] = (d.flooded == 1) & (d.call == 0)
    d["FP"] = (d.flooded == 0) & (d.call == 1)
    per = d.groupby("tile_id").agg(roads=("flooded", "size"), FN=("FN", "sum"), FP=("FP", "sum"),
                                   fold=("S fold, seed 662", "first"))
    fold_of_tile = pd.read_csv(HERE / "fold_tables.csv").set_index("tile_id")["fold_seed_662"]
    fig = plt.figure(figsize=(15.5, 8.2))
    ax = fig.add_axes([0.03, 0.08, 0.52, 0.84])
    for _, s in t.iterrows():
        k = int(fold_of_tile[s.tile_id]) - 1
        ax.add_patch(Rectangle((s.x_m - s.w_m / 2, s.y_m - s.h_m / 2), s.w_m, s.h_m, facecolor=FOLD[k], alpha=0.28,
                               edgecolor="white", lw=0.5))
        if s.tile_id in per.index:
            r = per.loc[s.tile_id]
            for val, dx, mk in ((r.FN, -0.2, "v"), (r.FP, 0.2, "o")):
                if val:
                    ax.plot(s.x_m + dx * s.w_m, s.y_m, mk, ms=2.2 + 2.4 * np.sqrt(val), color=FOLD[k], mec=INK,
                            mew=0.6, zorder=3)
            if r.FN + r.FP == 0:
                ax.plot(s.x_m, s.y_m, ".", ms=1.6, color=MUTED, zorder=2)
    from spatial_folds import block_info
    bi = block_info()
    side, (ox, oy) = bi["block_side_m"], bi["origin_m"]
    ft = pd.read_csv(HERE / "fold_tables.csv")
    for blk in ft.block.unique():
        bx, by = int(blk[1:3]), int(blk[4:6])
        ax.add_patch(Rectangle((ox + bx * side, oy - (by + 1) * side), side, side, fill=False, edgecolor=INK2,
                               lw=0.7))
    ax.set_xlim((t.x_m - t.w_m / 2).min() - 300, (t.x_m + t.w_m / 2).max() + 300)
    ax.set_ylim((t.y_m - t.h_m / 2).min() - 300, (t.y_m + t.h_m / 2).max() + 300)
    ax.set_aspect("equal")
    ax.set_xlabel("east (m, local equirectangular)")
    ax.set_ylabel("north (m)")
    nFN, nFP = int(d.FN.sum()), int(d.FP.sum())
    ax.set_title(f"Production's held-out errors under spatial folds (seed 662): {nFN} floods missed, {nFP} false "
                 f"floods, of {len(d)} roads\nMarker area ∝ errors on the tile; colour = the tile's S fold; "
                 "outlines = 1.75 km blocks", loc="left", fontsize=10)
    hand = [Patch(facecolor=FOLD[k], alpha=0.6, label=f"fold {k + 1}: "
                  f"{int(d[d['S fold, seed 662'] == k + 1].FN.sum())} missed / "
                  f"{int(d[d['S fold, seed 662'] == k + 1].FP.sum())} false") for k in range(5)]
    hand += [Line2D([], [], marker="v", lw=0, color=MUTED, mec=INK, ms=7, label="floods missed (FN)"),
             Line2D([], [], marker="o", lw=0, color=MUTED, mec=INK, ms=7, label="false floods (FP)")]
    ax.legend(handles=hand, loc="lower left", bbox_to_anchor=(1.0, 0.0), fontsize=7.8, frameon=False, ncol=1)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax2 = fig.add_axes([0.74, 0.16, 0.24, 0.7])
    rd = NUM["residual dependence check"]
    series = [("production errors under S, seed 662", C_S, "errors under S (spatial)", "o-"),
              ("production errors under T, seed 662 (comparison)", C_T, "errors under T (tile)", "s-"),
              ("labels on the 798 (reference)", MUTED, "flood labels (reference)", "^--")]
    bands = [r["band_km"] for r in rd[series[0][0]]]
    ax2.axvspan(0.5, 1.5, color="#f0efec", zorder=0)
    ax2.text(1.0, 0.45, "block side\n1.75 km is\nin this band", ha="center", va="top", fontsize=7.3, color=INK2)
    for key, col, lab, st in series:
        vals = [r["correlation"] if r["correlation"] is not None else np.nan for r in rd[key]]
        ax2.plot(range(len(vals)), vals, st, color=col, lw=2, ms=6, mec="white", label=lab)
    ax2.axhline(0, color=BASE, lw=0.8)
    ax2.axhline(0.1, color=GRID, lw=0.8, ls=":")
    ax2.set_xticks(range(len(bands)))
    ax2.set_xticklabels(bands, fontsize=8)
    ax2.set_ylim(-0.25, 0.6)
    ax2.set_xlabel("distance band between tile centroids (km)")
    ax2.set_ylabel("correlation (road pairs on different tiles, different road ids)")
    tidy(ax2, "y")
    ax2.legend(frameon=False, fontsize=8, loc="upper right")
    ax2.set_title("Residual dependence: do held-out errors cluster?", loc="left", fontsize=10)
    fig.savefig(OUT / "errors_map_correlogram.png")
    plt.close(fig)


def short(n):
    g, c, f = n.split("·")
    return f"{'P' if g == 'a' else 'S'}·{ {'raw': 'none', 'td': '2-date', 'he': 'He', 'both': 'both'}[c]}" + ("·vec" if f == "vec" else "")


def fig5():
    p = pd.read_csv(HERE / "spatial_cv_nested_picks.csv")
    seeds = [662] + [s for s in sorted(p.seed.unique()) if s != 662]
    counts = p.picked.value_counts()
    top = counts.index.tolist()[:6]
    col = {n: CAT[i] for i, n in enumerate(top)}
    other = [n for n in counts.index if n not in top]
    OTHER = "#d9d8d4"
    dark_text = {"#eda100", "#e87ba4", "#1baf7a", OTHER}
    fig, ax = plt.subplots(figsize=(11.5, 8.2))
    for i, s in enumerate(seeds):
        for k in range(1, 6):
            r = p[(p.seed == s) & (p["outer fold"] == k)].iloc[0]
            c = col.get(r.picked, OTHER)
            ax.add_patch(Rectangle((k - 0.46, -i - 0.44), 0.92, 0.88, facecolor=c, edgecolor="white", lw=1.2))
            ax.text(k, -i, f"{short(r.picked)}  {100 * r['picked inner accuracy']:.1f}", ha="center", va="center",
                    fontsize=6.8, color=INK if c in dark_text else "white")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(-len(seeds) + 0.5, 0.5)
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels([f"outer fold {k}" for k in range(1, 6)])
    ax.set_yticks([-i for i in range(len(seeds))])
    ax.set_yticklabels([f"seed {s}" for s in seeds], fontsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    hand = [Patch(facecolor=col[n], label=f"{short(n)} = {pretty(n)} ({counts[n]} of {len(p)})") for n in top]
    hand.append(Patch(facecolor=OTHER, label="other: " + ", ".join(f"{short(n)} ({counts[n]})" for n in other)))
    ax.legend(handles=hand, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=8)
    nvec = int(p.picked.str.endswith("vec").sum())
    ax.set_title(f"Which arm the inner spatial CV picks, outer fold by outer fold ({nvec} of {len(p)} picks carry the "
                 "DINOv2 vector)\nCell = picked arm (P production gate, S spotter gate) and its pooled inner accuracy "
                 "on inner held-out shared roads (%)", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "nested_picks.png")
    plt.close(fig)


def fig6():
    ta = NUM["(f) Track A road finding"]
    if not isinstance(ta, dict) or "fixed cut-off 0.75, by seed" not in ta or "662" not in ta["fixed cut-off 0.75, by seed"]:
        return False
    r = ta["fixed cut-off 0.75, by seed"]["662"]
    nested = ta.get("nested cut-off, seed 662")
    have_nested = isinstance(nested, dict)
    fig, axes = plt.subplots(1, 2 if have_nested else 1, figsize=(13 if have_nested else 7.5, 5.6), squeeze=False)
    ax = axes[0, 0]
    for j, (sch, col) in enumerate((("T", C_T), ("S", C_S))):
        if not isinstance(r.get(sch), dict):
            continue
        pf = r[sch]["per fold"]
        ax.plot([f["fold"] + (j - 0.5) * 0.18 for f in pf], [f["F1"] for f in pf], "o", color=col, ms=6, mec="white",
                label=f"{'tile' if sch == 'T' else 'spatial'} folds ({sch}): each fold")
        prim = r[sch]["primary: F1 on held-out val-split cells"]
        xv = 6.3 + (j - 0.5) * 0.36
        ax.plot([xv, xv], prim["F1 95% CI"], color=col, lw=2)
        ax.plot(xv, prim["F1"], "D", color=col, ms=7, mec=INK, label=f"{sch} pooled: F1 {prim['F1']:.3f} "
                f"[{prim['F1 95% CI'][0]:.3f}, {prim['F1 95% CI'][1]:.3f}]")
    rep = ta.get("reproduction (train-split cells -> val-split cells, as logged)")
    if rep:
        ax.axhline(rep["F1"], color=MUTED, lw=1, ls="--")
        ax.text(0.65, rep["F1"] + 0.004, f"logged train → val split: F1 {rep['F1']:.3f}", fontsize=7.5, color=INK2)
    ax.set_xticks([1, 2, 3, 4, 5, 6.3])
    ax.set_xticklabels(["fold 1", "fold 2", "fold 3", "fold 4", "fold 5", "pooled"])
    ax.set_ylabel("F1 on held-out val-split cells (cut-off 0.75)")
    tidy(ax, "y")
    ax.legend(frameon=False, fontsize=7.8, loc="upper left", bbox_to_anchor=(0.0, -0.08), ncol=2)
    gap = r.get("T - S F1 gap, primary (val-split cells)")
    note = (f"T − S on the same val-split cells: {gap['gap']:+.3f} [{gap['95% CI (blocks, paired)'][0]:+.3f}, "
            f"{gap['95% CI (blocks, paired)'][1]:+.3f}] (paired, blocks)") if gap else ""
    if not have_nested:
        note += "\nNested cut-off: not run (compute; projected " + \
            next((x.split("projected ")[1].split(" (")[0] for x in ta.get("log", []) if "projected" in x), "?") + \
            ", budget 3 h)"
    ax.text(0.99, 0.02, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8, color=INK2)
    ax.set_title("Track A road finding: tile folds vs spatial folds (seed 662)\nFold k under T and fold k under S are "
                 "different areas; only the pooled values compare", loc="left", fontsize=10)
    if have_nested:
        ax = axes[0, 1]
        cuts = np.round(np.arange(0.05, 1.0, 0.01), 2)
        for k, cur in nested["inner F1 curves (cut-offs 0.05-0.99)"].items():
            ax.plot(cuts, cur, color=FOLD[int(k)], lw=1.6, label=f"outer fold {int(k) + 1}: cut-off "
                    f"{nested['cut-off per outer fold'][int(k)]:.2f}")
            c = nested["cut-off per outer fold"][int(k)]
            ax.plot(c, max(cur), "o", color=FOLD[int(k)], mec=INK, ms=6)
        ax.axvline(0.75, color=INK2, ls="--", lw=1)
        ax.text(0.755, ax.get_ylim()[0] + 0.02, "production 0.75", fontsize=7.5, color=INK2)
        ax.set_xlabel("cut-off")
        ax.set_ylabel("inner out-of-fold F1 (outer-training cells, real road share)")
        ax.set_xlim(0.3, 0.99)
        tidy(ax, "y")
        ax.legend(frameon=False, fontsize=7.8, loc="lower left")
        ax.set_title("Nested cut-off: chosen inside each outer-training fold", loc="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "trackA_T_vs_S.png")
    plt.close(fig)
    return True


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    fig1()
    fig2()
    fig3()
    fig4()
    if (HERE / "spatial_cv_nested_picks.csv").exists():
        fig5()
    print("Track A figure:", fig6())
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))
