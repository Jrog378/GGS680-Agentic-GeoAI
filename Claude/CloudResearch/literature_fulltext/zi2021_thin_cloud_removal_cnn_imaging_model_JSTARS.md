# Coder handoff: Zi et al. (2021), Thin Cloud Removal for Multispectral Remote Sensing Images Using CNNs Combined With an Imaging Model

- **Citation:** Zi, Y., Xie, F., Zhang, N., Jiang, Z., Zhu, W., & Zhang, H. (2021). Thin cloud removal for multispectral remote sensing images using convolutional neural networks combined with an imaging model. *IEEE JSTARS* 14, 3811–3823. https://doi.org/10.1109/JSTARS.2021.3068166
- **PDF:** `/Users/jusrogers/Masters/papers/zi2021_thin_cloud_removal_cnn_imaging_model_JSTARS-summary.pdf` (page 1 = AI summary)
- **Source:** publisher open-access PDF (CC BY 4.0), https://ieeexplore.ieee.org/ielx7/4609443/9314330/09384224.pdf (OpenAlex oa_url). Journal pagination.
- **Validation:** PDF (8.3 MB), 13 pages (Read tool; pdfinfo 13; `file` misreported 10) = 3811–3823; title, six authors (Beihang University; Shanghai Aerospace Electronic Technology Institute), volume and DOI match Crossref; Conclusion (§VI) and references present. PASS.
- **Read:** pp. 3811–3823 in full; Tables II–IV read from page images (pp. 3818, 3821); references and biographies skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.
- **Name note:** the brief's "Zou et al. / Zi et al." — the first author is **Yue Zi**.

## 1. Imaging model (§II, p. 3812)
- x_s = x_g + x_c (eq. 1): x_s sensor DN, x_g ground DN without cloud, x_c thin-cloud thickness map (additive atmospheric term).
- Band dependence: x_ci = α_i · x_c0 (eq. 2), α_i = thickness coefficient of band i relative to reference map x_c0 (thickness decreases with wavelength; per Makarau [13]).
- Model and inversion: x_si = x_gi + α_i x_c0 (3a); x_gi = x_si − α_i x_c0 (3b).
- Bands used: Landsat 8 OLI bands 1–5 (coastal, blue, green, red, NIR); SWIR assumed "only marginally influenced" (p. 3812). Cirrus band not needed (U-Net learns cirrus and low/mid thin cloud).

## 2. Algorithm (§III, Fig. 1, pp. 3812–3815)
1. **U-Net** (5 scales, 3×3 conv + BN + ReLU, sigmoid output in (0,1)) on bands 1–5 → x_c0.
2. **Slope-Net**: input bands 1–5 + x_c0; 4 × (3×3 conv, BN, ReLU, 2×2 max-pool) + 4×4 avg-pool → 128×4×4 (receptive field 94×94); 1×1 conv → 16 sets of 5 coefficients, averaged.
   - Rationale (Fig. 3, p. 3814): scatter of x_c0 vs x_s2 is linear (R² 0.9788) over homogeneous land cover, but not over mixed cover (R² 0.7955, 0.5503); there is a "virtual boundary line at the lower right of the scatter plot … composed of the dark pixels in the clear image", and α_i = its slope.
3. Recover each band by eq. 3b.
- Simulation (§IV, eq. 4, p. 3816): from real cloudy patches, x_ci(p) = min over a **3×3** window of x_si (dark-pixel search, after [13]); band 1 = reference (α_1 = 1); α_i by linear regression of x_ci on x_c1; add to real clear patches with eq. 3a.
- Training: 27 clear + 17 cloudy (10–50% cloud) Landsat 8 scenes → 256×256 patches; 5,000 simulated sets (4,500 train / 500 test); real test set 350 cloudy patches. L2 loss, Adam (β1 0.9, β2 0.999, ε 1e−8), batch 1, 200 epochs, lr 2e−4 × 0.1 every 50 epochs; GTX 1080 (p. 3817).

