"""Visual cache for the pre-run notebooks (notebooks/method_bench_3/): the chosen development tiles' images, masks,
NOAA view, road strips and the cached flood calls, so the notebooks only load and plot (no heavy work).

Tile choice (the preregistered rule, fixed before any result): from the Ida prep tiles with a NOAA view, (1) thin cloud
= the largest thin-cloud area (score & C0 gate & t >= 0.2, from ida_rows_secondary.csv), (2) thick cloud = the largest
C0 opaque share, (3) clear = a clear development tile with the most touched roads, (4) flooded = the development tile
with the most roads labelled flooded among C0 gate tiles, (5)-(6) the smoke tiles 2_23_44 and 2_19_55 if not chosen.
    OMP_NUM_THREADS=2 nice -n 10 python3 -I nb_cache.py G > nb_cache_G.log 2>&1
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

T0 = time.time()
OUT = K.BIG / "nb"


def choose_tiles():
    import run_bench3 as RB
    import run_ida_helpers as H
    from sn8_heldout import touched_roads
    from sn8_refhaze import clear_tiles
    sec = pd.read_csv(K.HERE / "ida_rows_secondary.csv")
    ida = set(H.usable_tiles())
    thin = sec[(sec.region == "thin")].groupby("tile_id").px.first()
    res, _, _ = RB.load_tiles()
    roads = touched_roads(include_cloudy=True)
    pick = {}
    pick["thin cloud"] = str(thin.idxmax())
    op = {t: res[t]["c0_diag"]["opaque_px"] / res[t]["valid_px"] for t in res if t in ida}
    pick["thick cloud"] = max(op, key=op.get)
    n_roads = roads.groupby("tile_id").size()
    cl = [t for t in clear_tiles() if t in ida and t in n_roads.index]
    pick["clear"] = max(cl, key=lambda t: (n_roads[t], t))
    gate_tiles = [t for t in res if res[t]["c0_diag"]["gate_px"] > 0]
    fl = roads[roads.tile_id.isin(gate_tiles)].groupby("tile_id").flooded.sum()
    pick["flooded"] = str(fl.idxmax())
    chosen = []
    for k, t in pick.items():
        if t not in [c[1] for c in chosen]:
            chosen.append((k, t))
    for t in ("2_23_44", "2_19_55"):
        if t not in [c[1] for c in chosen]:
            chosen.append(("smoke tile", t))
    K.dev_guard_tiles([t for _, t in chosen])
    return chosen, {"thin_px": {t: int(thin.get(t, 0)) for _, t in chosen},
                    "opaque_share": {t: float(op.get(t, np.nan)) for _, t in chosen},
                    "flooded_roads": {t: int(fl.get(t, 0)) for _, t in chosen},
                    "roads": {t: int(n_roads.get(t, 0)) for _, t in chosen}}


def u8(x):
    return np.clip(np.rint(x), 0, 255).astype(np.uint8)


def road_index(tid, roads_tab):
    """Positions in the 1,037-road table of this tile's roads in strip order (tile_id, road_id, occurrence)."""
    r = roads_tab[roads_tab.tile_id == tid]
    occ = r.groupby("road_id").cumcount()
    return {(rid, int(o)): int(i) for rid, o, i in zip(r.road_id, occ, r.index)}


