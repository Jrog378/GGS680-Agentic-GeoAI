"""Method bench 2, the full run (outputs/preregistration_method_bench_2.md), strictly serial: one process, 2 threads, no
multiprocessing, no GPU. Every stage is resumable (per-tile pickles, cached calls) and checks production.json's sha256
before and after. Before every tile it waits while free memory < 30% or swap > 4 GB (b2_common.wait_for_memory).

Stages (`all` runs: thresholds, tiles, gates, ida, primary, score, screen, seeds, combo; primary waits for the
DINOv3 job, the Ida chain and bench 1 to end, amendment 2026-10-30):
  1 thresholds   G2's T_blue: Otsu on the pooled training-tile blue rise (every 16th valid pixel), cached.
  2 tiles        every one of the 200 development tiles kept by the tile rule (C0's gate tiles first): C0, the G masks
                 and their road shares (+ the production dark-rise share, reproduced against cloud_dark_rise_road), and
                 for every correction arm its corrected after image -> bench 1's after_rows (the 93 non-DINOv2 after
                 columns). Per-tile pickles in BIG/tiles/.
  3 gates        (a): G masks' false-alarm share on the clear development tiles, road coverage vs production.
  4 ida          (b) secondary: correction arms vs the NOAA reference on the Ida prep tiles (read-only), and (a) the
                 gate masks vs grey disagreement > the guard's 99th percentile.
  5 screen       (c) flood calls at seed 662 for every arm (production reproduced first: 378/63/103/254 or stop).
  6 seeds        (c) the arms not worse at 662 (gain >= -0.5 points) at all 21 seeds.
  7 combo        stage winners (preregistered rule) -> combined corrected images (BIG/combo/) -> 21-seed factorial.
  8 primary      (b) primary: DINOv2 feature distance to NOAA on the CPU (no MPS), 3-hour budget.
  score          writes bench2_numbers.json from whatever stages have finished (Ida statistics as bench 1's ida_score).
Dry run (no results written outside BIG/dry/): `dry <tile>` times one tile's full stage-2 job.

    cd evidence/pilot_scripts/method_bench_2
    OMP_NUM_THREADS=2 nice -n 10 python3 -I run_bench2.py all > run_bench2.log 2>&1
"""
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_common as B

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

T0 = time.time()
TILES_DIR = B.BIG / "tiles"
COMBO_DIR = B.BIG / "combo"
CALLS = B.BIG / "bench2_flood_calls.npz"
NUMBERS = B.HERE / "bench2_numbers.json"
DARKREF_CACHE = "road_corrected_darkref_c1fd17d88e15c874.csv"
NOT_WORSE = -0.005
MIN_THIN = 2000
RING_PX = 80
BUDGET_S = 3 * 3600

N_ARMS = ["N1 Du PIF", "N1b Du PIF no water removal", "N2 Schott roofs+roads", "N2b Schott roofs",
          "N2c Schott roofs+roads no eps check", "N3 Lin wPCA", "N3 Lin wPCA bounded", "N4 Song ridge all",
          "N4 Song ridge all bounded", "N4b Song ridge clear"]
A_ARMS = [f"A1 Chavez k={k}" for k in (0.0, 0.5, 0.7, 1.0, 2.0)]
GC_ARMS = ["G1 hysteresis corr-gate", "G1b hysteresis+blob corr-gate", "G1c hysteresis centred corr-gate",
           "G2 Lin blue rise corr-gate"]
GC_KEY = {"G1 hysteresis corr-gate": "G1", "G1b hysteresis+blob corr-gate": "G1b",
          "G1c hysteresis centred corr-gate": "G1c", "G2 Lin blue rise corr-gate": "G2"}
C_ARMS = N_ARMS + A_ARMS + GC_ARMS                     # correction arms: scored by after-date columns
G_ARMS = {"G1 hysteresis road-gate": "G1", "G1b hysteresis+blob road-gate": "G1b",
          "G1c hysteresis centred road-gate": "G1c", "G2 Lin blue rise road-gate": "G2"}


# ------------------------------------------------------------------------------------------------ arms on one tile
def masks_for(p, before, after, valid, T_blue):
    import g1_hysteresis, g2_lin_bluerise
    from sn8_clouds import _maps
    m = {"rise": _maps(p, valid)["masks"]["dark rise"]}
    info = {}
    m["G1"], info["G1"] = g1_hysteresis.gate(before, after, valid, None)
    m["G1b"], info["G1b"] = g1_hysteresis.gate(before, after, valid, 2500.0)
    m["G1c"], info["G1c"] = g1_hysteresis.gate(before, after, valid, None, centred=True)
    m["G2"], _, info["G2"] = g2_lin_bluerise.gate(p["before_rgb"], p["after_rgb"], valid, T_blue)
    return m, info


