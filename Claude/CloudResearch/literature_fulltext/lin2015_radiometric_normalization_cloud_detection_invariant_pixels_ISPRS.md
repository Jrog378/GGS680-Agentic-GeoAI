# Coder handoff: Lin, Lin, Lee & Chen (2015), Radiometric normalization and cloud detection of optical satellite images using invariant pixels

- **Citation:** Lin, C.-H., Lin, B.-Y., Lee, K.-Y., & Chen, Y.-C. (2015). *ISPRS Journal of Photogrammetry and Remote Sensing* 106, 107–117. https://doi.org/10.1016/j.isprsjprs.2015.05.003
- **PDF:** `/Users/jusrogers/Masters/papers/lin2015_radiometric_normalization_cloud_detection_invariant_pixels_ISPRS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 5.09 MB; 11 pages (Read tool and pdfinfo) = published range 107–117; page-1 title, authors (Lin, Lin, Lee, Chen; NCKU) and journal 106 (2015) 107–117 match; DOI 10.1016/j.isprsjprs.2015.05.003 printed on p. 107. §5 Conclusions and limitation (p. 116) and References (pp. 116–117) present. PASS. (Supplementary material, online only, not part of the PDF; not read.)
- **Read:** pp. 107–117 in full (Read tool, page images), including Tables 1–3 and Figs. 1–9.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Input: a time series of co-located images, some cloudy. Four steps (Fig. 1, p. 110): invariant pixel determination → radiometric normalisation → cloud-free reference image generation → cloud detection.

1. **Scatterplot, per band, per pair of successive images** (8-bit: 256 × 256 points, p. 111). Remove points on the top and right borders (brightest; "generally belong to the clouds", p. 110).
2. **Pixel similarity** (eqs. 7–10, p. 110), using the multi-band vectors x^a, x^b of a pixel on the two dates:
   - `S_ED = sqrt(Σ_i (x_i^a − x_i^b)²) / Max_ED` (normalised Euclidean distance);
   - `S_SA = arccos( Σ x^a x^b / sqrt(Σ(x^a)² Σ(x^b)²) )` (spectral angle);
   - `S_SC = ½(1 − corr(x^a, x^b))` (spectral correlation across bands);
   - `S(x) = 1 − (S_ED + S_SA + S_SC)/3` ∈ [0, 1].
3. **Point weight** (p. 110–111): density of scatterplot point p = Σ of S over the pixels that fall on p; enhanced as `w = C(w) = ∫0^w f(w) dw` (eq. 11), i.e. replaced by its CDF value.
4. **Weighted PCA** on the scatterplot points (eq. 12): weighted covariance `C(P) = Σ w_pk (p_k − p̄)(p_k − p̄)ᵀ / Σ w_pk`, weighted mean p̄; first eigenvector = major axis. Needs no cloud/water mask and no D_max (difference) constraint.
5. **Invariant pixels** (p. 111): pixels within ±d of the major axis. d is probed iteratively (Du 2002 quality control) so that the candidates' correlation > **0.75** → "invariant pixels" for reference composition; tighter d so correlation > **0.9** → PIFs for normalisation. "The thresholds 0.75 and 0.9 are empirical values, and these two thresholds are identical in all experiments".
6. **Normalisation** (eqs. 1–3, p. 108, Du et al. 2002): `σ_ref = max_k σ_Pk`, `P̄_ref = max_k((σ_ref/σ_Pk)·P̄_k)`; `α_k = σ_ref/σ_Pk`, `β_k = P̄_ref − α_k·P̄_k` from the PIF means/SDs. Whole sequence put on one scale.
7. **Reference image per cloudy image I_D** (eqs. 13–14, p. 111): `I_D^ref(i,j) = Σ_K δ_K(i,j)·IP_K(i,j) / Σ_K δ_K(i,j)` over the invariant pixels of all dates K, with `δ_K = Norm(1/TI(D,K)) + Norm(1/(TC_K(i,j) + δ))`, TI = days between D and K, TC = |IP_K(i,j) − mean over time of IP(i,j)|, δ = 0.0001. Empty pixels: bilinear interpolation.
8. **Cloud test** (Hagolle et al. 2010, eqs. 4–6 p. 108–109; simplified eq. 15 p. 112): `ToA_blue(I_D) − ToA_blue(I_D^ref) > 0.03` (reference composed for the same date, so the (D − D_ref)/30 term drops). Hagolle's extra checks: red/blue rise ratio > 1.5 → re-mark as clear (cropping/drying fields); `(ToA_green − ToA_SWIR)/(ToA_green + ToA_SWIR) > 0.6` → snow/ice. Post-processing (dilation, erosion, hole filling) **excluded** (p. 112).

## 2. Inputs, outputs, data needs
- Landsat-7 ETM+ L1T, bands blue, green, red, NIR, SWIR 1.55–1.75 µm (thermal, other IR, pan excluded) (p. 109).
- Sites (Table 1): California cropland 6 images (1999–2001); Taiwan mountain/ocean 20 images (~25% cloud); Tibet snow/cloud 24 images (~10% snow, ~15% cloud). 50 images total (p. 112).
- Needs **a time series** (many dates) for the reference composite; cloud test in **ToA reflectance**.

## 3. Quantitative results
- Major-axis accuracy (Table 2, p. 114, Tibet pair, against manually selected axes): weighted PCA RMSE **2.55**; best competitor (de Carvalho Júnior 2013 pixel-similarity PIFs) 6.40 (S_SA, T = 0.2) / 6.87 (S_ED, T = 0.1), worst up to 50.44. Standard PCA with D_max = 50, 100, 150 gave visibly wrong axes (Fig. 7).
- Cloud detection vs manual truth (Table 3, p. 116, Tibet sub-areas, 24 images): F-measure **Area I (significant land-cover change) 87.9 / 87.2 / 81.0**, Area II (near-constant cover) **92.0 / 91.2 / 90.9** for composed weighted-invariant reference / nearest-invariant reference / existing cloud-free image. The abstract's "improved by 1.1–6.9%" = 92.0 − 90.9 and 87.9 − 81.0 (percentage points, vs an existing cloud-free reference). Accuracy > 99% in Area II for all three.
- Area I failure of the existing reference: it had snow the target lacked → false cloud (p. 114–115).

## 4. Stated limitations
- "our method is limited when images are almost covered by clouds. In this case, only a few invariant pixels can be extracted" (p. 116); remedy: more images of the same place.
- d thresholds 0.75/0.9 empirical (p. 111). Reference composition relies on many dates.

## 5. How to apply to our pipeline
- **Two-date reality:** we have one clear before and one after date, so steps 7 (time-weighted composite) collapse to "the before image is the reference". What transfers is steps 1–6: weighted-PCA invariant-pixel selection and Du-style PIF normalisation, before our dark-rise cloud test.
- **Arm "wPCA tone":** for each tile (or scene), per band of RGB (or grey):
  1. 2-D histogram H(b, a) (256 × 256) of before b vs after a over non-gated pixels; zero the top row/right column (saturation/cloud).
  2. Per pixel S = 1 − (S_ED + S_SA + S_SC)/3 from the RGB vectors (needs ≥ 2 bands for S_SA/S_SC to mean anything; on grey use S_ED only). Point weight = Σ S per histogram cell → replace by its empirical CDF.
  3. Weighted 2×2 covariance of occupied cells → major axis.
  4. Grow d from small until corr(candidates) ≥ 0.9 fails, keep the largest d that passes → PIFs; gain = σ_b/σ_a, offset = μ_b − gain·μ_a on PIFs.
  5. Compare against our quantile curve (`tone_curve`) by road-flood F1 and by the residual on clear tiles.
- **Cloud test:** the paper's test is a blue-band reflectance rise (> 0.03 ToA) after normalisation — a two-date "rise against a clear reference", like our dark-rise, but on blue reflectance, not the dark channel. On 8-bit RGB, 0.03 ToA has no direct DN equivalent; refit.
- **Flood caveat:** the method's weighting favours the dense majority of the scatterplot. Where flood dominates a tile, the majority is changed ground (same failure mode as IR-MAD; Canty & Nielsen 2008 p. 1034). Use scene-level fits or a minimum invariant count.

## 6. Key quotes
- "Although this strategy can effectively identify cloud pixels, the detection accuracy mainly relies on the successful radiometric correction/normalization and reference image quality." (p. 107, about previous methods)
- "Relative radiometric normalization generally suffers from cloud covers, while multi-temporal cloud detection is sensitive to the radiometric normalization quality." (p. 107)
- "The thresholds 0.75 and 0.9 are empirical values, and these two thresholds are identical in all experiments of this study." (p. 111)
- "the proposed method for the major axis determination is a parameter-less process" (p. 113)
- "our method is limited when images are almost covered by clouds. In this case, only a few invariant pixels can be extracted" (p. 116)
