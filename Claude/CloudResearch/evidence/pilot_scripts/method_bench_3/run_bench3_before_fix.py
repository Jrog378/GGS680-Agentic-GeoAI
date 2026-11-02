"""Method bench 3, Phase G (greyscale) runner (outputs/preregistration_method_bench_3.md). Strictly serial: one
process, 2 threads, no multiprocessing, no GPU. Every stage is resumable and checks production.json's sha256 before and
after; it waits before every tile/fit batch while free memory < 30% or swap > 4 GB.

Stages (`all` = thresholds tiles gates ida primary score flood pul combo):
  thresholds  pooled training-tile fits: T1's cut (integer Otsu, eta >= 0.65 else p99), T1d check, B1p EM cuts.
  smoke       every arm on the 3 smoke tiles (NOT scored): smoke_results.json + figures/method_bench_3/smoke_*.png
  tiles       the 200 development tiles: gate masks -> road shares, U1 cues, per-road mean t (C0 and each correction),
              C0 and correction-arm after-date rows (bench 1's after_rows). Pickles in BIG/tiles/.
  gates       clear-tile false-alarm shares.
  ida         Ida secondary (grey error, edge r, guard) for the corrections and the gate check (132 prep tiles).
  primary     DINOv2 (CPU) feature distance to NOAA in thin, 3-hour token budget.
  score       Ida statistics (bench 1's paired_tiles).
  flood       production reproduced at 662 -> every arm at all 21 seeds; screen, seed averages, McNemar + Holm,
              accuracy on the roads a gate adds.
  pul         PUL / PULb (predict_proba path; production reproduced on that path first).
  combo       carry rule (top 2 per family) -> 3 x 3 x 3 factorial, 21 seeds, interactions.
    cd evidence/pilot_scripts/method_bench_3
    OMP_NUM_THREADS=2 nice -n 10 python3 -I run_bench3.py all > run_bench3.log 2>&1
"""
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b3_common as K

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

T0 = time.time()
TILES_DIR = K.BIG / "tiles"
CALLS = K.BIG / "bench3_flood_calls.npz"
NUMBERS = K.HERE / "bench3_numbers.json"
MIN_THIN = 2000
RING_PX = 80
BUDGET_S = 3 * 3600
GATE_KEYS = ["T1", "T1b", "B1", "B1p", "B2-1.3", "B2-1.6", "B2-1.8"]       # T1d added if the check makes it a candidate
G_GATE_ARMS = {"T1 Otsu grey rise": "T1", "T1b Otsu grey rise + blob": "T1b", "B1 EM-Bayes hysteresis": "B1",
               "B1p EM-Bayes pooled": "B1p", "B2 ICM-MRF beta 1.3": "B2-1.3", "B2 ICM-MRF beta 1.6": "B2-1.6",
               "B2 ICM-MRF beta 1.8": "B2-1.8"}
U1_ARMS = ["U1 DS certain gate", "U1s DS strict"]


def R2():
    import run_bench2                                    # bench 2, read-only (its _align, dev_tiles, disagreement)
    return run_bench2


def corr_arms():
    import g3_corr
    return list(g3_corr.ARMS)


# ------------------------------------------------------------------------------------------------ one tile
def tile_job(tid, TH, out_dir=TILES_DIR):
    f = out_dir / f"{tid}.pkl"
    if f.exists():
        return
    from after_features import after_rows
    from sn8_clouds import _tile
    from sn8_cloudspot import _strip, road_shares
    from sn8_lines import road_band
    from sn8_refhaze import dark_reference_dehaze
    import g3_corr, g3_gates
    K.dev_guard_tiles([tid])
    t1 = time.time()
    p, before, after, valid = _tile(tid)
    masks, minfo = g3_gates.masks(p, before, after, valid, TH)
    band = road_band()
    strip, roads, n, centre_px = _strip(tid, p, valid, band)
    c0 = dark_reference_dehaze(before, after, valid)
    outs = g3_corr.outputs(before, after, valid, c0)
    tmaps = {"t_C0": np.where(valid, c0["t"], 1.0)}
    for a, o in outs.items():
        tmaps[f"t_{a}"] = np.where(valid, o["t"], 1.0)
    res = {"tile_id": tid, "valid_px": int(valid.sum()), "mask_info": minfo,
           "tile_share": {k: float(v[valid].mean()) for k, v in masks.items()}, "road_shares": [], "u1": [],
           "arms": {}}
    if n:
        res["road_shares"] = road_shares(tid, strip, roads, n, centre_px, {**masks, **tmaps})
        res["u1"], res["u1_info"] = g3_gates.u1_cues(tid, p, before, after, valid, strip, roads, n, centre_px)
    raw = np.where(valid, after, 0).astype(np.float32)
    res["C0_rows"] = after_rows(tid, {**p, "after_grey": c0["corrected"]}, valid, band) \
        if not np.array_equal(c0["corrected"], raw) else None
    res["c0_diag"] = {"gate_px": int(c0["gate"].sum()), "opaque_px": int(c0["opaque"].sum())}
    for a in corr_arms():
        o = outs.get(a)
        if o is None:
            res["arms"][a] = {"same": "raw"}
            continue
        img = o["corrected"]
        diag = {"opaque_px": int(o["opaque"].sum()), "changed_px": int((img != raw).sum()), "info": o.get("info")}
        if np.array_equal(img, raw):
            res["arms"][a] = {"same": "raw", **diag}
        elif np.array_equal(img, c0["corrected"]):
            res["arms"][a] = {"same": "c0", **diag}
        else:
            res["arms"][a] = {"same": None, "rows": after_rows(tid, {**p, "after_grey": img}, valid, band), **diag}
    res["seconds"] = time.time() - t1
    out_dir.mkdir(parents=True, exist_ok=True)
    K.atomic_bytes(f, pickle.dumps(res))
    K.log(T0, f"{tid}: {res['seconds']:.0f} s, C0 gate {res['c0_diag']['gate_px']} px, shares "
              f"{ {k: round(v, 3) for k, v in res['tile_share'].items()} }")


