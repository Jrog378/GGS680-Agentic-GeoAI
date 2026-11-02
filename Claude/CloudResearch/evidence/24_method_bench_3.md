# 24: Method bench 3: the batch D3 papers in practice, greyscale first, then RGB, alone and combined (2026-10-30/31; EXPLORATORY, development data only)

**Status:** complete (Phase G finished 2026-10-31 01:06, Phase R 06:34). Plan:
`outputs/preregistration_method_bench_3.md` (written before any code or score; amendments dated, written before the
scores they precede). Code and numbers: `evidence/pilot_scripts/method_bench_3/`. **Pre-run notebooks for visual
checking:** `notebooks/method_bench_3/01_grey_arms.ipynb`, `02_grey_combos.ipynb`, `03_rgb_arms.ipynb`,
`04_rgb_vs_grey.ipynb`. **Nothing is promoted.** `production.json` was checked by sha256 before and after every stage and
is unchanged.

**Data:** Louisiana-East train + val only (200 development tiles kept by the tile rule, 99 with a C0 gate; 1,037
touched roads; published labels unmodified). The Ida test's frozen preparation was read-only: 132 usable prep tiles,
73 with at least 2,000 thin-cloud pixels. HRC_WHU: the 120 development images only. No sealed, test or negative tile, no
Germany, no LA-West. One process at a time, 2 threads, `nice -n 10`, memory gate before every tile, CPU only, no DINOv3.

## Setup and reproduction
- **Reproduction checks (all passed):**
  - production's flood model refitted at seed 662: (378, 63, 103, 254) on its 798 kept roads, at every flood stage;
  - production's calls reproduced on the `predict_proba` path (P > 0.5) before PUL was scored;
  - C0 recomputed from scratch: 21-seed gain −0.57 [−1.31, +0.15], 1 seed better, 17 worse, identical to benches 1–2;
  - D0 spotter on HRC_WHU fold 0 = `counts_library.csv`, image for image;
  - D0 spotter on the 200 SN8 tiles (CPU tokens) vs `gate_roads.csv`: largest road-share gap 1.6e−4, 99.3% of roads
    exact, and the same 790 kept roads as gate (b);
  - Phase R's per-band feature code fed the grey band reproduces the road table (max difference 3.6e−15).
- **Format:** estimate [95% interval]. Flood gains are accuracy points, mean over 21 seeds, against production on the
  roads both keep, with a 3 × 3 block bootstrap. Ida intervals: 2,000 resamples of 3 × 3 tile blocks, arm minus C0 per
  tile. "Closer" = lower DINOv2 feature distance to the NOAA aerial reference. McNemar (seed 662) is Holm-corrected
  across each phase's arms and separately across the factorial cells; **no McNemar test is significant after Holm** in
  Phase G, so no p-value is quoted below.
- **Pooled fits (training tiles):** T1's integer-level Otsu on the clipped grey rise gave η* = 0.547, below the 0.65
  acceptance (**ours**, not Otsu's), so T1 used the registered fallback cut 108.8 (99th percentile on
  production-clear pixels). Integer Otsu on the pooled dark rise gives k* = 72 (η* = 0.636): production's 71.36 is
  confirmed (T1d not an arm). Pooled EM (B1p) puts the Bayes cut at 96.5 and the 0.9-posterior cut at 120.5.
- **Re-running:**

      cd evidence/pilot_scripts/method_bench_3
      OMP_NUM_THREADS=2 nice -n 10 python3 -I run_bench3.py thresholds,tiles,gates,ida,flood,pul,primary,score,combo
      OMP_NUM_THREADS=2 nice -n 10 python3 -I hrc_d5.py; python3 -I d5_sn8.py
      python3 -I nb_cache.py G; python3 -I decide.py; python3 -I make_nb.py G      # notebooks 01, 02
      ./chain_R.sh                                                                  # Phase R, notebooks 03, 04

## Phase G (greyscale)
### Gates (road gates; production = dark rise > 71.4, road cannot be assessed at ≥ 20% of its strip)
Sources: `bench3_numbers.json` keys `flood`, `gates_clear_tiles`, `ida_gates`.

