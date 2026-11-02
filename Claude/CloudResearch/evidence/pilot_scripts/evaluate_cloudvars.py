"""Pre-registered (outputs/preregistration_cloud_variables.md): cloud as an extra variable, with and without two-date
de-hazing. Development data only. Writes cloudvars_calls.csv, cloudvars_numbers.json; prints the tables."""
import sys, time, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sn8_clouds import CLOUD_COLUMNS, ROAD_CLOUD_CUT, assessable, cloud_table
from sn8_heldout import touched_roads, paired_report
from sn8_models import FLOOD_MODELS
from sn8_refhaze import corrected_table, road_handling
from sn8_stages import production_cloud_rule, production_features, production_model
t0 = time.time()
roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
clouds = pd.concat([cloud_table("train"), cloud_table("val")], ignore_index=True)
assert clouds.tile_id.equals(roads.tile_id) and clouds.road_id.equals(roads.road_id)
for c in CLOUD_COLUMNS:
    roads[c] = clouds[c].to_numpy()
keep = assessable(roads, production_cloud_rule())                 # production training set
tile_rule = ~roads.cloudy.to_numpy()                              # tile-rule training set (thin-cloud roads included)
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
haze_tiles = sorted(roads.tile_id[hazy].unique())
all_tiles = sorted(roads.tile_id[tile_rule].unique())
print("roads under thin cloud", int(hazy.sum()), "on", len(haze_tiles), "tiles; tile-rule tiles", len(all_tiles), flush=True)
cols = production_features()
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
c = corrected_table(all_tiles, "darkref"); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
dh = roads.copy()
m = dh[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left")
on = dh.tile_id.isin(all_tiles).to_numpy()
assert not m.loc[on, cols].isna().any().any(), "missing corrected features"
dh.loc[on, cols] = m.loc[on, cols].to_numpy()
print("two-date features done", round(time.time() - t0), "s", flush=True)
fit = pd.concat([road_handling(t).assign(tile_id=t) for t in all_tiles]).drop_duplicates(["tile_id", "road_id"])
fit = roads[["tile_id", "road_id"]].merge(fit[["tile_id", "road_id", "in gate", "opaque"]], on=["tile_id", "road_id"], how="left")
for v in (roads, dh):
    v["fit_in_gate"], v["fit_opaque"] = fit["in gate"].fillna(0).to_numpy(), fit["opaque"].fillna(0).to_numpy()
print("fit variables done", round(time.time() - t0), "s", flush=True)
arms = {"1 as it is · production": (roads, cols, keep),
        "2 two-date · production": (dh, cols, keep),
        "3 as it is + cloud vars": (roads, cols + CLOUD_COLUMNS, tile_rule),
        "4 two-date + cloud vars": (dh, cols + CLOUD_COLUMNS, tile_rule),
        "5 two-date + cloud vars + fit vars": (dh, cols + CLOUD_COLUMNS + ["fit_in_gate", "fit_opaque"], tile_rule),
        "6 two-date · tile-rule training": (dh, cols, tile_rule)}
y = roads.flooded.astype(int).to_numpy()
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
make = FLOOD_MODELS[production_model()]
calls = {k: np.full(len(roads), -1) for k in arms}
for tr, te in folds.split(roads, y, groups=roads.tile_id):
    for k, (v, cs, train_mask) in arms.items():
        t_ = tr[train_mask[tr]]
        calls[k][te] = make().fit(v.iloc[t_][cs], y[t_]).predict(v.iloc[te][cs])
on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
groups = {"trusted flooded roads under thin cloud": hazy & (y == 1),
          "dry-labelled roads under thin cloud (labels untrusted)": hazy & (y == 0),
          "control: assessable roads on the same tiles": on_tiles & keep}
pairs = [("4 two-date + cloud vars", "2 two-date · production"), ("4 two-date + cloud vars", "3 as it is + cloud vars"),
         ("5 two-date + cloud vars + fit vars", "4 two-date + cloud vars"), ("6 two-date · tile-rule training", "2 two-date · production")]
out = {"code": "GeoAI-Roads 2ec5346", "roads under thin cloud": int(hazy.sum())}
for name, msk in groups.items():
    sub = roads[msk].reset_index(drop=True)
    acc = {k: round(float(np.mean(c_[msk] == y[msk])), 4) for k, c_ in calls.items()}
    cf = {k: int((c_[msk] == 1).sum()) for k, c_ in calls.items()}
    print(f"\n{name}: {int(msk.sum())} roads\n  share right: {json.dumps(acc, indent=0)}\n  called flooded: {json.dumps(cf, indent=0)}")
    vs1 = paired_report({k: c_[msk] for k, c_ in calls.items()}, "1 as it is · production", sub)
    print(vs1.to_string())
    pr = []
    for a, b in pairs:
        r = paired_report({a: calls[a][msk], b: calls[b][msk]}, b, sub).iloc[0].to_dict()
        pr.append({"arm": a, "against": b, **{k: r[k] for k in ("roads fixed", "roads broken", "McNemar p")}})
    print(pd.DataFrame(pr).to_string())
    out[name] = {"roads": int(msk.sum()), "share right": acc, "called flooded": cf, "vs arm 1": vs1.to_dict("records"), "pairs": pr}
res = roads[["tile_id", "road_id", "flooded"]].copy()
res["hazy"], res["assessable"], res["tile_rule"] = hazy, keep, tile_rule
for k, c_ in calls.items():
    res[f"call: {k}"] = c_
res.to_csv("cloudvars_calls.csv", index=False)
json.dump(out, open("cloudvars_numbers.json", "w"), indent=1)
print("saved", round(time.time() - t0), "s")
