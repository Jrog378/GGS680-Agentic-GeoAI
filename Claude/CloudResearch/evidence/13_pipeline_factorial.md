# 13: The library pipeline as a full factorial (2026-10-26; EXPLORATORY, development data only)

Our own measurements, not literature.

**Why:** Justin (2026-10-26): "Use all these techniques together. it should be a pipeline of tools that all interact to
get the optimal result test with and without them to understand their impacts strengths and weaknesses as well as the
optimal combos". This is the final integrated test of the library pipeline: every combination of its three stages,
repeated over 21 fold splits. DINOv3 is research-only and is not part of it.

**Setup:**
- **Plan:** `outputs/preregistration_pipeline_factorial.md`, written at 02:25 EDT, before any new arm was run.
- **Code:** GeoAI-Roads `55c8fc2`, clean tree. No module was edited.
- **Script:** `evidence/pilot_scripts/evaluate_pipeline_factorial.py`, with `evaluate_pipeline_factorial.log`.
  - Outputs: `pipeline_factorial_numbers.json`, `pipeline_factorial_calls.csv` (every road, the seed-662 call of
    each arm and its flooded-call share over the 21 seeds), `pipeline_factorial_seeds.csv` (per seed and arm) and
    `pipeline_factorial_seed_calls.npz` (every call, for re-scoring).
  - Figures: `pipeline_factorial_figures.py`, writing to `figures/pipeline_factorial/`.
- **Run time:** 1,806 s on the CPU, from cached tables only, with the forest at `n_jobs=-1` and no GPU. That is
  16 arms x 21 seeds x 5 folds = 1,680 forest fits.
- **Checks** (each passed, or the script would have stopped):
  - **Calls reproduce, call for call, at seed 662:**
    - production gives `cloudvars_calls.csv`, 390/51/91/266 on its 798;
    - the spotter gate with raw cues gives last night's `gate_roads.csv` calls on its 790, 416/34/88/252;
    - production + vector, both + raw and both + raw + vector give `everything_together_calls.csv` (C1037);
    - two-date gives `twodate_cornerfix_calls.csv`, and He gives `he_dehazed_calls.csv`.
  - **Intervals reproduce:** production's cloud-group intervals match `both_dehazers_numbers.json`, and the accuracy
    intervals match `held_out_report`.
  - **Counts:** 757 shared roads; the dark-rise shares in `gate_roads.csv` equal the road table's.
  - **Registry:** `production.json` has the same sha256 before and after the run.
- **Data:**
  - Louisiana-East train + val only: 1,037 roads on 217 tiles, 468 flooded. The script asserts
    `set(roads.split) <= {"train", "val"}`.
  - Published labels, unmodified.
  - **Not read:** test tiles, the north negative set, Germany, Louisiana-West, any all-splits label folder and the
    HRC_WHU test images. `allow_held_out` was never passed.
- **Status:** nothing is promoted, and `production.json` was not written.

**Arms (2 x 4 x 2).** Every arm is the production flood model, the tuned random forest. It is trained on the roads
its gate keeps.

| Stage | Options |
|---|---|
| 1 Gate (tile rule in both) | **production**: dark-rise road rule. **spotter**: bright + texture + DINOv2 road rule, same 20% strip cut. Its per-road shares come from last night's `gate_roads.csv`. |
| 2 Cues | **none** (raw 96); **two-date** (td_ 96 in place of raw); **He 2011** (he_ 96 in place of raw); **both + raw** (raw + td_ + he_, 288) |
| 3 Features | **prod** (the stage-2 columns); **+ vector** (+ the DINOv2 change vector, 16 PCs fitted inside each fold) |

**Folds:**
- `StratifiedGroupKFold(5, shuffle=True)` by tile, over all 1,037 roads.
- Each fold is fitted on the training-fold roads its gate keeps, and every held-out road is called.
- Seed 662 is the primary split, with seeds 1–20 on top of it. The model seed stays 662.

**Shared roads:** the 757 roads both gates keep (431 flooded, 189 tiles). The same roads and the same folds are used
under both gates, so only the training roads differ.

## In short
**Evidence (measured):**
1. **The DINOv2 change vector is the one tool that reliably helps.**
   - Main effect on the shared roads: **+1.25 points** (seed-averaged 95% CI **+0.56 to +1.95**).
   - It is positive in **21 of 21** splits, and positive within either gate: +1.36 under production, +1.13 under the
     spotter.
   - All 8 arms with the vector beat all 8 arms without it on mean accuracy.
2. **No other main effect clears 0 on the shared roads.**

   | Tool | Main effect (points) | 95% CI | Splits above 0 |
   |---|---|---|---|
   | Spotter gate | +0.34 | −0.19 to +0.96 | 16 / 21 |
   | Two-date | −0.36 | −1.06 to +0.27 | 4 / 21 |
   | He 2011 | −0.66 | −1.62 to +0.23 | 1 / 21 |
   | Both + raw | +0.11 | −0.38 to +0.59 | 13 / 21 |

   - **He without the vector costs accuracy:** −1.09 [−2.29, −0.02], 0 of 21 splits up.
   - **He with the vector is neutral:** −0.22. This is the only shared-road interaction that clears 0: He x vector
     +0.87 [+0.18, +1.61].
   - No gate x tool interaction clears 0 on the shared roads.
