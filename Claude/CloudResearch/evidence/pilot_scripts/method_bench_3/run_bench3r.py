"""Method bench 3, Phase R (RGB) runner (outputs/preregistration_method_bench_3.md, "Phase R"). Same machine rules as
Phase G (one process, 2 threads, memory gate, atomic writes, resumable). Reuses run_bench3's fit machinery with its own
calls file (BIG/bench3r_flood_calls.npz).

Stages (`all` = check tiles gates ida primary score flood pul combo greyrgb):
  check    R0's per-band code reproduces the road table's grey *_before and *_after columns (3 tiles) or the run stops.
  tiles    the 200 development tiles: R0 per-band rows, D1e / D1e-BR iHOT gates, A2b / A2b-noW / A2b-auto, ISFA cues,
           and the Phase-G carry-overs in RGB form (carry_R.json, written from the Phase G carry rule).
  ida      Ida secondary (grey = after grey + BT.601 of the RGB change, as bench 1's C5b) and gate rows.
  primary  DINOv2 (CPU) feature distance to NOAA in thin, 3-hour budget.
  flood    R0 reproduced (fits) -> every Phase R arm at 21 seeds, vs production and vs R0.
  pul      PUL / PULb on R0's columns (if carried).
  combo    carry rule within Phase R -> 3 x 3 x 3 factorial.
  greyrgb  best Phase G cell vs best Phase R cell (21 seeds, paired), and R0 vs production.
    OMP_NUM_THREADS=2 nice -n 10 python3 -I run_bench3r.py all > run_bench3r.log 2>&1
"""
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b3_common as K
import run_bench3 as RB

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

T0 = time.time()
RB.T0 = T0
TILES_DIR = K.BIG / "tiles_R"
CALLS_R = K.BIG / "bench3r_flood_calls.npz"
CALLS_G = RB.CALLS
NUMBERS = K.HERE / "bench3r_numbers.json"
CARRY = K.HERE / "carry_R.json"
A2B = {"A2b HOT lower-bound": {}, "A2b-noW no water proxy": {"water": False}, "A2b-auto MAD limit": {"auto": True}}
D1E = {"D1e IHOT-RGB": (0, 1, 2), "D1e-BR IHOT blue-red": (0, 2)}
KEPT = K.HERE / "bench3r_kept_roads.csv"


def carry_cfg():
    return json.loads(CARRY.read_text()) if CARRY.exists() else {"gates": [], "corr": [], "thr": []}


def grey_of(rgb_corr, after_rgb, after_grey, valid):
    """The grey copy: after grey + BT.601 of the RGB change (bench 1's C5b rule)."""
    g = after_grey + K.grey601(rgb_corr) - K.grey601(after_rgb.astype(np.float32))
    return np.where(valid, np.clip(g, 1, 255), 0).astype(np.float32)


def rgb_dark_rise(brgb, argb, valid):
    from sn8_clouds import dark_channel
    return dark_channel(argb.min(-1).astype(np.float32), valid) - dark_channel(brgb.min(-1).astype(np.float32), valid)


def carry_gate_masks(p, before, after, valid, cfg):
    """RGB forms of the carried Phase G gates (dark-rise family on the RGB dark channel)."""
    import g3_gates
    out = {}
    y = rgb_dark_rise(p["before_rgb"], p["after_rgb"], valid)
    for name in cfg.get("gates", []):
        key = RB.G_GATE_ARMS.get(name)
        if key is None:
            continue
        rn = f"RGB {name}"
        if key == "B1" or key.startswith("B2"):
            fit = g3_gates.b1_fit(y, valid)
            if fit["abstain"] is not None:
                out[rn] = np.zeros(valid.shape, bool)
            elif key == "B1":
                out[rn] = K.blob(K.hysteresis(y, valid, fit["t_l"], fit["t_h"]))
            else:
                out[rn] = K.icm(y, valid, fit["em"], float(key.split("-")[1]))[0]
        elif key == "B1p":
            TH = g3_gates.thresholds()
            bp = TH["B1p"]
            out[rn] = K.blob(K.hysteresis(y, valid, bp["t_l"], bp["t_h"]))
        elif key in ("T1", "T1b"):
            cut = carry_cfg().get("T1_rgb_cut")
            r, _ = blue_rise_clipped(p["before_rgb"], p["after_rgb"], valid)
            m = valid & (r > cut) if cut is not None else np.zeros(valid.shape, bool)
            out[rn] = K.blob(m) if key == "T1b" else m
    return out


