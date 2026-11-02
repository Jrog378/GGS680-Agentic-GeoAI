"""Scoring (c): every arm's effect on flood calls under the spatial folds S (preregistration_method_bench.md).

Production's tuned forest; folds = spatial_folds(all 1,037 roads, seed) as the factorial (scv_common.Setup.subset_folds),
training rows limited to the arm's gate, calls on every held-out road. Baseline: production's cached calls
c00__S__<seed> (spatial_cv_flood_calls.npz), reproduced first at seed 662 by refitting (378/63/103/254 on the 798).
Stage 1 (screen): every arm at seed 662. Stage 2: arms not worse at 662 (gain >= -0.5 points) over all 21 seeds.
Arms whose inputs are not ready are skipped (listed). Calls cached in mb_flood_calls.npz (resumable).
    nice -n 10 python3 -I run_flood.py [screen|seeds|combo] > run_flood_<stage>.log 2>&1
"""
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

T0 = time.time()
CALLS = C.HERE / "mb_flood_calls.npz"
NUMBERS = C.HERE / "flood_numbers.json"
NOT_WORSE = -0.005
C_ARMS = ["C1 He 2013", "C2 IR-MAD tone", "C3a fitted fade", "C3b Poisson seam", "C4 blob 0", "C4 blob 1250",
          "C4 blob 5000", "C4 blob 10000", "C5a gamma 1.8", "C5a gamma 2.2", "C5b band-linked RGB"]


def load_calls():
    if not CALLS.exists():
        return {}
    z = np.load(CALLS)
    return {k: z[k] for k in z.files}


def save_calls(d):
    tmp = C.HERE / "mb_flood_calls_writing.npz"
    np.savez_compressed(tmp, **d)
    tmp.replace(CALLS)


def _align(roads, tab):
    """tab's rows (tile_id, road_id, ...) in roads' order by (tile, road, occurrence); NaN rows where missing."""
    t = tab.copy()
    t["_n"] = t.groupby(["tile_id", "road_id"]).cumcount()
    r = roads[["tile_id", "road_id"]].copy()
    r["_n"] = r.groupby(["tile_id", "road_id"]).cumcount()
    return r.merge(t, on=["tile_id", "road_id", "_n"], how="left").drop(columns=["_n"])