def dev_tiles():
    return R2().dev_tiles()


def load_tiles():
    order, roads = dev_tiles()
    res = {}
    for t in order:
        f = TILES_DIR / f"{t}.pkl"
        if f.exists():
            res[t] = pickle.loads(f.read_bytes())
    return res, order, roads


# ------------------------------------------------------------------------------------------------ stages
def st_thresholds(num):
    import g3_gates
    TH = g3_gates.thresholds(T0)
    num["thresholds"] = TH
    K.log(T0, f"thresholds: {json.dumps(K.M1.plain(TH))}")
    return TH


def st_tiles(num):
    import g3_gates
    TH = g3_gates.thresholds(T0)
    order, _ = dev_tiles()
    for i, tid in enumerate(order):
        if (TILES_DIR / f"{tid}.pkl").exists():
            continue
        K.wait_for_memory(T0)
        try:
            tile_job(tid, TH)
        except Exception as e:
            import traceback
            traceback.print_exc()
            K.log(T0, f"{tid}: ERROR {e!r}")
        if (i + 1) % 10 == 0:
            K.log(T0, f"{i + 1}/{len(order)} tiles")


def st_gates(num):
    from sn8_refhaze import clear_tiles
    res, _, _ = load_tiles()
    clear = [t for t in clear_tiles() if t in res]
    out = {"clear_tiles_scored": len(clear)}
    keys = ["rise"] + [k for k in res[clear[0]]["tile_share"] if k != "rise"]
    for k in keys:
        v = np.array([res[t]["tile_share"].get(k, 0.0) for t in clear])
        out[k] = {"mean": float(v.mean()), "median": float(np.median(v)), "tiles_over_1pct": int((v > 0.01).sum())}
    cloudy = [t for t in res if res[t]["c0_diag"]["gate_px"] > 0]
    out["empty_on_cloudy"] = {k: int(sum(res[t]["tile_share"].get(k, 0) == 0 for t in cloudy)) for k in keys}
    out["cloudy_tiles"] = len(cloudy)
    out["B1_abstain_reasons"] = pd.Series([res[t]["mask_info"]["B1"]["abstain"] for t in res]).fillna("fitted") \
        .value_counts().to_dict()
    out["B1_abstain_clear"] = pd.Series([res[t]["mask_info"]["B1"]["abstain"] for t in clear]).fillna("fitted") \
        .value_counts().to_dict()
    num["gates_clear_tiles"] = out
    K.log(T0, f"gates: {json.dumps(K.M1.plain(out))}")


def ida_outputs(p, before, after, valid):
    from sn8_refhaze import dark_reference_dehaze
    import g3_corr
    c0 = dark_reference_dehaze(before, after, valid)
    return {"C0": c0, **g3_corr.outputs(before, after, valid, c0)}


