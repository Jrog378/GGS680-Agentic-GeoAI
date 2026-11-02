"""Agent B, (e) nested spatial CV: the honest accuracy of "pick the best combo" among the 16 factorial arms.
Test plan: outputs/preregistration_spatial_cv.md, Agent B (e).

For each of the 21 fold seeds s, nested_spatial_folds(1,037 dev roads, s) (inner seed = outer seed):
  - in each outer fold, an inner spatial CV on the outer-training rows only, for each of the 16 arms: fit on the
    inner-training rows the arm's gate keeps (after the inner purge), call the inner held-out rows;
  - pick rule: the highest pooled inner accuracy on the inner held-out roads kept by both gates; any arm within 0.005
    of the top is a tie; ties go to the fewest tools (the factorial's tool count), then the higher inner accuracy, then
    factorial order;
  - refit the picked arm on all outer-training rows its gate keeps and call the outer held-out roads. That refit is
    the (c) S fit of that arm in that fold, so it must equal spatial_cv_flood_calls.npz call for call (checked).
Writes spatial_cv_nested.npz (inner calls, resumable), spatial_cv_nested_picks.csv (one row per seed and outer fold:
every arm's inner accuracy and the pick) and the nested calls into the .npz. Scoring is in spatial_cv_score.py.

Development data only; cached tables only; CPU only; production.json sha256 checked before and after.
    /opt/miniconda3/bin/python3 -I spatial_cv_nested.py > spatial_cv_nested.log 2>&1      (from this folder)
"""
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from scv_common import (FLOOD_CALLS, HERE, NESTED_CALLS, SEEDS, Setup, dino_cache_guard, load_npz, registry_hash,
                        run_pool, save_npz, stamp)

import hashlib
import numpy as np
import pandas as pd

TIE = 0.005
SAVE_EVERY = 80
WORKERS = 5                    # 5 processes, so the scoring script can run beside it; 2 cores stay with Agent C


def pick(acc, tools, names):
    """The plan's pick rule over {arm: pooled inner accuracy}."""
    top = max(acc.values())
    tied = [n for n in names if acc[n] >= top - TIE - 1e-12]
    return sorted(tied, key=lambda n: (tools[n], -acc[n], names.index(n)))[0], tied


