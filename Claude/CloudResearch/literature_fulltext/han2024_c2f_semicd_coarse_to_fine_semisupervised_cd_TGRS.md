# Coder handoff: Han, Wu, Hu, Li & Chen (2024), C2F-SemiCD: coarse-to-fine semi-supervised change detection

- **Citation:** Han, C., Wu, C., Hu, M., Li, J., & Chen, H. (2024). C2F-SemiCD: A Coarse-to-Fine Semi-Supervised Change Detection Method Based on Consistency Regularization in High-Resolution Remote Sensing Images. *IEEE TGRS* 62, 1–21. https://doi.org/10.1109/TGRS.2024.3370568
- **PDF:** `/Users/jusrogers/Masters/papers/han2024_c2f_semicd_coarse_to_fine_semisupervised_cd_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** **arXiv preprint version**, arXiv:2404.13838 (posted 22 Apr 2024): https://arxiv.org/pdf/2404.13838 — 20 pages, revision-highlighted (yellow) manuscript; title and 5 authors match Crossref and the arXiv API.
- **Validation:** `file` = PDF; 6.0 MB; 20 pages (Read tool reads page 20, the end of the 45 references; pdfinfo 20); Conclusion and references present; 20 vs published 21 pages is expected for a preprint layout. PASS (preprint noted).
- **Read:** pp. 1–20 in full (all tables; figures by caption); references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Method (§II, pp. 3–6)
- **C2FNet (supervised network):** Siamese VGG16-BN encoder (5 blocks) on T1, T2 crops 256 × 256 × 3; decoder: channel attention (adaptive max-pool, conv /16, ReLU, conv ×16, sigmoid), spatial attention, Global Context Module (4 branches of atrous convs, concatenated), Refine module (attention map multiplied into 3 feature levels), Aggregation_Init and Aggregation_Final (multi-level upsample-multiply-concat). Decoded feature sizes 16×16×512 → 256×256×64 (Fig. 5). "Coarse-to-fine" = this decoder's progression from deep, coarse features to full-resolution ones.
- **Mean teacher:** consistency loss `J(θ) = E‖f(x, θ', η') − f(x, θ, η)‖²` (eq. 1); teacher EMA `θ'_t = α θ'_{t−1} + (1 − α) θ_t`, α = 0.99 (eq. 2). Supervised phase first (5 epochs), then unlabelled phase with teacher pseudo-labels.
- **Loss:** BCE with sigmoid (eqs. 3–5); `Loss = Loss_sup + β · Loss_semi`, β = 0.2 (eq. 9).
- **Training:** PyTorch, one RTX 3090, AdamW, weight decay 0.0025, lr 5e-4, batch 16, 100 epochs; model kept at best val F1 and IoU.

## 2. Data (Table I)
- GoogleGZ-CD: 20 seasonal VHR pairs, Guangzhou 2006–2019, **0.55 m**, many change types (water, roads, farmland, bare land, forest, buildings, vessels); 740 train tiles, 116 val, 300 test.
- WHU-CD: Christchurch, **0.2 m**, buildings after earthquake reconstruction; 5,949 train, 744 val, 745 test.
- LEVIR-CD: 637 pairs 1024², **0.5 m**, buildings; 7,122 train, 1,025 val, 2,049 test.
- Labelled ratios 5/10/20/30% chosen randomly.

## 3. Results (F1 %, Tables II–VI)
| Dataset | 5% | 10% | 20% | 30% | C2FNet 100% |
|---|---|---|---|---|---|
| GoogleGZ-CD | 80.93 | 82.61 | 83.98 | 85.14 | 86.86 |
| WHU-CD | 85.63 (3rd) | 86.58 (3rd) | 90.07 | 92.85 | 94.36 |
| LEVIR-CD | 89.97 | 90.80 | 91.16 | 91.58 | 91.83 |
- Best of 9 semi-supervised methods except WHU-CD 5% and 10% (UniMatch-DeepLabv3+ 88.35, 88.58).
- Cross-dataset (other building set as unlabelled): WHU→WHU 88.09–91.60; LEVIR→LEVIR 87.97–91.36 (Tables V–VI).
- Ablations (Table VII, GoogleGZ-CD): removing any module costs ≤ 2.6 F1 points; supervised epochs best at 15 (5 used); β effect "not particularly large".
- No repeated runs, variances or significance tests; one random split per ratio.

## 4. Stated limitations
- β "difficult to find the optimal solution"; suggest repeated runs and averaging (p. 17).
- C2FNet "can still be improved" (p. 19). Large buildings still missed on LEVIR-CD (p. 13).

## 5. Nuisance vs change of interest (what the user asked for)
- The introduction says existing semi-supervised CD methods have "room for improvement in distinguishing the changes of interest from the changes of irrelevant in feature extraction" (p. 2), but **no explicit nuisance mechanism** is introduced: separation is learned from the labels (GoogleGZ-CD pairs are seasonal), plus attention modules. No radiometric normalisation, cloud, haze or shadow handling.

## 6. How to apply to our pipeline
- **Not support for the two-pass "remove big change, re-detect small objects" design.** It is a single forward pass; "coarse-to-fine" is decoder scale. Cite it only as an example of multi-scale decoding.
- **Mean teacher for the flood/road head (if a learned head is used):** SN8 has human labels for a subset and many unlabelled tiles; the EMA-teacher recipe (α = 0.99, β = 0.2, 5 supervised epochs first) is a standard way to use the rest. Pseudo-labels are model-made labels — under the "labelled data only" rule they can be tried only after the labelled-only baseline is frozen, and evaluated on the untouched human-labelled test.
- **Label-ratio protocol:** report F1 at 5/10/20/30/100% of labelled tiles — a cheap, convincing way to show label efficiency for any learned arm (e.g. `sn8_cloudspot` random forest on HRC_WHU).
- **Feasibility:** RGB 0.5 m pairs at 256 × 256 match our tiles; a VGG16 network is trainable on one GPU. No SAR/NIR. Not relevant to the haze fade itself.

## 7. Key quotes
- "the C2FNet network 'gradually' completes the extraction of change features from coarse-grained to fine-grained through multi-scale feature fusion" (abstract, p. 1).
- "these semi-supervised CD methods still have room for improvement in distinguishing the changes of interest from the changes of irrelevant in feature extraction ability" (p. 2).
- "Even when the proportion of labels in the training data is only 30%, the results are close to the results of the fully supervised method" (p. 2).
