"""Test plan: outputs/preregistration_everything_together.md (Justin 2026-10-26: "are you able to start testing with
everything all together"). Primary arm "everything together": the production flood model on the raw production cues
(93 classical + 3 DINOv2 change cues), the same cues from both de-hazers (td_ two-date without the corner edit, he_ He
2011, as in "both cues") and the DINOv2 change vector reduced to 16 PCs inside each fold (as Code/dino_test.ipynb),
with production's cloud gate. Comparators: production, production + DINOv2 vector (best so far), both cues. Ablations:
without de-hazing (= best so far), without the vector, without the raw classical cues, without any classical cue.
Three fold constructions, one per scoring set, each the one that set was scored with before (checked call for call or
count for count against the logged numbers). Development data only; cached feature tables only (a DINOv2 cache miss
stops the script: no GPU). Writes everything_together_numbers.json and everything_together_calls.csv."""
import sys, time, json, hashlib, inspect
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
import sn8_dino as D
import sn8_refhaze as R
from sn8_clouds import ROAD_CLOUD_CUT, assessable, _tile
from sn8_dino import DINO_CUES, DINO_VECTOR, ReduceColumns, with_dino
from sn8_heldout import held_out_report, paired_report, touched_roads
from sn8_lines import road_band
from sn8_models import FLOOD_MODELS
from sn8_refhaze import cloud_gate, corrected_table
from sn8_results import RESULTS_DIR
from sn8_stages import confirm, production_cloud_rule, production_features, production_model
HERE = Path(__file__).resolve().parent
SEED = 662
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
    """The file corrected_table(tiles, method) reads; same key as sn8_refhaze.corrected_table (read-only copy)."""
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
    """roads with cols replaced by the corrected table c on the given tiles (as evaluate_both_dehazers.py)."""
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


# --- roads and cues --------------------------------------------------------------------------------------------------
roads = with_dino(touched_roads(include_cloudy=True))
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
tile_rule = ~roads.cloudy.astype(bool).to_numpy()
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
assert (len(roads), int(keep.sum()), int(tile_rule.sum()), int(hazy.sum())) == (1037, 798, 891, 93)
haze_tiles = sorted(roads.tile_id[hazy].unique()); all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
classical = [c for c in cols if c not in DINO_CUES]
assert len(cols) == 96 and len(classical) == 93 and cols[-3:] == DINO_CUES
print(f"production model: {production_model()}; cloud rule: {production_cloud_rule()}; {len(cols)} production "
      f"features; {len(roads)} development roads", stamp(), flush=True)
gated = {}
for t in all_tiles:
    p, b, a, valid = _tile(t)
    gated[t] = bool(cloud_gate(b, a, valid)[0].any())
gate_tiles = [t for t in all_tiles if gated[t]]
print(f"tile-rule tiles {len(all_tiles)}: {len(gate_tiles)} with a cloud gate", stamp(), flush=True)
assert (len(all_tiles), len(gate_tiles), len(haze_tiles)) == (200, 99, 39), "tile counts differ from the earlier arms"
light = roads[["tile_id", "road_id"] + cols].copy(); light["_n"] = light.groupby(["tile_id", "road_id"]).cumcount()
td = merged(light, gate_tiles, cached_table(gate_tiles, "darkref"), cols, "two-date (no corner edit)")
he = merged(light, all_tiles, cached_table(all_tiles, "dehaze"), cols, "He 2011")
X = pd.concat([roads[cols + DINO_VECTOR], td[cols].add_prefix("td_"), he[cols].add_prefix("he_")], axis=1)
assert X.index.equals(roads.index) and X.shape[1] == 96 + 1024 + 192
TD, HE = ["td_" + c for c in cols], ["he_" + c for c in cols]
TD_DINO, HE_DINO = ["td_" + c for c in DINO_CUES], ["he_" + c for c in DINO_CUES]
y = roads.flooded.astype(int).to_numpy()
make = FLOOD_MODELS[production_model()]

PROD, BEST, BOTH, ALL = "production", "production + DINOv2 vector (best so far)", "both cues", "everything together"
NO_VEC, NO_CLS, NO_ANY = "without the DINOv2 vector", "without classical (raw)", "without any classical cue (secondary)"
CLS93 = "classical 93 (production before DINOv2; check only)"
ARMS = {PROD: cols, BEST: cols + DINO_VECTOR, BOTH: TD + HE, ALL: cols + TD + HE + DINO_VECTOR,
        NO_VEC: cols + TD + HE, NO_CLS: DINO_CUES + TD + HE + DINO_VECTOR,
        NO_ANY: DINO_CUES + TD_DINO + HE_DINO + DINO_VECTOR}
