"""Known-answer checks with synthetic haze (outputs/preregistration_cloud_gate.md): S1 haze on the AFTER image
(no-regression check and task B), S2 haze on the BEFORE image (task A), S3 haze on BOTH dates (task A, both cloudy).
The 94 clear development tiles (sn8_refhaze.clear_tiles), seeds as sn8_refhaze.haze_recovery (662 + position).
Synthetic haze is used only for these known-answer checks, never as training labels.
Writes synthetic_tiles.csv (one row per scenario, arm and tile) and synthetic_confusion.json."""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import cv2
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

OUT = Path(__file__).resolve().parent
SEED = 662
BOTH_OFFSET = 5000                       # S3: the after image's haze field uses seed + position + 5000
ARMS = {"either-date": {}, "either-date, both smooth": {"both": "smooth"},
        **{f"hysteresis {lo}, seed": {"low": lo, "grow": "seed"} for lo in (50, 35, 20)},
        **{f"hysteresis {lo}, grown": {"low": lo, "grow": "grown"} for lo in (50, 35, 20)}}


def _metrics(corr, t, detected, cannot, truth, lc_truth, t_true, haze, clear, valid, flooded, dry):
    from sn8_refhaze import local_contrast
    err = corr - truth
    row = {"grey error": float(np.sqrt(np.mean(err[haze] ** 2))),
           "detail kept": float(np.median(local_contrast(corr)[haze]) / np.median(lc_truth[haze]))}
    if t is not None:
        tt = np.nan_to_num(t, nan=1.0)
        row["t error"] = float(np.mean(np.abs(tt - t_true)[haze]))
        row["clear ground changed"] = float(np.mean(tt[clear] < 0.95))
    if detected is not None:
        row.update({"tp": int((detected & haze).sum()), "fp": int((detected & valid & ~haze).sum()),
                    "fn": int((~detected & haze).sum())})
        row["detected on clear ground"] = float(detected[clear].mean())
    if cannot is not None:
        row["cannot under haze"] = float(cannot[haze].mean())
        row["cannot on clear ground"] = float(cannot[clear].mean())
    for name, m in (("flooded strip", flooded & haze), ("dry strip", dry & haze)):
        row[f"{name} px"] = int(m.sum())
        row[f"{name} sse"] = float(np.sum(err[m].astype(np.float64) ** 2))
    return row


