"""The four pictures outputs/preregistration_cloud_gate.md fixes, each tile picked by its stated rule:
A synthetic: the clear tile with the most flooded-road strip pixels under the S2 haze;
A real: the development tile with the largest share labelled before cloudy or both cloudy (either-date);
B real: among tiles the tile rule scores, the most pixels added by hysteresis 35 (seed) over either-date;
B synthetic: the clear tile whose S1 haze share is closest to the median haze share.
PNGs stay out of git (imagery)."""
import sys
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from sn8 import tile
from sn8_clouds import _tile, dark_channel, dehaze
from sn8_cloudsym import either_date_dehaze
from sn8_lines import CREDIT, draw_roads
from sn8_refhaze import dark_reference_dehaze, synthetic_haze

OUT = Path(__file__).resolve().parent
SEED = 662
LABEL_CMAP = ListedColormap([(0, 0, 0, 0), "orange", "deepskyblue", "red"])
s = pd.read_csv(OUT / "synthetic_tiles.csv")
r = pd.read_csv(OUT / "real_tiles.csv")


def grey(ax, img, valid, title, vmin=0, vmax=255):
    ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=vmin, vmax=vmax)
    ax.set_title(title, fontsize=10)


def labels_over(ax, img, valid, labels, cannot, title):
    grey(ax, img, valid, title)
    lab = np.ma.masked_where(labels == 0, labels)
    ax.imshow(lab, cmap=LABEL_CMAP, vmin=0, vmax=3, alpha=0.45, interpolation="nearest")
    if cannot.any():
        ax.contour(cannot, levels=[0.5], colors="black", linewidths=0.8)