ABLATIONS = [NO_VEC, NO_CLS, NO_ANY]
model_columns = {k: len(v) - (len(DINO_VECTOR) - D.VECTOR_PCS if DINO_VECTOR[0] in v else 0) for k, v in ARMS.items()}
print("model columns per arm:", model_columns, flush=True)


def factory(columns):
    return (lambda: make_pipeline(ReduceColumns(DINO_VECTOR), make())) if DINO_VECTOR[0] in columns else make


def held_out_calls(sub, train, columns):
    """Folds split over the `sub` roads (5 by tile, seed 662); each fold's model is fitted on the training-fold roads
    with `train` True and calls every held-out road of `sub`. -1 marks roads outside `sub`."""
    idx = np.flatnonzero(sub)
    Xs, ys, tiles, tr_ok = X.iloc[idx].reset_index(drop=True), y[idx], roads.tile_id.to_numpy()[idx], train[idx]
    call = np.full(len(roads), -1)
    for tr, te in StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED).split(Xs, ys, groups=tiles):
        tr = tr[tr_ok[tr]]
        call[idx[te]] = factory(columns)().fit(Xs.iloc[tr][columns], ys[tr]).predict(Xs.iloc[te][columns])
    return call


everyone = np.ones(len(roads), bool)
SCHEMES = {"A798": ("folds over the 798 assessable roads, fitted on them (production now)", keep, everyone),
           "B891": ("folds over the 891 tile-rule roads, fitted on all of them (the logged runs)", tile_rule, everyone),
           "C1037": ("folds over all 1,037 development roads, fitted on the assessable ones (tonight's cloud tests)",
                     everyone, keep)}
calls = {}
for s, (what, sub, train) in SCHEMES.items():
    arms = {**ARMS, CLS93: classical} if s == "B891" else ARMS
    calls[s] = {}
    for name, columns in arms.items():
        calls[s][name] = held_out_calls(sub, train, columns)
        print(f"{s} {name}: called", stamp(), flush=True)


# --- reproduction checks (stop if any fails) -------------------------------------------------------------------------
def counts(c, msk):
    p, t = c[msk], y[msk]
    assert (p >= 0).all()
    return int(((p == 1) & (t == 1)).sum()), int(((p == 0) & (t == 1)).sum()), int(((p == 1) & (t == 0)).sum()), \
        int(((p == 0) & (t == 0)).sum())


checks = [("A798", PROD, keep, (394, 47, 89, 268)), ("B891", CLS93, tile_rule, (401, 64, 87, 339)),
          ("B891", PROD, tile_rule, (408, 57, 83, 343)), ("B891", BEST, tile_rule, (409, 56, 80, 346))]
for s, name, msk, want in checks:
    got = counts(calls[s][name], msk)
    assert got == want, f"STOP: {s} {name} gives {got}, logged {want}"
cv = pd.read_csv(HERE / "cloudvars_calls.csv"); bd = pd.read_csv(HERE / "both_dehazers_calls.csv")
for f in (cv, bd):
    assert f.tile_id.equals(roads.tile_id) and f.road_id.equals(roads.road_id), "calls CSV row order differs"
assert (calls["C1037"][PROD] == cv["call: 1 as it is · production"].to_numpy()).all(), "STOP: production not reproduced"
assert (calls["C1037"][BOTH] == bd["call: both cues (td_ + he_)"].to_numpy()).all(), "STOP: both cues not reproduced"
print("checks passed: A798 production 394/47/89/268; B891 classical 401/64/87/339, production 408/57/83/343, "
      "best so far 409/56/80/346 (logged); C1037 production and both cues call for call", stamp(), flush=True)


# --- scoring ---------------------------------------------------------------------------------------------------------
def plain(v):
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else float(f"{float(v):.6g}")
    return v


def exact_p(row):
    """McNemar's exact p from a paired_report row, unrounded (paired_report rounds to 4 decimals)."""
    from scipy.stats import binomtest
    f, b = int(row["roads fixed"]), int(row["roads broken"])
    return binomtest(f, f + b, 0.5).pvalue if f + b else 1.0


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