def st_ida(num):
    from sn8_clouds import _tile
    import g3_gates
    import run_ida_helpers as H
    TH = g3_gates.thresholds(T0)
    sec_f, gat_f = K.HERE / "ida_rows_secondary.csv", K.HERE / "ida_rows_gates.csv"
    sec = pd.read_csv(sec_f) if sec_f.exists() else pd.DataFrame(columns=["tile_id"])
    gat = pd.read_csv(gat_f) if gat_f.exists() else pd.DataFrame(columns=["tile_id"])
    tiles = H.usable_tiles()
    K.dev_guard_tiles(tiles)
    K.log(T0, f"{len(tiles)} usable Ida prep tiles")
    for t in tiles:
        if t in set(sec.tile_id):
            continue
        K.wait_for_memory(T0)
        p, before, after, valid = _tile(t)
        masks, _ = g3_gates.masks(p, before, after, valid, TH)
        z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
        dis, cut = R2()._noaa_disagreement(z, after, valid)
        grow = []
        for k, mk in masks.items():
            m = mk & z["score"]
            tp = int((m & dis).sum())
            grow.append({"tile_id": t, "mask": k, "flagged": int(m.sum()), "disagree": int(dis.sum()), "tp": tp,
                         "cut": cut})
        outs = ida_outputs(p, before, after, valid)
        c0 = outs["C0"]
        thin = z["score"] & c0["gate"] & ~c0["opaque"]
        rows = []
        if thin.sum() < MIN_THIN:
            rows.append({"tile_id": t, "arm": "-", "region": "thin", "px": int(thin.sum())})
        else:
            d = ndi.distance_transform_edt(~c0["gate"])
            ring = z["score"] & ~c0["gate"] & (d > 0) & (d <= RING_PX) & ~z["bright"]
            for arm, o in [("as is", {"corrected": np.where(valid, after, 0)})] + list(outs.items()):
                img = o["corrected"]
                for rn, m in (("thin", thin), ("ring", ring)):
                    rows.append({"tile_id": t, "arm": arm, "region": rn, "px": int(m.sum()),
                                 "grey_err": float(np.abs(img - z["noaa"])[m].mean()) if m.sum() >= 50 else np.nan,
                                 "edge_r": H.edge_r(img, z["noaa"], m)})
                rows.append({"tile_id": t, "arm": arm, "region": "guard", "px": int(z["guard"].sum()),
                             "grey_change": float(np.abs(img - z["asis"])[z["guard"]].mean())})
        gat = pd.concat([gat, pd.DataFrame(grow)], ignore_index=True)
        sec = pd.concat([sec, pd.DataFrame(rows)], ignore_index=True)
        tmp = gat_f.with_suffix(".writing"); gat.to_csv(tmp, index=False); tmp.replace(gat_f)
        tmp = sec_f.with_suffix(".writing"); sec.to_csv(tmp, index=False); tmp.replace(sec_f)
        K.log(T0, f"Ida {t}: thin {int(thin.sum())} px")


def st_primary(num):
    import torch
    torch.backends.mps.is_available = lambda: False
    torch.set_num_threads(2)
    import run_ida_helpers as H
    from sn8_clouds import _tile
    sec = pd.read_csv(K.HERE / "ida_rows_secondary.csv")
    pri_f = K.HERE / "ida_rows_primary.csv"
    pri = pd.read_csv(pri_f) if pri_f.exists() else pd.DataFrame(columns=["tile_id"])
    spent_f = K.HERE / "ida_primary_spent.txt"
    spent = float(spent_f.read_text()) if spent_f.exists() else 0.0
    th = sec[(sec.region == "thin") & (sec.arm != "-")].groupby("tile_id").px.first().sort_values(ascending=False)
    for t in th.index:
        if t in set(pri.tile_id):
            continue
        if spent >= BUDGET_S:
            K.log(T0, f"primary budget spent ({spent:.0f} s); stopping before {t}")
            break
        K.wait_for_memory(T0)
        t1 = time.time()
        p, before, after, valid = _tile(t)
        outs = ida_outputs(p, before, after, valid)
        z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
        c0, s = outs["C0"], z["score"]
        thin = s & c0["gate"] & ~c0["opaque"]
        need = H.windows_with(thin, s.shape)
        tok_noaa = H.window_tokens(z["noaa"], s, need)
        rows = []
        for arm, o in [("as is", {"corrected": np.where(valid, after, 0)})] + list(outs.items()):
            tok = H.window_tokens(o["corrected"].astype(np.float32), s, need)
            dist = H.patch_to_px(H.cosdist(tok, tok_noaa), s.shape)
            rows.append({"tile_id": t, "arm": arm, "region": "thin", "px": int(thin.sum()),
                         "feat": float(dist[thin].mean()) if thin.sum() >= 50 else np.nan})
        H.clear_tokens()
        spent += time.time() - t1
        spent_f.write_text(str(spent))
        pri = pd.concat([pri, pd.DataFrame(rows)], ignore_index=True)
        tmp = pri_f.with_suffix(".writing"); pri.to_csv(tmp, index=False); tmp.replace(pri_f)
        K.log(T0, f"primary {t}: {time.time() - t1:.0f} s (spent {spent:.0f} s)")


