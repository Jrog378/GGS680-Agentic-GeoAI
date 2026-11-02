# 15. The DINOv3 research benchmark under spatially blocked folds (Agent C)

Run 2026-10-26, 19:00 to BFT_END EDT. Justin: "can you do a cross validation so that you dont overfit".

- **Plan:** `outputs/preregistration_spatial_cv.md`, the "Agent C" section and the "Decision rules". It was written at
  18:40, before any model was scored on the new folds.
- **Companion:** Agent B ran the classical + DINOv2 arms on the same folds (`evidence/14_spatial_cv.md`).
- **Last night's benchmark:** `evidence/11_dinov3_baseline.md` (frozen phase 1, fine-tuned phase 2).

**DINOv3 is a research benchmark only.** Justin: "we will not use dinov3 in the library, it is only for research and
benchmarking our other models".
- timm `vit_large_patch16_dinov3.sat493m`, under Meta's DINOv3 License.
- All code is in `evidence/pilot_scripts/dinov3/spatialcv_*.py` (new files; last night's files are unchanged).
- Nothing in `ProjectBranch/ClaudeFunctions/` or GeoAI-Descriptions imports it. Nothing was committed.
- Nothing was written to `production.json`. Its sha256 (`c3295b20…`) was checked before and after every CPU stage.

**Development data only.**
- The 186 train and 40 val tiles of Louisiana-East and their 1,037 touched roads.
- Splits were taken by name with `split_tables()`, and the test and negative tables were dropped at once.
- Every script asserts `set(roads.split) <= {"train", "val"}`. Nothing else was opened, and `allow_held_out` was never
  passed.
- Exploratory: these are the same tiles the DINOv2 stages were chosen on.

## Bottom line
BOTTOM_LINE

## What was run
- **Reproduction first.** Under last night's tile folds, all 13 phase 1 Track B arms gave phase 1's calls on the 891
  roads, call for call. Production gave 394 / 47 / 89 / 268 on the 798 roads; the best combo gave 409 / 56 / 80 / 346
  on the 891.
- **Caches reused, none rebuilt or deleted:**
  - last night's DINOv3 road tokens, cell features and cell basis (`dinov3/.cache/`);
  - the frozen 20-block trunk (`~/Masters/models/finetuned/dinov3_sat493m/trunk20_c0d6dac062e8/`).
  - The trunk still reproduces `tokens3` (cosine 1.000000).
- **Phase 2's training settings, unchanged:**
  - the last 2 of 24 blocks trained on the cached frozen trunk;
  - one random window per tile per epoch, one optimiser step per tile;
  - AdamW, float32, no augmentation;
  - the same learning rates, epoch caps and patience.
- **Arms:**
  - **Track B (flood per road), frozen:** phase 1's 13 arms on the 891 tile-rule roads, and its 7 production-type arms
    on the 798 roads production's cloud rule assesses.
  - **Track B, trained cues:** phase 2's arms with the B-head cues (a flood head on frozen DINOv3 tokens) and the B-ft
    cues (last 2 blocks + head fine-tuned), on both road sets.
  - **Track A (finding roads), frozen:** production's cell random forest with classical + DINOv2 (production),
    classical + DINOv3, DINOv3 only and DINOv2 only features.
  - **Track A, trained:** A-head (a linear head on frozen DINOv3 tokens) and A-ft (last 2 blocks + head). A-ft was cut
    from the 26 Oct GPU budget and run later, 29-30 Oct (see "A-ft, run 29-30 October").
- **The comparison with classical + DINOv2** is refitted here on the same folds and roads: production and the best
  combo (production + DINOv2 cues + change vector). Agent B's calls were then checked against ours (see
  "Cross-check with Agent B").

## Folds
- **Outer folds:** the seed-662 spatial folds of `spatial_cv/spatial_folds.py`, imported and not edited.
  - 63 square blocks of 1,751 m (the area of 3 x 3 tiles) are split into 5 folds.
  - **Purge:** in each fold, training roads whose road id occurs among the held-out roads are dropped as targets.
  - So no held-out road shares a road id with a training road. Under last night's tile folds, 608 of the 1,037 did.
  - Held-out roads per fold on the 798: 150, 180, 148, 194 and 126. Spatial training sets are about 15% smaller than
    tile-fold ones.
- **Frozen arms:** the random forest, and the change-vector PCs inside its pipeline, are fitted in each outer-training
  fold.
- **Trained arms:**
  - One model (or set of models) per outer fold, on that fold's training blocks only.
  - Early stopping, and A-head's cut-off, use **inner fold 1** of `nested_spatial_folds` / `nested_cell_folds`. The
    model is fitted on the other 4 inner folds' tiles (125-160 tiles).
  - **Track B cross-fitting:** each outer fold has 5 inner models. Inner model j is fitted outside inner fold j and
    gives inner fold j's cues. The held-out roads take the mean of the 5 inner models' probability grids, as last
    night's validation roads did.
  - **Targets:** the published road lines and the published `flooded` attribute only. Track B targets are the roads
    production's cloud rule assesses, among each model's purged training roads. Purged roads give no target; their
    pixels can still be context.
