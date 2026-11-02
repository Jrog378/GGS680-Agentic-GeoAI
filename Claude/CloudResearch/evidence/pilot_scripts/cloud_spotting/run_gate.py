"""The chosen library spotter as the cloud gate on the SpaceNet 8 development roads (preregistration, section
"SpaceNet 8"). Reads the chosen arm from numbers.json (summarise.py). Writes gate_roads.csv, gate_numbers.json and
prints the tables (gate.log)."""
import json
import sys
import time

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from sn8_clouds import ROAD_CLOUD_CUT, assessable, cloud_table
from sn8_cloudspot import LIBRARY_ARMS, CloudSpotter, spot_gate, spot_table
from sn8_grey import GREY_DIR
from sn8_heldout import gated_calls, gated_report, paired_report, touched_roads
from sn8_models import FLOOD_MODELS
from sn8_stages import production_cloud_rule, production_features, production_model

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
t0 = time.time()
log = lambda m: print(f"{time.time() - t0:7.0f} s  {m}", flush=True)
chosen = json.load(open(f"{HERE}/choice.json"))["chosen"]
log(f"chosen library spotter: {chosen} {LIBRARY_ARMS[chosen]}")

# development tiles only
index = pd.read_csv(GREY_DIR / "tiles.csv")
dev = set(index.tile_id[index.split.isin(["train", "val"])])
assert len(dev) == 226, len(dev)
spotter = CloudSpotter(LIBRARY_ARMS[chosen]).fit()
log("spotter fitted on the 120 HRC_WHU development images")
parts = []
for split in ("train", "val"):
    s = spot_table(split, spotter, log=None)
    c = cloud_table(split)
    assert set(s.tile_id) <= dev
    gap = np.abs(s.check_dark_rise_road.to_numpy() - c.cloud_dark_rise_road.to_numpy()).max()
    assert gap < 1e-9, f"strip code does not reproduce cloud_dark_rise_road ({gap})"
    parts.append(s)
    log(f"{split}: {len(s)} roads; dark-rise check max difference {gap:.2e}")
spot = pd.concat(parts, ignore_index=True)

roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
assert set(roads.tile_id) <= dev
assert spot.tile_id.equals(roads.tile_id) and spot.road_id.equals(roads.road_id)
roads["spot_road"], roads["spot_tile"] = spot.spot_road.to_numpy(), spot.spot_tile.to_numpy()
y = roads.flooded.astype(int).to_numpy()
tile_rule = ~roads.cloudy.astype(bool).to_numpy()
rule_flag = roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT
spot_flag = roads.spot_road.to_numpy() >= ROAD_CLOUD_CUT
out = {"chosen": chosen, "columns": LIBRARY_ARMS[chosen], "roads": len(roads), "tiles": int(roads.tile_id.nunique()),
       "flooded": int(y.sum())}

# agreement of the two road rules
agree = []
for scope, m in (("all roads", np.ones(len(roads), bool)), ("roads the tile rule keeps", tile_rule)):
    a, b = rule_flag & m, spot_flag & m
    agree.append({"scope": scope, "roads": int(m.sum()), "road rule flags": int(a.sum()), "spotter flags": int(b.sum()),
                  "both": int((a & b).sum()), "road rule only": int((a & ~b).sum()), "spotter only": int((~a & b).sum()),
                  "either": int((a | b).sum()), "Jaccard": (a & b).sum() / max((a | b).sum(), 1),
                  "flooded among road rule only": int((a & ~b & (y == 1)).sum()),
                  "flooded among spotter only": int((~a & b & (y == 1)).sum())})
