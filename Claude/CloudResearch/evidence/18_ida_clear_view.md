# 18: Ida clear-view test: does the cloud pipeline recover the ground NOAA's aircraft saw? (2026-10-29; EXPLORATORY, development data only)

**Status:** complete (2026-10-30). Steps 1-2 written 2026-10-29; steps 3-5 resumed after the 22:55 kernel panic and finished 2026-10-30 11:53. Every result is reported, whatever it shows. Nothing is promoted.

**Plan:** `outputs/preregistration_ida_clear_view.md` (incl. Revision 1), followed as written except where listed
under **Deviations**. Code: `evidence/pilot_scripts/ida_clear_view/`. Figures: `figures/ida_clear_view/`.

## Step 1: valid-pixel coverage (replaces the outline upper bounds of evidence 17)

Coverage = share of a satellite tile's valid pixels (both dates non-zero, 6 px eroded, as `sn8_clouds._tile`) under a
valid NOAA pixel (alpha 255) of one flight, that flight's photo tiles mosaicked; measured on the photos' 4x overview
(about 0.54 m) warped to the tile grid. `s1_coverage.py` → `s1_coverage.csv`.

- **153 of 226 development tiles are kept (valid cover ≥ 50%)**; **46 of the 56 tiles with cloudy roads.**
- Evidence 17's outline bound (≥ 90% inside a photo tile: 175 tiles) was too high by 22 tiles: those photo tiles are
  mostly no-data where they meet our tiles (e.g. 2_17_40: outline 100%, valid 0%; its photo tile is 3% valid).
- Cloudy tiles dropped (valid cover): 0_13_17 (0.00), 2_15_50 (0.35), 2_17_36 (0.00), 2_17_40 (0.00), 2_18_35 (0.00),
  2_18_36 (0.00), 2_18_41 (0.34), 2_18_62 (0.00), 2_19_62 (0.00), 2_30_34 (0.00).
- Clear tiles dropped: 63 (51 with no valid NOAA pixel; partial: 0_16_14 0.42, 0_16_2 0.40, 0_18_17 0.37, 0_21_21
  0.02, 0_9_2 0.01, 2_15_51 0.00, 2_17_49 0.46, 2_17_53 0.16, 2_18_54 0.34, 2_19_35 0.32, 2_21_57 0.19, 2_30_38 0.02).
- Kept tiles are mostly fully covered: median cover 1.00 (cloudy kept: mean 0.97; clear kept: mean 0.93).

## Step 2: flight per tile and date gaps

Flight = most valid pixels; ties to the earlier date.

| Flight (date) | Kept tiles | of which cloudy |
|---|---|---|
| 20210830a (30 Aug) | 12 | 4 |
| 20210830b (30 Aug) | 15 | 5 |
| 20210831a (31 Aug) | 110 | 36 |
| 20210902a (2 Sep) | 16 | 1 |

- 40 kept tiles are covered ≥ 50% by two or more flights (27 by two, 13 by three): the date-gap noise floor uses them.
- **Satellite date: unconfirmed.** Catalog `10300100C46F5900` (prefix 1030 = WorldView-2) is named in SpaceNet 8's
  `Louisiana-East_Training_Public_label_image_mapping.csv`, but no open source found gives its acquisition date or
  off-nadir angle: the GeoTIFFs carry no date tag; an exact web search for the id returns nothing; the SpaceNet 8 paper
  (Hänsch et al. 2022, local full text) says only "Louisiana (Ida, late Aug 2021)"; Maxar's open-data STAC catalog has
  no Ida 2021 event; the SpaceNet blog and the CVF PDF refused automated fetches (HTTP 403). Press reports describe
  WorldView-2 "after" images taken on Tuesday 31 Aug 2021 (space.com), which is consistent but not tied to this
  catalog id. **If the pass was 31 Aug, the gaps are −1 day (30 Aug flights, 27 tiles), 0 days (31 Aug, 110 tiles) and
  +2 days (2 Sep, 16 tiles).** Off-nadir angle: not found (open item).

