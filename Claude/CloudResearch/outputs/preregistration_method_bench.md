# Pre-registration: the method bench (every cloud method the full texts support, alone and then combined)

Written 2026-10-29, 22:34 EDT (file time), by Claude (AI), **before any arm was scored**. Development data only. Nothing is
promoted; `production.json` is read-only (its sha256 is checked before and after every script).

**Request (Justin, 2026-10-29):** "once the agents come back with cloud removal research, create a mockup testing
everything they found and we can decide what to keep in our project and what not to. Run comparison tests too if you
find many methods that can work together meaning test the impact alone and then in combination." Rule: code only from
knowledge validated in the full papers (the coder handoffs in `literature_fulltext/*.md`, as corrected by
`claim_checks_A/B/C.md`; where a handoff and an evidence note disagree, the handoff and claim check win).

**Code:** `evidence/pilot_scripts/method_bench/` (one module per arm, plus runners). **Figures:**
`figures/method_bench/`. **Results:** `evidence/22_method_bench.md`. Large arrays are cached on the external drive
(`/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_cache/`); the internal disk is nearly full.

## Hard rules
- Data: Louisiana-East train + val (226 tiles, 1,037 touched roads, published labels unmodified); HRC_WHU's 120
  development images through `sn8_cloudref.hrc_images("train")`. Never read: SN8 test, north negative, Germany,
  Louisiana-West, the 30 sealed HRC_WHU images. `allow_held_out` is never passed.
- Library (`ProjectBranch/ClaudeFunctions`), notebooks, results registry, the fold module and the Ida test's files are
  imported or read, never edited. No commits, no downloads, no derived labels, no DINOv3, no generative removal.
- Compute: CPU under `nice -n 10` while `pgrep -f spatialcv_gpu.py` finds the DINOv3 job; MPS for DINOv2 only after it
  ends. Modest memory; every intermediate cached.

## Baselines (what each arm replaces)
| Stage | Baseline | Where it lives |
|---|---|---|
| Detection (pixels) | **D0**: the chosen spotter, "classical + DINOv2 − dark", random forest, cut 0.5 (F1 0.868, evidence 12) | `sn8_cloudspot`, `cloud_spotting/choice.json` |
| Gate (roads) | **production gate**: tile rule + dark-rise road rule (share of strip under dark rise < 0.2) | `sn8_clouds.assessable`, `sn8_stages.production_cloud_rule` |
| Correction | **C0**: the current two-date fit, `sn8_refhaze.dark_reference_dehaze` (dark-rise gate in blobs ≥ 2,500 m², quantile tone curve on clear pixels, t from the dark channels, linear 20 m fade, t < 0.2 opaque) | `sn8_refhaze`, `sn8_cloudedge` ("current") |
| Texture | production's 96 columns (18 intensity/edge, 15 GLCM with per-tile equal-probability quantising, 60 texture incl. LBP (8, 2 px) entropy/flat/edge, 3 DINOv2 cues), tuned random forest | `sn8_stages.production_features` |

C0 is `dark_reference_dehaze` (not `either_date_dehaze`) because the factorial's two-date cues (`road_corrected_darkref_c1fd17d88e15c874.csv`), the ring measures (`sn8_cloudedge`) and every C arm below build on it. On the development tiles the before images are cloud-free, so the two differ only in the clear-pixel set.

## Arms, by pipeline stage
Page numbers are those the handoffs and claim checks give.

