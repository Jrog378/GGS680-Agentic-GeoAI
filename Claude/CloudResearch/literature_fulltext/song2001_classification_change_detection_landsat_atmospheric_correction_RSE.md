# Coder handoff: Song, Woodcock, Seto, Lenney & Macomber (2001), Classification and change detection using Landsat TM data: When and how to correct atmospheric effects?

- **Citation:** Song, C., Woodcock, C. E., Seto, K. C., Lenney, M. P., & Macomber, S. A. (2001). *Remote Sensing of Environment* 75(2), 230–244. https://doi.org/10.1016/S0034-4257(00)00169-3
- **PDF:** `/Users/jusrogers/Masters/papers/song2001_classification_change_detection_landsat_atmospheric_correction_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 0.40 MB; 15 pages (Read tool and pdfinfo) = published range 230–244; page-1 title and authors (Song, Woodcock, Seto, Lenney, Macomber) match; footer "REMOTE SENS. ENVIRON. 75:230–244 (2001)" and "PII S0034-4257(00)00169-3" match the DOI. Conclusions (pp. 242) and References (pp. 242–244) present. PASS. (`file` metadata says 10 pages; ignored.)
- **Read:** pp. 230–244 in full (Read tool, page images), including Tables 1–7 and Figs. 1–6.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. What the paper tests
Two questions (p. 230): when is atmospheric correction necessary before classification and change detection, and which method is best?

**Reasoning (pp. 232–233):**
- Single-date classification: subtracting a constant per band only translates the origin; the covariance is unchanged, so DOS "have no effect on classification results" (Fig. 2). Same for post-classification change detection and multidate composites classified as one image: "as long as the training data are derived from the image being classified, atmospheric correction is unnecessary".
- Image differencing (eqs. 1–2): `D_ijk = D'_ijk + C`, C = A_k(1) − A_k(2), the difference in additive effects; correction just shifts the threshold by C. Can be omitted when thresholds are found empirically, "However, for change detection algorithms that assume a zero mean for stable classes in the difference image, radiometric normalization needs to be applied before taking the difference" (p. 233).
- NDVI (eq. 4): additive effects enter non-linearly → correction needed (p. 233).

**Methods compared (pp. 233–236):**
- DOS family, eq. 6: `ρ = π(L_sat − L_p) / (T_v (E0 cos θz T_z + E_down))`; path radiance from the dark object assuming 1% reflectance (eq. 7); `DN_min` = "the darkest DN with at least a thousand pixels for the entire image" (p. 234).
  - DOS1: T_v = T_z = 1, E_down = 0. DOS2: T_z = cos θz (TM1–4). **DOS3: Rayleigh-only transmittances** with `τ_r = 0.008569 λ^−4 (1 + 0.0113 λ^−2 + 0.00013 λ^−4)` (eq. 8), E_down from 6S Rayleigh. DOS4: aerosol transmittance from L_p iteratively (eqs. 9–10, 4–5 iterations).
  - DDV (Liang et al. 1997, ρ1 = ρ7/4, ρ3 = ρ7/2; dense dark vegetation ρ7 ≤ 0.05 & NDVI > 0.1), MDDV (fixed window, 6S), PARA (Wen et al. 1999).
- **Relative: the Ridge Method** (Kennedy & Cohen; p. 235): density plot of date-1 DN vs date-2 DN for **all pixels**, per band; "DN values of all stable features form a 'ridge' with the straight line that passes along the ridge defining the relationship between dates". It "circumvents the difficulty in identifying PIFs"; the ridge "does not change due to minor landuse/landcover changes", but "substantial changes in the images between two dates, such as change in phenology or land use/land cover change, may compromise the utility of the Ridge Method" — the authors **excluded the area of substantial land-use change** when making the density plots, and used only winter images. Reference 10 Dec 1988; Fig. 3: TM1 1988 vs 1989 ridge slope 0.9529, intercept 1.0.

**Evaluation (pp. 239–241):** 7 Landsat-5 TM images (1988–1996), Pearl River Delta, co-registered RMSE < 0.3 px (p. 233). Maximum-likelihood classifier trained on one date and tested on another (4 classification tests + 1 change-detection test on composites with 6 change and 5 stable classes, each run both directions). Also Jeffries–Matusita distance of the same class across dates (Table 7).

