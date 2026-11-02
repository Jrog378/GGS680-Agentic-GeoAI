"""Check for the critic: does the dark-rise mask flag flooded and dry roads equally often under the same haze?
Clear roads only (development tiles), uniform synthetic haze I*t + A*(1-t) added to the after image."""
import sys
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from scipy import ndimage as ndi
from sn8 import tile
from sn8_clouds import _tile, dark_channel, cloud_thresholds, ROAD_CLOUD_CUT
from sn8_heldout import touched_roads
from sn8_lines import road_band
from sn8_roads import _road_lines, MIN_ROAD_PX
from sn8_torchgeo import RES
cut = cloud_thresholds()["dark rise"]; band = road_band()
roads = touched_roads()                       # the 798 assessable roads (clear by production's rule)
clear = roads[roads.cloud_dark_rise_road < 0.05]
A, levels = 220.0, (1.0, 0.9, 0.8, 0.7, 0.6, 0.5)
rows = []
for tid, g in clear.groupby("tile_id"):
    p, b, a, valid = _tile(tid)
    seg, _, seg_road, lines = _road_lines(tile(tid)["label"], (p["x0"], p["y0"]), valid.shape)
    n = len(lines) - 1
    dist, (ni, nj) = ndi.distance_transform_edt(seg == 0, return_indices=True)
    owner = np.where((dist * RES <= band) & valid, seg_road[seg[ni, nj]], 0).ravel()
    count = np.maximum(np.bincount(owner, minlength=n + 1), 1)
    centre = np.bincount(np.where((seg > 0) & valid, seg_road[seg[ni, nj]], 0).ravel(), minlength=n + 1)[1:]
    keep = [k for k in range(n) if centre[k] >= MIN_ROAD_PX]
    ids = [lines[k + 1]["road_id"] for k in keep]
    db = dark_channel(b, valid)
    floor_b = (np.bincount(owner, weights=db.ravel(), minlength=n + 1) / count)[1:][keep]
    for t in levels:
        ah = np.where(valid, a * t + A * (1 - t), 0).astype(np.float32)
        da = dark_channel(ah, valid)
        share = (np.bincount(owner, weights=((da - db) > cut).ravel().astype(float), minlength=n + 1) / count)[1:][keep]
        floor_a = (np.bincount(owner, weights=da.ravel(), minlength=n + 1) / count)[1:][keep]
        for rid, s, fa, fb in zip(ids, share, floor_a, floor_b):
            rows.append({"tile_id": tid, "road_id": rid, "t": t, "share": s, "floor_after": fa, "floor_before": fb})
d = pd.DataFrame(rows).merge(clear[["tile_id", "road_id", "flooded"]].drop_duplicates(["tile_id", "road_id"]), on=["tile_id", "road_id"])
d["flagged"] = d.share >= ROAD_CLOUD_CUT
summary = d.groupby(["t", "flooded"]).agg(roads=("flagged", "size"), flagged=("flagged", "mean"), share=("share", "mean"),
                                           floor_after=("floor_after", "mean"), floor_before=("floor_before", "mean")).round(3)
print("clear roads:", clear.shape[0], "tiles:", clear.tile_id.nunique()); print(summary.to_string())
# tile-resampled difference in flag rate (flooded - dry) at each haze level
rng = np.random.default_rng(662); out = []
for t, g in d.groupby("t"):
    tiles = g.tile_id.unique(); groups = {k: g[g.tile_id == k] for k in tiles}; diffs = []
    for _ in range(2000):
        s = pd.concat([groups[k] for k in rng.choice(tiles, len(tiles))])
        if s.flooded.any() and (~s.flooded).any():
            diffs.append(s[s.flooded].flagged.mean() - s[~s.flooded].flagged.mean())
    obs = g[g.flooded].flagged.mean() - g[~g.flooded].flagged.mean()
    out.append({"t": t, "flag rate flooded - dry": round(obs, 3), "95% CI": f"{np.percentile(diffs, 2.5):+.3f} to {np.percentile(diffs, 97.5):+.3f}"})
print(pd.DataFrame(out).to_string(index=False))
d.to_csv("mask_bias.csv", index=False)
