"""Arm D3 on the SN8 development roads: the share of each road's strip under the dark-rise mask with Hagolle's vetoes
(d3_hagolle.py). The unvetoed share must reproduce cloud_dark_rise_road exactly (checked on every road).
Writes d3_roads.csv (1,037 rows, touched_roads order) and d3_tiles.csv.
    nice -n 10 python3 -I run_d3.py [workers] > run_d3.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

T0 = time.time()
OUT = C.BIG / "d3"


def tile_job(tile_id):
    f = OUT / f"{tile_id}.csv"
    if f.exists():
        return pd.read_csv(f)
    from sn8_clouds import _maps, _tile
    from sn8_cloudspot import _strip, road_shares
    from sn8_lines import road_band
    from d3_hagolle import vetoes
    C.dev_guard_tiles([tile_id])
    p, before, after, valid = _tile(tile_id)
    m = _maps(p, valid)
    rise = m["masks"]["dark rise"]
    vi, vii, info = vetoes(p, before, after, valid, m["masks"])
    strip, roads, n, centre_px = _strip(tile_id, p, valid, road_band())
    if not n:
        df = pd.DataFrame(columns=["tile_id", "road_id"])
    else:
        df = pd.DataFrame(road_shares(tile_id, strip, roads, n, centre_px,
                                      {"rise": rise, "rise_D3i": rise & ~vi, "rise_D3ii": rise & ~vii,
                                       "rise_D3": rise & ~(vi | vii)}))
        df["r_clear"] = info["r_clear"]
        df["rise_tile"] = float(rise[valid].mean())
        df["veto_i_of_rise"] = float((vi & rise).sum() / max(rise.sum(), 1))
        df["veto_ii_of_rise"] = float((vii & rise).sum() / max(rise.sum(), 1))
    tmp = f.with_suffix(".writing")
    df.to_csv(tmp, index=False)
    tmp.replace(f)
    return df


def main():
    from concurrent.futures import ProcessPoolExecutor
    import multiprocessing
    from sn8_heldout import touched_roads
    h0 = C.registry_hash()
    OUT.mkdir(parents=True, exist_ok=True)
    roads = touched_roads(include_cloudy=True)
    assert set(roads.split) <= {"train", "val"} and len(roads) == 1037
    tiles = list(dict.fromkeys(roads.tile_id))
    C.dev_guard_tiles(tiles)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    with ProcessPoolExecutor(workers, mp_context=multiprocessing.get_context("spawn")) as ex:
        parts = list(ex.map(tile_job, tiles))
    tab = pd.concat([p for p in parts if len(p)], ignore_index=True)
    tab["_n"] = tab.groupby(["tile_id", "road_id"]).cumcount()
    r = roads[["tile_id", "road_id", "cloud_dark_rise_road"]].copy()
    r["_n"] = r.groupby(["tile_id", "road_id"]).cumcount()
    mrg = r.merge(tab, on=["tile_id", "road_id", "_n"], how="left", indicator=True)
    assert (mrg["_merge"] == "both").all()
    gap = np.abs(mrg.rise.to_numpy() - mrg.cloud_dark_rise_road.to_numpy()).max()
    assert gap < 1e-9, f"STOP: unvetoed share does not reproduce cloud_dark_rise_road ({gap})"
    mrg.drop(columns=["_merge", "_n"]).to_csv(C.HERE / "d3_roads.csv", index=False)
    C.log(T0, f"done; dark-rise reproduction max gap {gap:.1e}")
    assert C.registry_hash() == h0


if __name__ == "__main__":
    main()