def st_score(num):
    from ida_score import paired_tiles
    sf = K.HERE / "ida_rows_secondary.csv"
    if sf.exists():
        sec = pd.read_csv(sf)
        sec = sec[sec.arm != "-"]
        arms = [a for a in sec.arm.unique() if a != "C0"]
        num["ida_secondary_tiles"] = int(sec.tile_id.nunique())
        for metric in ("grey_err", "edge_r"):
            for region in ("thin", "ring"):
                num[f"ida_{metric}_{region}_vs_C0"] = {a: paired_tiles(sec, metric, region, a) for a in arms}
        num["ida_guard_grey_change_mean"] = sec[sec.region == "guard"].groupby("arm").grey_change.mean().to_dict()
    gf = K.HERE / "ida_rows_gates.csv"
    if gf.exists():
        g = pd.read_csv(gf)
        num["ida_gates"] = {k: {"tiles": int(len(v)), "precision_pooled": float(v.tp.sum() / max(v.flagged.sum(), 1)),
                                "recall_pooled": float(v.tp.sum() / max(v.disagree.sum(), 1))}
                            for k, v in g.groupby("mask")}
    pf = K.HERE / "ida_rows_primary.csv"
    if pf.exists():
        pri = pd.read_csv(pf)
        num["ida_primary_tiles"] = sorted(pri.tile_id.unique().tolist())
        gc = num.get("ida_guard_grey_change_mean", {})
        num["ida_primary_vs_C0"] = {}
        for a in [x for x in pri.arm.unique() if x != "C0"]:
            r = paired_tiles(pri, "feat", "thin", a)
            if r:
                r["guard_ok"] = bool(abs(gc.get(a, 0) - gc.get("C0", 0)) <= 1.0)
            num["ida_primary_vs_C0"][a] = r
        num["ida_primary_C0_vs_asis"] = paired_tiles(pri, "feat", "thin", "C0", base="as is")
    K.log(T0, "score written")


# ------------------------------------------------------------------------------------------------ flood calls
class Data:
    """The 1,037 development roads with production's columns, the Phase G gate masks and the corrected column blocks
    (each correction arm plain and Q1-scaled)."""

    def __init__(self):
        from scv_common import Setup
        from sn8_clouds import ROAD_CLOUD_CUT
        import g3_gates
        S = Setup(build_x=False)
        self.S, self.roads, self.y, self.cols = S, S.roads, S.y, S.cols
        self.gate_a, self.tile_rule, self.block = S.gates["a"], S.tile_rule, S.block
        self.X = S.roads[self.cols].copy()
        self.arms = {"production (refit)": {"gate": self.gate_a, "cols": list(self.cols)}}
        res, _, _ = load_tiles()
        tiles = sorted(self.roads.tile_id[self.tile_rule].unique())
        missing = [t for t in tiles if t not in res]
        assert not missing, f"tile pickles missing: {len(missing)}"
        al_ = R2()._align
        sh = pd.concat([pd.DataFrame(res[t]["road_shares"]) for t in tiles if res[t]["road_shares"]], ignore_index=True)
        al = al_(self.roads, sh)
        hit = al["rise"].notna().to_numpy()
        gap = np.abs(al.rise.to_numpy()[hit] - self.roads.cloud_dark_rise_road.to_numpy()[hit]).max()
        assert gap < 1e-9, f"STOP: dark-rise share does not reproduce cloud_dark_rise_road ({gap})"
        assert ((self.tile_rule & (al.rise.to_numpy() < ROAD_CLOUD_CUT)) == self.gate_a).all()
        self.shares = al
        keys = dict(G_GATE_ARMS)
        if "T1d" in al.columns:
            keys["T1d Otsu dark rise"] = "T1d"
        self.gate_names = []
        for name, k in keys.items():
            self.arms[name] = {"gate": self.tile_rule & (al[k].to_numpy() < ROAD_CLOUD_CUT), "cols": list(self.cols)}
            self.gate_names.append(name)
        # U1 (Dempster-Shafer over all strips)
        u = pd.concat([pd.DataFrame(res[t]["u1"]) for t in tiles if res[t]["u1"]], ignore_index=True)
        ua = al_(self.roads, u)
        okr = ua.u1_m1c.notna().to_numpy() & self.tile_rule
        pc, certain, centres = g3_gates.u1_fuse(ua.u1_m1c.to_numpy()[okr], ua.u1_G.to_numpy()[okr])
        self.u1 = {"P_c": np.full(len(self.y), np.nan), "certain": np.zeros(len(self.y), bool), "fcm_centres": centres}
        self.u1["P_c"][okr] = pc
        self.u1["certain"][okr] = certain
        share = al.rise.to_numpy()
        under = share >= ROAD_CLOUD_CUT
        self.arms["U1 DS certain gate"] = {"gate": self.tile_rule & (~under | self.u1["certain"]), "cols": list(self.cols)}
        self.arms["U1s DS strict"] = {"gate": self.gate_a & ~((share > 0) & ~self.u1["certain"]), "cols": list(self.cols)}
        self.gate_names += U1_ARMS
        # corrected blocks
        from sn8_glcm import GLCM_FEATURES
        from sn8_roads import FEATURES
        from sn8_texture import TEXTURE_FEATURES
        self.feats = FEATURES + GLCM_FEATURES + TEXTURE_FEATURES
        assert len(self.feats) == 93
        self.after_cols = [c for c in self.feats if c.endswith("_after")]
        self.change_cols = [c for c in self.feats if c.endswith("_change")]
        self.raw = self.roads[["tile_id", "road_id"] + self.feats].reset_index(drop=True)
        tabs = {a: [] for a in ["C0"] + corr_arms()}
        for t in tiles:
            r = res[t]
            c0 = pd.DataFrame(r["C0_rows"]) if r["C0_rows"] else None
            if c0 is not None:
                tabs["C0"].append(c0)
            for a in corr_arms():
                x = r["arms"][a]
                if x["same"] == "c0" and c0 is not None:
                    tabs[a].append(c0)
                elif x["same"] is None:
                    tabs[a].append(pd.DataFrame(x["rows"]))
        self.corr_names = []
        for i, (a, parts) in enumerate(tabs.items()):
            name = "C0 current two-date" if a == "C0" else a
            tcol = "t_C0" if a == "C0" else f"t_{a}"
            tbar = np.nan_to_num(al[tcol].to_numpy(), nan=1.0) if tcol in al.columns else np.ones(len(self.y))
            self._add(name, f"tb{i}_", parts, None)
            self._add(f"Q1 1/t on {name}", f"tq{i}_", parts, np.maximum(tbar, 0.2))
            if a != "C0":
                self.corr_names.append(name)

    def _add(self, name, pre, parts, scale):
        td = self.raw.copy()
        hit = np.zeros(len(td), bool)
        if parts:
            al = R2()._align(self.roads, pd.concat(parts, ignore_index=True))
            hit = al[self.after_cols[0]].notna().to_numpy()
            for c in self.after_cols:
                td.loc[hit, c] = al.loc[hit, c].to_numpy()
        for m in {c[: -len("_after")] for c in self.after_cols}:
            td[f"{m}_change"] = td[f"{m}_after"] - td[f"{m}_before"]
            if scale is not None:                                     # Q1: d > tau/t  <=>  d * t > tau (cap t at 0.2)
                td[f"{m}_change"] = np.where(hit, td[f"{m}_change"] * scale, td[f"{m}_change"])
        for c in self.feats:
            self.X[pre + c] = td[c].to_numpy()
        self.arms[name] = {"gate": self.gate_a, "cols": list(self.cols) + [pre + c for c in self.feats]}