def score_set(msk, arm_calls, label, n_boot=2000):
    """Confusion matrix and metrics per arm on the roads in msk, with tile-resampled 95% intervals for every metric
    (2,000 resamples, seed 662, drawn as sn8_heldout.held_out_report draws them)."""
    sub = roads[msk].reset_index(drop=True); t = y[msk]; tiles = sub.tile_id.to_numpy()
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(tiles == g) for g in np.unique(tiles)]
    boot = [np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))]) for _ in range(n_boot)]
    rows, preds = {}, {}
    for name, c in arm_calls.items():
        p = c[msk]; preds[name] = p
        m = metrics(t, p)
        dist = pd.DataFrame([metrics(t[b], p[b]) for b in boot])
        for k in ("accuracy", "precision", "recall", "specificity", "F1", "MCC"):
            m[f"{k} 95% CI"] = [float(np.nanpercentile(dist[k], 2.5)), float(np.nanpercentile(dist[k], 97.5))]
        rows[name] = m
    logged = held_out_report(preds, sub)          # the logged format, as a check on the accuracy intervals
    for name in arm_calls:
        lo, hi = rows[name]["accuracy 95% CI"]
        assert logged.loc[logged.features == name, "accuracy 95% CI"].iloc[0] == f"{lo:.2f}-{hi:.2f}", name
    print(f"\n=== {label}: {int(msk.sum())} roads on {len(groups)} tiles ({int(t.sum())} flooded)")
    show = pd.DataFrame(rows).T[["TP", "FN", "FP", "TN", "accuracy", "precision", "recall", "specificity", "F1", "MCC"]]
    show["acc 95% CI"] = [f"{100 * r['accuracy 95% CI'][0]:.1f}-{100 * r['accuracy 95% CI'][1]:.1f}" for r in rows.values()]
    show["MCC 95% CI"] = [f"{r['MCC 95% CI'][0]:.3f}-{r['MCC 95% CI'][1]:.3f}" for r in rows.values()]
    print(show.to_string(float_format=lambda v: f"{v:.3f}"), flush=True)
    return rows, preds, sub


def paired(preds, sub, label, arms_in):
    """Every arm against production (with the promotion rule applied, read-only), everything together against the
    best so far and against both cues, and each ablation against everything together."""
    out = {}
    vs_prod = paired_report({k: preds[k] for k in arms_in}, PROD, sub)
    out["against production"] = []
    for _, r in vs_prod.iterrows():
        ok, why = confirm(r)
        out["against production"].append({**r.to_dict(), "McNemar p (unrounded)": exact_p(r), "rule": why,
                                          "would pass": ok})
    for base in (BEST, BOTH):
        r = paired_report({ALL: preds[ALL], base: preds[base]}, base, sub).iloc[0]
        out[f"everything together against {base}"] = {**r.to_dict(), "McNemar p (unrounded)": exact_p(r),
                                                      "rule": confirm(r)[1], "would pass": confirm(r)[0]}
    abl = paired_report({ALL: preds[ALL], **{k: preds[k] for k in ABLATIONS}}, ALL, sub)
    out["ablations against everything together"] = [{**r.to_dict(), "McNemar p (unrounded)": exact_p(r)}
                                                    for _, r in abl.iterrows()]
    print(f"--- paired, {label}")
    print(pd.DataFrame(out["against production"]).drop(columns=["rule"]).to_string())
    print(pd.DataFrame([out[f"everything together against {b}"] for b in (BEST, BOTH)]).drop(columns=["rule"]).to_string())
    print(abl.to_string(), flush=True)
    return out


main_arms = list(ARMS)
results = {}
for label, s, msk in (("(i) 798 assessable roads (primary)", "A798", keep),
                      ("(ii) 891 tile-rule roads (logged construction)", "B891", tile_rule),
                      ("sensitivity: tonight's folds, 798 assessable", "C1037", keep),
                      ("sensitivity: tonight's folds, 891 tile-rule", "C1037", tile_rule)):
    arm_calls = {k: calls[s][k] for k in (main_arms + [CLS93] if s == "B891" else main_arms)}
    rows, preds, sub = score_set(msk, arm_calls, label)
    results[label] = {"scheme": SCHEMES[s][0], "roads": int(msk.sum()), "tiles": int(sub.tile_id.nunique()),
                      "flooded": int(y[msk].sum()), "arms": rows, "paired": paired(preds, sub, label, main_arms)}

# --- (iii) cloud groups, tonight's construction and bootstrap order --------------------------------------------------
on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
GROUPS = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
          "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
          "control: assessable roads on the same tiles": (on_tiles & keep, "right"),
          "clear-sky benchmark: assessable flooded roads on the same tiles": (on_tiles & keep & (y == 1), "found")}
