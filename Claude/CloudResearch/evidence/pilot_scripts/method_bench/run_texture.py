"""Texture arms T1-T3: per-road features on every development tile with touched roads (preregistration_method_bench.md).
Inputs as the library's texture families read them: grey / 255, the after image histogram-matched to the before over
the valid pixels, no-data filled with the valid median (sn8_texture._filled) for T1 and T2; the raw grey for T3 (as
sn8_glcm). Strips: sn8_cloudsym.road_strips (= the strips of sn8_roads / sn8_glcm). One row per road with at least
MIN_ROAD_PX valid centreline pixels, in feature_table order. Per-tile CSVs cached in BIG/texture/ (resumable).
    nice -n 10 python3 -I run_texture.py [workers] > run_texture.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

OUT = C.BIG / "texture"
T0 = time.time()


def tile_rows(tile_id):
    f = OUT / f"{tile_id}.csv"
    if f.exists():
        return pd.read_csv(f)
    from skimage import exposure
    from sn8_clouds import _tile
    from sn8_cloudsym import road_strips
    from sn8_roads import MIN_ROAD_PX
    from sn8_texture import _filled
    import t1_lbp, t2_lowe, t3_glcm
    C.dev_guard_tiles([tile_id])
    p, before, after, valid = _tile(tile_id)
    strip, centre, roads = road_strips(tile_id, p, valid)
    n = len(roads) - 1
    if n == 0:
        df = pd.DataFrame(columns=["tile_id", "road_id"])
        df.to_csv(f, index=False)
        return df
    gb = p["before_grey"] / 255
    ga = (p["after_grey"] / 255).astype(np.float64)
    ga[valid] = exposure.match_histograms(ga[valid], gb[valid])
    fb, fa = _filled(gb.astype(np.float32), valid), _filled(ga.astype(np.float32), valid)
    res = {}
    res.update(t1_lbp.lbp_features(fb, fa, valid, strip, n))
    res.update(t2_lowe.lowe_features(fb, fa, valid, strip, n))
    res.update(t3_glcm.glcm_features(p["before_grey"], p["after_grey"], valid, strip, n))
    rows = [{"tile_id": tile_id, "road_id": roads[k + 1]["road_id"], **{c: float(v[k]) for c, v in res.items()}}
            for k in range(n) if centre[k] >= MIN_ROAD_PX]
    df = pd.DataFrame(rows)
    tmp = f.with_suffix(".writing")
    df.to_csv(tmp, index=False)
    tmp.replace(f)
    return df


def main():
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    from sn8_heldout import touched_roads
    h0 = C.registry_hash()
    OUT.mkdir(parents=True, exist_ok=True)
    roads = touched_roads(include_cloudy=True)
    assert set(roads.split) <= {"train", "val"} and len(roads) == 1037
    tiles = list(dict.fromkeys(roads.tile_id))
    C.dev_guard_tiles(tiles)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ctx = multiprocessing.get_context("spawn")
    done = 0
    with ProcessPoolExecutor(workers, mp_context=ctx) as ex:
        futs = {ex.submit(tile_rows, t): t for t in tiles}
        for fu in as_completed(futs):
            fu.result()
            done += 1
            if done % 10 == 0:
                C.log(T0, f"{done}/{len(tiles)} tiles")
    parts = [pd.read_csv(OUT / f"{t}.csv") for t in tiles]
    tab = pd.concat([p for p in parts if len(p)], ignore_index=True)
    # align with the 1,037-road table (tile, road, occurrence)
    tab["_n"] = tab.groupby(["tile_id", "road_id"]).cumcount()
    r = roads[["tile_id", "road_id"]].copy()
    r["_n"] = r.groupby(["tile_id", "road_id"]).cumcount()
    m = r.merge(tab, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
    assert (m["_merge"] == "both").all(), f"{(m['_merge'] != 'both').sum()} roads without texture rows"
    m.drop(columns=["_merge", "_n"]).to_csv(C.HERE / "texture_roads.csv", index=False)
    assert C.registry_hash() == h0
    C.log(T0, f"done: {len(m)} roads")


if __name__ == "__main__":
    main()
