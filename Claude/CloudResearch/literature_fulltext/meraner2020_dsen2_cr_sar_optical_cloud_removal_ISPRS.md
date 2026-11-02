# Coder handoff: Meraner, Ebel, Zhu & Schmitt (2020), DSen2-CR (SAR-optical cloud removal)

- **Citation:** Meraner, A., Ebel, P., Zhu, X. X., & Schmitt, M. (2020). Cloud removal in Sentinel-2 imagery using a deep residual neural network and SAR-optical data fusion. *ISPRS Journal of Photogrammetry and Remote Sensing* 166, 333–346. https://doi.org/10.1016/j.isprsjprs.2020.05.013
- **PDF:** `/Users/jusrogers/Masters/papers/meraner2020_dsen2_cr_sar_optical_cloud_removal_ISPRS-summary.pdf` (page 1 = AI summary; journal p. 333 = PDF p. 2)
- **Source:** published version (Elsevier, CC BY), Helmholtz Munich PuSH repository, https://push-zb.helmholtz-munich.de/deliver.php?id=37494 (landing page https://push-zb.helmholtz-muenchen.de/frontdoor.php?source_opus=61517; also PMC7386944). Page numbers below are the journal's.
- **Validation (completeness-checker Mode 2):** `file` = PDF; 27.4 MB; 14 pages by Read tool and pdfinfo = published range 333–346; first page title/authors match Crossref; DOI matches; §6 Summary and conclusion (p. 345) and references (pp. 345–346) present. PASS.
- **Read:** pp. 333–346 in full; Table 1, eq. 3 and Figs. 3, 5 and 7 read from the page images (pp. 337–340) because extraction garbled them; reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. What the method does (§3, pp. 335–340)
1. **Data (SEN12MS-CR, §2.2, pp. 334–335):** 169 regions of interest (ROIs), ~5200 × 4000 px at 10 m, sampled over all landmasses plus an urban-only draw (deliberate urban bias), all seasons. Each ROI = cloudy Sentinel-2 L1C (all 13 bands, TOA reflectance 0–10,000; 20–70% cloud), clear Sentinel-2 (< 10% cloud), Sentinel-1 GRD IW VV + VH in dB. "All three images were acquired within the same meteorological season to limit surface changes" (p. 335). Cut to 256 × 256 px patches, stride 128 (50% overlap): 157,521 triplets, ~620 GB.
2. **Split by ROI, not patch (§2.3, p. 335):** 149 train / 10 val / 10 test ROIs → 134,907 / 11,921 / 10,693 patches; "the three datasets are spatially and temporally completely disparate".
3. **Network (§3.3, Fig. 3, pp. 335–337):** concat(13 optical + 2 SAR) → 3×3 conv + ReLU → B residual blocks [conv 3×3, ReLU, conv 3×3, × 0.1 residual scaling, + skip] → 3×3 conv back to 13 bands → **+ input cloudy image (long skip)**. So the network predicts a per-pixel correction: "In the case of a clear sky input or filmy clouds, the predicted corrections will be minor or non-existent. Conversely, for thick clouds with bright appearance, the corrections will be larger" (p. 336). F = 256; B is described as a hyperparameter but **its value is not given in the text** (we did not find it; do not quote a number). Cloud detection is implicit: no mask is fed at prediction time.
4. **Loss (§3.4, eqs. 2–3, p. 339–340):**
   - Plain target loss: `L_T = ||P − T||_1 / N_tot` (P prediction, T clear target, N_tot = pixels × channels).
   - **CARL:** `L_CARL = ||CSM ⊙ (P − T) + (1 − CSM) ⊙ (P − I)||_1 / N_tot + λ ||P − T||_1 / N_tot`, with I the cloudy input, CSM the binary cloud-and-shadow mask (1 = cloud/shadow), ⊙ element-wise over all channels. Inside the mask: match the other-date target; outside: reproduce the input. The λ term was added because the cloud-adaptive part alone made the network learn the mask "too precise[ly]" and produce artifacts; **λ = 1** "after extensive tuning" (p. 340).
