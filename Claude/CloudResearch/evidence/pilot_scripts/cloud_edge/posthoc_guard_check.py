"""POST-HOC (written after the choose-half selection, before any report-half number was looked at; choose half only).
1. The guard's "clear ground beyond the margin" (over 40 px from the gate, tone-matched dark rise <= 36) split by
   distance from the gate: is it as clear near the cloud as far from it? Uncorrected after image: median tone-matched
   dark rise and median grey residual (after - tone(before)); and the share each a/b setting changes (t < 0.95).
2. Where the seam index peaks (which ring from the gate edge) for as it is, the current fit and the chosen settings."""
import sys
from multiprocessing import Pool
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd
from scipy import ndimage as ndi
from sn8_clouds import _tile
from sn8_cloudedge import (ARMS, DARKREF_GATE_MARGIN_PX, FAR_PX, HAZY_SHARE_CUT, MIN_BAND_PX, SEAM_BORDER_PX,
                           SEAM_GATE_PX, SEAM_RING_PX, CHANGED_T, _seam_gradient, as_it_is, edge_dehaze, edge_parts)
OUT = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_edge/"
SPREAD_ARMS = [k for k in ARMS if k[0] in "ab"]
SEAM_ARMS = ["current", "a: soft gate 0.25, cap 160", "b: data fade 80", "b: data fade 40", "d: window 11",
             "e: He 2013 r20, eps 0.01", "e: He 2013 r50, eps 0.01"]
DIST = {"40-80": (40, 80), "80-120": (80, 120), "120-160": (120, 160), "over 160": (160, np.inf)}


def one(tid):
    _, before, after, valid = _tile(tid)
    parts = edge_parts(before, after, valid)
    sd, cut, tone = parts["sd"], parts["cut"], parts["tone"]
    tb = tone(before)
    clear = valid & (sd > DARKREF_GATE_MARGIN_PX) & (parts["rise"] <= HAZY_SHARE_CUT * cut)
    outs = {a: edge_dehaze(parts, before, after, valid, *ARMS[a]) for a in set(SPREAD_ARMS) | set(SEAM_ARMS)}
    rows = []
    for name, (lo, hi) in DIST.items():
        m = clear & (sd > lo) & (sd <= hi)
        r = {"tile_id": tid, "kind": "clear by distance", "band": name, "n": int(m.sum())}
        if m.sum() >= MIN_BAND_PX:
            r["rise"] = float(np.median(parts["rise"][m]))
            r["grey residual"] = float(np.median((after - tb)[m]))
            r.update({f"changed | {a}": float(np.mean(outs[a]["t"][m] < CHANGED_T)) for a in SPREAD_ARMS})
        rows.append(r)
    inner = ndi.distance_transform_edt(valid) > SEAM_BORDER_PX
    gb = _seam_gradient(tb.astype(np.float32), valid)
    ring_starts = list(range(*SEAM_GATE_PX, SEAM_RING_PX))
    for a in ["as it is"] + SEAM_ARMS:
        corr = as_it_is(after, valid)["corrected"] if a == "as it is" else outs[a]["corrected"]
        gc = _seam_gradient(corr, valid)
        far = inner & (sd > FAR_PX)
        fr = np.median(gc[far]) / max(np.median(gb[far]), 1e-6)
        prof = []
        for d in ring_starts:
            m = inner & (sd > d) & (sd <= d + SEAM_RING_PX)
            prof.append(np.median(gc[m]) / max(np.median(gb[m]), 1e-6) / fr if m.sum() >= MIN_BAND_PX else np.nan)
        prof = np.array(prof)
        k = int(np.nanargmax(prof)) if np.isfinite(prof).any() else -1
        rows.append({"tile_id": tid, "kind": "seam", "band": a, "peak ring start": ring_starts[k] if k >= 0 else np.nan,
                     "peak": float(prof[k]) if k >= 0 else np.nan,
                     **{f"ring {d}": float(v) for d, v in zip(ring_starts, prof)}})
    return rows


if __name__ == "__main__":
    t = pd.read_csv(OUT + "tiles.csv")
    tiles = t.tile_id[(t.half == "choose") & t.fit].tolist()
    with Pool(3) as pool:
        d = pd.DataFrame([r for part in pool.imap(one, tiles) for r in part])
    d.to_csv(OUT + "posthoc_guard_check.csv", index=False)
    pd.set_option("display.width", 250)
    c = d[d.kind == "clear by distance"]
    cols = ["n", "rise", "grey residual"] + [f"changed | {a}" for a in SPREAD_ARMS]
    print("1. Guard's clear ground beyond the margin, by distance from the gate (choose half; medians over tiles; "
          "n = pooled pixels)")
    g = c.groupby("band", sort=False)
    tab = g[cols[1:]].median()
    tab.insert(0, "pixels (pooled)", g["n"].sum())
    tab.insert(1, "tiles", g["rise"].count())
    print(tab.round(3).T.to_string())
    s = d[d.kind == "seam"]
    print("\n2. Seam index peak, by arm (choose half): median peak, and the ring (px from the gate edge) where it peaks")
    print(s.groupby("band", sort=False).agg(peak=("peak", "median"), ring_median=("peak ring start", "median"),
                                            ring_q25=("peak ring start", lambda x: x.quantile(.25)),
                                            ring_q75=("peak ring start", lambda x: x.quantile(.75))).round(2).to_string())
    prof = s.groupby("band", sort=False)[[c for c in s.columns if c.startswith("ring ")]].median()
    print("\nmedian seam profile (ratio to far ground), selected rings")
    print(prof[[f"ring {k}" for k in (-8, -4, 0, 8, 16, 24, 32, 40, 48, 64, 80, 100, 120, 156)]].round(2).to_string())
