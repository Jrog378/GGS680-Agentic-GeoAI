"""Agent B scoring for the spatially blocked CV (no fitting). Test plan: outputs/preregistration_spatial_cv.md.

Reads spatial_cv_flood_calls.npz (arms (a), (b), (c)), pipeline_factorial_seed_calls.npz ((c) under T, logged),
spatial_cv_nested.npz + spatial_cv_nested_picks.csv ((e)) and spatial_cv_trackA_probs.npz ((f), whatever is there)
and writes:
  spatial_cv_numbers.json      every number in evidence/14_spatial_cv.md
  spatial_cv_calls.csv         every road: masks, block, folds and the seed-662 call of every arm and scheme
  spatial_cv_seeds.csv         one row per arm, scheme, road set and seed
Metrics (every arm and scheme): TP, FN, FP, TN, accuracy, precision, recall, specificity, F1, MCC with 95% intervals
from 2,000 resamples (seed 662) of blocks for S and SB, 7 x 7 blocks for L, tiles for T, Tdev and TM, drawn as
sn8_heldout.held_out_report draws them. Paired against production on the same roads and scheme: accuracy difference
with a 5,000-resample interval (same units), roads fixed / broken, exact McNemar, and sn8_stages.confirm (read-only).
Seed-averaged intervals: each road's correctness averaged over the 21 seeds, the contrast taken road by road, blocks
resampled (2,000, seed 662). Development data only; nothing is fitted; production.json is not touched.
    /opt/miniconda3/bin/python3 -I spatial_cv_score.py > spatial_cv_score.log 2>&1      (from this folder)
"""
import json
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from scv_common import (FACTORIAL_NPZ, FLOOD_CALLS, HERE, NESTED_CALLS, PILOT, SEED, SEEDS, Setup, load_npz,
                        registry_hash)

import numpy as np
import pandas as pd
from scipy.stats import binomtest

N_BOOT, N_PAIR, N_GROUP = 2000, 5000, 5000
SCHEMES_AB = ["T", "Tdev", "TM", "S", "SB", "L"]
UNIT = {"T": "tile", "Tdev": "tile", "TM": "tile", "S": "block", "SB": "block", "L": "block7"}
SCHEME_NAME = {"T": "tile folds as logged", "Tdev": "tile folds split over all 1,037", "TM": "size-matched tile folds",
               "S": "spatial blocks (3 x 3 tiles, purged)", "SB": "spatial blocks + buffer",
               "L": "large blocks (7 x 7 tiles, purged)"}
P = 0          # index of seed 662
METRICS = ("accuracy", "precision", "recall", "specificity", "F1", "MCC")
t0 = time.time()


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


class Boot:
    """Resamples of the groups (tiles or blocks) of the roads in msk, drawn exactly as held_out_report /
    paired_report draw them (default_rng(662) unless given; one rng.integers(0, G, G) per resample), kept as a
    multiplicity matrix so any per-road statistic is a matrix product."""

    def __init__(self, groups, msk, n, rng=None):
        g = np.asarray(groups)[msk]
        uniq, self.gidx = np.unique(g, return_inverse=True)
        self.G = len(uniq)
        rng = np.random.default_rng(SEED) if rng is None else rng
        self.M = np.zeros((n, self.G), np.int32)
        for b in range(n):
            self.M[b] = np.bincount(rng.integers(0, self.G, self.G), minlength=self.G)
        self.n_g = np.bincount(self.gidx, minlength=self.G)
        self.msk = msk

    def sums(self, v):
        return self.M @ np.bincount(self.gidx, weights=np.asarray(v, float), minlength=self.G)

    def mean(self, v):
        return self.sums(v) / (self.M @ self.n_g)


_BOOTS = {}


def boot(groups_name, groups, msk, n):
    k = (groups_name, msk.tobytes(), n)
    if k not in _BOOTS:
        _BOOTS[k] = Boot(groups, msk, n)
    return _BOOTS[k]


def metric_values(tp, fn, fp, tn):
    tp, fn, fp, tn = (np.asarray(x, float) for x in (tp, fn, fp, tn))
    with np.errstate(invalid="ignore", divide="ignore"):
        n = tp + fn + fp + tn
        prec = np.where(tp + fp > 0, tp / (tp + fp), np.nan)
        rec = np.where(tp + fn > 0, tp / (tp + fn), np.nan)
        spec = np.where(tn + fp > 0, tn / (tn + fp), np.nan)
        f1 = np.where(tp + fp + fn > 0, 2 * tp / (2 * tp + fp + fn), np.nan)
        den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = np.where(den > 0, (tp * tn - fp * fn) / np.where(den > 0, den, 1), 0.0)
    return {"accuracy": (tp + tn) / n, "precision": prec, "recall": rec, "specificity": spec, "F1": f1, "MCC": mcc}


def score(call, y, msk, bt):
    """Confusion counts and metrics on msk with 95% intervals from the resamples bt."""
    p, t = call[msk], y[msk]
    assert (p >= 0).all(), "a road in the scored set has no call"
    ind = {"TP": (p == 1) & (t == 1), "FN": (p == 0) & (t == 1), "FP": (p == 1) & (t == 0), "TN": (p == 0) & (t == 0)}
    out = {k: int(v.sum()) for k, v in ind.items()}
    pt = metric_values(out["TP"], out["FN"], out["FP"], out["TN"])
    dist = metric_values(*(bt.sums(ind[k]) for k in ("TP", "FN", "FP", "TN")))
    for k in METRICS:
        out[k] = float(pt[k])
        out[f"{k} 95% CI"] = [float(np.nanpercentile(dist[k], 2.5)), float(np.nanpercentile(dist[k], 97.5))]
    out["roads"] = int(msk.sum())
    return out


def paired(call, base, y, msk, bt):
    """call against base on the same roads: accuracy difference, interval from bt, fixed / broken, exact McNemar and
    the promotion rule (sn8_stages.confirm, read-only)."""
    from sn8_stages import confirm
    ok, bk = call[msk] == y[msk], base[msk] == y[msk]
    d = bt.mean(ok) - bt.mean(bk)
    fixed, broken = int((ok & ~bk).sum()), int((~ok & bk).sum())
    p = binomtest(fixed, fixed + broken, 0.5).pvalue if fixed + broken else 1.0
    gain = float(ok.mean() - bk.mean())
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    row = pd.Series({"vs production": round(gain, 4), "95% CI": f"{lo:+.3f} to {hi:+.3f}", "McNemar p": round(p, 4)})
    passes, why = confirm(row)
    return {"gain": gain, "95% CI": [lo, hi], "fixed": fixed, "broken": broken, "McNemar p": float(p),
            "would pass (sn8_stages.confirm)": bool(passes), "rule": why}


