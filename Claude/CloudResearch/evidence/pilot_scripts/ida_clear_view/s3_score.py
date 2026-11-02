"""Steps 5-6, pixel side: per tile, per arm and region, the DINOv2 patch-feature distance to the NOAA photo (primary),
grey error and edge agreement (secondary), plus the pixel samples for outcomes 4 (t vs recovered), 5 (cloud detection),
the Ref-Diff leakage check and the optional spread check (Ding et al. 2024 idea).

Tokens: sn8_dino.tokens (frozen DINOv2 ViT-L/14 + registers, CPU), every image with the SAME valid mask (score =
satellite valid & NOAA valid & not NOAA cloud/glare), so no-data filling is identical across arms. A pixel's feature
distance is its 14 px patch's 1 - cosine(arm token, NOAA token); a region's mean is over its pixels (patches weighted by
how many region pixels they hold, as lines_dino weights road strips).
Grey error: mean |arm - tone-matched NOAA|. Edge agreement: Pearson r of gradient magnitude (sn8_coreg._gradient, 1 m
blur) between arm and NOAA over the region's pixels.
Regions (all inside score): thin = two-date gate (dark-rise blobs, + both-cloudy) with t >= 0.2 and not cannot-assess;
opaque = gate with t < 0.2 or cannot-assess; guard = outside every cloud mask (bright, dark, dark rise, the two-date
gates, the spotter where it ran). Each also on road strips (sn8_cloudsym.road_strips), building footprints (SN8 labels)
and the rest.
    nice -n 10 python3 -I s3_score.py [pixel|dino] > s3_score.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import cv2
import numpy as np
import pandas as pd

ARMS = ["asis", "he", "td", "tdspot"]
OUT = C.BIG / "score"
SUB = 4                     # pixel samples: every 4th row and column


def patch_to_px(d, shape):
    from sn8_dino import PATCH
    return np.repeat(np.repeat(d, PATCH, 0), PATCH, 1)[: shape[0], : shape[1]]


def cosdist(a, b):
    num = (a * b).sum(-1)
    den = np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1)
    return 1 - num / np.maximum(den, 1e-12)


def regions(z):
    s = z["score"]
    gate, t, cannot = z["gate_td"], z["t"], z["cannot"]
    thin = s & gate & ~cannot & (np.nan_to_num(t, nan=1) >= 0.2)
    opaque = s & gate & (cannot | (np.nan_to_num(t, nan=1) < 0.2))
    return {"thin": thin, "opaque": opaque, "guard": z["guard"]}


def edge_r(a, b, m):
    from sn8_coreg import _gradient
    if m.sum() < 50:
        return np.nan
    ga, gb = _gradient(a, m), _gradient(b, m)
    x, y = ga[m], gb[m]
    if x.std() < 1e-6 or y.std() < 1e-6:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def score_tile(tile_id, with_dino, floor=True):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{tile_id}_{'dino' if with_dino else 'pixel'}.npz"
    if f.exists():
        return pd.DataFrame(list(np.load(f, allow_pickle=True)["rows"]))
    z = dict(np.load(C.BIG / "prep" / f"{tile_id}.npz", allow_pickle=True))
    from sn8_cloudsym import road_strips
    p, _, _, valid = C.sat_tile(tile_id)
    strip, _, _ = road_strips(tile_id, p, valid)
    road = strip > 0
    bld = z["buildings"]
    s = z["score"]
    R = regions(z)
    noaa = z["noaa"]
    arms = {a: z[a] for a in ARMS if not (a == "tdspot" and not bool(z["spotter_run"]))}
    shape = s.shape
    dist, dist_before = {}, {}
    extra = {}
    if with_dino:
        C.cpu_backbone()
        tok = {"noaa": C.cached_tokens(noaa, s), "before": C.cached_tokens(z["before"], s)}
        for a, img in arms.items():
            tok[a] = C.cached_tokens(img, s)
        for a in arms:
            dist[a] = patch_to_px(cosdist(tok[a], tok["noaa"]), shape)
            dist_before[a] = patch_to_px(cosdist(tok[a], tok["before"]), shape)
        dist["before"] = patch_to_px(cosdist(tok["before"], tok["noaa"]), shape)
        # date-gap noise floor: NOAA vs NOAA (second flight) on clear ground, beside satellite vs NOAA on the same pixels
        if floor and "noaa2" in z and bool(z.get("noaa2_ok", np.zeros(1)).any()):
            m2 = s & z["noaa2_ok"]
            if (m2 & R["guard"]).sum() > 2000:
                t1, t2, ta = C.cached_tokens(noaa, m2), C.cached_tokens(z["noaa2"], m2), C.cached_tokens(z["asis"], m2)
                g = m2 & R["guard"]
                d12 = patch_to_px(cosdist(t1, t2), shape)[g]
                da1 = patch_to_px(cosdist(ta, t1), shape)[g]
                extra["floor"] = {"floor_px": int(g.sum()), "floor_feat_noaa_noaa": float(d12.mean()),
                                  "floor_feat_sat_noaa": float(da1.mean()),
                                  "floor_grey_noaa_noaa": float(np.abs(noaa - z["noaa2"])[g].mean()),
                                  "floor_grey_sat_noaa": float(np.abs(z["asis"] - noaa)[g].mean())}
    rows = []
    subsets = {"all": np.ones(shape, bool), "road": road, "building": bld & ~road, "other": ~bld & ~road}
    for rn, rm in R.items():
        for sn, sm in subsets.items():
            m = rm & sm
            n = int(m.sum())
            for a, img in arms.items():
                row = {"tile_id": tile_id, "region": rn, "subset": sn, "arm": a, "px": n}
                if n >= 50:
                    row["grey_err"] = float(np.abs(img - noaa)[m].mean())
                    row["grey_change"] = float(np.abs(img - z["asis"])[m].mean())
                    row["edge_r"] = edge_r(img, noaa, m)
                    if with_dino:
                        row["feat"] = float(dist[a][m].mean())
                        row["feat_to_before"] = float(dist_before[a][m].mean())
                rows.append(row)
            if with_dino and n >= 50:
                rows.append({"tile_id": tile_id, "region": rn, "subset": sn, "arm": "before", "px": n,
                             "feat": float(dist["before"][m].mean()),
                             "grey_err": float(np.abs(z["before"] - noaa)[m].mean())})
    sub = np.zeros(shape, bool)
    sub[SUB // 2::SUB, SUB // 2::SUB] = True
    samples = {}
    ks = (5, 5)
    disagree = np.abs(cv2.blur(z["asis"], ks) - cv2.blur(noaa, ks))
    ss = s & sub
    samples.update(o5_disagree=disagree[ss].astype(np.float32), o5_darkrise=z["darkrise"][ss], o5_spot=z["spot"][ss],
                   o5_guard=R["guard"][ss], o5_gate=z["gate_td"][ss], o5_bright=z["bright"][ss])
    if with_dino:
        gs = (R["thin"] | R["opaque"]) & sub
        samples.update(o4_t=np.nan_to_num(z["t"], nan=1)[gs].astype(np.float32),
                       o4_cannot=z["cannot"][gs], o4_feat_td=dist["td"][gs].astype(np.float32),
                       o4_feat_asis=dist["asis"][gs].astype(np.float32), o4_road=road[gs],
                       guard_feat_td=dist["td"][R["guard"] & sub].astype(np.float32),
                       guard_feat_asis=dist["asis"][R["guard"] & sub].astype(np.float32))
        # optional spread check (Ding et al. 2024 idea): two-date output across the plan's fixed gate settings
        if R["thin"].any():
            from sn8_cloudsym import HYSTERESIS_LOWS, either_date_dehaze
            p2, before, after, valid2 = C.sat_tile(tile_id)
            outs = [z["td"]] + [either_date_dehaze(before, after, valid2, low=lo)["after corrected"]
                                for lo in HYSTERESIS_LOWS]
            spread = np.std(np.stack(outs), 0)
            ts = R["thin"] & sub
            samples.update(spread_thin=spread[ts].astype(np.float32), spread_feat_td=dist["td"][ts].astype(np.float32),
                           spread_grey_err_td=np.abs(z["td"] - noaa)[ts].astype(np.float32))
        np.save(OUT / f"{tile_id}_featmap_td.npy", dist["td"].astype(np.float16))
        np.save(OUT / f"{tile_id}_featmap_asis.npy", dist["asis"].astype(np.float16))
        np.save(OUT / f"{tile_id}_featmap_he.npy", dist["he"].astype(np.float16))
    np.savez_compressed(f, rows=np.array(rows, dtype=object), extra=np.array(extra, dtype=object), **samples)
    return pd.DataFrame(rows)


N_CLEAR_DINO = 10          # compute budget (CPU only, shared machine): first 10 of the 30 sampled clear tiles, seed 662
N_FLOOR = 8                # noise floor (3 extra token maps per tile) on the first 8 scored tiles with a second flight


def prep_row(t, wait=True):
    """The prep row of a tile, waiting for s2_prep.py to write it."""
    f = C.BIG / "prep" / f"{t}.npz"
    while wait and not f.exists():
        time.sleep(30)
    time.sleep(1)
    return np.load(f, allow_pickle=True)["row"].item()


def dino_plan():
    """All kept cloudy tiles, then the 30 sampled clear tiles in a seed-662 order (the first N_CLEAR_DINO aligned
    ones are scored); the noise floor on the first N_FLOOR scored tiles with an aligned second flight."""
    scored = sorted((C.HERE / "scored_tiles.txt").read_text().split())
    cl = set(C.cloudy_tiles())
    cloudy = [t for t in scored if t in cl]
    clear = list(np.random.default_rng(C.SEED).permutation([t for t in scored if t not in cl]))
    return cloudy, clear


def dino_stream():
    """Yields (tile, floor?) in plan order as soon as each tile's prep exists; the same order in every worker."""
    cloudy, clear = dino_plan()
    n_clear = n_floor = 0
    for t in cloudy + clear:
        r = prep_row(t)
        if str(r.get("coreg_ok")) != "True":
            continue
        if t in clear:
            if n_clear >= N_CLEAR_DINO:
                break
            n_clear += 1
        fl = str(r.get("second_ok")) == "True" and n_floor < N_FLOOR
        n_floor += fl
        yield t, fl


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "pixel"
    k, n = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    if mode == "dino":
        stream = dino_stream()
    else:
        prep = pd.read_csv(C.HERE / "s2_prep.csv")
        stream = ((t, False) for t in prep.tile_id[prep.coreg_ok.astype(str) == "True"])
    t0 = time.time()
    for i, (t, fl) in enumerate(stream):
        if mode == "dino" and k == 0:
            with open(C.HERE / "dino_tiles.txt", "a") as fh:
                fh.write(f"{t}\t{'floor' if fl else ''}\n")
        if i % n != k:
            continue
        try:
            score_tile(t, mode == "dino", floor=fl)
            print(f"{i + 1} {t} floor={fl} {round(time.time() - t0)} s", flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"{t}: ERROR {e!r}", flush=True)


if __name__ == "__main__":
    main()
