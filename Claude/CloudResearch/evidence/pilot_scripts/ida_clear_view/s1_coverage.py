"""Step 1 and 2: valid-pixel NOAA coverage of every development tile, per flight, and the flight chosen per tile.

Coverage = share of the satellite tile's valid pixels (sn8_clouds._tile valid mask: both dates non-zero, 6 px eroded)
under a valid NOAA pixel (alpha = 255) of that flight, the flight's tiles mosaicked. Measured on the photos' 4x overview
(about 0.54 m) warped to the tile grid by nearest neighbour; this replaces the outline upper bounds of evidence 17.
Flight per tile (plan step 2): most valid pixels; ties to the earlier date (FLIGHTS order).
    nice -n 10 python3 -I s1_coverage.py > s1_coverage.log 2>&1
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import numpy as np
import pandas as pd


def one(tile_id):
    p, before, after, valid = C.sat_tile(tile_id)
    src = C.flight_sources(tile_id, p, valid.shape)
    row = {"tile_id": tile_id, "x0": p["x0"], "y0": p["y0"], "h": valid.shape[0], "w": valid.shape[1],
           "valid_px": int(valid.sum())}
    for f in C.FLIGHTS:
        row[f"n_src_{f}"] = len(src[f])
        if not src[f]:
            row[f"cover_{f}"] = 0.0
            continue
        rgba = C.reproject_flight(src[f], p, valid.shape, overview_level=1, resampling="nearest")
        row[f"cover_{f}"] = float(((rgba[..., 3] >= 255) & valid).sum() / max(valid.sum(), 1))
    return row


def main():
    t0 = time.time()
    tiles = list(C.dev_tiles().tile_id)
    with ProcessPoolExecutor(3) as ex:
        rows = list(ex.map(one, tiles))
    df = pd.DataFrame(rows)
    covers = df[[f"cover_{f}" for f in C.FLIGHTS]].to_numpy()
    best = covers.argmax(1)                      # argmax returns the first (earliest) on ties
    df["flight"] = [C.FLIGHTS[i] for i in best]
    df["cover"] = covers.max(1)
    df["n_flights_50"] = (covers >= C.MIN_COVER).sum(1)
    cl = set(C.cloudy_tiles())
    df["cloudy"] = df.tile_id.isin(cl)
    ub = pd.read_csv(C.CHECK / "noaa_ida_tile_cover.csv").set_index("tile_id").cover
    df["outline_upper_bound"] = df.tile_id.map(ub)
    df["kept_cover"] = df.cover >= C.MIN_COVER
    df.loc[~df.kept_cover, "flight"] = ""
    C.CACHE.mkdir(exist_ok=True)
    df.to_csv(C.HERE / "s1_coverage.csv", index=False)
    print(f"{len(df)} dev tiles; kept (valid cover >= 50%): {int(df.kept_cover.sum())}; cloudy kept "
          f"{int((df.kept_cover & df.cloudy).sum())} of {int(df.cloudy.sum())}; {round(time.time() - t0)} s")
    print("flight chosen:", df.flight[df.kept_cover].value_counts().to_dict())
    print("cloudy flight chosen:", df.flight[df.kept_cover & df.cloudy].value_counts().to_dict())
    print("tiles with >= 2 flights at >= 50%:", int((df.n_flights_50 >= 2).sum()))


if __name__ == "__main__":
    main()
