"""POST-HOC (not in the plan; written after the phase 2 results): do the fine-tuned Track B gains on the validation
roads depend on roads that continue from a training tile? A road id (an OSM way) can cross a tile edge, so a
validation road can share its id, and its flooded label, with a road on a training tile. The arms are refitted
exactly as run_phase2.py fits them (same cues from phase2_cues.csv, same model and seed); the accuracies must
reproduce phase2_numbers.json. Then the validation roads are split by whether their id also occurs on a training
tile. Writes posthoc_shared_roads.csv (per-road calls) and posthoc_shared_roads.json here."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import dinov3_bench as d3

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from sn8_clouds import assessable
from sn8_dino import DINO_CUES, with_dino
from sn8_heldout import touched_roads
from sn8_models import FLOOD_MODELS
from sn8_stages import production_cloud_rule, production_features, production_model

roads = d3.with_dino3(with_dino(touched_roads(include_cloudy=True)))
assert set(roads.split) <= {"train", "val"}
cues = pd.read_csv(HERE / "phase2_cues.csv")
assert cues.tile_id.equals(roads.tile_id) and cues.road_id.equals(roads.road_id)
H3 = [f"d3head_flood_{s}" for s in ("mean", "max", "share")]
T3 = [f"d3ft_flood_{s}" for s in ("mean", "max", "share")]
roads[H3 + T3] = cues[H3 + T3].to_numpy()
base = [c for c in production_features() if c not in DINO_CUES]
ARMS = {"base + DINOv2 cues (production)": base + DINO_CUES, "base + DINOv3 cues (frozen)": base + d3.DINO3_CUES,
        "base + DINOv2 cues + DINOv3 head cues": base + DINO_CUES + H3,
        "base + DINOv2 cues + DINOv3 fine-tuned cues": base + DINO_CUES + T3,
        "base + DINOv3 fine-tuned cues": base + T3}
make = FLOOD_MODELS[production_model()]
logged = json.loads((HERE / "phase2_numbers.json").read_text())["Track B"]
train_ids = set(roads.road_id[roads.split == "train"])
out, rows = {}, []
for set_name, keep in (("tile rule", ~roads.cloudy.astype(bool).to_numpy()), ("production cloud rule",
                                                                              assessable(roads, production_cloud_rule()))):
    rs = roads[keep]
    tr, te = rs[rs.split == "train"], rs[rs.split == "val"].reset_index(drop=True)
    y = te.flooded.astype(int).to_numpy()
    shared = te.road_id.isin(train_ids).to_numpy()
    calls = {n: make().fit(tr[c], tr.flooded.astype(int)).predict(te[c]) for n, c in ARMS.items()}
    ref = {r["features"]: r["accuracy"] for r in logged[set_name]["confusion"]}
    for n, p in calls.items():
        assert abs(np.mean(p == y) - ref[n]) < 1e-3, (set_name, n, np.mean(p == y), ref[n])
    res = {"validation roads": len(te), "sharing an id with a training road": int(shared.sum())}
    for grp, m in (("shared id", shared), ("not shared", ~shared)):
        g = {"roads": int(m.sum()), "flooded": int(y[m].sum())}
        for n, p in calls.items():
            g[n] = round(float(np.mean(p[m] == y[m])), 3) if m.any() else None
        prod = calls["base + DINOv2 cues (production)"] == y
        for n in ("base + DINOv2 cues + DINOv3 fine-tuned cues", "base + DINOv3 fine-tuned cues"):
            ok = calls[n] == y
            fx, br = int((ok & ~prod & m).sum()), int((~ok & prod & m).sum())
            g[f"{n} vs production: fixed / broken / McNemar p"] = [fx, br, binomtest(fx, fx + br).pvalue if fx + br else 1.0]
        res[grp] = g
    out[set_name] = res
    rows.append(te[["tile_id", "road_id", "flooded"]].assign(set=set_name, shared_id=shared, **calls))
pd.concat(rows).to_csv(HERE / "posthoc_shared_roads.csv", index=False)
(HERE / "posthoc_shared_roads.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
