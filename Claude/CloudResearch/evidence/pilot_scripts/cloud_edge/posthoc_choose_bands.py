"""POST-HOC (written after the choose-half selection, before any report-half number was looked at): choose-half band
medians for the main arms, to see where the ring sits and what the a/b arms change. Choose half only."""
import sys
sys.path.append("/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_edge")
import pandas as pd
from cloud_edge import arm_rows
from sn8_cloudedge import BANDS_PX
d = arm_rows()
h = d[d.half == "choose"]
arms = ["as it is", "current", "a: soft gate 0.25, cap 160", "a: soft gate 0.5, cap 80", "b: data fade 40", "b: data fade 80",
        "c: guided r20, eps 0.0001", "d: window 11", "e: He 2013 r20, eps 0.01", "e: He 2013 r50, eps 0.01"]
pd.set_option("display.width", 250)
for k in ("residual", "hazy share", "grey residual", "detail"):
    t = pd.DataFrame({a: [h[h.arm == a][f"{k} | {b}"].median() for b in BANDS_PX] for a in arms}, index=list(BANDS_PX)).T
    print(f"\n{k} (choose half, median over tiles of each tile's band value)")
    print(t.round(2).to_string())
