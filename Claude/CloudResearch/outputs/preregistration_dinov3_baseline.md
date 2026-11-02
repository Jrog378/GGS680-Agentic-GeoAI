# Test plan: frozen DINOv3 (SAT-493M) against frozen DINOv2 on both tracks (written before running)

Written 2026-10-26 00:20 EDT, before any DINOv3 feature or score was computed. Code: GeoAI-Roads 1532e9a for every
existing module (none is edited). Justin, 2026-10-26: "I want to see how Dinov3 does since that will be our baseline
goal", then "we will not use dinov3 in the library, it is only for research and benchmarking our other models".
So DINOv3 is a **research benchmark** for the library's models (DINOv2 + classical), not a library candidate. Its code
lives only in `evidence/pilot_scripts/dinov3/` (module `dinov3_bench.py`, driver `run_phase1.py`, caches in
`dinov3/.cache/`). Nothing in `ProjectBranch/ClaudeFunctions/` imports it, and nothing is written to
`Code/results/production.json`. Results: `evidence/11_dinov3_baseline.md`.

## Status
**Exploratory, development data only.** These tiles and roads were used to build and choose the DINOv2 stages, so the
DINOv2 arms are not fresh. Every outcome below is reported whatever it shows.

## Model
- timm `vit_large_patch16_dinov3.sat493m`: DINOv3 ViT-L/16 (Simeoni et al., 2025, Meta), pretrained on the SAT-493M
  satellite set. Read offline from `~/Masters/models/huggingface` (`HF_HUB_OFFLINE=1`), on the Mac GPU (MPS), frozen.
- **Licence:** Meta's DINOv3 License (timm `license: dinov3-license`), not Apache-2.0 like the DINOv2 weights. Fine for
  this research test; it is one more reason DINOv3 stays out of the library.
- **Input:** the `tile_pair` greyscale, repeated to 3 channels and normalised with the checkpoint's own timm data config
  (mean 0.430 / 0.411 / 0.296, std 0.213 / 0.156 / 0.143). No-data is filled with the date's valid mean, as for DINOv2.
- **Patches:** 16 px = 8 m. Each date runs as a 2 x 2 window grid (about 688 x 608 px), float32, the same layout as
  `sn8_dino.tokens`. Patch tokens only: the class token and the 4 register tokens are dropped.

## Data
- `split_tables(662)`: the 186 train and 40 val tiles of Louisiana-East only; `guard_split` is used as the library does.
  `allow_held_out` is never passed. Test, the north negative set, Germany and Louisiana-West are never opened.
- The script asserts `set(roads.split) <= {"train", "val"}`.

## Track B (flood per road): mirrors `dino_test.ipynb`
- **Cues and vector**, exactly as `sn8_dino.lines_dino`: per road strip (`road_band()`), each patch weighted by the
  road's strip pixels in it. `dino3_change_pooled`, `dino3_change_mean`, `dino3_change_max` (patches holding at least a
  quarter patch of strip), and the 1,024-d pooled after - before token, reduced to 16 PCs inside each fold.
- **Roads:** the 891 cloud-free touched roads of `dino_test` (`with_dino(touched_roads(include_cloudy=True))`, not
  `cloudy`). Production-type arms are also scored on the 798 roads production's current cloud rule (tile rule + road
  rule) assesses (`touched_roads()`).
- **Model:** production's flood model, `FLOOD_MODELS[production_model()]` (tuned random forest). Folds:
  `StratifiedGroupKFold(5, shuffle=True, random_state=662)` by tile, held-out predictions by `cross_val_predict`.
- **Base:** "production without DINO" = `production_features()` minus the DINOv2 cues (the 93 classical + texture
  columns; 83.1% in `dino_test`). Current production = base + DINOv2 cues (84.3%).

| Arm | DINOv2 (re-run, must reproduce) | DINOv3 | DINOv2 + DINOv3 |
|---|---|---|---|
| cues alone | 71.5% | DINOv3 cues | both cue sets |
| cues + vector (16 PCs) alone | 83.3% | DINOv3 cues + vector | both cues + both vectors (16 PCs each) |
| base + cues | 84.3% (= production) | base + DINOv3 cues (DINOv3 in place of DINOv2) | base + both cues |
| base + cues + vector | 84.7% | base + DINOv3 cues + vector | base + both cues + both vectors |

