"""Phase A step 1: haze scores for every development tile (train + val) -> haze_roads.csv, haze_tiles.csv (cached).
    nice -n 10 /opt/miniconda3/bin/python -I run_scores.py > run_scores.log 2>&1"""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from haze_common import HERE, load_spotter, tile_rows
import multiprocessing as mp
import pandas as pd

N_WORKERS = 3
_S = {}


def _init():
    _S["s"] = load_spotter()


def _one(tile_id):
    return tile_id, *tile_rows(tile_id, _S["s"])


def main():
    from sn8_grey import GREY_DIR
    t0 = time.time()
    index = pd.read_csv(GREY_DIR / "tiles.csv")
    dev = index[index.split.isin(["train", "val"])]
    assert len(dev) == 226
    load_spotter()
    parts = HERE / "tile_parts"
    parts.mkdir(exist_ok=True)
    todo = [t for t in dev.tile_id if not (parts / f"{t}.csv").exists()]
    print(f"{len(todo)} tiles to score", flush=True)
    with mp.get_context("spawn").Pool(N_WORKERS, initializer=_init) as pool:
        for i, (tid, rows, trow) in enumerate(pool.imap_unordered(_one, todo)):
            pd.DataFrame(rows, columns=None if rows else ["tile_id", "road_id"]).to_csv(parts / f"{tid}.roads.csv", index=False)
            pd.DataFrame([trow]).to_csv(parts / f"{tid}.csv", index=False)
            if i % 10 == 0:
                print(f"{i + 1}/{len(todo)} {round(time.time() - t0)} s", flush=True)
    # assemble in feature_table order (train tiles then val tiles, each in tiles.csv order)
    roads, tiles = [], []
    for split in ("train", "val"):
        for t in index.tile_id[index.split == split]:
            tiles.append(pd.read_csv(parts / f"{t}.csv").assign(split=split))
            r = pd.read_csv(parts / f"{t}.roads.csv")
            if len(r):
                roads.append(r.assign(split=split))
    pd.concat(roads, ignore_index=True).to_csv(HERE / "haze_roads.csv", index=False)
    pd.concat(tiles, ignore_index=True).to_csv(HERE / "haze_tiles.csv", index=False)
    print(f"done {round(time.time() - t0)} s", flush=True)


if __name__ == "__main__":
    main()