def tile_cache(kind, tid, phase, calls, arm_names, roads_tab, TH):
    from sn8_clouds import _tile
    from sn8_cloudspot import _strip
    from sn8_lines import road_band
    from sn8_refhaze import dark_reference_dehaze
    import run_ida_helpers as H
    import g3_corr, g3_gates
    p, b, a, v = _tile(tid)
    masks, _ = g3_gates.masks(p, b, a, v, TH)
    c0 = dark_reference_dehaze(b, a, v)
    outs = g3_corr.outputs(b, a, v, c0)
    arr = {"before": u8(b), "after": u8(a), "valid": v, "C0": u8(c0["corrected"]), "t_C0": u8(255 * np.nan_to_num(c0["t"], nan=1)),
           "c0_gate": c0["gate"], "c0_opaque": c0["opaque"]}
    for k, m in masks.items():
        arr[f"mask|{k}"] = m
    for k, o in outs.items():
        arr[f"img|{k}"] = u8(o["corrected"])
        arr[f"t|{k}"] = u8(255 * o["t"])
    arr["before_rgb"], arr["after_rgb"] = p["before_rgb"].astype(np.uint8), p["after_rgb"].astype(np.uint8)
    f = H.PREP / f"{tid}.npz"
    if f.exists():
        z = np.load(f, allow_pickle=True)
        if z["row"].item().get("coreg_ok") and "score" in z.files:
            arr["noaa"], arr["noaa_score"], arr["noaa_rgb"] = u8(z["noaa"]), z["score"], z["noaa_rgb"]
    strip, roads, n, cpx = _strip(tid, p, v, road_band())
    arr["strip"] = (strip if strip is not None else np.zeros(v.shape)).astype(np.int16)
    idx = road_index(tid, roads_tab)
    rows = []
    occ = {}
    from sn8_roads import MIN_ROAD_PX
    for k in range(n):
        rid = roads[k + 1]["road_id"]
        o = occ.get(rid, 0)
        if cpx[k] < MIN_ROAD_PX:
            continue
        occ[rid] = o + 1
        i = idx.get((rid, o))
        if i is None:
            continue
        row = {"strip_id": k + 1, "road_row": i, "road_id": rid, "flooded": int(roads_tab.flooded.iloc[i])}
        for name in arm_names:
            key0 = f"{name}__662"
            if key0 in calls:
                row[f"call662|{name}"] = int(calls[key0][i])
                seeds = [calls[f"{name}__{s}"][i] for s in K.M1.SEEDS if f"{name}__{s}" in calls]
                row[f"share21|{name}"] = float(np.mean([x == 1 for x in seeds if x >= 0])) if seeds else np.nan
        rows.append(row)
    OUT.mkdir(parents=True, exist_ok=True)
    K.atomic_npz(OUT / f"{phase}_{tid}.npz", **arr)
    pd.DataFrame(rows).to_csv(OUT / f"{phase}_{tid}_roads.csv", index=False)
    K.log(T0, f"{phase} {kind} {tid}: {len(rows)} roads, NOAA {'noaa' in arr}")


