"""Test plan: outputs/preregistration_pipeline_factorial.md (Justin 2026-10-26: "Use all these techniques together. it
should be a pipeline of tools that all interact to get the optimal result test with and without them to understand
their impacts strengths and weaknesses as well as the optimal combos").

The library pipeline as a full factorial, 2 x 4 x 2 = 16 arms, every arm the production flood model (tuned random
forest) trained on the roads its gate keeps:
  1 gate:     a production (tile rule + dark-rise road rule) | b spotter (tile rule + bright + texture + DINOv2 road
              rule, same 20% strip cut; per-road shares read from cloud_spotting/gate_roads.csv)
  2 cues:     raw 96 | td 96 (two-date, no corner edit, in place of raw) | he 96 (He 2011, in place of raw) |
              both (raw + td_ + he_)
  3 features: prod (the stage-2 columns) | vec (+ the DINOv2 change vector, 16 PCs fitted inside each fold)
Folds over all 1,037 development roads by tile (StratifiedGroupKFold 5, seed 662, then seeds 1-20); each fold's model
fitted on the training-fold roads its gate keeps; every held-out road called. Development data only; cached tables
only (a cache miss stops the script: no GPU). Calls of every seed are cached in pipeline_factorial_seed_calls.npz, so
the scoring can be rerun without refitting. Writes pipeline_factorial_numbers.json, pipeline_factorial_calls.csv and
pipeline_factorial_seeds.csv."""
import sys, time, json, hashlib, inspect
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from scipy.stats import binomtest
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
import sn8_dino as D
import sn8_refhaze as R
from sn8_clouds import ROAD_CLOUD_CUT, assessable, _tile
from sn8_cloudspot import spot_gate
from sn8_dino import DINO_CUES, DINO_VECTOR, ReduceColumns, with_dino
from sn8_heldout import held_out_report, paired_report, touched_roads
from sn8_lines import road_band
from sn8_models import FLOOD_MODELS
from sn8_refhaze import cloud_gate, corrected_table
from sn8_results import RESULTS_DIR
from sn8_stages import confirm, production_cloud_rule, production_features, production_model
HERE = Path(__file__).resolve().parent
SPOT_CSV = HERE / "cloud_spotting" / "gate_roads.csv"
SEED_CALLS = HERE / "pipeline_factorial_seed_calls.npz"
SEED = 662
SEEDS = [662] + list(range(1, 21))
SMOKE = len(sys.argv) > 1 and sys.argv[1] == "--smoke"     # 2 seeds, outputs to the folder given as argv[2]
OUT = Path(sys.argv[2]) if SMOKE else HERE
if SMOKE:            # a test of the scoring code: its own copy of the seed cache, its own outputs
    SEEDS = [662, 1]
    SEED_CALLS = OUT / "pipeline_factorial_seed_calls.npz"
N_BOOT, N_BOOT_GROUP = 2000, 5000
t0 = time.time()


def stamp():
    return f"{round(time.time() - t0)} s"


# --- guards: no GPU (DINOv2 caches must exist), production.json must not change -------------------------------------
for split in ("train", "val"):
    _, csv, npz = D._paths(split)
    if not (csv.exists() and npz.exists()):
        sys.exit(f"STOP: DINOv2 cache miss for {split} ({csv.name}); not recomputing (the GPU is in use elsewhere)")
REGISTRY = RESULTS_DIR / "production.json"
registry_hash = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()


def cache_path(tiles, method):
    """The file corrected_table(tiles, method) reads; same key as sn8_refhaze.corrected_table (read-only copy, as in
    evaluate_everything_together.py)."""
    code = [hashlib.sha256(inspect.getsource(f).encode()).hexdigest() for f in (
        R._robust_global, R._local_fit, R.reference_dehaze, R.cloud_gate, R.tone_curve, R.dark_reference_dehaze,
        R._corrected_pair, R.corrected_rows)]
    key = hashlib.sha256(json.dumps([R.SPLIT_FINGERPRINT, sorted(tiles), method, road_band(), R.REF_WIN, R.REF_PASSES,
                                     R.REF_K, R.T_MIN, R.DARKREF_MIN_CLOUD_M2, R.DARKREF_CLEAR_MARGIN_PX,
                                     R.DARKREF_GATE_MARGIN_PX, R.DARKREF_GUIDED, R.TONE_QUANTILES, *code]).encode()
                         ).hexdigest()[:16]
    return R.CACHE_DIR / f"road_corrected_{method}_{key}.csv"


def cached_table(tiles, method):
    p = cache_path(tiles, method)
    if not p.exists():
        sys.exit(f"STOP: cache miss for {method} on {len(tiles)} tiles ({p.name}); not recomputing")
    print(f"cache hit: {p.name}", flush=True)
    return corrected_table(tiles, method)


