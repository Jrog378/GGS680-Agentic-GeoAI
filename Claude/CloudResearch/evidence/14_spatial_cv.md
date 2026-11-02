# 14: Spatially blocked cross-validation (2026-10-26; EXPLORATORY, development data only)

Our own measurements, not literature. Agent B's part of the plan (classical + DINOv2, CPU). Agent C's DINOv3 runs
are reported separately.

**Why:** Justin (2026-10-26): "can you do a cross validation so that you dont overfit". Until now every flood-per-road
number came from tile folds. Under tile folds a held-out road can share its road id, and so its label, with a training
road on the next tile (58.6% of held-out roads at seed 662), and neighbouring tiles flood together. Method: Roberts et
al. 2017, *Ecography* 40(8) 913–929, block cross-validation with blocks larger than the dependence range.

**Setup:**
- **Plan:** `outputs/preregistration_spatial_cv.md`, written 18:40 EDT, before any model was scored on the new folds.
  This note follows its "Agent B" and "Decision rules" sections. Changes are listed under **Deviations**.
- **Folds:** `evidence/pilot_scripts/spatial_cv/spatial_folds.py` (sha256 `6ab96c29666193235477…`, imported, not
  edited). 63 grid blocks of 1,751 m (3 x 3 tiles). Purge route: in each fold, training roads whose id occurs among
  the fold's held-out roads are dropped. `StratifiedGroupKFold(5)` by block, seed 662, then seeds 1–20.