5. **Cloud/shadow mask, used only for training and for scoring (Fig. 5, p. 338; p. 340):**
   - Cloud score starts at 1, then min with rescale(B2, 0.1, 0.5), rescale(B1, 0.1, 0.3), rescale(B1+B10, 0.5, 0.7), rescale(B2+B3+B4, 0.2, 0.8) (brightness), rescale(NDSI, 0.8, 0.6) (not snow); closing 5×5, average 7×7, clip [0, 1]; cloud = score > **T_CL = 0.2** (chosen "after a visual evaluation").
   - Shadow: CSI = (B8 + B11)/2 < T_CSI AND B1 < T_WBI, median 5×5; thresholds from **T_CSI = 3/4, T_WBI = 5/6** (Zhai et al. 2018 parameters). Mask = cloud OR shadow.
   - "The threshold values were chosen in a conservative manner to reduce false negative detections" (p. 340): the mask is grown on purpose so cloud is not scored as clear.
6. **Training (§3.5, p. 340):** clip optical to [0, 10,000], ÷ 2000; SAR clipped to [−25, 0] (VV) / [−32.5, 0] (VH), shifted and scaled to [0, 2]; random rotations and flips; He-uniform init; Nadam, lr 7·10⁻⁵, batch 16; Keras/TensorFlow, 8 × P100.

## 2. Evaluation protocol (§4, Table 1, pp. 339–341)
- **Real clouds only.** Every number is on real cloudy/clear pairs from the 10 held-out ROIs; there is **no simulated-cloud test** and no split of results by cloud thickness or type.
- Three error regions (Table 1 caption, p. 339): **Target** = prediction vs clear target over the whole image; **Reprod** = prediction vs the input's clear pixels (outside CSM); **Recon** = prediction vs target inside the CSM.
- Metrics: MAE and RMSE (TOA reflectance), PSNR (dB), SAM (°), SSIM; band-wise normalised RMSE (Figs. 10–11).

## 3. Quantitative results (Table 1, p. 339)
| Model | MAE Target | MAE Reprod | MAE Recon | RMSE | PSNR dB | SAM Target | SAM Reprod | SAM Recon | SSIM |
|---|---|---|---|---|---|---|---|---|---|
| DSen2-CR, CARL | 0.0290 | 0.0204 | 0.0266 | 0.0366 | 28.7 | 8.15 | 3.94 | 8.04 | 0.875 |
| DSen2-CR, L_T | 0.0270 | 0.0398 | 0.0266 | 0.0343 | 29.3 | 8.07 | 6.33 | 8.13 | 0.878 |
| CARL, no SAR | 0.0306 | 0.0188 | 0.0282 | 0.0387 | 27.6 | 8.98 | 3.86 | 8.97 | 0.870 |
| L_T, no SAR | 0.0284 | 0.0389 | 0.0281 | 0.0361 | 28.8 | 8.97 | 6.17 | 9.05 | 0.873 |
| pix2pix (U-Net + PatchGAN, with SAR) | 0.0292 | 0.0210 | 0.0274 | 0.0424 | 28.2 | 13.68 | 13.93 | 12.67 | 0.844 |

- CARL vs L_T: **49% less MAE and 38% less SAM reproduction error**, reconstruction error "comparable" (p. 342–343). L_T wins the target-only metrics because "the optimization and the evaluation is performed on the same objective" (p. 343).
- SAR: reconstruction better by ~6% MAE and ~11% SAM; reproduction slightly worse (MAE/SAM +2%/+3% with L_T, +9%/+2% with CARL) because the network "partly integrates SAR information also when reproducing cloud-free regions" (p. 341).
- Spectrum: average band nRMSE 2–20%; worst B10, B9, B1 (atmospheric bands) (pp. 344–345).
- No significance tests, no confidence intervals, no per-ROI spread are reported.

## 4. Stated limitations and failures
- **Land-cover change between dates:** the clear target is a different day; with L_T the network learns "to predict and apply unwanted surface changes" (p. 339). Fig. 7 (p. 340): blooming rapeseed in the input stays yellow with CARL, turns green with L_T. Fig. 4 (p. 338) shows input/target pairs with visible surface change.
- **Thick cloud over complex scenes:** "when the scene is comprised of complex patterns and the cloud cover is optically very thick, the network fails to provide a detailed and fully accurate reconstruction" (p. 345); urban scenes reconstructed "only on a coarse scale" (p. 341, Fig. 6).
- Under CARL some reconstructed spectra lie "between input and target, either due to prediction inaccuracy or due to the partial retainment of input information induced by the CARL loss" (p. 345), i.e. haze is partly kept.
- No uncertainty output and no flagging of filled pixels: the method returns one image with no confidence map or abstain option.
- The mask is rule-based with visually chosen thresholds; mask errors are not evaluated.
- Authors expect better results if fine-tuned to one region or land-cover type (p. 345).