def blue_rise_clipped(brgb, argb, valid):
    import g3_gates
    return g3_gates.grey_rise(brgb[..., 2].astype(np.float32), argb[..., 2].astype(np.float32), valid)


def tile_job(tid, cfg, out_dir=TILES_DIR):
    f = out_dir / f"{tid}.pkl"
    if f.exists():
        return
    from sn8_clouds import _maps, _tile
    from sn8_cloudspot import _strip, road_shares
    from sn8_lines import road_band
    from sn8_refhaze import dark_reference_dehaze
    import g3_corr, r3_arms as R
    K.dev_guard_tiles([tid])
    t1 = time.time()
    p, before, after, valid = _tile(tid)
    brgb, argb = p["before_rgb"], p["after_rgb"]
    band = road_band()
    strip, roads, n, centre_px = _strip(tid, p, valid, band)
    rise = _maps(p, valid)["masks"]["dark rise"]
    res = {"tile_id": tid, "valid_px": int(valid.sum()), "info": {}, "arms": {}, "road_shares": [], "cues": []}
    res["R0"] = R.band_rows(tid, p, valid, band, brgb, argb)
    masks = {"rise": rise}
    for name, bands in D1E.items():
        fld, inf = R.ihot(brgb, argb, valid, bands=bands)
        masks[name], ginf = R.ihot_gate(fld, valid)
        res["info"][name] = {**inf, **ginf}
    masks.update(carry_gate_masks(p, before, after, valid, cfg))
    extra = {}
    raw_rgb = argb.astype(np.float32)
    for name, kw in A2B.items():
        corr, cannot, inf = R.a2b(brgb, argb, valid, rise, **kw)
        res["info"][name] = inf
        if corr is None:
            res["arms"][name] = {"same": "raw"}
            extra[f"cannot|{name}"] = np.zeros(valid.shape, bool)
            continue
        extra[f"cannot|{name}"] = cannot
        res["arms"][name] = {"same": None, "rows": R.after_band_rows(tid, p, valid, band, brgb, corr),
                             "changed_px": int((np.abs(corr - raw_rgb).max(-1) > 0).sum())}
    c0 = dark_reference_dehaze(before, after, valid)
    tmaps = {}
    want = [a for a in cfg.get("corr", []) if a in g3_corr.ARMS]
    if want and c0["gate"].any():
        outs = g3_corr.outputs(before, after, valid, c0, only=want, after_rgb=argb, before_rgb=brgb)
        for a, o in outs.items():
            rn = f"RGB {a}"
            tmaps[f"t_{rn}"] = np.where(valid, o["t"], 1.0)
            if np.array_equal(o["corrected"], np.where(valid[..., None], raw_rgb, 0)):
                res["arms"][rn] = {"same": "raw"}
            else:
                res["arms"][rn] = {"same": None, "rows": R.after_band_rows(tid, p, valid, band, brgb, o["corrected"]),
                                   "info": o["info"]}
    iw, s1, iinf = R.isfa(brgb, argb, valid, rise)
    res["info"]["ISFA"] = iinf
    sg = R.sfa_grey(before, after, valid)
    if n:
        cue = {"isfa_iwd": iw if iw is not None else np.full(valid.shape, np.nan),
               "isfa_sfa1": s1 if s1 is not None else np.full(valid.shape, np.nan), "sfa_grey": sg}
        rows = road_shares(tid, strip, roads, n, centre_px, {k: np.nan_to_num(v, nan=0.0) for k, v in cue.items()})
        if iw is None:
            for r in rows:
                r["isfa_iwd"] = np.nan
                r["isfa_sfa1"] = np.nan
        res["cues"] = rows
        res["road_shares"] = road_shares(tid, strip, roads, n, centre_px, {**masks, **extra, **tmaps})
    res["tile_share"] = {k: float(m[valid].mean()) for k, m in {**masks, **extra}.items()}
    res["seconds"] = time.time() - t1
    out_dir.mkdir(parents=True, exist_ok=True)
    K.atomic_bytes(f, pickle.dumps(res))
    K.log(T0, f"{tid}: {res['seconds']:.0f} s, shares { {k: round(v, 3) for k, v in res['tile_share'].items()} }")