def tile_cache_R(kind, tid, calls, arm_names, roads_tab, cfg):
    """Phase R images: RGB before/after, A2b variants and the RGB carry-over corrections (RGB and their grey copies),
    the iHOT field and its gates, the RGB carry-over gate masks, the ISFA IWD map; the roads as Phase G."""
    from sn8_clouds import _maps, _tile
    from sn8_refhaze import dark_reference_dehaze
    import run_bench3r as RR
    import r3_arms as R
    import g3_corr
    p, b, a, v = _tile(tid)
    brgb, argb = p["before_rgb"], p["after_rgb"]
    rise = _maps(p, v)["masks"]["dark rise"]
    g = np.load(OUT / f"G_{tid}.npz")
    arr = {k: g[k] for k in g.files if k in ("before", "after", "valid", "C0", "t_C0", "c0_gate", "c0_opaque", "noaa",
                                              "noaa_score", "noaa_rgb", "strip", "before_rgb", "after_rgb")}
    arr["mask|rise"] = rise
    for name, bands in RR.D1E.items():
        fld, _ = R.ihot(brgb, argb, v, bands=bands)
        arr[f"mask|{name}"], _ = R.ihot_gate(fld, v)
        if fld is not None and name == "D1e IHOT-RGB":
            lo, hi = np.nanpercentile(fld[v], [1, 99])
            arr["ihot"] = u8(255 * np.clip((np.nan_to_num(fld, nan=lo) - lo) / max(hi - lo, 1e-6), 0, 1))
    for k, m in RR.carry_gate_masks(p, b, a, v, cfg).items():
        arr[f"mask|{k}"] = m
    for name, kw in RR.A2B.items():
        corr, cannot, _ = R.a2b(brgb, argb, v, rise, **kw)
        if corr is not None:
            arr[f"rgb|{name}"] = u8(corr)
            arr[f"img|{name}"] = u8(RR.grey_of(corr, argb, a, v))
            arr[f"mask|cannot {name}"] = cannot
    c0 = dark_reference_dehaze(b, a, v)
    want = [x for x in cfg.get("corr", []) if x in g3_corr.ARMS]
    if want and c0["gate"].any():
        for x, o in g3_corr.outputs(b, a, v, c0, only=want, after_rgb=argb, before_rgb=brgb).items():
            arr[f"rgb|RGB {x}"] = u8(o["corrected"])
            arr[f"img|RGB {x}"] = u8(RR.grey_of(o["corrected"], argb, a, v))
            arr[f"t|RGB {x}"] = u8(255 * o["t"])
    iw, _, _ = R.isfa(brgb, argb, v, rise)
    if iw is not None:
        hi = np.nanpercentile(iw[v], 99)
        arr["isfa_iwd"] = u8(255 * np.clip(np.nan_to_num(iw, nan=0) / max(hi, 1e-6), 0, 1))
    rows = pd.read_csv(OUT / f"G_{tid}_roads.csv")[["strip_id", "road_row", "road_id", "flooded"]]
    for name in arm_names:
        if f"{name}__662" in calls:
            rows[f"call662|{name}"] = [int(calls[f"{name}__662"][i]) for i in rows.road_row]
            rows[f"share21|{name}"] = [float(np.mean([calls[f"{name}__{s}"][i] == 1 for s in K.M1.SEEDS
                                                      if f"{name}__{s}" in calls])) for i in rows.road_row]
    K.atomic_npz(OUT / f"R_{tid}.npz", **arr)
    rows.to_csv(OUT / f"R_{tid}_roads.csv", index=False)
    K.log(T0, f"R {kind} {tid}: {len(rows)} roads")


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "G"
    import run_bench3 as RB
    import g3_gates
    from sn8_heldout import touched_roads
    h0 = K.registry_hash()
    TH = g3_gates.thresholds(T0)
    if phase == "R":
        sel = json.loads((OUT / "G_tiles.json").read_text())
        chosen, info = [tuple(c) for c in sel["chosen"]], sel["info"]
    else:
        chosen, info = choose_tiles()
    from spatial_folds import dev_roads
    roads_tab = dev_roads().reset_index(drop=True)          # the flood stage's road order (asserted in scv_common)
    tr = touched_roads(include_cloudy=True).reset_index(drop=True)
    assert roads_tab.tile_id.equals(tr.tile_id) and roads_tab.road_id.equals(tr.road_id)
    calls = RB.load_calls()
    prod = RB.prod_calls(K.M1.SEEDS)
    for k, sd in enumerate(K.M1.SEEDS):
        calls[f"production__{sd}"] = prod[k]
    if phase == "R":
        import run_bench3r as RR
        z = np.load(RR.CALLS_R)
        calls.update({k: z[k] for k in z.files})
    arm_names = sorted({k.rsplit("__", 1)[0] for k in calls})
    for kind, tid in chosen:
        K.wait_for_memory(T0)
        if phase == "R":
            import run_bench3r as RR
            tile_cache_R(kind, tid, calls, arm_names, roads_tab, RR.carry_cfg())
        else:
            tile_cache(kind, tid, phase, calls, arm_names, roads_tab, TH)
    K.write_json(OUT / f"{phase}_tiles.json", {"chosen": chosen, "info": info, "arms_with_calls": arm_names})
    assert K.registry_hash() == h0
    K.log(T0, "done")


if __name__ == "__main__":
    main()
