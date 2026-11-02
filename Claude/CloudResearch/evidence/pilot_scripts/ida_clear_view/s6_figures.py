"""Figures for evidence 18 (Justin's rule: numbers come with pictures).
  F1_tile_status.png        every development tile: NOAA coverage, alignment, kept / dropped
  F2_panels_<tile>.png      cloudy tiles (label-free pick: the 5 scored tiles with the most thin-cloud pixels):
                            before | satellite after | He 2011 | two-date | NOAA reference (tone-matched) |
                            feature distance to NOAA, as is | feature distance, two-date (+ thin / opaque outlines)
  F3_alignment_<tile>.png   alignment check for 2 tiles: satellite after (magenta) over NOAA (green) before and
                            after the AROSICS-style correction, 150 m crops, with the tie-point shifts
  F4_outcomes.png           per-tile differences in feature distance (outcomes 1-3) and the t discard curve (outcome 4)
    python3 -I s6_figures.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#8a8a85"
CREDIT = ("Satellite: SpaceNet 8 / Maxar (CC BY-SA 4.0). Aerial: NOAA NGS Hurricane Ida emergency response imagery "
          "(public domain).")


def grey_ax(ax, img, m, title, lo=None, hi=None):
    if lo is None:
        lo, hi = np.percentile(img[m], [1, 99]) if m.any() else (0, 255)
    ax.imshow(np.where(m, img, lo), cmap="gray", vmin=lo, vmax=hi)
    ax.set_title(title, fontsize=10)
    ax.axis("off")


def outline(ax, mask, colour, lw=1.0):
    if mask.any():
        ax.contour(mask.astype(float), levels=[0.5], colors=[colour], linewidths=lw)


def f1_status():
    cov = pd.read_csv(C.HERE / "s1_coverage.csv")
    prep = pd.read_csv(C.HERE / "s2_prep.csv").set_index("tile_id")
    from spatial_folds import fold_table
    ft = fold_table(C.SEED).set_index("tile_id")
    cov = cov.join(ft[["x_m", "y_m", "region"]], on="tile_id", rsuffix="_ft")
    status = []
    for r in cov.itertuples():
        if not r.kept_cover:
            status.append("dropped: NOAA cover < 50%")
        elif r.tile_id in prep.index and bool(prep.loc[r.tile_id].get("coreg_ok", False) is True or
                                              str(prep.loc[r.tile_id].get("coreg_ok")) == "True"):
            status.append("kept: aligned")
        else:
            status.append("dropped: alignment")
    cov["status"] = status
    colours = {"kept: aligned": BLUE, "dropped: alignment": ORANGE, "dropped: NOAA cover < 50%": "#c9c8c2"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.5))
    for ax, reg in zip(axes, ("south", "west")):
        d = cov[cov.region == reg]
        for s, col in colours.items():
            x = d[d.status == s]
            ax.scatter(x.x_m / 1000, x.y_m / 1000, s=150, marker="s", c=col, label=f"{s} ({len(x)})",
                       edgecolors=["black" if c else "none" for c in x.cloudy], linewidths=1.2)
        ax.set_title(f"{reg} scene", fontsize=11)
        ax.set_xlabel("UTM 15N easting (km)")
        ax.set_ylabel("northing (km)")
        ax.set_aspect("equal")
        ax.legend(fontsize=8, loc="best", frameon=False)
        ax.grid(color="#e8e8e4", lw=0.5)
    fig.suptitle("Development tiles: NOAA valid-pixel coverage and alignment (black outline = tile with cloudy roads)",
                 fontsize=11)
    fig.text(0.5, 0.01, CREDIT, ha="center", fontsize=8, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 0.96))
    fig.savefig(C.FIG / "F1_tile_status.png", dpi=130)
    plt.close(fig)
    return cov


def f2_panels(tiles):
    from s3_score import regions
    for t in tiles:
        z = dict(np.load(C.BIG / "prep" / f"{t}.npz", allow_pickle=True))
        s = z["score"]
        R = regions(z)
        lo, hi = np.percentile(z["noaa"][s], [1, 99])
        fa = np.load(C.BIG / "score" / f"{t}_featmap_asis.npy").astype(np.float32)
        ft = np.load(C.BIG / "score" / f"{t}_featmap_td.npy").astype(np.float32)
        fh = np.load(C.BIG / "score" / f"{t}_featmap_he.npy").astype(np.float32)
        vmax = float(np.percentile(np.r_[fa[s], ft[s]], 99))
        fig, axes = plt.subplots(2, 4, figsize=(22, 12.5))
        ax = axes.ravel()
        grey_ax(ax[0], z["before"], s, f"{t}: before (pre-storm satellite)")
        grey_ax(ax[1], z["asis"], s, "satellite after, as is", lo, hi)
        outline(ax[1], R["thin"], "#eda100"); outline(ax[1], R["opaque"], ORANGE)
        grey_ax(ax[2], z["he"], s, "He 2011 (single image)", lo, hi)
        grey_ax(ax[3], z["td"], s, "two-date (production, 20 m fade)", lo, hi)
        grey_ax(ax[4], z["noaa"], s, "NOAA aerial, aligned + tone-matched (reference)", lo, hi)
        rgb = z["noaa_rgb"].astype(np.float32)
        ax[5].imshow(np.where(s[..., None], np.clip(rgb / max(np.percentile(rgb[s], 99), 1), 0, 1), 1))
        ax[5].set_title("NOAA aerial, colour (aligned)", fontsize=10); ax[5].axis("off")
        for a_, fmap, name in ((ax[6], fa, "as is"), (ax[7], ft, "two-date")):
            im = a_.imshow(np.where(s, fmap, np.nan), cmap="Blues", vmin=0, vmax=vmax)
            outline(a_, R["thin"], "#eda100"); outline(a_, R["opaque"], ORANGE)
            m = R["thin"]
            mt = f"; thin-cloud mean {fmap[m].mean():.3f}" if m.sum() > 0 else ""
            a_.set_title(f"DINOv2 feature distance to NOAA, {name}{mt}", fontsize=10)
            a_.axis("off")
            plt.colorbar(im, ax=a_, fraction=0.04)
        fig.text(0.5, 0.01, "Outlines: yellow = thin cloud (two-date gate, t >= 0.2), orange = opaque (t < 0.2, cannot "
                 f"assess). Darker blue = further from NOAA (1 - cosine of 14 px patch tokens). He 2011 thin-cloud mean "
                 f"{fh[R['thin']].mean() if R['thin'].any() else float('nan'):.3f}. " + CREDIT,
                 ha="center", fontsize=8, color=GREY, wrap=True)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(C.FIG / f"F2_panels_{t}.png", dpi=90)
        plt.close(fig)


def f3_alignment(tiles):
    import s2_prep as S
    for t in tiles:
        z = dict(np.load(C.BIG / "prep" / f"{t}.npz", allow_pickle=True))
        row = z["row"].item()
        p, before, after, valid = C.sat_tile(t)
        src = C.flight_sources(t, p, valid.shape)
        rgba = C.reproject_flight(src[row["flight"]], p, valid.shape)
        raw = C.grey_of(rgba)
        al = z["noaa_raw"]
        pts = list(z["pts"])
        # crop: the 300 x 300 px window around the guard pixel density peak
        dens = cv2.blur(z["guard"].astype(np.float32), (301, 301))
        r, c = np.unravel_index(np.argmax(dens), dens.shape)
        r0, c0 = int(np.clip(r - 150, 0, dens.shape[0] - 300)), int(np.clip(c - 150, 0, dens.shape[1] - 300))
        sl = (slice(r0, r0 + 300), slice(c0, c0 + 300))

        def comp(a, b):
            def n(x):
                lo, hi = np.percentile(x, [2, 98])
                return np.clip((x - lo) / max(hi - lo, 1e-6), 0, 1)
            a, b = n(a[sl]), n(b[sl])
            return np.dstack([a, b, a])
        fig, axes = plt.subplots(1, 3, figsize=(19, 6.6))
        axes[0].imshow(comp(after, raw)); axes[0].set_title(f"{t}: as warped from georeferencing (150 m crop)")
        axes[1].imshow(comp(after, al)); axes[1].set_title(
            f"after AROSICS-style correction (residual RMS {row.get('residual_rms_px', np.nan):.2f} px)")
        for a in axes[:2]:
            a.axis("off")
        ax = axes[2]
        grey_ax(ax, after, valid, f"tie points: {row.get('n_windows')} windows, shift x10")
        for q in pts:
            ax.arrow(q["col"], q["row"], 10 * q["dx"], 10 * q["dy"], color=ORANGE, width=3, head_width=14)
        ax.add_patch(plt.Rectangle((c0, r0), 300, 300, fill=False, ec=BLUE, lw=1.5))
        fig.text(0.5, 0.01, "Magenta = satellite after, green = NOAA grey; grey where they agree. " + CREDIT,
                 ha="center", fontsize=8, color=GREY)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        fig.savefig(C.FIG / f"F3_alignment_{t}.png", dpi=100)
        plt.close(fig)


def f4_outcomes():
    from s5_stats import load_rows
    num = json.loads((C.HERE / "s5_numbers.json").read_text())
    d = load_rows("dino")
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.8))
    for ax, (region, subset, title) in zip(axes[:2], (("thin", "road", "thin cloud, road strips"),
                                                      ("guard", "all", "clear guard, all pixels"))):
        x = d[(d.region == region) & (d.subset == subset) & (d.px >= 1000)].pivot_table(index="tile_id", columns="arm",
                                                                                        values="feat")
        for k, (a, b, col) in enumerate((("td", "asis", BLUE), ("he", "asis", ORANGE), ("td", "he", GREY))):
            if a in x and b in x:
                v = (x[a] - x[b]).dropna()
                ax.scatter(np.full(len(v), k) + np.random.default_rng(0).uniform(-0.15, 0.15, len(v)), v, s=22,
                           color=col, alpha=0.8)
                ax.plot([k - 0.3, k + 0.3], [v.mean()] * 2, color="black", lw=2)
        ax.axhline(0, color=GREY, lw=1)
        ax.set_xticks(range(3), ["two-date − as is", "He 2011 − as is", "two-date − He 2011"])
        ax.set_ylabel("Δ feature distance to NOAA (per tile; < 0 = closer)")
        ax.set_title(title)
        ax.grid(axis="y", color="#e8e8e4", lw=0.5)
    ax = axes[2]
    if "o4" in num:
        cur = pd.DataFrame(num["o4"]["discard_curve"])
        ax.plot(cur.dropped * 100, cur.feat_td, color=BLUE, lw=2, marker="o", ms=6)
        ax.set_xlabel("share of gated pixels dropped, lowest t first (%)")
        ax.set_ylabel("mean feature distance to NOAA, two-date")
        ax.set_title(f"t as uncertainty (AUC of t for recovered {num['o4']['auc_t']:.2f})")
        ax.grid(color="#e8e8e4", lw=0.5)
    fig.text(0.5, 0.01, "Black bars: mean over tiles. Each dot is one tile. " + CREDIT, ha="center", fontsize=8,
             color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(C.FIG / "F4_outcomes.png", dpi=120)
    plt.close(fig)


def main():
    C.FIG.mkdir(parents=True, exist_ok=True)
    f1_status()
    from s5_stats import load_rows
    d = load_rows("dino")
    thin = d[(d.region == "thin") & (d.subset == "all") & (d.arm == "td")].sort_values("px", ascending=False)
    pick = list(thin.tile_id[:5])
    f2_panels(pick)
    prep = pd.read_csv(C.HERE / "s2_prep.csv")
    ok = prep[prep.coreg_ok.astype(str) == "True"].sort_values("n_windows", ascending=False)
    cl = set(C.cloudy_tiles())
    al = [ok.tile_id[ok.tile_id.isin(cl)].iloc[0], ok.tile_id[~ok.tile_id.isin(cl)].iloc[0]]
    f3_alignment(al)
    f4_outcomes()
    print("panels:", pick, "alignment:", al)


if __name__ == "__main__":
    main()
