"""Real development tiles (outputs/preregistration_cloud_gate.md), label-free except the building footprints used to
check that houses do not come into the gate. Every training and validation tile: per arm, the share of pixels in
each label and in the gate, the building pixels gated, and the handle-step decision per road.
Writes real_tiles.csv and real_roads.csv."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import cv2
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
ARMS = {"either-date": {}, "either-date, both smooth": {"both": "smooth"},
        **{f"hysteresis {lo}, seed": {"low": lo, "grow": "seed"} for lo in (50, 35, 20)},
        **{f"hysteresis {lo}, grown": {"low": lo, "grow": "grown"} for lo in (50, 35, 20)}}


def building_mask(tile_id, p, shape):
    """The tile's labelled building footprints (published SpaceNet 8 labels, development tile) on the 0.5 m grid."""
    from sn8 import tile
    from sn8_lines import _TO_UTM
    from sn8_torchgeo import RES
    mask = np.zeros(shape, np.uint8)
    with open(tile(tile_id)["label"]) as f:
        features = json.load(f)["features"]
    for feat in features:
        props, geom = feat.get("properties") or {}, feat.get("geometry")
        if not geom or not props.get("building"):
            continue
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            lon, lat = np.array(poly[0])[:, :2].T
            x, y = _TO_UTM.transform(lon, lat)
            pts = np.c_[(x - p["x0"]) / RES, (p["y0"] - y) / RES].round().astype(np.int32)
            cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)


def run_tile(tid):
    cv2.setNumThreads(1)
    from sn8_clouds import _tile, dark_channel
    from sn8_cloudsym import either_date_dehaze, road_decisions, road_strips
    from sn8_lines import CLOUD_SHARE, cloud_share
    from sn8_refhaze import dark_reference_dehaze, road_handling
    t0 = time.time()
    p, before, after, valid = _tile(tid)
    dark = (dark_channel(before, valid), dark_channel(after, valid))
    strip, centre, roads = road_strips(tid, p, valid)
    houses = building_mask(tid, p, valid.shape) & valid
    cloudy = cloud_share(after, valid) >= CLOUD_SHARE
    tile_rows, road_rows = [], []
    ex = dark_reference_dehaze(before, after, valid)
    outs = {"existing two-date": {"gated": ex["gate"] & valid, "cannot": ex["opaque"], "labels": None,
                                  "rise": ex["gate"], "fall": np.zeros_like(valid), "both": np.zeros_like(valid)}}
    for arm, kw in ARMS.items():
        o = either_date_dehaze(before, after, valid, dark=dark, **kw)
        outs[arm] = {"gated": (o["labels"] > 0) & valid, "cannot": o["cannot"], "labels": o["labels"],
                     "rise": o["rise"], "fall": o["fall"], "both": o["both"], "reason": o["reason"]}
    for arm, o in outs.items():
        row = {"tile_id": tid, "arm": arm, "tile rule cloudy": bool(cloudy), "valid px": int(valid.sum()),
               "gated share": float(o["gated"][valid].mean()), "rise share": float(o["rise"][valid].mean()),
               "fall share": float((o["fall"] & valid)[valid].mean()), "both share": float(o["both"][valid].mean()),
               "cannot share": float(o["cannot"][valid].mean()), "building px": int(houses.sum()),
               "building gated px": int((houses & o["gated"]).sum()), "building cannot px": int((houses & o["cannot"]).sum()),
               "added vs either-date px": int((o["gated"] & ~outs["either-date"]["gated"]).sum())}
        if "reason" in o:
            for k, name in ((1, "both cloudy"), (2, "opaque after"), (3, "opaque before")):
                row[f"cannot: {name} share"] = float((o["reason"] == k)[valid].mean())
        tile_rows.append(row)
        for n, r in enumerate(road_decisions(strip, centre, roads, o["gated"], o["cannot"], o["labels"])):
            road_rows.append({"tile_id": tid, "arm": arm, "n": n, **r})
    # check: the existing arm's decisions equal sn8_refhaze.road_handling's on the roads both list
    rh = road_handling(tid, out=ex)
    mine = pd.DataFrame([r for r in road_rows if r["arm"] == "existing two-date"])
    mism = 0
    if len(rh) and len(mine):
        rh = rh.assign(k=rh.groupby("road_id").cumcount())
        mine = mine.assign(k=mine.groupby("road_id").cumcount())
        m = mine.merge(rh, on=["road_id", "k"], suffixes=("", "_rh"))
        mism = int((m.decision != m.decision_rh).sum())
    for row in tile_rows:
        row["road_handling mismatches"] = mism
    print(f"{tid} {time.time() - t0:.1f}s", flush=True)
    return tile_rows, road_rows


if __name__ == "__main__":
    from sn8_data import split_tables
    t0 = time.time()
    _, train, val, _, _ = split_tables(662)
    tiles = sorted(set(train.tile_id) | set(val.tile_id))
    print("development tiles:", len(tiles), flush=True)
    with Pool(4) as pool:
        results = pool.map(run_tile, tiles, chunksize=1)
    pd.DataFrame([r for t, _ in results for r in t]).to_csv(OUT / "real_tiles.csv", index=False)
    pd.DataFrame([r for _, rr in results for r in rr]).to_csv(OUT / "real_roads.csv", index=False)
    print("done", round(time.time() - t0), "s")
