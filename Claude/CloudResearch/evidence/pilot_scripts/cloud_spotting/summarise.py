"""Tables, tool impacts, the preregistered choice and the DINOv3 benchmark gap, from counts_library.csv and
counts_benchmark.csv (run_cv.py). Written before either file existed. Writes numbers.json and summary.log (stdout)."""
import json
import sys

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
sys.path.append(HERE)

import pandas as pd

from sn8_cloudspot import LIBRARY_ARMS, choose, paired_f1, pooled_table

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 30)
lib = pd.read_csv(f"{HERE}/counts_library.csv")
bench = pd.read_csv(f"{HERE}/counts_benchmark.csv")
counts = pd.concat([lib, bench], ignore_index=True)
assert counts.image.nunique() == 120
TYPES = sorted(counts.type.unique())
RULES = ["rule: bright", "rule: dark", "rule: bright OR dark", "rule: bright AND dark"]
BENCH = list(bench.arm.unique())
out = {}

# 1. every arm, overall (random forest primary; linear probe secondary)
for learner in ("random forest", "linear probe"):
    sub = counts[(counts.learner == learner) | counts.arm.isin(RULES)]
    t = pooled_table(sub)
    print(f"\n== overall, learner {learner} (fixed rules have learner 'none') ==\n{t.round(3).to_string(index=False)}")
    out[f"overall: {learner}"] = t.round(4).to_dict("records")

# 2. by land cover (random forest + rules), F1 and IoU with intervals resampled within the type
rows = []
for ty in TYPES:
    sub = counts[(counts.type == ty) & ((counts.learner == "random forest") | counts.arm.isin(RULES))]
    rows.append(pooled_table(sub).assign(type=ty))
by = pd.concat(rows, ignore_index=True)
out["by land cover: random forest"] = by.round(4).to_dict("records")
print("\n== F1 by land cover (random forest; 95% CI resampled within the type) ==")
print(by.assign(F1s=by.F1.round(3).astype(str) + " [" + by["F1 95% CI"] + "]")
      .pivot(index="arm", columns="type", values="F1s").loc[by.arm.unique()].to_string())
print("\n== precision / recall by land cover (random forest) ==")
print(by.assign(PR=by.precision.round(2).astype(str) + " / " + by.recall.round(2).astype(str))
      .pivot(index="arm", columns="type", values="PR").loc[by.arm.unique()].to_string())

# 3. paired against the dark rule (production's dark mask)
rf = "random forest"
vs_dark = pd.DataFrame([paired_f1(counts, a, "rule: dark", rf, "none") for a in list(LIBRARY_ARMS) + BENCH]
                       + [paired_f1(counts, r, "rule: dark", "none", "none") for r in RULES if r != "rule: dark"])
print(f"\n== F1 minus the dark rule's, paired (same resampled images) ==\n"
      f"{vs_dark.drop(columns=['ci_low', 'ci_high']).round(4).to_string(index=False)}")
out["vs dark rule"] = vs_dark.round(5).to_dict("records")
vd_type = []
for a in list(LIBRARY_ARMS) + BENCH:
    for ty in TYPES:
        p = paired_f1(counts, a, "rule: dark", rf, "none", types=[ty])
        vd_type.append({"arm": a, "type": ty, "F1 - dark rule": p["F1 a - b"], "95% CI": p["95% CI"]})
vd_type = pd.DataFrame(vd_type)
out["vs dark rule by land cover"] = vd_type.round(4).to_dict("records")
print("\n== F1 minus the dark rule's, by land cover ==")
print(vd_type.assign(s=vd_type["F1 - dark rule"].map("{:+.3f}".format) + " [" + vd_type["95% CI"] + "]")
      .pivot(index="arm", columns="type", values="s").loc[list(LIBRARY_ARMS) + BENCH].to_string())