def arm_outputs(tid, p, before, after, valid, masks, only=None):
    """{arm: output dict} for C0 and every correction arm (only=list restricts). Gate-tile logic as bench 1: tone and
    airlight arms act only where C0's gate exists; G corr-gate arms act where their own mask exists."""
    import a1_chavez, n1_du, n2_schott, n3_lin, n4_ridge
    from c_common import darkref_variant
    from sn8_refhaze import dark_reference_dehaze
    want = (lambda a: True) if only is None else (lambda a: a in only)
    c0 = dark_reference_dehaze(before, after, valid)
    outs = {"C0": c0}
    if c0["gate"].any():
        fp = n2_schott.footprints(tid, p, valid.shape, valid) if any(want(a) for a in N_ARMS if a.startswith("N2")) \
            else None
        rgb_b, rgb_a = p["before_rgb"], p["after_rgb"]
        fns = {"N1 Du PIF": lambda: n1_du.correct(before, after, valid),
               "N1b Du PIF no water removal": lambda: n1_du.correct(before, after, valid, water=False),
               "N2 Schott roofs+roads": lambda: n2_schott.correct(tid, p, before, after, valid, False, masks=fp),
               "N2b Schott roofs": lambda: n2_schott.correct(tid, p, before, after, valid, True, masks=fp),
               "N2c Schott roofs+roads no eps check": lambda: n2_schott.correct(tid, p, before, after, valid, False,
                                                                                masks=fp, check=False),
               "N3 Lin wPCA": lambda: n3_lin.correct(before, after, valid, rgb_b, rgb_a),
               "N3 Lin wPCA bounded": lambda: n3_lin.correct(before, after, valid, rgb_b, rgb_a, bound=True),
               "N4 Song ridge all": lambda: n4_ridge.correct(before, after, valid, False),
               "N4 Song ridge all bounded": lambda: n4_ridge.correct(before, after, valid, False, bound=True),
               "N4b Song ridge clear": lambda: n4_ridge.correct(before, after, valid, True)}
        for a, fn in fns.items():
            if want(a):
                outs[a] = fn()
        for a, k in zip(A_ARMS, a1_chavez.K):
            if want(a):
                outs[a] = a1_chavez.correct(before, after, valid, rgb_a, c0, k)
    for a in GC_ARMS:
        key = GC_KEY[a]
        if want(a) and masks[key].any():
            outs[a] = darkref_variant(before, after, valid, gate=masks[key])
    return outs


def tile_job(tid, T_blue, out_dir=TILES_DIR):
    f = out_dir / f"{tid}.pkl"
    if f.exists():
        return
    from after_features import after_rows
    from sn8_clouds import _tile
    from sn8_cloudspot import _strip, road_shares
    from sn8_lines import road_band
    B.dev_guard_tiles([tid])
    t1 = time.time()
    p, before, after, valid = _tile(tid)
    masks, minfo = masks_for(p, before, after, valid, T_blue)
    band = road_band()
    strip, roads, n, centre_px = _strip(tid, p, valid, band)
    res = {"tile_id": tid, "valid_px": int(valid.sum()), "mask_info": minfo,
           "tile_share": {k: float(v[valid].mean()) for k, v in masks.items()},
           "road_shares": road_shares(tid, strip, roads, n, centre_px, masks) if n else [], "arms": {}}
    outs = arm_outputs(tid, p, before, after, valid, masks)
    raw = np.where(valid, after, 0).astype(np.float32)
    c0 = outs["C0"]["corrected"]
    res["C0_rows"] = after_rows(tid, {**p, "after_grey": c0}, valid, band) if not np.array_equal(c0, raw) else None
    res["c0_diag"] = {"gate_px": int(outs["C0"]["gate"].sum()), "opaque_px": int(outs["C0"]["opaque"].sum())}
    for a in C_ARMS:
        o = outs.get(a)
        if o is None:
            res["arms"][a] = {"same": "raw"}
            continue
        img = o["corrected"]
        info = {k: v for k, v in (o.get("info") or {}).items() if k != "passes"}
        diag = {"gate_px": int(o["gate"].sum()), "opaque_px": int(o["opaque"].sum()),
                "changed_px": int((img != raw).sum()), "info": info}
        if np.array_equal(img, raw):
            res["arms"][a] = {"same": "raw", **diag}
        elif np.array_equal(img, c0):
            res["arms"][a] = {"same": "c0", **diag}
        else:
            res["arms"][a] = {"same": None, "rows": after_rows(tid, {**p, "after_grey": img}, valid, band), **diag}
    res["seconds"] = time.time() - t1
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".writing")
    tmp.write_bytes(pickle.dumps(res))
    tmp.replace(f)
    B.log(T0, f"{tid}: {res['seconds']:.0f} s, C0 gate {res['c0_diag']['gate_px']} px, "
              f"shares {({k: round(v, 4) for k, v in res['tile_share'].items()})}")


