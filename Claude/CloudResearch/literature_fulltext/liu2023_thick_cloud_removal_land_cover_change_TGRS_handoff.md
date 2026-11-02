# Coder handoff: Liu, Huang & Cai (2023), Thick cloud removal under land cover changes using multisource satellite imagery and a spatiotemporal attention network

- **Citation:** Liu, H., Huang, B., & Cai, J. (2023). *IEEE Transactions on Geoscience and Remote Sensing* 61, 5601218 (18 pp.). https://doi.org/10.1109/TGRS.2023.3236106
- **PDF:** `/Users/jusrogers/Masters/papers/liu2023_thick_cloud_removal_land_cover_change_TGRS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document, version 1.4; 61.15 MB (image-heavy figures); 18 pages (Read tool and pdfinfo); page-1 title, authors (Hao Liu, Bo Huang, Jiajun Cai), TGRS vol. 61, 2023, article 5601218 and DOI 10.1109/TGRS.2023.3236106 match todo.tsv; Conclusion (pp. 16–17), References [1]–[60] (pp. 17–18) and biographies present. PASS. (pdfinfo Title is the typesetter's proof filename; ignored.)
- **Read:** PDF pp. 1–18 = article pp. 1–18 in full (Read tool, page images), including Tables I–IX and Figs. 1–11.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's page numbers (1–18).

## 1. Algorithm, step by step
Notation (pp. 3–4): S2_0 = auxiliary cloud-free Sentinel-2 image ("months-long temporal intervals", p. 3); S2_1 = cloudy target Sentinel-2 image; S2_1C = S2_1 with all cloud pixels masked out; S3 = auxiliary Sentinel-3 OLCI image "near the target date" (p. 3); S2_0H = high-pass of S2_0.

1. **Cloud detection** (p. 4): Fmask [51] gives a binary mask (cloud/shadow = 1, clear = 0). "the cloud and cloud shadow dilation pixels and cloud probability are set as 4 and 0 in the experiment, respectively, to improve the detection recall." Misdetected cloudy pixels "are treated as ground truth and thus can introduce errors into the adjacent reconstruction" (p. 4).
2. **Simulated cloud masks for training** (p. 4): one Fmask mask from S2 tile T49QGF, 24 Feb 2020, 30% cloud; rotated 90° counterclockwise; 150 random 512 × 512 patches cropped ("30 of them have a percentage of 100%"); each rotated by a random angle and resized to 256 × 256. The same mask set is used for all training.
3. **Patch traversal** (p. 3, Fig. 1): a moving window over the cloud mask; clear patches → training set (with simulated masks); cloudy patches → testing set.
4. **Inputs to STAN** (p. 4–5): two groups concatenated in the channel dimension: (S2_0, S3) and (S2_1C, S2_0H). Laplacian high-pass: 3 × 3 kernel, centre 4, four vertical/horizontal neighbours −1, rest 0 (p. 5). The paper does not state how S3 is resampled to the S2 grid.
5. **Network** (p. 5, Figs. 3–4):
   - Double convolution module per branch: two 3 × 3 conv layers to 64 channels, ReLU.
   - Dual attention module (PAM + CAM, after [55]) on features downsampled by a factor of 8; Q, K, V by depthwise + pointwise conv; h = H/8, w = W/8, c = C/4 (eqs. 1–3, p. 5).
   - PAM (eq. 4): `PAM = X + reshape(softmax(Q_P × K_P) × V_P)`.
   - CAM (eqs. 5–8, p. 6): Q_C, K_C, V_C are reshapes of X; `CAM = X reshape(softmax(Q_C × K_C) × V_C)` (as printed).
   - Combination (eq. 9, p. 6): `Y = X + upsample(α × PAM(X) + β × CAM(X))`, α and β learnable, initialised to 0.
   - Branch outputs fused, then eight residual convolution modules [54]: 1 × 1 conv to 32, 3 × 3 conv, 1 × 1 conv back to 64; all except the first and last add the input as a residual (p. 5).
   - Output = cloudy-image branch features + residual features → final double conv → B bands (p. 5). No max-pooling; everything except the attention runs at full resolution.
6. **Training** (pp. 7–8): Adam, β1 = 0.9, β2 = 0.99, ε = 0.00001 (as printed); initial learning rate 0.001; batch size 8; L1 loss; PyTorch 1.7, fastai 1.0, i9-10900 CPU, 128 G memory, RTX 3090. Training/testing patches cropped with stride 48 and 256 → 19 898 and 1776 patches of 256 × 256. Pretraining and fine-tuning both 40 epochs. Simulated: train on clear regions, test on (simulated) cloudy regions per case. Real: fine-tune on the clear regions of each real cloudy image.
7. **Thin cloud and shadow** (p. 13): "all cloud shadows, thin clouds, and thick clouds were treated as thick clouds in this framework". Thin-cloud pixels are discarded and regenerated, not corrected.
8. **Metrics** (eqs. 10–13, p. 8): RMSE, CC, PSNR on cloudy pixels; SSIM over all pixels (k1 = 0.01, k2 = 0.03).

## 2. Inputs, outputs, data needs
- Sentinel-2 L1C, 10 m bands B2, B3, B4, B8 (20 m bands B2–B8a only for the bandwise test, Table IV) and Sentinel-3 OLCI bands matched by wavelength to B2–B8a (Table I, p. 7). S3 resolution ~300 m, revisit ~1 day (p. 6).
- Cases (Table II, p. 7): Paris T31UDQ (S2 2020/09/17, 2021/03/06, 2020/11/06 real cloudy; S3 2020/03/06 and 2020/11/05 as printed), Tianjin T50SMJ, Darlag T47SPT, Xi'an T49SCT. Simulated pairs IDs 1–2, 4–6, 7–8, 10–11; real tests 1–3, 4–6, 8–9, 11–12.
- Unseen-image tiles (Table VII, p. 14): T31UEQ, T50SPJ, T47SQT, T49SCU (geographically adjacent, same dates and S3).
- Needs: one clear reference S2 date, the cloudy target, **a cloud-free S3 image near the target date**, and enough clear pixels in the target scene to train/fine-tune.
- Output: cloud-free Sentinel-2 image (all masked pixels regenerated).

## 3. Quantitative results
Units: RMSE as printed on the Sentinel-2 L1C values (scale not stated). Baseline = "simply replacing the cloudy areas in S2_1 with the same areas in S2_0" (p. 9). `*` = with S3.
- **Simulated, Table III (p. 9), average over cases 2, 6, 8, 11:**
  - RMSE: Baseline 528.881; ResUnet 300.780 / ResUnet* 199.873; CRN 257.381 / CRN* 202.548; STS-CNN 290.087 / STS-CNN* 195.557; DSen2-CR* 189.505; STAN 179.923.
  - CC: Baseline 0.904; STAN 0.988. SSIM: Baseline 0.952; STAN 0.978. PSNR: Baseline 25.977; STAN 35.077; DSen2-CR* 34.613.
  - Per case STAN RMSE: 168.247 (2, Paris), 204.807 (6, Tianjin), 218.407 (8, Darlag), 128.230 (11, Xi'an); Baseline 501.176, 586.226, 731.258, 296.865.
- **Bandwise, Table IV (p. 9):** near-infrared and red-edge bands have larger errors than visible bands (e.g. STAN case 2: B2_10 71.13, B8_10 282.21).
- **Ablation, Table V (p. 13), Paris:** original 168.247 RMSE; without all three dual-attention modules 187.727; without residual learning 170.125; without high-pass 169.041.
- **S3 date, Table VI (p. 14), Paris:** RMSE 185.769 (S3 2021/02/24), 168.247 (2021/03/06, same day as target), 192.923 (03/23), 188.685 (03/29), 211.375 (04/22, 47-day gap). Table note gives the S2 dates as "2020/09/01 and 2020/03/06", which disagrees with Table II (2020/09/17, 2021/03/06): a printed inconsistency.
- **Unseen images, Table VIII (p. 15), averages:** RMSE Baseline 1162.141; STAN 376.642; STAN_t (fine-tuned) 278.141. PSNR Baseline 22.018; STAN 29.884; STAN_t 32.473. Case 18 (Darlag): Baseline 3097.060, STAN_t 581.985.
- **Training-size, Table IX (p. 15):** case 2 RMSE 177.671 with 10% of training data vs 168.247 with 100%.
- **Real cloudy images (Fig. 8, p. 12–13):** visual only; no ground truth.
- No significance tests, no change-detection or classification evaluation of the reconstructed images.

## 4. Stated limitations
- "The major limitation of the proposed approach is the necessity of the near-target-date cloud-free Sentinel-3 image for the temporal features that affect the land cover change information reconstruction." (p. 17)
- "the large spatial resolution gap between the Sentinel-3 and Sentinel-2 data makes it difficult for small objects to be accurately generated" (p. 17); Tianjin parcels "are too small to be distinguished in the S3 image" (p. 13).
- Fmask misses are treated as ground truth and spread error (p. 4).
- With the S3 from 22 Apr 2021 the output "shows some undesired land cover changes that correspond to the S3" (p. 16).
- NIR/red-edge bands carry more error than visible bands (p. 10).

## 5. How to apply to our pipeline
- **What it confirms.** Without a near-date source "the networks are blind to the temporal changes, so that only homogeneous changes can be generated" (p. 11). The no-S3 variants (ResUnet, CRN, STS-CNN) are the closest analogue of what we could run with one pre-storm date plus the clear part of the post-storm image, and their average RMSE was higher than their S3 versions' (300.780 vs 199.873, 257.381 vs 202.548, 290.087 vs 195.557; Table III). The paste-from-reference baseline, which is our "fill from the before date", was worst everywhere (528.881 vs 179.923). This supports our evidence-05 position: under cloud, a flood cannot be recovered from the pre-storm image; such pixels should abstain (CANNOT ASSESS), not be filled.
- **The S3 role does not transfer to our case.**
  - The guide must be cloud-free near the target date. Sentinel-3 OLCI is optical; under a hurricane cloud deck it is cloudy on the same days as Maxar. Liu et al. never test a cloudy S3.
  - Resolution gap: 300 m S3 → 0.5 m Maxar is ~600×, vs 30× in the paper, where parcels smaller than one S3 pixel were already lost (p. 13). Flooded streets and yards are far below 300 m.
  - Table VI tolerates a 47-day S3 gap for crop/snow change; a flood changes within days and recedes, so a weeks-off guide would show the wrong state.
  - The paper needs 4 bands including NIR (B8) and is trained per scene; we have RGB/grey uint8 only. RGB-only operation is not tested.
- **Clear-region fine-tuning** (Table VIII) is the transferable training idea: learn the pre→post mapping on the clear part of the same post-storm tile. Our `tone_curve` quantile fit on clear pixels already does the global version of this; the paper gives no evidence that a learned version recovers localised change (it recovers only "homogeneous" change).
- **Thin cloud:** treated as thick and discarded (p. 13), so the paper offers nothing for our haze/thin-cloud correction arms.
- **No new bench arm proposed.** No step is runnable on our data without a cloud-free near-date second source, and the parts that are runnable (pre-date paste, clear-region tone/mapping fit) are already C0 / existing arms. If a cloud-free near-date guide ever exists for an event (e.g. a NOAA aerial pass), it is our evaluation reference and cannot also be an input without leaking.

## 6. Key quotes
- "temporal-based methods normally assume that the land cover during the temporal intervals between the cloudy and auxiliary images (which should be as short as possible) is stable [42]." (p. 2)
- "Although SAR images contain information corresponding to the exact target date, they suffer from speckle noise and the lack of sufficient spectral information to reconstruct optical features." (p. 3)
- "In the cases without the Sentinel-3 data, the networks are blind to the temporal changes, so that only homogeneous changes can be generated." (p. 11)
- "the more heterogeneous and unpredictable the land cover changes, the more significant the contribution of the temporal Sentinel-3 data to image reconstruction." (p. 10)
- "all cloud shadows, thin clouds, and thick clouds were treated as thick clouds in this framework." (p. 13)
- "The major limitation of the proposed approach is the necessity of the near-target-date cloud-free Sentinel-3 image" (p. 17)
