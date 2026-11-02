"""Spatially blocked cross-validation folds for flood per road (SpaceNet 8 Louisiana-East, Hurricane Ida).

Justin (2026-10-26): "can you do a cross validation so that you dont overfit". Test plan, written before any model is
scored on these folds: outputs/preregistration_spatial_cv.md. Method: Roberts et al. 2017, "Cross-validation
strategies for data with temporal, spatial, hierarchical, or phylogenetic structure", Ecography 40(8) 913-929: block
cross-validation with blocks larger than the dependence range, optionally with a buffer.

Why: the old folds (StratifiedGroupKFold by tile) let a held-out road share its road id (an OSM way that crosses a tile
edge) and so its flooded label with a training road on the next tile, and neighbouring tiles are spatially
autocorrelated.

Development data only: the 226 training + validation tiles of Louisiana-East and their 1,037 touched roads
(sn8_heldout.touched_roads(include_cloudy=True), which reads train and val only). Tile positions come from
sn8_data.georef on each dev tile's pre image (TIFF tags, no pixels). Test, negative and sealed data are never read.

    import sys
    sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
    sys.path.append("/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/spatial_cv")
    from spatial_folds import (SEEDS, spatial_folds, nested_spatial_folds, tile_folds, size_matched_tile_folds,
                               cell_folds, nested_cell_folds, fold_table, block_info, dev_roads, splitter)

    folds = spatial_folds(roads, seed=662)               # [(train_index, test_index), ...], positions in `roads`
    folds = spatial_folds(roads, seed=662, buffer=True)  # sensitivity: also no training road next to a held-out tile
    old = tile_folds(roads, seed=662)                    # the old tile folds, exactly as the existing scripts make them
    ctl = size_matched_tile_folds(roads, seed=662)       # control: tile folds with training sets as small as spatial's
    for outer_train, outer_test, inner in nested_spatial_folds(roads, seed=662): ...   # inner: [(train, test), ...]
    cv = splitter(folds, roads)                          # for cross_val_predict(cv=cv), cue_predictions, gated_calls

`roads` is any table of development roads with tile_id and road_id (and flooded) columns: the 1,037, production's
798, the 891 tile-rule roads or any other subset. A road's fold is set by its block, from one block-to-fold map made
on all 1,037 development roads, so every subset shares the same folds. Gates are applied by the caller as before
(fit on tr[keep[tr]]). Purging and buffering are relative to all development roads of the held-out blocks, so the
training rows of a subset are always the training rows of the 1,037 that are in the subset.

Run as a script it builds the blocks, checks the folds and writes folds_numbers.json, fold_tables.csv and
fold_map.png next to this file (CPU only, about a minute):
    /opt/miniconda3/bin/python3 -I spatial_folds.py > spatial_folds.log 2>&1      (from this folder)
"""
import json
import sys
import time
from functools import lru_cache
from pathlib import Path

LIB = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
if LIB not in sys.path:
    sys.path.append(LIB)

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

HERE = Path(__file__).resolve().parent
SEED = 662
SEEDS = [662] + list(range(1, 21))     # the primary fold seed, then 20 more, as in the pipeline factorial
N_SPLITS = 5
BLOCK_TILES = 3                        # square blocks with the area of 3 x 3 tiles
MERGE_MAX_SHARE = 0.25                 # merge blocks that share a road id unless the largest would hold > 25% of roads
BUFFER_M = 600.0                       # buffered CV: two tiles also touch if their centroids are within 600 m
EARTH_R = 6371008.8                    # mean Earth radius (m) for the local equirectangular projection
N_DEV_TILES, N_DEV_ROADS = 226, 1037


# ---------- development tiles and roads ----------

@lru_cache(maxsize=1)
def _dev_tiles():
    """The 226 dev tiles: split, region, col, row, centroid lon / lat, and the centroid and size in metres on a local
    equirectangular projection centred on the mean dev centroid: x = R cos(lat0) (lon - lon0), y = R (lat - lat0)."""
    from sn8_data import georef, split_tables
    _, train, val, _, _ = split_tables()       # test and negative are discarded here and never looked at
    dev = pd.concat([train.assign(split="train"), val.assign(split="val")])[["tile_id", "split", "pre"]]
    dev = dev.sort_values("tile_id").reset_index(drop=True)
    x0, y0, dx, dy, w, h = np.array([georef(p) for p in dev.pre], float).T   # TIFF tags only, no pixels
    lon, lat = x0 + dx * w / 2, y0 - dy * h / 2
    lon0, lat0 = lon.mean(), lat.mean()
    m = np.pi / 180 * EARTH_R
    parts = dev.tile_id.str.split("_", expand=True).astype(int)
    t = pd.DataFrame({"tile_id": dev.tile_id, "split": dev.split, "region": parts[0], "col": parts[1],
                      "row": parts[2], "lon": lon, "lat": lat,
                      "x_m": (lon - lon0) * np.cos(np.radians(lat0)) * m, "y_m": (lat - lat0) * m,
                      "w_m": dx * w * np.cos(np.radians(lat0)) * m, "h_m": dy * h * m})
    assert len(t) == N_DEV_TILES and t.tile_id.is_unique and set(t.split) == {"train", "val"}
    t.attrs["projection"] = {"kind": "local equirectangular", "lon0": float(lon0), "lat0": float(lat0),
                             "R_m": EARTH_R, "x": "R cos(lat0) (lon - lon0)", "y": "R (lat - lat0)"}
    return t


@lru_cache(maxsize=1)
def _dev_roads():
    """The 1,037 touched dev roads in touched_roads(include_cloudy=True) row order, with the masks the plans use."""
    import sn8_dino as D
    for split in ("train", "val"):
        _, csv, npz = D._paths(split)
        if not (csv.exists() and npz.exists()):
            raise RuntimeError(f"DINOv2 cache miss for {split}; not recomputing (no GPU here)")
    from sn8_clouds import ROAD_CLOUD_CUT, assessable
    from sn8_heldout import touched_roads
    from sn8_stages import production_cloud_rule
    r = touched_roads(include_cloudy=True)
    assert set(r.split) <= {"train", "val"}, "development roads only"
    out = r[["tile_id", "road_id", "split"]].reset_index(drop=True)
    out["flooded"] = r.flooded.astype(bool).to_numpy()
    out["tile_rule"] = ~r.cloudy.astype(bool).to_numpy()                       # the 891
    out["production_rule"] = np.asarray(assessable(r, production_cloud_rule()), bool)   # the 798
    out["thin_cloud"] = out.tile_rule.to_numpy() & (r.cloud_dark_rise_road.to_numpy() >= ROAD_CLOUD_CUT)
    assert len(out) == N_DEV_ROADS and set(out.tile_id) <= set(_dev_tiles().tile_id)
    return out