## Steps 3-5: method as run (`s2_prep.py`, `s3_score.py`, `s4_calls.py`, `s5_stats.py`)

1. **NOAA to the tile grid.** The chosen flight's photo tiles (RGBA, about 0.15 m), area-averaged from full resolution
   onto the tile's 0.5 m UTM 15N grid (`rasterio.warp.reproject`, `Resampling.average`). NOAA valid = alpha 255 after
   averaging, eroded 3 px.
2. **Grey and NOAA's own cloud/glare.** Grey = 0.299 R + 0.587 G + 0.114 B (the SpaceNet greyscale copy's weights).
   NOAA cloud/glare = `sn8_clouds.bright_mask` on NOAA grey (grey > 200 and local std < 10 in 21 px). Masked out of the
   alignment, the tone fit and every metric (Revision 1 item 6).
3. **Satellite masks and arms** (library functions, imported, not edited): bright, dark-channel and dark-rise masks
   (`sn8_clouds.cloud_maps`); **as is**; **He 2011** (`sn8_clouds.dehaze`); **two-date**
   (`sn8_cloudsym.either_date_dehaze`, production settings, 20 m fade); **two-date + spotter gate**: the trained spotter
   (`sn8_cloudpipe.best_spotter`, research only, HRC_WHU licence) on the after image, its mask kept in blobs ≥ 2,500 m²
   (as the dark-rise gate) and used as the gate of `sn8_cloudsym._correct` (after against before; clear pixels = valid
   minus every gate + 10 m). The spotter ran on the 76 tiles chosen for DINOv2 scoring (all kept cloudy tiles + a fixed
   sample of 30 kept clear tiles, seed 662, drawn before any scoring).
4. **Local co-registration, AROSICS-style** (Scheffler et al. 2017, settings from the full-text note): a coarse
   whole-tile pre-shift (phase correlation of gradient images at 2 m, capped at 20 m); then 256 px (128 m) windows every
   128 px on gradient-magnitude images (`sn8_coreg._gradient`, 1 m blur), windows skipped if > 30% bad data (every
   satellite cloud mask + 10 m, NOAA cloud/glare, no-data); per window: phase correlation (OpenCV sub-pixel), reject
   peak reliability R < 30 % (Eq. 3, on |IFFT| of the normalised cross-power spectrum), shift > 5 px beyond the
   pre-shift, or SSIM not improved by the shift; RANSAC affine with the inlier threshold tuned until 10 ± 2 % of tie
   points are outliers; then re-measured and refined (residual affine composed) up to 5 times; NOAA warped once
   (bicubic). Reference = the satellite after image (the image being judged). If fewer than 4 windows survive with all
   cloud masked, thin cloud may carry tie points (only opaque cloud, t < 0.2 or bright, masked; flagged per tile).
   **Residual** = RMS length of the re-measured shifts after the RANSAC outlier removal (AROSICS's own internal
   residual, not independent check points). **Tiles with residual > 1 px (0.5 m), or < 4 tie points, are dropped.**
   An affine model cannot remove building lean (off-nadir satellite vs near-vertical aerial frame): road strips are the
   primary region.
5. **Tone curve (frozen for every arm).** `sn8_refhaze.tone_curve` (monotone quantile matching) from NOAA grey to
   satellite after grey, fitted on clear-guard pixels valid in both, then on unchanged pixels only (IR-MAD/PIF style):
   residual of the 5 px box-smoothed images, keep |r − median| < 1.96 robust σ (no-change probability > 0.05 under
   chi-square, 1 dof), iterate to convergence (< 0.5% of pixels change; at most 10 passes).
6. **Regions** (all inside score = satellite valid ∩ NOAA valid ∩ not NOAA cloud): **thin cloud** = two-date gate
   (dark-rise blobs + both-cloudy) with t ≥ 0.2 and not cannot-assess; **opaque** = gate with t < 0.2 or cannot-assess;
   **clear guard** = outside every cloud mask (bright, dark, dark rise, the two-date gates, the spotter where it ran).
   Each is split into road strips (`sn8_cloudsym.road_strips`, the learned band), building footprints (SN8 label
   polygons, not on roads) and the rest. Trees: no tree mask exists for these tiles, so trees are not separated.
