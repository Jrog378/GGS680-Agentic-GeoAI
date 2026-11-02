# Pre-registration: method bench 2 (the papers read in full on 2026-10-30, alone and then combined)

Written 2026-10-30 by Claude (AI), **before any code was written and before any arm was scored**. Development data only.
Nothing is promoted; `production.json` is read-only (its sha256 is checked before and after every stage).

**Request (Justin, 2026-10-30):** "begin to code", for the methods in the papers read in full today. Rule (as bench 1):
code only from knowledge validated in the full papers, i.e. the coder handoffs in `literature_fulltext/` for du2002,
zhang2002, schott1988, lin2015, chavez1988, song2001, kaufman1984, you2026 and lehegaratmascle2009, as corrected by
`claim_checks_D1.md` and `claim_checks_D2.md`. Where a handoff and an evidence note disagree, the handoff and the claim
check win. Each arm is coded as its paper describes it; every change forced by two-date 0.5 m RGB tiles is named below
as a **deviation**.

**Code:** `evidence/pilot_scripts/method_bench_2/` (new folder; `method_bench/` is imported read-only, never edited:
another agent is running it). **Figures:** `figures/method_bench_2/`. **Results:** `evidence/23_method_bench_2.md`
(written after the run). Cache: `/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_2_cache/` (the internal disk is
nearly full).

## Hard rules
- Data: Louisiana-East train + val only (226 tiles, 1,037 touched roads, published labels unmodified), checked by
  `mb_common.dev_guard_tiles` on every tile. Never read: SN8 test, north negative, Germany, Louisiana-West, the sealed
  HRC_WHU images. `allow_held_out` is never passed. HRC_WHU is not used (every arm here needs two dates).
- Library (`ProjectBranch/ClaudeFunctions`), bench 1's folder, the fold module, the spatial-CV scripts and the Ida test's
  files are imported or read, never edited. No commits, no promotions, no downloads, no web lookups.
- **No flood labels in any arm.** SN8 flood attributes are the target; they are never used to choose fitting pixels.
  Road and building **geometry** (published, unmodified) is used as a mask by N2 only, and that is named as a deviation.
  No derived flood-depth labels. No DINOv3. No GPU (no MPS, no torch device): DINOv2 tokens, if run, are CPU-only.
- Machine (16 GB): one python process at a time, `OMP_NUM_THREADS=2` (and the other BLAS thread variables), no
  multiprocessing (forest fits run serially in-process). The runner checks `memory_pressure` and `vm.swapusage` before
  every tile and waits while free memory < 30% or swap > 4 GB.

## Baselines (what each arm replaces)
Bench 1's baselines, unchanged:

| Stage | Baseline | Where it lives |
|---|---|---|
| Gate (pixels → roads) | **production gate**: dark-rise mask = dark channel rise (after − before, 20 m) > 71.36 (Otsu on pooled training pixels); road "cannot assess" when ≥ 0.2 of its strip is under it | `sn8_clouds._maps`, `sn8_stages.production_cloud_rule` |
| Correction gate | **C0's gate**: the same dark-rise mask, blobs ≥ 2,500 m² | `sn8_refhaze.cloud_gate` |
| Tone (before → after map) | **C0's quantile tone curve**: 256 quantiles matched over all clear pixels (outside the gate + 10 m) | `sn8_refhaze.tone_curve` |
| Haze model | **C0**: one grey airlight A (brightest of the 0.1% highest dark channel), t from the dark channels, 20 m fade, t < 0.2 opaque | `sn8_refhaze.dark_reference_dehaze` |

All correction arms reuse bench 1's `c_common.darkref_variant` (checked equal to the library at its defaults by bench 1),
through its `tone_fn` and `gate` hooks, so each arm differs from C0 in exactly one step.

## Arms
Page numbers are the handoffs' and claim checks'.