def load_calls():
    if not CALLS.exists():
        return {}
    z = np.load(CALLS)
    return {k: z[k] for k in z.files}


def save_calls(d):
    K.atomic_npz(CALLS, **d)


def _model(cols):
    from sklearn.pipeline import make_pipeline
    from sn8_dino import DINO_VECTOR, ReduceColumns
    from sn8_models import FLOOD_MODELS
    from sn8_stages import production_model
    make = FLOOD_MODELS[production_model()]
    m = make_pipeline(ReduceColumns(DINO_VECTOR), make()) if DINO_VECTOR[0] in cols else make()
    m.set_params(**{k: 1 for k in m.get_params(deep=True) if k.endswith("n_jobs")})
    return m


def fit_arms(D, names, seeds, done, pul=None):
    """Serial in-process fits (scv_common._task's rule: fit on the arm's kept training roads, call every held-out road).
    pul: {name: binned?} for the PUL arms (see pul_call)."""
    import scv_common as SC
    Bld = SC.builders()["S"]
    everyone = np.ones(len(D.y), bool)
    SC._init(D.X, D.y, D.S.model_name)
    todo = [(n, s) for s in seeds for n in names if f"{n}__{s}" not in done]
    K.log(T0, f"{len(todo)} fits to run")
    folds_cache = {}
    for i, (n, s) in enumerate(todo):
        if i % 20 == 0:
            K.wait_for_memory(T0)
        if s not in folds_cache:
            folds_cache[s] = D.S.subset_folds(everyone, Bld, s)
        spec = D.arms[n]
        if spec.get("pul") is not None:
            done[f"{n}__{s}"] = pul_call(D, spec, folds_cache[s], s)
        elif spec.get("proba"):
            done[f"{n}__{s}"] = proba_call(D, spec, folds_cache[s])
        else:
            _, call = SC._task(f"{n}__{s}", spec["cols"], [(tr[spec["gate"][tr]], te) for tr, te in folds_cache[s]])
            done[f"{n}__{s}"] = call
        if (i + 1) % 25 == 0:
            save_calls(done)
            K.log(T0, f"{i + 1}/{len(todo)} fits")
    save_calls(done)


