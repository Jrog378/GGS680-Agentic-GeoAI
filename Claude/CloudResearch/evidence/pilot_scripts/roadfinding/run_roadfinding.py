"""The pre-registered road-finding test (outputs/preregistration_roadfinding_cloud.md): does de-hazing the after image
help production's road detector find the OSM roads under the two-date cloud gate? Development tiles only.

Run:  /opt/miniconda3/bin/python3 -I run_roadfinding.py > run.log 2>&1   (from this folder)
Writes here: numbers.json (every table), roads_set_aside.csv (per road, visible share per arm), the PNGs; caches the
features and the out-of-fold probabilities in ClaudeFunctions/.cache/cloudroads."""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

FUNCS = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
sys.path.append(FUNCS)
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.model_selection import StratifiedGroupKFold

from sn8_cloudroads import (ARMS, CACHE_DIR, CELL_PX, DETECTOR_COLUMNS, VISIBLE_SHARE, _cache_key, arm_cells, arm_images,
                            features_at, mcnemar_cells, paired_auc, paired_cells, reproduction_check, save_pictures,
                            set_aside_roads, tile_layout, tile_resamples, visible_roads)
from sn8_cutoff import f1_cutoff, road_prior
from sn8_data import split_tables
from sn8_dino_cells import cell_basis
from sn8_grey import GREY_DIR
from sn8_models import classical_models
from sn8_stages import production_cutoff, production_detector, production_detector_features

import os
DEBUG = int(os.environ.get("ROADFINDING_SMOKE", "0"))   # smoke test on a few tiles: catches code errors only
OUT = Path(os.environ["ROADFINDING_OUT"]) if DEBUG else Path(__file__).resolve().parent
T0 = time.time()
BASE = "as it is"


def say(*a):
    print(f"[{time.time() - T0:7.0f} s]", *a, flush=True)


def file_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()[:12] for p in sorted(Path(FUNCS).glob("sn8*.py"))}


def tidy(df):
    return json.loads(df.to_json(orient="records", double_precision=4))


# ---------- data: development tiles only ----------
df, train, val, test, negative = split_tables(662)
dev = list(train.tile_id) + list(val.tile_id)
index = pd.read_csv(GREY_DIR / "tiles.csv")
assert len(dev) == 226 and set(dev) == set(index.tile_id[index.split.isin(["train", "val"])])
assert not set(dev) & (set(test.tile_id) | set(negative.tile_id)), "development tiles only"
del test, negative                       # never used below
git = subprocess.run(["git", "-C", str(Path(FUNCS).parent), "rev-parse", "--short", "HEAD"], capture_output=True,
                     text=True).stdout.strip()
changed = subprocess.run(["git", "-C", str(Path(FUNCS).parent), "status", "--short", "--", "ClaudeFunctions"],
                         capture_output=True, text=True).stdout
hashes_start = file_hashes()
say("code", git, "| uncommitted in ClaudeFunctions:", changed.strip().replace("\n", "; "))
name, cols = production_detector_features()
assert cols == DETECTOR_COLUMNS and production_detector() == "Random forest"
CUT = production_cutoff()
say("production detector:", production_detector(), "|", name, len(cols), "columns | cut-off", CUT)
out = {"plan": "outputs/preregistration_roadfinding_cloud.md", "code": git, "module hashes": hashes_start,
       "detector": {"model": production_detector(), "features": name, "columns": len(cols), "cut-off": CUT},
       "tiles": {"train": len(train), "val": len(val)}}

# ---------- 1. reproduction check (before any score) ----------
rc = reproduction_check(list(train.tile_id[:2]))
say("reproduction check\n" + rc.to_string())
out["reproduction check"] = tidy(rc)

# ---------- 2. the roads the cloud rule sets aside ----------
sa = set_aside_roads()
sa["road_id"] = sa.road_id.astype(str)
dup = int(sa.duplicated(["tile_id", "road_id"]).sum())
say("set-aside roads", len(sa), "on", sa.tile_id.nunique(), "tiles; duplicates (tile, road)", dup)
say("decisions", sa.decision.value_counts().to_dict(), "| CORRECT on opaque-cloud (tile-rule) tiles",
    int(((sa.decision == "CORRECT") & sa.cloudy.astype(bool)).sum()))
road_tiles = set(sa.tile_id)
if DEBUG:
    dev = [t for t in dev if t in road_tiles][:DEBUG] + [t for t in dev if t not in road_tiles][:DEBUG]