### Gate stage (G)
| Arm | What exactly | Source | Replaces | Deviations (forced by the data) |
|---|---|---|---|---|
| **G1** hysteresis, paper thresholds | Observation field y = dark-channel rise (after − before). z_p = the p-percentile of y over the tile's valid pixels, P(y ≤ z_p) = p/100, **p = 0.1** (i.e. the 0.1th percentile); t_p = z_p reflected about the distribution mean (t_p = 2·mean − z_p); t_h = 1.25·t_p, t_l = 0.95·t_p; cloud = 8-connected components of y > t_l that contain at least one pixel > t_h (the MRF's local minimum is exactly this hysteresis rule). No blob filter, no post-processing | Le Hégarat-Mascle & André 2009, p. 354 (MRF = hysteresis), p. 357 (thresholds, read on the page image: "Let z_p be the p-percentile (i.e. P(y_diff ≤ z_p) = p/100). t_p is the z_p symmetric relative to the distribution mean"), p. 358 (p, c_h, c_l fixed for all 39 images); claim_checks_D1 #4 | the single 71.36 cut (and, as a correction gate, the 2,500 m² blob filter) | (1) y is our two-date dark-channel rise, not the paper's single-date Green − a·MIR − b deviation from the soil line (no MIR); (2) thresholds per **tile** (the paper: per image); (3) the paper's mean is "very close to 0"; ours need not be, and the formula is applied as printed |
| **G1b** hysteresis + blob | G1, then C0's 2,500 m² minimum blob | G1 + `sn8_refhaze.cloud_gate` | as G1 | ours (isolates the blob filter's share) |
| **G2** Lin blue-rise test | Blue band: Lin 2015's weighted-PCA invariant pixels (N3's selector) on blue before vs blue after, Du-style mean/SD normalisation of the before blue onto the after scale, cloud = after_blue − norm(before_blue) > T_blue, per pixel, **no** dilation/erosion/hole filling (p. 112) | Lin et al. 2015 eq. 15 p. 112 (Hagolle 2010's test with the reference composed for the same date); claim_checks_D1 Lin #2 | the dark-rise mask | (1) the reference is the before image (a two-image series; the paper composes it from 6–24 dates, eqs. 13–14); (2) the paper's 0.03 ToA reflectance has no DN equivalent on 8-bit display RGB, so **T_blue = Otsu on the pooled training-tile blue rise (every 16th valid pixel)**, production's own rule for the dark-rise cut; (3) Hagolle's snow test needs SWIR and is dropped; the red/blue veto is bench 1's D3i and is not repeated |

Each G arm is used two ways: (i) as the **road gate** (share of strip under the mask ≥ 0.2 → cannot assess, tile rule
unchanged), (ii) as the **correction gate** inside C0's arithmetic (`darkref_variant(gate=...)`).

### Tone stage (N): replaces C0's quantile tone curve (grey, per tile)
| Arm | What exactly | Source | Deviations |
|---|---|---|---|
| **N1** Du PIF | Candidates = C0's clear pixels, not saturated (≤ 250 both dates), **water removed first**: grey ≥ WATER_DN = 40 on both dates (Du's lower-bound threshold, Table 1a), and \|d − median(d)\| < D with d = after − before, D₀ = 2·MAD(d). PCA (2 × 2 covariance) of [before, after] → major axis; keep \|minor coordinate\| < l; PCA again → improved axis; PIFs = candidates with \|minor\| < l about the improved axis. Accept if Pearson r(PIFs) ≥ 0.9; else tighten (pass k = 1…4: D = D₀·0.75^k, l = l₀·0.75^k), at most 5 passes. l₀ = 2.0 DN (Table 1d, bands 4–5). Map: gain = σ_after/σ_before, offset = μ_after − gain·μ_before on the PIFs (eq. 17). QC (reported): r and \|1 − SL\|, SL = PCA major-axis slope of the normalised PIFs (pp. 127–128). Abstain (gate opaque) if no pass reaches r ≥ 0.9 or fewer than 1,000 PIFs remain | du2002 handoff §1, §5; claim_checks_D1 Du #1, #4–6 | (1) per tile, not per scene (the bench's unit; Du assumes one homogeneous linear effect per image); (2) the reference is the after date (C0's direction); in float this is equivalent to Du's max-SD reference; (3) WATER_DN = 40 on 8-bit grey is ours (Du's TM thresholds do not transfer); (4) cloud is removed by C0's gate, not by an upper DN threshold; (5) Du's analyst loop is replaced by the fixed 5-pass schedule above; (6) abstain on failure (bench 1's C2 rule) |
| **N2** Schott PIF (roofs + roads) | PIF mask = SN8 building footprints ∪ road strips (geometry only; the road band from `road_band()`), ∩ C0's clear pixels, ∩ not saturated. Map: m = σ_after/σ_before, b = μ_after − m·μ_before over the PIFs (eqs. 6–9). Segmentation check (eq. 10): histogram-matching transform of the PIF histograms vs the linear one over the PIF 5–95% before-range; ε_T = RMS difference; accept if ε_T < 2 DC, else abstain. Abstain if < 1,000 PIFs | schott1988 handoff §1, §5; claim_checks_D1 Schott #1–3 | (1) Schott segments PIFs by NIR/red ratio AND a SWIR threshold; we have neither, so the PIFs are the published SN8 footprints used as masks (labels unmodified, flood attribute never read); (2) per tile; (3) reference = after date |
| **N2b** Schott PIF (roofs only) | N2 with building footprints only (roofs are raised, so less ponding than roads) | as N2 | as N2 |
| **N3** Lin weighted-PCA PIF | 256 × 256 histogram of before grey vs after grey over **all valid pixels** (no cloud or water mask, as the paper), top row and right column zeroed. Per pixel S = 1 − (S_ED + S_SA + S_SC)/3 from the before and after **RGB** vectors (eqs. 7–10; S_ED normalised by the tile's maximum ED; S_SA in radians; S_SC = ½(1 − corr across the 3 bands), 0.5 where a vector is constant). Cell weight = Σ S of its pixels, replaced by its empirical CDF (eq. 11). Weighted PCA over occupied cells (eq. 12) → major axis. PIFs = pixels within ±d of the axis, d = the largest of 1, 2, …, 40 DN whose candidates have correlation > 0.9 (p. 111). Map: Du's mean/SD on the PIFs (eqs. 1–3). Abstain if no d passes or < 1,000 PIFs | lin2015 handoff §1, §5; claim_checks_D1 Lin #1, #7 | (1) the axis is fitted on grey (the band C0 corrects), the similarity S on RGB; (2) one global fit per tile; the time-weighted reference composite (eqs. 13–14) collapses to the before image; (3) the d search grid is ours |
| **N4** Song ridge (all pixels) | Ridge Method: 256 × 256 density plot of before grey vs after grey over **all valid pixels**, Gaussian-smoothed (σ = 1 bin); for each before column with ≥ 50 pixels, the after value of maximum density; a straight line through these ridge points, least squares weighted by column counts. Map = that line. Abstain if slope ≤ 0 | song2001 handoff §1 ("density plot … for all pixels", p. 235), §5; claim_checks_D1 Song #3 | (1) smoothing σ, the 50-pixel column minimum and the weighted fit are ours (the paper gives no fitting details); (2) per tile |
| **N4b** Song ridge (changed area excluded) | N4 on C0's clear pixels only, i.e. the cloud excluded as the paper excluded "the area of substantial land-use change" | p. 235 | the flood itself cannot be excluded without labels (named risk) |

### Haze stage (A)
| Arm | What exactly | Source | Deviations |
|---|---|---|---|
| **A1-k** Chavez band-linked airlight, k ∈ {0, 0.5, 0.7, 1, 2} | C0's gate, tone, t and fade unchanged. Airlight per band: A_blue = the blue maximum over C0's haziest pixels (the 0.1% highest after dark channel); A_green = A_blue·(0.545/0.48)^−k, A_red = A_blue·(0.66/0.48)^−k (Chavez's relative scattering model λ^−k, Table 2). Each band: (a_i − A_i)/t + A_i (opaque left as is); the grey copy changes by BT.601 of the RGB change (as bench 1's C5b) | chavez1988 handoff §1, §5 (arm 3-iv); claim_checks_D1 Chavez #2, #4, #6 | (1) Chavez subtracts one constant haze DN per band over the whole image; here the power law links the **airlight** inside He's model, as the handoff's arm 3-iv proposes; (2) equal band gains assumed (unknown on display RGB; the paper notes DN ordering can invert, p. 475); (3) k is swept instead of chosen from the TM1 starting-haze classes (Table 5 is TM-DN-specific); k = 0 is the paper's "complete scattering (cloud)" end-member; (4) t is C0's for all bands (band-linked t is bench 1's C5b and is not repeated) |
| **A2** Zhang HOT-level haze removal | Clear line on the after date's clear pixels (blue vs red, least squares, red on blue); HOT = B·sinθ − R·cosθ (eq. 1); HOT rounded to integer levels; per level and band, lower bound = 1st percentile (levels with < 100 pixels skipped and interpolated); clear level = the median HOT of the clear pixels; Δ_b(h) = lowerbound_b(h) − lowerbound_b(h_clear), made monotone non-decreasing in h and ≥ 0 above h_clear, 0 at or below it; subtract Δ_b(HOT(pixel)); water excluded from the clear line and the level histograms | zhang2002 handoff §1, §5; claim_checks_D1 Zhang #2, #5, #10 | **NOT RUNNABLE on SN8 now.** The paper's water mask is a near-IR threshold (TM4); the project has **no water mask** (searched: library, ProjectBranch, CloudResearch pilot scripts). Floodwater raises HOT (p. 179; our evidence 20 on 2_14_51), so running without one would "dehaze" floodwater. Coded and unit-tested on synthetic haze only; it runs as soon as Justin names a water mask (open question) |

### Dropped, with reasons
- **Lv et al. 2016** (radiative-transfer thin-cloud removal): needs TOA reflectance, a near-IR band and water pixels
  under the cloud (claim_checks_D2 Lv #3–4).
- **You et al. 2026** (CA-MTCR): needs co-registered SAR on every date (its change cue is SAR-only, eq. 10), a 30-date
  Sentinel-2 series and supervised training with a cloud-free target (claim_checks_D2 You #1–2, #5). The cosine-weight
  idea on DINOv2 features is our adaptation, not the method, and is left out.
- **Kaufman 1984**: a physical model (adjacency transfer fraction, atmospheric MTF) with no correction algorithm that
  runs without aerosol optical thickness. Its use for us is the corrected texture argument (claim_checks_D2 Kaufman #6),
  not an arm.
- **Schott 1988's spectral PIF segmentation** (NIR/red ratio, SWIR threshold): no NIR/SWIR; replaced by footprints (N2).
- **Lin 2015's reference composite** (eqs. 13–14) and **Hagolle's snow test**: need a time series / SWIR.
- **Song 2001's absolute methods** (DOS1–4, DDV, MDDV, PARA): need radiance calibration, solar geometry or SWIR; the
  dark-object idea is covered by Chavez (A1).
- **Le Hégarat-Mascle 2009's shadow steps** and its mist/cloud property: shadows are out of scope (deferred by Justin).
- **Already in bench 1** (not repeated): HOT as a detection feature (D1b), IR-MAD tone (C2), band-linked t (C5b),
  Hagolle vetoes (D3), minimum-blob sweep (C4).

## Metrics and scoring (bench 1's, reused read-only)
Unit test first (step 2 of the request): each arm on 2–3 development tiles (`2_23_44`, `2_15_45`, `2_19_55`): shapes,
ranges, abstentions, one figure per arm. **Not scored, not used to choose anything.** WATER_DN and every constant above
are fixed now; if the smoke test shows a coding error, the fix is recorded in an amendment section below before the run.

### (a) Gate arms (G1, G1b, G2)
- **False alarms on clear tiles:** share of valid pixels flagged on the clear development tiles
  (`sn8_refhaze.clear_tiles()`), against the production dark-rise mask. Lower is better. (Le Hégarat-Mascle's own Q3
  false-alarm rate on clear images was 100%, p. 359–360; this is the check for it.)
- **Ida upper-noise check** (prep read-only, as bench 1's (d)): per usable Ida tile, precision and recall of the gate
  against "grey disagreement |after − NOAA| > the guard's 99th percentile" inside the score mask. Caveat as bench 1:
  disagreement includes 0–2 days of real change, parallax and moving objects; not a cloud label.
- **Road coverage:** roads kept vs production (added, removed).

### (b) Correction arms (G1/G1b/G2 as correction gates, N1–N4b, A1-k) against the NOAA reference (Ida test prep, read-only)
- Same tiles, regions and rules as bench 1 (b): usable prep tiles with ≥ 2,000 thin pixels; thin = C0's gate with
  t ≥ 0.2 inside the score mask (fixed for every arm, so arms are compared on the same pixels); ring = 0–40 m outside
  C0's gate; guard = the Ida guard.
- **Secondary (always run):** grey error |arm − NOAA| and edge correlation in thin and ring; guard grey change.
- **Primary (run only when the machine is free; CPU, 2 threads, a 3-hour budget):** DINOv2 patch-feature distance to
  NOAA in thin (1 − cosine of `sn8_dino` tokens, the score mask as valid for every image), tiles in decreasing thin
  order, every arm on a tile before the next. If not run, the report says so and the correction arms are judged on (c)
  and the secondary metrics only, labelled as secondary.
- Unit: the tile; arm − C0 per tile; 95% interval from 2,000 resamples of the 3 × 3 tile blocks; Wilcoxon as a check.
  **Helps alone (correction, own metric)** = the primary interval below 0, guard within ±1 grey level.

### (c) Every arm on flood calls (spatial folds S), as bench 1 (c)
- Production's tuned forest, `spatial_folds(all 1,037 roads, seed)`, calls on every held-out road; baseline =
  production's cached calls `c00__S__<seed>`, reproduced at seed 662 first (378/63/103/254 on the 798 kept roads) or
  the script stops. Fits are serial (in-process `scv_common._task`), no pool.
- Correction arms (N, A, G-as-correction-gate): production's 96 columns + the arm's 93 non-DINOv2 columns recomputed on
  its corrected after image (bench 1's `after_features.after_rows`), gate tiles corrected, other tiles raw; also
  reported against C0 scored the same way (bench 1's own C0 rows are recomputed here, not read from bench 1's cache).
- Gate arms (G-as-road-gate): production's columns; training rows and scoring on the arm's kept roads, paired with
  production on the roads both keep; coverage change reported.
- **Screen at seed 662:** accuracy gain vs production on the scored roads, block-bootstrap 95% interval, exact McNemar.
  **Not worse at 662** = gain ≥ −0.5 points → refitted at all 21 seeds (seed-averaged gain, interval, seeds
  better/worse).

## Alone, then combined
1. Every arm alone against its baseline on its own metric ((a) or (b)) and on flood calls (c).
2. **Helped alone** = own-metric interval excluding 0 in the good direction, **or** 21-seed flood gain ≥ 0.
3. Stage winners: within G, N and A, the arm that helped alone with the largest 21-seed flood gain (ties: the simpler,
   i.e. listed first). The A1 k-sweep counts as one arm family: its winner is one k.
4. Factorial over the stage winners (G × N × A, ≤ 2³ cells) on flood calls, 21 seeds. **Interaction** =
   gain(combination) − Σ gains(alone), block-bootstrap interval. Combining with bench 1's winners is a separate,
   later pre-registration (bench 1 has not finished).

## Decision table (for Justin; nothing is promoted)
| Verdict | Rule |
|---|---|
| **KEEP** | helps alone and in combination, interval excluding 0 |
| **MAYBE** | helps on one metric only, or within noise |
| **DROP** | no help, or harms (interval below 0 on a metric) |
| **NOT RUN** | not runnable on this data (A2 until a water mask exists) |

One line of evidence per arm.

## Known risks
- **Wet impervious surfaces (N2, N2b):** Schott requires that "the impervious surfaces that predominate the PIF
  population can be assumed to be reasonably dry" (p. 14). The after date is post-hurricane: roads and roofs may be wet
  or flooded for days, so the fit absorbs wet-surface darkening as if it were atmosphere. The roofs-only variant reduces
  ponding, not wetness. Any N2 gain or loss must be read with this in mind.
- **Flood is the majority change on flooded tiles (N1, N3, N4, G2):** Du's assumption 4 ("consistently changed targets
  are not the majority", p. 124), Lin's density weighting and Song's ridge all assume stable ground dominates. On mostly
  flooded tiles the fit can follow the flood. N1's water threshold removes dark water only; turbid water is not dark.
- **Weak pixel agreement at 0.5 m:** clear ground correlates poorly between the dates pixel by pixel (r = 0.46 and 0.09
  on two tiles, `sn8_refhaze` docstring). Du's r ≥ 0.9 and Lin's 0.9 will then be met only by narrow bands around the
  axis (small l or d), so the "invariant" pixels are partly defined by the axis itself. PIF counts and d/l are reported.
- **Linear vs nonlinear tone (N1–N4):** every paper here fits a straight line; C0's quantile curve exists because the
  8-bit display product's tone curves differ by date and are not linear (`sn8_refhaze` docstring, briefing P3). A
  straight line may lose to C0 for that reason alone.
- **Hysteresis false alarms on clear tiles (G1):** the paper's thresholds come from each image's own distribution, so a
  cloud-free tile still gets thresholds and may flag noise (the paper's Q3 false alarm on clear images was 100%). G1b's
  blob filter and the clear-tile check (a) measure this.
- **G2's threshold** is ours (Otsu), not the paper's 0.03 ToA; the per-pixel 0.5 m blue rise is noisy (Lin works at
  30 m).
- **Chavez's power law is for path radiance in radiance units**; display RGB has unknown gains and a possibly
  nonlinear stretch, so the DN-domain link may be wrong for any k.
- **Corrections may barely move flood calls:** most calls are made on roads the gate keeps, away from cloud (bench 1's
  risk, unchanged).
- **Multiple comparisons:** 16 runnable arms; intervals per comparison, unadjusted; read as screening.
- The DINOv2 cues of corrected images are not recomputed (compute), as bench 1.

## Amendments
Dated 2026-10-30, after the smoke test (`evidence/pilot_scripts/method_bench_2/smoke_test.log`,
`smoke_results.json`; figures `figures/method_bench_2/smoke_*.png`) and **before the full run**. Nothing has been scored.

1. **N1 QC (coding fix, not a method change).** With two dates, the major-axis slope of the *same* PIFs after their own
   mean/SD matching is exactly 1 by construction (equal variances), so the smoke test printed SL = 1.0 on every tile.
   Du had three images normalised to a shared reference, where SL is informative. The code now reports SL of the PIFs
   **re-selected** from the normalised candidates and SL over all candidates. Not used to accept or reject.
2. **G2 fallback (coding rule written into the code before the smoke test; recorded here).** If N3's selector abstains
   on a tile's blue band, that tile's blue map falls back to mean/SD matching over all valid pixels (logged per tile),
   so the cloud test still runs. Without it the gate would have no answer on that tile.
3. **A2 code check added:** a second synthetic case on a grey surface (R = G = B), where HOT moves only with haze, to
   check the code where the paper's dark-target assumption holds by construction.

**Not changed, but flagged for Justin before the full run (smoke observations, 3 tiles; not results):**
- **G1 as printed is far more conservative than production.** The dark-rise field is not centred on 0 (tile means
  57.6, 72.9 and 65.5) and its lower tail is long, so t_l = 136–170 and t_h = 179–224 against production's single
  cut of 71.4. G1 flagged 11.6%, 4.3% and 0.0% of valid pixels where production's dark rise flags 38.4%, 42.3% and
  29.7%; visually it keeps only the cloud cores (`smoke_G1_hysteresis.png`). The blob filter (G1b) removed nothing on
  these tiles. A centred variant (thresholds about the mean) would be a deviation from the printed formula.
- **N2 (Schott) abstained on all 3 tiles:** eps_T = 6.8, 6.6, 14.7 DC (roofs + roads) and 4.5, 5.6, 13.6 (roofs only)
  against the paper's < 2 DC acceptance. As registered, N2 and N2b will mostly equal "no correction".
- **N3 (Lin) can fit a near-vertical axis:** on 2_15_45 it accepted d = 1 with gain 32.9 and offset −2,706, which made
  black artefacts in the corrected image (`smoke_N3_Lin_wPCA.png`); it abstained on 2_23_44 (no d with r > 0.9) and gave
  gain 0.42 on 2_19_55. The weighted axis follows the shape of the occupied scatterplot cells (CDF weights compress the
  density), and cloud pixels stretch that shape vertically. The registered rule abstains only on gain ≤ 0.
- **N4 (Song ridge) is nearly flat:** slopes 0.057 / 0.066 (2_23_44) and 0.125 / 0.140 (2_19_55), negative (abstain) on
  2_15_45: the after-date mode hardly depends on the before value. That matches the paper's warning about substantial
  change.
- **N1 water threshold removes much of the clear ground:** grey < 40 on either date removed 59.6%, 34.3% and 13.3% of
  the clear pixels; the fit still passed r ≥ 0.9 (0.96, 0.99, 0.99) with gains 0.29, 0.34, 0.53.
- **N1's quality check fails on all 3 tiles** (amendment 1): SL of the re-selected PIFs 6.77, 5.23 and 1.42 (all
  candidates: 6.58, 5.06, 1.44), against Du's achieved |1 − SL| ≤ 1.6%. The narrow ±2 DN band around a weakly
  correlated cloud of points sets the gain; the bulk of the clear ground does not follow it. Reported, not used.
- **A2 code check:** on the grey synthetic surface, mean |error| inside the haze blob fell from 9.7 / 12.0 / 14.3 (R/G/B)
  to 4.4 / 4.3 / 4.1; on the real-colour synthetic (before RGB) only blue moved (14.3 → 13.0; R and G unchanged),
  because bluish dark surfaces (shadows) sit at high HOT levels without haze, which is the paper's own dark-target
  assumption failing. The arm stays not runnable on SN8 (no water mask).
- **A1:** k > 0 turns the near-white cloud orange/yellow in the corrected RGB; k = 0 (grey airlight, the paper's
  cloud end-member) looks most natural on these tiles (`smoke_A1.png`).

**Decisions on the flagged items (2026-10-30, before any run; coordinator's call under Justin's standing rule "test
ideas as arms and compare").** Every paper-faithful arm above is kept unchanged. These arms are **added**, and each is
a **DEVIATION from its paper**:
4. **G1c (deviation from Le Hégarat-Mascle 2009):** the dark-rise field is centred on its tile mean first (the paper's
   field is ~0-mean by construction), so t_p = mean − z_p, t_h = mean + 1.25·t_p and t_l = mean + 0.95·t_p. 8-connected
   hysteresis, no blob filter. It is used as both a road gate and a correction gate, like G1.
5. **N2c (deviation from Schott 1988):** N2 (roofs + roads) without the ε_T < 2 DC acceptance. ε_T is still reported.
   N2 itself stays as printed (it will mostly abstain, and that is the honest result).
6. **N3-bounded and N4-bounded (deviation from Lin 2015 and Song 2001):** N3 and N4 (all pixels) that also abstain when
   the fitted gain/slope is outside [0.1, 10]. Only for N3 and N4. The unbounded originals stay.
7. **N1b (deviation from Du 2002):** N1 with no water removal. There is no WATER_DN sweep.
8. **A2** stays coded and not run. It is waiting on a water mask (the GGS680 water mask is planned, not built).
9. **Primary metric:** the DINOv2 Ida primary (CPU only, 2 threads, 3-hour budget) is now in the run order (`all`). It
   starts only after the DINOv3 job, the Ida chain and bench 1 have ended (`run_bench2.wait_for_other_jobs`).

Runnable arms are now 25: G1, G1b, G1c, G2 (each as both road gate and correction gate); N1, N1b, N2, N2b, N2c, N3,
N3-bounded, N4, N4-bounded, N4b; A1 with k = 0, 0.5, 0.7, 1, 2. The stage-winner rule is unchanged: the G, N and A
families each pick one winner. The multiple-comparisons risk grows with the extra arms; the results remain screening.
1-tile dry run with the new variants (2_23_44): every arm ran. G1c's cuts on this tile were t_l 139 / t_h 165 (G1:
136 / 179), and it flagged 11.1% of valid pixels (G1 11.6%, production 38.4%). N2c fitted (gain 0.44) where N2 abstained.
N4-bounded abstained (slope 0.057), and N3-bounded abstained like N3 (no d with r > 0.9).