def proba_call(D, spec, folds):
    """Production's rule on the predict_proba path (call = P(flooded) > 0.5): the reproduction check for PUL."""
    call = np.full(len(D.y), -1, np.int8)
    for tr, te in folds:
        fit = tr[spec["gate"][tr]]
        m = _model(spec["cols"]).fit(D.X.iloc[fit][spec["cols"]], D.y[fit])
        call[te] = (m.predict_proba(D.X.iloc[te][spec["cols"]])[:, 1] > 0.5).astype(np.int8)
    return call


PUL_BINS = (0.0, 0.01, 0.2, 1.01)


def pul_call(D, spec, folds, seed):
    """Li, Guo & Elkan 2011: g = p(s = 1 | x) fitted on 75% of the training-fold roads under the tile rule (s = y, as
    published), c = mean g over the held-out 25%'s labelled positives (eq. 4), flooded if g > 0.5 c (binned: c of the
    road's cloud-share bin; a bin with < 5 held-out positives uses the pooled c)."""
    share = D.roads.cloud_dark_rise_road.to_numpy()
    bins = np.digitize(share, PUL_BINS) - 1
    call = np.full(len(D.y), -1, np.int8)
    cs = []
    for k, (tr, te) in enumerate(folds):
        rows = tr[D.tile_rule[tr]]
        rng = np.random.default_rng([662, seed, k])
        v = rng.random(len(rows)) < 0.25
        fit, val = rows[~v], rows[v]
        m = _model(spec["cols"]).fit(D.X.iloc[fit][spec["cols"]], D.y[fit])
        gv = m.predict_proba(D.X.iloc[val][spec["cols"]])[:, 1]
        pos = D.y[val] == 1
        c = float(gv[pos].mean()) if pos.any() else 1.0
        cb = {}
        for b in range(len(PUL_BINS) - 1):
            sel = pos & (bins[val] == b)
            cb[b] = float(gv[sel].mean()) if sel.sum() >= 5 else c
        g = m.predict_proba(D.X.iloc[te][spec["cols"]])[:, 1]
        cut = np.array([cb[b] for b in bins[te]]) if spec["pul"] == "binned" else c
        call[te] = (g > 0.5 * cut).astype(np.int8)
        cs.append({"fold": k, "c": c, "c_bins": cb, "n_pos_val": int(pos.sum()),
                   "n_pos_val_bins": {b: int((pos & (bins[val] == b)).sum()) for b in range(len(PUL_BINS) - 1)}})
    D.pul_c.setdefault(seed, {})[spec["pul"]] = cs
    return call


def prod_calls(seeds):
    z = np.load(K.M1.SCV / "spatial_cv_flood_calls.npz")
    return np.stack([z[f"c00__S__{s}"] for s in seeds])


def reproduce(D, done):
    fit_arms(D, ["production (refit)"], [662], done)
    prod = prod_calls(K.M1.SEEDS)
    assert np.array_equal(done["production (refit)__662"], prod[0]), "STOP: production refit at 662 differs"
    from scv_common import counts
    cnt = counts(prod[0], D.y, D.gate_a)
    assert cnt == (378, 63, 103, 254), f"STOP: production counts {cnt}"
    K.log(T0, f"reproduction ok: production at 662 on the 798 = {cnt}")
    return prod


def holm(ps):
    """Holm-adjusted p-values for {name: p}."""
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def summarise(D, done, prod, names, base_name=None, label=""):
    """Screen at 662 + 21-seed averages vs production (and vs a base arm), added-road accuracy for gate arms."""
    y = D.y
    out = {}
    for n in names:
        spec = D.arms[n]
        gate = spec["gate"]
        calls = np.stack([done[f"{n}__{s}"] for s in K.M1.SEEDS])
        shared = gate & D.gate_a
        r = {"kept": int(gate.sum()), "kept_prod": int(D.gate_a.sum()),
             "screen": K.M1.paired_flood(calls[0], prod[0], y, shared, D.block),
             "seeds": K.M1.seed_avg(calls, prod, y, shared, D.block)}
        if not np.array_equal(gate, D.gate_a):
            add, rem = gate & ~D.gate_a, D.gate_a & ~gate
            r["added"], r["removed"] = int(add.sum()), int(rem.sum())
            if add.sum():
                ok = (calls[:, add] == y[add]).astype(float).mean(0)
                bt = K.M1.Boot(D.block, add)
                dist = bt.mean(ok)
                r["added_acc"] = {"mean": float(ok.mean()), "ci": [float(np.percentile(dist, 2.5)),
                                                                     float(np.percentile(dist, 97.5))],
                                  "flooded_share": float(y[add].mean())}
        if base_name and n != base_name:
            base = np.stack([done[f"{base_name}__{s}"] for s in K.M1.SEEDS])
            r["vs_base"] = {"base": base_name, "screen": K.M1.paired_flood(calls[0], base[0], y, shared, D.block),
                            "seeds": K.M1.seed_avg(calls, base, y, shared, D.block)}
        out[n] = r
        q = r["seeds"]
        K.log(T0, f"{label}{n:40s} kept {r['kept']:4d} 21-seed {100 * q['mean_gain']:+.2f} [{100 * q['ci'][0]:+.2f}, "
                  f"{100 * q['ci'][1]:+.2f}] better {q['seeds_better']} worse {q['seeds_worse']} "
                  f"McNemar662 p={r['screen']['mcnemar_p']:.3f}")
    return out


