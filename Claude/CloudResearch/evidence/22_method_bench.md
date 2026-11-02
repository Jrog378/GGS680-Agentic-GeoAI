# 22: Method bench: every cloud method the full texts support, alone and combined (2026-10-30; EXPLORATORY, development data only)

**Status:** complete. Plan: `outputs/preregistration_method_bench.md` (written 2026-10-29 22:34, before any arm was
scored), followed as written except where listed under **Deviations**. Code: `evidence/pilot_scripts/method_bench/`.
Figures: `figures/method_bench/`. **Nothing is promoted.** `production.json` was hash-checked before and after every
runner and is unchanged.

**Data:** Louisiana-East train + val only (226 tiles, 1,037 touched roads, published labels unmodified). HRC_WHU's 120
development images. The Ida test's frozen preparation (73 usable tiles with thin cloud), read-only. No sealed, test or
negative tile was read.

**Reproduction checks, all passed:**
- **Production flood model:** refitted at seed 662 it gives 378 / 63 / 103 / 254 on the 798 roads it keeps, in every
  flood stage.
- **Spotter:** D0 reproduces `counts_library.csv` on fold 0 (24 images); D0 pooled F1 is 0.868 [0.848, 0.885].
- **Correction code:** `darkref_variant` equals `dark_reference_dehaze`, and `after_rows` equals the cached tables on 3
  tiles.
- **D3:** the unvetoed dark-rise share reproduces `cloud_dark_rise_road` on every road.

Format below: estimate [95% interval]. Flood gains are in accuracy points on the 798 roads production keeps, with a
3 × 3 block bootstrap. HRC intervals come from 2,000 image resamples within land cover. Ida intervals come from tile
blocks. Exact McNemar is reported only where it is significant.

## (a) Detection arms on HRC_WHU (`hrc_numbers.json`, `hrc_score.log`; figure `B3_hrc_detection.png`)
| Arm | F1 | paired F1 − D0 | images better / worse |
|---|---|---|---|
| D0 (current spotter) | 0.868 [0.848, 0.885] | — | — |
| D1a whiteness | 0.876 | +0.008 [−0.000, +0.016] | 76 / 44 |
| **D1b HOT** | **0.878** | **+0.011 [+0.004, +0.018]** | 78 / 42 (sign test p = 0.001) |
| D1c RGB dark channel | 0.867 | −0.001 [−0.003, +0.001] | 57 / 63 |
| D1d blue/red gradient ratio | 0.867 | −0.001 [−0.001, +0.000] | 51 / 69 |
| D1 all colour | 0.876 | +0.008 [−0.002, +0.017] | 80 / 40 |
| D2 Zhang & Xiao rule (no learning) | 0.749 | **−0.119 [−0.154, −0.082]** | 39 / 81 |

- **Water tiles** (the turbid-water false-alarm check): D1b +0.009 [−0.004, +0.027]; D2 −0.062 [−0.114, −0.018].
- **Pixel McNemar:** reported in the log, but not used to decide, because the pixels are not independent (plan).
- **D2:** high recall (0.90) and low precision (0.64). Its fixed constants were tuned on 9 photos (claim_checks_C).

**D4 calibration of D0, cross-fitted:**

| | ECE | Coverage at matched risk |
|---|---|---|
| raw | 0.026 [0.021, 0.037] | 0.683 (risk 0.071) |
| isotonic | 0.006 [0.005, 0.021] | 0.680 (risk 0.069) |
| Platt | 0.007 [0.005, 0.021] | 0.682 |

- ECE drops: isotonic −0.020 [−0.027, −0.006], Platt −0.019 [−0.028, −0.006].
- The pre-registered test also needs coverage at matched risk not to be lower, and it is slightly lower. So D4 improves
  calibration but not what the gate can keep.
- On D1b, isotonic or Platt cuts ECE from 0.033 to 0.005–0.006 with the same coverage pattern.

