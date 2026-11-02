"""The pre-registered road test (outputs/preregistration_twodate_roads.md): two-date de-hazing on the flood calls.
Development data only. Writes twodate_calls.csv and twodate_numbers.json and prints the tables."""
import sys, time, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sn8_clouds import assessable, ROAD_CLOUD_CUT
from sn8_heldout import touched_roads, paired_report
from sn8_models import FLOOD_MODELS
from sn8_refhaze import corrected_table, road_handling
from sn8_stages import production_cloud_rule, production_features, production_model
t0 = time.time()
roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
hazy = (~roads.cloudy.to_numpy()) & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
tiles = sorted(roads.tile_id[hazy].unique())
print("roads under thin cloud", int(hazy.sum()), "on", len(tiles), "tiles; labelled flooded", int(roads.flooded[hazy].sum()), flush=True)
cols = production_features()
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
versions = {"as it is": roads}
names = {"dehaze": "single image (He)", "darkref": "two-date"}
for method in ("dehaze", "darkref"):
    c = corrected_table(tiles, method); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
    v = roads.copy()
    m = v[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left")
    on = v.tile_id.isin(tiles).to_numpy()
    assert not m.loc[on, cols].isna().any().any(), f"{method}: missing corrected features"
    v.loc[on, cols] = m.loc[on, cols].to_numpy()
    versions[names[method]] = v
    print(method, "features done", round(time.time() - t0), "s", flush=True)
y = roads.flooded.astype(int).to_numpy()
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
make = FLOOD_MODELS[production_model()]
calls = {k: np.full(len(roads), -1) for k in versions}
for tr, te in folds.split(roads, y, groups=roads.tile_id):
    tr = tr[keep[tr]]
    model = make().fit(roads.iloc[tr][cols], y[tr])          # trained on assessable (clear) roads, as production is
    for k, v in versions.items():
        calls[k][te] = model.predict(v.iloc[te][cols])
on_tiles = roads.tile_id.isin(tiles).to_numpy()
handling = pd.concat([road_handling(t).assign(tile_id=t) for t in tiles]).drop_duplicates(["tile_id", "road_id"])
roads["handling"] = roads[["tile_id", "road_id"]].merge(handling, on=["tile_id", "road_id"], how="left").decision.to_numpy()
groups = {"trusted flooded roads under thin cloud": hazy & (y == 1),
          "dry-labelled roads under thin cloud (labels untrusted)": hazy & (y == 0),
          "control: assessable roads on the same tiles": on_tiles & keep}
out = {"roads under thin cloud": int(hazy.sum()), "tiles": len(tiles), "code": "GeoAI-Roads 2ec5346"}
for name, m in groups.items():
    sub = roads[m].reset_index(drop=True)
    acc = {k: round(float(np.mean(c[m] == y[m])), 4) for k, c in calls.items()}
    called_flooded = {k: int((c[m] == 1).sum()) for k, c in calls.items()}
    print(f"\n{name}: {int(m.sum())} roads\n  share right: {acc}\n  called flooded: {called_flooded}")
    rep = paired_report({k: c[m] for k, c in calls.items()}, "as it is", sub)
    print(rep.to_string())
    rep2 = paired_report({k: c[m] for k, c in calls.items() if k != "as it is"}, "single image (He)", sub)
    print(rep2.to_string())
    out[name] = {"roads": int(m.sum()), "share right": acc, "called flooded": called_flooded,
                 "vs as it is": rep.to_dict("records"), "two-date vs single image": rep2.to_dict("records")}
m = hazy & (y == 1)
by = {}
for d in ("ASSESS", "CORRECT", "CANNOT ASSESS"):
    md = m & (roads.handling.to_numpy() == d)
    if md.any():
        by[d] = {"roads": int(md.sum()), **{k: int((c[md] == 1).sum()) for k, c in calls.items()}}
print("\ntrusted flooded roads under thin cloud, flooded found by handling decision:", by)
out["trusted flooded by handling"] = by
res = roads[["tile_id", "road_id", "flooded", "handling"]].copy()
res["hazy"], res["assessable"] = hazy, keep
res["dark_rise_share"] = roads.cloud_dark_rise_road.to_numpy()
for k, c in calls.items():
    res[f"call: {k}"] = c
res.to_csv("twodate_calls.csv", index=False)
json.dump(out, open("twodate_numbers.json", "w"), indent=1)
print("saved", round(time.time() - t0), "s")