def st_carry(num):
    """carry_R.json from Phase G's carry rule (bench3_numbers.json 'carry'); T1's RGB form (the blue rise, otsu1979
    handoff step 2 as written) gets its pooled cut by the same rule as Phase G (integer Otsu, eta >= 0.65, else p99 on
    production-clear pixels)."""
    g = json.loads(RB.NUMBERS.read_text())["carry"]
    cfg = {"gates": g["gate"], "corr": g["corr"], "thr": g["thr"], "from": "bench3_numbers.json carry (Phase G)"}
    if any(RB.G_GATE_ARMS.get(x) in ("T1", "T1b") for x in g["gate"]):
        from sn8_clouds import _maps, _tile
        import g3_gates
        vals, clear = [], []
        for tid in K.train_tiles():
            K.wait_for_memory(T0)
            p, b, a, v = _tile(tid)
            r, _ = blue_rise_clipped(p["before_rgb"], p["after_rgb"], v)
            rm = _maps(p, v)["masks"]["dark rise"]
            vals.append(r[v][::16]); clear.append(r[v & ~rm][::16])
        o = K.otsu_int(np.concatenate(vals))
        p99 = float(np.percentile(np.concatenate(clear), 99))
        cfg["T1_rgb"] = {**o, "p99_clear": p99, "accepted": o["eta_star"] >= g3_gates.ETA_MIN}
        cfg["T1_rgb_cut"] = o["k_star"] if o["eta_star"] >= g3_gates.ETA_MIN else p99
    if any(x.startswith("U1") for x in g["gate"]):
        cfg["note_U1"] = "U1 carried: its RGB form (CVA over 3 bands, G-statistic averaged over bands) is not coded; " \
                         "U1 stays grey in Phase R (logged as a deviation)"
    CARRY.write_text(json.dumps(K.M1.plain(cfg), indent=1))
    num["carry_from_G"] = cfg
    K.log(T0, f"carry_R.json: {cfg}")


def st_check(num):
    from sn8_clouds import _tile
    from sn8_heldout import touched_roads
    from sn8_lines import road_band
    import r3_arms as R
    roads = touched_roads(include_cloudy=True)
    for tid in K.SMOKE_TILES:
        p, b, a, v = _tile(tid)
        g3b = np.repeat(p["before_grey"][..., None], 3, -1)
        g3a = np.repeat(p["after_grey"][..., None], 3, -1)
        rb, ra = R.band_rows(tid, p, v, road_band(), g3b, g3a)["R"]
        rt = roads[roads.tile_id == tid].reset_index(drop=True)
        cols = [c for c in pd.DataFrame(ra).columns if c.endswith("_after")]
        db = np.nanmax(np.abs(pd.DataFrame(rb)[cols].to_numpy(float) -
                              rt[[c.replace("_after", "_before") for c in cols]].to_numpy(float)))
        da = np.nanmax(np.abs(pd.DataFrame(ra)[cols].to_numpy(float) - rt[cols].to_numpy(float)))
        assert db < 1e-6 and da < 1e-6, f"STOP: per-band code does not reproduce the grey road table on {tid} " \
                                        f"(before {db}, after {da})"
        K.log(T0, f"check {tid}: per-band code == road table (before {db:.1e}, after {da:.1e})")
    num["check"] = "passed on 3 smoke tiles"


def st_tiles(num):
    cfg = carry_cfg()
    order, _ = RB.dev_tiles()
    for i, tid in enumerate(order):
        if (TILES_DIR / f"{tid}.pkl").exists():
            continue
        K.wait_for_memory(T0)
        try:
            tile_job(tid, cfg)
        except Exception as e:
            import traceback
            traceback.print_exc()
            K.log(T0, f"{tid}: ERROR {e!r}")
        if (i + 1) % 10 == 0:
            K.log(T0, f"{i + 1}/{len(order)} tiles")


def load_tiles():
    order, roads = RB.dev_tiles()
    return {t: pickle.loads((TILES_DIR / f"{t}.pkl").read_bytes()) for t in order if (TILES_DIR / f"{t}.pkl").exists()}


def st_gates(num):
    from sn8_refhaze import clear_tiles
    res = load_tiles()
    clear = [t for t in clear_tiles() if t in res]
    keys = [k for k in res[clear[0]]["tile_share"] if not k.startswith("cannot|")]
    out = {"clear_tiles_scored": len(clear)}
    for k in keys:
        v = np.array([res[t]["tile_share"].get(k, 0.0) for t in clear])
        out[k] = {"mean": float(v.mean()), "tiles_over_1pct": int((v > 0.01).sum())}
    out["abstain"] = {k: pd.Series([str((res[t]["info"].get(k) or {}).get("abstain")) for t in res]).value_counts()
                      .to_dict() for k in list(D1E) + list(A2B) + ["ISFA"]}
    num["gates_clear_tiles"] = out
    K.log(T0, f"gates: {json.dumps(K.M1.plain(out))}")