class Data:
    def __init__(self):
        from scv_common import Setup
        S = Setup(build_x=False)
        self.S = S
        self.roads, self.y, self.cols = S.roads, S.y, S.cols
        self.gate_a, self.tile_rule, self.block = S.gates["a"], S.tile_rule, S.block
        self.X = S.roads[self.cols].copy()
        self.arms = {"production (refit)": (self.gate_a, list(self.cols))}
        self.missing = {}
        self._texture()
        self._corr()
        self._d3()

    def _texture(self):
        f = C.HERE / "texture_roads.csv"
        if not f.exists():
            self.missing["T1/T2/T3"] = "texture_roads.csv not ready"
            return
        import t1_lbp, t2_lowe, t3_glcm
        t = pd.read_csv(f)
        assert t.tile_id.equals(self.roads.tile_id.reset_index(drop=True)) and t.road_id.equals(self.roads.road_id.reset_index(drop=True))
        for c in t1_lbp.COLUMNS + t2_lowe.COLUMNS + t3_glcm.COLUMNS:
            self.X[c] = t[c].to_numpy()
        lbp_old = [c for c in self.cols if c.startswith("lbp_")]
        glcm_old = [c for c in self.cols if c.startswith("glcm_")]
        assert len(lbp_old) == 9 and len(glcm_old) == 15
        self.arms["T1 LBP riu2 + VAR"] = (self.gate_a, [c for c in self.cols if c not in lbp_old] + t1_lbp.COLUMNS)
        self.arms["T2 dense Lowe descriptor"] = (self.gate_a, list(self.cols) + t2_lowe.COLUMNS)
        self.arms["T3 per-strip GLCM"] = (self.gate_a, [c for c in self.cols if c not in glcm_old] + t3_glcm.COLUMNS)
        self.tex_cols = {"T1": (lbp_old, t1_lbp.COLUMNS), "T2": ([], t2_lowe.COLUMNS), "T3": (glcm_old, t3_glcm.COLUMNS)}

    def _corr(self):
        from sn8_glcm import GLCM_FEATURES
        from sn8_roads import FEATURES
        from sn8_texture import TEXTURE_FEATURES
        feats = FEATURES + GLCM_FEATURES + TEXTURE_FEATURES
        assert len(feats) == 93
        tiles = sorted(self.roads.tile_id[self.tile_rule].unique())
        have = [t for t in tiles if (C.BIG / "corr" / f"{t}.pkl").exists()]
        if len(have) < len(tiles):
            self.missing["C arms"] = f"corr pickles {len(have)}/{len(tiles)}"
            return
        after_cols = [c for c in feats if c.endswith("_after")]
        base = {m[: -len("_after")] for m in after_cols}
        raw = self.roads[["tile_id", "road_id"] + feats].reset_index(drop=True)
        tabs = {a: [] for a in ["C0"] + C_ARMS}
        self.corr_diag = {}
        for t in tiles:
            res = pickle.loads((C.BIG / "corr" / f"{t}.pkl").read_bytes())
            c0 = pd.DataFrame(res["C0_rows"]) if res["C0_rows"] else None
            if c0 is not None:
                tabs["C0"].append(c0)
            for a in C_ARMS:
                r = res["arms"][a]
                self.corr_diag.setdefault(a, []).append({"tile_id": t, **{k: v for k, v in r.items() if k != "rows"}})
                if r["same"] == "c0" and c0 is not None:
                    tabs[a].append(c0)
                elif r["same"] is None:
                    tabs[a].append(pd.DataFrame(r["rows"]))
        for a, parts in tabs.items():
            td = raw.copy()
            if parts:
                al = _align(self.roads, pd.concat(parts, ignore_index=True))
                hit = al[after_cols[0]].notna().to_numpy()
                for c in after_cols:
                    td.loc[hit, c] = al.loc[hit, c].to_numpy()
            for m in base:
                td[f"{m}_change"] = td[f"{m}_after"] - td[f"{m}_before"]
            key = "C0 current two-date" if a == "C0" else a
            pre = "td0_" if a == "C0" else f"td{C_ARMS.index(a) + 1}_"
            for c in feats:
                self.X[pre + c] = td[c].to_numpy()
            self.arms[key] = (self.gate_a, list(self.cols) + [pre + c for c in feats])

    def _d3(self):
        f = C.HERE / "d3_roads.csv"
        if not f.exists():
            self.missing["D3"] = "d3_roads.csv not ready"
            return
        from sn8_clouds import ROAD_CLOUD_CUT
        d = pd.read_csv(f)
        assert d.tile_id.equals(self.roads.tile_id.reset_index(drop=True))
        assert (np.abs(d.rise.to_numpy() - self.roads.cloud_dark_rise_road.to_numpy()) < 1e-9).all()
        assert ((self.tile_rule & (d.rise.to_numpy() < ROAD_CLOUD_CUT)) == self.gate_a).all()
        for k, name in (("rise_D3i", "D3i veto red>1.5 blue"), ("rise_D3ii", "D3ii veto local correlation"),
                        ("rise_D3", "D3 both vetoes")):
            self.arms[name] = (self.tile_rule & (d[k].to_numpy() < ROAD_CLOUD_CUT), list(self.cols))


def fit_arms(D, names, seeds, done):
    from scv_common import builders, run_pool
    B = builders()["S"]
    everyone = np.ones(len(D.y), bool)
    tasks = []
    for s in seeds:
        folds = D.S.subset_folds(everyone, B, s)
        for n in names:
            key = f"{n}__{s}"
            if key in done:
                continue
            gate, cols = D.arms[n]
            tasks.append((key, cols, [(tr[gate[tr]], te) for tr, te in folds]))
    C.log(T0, f"{len(tasks)} fits to run")

    def on_result(key, call):
        done[key] = call
        if len(done) % 10 == 0:
            save_calls(done)

    run_pool(D.X, D.y, D.S.model_name, tasks, on_result, n_workers=3)
    save_calls(done)


def prod_calls(seeds):
    z = np.load(C.SCV / "spatial_cv_flood_calls.npz")
    return np.stack([z[f"c00__S__{s}"] for s in seeds])


