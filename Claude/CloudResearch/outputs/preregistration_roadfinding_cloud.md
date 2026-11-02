# Test plan: does de-hazing the after image help the road detector find roads under cloud? (written before running)

Written 2026-10-25 18:40 EDT, before any score was computed. Code: GeoAI-Roads 5d325d9 for every existing module
(none is edited). The new code goes in `ClaudeFunctions/sn8_cloudroads.py`; its source hash is logged with the run, and
its commit hash goes in the results. Script and logs: `evidence/pilot_scripts/roadfinding/`. Results:
`evidence/06_roadfinding_under_cloud.md`.

## Status
**Exploratory.** It runs on development tiles, and their cloudy after images have been looked at before. Nothing below
changes after the results are seen, and every outcome listed here is reported whatever it shows.

## Question
Under the two-date cloud gate, does the production road detector find more of the OpenStreetMap (OSM) roads on the
after image once that image is de-hazed? The detector is trained and called on the same kind of image.

**Why OSM:** the road lines in the SpaceNet 8 label files are OSM centrelines. Their geometry does not depend on what
analysts could see after the storm; only the `flooded` attribute does.

## Data (development only)
- **Tiles:** `df, train, val, test, negative = split_tables(662)`, using only the `train` (186) and `val` (40) tiles
  (226 tiles). No test tiles, north negative set, Germany or Louisiana-West. `allow_held_out` is never set.
- **Labels:**
  - road cells from the OSM centrelines of each tile's own label file, read through the library (`sn8_lines.road_mask`,
    `sn8_roads._road_lines`);
  - flood labels used only to split road cells, never as a target;
  - images in greyscale only (`tile_pair`).
- **Survey (label-free, done before this plan):** 123 of the 226 tiles have a cloud gate; 120 have correctable gate
  pixels and 75 have opaque ones.

## Cells and groups
- **Cells:** 2 m cells (4 x 4 pixels) that are fully valid on both dates. Valid is `sn8_clouds._tile`'s mask: both
  dates non-zero, eroded 6 px. The same mask is used for every arm, so the arms score identical cells.
- **Labels:** as in `sn8_detect.tile_cells`. A cell is road (1) when its centre is within 3.5 m of an OSM centreline,
  not road (0) beyond 8 m, and left out in between.
- **Groups, from `sn8_refhaze.dark_reference_dehaze` on each tile (label-free), by the cell's centre pixel:**
  - **correctable:** in the cloud gate and not opaque (t >= 0.2). These are the test cells of the primary outcome.
  - **opaque:** in the gate with t < 0.2. These are left as they are by the two-date method.
  - **fade margin:** outside the gate but within 20 m of it, where the two-date correction fades out (partly
    corrected). Reported, but in neither the test nor the control group.
  - **clear:** beyond the fade margin. This is the control.
- **Cells stored for scoring, the same positions in every arm:**
  - every road cell in the gate and the fade margin, and a seeded 25% sample of their not-road cells;
  - a seeded 5% uniform sample of the labelled clear cells of every tile;
  - every road cell on the tiles that hold one of the 239 set-aside roads (for the per-road rule below).
- **Weights:** scores are weighted by 1 / sampling share, so they stand for all cells at the natural road share. This
  is the weighting `sn8_cutoff.weighted_f1` uses.

## The detector (production, reproduced exactly)
- **Model:** `classical_models()["Random forest"]` (300 trees, seed 662), as `production_detector()` names it.
- **Features:** classical + DINOv2, 12 + 32 columns, as `production_detector_features()` names them. They are the
  `sn8_detect.tile_cells` feature maps and the `sn8_dino_cells` token components, measured on the arm's image.
  - The DINOv2 components keep production's basis (`cell_basis()`, fitted on the training tiles' before images). Arms
    that changed both the image and the basis would change two things at once.
- **Cut-off:** 0.75 (`production_cutoff()`).
- **Reproduction check, run before any score:** on two training tiles, with the before image and the before-only valid
  mask, the new module's features must equal `sn8_detect.tile_cells` and the cached `cell_dino_table("train")` rows to
  float tolerance (1e-4). If it fails, the code is fixed before anything is scored.
