# Measured results so far: cloud in the roads side test (SpaceNet 8, Hurricane Ida)

Source: Justin Rogers's GGS 662 project, roads side test (`~/Masters/GGS662/ProjectBranch`, code in the private repo
Jrog378/GeoAI-Roads). Dev log: `~/Masters/GGS662/Project/docs/devlog.md`, entries of 2026-10-23. Development data only
(training + validation tiles); test tiles, the north negative set and the sealed areas (Germany, Louisiana-West) were
never read. These are our own measurements, not literature.

## Data and setting
- SpaceNet 8 Louisiana-East (Hurricane Ida, 2021): Maxar before and after RGB tiles, warped to one 0.5 m UTM grid,
  used in **greyscale only** after the first step. Roads are OpenStreetMap centrelines marked flooded or not.
- Split: 186 training / 40 validation / 40 test tiles (stratified on flood class), plus a north negative set.
  Touched (development) roads: 1,037 on 217 tiles with roads.
- The flood model: a random forest on per-road classical cues (intensity, edges, Hough, ridge), texture (GLCM, Gabor,
  LBP, Laws, wavelet, semivariogram) and frozen DINOv2 change cues, held out in 5 folds by tile.

## Labels under cloud
- SpaceNet 8's analysts were told to "only attribute what was visible" (Hänsch et al. 2022, p. 3), and the paper notes
  its baseline learned this rule (p. 6).
- In the label files of the 226 development tiles, a road feature's `flooded` attribute is "yes" (487 features) or left out
  (593); "no" never occurs (re-checked 2026-10-24 on train + val only). These 1,080 are label-file features; the 1,037
  roads are what the road builder keeps from them. So a
  road hidden by cloud reads as "not flooded": **under cloud a flooded label can be trusted, a dry label cannot.**
- Labelled flooded: 2% of roads on the 17 tiles with >= 20% thick cloud, 26% of scored roads under thin cloud, 55% of
  clear roads. In area 2, cloudy tiles have few flooded labels among heavily flooded clear neighbours (e.g. 0 of 7
  against 79%); in area 0 the neighbours are dry too (geography).

## Cloud masks (greyscale, after image)
- **bright** (the original tile rule): grey > 200 and smooth. Finds only opaque cloud cores.
- **dark**: the dark channel (darkest pixel within 20 m; He, Sun & Tang 2011) above an Otsu threshold learned on the
  training tiles (98 grey levels).
- **dark rise**: the dark channel's rise from before to after (Otsu threshold 71), so bright surfaces that were bright
  before too are not read as cloud. Neither dark mask flags floodwater on the most-flooded training tile.
- On the roads the tile rule scored (891), the dark-rise mask puts 93 roads (>= 20% of the strip) under cloud.
- **Checked against expert cloud labels** (HRC_WHU, Li et al. 2019; 120 development images, 0.5-15 m Google Earth RGB
  converted to greyscale; the 30 test images are sealed): bright mask precision 0.81, recall 0.28, F1 0.41; dark mask
  precision 0.62, recall 0.68, F1 0.65 (vegetation 0.78, water 0.74, urban 0.66; false alarms on bright barren ground,
  F1 0.48). The SpaceNet 8 threshold is near the best on HRC_WHU (F1 0.66 at 90). The two-date dark-rise mask cannot
  be checked on HRC_WHU (single date).
- Before images: no Louisiana-East before image is cloudy; an absolute dark-channel mask on them fires on bright calm
  water and bare ground instead.

## Effect of cloud on the flood calls
- Production's held-out calls on the 891 tile-rule roads: under thin cloud (dark rise >= 20% of the strip) it finds
  67% of the 24 flooded roads, against 87% in clear sky (Fisher p = 0.010, Holm p = 0.030 over three masks; the
  tile-resampled 95% interval, -0.54 to +0.001, just reaches 0). Dry roads under cloud are "kept dry" 94% of the time,
  inflated by the labelling rule.

## Ways of handling cloud (every touched road, 5 folds by tile; a rule's "cannot assess" roads neither fitted nor scored)
| rule | roads assessed | accuracy | flooded found | on the 766 roads all rules share, vs the tile rule |
|---|---|---|---|---|
| tile rule (original) | 891 | 81.8% | 85.8% | - |
| no cloud rule | 1,037 | 83.0% | 82.7% | -0.9 (p 0.31) |
| road rule (dark rise >= 20% of the strip) | 808 | 81.3% | 87.4% | +0.7 (p 0.38) |
| tile rule + road rule | 798 | 81.8% | 87.8% | +0.7 (p 0.36) |
| tile rule + cloud shares as features | 891 | 82.5% | 86.0% | +0.8 (p 0.21) |
| tile rule + de-hazed after image (He et al.) | 891 | 80.9% | 83.9% | -1.7 (p 0.15) |
- No rule changes accuracy significantly on the roads they share. De-hazing found 3 more of the 24 trusted flooded
  roads under cloud (n.s.); cloud as features found 2 fewer (the direction of learning the labelling rule). Roads
  handed back from cloudy tiles were called right only half the time.
- **Adopted (Justin, 2026-10-23): tile rule + road rule** for fitting and scoring, on validity grounds (labels under
  cloud cannot be trusted), not as an accuracy gain. Production on the 798 assessable roads: 83.0% (always "flooded"
  55.3%).

## Two-date de-hazing (exploratory; `sn8_refhaze.py`, Justin's idea of 2026-10-23)
- Model: in each 64 m window, after ~ alpha * before + beta on the pixels that did not change; with the dates' gain g, h
  from the tile's clear pixels, t = alpha / g and L = beta - t * h; haze only where 0.2 <= t <= 1 and L >= 0;
  corrected = (after - L) / t. Frozen flood model trained on clear roads.
- 24 trusted flooded roads under thin cloud: flooded found 70.8% as it is, 87.5% single-image (He; +4/-0, McNemar
  p 0.125), 83.3% two-date (+3/-0, p 0.25). 175 clear roads on the same tiles: 77.7%, 73.7%, 78.3%. These roads were
  looked at before, so this is exploratory.
- **Diagnostic (2026-10-24, before the slides): the fit is rough.** At 0.5 m the two dates barely agree pixel by
  pixel: clear-pixel correlation r = 0.46 on tile 2_19_55 and 0.09 on 2_15_45 (look angle, shadows, stripped trees,
  residual shift). So the least-squares slopes are diluted: g = 0.16 on 2_19_55 (an orthogonal fit gives 0.31) and
  local alpha is 0.03-0.05 everywhere. The fit then reads clear ground as hazy too (median t 0.32 on the clear
  pixels, 66% counted as haze), and about half of the cloud pixels fall below t = 0.2 and are left as they are
  (opaque). In the figure the bright core of the cloud stays; the haze over the roads is lifted. What it does is
  closer to a local contrast stretch than a haze estimate.
