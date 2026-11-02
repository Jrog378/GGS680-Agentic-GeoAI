# 23: Method bench 2: the papers read in full on 2026-10-30, alone and then combined (2026-10-30; EXPLORATORY, development data only)

**Status:** complete. The run ended at 18:15 on 2026-10-30 with exit code 0. Plan: `outputs/preregistration_method_bench_2.md`
(written before any code or score; amendments 1–9 written after the smoke test and before the full run). It was
followed as written except where listed under **Deviations**. Code and numbers: `evidence/pilot_scripts/method_bench_2/`.
Figures: `figures/method_bench_2/`. **Nothing is promoted.** The runner checked the sha256 of `production.json` after every
stage and the file is unchanged (sha256 `e592414b…`, last modified 29 Oct 18:15, before the run started).

**Data:** Louisiana-East train + val only (200 development tiles kept by the tile rule, 99 of them with a C0 gate; 1,037
touched roads; published labels unmodified). The Ida test's frozen preparation was read-only: 132 usable prep tiles,
of which 73 have at least 2,000 thin-cloud pixels and were scored. No sealed, test or negative tile was read, and no
flood label was used to fit any arm. Single process, 2 threads, CPU only; no DINOv3.

## Setup and reproduction
- **Stages run, in order:**
  1. thresholds: G2's T_blue = 240.8, from Otsu on 186 training tiles.
  2. tiles: 200 tiles, every arm, after-date feature rows.
  3. gates: false alarms on 94 clear tiles.
  4. ida: secondary grey and edge metrics on 73 tiles; the gate check on 132 tiles.
  5. primary: DINOv2 on the CPU, 3-hour budget.
  6. score.
  7. screen: seed 662.
  8. seeds: 12 arms at 21 seeds.
  9. combo.
