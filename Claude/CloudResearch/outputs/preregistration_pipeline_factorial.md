# Test plan: the library pipeline as a full factorial (written before running)

Written 2026-10-26 02:25 EDT, before any of the new arms was run. Code: GeoAI-Roads `55c8fc2`, clean working tree.
Script: `evidence/pilot_scripts/evaluate_pipeline_factorial.py`. Outputs: `pipeline_factorial_numbers.json`,
`pipeline_factorial_calls.csv`, `evaluate_pipeline_factorial.log`. Figures: `figures/pipeline_factorial/`.

Justin (2026-10-26): "Use all these techniques together. it should be a pipeline of tools that all interact to get the
optimal result test with and without them to understand their impacts strengths and weaknesses as well as the optimal
combos".

## Status
**Exploratory, development data only (Louisiana-East train + val). Nothing is promoted.**
- 7 of the 16 cells were scored before, at the primary fold seed (marked * below). Choosing the best of 16 arms on
  these roads favours the development set. Confirmation needs the sealed test tiles or a second event.
- Every result is reported, whatever it is. Departures go in `evidence/13_pipeline_factorial.md`, not here.

## Arms: 2 x 4 x 2 = 16, library tools only (no DINOv3)
Every arm uses the production flood model, `FLOOD_MODELS[production_model()]` (tuned random forest, 300 trees,
`n_jobs=-1`, model seed 662), trained on the roads its gate keeps. CPU only.

| Stage | Options |
|---|---|
| **1 Gate** (the tile rule is kept in both) | **a** production: `assessable(roads, production_cloud_rule())`, dark-rise road rule. **b** spotter: `sn8_cloudspot.spot_gate`, i.e. the tile rule + bright + texture + DINOv2 road rule at the same 20% strip cut. Its per-road shares `spot_road` are read from last night's `cloud_spotting/gate_roads.csv` (not recomputed). |
| **2 Cues** | **raw**: the 96 production cues. **td**: the 96 two-date cues (no corner edit) in their place. **he**: the 96 He 2011 cues in their place. **both**: raw 96 + td_ 96 + he_ 96. Built exactly as `evaluate_both_dehazers.py` / `evaluate_everything_together.py`, from the cached `corrected_table` tables (a cache miss stops the script). |
| **3 Features** | **prod**: the columns from stage 2. **vec**: the same + the DINOv2 change vector (1,024) reduced to 16 PCs inside each fold, `make_pipeline(ReduceColumns(DINO_VECTOR), make())`. |

Seen before at the primary seed (*): a·raw·prod (production), a·raw·vec, a·td·prod, a·he·prod, a·both·prod,
a·both·vec (everything together), b·raw·prod. The "both" option keeps raw, whereas td and he replace it, as asked.

Tool count, for the simplicity rule: gate b = 1, td = 1, he = 1, both = 2, vec = 1. Production has 0 and the largest
arm, b·both·vec, has 4.

## Folds
- `StratifiedGroupKFold(5, shuffle=True, random_state=s)` by tile, split over **all 1,037 development roads**, as in
  `run_gate.py` (`gated_calls`) and tonight's cloud tests. Each fold's model is fitted on the training-fold roads its
  gate keeps and calls every held-out road. So both gates share the same folds, and the cloud groups can be scored.
- **Primary seed s = 662. Then 20 more seeds, s = 1-20.** The model seed stays 662.
- **Reproduction checks at s = 662 (the script stops if any fails):**
  - a·raw·prod = `cloudvars_calls.csv` production, call for call; on its 798 kept roads 390/51/91/266;
  - b·raw·prod = `gate_roads.csv` spotter calls on its 790 kept roads (416/34/88/252);
  - a·raw·vec, a·both·prod, a·both·vec = `everything_together_calls.csv` C1037 best so far, without the vector and
    everything together;
  - a·td·prod = `twodate_cornerfix_calls.csv`; a·he·prod = `he_dehazed_calls.csv`;
  - 757 shared roads; the spotter's `cloud_dark_rise_road` column matches the road table.

## Scoring
- **(i) Shared roads: the 757 kept by both gates (primary set).** Per arm at s = 662: TP, FN, FP, TN, accuracy,
  precision, recall, specificity, F1, MCC, each with a tile-resampled 95% interval (2,000 resamples, seed 662, drawn
  as `held_out_report`). Across the 21 seeds: mean, SD, min and max accuracy; seeds above / equal to / below
  production.
- **(ii) Each gate's own kept roads** (798 under a, 790 under b): the same metrics at s = 662, the roads set aside and
  how many of them are flooded, and accuracy on the roads only that gate keeps. Seed mean accuracy.
- **(iii) Cloud groups, defined by production's rule for comparability:** 24 trusted flooded roads under thin cloud
  (found), 69 dry-labelled roads under thin cloud (called flooded), 175 control roads on the same 39 tiles (right),
  and the 95-road clear-sky benchmark (found). Count, share and a 5,000-resample tile interval at s = 662; seed mean.
  Under gate b some of these roads are training roads in other folds; every score is still held out.
- **Paired tests against production (a·raw·prod) at s = 662:** `paired_report` (accuracy difference, 5,000-resample
  tile interval, roads fixed / broken, exact McNemar) on the shared roads; for gate-a arms also on the 798.

## Main effects and interactions (shared roads)
- **Main effect** of an option = its accuracy minus the stage's baseline option (a, raw, prod), averaged over every
  combination of the other two stages (8 cells for gate and features, 4 for each cue option).
- **Two-way interactions:** gate x cues (does each cue option gain more under b than under a), gate x vector, cues x
  vector, each averaged over the third stage. The three-way terms go in the JSON only.
- Each contrast is reported (1) at s = 662 with a tile-resampled interval, (2) as the mean, SD, min and max over the
  21 seeds with the seeds > 0, and (3) with a **seed-averaged interval**: each road's correctness averaged over the 21
  seeds, the contrast taken road by road, tiles resampled (2,000, seed 662). An interaction "matters" when interval
  (3) excludes 0. All are reported.
- The same main effects are reported on the cloud-group measures (secondary).

## Choosing the optimal combo (fixed now)
1. Rank arms by mean shared-road accuracy over the 21 seeds. The top arm is the provisional best.
2. Every arm with fewer tools whose seed-averaged paired interval against the top arm includes 0 is a tie.
3. **The optimal combo is the arm with the fewest tools among the top arm and its ties**; equal tool counts go to the
   higher mean accuracy. Production itself can be chosen this way.

## Promotion rule (read-only)
`Code/results/production.json`: on the same held-out roads, gain > 0, 95% tile interval above 0, exact McNemar
p < 0.05. Applied with `sn8_stages.confirm` to each arm against production on the shared roads at s = 662 (and on
the 798 for gate-a arms), with the number of seeds out of 21 in which it would pass. `production.json` is never
written: its sha256 is checked before and after.
- Note before running: gate b's spotter is trained on HRC_WHU (academic use only), and vec needs the in-fold PCA,
  so a pass would be a candidate for Justin, not a promotion.
- Nothing is corrected for multiplicity (16 arms, 21 seeds, several sets).

## Data rules
- Development roads only: the script asserts `set(roads.split) <= {"train", "val"}`.
- It never reads the test tiles, the north negative set, Germany, Louisiana-West, any all-splits label folder or the
  HRC_WHU test images, and it never passes `allow_held_out=True`.
- Labels are the published labels, unmodified. Cached tables only; a DINOv2 or `corrected_table` cache miss stops the
  script, so no GPU is used.