def dev_tiles():
    from sn8_heldout import touched_roads
    roads = touched_roads(include_cloudy=True)
    assert set(roads.split) <= {"train", "val"} and len(roads) == 1037
    tiles = sorted(roads.tile_id[~roads.cloudy.astype(bool)].unique())
    B.dev_guard_tiles(tiles)
    assert len(tiles) == 200
    from sn8_refhaze import CACHE_DIR
    gate_tiles = sorted(pd.read_csv(CACHE_DIR / DARKREF_CACHE).tile_id.unique())
    assert len(gate_tiles) == 99, len(gate_tiles)
    return gate_tiles + [t for t in tiles if t not in set(gate_tiles)], roads


# ------------------------------------------------------------------------------------------------ stages
def st_thresholds():
    import g2_lin_bluerise
    T = g2_lin_bluerise.threshold(T0)
    B.log(T0, f"G2 T_blue = {T:.3f}")
    return T


def st_tiles():
    import g2_lin_bluerise
    T = g2_lin_bluerise.threshold(T0)
    order, _ = dev_tiles()
    for i, tid in enumerate(order):
        if (TILES_DIR / f"{tid}.pkl").exists():
            continue
        B.wait_for_memory(T0)
        try:
            tile_job(tid, T)
        except Exception as e:
            import traceback
            traceback.print_exc()
            B.log(T0, f"{tid}: ERROR {e!r}")
        if (i + 1) % 10 == 0:
            B.log(T0, f"{i + 1}/{len(order)} tiles")


def load_tiles():
    order, roads = dev_tiles()
    res = {}
    for t in order:
        f = TILES_DIR / f"{t}.pkl"
        if f.exists():
            res[t] = pickle.loads(f.read_bytes())
    return res, order, roads


def st_gates(num):
    from sn8_refhaze import clear_tiles
    res, order, roads = load_tiles()
    clear = [t for t in clear_tiles() if t in res]
    out = {"clear_tiles_scored": len(clear)}
    for k in ("rise", "G1", "G1b", "G1c", "G2"):
        v = np.array([res[t]["tile_share"][k] for t in clear])
        out[f"clear_share_{k}"] = {"mean": float(v.mean()) if len(v) else None,
                                   "median": float(np.median(v)) if len(v) else None,
                                   "tiles_over_1pct": int((v > 0.01).sum())}
    num["gates_clear_tiles"] = out
    B.log(T0, f"clear-tile false-alarm shares: {out}")


def _noaa_disagreement(z, after, valid):
    s, guard, noaa, asis = z["score"], z["guard"], z["noaa"], z["asis"]
    d = np.abs(asis - noaa)
    cut = float(np.percentile(d[guard], 99))
    return s & (d > cut), cut


def st_ida():
    from sn8_clouds import _tile
    import g2_lin_bluerise
    import run_ida_helpers as H
    T = g2_lin_bluerise.threshold(T0)
    sec_f = B.HERE / "ida_rows_secondary.csv"
    gat_f = B.HERE / "ida_rows_gates.csv"
    sec = pd.read_csv(sec_f) if sec_f.exists() else pd.DataFrame(columns=["tile_id"])
    gat = pd.read_csv(gat_f) if gat_f.exists() else pd.DataFrame(columns=["tile_id"])
    tiles = H.usable_tiles()
    B.dev_guard_tiles(tiles)
    B.log(T0, f"{len(tiles)} usable Ida prep tiles")
    for t in tiles:
        if t in set(sec.tile_id):
            continue
        B.wait_for_memory(T0)
        p, before, after, valid = _tile(t)
        masks, _ = masks_for(p, before, after, valid, T)
        z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
        dis, cut = _noaa_disagreement(z, after, valid)
        grow = []
        for k in ("rise", "G1", "G1b", "G1c", "G2"):
            m = masks[k] & z["score"]
            tp = int((m & dis).sum())
            grow.append({"tile_id": t, "mask": k, "flagged": int(m.sum()), "disagree": int(dis.sum()), "tp": tp,
                         "precision": tp / max(int(m.sum()), 1), "recall": tp / max(int(dis.sum()), 1), "cut": cut})
        gat = pd.concat([gat, pd.DataFrame(grow)], ignore_index=True)
        gat.to_csv(gat_f, index=False)
        outs = arm_outputs(t, p, before, after, valid, masks)
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
        sec = pd.concat([sec, pd.DataFrame(rows)], ignore_index=True)
        sec.to_csv(sec_f, index=False)
        B.log(T0, f"Ida {t}: thin {int(thin.sum())} px")