**Not run:**
- **D1 / D4 on flood calls:** this needs the spotter on all 200 SN8 after images, and those DINOv2 tokens were not
  computed (plan).
- **Scoring (d), detection masks against the Ida satellite–NOAA disagreement:** no runner was written for it before the
  crash. The Ida test's own outcome 5 covers the dark-rise mask and D0: F1 0.507 [0.376, 0.607] and 0.536
  [0.418, 0.633] (evidence 18).

## (b) Correction arms against the NOAA aerial reference (`ida_numbers.json`, `ida_score.log`; figures `B2_ida_primary.png`, `B4_tile_2_21_42.png`)
- **Coverage:** all 73 usable Ida tiles were scored within the 3-hour token budget (4,593 s spent, CPU, then MPS once the
  DINOv3 job ended).
- **Metric:** feature distance = 1 − cosine of DINOv2 tokens to the tone-matched NOAA image (lower = closer). Every arm
  is paired with C0, the current two-date fit.
- **Guard:** mean |arm − as is| grey change on clear ground (plan limit 1 grey level).

| Arm | thin cloud: Δ vs C0 | ring 0–40 m: Δ vs C0 | guard grey | grey error thin, Δ vs C0 |
|---|---|---|---|---|
| as is (no correction) | −0.0048 [−0.0150, +0.0071] | −0.0269 [−0.0373, −0.0157] | 0.00 | +46.5 [+35.7, +56.5] |
| C1 He 2013 recipe | **+0.0127 [+0.0049, +0.0213]** (further) | +0.0079 [+0.0019, +0.0144] | 1.50 | −1.1 [−2.6, +0.6] |
| C2 IR-MAD tone | −0.0030 [−0.0129, +0.0068] | −0.0149 [−0.0227, −0.0069] | 0.49 | +26.2 [+18.3, +35.0] |
| C3a fitted fade | −0.0027 [−0.0091, +0.0033] | −0.0116 [−0.0190, −0.0045] | 2.16 | 0 (acts outside the gate) |
| C3b Poisson seam | −0.0031 [−0.0091, +0.0015] | −0.0026 [−0.0068, +0.0016] | 1.68 | 0 |
| C4 blob 0 m² | +0.0010 [−0.0016, +0.0034] | +0.0021 [−0.0010, +0.0049] | 1.30 | +0.0 |
| C4 blob 1,250 m² | +0.0005 [−0.0004, +0.0015] | +0.0009 [−0.0004, +0.0024] | 1.14 | −0.0 |
| C4 blob 5,000 m² | −0.0021 [−0.0080, +0.0020] | −0.0041 [−0.0089, −0.0007] | 1.05 | +3.1 [+0.7, +7.0] |
| C4 blob 10,000 m² | −0.0056 [−0.0129, +0.0003] | −0.0084 [−0.0140, −0.0037] | 0.97 | +9.0 [+4.8, +13.9] |
| **C5a γ 1.8** | **−0.0070 [−0.0128, −0.0025]** (closer, 49 of 73 tiles) | −0.0053 [−0.0087, −0.0018] | 0.87 | +8.5 [+5.7, +11.4] |
| **C5a γ 2.2** | **−0.0065 [−0.0132, −0.0013]** | −0.0072 [−0.0118, −0.0026] | 0.77 | +12.6 [+8.7, +16.7] |
| C5b band-linked RGB | −0.0026 [−0.0037, −0.0014] (closer; guard 1.07 > 1) | −0.0027 [−0.0035, −0.0018] | 1.07 | +1.3 [+0.7, +1.8] |

**Reading:**
- C0 itself is not closer to NOAA than doing nothing (as is − C0 = −0.0048 [−0.0150, +0.0071]). This repeats evidence
  18 on a larger tile set.
- Only the γ-linearised arms move the thin-cloud features measurably toward NOAA while passing the guard. The effect is
  small: −0.007 on a level of about 0.68.