3. **The 8 vector arms tie at the top.** They span 84.05–84.56% mean accuracy, and every paired interval against the
   top arm includes 0.
   - **Preregistered choice: production gate + no de-hazing + DINOv2 vector.**
     - It has 1 tool and reaches 84.48% ± 0.52 (SD over splits).
     - It beats production in 20 of 21 splits, by a mean +1.25 points.
     - It is the "best so far" arm of 2026-10-23.
   - The top arm by mean is spotter + both + raw + vector, at 84.56%. It is +0.08 above the chosen arm, with an
     interval of −0.84 to +1.03.
4. **The promotion rule passes at seed 662 but not reliably.**
   - The chosen arm against production passes on the shared roads: +2.2 [+0.9, +3.7], 23 fixed / 6 broken,
     p = 0.0023. It also passes on production's 798: +2.3, p = 0.0014.
   - But it passes in only **5 of 21** splits.
   - **Seed 662 is production's worst split** (82.4%, the lowest of 21; the mean is 83.24%), so seed-662 gains are
     larger than typical.
5. **Last night's spotter-gate gain was the luckiest split.**
   - Spotter + raw against production at seed 662 gave +1.85 points (p = 0.029), the largest of the 21 splits.
   - Over the 21 splits the mean is **+0.52** (range −0.79 to +1.85). It is higher in 15, lower in 5 and tied in 1, and
     the rule passes in 1 of 21.
6. **Under thin cloud the tools do differ. Production's road rule defines the groups, and these roads are set aside
   in production.** All values below are means over the splits.
   - **Trusted flooded roads (24):**
     - Production finds 72.6%.
     - The spotter gate adds +5.6 points (21 / 21 splits), and He adds +8.1 (21 / 21).
     - But they do not add up: **gate x He −13.0 [−27.6, −4.1]**, and gate x two-date −11.4 [−24.6, −2.9].
     - He adds +14.6 points under the production gate and +1.6 under the spotter gate.
   - **Dry-labelled roads (69, labels untrusted):** every cloud tool raises flooded calls from production's 10.4%.
     - Two-date: +24.5 points.
     - He 2011: +15.4 points.
     - Spotter gate: +15.3 points.
     - The vector lowers them by −10.1.
     - Worst arms: spotter + two-date at 54.3%, and spotter + He at 50.9%.
   - **Control (175 clear roads on the same tiles):** no main effect clears 0.
   - **Clear-sky benchmark (95 flooded clear roads on the same tiles):** the spotter gate finds +4.0 points more
     [+1.7, +6.4] (21 / 21 splits). Spotter + both + raw (+ vector) reaches 91.4–91.5%, against production's 85.6%.
7. **The gates themselves:**
   - Production sets aside 239 roads (27 flooded); the spotter sets aside 247 (18 flooded).
   - On its own kept roads, the best spotter arm scores 84.94% mean (b·both·vec) and the best production arm 83.86%.
     These are different road sets and cannot be compared directly.

**Inference (not measured):**
- **The vector carries the flood call on clear roads.** It is the only tool whose gain survives the change of split.
  The de-hazers change the cues of roads under or near haze. On the shared roads, which are mostly clear, that mostly
  adds noise.
- **The spotter gate and the de-hazers do the same job.** Each lets the model handle thin-cloud flooded roads.
  - The spotter does it by training on 19 of the 24 trusted flooded thin-cloud roads, which production sets aside.
  - The de-hazers do it by cleaning the cues.
  - So stacking them gains nothing: the strong negative gate x de-hazer interaction on the trusted flooded group.
- **That same help may be the cost on dry-labelled thin-cloud roads.**
  - Every cloud tool makes the model call more of them flooded.
  - The labels of those 69 roads cannot be trusted, so this is either found floods or false alarms, and the labels
    cannot say which.
  - The vector works the other way, so the vector arms are the most conservative on these roads.
- **The clear-sky benchmark gain of the spotter gate is in training.** The 95 roads are kept by production, and 87 of
  them by the spotter, and they are scored the same way. What changed is which neighbouring roads trained the model.
- **A single split cannot rank these arms.**
  - The SD over splits (about 0.5–0.7 points) is as large as most effects.
  - Seed 662 is production's worst split, which is why tonight's single-split gains looked larger.

## 1. The 16 arms on the shared roads (757 roads, 431 flooded)
"vs production" is the seed-662 paired difference with a 5,000-resample tile interval, roads fixed / broken and the
exact McNemar p. "Rule" is whether `sn8_stages.confirm` would pass it at seed 662, and in how many of the 21 splits.

