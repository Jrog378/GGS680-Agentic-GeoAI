# Test plan: two-date de-hazing on the flood calls (written before running)

Written 2026-10-25 16:46 EDT, before any result. Code frozen at GeoAI-Roads 2ec5346:
- `dark_reference_dehaze`;
- `corrected_table(tiles, "darkref")`.

Justin (2026-10-25): "set this up to be run on the flood cells so we can present that too".

## Status
**Exploratory.** These roads were looked at on 2026-10-24 with an earlier fit, so this is not the confirmatory test. That
test is on unseen roads, under methodology v2. Nothing below changes after the results are seen, and the results are
reported whatever they are.

## Data (development only)
- **Roads:** `touched_roads(include_cloudy=True)`, the SpaceNet 8 Louisiana-East training and validation tiles. No test
  tiles, no north negative set, no sealed areas.
- **Roads under thin cloud:** roads on tiles that the tile rule scores, with at least 20% of their strip under the
  dark-rise mask (93 roads on 39 tiles in the pilot). They split into two groups:
  - **trusted flooded:** labelled flooded (24 in the pilot). Under cloud, a flooded label can be trusted.
  - **dry-labelled:** the rest (69 in the pilot). Under cloud, a dry label cannot be trusted, because analysts left out
    what they could not see.
- **Control:** the assessable roads (production's cloud rule, tile rule + road rule) on the same 39 tiles.

## Model
- Production's flood model and features (`production_model()`, `production_features()`).
- Trained in 5 folds by tile (StratifiedGroupKFold, shuffled, seed 662) on the assessable roads only, as in production.
- Each held-out road is then called with its features measured three ways:
  1. **as it is:** the uncorrected after image;
  2. **single image:** de-hazed with He et al. (2011) (`dehaze`), the baseline;
  3. **two-date:** de-hazed with `dark_reference_dehaze`.

  In arms 2 and 3, every road feature on the 39 tiles is measured again on the corrected after image.

## Outcomes
- **Primary:** flooded found on the trusted flooded roads under thin cloud, two-date against as it is, with an exact
  two-sided McNemar test.
- **Secondary:**
  1. the same, two-date against single image;
  2. accuracy on the control roads, two-date against as it is (fixed / broken counts and McNemar);
  3. dry-labelled roads under thin cloud called flooded, by arm. This is reported, not scored as error, since those
     labels are untrusted;
  4. the primary split by `road_handling` (CORRECT against CANNOT ASSESS). This one is descriptive.
- **Reporting:** the numbers go in `evidence/01` and on the deck. Roads are never re-picked after the results are seen.