## 3. Results
- Coefficient AEE (eq. 5; Table II, p. 3818), bands 1–5: Xu 9.76/13.31/22.03/28.95/52.62%; Makarau 11.07/12.96/17.43/22.17/27.88%; Liu 30.10/31.66/36.48/39.28/62.21%; Slope-Net* (global pool) 3.09/3.61/4.99/6.03/9.76%; **Slope-Net 2.22/2.77/3.74/4.37/8.45%**. Error grows toward NIR.
- Synthetic test (Table III): MSE / PSNR / SSIM — DeepDive 0.0116/21.67/0.8110; DH-CNN 0.0051/25.05/0.8957; RSC-Net 0.0066/23.68/0.9166; McGAN 0.0006/33.48/0.9715; SCR-GAN 0.0008/32.85/0.9657; **proposed 0.0006/34.26/0.9832**.
- Real test, no ground truth (Table IV, p. 3821), DC ↓ / ΔH ↓: Xu 0.2497/**0.0320**; Makarau 0.3276/0.0328; **Li 0.1292**/0.1575; CR-NAPCT 0.3231/0.0453; DeepDive 0.1786/0.1537; DH-CNN 0.1434/0.1292; RSC-Net 0.1970/0.0468; McGAN 0.1827/0.0352; SCR-GAN 0.1535/0.1478; **proposed 0.1351/0.0337** (2nd DC, 3rd ΔH).
- No-reference metrics (eqs. 6–7): DC = mean over cloudy-region pixels of the dark channel of the restored image (min over r,g,b and a **5×5** patch) — residual haze; ΔH = mean |hue_restored − hue_cloudy| over non-cloud pixels (HSI) — colour change where there was no cloud. Cloud/non-cloud regions from binarising x_c0.

## 4. Stated limitations (pp. 3821–3822)
- Two CNNs → "accumulative estimation error" vs end-to-end methods.
- Trained on simulated data; "the simulated cloudy images are not completely consistent with the real cloudy images, so the thin cloud removal results of real cloudy images are worse". Future: end-to-end training on real unpaired images.

## 5. How to apply to our pipeline
- **Not directly usable:** the networks need Landsat bands 1–5 incl. coastal and NIR at 30 m, single date. Our data are Maxar RGB 0.5 m (used as grey), with a clear before date.
- **`sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym`:** our model is the transmission form after = t·ground + L. Zi's is the t = 1 special case (pure additive). Arm idea: compare the current transmission fit with an **additive-only** correction (after − L̂, no division by t) for very thin haze, where division by t amplifies noise; Zi's results show additive subtraction alone gives good colour fidelity on thin cloud. Keep T_MIN abstain for thick cloud.
- **Per-band coefficients on RGB:** if we de-haze R, G, B separately, Zi's band-ratio model (x_ci = α_i x_c0, α decreasing with wavelength) predicts blue gets the most haze. Fit α_R, α_G relative to blue on clear-reference pixels; check that α_B > α_G > α_R as a sanity test of the haze estimate. Then the grey product inherits a physically consistent correction.
- **Lower-boundary slope as a label-free fit (`sn8_refhaze` fit of after vs before):** Zi's observation is that over mixed cover the full scatter is not linear but its **lower envelope** (dark pixels) is. Our gain/offset fit uses all clear pixels in a window; an arm could fit the lower envelope (e.g. a low quantile regression, 5th–10th percentile) of after vs before inside the cloud gate instead of least squares on all pixels. That is our inference, not tested in the paper.
- **Label-free evaluation (`sn8_cloudedge.ring_measures` companion):** add Zi's DC (residual dark channel inside the cloud gate after correction, 5×5 patch, grey = drop the min over channels) and ΔH (or, for grey, mean |Δgrey| outside the gate, which should be ~0) as two more no-label columns. They map onto "residual haze" and "damage outside the cloud".
- **Feasibility:** concept transfers (RGB uint8 0.5 m, no NIR needed for the additive model or metrics); trained models do not.

## 6. Key quotes
- "the recovered clear image can be obtained by subtracting the thin cloud thickness maps from the cloudy image according to the traditional thin cloud imaging model" (abstract, p. 3811)
- "there is a virtual boundary line at the lower right of the scatter plot, which is composed of the dark pixels in the clear image" (p. 3814)
- "the thin cloud removal results of real cloudy images are worse than the thin cloud removal results of simulated cloudy images" (p. 3822)
