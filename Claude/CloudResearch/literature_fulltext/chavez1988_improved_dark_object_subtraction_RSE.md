# Coder handoff: Chavez (1988), An improved dark-object subtraction technique for atmospheric scattering correction of multispectral data

- **Citation:** Chavez, P. S., Jr. (1988). *Remote Sensing of Environment* 24(3), 459–479. https://doi.org/10.1016/0034-4257(88)90019-3
- **PDF:** `/Users/jusrogers/Masters/papers/chavez1988_improved_dark_object_subtraction_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 1.50 MB; 21 pages (Read tool and pdfinfo) = published range 459–479; page-1 title, author (Chavez, USGS Flagstaff) and "Remote Sensing of Environment 24:459-479 (1988)" match; PII 0034-4257(88)90019-3 in the PDF metadata matches the DOI. Summary (p. 478) and References (pp. 478–479, ending "Received 23 April 1986; revised 20 November 1987") present. PASS. Pp. 469–470 are the colour plate (Fig. 3a–d).
- **Read:** pp. 459–479 in full (Read tool, page images), including Tables 1–5 and Figs. 1–3.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Scope: additive scattering (path radiance, "haze") only; absorption is multiplicative and "not considered in this paper" (pp. 459–460). Like the standard method, a **constant haze value per band over the entire image** ("a first-order correction", p. 460).

1. **Starting haze value (SHV)** from the histogram of one visible band ("the one that shows more clearly the distinct increase in the number of pixels present at the lower end of the histogram", p. 471): the DN where the count rises sharply (Fig. 2; TM bands 1–4 of the Arizona scene → 40, 13, 12, 8, p. 466). Use the whole image or a large part; "If histograms of very localized areas are used, a real minimum or dark-object may not be found, and the DN value selected will overcorrect" (p. 466).
2. **Choose a relative scattering model** (power law λ^−k) by the SHV amplitude (p. 467, Table 5 p. 477, from > 25 TM scenes; TM1 SHV): very clear λ^−4 (≤ 55), clear λ^−2 (56–75), moderate λ^−1 (76–95), hazy λ^−0.7 (96–115), very hazy λ^−0.5 (> 115). Range of the exponent: "this relationship can vary from λ^0 to λ^−4, with λ^0 representing complete scattering (e.g., complete cloud cover)" (p. 466); a real clear atmosphere "seems to follow more of a λ^−2 to λ^−0.7 relationship" (p. 466).
3. **Predict other bands' haze in radiance-proportional units** (Table 2 p. 472): factor_i = (λ_i/λ_start)^−k using band-mean wavelengths (TM1 0.485, TM2 0.560, TM3 0.660, TM4 0.830, TM5 1.650, TM7 2.215 µm; Table 1 p. 468). Offset-correct the SHV first: `SHV' = SHV − OFFSET_start`.
   `HAZE_i = SHV' × factor_i`.
4. **Gain/offset normalisation back to DN** (eqs. 1–5, pp. 471–474): sensor `DN_i = GAIN_i·Rad_i + OFFSET_i` (eq. 1); `DN(HAZE_i) = NORM_i·HAZE_i + OFFSET_i` (eq. 5) with `NORM_i = GAIN_i / GAIN_start` (Table 3). Worked example (p. 474–475): TM1 SHV 40, offset 2.58 → 37.42; very-clear factor TM2 0.563 → 21.067; ×NORM 0.51 + offset 2.44 → **13.184 DN**.
5. **Subtract** DN(HAZE_i) from every pixel of band i.
6. **Checks:** the SHV "must not overpredict the values for the other bands; if this occurs, either a smaller starting haze value is required or selection of a starting haze DN value from another band may be necessary" (p. 471). For TM 5 and 7 the predicted DNs were too high (over-correction); "a haze DN value of zero, or one DN at the most, can be used for Bands 5 and 7" (p. 476).

