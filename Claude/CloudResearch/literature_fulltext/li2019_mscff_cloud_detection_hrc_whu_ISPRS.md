# Coder handoff: Li, Shen, Cheng, Liu, You & He (2019), MSCFF cloud detection and the HRC_WHU dataset

- **Citation:** Li, Z., Shen, H., Cheng, Q., Liu, Y., You, S., & He, Z. (2019). Deep learning based cloud detection for medium and high resolution remote sensing images of different sensors. *ISPRS JPRS* 150, 197–212. https://doi.org/10.1016/j.isprsjprs.2019.02.017
- **PDF:** `/Users/jusrogers/Masters/papers/li2019_mscff_cloud_detection_hrc_whu_ISPRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/1810.05801 — a 37-page single-column manuscript (pages numbered 1–37), not the journal's 197–212. Page numbers below are the manuscript's.
- **Validation:** PDF 2.8 MB, 37 pages (Read tool; pdfinfo agrees); title and all six authors match Crossref for the DOI; Conclusions (p. 31) and references (pp. 32–37) present. 37 manuscript pages vs 16 journal pages is consistent with a double-spaced accepted manuscript. PASS (preprint pagination noted).
- **Read:** pp. 1–32 in full; references pp. 32–37 skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. How HRC_WHU was labelled (the question we were asked to check; pp. 16–17)
- 150 Google Earth images, **RGB only, 1280 × 720 × 3, 0.5–15 m** (Table 2, p. 15). "satellite images, aerial photography, and geographic information system data are superimposed" in Google Earth (p. 16), so the scenes are not all satellite and have **no accurate geolocation** (Fig. 4 caption, p. 16). Resolution per image is not given.
- Labellers: "experts in the field of remote sensing image interpretation from Wuhan University" (p. 16).
- Procedure: contrast-stretch the cloudy image in Adobe Photoshop; alternate **magic wand (tolerance 5–30)** and **lasso** (lasso fixes what the wand cannot select); cloud = 255, clear = 0 (pp. 16–17). Binary: there is **no thin-cloud class** in HRC_WHU.
- **Thin cloud:** "the thin clouds were labeled as cloud if they were visually identifiable and the underlying surface could not be seen clearly" (p. 17). So thin cloud through which the ground *can* be seen clearly is labelled **clear (0)**. The rule follows their earlier GF-1 work (Li et al. 2017).
- **Shadow:** "Considering that cloud shadows in high-resolution images are rare and hard to accurately select, only clouds were labeled in the reference masks." (p. 17). The deep models for HR were "trained to only detect clouds" (p. 24).
- Split: 120 of 150 scenes for training, **6,000 partially overlapping 256 × 256 patches**; 30 test scenes chosen at random "to ensure that the numbers of images in different land-cover types were almost equal" (pp. 17–18). Fig. 8 shows five HR land-cover types: water, bright surface, vegetation, urban, snow/ice (p. 25).
- Contrast with the Landsat sets they also used: L7_Irish and L8_Biome do have thin-cloud labels, but the authors **merged thin cloud into cloud** for all experiments (p. 17).

## 2. Algorithm (MSCFF, §2, pp. 6–14)
- Preprocess: scale to [0,1] by maximum normalisation (uncalibrated sensors, incl. HR) or TOA reflectance (Landsat). 256 × 256 non-overlapping training patches (overlapping for HR), no augmentation (p. 7). At test time, overlapping patches; the **maximum** is taken where they overlap (p. 12).
- Network: fully convolutional encoder-decoder of six "CBRR" blocks (three 3 × 3 conv + BN + ReLU with a residual connection); max-pool 2 × 2 after the first three encoder blocks; **dilated convolutions, factors 2, 4, 4, 2**, in the last two encoder / first two decoder blocks; deconvolution to upsample; encoder–decoder skip connections summed. All six decoder scales are upsampled to input size, concatenated and fused by a last conv into **two maps (cloud, shadow)** (pp. 8–11, Fig. 2). 64 filters everywhere (wider variant only slightly better, p. 14).
- Loss: mean-squared error, eq. (1) `L(w) = (1/N) Σ ||y_i − F(x_i, w)||²` — chosen over cross-entropy (nearly equal accuracy) so the output map can be thresholded to trade commission vs omission (p. 12).
- Training: SGD, batch 10, poly LR decay from 0.1, 200,000 iterations from scratch, MatConvNet, Titan Xp, 2–3 days per dataset (p. 12). **One model per dataset/sensor** (p. 18).
- Output: threshold **t = 0.5** default; cloud overrides shadow when both fire (pp. 12–13).
- Metrics (eqs. 2–6, pp. 19–20): OA, recall, precision, "mIoU" defined as intersection/union of detected and reference **cloud** areas (i.e. cloud-class IoU, not a two-class mean), F1.

## 3. Quantitative results (Table 4, p. 20; HR = HRC_WHU 30 test scenes)
| Method | OA | Recall | Precision | mIoU | F |
|---|---|---|---|---|---|
| PRS (rule-based, aerial photos) | 86.66% | 77.00% | 87.83% | 0.696 | 0.821 |
| DeepLab v2 (VGG16) | 93.83% | 92.66% | 91.84% | 0.856 | 0.922 |
| DCN | 94.91% | 92.02% | 94.97% | 0.877 | 0.935 |
| MSCFF | 95.99% | 94.41% | 95.43% | 0.903 | 0.949 |
- Landsat-8 bands (Table 5, p. 27): RGB-only mIoU 0.866, NIR+RGB 0.878, all bands 0.895 — NIR helps.
- PRS "only detects the thick clouds" and calls snow cloud (p. 24); DCN omits "thin clouds around cloud boundaries" on Landsat (p. 21).

## 4. Stated limitations (pp. 30–31)
- Large bright objects bigger than the patch / receptive field (snow) are called cloud without a thermal band.
- HR cloud shadows are "less evident" and "easily confused with building shadows"; the shadow model was trained on medium resolution and "it is not recommended" to apply it to HR imagery.
- Scale: bright-surface spatial features (buildings) change with resolution; train on mixed resolutions.
- Inputs with large DN range need a contrast stretch before the model (p. 29).

## 5. How to apply to our pipeline
- **`sn8_cloudspot` (trains on HRC_WHU):** what it learns is the paper's label rule: **cloud = visible and the ground cannot be seen clearly; see-through haze = clear**. So:
  1. The spotter is a detector of opaque/semi-opaque cloud, not of the thin haze `sn8_refhaze` / `sn8_cloudsym` correct. Do not score the spotter against the dark-rise haze gate as if they targeted the same thing; describe the spotter as the "cannot see the ground" (abstain) layer and the dark-rise gate as the "can correct" layer.
  2. Pixels labelled 0 can contain thin cloud. A spotter that fires on them is not necessarily wrong; when inspecting false positives on HRC_WHU, tag them "thin, ground visible" vs "not cloud" before calling them errors.
  3. No shadow labels exist: a shadow detector cannot be trained or evaluated on HRC_WHU.
  4. Labels are magic-wand polygons with tolerance 5–30 on a contrast-stretched image: boundary pixels are uncertain. A boundary-excluded score (e.g. ignore a few pixels either side of the mask edge) is a fair sensitivity check.
  5. Resolution varies per image (0.5–15 m, unknown per image) and some scenes are aerial photographs. Our 0.5 m tiles are the fine end; scale mismatch is the authors' own stated limit.
- **Comparison number:** on the same 30 test images, MSCFF cloud IoU 0.903 / F 0.949 / OA 95.99%. Those 30 are sealed for us (`sn8_cloudref` refuses them), so the number is only for the final, frozen spotter. Our 5-fold CV on the 120 is not comparable to it.
- **Thresholding:** the authors chose MSE output so the threshold can be moved toward fewer omissions for change surveys (p. 12) — the same logic supports reporting our spotter's risk–coverage curve rather than one cut.
- **Feasibility:** dataset fits our data well (RGB, 0.5 m at its fine end); academic-use-only licence (per evidence 02), so the spotter is research-only. MSCFF itself (MatConvNet) is not needed.

## 6. Key quotes
- "the thin clouds were labeled as cloud if they were visually identifiable and the underlying surface could not be seen clearly" (p. 17)
- "Considering that cloud shadows in high-resolution images are rare and hard to accurately select, only clouds were labeled in the reference masks." (p. 17)
- "we treated both cloud and thin cloud as cloud, and merged cloud shadow over land and water into the shadow class" (p. 17, Landsat sets)
- "it is not recommended to extendedly apply the pre-trained model to high-resolution images for cloud shadow detection" (p. 31)
