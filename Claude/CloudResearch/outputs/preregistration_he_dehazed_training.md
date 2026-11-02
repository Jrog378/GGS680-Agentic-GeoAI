# Test plan: the single-image baseline (He et al. 2011), model trained on de-hazed images (written before running)

Written 2026-10-25 19:53 EDT, before any result. Code: GeoAI-Roads 5d325d9 (`corrected_table(tiles, "dehaze")`
on all 200 tile-rule tiles). Script: `evidence/pilot_scripts/evaluate_he_dehazed.py`.

## Why
The rubric reviewer found that only the two-date method was given de-hazed training. This run gives the baseline the
same training, so the slide 7 comparison is fair.

## Design
- **Identical to arm 2 of `preregistration_cloud_variables.md`,** except the cues come from single-image de-hazing:
  - production flood model;
  - 5 folds by tile, seed 662;
  - trained on the assessable roads with de-hazed features on every tile.
- **Roads:** the same three groups:
  - 24 trusted flooded roads under thin cloud;
  - 69 dry-labelled roads under thin cloud;
  - 175 assessable control roads on the same 39 tiles.
- **Outcomes:**
  - flooded found, dry-labelled called flooded, and control accuracy;
  - paired against none (as it is) and against two-date trained de-hazed (arm 2), by exact McNemar;
  - tile-resampled 95% intervals for every arm and group.
- **Status:** exploratory, on roads seen before. The results are reported whatever they are.

## Deviation (logged 2026-10-25 21:45 EDT, before any outcome was computed)
The first run stopped at a guard in the script: one road (tile 0_16_12) is flat after single-image de-hazing, so its
six variogram cues are undefined (NaN, as `semivariogram` documents). The guard was stricter than the production
model, which fills missing values with the median. The guard now checks that every road has a row and allows NaN only
in variogram cues. No outcome had been computed when this was changed.
