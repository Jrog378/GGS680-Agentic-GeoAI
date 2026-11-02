# 11. DINOv3 (SAT-493M) as a research benchmark for the library's DINOv2 + classical models

Run 2026-10-26: phase 1 (frozen) 00:20-03:00 EDT; phase 2 (fine-tuned) 03:15-04:50 EDT. Justin asked for it: "I want to see how Dinov3 does since that will
be our baseline goal". He then added: "we will not use dinov3 in the library, it is only for research and
benchmarking our other models".

So DINOv3 here is a **yardstick for the library's models**: frozen DINOv2 + the classical cues. It is not a candidate
for the library.
- Its code lives only in `evidence/pilot_scripts/dinov3/`. Nothing in `ProjectBranch/ClaudeFunctions/` imports it,
  and nothing was committed to GeoAI-Roads.
- Nothing was written to `Code/results/production.json`.
- The plan was written before the run: `outputs/preregistration_dinov3_baseline.md`, with its 01:40 amendment
  (implementation only).

**Development data only:** the 186 train and 40 val tiles of Louisiana-East, greyscale. The scripts assert
`set(roads.split) <= {"train", "val"}`. Test, the north negative set, Germany and Louisiana-West were never opened, and
`allow_held_out` was never passed. Exploratory: the DINOv2 arms were chosen on these same tiles.

## Model and licence
- **Model:** timm `vit_large_patch16_dinov3.sat493m`. This is DINOv3 ViT-L/16 (Siméoni et al., 2025, Meta),
  pretrained on the SAT-493M satellite set.
  - Frozen, read offline from `~/Masters/models/huggingface`, run on the Mac GPU (MPS).
  - The greyscale tile is repeated to 3 channels and normalised with the checkpoint's own config: mean 0.430 / 0.411 /
    0.296, std 0.213 / 0.156 / 0.143.
  - Patches are 16 px = 8 m, in 2 x 2 windows per date. The class token and the 4 register tokens are dropped.
- **Licence:** **Meta's DINOv3 License** (timm tag `dinov3-license`), not Apache-2.0 like the DINOv2 weights the
  library uses. It is fine for this research benchmark and is a further reason DINOv3 stays out of the library. Any
  model fitted on these features is research-only twice over: the DINOv3 License, plus SpaceNet 8's CC BY-SA.
- `~/Masters/models/hotosm/dinov3-damage` was not used.

## Bottom line
1. **Finding roads (Track A): DINOv3 beats DINOv2.**
   - Classical + DINOv3 reaches validation-cell F1 **0.747**, against **0.713** for classical + DINOv2 (production's
     features): **+0.033** (tile-resampled 95% CI +0.014 to +0.057).
   - DINOv3 alone reaches **0.733** against **0.683** for DINOv2 alone: **+0.050** (+0.021 to +0.082).
   - DINOv3's detections are cleaner: precision 0.74 against 0.70 at the same recall or better.
   - Adding DINOv2 on top of classical + DINOv3 adds nothing detectable (+0.006, -0.010 to +0.021).
2. **Flood per road (Track B): DINOv3 does not beat DINOv2.** No DINOv3 arm differs significantly from its DINOv2
   counterpart:
   - cues alone: 72.2% against 71.5%, p = 0.74;
   - cues + vector: 84.3% against 83.3%, p = 0.44;
   - production with DINOv3 cues in place of DINOv2's: **83.4% against 84.3%**, p = 0.23;
   - with the vector as well: 83.7% against 84.7%, p = 0.21.

   On the classical pipeline, the DINOv3 cues add nothing detectable (+0.3 points over the base, p = 0.76). The DINOv2
   cues did add (+1.2, p = 0.035).
3. **The two backbones carry partly different change information.**
   - Without the classical cues, DINOv2 + DINOv3 together beat either one alone: cues 76.2% against 71.5% (DINOv2,
     p = 0.0004) and 72.2% (DINOv3, p = 0.004).
   - Cues + vectors together reach 85.9%, the highest of every arm on the 891 roads: +2.6 over DINOv2's (p = 0.013) and
     +1.6 over DINOv3's (p = 0.029).
   - That 85.9% is **not** significantly above production (84.3%, +1.6, CI -0.6 to +3.7, p = 0.18).
   - On top of the classical cues, adding both backbones gives at most +0.6 points (n.s.).
4. **As a yardstick:**
   - For finding roads, the library's frozen DINOv2 sits about 3-5 F1 points below what a satellite-pretrained
     frontier backbone reaches with the same random forest.
   - For flood per road, the library's DINOv2 + classical pipeline already matches frozen DINOv3.

