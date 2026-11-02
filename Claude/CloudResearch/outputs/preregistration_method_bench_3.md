# Pre-registration: method bench 3 (batch D3 papers in practice: greyscale first, then RGB; alone, then combined)

Written 2026-10-30 20:20 by Claude (AI), **before any bench-3 code was written and before any arm was scored**.
Development data only. Nothing is promoted; `ProjectBranch/Code/results/production.json` is read-only (sha256 checked
before and after every stage).

**Request (Justin, 2026-10-30):** "lets continue putting these methods into practice, first trying to use black and white
transformed imagery still and then later moving to rgb. again run these tests against each other and together along
with showing examples in the ipynbs that are prerun so I can go through and validate the work visually".

**Rule (as benches 1 and 2):** code only from the batch-D3 coder handoffs in `literature_fulltext/` (otsu1979,
bruzzone2000, pan2015, li_hu_ai2019, gibson2012, lin2013, chen2016_ihot, zhang_guindon2003, wu2014 SFA, zhang2018 DS,
li2011_pul, he2021_dabnet) as corrected by `claim_checks_D3.md`, never from abstracts. Every change forced by two-date
0.5 m display tiles is named as a **deviation**; every number that is ours, not the paper's, is labelled **ours**.

**Code:** `evidence/pilot_scripts/method_bench_3/` (new). Benches 1 and 2 (`method_bench/`, `method_bench_2/`) are
imported read-only: `b2_common` (paths, guards, memory wait), `run_ida_helpers` (CPU DINOv2 windows), bench 1's
`mb_common` (block bootstrap, McNemar, seed averages), `c_common`, `after_features.after_rows`, `run_ida` and
`ida_score.paired_tiles`, and bench 2's `run_bench2` flood machinery (`Data`, `fit_arms`, `reproduce`, `_align`).
**Figures:** `figures/method_bench_3/`. **Notebooks:** `notebooks/method_bench_3/`. **Results:**
`evidence/24_method_bench_3.md`. **Cache:** `/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache/`.

## Hard rules
- **Data:** Louisiana-East train + val only (226 tiles; 200 kept by the tile rule, 99 with a C0 gate; 1,037 touched
  roads; published labels unmodified), checked by `mb_common.dev_guard_tiles` on every tile. The Ida test's frozen
  preparation (132 usable prep tiles) is read-only. HRC_WHU: the 120 development images only (`hrc_images("train")`).
  **Never read:** SN8 test, north negative, Germany, Louisiana-West, the sealed HRC_WHU images. `allow_held_out` is
  never passed.
- **No flood labels inside any arm.** Labels are used only to score, and, for the flood model, as its training target
  (unchanged). PUL uses the published labels as they are (s = y); it changes which rows train and the decision cut.
- No library edits (`ProjectBranch/ClaudeFunctions`), no edits to benches 1/2, no commits, no promotion, no downloads
  (also no `pip install`: see Notebooks), no DINOv3, no GPU (DINOv2 on the CPU, MPS disabled).
- **Machine (16 GB; kernel panic on 29 Oct):** one heavy process at a time; `OMP_NUM_THREADS=2` (and the other BLAS
  variables) and `nice -n 10`; a memory gate before each stage and each tile (free ≥ 30% and swap ≤ 4 GB, otherwise
  wait: `b2_common.wait_for_memory`); atomic writes (`*.writing` then rename); every stage resumable from per-tile
  caches.
- **If something fails:** keep the original file as `*_before_fix.py`, fix it minimally, log a deviation here and in
  evidence 24.
- Slide-style statements give p-values only when significant; scores are never written as "#/#".

## Baselines
| Stage | Baseline | Where |
|---|---|---|
| Road gate | production dark-rise rule (dark rise > 71.36; road cannot be assessed when ≥ 0.2 of its strip is under it) | `sn8_stages.production_cloud_rule` |
| Correction | **C0** two-date dark-reference dehaze (gate ≥ 2,500 m², quantile tone curve, grey airlight, 20 m fade, t < 0.2 opaque) | `sn8_refhaze.dark_reference_dehaze` |
| Flood calls | production's tuned forest on its 96 columns, `spatial_folds` (S), seeds 662 + 1–20; reproduced at 662 as (378, 63, 103, 254) on the 798 kept roads or the run stops | `scv_common`, bench 2 `reproduce` |
| Spotter | D0 (classical + DINOv2 − dark), HRC_WHU 5-fold by land cover, reproduced against `counts_library.csv` on fold 0 or the run stops | bench 1 `run_hrc.py` |
| Colour (Phase R) | **R0** (defined below) | this bench |

