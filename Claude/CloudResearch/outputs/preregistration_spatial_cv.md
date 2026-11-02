# Test plan: spatially blocked cross-validation (written before any model is scored on the new folds)

Written 2026-10-26 18:40 EDT. No model has been fitted or scored on the new folds. Code: GeoAI-Roads `55c8fc2`, clean
working tree. Fold module: `evidence/pilot_scripts/spatial_cv/spatial_folds.py` (sha256 `6ab96c2966619323…`).
Fold checks: `spatial_cv/folds_numbers.json`, `fold_tables.csv`, `fold_map.png`, `spatial_folds.log`. Results and
deviations go in `evidence/14_spatial_cv.md`, not here.

Justin (2026-10-26): "can you do a cross validation so that you dont overfit".

## Status
**Exploratory, development data only (Louisiana-East train + val: 226 tiles, 1,037 touched roads). Nothing is
promoted from tile-fold numbers again.**
- Every arm below has tile-fold numbers already. The spatial-fold numbers will be new.
- Before writing this plan, only fold-building numbers were looked at: shared road ids, fold sizes, distances and a
  correlogram of the labels. No model was fitted.
- Every result is reported, whatever it shows.

## Why the old folds are not enough
- The old folds are `StratifiedGroupKFold(5, shuffle=True, random_state=662)` grouped by tile.
- A road id is an OSM way. It can cross a tile edge. Then a held-out road shares its id, and its flooded label, with a
  training road on the next tile.
- At seed 662, **608 of the 1,037 held-out roads (58.6%) share an id with a training road in the same fold**. The mean
  over 21 seeds is 58.5%. On production's 798, split over themselves, it is 484 (60.7%), with a mean of 56.9%.
- Under tile folds, 99% of held-out tiles touch a training tile.
- Neighbouring tiles flood together. The flooded labels of roads on different tiles, with different ids, correlate
  0.54 at 0-1 km, 0.38 at 1-2 km, 0.22 at 2-3 km and 0.16 at 3-4 km. The correlation first falls below 0.1 in the
  4-6 km band. This is the labels' dependence, not the models' errors. It is an upper bound on the dependence that
  matters.
- Method: Roberts et al. 2017, *Ecography* 40(8) 913-929. Use block cross-validation with blocks larger than the
  dependence range, optionally with a buffer.

## The folds (fixed; built and checked before this plan)
- **Projection.** Local equirectangular, centred on the mean dev tile centroid: x = R cos(lat0)(lon - lon0),
  y = R (lat - lat0), with R = 6,371,008.8 m. Centroids come from `sn8_data.georef` on each dev tile's pre image
  (TIFF tags only).
- **Tiles are not 550 m squares.** They are 544-578 m east-west by 626-666 m north-south. So each block is a square
  with the area of 3 x 3 median tiles: **side 1,751 m**. The grid's origin is the north-west corner of the dev extent.
  This gives **63 blocks**, 61 of them with roads. Blocks hold 1-10 dev tiles (median 3) and 0-94 roads (median 9).
- **Merge or purge: purge.** 114 of the 597 road ids cross a block edge. Merging every two blocks that share an id leaves 4
  blocks, and the largest holds 524 of the 1,037 roads (50.5%). That is over the 25% limit. So the grid blocks are kept,
  and **in each fold, training roads whose id occurs among that fold's held-out dev roads are dropped from training**.
  They are still scored when they are held out. At seed 662 this drops 648 training roads in all (100-165 per fold).
  The mean over the 21 seeds is 613.
- **Fold assignment.** `StratifiedGroupKFold(5, shuffle=True, random_state=s)` is run once over all 1,037 dev roads,
  with groups = block and y = flooded. Every subset (798, 891, the cloud groups) inherits that block-to-fold map, so
  subsets share folds. The 9 dev tiles without a touched road go to their block's fold. The 2 blocks with no road go to
  the fold with the fewest tiles. This matters for Track A cells only.
- **Buffer (sensitivity).** In each fold, every training road on a dev tile that touches a held-out tile is dropped.
  "Touches" means an 8-neighbour in the same region grid, or centroids within 600 m. The two regions are at least
  5.8 km apart, so only the 8-neighbour rule acts. At seed 662 this drops a further 814 training roads (mean 743).
- **Seeds.** 662 is primary, then 1-20. These are the same as in the factorial. The model seed stays 662.
- **What the checks show.**

  | At seed 662 (mean of 21 seeds) | tile folds | spatial folds | spatial, buffered |
  |---|---|---|---|
  | Held-out roads sharing an id with training | 58.6% (58.5%) | **0** (0) | 0 (0) |
  | Median distance to nearest training tile | 578 m | 881 m | 1,365 m (1,456 m) |
  | Minimum distance | 544 m | 544 m | 1,088 m |
  | Held-out tiles touching a training tile | 99% | 60% (58%) | 0% |