# ------------------------------------------------------------------------------------------------ flood calls
def _align(roads, tab):
    t = tab.copy()
    t["_n"] = t.groupby(["tile_id", "road_id"]).cumcount()
    r = roads[["tile_id", "road_id"]].copy()
    r["_n"] = r.groupby(["tile_id", "road_id"]).cumcount()
    return r.merge(t, on=["tile_id", "road_id", "_n"], how="left").drop(columns=["_n"])


class Data:
    def __init__(self, combo_rows=None):
        from scv_common import Setup
        from sn8_clouds import ROAD_CLOUD_CUT
        S = Setup(build_x=False)
        self.S, self.roads, self.y, self.cols = S, S.roads, S.y, S.cols
        self.gate_a, self.tile_rule, self.block = S.gates["a"], S.tile_rule, S.block
        self.X = S.roads[self.cols].copy()
        self.arms = {"production (refit)": (self.gate_a, list(self.cols))}
        res, _, _ = load_tiles()
        tiles = sorted(self.roads.tile_id[self.tile_rule].unique())
        missing = [t for t in tiles if t not in res]
        assert not missing, f"tile pickles missing: {len(missing)}"
        # gate arms: road shares, reproduction of cloud_dark_rise_road first
        sh = pd.concat([pd.DataFrame(res[t]["road_shares"]) for t in tiles if res[t]["road_shares"]], ignore_index=True)
        al = _align(self.roads, sh)
        hit = al["rise"].notna().to_numpy()
        gap = np.abs(al.rise.to_numpy()[hit] - self.roads.cloud_dark_rise_road.to_numpy()[hit]).max()
        assert gap < 1e-9, f"STOP: dark-rise share does not reproduce cloud_dark_rise_road ({gap})"
        assert ((self.tile_rule & hit) == self.tile_rule).all(), "road shares missing for kept-tile roads"
        assert ((self.tile_rule & (al.rise.to_numpy() < ROAD_CLOUD_CUT)) == self.gate_a).all()
        for name, k in G_ARMS.items():
            self.arms[name] = (self.tile_rule & (al[k].to_numpy() < ROAD_CLOUD_CUT), list(self.cols))
        # correction arms: after columns
        from sn8_glcm import GLCM_FEATURES
        from sn8_roads import FEATURES
        from sn8_texture import TEXTURE_FEATURES
        feats = FEATURES + GLCM_FEATURES + TEXTURE_FEATURES
        assert len(feats) == 93
        self.feats = feats
        after_cols = [c for c in feats if c.endswith("_after")]
        self.after_cols = after_cols
        raw = self.roads[["tile_id", "road_id"] + feats].reset_index(drop=True)
        self.raw = raw
        tabs = {a: [] for a in ["C0"] + C_ARMS}
        for t in tiles:
            r = res[t]
            c0 = pd.DataFrame(r["C0_rows"]) if r["C0_rows"] else None
            if c0 is not None:
                tabs["C0"].append(c0)
            for a in C_ARMS:
                x = r["arms"][a]
                if x["same"] == "c0" and c0 is not None:
                    tabs[a].append(c0)
                elif x["same"] is None:
                    tabs[a].append(pd.DataFrame(x["rows"]))
        for i, (a, parts) in enumerate(tabs.items()):
            self._add(("C0 current two-date" if a == "C0" else a), f"tb{i}_", parts)
        if combo_rows:
            for j, (name, parts) in enumerate(combo_rows.items()):
                self._add(name, f"tbc{j}_", parts)

    def _add(self, name, pre, parts):
        td = self.raw.copy()
        if parts:
            al = _align(self.roads, pd.concat(parts, ignore_index=True))
            hit = al[self.after_cols[0]].notna().to_numpy()
            for c in self.after_cols:
                td.loc[hit, c] = al.loc[hit, c].to_numpy()
        for m in {c[: -len("_after")] for c in self.after_cols}:
            td[f"{m}_change"] = td[f"{m}_after"] - td[f"{m}_before"]
        for c in self.feats:
            self.X[pre + c] = td[c].to_numpy()
        self.arms[name] = (self.gate_a, list(self.cols) + [pre + c for c in self.feats])


