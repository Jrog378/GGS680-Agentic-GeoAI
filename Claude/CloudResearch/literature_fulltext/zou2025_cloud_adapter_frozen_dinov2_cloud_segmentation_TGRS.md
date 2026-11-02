# Coder handoff: Zou, Zhang, Li, Wang, Xing, Jin, Lang & Tao (2025), Cloud-Adapter (frozen DINOv2 for cloud segmentation)

- **Citation:** Zou, X., Zhang, S., Li, K., Wang, S., Xing, J., Jin, L., Lang, C., & Tao, P. (2025). Adapting vision foundation models for robust cloud segmentation in remote sensing images. *IEEE TGRS* 63, 1–14. https://doi.org/10.1109/TGRS.2025.3597410
- **arXiv id:** 2411.13127 (v1 and v2; v2 of 23 Nov 2024 used). Code/checkpoints: https://xavierjiezou.github.io/Cloud-Adapter/ ; HRC_WHU mirror used by the authors: HF `XavierJiezou/cloud-adapter-datasets` (evidence 02).
- **PDF:** `/Users/jusrogers/Masters/papers/zou2025_cloud_adapter_frozen_dinov2_cloud_segmentation_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/2411.13127 (pages 1–13). The TGRS version (2025) is 14 pages and may differ (it appeared ~9 months later).
- **Validation:** PDF 7.8 MB, 13 pages (Read tool; pdfinfo agrees); title and eight authors match Crossref for the DOI; Conclusion with limitations (p. 10) and 62 references present. PASS (preprint).
- **Read:** pp. 1–11 in full (incl. all 13 tables); references/biographies pp. 11–13 skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§III, pp. 3–4; Figs. 2–3)
- **Backbone:** a VFM, **frozen** (weights never updated). Default DINOv2-Large (24 transformer layers).
- **Spatial perception module (SPM):** stem = two depthwise-separable convs (1×1 channel mapping, then 3×3); then **k = 4** ConvNet blocks, each stride 2 ("Pure-ConvNet" from ref. [55]); aggregator = adaptive average pooling of every block output to the smallest block's size, summed: `F_agg = Σ_{i=1..k} P_avg(F_ci)` (eq. 1). Parameter-free aggregator. Context dimension 64.
- **Adapting module** at transformer layer j: `Q = M_q(F_j^t), K = M_k(F_agg), V = M_v(F_agg)` (eq. 2); `S = softmax(QKᵀ/√d)` (eq. 3); `O = S·V` (eq. 4); `F_j^att = M(O) + F_j^t` (eq. 5); M is a low-rank MLP without activation, `M(z) = W2(W1 z)`, **rank r = 16** (eq. 6). Inserted at **N = 24** layers (every layer).
- So the backbone weights are frozen but its **features are modulated** inside every layer by the adapter (not a probe on frozen outputs).
- **Head:** Mask2Former. Its parameters are **not** counted in "*Params" (the no-adapter baseline is listed as 0.00 M, Table VI).
- **Training:** RTX 3090; AdamW, LR 1e-4, weight decay 0.05; linear warm-up from 1e-6 over 1,000 iterations then PolyLR (power 0.9) to 40,000 iterations; batch 4; validation every 4,000 steps; **seed 42**; kaiming-normal init (p. 5). One model per dataset.
- **How multispectral inputs are fed to DINOv2 (3-channel patch embedding) is not stated.**

## 2. Data (Table I, pp. 4–5)
| Dataset | Sensor | Res. | Train / Val / Test | Patch | Classes |
|---|---|---|---|---|---|
| CloudSEN12 High (L1C, L2A) | Sentinel-2 | 10 m | 8,490 / 535 / 975 | 512 | 4 (clear, thin, thick, shadow) |
| L8 Biome | Landsat 8 | 30 m | 7,931 / 2,643 / 2,643 | 512 | 4 |
| GF12MS WHU (GF1, GF2) | Gaofen 1, 2 | 8 m, 4 m | 20,697 / 11,645 / – | 256 | 2 |
| HRC_WHU | Google Earth | 0.5–15 m | **120 / – / 30** | 256 | 2 (clear, cloud) |
- "in typical binary cloud segmentation datasets, thin and thick clouds are grouped into a single category, 'cloud,' while cloud shadows are excluded" (p. 4).
- **HRC_WHU has no validation set**, yet training validates every 4,000 steps. Which set was used for checkpoint choice on HRC_WHU is not stated; if it was the 30 test images, the 89.05 is optimistically biased. (Our concern, not stated by the authors.)

## 3. Quantitative results
- **Backbone choice** (Table II, CloudSEN12 L1C, mIoU): DINOv2-S 68.12, -B 71.95, **-L 74.18** (1.82 M, 0.6%); SAM-B 72.53, -L 73.36, -H 73.70. DINOv2-L trained in 11 h 8 min with 14.6 GB vs SAM-H 19 h 9 min, 24.9 GB.
- **Component ablation** (Table VI, CloudSEN12 L1C mIoU): frozen backbone → head only **73.10**; + stem 73.12; + ConvNet blocks 73.20; + aggregator 73.37; + adapting modules **74.18**. Frozen DINOv2-L features carry nearly all the accuracy; the adapter adds ~1.1 points.
- Ablations of context dim (16→128: 73.72–74.18), rank (4→32: 73.84–74.18), interaction N (4→24: 73.75–74.18) all move < 0.5 point (Figs. 4–5, Table V). Single seed, so these differences are within likely run-to-run noise.
- **HRC_WHU** (Table VII): Cloud-Adapter aAcc 94.50, **mIoU 89.05**, mAcc 93.74, mDice 94.19; HRCloudNet 83.44; UNetMobv2 79.91; RSAM-Seg 80.90; KappaMask 67.48. mIoU here is the mean over the classes (clear and cloud), eq. 7 + "mean values computed for each class" (p. 5). MSCFF (the dataset authors' model, cloud IoU 0.903) is not in the comparison.
- GF1: 92.55 (KappaMask 92.42); GF2: 83.02 (UNetMobv2 80.44).
- **Thin cloud is the weak class:** CloudSEN12 L1C IoU clear 89.19, thick 85.46, **thin 56.15**, shadow 65.93 (Table X); L2A thin 54.97 (Table XI); L8 Biome thin 44.41, overall mIoU 57.53 (Table XII).
- L8 Biome by land cover (Table XIII): Cloud-Adapter not best on Grass/Crops (41.60 vs DBNet 59.08), Urban, Water.

## 4. Stated limitations (p. 10)
- "performance of Cloud-Adapter depends heavily on the VFM, and the large parameters of VFMs make it difficult to deploy on edge devices".
- On L8 Biome "a substantial gap remains when compared to manually annotated masks".
- Not done (our reading): no cross-dataset / cross-sensor transfer, no variance over seeds, no significance tests.

## 5. How to apply to our pipeline
- **`sn8_cloudspot` (frozen DINOv2 ViT-L/14 with registers, grey ×3, PCA → random forest per pixel, on HRC_WHU):**
  1. **The frozen-feature design is supported.** Table VI: frozen DINOv2-L + head = 73.10 vs 74.18 with the full adapter (CloudSEN12 L1C). The authors' own ablation shows the frozen features do almost all the work. Our gap to Cloud-Adapter on HRC_WHU, if any, is more likely in the **head** (RF on PCA-reduced tokens interpolated from 14 px patch centres vs a Mask2Former decoder with multi-scale context) than in the frozen backbone.
  2. **Cheapest next arm that stays "frozen":** add multi-scale spatial context the way SPM does, without training the backbone — e.g. our classical cues already give fine-scale texture; add average-pooled versions at 2, 4, 8, 16 px strides (SPM's aggregator is just pooling and summing) as RF features. This is the part of Cloud-Adapter that needs no gradient through DINOv2.
  3. **The adapting module is not frozen-feature use**: it changes every layer's output through trained cross-attention. Implementing it means training through DINOv2-L (fine on a GPU; Justin's rule allows training) but our tokens would then no longer be "frozen DINOv2" features. Treat it as a separate arm, not a tweak.
  4. **DINOv2-L > -B > -S** for clouds (Table II). Keep ViT-L; do not drop to -B for speed without testing.
- **Numbers to compare against (HRC_WHU 30 test images, sealed for us):** Cloud-Adapter two-class mIoU 89.05 / aAcc 94.50; MSCFF cloud-only IoU 0.903 (Li 2019). When we finally score the frozen spotter on the sealed 30, report **both** cloud IoU and two-class mean IoU so it can be placed against both papers. Our 5-fold CV on the 120 is not comparable.
- **Thin cloud**: even this model gets only ~55% IoU on Sentinel-2 thin cloud. And HRC_WHU has no thin-cloud class (see-through haze = clear). Nothing here validates a DINOv2 spotter for the thin haze that `sn8_refhaze` corrects.
- **Feasibility:** our data are RGB 0.5 m, grey-repeated to 3 channels; DINOv2's patch embedding wants 3 channels so this is natural. Code and checkpoints are public; the HRC_WHU checkpoint inherits the dataset's academic-only licence.

## 6. Key quotes
- "Cloud-Adapter approach, utilizing only 0.6% of the trainable parameters of the frozen backbone, achieves substantial performance gains" (abstract, p. 1)
- "In the baseline model, without any components from the spatial perception module or adapting module, the features from the VFM backbone were directly passed to the head for segmentation prediction. This configuration achieved a mIoU of 73.10%." (p. 7)
- "thin and thick clouds are grouped into a single category, 'cloud,' while cloud shadows are excluded from the annotations" (p. 4)
- "DINOv2 (Large) emerges as the optimal backbone for our method" (p. 6)
