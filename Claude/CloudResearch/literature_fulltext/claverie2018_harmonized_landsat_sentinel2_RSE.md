# Coder handoff: Claverie et al. (2018), The Harmonized Landsat and Sentinel-2 (HLS) surface reflectance data set

- **Citation:** Claverie, M., Ju, J., Masek, J. G., Dungan, J. L., Vermote, E. F., Roger, J.-C., Skakun, S. V., & Justice, C. (2018). *Remote Sensing of Environment* 219, 145–161. https://doi.org/10.1016/j.rse.2018.09.002
- **PDF:** `/Users/jusrogers/Masters/papers/claverie2018_harmonized_landsat_sentinel2_RSE-summary.pdf` (page 1 = AI summary; journal pages 145–161 follow)
- **Source:** NASA Technical Reports Server, https://ntrs.nasa.gov/citations/20190028663 (publisher's typeset version). The local copy with an earlier summary prepended (`~/Claude/Personal/research/geoai-descriptions-literature/pdfs/hls-...-summary.pdf`) was **not used** and not touched, because an open copy existed.
- **Validation:** PDF, 17 pages (Read tool and pdfinfo) = published range 145–161; title/authors/DOI match Crossref; Conclusion (§7) and References present. PASS.
- **Read:** pp. 145–161 in full; reference list skimmed. Text extracted in reading order (two-column layout).
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.
- **Type:** dataset/processing-chain paper, not a cloud method. Sections below keep what we can use.

## 1. Processing chain (what each step does)
1. **Atmospheric correction, LaSRC v3.5.5** (§3.2, p. 147–148): 6S inversion, Lambertian plane-parallel atmosphere. Aerosol (AOT, Ångström) from the difference between assumed surface ratios (red/blue, red/ultra-blue; fixed globally from MODIS/MISR as a function of a mid-IR vegetation index) and observed TOA ratios. "Adjacency effects are not corrected." OLI SR uncertainty 0.11% (SWIR1) to 0.85% (blue) absolute; MSI 0.3% to 1.4%.
2. **Cloud masks** (§3.3, p. 148):
   - **Landsat 8 (LaSRC internal):** thresholds on (i) the residual of the two-ratio AOT inversion, **0.05**; (ii) TIRS band-10 brightness temperature, **305 K**. "Adjacency cloud is applied over **150 m windows (i.e., five 30 m pixels with the window size selected empirically)** surrounding cloudy pixels." Shadows from cloud location + a priori cloud height (±1 km) + band 6 TOA + band 4 − band 3 difference. Snow: any positive NDSI (low threshold "selected empirically"). Reported performance (citing Foga et al. 2017): 4.7% omission, 24% commission.
   - **Sentinel-2:** Fmask adapted without thermal, with cirrus (Zhu et al. 2015). Chosen over Hagolle 2010/Louis 2016 because those "have not yet been fully validated or compared".
3. **Co-registration** (§3.4, p. 149): AROP to a per-tile Sentinel-2 L1C (baseline ≥ 02.04) reference "with minimal cloud cover"; affine model x′ = a1 + a2x + a3y (eq. 1); tie points from NIR cross-correlation. "Cloudy areas will generally result in low correlation coefficients for the local area and the potential tie point is excluded". < 10 valid tie points → flag, no co-registration.
4. **QA resampling** (p. 149): cubic convolution for SR; for QA bits only the inner 2 × 2 of the 4 × 4 kernel, with a **"presence" rule**: any flagged pixel → output flagged. "This aggressiveness in QA resampling avoids introduction of new cloud masking omission errors."
5. **BRDF normalisation** (§3.5, p. 149–150): c-factor, fixed global kernel coefficients (Table 3), nadir view, constant per-tile solar zenith from a 6th-degree polynomial in latitude (eq. 4).
6. **Bandpass adjustment** (§3.6, p. 150–151): OLI = slope × MSI + offset per band (Table 4; slopes 0.977–1.005), fitted on 10,000 Hyperion spectra (158 scenes, PCA + k-means reduction).

