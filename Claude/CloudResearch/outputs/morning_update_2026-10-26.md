# Morning update, 26 Oct 2026 (overnight runs; development data only, sealed data untouched)

## 1. Everything together (flood model): done
- **What it is:** the production random forest with every library piece switched on:
  - the cloud gate;
  - the cues from both de-hazers (two-date and He);
  - the classical cues;
  - the 3 DINOv2 change cues;
  - the DINOv2 change vector.
- **Result:** it does not pass the promotion rule. On the 798 assessable roads it is 83.6% against production's 83.0%
  (+0.6, 95% CI −0.7 to +1.9; 20 fixed / 15 broken; not significant). On the 891 roads it is 1 point lower, also not
  significant.
- **Under thin cloud it is the best balance so far:**
  - it finds 21 of 24 trusted flooded roads (production 17);
  - it keeps dry-labelled flood calls at 6 of 69 (production 6, two-date 29);
  - it gets 141 of 175 clear roads on those tiles right (production 136).
  - None of these gaps is significant.
- **The fold split moves the ranking.** Across 20 fold seeds production ranges from 81.6% to 84.2%. Arms a point
  apart can't be ranked with 798 roads, so more data is needed (see the requirements doc).
- **Classical cues:** they still matter. Removing every classical cue costs 2.9 points (p = 0.024). Once the de-hazed
  copies are in, the raw classical copy adds nothing.
- **Details:** `evidence/01_measured_results.md` (last section) and
  `evidence/pilot_scripts/everything_together_numbers.json`.

## 2. Cloud spotting (classical vs DINOv2, with DINOv3 as the benchmark): done, a big gain
- **Best library spotter: bright rule + texture + DINOv2.**
  - On the 120 HRC_WHU development images (5 folds by image) it scores F1 0.868, against 0.648 for today's dark rule:
    +0.22 [+0.19, +0.25]. It is better on 112 of the 120 images.
  - It reaches 97% of the DINOv3 benchmark (F1 0.892).
  - Texture is the classical tool that matters: +0.15. DINOv2 adds +0.11 on top of classical.
  - By land cover it is weakest on barren (0.78) and snow (0.83), where bright ground causes false alarms.
- **As the flood model's cloud gate** (SpaceNet 8 development tiles, in place of the dark-rise road rule):
  - On the 757 roads both gates keep, the flood model is right more often: +1.9 points [+0.4, +3.4], 25 roads fixed
    against 11 broken, p = 0.029. **Correction from section 3:** that split happened to be the best of 21. Averaged
    over 21 splits the gate's gain is +0.5 points (main effect +0.34, interval includes 0). Real, but small.
  - It sets aside 247 roads against 239, but only 18 of them flooded against 27. The dark-rise rule reads pale
    floodwater as cloud.
- **Caveats:**
  - There are no cloud labels on SpaceNet 8, so the gain shows up in training, not as proof of better cloud spotting
    there.
  - HRC_WHU is academic use only, so the spotter is research-only until the licence question is settled.
- **Your decision:** see section 3. The pipeline test changes the recommendation.
- **Details:** `evidence/12_cloud_spotting_pipeline.md`, `figures/cloud_spotting/`. Library module
  `sn8_cloudspot.py` (commit 55c8fc2, not pushed). The DINOv3 code stays in research folders.

## 3. The whole pipeline, with and without each tool: done
- **What was tested:** 16 combinations: 2 cloud gates × 4 de-hazing options × with/without the DINOv2 change vector.
  Each was run over 21 different fold splits, because one split can't rank arms a point apart. Scored on the 757
  roads both gates keep.

| Tool | Average effect on accuracy | 95% interval | Splits where it helps |
|---|---|---|---|
| **DINOv2 change vector** | **+1.25 points** | **+0.56 to +1.95** | **21 of 21** |
| Spotter cloud gate | +0.34 | −0.19 to +0.96 | 16 of 21 |
| Both de-hazers + raw cues | +0.11 | −0.38 to +0.59 | 13 of 21 |
| Two-date de-hazing alone | −0.36 | −1.06 to +0.27 | 4 of 21 |
| He 2011 de-hazing alone | −0.66 | −1.62 to +0.23 | 1 of 21 |

- **Only the DINOv2 change vector helps reliably.** The other tools are within noise on clear roads.
- **Under thin cloud the cloud tools do matter:**
  - The spotter gate adds +5.6 points of trusted flooded roads found, and He adds +8.1, both in 21 of 21 splits. They
    overlap: together they don't add up, so they do the same job.
  - The spotter gate finds +4.0 points more flooded roads in clear sky on those tiles.
  - Two-date and He also raise flood calls on the untrusted dry-labelled cloudy roads (+24.5 and +15.4 points); the
    vector pulls that back down (−10.1).
- **Best overall:** spotter gate + both de-hazers + vector, 84.6% average, against production's 83.2%. MCC 0.709 at
  the main split, against 0.640.
