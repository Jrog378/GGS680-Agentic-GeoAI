"""Step 7: statistics for every outcome. Unit: the tile (per-tile means, paired across arms). 95% intervals: 2,000
bootstrap resamples of the 3 x 3 tile blocks of evidence 14 (spatial_folds.fold_table(662).block); Wilcoxon
signed-rank over tiles as the check; Holm across the three arm comparisons of outcomes 1-2 (two-date - as is,
two-date - He 2011, He 2011 - as is). Writes s5_numbers.json and prints every table.
    python3 -I s5_stats.py > s5_stats.log 2>&1
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

N_BOOT = 2000
MIN_PX = 1000                     # a tile enters a region's comparison with at least this many pixels there (5 patches)
OUT = C.BIG / "score"
NUM = {}


def blocks():
    from spatial_folds import fold_table
    ft = fold_table(C.SEED)
    return dict(zip(ft.tile_id, ft.block))


BLOCK = None


def boot_idx(tiles, rng):
    """Index arrays of tiles for each resample of the blocks."""
    b = np.array([BLOCK[t] for t in tiles])
    ub = np.unique(b)
    members = {k: np.flatnonzero(b == k) for k in ub}
    for _ in range(N_BOOT):
        pick = rng.choice(ub, len(ub), replace=True)
        yield np.concatenate([members[k] for k in pick])


def ci_mean(values, tiles, seed=C.SEED):
    v = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    bs = [v[i].mean() for i in boot_idx(list(tiles), rng)]
    return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def wil(v):
    v = np.asarray(v, float)
    v = v[v != 0]
    return float(wilcoxon(v).pvalue) if len(v) >= 5 else float("nan")


def holm(ps):
    order = np.argsort(ps)
    m = len(ps)
    adj = np.empty(m)
    run = 0
    for r, i in enumerate(order):
        run = max(run, min(1, (m - r) * ps[i]))
        adj[i] = run
    return adj.tolist()


def fmt(m, lo, hi, d=4):
    return f"{m:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]"


def load_rows(kind):
    fs = sorted(OUT.glob(f"*_{kind}.npz"))
    rows = [pd.DataFrame(list(np.load(f, allow_pickle=True)["rows"])) for f in fs]
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def paired(df, region, subset, metric, a, b, min_px=MIN_PX):
    d = df[(df.region == region) & (df.subset == subset) & (df.px >= min_px)]
    w = d.pivot_table(index="tile_id", columns="arm", values=metric)
    w = w.dropna(subset=[a, b])
    diff = (w[a] - w[b]).to_numpy()
    if len(diff) < 3:
        return {"n_tiles": len(diff)}
    m, lo, hi = ci_mean(diff, w.index)
    return {"n_tiles": int(len(diff)), "mean_a": float(w[a].mean()), "mean_b": float(w[b].mean()), "diff": m, "lo": lo,
            "hi": hi, "wilcoxon_p": wil(diff), "a_better_tiles": int((diff < 0).sum()) if metric in ("feat", "grey_err")
            else int((diff > 0).sum())}


def auc(score, label):
    from sklearn.metrics import roc_auc_score
    if label.all() or (~label).all():
        return float("nan")
    return float(roc_auc_score(label, score))


def main():
    global BLOCK
    BLOCK = blocks()
    dino = load_rows("dino")
    pix = load_rows("pixel")
    prep = pd.read_csv(C.HERE / "s2_prep.csv")
    cov = pd.read_csv(C.HERE / "s1_coverage.csv")
    cl = set(C.cloudy_tiles())
    NUM["tiles"] = {"dev": 226, "kept_cover": int(cov.kept_cover.sum()), "cloudy_kept_cover": int((cov.kept_cover & cov.cloudy).sum()),
                    "aligned_ok": int(prep.coreg_ok.fillna(False).astype(bool).sum()),
                    "cloudy_aligned_ok": int(prep[prep.coreg_ok.fillna(False).astype(bool)].tile_id.isin(cl).sum()),
                    "dino_scored": int(dino.tile_id.nunique()) if len(dino) else 0,
                    "dino_scored_cloudy": int(dino.tile_id[dino.tile_id.isin(cl)].nunique()) if len(dino) else 0}
    print(json.dumps(NUM["tiles"]))

    # ---- outcomes 1-2 (feature distance, thin cloud), Holm over the three comparisons; road strips first
    comps = [("td", "asis"), ("td", "he"), ("he", "asis")]
    for subset in ("road", "all", "other", "building"):
        res = {f"{a}-{b}": paired(dino, "thin", subset, "feat", a, b) for a, b in comps}
        ps = [res[k].get("wilcoxon_p", np.nan) for k in res]
        if all(np.isfinite(ps)):
            for k, h in zip(res, holm(ps)):
                res[k]["holm_p"] = h
        res["tdspot-td"] = paired(dino, "thin", subset, "feat", "tdspot", "td")
        res["tdspot-asis"] = paired(dino, "thin", subset, "feat", "tdspot", "asis")
        NUM[f"o12_thin_{subset}"] = res
        print(f"\nOutcomes 1-2, thin cloud, {subset}: feature distance to NOAA")
        for k, r in res.items():
            if "diff" in r:
                print(f"  {k}: {fmt(r['diff'], r['lo'], r['hi'])}  tiles {r['n_tiles']}  means {r['mean_a']:.4f} vs "
                      f"{r['mean_b']:.4f}  Wilcoxon p {r['wilcoxon_p']:.3g}  Holm {r.get('holm_p', float('nan')):.3g}  "
                      f"first arm closer on {r['a_better_tiles']}")
            else:
                print(f"  {k}: too few tiles ({r['n_tiles']})")
    # opaque, reported
    for subset in ("road", "all"):
        res = {f"{a}-{b}": paired(dino, "opaque", subset, "feat", a, b) for a, b in comps}
        NUM[f"o12_opaque_{subset}"] = res
        print(f"\nOpaque (t < 0.2), {subset}:")
        for k, r in res.items():
            if "diff" in r:
                print(f"  {k}: {fmt(r['diff'], r['lo'], r['hi'])}  tiles {r['n_tiles']}  means {r['mean_a']:.4f} vs {r['mean_b']:.4f}")
    # absolute levels, before image as a reference point
    lv = dino[(dino.px >= MIN_PX)].groupby(["region", "subset", "arm"]).agg(feat=("feat", "mean"), tiles=("tile_id", "nunique"))
    print("\nMean feature distance to NOAA by region (tile means):\n" + lv.to_string())
    NUM["feat_levels"] = {"|".join(k): v for k, v in lv.feat.round(5).items()}

    # ---- outcome 3: guard
    print("\nOutcome 3 (guard, clear ground):")
    NUM["o3"] = {}
    for subset in ("road", "all"):
        for a in ("td", "he", "tdspot"):
            r = paired(dino, "guard", subset, "feat", a, "asis")
            g = pix[(pix.region == "guard") & (pix.subset == subset) & (pix.arm == a) & (pix.px >= MIN_PX)]
            gc = ci_mean(g.grey_change.to_numpy(), g.tile_id) if len(g) > 2 else (np.nan,) * 3
            r.update(grey_change=gc[0], grey_change_lo=gc[1], grey_change_hi=gc[2], grey_tiles=int(len(g)))
            if "diff" in r:
                r["pass_feat"] = bool(r["lo"] >= -0.01 and r["hi"] <= 0.01)
            r["pass_grey"] = bool(gc[0] < 1)
            NUM["o3"][f"{a}_{subset}"] = r
            if "diff" in r:
                print(f"  {a} - as is, {subset}: feat {fmt(r['diff'], r['lo'], r['hi'])} (tiles {r['n_tiles']}); grey change "
                      f"{gc[0]:.3f} [{gc[1]:.3f}, {gc[2]:.3f}] on {len(g)} tiles; pass feat {r.get('pass_feat')} grey {r['pass_grey']}")

    # ---- outcome 4: t vs recovered; discard curve
    o4 = {k: [] for k in ("t", "feat", "tile", "road", "cannot")}
    gfeat = []
    for f in sorted(OUT.glob("*_dino.npz")):
        z = np.load(f, allow_pickle=True)
        tid = f.name.replace("_dino.npz", "")
        if "o4_t" in z.files and len(z["o4_t"]):
            o4["t"].append(z["o4_t"]); o4["feat"].append(z["o4_feat_td"]); o4["road"].append(z["o4_road"])
            o4["cannot"].append(z["o4_cannot"]); o4["tile"].append(np.full(len(z["o4_t"]), tid))
        if "guard_feat_td" in z.files:
            gfeat.append(z["guard_feat_td"])
    if o4["t"]:
        T, Fd, Tl = (np.concatenate(o4[k]) for k in ("t", "feat", "tile"))
        thr = float(np.percentile(np.concatenate(gfeat), 95))
        rec = Fd < thr
        a0 = auc(T, rec)
        tiles = np.unique(Tl)
        idx = {t: np.flatnonzero(Tl == t) for t in tiles}
        rng = np.random.default_rng(C.SEED)
        bs = []
        for ii in boot_idx(list(tiles), rng):
            sel = np.concatenate([idx[tiles[i]] for i in ii])
            bs.append(auc(T[sel], rec[sel]))
        bs = np.array(bs)
        NUM["o4"] = {"guard_p95_feat": thr, "pixels_sampled": int(len(T)), "tiles": int(len(tiles)),
                     "recovered_share": float(rec.mean()), "auc_t": a0, "lo": float(np.nanpercentile(bs, 2.5)),
                     "hi": float(np.nanpercentile(bs, 97.5)),
                     "feat_td_t_ge_02": float(Fd[T >= 0.2].mean()) if (T >= 0.2).any() else None,
                     "feat_td_t_lt_02": float(Fd[T < 0.2].mean()) if (T < 0.2).any() else None,
                     "recovered_t_ge_02": float(rec[T >= 0.2].mean()) if (T >= 0.2).any() else None,
                     "recovered_t_lt_02": float(rec[T < 0.2].mean()) if (T < 0.2).any() else None}
        order = np.argsort(T)
        curve = []
        for q in np.arange(0, 1.0, 0.1):
            keep = order[int(q * len(order)):]
            curve.append({"dropped": round(float(q), 1), "t_cut": float(T[order[int(q * len(order))]]),
                          "feat_td": float(Fd[keep].mean()), "recovered": float(rec[keep].mean())})
        NUM["o4"]["discard_curve"] = curve
        print(f"\nOutcome 4: AUC of t for recovered (TD distance < guard p95 {thr:.4f}) = {a0:.3f} "
              f"[{NUM['o4']['lo']:.3f}, {NUM['o4']['hi']:.3f}] over {len(tiles)} tiles; "
              f"distance t>=0.2 {NUM['o4']['feat_td_t_ge_02']}, t<0.2 {NUM['o4']['feat_td_t_lt_02']}")
        print("  discard curve: " + "; ".join(f"drop {c['dropped']:.1f} (t>={c['t_cut']:.2f}): {c['feat_td']:.4f}, "
                                               f"rec {c['recovered']:.2f}" for c in curve))

    # ---- outcome 5: cloud detection against satellite-NOAA disagreement
    d5 = {k: [] for k in ("d", "rise", "spot", "guard", "tile", "spotrun")}
    for kind in ("pixel", "dino"):
        pass
    seen = set()
    for f in sorted(OUT.glob("*_dino.npz")) + sorted(OUT.glob("*_pixel.npz")):
        tid = f.name.rsplit("_", 1)[0]
        if tid in seen:
            continue
        seen.add(tid)
        z = np.load(f, allow_pickle=True)
        d5["d"].append(z["o5_disagree"]); d5["rise"].append(z["o5_darkrise"]); d5["spot"].append(z["o5_spot"])
        d5["guard"].append(z["o5_guard"]); d5["tile"].append(np.full(len(z["o5_disagree"]), tid))
        d5["spotrun"].append(np.full(len(z["o5_disagree"]), f.name.endswith("_dino.npz")))
    D, RI, SP, G, TL, SR = (np.concatenate(d5[k]) for k in ("d", "rise", "spot", "guard", "tile", "spotrun"))
    thr5 = float(np.percentile(D[G], 99))
    dis = D > thr5

    def f1(pred, truth, tl):
        tiles = np.unique(tl)
        cnt = {t: np.array([((pred & truth) & (tl == t)).sum(), ((pred & ~truth) & (tl == t)).sum(),
                            ((~pred & truth) & (tl == t)).sum()]) for t in tiles}
        tot = sum(cnt.values())
        def _f(c):
            return 2 * c[0] / max(2 * c[0] + c[1] + c[2], 1)
        rng = np.random.default_rng(C.SEED)
        bs = [_f(sum(cnt[tiles[i]] for i in ii)) for ii in boot_idx(list(tiles), rng)]
        return {"f1": float(_f(tot)), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                "precision": float(tot[0] / max(tot[0] + tot[1], 1)), "recall": float(tot[0] / max(tot[0] + tot[2], 1)),
                "tiles": int(len(tiles))}
    NUM["o5"] = {"threshold_guard_p99": thr5, "disagree_share": float(dis.mean()),
                 "darkrise_all_tiles": f1(RI, dis, TL), "darkrise_spotter_tiles": f1(RI[SR], dis[SR], TL[SR]),
                 "spotter_spotter_tiles": f1(SP[SR], dis[SR], TL[SR])}
    print(f"\nOutcome 5 (upper-noise check): disagreement > guard p99 = {thr5:.1f} grey levels; " +
          "; ".join(f"{k}: F1 {v['f1']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}] P {v['precision']:.2f} R {v['recall']:.2f} "
                    f"({v['tiles']} tiles)" for k, v in NUM["o5"].items() if isinstance(v, dict)))

    # ---- outcome 7: grey error and edge r (all aligned tiles)
    print("\nOutcome 7 (secondary; no arm is chosen on these):")
    NUM["o7"] = {}
    for region in ("thin", "opaque", "guard"):
        for subset in ("road", "all"):
            for metric in ("grey_err", "edge_r"):
                for a, b in comps:
                    r = paired(pix, region, subset, metric, a, b)
                    NUM["o7"][f"{region}_{subset}_{metric}_{a}-{b}"] = r
                    if "diff" in r:
                        print(f"  {region} {subset} {metric} {a}-{b}: {fmt(r['diff'], r['lo'], r['hi'], 3)} "
                              f"(tiles {r['n_tiles']}; means {r['mean_a']:.3f} vs {r['mean_b']:.3f})")

    # ---- Ref-Diff leakage diagnostic (thin road strips and all thin): closer to the pre-storm image than to NOAA?
    NUM["leakage"] = {}
    for subset in ("road", "all"):
        d = dino[(dino.region == "thin") & (dino.subset == subset) & (dino.px >= MIN_PX) & dino.arm.isin(["asis", "he", "td", "tdspot"])]
        for a in ("asis", "he", "td", "tdspot"):
            x = d[d.arm == a]
            if len(x) > 2:
                diff = (x.feat_to_before - x.feat).to_numpy()
                m, lo, hi = ci_mean(diff, x.tile_id)
                NUM["leakage"][f"{a}_{subset}"] = {"feat_to_before": float(x.feat_to_before.mean()),
                                                   "feat_to_noaa": float(x.feat.mean()), "diff": m, "lo": lo, "hi": hi,
                                                   "closer_to_before_tiles": int((diff < 0).sum()), "tiles": int(len(x))}
        print(f"\nLeakage ({subset}): " + "; ".join(f"{k}: to before {v['feat_to_before']:.4f} vs to NOAA "
                                                    f"{v['feat_to_noaa']:.4f}, closer to before on {v['closer_to_before_tiles']}/{v['tiles']}"
                                                    for k, v in NUM["leakage"].items() if k.endswith(subset)))

    # ---- noise floor
    fl = []
    for f in sorted(OUT.glob("*_dino.npz")):
        e = np.load(f, allow_pickle=True)["extra"].item()
        if "floor" in e:
            fl.append({"tile_id": f.name.replace("_dino.npz", ""), **e["floor"]})
    if fl:
        F = pd.DataFrame(fl)
        F.to_csv(C.HERE / "s5_noise_floor.csv", index=False)
        NUM["noise_floor"] = {"tiles": int(len(F)), **{c: float(F[c].mean()) for c in F.columns if c.startswith("floor_")}}
        print(f"\nDate-gap noise floor ({len(F)} tiles, clear ground): " + json.dumps(NUM["noise_floor"]))

    # ---- optional spread check
    sp, sf, se = [], [], []
    for f in sorted(OUT.glob("*_dino.npz")):
        z = np.load(f, allow_pickle=True)
        if "spread_thin" in z.files:
            sp.append(z["spread_thin"]); sf.append(z["spread_feat_td"]); se.append(z["spread_grey_err_td"])
    if sp:
        sp, sf, se = map(np.concatenate, (sp, sf, se))
        NUM["spread"] = {"pixels": int(len(sp)), "spearman_spread_feat": float(spearmanr(sp, sf).statistic),
                         "spearman_spread_grey_err": float(spearmanr(sp, se).statistic)}
        print("\nSpread check: " + json.dumps(NUM["spread"]))

    # ---- call level, outcome 6, label gap
    rc = C.HERE / "s4_road_calls.csv"
    if rc.exists():
        W = pd.read_csv(rc)
        NUM["calls"] = {}
        print("\nCall level (adapted from M3R-CR): agreement with the calls on the NOAA image")
        for grp, m in (("cloudy", W.cloudy), ("thin", W.thin_cloud), ("opaque tiles", W.cloudy & ~W.thin_cloud),
                       ("clear (ceiling)", ~W.cloudy)):
            x = W[m]
            res = {"roads": int(len(x)), "tiles": int(x.tile_id.nunique())}
            for a in ("asis", "he", "td", "tdspot"):
                c = f"call_{a}"
                xx = x.dropna(subset=[c, "call_noaa"])
                if len(xx) < 3:
                    continue
                ag = (xx[c] == xx.call_noaa).astype(float)
                tt = xx.tile_id.to_numpy()
                # road-level agreement, blocks resampled
                rng = np.random.default_rng(C.SEED)
                tiles = np.unique(tt)
                idx = {t: np.flatnonzero(tt == t) for t in tiles}
                bs = [ag.to_numpy()[np.concatenate([idx[tiles[i]] for i in ii])].mean() for ii in boot_idx(list(tiles), rng)]
                res[a] = {"roads": int(len(xx)), "agree": float(ag.mean()), "lo": float(np.percentile(bs, 2.5)),
                          "hi": float(np.percentile(bs, 97.5)), "called_flooded": float(xx[c].mean()),
                          "noaa_called_flooded": float(xx.call_noaa.mean())}
                if a != "asis":
                    a0 = (xx.call_asis == xx.call_noaa).astype(float).to_numpy()
                    d = ag.to_numpy() - a0
                    bs = [d[np.concatenate([idx[tiles[i]] for i in ii])].mean() for ii in boot_idx(list(tiles), np.random.default_rng(C.SEED))]
                    res[a].update(diff_vs_asis=float(d.mean()), diff_lo=float(np.percentile(bs, 2.5)),
                                  diff_hi=float(np.percentile(bs, 97.5)), fixed=int((d > 0).sum()), broken=int((d < 0).sum()))
            NUM["calls"][grp] = res
            print(f"  {grp}: {res['roads']} roads, {res['tiles']} tiles: " + "; ".join(
                f"{a} {v['agree']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}]" + (f" (vs as is {v['diff_vs_asis']:+.3f} [{v['diff_lo']:+.3f}, {v['diff_hi']:+.3f}], fixed {v['fixed']} broken {v['broken']})" if 'diff_vs_asis' in v else "")
                for a, v in res.items() if isinstance(v, dict)))
        # outcome 6
        NUM["o6"] = {}
        for grp, m in (("cloudy", W.cloudy), ("thin", W.thin_cloud), ("clear (ceiling)", ~W.cloudy)):
            x = W[m]
            res = {}
            for a in ("asis", "he", "td", "tdspot"):
                c = f"dino_change_pooled_{a}"
                xx = x.dropna(subset=[c, "dino_change_pooled_noaa"])
                if len(xx) < 5:
                    continue
                rho = float(spearmanr(xx[c], xx.dino_change_pooled_noaa).statistic)
                tt = xx.tile_id.to_numpy(); tiles = np.unique(tt)
                idx = {t: np.flatnonzero(tt == t) for t in tiles}
                bs = []
                for ii in boot_idx(list(tiles), np.random.default_rng(C.SEED)):
                    sel = np.concatenate([idx[tiles[i]] for i in ii])
                    bs.append(spearmanr(xx[c].to_numpy()[sel], xx.dino_change_pooled_noaa.to_numpy()[sel]).statistic)
                res[a] = {"roads": int(len(xx)), "rho": rho, "lo": float(np.nanpercentile(bs, 2.5)),
                          "hi": float(np.nanpercentile(bs, 97.5))}
            NUM["o6"][grp] = res
            print(f"  outcome 6 {grp}: " + "; ".join(f"{a} rho {v['rho']:.3f} [{v['lo']:.3f}, {v['hi']:.3f}] (n {v['roads']})" for a, v in res.items()))
        # label gap
        x = W[W.cloudy]
        NUM["label_gap"] = {"cloudy_roads_scored": int(len(x)), "marked_flooded_scored": int(x.flooded_label.sum()),
                            "noaa_called_flooded": int(x.call_noaa.sum()),
                            "noaa_called_flooded_and_marked": int((x.call_noaa.astype(bool) & x.flooded_label.astype(bool)).sum()),
                            "noaa_called_flooded_not_marked": int((x.call_noaa.astype(bool) & ~x.flooded_label.astype(bool)).sum()),
                            "asis_called_flooded": int(x.call_asis.sum()), "marked_flooded_all_dev": 27,
                            "thin_noaa_called_flooded": int(x[x.thin_cloud].call_noaa.sum()),
                            "thin_marked": int(x[x.thin_cloud].flooded_label.sum())}
        c = W[~W.cloudy]
        NUM["label_gap"]["clear_marked"] = int(c.flooded_label.sum())
        NUM["label_gap"]["clear_noaa_called_flooded"] = int(c.call_noaa.sum())
        NUM["label_gap"]["clear_noaa_called_and_marked"] = int((c.call_noaa.astype(bool) & c.flooded_label.astype(bool)).sum())
        NUM["label_gap"]["clear_asis_called_flooded"] = int(c.call_asis.sum())
        print("\nLabel gap: " + json.dumps(NUM["label_gap"]))
    (C.HERE / "s5_numbers.json").write_text(json.dumps(NUM, indent=1, default=float))


if __name__ == "__main__":
    main()