- **How the pilot was scored** (`evidence/pilot_scripts/evaluate.py`, saved from the session scratchpad on 2026-10-24;
  output `evaluate.log`, per-road calls `refhaze_calls.csv`):
  - roads: every touched development road; "thin cloud" = not on an opaque tile and >= 20% of the road strip under the
    dark-rise mask (93 roads on 39 tiles: 24 labelled flooded, 69 not); the control = the production-assessable roads
    (tile rule + road rule) on those same 39 tiles (175 roads);
  - model: the production random forest trained on clear roads only, 5 folds by tile; each arm recomputes every road
    feature (classical, GLCM, texture, DINOv2 cues) on its corrected after image;
  - per-arm changes against "as it is": flooded roads 3 fixed / 0 broken (two-date), 4 / 0 (He); dry-labelled roads
    0 / 3 (two-date), 0 / 16 (He); control roads 6 fixed / 5 broken (two-date, accuracy 77.7% -> 78.3%), 10 / 17 (He);
  - settings history: v1 used np.polyfit for the global fit (log `evaluate_v1_polyfit.log`, RankWarnings); v2 (the
    numbers above) replaced it with the closed-form fit and its guard, results otherwise identical.
- **Fix to pre-register (not tuned on these 24 roads):** fit the dates' relation on invariant pixels found by IR-MAD
  (Canty & Nielsen 2008) with an orthogonal fit, at a scale where the dates agree (coarser windows or smoothed
  images), then test once on roads not looked at.

## Revised two-date fit (2026-10-25; exploratory, label-free; `dark_reference_dehaze`, `refhaze_test.ipynb`)
Justin: the pilot's haze layer "is way too sensitive and catching houses as clouds".
- **Method:**
  - t = (A − dark after) ÷ (A − tone(dark before)), inside a cloud gate (dark-rise blobs ≥ 2,500 m²), fading out over
    20 m past it;
  - tone is a quantile match on clear pixels;
  - A is the brightest pixel among the 0.1% haziest;
  - t below 0.2 is opaque and left as it is;
  - no guided filter.
- **Synthetic haze, 94 clear development tiles** (He's model, t down to 0.35, A = 240; it follows the revised fit's own
  model, so it favours it):

  | Under the haze | as it is | pilot fit | revised fit |
  |---|---|---|---|
  | Grey error | 56.9 | 51.7 | 37.2 |
  | Detail kept | 0.82 | 0.92 | 1.02 |

  - The revised fit is closer on 89 of 94 tiles (sign test p = 6e-21).
  - Clear ground read as haze: 42% with the pilot fit, 0% with the revised fit (0% by design, because of the gate).
- **The single-image baseline (He et al. 2011, `dehaze`) on the same synthetic haze:**
  - grey error 27.3, lower than the two-date fit's 37.2;
  - detail kept 0.84;
  - clear ground read as haze 85%.

  The two-date fit has the higher error because it only corrects inside the cloud gate, so faint haze outside the
  dark-rise mask (t above about 0.63 here) stays uncorrected.
- **Guided filter on t, chosen on the even-position tiles and reported on the odd ones:**
  - detail kept 0.68 with it, 1.04 without;
  - grey error 37.3 with it, 38.1 without.
  - So it is off: with the hazy image as its guide, it made t follow the texture.
- **Real cloud, local contrast in 5 m windows under the gate:**

  | Tile | before (toned) | after | corrected | r(before, corrected) |
  |---|---|---|---|---|
  | 2_23_44 | 7.4 | 2.1 | 3.5 | 0.05 |
  | 2_19_55 | 5.8 | 3.1 | 4.5 | 0.31 |
  | 0_18_13 | 10.6 | 3.1 | 6.3 | 0.25 |

  - The brightness comes back.
  - Ground detail comes back only partly (2_19_55, 0_18_13) or hardly at all (2_23_44, the slide tile).
- **Example tile, picked by a label-free rule:** the road with the most metres under thin cloud (481 m, way/847378248 on
  2_23_44). The handle step on that tile:
  - the road is CORRECT (71% of its strip in the gate, 16% opaque);
  - two roads are ASSESS.
- **Not scored on roads.** That test is to be pre-registered first.

## Two-date de-hazing on the flood calls (2026-10-25; exploratory; plan written first: `outputs/preregistration_twodate_roads.md`)
- **Setup:**
  - code GeoAI-Roads 2ec5346;
  - `evidence/pilot_scripts/evaluate_twodate.py`, with its log and `twodate_calls.csv` / `twodate_numbers.json`;
  - 93 roads under thin cloud on 39 development tiles;
  - production flood model, 5 folds by tile, trained on the assessable roads;
  - run time 16 minutes.

| Roads | as it is | single image (He) | two-date |
|---|---|---|---|
| Trusted flooded under thin cloud, found (24) | 17 | 21 | 20 |
| Dry-labelled under thin cloud, called flooded (69; labels untrusted) | 6 | 22 | 39 |
| Control: assessable roads on the same tiles, called right (175) | 77.7% | 73.7% | 72.0% |

- **Primary outcome**, two-date against as it is, on the trusted flooded roads: 4 fixed, 1 broken, McNemar p = 0.375.
  Not significant.
- **Secondary outcomes:**
  - two-date against single image: 0 fixed, 1 broken (p = 1.0);
  - control, two-date against as it is: 5 fixed, 15 broken (p = 0.041), so worse;
  - control, single image against as it is: 10 fixed, 17 broken (p = 0.25).
- **By handling decision:** 23 of the 24 trusted flooded roads are CORRECT (16 found as it is, 20 two-date) and 1 is
  ASSESS.
- **Reading:**
  - de-hazing helps the detector find flooded roads under thin cloud, but not significantly on 24 roads;
  - it also raises flood calls on dry-labelled cloudy roads (some may be real floods, since those labels are untrusted);
  - it costs accuracy on the clear roads of those tiles.
- **Likely cause** (inference, not tested): the flood model is trained on uncorrected images, so it reads the
  correction itself as change.
- **Next:** train the flood model on de-hazed images too, then test once on unseen roads.

## Cloud as an extra variable, and training on de-hazed images (2026-10-25; exploratory; plan: `outputs/preregistration_cloud_variables.md`)
- **Setup:**
  - `evidence/pilot_scripts/evaluate_cloudvars.py`, with its log, `cloudvars_calls.csv` and `cloudvars_numbers.json`;
  - two-date features for all 200 tile-rule tiles; 45 minutes.

