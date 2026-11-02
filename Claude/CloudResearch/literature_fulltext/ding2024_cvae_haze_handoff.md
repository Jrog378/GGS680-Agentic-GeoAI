# Coder handoff: Ding, Xie, Qiu, Zhang & Shi (2024), Robust haze and thin cloud removal via conditional variational autoencoders

- **Citation:** Ding, H., Xie, F., Qiu, L., Zhang, X., & Shi, Z. (2024). *IEEE Transactions on Geoscience and Remote Sensing* 62, 5604616 (pp. 1–16). https://doi.org/10.1109/TGRS.2024.3349779
- **PDF:** `/Users/jusrogers/Masters/papers/ding2024_cvae_haze-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 6.30 MB; 16 pages (Read tool and pdfinfo) = article 5604616 pp. 1–16; page-1 title, authors (Haidong Ding, Fengying Xie, Linwei Qiu, Xiaozhe Zhang, Zhenwei Shi; Beihang University), TGRS vol. 62 2024 and DOI 10.1109/TGRS.2024.3349779 match todo.tsv; Conclusion (p. 13), 102-item reference list (pp. 13–15) and biographies (pp. 15–16) present. PASS.
- **Read:** PDF pp. 1–16 = article pp. 1–16 in full (Read tool, page images), including Tables I–IX and Figs. 1–12.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's (1–16).
- **Venue / JIF rule:** IEEE TGRS, above 4 (approx. 7–8; general knowledge, not checked against JCR).
- **Precursor:** "This article presents an expanded version of our previous conference paper [32]" (p. 2): Ding, Zi & Xie, "Uncertainty-based thin cloud removal network via conditional variational autoencoders", ACCV 2022, pp. 469–485 (ref. 32, p. 14).

## 1. Algorithm, step by step
1. **CVAE objective** (eq. 1, p. 4): `log P(Y|X) ≥ −D_KL(Q_φ(z|X,Y) || P_θ(z|X)) + E_Q[log P_ω(Y|X,z)]`. Prior net P_θ(z|X), posterior net Q_φ(z|X,Y), restoration net P_ω(Y|X,z).
2. **Prior/posterior nets** (p. 4–5, Fig. 2): stacks of Conv3×3 + BN, then GAP, then two FC heads for μ and σ; axis-aligned Gaussian `z ~ N(μ, diag(σ²))`; **latent dimension N = 9** (p. 4). Reparameterisation `z = μ + σ·ε`, ε ~ N(0, I) (eq. 2, p. 5). Train: z from the posterior; test: z from the prior (p. 5).
3. **Restoration net** (p. 5, Fig. 2): MIMO U-shape, three encoders taking the image at full, 1/2 and 1/4 scale and three decoders with 3 × 3 output convs. **N = 3 ResBlocks** per encoder/decoder. Downsampling by stride, upsampling by transpose conv. z is concatenated at the bottleneck (Fig. 2).
   - ResBlock (Fig. 2(b)): Conv3×3–ELU–Conv3×3; channel attention (GAP, Conv1×1–ELU–Conv1×1, sigmoid); spatial attention (Conv1×1 + sigmoid, map [1, H, W]).
   - **SFFM** (eqs. 3–5, p. 5): `h = NL(GAP(F^e + F^d))`, reduction **r = 8**; two FC layers give E^c, D^c; per-channel softmax weights; `F* = w^e·F^e + w^d·F^d`.
4. **Dynamic fusion network** (eqs. 6–7, p. 6, Fig. 4): concatenate **n = 6** sampled outputs Ỹ ∈ R^{nC×H×W}. Feature branch: shallow layer + two ResBlocks give Ỹ_r ∈ R^{C'×H×W}. Kernel branch: `K_i = FC_i(σ(NL(GAP(Ỹ))))`, one FC per output channel R, G, B, reshaped to [C', k, k], **k = 3**. Output `Y* = K ⊛ Ỹ_r`.
5. **Losses** (eqs. 8–12, pp. 6–7):
   - Stage 1: `L = β·D_KL + L_rec`, **β = 1.0**; `L_rec = L1 + λ1·L_fre`, **λ1 = 0.1**; `L1 = Σ_s ω_s ||Ŷ_s − Y_s||₁`, `L_fre = Σ_s ω_s ||F(Ŷ_s) − F(Y_s)||₁` (FFT), **ω = [1.0, 0.3, 0.1]** over the 3 scales.
   - Stage 2: freeze the prior, posterior and restoration nets; generate DFN training data by repeated random sampling; `L_dfn = ||Y* − Y||₁ + λ1 ||F(Y*) − F(Y)||₁` (eq. 12).
6. **Training** (p. 7): PyTorch; Intel Xeon 6252 + **NVIDIA A100**; Adam β1 = 0.9, β2 = 0.999; lr **1e-4 → 1e-6** cosine; **batch 16**; random **256 × 256** crops. Stage-1 epochs: 300 (T-CLOUD), 1000 (RICE-I, SateHaze1k), 50 (RS-Haze). Stage-2 epochs: 50, 300, 15 respectively.

## 2. Inputs, outputs, data needs
- Input: one degraded RGB image (also tested on single coastal and NIR bands, Table III). Output: one fused RGB image. No transmission, thickness or uncertainty map is output.
- Training data: paired degraded/clear images (Table I, p. 6): T-CLOUD 2,351 train / 588 test, 256 × 256, real; RICE-I 400 / 100, 512 × 512, real (Google Earth); WHUS2-CR 4,000 / 1,000, 256 × 256, real (Sentinel-2A); SateHaze1k 960 / 135, 512 × 512, synthetic (320 train, 35 val, 45 test per level, p. 7); RS-Haze 51,300 / 2,700, 512 × 512, synthetic.
- **T-CLOUD** (new, p. 7): 2,939 Landsat 8 RGB pairs, cloudy and clear one revisit apart (16 days), chosen for similar lighting, 256 × 256; split 8:2. The authors note "illumination noise is inevitable" (p. 7).
- **Code/weights:** the paper gives **no code, weights or dataset URL** (none found on any page; the biography of Z. Shi gives the lab site levir.buaa.edu.cn, p. 16).
- Size: **5.91 M parameters, 34.40 GFLOPs** (Table II, p. 8).

## 3. Quantitative results
- Table II (p. 8), PSNR / SSIM / CIEDE2000: **T-CLOUD 31.52 / 0.8893 / 3.6275**; **RICE-I 36.29 / 0.9671 / 1.8316**; **WHUS2-CR 30.23 / 0.9303 / 4.1672**. The next best on T-CLOUD is MSAR-DefogNet, 28.84 / 0.8432 / 4.1862: "gains of 2.68 dB in PSNR and 0.0461 in SSIM" (p. 9). On WHUS2-CR the gain is "0.34 dB in PSNR and 0.0135 in SSIM" (p. 9).
- Table III (p. 9): coastal band 32.04 / 0.8798; NIR band 23.08 / 0.7744 (best in both).
- Table IV (p. 11), PSNR / SSIM: SateHaze1k thin 27.36 / 0.9293, moderate 28.37 / 0.9566, thick 22.83 / 0.8518, average 26.19 / 0.9126; RS-Haze 39.52 / 0.9706. DCP [16]: SateHaze1k average 11.06 / 0.6477, RS-Haze 17.86 / 0.7340.
- Ablations on T-CLOUD at half the training rounds (p. 11): z = 3 / 6 / 9 / 12: 28.72 / 29.20 / **29.63** / 29.07 dB (Table V). Fusion: average of samples 28.12, SFN 28.96, DFN **29.63** (Table VI). Loss: L1 29.37, MSE 28.73, L1 + L_fre **29.63** (Table VII). Aggregation: concat 27.76, sum 27.94, SFFM **29.63** (Table VIII). Without attention 25.03, without MIMO 27.51, full **29.63** (Table IX, p. 13).
- No error bars, no repeated runs, no significance tests.

## 4. Stated limitations
- "an inherent drawback lies in the increased computational load due to multiple samplings" (p. 13).
- T-CLOUD pairs are 16 days apart; "The presence of illumination noise is inevitable due to changes in ambient light" (p. 7). Real change between the pair dates is not discussed.

## 5. How to apply to our pipeline
- **Feasibility: low for now; no bench arm proposed.**
  - No released weights or code are stated, so we would have to reimplement and train. Training on an A100 took 300–1000 epochs; on our MPS/CPU that is days per dataset (an estimate, not measured).
  - Training pairs: the published sets are 30 m Landsat (T-CLOUD), Google Earth (RICE-I), 10 m Sentinel-2 (WHUS2-CR) and synthetic haze. None is 0.5 m Maxar. SpaceNet 8 pre/post pairs contain the flood itself, so training on them would teach the net to remove flood change as "haze". This breaks our labelled-data-only and no-hallucination rules.
  - Not change-aware; single-image. It outputs no transmission or confidence map for our t ≥ 0.2 gate.
  - Grey: Table III shows it works per single band after retraining on that band, so a grey retrain is plausible in principle.
- **The "sample spread as uncertainty" idea (evidence 19 item 10, preregistration) is ours, not Ding's.** Ding draws n = 6 samples and fuses them. It never measures their spread, never maps it per pixel and never tests it against error. Its own ablation shows that plain averaging of the samples is the worst fusion (28.12 dB, Table VI). Keep the optional spread check, but cite Ding only as "multiple plausible restorations exist", not as the source of a spread-based confidence.
- If a learned remover is ever wanted, a 5.91 M-parameter, 34.4 GFLOP model is small enough to run inference on our hardware. The blocker is training data at our resolution, not compute.

## 6. Key quotes
- "image restoration is a highly ill-posed problem, as the sharp pixel value corresponding to the input cannot be uniquely determined solely from the degraded image" (abstract, p. 1)
- "In this uncertainty pipeline, we can generate a more accurate restored image based on these multiple predictions." (abstract, p. 1)
- "where n = 6 is the number of samples" (p. 6)
- "Both training and test sets are from Landsat 8 RGB images. Our dataset contains 2939 doublets of cloud images and their clear counterparts separated by one satellite reentry period (16 days)." (p. 7)
- "However, an inherent drawback lies in the increased computational load due to multiple samplings." (p. 13)