## Phase G (greyscale: BT.601 grey, as now)
### G-gate family (road gates)
| Arm | What exactly | Source | Deviations / ours |
|---|---|---|---|
| **T1** Otsu on the clipped grey rise | Field: grey rise r = after − (g·before + o), (g, o) = mean/SD map over the tile's valid pixels (Du/Lin eqs.), **g clipped to [0.5, 2.0]** (o refitted on the means when clipped; tiles clipped are counted), r clipped to [−255, 255]. Pooled over the 186 training tiles, every 16th valid pixel. **Otsu over integer levels −255..255** (511 levels, eqs. 17–19), reporting k*, η*, ω1, μ0, μ1. **Accept k* if η* ≥ 0.65**; otherwise fall back to the 99th percentile of r on production-clear pixels (outside the dark-rise mask), pooled the same way. Mask = r > cut per pixel, no morphology (as bench 2's G2) | otsu1979 handoff §5 arm T1 steps 2–5 | grey in place of blue (Phase G); **the 0.65 cut-off is ours** (taken from the SAR flood-thresholding work cited by our Tiampo handoff), not Otsu's: Otsu gives no number; mean/SD map in place of Lin's selector (the handoff's own fallback) |
| **T1b** | T1 + C0's 2,500 m² minimum blob | ours | isolates the blob filter |
| **T1d** (check) | Integer-level Otsu on the pooled dark rise. If \|k* − 71.36\| > 5 DN it becomes a gate arm (dark rise > k*); otherwise 71.4 is confirmed and T1d is not run as an arm | handoff §5 step 6 | — |
| **B1** EM/Bayes hysteresis, per tile | Field y = production dark rise (valid pixels). Two-Gaussian EM (eqs. 2–4, variance with the current mean as printed), fitted on every 4th valid pixel; init α = 0.5 around M = (p1 + p99.9)/2: S_n = y < M(1 − α), S_c = y > M(1 + α); stop at relative log-likelihood change < 1e−6 or 100 iterations. **Abstain (no cloud)** if P(ω_c) < 0.002, or (μ_c − μ_n)/σ_n < 2, or μ_c < 71.4 − 2σ_n. **t_h** = the y with P(ω_c\|y) = 0.9, **t_l** = T̂_o, the eq. 7 root between μ_n and μ_c (P = 0.5; abstain if no root). 8-connected hysteresis (as G1), then the 2,500 m² blob | bruzzone2000 handoff §5 arm B1 steps 1–4 | per tile (the paper: per scene); subsample of 4 for the fit (ours, speed); the abstain constants are the handoff's starting values |
| **B1p** pooled | B1 fitted once on the pooled 186 training tiles (every 16th pixel); the same t_h, t_l on every tile. T̂_o is reported next to 71.4 | handoff step 5 | — |
| **B2-β** ICM-MRF, β ∈ {1.3, 1.6, 1.8} | B1's EM estimates and abstain rules; labels by ICM on eq. 13: data term eq. 14, context −β × (number of the 8 neighbours with the same label) (eqs. 11–12); start = per-pixel Bayes label; updates in a 4-colour (2 × 2 parity) order so each update is sequential-equivalent; stop when < 0.01% of labels change or after 30 sweeps. No blob filter | bruzzone2000 §1 step 5, handoff arm B1-MRF; β values from Table II (1.6–1.8) and the synthetic test (1.3) | the colour-coded sweep order is ours (the paper does not give one) |
| **U1** Dempster–Shafer certain/uncertain | Objects = the published SN8 road strips (the paper's eCognition segments are not available; deviation). Cue 1 (pixel, eqs. 1–3): \|after − tone(before)\| with C0's quantile tone curve (ours: the dates' tone curves differ), two-Gaussian EM per tile (B1's code), changed = posterior ≥ 0.5; m1 = (share changed, share unchanged) over the strip (eq. 7). Cue 2 (object, eq. 4): G-statistic between the strip's before and after histograms (tone-mapped before; L = 32 bins), turned into p_c / p_u by 2-cluster fuzzy c-means (m = 2) over **all** 1,037 development strips (no labels); m2 = (p_c, p_u) (eq. 8). Dempster's rule, singleton form P_c = m1c·m2c / (m1c·m2c + m1u·m2u). **Certain** if P_c ≥ 0.75 or P_u ≥ 0.75 (T = 0.75, p. 16). Gate as the handoff (step 4): a road under the production cloud mask (share ≥ 0.2) that is certain can be assessed; under the mask and uncertain → cannot assess; roads outside the mask unchanged | zhang2018 handoff §5 steps 2–4 | objects = road strips; cue 1 is the paper's own CVA/EM cue on grey, not the DINOv2 heatmap the handoff proposes (no per-pixel DINOv2 change maps exist for the 200 tiles; computing them is a CPU-hours job); FCM pooled over strips (a tile has too few roads); no SVM stage (it self-trains: labelled-data-only rule) |
| **U1s** strict | Production gate, and a kept road with any cloud (share > 0) that is uncertain → cannot assess | ours | the opposite direction (drops, never adds) |
| **D5a / D5b** boundary-weighted spotter | HRC_WHU: label boundary = pixels whose 3 × 3 neighbourhood holds both classes; d = distance to the **nearest** boundary pixel (EDT); w = 1 + α·exp(−d/σ), α = 1, σ = 8 px. D5a: w as `sample_weight` on D0's 1,000 pixels per image. D5b: 1,000 pixels per image drawn with probability ∝ w (rng (662, i, 5)), unweighted. Same folds, PCA and forest as D0 | he2021_dabnet handoff §5 steps 1–4 | nearest-boundary distance replaces the printed sum (the printed eq. 10–11 gives w ≈ 1 everywhere: handoff coding warning); σ = 4/16 not swept (would need nested folds) |

Each gate arm is a **road gate** (share of strip under the mask ≥ 0.2 → cannot assess, tile rule unchanged). Bench 2
tested gates as correction gates (all harmed); that is not repeated. **D5's flood effect is conditional:** it needs the
spotter run on all 200 SN8 tiles with full DINOv2 tokens on the CPU (≈ 1–1.5 h). It is run only if D5 passes its own
rule (pooled F1 not worse than D0 and boundary-band F1 gain interval above 0); then D5's spotter gate is compared with
D0's spotter gate (`gate_roads.csv` spot_road) on flood calls.

### G-corr family (corrections; each replaces exactly one step of C0)
All use `sn8_cloudedge.edge_parts` (C0's gate, tone curve, grey airlight A, signed distance). Each new t replaces C0's
two-date t **inside C0's gate**, spread with C0's 20 m linear fade (t = 1 − fade·(1 − t)), t < 0.2 opaque (left as is,
"cannot assess"), J = (I − A)/t + A, clipped to [1, 255]. They act only on tiles where C0 has a gate (as benches 1–2).

| Arm | t (or seam) | Source | Deviations / ours |
|---|---|---|---|
| **P1** Pan C-shift, tile C | D = 15 × 15 minimum (Pan's patch; grey: one band). C_tile = mean of tone(D_before) over C0's clear pixels (before date mapped to the after scale by C0's tone curve). t̃ = clip((A − D_after)/(A − C_tile), 0.1, 1) (eq. 12, t0 = 0.1), guided filter r = 20 px, ε = 1e−3, guide = after/255 (eq. 13). Abstain if A − C_tile ≤ 1 | pan2015 handoff §5 arm P1 steps 1–4 | C from the before date (two-date use of Pan's global constant); tone mapping of C is ours; clip of t̃ is the handoff's addition |
| **P1w** local C | P1 with C(x) = 61 × 61 box mean of tone(D_before) | handoff variant P1w | — |
| **S1** sphere DCP | n = after/A; u = box15(n), s = sqrt(box15(n²) − u²); t̃ = clip(1 − 0.95·(u − s), 0.1, 1) (eq. 17, w = 0.95, S_Ω = 15 × 15); guided filter r = 55, ε = 1e−3 on after/255 (C1's settings, as the handoff says). **No homomorphic stage, no colour transfer** | li_hu_ai2019 handoff §5 arm S1 | grey: σ = s of the one band; refinement filter unstated in the paper (guided chosen) |
| **S1p** sphere + Pan C | D_s = A·(u − s); C_tile = mean over C0's clear pixels of tone(D_s,before) (D_s,before = box15 mean − box15 SD of the before grey); t̃ = clip((A − D_s)/(A − C_tile), 0.1, 1); S1's guided filter | handoff variant S1p (**our combination**, in neither paper) | tone of a statistic is approximate (monotone map) |
| **M1** median DCP | θ = 11 × 11 median of after/A (no-data filled with 255, as `dark_channel`); t = clip(1 − 0.95·θ, 0.01, 1) (eqs. 10–11); **no refinement** | gibson2012 handoff §5 arm M1 steps 1–3 | the handoff's "C0's tone curve as in C1" has no role in a one-date t; not applied |
| **L1** Poisson seam | C0's correction at full strength inside the gate (t_data, no fade) = A_c. Ω = the gate dilated by 40 px (C0's fade band). Per pixel of Ω, 4-neighbour eq. 9 with guidance v_pq = A_c(p) − A_c(q) for pairs inside the gate and v_pq = after(p) − after(q) for every other pair, Dirichlet f* = after on ∂Ω, no-data Neumann (eq. 11 at the tile edge). Sparse direct solve; residual recorded | lin2013 handoff §5 arm L1 | **Deviation:** the literal handoff (guidance ∇A_c everywhere in Ω with A_c = C0 incl. fade) returns C0 unchanged, and with A_c at full strength it returns "C0 without fade"; dropping the guidance only on pairs that cross the gate edge is the Poisson seam (the jump is replaced by a membrane) |

### G-thr family (decision threshold / training)
| Arm | What exactly | Source | Deviations / ours |
|---|---|---|---|
| **Q1** 1/t-scaled change threshold | On C0's corrected roads, every corrected `*_change` column × max(t̄, 0.2), t̄ = mean of C0's t over the road strip. A forest split d > τ on the scaled column is d > τ/max(t̄, 0.2) on the unscaled one (cap τ/0.2), with τ learned by the forest as now (no new tuning) | gibson2012 handoff §5 arm "G1 1/t-scaled change threshold" (eq. 47, eq. 57) | the threshold is the forest's own learned split, not a single τ |
| **PUL** | Training rows = training-fold roads under the tile rule (cloudy-road rows included; production trains on its kept roads only); target s = y as published. 25% of those rows held out (V, rng 662 + seed); g = production's forest fitted on the other 75%; c = mean g over V's labelled positives (eq. 4); call flooded if g > 0.5·c (p. 719). Scored on production's kept roads | li2011_pul handoff §5 steps 1–4 | the classifier is production's forest, not a neural net (the paper allows any calibrated classifier, p. 724) |
| **PULb** binned c | PUL with c per road-cloud-share bin [0, 0.01), [0.01, 0.2), [0.2, 1]; a bin with < 5 positives in V uses the pooled c. Binned c is reported (SCAR check: flat under SCAR) | handoff step 3 (our extension, as the handoff says) | — |

PUL fits the flood-training code without changing labels (s = y; only the training rows and the decision cut change),
so it is run. Its calls come from `predict_proba`; production's calls are reproduced at seed 662 from the same code
(proba > 0.5) before PUL is scored, or PUL is not run.

## Phase R (RGB; starts only after Phase G is scored and its notebooks are executed)
| Arm | What exactly | Source |
|---|---|---|
| **R0** colour baseline | Production's 93 non-DINOv2 road features computed **per band** (R, G, B treated each as the grey input of the same code; before and after; 279 columns) in place of the 93 grey columns, + the 3 DINOv2 cues (grey, unchanged). Same forest, folds and seeds. The per-band code is checked first: on the grey band it must reproduce the road table's `*_before` and `*_after` columns (≤ 1e−6) | ours (the colour baseline the request names) |
| **D1e** IHOT-RGB gate | Step 0: clear line R = k·B + b on the before tile (`d1_colour.clear_line`), HOT⁰ on the after tile. Fit mask F = valid, not saturated, not grey fall > 2 SD of the tile's grey change, not before-date dark channel below its 5th percentile. Alternate OLS: THOT = fit of iHOT on (ΔR, ΔG, ΔB, 1) over F (eq. 3); iHOT = fit of THOT (after pixels) / c (before pixels) on (R, G, B, 1) (eq. 5); stop when \|ΔC\| < 0.001 or 30 iterations; after-blue = 255 → the tile's max iHOT. Gate: B1's EM/Bayes hysteresis + blob on iHOT (the paper gives no cut). **D1e-BR**: blue and red only | chen2016_ihot handoff §5 arm D1e steps 1–8 (Use B) |
| **A2b** Zhang HOT, lower-bound slope | Clear sample (after): outside production's dark-rise gate, outside W, all bands < 250, grey > 5. R = a·B + c; HOT = B sin θ − R cos θ; ΔHOT = HOT + c cos θ; 61 × 61 median. **W** (water proxy): (i) before-date pixels with HOT_before > its 95th percentile and grey_before < its 20th percentile; (ii) after-date "darkened" pixels (grey fall > 2 SD of the tile's grey change, the D1e rule); dilated 4 px. s_b = least-squares slope of the per-integer-ΔHOT-bin 1st-percentile lower bound on ΔHOT over bins in (2, 20] with ≥ 100 non-W pixels; abstain if < 5 bins or s_b < 0. Correct non-W pixels with 2 < ΔHOT ≤ 20: DN_b − s_b·(ΔHOT − 2); ΔHOT > 20 left as is and **"cannot assess"** (a road with ≥ 0.2 of its strip there is not assessed). Applied on every tile where it does not abstain (the paper corrects the scene). **A2b-noW** (no W) and **A2b-auto** (lower limit 2·MAD of clear ΔHOT) | zhang_guindon2003 handoff §5 arm A2b steps 1–6 |
| **ISFA-RGB** change cue | Per tile ISFA on before/after RGB (float): weighted z-scores (eqs. 23–24, 12), A, B (eqs. 25–26), `eigh(A, B)`, SFA (eq. 20), IWD T = Σ SFA_j²/√λ_j (eq. 27), v = χ²₃ sf(T) (eq. 22); stop when max \|Δ√λ\| < 1e−6 or 50 iterations; fit excludes the production dark-rise mask and saturated pixels; abstain (cue = NaN, filled with the training median) on a singular fit. Per-road columns: strip mean of IWD and of \|SFA₁\|, added to the colour baseline's columns. **ISFA-grey** control: the one-band SFA (standardised difference) strip mean | wu2014 handoff §5 arm ISFA-RGB steps 1–3, 5 |
| **Phase-G carry-overs on RGB** | The arms carried into the Phase G factorial (top 2 per family, below) rerun in RGB form where the method allows: dark-rise gates on the RGB dark channel (min over bands, then the same 20 m window); P1/S1/M1 with the minimum over bands (A = A0·[1, 1, 1], Pan's grey airlight); L1 per band; Q1 and PUL on the R0 columns; U1 with the CVA magnitude over three bands and G-statistic averaged over bands (eq. 4). T1 in RGB form = the blue rise (otsu handoff step 2 as written) | the same handoffs |

RGB corrections are scored on the Ida reference as their BT.601 grey (the reference and the DINOv2 input are grey, so
both phases share one yardstick), and on flood calls with R0's per-band after columns recomputed on the corrected RGB.

## Not run (with reasons)
- **L2 Lin cloning from the before date:** diagnostic only (it pastes pre-storm ground into the flood; lin2013 handoff
  §5). Never feeds flood calls.
- **The chip-level cloud gate (Shendryk 2019):** needs Justin's ruling on derived labels (chip labels derived from
  pixel masks).
- **FwDET edge gate:** needs a new 3DEP download.
- **DINOv3:** research-only; left out.
- **Li Hu Ai's homomorphic filter and colour transfer:** underspecified (no gains, no colour method); the handoff
  advises against the filter (it flattens real flood darkening).
- **D1e as a spotter feature (Use A):** HRC_WHU has no clear partner date.
- **The SVM stage of Zhang 2018** (self-training on own labels: labelled-data-only rule).

## Metrics and scoring (benches 1–2's, reused read-only)
**Smoke test first:** each arm on 3 development tiles (`2_23_44`, `2_15_45`, `2_19_55`): shapes, ranges, abstentions,
timings, one figure per arm. **Not scored, not used to choose anything.** Smoke observations may prompt **variants**,
logged below as dated amendments **before** the scored run; paper-faithful arms are never removed.

1. **Gates:** (a) false alarms on the 94 clear development tiles (mean share flagged; tiles > 1%); (b) Ida check:
   pooled precision/recall against satellite–NOAA disagreement (\|as is − NOAA\| > the guard's 99th percentile) on the
   132 usable prep tiles (not a cloud label: it holds real change, parallax and motion); (c) coverage (roads added and
   removed vs production) and **the accuracy of the arm's calls on the added roads** (21-seed mean, block-bootstrap
   interval; evidence 23 fix #6).
2. **Spotter (D5):** HRC_WHU pooled F1, paired per-image difference vs D0 (bootstrap 95% interval, sign test), plus
   **boundary-band F1** (grid pixels within 16 px of the label edge) and interior F1 (> 16 px).
3. **Corrections:** Ida (b) as benches 1–2: thin = score ∩ C0's gate ∩ t ≥ 0.2 (fixed for every arm); ring = 0–40 m
   outside the gate; guard = the Ida guard. **Primary** = DINOv2 feature distance to NOAA in thin, CPU only, tiles in
   decreasing thin area, every arm on a tile before the next, **3-hour token budget per phase**. Secondary = grey error
   \|arm − NOAA\| in thin and ring, edge correlation, guard grey change \|arm − as is\| (guard passes if within 1 grey
   level of C0's). Unit = tile; arm − C0; 2,000 resamples of 3 × 3 tile blocks; Wilcoxon as a check.
4. **Flood calls, every arm:** production's forest, spatial folds S, **all 21 seeds for every arm** (the seed-662 screen
   is still reported, but it no longer decides who gets 21 seeds: fits are cheap, ≈ 3 s each). Gain = accuracy minus
   production's on the roads both keep, 21-seed mean, 3 × 3 block bootstrap; seeds better / worse; correction arms also
   against C0, and Phase R arms also against R0. Exact McNemar at seed 662 vs production; **Holm** correction across
   every arm of a phase (and separately across the factorial cells).
5. **Grey error** (Ida secondary) is reported, not used to choose (as bench 2).

## Alone, then combined (pre-registered so the combo stage cannot stall)
1. Every arm alone against its baseline on its own metric (1–3) and on flood calls (4).
2. **Helped alone** = own-metric interval excluding 0 in the good direction (corrections: Ida primary below 0 with the
   guard passed; D5: paired F1 above 0), **or** 21-seed flood gain ≥ 0.
3. **Carry rule (no stall):** within each family the **top 2 arms by the family's primary metric** go into the
   factorial **whether or not they "helped alone"**; an arm that did not help alone is labelled **exploratory** in the
   factorial. Primary metric: G-gate = 21-seed flood gain vs production; G-corr = Ida primary Δ vs C0 (most negative
   first; guard-passing arms ranked before guard-failing ones; arms with no primary use the secondary grey error and are
   labelled so); G-thr = 21-seed flood gain vs production. Variants of one arm (B2-β, P1/P1w, PUL/PULb, U1/U1s, T1/T1b)
   compete like separate arms. Ties: the arm listed first.
4. **Factorial (Phase G):** levels {baseline, top-1, top-2} for each of the three families → 3 × 3 × 3 = 27 cells (the
   all-baseline cell = production refit). Corrections change the corrected columns; gates change the kept roads;
   thresholds change the columns (Q1) or training and cut (PUL). Q1 at the correction level "baseline" is applied to C0
   (Q1 is defined only on a correction; that is how Q1 alone is scored). 21 seeds per cell. **Interaction** =
   gain(cell) − Σ gain(each member alone), all against production on the cell's roads, block-bootstrap interval.
5. **Phase R:** the same carry rule and a 3 × 3 × 3 factorial with families R-gate (D1e, D1e-BR, RGB carry-over gates),
   R-corr (A2b, A2b-noW, A2b-auto, RGB carry-over corrections), R-thr/cue (ISFA-RGB, ISFA-grey, RGB Q1/PUL), with R0 as
   the baseline (gains against R0 and against production).
6. **Grey vs RGB:** the best Phase G cell against the best Phase R cell (best = highest 21-seed gain vs production),
   paired over 21 seeds on the roads both keep, plus R0 vs production.

## Decision table (for Justin; nothing is promoted)
| Verdict | Rule |
|---|---|
| **KEEP** | helps alone and in combination, interval excluding 0 |
| **MAYBE** | helps on one metric only, or within noise (21-seed gain ≥ 0 with an interval including 0) |
| **DROP** | no help, or harms (interval in the bad direction on a deciding metric) |
| **NOT RUN** | not runnable on this data, or conditional and the condition failed |

Deciding metrics as benches 1–2: the Ida primary with the guard (corrections), flood calls (all), HRC F1 (D5), coverage
and the Ida check (gates). One line of evidence per arm.

## Notebooks (key deliverable)
`notebooks/method_bench_3/01_grey_arms.ipynb`, `02_grey_combos.ipynb`, `03_rgb_arms.ipynb`, `04_rgb_vs_grey.ipynb`,
executed and saved with outputs. They load cached outputs only (each < ~2 minutes). **Tile choice rule (fixed now,
before any result):** from the Ida prep tiles that are development tiles with a NOAA view, (1) **thin cloud** = the
largest thin-cloud area (score ∩ C0 gate ∩ t ≥ 0.2); (2) **thick cloud** = the largest C0 opaque share; (3) **clear** =
a clear development tile (`clear_tiles()`) with the most touched roads; (4) **flooded** = the development tile with the
most roads labelled flooded among C0 gate tiles; (5)–(6) the smoke tiles 2_23_44 and 2_19_55 if not already chosen.
Per tile: before, after and arm output side by side; gate masks overlaid; the NOAA view where it exists; \|arm − NOAA\|;
flood calls against labels on the roads (seed 662, and the share of the 21 seeds calling flooded). Each tile gets a
short markdown cell on what to look for. Markdown states each number with its source file. **Execution:**
`jupyter nbconvert --to notebook --execute --inplace` if nbconvert exists; it is **not installed** here and installs are
not allowed, so the notebooks are executed with **nbclient** (the engine nbconvert's `--execute` uses), saved in place
with outputs (logged as a deviation).

## Known risks
- **Rare or absent cloud (B1, B2, D1e):** EM can split clear-ground noise into two Gaussians when P(ω_c) → 0; the
  abstain rules exist for this, and the clear-tile check measures it.
- **The dark rise's negative tail** (parallax, misregistration) can pull the "unchanged" Gaussian wide (B1/B2).
- **Pan/Li/Gibson are one-date DCP variants** inside a two-date gate; bench 1's C1 (He 2013) moved features away from
  NOAA, and these may too. The useful contrast is each arm against C0 and against C1's bench-1 result.
- **L1 may remove the dehazing offset** inside the gate (Poisson cloning keeps gradients, not levels).
- **Q1 acts only on corrected roads that the gate keeps** (most kept roads have t ≈ 1), so it may barely move calls.
- **U1 may admit cloud as "certain change"**: cloud is change to every two-date cue. The added-road accuracy checks it.
- **PUL's SCAR assumption fails under cloud** (labels go missing where cloud is); the binned c is the test of it.
- **A2b's water proxy** may miss turbid floodwater (then floodwater is "dehazed"); A2b-noW measures the size of it.
- **R0 triples the column count**: the forest's `max_features` sampling changes, so R0 vs production mixes "colour"
  with "more columns". Reported as such.
- **Multiple comparisons:** many arms; Holm is applied to McNemar; intervals are per comparison, read as screening.

## Amendments
(dated; written after the smoke test and before any scored run)

**Amendments 2026-10-30 20:28 (after the pooled threshold fit and the smoke test; nothing scored).** Sources:
`evidence/pilot_scripts/method_bench_3/run_thresholds.log`, `BIG/g_thresholds.json`, `smoke_test.log`,
`smoke_results.json`, figures `figures/method_bench_3/smoke_*.png`.
1. **Coding fix (deviation 1), B1/B1p/B2/U1:** the eq. 7 transcription in the bruzzone2000 handoff prints the log term
   with a minus sign; for Gaussians, eq. 6 (P_c p(T|c) = P_n p(T|n), which eq. 7 is meant to solve) gives a plus sign.
   With the minus sign the smoke tile 2_23_44 had no root between the means. The code now solves eq. 6 (plus sign);
   the posterior at the returned T̂_o is checked = 0.50 and at t_h = 0.90 on all 3 smoke tiles.
2. **Pooled fits (training tiles, not scores):** T1's integer-level Otsu on the clipped grey rise gave k* = 2, η* = 0.547
   (below 0.65), so T1 uses the registered fallback, the 99th percentile on production-clear pixels = **108.8**; 40 of
   186 training tiles had their mean/SD gain clipped. **T1d:** integer Otsu on the pooled dark rise gives k* = 72
   (η* = 0.636) against production's 71.36: within 5 DN, so **71.4 is confirmed and T1d is not an arm**. **B1p:** pooled
   EM gives P(ω_c) = 0.127, T̂_o = 96.5 and t_h = 120.5, against production's single cut of 71.4.
3. **Smoke observations (not results), no arm changed or added:**
   - **B2 (ICM) is almost the per-pixel Bayes label:** on all 3 smoke tiles ICM stopped after 1 sweep, flipping 5–14
     pixels, identically for β = 1.3, 1.6, 1.8. The dark rise is already box-smoothed over 20 m, so the MRF prior has
     nothing left to smooth. The three β arms will be (near-)identical; ties are broken by the listed-first rule (1.3).
   - **B1 per tile** cuts (t_l / t_h): 38.7/48.3, 69.4/88.9, 97.0/104.9; it flags 43.8%, 43.5% and 7.1% against
     production's 38.4%, 42.3% and 29.7%. **B1p** flags 23.2%, 31.4%, 7.2%. **T1** flags 9.6%, 9.2% and 0.0% (speckled:
     bright roofs and a road on 2_23_44 pass the grey-rise cut).
   - **S1 and M1 darken the gate strongly** (mean grey in the gate 25–53 against C0's 69–89 and "as is" 117–163): the
     one-date dark channel of a cloud is high, so t is low everywhere under it. **P1/P1w/S1p** stay within 2–8 grey levels
     of C0 on average (C_tile 24–88). **L1** brings the gate back towards "as is" (mean 106–129): Poisson cloning keeps
     the correction's gradients but takes its level from the uncorrected border, as the registered risk said.
   - **U1:** cue-1 EM fitted on all 3 tiles; G/n per strip 0.2–1.4.
   - Timings: gates 0.3–0.7 s, the six corrections 4.5–6.6 s per tile (L1's sparse solve ≈ 6 s for ~0.6 M unknowns,
     relative residual ≈ 3e−15).

**Deviation 2 (2026-10-30 21:30, during the run; no result affected).** The Phase G primary stopped at start-up:
setting `torch.backends.mps.is_available = lambda: False` (bench 2's way of forcing the CPU) before `torch._dynamo` is
first imported makes this torch version fail (`'function' object has no attribute '__wrapped__'`). Fix: import
`torch._dynamo` before the patch (one line in `run_bench3.py`, `run_bench3r.py`, `d5_sn8.py`); the original is kept as
`run_bench3_before_fix.py`. The DINOv2 model still loads on the CPU (checked). Stages already finished (tiles, gates,
ida, flood, pul, HRC) did not use torch and are unchanged.

**D5 condition met (21:30).** D5a passed its own rule (HRC_WHU pooled F1 vs D0 +0.0009 [+0.000, +0.002]; boundary band
+0.0042 [+0.003, +0.006]; `hrc_d5_numbers.json`), so D5's preregistered conditional flood test is run:
`d5_sn8.py` (D0 and D5a spotters refitted on the 120 HRC_WHU development images, CPU tokens on the 200 SN8 development
tiles, D0 reproduced against `gate_roads.csv`, 21 seeds, D5a gate paired with D0's spotter gate).

**Amendment 2026-10-31 01:12: Phase R, written after Phase G was scored and before any Phase R score.**
1. **Carry-overs from Phase G (the carry rule as registered; `carry_R.json`):** gates B1p and B1 (on the RGB dark
   channel, minimum over bands); corrections L1 and P1 (P1 with the minimum over bands and C0's grey airlight; L1 per
   band); decision arms Q1 (on the RGB corrections' t) and PULb (on R0's columns). L1, P1, Q1 and PULb are
   **exploratory** (they did not help alone in Phase G).
2. **R0 check passed:** the per-band code fed the grey band reproduces the road table's `*_before` and `*_after` columns
   on the 3 smoke tiles (max difference 3.6e−15).
3. **Choices made while coding Phase R (ours, before any score):** EM on iHOT is run on the field shifted to start at
   its 1st percentile (the paper's X_D starts at 0; iHOT's offset is arbitrary), and B1's third abstain rule (71.4 − 2σ,
   dark-rise units) is not applied to iHOT; the "darkened" proxy (D1e fit mask, A2b water proxy) is the grey fall
   centred on the tile's median change > 2 SD; A2b's 61 × 61 median of ΔHOT is computed as a 15 × 15 median on a
   4× downsampled field (approximation); ISFA abstains when it has not converged in 50 iterations (handoff step 2).
4. **Dry run (2 smoke tiles, not scored):** A2b's lower-bound slopes are 13–17 DN per ΔHOT level (Landsat's are a
   fraction of that), so A2b removes up to ~50 grey levels under cloud; ΔHOT never exceeds 20 after the median, so A2b's
   "cannot assess" rule fires on no pixel there. D1e flags 44% / 11% (production 38% / 30%). ISFA did not converge on
   2_23_44 (abstains there) and converged in 27 iterations on 2_19_55. ~50 s per tile.

**Deviation 3 (2026-10-31 03:40, after the Phase R single-arm flood scores; reading of the decision rule, nothing
rerun).** The plan names R0 as Phase R's baseline but its decision table does not say which baseline "helped alone"
uses in Phase R. R0 itself is below production (−0.90 [−1.76, −0.28]), so every Phase R arm built on R0's columns
inherits that cost. Reading used in `decide.py`: in Phase R an arm **helped alone** if its own metric or its 21-seed gain
**against R0** has an interval above 0, or its gain against production is ≥ 0; it is **not** called "harms" when its
only bad interval is against production while it beats R0; **KEEP still needs a factorial cell above production**.
Both comparisons are reported for every arm. The carry rule (ranking by the gain against production) was not changed.

**Deviation 4 (2026-10-31 06:05, after the first Phase R factorial; coding error, cells refitted).** In the Phase R
factorial the cell's road gate was intersected with the correction arm's whole gate (production's gate plus A2b's
cannot-assess rule). That removed the roads the RGB B1p / B1 gates add, so every "gate + correction" cell equalled its
"correction" cell (seen as identical numbers). Fix: intersect only with the correction's own cannot-assess rule. The
original is kept as `run_bench3r_before_fix.py` and its log as `run_bench3r_R4_combo_attempt1_bug.log`; the Phase R
combination calls were deleted from the cache and refitted. Phase G's factorial does not have this step and is
unaffected.