- **Schemes:**
  - **S**: spatial blocks, purged (primary);
  - **SB**: S plus a buffer (no training road on a tile next to a held-out tile);
  - **T**: tile folds, made exactly as each arm was logged;
  - **Tdev**: tile folds split over all 1,037 roads;
  - **TM**: size-matched tile folds (Tdev folds with training sets cut at random to the size of S's);
  - **L**: 7 x 7-tile blocks (4,085 m).
- **Scripts** (all in `evidence/pilot_scripts/spatial_cv/`):
  - `scv_common.py`: the factorial's setup, copied, plus a CPU process pool;
  - `spatial_cv_flood.py`: fits for (a), (b), (c);
  - `spatial_cv_nested.py`: (e);
  - `spatial_cv_trackA.py`: (f);
  - `spatial_cv_score.py`: every metric, interval, paired test and decision rule (no fitting);
  - `spatial_cv_figures.py`: the pictures.
- **Outputs:** `spatial_cv_numbers.json` (every number below), `spatial_cv_calls.csv` (every road: masks, block, folds
  and the seed-662 call of every arm and scheme), `spatial_cv_seeds.csv` (per arm, scheme, road set and seed), the
  call caches (`spatial_cv_flood_calls.npz`, `spatial_cv_nested.npz`, `spatial_cv_trackA_probs.npz`), the logs and
  `figures/`.
- **Model and data:**
  - Every flood arm keeps its logged model (the tuned forest), columns and gate; only the folds change.
  - Data: Louisiana-East train + val only, 226 tiles, 1,037 roads (468 flooded). Every script asserts
    `set(roads.split) <= {"train", "val"}`. Published labels, unmodified.
  - Not read: test tiles, the north negative set, Germany, Louisiana-West, the HRC_WHU test images.
    `allow_held_out` was never passed, and `split_summary` was never called.
  - The label folder was opened directly once by mistake (one training tile); see Deviations.
- **Compute:** CPU only, cached tables only (a cache miss stops a script). Agent C had the GPU.
  - Flood fits ran in 5–6 processes, one core per forest, leaving 2 cores for Agent C.
  - Run times:
    - flood fits 668 s;
    - nested 4,487 s, plus about 200 s in the stopped first attempt;
    - Track A 8,238 s, plus 290 s for `road_prior`.
- **Registry:** `production.json` has sha256 `c3295b2069c2bf63…` before and after every script. Nothing was
  promoted or written.

## In short
**Evidence (measured):**
1. **Tile folds overstate accuracy by about 4 points.**
   - Production on its 798 roads: **82.51% ± 0.61 under tile folds, 78.58% ± 0.80 under spatial folds** (seed 662:
     83.0 [79.4–86.4] against 79.2 [73.3–84.5]).
   - The optimism gap is **+3.93 points [+2.33, +5.96]**, positive in 21 of 21 seeds.
   - The best combo (production + DINOv2 vector, on the 891): **84.74% ± 0.68 against 80.66% ± 0.72**, gap +4.07
     [+2.64, +6.04].
   - Every one of the 16 factorial arms loses 4.1–5.1 points.
2. **The gap is leakage and nearness, not the smaller training sets.**
   - The smaller training sets cost only +0.25 [−0.04, +0.61] (production) and +0.22 [+0.01, +0.46] (best combo).
     That is Tdev minus size-matched tile folds.
   - Leakage + nearness (TM − S) is +3.92 [+2.38, +6.01] and +3.94 [+2.45, +5.93].
3. **The DINOv2 vector is still the one tool that helps under spatial folds:** main effect +1.33 [+0.36, +2.36],
   21 of 21 seeds (tile folds: +1.25).
   - Two arms beat production on the seed-averaged S interval: production gate + vector, +1.16 [+0.21, +2.16], and
     spotter gate + vector, +1.51 [+0.09, +3.06].
   - **No arm passes the promotion rule at seed 662 under S** (best: +1.98 [+0.00, +4.10], p = 0.086). So by the
     plan's rule no gain counts.
   - He 2011 now costs accuracy: −1.14 [−2.23, −0.20].
4. **Nested spatial CV, the honest accuracy of "pick the best combo": 80.05% ± 0.81 on the 757 shared roads**,
   against production's 78.98% under S.
   - That is +1.08, with a seed-averaged interval of [−0.20, +2.39]: not significant.
   - It is 78.86% on the 798 (+0.29 [−1.64, +1.92]).
   - Picking after the fact overstates it by 0.43 [−0.94, +0.01].
   - 94 of the 105 picks carry the vector; 11 different arms win somewhere.
5. **Re-chosen with S numbers, the optimal combo is unchanged:** production gate · no de-hazing · + DINOv2 vector,
   80.13% ± 0.71.
6. **Thin-cloud groups under S are clustered.**
   - Trusted flooded (24): 0 / 4 / 3 / 1 / 16 per fold. Production finds 18 = 75.0% [33.3, 90.7] at seed 662, 76.8%
     on average.
   - Dry-labelled (69): 22 / 4 / 25 / 17 / 1. Production calls 12 = 17.4% [6.9, 31.7] flooded, 19.3% on average
     (tile folds: 10.4%).
   - Control (175): 29 / 24 / 50 / 45 / 27. Production gets 131 = 74.9% [65.7, 83.9] right.
   - Clear-sky benchmark (95): 9 / 22 / 22 / 18 / 24. Production finds 78 = 82.1% [72.6, 90.0].
7. **The 1.75 km blocks pass Roberts' test:** production's held-out errors correlate 0.08 at 0–1 km and 0.03 at
   1–2 km.
8. **Track A road finding shows no optimism.**
   - F1 on held-out val-split cells at the fixed 0.75: **0.685 [0.627, 0.745] under T, 0.681 [0.609, 0.757] under S**;
     T − S +0.004 [−0.011, +0.019].
   - Both are below the logged train → val 0.713, because recall drops to about 0.60.
   - The nested cut-off was not run (compute: projected 4.35 h against a 3-hour budget).

**Inference (not measured):**
- Every tile-fold number in `13_pipeline_factorial.md` and earlier is about 4 points optimistic. The ranking of the
  tools mostly survives, but no gain is strong enough to pass the rule once the neighbours are gone.
- The model partly learned each neighbourhood's flood answer. Under S it is wrong across whole areas, in one
  direction: the problem is area shift.

## 1. Reproduction checks (run first; each script stops if one fails)
| Check | Logged | Reproduced |
|---|---|---|
| (a) production, T split over the 798 | 394 / 47 / 89 / 268 (83.0%), `everything_together_calls.csv` A798 | yes, call for call |
| (a) production, Tdev | 390 / 51 / 91 / 266, the factorial's production calls on the 798 | yes, call for call |
| (b) best combo, T split over the 891 | 409 / 56 / 80 / 346, `everything_together_calls.csv` B891 | yes, call for call |
| (c) all 16 arms refitted at seed 662 under the factorial's tile folds | `pipeline_factorial_seed_calls.npz` (itself = `pipeline_factorial_calls.csv`) | yes, all 16, call for call |
| (c) T scoring | the factorial's seed-662 accuracy intervals, paired intervals and McNemar p, and its 21-seed means | yes (same tile resamples) |
| (a) under S and SB | must equal (c)'s production arm on the 798, because subsets inherit the block folds | yes, 21 seeds (S) and seed 662 (SB) |
| (e) refit of each picked arm | must equal the (c) S fit of that arm in that outer fold | yes, all 105 |
| (f) Track A, train → val at 0.75 | 7,580 cells called road, precision 0.696, recall 0.732, F1 0.713 (dino_cells_test, 2026-10-23T173707) | yes: 7,580, 0.696, 0.732, 0.713 |
| Cached tables | the factorial's cue caches: `road_corrected_darkref_c1fd17d88e15c874.csv`, `road_corrected_dehaze_49f162b007e4c30f.csv` | cache hits, the same files |
| `production.json` | sha256 `c3295b2069c2bf63…` | unchanged after every script |

## 2. (a) Production on its 798 kept roads
Production is the tuned forest on the 96 production columns, fitted on the 798 roads its gate keeps (441 flooded, 357
dry). Seed 662; percent with 95% intervals (2,000 resamples of tiles for T, Tdev and TM; of 3 x 3 blocks for S and
SB; of 7 x 7 blocks for L). The last column is the accuracy over the 21 fold seeds.

| Scheme | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC | Mean ± SD (min–max), 21 seeds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T (split over the 798, as logged) | 394 | 47 | 89 | 268 | 83.0 (79.4–86.4) | 81.6 (76.0–86.3) | 89.3 (85.2–93.1) | 75.1 (67.9–81.6) | 85.3 (81.2–88.8) | 0.655 (0.582–0.725) | 82.51 ± 0.61 (81.6–84.2) |
| Tdev (split over the 1,037) | 390 | 51 | 91 | 266 | 82.2 (78.6–85.7) | 81.1 (75.6–85.8) | 88.4 (84.4–92.4) | 74.5 (67.4–81.3) | 84.6 (80.6–88.0) | 0.640 (0.565–0.712) | 82.75 ± 0.48 (82.1–83.7) |
| TM (size-matched tile folds) | 393 | 48 | 88 | 269 | 83.0 (79.2–86.5) | 81.7 (76.1–86.5) | 89.1 (84.8–93.1) | 75.4 (68.1–81.9) | 85.2 (81.2–88.8) | 0.655 (0.575–0.728) | 82.50 ± 0.59 (81.5–83.6) |
| **S (spatial blocks, primary)** | 378 | 63 | 103 | 254 | **79.2 (73.3–84.5)** | 78.6 (67.8–86.2) | 85.7 (77.8–91.0) | 71.1 (60.3–80.3) | 82.0 (73.5–87.8) | 0.578 (0.462–0.677) | **78.58 ± 0.80 (76.4–80.1)** |
| SB (S + buffer) | 379 | 62 | 108 | 249 | 78.7 (72.7–84.1) | 77.8 (66.7–85.7) | 85.9 (77.3–92.2) | 69.7 (58.5–79.7) | 81.7 (73.0–87.5) | 0.568 (0.445–0.671) | 77.32 ± 1.01 (75.7–79.2) |
| L (7 x 7 blocks) | 381 | 60 | 124 | 233 | 76.9 (70.8–82.5) | 75.4 (60.5–84.8) | 86.4 (77.5–93.3) | 65.3 (47.3–79.8) | 80.5 (69.7–86.3) | 0.533 (0.401–0.640) | 77.23 ± 0.35 (76.9–77.7) |

**The optimism gap, split into its parts** (same 798 roads; points; seed-averaged intervals resample 3 x 3 blocks):

| Difference | Seed 662 [95% CI] | right only in the first / only in the second; McNemar p | Mean (SD) over 21 seeds | Min to max | Seeds > 0 / < 0 | Seed-averaged 95% CI |
|---|---|---|---|---|---|---|
| **T − S (the optimism gap)** | +3.76 [+1.97, +6.21] | 49 / 19; p = 0.0004 | **+3.93 (1.06)** | +1.75 to +6.64 | 21 / 0 | **+2.33, +5.96** |
| T − Tdev (own split against the split over the 1,037) | +0.75 [−0.69, +2.09] | 22 / 16 | −0.24 (0.92) | −1.88 to +1.63 | 9 / 12 | −0.71, +0.13 |
| **Tdev − TM: smaller training sets** | −0.75 [−2.08, +0.61] | 10 / 16 | **+0.25 (0.53)** | −0.75 to +1.13 | 14 / 5 | **−0.04, +0.61** |
| **TM − S: leakage + nearness** | +3.76 [+1.38, +6.97] | 51 / 21; p = 0.0005 | **+3.92 (0.97)** | +1.63 to +6.14 | 21 / 0 | **+2.38, +6.01** |
| S − SB (the buffer) | +0.50 [−2.06, +2.98] | 34 / 30 | +1.25 (0.77) | −0.75 to +2.51 | 20 / 1 | +0.28, +2.50 |
| S − L (larger blocks) | +2.26 [+0.00, +4.96] | 42 / 24; p = 0.036 | +1.34 (0.92) | −0.50 to +3.13 | 20 / 1 | −0.58, +3.61 |

**Measured:**
- Production's tile-fold accuracy is about 4 points too high: 82.5% under T, 78.6% under S, gap +3.93 [+2.33, +5.96],
  in 21 of 21 seeds.
- Almost none of the gap is the smaller training set. Size-matched tile folds keep 82.5%, and Tdev − TM is +0.25
  [−0.04, +0.61]. The whole gap sits in TM − S: +3.92 [+2.38, +6.01].
- Under S, production loses recall (89.3 to 85.7) and specificity (75.1 to 71.1). Both move.
- The buffer costs another 1.25 points [+0.28, +2.50]. The 7 x 7 blocks cost 1.34, with an interval that includes 0.

## 3. (b) The best combo so far on the 891 tile-rule roads
Production + the DINOv2 change vector (16 PCs fitted inside each training fold), fitted on the 891 tile-rule roads
(465 flooded, 426 dry).

| Scheme | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC | Mean ± SD (min–max), 21 seeds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T (split over the 891, as logged) | 409 | 56 | 80 | 346 | 84.7 (81.3–88.1) | 83.6 (78.4–88.4) | 88.0 (83.2–92.0) | 81.2 (75.3–86.7) | 85.7 (81.7–89.1) | 0.694 (0.626–0.759) | 84.74 ± 0.68 (83.7–86.1) |
| Tdev | 412 | 53 | 80 | 346 | 85.1 (81.7–88.3) | 83.7 (78.5–88.5) | 88.6 (84.2–92.3) | 81.2 (75.4–86.8) | 86.1 (82.2–89.4) | 0.701 (0.633–0.764) | 84.82 ± 0.39 (84.0–85.3) |
| TM | 410 | 55 | 80 | 346 | 84.8 (81.5–88.0) | 83.7 (78.3–88.4) | 88.2 (83.2–92.0) | 81.2 (75.3–86.7) | 85.9 (81.9–89.3) | 0.697 (0.629–0.759) | 84.60 ± 0.48 (83.5–85.5) |
| **S** | 401 | 64 | 100 | 326 | **81.6 (76.6–85.9)** | 80.0 (69.6–86.9) | 86.2 (78.3–91.6) | 76.5 (66.9–84.3) | 83.0 (74.3–88.4) | 0.632 (0.530–0.709) | **80.66 ± 0.72 (78.8–81.7)** |
| SB | 396 | 69 | 107 | 319 | 80.2 (74.9–85.0) | 78.7 (67.2–86.3) | 85.2 (76.9–90.8) | 74.9 (65.3–83.1) | 81.8 (72.6–87.7) | 0.605 (0.493–0.692) | 79.51 ± 0.76 (78.1–80.8) |
| L | 404 | 61 | 118 | 308 | 79.9 (74.0–85.0) | 77.4 (62.3–86.4) | 86.9 (77.6–93.4) | 72.3 (58.3–83.7) | 81.9 (70.9–87.8) | 0.600 (0.483–0.692) | 80.09 ± 0.24 (79.9–80.5) |

| Difference (891 roads) | Seed 662 [95% CI] | Mean (SD), 21 seeds | Seeds > 0 | Seed-averaged 95% CI |
|---|---|---|---|---|
| **T − S (optimism gap)** | +3.14 [+1.07, +5.75], 43 / 15, p = 0.0003 | **+4.07 (0.92)** | 21 | **+2.64, +6.04** |
| Tdev − TM: smaller training sets | +0.22 [−0.56, +1.16] | +0.22 (0.42) | 14 | +0.01, +0.46 |
| TM − S: leakage + nearness | +3.25 [+1.26, +5.72] | +3.94 (0.98) | 21 | +2.45, +5.93 |
| S − SB | +1.35 [+0.00, +2.94] | +1.15 (0.65) | 20 | +0.09, +2.35 |
| S − L | +1.68 [−0.22, +4.26] | +0.58 (0.72) | 17 | −1.15, +2.62 |

**Against production on the same 798 roads, scheme by scheme** (paired; tiles resampled for T, Tdev, TM, blocks for
S, SB, L at seed 662; seed-averaged intervals resample 3 x 3 blocks for every scheme):

| Scheme | (b) − production, seed 662 [95% CI] | fixed / broken | McNemar p | Rule at 662 | Mean gain, 21 seeds (above / equal / below) | Seed-averaged 95% CI | Rule passes (of 21) |
|---|---|---|---|---|---|---|---|
| T | +1.25 [−0.28, +2.97] | 25 / 15 | 0.15 | no | +1.58 (20 / 0 / 1) | +0.44, +2.84 | 7 |
| Tdev | +2.38 [+0.84, +4.02] | 31 / 12 | 0.0054 | yes | +1.40 (21 / 0 / 0) | +0.27, +2.58 | 9 |
| TM | +1.38 [−0.14, +2.99] | 26 / 15 | 0.12 | no | +1.49 (21 / 0 / 0) | +0.42, +2.65 | 9 |
| **S** | **+1.88 [−0.15, +4.42]** | 35 / 20 | 0.058 | **no** | **+1.45 (20 / 1 / 0)** | **−0.01, +3.10** | **3** |
| SB | +0.88 [−1.51, +3.40] | 32 / 25 | 0.43 | no | +1.40 (21 / 0 / 0) | −0.16, +3.17 | 1 |
| L | +2.51 [+0.54, +5.04] | 35 / 15 | 0.0066 | yes | +2.36 (21 / 0 / 0) | +0.46, +4.32 | 12 |

**Measured:**
- The best combo also drops about 4 points under S: 84.7% to 80.7%, gap +4.07 [+2.64, +6.04].
- Against production on the 798 under S, it is +1.88 points at seed 662 [−0.15, +4.42], p = 0.058. The rule does not
  pass. It is higher in 20 of 21 seeds (equal in 1), by +1.45 on average, but the seed-averaged interval just touches
  0 (−0.01, +3.10).
- Under the 7 x 7 blocks (L) its gain is larger, +2.36 [+0.46, +4.32], and the rule passes at seed 662. L is a
  sensitivity arm, not the primary.

## 4. (c) The 16-arm pipeline factorial under spatial folds (757 shared roads, 431 flooded)
Same arms, gates, columns and model as `13_pipeline_factorial.md`; only the folds change. T is the logged factorial
(read from `pipeline_factorial_seed_calls.npz`). "vs production" is the seed-662 S difference with a 5,000-resample
block interval, roads fixed / broken and exact McNemar. The seed-averaged gain resamples 3 x 3 blocks (2,000).
Ranked by the S mean.

| Arm (gate · cues · features) | Tools | S seed 662 [95% CI] | S mean ± SD (min–max) | S splits > / = / < production | T mean | Gap T − S [seed-avg CI] | vs production, S 662 [CI]; fixed / broken; p | S seed-averaged gain [CI] | Rule (S 662; seeds) |
|---|---|---|---|---|---|---|---|---|---|
| spotter · none · + vector | 2 | 80.2 [74.4–85.3] | **80.49 ± 0.77** (78.3–81.6) | 21 / 0 / 0 | 84.55 | +4.06 [+2.32, +6.44] | +0.7 [−1.0, +2.3]; 28 / 23; 0.58 | **+1.51 [+0.09, +3.06]** | no; 1/21 |
| spotter · two-date · + vector | 3 | 79.7 [73.8–84.7] | 80.14 ± 0.73 (79.0–81.8) | 20 / 0 / 1 | 84.40 | +4.26 [+2.54, +6.52] | +0.1 [−1.7, +2.0]; 31 / 30; 1.0 | +1.16 [−0.41, +2.79] | no; 2/21 |
| **production · none · + vector** | 1 | 80.3 [74.6–85.3] | **80.13 ± 0.71** (78.3–81.8) | 20 / 0 / 1 | 84.48 | +4.35 [+2.61, +6.68] | +0.8 [−0.6, +2.6]; 20 / 14; 0.39 | **+1.16 [+0.21, +2.16]** | no; 3/21 |
| production · two-date · + vector | 2 | 79.8 [74.0–84.9] | 79.93 ± 0.51 (78.7–80.8) | 18 / 0 / 3 | 84.20 | +4.27 [+2.64, +6.56] | +0.3 [−2.0, +2.5]; 30 / 28; 0.90 | +0.96 [−0.40, +2.31] | no; 1/21 |
| spotter · both + raw · + vector | 4 | 80.6 [75.0–85.5] | 79.79 ± 0.79 (78.3–80.8) | 16 / 2 / 3 | 84.56 | +4.77 [+2.87, +7.17] | +1.1 [−0.8, +3.4]; 30 / 22; 0.33 | +0.82 [−0.37, +2.00] | no; 1/21 |
| production · both + raw · + vector | 3 | 80.4 [74.5–85.9] | 79.73 ± 0.75 (78.1–81.0) | 17 / 3 / 1 | 84.42 | +4.69 [+2.81, +7.01] | +0.9 [−0.3, +2.5]; 22 / 15; 0.32 | +0.75 [−0.02, +1.57] | no; 2/21 |
| production · He 2011 · + vector | 2 | 80.8 [74.7–86.1] | 79.68 ± 0.93 (77.9–80.8) | 15 / 1 / 5 | 84.05 | +4.37 [+2.68, +6.73] | +1.3 [−1.0, +4.0]; 44 / 34; 0.31 | +0.70 [−0.75, +2.23] | no; 0/21 |
| spotter · He 2011 · + vector | 3 | 81.5 [75.6–86.3] | 79.59 ± 0.94 (77.8–81.5) | 16 / 1 / 4 | 84.54 | +4.95 [+3.08, +7.55] | +2.0 [+0.0, +4.1]; 41 / 26; 0.086 | +0.62 [−1.13, +2.38] | no; 0/21 |
| spotter · none · prod | 1 | 79.5 [73.6–84.9] | 79.32 ± 0.76 (77.3–80.3) | 12 / 2 / 7 | 83.76 | +4.44 [+2.81, +6.78] | +0.0 [−1.2, +1.5]; 17 / 17; 1.0 | +0.34 [−0.61, +1.23] | no; 1/21 |
| spotter · both + raw · prod | 3 | 79.7 [73.5–85.1] | 79.17 ± 0.73 (77.8–80.8) | 12 / 2 / 7 | 83.85 | +4.69 [+2.75, +7.13] | +0.1 [−1.5, +2.0]; 26 / 25; 1.0 | +0.19 [−0.81, +1.14] | no; 0/21 |
| production · both + raw · prod | 2 | 78.9 [72.9–84.3] | 79.05 ± 0.97 (76.9–80.6) | 10 / 1 / 10 | 83.63 | +4.58 [+2.63, +6.98] | −0.7 [−2.1, +1.1]; 13 / 18; 0.47 | +0.07 [−0.80, +0.83] | no; 2/21 |
| **production · none · prod (production)** | 0 | 79.5 [73.3–85.1] | **78.98 ± 0.73** (77.1–80.7) | — | 83.24 | **+4.26 [+2.64, +6.38]** | — | — | — |
| spotter · two-date · prod | 2 | 79.0 [72.9–84.4] | 78.78 ± 0.83 (77.0–80.3) | 9 / 1 / 11 | 83.22 | +4.43 [+2.75, +6.58] | −0.5 [−2.0, +1.2]; 22 / 26; 0.67 | −0.20 [−1.21, +0.81] | no; 0/21 |
| production · two-date · prod | 1 | 79.3 [72.9–85.0] | 78.51 ± 0.65 (77.0–79.4) | 5 / 0 / 16 | 82.75 | +4.24 [+2.62, +6.42] | −0.3 [−1.9, +1.5]; 19 / 21; 0.87 | −0.47 [−1.38, +0.37] | no; 0/21 |
| spotter · He 2011 · prod | 2 | 78.5 [72.2–83.9] | 77.57 ± 0.78 (75.6–78.6) | 1 / 0 / 20 | 82.71 | +5.13 [+3.08, +7.90] | −1.1 [−3.2, +1.3]; 33 / 41; 0.42 | −1.40 [−3.11, +0.04] | no; 0/21 |
| production · He 2011 · prod | 1 | 78.9 [72.6–84.3] | 77.50 ± 0.86 (76.1–78.9) | 0 / 0 / 21 | 82.10 | +4.60 [+2.79, +7.06] | −0.7 [−2.9, +1.8]; 36 / 41; 0.65 | **−1.48 [−2.92, −0.27]** | no; 0/21 |

**Measured:**
- **Every arm is 4.1 to 5.1 points worse under S** (seed means). Every gap interval is above 0.
- **No arm passes the promotion rule at seed 662 under S.** The closest is spotter · He 2011 · + vector, +2.0
  [+0.0, +4.1], p = 0.086. Over the 21 seeds no arm passes in more than 3.
- **Two arms beat production on the seed-averaged S interval:**
  - spotter · none · + vector, +1.51 [+0.09, +3.06];
  - production · none · + vector, +1.16 [+0.21, +2.16].
  - Neither passes the rule at seed 662, so by the plan's rule neither gain counts.
- **One arm is worse than production:** production · He 2011 · prod, −1.48 [−2.92, −0.27], 0 of 21 seeds above.
- On the 798, no gate-a arm passes at seed 662 either. Production + vector is +0.88 [−0.63, +2.76], p = 0.35.
- The arms move together: the S ranking is close to the T ranking, but every T mean is 4.1–5.1 points higher.

**Confusion matrices, S, seed 662** (757 shared roads; percent with block intervals):

| Arm | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| spotter · none · + vector | 389 | 42 | 108 | 218 | 80.2 (74.4–85.3) | 78.3 (67.8–85.6) | 90.3 (84.0–94.6) | 66.9 (54.6–77.2) | 83.8 (76.2–88.9) | 0.596 (0.477–0.691) |
| spotter · two-date · + vector | 384 | 47 | 107 | 219 | 79.7 (73.8–84.7) | 78.2 (67.7–85.6) | 89.1 (82.8–93.3) | 67.2 (54.9–77.8) | 83.3 (75.6–88.5) | 0.584 (0.463–0.684) |
| production · none · + vector | 384 | 47 | 102 | 224 | 80.3 (74.6–85.3) | 79.0 (69.0–86.2) | 89.1 (82.5–93.5) | 68.7 (56.6–79.0) | 83.8 (76.3–88.8) | 0.597 (0.482–0.695) |
| production · two-date · + vector | 382 | 49 | 104 | 222 | 79.8 (74.0–84.9) | 78.6 (68.4–85.8) | 88.6 (81.9–93.1) | 68.1 (55.4–78.9) | 83.3 (75.7–88.6) | 0.586 (0.467–0.688) |
| spotter · both + raw · + vector | 384 | 47 | 100 | 226 | 80.6 (75.0–85.5) | 79.3 (69.4–86.3) | 89.1 (82.6–93.9) | 69.3 (57.4–79.3) | 83.9 (76.3–89.0) | 0.602 (0.488–0.701) |
| production · both + raw · + vector | 382 | 49 | 99 | 227 | 80.4 (74.5–85.9) | 79.4 (69.5–86.6) | 88.6 (81.4–93.8) | 69.6 (57.7–79.8) | 83.8 (76.0–89.2) | 0.599 (0.478–0.703) |
| production · He 2011 · + vector | 383 | 48 | 97 | 229 | 80.8 (74.7–86.1) | 79.8 (69.8–86.8) | 88.9 (81.6–93.6) | 70.2 (58.5–80.3) | 84.1 (75.9–89.5) | 0.608 (0.485–0.709) |
| spotter · He 2011 · + vector | 390 | 41 | 99 | 227 | 81.5 (75.6–86.3) | 79.8 (69.5–86.8) | 90.5 (84.5–94.4) | 69.6 (57.9–79.5) | 84.8 (77.1–89.7) | 0.622 (0.510–0.710) |
| spotter · none · prod | 379 | 52 | 103 | 223 | 79.5 (73.6–84.9) | 78.6 (68.2–86.0) | 87.9 (80.7–93.2) | 68.4 (56.5–78.8) | 83.0 (75.0–88.5) | 0.580 (0.457–0.684) |
| spotter · both + raw · prod | 379 | 52 | 102 | 224 | 79.7 (73.5–85.1) | 78.8 (68.4–86.2) | 87.9 (80.4–93.3) | 68.7 (56.7–79.2) | 83.1 (74.9–88.6) | 0.583 (0.457–0.690) |
| production · both + raw · prod | 372 | 59 | 101 | 225 | 78.9 (72.9–84.3) | 78.6 (68.4–86.0) | 86.3 (78.4–92.0) | 69.0 (56.4–79.5) | 82.3 (74.3–88.0) | 0.566 (0.440–0.674) |
| **production** | 375 | 56 | 99 | 227 | 79.5 (73.3–85.1) | 79.1 (68.4–86.6) | 87.0 (79.5–92.3) | 69.6 (57.8–79.7) | 82.9 (74.5–88.5) | 0.580 (0.449–0.686) |
| spotter · two-date · prod | 379 | 52 | 107 | 219 | 79.0 (72.9–84.4) | 78.0 (67.6–85.7) | 87.9 (80.5–92.9) | 67.2 (54.5–78.2) | 82.7 (74.4–88.2) | 0.569 (0.442–0.673) |
| production · two-date · prod | 377 | 54 | 103 | 223 | 79.3 (72.9–85.0) | 78.5 (68.2–86.2) | 87.5 (79.7–92.8) | 68.4 (56.3–79.1) | 82.8 (74.7–88.5) | 0.574 (0.446–0.687) |
| spotter · He 2011 · prod | 374 | 57 | 106 | 220 | 78.5 (72.2–83.9) | 77.9 (67.0–85.6) | 86.8 (79.5–92.2) | 67.5 (55.1–77.9) | 82.1 (73.6–87.8) | 0.558 (0.429–0.665) |
| production · He 2011 · prod | 373 | 58 | 102 | 224 | 78.9 (72.6–84.3) | 78.5 (67.5–86.1) | 86.5 (78.5–92.3) | 68.7 (56.1–79.0) | 82.3 (73.8–88.1) | 0.566 (0.435–0.676) |

- Under T, every arm called 80–92 dry roads flooded (`13_pipeline_factorial.md` §2). Under S it is 97–108. The
  block intervals are about 1.5 times as wide as the tile intervals.

**Buffered folds (SB), seed 662, shared roads:** production 79.5 [73.4–84.9]. Every other arm is at or below
production, from +0.3 (spotter · none · + vector) to −3.2 (production · He 2011 · prod, p = 0.0079). Seven arms
are significantly below production at seed 662 (p < 0.05), all of them without the vector, plus both "both + raw +
vector" arms. Every row is in the JSON under `(c) … paired against production … SB`.

### Main effects and interactions under S (shared roads, points)
Seed-averaged intervals resample 3 x 3 blocks. The T column recomputes the logged factorial's effects with the same
block resampling, so the two columns compare like with like (the logged tile-resampled intervals are narrower).

| Contrast | S: seed 662 [95% CI] | S: mean (SD) over seeds | S: > 0 / < 0 | **S: seed-averaged 95% CI** | Matters under S | T: mean [seed-averaged block CI] |
|---|---|---|---|---|---|---|
| main: spotter gate | +0.08 [−0.84, +0.98] | +0.17 (0.32) | 15 / 5 | −0.65, +0.98 | no | +0.34 [−0.23, +0.90] |
| main: two-date | −0.46 [−1.45, +0.46] | −0.39 (0.51) | 4 / 17 | −1.10, +0.26 | no | −0.36 [−1.11, +0.31] |
| **main: He 2011** | +0.03 [−1.30, +1.51] | **−1.14 (0.52)** | 1 / 20 | **−2.23, −0.20** | **yes (worse)** | −0.66 [−1.59, +0.19] |
| main: both + raw | +0.00 [−0.85, +0.96] | −0.29 (0.39) | 4 / 15 | −1.14, +0.38 | no | +0.11 [−0.41, +0.59] |
| **main: DINOv2 vector** | +1.27 [+0.22, +2.39] | **+1.33 (0.24)** | **21 / 0** | **+0.36, +2.36** | **yes** | +1.25 [+0.37, +2.22] |
| vector within the production gate | +1.22 | +1.36 (0.46) | 21 / 0 | +0.39, +2.38 | yes | +1.36 [+0.48, +2.32] |
| vector within the spotter gate | +1.32 | +1.29 (0.28) | 21 / 0 | +0.27, +2.38 | yes | +1.13 [+0.25, +2.12] |
| He within the spotter gate | +0.13 | −1.32 (0.61) | 1 / 20 | −2.46, −0.32 | yes (worse) | −0.53 [−1.45, +0.36] |
| He without the vector | −0.86 | −1.61 (0.67) | 0 / 21 | −3.04, −0.37 | yes (worse) | −1.09 [−2.28, −0.08] |
| He with the vector | +0.92 | −0.67 (0.64) | 2 / 18 | −1.65, +0.22 | no | −0.22 [−1.06, +0.57] |
| interaction He 2011 x vector | +1.78 | +0.94 (0.81) | 17 / 2 | −0.19, +2.05 | no | +0.87 [+0.17, +1.64] |
| interaction both + raw x vector | +0.53 | −0.51 (0.66) | 6 / 13 | −1.10, −0.02 | yes | −0.27 [−0.92, +0.37] |
| other interactions (gate x de-hazer, gate x vector, two-date x vector) | | −0.35 to +0.23 | | all include 0 | no | all include 0 |

**Measured:**
- **The vector is still the one tool that helps:** +1.33 [+0.36, +2.36] under S, against +1.25 under T. It is
  positive in 21 of 21 splits under either gate.
- **He 2011 now costs accuracy:** −1.14 [−2.23, −0.20] (T: −0.66, interval including 0). It costs most without the
  vector (−1.61) and under the spotter gate (−1.32).
- The spotter gate's main effect halves, to +0.17 [−0.65, +0.98].
- The He x vector interaction no longer clears 0 (−0.19, +2.05). "Both + raw x vector" now does, at −0.51
  [−1.10, −0.02].

### The optimal combo, re-chosen with S numbers (the factorial's preregistered rule)
- **Top arm by S mean:** spotter · none · + vector, 80.49% (2 tools).
- **Ties:** arms with fewer tools whose seed-averaged block interval against the top includes 0. Only one:
  production · none · + vector (1 tool), 80.13%, top minus it +0.35 [−0.74, +1.42].
  - Production itself (0 tools) is not a tie: top minus production +1.51 [+0.09, +3.06].
- **Chosen: production gate · no de-hazing · + DINOv2 vector**, the same arm the tile folds chose. Its S mean is
  80.13% ± 0.71.
- Under T the rule had 8 ties; under S it has 1. The block intervals are wider, but the S means spread out more
  (77.50 to 80.49, against 82.10 to 84.56).

## 5. (d) The four thin-cloud groups under S
Production's road rule defines the groups (as in the factorial). Count and share at seed 662 with a 5,000-resample
**block** interval (one generator over the four groups in order, as the factorial), the S mean over 21 seeds and the
logged T mean. Per-fold counts are the measure's count in each S fold at seed 662.

**Where the groups sit (seed 662, S folds 1–5):**

| Group | Roads | Tiles | Blocks | Roads per S fold | Roads per T fold |
|---|---|---|---|---|---|
| Trusted flooded, thin cloud (found) | 24 | 13 | 9 | 0 / 4 / 3 / 1 / 16 | 2 / 0 / 12 / 6 / 4 |
| Dry-labelled, thin cloud (called flooded) | 69 | 29 | 14 | 22 / 4 / 25 / 17 / 1 | 6 / 17 / 12 / 21 / 13 |
| Control, same tiles (right) | 175 | 32 (of the 39 thin-cloud tiles) | 19 | 29 / 24 / 50 / 45 / 27 | 23 / 29 / 41 / 40 / 42 |
| Clear-sky benchmark (found) | 95 | 23 | 13 | 9 / 22 / 22 / 18 / 24 | 20 / 8 / 19 / 28 / 20 |

**Shares, S at seed 662 [block 95% CI]; S mean over 21 seeds; logged T mean:**

| Arm | Trusted flooded: found (24) | Dry-labelled: called flooded (69) | Control: right (175) | Clear-sky benchmark: found (95) |
|---|---|---|---|---|
| **production** | 18 = 75.0% [33.3, 90.7]; S 76.8; T 72.6 | 12 = 17.4% [6.9, 31.7]; S 19.3; T 10.4 | 131 = 74.9% [65.7, 83.9]; S 72.3; T 77.6 | 78 = 82.1% [72.6, 90.0]; S 79.4; T 85.6 |
| production · none · + vector | 19 = 79.2% [36.4, 93.8]; S 81.5; T 80.4 | 9 = 13.0% [3.8, 28.0]; S 15.9; T 7.6 | 135 = 77.1% [67.4, 87.7]; S 74.9; T 78.5 | 80 = 84.2% [71.7, 93.7]; S 82.2; T 85.2 |
| production · two-date · prod | 20 = 83.3% [50.0, 96.0]; S 83.7; T 84.9 | 33 = 47.8% [18.8, 73.2]; S 51.6; T 39.9 | 126 = 72.0% [61.4, 84.3]; S 69.6; T 74.9 | 79 = 83.2% [70.4, 92.3]; S 82.6; T 84.4 |
| production · two-date · + vector | 20 = 83.3%; S 85.7; T 86.1 | 29 = 42.0%; S 44.4; T 19.7 | 129 = 73.7%; S 72.5; T 77.6 | 79 = 83.2%; S 82.8; T 85.1 |
| production · He 2011 · prod | 21 = 87.5% [54.5, 100]; S 88.9; T 91.3 | 20 = 29.0% [10.0, 46.6]; S 28.6; T 17.3 | 132 = 75.4%; S 73.6; T 77.2 | 84 = 88.4% [80.7, 94.5]; S 85.1; T 88.4 |
| production · He 2011 · + vector | 22 = 91.7% [66.6, 100]; S 88.5; T 90.9 | 15 = 21.7%; S 23.9; T 11.0 | 139 = 79.4% [70.1, 89.4]; S 75.3; T 78.9 | 86 = 90.5% [80.8, 97.6]; S 85.7; T 88.7 |
| production · both + raw · prod | 20 = 83.3%; S 85.9; T 84.1 | 12 = 17.4%; S 20.0; T 10.3 | 135 = 77.1%; S 73.9; T 78.7 | 82 = 86.3%; S 83.7; T 87.8 |
| production · both + raw · + vector | 20 = 83.3%; S 85.7; T 84.9 | 12 = 17.4%; S 18.7; T 8.3 | 139 = 79.4% [71.0, 88.6]; S 74.9; T 79.2 | 83 = 87.4%; S 83.4; T 87.5 |
| spotter · none · prod | 22 = 91.7%; S 88.3; T 89.5 | 31 = 44.9% [22.7, 61.9]; S 40.6; T 19.7 | 127 = 72.6%; S 72.4; T 77.7 | 83 = 87.4%; S 87.1; T 89.8 |
| spotter · none · + vector | 23 = 95.8% [78.6, 100]; S 90.9; T 90.9 | 35 = 50.7% [25.3, 72.1]; S 36.1; T 13.4 | 130 = 74.3%; S 74.3; T 77.8 | 84 = 88.4%; S 87.9; T 89.9 |
| spotter · two-date · prod | 21 = 87.5%; S 87.3; T 87.1 | 42 = 60.9% [33.9, 82.3]; S 64.6; T 54.3 | 123 = 70.3%; S 69.5; T 73.7 | 81 = 85.3%; S 86.3; T 89.3 |
| spotter · two-date · + vector | 22 = 91.7%; S 88.7; T 88.5 | 38 = 55.1%; S 55.8; T 35.0 | 127 = 72.6%; S 73.0; T 76.7 | 82 = 86.3%; S 87.8; T 90.7 |
| spotter · He 2011 · prod | 22 = 91.7%; S 90.1; T 91.5 | 42 = 60.9% [36.2, 79.1]; S 64.3; T 50.9 | 126 = 72.0%; S 71.5; T 75.0 | 85 = 89.5%; S 88.8; T 91.1 |
| spotter · He 2011 · + vector | 22 = 91.7%; S 91.5; T 92.1 | 41 = 59.4%; S 54.7; T 33.3 | 127 = 72.6%; S 73.1; T 76.9 | 84 = 88.4%; S 88.3; T 90.8 |
| spotter · both + raw · prod | 21 = 87.5%; S 89.5; T 90.1 | 35 = 50.7%; S 46.1; T 23.4 | 128 = 73.1%; S 72.6; T 76.8 | 84 = 88.4%; S 88.6; T 91.4 |
| spotter · both + raw · + vector | 21 = 87.5%; S 88.9; T 90.1 | 34 = 49.3%; S 42.4; T 17.1 | 129 = 73.7%; S 73.8; T 77.4 | 85 = 89.5% [81.1, 95.9]; S 89.1; T 91.5 |

Every interval, the min and max over seeds and the per-fold counts of every arm are in the JSON under `(d)`.

**Per-fold counts at seed 662** (production; the measure's count in S folds 1–5):
- Trusted flooded found: 0 / 3 / 1 / 0 / 14 of 0 / 4 / 3 / 1 / 16. Spotter · none · + vector: 0 / 4 / 3 / 0 / 16.
- Dry-labelled called flooded: 1 / 0 / 8 / 3 / 0 of 22 / 4 / 25 / 17 / 1. Spotter · none · + vector: 12 / 4 / 18 / 1 / 0.
- Control right: 22 / 21 / 36 / 29 / 23 of 29 / 24 / 50 / 45 / 27.
- Benchmark found: 6 / 20 / 18 / 12 / 22 of 9 / 22 / 22 / 18 / 24.

**Group main effects under S** (seed mean, seed-averaged block interval, splits > 0):

| Contrast | Trusted flooded: found | Dry-labelled: called flooded | Control: right | Benchmark: found |
|---|---|---|---|---|
| main: spotter gate | +4.8 [+1.6, +14.9], 21/21 | **+22.8** [+12.9, +30.5], 21/21 | −0.8 [−5.5, +3.1] | +4.9 [+2.3, +8.8], 21/21 |
| main: two-date | +2.0 [−1.6, +12.2] | **+26.1** [+12.7, +36.3], 21/21 | −2.3 [−6.0, +1.0] | +0.7 [−3.2, +4.1] |
| main: He 2011 | +5.4 [+1.3, +16.1], 20/21 | +14.9 [+5.9, +23.2], 21/21 | −0.1 [−3.9, +3.2] | +2.8 [+0.1, +7.0], 21/21 |
| main: both + raw | +3.1 [−0.5, +10.9] | +3.8 [+1.5, +5.9], 21/21 | +0.3 [−1.4, +2.6] | +2.0 [+0.5, +4.4], 19/21 |
| main: DINOv2 vector | +1.4 [+0.4, +3.5], 19/21 | −5.4 [−7.8, −3.0], 0/21 | **+2.1** [+0.5, +3.5], 21/21 | +0.7 [−0.7, +2.2] |
| interaction gate x He 2011 | −8.3 [−28.0, −2.1] | +12.5 [+4.5, +20.2] | −1.9 [−3.6, +0.4] | −3.5 [−7.9, +1.3] |
| interaction gate x two-date | −7.1 [−27.2, −1.2] | −8.6 [−19.5, +6.6] | +0.4 [−1.2, +1.9] | −2.3 [−5.5, +1.0] |

**Measured:**
- **The groups are clustered, so one fold carries them.** At every one of the 21 seeds, 16 of the 24 trusted flooded
  roads (67%) fall in one fold and one fold has none. They sit on 13 tiles in 9 blocks, and two blocks hold 9 and 6
  of them. One fold holds 29–45% of the 69 dry-labelled roads (two blocks hold 16 and 11 of them).
- **Production under S finds 76.8% of the trusted flooded roads (T: 72.6%).** The interval at seed 662 is
  33.3–90.7%, because 14 of the 18 found sit in fold 5.
- **Production calls 19.3% of the dry-labelled roads flooded under S, against 10.4% under T.** Every arm calls more of
  them flooded under S. The spotter arms rise the most: spotter · none · + vector goes from 13.4% to 36.1%.
- **The spotter gate's extra flooded calls on dry-labelled roads grow:** +22.8 points under S, +15.3 under T.
- **On the clear roads the tools behave as under T:** the spotter gate still finds +4.9 more of the benchmark
  (21 / 21), and the vector keeps +2.1 more controls right (21 / 21).

## 6. (e) Nested spatial CV: the honest accuracy of "pick the best combo"
- **What was run:** `nested_spatial_folds(1,037 roads, s)` at all 21 seeds (inner seed = outer seed).
  - In each of the 5 outer folds, every one of the 16 arms ran a 5-fold inner spatial CV on the outer-training roads
    only: 8,400 forests.
  - The pick was the highest pooled inner accuracy on the inner held-out shared roads. Arms within 0.005 of the top
    tied, and ties went to the fewest tools.
  - The picked arm was refitted on all outer-training roads its gate keeps and called the outer held-out roads.
- **Check:** every one of the 105 refits equals the (c) S fit of the picked arm in that fold, call for call.
- **Run time:** 4,487 s on 5 processes, while Agent C loaded the machine (load average 13–36).

**The nested accuracy against production under S** (same roads, same folds):

| Road set | Nested, seed 662 [block CI] | Nested mean ± SD (min–max), 21 seeds | Production S mean | Seeds above / equal / below | Nested − production, seed 662 [CI]; fixed / broken; p | **Seed-averaged nested − production [CI]** | Rule passes |
|---|---|---|---|---|---|---|---|
| **757 shared** | 79.5 [73.4–84.8] | **80.05 ± 0.81** (78.6–81.8) | 78.98 | 19 / 1 / 1 | +0.0 [−2.3, +2.1]; 29 / 29; 1.0 | **+1.08 [−0.20, +2.39]** | 2 / 21 |
| 798 production kept | 78.5 [72.3–83.9] | 78.86 ± 0.94 (76.9–80.6) | 78.58 | 11 / 3 / 7 | −0.8 [−3.5, +1.6]; 32 / 38; 0.55 | +0.29 [−1.64, +1.92] | 1 / 21 |

Seed 662, 757 shared roads: TP 386, FN 45, FP 110, TN 216; precision 77.8, recall 89.6, specificity 66.3, F1 83.3,
MCC 0.582 (0.463–0.680).

**The selection optimism** (nested minus the arm that is best after the fact, spotter · none · + vector, S mean
80.49% on the shared roads):

| Road set | Nested − best single arm, mean over seeds | Seed-averaged 95% CI | Seed 662 | Nested − the re-chosen optimal combo (production · none · + vector) |
|---|---|---|---|---|
| 757 shared | −0.43 | −0.94, +0.01 | −0.66 | −0.08 [−0.99, +0.71] |
| 798 production kept | −0.45 | −0.90, −0.04 | −0.63 | −0.78 [−2.72, +0.52] |

**Which arm won where** (`spatial_cv_nested_picks.csv`, figure 5):
- Spotter · none · + vector 42 of 105 outer folds; spotter · two-date · + vector 22; production · none · + vector 14;
  production · two-date · + vector 7; production · He 2011 · + vector 6; spotter · none · prod 5; spotter · He 2011 ·
  + vector 3; spotter · two-date · prod 3; production, production · two-date · prod and production · both + raw ·
  prod 1 each.
- **94 of the 105 picks carry the DINOv2 vector.** Production itself was picked once.
- The pick changes from fold to fold and seed to seed. No arm wins all 5 outer folds of any seed. On average 1.9 arms
  tie within 0.005 of the top.

**Measured:**
- **The honest estimate of "pick the best combo" is 80.05% ± 0.81 on the shared roads** (78.86% on production's 798).
- It is above production in 19 of 21 seeds, by +1.08 on average. But the seed-averaged interval includes 0
  (−0.20, +2.39), and at seed 662 it ties production (29 fixed, 29 broken). The rule does not pass.
- Picking the best arm after the fact overstates it by about 0.4 points (−0.43 [−0.94, +0.01]).
- On the 798 the nested pick gains nothing: +0.29 [−1.64, +1.92].
- *Inference:* 75 of the 105 picks use the spotter gate, which never trains on the 41 roads only production keeps.
  That may be why the pick does worse on production's own roads.

## 7. (f) Track A road finding (is a 2 m cell road?)
- **Detector:** `classical_models()["Random forest"]` (300 trees), on production's detector features: 12 classical
  cell features + the 32 DINOv2 cell PCs. Cut-off fixed at production's 0.75.
- **Cells:** `cell_table("train")` (205,581 cells, 25.0% road, road-enriched) + `cell_table("val")` (338,885 cells,
  2.1% road, uniform), pooled: 544,466 cells on the 226 development tiles.
  - S = `cell_folds` (each cell in its tile's block fold). T = `StratifiedGroupKFold(5, shuffle=True, 662)` by tile
    over the pooled cells, as `oof_probabilities` does.
- **Real road share:** `road_prior("train")` = 0.02206, for the secondary weights and the nested cut-off.
- **Run:**
  - reproduction fit 188 s; 10 pooled fold fits of 633–1,010 s each (load average 13–36 from Agent C); 8,238 s in all.
  - **Nested cut-off at seed 662: not run (compute).** The script projected 25 inner fits at 4.35 h, over the 3-hour
    budget.
  - **Seeds 1–20: not run (compute).**
- **Limitation:** the DINOv2 cell basis (32 PCs, label-free) stays as cached. It was fitted on the 186 training
  tiles' patch tokens, which include tiles that S holds out. The tokens are not cached, so a per-fold refit would need
  the GPU.

| Seed 662 | F1 on held-out val-split cells [95% CI] (primary) | Precision | Recall | Cells called road | Weighted F1, all held-out cells [95% CI] (secondary) |
|---|---|---|---|---|---|
| Logged train → val split (reproduction check) | 0.713 | 0.696 | 0.732 | 7,580 | — |
| T (tile folds; tiles resampled) | **0.685 [0.627, 0.745]** | 0.783 | 0.609 | 5,600 | 0.661 [0.624, 0.695] |
| **S (spatial folds; blocks resampled)** | **0.681 [0.609, 0.757]** | 0.790 | 0.598 | 5,457 | 0.655 [0.611, 0.696] |
| **T − S (same cells, paired block resamples)** | **+0.004 [−0.011, +0.019]** | | | | +0.006 [−0.000, +0.013] |

- F1 on val-split cells per S fold: 0.591 / 0.786 / 0.701 / 0.630 / 0.615. Per T fold: 0.696 / 0.757 / 0.658 / 0.675
  / 0.618. Fold k is a different area under T and under S.
- Intervals: 2,000 resamples (seed 662) of the groups of the scored cells. The secondary F1 weights each not-road cell
  by (1 − real) / real x sampled / (1 − sampled), with sampled = the pooled road share (0.108), as `f1_cutoff` does.

**Measured:**
- **Road finding shows no detectable optimism under spatial folds:** T − S is +0.004 [−0.011, +0.019] on the
  primary F1, and +0.006 [−0.000, +0.013] on the secondary.
- Both pooled-CV F1s (0.68) are below the logged train → val F1 (0.713). Recall falls from 0.73 to about 0.60, and
  precision rises from 0.70 to about 0.79, under T and S alike.
- Under S the fold F1s spread more: 0.59–0.79, against 0.62–0.76.

**Inference:**
- A cell's road label depends on its own pixels, and cells carry no road id, so little leaks between tiles. Road
  appearance transfers across the area; flood status does not.
- The fixed 0.75 cut-off was chosen for a detector trained on road-enriched train-split cells (25% road). The pooled
  training sets are about 11% road, because val-split cells are 2% road, so the forest's probabilities are lower and
  0.75 calls too few cells. A cut-off chosen inside each fold (the nested arm) would correct for this. It was not run
  (compute).

## 8. Residual dependence check (production, S, seed 662)
Moran-type correlation of held-out errors (1 = wrong) between production's 798 roads on different tiles with
different road ids, by tile-centroid distance band. These are the label correlogram's bands and pair rule
(`spatial_folds._correlogram`). The labels on the same 798 roads are shown for reference.

| Band (km) | 0–1 | 1–2 | 2–3 | 3–4 | 4–6 | 6–8 | 8–12 | 12–16 | 16–24 |
|---|---|---|---|---|---|---|---|---|---|
| **Errors under S** | **0.081** | **0.034** | −0.030 | −0.062 | −0.001 | 0.021 | −0.013 | −0.017 | 0.005 |
| Errors under T (comparison) | 0.072 | 0.035 | −0.023 | −0.068 | −0.000 | 0.012 | −0.021 | −0.004 | 0.005 |
| Errors under L (comparison) | 0.097 | 0.034 | −0.005 | −0.049 | 0.008 | 0.024 | −0.024 | −0.025 | 0.003 |
| Flood labels on the 798 (reference) | 0.40 | 0.26 | 0.13 | 0.13 | 0.08 | 0.17 | −0.17 | −0.14 | −0.02 |

**Measured:**
- The held-out errors are barely correlated at any distance: 0.08 at 0–1 km, 0.03 at 1–2 km and within ±0.07 beyond.
  The labels themselves correlate 0.40 at 0–1 km.
- The errors under T and L look the same. Production is wrong on 20.8% of the 798 under S. There are 11,759 road
  pairs in the 0–1 km band.

**Inference:**
- **The 1.75 km blocks pass Roberts' test.** The residual dependence is below 0.1 already in the first band, so
  blocks of 1.75 km are larger than its range. The 7 x 7 blocks (L) are not needed for independence. Their training
  sets are larger, not smaller (770 roads per fold on average, against 707), so their further −1.34 (interval
  including 0) is more likely extrapolation: each held-out region is larger and farther from the training roads.
- **The leak is not in the errors; it is in the training set.** Under T the errors are no more clustered, yet T is
  4 points higher. What T gives the model is a training road with the same id (58.6% of held-out roads) or on the next
  tile. So a residual correlogram alone would not have shown the optimism; the purge and the blocks were needed.

## 9. Decision-rule verdicts (promotion rule on S only; `production.json` not written)
The rule: gain > 0, a 95% block interval above 0 and exact McNemar p < 0.05 at seed 662, against production on the
same roads (`sn8_stages.confirm`). A gain counts only if its seed-averaged S interval also excludes 0.

| Candidate (roads) | S gain, seed 662 [95% CI] | McNemar p | Rule at 662 | Seed-averaged S gain [95% CI] | Rule passes, 21 seeds | **Counts?** |
|---|---|---|---|---|---|---|
| production · none · + vector (757) | +0.79 [−0.65, +2.64] | 0.39 | no | +1.16 [+0.21, +2.16] | 3 | no |
| spotter · none · + vector (757) | +0.66 [−1.01, +2.32] | 0.58 | no | +1.51 [+0.09, +3.06] | 1 | no |
| spotter · He 2011 · + vector (757) | +1.98 [+0.00, +4.10] | 0.086 | no | +0.62 [−1.13, +2.38] | 0 | no |
| every other factorial arm (757) | −1.06 to +1.32 | ≥ 0.31 | no | −1.48 to +1.16, every interval reaching 0 or below | 0–2 | no |
| (b) best combo on the 891, scored on the 798 | +1.88 [−0.15, +4.42] | 0.058 | no | +1.45 [−0.01, +3.10] | 3 | no |
| (e) nested pick (757) | +0.00 [−2.27, +2.09] | 1.0 | no | +1.08 [−0.20, +2.39] | 2 | no |
| (e) nested pick (798) | −0.75 [−3.49, +1.60] | 0.55 | no | +0.29 [−1.64, +1.92] | 1 | no |

- **Nothing passes the promotion rule under spatial folds.** Production stays as it is.
- **The factorial's optimal combo, re-chosen with S numbers, is still production gate · no de-hazing · + DINOv2
  vector** (§4). Its honest S estimate is 80.13% ± 0.71 on the shared roads, against production's 78.98%.
- **The number to quote for "the best combo" is the nested one: 80.05% ± 0.81** on the 757 shared roads (78.86% on
  production's 798). That is +1.08 over production, with a seed-averaged interval of −0.20 to +2.39, which includes 0.
- Track A: see §7. No McNemar test is used on cells.

## 10. Pictures (`evidence/pilot_scripts/spatial_cv/figures/`)
1. **`arms_T_vs_S.png`:** every arm's accuracy under T (orange) and S (blue): the min to max over 21 seeds (bar),
   the mean (dot) and seed 662 (black diamond). Production is shaded.
   - Every arm's S range sits wholly left of its T range.
   - The vector arms still lead under S, but all 16 arms fit between 77.5% and 80.5%.
2. **`optimism_gap.png`:**
   - Left: T − S per arm, with the seed-averaged block interval and seed 662. Every bar is 3.9–5.1 points, and every
     interval is clear of 0.
   - Right: the gap of (a) and (b) split into its parts. The smaller training set (Tdev − TM) is +0.25 and +0.22;
     leakage + nearness (TM − S) is +3.92 and +3.94.
3. **`confusion_T_vs_S.png`:** production and the best S arm (spotter · none · + vector) on the 757 shared roads at
   seed 662.
   - Production goes from 46 to 56 missed floods and from 87 to 99 false floods.
   - The best S arm goes from 29 to 42 missed and from 85 to 108 false.
4. **`errors_map_correlogram.png`:**
   - Left: production's held-out errors under S at seed 662, per tile, coloured by the tile's S fold, with the
     1.75 km blocks outlined.
   - Right: the correlogram of held-out errors under S and T, with the labels' correlogram for reference.
5. **`nested_picks.png`:** the arm the inner CV picked in each outer fold and seed, with its inner accuracy. Blue
   (spotter · none · + vector) and orange (spotter · two-date · + vector) dominate. 94 of 105 picks carry the vector.
6. **`trackA_T_vs_S.png`:** Track A F1 on held-out val-split cells, per fold and pooled, under T and S at seed 662,
   with the logged train → val F1 (dashed).
   - The pooled values overlap.
   - The nested cut-off panel is replaced by a note: not run (compute).

## 11. What goes wrong, and why (with the pictures)
1. **Tile folds let the answer leak in from the next tile** (`optimism_gap.png`, `arms_T_vs_S.png`).
   - *Measured:* every arm is 3.9–5.1 points lower under S, in 21 of 21 seeds.
   - *Measured:* the gap is not the smaller training set. The smaller training sets cost only +0.25 [−0.04, +0.61]
     for production (Tdev − TM); leakage + nearness (TM − S) is +3.92 [+2.38, +6.01].
   - *Inference:* under T, 58.6% of held-out roads have a training road with the same OSM id and label on the next
     tile. Roads on neighbouring tiles flood together (label correlation 0.40 at under 1 km on the 798). So part of
     what the model "knew" was the neighbourhood's answer, not the road's imagery.
2. **Without that help the model misses more floods and calls more false floods** (`confusion_T_vs_S.png`).
   - *Measured:* production goes from 46 missed / 87 false to 56 missed / 99 false on the shared roads (seed 662).
     Specificity falls from 73.3% to 69.6% and recall from 89.3% to 87.0%.
   - The best S arm loses more specificity, 73.9% to 66.9%: it calls 108 of 326 dry roads flooded.
3. **The errors differ by area, not road by road** (`errors_map_correlogram.png`).
   - *Measured:* at seed 662, fold 2 has 32 false floods and 4 misses. Fold 4 has 26 misses and 25 false floods.
     Fold 1 has 9 and 8.
   - *Measured:* between tiles the errors barely correlate: 0.08 at 0–1 km, against 0.40 for the labels.
   - *Inference:* the flood pattern changes from area to area. A model fitted elsewhere is wrong across whole patches
     of a held-out area, in one direction. This is a shift between areas, not leftover pairwise dependence, so larger
     blocks would not remove it.
4. **Thin-cloud tools call far more of the dry-labelled hazy roads flooded once the neighbours are gone** (§5).
   - *Measured:* production goes from 10.4% to 19.3%, and spotter · none · + vector from 13.4% to 36.1%.
   - The spotter gate's main effect on these roads rises from +15.3 to +22.8 points.
   - Two folds hold 47 of the 69 roads, so the shares lean on two areas.
   - *Inference:* under T, the same-id twins of these roads in training carried their "dry" label. The labels of these
     roads cannot be trusted under cloud, so these extra calls may be found floods or false alarms. The labels cannot
     say which.
5. **He 2011 cues now cost accuracy:** −1.14 [−2.23, −0.20] under S.
   - *Inference:* the de-hazed copies add 96 noisy columns. With near neighbours in training the forest could ignore
     them; without, they mislead it.
6. **The pick is unstable** (`nested_picks.png`).
   - *Measured:* 11 different arms win at least one outer fold. The 8 vector arms sit within 0.9 points of each
     other under S (79.59–80.49%), so a different area picks a different arm.
   - *Measured:* the honest gain of picking is +1.08 [−0.20, +2.39], not significant.
7. **Track A loses recall at the fixed cut-off, under T and S alike** (`trackA_T_vs_S.png`).
   - *Measured:* recall is 0.61 (T) and 0.60 (S), against 0.73 in the logged train → val run, while T − S is only
     +0.004.
   - *Inference:* the problem is the cut-off's calibration (0.75 was tuned for 25%-road training sets; pooled ones are
     about 11% road), not spatial leakage.

## 12. What we do next to improve
- **Use S everywhere from now on.** Every candidate is scored with S folds and block intervals, and with nested
  spatial CV whenever a choice is made. Tile-fold numbers are no longer quoted for promotion or on slides.
  - That needs `spatial_folds` in the library and the `*_test` notebooks switched over. That is Justin's call.
- **Re-tune the flood forest under spatial folds.** Its settings (depth 10, sqrt features) were tuned with
  tile-grouped CV, which leaks, so they may be tuned to the leak. Then re-test the vector inside nested spatial CV.
- **The DINOv2 vector:** under S it is +1.16 [+0.21, +2.16] seed-averaged, but it fails the rule at seed 662
  (+0.79, p = 0.39). The next step is more power, not more arms:
  - fewer, pre-chosen arms (production against production + vector only);
  - the re-tuned forest;
  - then the sealed tiles once the candidate is frozen.
- **Area shift:** test, as an S arm, cues normalised within each tile or block (each road's change relative to its
  neighbourhood). Point 3 suggests whole areas are mis-calibrated.
- **Thin cloud:** the 69 dry-labelled hazy roads still need trustworthy labels (cloud-free reference or field data)
  before any cloud tool can be judged on them. Their spread over folds (22 / 4 / 25 / 17 / 1) means group results
  must be read per fold.
- **Track A:** run the nested cut-off when the Mac is free. It needs 25 inner forests: about 4.4 h at today's
  speed, less without Agent C's load. Then add the 20 extra seeds. Until then, the fixed 0.75 should not be used for
  detectors trained on pooled cells.

## What stays uncertain
- **These are still development roads.** Every arm has now been scored many times on them. The sealed tiles or a second
  event remain the test.
- **Distance matters past 1.75 km.** The 7 x 7 blocks are another 1.34 lower for production, and the interval includes
  0. A new event is farther away still, so the S numbers may still be optimistic for a new place.
- **The group results lean on one or two folds.** 16 of the 24 trusted flooded roads sit in one fold at every seed.
- **The size-matched control subsamples at random.** It matches the number of training roads, not their spread over
  the area.
- **Track A** has one seed and the fixed cut-off only. Its DINOv2 cell basis was fitted on patches from tiles that S
  holds out (label-free, but not refitted per fold).

## Deviations from the plan, and process notes (all times EDT, 2026-10-26)
1. **(c) reproduction refit (18:50, before any S fit).**
   - The plan says every arm under T must reproduce its logged calls. It also says (c)'s T is read from the `.npz`,
     not refitted.
   - To test the fitting code that makes the S calls, all 16 arms were refitted once, at seed 662 only, under the
     factorial's tile folds (80 forests). All 16 matched the `.npz` call for call.
   - Every T number in this note is still read from the logged `.npz`.
2. **Execution (not a model change).**
   - The flood forests ran in a pool of 5–6 CPU processes with `n_jobs=1` per forest; the logged models use
     `n_jobs=-1`.
   - The Track A forest ran at 6 threads, grown in warm-start steps of 50 trees whose probabilities are summed and
     whose trees are then freed. This was for memory: Agent C's GPU processes held 9–13 GB of the shared 16 GB.
   - Neither changes a tree. The flood reproduction checks match call for call. A chunked test fit matched a plain
     fit to 0.0 difference, and the Track A reproduction check matches the logged run exactly.
3. **Scoring crash and fix (19:01).**
   - The first scoring run stopped on an over-tight check: my McNemar p against the logged JSON value, which is
     rounded to 6 significant figures.
   - The check now allows a relative 1e-5, and the interval check ±0.0005. Then it was rerun.
   - Before the crash, the log had printed (a), (b) and (c)'s seed-662 accuracies. Nothing in the plan was changed.
4. **Resampling units.**
   - Seed-averaged intervals resample the 3 x 3 blocks for every scheme, L included. The plan says "resample
     blocks".
   - The (c) T effects in §4 are recomputed with block resampling, to compare like with like. The logged
     tile-resampled ones stay in `13_pipeline_factorial.md`.
5. **Error map at tile level.** No library road table holds road geometry, and the label folder is not opened
   directly. So figure 4 counts each tile's held-out errors and does not draw the roads.
6. **Track A reproduction check.** The logged Track A result is a train → val split (dino_cells_test,
   2026-10-23T173707), not tile folds. So the T check for (f) is that run: fit on all train-split cells, score the
   val-split cells at 0.75.
7. **Process slips (no sealed data touched).** The coordinator ruled that these are process slips, not data events,
   and they do not go in the data ledger.
   - **18:58:** I opened `ProjectBranch/Images/SN8_Louisiana-East_Ida2021/labels/0_10_2.geojson` (one training
     tile) myself and printed one road's properties and two coordinates. I was checking whether road geometry could
     be used for the error map. It was not used.
   - **19:03:50–19:04:40:** a first `road_prior("train")` call (the library's training-tile label read) was killed
     after about 40 s. Nothing was saved; its log is `spatial_cv_trackA_prior_attempt1_stopped.log`.
   - I stopped all work and reported. The coordinator ruled that library reads of train/val labels behind
     `guard_split`, such as `road_prior("train")`, are allowed, and that opening the label folder directly is not.
   - `road_prior("train")` was rerun from 19:08 to 19:13 (290 s): real road share 0.02206. No file in the label folder
     was opened directly after 18:58.
8. **Nested CV restart.**
   - The first nested run was stopped at 19:04, during the stop above, after 80 of 1,680 inner call sets.
   - It was resumed at 19:08 from `spatial_cv_nested.npz`, reusing those 80 call sets. The fits are deterministic.
   - The first log is kept as `spatial_cv_nested_attempt1_stopped.log`.
9. **Extra outputs beyond the plan:**
   - the residual correlogram under T and L, and of the labels on the 798 (JSON, figure 4);
   - the thin-cloud group contrasts under S (JSON, §5);
   - fold counts of every group at every seed (JSON).