def ida_outputs_R(p, before, after, valid, cfg):
    """{arm: {"corrected": grey copy, "gate"/"opaque" for C0}} for C0 (grey) and each Phase R correction."""
    from sn8_clouds import _maps
    from sn8_refhaze import dark_reference_dehaze
    import g3_corr, r3_arms as R
    c0 = dark_reference_dehaze(before, after, valid)
    outs = {"C0": c0}
    brgb, argb = p["before_rgb"], p["after_rgb"]
    rise = _maps(p, valid)["masks"]["dark rise"]
    for name, kw in A2B.items():
        corr, _, _ = R.a2b(brgb, argb, valid, rise, **kw)
        if corr is not None:
            outs[name] = {"corrected": grey_of(corr, argb, after, valid)}
    want = [a for a in cfg.get("corr", []) if a in g3_corr.ARMS]
    if want and c0["gate"].any():
        for a, o in g3_corr.outputs(before, after, valid, c0, only=want, after_rgb=argb, before_rgb=brgb).items():
            outs[f"RGB {a}"] = {"corrected": grey_of(o["corrected"], argb, after, valid)}
    return outs


def st_ida(num):
    from sn8_clouds import _tile
    import run_ida_helpers as H
    import r3_arms as R
    cfg = carry_cfg()
    sec_f, gat_f = K.HERE / "ida_rows_secondary_R.csv", K.HERE / "ida_rows_gates_R.csv"
    sec = pd.read_csv(sec_f) if sec_f.exists() else pd.DataFrame(columns=["tile_id"])
    gat = pd.read_csv(gat_f) if gat_f.exists() else pd.DataFrame(columns=["tile_id"])
    tiles = H.usable_tiles()
    K.dev_guard_tiles(tiles)
    for t in tiles:
        if t in set(sec.tile_id):
            continue
        K.wait_for_memory(T0)
        p, before, after, valid = _tile(t)
        z = np.load(H.PREP / f"{t}.npz", allow_pickle=True)
        dis, cut = RB.R2()._noaa_disagreement(z, after, valid)
        masks = {}
        for name, bands in D1E.items():
            fld, _ = R.ihot(p["before_rgb"], p["after_rgb"], valid, bands=bands)
            masks[name], _ = R.ihot_gate(fld, valid)
        masks.update(carry_gate_masks(p, before, after, valid, cfg))
        grow = []
        for k, mk in masks.items():
            m = mk & z["score"]
            grow.append({"tile_id": t, "mask": k, "flagged": int(m.sum()), "disagree": int(dis.sum()),
                         "tp": int((m & dis).sum()), "cut": cut})
        outs = ida_outputs_R(p, before, after, valid, cfg)
        c0 = outs["C0"]
        thin = z["score"] & c0["gate"] & ~c0["opaque"]
        rows = []
        if thin.sum() < RB.MIN_THIN:
            rows.append({"tile_id": t, "arm": "-", "region": "thin", "px": int(thin.sum())})
        else:
            d = ndi.distance_transform_edt(~c0["gate"])
            ring = z["score"] & ~c0["gate"] & (d > 0) & (d <= RB.RING_PX) & ~z["bright"]
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
    import torch._dynamo  # noqa: F401  (deviation 2: import before the patch; torch._dynamo reads __wrapped__)
    torch.backends.mps.is_available = lambda: False
    torch.set_num_threads(2)
    import run_ida_helpers as H
    from sn8_clouds import _tile
    cfg = carry_cfg()
    sec = pd.read_csv(K.HERE / "ida_rows_secondary_R.csv")
    pri_f = K.HERE / "ida_rows_primary_R.csv"
    pri = pd.read_csv(pri_f) if pri_f.exists() else pd.DataFrame(columns=["tile_id"])
    spent_f = K.HERE / "ida_primary_spent_R.txt"
    spent = float(spent_f.read_text()) if spent_f.exists() else 0.0
    th = sec[(sec.region == "thin") & (sec.arm != "-")].groupby("tile_id").px.first().sort_values(ascending=False)
    for t in th.index:
        if t in set(pri.tile_id):
            continue
        if spent >= RB.BUDGET_S:
            K.log(T0, f"primary budget spent ({spent:.0f} s); stopping before {t}")
            break
        K.wait_for_memory(T0)
        t1 = time.time()
        p, before, after, valid = _tile(t)
        outs = ida_outputs_R(p, before, after, valid, cfg)
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
    sec = pd.read_csv(K.HERE / "ida_rows_secondary_R.csv")
    sec = sec[sec.arm != "-"]
    arms = [a for a in sec.arm.unique() if a != "C0"]
    num["ida_secondary_tiles"] = int(sec.tile_id.nunique())
    for metric in ("grey_err", "edge_r"):
        for region in ("thin", "ring"):
            num[f"ida_{metric}_{region}_vs_C0"] = {a: paired_tiles(sec, metric, region, a) for a in arms}
    num["ida_guard_grey_change_mean"] = sec[sec.region == "guard"].groupby("arm").grey_change.mean().to_dict()
    g = pd.read_csv(K.HERE / "ida_rows_gates_R.csv")
    num["ida_gates"] = {k: {"tiles": int(len(v)), "precision_pooled": float(v.tp.sum() / max(v.flagged.sum(), 1)),
                            "recall_pooled": float(v.tp.sum() / max(v.disagree.sum(), 1))} for k, v in g.groupby("mask")}
    pf = K.HERE / "ida_rows_primary_R.csv"
    if pf.exists():
        pri = pd.read_csv(pf)
        num["ida_primary_tiles"] = sorted(pri.tile_id.unique().tolist())
        gc = num["ida_guard_grey_change_mean"]
        num["ida_primary_vs_C0"] = {}
        for a in [x for x in pri.arm.unique() if x != "C0"]:
            r = paired_tiles(pri, "feat", "thin", a)
            if r:
                r["guard_ok"] = bool(abs(gc.get(a, 0) - gc.get("C0", 0)) <= 1.0)
            num["ida_primary_vs_C0"][a] = r


