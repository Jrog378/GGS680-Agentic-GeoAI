# Coder handoff: Sui, Ma, Yang, Zhang, Pun & Liu (2024), Diffusion Enhancement (DE) and the CUHK-CR benchmark

- **Citation:** Sui, J., Ma, Y., Yang, W., Zhang, X., Pun, M.-O., & Liu, J. (2024). Diffusion enhancement for cloud removal in ultra-resolution remote sensing imagery. *IEEE TGRS* 62, 1–14. https://doi.org/10.1109/TGRS.2024.3411671
- **PDF:** `/Users/jusrogers/Masters/papers/sui2024_diffusion_enhancement_cloud_removal_cuhk_cr_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/2401.15105 (v1, 25 Jan 2024; the only version). Pages numbered 1–13. The published version is 14 pages; content may differ slightly.
- **Validation:** PDF 2.3 MB, 13 pages (Read tool; pdfinfo agrees); title and six authors match Crossref; Conclusion (p. 12) and 44 references present. PASS (preprint).
- **Read:** pp. 1–12 in full; references pp. 12–13 skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
**Single cloudy image only.** Training uses (cloudy, clear 10–17 days apart) pairs as supervision; at inference DE sees only the cloudy image y (the noise predictor is conditioned on y; the "reference visual prior" x0,E = E(y) is the output of a pretrained single-image cloud-removal network, eq. 11, p. 6). "Reference" here does **not** mean a reference date. Nothing in DE can see the ground under opaque cloud; it predicts it.

## 1. CUHK-CR dataset (§III, pp. 3–4)
- Jilin-1KF01B push-broom camera: pan 0.5 m (450–800 nm), B/G/R/NIR at 2 m, pan-sharpened to **0.5 m, 4 bands** (Table II).
- Three sites in China (Table III): Shenzhen (cloudy 2022-08-24, clear 2022-09-03), Jinan (2022-08-24 / 2022-09-10), Hangzhou (2023-01-31 / 2023-01-21). Gap ≤ 17 days; the clear image can be before or after.
- **CUHK-CR1 (thin): 668 images; CUHK-CR2 (thick): 559 images**, 512 × 512; 8:2 split → 534/134 and 448/111 (p. 3). Resized/cropped to 256 × 256 for all experiments (p. 7).
- **How thin vs thick was decided is not stated.** A Cloud-Net detector was used only for Cloud Coverage Probability statistics and "fails to differentiate between thin and thick cloud layers" (p. 4). Images "totally obscured by the dense clouds" were removed "through visual observation" (p. 4). Mean CCP: 50.7% thin, 42.5% thick (Figs. 1–2).
- No cloud masks are used in scoring; metrics are over the whole image.

## 2. Algorithm (§IV, pp. 4–7)
- Forward DDPM, eqs. 1–4: `x_t = √ᾱ_t x0 + √(1−ᾱ_t) ε`.
- Conditional noise predictor (CNP) `ε_t = ε̂_θ(x_t, t, y)` (eq. 8), loss `L_DDPM = E||ε − ε̂_θ(x_t,t,y)||²` (eq. 7).
- Clean estimate from noise: `x0,ε,t = (x_t − √(1−ᾱ_t) ε_t)/√ᾱ_t` (eq. 9).
- Reference prior: `x0,E = E(y)` from a pretrained end-to-end CR net (MemoryNet or MSDA-CR) (eq. 11).
- Fusion: `x0,t = (1 − W) ⊙ x0,ε,t + W ⊙ x0,E` (eq. 13), W ∈ R^{C×H×W} from a small UNet ("WA") fed [x_t, y, x0,E] and t. W clipped to **[η, 1], η = 0.3** at inference (trained with η = 0).
- Step: `x_{t−1} = (√ᾱ_{t−1} β_t/(1−ᾱ_t)) x0,t + (√α_t (1−ᾱ_{t−1})/(1−ᾱ_t)) x_t + β̃_t z` (eq. 10).
- Training: CNP on 64 × 64 (¼ size, batch 64) to near convergence → train WA with CNP frozen, `L_WA = |x̃0 − x0,t|` with stop-gradient on x0,ε,t (eq. 14) → joint fine-tune at 256 × 256 (batch 16), `L = λ L_DDPM + L_WA`, λ = 1 (eq. 15). LR 1e-5; CNP 96 channels, WA 64 (Table VI). Inference 50 DDIM steps. One RTX 4090.
- Behaviour: mean W starts high and falls to near 0 by the last steps (Fig. 9): the reference net sets structure, diffusion adds texture.

## 3. Quantitative results (Tables IV, V, VII–X)
| CUHK-CR (4-band) | PSNR thin | SSIM thin | LPIPS thin | PSNR thick | SSIM thick | LPIPS thick |
|---|---|---|---|---|---|---|
| MemoryNet | 26.073 | 0.7741 | 0.0315 | 24.224 | 0.6838 | 0.0403 |
| MSDA-CR | 25.435 | 0.7483 | 0.0374 | 23.755 | 0.6661 | 0.0433 |
| DE-MemoryNet | 26.183 | 0.7746 | 0.0290 | 24.348 | 0.6843 | 0.0369 |
| DE-MSDA | 25.739 | 0.7592 | 0.0321 | 23.968 | 0.6737 | 0.0372 |
- DE adds ~0.1 dB to MemoryNet and ~0.3 dB to MSDA-CR on CUHK-CR. No variance, no significance test, one split.
- RICE (RGB): DE-MemoryNet 35.53 dB (RICE1), ~33.6 dB (RICE2) (Table IV).
- Resolution test (Table VII, MemoryNet, 128 px crops): train 1 m → test 0.5 m 22.58 dB; train 2 m → test 0.5 m 21.39 dB.
- Ablations on RICE2: learned WA vs fixed 0.5 blend +0.3 dB; coarse-to-fine +0.3–0.4 dB (Table IX).
- Cost: DE 36.8 M parameters, 12 FPS at 256 px (Table X).

## 4. Stated limitations
- Pure diffusion: "the textures generated only by the diffusion model often fail to precisely align with the actual scene since the diffusion model primarily focuses on learning the distribution of the entire image set rather than the pixel-level fine information." (p. 5) — said of pure diffusion, as the reason for the reference prior, not of DE.
- "reference model results might introduce inaccuracy" (p. 6); CUHK-CR results "generally less satisfactory compared to RICE" (p. 9).
- Not tested: other sensors, downstream tasks, change detection, uncertainty.

## 5. How to apply to our pipeline
- **Do not feed DE output to the flood/change detector.** It is a single-image generator: under cloud it draws plausible ground, so it can paint water away or invent it (consistent with evidence 05, "not recommended for scoring").
- **Usable without inventing content:**
  1. **Thin vs thick reported separately.** Every CUHK-CR metric is split by subset. Do the same for `sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym.either_date_dehaze`: report corrected roads (t ≥ T_MIN) and abstained/opaque roads (t < T_MIN) separately, never pooled. The paper never defines thin vs thick; our T_MIN = 0.2 cut is explicit, which is better practice — state it.
  2. **Near-date clear image as truth** (10–17 days). We have no post-event clear date, so not reproducible for us; `sn8_refhaze.haze_recovery` (synthetic haze on clear tiles) is our substitute.
  3. **Resolution matters** (Table VII): 1–2 m training loses 1.2–2.3 dB at 0.5 m. Supports native-0.5 m training/evaluation for `sn8_cloudspot` (HRC_WHU mixes 0.5–15 m).
  4. **Small reported gains** (~0.1–0.3 dB, one split, no significance): not evidence that diffusion beats a plain CNN at 0.5 m.
- **Feasibility:** CUHK-CR is 4-band Jilin-1 with NIR; ours is RGB uint8 used as grey, no flood scenes. Retraining needed; only sensible as a labelled "synthetic, display only" picture.

## 6. Key quotes
- "the outcomes obtained from pure diffusion models for CR are often inaccurate with undesirable fake textures" (p. 2)
- "the textures generated only by the diffusion model often fail to precisely align with the actual scene" (p. 5)
- "It is important to note that the detector fails to differentiate between thin and thick cloud layers." (p. 4)
- "models trained with low-resolution images yield less favorable results when tested on high-resolution datasets" (p. 11)
