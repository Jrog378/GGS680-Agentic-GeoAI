# Coder handoff: Cohen et al. (2018), FwDET v1, floodwater depth from an inundation map and a DEM

- **Citation:** Cohen, S., Brakenridge, G. R., Kettner, A., Bates, B., Nelson, J., McDonald, R., Huang, Y.-F.,
  Munasinghe, D., & Zhang, J. (2018). Estimating floodwater depths from flood inundation maps and topography. *JAWRA*
  54(4), 847–858. https://doi.org/10.1111/1752-1688.12609 (online 17 Nov 2017, per Crossref).
- **Copy read:** the publisher's typeset early-view PDF, hosted by the CSDMS model repository:
  https://csdms.colorado.edu/csdms_wiki/images/Cohen_et_al_JAWRA2017.pdf. It is paginated "JAWRA 1–12", not 847–858.
  The Wiley open link (`pdfdirect`) returned a Cloudflare bot check (HTTP 403 HTML), which was not circumvented.
  **Page numbers below are the copy's; journal page = 846 + copy page.**
- **PDF with summary:** `/Users/jusrogers/Masters/papers/cohen2018_fwdet_floodwater_depth_JAWRA-summary.pdf` (page 1 =
  AI summary; 13 pages = 12 + 1).
- **Validation:** real PDF (6.8 MB, Acrobat Distiller, created 14 Nov 2017). Title, nine authors, volume, issue and page
  span (12 pages = 847–858) match Crossref. Conclusions, acknowledgements and literature cited are present. PASS
  (version of record, early-view pagination).
- **Pages read:** 1–12 (all), as text; Fig. 2 (method flow chart and worked grid) checked on the rendered p. 4.
- **Supports evidence-19 recommendation:** #8 (depth label with a pre-registered margin and a structure flag), and the
  Q4 answer "FwDET takes the water surface from the flood edge". The newer version, Cohen et al. 2019 (FwDET v2.0,
  `cohen2019_fwdet_v2_floodwater_depth_NHESS.md`), is the one to implement. v1 is the baseline it improved on.

## Algorithm (pp. 2–4, Fig. 2)
Inputs: flood-extent polygon (or raster, converted to polygon first) and a DEM on the same grid.
1. **Boundary cells.** Polygon → polyline → raster on the DEM grid. Holes and multiple polygons also give boundary cells
   (p. 3).
2. **Boundary elevation.** `WSE_b = DEM_b` at each boundary cell (Map Algebra conditional).
3. **Nearest-boundary assignment.** Every cell gets the elevation of its *nearest* boundary cell, by a loop of ArcGIS
   Focal Statistics with a circular neighbourhood that grows each iteration. A cell keeps the value from the smallest
   neighbourhood that reaches a boundary cell. Iterations needed ≈ max flood width / (2 × cell size). Example: 1,000 m
   width at 10 m → at least 50 (p. 3).
4. **Depth.** `d = WSE_nearest − DEM`, clipped to the flood polygon. Negative depths are removed (Fig. 2g shows them as
   0) (pp. 3–4).
5. **Optional smoothing.** ArcGIS Filter, "low-pass" = 3×3 mean (p. 4). The authors warn that it also smooths real
   sharp transitions, such as floodplain to channel.
- Assumption (p. 2, Fig. 1): negligible cross-valley water-surface slope, so the edge elevation equals the local water
  level.
- Open equivalent (my note, not in the paper): `scipy.ndimage.distance_transform_edt(~boundary, return_indices=True)`
  gives the nearest boundary cell in one call, with no loop and none of the circular-neighbour banding artefacts.

## Equations and symbols
- `d(x) = z_b*(x) − z(x)`, for `x ∈ F`, with `d < 0 → removed`. Here `z` is the DEM, `F` the flood extent and
  `b*(x) = argmin_{b ∈ B} ‖x − b‖` the nearest boundary cell. (This is my notation; the paper gives it in words and in
  Fig. 2.)

## Parameters and defaults
- Neighbourhood: circular (judged "smoother" than other shapes, p. 3). Smoothing: one 3×3 mean pass. Iterations: as
  above (100 for St. Vrain at 1 m; 200 for Brazos at 10 m).
- Runtime: 3.6 min (St. Vrain, 640×615 cells, 100 iterations) to 31.7 min (Brazos, 2087×1816, 200 iterations) on a
  4-core 3.7 GHz desktop (pp. 5–6).

## Data used
- **Validation:** iRIC-FaSTMECH hydraulic model depths. Brazos River, TX, May 2016 (10 m DEM, about 4.5 km wide).
  St. Vrain Creek, CO, Sept 2013 (1 m lidar DEM from FEMA Region VIII, about 0.3 km wide).