def merged(roads, tiles, c, cols, what):
    """roads with cols replaced by the corrected table c on the given tiles (as evaluate_everything_together.py)."""
    c = c.copy(); c["_n"] = c.groupby(["tile_id", "road_id"]).cumcount()
    out = roads.copy()
    m = out[["tile_id", "road_id", "_n"]].merge(c, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
    on = out.tile_id.isin(tiles).to_numpy()
    assert (m.loc[on, "_merge"] == "both").all(), f"{what}: missing corrected rows"
    gaps = m.loc[on, cols].isna()
    assert set(gaps.columns[gaps.any()]) <= {k for k in cols if k.startswith("vario")}, f"{what}: unexpected gaps"
    print(f"{what}: roads with undefined variogram cues: {int(gaps.any(axis=1).sum())}", flush=True)
    out.loc[on, cols] = m.loc[on, cols].to_numpy()
    return out


# --- roads, gates and cues --------------------------------------------------------------------------------------------
roads = with_dino(touched_roads(include_cloudy=True))
assert set(roads.split) <= {"train", "val"}, "development roads only"
spot = pd.read_csv(SPOT_CSV)
assert spot.tile_id.equals(roads.tile_id) and spot.road_id.equals(roads.road_id), "gate_roads.csv row order differs"
assert set(spot.split) <= {"train", "val"}
assert (spot.cloudy.astype(bool).to_numpy() == roads.cloudy.astype(bool).to_numpy()).all()
assert np.abs(spot.cloud_dark_rise_road.to_numpy() - roads.cloud_dark_rise_road.to_numpy()).max() < 1e-12
assert (spot.flooded.astype(bool).to_numpy() == roads.flooded.astype(bool).to_numpy()).all()
roads["spot_road"] = spot.spot_road.to_numpy()
y = roads.flooded.astype(int).to_numpy()
tiles_all = roads.tile_id.to_numpy()
GATES = {"a": assessable(roads, production_cloud_rule()), "b": spot_gate(roads)}
GATE_NAME = {"a": "production gate (dark-rise road rule)", "b": "spotter gate (bright + texture + DINOv2 road rule)"}
shared = GATES["a"] & GATES["b"]
tile_rule = ~roads.cloudy.astype(bool).to_numpy()
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
assert (len(roads), int(GATES["a"].sum()), int(GATES["b"].sum()), int(shared.sum()), int(hazy.sum())) == \
    (1037, 798, 790, 757, 93), "road counts differ from last night"
haze_tiles = sorted(roads.tile_id[hazy].unique()); all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
assert len(cols) == 96 and cols[-3:] == DINO_CUES
print(f"production model: {production_model()}; cloud rule: {production_cloud_rule()}; {len(cols)} production "
      f"features; {len(roads)} development roads; kept a {int(GATES['a'].sum())}, b {int(GATES['b'].sum())}, "
      f"shared {int(shared.sum())}", stamp(), flush=True)
gate_tiles = [t for t in all_tiles if bool(cloud_gate(*_tile(t)[1:])[0].any())]
assert (len(all_tiles), len(gate_tiles), len(haze_tiles)) == (200, 99, 39), "tile counts differ from the earlier arms"
print(f"tile-rule tiles {len(all_tiles)}: {len(gate_tiles)} with a cloud gate", stamp(), flush=True)
light = roads[["tile_id", "road_id"] + cols].copy(); light["_n"] = light.groupby(["tile_id", "road_id"]).cumcount()
td = merged(light, gate_tiles, cached_table(gate_tiles, "darkref"), cols, "two-date (no corner edit)")
he = merged(light, all_tiles, cached_table(all_tiles, "dehaze"), cols, "He 2011")
X = pd.concat([roads[cols + DINO_VECTOR], td[cols].add_prefix("td_"), he[cols].add_prefix("he_")], axis=1)
assert X.index.equals(roads.index) and X.shape[1] == 96 + 1024 + 192
TD, HE = ["td_" + c for c in cols], ["he_" + c for c in cols]
CUES = {"raw": cols, "td": TD, "he": HE, "both": cols + TD + HE}
CUE_NAME = {"raw": "none (raw)", "td": "two-date", "he": "He 2011", "both": "both cues + raw"}
FEATS = {"prod": [], "vec": DINO_VECTOR}
FEAT_NAME = {"prod": "production features", "vec": "+ DINOv2 change vector"}
TOOLS = {"a": 0, "b": 1, "raw": 0, "td": 1, "he": 1, "both": 2, "prod": 0, "vec": 1}
CELLS = [(g, c, f) for g in GATES for c in CUES for f in FEATS]
ARMS = {f"{g}·{c}·{f}": (g, CUES[c] + FEATS[f]) for g, c, f in CELLS}
NAMES = list(ARMS)
PROD = "a·raw·prod"
assert NAMES[0] == PROD and len(NAMES) == 16
tools = {n: sum(TOOLS[p] for p in n.split("·")) for n in NAMES}
make = FLOOD_MODELS[production_model()]
fingerprint = hashlib.sha256(json.dumps([NAMES, [ARMS[n][1] for n in NAMES], len(roads), int(shared.sum()),
                                         production_model()]).encode()).hexdigest()[:16]


def arm_calls(columns, keep, folds):
    """Each fold's model fitted on its training-fold roads that `keep` lets in; every held-out road called."""
    call = np.full(len(roads), -1)
    for tr, te in folds:
        tr = tr[keep[tr]]
        model = make_pipeline(ReduceColumns(DINO_VECTOR), make()) if DINO_VECTOR[0] in columns else make()
        call[te] = model.fit(X.iloc[tr][columns], y[tr]).predict(X.iloc[te][columns])
    return call


# --- reproduction checks at the primary seed (stop if any fails); run before the other seeds are fitted --------------
def counts(c, msk):
    p, t = c[msk], y[msk]
    return int(((p == 1) & (t == 1)).sum()), int(((p == 0) & (t == 1)).sum()), int(((p == 1) & (t == 0)).sum()), \
        int(((p == 0) & (t == 0)).sum())


ka, kb = GATES["a"], GATES["b"]
CHECKS = ["a·raw·prod = cloudvars_calls.csv production (1,037 roads, call for call); 390/51/91/266 on its 798",
          "b·raw·prod = gate_roads.csv spotter calls on its 790 kept roads; 416/34/88/252",
          "a·raw·vec, a·both·prod, a·both·vec = everything_together_calls.csv C1037 best so far / without the vector / "
          "everything together (call for call)",
          "a·td·prod = twodate_cornerfix_calls.csv; a·he·prod = he_dehazed_calls.csv (call for call)",
          "757 shared roads, 798 / 790 kept; gate_roads.csv dark-rise shares match the road table"]


def reproduce(primary):
    call0 = {n: primary[i] for i, n in enumerate(NAMES)}
    cv = pd.read_csv(HERE / "cloudvars_calls.csv"); et = pd.read_csv(HERE / "everything_together_calls.csv")
    fx = pd.read_csv(HERE / "twodate_cornerfix_calls.csv"); hc = pd.read_csv(HERE / "he_dehazed_calls.csv")
    for f in (cv, et, fx, hc):
        assert f.tile_id.equals(roads.tile_id) and f.road_id.equals(roads.road_id), "calls CSV row order differs"
    same = [(PROD, cv["call: 1 as it is · production"]),
            ("a·raw·vec", et["C1037 · production + DINOv2 vector (best so far)"]),
            ("a·both·prod", et["C1037 · without the DINOv2 vector"]), ("a·both·vec", et["C1037 · everything together"]),
            ("a·td·prod", fx["call: two-date · trained de-hazed (no corner edit)"]),
            ("a·he·prod", hc["call: He 2011 · trained de-hazed"])]
    for n, logged in same:
        assert (call0[n] == logged.to_numpy()).all(), f"STOP: {n} does not reproduce the logged calls"
    assert (call0[PROD][ka] == spot["call: production (tile rule + road rule)"].to_numpy()[ka]).all()
    assert (call0["b·raw·prod"][kb] ==
            spot["call: spotter (tile rule + classical + DINOv2 - dark road rule)"].to_numpy()[kb]).all()
    assert counts(call0[PROD], ka) == (390, 51, 91, 266) and counts(call0["b·raw·prod"], kb) == (416, 34, 88, 252)
    print("checks passed:", *CHECKS, sep="\n  ")
    print(stamp(), flush=True)


# --- calls for every seed (cached, resumable) -------------------------------------------------------------------------
done = {}
if SEED_CALLS.exists():
    z = np.load(SEED_CALLS, allow_pickle=False)
    if str(z["fingerprint"]) == fingerprint:
        done = {int(s): z["calls"][i] for i, s in enumerate(z["seeds"])}
        print(f"reusing cached calls for seeds {sorted(done)}", flush=True)
        if 662 in done:
            reproduce(done[662])
    else:
        print("cached calls are for other arms; recomputing", flush=True)
for s in SEEDS:
    if s in done:
        continue
    folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=s).split(X, y, groups=tiles_all))
    out = np.zeros((len(NAMES), len(roads)), np.int8)
    for i, n in enumerate(NAMES):
        g, columns = ARMS[n]
        out[i] = arm_calls(columns, GATES[g], folds)
    done[s] = out
    if s == 662:
        reproduce(out)
    acc = {n: (out[i][shared] == y[shared]).mean() for i, n in enumerate(NAMES)}
    print(f"seed {s:3d} called; shared-road accuracy " + " ".join(f"{n} {100 * a:.1f}" for n, a in acc.items()),
          stamp(), flush=True)
    order = list(done)                                   # every seed computed so far, cached or new
    tmp = SEED_CALLS.with_name(SEED_CALLS.stem + "_writing.npz")
    np.savez_compressed(tmp, fingerprint=fingerprint, seeds=np.array(order), calls=np.stack([done[x] for x in order]))
    tmp.replace(SEED_CALLS)                              # atomic, so a reader never sees half a file
