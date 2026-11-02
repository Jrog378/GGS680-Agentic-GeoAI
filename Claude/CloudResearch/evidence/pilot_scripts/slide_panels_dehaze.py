"""Slide panels for the de-hazing slides (result 2 and the layering slide), 2026-10-25. Development data only.
Example road picked by a label-free rule fixed before drawing: on the tiles the tile rule scores, the road with the most
metres under thin cloud (length x share of its strip under the dark-rise mask). Writes P5_*.png and adds the "P5" and
"synthetic" numbers to panel_numbers.json."""
import sys, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sn8 import tile
from sn8_clouds import _tile, cloud_table, dehaze, ROAD_CLOUD_CUT
from sn8_heldout import touched_roads
from sn8_lines import _TO_UTM
from sn8_torchgeo import RES
from sn8_refhaze import T_MIN, clear_tiles, dark_reference_dehaze, haze_recovery, reference_dehaze
OUT = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/presentation/assets/"
REJ, STD, NOFLOOD = "#E8602A", "#BC3754", "#4FC3F7"

roads = touched_roads(include_cloudy=True)
c = pd.concat([cloud_table("train"), cloud_table("val")], ignore_index=True)
assert c.tile_id.equals(roads.tile_id) and c.road_id.equals(roads.road_id)
roads["share"] = c.cloud_dark_rise_road.to_numpy()
hz = roads[~roads.cloudy & (roads.share >= ROAD_CLOUD_CUT)].copy()
hz["m_under"] = hz.length_m * hz.share
pick = hz.sort_values("m_under", ascending=False).iloc[0]
T = pick.tile_id
p, b, a, valid = _tile(T)
old, new = reference_dehaze(b, a, valid), dark_reference_dehaze(b, a, valid)
with open(tile(T)["label"]) as f:
    feats = json.load(f)["features"]

def draw_roads(ax):
    """Labelled roads, thick enough to read on a slide: crimson = labelled flooded, light blue = no flood label."""
    for feat in feats:
        pr, g = feat.get("properties") or {}, feat.get("geometry")
        if not g or not isinstance(pr.get("highway"), str):
            continue
        for line in [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]:
            lon, lat = np.array(line)[:, :2].T
            x, y = _TO_UTM.transform(lon, lat)
            ax.plot((x - p["x0"]) / RES, (p["y0"] - y) / RES, lw=3.4, color=STD if pr.get("flooded") == "yes" else NOFLOOD)

def save(draw, name):
    fig = plt.figure(figsize=(6, 6)); ax = fig.add_axes([0, 0, 1, 1]); draw(ax); ax.axis("off")
    fig.savefig(OUT + name, dpi=170, facecolor="black"); plt.close(fig)

def grey(img, opaque=None):
    def draw(ax):
        ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
        if opaque is not None:
            ax.imshow(np.ma.masked_where(~opaque, opaque), cmap=ListedColormap([REJ]), alpha=0.5)
        draw_roads(ax)
        ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0)
    return draw

def tmap(t):
    def draw(ax):
        ax.imshow(t, cmap="inferno", vmin=T_MIN, vmax=1); ax.set_facecolor("black")
        ax.set_xlim(0, valid.shape[1]); ax.set_ylim(valid.shape[0], 0)
    return draw

save(grey(b), "P5_before.png"); save(grey(a), "P5_after.png")
save(grey(old["corrected"]), "P5_pilot.png"); save(grey(new["corrected"], new["opaque"]), "P5_revised.png")
save(grey(dehaze(a, valid)[0]), "P5_single.png")
save(tmap(old["t"]), "P5_t_pilot.png"); save(tmap(new["t"]), "P5_t_revised.png")
if "--panels-only" in sys.argv:
    sys.exit()

d = haze_recovery(clear_tiles())
d.to_csv("haze_recovery.csv", index=False)
cols = [k for k in d.columns if k not in ("tile_id",)]
nums = json.load(open(OUT + "panel_numbers.json"))
nums["P5"] = {"tile": T, "road": str(pick.road_id), "length_m": float(pick.length_m), "share_under": round(float(pick.share), 3),
              "m_under": round(float(pick.m_under), 1), "airlight": new["airlight"],
              "gate_share": round(float(new["gate"][valid].mean()), 3), "opaque_share_of_gate": round(float(new["opaque"][new["gate"]].mean()), 3)}
nums["synthetic"] = {"tiles": len(d), **{k: round(float(d[k].mean()), 3) for k in cols},
                     "revised better t": int((d["t error under haze: revised fit"] < d["t error under haze: pilot fit"]).sum()),
                     "revised better grey": int((d["grey error under haze: revised fit"] < d["grey error under haze: pilot fit"]).sum())}
json.dump(nums, open(OUT + "panel_numbers.json", "w"), indent=1)
print(json.dumps({k: nums[k] for k in ("P5", "synthetic")}, indent=1))
