"""Shared setup for Agent B's spatially blocked cross-validation (flood per road, SpaceNet 8 Louisiana-East).

Test plan: outputs/preregistration_spatial_cv.md ("Agent B" and "Decision rules"), written before any model was
scored on the new folds. The road table, gates, cue tables and the 16 factorial arms are built exactly as
evaluate_pipeline_factorial.py builds them (that code is copied here, not changed), so only the folds change.

Development data only: the 226 train + val tiles of Louisiana-East and their 1,037 touched roads. Cached tables only
(a DINOv2 or corrected_table cache miss stops the script; no GPU). production.json is read-only (sha256 checked by
each script before and after).

Fitting runs in a pool of CPU processes (spawn), each forest with n_jobs=1 so that the pool uses N_WORKERS cores and
leaves the rest for Agent C. n_jobs does not change a random forest's trees (the tree seeds are drawn before the
parallel fit); the reproduction checks confirm the calls are the logged ones, call for call.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("MPLBACKEND", "Agg")
import hashlib
import inspect
import json
import multiprocessing
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
HERE = Path(__file__).resolve().parent
PILOT = HERE.parent
for _p in (LIB, str(HERE)):
    if _p not in sys.path:
        sys.path.append(_p)

import numpy as np
import pandas as pd

SEED = 662
SEEDS = [662] + list(range(1, 21))
N_WORKERS = 6                         # 8 cores: 6 for these fits, 2 left for Agent C
FLOOD_CALLS = HERE / "spatial_cv_flood_calls.npz"
NESTED_CALLS = HERE / "spatial_cv_nested.npz"
FACTORIAL_NPZ = PILOT / "pipeline_factorial_seed_calls.npz"
SPOT_CSV = PILOT / "cloud_spotting" / "gate_roads.csv"


def stamp(t0):
    return f"{round(time.time() - t0)} s"


def registry_path():
    from sn8_results import RESULTS_DIR
    return RESULTS_DIR / "production.json"


def registry_hash():
    return hashlib.sha256(registry_path().read_bytes()).hexdigest()


def dino_cache_guard():
    import sn8_dino as D
    for split in ("train", "val"):
        _, csv, npz = D._paths(split)
        if not (csv.exists() and npz.exists()):
            sys.exit(f"STOP: DINOv2 cache miss for {split} ({csv.name}); not recomputing (the GPU is in use elsewhere)")


# --- copied from evaluate_pipeline_factorial.py (read-only cache lookups) --------------------------------------------
def cache_path(tiles, method):
    """The file corrected_table(tiles, method) reads; same key as sn8_refhaze.corrected_table."""
    import sn8_refhaze as R
    from sn8_lines import road_band
    code = [hashlib.sha256(inspect.getsource(f).encode()).hexdigest() for f in (
        R._robust_global, R._local_fit, R.reference_dehaze, R.cloud_gate, R.tone_curve, R.dark_reference_dehaze,
        R._corrected_pair, R.corrected_rows)]
    key = hashlib.sha256(json.dumps([R.SPLIT_FINGERPRINT, sorted(tiles), method, road_band(), R.REF_WIN, R.REF_PASSES,
                                     R.REF_K, R.T_MIN, R.DARKREF_MIN_CLOUD_M2, R.DARKREF_CLEAR_MARGIN_PX,
                                     R.DARKREF_GATE_MARGIN_PX, R.DARKREF_GUIDED, R.TONE_QUANTILES, *code]).encode()
                         ).hexdigest()[:16]
    return R.CACHE_DIR / f"road_corrected_{method}_{key}.csv"


def cached_table(tiles, method):
    from sn8_refhaze import corrected_table
    p = cache_path(tiles, method)
    if not p.exists():
        sys.exit(f"STOP: cache miss for {method} on {len(tiles)} tiles ({p.name}); not recomputing")
    print(f"cache hit: {p.name}", flush=True)
    return corrected_table(tiles, method)


def merged(roads, tiles, c, cols, what):
    """roads with cols replaced by the corrected table c on the given tiles (as evaluate_pipeline_factorial.py)."""
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


class Setup:
    """The factorial's roads, gates, cue columns and arms (and X, the 1,312 feature columns, if build_x)."""

    def __init__(self, build_x=True):
        from sn8_clouds import ROAD_CLOUD_CUT, assessable, _tile
        from sn8_cloudspot import spot_gate
        from sn8_dino import DINO_CUES, DINO_VECTOR, with_dino
        from sn8_heldout import touched_roads
        from sn8_refhaze import cloud_gate
        from sn8_stages import production_cloud_rule, production_features, production_model
        from spatial_folds import dev_roads, fold_table
        t0 = time.time()
        roads = with_dino(touched_roads(include_cloudy=True))
        assert set(roads.split) <= {"train", "val"}, "development roads only"
        spot = pd.read_csv(SPOT_CSV)
        assert spot.tile_id.equals(roads.tile_id) and spot.road_id.equals(roads.road_id), "gate_roads.csv order differs"
        assert set(spot.split) <= {"train", "val"}
        assert (spot.cloudy.astype(bool).to_numpy() == roads.cloudy.astype(bool).to_numpy()).all()
        assert np.abs(spot.cloud_dark_rise_road.to_numpy() - roads.cloud_dark_rise_road.to_numpy()).max() < 1e-12
        assert (spot.flooded.astype(bool).to_numpy() == roads.flooded.astype(bool).to_numpy()).all()
        roads["spot_road"] = spot.spot_road.to_numpy()
        self.y = roads.flooded.astype(int).to_numpy()
        self.gates = {"a": assessable(roads, production_cloud_rule()), "b": spot_gate(roads)}
        self.gate_name = {"a": "production gate (dark-rise road rule)",
                          "b": "spotter gate (bright + texture + DINOv2 road rule)"}
        self.shared = self.gates["a"] & self.gates["b"]
        self.tile_rule = ~roads.cloudy.astype(bool).to_numpy()
        self.hazy = self.tile_rule & (roads.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
        assert (len(roads), int(self.gates["a"].sum()), int(self.gates["b"].sum()), int(self.shared.sum()),
                int(self.hazy.sum()), int(self.tile_rule.sum())) == (1037, 798, 790, 757, 93, 891), \
            "road counts differ from the factorial"
        self.haze_tiles = sorted(roads.tile_id[self.hazy].unique())
        self.all_tiles = sorted(roads.tile_id[self.tile_rule].unique())
        cols = production_features()
        assert len(cols) == 96 and cols[-3:] == DINO_CUES
        self.cols = cols
        self.model_name = production_model()
        self.cloud_rule = production_cloud_rule()
        # the fold module's road table must be this table, row for row
        d = dev_roads()
        assert d.tile_id.equals(roads.tile_id) and d.road_id.equals(roads.road_id)
        assert (d.flooded.to_numpy() == self.y.astype(bool)).all()
        assert (d.production_rule.to_numpy() == self.gates["a"]).all() and (d.tile_rule.to_numpy() == self.tile_rule).all()
        assert (d.thin_cloud.to_numpy() == self.hazy).all()
        self.R = pd.DataFrame({"tile_id": roads.tile_id.to_numpy(), "road_id": roads.road_id.to_numpy(),
                               "flooded": self.y.astype(bool)})
        self.split = roads.split.to_numpy()
        ft = fold_table(SEED)
        self.block_of_tile = dict(zip(ft.tile_id, ft.block))
        self.block = roads.tile_id.map(self.block_of_tile).to_numpy()
        ft7 = fold_table(SEED, block_tiles=7)
        self.block7 = roads.tile_id.map(dict(zip(ft7.tile_id, ft7.block))).to_numpy()
        self.tile = roads.tile_id.to_numpy()
        self.tile_xy = ft.set_index("tile_id")[["x_m", "y_m"]]
        TD, HE = ["td_" + c for c in cols], ["he_" + c for c in cols]
        self.cues = {"raw": cols, "td": TD, "he": HE, "both": cols + TD + HE}
        self.cue_name = {"raw": "none (raw)", "td": "two-date", "he": "He 2011", "both": "both cues + raw"}
        self.feats = {"prod": [], "vec": DINO_VECTOR}
        self.feat_name = {"prod": "production features", "vec": "+ DINOv2 change vector"}
        tool = {"a": 0, "b": 1, "raw": 0, "td": 1, "he": 1, "both": 2, "prod": 0, "vec": 1}
        cells = [(g, c, f) for g in self.gates for c in self.cues for f in self.feats]
        self.arms = {f"{g}·{c}·{f}": (g, self.cues[c] + self.feats[f]) for g, c, f in cells}
        self.names = list(self.arms)
        self.prod = "a·raw·prod"
        assert self.names[0] == self.prod and len(self.names) == 16
        self.tools = {n: sum(tool[p] for p in n.split("·")) for n in self.names}
        self.dino_vector = DINO_VECTOR
        self.best_cols = cols + DINO_VECTOR          # arm (b): production + DINOv2 cues + change vector
        self.roads = roads
        self.X = None
        if build_x:
            gate_tiles = [t for t in self.all_tiles if bool(cloud_gate(*_tile(t)[1:])[0].any())]
            assert (len(self.all_tiles), len(gate_tiles), len(self.haze_tiles)) == (200, 99, 39), \
                "tile counts differ from the earlier arms"
            print(f"tile-rule tiles {len(self.all_tiles)}: {len(gate_tiles)} with a cloud gate", stamp(t0), flush=True)
            light = roads[["tile_id", "road_id"] + cols].copy()
            light["_n"] = light.groupby(["tile_id", "road_id"]).cumcount()
            td = merged(light, gate_tiles, cached_table(gate_tiles, "darkref"), cols, "two-date (no corner edit)")
            he = merged(light, self.all_tiles, cached_table(self.all_tiles, "dehaze"), cols, "He 2011")
            X = pd.concat([roads[cols + DINO_VECTOR], td[cols].add_prefix("td_"), he[cols].add_prefix("he_")], axis=1)
            assert X.index.equals(roads.index) and X.shape[1] == 96 + 1024 + 192
            self.X = X
        print(f"setup: {len(roads)} dev roads; kept a {int(self.gates['a'].sum())}, b {int(self.gates['b'].sum())}, "
              f"shared {int(self.shared.sum())}; model {self.model_name}; cloud rule {self.cloud_rule}", stamp(t0),
              flush=True)

    def subset_folds(self, mask, build, seed):
        """Folds built on the subset table (rows where mask), returned as positions among the 1,037."""
        idx = np.flatnonzero(mask)
        sub = self.R.iloc[idx].reset_index(drop=True)
        return [(idx[tr], idx[te]) for tr, te, *_ in build(sub, seed)]


# --- fold builders (the fold module's functions; nothing is changed) -------------------------------------------------
def builders():
    from spatial_folds import size_matched_tile_folds, spatial_folds, tile_folds
    return {"T": lambda t, s: tile_folds(t, s), "Tdev": lambda t, s: tile_folds(t, s, over="dev"),
            "TM": lambda t, s: size_matched_tile_folds(t, s), "S": lambda t, s: spatial_folds(t, s),
            "SB": lambda t, s: spatial_folds(t, s, buffer=True), "L": lambda t, s: spatial_folds(t, s, block_tiles=7)}


# --- the process pool -------------------------------------------------------------------------------------------------
_W = {}


def _init(X, y, model_name):
    _W.update(X=X, y=y, model=model_name)


def _task(key, columns, folds):
    """Each fold's model (the arm's logged model) fitted on fit_rows, calling call_rows; -1 elsewhere."""
    from sklearn.pipeline import make_pipeline
    from sn8_dino import DINO_VECTOR, ReduceColumns
    from sn8_models import FLOOD_MODELS
    X, y, make = _W["X"], _W["y"], FLOOD_MODELS[_W["model"]]
    call = np.full(len(y), -1, np.int8)
    for fit_rows, call_rows in folds:
        model = make_pipeline(ReduceColumns(DINO_VECTOR), make()) if DINO_VECTOR[0] in columns else make()
        model.set_params(**{k: 1 for k in model.get_params(deep=True) if k.endswith("n_jobs")})
        call[call_rows] = model.fit(X.iloc[fit_rows][columns], y[fit_rows]).predict(X.iloc[call_rows][columns])
    return key, call


def run_pool(X, y, model_name, tasks, on_result, n_workers=N_WORKERS):
    """tasks: [(key, columns, [(fit_rows, call_rows), ...]), ...]; on_result(key, call) as each finishes."""
    if not tasks:
        return
    ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(n_workers, mp_context=ctx, initializer=_init, initargs=(X, y, model_name)) as ex:
        futs = [ex.submit(_task, *t) for t in tasks]
        for f in as_completed(futs):
            on_result(*f.result())


def save_npz(path, arrays, meta):
    tmp = path.with_name(path.stem + "_writing.npz")
    np.savez_compressed(tmp, meta=json.dumps(meta), **arrays)
    tmp.replace(path)


def load_npz(path):
    if not path.exists():
        return {}, None
    z = np.load(path, allow_pickle=False)
    return {k: z[k] for k in z.files if k != "meta"}, json.loads(str(z["meta"]))


def counts(call, y, msk):
    p, t = call[msk], y[msk]
    assert (p >= 0).all()
    return int(((p == 1) & (t == 1)).sum()), int(((p == 0) & (t == 1)).sum()), int(((p == 1) & (t == 0)).sum()), \
        int(((p == 0) & (t == 0)).sum())