| Arm (gate · cues · features) | Tools | Acc. seed 662 [95% CI] | Mean ± SD, 21 splits | Min–max | Splits > / = / < production | vs production, seed 662 [95% CI] | fixed / broken | McNemar p | Rule (662; splits) |
|---|---|---|---|---|---|---|---|---|---|
| spotter · both + raw · + vector | 4 | 85.6 [81.8–89.0] | **84.56 ± 0.60** | 83.0–85.6 | 20 / 0 / 1 | +3.2 [+1.4, +5.1] | 35 / 11 | 0.0005 | yes; 5/21 |
| spotter · none · + vector | 2 | 84.9 [81.4–88.2] | 84.55 ± 0.60 | 83.6–85.7 | 21 / 0 / 0 | +2.5 [+0.7, +4.4] | 32 / 13 | 0.0066 | yes; 4/21 |
| spotter · He 2011 · + vector | 3 | 84.4 [80.8–87.8] | 84.54 ± 0.62 | 83.1–85.6 | 21 / 0 / 0 | +2.0 [+0.3, +3.7] | 34 / 19 | 0.053 | no; 3/21 |
| **production · none · + vector (chosen)** | **1** | 84.7 [81.1–88.0] | **84.48 ± 0.52** | 83.4–86.0 | 20 / 0 / 1 | +2.2 [+0.9, +3.7] | 23 / 6 | 0.0023 | yes; 5/21 |
| production · both + raw · + vector (everything together) | 3 | 83.8 [80.1–87.2] | 84.42 ± 0.69 | 83.0–85.5 | 20 / 0 / 1 | +1.3 [+0.0, +2.7] | 20 / 10 | 0.099 | no; 7/21 |
| spotter · two-date · + vector | 3 | 84.9 [81.3–88.4] | 84.40 ± 0.55 | 83.8–85.7 | 21 / 0 / 0 | +2.5 [+0.5, +4.5] | 34 / 15 | 0.0094 | yes; 3/21 |
| production · two-date · + vector | 2 | 83.9 [80.3–87.2] | 84.20 ± 0.55 | 83.1–85.2 | 18 / 0 / 3 | +1.5 [−0.4, +3.4] | 28 / 17 | 0.14 | no; 1/21 |
| production · He 2011 · + vector | 2 | 83.9 [80.3–87.4] | 84.05 ± 0.60 | 82.7–85.1 | 18 / 1 / 2 | +1.5 [−0.6, +3.5] | 36 / 25 | 0.20 | no; 2/21 |
| spotter · both + raw · prod | 3 | 84.5 [80.8–88.1] | 83.85 ± 0.48 | 82.8–84.7 | 16 / 3 / 2 | +2.1 [+0.7, +3.7] | 26 / 10 | 0.011 | yes; 1/21 |
| spotter · none · prod (last night's spotter gate) | 1 | 84.3 [80.5–87.9] | 83.76 ± 0.63 | 82.4–84.9 | 15 / 1 / 5 | +1.8 [+0.4, +3.4] | 25 / 11 | 0.029 | yes; 1/21 |
| production · both + raw · prod | 2 | 83.0 [78.9–86.7] | 83.63 ± 0.49 | 82.8–84.5 | 13 / 2 / 6 | +0.5 [−1.0, +2.1] | 15 / 11 | 0.56 | no; 1/21 |
| **production · none · prod (production)** | 0 | 82.4 [78.5–86.1] | **83.24 ± 0.50** | 82.4–84.3 | — | — | — | — | — |
| spotter · two-date · prod | 2 | 83.5 [79.6–87.0] | 83.22 ± 0.56 | 82.3–84.5 | 6 / 2 / 13 | +1.1 [−0.6, +2.7] | 24 / 16 | 0.27 | no; 0/21 |
| production · two-date · prod | 1 | 82.7 [78.7–86.3] | 82.75 ± 0.51 | 81.6–84.0 | 4 / 2 / 15 | +0.3 [−1.3, +1.8] | 18 / 16 | 0.86 | no; 0/21 |
| spotter · He 2011 · prod | 2 | 82.6 [78.6–86.2] | 82.71 ± 0.38 | 81.9–83.4 | 3 / 3 / 15 | +0.1 [−1.8, +2.0] | 31 / 30 | 1.0 | no; 0/21 |
| production · He 2011 · prod | 1 | 81.9 [77.9–85.6] | 82.10 ± 0.56 | 81.0–83.2 | 0 / 0 / 21 | −0.5 [−2.3, +1.3] | 26 / 30 | 0.69 | no; 0/21 |

**Gain over production in each split** (points):
- Mean gain, from most to least:

  | Arm | Mean gain | | Arm | Mean gain |
  |---|---|---|---|---|
  | b·both·vec | +1.33 | | b·raw·prod | +0.52 |
  | b·he·vec | +1.31 | | a·both·prod | +0.39 |
  | b·raw·vec | +1.31 | | b·td·prod | −0.02 |
  | a·raw·vec | +1.25 | | a·td·prod | −0.48 |
  | a·both·vec | +1.18 | | b·he·prod | −0.53 |
  | b·td·vec | +1.16 | | a·he·prod | −1.14 |
  | a·td·vec | +0.97 | | | |
  | a·he·vec | +0.81 | | | |
  | b·both·prod | +0.62 | | | |

- The SD of each gain over the splits is 0.55–0.76.

## 2. Confusion matrices and metrics, shared roads, seed 662
Percent, with tile-resampled 95% intervals (2,000 resamples, seed 662).

| Arm | TP | FN | FP | TN | Accuracy | Precision | Recall | Specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|
| spotter · both + raw · + vector | 406 | 25 | 84 | 242 | 85.6 (81.8–89.0) | 82.9 (77.1–87.7) | 94.2 (91.4–96.5) | 74.2 (66.2–81.3) | 88.2 (84.3–91.2) | 0.709 (0.639–0.773) |
| spotter · none · + vector | 402 | 29 | 85 | 241 | 84.9 (81.4–88.2) | 82.5 (76.9–87.5) | 93.3 (90.6–95.6) | 73.9 (65.6–81.1) | 87.6 (83.9–90.6) | 0.695 (0.625–0.758) |
| spotter · He 2011 · + vector | 399 | 32 | 86 | 240 | 84.4 (80.8–87.8) | 82.3 (76.8–86.9) | 92.6 (89.3–95.3) | 73.6 (66.0–80.5) | 87.1 (83.3–90.1) | 0.683 (0.610–0.752) |
| **production · none · + vector (chosen)** | 395 | 36 | 80 | 246 | 84.7 (81.1–88.0) | 83.2 (77.6–87.9) | 91.6 (88.2–94.7) | 75.5 (67.7–82.2) | 87.2 (83.4–90.3) | 0.687 (0.615–0.754) |
| production · both + raw · + vector | 393 | 38 | 85 | 241 | 83.8 (80.1–87.2) | 82.2 (76.5–87.1) | 91.2 (87.7–94.3) | 73.9 (65.8–80.9) | 86.5 (82.6–89.7) | 0.668 (0.593–0.738) |
| spotter · two-date · + vector | 403 | 28 | 86 | 240 | 84.9 (81.3–88.4) | 82.4 (76.7–87.3) | 93.5 (90.5–95.9) | 73.6 (65.1–80.9) | 87.6 (83.9–90.7) | 0.695 (0.622–0.762) |
| production · two-date · + vector | 395 | 36 | 86 | 240 | 83.9 (80.3–87.2) | 82.1 (76.5–86.8) | 91.6 (88.3–94.4) | 73.6 (65.5–81.0) | 86.6 (82.6–89.7) | 0.671 (0.599–0.737) |
| production · He 2011 · + vector | 394 | 37 | 85 | 241 | 83.9 (80.3–87.4) | 82.3 (76.9–86.8) | 91.4 (87.7–94.6) | 73.9 (66.1–80.5) | 86.6 (82.6–89.8) | 0.671 (0.594–0.743) |
| spotter · both + raw · prod | 398 | 33 | 84 | 242 | 84.5 (80.8–88.1) | 82.6 (76.7–87.5) | 92.3 (88.8–95.3) | 74.2 (66.3–81.3) | 87.2 (83.2–90.4) | 0.685 (0.611–0.755) |
| spotter · none · prod | 397 | 34 | 85 | 241 | 84.3 (80.5–87.9) | 82.4 (76.6–87.3) | 92.1 (88.9–95.0) | 73.9 (66.1–81.3) | 87.0 (83.1–90.2) | 0.680 (0.603–0.752) |
| production · both + raw · prod | 392 | 39 | 90 | 236 | 83.0 (78.9–86.7) | 81.3 (75.3–86.3) | 91.0 (87.4–94.2) | 72.4 (64.1–79.9) | 85.9 (81.8–89.3) | 0.652 (0.568–0.728) |
| **production** | 385 | 46 | 87 | 239 | 82.4 (78.5–86.1) | 81.6 (75.7–86.5) | 89.3 (85.0–93.1) | 73.3 (65.1–80.6) | 85.3 (81.1–88.8) | 0.640 (0.561–0.717) |
| spotter · two-date · prod | 396 | 35 | 90 | 236 | 83.5 (79.6–87.0) | 81.5 (75.5–86.5) | 91.9 (88.6–94.7) | 72.4 (64.2–79.8) | 86.4 (82.4–89.6) | 0.664 (0.587–0.734) |
| production · two-date · prod | 390 | 41 | 90 | 236 | 82.7 (78.7–86.3) | 81.2 (75.4–86.2) | 90.5 (86.8–93.6) | 72.4 (64.2–80.0) | 85.6 (81.5–89.0) | 0.646 (0.567–0.719) |
| spotter · He 2011 · prod | 391 | 40 | 92 | 234 | 82.6 (78.6–86.2) | 81.0 (74.9–85.9) | 90.7 (87.0–93.9) | 71.8 (63.8–78.9) | 85.6 (81.3–89.0) | 0.644 (0.566–0.716) |
| production · He 2011 · prod | 383 | 48 | 89 | 237 | 81.9 (77.9–85.6) | 81.1 (75.1–86.1) | 88.9 (84.2–93.0) | 72.7 (64.9–79.4) | 84.8 (80.3–88.6) | 0.629 (0.549–0.706) |

**Measured:**
- Every gain over production is mostly in **recall**.
  - The chosen arm finds 395 flooded roads against 385 and keeps 246 dry against 239.
  - Spotter + both + raw + vector finds 406, and its specificity is close to production's (74.2 against 73.3).
- No arm's specificity interval is clear of any other's. Every arm calls 80–92 dry roads flooded.

## 3. Each gate's own kept roads (seed 662; mean over the 21 splits in the last column)
- **Production gate:**
  - Keeps 798 and sets aside 239: 27 flooded, 212 dry.
  - 41 roads only it keeps; 10 of them are flooded.
- **Spotter gate:**
  - Keeps 790 and sets aside 247: 18 flooded, 229 dry.
  - 33 roads only it keeps; 19 of them are flooded.

| Arm | TP | FN | FP | TN | Accuracy [95% CI] | Recall | Specificity | MCC | Roads only this gate keeps: right | Mean ± SD, 21 splits |
|---|---|---|---|---|---|---|---|---|---|---|
| production · none · prod | 390 | 51 | 91 | 266 | 82.2 [78.6–85.7] | 88.4 | 74.5 | 0.640 | 78.0% of 41 | 82.75 ± 0.48 |
| production · none · + vector | 400 | 41 | 83 | 274 | 84.5 [81.1–87.8] | 90.7 | 76.8 | 0.686 | 80.5% | 83.83 ± 0.66 |
| production · two-date · prod | 394 | 47 | 93 | 264 | 82.5 [78.8–85.9] | 89.3 | 73.9 | 0.645 | 78.0% | 81.85 ± 0.54 |
| production · two-date · + vector | 399 | 42 | 93 | 264 | 83.1 [79.6–86.4] | 90.5 | 73.9 | 0.659 | 68.3% | 83.29 ± 0.61 |
| production · He 2011 · prod | 390 | 51 | 98 | 259 | 81.3 [77.5–84.9] | 88.4 | 72.5 | 0.622 | 70.7% | 81.33 ± 0.53 |
| production · He 2011 · + vector | 401 | 40 | 93 | 264 | 83.3 [79.6–86.7] | 90.9 | 73.9 | 0.664 | 73.2% | 83.35 ± 0.56 |
| production · both + raw · prod | 397 | 44 | 93 | 264 | 82.8 [79.0–86.4] | 90.0 | 73.9 | 0.653 | 80.5% | 83.14 ± 0.45 |
| production · both + raw · + vector | 398 | 43 | 89 | 268 | 83.5 [80.0–86.8] | 90.2 | 75.1 | 0.666 | 78.0% | 83.86 ± 0.66 |
| spotter · none · prod | 416 | 34 | 88 | 252 | 84.6 [80.8–88.1] | 92.4 | 74.1 | 0.686 | 90.9% of 33 | 83.98 ± 0.62 |
| spotter · none · + vector | 421 | 29 | 88 | 252 | 85.2 [81.7–88.4] | 93.6 | 74.1 | 0.700 | 90.9% | 84.85 ± 0.58 |
| spotter · two-date · prod | 415 | 35 | 93 | 247 | 83.8 [80.2–87.3] | 92.2 | 72.6 | 0.670 | 90.9% | 83.48 ± 0.57 |
| spotter · two-date · + vector | 421 | 29 | 88 | 252 | 85.2 [81.7–88.5] | 93.6 | 74.1 | 0.700 | 90.9% | 84.71 ± 0.57 |
| spotter · He 2011 · prod | 410 | 40 | 96 | 244 | 82.8 [78.9–86.3] | 91.1 | 71.8 | 0.649 | 87.9% | 82.86 ± 0.41 |
| spotter · He 2011 · + vector | 418 | 32 | 89 | 251 | 84.7 [81.0–87.9] | 92.9 | 73.8 | 0.689 | 90.9% | 84.83 ± 0.60 |
| spotter · both + raw · prod | 417 | 33 | 86 | 254 | 84.9 [81.1–88.4] | 92.7 | 74.7 | 0.694 | 93.9% | 84.23 ± 0.48 |
| spotter · both + raw · + vector | 425 | 25 | 86 | 254 | 85.9 [82.3–89.3] | 94.4 | 74.7 | 0.716 | 93.9% | 84.94 ± 0.56 |

Each gate is scored on different roads here. The spotter gate keeps more flooded roads (450 of 790, against 441 of
798), and flooded roads are the easier class (recall about 90% against specificity about 74%). So the gap between the
two halves of this table is not a fair gate comparison: section 1 is.

## 4. Main effects and interactions (shared roads, accuracy points)
Four columns: the value at seed 662 with a tile interval; the mean, SD and min to max over the 21 splits; the splits
above / below 0; and the **seed-averaged interval**. That interval takes each road's correctness averaged over the 21
splits, forms the contrast road by road and resamples tiles (2,000). "Matters" means that interval excludes 0.

| Contrast | Seed 662 [95% CI] | Mean (SD) over splits | Min to max | > 0 / < 0 | Seed-averaged 95% CI | Matters |
|---|---|---|---|---|---|---|
| **main: spotter gate** | +1.07 [+0.26, +1.90] | +0.34 (0.36) | −0.21 to +1.07 | 16 / 5 | −0.19, +0.96 | no |
| **main: two-date** | −0.33 [−1.36, +0.51] | −0.36 (0.41) | −1.12 to +0.46 | 4 / 17 | −1.06, +0.27 | no |
| **main: He 2011** | −0.89 [−2.14, +0.23] | −0.66 (0.38) | −1.35 to +0.07 | 1 / 20 | −1.62, +0.23 | no |
| **main: both + raw** | +0.13 [−0.71, +0.89] | +0.11 (0.34) | −0.46 to +0.73 | 13 / 8 | −0.38, +0.59 | no |
| **main: DINOv2 vector** | +1.40 [+0.41, +2.37] | **+1.25 (0.24)** | +0.88 to +1.67 | **21 / 0** | **+0.56, +1.95** | **yes** |
| vector within the production gate | +1.55 | +1.36 (0.38) | +0.73 to +1.95 | 21 / 0 | +0.64, +2.12 | yes |
| vector within the spotter gate | +1.25 | +1.13 (0.22) | +0.63 to +1.45 | 21 / 0 | +0.41, +1.87 | yes |
| He without the vector | −1.12 | −1.09 (0.50) | −2.25 to −0.13 | 0 / 21 | −2.29, −0.02 | yes |
| He with the vector | −0.66 | −0.22 (0.53) | −1.12 to +0.99 | 7 / 14 | −1.12, +0.60 | no |
| interaction gate x two-date | −0.13 | +0.03 (0.50) | −1.19 to +1.06 | 10 / 10 | −0.52, +0.59 | no |
| interaction gate x He 2011 | −0.46 | +0.26 (0.63) | −0.66 to +1.78 | 15 / 6 | −0.35, +0.94 | no |
| interaction gate x both + raw | +0.66 | −0.11 (0.56) | −1.06 to +0.99 | 8 / 13 | −0.57, +0.32 | no |
| interaction gate x vector | −0.30 | −0.23 (0.38) | −0.79 to +0.40 | 6 / 14 | −0.58, +0.10 | no |
| interaction two-date x vector | −0.13 | +0.30 (0.43) | −0.40 to +1.06 | 16 / 5 | −0.10, +0.70 | no |
| **interaction He 2011 x vector** | +0.46 | **+0.87 (0.71)** | −0.26 to +2.11 | 19 / 2 | **+0.18, +1.61** | **yes** |
| interaction both + raw x vector | −0.53 | −0.27 (0.66) | −1.12 to +1.39 | 5 / 16 | −0.76, +0.26 | no |

- The de-hazers' within-gate effects are all within ±0.8 of 0, and none clears 0.
  - Production gate: two-date −0.38, He −0.79, both + raw +0.16.
  - Spotter gate: −0.35, −0.53 and +0.05.
- The three-way terms (gate x de-hazer x vector) average +0.18 to +0.37, and none clears 0.
- Every row, and the same table for each cloud group, is in `pipeline_factorial_numbers.json` under "contrasts".

## 5. Cloud groups (defined by production's road rule, for comparability)
Share over the 21 splits (mean), with seed 662 in brackets. Under the production gate all 93 thin-cloud roads are
"cannot assess", so its numbers there are what it would call if forced. The spotter gate keeps 19 of the 24 trusted
flooded roads and 14 of the 69 dry-labelled ones, and it sets aside 30 of the 175 controls (8 of the 95 benchmark
roads). Every call is still held out.

| Arm | Trusted flooded, thin cloud: found (24) | Dry-labelled, thin cloud: called flooded (69) | Control: right (175) | Clear-sky benchmark: found (95) |
|---|---|---|---|---|
| **production** | 72.6 (70.8) | 10.4 (8.7) | 77.6 (77.7) | 85.6 (85.3) |
| production · none · + vector (chosen) | 80.4 (70.8) | **7.6** (7.2) | 78.5 (80.6) | 85.2 (86.3) |
| production · two-date · prod | 84.9 (83.3) | 39.9 (42.0) | 74.9 (76.6) | 84.4 (85.3) |
| production · two-date · + vector | 86.1 (83.3) | 19.7 (18.8) | 77.6 (76.6) | 85.1 (84.2) |
| production · He 2011 · prod | 91.3 (91.7) | 17.3 (13.0) | 77.2 (77.1) | 88.4 (85.3) |
| production · He 2011 · + vector | 90.9 (87.5) | 11.0 (7.2) | 78.9 (78.9) | 88.7 (86.3) |
| production · both + raw · prod | 84.1 (83.3) | 10.3 (10.1) | 78.7 (78.3) | 87.8 (86.3) |
| production · both + raw · + vector | 84.9 (87.5) | 8.3 (8.7) | **79.2** (80.6) | 87.5 (88.4) |
| spotter · none · prod | 89.5 (87.5) | 19.7 (23.2) | 77.7 (77.1) | 89.8 (91.6) |
| spotter · none · + vector | 90.9 (91.7) | 13.4 (14.5) | 77.8 (77.7) | 89.9 (91.6) |
| spotter · two-date · prod | 87.1 (91.7) | 54.3 (50.7) | 73.7 (74.9) | 89.3 (91.6) |
| spotter · two-date · + vector | 88.5 (83.3) | 35.0 (37.7) | 76.7 (76.0) | 90.7 (90.5) |
| spotter · He 2011 · prod | 91.5 (91.7) | 50.9 (50.7) | 75.0 (73.1) | 91.1 (89.5) |
| spotter · He 2011 · + vector | **92.1** (91.7) | 33.3 (39.1) | 76.9 (76.0) | 90.8 (90.5) |
| spotter · both + raw · prod | 90.1 (91.7) | 23.4 (20.3) | 76.8 (77.1) | 91.4 (93.7) |
| spotter · both + raw · + vector | 90.1 (87.5) | 17.1 (15.9) | 77.4 (77.7) | **91.5** (93.7) |

**Seed-662 intervals:**
- The intervals are wide because the groups are small:
  - trusted flooded, production 70.8% [42.1–88.2];
  - dry-labelled, 8.7% [3.1–15.1];
  - control, 77.7% [70.4–84.9];
  - benchmark, 85.3% [78.1–92.7].
- Every interval and paired McNemar test is in the JSON.

**Contrasts in the groups** (mean over splits; seed-averaged 95% CI; "> 0" splits):

| Contrast | Trusted flooded: found | Dry-labelled: called flooded | Control: right | Clear-sky benchmark: found |
|---|---|---|---|---|
| main: spotter gate | **+5.6** [+1.9, +12.2], 21/21 | **+15.3** [+10.8, +19.3], 21/21 | −1.3 [−5.2, +1.8] | **+4.0** [+1.7, +6.4], 21/21 |
| main: two-date | +3.3 [−4.1, +12.6] | **+24.5** [+13.7, +33.0], 21/21 | −2.1 [−5.8, +0.7] | −0.3 [−4.9, +3.4] |
| main: He 2011 | **+8.1** [+2.3, +16.7], 21/21 | **+15.4** [+9.3, +20.7], 21/21 | −0.9 [−5.2, +2.4] | +2.1 [−2.4, +6.4] |
| main: both + raw | +4.0 [−0.8, +9.7] | +2.0 [+0.0, +3.4] | +0.2 [−1.9, +2.0] | +1.9 [−0.1, +3.8] |
| main: DINOv2 vector | +1.6 [+0.6, +2.9] | **−10.1** [−13.9, −5.9], 0/21 | +1.4 [−0.2, +3.7] | +0.2 [−0.9, +1.3] |
| He within the production gate | **+14.6** [+4.8, +29.9], 21/21 | +5.2 [+1.3, +9.9] | 0.0 | +3.1 |
| He within the spotter gate | +1.6 [−1.9, +4.9] | **+25.6** [+15.7, +33.8] | −1.8 | +1.1 |
| two-date within the production gate | +9.0 [−1.8, +23.9] | +20.8 [+9.0, +31.5] | −1.8 | −0.7 |
| two-date within the spotter gate | −2.4 [−8.0, +2.0] | +28.1 [+16.9, +36.9] | −2.5 | +0.2 |
| **interaction gate x He 2011** | **−13.0** [−27.6, −4.1] | **+20.4** [+11.5, +28.9] | −1.7 | −2.0 |
| **interaction gate x two-date** | **−11.4** [−24.6, −2.9] | +7.3 [−1.3, +15.7] | −0.8 | +0.9 |
| **interaction gate x both + raw** | **−8.1** [−19.1, −0.1] | +3.4 [−0.2, +6.0] | −1.6 | −0.6 |
| interaction two-date x vector | −3.3 [−8.5, +0.7] | **−15.3** [−23.7, −6.6] | **+2.3** [+0.8, +4.1] | +1.2 |
| interaction He 2011 x vector | −4.5 [−9.5, −1.1] | −7.4 [−11.8, −3.1] | +1.3 | +0.1 |

## 6. Each tool: impact, strengths and weaknesses
**DINOv2 change vector (16 PCs in each fold).**
- **Impact:** the one robust gain on the shared roads: +1.25 [+0.56, +1.95], positive in 21 of 21 splits and under
  either gate.
- **Strengths:**
  - It raises recall without losing specificity. The chosen arm keeps the most dry roads dry of all 16 arms at seed 662
    (246).
  - Under thin cloud it is the most conservative tool: −10.1 points of flooded calls on dry-labelled roads.
  - It halves two-date's extra flooded calls there: +32.1 without it, +16.8 with it (two-date x vector −15.3).
  - It removes He's cost on clear roads (He x vector +0.87).
- **Weaknesses:**
  - It needs the in-fold PCA inside production, which production does not have yet.
  - On the 24 trusted flooded thin-cloud roads it adds only +1.6 points.

**Spotter gate (bright + texture + DINOv2 road rule).**
- **Impact:** on the shared roads a small, unsteady gain: +0.34 [−0.19, +0.96], 16 of 21 splits. Against production
  alone it is +0.52 (15 up / 5 down).
- **Strengths:**
  - It sets aside fewer flooded roads: 18 against 27.
  - It finds more flooded roads near and under thin cloud: +5.6 on the trusted group and +4.0 on the clear-sky
    benchmark, both in 21 of 21 splits.
- **Weaknesses:**
  - Under thin cloud it raises flooded calls on dry-labelled roads by +15.3 (21 of 21). The labels cannot say whether
    those calls are wrong.
  - It makes the de-hazers redundant on the trusted group (gate x de-hazer −8 to −13), and it worsens He's flooded
    calls on dry-labelled roads (gate x He +20.4).
  - It is trained on HRC_WHU, which is academic use only, so it stays research-only until it is retrained on open
    labels.
  - Its SpaceNet 8 pixel accuracy is unmeasured.

**Two-date de-hazing (no corner edit).**
- **Impact:** −0.36 on the shared roads (4 of 21 splits up). It costs most without the vector: −0.51 alone, −3.3 on the
  controls.
- **Strength:** under the production gate it finds +9.0 more of the trusted flooded thin-cloud roads, but that
  interval includes 0.
- **Weakness:** it adds the most flooded calls on dry-labelled thin-cloud roads, +24.5 (up to 54.3% with the spotter
  gate). Under the spotter gate it adds nothing on the trusted group (−2.4).

**He 2011 de-hazing.**
- **Impact:** −0.66 on the shared roads (1 of 21 splits up), −1.09 without the vector and −0.22 with it.
- **Strength:** the strongest thin-cloud tool under the production gate. It finds +14.6 points more of the trusted
  flooded roads (21 of 21), and production + He reaches 91.3%. On dry-labelled roads it adds +5.2, much less than
  two-date's +20.8.
- **Weakness:** under the spotter gate it finds little extra (+1.6) but adds +25.6 flooded calls on dry-labelled roads.

**Both cues + raw (raw + td_ + he_).**
- **Impact:** neutral everywhere. Shared roads +0.11; trusted group +4.0, with an interval that includes 0;
  dry-labelled calls +2.0.
- **Strength:** it is the safest de-hazing option. It keeps the raw cues, so the forest leans on them where the copies
  are noisy.
- **Weakness:** it brings almost none of He's thin-cloud gain (84.1% against 91.3% under the production gate, without
  the vector) and triples the columns.

