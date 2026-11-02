# 20: Sub-threshold haze and texture (2026-10-29; EXPLORATORY, development data only)

These are our own measurements, not literature. Phase A (diagnosis) ran. Phase B (fixes) did **not** run, because its
pre-set gate failed (see Verdict).

## Question
Justin (2026-10-29): "I think the misty clouds are messing with the texture of our imagery and isnt being detected by
our cloud detector since it doesnt look like a cloud, however this is clearly some form of noise in our image that can
throw off results especially texture results which might allow us to increase our accuracy if we can figure out whats
going on".

This splits into three testable parts:
1. Is there haze on roads that production's cloud gate calls clear?
2. Does that haze shift the change features of roads that did not change?
3. Does it go with production's held-out errors?

## Data
- **Roads:** Louisiana-East train + val only: 226 tiles and 1,037 roads (`touched_roads(include_cloudy=True)`).
  - The 798 roads production's gate keeps are the focus: 441 flooded and 357 not marked flooded.
  - Test, negative, Germany, Louisiana-West and the HRC_WHU test images were not read. `allow_held_out` was never
    passed.
- **Labels:** the SpaceNet 8 published labels, unmodified. No new labels were made.
- **Held-out calls:** production arm c00 (no de-hazing, tuned forest, 96 production columns, gate (a)) under the
  spatial folds S at seeds 662 and 1–20, read from `spatial_cv/spatial_cv_flood_calls.npz`.
  - Per road, the right share is the mean over the 21 seeds. Production's accuracy on the 798 is 78.58%, as in
    evidence/14.
- **Blocks:** the 3 x 3-tile blocks of `spatial_folds.fold_table(662)`. The fold module was imported, not edited
  (sha256 `6ab96c29666193235477…`).
