"""Correction arms C0-C5 on the development tiles: corrected after images and the after-date road features for the flood
calls (preregistration_method_bench.md, scoring (c)), plus per-tile diagnostics.

Checks first (the script stops if one fails), on the first CHECK_TILES gate tiles:
  1. c_common.darkref_variant at its defaults == sn8_refhaze.dark_reference_dehaze (corrected, t, gate, opaque);
  2. after_features.after_rows on C0's corrected image == the cached darkref table's *_after columns
     (road_corrected_darkref_c1fd17d88e15c874.csv, the factorial's two-date cues) and, on the raw after image, ==
     the production road table's *_after columns.
Per tile, each arm's corrected image is compared with C0's and with the raw after image; features are computed only
when it differs from both (else the row is marked "c0" or "raw"). Per-tile pickles in BIG/corr/ (resumable).
    nice -n 10 python3 -I run_corr.py [workers] > run_corr.log 2>&1
"""
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

OUT = C.BIG / "corr"
T0 = time.time()
CHECK_TILES = 3
DARKREF_CACHE = "road_corrected_darkref_c1fd17d88e15c874.csv"
ARMS = ["C1 He 2013", "C2 IR-MAD tone", "C3a fitted fade", "C3b Poisson seam", "C4 blob 0", "C4 blob 1250",
        "C4 blob 5000", "C4 blob 10000", "C5a gamma 1.8", "C5a gamma 2.2", "C5b band-linked RGB"]


def arm_images(tile_id):
    """{arm: output dict} for C0 and every arm on one tile, plus (p, before, after, valid)."""
    from sn8_clouds import _tile
    from sn8_cloudedge import edge_parts
    from sn8_refhaze import dark_reference_dehaze
    import c1_he2013, c2_irmad, c3_seam, c4_blob, c5_gamma_band
    p, before, after, valid = _tile(tile_id)
    base = dark_reference_dehaze(before, after, valid)
    outs = {"C0": base}
    parts = edge_parts(before, after, valid, base) if base["gate"].any() else None
    if parts is not None:
        outs["C1 He 2013"] = c1_he2013.correct(before, after, valid, parts)
        outs["C3a fitted fade"] = c3_seam.correct_fade(before, after, valid, parts)
        outs["C3b Poisson seam"] = c3_seam.correct_poisson(before, after, valid, parts)
    if base["gate"].any():
        outs["C2 IR-MAD tone"] = c2_irmad.correct(before, after, valid, p["before_rgb"], p["after_rgb"])
        for g in c5_gamma_band.GAMMAS:
            outs[f"C5a gamma {g}"] = c5_gamma_band.correct_gamma(before, after, valid, g)
        outs["C5b band-linked RGB"] = c5_gamma_band.correct_band(before, after, valid, p["after_rgb"], base)
    for s in c4_blob.SIZES:
        outs[f"C4 blob {int(s)}"] = c4_blob.correct(before, after, valid, s)
    return outs, (p, before, after, valid)


def tile_job(tile_id):
    f = OUT / f"{tile_id}.pkl"
    if f.exists():
        return tile_id
    from sn8_lines import road_band
    from after_features import after_rows
    C.dev_guard_tiles([tile_id])
    outs, (p, before, after, valid) = arm_images(tile_id)
    raw = np.where(valid, after, 0).astype(np.float32)
    c0 = outs["C0"]["corrected"]
    band = road_band()
    res = {"tile_id": tile_id, "arms": {}}
    c0_rows = after_rows(tile_id, {**p, "after_grey": c0}, valid, band) if not np.array_equal(c0, raw) else None
    res["C0_rows"] = c0_rows
    for arm in ARMS:
        o = outs.get(arm)
        if o is None:
            res["arms"][arm] = {"same": "raw"}
            continue
        img = o["corrected"]
        info = {k: v for k, v in o.get("info", {}).items() if k != "profile"} if isinstance(o.get("info"), dict) else {}
        diag = {"gate_px": int(o["gate"].sum()) if "gate" in o else int(outs["C0"]["gate"].sum()),
                "opaque_px": int(o["opaque"].sum()), "changed_px": int((img != raw).sum()), "info": info}
        if np.array_equal(img, raw):
            res["arms"][arm] = {"same": "raw", **diag}
        elif np.array_equal(img, c0):
            res["arms"][arm] = {"same": "c0", **diag}
        else:
            res["arms"][arm] = {"same": None, "rows": after_rows(tile_id, {**p, "after_grey": img}, valid, band), **diag}
    if "C3a fitted fade" in outs:
        res["c3a_profile"] = outs["C3a fitted fade"]["info"]
    res["c0_diag"] = {"gate_px": int(outs["C0"]["gate"].sum()), "opaque_px": int(outs["C0"]["opaque"].sum()),
                      "valid_px": int(valid.sum())}
    tmp = f.with_suffix(".writing")
    tmp.write_bytes(pickle.dumps(res))
    tmp.replace(f)
    return tile_id


