"""Spatial CV of the DINOv3 benchmark (Agent C), 2026-10-29: last night's report rerun with the B-ft and A-ft folds.
Research only; DINOv3 never enters the library. CPU only; nothing is refitted.

spatialcv_report.py is not changed. Its source is run here with two differences, so that last night's outputs stay:
  - spatialcv_common.OUT points at spatialcv_ft/ (numbers, tables, cell calls, pictures are written there);
  - the trained-cue calls are read from spatialcv_ft/ (spatialcv_cpu_ft.py), not from last night's file.
Then the trained-cue arms are also paired against the best combo on the 798 roads (the report pairs them with it on the
891 only), and those rows go to spatialcv_ft/spatialcv_numbers_ft_extra.json.

    /opt/miniconda3/bin/python3 -I spatialcv_report_ft.py > spatialcv_ft/spatialcv_report.log 2>&1
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import spatialcv_common as C

OUT = Path(os.environ.get("SPATIALCV_FT_OUT", HERE / "spatialcv_ft"))   # override: code check only
assert (OUT / "spatialcv_calls_B-trained_798.csv").exists(), "run spatialcv_cpu_ft.py first"
C.OUT = OUT
src_path = HERE / "spatialcv_report.py"
src = src_path.read_text()
old = 'HERE / f"spatialcv_calls_B-trained_{set_name}.csv"'
assert src.count(old) == 1
src = src.replace(old, 'C.OUT / f"spatialcv_calls_B-trained_{set_name}.csv"')
g = {"__file__": str(src_path), "__name__": "spatialcv_report_ft"}
exec(compile(src, str(src_path), "exec"), g)

import numpy as np
import pandas as pd

BT, B, BEST, say = g["BT"], g["B"], g["BEST"], g["say"]
rows = []
for s in ("798", "891"):
    calls, frozen = BT[s]["calls"], B[s]["calls"]
    assert frozen.tile_id.equals(calls.tile_id) and frozen.road_id.equals(calls.road_id)
    y, blocks = calls.flooded.to_numpy(), calls.block.to_numpy()
    for n, p in BT[s]["S"].items():
        if "head" in n or "fine-tuned" in n:
            rows.append({"set": s, "arm": n, "against": BEST + " (best combo)", **C.paired(p, B[s]["S"][BEST], y, blocks)})
extra = pd.DataFrame(rows)
(OUT / "spatialcv_numbers_ft_extra.json").write_text(json.dumps({"trained-cue arms against the best combo": C.tidy(extra)},
                                                                indent=1))
say("trained-cue arms against the best combo\n" + extra.to_string())