def finish(fig, path, note):
    for ax in fig.axes:
        if not ax.get_label() == "<colorbar>":
            ax.axis("off")
    fig.text(0.5, 0.005, CREDIT + ". " + note, ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print("saved", path.name)


# ---------- A, synthetic: cloud on the before image ----------
a = s[(s.scenario == "S2 before haze") & (s.arm == "as it is")].sort_values(["flooded strip px", "tile_id"],
                                                                             ascending=[False, True]).iloc[0]
tid, pos = a.tile_id, int(a.position)
p, before, after, valid = _tile(tid)
hazy_b, t_true = synthetic_haze(before, valid, SEED + pos)
o = either_date_dehaze(hazy_b, after, valid)
he = dehaze(hazy_b, valid)[0]
haze = valid & (t_true < 0.95)
err = lambda x: np.sqrt(np.mean((x - before)[haze] ** 2))
fig, ax = plt.subplots(2, 4, figsize=(22, 11))
grey(ax[0, 0], before, valid, f"{tid} before, clear (the answer)")
grey(ax[0, 1], hazy_b, valid, f"before + synthetic cloud (grey error {err(hazy_b):.0f})")
ax[0, 1].contour(haze, levels=[0.5], colors="yellow", linewidths=0.8)
grey(ax[0, 2], after, valid, "after (the reference); labelled roads red = flooded")
draw_roads(ax[0, 2], tile(tid)["label"], (p["x0"], p["y0"]))
ax[0, 2].set_xlim(0, valid.shape[1]); ax[0, 2].set_ylim(valid.shape[0], 0)
labels_over(ax[0, 3], hazy_b, valid, o["labels"], o["cannot"],
            "labels: orange after, blue before, red both cloudy;\nblack line = cannot assess; yellow = true haze")
ax[0, 3].contour(haze, levels=[0.5], colors="yellow", linewidths=0.8)
grey(ax[1, 0], o["before corrected"], valid, f"before, either-date corrected (grey error {err(o['before corrected']):.0f})")
grey(ax[1, 1], he, valid, f"before, single image He (grey error {err(he):.0f})")
im = ax[1, 2].imshow(np.where(haze, np.abs(o["before corrected"] - before), np.nan), cmap="magma", vmin=0, vmax=80)
ax[1, 2].set_title("|either-date - clear before| under the haze", fontsize=10)
draw_roads(ax[1, 2], tile(tid)["label"], (p["x0"], p["y0"]))
ax[1, 2].set_xlim(0, valid.shape[1]); ax[1, 2].set_ylim(valid.shape[0], 0)
ax[1, 3].imshow(np.where(haze, np.abs(he - before), np.nan), cmap="magma", vmin=0, vmax=80)
ax[1, 3].set_title("|He - clear before| under the haze", fontsize=10)
draw_roads(ax[1, 3], tile(tid)["label"], (p["x0"], p["y0"]))
ax[1, 3].set_xlim(0, valid.shape[1]); ax[1, 3].set_ylim(valid.shape[0], 0)
plt.colorbar(im, ax=ax[1, 2:], fraction=0.02, label="grey levels")
finish(fig, OUT / "fig_A_synthetic_before_cloud.png",
       "Synthetic haze (He's model, t down to 0.35) on the BEFORE image; the after image is the reference. "
       "Rule: the clear tile with the most flooded-road strip under the haze.")

# ---------- A, real: what fires on real development tiles ----------
e = r[r.arm == "either-date"].assign(score=lambda d: d["fall share"] + d["both share"])
e = e.sort_values(["score", "tile_id"], ascending=[False, True]).iloc[0]
tid = e.tile_id
p, before, after, valid = _tile(tid)
o = either_date_dehaze(before, after, valid)
db, da = dark_channel(before, valid), dark_channel(after, valid)
fig, ax = plt.subplots(1, 5, figsize=(28, 7.2))
grey(ax[0], before, valid, f"{tid} before")
grey(ax[1], after, valid, "after")
labels_over(ax[2], after, valid, o["labels"], o["cannot"],
            f"labels (fall {100 * e['fall share']:.1f}%, both {100 * e['both share']:.1f}% of tile)\n"
            "orange after, blue before, red both cloudy; black = cannot assess")
for k, (img, name) in enumerate(((db, "dark channel before"), (da, "dark channel after"))):
    im = ax[3 + k].imshow(np.where(valid, img, np.nan), cmap="viridis", vmin=0, vmax=255)
    ax[3 + k].set_title(name + " (single-date cut 98)", fontsize=10)
    ax[3 + k].contour(np.where(valid, img, 0) > 98, levels=[0.5], colors="white", linewidths=0.6)
plt.colorbar(im, ax=ax[3:], fraction=0.02)
finish(fig, OUT / "fig_A_real_what_fires.png",
       "Development before images are cloud-free, so every before-cloudy or both-cloudy pixel here is a false alarm "
       "or faint before haze. Rule: the tile with the largest such share.")

# ---------- B, real: faint haze the grown gate takes in ----------
b = r[(r.arm == "hysteresis 35, seed") & ~r["tile rule cloudy"]].sort_values(["added vs either-date px", "tile_id"],
                                                                              ascending=[False, True]).iloc[0]
tid = b.tile_id
p, before, after, valid = _tile(tid)
db, da = dark_channel(before, valid), dark_channel(after, valid)
o0 = either_date_dehaze(before, after, valid, dark=(db, da))
grown = {lo: either_date_dehaze(before, after, valid, low=lo, dark=(db, da)) for lo in (50, 35, 20)}
level = np.zeros(valid.shape, np.uint8)
for k, lo in enumerate((20, 35, 50)):
    level[grown[lo]["labels"] > 0] = k + 1
level[o0["labels"] > 0] = 4
fig, ax = plt.subplots(2, 3, figsize=(21, 13))
grey(ax[0, 0], before, valid, f"{tid} before")
grey(ax[0, 1], after, valid, "after, as it is")
grey(ax[0, 2], after, valid, "gate: red = today's (71); then grown to 50, 35, 20 (orange to pale)")
ax[0, 2].imshow(np.ma.masked_where(level == 0, level), cmap=ListedColormap(["#fff3b0", "#ffc04d", "#ff8c00", "red"]),
                vmin=0.5, vmax=4.5, alpha=0.55, interpolation="nearest")
grey(ax[1, 0], o0["after corrected"], valid,
     f"after corrected, today's gate ({100 * (o0['labels'] > 0)[valid].mean():.1f}% gated)")
grey(ax[1, 1], grown[35]["after corrected"], valid,
     f"after corrected, hysteresis 35 ({100 * (grown[35]['labels'] > 0)[valid].mean():.1f}% gated)")
im = ax[1, 2].imshow(np.where(valid, da - db, np.nan), cmap="RdBu_r", vmin=-120, vmax=120)
ax[1, 2].contour(np.where(valid, da - db, 0), levels=[20, 35, 50, 71], colors=["#fff3b0", "#ffc04d", "#ff8c00", "red"],
                 linewidths=0.6)
ax[1, 2].set_title("dark-channel change, after - before (contours 20, 35, 50, 71)", fontsize=10)
plt.colorbar(im, ax=ax[1, 2], fraction=0.04)
finish(fig, OUT / "fig_B_real_faint_haze.png",
       "Rule: among the development tiles the tile rule scores, the one with the most pixels added by hysteresis 35 "
       "(seed rule) over today's gate.")

# ---------- B, synthetic ----------
g = s[(s.scenario == "S1 after haze") & (s.arm == "as it is")].copy()
g["dist"] = (g["haze share"] - g["haze share"].median()).abs()
c = g.sort_values(["dist", "tile_id"]).iloc[0]
tid, pos = c.tile_id, int(c.position)
p, before, after, valid = _tile(tid)
hazy, t_true = synthetic_haze(after, valid, SEED + pos)
haze = valid & (t_true < 0.95)
o0 = either_date_dehaze(before, hazy, valid)
o35 = either_date_dehaze(before, hazy, valid, low=35)
he = dehaze(hazy, valid)[0]
err = lambda x: np.sqrt(np.mean((x - after)[haze] ** 2))
level = np.zeros(valid.shape, np.uint8)
for k, lo in enumerate((20, 35, 50)):
    level[either_date_dehaze(before, hazy, valid, low=lo)["labels"] == 1] = k + 1
level[o0["labels"] == 1] = 4
fig, ax = plt.subplots(2, 4, figsize=(26, 12))
im = ax[0, 0].imshow(np.where(valid, t_true, np.nan), cmap="viridis", vmin=0.35, vmax=1)
ax[0, 0].set_title(f"{tid} true t of the synthetic haze (1 = clear); yellow t = 0.95", fontsize=10)
ax[0, 0].contour(haze, levels=[0.5], colors="yellow", linewidths=0.8)
plt.colorbar(im, ax=ax[0, 0], fraction=0.04)
grey(ax[0, 1], hazy, valid, f"after + synthetic haze (grey error {err(hazy):.0f})")
grey(ax[0, 2], hazy, valid, "gate: red today's (71), grown to 50 / 35 / 20; yellow = true haze")
ax[0, 2].imshow(np.ma.masked_where(level == 0, level), cmap=ListedColormap(["#fff3b0", "#ffc04d", "#ff8c00", "red"]),
                vmin=0.5, vmax=4.5, alpha=0.55, interpolation="nearest")
ax[0, 2].contour(haze, levels=[0.5], colors="yellow", linewidths=0.8)
grey(ax[0, 3], after, valid, "after, clear (the answer)")
for k, (img, name) in enumerate(((o0["after corrected"], "either-date, today's gate"),
                                 (o35["after corrected"], "either-date, hysteresis 35"), (he, "single image He"))):
    ax[1, k].imshow(np.where(haze, np.abs(img - after), np.nan), cmap="magma", vmin=0, vmax=80)
    ax[1, k].set_title(f"|{name} - clear after| (grey error {err(img):.0f})", fontsize=10)
grey(ax[1, 3], o35["after corrected"], valid, "after corrected, hysteresis 35")
finish(fig, OUT / "fig_B_synthetic.png",
       "Synthetic haze on the after image (known answer). Rule: the clear tile whose haze share is closest to the median.")
