"""Phase 1 of the DINOv3 benchmark (outputs/preregistration_dinov3_baseline.md): frozen DINOv3 (SAT-493M) against
frozen DINOv2 on Track B (flood per road) and Track A (finding roads). Development tiles only (186 train + 40 val).

Run from this folder, in the background (each stage caches what it makes in .cache/):
    /opt/miniconda3/bin/python3 -I run_phase1.py features  > features.log 2>&1   # DINOv3 tokens, Mac GPU (the long part)
    /opt/miniconda3/bin/python3 -I run_phase1.py trackA2   > trackA2.log 2>&1    # classical / DINOv2 cell arms (CPU)
    /opt/miniconda3/bin/python3 -I run_phase1.py trackB    > trackB.log 2>&1     # road arms only (a check)
    /opt/miniconda3/bin/python3 -I run_phase1.py all       > phase1.log 2>&1     # every arm, tables, pictures
Writes here: phase1_numbers.json (every table), phase1_*.png. Nothing is written to ProjectBranch/Code/results."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import dinov3_bench as d3   # puts ClaudeFunctions on sys.path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

from sn8_clouds import assessable
from sn8_cutoff import _prf, cell_scores, f1_cutoff, oof_probabilities, road_prior
from sn8_data import split_tables
from sn8_detect import CELL_FEATURES
from sn8_dino import DINO_CUES, DINO_VECTOR, ReduceColumns, with_dino
from sn8_dino_cells import DINO_CELL_FEATURES, cell_basis, cell_dino_table
from sn8_grey import GREY_DIR
from sn8_heldout import cue_predictions, held_out_report, paired_report, touched_roads
from sn8_models import FLOOD_MODELS, classical_models
from sn8_stages import production_cloud_rule, production_detector, production_features, production_model

SEED = 662
STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"
T0 = time.time()
TIMES = {}
FUNCS = Path(d3.FUNCS)


def say(*a):
    print(f"[{time.time() - T0:7.0f} s]", *a, flush=True)


def timed(name, fn, *args, **kw):
    t = time.time()
    out = fn(*args, **kw)
    TIMES[name] = round(time.time() - t, 1)
    say(f"{name}: {TIMES[name]} s")
    return out


def progress(msg, _last=[0.0]):
    if time.time() - _last[0] > 60:
        _last[0] = time.time()
        say(msg, _mps())


def _mps():
    import torch
    return f"(MPS driver memory {torch.mps.driver_allocated_memory() / 1e9:.2f} GB)" if torch.backends.mps.is_available() else ""


def tidy(df):
    return json.loads(df.to_json(orient="records", double_precision=4))


# ---------- data: development tiles only ----------
df, train, val, test, negative = split_tables(SEED)
dev = set(train.tile_id) | set(val.tile_id)
index = pd.read_csv(GREY_DIR / "tiles.csv")
assert len(train) == 186 and len(val) == 40
assert dev == set(index.tile_id[index.split.isin(["train", "val"])])
assert not dev & (set(test.tile_id) | set(negative.tile_id)), "development tiles only"
del test, negative                       # never used below

if STAGE in ("features", "all"):
    say("DINOv3 features (cached after the first run)")
    for split in ("train", "val"):
        timed(f"Track B road tokens, {split}", d3.dino3_table, split, progress=progress)
    timed("Track A cell basis (training tiles)", d3.cell_basis3, progress)
    for split in ("train", "val"):
        timed(f"Track A cell features, {split}", d3.cell_dino3_table, split, progress=progress)
    say("features done", _mps())
    if STAGE == "features":
        (HERE / "phase1_feature_times.json").write_text(json.dumps(TIMES, indent=1))
        sys.exit(0)

folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)   # by tile, both tracks
if STAGE != "trackB":   # trackB: the road arms only (a quick check while the cell features build)
    # ---------- Track A: cells ----------
    cells_train, cells_val = cell_dino_table("train"), cell_dino_table("val")
    assert set(cells_train.tile_id) <= set(train.tile_id) and set(cells_val.tile_id) <= set(val.tile_id)
    SETS2 = {"classical": CELL_FEATURES, "classical + DINOv2": CELL_FEATURES + DINO_CELL_FEATURES,
             "DINOv2 only": DINO_CELL_FEATURES}
    SETS3 = {"classical + DINOv3": CELL_FEATURES + d3.DINO3_CELL_FEATURES, "DINOv3 only": d3.DINO3_CELL_FEATURES,
             "classical + DINOv2 + DINOv3": CELL_FEATURES + DINO_CELL_FEATURES + d3.DINO3_CELL_FEATURES,
             "DINOv2 + DINOv3": DINO_CELL_FEATURES + d3.DINO3_CELL_FEATURES}
    if STAGE == "all":
        for split, cells in (("train", cells_train), ("val", cells_val)):
            c3 = d3.cell_dino3_table(split)
            assert c3.tile_id.equals(cells.tile_id) and c3.row.equals(cells.row) and c3.col.equals(cells.col)
            cells[d3.DINO3_CELL_FEATURES] = c3[d3.DINO3_CELL_FEATURES].to_numpy()
    sampled = float((cells_train.label == 1).mean())
    real = timed("road prior (training tiles)", road_prior, "train")
    make_detector = lambda: classical_models()[production_detector()]


    def track_a_arm(name, cols):
        """Cut-off from out-of-fold training cells (F1 at the real share), the detector fit on every training cell, and
        its validation probabilities. Cached in .cache/ by name, columns and cell counts."""
        key = hashlib.sha256(json.dumps([name, cols, len(cells_train), len(cells_val), production_detector(), sampled,
                                         real, repr(make_detector())]).encode()).hexdigest()[:16]
        path = d3.CACHE_DIR / f"trackA_{key}.npz"
        if not path.exists():
            t = time.time()
            oof = oof_probabilities(make_detector, cells_train, folds, cols)
            cut = f1_cutoff(cells_train.label, oof, sampled, real)[0]
            model = make_detector().fit(cells_train[cols], cells_train.label)
            prob = model.predict_proba(cells_val[cols])[:, 1]
            d3.CACHE_DIR.mkdir(exist_ok=True)
            np.savez_compressed(path, oof=oof, cut=cut, prob=prob, seconds=time.time() - t)
            say(f"Track A arm {name}: cut-off {cut:.2f}, {time.time() - t:.0f} s")
        z = np.load(path)
        return float(z["cut"]), z["prob"], float(z["seconds"])


    for name, cols in SETS2.items():
        track_a_arm(name, cols)
    if STAGE == "trackA2":
        sys.exit(0)

    A = {name: track_a_arm(name, cols) for name, cols in {**SETS2, **SETS3}.items()}
    TIMES["Track A detector fits (all arms, s)"] = round(sum(v[2] for v in A.values()), 1)
    np.savez_compressed(HERE / "phase1_trackA_val.npz", names=np.array(list(A)), cuts=np.array([A[n][0] for n in A]),
                        probs=np.stack([A[n][1] for n in A]), tile_id=cells_val.tile_id.to_numpy().astype(str),
                        row=cells_val.row.to_numpy(), col=cells_val.col.to_numpy(), label=cells_val.label.to_numpy())
    called = {f"{n} ({cut:.2f})": prob >= cut for n, (cut, prob, _) in A.items()}
    label = {n: f"{n} ({A[n][0]:.2f})" for n in A}
    yv, tv = cells_val.label.to_numpy(), cells_val.tile_id.to_numpy()
    track_a = cell_scores(yv, called, tv)
    counts = []
    for n in A:
        c = called[label[n]]
        counts.append({"arm": label[n], "TP": int(((yv == 1) & c).sum()), "FN": int(((yv == 1) & ~c).sum()),
                       "FP": int(((yv == 0) & c).sum()), "TN": int(((yv == 0) & ~c).sum())})
    track_a_counts = pd.DataFrame(counts)
    pairs_a = [("classical + DINOv2", "classical + DINOv3"), ("DINOv2 only", "DINOv3 only"),
               ("classical + DINOv2", "classical + DINOv2 + DINOv3"), ("DINOv2 only", "DINOv2 + DINOv3"),
               ("classical + DINOv3", "classical + DINOv2 + DINOv3")]
    track_a_pairs = []
    for base_name, cand in pairs_a:
        s = cell_scores(yv, {label[base_name]: called[label[base_name]], label[cand]: called[label[cand]]}, tv).iloc[1]
        track_a_pairs.append({"arm": label[cand], "against": label[base_name], "F1": s["F1"],
                              "F1 difference": s.iloc[6], "95% CI of the difference": s["95% CI of the difference"]})
    track_a_pairs = pd.DataFrame(track_a_pairs)
    say("Track A\n" + track_a.to_string() + "\n" + track_a_pairs.to_string())

# ---------- Track B: roads ----------
roads = d3.with_dino3(with_dino(touched_roads(include_cloudy=True)))
assert set(roads.split) <= {"train", "val"}
assert set(roads.tile_id) <= dev
touched = roads[~roads.cloudy].reset_index(drop=True)                # the 891 roads of dino_test
assessed = roads[assessable(roads, production_cloud_rule())].reset_index(drop=True)
assert len(touched) == 891 and len(assessed) == 798
assert assessed[["tile_id", "road_id"]].equals(touched_roads()[["tile_id", "road_id"]])
make = FLOOD_MODELS[production_model()]
base = [c for c in production_features() if c not in DINO_CUES]     # production without DINO (93 columns)
assert len(base) == 93 and all(c in production_features() for c in DINO_CUES)
V2 = lambda: ReduceColumns(DINO_VECTOR)                                        # the library's, as in dino_test
V2p = lambda: d3.ReducePrefixed(DINO_VECTOR, prefix="dino2_pc")               # when both vectors go in
DINO3_VECTOR = d3.DINO3_VECTOR
V3 = lambda: d3.ReducePrefixed(DINO3_VECTOR, prefix="dino3_pc")
C3 = d3.DINO3_CUES
ARMS = {  # name: (reducers, columns)
    "DINOv2 cues": ([], DINO_CUES),
    "DINOv2 cues + vector": ([V2], DINO_CUES + DINO_VECTOR),
    "base (production without DINO)": ([], base),
    "base + DINOv2 cues (production)": ([], base + DINO_CUES),
    "base + DINOv2 cues + vector": ([V2], base + DINO_CUES + DINO_VECTOR),
    "DINOv3 cues": ([], C3),
    "DINOv3 cues + vector": ([V3], C3 + DINO3_VECTOR),
    "base + DINOv3 cues": ([], base + C3),
    "base + DINOv3 cues + vector": ([V3], base + C3 + DINO3_VECTOR),
    "DINOv2 + DINOv3 cues": ([], DINO_CUES + C3),
    "DINOv2 + DINOv3 cues + vectors": ([V2p, V3], DINO_CUES + C3 + DINO_VECTOR + DINO3_VECTOR),
    "base + DINOv2 + DINOv3 cues": ([], base + DINO_CUES + C3),
    "base + DINOv2 + DINOv3 cues + vectors": ([V2p, V3], base + DINO_CUES + C3 + DINO_VECTOR + DINO3_VECTOR),
}
PRODUCTION_TYPE = [n for n in ARMS if n.startswith("base")]
PRODUCTION = "base + DINOv2 cues (production)"
COUNTERPART = {"DINOv3 cues": "DINOv2 cues", "DINOv3 cues + vector": "DINOv2 cues + vector",
               "base + DINOv3 cues": PRODUCTION, "base + DINOv3 cues + vector": "base + DINOv2 cues + vector",
               "DINOv2 + DINOv3 cues": "DINOv2 cues", "DINOv2 + DINOv3 cues + vectors": "DINOv2 cues + vector",
               "base + DINOv2 + DINOv3 cues": PRODUCTION,
               "base + DINOv2 + DINOv3 cues + vectors": "base + DINOv2 cues + vector"}
DINOV3_PARTNER = {"DINOv2 + DINOv3 cues": "DINOv3 cues", "DINOv2 + DINOv3 cues + vectors": "DINOv3 cues + vector",
                  "base + DINOv2 + DINOv3 cues": "base + DINOv3 cues",
                  "base + DINOv2 + DINOv3 cues + vectors": "base + DINOv3 cues + vector"}


def factory(reducers):
    return make if not reducers else (lambda: make_pipeline(*[r() for r in reducers], make()))


def predict(roads_set, names):
    y = roads_set.flooded.astype(int)
    out = {}
    for n in names:
        reducers, cols = ARMS[n]
        t = time.time()
        out[n] = cross_val_predict(factory(reducers)(), roads_set[cols], y, groups=roads_set.tile_id, cv=folds)
        TIMES[f"Track B {n} ({len(roads_set)} roads)"] = round(time.time() - t, 1)
    return out


def confusion(preds, roads_set):
    """held_out_report (TP / FN / FP / TN, accuracy with its tile-resampled 95% CI, recall, specificity, MCC) in arm
    order, with precision and F1 added."""
    r = held_out_report(preds, roads_set).set_index("features")
    r = r.loc[list(preds) + ['always "flooded"']].reset_index()
    r.insert(r.columns.get_loc("flooded found"), "precision", (r.TP / (r.TP + r.FP)).round(3))
    r.insert(r.columns.get_loc("dry kept dry") + 1, "F1", (2 * r.TP / (2 * r.TP + r.FP + r.FN)).round(3))
    return r.rename(columns={"flooded found": "recall"})


def paired(preds, roads_set, pairs):
    rows = []
    for cand, against in pairs:
        r = paired_report({against: preds[against], cand: preds[cand]}, against, roads_set).iloc[0].to_dict()
        rows.append({"arm": cand, "against": against, "accuracy difference": r[f"vs {against}"], "95% CI": r["95% CI"],
                     "roads fixed": r["roads fixed"], "roads broken": r["roads broken"], "McNemar p": r["McNemar p"]})
    return pd.DataFrame(rows)


P891 = predict(touched, ARMS)
b891 = confusion(P891, touched)
dino3_cue_table = held_out_report(cue_predictions(touched, C3, folds), touched)
pairs_b = ([(c, a) for c, a in COUNTERPART.items()] + [(c, PRODUCTION) for c in ARMS if "DINOv3" in c
                                                        and COUNTERPART[c] != PRODUCTION]
           + [(c, a) for c, a in DINOV3_PARTNER.items()]
           + [(c, "base (production without DINO)") for c in PRODUCTION_TYPE if c != "base (production without DINO)"])
p891 = paired(P891, touched, pairs_b)
say("Track B, 891 roads\n" + b891.to_string() + "\n" + p891.to_string())
P798 = predict(assessed, PRODUCTION_TYPE)
b798 = confusion(P798, assessed)
p798 = paired(P798, assessed, [(c, a) for c, a in pairs_b if c in PRODUCTION_TYPE and a in PRODUCTION_TYPE])
say("Track B, 798 roads\n" + b798.to_string() + "\n" + p798.to_string())
reproduce = {n: round(float((P891[n] == touched.flooded.astype(int)).mean()), 3) for n in
             ["DINOv2 cues", "DINOv2 cues + vector", "base (production without DINO)", PRODUCTION,
              "base + DINOv2 cues + vector"]}
logged = {"DINOv2 cues": 0.715, "DINOv2 cues + vector": 0.833, "base (production without DINO)": 0.831,
          PRODUCTION: 0.843, "base + DINOv2 cues + vector": 0.847}
say("DINOv2 reproduction (now vs logged 2026-10-23):", {n: (reproduce[n], logged[n]) for n in reproduce})
if STAGE == "trackB":
    sys.exit(0)

# ---------- pictures ----------
from sn8_roads import draw_change_map

VAL_TILE_B = val.nlargest(1, "roads_flooded").tile_id.iloc[0]       # fixed rule, as dino_test
VAL_TILE_A = val.nlargest(1, "roads").tile_id.iloc[0]               # fixed rule, as dino_cells_test
t = time.time()
c2, c3 = d3.show_change_pair(VAL_TILE_B, HERE / f"phase1_change_maps_{VAL_TILE_B}.png",
                             note="Fixed rule: the validation tile with the most flooded roads.")
on_tile = np.flatnonzero(touched.tile_id.to_numpy() == VAL_TILE_B)
truth = {touched.road_id[i]: int(touched.flooded[i]) for i in on_tile}
_show = plt.show
for n in (PRODUCTION, "base + DINOv3 cues", "base + DINOv3 cues + vector"):
    out = HERE / f"phase1_calls_{VAL_TILE_B}_{n.replace(' ', '_').replace('+', 'and').replace('(', '').replace(')', '')}.png"
    plt.show = lambda out=out: (plt.gcf().savefig(out, dpi=70), plt.close(plt.gcf()))
    draw_change_map(VAL_TILE_B, {touched.road_id[i]: int(P891[n][i]) for i in on_tile}, truth, f"{n} (held out)")
plt.show = _show
fit_a = {n: classical_models()[production_detector()].fit(cells_train[cols], cells_train.label)
         for n, cols in (("classical + DINOv2", SETS2["classical + DINOv2"]),
                         ("classical + DINOv3", SETS3["classical + DINOv3"]), ("DINOv3 only", SETS3["DINOv3 only"]))}
all_cells = d3.all_cells3(VAL_TILE_A, cell_basis(), d3.cell_basis3())
d3.show_cells_pair(VAL_TILE_A, [(n, fit_a[n], {**SETS2, **SETS3}[n], A[n][0]) for n in fit_a], all_cells,
                   HERE / f"phase1_cells_{VAL_TILE_A}.png")
TIMES["pictures"] = round(time.time() - t, 1)
picture_numbers = {"tile B": VAL_TILE_B, "tile A": VAL_TILE_A,
                   "patch change, median / 99th percentile": {
                       "DINOv2": [float(np.nanmedian(c2)), float(np.nanpercentile(c2, 99))],
                       "DINOv3": [float(np.nanmedian(c3)), float(np.nanpercentile(c3, 99))]}}

# ---------- log ----------
feature_times = json.loads((HERE / "phase1_feature_times.json").read_text()) if (HERE / "phase1_feature_times.json").exists() else {}
git = subprocess.run(["git", "-C", str(FUNCS.parent), "rev-parse", "--short", "HEAD"], capture_output=True,
                     text=True).stdout.strip()
numbers = {
    "run": time.strftime("%Y-%m-%dT%H:%M:%S"), "plan": "outputs/preregistration_dinov3_baseline.md",
    "GeoAI-Roads commit": git, "model": d3.MODEL3, "licence": d3.LICENCE3,
    "normalisation": dict(zip(("mean", "std"), d3.backbone3()[2:])),
    "code hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12]
                    for p in [*sorted(FUNCS.glob("sn8*.py")), HERE / "dinov3_bench.py", Path(__file__)]},
    "data": {"train tiles": len(train), "val tiles": len(val), "roads (tile rule)": len(touched),
             "roads (production cloud rule)": len(assessed), "training cells": len(cells_train),
             "validation cells": len(cells_val), "road share sampled / real": [sampled, real]},
    "times (s)": {**feature_times, **TIMES, "this run total": round(time.time() - T0, 1)},
    "DINOv2 reproduction (now, logged)": {n: [reproduce[n], logged[n]] for n in reproduce},
    "Track A": {"validation cells": tidy(track_a), "counts": tidy(track_a_counts), "pairs": tidy(track_a_pairs),
                "cut-offs": {n: v[0] for n, v in A.items()}},
    "Track B": {"891 roads": tidy(b891), "891 paired": tidy(p891), "DINOv3 single cues": tidy(dino3_cue_table),
                "798 roads": tidy(b798), "798 paired": tidy(p798)},
    "pictures": picture_numbers,
}
(HERE / "phase1_numbers.json").write_text(json.dumps(numbers, indent=1, default=float))
pd.DataFrame({"tile_id": touched.tile_id, "road_id": touched.road_id, "flooded": touched.flooded.astype(int),
              **{n: P891[n] for n in ARMS}}).to_csv(HERE / "phase1_calls_891.csv", index=False)
say("done; numbers in phase1_numbers.json")
