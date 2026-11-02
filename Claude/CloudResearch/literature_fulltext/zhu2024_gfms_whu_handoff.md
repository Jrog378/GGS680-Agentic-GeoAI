# Coder handoff: Zhu, Li & Shen (2024), Transferring deep models for cloud detection in multisensor images via weakly supervised learning (TransMCD; GF1MS-WHU / GF2MS-WHU)

- **Citation:** Zhu, S., Li, Z., & Shen, H. (2024). Transferring deep models for cloud detection in multisensor images via weakly supervised learning. *IEEE Transactions on Geoscience and Remote Sensing* 62, 5609518 (18 pp.). https://doi.org/10.1109/TGRS.2024.3358824 . Received 21 Nov 2023, revised 16 Jan 2024, accepted 22 Jan 2024, published 14 Feb 2024 (p. 1).
- **PDF:** `/Users/jusrogers/Masters/papers/zhu2024_gfms_whu-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 4.9 MB; 18 pages (Read tool and pdfinfo) = article pages 1–18; page-1 title, authors (Shaocong Zhu, Zhiwei Li, Huanfeng Shen), TGRS vol. 62, 2024, article 5609518 and DOI 10.1109/TGRS.2024.3358824 match todo.tsv; Conclusion (p. 16) and References [1]–[63] (pp. 16–18) present. PASS.
- **Read:** article pp. 1–18 in full (Read tool, page images), including Tables I–XI, Figs. 1–14, references and biographies. Page numbers below are article pages (5609518-n).
- **Prepared by:** Claude (AI), 2026-10-30.

## 1. Algorithm, step by step
Method name in the paper: **TransMCD** (Fig. 1, p. 3). "GFMS_WHU" is only our ledger key.
1. **Pretrain** (pp. 3–4) a segmentation CNN on the labelled source D_S (GF1-WHU = GF-1 WFV, 108 scenes, 16 m). Main model RegNetY-4.0GF (Fig. 2): stem 3×3 conv stride 2, 32 channels; 4 layers of grouped residual bottlenecks; 2 output channels; sigmoid; **cloud if score > 0.5**. Loss `L_Combi = L_BCE + L_IoU + L_SSIM` (eq. 1), with `L_BCE = −(y log ŷ + (1−y) log(1−ŷ))` (eq. 2), `L_IoU = 1 − y·ŷ / (y + ŷ − y·ŷ)` (eq. 3), `L_SSIM = 1 − (2μ_yμ_ŷ + c1)(2σ_yŷ + c2) / ((μ_y² + μ_ŷ² + c1)(σ_y² + σ_ŷ² + c2))` (eq. 4), c1 = 0.01², c2 = 0.03². SSIM is said to focus the model on "variations occurring at the edges of the cloud" (p. 4).
2. **Rough mask M_R:** run the pretrained model on each target image D_T (p. 5).
3. **Spectral mask M_S** (pp. 4–5, Fig. 4): per target image, the threshold for each feature is set from "the average spectral features of the D_T image across the cloud coverage in M_R" (exact rule — mean only? which side? — not given). Features:
   - Whiteness index `WI = Σ_{i=1..3} |Band_i − MeanVis| / MeanVis` (eq. 5), visible bands only; near 0 = cloud.
   - HSI from RGB: H (eqs. 6, 9), `S = 1 − 3·min(R,G,B)/(R+G+B)` (eq. 7), `I = (R+G+B)/3` (eq. 8); cloud = low S, high I.
   - NIR reflectance (high).
   - M_S = intersection of the per-feature masks (Fig. 4).
4. **Hybrid mask** `M_H = M_R ∩ M_S`. Crop M_R, M_S, M_H into blocks (256 × 256, Table XI p. 14). **Cloud blocks:** M_H cloud fraction > 5%. **Clear blocks:** no cloud in both M_R and M_S (p. 6).
5. **Pixel pseudo-labels for cloud blocks** (UIS, p. 6, Fig. 5; Kanezaki 2018 [46]): (1) Felzenszwalb superpixels [53]; (2) CNN predicts labels on the block; (3) each superpixel takes its most frequent predicted label; (4) repeat 2–3, updating the CNN, merging small regions (Fig. 5 shows a stop when superpixel count > 10 is no longer met). Fig. 3 (p. 4) combines the segmentation map with the rough cloud patch by a per-segment "cloud percent" rule (threshold not stated).
6. **Fine-tune** (p. 6): mix D_S samples and D_T pseudo-labels 1:1, then "gradually remove the D_S samples"; the last iterations use D_T pseudo-labels only (schedule not given).
7. **Training settings** (p. 8): ImageNet weights; Adam β1 = 0.9, β2 = 0.999, ε = 1e−8; 50 epochs; learning rate 1e−5 (pretraining), 1e−4 (fine-tuning), ×0.1 at epochs 15 and 35; crops 250 × 250 zero-padded to 256 × 256; augmentation as [62]; each image divided by its maximum value; **input = blue, green, red, NIR**; one RTX 3070Ti (8 GB).

## 2. Inputs, outputs, data needs
- **Input:** 4 bands (B, G, R, NIR) for every model and stage (p. 8). No RGB-only or grey result is reported for the CNNs. The spectral step can be run RGB-only (WI + HSI); Table VI reports that combination.
- **Datasets** (Table I, p. 6; pp. 6–7): GF1-WHU (GF-1 WFV, 16 m, 108 labelled; source only; http://sendimage.whu.edu.cn/en/mfc-validation-data/); **GF1MS-WHU** (GF-1 PMS MS, 8 m, 33 labelled, 141 unlabelled, June 2014–Dec 2020); **GF2MS-WHU** (GF-2 PMS MS, 4 m, 29 labelled, 163 unlabelled from Hubei, Jilin, Hainan, June 2014–Oct 2020); WHUS2-CD (Sentinel-2 10 m B/G/R/NIR, 32 labelled, Apr 2018–May 2020; github.com/Neooolee/WHUS2-CD). Labels by Photoshop lasso, cloud = 255 (p. 6). "10 428 and 21 917 fully labeled image patches" made available at https://github.com/whu-ZSC/GF1-GF2MS-WHU (p. 2).
- **HRC_WHU is not used.**
- **Splits:** ML-FS (fully supervised on target labels) uses 70/30 on GF1MS/GF2MS; GF1-WHU and WHUS2-CD splits follow their original papers (p. 8). Test scenes: 10 (GF1MS), 9 (GF2MS), 8 (WHUS2-CD) (Tables III–V).
- **Internal inconsistency:** p. 6 / Table I say 163 unlabelled GF-2 images; p. 10 says "we used 134 unlabeled 4-m GF2-MS images to fine-tune".
- **Code / weights:** not released or linked; only the dataset link.

## 3. Quantitative results (single runs; no CIs or significance tests). OA / Precision / Recall / F1
- **Pretraining on GF1-WHU** (Table II, p. 8): ResNet 0.9799/0.9388/0.9124/0.9226; RegNetY 0.9795/0.9311/0.9161/0.9209; DeepLab V3+ 0.9777/0.9480/0.8986/0.9208; BoundaryNet 0.9800/0.9148/0.9357/0.9235.
- **GF1MS-WHU** (Table III, p. 9), F1 Pre-trained → ML-FS → TransMCD (TransMCD gain): ResNet 0.8874 → 0.9258 → 0.9057 (1.83); RegNetY 0.8973 → 0.9242 → 0.9179 (2.06); DeepLab 0.8944 → 0.9224 → 0.9067 (1.23); BoundaryNet 0.8549 → 0.9190 → 0.8830 (2.81).
- **GF2MS-WHU** (Table IV, p. 10): ResNet 0.8569 → 0.9179 → 0.8900 (3.31); RegNetY 0.8707 → 0.9216 → 0.9052 (3.45); DeepLab 0.8469 → 0.9134 → 0.8985 (5.16); BoundaryNet 0.8421 → 0.9103 → 0.8961 (5.40).
- **WHUS2-CD** (Table V, p. 11): ResNet 0.8183 → 0.9135 → 0.8777 (5.94); RegNetY 0.8325 → 0.9141 → 0.8851 (5.26); DeepLab 0.7711 → 0.9002 → 0.8674 (9.63); BoundaryNet 0.7870 → 0.9170 → 0.8735 (8.65).
- "Improvement (%)" columns are F1 differences ×100 (percentage points), not relative %.
- **Spectral features** (Table VI, p. 12): WI 0.9492/0.9344/0.5979/0.7216; HSI 0.9363/0.9384/0.4681/0.6175; NIR 0.8985/0.6780/0.5087/0.5226; **WI-HSI (RGB-only) 0.9352/0.9387/0.4589/0.6077**; WI-NIR 0.9389/0.9759/0.4835/0.6389; HSI-NIR 0.9361/0.9753/0.4387/0.5996; WI-HSI-NIR 0.9308/0.9776/0.4254/0.5856.
- **Masks** (Table VII, p. 12): rough M_R 0.9728/0.8706/0.9029/0.8816; spectral M_S 0.9308/0.9776/0.4254/0.5856; hybrid M_H 0.9307/**0.9956**/0.4225/0.5862. Blocks (Table VIII): M_H 6626 cloud / 10746 clear vs ground truth 11124 / 16770 (62.3% of samples kept, p. 14).
- **Pixel pseudo-labels** (Table IX, p. 13, RegNetY): GF1MS rough 0.9326/0.8981/0.9198/0.8990 → pseudo 0.9455/0.9070/0.9476/0.9209 (+2.19); GF2MS rough 0.9108/0.8769/0.9411/0.8978 → pseudo 0.9253/0.8952/0.9473/0.9131 (+1.53).
- **Region transfer** (Table X, p. 14, RegNetY; train Hubei, test other provinces): GF1MS pre 0.8751, ML-FS 0.8922, TransMCD **0.8999**; GF2MS pre 0.8565, ML-FS 0.8802, TransMCD **0.8873**.
- **Time** (Table XI, p. 14): GF1-MS 4548×4544 manual 500–600 min (175 cloud / 149 clear blocks) vs TransMCD 6–7 min (100/107); GF2-MS 7300×6908 manual 800–900 min (312/444) vs 9–10 min (152/300).

## 4. Stated limitations
- M_H "has a lot of leakage recognition, and its recall is only 0.4225. Many image blocks containing thin cloud features will not be selected as pseudo labels" → the fine-tuned model "cannot accurately identify thin clouds" (p. 15, Figs. 13(a), 14(a)).
- Snow next to cloud is labelled cloud in pseudo-labels because M_R errs there; "the TransMCD method is unable to accurately identify snow" (pp. 15–16, Fig. 14(b)).
- "TransMCD method is suitable for cloud detection in images without snow or large areas of thin clouds" (p. 16).
- Only four models tested; ImageNet weights only (p. 16). Accuracy depends on how well the pretrained model transfers and on the D_S–D_T gap (p. 13).

## 5. How to apply to our pipeline
- **No HRC_WHU; inputs include NIR; resolutions 4–16 m.** None of these F1 values is comparable to our spotter's HRC_WHU F1 (D0 0.868, D1b 0.878, ev22/23).
- **Weak-label transfer is the method's point, and it fits our gap exactly:** our spotter is trained on HRC_WHU (Google Earth, 0.5–15 m) and its accuracy on SpaceNet 8 Maxar pixels is unmeasured (ev12). TransMCD's recipe would adapt it to SN8 after-images with no labels. **But it trains on pseudo-labels, which the labelled-data-only rule defers** ("own/pseudo/Gemma labels only later"). So no arm is proposed now; recipe kept for when the rule allows it:
  1. Run the HRC_WHU spotter on SN8 Louisiana-East train/val after-images → M_R.
  2. RGB-only spectral mask: WI (eq. 5) and HSI S, I (eqs. 7–8) thresholded at their mean over M_R pixels per image; Table VI's RGB-only WI-HSI had precision 0.9387, recall 0.4589 on GF-1 MS. Optionally add our HOT (D1b) as the third feature in place of NIR.
  3. M_H = M_R ∩ M_S; 256-px blocks with > 5% M_H = cloud; no cloud in both = clear. Expect few thin-cloud blocks (paper's recall 0.42), which is the haze we most need.
  4. Re-fit the forest on HRC_WHU + pseudo-blocks 1:1. Scoring would still need labelled cloud on SN8, which does not exist; that is the deeper blocker.
- **Usable now without pseudo-labels:** (a) WI as an extra RGB feature for the spotter is close to our D1a whiteness arm (F1 +0.008 [−0.000, +0.016], within noise; ev22), so no new arm. (b) The SSIM term in their loss is a boundary-focus idea for CNNs; our forest has no equivalent; see the DABNet handoff's "D5 boundary-weighted spotter samples" arm for the boundary question.
- **Grey vs RGB:** WI and S are undefined on grey; any use needs the RGB Maxar bands.

## 6. Key quotes
- "During the pretraining and fine-tuning of all models, the input are the original spectral bands (blue, green, red, and NIR) of the images." (p. 8)
- "Note that this article only uses labeled images in the GF1-WHU dataset to pretrain the cloud detection model." (p. 6)
- "The closer the WI of the pixel is to zero, the higher the probability that the pixel is cloud." (p. 5)
- "The blocks of M_H with cloud regions exceeding 5% are classified as cloud image blocks" (p. 5)
- "we believe that the TransMCD method is suitable for cloud detection in images without snow or large areas of thin clouds." (p. 16)