| Arm | Found (24 trusted) | Dry-labelled called flooded (69) | Control right (175) |
|---|---|---|---|
| 1 as it is, production | 17 | 6 | 77.7% |
| 2 two-date, production training | 20 | 30 | 76.6% |
| 3 as it is + cloud variables (tile-rule training) | 16 | 3 | 80.0% |
| 4 two-date + cloud variables | 19 | 4 | 77.7% |
| 5 two-date + cloud variables + fit variables | 18 | 4 | 78.9% |
| 6 two-date, tile-rule training, no cloud variables | 19 | 7 | 76.6% |

- **Primary** (arm 4 against arm 2, found): 0 fixed, 1 broken, p = 1.0. The cloud variables do not find more flooded
  roads.
- Arm 4 against arm 3: 4 fixed, 1 broken, p = 0.375.
- The cloud variables cut flood calls on cloudy dry-labelled roads, but arm 6 (no cloud variables, trained on cloudy
  roads) does nearly the same (7). So the cut comes mostly from training on roads whose dry labels follow the labelling
  rule.
- **Not anticipated by the plan (disclosed):**
  - In this run arm 2 trains on the de-hazed features of every tile. In the first road test (above), the two-date arm
    trained on the uncorrected features and was called on corrected ones.
  - The difference matters. Clear roads right: 72.0% (trained as it is) against 76.6% (trained de-hazed; against arm 1:
    7 fixed, 9 broken, p = 0.80).
  - Flooded found: 20 of 24 either way.
  - So the false alarms on clear roads came mostly from training on one kind of image and calling on another.
  - This is a post-hoc reading of arm 2, to be confirmed on unseen roads.

## Related checks
- Visibility gate (trees and shadow, from a road detector on the before image): not shown to drop the roads the model
  gets wrong (+3.6 points kept vs dropped, p 0.30); accuracy is flat across visible share.
- Co-registration: ground shifts about 0.6 m; no effect. PCA reduction: no reduction kept accuracy.
- DINOv2 change cues added +1.2 points (p 0.035) and still +1.6 (p 0.019) on the 798 assessable roads.

## Open questions we have not answered
- How good is the two-date (dark rise) mask against real two-date cloud labels?
- Can a thin-cloud road be recovered (local de-hazing) rather than abstained?
- What to do when only the before image is cloudy (an after-only call)?
- How should "cannot assess" be reported (coverage against accuracy)?
- Do cloud shadows pose as floods at 0.5 m?

## Clear-sky benchmark for the flood calls (2026-10-25 22:30, computed after the runs; not in a test plan)
The handle question asks whether seeing through cloud finds change "as well as under clear sky". The same runs give
the clear-sky level. On the 39 thin-cloud tiles, the assessable (clear) roads labelled flooded number 95, and none of
them overlaps the 93 roads under thin cloud. All three arms, each trained on de-hazed images, find 81 of those 95
(85%):
- none;
- two-date (2ec5346);
- He 2011.

Under thin cloud the same arms find 17, 20 and 22 of 24 (71%, 83%, 92%), with wide intervals. Source:
`pilot_scripts/cloudvars_calls.csv` and `he_dehazed_calls.csv`, from development calls only (script in the session
scratchpad: `clearsky.py`). Exploratory: the 24 flooded roads under thin cloud were seen before.

## Two-date trained de-hazed, rerun without the corner edit (2026-10-25 23:20; plan `outputs/preregistration_twodate_cornerfix.md`)
- 99 tile-rule tiles with a cloud gate got `darkref` on 5d325d9. The 101 without a gate kept their as-it-is features,
  checked on two tiles to reproduce `corrected_rows(tile, "none")`.
- Flooded roads under thin cloud: 20 of 24, unchanged.
- Dry-labelled roads called flooded: 29 of 69, against 30.
- Clear roads right: 134 of 175 (76.6%), unchanged; vs none 8 fixed, 10 broken, p = 0.81.
- He 2011 against the corrected run: flooded found 2 fixed, 0 broken (p = 0.50); dry-labelled 23 / 3 (p = 0.0001);
  clear roads 13 / 12 (p = 1.0).
- Clear sky, same tiles: still 81 of 95.
- The corner edit barely moved arm 2. The slide 6–7 numbers now come from this run
  (`twodate_cornerfix_numbers.json`, `he_vs_twodate_cornerfix.json`).

## Both cloud masks together on HRC_WHU (2026-10-25 23:40; plan written in `pilot_scripts/mask_combo.py` before running)
Scored on the 120 development images, pooled pixels, with no settings tuned.

| Mask | Precision | Recall | F1 |
|---|---|---|---|
| bright | 0.812 | 0.275 | 0.411 |
| dark | 0.618 | 0.682 | 0.649 |
| AND | 0.818 | 0.274 | 0.411 |
| OR | 0.617 | 0.683 | 0.648 |
| grow (bright cores + touching dark blobs, the primary) | 0.616 | 0.653 | 0.634 |

The bright mask is almost a subset of the dark mask: AND equals bright and OR equals dark. Combining adds nothing,
and grow loses the thin cloud that has no bright core. By land cover, the bright rule beats the dark channel only on
barren (0.57 against 0.48), where bright bare ground fools the dark channel. Source: `pilot_scripts/mask_combo.csv`.

## Two-date and He cues together (2026-10-25 23:35; plan `outputs/preregistration_both_dehazers.md`; exploratory)
Justin (2026-10-25): "cant we use both He and two date?"
- **Setup:**
  - `evidence/pilot_scripts/evaluate_both_dehazers.py`, with its log, `both_dehazers_calls.csv` and
    `both_dehazers_numbers.json`; 82 s (both cue tables read from the cache the earlier runs wrote).
  - **Both cues:** the production flood model (tuned random forest) on the 96 production cues of each de-hazer side by
    side, 192 columns: `td_` two-date without the corner edit (99 gated tiles `darkref`, 101 as they are), `he_` He 2011
    (all 200 tile-rule tiles). Trained on the assessable roads, 5 folds by tile, seed 662.
  - **Check:** the same features and folds rebuilt the two single de-hazer arms call for call, and the earlier arms'
    intervals reproduce.
  - AND / OR: **post hoc (chosen after seeing the calls)**, from the existing two-date and He calls, no new training.

### Measured
Count, share and tile-resampled 95% interval (5000 resamples, seed 662).