# ------------------------------------------------------------------------------------------------ flood
class DataR(RB.Data):
    """Phase G's Data (production columns, gates, grey corrected blocks) plus R0's per-band columns, the Phase R gate
    masks, the RGB corrected blocks and the ISFA cues."""

    def __init__(self):
        super().__init__()
        from sn8_clouds import ROAD_CLOUD_CUT
        from sn8_dino import DINO_CUES
        res = load_tiles()
        tiles = sorted(self.roads.tile_id[self.tile_rule].unique())
        missing = [t for t in tiles if t not in res]
        assert not missing, f"Phase R pickles missing: {len(missing)}"
        al_ = RB.R2()._align
        metrics = sorted({c[: -len("_after")] for c in self.after_cols})
        # R0 columns
        r0 = {}
        for bnd in ("R", "G", "B"):
            bt = pd.concat([pd.DataFrame(res[t]["R0"][bnd][0]) for t in tiles if res[t]["R0"][bnd][0]], ignore_index=True)
            at = pd.concat([pd.DataFrame(res[t]["R0"][bnd][1]) for t in tiles if res[t]["R0"][bnd][1]], ignore_index=True)
            ab, aa = al_(self.roads, bt), al_(self.roads, at)
            for m in metrics:
                r0[f"{bnd}_{m}_before"] = ab[f"{m}_after"].to_numpy()
                r0[f"{bnd}_{m}_after"] = aa[f"{m}_after"].to_numpy()
                r0[f"{bnd}_{m}_change"] = r0[f"{bnd}_{m}_after"] - r0[f"{bnd}_{m}_before"]
        for c, v in r0.items():
            self.X["r0_" + c] = v
        self.r0_feats = ["r0_" + c for c in r0]
        self.r0_cols = self.r0_feats + list(DINO_CUES)
        hit = np.isfinite(self.X[self.r0_feats[0]].to_numpy())
        assert hit[self.tile_rule].all(), "R0 rows missing for tile-rule roads"
        self.arms["R0 colour baseline"] = {"gate": self.gate_a, "cols": self.r0_cols}
        # Phase R gates
        sh = pd.concat([pd.DataFrame(res[t]["road_shares"]) for t in tiles if res[t]["road_shares"]], ignore_index=True)
        al = al_(self.roads, sh)
        assert np.abs(np.nan_to_num(al.rise.to_numpy()) - np.nan_to_num(self.shares.rise.to_numpy())).max() < 1e-9
        self.r_gate_names = []
        for k in [c for c in al.columns if c in D1E or c.startswith("RGB ") and not c.startswith("t_")]:
            if k.startswith("t_"):
                continue
            self.arms[k] = {"gate": self.tile_rule & (al[k].to_numpy() < ROAD_CLOUD_CUT), "cols": self.r0_cols}
            self.r_gate_names.append(k)
        # corrections (per-band after rows) on R0's columns
        self.r_corr_names = []
        for j, name in enumerate(list(A2B) + [f"RGB {a}" for a in carry_cfg().get("corr", [])]):
            parts = {bnd: [] for bnd in ("R", "G", "B")}
            for t in tiles:
                x = res[t]["arms"].get(name)
                if x and x.get("same") is None and x.get("rows"):
                    for bnd in parts:
                        parts[bnd].append(pd.DataFrame(x["rows"][bnd]))
            tcol = f"t_{name}"
            tbar = np.nan_to_num(al[tcol].to_numpy(), nan=1.0) if tcol in al.columns else None
            gate = self.gate_a
            if f"cannot|{name}" in al.columns:
                gate = self.gate_a & (np.nan_to_num(al[f"cannot|{name}"].to_numpy()) < ROAD_CLOUD_CUT)
            self._add_r(name, f"rc{j}_", parts, None, gate)
            self.r_corr_names.append(name)
            if tbar is not None:
                self._add_r(f"Q1 1/t on {name}", f"rq{j}_", parts, np.maximum(tbar, 0.2), gate)
        # ISFA cues
        cu = pd.concat([pd.DataFrame(res[t]["cues"]) for t in tiles if res[t]["cues"]], ignore_index=True)
        ca = al_(self.roads, cu)
        for c in ("isfa_iwd", "isfa_sfa1", "sfa_grey"):
            v = ca[c].to_numpy(float)
            med = np.nanmedian(v[self.tile_rule])
            self.X["cue_" + c] = np.where(np.isfinite(v), v, med)
        self.arms["ISFA-RGB IWD + SFA1"] = {"gate": self.gate_a, "cols": self.r0_cols + ["cue_isfa_iwd", "cue_isfa_sfa1"]}
        self.arms["ISFA-grey control"] = {"gate": self.gate_a, "cols": self.r0_cols + ["cue_sfa_grey"]}
        self.r_thr_names = ["ISFA-RGB IWD + SFA1", "ISFA-grey control"]
        self.isfa_abstain_roads = int((~np.isfinite(ca.isfa_iwd.to_numpy(float)) & self.tile_rule).sum())

    def _add_r(self, name, pre, parts, scale, gate):
        cols = []
        for bnd, ps in parts.items():
            after = {f"{bnd}_{m}_after": self.X[f"r0_{bnd}_{m}_after"].to_numpy().copy()
                     for m in {c[: -len("_after")] for c in self.after_cols}}
            hit = np.zeros(len(self.y), bool)
            if ps:
                al = RB.R2()._align(self.roads, pd.concat(ps, ignore_index=True))
                hit = al[self.after_cols[0]].notna().to_numpy()
                for c in self.after_cols:
                    after[f"{bnd}_{c}"][hit] = al.loc[hit, c].to_numpy()
            for m in {c[: -len("_after")] for c in self.after_cols}:
                a = after[f"{bnd}_{m}_after"]
                ch = a - self.X[f"r0_{bnd}_{m}_before"].to_numpy()
                if scale is not None:
                    ch = np.where(hit, ch * scale, ch)
                self.X[f"{pre}{bnd}_{m}_after"] = a
                self.X[f"{pre}{bnd}_{m}_change"] = ch
                cols += [f"{pre}{bnd}_{m}_after", f"{pre}{bnd}_{m}_change"]
        self.arms[name] = {"gate": gate, "cols": self.r0_cols + cols}