## 2. Results
- Table 5 (p. 240) sums of ranks (lower is better): **DOS3 29.5, DOS1 34, Ridge 38.5**, MDDV 48.5, PARA 50, DDV 52, DOS2 53.5, DOS4 59.5, **Raw 84.5 (last)**. "all corrections improved the classification accuracy relative to the uncorrected raw data"; "there is no single consistent 'winner' over all the tests" (p. 240). Ridge "accuracies are not far from DOS3 and DOS1, indicating that it is a viable option".
- Change-detection test 5 accuracies: Raw 52–58%, Ridge 63–76%, DOS3 70–74%, DOS1 70–77% (Table 5).
- Same-image train/test: accuracies almost identical for all methods including raw (Table 6) → correction unnecessary then (p. 241).
- JM distance: DOS3, DOS1 and Ridge bring dates closest (Table 7, p. 242).

## 3. Conclusions as stated (p. 242)
- "only when training data from one time or place are applied in another time or place is atmospheric correction necessary".
- "it is important that the radiometric measurements be set on a common relative scale, but accurate estimation of surface reflectance is not necessary".
- "Contrary to expectations, the recently developed methods … which are more complicated do not lead consistently to improved classification and change detection accuracies relative to the simpler ones."
- "For applications where surface reflectances are not required, simple atmospheric correction algorithms, such as DOS or a relative correction, is recommended."

## 4. Limitations
- Landsat TM, 30 m, horizontally homogeneous atmosphere assumed (no cloud/haze patches); winter images only; no in-situ reflectance, so absolute accuracy not evaluated (p. 238–239, 242).

## 5. How to apply to our pipeline
- **Our setting is the "generalisation" case:** the detector (DINOv2 features / classical change cues) compares a before and an after date, so the dates must be on a common relative scale; absolute reflectance is not needed (supports skipping any reflectance retrieval on 8-bit display data).
- **Our tone curve vs the Ridge Method:** our quantile matching over all clear pixels is closest to the Ridge Method (all pixels, the dense stable ridge drives the fit). The paper supports it as "viable" (3rd of 9) **only with the substantially changed area excluded**; it warns that substantial land-cover change "may compromise" it. A flood is substantial change, so: (i) fit the ridge/tone on pixels outside the flooded area (SN8 flood labels are not usable at test time; use the dark-rise/water prior or IR-MAD no-change weights); (ii) prefer the mode-ridge (density maximum per column) over quantile matching, since the ridge is the stable mode while quantiles shift with any change in class proportions.
- **Arm "ridge":** per band (or grey), 2-D histogram H(before, after) over clear pixels; for each before-DN bin take the after-DN of maximum density (smoothed); fit a straight line through these modes, weighting by bin counts (the paper's ridge line). Compare with `tone_curve` by road-flood F1.
- **Image differencing:** if any downstream cue thresholds a before−after difference with a fixed zero-mean assumption, normalisation is required (p. 233); if thresholds are learned per tile, an offset is absorbed.
- **DOS3 idea for haze:** a dark-object path radiance plus Rayleigh λ^−4 spectral shape ranked best; with RGB display data we cannot compute radiance, but the λ-dependence links to Chavez arm 3-iv.

## 6. Key quotes
- "In many applications involving classification and change detection, atmospheric correction is unnecessary as long as the training data and the data to be classified are in the same relative scale. In other circumstances, corrections are mandatory to put multitemporal data on the same radiometric scale in order to monitor terrestrial surfaces over time." (p. 230)
- "Contrary to expectations, the more complicated algorithms do not necessarily lead to improved performance of classification and change detection. Simple dark object subtraction, with or without the Rayleigh atmosphere correction, or relative atmospheric correction are recommended for classification and change detection applications." (p. 230)
- "substantial changes in the images between two dates, such as change in phenology or land use/land cover change, may compromise the utility of the Ridge Method" (p. 235)
- "for change detection algorithms that assume a zero mean for stable classes in the difference image, radiometric normalization needs to be applied before taking the difference" (p. 233)
