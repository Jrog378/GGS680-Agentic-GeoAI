"""Agent B, spatially blocked CV for flood per road: the fits for arms (a), (b) and (c); (d) is scored from (c)'s calls.
Test plan: outputs/preregistration_spatial_cv.md, "Agent B" and "Decision rules" (written before any model was scored
on the new folds). Justin (2026-10-26): "can you do a cross validation so that you dont overfit".

  (a) production (tuned forest, 96 production columns) on its 798 kept roads
  (b) the best combo so far (+ the DINOv2 change vector, 16 PCs fitted inside each training fold) on the 891 tile-rule
      roads
  (c) the 16-arm pipeline factorial (gate x de-hazer x features) over all 1,037 development roads, each fold fitted on
      the training roads its gate keeps

Fold schemes (spatial_folds.py, imported, not edited): T (tile folds as each arm was logged), Tdev (tile folds split
over all 1,037), TM (size-matched tile folds), S (spatial blocks, purged), SB (S + buffer), L (7 x 7 blocks).
(a), (b): all six schemes x 21 seeds. (c): S x 21 seeds, SB at seed 662; its T is the logged factorial
(pipeline_factorial_seed_calls.npz, not refitted for the 21 seeds).

Reproduction checks first, at seed 662 under T (the script stops if one fails):
  (a) T 394/47/89/268 and = everything_together_calls.csv "A798 · production", call for call;
      Tdev 390/51/91/266 and = the factorial's production calls on the 798;
  (b) T 409/56/80/346 and = everything_together_calls.csv "B891 · production + DINOv2 vector (best so far)";
  (c) all 16 arms refitted once under the factorial's seed-662 folds = pipeline_factorial_seed_calls.npz, call for
      call (this refit is the check only; the T numbers used are read from the .npz).
Then consistency: (a) under S / SB = (c)'s production arm on the 798 (subsets inherit the block folds).

Development data only; cached tables only; CPU only (N_WORKERS processes, forests at n_jobs=1); production.json
sha256 checked before and after. Writes spatial_cv_flood_calls.npz (resumable) and prints to spatial_cv_flood.log:
    /opt/miniconda3/bin/python3 -I spatial_cv_flood.py > spatial_cv_flood.log 2>&1      (from this folder)
"""
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from scv_common import (FACTORIAL_NPZ, FLOOD_CALLS, PILOT, SEEDS, Setup, builders, counts, dino_cache_guard, load_npz,
                        registry_hash, run_pool, save_npz, stamp)

import hashlib
import numpy as np
import pandas as pd

SAVE_EVERY = 40


