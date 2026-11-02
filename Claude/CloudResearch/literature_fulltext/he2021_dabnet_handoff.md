# Coder handoff: He, Sun, Yan & Fu (2022; online 2021), DABNet: Deformable contextual and boundary-weighted network for cloud detection in remote sensing images

- **Citation:** He, Q., Sun, X., Yan, Z., & Fu, K. (2022). DABNet: Deformable contextual and boundary-weighted network for cloud detection in remote sensing images. *IEEE Transactions on Geoscience and Remote Sensing* 60, 5601216 (16 pp.). https://doi.org/10.1109/TGRS.2020.3045474 . Received 1 Nov 2020, revised 28 Nov 2020, accepted 14 Dec 2020, **published online 5 Jan 2021**, current version 3 Dec 2021 (p. 1). Cite as 2022 (vol. 60); 2021 is the early-access year.
- **PDF:** `/Users/jusrogers/Masters/papers/he2021_dabnet-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 11.6 MB; 16 pages (Read tool and pdfinfo) = article pages 1–16; page-1 title, authors (He, Sun, Yan, Fu), TGRS vol. 60, 2022, article 5601216 and DOI 10.1109/TGRS.2020.3045474 match todo.tsv; Conclusion (p. 14) and References [1]–[62] (pp. 15–16) present. PASS.
- **Read:** article pp. 1–16 in full (Read tool, page images), including Tables I–IX, Figs. 1–22, references and biographies. Page numbers below are article pages (5601216-n).
- **Prepared by:** Claude (AI), 2026-10-30.

## 1. Algorithm, step by step
Three parts (Fig. 3, p. 4; Algorithm 1, p. 4):
1. **Backbone DSN** (pp. 4–5, Fig. 4): ShuffleNetV2 with the downsampling of stages 3 and 4 removed, replaced by dilated convolutions of rate 2 (stage 3) and 4 (stage 4); output stride 8 instead of 32. Batch norm after some convolution layers. Layer count and parameters unchanged.
2. **DCFP** (eq. 4, p. 5; Figs. 5–6): `N_DCFP = Concat(X, N_DCM(X, r1), …, N_DCM(X, rn))`. Each DCM is a depthwise deformable dilated 3×3 convolution: `y(l, x, r) = Σ_{g_n∈G(r)} x(l + g_n + Δg_n)·w(l, g_n)` (eq. 6), grid G(r) of eq. 5, offsets Δg_n learnt by an extra conv layer; 1×1 conv after; residual path. Best rates **{1, 6, 12, 18}** (Table II, p. 9).
3. **Restoration network** (p. 6): concat multiscale + low-level features, 1×1 conv, bilinear upsampling (×8) and 3×3 convs (Fig. 3) → per-pixel cloud probability (softmax, eq. 9).
4. **Boundary-weighted (BW) loss** (p. 7), exactly as printed:
   - eq. 8: `L_bw = −(1/p) Σ_{i=1..p} w_i [(1 − y*_i) log(1 − f_i(y*_i|x_i)) + y*_i log f_i(y*_i|x_i)] + λ‖θ‖₂` ; p = number of pixels; λ not given.
   - eq. 10: `ρ_i = Σ_{j∈B} sqrt((x_i − x_j)² + (y_i − y_j)²)`, B = boundary pixels of the ground truth ("through the boundary detection of the ground truth"; the edge operator is not named).
   - eq. 11: `w_i = exp(−ρ_i) / Σ_{k=1..p} exp(−ρ_k) + 1`.
   - eq. 12: the extra term vs BCE is ΔL = −(1/p) Σ [exp(−ρ_i)/Σ_k exp(−ρ_k)]·[BCE term].
   - **Coding warning (our reading of the printed equations):** (a) ρ_i is a **sum** of distances to *all* boundary pixels, not the distance to the nearest one; (b) the softmax over all p pixels makes the extra weights sum to exactly 1 over the image, so with p = 321² ≈ 103,000 pixels the mean extra weight is ≈ 1e-5 and exp(−ρ) underflows for nearly every pixel. Taken literally, w_i ≈ 1 everywhere and the loss equals BCE + L2. The reported gain (Table IV) therefore cannot come from the formula as printed; the authors' code is not released. Any implementation must reinterpret it; the paper's stated intent is "a monotonically decreasing function about the boundary distance" (p. 2) with w_i in [1, 2].
5. **Training** (p. 9): RGB input only; cloud only (shadow, clear and no-data → background on GF-1 WFV, p. 8). Slices 321×321, batch 16 random slices, flips and rotations, Adam β1 = 0.9, β2 = 0.999, ε = 1e−8, initial learning rate printed as "1e^−6", halved every 10 epochs, 50 epochs, one RTX 2080Ti, PyTorch. L2 regularisation and batch norm (p. 8).

## 2. Inputs, outputs, data needs
- **Input:** RGB (p. 9: "All models use RGB images as input"), although both datasets have NIR.
- **Output:** binary cloud mask (no shadow, no thin/thick split).
- **Datasets** (pp. 7–8):
  - GF-1 WFV (SENDIMAGE lab, Li et al. 2017 [15]): 108 full scenes, 16 m, NIR + 3 visible; 70% train / 30% test at random.
  - **AIR-CD** (new): 34 GF-2 scenes (PMS1 and PMS2), Feb–Nov 2017, four Chinese provinces, 4 m, NIR + visible, 7300 × 6908 px; experts labelled cloud pixel by pixel, iteratively checked; only cloud labelled; 25 train / 9 test at random. Link https://github.com/aicyberteam/air-cd (pp. 2, 8).
- **HRC_WHU is not used.** MSCFF (the HRC_WHU paper's model, ref. [29]) is only a comparison model, retrained on AIR-CD and GF-1 WFV.
- **Code / weights:** not released or linked; only the AIR-CD data link.

## 3. Quantitative results (single runs; no confidence intervals or significance tests)
- **Table VI (p. 11), AIR-CD MIoU / OA / F1 (%)**: FCN-8s 85.52/89.62/88.37; PSPNet 88.96/94.71/92.53; DeepLabV3+ 91.48/97.35/96.09; MFFSNet 90.87/96.84/95.71; MSCFF 91.45/**97.83**/96.42; CDNet 91.83/97.45/96.74; **DABNet 92.08/97.69/96.95**.
- **Table VI, GF-1 WFV**: FCN-8s 84.19/89.17/87.96; PSPNet 86.32/93.24/91.03; DeepLabV3+ 89.27/95.07/94.68; MFFSNet 89.08/95.83/94.59; MSCFF 90.35/**96.74**/95.27; CDNet 89.97/96.46/**95.73**; **DABNet 90.68**/96.52/94.85.
- Efficiency (Table VI): DABNet 4.12 M params, 8.29 G multiply-adds; others 49.46–85.52 M, 19.86–227.97 G. Inference (Table VII, p. 11): DABNet 0.037 / 0.16 / 0.62 s at 256² / 512² / 1024²; others 0.061–0.084 / 0.24–0.33 / 0.96–1.38 s.
- Backbone (Table I, p. 9, AIR-CD): ShuffleNetV2+RN 82.16/87.84/85.92; DSN+RN 84.92/90.03/88.17.
- DCFP rates (Table II, p. 9): none 84.92/90.03/88.17; {1} 86.83/91.95/90.13; {1,6} 87.96/93.29/91.58; {1,6,12} 88.68/94.37/93.02; **{1,6,12,18} 89.75/95.98/94.83**; {1,6,12,18,24} 88.94/94.82/93.85. Table III (p. 9): +PPM 87.16/92.68/91.24; +ASPP 88.39/94.13/92.05; +DCFP 89.75/95.98/94.83.
- **BW loss (Table IV, p. 10, AIR-CD):** BCE 91.26/95.07/94.39 → BW 92.08/97.69/96.95. Note: the BCE row (MIoU 91.26) does not match the full BCE model of Tables II–III (89.75/95.98/94.83); the paper does not explain the difference.
- **Table V (p. 10, GF-1 WFV):** baseline 83.26/87.16/85.27; +DCFP 87.96/93.28/91.43; +BW loss 85.68/89.84/88.15; +DCFP+BW 90.68/96.52/94.85.
- Slice size (Table VIII, p. 13, AIR-CD): 256² 91.27/97.15/96.37; 512² 92.18/97.52/97.04; 1024² 92.53/97.98/97.61. Authors recommend ≈512².
- Water-body extraction (Table IX, p. 14; Gaofen challenge, 1000 GF-2 images of 492²): PSPNet 83.94/87.82/86.35; DeepLabV3+ 86.21/90.96/89.74; DABNet 88.37/92.03/91.26.
- Boundary metric: none. The boundary gain is shown only qualitatively (Figs. 8, 12) and through overall MIoU/OA/F1.

## 4. Stated limitations
- "there are still some obvious errors in thin cloud detection … the problem of omission of thin clouds is prone to appear … Especially, at the boundary of thin clouds, this problem is more serious" (p. 14, Fig. 22).
- Running time also depends on memory access; some baselines are close (p. 12).

## 5. How to apply to our pipeline
- **No HRC_WHU, so no number here is comparable to our spotter's HRC_WHU F1 (D0 0.868, D1b 0.878).** AIR-CD (4 m GF-2) and GF-1 WFV (16 m) are far coarser than our 0.5 m Maxar; their F1 values are on random scene splits, single runs.
- **RGB-only is supported:** the paper trains on RGB only, so an RGB/grey spotter is not unusual. It never tests grey.
- **The ring problem (ev09) is mostly a correction problem, not a detection one:** ev09 found the haze fringe 40–80 px beyond the gate, where HRC_WHU-style labels mark "clear" (thin cloud labelled only where the ground is not seen). A boundary-weighted detector sharpens the labelled edge; it cannot learn a fringe the labels do not contain. So the expected gain is on detection F1 near label edges (and so the gate's position), not on the 40–80 px ring.
- **Our spotter is a random forest on 1,000 random pixels per image (ev12)**, not a CNN, so the BW loss maps to a per-sample weight (or to boundary-biased sampling).

### Proposed bench arm: D5 boundary-weighted spotter samples
1. On each HRC_WHU training image (development 120 only, same folds as D0), compute the label boundary B (pixels whose 3×3 neighbourhood has both classes) and the distance d to the **nearest** boundary pixel (Euclidean distance transform). This is our reinterpretation of eq. 10 (nearest, not sum).
2. Weight `w = 1 + α·exp(−d/σ)` (keeps the paper's range w ∈ [1, 2] at α = 1). Starting values: α = 1, σ = 8 px (about one DINOv2 patch of 14 px at the resized scale; also try σ = 4 and 16 inside the training folds only).
3. Variant D5a: pass w as `sample_weight` to the random forest, same 1,000 random pixels. Variant D5b: draw the 1,000 pixels with probability ∝ w (more pixels near edges), unweighted fit.
4. Score exactly as D0/D1b: pooled F1 on the every-4th-pixel grid of held-out folds, paired per-image difference vs D0 (and vs D1b if HOT is in), bootstrap 95% CI, sign test. Add a **boundary-band F1** (pixels with d ≤ 16 px of the label edge) and an interior F1 (d > 16) so a gain at the edge is not hidden by the interior.
5. Report imagery: label edge, D0 and D5 masks, error crops along edges (barren and snow images first, the spotter's weakest).
6. Decision: keep only if pooled F1 is not worse and the boundary-band F1 gain has a CI above 0. Then, separately, re-run the ev09 ring measure with the D5 gate to see whether the gate edge moved.

## 6. Key quotes
- "All models use RGB images as input and only detect clouds, excluding cloud shadows." (p. 9)
- "we define a BW loss function that is a monotonically decreasing function about the boundary distance. By giving more weight to the boundary in network training instead of treating all pixels equally, the problem of the blurred boundary in cloud detection can be effectively improved." (p. 2)
- "Considering the high spatial resolution of the GF-2 satellite image and the relatively few cloud shadows, only cloud is labeled in the reference mask." (p. 8)
- "The data set will be open to the community to provide support for research in the field of cloud detection (https://github.com/aicyberteam/air-cd)." (p. 2)
- "there are still some obvious errors in thin cloud detection." (p. 14)