5. **Phase 2: fine-tuned DINOv3, trained on the 186 training tiles only and scored once on the 40 validation tiles.**
   - **Finding roads:** fine-tuning the last 2 blocks reaches validation-cell F1 **0.780**, against 0.713 for
     production (**+0.067**, +0.023 to +0.109). It is +0.034 over frozen classical + DINOv3 (-0.013 to +0.069, not
     significant).
   - **Flood per road:** per-road cues from a fine-tuned DINOv3 flood head lift production's random forest on the
     validation roads by **5.7 to 9.6 points**, from 81.7-84.7% to 89.4-91.3%. Against production, only one arm meets
     the library's stage rule (interval above 0 and p < 0.05): base + fine-tuned cues on the cloud-rule roads,
     **+9.6 (+2.8 to +18.8), 10 roads fixed and 0 broken, p = 0.002**.
   - **Caveat, post hoc:** these gains sit almost entirely on validation roads whose OSM way continues from a
     training tile. That is 77 of the 104 cloud-rule roads; on the other 27 the fine-tuned arms change nothing.
     Spatial continuity may inflate them; see phase 2 below.

## Track B: flood per road (5 folds by tile, `StratifiedGroupKFold(5, shuffle=True, random_state=662)`)
The model is production's tuned random forest. "Base" means production without DINO: the 93 classical and texture
columns. Production = base + DINOv2 cues. "Vector" = the pooled after - before token, reduced to 16 PCs inside each
fold.

**Reproduction:** the DINOv2 arms give exactly the logged 2026-10-23 accuracies: 0.715, 0.833, 0.831, 0.843, 0.847.

### 891 cloud-free touched roads (465 flooded): confusion matrices
| arm | TP | FN | FP | TN | accuracy (95% CI) | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| DINOv2 cues | 369 | 96 | 158 | 268 | 0.715 (0.67-0.76) | 0.700 | 0.794 | 0.629 | 0.744 | 0.429 |
| DINOv3 cues | 389 | 76 | 172 | 254 | 0.722 (0.67-0.77) | 0.693 | 0.837 | 0.596 | 0.758 | 0.448 |
| DINOv2 + DINOv3 cues | 387 | 78 | 134 | 292 | 0.762 (0.72-0.80) | 0.743 | 0.832 | 0.685 | 0.785 | 0.525 |
| DINOv2 cues + vector | 408 | 57 | 92 | 334 | 0.833 (0.79-0.87) | 0.816 | 0.877 | 0.784 | 0.846 | 0.666 |
| DINOv3 cues + vector | 413 | 52 | 88 | 338 | 0.843 (0.80-0.88) | 0.824 | 0.888 | 0.793 | 0.855 | 0.686 |
| DINOv2 + DINOv3 cues + vectors | 425 | 40 | 86 | 340 | **0.859** (0.82-0.89) | 0.832 | 0.914 | 0.798 | 0.871 | 0.719 |
| base (production without DINO) | 401 | 64 | 87 | 339 | 0.831 (0.79-0.86) | 0.822 | 0.862 | 0.796 | 0.842 | 0.661 |
| **base + DINOv2 cues (production)** | 408 | 57 | 83 | 343 | **0.843** (0.81-0.88) | 0.831 | 0.877 | 0.805 | 0.854 | 0.686 |
| base + DINOv3 cues | 405 | 60 | 88 | 338 | 0.834 (0.80-0.87) | 0.822 | 0.871 | 0.793 | 0.846 | 0.668 |
| base + DINOv2 + DINOv3 cues | 411 | 54 | 84 | 342 | 0.845 (0.81-0.88) | 0.830 | 0.884 | 0.803 | 0.856 | 0.690 |
| base + DINOv2 cues + vector | 409 | 56 | 80 | 346 | 0.847 (0.81-0.88) | 0.836 | 0.880 | 0.812 | 0.857 | 0.694 |
| base + DINOv3 cues + vector | 410 | 55 | 90 | 336 | 0.837 (0.80-0.87) | 0.820 | 0.882 | 0.789 | 0.850 | 0.675 |
| base + DINOv2 + DINOv3 cues + vectors | 415 | 50 | 85 | 341 | 0.848 (0.81-0.88) | 0.830 | 0.892 | 0.800 | 0.860 | 0.698 |
| always "flooded" | 465 | 0 | 426 | 0 | 0.522 (0.44-0.60) | 0.522 | 1.000 | 0.000 | 0.686 | 0.000 |

