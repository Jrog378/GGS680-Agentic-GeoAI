"""Spatial CV of the DINOv3 research benchmark (Agent C): tables, numbers and pictures from the saved calls. CPU only;
nothing is refitted here except reading what spatialcv_cpu.py and spatialcv_gpu.py wrote.

    /opt/miniconda3/bin/python3 -I spatialcv_report.py > spatialcv_report.log 2>&1
Writes spatialcv_numbers.json, spatialcv_tables.md, spatialcv_calls_cells_val.npz and the spatialcv_*.png pictures.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE))
import spatialcv_common as C

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

say = C.Log()
INK, MUTED, GRID_C, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
PROD = "base + DINOv2 cues (production)"
BEST = "base + DINOv2 cues + vector"
PH1 = json.loads((HERE / "phase1_numbers.json").read_text())
PH2 = json.loads((HERE / "phase2_numbers.json").read_text())
NUM = {"run": time.strftime("%Y-%m-%dT%H:%M:%S"), "plan": "outputs/preregistration_spatial_cv.md (Agent C)",
       "folds": "spatial_folds / cell_folds / nested_*_folds, seed 662, 3 x 3-tile blocks, purge route",
       "code sha256 (first 12)": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in
                                  sorted(HERE.glob("spatialcv_*.py")) + [HERE.parent / "spatial_cv" / "spatial_folds.py"]}}
MD = []


def md_table(df, cols=None):
    df = df[cols] if cols else df
    out = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r.values) + " |")
    return "\n".join(out)


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID_C)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="x", color=GRID_C, linewidth=0.6)
    ax.set_axisbelow(True)


def ci(text):
    lo, hi = (float(x) for x in text.split("-") if x)
    return lo, hi


# ======================================================================================================================
# Track B
# ======================================================================================================================
def b_tables(calls, prefix, pairs, set_name):
    """Reports and paired tests for the arms in `calls` (columns '<prefix>: arm'), blocks resampled."""
    y = calls.flooded.to_numpy()
    blocks = calls.block.to_numpy()
    arms = {c.split(": ", 1)[1]: calls[c].to_numpy() for c in calls.columns if c.startswith(prefix + ": ")}
    rep = C.road_report(arms, y, blocks)
    pr = []
    for cand, base in pairs:
        if cand in arms and base in arms:
            pr.append({"set": set_name, "arm": cand, "against": base, **C.paired(arms[cand], arms[base], y, blocks)})
    return arms, rep, pd.DataFrame(pr)


def per_fold_acc(calls, arms):
    f = calls.outer_fold.to_numpy()
    y = calls.flooded.to_numpy()
    return {n: [float(np.mean(p[f == k] == y[f == k])) for k in range(1, 6)] for n, p in arms.items()}


sys.argv = sys.argv[:1]
import spatialcv_cpu as CPU   # arm names and pairs only (its stages run only when named on the command line)

B = {}
for set_name in ("891", "798"):
    path = HERE / f"spatialcv_calls_B-frozen_{set_name}.csv"
    if not path.exists():
        continue
    calls = pd.read_csv(path)
    arms_s, rep_s, pr_s = b_tables(calls, "S", CPU.PAIRS_B, set_name)
    arms_t, rep_t, _ = b_tables(calls, "T", [], set_name)
    y = calls.flooded.to_numpy()
    # optimism: tile-fold minus spatial-fold accuracy on the same roads (blocks resampled for the interval)
    opt = [{"arm": n, **{k: v for k, v in C.paired(arms_t[n], arms_s[n], y, calls.block.to_numpy()).items()
                         if k in ("difference", "95% CI", "roads fixed", "roads broken", "McNemar p")}}
           for n in arms_s]
    B[set_name] = {"calls": calls, "S": arms_s, "T": arms_t, "rep S": rep_s, "rep T": rep_t, "pairs": pr_s,
                   "optimism": pd.DataFrame(opt), "per fold": per_fold_acc(calls, arms_s)}
    say(f"Track B frozen, {set_name} roads: S\n" + rep_s.to_string() + "\n" + pr_s.to_string())

BT = {}
for set_name in ("891", "798"):
    path = HERE / f"spatialcv_calls_B-trained_{set_name}.csv"
    if not path.exists():
        continue
    calls = pd.read_csv(path)
    pairs = [("base + DINOv2 cues + DINOv3 fine-tuned cues", PROD), ("base + DINOv2 cues + DINOv3 head cues", PROD),
             ("base + DINOv3 fine-tuned cues", PROD), ("base + DINOv3 head cues", PROD),
             ("base + DINOv3 fine-tuned cues", "base + DINOv3 cues (frozen)"),
             ("base + DINOv3 head cues", "base + DINOv3 cues (frozen)"), ("base + DINOv3 cues (frozen)", PROD),
             ("base + DINOv2 cues + DINOv3 fine-tuned cues", "base + DINOv2 cues + DINOv3 head cues"),
             ("base + DINOv3 fine-tuned cues", "base + DINOv3 head cues"),
             ("DINOv3 fine-tuned cues", "DINOv2 cues"), ("DINOv3 fine-tuned cues", "DINOv3 cues (frozen)"),
             ("DINOv3 head cues", "DINOv3 cues (frozen)"), ("DINOv3 head cues", "DINOv2 cues"),
             ("DINOv3 cues (frozen)", "DINOv2 cues"), (PROD, "base (production without DINO)")]
    arms, rep, pr = b_tables(calls, "S", pairs, set_name)
    if set_name == "891" and "891" in B:   # against the best combo (production + DINOv2 vector) on the same roads
        frozen = B["891"]["calls"]
        assert frozen.tile_id.equals(calls.tile_id) and frozen.road_id.equals(calls.road_id)
        best = B["891"]["S"][BEST]
        y = calls.flooded.to_numpy()
        extra = [{"set": "891", "arm": n, "against": BEST + " (best combo)", **C.paired(arms[n], best, y,
                                                                                        calls.block.to_numpy())}
                 for n in arms if "head" in n or "fine-tuned" in n]
        pr = pd.concat([pr, pd.DataFrame(extra)], ignore_index=True)
        # the frozen arms in both files are the same model on the same folds: their calls must agree
        for n in ("base (production without DINO)", PROD, "DINOv2 cues"):
            assert np.array_equal(arms[n], B["891"]["S"][n]), n
    BT[set_name] = {"calls": calls, "S": arms, "rep S": rep, "pairs": pr, "per fold": per_fold_acc(calls, arms)}
    say(f"Track B trained cues, {set_name} roads: S\n" + rep.to_string() + "\n" + pr.to_string())

# ======================================================================================================================
# Track A
# ======================================================================================================================
A = None
rf_files = sorted(C.FOLD_DIR.glob("A-rf_*_outer*.npz"))
nn_done = {n: all((C.FOLD_DIR / f"{n}_outer{k}.npz").exists() for k in range(5)) for n in ("A-head", "A-ft")}
if rf_files or any(nn_done.values()):
    from sn8_detect import cell_table
    cells = pd.concat([cell_table(s)[["tile_id", "row", "col", "label"]].assign(split=s) for s in ("train", "val")],
                      ignore_index=True)
    ntr = int((cells.split == "train").sum())
    ft_, tile_fold, _ = C.tile_folds_662()
    block = cells.tile_id.map(dict(zip(ft_.tile_id, ft_.block))).to_numpy()
    fold = cells.tile_id.map(tile_fold).to_numpy()
    y = cells.label.to_numpy()
    real = PH1["data"]["road share sampled / real"][1]
    s_tr = float((cells.label[cells.split == "train"] == 1).mean())
    # all held-out cells weighted to the real road share: training-split not-road cells as f1_cutoff weights them;
    # validation-split cells are a uniform sample and keep weight 1
    w = np.where((cells.split == "train").to_numpy() & (y == 0), (1 - real) / real * s_tr / (1 - s_tr), 1.0)
    called = {}
    rf_names = {"classical + DINOv2 (production)": "classical + DINOv2 (production), frozen",
                "classical + DINOv3": "classical + DINOv3, frozen", "DINOv3 only": "DINOv3 only, frozen",
                "DINOv2 only": "DINOv2 only, frozen"}
    cuts = {}
    for name, label in rf_names.items():
        files = [C.FOLD_DIR / f"A-rf_{name.replace(' ', '_').replace('+', 'and')}_outer{k}.npz" for k in range(5)]
        if not all(f.exists() for f in files):
            continue
        c = np.full(len(cells), -1, int)
        for f in files:
            z = np.load(f)
            c[z["idx"]] = (z["prob"] >= float(z["cut"])).astype(int)
            cuts[label] = float(z["cut"])
        assert (c >= 0).all()
        called[label] = c.astype(bool)
    nn_cut = {}
    for name, label in (("A-head", "DINOv3 linear head on frozen tokens"),
                        ("A-ft", "DINOv3 fine-tuned (last 2 blocks + head)")):
        if not nn_done[name]:
            continue
        c = np.full(len(cells), -1, int)
        nn_cut[label] = []
        for k in range(5):
            z = np.load(C.FOLD_DIR / f"{name}_outer{k}.npz")
            info = json.loads((C.FOLD_DIR / f"{name}_outer{k}.json").read_text())
            cut = info["cut-off (inner fold 1)"]
            nn_cut[label].append(cut)
            c[z["idx_train"]] = z["prob_train"] >= cut
            c[ntr + z["idx_val"]] = z["prob_val"] >= cut
        assert (c >= 0).all()
        called[label] = c.astype(bool)
    base = "classical + DINOv2 (production), frozen"
    if base in called:
        va = (cells.split == "val").to_numpy()
        rep_val = C.cell_report(y[va], {n: c[va] for n, c in called.items()}, block[va], base)
        rep_all = C.cell_report(y, called, block, base, w=w)
        per_fold = {n: {"val cells": [C.f1_of(y[va & (fold == k)], c[va & (fold == k)]) for k in range(5)],
                        "all cells (weighted)": [C.f1_of(y[fold == k], c[fold == k], w[fold == k]) for k in range(5)]}
                    for n, c in called.items()}
        pairs = []
        for cand, ag in (("DINOv3 fine-tuned (last 2 blocks + head)", "classical + DINOv3, frozen"),
                         ("DINOv3 fine-tuned (last 2 blocks + head)", "DINOv3 only, frozen"),
                         ("DINOv3 fine-tuned (last 2 blocks + head)", "DINOv3 linear head on frozen tokens"),
                         ("DINOv3 fine-tuned (last 2 blocks + head)", "DINOv2 only, frozen"),
                         ("DINOv3 only, frozen", "DINOv2 only, frozen"),
                         ("DINOv3 linear head on frozen tokens", "DINOv3 only, frozen")):
            if cand in called and ag in called:
                for scope, m, ww in (("val cells", va, None), ("all cells (weighted)", np.ones(len(y), bool), w)):
                    r = C.cell_report(y[m], {ag: called[ag][m], cand: called[cand][m]}, block[m], ag,
                                      w=None if ww is None else ww[m]).iloc[1]
                    pairs.append({"scope": scope, "arm": cand, "against": ag, "F1": r["F1"],
                                  "F1 difference": r[f"F1 vs {ag}"], "95% CI": r["95% CI of the difference"],
                                  "verdict": r["verdict"]})
        A = {"val": rep_val, "all": rep_all, "per fold": per_fold, "pairs": pd.DataFrame(pairs), "cuts": cuts,
             "nn cuts per fold": nn_cut, "cells": {"held-out val-split cells": int(va.sum()),
                                                   "held-out training-split cells": int((~va).sum()),
                                                   "val-split road cells": int((y[va] == 1).sum()),
                                                   "real road share": real, "training-split road share": s_tr}}
        np.savez_compressed(C.OUT / "spatialcv_calls_cells.npz", tile_id=cells.tile_id.to_numpy().astype(str),
                            row=cells.row.to_numpy(), col=cells.col.to_numpy(), split=cells.split.to_numpy(),
                            label=y, outer_fold=fold + 1, block=block, names=np.array(list(called)),
                            called=np.stack([called[n] for n in called]))
        say("Track A, held-out validation-split cells\n" + rep_val.to_string() + "\nall held-out cells (weighted)\n"
            + rep_all.to_string() + "\n" + A["pairs"].to_string())

# ======================================================================================================================
# Agent B's calls, if they exist: production's S calls at seed 662 must match ours call for call
# ======================================================================================================================
AGENT_B = {"looked in": "evidence/pilot_scripts/spatial_cv/ (read only)", "files": [], "checks": []}
bcsv = HERE.parent / "spatial_cv" / "spatial_cv_calls.csv"
if bcsv.exists() and B:
    AGENT_B["files"].append(bcsv.name)
    ab = pd.read_csv(bcsv)
    for set_name, mask_col, ours, theirs in (("798", "kept by production gate (a)", PROD, "(a) production"),
                                             ("891", "tile rule (891)", BEST, "(b) best combo")):
        mine = B[set_name]["calls"]
        sub = ab[ab[mask_col].astype(bool)].reset_index(drop=True)
        assert sub.tile_id.equals(mine.tile_id) and sub.road_id.equals(mine.road_id)
        for scheme in ("S", "T"):
            col = f"{theirs} · {scheme} · call seed 662"
            if col in sub:
                a, b = sub[col].to_numpy(), mine[f"{scheme}: {ours}"].to_numpy()
                same = int((a == b).sum())
                AGENT_B["checks"].append({"set": set_name, "arm": ours, "scheme": scheme, "Agent B column": col,
                                          "roads": len(b), "calls equal": same, "match": same == len(b)})
                say(f"Agent B check, {set_name}, {ours}, {scheme}: {same} of {len(b)} calls equal")
bnpz = HERE.parent / "spatial_cv" / "spatial_cv_trackA_probs.npz"
if bnpz.exists() and A:
    zb = np.load(bnpz)
    if all(f"S__662__{k}" in zb.files for k in range(5)):
        from spatial_folds import cell_folds
        AGENT_B["files"].append(bnpz.name)
        cf = cell_folds(cells.tile_id.to_numpy(), C.SEED)
        theirs = np.full(len(cells), -1, int)
        for k, (_, te) in enumerate(cf):
            assert len(zb[f"S__662__{k}"]) == len(te), "Agent B's held-out cells differ from ours"
            theirs[te] = zb[f"S__662__{k}"] >= 0.75
        assert (theirs >= 0).all()
        mine = called["classical + DINOv2 (production), frozen"]
        name_b = "classical + DINOv2 (production), fit on pooled train + val-split cells (Agent B's construction)"
        AGENT_B["Track A"] = {"cells": len(cells), "calls equal to ours": int((theirs.astype(bool) == mine).sum()),
                              "why they differ": "Agent B fits on every outer-training cell (both splits pooled); "
                                                 "we fit on the outer-training tiles' road-enriched training-split "
                                                 "cells only (production's training sample)"}
        va = (cells.split == "val").to_numpy()
        both = {name_b: theirs.astype(bool), **called}
        AGENT_B["Track A"]["held-out validation-split cells"] = C.tidy(
            C.cell_report(y[va], {n: c[va] for n, c in both.items()}, block[va], name_b))
        AGENT_B["Track A"]["all held-out cells (weighted)"] = C.tidy(C.cell_report(y, both, block, name_b, w=w))
        say("Agent B's Track A production (pooled fit), as a second reference\n"
            + pd.DataFrame(AGENT_B["Track A"]["held-out validation-split cells"]).to_string())
    else:
        AGENT_B["Track A"] = {"status": f"not all 5 outer folds saved yet ({[k for k in zb.files if k.startswith('S__662')]})"}
NUM["Agent B comparison"] = AGENT_B

# ======================================================================================================================
# numbers + tables
# ======================================================================================================================
gpu_times = {f.stem: json.loads(f.read_text()) for f in sorted(C.FOLD_DIR.glob("gpu_times*.json"))}
not_run = json.loads((C.FOLD_DIR / "not_run.json").read_text()) if (C.FOLD_DIR / "not_run.json").exists() else {}
fold_info = {p.stem: json.loads(p.read_text()) for p in sorted(C.FOLD_DIR.glob("*_outer*.json"))}
for v in fold_info.values():
    for key in ("es history", "cross-fit histories", "history"):
        v.pop(key, None)
NUM["GPU times (s)"] = gpu_times
NUM["not run"] = not_run
NUM["per outer fold (GPU arms)"] = fold_info
NUM["Track B frozen"] = {s: {"S": C.tidy(v["rep S"]), "T (old tile folds)": C.tidy(v["rep T"]),
                             "paired (S)": C.tidy(v["pairs"]), "optimism T - S": C.tidy(v["optimism"]),
                             "per outer fold accuracy (S)": v["per fold"]} for s, v in B.items()}
NUM["Track B trained cues"] = {s: {"S": C.tidy(v["rep S"]), "paired (S)": C.tidy(v["pairs"]),
                                   "per outer fold accuracy (S)": v["per fold"]} for s, v in BT.items()}
if A:
    NUM["Track A"] = {"held-out validation-split cells": C.tidy(A["val"]),
                      "all held-out cells, weighted to the real road share": C.tidy(A["all"]),
                      "pairs": C.tidy(A["pairs"]), "per outer fold F1": A["per fold"], "cut-offs (frozen)": A["cuts"],
                      "cut-offs per outer fold (A-head / A-ft, inner fold 1)": A["nn cuts per fold"],
                      "cells": A["cells"]}
(C.OUT / "spatialcv_numbers.json").write_text(json.dumps(NUM, indent=1, default=float))

cols_b = ["arm", "TP", "FN", "FP", "TN", "accuracy", "accuracy 95% CI", "precision", "recall", "specificity", "F1",
          "MCC"]
cols_p = ["arm", "against", "difference", "95% CI", "roads fixed", "roads broken", "McNemar p", "verdict"]
for s, v in B.items():
    MD += [f"## Track B frozen arms, {s} roads, spatial folds (seed 662)", md_table(v["rep S"], cols_b), "",
           md_table(v["pairs"], cols_p), "", f"### Optimism (old tile folds minus spatial folds, {s} roads)",
           md_table(v["optimism"]), ""]
for s, v in BT.items():
    MD += [f"## Track B trained-cue arms, {s} roads, spatial folds (seed 662)", md_table(v["rep S"], cols_b), "",
           md_table(v["pairs"], cols_p), ""]
if A:
    cols_a = ["arm", "precision", "recall", "F1", "F1 95% CI", list(A["val"].columns)[8], "95% CI of the difference",
              "verdict"]
    MD += ["## Track A, held-out validation-split cells (spatial folds)", md_table(A["val"], cols_a), "",
           "## Track A, all held-out cells weighted to the real road share", md_table(A["all"], cols_a), "",
           "## Track A pairs", md_table(A["pairs"]), ""]
(C.OUT / "spatialcv_tables.md").write_text("# Spatial CV of the DINOv3 benchmark: tables (generated)\n\n" + "\n".join(MD))
say("numbers and tables written")

# ======================================================================================================================
# pictures
# ======================================================================================================================
def dot_ci(ax, ypos, val, lo, hi, colour, label=None, ink=INK):
    ax.plot([lo, hi], [ypos, ypos], color=colour, linewidth=2, solid_capstyle="round")
    ax.plot([val], [ypos], "o", color=colour, markersize=8, markeredgecolor=SURFACE, markeredgewidth=1.5,
            label=label)
    ax.annotate(f"{val:.3f}", (hi, ypos), xytext=(5, 0), textcoords="offset points", va="center", fontsize=7.5,
                color=ink)


def figure_b(set_name="798"):
    """Track B: accuracy per arm, last night (tile folds / validation tiles) beside the spatial folds."""
    rows = []
    ph1 = {r["features"]: r for r in PH1["Track B"][f"{set_name} roads"]}
    ph2 = {k: {r["features"]: r for r in v["confusion"]} for k, v in PH2["Track B"].items()}
    ph2_set = "production cloud rule" if set_name == "798" else "tile rule"
    n_val = PH2["Track B"][ph2_set]["roads"]["validation"]
    what = ("the 798 roads production's cloud rule assesses" if set_name == "798" else
            "the 891 tile-rule (cloud-free tile) roads")
    if set_name in B:
        rep = B[set_name]["rep S"].set_index("arm")
        extra = ("DINOv3 cues + vector", "DINOv2 + DINOv3 cues + vectors") if set_name == "891" else ()
        for n in ("base (production without DINO)", PROD, "base + DINOv3 cues", "base + DINOv2 + DINOv3 cues",
                  BEST, "base + DINOv3 cues + vector", "base + DINOv2 + DINOv3 cues + vectors") + extra:
            if n in rep.index:
                rows.append((set_name, n + "  [frozen]", ph1[n]["accuracy"], ph1[n]["accuracy 95% CI"],
                             "5 tile folds", rep.loc[n, "accuracy"], rep.loc[n, "accuracy 95% CI"]))
    if set_name in BT:
        rep = BT[set_name]["rep S"].set_index("arm")
        for n in ("base + DINOv3 head cues", "base + DINOv3 fine-tuned cues", "base + DINOv2 cues + DINOv3 head cues",
                  "base + DINOv2 cues + DINOv3 fine-tuned cues"):
            if n in rep.index:
                r2 = ph2[ph2_set][n]
                rows.append((set_name, n + "  [trained]", r2["accuracy"], r2["accuracy 95% CI"], "40 validation tiles",
                             rep.loc[n, "accuracy"], rep.loc[n, "accuracy 95% CI"]))
    if not rows:
        return None
    fig, ax = plt.subplots(figsize=(11, 0.62 * len(rows) + 2.2), facecolor="white")
    style(ax)
    for i, (_, n, a0, c0, how, a1, c1) in enumerate(rows[::-1]):
        lo0, hi0 = ci(c0)
        lo1, hi1 = ci(c1)
        dot_ci(ax, i + 0.17, a0, lo0, hi0, BLUE, "last night (tile folds for frozen arms; 40 validation tiles for "
                                                 "trained arms)" if i == 0 else None, ink=MUTED)
        dot_ci(ax, i - 0.17, a1, lo1, hi1, ORANGE, "spatial folds (seed 662, purged, 5 outer folds)" if i == 0 else None)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[1] for r in rows[::-1]], fontsize=9, color=INK)
    prod = B[set_name]["rep S"].set_index("arm").loc[PROD, "accuracy"]
    ax.axvline(prod, color=MUTED, linewidth=0.8)
    ax.set_xlabel(f"accuracy on {what}\n(dots: estimate; lines: 95% interval; grey line: production under the "
                  "spatial folds)", fontsize=9, color=MUTED)
    ax.set_ylim(-0.75, len(rows) - 0.1)
    ax.set_title("Track B, flood per road: last night's numbers beside the spatial folds\n"
                 "Intervals: tiles resampled (last night), 3 x 3-tile blocks resampled (spatial).\n"
                 f"Last night's trained arms were scored on the {n_val} validation roads only; frozen arms on all "
                 f"{set_name}.",
                 fontsize=10, color=INK, loc="left")
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", fontsize=8.5, frameon=False, ncol=2, bbox_to_anchor=(0.01, 0.0))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = C.OUT / f"spatialcv_trackB_accuracy_{set_name}.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def figure_a():
    if not A:
        return None
    ph1 = {r["cut-off"].rsplit(" (", 1)[0]: r for r in PH1["Track A"]["validation cells"]}
    ph2 = {r["cut-off"].rsplit(" (", 1)[0]: r for r in PH2["Track A"]["validation cells"]}
    last = {"classical + DINOv2 (production), frozen": ph1["classical + DINOv2"],
            "DINOv2 only, frozen": ph1["DINOv2 only"], "classical + DINOv3, frozen": ph1["classical + DINOv3"],
            "DINOv3 only, frozen": ph1["DINOv3 only"],
            "DINOv3 linear head on frozen tokens": ph2["DINOv3 linear head on frozen tokens"],
            "DINOv3 fine-tuned (last 2 blocks + head)": ph2["DINOv3 fine-tuned (last 2 blocks + head)"]}
    rep_v, rep_a = A["val"].set_index("arm"), A["all"].set_index("arm")
    names = [n for n in last if n in rep_v.index]
    fig, axes = plt.subplots(1, 2, figsize=(14, 0.9 * len(names) + 2.6), facecolor="white", sharey=True)
    for ax, rep, title, show_last in ((axes[0], rep_v, "held-out validation-split cells (primary)", True),
                                      (axes[1], rep_a, "all held-out cells, weighted to the real road share", False)):
        style(ax)
        for i, n in enumerate(names[::-1]):
            if show_last:
                lo0, hi0 = ci(last[n]["F1 95% CI"])
                dot_ci(ax, i + 0.17, last[n]["F1"], lo0, hi0, BLUE,
                       "last night (fit on training tiles, scored on the 40 validation tiles)" if i == 0 else None,
                       ink=MUTED)
            lo1, hi1 = ci(rep.loc[n, "F1 95% CI"])
            dot_ci(ax, i - (0.17 if show_last else 0), rep.loc[n, "F1"], lo1, hi1, ORANGE,
                   "spatial folds (seed 662, 5 outer folds)" if i == 0 else None)
        ax.axvline(rep.loc["classical + DINOv2 (production), frozen", "F1"], color=MUTED, linewidth=0.8)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        ax.set_xlabel("road-cell F1 (dots: estimate; lines: 95% interval)", fontsize=9, color=MUTED)
        ax.set_ylim(-0.6, len(names) - 0.4)
    axes[0].set_yticks(range(len(names)))
    axes[0].set_yticklabels(names[::-1], fontsize=9, color=INK)
    fig.suptitle("Track A, finding roads: last night's validation numbers beside the spatial folds (grey line: "
                 "production under spatial folds)", fontsize=11, color=INK, x=0.01, ha="left")
    fig.text(0.01, 0.005, "Intervals: tiles resampled (last night), 3 x 3-tile blocks resampled (spatial). Frozen "
             "arms keep their logged cut-offs; A-head chooses its cut-off on inner fold 1 of each outer fold. A-ft was "
             "not run (GPU budget; see the write-up).",
             fontsize=8, color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower left", fontsize=8.5, frameon=False, ncol=2, bbox_to_anchor=(0.01, 0.03))
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    path = C.OUT / "spatialcv_trackA_f1.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def figure_folds():
    """Per outer fold: Track B accuracy (798) and Track A F1 (all held-out cells, weighted), one line per arm."""
    panels = []
    if "798" in B:
        pf = dict(B["798"]["per fold"])
        if "798" in BT:
            pf.update({n: v for n, v in BT["798"]["per fold"].items() if "head" in n or "fine-tuned" in n})
        keep = [n for n in (PROD, "base + DINOv3 cues", "base + DINOv3 head cues", "base + DINOv3 fine-tuned cues")
                if n in pf]
        panels.append(("Track B: accuracy per outer fold, 798 roads", {n: pf[n] for n in keep}, "accuracy"))
    if A:
        keep = [n for n in ("classical + DINOv2 (production), frozen", "classical + DINOv3, frozen",
                            "DINOv3 linear head on frozen tokens", "DINOv3 fine-tuned (last 2 blocks + head)")
                if n in A["per fold"]]
        panels.append(("Track A: road-cell F1 per outer fold, all held-out cells (weighted)",
                       {n: A["per fold"][n]["all cells (weighted)"] for n in keep}, "F1"))
    if not panels:
        return None
    colours = [BLUE, ORANGE, AQUA, YELLOW]
    markers = ["o", "s", "^", "D"]
    fig, axes = plt.subplots(1, len(panels), figsize=(7.2 * len(panels), 4.8), facecolor="white", squeeze=False)
    for ax, (title, series, ylab) in zip(axes[0], panels):
        ax.set_facecolor(SURFACE)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.grid(axis="y", color=GRID_C, linewidth=0.6)
        ax.tick_params(colors=MUTED, labelsize=9)
        for (n, v), c, m in zip(series.items(), colours, markers):
            ax.plot(range(1, 6), v, marker=m, color=c, linewidth=2, markersize=8, markeredgecolor=SURFACE,
                    markeredgewidth=1.5, label=n)
        ax.set_xticks(range(1, 6))
        ax.set_xlabel("outer fold (spatial, seed 662)", fontsize=9, color=MUTED)
        ax.set_ylabel(ylab, fontsize=9, color=MUTED)
        ax.set_title(title, fontsize=10, color=INK, loc="left")
        ax.legend(fontsize=8, frameon=False, loc="lower left")
    fig.tight_layout()
    path = C.OUT / "spatialcv_per_fold.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def figure_tile_b():
    """The Track B picture tile, held out in its outer fold: before, after, frozen DINOv3 patch change, and P(flooded)
    from the head on frozen tokens and from the fine-tuned model (mean of the fold's 5 inner models)."""
    from sn8 import tile
    from sn8_lines import draw_roads
    from sn8_torchgeo import tile_pair
    import dinov3_finetune as ft
    pic = [p for p in C.FOLD_DIR.glob("B-ft_outer*.npz") if any(k.startswith("grid_") for k in np.load(p).files)]
    if not pic:
        return None
    zf = np.load(pic[0])
    t = [k for k in zf.files if k.startswith("grid_")][0][5:]
    k = int(pic[0].stem.split("outer")[1])
    zh = np.load(C.FOLD_DIR / f"B-head_outer{k}.npz")
    cm = np.load(C.FOLD_DIR / f"change_maps_{t}.npz")
    p = tile_pair(t)
    from sn8_lines import road_band
    owner = ft.strip_layout(t, road_band())[2]
    fig, axes = plt.subplots(2, 3, figsize=(22, 15), facecolor="white")
    axes[0, 0].imshow(p["before_grey"], cmap="gray", vmin=0, vmax=255)
    axes[0, 0].set_title(f"{t} before (greyscale)", fontsize=12)
    axes[0, 1].imshow(p["after_grey"], cmap="gray", vmin=0, vmax=255)
    axes[0, 1].set_title("after (greyscale)", fontsize=12)
    c3 = cm["dinov3"]
    im = axes[0, 2].imshow(c3, cmap="magma", vmin=0, vmax=np.nanpercentile(c3, 99),
                           extent=(0, c3.shape[1] * 16, c3.shape[0] * 16, 0))
    axes[0, 2].set_title("frozen DINOv3 patch change (8 m), 1 - cosine\n(no training: what the frozen backbone sees)",
                         fontsize=12)
    plt.colorbar(im, ax=axes[0, 2], fraction=0.04)
    calls = {}
    if "891" in BT:
        cb = BT["891"]["calls"]
        on = (cb.tile_id == t).to_numpy()
        for n in ("base + DINOv3 head cues", "base + DINOv3 fine-tuned cues", PROD):
            if n in BT["891"]["S"]:
                calls[n] = (int((BT["891"]["S"][n][on] == cb.flooded.to_numpy()[on]).sum()), int(on.sum()))
    for a, g, title in ((axes[1, 0], zh[f"grid_{t}"], "head on frozen DINOv3 tokens (B-head): P(flooded)"),
                        (axes[1, 1], zf[f"grid_{t}"], "fine-tuned DINOv3, last 2 blocks + head (B-ft): P(flooded)")):
        a.imshow(p["after_grey"], cmap="gray", vmin=0, vmax=255)
        im = a.imshow(np.ma.masked_invalid(np.where(owner > 0, g, np.nan)), cmap="coolwarm", vmin=0, vmax=1,
                      extent=(0, g.shape[1] * 4, g.shape[0] * 4, 0), alpha=0.85)
        a.set_title(title + f"\nroad strips only; mean of outer fold {k + 1}'s 5 inner models, none saw this tile",
                    fontsize=12)
        plt.colorbar(im, ax=a, fraction=0.04)
    diff = zf[f"grid_{t}"] - zh[f"grid_{t}"]
    axes[1, 2].imshow(p["after_grey"], cmap="gray", vmin=0, vmax=255)
    im = axes[1, 2].imshow(np.ma.masked_invalid(np.where(owner > 0, diff, np.nan)), cmap="PuOr_r", vmin=-1, vmax=1,
                           extent=(0, diff.shape[1] * 4, diff.shape[0] * 4, 0), alpha=0.9)
    txt = "; ".join(f"{n}: {a}/{b} roads right" for n, (a, b) in calls.items())
    axes[1, 2].set_title("fine-tuned minus frozen head: P(flooded)\n" + txt, fontsize=10)
    plt.colorbar(im, ax=axes[1, 2], fraction=0.04)
    for a in axes.flat:
        draw_roads(a, tile(t)["label"], (p["x0"], p["y0"]))
        a.set_xlim(0, p["before_grey"].shape[1])
        a.set_ylim(p["before_grey"].shape[0], 0)
        a.axis("off")
    fig.text(0.5, 0.008, "Imagery: Maxar via SpaceNet 8 (SpaceNet LLC), CC BY-SA 4.0. Labelled roads: red flooded, "
             "cyan dry. Same tile as last night's phase 2 picture (fixed rule: the validation tile with the most "
             "flooded roads); here it is held out by its spatial block.", ha="center", fontsize=11)
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    path = C.OUT / f"spatialcv_flood_maps_{t}.png"
    fig.savefig(path, dpi=70)
    plt.close(fig)
    return path


def figure_tile_a():
    """The Track A picture tile, held out: every labelled cell for the linear head on frozen tokens and for the
    fine-tuned model of its outer fold (green found, red not road, blue missed)."""
    from matplotlib.colors import ListedColormap
    from sn8_torchgeo import tile_pair
    import dinov3_finetune as ft
    files = {n: [p for p in C.FOLD_DIR.glob(f"{n}_outer*.npz") if any(k.startswith("grid_") for k in np.load(p).files)]
             for n in ("A-head", "A-ft")}
    if not all(files.values()):
        return None
    fig, axes = plt.subplots(1, 2, figsize=(16, 8.8), facecolor="white")
    for a, n, title in zip(axes, ("A-head", "A-ft"), ("linear head on frozen DINOv3 tokens",
                                                       "fine-tuned DINOv3, last 2 blocks + head")):
        z = np.load(files[n][0])
        t = [k for k in z.files if k.startswith("grid_")][0][5:]
        k = int(files[n][0].stem.split("outer")[1])
        cut = json.loads((C.FOLD_DIR / f"{n}_outer{k}.json").read_text())["cut-off (inner fold 1)"]
        g = z[f"grid_{t}"]
        grid = tuple(int(v) for v in np.load(ft.trunk_dir() / f"{t}_before.npz")["grid"])
        lab = ft.road_cell_grid(t, grid)
        found = g >= cut
        out = np.full(lab.shape, np.nan)
        out[(lab == 1) & found] = 0
        out[(lab == 0) & found] = 1
        out[(lab == 1) & ~found] = 2
        tp, fp, fn = int(((lab == 1) & found).sum()), int(((lab == 0) & found).sum()), int(((lab == 1) & ~found).sum())
        p = tile_pair(t)
        a.imshow(p["before_grey"], cmap="gray", vmin=0, vmax=255)
        a.imshow(out, cmap=ListedColormap(["limegreen", "red", "dodgerblue"]), vmin=0, vmax=2, alpha=0.7,
                 extent=(0, lab.shape[1] * 4, lab.shape[0] * 4, 0))
        a.set_title(f"{t}: {title}, cut-off {cut:.2f} (inner fold 1 of outer fold {k + 1})\ngreen found {tp} | red "
                    f"not road {fp} | blue missed {fn} | precision {tp / max(tp + fp, 1):.2f}, recall "
                    f"{tp / max(tp + fn, 1):.2f}", fontsize=10)
        a.set_xlim(0, p["before_grey"].shape[1])
        a.set_ylim(p["before_grey"].shape[0], 0)
        a.axis("off")
    fig.text(0.5, 0.01, "Imagery: Maxar via SpaceNet 8 (SpaceNet LLC), CC BY-SA 4.0. Every labelled 2 m cell of the "
             "tile; cells 3.5-8 m from a road are left out. Same tile as last night (most labelled roads among the "
             "validation tiles); here held out by its spatial block.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = C.OUT / f"spatialcv_cells_{t}.png"
    fig.savefig(path, dpi=80)
    plt.close(fig)
    return path


for fn in (figure_b, lambda: figure_b("891"), figure_a, figure_folds, figure_tile_b, figure_tile_a):
    try:
        out = fn()
        say(f"{getattr(fn, '__name__', 'figure')}: {out}")
    except Exception as e:   # a picture must not lose the numbers above; the error is printed in full
        import traceback
        traceback.print_exc()
        say(f"{fn.__name__} failed: {e!r}")
say("report done")
