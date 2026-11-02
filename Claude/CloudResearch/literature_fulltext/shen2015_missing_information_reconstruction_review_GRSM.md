# Coder handoff: Shen, Li, Cheng et al. (2015), Missing Information Reconstruction of Remote Sensing Data: A Technical Review

- **Citation:** Shen, H., Li, X., Cheng, Q., Zeng, C., Yang, G., Li, H., & Zhang, L. (2015). *IEEE Geoscience and Remote Sensing Magazine* 3(3), 61–85. https://doi.org/10.1109/MGRS.2015.2441912
- **PDF:** `/Users/jusrogers/Masters/papers/shen2015_missing_information_reconstruction_review_GRSM-summary.pdf` (page 1 = AI summary)
- **Source:** author manuscript (header "GRSM-2014-00034"), Wuhan University SENDIMAGE site, https://sendimage.whu.edu.cn/wp-content/uploads/37g2015_Missing-Information-Reconstruction-of-Remote-Sensing-Data.pdf . Manuscript pagination 1–22, not the journal's 61–85. Page numbers below are the manuscript's.
- **Validation:** `file` = PDF; 2.7 MB; 22 pages (Read tool and pdfinfo agree); title and all seven authors match Crossref; DOI from Crossref (the manuscript does not print it); Conclusion (§VIII), acknowledgments, ~100 references and biographies present. 22 manuscript pages vs 25 published pages: accepted-manuscript single-file layout, not truncation (the text runs through §VIII-E and the reference list). PASS (accepted-manuscript pagination noted).
- **Read:** pp. 1–19 in full (all sections, figure captions, Tables I–III); references and biographies pp. 19–22 skimmed (cited refs [2], [43], [45], [62], [64] looked up).
- **Prepared by:** Claude (AI), 2026-10-29.
- **Type:** review, not a single method. Sections below keep what we can use.

## 1. Problem statement and taxonomy (§I–§II, pp. 1–3)
- Observed data J = M·I with M a diagonal 0/1 mask; Ω = S ∪ E (missing region S, existing region E). Goal: estimate I on S from E, "visually natural, but also in accordance with the physical meaning" (p. 2).
- Four categories by the source of the complementary information (p. 1, p. 3):
  1. **spatial-based**: interpolation/kriging, propagated diffusion (PDE), variation-based (regularised: Laplacian, TV, Huber-Markov, nonlocal TV), exemplar-based (patch copying);
  2. **spectral-based**: model a damaged band from intact bands (MODIS band 6 from 7, or from 1–7);
  3. **temporal-based**: replacement (direct, or indirect with a correction f₂), temporal filters (BISE, Savitzky-Golay, asymmetric Gaussian, double logistic, HANTS, wavelets), temporal learning (compressed sensing, dictionary learning, SOM);
  4. **hybrid**: spatio-temporal (successive, or "spatial completion with temporal guidance", STMRF), spectral-temporal (sparse representation).

## 2. Equations worth having
- Interpolation (eq. 1): Î(x₀) = Σᵢ wᵢ I(xᵢ). Kriging weights minimise σ_E² (eq. 2).
- Linear diffusion (eqs. 3–4): ∂I/∂t₀ = ΔI; "introduces a lot of blurring" (p. 3).
- Variational inpainting (eq. 8): Î = argmin_I ‖MI − J‖_q^q + λ U(I). U = Laplacian ‖∇²I‖² (eq. 9, smooth, blurs edges), TV ‖∇I‖ (eq. 10, sharp edges but "unconnected when the width of the missing gap is larger than that of the object", p. 4), Huber-Markov (eqs. 11–13, threshold μ between quadratic and linear), nonlocal TV (eqs. 14–16, weight w(x,y) = exp(−G∗‖I(x+·) − I(y+·)‖²/h²)).
- Indirect temporal replacement (eq. 20): Î_T0(x₀) = f₂(I_T1(x₀), …, I_Ti(x₀)); the correction is fitted "according to the whole of the remaining data (region E)" or, more locally, on the neighbourhood of the missing region (p. 10).
- Sparse spectral-temporal (eq. 25): argmin ‖MX − Y‖² + Σ μᵢⱼ‖αᵢⱼ‖₀ + Σ γᵢⱼ‖Dαᵢⱼ − PᵢⱼX‖².