- **Reproduction checks, all passed:**
  - The production flood model refitted at seed 662 gives (378, 63, 103, 254) on the 798 roads it keeps, at both the
    screen and the seeds stage.
  - **C0 recomputed from scratch** (not read from bench 1's cache) gives a 21-seed gain of −0.57 [−1.31, +0.15], better on
    1 seed and worse on 17. This is identical to bench 1's C0 row (evidence 22).
- **Re-running it:** every stage is resumable from per-tile caches on
  `/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_2_cache/`.

      cd evidence/pilot_scripts/method_bench_2
      OMP_NUM_THREADS=2 nice -n 10 python3 -I run_bench2.py all > run_bench2.log 2>&1
      OMP_NUM_THREADS=2 nice -n 10 python3 -I b2_figures.py        # figures F1–F4 (3 tiles recomputed, no tokens)

**Format:** estimate [95% interval]. Flood gains are in accuracy points, 21-seed mean, against production, with a 3 × 3
block bootstrap. Ida intervals come from 2,000 resamples of 3 × 3 tile blocks, pairing each arm with C0 per tile.
"Closer" means a lower DINOv2 feature distance to the NOAA aerial reference. Exact McNemar at seed 662 was not
significant for any arm (every p ≥ 0.14), so no McNemar p is quoted below.

## (G) Gate arms: Le Hégarat-Mascle hysteresis (G1, G1b, G1c) and Lin blue rise (G2)
**As cloud detectors** (figure `F3_gates_ida.png`). The Ida check scores each mask against the satellite–NOAA
disagreement (|as is − NOAA| > the guard's 99th percentile). That disagreement also contains real change, parallax and
moving objects, so it is not a cloud label.

| Mask | Ida precision (pooled, 132 tiles) | Ida recall | Clear tiles: mean share flagged | Clear tiles with > 1% flagged (of 94) |
|---|---|---|---|---|
| production dark rise | 0.63 | 0.80 | 0.13% | 0 |
| G1 hysteresis as printed | 0.74 | 0.12 | 0.55% | 12 |
| G1b + 2,500 m² blob | 0.77 | 0.12 | 0.47% | 10 |
| G1c centred (deviation) | 0.76 | 0.13 | 0.54% | 12 |
| G2 blue rise | 0.18 | 0.04 | 2.98% | 15 |

- **G1 / G1b / G1c** flag only cloud cores. On the 99 cloudy development tiles, G1 is **empty on 54**, and it is empty more
  often on heavily clouded tiles. Its low cut t_l has a median of 111 DN, against production's single cut of 71.4.
- **G2** has the lowest precision. It fires on clear tiles that have no dark rise at all (0_12_14: 26% of the tile).

**As road gates** (flood calls, `F2_flood_seeds.png`). Paired on the roads that both production and the arm keep.

| Arm | roads kept (production 798) | screen at 662 | 21-seed gain |
|---|---|---|---|
| G1 road gate | 869 (74 added, 3 removed) | +1.01 [−0.36, +2.72] | −0.08 [−0.83, +0.84]; 9 seeds better, 11 worse |
| **G1b road gate** | 870 (74 added, 2 removed) | +0.38 [−1.14, +2.42] | **+0.16 [−0.61, +1.12]**; 11 better, 8 worse |
| G1c road gate | 867 (72 added, 3 removed) | +0.75 [−0.59, +2.55] | −0.19 [−0.95, +0.71]; 9 better, 11 worse |
| G2 road gate | 886 (92 added, 4 removed) | +0.38 [−1.14, +2.49] | +0.14 [−0.74, +1.27]; 11 better, 9 worse |

The gate arms let 69 to 88 more roads be assessed. Their accuracy on the roads both keep does not change beyond noise.
**Accuracy on the added roads was not computed by the run** (bench 1 reported it for D3ii), so the extra coverage is
not yet shown to be safe.

**As correction gates** (inside C0's arithmetic; paired with C0 only on tiles where the arm's mask is non-empty).

| Arm | Ida primary Δ vs C0 | tiles | guard grey | flood |
|---|---|---|---|---|
| G1 corr gate | **+0.0120 [+0.0023, +0.0205]** (further) | 21 | 0.15 | screen −0.75, not carried |
| G1b corr gate | **+0.0118 [+0.0021, +0.0204]** (further) | 21 | 0.12 | screen −1.00, not carried |
| G1c corr gate | +0.0101 [−0.0001, +0.0212] | 25 | 0.12 | screen −0.501, just under the −0.5 cut, not carried |
| G2 corr gate | +0.0055 [−0.0044, +0.0138] | 21 | **2.61** | **−0.42 [−0.87, −0.01]**; 4 better, 15 worse (vs C0 +0.15 [−0.43, +0.72]) |

## (N) Tone arms: Du, Schott, Lin and Song in place of C0's quantile tone curve
Figure `F1_ida_primary.png`. Primary = DINOv2 feature distance under thin cloud, on 54 tiles (see Deviation 1).
Secondary = grey error under thin cloud, on 73 tiles. "Abstained" counts the 99 cloudy development tiles where the arm
returned the image uncorrected.

| Arm | abstained | Ida primary Δ vs C0 | guard grey (C0 1.11) | grey error thin Δ vs C0 | flood |
|---|---|---|---|---|---|
| N1 Du PIF | 0 | **+0.0064 [+0.0020, +0.0118]** (further; 37 of 54 tiles) | 1.90 | +8.6 [+5.2, +12.9] | screen −0.63 |
| N1b Du, no water removal | 0 | +0.0043 [−0.0002, +0.0092] | 1.55 | +5.0 [+2.2, +8.7] | screen −1.00 |
| N2 Schott roofs + roads | 90 (ε_T ≥ 2 DC on 89) | −0.0005 [−0.0118, +0.0115] | 0.14 | +44.1 (≈ as is) | screen −0.88 |
| N2b Schott roofs | 96 | +0.0000 [−0.0112, +0.0123] | 0.04 | +44.5 (≈ as is) | **−0.57 [−1.09, −0.24]**; 2 better, 15 worse (vs C0 +0.00 [−0.67, +0.64]) |
| N2c Schott, no ε_T check | 1 | **+0.0141 [+0.0083, +0.0218]** (further; 44 of 54) | 1.63 | +10.5 [+6.0, +16.6] | −0.27 [−0.92, +0.30] (vs C0 +0.29 [−0.23, +0.85]) |
| N3 Lin wPCA | 21 | +0.0056 [−0.0037, +0.0144] | 0.66 | +27.5 [+18.2, +37.0] | −0.58 [−1.21, +0.01] (vs C0 −0.02 [−0.44, +0.39]) |
| N3 bounded | 31 | +0.0049 [−0.0042, +0.0132] | 0.43 | +27.8 [+18.4, +37.4] | −0.59 [−1.29, +0.06] (vs C0 −0.02 [−0.45, +0.41]) |
| **N4 Song ridge, all pixels** | 31 | **−0.0103 [−0.0196, −0.0000]** (closer; 34 of 54; Wilcoxon p = 0.010) | 0.26 | +18.2 [+11.5, +25.8] | screen −0.88 |
| N4 bounded | 49 | −0.0068 [−0.0171, +0.0043] | 0.18 | +25.8 [+17.6, +34.9] | screen −1.00 |
| N4b Song ridge, clear pixels | 19 | −0.0043 [−0.0119, +0.0041] | 0.66 | +11.0 [+6.1, +16.1] | screen −0.88 |

**Reading:**
- **N4 is the only tone arm closer to NOAA, and only just:** its interval's upper end is −0.00004. Most of the gain is
  abstention. On 15 of the 54 primary tiles N4 abstained (negative ridge slope) and so equals "as is". On those tiles,
  "as is" is 0.023 closer than C0, which gives about 60% of N4's mean. On its 39 fitted tiles N4 is −0.0053 against C0.
  Where it fits, the ridge slope is nearly flat (median 0.11 on the cloudy development tiles), so the reference carries
  almost no before-date texture. The result is close to "as is" with an offset (`F4_before_after_2_21_42.png`, slope
  0.007).
- **The Schott arms are mostly "no correction"** as registered. N2 abstained on 90 of 99 cloudy tiles and N2b on 96. When
  the ε_T check is dropped (N2c), the fit moves features further from NOAA.
- **Every tone arm has a larger grey error under thin cloud than C0's quantile curve.** This is the pre-registered
  "linear vs nonlinear tone" risk.

## (A) Haze arms: Chavez band-linked airlight (A1) and Zhang HOT (A2)
| Arm | Ida primary Δ vs C0 (54 tiles) | guard grey | grey error thin Δ vs C0 | flood |
|---|---|---|---|---|
| **A1 k = 0** (grey airlight, Chavez's "cloud" end-member) | **−0.0030 [−0.0054, −0.0001]** (closer; 38 of 54; Wilcoxon p = 0.002) | 0.97 | +6.2 [+4.0, +8.6] | screen −1.25 |
| A1 k = 0.5 | −0.0022 [−0.0072, +0.0031] | 0.78 | +21.5 [+16.4, +26.0] | −0.56 [−1.27, +0.08] (vs C0 +0.01 [−0.42, +0.37]) |
| A1 k = 0.7 | −0.0027 [−0.0081, +0.0032] | 0.72 | +27.7 [+21.6, +33.3] | **−0.56 [−1.13, −0.01]**; 3 better, 16 worse (vs C0 +0.01 [−0.43, +0.43]) |
| A1 k = 1 | −0.0024 [−0.0083, +0.0039] | 0.64 | +36.3 [+28.8, +43.2] | screen −0.63 |
| A1 k = 2 | +0.0011 [−0.0072, +0.0097] | 0.45 | +58.0 [+47.8, +67.5] | screen −1.13 |
| A2 Zhang HOT | **not run**: needs a water mask | — | — | — |

- **A1 k = 0 is closer to NOAA, but the effect is tiny:** −0.003 on a level of about 0.68, with a per-tile median of
  −0.0012.
- **Grey error grows steadily with k.** For k > 0 the near-white cloud is tinted orange (smoke test), as the plan's
  radiance-vs-display-DN risk predicted.

## Flood calls: what the 21-seed runs show (`F2_flood_seeds.png`)
- **Carried to 21 seeds:** 12 arms passed the −0.5-point screen. The "not carried" list is in the figure footer.
- **Three intervals are below 0 against production:**
  - N2b: −0.57 [−1.09, −0.24].
  - A1 k = 0.7: −0.56 [−1.13, −0.01].
  - G2 as a correction gate: −0.42 [−0.87, −0.01].
- **Against C0, every one of those is 0 within noise.** C0's own added columns already cost −0.57 [−1.31, +0.15]. These
  arms inherit that loss rather than adding a new one.
- **Every interval of a correction arm against C0 includes 0.**
- **The two road gates with a gain ≥ 0** are G1b (+0.16) and G2 (+0.14), both within noise.

## Alone, then combined
**Helped alone (pre-registered: own-metric interval excluding 0 in the good direction, or 21-seed flood gain ≥ 0):**
- **Own metric:** N4 Song ridge and A1 k = 0. Their primary intervals are below 0 and the guard passes.
- **Flood gain ≥ 0:** G1b and G2 as road gates.

**Stage winners:**
- The rule picks, within each stage, the arm that helped alone with the largest 21-seed flood gain:
  - G = G1b road gate (+0.16 beats G2's +0.14).
  - N: none.
  - A: none.
- N4 and A1 k = 0 failed the seed-662 screen (−0.88 and −1.25). So they have no 21-seed gain and could not be ranked.
  This is the same reading bench 1 used for C5a γ 2.2 (Deviation 5 below).

**Combinations:** none were tested. A factorial needs at least two stage winners, and the run found one (log: "fewer
than two stage winners: no combination to test"). So **no arm can meet the KEEP rule**, which requires help in
combination.

## Decision table (for Justin; nothing is promoted)
**Rules applied as pre-registered:**
- **KEEP:** helps alone and in combination, with an interval excluding 0.
- **MAYBE:** helps on one metric only, or within noise.
- **DROP:** no help, or harms (interval in the bad direction on a metric).
- **NOT RUN:** cannot run on this data.

**Deciding metrics**, as in bench 1:
- the Ida primary, with the guard;
- flood calls;
- for the gates, coverage and the Ida check.

Grey error is secondary and is not used to choose (Ida Revision 1 item 2). If it were used, every correction arm would be
DROP, because every one has a larger thin-cloud grey error than C0.

**How "within noise" is read:** a 21-seed flood estimate ≥ 0 whose interval includes 0. This is the plan's own
"helped alone" flood test, and bench 1 read it the same way. An arm whose deciding metrics all point the wrong way or sit
at 0 is "no help" (DROP).

| Arm | Decision | One line of evidence |
|---|---|---|
| G1 hysteresis, road gate | DROP | no help: flood −0.08 [−0.83, +0.84]; Ida recall 0.12, empty on 54 of 99 cloudy tiles |
| **G1b hysteresis + blob, road gate** | **MAYBE** | the only stage winner: flood +0.16 [−0.61, +1.12] (within noise), 72 more roads assessed; combination not testable; accuracy on the added roads unknown |
| G1c centred (deviation), road gate | DROP | no help: flood −0.19 [−0.95, +0.71] |
| G2 Lin blue rise, road gate | MAYBE | flood +0.14 [−0.74, +1.27] (within noise), but a poor cloud detector (Ida precision 0.18, recall 0.04; 2.98% false alarms on clear tiles) |
| G1 as correction gate | DROP | harms: further from NOAA +0.0120 [+0.0023, +0.0205] |
| G1b as correction gate | DROP | harms: further from NOAA +0.0118 [+0.0021, +0.0204] |
| G1c as correction gate | DROP | no help: +0.0101 [−0.0001, +0.0212]; screen −0.50 |
| G2 as correction gate | DROP | harms: flood −0.42 [−0.87, −0.01]; guard 2.61 fails |
| N1 Du PIF | DROP | harms: further from NOAA +0.0064 [+0.0020, +0.0118]; guard 1.90 |
| N1b Du, no water removal (deviation) | DROP | no help: +0.0043 [−0.0002, +0.0092]; screen −1.00 |
| N2 Schott roofs + roads | DROP | no help: abstained on 90 of 99 cloudy tiles (ε_T median 6.6 DC vs the paper's < 2); screen −0.88 |
| N2b Schott roofs | DROP | harms vs production: flood −0.57 [−1.09, −0.24] (vs C0 0.00); abstained on 96 of 99 |
| N2c Schott, no ε_T check (deviation) | DROP | harms: further from NOAA +0.0141 [+0.0083, +0.0218] |
| N3 Lin wPCA | DROP | no help: +0.0056 [−0.0037, +0.0144]; flood −0.58 [−1.21, +0.01] |
| N3 bounded (deviation) | DROP | no help: +0.0049 [−0.0042, +0.0132]; flood −0.59 [−1.29, +0.06] |
| **N4 Song ridge, all pixels** | **MAYBE** | helps alone on its own metric: closer to NOAA −0.0103 [−0.0196, −0.0000] with guard 0.26, but about 60% of it is abstention; flood screen −0.88; grey +18.2 |
| N4 bounded (deviation) | DROP | no help: −0.0068 [−0.0171, +0.0043]; screen −1.00 |
| N4b Song ridge, clear pixels | DROP | no help: −0.0043 [−0.0119, +0.0041]; screen −0.88 |
| **A1 Chavez k = 0** | **MAYBE** | helps alone on its own metric: closer −0.0030 [−0.0054, −0.0001] with guard 0.97; flood screen −1.25; grey +6.2 |
| A1 k = 0.5 | DROP | no help: −0.0022 [−0.0072, +0.0031]; flood −0.56 [−1.27, +0.08] |
| A1 k = 0.7 | DROP | harms vs production: flood −0.56 [−1.13, −0.01] (vs C0 +0.01) |
| A1 k = 1 | DROP | no help: −0.0024 [−0.0083, +0.0039]; screen −0.63 |
| A1 k = 2 | DROP | no help: +0.0011 [−0.0072, +0.0097]; screen −1.13; grey +58 |
| A2 Zhang HOT | NOT RUN | needs a water mask (the GGS680 water mask is planned, not built) |
| Combinations (G × N × A) | NOT RUN | only one stage winner (G1b) |

**No arm earns KEEP.** Four arms are MAYBE, and two of them are worth a second look:
- **N4:** read as "C0 should sometimes not correct at all", not as "Song's ridge is a better tone curve".
- **A1 k = 0:** a small, consistent gain in features (38 of 54 tiles).
- **G1b and G2** are MAYBE only on the flood rule. Neither is a usable cloud detector as coded.

## What goes wrong, and what we would fix
1. **G1's thresholds, as printed, sit above the cloud.**
   - *What goes wrong:* the paper's field is centred near 0 by construction. Our dark-rise field has a tile mean around
     41 (median) and a long negative tail from parallax and misregistration. Reflecting the 0.1th percentile about that
     mean puts t_l at 111 DN (median). On heavily clouded tiles the mean itself rises, and the gate goes empty: 54 of 99
     cloudy tiles (`F3_gates_ida.png`: 0_13_5 and 2_21_42 are almost all cloud, and G1 flags 0%). Centring (G1c) does
     not help, because the lower tail measures registration noise, not clear-sky scatter.
   - *Fix to test:* keep the hysteresis (it is precise, at 0.74–0.77), but take t_h from production's 71.4 cut and set
     t_l from the clear-ground spread of the rise (outside production's gate). That makes it a growing step around the
     cut we already trust.
2. **G2's threshold is an artefact of bad blue maps.**
   - *What goes wrong:* Otsu on the pooled blue rise gave T_blue = 240.8 DN. On 8-bit blue, a rise that large can only
     occur where the before→after blue map is badly wrong: N3's selector abstained and fell back to mean/SD on 32 of 99
     cloudy tiles, and fitted gains reach 3.4 at the 90th percentile. So G2 marks mis-normalised tiles, not cloud
     (precision 0.18).
   - *Fix to test:* set the cut from the blue-rise distribution on production-clear pixels (for example its 99th
     percentile), with a plain mean/SD blue map.
3. **The straight-line tone papers do not fit 0.5 m two-date display RGB.**
   - *What goes wrong:* clear ground correlates weakly between the dates. So:
     - Du's r ≥ 0.9 is met only by a narrow band, and the gains vary from 0.39 to 1.79 (10th to 90th percentile).
     - Schott's ε_T fails on 90 of 99 tiles.
     - Lin abstains on 21 tiles.
     - Song's ridge is nearly flat or negative.

     Where these arms do fit, they are further from NOAA than C0, or within noise. They are always worse on grey, because
     the 8-bit tone curves differ by date in a nonlinear way.
   - *Fix:* none worth testing within these papers. C0's quantile curve stays.
4. **N4's gain shows that C0 itself hurts on some tiles.**
   - *What goes wrong:* on the 15 primary tiles where N4 abstained, leaving the image alone was 0.023 closer to NOAA than
     C0 (`F4_before_after_0_13_5.png`: N4 = as is, and feature distance is 0.830 for both against C0's 0.834). C0 pastes
     before-date structure into the cloud. DINOv2 rewards after-date texture, even under haze. This repeats evidence 18
     and 22, where C0 was not closer than "as is".
   - *Fix to test:* an abstention rule on C0, as its own pre-registered arm: leave a tile uncorrected when the clear-ground
     relation is weak (for example a ridge slope ≤ 0, or a low before/after correlation). Then score it on features and
     flood calls.
5. **Features and grey disagree, so the choice of metric decides the winner.**
   - *What goes wrong:* N4 and A1 k = 0 are closer in features but further in grey (+18.2 and +6.2). Grey rewards matching
     levels; features reward structure and texture.
   - *Fix:* keep features as the deciding metric, as pre-registered, and always show both next to the images (F4).
6. **Corrections do not move flood calls.**
   - *What goes wrong:* every correction arm against C0 is 0 within noise. As in bench 1, calls are made on roads the gate
     keeps, away from cloud.
   - *Fix:* test corrections on the roads the gate removes (the extra 72–92 roads a looser gate would add). That needs
     the accuracy of those added roads, which this run did not compute. It is light to compute from the cached calls
     (`bench2_flood_calls.npz`), and it is the first thing to add before any gate decision.

## Deviations
1. **The primary stopped early.**
   - **What happened:** the DINOv2 Ida primary (CPU only, 2 threads) used its 3-hour budget (10,912 s of token time,
     including the overrun of the last tile) after **54 of 73 tiles**. It stopped before 0_21_16.
   - **Which tiles are missing:** tiles were taken in decreasing thin-cloud area, so the 19 unscored tiles are those
     with the least thin cloud. The primary therefore describes the more clouded tiles.
   - **What still covers all 73:** the secondary grey and edge metrics.
   - **G arms:** the G correction gates are paired with C0 only where their own mask is non-empty (21 to 25 of the 54
     tiles), because a G arm with an empty mask is "no correction" by design (`arm_outputs`).
2. **Amendments 1–9 (written before the full run, after the smoke test):**
   1. N1's QC reports SL of the re-selected PIFs.
   2. G2 falls back to mean/SD when N3's selector abstains. This was used on 32 of 99 cloudy tiles.
   3. A2 gets a synthetic grey-surface check.
   4. G1c (centred hysteresis) was added.
   5. N2c (Schott without ε_T) was added.
   6. N3- and N4-bounded (gain in [0.1, 10]) were added.
   7. N1b (no water removal) was added.
   8. A2 stays coded but not run.
   9. The DINOv2 primary was added to the run order, CPU only, after the other jobs ended.

   Arms 4–7 are **deviations from their papers** and are labelled "(deviation)" above. Runnable arms: 25.
3. **A2 (Zhang HOT haze removal) not run.**
   - **Why:** it needs a water mask, and the paper's comes from a near-IR threshold. Without one, floodwater (high HOT)
     would be "dehazed".
   - **What was done:** it is coded and checked on synthetic haze only (grey surface: inside-blob error 9.7/12.0/14.3 →
     4.4/4.3/4.1 for R/G/B).
   - **What it waits on:** it runs when the GGS680 water mask exists.
4. **How the guard is applied.** The code tests |guard(arm) − guard(C0)| ≤ 1 grey level, that is, relative to C0's
   1.11. The plan says "guard within ±1 grey level". Under an absolute reading (≤ 1 from "as is"), the two arms that
   helped still pass (N4 0.26, A1 k = 0 0.97). The ones that fail are N1 (1.90), N1b (1.55), N2c (1.63) and G2 (2.61).
   No verdict changes.
5. **Stage-winner reading.**
   - **The issue:** the winner rule ranks the arms that helped alone by their 21-seed flood gain. N4 and A1 k = 0 helped
     on their own metric, but they failed the seed-662 screen, so they have no 21-seed gain and were not eligible.
   - **Precedent:** bench 1 used the same reading for C5a γ 2.2.
   - **What the other reading would have meant:** treating them as N and A winners would have run a G1b × N4 × A1 k = 0
     factorial.
   - **Status:** this is an open reading for Justin. Nothing was rerun.
6. **The screen cut was applied as written.** G1c as a correction gate scored −0.501 points at seed 662, just under the
   −0.5 cut, and was not carried.
7. **The gates' own metric has no interval.** Ida precision and recall and the clear-tile shares are pooled, so the gate
   arms could "help alone" only through flood calls.

## Files
- **Numbers** (`evidence/pilot_scripts/method_bench_2/`):
  - `bench2_numbers.json`: every statistic above.
  - `ida_rows_primary.csv` (54 tiles), `ida_rows_secondary.csv` (73 tiles) and `ida_rows_gates.csv` (132 tiles).
  - `ida_primary_spent.txt`.
  - `smoke_results.json`.
  - Cached flood calls and per-tile pickles on `/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_2_cache/`.
- **Logs:** `run_bench2.log` (the full run, 14:01–18:15), `smoke_test.log` and `dry_run.log`.
- **Figures** (`figures/method_bench_2/`, made by `b2_figures.py`):
  - `F1_ida_primary.png`: forest plot of the primary (feature distance vs C0, 54 tiles, with guard) beside grey error
    under thin cloud.
  - `F2_flood_seeds.png`: forest plot of 21-seed flood gains, against production and against C0. The arms not carried
    are listed in the footer.
  - `F3_gates_ida.png`: production dark rise, G1, G1b, G1c and G2 on 3 Ida tiles (0_13_5, 2_21_42, 2_23_44), each shown
    as hits, false alarms and missed disagreement against NOAA.
  - `F4_before_after_0_13_5.png` and `F4_before_after_2_21_42.png`: before, as is, C0, N4, A1 k = 0 and NOAA, with
    |image − NOAA| maps and N4 − C0. The tiles are the two largest thin-cloud areas, chosen without labels or results.
  - `smoke_*.png`: the smoke test, which was not scored.
