# Coder handoff: Zou, Li, Xing, Zhang, Wang, Jin & Tao (2024), DiffCR (fast conditional diffusion for cloud removal)

- **Citation:** Zou, X., Li, K., Xing, J., Zhang, Y., Wang, S., Jin, L., & Tao, P. (2024). DiffCR: A fast conditional diffusion framework for cloud removal from optical satellite images. *IEEE TGRS* 62, 1–14. https://doi.org/10.1109/TGRS.2024.3365806
- **PDF:** `/Users/jusrogers/Masters/papers/zou2024_diffcr_fast_conditional_diffusion_cloud_removal_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/2308.04417 (v1, 8 Aug 2023; only version), 13 pages. Its running header "VOL. 14, NO. 8, AUGUST 2021" is an IEEE template leftover, not the publication. The TGRS version (2024, 14 pp.) appeared ~6 months later and may contain more experiments (see claim 3 below). Code: https://github.com/XavierJiezou/DiffCR
- **Validation:** PDF 16.6 MB, 13 pages (Read tool; pdfinfo agrees); title and seven authors match Crossref for the DOI; Conclusion (§V, p. 11) and references present. Same first author as Cloud-Adapter. PASS (preprint).
- **Read:** pp. 1–11 in full; references and biographies pp. 11–13 skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
**N = 3 cloudy Sentinel-2 images of the same patch** (multi-temporal); label = the least-cloudy clear acquisition. No clear reference date is an input. With N = 1 it is single-image removal (tested only in the ablation, Table II). Generative under cloud.

## 1. Algorithm (§III, pp. 3–7)
- DDPM forward (eqs. 1–3), conditional reverse `p_θ(y_{t−1} | y_t, x)` (eqs. 4–5), x = stack of N cloudy images.
- **Data prediction**: train f_θ to output y0 directly, `L = E||y0 − f_θ(√ᾱ_t y0 + √(1−ᾱ_t) ε, t, x)||_p^p` (eq. 18), not ε (eq. 17).
- Denoiser: UNet of **TCFBlocks** (eqs. 6–11): `F_n = SEM(F_i) + F_i + F_t`, `F_o = FRM(F_n) + F_n + F_c`; SEM = LN → 1×1 conv → depthwise 3×3 → split self-activation → split channel attention (half GAP, half GMP) → 1×1; FRM = LN → 1×1 (×2 channels) → SSA → 1×1.
- **Decoupled condition encoder** (eq. 12): TCFBlocks + 2×2 stride-2 conv downsampling on x; its multi-scale features F_c are added in every denoiser block (vs concatenating x with y_t).
- Time encoder: sinusoidal + MLP (eq. 13). Skip connections by sum; PixelShuffle upsampling.
- Sigmoid noise schedule; T = 2000; DPM-solver; **1 sampling step** used for the final results.
- Training: AdamW 5e-5, batch 8, ~7 M steps, EMA 0.9999, 4 × RTX 3090.

## 2. Data (§IV-A)
- **Sen2_MTC_Old:** 945 Sentinel-2 tiles, 10 m, 256 × 256 patches; "clear" < 1% cloud, "cloudy" 10–30%, > 30% discarded; 3 cloudy inputs + 1 clear label; 3,130 pairs; values 0–255.
- **Sen2_MTC_New:** ~50 tiles × ~70 patches, same construction, reflectance 0–10,000, better annotation (all ablations here).

## 3. Quantitative results (Tables I–VI)
- Table VI: Sen2_MTC_Old PSNR/SSIM/FID/LPIPS 29.112 / 0.886 / 89.8 / 0.258 vs DDPM-CR (1000 steps) 27.060 / 0.854 / 110.9 / 0.320; Sen2_MTC_New 19.150 / 0.671 / 83.2 / 0.291 vs DDPM-CR 18.742 / 0.614 / 94.4 / 0.329, UnCRtainTS 18.770 / 0.631. 22.9 M params, 45.9 GMACs (5.1% / 5.4% of DDPM-CR).
- Table II: noise prediction collapses (PSNR ≈ 3.7 dB); data prediction **N = 1: 15.14, N = 2: 16.22, N = 3: 19.15 dB**.
- Table III: decoupled condition encoder +0.33 dB over concatenation.
- Table IV: 1 step 19.150 dB in 0.09 s; 3 steps 19.182; 50 steps 19.102; 100 steps 19.077 — more steps slightly worse.
- Table V: width 64 chosen; concat skip connections unstable (15.1 dB).
- Single runs; no significance tests.

## 4. Stated limitations (§IV-E, p. 11; Fig. 7)
- "when the input cloudy images containing lake regions with black hole-like shapes, our method encounters challenges in accurately reconstructing the lake areas ... attributed to the inherent similarity between the irregular, dark lake regions and cloud shadows"; "the clouds may erroneously occupy the holes in the generation".
- Training still needs many iterations; not validated beyond cloud removal.

## 5. How to apply to our pipeline
- **Do not use as a fill for flood scoring** (generative; fuses cloudy dates, not a clear before date; 10 m).
- **Usable without inventing content:**
  1. **Dark water ↔ cloud shadow confusion** (their failure case). Floodwater is dark and flat, like a cloud shadow. Any shadow handling we add (none exists yet: HRC_WHU has no shadow labels) must not treat dark, flat after-pixels as shadow to be brightened or masked. In `sn8_cloudsym`, the dark-channel fall gate (cloud in the BEFORE image) and any future shadow arm should be checked against labelled flooded roads before use; a shadow keeps the before texture (darkened), water replaces it — test texture retention (`sn8_texture`) as the separator.
  2. **Extra dates >> architecture**: N = 1 → 3 is +4 dB, larger than every design change in the paper. Same message as EMRDM.
  3. **Few-step sampling suffices** for conditional restoration (1–5 steps): only relevant if a generative display product is ever made.
- **Feasibility:** retraining needs paired multi-date cloudy/clear data; nothing at 0.5 m in the paper. Not recommended.

## 6. Key quotes
- "Since the conditional input image and the cloud-free ground truth image share more similar data distributions, data prediction is significantly easier than noise prediction" (p. 7)
- "DiffCR exhibits inadequacy in scenarios where the input cloudy images feature lake formations resembling black holes. In such cases, the clouds may erroneously occupy the holes in the generation." (Fig. 7 caption, p. 11)
- "obtaining a cloud-free image from a single frame becomes a significant challenge when the cloud coverage is extensive, as there is insufficient information to facilitate image reconstruction" (p. 2)