Also each DINOv3 cue alone with one threshold (`cue_predictions`), as in `dino_test`.

- **Paired tests** (`paired_report`, same roads and folds): exact McNemar and the tile-resampled 95% interval of the
  accuracy difference for each DINOv3 arm against its DINOv2 counterpart and against production (current, with
  DINOv2 cues), and for each DINOv2 + DINOv3 arm against its DINOv2 counterpart. Base-without-DINO is also shown.
- **Confusion matrices:** TP / FN / FP / TN, accuracy (tile-resampled 95% CI), precision, recall, F1, MCC for every arm
  on the 891 roads, and for the four production-type arms of each column on the 798 assessable roads.
- **"Beats DINOv2"** means: higher accuracy than the counterpart with McNemar p < 0.05 and the interval above 0. A
  difference without that is reported as no detectable difference, not as a ranking.

## Track A (finding roads): mirrors `dino_cells_test.ipynb`
- **Cell features,** exactly as `sn8_dino_cells`: before-image tokens reduced to 32 PCs fitted on a seeded sample of 300
  patches per training tile (seed 662, training tiles only), the PC maps upsampled bilinearly to the 0.5 m grid and
  read at each 2 m cell centre of `cell_table("train")` and `cell_table("val")`.
- **Detector:** `classical_models()[production_detector()]` (random forest, 300 trees), fitted on the training cells.
- **Cut-off:** each arm's own, `f1_cutoff` on out-of-fold training-cell probabilities (the same 5 tile folds) at the
  real road share (`road_prior("train")`). The DINOv2 arms are re-run the same way and must reproduce 0.77 / 0.75 / 0.76.
- **Arms:** classical; classical + DINOv2; DINOv2 only; classical + DINOv3; DINOv3 only; classical + DINOv2 + DINOv3;
  DINOv2 + DINOv3.
- **Outcome:** validation-cell precision, recall and F1, F1 with a tile-resampled 95% interval (`cell_scores`), and the
  F1 difference (tile-resampled interval) from each arm's DINOv2 counterpart and from classical. As before, no McNemar
  on cells (cells within a tile are not independent).

## Pictures
- **Tile, fixed rule:** the validation tile with the most flooded roads (`val.nlargest(1, "roads_flooded")`, as
  `dino_test` uses). Before, after, the DINOv2 patch change (7 m) and the DINOv3 patch change (8 m), 1 - cosine, with
  the labelled roads; credit "Imagery: Maxar via SpaceNet 8".
- **Track A:** the validation tile with the most labelled roads (as `dino_cells_test`): classical + DINOv2 against
  classical + DINOv3 detections at their cut-offs.

## Logged
Run times per step, peak MPS memory, the source hashes of every module used, and every table as JSON in
`dinov3/phase1_numbers.json` (not in `Code/results/`).

## Amendment, 2026-10-26 01:40 EDT (implementation only; before any Track A DINOv3 score)
- **Track A tokens, computed in two parts.** The before-image tokens for the cell features run in two parts: the first
  20 blocks are stored in float32 (`dinov3_finetune.trunk`, shared with phase 2's fine-tuning), then the last 4 blocks
  and the final norm run on them. These are the same float32 operations as `forward_features`. On a training tile the
  result equals `tokens3` bitwise (max abs difference 0.0). The plan is unchanged; this only avoids running the
  before images through the GPU twice. The shared GPU ran about 3.5 times slower than benchmarked.
- **Track B was run before Track A had finished,** as a code check (`run_phase1.py trackB`). Its tables are final. The
  DINOv2 arms reproduce the logged accuracies exactly: 0.715 / 0.833 / 0.831 / 0.843 / 0.847.

## Phase 2: fine-tuning (appended 2026-10-26 03:08 EDT, before any training)

Justin, 2026-10-26: "Yes finetune as well using only our training set and not touching the sealed imagery go ahead
and run some fine tuning if you can". Written after the phase 1 results were seen (they are in
`evidence/11_dinov3_baseline.md`); nothing below was tuned on the validation tiles. Before this section, only a code
check ran, on 8 training and 3 validation tiles with **random** targets and shuffled road labels (no label
information), with its outputs thrown away. Code: `dinov3/dinov3_finetune.py`
(networks, targets, training loop) and `dinov3/run_phase2.py` (the run). Checkpoints, the frozen-trunk cache and
the strip tokens go in `~/Masters/models/finetuned/dinov3_sat493m/`, outside every repo.

