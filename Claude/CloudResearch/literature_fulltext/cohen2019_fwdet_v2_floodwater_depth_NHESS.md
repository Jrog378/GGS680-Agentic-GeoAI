# Coder handoff: Cohen et al. 2019, FwDET v2.0 (NHESS 19, 2053–2065)

**Citation:** Cohen, S., Raney, A., Munasinghe, D., Loftis, J. D., Molthan, A., Bell, J., Rogers, L., Galantowicz, J.,
Brakenridge, G. R., Kettner, A. J., Huang, Y.-F., & Tsang, Y.-P. (2019). The Floodwater Depth Estimation Tool (FwDET
v2.0) for improved remote sensing analysis of coastal flooding. *NHESS* 19, 2053–2065. doi:10.5194/nhess-19-2053-2019
**Copy:** publisher PDF (CC BY 4.0), 13 pp. PDF: `/Users/jusrogers/Masters/papers/cohen2019_fwdet_v2_floodwater_depth_NHESS-summary.pdf`
(page 1 = AI summary). **Read:** pp. 2053–2065 (all). Code: github.com/csdms-contrib/fwdet. Claude, 2026-10-29.
Page numbers below are journal pages (PDF page = journal page − 2052, +1 in the summary file).

## Algorithm (p. 2054–2056)
Inputs: flood-extent polygon F (any source), DEM z (same grid used throughout), optional cost raster.
1. F → polyline → rasterise on the DEM grid → **boundary cells** B.
2. Water-surface elevation at boundary cells: WSE_b = z_b.
3. **Coastal rule (v2.0):** drop b ∈ B if z_b ≤ 0 **or any neighbour has z ≤ 0** (p. 2055).
4. For each flooded cell c ∈ F: WSE_c = WSE of the nearest remaining boundary cell (Euclidean), implemented with
   ArcGIS Cost Allocation; cost = 1000 where z ≤ 0 (and on permanent inland water from a land-cover map), 1 elsewhere,
   so allocation does not jump across water bodies. Float→int trick: multiply DEM by 1e6 before, divide after.
5. Depth d_c = WSE_c − z_c, clipped to F.
- Isolated dry islands inside F become extra boundary cells (good if real, bad if roofs/embankments).
- Open equivalent: scipy.ndimage.distance_transform_edt(~B_mask, return_indices=True) gives the nearest boundary cell;
  for the cost rule use a geodesic distance (e.g. skimage.graph.MCP_Geometric) with high cost on water.

## Evaluation (p. 2056–2059)
- Reference: calibrated hydrodynamic models (UnTRIM street-level 1–10 m for Norfolk–Portsmouth, Irene 2011, 1 m
  topobathymetric lidar; iRIC-FaSTMECH for Brazos 2016, 10 m NED). "The (calibrated) model-simulated water depth is
  assumed here to be the true water depth" (p. 2056). The street-level model vs 18 USGS high-water marks: RMSE 9.73 cm.
- **The FwDET input extent was made from the model's own depth raster** (nonzero depth → polygon), "without introducing
  potential biases by using different inundation extent data" (p. 2056). So the errors below assume a perfect extent.
- Norfolk–Portsmouth: model mean 0.77 m / FwDET 0.65 m; mean diff −0.16 m (SD 0.29); **MAD 0.18 m** (SD 0.28; 23 % of
  mean depth); most cells within 0 to −0.33 m.
- Brazos: mean 2.2 / 2.1 m; mean diff −0.16 (SD 0.46); **MAD 0.31 m** (14 %); v1.0 MAD 0.37 m.
- Max depth "considerably overpredicted" in both.

## Failure modes (verbatim cues)
- 1 m lidar: buildings "created non-flooded areas within the flooded domain which FwDET v2.0 identified as boundary
  locations", giving "false elevation reflections of sometimes multistory building roofs"; "other structures (e.g.,
  highways, overpasses, dikes) can lead to these considerable overestimations" (p. 2057).
- Underestimation near banks/shorelines; straight-line artefacts from Euclidean nearest-boundary (p. 2057).
- Real-image applications: Irene from Landsat 5 days after landfall, 30 m NED: mean 0.64 m, **max 41.7 m** ("obviously
  an overprediction"), "insufficient ground-based observations to make a quantitative accuracy determination"
  (p. 2059); Norfolk mean 0.85 m vs 0.77 model (overestimate attributed to resolution and fragmentation).
- Fragmented extents: small polygons on flat ground give ~0 depth (p. 2061).
- "The accuracy and timing, relative to the flood peak, of the remotely sensed flood map, are likely to be the greatest
  source of uncertainty" (p. 2064).

## How to apply to our pipeline / Ida test
- **Only if Justin approves a depth label** (pre-registration "Not adopted now" item; evidence 19 plan change 8).
  Possible new module `sn8_flooddepth.py` (exploratory), inputs: a flood extent (e.g. NOAA-photo water mask or our
  detector's flooded roads + water), 3DEP 1 m DEM, OSM roads.
- Steps: (1) FwDET depth on the 1 m DEM; (2) sample depth along each road centreline (median over the strip);
  (3) label flooded if median depth > margin_hi, dry if < 0 (or road not in extent), else uncertain; (4) **flag roads
  on structures** (OSM `bridge=yes`, `layer>0`, `embankment=yes`) and roads whose DEM elevation exceeds the local
  boundary-cell median by > 1 m — FwDET names these as overestimate sources; exclude boundary cells that fall on OSM
  building footprints (roof elevations) and on flagged structures before allocation.
- **Margin:** 0.18 m is a perfect-extent lower bound at 1 m lidar; real-extent cases are worse and unquantified. Keep
  the evidence-19 margin ≥ 0.5 m; report sensitivity at 0.3 / 0.5 / 1.0 m.
- **Timing:** an extent from the NOAA photo (0–2 days after the satellite, days after landfall) gives depth at photo
  time, not peak; high-water-mark surfaces give peak. Do not mix them; label which.
- **Check 3DEP is bare-earth** (DTM): FwDET's roof errors arise when buildings remain in the surface.
- **Feasibility:** good (open DEM, open algorithm, no SAR needed). Extent source is the weak link.
