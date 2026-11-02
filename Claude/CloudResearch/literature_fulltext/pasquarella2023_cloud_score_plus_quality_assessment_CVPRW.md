# Coder handoff: Pasquarella, Brown, Czerwinski & Rucklidge (2023), Comprehensive quality assessment of optical satellite imagery using weakly supervised video learning (Cloud Score+)

- **Citation:** Pasquarella, V. J., Brown, C. F., Czerwinski, W., & Rucklidge, W. J. (2023). *CVPR Workshops (EarthVision)*, 2125–2135. https://doi.org/10.1109/CVPRW59228.2023.00206 (Google LLC; company paper).
- **PDF:** `/Users/jusrogers/Masters/papers/pasquarella2023_cloud_score_plus_quality_assessment_CVPRW-summary.pdf` (page 1 = AI summary)
- **Source:** CVF open access, https://openaccess.thecvf.com/content/CVPR2023W/EarthVision/papers/Pasquarella_Comprehensive_Quality_Assessment_of_Optical_Satellite_Imagery_Using_Weakly_Supervised_CVPRW_2023_paper.pdf ("identical to the accepted version" except the watermark). Evidence 10 recorded this page as 403; it downloaded fine today.
- **Validation:** PDF 1.5, 4.8 MB, 11 pages (Read tool and pdfinfo) = published 2125–2135; title, 4 authors and DOI match Crossref; Conclusions + 67 references present. PASS.
- **Read:** pp. 2125–2135 in full; eqs. 4–6 and Tables 1–2 read from page images; references skimmed.
- **Type:** method + benchmark comparison (cloud/shadow QA). Prepared by Claude (AI), 2026-10-29.

## 1. Core idea and equations
- Continuous QA instead of classes: "due to the continuous density of the atmospheric volume, we argue that quantification of occlusion and corruption effects is better treated as a regression problem rather than a discretized classification problem" (abstract, p. 2125).
- Corruption model (eq. 1, p. 2127): `QA(p_m) = q`, `p_m = p_t q + c (1 − q)`; p_m observed pixel, p_t "true" TOA reflectance under minimal optical depth, c the corrupted surface (cloud, shadow, atmosphere), q ∈ [0, 1]. Mixing pixels mixes q linearly (used for mixup).
- Atmospheric similarity (eq. 2): `ASIM_i(x_i, y_i) = min_{p ∈ {x_i, y_i}} QA(p)`. If r is clear (QA = 1), `ASIM(x, r) = QA(x)` — the score of an image against a clear reference is its quality.
- Inputs log-transformed `x' = log(x + 1)/10` (eq. 3), Sentinel-2 L1C TOA, all 13 bands.
- Loss (eqs. 4–6): Gaussian NLL with clamped log-variance: `z = log σ²|_[a,b]`, `r = (z − log σ²)²`, `l = (log 2π + z + (µ′ − µ)²/e^z)·½ + r`, a = −16, b = 5.

## 2. Training pipeline (pp. 2127–2129)
1. ASIM pre-training on ~6 M image pairs (same-location pair identification; robust to snow, phenology, misregistration), pairs mined with SSIM.
2. Fine-tune on **388** hand-picked fully clear pairs + **512** pairs with sparse markup at grades {0, 1/3, 2/3, 1} + synthetic clouds, shadows, haze (mixup).
3. Mine sequences (12 UTM zones chosen for confusing surfaces: bright targets, topographic shadow, urban, water; 1.8 km cells; yearly octants). Pairs with `µ − σ > 0.75` are clear references; every image scored against the nearest reference. Sequences with no reference, "too cloudy" or "too clear" are rejected. Result: **2.2 M** clips, 2018–2021, with terrain-illumination targets from AW3D30.
4. QA model: target + query set (1→8 images in training; 16 at inference) of the same place, three-head attention over time, per-pixel MLP heads for QA (µ, log σ²), QA percentile, terrain illumination. Seams between inference sub-tiles fixed by a gain/bias least squares (eq. 8, λ = 1).

