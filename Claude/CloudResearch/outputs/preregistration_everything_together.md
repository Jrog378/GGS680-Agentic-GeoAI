# Test plan: everything together (written before running)

Written 2026-10-26 00:15 EDT, before any result of the new arms. Code: GeoAI-Roads 1532e9a, clean working tree.
Script: `evidence/pilot_scripts/evaluate_everything_together.py`. Outputs: `everything_together_numbers.json`,
`everything_together_calls.csv`, `evaluate_everything_together.log`.

Justin (2026-10-26): "are you able to start testing with everything all together".

## Status
**Exploratory.** It runs on development roads (Louisiana-East train + val) that every earlier arm has scored, and the
24 flooded roads under thin cloud have been looked at many times. Choosing the best of many arms on these roads favours
the development set. The results are reported whatever they are. Confirmation needs the sealed test tiles or a
second event.

## Arms
All arms use the production flood model (tuned random forest, `n_jobs=-1`). Where the DINOv2 change vector is used, it
is reduced to 16 principal components inside each fold, exactly as in `Code/dino_test.ipynb`:
`make_pipeline(ReduceColumns(DINO_VECTOR), make())`, with the vector from `with_dino`.

Building blocks:
- raw 96: `production_features()` on the raw images, which is 93 classical + 3 DINOv2 change cues;
- td_ 96 and he_ 96: the same 96 cues from the two-date de-hazer (no corner edit) and from He 2011, built exactly as
  in "both cues" (`preregistration_both_dehazers.md`; cached `corrected_table` tables);
- vector: `DINO_VECTOR` (1,024) going to 16 PCs.

| Arm | Columns into the model |
|---|---|
| production | raw 96 |
| production + DINOv2 vector (best so far) | raw 96 + vector |
| both cues (tonight) | td_ 96 + he_ 96 |
| **everything together (primary)** | raw 96 + td_ 96 + he_ 96 + vector (304 after the PCA) |
| ablation: without de-hazing | raw 96 + vector. This is the best-so-far arm by construction, so it is reported once. |
| ablation: without the DINOv2 vector | raw 96 + td_ 96 + he_ 96 |
| ablation: without classical (raw) | raw 3 DINOv2 cues + td_ 96 + he_ 96 + vector. The de-hazed copies of the classical cues stay. |
| secondary ablation: without any classical cue | raw 3 + td_ 3 + he_ 3 DINOv2 cues + vector |

The cloud gate stays as in production: opaque (tile rule) and thin-cloud (road rule) roads are "cannot assess". They
are not trained on and not scored, except in set (iii), whose purpose is to score them.

## Folds and scoring sets
The splitter is the same everywhere: `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)` by tile. Each
set is split over its own roads, as each was scored before.

- **(i) 798 assessable roads: primary.**
  - Folds are split over the 798, and each fold's model is fitted on the other folds' roads.
  - This is how production's logged 83.0% was made. It was checked before this plan was written, on production only:
    TP 394, FN 47, FP 89, TN 268.
- **(ii) All 891 tile-rule roads, for comparison with the logged runs.**
  - The construction is the logged one: folds split over the 891, every training-fold road fitted (the logged runs had
    no road rule). So the road-rule gate is not part of this set.
  - Checked before the plan: classical 93 gives the logged 401/64/87/339, and production (96) gives the logged
    408/57/83/343.
  - The script also checks that production + vector reproduces the logged 409/56/80/346 (`2026-10-23T151346_dino_test`).
    If it does not, the script stops.
- **(iii) Cloud groups: tonight's construction.**
  - Folds are split over all 1,037 development roads, each fitted on the training folds' assessable roads, and every
    road is called.
  - Groups:
    - 24 trusted flooded roads under thin cloud (measure: found);
    - 69 dry-labelled roads under thin cloud (labels untrusted; measure: called flooded);
    - 175 assessable control roads on the same 39 tiles (measure: right);
    - the clear-sky benchmark, the 95 assessable flooded roads on those tiles (measure: found).
  - Check: production and "both cues" must reproduce `cloudvars_calls.csv` and `both_dehazers_calls.csv` call for call,
    and their group intervals must reproduce `both_dehazers_numbers.json`. If not, the script stops.
  - The same calls are also scored on the 798 and the 891, as a sensitivity check of the fold split.

## Outcomes
- **Sets (i) and (ii), per arm:**
  - the confusion matrix (TP, FN, FP, TN);
  - accuracy, precision, recall (flooded found), specificity (dry kept dry), F1 and MCC;
  - tile-resampled 95% percentile intervals for each, from 2,000 resamples with seed 662, drawn as in
    `held_out_report`, so the accuracy intervals match the logged ones.
- **Set (iii), per group:** count, share and a tile-resampled 95% interval (5,000 resamples, seed 662, drawn in the
  same group order as tonight), plus the confusion counts.
- **Paired tests** (`paired_report`: accuracy difference with a 5,000-resample tile interval, roads fixed and broken,
  exact McNemar), in every set and group:
  - everything together against production, against the best so far, and against both cues;
  - each ablation against everything together.

## Primary test and promotion rule
- **Primary:** everything together against production on (i), the 798.
- Production's rule (`Code/results/production.json`): on the same held-out roads, the gain must be > 0, its 95%
  tile-resampled interval must exclude 0, and McNemar's exact p must be < 0.05. Of several confirmed options, the
  largest gain is promoted.
- **The rule is applied with `sn8_stages.confirm` (read-only).** The report says only whether everything together would
  pass. `production.json` is not written: the script checks its hash before and after.
- **Secondary:**
  - the same rule on (ii);
  - everything together against the best so far on (i), the rule's largest-gain clause.
- Note before running: the vector arm was held back on 2026-10-23 because production has no in-fold PCA. Everything
  together needs that PCA too, plus both de-hazers at inference time. So a pass would be a candidate for Justin, not a
  promotion.
- Every other test is exploratory and is not corrected for multiplicity.
  - Sets: (i), (ii) and the 4 groups.
  - Per set: 3 comparisons, plus 2 ablations and 1 secondary ablation against everything together. The
    without-de-hazing ablation is the best-so-far comparison.
  - Each arm is also tested against production, for the rule's largest-gain clause.

## Data rules
- Development roads only: the script asserts `set(roads.split) <= {"train", "val"}`.
- It does not read the test tiles, the north negative set, Germany, Louisiana-West, any all-splits label folder or the
  HRC_WHU test images, and it never passes `allow_held_out=True`.
- It works from cached feature tables only. A DINOv2 cache miss stops the script, so no GPU is used.
- It does not touch `sn8_dino3.py`.
