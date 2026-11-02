"""Spatial CV of the DINOv3 research benchmark (Agent C, CPU part): the random-forest arms on the seed-662 spatial folds.
Research only; DINOv3 never enters the library.

Stages (each writes its calls / probabilities to disk as it goes; a finished part is skipped on a rerun):
    B-frozen   Track B, phase 1's 13 arms on the 891 tile-rule roads and its 7 production-type arms on the 798 roads
               production's cloud rule assesses. First the reproduction check under the old tile folds (T): every arm
               must give phase 1's logged calls (phase1_calls_891.csv) call for call, production on the 798 must give
               394 / 47 / 89 / 268 and the best combo on the 891 409 / 56 / 80 / 346, or the script stops.
    B-trained  Track B, phase 2's arms with the fold-specific B-head / B-ft cues from spatialcv_gpu.py.
    A-rf       Track A, the cell random forests (production's detector) with frozen DINOv2 / DINOv3 cell features.

    OMP_NUM_THREADS=1 /opt/miniconda3/bin/python3 -I spatialcv_cpu.py B-frozen > spatialcv_cpu_B-frozen.log 2>&1

CPU only (the other agent keeps about 6 cores: forests run with n_jobs = SPATIALCV_NJOBS, default 2). Cached tables
only; the DINOv3 model is never loaded here.
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import spatialcv_common as C
import dinov3_bench as d3

import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline

from sn8_dino import DINO_CUES, DINO_VECTOR, ReduceColumns
from sn8_models import FLOOD_MODELS, classical_models
from sn8_stages import REGISTRY, production_cutoff, production_detector, production_features, production_model

NJOBS = int(os.environ.get("SPATIALCV_NJOBS", "2"))
STAGES = sys.argv[1:] or ["B-frozen"]
say = C.Log()
C.FOLD_DIR.mkdir(exist_ok=True)
PROD_SHA = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()


def tile_block():
    ft_, _, _ = C.tile_folds_662()
    return dict(zip(ft_.tile_id, ft_.block)), dict(zip(ft_.tile_id, ft_.fold.astype(int)))


BLOCK_OF, FOLD_OF = tile_block()


def cv_calls(factory, X, y, folds):
    """Held-out calls: each fold's model (a fresh factory()) is fit on its training rows and calls its test rows."""
    p = np.full(len(y), -1)
    for tr, te in folds:
        p[te] = factory().fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
    assert (p >= 0).all()
    return p


# ======================================================================================================================
# Track B
# ======================================================================================================================
make = FLOOD_MODELS[production_model()]
BASE = [c for c in production_features() if c not in DINO_CUES]
assert len(BASE) == 93 and all(c in production_features() for c in DINO_CUES)
V2 = lambda: ReduceColumns(DINO_VECTOR)                               # the library's, as in dino_test
V2p = lambda: d3.ReducePrefixed(DINO_VECTOR, prefix="dino2_pc")      # when both vectors go in (phase 1)
V3 = lambda: d3.ReducePrefixed(d3.DINO3_VECTOR, prefix="dino3_pc")
C3 = d3.DINO3_CUES
ARMS = {  # phase 1's arms, unchanged: name: (reducers, columns)
    "DINOv2 cues": ([], DINO_CUES),
    "DINOv2 cues + vector": ([V2], DINO_CUES + DINO_VECTOR),
    "base (production without DINO)": ([], BASE),
    "base + DINOv2 cues (production)": ([], BASE + DINO_CUES),
    "base + DINOv2 cues + vector": ([V2], BASE + DINO_CUES + DINO_VECTOR),
    "DINOv3 cues": ([], C3),
    "DINOv3 cues + vector": ([V3], C3 + d3.DINO3_VECTOR),
    "base + DINOv3 cues": ([], BASE + C3),
    "base + DINOv3 cues + vector": ([V3], BASE + C3 + d3.DINO3_VECTOR),
    "DINOv2 + DINOv3 cues": ([], DINO_CUES + C3),
    "DINOv2 + DINOv3 cues + vectors": ([V2p, V3], DINO_CUES + C3 + DINO_VECTOR + d3.DINO3_VECTOR),
    "base + DINOv2 + DINOv3 cues": ([], BASE + DINO_CUES + C3),
    "base + DINOv2 + DINOv3 cues + vectors": ([V2p, V3], BASE + DINO_CUES + C3 + DINO_VECTOR + d3.DINO3_VECTOR),
}
PRODUCTION_TYPE = [n for n in ARMS if n.startswith("base")]
PROD, BEST = "base + DINOv2 cues (production)", "base + DINOv2 cues + vector"
COUNTERPART = {"DINOv3 cues": "DINOv2 cues", "DINOv3 cues + vector": "DINOv2 cues + vector",
               "base + DINOv3 cues": PROD, "base + DINOv3 cues + vector": BEST,
               "DINOv2 + DINOv3 cues": "DINOv2 cues", "DINOv2 + DINOv3 cues + vectors": "DINOv2 cues + vector",
               "base + DINOv2 + DINOv3 cues": PROD, "base + DINOv2 + DINOv3 cues + vectors": BEST}