def seed_stats(v, base=None):
    v = np.asarray(v, float)
    out = {"seed 662": float(v[P]), "mean": float(v.mean()), "SD": float(v.std(ddof=1)), "min": float(v.min()),
           "max": float(v.max())}
    if base is not None:
        d = v - np.asarray(base, float)
        out.update({"seeds above production": int((d > 1e-12).sum()), "seeds equal": int((np.abs(d) <= 1e-12).sum()),
                    "seeds below production": int((d < -1e-12).sum()), "mean gain vs production": float(d.mean())})
    return out


def seed_avg_ci(ok_a, ok_b, bt):
    """Seed-averaged interval of mean(ok_a) - mean(ok_b): ok_* are (seed, road-on-msk) correctness."""
    d = ok_a.mean(axis=0) - (ok_b.mean(axis=0) if ok_b is not None else 0)
    dist = bt.mean(d)
    return float(d.mean()), [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]


def excludes0(ci):
    return bool(ci[0] > 0 or ci[1] < 0)


def main():
    S = Setup(build_x=False)
    from spatial_folds import _correlogram, fold_table, spatial_folds, tile_folds
    y, ka, kb, shared, rule891, hazy = S.y, S.gates["a"], S.gates["b"], S.shared, S.tile_rule, S.hazy
    names, PROD, tools = S.names, S.prod, S.tools
    code = {n: f"c{i:02d}" for i, n in enumerate(names)}
    G = {"tile": S.tile, "block": S.block, "block7": S.block7}
    flood, fmeta = load_npz(FLOOD_CALLS)
    assert fmeta, "run spatial_cv_flood.py first"
    z = np.load(FACTORIAL_NPZ, allow_pickle=False)
    FC = {int(s): z["calls"][i].astype(np.int8) for i, s in enumerate(z["seeds"])}
    fact = json.load(open(PILOT / "pipeline_factorial_numbers.json"))

    def A(arm, scheme, s):
        return flood[f"{arm}__{scheme}__{s}"]

    def Cc(n, scheme, s):
        if scheme == "T":
            return FC[s][names.index(n)]
        return flood[f"{code[n]}__{scheme}__{s}"]

    seed_rows = []
    numbers = {"what": "Agent B: spatially blocked CV of the flood-per-road arms (development data only: Louisiana-East "
                       "train + val, 226 tiles, 1,037 roads); Track A road finding on the same tiles",
               "test plan": "outputs/preregistration_spatial_cv.md (Agent B, Decision rules)",
               "fold module": "spatial_cv/spatial_folds.py (sha256 " + fmeta["fold module sha256"][:16] + "...)",
               "production model": S.model_name, "cloud rule": S.cloud_rule, "fold seeds": SEEDS,
               "schemes": SCHEME_NAME, "resampling units": UNIT,
               "roads": {"development": len(y), "kept a (798)": int(ka.sum()), "kept b (790)": int(kb.sum()),
                         "shared (757)": int(shared.sum()), "tile rule (891)": int(rule891.sum()),
                         "flooded shared": int(y[shared].sum()), "tiles": int(len(set(S.tile))),
                         "blocks (3 x 3) with roads": int(len(set(S.block))),
                         "blocks (7 x 7) with roads": int(len(set(S.block7)))}}

    # ============ (a) production on its 798 and (b) the best combo on the 891 =====================================
    ab = {}
    corr_ab = {}
    for arm, label, msk in (("A", "(a) production on its 798 kept roads", ka),
                            ("B", "(b) best combo so far (production + DINOv2 vector) on the 891 tile-rule roads",
                             rule891)):
        sec = {"label": label, "roads": int(msk.sum()), "schemes": {}}
        for scheme in SCHEMES_AB:
            calls = [A(arm, scheme, s) for s in SEEDS]
            ok = np.stack([c[msk] == y[msk] for c in calls])            # (seed, road on msk)
            corr_ab[(arm, scheme)] = ok
            sc = score(calls[P], y, msk, boot(UNIT[scheme], G[UNIT[scheme]], msk, N_BOOT))
            acc = ok.mean(axis=1)
            sec["schemes"][scheme] = {"scheme": SCHEME_NAME[scheme], "seed 662": sc, "accuracy over seeds":
                                      seed_stats(acc), "metric means over seeds": {
                                          m: float(np.mean([score(c, y, msk, boot("block", G["block"], msk, 2)
                                                                  )[m] for c in calls])) for m in METRICS}}
            for k, s in enumerate(SEEDS):
                seed_rows.append({"section": label[:3], "arm": label[4:], "scheme": scheme, "road set": str(msk.sum()),
                                  "seed": s, "accuracy": acc[k]})
            print(f"{label[:3]} {scheme:4s}: seed 662 {100 * sc['accuracy']:.2f} "
                  f"[{100 * sc['accuracy 95% CI'][0]:.1f}, {100 * sc['accuracy 95% CI'][1]:.1f}]; mean over seeds "
                  f"{100 * acc.mean():.2f} (SD {100 * acc.std(ddof=1):.2f})", flush=True)
        # optimism gaps (same roads): T - S and its parts
        bt_pair = boot("block", G["block"], msk, N_PAIR)
        bt_avg = boot("block", G["block"], msk, N_BOOT)
        gaps = {}
        for name, hi_s, lo_s in (("T - S (optimism gap)", "T", "S"), ("Tdev - S", "Tdev", "S"),
                                 ("T - Tdev (own split vs split over the 1,037)", "T", "Tdev"),
                                 ("Tdev - TM (smaller training sets)", "Tdev", "TM"),
                                 ("TM - S (leakage + nearness)", "TM", "S"), ("S - SB (buffer)", "S", "SB"),
                                 ("S - L (larger blocks)", "S", "L")):
            oh, ol = corr_ab[(arm, hi_s)], corr_ab[(arm, lo_s)]
            per_seed = oh.mean(axis=1) - ol.mean(axis=1)
            pr = paired(A(arm, hi_s, SEED), A(arm, lo_s, SEED), y, msk, bt_pair)
            m, ci = seed_avg_ci(oh, ol, bt_avg)
            gaps[name] = {"seed 662": float(per_seed[P]), "seed 662 95% CI (blocks)": pr["95% CI"],
                          "seed 662 roads right only in the first / only in the second": [pr["fixed"], pr["broken"]],
                          "seed 662 McNemar p": pr["McNemar p"], "seed mean": float(per_seed.mean()),
                          "seed SD": float(per_seed.std(ddof=1)), "seed min": float(per_seed.min()),
                          "seed max": float(per_seed.max()), "seeds > 0": int((per_seed > 1e-12).sum()),
                          "seeds < 0": int((per_seed < -1e-12).sum()), "seed-averaged 95% CI (blocks)": ci,
                          "excludes 0": excludes0(ci)}
            print(f"  gap {name}: seed 662 {100 * per_seed[P]:+.2f}, mean {100 * per_seed.mean():+.2f} "
                  f"[{100 * ci[0]:+.2f}, {100 * ci[1]:+.2f}]", flush=True)
        sec["optimism gaps (accuracy, same roads)"] = gaps
        ab[arm] = sec
    # (b) against production on the 798 (same roads, same scheme)
    vs = {}
    for scheme in SCHEMES_AB:
        bt = boot(UNIT[scheme], G[UNIT[scheme]], ka, N_PAIR)
        okb = np.stack([A("B", scheme, s)[ka] == y[ka] for s in SEEDS])
        oka = np.stack([A("A", scheme, s)[ka] == y[ka] for s in SEEDS])
        pr = paired(A("B", scheme, SEED), A("A", scheme, SEED), y, ka, bt)
        m, ci = seed_avg_ci(okb, oka, boot("block", G["block"], ka, N_BOOT))
        per = [paired(A("B", scheme, s), A("A", scheme, s), y, ka, bt) for s in SEEDS]
        vs[scheme] = {"seed 662": pr, "(b) accuracy on the 798 over seeds": seed_stats(okb.mean(1), oka.mean(1)),
                      "(b) on the 798, seed 662": score(A("B", scheme, SEED), y, ka,
                                                        boot(UNIT[scheme], G[UNIT[scheme]], ka, N_BOOT)),
                      "seed-averaged gain 95% CI (blocks)": ci, "seed-averaged gain": m,
                      "seeds the rule would pass": int(sum(p_["would pass (sn8_stages.confirm)"] for p_ in per))}
        for k, s in enumerate(SEEDS):
            seed_rows.append({"section": "(b)", "arm": "best combo vs production", "scheme": scheme, "road set": "798",
                              "seed": s, "accuracy": float(okb[k].mean()), "production accuracy": float(oka[k].mean()),
                              "gain vs production": per[k]["gain"], "95% CI": per[k]["95% CI"],
                              "fixed": per[k]["fixed"], "broken": per[k]["broken"], "McNemar p": per[k]["McNemar p"],
                              "would pass": per[k]["would pass (sn8_stages.confirm)"]})
        print(f"(b) vs production on the 798, {scheme}: {100 * pr['gain']:+.2f} [{100 * pr['95% CI'][0]:+.2f}, "
              f"{100 * pr['95% CI'][1]:+.2f}] p = {pr['McNemar p']:.4f}; seed-averaged {100 * m:+.2f} "
              f"[{100 * ci[0]:+.2f}, {100 * ci[1]:+.2f}]", flush=True)
    ab["B"]["against production on the 798 (same roads, same scheme)"] = vs
    numbers["(a) production"] = ab["A"]
    numbers["(b) best combo so far"] = ab["B"]

    # ============ (c) the 16-arm factorial ==========================================================================
    corr = {sch: np.stack([np.stack([Cc(n, sch, s) == y for n in names]) for s in SEEDS]) for sch in ("S", "T")}
    calls_seed = {sch: np.stack([np.stack([Cc(n, sch, s) for n in names]) for s in SEEDS]) for sch in ("S", "T")}
    fac = {"arms": {}, "seed 662": {}, "paired against production": {}}
    for sch in ("S", "SB", "T"):
        bt_s = boot(UNIT[sch], G[UNIT[sch]], shared, N_BOOT)
        rows = {n: score(Cc(n, sch, SEED), y, shared, bt_s) for n in names}
        if sch == "T":     # the logged factorial's intervals are reproduced (tiles, same draws)
            for n in names:
                lo, hi = rows[n]["accuracy 95% CI"]
                lf, hf = fact["(i) shared roads, seed 662"]["arms"][n]["accuracy 95% CI"]
                assert abs(lo - lf) < 1e-5 and abs(hi - hf) < 1e-5, f"T interval not reproduced for {n}"
        own = {}
        for g in ("a", "b"):
            bt_o = boot(UNIT[sch], G[UNIT[sch]], S.gates[g], N_BOOT)
            own[g] = {n: score(Cc(n, sch, SEED), y, S.gates[g], bt_o) for n in names if n.startswith(g + "·")}
        btp = boot(UNIT[sch], G[UNIT[sch]], shared, N_PAIR)
        pr = {n: paired(Cc(n, sch, SEED), Cc(PROD, sch, SEED), y, shared, btp) for n in names[1:]}
        if sch == "T":
            for r in fact["(i) shared roads, seed 662"]["paired against production"]:
                assert abs(pr[r["features"]]["McNemar p"] - r["McNemar p (unrounded)"]) <= 1e-5 * r["McNemar p (unrounded)"]
                lo, hi = (float(x) for x in r["95% CI"].replace(" to ", " ").split())
                assert abs(pr[r["features"]]["95% CI"][0] - lo) <= 0.0005 + 1e-9, r["features"]
        bt798 = boot(UNIT[sch], G[UNIT[sch]], ka, N_PAIR)
        pr798 = {n: paired(Cc(n, sch, SEED), Cc(PROD, sch, SEED), y, ka, bt798) for n in names[1:8]}
        fac["seed 662"][sch] = {"shared roads": rows, "own kept roads": own}
        fac["paired against production"][sch] = {"shared roads": pr, "production's 798 (gate-a arms)": pr798}
        print(f"\n(c) {sch} seed 662, shared roads: " + "; ".join(
            f"{n} {100 * rows[n]['accuracy']:.1f}" for n in names), flush=True)
    print("check passed: (c) T intervals and paired tests reproduce pipeline_factorial_numbers.json", flush=True)
    # across seeds, S and T
    acc_sh = {sch: corr[sch][:, :, shared].mean(axis=2) for sch in ("S", "T")}       # (seed, arm)
    acc_own = {sch: np.stack([corr[sch][:, i, S.gates[n[0]]].mean(axis=1) for i, n in enumerate(names)], 1)
               for sch in ("S", "T")}
    bt_sh_pair = {"S": boot("block", G["block"], shared, N_PAIR), "T": boot("tile", G["tile"], shared, N_PAIR)}
    bt_sh_avg = boot("block", G["block"], shared, N_BOOT)
    rule_seeds = {sch: {n: 0 for n in names[1:]} for sch in ("S", "T")}
    for sch in ("S", "T"):
        for k, s in enumerate(SEEDS):
            for i, n in enumerate(names):
                row = {"section": "(c)", "arm": n, "scheme": sch, "road set": "757 shared", "seed": s,
                       "accuracy": float(acc_sh[sch][k, i]), "own kept accuracy": float(acc_own[sch][k, i])}
                if i:
                    r = paired(calls_seed[sch][k, i], calls_seed[sch][k, 0], y, shared, bt_sh_pair[sch])
                    rule_seeds[sch][n] += int(r["would pass (sn8_stages.confirm)"])
                    row.update({"production accuracy": float(acc_sh[sch][k, 0]), "gain vs production": r["gain"],
                                "95% CI": r["95% CI"], "fixed": r["fixed"], "broken": r["broken"],
                                "McNemar p": r["McNemar p"], "would pass": r["would pass (sn8_stages.confirm)"]})
                seed_rows.append(row)
    for i, n in enumerate(names):
        okS, okT = corr["S"][:, i, shared], corr["T"][:, i, shared]
        m_gain, ci_gain = seed_avg_ci(okS, corr["S"][:, 0, shared], bt_sh_avg)
        m_gap, ci_gap = seed_avg_ci(okT, okS, bt_sh_avg)
        gap = acc_sh["T"][:, i] - acc_sh["S"][:, i]
        pg = paired(Cc(n, "T", SEED), Cc(n, "S", SEED), y, shared, bt_sh_pair["S"])
        fac["arms"][n] = {
            "gate": S.gate_name[n.split("·")[0]], "cues": S.cue_name[n.split("·")[1]],
            "features": S.feat_name[n.split("·")[2]], "tools": tools[n],
            "S shared accuracy over seeds": seed_stats(acc_sh["S"][:, i], acc_sh["S"][:, 0]),
            "T shared accuracy over seeds": seed_stats(acc_sh["T"][:, i], acc_sh["T"][:, 0]),
            "S own kept accuracy over seeds": seed_stats(acc_own["S"][:, i]),
            "T own kept accuracy over seeds": seed_stats(acc_own["T"][:, i]),
            "S gain vs production, seed-averaged": m_gain, "S gain vs production, seed-averaged 95% CI (blocks)":
                ci_gain if i else None, "S seed-averaged gain excludes 0": excludes0(ci_gain) if i else None,
            "S rule passes (of 21 seeds, shared, blocks)": rule_seeds["S"].get(n),
            "T rule passes (of 21 seeds, shared, tiles)": rule_seeds["T"].get(n),
            "optimism gap T - S, seed 662": float(gap[P]), "optimism gap seed 662 95% CI (blocks)": pg["95% CI"],
            "optimism gap seed mean": float(gap.mean()), "optimism gap seed SD": float(gap.std(ddof=1)),
            "optimism gap seed min / max": [float(gap.min()), float(gap.max())],
            "optimism gap seeds > 0": int((gap > 1e-12).sum()),
            "optimism gap seed-averaged 95% CI (blocks)": ci_gap, "optimism gap excludes 0": excludes0(ci_gap)}
        # check: T numbers equal the logged factorial's
        lf = fact["across seeds (shared roads)"][n]
        assert abs(lf["shared accuracy mean"] - acc_sh["T"][:, i].mean()) < 1e-5, n
    print("check passed: (c) T seed means reproduce pipeline_factorial_numbers.json", flush=True)
    print("\n(c) shared-road accuracy, mean over 21 seeds: T vs S (gap)")
    for i, n in enumerate(names):
        a = fac["arms"][n]
        print(f"  {n:12s} T {100 * acc_sh['T'][:, i].mean():.2f}  S {100 * acc_sh['S'][:, i].mean():.2f} "
              f"(SD {100 * acc_sh['S'][:, i].std(ddof=1):.2f}, {100 * acc_sh['S'][:, i].min():.1f}-"
              f"{100 * acc_sh['S'][:, i].max():.1f})  gap {100 * a['optimism gap seed mean']:+.2f} "
              f"[{100 * a['optimism gap seed-averaged 95% CI (blocks)'][0]:+.2f}, "
              f"{100 * a['optimism gap seed-averaged 95% CI (blocks)'][1]:+.2f}]"
              + (f"  gain vs prod {100 * a['S gain vs production, seed-averaged']:+.2f} "
                 f"[{100 * a['S gain vs production, seed-averaged 95% CI (blocks)'][0]:+.2f}, "
                 f"{100 * a['S gain vs production, seed-averaged 95% CI (blocks)'][1]:+.2f}] rule S "
                 f"{rule_seeds['S'][n]}/21" if i else ""), flush=True)

    # contrasts (main effects, interactions), as the factorial defines them
    def w_of(terms):
        w = np.zeros(len(names))
        for (g, c, f), v in terms.items():
            w[names.index(f"{g}·{c}·{f}")] += v
        return w

    def avg(terms_list):
        out = {}
        for t_ in terms_list:
            for k, v in t_.items():
                out[k] = out.get(k, 0) + v / len(terms_list)
        return out

    Gs, CU, FE = ["a", "b"], ["raw", "td", "he", "both"], ["prod", "vec"]
    CN = S.cue_name
    CON = {"main: spotter gate (b - a)": avg([{("b", c, f): 1, ("a", c, f): -1} for c in CU for f in FE])}
    for k in ("td", "he", "both"):
        CON[f"main: {CN[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for g in Gs for f in FE])
    CON["main: DINOv2 vector (vec - prod)"] = avg([{(g, c, "vec"): 1, (g, c, "prod"): -1} for g in Gs for c in CU])
    for g in Gs:
        for k in ("td", "he", "both"):
            CON[f"within gate {g}: {CN[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for f in FE])
        CON[f"within gate {g}: DINOv2 vector"] = avg([{(g, c, "vec"): 1, (g, c, "prod"): -1} for c in CU])
    for f in FE:
        for k in ("td", "he", "both"):
            CON[f"within features {f}: {CN[k]} (- raw)"] = avg([{(g, k, f): 1, (g, "raw", f): -1} for g in Gs])
    for k in ("td", "he", "both"):
        CON[f"interaction gate x {CN[k]}"] = avg([{("b", k, f): 1, ("b", "raw", f): -1, ("a", k, f): -1,
                                                   ("a", "raw", f): 1} for f in FE])
    CON["interaction gate x vector"] = avg([{("b", c, "vec"): 1, ("b", c, "prod"): -1, ("a", c, "vec"): -1,
                                             ("a", c, "prod"): 1} for c in CU])
    for k in ("td", "he", "both"):
        CON[f"interaction {CN[k]} x vector"] = avg([{(g, k, "vec"): 1, (g, "raw", "vec"): -1, (g, k, "prod"): -1,
                                                    (g, "raw", "prod"): 1} for g in Gs])
    W = {k: w_of(v) for k, v in CON.items()}

    def contrast_table(value, msk):
        """value (seed, arm, road) -> each contrast at seed 662 and seed-averaged, blocks resampled (2,000)."""
        bt = boot("block", G["block"], msk, N_BOOT)
        per_seed = value[:, :, msk].mean(axis=2)
        out = {}
        for k, w in W.items():
            v = per_seed @ w
            d0 = w @ value[P][:, msk].astype(float)
            d = w @ value.mean(axis=0)[:, msk].astype(float)
            dist0, dist = bt.mean(d0), bt.mean(d)
            ci0 = [float(np.percentile(dist0, 2.5)), float(np.percentile(dist0, 97.5))]
            ci = [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]
            out[k] = {"seed 662": float(v[P]), "seed 662 95% CI (blocks)": ci0, "seed mean": float(v.mean()),
                      "seed SD": float(v.std(ddof=1)), "seed min": float(v.min()), "seed max": float(v.max()),
                      "seeds > 0": int((v > 1e-12).sum()), "seeds < 0": int((v < -1e-12).sum()),
                      "seed-averaged 95% CI (blocks)": ci, "matters (seed-averaged CI excludes 0)": excludes0(ci)}
        return out

    fac["contrasts, shared roads (accuracy)"] = {sch: contrast_table(corr[sch].astype(float), shared)
                                                 for sch in ("S", "T")}
    print("\n(c) main effects on the shared roads (points; seed mean, seed-averaged block CI): S | T")
    for k in list(W)[:5]:
        s_, t_ = fac["contrasts, shared roads (accuracy)"]["S"][k], fac["contrasts, shared roads (accuracy)"]["T"][k]
        print(f"  {k:36s} S {100 * s_['seed mean']:+.2f} [{100 * s_['seed-averaged 95% CI (blocks)'][0]:+.2f}, "
              f"{100 * s_['seed-averaged 95% CI (blocks)'][1]:+.2f}] {s_['seeds > 0']}/21 | T {100 * t_['seed mean']:+.2f}"
              f" [{100 * t_['seed-averaged 95% CI (blocks)'][0]:+.2f}, {100 * t_['seed-averaged 95% CI (blocks)'][1]:+.2f}]",
              flush=True)

    # the optimal combo re-chosen with S numbers (the factorial's preregistered rule, blocks resampled)
    choice = {}
    for sch in ("S", "T"):
        mean_acc = acc_sh[sch].mean(axis=0)
        top = names[int(np.argmax(mean_acc))]
        vs_top = {}
        for i, n in enumerate(names):
            if n == top:
                continue
            m, ci = seed_avg_ci(corr[sch][:, names.index(top), shared], corr[sch][:, i, shared], bt_sh_avg)
            vs_top[n] = {"tools": tools[n], "mean accuracy": float(mean_acc[i]), "top minus arm": m, "95% CI": ci,
                         "interval includes 0": bool(ci[0] <= 0 <= ci[1]), "simpler than top": tools[n] < tools[top]}
        ties = [n for n, r in vs_top.items() if r["simpler than top"] and r["interval includes 0"]]
        chosen = sorted([top] + ties, key=lambda n: (tools[n], -mean_acc[names.index(n)]))[0]
        choice[sch] = {"top arm": top, "top mean accuracy": float(mean_acc[names.index(top)]),
                       "ties (simpler, seed-averaged block CI includes 0)": ties, "chosen": chosen,
                       "chosen mean accuracy": float(mean_acc[names.index(chosen)]), "chosen tools": tools[chosen],
                       "every arm against the top arm (seed-averaged, blocks)": vs_top}
        print(f"\n(c) optimal combo under {sch}: top {top} ({100 * mean_acc[names.index(top)]:.2f}); ties {ties}; "
              f"chosen {chosen}", flush=True)
    fac["optimal combo (preregistered rule, block-resampled seed-averaged intervals)"] = choice
    numbers["(c) pipeline factorial"] = fac

    # ============ (d) the four thin-cloud groups under S ===========================================================
    on_tiles = np.isin(S.tile, S.haze_tiles)
    GROUPS = {"trusted flooded roads under thin cloud": (hazy & (y == 1), "found"),
              "dry-labelled roads under thin cloud (labels untrusted)": (hazy & (y == 0), "called flooded"),
              "control: assessable roads on the same tiles": (on_tiles & ka, "right"),
              "clear-sky benchmark: assessable flooded roads on the same tiles": (on_tiles & ka & (y == 1), "found")}
    assert [int(m.sum()) for m, _ in GROUPS.values()] == [24, 69, 175, 95]
    fold662 = np.full(len(y), -1)
    for k, (_, te) in enumerate(spatial_folds(S.R, SEED)):
        fold662[te] = k
    tfold662 = np.full(len(y), -1)
    for k, (_, te) in enumerate(tile_folds(S.R, SEED)):
        tfold662[te] = k
    fold_by_seed = {}
    for s in SEEDS:
        f = np.full(len(y), -1)
        for k, (_, te) in enumerate(spatial_folds(S.R, s)):
            f[te] = k
        fold_by_seed[s] = f
    assert (fold_by_seed[SEED] == fold662).all()

    def measure(c, msk, how):
        return (c[..., msk] == 1) if how in ("found", "called flooded") else (c[..., msk] == y[msk])

    rng = np.random.default_rng(SEED)
    groups_out = {}
    for gname, (msk, how) in GROUPS.items():
        bt = Boot(G["block"], msk, N_GROUP, rng)
        res = {}
        for i, n in enumerate(names):
            v = measure(Cc(n, "S", SEED), msk, how).astype(float)
            dist = bt.mean(v)
            per_seed_S = measure(calls_seed["S"][:, i], msk, how).mean(axis=1)
            per_seed_T = measure(calls_seed["T"][:, i], msk, how).mean(axis=1)
            res[n] = {"count": int(v.sum()), "share": float(v.mean()), "95% CI (blocks)":
                      [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))],
                      "seed mean share": float(per_seed_S.mean()), "seed min share": float(per_seed_S.min()),
                      "seed max share": float(per_seed_S.max()), "kept by its gate": int(S.gates[n[0]][msk].sum()),
                      "per S fold at seed 662 (count of the measure)":
                          [int(v[fold662[msk] == k].sum()) for k in range(5)],
                      "T share seed 662": float(per_seed_T[P]), "T seed mean share": float(per_seed_T.mean())}
        groups_out[gname] = {"roads": int(msk.sum()), "tiles": int(len(set(S.tile[msk]))),
                             "blocks": int(len(set(S.block[msk]))), "measure": how,
                             "roads per S fold at seed 662": [int((fold662[msk] == k).sum()) for k in range(5)],
                             "roads per T fold at seed 662": [int((tfold662[msk] == k).sum()) for k in range(5)],
                             "roads per S fold, every seed": {
                                 str(s): [int((fold_by_seed[s][msk] == k).sum()) for k in range(5)] for s in SEEDS},
                             "arms": res}
        val = groups_out[gname]["arms"]
        print(f"\n(d) {gname}: {int(msk.sum())} roads ({how}); per S fold {groups_out[gname]['roads per S fold at seed 662']}")
        for n in names:
            r = val[n]
            print(f"  {n:12s} {r['count']:3d} {100 * r['share']:5.1f}% [{100 * r['95% CI (blocks)'][0]:.1f}, "
                  f"{100 * r['95% CI (blocks)'][1]:.1f}]  S seed mean {100 * r['seed mean share']:5.1f}%  "
                  f"(T {100 * r['T seed mean share']:5.1f}%)  per fold {r['per S fold at seed 662 (count of the measure)']}",
                  flush=True)
    numbers["(d) thin-cloud groups under S"] = groups_out
    group_con = {}
    for gname, (msk, how) in GROUPS.items():
        v = (calls_seed["S"] == 1) if how in ("found", "called flooded") else corr["S"]
        group_con[gname] = contrast_table(v.astype(float), msk)
    numbers["(d) thin-cloud groups under S"]["contrasts under S (blocks)"] = group_con

    # ============ (e) nested spatial CV ================================================================================
    nested, nmeta = load_npz(NESTED_CALLS)
    if nmeta and all(f"nested__{s}" in nested for s in SEEDS):
        picks = pd.read_csv(HERE / "spatial_cv_nested_picks.csv")
        NC = np.stack([nested[f"nested__{s}"] for s in SEEDS])
        e = {"picks per outer fold and seed": picks[["seed", "outer fold", "picked", "picked tools",
                                                      "picked inner accuracy", "top arm", "top inner accuracy",
                                                      "tied arms"]].to_dict("records"),
             "pick counts (of 105 outer folds)": picks.picked.value_counts().to_dict()}
        best_single = choice["S"]["top arm"]
        chosen_S = choice["S"]["chosen"]
        for label, msk in (("757 shared", shared), ("798 production kept", ka)):
            okN = NC[:, msk] == y[msk]
            okP = calls_seed["S"][:, 0][:, msk] == y[msk]
            okB = calls_seed["S"][:, names.index(best_single)][:, msk] == y[msk]
            okC = calls_seed["S"][:, names.index(chosen_S)][:, msk] == y[msk]
            bt_avg = boot("block", G["block"], msk, N_BOOT)
            btp = boot("block", G["block"], msk, N_PAIR)
            per = [paired(NC[k], calls_seed["S"][k, 0], y, msk, btp) for k in range(len(SEEDS))]
            m_p, ci_p = seed_avg_ci(okN, okP, bt_avg)
            m_b, ci_b = seed_avg_ci(okN, okB, bt_avg)
            m_c, ci_c = seed_avg_ci(okN, okC, bt_avg)
            e[label] = {"nested accuracy, seed 662": score(NC[P], y, msk, boot("block", G["block"], msk, N_BOOT)),
                        "nested accuracy over seeds": seed_stats(okN.mean(1), okP.mean(1)),
                        "production S accuracy over seeds": seed_stats(okP.mean(1)),
                        "nested vs production, seed 662 (paired, blocks)": per[P],
                        "nested vs production, seed-averaged": m_p, "nested vs production, seed-averaged 95% CI": ci_p,
                        "nested vs production: seeds the rule would pass": int(sum(
                            p_["would pass (sn8_stages.confirm)"] for p_ in per)),
                        "best single S arm (by S mean, shared)": best_single,
                        "selection optimism: nested - best single arm, per seed mean": float(
                            (okN.mean(1) - okB.mean(1)).mean()),
                        "selection optimism: seed-averaged 95% CI": ci_b,
                        "selection optimism, seed 662": float(okN[P].mean() - okB[P].mean()),
                        "nested - re-chosen optimal combo (S), seed-averaged": m_c,
                        "nested - re-chosen optimal combo (S), 95% CI": ci_c}
            for k, s in enumerate(SEEDS):
                seed_rows.append({"section": "(e)", "arm": "nested pick", "scheme": "S nested", "road set": label,
                                  "seed": s, "accuracy": float(okN[k].mean()), "production accuracy":
                                      float(okP[k].mean()), "gain vs production": per[k]["gain"],
                                  "95% CI": per[k]["95% CI"], "fixed": per[k]["fixed"], "broken": per[k]["broken"],
                                  "McNemar p": per[k]["McNemar p"],
                                  "would pass": per[k]["would pass (sn8_stages.confirm)"]})
            print(f"\n(e) nested on the {label}: seed 662 {100 * okN[P].mean():.2f}; mean {100 * okN.mean():.2f} "
                  f"(SD {100 * okN.mean(1).std(ddof=1):.2f}); production S mean {100 * okP.mean():.2f}; vs production "
                  f"{100 * m_p:+.2f} [{100 * ci_p[0]:+.2f}, {100 * ci_p[1]:+.2f}]; minus best single ({best_single}) "
                  f"{100 * m_b:+.2f} [{100 * ci_b[0]:+.2f}, {100 * ci_b[1]:+.2f}]", flush=True)
        print("(e) picks:", e["pick counts (of 105 outer folds)"], flush=True)
        numbers["(e) nested spatial CV"] = e
    else:
        NC = None
        numbers["(e) nested spatial CV"] = {"status": "not run yet"}

    # ============ residual dependence (production under S, seed 662) =============================================
    def errors_corr(call, msk):
        r = pd.DataFrame({"tile_id": S.tile[msk], "road_id": S.R.road_id.to_numpy()[msk],
                          "flooded": (call[msk] != y[msk])})
        return _correlogram(r)

    lab = pd.DataFrame({"tile_id": S.tile[ka], "road_id": S.R.road_id.to_numpy()[ka], "flooded": y[ka].astype(bool)})
    resid = {"what": "Moran-type correlation of held-out errors (1 = wrong) between production's 798 roads on different "
                     "tiles with different road ids, by tile-centroid distance band (the label correlogram's bands)",
             "production errors under S, seed 662": errors_corr(A("A", "S", SEED), ka),
             "production errors under T, seed 662 (comparison)": errors_corr(A("A", "T", SEED), ka),
             "production errors under L, seed 662 (comparison)": errors_corr(A("A", "L", SEED), ka),
             "labels on the 798 (reference)": _correlogram(lab),
             "error rate under S, seed 662": float((A("A", "S", SEED)[ka] != y[ka]).mean())}
    print("\nresidual correlogram (production, S, seed 662):",
          [(c["band_km"], round(c["correlation"], 3)) for c in resid["production errors under S, seed 662"]])
    print("residual correlogram (production, T, seed 662):",
          [(c["band_km"], round(c["correlation"], 3)) for c in resid["production errors under T, seed 662 (comparison)"]])
    numbers["residual dependence check"] = resid

    # ============ (f) Track A ====================================================================================
    numbers["(f) Track A road finding"] = trackA()

    # ============ decision-rule verdicts ===========================================================================
    verdicts = []
    pS = fac["paired against production"]["S"]["shared roads"]
    for n in names[1:]:
        r = pS[n]
        a = fac["arms"][n]
        counts_ = r["would pass (sn8_stages.confirm)"] and a["S seed-averaged gain excludes 0"] and \
            a["S gain vs production, seed-averaged 95% CI (blocks)"][0] > 0
        verdicts.append({"candidate": n, "set": "757 shared", "S seed 662 gain": r["gain"], "95% CI": r["95% CI"],
                         "McNemar p": r["McNemar p"], "rule at seed 662": r["would pass (sn8_stages.confirm)"],
                         "seed-averaged gain": a["S gain vs production, seed-averaged"],
                         "seed-averaged 95% CI": a["S gain vs production, seed-averaged 95% CI (blocks)"],
                         "rule passes over 21 seeds": a["S rule passes (of 21 seeds, shared, blocks)"],
                         "gain counts (rule at 662 and seed-averaged CI above 0)": bool(counts_)})
    vb = ab["B"]["against production on the 798 (same roads, same scheme)"]["S"]
    verdicts.append({"candidate": "(b) best combo on the 891, scored on the 798", "set": "798",
                     "S seed 662 gain": vb["seed 662"]["gain"], "95% CI": vb["seed 662"]["95% CI"],
                     "McNemar p": vb["seed 662"]["McNemar p"],
                     "rule at seed 662": vb["seed 662"]["would pass (sn8_stages.confirm)"],
                     "seed-averaged gain": vb["seed-averaged gain"],
                     "seed-averaged 95% CI": vb["seed-averaged gain 95% CI (blocks)"],
                     "rule passes over 21 seeds": vb["seeds the rule would pass"],
                     "gain counts (rule at 662 and seed-averaged CI above 0)": bool(
                         vb["seed 662"]["would pass (sn8_stages.confirm)"] and
                         vb["seed-averaged gain 95% CI (blocks)"][0] > 0)})
    if NC is not None:
        for label in ("757 shared", "798 production kept"):
            en = numbers["(e) nested spatial CV"][label]
            r = en["nested vs production, seed 662 (paired, blocks)"]
            verdicts.append({"candidate": "(e) nested pick", "set": label, "S seed 662 gain": r["gain"],
                             "95% CI": r["95% CI"], "McNemar p": r["McNemar p"],
                             "rule at seed 662": r["would pass (sn8_stages.confirm)"],
                             "seed-averaged gain": en["nested vs production, seed-averaged"],
                             "seed-averaged 95% CI": en["nested vs production, seed-averaged 95% CI"],
                             "rule passes over 21 seeds": en["nested vs production: seeds the rule would pass"],
                             "gain counts (rule at 662 and seed-averaged CI above 0)": bool(
                                 r["would pass (sn8_stages.confirm)"] and
                                 en["nested vs production, seed-averaged 95% CI"][0] > 0)})
    numbers["decision-rule verdicts (promotion rule on S only; read-only)"] = verdicts
    print("\nverdicts (S):")
    for v in verdicts:
        print(f"  {v['candidate']:46s} {v['set']:20s} 662 {100 * v['S seed 662 gain']:+.2f} "
              f"[{100 * v['95% CI'][0]:+.2f}, {100 * v['95% CI'][1]:+.2f}] p={v['McNemar p']:.4f} rule {v['rule at seed 662']}"
              f"; seed-avg {100 * v['seed-averaged gain']:+.2f} [{100 * v['seed-averaged 95% CI'][0]:+.2f}, "
              f"{100 * v['seed-averaged 95% CI'][1]:+.2f}]; passes {v['rule passes over 21 seeds']}/21; counts "
              f"{v['gain counts (rule at 662 and seed-averaged CI above 0)']}", flush=True)

    # ============ save ==========================================================================================
    ft = fold_table(SEED)
    table = pd.DataFrame({"tile_id": S.tile, "road_id": S.R.road_id, "split": S.split, "flooded": y,
                          "kept by production gate (a)": ka, "kept by spotter gate (b)": kb, "shared": shared,
                          "tile rule (891)": rule891, "thin cloud (production road rule)": hazy, "block (3 x 3)": S.block,
                          "block (7 x 7)": S.block7, "S fold, seed 662": fold662 + 1, "T fold, seed 662": tfold662 + 1})
    for arm, msk, lab_ in (("A", ka, "(a) production"), ("B", rule891, "(b) best combo")):
        for scheme in SCHEMES_AB:
            table[f"{lab_} · {scheme} · call seed 662"] = A(arm, scheme, SEED)
    for sch in ("S", "SB", "T"):
        for n in names:
            table[f"(c) {n} · {sch} · call seed 662"] = Cc(n, sch, SEED)
    for n in names:
        table[f"(c) {n} · S · flooded-call share over 21 seeds"] = calls_seed["S"][:, names.index(n)].mean(0).round(4)
    if NC is not None:
        table["(e) nested pick · S · call seed 662"] = NC[P]
        table["(e) nested pick · S · right share over 21 seeds"] = (NC == y).mean(0).round(4)
    table.to_csv(HERE / "spatial_cv_calls.csv", index=False)
    pd.DataFrame(seed_rows).to_csv(HERE / "spatial_cv_seeds.csv", index=False)
    numbers["run time s"] = round(time.time() - t0)
    json.dump(plain(numbers), open(HERE / "spatial_cv_numbers.json", "w"), indent=1)
    print(f"\nsaved spatial_cv_numbers.json, spatial_cv_calls.csv ({table.shape[1]} columns), spatial_cv_seeds.csv "
          f"({len(seed_rows)} rows)", f"{round(time.time() - t0)} s", flush=True)