| Arm | Found (24 trusted flooded, thin cloud) | Dry-labelled called flooded (69; labels untrusted) | Control right (175) | Clear sky: flooded found (95) |
|---|---|---|---|---|
| none | 17 (70.8% [42.1, 88.2]) | 6 (8.7% [3.1, 15.1]) | 136 (77.7% [70.4, 84.9]) | 81 (85.3% [78.1, 92.7]) |
| two-date · trained de-hazed | 20 (83.3% [62.5, 96.3]) | 29 (42.0% [25.5, 56.0]) | 134 (76.6% [67.3, 84.6]) | 81 (85.3% [77.5, 91.6]) |
| He 2011 · trained de-hazed | 22 (91.7% [75.0, 100.0]) | 9 (13.0% [5.6, 21.3]) | 135 (77.1% [68.1, 85.1]) | 81 (85.3% [76.0, 93.7]) |
| **both cues** | 21 (87.5% [66.7, 100.0]) | 9 (13.0% [6.0, 20.0]) | 141 (80.6% [72.5, 87.9]) | 86 (90.5% [83.8, 96.2]) |
| AND, post hoc | 20 (83.3% [62.5, 96.3]) | 6 (8.7% [3.1, 15.1]) | 133 (76.0% [66.7, 84.5]) | 74 (77.9% [66.0, 88.0]) |
| OR, post hoc | 22 (91.7% [75.0, 100.0]) | 32 (46.4% [31.2, 59.1]) | 136 (77.7% [68.3, 85.8]) | 88 (92.6% [86.8, 97.5]) |

The clear-sky roads are the 95 flooded roads among the 175 control roads (none under thin cloud), so those two columns
are not independent.

**Paired tests**, exact McNemar: roads fixed / roads broken, p. For the dry-labelled roads "fixed" means no longer
called flooded. The nine planned tests are the first three columns; the clear-sky column was computed alongside.

| Both cues against | Found (24) | Dry-labelled (69) | Control (175) | Clear sky (95) |
|---|---|---|---|---|
| none | 4 / 0, p = 0.125 | 0 / 3, p = 0.25 | 10 / 5, p = 0.30 | 6 / 1, p = 0.125 |
| He 2011 · trained de-hazed | 0 / 1, p = 1.0 | 3 / 3, p = 1.0 | 10 / 4, p = 0.18 | 6 / 1, p = 0.125 |
| two-date · trained de-hazed | 1 / 0, p = 1.0 | **20 / 0, p = 1.9e-6** | 10 / 3, p = 0.092 | 7 / 2, p = 0.18 |

| Post hoc, against none | Found (24) | Dry-labelled (69) | Control (175) | Clear sky (95) |
|---|---|---|---|---|
| AND | 4 / 1, p = 0.375 | 0 / 0, p = 1.0 | 9 / 12, p = 0.66 | 3 / 10, p = 0.092 |
| OR | 5 / 0, p = 0.0625 | **0 / 26, p = 3.0e-8** | 9 / 9, p = 1.0 | **8 / 1, p = 0.039** |

- Accuracy differences on the control roads, with tile-resampled intervals: both cues against none +2.9 points
  (-0.6 to +6.2); against He +3.4 (+0.0 to +7.6); against two-date +4.0 (+0.5 to +8.4). The last interval excludes 0,
  but the exact test (10 / 3) does not reach 0.05.
- One planned test is significant, and it passes a Bonferroni cut over the nine (0.0056): both cues makes 20 fewer
  flood calls than two-date on the dry-labelled roads (9 against 29), and breaks none.
- He already found 22 of 24, so against He the found test could not reach significance (at most 2 roads to fix; noted
  in the plan before running).

### Inference (not measured)
- Adding the two-date cues to He does not find more flooded roads under thin cloud (21 against He's 22, one road
  apart).
- On the dry-labelled cloudy roads the combined model behaves like He (9 calls), not like two-date (29). It does not
  pick up two-date's extra flood calls. Those labels cannot be trusted under cloud, so fewer calls is not proven better.
- Both cues is highest on the clear roads (80.6% right; 86 of 95 flooded found, against 81 for every other model).
  None of these gains is significant. A model with 192 columns builds a different forest than one with 96, so this can
  be noise, and it needs unseen roads to tell.
- OR finds the most (22 of 24; 88 of 95 clear sky, p = 0.039 against none). It also keeps two-date's flood calls on
  dry-labelled roads (32). AND removes them (6) but finds fewer clear flooded roads (74 of 95). Both rules were chosen
  after seeing the calls.
- Exploratory: the 24 flooded roads under thin cloud were seen before. Confirmation needs a second event.

