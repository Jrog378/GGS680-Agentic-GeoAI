# Coder handoff: Byun & Han (2018), Relative radiometric normalization of bitemporal very high-resolution satellite images for flood change detection

- **Citation:** Byun, Y., & Han, D. (2018). Relative radiometric normalization of bitemporal very high-resolution satellite images for flood change detection. *Journal of Applied Remote Sensing* 12(2), 026021. https://doi.org/10.1117/1.JRS.12.026021 (CC BY 3.0)
- **PDF:** `/Users/jusrogers/Masters/papers/byun2018_relative_radiometric_normalization_flood_change_detection_JARS-summary.pdf` (page 1 = AI summary; then the SPIE cover; paper pages follow)
- **Source:** publisher PDF (SPIE Digital Library) downloaded through Justin's GMU session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out). Supersedes claim_checks_C, which only had the abstract (bot wall).
- **Validation:** real PDF (`file`: PDF document; 8.2 MB). Read tool and pdfinfo: 20 pages = SPIE cover sheet + article pages 026021-1 to 026021-19 (Crossref: pages 1–19). Title, both authors, J. Appl. Remote Sens. 12(2) 026021 and the DOI match on the cover and p. 1. §5 Conclusions (pp. 15–17) and references 1–39 (pp. 17–19) present. PASS.
- **Read:** PDF pp. 1–20 in full (page images), all tables and figures.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's (026021-n → p. n). Venue below JIF 4: context only, not for slides.

## 1. Algorithm, step by step (§3, pp. 4–7)
Six steps (pp. 4–5): (1) NDWI difference before/after; (2) weights from eq. 6 using the NDWI difference and post-flood NIR; (3) weighted means and covariances (eqs. 7–8); (4) CCA → MAD variates; (5) PIFs = pixels with no-change probability > t; (6) orthogonal regression, band by band, of the after image onto the before image on the PIFs.

1. **NDWI** (McFeeters; eq. 3, p. 6): `NDWI = (G − NIR) / (G + NIR)`; d = NDWI_after − NDWI_before (sign not stated; enters squared).
2. **Weight** (eqs. 4–6, p. 6): `ω(d, r) = exp(−d² / (2σ)) × 1 / (1 + exp(−k (r − r0)))`, with r = post-flood NIR reflectance, r0 = **third quartile** of post-flood NIR. **σ = 0.0001, k = 3**, tuned on Chad and reused unchanged on Sudan (p. 6). Note the printed Gaussian uses 2σ, not 2σ². Effect: low weight where NDWI changed or where post-flood NIR is low (water).
3. **Weighted statistics** (eqs. 7–8, p. 7): `F̄_i = Σ ω_j F_ji / Σ ω_j`; `S_ik = Σω / ((Σω)² − Σω²) · Σ ω_j (F_ji − F̄_i)(F_jk − F̄_k)`. All ω = 1 → ordinary MAD.
4. **MAD** (eqs. 1–2, p. 5): CCA, `M = aᵀF − bᵀG`, generalised eigenproblems as in Nielsen/Canty.
5. **PIFs** (eqs. 9–10, p. 7): `Z = Σ (M_i/σ_Mi)²`, `σ²_Mi = 2(1 − ρ_{k−i+1})`, `Pr_no-change = 1 − P_χ²;K(z)`, **t = 0.99** (the paper says "the same threshold as in the original MAD designed by Nielsen").
6. **Not iterative.** The weights come from NDWI/NIR once; the proposed method "is computationally efficient since it does not require an iterative procedure" (p. 14). IR-MAD is the comparison.
7. **Normalisation:** orthogonal linear regression per band on the PIFs (p. 7); before = reference, after = target (p. 9).
8. **QC:** paired t-test (means) and F-test (variances) on hold-out PIFs not used in the fit, significance 0.05 (p. 10).
9. **Change detection on the normalised pair:** (a) MAD-based: no change within ±2σ_Mi in every component, union of changes (pp. 11–12); (b) CVA magnitude thresholded by EM + Bayes rule (pp. 12–13).