## 2. Inputs, outputs, data needs
- One image, its DN histograms, band-centre wavelengths, and the sensor's per-band GAIN/OFFSET (Table 3: Landsat-4 TM and MSS).
- Output: per-band haze DN to subtract.

## 3. Results
- Arizona TM (Table 4A): old/new haze DN for bands 1, 2, 3, 4, 5, 7 = 40, 13, 12, 8, 5, 2 vs 40, 13.2, 8.9, 4.9, 16.7, 3.3 (very clear model). Close because a deep canyon gave a good dark object (p. 475–476).
- Tunisia MSS (Table 4B–C): old 13, 9, 21, 16 vs new 13, 8.6, 6.9, 0.4 (very clear); old 30, 50, 50, 40 vs new 30, 34.4, 43.6, 6.4 (hazy).
- Note: "because of the gain differences it is possible for the final haze value for a longer wavelength band (MSS Band 6) to have a larger value than a shorter wavelength band (MSS Band 5)" (Table 4 note, p. 475; also Table 5 note p. 477).
- Evaluation is **visual** only: calibrated natural-colour composites of central Saudi Arabia compared with field photographs (pp. 468–470). No quantitative accuracy.

## 4. Stated limitations
- Constant haze per band over the image (p. 460).
- Over-correction in TM 5/7 unexplained (p. 476).
- The five discrete models cause jumps at class boundaries; a continuously variable exponent would remove them (p. 477–478).
- "Research is currently under way to establish a better relationship between the starting haze value and the type of atmospheric conditions" (p. 478).

## 5. How to apply to our pipeline
- **Arm 3-iv (band-linked airlight):** the published constraint is a **power law in wavelength applied in radiance (or reflectance) units**, then mapped to DN by each band's gain/offset. In DN the ordering blue > green > red is **not guaranteed** (gain differences can invert it; p. 475). Our 8-bit display RGB has unknown per-band gains and a possibly non-linear stretch, so:
  1. estimate the airlight on the clearest channel (blue) from the after-date dark-object (or our dark-channel A);
  2. predict green/red airlight as `A_g = A_b·(λ_g/λ_b)^−k`, `A_r = A_b·(λ_r/λ_b)^−k` with k ∈ {0, 0.5, 0.7, 1, 2} (λ for WorldView-class RGB ≈ 0.48, 0.545, 0.66 µm), assuming equal gains (unknown — flag it);
  3. pick k by the SHV amplitude (paper's rule) or, better for us, by minimising the residual against the before date on invariant pixels; k = 0 is a grey airlight (our current single A), which the paper calls the complete-cloud case.
- **Thin cloud vs haze:** the paper places thick cloud at λ^0 (no wavelength dependence) and haze at λ^−0.5 to λ^−2. Our thin cloud sits between, so a single grey A is the cloud end-member, not wrong for cloud, but wrong for haze.
- **Local vs global:** the paper's dark-object value is image-wide and warns that local histograms over-correct. Our per-pixel/local transmission (He et al.) is beyond this paper.
- **Ma et al. 2022 (claim_checks_C #6):** their `t_i = t_1^{(λ_1/λ_i)^γ}` with γ ∈ [0, 4] cites exactly this λ^0 to λ^−4 range (p. 466).

## 6. Key quotes
- "atmospheric scattering is highly wavelength-dependent in the visible part of the electromagnetic spectrum and the scattering values are correlated with each other" (p. 459)
- "this relationship can vary from λ^0 to λ^−4, with λ^0 representing complete scattering (e.g., complete cloud cover)" (p. 466)
- "This type of correction involves subtracting a constant DN value from the entire digital image. This assumes a constant haze value throughout the entire image, which is often not the case." (p. 460)
- "If histograms of very localized areas are used, a real minimum or dark-object may not be found, and the DN value selected will overcorrect for atmospheric haze." (p. 466)
- "because of the gain differences it is possible for the final haze value for a longer wavelength band (MSS Band 6) to have a larger value than a shorter wavelength band (MSS Band 5)" (p. 475)
