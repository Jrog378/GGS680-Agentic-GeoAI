"""The preregistered choice among the library arms only (sn8_cloudspot.choose on counts_library.csv), so the
SpaceNet 8 gate test can start before the DINOv3 benchmark finishes. Writes choice.json; summarise.py recomputes the
choice from the same counts and asserts it agrees."""
import json
import sys

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")

import pandas as pd

from sn8_cloudspot import LIBRARY_ARMS, choose

pd.set_option("display.width", 250)
counts = pd.read_csv(f"{HERE}/counts_library.csv")
chosen, table = choose(counts, LIBRARY_ARMS, "random forest")
print(table.round(4).to_string(index=False))
print("chosen:", chosen)
json.dump({"chosen": chosen, "columns": LIBRARY_ARMS[chosen], "table": table.round(5).to_dict("records")},
          open(f"{HERE}/choice.json", "w"), indent=1, default=float)