### Data and leakage
- **Fit:** the 186 training tiles only. **Inner split:** `train_test_split(train, test_size=0.2,
  stratify=flood_class, random_state=662)`, by tile: 148 inner-fit / 38 inner-validation tiles. Early stopping,
  the number of epochs and the Track A cut-off are chosen on the inner-validation tiles. Fixed settings (below) are not
  tuned.
- **Score:** the 40 validation tiles, once, against frozen DINOv3 and frozen DINOv2 on the same validation cells and
  roads. **No 5-fold train + val CV for any fine-tuned arm.** No fine-tuned weight sees a validation tile.
- **Sealed:** test, north negative, Germany, Louisiana-West and HRC_WHU test are never opened; `allow_held_out` is
  never passed (`trunk()` refuses any tile outside train / val through `guard_split`).
- **Labels:** SpaceNet 8's published road lines and `flooded` attribute only, unmodified. Targets are rasterised the
  library's way (`road_mask` / `_road_lines`, strips from `road_band()`); no pseudo-labels.

### What is trained
- **Frozen trunk** (already cached for phase 1 and before this section; caching is not training):
  - Blocks 1-20 of the 24 run once per window (2 x 2 windows per date) and are cached: the before image in float32
    (phase 1's Track A tokens were computed from this same cache, bitwise equal to `tokens3`), the after image in
    float16.
  - A check before training: trunk + the 4 frozen top blocks must reproduce `tokens3` (cosine > 0.99 on a training
    tile).
  - Each date uses its own valid mask; Track B strips stay on pixels valid on both dates.
- **Track A, finding roads (before image):**
  - **A-ft:** the last 2 blocks + final LayerNorm unfrozen (lr 2e-5; blocks 21-22 stay frozen), and a linear head
    from each 16 px token to its 4 x 4 grid of 2 m cells (lr 1e-3).
  - **A-head (control):** the same head on frozen tokens, to separate fine-tuning from the head.
  - Target: `sn8_detect`'s cell labels on every labelled cell of the inner-fit tiles (road within 3.5 m, not road
    beyond 8 m, the band between and partly valid cells ignored); masked binary cross-entropy.
  - A-ft: up to 12 epochs, patience 3. A-head: up to 8 epochs, patience 3. Both early-stop on the
    inner-validation loss.
  - **Cut-off:** best F1 over every labelled inner-validation cell. The inner-fit model is the one scored.
- **Track B, flood per road (before + after):**
  - **B-ft:** the last 2 blocks + LayerNorm unfrozen (lr 1e-5), shared by both dates, and an MLP head (3,072 -> 256 ->
    16) on [before, after, after - before] per patch, to its 4 x 4 cells.
  - **B-head:** the same MLP head on frozen DINOv3 tokens.
  - Target: every 2 m cell whose centre is in a road's strip takes that road's published `flooded` attribute. Only the
    training roads production's cloud rule assesses (tile rule + road rule) are targets; under cloud a dry label is
    not trusted.
  - **Epochs:** chosen by early stopping on the inner-validation tiles. B-ft: up to 6, patience 2. B-head: up to
    40, patience 3.
  - **Per-road cues:** strip-weighted mean P(flooded), the max over cells holding at least a quarter cell of strip,
    and the strip share at P >= 0.5.
  - **Cross-fitting, so the random forest never learns from in-sample cues:**
    - The training tiles are split into 5 folds by tile (`StratifiedGroupKFold(5, shuffle=True, random_state=662)`
      on the training roads).
    - Each fold's model is trained on the other 4 folds for the chosen epochs, and gives the cues of its own fold's
      training roads.
    - Validation cues: the 5 fold models' probabilities averaged. None of them saw a validation tile.
    - B-ft uses 3 folds (folds 3 and 4 merged into 0 and 1), for the time budget below.
  - **Into the production random forest** (`FLOOD_MODELS[production_model()]`): fitted on the training roads, scored
    on the validation roads. Two road sets, as in phase 1: the tile rule (cloud-free tiles) and production's
    cloud rule.