def st_flood(num):
    D = Data()
    done = load_calls()
    prod = reproduce(D, done)
    names = D.gate_names + ["C0 current two-date"] + D.corr_names + ["Q1 1/t on C0 current two-date"]
    fit_arms(D, names, K.M1.SEEDS, done)
    # production prod accuracy on its own roads (reference for added-road accuracy)
    okp = (prod[:, D.gate_a] == D.y[D.gate_a]).astype(float).mean(0)
    bt = K.M1.Boot(D.block, D.gate_a)
    dist = bt.mean(okp)
    num["prod_acc_kept"] = {"mean": float(okp.mean()), "ci": [float(np.percentile(dist, 2.5)),
                                                              float(np.percentile(dist, 97.5))]}
    flood = summarise(D, done, prod, D.gate_names, label="gate ")
    flood.update(summarise(D, done, prod, ["C0 current two-date"] + D.corr_names, base_name="C0 current two-date",
                           label="corr "))
    flood.update(summarise(D, done, prod, ["Q1 1/t on C0 current two-date"], base_name="C0 current two-date",
                           label="thr "))
    num["flood"] = flood
    num["u1_info"] = {"fcm_centres": D.u1["fcm_centres"].tolist(),
                      "certain_share_tile_rule": float(D.u1["certain"][D.tile_rule].mean()),
                      "certain_share_under_mask": float(D.u1["certain"][D.tile_rule & ~D.gate_a].mean())}
    write_kept(D)
    st_holm(num)


KEPT = K.HERE / "bench3_kept_roads.csv"


def write_kept(D):
    """Which of the 1,037 roads each arm assesses (its gate), for the notebooks; merged with what is already there."""
    old = pd.read_csv(KEPT) if KEPT.exists() else pd.DataFrame()
    new = pd.DataFrame({"tile_id": D.roads.tile_id.to_numpy(), "road_id": D.roads.road_id.to_numpy(),
                        "flooded": D.y, **{n: D.arms[n]["gate"].astype(int) for n in D.arms}})
    for c in old.columns:
        if c not in new.columns:
            new[c] = old[c].to_numpy()
    tmp = KEPT.with_suffix(".writing")
    new.to_csv(tmp, index=False)
    tmp.replace(KEPT)


def st_holm(num):
    ps = {}
    for n, r in num.get("flood", {}).items():
        ps[n] = r["screen"]["mcnemar_p"]
    num["holm_phaseG"] = holm(ps) if ps else {}


def st_pul(num):
    D = Data()
    D.pul_c = {}
    done = load_calls()
    prod = reproduce(D, done)
    D.arms["production (proba path)"] = {"gate": D.gate_a, "cols": list(D.cols), "proba": True}
    fit_arms(D, ["production (proba path)"], [662], done)
    assert np.array_equal(done["production (proba path)__662"], prod[0]), \
        "STOP: production on the predict_proba path (P > 0.5) differs from its calls; PUL not run"
    K.log(T0, "proba path reproduces production at 662")
    D.arms["PUL"] = {"gate": D.gate_a, "cols": list(D.cols), "pul": "single"}
    D.arms["PULb binned c"] = {"gate": D.gate_a, "cols": list(D.cols), "pul": "binned"}
    for n in ("PUL", "PULb binned c"):                              # PUL's c is a by-product: refit (not cached)
        for s in K.M1.SEEDS:
            done.pop(f"{n}__{s}", None)
    fit_arms(D, ["PUL", "PULb binned c"], K.M1.SEEDS, done)
    r = summarise(D, done, prod, ["PUL", "PULb binned c"], label="thr ")
    num.setdefault("flood", {}).update(r)
    num["pul_c"] = D.pul_c
    st_holm(num)


