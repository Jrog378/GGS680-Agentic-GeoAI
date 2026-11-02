# Coder handoff: Berman, Treibitz & Avidan (2020), Single Image Dehazing Using Haze-Lines

- **Citation:** Berman, D., Treibitz, T., & Avidan, S. (2020). *IEEE TPAMI* 42(3), 720–734. https://doi.org/10.1109/TPAMI.2018.2882478 (DOI from Crossref).
- **PDF:** `/Users/jusrogers/Masters/papers/berman2020_haze_lines_single_image_dehazing_TPAMI-summary.pdf` (page 1 = AI summary)
- **Source:** IEEE early-access accepted version ("accepted for publication … not been fully edited"), hosted by co-author Treibitz's Viseaon lab, University of Haifa: https://www.viseaon.haifa.ac.il/_files/ugd/acdb85_20cc773638b44f12bb45e0561f7d76fa.pdf . Pages 1–14 numbered + 2 unnumbered (cover/biographies). Page numbers below are the copy's.
- **Validation:** PDF, 48.1 MB, 16 pages (Read tool error "This PDF has 16 pages"; pdfinfo 16) vs 15 published (720–734): early-access layout, consistent. Title/authors/DOI match Crossref; Conclusion (§6), references and biographies present. PASS (early-access version noted).
- **Read:** all 16 pages (references/biographies skimmed).
- **Prepared by:** Claude (AI), 2026-10-29. Code: https://github.com/danaberman/non-local-dehazing (MATLAB; not downloaded).

## 1. Algorithm (Algs. 1–2, §4, pp. 4–7)
Intensities **normalised to [0, 1]** (p. 8). Model I = tJ + (1 − t)A (eq. 1), t same for all channels.
1. **Airlight A (Alg. 1):** K-means/indexed colours N = 1000 clusters {I_n, w_n}; Hough vote in each 2-D channel pair (RG, GB, RB) over candidate A on a grid ΔA = 0.02, K = 40 angles; vote if distance to line < τ = τ0(1 + ‖I − A‖/√3), τ0 = 0.02, and A > I_n in every channel; weight w_n·f(‖I_n − A‖), f(y) = 1 + 4e^−y; A = argmax of the outer product of the three accumulators. Works without visible sky ("as is often the case, for example in aerial photos", p. 8).
2. **Haze-lines:** I_A = I − A in spherical coords (r, θ, φ); assign each pixel to the nearest of Q = 1000 uniformly tessellated sphere points (KD-tree).
3. **Initial t:** t̃ = r / r̂_max, r̂_max = max r on the haze-line (eq. 17).
4. **Lower bound:** t_LB = 1 − min_c(I_c/A_c) (eq. 18; the pixel-wise dark channel bound); t̃_LB = max(t̃, t_LB).
5. **Regularise (eq. 20):** min Σ f(σ(x))(t̂ − t̃_LB)²/σ(x)² + λ Σ_{y∈N4} (t̂(x) − t̂(y))² / ‖Ĩ(x) − Ĩ(y)‖², λ = 0.1, σ(x) = std of radii on the haze-line, f(σ) = min{1, 3·max{0.001, σ/max σ − 0.1}}. Solved by closed-form WLS (3.1 s/MP) or **constrained WLS t̂ ≥ t_LB** (interior point; 121.9 s/MP) (§5.4).
6. **Recover:** J = (I − (1 − t̂)A)/t̂ (eq. 21).

## 2. Quantitative results we could compare to
- O-HAZE (45 real smoke-machine scenes; SSIM ↑, CIEDE2000 ↓) (Table 1): DCP 0.735/20.745; Meng 0.753/16.968; MSCNN 0.765/14.670; HL 0.750/17.088; **HL constrained 0.781/16.579**.
- Airlight on 40 images: lower median L2 error than [5], [7], [18]; inter-annotator median 0.02 (Fig. 8).
- Synthetic robustness (Fig. 15): t error ≈ 50% of t at t = 0.15, rising as t falls; at t = 1 the mean error is higher than for t < 0.6 with a large SD → best in medium haze.
- Sensitivity to A (Fig. 16): t errors grow with σ_A; J errors much less.

## 3. Stated limitations
- Plain WLS violates t ≥ t_LB → dark, detail-losing output (Fig. 14).
- Non-uniform lighting; colours collinear with A are indistinguishable from haze (eq. 12; Fig. 17).
- Model holds for linear radiance; "most camera-processed images (commonly in JPEG format) do not have a linear relationship with the radiance … the dehazing process should be applied to a radiometrically corrected image" (p. 3).
- Single atmospheric light; "in thick fog, the atmospheric light often varies spatially" (p. 3).

## 4. How to apply to our pipeline
- **Greyscale: not applicable as a whole.** With one band, I − A is a scalar, so every pixel lies on one haze-line and t̃ collapses to a global ratio. The method requires the RGB tiles. The Maxar tiles are RGB uint8 (processed, not linear radiance), so an RGB single-date arm is possible but outside our greyscale rule and the paper warns about non-linear images.
- **Reusable parts (grey-compatible):**
  - **Constrained refinement:** whatever refines t (guided filter, WGIF, BCCR, SD filter) should not let t drop below a physical lower bound. For grey data the bound J ≥ 0 gives t_LB = 1 − after/A (eq. 18 with one channel), so clip refined t to [t_LB, 1]. Berman shows ignoring the bound loses detail (Fig. 14). Add to `sn8_cloudedge.t_source` after any refinement: `t = np.maximum(t_refined, 1 - after/airlight)`.
  - **Confidence-weighted data term:** weight the data term by how trustworthy the raw t is (they use the radius spread). For us: weight by the number/quality of clear pixels in the tone-curve fit, or by |dark rise| relative to noise; low weight near no-data.
  - **Edge weights 1/‖ΔI‖²** from the hazy (after) image for the smoothness term (eq. 20) — a WLS refinement with λ = 0.1 on [0,1] data.
- **Thresholds:** the paper's own t-error analysis (≈ 50% error at t = 0.15) supports our T_MIN = 0.2 abstain rule, and warns that thin haze (t → 1) is the hardest regime for single-image t.
- **Airlight without sky:** the Hough method is designed for scenes with no visible sky (aerial). Our A is the brightest pixel among the haziest 0.1% (He 2011); with RGB tiles the haze-line Hough A could be a cross-check.
- **Feasibility:** single-image RGB method; no SAR/NIR needed; does not use the before date. Low priority for code beyond the bound/WLS ideas.

## 5. Key quotes
- "the proposed method is global and does not divide the image to patches" (p. 1)
- "Unfortunately, when solving Eq. (20) with a closed form weighted-least squares (WLS) solution, the solution does not always conform to the lower bound in Eq. (18)." (p. 12)
- "For transmission values of 0.15, the mean estimation error is about 50% of the transmission value, and the error increases as the transmission decreases." (p. 13)
