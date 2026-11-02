"""Pre-registered (outputs/preregistration_he_dehazed_training.md): single-image de-hazing (He), model trained on
de-hazed images, against none and two-date trained de-hazed. Also tile-resampled 95% intervals per arm and group for
the slide 7 bars. Development data only. Writes he_dehazed_numbers.json."""
import sys, time, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sn8_clouds import ROAD_CLOUD_CUT, assessable
from sn8_heldout import touched_roads, paired_report
from sn8_models import FLOOD_MODELS
from sn8_refhaze import corrected_table
from sn8_stages import production_cloud_rule, production_features, production_model
t0 = time.time()
roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
tile_rule = ~roads.cloudy.to_numpy()
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
haze_tiles = sorted(roads.tile_id[hazy].unique()); all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
c = corrected_table(all_tiles, "dehaze"); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
he = roads.copy()
m = he[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
on = he.tile_id.isin(all_tiles).to_numpy()
assert (m.loc[on, "_merge"] == "both").all(), "missing corrected rows"
# semivariogram() is NaN on a flat region by design; the production pipeline fills NaN with the median (deviation
# logged in the test plan: 1 road, 0_16_12, flat after single-image de-hazing)
gaps = m.loc[on, cols].isna()
assert set(gaps.columns[gaps.any()]) <= {k for k in cols if k.startswith("vario")}, "unexpected missing features"
print("roads with undefined variogram after de-hazing:", int(gaps.any(axis=1).sum()), flush=True)
he.loc[on, cols] = m.loc[on, cols].to_numpy()
print("single-image features done", round(time.time() - t0), "s", flush=True)
y = roads.flooded.astype(int).to_numpy()
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
make = FLOOD_MODELS[production_model()]
call = np.full(len(roads), -1)
for tr, te in folds.split(roads, y, groups=roads.tile_id):
    t_ = tr[keep[tr]]
    call[te] = make().fit(he.iloc[t_][cols], y[t_]).predict(he.iloc[te][cols])
cv = pd.read_csv("cloudvars_calls.csv"); td = pd.read_csv("twodate_calls.csv")
pd.DataFrame({"tile_id": roads.tile_id, "road_id": roads.road_id, "call: He 2011 · trained de-hazed": call}).to_csv("he_dehazed_calls.csv", index=False)
assert cv.tile_id.equals(roads.tile_id) and td.tile_id.equals(roads.tile_id)
calls = {"none": cv["call: 1 as it is · production"].to_numpy(),
         "two-date · trained as it is": td["call: two-date"].to_numpy(),
         "He 2011 · trained as it is": td["call: single image (He)"].to_numpy(),
         "two-date · trained de-hazed": cv["call: 2 two-date · production"].to_numpy(),
         "He 2011 · trained de-hazed": call}
on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
groups = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
          "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
          "control: assessable roads on the same tiles": (on_tiles & keep, "right")}
rng = np.random.default_rng(662); out = {"code": "GeoAI-Roads 5d325d9"}
for name, (msk, measure) in groups.items():
    sub = roads[msk].reset_index(drop=True); tiles = sub.tile_id.to_numpy(); ys = y[msk]
    idx = [np.flatnonzero(tiles == t) for t in np.unique(tiles)]
    boot = [np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))]) for _ in range(5000)]
    res = {}
    for k, c_ in calls.items():
        v = (c_[msk] == 1) if measure in ("found", "called flooded") else (c_[msk] == ys)
        dist = [v[b].mean() for b in boot]
        res[k] = {"share": round(float(v.mean()), 4), "count": int(v.sum()), "lo": round(float(np.percentile(dist, 2.5)), 4),
                  "hi": round(float(np.percentile(dist, 97.5)), 4)}
    rep_none = paired_report({k: c_[msk] for k, c_ in calls.items()}, "none", sub)
    rep_td = paired_report({"He 2011 · trained de-hazed": calls["He 2011 · trained de-hazed"][msk],
                            "two-date · trained de-hazed": calls["two-date · trained de-hazed"][msk]}, "two-date · trained de-hazed", sub)
    print(f"\n{name}: {int(msk.sum())} roads ({measure})")
    for k, r in res.items():
        print(f"  {k:30s} {r['count']:4d}  {100 * r['share']:.1f}%  [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]")
    print(rep_none.to_string()); print(rep_td.to_string())
    out[name] = {"roads": int(msk.sum()), "measure": measure, "arms": res, "vs none": rep_none.to_dict("records"),
                 "He vs two-date (both trained de-hazed)": rep_td.to_dict("records")}
json.dump(out, open("he_dehazed_numbers.json", "w"), indent=1)
print("saved", round(time.time() - t0), "s")
