# Coder handoff: Wilson & Jetz (2016), EarthEnv global 1 km MODIS cloud frequency (MODCF)

- **Citation:** Wilson, A. M., & Jetz, W. (2016). Remotely sensed high-resolution global cloud dynamics for predicting
  ecosystem and biodiversity distributions. *PLOS Biology* 14(3), e1002415.
  https://doi.org/10.1371/journal.pbio.1002415
- **Copy read:** the published open-access version (CC BY), PLOS printable PDF:
  https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.1002415&type=printable. 20 pages.
  Page numbers below are the PDF's "n / 20".
- **PDF with summary:** `/Users/jusrogers/Masters/papers/wilson2016_global_1km_modis_cloud_frequency_PLOSBiol-summary.pdf`
- **Validation:** real PDF (8.7 MB, 20 pp.); title, authors, volume 14(3) and article e1002415 match Crossref;
  conclusion, methods, supporting-information captions and 75 references present. PASS (published version).
- **Pages read:** 1–20. The main text (1–14) and SI captions (14–16) were read in full; references (16–20) were skimmed.
  The SI files (S1–S4 Tables, S1–S8 Figs) were **not** downloaded. The EarthEnv dataset was **not** downloaded (per brief).
- **Supports ranked fixes (evidence 21):** #12 (context only; gap 7). A small supporting point for #1 (an RGB-brightness
  cloud mask fails on bright urban surfaces).

## How the product is made (Materials and Methods, pp. 10–12)
1. **Source flag:** bit 10 of the `state_1km` SDS in daily **MOD09GA** (Terra, ~10:30 local) and **MYD09GA** (Aqua,
   ~13:30 local), Feb 2000 – Mar 2014. This is the MOD09 internal cloud mask (PGE11). It has:
   - a reflective "middle infrared anomaly" test, `MIRA = ρ20,21 − 0.82ρ7 + 0.32ρ6` (ρ = MODIS band number);
   - a 1.38 µm test (ρ26);
   - a thermal test against NCEP 2 m air temperature.
   - It is binary, with no confidence.
2. **MOD35 deliberately not used:** "due to spatially heterogeneous application of cloud tests (including recently
   reprocessed Collection 6), the MOD35 mask is unsuitable for generating global and spatially consistent maps of
   cloud frequencies at 1 km" (p. 11).
3. Monthly cloud frequency `CF_{m,y}` = proportion of days with a positive cloud flag, computed separately for Terra and
   Aqua in Google Earth Engine.
4. Orbital-gap striping was removed with VSNR, a Bayesian destriping method, using a Gabor filter (y = 200, x = 5,
   θ = ±15°). Anomalously high CF over bright, variable-albedo salt flats (Lake Eyre, Salar de Uyuni) was gap-filled
   using MCD43B3 albedo.
5. Terra and Aqua were averaged and regridded to 30 arc-sec (~1 km). The monthly climatologies were then summarised:
   - `μ_m = mean_y(CF_{m,y})` (monthly mean);
   - `σ_m = SD_y(CF_{m,y})` (inter-annual SD for each month);
   - inter-annual variability = `mean(σ_m)`;
   - intra-annual variability = `SD(μ_m)`;
   - seasonal concentration: 12 polar vectors with magnitude μ_m; |sum| / annual mean, scaled 0–100 (p. 12).
6. Daytime only: there is no data at high latitudes in winter.

## Validation numbers (p. 12; S2 Table not downloaded)
- Reference: 5,388 synoptic stations (human "total cloud", 1971–2009), compared with mean MODCF within a **16 km
  radius** of each station.
- MODIS era (2000–2009; 1,558 stations with ≥ 20 obs per month): **R² = 0.78**, n = 17,021, RMSE = 7.99% cloud frequency.
  Monthly R² ranges from 0.66 (May, RMSE 8.30%) to 0.84 (November, RMSE 7.33%).
- Full record (4,679 stations): R² = 0.74, n = 53,678.
- Biases: positive above 60° latitude; negative over monsoonal India in JJA (attributed to overpass timing vs the
  diurnal cycle). Residuals by land cover are in S4 Fig (not seen).
- Ecology results (context): cloud-forest model ΔBIC = 69; species AUC 0.68 → 0.87 (woodcreeper) and 0.82 → 0.87
  (king protea) (Table 1, p. 8).

## Key quotes and limits
- "monthly cloud frequencies from 15 y of twice-daily Moderate Resolution Imaging Spectroradiometer (MODIS) satellite
  images" (abstract, p. 1). The Methods give Feb 2000 – Mar 2014 and "2000–2014" for the climatology.
- On RGB-brightness cloud masks (Douglas et al.): "strongly dependent on the brightness threshold, and is problematic
  over high-albedo surfaces (such as urban areas or snow)" (p. 3).
- Station data are not truth: "the station observations are themselves visual estimates of cloud fraction" (pp. 12–13).
- The dataset licence is **not stated in the paper**. The paper itself is CC BY. Evidence 21's "CC BY-NC 4.0" for
  the EarthEnv files comes from the data page, which was not re-checked here.

## How to apply to our pipeline
- **Context only (fix 12, gap 7). No module change.**
  - An August-mean MODCF value at the Louisiana-East AOI could go in the methods text as "how often late-morning
    August passes are cloudy here".
  - It **cannot** say whether there was cloud or haze over a road on 31 Aug 2021. It is binary and 1 km, and averages
    15 years of a flag with no thin-haze grade.
  - If wanted, read one pixel with a ranged GeoTIFF read of `MODCF_monthlymean_08.tif`, not a full 0.88 GB download.
    This needs Justin's OK, because it is a dataset fetch.
- **Fix 1 (`sn8_cloudspot.py` `classical_cues`):** the paper's warning about RGB brightness over urban surfaces is
  independent support for scoring the whiteness cue's false positives on bright roofs and concrete separately (as
  well as turbid water).
- **Texture (`sn8_texture.py`, `sn8_glcm.py`):** not addressed.
- **Feasibility:** nothing to compute on our RGB uint8 0.5 m tiles. It is a ~1 km climatological covariate only.