- **Scoring:**
  - Held-out calls are pooled over the 5 outer folds.
  - Accuracy and F1 intervals resample whole blocks (2,000 resamples, seed 662). Paired differences use 5,000 block
    resamples and exact McNemar.
  - Cells get no McNemar test: cells within a block are not independent.
- **"Beats"** means a higher score, a block-resampled interval above 0 and McNemar p < 0.05. For cells it means a higher
  F1 with the interval above 0. "Worse" is the mirror image. Anything else is "no detectable difference".

## Track B: flood per road
The model is production's tuned random forest. "Base" is production without DINO (the 93 classical and texture
columns). Production is base + DINOv2 cues. The best combo is production + the DINOv2 change vector (16 PCs fitted
inside each fold). "Vector" is the pooled after - before token, reduced to 16 PCs inside each fold.

### Production loses 4-5 points under spatial folds; the DINOv3 change vectors lose much less
Old tile folds (T) minus spatial folds (S), on the same roads. Blocks are resampled; McNemar is exact.

| arm | 798 roads: T -> S | T - S (95% CI) | 891 roads: T -> S | T - S (95% CI) |
|---|---|---|---|---|
| base (no DINO) | 81.3% -> 78.7% | +2.6 (+0.6 to +5.4), p = 0.010 | 83.1% -> 78.2% | +4.8 (+2.3 to +7.9), p < 0.0001 |
| **production** | 83.0% -> **79.2%** | **+3.8 (+2.0 to +6.2), p = 0.0004** | 84.3% -> **79.3%** | **+4.9 (+2.6 to +8.0), p < 0.0001** |
| best combo (production + DINOv2 vector) | 83.1% -> 80.1% | +3.0 (+0.8 to +5.8), p = 0.005 | 84.7% -> 81.6% | +3.1 (+1.1 to +5.8), p = 0.0003 |
| base + DINOv3 cues | 82.7% -> 79.8% | +2.9 (+0.8 to +5.5), p = 0.005 | 83.4% -> 79.8% | +3.6 (+1.8 to +6.0), p < 0.0001 |
| base + DINOv3 cues + vector | 83.0% -> 81.5% | +1.5 (-0.1 to +3.3), p = 0.13 | 83.7% -> 82.5% | +1.2 (-0.6 to +3.9), p = 0.18 |
| base + DINOv2 + DINOv3 cues + vectors | 83.6% -> 83.0% | +0.6 (-1.7 to +3.1), p = 0.59 | 84.8% -> 83.2% | +1.7 (-0.4 to +4.4), p = 0.063 |
| DINOv3 cues + vector | - | - | 84.3% -> 83.0% | +1.2 (-0.4 to +3.3), p = 0.18 |
| DINOv2 + DINOv3 cues + vectors | - | - | 85.9% -> 85.1% | +0.8 (-0.7 to +2.6), p = 0.37 |