def write_kept(D):
    old = pd.read_csv(KEPT) if KEPT.exists() else pd.DataFrame()
    new = pd.DataFrame({"tile_id": D.roads.tile_id.to_numpy(), "road_id": D.roads.road_id.to_numpy(),
                        "flooded": D.y, **{n: D.arms[n]["gate"].astype(int) for n in D.arms}})
    for c in old.columns:
        if c not in new.columns:
            new[c] = old[c].to_numpy()
    tmp = KEPT.with_suffix(".writing")
    new.to_csv(tmp, index=False)
    tmp.replace(KEPT)


def st_flood(num):
    RB.CALLS = CALLS_R
    D = DataR()
    done = RB.load_calls()
    prod = RB.reproduce(D, done)
    names = ["R0 colour baseline"] + D.r_gate_names + D.r_corr_names + \
        [n for n in D.arms if n.startswith("Q1 1/t on ") and (n[len("Q1 1/t on "):] in D.r_corr_names)] + D.r_thr_names
    RB.fit_arms(D, names, K.M1.SEEDS, done)
    num["flood"] = RB.summarise(D, done, prod, names, base_name="R0 colour baseline", label="R ")
    num["isfa_abstain_roads"] = D.isfa_abstain_roads
    write_kept(D)
    num["holm_phaseR"] = RB.holm({n: r["screen"]["mcnemar_p"] for n, r in num["flood"].items()})