## 3. Evaluation protocols (directly reusable)
- **Simulated loss on a real clear image (§VII-B-2, p. 17):** "An original image is first degraded by removing some pixels, and then is used as the reference for the reconstructed result." Indicators: SSIM, MSE, MRE, MAE, CC, PSNR, SA, UIQI. Every experiment in the review uses this (Fig. 8 dead lines on Landsat TM; Fig. 13 MODIS; Fig. 15 SLC-off simulated from a March 2002 ETM+ image; Fig. 23 cloud simulated on a MODIS image; Fig. 25 MODIS block removed).
- **Real-cloud examples are judged only visually** (Fig. 9, Fig. 16): no truth exists under real cloud.
- **Task-oriented evaluation (p. 17):** measure the reconstruction by its effect on the downstream task (classification, vegetation change monitoring). "The authors in [43] firstly generated the error map to convey the reconstruction reliability to the end-users" ([43] = Benabdelkader & Melgani, "Contextual spatiospectral postreconstruction of cloud-contaminated images", IEEE GRSL).
- **Mask rules (§VII-A, p. 17):** "omitting is a fatal failure for reconstruction because the corresponding locations cannot be reconstructed. Thus … it is allowed that the good location is detected as missing location, but omitting the missing location cannot be allowed absolutely"; "the usual way of doing is to appropriately dilate the determination result of missing location". Cloud detection "can be over 90% in most situations" (no metric or source given for this figure).

## 4. Quantitative results we could compare to
- Dead lines on Landsat TM (Table I, p. 6): corrupted 19.667 dB / SSIM 0.730; kriging 38.372 / 0.961; BSCB diffusion 41.375 / 0.978; **TV 41.961 / 0.983**; exemplar 38.851 / 0.967.
- Large cloud (Fig. 9, p. 6): exemplar copying looks best; interpolation, diffusion and variational methods blur. No numbers. "Regardless of the accuracy, the exemplar-based method achieves a good result" (p. 6), and §VIII-D: exemplar output is "low-accuracy and even false reconstruction" acceptable only where a false fill is allowed (p. 18).
- MODIS band 6 (Table II, p. 9): MAE 0.18420 → 0.00212 (RMEMR), PSNR 13.06 → 49.11 dB.
- Simulated MODIS cloud with a reference from a different season (Fig. 23, p. 15): CC spatial 0.70263, temporal 0.83804, spatio-temporal hybrid 0.86527. Temporal fill left the river "still different" from the rest of the river (p. 15).
- Sparse spectral vs temporal (Table III, p. 16): MRE 2.73% spectral, 2.83% temporal, 2.35% joint; "The land-surface features can change in the multitemporal data, which results in the worst reconstruction result when using the temporal-based method" (p. 16).

## 5. What fails under land-cover change (the part most relevant to us)
- "For the temporal-based methods, the time interval is a double-edged sword … if the time interval is too long, the land cover can vary so greatly that the correlation is destroyed" (p. 9).
- Temporal differences: "1) … observation conditions; 2) … regular changes … (e.g., phenological changes); and 3) … abrupt transformation of geographical objects (e.g., new buildings …). Generally speaking, the temporal-based methods are appropriate for the first two kinds" (p. 9). A flood is the third kind.
- Direct replacement "cannot work on most occasions" because of atmosphere, sun angle and look angle differences (p. 9). Indirect replacement: "because of the errors of registration and the abrupt changes in land cover, the temporal replacement may result in an aliasing phenomenon" (p. 10).
- LLHM (USGS EROS SLC-off histogram matching in a moving window): "can perform well in most regions if the input scenes are of high quality. Nevertheless, it tends to be more sensitive with regard to data selection, and has difficulty with heterogeneous landscapes where the features are smaller than the local moving window size" (p. 10). In Fig. 15(e) LLHM leaves "obvious artifacts … near the edge of the river … a simple linear algorithm using all the common pixels is unsatisfactory" (p. 10).
- Conclusion: temporal methods "are almost custom-made techniques for cloud cover, but they are sensitive to land-cover changes, especially abrupt changes" (p. 17).