def main():
    t0 = time.time()
    dino_cache_guard()
    h0 = registry_hash()
    S = Setup(build_x=True)
    from spatial_folds import nested_spatial_folds
    y, shared = S.y, S.shared
    code = {n: f"c{i:02d}" for i, n in enumerate(S.names)}
    flood, fmeta = load_npz(FLOOD_CALLS)
    assert fmeta and all(f"{code[n]}__S__{s}" in flood for n in S.names for s in SEEDS), "run spatial_cv_flood.py first"
    fold_sha = hashlib.sha256((HERE / "spatial_folds.py").read_bytes()).hexdigest()
    fingerprint = hashlib.sha256(repr([S.names, [S.arms[n][1] for n in S.names], S.model_name, fold_sha, SEEDS, TIE])
                                 .encode()).hexdigest()[:16]
    done, meta = load_npz(NESTED_CALLS)
    if meta and meta.get("fingerprint") != fingerprint:
        print("cached nested calls are for other arms or folds; recomputing", flush=True)
        done = {}
    elif done:
        print(f"reusing {len(done)} cached call sets", flush=True)
    n_new = [0]

    def save():
        save_npz(NESTED_CALLS, done, {"fingerprint": fingerprint, "fold module sha256": fold_sha, "seeds": SEEDS,
                                      "arm codes": code, "tie": TIE})

    def on_result(key, call):
        done[key] = call
        n_new[0] += 1
        if n_new[0] % SAVE_EVERY == 0:
            save()
            print(f"  {len(done)} call sets ({n_new[0]} new)", stamp(t0), flush=True)

    nested = {s: nested_spatial_folds(S.R, s) for s in SEEDS}
    for s in SEEDS:      # the outer folds are the (c) S folds
        from spatial_folds import spatial_folds
        for (otr, ote, _), (tr, te) in zip(nested[s], spatial_folds(S.R, s)):
            assert np.array_equal(otr, tr) and np.array_equal(ote, te)
    print("outer folds = spatial_folds (21 seeds)", stamp(t0), flush=True)

    # --- pass 1: inner CV of every arm in every outer fold ---------------------------------------------------------------
    tasks = []
    for s in SEEDS:
        for k, (otr, ote, inner) in enumerate(nested[s]):
            for n in S.names:
                key = f"in__{code[n]}__{s}__{k}"
                if key in done:
                    continue
                keep = S.gates[S.arms[n][0]]
                tasks.append((key, S.arms[n][1], [(itr[keep[itr]], ite) for itr, ite in inner]))
    print(f"\n[1] inner CV: {len(tasks)} call sets to fit ({5 * len(tasks)} forests)", flush=True)
    run_pool(S.X, y, S.model_name, tasks, on_result, WORKERS)
    save()
    print("[1] done", stamp(t0), flush=True)

    # --- picks ------------------------------------------------------------------------------------------------------------
    rows, refits = [], []
    for s in SEEDS:
        for k, (otr, ote, inner) in enumerate(nested[s]):
            in_outer = np.zeros(len(y), bool)
            in_outer[otr] = True
            m = in_outer & shared
            acc = {}
            for n in S.names:
                c = done[f"in__{code[n]}__{s}__{k}"]
                assert (c[otr] >= 0).all() and (c[ote] == -1).all(), "inner calls must cover the outer training only"
                acc[n] = float((c[m] == y[m]).mean())
            chosen, tied = pick(acc, S.tools, S.names)
            top = max(acc, key=lambda n: (acc[n], -S.names.index(n)))
            rows.append({"seed": s, "outer fold": k + 1, "outer-training roads": len(otr),
                         "inner-scored shared roads": int(m.sum()), "outer held-out roads": len(ote),
                         "top arm": top, "top inner accuracy": acc[top], "tied arms": " | ".join(tied),
                         "picked": chosen, "picked tools": S.tools[chosen], "picked inner accuracy": acc[chosen],
                         **{f"inner accuracy · {n}": acc[n] for n in S.names}})
            key = f"out__{s}__{k}"
            if key not in done:
                keep = S.gates[S.arms[chosen][0]]
                refits.append((key, S.arms[chosen][1], [(otr[keep[otr]], ote)]))
    picks = pd.DataFrame(rows)
    picks.to_csv(HERE / "spatial_cv_nested_picks.csv", index=False)
    print(f"\n[2] picks: {picks.picked.value_counts().to_dict()}; refitting {len(refits)} picked arms", flush=True)
    run_pool(S.X, y, S.model_name, refits, on_result, WORKERS)

    # --- nested calls, checked against the (c) S fits -------------------------------------------------------------------
    for s in SEEDS:
        call = np.full(len(y), -1, np.int8)
        for k, (otr, ote, _) in enumerate(nested[s]):
            chosen = picks.loc[(picks.seed == s) & (picks["outer fold"] == k + 1), "picked"].iloc[0]
            c = done[f"out__{s}__{k}"]
            assert (c[ote] == flood[f"{code[chosen]}__S__{s}"][ote]).all(), f"refit of {chosen} differs, seed {s}"
            call[ote] = c[ote]
        assert (call >= 0).all()
        done[f"nested__{s}"] = call
        print(f"  seed {s:3d}: picks {list(picks.loc[picks.seed == s, 'picked'])}; nested shared accuracy "
              f"{100 * (call[shared] == y[shared]).mean():.2f}", flush=True)
    save()
    print("check passed: every refit equals the (c) S fit of the picked arm, call for call", flush=True)
    h1 = registry_hash()
    assert h1 == h0, "production.json changed during the run"
    print(f"production.json sha256 unchanged; saved {NESTED_CALLS.name} and spatial_cv_nested_picks.csv", stamp(t0),
          flush=True)


if __name__ == "__main__":
    main()