7. **Feature distance (primary).** Frozen DINOv2 ViT-L/14 + registers (`sn8_dino.tokens`, CPU), every image of a tile
   with the same valid mask (score), so the no-data fill is identical. A pixel's distance = 1 − cosine of its 14 px
   patch's tokens (arm vs tone-matched NOAA); region means over pixels. Tile means, region needs ≥ 1,000 px on a tile.

8. **Call level (Revision 1 item 1, adapted from M3R-CR; not their protocol).** Production's flood forest, fitted as
   factorial arm c00 under spatial folds S at seed 662 and frozen; **reproduction check passed (1,037 / 1,037 calls
   equal to the saved c00__S__662).** Each held-out road on the DINOv2-scored tiles was called again from features measured on
   each arm's after image and on the tone-matched NOAA image (same valid mask for every image). Cloudy = roads the production
   gate drops; thin = cloudy roads on thin-cloud strips.

## Steps 3-5: results

**Tiles.** 153 kept by coverage → **132 aligned** (21 dropped by the alignment rule: 11 with fewer than 4 surviving
windows, 10 with residual RMS > 1 px, max 2.37 px). Aligned tiles: residual RMS mean 0.57 px, median 0.54 px, max
0.98 px (AROSICS-internal residual); 14 aligned with thin cloud allowed to carry tie points. **35 of the 46 covered
cloudy tiles aligned.** DINOv2 scoring: the 35 aligned cloudy tiles + 10 clear tiles (the first 10 aligned of the seed-662
sample) = 45 tiles; pixel metrics on all 132. Dropped tiles: 0_13_1, 0_13_6, 0_14_7, 0_15_6, 0_15_7, 0_15_11, 0_16_4,
0_17_10, 0_18_10, 0_18_16, 0_19_14, 2_15_45, 2_15_47, 2_16_45, 2_16_48, 2_16_49, 2_19_43, 2_20_40, 2_20_41, 2_20_42,
2_21_41.

Numbers: tile means, paired across arms; [95% interval from 2,000 resamples of the 3 × 3 tile blocks]. Feature distance
= 1 − cosine of DINOv2 patch tokens to the tone-matched NOAA image (lower = closer). Numbers file:
`pilot_scripts/ida_clear_view/s5_numbers.json`; log `s5_stats.log`.

### Outcome 1 (primary): two-date is **not** closer to NOAA under thin cloud: **fails**
| Thin cloud (t ≥ 0.2) | two-date − as is | two-date − He 2011 | He 2011 − as is | tiles |
|---|---|---|---|---|
| road strips (primary region) | +0.0071 [−0.0049, +0.0173] | +0.0102 [+0.0002, +0.0184] | −0.0030 [−0.0070, +0.0011] | 33 |
| all pixels | +0.0006 [−0.0101, +0.0106] | +0.0018 [−0.0073, +0.0104] | −0.0012 [−0.0046, +0.0034] | 37 |
| buildings | +0.0161 [+0.0059, +0.0251] | +0.0095 [+0.0002, +0.0177] | +0.0067 [+0.0027, +0.0103] | 23 |

- The pass condition (difference < 0 with the interval below 0) is not met: on road strips two-date is closer than as is
  on 12 of 33 tiles. After Holm across the three comparisons, no road-strip or all-pixel difference is significant. On
  building footprints two-date is significantly **further** from NOAA than as is (Holm-adjusted Wilcoxon p = 0.003;
  closer on 5 of 23 tiles). Building lean between the off-nadir satellite and the near-vertical aerial frame is a
  known confound there (plan, Revision 1 item 5).
- Spotter-gated two-date: −0.0005 [−0.0104, +0.0075] vs two-date (all pixels). On road strips +0.0092 [−0.0001, +0.0175];
  vs as is +0.0163 [+0.0002, +0.0311]. Not closer.