**Each DINOv3 cue alone, with one threshold:**
- `dino3_change_pooled` 0.688 (DINOv2's 0.658);
- `dino3_change_mean` 0.687 (0.663);
- `dino3_change_max` 0.639 (0.524).

### Paired tests, 891 roads
These use the same roads and folds. The interval resamples whole tiles; McNemar is exact.

| arm | against | difference | 95% CI | fixed / broken | McNemar p |
|---|---|---|---|---|---|
| DINOv3 cues | DINOv2 cues | +0.007 | -0.030 to +0.046 | 114 / 108 | 0.74 |
| DINOv3 cues + vector | DINOv2 cues + vector | +0.010 | -0.020 to +0.040 | 57 / 48 | 0.44 |
| base + DINOv3 cues | **production** (base + DINOv2 cues) | -0.009 | -0.024 to +0.005 | 13 / 21 | 0.23 |
| base + DINOv3 cues + vector | base + DINOv2 cues + vector | -0.010 | -0.025 to +0.005 | 16 / 25 | 0.21 |
| base + DINOv3 cues + vector | production | -0.006 | -0.023 to +0.012 | 26 / 31 | 0.60 |
| DINOv3 cues + vector | production | +0.000 | -0.025 to +0.025 | 51 / 51 | 1.00 |
| DINOv3 cues | production | -0.121 | -0.160 to -0.083 | 62 / 170 | <0.0001 |
| DINOv2 + DINOv3 cues | DINOv2 cues | **+0.047** | +0.021 to +0.075 | 88 / 46 | **0.0004** |
| DINOv2 + DINOv3 cues | DINOv3 cues | **+0.040** | +0.010 to +0.068 | 93 / 57 | **0.004** |
| DINOv2 + DINOv3 cues + vectors | DINOv2 cues + vector | **+0.026** | +0.002 to +0.049 | 51 / 28 | **0.013** |
| DINOv2 + DINOv3 cues + vectors | DINOv3 cues + vector | **+0.016** | +0.002 to +0.030 | 25 / 11 | **0.029** |
| DINOv2 + DINOv3 cues + vectors | production | +0.016 | -0.006 to +0.037 | 54 / 40 | 0.18 |
| base + DINOv2 + DINOv3 cues | production | +0.002 | -0.013 to +0.016 | 21 / 19 | 0.87 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | +0.001 | -0.013 to +0.015 | 20 / 19 | 1.00 |
| base + DINOv2 + DINOv3 cues + vectors | production | +0.006 | -0.013 to +0.023 | 31 / 26 | 0.60 |
| base + DINOv2 + DINOv3 cues | base + DINOv3 cues | +0.011 | +0.001 to +0.022 | 18 / 8 | 0.076 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv3 cues + vector | +0.011 | +0.002 to +0.021 | 14 / 4 | 0.031 |
| production | base (without DINO) | +0.012 | +0.002 to +0.023 | 17 / 6 | 0.035 |
| base + DINOv2 cues + vector | base | +0.017 | +0.003 to +0.031 | 28 / 13 | 0.028 |
| base + DINOv3 cues | base | +0.003 | -0.011 to +0.018 | 22 / 19 | 0.76 |
| base + DINOv3 cues + vector | base | +0.007 | -0.012 to +0.026 | 35 / 29 | 0.53 |
| base + DINOv2 + DINOv3 cues | base | +0.015 | -0.001 to +0.030 | 31 / 18 | 0.085 |
| base + DINOv2 + DINOv3 cues + vectors | base | +0.018 | -0.002 to +0.038 | 43 / 27 | 0.072 |

### 798 roads production's cloud rule assesses (tile rule + road rule; 441 flooded): production-type arms
| arm | TP | FN | FP | TN | accuracy (95% CI) | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 381 | 60 | 89 | 268 | 0.813 (0.78-0.85) | 0.811 | 0.864 | 0.751 | 0.836 | 0.621 |
| **base + DINOv2 cues (production)** | 394 | 47 | 89 | 268 | **0.830** (0.79-0.86) | 0.816 | 0.893 | 0.751 | 0.853 | 0.655 |
| base + DINOv3 cues | 394 | 47 | 91 | 266 | 0.827 (0.79-0.86) | 0.812 | 0.893 | 0.745 | 0.851 | 0.650 |
| base + DINOv2 + DINOv3 cues | 394 | 47 | 88 | 269 | 0.831 (0.79-0.87) | 0.817 | 0.893 | 0.754 | 0.854 | 0.658 |
| base + DINOv2 cues + vector | 394 | 47 | 88 | 269 | 0.831 (0.80-0.87) | 0.817 | 0.893 | 0.754 | 0.854 | 0.658 |
| base + DINOv3 cues + vector | 395 | 46 | 90 | 267 | 0.830 (0.79-0.87) | 0.814 | 0.896 | 0.748 | 0.853 | 0.655 |
| base + DINOv2 + DINOv3 cues + vectors | 399 | 42 | 89 | 268 | 0.836 (0.80-0.87) | 0.818 | 0.905 | 0.751 | 0.859 | 0.669 |
| always "flooded" | 441 | 0 | 357 | 0 | 0.553 (0.47-0.63) | 0.553 | 1.000 | 0.000 | 0.712 | 0.000 |

**Paired, 798 roads:**
- **DINOv3 against DINOv2:**
  - base + DINOv3 cues vs production: -0.003 (-0.018 to +0.013), 18 / 20, p = 0.87;
  - base + DINOv3 cues + vector vs its DINOv2 counterpart: -0.001, p = 1.00;
  - base + DINOv3 cues + vector vs production: +0.000, p = 1.00.
- **Both backbones against production or its counterpart:**
  - base + both cues vs production: +0.001, p = 1.00;
  - base + both cues + vectors vs base + DINOv2 cues + vector: +0.005, p = 0.64;
  - base + both cues + vectors vs production: +0.006, p = 0.58.
- **Against the base (no DINO):**
  - production vs base: +0.016 (+0.005 to +0.028), p = 0.019;
  - base + DINOv3 cues vs base: +0.014, p = 0.16;
  - base + both + vectors vs base: +0.023 (+0.003 to +0.043), p = 0.033.

Every DINOv3 and DINOv2 option lies within 0.6 points of production; none differs detectably.

## Track A: finding roads (validation cells, 40 tiles, 338,885 cells, 7,205 road)
The detector is production's random forest (300 trees). The cell features are the before-image tokens reduced to 32
PCs, fitted on 300 seeded patches per training tile, interpolated to 2 m cells. Each arm's cut-off is the best F1 on
out-of-fold training cells (5 tile folds) at the real road share (0.0221). Every arm scores the same cells.

**Reproduction:** the DINOv2 arms give exactly the logged results. F1 is 0.510 / 0.713 / 0.683 and the cut-offs are
0.77 / 0.75 / 0.76.

| arm (cut-off) | TP | FN | FP | TN | precision | recall | F1 (95% CI) | F1 vs classical (95% CI) |
|---|---|---|---|---|---|---|---|---|
| classical (0.77) | 3,704 | 3,501 | 3,617 | 328,063 | 0.506 | 0.514 | 0.510 (0.442-0.581) | - |
| classical + DINOv2 (0.75), **production** | 5,274 | 1,931 | 2,306 | 329,374 | 0.696 | 0.732 | 0.713 (0.651-0.772) | +0.203 (+0.159 to +0.248) |
| DINOv2 only (0.76) | 5,116 | 2,089 | 2,661 | 329,019 | 0.658 | 0.710 | 0.683 (0.620-0.745) | +0.173 (+0.117 to +0.228) |
| **classical + DINOv3 (0.71)** | 5,441 | 1,764 | 1,927 | 329,753 | 0.738 | 0.755 | **0.747** (0.690-0.802) | +0.237 (+0.194 to +0.284) |
| **DINOv3 only (0.69)** | 5,447 | 1,758 | 2,213 | 329,467 | 0.711 | 0.756 | **0.733** (0.672-0.793) | +0.223 (+0.173 to +0.275) |
| classical + DINOv2 + DINOv3 (0.70) | 5,666 | 1,539 | 2,182 | 329,498 | 0.722 | 0.786 | 0.753 (0.689-0.811) | +0.243 (+0.196 to +0.289) |
| DINOv2 + DINOv3 (0.72) | 5,552 | 1,653 | 2,030 | 329,650 | 0.732 | 0.771 | 0.751 (0.687-0.811) | +0.241 (+0.192 to +0.291) |

**F1 differences from the DINOv2 counterpart** (same cells; whole tiles resampled, 1,000 draws). As before, there is no
McNemar on cells, because cells within a tile are not independent.
| arm | against | F1 difference (95% CI) |
|---|---|---|
| classical + DINOv3 | classical + DINOv2 (production) | **+0.033 (+0.014 to +0.057)** |
| DINOv3 only | DINOv2 only | **+0.050 (+0.021 to +0.082)** |
| classical + DINOv2 + DINOv3 | classical + DINOv2 | +0.039 (+0.027 to +0.052) |
| DINOv2 + DINOv3 | DINOv2 only | +0.068 (+0.051 to +0.090) |
| classical + DINOv2 + DINOv3 | classical + DINOv3 | +0.006 (-0.010 to +0.021) |

## Pictures (`evidence/pilot_scripts/dinov3/`; imagery: Maxar via SpaceNet 8)
- **`phase1_change_maps_2_15_48.png`:** the validation tile with the most flooded roads (fixed rule, as `dino_test`).
  It shows before, after, and the DINOv2 patch change (7 m) beside the DINOv3 patch change (8 m), with the labelled
  roads.
  - The DINOv3 map is smoother and follows objects. The flooded main road and the flooded open ground to its east
    stand out as continuous high-change bands.
  - The DINOv2 map is speckled patch to patch.
  - Median change: DINOv2 0.37, DINOv3 0.44. 99th percentile: DINOv2 0.86, DINOv3 0.76.
- **`phase1_calls_2_15_48_*.png`:** production's held-out per-road calls against base + DINOv3 cues (± vector) on the
  same tile.
- **`phase1_cells_0_14_7.png`:** the validation tile with the most labelled roads (as `dino_cells_test`). It shows
  every cell for classical + DINOv2 (production), classical + DINOv3 and DINOv3 only.
  - Recall is the same (0.66, 0.66, 0.65).
  - Precision rises from 0.77 to 0.88 and 0.88. DINOv2's false road cells along the rail / levee line at the lower
    left are gone with DINOv3 (1,114 false cells, against 530 and 503).
  - The PNG was redrawn after the run with its title row unclipped (`redraw_cells_picture.py`). That script refits
    the same three detectors; the counts are identical.

## Run time (Apple M2, MPS GPU shared with another agent's DINOv2 / DINOv3 extraction)
- **Track B tokens** (226 tiles x 2 dates, 4 windows each): 2,990 s for train and 589 s for val, about 16 s per tile.
  That is about 3.5x slower than the 0.8 s per window measured alone first.
- **Track A** before-image trunk + basis (186 training tiles): 1,779 s. Cell features: 329 s (train) + 244 s (val).
- **GPU total: about 99 minutes.**
- **Random-forest fits for the 7 Track A arms** (6 fits each on 205,581 cells): 5,519 s (550-1,309 s per arm), on a
  heavily shared CPU.
- **Track B arms:** about 2-9 s each. Pictures: 346 s.
- **Wall clock:** 00:20-03:00. Peak MPS driver memory 2.19 GB per process.

## Caveats
- **Exploratory.** Same development tiles as the DINOv2 stages, and one event, one sensor. DINOv3 was not tuned, but
  DINOv2's settings (2 x 2 windows, strip pooling, 32 cell PCs, 16 vector PCs) were carried over unchanged. Other
  settings might suit DINOv3's 16 px patches better.
- **Track A's interval** resamples the 40 validation tiles. Both DINOv3 gains exclude 0, but it is one validation
  split. The cut-offs are chosen on training cells only.
- **Track B's DINOv3-for-DINOv2 swap** is about -1 point with intervals of ±1.5. "No detectable difference" is the
  honest reading; neither is better.

## Phase 2: fine-tuning on the training tiles only (plan: the "Phase 2" section of the test plan)
Justin, 2026-10-26: "Yes finetune as well using only our training set and not touching the sealed imagery".

**What ran:**
- **Frozen trunk:** DINOv3's blocks 1-20 stay frozen and cached.
- **Fine-tuned parts:** the last 2 blocks (21-22 frozen, 23-24 + final LayerNorm trained), plus a head mapping each
  16 px token to its 4 x 4 grid of 2 m cells.
- **Data:**
  - Fit on 148 of the 186 training tiles.
  - The other 38 (inner validation, a seeded split stratified on flood class) chose the epochs, by early stopping
    on their loss, and the Track A cut-off.
  - Each fine-tuned arm is scored **once on the 40 validation tiles**, never by train + val cross-validation.
- **Labels:** SpaceNet 8's road lines and published `flooded` attribute only, rasterised the library's way. Track B
  targets are only the training roads that the production cloud rule assesses.
- **Settings:** AdamW, float32, no augmentation. An epoch = one random window per tile.
- **Track B cross-fitting, so the random forest never learns from in-sample cues:**
  - Five fold models are trained on the training tiles (`StratifiedGroupKFold(5, shuffle=True, random_state=662)`
    on the training roads, by tile).
  - Each fold model gives the cues of its own fold's training roads.
  - Validation cues are the mean of the 5 fold models; none of them saw a validation tile.
- **Same tiles and roads as the frozen arms:** the frozen DINOv2 and DINOv3 arms are scored on the same validation
  cells and roads, with their models fitted on the training tiles.
- **Checks before training:**
  - trunk + frozen top blocks = `tokens3` (cosine 1.00000);
  - the Track A targets equal the library's cell labels;
  - a code check with random targets.
- **Bug found by the code check, fixed before training:** one road id can occur twice on a tile (6 pairs). Cues are
  therefore matched to roads by row position.

**Chosen on the inner validation tiles:**
- A-ft: best of 20 epochs (cap reached; loss flat from about epoch 10). Cut-off 0.46; inner-validation F1 0.780.
- A-head: 12 epochs (cap reached, still falling slowly). Cut-off 0.25; inner-validation F1 0.670.
- B-head: **1 epoch** (its inner-validation loss rose from epoch 2).
- B-ft: **3 epochs** (lowest inner-validation loss of 6).

Loss curves: `phase2_loss_curves.png`.

### Track A, validation cells (the same 338,885 cells as phase 1)
| arm (cut-off) | TP | FN | FP | TN | precision | recall | F1 (95% CI) |
|---|---|---|---|---|---|---|---|
| classical + DINOv2 (0.75), **production**, frozen | 5,274 | 1,931 | 2,306 | 329,374 | 0.696 | 0.732 | 0.713 (0.651-0.772) |
| DINOv2 only (0.76), frozen | 5,116 | 2,089 | 2,661 | 329,019 | 0.658 | 0.710 | 0.683 (0.620-0.745) |
| classical + DINOv3 (0.71), frozen | 5,441 | 1,764 | 1,927 | 329,753 | 0.738 | 0.755 | 0.747 (0.690-0.802) |
| DINOv3 only (0.69), frozen | 5,447 | 1,758 | 2,213 | 329,467 | 0.711 | 0.756 | 0.733 (0.672-0.793) |
| DINOv3 linear head on frozen tokens (0.25) | 5,180 | 2,025 | 2,820 | 328,860 | 0.648 | 0.719 | 0.681 (0.617-0.746) |
| **DINOv3 fine-tuned, last 2 blocks + head (0.46)** | 5,735 | 1,470 | 1,756 | 329,924 | 0.766 | 0.796 | **0.780 (0.722-0.836)** |

| fine-tuned / head arm | against | F1 difference (95% CI, tiles resampled) |
|---|---|---|
| DINOv3 fine-tuned | classical + DINOv2 (production) | **+0.067 (+0.023 to +0.109)** |
| DINOv3 fine-tuned | DINOv2 only | **+0.098 (+0.051 to +0.141)** |
| DINOv3 fine-tuned | DINOv3 only, frozen | +0.048 (-0.001 to +0.088) |
| DINOv3 fine-tuned | classical + DINOv3, frozen | +0.034 (-0.013 to +0.069) |
| DINOv3 fine-tuned | DINOv3 linear head, frozen | +0.099 (+0.056 to +0.137) |
| DINOv3 linear head, frozen | DINOv3 only, frozen (random forest on 32 PCs) | -0.052 (-0.082 to -0.028) |
| DINOv3 linear head, frozen | classical + DINOv2 (production) | -0.032 (-0.060 to -0.006) |

**Reading:**
- Fine-tuning helps. It beats the same linear head on frozen tokens by 0.10 F1 and production by 0.07.
- It is not detectably better than frozen DINOv3 with the random forest.
- The fine-tuned model was fitted on 148 tiles and the frozen detectors on all 186.

### Track B, validation roads
The model is production's tuned random forest, fitted on the training roads and scored once on the validation roads.
"Head cues" come from the flood head on frozen DINOv3 tokens; "fine-tuned cues" from the last 2 blocks + head. Each
is a cue triple: strip-mean, max and share of P(flooded) >= 0.5.

**Tile rule: 767 training roads, then 124 validation roads (63 flooded) on 36 tiles**
| arm | TP | FN | FP | TN | accuracy (95% CI) | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| base (no DINO) | 55 | 8 | 11 | 50 | 0.847 (0.79-0.91) | 0.833 | 0.873 | 0.820 | 0.853 | 0.694 |
| **base + DINOv2 cues (production)** | 55 | 8 | 11 | 50 | **0.847** (0.77-0.92) | 0.833 | 0.873 | 0.820 | 0.853 | 0.694 |
| base + DINOv3 cues (frozen) | 54 | 9 | 11 | 50 | 0.839 (0.76-0.92) | 0.831 | 0.857 | 0.820 | 0.844 | 0.678 |
| base + DINOv2 cues + DINOv3 head cues | 58 | 5 | 8 | 53 | 0.895 (0.82-0.97) | 0.879 | 0.921 | 0.869 | 0.899 | 0.791 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | 60 | 3 | 9 | 52 | **0.903** (0.84-0.96) | 0.870 | 0.952 | 0.852 | 0.909 | 0.810 |
| base + DINOv3 head cues | 57 | 6 | 7 | 54 | 0.895 (0.83-0.96) | 0.891 | 0.905 | 0.885 | 0.898 | 0.790 |
| base + DINOv3 fine-tuned cues | 58 | 5 | 9 | 52 | 0.887 (0.83-0.95) | 0.866 | 0.921 | 0.852 | 0.892 | 0.776 |
| DINOv2 cues | 47 | 16 | 15 | 46 | 0.750 (0.64-0.86) | 0.758 | 0.746 | 0.754 | 0.752 | 0.500 |
| DINOv3 cues (frozen) | 51 | 12 | 26 | 35 | 0.694 (0.60-0.79) | 0.662 | 0.810 | 0.574 | 0.729 | 0.395 |
| DINOv3 head cues | 56 | 7 | 9 | 52 | 0.871 (0.80-0.94) | 0.862 | 0.889 | 0.852 | 0.875 | 0.742 |
| DINOv3 fine-tuned cues | 55 | 8 | 10 | 51 | 0.855 (0.79-0.92) | 0.846 | 0.873 | 0.836 | 0.859 | 0.710 |
| always "flooded" | 63 | 0 | 61 | 0 | 0.508 (0.33-0.65) | 0.508 | 1.000 | 0.000 | 0.674 | 0.000 |

**Production cloud rule: 694 training roads, then 104 validation roads (56 flooded) on 34 tiles**
| arm | TP | FN | FP | TN | accuracy (95% CI) | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| base (no DINO) | 50 | 6 | 15 | 33 | 0.798 (0.71-0.87) | 0.769 | 0.893 | 0.688 | 0.826 | 0.598 |
| **base + DINOv2 cues (production)** | 52 | 4 | 15 | 33 | **0.817** (0.72-0.89) | 0.776 | 0.929 | 0.688 | 0.846 | 0.642 |
| base + DINOv3 cues (frozen) | 50 | 6 | 13 | 35 | 0.817 (0.72-0.90) | 0.794 | 0.893 | 0.729 | 0.840 | 0.635 |
| base + DINOv2 cues + DINOv3 head cues | 54 | 2 | 8 | 40 | 0.904 (0.83-0.97) | 0.871 | 0.964 | 0.833 | 0.915 | 0.810 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | 55 | 1 | 10 | 38 | 0.894 (0.82-0.96) | 0.846 | 0.982 | 0.792 | 0.909 | 0.797 |
| base + DINOv3 head cues | 54 | 2 | 10 | 38 | 0.885 (0.81-0.96) | 0.844 | 0.964 | 0.792 | 0.900 | 0.775 |
| **base + DINOv3 fine-tuned cues** | 55 | 1 | 8 | 40 | **0.913** (0.85-0.97) | 0.873 | 0.982 | 0.833 | 0.924 | 0.832 |
| DINOv2 cues | 44 | 12 | 21 | 27 | 0.683 (0.59-0.78) | 0.677 | 0.786 | 0.562 | 0.727 | 0.359 |
| DINOv3 cues (frozen) | 44 | 12 | 18 | 30 | 0.712 (0.61-0.81) | 0.710 | 0.786 | 0.625 | 0.746 | 0.417 |
| DINOv3 head cues | 49 | 7 | 7 | 41 | 0.865 (0.81-0.93) | 0.875 | 0.875 | 0.854 | 0.875 | 0.729 |
| DINOv3 fine-tuned cues | 52 | 4 | 10 | 38 | 0.865 (0.81-0.93) | 0.839 | 0.929 | 0.792 | 0.881 | 0.732 |
| always "flooded" | 56 | 0 | 48 | 0 | 0.538 (0.36-0.69) | 0.538 | 1.000 | 0.000 | 0.700 | 0.000 |

**Paired tests on the same validation roads** (whole tiles resampled; exact McNemar)
| arm | against | tile rule: difference (95% CI), fixed / broken, p | cloud rule: difference (95% CI), fixed / broken, p |
|---|---|---|---|
| base + DINOv2 + fine-tuned cues | production | +0.057 (+0.000 to +0.125), 8 / 1, **p = 0.039** | +0.077 (+0.000 to +0.179), 10 / 2, **p = 0.039** |
| base + DINOv2 + head cues | production | +0.048 (-0.018 to +0.132), 8 / 2, p = 0.11 | +0.086 (+0.000 to +0.194), 11 / 2, **p = 0.023** |
| base + fine-tuned cues | production | +0.040 (-0.018 to +0.113), 6 / 1, p = 0.13 | **+0.096 (+0.028 to +0.188), 10 / 0, p = 0.002** |
| base + fine-tuned cues | base + frozen DINOv3 cues | +0.048 (-0.031 to +0.131), 9 / 3, p = 0.15 | **+0.096 (+0.017 to +0.185), 11 / 1, p = 0.006** |
| base + head cues | base + frozen DINOv3 cues | +0.057 (+0.000 to +0.131), 10 / 3, p = 0.092 | +0.067 (-0.019 to +0.169), 11 / 4, p = 0.12 |
| base + frozen DINOv3 cues | production | -0.008 (-0.038 to +0.031), 3 / 4, p = 1.00 | +0.000 (-0.039 to +0.058), 3 / 3, p = 1.00 |
| base + DINOv2 + fine-tuned | base + DINOv2 + head | +0.008 (-0.045 to +0.056), 4 / 3, p = 1.00 | -0.010 (-0.045 to +0.020), 1 / 2, p = 1.00 |
| fine-tuned cues alone | DINOv2 cues alone | **+0.105 (+0.013 to +0.202), 21 / 8, p = 0.024** | **+0.183 (+0.080 to +0.300), 27 / 8, p = 0.002** |
| fine-tuned cues alone | frozen DINOv3 cues alone | **+0.161 (+0.062 to +0.269), 29 / 9, p = 0.002** | **+0.154 (+0.055 to +0.266), 21 / 5, p = 0.003** |
| head cues alone | frozen DINOv3 cues alone | **+0.177 (+0.083 to +0.281), 32 / 10, p = 0.0009** | **+0.154 (+0.048 to +0.267), 23 / 7, p = 0.005** |
| frozen DINOv3 cues alone | DINOv2 cues alone | -0.057 (-0.186 to +0.070), 20 / 27, p = 0.38 | +0.029 (-0.049 to +0.123), 17 / 14, p = 0.72 |

**Reading:**
- A flood head trained on the published flooded attribute turns DINOv3's tokens into much better per-road evidence
  than the label-free change cues. Alone, its cues are 10-18 points above the DINOv2 or DINOv3 change cues.
- Added to the classical pipeline, the gain is 4-10 points.
- Most of the gain is already there with the head on **frozen** tokens. Fine-tuning the last 2 blocks adds nothing
  detectable on top (-1.0 to +0.8 points).
- Against production, only one arm meets the library's stage rule (interval above 0 and p < 0.05): base +
  fine-tuned cues on the cloud-rule roads. The other rows against production with p < 0.05 have intervals that touch
  0.

**Post-hoc check: roads that continue from a training tile** (`posthoc_shared_roads.py`, written after these
results; it refits the arms and reproduces the accuracies above)
- **The overlap:** a SpaceNet 8 road is an OSM way, and a way can cross a tile edge. **87 of the 124** (tile rule)
  and **77 of the 104** (cloud rule) validation roads share their way id, and with it the flooded label, with a road
  on a training tile.
- **Where the gains fall:**

  | road set | validation roads | base + fine-tuned vs production (fixed / broken) | base + DINOv2 + fine-tuned vs production (fixed / broken) |
  |---|---|---|---|
  | cloud rule, way also on a training tile | 77 | 10 / 0 | 10 / 2 |
  | cloud rule, way not on a training tile | 27 | 0 / 0 | 0 / 0 |
  | tile rule, way also on a training tile | 87 | 4 / 1 | 4 / 1 |
  | tile rule, way not on a training tile | 37 | 2 / 0 | 4 / 0 |

- **Inference:** the head may partly learn local appearance that carries across the tile edge along the same road
  and the same water. Every arm that learns from training roads can profit from that; a trained head has more room
  to do so.
- **What would settle it:** the 37 / 27 independent roads are too few to tell. Settling it needs a spatially
  blocked split (for example by before-scene region, 0 / 2, or blocks of neighbouring tiles), or the sealed test
  areas.
- **Status:** the Track B gain is a promising lead, not a confirmed result.

### Pictures (`evidence/pilot_scripts/dinov3/`; imagery: Maxar via SpaceNet 8)
- **`phase2_flood_maps_2_15_48.png`:** the validation tile with the most flooded roads (13 flooded, all its roads).
  It shows before, after, the frozen DINOv2 and DINOv3 patch change, and P(flooded) on the road strips from the
  head on frozen tokens and from the fine-tuned model (mean of the 5 fold models, none trained on this tile).
  - Both trained heads call nearly every strip flooded, which is right here.
  - The head on frozen tokens leaves two short side streets at the upper left low (blue). The fine-tuned model
    leaves one.
  - The frozen change maps, by contrast, are high on open ground and low along some flooded streets.
- **`phase2_cells_0_14_7.png`:** the validation tile with the most labelled roads. It shows every cell for the linear
  head on frozen tokens and for the fine-tuned model.
  - Frozen head: precision 0.75, recall 0.64. Fine-tuned: precision 0.81, recall 0.86.
  - Fine-tuning fills in the side streets the frozen detectors miss (blue in phase 1). Its false road cells are
    driveways and yards next to roads, not the rail / levee line.
- **`phase2_loss_curves.png`:** training and inner-validation loss per epoch, for all four inner runs.

### Run time and checkpoints
- **Phase 2 wall clock:** 5,662 s (94 min) on the Mac GPU.
  - A-head 473 s; A-ft 1,632 s (20 epochs of about 68 s).
  - B-head strip tokens 186 s, training 8 s.
  - B-ft 2,889 s: inner run 6 epochs of about 105 s, then 5 folds x 3 epochs, plus predictions.
  - Pictures 30 s.
- **Frozen trunk cache:** 1,285 s for the after images. The before images were cached in phase 1.
- **Checkpoints:** in `~/Masters/models/finetuned/dinov3_sat493m/`, outside every repo.
  - Trained parameters only: `trackA_A-ft.pt`, `trackA_A-head.pt`, `trackB_ft_inner.pt`, `trackB_ft_fold{0-4}.pt`,
    `trackB_head_fold{0-4}.pt`.
  - With them, the trunk cache `trunk20_c0d6dac062e8/` (about 7.5 GB).
- **Licence:** the checkpoints are research-only. They derive from DINOv3 (Meta DINOv3 License) and were trained on
  SpaceNet 8 (CC BY-SA 4.0).

### Phase 2 caveats
- **One validation split**: 40 tiles, about 110 roads. The Track B intervals are wide (±7-10 points).
- **The road-continuity overlap** above. A spatially blocked check, or the sealed test, is needed before any claim.
- **The fine-tuning was cut down to fit the shared Mac GPU:**
  - 2 trained blocks;
  - one window per tile per epoch;
  - no augmentation;
  - a fixed learning rate (not tuned).

  A-head stopped at its epoch cap while still improving, so its 0.681 understates a linear probe.
- **Not a library candidate** (Justin's decision; DINOv3 License). The finding for the library: a **trained flood head
  on frozen tokens** carried most of the Track B gain. A DINOv2 flood head (Apache-2.0) is the open-model version to
  test next.

## Files
- **Plan:** `outputs/preregistration_dinov3_baseline.md` (and its phase 2 section).
- **Code (research only):** `evidence/pilot_scripts/dinov3/`.
  - `dinov3_bench.py`: loader, `tokens3`, cues, cell features, pictures.
  - `run_phase1.py`: driver; `make_tables.py`: these tables.
  - `dinov3_finetune.py`: the trunk cache, shared with phase 2.
- **Numbers:** `dinov3/phase1_numbers.json` (every table, times, code hashes). Per-road held-out calls:
  `phase1_calls_891.csv`. Track A validation probabilities: `phase1_trackA_val.npz`.
- **Logs:** `features_trackB.log`, `features.log`, `trackA2.log`, `trackB.log`, `phase1.log`.
- **Caches** (not in any repo): `dinov3/.cache/` (road tokens, cell basis and features, detector arms) and
  `~/Masters/models/finetuned/dinov3_sat493m/trunk20_c0d6dac062e8/` (frozen blocks 1-20; before images float32, after
  images float16).
- **Phase 2:**
  - `dinov3_finetune.py`: networks, targets, training loop.
  - `run_phase2.py`: driver (its smoke mode uses random targets).
  - `phase2_numbers.json`: tables, loss curves, settings, times.
  - `phase2_cues.csv`: per-road head and fine-tuned cues.
  - `phase2.log`; `posthoc_shared_roads.py` / `.json` / `.csv`.
  - `tables_phase2.md`.
- **GeoAI-Roads:** HEAD at the run was `55c8fc2` (another agent's commits since 1532e9a). No module was edited and
  nothing was committed for this benchmark; the module hashes are in the numbers file.