## 7. The optimal combo (preregistered rule) and the promotion rule
- **Rank by mean shared-road accuracy over the 21 splits:** the top arm is spotter · both + raw · + vector, 84.56%
  (4 tools).
- **Ties:**
  - All 7 other vector arms are ties: they have fewer tools, and their seed-averaged paired interval against the top
    includes 0 (from +0.01 [−0.56, +0.57] to +0.52 [−0.33, +1.51]).
  - None of the 8 arms without the vector ties. The closest is spotter · both + raw · prod, at +0.71 [+0.22, +1.21].
- **Fewest tools among them: production gate · no de-hazing · + DINOv2 vector** (1 tool), 84.48%. Against the top arm
  it is +0.08 [−0.84, +1.03].
- **Promotion rule** (`production.json`; read-only, not written):

  | Test | Gain [95% CI] | McNemar p | Passes? |
  |---|---|---|---|
  | Shared roads, seed 662 | +2.2 [+0.9, +3.7] | 0.0023 | yes |
  | Production's 798 kept roads, seed 662 | +2.3 [+0.9, +3.6] | 0.0014 | yes |
  | Shared roads, other splits | — | — | 5 of 21 |

  - **Other arms that pass at seed 662** (shared roads): spotter · none · prod, spotter · none · + vector, spotter ·
    two-date · + vector, spotter · both + raw · prod and spotter · both + raw · + vector.
  - None passes in more than 7 of the 21 splits. Everything together passes in 7, the chosen arm in 5.
  - Of the arms that pass at seed 662, the largest gain is spotter · both + raw · + vector, +3.2 [+1.4, +5.1],
    p = 0.0005. The rule's "largest gain" clause would pick it.
  - The preregistered choice rule instead picks the simplest of the tied arms. It ranks by the 21-split mean, not one
    split, and seed 662 is production's worst split.