## 6. Stated limitations / scope
- "the missing data means that the objective information is completely obscured or not observed … another kind … partially missing, such as shadow, thin cloud, and haze … it is not discussed in this paper" (§VIII-E, p. 18). The review therefore says nothing about de-hazing; our two-date haze correction is outside its scope.
- Spectral methods "cannot be used with thick cloud cover" (p. 17); spatial methods are "ineffective in reconstructing large-area missing information" (p. 17).

## 7. How to apply to our pipeline
- **Abstain under opaque cloud (`sn8_refhaze` / `sn8_cloudsym`, T_MIN = 0.2 → "cannot assess"):** the review's taxonomy backs it. Our only temporal source is the before date and the change between dates is abrupt (category 3, p. 9), the class the authors say temporal methods do not handle. Filling from the before date is the "direct replacement" they say "cannot work on most occasions" even without change. Keep abstaining; do not add a before-date fill arm.
- **Cloud gate dilation (`sn8_refhaze.cloud_gate`, `sn8_cloudsym.change_gate`, `sn8_cloudspot` gate):** the paper's rule is asymmetric: a missed cloud pixel is fatal, a false one is tolerable, so dilate the mask. Our 20 m linear fade past the gate is a soft version of this. Arm to test: dilate the binary "cannot assess" mask by a few metres (e.g. 5, 10, 20 m) before road scoring and measure roads lost vs ring residual (sn8_cloudedge.ring_measures). This is a direct, cheap arm.
- **Tone curve (`sn8_refhaze.tone_curve`, quantile matching on clear pixels):** this is the paper's "indirect replacement" correction fitted on region E (p. 10); LLHM shows the failure mode when one global or windowed linear fit runs over heterogeneous ground ("artifacts near the edge of the river"). Supports the existing concern that our curve uses flood-changed clear pixels: fit on invariant pixels, or exclude dark-water pixels from the fit.
- **Evaluation:** the simulated-loss protocol (§VII-B-2) is what `sn8_refhaze.synthetic_haze` / `haze_recovery` already does for haze. For any new arm, report PSNR, SSIM and MAE inside the pasted mask on clear tiles, plus the task-oriented score (road attribute agreement on the SpaceNet 8 labels), as the paper recommends both.
- **Reliability map:** the review points to an error map conveying reliability to end users ([43], p. 17). Emit a per-pixel reliability layer with the corrected after image (for example t itself, the fade weight, and a flag for "corrected" vs "observed" vs "cannot assess") so road decisions can weigh corrected pixels. No formula is given in this review; [43] would be the source (not read).
- **Spatial inpainting for small gaps only:** TV is best on narrow gaps (Table I) and blurs large ones; exemplar copying invents. If we ever fill thin seams (e.g. the ring), TV on gaps narrower than the road width is the defensible choice; never inpaint cloud cores that cover roads.

## 8. Feasibility with our data
- **We have no SAR, no NIR or other bands (RGB uint8 used as grey), and no other dates beyond the single clear pre-storm image; the post-storm date is the target.** Spectral methods: not applicable (no redundant intact band under cloud; all RGB bands are clouded together). Temporal and hybrid methods: need a near-date reference with no abrupt change; ours differs by the flood, so they would copy pre-flood ground. Multisource fusion (§VIII-B, SAR): not available.
- **Usable now:** the mask-dilation rule, the simulated-loss evaluation protocol and indicators, the task-oriented evaluation idea, the reliability-map idea, and TV inpainting for narrow seams. All work on 0.5 m greyscale with no extra data.

## 9. Key quotes
- "the temporal-based methods are appropriate for the first two kinds of temporal differences" (p. 9)
- "because of the errors of registration and the abrupt changes in land cover, the temporal replacement may result in an aliasing phenomenon" (p. 10)
- "omitting the missing location cannot be allowed absolutely … the usual way of doing is to appropriately dilate the determination result of missing location" (p. 17)
- "they are sensitive to land-cover changes, especially abrupt changes" (p. 17)
- "the missing data means that the objective information is completely obscured or not observed … partially missing, such as shadow, thin cloud, and haze" (p. 18)
