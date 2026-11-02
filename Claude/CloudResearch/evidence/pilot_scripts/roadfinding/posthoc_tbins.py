"""POST-HOC (not in the test plan; written after the results): where in the cloud gate the after-image detectors find
road cells. Recall of road cells and the weighted share of cells called road, by the two-date fit's transmission t at
the cell centre (t = 1 clear, 0.2 the opaque limit), from run_roadfinding.py's cached out-of-fold probabilities.
Development tiles only. Writes posthoc_tbins.csv and posthoc_tbins.png here."""
import sys
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sn8_cloudroads import ARMS, CACHE_DIR, CELL_PX, _cache_key, arm_images, set_aside_roads, tile_layout
from sn8_data import split_tables

OUT = Path(__file__).resolve().parent
df, train, val, test, negative = split_tables(662)
dev = list(train.tile_id) + list(val.tile_id)
del test, negative
road_tiles = set(set_aside_roads().tile_id)
parts = []
for t in dev:
    imgs = arm_images(t)
    lay = tile_layout(t, imgs, keep_road_cells=t in road_tiles)
    lay["t"] = imgs["t"][lay.row * CELL_PX + CELL_PX // 2, lay.col * CELL_PX + CELL_PX // 2]
    parts.append(lay)
cells = pd.concat(parts, ignore_index=True)
z = np.load(CACHE_DIR / f"probs_{_cache_key(True)}_{_cache_key(False)}_{len(cells)}.npz")
key = lambda a: a.replace(" ", "_").replace("(", "").replace(")", "")
m = cells["eval"].to_numpy() & (cells.group == "correctable").to_numpy()
c = cells[m].copy()
bins = [0.2, 0.4, 0.6, 0.8, 1.0001]
c["t bin"] = pd.cut(c.t, bins, right=False, labels=["0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"])
rows = []
for a in ARMS:
    called = z[key(a)][m] >= 0.75
    for b, g in c.assign(called=called).groupby("t bin", observed=True):
        road = g.label == 1
        rows.append({"arm": a, "t bin": b, "tiles": g.tile_id.nunique(), "road cells": int(road.sum()),
                     "recall": float(g.called[road].mean()) if road.any() else np.nan,
                     "weighted share called road": float((g.weight * g.called).sum() / g.weight.sum())})
tab = pd.DataFrame(rows)
tab.round(4).to_csv(OUT / "posthoc_tbins.csv", index=False)
print(tab.round(4).to_string())
fig, ax = plt.subplots(figsize=(9, 4.5))
labels = list(c["t bin"].cat.categories)
for k, a in enumerate(ARMS):
    r = tab[tab.arm == a].set_index("t bin").reindex(labels)
    ax.bar(np.arange(len(labels)) + (k - 1.5) * 0.2, 100 * r.recall, 0.2, label=a)
n = tab[tab.arm == ARMS[0]].set_index("t bin").reindex(labels)["road cells"]
ax.set_xticks(range(len(labels)), [f"t {l}\n({int(v):,} road cells)" for l, v in zip(labels, n)])
ax.set_ylabel("road cells found (%)")
ax.set_title("Correctable cloud cells: road cells found by each arm's detector, by the two-date fit's t\n"
             "(post hoc; development tiles; cut-off 0.75; OSM roads)", fontsize=10)
ax.legend(fontsize=8)
plt.tight_layout()
fig.savefig(OUT / "posthoc_tbins.png", dpi=110)