- **Pass or candidate:** the chosen arm passes the rule at seed 662, but it is a candidate for Justin, not a promotion.
  - It needs the in-fold PCA inside production.
  - It passes in only 5 of 21 splits.
  - These roads have been scored many times.

## 8. Pictures (`figures/pipeline_factorial/`)
- **`arms_shared_accuracy.png` (preregistered):** the 16 arms on the 757 shared roads.
  - Each arm shows its mean over the 21 splits (large dot), every split (small dots), its min to max (bar) and
    seed 662 (diamond). Colour is the gate.
  - The vector arms form one block above the rest.
  - Production's seed-662 diamond sits at the bottom of its own range.
- **`main_effects.png` (preregistered):** each tool's main effect (top) and the same effect within each gate (bottom),
  with every split and the seed-averaged interval. Only the vector bar is clear of 0.
- **`cloud_groups.png` (added beyond the plan):** every arm's mean share in each of the four cloud groups, with the min
  to max over splits.
  - Under the spotter gate, the de-hazers barely change the trusted flooded group but raise the flooded calls on
    dry-labelled roads about 2.5-fold (19.7% to 54.3% and 50.9% without the vector).

## Departures from the plan
1. **Smoke test first.**
   - The script was first run in a 2-split smoke mode (seeds 662 and 1, outputs to the scratchpad) to test the scoring.
   - It crashed on a column name (`paired_report` names the column after the baseline arm) after sets (i)–(iii) had
     printed for those 2 splits.
   - So the seed-662 and seed-1 numbers were seen before the full run. The plan was not changed.
   - The fix renamed that key. Two safety changes went in with it: an atomic cache write, and a separate cache for the
     smoke mode.
   - The full run recomputed all 21 splits from nothing, and the seed-1 calls matched the smoke run's exactly.