for s in SEEDS:      # every seed's shared-road accuracy, also when the calls came from the cache
    print(f"seed {s:3d}: shared-road accuracy " + " ".join(
        f"{n} {100 * (done[s][i][shared] == y[shared]).mean():.1f}" for i, n in enumerate(NAMES)), flush=True)
C = np.stack([done[s] for s in SEEDS]).astype(int)        # (seed, arm, road)
assert (C >= 0).all() and set(np.unique(C)) <= {0, 1}
P = 0                                                       # index of the primary seed
call0 = {n: C[P, i] for i, n in enumerate(NAMES)}


# --- scoring helpers --------------------------------------------------------------------------------------------------
def plain(v):
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else float(f"{float(v):.6g}")
    if isinstance(v, np.ndarray):
        return plain(v.tolist())
    return v


def metrics(t, p):
    tp, fn = np.sum((p == 1) & (t == 1)), np.sum((p == 0) & (t == 1))
    fp, tn = np.sum((p == 1) & (t == 0)), np.sum((p == 0) & (t == 0))
    prec = tp / (tp + fp) if tp + fp else np.nan
    rec = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else np.nan
    den = np.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    mcc = (tp * tn - fp * fn) / den if den else 0.0
    return {"TP": tp, "FN": fn, "FP": fp, "TN": tn, "accuracy": (tp + tn) / len(t), "precision": prec, "recall": rec,
            "specificity": spec, "F1": f1, "MCC": mcc}