### Detection / gate
| Arm | What exactly | Source (handoff, page) | Replaces |
|---|---|---|---|
| **D1a** whiteness | Σ_i \|(B_i − MeanVis)/MeanVis\|, MeanVis = (R+G+B)/3 (floor 1 on 8-bit), per pixel, added to D0's columns | Zhu & Woodcock 2012, Eq. 2, p. 85 (claim_checks_C, Fmask #1). Caveat: in Fmask it is ANDed with SWIR/thermal tests, so Fmask's accuracy does not transfer (claim_checks_C #8) | D0 columns |
| **D1b** HOT distance | HOT = B sin θ − R cos θ with the clear line R = k·B + b. SN8: line fitted per tile on the **before** image's clear pixels (no mask, not saturated > 250 or < 5), HOT of the after image. HRC_WHU (one date): line fitted per training fold on the training images' expert-clear training pixels (deviation forced by the data). Constants learned by the forest, not Fmask's 0.5/0.08 (reflectance-specific, claim_checks_C Fmask #5) | Zhu & Woodcock 2012 Eq. 3, p. 85; Qiu et al. 2019 p. 8 (HOT probability) | D0 columns |
| **D1c** RGB dark channel | `sn8_clouds.dark_channel` of min(R, G, B) (He et al. 2011 Eq. 5: min over channels, then the window minimum; the library's box smoothing kept) | he2011 handoff; claim_checks_A He 2011 #5 | D0 columns |
| **D1d** blue/red gradient ratio | (mean Sobel magnitude of B over 21 px + 1) / (same for R + 1). **Our adaptation**: Shen 2014 uses a scene-mean, brightness-normalised gradient per band to set cut-offs (Eqs. 3–4, p. 227), not a per-pixel feature (claim_checks_C Shen #8) | shen2014 handoff | D0 columns |
| **D1** all colour | D1a–d together | as above | D0 columns |
| **D2** Zhang & Xiao rule | The full four-stage rule with the paper's fixed constants: HSI (Eqs. 1–3), W = (I+1)/(H+1) bilateral-filtered, Otsu clamped to [100, 150] and hue 50–80 (Eq. 7), multiscale bilateral detail map (M = 4, Ω = 7, σs,0 = 2, σr = R/10, σd = 7, levels 2–4, dilated twice 7 × 7, Otsu, low detail), median filter, components < 120 px dropped, holes filled, guided feathering (colour guide, r = 60, ε = 1e-6, threshold 60/255). Unspecified in the paper (our choices, fixed now): W's bilateral filter = OpenCV d = 7, σcolor = 0.1 (W on [0, 1]), σspace = 2; median filter 5 × 5 | zhang2014 handoff pp. 3–8; claim_checks_C Zhang & Xiao #3–7 | D0 (rule-based reference arm, no learning) |
| **D3i** Hagolle veto (i) | Inside the dark-rise mask, a pixel is **not** cloud if Δred > 1.5·Δblue, where Δband = after − tone_band(before) (quantile tone curve per band on clear pixels: valid, outside every cloud mask + 10 m), both box-smoothed over 41 px (the dark channel's 20 m scale; Hagolle works at 100–240 m) | Hagolle 2010 Eq. 2, l. 173–178 (claim_checks_A g2 #6). The 1.5 is reflectance-based; used as published (no labels to learn it from) | production gate's dark-rise mask |
| **D3ii** Hagolle veto (ii) | Inside the dark-rise mask, not cloud if the local Pearson r of before vs after grey in 41 px windows ≥ r_clear, the tile's median local r on clear pixels (label-free, scene-adaptive). The paper gives no window or threshold (l. 179–195); these are ours | Hagolle 2010 l. 179–195 | as D3i |
| **D3** both vetoes | D3i OR D3ii vetoes | | as D3i |
| **D4** calibrated probability | D0's (and D1's, if D1 is the detection winner) out-of-fold probabilities calibrated by **isotonic** regression and by **Platt** scaling (logistic on the logit), cross-fitted: the calibrator for fold k is fitted on the other four folds' held-out grid pixels. ECE (M = 15 equal-width bins), reliability diagram, Brier, NLL. Risk–coverage on HRC_WHU pixels (risk = share of accepted "clear" pixels that are expert cloud). The cut-off p* for the gate is set on the calibration folds as the largest p whose risk ≤ the risk of D0's current 0.5 cut on those folds (NOAA ECM-style: a cut set by a target, not by hand) | Guo et al. 2017 Eqs. 3, §4 pp. 3–4 (claim_checks_C Guo #3: test isotonic and Platt for a forest, do not assume temperature scaling); Heidinger & Straka 2020 pp. 29–30 (claim_checks_C #3); Ackerman 1998 Eq. 1–2 (multi-level confidence; claim_checks_C #2); Geifman & El-Yaniv 2017 (risk–coverage, claim_checks_A g7) | the 0.5 cut and the 0.2 road share |

### Correction (all on the after date's dark-rise gate, greyscale unless stated)
| Arm | What exactly | Source | Replaces |
|---|---|---|---|
| **C1** He 2013 recipe | `sn8_cloudedge` t source "opened": each date's dark channel as the 41 px minimum then 41 px maximum (opening, no box blur), t as C0, then the guided filter on t with the hazy **after** image as guide, ε = 1e-3 on [0, 1], r = 55 px (He's r/patch = 20/15 scaled to our 41 px window); C0's 20 m fade | he2013 handoff §5 p. 11; claim_checks_A He 2013 #1–2 | C0's box-blurred t |
| **C2** IR-MAD tone | IR-MAD on the RGB clear pixels (N = 3, χ²₃, weights = Pr(no change), re-weighted σ, stop at \|Δρ\| < 1e-4 or 30 iterations, every 4th pixel); invariant = Pr(no change) > 0.95; the before→after grey map = **orthogonal** regression on the invariant pixels; the gate is abstained (opaque, "cannot assess") when fewer than 1,000 invariant pixels remain. QC as the paper: 30% of invariant pixels held out, paired t and F tests (reported, not used to decide) | canty2008 handoff §1, pp. 1028–1031; claim_checks_A Canty #3, #6, #7 | C0's quantile tone curve |
| **C3a** fitted fade | Per tile: the tone-matched dark-rise excess outside the gate in 1 m distance bins (0–60 m), against log-distance; the fade width = the first bin whose median excess is within one robust SD (1.4826·MAD) of the far-clear median (> 60 m); clipped to [5, 60] m; C0 otherwise | Koren 2007 / Várnai & Marshak 2009 (brightening decays with distance; evidence 10); Fmask/Hagolle fixed buffers are operational choices (claim_checks_A g1 #4, g2 #4). The rule itself is ours | C0's fixed 20 m |
| **C3b** Poisson seam | Ω = gate dilated by the 20 m margin; the correction field c = corrected − after at full strength inside the gate; c̃ solves Δc̃ = 0 on the margin band with c̃ = c on the gate edge and 0 on the outer edge (membrane interpolant, 4-neighbour Laplacian, sparse solve); no-data treated as Neumann | Pérez et al. 2003 Eqs. 4–5, 7, p. 315 (claim_checks_A g5) | C0's linear ramp |
| **C4** minimum blob | The gate's minimum blob swept: 0, 1,250, 5,000 and 10,000 m² (C0 = 2,500) | Fmask's 3-px rule and its sensitivity sweep (claim_checks_A g1 #1; claim_checks_C Fmask #6) | 2,500 m² |
| **C5a** γ-linearisation | **Our own test** (Ju 2018 treats gamma as the dehazing operator, not input linearisation; claim_checks_C Ju 2018 #2): before and after mapped to 255·(x/255)^γ, γ ∈ {1.8, 2.2}, C0's arithmetic (tone, airlight, t, inversion) run in that space, the result mapped back; the gate is unchanged | evidence 21 arm 3-iii | C0 (γ = 1.0) |
| **C5b** band-linked RGB | **Our own test.** t from C0 taken as the green band's (grey ≈ green); t_i = t_g^((λ_g/λ_i)^1) with λ = 0.48, 0.545, 0.66 µm (WorldView blue/green/red centres); airlight per band from the same haziest pixels; each band corrected with C0's arithmetic; the grey copy is changed by BT.601 of the RGB correction | Ma et al. 2022 band link, pp. 14–15 (claim_checks_C TIIN #6, γ = 1 as their training) | C0's single grey A and t |

### Texture (the flood model's road features, both dates and after − before, inside each road strip)
| Arm | What exactly | Source | Replaces |
|---|---|---|---|
| **T1** LBP riu2 + VAR | riu2 codes (skimage "uniform", bilinear) at (P, R) = (8, 1), (16, 2), (24, 3) px; per strip and scale: entropy and flat-code share (before, after, change), the G-statistic between the before and after code histograms (Ojala Eq. 13), and mean VAR_{P,R} (before, after, change): 30 columns. Grey as sn8_texture (after histogram-matched to before; no per-window normalisation, so haze shows in VAR, as the handoff advises) | ojala2002 handoff, Eqs. 6–13, p. 982 defaults; claim_checks_C Ojala #4–5 | the 9 `lbp_*` columns |
| **T2** dense Lowe descriptor | Gaussian smoothing σ = 1 px, pixel-difference gradients, 8 signed orientation bins with linear interpolation, 4 × 4 px cells, 16 × 16 px blocks (4 × 4 cells) at a 4 px stride, Gaussian weight σ = 8 px by cell centre, L2-Hys (unit length, clip 0.2, renormalise); no keypoints. Per strip: cosine distance between the before and after pooled descriptors, mean per-block cosine distance, orientation entropy (before, after, change) and mean gradient magnitude as the separate contrast channel (before, after, change): 8 columns | lowe2004 handoff §6.1 p. 16; claim_checks_C Lowe #5 (descriptor only) | added to production (replaces nothing) |
| **T3** per-strip GLCM | sn8_glcm's settings (32 levels, 1 m, 4 directions, symmetric) but equal-probability levels computed over each road strip's own pixels per date, not over the tile | haralick1979 handoff p. 787 ("probability quantizing"); claim_checks_C Haralick #2–3 | the 15 `glcm_*` columns |

### Not included
Weather data (GOES/METAR/ERA5: context only below about 1 km; claim_checks_C Jiménez, Wagner & Kleiss, Götz), cloud
shadows (deferred by Justin), DINOv3 (research benchmark only, never an arm), derived flood-depth labels (not approved),
generative or diffusion removal, Shen 2014's homomorphic filter (filter shape H(u, v) never specified, claim_checks_C
Shen #10), Makarau 2014 (multispectral additive model needing two short-wave bands), the IHOT residual-haze map (Chen
2016 read at abstract level only, so not coded).

## Metrics and scoring

### (a) Detection arms on HRC_WHU (D0, D1a–d, D1, D2, D4)
- The library's unit: 1,000 random training pixels per image; scored on the every-4th-pixel grid; 5 folds by image,
  `StratifiedGroupKFold(5, shuffle, 662)` by land cover; DINOv2 PCA inside each training fold (`sn8_cloudspot`
  functions, imported). **Reproduction check first:** D0's per-image confusion counts must equal
  `cloud_spotting/counts_library.csv` (arm "classical + DINOv2 - dark", random forest), or the script stops.
- Pooled pixel F1 and IoU with 95% intervals from 2,000 image resamples within land cover (`sn8_cloudspot.pooled_table`);
  paired F1 vs D0 (`paired_f1`: interval from the same resamples, per-image sign test); pixel McNemar (exact, on the
  grid pixels; reported, but the pixels are not independent, so the image-resampled interval decides).
- Land cover "water" reported separately (the turbid-water false-alarm check Fmask and Shen ask for).
- D4: ECE, Brier, NLL before and after calibration, reliability diagram, and coverage at matched risk.
- **Helps alone (detection)** = paired F1 interval vs D0 above 0 (D1, D2), or ECE interval below D0's with coverage at
  matched risk not lower (D4).

### (b) Correction arms against the NOAA reference (Ida test, read-only reuse)
- Tiles: the Ida test's usable tiles (`s2_prep.csv`, coreg_ok) with at least 2,000 thin-region pixels; its frozen
  preparation (`prep/<tile>.npz`: score mask, NOAA grey tone-matched to the after image, regions). Each arm is run by
  this bench on `sn8_clouds._tile` (same grid). Regions: thin = C0's gate with t ≥ 0.2 inside the score mask; guard =
  the Ida test's guard.
- **Primary:** DINOv2 patch-feature distance to NOAA inside thin (1 − cosine of `sn8_dino.tokens`, every image with
  the same valid mask = the score mask, as the Ida test). CPU tokens cost about 130 s per image here, so tokens are
  computed only for the `sn8_dino` windows (2 × 2 grid) that hold thin pixels, identical to the full computation on
  those windows. Tiles in decreasing order of thin pixels; every arm on a tile before the next tile; stop when a 3-hour
  CPU budget is spent (or all tiles, if MPS frees up). The tiles scored are listed.
- **Secondary:** grey error |arm − NOAA| and edge (gradient) correlation in thin; clear-ground guard (grey change on
  guard pixels); the label-free edge-ring score of `sn8_cloudedge.ring_measures` (evidence 09) on all gate tiles.
- Unit: the tile; paired arm − C0 per tile; 95% intervals from 2,000 resamples of the 3 × 3 tile blocks; Wilcoxon as a
  check. **Helps alone (correction)** = feature-distance interval vs C0 below 0 (closer to NOAA), with the guard within
  ±0.01 feature distance / 1 grey level.

### (c) Every arm's effect on flood calls (spatial folds S)
- Model: production's tuned forest; folds: `spatial_folds(…, seed)` built over all 1,037 roads (as the factorial),
  training rows limited to the arm's gate; calls on every held-out road. Baseline: production's calls `c00__S__<seed>`
  from `spatial_cv/spatial_cv_flood_calls.npz` (refitted once at seed 662 as a reproduction check: 378/63/103/254).
- Columns per arm: T arms = production's 96 with their swap; C arms = production's 96 + the arm's 93 non-DINOv2
  columns recomputed on its corrected after image (prefix `td_`; gate tiles corrected, other tiles raw, as the
  factorial). The DINOv2 cues are **not** recomputed on corrected images (about 130 s per image on the CPU); C0 is
  scored the same way (its 93 columns from the cached darkref table), so every C arm is compared with C0 like for like.
  Gate arms (D3; D1/D4 if SN8 tokens exist) change the kept roads; they are scored on their own kept roads and paired
  with production on the roads both keep, with the coverage change reported.
- **Screening at seed 662:** accuracy gain vs production on the scored roads, 95% interval from 2,000 resamples of the
  3 × 3 blocks, exact McNemar. **Not worse at 662** = gain ≥ −0.5 points. Those arms are refitted for all 21 seeds:
  seed-averaged gain with its block-bootstrap interval (the same resamples for every seed), seeds better/worse.
- C arms are also reported against C0 (the step they replace).
- **D1 and D4 on flood calls need the spotter on every SN8 tile, i.e. DINOv2 tokens of 200 after images.** They run
  only if MPS frees up during the bench (or the tokens exist in the Ida cache for every tile needed); otherwise this
  part is reported as not run, and D1/D4 are judged on HRC_WHU and the Ida check only.

### (d) Detection arms against the Ida satellite–NOAA disagreement
Where the Ida preparation exists and the needed tokens are cached by the Ida test (read-only): F1 of each detection
mask against "disagreement > the guard's 99th percentile" (the Ida plan's outcome 5, with its caveat: disagreement also
includes 0–2 days of real change, parallax and moving objects; an upper-noise check, not a cloud label).

## Alone, then combined
1. Every arm alone against its baseline on its own metric ((a) or (b)) and on flood calls (c).
2. **Helped alone** = interval excluding 0 in the good direction on its own metric, **or** not worse on flood calls
   (seed-averaged gain ≥ 0 with 21 seeds).
3. Within each stage the best arm that helped alone = the largest seed-averaged flood-call gain (ties: the simpler).
4. Factorial over the stage winners (D × C × T, 2^k cells, k ≤ 3 here) on flood calls, 21 seeds; if more than four
   winners, greedy forward selection re-scored at each step. **Interaction** = gain(combination) − Σ gains(alone), with
   its block-bootstrap interval.

## Decision table (for Justin; nothing is promoted)
- **KEEP**: helps alone and in combination, with an interval excluding 0.
- **MAYBE**: helps on one metric only, or within noise.
- **DROP**: no help, or harms (interval below 0 on a metric).
One line of evidence per arm.

## Known risks
- HRC_WHU is RGB at 0.5–15 m from mixed sources; colour cues may not transfer to Maxar 0.5 m display products.
- Flood calls are mostly made on roads the production gate keeps, away from cloud, so correction arms may barely move
  them; a null there is not evidence the correction is useless for cloudy roads (they are not assessed).
- Multiple comparisons: about 25 arms; intervals are per comparison, unadjusted; read as screening.
- The DINOv2 cues of corrected images are not recomputed (compute); that part of a correction's effect is missing.