2. **`cloud_groups.png`** was added beyond the two preregistered charts.
3. **`pipeline_factorial_seeds.csv` and the seed-calls `.npz`** are extra outputs. The JSON keeps 6 significant figures.

## What stays uncertain
- **Whether the vector's +1.25 holds on unseen roads.** It is the steadiest effect here (21 of 21 splits), but these
  are development roads that every earlier arm has scored.
- **Whether the cloud tools' extra flooded calls on dry-labelled thin-cloud roads are found floods or false alarms.**
  The labels under cloud cannot be trusted, so these 69 roads cannot score it. Only cloud-free reference labels or
  field data could.
- **The thin-cloud groups are small.** The groups have 24 and 69 roads on 13 and 29 tiles, and they have been looked at
  many times. The seed-662 intervals span 30–45 points on the 24.
- **Whether the spotter gate's training benefit is real or label-driven.** It trains on 19 trusted flooded thin-cloud
  roads that production sets aside, and on 14 dry-labelled ones whose labels are suspect.
- **Ranking within the vector block.** The 8 vector arms are within 0.52 points of each other, which is well inside the
  split-to-split SD. A second event or the sealed tiles could reorder them.
- **The "both" option is not symmetric with td and he.** It keeps raw, while td and he replace it, as asked. So
  "both + raw" against "He" mixes two changes: adding two-date and adding raw back.
- **Licence:** the spotter is HRC_WHU-trained, academic use only.