def boot_sets(msk, n_boot, rng=None):
    """Tile resamples of the roads in msk, drawn as sn8_heldout.held_out_report draws them."""
    tiles = tiles_all[msk]
    rng = np.random.default_rng(SEED) if rng is None else rng
    groups = [np.flatnonzero(tiles == g) for g in np.unique(tiles)]
    return [np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))]) for _ in range(n_boot)], \
        len(groups)


def score_set(msk, names, label):
    """Confusion matrix and metrics per arm on the roads in msk at the primary seed, each with a tile-resampled 95%
    interval (2,000 resamples, seed 662)."""
    sub = roads[msk].reset_index(drop=True); t = y[msk]
    boot, n_tiles = boot_sets(msk, N_BOOT)
    rows, preds = {}, {}
    for n in names:
        p = call0[n][msk]; preds[n] = p
        m = metrics(t, p)
        dist = pd.DataFrame([metrics(t[b], p[b]) for b in boot])
        for k in ("accuracy", "precision", "recall", "specificity", "F1", "MCC"):
            m[f"{k} 95% CI"] = [float(np.nanpercentile(dist[k], 2.5)), float(np.nanpercentile(dist[k], 97.5))]
        rows[n] = m
    logged = held_out_report(preds, sub)          # the logged format, as a check on the accuracy intervals
    for n in names:
        lo, hi = rows[n]["accuracy 95% CI"]
        assert logged.loc[logged.features == n, "accuracy 95% CI"].iloc[0] == f"{lo:.2f}-{hi:.2f}", n
    print(f"\n=== {label}: {int(msk.sum())} roads on {n_tiles} tiles ({int(t.sum())} flooded), seed 662")
    show = pd.DataFrame(rows).T[["TP", "FN", "FP", "TN", "accuracy", "precision", "recall", "specificity", "F1", "MCC"]]
    show["acc 95% CI"] = [f"{100 * r['accuracy 95% CI'][0]:.1f}-{100 * r['accuracy 95% CI'][1]:.1f}" for r in rows.values()]
    show["MCC 95% CI"] = [f"{r['MCC 95% CI'][0]:.3f}-{r['MCC 95% CI'][1]:.3f}" for r in rows.values()]
    print(show.to_string(float_format=lambda v: f"{v:.3f}"), flush=True)
    return rows, preds, sub


def exact_p(row):
    f, b = int(row["roads fixed"]), int(row["roads broken"])
    return binomtest(f, f + b, 0.5).pvalue if f + b else 1.0


def against_production(preds, sub, label):
    rep = paired_report(preds, PROD, sub)
    out = []
    for _, r in rep.iterrows():
        ok, why = confirm(r)
        out.append({**r.to_dict(), "McNemar p (unrounded)": exact_p(r), "rule": why, "would pass": ok})
    print(f"--- paired against production, {label}")
    print(pd.DataFrame(out).drop(columns=["rule"]).to_string(), flush=True)
    return out


