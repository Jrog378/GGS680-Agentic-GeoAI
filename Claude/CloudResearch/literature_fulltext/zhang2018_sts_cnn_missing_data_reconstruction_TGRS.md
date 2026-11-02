# Coder handoff: Zhang, Yuan, Zeng, Li & Wei (2018), STS-CNN missing-data reconstruction

- **Citation:** Zhang, Q., Yuan, Q., Zeng, C., Li, X., & Wei, Y. (2018). Missing Data Reconstruction in Remote Sensing Image With a Unified Spatial–Temporal–Spectral Deep Convolutional Neural Network. *IEEE TGRS* 56(8), 4274–4288. https://doi.org/10.1109/TGRS.2018.2810208
- **PDF:** `/Users/jusrogers/Masters/papers/zhang2018_sts_cnn_missing_data_reconstruction_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/1802.08369 ("To be published in IEEE TGRS", Word 2016, 22 Feb 2018). Pages numbered 1–14 below are the preprint's, not the journal's 4274–4288 (15 pages).
- **Validation:** `file` = PDF, 2.55 MB; 14 pages (Read tool; pdfinfo agrees); title and five authors match Crossref; Conclusions (p. 13) and 50 references (pp. 13–14) present. 14 preprint pages vs 15 journal pages is the expected layout difference. PASS (preprint version).
- **Read:** pp. 1–14 in full, including every figure and table (pp. 4–6, 8–9, 11–13 rendered as images to check the architecture, masks and tables); references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§III, Figs. 3–9, pp. 4–6)
Inputs: y1 = the image with missing pixels ("spatial data"), y2 = the auxiliary image, mask. For cloud, "input y1 is a temporal image with regions covered by thick cloud, and input y2 is another temporal image without cloud" (p. 5).
```
f1 = Conv3x3(y1, 30); f2 = Conv3x3(y2, 30); f = concat(f1, f2)          # 60 maps (Fig. 4)
f = Conv3x3(f, 60)
m = concat(Conv3x3(f,20), Conv5x5(f,20), Conv7x7(f,20)) + skip           # multi-scale block (Fig. 5)
f = ConvReLU(m, 60)
for d in [1, 2, 3, 2, 1]: f = DilatedConv3x3_ReLU(f, 60, dilation=d)     # layers 2-6, skips (Figs. 7, 9)
c = Conv3x3(y1 + y2 ⊙ (1 - Mask), 60)                                     # mask branch (Figs. 3, 8)
#   c is added to the feature maps after the 1st and 4th dilated convs ("lower solid line", Fig. 9b, p. 6)
out = Conv3x3(f, 1)                                                       # 3×3×1 output = predicted residual
```
- **How the mask is used (p. 6; Figs. 3, 8):** only through the composite `Input1 + Input2 ⊙ (1 − Mask)`: the damaged image with its gaps filled by the auxiliary image. Text: "input 1 with filled missing gaps by input 2 and mask is transferred to the subsequent layer in the network, which can also enhance the feature of auxiliary spectral/temporal information" (p. 6). The mask convention is not defined; from the formula, Mask = 1 on valid pixels and the gaps in y1 are zeros (black in Figs. 11b, 12b, 13b). The mask is not a separate input channel and does not weight the loss.
- **Residual target (eq. 9, p. 6):** `r_i = y1_i − x_i` (x = clear original). The figures label it "Label − Input1". "r_i is also just equivalent to the missing regions, outside which most pixel values in the residual image are close to zero" (p. 6).
- **Loss (eq. 10, p. 6):** `loss(Θ) = 1/(2N) Σ_i ‖φ(y1_i, y2_i, Θ) − r_i‖²` over the whole patch (not restricted to the gap).
- **Bands:** the output layer is 3×3×1 (Fig. 3) while TM tests are 6-band; the paper does not say whether bands are processed one at a time or how y2's bands are stacked. Unstated.
- One architecture, **separately trained models per task**: "the corresponding training data are employed independently to train the specific models, respectively" (p. 6).

## 2. Training and parameters (§IV-A, pp. 6–7)
- Cloud / SLC-off training: 16 Landsat TM dates, 2001-10-07 to 2002-05-04, 1720 × 2040 × 6, 30 m, "arranged them in sets of temporal pairs", patches 100 × 100, stride 100. MODIS: 600 Terra crops 400 × 400 × 7, patches 40 × 40, stride 40.
- Tests: "another two single examples of two temporal Landsat images (400×400×6) were set up as simulated images with a missing information mask"; every simulated experiment repeated 10 times, mean ± sd in Tables I–IV (p. 7). The paper does not say what varied between repeats or whether test crops are geographically separate from training.
- SGD, learning rate 0.01, 100 epochs, ×0.1 every 20 epochs; Caffe; TITAN X Pascal. Ablations: 500,000 iterations (p. 12). Testing code: github.com/WHUQZhang/STS-CNN (p. 7).
- Metrics: mPSNR and mSSIM over bands, CC, SAM (p. 7).

## 3. Evaluation protocol we can copy (pp. 8–9, Figs. 11–13)
- **Simulated cloud = black blobs pasted on a clear real image with known truth.** Fig. 12b: one large irregular blob near the top (a cluster of merged round lobes) and two smaller round blobs, on a 400 × 400 crop (by eye ~10–15% of the image; sizes are not stated anywhere). Fig. 13b: SLC-off stripes plus the same kind of lobed blob and several circles of different radii.
- Truth/auxiliary date gaps used: Fig. 11 truth 2001-10-23, auxiliary 2001-11-08 (16 days); Fig. 13 truth 2001-11-13, auxiliary 2002-04-17 (~5 months). **Fig. 12's caption labels are copied from Fig. 11** ("(b) Simulated SLC-off", same dates) although the picture is a different scene with cloud blobs; its real dates are therefore uncertain. The auxiliary image in Fig. 12c is visibly different in tone and field patterns from the truth, so the cloud test does include seasonal change, but no abrupt change is tested.
- **Misregistration sweep (p. 12, Figs. 18–19):** 0–5 px shifts on the simulated SLC-off case; STS-CNN has "the lowest" degradation rate vs LLHM, NSPI, WLR. Curves only, no table.
- Real cloud (Fig. 16, p. 11): visual only; the text points back to Table III, which is the simulated case. The text also calls both images "two temporal TM images which contained thick cloud", while (b) is labelled "without clouds".

## 4. Quantitative results (mean ± sd over 10 runs)
| Task (table, page) | STS-CNN | Best competitor |
|---|---|---|
| Dead lines, Terra MODIS b6 (I, p. 7) | PSNR 44.569, SSIM 0.990, CC 0.989 | WCLF 43.498 / 0.986 / 0.985 |
| SLC-off, TM (II, p. 8) | mPSNR 38.531, mSSIM 0.950, CC 0.973, SAM 1.013 | AWTC 37.984 / 0.947 / 0.970 / 1.114 |
| **Cloud, TM (III, p. 9)** | mPSNR 26.805, mSSIM 0.912, CC 0.965, SAM 0.766 | **STWR mPSNR 27.014 (higher)**, mSSIM 0.910, CC 0.963, SAM 0.775 |
| SLC-off + cloud (IV, p. 9) | mPSNR 24.063, mSSIM 0.853, CC 0.946, SAM 2.990 | WLR 23.920 / 0.838 / 0.932 / 3.141 |
- Ablations (p. 12): multi-scale block "about 1/0.5 dB", dilated convolution "0.2/0.4 dB" (MODIS / SLC-off). The sd values are tiny (0.001–0.03) and no significance test is reported, so differences of 0.2 dB between methods are not shown to be meaningful.

## 5. Stated limitations
- "When removing thick cloud through the use of temporal information, it results in some spectral distortion and blurring." (p. 13)
- Temporal methods generally: "the temporal differences are major obstacles to the reconstruction process, and registration errors between multi-temporal images also have a negative impact" (p. 3).
- Not stated but true of the design: no output flag of filled pixels, no confidence, no test where the ground changed between the auxiliary and target dates (flood, construction). The paper attributes all temporal differences to "a highly complex non-linear relation" (p. 8) that the CNN learns from paired training dates.

## 6. How to apply to our pipeline
- **Do not port the network.** It is a thick-cloud filler: inside the gap the output is learned from y2 (the other date). Our y2 would be the pre-storm image, which is exactly what a flood change detector must not see inside the cloud: it would paint pre-flood roads into the post-storm image and erase the flood signal.
- **`sn8_refhaze.haze_recovery` / `synthetic_haze` (and any later opaque-cloud arm):** adopt the protocol. Paste blob masks on clear real after-tiles (one large lobed blob plus 2–4 circles of mixed radii, as Figs. 12b/13b), keep the truth, report PSNR, SSIM and CC computed **inside the mask only** (the paper reports whole-image means, which dilute the gap error; report both). Also repeat at 0–5 px before/after misregistration (p. 12) to measure how the two-date fit degrades with alignment error. Justin put synthetic cloud on hold (2026-10-25), so this is for when that resumes.
- **Mask composite as a baseline arm:** `after ⊙ M + tone(before) ⊙ (1 − M)` (the paper's `y1 + y2 ⊙ (1 − Mask)` with our quantile tone curve from `sn8_refhaze.tone_curve`) is the naive temporal fill STS-CNN starts from. Useful only as a labelled "pre-storm fill" for display, and only if those pixels are flagged as not assessable for change. Our current "cannot assess" route in `road_handling` / `either_date_handling` stays the right decision for opaque cloud.
- **Residual idea for the thin-cloud path:** predicting `after − clear` (eq. 9) rather than the clear image matches our model (correction = haze term). If a learned correction is ever trained, train it on the residual, with the loss restricted to clear-ground pixels and the flood area excluded.
- **Flag filled pixels:** the paper does not; we must. Any corrected or filled pixel should carry a mask through to the change detector and to the road decisions.

## 7. Feasibility with our data
- We have **no SAR, no NIR, no extra dates**: one clear pre-storm date and the post-storm date only, RGB uint8 at 0.5 m used as grey.
- For cloud, STS-CNN needs a temporal auxiliary image; our only one is the pre-storm date, which differs from the target by the flood. The paper never tests that case, so nothing in it says the fill would be right where land cover changed; by design it would copy (a non-linear mapping of) the pre-storm ground.
- Spectral mode is unavailable (it needs an intact correlated band; our RGB bands are all hit by cloud together, and the paper itself says spectral methods "cannot deal with thick cloud cover, because this leads to the absence of all the spectral bands", p. 2).
- Training would need many clear date pairs of the same 0.5 m scenes; we have none beyond the development tiles, and published-label rules restrict what we may train on.
- **Usable now:** the simulated-mask protocol (blob shapes, known truth, PSNR/SSIM/CC, misregistration sweep), the residual formulation, and the warning that temporal fills give "spectral distortion and blurring" even without land-cover change.

## 8. Key quotes
- "For removing thick cloud in remote sensing imagery, input y1 is a temporal image with regions covered by thick cloud, and input y2 is another temporal image without cloud." (p. 5)
- "input 1 with filled missing gaps by input 2 and mask is transferred to the subsequent layer in the network" (p. 6)
- "the corresponding training data are employed independently to train the specific models, respectively" (p. 6)
- "the temporal differences are major obstacles to the reconstruction process" (p. 3)
- "When removing thick cloud through the use of temporal information, it results in some spectral distortion and blurring." (p. 13)