def score_arm(D, name, calls662, prod662):
    gate = D.arms[name][0]
    y = D.y
    out = {"name": name, "kept": int(gate.sum()), "kept_prod": int(D.gate_a.sum())}
    shared = gate & D.gate_a
    out["paired_shared"] = C.paired_flood(calls662, prod662, y, shared, D.block)
    out["acc_own"] = float((calls662[gate] == y[gate]).mean())
    if not np.array_equal(gate, D.gate_a):
        added = gate & ~D.gate_a
        removed = D.gate_a & ~gate
        out["added"] = int(added.sum()); out["removed"] = int(removed.sum())
        out["acc_added"] = float((calls662[added] == y[added]).mean()) if added.any() else None
        out["acc_removed_prod"] = float((prod662[removed] == y[removed]).mean()) if removed.any() else None
    return out


def own_metric_helped():
    """Arms whose own-metric interval excludes 0 in the good direction (hrc_numbers.json, ida_numbers.json)."""
    out = {}
    f = C.HERE / "hrc_numbers.json"
    if f.exists():
        h = json.loads(f.read_text())
        for r in h["paired_vs_D0"]:
            if r["scope"] == "all":
                out[r["a"]] = bool(r["ci_low"] > 0)
    f = C.HERE / "ida_numbers.json"
    if f.exists():
        h = json.loads(f.read_text())
        for arm, r in h.get("primary_vs_C0", {}).items():
            out[arm] = bool(r["ci"][1] < 0 and r.get("guard_ok", True))
    return out


def select_winners(num):
    """Preregistered: helped alone = own-metric interval excludes 0 (good direction) OR 21-seed mean flood gain >= 0;
    within each stage, the largest 21-seed mean flood gain among those (ties: the simpler, i.e. listed first)."""
    own = own_metric_helped()
    sd = num.get("seeds", {})
    helped, gains = {}, {}
    for n, r in sd.items():
        h_flood = r["mean_gain"] >= 0
        h_own = own.get(n, False)
        helped[n] = {"flood_not_worse": h_flood, "own_metric": h_own, "helped": h_flood or h_own}
        gains[n] = r["mean_gain"]
    for n, v in own.items():
        if v and n not in helped:
            helped[n] = {"flood_not_worse": False, "own_metric": True, "helped": True, "note": "not run at 21 seeds"}
    stage_of = lambda n: "D" if n.startswith("D") else "C" if n.startswith("C") and not n.startswith("C0") else \
        "T" if n.startswith("T") else None
    winner = {"D": None, "C": None, "T": None}
    for s in winner:
        cand = [n for n, h in helped.items() if h["helped"] and stage_of(n) == s and n in gains]
        if cand:
            winner[s] = max(cand, key=lambda n: gains[n])
    return {"helped": helped, "winner": winner}