- Opaque (t < 0.2): two-date − as is +0.0364 [+0.0148, +0.0596] (all, 28 tiles), +0.0128 [−0.0020, +0.0217] (roads, 13
  tiles). Two-date leaves opaque pixels uncorrected (grey identical, below), so the feature change there comes from the
  corrected surroundings inside the same DINOv2 window.
- **Absolute levels put the result in context:** thin-cloud road strips sit at 0.70 for every arm. The pre-storm
  **before** image is at 0.48 on the same pixels, and the clear guard is at 0.48 for as is. The date-gap noise floor
  (NOAA against NOAA, 8 tiles, clear ground) is 0.38. The satellite against NOAA on the same pixels is 0.49. So under
  thin cloud every after-image arm is far from NOAA, and no de-hazer closes much of the gap. That gap is about 0.2 above
  clear ground and about 0.3 above the noise floor.

### Outcome 2 (against He 2011): no arm is closer than He 2011
On road strips two-date is +0.0102 [+0.0002, +0.0184] further from NOAA than He 2011 (Holm-adjusted p not significant).
On all pixels the difference is +0.0018 [−0.0073, +0.0104].

### Outcome 3 (guard, clear ground): **fails on feature distance; passes on grey for two-date**
| Clear guard | feature Δ vs as is (all pixels, 45 tiles) | feature Δ (roads, 40 tiles) | grey change (all, 132 tiles) |
|---|---|---|---|
| two-date | +0.0185 [+0.0075, +0.0306] | +0.0291 [+0.0115, +0.0499] | 0.61 [0.43, 0.82] grey levels |
| He 2011 | +0.0215 [+0.0124, +0.0327] | +0.0278 [+0.0169, +0.0439] | 34.3 [30.7, 38.0] |
| two-date + spotter gate | +0.0188 [+0.0074, +0.0295] | +0.0296 [+0.0126, +0.0480] | 1.60 [1.01, 2.20] (62 tiles) |

Two-date barely changes clear-ground pixels (0.61 grey levels on average, so it passes the < 1 grey-level rule). Even so,
their DINOv2 tokens move away from NOAA by more than the ±0.01 the plan allows. Reading: `sn8_dino.tokens` runs
ViT-L on 2 × 2 windows of the whole tile with global attention, so correcting cloud elsewhere in the window changes the
tokens of untouched clear patches. The feature-distance guard is therefore not local, and this caveat applies to every
feature-distance comparison here. He 2011 changes the whole image (34 grey levels), so it fails both checks.