def load_calls():
    if not CALLS.exists():
        return {}
    z = np.load(CALLS)
    return {k: z[k] for k in z.files}


def save_calls(d):
    tmp = B.BIG / "bench2_flood_calls_writing.npz"
    np.savez_compressed(tmp, **d)
    tmp.replace(CALLS)


def fit_arms(D, names, seeds, done):
    """Serial, in-process (scv_common._task with forest n_jobs = 1): no process pool."""
    import scv_common as SC
    Bld = SC.builders()["S"]
    everyone = np.ones(len(D.y), bool)
    SC._init(D.X, D.y, D.S.model_name)
    todo = [(n, s) for s in seeds for n in names if f"{n}__{s}" not in done]
    B.log(T0, f"{len(todo)} fits to run")
    folds_cache = {}
    for i, (n, s) in enumerate(todo):
        B.wait_for_memory(T0)
        if s not in folds_cache:
            folds_cache[s] = D.S.subset_folds(everyone, Bld, s)
        gate, cols = D.arms[n]
        key, call = SC._task(f"{n}__{s}", cols, [(tr[gate[tr]], te) for tr, te in folds_cache[s]])
        done[key] = call
        if (i + 1) % 10 == 0:
            save_calls(done)
            B.log(T0, f"{i + 1}/{len(todo)} fits")
    save_calls(done)


def prod_calls(seeds):
    z = np.load(B.M1.SCV / "spatial_cv_flood_calls.npz")
    return np.stack([z[f"c00__S__{s}"] for s in seeds])


def reproduce(D, done):
    fit_arms(D, ["production (refit)"], [662], done)
    prod = prod_calls(B.M1.SEEDS)
    assert np.array_equal(done["production (refit)__662"], prod[0]), "STOP: production refit at 662 differs"
    from scv_common import counts
    cnt = counts(prod[0], D.y, D.gate_a)
    assert cnt == (378, 63, 103, 254), f"STOP: production counts {cnt}"
    B.log(T0, f"reproduction ok: production at 662 on the 798 = {cnt}")
    return prod


def st_screen(num):
    D = Data()
    done = load_calls()
    prod = reproduce(D, done)
    names = [n for n in D.arms if n != "production (refit)"]
    fit_arms(D, names, [662], done)
    scr = {}
    y = D.y
    for n in names:
        gate = D.arms[n][0]
        r = {"kept": int(gate.sum()), "kept_prod": int(D.gate_a.sum()),
             "paired_shared": B.M1.paired_flood(done[f"{n}__662"], prod[0], y, gate & D.gate_a, D.block)}
        if not np.array_equal(gate, D.gate_a):
            r["added"], r["removed"] = int((gate & ~D.gate_a).sum()), int((D.gate_a & ~gate).sum())
        if n in C_ARMS:
            r["vs_C0"] = B.M1.paired_flood(done[f"{n}__662"], done["C0 current two-date__662"], y, D.gate_a, D.block)
        scr[n] = r
        q = r["paired_shared"]
        B.log(T0, f"{n:34s} kept {r['kept']:4d} gain {100 * q['gain']:+.2f} [{100 * q['ci'][0]:+.2f}, "
                  f"{100 * q['ci'][1]:+.2f}] fixed {q['fixed']} broken {q['broken']} p={q['mcnemar_p']:.3f}")
    num["screen"] = scr


