# Coder handoff: You, Xu, Pan, Dong, Yang & Xia (2026), Change-aware multi-temporal cloud removal

- **Citation:** You, G., Xu, F., Pan, J., Dong, R., Yang, W., & Xia, G.-S. (2026). Change-aware multi-temporal cloud removal. *Science China Information Sciences* 69(3), 132306:1–132306:15. https://doi.org/10.1007/s11432-025-4669-x
- **PDF:** `/Users/jusrogers/Masters/papers/you2026_change_aware_multitemporal_cloud_removal_SCIS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded through Justin's GMU session (staging copy `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** real PDF (`file`: PDF document; 4.1 MB). Read tool and pdfinfo: 15 pages = article pages 132306:1–15 printed in the header. Page-1 title, all six authors and the DOI match the citation. Conclusion (§6, p. 14) and references 1–55 (pp. 14–15) present. PASS. (`file` metadata says 6 pages; ignored, as the checker rules say.)
- **Read:** pp. 1–15 in full (page images), including tables, figures and the reference list.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's (132306:n → p. n).

## 1. Method (CA-MTCR), step by step
Goal (p. 4, eq. 2): reconstruct the cloud-free optical image at the *current* step N from (I_opt^N, I_sar^N) plus historical pairs {(I_opt^i, I_sar^i)}, i = 1…N−1, treating history as references, not equal inputs.

1. **Per-date encoders** (eqs. 3–4, p. 4): F_opt^t = F_opt(I_opt^t), F_sar^t = F_sar(I_sar^t) for every t.
2. **Region-selective optical encoder** (pp. 5–6, Fig. 3): L = 9 Transformer blocks (p. 8). After each block j, two cloud cues:
   - R1 = spatial-attention output on the block output (cloud features give "abnormal responses");
   - R2 = cosine distance between block input and output (large where the block "fills" cloud).
   - Concatenate R1, R2 → channel attention (CAM) → conv → sigmoid → soft mask R; the block output is multiplied by R and added to the residual, so cloud features are suppressed before the next block.
3. **SAR encoder** (p. 6, eq. 9): 3 conv layers + 2 MBConv blocks, pre-trained as a VQ-VAE Noise2Noise despeckler on pairs of SAR images of the same scene from different dates: `L_pre = ||y2 − ŷ1||² + α||sg[z_e] − e_c||² + β||z_e − sg[e_c]||²`, α = 1, β = 0.1, 50 epochs, lr 2e-4 (p. 8). Pairs drawn from dates "with minimal temporal variation". Only the encoder is kept, then fine-tuned at lr 1e-5.
4. **Multi-modal fusion per date** (eq. 5, p. 6): concat(F_opt^t, F_sar^t) → conv → MBConv = F_f^t.
5. **Change information from SAR only** (eq. 10, p. 6): per location, `c^t = <F_sar^t, F_sar^N> / (||F_sar^t|| ||F_sar^N||)` for t < N; `c^N = 1`. High cosine similarity = low change likelihood.
6. **Change-aware fusion** (eqs. 11–12, p. 6–7, Fig. 4): `{W^t} = Attn({Conv(c^t || F_f^t)})` with L-TAE temporal attention; `F_c = Σ_t F_f^t ⊙ W^t`. This is a **soft per-location weighting of all dates**, not a hard choice of dates.
7. **Decoder** H_d(F_c) → Î_opt^N (eq. 8).
8. **Loss** (eqs. 13–16, p. 7): `L = λ1·L1 + λ2·L_fr + λ3·L_sr`, λ = 2.0, 1.0, 250.0 (p. 8). L_fr = L1 of VGG16 features (relu1_1…relu5_1); L_sr = Gram-matrix (style) loss.
9. **Training** (p. 8): PyTorch, 2× RTX 3090, batch 6, 30 epochs, Adam lr 1e-4, halved every 5 epochs after epoch 10.

## 2. Inputs, outputs, data needs
- **Needs, for every date:** Sentinel-2 multispectral optical (clipped to [0, 10000], scaled to [0, 1]) **and** a co-registered Sentinel-1 SAR image (clipped to [−25, 0] dB, scaled to [0, 1]) (p. 8). The change signal comes only from SAR (eq. 10). Without SAR the model drops to 29.84 dB (Table 3, p. 13), i.e. no better than the plain multi-temporal baselines.
- **Training data:** SEN12MS-CR-TS (53 ROIs; 10,176 / 1,410 / 3,716 train/val/test 256 × 256 patches, 30 dates each) and AllClear 3.4% subset (10,176 train / 1,500 val / 2,735 test, 4 consecutive dates) (p. 8). Supervised: needs a cloud-free target near the target date.
- **Auxiliary dates are chosen at random** from the remaining dates (SEN12MS-CR-TS) or are the AllClear neighbours (p. 8). The method never selects dates itself.
- Output: one reconstructed 10 m Sentinel-2 image for the target date.

