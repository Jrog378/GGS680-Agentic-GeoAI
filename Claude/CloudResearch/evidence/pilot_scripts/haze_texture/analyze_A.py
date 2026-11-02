"""Phase A steps 1-4 (evidence/20): agreement of the haze scores, haze the masks miss, texture inflation on unchanged
roads, and the relation to production's held-out errors (arm c00, spatial folds S, 21 seeds). No fitting of flood
models here. Writes phaseA_numbers.json, phaseA_*.csv and the figures.
    nice -n 10 /opt/miniconda3/bin/python -I analyze_A.py > analyze_A.log 2>&1"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from haze_common import FIG, HERE, SCV, tile_maps

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LogisticRegression

N_BOOT = 2000
SEED = 662
SEEDS = [662] + list(range(1, 21))
ROADS_CSV = HERE / "roads_dev.csv"
# the four scores (after date) and their before-date null versions
PRIMARY = {"rise": ("rise_med", "fall_med"), "hot": ("hot_post_med", "hot_pre_med"),
           "atten": ("atten_med", None), "spot": ("spot_post_mean", "spot_pre_mean")}
LABEL = {"rise": "(a) dark-channel rise", "atten": "(b) contrast attenuation", "hot": "(c) HOT (colour)",
         "spot": "(d) spotter probability"}


def load():
    if not ROADS_CSV.exists():
        from sn8_heldout import touched_roads
        r = touched_roads(include_cloudy=True)
        from sn8_clouds import cloud_table
        c = pd.concat([cloud_table("train"), cloud_table("val")], ignore_index=True)
        assert c.tile_id.equals(r.tile_id) and c.road_id.equals(r.road_id)
        for k in ("cloud_bright_road", "cloud_dark_road", "dark_rise_road"):
            r[k] = c[k].to_numpy()
        r.to_csv(ROADS_CSV, index=False)
    r = pd.read_csv(ROADS_CSV)
    assert set(r.split) <= {"train", "val"} and len(r) == 1037
    h = pd.read_csv(HERE / "haze_roads.csv")
    assert h.tile_id.equals(r.tile_id) and h.road_id.equals(r.road_id), "haze_roads.csv order differs"
    r = pd.concat([r, h.drop(columns=["tile_id", "road_id", "split"])], axis=1)
    spot = pd.read_csv(HERE.parent / "cloud_spotting" / "gate_roads.csv")
    assert spot.tile_id.equals(r.tile_id) and spot.road_id.equals(r.road_id)
    r["spot_road"] = spot.spot_road.to_numpy()
    from spatial_folds import dev_roads, fold_table
    d = dev_roads()
    assert d.tile_id.equals(r.tile_id) and d.road_id.equals(r.road_id)
    r["kept"] = d.production_rule.to_numpy()
    assert r.kept.sum() == 798
    ft = fold_table(SEED)
    r["block"] = r.tile_id.map(dict(zip(ft.tile_id, ft.block)))
    z = np.load(SCV / "spatial_cv_flood_calls.npz")
    y = r.flooded.astype(int).to_numpy()
    calls = np.stack([z[f"c00__S__{s}"] for s in SEEDS])
    assert (calls[:, r.kept.to_numpy()] >= 0).all()
    r["right_share"] = (calls == y).mean(0)
    r["called_flooded_share"] = (calls == 1).mean(0)
    return r, calls


def block_boot(blocks, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    u = np.unique(blocks)
    groups = [np.flatnonzero(blocks == b) for b in u]
    for _ in range(n):
        yield np.concatenate([groups[i] for i in rng.integers(0, len(groups), len(groups))])


def spearman_cols(X, h):
    """Spearman of each column of X with h (rows with NaN dropped per column)."""
    out = []
    for j in range(X.shape[1]):
        ok = np.isfinite(X[:, j]) & np.isfinite(h)
        a, b = rankdata(X[ok, j]), rankdata(h[ok])
        out.append(np.corrcoef(a, b)[0, 1])
    return np.array(out)


def within_tile(v, tiles):
    """Ranks, then minus each tile's mean rank (tile fixed effects on ranks)."""
    s = pd.Series(rankdata(v), index=range(len(v)))
    return (s - s.groupby(tiles).transform("mean")).to_numpy()


