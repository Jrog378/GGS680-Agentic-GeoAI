"""Spatial CV of the DINOv3 benchmark (Agent C), 2026-10-30: the 26 Oct report rerun once all 5 A-ft outer folds exist.
Research only; DINOv3 never enters the library. CPU only; nothing is refitted (it only reads spatialcv_folds/).

spatialcv_report.py is not changed. Its source is run here, in this folder, with two text edits:
  - the Track A figure's footnote no longer says "A-ft was not run";
  - only the pictures that show A-ft are redrawn (figure_a, figure_folds, figure_tile_a). The Track B pictures read
    inputs that have not changed since 26 Oct, so they are left as they are.
The report scores A-ft exactly like A-head: per outer fold, the cut-off chosen on inner fold 1
(spatialcv_folds/A-ft_outer*.json), held-out validation-split cells (primary) and all held-out cells weighted to the
real road share (secondary), block-resampled F1 intervals and F1-difference intervals (2,000, seed 662), no McNemar on
cells (the plan).

Back up first (done 2026-10-30): spatialcv_numbers.json, spatialcv_tables.md, spatialcv_calls_cells.npz,
spatialcv_trackA_f1.png and spatialcv_per_fold.png were copied to <name>_before_aft.<ext>.

    OMP_NUM_THREADS=2 /opt/miniconda3/bin/python3 -I spatialcv_report_aft.py > spatialcv_report_aft.log 2>&1
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
for name in ("spatialcv_numbers.json", "spatialcv_tables.md", "spatialcv_calls_cells.npz", "spatialcv_trackA_f1.png",
             "spatialcv_per_fold.png"):
    p = HERE / name
    assert (HERE / f"{p.stem}_before_aft{p.suffix}").exists(), f"back up {name} first"

src_path = HERE / "spatialcv_report.py"
src = src_path.read_text()
edits = [
    ('A-ft was "\n             "not run (GPU budget; see the write-up).',
     'A-ft does the same.'),
    ("for fn in (figure_b, lambda: figure_b(\"891\"), figure_a, figure_folds, figure_tile_b, figure_tile_a):",
     "for fn in (figure_a, figure_folds, figure_tile_a):"),
]
for old, new in edits:
    assert src.count(old) == 1, old
    src = src.replace(old, new)
g = {"__file__": str(src_path), "__name__": "spatialcv_report_aft"}
exec(compile(src, str(src_path), "exec"), g)
