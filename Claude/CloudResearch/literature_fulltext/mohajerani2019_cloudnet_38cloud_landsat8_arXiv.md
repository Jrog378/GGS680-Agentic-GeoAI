# Coder handoff: Mohajerani & Saeedi (2019), Cloud-Net: An end-to-end cloud detection algorithm for Landsat 8 imagery (38-Cloud)

- **Citation:** Mohajerani, S., & Saeedi, P. (2019). *IGARSS 2019*, 1029–1032. https://doi.org/10.1109/IGARSS.2019.8898776 — **arXiv preprint version** (arXiv:1901.10077v1, 29 Jan 2019); title and authors match the published paper (Crossref).
- **PDF:** `/Users/jusrogers/Masters/papers/mohajerani2019_cloudnet_38cloud_landsat8_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** https://arxiv.org/pdf/1901.10077v1
- **Validation:** PDF 1.5, 2.7 MB, 4 pages (last page read with the Read tool; pdfinfo 4) = published 1029–1032; Conclusion + 21 references present. PASS (preprint).
- **Read:** all 4 pages. Page numbers below are the preprint's 1–4.
- **Type:** method + dataset attribution (38-Cloud). Academic (Simon Fraser). Prepared by Claude (AI), 2026-10-29.

## 1. Data and labels (§3.0.1, p. 3)
- 38 Landsat 8 scenes (18 train / 20 test), from the authors' MMSP 2018 dataset; 5 scenes with "inaccurate and uncertain GTs" replaced; **all training GTs manually annotated** (previously automatic). 384 × 384 non-overlapping patches: 8,400 train, 9,201 test. Bands 2–5 (B, G, R, NIR).
- Classes: binary **cloud vs clear** ("The predicted mask has two classes of 'cloud' and 'clear'", p. 3). **No thin-cloud, haze, shadow or invalid definition is given in this paper.**
- Availability: "publicly available to the research community by request" (pp. 1, 3). No licence stated.

## 2. Model (§2, pp. 2–3)
- Cloud-Net: U-Net-like with in-block concat/copy/add shortcuts; input 192 × 192 × 4 (patches downsized from 384), sigmoid output.
- Soft Jaccard loss `J_L = −(Σ t_i y_i + ε)/(Σ t_i + Σ y_i − Σ t_i y_i + ε)`, ε = 1e-7 (eq. 1). Adam, lr 1e-4, decay 0.7, patience 15, to 1e-9; uniform init [−1, 1]; flips/rotation/zoom.
- Test: tile → 192 → probability → **global threshold 0.047** → resize to 384 → stitch.

## 3. Metrics and numbers (eq. 2, Table 1, p. 3; 20 test scenes)
| Method | Jaccard | Precision | Recall | Specificity | OA |
|---|---|---|---|---|---|
| FCN (MMSP 2018) retrained on 38-Cloud | 72.17 | 84.59 | 81.37 | 98.45 | 95.23 |
| Fmask (Zhu 2015) | 75.16 | 77.71 | 97.22 | 93.96 | 94.89 |
| Cloud-Net | 78.50 | 91.23 | 84.85 | 98.67 | 96.48 |
- Note: the same authors later report Cloud-Net at Jaccard 87.32 and Fmask V3 at 85.91 on the same test set (Cloud-Net+ paper, Table III) — different evaluation settings; the two sets of numbers are not comparable.
- No exclusion of cloud edges or invalid pixels is described; no significance tests.

## 4. Limitations
- Not discussed beyond the dataset fixes. Only 2 qualitative examples.

## 5. How to apply to our pipeline
- Low value for code. Two small lessons:
  - **Threshold tuning:** their operating threshold 0.047 is far from 0.5; pick our `CloudSpotter` probability threshold on development folds (balanced omission/commission, as Cloud Score+), never assume 0.5.
  - **Visible + NIR only beats Fmask** at 30 m: weak support that colour/visible cues can carry cloud detection; for us only RGB (no NIR) is available.
- 38-Cloud is not a training source for 0.5 m tiles (30 m Landsat; academic data; binary labels).

## 6. Key quotes
- "we have noticed that five of them ... had inaccurate and uncertain GTs. We replaced these images with five new images." (p. 3)
- "it is binarized using a global threshold of 0.047" (p. 3)