DINOV3_PARTNER = {"DINOv2 + DINOv3 cues": "DINOv3 cues", "DINOv2 + DINOv3 cues + vectors": "DINOv3 cues + vector",
                  "base + DINOv2 + DINOv3 cues": "base + DINOv3 cues",
                  "base + DINOv2 + DINOv3 cues + vectors": "base + DINOv3 cues + vector"}
PAIRS_B = ([(c, a) for c, a in COUNTERPART.items()]
           + [(c, PROD) for c in ARMS if "DINOv3" in c and COUNTERPART[c] != PROD]
           + [(c, a) for c, a in DINOV3_PARTNER.items()]
           + [(c, "base (production without DINO)") for c in PRODUCTION_TYPE if c != "base (production without DINO)"]
           + [(c, BEST) for c in ARMS if "DINOv3" in c and COUNTERPART[c] != BEST])


def factory(reducers):
    def f():
        est = make_pipeline(*[r() for r in reducers], make()) if reducers else make()
        return C.limit_jobs(est, NJOBS)
    return f


def frame(sub, y, calls):
    return pd.DataFrame({"tile_id": sub.tile_id, "road_id": sub.road_id, "block": sub.tile_id.map(BLOCK_OF),
                         "outer_fold": sub.tile_id.map(FOLD_OF) + 1, "flooded": y, **calls})


def stage_b_frozen():
    roads, rule, tile_rule = C.load_roads(gpu=False)
    sets = {"891": tile_rule, "798": rule}
    t0 = time.time()
    # reproduction under the old tile folds, split over each set itself (phase 1's construction)
    logged = pd.read_csv(HERE / "phase1_calls_891.csv")
    sub891, t891 = C.subset_folds(roads, tile_rule, "T")
    assert logged.tile_id.equals(sub891.tile_id) and logged.road_id.equals(sub891.road_id)
    y891 = sub891.flooded.astype(int).to_numpy()
    T = {"891": {}, "798": {}}
    for n, (red, cols) in ARMS.items():
        T["891"][n] = cv_calls(factory(red), sub891[cols], y891, t891)
        same = int((T["891"][n] == logged[n].to_numpy()).sum())
        say(f"T reproduction, 891, {n}: {same} of {len(y891)} calls equal phase 1's")
        assert same == len(y891), f"{n} does not reproduce phase 1 under tile folds"
    sub798, t798 = C.subset_folds(roads, rule, "T")
    y798 = sub798.flooded.astype(int).to_numpy()
    for n in PRODUCTION_TYPE:
        red, cols = ARMS[n]
        T["798"][n] = cv_calls(factory(red), sub798[cols], y798, t798)
    cm = lambda p, y: (int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum()),
                       int(((y == 0) & (p == 1)).sum()), int(((y == 0) & (p == 0)).sum()))
    assert cm(T["798"][PROD], y798) == (394, 47, 89, 268), cm(T["798"][PROD], y798)
    assert cm(T["891"][BEST], y891) == (409, 56, 80, 346), cm(T["891"][BEST], y891)
    say("reproduction passed: phase 1's 13 arms call for call on the 891; production 394/47/89/268 on the 798; "
        f"best combo 409/56/80/346 on the 891 ({time.time() - t0:.0f} s)")
    # spatial folds (S), seed 662
    S = {}
    for set_name, names in (("891", list(ARMS)), ("798", PRODUCTION_TYPE)):
        sub, folds = C.subset_folds(roads, sets[set_name], "S")
        y = sub.flooded.astype(int).to_numpy()
        S[set_name] = {}
        for n in names:
            t = time.time()
            red, cols = ARMS[n]
            S[set_name][n] = cv_calls(factory(red), sub[cols], y, folds)
            say(f"S, {set_name}, {n}: {time.time() - t:.1f} s")
        out = frame(sub, y, {**{f"S: {n}": S[set_name][n] for n in names}, **{f"T: {n}": T[set_name][n] for n in names}})
        out.to_csv(C.OUT / f"spatialcv_calls_B-frozen_{set_name}.csv", index=False)
    assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == PROD_SHA
    say(f"B-frozen done ({time.time() - t0:.0f} s); production.json unchanged")


