"""Pilot figures for Assignment 4 (development data only). Night Pass colours on white plates."""
import sys, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd, cv2
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from sn8 import tile
from sn8_clouds import _tile, cloud_maps, cloud_table, CLOUD_COLUMNS
from sn8_heldout import touched_roads
from sn8_lines import draw_roads, CREDIT
from sn8_refhaze import reference_dehaze
from sn8_torchgeo import RES
OUT = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/figures/"
INK, MUTED, RULE = "#16131F", "#5C5A69", "#C9CED5"
STD, VAL, SIGNAL, CONF, REJ, AGENT = "#BC3754", "#23479A", "#FCA50A", "#0A7570", "#E8602A", "#420A68"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": RULE, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.titlecolor": INK, "font.size": 11})
roads = touched_roads(include_cloudy=True)
tiles = roads.groupby("tile_id").agg(cloudy=("cloudy", "first"), dr=("cloud_dark_rise_road", "max"), n=("flooded", "size"),
                                     fl=("flooded", "sum")).reset_index()
ct = pd.concat([cloud_table("train"), cloud_table("val")]).groupby("tile_id").cloud_dark_rise_tile.first()
tiles["dark_rise_tile"] = tiles.tile_id.map(ct)
tiles["cls"] = np.where(tiles.cloudy, "opaque cloud (>= 20% bright)", np.where(tiles.dark_rise_tile >= 0.1, "thin cloud or haze", "clear"))
cls_col = {"clear": CONF, "thin cloud or haze": SIGNAL, "opaque cloud (>= 20% bright)": STD}

# ---- F1 study area: after-image mosaic of the development tiles, outlined by cloud class, one panel per area
fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))
for ax, area, name in ((axes[0], "0", "south scene (area 0)"), (axes[1], "2", "west scene (area 2)")):
    sub = tiles[tiles.tile_id.str.startswith(area + "_")]
    xs, ys = [], []
    for _, t in sub.iterrows():
        p, b, a, valid = _tile(t.tile_id)
        small = cv2.resize(np.where(valid, a, np.nan).astype(np.float32), None, fx=1 / 8, fy=1 / 8, interpolation=cv2.INTER_AREA)
        h, w = a.shape
        x0, y0 = p["x0"] / 1000, p["y0"] / 1000
        ext = (x0, x0 + w * RES / 1000, y0 - h * RES / 1000, y0)
        ax.imshow(np.ma.masked_invalid(small), cmap="gray", vmin=0, vmax=255, extent=ext, zorder=1)
        ax.add_patch(Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], fill=False, lw=1.6, ec=cls_col[t.cls], zorder=2))
        xs += ext[:2]; ys += ext[2:]
    ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2); ax.set_ylim(min(ys) - 0.2, max(ys) + 0.2); ax.set_aspect("equal")
    ax.set_xlabel("UTM 15N easting (km)"); ax.set_ylabel("northing (km)")
    counts = sub.cls.value_counts().to_dict()
    ax.set_title(f"{name}: {len(sub)} development tiles\n" + ", ".join(f"{v} {k.split(' (')[0]}" for k, v in counts.items()), fontsize=11)
fig.legend(handles=[Patch(fc="none", ec=c, lw=2, label=k) for k, c in cls_col.items()], loc="lower center", ncol=3, frameon=False)
fig.suptitle("Study area: SpaceNet 8 Louisiana-East after Hurricane Ida (2021), after images, greyscale", color=INK, fontsize=13)
fig.text(0.5, 0.005, CREDIT + ". Development tiles only; the 40 test tiles and the north set are held out.", ha="center", color=MUTED, fontsize=8)
plt.tight_layout(rect=(0, 0.07, 1, 0.95)); plt.savefig(OUT + "F1_study_area.png", dpi=150); plt.close()

# ---- F2 labels under cloud: one tile + the flooded share by cloud class
T = "2_15_45"
m = cloud_maps(T); p, valid = m["pair"], m["valid"]
fig = plt.figure(figsize=(14, 6.2)); gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1])
ax = fig.add_subplot(gs[0]); ax.imshow(np.where(valid, p["after_grey"], 0), cmap="gray", vmin=0, vmax=255)
mk = m["masks"]["dark rise"]; ax.imshow(np.ma.masked_where(~mk, mk), cmap=ListedColormap([SIGNAL]), alpha=0.35)
import pyproj
from sn8_lines import _TO_UTM
with open(tile(T)["label"]) as f: feats = json.load(f)["features"]
for feat in feats:
    pr, g = feat.get("properties") or {}, feat.get("geometry")
    if not g or not isinstance(pr.get("highway"), str): continue
    for line in [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]:
        lon, lat = np.array(line)[:, :2].T; x, y = _TO_UTM.transform(lon, lat)
        ax.plot((x - p["x0"]) / RES, (p["y0"] - y) / RES, lw=2.4, color=STD if pr.get("flooded") == "yes" else "#4FC3F7")
ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0); ax.axis("off")
ax.set_title(f"Tile {T}, after image: every flooded label is on the clear side", fontsize=11)
ax.legend(handles=[Line2D([], [], color=STD, lw=3, label='labelled "flooded"'), Line2D([], [], color="#4FC3F7", lw=3, label="no flood label (reads as dry)"),
                   Patch(fc=SIGNAL, alpha=0.5, label="thin cloud (dark-rise mask)")], loc="lower left", fontsize=9, framealpha=0.9)
ax = fig.add_subplot(gs[1])
groups = [("clear roads", (~roads.cloudy) & (roads.cloud_dark_rise_road < 0.2)),
          ("thin cloud on the road", (~roads.cloudy) & (roads.cloud_dark_rise_road >= 0.2)),
          ("opaque-cloud tiles", roads.cloudy)]