def run_tile(job):
    i, tid = job
    cv2.setNumThreads(1)
    from sn8_clouds import _tile, dark_channel, dehaze
    from sn8_cloudsym import either_date_dehaze, road_strips
    from sn8_refhaze import dark_reference_dehaze, local_contrast, synthetic_haze
    t0 = time.time()
    p, before, after, valid = _tile(tid)
    strip, centre, roads = road_strips(tid, p, valid)
    fl = np.array([False] + [r["flooded"] for r in roads[1:]])
    flooded, dry = (strip > 0) & fl[strip], (strip > 0) & ~fl[strip]
    db0, da0 = dark_channel(before, valid), dark_channel(after, valid)
    rows, conf = [], {}

    def add(scenario, arm, **m):
        rows.append({"scenario": scenario, "arm": arm, "tile_id": tid, "position": i, **m})

    # S1: haze on the after image (the regression check, and task B)
    hazy, t_true = synthetic_haze(after, valid, SEED + i)
    haze = valid & (t_true < 0.95)
    clear = valid & (ndi.distance_transform_edt(t_true >= 0.999) > 80)
    lc = local_contrast(after)
    dh = dark_channel(hazy, valid)
    common = dict(truth=after, lc_truth=lc, t_true=t_true, haze=haze, clear=clear, valid=valid, flooded=flooded, dry=dry)
    add("S1 after haze", "as it is", **{"haze share": float(haze[valid].mean())},
        **_metrics(hazy, None, None, None, **common))
    ex = dark_reference_dehaze(before, hazy, valid)
    add("S1 after haze", "existing two-date", **_metrics(ex["corrected"], ex["t"], ex["gate"], ex["opaque"], **common))
    he = dehaze(hazy, valid)
    add("S1 after haze", "single image (He)", **_metrics(he[0], he[1], None, None, **common))
    for arm, kw in ARMS.items():
        o = either_date_dehaze(before, hazy, valid, dark=(db0, dh), **kw)
        extra = {"fall share": float(o["fall"][valid].mean()), "both share": float(o["both"][valid].mean()),
                 "before altered": float((np.abs(o["before corrected"] - before) > 0.5)[valid].mean())}
        if arm == "either-date":
            d = np.abs(o["after corrected"] - ex["corrected"])[valid]
            extra.update({"max diff vs existing": float(d.max()), "px differing vs existing": int((d > 1e-3).sum()),
                          "gate differs vs existing": int((o["rise"] != ex["gate"]).sum())})
        add("S1 after haze", arm, **extra,
            **_metrics(o["after corrected"], o["t after"], o["labels"] == 1, o["cannot"], **common))

    # S2: the same haze field on the before image (task A)
    hazy_b, t_true = synthetic_haze(before, valid, SEED + i)
    haze = valid & (t_true < 0.95)
    clear = valid & (ndi.distance_transform_edt(t_true >= 0.999) > 80)
    lc = local_contrast(before)
    dhb = dark_channel(hazy_b, valid)
    common = dict(truth=before, lc_truth=lc, t_true=t_true, haze=haze, clear=clear, valid=valid, flooded=flooded,
                  dry=dry)
    add("S2 before haze", "as it is", **{"haze share": float(haze[valid].mean())},
        **_metrics(hazy_b, None, None, None, **common))
    ex = dark_reference_dehaze(hazy_b, after, valid)      # today's code: looks only for cloud in the after image
    add("S2 before haze", "existing two-date", **{"gate share": float(ex["gate"][valid].mean()),
        "after altered": float((np.abs(ex["corrected"] - after) > 0.5)[valid].mean())},
        **_metrics(hazy_b, np.where(valid, 1.0, np.nan), np.zeros_like(valid), ex["opaque"], **common))
    he = dehaze(hazy_b, valid)
    add("S2 before haze", "single image (He)", **_metrics(he[0], he[1], None, None, **common))
    for arm, kw in ARMS.items():
        o = either_date_dehaze(hazy_b, after, valid, dark=(dhb, da0), **kw)
        add("S2 before haze", arm, **{"rise share": float(o["rise"][valid].mean()), "both share": float(o["both"][valid].mean()),
            "after altered": float((np.abs(o["after corrected"] - after) > 0.5)[valid].mean())},
            **_metrics(o["before corrected"], o["t before"], o["labels"] == 2, o["cannot"], **common))

    # S3: haze on both dates, two different fields (task A: both cloudy, and which date is which)
    hazy_a, ta = synthetic_haze(after, valid, SEED + i + BOTH_OFFSET)
    tb = t_true
    truth_lab = np.where(valid, (ta < 0.95).astype(int) + 2 * (tb < 0.95).astype(int), -1)   # 0 none 1 a 2 b 3 both
    dha = dark_channel(hazy_a, valid)
    for arm, kw in (("either-date", {}), ("either-date, both smooth", {"both": "smooth"})):
        o = either_date_dehaze(hazy_b, hazy_a, valid, dark=(dhb, dha), **kw)
        pred = o["labels"].astype(int)
        c = np.zeros((4, 4), int)
        np.add.at(c, (truth_lab[valid], pred[valid]), 1)
        conf[arm] = c.tolist()
        only_a, only_b, both_true = valid & (truth_lab == 1), valid & (truth_lab == 2), valid & (truth_lab == 3)
        m = {"after-only px": int(only_a.sum()), "before-only px": int(only_b.sum()), "both px": int(both_true.sum()),
             "after-only error as it is": float(np.sqrt(np.mean((hazy_a - after)[only_a] ** 2))) if only_a.any() else np.nan,
             "after-only error": float(np.sqrt(np.mean((o["after corrected"] - after)[only_a] ** 2))) if only_a.any() else np.nan,
             "before-only error as it is": float(np.sqrt(np.mean((hazy_b - before)[only_b] ** 2))) if only_b.any() else np.nan,
             "before-only error": float(np.sqrt(np.mean((o["before corrected"] - before)[only_b] ** 2))) if only_b.any() else np.nan,
             "cannot in both": float(o["cannot"][both_true].mean()) if both_true.any() else np.nan,
             "cannot in one-date haze": float(o["cannot"][only_a | only_b].mean()) if (only_a | only_b).any() else np.nan}
        add("S3 both dates", arm, **m)
    print(f"{i:3d} {tid} {time.time() - t0:.1f}s", flush=True)
    return rows, conf


if __name__ == "__main__":
    from sn8_data import split_tables
    from sn8_refhaze import clear_tiles
    t0 = time.time()
    _, train, val, _, _ = split_tables(662)
    dev = set(train.tile_id) | set(val.tile_id)
    tiles = clear_tiles()
    assert set(tiles) <= dev, "development tiles only"
    print("clear development tiles:", len(tiles), flush=True)
    with Pool(4) as pool:
        results = pool.map(run_tile, list(enumerate(tiles)), chunksize=1)
    rows = [r for res, _ in results for r in res]
    conf = {}
    for _, c in results:
        for arm, m in c.items():
            conf[arm] = (np.array(conf.get(arm, np.zeros((4, 4), int))) + np.array(m)).tolist()
    pd.DataFrame(rows).to_csv(OUT / "synthetic_tiles.csv", index=False)
    json.dump({"confusion (rows truth, columns label: 0 clear, 1 after, 2 before, 3 both)": conf},
              open(OUT / "synthetic_confusion.json", "w"), indent=1)
    print("done", round(time.time() - t0), "s")
