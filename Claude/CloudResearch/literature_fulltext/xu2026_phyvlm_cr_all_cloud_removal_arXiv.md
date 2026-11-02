# Coder handoff: Xu, Li & Shen (2026), Physics-Guided VLM Priors for All-Cloud Removal (PhyVLM-CR)

- **Citation:** Xu, L., Li, H., & Shen, H. (2026). Physics-Guided VLM Priors for All-Cloud Removal. arXiv:2603.07074 [cs.CV], submitted 7 March 2026. **arXiv preprint version** (letter format, no journal named; not peer-reviewed as far as the PDF shows).
- **PDF:** `/Users/jusrogers/Masters/papers/xu2026_phyvlm_cr_all_cloud_removal_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** https://arxiv.org/pdf/2603.07074
- **Validation:** `file` = PDF; 764 KB; 5 pages (Read tool read all 5; pdfinfo 5); title and 3 authors match the arXiv API record; Conclusion and 14 references present; no DOI. PASS.
- **Read:** pp. 1–5 in full (from the PDF directly; equations read from page images).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§II–III, pp. 1–3)
Model: `I(x) = J(x) t(x) + A (1 − t(x))` (eq. 1); `J = J_VLM + E` (eq. 2, E = hallucination residual).
1. **Cognitive prior:** `J_VLM` = Qwen-Image-Edit output for the prompt "remove cloud" (in Chinese).
2. **Airlight A (eqs. 3–4):** `Ω = {x | σ(V_x)·σ(1 − S_x)·σ(−‖∇I_x‖) > κ}` (V brightness, S saturation, ∇I gradient, σ sigmoid); κ "set to the 85% of the probability map"; `A = median_{x∈Ω} I(x)`.
3. **Transmission (eq. 5):** base layers (superscript B) by edge-preserving filtering, then per pixel
   `t = (I^B − A)ᵀ (J_VLM^B − A) / (‖J_VLM^B − A‖² + ε)`, ε = 10⁻⁶ (a least-squares slope across bands).
4. **Confidence (eqs. 6–7):** `r = ‖I^B − (t J_VLM^B + (1 − t) A)‖₂`;
   `U = exp(−r/λ_phy) · exp(−max(0, H(J_VLM) − H(I))/λ_hall)`, H = Laplacian high-frequency magnitude; λ_phy, λ_hall = 75th percentiles of the respective maps.
5. **Refine t** with a guided filter weighted by U (no r, ε given).
6. **Physical inversion (eq. 8):** `J_phy = (I − A)/max(t, t0) + A` (t0 not given).
7. **Frequency-decoupled adjustment (eq. 9):** `J_cog = J_phy + α U (J_VLM^lp − J_phy^lp) + β t (I − I^lp)` (lp = low-pass; α, β not given).
8. **Fusion with a reference date (eqs. 10–11):** reference `I_ref` "radiometrically aligned to the current scene using linear parameters estimated from high-visibility areas"; `J = ω J_cog + (1 − ω) I_ref`, **`ω = exp(−γ (1 − t))`, γ = 4.0**, chosen so the surface signal falls below 2% (e⁻⁴ ≈ 0.018) at the optical-depth limit (citing Chavez 1988).

## 2. Data and protocol (§IV, Table I, p. 3–5)
- Sentinel-2 surface reflectance, 10 m visible bands, six scenes in China (Sichuan, Hainan, Qinghai, Hubei, Jiangsu, Yunnan), 2023.
- T1 cloudy; **T2 = nearest clear date = ground truth** (5–45 days from T1); **T3 = second-nearest clear date = reference** (20–50 days). Comparison methods get thick-cloud masks from MSK_CLDPRB ≥ 40, resampled 20 → 10 m, closed then opened.
- Baselines: SSADCP (thin) + FRARC (thick) with masks; ZID (thin) + DIP (thick), 500 iterations each, ~30 min/scene; raw Qwen output.

## 3. Results (Table II, p. 4)
| Scene | Physical | Zero-shot DL | VLM | PhyVLM-CR |
|---|---|---|---|---|
| PSNR range | 15.50–19.70 | 9.71–14.57 | 13.23–20.89 | **18.77–27.19** |
| SSIM range | 0.53–0.77 | 0.22–0.31 | 0.03–0.57 | **0.72–0.92** |
- Best in all six scenes on both metrics. Qualitative: mask-based pipeline leaves residue in thick-to-thin transition zones and replaces bright surfaces misread as cloud with reference data; raw VLM invents land cover "and even spurious characters" under thick cloud (p. 5).

## 4. Limitations (ours, from reading; the paper states none)
- Truth is a different date (5–45 days), so PSNR/SSIM also count real ground change; six scenes; no significance tests; no ablation of U, the guided filter or ω; α, β, t0, guided-filter r/ε and the edge-preserving filter not specified; speed claimed "second-level" but the VLM step's cost not given.
- Preprint; not peer-reviewed.

## 5. How to apply to our pipeline
- **Soft visibility weight instead of hard abstain + fixed fade (`sn8_refhaze.dark_reference_dehaze`, `sn8_cloudedge.edge_dehaze`):** we already have t from the two-date fit. Compute `ω = exp(−γ (1 − t))` with γ = 4 as the paper's default, and test γ ∈ {2, 4, 8} as arms. Use ω (a) as a per-pixel confidence in the provenance layer and (b) to blend between "corrected" and "not observed" — **not** to blend in the before image (that is the paper's step 8, which would copy pre-flood ground into flooded roads). With γ = 4, ω < 0.5 when t < ~0.83 and ω ≈ 0.04 at our `T_MIN` = 0.2; compare the road counts that fall below thresholds against the current hard `T_MIN` rule.
- **No-mask gating removes the gate edge:** the paper's point is that a continuous t-driven weight avoids the seam at a binary cloud mask. Our ring sits exactly at the gate edge; an arm where the correction is applied everywhere with weight `1 − t`-driven (no gate, no 20 m fade) addresses the ring the same way. Compare on `sn8_cloudedge.ring_measures`.
- **Confidence-weighted guided filter on t:** refine t with a guided filter whose input is weighted by a confidence map (our analogue of U: the local fit residual of `after ≈ t·before_toned + (1 − t)A`). This complements the He 2013 recipe (guide = hazy after image).
- **Airlight from bright, unsaturated, low-gradient pixels:** `sn8_clouds` uses the He 0.1% rule (`AIRLIGHT_SHARE`). The paper's Ω (brightness × (1 − saturation) × low gradient, top ~15%, median) is computable on our RGB tiles and avoids white roofs (high gradient at edges, but flat roofs are low-gradient — check on tiles with large white roofs).
- **Reference alignment = our tone curve:** "linear parameters estimated from high-visibility areas" is the same idea as `tone_curve` on clear pixels (theirs linear, ours quantile).
- **VLM step:** not feasible or desirable for scoring; a generative fill would invent roads.
- **Feasibility:** steps 2–6 and 8's weight are feasible on RGB uint8 0.5 m with the before date as our "J" proxy (we have the clear before image where the paper uses J_VLM). No SAR/NIR needed.

## 6. Key quotes
- "The resulting reliance on cloud detection makes removal quality heavily contingent on segmentation accuracy. Misalignment in transition zones inevitably leads to error propagation and visible boundary artifacts." (p. 1)
- "the parameter γ is set to 4.0 … simulating an effective optical depth limit where the surface signal transmission drops below 2%" (p. 3)
- "the VLM relies solely on semantic priors, leading to severe hallucinations where valid ground details are replaced by fictitious textures, including non-existent land-cover patterns and even spurious characters" (p. 5)
