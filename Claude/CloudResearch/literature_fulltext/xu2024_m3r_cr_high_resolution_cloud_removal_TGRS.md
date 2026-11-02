# Coder handoff: Xu et al. 2024, M3R-CR / Align-CR (IEEE TGRS 62)

**Citation:** Xu, F., Shi, Y., Ebel, P., Yang, W., & Zhu, X. X. (2024). Multimodal and multiresolution data fusion for
high-resolution cloud removal: A novel baseline and benchmark. *IEEE TGRS* 62, 1–15. doi:10.1109/TGRS.2023.3337845
**Copy read:** arXiv:2301.03432v2 (11 Oct 2024), 15 pp, author version; page range matches the published 1–15.
PDF: `/Users/jusrogers/Masters/papers/xu2024_m3r_cr_high_resolution_cloud_removal_TGRS-summary.pdf` (page 1 = AI summary,
so paper page n = PDF page n+1). **Read:** pp. 1–15, all. Written by Claude, 2026-10-29.

## What it is
A benchmark (780 areas, PlanetScope 3 m cloudy + clear, Sentinel-1 10 m, WorldCover labels) and a SAR-guided deep
cloud remover (Align-CR). The part we can use is the **evaluation protocol**, not the network.

## Evaluation protocol (the part to copy)
1. **Pairs:** cloudy and cloud-free PlanetScope L3B TOA images, "average time interval … is 2.8 days" (p. 5). Nuisances
   (sun, geometry, humidity, landscape change) are "considered largely negligible" at large sample size (p. 4). No
   explicit cloudy-to-clear co-registration beyond orthorectification; the loss is made robust instead (below).
2. **Preprocessing:** optical clipped to [0, 10000] then /10000; S1 VV clipped [−25, 0], VH [−32.5, 0], scaled to
   [0, 1] (p. 7).
3. **Pixel metrics:** MAE and PSNR (reconstruction error), SAM and SSIM (spectral/structural), with MAE and SAM split by
   the 6 land-cover classes (Table II, p. 8–9). The split by class is possible only because of the WorldCover map.
4. **Downstream ("semantic recovery") test, p. 10–11:**
   - Train DeepLabv3+ (ResNet-50) on the **cloud-free** images with WorldCover labels (same train/test split).
   - Run it on three inputs: cloud-free, cloudy, and each method's reconstruction.
   - Score each against **WorldCover** with mIoU and pixel accuracy, per cloud-cover bin (0–20 … 80–100 %) and overall
     (Table III). "the closer they are to the results with the cloud-free images as input, the better" (p. 11).
   - Fig. 6 plots the *difference in mIoU/PA* between cloud-free input and each method (lower is better).
   - **Important nuance:** the score is each input's accuracy against an independent label map, then compared with the
     cloud-free input's score. It is **not** a pixel-wise agreement between the predictions on the reconstruction and
     the predictions on the cloud-free image. Our Revision-1 outcome (per-road agreement with the detector's calls on
     the NOAA image) is a direct-agreement variant: cite it as "after M3R-CR", not as the same metric.
5. **NDVI check (p. 12):** RMSE of NDVI vs cloud-free, and mIoU of 5 NDVI classes with cloud-free NDVI classes as the
   reference. Here the cloud-free image's own output *is* the reference (closer to our agreement idea). Needs NIR: not
   for us.

## Align-CR (for completeness; not implementable on our data)
- Residual learning: output = cloudy image + learned residual (long skip). SAR upsampled (nearest neighbour) to 3 m.
- D = 6 AlignFuse blocks: alignment = pyramid-cascading-deformable convolution (PCD) predicting offsets
  Δp = H_offset(F_opt, F_sar), F̂_sar = DConv(F_sar, Δp) (Eqs. 6–7); fusion = SAR-guided global context (Swin layer) +
  SAR-based local feature compensation.
- Loss (Eq. 8): L = (1 + w·M) ⊙ ((y − ŷ)² + ε²)^α, M = cloud mask (Planet UDM), w = 5, ε = 1e-3, α = 0.45. Charbonnier
  "better handle[s] outliers" from the imperfect near-date target (p. 7).
- Training: Adam, 30 epochs, lr 1e-4 (1e-5 for alignment blocks), halve every 5 epochs after 10; 160×160 crops,
  batch 12, 2×RTX 3090.

## Quantitative results we could cite (no significance tests; ± over runs)
- PSNR: Align-CR 30.54, GLF-CR 30.00, DSen2-CR 28.86, no-SAR variant 29.73 dB; SSIM 0.914 (Table II).
- Downstream overall mIoU / PA: cloud-free 43.24 / 64.66; cloudy 11.72 / 21.46; Align-CR 30.63 / 46.02; GLF-CR
  29.34 / 43.69 (Table III).
- **Rank flips (p. 11):** SAR-Opt-cGAN beats McGAN and SpA GAN on every visual metric but scores lower downstream
  (mIoU 10.19 vs 13.42 / 16.01). Align-CR beats w/o-Align on every visual metric but loses mIoU at 80–100 % cloud
  (23.29 vs 24.59). "the metrics for measuring the visual recovery quality can not adequately reflect the performance of
  cloud removal methods in terms of semantic recovery" (p. 11).
- Even the cloud-free input gets only 43 % mIoU against WorldCover (10 m, ~75 % accurate, p. 5): the reference labels
  are noisy, so absolute numbers are low; only the comparison across inputs is meaningful.

## Stated limitations
- Near-date reference is not perfect truth (p. 4, p. 7). "there remains a significant discrepancy between the predicted
  cloud-free images and their corresponding real cloud-free images" (p. 11). Urban areas are hardest. L1-type losses
  push toward over-smoothing and loss of semantics (p. 11).

## How to apply to our pipeline / Ida test
- **Pre-registration Revision 1 item 1 (call-level outcome):** keep it, but add M3R-CR's *own* form as a second number
  so the citation is exact: for each arm, the detector's per-road accuracy against an independent label (SpaceNet 8
  flood labels on clear roads only, where they are valid) next to the NOAA-input accuracy; plus our direct agreement
  (per-road calls on arm vs calls on NOAA). Report both; state that the agreement version is our adaptation.
- **Report per cloud-cover bin**, as Table III does: bin cloudy roads by strip cloud share (e.g. 0–20 … 80–100 %) in
  `sn8_cloudsym.either_date_handling` output, and show the arm gap per bin. This is cheap and matches the paper's design.
- **Per-class split:** report outcomes 1–3 separately for road strip / building / tree / water pixels (our analogue of
  their land-cover split), which also covers Revision 1 item 5.
- **Rank-flip check:** compute both grey error (outcome 7) and the call-level outcome per arm and print whether they
  rank arms the same way. Do not choose an arm on grey error (Revision 1 item 2).
- **Robust loss idea:** if any de-hazing parameter is ever fitted against the NOAA image, use a Charbonnier/Huber-type
  robust error, not L2, because the 0–2-day reference has real differences.
- **Feasibility:** protocol fully feasible (RGB→grey, 0.5 m, one clear pre date). Align-CR itself: not feasible (needs
  co-temporal SAR and training data; 43.5 M parameters).
- Modules: evaluation code only (a new Ida scoring script that calls `sn8_cloudsym.either_date_dehaze`,
  `sn8_clouds.dehaze`, and the frozen production road detector). No change to `sn8_cloudsym.py`/`sn8_clouds.py` logic.