- **Fold sizes at seed 662.** Held-out roads per fold are 204, 205, 202, 222 and 204, with flooded shares from 0.446
  to 0.455. Across all 21 seeds the folds hold 201-223 roads.
  - On the 798, folds hold 150, 180, 148, 194 and 126 roads.
  - Training roads per fold (1,037) are 733, 681, 670, 689 and 727. Under tile folds they are 828-831. So **spatial
    training sets are about 15% smaller**.
- **The thin-cloud groups are clustered.** At seed 662, the 24 trusted flooded roads fall 0 / 4 / 3 / 1 / 16 across
  the folds. The 69 dry-labelled roads fall 22 / 4 / 25 / 17 / 1. Group results will lean on one fold.
- **Controls fixed now:**
  - **Size-matched tile folds** (`size_matched_tile_folds`). These are tile folds whose training roads are randomly
    cut to the size of the matching spatial fold.
    - Tile minus size-matched is what the smaller training sets cost.
    - Size-matched minus spatial is what the leakage and nearness were worth.
  - **Large blocks, 7 x 7 tiles** (`block_tiles=7`: side 4,085 m, past the ~4 km label range). This gives 20 blocks and
    the purge route. Folds hold 180-241 roads, with flooded shares from 0.33 to 0.53.

Use (from any script; CPU, about 5 s to load):
```python
sys.path.append(".../ProjectBranch/ClaudeFunctions"); sys.path.append(".../pilot_scripts/spatial_cv")
from spatial_folds import (SEEDS, spatial_folds, nested_spatial_folds, tile_folds, size_matched_tile_folds,
                           cell_folds, nested_cell_folds, fold_table, dev_roads, splitter)
folds = spatial_folds(roads, s)                 # (train, test) positions in `roads`; then fit on tr[keep[tr]]
```

## Agent B (CPU: classical + DINOv2, library tools only)
**General rules**
- Each arm keeps its logged model, features and gate. Only the folds change.
- In each fold, the gate's kept training rows are used: `tr[keep[tr]]`, after purging. The gate's kept held-out roads
  are scored.
- Fold schemes:
  - **S**: spatial, 21 seeds (primary);
  - **SB**: spatial with the buffer, seed 662 and the 21-seed mean;
  - **T**: tile folds made exactly as each arm was logged;
  - **TM**: size-matched tile folds, 21 seeds, for (a) and (b);
  - **L**: 7 x 7 blocks, seed 662 and the seed mean, for (a) and (b).
- **Reproduction check.** At s = 662, each arm under T must reproduce its logged calls. If one does not, the script
  stops.
- CPU only. Cached tables only: a cache miss stops the script. `production.json` must have the same sha256 before and
  after.

**Arms**
- **(a) Production on its 798 kept roads.**
  - T: `tile_folds(roads798)`, split over the 798 itself. It must reproduce the logged 394 / 47 / 89 / 268 (83.0%).
  - Also T-dev: `tile_folds(roads798, over="dev")`, the factorial's construction. It must give 390 / 51 / 91 / 266.
- **(b) The best combo so far on the 891 tile-rule roads.** This is production + DINOv2 cues + the change vector, with
  the 16 PCs fitted inside each training fold (`make_pipeline(ReduceColumns(DINO_VECTOR), make())`).
  - T: split over the 891. It must reproduce the logged 409 / 56 / 80 / 346.
  - Also T-dev.
- **(c) The 16-arm pipeline factorial** (gate x de-hazer x features). Use the arms, sets, metrics, main effects,
  interactions and optimal-combo rule of `evaluate_pipeline_factorial.py` and `preregistration_pipeline_factorial.md`.
  The only change is S folds over the 1,037.
  - T is the logged factorial. Read it from `pipeline_factorial_seed_calls.npz`; do not refit.
  - SB at seed 662.
- **(d) The four thin-cloud groups under S.** These are the 24 trusted flooded roads (found), the 69 dry-labelled
  roads (called flooded), the 175 control roads (right) and the 95-road clear-sky benchmark (found). Score them with
  the calls from (c), for every arm.
  - Report count, share and a 5,000-resample block interval at seed 662, and the seed mean.
  - Also report the per-fold counts, because the groups are clustered.