- **Fixed settings:**
  - **Epoch (A-ft, A-head, B-ft):** one random window (of those holding target cells) from every fit tile, one
    optimiser step per tile. Each epoch sees about a quarter of the training pixels, like a random crop.
  - **Per-epoch evaluation:** a fixed, seeded set of 2 target windows per inner-validation tile.
  - **B-head:** trained on every strip patch, batches of 256.
  - AdamW: weight decay 0.05 on blocks, 1e-4 on heads.
  - Gradient norm clipped at 1.
  - float32. Mixed precision measured only ~3% faster on this MPS, and bf16 slower.
  - Seed 662.
  - No image augmentation: the cached trunk fixes the view.

### Time budget (why the scope above)
During phase 1 the shared Mac GPU ran about 3.5 times slower than its first benchmark: 2.7 s for each
688 x 608 window, against 0.8 s. That speed was measured while caching, before any training. At that speed, 4
trained blocks, full-tile epochs and 5 B-ft folds would not finish overnight, so three cuts were fixed now, before
training:
- 2 trained blocks instead of 4;
- one window per tile per epoch;
- 3 B-ft folds.

### Outcomes (validation tiles only)
- **Track A:** validation-cell precision, recall and F1 (tile-resampled 95% CI) and TP / FN / FP / TN for A-ft and
  A-head, beside phase 1's frozen arms (classical, classical + DINOv2 = production, DINOv2 only, classical + DINOv3,
  DINOv3 only). These are the same cells; the frozen arms' detectors were fitted on all training cells.
  - Paired F1 differences with tile-resampled intervals: A-ft against classical + DINOv2, DINOv2 only, DINOv3 only,
    classical + DINOv3 and A-head; A-head against DINOv3 only and classical + DINOv2.
- **Track B:** per road set, a confusion matrix (TP / FN / FP / TN, accuracy with a tile-resampled CI, precision,
  recall, F1, MCC) for these arms:
  - base;
  - base + DINOv2 cues (production);
  - base + frozen DINOv3 cues;
  - base + DINOv2 cues + head cues;
  - base + DINOv2 cues + fine-tuned cues;
  - base + head cues;
  - base + fine-tuned cues;
  - each cue set alone.

  Exact McNemar and the tile-resampled interval for the fine-tuned and head arms against the frozen arms (list in
  `run_phase2.py`, `B_PAIRS`). **Power is low:** the validation split holds 124 roads on 36 tiles under the tile rule and 104 on 34 under the
  cloud rule. A
  difference that is not significant is reported as no detectable difference.
- **Logged:** loss curves (training and inner-validation per epoch), times, settings, the chosen epochs and
  cut-offs, and checkpoint paths.
- **Pictures:**
  - the validation tile with the most flooded roads: before, after, frozen DINOv2 and DINOv3 change, and head and
    fine-tuned P(flooded) on the strips, with the labelled roads;
  - the validation tile with the most labelled roads: A-head and A-ft detections.

### Phase 2 amendment, 2026-10-26 03:12 EDT (before any training; only the random-target code check had run)
- **Time budget relaxed.** The code check measured the GPU back at full speed (the other agent's GPU job had ended).
  Per tile per epoch it took 0.23 s for A-head, 0.55 s for A-ft and 0.7 s for B-ft. So:
  - the epoch caps are raised: A-ft 12 -> 20 (patience 3 -> 4), A-head 8 -> 12, B-ft 6 -> 10 (patience 2 -> 3);
  - B-ft is cross-fitted on the same **5** folds as B-head, not 3.
  - The trained blocks stay as planned: 2 for A-ft and 2 for B-ft.
- **Bug found by the code check, fixed:** one road id can occur twice on a tile. 6 (tile, road id) pairs occur twice
  (12 of the 1,037 roads). Track B targets and cues are now matched to roads by their position in the
  library's road table, not by id. The script asserts that the order matches.