### Outcome 4 (honest gate): t ranks recovery modestly
AUC of t for "recovered" (two-date distance below the guard's 95th percentile, 0.848) = **0.652 [0.591, 0.718]** over
38 tiles. The recovered share is 0.78 where t ≥ 0.2 and 0.57 where t < 0.2. Mean distance is 0.712 vs 0.815. Discard
curve: dropping the lowest-t 50% of gated pixels lowers the mean distance from 0.729 to 0.675, and dropping 90% lowers
it to 0.605. So CANNOT ASSESS (t < 0.2) does mark ground that is recovered less often, but t is a weak ranker.

### Outcome 5 (cloud detection; upper-noise check, not a cloud label)
Disagreement = the tone-matched satellite and NOAA differ by more than the guard's 99th percentile (110 grey levels):

| Mask | F1 | 95% interval | precision | recall | tiles |
|---|---|---|---|---|---|
| dark rise | 0.507 | [0.376, 0.607] | 0.38 | 0.78 | 132 |
| dark rise | 0.543 | [0.383, 0.654] | 0.38 | 0.94 | 45 (spotter tiles) |
| spotter | 0.536 | [0.418, 0.633] | 0.38 | 0.92 | 45 |

The two masks are indistinguishable on these tiles.

### Outcome 6 (DINOv2 change cue per road, against pre vs NOAA): no signal under cloud
Spearman ρ between each arm's pre-vs-post change cue and the pre-vs-NOAA cue:

| Group | as is | He 2011 | two-date | spotter-gated |
|---|---|---|---|---|
| cloudy roads (158) | −0.235 [−0.442, −0.046] | −0.292 [−0.474, −0.104] | −0.238 [−0.447, −0.040] | −0.150 [−0.419, +0.061] |
| thin-cloud roads (70) | −0.010 [−0.383, +0.396] | −0.005 | +0.035 [−0.362, +0.425] | +0.004 |
| clear roads, ceiling (209) | 0.602 [0.349, 0.755] | 0.524 | 0.592 | 0.562 |

On clear roads the satellite change cue tracks the NOAA change cue (ρ ≈ 0.6). Under cloud no arm recovers it.

### Call level (Revision 1 item 1): raw agreement rises, but beyond chance it stays near zero
Agreement of each arm's per-road flood calls with the calls on the NOAA image. Exact McNemar is on roads where
exactly one of the arm and as is agrees with NOAA (p only where significant):

| Group | as is | He 2011 | two-date | spotter-gated |
|---|---|---|---|---|
| thin-cloud roads (70, 28 tiles) | 0.329 [0.179, 0.553] | 0.514 (+0.186 [+0.075, +0.278]; 14 fixed / 1 broken, p = 0.001) | 0.686 (+0.357 [+0.111, +0.534]; 28 / 3, p = 5e-6) | 0.729 (+0.400 [+0.132, +0.554]; 30 / 2, p = 3e-7) |
| all cloudy (158, 35 tiles) | 0.316 | 0.399 (+0.082 [+0.013, +0.161]; 16 / 3, p = 0.004) | 0.462 (+0.146 [−0.021, +0.338]; 32 / 9, p = 4e-4) | 0.475 (+0.158 [−0.013, +0.339]; 34 / 9, p = 2e-4) |
| opaque-tile roads (88, 7 tiles) | 0.307 | 0.307 | 0.284 | 0.273 |
| clear roads, ceiling (209, 51 tiles) | 0.670 | 0.756 (27 / 9, p = 0.004) | 0.718 (13 / 3, p = 0.02) | 0.746 (21 / 5, p = 0.003) |

**This is not evidence of recovery.** The frozen detector calls **91% of thin-cloud roads** and 87% of cloudy roads
flooded on the NOAA image. It also calls 70% of clear roads flooded, where the published labels mark 40% (83 / 209).
Against the published labels on clear roads, its accuracy on the NOAA image is 0.60 (as is: 0.75). The NOAA image is out
of domain for a detector trained on satellite pairs, so it calls "flooded" far more often. Each arm's agreement then
rises with its own share of flooded calls. On thin-cloud roads, two-date's agreement (0.686) equals its flooded-call
share (0.686). **Post-hoc check (not pre-registered; `s5b_posthoc_kappa.py`, `s5b_kappa.json`):** chance-corrected
agreement (Cohen's κ) on thin-cloud roads is +0.026 [−0.066, +0.182] for as is, +0.051 for He 2011, +0.092
[−0.085, +0.325] for two-date and +0.126 [−0.077, +0.342] for spotter-gated. All cloudy roads: +0.041 to +0.087. Clear
ceiling: +0.35 to +0.48. Beyond chance, no arm's calls under cloud agree with the NOAA-image calls. On thin-cloud roads,
accuracy against the published labels falls from 0.857 (as is) to 0.471 (two-date), because the de-hazed roads are
called flooded more often. The labels there were made without seeing under the cloud (evidence 16), so this does not
settle which calls are right.

### Label gap (Revision 1 item 8; a finding, not a score)
On the 158 scored cloudy roads, the detector on the NOAA image calls 138 flooded. 17 of these are among the 17 marked
flooded, and 121 are not marked. As the paragraph above shows, the NOAA-image detector over-calls floods (70% on clear
roads against 40% marked). **The 121 are therefore not a count of missed floods.** They need a human look at the NOAA
photos, not this detector.

### Secondary (outcome 7; no arm is chosen on these) and diagnostics
- **Grey error to NOAA, thin cloud, roads (37 tiles):** as is 71.5, He 2011 40.2, two-date 27.2 grey levels. Two-date
  − as is = −44.3 [−58.4, −28.9]. The large pixel-level gain is exactly the pixel/task rank flip Revision 1 item 2
  warned about (SEN12MS-CR, AllClear). Edge correlation in thin cloud does not improve: two-date − as is = −0.032
  [−0.044, −0.021] (all pixels, 73 tiles).
- **Ref-Diff leakage check (thin road strips):** every arm is closer to NOAA than to the pre-storm image. Two-date: 0.706
  to NOAA vs 0.753 to before, closer to before on only 3 of 33 tiles. No sign that two-date copies the before image.
- **Noise floor (8 tiles with an aligned second flight):** NOAA vs NOAA 0.382 feature distance and 17.4 grey levels;
  satellite vs NOAA on the same clear pixels 0.490 and 17.6.
- **Spread check (optional):** Spearman of the two-date output's spread across the gate settings with distance to NOAA
  is +0.034 (pixels: 977,469), and with grey error −0.118. It is not a useful uncertainty.

### Figures (`figures/ida_clear_view/`)
- `F1_tile_status.png`: every development tile, coloured by NOAA coverage and alignment.
- `F2_panels_<tile>.png`, for 0_13_5, 2_21_42, 0_19_13, 2_18_44 and 2_22_41 (the 5 scored tiles with the most
  thin-cloud pixels, chosen without labels): before, after, He 2011, two-date, NOAA grey and colour, and feature-distance
  maps for as is and two-date with thin and opaque outlines. Every grey panel uses NOAA's display range, so hazy
  images saturate to white (e.g. 0_13_5, mostly opaque).
- `F3_alignment_0_11_3.png`, `F3_alignment_0_16_11.png`: before and after the AROSICS-style correction, with tie points.
- `F4_outcomes.png`: per-tile differences in thin road strips and the clear guard, and the t discard curve.

### Deviations (all recorded here, none changes a pre-registered rule)
1. **Crash and resume.** The 22:55 kernel panic stopped `s2_prep` part-way. Every cached file was load-checked
   afterwards. Two prep files were written by an earlier code version, with a "before image" alignment fallback that was
   later removed (0_14_7, 0_15_6), so they were moved to `ida_clear_view_cache/stale_pre_crash/` and redone. On
   2026-10-30 the run was stopped once more on purpose, to drop from 2 to 1 worker while memory was low. That stop cut
   off 0_16_4, which was moved aside and redone.
2. **Atomic writes:** `s2_prep.py` now writes each tile's file to a temp file and renames it, so a stop cannot leave a
   partial file. Contents and results are unchanged. The original is kept as `s2_prep_before_atomic_write.py`.
3. **Bug fix in `s4_calls.py`:** tile 2_27_34 has no roads in its label file, so `road_rows` built a frame without
   columns and raised `KeyError: 'image'`. The fix gives an empty frame its key columns. The original is kept as
   `s4_calls_before_fix.py`. The 58 per-tile road tables already cached were reused, and the reproduction check passed
   again on the rerun.
4. **Post-hoc κ** (above): added after the results, and labelled as post-hoc.
5. **Compute budget (written into `s3_score.py` before scoring):** DINOv2 scoring covered 10 of the 30 sampled clear
   tiles, and the noise floor covered the first 8 tiles with an aligned second flight.

## Steps 3-5 in short
- Under thin cloud, no de-hazer brings the post image measurably closer to what NOAA's aircraft saw. Measured by the
  representation the change detector uses, two-date is not closer than as is (+0.0071 [−0.0049, +0.0173] on road
  strips), and not closer than He 2011. All arms stay about 0.2 further from NOAA than clear ground is.
- Two-date fixes pixel brightness: grey error on thin road strips falls from 71 to 27 grey levels. That gain does not
  carry into DINOv2 features, the per-road change cue (ρ ≈ 0 under thin cloud, against 0.6 on clear roads), or
  chance-corrected call agreement (κ ≤ 0.13).
- t is a weak but real "can we trust this" signal (AUC 0.65 [0.59, 0.72]).
- The NOAA-image route as a stand-in truth is limited by the detector's domain shift: it calls 70% of clear roads
  flooded against 40% labelled. A truly independent test needs a different reference or objective, as Justin noted on
  29 Oct.