## 2. Inputs, outputs, data needs
- **KOMPSAT-2**, 10-bit, PAN 1 m + 4 MS bands at 4 m (blue, green, red, **NIR**), Level 1R, Gram–Schmidt pan-sharpened to 1 m, manual co-registration RMSE 0.5 px on 10 checkpoints (Table 1, p. 3).
- **Chad (N'Djamena):** before 22 Jun 2010, after 14 Oct 2012 (off-nadir 2° vs 24°). **Sudan (Atbara River):** before 9 Jan 2012, after 9 Aug 2013 (−2° vs −19°). The before/after gaps are **2.3 and 1.6 years**; the authors note short gaps were not available (p. 3).
- Study windows: 250,000 px (Chad) and 1,000,000 px (Sudan) (Tables 6–7).
- Reference: hand-digitised "visually salient flooded area along the river" only; urban changes not labelled (p. 13, Fig. 10).

## 3. Quantitative results to compare against
- **PIFs:** IR-MAD 150 (Chad) / 496 (Sudan), mostly inside the flooded area; proposed 143 / 1,080, mostly in non-flooded homogeneous areas (Fig. 3, p. 8).
- **Hold-out QC** (Tables 2–5, pp. 10–12): Chad, 44 px — IR-MAD fails every band (P = 0.000 means and variances; band 4 mean P = 0.019); proposed passes all (means P 0.24–0.48, variances 0.26–0.81). Sudan, 326 px — IR-MAD fails all; proposed passes means (P 0.10–0.90) and variances in bands 1–3 (0.11–0.29) but **fails the band-4 variance test (P = 0.042)**.
- **Flood change detection, overall accuracy** (Tables 6–7, pp. 15–16):

| Detector | Site | IR-MAD | Proposed | Gain (points) |
|---|---|---|---|---|
| CVA + EM | Chad | 81.79% | 83.62% | +1.83 |
| CVA + EM | Sudan | 63.25% | 75.91% | +12.66 |
| MAD ±2σ | Chad | 51.01% | 51.04% | +0.03 |
| MAD ±2σ | Sudan | 70.75% | 76.20% | +5.45 |

  The abstract's "1.8% and 12.6%" are the **CVA** rows, in **percentage points of overall accuracy** (p. 17 confirms "Using the CVA-based change-detection method"). The MAD detector barely changes at Chad and is near chance there (51%; flood omission 96.5–98.7%).
- Trade-off hidden in OA: at Chad (CVA) the proposed method **misses more flood** (flood omission 13.3% vs 10.2%) while cutting commission (23.18% vs 27.2%). At Sudan (CVA) flood omission rises 5.95% → 16.47% while commission falls 61.62% → 50.84%.
- No significance test on the OA differences; one image pair per site; parameters tuned on Chad.

## 4. Stated limitations (pp. 14–15)
- "focuses only on flood-related issues and is sensitive to the NIR band because it is designed based on the NIR band of the post-flood image".
- Both change detectors over-detect (p. 13). Future work: VHR SAR.

## 5. How to apply to our pipeline (Maxar RGB 0.5 m, no NIR)
- **NIR-dependent as published.** Both weight terms need NIR (NDWI and the post-flood NIR logistic). We have RGB only, so the method cannot run as is (confirms our earlier note).
- **What carries over: the idea of down-weighting likely-flood pixels *before* the CCA/fit.** This is exactly the hazard flagged in the Canty 2008 handoff (IR-MAD converges to the majority; in a flood scene the majority may be water). An RGB substitute, our adaptation:
  - Replace NDWI-difference with a **before-date** water/darkening cue we already have, e.g. the change in an RGB water index or our "dark-rise" sign: `d = (dark_after − dark_before)`; `ω1 = exp(−d²/(2s²))` (use σ², not the paper's σ).
  - Replace the post-flood NIR logistic with a logistic on **after-date brightness** or on a non-water probability, r0 = 75th percentile as in the paper: `ω2 = 1/(1+exp(−k(r−r0)))`.
  - Feed ω into weighted mean/covariance (eqs. 7–8; numpy `np.cov(..., aweights=w)` gives the same unbiased weighted estimator), run one CCA, take PIFs at Pr > 0.99, fit orthogonal regression per band, QC with paired t and F on held-out PIFs (`scipy.stats.ttest_rel`, F via `scipy.stats.f`).
  - Arm: compare against our IR-MAD tone arm (Canty handoff) on the same tiles; report flood omission and commission separately, not only OA (the paper's own tables show OA hides an omission increase).
- **Threshold:** use t = 0.99 when copying this paper, 0.95 when copying Canty 2008; say which.
- **Evidence weight:** JARS (JIF below 4), two sites, hand-drawn references limited to the salient river flood, before/after 1.6–2.3 years apart. Context only.

## 6. Key quotes
- "these methods lead to an incorrect projection of the MAD variates in data sets with a large number of pixels in the scene that change over time, such as flood disaster data sets. The problem arises because the covariance matrix is greatly influenced by the image pixels affected by the flood" (p. 5).
- "In this study, the decision threshold t was set to 0.99" (p. 7).
- "the proposed method produced a better result than the IR-MAD method with an OA of 83.62% and 75.91%, respectively, for each site. The OA of the proposed method is higher by 1.8% and 12.6% for the two sites than the OA of the IR-MAD method" (p. 14).
- "Our method is computationally efficient since it does not require an iterative procedure. However, there are disadvantages in that it focuses only on flood-related issues and is sensitive to the NIR band" (pp. 14–15).