- **Important:** the **model-predicted extent** was the FwDET input, "to remove model-related errors" (p. 5). So the
  scores measure FwDET's simplification only, not the error from mapping the extent.
- **Demonstrations (no reference depths):** DFO MODIS 250 m map with HydroSHEDS 90 m DEM (Irrawaddy, Aug 2016). USFIMR
  Sentinel-1 10 m change-detection map with 10 m and 30 m NED (San Jacinto, TX, May 2016; includes Lake Houston and
  urban areas).

## Outputs
- A raster of depth in metres inside the flood extent.

## Comparable results (as stated)
- Brazos: mean depth 1.95 m (FwDET) vs 1.49 m (model), including zero-depth cells; max 12.4 vs 12.5 m; "RMSD" 0.37 m
  (p. 6).
- St. Vrain: mean 0.72 vs 1.28 m; max 4.64 vs 4.26 m; RMSD 0.38 m (p. 7).
- "RMSD" is defined as "the average absolute difference between all cells between the two water depth maps" (p. 6),
  which is a mean absolute difference, not an RMS.
- **My check, not the paper's:** the gap between the two means (0.46 m Brazos; 0.56 m St. Vrain) is larger than the
  reported mean absolute difference (0.37; 0.38). Over the same cells, the mean absolute difference cannot be smaller
  than the difference of the means. So the averages and the RMSD were probably computed over different cell sets (the
  paper says the means include zero-depth cells). Do not combine these numbers.
- Most of Brazos differs by < 0.5 m. Local differences exceed 5 m at the up- and downstream reach edges, where boundary
  cells sit in the channel (p. 6).
- San Jacinto: mean 0.75 m (10 m DEM) vs 1.25 m (30 m DEM); max 11.7 vs 13.3 m (p. 9).

## Limitations (as stated)
- "considerable bias in locations where the inundation extent does not align well with the DEM" (p. 1).
- Narrow valleys → large overestimates (boundary cells land on ridges). Reservoirs and large channels → underestimates
  (the DEM records the water surface, and boundary cells fall on the water body). Complex and urban flooding → "localized
  hotspots of overestimation", from misclassified boundary cells and from ponds and ditches (pp. 8, 11).
- Banding and straight-line artefacts from the Focal Statistics neighbourhood survive the low-pass filter (pp. 7–8).
- Mismatch "can result not only from relatively coarse spatial resolution but also from projection or grid-cell
  alignment issues" (p. 8).
- No observed-depth validation. High-water-mark testing is stated as future work (p. 11).
- **Not in v1:** roofs, highways, overpasses and dikes as named error sources. Those come from v2.0 (Cohen et al. 2019).

## Key quotes
- "The approach is intended for first-order overview, not detailed analysis of floodwater dynamics." (p. 2)
- "timely information about floodwater depth is important for directing rescue and relief resources, determination of
  road closures and accessibility" (p. 2)
- "Complex inundation patterns and urban flooding are prone to localized hotspots of overestimation." (p. 11)
- "We plan to further test FwDET using observed water depth from sources such as the USGS High Water Mark (HWM) data"
  (p. 11)

## How to apply to our pipeline
- **Not a cloud, haze or texture module.** Nothing here belongs in `sn8_clouds.py`, `sn8_cloudsym.py`,
  `sn8_cloudspot.py`, `sn8_texture.py` or `sn8_glcm.py`. It supports **validation and labels**: a physical cross-check
  of SpaceNet 8 / Ida flooded-road labels and of our cloud-corrected flood extents. It would live in an evaluation
  script, not in the library.
- **Recipe (implement the v2.0 variant):** take the flood extent (SN8 flood polygons, or our clear-sky water mask),
  then 3DEP 1 m DEM → boundary cells → EDT nearest-boundary WSE → depth. Sample the depth along road centrelines.
  Apply the evidence-19 #8 margin: flooded if > 0.5 m, dry if < 0, uncertain otherwise. Flag bridges, overpasses and
  embankments.
- **The interaction with haze matters:** FwDET depends entirely on where the extent edge falls. A haze- or
  cloud-shifted edge on 0.5 m imagery puts boundary cells on the wrong elevation. That is the "misclassified boundary
  cells → hotspots" failure (p. 8). So compute depth only from edges in pixels our cloud gate marks clear, or report the
  depth as uncertain wherever a boundary cell lies in a CANNOT-ASSESS cell.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** feasible. It needs only a binary extent
  and the 1 m DEM. Resample the 0.5 m mask to the 1 m DEM grid with an explicit CRS and grid alignment, since the paper
  names alignment as an error source. The quoted 0.37–0.38 m agreement excludes extent error, so expect worse with our
  extents. Peak-vs-pass-date timing (evidence 19 Q4) is not addressed by this paper.