| Arm | roads kept (production 798) | 21-seed gain | accuracy on added roads (production on its own 798: 0.786) | Ida precision / recall (production 0.63 / 0.80) | clear tiles: mean flagged, tiles > 1% (of 94) |
|---|---|---|---|---|---|
| T1 Otsu grey rise | 889 (+91) | −0.08 [−0.87, +0.93]; 9 better, 11 worse | 0.835 [0.710, 0.917] | 0.65 / 0.14 | 1.01%, 29 |
| T1b + blob | 891 (+93) | −0.03 [−0.87, +1.13] | 0.839 [0.715, 0.920] | 0.74 / 0.08 | 0.13%, 3 |
| **B1 EM/Bayes hysteresis, per tile** | 804 (+34, −28) | **+0.45 [−0.24, +1.11]**; 14 better, 6 worse | 0.756 [0.546, 0.893] | 0.49 / 0.52 | 1.97%, 8 |
| **B1p EM/Bayes, pooled cuts** | 852 (+54) | **+0.48 [−0.26, +1.30]**; 17 better, 2 worse | 0.757 [0.566, 0.884] | **0.87** / 0.62 | 0.00%, 0 |
| B2 ICM-MRF (β 1.3 = 1.6 = 1.8) | 790 (+31, −39) | +0.29 [−0.40, +0.90]; 13 better, 8 worse | 0.762 [0.509, 0.911] | 0.46 / 0.53 | 2.41%, 8 |
| U1 Dempster–Shafer certain gate | 876 (+78) | +0.02 [−0.74, +1.04] | 0.835 [0.702, 0.918] | (road-level) | (road-level) |
| U1s DS strict | 795 (−3) | +0.20 [−0.13, +0.45]; 12 better, 8 worse | — | (road-level) | (road-level) |

- **B1 abstains on most tiles.** Its EM fitted on 70 of 200 tiles; it abstained for poor separation on 72, for
  μ_c < 71.4 − 2σ_n on 41, for no Bayes root on 15, EM failure on 2. It is empty on 41 of the 99 cloudy tiles, and B1p
  on 50. On the 94 clear tiles, B1 still flags > 1% on 8 tiles (EM splits clear-ground noise when it does fit).
- **B2 equals the per-pixel Bayes label.** ICM changed 5–14 pixels per smoke tile and the three β give identical gates:
  the dark rise is already box-smoothed over 20 m, so the MRF prior has nothing left to smooth.
- **U1 certifies 86% of strips as "certain"** (84% of those under the cloud mask): to a two-date change cue, cloud is
  change. So U1 mostly re-admits clouded roads. Their calls are about as accurate as production's kept roads (0.835),
  but the interval is wide.