# 4. tool impacts: gain when added, loss when removed (preregistered pairs)
IMPACTS = [
    ("gain: dark added to bright", "bright + dark", "bright"),
    ("gain: bright added to dark", "bright + dark", "dark"),
    ("gain: texture added to bright + dark", "classical", "bright + dark"),
    ("gain: DINOv2 added to classical", "classical + DINOv2", "classical"),
    ("gain: classical added to DINOv2", "classical + DINOv2", "DINOv2"),
    ("loss: bright removed from classical + DINOv2", "classical + DINOv2", "classical + DINOv2 - bright"),
    ("loss: dark removed from classical + DINOv2", "classical + DINOv2", "classical + DINOv2 - dark"),
    ("loss: texture removed from classical + DINOv2", "classical + DINOv2", "classical + DINOv2 - texture"),
    ("loss: DINOv2 removed from classical + DINOv2", "classical + DINOv2", "classical"),
    ("benchmark gain: DINOv3 added to classical", "classical + DINOv3", "classical"),
    ("benchmark gain: DINOv3 added to DINOv2", "DINOv2 + DINOv3", "DINOv2"),
    ("benchmark gain: DINOv3 added to classical + DINOv2", "everything", "classical + DINOv2"),
    ("benchmark gain: classical added to DINOv3", "classical + DINOv3", "DINOv3"),
    ("benchmark loss: bright removed from everything", "everything", "everything - bright"),
    ("benchmark loss: dark removed from everything", "everything", "everything - dark"),
    ("benchmark loss: texture removed from everything", "everything", "everything - texture"),
    ("benchmark loss: DINOv2 removed from everything", "everything", "classical + DINOv3"),
    ("benchmark loss: DINOv3 removed from everything", "everything", "classical + DINOv2"),
]
imp, imp_type = [], []
for label, a, b in IMPACTS:
    p = paired_f1(counts, a, b, rf, rf)
    imp.append({"impact": label, "F1 with - without": p["F1 a - b"], "95% CI": p["95% CI"],
                "images with higher": p["images a higher"], "images without higher": p["images b higher"],
                "sign test p": p["sign test p"]})
    for ty in TYPES:
        q = paired_f1(counts, a, b, rf, rf, types=[ty])
        imp_type.append({"impact": label, "type": ty, "dF1": q["F1 a - b"], "95% CI": q["95% CI"]})
imp, imp_type = pd.DataFrame(imp), pd.DataFrame(imp_type)
print(f"\n== tool impacts (random forest; F1 with the tool minus without, paired) ==\n{imp.round(4).to_string(index=False)}")
print("\n== tool impacts by land cover ==")
print(imp_type.assign(s=imp_type.dF1.map("{:+.3f}".format) + " [" + imp_type["95% CI"] + "]")
      .pivot(index="impact", columns="type", values="s").loc[imp.impact].to_string())
out["impacts"] = imp.round(5).to_dict("records")
out["impacts by land cover"] = imp_type.round(4).to_dict("records")

# 5. the preregistered choice (library arms only) and the benchmark gap
chosen, table = choose(counts, LIBRARY_ARMS, rf)
print(f"\n== choice among the library arms ==\n{table.round(4).to_string(index=False)}\nchosen: {chosen}")
f1 = {a: r["F1"] for a, r in pooled_table(counts[counts.learner == rf]).set_index("arm").iterrows()}
best_bench = max(BENCH, key=lambda a: f1[a])
gap = paired_f1(counts, best_bench, chosen, rf, rf)
best_lib = table.sort_values("F1").arm.iloc[-1]
gap_best = paired_f1(counts, best_bench, best_lib, rf, rf)
print(f"benchmark: best DINOv3 arm {best_bench} F1 {f1[best_bench]:.4f}; chosen {chosen} F1 {f1[chosen]:.4f} "
      f"({100 * f1[chosen] / f1[best_bench]:.1f}% of it); gap {gap['F1 a - b']:+.4f} [{gap['95% CI']}]; "
      f"best library arm {best_lib}: gap {gap_best['F1 a - b']:+.4f} [{gap_best['95% CI']}]")
chosen_vs_dark = paired_f1(counts, chosen, "rule: dark", rf, "none")
print(f"chosen vs the dark rule: {chosen_vs_dark['F1 a - b']:+.4f} [{chosen_vs_dark['95% CI']}], "
      f"sign test {chosen_vs_dark['images a higher']} / {chosen_vs_dark['images b higher']}, p = {chosen_vs_dark['sign test p']:.3g}")
out["choice"] = {"table": table.round(5).to_dict("records"), "chosen": chosen, "columns": LIBRARY_ARMS[chosen],
                 "best library arm": best_lib, "best benchmark arm": best_bench,
                 "benchmark gap (best benchmark - chosen)": {k: gap[k] for k in ("F1 a - b", "95% CI")},
                 "benchmark gap (best benchmark - best library)": {k: gap_best[k] for k in ("F1 a - b", "95% CI")},
                 "chosen share of benchmark F1": f1[chosen] / f1[best_bench],
                 "chosen vs dark rule": {k: chosen_vs_dark[k] for k in ("F1 a - b", "95% CI", "images a higher",
                                                                          "images b higher", "sign test p")}}
json.dump(out, open(f"{HERE}/numbers.json", "w"), indent=1, default=float)
print("\nsaved numbers.json")
assert chosen == json.load(open(f"{HERE}/choice.json"))["chosen"], "choice differs from choose.py's"