def ci(a):
    a = np.asarray(a)
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def boot_p(a):
    a = np.asarray(a)
    a = a[np.isfinite(a)]
    return float(min(1.0, 2 * min((a <= 0).mean(), (a >= 0).mean())))


def bh(p):
    p = np.asarray(p)
    o = np.argsort(p)
    q = p[o] * len(p) / (np.arange(len(p)) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty_like(q)
    out[o] = np.minimum(q, 1)
    return out


def main():
    r, calls = load()
    out = {}
    kept = r.kept.to_numpy()
    y = r.flooded.astype(int).to_numpy()
    after_cols = [v[0] for v in PRIMARY.values()]
    mask_cols = ["cloud_dark_rise_road", "cloud_bright_road", "cloud_dark_road", "spot_road"]

    # ---------------- 1. agreement ----------------
    cols = after_cols + ["rise_p90", "hot_post_p90", "atten_p90"]
    agree = {}
    for scope, m in (("all 1037", np.ones(len(r), bool)), ("kept 798", kept)):
        sub = r.loc[m, cols + mask_cols]
        agree[scope] = sub.rank().corr().round(3).to_dict()
        print(f"\n[1] Spearman among scores and masks, {scope}\n", sub.rank().corr().round(2).to_string())
    out["agreement_spearman"] = agree
    tiles = pd.read_csv(HERE / "haze_tiles.csv")
    tcols = ["raw_rise_med", "rise_p90", "atten_med", "hot_post_p90", "spot_post_mean", "mask_bright", "mask_dark",
             "mask_dark_rise"]
    print("\n[1] tile level (226 tiles) Spearman\n", tiles[tcols].rank().corr().round(2).to_string())
    out["tile_agreement_spearman"] = tiles[tcols].rank().corr().round(3).to_dict()

    # ---------------- 2. haze the masks miss ----------------
    k = r[kept].reset_index(drop=True)
    elevated, null99 = {}, {}
    for name, (a, b) in PRIMARY.items():
        nullv = -k[a].to_numpy() if b is None else k[b].to_numpy()
        null99[name] = float(np.nanpercentile(nullv, 99))
        elevated[name] = (k[a].to_numpy() > null99[name])
    E = pd.DataFrame(elevated)
    n_el = E.sum(1)
    nomask = (k.cloud_dark_rise_road == 0) & (k.cloud_bright_road == 0) & (k.cloud_dark_road == 0)
    step2 = {"null 99th percentile (before-date version, kept roads)": null99,
             "kept roads above it, per score": {c: int(E[c].sum()) for c in E},
             "share above it (expected 0.01 if no haze)": {c: float(E[c].mean()) for c in E},
             "above on rise and HOT": int((E.rise & E.hot).sum()),
             "above on >= 2 of 4 scores": int((n_el >= 2).sum()),
             "above on >= 2 of 4, flooded / not": [int(((n_el >= 2) & k.flooded).sum()), int(((n_el >= 2) & ~k.flooded).sum())],
             "above on >= 2 of 4 and no pixel under any mask": int(((n_el >= 2) & nomask).sum()),
             "kept roads with no pixel under any mask": int(nomask.sum()),
             "above on >= 2 of 4, tiles": int(k.tile_id[n_el >= 2].nunique()),
             "above on rise, flooded / not": [int((E.rise & k.flooded).sum()), int((E.rise & ~k.flooded).sum())]}
    out["step2"] = step2
    print("\n[2]", json.dumps(step2, indent=1))
    pd.concat([k[["tile_id", "road_id", "flooded", "cloud_dark_rise_road"] + after_cols], E.add_prefix("elev_")],
              axis=1).to_csv(HERE / "phaseA_elevated.csv", index=False)
    fig_hists(k, null99)

    # ---------------- 3. texture inflation on unchanged roads ----------------
    change = [c for c in r.columns if c.endswith("_change")] + ["dino_change_pooled", "dino_change_mean", "dino_change_max"]
    sign = {}
    for c in change:
        sign[c] = float(np.sign(np.nanmedian(k.loc[k.flooded, c]) - np.nanmedian(k.loc[~k.flooded, c])) or 1)
    u = k[~k.flooded.astype(bool)].reset_index(drop=True)
    print(f"\n[3] unchanged roads (kept, not marked flooded): {len(u)} on {u.tile_id.nunique()} tiles, "
          f"{u.block.nunique()} blocks")
    Xf = np.stack([sign[c] * u[c].to_numpy() for c in change], 1)       # flood-ward change: > 0 looks more flooded
    Xa = np.abs(np.stack([u[c].to_numpy() for c in change], 1))         # size of the change, either way
    blocks = u.block.to_numpy()
    boots = list(block_boot(blocks))
    texture_idx = [i for i, c in enumerate(change) if not c.startswith("dino")]
    dino_idx = [i for i, c in enumerate(change) if c.startswith("dino")]
    rows, summary = [], {}
    for name, (a, _) in PRIMARY.items():
        h = u[a].to_numpy()
        for kind, X in (("flood-ward", Xf), ("absolute", Xa)):
            est = spearman_cols(X, h)
            bs = np.array([spearman_cols(X[i], h[i]) for i in boots])
            # within tile (tile fixed effects on ranks)
            wt_h = within_tile(h, u.tile_id.to_numpy())
            wt = np.array([np.corrcoef(within_tile(np.nan_to_num(X[:, j], nan=np.nanmedian(X[:, j])),
                                                    u.tile_id.to_numpy()), wt_h)[0, 1] for j in range(X.shape[1])])
            ps = [boot_p(bs[:, j]) for j in range(len(change))]
            q = bh(ps)
            for j, c in enumerate(change):
                lo, hi = ci(bs[:, j])
                rows.append({"score": name, "kind": kind, "feature": c, "flood sign": sign[c], "spearman": est[j],
                             "ci_lo": lo, "ci_hi": hi, "boot p": ps[j], "BH q": q[j], "within-tile r": wt[j]})
            for fam, idx in (("texture + classical (31)", texture_idx), ("DINOv2 (3)", dino_idx)):
                m_est = float(np.mean(est[idx]))
                m_bs = bs[:, idx].mean(1)
                summary[f"{name} · {kind} · {fam}"] = {
                    "mean spearman": m_est, "95% CI": ci(m_bs), "within-tile mean r": float(np.mean(wt[idx])),
                    "features with CI above 0": int(sum(ci(bs[:, j])[0] > 0 for j in idx)),
                    "features with CI below 0": int(sum(ci(bs[:, j])[1] < 0 for j in idx)),
                    "features with BH q < 0.05": int(sum(q[j] < 0.05 for j in idx))}
    t3 = pd.DataFrame(rows)
    t3.to_csv(HERE / "phaseA_texture_inflation.csv", index=False)
    out["step3_summary"] = summary
    out["step3_n_unchanged"] = int(len(u))
    print("\n[3] summaries\n", pd.DataFrame(summary).T.to_string())
    top = t3[t3.kind == "flood-ward"].sort_values("spearman", ascending=False)
    print("\n[3] largest flood-ward correlations\n", top.head(15).round(3).to_string())
    print("\n[3] most negative\n", top.tail(8).round(3).to_string())
    fig_inflation(t3, change)

    # ---------------- 4. errors ----------------
    err = 1 - k.right_share.to_numpy()
    yk = k.flooded.astype(int).to_numpy()
    kb = k.block.to_numpy()
    kboots = list(block_boot(kb, seed=SEED + 1))
    step4 = {"production S accuracy (mean over 21 seeds) on the 798": float(1 - err.mean())}
    qrows = []
    for name, (a, _) in PRIMARY.items():
        h = k[a].to_numpy()
        res = {}
        for grp, m in (("all 798", np.ones(len(k), bool)), ("not flooded: false alarms", yk == 0),
                       ("flooded: misses", yk == 1)):
            hh, ee, bb = h[m], err[m], kb[m]
            qs = np.nanquantile(hh, [0.25, 0.5, 0.75])
            qi = np.digitize(hh, qs)
            means = [float(ee[qi == j].mean()) for j in range(4)]
            idx_m = np.flatnonzero(m)
            pos = {g: j for j, g in enumerate(idx_m)}
            diffs, cis = [], {j: [] for j in range(4)}
            for b in kboots:
                b = np.array([pos[i] for i in b if i in pos], int)
                if len(b) == 0:
                    continue
                e_b, q_b = ee[b], qi[b]
                vals = [e_b[q_b == j].mean() if (q_b == j).any() else np.nan for j in range(4)]
                for j in range(4):
                    cis[j].append(vals[j])
                diffs.append(vals[3] - vals[0])
            res[grp] = {"quartile error rates": means, "quartile 95% CIs": [ci(cis[j]) for j in range(4)],
                        "Q4 - Q1": means[3] - means[0], "Q4 - Q1 95% CI": ci(diffs), "n per quartile":
                            [int((qi == j).sum()) for j in range(4)]}
            for j in range(4):
                qrows.append({"score": name, "group": grp, "quartile": j + 1, "error": means[j],
                              "ci_lo": ci(cis[j])[0], "ci_hi": ci(cis[j])[1]})
        # logistic model: error ~ z(haze) + flooded (+ separately within each label)
        zh = (h - np.nanmean(h)) / np.nanstd(h)

        def fit(idx, with_label=True):
            X = np.column_stack([zh[idx], yk[idx]]) if with_label else zh[idx, None]
            n = len(idx)
            Xr = np.vstack([X, X])
            yr = np.r_[np.ones(n), np.zeros(n)]
            w = np.r_[err[idx], 1 - err[idx]] * len(SEEDS)
            mdl = LogisticRegression(penalty=None, max_iter=1000).fit(Xr, yr, sample_weight=w)
            return mdl.coef_[0]

        all_idx = np.arange(len(k))
        coef = fit(all_idx)
        bcoef = np.array([fit(b) for b in kboots])
        res["logistic: error ~ z(haze) + flooded"] = {"haze log-odds per SD": float(coef[0]), "95% CI": ci(bcoef[:, 0]),
                                                      "odds ratio per SD": float(np.exp(coef[0])),
                                                      "flooded coef": float(coef[1])}
        for grp, lab in (("false alarms (not flooded)", 0), ("misses (flooded)", 1)):
            idx = np.flatnonzero(yk == lab)
            c0 = fit(idx, False)[0]
            bc = []
            for b in kboots:
                bi = b[yk[b] == lab]
                if len(bi):
                    bc.append(fit(bi, False)[0])
            res[f"logistic within {grp}"] = {"haze log-odds per SD": float(c0), "95% CI": ci(bc)}
        step4[name] = res
        print(f"\n[4] {LABEL[name]} ({a})\n", json.dumps(res, indent=1))
    pd.DataFrame(qrows).to_csv(HERE / "phaseA_error_quartiles.csv", index=False)
    out["step4"] = step4
    fig_errors(pd.DataFrame(qrows))

    # ---------------- decision for Phase B ----------------
    gate = {}
    for name in ("rise", "hot"):
        s3 = summary[f"{name} · flood-ward · texture + classical (31)"]["95% CI"]
        s4 = step4[name]["logistic: error ~ z(haze) + flooded"]["95% CI"]
        gate[name] = {"inflation CI": s3, "error CI": s4, "both exclude 0 upward": bool(s3[0] > 0 and s4[0] > 0)}
    out["phase B gate"] = gate
    print("\n[gate]", json.dumps(gate, indent=1))
    (HERE / "phaseA_numbers.json").write_text(json.dumps(out, indent=1, default=float))


# ------------------------------------------------------------------ figures
def fig_hists(k, null99):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.2))
    for ax, (name, (a, b)) in zip(axes, PRIMARY.items()):
        va = k[a].dropna().to_numpy()
        vb = (-k[a] if b is None else k[b]).dropna().to_numpy()
        lo, hi = np.percentile(np.r_[va, vb], [0.5, 99.5])
        bins = np.linspace(lo, hi, 50)
        ax.hist(vb, bins, alpha=0.55, color="#7f7f7f", label="null: before date" if b else "null: mirror")
        ax.hist(va, bins, alpha=0.55, color="#d95f02", label="after date")
        ax.axvline(null99[name], color="k", ls="--", lw=1, label="null 99th pct")
        ax.set_title(f"{LABEL[name]}\n{int((va > null99[name]).sum())} of {len(va)} kept roads above", fontsize=10)
        ax.set_xlabel(a)
        ax.legend(fontsize=8)
    fig.suptitle("The 798 roads production's cloud gate calls clear: road-strip haze scores, after date vs a null",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "A2_score_distributions.png", dpi=110)
    plt.close(fig)