- **The roads the gates add are called about as well as the kept ones** (0.76–0.84 against 0.79), with wide intervals
  (31–93 roads). This is the first time a bench measured it (evidence 23 fix #6).

### Corrections (inside C0's gate, C0's 20 m fade, t < 0.2 left as is)
Primary: DINOv2 feature distance to NOAA in thin cloud, **all 73 tiles** (the 3-hour budget was not reached, 7,935 s).
Sources: `ida_primary_vs_C0`, `ida_grey_err_thin_vs_C0`, `ida_edge_r_thin_vs_C0`, `ida_guard_grey_change_mean`, `flood`.

| Arm | Ida primary Δ vs C0 | tiles closer | guard (C0 1.11) | grey error thin Δ vs C0 | edge r thin Δ | flood vs production | flood vs C0 |
|---|---|---|---|---|---|---|---|
| as is (reference) | −0.0048 [−0.0150, +0.0071] | 38 of 73 | 0.00 | +46.5 | +0.032 | — | — |
| P1 Pan C, tile C | −0.0007 [−0.0063, +0.0043] | 35 | 0.94 | −1.0 [−2.1, +0.3] | −0.024 | −0.50 [−1.15, +0.08] | +0.07 [−0.33, +0.43] |
| P1w Pan C, local C | +0.0020 [−0.0025, +0.0066] | 34 | 1.21 | −1.3 | −0.015 | **−0.87 [−1.50, −0.30]**; 1 better, 20 worse | −0.30 [−0.67, +0.04] |
| S1 sphere DCP | **+0.0309 [+0.0200, +0.0421]** (further) | 11 | **3.64** | +16.3 [+10.3, +22.8] | −0.024 | −0.67 [−1.50, +0.03] | −0.11 [−0.68, +0.49] |
| S1p sphere + Pan C | **+0.0098 [+0.0012, +0.0188]** (further) | 28 | 0.91 | −0.7 | −0.027 | −0.36 [−1.02, +0.20] | +0.20 [−0.28, +0.66] |
| M1 median DCP | **+0.0250 [+0.0114, +0.0376]** (further) | 22 | **3.85** | +27.6 [+20.2, +35.2] | −0.038 | −0.18 [−1.05, +0.59] | +0.39 [−0.33, +1.18] |
| L1 Poisson seam | −0.0065 [−0.0166, +0.0021] | 40 | 0.22 | +29.2 [+22.1, +35.8] | −0.007 | −0.51 [−1.17, +0.07] | +0.05 [−0.34, +0.46] |

- **No correction is closer to NOAA than C0 with an interval below 0.** The two that lean closer are L1, which is
  partly "as is" (Poisson cloning returns the level to the uncorrected border, grey error +29), and P1 (−0.0007).
- **The one-date dark channels move away from NOAA.** S1 and M1 darken the whole gate (mean grey 25–53 against C0's
  69–89 on the smoke tiles). They fail the guard (3.6–3.9 grey levels on clear ground), as He 2013 (C1) did in bench 1.
  Pan's C (P1, S1p) pulls them back to C0's level, but not past it.
- **C0 itself is not closer than "as is"** (C0 − as is +0.0048 [−0.0071, +0.0150]): the same reading as evidence
  18/22/23.
- **Flood calls:** every correction against C0 is 0 within noise. P1w is below 0 against production; that is C0's own
  −0.57 plus noise (vs C0 −0.30 [−0.67, +0.04]).

### Decision side
- **Q1 (change ÷ t, Gibson eq. 47):** −0.54 [−1.25, +0.15] vs production, +0.03 [−0.13, +0.19] vs C0. As the registered
  risk said, most kept roads have t ≈ 1, so the scaling barely touches them.
- **PUL / PULb (Li 2011):** −2.32 [−6.17, +0.73] and −2.27 [−6.12, +0.73]; worse on all 21 seeds. The held-out
  labelling rate c was 0.71–0.76 per fold, so the cut g > 0.5c (≈ 0.37) calls far more roads flooded: at seed 662,
  38 calls fixed against 68 broken. **SCAR check (binned c):** in the 2 folds with ≥ 5 cloudy positives, c under cloud
  (share ≥ 0.2) was 0.63 and 0.62 against 0.73 and 0.74 on clear roads: lower under cloud, as the handoff predicted
  (`pul_c`, seed 662). Only 22 cloudy positives fall in the held-out sets at that seed, so this is a hint, not a measurement.

### Spotter (D5, He et al. 2022 boundary weights; HRC_WHU, `hrc_d5_numbers.json`)
| Arm | pooled F1 (D0 0.8679) | paired F1 vs D0 | boundary band (≤ 16 px) F1 vs D0 | interior |
|---|---|---|---|---|
| **D5a weighted samples** | 0.8688 | **+0.0009 [+0.0001, +0.0016]**; 71 images higher, 49 lower | **+0.0042 [+0.0027, +0.0057]** | −0.0001 [−0.001, +0.001] |
| D5b edge-sampled pixels | 0.8680 | +0.0001 [−0.0012, +0.0014] | +0.0034 [+0.0017, +0.0051] | −0.0009 [−0.003, +0.001] |

D5a met its preregistered rule, so its conditional flood test ran (`d5_sn8_numbers.json`): the D5a spotter gate against
D0's spotter gate on SN8, **+0.07 [−0.18, +0.33]** (9 seeds better, 10 worse). A sharper label edge on HRC_WHU does not
move the road calls.

### Combinations (Phase G factorial)
Carried by the preregistered top-2 rule: gates **B1p, B1**; corrections **L1, P1** (exploratory: neither helped
alone); decision **Q1, PULb** (exploratory). That gives 20 cells × 21 seeds (`combo`, figure in notebook 02).
- **No cell has a gain interval above 0.** The best are B1p + L1 + Q1 −0.05 [−0.72, +0.59] and B1p + P1 −0.18
  [−0.85, +0.48]. Every cell holding PULb is −2.1 to −2.9.
- **Interactions:** one interval excludes 0: **B1 + Q1, −0.84 [−1.58, −0.29]** (the two hurt each other). All others
  include 0. L1 + Q1 (+0.57 [−0.08, +1.24]) and B1p + L1 + Q1 (+0.52 [−0.42, +1.53]) lean positive.
- Every gate gain shrinks when a correction or Q1 is added, because those add C0-type columns, which cost about 0.5
  points on their own.

### Phase G decision table (`bench3_decisions.json`; nothing is promoted)
| Arm | Decision | One line of evidence |
|---|---|---|
| T1 Otsu grey rise | DROP | no help: flood −0.08 [−0.87, +0.93]; Ida recall 0.14; 29 of 94 clear tiles > 1% flagged |
| T1b + blob | DROP | no help: flood −0.03 [−0.87, +1.13]; empty on 68 of 99 cloudy tiles |
| **B1 EM/Bayes hysteresis** | **MAYBE** | flood +0.45 [−0.24, +1.11] (14 of 21 seeds better), within noise; abstains on 130 of 200 tiles; harms with Q1 (interaction −0.84 [−1.58, −0.29]) |
| **B1p EM/Bayes pooled** | **MAYBE** | flood +0.48 [−0.26, +1.30] (17 of 21 better), within noise; the most precise gate on Ida (0.87 vs 0.63) with no false alarms on clear tiles; adds 54 roads called at 0.757 |
| B2 ICM-MRF (β 1.3/1.6/1.8) | MAYBE | flood +0.29 [−0.40, +0.90]; identical to per-pixel Bayes (the MRF changes ≤ 14 pixels per tile) |
| U1 DS certain gate | MAYBE | flood +0.02 [−0.74, +1.04]; certifies 84% of clouded strips (cloud reads as change) |
| U1s DS strict | MAYBE | flood +0.20 [−0.13, +0.45]; removes only 3 roads |
| P1 Pan C tile | DROP | no help: Ida −0.0007 [−0.0063, +0.0043]; flood −0.50 [−1.15, +0.08] |
| P1w Pan C local | DROP | harms: flood −0.87 [−1.50, −0.30] vs production (vs C0 −0.30 [−0.67, +0.04]) |
| S1 sphere DCP | DROP | harms: further from NOAA +0.0309 [+0.0200, +0.0421]; guard 3.64 |
| S1p sphere + Pan C | DROP | harms: further +0.0098 [+0.0012, +0.0188] |
| M1 median DCP | DROP | harms: further +0.0250 [+0.0114, +0.0376]; guard 3.85 |
| L1 Poisson seam | DROP | no help: Ida −0.0065 [−0.0166, +0.0021]; grey +29.2; flood −0.51 [−1.17, +0.07] |
| Q1 1/t threshold | DROP | no help: flood −0.54 [−1.25, +0.15] (vs C0 +0.03) |
| PUL / PULb | DROP | no help: −2.32 / −2.27, worse on all 21 seeds |
| **D5a boundary-weighted spotter** | **MAYBE** | HRC F1 +0.0009 [+0.0001, +0.0016], edge band +0.0042 [+0.0027, +0.0057]; SN8 flood vs D0 +0.07 [−0.18, +0.33] |
| D5b edge-sampled | MAYBE | edge band +0.0034 [+0.0017, +0.0051], pooled +0.0001 (within noise) |
| T1d, L2, chip gate, FwDET, DINOv3 | NOT RUN | 71.4 confirmed by T1d; reasons in the preregistration |

**No Phase G arm earns KEEP.** Worth a second look: **B1p** (a pooled EM/Bayes cut of the dark rise, 96.5/120.5 with
hysteresis). It is the most precise cloud mask so far, never fires on clear tiles, assesses 54 more roads at about
production's accuracy, and is better on 17 of 21 seeds. Its gain interval still includes 0.

## Phase R (RGB)
Plan amendment of 2026-10-31 01:12 (carry-overs, R0 check, coding choices, dry run), written before any Phase R
score. Sources: `bench3r_numbers.json`, `carry_R.json`, `bench3r_kept_roads.csv`; notebooks 03 and 04.

### R0, the colour baseline
Production's 93 road features computed per band (279 columns + the 3 DINOv2 cues) in place of grey. Same forest, folds
and seeds: **−0.90 [−1.76, −0.28]** against production, 1 seed better, 19 worse. Colour columns, as coded, make the
calls worse. That mixes "colour" with "three times the columns" (registered risk), so it does not show that colour
carries no flood signal. Every Phase R arm is built on R0's columns and inherits that cost, so each is reported against
R0 and against production (deviation 3 for how the decision table reads that).

### Phase R arms alone
| Arm | vs production (21 seeds) | vs R0 | other |
|---|---|---|---|
| D1e IHOT-RGB gate | −1.66 [−3.35, +0.07]; 0 better, 21 worse | −0.94 [−2.34, +0.52] | removes 142 roads; flags 21.8% of clear-tile pixels (46 of 94 tiles > 1%); Ida precision 0.27, recall 0.61 |
| D1e-BR (blue, red) | −1.06 [−2.70, +0.62] | −0.27 [−1.62, +1.38] | removes 174 roads; precision 0.28 |
| **RGB B1p (pooled EM/Bayes on the RGB dark channel)** | −0.17 [−1.06, +0.60] | **+0.73 [+0.14, +1.50]**; 18 better, 2 worse | adds 56 roads (accuracy 0.73 [0.55, 0.86]); 0% on clear tiles; precision **0.87**, recall 0.59 |
| **RGB B1 (per tile)** | −0.18 [−1.18, +0.61] | **+0.62 [+0.12, +1.17]**; 18 better, 3 worse | +31 / −26 roads; precision 0.53 |
| A2b HOT lower-bound | −0.72 [−1.83, +0.27] | +0.18 [−0.47, +0.91] | Ida +0.0141 [−0.0010, +0.0311] (46 tiles); guard 2.23 fails; abstains on 101 of 200 tiles |
| A2b-noW | −0.98 [−2.15, +0.08] | −0.08 [−0.73, +0.71] | Ida +0.0090 [−0.0057, +0.0222]; guard 2.80 fails |
| A2b-auto (MAD lower limit) | −0.61 [−1.90, +0.41] | +0.29 [−0.42, +0.98] | **Ida further +0.0142 [+0.0061, +0.0221]** (35 tiles); guard 0.37 |
| **RGB P1 Pan C-shift** | −0.19 [−1.24, +0.69] | **+0.71 [+0.10, +1.37]**; 17 better, 4 worse | **Ida closer than C0: −0.0084 [−0.0133, −0.0035]**, 47 of 73 tiles closer, guard 0.70 passes; grey error +5.5 [+3.2, +7.6] |
| RGB L1 Poisson seam | **−0.93 [−2.01, −0.05]** | −0.03 [−0.54, +0.57] | Ida −0.0057 [−0.0151, +0.0025]; grey +29.3 |
| Q1 on RGB P1 | −0.36 [−1.43, +0.58] | +0.54 [−0.06, +1.25] | — |
| Q1 on RGB L1 | −0.90 [−1.99, −0.01] | +0.01 [−0.56, +0.64] | — |
| ISFA-RGB (IWD + \|SFA₁\|) | −0.65 [−1.47, −0.01] | +0.25 [−0.03, +0.61]; 15 better | converged on only 57 of 200 tiles (119 not converged, 23 singular, 1 collapsed); 649 of 891 roads got the median fill |
| ISFA-grey control | −0.66 [−1.55, +0.01] | +0.24 [−0.06, +0.53] | the one-band standardised difference does as well as ISFA-RGB |
| RGB PULb | −2.33 [−6.57, +0.85]; 0 better | −1.43 [−5.44, +1.78] | as in Phase G |

- **RGB P1 is the only correction in all three benches** that is closer to NOAA than C0 with its interval below 0 and
  the guard passed. In grey (Phase G) the same arm was −0.0007 [−0.0063, +0.0043]: taking the dark channel as the
  minimum over the three bands, rather than over grey, is what moves it. It is still 5.5 grey levels further than C0 in
  grey error, and on the thin-cloud tile it clips the haziest areas to white (notebook 03, tile 0_13_5).
- **The pooled EM/Bayes gate carries over to colour:** RGB B1p beats R0 on 18 of 21 seeds with an interval above 0, and
  it keeps grey B1p's precision (0.87) and its zero false alarms on clear tiles.
- **D1e (IHOT) fails as a gate:** it flags a fifth of every clear tile, because iHOT is fitted per tile and the EM then
  splits ordinary colour variation into two classes.
- **A2b does not suit 0.5 m display RGB:** the lower-bound slopes are 13–17 DN per ΔHOT level, so it subtracts tens of
  grey levels under cloud. It abstains on about half the tiles (too few ΔHOT bins in (2, 20]), and ΔHOT never passes 20
  after the 61-pixel median, so the "cannot assess" rule never fired.

### Phase R combinations
Carried (top 2 per family against production): gates **RGB B1p, RGB B1**; corrections **RGB P1, RGB L1**;
decision/cue **Q1 on RGB P1, ISFA-RGB**. Q1 on P1 contains P1, so a "P1 + Q1" cell is Q1 on P1 (same columns), and its
interaction double-counts P1. After the deviation 4 fix (cells refitted):
- **No cell is above production.** The best are RGB B1 + RGB P1, −0.07 [−1.38, +1.04] (vs R0 +0.72 [−0.03, +1.59]),
  and RGB B1p + RGB P1 + ISFA, −0.14 [−1.08, +0.74] (vs R0 **+0.76 [+0.06, +1.63]**).
- **Interactions are mostly negative** (for example B1p + P1, −0.72 [−1.14, −0.32]): the gains of the parts against R0
  overlap rather than add up. Part of this comes from summing two gains measured against the same R0 base (the
  double-counting noted above).
- No McNemar is significant after Holm.

### Grey against RGB
Best grey set-up (highest 21-seed gain against production, single arm or cell): **B1p EM/Bayes pooled** (+0.48
[−0.26, +1.30]). Best RGB set-up: **RGB B1 + RGB P1** (−0.07). **RGB minus grey: −0.60 [−2.22, +0.69]** on the 772 roads
both assess; 3 seeds better, 15 worse. Across all development roads assessed by both, their majority calls differ on
39 roads: the grey set-up is right on 23 and the RGB set-up on 16 (notebook 04, error crops).

### Phase R decision table (`bench3_decisions.json`, key `phase_R`)
| Arm | Decision | One line of evidence |
|---|---|---|
| R0 colour baseline | DROP (as a replacement for the grey columns) | −0.90 [−1.76, −0.28] vs production |
| D1e / D1e-BR IHOT gates | DROP | −1.66 / −1.06 vs production, 0 of 21 seeds better (D1e); 22% false alarms on clear tiles |
| **RGB B1p** | **MAYBE** | beats R0 +0.73 [+0.14, +1.50]; precision 0.87; −0.17 vs production |
| **RGB B1** | **MAYBE** | beats R0 +0.62 [+0.12, +1.17]; −0.18 vs production |
| A2b, A2b-noW | DROP | no help; guard fails (2.2, 2.8) |
| A2b-auto | DROP | harms: further from NOAA +0.0142 [+0.0061, +0.0221] |
| **RGB P1 Pan C-shift** | **MAYBE** | closer to NOAA than C0 −0.0084 [−0.0133, −0.0035] with the guard passed, and beats R0 +0.71 [+0.10, +1.37]; −0.19 vs production; no cell above production, so not KEEP |
| RGB L1, Q1 on RGB L1 | DROP | below production (−0.93, −0.90), 0 vs R0 |
| Q1 on RGB P1 | DROP | no help beyond P1 itself (vs R0 +0.54 [−0.06, +1.25]) |
| ISFA-RGB, ISFA-grey | DROP | 0 vs R0 (+0.25, +0.24, intervals include 0); ISFA converges on 57 of 200 tiles |
| RGB PULb | DROP | −2.33, 0 of 21 seeds better |
| D1e as a spotter feature | NOT RUN | HRC_WHU has no clear partner date |

**No arm earns KEEP in either phase. Nothing is promoted.**

## What goes wrong, and what we would fix
1. **Colour features, as coded, hurt the flood model (R0 −0.90).**
   - *What goes wrong:* tripling the road columns (279 per-band columns) dilutes the forest's `max_features` sampling
     with three near-copies of each grey feature, and every RGB arm pays that cost.
   - *Fix to test:* keep the 93 grey columns and add a few colour columns only (for example the per-road mean of blue −
     red change and of the RGB dark-channel change), or reduce the 279 per-band columns by PCA inside each fold.
     Then re-score RGB B1p and RGB P1 on that base.
2. **The single-date dark-channel family over-corrects under cloud in grey (S1, M1) and only P1 survives in RGB.**
   - *What goes wrong:* a cloud's own dark channel is high, so t is low everywhere under it (S1/M1 mean grey 25–53
     against C0's 69–89). In RGB, P1's three-band minimum finds darker ground pixels, so t is better, but the brightest
     haze is clipped to white because the grey airlight is used for all three bands.
   - *Fix to test:* RGB P1 with a per-band airlight (He's A per band, which Pan averages to grey) and the clip
     replaced by C0's opaque rule per band. Score it on the Ida primary and on top of the column fix in item 1.
3. **The pooled EM/Bayes gate is precise but its gain is within noise.**
   - *What goes wrong:* B1p assesses 54–56 more roads, called at 0.73–0.76 against production's 0.79 on its own roads.
     The added roads are hazier and harder, so they hold back the paired gain on the roads both keep.
   - *Fix to test:* combine B1p's pixel mask with production's road rule only where they agree (B1p ∩ dark rise), and
     report the added-road accuracy with its own interval. That needs more flooded roads under thin cloud than LA-East
     has, so it is the first candidate for a fresh-data check once frozen (the sealed-data rule applies).
4. **Per-tile EM abstains on most tiles (B1 fits 70 of 200), and the MRF does nothing.**
   - *What goes wrong:* the dark rise is box-smoothed over 20 m and its clear-ground spread is wide, so the two
     Gaussians rarely separate by 2 σ, and ICM has nothing left to smooth.
   - *Fix:* none worth testing per tile: the pooled fit (B1p) is the better form. For an MRF, use the unsmoothed
     erosion-only dark rise.
5. **Two-date change cues read cloud as change (U1, ISFA, D1e).**
   - *What goes wrong:* U1 certified 84% of clouded strips as "certain", ISFA did not converge on most clouded tiles,
     and IHOT's per-tile regression splits ordinary colour variation.
   - *Fix:* use these only on roads the gate keeps (outside cloud), as extra change cues for the flood model. ISFA
     there is no better than the one-band standardised difference (+0.25 vs +0.24 against R0), so the cheap grey
     control would be the one to try.
6. **PUL's threshold is miscalibrated for road labels.**
   - *What goes wrong:* SN8 labels negatives as well as positives, and c ≈ 0.72 lowers the flooded cut to ≈ 0.36, so
     it over-calls flood (worse on all 21 seeds). The binned c is lower under cloud (0.62–0.63 against 0.73–0.74 where
     a bin has ≥ 5 positives, seed 662), the SCAR failure the handoff predicted, but it rests on 22 positives.
   - *Fix:* none for flood calls. The finding (labelling rate lower under cloud) belongs with the evidence-02 missing-
     label question, not with the model.
7. **Boundary weighting sharpens HRC_WHU edges but does not move SN8 calls (D5a).**
   - *Fix:* none for flood calls. Keep it as a detection-only note (+0.0042 [+0.0027, +0.0057] F1 within 16 px of
     the label edge).
8. **No correction moves flood calls against C0** (all within noise, as in benches 1–2). The Ida primary is the only
   metric where corrections differ, and only RGB P1 helps there.

## Deviations
1. **Bayes-cut sign (B1/B1p/B2/U1/D1e):** the handoff's transcription of eq. 7 has the log term's sign flipped relative
   to eq. 6; the code solves eq. 6. Posterior checked = 0.50 at T̂_o and 0.90 at t_h (amendment, before any score).
2. **Torch patch order:** the first Phase G primary stopped at start-up (`__wrapped__`); fixed by importing
   `torch._dynamo` before disabling MPS (`run_bench3_before_fix.py`, `run_bench3_G3_primary_attempt1_crash.log`). No
   score was affected.
3. **Phase R decision reading:** "helped alone" in Phase R also counts an interval above 0 against R0; KEEP still needs
   a cell above production (written before the decision table, after the single-arm scores).
4. **Phase R factorial gate bug:** "gate + correction" cells lost the gate's added roads; fixed and refitted
   (`run_bench3r_before_fix.py`, `run_bench3r_R4_combo_attempt1_bug.log`).
5. **Notebook builder:** `make_nb.py R` failed on an import path under `python -I`; fixed (`make_nb_before_fix.py`,
   `make_nb_R_attempt1_crash.log`).
6. **Notebook execution:** `jupyter nbconvert` is not installed and installs are not allowed. The notebooks were
   executed in place with **nbclient** (the engine nbconvert `--execute` uses) and saved with their outputs.
7. **Smaller coding choices** (amendments): U1 G-statistic per pixel (strips differ in size); U1's FCM pooled over all
   strips; iHOT shifted before EM; A2b's 61-pixel median approximated on a 4× downsampled field; the "darkened" proxy
   centred on the tile's median change; ISFA abstains when not converged.
8. **D0 on SN8 (CPU tokens) vs `gate_roads.csv`:** road shares match to 1.6e−4 (99.3% exact) and give the same 790 kept
   roads; not bit-identical (the cached shares came from an earlier token run).

## Files
- **Plan:** `outputs/preregistration_method_bench_3.md` (amendments and deviations dated inside).
- **Code** (`evidence/pilot_scripts/method_bench_3/`): `b3_common.py`, `g3_gates.py`, `g3_corr.py`, `r3_arms.py`,
  `run_bench3.py` (Phase G), `run_bench3r.py` (Phase R), `hrc_d5.py`, `d5_sn8.py`, `smoke_test.py`, `nb_cache.py`,
  `nbviz.py`, `make_nb.py`, `make_nb_r.py`, `decide.py`, `chain_G.sh`, `chain_G2.sh`, `chain_R.sh`; originals of the
  fixed files are kept as `*_before_fix.py`.
- **Numbers:** `bench3_numbers.json` (Phase G), `bench3r_numbers.json` (Phase R), `hrc_d5_numbers.json` (+
  `hrc_d5_counts.csv`), `d5_sn8_numbers.json`, `bench3_decisions.json`, `smoke_results.json`, `carry_R.json`,
  `ida_rows_{secondary,gates,primary}.csv` (G) and `*_R.csv` (R), `bench3_kept_roads.csv`, `bench3r_kept_roads.csv`.
- **Logs:** `run_thresholds.log`, `smoke_test.log`, `run_bench3_G1.log`, `run_bench3_G2_flood.log`, `hrc_d5.log`,
  `run_bench3_G3_primary.log`, `d5_sn8.log`, `run_bench3_G4_combo.log`, `run_bench3r_R0.log`, `run_bench3r_R1.log` to
  `R4_combo.log`, `nb_cache_{G,R}.log`, `make_nb_R.log`.
- **Caches** (`/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache/`): per-tile pickles (`tiles/`,
  `tiles_R/`, `d5_spot/`), flood calls (`bench3_flood_calls.npz`, `bench3r_flood_calls.npz`), notebook images (`nb/`),
  `g_thresholds.json`, `hrc_edge.npz`.
- **Figures** (`figures/method_bench_3/`): `smoke_gates_*.png`, `smoke_corr_*.png`; forest plots `G_forest_*.png` and
  `R_forest_*.png`, which are exported from notebooks 02 and 04.
- **Notebooks** (`notebooks/method_bench_3/`, pre-run, 6 development tiles: thin cloud 0_13_5, thick cloud 0_11_4,
  clear 0_15_8, flooded 2_20_58, smoke 2_23_44 and 2_19_55): `01_grey_arms.ipynb`, `02_grey_combos.ipynb`,
  `03_rgb_arms.ipynb`, `04_rgb_vs_grey.ipynb`.

