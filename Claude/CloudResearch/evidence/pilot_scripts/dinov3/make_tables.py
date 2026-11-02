"""Markdown tables from phase1_numbers.json / phase2_numbers.json, for evidence/11_dinov3_baseline.md (no new scores).
    /opt/miniconda3/bin/python3 -I make_tables.py phase1 > tables_phase1.md"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def md(rows, cols=None, rename=None):
    if not rows:
        return "(none)\n"
    cols = cols or list(rows[0])
    rename = rename or {}
    head = "| " + " | ".join(rename.get(c, c) for c in cols) + " |"
    out = [head, "|" + "---|" * len(cols)]
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, float):
                v = f"{v:.4f}" if c in ("McNemar p",) else (f"{v:+.3f}" if "difference" in c else f"{v:.3f}")
            cells.append("" if v is None else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


which = sys.argv[1] if len(sys.argv) > 1 else "phase1"
n = json.loads((HERE / f"{which}_numbers.json").read_text())
CONF = ["features", "TP", "FN", "FP", "TN", "accuracy", "accuracy 95% CI", "precision", "recall", "dry kept dry", "F1", "MCC"]
PAIR = ["arm", "against", "accuracy difference", "95% CI", "roads fixed", "roads broken", "McNemar p"]
if which == "phase1":
    print("## Track B, 891 roads\n")
    print(md(n["Track B"]["891 roads"], CONF, {"features": "arm"}))
    print("## Track B, 891 roads, paired\n")
    print(md(n["Track B"]["891 paired"], PAIR))
    print("## Track B, 798 roads\n")
    print(md(n["Track B"]["798 roads"], CONF, {"features": "arm"}))
    print("## Track B, 798 roads, paired\n")
    print(md(n["Track B"]["798 paired"], PAIR))
    print("## DINOv3 single cues\n")
    print(md(n["Track B"]["DINOv3 single cues"], ["features", "TP", "FN", "FP", "TN", "accuracy", "accuracy 95% CI", "MCC"]))
    print("## Track A\n")
    print(md(n["Track A"]["validation cells"]))
    print(md(n["Track A"]["counts"]))
    print(md(n["Track A"]["pairs"]))
    print(json.dumps({k: n[k] for k in ("times (s)", "DINOv2 reproduction (now, logged)", "data", "pictures")}, indent=1))
else:
    for k, v in n["Track B"].items():
        print(f"## Track B, {k}: {v['roads']}\n")
        print(md(v["confusion"], CONF, {"features": "arm"}))
        print(md(v["paired"], PAIR))
    print("## Track A\n")
    print(md(n["Track A"]["validation cells"]))
    print(md(n["Track A"]["counts"]))
    print(md(n["Track A"]["pairs"]))
    print(json.dumps({k: n[k] for k in ("times (s)", "chosen", "data", "pictures")}, indent=1))
    for k, h in n["loss curves"].items():
        print(k, [(r["epoch"], round(r["train loss"], 4), round(r.get("eval loss", float("nan")), 4)) for r in h])