## 3. Quantitative results to compare against (Table 1, p. 9)
| Method | SEN12MS-CR-TS PSNR / SAM / SSIM / MAE | AllClear PSNR / SAM / SSIM / MAE |
|---|---|---|
| HDRSA-Net (best mono-temporal) | 30.76 / 5.60 / 0.903 / 0.022 | 31.00 / 7.74 / 0.888 / 0.028 |
| UnCRtainTS (best multi-temporal) | 29.76 / 6.75 / 0.900 / 0.024 | 33.41 / 5.49 / **0.925** / 0.021 |
| CA-MTCR | **31.79 / 5.18 / 0.903 / 0.019** | **34.21 / 4.85** / 0.921 / **0.018** |

- The abstract's "about 2.0 dB" on SEN12MS-CR-TS is **over UnCRtainTS** (31.79 − 29.76 = 2.03); over the best method in the table (HDRSA-Net, mono-temporal, SAR-assisted) the gain is 1.03 dB, and SSIM is tied at 0.903. On AllClear CA-MTCR is not best on SSIM.
- Ablation (Table 2, p. 10): baseline 29.97; without the change term ("w/o CA") 30.16; without region selection 31.62; full 31.79. So the SAR change term is worth 1.63 dB, the region-selective encoder 0.17 dB.
- Temporal offset (Fig. 7a, p. 12): UnCRtainTS and "w/o CA" fall from about 31 dB at offset 1 to about 28–28.5 dB at offset 13; CA-MTCR stays at about 31.4–31.9 dB.
- SAR at 1/5 and 1/10 resolution: 31.68 and 31.63 dB (Table 3, p. 13).
- 8.45 FPS on one RTX 3090 (p. 13). 7.45 M parameters, 456.57 GFLOPs (Table 1).
- No significance tests, no repeated runs, no per-land-cover breakdown; "rapid land cover change" is shown only as two qualitative scenes (Fig. 8, pp. 12–13).

## 4. Stated limitations
- With full cloud on every optical date the output relies on SAR and "inevitably" loses spectral fidelity (pp. 12–13).
- SAR "lack[s] spectral information", so it is used for structure and change, and spectral detail comes from optical history (pp. 3, 9).
- Speckle causes mottled artefacts in homogeneous areas for the baselines; the pre-trained SAR encoder is their fix (pp. 9–10).

## 5. How to apply to our pipeline
- **Direct use: not feasible.** We have one RGB/grey 0.5 m Maxar before date, one cloudy after date, no SAR, no NIR/SWIR, no 30-date series and no cloud-free target on the after date. The method's change cue is SAR-only (eq. 10), and it is trained on 10 m Sentinel-2.
- **Idea we can borrow (arm, not a port):** per-location change weight between dates computed as the **cosine similarity of feature vectors** (eq. 10), used as a soft weight on how much to trust the before date. We could compute it from DINOv2 patch features of before vs after **outside the cloud mask only** (inside the cloud the after features are corrupted, which is exactly why the paper uses SAR there). Inside cloud it gives nothing; it is a boundary/context prior at best. Label it "our adaptation of eq. 10", not their method.
- **Region-selective idea** (R2, p. 6): the cosine distance between a block's input and output tokens marks where the network is "filling" cloud. Analogous diagnostic for us: cosine distance between DINOv2 features of hazy vs dehazed after-image patches as a "how much did dehazing change this patch" map. Cheap; numpy only.
- **Confirms our gap statement:** the paper's own framing (p. 3) is that pixel-replacement temporal methods are "unreliable in regions characterized by frequent cloud cover or by rapid land cover changes", and its fix needs a sensor that sees through cloud on every date. Nothing here handles one grey band plus a clear before date.
- **Evidence weight:** venue Sci. China Inf. Sci. (JIF stated as 8.1 in our notes; not re-checked here). Results are benchmark averages on Sentinel-2, no significance testing.

## 6. Key quotes
- "existing multi-temporal cloud removal methods fail to account for inconsistencies in data collected at different times (e.g., seasonal variations, human activities, meteorological events, etc.), resulting in severe performance degradation when surface changes occur" (abstract, p. 1).
- "the greater the cosine similarity, the lower the likelihood of significant changes between the time steps" (p. 6).
- "Additional time steps are randomly selected from the remaining time steps to serve as auxiliary data" (p. 8).
- "historical optical imagery provides reliable cues for reconstruction in unchanged regions, whereas only regions undergoing changes rely on SAR imagery to approximate spectral and textural attributes" (p. 3).
- "removing change awareness results in a noticeable performance decline, with a drop of 1.63 dB in PSNR" (p. 11).