- **Evidence:** production's tile-fold accuracy was 3.8 points too high on the 798 roads and 4.9 on the 891.
- **Evidence (Agent B's control):** Agent B's size-matched tile folds give production 82.96% at seed 662, the same as
  plain tile folds (82.96%). So the smaller spatial training sets cost nothing at that seed. The 3.8 points are what
  the shared road ids and neighbouring tiles were worth.
- **Inference:** the classical cues profit most from that leak. The frozen DINOv3 change vectors carry information that
  transfers to new blocks.

### Frozen DINOv3 arms against classical + DINOv2 (spatial folds, seed 662)
**798 roads (production's cloud rule)**
| arm | TP | FN | FP | TN | accuracy (95% CI) | vs production: points (95% CI), fixed / broken, p | verdict |
|---|---|---|---|---|---|---|---|
| base (no DINO) | 373 | 68 | 102 | 255 | 78.7% (73.1-83.8) | -0.5 (-2.0 to +1.1), 18 / 22, p = 0.64 | no detectable difference |
| **production** | 378 | 63 | 103 | 254 | **79.2%** (73.3-84.5) | - | - |
| best combo | 388 | 53 | 106 | 251 | 80.1% (74.7-84.9) | +0.9 (-0.6 to +2.8), 24 / 17, p = 0.35 | no detectable difference |
| base + DINOv3 cues | 382 | 59 | 102 | 255 | 79.8% (74.5-84.9) | +0.6 (-0.9 to +2.5), 22 / 17, p = 0.52 | no detectable difference |
| base + DINOv3 cues + vector | 394 | 47 | 101 | 256 | 81.5% (76.0-86.8) | +2.3 (-0.4 to +5.5), 43 / 25, p = 0.038 | no detectable difference |
| base + DINOv2 + DINOv3 cues | 384 | 57 | 99 | 258 | 80.5% (75.4-85.5) | +1.2 (-0.4 to +3.4), 28 / 18, p = 0.18 | no detectable difference |
| **base + DINOv2 + DINOv3 cues + vectors** | 404 | 37 | 99 | 258 | **83.0%** (77.8-87.6) | **+3.8 (+1.2 to +6.7), 51 / 21, p = 0.0005** | **beats** |

Against the best combo on the same roads: base + DINOv3 cues + vector +1.4 (-0.7 to +3.7), p = 0.18, no detectable
difference. Base + both backbones + vectors **+2.9 (+1.1 to +4.8), 36 / 13, p = 0.0014: beats**.

**891 roads (tile rule)**
| arm | accuracy (95% CI) | vs production: points (95% CI), fixed / broken, p | verdict | vs best combo | verdict |
|---|---|---|---|---|---|
| **production** | **79.3%** (73.5-84.6) | - | - | - | - |
| best combo | 81.6% (76.6-85.9) | +2.2 (+0.5 to +4.2), 42 / 22, p = 0.017 | beats | - | - |
| base + DINOv3 cues | 79.8% (74.4-84.8) | +0.4 (-0.9 to +2.1), 21 / 17, p = 0.63 | no detectable difference | -1.8 (-3.4 to -0.1), p = 0.040 | worse |
| base + DINOv3 cues + vector | 82.5% (77.0-87.3) | **+3.1 (+1.0 to +5.5), 50 / 22, p = 0.0013** | **beats** | +0.9 (-1.2 to +3.0), p = 0.36 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | 83.2% (78.1-87.6) | **+3.8 (+2.0 to +5.9), 55 / 21, p = 0.0001** | **beats** | +1.6 (+0.1 to +3.1), p = 0.049 | beats |
| DINOv3 cues + vector (no base) | 83.0% (77.7-88.2) | +3.7 (-0.1 to +7.8), 89 / 56, p = 0.008 | no detectable difference | +1.5 (-2.1 to +5.2), p = 0.28 | no detectable difference |
| **DINOv2 + DINOv3 cues + vectors (no base)** | **85.1%** (80.3-89.5) | **+5.7 (+2.3 to +9.9), 95 / 44, p < 0.0001** | **beats** | **+3.5 (+0.5 to +7.0), p = 0.003** | **beats** |
| DINOv3 cues (no base) | 71.5% (65.0-78.0) | -7.9 (-13.3 to -2.0), p < 0.0001 | worse | -10.1 | worse |

DINOv3 against DINOv2, like for like:
- cues: +0.2 (-4.7 to +5.8), p = 0.95, no detectable difference;
- cues + vector: +2.6 (-1.6 to +6.9), p = 0.052, no detectable difference;
- in the base: +0.4 (-0.9 to +2.1), p = 0.63, no detectable difference.

Both backbones together beat either alone (cues: +5.3 over DINOv2 and +5.1 over DINOv3; cues + vectors: +4.6 and
+2.0; all p <= 0.011).

**Post hoc, not in the plan: do these hold over the 21 fold seeds?** Written at about 19:15, after the seed-662
results above were seen (`spatialcv_posthoc_seeds.py`). Same arms, roads, purge and model seed. The interval is the
plan's seed-averaged one: each road's correctness averaged over the 21 seeds, the contrast taken road by road, blocks
resampled.

| arm | 798: seeds above / equal / below production | 798: seed-averaged difference (95% CI) | 891: seeds above / equal / below | 891: seed-averaged difference (95% CI) |
|---|---|---|---|---|
| best combo | 20 / 1 / 0 | +1.1 (+0.1 to +2.0) | 21 / 0 / 0 | +1.6 (+0.4 to +2.8) |
| base + DINOv3 cues | 18 / 0 / 3 | +0.6 (-0.3 to +1.7) | 18 / 0 / 3 | +0.9 (+0.0 to +1.9) |
| base + DINOv3 cues + vector | 20 / 0 / 1 | **+1.9 (+0.3 to +3.7)** | 21 / 0 / 0 | **+2.4 (+1.0 to +4.0)** |
| base + DINOv2 + DINOv3 cues + vectors | 21 / 0 / 0 | **+2.4 (+0.4 to +4.8)** | 21 / 0 / 0 | **+3.2 (+1.5 to +5.2)** |
| DINOv3 cues + vector (no base) | - | - | 21 / 0 / 0 | +4.2 (+1.4 to +7.4) |
| DINOv2 + DINOv3 cues + vectors (no base) | - | - | 21 / 0 / 0 | **+5.2 (+2.3 to +8.7)** |

Production's mean over the 21 seeds is 78.6% on the 798 (SD 0.8) and 79.1% on the 891 (SD 0.6). The seed-662 gains
above are a little larger than the seed means, but every vector arm stays above production at nearly every seed.

### Trained cues: B-head and B-ft (spatial folds, seed 662)
- **B-head**, the flood head on frozen DINOv3 tokens, chose 1, 1, 1, 2 and 1 epochs on inner fold 1. Last night it
  chose 1.
- **B-ft**, the last 2 blocks + head, chose BFT_EPOCHS. Last night it chose 3.

BFT_TABLES

### Per outer fold (798 roads)
| arm | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 |
|---|---|---|---|---|---|
| production | 0.887 | 0.800 | 0.770 | 0.737 | 0.778 |
| base + DINOv3 cues + vector | 0.913 | 0.844 | 0.777 | 0.737 | 0.817 |
| base + DINOv2 + DINOv3 cues + vectors | 0.933 | 0.844 | 0.784 | 0.773 | 0.825 |
| base + DINOv3 head cues | 0.920 | 0.872 | 0.777 | 0.763 | 0.817 |
BFT_FOLDS

The folds differ more from each other (0.74 to 0.89 for production) than the arms differ within a fold. The DINOv3 arms
are at or above production in every fold.

## Track A: finding roads (cells)
**Set-up:**
- **Cells:** `cell_table("train")` (205,581, a road-enriched sample) and `cell_table("val")` (338,885, a uniform 10%
  sample) under `cell_folds` at seed 662.
- **Fitting:** each frozen forest (production's detector, 300 trees, seed 662) is fitted on the road-enriched
  training-split cells of the outer-training tiles (157,000-170,000 cells per fold). That is production's own training
  sample. It is then called on every held-out cell of both splits. This is a logged choice (see "Deviations").
- **Cut-offs:** frozen arms keep their logged cut-offs: production 0.75 (the plan's fixed cut-off), classical + DINOv3
  0.71, DINOv3 only 0.69, DINOv2 only 0.76. A-head chooses its cut-off on inner fold 1 of each outer fold: 0.19, 0.32,
  0.31, 0.30 and 0.41. A-ft does the same: 0.35, 0.46, 0.43, 0.46 and 0.48 (last night: 0.46).
- **Primary score:** F1 on the 338,885 held-out validation-split cells (7,205 road).
- **Secondary score:** F1 on all 544,466 held-out cells, with training-split not-road cells weighted to the real road
  share (0.0221) as `f1_cutoff` weights them.

**Held-out validation-split cells (primary)**
| arm (cut-off) | precision | recall | F1 (95% CI) | F1 vs production (95% CI) | verdict |
|---|---|---|---|---|---|
| classical + DINOv2 (0.75), **production** | 0.701 | 0.718 | **0.709** (0.639-0.776) | - | - |
| classical + DINOv3 (0.71), frozen | 0.741 | 0.723 | **0.732** (0.667-0.800) | **+0.023 (+0.002 to +0.047)** | beats |
| DINOv3 only (0.69), frozen | 0.713 | 0.731 | 0.722 (0.654-0.792) | +0.013 (-0.015 to +0.044) | no detectable difference |
| DINOv2 only (0.76), frozen | 0.660 | 0.702 | 0.680 (0.609-0.742) | -0.029 (-0.050 to -0.013) | worse |
| DINOv3 linear head on frozen tokens (A-head; inner fold 1) | 0.666 | 0.651 | 0.658 (0.582-0.732) | -0.051 (-0.087 to -0.020) | worse |
| **DINOv3 fine-tuned, last 2 blocks + head (A-ft; inner fold 1)** | 0.738 | 0.747 | **0.743** (0.681-0.807) | **+0.033 (+0.008 to +0.065)** | **beats** |

**All held-out cells, weighted to the real road share (secondary)**
| arm | precision | recall | F1 (95% CI) | F1 vs production (95% CI) | verdict |
|---|---|---|---|---|---|
| classical + DINOv2, **production** | 0.688 | 0.676 | **0.682** (0.648-0.716) | - | - |
| classical + DINOv3, frozen | 0.741 | 0.695 | **0.717** (0.683-0.749) | **+0.035 (+0.021 to +0.051)** | beats |
| DINOv3 only, frozen | 0.716 | 0.688 | 0.702 (0.671-0.733) | +0.020 (+0.001 to +0.040) | beats |
| DINOv2 only, frozen | 0.664 | 0.646 | 0.655 (0.623-0.687) | -0.027 (-0.038 to -0.017) | worse |
| A-head | 0.683 | 0.607 | 0.643 (0.605-0.678) | -0.039 (-0.062 to -0.017) | worse |
| **A-ft** | 0.761 | 0.720 | **0.740** (0.704-0.775) | **+0.058 (+0.039 to +0.079)** | **beats** |

**Backbone against backbone, same cells:**
- DINOv3 only against DINOv2 only: **+0.042 (+0.010 to +0.082)** on validation-split cells; +0.047 (+0.028 to +0.067)
  on all cells. Beats on both.
- A-head against DINOv3 only (the random forest on 32 PCs of the same tokens): -0.064 (-0.098 to -0.034). Worse.
- A-ft against A-head: **+0.084 (+0.055 to +0.118)** on validation-split cells; +0.097 (+0.080 to +0.115) on all
  cells. Beats on both.
- A-ft against classical + DINOv3 (the best frozen arm): +0.010 (-0.021 to +0.038) on validation-split cells, no
  detectable difference; +0.023 (+0.005 to +0.039) on all cells, beats.
- A-ft against DINOv3 only: +0.020 (-0.012 to +0.052) on validation-split cells, no detectable difference; +0.038
  (+0.020 to +0.055) on all cells, beats.
- A-ft against DINOv2 only: +0.062 (+0.036 to +0.097) and +0.085 (+0.066 to +0.106). Beats on both.

**Per outer fold** (validation-split cells; fold 1 holds the fewest road cells):
- production 0.558 / 0.761 / 0.779 / 0.691 / 0.697;
- classical + DINOv3 0.590 / 0.816 / 0.775 / 0.708 / 0.709;
- A-ft 0.643 / 0.773 / 0.822 / 0.704 / 0.725 (full table under "A-ft, run 29-30 October").

Classical + DINOv3 is above production in 4 of the 5 folds on validation-split cells; the exception (fold 3) is 0.004
lower. On all cells (weighted) it is above production in all 5 folds: 0.708 / 0.726 / 0.686 / 0.706 / 0.758 against
0.668 / 0.695 / 0.669 / 0.659 / 0.711.

**Reading (inference):**
- Track A hardly moves between last night's split and the spatial folds. Production goes from 0.713 to 0.709.
- That fits how leakage works here. A cell carries no road id, and a tile's cells are its own pixels; neighbouring
  tiles add little that the classical cues and frozen tokens can copy.
- The DINOv3 cell features still beat DINOv2's under spatial folds, by a similar margin to last night.

### A-ft, run 29-30 October
A-ft is DINOv3 with its last 2 of 24 blocks and a cell head fine-tuned (phase 2's settings: 20-epoch cap, patience 4,
learning rates 2e-5 blocks / 1e-3 head). It was scored exactly like A-head, by the same unchanged report code
(`spatialcv_report.py`, run through `spatialcv_report_aft.py`). Each outer fold has one fine-tune on its training blocks.
Early stopping and the cut-off come from inner fold 1, and the held-out cells are pooled over the 5 outer folds. The
intervals come from resampling blocks (2,000, seed 662). As the plan says, cells get no McNemar test, so there is no
p-value here. "Beats" means a higher F1 with the block interval of the difference above 0.

**Result (evidence, seed 662, held-out validation-split cells, primary):**
- A-ft F1 **0.743** (0.681-0.807); production 0.709 (0.639-0.776).
- **A-ft against production: +0.033 (+0.008 to +0.065), beats.**
- **A-ft against A-head: +0.084 (+0.055 to +0.118), beats.**
- Secondary (all held-out cells, weighted to the real road share): A-ft 0.740 (0.704-0.775). Against production
  +0.058 (+0.039 to +0.079) and against A-head +0.097 (+0.080 to +0.115). Beats on both.
- A-ft has higher precision (0.738 against 0.701) and higher recall (0.747 against 0.718) than production on the primary
  cells.

**Does last night's +0.067 hold under spatial folds?** The direction holds, but the size does not.
- Last night A-ft beat production by +0.067 (+0.023 to +0.109): A-ft 0.780 against 0.713, on the 40 validation tiles.
- Under spatial folds the gain is +0.033 (+0.008 to +0.065), about half. Last night's +0.067 lies just above the new
  interval.
- The drop is mostly A-ft's own: A-ft fell from 0.780 to 0.743 (-0.037), while production fell from 0.713 to 0.709.
- Inference: the fine-tuned model profited from nearness to its training tiles more than production's frozen forest
  did. The comparison is not like for like, though. Last night's numbers came from one model fitted on 186 tiles and
  scored on 40; here there are five models, each fitted on 125-160 tiles. So part of the drop may come from the
  smaller training sets. A size-matched control for A-ft was not run.
- Against the best frozen arm, classical + DINOv3, A-ft shows no detectable difference on the primary cells (+0.010,
  -0.021 to +0.038). Last night it was +0.034. It beats classical + DINOv3 only on the secondary scope (+0.023, +0.005
  to +0.039). What would firm this up: the primary cells come from the 40 validation tiles only, so their block
  interval is wide. Repeating A-ft at more fold seeds would give the plan's seed-averaged interval, at about 3 h of
  GPU per seed at this run's pace.
- **Plan rule:** a gain counts only if its seed-averaged S interval also excludes 0. A-ft was run at seed 662 only, so
  its gain over production is a seed-662 result. It is not confirmed under that rule. DINOv3 is research-only, so it
  is not promoted in any case.

**Per outer fold** (F1; fold k = `A-ft_outer{k-1}`; epochs and cut-offs chosen on inner fold 1)
| outer fold | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| held-out tiles | 45 | 58 | 48 | 35 | 40 |
| A-ft best epoch (of epochs run) | 18 (20) | 13 (17) | 19 (20) | 8 (12) | 9 (13) |
| A-ft cut-off | 0.35 | 0.46 | 0.43 | 0.46 | 0.48 |
| A-ft inner fold 1 F1 | 0.825 | 0.773 | 0.810 | 0.741 | 0.721 |
| **validation-split cells:** production | 0.558 | 0.761 | 0.779 | 0.691 | 0.697 |
| A-head | 0.543 | 0.739 | 0.743 | 0.642 | 0.574 |
| A-ft | **0.643** | **0.773** | **0.822** | **0.704** | **0.725** |
| A-ft minus production | +0.085 | +0.012 | +0.043 | +0.013 | +0.028 |
| A-ft minus A-head | +0.100 | +0.035 | +0.079 | +0.062 | +0.151 |
| **all held-out cells (weighted):** production | 0.668 | 0.695 | 0.669 | 0.659 | 0.711 |
| A-head | 0.643 | 0.649 | 0.645 | 0.609 | 0.662 |
| A-ft | **0.772** | **0.722** | **0.760** | **0.675** | **0.765** |
| A-ft minus production | +0.104 | +0.027 | +0.091 | +0.016 | +0.054 |

- A-ft is above production and above A-head in all 5 outer folds, on both scopes.
- Its margin over production varies from +0.012 (fold 2) to +0.085 (fold 1) on the primary cells.
- Inner fold 1 F1 (0.72-0.83) is higher than the held-out outer-fold F1 (0.64-0.82). Inner fold 1 also chose the
  cut-off, so its F1 is optimistic and is not a result.

**Pictures, paired with the numbers above** (`evidence/pilot_scripts/dinov3/`; imagery: Maxar via SpaceNet 8):
- `spatialcv_trackA_f1.png` (updated 30 Oct): the bottom row is A-ft. Last night it scored 0.780 (blue); under spatial
  folds it scores 0.743 (orange) on the primary cells and 0.740 on all cells. Both orange dots are right of the grey
  production line, and A-head's interval lies further left. The 26 Oct version, without A-ft, is
  `spatialcv_trackA_f1_before_aft.png`.
- `spatialcv_per_fold.png` (updated): the right panel shows A-ft (yellow diamonds) above production (blue) and A-head
  (green) in every fold. Its dip in fold 4 (0.675) is where production is also lowest.
- `spatialcv_cells_0_14_7.png` (new): the Track A picture tile, held out in outer fold 5. Each cell is coloured green
  (found), red (not road) or blue (missed). A-head finds 2,574 road cells, calls 695 not-road cells road and misses
  3,077 (precision 0.79, recall 0.46). A-ft finds 3,239, with 258 not road and 2,412 missed (precision 0.93, recall
  0.57). A-head's false roads sit along the main road's verges; A-ft removes most of them. Both still miss parts of
  the narrow side roads.

GAINS

## Pictures (`evidence/pilot_scripts/dinov3/`; imagery: Maxar via SpaceNet 8)
PICTURES

## Cross-check with Agent B
Agent B's files in `spatial_cv/` were read, never edited (`spatial_cv_calls.csv`, `spatial_cv_trackA_probs.npz`).
- **Track B matches call for call.**
  - Production on the 798 roads: 798 of 798 calls equal under spatial folds (79.2%) and 798 of 798 under tile folds.
  - The best combo on the 891 roads: 891 of 891 equal under both.
  - So every Track B comparison here is against exactly Agent B's seed-662 S calls.
- **Track A does not match, by construction.**
  - Agent B fits production's forest on every outer-training cell, pooling the road-enriched training-split sample
    with the uniform validation-split sample (442,515 cells in fold 1). We fit on the road-enriched training-split cells
    only (165,024 in fold 1).
  - 535,838 of the 544,466 cell calls agree.
  - Pooling drops the training road share from 0.25 to about 0.11, so the fixed 0.75 cut-off calls fewer roads.
    Agent B's production scores F1 0.681 (precision 0.790, recall 0.598) on the held-out validation-split cells; ours
    scores 0.709.
  - Against Agent B's production on the same cells:
    - classical + DINOv3 +0.051 (+0.028 to +0.076), beats;
    - DINOv3 only +0.042 (+0.007 to +0.076), beats;
    - DINOv2 only -0.001 (-0.042 to +0.038), no detectable difference;
    - A-head -0.022 (-0.065 to +0.019), no detectable difference;
    - A-ft +0.062 (+0.027 to +0.098), beats (added 30 Oct).
  - The like-for-like comparison is the one in the Track A tables: every forest is fitted on the same sample.

## Deviations and implementation choices (time, reason)
1. **Track A forests fit on the road-enriched training-split cells only** (19:00, before any Track A score was seen).
   - The Agent C plan does not say which cells to fit on. Plan (f) for Agent B pools both cell tables, and Agent B did.
   - Reason: production's detector and all four fixed cut-offs (0.75, 0.71, 0.69, 0.76) were made at the enriched
     sample's road share (0.25). Pooling in the uniform validation-split sample drops that share to about 0.11 and
     shifts every forest's probabilities, so a fixed cut-off would no longer mean the same thing. It also needs 2.6
     times the fit rows on a CPU we shared.
   - Effect: see "Cross-check with Agent B".
2. **Frozen Track A arms keep last night's cut-offs.** These were chosen on out-of-fold training cells under tile folds,
   so some of those cells are now held out. This affects all four frozen arms alike; production's 0.75 is the plan's
   fixed cut-off. Nested cut-offs for the DINOv3 arms were not run.
3. **Cell bases not refitted.** The 32-PC cell bases of both backbones (label-free) stay as fitted last night on the
   186 training tiles. The DINOv2 token cache does not allow a CPU refit (Agent B's limitation), and the DINOv3 basis
   was kept the same way for symmetry.
4. **Checkpoints in float16, some skipped.**
   - Trained parameters only, in float16, to spare a disk that fell to 3.4 GB free during the run (swap grew to about
     10 GB).
   - The script skips a checkpoint when less than 6 GB is free. B-ft outer fold 2's early-stopping model and its inner
     model 1 were not saved. Results are unaffected: every fold's cues were written to `spatialcv_folds/`.
5. **A parallel GPU attempt, stopped** (20:12-20:28).
   - After B-ft's first inner fold chose 6 epochs, Track A was started in a second GPU process.
   - Both then ran at about half speed (a B-ft epoch went from 118 s to 215 s), so it gained nothing. It was stopped;
     nothing of it was kept.
   - The CPU forests were paused for the same 18 minutes (20:11-20:29) and resumed fold by fold.
6. **A-head from cached frozen tokens** (`spatialcv_ahead_cached.py`, 20:35).
   - A-head's input tokens never change: Top(4) is frozen, in eval mode. So they were computed once per tile and cached
     in the scratchpad. Then `dinov3_finetune.train_epochs("A", n_frozen=4)` was run line for line on them, with the
     same seeds, window draws, optimiser, clipping, patience and cut-off rule.
   - Checks:
     - the cached tokens give the same probabilities as the on-the-fly Top(4) (maximum difference 0 on two tiles);
     - epochs 1-2 of outer fold 1 gave the stopped on-the-fly run's losses to 4 decimals (0.3227 / 0.1649 and
       0.1225 / 0.1034).
   - The 5.2 GB scratch cache was then deleted for disk space. It was a temporary file of this run, not one of the
     existing caches.
7. **The Track B process was stopped right after B-ft's last fold**, before its own Track A stages. Its time estimate
   for A-ft would have been taken from the cached A-head's 18 s epochs and could have started A-ft against the budget
   rule. Its last step, the frozen change maps of the picture tile (label-free), was run separately.
8. **Post-hoc 21-seed check** of the frozen Track B arms (written about 19:15, after the seed-662 results). This is not
   in the plan, and it is labelled post hoc wherever it is quoted.
9. **Warnings.** A scikit-learn `UserWarning` (configuration not propagated to joblib workers) appears 65,646 times in
   `spatialcv_posthoc_seeds.log`. It was not filtered. No scikit-learn configuration is set, so it changes nothing.
10. **Early stopping on inner fold 1 chose more B-ft epochs than phase 2:** BFT_EPOCHS against 3. This follows from the
    plan (inner fold 1 replaces the random 20% split), not from a change of settings. The inner-fold losses are noisy:
    in outer fold 1 they went 0.83, 0.93, 0.81, 0.94, 0.83, 0.69, 1.07, 1.10 and 1.55 over epochs 1-9.
11. **A-ft run after the 26 Oct results were seen** (29 Oct 21:46 to 30 Oct 10:38; `spatialcv_gpu_aft.log`).
    - It was cut on 26 Oct for GPU time (see "Not run"). It was then run later with `spatialcv_gpu.py`, using the
      plan's procedure and phase 2's settings unchanged. The only change to that script on 29 Oct (21:45, kept as
      `spatialcv_gpu_before_keyfix.py`) is one line in the time projection: it reads A-head's cached epoch time
      under its other key name. Training and scoring are not affected.
    - Its scores were first seen on 30 Oct, after all the other arms' results. No setting was chosen after seeing them.
12. **A-ft crashed and was resumed.** The Mac had a kernel panic at 22:55 on 29 Oct, during outer fold 2's epoch 8.
    - Outer fold 1 had finished at 22:32 and was saved to `spatialcv_folds/A-ft_outer0.*` and
      `trackA_A-ft_outer0.pt`. **It was kept.**
    - The run resumed at 08:13 on 30 Oct. The script skips any finished fold, so it restarted outer fold 2 from epoch 1
      and then ran folds 3-5. Nothing of the crashed partial fold was kept.
    - The outer folds are independent: each is a fresh fine-tune from the same frozen trunk on its own training blocks,
      with its own seeds. So keeping fold 1 does not change folds 2-5.
    - Check: the restarted fold 2 gave the crashed attempt's losses to 4 decimals for epochs 1-3 (train / eval 0.2036 /
      0.0483, 0.0554 / 0.0373, 0.0388 / 0.0323).
    - The machine was shared with the Ida test chain on 30 Oct (from about 09:04). Epochs took 56-152 s, mostly
      110-120 s, against about 100 s on 29 Oct and 68 s in phase 2. This affects time, not results. Fold times: 2,601 / 1,756 / 3,164 / 1,775 / 1,886 s (3.1 h),
      against the 2.4 h projected on 26 Oct.
13. **The report was rerun only for Track A pictures** (`spatialcv_report_aft.py`, 30 Oct). It runs the unchanged
    `spatialcv_report.py` source with two text edits: the Track A figure's footnote, and a figure list that redraws
    only the pictures showing A-ft (`spatialcv_trackA_f1.png`, `spatialcv_per_fold.png`, new
    `spatialcv_cells_0_14_7.png`). Numbers and tables were rewritten in full.
    - Check: every Track B entry of `spatialcv_numbers.json` equals the 26 Oct file. Every 26 Oct Track A row is still
      present, unchanged. The Agent B production cross-check still gives 535,838 equal cell calls.
    - The 26 Oct outputs were copied to `*_before_aft.*` first.

## Not run
- **A-ft (Track A, last 2 blocks + head) was not run on 26 Oct. It was run later, 29-30 Oct** (see "A-ft, run 29-30
  October" and deviations 11-12).
  - On 26 Oct, the projection after the first fine-tune (B-ft outer fold 1: 5,776 s) was **11.3 h of GPU in all**,
    against a budget of about 7 h. B-ft alone ran to about BFT_HOURS h.
  - The plan's order is B-head, B-ft, A-head, A-ft. So A-ft, last, was cut at 20:44, and no epochs were cut.
  - Last night's +0.067 F1 for A-ft over production has now been tested under spatial folds. It shrinks to **+0.033
    (+0.008 to +0.065)**: still a gain, about half the size.
  - `spatialcv_folds/not_run.json` still records the 26 Oct cut. It was left as written.
- **Nested cut-offs** for the frozen DINOv3 Track A arms: 25 inner forest fits per arm on a shared CPU.
- **Fold seeds other than 662 for the trained arms.** The plan gives Agent C seed 662. The frozen Track B arms got a
  post-hoc 21-seed check.
- **Buffered (SB), size-matched (TM) and 7 x 7-block (L) schemes:** Agent B's part of the plan, not Agent C's.

## What we do next
NEXT

## Run time
RUNTIME

## Files
All under `evidence/pilot_scripts/dinov3/` unless noted. Research only; nothing is in any repo.
- **Plan:** `outputs/preregistration_spatial_cv.md` (Agent C, Decision rules).
- **Code:**
  - `spatialcv_common.py`: folds, data, block-resampled scores;
  - `spatialcv_gpu.py`: B-head, B-ft (and the A arms' code path);
  - `spatialcv_ahead_cached.py`: A-head on cached frozen tokens;
  - `spatialcv_report_aft.py`: the report rerun with A-ft (30 Oct);
  - `spatialcv_cpu.py`: the random-forest arms and the reproduction checks;
  - `spatialcv_report.py`: tables, numbers, pictures;
  - `spatialcv_posthoc_seeds.py`: the post-hoc 21-seed check.
- **Numbers:**
  - `spatialcv_numbers.json`: every table, per-fold results, GPU times, the Agent B checks, code hashes;
  - `spatialcv_tables.md`: generated tables;
  - `spatialcv_posthoc_seeds.json`.
- **Per-road calls:**
  - `spatialcv_calls_B-frozen_798.csv` / `_891.csv`: S and T calls of every frozen arm;
  - `spatialcv_calls_B-trained_798.csv` / `_891.csv`: S calls of the trained-cue arms;
  - `spatialcv_heldout_cues.csv`: each road's B-head and B-ft cues from its own held-out fold.
  - Each file carries tile, road id, block, outer fold and the published flooded label.
- **Per-cell calls:** `spatialcv_calls_cells.npz` (tile, row, col, split, label, outer fold, block, then each arm's
  call).
- **Per fold, written as each finished:** `spatialcv_folds/`:
  - `B-head_outer*`, `B-ft_outer*`, `A-head_outer*`, `A-ft_outer*` (`.npz` cues or probabilities, `.json` epochs,
    cut-offs, loss curves, tile and road counts);
  - `A-rf_*_outer*.npz`;
  - `gpu_times*.json`, `not_run.json`, `a_targets.npz`, `change_maps_2_15_48.npz`.
- **Logs:** `spatialcv_gpu.log`, `spatialcv_gpu_trackA.log` (the stopped parallel attempt), `spatialcv_ahead_cached.log`,
  `spatialcv_cpu_B-frozen.log`, `spatialcv_cpu_A-rf.log`, `spatialcv_cpu_B-trained*.log`, `spatialcv_report.log`,
  `spatialcv_posthoc_seeds.log`, `spatialcv_gpu_aft.log` (A-ft, with the crash and restart marked),
  `spatialcv_report_aft.log`.
- **Pictures:** `spatialcv_trackB_accuracy_798.png`, `spatialcv_trackB_accuracy_891.png`, `spatialcv_trackA_f1.png`,
  `spatialcv_per_fold.png`, `spatialcv_flood_maps_2_15_48.png`, `spatialcv_cells_0_14_7.png` (30 Oct).
- **26 Oct versions, before A-ft was added:** `spatialcv_numbers_before_aft.json`, `spatialcv_tables_before_aft.md`,
  `spatialcv_calls_cells_before_aft.npz`, `spatialcv_trackA_f1_before_aft.png`, `spatialcv_per_fold_before_aft.png`.
- **Weights:** `~/Masters/models/finetuned/dinov3_sat493m/spatial_cv/`. Trained parameters only, float16 for the
  blocks. Research-only twice over: the DINOv3 License and SpaceNet 8's CC BY-SA 4.0.
