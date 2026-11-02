"""Slide panels for Assignment 4: imagery only (titles, legends and bars are built on the slides from panel_numbers.json).
Development data only; same selection rules as figures.py."""
import sys, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd, cv2
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle
from sn8 import tile
from sn8_clouds import _tile, cloud_maps, cloud_table
from sn8_heldout import touched_roads
from sn8_lines import draw_roads, _TO_UTM
from sn8_refhaze import reference_dehaze, T_MIN
from sn8_torchgeo import RES
from sn8_cloudref import hrc_table, pooled_scores
OUT = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/presentation/assets/"
INK, STD, SIGNAL, CONF, NOFLOOD = "#16131F", "#BC3754", "#FCA50A", "#0A7570", "#4FC3F7"
nums = {}

def save_square(img_fn, name, size=6):
    fig = plt.figure(figsize=(size, size)); ax = fig.add_axes([0, 0, 1, 1]); img_fn(ax); ax.axis("off")
    fig.savefig(OUT + name, dpi=170, facecolor="black"); plt.close(fig)

roads = touched_roads(include_cloudy=True)
tiles = roads.groupby("tile_id").agg(cloudy=("cloudy", "first")).reset_index()
ct = pd.concat([cloud_table("train"), cloud_table("val")]).groupby("tile_id").cloud_dark_rise_tile.first()
tiles["dark_rise_tile"] = tiles.tile_id.map(ct)
tiles["cls"] = np.where(tiles.cloudy, "opaque", np.where(tiles.dark_rise_tile >= 0.1, "thin", "clear"))
col = {"clear": CONF, "thin": SIGNAL, "opaque": STD}

# P1: the two scenes' after-image mosaics, tiles outlined by cloud class, 2 km scale bar
for area, name in (("0", "south"), ("2", "west")):
    sub = tiles[tiles.tile_id.str.startswith(area + "_")]
    nums[f"tiles_{name}"] = {"total": len(sub), **sub.cls.value_counts().to_dict()}
    exts = []
    for t in sub.tile_id:
        p, b, a, valid = _tile(t); h, w = a.shape; x0, y0 = p["x0"] / 1000, p["y0"] / 1000
        exts.append((t, (x0, x0 + w * RES / 1000, y0 - h * RES / 1000, y0)))
    xs = [e for _, x in exts for e in x[:2]]; ys = [e for _, x in exts for e in x[2:]]
    W, H = max(xs) - min(xs) + 0.4, max(ys) - min(ys) + 0.4
    fig = plt.figure(figsize=(7 * W / H, 7)); ax = fig.add_axes([0, 0, 1, 1])
    for t, ext in exts:
        p, b, a, valid = _tile(t)
        small = cv2.resize(np.where(valid, a, np.nan).astype(np.float32), None, fx=1 / 8, fy=1 / 8, interpolation=cv2.INTER_AREA)
        ax.imshow(np.ma.masked_invalid(small), cmap="gray", vmin=0, vmax=255, extent=ext, zorder=1)
        cls = sub.set_index("tile_id").cls[t]
        ax.add_patch(Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], fill=False, lw=2.6, ec=col[cls], zorder=2))
    ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2); ax.set_ylim(min(ys) - 0.2, max(ys) + 0.2); ax.set_aspect("equal"); ax.axis("off")
    bx, by = min(xs) - 0.1, min(ys) - 0.05
    ax.plot([bx, bx + 2], [by, by], color=INK, lw=6, solid_capstyle="butt", zorder=3)
    fig.savefig(OUT + f"P1_{name}.png", dpi=150, facecolor="white"); plt.close(fig)
    nums[f"P1_{name}_aspect"] = round(W / H, 4)