H3 = [f"d3head_flood_{s}" for s in ("mean", "max", "share")]
T3 = [f"d3ft_flood_{s}" for s in ("mean", "max", "share")]
B_ARMS = {"base (production without DINO)": BASE, PROD: BASE + DINO_CUES, "base + DINOv3 cues (frozen)": BASE + C3,
          "base + DINOv2 cues + DINOv3 head cues": BASE + DINO_CUES + H3,
          "base + DINOv2 cues + DINOv3 fine-tuned cues": BASE + DINO_CUES + T3,
          "base + DINOv3 head cues": BASE + H3, "base + DINOv3 fine-tuned cues": BASE + T3,
          "DINOv2 cues": DINO_CUES, "DINOv3 cues (frozen)": C3, "DINOv3 head cues": H3, "DINOv3 fine-tuned cues": T3}


def stage_b_trained():
    """Phase 2's arms on the spatial folds. In outer fold k the trained cues are fold k's: cross-fitted on the
    outer-training roads (inner folds) and the mean of the 5 inner models on the held-out roads."""
    roads, rule, tile_rule = C.load_roads(gpu=False)
    have = {name: all((C.FOLD_DIR / f"{name}_outer{k}.npz").exists() for k in range(C.N_FOLDS))
            for name in ("B-head", "B-ft")}
    say(f"trained cues available: {have}")
    cue = {}
    for name, cols in (("B-head", H3), ("B-ft", T3)):
        if have[name]:
            cue[name] = [np.load(C.FOLD_DIR / f"{name}_outer{k}.npz")["cues"] for k in range(C.N_FOLDS)]
    arms = {n: c for n, c in B_ARMS.items() if not ((set(c) & set(H3) and "B-head" not in cue) or
                                                   (set(c) & set(T3) and "B-ft" not in cue))}
    t0 = time.time()
    for set_name, mask in (("891", tile_rule), ("798", rule)):
        sub, folds = C.subset_folds(roads, mask, "S")
        idx = np.flatnonzero(mask)
        y = sub.flooded.astype(int).to_numpy()
        calls = {n: np.full(len(y), -1) for n in arms}
        for k, (tr, te) in enumerate(folds):
            X = sub.copy()
            for name, cols in (("B-head", H3), ("B-ft", T3)):
                if name in cue:
                    X[cols] = cue[name][k][idx]
                    assert np.isfinite(X[cols].to_numpy()[np.concatenate([tr, te])]).any(axis=1).all()
            for n, cols in arms.items():
                calls[n][te] = C.limit_jobs(make(), NJOBS).fit(X.iloc[tr][cols], y[tr]).predict(X.iloc[te][cols])
        assert all((v >= 0).all() for v in calls.values())
        frame(sub, y, {f"S: {n}": v for n, v in calls.items()}).to_csv(
            C.OUT / f"spatialcv_calls_B-trained_{set_name}.csv", index=False)
        # per-road cues of the held-out roads (each road's own outer fold), for the record
        if set_name == "891":
            rec = roads[["tile_id", "road_id", "split", "flooded", "cloudy"]].copy()
            rec["outer_fold"] = rec.tile_id.map(FOLD_OF) + 1
            for name, cols in (("B-head", H3), ("B-ft", T3)):
                if name in cue:
                    vals = np.full((len(roads), 3), np.nan)
                    for k in range(C.N_FOLDS):
                        m = (rec.outer_fold - 1 == k).to_numpy()
                        vals[m] = cue[name][k][m]
                    rec[cols] = vals
            rec.to_csv(C.OUT / "spatialcv_heldout_cues.csv", index=False)
    assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == PROD_SHA
    say(f"B-trained done ({time.time() - t0:.0f} s): arms {list(arms)}")


