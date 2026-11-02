# Coder handoff: Hersbach et al. (2020), The ERA5 global reanalysis

- **Citation:** Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., … Thépaut, J.-N. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society* 146(730), 1999–2049. https://doi.org/10.1002/qj.3803 (CC BY 4.0; ECMWF, agency)
- **PDF:** `/Users/jusrogers/Masters/papers/hersbach2020_era5_global_reanalysis_QJRMS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** Wiley publisher PDF downloaded through Justin's session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out). Supersedes claim_checks_C (Cloudflare block).
- **Validation:** real PDF (`file`: PDF document; 41.6 MB). Read tool and pdfinfo: 51 pages = published range 1999–2049. Page-1 title, the author list (Hersbach, Bell, Berrisford, Hirahara … Thépaut) and DOI 10.1002/qj.3803 match; "How to cite" box on p. 2049 matches. §10 Concluding remarks (pp. 2037–2042), glossary (Table 8) and references (pp. 2043–2049) present. Supporting information is online only (not in this PDF). PASS.
- **Read:** pp. 1999–2049 in full (page images), all 51 pages including tables, figures, glossary and references. This handoff focuses on what matters for weather and cloud context, as asked.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. What ERA5 is (system facts with pages)
- ECMWF IFS **Cy41r2** (operational 8 Mar–21 Nov 2016), hybrid incremental **4D-Var** with 12-h windows (09–21 and 21–09 UTC) (p. 2002, Table 2 p. 2003).
- **Resolution:** HRES **31 km (TL639), 137 levels to 0.01 hPa**; 10-member EDA at 63 km (TL319) (Table 2, p. 2003).
- **Output: hourly throughout** (uncertainty 3-hourly); 205 surface, 46 wave, 30 upper-air parameters (Table 2).
- **Distribution grid:** the CDS copy is "converted from the native reduced-Gaussian grid to a regular latitude–longitude grid (**0.25°** for the high-resolution deterministic reanalysis and 0.5° for the ensemble products)" (p. 2008). So 0.25° is a regridded product of a ~31 km model, not a 0.25° native field.
- Availability: final product 2–3 months behind real time; preliminary product within **5 days**; "both products will rarely differ" (p. 2001, 2008). Period 1979 onward at publication; 1950–1978 back-extension to follow (p. 2008, 2039).
- Archive ~5 PB in MARS; ~1 PB post-processed on the CDS (p. 2008). Online documentation: confluence.ecmwf.int/display/CKB (p. 2008).

## 2. Clouds in ERA5 (what the paper says, and does not)
- **Cloud is a model variable, not an observed product.** Large-scale cloud and precipitation scheme "based on Tiedtke (1993)", upgraded with mixed-phase cloud, prognostic rain and snow, warm-rain microphysics and ice supersaturation (p. 2009). Convection (Tiedtke 1989) revised; diurnal cycle of convection over land shifted "from noon to late afternoon" (p. 2009). Radiation McRad with McICA for "subgrid cloud structure and overlap", called **hourly on a grid 2.5 times coarser** in each direction (p. 2009).
- **Observations that touch cloud:** all-sky assimilation of microwave imagers and humidity sounders (cloud, rain, humidity) (pp. 2010, 2018); geostationary IR **clear-sky** water-vapour radiances (GOES-8 to -16 etc.) (pp. 2018–2019, Fig. 5); AMVs from tracked cloud features (p. 2019); hyperspectral IR with a cloud-detection step (McNally & Watts 2003) (p. 2018); NCEP Stage IV radar–gauge precipitation over the USA from 2009 (p. 2013). **No cloud-cover observation (e.g. METAR cloud amount, satellite cloud mask) is assimilated**; METAR is used for surface pressure (p. 2013, Fig. 4).
- **No validation of total cloud cover is presented anywhere in the paper.** The evaluations are temperature/wind/humidity fits to radiosondes, PILOT and SYNOP (Fig. 14, p. 2027), wave height vs buoys (Fig. 13), precipitation vs GPCP/GPCC/TRMM (pp. 2033–2035), energy and mass budgets.
- The field name `total_cloud_cover` does **not** appear in the paper. The paper only states that the CDS holds "a large number of near-surface parameters and other two-dimensional fields" (p. 2008).

## 3. Quantitative facts relevant to weather context
- Precipitation: global-mean correlation with monthly GPCP **77% (ERA5) vs 67% (ERA-Interim)** (abstract; p. 2035); vs GPCC over land 63% vs 50%; vs TRMM 3B43 (50°S–50°N, 1998–2018) correlation 70% vs 63%, mean absolute difference 0.58 vs 0.65 mm/day (p. 2035). Differences larger over the eastern Pacific ITCZ.
- Re-forecasts gain "up to one day" in skill vs ERA-Interim (abstract; Fig. 1).
- Tropical cyclones: central pressures lower and closer to the operational analysis than ERA-Interim; example Hurricane Florence 2018 (p. 2030).
- Storm *Lothar*: ERA5 minimum pressure about 5 hPa too high at 09 UTC, within 1 hPa at 10–11 UTC; gusts to 42 m/s vs 59 m/s observed (pp. 2030–2031, Fig. 18). Peak extremes are smoothed.
- Ensemble spread "mainly samples random errors" and "should mainly be used as a guide for the quality of representing the correct synoptic situation at a given time", not for systematic errors (pp. 2025, 2042).
- Known issues (pp. 2038–2039): systematic **jumps at window boundaries** (e.g. 0.25 m/s drop in 10 m wind over Paris at 10 UTC); rare "rain bombs" at isolated grid points (mostly Africa, orographic); unrealistically deep snow above ~1,500 m; occasional 10 m winds near 300 m/s at a few orographic points (fixed from 19 Feb 2020); Great Lakes 2 m temperature annual cycle too strong (SST not used over lakes 1979–2013).
- ERA5-Land at 9 km is the downscaled land product (p. 2039).

## 4. Inputs, outputs, data needs (for us)
- For Hurricane Ida (29 Aug–1 Sep 2021, 29.6–29.85 N, 89.9–90.15 W): one 0.25° cell is about 28 × 24 km here, covering both of our scenes; the model's effective resolution is coarser than the grid (31 km native, radiation on a 2.5× coarser grid).
- Hourly fields; the hour stamp is an analysis valid time within a 12-h 4D-Var window, so the 15–17 UTC values sit inside the 09–21 UTC window (p. 2002).

## 5. How to apply to our pipeline
- **Keep arm 7-iii as "context only"; the paper strengthens that ruling.** ERA5 cloud cover is a parametrised model diagnostic at ~31 km with no cloud-cover observation assimilated and no cloud-cover validation in the reference paper. Report it in the methods text as "ERA5 (ECMWF reanalysis, ~31 km, hourly) total cloud cover at the pass hour", not as evidence of cloud at our tiles and never as a feature or label.
- **What it can contribute:** synoptic context for Ida's pass day (pressure, wind, precipitation timing, humidity at 850/700 hPa, i.e. whether thin high cloud or a moist boundary layer is plausible). Precipitation over the US is constrained by Stage IV radar–gauge data from 2009 (p. 2013), so ERA5 precipitation timing near New Orleans is better grounded than its cloud fields.
- **Code note (if Justin ever wants the context number):** read one 0.25° cell × a few hours from the ARCO Zarr already listed in evidence 21 (xarray `open_zarr`, select nearest lat/lon and 15–17 UTC on 2021-08-31). No download of the full store. Cite this paper plus the dataset; the variable name comes from the store, not from the paper.
- **Do not** compare ERA5 cloud cover against our spotter's tile cloud fraction as if it were truth: the paper gives no basis for its accuracy at any scale.

## 6. Key quotes
- "In addition to a significantly enhanced horizontal resolution of 31 km, compared to 80 km for ERA-Interim, ERA5 has hourly output throughout, and an uncertainty estimate from an ensemble (3-hourly at half the horizontal resolution)." (abstract, p. 1999)
- "The CDS data have been converted from the native reduced-Gaussian grid to a regular latitude–longitude grid (0.25° for the high-resolution deterministic reanalysis and 0.5° for the ensemble products …)." (p. 2008)
- "The large-scale cloud and precipitation scheme, based on Tiedtke (1993), was upgraded with an improved representation of mixed-phase clouds …" (p. 2009)
- "For this reason the ensemble spread should mainly be used as a guide for the quality of representing the correct synoptic situation at a given time, rather than for long-term and/or larger-scale averages" (p. 2025).
- "For precipitation, global-mean correlation with monthly-mean GPCP data is increased from 67% to 77%." (abstract, pp. 1999–2000)