## 3. Evaluation protocol and numbers (§4, pp. 2129–2131)
- All labels and outputs collapsed to **clear vs not clear**; cloud and cloud shadow → not clear. Thin cloud is not treated separately in scoring (CMIX-I uses cloud characteristics, shadow and aerosol IDs to form the binary label).
- Continuous products thresholded at 0.00–1.00 in **0.01 steps**; report the threshold that gives the **most balanced omission and commission** error. Metrics: F1, overall accuracy, omission, commission, precision, recall.
- **Tarrio** (2,681 points, 28 S2 images, 6 tiles; 50 points removed for label mismatch; strata weights ignored), Table 1:
| Processor | Thr. | F1 | OA | Omission | Commission |
|---|---|---|---|---|---|
| CS+ | 0.64 | 0.8466 | 0.8096 | 0.1889 | 0.1933 |
| Fmask v2 | – | 0.8133 | 0.7742 | 0.2411 | 0.1976 |
| MAJA | – | 0.8002 | 0.7218 | 0.1402 | 0.5324 |
| s2cloudless | 0.12 | 0.7589 | 0.7111 | 0.2985 | 0.2711 |
| Fmask v4 | – | 0.7444 | 0.7233 | 0.3783 | 0.0896 |
| Sen2Cor | – | 0.5190 | 0.5675 | 0.6399 | 0.0508 |
| QA60 | – | 0.4579 | 0.5401 | 0.7003 | 0.0173 |
- **CMIX-I PixBox** (17,351 points, 29 L1C products), Table 2: CS+ all points thr 0.50 F1 0.8816 / OA 0.8768; CS+ no shadows thr 0.48 F1 0.8800; s2cloudless all points thr 0.18 F1 0.8162; s2cloudless provider threshold 0.40 F1 0.8263 (no shadows).
- No significance tests, no confidence intervals.

## 4. Stated limitations (p. 2131)
- "known weaknesses include detection of cloud shadows over water, mis-characterization of moving boats as bad QA, and high uncertainty over active ice floes." Optimal threshold is dataset-dependent (0.64 vs 0.48–0.50). Variance output can filter uncertain cases.
- Landsat 8/9 results "very promising" but informal (Fig. 6).

## 5. Licence / usage
- The paper states none for the model or product. It says CS+ products are expected for "all historic and newly acquired Sentinel-2 L1C images" (p. 2132). (Our notes elsewhere that CS+ is an Earth Engine collection come from outside this paper.)

## 6. How to apply to our pipeline
- **Graded gate (sn8_cloudsym gate, sn8_refhaze t):** our t from the two-date dark-channel fit already is a per-pixel q in eq. 1's sense (p_m = p_t t + A(1 − t)). Expose t (and a local uncertainty, e.g. fit residual) as the visibility score instead of only the binary blob gate; derive "cannot assess" as t < T_MIN, "corrected" as T_MIN ≤ t < ~0.9, "clear" above. This is a re-labelling of existing outputs, not new modelling.
- **Reference logic:** ASIM(x, r) = QA(x) when r is clear is exactly our setting (clear before date = r). It supports using pre/post similarity as the visibility measure. Caveat the paper also states: real change between dates (flood!) looks like corruption to a similarity score. Our gate must separate flood darkening from haze brightening/contrast loss; keep the dark-rise sign test and texture-correlation test (`sn8_texture`).
- **Evaluation recipe for our cloud masks (sn8_cloudspot on HRC_WHU, sn8_clouds masks):** collapse to cloud vs clear, sweep thresholds in 0.01 steps, report the threshold that balances omission and commission, with F1, OA, omission, commission, precision, recall — the same table columns, so our numbers line up with Table 1/2 in form. Add our McNemar tests (they have none).
- **Failure modes to test:** shadows over water (= our flooded roads under cumulus shadow) are CS+'s first listed weakness; report this stratum separately.
- **Feasibility:** concept, model eq. 1, and protocol are feasible on RGB uint8 0.5 m with one before date. The trained model is Sentinel-2 L1C with time series; not usable.

## 7. Key quotes
- "better treated as a regression problem rather than a discretized classification problem" (p. 2125)
- "when observing a time series of acquisitions or a clear image at the same location, humans can easily perceive clouds and cloud shadows even without large spatial contexts" (p. 2127)
- "the true counterfactual, i.e., the image uncontaminated by the atmosphere, is unknowable due to unseen changes in ground condition" (p. 2126)
- "known weaknesses include detection of cloud shadows over water" (p. 2131)
