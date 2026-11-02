"""Pre-registered (outputs/preregistration_twodate_cornerfix.md): two-date de-hazing, model trained de-hazed, with
cloud-free tiles (empty gate) left exactly as they are. Development data only. Writes twodate_cornerfix_numbers.json
and twodate_cornerfix_calls.csv."""
import sys, time, json
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sn8_clouds import ROAD_CLOUD_CUT, assessable, _tile
from sn8_heldout import touched_roads, paired_report
from sn8_models import FLOOD_MODELS
from sn8_lines import road_band
from sn8_refhaze import cloud_gate, corrected_rows, corrected_table
from sn8_stages import production_cloud_rule, production_features, production_model
t0 = time.time()
roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
tile_rule = ~roads.cloudy.to_numpy()
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
haze_tiles = sorted(roads.tile_id[hazy].unique()); all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
gated = {}
for t in all_tiles:
    p, b, a, valid = _tile(t)
    gated[t] = bool(cloud_gate(b, a, valid)[0].any())
gate_tiles = [t for t in all_tiles if gated[t]]; empty = [t for t in all_tiles if not gated[t]]
print(f"tile-rule tiles {len(all_tiles)}: {len(gate_tiles)} with a cloud gate, {len(empty)} empty", round(time.time() - t0), "s", flush=True)
# check: the unchanged after image reproduces the as-it-is features (two empty-gate tiles)
for t in empty[:2]:
    r = pd.DataFrame(corrected_rows(t, "none", road_band())); r["_n"] = r.groupby("road_id").cumcount()
    a = roads[roads.tile_id == t].copy(); a["_n"] = a.groupby("road_id").cumcount()
    j = a[["road_id", "_n"] + cols].merge(r[["road_id", "_n"] + cols], on=["road_id", "_n"], how="left", suffixes=("", "_r"))
    assert len(j) == len(a) and len(a) > 0, f"{t}: roads missing"
    x, y_ = j[[k + "_r" for k in cols]].to_numpy(float), j[cols].to_numpy(float)
    ok = np.isclose(x, y_, rtol=1e-6, atol=1e-6, equal_nan=True)
    assert ok.all(), f"{t}: as-it-is features not reproduced, e.g. {np.array(cols)[~ok.all(axis=0)][:5]}"
print("check passed: unchanged image gives the as-it-is features", round(time.time() - t0), "s", flush=True)
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
c = corrected_table(gate_tiles, "darkref"); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
td = roads.copy()
m = td[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
on = td.tile_id.isin(gate_tiles).to_numpy()
assert (m.loc[on, "_merge"] == "both").all(), "missing corrected rows"
gaps = m.loc[on, cols].isna()
assert set(gaps.columns[gaps.any()]) <= {k for k in cols if k.startswith("vario")}, "unexpected missing features"
td.loc[on, cols] = m.loc[on, cols].to_numpy()
print("two-date features done", round(time.time() - t0), "s", flush=True)
y = roads.flooded.astype(int).to_numpy()
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
make = FLOOD_MODELS[production_model()]
call = np.full(len(roads), -1)
for tr, te in folds.split(roads, y, groups=roads.tile_id):
    t_ = tr[keep[tr]]
    call[te] = make().fit(td.iloc[t_][cols], y[t_]).predict(td.iloc[te][cols])
cv = pd.read_csv("cloudvars_calls.csv"); tw = pd.read_csv("twodate_calls.csv")
assert cv.tile_id.equals(roads.tile_id) and tw.tile_id.equals(roads.tile_id)
pd.DataFrame({"tile_id": roads.tile_id, "road_id": roads.road_id, "call: two-date · trained de-hazed (no corner edit)": call}).to_csv("twodate_cornerfix_calls.csv", index=False)
he = json.load(open("he_dehazed_numbers.json"))
calls = {"none": cv["call: 1 as it is · production"].to_numpy(),
         "two-date · trained de-hazed (2ec5346, corner edit)": cv["call: 2 two-date · production"].to_numpy(),
         "two-date · trained de-hazed": call}
on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
groups = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
          "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
          "control: assessable roads on the same tiles": (on_tiles & keep, "right")}
rng = np.random.default_rng(662); out = {"code": "GeoAI-Roads 5d325d9, empty-gate tiles left as they are",
                                         "tiles with a gate": len(gate_tiles), "tiles without": len(empty)}
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
    print(f"\n{name}: {int(msk.sum())} roads ({measure})")
    for k, r in res.items():
        print(f"  {k:52s} {r['count']:4d}  {100 * r['share']:.1f}%  [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]")
    print(rep_none.to_string())
    out[name] = {"roads": int(msk.sum()), "measure": measure, "arms": res, "vs none": rep_none.to_dict("records")}
json.dump(out, open("twodate_cornerfix_numbers.json", "w"), indent=1)
print("saved", round(time.time() - t0), "s")
