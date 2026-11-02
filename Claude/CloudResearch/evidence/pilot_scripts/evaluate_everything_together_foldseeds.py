"""POST HOC (chosen 2026-10-26 ~00:30 EDT, after seeing evaluate_everything_together.py's results; not in the test
plan). Why: the best-so-far arm's gain over production on the 798 assessable roads was +0.1 points with production's
fold split (seed 662 over the 798) but +2.3 points (p = 0.001) with tonight's split (seed 662 over all 1,037 roads),
so the arm differences may be mostly fold luck. Check: the primary comparison (set (i), the 798, folds over the 798,
production model, model seed 662 unchanged) repeated over 20 other fold seeds (1-20); per seed the accuracy of each
arm, the gain over production, McNemar's exact test and the promotion rule (sn8_stages.confirm, read-only).
Development data only; cached tables only. Writes everything_together_foldseeds.json and .csv."""
import sys, time, json, hashlib
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
import sn8_dino as D
import sn8_refhaze as R
from sn8_lines import road_band
from sn8_clouds import assessable, _tile
from sn8_dino import DINO_CUES, DINO_VECTOR, ReduceColumns, with_dino
from sn8_heldout import paired_report, touched_roads
from sn8_models import FLOOD_MODELS
from sn8_refhaze import cloud_gate
from sn8_results import RESULTS_DIR
from sn8_stages import confirm, production_cloud_rule, production_features, production_model
HERE = Path(__file__).resolve().parent
t0 = time.time()
for split in ("train", "val"):
    _, csv, npz = D._paths(split)
    if not (csv.exists() and npz.exists()):
        sys.exit(f"STOP: DINOv2 cache miss for {split}; not recomputing")
REGISTRY = RESULTS_DIR / "production.json"
registry_hash = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()


def cache_path(tiles, method):
    """The file corrected_table(tiles, method) reads (read-only copy of sn8_refhaze's key, as the main script)."""
    import inspect
    code = [hashlib.sha256(inspect.getsource(f).encode()).hexdigest() for f in (
        R._robust_global, R._local_fit, R.reference_dehaze, R.cloud_gate, R.tone_curve, R.dark_reference_dehaze,
        R._corrected_pair, R.corrected_rows)]
    key = hashlib.sha256(json.dumps([R.SPLIT_FINGERPRINT, sorted(tiles), method, road_band(), R.REF_WIN, R.REF_PASSES,
                                     R.REF_K, R.T_MIN, R.DARKREF_MIN_CLOUD_M2, R.DARKREF_CLEAR_MARGIN_PX,
                                     R.DARKREF_GATE_MARGIN_PX, R.DARKREF_GUIDED, R.TONE_QUANTILES, *code]).encode()
                         ).hexdigest()[:16]
    return R.CACHE_DIR / f"road_corrected_{method}_{key}.csv"


def cached_table(tiles, method):
    if not cache_path(tiles, method).exists():
        sys.exit(f"STOP: cache miss for {method}; not recomputing")
    return R.corrected_table(tiles, method)


def merged(roads, tiles, c, cols, what):
    """As in evaluate_everything_together.py."""
    c = c.copy(); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
    out = roads.copy()
    m = out[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
    on = out.tile_id.isin(tiles).to_numpy()
    assert (m.loc[on, "_merge"] == "both").all(), f"{what}: missing corrected rows"
    out.loc[on, cols] = m.loc[on, cols].to_numpy()
    return out


roads = with_dino(touched_roads(include_cloudy=True))
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
tile_rule = ~roads.cloudy.astype(bool).to_numpy()
all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
gate_tiles = [t for t in all_tiles if bool(cloud_gate(*_tile(t)[1:])[0].any())]
assert (len(all_tiles), len(gate_tiles), int(keep.sum())) == (200, 99, 798)
light = roads[["tile_id", "road_id"] + cols].copy(); light["_n"] = light.groupby(["tile_id", "road_id"]).cumcount()
td = merged(light, gate_tiles, cached_table(gate_tiles, "darkref"), cols, "two-date (no corner edit)")
he = merged(light, all_tiles, cached_table(all_tiles, "dehaze"), cols, "He 2011")
X = pd.concat([roads[cols + DINO_VECTOR], td[cols].add_prefix("td_"), he[cols].add_prefix("he_")], axis=1)
TD, HE = ["td_" + c for c in cols], ["he_" + c for c in cols]
y = roads.flooded.astype(int).to_numpy()
make = FLOOD_MODELS[production_model()]
PROD, BEST, BOTH, ALL, NO_CLS = ("production", "production + DINOv2 vector (best so far)", "both cues",
                                 "everything together", "without classical (raw)")
ARMS = {PROD: cols, BEST: cols + DINO_VECTOR, BOTH: TD + HE, ALL: cols + TD + HE + DINO_VECTOR,
        NO_CLS: DINO_CUES + TD + HE + DINO_VECTOR}
print("built", round(time.time() - t0), "s", flush=True)

idx = np.flatnonzero(keep)
Xs, ys, tiles = X.iloc[idx].reset_index(drop=True), y[idx], roads.tile_id.to_numpy()[idx]
sub = roads.iloc[idx].reset_index(drop=True)


def calls_for(columns, seed):
    out = np.zeros(len(idx), int)
    for tr, te in StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed).split(Xs, ys, groups=tiles):
        model = make_pipeline(ReduceColumns(DINO_VECTOR), make()) if DINO_VECTOR[0] in columns else make()
        out[te] = model.fit(Xs.iloc[tr][columns], ys[tr]).predict(Xs.iloc[te][columns])
    return out