# --- (i) shared roads, (ii) each gate's own roads ---------------------------------------------------------------------
shared_rows, shared_preds, shared_sub = score_set(shared, NAMES, "(i) shared roads, kept by both gates")
shared_paired = against_production(shared_preds, shared_sub, "(i) shared roads")
own = {}
for g in GATES:
    names_g = [n for n in NAMES if n.startswith(g + "·")]
    rows, preds, sub = score_set(GATES[g], names_g, f"(ii) {GATE_NAME[g]}: its own kept roads")
    keep = GATES[g]; only = keep & ~shared
    own[g] = {"gate": GATE_NAME[g], "kept": int(keep.sum()), "set aside": int((~keep).sum()),
              "flooded set aside": int((~keep & (y == 1)).sum()), "dry set aside": int((~keep & (y == 0)).sum()),
              "kept only by this gate": int(only.sum()), "flooded among them": int((only & (y == 1)).sum()),
              "arms": rows,
              "accuracy on the roads only this gate keeps": {n: float((call0[n][only] == y[only]).mean())
                                                              for n in names_g}}
    if g == "a":
        own[g]["paired against production (798)"] = against_production(preds, sub, "(ii) production gate's 798")
    print(f"{GATE_NAME[g]}: kept {own[g]['kept']}, set aside {own[g]['set aside']} ({own[g]['flooded set aside']} "
          f"flooded); only this gate keeps {own[g]['kept only by this gate']} ({own[g]['flooded among them']} flooded)")

# --- (iii) cloud groups (production's definition), primary seed, tonight's bootstrap order ---------------------------
on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
GROUPS = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
          "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
          "control: assessable roads on the same tiles": (on_tiles & ka, "right"),
          "clear-sky benchmark: assessable flooded roads on the same tiles": (on_tiles & ka & (y == 1), "found")}
assert [int(m.sum()) for m, _ in GROUPS.values()] == [24, 69, 175, 95]


def measure_of(c, msk, measure):
    return (c[..., msk] == 1) if measure in ("found", "called flooded") else (c[..., msk] == y[msk])


tonight = json.load(open(HERE / "both_dehazers_numbers.json"))
ev = json.load(open(HERE / "everything_together_numbers.json"))["cloud groups (tonight's construction)"]
rng = np.random.default_rng(SEED)
cloud = {}
for gname, (msk, measure) in GROUPS.items():
    boot, n_tiles = boot_sets(msk, N_BOOT_GROUP, rng)
    res = {}
    for i, n in enumerate(NAMES):
        c = call0[n][msk]; ys = y[msk]
        v = measure_of(call0[n], msk, measure)
        dist = [v[b].mean() for b in boot]
        res[n] = {"share": float(v.mean()), "count": int(v.sum()), "lo": float(np.percentile(dist, 2.5)),
                  "hi": float(np.percentile(dist, 97.5)),
                  "seed mean share": float(measure_of(C[:, i], msk, measure).mean()),
                  "seed min share": float(measure_of(C[:, i], msk, measure).mean(axis=1).min()),
                  "seed max share": float(measure_of(C[:, i], msk, measure).mean(axis=1).max()),
                  "kept by its gate": int(GATES[n[0]][msk].sum()),
                  "TP": int(((c == 1) & (ys == 1)).sum()), "FN": int(((c == 0) & (ys == 1)).sum()),
                  "FP": int(((c == 1) & (ys == 0)).sum()), "TN": int(((c == 0) & (ys == 0)).sum())}
    t_ = tonight[gname]["arms"]["none"]
    assert (res[PROD]["count"], round(res[PROD]["lo"], 4), round(res[PROD]["hi"], 4)) == \
        (t_["count"], t_["lo"], t_["hi"]), f"STOP: {gname} production interval not reproduced"
    e_ = ev[gname]["arms"]["everything together"]
    assert res["a·both·vec"]["count"] == e_["count"], f"STOP: {gname} everything together not reproduced"
    sub = roads[msk].reset_index(drop=True)
    rep = paired_report({n: call0[n][msk] for n in NAMES}, PROD, sub)
    print(f"\n=== (iii) {gname}: {int(msk.sum())} roads on {n_tiles} tiles ({measure}); seed 662 and mean of "
          f"{len(SEEDS)} seeds")
    for n, r in res.items():
        print(f"  {n:12s} {r['count']:4d}  {100 * r['share']:5.1f}%  [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]  "
              f"seed mean {100 * r['seed mean share']:5.1f}% ({100 * r['seed min share']:.1f}-"
              f"{100 * r['seed max share']:.1f})  kept by its gate {r['kept by its gate']}")
    cloud[gname] = {"roads": int(msk.sum()), "tiles": n_tiles, "measure": measure, "arms": res,
                    "paired against production (right = call matches label)": [
                        {**r.to_dict(), "McNemar p (unrounded)": exact_p(r)} for _, r in rep.iterrows()]}