agree = pd.DataFrame(agree)
print(f"\n== roads flagged cloudy (share of strip >= {ROAD_CLOUD_CUT}) ==\n{agree.round(3).to_string(index=False)}")
out["agreement"] = agree.round(4).to_dict("records")
tiles = roads.groupby("tile_id").agg(spot_tile=("spot_tile", "first"), rise_road=("cloud_dark_rise_road", "mean"))
out["tile share: spotter vs mean road dark-rise share, Spearman"] = float(tiles.spot_tile.corr(tiles.rise_road, "spearman"))
print("tiles with spotter share > 5% of the scored grid:", int((tiles.spot_tile > 0.05).sum()), "of", len(tiles))
out["tiles with spotter share > 5%"] = int((tiles.spot_tile > 0.05).sum())

# the flood model with each gate
keep = {"production (tile rule + road rule)": assessable(roads, production_cloud_rule()),
        f"spotter (tile rule + {chosen} road rule)": spot_gate(roads)}
assert production_cloud_rule() == "tile rule + road rule"
cols = production_features()
make = FLOOD_MODELS[production_model()]
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
log(f"flood model {production_model()} on {len(cols)} production features")
calls = {k: gated_calls(make, roads, cols, v, folds) for k, v in keep.items()}
rep = gated_report(calls, roads)
print(f"\n== each gate, held-out calls on the roads it keeps ==\n{rep.to_string(index=False)}")
out["gated report"] = rep.to_dict("records")
conf = []
for k, c in calls.items():
    a = c >= 0
    conf.append({"gate": k, "kept": int(a.sum()), "set aside": int((~a).sum()),
                 "flooded set aside": int((~a & (y == 1)).sum()), "dry set aside": int((~a & (y == 0)).sum()),
                 "TP": int(((c == 1) & (y == 1)).sum()), "FN": int(((c == 0) & (y == 1)).sum()),
                 "FP": int(((c == 1) & (y == 0)).sum()), "TN": int(((c == 0) & (y == 0)).sum())})
conf = pd.DataFrame(conf)
print(f"\n== confusion matrices on the kept roads ==\n{conf.to_string(index=False)}")
out["confusion"] = conf.to_dict("records")
kp, ks = keep.values()
shared = kp & ks
sub = roads[shared].reset_index(drop=True)
names = list(calls)
pr = paired_report({"production": calls[names[0]][shared], "spotter": calls[names[1]][shared]}, "production", sub)
acc = {k: float(np.mean(c[shared] == y[shared])) for k, c in zip(("production", "spotter"), calls.values())}
print(f"\n== shared roads (kept by both): {int(shared.sum())} ==\naccuracy {acc}\n{pr.to_string(index=False)}")
out["shared"] = {"roads": int(shared.sum()), "flooded": int(y[shared].sum()), "accuracy": acc,
                 "paired": pr.to_dict("records")}
only = []
for label, m, c in (("kept by production only", kp & ~ks, calls[names[0]]), ("kept by spotter only", ks & ~kp, calls[names[1]])):
    only.append({"roads": label, "n": int(m.sum()), "flooded": int((m & (y == 1)).sum()), "dry": int((m & (y == 0)).sum()),
                 "called flooded": int((m & (c == 1)).sum()), "right": int((m & (c == y)).sum()),
                 "accuracy": float(np.mean(c[m] == y[m])) if m.any() else np.nan,
                 "median dark-rise share": float(np.median(roads.cloud_dark_rise_road[m])) if m.any() else np.nan,
                 "median spotter share": float(np.median(roads.spot_road[m])) if m.any() else np.nan})
only = pd.DataFrame(only)
print(f"\n== roads only one gate keeps (that gate's calls) ==\n{only.round(3).to_string(index=False)}")
out["only one gate"] = only.round(4).to_dict("records")
res = roads[["tile_id", "road_id", "split", "flooded", "cloudy", "cloud_dark_rise_road", "spot_road", "spot_tile"]].copy()
for k, c in calls.items():
    res[f"call: {k}"] = c
res.to_csv(f"{HERE}/gate_roads.csv", index=False)
json.dump(out, open(f"{HERE}/gate_numbers.json", "w"), indent=1, default=float)
log("saved gate_roads.csv and gate_numbers.json")