def trackA():
    """Track A from spatial_cv_trackA_probs.npz: whatever has been fitted."""
    path = HERE / "spatial_cv_trackA_probs.npz"
    if not path.exists():
        return {"status": "not run"}
    from spatial_cv_trackA import load_cells, tile_folds_cells
    from spatial_folds import cell_folds, fold_table
    z = np.load(path, allow_pickle=False)
    arrays = {k: z[k] for k in z.files if k != "meta"}
    meta = json.loads(str(z["meta"]))
    cells, cols, cut, det, n_train = load_cells()
    y = cells.label.to_numpy().astype(int)
    ids = cells.tile_id.to_numpy()
    is_val = (cells.src == "val").to_numpy()
    real = meta["real"]
    sampled = float(y.mean())
    w = np.where(y == 1, 1.0, (1 - real) / real * sampled / (1 - sampled))
    ft = fold_table(SEED)
    blk = pd.Series(ids).map(dict(zip(ft.tile_id, ft.block))).to_numpy()
    assert not pd.isna(blk).any()
    unit = {"S": blk, "T": ids, "nested": blk}
    out = {"detector": det, "columns": len(cols), "cut-off": cut, "real road share (road_prior('train'))": real,
           "pooled cells": len(cells), "train-split cells": n_train, "val-split cells": int(is_val.sum()),
           "road share: train-split / val-split / pooled": [float(y[~is_val].mean()), float(y[is_val].mean()), sampled],
           "secondary weights": "road 1; not-road (1 - real) / real x sampled / (1 - sampled), sampled = pooled road share",
           "fit seconds": meta.get("fit seconds", {}), "log": meta.get("log", []),
           "DINOv2 cell basis": "kept as cached (fitted on the training tiles' patch tokens, label-free); tokens are not "
                                "cached, so a per-fold refit would need the GPU"}
    if "repro_val" in arrays:
        p = arrays["repro_val"]
        c = p >= cut
        yv = y[is_val]
        tp, fp, fn = int(((yv == 1) & c).sum()), int(((yv == 0) & c).sum()), int(((yv == 1) & ~c).sum())
        out["reproduction (train-split cells -> val-split cells, as logged)"] = {
            "cells called road": int(c.sum()), "precision": tp / (tp + fp), "recall": tp / (tp + fn),
            "F1": 2 * tp / (2 * tp + fp + fn), "logged": "7,580 called, precision 0.696, recall 0.732, F1 0.713"}

    def prob(scheme, s):
        folds = cell_folds(ids, s) if scheme == "S" else tile_folds_cells(cells, s)
        if not all(f"{scheme}__{s}__{k}" in arrays for k in range(5)):
            return None, folds
        pr = np.full(len(cells), np.nan, np.float64)
        for k, (_, te) in enumerate(folds):
            pr[te] = arrays[f"{scheme}__{s}__{k}"]
        assert not np.isnan(pr).any()
        return pr, folds

    def f1_stats(called, msk, groups, weights=None, n=N_BOOT):
        wt = np.ones(len(y)) if weights is None else weights
        tp_i = ((y == 1) & called) * wt
        fp_i = ((y == 0) & called) * wt
        fn_i = ((y == 1) & ~called) * wt
        bt = Boot(groups, msk, n)
        TP, FP, FN = (bt.sums(v[msk]) for v in (tp_i, fp_i, fn_i))
        f1d = 2 * TP / (2 * TP + FP + FN)
        tp, fp, fn = tp_i[msk].sum(), fp_i[msk].sum(), fn_i[msk].sum()
        return {"F1": float(2 * tp / (2 * tp + fp + fn)), "F1 95% CI": [float(np.percentile(f1d, 2.5)),
                                                                        float(np.percentile(f1d, 97.5))],
                "precision": float(tp / (tp + fp)), "recall": float(tp / (tp + fn)),
                "cells called road": int(called[msk].sum()), "cells": int(msk.sum())}, f1d

    res = {}
    for s in [x for x in SEEDS if any(k.startswith(f"S__{x}__") for k in arrays)]:
        res[str(s)] = {}
        for scheme in ("S", "T"):
            pr, folds = prob(scheme, s)
            if pr is None:
                res[str(s)][scheme] = "not run (compute)"
                continue
            called = pr >= cut
            prim, d_prim = f1_stats(called, is_val, unit[scheme])
            sec, d_sec = f1_stats(called, np.ones(len(y), bool), unit[scheme], w)
            fold = np.empty(len(y), int)
            for k, (_, te) in enumerate(folds):
                fold[te] = k
            per_fold = []
            for k in range(5):
                m = is_val & (fold == k)
                tp, fp, fn = (int(v.sum()) for v in (((y == 1) & called)[m], ((y == 0) & called)[m],
                                                    ((y == 1) & ~called)[m]))
                per_fold.append({"fold": k + 1, "val-split cells": int(m.sum()),
                                 "F1": 2 * tp / (2 * tp + fp + fn) if tp else 0.0,
                                 "held-out cells (all)": int((fold == k).sum())})
            res[str(s)][scheme] = {"primary: F1 on held-out val-split cells": prim,
                                   "secondary: weighted F1, all held-out cells": sec, "per fold": per_fold}
        if isinstance(res[str(s)].get("S"), dict) and isinstance(res[str(s)].get("T"), dict):
            prS, _ = prob("S", s)
            prT, _ = prob("T", s)
            for lab, msk, wt in (("primary (val-split cells)", is_val, None), ("secondary (weighted, all)",
                                                                                 np.ones(len(y), bool), w)):
                _, dT = f1_stats(prT >= cut, msk, blk, wt)
                _, dS = f1_stats(prS >= cut, msk, blk, wt)
                fT = res[str(s)]["T"]["primary: F1 on held-out val-split cells" if wt is None else
                                      "secondary: weighted F1, all held-out cells"]["F1"]
                fS = res[str(s)]["S"]["primary: F1 on held-out val-split cells" if wt is None else
                                      "secondary: weighted F1, all held-out cells"]["F1"]
                res[str(s)][f"T - S F1 gap, {lab}"] = {"gap": fT - fS, "95% CI (blocks, paired)": [
                    float(np.percentile(dT - dS, 2.5)), float(np.percentile(dT - dS, 97.5))]}
    out["fixed cut-off 0.75, by seed"] = res
    if "nested cut-offs" in meta and len(meta["nested cut-offs"]) == 5:
        prS, folds = prob("S", SEED)
        called = np.zeros(len(y), bool)
        cuts = [meta["nested cut-offs"][str(k)] for k in range(5)]
        for k, (_, te) in enumerate(folds):
            called[te] = prS[te] >= cuts[k]
        prim, d1 = f1_stats(called, is_val, blk)
        sec, _ = f1_stats(called, np.ones(len(y), bool), blk, w)
        _, d0 = f1_stats(prS >= cut, is_val, blk)
        out["nested cut-off, seed 662"] = {"cut-off per outer fold": cuts, "primary: F1 on held-out val-split cells":
                                           prim, "secondary: weighted F1, all held-out cells": sec,
                                           "nested minus fixed 0.75 (primary), 95% CI (blocks)": [
                                               float(np.percentile(d1 - d0, 2.5)), float(np.percentile(d1 - d0, 97.5))],
                                           "inner F1 curves (cut-offs 0.05-0.99)": meta.get("nested curves")}
    else:
        out["nested cut-off, seed 662"] = "not run (compute)" if any("not run" in x for x in meta.get("log", [])) \
            else "not run yet"
    return out


if __name__ == "__main__":
    h0 = registry_hash()
    main()
    assert registry_hash() == h0