- **Training cells (production's rule, `sn8_detect.cell_table` for "train"):** per tile, up to 300 road cells and 3
  times as many not-road cells, seeded. The rule is applied to all 226 development tiles, so every tile can be held
  out once. The cell positions are the same in every arm, which keeps the road share at production's (about 25%), so
  the 0.75 cut-off means the same as it does in production.
- **Folds:** 5, by tile (`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)`), split on the training
  cells with their labels and tiles. Every stored cell of a tile is called by the model whose training folds left that
  tile out.

## Arms (the detector is trained and called on the same kind of image)
| Arm | Image the features are measured on |
|---|---|
| 1 as it is | the after image |
| 2 two-date | `dark_reference_dehaze(before, after, valid)["corrected"]` (identical to arm 1 on tiles with no gate) |
| 3 single image (He) | `sn8_clouds.dehaze(after, valid)[0]` (He, Sun & Tang 2011) |
| 4 before | the before image: the cloud-free reference, the upper bound |

## Outcomes
**Primary:** F1 of road cells against OSM in the correctable cells, arm 2 minus arm 1.
- The 95% interval comes from resampling whole tiles: 5000 resamples, seed 662, the same resampled tiles for both
  arms, over the tiles with correctable labelled cells.
- **"Helps"** means the difference is above 0 and its interval excludes 0.
- **Why F1, not recall:** recall alone rewards calling more cells road. In the flood test, de-hazing raised false
  alarms, and F1 counts both errors. Recall and precision are reported as secondary outcomes.

**Secondary** (every one reported; each has a tile-resampled 95% interval unless marked descriptive):
1. Recall and precision in the correctable cells, arm 2 against arm 1. Also exact McNemar tests on cells: on road cells
   (found / missed) and on not-road cells (false alarms). **Cells within a tile are correlated, so McNemar on cells
   overstates significance;** the tile interval is the main uncertainty.
2. F1 in the correctable cells: arm 3 against arm 1, and arm 2 against arm 3.
3. Arm 4 (before) in the correctable cells, the ceiling, and the share of the arm 1 to arm 4 gap that arm 2 closes
   (descriptive).
4. F1 in the opaque cells, every arm against arm 1.
5. F1 in the clear control, every arm against arm 1, on all development tiles and on the gated tiles only. A
   difference whose interval lies entirely below 0 is reported as harm.
6. **Flood confound:** recall on road cells, split by the nearest OSM road's development flood label ("flooded = yes"
   against not). Reported in the correctable, opaque and clear groups, arm 2 against arm 1.
   - Under cloud only "yes" is trusted. "Not" there mixes dry roads with unlabelled ones.
   - The arms are compared on the same cells, so water that hides a road hides it in every after-image arm.
7. **Threshold-free:** ROC AUC in the correctable cells (weighted), arm 2 against arm 1. The after-image detectors'
   probabilities may sit differently from production's.
8. **Cut-off sensitivity:** each arm's own F1 cut-off, chosen as `detector_test` does: `f1_cutoff` on the out-of-fold
   probabilities of the training cells, at production's real road share (`road_prior("train")`). It is then applied
   to the correctable cells (arm 2 against arm 1). This is not nested, so it is mildly optimistic, by the same amount
   in every arm.
9. Fade-margin cells: F1 per arm (descriptive).

## The roads that could come back (per road)
- **Roads:** the 239 development roads that production's cloud rule (tile rule + road rule) sets aside, from
  `touched_roads(include_cloudy=True)` and `assessable`.
- **Handling decision:** `sn8_refhaze.road_handling` gives each one ASSESS, CORRECT or CANNOT ASSESS (expected 15 /
  136 / 88; 55 of the CORRECT roads are on opaque-cloud tiles).
- **Rule (the project's visibility rule, `visibility_test.ipynb`):** a road is **visible** when the detector calls at
  least 50% of its own cells road at the 0.75 cut-off. A road's own cells are the cells whose centre is within 3.5 m of
  its OSM centreline, nearest road only, as `sn8_detect.road_visibility` measures them. A road with no valid cells of
  its own counts as not visible.
- **Reported per arm:**
  - roads visible among the 151 that could come back (ASSESS + CORRECT), split by decision and with the 55 on
    opaque-cloud tiles apart;
  - the 88 CANNOT ASSESS roads;
  - roads newly visible and newly lost against arm 1, with an exact McNemar test on roads and a tile-resampled
    interval of the difference in the share visible.
- **Flood labels:** visible counts are also split by flood label ("yes" against not).
  - Under cloud only "yes" is trusted, and the 55 roads on opaque-cloud tiles carry no flood label at all.
  - No flood call is scored here: that needs labels which cloud makes untrustworthy.

## Pictures
- **Tile:** picked by a fixed rule that uses no flood label and no detector output: the development tile with the
  most OSM road cells in the correctable part of the gate.
- **PNGs**, saved in `evidence/pilot_scripts/roadfinding/`:
  - the before image, the after image as it is, the two-date de-hazed image and the single-image de-hazed image, each
    with the gate outlined;
  - for each arm, the detected road cells against OSM on its own image (green found, red detected but not road, blue
    missed).

## Changes from the suggested design, and why
1. **The primary outcome is F1 rather than recall** (reason above).
2. **Fade-margin cells are kept out of both groups:** they are partly corrected, so they are neither test nor control.
3. **Not-road cells under the gate are sampled at 25%, and clear cells at 5%, with weights.** About 3.3 million
   labelled gate cells across four arms would take several GB of cache. The tile-resampled interval, not the cell
   count, sets the uncertainty.
4. **One valid mask (both dates) serves every arm,** so the cells are identical. The before arm therefore differs
   slightly from production, which masks the before image only.
5. **The cut-off stays at production's 0.75 in every arm** (exact reproduction). Because the probabilities of
   after-image detectors may sit differently, a threshold-free AUC and a per-arm cut-off are reported as checks
   (secondary outcomes 7 and 8).
6. **The clear control is also reported on the gated tiles only**, the closest match to the cloud cells.