## 5. How to apply to our pipeline
Nothing in the network transfers (we have no SAR, no extra bands, no training pairs of our own). Four things do:
1. **Correct only inside the gate, prove the outside is untouched (`sn8_refhaze.dark_reference_dehaze`, `sn8_cloudsym.either_date_dehaze`).** CARL is the learned version of our rule. Add a **reproduction error** to every correction arm: MAE between corrected and uncorrected *after* image on pixels outside the cloud gate (including the 20 m fade zone reported separately). It should be 0 outside gate + fade by construction; any non-zero value is a bug or a leak from the guided filter / blur. Report it next to the in-gate numbers, as Table 1 does.
2. **Score inside and outside separately (Target / Reprod / Recon split).** For `haze_recovery` (synthetic haze on clear tiles, known answer) we have a true target, so report Recon = error inside the gate vs the clear tile, Reprod = outside, and whole-tile Target. On real tiles the only "target" is the before image, which differs by the flood: like the paper, expect real change to inflate the in-gate error, so do not use before-vs-corrected error on flooded pixels as accuracy. Use the paper's warning (p. 343) that optimising for match-to-reference rewards copying the reference.
3. **Do not pull the before image into the gate wholesale.** The L_T result is the failure we must avoid: a fill that matches the other date paints the other date's land cover (rapeseed yellow → green). Our tone-curve/transmission correction keeps the after pixel (t, L per pixel) instead of substituting before pixels; keep it that way, and keep T_MIN = 0.2 abstain. For thick cloud the paper's answer is SAR; ours is to abstain.
4. **Grow the mask on purpose.** Their thresholds were set "conservative[ly] to reduce false negative detections" (p. 340) and they use morphological closing + averaging. This supports dilating the cloud gate (our 20 m fade) rather than trimming it; cloud missed by the gate is scored as clear and corrupts the tone fit in `tone_curve`.
- `sn8_cloudspot`: the rule-based cloud score (Fig. 5) needs B1, B10, NDSI and SWIR; only the B2+B3+B4 brightness term has an RGB analogue. Not worth adding as a cue beyond our existing bright flag.

## 6. Feasibility with our data
- **We have no SAR and no other dates (one clear pre-storm date + the post-storm date), RGB uint8 at 0.5 m, no NIR/SWIR.** DSen2-CR itself is not feasible: it needs Sentinel-1, 13 bands and 100k+ training triplets; its gain under thick cloud comes from SAR (Fig. 6). Pre-trained weights are for 10 m Sentinel-2 L1C and would not apply to Maxar.
- **Usable now:** the CARL principle (only the gate changes; measure reproduction error outside it), the three-region scoring (Target / Reprod / Recon), the real-cloud held-out-region protocol (our analogue: split by tile/area, never by patch), and the evidence that different-date references import land-cover change.
- **Not available from this paper:** no uncertainty or confidence map, no thin vs thick breakdown, no simulated-cloud benchmark, no significance tests. For abstention or flagging of filled pixels look elsewhere.

## 7. Key quotes
- "In the cloud-adaptive part, the mean absolute error loss is computed w.r.t. the target image for cloudy or shadowed pixels of the input image, and w.r.t. the input image itself for clear-sky pixels." (p. 339)
- "the network is induced to learn, predict and apply unwanted surface changes, due to being trained on multitemporal data with changing ground conditions" (p. 339)
- "The threshold values were chosen in a conservative manner to reduce false negative detections." (p. 340)
- "using L_T naturally leads to better results in target-only based metrics (here RMSE, PSNR and SSIM) since the optimization and the evaluation is performed on the same objective" (p. 343)
- "when the scene is comprised of complex patterns and the cloud cover is optically very thick, the network fails to provide a detailed and fully accurate reconstruction" (p. 345)