def main():
    t0 = time.time()
    dino_cache_guard()
    h0 = registry_hash()
    print(f"production.json sha256 {h0}", flush=True)
    S = Setup(build_x=True)
    B = builders()
    y, ka, rule891 = S.y, S.gates["a"], S.tile_rule
    everyone = np.ones(len(y), bool)
    code = {n: f"c{i:02d}" for i, n in enumerate(S.names)}

    # the logged factorial (T for (c)) and its CSV
    z = np.load(FACTORIAL_NPZ, allow_pickle=False)
    FC = {int(s): z["calls"][i].astype(int) for i, s in enumerate(z["seeds"])}
    assert sorted(FC) == sorted(SEEDS)
    fcsv = pd.read_csv(PILOT / "pipeline_factorial_calls.csv")
    assert fcsv.tile_id.equals(S.roads.tile_id) and fcsv.road_id.equals(S.roads.road_id)
    for i, n in enumerate(S.names):
        assert (FC[662][i] == fcsv[f"call seed 662 · {n}"].to_numpy()).all(), f"npz seed 662 differs from CSV: {n}"
    et = pd.read_csv(PILOT / "everything_together_calls.csv")
    assert et.tile_id.equals(S.roads.tile_id) and et.road_id.equals(S.roads.road_id)

    fold_sha = hashlib.sha256((Path(__file__).resolve().parent / "spatial_folds.py").read_bytes()).hexdigest()
    fingerprint = hashlib.sha256(repr([S.names, [S.arms[n][1] for n in S.names], S.model_name, S.cloud_rule,
                                       fold_sha, SEEDS]).encode()).hexdigest()[:16]
    done, meta = load_npz(FLOOD_CALLS)
    if meta and meta.get("fingerprint") != fingerprint:
        print("cached calls are for other arms or folds; recomputing", flush=True)
        done = {}
    elif done:
        print(f"reusing {len(done)} cached call sets", flush=True)
    n_new = [0]

    def save():
        save_npz(FLOOD_CALLS, done, {"fingerprint": fingerprint, "fold module sha256": fold_sha, "seeds": SEEDS,
                                     "arm codes": code, "model": S.model_name})

    def on_result(key, call):
        done[key] = call
        n_new[0] += 1
        if n_new[0] % SAVE_EVERY == 0:
            save()
            print(f"  {len(done)} call sets ({n_new[0]} new)", stamp(t0), flush=True)

    def tasks_ab(arm, scheme, seeds):
        mask, columns = (ka, S.cols) if arm == "A" else (rule891, S.best_cols)
        for s in seeds:
            key = f"{arm}__{scheme}__{s}"
            if key not in done:     # every training road of the subset is kept (the gate made the subset)
                yield key, columns, S.subset_folds(mask, B[scheme], s)

    def tasks_c(scheme, seeds, prefix=""):
        for s in seeds:
            folds = None
            for n in S.names:
                key = f"{prefix}{code[n]}__{scheme}__{s}"
                if key in done:
                    continue
                folds = folds or S.subset_folds(everyone, B[scheme], s)
                g, columns = S.arms[n]
                keep = S.gates[g]
                yield key, columns, [(tr[keep[tr]], te) for tr, te in folds]

    # --- 1. reproduction checks at seed 662 under T -------------------------------------------------------------------
    t1 = time.time()
    tasks = list(tasks_ab("A", "T", [662])) + list(tasks_ab("A", "Tdev", [662])) + list(tasks_ab("B", "T", [662])) + \
        list(tasks_c("T", [662], prefix="chk_"))
    print(f"\n[1] reproduction checks: {len(tasks)} call sets to fit", flush=True)
    run_pool(S.X, y, S.model_name, tasks, on_result)
    save()
    fails = []
    a_t, a_td, b_t = done["A__T__662"], done["A__Tdev__662"], done["B__T__662"]
    if counts(a_t, y, ka) != (394, 47, 89, 268):
        fails.append(f"(a) T gives {counts(a_t, y, ka)}, logged 394/47/89/268")
    if not (a_t[ka] == et["A798 · production"].to_numpy()[ka]).all():
        fails.append("(a) T differs from everything_together_calls.csv A798 · production")
    if counts(a_td, y, ka) != (390, 51, 91, 266):
        fails.append(f"(a) Tdev gives {counts(a_td, y, ka)}, logged 390/51/91/266")
    if not (a_td[ka] == FC[662][0][ka]).all():
        fails.append("(a) Tdev differs from the factorial's production calls on the 798")
    if counts(b_t, y, rule891) != (409, 56, 80, 346):
        fails.append(f"(b) T gives {counts(b_t, y, rule891)}, logged 409/56/80/346")
    best_col = "B891 · production + DINOv2 vector (best so far)"
    if not (b_t[rule891] == et[best_col].to_numpy()[rule891]).all():
        fails.append("(b) T differs from everything_together_calls.csv B891 best so far")
    for i, n in enumerate(S.names):
        if not (done[f"chk_{code[n]}__T__662"] == FC[662][i]).all():
            fails.append(f"(c) {n} refitted under T at seed 662 differs from the logged factorial")
    if fails:
        print("STOP: reproduction checks failed:", *fails, sep="\n  ", flush=True)
        sys.exit(1)
    print("checks passed:\n  (a) T 394/47/89/268 = everything_together A798 production, call for call\n"
          "  (a) Tdev 390/51/91/266 = the factorial's production calls on the 798\n"
          "  (b) T 409/56/80/346 = everything_together B891 best so far, call for call\n"
          "  (c) all 16 arms under the factorial's seed-662 tile folds = pipeline_factorial_seed_calls.npz, call for "
          "call", stamp(t1), flush=True)

    # --- 2. (a) and (b): six schemes x 21 seeds -----------------------------------------------------------------------
    t2 = time.time()
    tasks = [t for arm in ("A", "B") for scheme in ("S", "T", "Tdev", "TM", "SB", "L")
             for t in tasks_ab(arm, scheme, SEEDS)]
    print(f"\n[2] (a) and (b): {len(tasks)} call sets to fit", flush=True)
    run_pool(S.X, y, S.model_name, tasks, on_result)
    save()
    for arm, msk in (("A", ka), ("B", rule891)):
        for scheme in ("T", "Tdev", "TM", "S", "SB", "L"):
            acc = [float((done[f"{arm}__{scheme}__{s}"][msk] == y[msk]).mean()) for s in SEEDS]
            print(f"  ({arm.lower()}) {scheme:4s}: accuracy seed 662 {100 * acc[0]:.2f}, mean {100 * np.mean(acc):.2f} "
                  f"(min {100 * min(acc):.2f}, max {100 * max(acc):.2f})", flush=True)
    print("[2] done", stamp(t2), flush=True)

    # --- 3. (c): S x 21 seeds, SB at seed 662 ----------------------------------------------------------------------------
    t3 = time.time()
    tasks = list(tasks_c("S", SEEDS)) + list(tasks_c("SB", [662]))
    print(f"\n[3] (c) factorial: {len(tasks)} call sets to fit", flush=True)
    run_pool(S.X, y, S.model_name, tasks, on_result)
    save()
    for scheme, seeds in (("S", SEEDS), ("SB", [662])):
        for n in S.names:
            acc = [float((done[f"{code[n]}__{scheme}__{s}"][S.shared] == y[S.shared]).mean()) for s in seeds]
            print(f"  {scheme:2s} {n:12s} shared accuracy seed 662 {100 * acc[0]:.2f}, mean {100 * np.mean(acc):.2f}",
                  flush=True)
    print("[3] done", stamp(t3), flush=True)

    # --- 4. consistency: (a) under S / SB is (c)'s production arm on the 798 ---------------------------------------------
    for s in SEEDS:
        assert (done[f"A__S__{s}"][ka] == done[f"{code[S.prod]}__S__{s}"][ka]).all(), f"(a) S differs from (c) at {s}"
    assert (done["A__SB__662"][ka] == done[f"{code[S.prod]}__SB__662"][ka]).all()
    print("\nconsistency passed: (a) under S (21 seeds) and SB (seed 662) = the factorial's production arm on the 798",
          flush=True)
    for k, v in done.items():
        assert set(np.unique(v)) <= {-1, 0, 1}, k
    h1 = registry_hash()
    assert h1 == h0, "production.json changed during the run"
    print(f"production.json sha256 unchanged ({h1[:16]}...); {len(done)} call sets saved to {FLOOD_CALLS.name}",
          stamp(t0), flush=True)


if __name__ == "__main__":
    main()