# ------------------------------------------------------------------------------------------------ combinations
def carry(num):
    """Top 2 per family by the family's primary metric (preregistered carry rule)."""
    fl = num["flood"]
    gates = sorted([n for n in fl if n in G_GATE_ARMS or n in U1_ARMS or n.startswith("T1d")],
                   key=lambda n: -fl[n]["seeds"]["mean_gain"])[:2]
    pri = num.get("ida_primary_vs_C0") or {}
    corr = [a for a in corr_arms()]
    def ckey(a):
        r = pri.get(a)
        if r:
            return (0 if r.get("guard_ok") else 1, r["mean_diff"])
        s = (num.get("ida_grey_err_thin_vs_C0") or {}).get(a)
        return (2, s["mean_diff"] if s else 1e9)
    corr = sorted(corr, key=ckey)[:2]
    thr = sorted([n for n in fl if n.startswith("Q1 1/t on C0") or n.startswith("PUL")],
                 key=lambda n: -fl[n]["seeds"]["mean_gain"])[:2]
    helped = {}
    for n in gates + thr:
        helped[n] = fl[n]["seeds"]["mean_gain"] >= 0
    for a in corr:
        r = pri.get(a)
        helped[a] = bool(r and r["ci"][1] < 0 and r.get("guard_ok")) or \
            (fl.get(a, {}).get("seeds", {}).get("mean_gain", -1) >= 0)
    return {"gate": gates, "corr": corr, "thr": thr, "exploratory": [n for n, h in helped.items() if not h]}


def st_combo(num):
    import itertools
    car = carry(num)
    num["carry"] = car
    K.log(T0, f"carried: {car}")
    D = Data()
    D.pul_c = {}
    done = load_calls()
    prod = reproduce(D, done)
    D.arms["PUL"] = {"gate": D.gate_a, "cols": list(D.cols), "pul": "single"}
    D.arms["PULb binned c"] = {"gate": D.gate_a, "cols": list(D.cols), "pul": "binned"}
    cells = {}
    for g, c, t in itertools.product([None] + car["gate"], [None] + car["corr"], [None] + car["thr"]):
        members = [m for m in (g, c, t) if m]
        if len(members) < 2:
            continue
        gate = D.arms[g]["gate"] if g else D.gate_a
        spec = {"gate": gate}
        if t and t.startswith("Q1"):
            base = c if c else "C0 current two-date"
            spec["cols"] = D.arms[f"Q1 1/t on {base}"]["cols"]
        else:
            spec["cols"] = D.arms[c]["cols"] if c else list(D.cols)
        if t and t.startswith("PUL"):
            spec["pul"] = D.arms[t]["pul"]
        name = "COMBO " + " + ".join(members)
        D.arms[name] = spec
        cells[name] = members
    fit_arms(D, list(cells), K.M1.SEEDS, done)
    y = D.y
    out = {}
    ps = {}
    for name, members in cells.items():
        calls = np.stack([done[f"{name}__{s}"] for s in K.M1.SEEDS])
        shared = D.arms[name]["gate"] & D.gate_a
        r = K.M1.seed_avg(calls, prod, y, shared, D.block)
        r["screen"] = K.M1.paired_flood(calls[0], prod[0], y, shared, D.block)
        ps[name] = r["screen"]["mcnemar_p"]
        okp = (prod[:, shared] == y[shared]).mean(0)
        inter = (calls[:, shared] == y[shared]).mean(0) - okp
        alone = {}
        for m in members:
            mc = np.stack([done[f"{m}__{s}"] for s in K.M1.SEEDS])
            alone[m] = K.M1.seed_avg(mc, prod, y, shared, D.block)
            inter = inter - ((mc[:, shared] == y[shared]).mean(0) - okp)
        dist = K.M1.Boot(D.block, shared).mean(inter)
        r["members"] = members
        r["members_alone_on_cell_roads"] = alone
        r["interaction"] = float(inter.mean())
        r["interaction_ci"] = [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]
        out[name] = r
        K.log(T0, f"{name}: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}], "
                  f"interaction {100 * r['interaction']:+.2f} [{100 * r['interaction_ci'][0]:+.2f}, "
                  f"{100 * r['interaction_ci'][1]:+.2f}]")
    num["combo"] = out
    num["holm_combo"] = holm(ps)
    write_kept(D)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    h0 = K.registry_hash()
    num = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {}
    steps = {"thresholds": st_thresholds, "tiles": st_tiles, "gates": st_gates, "ida": st_ida, "primary": st_primary,
             "score": st_score, "flood": st_flood, "pul": st_pul, "combo": st_combo}
    run = ["thresholds", "tiles", "gates", "ida", "primary", "score", "flood", "pul", "combo"] if stage == "all" \
        else stage.split(",")
    for s in run:
        K.log(T0, f"=== stage {s}")
        K.wait_for_memory(T0)
        steps[s](num)
        num["stages_done"] = sorted(set(num.get("stages_done", [])) | {s})
        K.write_json(NUMBERS, num)
        assert K.registry_hash() == h0, "production.json changed"
    K.log(T0, "done")


if __name__ == "__main__":
    main()
