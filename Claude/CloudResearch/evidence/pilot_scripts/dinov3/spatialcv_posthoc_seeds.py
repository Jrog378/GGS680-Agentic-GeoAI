"""POST HOC, not in the plan (written 2026-10-26 ~19:15, after the seed-662 spatial-fold results of the frozen Track B
arms were seen). The plan gives Agent C the seed-662 spatial folds only. Under them several frozen DINOv3 vector arms
cleared the "beats" bar against production, which they did not under last night's tile folds. This asks whether that
holds over the plan's 21 fold seeds (662, then 1-20), with the same model seed (662), arms, roads and purge.

For each arm and road set: accuracy at every seed (mean, SD, min, max; seeds above / equal / below production), and the
plan's seed-averaged interval: each road's correctness averaged over the 21 seeds, the contrast against production
taken road by road, then whole blocks resampled (2,000, seed 662). CPU only; cached tables only.

    OMP_NUM_THREADS=1 /opt/miniconda3/bin/python3 -I spatialcv_posthoc_seeds.py > spatialcv_posthoc_seeds.log 2>&1
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
sys.argv = sys.argv[:1]
import spatialcv_common as C
import spatialcv_cpu as CPU      # arm definitions only

import numpy as np
import pandas as pd
from spatial_folds import SEEDS, spatial_folds

say = C.Log()
ARMS = [CPU.PROD, CPU.BEST, "base + DINOv3 cues", "base + DINOv3 cues + vector", "base + DINOv2 + DINOv3 cues",
        "base + DINOv2 + DINOv3 cues + vectors", "DINOv3 cues + vector", "DINOv2 + DINOv3 cues + vectors"]
roads, rule, tile_rule = C.load_roads(gpu=False)
out = {"what": "POST HOC: frozen Track B arms over the 21 fold seeds (spatial folds, purged); model seed 662",
       "seeds": SEEDS}
for set_name, mask in (("891", tile_rule), ("798", rule)):
    sub = roads[mask].reset_index(drop=True)
    y = sub.flooded.astype(int).to_numpy()
    blocks = sub.tile_id.map(CPU.BLOCK_OF).to_numpy()
    names = [n for n in ARMS if set_name == "891" or n.startswith("base")]
    ok = {n: np.zeros((len(SEEDS), len(y)), bool) for n in names}
    for i, s in enumerate(SEEDS):
        folds = spatial_folds(sub, s)
        for n in names:
            red, cols = CPU.ARMS[n]
            ok[n][i] = CPU.cv_calls(CPU.factory(red), sub[cols], y, folds) == y
        say(f"{set_name} roads, fold seed {s}: " + ", ".join(f"{n} {ok[n][i].mean():.3f}" for n in names))
    if True:   # seed 662 must equal the main run's calls
        main = pd.read_csv(HERE / f"spatialcv_calls_B-frozen_{set_name}.csv")
        for n in names:
            assert np.array_equal(ok[n][0], main[f"S: {n}"].to_numpy() == y), n
    res = []
    prod = ok[CPU.PROD]
    for n in names:
        acc = ok[n].mean(1)
        a0 = prod.mean(1)
        row = {"arm": n, "accuracy at seed 662": float(acc[0]), "mean over 21 seeds": float(acc.mean()),
               "SD": float(acc.std(ddof=1)), "min": float(acc.min()), "max": float(acc.max())}
        if n != CPU.PROD:
            row["seeds above / equal / below production"] = [int((acc > a0).sum()), int((acc == a0).sum()),
                                                              int((acc < a0).sum())]
            d = ok[n].mean(0).astype(float) - prod.mean(0)
            boot = np.array([d[i].mean() for i in C.block_boot(blocks, 2000)])
            row["seed-averaged difference vs production"] = float(d.mean())
            row["seed-averaged 95% CI (blocks)"] = f"{np.percentile(boot, 2.5):+.3f} to {np.percentile(boot, 97.5):+.3f}"
            row["seed-averaged CI excludes 0"] = bool(np.percentile(boot, 2.5) > 0 or np.percentile(boot, 97.5) < 0)
        res.append(row)
    out[f"{set_name} roads"] = res
    say(f"{set_name} roads\n" + pd.DataFrame(res).to_string())
(HERE / "spatialcv_posthoc_seeds.json").write_text(json.dumps(out, indent=1))
say("done")
