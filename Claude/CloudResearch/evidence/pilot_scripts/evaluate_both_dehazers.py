"""Test plan: outputs/preregistration_both_dehazers.md (Justin 2026-10-25: "cant we use both He and two date?").
Primary arm "both cues": the production flood model trained and called on the two-date cues (no corner edit, prefix
td_) and the He 2011 cues (prefix he_) of every road, side by side. Post hoc (chosen after seeing the calls): AND / OR
of the existing two-date and He calls. Development data only. Writes both_dehazers_numbers.json and
both_dehazers_calls.csv."""
import sys, time, json, hashlib, inspect
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
import sn8_refhaze as R
from sn8_clouds import ROAD_CLOUD_CUT, assessable, _tile
from sn8_heldout import touched_roads, paired_report
from sn8_lines import road_band
from sn8_models import FLOOD_MODELS
from sn8_refhaze import cloud_gate, corrected_table
from sn8_stages import production_cloud_rule, production_features, production_model
HERE = Path(__file__).resolve().parent
t0 = time.time()


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
    """roads with cols replaced by the corrected table c on the given tiles (as the earlier scripts do)."""
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


roads = touched_roads(include_cloudy=True)
assert set(roads.split) <= {"train", "val"}, "development roads only"
keep = assessable(roads, production_cloud_rule())
tile_rule = ~roads.cloudy.to_numpy()
hazy = tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
haze_tiles = sorted(roads.tile_id[hazy].unique()); all_tiles = sorted(roads.tile_id[tile_rule].unique())
cols = production_features()
print(f"production model: {production_model()}; {len(cols)} production features; {len(roads)} roads", flush=True)
gated = {}
for t in all_tiles:
    p, b, a, valid = _tile(t)
    gated[t] = bool(cloud_gate(b, a, valid)[0].any())
gate_tiles = [t for t in all_tiles if gated[t]]
print(f"tile-rule tiles {len(all_tiles)}: {len(gate_tiles)} with a cloud gate, {len(all_tiles) - len(gate_tiles)} empty",
      round(time.time() - t0), "s", flush=True)
assert (len(all_tiles), len(gate_tiles)) == (200, 99), "tile counts differ from the earlier arms"
roads["_n"] = roads.groupby(["tile_id", "road_id"]).cumcount()
td = merged(roads, gate_tiles, cached_table(gate_tiles, "darkref"), cols, "two-date (no corner edit)")
he = merged(roads, all_tiles, cached_table(all_tiles, "dehaze"), cols, "He 2011")
both = pd.concat([td[cols].add_prefix("td_"), he[cols].add_prefix("he_")], axis=1)
bcols = list(both.columns)
assert len(bcols) == 2 * len(cols) and both.index.equals(roads.index)
print(f"both cues: {len(bcols)} columns", round(time.time() - t0), "s", flush=True)

y = roads.flooded.astype(int).to_numpy()
folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662).split(roads, y, groups=roads.tile_id))
make = FLOOD_MODELS[production_model()]


def cv_calls(X, c):
    call = np.full(len(roads), -1)
    for tr, te in folds:
        t_ = tr[keep[tr]]
        call[te] = make().fit(X.iloc[t_][c], y[t_]).predict(X.iloc[te][c])
    return call


cv = pd.read_csv(HERE / "cloudvars_calls.csv"); hc = pd.read_csv(HERE / "he_dehazed_calls.csv")
fx = pd.read_csv(HERE / "twodate_cornerfix_calls.csv")
for f in (cv, hc, fx):
    assert f.tile_id.equals(roads.tile_id) and f.road_id.equals(roads.road_id), "calls CSV row order differs"
he_call = hc["call: He 2011 · trained de-hazed"].to_numpy()
td_call = fx["call: two-date · trained de-hazed (no corner edit)"].to_numpy()
# check: the same features and folds reproduce the two single-dehazer arms exactly
assert (cv_calls(td, cols) == td_call).all(), "two-date arm not reproduced"
assert (cv_calls(he, cols) == he_call).all(), "He arm not reproduced"
print("check passed: two-date and He arms reproduced call for call", round(time.time() - t0), "s", flush=True)
call = cv_calls(both, bcols)
print("both cues trained and called", round(time.time() - t0), "s", flush=True)

AND, OR = "AND of two-date and He (post hoc)", "OR of two-date and He (post hoc)"
calls = {"none": cv["call: 1 as it is · production"].to_numpy(),
         "two-date · trained de-hazed": td_call,
         "He 2011 · trained de-hazed": he_call,
         "both cues": call,
         AND: ((td_call == 1) & (he_call == 1)).astype(int),
         OR: ((td_call == 1) | (he_call == 1)).astype(int)}
pd.DataFrame({"tile_id": roads.tile_id, "road_id": roads.road_id, "call: both cues (td_ + he_)": call,
              "call: " + AND: calls[AND], "call: " + OR: calls[OR]}).to_csv(HERE / "both_dehazers_calls.csv", index=False)

on_tiles = roads.tile_id.isin(haze_tiles).to_numpy()
groups = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
          "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
          "control: assessable roads on the same tiles": (on_tiles & keep, "right"),
          "clear-sky benchmark: assessable flooded roads on the same tiles": (on_tiles & keep & (y == 1), "found")}
assert not (groups["clear-sky benchmark: assessable flooded roads on the same tiles"][0] & hazy).any()


def plain(records):
    return [{k: (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v)
             for k, v in r.items()} for r in records]


rng = np.random.default_rng(662)   # drawn in the same group order as before, so the earlier arms keep their intervals
out = {"code": "GeoAI-Roads 1532e9a (modules used unchanged since 5d325d9)", "test plan": "outputs/preregistration_both_dehazers.md",
       "production model": production_model(), "features per de-hazer": len(cols), "both-cues columns": len(bcols),
       "tile-rule tiles": len(all_tiles), "tiles with a cloud gate": len(gate_tiles), "thin-cloud tiles": len(haze_tiles),
       "post hoc": [AND, OR]}
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
    pre = {}
    for base in ("none", "He 2011 · trained de-hazed", "two-date · trained de-hazed"):
        pre[base] = paired_report({"both cues": calls["both cues"][msk], base: calls[base][msk]}, base, sub)
    post = paired_report({k: calls[k][msk] for k in ("none", AND, OR)}, "none", sub)
    print(f"\n{name}: {int(msk.sum())} roads on {len(idx)} tiles ({measure})")
    for k, r in res.items():
        print(f"  {k:36s} {r['count']:4d}  {100 * r['share']:.1f}%  [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]")
    for base, rep in pre.items():
        print(rep.to_string())
    print("post hoc:"); print(post.to_string())
    out[name] = {"roads": int(msk.sum()), "tiles": len(idx), "measure": measure, "arms": res,
                 "both cues vs": {b: plain(r.to_dict("records"))[0] for b, r in pre.items()},
                 "post hoc vs none": plain(post.to_dict("records"))}
json.dump(out, open(HERE / "both_dehazers_numbers.json", "w"), indent=1)
print("saved", round(time.time() - t0), "s")