# ---------- 3. cells and features (cached) ----------
basis = cell_basis()
layouts, unchanged = [], {}
for i, t in enumerate(dev):
    imgs = arm_images(t)
    keep = t in road_tiles
    lay = tile_layout(t, imgs, keep_road_cells=keep)
    unchanged[t] = imgs["two-date unchanged"]
    for arm in ARMS:
        arm_cells(t, arm, lay, imgs, basis, keep_road_cells=keep)
    layouts.append(lay)
    if i % 10 == 0 or i == len(dev) - 1:
        say(f"features {i + 1}/{len(dev)} tiles ({t}, gate px {int(imgs['gate'].sum())})")
cells = pd.concat(layouts, ignore_index=True)
say("stored cells", len(cells), "| training", int(cells.train.sum()), "| scored", int(cells["eval"].sum()),
    "| tiles with a changed two-date image", sum(not v for v in unchanged.values()))
gcount = cells[cells["eval"]].groupby(["group", "label"]).agg(cells=("row", "size"), weighted=("weight", "sum"),
                                                              tiles=("tile_id", "nunique")).reset_index()
say("scored cells by group\n" + gcount.to_string())
out["scored cells"] = tidy(gcount)

# picture tile: the most OSM road cells in the correctable part of the gate (no flood label, no detector output)
corr_road = cells[(cells.group == "correctable") & (cells.label == 1)]
PIC = corr_road.tile_id.value_counts().index[0]
pr, pc = corr_road[corr_road.tile_id == PIC].row.mean() * CELL_PX, corr_road[corr_road.tile_id == PIC].col.mean() * CELL_PX
pic_imgs = arm_images(PIC)
H, W = pic_imgs["valid"].shape
r0, c0 = int(np.clip(pr - 250, 0, max(H - 500, 0))), int(np.clip(pc - 250, 0, max(W - 500, 0)))
ZOOM = (r0, min(r0 + 500, H), c0, min(c0 + 500, W))
say("picture tile", PIC, "| correctable road cells", int((corr_road.tile_id == PIC).sum()), "| zoom", ZOOM)

# ---------- 4. folds by tile and out-of-fold probabilities ----------
tr = np.flatnonzero(cells.train.to_numpy())
folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)
fold_of = {}
for k, (_, te) in enumerate(folds.split(cells.iloc[tr], cells.label.iloc[tr], groups=cells.tile_id.iloc[tr])):
    for t in cells.tile_id.iloc[tr[te]].unique():
        fold_of[t] = k
assert set(fold_of) == set(dev), set(dev) - set(fold_of)
fold = cells.tile_id.map(fold_of).to_numpy()
y = cells.label.to_numpy()
prob_path = CACHE_DIR / f"probs_{_cache_key(True)}_{_cache_key(False)}_{len(cells)}.npz"
pic_full = None
if prob_path.exists():
    z = np.load(prob_path, allow_pickle=False)
    probs = {a: z[a.replace(" ", "_").replace("(", "").replace(")", "")] for a in ARMS}
    pic_grid = {a: z["pic_" + a.replace(" ", "_").replace("(", "").replace(")", "")] for a in ARMS}
    say("out-of-fold probabilities read from", prob_path.name)
else:
    from sn8_cloudroads import cell_feature_maps
    _, full = cell_feature_maps(pic_imgs["images"]["as it is"], pic_imgs["valid"])
    fr, fc = np.nonzero(full)
    probs, pic_grid = {}, {}
    for arm in ARMS:
        parts = []
        for t, lay in zip(dev, layouts):
            parts.append(arm_cells(t, arm, lay, {"two-date unchanged": unchanged[t]}, basis,
                                   keep_road_cells=t in road_tiles))
        X = np.concatenate(parts)
        assert X.shape == (len(cells), len(DETECTOR_COLUMNS)) and np.isfinite(X).all()
        p = np.zeros(len(cells), np.float32)
        grid = np.zeros(full.shape, np.float32)
        for k in range(5):
            fit = cells.train.to_numpy() & (fold != k)
            model = classical_models()[production_detector()].fit(pd.DataFrame(X[fit], columns=DETECTOR_COLUMNS), y[fit])
            te = fold == k
            p[te] = model.predict_proba(pd.DataFrame(X[te], columns=DETECTOR_COLUMNS))[:, 1]
            if fold_of[PIC] == k:
                xp = features_at(pic_imgs["images"][arm], pic_imgs["valid"], fr, fc, basis)
                grid[fr, fc] = model.predict_proba(pd.DataFrame(xp, columns=DETECTOR_COLUMNS))[:, 1]
            say(f"{arm}: fold {k + 1}/5 fitted on {int(fit.sum())} cells, called {int(te.sum())}")
        probs[arm], pic_grid[arm] = p, grid
        del X, parts
    key = lambda a: a.replace(" ", "_").replace("(", "").replace(")", "")
    np.savez_compressed(prob_path, **{key(a): probs[a] for a in ARMS}, **{"pic_" + key(a): pic_grid[a] for a in ARMS})
    say("saved", prob_path.name)
