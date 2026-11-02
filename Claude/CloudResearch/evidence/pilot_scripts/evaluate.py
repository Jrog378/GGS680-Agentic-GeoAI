"""Prototype test of two-date de-hazing on the tiles with thin-cloud roads (development data only)."""
import sys, time
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sn8_clouds import assessable, ROAD_CLOUD_CUT
from sn8_heldout import touched_roads, paired_report
from sn8_models import FLOOD_MODELS
from sn8_refhaze import corrected_table
from sn8_stages import production_cloud_rule, production_features, production_model
t0 = time.time()
roads = touched_roads(include_cloudy=True)
keep = assessable(roads, production_cloud_rule())
hazy = (~roads.cloudy.to_numpy()) & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
tiles = sorted(roads.tile_id[hazy].unique())
print("hazy roads", hazy.sum(), "on", len(tiles), "tiles; flooded", int(roads.flooded[hazy].sum()), flush=True)
cols = production_features()
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
versions = {"as it is": roads}
for method in ("dehaze", "refhaze"):
    c = corrected_table(tiles, method); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
    v = roads.copy()
    m = v[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left")
    on = v.tile_id.isin(tiles).to_numpy()
    v.loc[on, cols] = m.loc[on, cols].to_numpy()
    versions[{"dehaze": "single-image de-hazing (He)", "refhaze": "two-date de-hazing"}[method]] = v
    print(method, "done", round(time.time() - t0), "s", flush=True)
y = roads.flooded.astype(int).to_numpy()
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
make = FLOOD_MODELS[production_model()]
calls = {k: np.full(len(roads), -1) for k in versions}
for tr, te in folds.split(roads, y, groups=roads.tile_id):
    tr = tr[keep[tr]]
    model = make().fit(roads.iloc[tr][cols], y[tr])          # trained on clear roads, as production is
    for k, v in versions.items():
        calls[k][te] = model.predict(v.iloc[te][cols])
on_tiles = roads.tile_id.isin(tiles).to_numpy()
groups = {"trusted flooded roads under thin cloud": hazy & (y == 1),
          "dry-labelled roads under thin cloud (labels untrusted)": hazy & (y == 0),
          "clear roads on the same tiles (control)": on_tiles & keep}
for name, m in groups.items():
    sub = roads[m].reset_index(drop=True)
    print(f"\n{name}: {int(m.sum())} roads")
    print({k: round(float(np.mean(c[m] == y[m])), 3) for k, c in calls.items()})
    print(paired_report({k: c[m] for k, c in calls.items()}, "as it is", sub).to_string())
out = roads[["tile_id", "road_id", "flooded"]].copy()
out["hazy"], out["assessable"] = hazy, keep
out["dark_rise_share"] = roads.cloud_dark_rise_road.to_numpy()
for k, c in calls.items():
    out[f"call: {k}"] = c
out.to_csv("refhaze_calls.csv", index=False)
print("saved calls")
