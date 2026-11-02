"""Agent B, (f) Track A road finding under spatial folds: is a 2 m cell road? Test plan:
outputs/preregistration_spatial_cv.md, Agent B (f).

Detector: classical_models()[production_detector()] (the random forest, 300 trees) on production's detector features
(classical + DINOv2 cells: CELL_FEATURES + the 32 DINOv2 cell PCs), cut-off production_cutoff() = 0.75.
Cells: cell_table("train") (a road-enriched sample) + cell_table("val") (a uniform sample), pooled; every cell is on a
development tile. Fold schemes, seed 662 first:
  S  cell_folds(tile ids, s): each cell held out in its tile's block fold (the road folds' block map; no purge)
  T  StratifiedGroupKFold(5, shuffle=True, random_state=s) by tile over the pooled cells, as oof_probabilities does
  nested (seed 662, if the projected time is under 3 hours): nested_cell_folds; in each outer fold the cut-off is
  f1_cutoff on the inner out-of-fold probabilities of the outer-training cells only, at the real road share; the
  outer model is the S fold's model (same training cells), so its probabilities are reused.
Reproduction check first: the logged run (dino_cells_test 2026-10-23T173707) fitted on all training cells and scored
the validation cells at 0.75: 7,580 cells called road, precision 0.696, recall 0.732, F1 0.713. The script refits it
and stops if it differs. (The logged Track A result is this train -> val split; there are no logged T fold calls.)

The DINOv2 cell basis (32 PCs, label-free) stays as cached: it was fitted on the training tiles' patch tokens, and the
tokens are not cached, so a refit per fold would need the GPU (logged as a limitation).

CPU only (the forest at N_THREADS threads, leaving 2 cores for Agent C); cached tables only; development tiles only.
Memory: the machine is shared with Agent C's GPU run, so each forest is grown in warm-start steps of CHUNK trees whose
probabilities are summed and whose trees are then freed (forest_proba); the trees and the mean probability are those
of a single fit, and the reproduction check confirms the logged counts exactly.
Held-out probabilities are saved after every fit (spatial_cv_trackA_probs.npz, resumable). Scoring is in
spatial_cv_score.py.
    /opt/miniconda3/bin/python3 -I spatial_cv_trackA.py [--seeds N] > spatial_cv_trackA.log 2>&1   (from this folder)
"""
import os
os.environ.setdefault("MPLBACKEND", "Agg")
import hashlib
import json
import sys
import time
from pathlib import Path

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
HERE = Path(__file__).resolve().parent
for _p in (LIB, str(HERE)):
    if _p not in sys.path:
        sys.path.append(_p)

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

N_THREADS = 6
PROBS = HERE / "spatial_cv_trackA_probs.npz"
NESTED_BUDGET_S = 3 * 3600
SEED = 662
SEEDS = [662] + list(range(1, 21))


def save(arrays, meta):
    tmp = PROBS.with_name(PROBS.stem + "_writing.npz")
    np.savez_compressed(tmp, meta=json.dumps(meta), **arrays)
    tmp.replace(PROBS)


def load_cells():
    """The pooled development cells (train-split rows first, then val-split rows), the detector columns and settings."""
    from sn8_dino_cells import cell_dino_table
    from sn8_stages import production_cutoff, production_detector, production_detector_features
    name, cols = production_detector_features()
    assert name == "classical + DINOv2" and len(cols) == 44, (name, len(cols))
    cut = production_cutoff()
    assert cut == 0.75, cut
    tr, va = cell_dino_table("train"), cell_dino_table("val")
    cells = pd.concat([tr.assign(src="train"), va.assign(src="val")], ignore_index=True)
    cells["tile_id"] = cells.tile_id.astype(str)
    return cells, cols, cut, production_detector(), len(tr)


def tile_folds_cells(cells, seed):
    split = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    return list(split.split(cells, cells.label, groups=cells.tile_id))


def make_detector(name):
    from sn8_models import classical_models
    m = classical_models()[name]
    m.set_params(**{k: N_THREADS for k in m.get_params(deep=True) if k.endswith("n_jobs")})
    return m


CHUNK = 50      # trees grown per warm-start step; each step's trees are used, then freed (memory on a shared Mac)