rows = []
for seed in [662] + list(range(1, 21)):
    preds = {k: calls_for(c, seed) for k, c in ARMS.items()}
    if seed == 662:   # check: reproduces set (i) of the main run
        assert int(((preds[PROD] == 1) & (ys == 1)).sum()) == 394 and int((preds[ALL] == ys).sum()) == 667
    rep = paired_report(preds, PROD, sub)
    best = paired_report({ALL: preds[ALL], BEST: preds[BEST]}, BEST, sub).iloc[0]
    row = {"fold seed": seed, **{f"accuracy: {k}": float((p == ys).mean()) for k, p in preds.items()}}
    for _, r in rep.iterrows():
        ok, _ = confirm(r)
        row[f"gain: {r['features']}"] = float(r["vs production"])
        row[f"fixed/broken: {r['features']}"] = f"{r['roads fixed']}/{r['roads broken']}"
        row[f"McNemar p: {r['features']}"] = float(r["McNemar p"])
        row[f"would pass: {r['features']}"] = bool(ok)
    row["everything minus best so far"] = float(best[f"vs {BEST}"])
    row["McNemar p: everything vs best so far"] = float(best["McNemar p"])
    rows.append(row)
    print(f"seed {seed:3d}: " + "  ".join(f"{k[:26]} {100 * row[f'accuracy: {k}']:.1f}" for k in ARMS)
          + f"  | rule passes: " + ", ".join(k for k in ARMS if k != PROD and row[f"would pass: {k}"]),
          round(time.time() - t0), "s", flush=True)

df = pd.DataFrame(rows)
df.to_csv(HERE / "everything_together_foldseeds.csv", index=False)
new = df[df["fold seed"] != 662]
summary = {}
for k in ARMS:
    a = new[f"accuracy: {k}"]
    summary[k] = {"mean accuracy": float(a.mean()), "sd": float(a.std(ddof=1)), "min": float(a.min()),
                  "max": float(a.max())}
    if k != PROD:
        g = new[f"gain: {k}"]
        summary[k].update({"mean gain vs production": float(g.mean()), "min gain": float(g.min()),
                           "max gain": float(g.max()), "seeds with gain > 0": int((g > 0).sum()),
                           "seeds the rule passes": int(new[f"would pass: {k}"].sum()),
                           "seeds with McNemar p < 0.05": int((new[f"McNemar p: {k}"] < 0.05).sum())})
e = new["everything minus best so far"]
summary["everything minus best so far"] = {"mean": float(e.mean()), "min": float(e.min()), "max": float(e.max()),
                                           "seeds > 0": int((e > 0).sum()), "seeds < 0": int((e < 0).sum()),
                                           "seeds with McNemar p < 0.05": int((new["McNemar p: everything vs best so far"] < 0.05).sum())}
assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == registry_hash
json.dump({"post hoc": __doc__, "seeds": [int(s) for s in new["fold seed"]], "summary over the 20 new seeds": summary},
          open(HERE / "everything_together_foldseeds.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print("saved", round(time.time() - t0), "s")
