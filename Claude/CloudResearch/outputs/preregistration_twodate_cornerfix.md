# Test plan: two-date de-hazing trained de-hazed, rerun without the corner edit (written before running)

Written 2026-10-25 21:55 EDT, before any result. Code: GeoAI-Roads 5d325d9. Script:
`evidence/pilot_scripts/evaluate_twodate_cornerfix.py`.

## Why
- The cloud-gate agent found that `dark_reference_dehaze` edits a ~20 m corner on tiles with an empty cloud gate.
  The cause is `distance_transform_edt` on an all-True array.
- The arm "two-date · trained de-hazed" (`preregistration_cloud_variables.md`, arm 2) trains on every tile-rule
  tile, including the cloud-free ones, so its numbers include those edits. It was also run on 2ec5346, before the
  fallback fix.

## The fix
- With an empty gate there is nothing to correct, so the after image is left exactly as it is. The library fix
  (`if not gate.any()`: return the after image unchanged) is committed after the road-finding agent's run ends,
  because that run imports this module.
- This test applies the same rule without editing the library:
  - tiles with a non-empty gate get `corrected_table(gate_tiles, "darkref")` on the current code (5d325d9);
  - tiles with an empty gate keep their as-it-is features.
- The script first checks, on two empty-gate tiles, that `corrected_rows(tile, "none")` reproduces the as-it-is
  features. If the check fails, the script stops.

## Design
- Otherwise identical to arm 2:
  - production flood model;
  - 5 folds by tile, seed 662;
  - trained on assessable roads with corrected features on every tile-rule tile.
- **Roads:** 24 trusted flooded under thin cloud; 69 dry-labelled under thin cloud; 175 assessable control roads on
  the same 39 tiles.
- **Outcomes:**
  - flooded found, dry-labelled called flooded, and control accuracy, with tile-resampled 95% intervals;
  - exact McNemar against none and against He 2011 trained de-hazed (`preregistration_he_dehazed_training.md`).
- **Status:** exploratory, on roads seen before. The results are reported whatever they are, and replace arm 2's
  numbers on the slides.