# ======================================================================================================================
# Track A: cell random forests
# ======================================================================================================================
A_ARMS = {  # name: (columns, cut-off). Production's cut-off is production_cutoff() (0.75, the plan's fixed cut-off);
            # the other arms keep the cut-off logged for them last night (phase 1, out-of-fold training cells).
    "classical + DINOv2 (production)": ("classical + DINOv2", None),
    "classical + DINOv3": ("classical + DINOv3", 0.71),
    "DINOv3 only": ("DINOv3 only", 0.69),
    "DINOv2 only": ("DINOv2 only", 0.76),
}


def load_cells():
    """cell_table("train") + cell_table("val") with the DINOv2 and DINOv3 cell features (cached files only)."""
    from sn8_detect import CELL_FEATURES
    from sn8_dino_cells import DINO_CELL_FEATURES, cell_dino_table
    parts = []
    for split in ("train", "val"):
        c = cell_dino_table(split)
        f3 = sorted(d3.CACHE_DIR.glob(f"cells_{d3.MODEL3}_{split}_*.npz"))
        assert len(f3) == 1, f"DINOv3 cell cache for {split}"
        z = np.load(f3[0])
        assert np.array_equal(z["row"], c.row.to_numpy()) and np.array_equal(z["col"], c.col.to_numpy())
        assert np.array_equal(z["tile_id"], c.tile_id.astype(str).to_numpy())
        c[d3.DINO3_CELL_FEATURES] = z["features"]
        parts.append(c.assign(split=split))
    cells = pd.concat(parts, ignore_index=True)
    assert set(cells.tile_id) <= set(BLOCK_OF), "development tiles only"
    sets = {"classical": CELL_FEATURES, "classical + DINOv2": CELL_FEATURES + DINO_CELL_FEATURES,
            "DINOv2 only": DINO_CELL_FEATURES, "classical + DINOv3": CELL_FEATURES + d3.DINO3_CELL_FEATURES,
            "DINOv3 only": d3.DINO3_CELL_FEATURES}
    return cells, sets


def stage_a_rf():
    """Production's detector (classical_models()[production_detector()], 300 trees, seed 662) per outer fold: fit on
    the road-enriched training-split cells of the outer-training tiles (production's training sample), called on every
    held-out cell (both splits)."""
    from spatial_folds import cell_folds
    cells, sets = load_cells()
    folds = cell_folds(cells.tile_id.to_numpy(), C.SEED)
    is_train = (cells.split == "train").to_numpy()
    y = cells.label.to_numpy()
    say(f"{len(cells)} cells ({is_train.sum()} training-split, {(~is_train).sum()} validation-split); held-out per "
        f"fold {[len(te) for _, te in folds]}; fit rows per fold {[int(is_train[tr].sum()) for tr, _ in folds]}")
    for name, (fs, cut) in A_ARMS.items():
        cols = sets[fs]
        for k, (tr, te) in enumerate(folds):
            path = C.FOLD_DIR / f"A-rf_{name.replace(' ', '_').replace('+', 'and')}_outer{k}.npz"
            if path.exists():
                continue
            t = time.time()
            fit = tr[is_train[tr]]
            model = C.limit_jobs(classical_models()[production_detector()], NJOBS)
            model.fit(cells.iloc[fit][cols], y[fit])
            prob = model.predict_proba(cells.iloc[te][cols])[:, 1].astype(np.float32)
            del model
            np.savez_compressed(path, idx=te, prob=prob, cut=production_cutoff() if cut is None else cut,
                                seconds=time.time() - t, fit_rows=len(fit))
            say(f"A-rf {name} outer fold {k + 1}: {len(fit)} fit cells, {len(te)} called, {time.time() - t:.0f} s")
    assert hashlib.sha256(REGISTRY.read_bytes()).hexdigest() == PROD_SHA
    say("A-rf done")


if __name__ == "__main__":
    for stage in STAGES:
        {"B-frozen": stage_b_frozen, "B-trained": stage_b_trained, "A-rf": stage_a_rf}[stage]()