def main():
    stage =sys.argv[1] if len(sys.argv) > 1 else "screen"
    h0 = C.registry_hash()
    D = Data()
    C.log(T0, f"arms ready: {list(D.arms)}; missing: {D.missing}")
    done = load_calls()
    num = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {}
    num["missing_inputs"] = D.missing
    y = D.y
    # reproduction: production refit at 662 == cached c00
    fit_arms(D, ["production (refit)"], [662], done)
    prod = prod_calls(C.SEEDS)
    ref = done["production (refit)__662"]
    assert np.array_equal(ref, prod[0]), "STOP: production refit at 662 differs from the cached c00 calls"
    from scv_common import counts
    cnt = counts(prod[0], y, D.gate_a)
    assert cnt == (378, 63, 103, 254), f"STOP: production counts {cnt}"
    C.log(T0, f"reproduction ok: production at 662 on the 798 = {cnt}")
    names = [n for n in D.arms if n != "production (refit)"]
    if stage == "screen":
        fit_arms(D, names, [662], done)
        scr = num.get("screen", {})
        for n in names:
            scr[n] = score_arm(D, n, done[f"{n}__662"], prod[0])
            if n.startswith("C") and "C0 current two-date__662" in done and n != "C0 current two-date":
                scr[n]["vs_C0"] = C.paired_flood(done[f"{n}__662"], done["C0 current two-date__662"], y, D.gate_a, D.block)
            p = scr[n]["paired_shared"]
            C.log(T0, f"{n:32s} kept {scr[n]['kept']:4d}  gain {100 * p['gain']:+.2f} [{100 * p['ci'][0]:+.2f}, "
                      f"{100 * p['ci'][1]:+.2f}] fixed {p['fixed']} broken {p['broken']} p={p['mcnemar_p']:.3f}")
        num["screen"] = scr
        if hasattr(D, "corr_diag"):
            num["corr_diag"] = {a: pd.DataFrame(v).drop(columns=["info"], errors="ignore").describe().to_dict()
                                for a, v in D.corr_diag.items()}
    elif stage == "seeds":
        scr = num["screen"]
        go = [n for n in names if n in scr and scr[n]["paired_shared"]["gain"] >= NOT_WORSE]
        C.log(T0, f"21-seed arms: {go}")
        fit_arms(D, go, C.SEEDS, done)
        sd = num.get("seeds", {})
        for n in go:
            calls = np.stack([done[f"{n}__{s}"] for s in C.SEEDS])
            shared = D.arms[n][0] & D.gate_a
            sd[n] = C.seed_avg(calls, prod, y, shared, D.block)
            if n.startswith("C") and n != "C0 current two-date" and all(f"C0 current two-date__{s}" in done for s in C.SEEDS):
                c0 = np.stack([done[f"C0 current two-date__{s}"] for s in C.SEEDS])
                sd[n]["vs_C0"] = C.seed_avg(calls, c0, y, D.gate_a, D.block)
            r = sd[n]
            C.log(T0, f"{n:32s} 21 seeds: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}]"
                      f" better {r['seeds_better']} worse {r['seeds_worse']}")
        num["seeds"] = sd
    elif stage == "combo":
        # winners per stage (preregistered rule), written by select_winners() into num["winners"]
        win = select_winners(num)
        num["winners"] = win
        C.log(T0, f"winners: {win}")
        picks = {k: v for k, v in win["winner"].items() if v}
        stages = sorted(picks)
        import itertools
        combos = []
        for r in range(2, len(stages) + 1):
            combos += list(itertools.combinations(stages, r))
        for combo in combos:
            name = "COMBO " + " + ".join(picks[s] for s in combo)
            gate = D.gate_a.copy()
            cols = list(D.cols)
            for s in combo:
                g, c = D.arms[picks[s]]
                if s == "D":
                    gate = g
                elif s == "T":
                    old, new = D.tex_cols[picks[s][:2]]
                    cols = [x for x in cols if x not in old] + new
                elif s == "C":
                    cols = cols + [x for x in c if x not in D.cols]
            D.arms[name] = (gate, cols)
        need = [n for n in D.arms if n.startswith("COMBO")] + [picks[s] for s in stages]
        fit_arms(D, need, C.SEEDS, done)
        out = {}
        alone = {}
        for n in [picks[s] for s in stages] + [x for x in D.arms if x.startswith("COMBO")]:
            calls = np.stack([done[f"{n}__{s}"] for s in C.SEEDS])
            alone[n] = calls
        # all comparisons on the roads every arm in the combination keeps (shared with production)
        for n in [x for x in D.arms if x.startswith("COMBO")]:
            members = n[len("COMBO "):].split(" + ")
            shared = D.arms[n][0] & D.gate_a
            for m in members:
                shared &= D.arms[m][0]
            r = C.seed_avg(alone[n], prod, y, shared, D.block)
            parts = {m: C.seed_avg(alone[m], prod, y, shared, D.block) for m in members}
            # interaction: combination gain minus the sum of the members' gains, block-bootstrapped together
            bt = C.Boot(D.block, shared)
            okc = (alone[n][:, shared] == y[shared]).mean(0)
            okp = (prod[:, shared] == y[shared]).mean(0)
            inter = okc - okp - sum((alone[m][:, shared] == y[shared]).mean(0) - okp for m in members)
            dist = bt.mean(inter)
            r["members"] = parts
            r["interaction"] = float(inter.mean())
            r["interaction_ci"] = [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]
            okc662 = done[f"{n}__662"]
            r["seed662"] = C.paired_flood(okc662, prod[0], y, shared, D.block)
            out[n] = r
            C.log(T0, f"{n}: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}], "
                      f"interaction {100 * r['interaction']:+.2f} [{100 * r['interaction_ci'][0]:+.2f}, "
                      f"{100 * r['interaction_ci'][1]:+.2f}]")
        num["combo"] = out
    C.write_json(NUMBERS, num)
    assert C.registry_hash() == h0
    C.log(T0, "done")


if __name__ == "__main__":
    main()