- **(e) Nested spatial CV: the honest accuracy of "pick the best combo".**
  - Use `nested_spatial_folds(roads1037, s)` at all 21 seeds; the inner seed is the outer seed.
  - In each outer fold, run an inner spatial CV on the outer-training rows only, for each of the 16 arms. Fit on the
    inner-training rows the arm's gate keeps, and call the inner held-out rows.
  - **Pick rule.** Take the highest pooled inner accuracy on the inner held-out roads kept by both gates. Any arm within
    0.005 of the top is a tie. Ties go to the arm with the fewest tools (the factorial's tool count). Equal tool counts
    go to the higher inner accuracy, then to factorial order.
  - Refit the picked arm on all outer-training rows (its gate). Call the outer held-out roads.
  - Report:
    - nested accuracy on the 757 shared roads and on the 798;
    - which arm was picked in each outer fold and seed;
    - nested minus the best single arm's S accuracy (the selection optimism);
    - nested against production under S (paired, same roads).
- **(f) Track A road finding** (classical + DINOv2 cells; `classical_models()[production_detector()]`).
  - Use the cells of `cell_table("train")` and `cell_table("val")`, under `cell_folds` at seed 662 and then the 21
    seeds.
  - Cut-off fixed at **0.75**. Then nested: `nested_cell_folds`, with the cut-off from `f1_cutoff` on inner
    out-of-fold probabilities of the outer-training cells only, at the real road share.
  - Train-split cells are a road-enriched sample; val-split cells are a uniform sample.
    - Primary: F1 on held-out val-split cells.
    - Secondary: F1 on all held-out cells, weighted to the real road share (`weighted_f1`, as `f1_cutoff` weights).
  - T: the same splitter grouped by tile over the cells, as `oof_probabilities` does.
  - The DINOv2 cell basis (32 PCs, label-free) was fitted on the 186 training tiles.
    - If its token cache allows a CPU refit, refit it in each outer-training fold.
    - Otherwise keep it, and log it as a limitation.
  - No McNemar on cells.

**Metrics, for every arm and scheme**
- TP, FN, FP, TN, accuracy, precision, recall, specificity, F1 and MCC.
- **95% intervals by resampling blocks for S, SB and L, and tiles for T and TM.** Use 2,000 resamples, seed 662.
- **Paired against production on the same roads, same scheme.** Report the accuracy difference with a 5,000-resample
  block interval, roads fixed and broken, and exact McNemar.
- **Over the 21 seeds.** Report the mean, SD, min and max, and the seeds above / equal to / below production.
- **Seed-averaged interval.** Average each road's correctness over the 21 seeds. Take the contrast road by road, then
  resample blocks (2,000, seed 662).
- **Optimism gap per arm.** This is T accuracy minus S accuracy on the same roads. Report it at seed 662 and as the
  seed mean with a seed-averaged block interval.
  - For (a) and (b), split it into T-dev minus TM (smaller training sets) and TM minus S (leakage and nearness).
- **Residual dependence check.** For production under S at seed 662, report the correlation of held-out errors by
  distance band, with the same bands as the label correlogram. This shows whether 1.75 km blocks pass Roberts' test.
  The primary stays 3 x 3 whatever this shows; L is reported beside it.

## Agent C (GPU, research only: DINOv3)
- timm `vit_large_patch16_dinov3.sat493m` is a research benchmark only. It never goes in the library: no module,
  import or commit. Scripts and caches stay in `evidence/pilot_scripts/dinov3/`, and nothing is written to
  `production.json`.
- **Folds.** Use the seed-662 S outer folds (`spatial_folds` for roads, `cell_folds` for cells).
  - Frozen arms: cues, vector PCs and heads are fitted inside each outer-training fold.
  - Fine-tuned arms (A-ft, A-head, B-head, B-ft, with phase 2's settings): one fine-tune per outer fold, on that
    fold's training blocks only.
  - Early stopping uses inner fold 1 of `nested_spatial_folds` / `nested_cell_folds` in place of phase 2's random 20%
    tile split. Track B cross-fitting uses that outer fold's inner folds.
  - Purged roads give no training target; their pixels may still appear as context.
- **Compare with classical + DINOv2** on the same folds and roads: Agent B's S calls at seed 662. Use exact McNemar
  and a block-resampled interval of the difference.
  - "Beats" means a higher score, an interval above 0 and p < 0.05. Anything less is reported as no detectable
    difference.
- **Order, if GPU time runs short:** Track B (B-head, then B-ft), then Track A. Anything not run is reported as not
  run.

## Decision rules (fixed now)
- **The promotion rule (`sn8_stages.confirm`) is applied only to S numbers.** The rule is gain > 0, a 95% interval
  above 0 and McNemar p < 0.05. Apply it at s = 662 with block-resampled intervals, against production on the same
  roads.
  - **A gain counts only if its seed-averaged S interval also excludes 0.**
- The factorial's optimal combo is re-chosen with S numbers. The nested number (e) is the estimate quoted for
  "the best combo".
- **Non-significant results are reported as what we will do next to improve, not as wins.** No p-value is shown on a
  slide unless it is significant. Methods whose intervals overlap are not ranked.
- No result is corrected for multiplicity. They are exploratory.
- **Data rules.**
  - Nothing reads the test tiles, the north negative set, Germany, Louisiana-West, the all-splits label folder or the
    HRC_WHU test images. Nothing passes `allow_held_out=True`.
  - Scripts assert `set(roads.split) <= {"train", "val"}`. `spatial_folds` refuses any non-dev tile.
  - Labels are the published labels, unmodified.
- **Anything changed after results are seen is logged as a deviation** in `evidence/14_spatial_cv.md`, with the time
  and the reason.