vals = [100 * roads[g].flooded.mean() for _, g in groups]; ns = [int(g.sum()) for _, g in groups]
bars = ax.bar(range(3), vals, color=[CONF, SIGNAL, STD], width=0.6)
for b, v, n in zip(bars, vals, ns): ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.0f}%\n({n} roads)", ha="center", color=INK)
ax.set_xticks(range(3), [g for g, _ in groups]); ax.set_ylim(0, 70); ax.set_ylabel('roads labelled "flooded" (%)')
ax.spines[["top", "right"]].set_visible(False)
ax.set_title("Under cloud the labels say flooded far less often", fontsize=11)
fig.suptitle('Analysts "only attribute what was visible" (Hänsch et al. 2022), so a hidden road reads as dry', color=INK, fontsize=13)
fig.text(0.5, 0.01, CREDIT + ". Development roads (1,037). Part of the gap is geography (area 0 is dry around its cloudy tiles).", ha="center", color=MUTED, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 0.94)); plt.savefig(OUT + "F2_labels_under_cloud.png", dpi=150); plt.close()

# ---- F3 two-date de-hazing: crops + results
calls = pd.read_csv("refhaze_calls.csv")
fixed = calls[calls.hazy & (calls.flooded) & (calls["call: as it is"] == 0) & (calls["call: two-date de-hazing"] == 1)]
pick = fixed.sort_values("dark_rise_share", ascending=False).iloc[0]   # rule: the fixed road under the most cloud
pt, b, a, valid = _tile(pick.tile_id); out = reference_dehaze(b, a, valid)
fig = plt.figure(figsize=(15, 6)); gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.35])
for k, (img, title) in enumerate(((b, "before (clear reference)"), (a, "after, thin cloud"), (out["corrected"], "after, corrected from the before"))):
    ax = fig.add_subplot(gs[k]); ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
    draw_roads(ax, tile(pick.tile_id)["label"], (pt["x0"], pt["y0"]))
    ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0); ax.axis("off"); ax.set_title(title, fontsize=11)
ax = fig.add_subplot(gs[3])
labels = ["as it is", "single-image\nde-hazing (He)", "two-date\nde-hazing"]
keys = ["call: as it is", "call: single-image de-hazing (He)", "call: two-date de-hazing"]
tf = calls[calls.hazy & calls.flooded]; cl = calls[calls.assessable & calls.tile_id.isin(calls[calls.hazy].tile_id.unique())]
found = [100 * (tf[k] == 1).mean() for k in keys]; ctrl = [100 * (cl[k] == cl.flooded.astype(int)).mean() for k in keys]
x = np.arange(3)
b1 = ax.bar(x - 0.2, found, 0.38, color=[MUTED, VAL, SIGNAL], label=f"flooded found, {len(tf)} trusted flooded roads under thin cloud")
b2 = ax.bar(x + 0.2, ctrl, 0.38, color="white", ec=INK, hatch="//", label=f"accuracy, {len(cl)} clear roads on the same tiles (control)")
for bb, v in list(zip(b1, found)) + list(zip(b2, ctrl)): ax.text(bb.get_x() + bb.get_width() / 2, v + 1, f"{v:.0f}%", ha="center", fontsize=9, color=INK)
ax.set_xticks(x, labels); ax.set_ylim(0, 105); ax.set_ylabel("%"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower center", fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.32))
ax.set_title("Two-date: +3 of 24 floods found, clear roads unchanged\n(exploratory; McNemar p = 0.25)", fontsize=10)
fig.suptitle(f"Seeing through thin cloud with the second image (tile {pick.tile_id}; red = labelled flooded)", color=INK, fontsize=13)
fig.text(0.5, 0.01, CREDIT + ". Development data; frozen flood model trained on clear roads; these 24 roads were looked at before, so the result is exploratory.", ha="center", color=MUTED, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 0.93)); plt.savefig(OUT + "F3_two_date_dehazing.png", dpi=150); plt.close()

# ---- F4 cloud masks against expert cloud labels (HRC_WHU)
from sn8_cloudref import hrc_table, pooled_scores
t = pooled_scores(hrc_table("train"), ("mask", "type"))
types = ["vegetation", "water", "urban", "snow", "barren"]
fig, ax = plt.subplots(figsize=(9, 4.4)); x = np.arange(len(types))
for k, (mask, col, name) in enumerate((("bright", MUTED, "bright rule (old tile rule)"), ("dark", STD, "dark-channel mask (new)"))):
    v = [t[(t["mask"] == mask) & (t.type == ty)].F1.iloc[0] for ty in types]
    bs = ax.bar(x + (k - 0.5) * 0.38, v, 0.38, color=col, label=name)
    for bb, vv in zip(bs, v): ax.text(bb.get_x() + bb.get_width() / 2, vv + 0.015, f"{vv:.2f}", ha="center", fontsize=8)
ax.set_xticks(x, types); ax.set_ylim(0, 1); ax.set_ylabel("F1 against expert cloud masks"); ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False); ax.set_title("Greyscale cloud masks against human cloud labels (HRC_WHU, 120 development images)", fontsize=11)
fig.text(0.5, 0.01, "HRC_WHU (Li et al. 2019), academic use only; 30 test images sealed.", ha="center", color=MUTED, fontsize=8)
plt.tight_layout(rect=(0, 0.04, 1, 1)); plt.savefig(OUT + "F4_masks_vs_expert_labels.png", dpi=150); plt.close()
print("picked road for F3:", pick.tile_id, pick.road_id, round(pick.dark_rise_share, 2)); print("done")