- **Imagery:** the greyscale tiles, and for HOT the ORIGINAL 3-band RGB (`tile_pair`'s `before_rgb` / `after_rgb`).
  This was the first use of colour.

## Method
Scripts are in `evidence/pilot_scripts/haze_texture/`:
- `haze_common.py`: the scores;
- `run_scores.py`: all 226 tiles, giving `haze_roads.csv` and `haze_tiles.csv`;
- `analyze_A.py`: steps 1–4, giving `phaseA_numbers.json`, `phaseA_texture_inflation.csv`,
  `phaseA_error_quartiles.csv` and `phaseA_elevated.csv`;
- `extra_checks.py`: `phaseA_extra.json`;
- `fig_panels.py`: the example-road panels.

Everything ran on CPU under `nice -n 10`, with no GPU.

**The four scores.** Each uses no gate and no threshold. Each is summarised over every road strip (`sn8_cloudsym.road_strips`,
the same pixels as `sn8_roads`) as the median, 90th percentile and mean. Each also has a **null version computed the
same way on the before date**: the touched before images are cloud-free, so the null shows how high a score gets with
no haze.

| | Score (after date) | Null (before date) |
|---|---|---|
| (a) rise | Dark channel of the after image minus the tone-matched before dark channel (`sn8_clouds.dark_channel`, `sn8_refhaze.tone_curve` on pixels no mask flags, 10 m margin), centred on the tile's no-mask median. | Dark before minus tone-matched dark after |
| (b) atten | −log((std_after + 1)/(std_before + 1)) of the 5.5 m local std, minus the tile's median on no-mask pixels. Above 0 means contrast was lost. | The mirror image (−atten) |
| (c) HOT | Haze Optimized Transform (Zhang, Guindon & Cihlar 2002, *RSE* 82:173–187). The clear line red = k·blue + b is fitted per tile on the least-hazy pixels: no mask, lowest quarter of rise, not saturated or near black. HOT = B sinθ − R cosθ, centred on the fit pixels. **Caveat:** this is 8-bit display RGB, not reflectance. Water, shadow and bright roofs also move HOT. | HOT of the before RGB, using its own line |
| (d) spot | Mean cloud probability from the HRC_WHU-trained spotter in the strip, sub-threshold values included. **Deviation:** the `classical` library arm stands in for the gate's `classical + DINOv2 − dark`. That arm needs DINOv2 tokens of every SN8 tile, which are not cached and would need the GPU. | The same on the before image |

**What each step did:**
- **Agreement (step 1):** Spearman correlations among the scores and against the existing masks: dark-rise, bright,
  dark and the chosen spotter's `spot_road`.
- **Missed haze (step 2):** counts the kept roads whose after-date score is above the 99th percentile of its null.
- **Texture inflation (step 3):**
  - Data: the 357 unchanged roads (kept, not marked flooded), 141 tiles, 48 blocks.
  - Change features: the 31 classical, GLCM and texture `_change` features and the 3 DINOv2 cues.
  - Each feature is signed **flood-ward**: multiplied by the sign of (flooded median − not-flooded median) on the 798.
    Above 0 then means "looks more flooded".
  - Statistic: Spearman of each signed feature with each score, with 95% intervals from 2,000 resamples of the 3 x 3
    blocks. Benjamini–Hochberg q is given over the 34 features. A within-tile version (tile fixed effects on ranks)
    is the confound check.
- **Errors (step 4):**
  - Error share by score quartile, on all 798, on the not-flooded roads (false alarms) and on the flooded roads
    (misses), each with a Q4 − Q1 contrast.
  - A logistic model, error ~ z(score) + flooded, fitted on the 21-seed error shares.
  - Intervals come from 2,000 block resamples.
- **Phase B gate** (set in the brief before scoring): run Phase B only if, for the primary haze scores (a) rise or
  (c) HOT, both of these intervals lie above 0:
  1. the mean flood-ward inflation over the 31 texture and classical features;
  2. the haze coefficient in the label-adjusted error model.

  (b) atten is not a primary score because it is circular: it is a local-std change, almost the same quantity as
  `texture_change`. (d) is not primary because the stand-in spotter fires on bright, smooth roads (see step 1).

## Results

### 1. The scores barely agree on the "clear" roads
- **All 1,037 roads:** the scores track the masks. Rise against dark-rise share ρ = 0.65; spot against it 0.63;
  HOT 0.36; atten 0.33.
- **The 798 kept roads:** the scores hardly agree.

  | Pair | ρ |
  |---|---|
  | rise – HOT | 0.07 |
  | rise – atten | **−0.17** |
  | HOT – atten | 0.17 |
  | rise – spot | 0.31 |

  The independent haze measures, dark channel and colour, do not see the same thing below the gate. Contrast loss is
  *negatively* related to the dark-channel rise there.
- **Tile level (226 tiles):** raw dark-channel rise against the dark-rise mask share is ρ = 0.74, and HOT against the
  masks is about 0.28.
- **The stand-in spotter fires on roads themselves:** its median probability on the roads of a clear tile is about
  0.5–0.7, and it is higher on the BEFORE date than the after (median 0.35 against 0.11 on the 798). That makes it a
  weak haze instrument here.

### 2. Is there haze the masks miss? Rarely, but where there is, it is real and visible
- **Against the before-date null, the gate's clear roads do not carry more haze than cloud-free before images:**

  | Score | Above null p99 | Above p95 | Above p90 | Median, after vs null |
  |---|---|---|---|---|
  | rise | **1 of 798 (0.1%)** | 2.0% | 3.3% | −3.5 vs +4.7 |
  | HOT | **0 (0%)** | 0.1% | 0.5% | −0.14 vs +1.38 |
  | spot | 1 (0.1%) | 0.3% | 1.1% | — |
  | atten | 17 (2.1%) | 6.0% | 12.5% | — |

  - No haze would give 1%, 5% and 10% above the three cuts.
  - Only 1 road is above the null on 2 or more of the 4 scores, and 0 such roads have no mask pixel. 692 of the 798
    have no pixel under any mask.
  - atten is the only score in excess, and it is circular (see below).
- **The pictures nevertheless show genuine sub-threshold mist on a handful of roads:**
  - `0_18_12 way/847378778`: rise 89.7, 6% under the dark-rise mask, not flooded.
  - `0_17_13 way/847378796`: rise 60.3, 4% masked, not flooded.

  Both are milky veils that blur the road and the ground around it. The gate passes them because less than 20% of
  each strip crosses the Otsu cut. These are the "misty clouds" Justin describes. They are the top 1–3% of the kept
  roads by rise, roughly 10–25 roads, not a widespread layer.
- **The highest-HOT roads are mostly not haze:**
  - `2_30_37`: a crop field that greened;
  - `2_14_51`: a flooded road (HOT rises over turbid water);
  - `0_13_1`: half the crop is hazy, along with a no-data edge.
- **Clean controls** (`2_21_56`, `2_20_56`): sharp in both dates; rise and HOT are negative.
- **Tile-wide haze:** the tone curve, like the features' histogram matching, absorbs haze spread evenly over a tile.
  The tile's *raw* dark-channel rise (median 15.9, 90th percentile 50.7 grey levels over kept-road tiles) is not
  related to errors: label-adjusted log-odds +0.16 per SD [−0.12, +0.48].
- **Figures:**
  - `figures/haze_texture/A2_score_distributions.png`
  - `figures/haze_texture/A2_hazy_roads_panels.png`: 6 high-score roads and 2 controls. Columns: before RGB, after RGB,
    rise map, HOT map, attenuation map, with the strip outlined.

### 3. Haze does distort texture on unchanged roads, but it pushes in both directions
Dark-channel rise against flood-ward change on the 357 unchanged roads:
- **Toward "flooded"** (CI above 0): 6 features, all coarse-scale or edge cues that flooding lowers and haze also
  lowers.

  | Feature | ρ | 95% CI |
  |---|---|---|
  | wavelet3 (2–4 m) | +0.35 | [0.23, 0.44] |
  | ridge | +0.27 | [0.12, 0.39] |
  | Gabor 8 m energy | +0.26 | [0.14, 0.39] |
  | Gabor 4 m energy | +0.26 | [0.13, 0.37] |
  | edge | +0.19 | [0.05, 0.30] |
  | GLCM correlation | +0.19 | [0.05, 0.33] |

- **Away from "flooded"** (CI below 0): 15 features.

  | Feature | ρ | 95% CI |
  |---|---|---|
  | grey change | **−0.52** | [−0.59, −0.43] |
  | GLCM contrast | −0.36 | |
  | wavelet1 | −0.36 | |
  | GLCM entropy | −0.34 | |
  | Laws L5E5 | −0.32 | |
  | `texture_change` | −0.31 | |
  | … | | |

  Haze brightens the road, and flooding darkens it. Flooding also *raises* fine-scale texture here (debris, ripples),
  while haze lowers it.
- **Mean over the 31 features: −0.089 [−0.125, −0.044]**. Haze on balance makes an unchanged road look slightly *less*
  flooded, not more.
- The within-tile correlations agree (mean −0.091), so this is not a tile-level confound.
- **DINOv2 cues:** +0.11 [−0.03, +0.24] with rise. With HOT the DINOv2 change cues do rise: +0.21 [+0.08, +0.33]. But
  they fall to +0.05 within tile, so this is mostly between-tile differences (crop or water colour), not haze on the
  road.
- **HOT:** mean over the 31 features +0.007 [−0.038, +0.057]. 7 features are above 0 and 3 below. It shows the same
  coarse-scale pattern (Gabor 8 m, ridge, LBP edge, about +0.2).
- **atten is circular:** it correlates up to |ρ| 0.5 with the features (edge +0.55, `texture_change` −0.51) because it
  measures the same local-std change. These are not haze effects.
- **Effect size:** a single-score Spearman of 0.2–0.35 on individual coarse-scale cues is real but moderate, and it
  is partly cancelled by the brightness and fine-scale cues.
- **Figure:** `figures/haze_texture/A3_texture_inflation.png`.

### 4. Haze does not detectably drive production's errors once the label is accounted for
Production's held-out accuracy on the 798 is 78.58% (S, mean over 21 seeds).

| Score | All 798, Q1→Q4 error | Q4 − Q1 | Logistic, error ~ z(score) + flooded (log-odds per SD) | False alarms only | Misses only |
|---|---|---|---|---|---|
| (a) rise | 17.3 → 19.6 → 22.3 → 26.4% | +9.1 [+0.8, +18.0] | **+0.04 [−0.13, +0.24]** | −0.12 [−0.44, +0.09] | +0.22 [−0.09, +0.92] |
| (c) HOT | 22.8 → 17.9 → 19.7 → 25.3% | +2.5 [−7.0, +13.2] | **−0.02 [−0.23, +0.25]** | +0.12 [−0.19, +0.53] | −0.29 [−0.61, +0.08] |
| (b) atten (circular) | 18.1 → 16.9 → 20.8 → 29.9% | +11.7 [+0.3, +23.9] | +0.37 [+0.14, +0.62] | **+0.62 [+0.26, +1.16]** | +0.10 [−0.34, +0.45] |
| (d) spot (stand-in) | 29.6 → 20.9 → 21.7 → 13.6% | −16.0 [−29.1, −4.6] | −0.62 [−0.93, −0.35] | −1.13 [−1.61, −0.77] | +0.50 [+0.06, +1.00] |

- **Rise:** the raw quartile trend comes from the label mix. Hazier roads are more often flooded, and flooded roads
  are missed more under haze.
  - Misses by rise quartile: 10.0 → 12.3 → 14.9 → 21.8%, Q4 − Q1 +11.8 [+1.0, +23.9].
  - The continuous logistic within the flooded roads is +0.22 [−0.09, +0.92], which includes 0.
  - So there is a hint that sub-threshold haze hides floods, but it is not established. False alarms do not rise
    with haze.
- **atten:** the strong false-alarm relation is expected and says nothing about haze. A dry road whose local contrast
  fell (mud, debris, wet surface, or an unlabelled flood) looks flooded *by construction*. On the kept roads atten is
  negatively related to the dark-channel rise (ρ −0.17).
- **spot:** the stand-in spotter is high on bright, smooth roads. Bright after means not-dark water, so it has fewer
  false alarms. This is not a haze effect.
- **Figure:** `figures/haze_texture/A4_errors_by_quartile.png`.

## Verdict
1. **Haze the masks miss exists, but it is rare.**
   - Against cloud-free before images, the 798 "clear" roads show no excess on the dark-channel or colour (HOT) haze
     scores: 0.1% and 0% above the null's 99th percentile.
   - A few roads (the top 1–3% by dark-channel rise, for example `0_18_12` and `0_17_13`) carry real, visible mist
     with less than 20% of the strip over the mask cut.
2. **It does distort texture, as Justin suspected, but not in one direction.**
   - On unchanged roads, haze suppresses contrast at every scale.
   - Coarse-scale and edge cues therefore move toward "flooded" (ρ up to +0.35).
   - Brightness and fine-scale texture move away from it (ρ down to −0.52).
   - Net: −0.09 [−0.13, −0.04].
3. **It does not measurably cost accuracy.**
   - With the flooded label as a covariate, the haze coefficient is +0.04 [−0.13, +0.24] for rise and −0.02 for HOT.
   - The only lead is that flooded roads under more sub-threshold haze are missed more often: Q4 − Q1 +11.8 points
     [+1.0, +23.9], but the continuous model's interval includes 0.
4. **Phase B gate: failed** for both primary scores. The inflation interval for rise is *below* 0, the HOT one spans 0,
   and both error intervals span 0. **Phase B was not run.** The brief made Phase B conditional, so no arms were
   scored and nothing was promoted.
5. **Inference (not measured):**
   - The forest already sees both sides of the haze shift, and the two directions roughly cancel. Haze-normalised
     texture is therefore unlikely to add accuracy on these roads.
   - The one place worth a targeted look is misses on flooded roads under faint haze. That needs a pre-registered test
     of its own.

## Deviations
- **(d) uses the classical HRC_WHU spotter, not the gate's `classical + DINOv2 − dark`.** The DINOv2 tokens of SN8
  tiles are not cached, and this run was CPU-only.
- **"Clearly elevated" was defined against a before-date null** (99th percentile), since the brief gave no cut.
- **The rise score is centred on each tile's no-mask median.** Without this the tone-matched rise and fall are not
  comparable. As a result, tile-wide haze is absorbed; it is checked separately through the raw tile rise.
- **`production.json`'s sha256 is now `e592414b9bd322b9…`, not the `c3295b2069c2bf63…` logged in evidence/14.** This
  run only reads it (through `production_features` / `production_cloud_rule`) and wrote nothing. The calls used are
  the saved c00 calls from evidence/14.
