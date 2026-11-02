# Coder handoff: Zheng, D'Angelo, Maidment & Passalacqua (2022), NWM-HAND / GeoFlood checked against Hurricane Harvey high-water marks

- **Citation:** Zheng, X., D'Angelo, C., Maidment, D. R., & Passalacqua, P. (2022). Application of a large-scale
  terrain-analysis-based flood mapping system to Hurricane Harvey. *JAWRA* 58(2), 149–163.
  https://doi.org/10.1111/1752-1688.12987
- **Copy read:** the author's accepted manuscript ("has not been through the copyediting, typesetting, pagination and
  proofreading process", p. 1), from the NOAA Institutional Repository:
  https://repository.library.noaa.gov/view/noaa/57036/noaa_57036_DS1.pdf (OpenAlex lists it as an open location). It
  has 34 double-spaced, line-numbered pages; the figures are separate pages at the end. Both Wiley links (`pdfdirect`
  and `am-pdf`) returned a Cloudflare bot check (HTTP 403 HTML), which was not circumvented. **Page numbers below are the
  manuscript's.**
- **PDF with summary:** `/Users/jusrogers/Masters/papers/zheng2022_terrain_analysis_flood_mapping_harvey_JAWRA-summary.pdf`
  (page 1 = AI summary; 35 pages = 34 + 1).
- **Validation:** real PDF (1.7 MB, created 14 Jan 2022). Title and the four authors match Crossref (58(2), 149–163;
  15 published pages). Conclusions (pp. 17–18), appendix, acknowledgements, data availability and literature cited
  (pp. 19–22) are present. PASS (accepted manuscript; the typeset layout differs).
- **Pages read:** 1–34 (all). Text pp. 1–19; references pp. 19–22 skimmed; Tables 1, 2 and A.1 on rendered pp. 23–24;
  captions p. 25; figures pp. 26–34 are image-only, and Fig. 8 (p. 33) was viewed.
- **Supports evidence-19 recommendation:** #8 (depth label with a margin and a structure flag). It supports the
  structure flag strongly. It undercuts the size of the 0.5 m margin (see below). It also bears on #9 (visible-only
  labelling), because the satellite DFO extent captured only 26.2% of HWMs.

## Method (pp. 8–10)
1. **HAND depth (Eq. 1):** `d_i = h − hand_i`. Cell i is flooded if `h > hand_i`. Here `hand_i` is the cell's height
   above the nearest drainage flowline cell, and h is the reach flowline (thalweg) water depth.
2. **h from discharge:** HAND depth grids at many stages give the reach geometry (flood volume, wetted area, top width,
   hydraulic radius). Manning's equation (1-D steady flow, bed slope S, roughness n) gives a **synthetic rating curve**.
   NWM analysis-and-assimilation discharge (hourly, about 7,000 gauges nudged, archived 23 Aug–3 Sep 2017) is converted
   to h per NHDPlus MR reach (pp. 7–9).
3. **GeoFlood (p. 9):** the same HAND workflow on a 1 m lidar DEM, with flowlines re-extracted by GeoNet (nonlinear
   filtering, terrain statistics, cost minimisation) instead of NHDPlus.
4. **Checks against HWMs:**
   - Depth error (Eq. 2): `e_depth = d − d̂`, where d̂ = the HWM "height above ground".
   - Hit rate (Eq. 3): `h_r = N(d ≥ 0) / N`.
   - Ground error (Eqs. 4–5): `ĝ = ŝ − d̂` (ŝ = peak stage, NAVD88), `e_ground = g − ĝ`, where g = DEM elevation at
     the mark.
   - The mean and SD of e_depth are reported (p. 10).
5. **Manning's n calibration (pp. 10–12):** grid search over 0.01–0.2 in steps of 0.005. Done per reach (minimising the
   reach-mean depth error) and in bulk per stream order and per stream level. Fit (Eq. 6): `n = 0.2313 · o^(−1.325)`.
6. **"Observed" extent (p. 13):** for each catchment with HWMs, the flowline depth is set to `hand(HWM) + d̂` and HAND
   is re-run. So the reference extent is itself a HAND product driven by HWM depths, not an independent map.
7. **DFO comparison (pp. 15–16):** DFO max-extent (MODIS, Sentinel-1, COSMO-SkyMed, Radarsat-2) resampled to 10 m.
   Overlap, DFO-only and model-only are reported as shares of the union area.

## Data
- **Truth:** 1,263 USGS peak-summary points from more than 2,000 raw HWMs (about 5 weeks, more than 100 staff; SE Texas
  and 3 SW Louisiana parishes). 1,211 are in Texas, and 1,072 are used after a 2 km coastal buffer (tides). Each has
  peak stage (NAVD88) and height above ground (pp. 6–7, 10).
- 13 HUC6 basins; 633 catchments in the DFO comparison (NE and SW of Houston excluded for missing DFO data).
- Terrain: 1/3″ (about 10 m) NED for all of Texas. A **TNRIS 2017 lidar 1 m DEM** for part of central Texas (49
  points, 45 catchments). It is not described as 3DEP (p. 8).
- Data availability (p. 19): GeoFlood github.com/passaH2O/GeoFlood. The Harvey HWMs are on HydroShare
  (resource 2836494ee75e43a9bfb647b37260e461). Lidar from TNRIS. National HAND grids at web.corral.tacc.utexas.edu/nfiedata/.

## Outputs
- Per-cell water-depth grids and inundation extents per catchment. Per-HWM depth and ground errors. Calibrated n per
  stream order.

## Comparable results (as stated)
- Ground error, NED, all points: mean 0.06 m, SD 3.46 m. Without 4 outliers above 20 m: −0.05 m, SD 1.53 m. 29.2% of
  points are within 0.305 m and 66.0% within 1 m (p. 11).
