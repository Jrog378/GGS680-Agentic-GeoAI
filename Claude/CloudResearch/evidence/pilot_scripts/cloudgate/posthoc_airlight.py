"""POST-HOC (not in the plan): in S1, the airlight the method estimates against the synthetic truth (240), and the
share of the thickest synthetic haze (true t < 0.4) left opaque. Also: real development tiles with an empty existing
gate (the empty-gate quirk of dark_reference_dehaze applies there)."""
import sys
from multiprocessing import Pool
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd

def one(job):
    i, tid = job
    import cv2; cv2.setNumThreads(1)
    from sn8_clouds import _tile
    from sn8_cloudsym import either_date_dehaze
    from sn8_refhaze import synthetic_haze
    p, before, after, valid = _tile(tid)
    hazy, t_true = synthetic_haze(after, valid, 662 + i)
    o = either_date_dehaze(before, hazy, valid)
    core = valid & (t_true < 0.4)
    return {"tile_id": tid, "airlight": o["airlight after"], "core px": int(core.sum()),
            "core opaque": float(o["cannot"][core].mean()) if core.any() else np.nan,
            "t estimated in core (median)": float(np.nanmedian(o["t after"][core])) if core.any() else np.nan}

if __name__ == "__main__":
    from sn8_refhaze import clear_tiles
    with Pool(4) as pool:
        d = pd.DataFrame(pool.map(one, list(enumerate(clear_tiles()))))
    print(d.describe().round(3).to_string())
    r = pd.read_csv(Path(__file__).resolve().parent / "real_tiles.csv")
    ex = r[r.arm == "existing two-date"]
    print("\nreal development tiles with an empty existing gate:", int((ex["gated share"] == 0).sum()), "of", len(ex))
