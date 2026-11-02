# Coder handoff: Johnson, Munasinghe, Eyelade & Cohen (2019), evaluation of NWM–HAND flood mapping

- **Citation:** Johnson, J. M., Munasinghe, D., Eyelade, D., & Cohen, S. (2019). An integrated evaluation of the National
  Water Model (NWM)–Height Above Nearest Drainage (HAND) flood mapping methodology. *Natural Hazards and Earth System
  Sciences* 19, 2405–2420. https://doi.org/10.5194/nhess-19-2405-2019
- **Copy read:** published open-access version (CC BY 4.0),
  https://nhess.copernicus.org/articles/19/2405/2019/nhess-19-2405-2019.pdf. It has 16 pages. Page numbers below are the
  **journal's** (2405–2420).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/johnson2019_nwm_hand_flood_mapping_evaluation_NHESS-summary.pdf`
- **Validation:** real PDF (5.3 MB, 16 pages by the Read tool and pdfinfo); title, four authors, volume 19 and pages
  2405–2420 match Crossref; conclusion, code/data availability, appendix and references present. PASS (version of record).
- **Pages read:** 2405–2420 (all), in text chunks; Eqs. 2–8 and Tables 2–3 checked on the rendered pp. 2409–2411.
- **Supports evidence-19 recommendation:** #8 only indirectly (as a caution on terrain-based labels; it gives **no depth
  error**). It mostly supports the Q4 "My read" caution that terrain/HAND-type references are weak at the cell level and
  in flat, urban terrain. It is not a cloud-correction method.

## What the method is (pp. 2406–2408, Fig. 1)
1. HAND raster: for every out-of-stream cell, the relief to its nearest in-stream cell (TauDEM "distance down"), on the
   10 m NED with NHDPlus medium-resolution flowlines. Cells are grouped into NHD reach catchments (COMID).
2. Synthetic rating curve (SRC) per reach from HAND-derived cross-sections, Manning (Eq. 1):
   `Q(y) = (1/N) · A · R^(2/3) · S^(1/2)` — Q discharge at stage y, N Manning's roughness, A cross-sectional area, R
   hydraulic radius, S reach slope (from the NHD attribute table).
   - Default: "a constant channel roughness (N) of 0.05 has been adopted for all of CONUS" (p. 2406).
3. Flow at the reach outlet (NWM forecast/reanalysis, or a USGS gauge) → stage from the SRC → stage raster by
   reclassifying the catchment mask → `depth = stage − HAND`; `> 0` wet, `< 0` dry (Fig. 1g–h).
4. The study used NWM **v1.2 reanalysis** at the timestamp of each satellite image (p. 2408).

## Evaluation protocol (pp. 2408–2409), reusable as code
- Reference: 28 USFIMR maps (University of Alabama), made by image classification of Landsat 5/7/8 and Sentinel-1, "with
  some ground truthing based on secondary sources (e.g., news reports, social media)" (pp. 2407–2408). Table A1 lists
  them: FL, AL, MS, ND, TX, OK, WI, IA, MN, SC, NC; **none in Louisiana**.
- Masking: concave-hull clip of the reference extent; permanent water (NHD FCodes 39004, 39009, 40300, 40307, 40308,
  40309) rasterized to the 10 m grid and set to NA (p. 2408).
- Confusion cells (Table 1): WW true wet, WD false dry (observed wet, modelled dry), DW false wet, DD true dry. First letter
  = observed.
- Metrics:
  - `AreaRatio = total wet simulation cells / total wet observed cells` (Eq. 2)
  - `A = WW / (WW + WD + DW)` (Eq. 3), `U = WD / (WW + WD + DW)` (Eq. 4), `O = DW / (WW + WD + DW)` (Eq. 5);
    A + O + U = 1. (A is the critical success index / IoU of the wet class.)
  - `ΔA = (A_NWIS − A_NWM) / A_NWIS` (Eq. 6); `nME = (control − simulation)/control` (Eq. 7);
    `nMAE = abs(control − simulation)/control` (Eq. 8).
- "we only analyze … at the given time step coinciding with the time of image capture (not necessarily peak flooding)"
  (p. 2409).

## Results to compare against (numbers as stated)
- 28 floodplains (Table 2): accurate median 0.15 / mean 0.19; over 0.25 / 0.27; under 0.47 / 0.53. Median area ratio
  73%; 82% of maps had area ratio < 1; 5 over-predicted cases with mean area ratio 230.4% (p. 2409).
- 54 gauged catchments (Table 3), NWM/NWIS: accurate median 16%/16%, mean 25%/25%; over median 45%/47%, mean 44%/47%;
  under median 26%/21%, mean 31%/28%. R² NWIS vs NWM: 0.93 (A), 0.82 (O), 0.75 (U) (p. 2410).
- NWM flow error matters little until nMAE > 60%: absolute mean ΔA rises from < 10% to > 30% (Table 4, p. 2412).
- 90% of the 54 gauged catchments are Strahler order ≥ 4; low-order reaches are on average 81% of the floodplain networks
  (p. 2412).
- Manning sensitivity: a 2nd-order reach needed N = 0.16 (Fig. 6); a 6th-order low-relief reach needed N = 0.005
  (Fig. 7a); "varying Manning's N within a range of 0.0001 and 0.2" fixed every tested section except zero-relief ones
  (p. 2416).
- Low relief: Iowa River reach floods "for any stage exceeding 0.5 m regardless of the volume of water"; NED absolute
  vertical accuracy 2.44 m (p. 2413).

## Key quotes and limits
- "NWM–HAND should be used with caution when identifying flood boundaries or making decisions of whether a cell is dry or
  wet" (abstract, p. 2405).
- "Since HAND is not a physical model, it is unable to conserve volume through space or time" (p. 2413).
- Reference-map errors: "The spectral similarity of dark vegetation and water pixels in optical satellite imagery
  contributes to uncertainties in both directions" (p. 2415); Flood ID 5 came from "a Landsat scene with 40 % cloud
  cover" (p. 2416); "no form of ground truthing is infallible" (p. 2416).
- Internal inconsistency to note: the abstract says under-prediction in "4th-order and lower-order reaches", but the body
  defines lower-order as "Strahler order of 3 or less" (p. 2412). The conclusion gives catchment over/under as 44%/31%
  (NWM means), the discussion 47%/28% (NWIS means).
- No depth validation at all: extent only ("2-D fitness statistic", p. 2409).

## How to apply to our pipeline
- **No module.** This supports **validation/labels**, not `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`,
  `sn8_texture.py` or `sn8_glcm.py`.
- **Do not use NWM–HAND extent as a road label.** At 19–25% wet-cell accuracy, and with flat, low-relief terrain as its
  named worst case, it is weaker than SpaceNet 8 labels or NOAA photos for coastal Louisiana (Ida area). At most, use it as
  a coarse "at-risk" flag to stratify errors.
- **Reuse the AOU metrics** for any flood-extent comparison (our road-flood masks against NOAA photo interpretation, or a
  3DEP-based depth mask). They are one line each, and A is the wet-class IoU. Mask permanent water first, as they do.
- **If a HAND/depth label is built (rec. 8):** compute HAND from 3DEP 1 m, not 10 m NED; the paper names DEM resolution and
  vertical accuracy as limiting in low relief. Keep the "image time ≠ peak" caveat, which the paper states for its own
  reference maps.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** our imagery is not an input to HAND. A HAND/
  SRC map needs a DEM, a flowline network and a discharge (NWM retrospective or gauges), all public. It is feasible as an
  independent reference layer, but this paper's own numbers say it is not accurate enough to score per road.