- Their grey error gets worse. No arm is chosen on grey (Ida Revision 1 item 2), so that is reported, not used.
- He's published refinement (C1) moves the features **away** from NOAA.
- In the ring, "as is" is closest: every correction's fade makes the ring less NOAA-like than leaving it alone. C3a, C2
  and C5 lose less of it than C0.
- **Caveat (evidence 18):** DINOv2 tokens use window-wide attention, so feature distance is not strictly local.

## (c) Flood calls under spatial folds S (`flood_numbers.json`, `run_flood_*.log`; figure `B1_flood_gains.png`)
**Screen at seed 662:** no arm is significant by exact McNemar; every p ≥ 0.39. Arms below −0.5 points were not
carried to 21 seeds (pre-registered): C3a −0.75, all four C4 sizes (−0.63 to −0.75) and C5a γ 2.2 −0.63.

| Arm | 21-seed mean gain vs production | seeds better / worse | vs C0 (C arms) |
|---|---|---|---|
| T1 LBP riu2 + VAR | **−0.88 [−1.84, −0.08]** | 2 / 18 | — |
| T2 dense Lowe descriptor | +0.13 [−0.28, +0.63] | 11 / 9 | — |
| T3 per-strip GLCM | +0.18 [−0.29, +0.69] | 12 / 8 | — |
| C0 current two-date (added columns) | −0.57 [−1.31, +0.15] | 1 / 17 | — |
| C1 He 2013 | **−0.64 [−1.33, −0.01]** | 3 / 17 | −0.08 [−0.50, +0.30] |
| C2 IR-MAD tone | −0.43 [−1.00, +0.06] | 4 / 15 | +0.14 [−0.44, +0.71] |
| C3b Poisson seam | −0.35 [−0.99, +0.25] | 5 / 13 | +0.22 [−0.12, +0.56] |
| C5a γ 1.8 | −0.39 [−1.00, +0.21] | 6 / 12 | +0.17 [−0.24, +0.56] |
| C5b band-linked RGB | −0.64 [−1.33, +0.00] | 2 / 18 | −0.07 [−0.35, +0.19] |
| D3i veto red > 1.5 blue | +0.00 [−0.26, +0.29] | 8 / 10 | — |
| D3ii veto local correlation | +0.27 [−0.30, +0.87] | 13 / 8 | — |
| D3 both vetoes | +0.27 [−0.30, +0.87] (identical to D3ii) | 13 / 8 | — |

- **Gate coverage:**
  - D3ii keeps 836 roads instead of 798. It adds 38 roads and removes none, and production-type calls on the added
    roads are 73.7% correct, against 79.2% on the 798.
  - D3i adds 1 road.
  - Veto (i) adds nothing beyond (ii), so D3 equals D3ii.
- **Corrections in flood calls:** every correction arm's columns lower flood-call accuracy slightly against production.
  None is distinguishable from C0, the step it replaces. As the plan warned, flood calls are made on roads the gate
  keeps, away from cloud, so a null here does not test correction under cloud.

**Combinations** (stage winners by the pre-registered rule: D = D3ii, C = C5a γ 1.8, T = T3; all 21 seeds; on the 798
shared roads):

| Combination | gain | interaction (gain − Σ alone) |
|---|---|---|
| C5a γ1.8 + D3ii | −0.56 [−1.28, +0.19] | −0.44 [−0.82, +0.01] |
| C5a γ1.8 + T3 | −0.36 [−0.96, +0.19] | −0.15 [−0.60, +0.21] |
| D3ii + T3 | +0.25 [−0.57, +1.13] | −0.20 [−0.56, +0.17] |
| all three | −0.35 [−0.97, +0.37] | −0.41 [−0.89, +0.12] |

No combination helps, and every interaction is zero or negative within noise; nothing adds up.

## Decision table (for Justin; nothing is promoted)
**Rules applied as pre-registered:**
- **KEEP** = helps alone and in combination, with an interval excluding 0.
- **MAYBE** = helps on one metric only, or within noise.
- **DROP** = no help, or harms (interval in the bad direction on a deciding metric).
- **Deciding metrics:** detection F1, Ida feature distance with the guard, and flood calls. Grey error is secondary and
  not used to choose (Ida Revision 1 item 2).

