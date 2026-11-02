"""No-regression check (outputs/preregistration_cloud_gate.md): rerun sn8_refhaze.haze_recovery on the 94 clear
development tiles exactly as it is, and compare every number with the archived run (../haze_recovery.csv)."""
import sys
import time
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd

from sn8_refhaze import clear_tiles, haze_recovery

OUT = Path(__file__).resolve().parent
t0 = time.time()
d = haze_recovery(clear_tiles())
d.to_csv(OUT / "haze_recovery_rerun.csv", index=False)
old = pd.read_csv(OUT.parent / "haze_recovery.csv")
assert list(old.tile_id) == list(d.tile_id), "tile lists differ"
diff = (d.drop(columns="tile_id") - old.drop(columns="tile_id")).abs().max()
print("largest per-tile difference against the archived haze_recovery.csv, per column:")
print(diff.to_string())
print("\nmeans, rerun:")
print(d.drop(columns="tile_id").mean().round(4).to_string())
print("done", round(time.time() - t0), "s")
