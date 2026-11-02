"""Redraws phase1_cells_0_14_7.png with the title row unclipped (the same three detectors, refitted on the training
cells exactly as run_phase1.py fits them; cut-offs from phase1_numbers.json). No new scores."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import dinov3_bench as d3

import matplotlib
matplotlib.use("Agg")
from sn8_detect import CELL_FEATURES
from sn8_dino_cells import DINO_CELL_FEATURES, cell_basis, cell_dino_table
from sn8_models import classical_models
from sn8_stages import production_detector

n = json.loads((HERE / "phase1_numbers.json").read_text())
cuts = n["Track A"]["cut-offs"]
tile_a = n["pictures"]["tile A"]
cells = cell_dino_table("train")
c3 = d3.cell_dino3_table("train")
assert c3.tile_id.equals(cells.tile_id) and c3.row.equals(cells.row)
cells[d3.DINO3_CELL_FEATURES] = c3[d3.DINO3_CELL_FEATURES].to_numpy()
sets = {"classical + DINOv2": CELL_FEATURES + DINO_CELL_FEATURES, "classical + DINOv3": CELL_FEATURES + d3.DINO3_CELL_FEATURES,
        "DINOv3 only": d3.DINO3_CELL_FEATURES}
runs = [(name, classical_models()[production_detector()].fit(cells[cols], cells.label), cols, cuts[name])
        for name, cols in sets.items()]
d3.show_cells_pair(tile_a, runs, d3.all_cells3(tile_a, cell_basis(), d3.cell_basis3()), HERE / f"phase1_cells_{tile_a}.png")
print("redrawn", tile_a)
