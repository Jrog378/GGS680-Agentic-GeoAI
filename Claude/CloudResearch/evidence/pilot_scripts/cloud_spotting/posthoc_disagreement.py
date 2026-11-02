"""POST HOC (chosen after seeing gate.log): pictures of where the two road rules disagree. The tile with the most
roads that only the spotter gate keeps (production's dark-rise rule sets them aside) and the tile with the most roads
that only production keeps (the spotter sets them aside); ties go to the first tile id in sorted order. Also prints
those roads' labels and shares."""
import sys

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append(HERE)

import pandas as pd

from figures import FIG, LIBRARY_ARMS, CloudSpotter, chosen, sn8_gate_figure

g = pd.read_csv(f"{HERE}/gate_roads.csv")
assert set(g.split) <= {"train", "val"}
kp = g.filter(like="call: production").iloc[:, 0] >= 0
ks = g.filter(like="call: spotter").iloc[:, 0] >= 0
g["only"] = None
g.loc[ks & ~kp, "only"] = "kept by spotter only"
g.loc[kp & ~ks, "only"] = "kept by production only"
cols = ["tile_id", "road_id", "flooded", "cloudy", "cloud_dark_rise_road", "spot_road", "spot_tile"]
spotter = CloudSpotter(LIBRARY_ARMS[chosen]).fit()
for label, tag in (("kept by spotter only", "spotter_keeps"), ("kept by production only", "production_keeps")):
    sub = g[g.only == label]
    per = sub.groupby("tile_id").size()
    print(f"\n{label}: {len(sub)} roads on {len(per)} tiles; flooded {int(sub.flooded.sum())}")
    print(per.sort_values(ascending=False).head(6).to_string())
    tid = sorted(per[per == per.max()].index)[0]
    print(sub[sub.tile_id == tid][cols].round(3).to_string(index=False))
    sn8_gate_figure(tid, spotter, f"{FIG}/posthoc_sn8_{tid}_{tag}.png",
                    note=f"POST HOC: the tile with the most roads {label} ({int(per.max())}).")
