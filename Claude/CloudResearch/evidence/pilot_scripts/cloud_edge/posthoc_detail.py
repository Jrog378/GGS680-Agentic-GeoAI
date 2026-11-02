"""POST-HOC (after the selection and the report-stage tables; not used to choose anything): detail per band relative to
the before image, so a contrast stretch shows. Per tile and band: median local contrast of tone(before); the arm's
band detail (arms_tiles.csv) over it, divided by the same ratio on far clear ground (1 = the after/before contrast
relation of far clear ground). Every gate tile, both halves reported separately."""
import sys
from multiprocessing import Pool
sys.path.append("/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_edge")
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd
from sn8_clouds import _tile
from sn8_cloudedge import BANDS_PX, MIN_BAND_PX, edge_parts
from sn8_refhaze import local_contrast
OUT = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_edge/"
ARMS_SHOWN = ["as it is", "current", "e: He 2013 r50, eps 0.01", "a: soft gate 0.25, cap 160", "a: soft gate 0.5, cap 80",
              "b: data fade 80"]


def one(tid):
    _, before, after, valid = _tile(tid)
    parts = edge_parts(before, after, valid)
    lc = local_contrast(parts["tone"](before).astype(np.float32))
    use = valid & ~parts["base"]["opaque"]
    sd = parts["sd"]
    row = {"tile_id": tid}
    for name, (lo, hi) in BANDS_PX.items():
        m = use & (sd > lo) & (sd <= hi)
        row[name] = float(np.median(lc[m])) if m.sum() >= MIN_BAND_PX else np.nan
    return row


if __name__ == "__main__":
    from cloud_edge import arm_rows
    t = pd.read_csv(OUT + "tiles.csv")
    with Pool(3) as pool:
        b = pd.DataFrame(pool.map(one, t.tile_id[t.fit].tolist())).set_index("tile_id")
    b.to_csv(OUT + "posthoc_before_detail.csv")
    d = arm_rows()
    pd.set_option("display.width", 250)
    for half in ("choose", "report"):
        rows = {}
        for arm in ARMS_SHOWN:
            g = d[(d.arm == arm) & (d.half == half)].set_index("tile_id")
            r = pd.DataFrame({k: g[f"detail | {k}"] / b.loc[g.index, k] for k in BANDS_PX})
            rows[arm] = r.div(r["far"], axis=0).median()
        print(f"\n{half} half: detail relative to the before image, over the same ratio on far clear ground "
              "(median over tiles; 1 = as on far clear ground)")
        print(pd.DataFrame(rows).T.round(2).to_string())