def st_seeds(num):
    D = Data()
    done = load_calls()
    prod = reproduce(D, done)
    scr = num["screen"]
    go = [n for n in scr if scr[n]["paired_shared"]["gain"] >= NOT_WORSE]
    if "C0 current two-date" not in go:
        go.append("C0 current two-date")                    # needed for the vs-C0 comparison
    B.log(T0, f"21-seed arms: {go}")
    fit_arms(D, go, B.M1.SEEDS, done)
    sd = {}
    for n in go:
        calls = np.stack([done[f"{n}__{s}"] for s in B.M1.SEEDS])
        sd[n] = B.M1.seed_avg(calls, prod, D.y, D.arms[n][0] & D.gate_a, D.block)
        if n in C_ARMS:
            c0 = np.stack([done[f"C0 current two-date__{s}"] for s in B.M1.SEEDS])
            sd[n]["vs_C0"] = B.M1.seed_avg(calls, c0, D.y, D.gate_a, D.block)
        r = sd[n]
        B.log(T0, f"{n:34s} 21 seeds: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, "
                  f"{100 * r['ci'][1]:+.2f}] better {r['seeds_better']} worse {r['seeds_worse']}")
    num["seeds"] = sd


def stage_of(n):
    return "G" if n.startswith("G") else "N" if n.startswith("N") else "A" if n.startswith("A") else None


def select_winners(num):
    """Preregistered: helped alone = own-metric interval excluding 0 in the good direction (Ida primary, if run) OR
    21-seed flood gain >= 0; per stage G/N/A the largest 21-seed gain among those (ties: listed first)."""
    own = {}
    for arm, r in (num.get("ida_primary_vs_C0") or {}).items():
        if r:
            own[arm] = bool(r["ci"][1] < 0 and r.get("guard_ok", True))
    sd = num.get("seeds", {})
    helped = {n: {"flood_not_worse": r["mean_gain"] >= 0, "own_metric": own.get(n, False)} for n, r in sd.items()
              if n != "C0 current two-date"}
    for h in helped.values():
        h["helped"] = h["flood_not_worse"] or h["own_metric"]
    listed = list(G_ARMS) + C_ARMS
    winner = {}
    for s in ("G", "N", "A"):
        cand = [n for n in listed if n in helped and helped[n]["helped"] and stage_of(n) == s]
        winner[s] = max(cand, key=lambda n: (sd[n]["mean_gain"], -listed.index(n))) if cand else None
    return {"helped": helped, "winner": winner}


def combo_image(tid, p, before, after, valid, masks, parts):
    """One corrected image for a combination of winners: G corr-gate (gate), N (tone_fn), A (airlight link)."""
    import a1_chavez, n1_du, n2_schott, n3_lin, n4_ridge
    from c_common import darkref_variant
    gate = None
    for n in parts:
        if n in GC_ARMS:
            gate = masks[GC_KEY[n]]
    tone_fn = None
    for n in parts:
        if n.startswith("N1"):
            tone_fn = n1_du.make_tone_fn(water=(n == "N1 Du PIF"))
        elif n.startswith("N2"):
            bld, road = n2_schott.footprints(tid, p, valid.shape, valid)
            tone_fn = n2_schott.make_tone_fn(bld if n == "N2b Schott roofs" else bld | road,
                                             check=not n.startswith("N2c"))
        elif n.startswith("N3"):
            tone_fn = n3_lin.make_tone_fn(p["before_rgb"], p["after_rgb"], bound=n.endswith("bounded"))
        elif n.startswith("N4"):
            tone_fn = n4_ridge.make_tone_fn(n == "N4b Song ridge clear", bound=n.endswith("bounded"))
    o = darkref_variant(before, after, valid, tone_fn=tone_fn, gate=gate)
    for n in parts:
        if n in A_ARMS:
            o = a1_chavez.correct(before, after, valid, p["after_rgb"], o, float(n.split("=")[1]))
    return o


