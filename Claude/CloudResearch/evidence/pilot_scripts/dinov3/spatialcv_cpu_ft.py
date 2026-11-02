"""Spatial CV of the DINOv3 benchmark (Agent C, CPU), 2026-10-29: the B-trained stage of spatialcv_cpu.py rerun once all
5 B-ft outer folds exist. Research only; DINOv3 never enters the library.

Nothing in spatialcv_cpu.py is changed: it is imported and its stage_b_trained() is called with spatialcv_common.OUT
pointed at the new folder spatialcv_ft/, so last night's spatialcv_calls_B-trained_*.csv and spatialcv_heldout_cues.csv
are left as they are. Check: every arm that does not use the fine-tuned cues must give last night's calls, call for call.

    OMP_NUM_THREADS=1 /opt/miniconda3/bin/python3 -I spatialcv_cpu_ft.py > spatialcv_ft/spatialcv_cpu_B-trained.log 2>&1
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
sys.argv = sys.argv[:1]
import spatialcv_common as C
import spatialcv_cpu as CPU

import numpy as np
import pandas as pd

OUT = HERE / "spatialcv_ft"
OUT.mkdir(exist_ok=True)
assert all((C.FOLD_DIR / f"B-ft_outer{k}.npz").exists() for k in range(C.N_FOLDS)), "B-ft folds missing"
sha0 = hashlib.sha256(CPU.REGISTRY.read_bytes()).hexdigest()
C.OUT = OUT
CPU.stage_b_trained()
assert hashlib.sha256(CPU.REGISTRY.read_bytes()).hexdigest() == sha0
for s in ("798", "891"):
    new, old = pd.read_csv(OUT / f"spatialcv_calls_B-trained_{s}.csv"), pd.read_csv(HERE / f"spatialcv_calls_B-trained_{s}.csv")
    assert new.tile_id.equals(old.tile_id) and new.road_id.equals(old.road_id)
    for col in old.columns:
        same = int((new[col].to_numpy() == old[col].to_numpy()).sum())
        CPU.say(f"check {s}, {col}: {same} of {len(old)} equal last night's file")
        assert same == len(old), col
    assert set(roads_split := pd.read_csv(OUT / "spatialcv_heldout_cues.csv").split) <= {"train", "val"}
CPU.say(f"done; production.json sha256 {sha0[:12]} unchanged")
