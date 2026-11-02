# Coder handoff: Li, Shen, Cheng, Li & Zhang (2019), Thick Cloud Removal … Stepwise Radiometric Adjustment and Residual Correction (SRARC)

- **Citation:** Li, Z., Shen, H., Cheng, Q., Li, W., & Zhang, L. (2019). *Remote Sensing* 11(16), 1925. https://doi.org/10.3390/rs11161925
- **PDF:** `/Users/jusrogers/Masters/papers/li2019_thick_cloud_removal_stepwise_radiometric_RemoteSens-summary.pdf` (page 1 = AI summary)
- **Source:** MDPI open access (publisher PDF), https://mdpi-res.com/d_attachment/remotesensing/remotesensing-11-01925/article_deploy/remotesensing-11-01925.pdf (the www.mdpi.com /pdf link refused scripted access). Pages "1 of 19" … "19 of 19".
- **Validation:** PDF, 22.4 MB, 19 pages (Read tool error "This PDF has 19 pages"; pdfinfo 19) = 19-page article; title/5 authors/DOI match Crossref; Conclusions (§5) and 47 references present. PASS. Note: the text layer is garbled on pp. 4–15 (overlaid review-draft text); method/results read from the rendered pages.
- **Read:** pp. 1–19 (pp. 5–16 from page images; references skimmed).
- **Prepared by:** Claude (AI), 2026-10-29. Not the same paper as the HRC_WHU/MSCFF cloud-detection paper (Li et al. 2019, ISPRS JPRS), handled by another group.

## 1. Algorithm (§2, pp. 3–8, Fig. 1)
Inputs: cloudy target T, co-registered auxiliary R (other date), cloud(+shadow) masks of both; all bands used.
1. **Mask optimisation (§2.1):** stack TR = {t1..tn, r1..rn}, SLIC superpixels, initial superpixel size **N = 50 px**; take the nearest superpixels around each cloud boundary; new boundary = polyline through superpixel centroids (image moments, eqs. 1–2) and centres of shared superpixel edges, "to ensure that they go through homogeneous areas" (p. 3). Segmenting the stacked pair accounts for land-cover change.
2. **Stepwise local radiometric adjustment (§2.2, eq. 3):** for each cloud pixel and band, `T'(i,j) = σ_Tk/σ_Rk · R(i,j) + µ_Tk − σ_Tk/σ_Rk · µ_Rk`, µ, σ over **valid cloud-free pixels** in window k of side 2r + 1, **r = 80** (Fig. 12a: 20–160 fine; UQI flat). Strategies: fill from boundary to centre by one-pixel erosions; recovered pixels count as clear afterwards; skip a pixel until **≥ 30 valid pixels** in its window; box filters for µ, σ.
3. **Residual correction (§2.3, eqs. 4–6):** `T'' = argmin ∬_Ω |∇T'' − ∇T'|² + λ|T'' − T'|²`, `T''|∂Ω = T*|∂Ω` (target around Ω). With T'' = T' + T̃: `T̃ = argmin ∬ |∇T̃|² + λ|T̃|²` with T̃|∂Ω = (T* − T')|∂Ω — "solving the Laplace equation with boundary condition" (p. 8); with λ > 0 it is a screened Poisson (Helmholtz) equation, so the boundary mismatch decays into Ω instead of spreading over all of it. **λ "empirically set to a small value"** (no number given). **3 iterations** (Fig. 12b).
   - Stated motivation for λ: Pérez's gradient-only cloning propagates "error … from boundaries to the center" (p. 7).

## 2. Data, scale, results
- Simulated: Beijing-2 PMS 4 m (1000 × 1000 × 4, Oct 2017 vs Oct 2016, real land-cover change), Gaofen-2 PMS 8 m (800² × 4, phenology), Sentinel-2 10 m (600² × 4, 10-day gap). Metrics on recovered areas (CC, RMSE, UQI, SSIM) and NL (noise) on the whole image. RMSE values ~0.01–0.35 imply reflectance on a [0,1]-type scale (not stated explicitly).
- Table 1 (p. 8), SRARC best on all metrics in all three: e.g. Fig. 6 scene CC 0.8240 (LLHM 0.7195, MNSPI 0.4551, WLR 0.4912), RMSE 0.0442 (LLHM 0.0625); Fig. 8 scene CC 0.9195 vs 0.8789–0.9083.
- Real: Beijing-2 4 m (2678 × 4567), Sentinel-2 10 m three dates (7000²) with MSCFF masks — visual only.
- Time: 38.7 s for 1000 × 1000 × 4 at 23.44% cloud, MATLAB (p. 15).

## 3. Stated limitations (p. 16)
- "cloud-contaminated areas in the target image cannot be accurately recovered under the condition that abrupt land-cover changes have occurred between the target image and auxiliary image" — only brightness of the auxiliary is corrected.
- Treating recovered pixels as clear "may propagate potential error". Suited to "a relatively short temporal interval and no significant land-cover changes".

## 4. How to apply to our pipeline
- **Do not port step 2's replacement** (filling cloud with adjusted BEFORE pixels): it paints the dry pre-storm road into the flooded after image — exactly the failure the authors state for abrupt land-cover change and our rule forbids (evidence 05).
- **Residual correction → `sn8_cloudedge` arm "N2: screened-Poisson seam"** (pairs with the Pérez handoff): Ω = corrected region (gate + margin); T' = fully corrected after image inside Ω; T* = uncorrected after outside. Solve `(−Δ + λ) T̃ = 0` in Ω with `T̃ = T* − T'` on ∂Ω, then `T'' = T' + T̃`; iterate 3×. Grey-native. λ unspecified: as our choice, set λ = 1/ℓ² so the boundary mismatch decays over a length ℓ (e.g. ℓ = 20–40 px = 10–20 m, comparable to our current 40 px fade) and sweep ℓ ∈ {10, 20, 40, 80} px. In pixel units with a 5-point Laplacian, λ is per px².
  - Applying it to the **correction field** (1 − t or L) instead of the image is cleaner for us (no texture in the field): solve for a correction that equals the data correction inside and 0 outside with a screened-Poisson transition.
- **Mask optimisation → `sn8_cloudsym.change_gate` / `sn8_refhaze.cloud_gate`:** snap the gate edge to superpixel boundaries computed on the stacked (before, after) grey pair, `skimage.segmentation.slic(np.dstack([before, after]), n_segments=H*W/50, channel_axis=-1)`, so the seam runs through homogeneous ground instead of across roofs/roads. Cheap; reduces visible seams at 0.5 m where the gate cuts through objects.
- **Local mean/std matching (eq. 3, r = 80):** a published counterpart to our global quantile tone curve (`sn8_refhaze.tone_curve`) and to REF_WIN = 129 local fits; could be cited for a local tone-matching arm of the dark channel of the before image (not the before pixels themselves).
- **Feasibility:** residual correction and mask optimisation fully feasible on grey 0.5 m, two dates, no SAR/NIR. Paper's resolutions are 4–10 m.

## 5. Key quotes
- "the SRARC method first optimizes the given cloud mask … to ensure that the labeled cloud boundaries go through homogeneous areas of the target image, to ensure a seamless reconstruction" (abstract, p. 1)
- "In the study of Pérez et al. [44], only a gradient constraint was used … In this paper, we additionally introduce the intensity constraint in Equation (4) to better preserve radiometric information" (p. 7)
- "cloud-contaminated areas in the target image cannot be accurately recovered under the condition that abrupt land-cover changes have occurred" (p. 16)