def dev_roads():
    """A copy of the 1,037 dev roads (tile_id, road_id, split, flooded and the tile_rule / production_rule /
    thin_cloud masks), in touched_roads(include_cloudy=True) order."""
    return _dev_roads().copy()


def _check(roads):
    """Stop unless every row is a development road (counts only are reported, never ids)."""
    tiles = set(_dev_tiles().tile_id)
    n_bad = len(set(map(str, roads.tile_id)) - tiles)
    if n_bad:
        raise ValueError(f"{n_bad} tile(s) are not development tiles; spatial folds cover the 226 dev tiles only")
    d = _dev_roads()
    if not set(zip(roads.tile_id, roads.road_id)) <= set(zip(d.tile_id, d.road_id)):
        raise ValueError("some rows are not development roads (tile_id, road_id)")
    if "flooded" in roads:
        key = dict(zip(zip(d.tile_id, d.road_id), d.flooded))
        if any(key[k] != bool(f) for k, f in zip(zip(roads.tile_id, roads.road_id), roads.flooded)):
            raise ValueError("flooded differs from the development labels")


# ---------- blocks ----------

def _find(parent, a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


@lru_cache(maxsize=8)
def _blocks(block_tiles=BLOCK_TILES):
    """Square grid blocks on the projected dev centroids, then the merge-or-purge decision. Returns (tiles, info)."""
    t = _dev_tiles().copy()
    r = _dev_roads()
    side = block_tiles * float(np.sqrt(np.median(t.w_m * t.h_m)))     # same area as block_tiles x block_tiles tiles
    ox, oy = float((t.x_m - t.w_m / 2).min()), float((t.y_m + t.h_m / 2).max())   # NW corner of the dev extent
    t["bx"] = np.floor((t.x_m - ox) / side).astype(int)
    t["by"] = np.floor((oy - t.y_m) / side).astype(int)
    t["grid_block"] = [f"b{a:02d}_{b:02d}" for a, b in zip(t.bx, t.by)]
    grid_of = dict(zip(t.tile_id, t.grid_block))
    parent = {b: b for b in t.grid_block}
    road_blocks = r.tile_id.map(grid_of)
    for bs in road_blocks.groupby(r.road_id).unique():               # union every two blocks that share a road id
        for b in bs[1:]:
            ra, rb = _find(parent, bs[0]), _find(parent, b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    t["merged_block"] = [_find(parent, b) for b in t.grid_block]
    merged_roads = r.tile_id.map(dict(zip(t.tile_id, t.merged_block))).value_counts()
    largest = int(merged_roads.iloc[0])
    share = largest / len(r)
    route = "merge" if share <= MERGE_MAX_SHARE else "purge"
    t["block"] = t.merged_block if route == "merge" else t.grid_block
    roads_per_grid = road_blocks.value_counts()
    ids_cross = int((road_blocks.groupby(r.road_id).nunique() > 1).sum())
    info = {"route": route, "block_tiles": block_tiles, "block_side_m": side, "origin_m": [ox, oy],
            "grid blocks": int(t.grid_block.nunique()), "grid blocks with roads": int(len(roads_per_grid)),
            "road ids": int(r.road_id.nunique()), "road ids on more than one tile":
                int((r.groupby("road_id").tile_id.nunique() > 1).sum()),
            "road ids crossing a grid-block edge": ids_cross,
            "roads with such ids": int(r.road_id.isin(road_blocks.groupby(r.road_id).nunique()
                                                      .loc[lambda s: s > 1].index).sum()),
            "merged blocks (with roads)": int(len(merged_roads)),
            "merged block sizes (roads)": merged_roads.astype(int).tolist(),
            "merged block sizes (grid blocks)": t.drop_duplicates("grid_block").merged_block.value_counts()
                .loc[merged_roads.index].astype(int).tolist(),
            "largest merged block: roads": largest, "largest merged block: share of dev roads": share,
            "merge threshold (share)": MERGE_MAX_SHARE}
    info["why"] = (f"merging the {info['grid blocks']} grid blocks that share a road id leaves "
                   f"{info['merged blocks (with roads)']} blocks, the largest holding {largest} of {len(r)} dev roads "
                   f"({100 * share:.1f}%), " + ("<= 25%, so blocks are merged" if route == "merge" else
                   "> 25%, so the grid blocks are kept and each fold's training roads that share a road id with "
                   "its held-out roads are purged"))
    return t, info


def block_info(block_tiles=BLOCK_TILES):
    """The block numbers and the route taken (merge or purge) with the reason."""
    return dict(_blocks(block_tiles)[1])


@lru_cache(maxsize=1)
def _adjacent():
    """226 x 226: tiles that touch (8-neighbours in the same region grid, or centroids within BUFFER_M) and the
    centroid distances (m)."""
    t = _dev_tiles()
    xy = t[["x_m", "y_m"]].to_numpy()
    dist = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    reg, col, row = (t[c].to_numpy() for c in ("region", "col", "row"))
    eight = (reg[:, None] == reg[None, :]) & (np.abs(col[:, None] - col[None, :]) <= 1) & \
        (np.abs(row[:, None] - row[None, :]) <= 1)
    adj = (eight | (dist <= BUFFER_M)) & ~np.eye(len(t), dtype=bool)
    return adj, dist


def _touching(tile_ids):
    """Dev tiles that touch any of tile_ids (not including tile_ids themselves)."""
    t = _dev_tiles()
    m = t.tile_id.isin(set(tile_ids)).to_numpy()
    adj, _ = _adjacent()
    return set(t.tile_id[adj[m].any(axis=0) & ~m])


# ---------- the block-to-fold maps ----------

def _assign_roadless(fold, blocks_tiles, n_splits):
    """Blocks with no dev road (they matter for the cell folds only) go, in name order, to the fold with the fewest
    tiles so far (ties to the lower fold)."""
    tiles_per_fold = np.zeros(n_splits, int)
    size = blocks_tiles.value_counts()
    for b, k in fold.items():
        tiles_per_fold[k] += int(size.get(b, 0))
    for b in sorted(set(blocks_tiles) - set(fold)):
        k = int(np.argmin(tiles_per_fold))
        fold[b] = k
        tiles_per_fold[k] += int(size[b])
    return fold


@lru_cache(maxsize=256)
def _fold_of_block(seed, n_splits, block_tiles):
    """StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed) over all 1,037 dev roads, groups = block,
    y = flooded, computed once; every block gets the fold its roads were held out in."""
    t, _ = _blocks(block_tiles)
    r = _dev_roads()
    blk = r.tile_id.map(dict(zip(t.tile_id, t.block))).to_numpy()
    fold = {}
    split = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for k, (_, te) in enumerate(split.split(blk, r.flooded.astype(int).to_numpy(), groups=blk)):
        for b in np.unique(blk[te]):
            fold[b] = k
    return dict(_assign_roadless(fold, t.block, n_splits))


@lru_cache(maxsize=2048)
def _inner_fold_of_block(seed, outer_fold, n_splits, n_inner, block_tiles):
    """The inner map for one outer fold: the same splitter (same seed) over the dev roads of the outer-training blocks
    only, groups = block; roadless outer-training blocks by the fewest-tiles rule."""
    t, _ = _blocks(block_tiles)
    outer = _fold_of_block(seed, n_splits, block_tiles)
    r = _dev_roads()
    blk = r.tile_id.map(dict(zip(t.tile_id, t.block))).to_numpy()
    keep = np.array([outer[b] != outer_fold for b in blk])
    fold = {}
    split = StratifiedGroupKFold(n_splits=n_inner, shuffle=True, random_state=seed)
    for j, (_, te) in enumerate(split.split(blk[keep], r.flooded.to_numpy()[keep].astype(int), groups=blk[keep])):
        for b in np.unique(blk[keep][te]):
            fold[b] = j
    outer_train_tiles = t.block[t.block.map(outer) != outer_fold]
    return dict(_assign_roadless(fold, outer_train_tiles, n_inner))


def fold_table(seed=SEED, n_splits=N_SPLITS, block_tiles=BLOCK_TILES):
    """One row per dev tile: tile_id, block, fold (0 .. n_splits-1), plus split, region, col, row, the projected
    centroid and size (m), the grid and merged block and the number of dev roads on the tile."""
    t, _ = _blocks(block_tiles)
    fob = _fold_of_block(seed, n_splits, block_tiles)
    out = t[["tile_id", "block", "split", "region", "col", "row", "x_m", "y_m", "w_m", "h_m", "grid_block",
             "merged_block"]].copy()
    out.insert(2, "fold", out.block.map(fob).astype(int))
    out["dev_roads"] = out.tile_id.map(_dev_roads().tile_id.value_counts()).fillna(0).astype(int)
    return out.reset_index(drop=True)


def _tile_fold(seed, n_splits, block_tiles):
    ft = fold_table(seed, n_splits, block_tiles)
    return dict(zip(ft.tile_id, ft.fold))


# ---------- folds over roads ----------

def _drop(tr, roads, held_ids, held_tiles, purge, buffer):
    """Training positions minus purged roads (road id among the held-out dev roads) and, if buffer, minus the roads on
    dev tiles that touch a held-out tile."""
    if purge:
        tr = tr[~np.isin(roads.road_id.to_numpy()[tr], list(held_ids))]
    if buffer:
        tr = tr[~np.isin(roads.tile_id.to_numpy()[tr], list(_touching(held_tiles)))]
    return tr


def spatial_folds(roads, seed=SEED, n_splits=N_SPLITS, buffer=False, block_tiles=BLOCK_TILES):
    """[(train_index, test_index), ...] over the rows of `roads` (positions, as scikit-learn splitters give).

    A road is held out in the fold of its block. If the purge route was taken (see block_info()), each fold's
    training roads whose road_id occurs among that fold's held-out dev roads are dropped from training (they are
    still scored when they are held out). buffer=True also drops every training road on a dev tile that touches a
    tile holding held-out dev roads (8-neighbour in the same region grid, or centroids within 600 m): Roberts et
    al.'s buffered block CV, a sensitivity arm."""
    _check(roads)
    purge = _blocks(block_tiles)[1]["route"] == "purge"
    tf = _tile_fold(seed, n_splits, block_tiles)
    f = roads.tile_id.map(tf).to_numpy()
    d = _dev_roads()
    dfold = d.tile_id.map(tf).to_numpy()
    out = []
    for k in range(n_splits):
        te, tr = np.flatnonzero(f == k), np.flatnonzero(f != k)
        held = dfold == k
        tr = _drop(tr, roads, set(d.road_id[held]), set(d.tile_id[held]), purge, buffer)
        out.append((tr, te))
    return out


def nested_spatial_folds(roads, seed=SEED, n_splits=N_SPLITS, n_inner=N_SPLITS, buffer=False,
                         block_tiles=BLOCK_TILES):
    """[(outer_train, outer_test, [(inner_train, inner_test), ...]), ...]; every index is a position in `roads`.

    The outer folds are spatial_folds(roads, seed, n_splits, buffer). In each outer fold the inner folds split the
    outer-training rows only, by block: StratifiedGroupKFold(n_inner, shuffle=True, random_state=seed) over the dev
    roads of the outer-training blocks (so subsets share inner folds too). Purging (purge route) and buffering are
    applied again inside, relative to the inner held-out blocks. Nothing of the outer held-out fold enters an inner
    fold."""
    _check(roads)
    purge = _blocks(block_tiles)[1]["route"] == "purge"
    t, _ = _blocks(block_tiles)
    blk_of = dict(zip(t.tile_id, t.block))
    d = _dev_roads()
    dblk = d.tile_id.map(blk_of).to_numpy()
    rblk = roads.tile_id.map(blk_of).to_numpy()
    out = []
    for k, (tr, te) in enumerate(spatial_folds(roads, seed, n_splits, buffer, block_tiles)):
        inner_map = _inner_fold_of_block(seed, k, n_splits, n_inner, block_tiles)
        j_of = np.array([inner_map[b] for b in rblk[tr]])
        dj = np.array([inner_map.get(b, -1) for b in dblk])
        inner = []
        for j in range(n_inner):
            ite, itr = tr[j_of == j], tr[j_of != j]
            held = dj == j
            itr = _drop(itr, roads, set(d.road_id[held]), set(d.tile_id[held]), purge, buffer)
            inner.append((itr, ite))
        out.append((tr, te, inner))
    return out


def tile_folds(roads, seed=SEED, n_splits=N_SPLITS, over="own"):
    """The old folds: StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed) by tile with y = flooded.
    over="own" splits over the rows of `roads`, as most scripts do (e.g. the 798 or the 891 split over their own
    roads; on the 1,037 in their order it is the split of evaluate_pipeline_factorial.py). over="dev" splits over
    all 1,037 dev roads and keeps the rows of `roads`, as the factorial and the cloud tests score a gate's kept roads.
    No purging and no buffer."""
    _check(roads)
    split = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    if over == "own":
        return list(split.split(roads, roads.flooded.astype(int).to_numpy(), groups=roads.tile_id.to_numpy()))
    if over != "dev":
        raise ValueError("over must be 'own' or 'dev'")
    d = _dev_roads()
    tf = {}
    for k, (_, te) in enumerate(split.split(d, d.flooded.astype(int).to_numpy(), groups=d.tile_id.to_numpy())):
        tf.update(dict.fromkeys(d.tile_id.to_numpy()[te], k))
    f = roads.tile_id.map(tf).to_numpy()
    return [(np.flatnonzero(f != k), np.flatnonzero(f == k)) for k in range(n_splits)]


def size_matched_tile_folds(roads, seed=SEED, n_splits=N_SPLITS, block_tiles=BLOCK_TILES):
    """A control for the optimism gap: purging (and the blocks) make spatial training sets smaller, which lowers
    accuracy by itself. These are tile_folds(over="dev") with fold k's dev training roads subsampled at random
    (numpy default_rng(seed), without replacement) to the size of spatial fold k's dev training roads, then restricted
    to the rows of `roads`. Tile minus size-matched = what the smaller training sets cost; size-matched minus spatial
    = what leakage and nearness were worth."""
    _check(roads)
    d = _dev_roads()
    rng = np.random.default_rng(seed)
    pos = {k: i for i, k in enumerate(zip(d.tile_id, d.road_id, d.groupby(["tile_id", "road_id"]).cumcount()))}
    keys = list(zip(roads.tile_id, roads.road_id, roads.groupby(["tile_id", "road_id"]).cumcount()))
    if len(set(keys)) != len(keys) or any(k not in pos for k in keys):
        raise ValueError("rows must be distinct development roads")
    dev_row = np.array([pos[k] for k in keys])
    out = []
    for (dtr, _), (str_, _), (_, te) in zip(tile_folds(d, seed, n_splits, over="dev"),
                                            spatial_folds(d, seed, n_splits, False, block_tiles),
                                            tile_folds(roads, seed, n_splits, over="dev")):
        kept = np.zeros(len(d), bool)
        kept[rng.choice(dtr, size=len(str_), replace=False)] = True
        out.append((np.flatnonzero(kept[dev_row] & ~np.isin(np.arange(len(roads)), te)), te))
    return out


# ---------- folds over cells (Track A, road finding) ----------

def cell_folds(cell_tile_ids, seed=SEED, n_splits=N_SPLITS, buffer=False, block_tiles=BLOCK_TILES):
    """[(train_index, test_index), ...] over cells: each cell is held out in its tile's block fold (the same map as
    the roads; blocks without roads by the fewest-tiles rule). buffer=True also drops training cells on dev tiles
    that touch a held-out tile. Cells carry no road id, so nothing is purged."""
    ids = np.asarray(cell_tile_ids).astype(str)
    tf = _tile_fold(seed, n_splits, block_tiles)
    n_bad = len(set(ids) - set(tf))
    if n_bad:
        raise ValueError(f"{n_bad} tile(s) are not development tiles; spatial folds cover the 226 dev tiles only")
    f = np.array([tf[i] for i in ids])
    out = []
    for k in range(n_splits):
        te, tr = np.flatnonzero(f == k), np.flatnonzero(f != k)
        if buffer:
            near = _touching({i for i, v in tf.items() if v == k})
            tr = tr[~np.isin(ids[tr], list(near))]
        out.append((tr, te))
    return out


def nested_cell_folds(cell_tile_ids, seed=SEED, n_splits=N_SPLITS, n_inner=N_SPLITS, block_tiles=BLOCK_TILES):
    """[(outer_train, outer_test, [(inner_train, inner_test), ...]), ...] over cells, with the same outer and inner
    block maps as nested_spatial_folds (for choosing a cut-off inside the outer-training blocks only)."""
    ids = np.asarray(cell_tile_ids).astype(str)
    t, _ = _blocks(block_tiles)
    blk = np.array([dict(zip(t.tile_id, t.block))[i] for i in ids])
    out = []
    for k, (tr, te) in enumerate(cell_folds(ids, seed, n_splits, False, block_tiles)):
        inner_map = _inner_fold_of_block(seed, k, n_splits, n_inner, block_tiles)
        j_of = np.array([inner_map[b] for b in blk[tr]])
        out.append((tr, te, [(tr[j_of != j], tr[j_of == j]) for j in range(n_inner)]))
    return out


# ---------- a splitter for scikit-learn and the library ----------

class FixedFolds:
    """Hands back precomputed folds through the scikit-learn splitter interface (cross_val_predict(cv=...), and the
    library functions that call folds.split(table, y, groups=...)). Stops if used on a table of another length."""

    def __init__(self, folds, n_rows):
        self.folds = [(np.asarray(tr), np.asarray(te)) for tr, te, *_ in folds]
        self.n_rows = int(n_rows)

    def split(self, X, y=None, groups=None):
        if len(X) != self.n_rows:
            raise ValueError(f"these folds are for {self.n_rows} rows, not {len(X)}")
        yield from self.folds

    def get_n_splits(self, X=None, y=None, groups=None):
        return len(self.folds)


def splitter(folds, rows):
    """FixedFolds(folds, len(rows)): e.g. cue_predictions(roads, cols, splitter(spatial_folds(roads), roads))."""
    return FixedFolds(folds, len(rows))


# ======================================================================================================================
# Run as a script: build, check, write the numbers and the picture (no model is fitted or scored)
# ======================================================================================================================

def _leak(roads, folds):
    """Held-out roads whose road_id occurs among the same fold's training roads: count and share."""
    rid = roads.road_id.to_numpy()
    n = sum(int(np.isin(rid[te], rid[tr]).sum()) for tr, te, *_ in folds)
    return n, n / len(roads)


def _nearest(roads, folds):
    """For each held-out tile (a tile with held-out roads), the centroid distance to the nearest tile with training
    roads in that fold, pooled over folds; and the share whose nearest training tile touches it."""
    t = _dev_tiles()
    pos = {k: i for i, k in enumerate(t.tile_id)}
    adj, dist = _adjacent()
    tid = roads.tile_id.to_numpy()
    d, touch = [], []
    for tr, te, *_ in folds:
        h = [pos[x] for x in np.unique(tid[te])]
        g = [pos[x] for x in np.unique(tid[tr])]
        d.extend(dist[np.ix_(h, g)].min(axis=1))
        touch.extend(adj[np.ix_(h, g)].any(axis=1))
    d = np.array(d)
    return {"median_m": float(np.median(d)), "min_m": float(d.min()), "mean_m": float(d.mean()),
            "share of held-out tiles touching a training tile": float(np.mean(touch)), "held-out tiles": len(d)}


def _correlogram(r):
    """Raw-label dependence: the Moran-type correlation of `flooded` between dev roads on different tiles with
    different road ids, by tile-centroid distance band (labels only; no model)."""
    t = _dev_tiles()
    pos = {k: i for i, k in enumerate(t.tile_id)}
    _, dist = _adjacent()
    i = r.tile_id.map(pos).to_numpy()
    D = dist[np.ix_(i, i)]
    z = r.flooded.astype(float).to_numpy()
    z = (z - z.mean()) / z.std()
    zz = z[:, None] * z[None, :]
    rid = r.road_id.to_numpy()
    ok = (i[:, None] != i[None, :]) & (rid[:, None] != rid[None, :])
    ok &= np.triu(np.ones_like(ok), 1).astype(bool)
    bands = [0, 1000, 2000, 3000, 4000, 6000, 8000, 12000, 16000, 24000]
    rows = []
    for lo, hi in zip(bands[:-1], bands[1:]):
        m = ok & (D >= lo) & (D < hi)
        rows.append({"band_km": f"{lo / 1000:g}-{hi / 1000:g}", "pairs": int(m.sum()),
                     "correlation": float(zz[m].mean()) if m.any() else None})
    return rows


def _fold_rows(r, folds, masks, tile_fold=None):
    """Per fold: held-out tiles, roads, flooded share, training roads (after purge / buffer), on each mask."""
    y = r.flooded.to_numpy()
    rows = []
    for k, (tr, te) in enumerate(folds):
        row = {"fold": k + 1, "held-out tiles (with roads)": int(r.tile_id.iloc[te].nunique())}
        if tile_fold is not None:
            row["held-out tiles (all, incl. roadless)"] = int(sum(v == k for v in tile_fold.values()))
        for name, m in masks.items():
            te_m, tr_m = te[m[te]], tr[m[tr]]
            row[f"{name}: held-out roads"] = int(len(te_m))
            row[f"{name}: held-out flooded share"] = float(y[te_m].mean()) if len(te_m) else None
            row[f"{name}: training roads"] = int(len(tr_m))
        rows.append(row)
    return rows


def _plain(v):
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else float(f"{float(v):.6g}")
    if isinstance(v, np.ndarray):
        return _plain(v.tolist())
    return v


def _assert_partition(roads, folds, name):
    n = len(roads)
    tests = np.concatenate([te for _, te, *_ in folds])
    assert len(tests) == n and len(np.unique(tests)) == n, f"{name}: the test folds do not partition the roads"
    for tr, te, *_ in folds:
        assert not np.intersect1d(tr, te).size, f"{name}: a road is in both training and test"


def _figure(r, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, Rectangle

    colours = ["#2a78d6", "#eda100", "#1baf7a", "#e87ba4", "#008300"]   # validated, digits as the second encoding
    ink, muted, grey = "#0b0b0b", "#52514e", "#d9d8d4"
    t, info = _blocks()
    ft = fold_table(SEED)
    sf = dict(zip(ft.tile_id, ft.fold))
    old = tile_folds(r, SEED)
    of = {}
    leak_tiles = set()
    rid, tid = r.road_id.to_numpy(), r.tile_id.to_numpy()
    for k, (tr, te) in enumerate(old):
        of.update(dict.fromkeys(tid[te], k))
        leak_tiles |= set(tid[te][np.isin(rid[te], rid[tr])])
    n_leak_old = _leak(r, old)[0]
    n_leak_new = _leak(r, spatial_folds(r, SEED))[0]
    side, (ox, oy) = info["block_side_m"], info["origin_m"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 9.4), facecolor="white")
    titles = [f"New: spatial block folds (seed 662)\n{info['grid blocks']} blocks of ~{side / 1000:.2f} km, "
              f"purged; {n_leak_new} of {len(r)} held-out roads share an id with training",
              f"Old: tile folds (seed 662), each tile on its own\n{n_leak_old} of {len(r)} held-out roads share an "
              f"id with training (dot on their tile)"]
    for ax, fmap, title, is_new in ((axes[0], sf, titles[0], True), (axes[1], of, titles[1], False)):
        for _, s in t.iterrows():
            k = fmap.get(s.tile_id)
            roadless = s.tile_id not in set(r.tile_id)
            face = colours[k] if k is not None else grey
            ax.add_patch(Rectangle((s.x_m - s.w_m / 2, s.y_m - s.h_m / 2), s.w_m, s.h_m, facecolor=face,
                                   edgecolor="white", linewidth=0.6, alpha=0.45 if roadless else 0.9,
                                   hatch="////" if roadless else None))
            if k is not None:
                ax.text(s.x_m, s.y_m, str(k + 1), ha="center", va="center", fontsize=5.5, color=ink)
            if not is_new and s.tile_id in leak_tiles:
                ax.plot(s.x_m + s.w_m * 0.28, s.y_m + s.h_m * 0.28, "o", ms=2.4, color=ink)
        for bx, by in t[["bx", "by"]].drop_duplicates().itertuples(index=False):
            ax.add_patch(Rectangle((ox + bx * side, oy - (by + 1) * side), side, side, fill=False,
                                   edgecolor=ink if is_new else muted, linewidth=1.1 if is_new else 0.5,
                                   linestyle="-" if is_new else ":"))
        pad = 400
        ax.set_xlim((t.x_m - t.w_m / 2).min() - pad, (t.x_m + t.w_m / 2).max() + pad)
        ax.set_ylim((t.y_m - t.h_m / 2).min() - 1100, (t.y_m + t.h_m / 2).max() + pad)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=11, color=ink, loc="left")
        ax.set_xlabel("east (m, local equirectangular)", fontsize=9, color=muted)
        ax.set_ylabel("north (m)", fontsize=9, color=muted)
        ax.tick_params(labelsize=8, colors=muted)
        for sp in ax.spines.values():
            sp.set_color(grey)
        for reg, name in ((2, "west (region 2)"), (0, "south (region 0)")):
            s = t[t.region == reg]
            ax.text(s.x_m.mean(), (s.y_m - s.h_m / 2).min() - 700, name, ha="center", fontsize=9, color=muted,
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
    handles = [Patch(facecolor=c, edgecolor="white", label=f"fold {k + 1}") for k, c in enumerate(colours)]
    handles += [Patch(facecolor=grey, edgecolor=muted, hatch="////", alpha=0.6,
                      label="no touched road (cells only; old folds: no fold)"),
                Patch(fill=False, edgecolor=ink, label="spatial block outline")]
    fig.legend(handles=handles, loc="lower center", ncol=7, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.022))
    fig.suptitle("Louisiana-East development tiles (train + val, 226 tiles, 1,037 roads): fold of each tile",
                 fontsize=13, color=ink, x=0.06, ha="left")
    fig.text(0.06, 0.006, "Fold number printed in each tile. Test, negative and sealed tiles are not shown and were "
             "not read. Tile footprints from GeoTIFF tags.", fontsize=8, color=muted)
    fig.tight_layout(rect=(0, 0.075, 1, 0.95))
    fig.subplots_adjust(bottom=0.1)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    t0 = time.time()
    tiles = _dev_tiles()
    r = _dev_roads()
    assert set(r.split) <= {"train", "val"}
    assert (len(tiles), len(r), int(r.production_rule.sum()), int(r.tile_rule.sum())) == (226, 1037, 798, 891)
    hazy = r.thin_cloud.to_numpy()
    haze_tiles = set(r.tile_id[hazy])
    groups = {"trusted flooded (thin cloud)": hazy & r.flooded.to_numpy(),
              "dry-labelled (thin cloud)": hazy & ~r.flooded.to_numpy(),
              "control (assessable, same tiles)": r.tile_id.isin(haze_tiles).to_numpy() & r.production_rule.to_numpy()}
    assert [int(m.sum()) for m in groups.values()] == [24, 69, 175], "cloud groups differ from the factorial"
    calls = pd.read_csv(HERE.parent / "pipeline_factorial_calls.csv", usecols=["tile_id", "road_id"])
    assert calls.tile_id.equals(r.tile_id) and calls.road_id.equals(r.road_id), "row order differs from the factorial"
    print(f"dev tiles {len(tiles)}, dev roads {len(r)} (798 production rule, 891 tile rule); row order = factorial "
          f"({round(time.time() - t0)} s)", flush=True)

    t, info = _blocks()
    print("route:", info["route"], "-", info["why"], flush=True)
    tiles_per_block = t.block.value_counts()
    roads_per_block = r.tile_id.map(dict(zip(t.tile_id, t.block))).value_counts()
    blocks = {"blocks": int(t.block.nunique()), "blocks with dev roads": int(len(roads_per_block)),
              "tiles per block": tiles_per_block.describe()[["min", "25%", "50%", "mean", "75%", "max"]].to_dict(),
              "roads per block (blocks with roads)": roads_per_block.describe()[["min", "25%", "50%", "mean", "75%",
                                                                                 "max"]].to_dict(),
              "tiles per block (all)": tiles_per_block.sort_index().astype(int).to_dict(),
              "roads per block (all)": roads_per_block.reindex(sorted(t.block.unique())).fillna(0).astype(int)
                  .to_dict(),
              "dev tiles without a touched road": int((~tiles.tile_id.isin(r.tile_id)).sum()),
              "blocks without a touched road": int(t.block.nunique() - len(roads_per_block))}

    masks = {"1037": np.ones(len(r), bool), "798": r.production_rule.to_numpy(), "891": r.tile_rule.to_numpy()}
    sub798 = r[masks["798"]].reset_index(drop=True)
    idx798 = np.flatnonzero(masks["798"])
    adjacency_note = {"neighbour rule": "8-neighbour in the same region grid, or centroids within 600 m",
                      "min cross-region centroid distance m": float(_adjacent()[1][np.ix_(
                          (tiles.region == 0).to_numpy(), (tiles.region == 2).to_numpy())].min())}

    per_seed = []
    for s in SEEDS:
        sp = spatial_folds(r, s)
        sb = spatial_folds(r, s, buffer=True)
        tf = tile_folds(r, s)
        sp798 = spatial_folds(sub798, s)
        tf798 = tile_folds(sub798, s)
        tfdev798 = tile_folds(sub798, s, over="dev")
        # the grid blocks without purging, to show what purging removes
        tfm = _tile_fold(s, N_SPLITS, BLOCK_TILES)
        fk = r.tile_id.map(tfm).to_numpy()
        unpurged = [(np.flatnonzero(fk != k), np.flatnonzero(fk == k)) for k in range(N_SPLITS)]
        for name, rows, folds in (("spatial", r, sp), ("spatial buffered", r, sb), ("tile", r, tf),
                                  ("spatial 798", sub798, sp798), ("tile 798", sub798, tf798),
                                  ("tile dev->798", sub798, tfdev798), ("grid unpurged", r, unpurged)):
            _assert_partition(rows, folds, f"{name} seed {s}")
        # subsets inherit the folds: the 798's spatial folds are the 1,037's restricted to the 798
        for (tr, te), (tr8, te8) in zip(sp, sp798):
            assert np.array_equal(idx798[te8], np.intersect1d(te, idx798)), "798 test folds differ from the 1,037's"
            assert np.array_equal(idx798[tr8], np.intersect1d(tr, idx798)), "798 training folds differ"
        # a road is in exactly one test fold (also across subsets) and no non-dev tile appears
        assert set(fold_table(s).tile_id) == set(tiles.tile_id)
        lk = {name: _leak(rows, folds) for name, rows, folds in
              (("tile folds (1037)", r, tf), ("tile folds (798, own split)", sub798, tf798),
               ("tile folds (798, dev split)", sub798, tfdev798), ("spatial folds (1037)", r, sp),
               ("spatial folds (798)", sub798, sp798), ("spatial buffered (1037)", r, sb),
               ("grid blocks without purging (1037)", r, unpurged))}
        assert lk["spatial folds (1037)"][0] == 0 and lk["spatial folds (798)"][0] == 0
        assert lk["spatial buffered (1037)"][0] == 0
        purged = [int(len(np.flatnonzero(fk != k)) - len(sp[k][0])) for k in range(N_SPLITS)]
        buffered = [int(len(sp[k][0]) - len(sb[k][0])) for k in range(N_SPLITS)]
        per_seed.append({"seed": s, "leak": lk,
                         "nearest": {"tile folds": _nearest(r, tf), "spatial folds": _nearest(r, sp),
                                     "spatial buffered": _nearest(r, sb)},
                         "purged per fold": purged, "buffer-dropped per fold": buffered,
                         "held-out roads per fold": [int(len(te)) for _, te in sp],
                         "held-out flooded share per fold": [float(r.flooded.to_numpy()[te].mean()) for _, te in sp],
                         "tile folds held-out roads per fold": [int(len(te)) for _, te in tf]})
        print(f"seed {s:3d}: leakage tile {lk['tile folds (1037)'][0]:4d} ({100 * lk['tile folds (1037)'][1]:.1f}%), "
              f"spatial {lk['spatial folds (1037)'][0]}; unpurged grid {lk['grid blocks without purging (1037)'][0]}; "
              f"purged {sum(purged)}, buffer drops {sum(buffered)}; held-out roads/fold "
              f"{per_seed[-1]['held-out roads per fold']}", flush=True)

    # nested folds: the inner folds never use the outer held-out rows, and inner tests partition the outer training
    for s in (662, 1):
        for rows in (r, sub798):
            for tr, te, inner in nested_spatial_folds(rows, s):
                tests = np.concatenate([ite for _, ite in inner])
                assert np.array_equal(np.sort(tests), np.sort(tr)), "inner tests must partition the outer training"
                for itr, ite in inner:
                    assert not np.intersect1d(itr, te).size and not np.intersect1d(ite, te).size
                    assert not np.intersect1d(itr, ite).size
                    rid = rows.road_id.to_numpy()
                    assert not np.isin(rid[ite], rid[itr]).any(), "inner leakage"
    # size-matched control: tile test folds, training sets as large as spatial's (1,037), nested in the tile training
    for s in (662, 1, 2):
        for rows in (r, sub798):
            sm, tf_, sp_ = size_matched_tile_folds(rows, s), tile_folds(rows, s, over="dev"), spatial_folds(rows, s)
            _assert_partition(rows, sm, f"size-matched seed {s}")
            for (a, b), (c, e) in zip(sm, tf_):
                assert np.array_equal(b, e) and np.isin(a, c).all()
        for (a, _), (c, _) in zip(size_matched_tile_folds(r, s), spatial_folds(r, s)):
            assert len(a) == len(c), "size-matched training sets must equal the spatial ones on the 1,037"
    # block-size scan (the raw-label correlogram suggests dependence beyond 3 x 3 tiles)
    scan = []
    for bt in (3, 4, 5, 6, 7):
        bi = block_info(bt)
        held, train_n, flo, purged_n = [], [], [], []
        for s in SEEDS:
            f = spatial_folds(r, s, block_tiles=bt)
            assert _leak(r, f)[0] == 0
            _assert_partition(r, f, f"block_tiles {bt} seed {s}")
            held += [len(te) for _, te in f]
            train_n += [len(tr) for tr, _ in f]
            flo += [float(r.flooded.to_numpy()[te].mean()) for _, te in f]
            purged_n.append(sum(len(r) - len(te) - len(tr) for tr, te in f))
        scan.append({"block_tiles": bt, "side_m": bi["block_side_m"], "route": bi["route"],
                     "blocks": bi["grid blocks"], "blocks with roads": bi["grid blocks with roads"],
                     "largest merged share": bi["largest merged block: share of dev roads"],
                     "held-out roads per fold (min, max over 21 seeds)": [min(held), max(held)],
                     "training roads per fold (mean, min)": [float(np.mean(train_n)), min(train_n)],
                     "held-out flooded share per fold (min, max)": [min(flo), max(flo)],
                     "purged per seed (mean)": float(np.mean(purged_n))})
        print(f"block_tiles {bt}: {scan[-1]}", flush=True)
    # cell folds: every dev tile, one fold each, consistent with the road folds
    cf = cell_folds(tiles.tile_id.to_numpy(), SEED)
    tests = np.concatenate([te for _, te in cf])
    assert len(tests) == len(tiles) and len(np.unique(tests)) == len(tiles)
    tfm = _tile_fold(SEED, N_SPLITS, BLOCK_TILES)
    for k, (_, te) in enumerate(cf):
        assert all(tfm[x] == k for x in tiles.tile_id.to_numpy()[te])
    for tr, te, inner in nested_cell_folds(tiles.tile_id.to_numpy(), SEED):
        assert np.array_equal(np.sort(np.concatenate([ite for _, ite in inner])), np.sort(tr))
    print("asserts passed: partitions, no road in two test folds, subsets inherit folds, zero leakage under spatial "
          "folds, nested and cell folds consistent, dev tiles only", flush=True)

    # primary seed per fold
    sp, sb, tf = spatial_folds(r, SEED), spatial_folds(r, SEED, buffer=True), tile_folds(r, SEED)
    y = r.flooded.to_numpy()
    per_fold = {"spatial": _fold_rows(r, sp, masks, tfm), "spatial buffered": _fold_rows(r, sb, masks),
                "tile (split over the 1,037)": _fold_rows(r, tf, masks),
                "tile (split over the 798 itself)": _fold_rows(sub798, tile_folds(sub798, SEED),
                                                               {"798": np.ones(len(sub798), bool)})}
    for k, (_, te) in enumerate(sp):
        for g, m in groups.items():
            per_fold["spatial"][k][f"cloud group: {g}"] = int(m[te].sum())
        per_fold["spatial"][k]["blocks"] = int(sum(v == k for v in _fold_of_block(SEED, N_SPLITS, BLOCK_TILES)
                                                   .values()))
        per_fold["spatial"][k]["purged training roads"] = per_seed[0]["purged per fold"][k]
        per_fold["spatial"][k]["buffer-dropped training roads"] = per_seed[0]["buffer-dropped per fold"][k]
        per_fold["spatial"][k]["buffer-dropped training roads (798)"] = int(
            masks["798"][sp[k][0]].sum() - masks["798"][sb[k][0]].sum())

    def seed_stats(get):
        v = np.array([get(p) for p in per_seed], float)
        return {"seed 662": float(v[0]), "mean": float(v.mean()), "sd": float(v.std(ddof=1)), "min": float(v.min()),
                "max": float(v.max())}

    leak_names = list(per_seed[0]["leak"])
    summary = {
        "leakage: held-out roads sharing a road id with the fold's training roads":
            {n: {"count": seed_stats(lambda p, n=n: p["leak"][n][0]),
                 "share": seed_stats(lambda p, n=n: p["leak"][n][1])} for n in leak_names},
        "nearest training-tile centroid distance to each held-out tile":
            {n: {"median_m": seed_stats(lambda p, n=n: p["nearest"][n]["median_m"]),
                 "min_m": seed_stats(lambda p, n=n: p["nearest"][n]["min_m"]),
                 "share touching a training tile":
                     seed_stats(lambda p, n=n: p["nearest"][n]["share of held-out tiles touching a training tile"])}
             for n in ("tile folds", "spatial folds", "spatial buffered")},
        "purged training roads (sum over folds)": seed_stats(lambda p: sum(p["purged per fold"])),
        "buffer-dropped training roads (sum over folds)": seed_stats(lambda p: sum(p["buffer-dropped per fold"])),
        "spatial held-out roads per fold": {"min over folds and seeds": int(min(min(p["held-out roads per fold"])
                                                                                for p in per_seed)),
                                            "max over folds and seeds": int(max(max(p["held-out roads per fold"])
                                                                                for p in per_seed))},
        "spatial held-out flooded share per fold": {
            "min over folds and seeds": float(min(min(p["held-out flooded share per fold"]) for p in per_seed)),
            "max over folds and seeds": float(max(max(p["held-out flooded share per fold"]) for p in per_seed)),
            "dev flooded share": float(y.mean())},
    }
    corr = _correlogram(r)
    print("raw-label correlogram:", [(c["band_km"], round(c["correlation"], 3) if c["correlation"] is not None
                                      else None) for c in corr], flush=True)

    numbers = {"what": "spatially blocked CV folds for flood per road; development data only (226 train + val tiles, "
                       "1,037 touched roads); no model fitted or scored",
               "method": "Roberts et al. 2017, Ecography 40(8) 913-929: block CV, blocks larger than the dependence "
                         "range, optional buffer",
               "projection": tiles.attrs["projection"], "route": info["route"], "why": info["why"], "blocks": {
                   **{k: v for k, v in info.items() if k not in ("why",)}, **blocks},
               "neighbours": adjacency_note,
               "fold assignment": "StratifiedGroupKFold(5, shuffle=True, random_state=seed) over the 1,037 dev roads, "
                                  "groups = block, y = flooded; blocks without roads to the fold with the fewest tiles; "
                                  "purge relative to each fold's held-out dev roads",
               "seeds": SEEDS, "summary over the 21 seeds": summary, "per fold at seed 662": per_fold,
               "per seed": per_seed,
               "raw-label correlogram (dev roads on different tiles, different road ids)": corr,
               "block-size scan (sensitivity; primary is 3)": scan,
               "size-matched tile folds (control)": "tile_folds(over='dev') with fold k's dev training roads "
                   "subsampled (default_rng(seed)) to the size of spatial fold k's dev training roads",
               "dev counts": {"tiles": len(tiles), "roads": len(r), "production rule": int(masks["798"].sum()),
                              "tile rule": int(masks["891"].sum()), "flooded": int(y.sum()),
                              **{g: int(m.sum()) for g, m in groups.items()}}}
    (HERE / "folds_numbers.json").write_text(json.dumps(_plain(numbers), indent=1))
    ftab = fold_table(SEED)[["tile_id", "split", "region", "col", "row", "x_m", "y_m", "block", "dev_roads"]]
    for s in SEEDS:
        ftab[f"fold_seed_{s}"] = ftab.tile_id.map(_tile_fold(s, N_SPLITS, BLOCK_TILES)) + 1
    ftab.round(1).to_csv(HERE / "fold_tables.csv", index=False)
    _figure(r, HERE / "fold_map.png")
    print(json.dumps(_plain({"route": info["route"], "why": info["why"], "blocks": blocks["blocks"],
                             "summary": summary}), indent=1))
    print("per fold at seed 662 (spatial):")
    print(pd.DataFrame(per_fold["spatial"]).to_string())
    print("per fold at seed 662 (tile, split over the 1,037):")
    print(pd.DataFrame(per_fold["tile (split over the 1,037)"]).to_string())
    print(f"wrote folds_numbers.json, fold_tables.csv, fold_map.png ({round(time.time() - t0)} s)")


if __name__ == "__main__":
    main()