calls = {a: probs[a] >= CUT for a in ARMS}
ev = cells["eval"].to_numpy()
grp = cells.group.to_numpy()

# ---------- 5. scores ----------
def cell_table(mask, baseline=BASE, arms=ARMS):
    return paired_cells(cells, {a: calls[a] for a in arms}, mask, baseline)


res = {}
m_corr = ev & (grp == "correctable")
prim = cell_table(m_corr)
say("PRIMARY + secondary 1-3: correctable cells, each arm against as it is\n" + prim.to_string())
res["correctable, vs as it is"] = tidy(prim)
he = cell_table(m_corr, "single image (He)", ("single image (He)", "two-date"))
say("correctable cells, two-date against single image\n" + he.to_string())
res["correctable, two-date vs single image"] = tidy(he)
mc = {a: mcnemar_cells(cells, calls[a], calls[BASE], m_corr) for a in ARMS if a != BASE}
say("McNemar on cells (overstates significance: cells in one tile are correlated)", json.dumps(mc, indent=1))
res["correctable, McNemar on cells vs as it is"] = mc
f = prim.set_index("arm").F1
res["share of the as-it-is to before gap closed (descriptive)"] = {
    a: float((f[a] - f[BASE]) / (f["before"] - f[BASE])) for a in ("two-date", "single image (He)")}
say("gap closed", res["share of the as-it-is to before gap closed (descriptive)"])

for g in ("opaque", "fade", "clear"):
    t = cell_table(ev & (grp == g))
    say(f"{g} cells\n" + t.to_string())
    res[f"{g}, vs as it is"] = tidy(t)
gated_tiles = set(cells.tile_id[cells.group != "clear"])
t = cell_table(ev & (grp == "clear") & cells.tile_id.isin(gated_tiles).to_numpy())
say("clear cells on the gated tiles only\n" + t.to_string())
res["clear on gated tiles, vs as it is"] = tidy(t)

# flood confound: recall on road cells by the nearest OSM road's development flood label
fl = cells.flooded.to_numpy()
conf = []
for g in ("correctable", "opaque", "clear"):
    for lab, fv in (("flooded = yes", 1), ("not labelled flooded", 0)):
        m = ev & (grp == g) & (y == 1) & (fl == fv)
        if m.sum() == 0:
            continue
        t = cell_table(m)
        for _, r in t.iterrows():
            conf.append({"group": g, "road label": lab, "arm": r.arm, "tiles": r.tiles,
                         "road cells": int(m.sum()), "recall": r.recall, "recall - as it is": r[f"recall - {BASE}"],
                         "95% CI": r["recall diff 95% CI"]})
conf = pd.DataFrame(conf)
say("flood confound: recall on road cells by flood label\n" + conf.to_string())
res["flood confound (recall on road cells)"] = tidy(conf)

auc = paired_auc(cells, probs, m_corr, BASE)
say("threshold-free: weighted ROC AUC, correctable cells\n" + auc.to_string())
res["correctable, AUC"] = tidy(auc)

real = road_prior("train")
trm = cells.train.to_numpy()
sampled = float((y[trm] == 1).mean())
own = {a: f1_cutoff(y[trm], probs[a][trm], sampled, real)[0] for a in ARMS}
say("per-arm F1 cut-offs (out-of-fold training cells, real share %.4f, sampled %.4f):" % (real, sampled), own)
t = paired_cells(cells, {a: probs[a] >= own[a] for a in ARMS}, m_corr, BASE)
say("correctable cells at each arm's own cut-off\n" + t.to_string())
res["per-arm cut-offs"] = own
res["correctable, own cut-offs"] = tidy(t)

# ---------- 6. the roads that could come back ----------
rc_cells = cells[cells.road_cell_kept.to_numpy()]
for a in ARMS:
    v = visible_roads(rc_cells, calls[a][cells.road_cell_kept.to_numpy()])
    sa = sa.merge(v.rename(columns={"road_cells": f"road cells", "visible_share": f"visible share: {a}"}),
                  on=["tile_id", "road_id"], how="left", suffixes=("", f" ({a})"))