def st_combo(num):
    import itertools
    import g2_lin_bluerise
    from after_features import after_rows
    from sn8_clouds import _tile
    from sn8_lines import road_band
    win = select_winners(num)
    num["winners"] = win
    picks = {s: n for s, n in win["winner"].items() if n}
    B.log(T0, f"winners: {picks}")
    if len(picks) < 2:
        B.log(T0, "fewer than two stage winners: no combination to test")
        return
    stages = sorted(picks)
    combos = [c for r in range(2, len(stages) + 1) for c in itertools.combinations(stages, r)]
    # images: road-gate G winners change kept roads, not images; corr-gate G, N and A winners change the image
    img_combos = {}
    for c in combos:
        parts = [picks[s] for s in c if not picks[s].endswith("road-gate")]
        if len(parts) >= 2:
            img_combos["IMG " + " + ".join(parts)] = parts
    T = g2_lin_bluerise.threshold(T0)
    order, _ = dev_tiles()
    band = road_band()
    for tid in order:
        f = COMBO_DIR / f"{tid}.pkl"
        if f.exists() or not img_combos:
            continue
        B.wait_for_memory(T0)
        p, before, after, valid = _tile(tid)
        masks, _ = masks_for(p, before, after, valid, T)
        res = {}
        for name, parts in img_combos.items():
            o = combo_image(tid, p, before, after, valid, masks, parts)
            img = o["corrected"]
            res[name] = None if np.array_equal(img, np.where(valid, after, 0)) else \
                after_rows(tid, {**p, "after_grey": img}, valid, band)
        COMBO_DIR.mkdir(parents=True, exist_ok=True)
        f.write_bytes(pickle.dumps(res))
    combo_rows = {n: [] for n in img_combos}
    for tid in order:
        f = COMBO_DIR / f"{tid}.pkl"
        if f.exists():
            for n, rows in pickle.loads(f.read_bytes()).items():
                if rows:
                    combo_rows[n].append(pd.DataFrame(rows))
    D = Data(combo_rows)
    done = load_calls()
    prod = reproduce(D, done)
    final = {}
    for c in combos:
        members = [picks[s] for s in c]
        img_parts = [m for m in members if not m.endswith("road-gate")]
        gate = D.gate_a.copy()
        for m in members:
            if m.endswith("road-gate"):
                gate = D.arms[m][0]
        cols = D.arms["IMG " + " + ".join(img_parts)][1] if len(img_parts) >= 2 else \
            (D.arms[img_parts[0]][1] if img_parts else list(D.cols))
        name = "COMBO " + " + ".join(members)
        D.arms[name] = (gate, cols)
        final[name] = members
    need = list(final) + [picks[s] for s in stages]
    fit_arms(D, need, B.M1.SEEDS, done)
    out = {}
    y = D.y
    for name, members in final.items():
        calls = np.stack([done[f"{name}__{s}"] for s in B.M1.SEEDS])
        shared = D.arms[name][0] & D.gate_a
        for m in members:
            shared &= D.arms[m][0]
        r = B.M1.seed_avg(calls, prod, y, shared, D.block)
        alone = {m: np.stack([done[f"{m}__{s}"] for s in B.M1.SEEDS]) for m in members}
        bt = B.M1.Boot(D.block, shared)
        okp = (prod[:, shared] == y[shared]).mean(0)
        inter = (calls[:, shared] == y[shared]).mean(0) - okp - sum((alone[m][:, shared] == y[shared]).mean(0) - okp
                                                                      for m in members)
        dist = bt.mean(inter)
        r["members"] = {m: B.M1.seed_avg(alone[m], prod, y, shared, D.block) for m in members}
        r["interaction"] = float(inter.mean())
        r["interaction_ci"] = [float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))]
        out[name] = r
        B.log(T0, f"{name}: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}], "
                  f"interaction {100 * r['interaction']:+.2f}")
    num["combo"] = out


OTHER_JOBS = ("spatialcv_gpu.py", "s3_score.py", "ida_clear_view", "method_bench/run_", "run_corr.py", "run_ida.py",
              "run_flood.py", "run_hrc.py", "run_texture.py", "run_d3.py")


def wait_for_other_jobs(poll_s=300):
    """Amendment 2026-10-30: the primary runs only after the DINOv3 job, the Ida chain and bench 1 have finished."""
    import subprocess
    while True:
        busy = [j for j in OTHER_JOBS if subprocess.run(["pgrep", "-f", j], capture_output=True).returncode == 0]
        if not busy:
            return
        B.log(T0, f"primary waiting for: {busy}")
        time.sleep(poll_s)


def st_primary(num):
    """DINOv2 feature distance to NOAA in thin, CPU only (MPS disabled), 2 threads, BUDGET_S of token time; starts only
    when the DINOv3 job, the Ida chain and bench 1 have ended (wait_for_other_jobs)."""
    wait_for_other_jobs()
    import torch
    torch.backends.mps.is_available = lambda: False          # no GPU, whatever else is running
    torch.set_num_threads(2)
    import run_ida_helpers as H
    from sn8_clouds import _tile
    import g2_lin_bluerise
    T = g2_lin_bluerise.threshold(T0)
    sec = pd.read_csv(B.HERE / "ida_rows_secondary.csv")
    pri_f = B.HERE / "ida_rows_primary.csv"
    pri = pd.read_csv(pri_f) if pri_f.exists() else pd.DataFrame(columns=["tile_id"])
    spent_f = B.HERE / "ida_primary_spent.txt"
    spent = float(spent_f.read_text()) if spent_f.exists() else 0.0
    th = sec[(sec.region == "thin") & (sec.arm != "-")].groupby("tile_id").px.first().sort_values(ascending=False)
    for t in th.index:
        if t in set(pri.tile_id):
            continue
        if spent >= BUDGET_S:
            B.log(T0, f"primary budget spent ({spent:.0f} s); stopping before {t}")
            break
        B.wait_for_memory(T0)
        t1 = time.time()
        p, before, after, valid = _tile(t)
        masks, _ = masks_for(p, before, after, valid, T)
        outs = arm_outputs(t, p, before, after, valid, masks)
        z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
        c0 = outs["C0"]
        s = z["score"]
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
        pri.to_csv(pri_f, index=False)
        B.log(T0, f"primary {t}: {time.time() - t1:.0f} s (spent {spent:.0f} s)")