def forest_proba(name, X_fit, y_fit, X_pred, chunk=CHUNK):
    """Road probability of the detector (SimpleImputer + RandomForestClassifier(300, random_state=662)) fitted on
    X_fit and applied to X_pred. The forest is grown with warm_start in steps of `chunk` trees; scikit-learn draws
    each tree's seed from the same stream as a single fit, so the trees are the single fit's trees. Each step's trees
    add their class-1 probabilities to a running sum and are then freed; the mean over the 300 trees is the forest's
    predict_proba. The reproduction check (logged train -> val run) confirms this."""
    model = make_detector(name)
    imp, rf = model.steps[0][1], model.steps[-1][1]
    assert type(rf).__name__ == "RandomForestClassifier" and len(model.steps) == 2
    Xf = imp.fit_transform(X_fit)
    Xp = np.asarray(imp.transform(X_pred), dtype=np.float32)
    n = rf.n_estimators
    rf.set_params(warm_start=True)
    total = np.zeros(len(Xp))
    done = 0
    while done < n:
        k = min(chunk, n - done)
        rf.set_params(n_estimators=done + k)
        rf.fit(Xf, y_fit)
        assert list(rf.classes_) == [0, 1]
        for t in rf.estimators_[done:done + k]:
            total += t.predict_proba(Xp, check_input=False)[:, 1]
        for i in range(done, done + k):
            rf.estimators_[i] = None
        done += k
    return total / n