sa = sa.loc[:, ~sa.columns.str.startswith("road cells (")]
for a in ARMS:
    sa[f"visible: {a}"] = sa[f"visible share: {a}"].fillna(0) >= VISIBLE_SHARE
say("set-aside roads with no own cells:", int(sa["road cells"].isna().sum()))
sa["could come back"] = sa.decision.isin(["ASSESS", "CORRECT"])
sa["on opaque-cloud tile"] = sa.cloudy.astype(bool)
subsets = {"151 could come back (ASSESS + CORRECT)": sa["could come back"],
           "ASSESS": sa.decision == "ASSESS", "CORRECT": sa.decision == "CORRECT",
           "CORRECT, on tile-rule-scored tiles": (sa.decision == "CORRECT") & ~sa["on opaque-cloud tile"],
           "CORRECT, on opaque-cloud tiles": (sa.decision == "CORRECT") & sa["on opaque-cloud tile"],
           "CANNOT ASSESS": sa.decision == "CANNOT ASSESS",
           "151, labelled flooded = yes": sa["could come back"] & sa.flooded.astype(bool),
           "151, not labelled flooded": sa["could come back"] & ~sa.flooded.astype(bool)}
rows = []
for nm, m in subsets.items():
    m = m.to_numpy()
    row = {"roads": nm, "n": int(m.sum())}
    for a in ARMS:
        row[a] = int(sa[f"visible: {a}"].to_numpy()[m].sum())
    rows.append(row)
vis_table = pd.DataFrame(rows)
say(f"roads visible (>= {VISIBLE_SHARE:.0%} of own cells called road, cut-off {CUT:.2f})\n" + vis_table.to_string())
res["roads visible"] = tidy(vis_table)
m = sa["could come back"].to_numpy()
tiles151 = np.unique(sa.tile_id[m])
draws = tile_resamples(tiles151)
per_tile = sa[m].groupby("tile_id")
pair = {}
for a in ARMS:
    if a == BASE:
        continue
    va, vb = sa[f"visible: {a}"].to_numpy()[m], sa[f"visible: {BASE}"].to_numpy()[m]
    new, lost = int((va & ~vb).sum()), int((~va & vb).sum())
    n_t = per_tile.size().reindex(tiles151).to_numpy()
    a_t = per_tile[f"visible: {a}"].sum().reindex(tiles151).to_numpy()
    b_t = per_tile[f"visible: {BASE}"].sum().reindex(tiles151).to_numpy()
    d = (draws @ a_t - draws @ b_t) / (draws @ n_t)
    pair[a] = {"newly visible": new, "lost": lost, "McNemar p (roads)": binomtest(new, new + lost, 0.5).pvalue if new + lost else 1.0,
               "share visible - as it is": float((va.mean() - vb.mean())),
               "95% CI (tiles resampled)": f"{np.percentile(d, 2.5):+.3f} to {np.percentile(d, 97.5):+.3f}",
               "tiles": len(tiles151)}
say("151 roads, each arm against as it is", json.dumps(pair, indent=1))
res["151 roads vs as it is"] = pair
keep_cols = ["tile_id", "road_id", "split", "decision", "flooded", "on opaque-cloud tile", "in gate", "opaque",
             "road cells"] + [f"visible share: {a}" for a in ARMS]
sa[keep_cols].round(4).to_csv(OUT / "roads_set_aside.csv", index=False)

# ---------- 7. pictures ----------
grid_calls = {a: pic_grid[a] >= CUT for a in ARMS}
paths = save_pictures(PIC, pic_imgs, grid_calls, OUT, zoom=ZOOM)
say("pictures:", [p.name for p in paths])
res["picture tile"] = {"tile": PIC, "rule": "most OSM road cells in the correctable part of the gate", "zoom px": ZOOM,
                       "fold": fold_of[PIC]}

# ---------- 8. log ----------
hashes_end = file_hashes()
out["module files changed during the run"] = sorted(k for k in set(hashes_start) | set(hashes_end)
                                                    if hashes_start.get(k) != hashes_end.get(k))
out["set-aside roads"] = {"n": len(sa), "decisions": sa.decision.value_counts().to_dict(), "duplicates": dup,
                          "CORRECT on opaque-cloud tiles": int(((sa.decision == "CORRECT") & sa["on opaque-cloud tile"]).sum())}
out["stored cells"] = int(len(cells))
out["results"] = res
out["run time s"] = round(time.time() - T0)
(OUT / "numbers.json").write_text(json.dumps(out, indent=1, default=str))
say("done; module files changed during the run:", out["module files changed during the run"])