| Arm | Decision | One line of evidence |
|---|---|---|
| D1b HOT | **MAYBE** | Only detection arm that helps: F1 +0.011 [+0.004, +0.018] on HRC_WHU; untested on flood calls (no SN8 tokens) and per-tile clear line is our adaptation (below) |
| D1a whiteness | MAYBE | F1 +0.008 [−0.000, +0.016], within noise |
| D1 all colour | MAYBE | +0.008 [−0.002, +0.017], no better than D1b alone |
| D1c RGB dark channel | DROP | −0.001 [−0.003, +0.001], no help |
| D1d blue/red gradient ratio | DROP | −0.001 [−0.001, +0.000], no help |
| D2 Zhang & Xiao rule | DROP | harms: F1 −0.119 [−0.154, −0.082] |
| D3ii veto local correlation | **MAYBE** | flood +0.27 [−0.30, +0.87] (within noise) while assessing 38 more roads at 73.7% accuracy |
| D3i veto red > 1.5 blue | DROP | +0.00 [−0.26, +0.29], adds 1 road |
| D3 both vetoes | DROP | identical to D3ii; the extra veto adds nothing (keep the simpler) |
| D4 isotonic / Platt calibration | MAYBE | ECE −0.020 [−0.027, −0.006], but coverage at matched risk not higher (0.680 vs 0.683) |
| C1 He 2013 recipe | DROP | harms: further from NOAA +0.0127 [+0.0049, +0.0213]; flood −0.64 [−1.33, −0.01] |
| C2 IR-MAD tone | DROP | no help on features (−0.0030 [−0.0129, +0.0068]) or flood (−0.43 [−1.00, +0.06]); diverged on 7 tiles |
| C3a fitted fade | DROP | thin no help; ring closer (−0.0116) but guard 2.16 grey levels; flood screen −0.75 |
| C3b Poisson seam | MAYBE | within noise everywhere; vs C0 on flood +0.22 [−0.12, +0.56]; guard 1.68 |
| C4 blob 0 / 1,250 / 5,000 / 10,000 m² | DROP | no thin-cloud help; flood screen −0.63 to −0.75 |
| **C5a γ 1.8** | **MAYBE** | only correction closer to NOAA with the guard passed: −0.0070 [−0.0128, −0.0025]; flood −0.39 [−1.00, +0.21] vs production, +0.17 [−0.24, +0.56] vs C0 |
| C5a γ 2.2 | MAYBE | NOAA −0.0065 [−0.0132, −0.0013]; flood screen −0.63, not carried |
| C5b band-linked RGB | DROP | NOAA −0.0026 [−0.0037, −0.0014] but guard 1.07 fails; flood −0.64 [−1.33, +0.00] |
| T1 LBP riu2 + VAR | DROP | harms: flood −0.88 [−1.84, −0.08], worse on 18 of 21 seeds |
| T2 dense Lowe descriptor | MAYBE | +0.13 [−0.28, +0.63], within noise |
| T3 per-strip GLCM | MAYBE | +0.18 [−0.29, +0.69], within noise |
| Combinations | DROP | none helps; interactions ≤ 0 (e.g. γ1.8 + D3ii −0.44 [−0.82, +0.01]) |

**No arm earns KEEP.** The four most worth a second look are:
- **D1b HOT:** the detection gain is real on HRC_WHU, but its effect on flood calls needs SN8 tokens.
- **C5a γ 1.8:** the only correction measurably closer to NOAA.
- **D3ii:** more roads assessed, at no accuracy cost within noise.
- **T3:** the cheapest texture fix.