assert [int(m.sum()) for m, _ in GROUPS.values()] == [24, 69, 175, 95]
tonight = json.load(open(HERE / "both_dehazers_numbers.json"))
rng = np.random.default_rng(SEED)   # drawn in the same group order as tonight, so tonight's arms keep their intervals
cloud = {}
for gname, (msk, measure) in GROUPS.items():
    sub = roads[msk].reset_index(drop=True); tiles = sub.tile_id.to_numpy(); ys = y[msk]
    idx = [np.flatnonzero(tiles == t) for t in np.unique(tiles)]
    boot = [np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))]) for _ in range(5000)]
    res = {}
    for k in main_arms:
        c = calls["C1037"][k][msk]
        v = (c == 1) if measure in ("found", "called flooded") else (c == ys)
        dist = [v[b].mean() for b in boot]
        res[k] = {"share": float(v.mean()), "count": int(v.sum()), "lo": float(np.percentile(dist, 2.5)),
                  "hi": float(np.percentile(dist, 97.5)),
                  "TP": int(((c == 1) & (ys == 1)).sum()), "FN": int(((c == 0) & (ys == 1)).sum()),
                  "FP": int(((c == 1) & (ys == 0)).sum()), "TN": int(((c == 0) & (ys == 0)).sum())}
    for mine, theirs in ((PROD, "none"), (BOTH, "both cues")):
        t_ = tonight[gname]["arms"][theirs]
        assert (res[mine]["count"], round(res[mine]["lo"], 4), round(res[mine]["hi"], 4)) == \
            (t_["count"], t_["lo"], t_["hi"]), f"STOP: {gname} {mine} interval not reproduced"
    preds = {k: calls["C1037"][k][msk] for k in main_arms}
    print(f"\n=== (iii) {gname}: {int(msk.sum())} roads on {len(idx)} tiles ({measure})")
    for k, r in res.items():
        print(f"  {k:42s} {r['count']:4d}  {100 * r['share']:5.1f}%  [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]  "
              f"TP {r['TP']} FN {r['FN']} FP {r['FP']} TN {r['TN']}")
    cloud[gname] = {"roads": int(msk.sum()), "tiles": len(idx), "measure": measure, "arms": res,
                    "paired": paired(preds, sub, gname, main_arms)}
print("check passed: tonight's production and both-cues group intervals reproduced", stamp(), flush=True)

# --- save --------------------------------------------------------------------------------------------------------------
assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == registry_hash, "production.json changed during the run"
primary = next(r for r in results["(i) 798 assessable roads (primary)"]["paired"]["against production"]
               if r["features"] == ALL)
secondary = next(r for r in results["(ii) 891 tile-rule roads (logged construction)"]["paired"]["against production"]
                 if r["features"] == ALL)
table = pd.DataFrame({"tile_id": roads.tile_id, "road_id": roads.road_id, "split": roads.split, "flooded": y,
                      "assessable": keep, "tile_rule": tile_rule, "hazy": hazy})
for s, arm_calls in calls.items():
    for k, c in arm_calls.items():
        table[f"{s} · {k}"] = c
table.to_csv(HERE / "everything_together_calls.csv", index=False)
out = {"code": "GeoAI-Roads 1532e9a (clean tree)", "test plan": "outputs/preregistration_everything_together.md",
       "production model": production_model(), "cloud rule": production_cloud_rule(),
       "arms (columns before the PCA)": {k: len(v) for k, v in ARMS.items()}, "model columns per arm": model_columns,
       "schemes": {s: v[0] for s, v in SCHEMES.items()}, "tile-rule tiles": len(all_tiles),
       "tiles with a cloud gate": len(gate_tiles), "thin-cloud tiles": len(haze_tiles),
       "checks": ["A798 production 394/47/89/268 (logged 83.0%)", "B891 classical 93 401/64/87/339 (logged)",
                  "B891 production 408/57/83/343 (logged production + DINOv2 change cues)",
                  "B891 best so far 409/56/80/346 (logged dino_test)",
                  "C1037 production and both cues reproduce cloudvars_calls.csv / both_dehazers_calls.csv call for call",
                  "C1037 group intervals of production and both cues reproduce both_dehazers_numbers.json",
                  "accuracy intervals match sn8_heldout.held_out_report", "production.json unchanged (sha256)"],
       "promotion rule (not applied to production.json)": {"primary, 798": primary, "secondary, 891": secondary},
       "scoring sets": results, "cloud groups (tonight's construction)": cloud, "run time s": round(time.time() - t0)}
json.dump(plain(out), open(HERE / "everything_together_numbers.json", "w"), indent=1)
print(f"\nPRIMARY (798): everything together vs production: {primary['rule']}")
print(f"secondary (891): {secondary['rule']}")
print("saved", stamp())
