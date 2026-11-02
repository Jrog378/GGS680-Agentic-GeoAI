# Test plan: cloud as an extra variable, with and without de-hazing (written before running)

Written 2026-10-25 17:26 EDT, before any result. Code: GeoAI-Roads 2ec5346, unchanged. Script:
`evidence/pilot_scripts/evaluate_cloudvars.py`.

Justin (2026-10-25): "Can we treat the cloud as an extra variable since we are using random forest to predict change".
And: "It didn't help because we were using a method that didn't clear the clouds" (the 2026-10-23 arm "cloud shares as
features" ran on the uncorrected images).

## Status
**Exploratory.** It runs on development roads that were looked at before. Nothing changes after the results are seen,
and the results are reported whatever they are.

## Data
- The development roads, the same groups as `preregistration_twodate_roads.md`:
  - 24 trusted flooded roads under thin cloud;
  - 69 dry-labelled roads under thin cloud;
  - the 175 assessable control roads on the same 39 tiles.
- **Cues** are measured two ways:
  - on the after image as it is;
  - on the two-date de-hazed after image (`corrected_table(tiles, "darkref")`) for all 200 tiles the tile rule scores.
    A tile with no cloud gate comes out unchanged.

## Arms (production flood model, 5 folds by tile, seed 662; every road held out once)
| Arm | Cues | Trained on | Extra variables |
|---|---|---|---|
| 1 | as it is | assessable roads (production) | none |
| 2 | two-date | assessable roads | none (2026-10-25 test) |
| 3 | as it is | tile-rule roads (thin-cloud roads included) | the eight cloud columns (2026-10-23 arm) |
| 4 | two-date | tile-rule roads | the eight cloud columns |
| 5 | two-date | tile-rule roads | the eight cloud columns + the fit's share in the gate and share opaque |
| 6 | two-date | tile-rule roads | none (separates the training set from the variables) |

**Why arms 3 to 6 train on cloudy roads:** the cloud variables only vary there. Those roads include dry labels that
cannot be trusted under cloud, so a model with cloud variables can learn "cloudy means dry" (the labelling rule). That
is the known risk.

## Outcomes
- **Primary:** flooded found on the 24 trusted flooded roads under thin cloud, arm 4 against arm 2 (exact McNemar).
  This is Justin's hypothesis: cloud variables help once the clouds are cleared.
- **Secondary:**
  - arm 4 against arm 3 (the same variables, de-hazed or not);
  - arm 5 against arm 4;
  - arm 6 against arm 2;
  - dry-labelled roads called flooded, by arm;
  - accuracy on the 175 control roads, every arm against arm 1.