## Everything together (2026-10-26 00:15–00:50; plan `outputs/preregistration_everything_together.md`; exploratory)
Justin (2026-10-26): "are you able to start testing with everything all together".
- **Setup:**
  - `evidence/pilot_scripts/evaluate_everything_together.py`, with its log, `everything_together_calls.csv` and
    `everything_together_numbers.json`; 172 s on the CPU from cached feature tables only (no GPU, no recompute).
  - **Everything together:** the production flood model (tuned random forest) on 304 columns, with the cloud gate as
    in production:
    - the raw 96 production cues (93 classical + 3 DINOv2 change cues);
    - the same 96 cues from each de-hazer, `td_` (two-date without the corner edit) and `he_` (He 2011), as in "both
      cues";
    - the DINOv2 change vector, reduced to 16 PCs inside each fold, as in `Code/dino_test.ipynb`.
  - **Ablations:**
    - without de-hazing (this is the best-so-far arm, so it is reported once);
    - without the vector;
    - without the raw classical cues (their de-hazed copies stay);
    - secondary: without any classical cue.
  - **Folds:** `StratifiedGroupKFold(5, shuffle=True, random_state=662)` by tile, split over each scoring set's own
    roads, as each set was scored before:
    - (i) 798: folds over the 798, fitted on them (production's 83.0%);
    - (ii) 891: folds over the 891, every road fitted (the logged runs, which had no road rule);
    - (iii) cloud groups: folds over all 1,037 roads, fitted on the assessable ones (tonight's runs).
  - **Checks, all passed:**
    - the logged counts reproduce: on the 798, production 394/47/89/268; on the 891, classical 93 401/64/87/339,
      production 408/57/83/343 and best so far 409/56/80/346;
    - tonight's production and both-cues calls and group intervals reproduce call for call;
    - `production.json` is unchanged (checked by hash).
  - **Disclosed:**
    - the first run crashed on a coding error in the check block, before any arm was scored
      (`evaluate_everything_together_attempt1_crash.log`);
    - the rerun also writes unrounded McNemar p values; nothing else changed.

### Measured
**(i) The 798 assessable roads (primary).** 441 of the 798 roads (193 tiles) are labelled flooded. Values are percent
with the tile-resampled 95% interval (2,000 resamples, seed 662); MCC runs from −1 to 1.

| Arm | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| production | 394 | 47 | 89 | 268 | 83.0 (79.4–86.4) | 81.6 (76.0–86.3) | 89.3 (85.2–93.1) | 75.1 (67.9–81.6) | 85.3 (81.2–88.8) | 0.655 (0.582–0.725) |
| production + DINOv2 vector (best so far; = without de-hazing) | 394 | 47 | 88 | 269 | 83.1 (79.5–86.6) | 81.7 (76.2–86.5) | 89.3 (85.4–93.0) | 75.4 (67.9–82.0) | 85.4 (81.4–88.6) | 0.658 (0.583–0.727) |
| both cues | 399 | 42 | 95 | 262 | 82.8 (79.1–86.3) | 80.8 (75.1–85.6) | 90.5 (86.6–93.9) | 73.4 (65.7–80.4) | 85.3 (81.2–88.8) | 0.654 (0.577–0.722) |
| **everything together** | 399 | 42 | 89 | 268 | 83.6 (79.9–87.1) | 81.8 (76.4–86.4) | 90.5 (86.2–94.1) | 75.1 (67.8–81.6) | 85.9 (81.8–89.3) | 0.669 (0.595–0.737) |
| without the DINOv2 vector | 398 | 43 | 92 | 265 | 83.1 (79.1–86.7) | 81.2 (75.5–86.1) | 90.2 (86.1–93.9) | 74.2 (66.9–81.1) | 85.5 (81.2–89.1) | 0.659 (0.578–0.730) |
| without classical (raw) | 401 | 40 | 93 | 264 | 83.3 (79.5–86.9) | 81.2 (75.5–86.0) | 90.9 (86.8–94.6) | 73.9 (66.4–80.8) | 85.8 (81.5–89.2) | 0.664 (0.587–0.736) |
| without any classical cue (secondary) | 388 | 53 | 101 | 256 | 80.7 (76.6–84.5) | 79.3 (73.0–84.6) | 88.0 (83.3–91.9) | 71.7 (64.0–79.1) | 83.4 (78.9–87.2) | 0.609 (0.526–0.687) |

Paired tests: accuracy difference with a tile-resampled 95% interval (5,000 resamples), roads fixed / broken, and
exact McNemar.

| Comparison | Accuracy difference, points (95% CI) | Fixed / broken | McNemar p | Rule |
|---|---|---|---|---|
| **everything together vs production (primary)** | +0.6 (−0.7 to +1.9) | 20 / 15 | 0.50 | no |
| production + DINOv2 vector (best so far) vs production | +0.1 (−1.4 to +1.7) | 20 / 19 | 1.0 | no |
| both cues vs production | −0.1 (−1.6 to +1.2) | 18 / 19 | 1.0 | no |
| without the DINOv2 vector vs production | +0.1 (−1.2 to +1.4) | 18 / 17 | 1.0 | no |
| without classical (raw) vs production | +0.4 (−1.2 to +1.9) | 24 / 21 | 0.766 | no |
| without any classical cue (secondary) vs production | −2.3 (−5.3 to +0.8) | 52 / 70 | 0.123 | no |
| everything together vs best so far | +0.5 (−1.1 to +2.1) | 21 / 17 | 0.627 | |
| everything together vs both cues | +0.8 (−0.4 to +1.9) | 18 / 12 | 0.362 | |
| without the DINOv2 vector vs everything together | −0.5 (−1.8 to +0.8) | 12 / 16 | 0.572 | |
| without classical (raw) vs everything together | −0.2 (−1.3 to +0.8) | 10 / 12 | 0.832 | |
| without any classical cue (secondary) vs everything together | −2.9 (−5.6 to −0.2) | 36 / 59 | 0.0235 | |

**Promotion rule.** The rule is `production.json`'s, applied with `sn8_stages.confirm` (read-only). `production.json`
was not written.
- Everything together against production on the 798: +0.6 points (−0.7 to +1.9), p = 0.50. **It would not pass.**
- On the 891: −1.0 (−2.8 to +0.6), p = 0.19. It would not pass.
- No arm passes on either set.

**(ii) All 891 tile-rule roads (the logged construction).** 465 of the 891 roads (200 tiles) are labelled flooded.

| Arm | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| production | 408 | 57 | 83 | 343 | 84.3 (80.8–87.6) | 83.1 (77.7–88.1) | 87.7 (82.6–91.8) | 80.5 (74.6–86.0) | 85.4 (81.2–88.9) | 0.686 (0.614–0.749) |
| production + DINOv2 vector (best so far; = without de-hazing) | 409 | 56 | 80 | 346 | 84.7 (81.3–88.1) | 83.6 (78.4–88.4) | 88.0 (83.2–92.0) | 81.2 (75.3–86.7) | 85.7 (81.7–89.1) | 0.694 (0.626–0.759) |
| both cues | 403 | 62 | 92 | 334 | 82.7 (79.1–86.3) | 81.4 (75.9–86.6) | 86.7 (81.4–91.0) | 78.4 (72.1–84.0) | 84.0 (79.6–87.9) | 0.654 (0.581–0.724) |
| **everything together** | 405 | 60 | 89 | 337 | 83.3 (79.9–86.8) | 82.0 (76.3–86.9) | 87.1 (81.8–91.5) | 79.1 (72.9–84.9) | 84.5 (80.3–88.2) | 0.665 (0.595–0.736) |
| without the DINOv2 vector | 407 | 58 | 89 | 337 | 83.5 (79.8–87.0) | 82.1 (76.3–87.1) | 87.5 (82.3–91.8) | 79.1 (72.9–84.6) | 84.7 (80.3–88.4) | 0.670 (0.596–0.739) |
| without classical (raw) | 411 | 54 | 83 | 343 | 84.6 (81.2–88.0) | 83.2 (77.9–88.0) | 88.4 (83.2–92.3) | 80.5 (74.4–86.0) | 85.7 (81.6–89.2) | 0.692 (0.624–0.758) |
| without any classical cue (secondary) | 406 | 59 | 97 | 329 | 82.5 (78.6–86.1) | 80.7 (74.5–86.2) | 87.3 (82.8–91.0) | 77.2 (70.7–83.5) | 83.9 (79.3–87.6) | 0.650 (0.572–0.720) |
| classical 93 (production before DINOv2; check) | 401 | 64 | 87 | 339 | 83.1 (79.4–86.5) | 82.2 (76.4–87.4) | 86.2 (80.9–90.6) | 79.6 (73.6–85.0) | 84.2 (79.7–87.9) | 0.661 (0.588–0.727) |

| Comparison | Accuracy difference, points (95% CI) | Fixed / broken | McNemar p | Rule |
|---|---|---|---|---|
| everything together vs production | −1.0 (−2.8 to +0.6) | 14 / 23 | 0.188 | no |
| production + DINOv2 vector (best so far) vs production | +0.4 (−0.7 to +1.6) | 20 / 16 | 0.618 | no |
| both cues vs production | −1.6 (−3.4 to +0.1) | 21 / 35 | 0.0814 | no |
| without the DINOv2 vector vs production | −0.8 (−2.4 to +0.9) | 14 / 21 | 0.311 | no |
| without classical (raw) vs production | +0.3 (−1.4 to +2.1) | 26 / 23 | 0.775 | no |
| without any classical cue (secondary) vs production | −1.8 (−4.7 to +1.1) | 60 / 76 | 0.198 | no |
| everything together vs best so far | −1.5 (−3.0 to +0.0) | 11 / 24 | 0.041 | |
| everything together vs both cues | +0.6 (−0.7 to +1.9) | 19 / 14 | 0.487 | |
| without the DINOv2 vector vs everything together | +0.2 (−1.0 to +1.5) | 15 / 13 | 0.851 | |
| without classical (raw) vs everything together | +1.4 (+0.1 to +2.6) | 20 / 8 | 0.0357 | |
| without any classical cue (secondary) vs everything together | −0.8 (−3.7 to +2.1) | 55 / 62 | 0.579 | |

"Production" here is today's 96-cue production, so it is the logged "production + DINOv2 change cues". The logged
+1.7 points for the vector (p = 0.028) was measured against the 93-cue production. Against today's production the
vector adds +0.4 (20 / 16, p = 0.62).

**(iii) Cloud groups (tonight's construction).** Each cell gives the count, the share and a tile-resampled 95% interval
(5,000 resamples, seed 662, drawn in tonight's order). Production's and both cues' intervals are tonight's, reproduced.

| Arm | Found (24 trusted flooded, thin cloud) | Dry-labelled called flooded (69; labels untrusted) | Control right (175) | Clear sky: flooded found (95) |
|---|---|---|---|---|
| production | 17 (70.8% [42.1, 88.2]) | 6 (8.7% [3.1, 15.1]) | 136 (77.7% [70.4, 84.9]) | 81 (85.3% [78.1, 92.7]) |
| production + DINOv2 vector (best so far) | 17 (70.8% [44.4, 89.3]) | 5 (7.2% [1.8, 13.0]) | 141 (80.6% [72.9, 87.4]) | 82 (86.3% [78.0, 93.9]) |
| both cues | 21 (87.5% [66.7, 100.0]) | 9 (13.0% [6.0, 20.0]) | 141 (80.6% [72.5, 87.9]) | 86 (90.5% [83.8, 96.2]) |
| **everything together** | 21 (87.5% [66.7, 100.0]) | 6 (8.7% [3.1, 15.1]) | 141 (80.6% [72.7, 87.7]) | 84 (88.4% [81.6, 94.7]) |
| without the DINOv2 vector | 20 (83.3% [57.9, 96.6]) | 7 (10.1% [3.3, 17.2]) | 137 (78.3% [70.1, 85.6]) | 82 (86.3% [78.8, 93.8]) |
| without classical (raw) | 21 (87.5% [66.7, 100.0]) | 6 (8.7% [1.9, 15.7]) | 143 (81.7% [73.5, 89.0]) | 87 (91.6% [85.0, 97.1]) |
| without any classical cue (secondary) | 21 (87.5% [70.0, 100.0]) | 5 (7.2% [0.0, 16.3]) | 131 (74.9% [65.6, 84.0]) | 80 (84.2% [72.7, 93.5]) |

- **Confusion counts:**
  - For the flooded groups, TP is the count found and FN the rest. For the dry-labelled group, FP is the count called
    flooded and TN the rest.
  - Control roads (175), TP / FN / FP / TN:

    | Arm | TP / FN / FP / TN |
    |---|---|
    | production | 81 / 14 / 25 / 55 |
    | best so far | 82 / 13 / 21 / 59 |
    | both cues | 86 / 9 / 25 / 55 |
    | everything together | 84 / 11 / 23 / 57 |
    | without the vector | 82 / 13 / 25 / 55 |
    | without classical (raw) | 87 / 8 / 24 / 56 |
    | without any classical cue | 80 / 15 / 29 / 51 |
- The clear-sky roads are the flooded roads among the control roads, so those two columns are not independent.

Paired tests, exact McNemar: roads fixed / broken, p. For the dry-labelled roads, "fixed" means no longer called
flooded.

| Everything together against | Found (24) | Dry-labelled (69) | Control (175) | Clear sky (95) |
|---|---|---|---|---|
| production | 4 / 0, p = 0.125 | 0 / 0, p = 1.0 | 7 / 2, p = 0.18 | 5 / 2, p = 0.453 |
| best so far | 4 / 0, p = 0.125 | 0 / 1, p = 1.0 | 4 / 4, p = 1.0 | 4 / 2, p = 0.688 |
| both cues | 0 / 0, p = 1.0 | 3 / 0, p = 0.25 | 6 / 6, p = 1.0 | 1 / 3, p = 0.625 |

| Ablation against everything together | Found (24) | Dry-labelled (69) | Control (175) | Clear sky (95) |
|---|---|---|---|---|
| without the DINOv2 vector | 0 / 1, p = 1.0 | 0 / 1, p = 1.0 | 4 / 8, p = 0.388 | 2 / 4, p = 0.688 |
| without classical (raw) | 0 / 0, p = 1.0 | 1 / 1, p = 1.0 | 5 / 3, p = 0.727 | 3 / 0, p = 0.25 |
| without any classical cue (secondary) | 1 / 1, p = 1.0 | 4 / 3, p = 1.0 | 11 / 21, p = 0.11 | 4 / 8, p = 0.388 |

**Sensitivity check, in the plan: the same arms with tonight's split, scored on the 798 and the 891.** Each change
against production gives roads fixed / broken and McNemar p.

| Arm | 798: TP / FN / FP / TN | 798 accuracy | vs production | 891: TP / FN / FP / TN | 891 accuracy | vs production |
|---|---|---|---|---|---|---|
| production | 390 / 51 / 91 / 266 | 82.2 | | 407 / 58 / 97 / 329 | 82.6 | |
| best so far | 400 / 41 / 83 / 274 | 84.5 | +2.3 (24 / 6, p = 0.0014), passes | 417 / 48 / 88 / 338 | 84.7 | +2.1 (27 / 8, p = 0.0019), passes |
| both cues | 397 / 44 / 91 / 266 | 83.1 | +0.9 (27 / 20, p = 0.38) | 418 / 47 / 100 / 326 | 83.5 | +0.9 (31 / 23, p = 0.34) |
| **everything together** | 398 / 43 / 89 / 268 | 83.5 | +1.2 (21 / 11, p = 0.11) | 419 / 46 / 95 / 331 | 84.2 | +1.6 (25 / 11, p = 0.029), passes |
| without the DINOv2 vector | 397 / 44 / 93 / 264 | 82.8 | +0.6 (17 / 12, p = 0.46) | 417 / 48 / 100 / 326 | 83.4 | +0.8 (20 / 13, p = 0.30) |
| without classical (raw) | 402 / 39 / 91 / 266 | 83.7 | +1.5 (26 / 14, p = 0.081) | 423 / 42 / 97 / 329 | 84.4 | +1.8 (31 / 15, p = 0.026), passes |
| without any classical cue | 389 / 52 / 102 / 255 | 80.7 | −1.5 (58 / 70, p = 0.33) | 410 / 55 / 107 / 319 | 81.8 | −0.8 (66 / 73, p = 0.61) |

With this split, everything together passes the rule on the 891. The best so far passes on both sets with a larger
gain, so under the rule's largest-gain clause the best so far would still be the one promoted.

**Post hoc fold-seed check (not in the plan; chosen after seeing the results above).**
- Files: `pilot_scripts/evaluate_everything_together_foldseeds.py`, with its log, `everything_together_foldseeds.csv`
  and `.json`. The run took 25 minutes; the machine was shared.
- Why: the best so far gained +0.1 with production's split and +2.3 with tonight's.
- Method: the primary comparison on the 798, repeated with 20 other fold seeds (1–20). Folds are still split over the
  798, and the model seed stays 662. Seed 662 reproduced set (i).
- The log carries scikit-learn's warning about passing its configuration to joblib workers. It was not filtered, and
  the run uses the default configuration.

| Arm (20 new splits) | Mean accuracy (SD; range) | Mean gain vs production (range), points | Gain > 0 | Rule passes |
|---|---|---|---|---|
| production | 82.5 (0.6; 81.6–84.2) | | | |
| best so far | 83.6 (0.6; 82.3–84.5) | +1.1 (+0.1 to +2.3) | 20 / 20 | 3 / 20 |
| both cues | 82.1 (0.7; 81.0–83.1) | −0.4 (−1.5 to +0.5) | 5 / 20 | 0 / 20 |
| everything together | 83.3 (0.7; 82.0–84.6) | +0.8 (−0.4 to +1.8) | 16 / 20 | 3 / 20 |
| without classical (raw) | 83.2 (0.7; 81.5–84.3) | +0.7 (−1.0 to +2.3) | 16 / 20 | 1 / 20 |

- Everything together minus the best so far averages −0.3 points (range −1.0 to +0.6). It is below the best so far
  on 17 of the 20 splits, and the difference is significant (McNemar p < 0.05) on none.
- The 20 splits share the same roads, so they are not independent tests, and these counts are not p-values.

### Inference (not measured)
- **Everything together is not a clear improvement.**
  - On the primary set it is the top arm (83.6%, MCC 0.669), but only 0.6 points above production, and it would not
    pass the rule.
  - Over 21 splits it averages 0.8 points above production and 0.3 below the DINOv2 vector alone.
  - On clear roads, putting the de-hazed cues on top of the best so far does not help, and on the 891 it hurts
    (−1.5, p = 0.041, uncorrected).
- **Under thin cloud it keeps what the de-hazed cues gave.**
  - It finds 21 of the 24 trusted flooded roads, against 17 for production and for the best so far.
  - It avoids both cues' extra flood calls on dry-labelled cloudy roads: 6 (production's number) against 9.
  - This is a lead, not a result: 4 / 0 gives p = 0.125, and the 24 roads were seen before.
- **The raw classical cues add nothing once their de-hazed copies are in.**
  - Dropping them gives −0.2 on the 798 and +1.4 on the 891 (p = 0.036, uncorrected).
  - A likely cause, untested: on the 101 tiles without a cloud gate the `td_` copies equal the raw cues. The forest
    tries about 17 of 304 columns at each split, so repeated cues take more of those draws.
  - Classical cues as a family are still needed: with none of them (DINOv2 only, raw and de-hazed), accuracy is 2.9
    points lower on the 798 (p = 0.024).
- **The fold split is as large as the effects.**
  - Production alone ranges from 81.6% to 84.2% across splits.
  - Whether an arm "passes" depends on which split is used: the vector passes with tonight's split, not with
    production's, and on 3 of 20 others.
  - The vector's gain is small but always positive (20 of 20 splits, mean +1.1). That is the steadiest sign in these
    runs.
  - One split per comparison cannot rank arms a point apart. Repeated splits with a test that allows for their overlap
    would be needed.
- **If a candidate is frozen for the sealed test**, these runs do not separate everything together from the best so
  far on clear roads. They differ only under thin cloud, where the evidence is 24 seen-before roads.
  - Both need the in-fold PCA inside production.
  - Everything together also needs both de-hazers at inference time.

## Cloud spotting as a pipeline of tools (2026-10-26 02:00; plan `outputs/preregistration_cloud_spotting_pipeline.md`; exploratory; full write-up `evidence/12_cloud_spotting_pipeline.md`)
Justin (2026-10-26): test DINOv2 and DINOv3 for cloud spotting, every technique alone and together. Later: "we will
not use dinov3 in the library, it is only for research and benchmarking our other models".
- **Setup:**
  - Per-pixel learners (random forest, fixed settings) on the 120 HRC_WHU development images, scored on held-out images
    (5 folds by image) against the expert masks.
  - Intervals come from resampled images. Code: GeoAI-Roads `55c8fc2` (`sn8_cloudspot.py`, library tools only).
  - Drivers: `pilot_scripts/cloud_spotting/`.

| Arm | Precision | Recall | F1 [95% CI] | IoU |
|---|---|---|---|---|
| dark rule (production, fixed) | 0.618 | 0.682 | 0.648 [0.611–0.686] | 0.480 |
| classical (bright + dark + texture) | 0.768 | 0.751 | 0.760 [0.728–0.790] | 0.612 |
| DINOv2 alone | 0.879 | 0.840 | 0.859 [0.840–0.876] | 0.753 |
| **chosen library spotter: bright + texture + DINOv2** | 0.884 | 0.853 | **0.868 [0.848–0.885]** | 0.767 |
| *DINOv3 alone (benchmark, research only)* | 0.911 | 0.873 | 0.892 [0.874–0.906] | 0.804 |
| *best benchmark: everything − dark* | 0.914 | 0.876 | 0.894 [0.877–0.909] | 0.809 |

- **Against the dark rule:** the chosen spotter gains +0.220 F1 [+0.188, +0.250] and is higher on 112 of 120 images.
- **Tool impacts:**
  - Texture added to bright + dark: +0.146 [+0.122, +0.170].
  - DINOv2 added to classical: +0.106 [+0.084, +0.128].
  - Classical cues added to DINOv2: +0.006 [−0.002, +0.013].
  - Removing any one classical tool from classical + DINOv2: within ±0.0025.
  - A forest on the dark channel alone scores below the fixed dark rule (0.579 against 0.648).
- **Land cover:** the chosen spotter is weakest on barren (0.781) and snow (0.833), where bright ground causes false
  alarms. On urban it misses thin cloud (recall 0.77).
- **Benchmark:** the library spotter reaches 97.0% of the best DINOv3 arm (gap +0.027 [+0.019, +0.035]).
- **SpaceNet 8 development roads, the spotter as the road cloud gate in place of the dark-rise road rule** (tile rule
  kept, same 20% cut):
  - The two rules agree with Jaccard 0.71 (229 against 239 roads flagged, 195 by both).
  - Roads set aside: 239 (27 flooded) under production and 247 (18 flooded) under the spotter.
  - On the kept roads the tuned flood forest scores 0.822 (TP 390, FN 51, FP 91, TN 266) under production and 0.846
    (TP 416, FN 34, FP 88, TN 252) under the spotter.
  - On the 757 shared roads: +1.85 points [+0.4, +3.4], 25 fixed / 11 broken, exact McNemar p = 0.029.
- **Caveat:** labels under cloud cannot be trusted, so this gain can come from different training roads rather than
  better cloud spotting. The spotter's SpaceNet 8 pixel accuracy is unmeasured (no labels), and HRC_WHU is academic use
  only.
- **Pictures:** `figures/cloud_spotting/`.

## The library pipeline as a full factorial (2026-10-26 03:05; plan `outputs/preregistration_pipeline_factorial.md`; exploratory; full write-up `evidence/13_pipeline_factorial.md`)
Justin (2026-10-26): "Use all these techniques together ... test with and without them to understand their impacts
strengths and weaknesses as well as the optimal combos".

**Setup:**
- **Arms:** 2 gates x 4 cue sets x 2 feature sets = 16 arms, every one the tuned production forest trained on the roads
  its gate keeps.
  - Gates: production (dark-rise road rule) or spotter (bright + texture + DINOv2 road rule).
  - Cue sets: none, two-date, He 2011, or both + raw.
  - Feature sets: production features, or + the DINOv2 vector (16 in-fold PCs).
- **Folds:** 5 by tile over all 1,037 roads, at seed 662 and 20 more splits.
- **Scored on** the 757 roads both gates keep.
- **Run:** `pilot_scripts/evaluate_pipeline_factorial.py`, 1,806 s on the CPU, cached tables only.
- **Checks:** every earlier arm reproduces call for call, and `production.json` is unchanged.

**Measured:**

| Arm | Mean accuracy over 21 splits ± SD | Seed 662 | Splits above production |
|---|---|---|---|
| production | 83.24 ± 0.50 | 82.4 (its worst split) | — |
| **production gate + DINOv2 vector (chosen)** | **84.48 ± 0.52** | 84.7 (TP 395, FN 36, FP 80, TN 246) | 20 / 21 |
| spotter gate + both + raw + vector (top mean) | 84.56 ± 0.60 | 85.6 (TP 406, FN 25, FP 84, TN 242) | 20 / 21 |
| spotter gate alone (last night's) | 83.76 ± 0.63 | 84.3 | 15 / 21 |

- **Main effects on the shared roads**, as points with the seed-averaged tile interval:

  | Tool | Main effect | 95% CI | Splits above 0 |
  |---|---|---|---|
  | **DINOv2 vector** | **+1.25** | **+0.56 to +1.95** | 21 / 21 |
  | Spotter gate | +0.34 | −0.19 to +0.96 | 16 / 21 |
  | Two-date | −0.36 | −1.06 to +0.27 | 4 / 21 |
  | He 2011 | −0.66 | −1.62 to +0.23 | 1 / 21 |
  | Both + raw | +0.11 | −0.38 to +0.59 | 13 / 21 |

  - The only interaction that clears 0 is He x vector, +0.87: He costs −1.09 without the vector and −0.22 with it.
- **Last night's spotter-gate gain was the luckiest split.** Its +1.85 (p = 0.029) is the largest of the 21; the mean
  is +0.52.
- **Thin cloud** (production's groups; means over splits):
  - **Trusted flooded (24):**
    - production finds 72.6%; the spotter gate adds +5.6 and He +8.1;
    - but gate x He is −13.0 [−27.6, −4.1], so they do not add up;
    - He gives +14.6 under the production gate and +1.6 under the spotter.
  - **Dry-labelled, labels untrusted (69):** flooded calls go up from 10.4%:
    - two-date +24.5, He +15.4 and the spotter gate +15.3;
    - the vector lowers them by −10.1.
  - **Clear-sky benchmark (95):** the spotter gate finds +4.0 more [+1.7, +6.4].
- **Optimal combo (preregistered rule):**
  - All 8 vector arms tie within 0.52 points, and every paired interval against the top includes 0.
  - So the simplest is chosen: **production gate + raw cues + DINOv2 vector**.
  - **Promotion rule:** it passes at seed 662 (+2.2 [+0.9, +3.7], 23 / 6, p = 0.0023; on the 798, +2.3, p = 0.0014),
    but in only 5 of 21 splits. Nothing was promoted.

**Inference:**
- The vector is the one tool whose gain survives the change of split.
- The spotter gate and the de-hazers do the same job under thin cloud, so stacking them gains nothing there.
- Every cloud tool raises flooded calls on dry-labelled cloudy roads. Whether these are floods or false alarms cannot
  be told from these labels.

**Pictures:** `figures/pipeline_factorial/`: `arms_shared_accuracy.png`, `main_effects.png` and `cloud_groups.png`.