def st_pul(num):
    if not any(t.startswith("PUL") for t in carry_cfg().get("thr", [])):
        K.log(T0, "PUL not carried into Phase R: skipped")
        return
    RB.CALLS = CALLS_R
    D = DataR()
    D.pul_c = {}
    done = RB.load_calls()
    prod = RB.reproduce(D, done)
    names = []
    for t in carry_cfg()["thr"]:
        if t.startswith("PUL"):
            n = f"RGB {t}"
            D.arms[n] = {"gate": D.gate_a, "cols": D.r0_cols, "pul": "binned" if "binned" in t else "single"}
            names.append(n)
    RB.fit_arms(D, names, K.M1.SEEDS, done)
    num.setdefault("flood", {}).update(RB.summarise(D, done, prod, names, base_name="R0 colour baseline", label="R "))
    num["pul_c"] = D.pul_c


def carry_R(num):
    fl = num["flood"]
    gate_c = [n for n in fl if n in D1E or n.startswith("RGB ") and n[4:] in RB.G_GATE_ARMS]
    gates = sorted(gate_c, key=lambda n: -fl[n]["seeds"]["mean_gain"])[:2]
    pri = num.get("ida_primary_vs_C0") or {}
    corr_c = [n for n in fl if n in A2B or (n.startswith("RGB ") and not n[4:] in RB.G_GATE_ARMS
                                            and not n.startswith("RGB PUL"))]

    def ckey(a):
        r = pri.get(a)
        if r:
            return (0 if r.get("guard_ok") else 1, r["mean_diff"])
        s = (num.get("ida_grey_err_thin_vs_C0") or {}).get(a)
        return (2, s["mean_diff"] if s else 1e9)
    corr = sorted(corr_c, key=ckey)[:2]
    thr_c = [n for n in fl if n.startswith("ISFA") or n.startswith("RGB PUL") or n.startswith("Q1 1/t on")]
    thr = sorted(thr_c, key=lambda n: -fl[n]["seeds"]["mean_gain"])[:2]
    return {"gate": gates, "corr": corr, "thr": thr}


