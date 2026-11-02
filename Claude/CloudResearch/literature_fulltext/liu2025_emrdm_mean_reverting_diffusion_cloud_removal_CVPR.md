# Coder handoff: Liu, Li, Guan, Zhou & Zhang (2025), EMRDM (improved mean-reverting diffusion for cloud removal)

- **Citation:** Liu, Y., Li, W., Guan, J., Zhou, S., & Zhang, Y. (2025). Effective cloud removal for remote sensing images by an improved mean-reverting denoising model with elucidated design space. *CVPR 2025*, 17851–17861. https://doi.org/10.1109/CVPR52734.2025.01663
- **PDF:** `/Users/jusrogers/Masters/papers/liu2025_emrdm_mean_reverting_diffusion_cloud_removal_CVPR-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/2503.23717 (v1, 31 Mar 2025): main paper pp. 1–8 + references + supplementary (29 PDF pages). Code: https://github.com/Ly403/EMRDM
- **Validation:** PDF 9.5 MB, 29 pages (Read tool; pdfinfo agrees); title and five authors (Tongji, Fudan) match Crossref for the DOI; Conclusion (§5, p. 8) and references present. 29 pages vs the 11-page proceedings range is explained by the supplementary material. PASS (preprint).
- **Read:** main paper pp. 1–8 in full; supplementary C.1 (datasets, preprocessing), C.1 compared methods, C.2 efficiency in full; App. A derivations, App. B related work and references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
- **CUHK-CR (0.5 m):** single cloudy image (RGB + NIR); 8 input channels = 4 noisy + 4 cloudy (supp. Table 5). No reference date.
- **SEN12MS-CR:** single cloudy Sentinel-2 + Sentinel-1 SAR.
- **Sen2_MTC_New ("multi-temporal"):** **L = 3 cloudy images** of the same place + IR; all inputs may be cloudy; no clear reference. Each date is denoised, then outputs are averaged (Alg. 2, line 13).
So none of its settings is "clear before date + cloudy after date". Under thick cloud in the single-image setting it generates.

## 1. Algorithm (§3, pp. 3–6)
- Forward mean-reverting SDE (eq. 3): `dx = f(t)(x − μ) dt + g(t) dω`, μ = cloudy image. Perturbation kernel (eqs. 4–6): `x̃(t) = x(t)/s(t) ~ N(x(0) + ((1 − s)/s) μ, σ(t)² I)` with `s(t) = exp∫f`, `σ(t) = sqrt(∫ g²/s²)` (eq. 7). Choice: **σ(t) = t, s(t) = 1/(1 + αt), α = 3** (Table 3), so k(t) = (1−s)/s = αt.
- Backward ODE (eq. 11) with denoiser D_θ; score from denoiser (eq. 10).
- Preconditioning (eqs. 13–17): `D_θ = mean_l(c_skip x̃^l) + c_out F_θ({c_in x̃^l}; c_noise; c)` with c_in, c_skip, c_out depending on σ_data, σ_mu (cloudy variance), σ_cov (clear–cloudy covariance), L; c_noise = ¼ ln σ. Best σ_data = σ_mu = 1.0, σ_cov = 0.9.
- Training (Alg. 1, eq. 18): ln σ ~ N(P_mean, P_std²); `x̃_0 = x(0) + α σ μ`; loss λ(σ)||D_θ − x(0)||², λ = 1/c_out².
- Sampling (Alg. 2): EDM-style Euler with churn; **N = 5 steps** best (50 steps worse, Table 3); σ_max = 100, σ_min = 0.001; stochastic sampler better PSNR, deterministic better SSIM/LPIPS at high churn.
- Network: HDiT; multi-temporal variant = L weight-sharing encoders + temporal HDiT block with temporal fusion self-attention (learned query, L-TAE style); attention masks reweight skip connections (eq. 12).

## 2. Data (supp. C.1)
- CUHK-CR1 (thin, 668) and CUHK-CR2 (thick, 559) from Sui et al. 2024; 534/134 and 448/111 split; resized 512 → 256; RGB + NIR; scaled to [−1, 1]. Only train/test, no validation split reported.
- SEN12MS-CR (13-band S2 + 2-band S1), standard split; Sen2_MTC_New (RGB + IR, 2,380 / 350 / 687 train/val/test).
- Hyperparameter studies are on Sen2_MTC_New only.

## 3. Quantitative results (Table 1, p. 6; Tables 2–4, pp. 7–8)
| Dataset | EMRDM | Best prior |
|---|---|---|
| CUHK-CR1 (thin) PSNR/SSIM/LPIPS | 27.281 / 0.8007 / 0.0218 | DE-MemoryNet 26.183 / 0.7746 / 0.0290 |
| CUHK-CR2 (thick) | 24.594 / 0.6951 / 0.0301 | DE-MemoryNet 24.348 / 0.6843 / 0.0369 |
| SEN12MS-CR PSNR/SSIM/MAE/SAM | 32.14 / 0.924 / 0.018 / 5.267 | DiffCR 31.77 / 0.902 / 0.019 / 5.821 |
| Sen2_MTC_New PSNR/SSIM/LPIPS | 20.067 / 0.709 / 0.255 | DiffCR 19.150 / 0.671 / 0.291 |
- Thin-cloud gain at 0.5 m ≈ 1.1 dB; **thick-cloud gain ≈ 0.25 dB**.
- Ablation (Table 2, Sen2_MTC_New): pure generative DM (s = 1, no cloudy input) 12.81 dB → + cloudy image 18.26 → + IR 19.31 → + MRDM framework 19.52 → + preconditioning 19.47 (PSNR) with better SSIM/LPIPS. Conditioning on the observation is the big step; the framework adds ~0.2 dB.
- Sequence length (Table 4): L = 1 16.09 dB, L = 2 18.10, L = 3 20.07 — more dates matter more than any design choice.
- Baseline values largely cited from earlier papers (supp. C.1); single runs; no significance tests; no limitations section.
- Cost: 39.1 M params (mono-temporal), ~130 ms per 256 px image on an RTX 4090.

## 4. Stated limitations
None stated. Our reading: (i) generative under opaque cloud; (ii) multi-temporal input means several cloudy acquisitions, not a clear reference; (iii) no downstream or change test; (iv) CUHK-CR has no validation split, so checkpoint choice on it is unstated.

## 5. How to apply to our pipeline
- **Do not feed EMRDM output to the flood detector**; single-image generation at 0.5 m.
- **Usable without inventing content:**
  1. **Observation anchoring is the lever, not the generator.** Their Table 2 shows starting from the cloudy observation is worth +5.5 dB over pure noise; the rest is fine-tuning. Our physics route (`sn8_refhaze.dark_reference_dehaze`, t from the haze model) is already fully anchored to the observation and the clear before date; no change needed, but this is a citation for "anchor to what is observed".
  2. **Thin vs thick reported separately at 0.5 m**, with the thick-cloud gain over prior work only ~0.25 dB: supports treating thick/opaque cloud as "not observed" (T_MIN abstain) rather than trying to reconstruct it.
  3. **More dates beat better models** (L = 1 → 3: +4 dB). For us: if a second post-event acquisition ever exists, it is worth more than any generative fill. Note for the project's data-request list, not a code change.
- **Feasibility:** retraining needs paired cloudy/clear 0.5 m data with NIR (CUHK-CR); our RGB uint8 grey data would need a 3-channel retrain; GPU (RTX 4090 class). Not recommended for scoring.

## 6. Key quotes
- "Existing diffusion-based CR methods typically employ vanilla DM frameworks that start the diffusion process from pure noise ... this is unnecessary as cloudy images contain substantial unexploited information. Even worse, noise-initiated generation lacks pixel-level consistency" (p. 1)
- "Increasing L consistently boosts performance across all metrics, highlighting the benefits of multi-temporal inputs" (p. 8)
- "a large N yields poor results, while using only five steps delivers superior results across most metrics" (p. 8)