def checks(gate_tiles, roads):
    from sn8_clouds import _tile
    from sn8_lines import road_band
    from sn8_refhaze import CACHE_DIR, dark_reference_dehaze
    from after_features import after_rows
    from c_common import darkref_variant
    cache = pd.read_csv(CACHE_DIR / DARKREF_CACHE)
    band = road_band()
    for tid in gate_tiles[:CHECK_TILES]:
        p, b, a, v = _tile(tid)
        ref = dark_reference_dehaze(b, a, v)
        mine = darkref_variant(b, a, v)
        for k in ("corrected", "gate", "opaque"):
            assert np.array_equal(ref[k], mine[k]), f"STOP: darkref_variant differs from dark_reference_dehaze ({k}, {tid})"
        assert np.allclose(np.nan_to_num(ref["t"]), np.nan_to_num(mine["t"])), f"STOP: t differs on {tid}"
        rows = pd.DataFrame(after_rows(tid, {**p, "after_grey": ref["corrected"]}, v, band))
        cr = cache[cache.tile_id == tid].reset_index(drop=True)
        assert len(rows) == len(cr) and (rows.road_id.to_numpy() == cr.road_id.to_numpy()).all(), f"STOP: rows differ {tid}"
        cols = [c for c in rows.columns if c.endswith("_after")]
        d = np.nanmax(np.abs(rows[cols].to_numpy(float) - cr[cols].to_numpy(float)))
        assert d < 1e-6, f"STOP: after_rows differs from the darkref cache on {tid} (max {d})"
        rr = pd.DataFrame(after_rows(tid, p, v, band))
        rt = roads[roads.tile_id == tid].reset_index(drop=True)
        d2 = np.nanmax(np.abs(rr[cols].to_numpy(float) - rt[cols].to_numpy(float)))
        assert d2 < 1e-6, f"STOP: after_rows on the raw image differs from the road table on {tid} (max {d2})"
        C.log(T0, f"check {tid}: darkref_variant == library; after_rows == cache ({d:.1e}) and road table ({d2:.1e})")


def main():
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    from sn8_dino import with_dino
    from sn8_heldout import touched_roads
    from sn8_cloudsym import _keep_blobs  # noqa: F401  (imported to fail early if the module moved)
    h0 = C.registry_hash()
    OUT.mkdir(parents=True, exist_ok=True)
    roads = touched_roads(include_cloudy=True)
    assert set(roads.split) <= {"train", "val"} and len(roads) == 1037
    tiles = sorted(roads.tile_id[~roads.cloudy.astype(bool)].unique())
    C.dev_guard_tiles(tiles)
    assert len(tiles) == 200
    from sn8_refhaze import CACHE_DIR
    gate_tiles = sorted(pd.read_csv(CACHE_DIR / DARKREF_CACHE).tile_id.unique())
    assert len(gate_tiles) == 99, len(gate_tiles)
    if "--skip-checks" not in sys.argv:
        checks(gate_tiles, roads)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
    # gate tiles first (where nearly every arm acts), then the rest (C4 with small blobs may find new gates)
    order = gate_tiles + [t for t in tiles if t not in set(gate_tiles)]
    ctx = multiprocessing.get_context("spawn")
    done = 0
    with ProcessPoolExecutor(workers, mp_context=ctx) as ex:
        futs = {ex.submit(tile_job, t): t for t in order}
        for fu in as_completed(futs):
            try:
                fu.result()
            except Exception as e:
                import traceback
                traceback.print_exc()
                C.log(T0, f"{futs[fu]}: ERROR {e!r}")
            done += 1
            if done % 5 == 0:
                C.log(T0, f"{done}/{len(order)} tiles")
    assert C.registry_hash() == h0
    C.log(T0, "done")


if __name__ == "__main__":
    main()
