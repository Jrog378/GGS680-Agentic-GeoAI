# Test plan: cloud spotting as a pipeline of tools (written before running)

Written 2026-10-26 00:20 EDT, before any score was computed. The only run so far was a crash test: DINOv3 loaded
offline on the CPU and returned a (1, 925, 1024) token array for one blank 368 x 640 window. No image was read and no
value was looked at.

**Justin (2026-10-26):** "go ahead and test out dinov2 and dinov3 for cloud spotting as well. Use all these techniques
together. it should be a pipeline of tools that all interact to get the optimal result test with and without them to
understand their impacts strengths and weaknesses as well as the optimal combos".

Later the same night: "we will not use dinov3 in the library, it is only for research and benchmarking our other
models". So:
- The library module `ClaudeFunctions/sn8_cloudspot.py` holds only the library tools: the bright rule, the dark
  channel, the texture cues and DINOv2.
- The DINOv3 code lives only in `evidence/pilot_scripts/cloud_spotting/` and is never committed to GeoAI-Roads.
- The optimal combo is chosen from the library arms only. The DINOv3 arms are a benchmark: they show how close the
  library pipeline gets.

## Status
**Exploratory, development data only. Nothing is promoted.**
- The production cloud rule (tile rule + road rule) was Justin's decision, and it stays.
- Every result is reported, whatever it is. Nothing here changes after the results are seen.
- Any departure from this plan goes in `evidence/12_cloud_spotting_pipeline.md`, not into this file.

## Data
- **HRC_WHU:** the 120 development images, `hrc_images("train")` (24 each of barren, snow, urban, vegetation and
  water).
  - The 30 test images stay sealed, and `allow_held_out` is never passed.
  - Inputs are greyscale only: `hrc_image`'s BT.601 grey.
  - The label is the expert cloud mask, unmodified.
- **SpaceNet 8:** Louisiana-East training and validation tiles only (186 + 40 = 226). The scripts assert
  `set(roads.split) <= {"train", "val"}` and that every tile read is a train or val tile.
  - Never opened: the test tiles, the north negative set, Germany, Louisiana-West and any all-splits label folder.
  - The flood labels are the published labels, unmodified. Greyscale only.

## Unit
Pixels, with features computed per pixel. The DINO features are computed per patch and interpolated to pixels
bilinearly, as `sn8_dino_cells` does for cells. A patch's value sits at its centre, matching `cv2.resize`
INTER_LINEAR with the border replicated.
- **Training pixels:** 1,000 per image, drawn uniformly at random. The generator is `np.random.default_rng([662, i])`,
  where i is the image's place in `hrc_images("train")`. The positions are fixed before any feature is computed.
- **Scored pixels:** a fixed grid of every 4th row and column, starting at (2, 2). That is 180 x 320 = 57,600 pixels
  per image, or 6.91 M over the 120 images. Each image is scored once, by the fold model that never saw it.
- The fixed rules are also scored on every pixel, as a check that the grid matches the full image. Tonight's
  full-image values (`mask_combo.csv`): bright F1 0.411, dark 0.649.

## Tools (per-pixel features, grey 0–255; windows in pixels, as in `sn8_clouds`)
| Tool | Features |
|---|---|
| **B**, bright rule | grey; local std over 21 px; the bright flag (`bright_mask`: grey > 200 and std < 10) |
| **D**, dark channel | the dark channel (`dark_channel`, 41 px); the dark flag (above `cloud_thresholds()["dark"]`, the SpaceNet 8 Otsu cut) |
| **T**, texture / local contrast | local range (max − min) over 21 px; mean Sobel gradient magnitude over 21 px; local std over 41 px |
| **V2**, DINOv2 (library) | `sn8_dino.tokens`: ViT-L/14 with registers, frozen, grey repeated to 3 channels, ImageNet mean and std, 2 x 2 windows, 14 px patches → 32 principal components |
| **V3**, DINOv3 (research benchmark only) | timm `vit_large_patch16_dinov3.sat493m`, frozen, read offline from `~/Masters/models/huggingface/hub`; grey repeated to 3 channels, the model's own sat493m mean and std, the same 2 x 2 windows, 16 px patches → 32 principal components |

