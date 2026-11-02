"""Scoring (a): detection arms on HRC_WHU (no fitting of the spotter here; reads run_hrc.py's outputs) and arm D4
(calibration, cross-fitted on the out-of-fold probabilities). Writes hrc_numbers.json and prints tables.
    nice -n 10 python3 -I hrc_score.py > hrc_score.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

T0 = time.time()
N_BINS = 15
CAL_SAMPLE = 300_000


def ece_parts(p, y, n_bins=N_BINS):
    """Per-bin (count, sum of confidence, sum of outcome) for the probability of cloud (equal-width bins)."""
    b = np.clip((p * n_bins).astype(int), 0, n_bins - 1)
    return (np.bincount(b, minlength=n_bins), np.bincount(b, weights=p, minlength=n_bins),
            np.bincount(b, weights=y.astype(float), minlength=n_bins))


def ece_from(parts):
    n, sc, sy = parts
    tot = n.sum(-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.nansum(np.abs(sy - sc) / np.maximum(tot, 1), -1)


def platt_fit(p, y):
    from sklearn.linear_model import LogisticRegression
    z = np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))[:, None]
    m = LogisticRegression(C=1e6, max_iter=1000).fit(z, y)
    return lambda q: m.predict_proba(np.log(np.clip(q, 1e-4, 1 - 1e-4) / (1 - np.clip(q, 1e-4, 1 - 1e-4)))[:, None])[:, 1]


def iso_fit(p, y):
    from sklearn.isotonic import IsotonicRegression
    m = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(p, y)
    return lambda q: m.predict(q)


def risk_cut(p, y, budget, grid=np.linspace(0.01, 0.99, 99)):
    """Largest cut c with risk(p < c) = share of cloud among accepted pixels <= budget."""
    best = None
    for c in grid:
        acc = p < c
        if acc.sum() == 0:
            continue
        if y[acc].mean() <= budget:
            best = c
    return best


def main():
    from sn8_cloudspot import paired_f1, pooled_table, resamples
    from scipy.stats import binomtest
    counts = pd.read_csv(C.HERE / "hrc_counts.csv")
    z = np.load(C.BIG / "hrc_proba.npz")
    names = sorted({k.split("|", 1)[1] for k in z.files if k.startswith("y|")},
                   key=lambda n: (n.split("_")[0], int(n.split("_")[1])))
    types = np.array([n.split("_")[0] for n in names])
    num = {}
    # pooled table and paired vs D0
    pt = pooled_table(counts, by=("arm", "learner"))
    print(pt.to_string(index=False))
    num["pooled"] = pt.to_dict("records")
    pairs = []
    for arm, lr in counts[["arm", "learner"]].drop_duplicates().itertuples(index=False):
        if arm == "D0":
            continue
        for scope, tps in (("all", None), ("water", ["water"])):
            r = paired_f1(counts, arm, "D0", lr, "random forest", types=tps)
            # pixel McNemar on the grid pixels (pixels are not independent: reported only)
            fx = bk = 0
            for n in names:
                if tps and n.split("_")[0] not in tps:
                    continue
                y = z[f"y|{n}"].astype(bool)
                pa = z[f"{arm}|{n}"].astype(np.float32) >= (60 / 255 if arm.startswith("D2") else 0.5)
                pb = z[f"D0|{n}"].astype(np.float32) >= 0.5
                fx += int(((pa == y) & (pb != y)).sum()); bk += int(((pa != y) & (pb == y)).sum())
            r.update(scope=scope, pixel_fixed=fx, pixel_broken=bk,
                     pixel_mcnemar_p=float(binomtest(fx, fx + bk, 0.5).pvalue) if fx + bk else 1.0)
            pairs.append(r)
    pr = pd.DataFrame(pairs)
    print(pr[["a", "scope", "F1 a - b", "95% CI", "images a higher", "images b higher", "sign test p",
              "pixel_fixed", "pixel_broken", "pixel_mcnemar_p"]].to_string(index=False))
    num["paired_vs_D0"] = pr.to_dict("records")
    # ------------------------------------------------------------------ D4 calibration (cross-fitted by fold)
    fold = {n: int(z[f"fold|{n}"][0]) for n in names}
    idx = resamples(types, 2000)                 # image resamples within land cover (sn8_cloudspot's)
    cal_out = {}
    d1_best = None
    pr_all = pr[pr.scope == "all"]
    d1 = pr_all[pr_all.a.str.startswith("D1")].sort_values("F1 a - b", ascending=False)
    if len(d1) and d1.iloc[0]["ci_low"] > 0:
        d1_best = d1.iloc[0]["a"]
    bases = ["D0"] + ([d1_best] if d1_best else [])
    rng = np.random.default_rng(C.SEED)
    for base in bases:
        per_img = {m: [] for m in ("raw", "isotonic", "Platt")}
        rc = {m: {"coverage": [], "risk": []} for m in ("raw@0.5", "isotonic@p*", "Platt@p*")}
        cuts = {"isotonic": [], "Platt": []}
        f1_05 = {m: np.zeros(3) for m in ("isotonic", "Platt")}
        rel = {m: [np.zeros(N_BINS), np.zeros(N_BINS), np.zeros(N_BINS)] for m in ("raw", "isotonic", "Platt")}
        brier = {m: [0.0, 0] for m in ("raw", "isotonic", "Platt")}
        nll = {m: [0.0, 0] for m in ("raw", "isotonic", "Platt")}
        imgs_cal = {}
        for k in range(5):
            tr = [n for n in names if fold[n] != k]
            te = [n for n in names if fold[n] == k]
            ptr = np.concatenate([z[f"{base}|{n}"].astype(np.float32) for n in tr])
            ytr = np.concatenate([z[f"y|{n}"] for n in tr]).astype(int)
            s = rng.choice(len(ptr), min(CAL_SAMPLE, len(ptr)), replace=False)
            fits = {"isotonic": iso_fit(ptr[s], ytr[s]), "Platt": platt_fit(ptr[s], ytr[s])}
            budget = ytr[ptr < 0.5].mean()                 # D0's (raw) risk at its 0.5 cut on the calibration folds
            pstar = {m: risk_cut(f(ptr[s]), ytr[s], budget) for m, f in fits.items()}
            for m in pstar:
                cuts[m].append(pstar[m])
            for n in te:
                p = z[f"{base}|{n}"].astype(np.float32)
                y = z[f"y|{n}"].astype(bool)
                cal = {"raw": p, **{m: f(p) for m, f in fits.items()}}
                imgs_cal[n] = cal
                for m, q in cal.items():
                    per_img[m].append(ece_parts(q, y))
                    pp = ece_parts(q, y)
                    for j in range(3):
                        rel[m][j] += pp[j]
                    brier[m][0] += float(((q - y) ** 2).sum()); brier[m][1] += len(y)
                    qq = np.clip(q, 1e-6, 1 - 1e-6)
                    nll[m][0] += float(-(y * np.log(qq) + (~y) * np.log(1 - qq)).sum()); nll[m][1] += len(y)
                for m in ("isotonic", "Platt"):
                    pr_ = cal[m] >= 0.5
                    f1_05[m] += [(pr_ & y).sum(), (pr_ & ~y).sum(), (~pr_ & y).sum()]
                for m, q, c in (("raw@0.5", p, 0.5), ("isotonic@p*", cal["isotonic"], pstar["isotonic"]),
                                ("Platt@p*", cal["Platt"], pstar["Platt"])):
                    acc = q < (c if c is not None else 0.0)
                    rc[m]["coverage"].append((acc.sum(), len(y)))
                    rc[m]["risk"].append(((acc & y).sum(), acc.sum()))
        order = names
        res = {}
        parts = {m: [None] * len(names) for m in per_img}
        for m in per_img:
            # per_img was appended in fold order; rebuild per image in `names` order
            pass
        # per-image bin parts in names order for resampling
        P = {m: np.stack([np.stack(ece_parts(imgs_cal[n][m], z[f"y|{n}"].astype(bool))) for n in order])
             for m in ("raw", "isotonic", "Platt")}            # (images, 3, bins)
        for m in P:
            pooled = P[m].sum(0)
            e = float(ece_from(tuple(pooled)))
            boot = ece_from(tuple(np.moveaxis(P[m][idx].sum(1), 1, 0)))
            res[m] = {"ECE": e, "ECE 95% CI": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                      "Brier": brier[m][0] / brier[m][1], "NLL per pixel": nll[m][0] / nll[m][1],
                      "reliability": {"count": rel[m][0].tolist(), "mean_conf": (rel[m][1] / np.maximum(rel[m][0], 1)).tolist(),
                                      "frac_cloud": (rel[m][2] / np.maximum(rel[m][0], 1)).tolist()}}
            if m != "raw":
                d = ece_from(tuple(np.moveaxis(P[m][idx].sum(1), 1, 0))) - ece_from(tuple(np.moveaxis(P["raw"][idx].sum(1), 1, 0)))
                res[m]["ECE minus raw"] = e - res["raw"]["ECE"]
                res[m]["ECE minus raw 95% CI"] = [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
                tp, fp, fn = f1_05[m]
                res[m]["F1 at 0.5"] = float(2 * tp / (2 * tp + fp + fn))
                res[m]["p* per fold"] = cuts[m]
        for m, v in rc.items():
            cov = np.array(v["coverage"]); rk = np.array(v["risk"])
            res[f"risk-coverage {m}"] = {"coverage": float(cov[:, 0].sum() / cov[:, 1].sum()),
                                         "risk": float(rk[:, 0].sum() / max(rk[:, 1].sum(), 1))}
        cal_out[base] = res
        print(f"\nD4 calibration of {base}:")
        for m in ("raw", "isotonic", "Platt"):
            r = res[m]
            print(f"  {m:9s} ECE {r['ECE']:.4f} [{r['ECE 95% CI'][0]:.4f}, {r['ECE 95% CI'][1]:.4f}]  Brier {r['Brier']:.4f}"
                  f"  NLL {r['NLL per pixel']:.4f}" + (f"  ECE-raw {r['ECE minus raw']:+.4f} [{r['ECE minus raw 95% CI'][0]:+.4f},"
                                                         f" {r['ECE minus raw 95% CI'][1]:+.4f}]  F1@0.5 {r['F1 at 0.5']:.4f}"
                                                         f"  p* {r['p* per fold']}" if m != 'raw' else ""))
        for m in rc:
            print(f"  {m:12s} coverage {res[f'risk-coverage {m}']['coverage']:.4f}  risk {res[f'risk-coverage {m}']['risk']:.4f}")
    num["D4"] = cal_out
    num["D1_best_for_D4"] = d1_best
    C.write_json(C.HERE / "hrc_numbers.json", num)
    C.log(T0, "done")


if __name__ == "__main__":
    main()