print("check passed: production's group intervals reproduce both_dehazers_numbers.json; everything together's counts "
      "reproduce everything_together_numbers.json", stamp(), flush=True)

# --- across seeds -----------------------------------------------------------------------------------------------------
correct = (C == y[None, None, :])                           # (seed, arm, road)
acc_shared = correct[:, :, shared].mean(axis=2)             # (seed, arm)
acc_own = np.stack([correct[:, i, GATES[n[0]]].mean(axis=1) for i, n in enumerate(NAMES)], axis=1)
seed_rows, rule_seeds = [], {n: 0 for n in NAMES[1:]}
for k, s in enumerate(SEEDS):
    preds = {n: C[k, i][shared] for i, n in enumerate(NAMES)}
    rep = paired_report(preds, PROD, shared_sub)
    for _, r in rep.iterrows():
        ok, _ = confirm(r)
        rule_seeds[r["features"]] += int(ok)
        i = NAMES.index(r["features"])
        seed_rows.append({"fold seed": s, "arm": r["features"], "shared accuracy": acc_shared[k, i],
                          "own kept accuracy": acc_own[k, i], "gain vs production (shared)": r[f"vs {PROD}"],
                          "95% CI": r["95% CI"], "fixed": r["roads fixed"], "broken": r["roads broken"],
                          "McNemar p": r["McNemar p"], "would pass": ok})
    seed_rows.append({"fold seed": s, "arm": PROD, "shared accuracy": acc_shared[k, 0], "own kept accuracy": acc_own[k, 0]})
    print(f"seed {s:3d} scored", stamp(), flush=True)
seeds_df = pd.DataFrame(seed_rows)
seeds_df.to_csv(OUT / "pipeline_factorial_seeds.csv", index=False)
summary = {}
for i, n in enumerate(NAMES):
    a, o = acc_shared[:, i], acc_own[:, i]
    d = a - acc_shared[:, 0]
    summary[n] = {"gate": GATE_NAME[n.split("·")[0]], "cues": CUE_NAME[n.split("·")[1]],
                  "features": FEAT_NAME[n.split("·")[2]], "tools": tools[n],
                  "shared accuracy, seed 662": float(a[P]), "shared accuracy mean": float(a.mean()),
                  "shared accuracy SD": float(a.std(ddof=1)), "shared accuracy min": float(a.min()),
                  "shared accuracy max": float(a.max()), "own kept accuracy, seed 662": float(o[P]),
                  "own kept accuracy mean": float(o.mean()), "own kept accuracy SD": float(o.std(ddof=1)),
                  "seeds above production": int((d > 1e-12).sum()), "seeds equal": int((np.abs(d) <= 1e-12).sum()),
                  "seeds below production": int((d < -1e-12).sum()), "mean gain vs production": float(d.mean()),
                  "rule passes (of 21 seeds, shared roads)": rule_seeds.get(n)}
print(f"\n=== shared-road accuracy across the {len(SEEDS)} fold seeds {SEEDS}")
print(pd.DataFrame(summary).T.drop(columns=["gate", "cues", "features"]).infer_objects().to_string(
    float_format=lambda v: f"{v:.4f}"), flush=True)


# --- main effects and interactions (linear contrasts over the 16 cells) -----------------------------------------------
def w_of(terms):
    """Weights over the arms from {(g, c, f): weight}."""
    w = np.zeros(len(NAMES))
    for (g, c, f), v in terms.items():
        w[NAMES.index(f"{g}·{c}·{f}")] += v
    return w


def avg(terms_list):
    out = {}
    for t in terms_list:
        for k, v in t.items():
            out[k] = out.get(k, 0) + v / len(terms_list)
    return out


