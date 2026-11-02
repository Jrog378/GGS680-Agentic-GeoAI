# Coder handoff: Chen, Krajewski, Goska & Young (2017), Using LiDAR surveys to document floods: a case study of the 2008 Iowa flood

- **Citation:** Chen, B., Krajewski, W. F., Goska, R., & Young, N. (2017). Using LiDAR surveys to document floods: A case study of the 2008 Iowa flood. *Journal of Hydrology* 553, 338–349. https://doi.org/10.1016/j.jhydrol.2017.08.009
- **PDF:** `/Users/jusrogers/Masters/papers/chen2017_lidar_surveys_document_floods_2008_iowa_JHYDROL-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded through Justin's GMU session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** real PDF (`file`: PDF document; 6.3 MB). Read tool and pdfinfo: 12 pages = published range 338–349. Page-1 title, all four authors and DOI 10.1016/j.jhydrol.2017.08.009 match. §6 Conclusion (p. 348) and references (pp. 348–349) present. PASS.
- **Read:** pp. 338–349 in full (page images), including figures and the reference list.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step (§3, pp. 342–344, flow chart Fig. 5)
Assumptions (p. 342): (1) water-surface elevation (WSE) is similar within a short (~10 m) channel segment; (2) the floodplain WSE is within an interval like the adjacent main-channel WSE (used only to classify points wet/dry); (3) the flood profile does not change much during the survey.

1. **Segmentation:** split the approximate river centreline into ~10 m segments; draw 10 m-wide cross-section cut lines; each pair of neighbouring cut lines → a main river channel segment (MRCS); extend each to a 2 km-wide corresponding floodplain segment (CFS) (p. 342, Fig. 6).
2. **Channel WSE per MRCS** (p. 342): to reject banks, bridges, vegetation and power lines, (a) take the lowest elevation minE in the MRCS; (b) keep elevations in [minE, minE + 2σ]; (c) WSE μ = mean of those. **σ = 0.09 m**, the median of the per-segment standard deviations over 2,450 MRCSs (Fig. 4b). MRCSs with no points (under bridges) get the mean of the nearest up- and downstream WSEs (p. 343).
3. **Classify points in the CFS:** a LiDAR point is **flooded if its elevation is in [μ − 2σ, μ + 2σ]** (pp. 342–343, Fig. 5). A point in several CFSs takes the label from the MRCS whose centre is nearest (p. 343, Fig. 8). Intensity was **not** used: return intensity varied too much between known water points (p. 340).
4. **Floodwater-surface DEM** (p. 343–344): 2 m buffer around each flooded point, dissolve → preliminary flood boundary (2 m because ~98% of the area has > 0.5 pts/m²); fill holes < 500 m²; natural-neighbour interpolation of flooded points with the boundary as break lines, **2 m grid**, max search 5 m.
5. **Two survey days:** WSE dropped δ ≈ 0.26 m between 19 and 20 June over the overlap reach; day-2 elevations were raised by 0.26 m before merging (p. 344).
6. **Depth** = floodwater-surface DEM − non-flood bare-earth DTM (Iowa P-Library 2 m, ±18 cm vertical, hydro-conditioned) (pp. 342, 346). 7% of 1,734,115 residual pixels were negative and were dropped; depths 0–4.46 m (p. 346).
7. **Evaluation:** `RMSE_profile = sqrt(Σ (H_LiDAR,i − H_USGS,i)² / n)` against high-water marks (eq. 1, p. 344); extent consistency `F = A / (A + B + C)` against SPOT (eq. 2, p. 344).

## 2. Inputs, outputs, data needs
- **LiDAR flown during the flood:** NCALM, Optech GEMINI, 1064 nm, 750 m altitude, 70 kHz, ~42° FOV, 100% overlap; 19–20 June 2008, **about 3.5 days after the 15 June crest**, on the recession (pp. 339–340). Density 4.5 pts/m² over land, 1–1.5 (median 1.8 over 2,450 channel segments) over water (p. 340). Calibration bias < 20 cm corrected; SD over solid surfaces < 3 cm (p. 340).
- Approximate river centreline; flood-free bare-earth DTM; HWMs (22 within the reach, from USGS/FEMA's 88) and the Iowa DNR's manually edited 10 m SPOT classification of 17 June (p. 342).
- Study area: 20 km × 2 km corridor of the Iowa River below Coralville Dam; flat, almost levee-free, bed slope 0.06% (p. 339).

## 3. Quantitative results to compare against
- **Profile vs HWMs: RMSE 0.30 m** (22 HWMs; p. 345). The LiDAR profile in Fig. 9 is shown both as flown (19 June) and **raised by 0.9 m** to the crest stage (gauge 9.6 m on 15 June vs 8.7 m on 19 June); the HWMs are compared with the raised curve. The text cites the RMSE to "Section 3.4", which does not exist (the definition is §3.3); it does not say explicitly which curve the 0.30 m uses. Surface gradient 0.0004 (p. 344–345).
- **Extent vs SPOT: F = 0.72** (A = 1,535,493; B = 405,068 dry in LiDAR/wet in SPOT; C = 191,078), **0.81 if isolated ponds in the SPOT map are removed** (p. 345). SPOT was two days earlier than LiDAR, also on the recession.
- Horizontal resolution of the extent ~3 m by visual comparison with "pseudo-simultaneous" aerial photos (Fig. 12, p. 347). Flooded areas under canopy and shade were mapped (Fig. 12c–d); capability "weakened once a flood has begun to recede" (Fig. 12e–f).
- Water-point height precision: median SD 9 cm (80% of segments < 10 cm) (p. 340).
- **Depth itself was not validated.** "an unsolvable weakness of our LiDAR survey … is the absence of data assessing the accuracy of height measurements of water points" (p. 347).

## 4. Stated limitations (pp. 346–348)
- Validation is incomplete: HWMs are peak marks at different times, the survey was 3.5 days after crest, SPOT two days before the survey, and SPOT includes isolated ponds (p. 346).
- Negative depths (7%) come from LiDAR precision, georeferencing and point-to-raster conversion (p. 348).
- The horizontal-WSE-per-cross-section assumption may fail where dikes separate channel and floodplain (p. 348). Single NIR wavelength limits returns over water.
- Survey must be flown near peak flow to capture peak extent (p. 348).

## 5. How to apply to our pipeline
- **We do not have flood-time LiDAR for Ida**, so the method cannot run as is. What carries over is the **depth recipe** and the **error budget** for any depth label we build (evidence 19 rec. 8):
  - Water surface from observed water points, then subtract a pre-flood bare-earth DEM (3DEP 1 m for us), drop negative depths and report their share (paper: 7%).
  - A robust per-segment water level: lowest elevation + 2σ window, mean of those (step 2). Our analogue: for each flooded road segment, take DEM values along the mapped flood edge, keep [min, min + 2σ], average. σ must be our own DEM/edge noise, not their 0.09 m.
  - Note the timing gap: their survey was 3.5 days after crest and their profile had to be raised 0.9 m to match HWMs. For Ida, the Maxar pass and the NOAA photos are also off-peak; HWMs record peak (consistent with our rec. 8 wording).
- **Metric to reuse:** F = A/(A+B+C) (eq. 2) is the critical success index / IoU of the wet class. If we report flood-extent agreement against a reference map, use this name and give A, B, C counts as they do.
- **Not a depth accuracy:** cite 0.30 m as a **water-surface profile RMSE against 22 HWMs**, not a depth error. The paper itself says depth accuracy was not assessed.
- **Feasibility:** needs only numpy/scipy (segmenting, interpolation with `scipy.interpolate.griddata` or natural neighbour, raster subtraction) once a water-surface point set exists. Our water points would come from a flood mask edge on the DEM, as in FwDET, not from LiDAR returns.

## 6. Key quotes
- "classifying the LiDAR points inside the CFS having elevations within the interval [μ − 2σ, μ + 2σ] as flooded points" (p. 342).
- "The root mean squared error of the LiDAR-derived floodwater surface profile to high-water marks was 30 cm, the consistency between the two flooded areas derived from LiDAR and SPOT imagery was 72% (81% if suspicious isolated ponds in the SPOT-derived extent were removed)" (abstract, p. 338).
- "an unsolvable weakness of our LiDAR survey of the 2008 Iowa flood is the absence of data assessing the accuracy of height measurements of water points" (p. 347).
- "Among the 1,734,115 pixels of the residual map, 7% carry negative values" (p. 346).