- Depth error, NED, 1,072 points:

  | Setting | Mean (m) | SD (m) | Hit rate |
  |---|---|---|---|
  | Uncalibrated, n = 0.05 | −0.45 | 3.60 | – |
  | Reach-calibrated | −0.68 | 2.20 | 41.9% (449) |
  | Reach-calibrated, positive depths only | +0.57 | 0.94 | 60.9% (653) |
  | Stream-order-calibrated (Table 1) | −0.39 | 3.05 | – |
  | Stream-level-calibrated (Table A.1) | −0.03 | 3.63 | – |

  Source pages: 11–12, 23–24. First-order streams are worst (Table 1: −1.22 m, SD 2.69 m, n = 0.2).
- Extent, NED: modelled 5,526 km² vs HWM-reconstructed 6,049 km², i.e. **91.3% as a ratio of totals**. Per site, 48.8%
  have an area ratio between 0.5 and 1.5 and 80.1% between 0 and 2. "Nearly 20%" of sites more than double (p. 13).
- Lidar subset (49 points):
  - Ground error: mean −0.47 → −0.25 m, SD 2.19 → 1.85 m. Within 0.305 m: 44.9% vs 20.4%. Within 1 m: 73.5% vs 49.0%.
  - Reach-calibrated depth: hit rate 36.7% for both; mean −0.66 m (lidar) vs −0.84 m (NED), SD 1.36 vs 1.96 m.
  - Positive depths only: lidar 30/49, mean 0.27 m, SD 0.35 m; NED 22/49, mean 0.77 m, SD 1.06 m.
  - Stream-order calibration: −0.33 m (lidar) vs −0.74 m (NED).
  - Extent: 72.5% (lidar) vs 70.4% (NED) of the HWM-reconstructed 38.34 km².
  - Source pages: 13–15 and Table 2.
- DFO, HWM catchments: model 2,695 km² vs DFO 2,138 km². Overlap 26%, DFO-only 30%, model-only 44%. Similar results for
  rural (185) and urban (448) catchments. Statewide: overlap 21%, DFO-only 35%, model-only 44%. **Only 281/1,072
  (26.2%) of HWMs fall inside DFO** (p. 16).

## Limitations (as stated)
- Results come from NWM analysis-and-assimilation, i.e. "the best performance … for this event", not a forecast
  (p. 7).
- Sparse HWMs: a small rural reach needs 5–10 marks, and more are needed in urban areas. Interpolating sparse HWMs
  "can result in significant overestimation" (p. 6, Fig. 2).
- Residual errors come from NWM streamflow and from unmodelled backwater and hydrodynamics (p. 18). Pluvial flooding is
  not captured (p. 18).
- DFO: buildings and vegetation affect satellite detection. Multi-source reprojection and rescaling make it
  discontinuous (pp. 16–17).

## Key quotes
- "Many of the high-water marks were collected on roads and bridges across rivers in flood, whose elevations are not
  retained in the DEM." (p. 14, about hydro-enforcing)
- "High-water marks are the evidence of the highest water levels (peak height of high water) during a flood" (p. 5)
- "adopting higher resolution terrain inputs with an approximate inundation mapping approach does not necessarily
  improve the accuracy of the estimated flood extent." (p. 15)
- "using high resolution terrain results in more accurate and detailed flood depth estimates … especially near
  artificial structures in urban environments." (p. 15)
- "This relatively low hit rate indicates that the remote-sensing-based DFO inundation map may not be capable to
  capture flood conditions at higher-order streams." (p. 16)

## How to apply to our pipeline
- **Not a cloud, haze or texture module.** Nothing goes into `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`,
  `sn8_texture.py` or `sn8_glcm.py`. It **supports validation and labels**, in an evaluation script outside the
  library.
- **Depth-label margin (#8):** with lidar and positive-depth points, the depth error is 0.27 ± 0.35 m. In every NED
  setting the SD is 2–3.6 m. The evidence-19 figure "mean error about 0.5 m" is a *signed* mean, not a spread. So use a
  3DEP 1 m DEM only (never 10 m NED). Pre-register the margin from a spread, e.g. the lidar SD, plus our own HWM-vs-3DEP
  ground check, rather than from the 0.5 m mean.
- **Structure flag (#8):** hydro-enforced DEMs drop road and bridge decks, which is exactly where HWMs and our roads
  are. Before using a depth on a road, compare 3DEP ground at the road with the road surface. Our own observation from
  Fig. 8 (p. 33): in the lidar panels, the road crossing appears as a dry band through the flood. Flag bridges and
  embankments, and treat bridge cells as CANNOT ASSESS.
- **Ground-error check we can copy (Eqs. 4–5):** if Ida HWMs with peak stage and height above ground can be obtained
  (USGS STN; not located yet, per evidence 19), compute `ĝ = ŝ − d̂` vs 3DEP at each mark. This gives the DEM's error at
  our sites before any depth label is trusted.
- **Satellite-extent caution (#9):** a multi-sensor satellite maximum-extent map held only 26.2% of HWMs. That is
  evidence that image-based flood labels miss much real flooding, which matters for SpaceNet 8 labels drawn from optical
  imagery.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** nothing here needs our imagery. The
  inputs are DEM, flowlines, HWMs and optionally NWM discharge, all public. HAND on 3DEP plus Ida HWMs is feasible
  without SAR. NWM discharge is not needed if HWM depths set h, as in the paper's "observed" extent reconstruction.
  Caveats: Louisiana is coastal and tidal (the paper excluded a 2 km coastal buffer for tides), and Ida flooding around
  New Orleans was largely surge and pluvial. HAND's riverine assumption may not hold there.