def fig_inflation(t3, change):
    import matplotlib.pyplot as plt
    d = t3[t3.kind == "flood-ward"]
    fig, axes = plt.subplots(1, 4, figsize=(22, 9), sharey=True)
    for ax, name in zip(axes, PRIMARY):
        s = d[d.score == name].set_index("feature").loc[change]
        yy = np.arange(len(change))
        col = ["#d95f02" if lo > 0 else "#1b9e77" if hi < 0 else "#999999" for lo, hi in zip(s.ci_lo, s.ci_hi)]
        ax.errorbar(s.spearman, yy, xerr=[s.spearman - s.ci_lo, s.ci_hi - s.spearman], fmt="none", ecolor=col)
        ax.scatter(s.spearman, yy, c=col, s=18)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_title(f"{LABEL[name]}", fontsize=10)
        ax.set_xlabel("Spearman with flood-ward change\n(unchanged roads; 95% CI, 3x3-block bootstrap)")
    axes[0].set_yticks(np.arange(len(change)))
    axes[0].set_yticklabels(change, fontsize=8)
    axes[0].invert_yaxis()
    fig.suptitle("Does haze make roads that did NOT flood look flooded? (orange: CI above 0)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "A3_texture_inflation.png", dpi=110)
    plt.close(fig)


def fig_errors(q):
    import matplotlib.pyplot as plt
    groups = ["all 798", "not flooded: false alarms", "flooded: misses"]
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.2), sharey=True)
    for ax, name in zip(axes, PRIMARY):
        for g, c, off in zip(groups, ["k", "#d95f02", "#1b9e77"], (-0.15, 0, 0.15)):
            s = q[(q.score == name) & (q.group == g)]
            ax.errorbar(s.quartile + off, s.error, yerr=[s.error - s.ci_lo, s.ci_hi - s.error], fmt="o-", color=c,
                        label=g, capsize=3)
        ax.set_xticks([1, 2, 3, 4])
        ax.set_xlabel("haze quartile (1 = least)")
        ax.set_title(LABEL[name], fontsize=10)
    axes[0].set_ylabel("held-out error rate (c00, S, 21 seeds)")
    axes[0].legend(fontsize=8)
    fig.suptitle("Production's held-out error on the 798 'clear' roads by haze quartile (95% CI, 3x3-block bootstrap)",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "A4_errors_by_quartile.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    main()