def st_score(num):
    """Ida statistics as bench 1's ida_score.paired_tiles (imported), on bench 2's rows."""
    from ida_score import paired_tiles
    sf = B.HERE / "ida_rows_secondary.csv"
    if sf.exists():
        sec = pd.read_csv(sf)
        sec = sec[sec.arm != "-"]
        arms = [a for a in sec.arm.unique() if a != "C0"]
        num["ida_secondary_tiles"] = int(sec.tile_id.nunique())
        for metric in ("grey_err", "edge_r"):
            for region in ("thin", "ring"):
                num[f"ida_{metric}_{region}_vs_C0"] = {a: paired_tiles(sec, metric, region, a) for a in arms}
        num["ida_guard_grey_change_mean"] = sec[sec.region == "guard"].groupby("arm").grey_change.mean().to_dict()
    gf = B.HERE / "ida_rows_gates.csv"
    if gf.exists():
        g = pd.read_csv(gf)
        num["ida_gates"] = {k: {"tiles": int(len(v)), "precision_pooled": float(v.tp.sum() / max(v.flagged.sum(), 1)),
                                "recall_pooled": float(v.tp.sum() / max(v.disagree.sum(), 1))}
                            for k, v in g.groupby("mask")}
    pf = B.HERE / "ida_rows_primary.csv"
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


def st_dry(tid):
    """Times one tile's stage-2 job into BIG/dry/ (not read by any scoring stage)."""
    import g2_lin_bluerise
    from sn8_clouds import _tile
    from skimage.filters import threshold_otsu
    B.dev_guard_tiles([tid])
    T = json.loads(g2_lin_bluerise.T_FILE.read_text())["T_blue"] if g2_lin_bluerise.T_FILE.exists() else None
    if T is None:                     # dry run only: a provisional threshold from this tile (never used for results)
        p, _, _, valid = _tile(tid)
        r, _ = g2_lin_bluerise.blue_rise(p["before_rgb"], p["after_rgb"], valid)
        T = float(threshold_otsu(r[valid][::16]))
        B.log(T0, f"dry: provisional T_blue {T:.2f} from {tid} (dry run only)")
    d = B.BIG / "dry"
    f = d / f"{tid}.pkl"
    if f.exists():
        f.unlink()
    t1 = time.time()
    tile_job(tid, T, out_dir=d)
    res = pickle.loads(f.read_bytes())
    n_rows = sum(1 for a in res["arms"].values() if a.get("same") is None)
    B.log(T0, f"dry {tid}: {time.time() - t1:.0f} s total; {n_rows} arms needed new feature rows; "
              f"{len(res['road_shares'])} roads with shares")


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    h0 = B.registry_hash()
    if stage == "dry":
        st_dry(sys.argv[2])
        assert B.registry_hash() == h0
        return
    num = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {}
    steps = {"thresholds": lambda: st_thresholds(), "tiles": st_tiles, "gates": lambda: st_gates(num),
             "ida": st_ida, "screen": lambda: st_screen(num), "seeds": lambda: st_seeds(num),
             "combo": lambda: st_combo(num), "primary": lambda: st_primary(num), "score": lambda: st_score(num)}
    run = ["thresholds", "tiles", "gates", "ida", "primary", "score", "screen", "seeds", "combo"] if stage == "all" \
        else [stage]
    for s in run:
        B.log(T0, f"=== stage {s}")
        steps[s]()
        num["stages_done"] = sorted(set(num.get("stages_done", [])) | {s})
        B.write_json(NUMBERS, num)
        assert B.registry_hash() == h0, "production.json changed"
    B.log(T0, "done")


if __name__ == "__main__":
    main()