## 2. Quality control (what is measured)
- **MODIS cross-comparison** (§5.2, p. 153–154): HLS aggregated to 0.05° only where 99% of pixels are clear in QA. Products flagged and dropped if > 1 CMG pixel has Δρ_green = ρ_MODIS − ρ_HLS < −0.04 or ρ_MODIS/ρ_HLS > 3 (eqs. 5–6; thresholds "set manually"); green chosen because cloud affects it and it is not used for AOT. Dropped 2.8% of S10/S30, 0.5% of L30.
- **Results:** RMSD ≤ 11% except S30 blue (bias ~30%, suspected calibration/spectral adjustment issue). CE90 6.2 m (S10), 18.8 m (L30) = 0.62 pixel; AROP failed on ~15% of products, "mostly because the extensive cloud made … the identification of tie points impossible".
- **Theoretical uncertainty** (Table 6, p. 153): blue 0.012–0.014 (25–29% relative), red 0.01 (10–13%); "undetected clouds may produce much larger errors that are not accounted in this budget".
- **Temporal consistency** (§5.4, p. 154–157): TSI noise index (eq. 7) on triplets; outlier filter = Hampel filter on NIR/red ratio (3 samples each side, flag if > 3 × MAD-based scale, window ≤ 60 days each side) AND majority of neighbours within a **150 m circular kernel** also flagged. 90th percentile TSI after filtering ≤ 0.006 (visible), ≤ 0.014 (NIR/SWIR). The filter is a diagnostic; it does not remove pixels from the product.

## 3. Stated limitations (p. 158–159)
- "The Sentinel-2 cloud mask remains a main known issue"; omissions are mostly thin cloud.
- Temporal outlier filters: "real surface changes can be mistaken for outliers. Therefore, reliable cloud masking for individual images is critical as a first step."
- Multi-temporal masks (MACCS/MAJA, Hagolle et al. 2010; Tmask) "show promise … but require regular cloud free observations of each pixel (better than monthly)".
- Adjacency effects not corrected.

## 4. How to apply to our pipeline
- **Edge band past the gate (`sn8_refhaze` / `sn8_cloudsym`, 20 m linear fade):** HLS supports buffering the cloud mask (LaSRC: 150 m = 5 pixels, empirical). In pixel units our 20 m = 40 px; in metres ours is far smaller. The HLS buffer is a hard exclusion, not a fade. Cite it as "operational masks buffer the cloud edge; width is empirical", not as support for our particular fade.
- **Resampling / downscaling any mask (e.g. `sn8_cloudspot` outputs, mask pyramids):** adopt the "presence" rule — when a mask is reduced or warped, any cloudy contributor makes the output cloudy. Never average a cloud mask and threshold at 0.5.
- **Correlation drop as a cloud cue:** AROP discards tie points whose local correlation is low under cloud — the same principle as Hagolle 2010's veto. Supports a before/after local-correlation feature in `sn8_cloudspot` or as a veto inside `cloud_gate` blobs.
- **Change vs cloud:** HLS states plainly that temporal outlier filters confuse real change with cloud. For a flood, that is our exact failure mode: a dark-rise or outlier test alone cannot separate cloud from flood; keep the "cannot assess" route.
- **Feasibility with our data (RGB uint8 0.5 m, one pre-storm date, no SAR, no NIR):** LaSRC's cloud tests need TIRS and the ultra-blue band (not available); the Hampel filter needs a time series (not available). Usable: buffer practice, presence-rule resampling, correlation-based tie-point/pixel rejection, and the honest note that thin-cloud omission is the known weak point even operationally.

## 5. Key quotes
- "Adjacency cloud is applied over 150 m windows (i.e., five 30 m pixels with the window size selected empirically)" (p. 148)
- "This aggressiveness in QA resampling avoids introduction of new cloud masking omission errors." (p. 149)
- "real surface changes can be mistaken for outliers." (p. 159)