def main():
    t0 = time.time()
    seeds_wanted = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 1
    from sn8_cutoff import f1_cutoff, road_prior
    from sn8_data import split_tables
    from spatial_folds import cell_folds, nested_cell_folds
    from sn8_results import RESULTS_DIR
    reg = RESULTS_DIR / "production.json"
    h0 = hashlib.sha256(reg.read_bytes()).hexdigest()
    cells, cols, cut, det, n_train = load_cells()
    _, train, val, _, _ = split_tables()        # test and negative are discarded here and never looked at
    dev = set(train.tile_id) | set(val.tile_id)
    assert set(cells.tile_id) <= dev and len(dev) == 226
    assert set(cells.tile_id[cells.src == "train"]) <= set(train.tile_id)
    assert set(cells.tile_id[cells.src == "val"]) <= set(val.tile_id)
    y = cells.label.to_numpy().astype(int)
    assert set(np.unique(y)) == {0, 1}
    print(f"cells: {len(cells)} on {cells.tile_id.nunique()} dev tiles ({n_train} train-split, {len(cells) - n_train} "
          f"val-split; road share {y[:n_train].mean():.3f} / {y[n_train:].mean():.3f}); detector {det}, {len(cols)} "
          f"columns, cut-off {cut}", f"{round(time.time() - t0)} s", flush=True)
    key = hashlib.sha256(repr([len(cells), cols, det, cut, int(y.sum())]).encode()).hexdigest()[:16]
    arrays, meta = {}, {"fingerprint": key}
    if PROBS.exists():
        z = np.load(PROBS, allow_pickle=False)
        m0 = json.loads(str(z["meta"]))
        if m0.get("fingerprint") == key:
            arrays = {k: z[k] for k in z.files if k != "meta"}
            meta = m0
            print(f"reusing {len(arrays)} saved probability sets", flush=True)
    meta.setdefault("fit seconds", {})
    meta.setdefault("log", [])

    def fit_predict(k, fit_idx, pred_idx):
        if k in arrays:
            return arrays[k]
        t = time.time()
        p = forest_proba(det, cells.iloc[fit_idx][cols], y[fit_idx], cells.iloc[pred_idx][cols]).astype(np.float64)
        arrays[k] = p
        meta["fit seconds"][k] = round(time.time() - t, 1)
        save(arrays, meta)
        print(f"  {k}: fitted on {len(fit_idx)} cells, called {len(pred_idx)}, {meta['fit seconds'][k]} s "
              f"(total {round(time.time() - t0)} s)", flush=True)
        return p

    # --- real road share (as dino_cells_test.ipynb: road_prior("train")) --------------------------------------------
    if "real" not in meta:
        t = time.time()
        meta["real"] = float(road_prior("train"))
        save(arrays, meta)
        print(f"real road share (road_prior('train')): {meta['real']:.5f} ({round(time.time() - t)} s)", flush=True)
    real = meta["real"]
    if "--prior-only" in sys.argv:
        print("--prior-only: real road share saved; no detector fitted", flush=True)
        return

    # --- 1. reproduction: fit on all train-split cells, call the val-split cells at the cut-off -------------------------
    itr, iva = np.arange(n_train), np.arange(n_train, len(cells))
    p = fit_predict("repro_val", itr, iva)
    called = p >= cut
    yv = y[iva]
    tp, fp, fn = int(((yv == 1) & called).sum()), int(((yv == 0) & called).sum()), int(((yv == 1) & ~called).sum())
    prec, rec, f1 = tp / (tp + fp), tp / (tp + fn), 2 * tp / (2 * tp + fp + fn)
    print(f"[1] reproduction (train -> val, cut-off {cut}): {int(called.sum())} cells called road, precision "
          f"{prec:.3f}, recall {rec:.3f}, F1 {f1:.3f}", flush=True)
    if not (int(called.sum()) == 7580 and round(prec, 3) == 0.696 and round(rec, 3) == 0.732 and round(f1, 3) == 0.713):
        print("STOP: Track A does not reproduce the logged run (7,580 called, 0.696 / 0.732 / 0.713)", flush=True)
        sys.exit(1)
    print("check passed: the logged dino_cells_test validation result is reproduced", flush=True)
    first_fit = meta["fit seconds"].get("repro_val")

    # --- 2. seed 662, fixed cut-off: S then T ------------------------------------------------------------------------
    ids = cells.tile_id.to_numpy()
    for scheme, folds in (("S", cell_folds(ids, SEED)), ("T", tile_folds_cells(cells, SEED))):
        for k, (tr, te) in enumerate(folds):
            fit_predict(f"{scheme}__{SEED}__{k}", tr, te)
        print(f"[2] {scheme} at seed {SEED}: done", f"{round(time.time() - t0)} s", flush=True)

    # --- 3. nested cut-off at seed 662, if the projected time is under 3 hours ----------------------------------------
    nested = nested_cell_folds(ids, SEED)
    s_fold_secs = [meta["fit seconds"][f"S__{SEED}__{k}"] for k in range(5) if f"S__{SEED}__{k}" in meta["fit seconds"]]
    todo = [(k, j) for k in range(5) for j in range(5) if f"nin__{SEED}__{k}__{j}" not in arrays]
    per_fit = (np.mean(s_fold_secs) if s_fold_secs else first_fit or 0) * 0.8   # inner sets hold ~80% of the cells
    projected = per_fit * len(todo)
    meta["nested projection s"] = round(projected)
    meta["log"].append(f"nested at seed {SEED}: {len(todo)} inner fits to go, projected {projected / 3600:.2f} h "
                       f"(budget 3 h)")
    print(meta["log"][-1], flush=True)
    if projected <= NESTED_BUDGET_S:
        for k, (otr, ote, inner) in enumerate(nested):
            oof = np.full(len(cells), np.nan, np.float64)
            for j, (itr_, ite_) in enumerate(inner):
                oof[ite_] = fit_predict(f"nin__{SEED}__{k}__{j}", itr_, ite_)
            assert not np.isnan(oof[otr]).any()
            c, curve = f1_cutoff(y[otr], oof[otr], float((y[otr] == 1).mean()), real)
            meta.setdefault("nested cut-offs", {})[str(k)] = c
            meta.setdefault("nested curves", {})[str(k)] = curve.iloc[:, 1].round(5).tolist()
            save(arrays, meta)
            print(f"[3] nested outer fold {k + 1}: cut-off {c:.2f} (inner out-of-fold, real share)", flush=True)
    else:
        meta["log"].append("nested cut-off at seed 662: not run (compute)")
        save(arrays, meta)
        print(meta["log"][-1], flush=True)

    # --- 4. more seeds with the fixed cut-off, only if asked and time remains ----------------------------------------
    for s in SEEDS[1:seeds_wanted]:
        for scheme, folds in (("S", cell_folds(ids, s)), ("T", tile_folds_cells(cells, s))):
            for k, (tr, te) in enumerate(folds):
                fit_predict(f"{scheme}__{s}__{k}", tr, te)
        print(f"[4] seed {s}: done", f"{round(time.time() - t0)} s", flush=True)
    h1 = hashlib.sha256(reg.read_bytes()).hexdigest()
    assert h1 == h0, "production.json changed during the run"
    print(f"production.json unchanged; saved {PROBS.name}", f"{round(time.time() - t0)} s", flush=True)


if __name__ == "__main__":
    main()