- **Chosen by the rule written in advance:** the simplest arm that ties the best, i.e. production gate + raw cues +
  DINOv2 vector, 84.5% average.
  - It passes the promotion rule at the main split (+2.2, p = 0.002), but only in 5 of 21 splits.
  - No arm passes in more than 7.
- **What this means:**
  - The gains are real but about 1–1.5 points, too small to confirm with 757 roads.
  - Under thin cloud, the cloud tools (spotter gate, He) clearly help find flooded roads.
  - Nothing was promoted; production is unchanged.
- **Decision for you (one at a time):** add the DINOv2 change vector to production as a candidate, then confirm it on
  more data? Its in-fold PCA has to go into production code first.
- **Details:** `evidence/13_pipeline_factorial.md`, figures in `figures/pipeline_factorial/`.

## 4. DINOv3 benchmark, frozen and fine-tuned: done (research only, not in the library)
- **Finding roads: DINOv3 beats DINOv2.**
  - Frozen: classical + DINOv3 reaches F1 0.747, against production's 0.713 (+0.033, significant). DINOv3 alone gets
    0.733, against 0.683 for DINOv2 alone.
  - Fine-tuned (last 2 blocks + head, trained on the 186 training tiles, scored on the 40 validation tiles): F1 0.780,
    +0.067 over production (significant).
- **Flood per road: frozen DINOv3 does not beat DINOv2.**
  - DINOv3 cues added to the classical cues add nothing (+0.3, not significant); DINOv2's added +1.2.
  - Both backbones together, without the classical cues, reach 85.9%, the best single number, but not significantly
    above production.
- **Fine-tuned DINOv3 flood head:**
  - On the validation roads it is +5.7 to +9.6 points over production (e.g. 91.3% against 81.7% on 104 roads, 10
    fixed / 0 broken).
  - **Caveat:** 77 of those 104 validation roads continue from a training tile with the same label, and all 10 fixes
    are on them. Treat it as a lead, not a result, until a spatially separate check.
- **Library goal:**
  - For roads, the library (classical + DINOv2, F1 0.713) is at 95% of frozen DINOv3 (0.747) and 91% of fine-tuned
    DINOv3 (0.780).
  - For flood calls, the library already matches DINOv3.
- **Details:**
  - write-up: `evidence/11_dinov3_baseline.md`;
  - code: `evidence/pilot_scripts/dinov3/`;
  - checkpoints: `~/Masters/models/finetuned/dinov3_sat493m/` (research-only; Meta DINOv3 License).

## 5. One finding that affects everything: validation is not spatially independent
Most validation roads continue from training tiles. The validation-based numbers (road finding, fine-tuning) may be
optimistic. The cheapest fix needs no download: re-split Louisiana-East by area. That changes the logged split, so it
is your call.

## Decisions waiting for you (I'll ask one at a time)
1. Re-split Louisiana-East by area for a spatially independent development check.
2. Add the DINOv2 change vector to production as a candidate (section 3).
3. The spotter cloud gate (section 2), which is research-only for now because of the HRC_WHU licence.
4. Whether the hazy band next to a cloud counts as haze (the ring fix).
5. The data and compute options in `outputs/requirements_more_data_and_compute.md`: downloads, derived flood labels,
   a cloud GPU.

The requirements doc is at `outputs/requirements_more_data_and_compute.md`.

## 2026-10-30: fine-tuned DINOv3 road finding (A-ft) under spatial folds (research only)
- **Done:** all 5 outer folds, 29 Oct 21:46 to 30 Oct 10:38. The Mac crashed at 22:55 (kernel panic). Outer fold 1 had
  finished and was kept; the run resumed at 08:13 and redid fold 2 from the start. The folds are independent, and the
  redone fold 2 matched the crashed attempt's losses to 4 decimals. Development tiles only; nothing was promoted and
  `production.json` was not touched.
- **Result (held-out validation-split cells, seed 662):** A-ft F1 **0.743** (0.681-0.807), against production's 0.709.
  - **Against production: +0.033 (+0.008 to +0.065), beats.**
  - **Against A-head: +0.084 (+0.055 to +0.118), beats.**
  - The plan gives no McNemar test for cells; "beats" means the block-resampled interval is above 0.
  - It is above production and above A-head in all 5 folds. Per fold: 0.643 / 0.773 / 0.822 / 0.704 / 0.725, against
    production's 0.558 / 0.761 / 0.779 / 0.691 / 0.697.
- **Last night's +0.067 holds in direction only.** Under spatial folds the gain is about half (+0.033), and +0.067 lies
  just above the new interval. Most of the drop is A-ft's own: it fell from 0.780 to 0.743.
- **Against frozen classical + DINOv3:** +0.010 (-0.021 to +0.038), no detectable difference. More fold seeds would
  firm this up, at about 3 h of GPU each.
- **Details:** `evidence/15_dinov3_spatial_cv.md`, "A-ft, run 29-30 October". Pictures: `spatialcv_trackA_f1.png`
  (updated), `spatialcv_per_fold.png` (updated) and `spatialcv_cells_0_14_7.png` (new), all in
  `evidence/pilot_scripts/dinov3/`.
