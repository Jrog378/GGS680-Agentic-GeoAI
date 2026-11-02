# Test plan: two-date and He cues together (written before running)

Written 2026-10-25 23:33 EDT, before any result of the new arm. Code: GeoAI-Roads 1532e9a (the modules used are
unchanged since 5d325d9). Script: `evidence/pilot_scripts/evaluate_both_dehazers.py`.

Justin (2026-10-25): "cant we use both He and two date?"

## Status
**Exploratory.** It runs on development roads (Louisiana-East train + val) that were looked at before: the 24 flooded
roads under thin cloud have been scored by every earlier arm. The results are reported whatever they are. Confirmation
needs a second event.

## Primary arm: "both cues"
- **Cues, for every road:** the production features from both de-hazers, side by side, prefixed `td_` and `he_`:
  - `td_`: two-date de-hazing without the corner edit, built exactly as in `preregistration_twodate_cornerfix.md`
    (`corrected_table(gate_tiles, "darkref")` on the 99 tile-rule tiles with a non-empty cloud gate; as-it-is cues on
    the other 101);
  - `he_`: single-image de-hazing (He et al. 2011), `corrected_table(all_tiles, "dehaze")` on all 200 tile-rule
    tiles, as in `preregistration_he_dehazed_training.md`. The one road with undefined variogram cues (0_16_12) is
    filled by the production model's median imputer.
  - Roads on tiles the tile rule sets aside keep their as-it-is cues in both halves (as before; they are never trained
    on or scored).
- **Everything else identical to the earlier arms:**
  - production flood model;
  - trained on the assessable roads;
  - 5 folds by tile (`StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=662)`), every road held out once.

## Roads
- 24 trusted flooded roads under thin cloud (measure: found);
- 69 dry-labelled roads under thin cloud (labels untrusted; measure: called flooded);
- 175 assessable control roads on the same 39 tiles (measure: right).
- Clear-sky benchmark: the 95 assessable roads labelled flooded on those 39 tiles (the earlier arms found 81).

## Outcomes
- Found / called flooded / right per group, with tile-resampled 95% intervals (5000 resamples, rng seed 662, drawn in
  the same order as before, so the earlier arms reproduce their intervals).
- Exact McNemar, "both cues" against:
  1. none (as it is, production);
  2. He 2011 trained de-hazed;
  3. two-date trained de-hazed (no corner edit).
- Nine paired tests (three groups x three comparisons), not corrected for multiplicity; read as exploratory.
- Note before running: He already finds 22 of 24, so on the found measure "both cues" can fix at most 2 roads against
  He, and the exact test cannot reach p < 0.05 there (smallest possible p = 0.5). The informative comparisons against He
  are the dry-labelled flood calls and the control accuracy.

## Post hoc rules (chosen after seeing the calls)
Labelled as post hoc wherever they are reported. Built from the existing calls, no new training:
- **AND:** flooded only if both two-date (no corner edit) and He trained de-hazed say flooded;
- **OR:** flooded if either says flooded.
- Reported for the same three groups and the clear-sky benchmark, each against none (exact McNemar), with the same
  intervals.

## Data rules
Development roads only: the script asserts `set(roads.split) <= {"train", "val"}`. No test tiles, no north negative
set, no Germany or Louisiana-West, no all-splits label folder, no `allow_held_out=True`.