G, CU, FE = list(GATES), list(CUES), list(FEATS)
CONTRASTS = {}
CONTRASTS["main: spotter gate (b - a)"] = avg([{("b", c, f): 1, ("a", c, f): -1} for c in CU for f in FE])
for k in ("td", "he", "both"):
    CONTRASTS[f"main: {CUE_NAME[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for g in G for f in FE])
CONTRASTS["main: DINOv2 vector (vec - prod)"] = avg([{(g, c, "vec"): 1, (g, c, "prod"): -1} for g in G for c in CU])
# conditional (simple) effects, easier to read than the interactions
for g in G:
    for k in ("td", "he", "both"):
        CONTRASTS[f"within gate {g}: {CUE_NAME[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for f in FE])
    CONTRASTS[f"within gate {g}: DINOv2 vector"] = avg([{(g, c, "vec"): 1, (g, c, "prod"): -1} for c in CU])
for c in CU:
    CONTRASTS[f"within cues {c}: spotter gate (b - a)"] = avg([{("b", c, f): 1, ("a", c, f): -1} for f in FE])
for f in FE:
    CONTRASTS[f"within features {f}: spotter gate (b - a)"] = avg([{("b", c, f): 1, ("a", c, f): -1} for c in CU])
for f in FE:
    for k in ("td", "he", "both"):
        CONTRASTS[f"within features {f}: {CUE_NAME[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for g in G])
for k in ("td", "he", "both"):
    CONTRASTS[f"interaction gate x {CUE_NAME[k]}"] = avg([{("b", k, f): 1, ("b", "raw", f): -1, ("a", k, f): -1,
                                                          ("a", "raw", f): 1} for f in FE])
CONTRASTS["interaction gate x vector"] = avg([{("b", c, "vec"): 1, ("b", c, "prod"): -1, ("a", c, "vec"): -1,
                                               ("a", c, "prod"): 1} for c in CU])
for k in ("td", "he", "both"):
    CONTRASTS[f"interaction {CUE_NAME[k]} x vector"] = avg([{(g, k, "vec"): 1, (g, "raw", "vec"): -1,
                                                           (g, k, "prod"): -1, (g, "raw", "prod"): 1} for g in G])
for k in ("td", "he", "both"):
    CONTRASTS[f"three-way gate x {CUE_NAME[k]} x vector"] = {
        ("b", k, "vec"): 1, ("b", "raw", "vec"): -1, ("b", k, "prod"): -1, ("b", "raw", "prod"): 1,
        ("a", k, "vec"): -1, ("a", "raw", "vec"): 1, ("a", k, "prod"): 1, ("a", "raw", "prod"): -1}
W = {k: w_of(v) for k, v in CONTRASTS.items()}


def contrast_ci(per_road, msk, w, n_boot=N_BOOT):
    """Tile-resampled 95% interval of the contrast w over arms, from per-road values (arm, road) on msk."""
    d = w @ per_road[:, msk]
    boot, _ = boot_sets(msk, n_boot)
    dist = [d[b].mean() for b in boot]
    return float(d.mean()), [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]


def contrast_table(value_seed_arm_road, msk, label):
    """value (seed, arm, road) -> each contrast at seed 662 with a tile interval, over the 21 seeds, and seed-averaged
    with a tile interval."""
    per_seed = value_seed_arm_road[:, :, msk].mean(axis=2)       # (seed, arm)
    seed_avg = value_seed_arm_road.mean(axis=0)                  # (arm, road)
    rows = {}
    for k, w in W.items():
        v = per_seed @ w
        p0, ci0 = contrast_ci(value_seed_arm_road[P].astype(float), msk, w)
        m, ci = contrast_ci(seed_avg, msk, w)
        rows[k] = {"seed 662": p0, "seed 662 95% CI": ci0, "seed mean": float(v.mean()), "seed SD": float(v.std(ddof=1)),
                   "seed min": float(v.min()), "seed max": float(v.max()), "seeds > 0": int((v > 1e-12).sum()),
                   "seeds < 0": int((v < -1e-12).sum()), "seed-averaged 95% CI": ci,
                   "matters (seed-averaged CI excludes 0)": bool(ci[0] > 0 or ci[1] < 0)}
        assert abs(m - v.mean()) < 1e-9
    print(f"\n=== contrasts, {label} (points)")
    show = pd.DataFrame(rows).T
    print(pd.DataFrame({"seed 662": 100 * show["seed 662"].astype(float),
                        "662 CI": [f"{100 * a:+.1f},{100 * b:+.1f}" for a, b in show["seed 662 95% CI"]],
                        "mean": 100 * show["seed mean"].astype(float), "SD": 100 * show["seed SD"].astype(float),
                        "min": 100 * show["seed min"].astype(float), "max": 100 * show["seed max"].astype(float),
                        ">0": show["seeds > 0"], "<0": show["seeds < 0"],
                        "seed-avg CI": [f"{100 * a:+.2f},{100 * b:+.2f}" for a, b in show["seed-averaged 95% CI"]],
                        "matters": show["matters (seed-averaged CI excludes 0)"]}).to_string(
        float_format=lambda v: f"{v:+.2f}"), flush=True)
    return rows


effects = {"shared roads (accuracy)": contrast_table(correct.astype(float), shared, "shared roads, accuracy")}
for gname, (msk, measure) in GROUPS.items():
    v = (C == 1) if measure in ("found", "called flooded") else correct
    effects[f"{gname} ({measure})"] = contrast_table(v.astype(float), msk, f"{gname} ({measure})")

# --- the optimal combo (preregistered rule) ---------------------------------------------------------------------------
mean_acc = acc_shared.mean(axis=0)
top = NAMES[int(np.argmax(mean_acc))]
seed_avg_correct = correct.mean(axis=0).astype(float)
vs_top = {}
for i, n in enumerate(NAMES):
    if n == top:
        continue
    w = np.zeros(len(NAMES)); w[NAMES.index(top)] = 1; w[i] = -1
    d, ci = contrast_ci(seed_avg_correct, shared, w)
    vs_top[n] = {"tools": tools[n], "mean accuracy": float(mean_acc[i]), "top minus arm": d, "95% CI": ci,
                 "interval includes 0": bool(ci[0] <= 0 <= ci[1]), "simpler than top": tools[n] < tools[top]}
ties = [n for n, r in vs_top.items() if r["simpler than top"] and r["interval includes 0"]]
pool = [top] + ties
chosen = sorted(pool, key=lambda n: (tools[n], -mean_acc[NAMES.index(n)]))[0]
print(f"\n=== choice: top arm by mean shared accuracy {top} ({100 * mean_acc[NAMES.index(top)]:.2f}%, {tools[top]} tools);"
      f" simpler ties {ties}; chosen {chosen}")
print(pd.DataFrame(vs_top).T.to_string(), flush=True)
choice = {"top arm": top, "top mean accuracy": float(mean_acc[NAMES.index(top)]), "ties (simpler, CI includes 0)": ties,
          "chosen": chosen, "chosen mean accuracy": float(mean_acc[NAMES.index(chosen)]),
          "chosen tools": tools[chosen], "every arm against the top arm (seed-averaged, tiles resampled)": vs_top,
          "chosen against production, seed 662 (promotion rule)":
              next((r for r in shared_paired if r["features"] == chosen), "chosen is production")}

# --- save -------------------------------------------------------------------------------------------------------------
assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == registry_hash, "production.json changed during the run"
table = pd.DataFrame({"tile_id": roads.tile_id, "road_id": roads.road_id, "split": roads.split, "flooded": y,
                      "kept by production gate (a)": ka, "kept by spotter gate (b)": kb, "shared": shared,
                      "hazy (production road rule)": hazy, "dark-rise share": roads.cloud_dark_rise_road,
                      "spotter share": roads.spot_road})
for i, n in enumerate(NAMES):
    table[f"call seed 662 · {n}"] = C[P, i]
for i, n in enumerate(NAMES):
    table[f"flooded-call share over 21 seeds · {n}"] = C[:, i].mean(axis=0).round(4)
table.to_csv(OUT / "pipeline_factorial_calls.csv", index=False)
rule = {n: {"shared, seed 662": next(r for r in shared_paired if r["features"] == n)["rule"],
            "would pass (shared, seed 662)": next(r for r in shared_paired if r["features"] == n)["would pass"],
            "seeds it would pass (of 21, shared)": rule_seeds[n]} for n in NAMES[1:]}
for r in own["a"]["paired against production (798)"]:
    rule[r["features"]].update({"798, seed 662": r["rule"], "would pass (798, seed 662)": r["would pass"]})
out = {"code": "GeoAI-Roads 55c8fc2 (clean tree)", "test plan": "outputs/preregistration_pipeline_factorial.md",
       "production model": production_model(), "cloud rule": production_cloud_rule(), "fold seeds": SEEDS,
       "arms": {n: {"gate": GATE_NAME[n.split('·')[0]], "cues": CUE_NAME[n.split('·')[1]],
                    "features": FEAT_NAME[n.split('·')[2]], "tools": tools[n],
                    "columns before the PCA": len(ARMS[n][1]),
                    "model columns": len(ARMS[n][1]) - (len(DINO_VECTOR) - D.VECTOR_PCS if n.endswith("vec") else 0)}
                for n in NAMES},
       "folds": "StratifiedGroupKFold(5, shuffle=True) by tile over all 1,037 development roads; each fold fitted on "
                "the training-fold roads its gate keeps; every held-out road called",
       "roads": {"development": len(roads), "kept a": int(ka.sum()), "kept b": int(kb.sum()), "shared": int(shared.sum()),
                 "flooded shared": int(y[shared].sum())},
       "tile-rule tiles": len(all_tiles), "tiles with a cloud gate": len(gate_tiles), "thin-cloud tiles": len(haze_tiles),
       "checks": CHECKS + ["accuracy intervals match sn8_heldout.held_out_report",
                           "production's cloud-group intervals reproduce both_dehazers_numbers.json",
                           "production.json unchanged (sha256)"],
       "(i) shared roads, seed 662": {"arms": shared_rows, "paired against production": shared_paired},
       "(ii) own kept roads, seed 662": own, "(iii) cloud groups": cloud,
       "across seeds (shared roads)": summary, "contrasts": effects, "choice": choice,
       "promotion rule (not applied to production.json)": rule, "run time s": round(time.time() - t0)}
json.dump(plain(out), open(OUT / "pipeline_factorial_numbers.json", "w"), indent=1)
print(f"\nCHOSEN: {chosen}; promotion rule on the shared roads at seed 662: "
      f"{rule[chosen]['shared, seed 662'] if chosen != PROD else 'production itself'}")
print("saved", stamp())