def st_combo(num):
    import itertools
    RB.CALLS = CALLS_R
    car = carry_R(num)
    num["carry"] = car
    K.log(T0, f"carried (R): {car}")
    D = DataR()
    D.pul_c = {}
    done = RB.load_calls()
    prod = RB.reproduce(D, done)
    for t in carry_cfg().get("thr", []):
        if t.startswith("PUL"):
            D.arms[f"RGB {t}"] = {"gate": D.gate_a, "cols": D.r0_cols, "pul": "binned" if "binned" in t else "single"}
    cells = {}
    for g, c, t in itertools.product([None] + car["gate"], [None] + car["corr"], [None] + car["thr"]):
        members = [m for m in (g, c, t) if m]
        if len(members) < 2:
            continue
        spec = {"gate": D.arms[g]["gate"] if g else D.gate_a}
        if c:                       # deviation 4 fix: apply only the correction's own cannot-assess rule (A2b), not
            spec["gate"] = spec["gate"] & (D.arms[c]["gate"] | ~D.gate_a)   # production's gate on top of the gate arm
        cols = D.arms[c]["cols"] if c else list(D.r0_cols)
        if t and t.startswith("Q1 1/t on"):
            base = c if c else t[len("Q1 1/t on "):]
            cols = D.arms.get(f"Q1 1/t on {base}", D.arms[t])["cols"]
        elif t and t.startswith("ISFA"):
            cols = cols + [x for x in D.arms[t]["cols"] if x.startswith("cue_")]
        if t and t.startswith("RGB PUL"):
            spec["pul"] = D.arms[t]["pul"]
        spec["cols"] = cols
        name = "COMBO R " + " + ".join(members)
        D.arms[name] = spec
        cells[name] = members
    RB.fit_arms(D, list(cells), K.M1.SEEDS, done)
    y = D.y
    out, ps = {}, {}
    r0 = np.stack([done[f"R0 colour baseline__{s}"] for s in K.M1.SEEDS])
    for name, members in cells.items():
        calls = np.stack([done[f"{name}__{s}"] for s in K.M1.SEEDS])
        shared = D.arms[name]["gate"] & D.gate_a
        r = K.M1.seed_avg(calls, prod, y, shared, D.block)
        r["vs_R0"] = K.M1.seed_avg(calls, r0, y, shared, D.block)
        r["screen"] = K.M1.paired_flood(calls[0], prod[0], y, shared, D.block)
        ps[name] = r["screen"]["mcnemar_p"]
        ok0 = (r0[:, shared] == y[shared]).mean(0)
        inter = (calls[:, shared] == y[shared]).mean(0) - ok0
        for m in members:
            mc = np.stack([done[f"{m}__{s}"] for s in K.M1.SEEDS])
            inter = inter - ((mc[:, shared] == y[shared]).mean(0) - ok0)
        dist = K.M1.Boot(D.block, shared).mean(inter)
        r.update(members=members, interaction_vs_R0=float(inter.mean()),
                 interaction_ci=[float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))])
        out[name] = r
        K.log(T0, f"{name}: gain {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}] vs prod; "
                  f"vs R0 {100 * r['vs_R0']['mean_gain']:+.2f}; interaction {100 * r['interaction_vs_R0']:+.2f}")
    num["combo"] = out
    num["holm_combo"] = RB.holm(ps)
    write_kept(D)


def st_greyrgb(num):
    """Best Phase G cell vs best Phase R cell (highest 21-seed gain vs production), paired over 21 seeds."""
    numG = json.loads(RB.NUMBERS.read_text())
    candG = {**{n: r["seeds"] for n, r in numG["flood"].items()}, **numG.get("combo", {})}
    candR = {**{n: r["seeds"] for n, r in num["flood"].items()}, **num.get("combo", {})}
    bestG = max(candG, key=lambda n: candG[n]["mean_gain"])
    bestR = max(candR, key=lambda n: candR[n]["mean_gain"])
    zG, zR = np.load(CALLS_G), np.load(CALLS_R)
    RB.CALLS = CALLS_R
    D = DataR()
    cg = np.stack([zG[f"{bestG}__{s}"] for s in K.M1.SEEDS])
    cr = np.stack([zR[f"{bestR}__{s}"] for s in K.M1.SEEDS])
    gkeep = pd.read_csv(RB.KEPT)[bestG].to_numpy().astype(bool) if bestG in pd.read_csv(RB.KEPT).columns else D.gate_a
    rkeep = pd.read_csv(KEPT)[bestR].to_numpy().astype(bool) if bestR in pd.read_csv(KEPT).columns else D.gate_a
    shared = gkeep & rkeep & D.gate_a
    r = K.M1.seed_avg(cr, cg, D.y, shared, D.block)
    r["screen"] = K.M1.paired_flood(cr[0], cg[0], D.y, shared, D.block)
    prod = RB.prod_calls(K.M1.SEEDS)
    r0 = np.stack([zR[f"R0 colour baseline__{s}"] for s in K.M1.SEEDS])
    num["grey_vs_rgb"] = {"best_grey": bestG, "best_rgb": bestR, "rgb_minus_grey": r,
                          "R0_vs_production": K.M1.seed_avg(r0, prod, D.y, D.gate_a, D.block)}
    K.log(T0, f"grey vs RGB: {bestR} minus {bestG}: {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, "
              f"{100 * r['ci'][1]:+.2f}]")


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    h0 = K.registry_hash()
    num = json.loads(NUMBERS.read_text()) if NUMBERS.exists() else {}
    steps = {"carry": st_carry, "check": st_check, "tiles": st_tiles, "gates": st_gates, "ida": st_ida, "primary": st_primary,
             "score": st_score, "flood": st_flood, "pul": st_pul, "combo": st_combo, "greyrgb": st_greyrgb}
    run = ["carry", "check", "tiles", "gates", "ida", "primary", "score", "flood", "pul", "combo", "greyrgb"] \
        if stage == "all" else stage.split(",")
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