# P2: tile 2_15_45 after image, thin-cloud mask, roads by flood label
T = "2_15_45"; m = cloud_maps(T); p, valid = m["pair"], m["valid"]; mk = m["masks"]["dark rise"]
with open(tile(T)["label"]) as f: feats = json.load(f)["features"]
def p2(ax):
    ax.imshow(np.where(valid, p["after_grey"], 0), cmap="gray", vmin=0, vmax=255)
    ax.imshow(np.ma.masked_where(~mk, mk), cmap=ListedColormap([SIGNAL]), alpha=0.35)
    for feat in feats:
        pr, g = feat.get("properties") or {}, feat.get("geometry")
        if not g or not isinstance(pr.get("highway"), str): continue
        for line in [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]:
            lon, lat = np.array(line)[:, :2].T; x, y = _TO_UTM.transform(lon, lat)
            ax.plot((x - p["x0"]) / RES, (p["y0"] - y) / RES, lw=3.4, color=STD if pr.get("flooded") == "yes" else NOFLOOD)
    ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0)
save_square(p2, "P2_tile_2_15_45.png")
groups = [("clear", (~roads.cloudy) & (roads.cloud_dark_rise_road < 0.2)), ("thin", (~roads.cloudy) & (roads.cloud_dark_rise_road >= 0.2)),
          ("opaque", roads.cloudy)]
nums["flooded_share"] = {k: {"pct": round(100 * roads[g].flooded.mean(), 1), "roads": int(g.sum())} for k, g in groups}

# P3: two-date de-hazing on the fixed road under the most cloud (figures.py rule), plus the fitted transmission t
calls = pd.read_csv("refhaze_calls.csv")
fixed = calls[calls.hazy & calls.flooded & (calls["call: as it is"] == 0) & (calls["call: two-date de-hazing"] == 1)]
pick = fixed.sort_values("dark_rise_share", ascending=False).iloc[0]
pt, b, a, valid = _tile(pick.tile_id); out = reference_dehaze(b, a, valid); lab = tile(pick.tile_id)["label"]
for img, name in ((b, "before"), (a, "after"), (out["corrected"], "corrected")):
    def p3(ax, img=img):
        ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255); draw_roads(ax, lab, (pt["x0"], pt["y0"]))
        ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0)
    save_square(p3, f"P3_{name}.png")
def p3t(ax):
    ax.imshow(np.where(valid, out["t"], np.nan), cmap="inferno", vmin=T_MIN, vmax=1); ax.set_facecolor("black")
    ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0)
save_square(p3t, "P3_transmission.png")
tv = out["t"][valid]
nums["P3"] = {"tile": pick.tile_id, "road": str(pick.road_id), "t_min": round(float(np.nanmin(tv)), 2), "t_median": round(float(np.nanmedian(tv)), 2),
              "hazy_share": round(float(np.mean(tv < 0.999)), 3), "gain": [round(v, 3) for v in out["gain"]]}
keys = {"as it is": "call: as it is", "single-image": "call: single-image de-hazing (He)", "two-date": "call: two-date de-hazing"}
tf = calls[calls.hazy & calls.flooded]; cl = calls[calls.assessable & calls.tile_id.isin(calls[calls.hazy].tile_id.unique())]
nums["dehaze"] = {"flooded_roads": len(tf), "clear_roads": len(cl),
                  **{k: {"found": round(100 * (tf[c] == 1).mean(), 1), "clear_acc": round(100 * (cl[c] == cl.flooded.astype(int)).mean(), 1)} for k, c in keys.items()}}

# F4 numbers: mask F1 by land cover against HRC_WHU expert masks (development images)
ht = hrc_table("train")
t = pooled_scores(ht, ("mask", "type")); pall = pooled_scores(ht, ("mask",))
nums["hrc"] = {"images": int(ht.image.nunique()), "by_type": {f"{r['mask']}|{r['type']}": r.F1 for _, r in t.iterrows()},
               "pooled": {r["mask"]: {"F1": r.F1, "P": r.precision, "R": r.recall} for _, r in pall.iterrows()}}
json.dump(nums, open(OUT + "panel_numbers.json", "w"), indent=1)
print(json.dumps(nums, indent=1))
