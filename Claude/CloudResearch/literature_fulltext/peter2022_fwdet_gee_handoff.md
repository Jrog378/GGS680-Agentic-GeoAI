# Coder handoff: Peter, Cohen, Lucey, Munasinghe, Raney & Brakenridge (2022), Google Earth Engine implementation of the Floodwater Depth Estimation Tool (FwDET-GEE)

- **Citation:** Peter, B. G., Cohen, S., Lucey, R., Munasinghe, D., Raney, A., & Brakenridge, G. R. (2022). Google Earth Engine implementation of the Floodwater Depth Estimation Tool (FwDET-GEE) for rapid and large scale flood analysis. *IEEE Geoscience and Remote Sensing Letters* 19, 1501005 (5 pp.). https://doi.org/10.1109/LGRS.2020.3031190 (published online 28 Oct 2020; current version 15 Dec 2021; volume year 2022).
- **PDF:** `/Users/jusrogers/Masters/papers/peter2022_fwdet_gee-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document, version 1.4; 5.67 MB; 5 pages (Read tool and pdfinfo; pdfinfo Title = the paper title); page-1 title, six authors, GRSL vol. 19, 2022, article 1501005 and DOI 10.1109/LGRS.2020.3031190 match todo.tsv; Conclusion and References [1]–[22] present (p. 5). PASS.
- **Read:** PDF pp. 1–5 = article pp. 1–5 (article 1501005) in full (Read tool, page images), including Figs. 1–3 and eq. 1.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's page numbers (1–5).

## 1. Algorithm, step by step
FwDET-GEE "is a conceptual replication of FwDETv2.0 [6]" (p. 1). Core idea (p. 1): identify DEM elevations at the flood boundary, give each flooded cell the elevation of "its nearest boundary cell" as water surface, subtract the DEM.

The six steps as listed (p. 2):
1. **DEM acquisition.** GEE catalogue DEMs, e.g. SRTM 30 m, USGS NED 10 m (p. 2). All tests used USGS NED 10 m (p. 5). Only user input: a flood-extent layer (raster or vector) uploaded as a GEE asset (p. 2).
2. **Two DEM filtering passes** (pp. 2–3):
   - Pass 1, whole DEM: 3 × 3 square kernel ("all nine pixels are used in the calculation"); modified z-score (eq. 1, p. 3):
     `Z_m = 0.6745 (x_i − x̃) / median(|x_i − x̃|)`, x̃ = median of the nine pixels, denominator = MAD. Outlier if |Z_m| > 3.5 (threshold "based on author recommendations [16]", Iglewicz & Hoaglin). Outlier replaced by "the median of the surrounding eight pixels" (the outlier itself excluded).
   - Pass 2: same process on "DEM pixels nearest the border of the flood extent layer, since these pixels have the highest impact on producing the estimated floodwater surface elevation" (p. 2).
   - Fig. 1 (p. 2) also labels a "low-pass kernel" producing a "Smoothed DEM".
3. **Boundary elevations:** mask the flood extent out of the DEM so flood-boundary elevations can be identified (p. 3).
4. **Water surface:** "a cumulative cost gap-filling algorithm" recommended on the GEE Developer Forum, comparable to ArcGIS Cost Allocation used in FwDETv2.0 (p. 3). Limitation: "susceptibility to visual striping artifacts" (p. 3). Exact code is in the Harvard Dataverse archive (doi 10.7910/DVN/JQ4BCN); not given in the paper.
5. **Depth = modelled water surface − smoothed DEM** (p. 2 list; Fig. 1 "Subtract smoothed DEM from new surface model").
6. **Low-pass convolution** of the depth layer "to smooth the cumulative cost layer and produce a surface that is more indicative of reality" (p. 3). Kernel size not stated.
- Optional: add permanent water (JRC Global Surface Water occurrence, 30 m, 0–100%) to the flood layer for a continuous extent, then remove it from the depth layer (p. 2, Fig. 1). Optional: intersect depth with building footprints (Microsoft US Building Footprints) (pp. 2–4).

## 2. Inputs, outputs, data needs
- Inputs: flood-extent mask (any source: "user-uploaded raster/vector assets from any source", p. 2) + DEM. Extents used: Brazos (validation, model extent), DFO Michigan map from "a Landsat 8 satellite image from May 20, 2020" (p. 3), EnviroAtlas 100-year flood model (Alabama) (p. 2).
- Output: floodwater depth raster at DEM resolution.
- No imagery, no SAR, no spectral input in the depth step.

## 3. Quantitative results
Validation (pp. 3–4): Brazos River, northwest of Houston, May 2016; reference = iRIC-FaSTMECH hydrodynamic model depth as "proxy for 'true' depth"; 484 384 pixels at 10 m; metric RMSE.
- RMSE vs iRIC HM: **FwDET v2.0 0.68 m; FwDET-GEE 0.62 m** (0.06 m improvement). FwDET v2.0 vs FwDET-GEE: RMSE 0.70 m (p. 3).
- DEM without outlier filtering: filtering gave "a minor improvement in model accuracy (0.0007 m)"; Brazos "is relatively flat" (p. 3).
- Maximum depths 12.57–13.23 m; minimum 0–0.0005 m across products (p. 3).
- FwDET-GEE underestimated depth over 47.32% of the area and overestimated over 52.68%; mean underestimation 0.34 m (SD 0.62), mean overestimation 0.32 m (SD 0.42); maximum underestimation 12.56 m, maximum overestimation 4.80 m (p. 3).
- Error > 2 m: 1.2% of the area; error > 1 m: "approximately 9.2%" (p. 3).
- Fig. 2 statistics (p. 4): iRIC HM mean 2.3031, median 1.2327; FwDETv2.0 mean 1.9895, median 0.9452; FwDET-GEE mean 2.3099, median 1.2375 (m).
- Timing (pp. 4–5): Brazos ~54 km² (537 777 px) 4 min export; central Michigan ~1182 km² (11 821 973 px) 41 min; Alabama 100-year ~20 271 km² (202 711 005 px) 73 min. GFP activation map delivered 22 May 2020 for the 19 May Edenville/Sanford dam failures (p. 3).
- No comparison with high-water marks or gauges.

## 4. Stated limitations
- Cumulative cost interpolation is susceptible to "visual striping artifacts" (p. 3).
- The outlier filter's benefit was tested only on a flat area; "areas that are topographically variable may receive more benefit" (p. 3), untested.
- "A near-term goal is to ground-verify FwDET-GEE; however, access to such data is a broad limitation among the flood mapping body of science [22]." (p. 5)
- Optical flood maps have gaps: "cloud cover and satellite revisit rates can limit availability" (p. 2); the JRC water layer "can be used to fill gaps in the flood inundation layers due to cloud cover" only where water is permanent (p. 2).

## 5. How to apply to our pipeline
- **Depth notes (evidence 19).** FwDET-GEE's 0.62 m RMSE (and v2.0's 0.68 m RMSE on the same Brazos test) sits above the "about 0.2–0.5 m" range our notes quote. The units differ (our 0.18/0.31 m are Cohen 2019 mean absolute differences; these are RMSE), but a depth margin of 0.5 m would sit below one RMSE of this method on a 10 m DEM. About 9.2% of cells were off by more than 1 m.
- **Feasibility.** Needs only a flood mask and a bare-earth DEM, which fits our setup (SN8 flood labels or our predicted masks + USGS 3DEP 1 m listed in evidence 19). No NIR or imagery needed. The GEE cumulative-cost step can be replaced locally by a nearest-boundary-cell assignment (`scipy.ndimage.distance_transform_edt(..., return_indices=True)`), which is FwDET's stated rule (p. 1). Getting 3DEP tiles is a new download (ask Justin if large). The outlier filter matters more at 1 m lidar with buildings and bridges, where FwDET v2.0 named its failures.
- **Cloud link.** Depth from extent + DEM does not see through cloud; it inherits the extent. But a FwDET-style **boundary-elevation check** can act as a quality layer: a real flood edge lies near a level water surface, so a mapped flood patch whose edge elevations spread widely is suspect (e.g. a dark cloud shadow labelled as water on a slope).

### Proposed bench arm: FwDET edge-plausibility gate
1. Inputs: a binary flood map per tile (start with SpaceNet 8 flood labels on the working set to calibrate, then our predicted flood masks), bare-earth DEM resampled to the tile grid (3DEP 1 m; FwDET-GEE used NED 10 m).
2. DEM cleaning as the paper: 3 × 3 modified z-score (eq. 1), |Z_m| > 3.5 → median of the 8 neighbours; repeat on the one-pixel ring outside each flood patch.
3. Connected flood patches (8-connectivity); for each, collect DEM elevations on its outer boundary ring; compute median, robust spread (MAD × 1.4826) and the 90th−10th percentile range.
4. FwDET depth inside each patch: nearest boundary cell elevation − cleaned DEM; record the fraction of patch cells with negative depth (water surface below ground).
5. Calibrate on labelled true flood patches: starting rule = abstain/flag a patch if boundary MAD-spread > 1.0 m (≈ the paper's 1 m error tail) or > 30% of cells have negative depth; tune once on the working set only.
6. Compare: flood precision/recall (and false-positive area under cloud shadow/haze) of the predicted masks with vs without the gate, against SN8 labels on the same tiles, with McNemar on per-patch decisions. Sealed data untouched.
Caveat: on flat coastal Louisiana the edge spread of real floods may already be small and the DEM noise relative; the 1 m threshold is a starting value, not from the paper.

## 6. Key quotes
- "FwDET-GEE is a conceptual replication of FwDETv2.0 [6]" (p. 1)
- "using those elevations to assign floodwater surface elevation to each cell within the flooded domain by identifying its nearest boundary cell." (p. 1)
- "The modified z-score is calculated for each pixel using this kernel and a threshold of 3.5 used to determine outlier status." (p. 2)
- "FwDETv2.0 showed an RMSE of 0.68 m, whereas FwDET-GEE showed an RMSE of 0.62 m when compared to the iRIC HM validation layer." (p. 3)
- "depth estimations with a margin of error greater than 2 m amounted to only 1.2% of the area. More conservatively, the margin of error greater than 1 m amounted to approximately 9.2% of the area." (p. 3)
- "One limitation of cumulative cost interpolation is its susceptibility to visual striping artifacts" (p. 3)
- "A near-term goal is to ground-verify FwDET-GEE" (p. 5)