**PCA rule:**
- Each backbone's 1,024-d tokens are reduced to **32** components.
- The PCA is fitted inside each training fold only, on 500 patches per training image (seeded), centred and not
  whitened.
- The final spotter for SpaceNet 8 fits it the same way on all 120 images.

## Learners (fixed settings, no tuning)
- **Primary:** `RandomForestClassifier(n_estimators=100, max_features="sqrt", min_samples_leaf=20, n_jobs=4,
  random_state=662)`. A pixel is cloud when its predicted probability is ≥ 0.5.
- **Secondary, the linear probe:** `StandardScaler` + `LogisticRegression(C=1.0, max_iter=2000)`, cut at 0.5. It is
  reported but does not enter the choice.
- No class weights. Each arm's learner sees only that arm's feature columns.

## Validation
`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)` over the 120 images, stratified by land-cover type
and grouped by image. Every image's pixels are in exactly one fold.

## Arms
**Fixed rules** (no learning; references, not candidates):
- the bright rule;
- the dark rule (production's dark mask, the reference for every paired comparison);
- bright OR dark;
- bright AND dark.

**Library arms** (the choice set):
| # | Arm | Tools |
|---|---|---|
| 1 | bright | B |
| 2 | dark | D |
| 3 | bright + dark | B D |
| 4 | classical (all classical cues) | B D T |
| 5 | DINOv2 | V2 |
| 6 | **classical + DINOv2, the library primary** | B D T V2 |
| 7 | 6 − bright | D T V2 |
| 8 | 6 − dark | B T V2 |
| 9 | 6 − texture | B D V2 |

6 − DINOv2 is arm 4.

**DINOv3 benchmark arms** (research only, never chosen):
| # | Arm | Tools |
|---|---|---|
| 10 | DINOv3 | V3 |
| 11 | DINOv2 + DINOv3 | V2 V3 |
| 12 | classical + DINOv3 | B D T V3 |
| 13 | **everything, the benchmark primary** | B D T V2 V3 |
| 14 | 13 − bright | D T V2 V3 |
| 15 | 13 − dark | B T V2 V3 |
| 16 | 13 − texture | B D V2 V3 |

13 − DINOv2 is arm 12, and 13 − DINOv3 is arm 6.

## Metrics
- **Pooled pixel scores** on the scored pixels: precision, recall, F1 and IoU, overall and by land-cover type. Every
  pixel weighs the same.
- **Intervals:** 95% percentile intervals from 2,000 resamples of whole images, seed 662. Overall, images are
  resampled within each land-cover type. By type, they are resampled within the type.
- **Paired comparisons** (each arm against the dark rule, and every tool comparison below):
  - the F1 difference, with its 95% interval from the same resampled images;
  - an exact sign test on the per-image F1 (images where the arm is higher against lower). Ties are dropped, and so
    are images where the F1 is undefined.
- **Tool impacts**, as F1 differences with paired intervals:
  - **Gain when added (library):** dark to bright (3 − 1); bright to dark (3 − 2); texture to bright + dark
    (4 − 3); DINOv2 to classical (6 − 4); classical to DINOv2 (6 − 5).
  - **Loss when removed from 6:** 6 − 7 (bright), 6 − 8 (dark), 6 − 9 (texture), 6 − 4 (DINOv2).
  - **Benchmark:** DINOv3 added to classical (12 − 4), to DINOv2 (11 − 5) and to arm 6 (13 − 6); classical added to
    DINOv3 (12 − 10).
  - **Loss when removed from 13:** 13 − 14, 13 − 15, 13 − 16, 13 − 12 (DINOv2) and 13 − 6 (DINOv3).

## How the optimal (library) combo is chosen
1. The best arm is the one among arms 1–9 with the highest pooled random-forest F1.
2. The candidates are the best arm, plus every arm 1–9 whose paired 95% interval for (best − arm) F1 includes 0. A
   paired interval is used rather than the overlap of two separate intervals, because the arms are scored on the
   same images.
3. The chosen spotter is the simplest candidate. Simpler means, in order:
   1. not using DINOv2, which needs a GPU and a 300 M-parameter model;
   2. fewer classical tools;
   3. fewer feature columns.

   Any tie left is broken by the higher F1.
4. The benchmark gap is the best of arms 10–16 minus the chosen spotter: an F1 difference with a paired interval,
   plus the chosen F1 as a share of the benchmark F1.
5. If the chosen spotter's paired interval against the dark rule includes 0, the write-up says that no learned
   spotter beats production's dark channel here. The SpaceNet 8 test still runs with the chosen spotter.

## SpaceNet 8 (226 development tiles; no cloud labels)
1. **The spotter.**
   - The chosen arm, its random forest refitted on the training pixels of all 120 development images, with the PCA
     (if DINOv2 is in it) fitted on all 120.
   - It is applied to each tile's greyscale after image. Pixels off the valid mask (`sn8_clouds` erodes the no-data)
     are not cloud.
   - Cloud is p ≥ 0.5.
2. **Per road:** the share of the road's strip under the spotter mask.
   - The strip is the one `sn8_clouds.lines_cloud` uses: within `road_band()` m of the road line, on valid pixels.
   - The module's strip code must reproduce `cloud_dark_rise_road` from the dark-rise mask exactly. The run asserts it.
3. **Agreement with the production road rule:** roads flagged by the road rule (dark-rise share ≥ 0.2), roads
   flagged by the spotter (share ≥ 0.2, the same `ROAD_CLOUD_CUT`), both, either, and the Jaccard overlap. Reported
   on all roads and on the roads the tile rule keeps.
4. **The flood model with each gate:**
   - **Production gate:** `assessable(roads, production_cloud_rule())`, that is, the tile rule + road rule.
   - **Spotter gate:** the tile rule + the spotter road rule (share < 0.2). It replaces the road rule only.
   - **Model:** `FLOOD_MODELS[production_model()]` on `production_features()`, over
     `touched_roads(include_cloudy=True)`, with `StratifiedGroupKFold(5, shuffle=True, random_state=662)` by tile.
     The folds are the same for both gates, and `gated_calls` is used: each fold fits on the kept roads of the other
     folds and calls the kept roads of its own.
   - **Reported per gate:** roads kept, roads set aside, and flooded roads set aside. On the kept roads: the full
     confusion matrix (TP / FN / FP / TN), accuracy with a tile-resampled 95% interval, and MCC.
   - **On the shared roads** (kept by both): each gate's accuracy, the difference with a tile-resampled interval,
     roads fixed / broken, and exact McNemar (`paired_report`).
   - **On the roads only one gate keeps:** that gate's calls and the labels there.
5. **Label caveat:** cloud on a road makes its flood label untrustworthy. SpaceNet 8 analysts labelled only what they
   could see, so a hidden flooded road reads as "not flooded". A gate that keeps more cloudy roads can therefore score
   worse on these labels without spotting cloud worse. That is reported as it is, not optimised away.

## Pictures (`figures/cloud_spotting/`)
- **HRC_WHU:** the first barren and the first vegetation image in `hrc_images("train")` order (barren_1 and
  vegetation_1). Panels: grey image, expert mask, dark rule, DINOv3 alone (benchmark), and the chosen library spotter.
  The learned maps are each image's held-out fold predictions on every pixel. Credit line: "HRC_WHU (Li et al. 2019),
  academic use only".
- **SpaceNet 8:** tile 2_23_44 (thin cloud): before, after, the dark-rise mask, the spotter mask, and the roads each
  gate sets aside. Credit line: "Imagery: Maxar via SpaceNet 8".

## Code
- **Library:** a new module `ClaudeFunctions/sn8_cloudspot.py` with no DINOv3 code. It imports `sn8_clouds`,
  `sn8_cloudref` and `sn8_dino` and copies nothing from them. It is committed alone with `git commit -- <path>` and
  not pushed.
- **Research drivers:** `evidence/pilot_scripts/cloud_spotting/`. The DINOv3 loader is there, uncommitted.
- **Caches:** under `ClaudeFunctions/.cache/cloudspot/`. DINOv3 files there carry a `research_` prefix.
- **Process:** `python3 -I` with `/opt/miniconda3/bin/python3`. No installs, no downloads, no warning filters. The GPU
  is shared, so token extraction runs one window at a time, in the background.