## Caveats from the full texts (claim_checks_D1 / D2; no arm was added or changed for them)
- **HOT (D1b):** Zhang et al. fit **one clear line per scene**, on a clear region an analyst chooses. Our clear line is
  fitted per tile (SN8) or per training fold (HRC_WHU), which is an adaptation (claim_checks_D1 #5). Zhang reports snow
  as the bright-surface failure case; bare soil gives a low HOT (#9).
- **Invariant-pixel normalisation (C2):** windowed fits are our extension; Du 2002 and Lin fit globally (D1 #5, #7).
  Lin states the method is "limited when images are almost covered by clouds … only a few invariant pixels can be
  extracted". That is what happened on the 7 tiles where IR-MAD diverged (Deviation 2).
- **Song 2001** supports a ridge method on all pixels, not invariant-pixel selection (D1 #2–3). The bench's IR-MAD arm is
  not supported by Song.
- **Chavez's scattering constraint:** a power law λ^−k in radiance, not a blue > green > red ordering (D1, ev21 #4).
  This bears on C5b's band link (we used Ma et al.'s exponent 1, as pre-registered) and is reported only.
- The D2 corrections (flood-depth error figures, ERA5 grid, Kaufman's adjacency blur) touch no bench arm.

## Deviations
1. **Crash and resume (22:55 kernel panic, 29 Oct).** `run_corr`, `run_texture` and `run_d3` resumed from their atomic
   per-tile caches, and every cache was load-checked first. `run_hrc` saves nothing per fold, so it was rerun in full,
   and its reproduction check passed again. The pre-crash logs were kept as `*_attempt1_crash.log`.
2. **IR-MAD (C2) bug fix.** On 7 tiles (2_13_47, 2_16_36, 2_17_36, 2_20_37, 2_20_38, 2_22_41, 2_28_32) the IR-MAD
   no-change weights collapsed during iteration, the weighted covariances became non-finite, and `scipy.linalg.eigh`
   raised `ValueError`. The code caught only `LinAlgError`, so `run_corr` lost those tiles. The pre-registered
   "IR-MAD failed → abstain (cannot assess)" path now also catches this failure. The original is kept as
   `c2_irmad_before_fix.py`, and only those 7 tiles were rerun (`run_corr_c2fix.log`, with `--skip-checks` because the
   checks had already passed).
3. **Scoring (d) not run:** no runner was written; the Ida test's outcome 5 covers the dark-rise mask and D0.
4. **D1 / D4 on flood calls not run:** no SN8 spotter tokens, as the plan anticipated.
5. **Combo stage:** the winner rule counted C5a γ 1.8 as "helped" by its own metric (NOAA). C5a γ 2.2 and D1b were
   also flagged "helped" but were not carried to 21 seeds: γ 2.2 failed the screen, and D1b has no flood arm.
6. **Guard:** the pre-registered guard is "±0.01 feature distance / 1 grey level". `ida_score.py` applies only the grey
   part (`guard_ok`), and the table above reports the grey guard. C0 itself has a guard grey change of 1.11.

## Files
- **Numbers:** `pilot_scripts/method_bench/hrc_numbers.json`, `ida_numbers.json`, `flood_numbers.json`,
  `hrc_counts.csv`, `ida_rows_secondary.csv`, `ida_rows_primary.csv`, `texture_roads.csv`, `d3_roads.csv`, and
  `mb_flood_calls.npz` (every fit's calls).
- **Logs:** `run_*.log`, `hrc_score.log`, `ida_score.log` and `bench_chain_status.log`.
- **Figures** (`figures/method_bench/`, made by `mb_figures.py`):
  - `B1_flood_gains.png`: forest plot of 21-seed flood gains, arms and combinations.
  - `B2_ida_primary.png`: feature distance to NOAA vs C0, thin and ring, with guard grey change.
  - `B3_hrc_detection.png`: paired F1 vs D0.
  - `B4_tile_2_21_42.png`: one cloudy tile (the 2nd-largest thin-cloud area, chosen without labels). It shows before,
    after, C0, C5a γ 1.8, C1, C3b and NOAA, plus feature-distance maps for as is, C0 and C1. On this tile C1's
    thin-cloud mean is 0.827, C0's 0.805 and as is 0.791.
