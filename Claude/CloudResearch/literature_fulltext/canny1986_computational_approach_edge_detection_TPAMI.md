# Coder handoff: Canny (1986), A Computational Approach to Edge Detection — focus: hysteresis thresholding

- **Citation:** Canny, J. (1986). *IEEE TPAMI* PAMI-8(6), 679–698. https://doi.org/10.1109/TPAMI.1986.4767851
- **PDF:** `/Users/jusrogers/Masters/papers/canny1986_computational_approach_edge_detection_TPAMI-summary.pdf` (page 1 = AI summary)
- **Source:** local copy (IEEE Xplore publisher PDF, GMU licence stamp "Downloaded on October 17, 2026"), copied from `/Users/jusrogers/Masters/GGS680/references/Canny 1986. A computational approach to edge detection.pdf` (original left in place). Licensed copy: keep for personal use.
- **Validation:** PDF, 7.32 MB, 20 pages (Read tool error "This PDF has 20 pages"; pdfinfo 20) = 679–698; title/author/DOI match Crossref; Conclusions (§X), references and biography present. PASS.
- **Read:** pp. 679–698 in full (variational derivation §III–IV and references read for structure).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Hysteresis thresholding (§VI, pp. 689–690) — what Canny actually does
- Problem, **streaking**: with one threshold T1 and an edge whose response averages T1, "We expect the contour to be above threshold only about half the time. This leads to a broken edge contour." (p. 690)
- Rule: "If any part of a contour is above a high threshold, those points are immediately output, as is the entire connected segment of contour which contains the points and which lies above a low threshold." (p. 690)
- Effect: "The probability of streaking is greatly reduced because for a contour to be broken it must now fluctuate above the high threshold and below the low threshold. Also the probability of isolated false edge points is reduced because the strength of such points must be above a higher threshold." (p. 690)
- **Ratio: "The ratio of the high to low threshold in the implementation is in the range two or three to one."** (p. 690). Fig. 7: image thresholded at T1, at 2T1, and with hysteresis using both (576 × 454 image).
- Thresholds are **noise-adaptive**: noise is estimated by Wiener-filtering the operator output and taking a **global histogram**; "the positions of the low percentiles (say less than 80 percent) will be determined mainly the noise energy" (p. 689). "The thresholds were set according to the amount of noise in the image" (§X, p. 697). Exact percentile/multiplier for T_high is not given.
- Hysteresis acts on **contours** (connected chains of non-maximum-suppressed edge points), not areas; connectivity rule (4/8) is not specified.

## 2. Rest of the paper (for context)
- Criteria: detection (SNR, eq. 3), localisation (eq. 9), single response (noise-maximum spacing x_max = kW, eqs. 12–13). Step-edge uncertainty principle: Σ(f_w) = √w Σ(f), Λ(f'_w) = Λ(f')/√w (eq. 21). Optimal step operator ≈ first derivative of Gaussian (ΣΛ ≈ 0.92 vs optimal 1.12; ~20% worse; r ≈ 0.51 vs 0.576) (pp. 687–688).
- 2-D: edge = maximum of |∇(G∗I)| along n = ∇(G∗I)/|∇(G∗I)| (eqs. 45–48). Multiple widths combined by feature synthesis (σ = 1 and 2, or 1 and 5, Figs. 8–9). Directional masks: 6 orientations, 5 samples, d/σ ≈ 1.4 (p. 696).

## 3. How to apply to our pipeline
- **`sn8_cloudsym.change_gate` (task B, `low`)**: high = 71 (dark-rise Otsu cut), lows `HYSTERESIS_LOWS = (50, 35, 20)` → high/low ratios **1.42, 2.03, 3.55**. Canny's implementation range 2–3 : 1 corresponds to **low ≈ 24–36** for high = 71. So: low = 35 is inside Canny's range; low = 50 is tighter than he used; low = 20 is looser. Report this when choosing among arms; consider adding low = 24 (ratio ≈ 3.0) as the other end of Canny's range. (These are his values for gradient magnitude on photographs, not for dark-channel change; the ratio is a starting point, not a validated constant for clouds.)
- **Noise-adaptive cut (Canny's own threshold rule):** estimate the noise of the dark-channel change d on clear ground (e.g. a robust spread of d over pixels outside any gate, MAD × 1.4826, or a low percentile of |d|), and set low = k_low × noise, high = k_high × noise with k_high/k_low = 2–3. This makes the gate adapt per tile/scene, matching our universality rule, instead of a fixed 71 learned on the training tiles.
- **Area vs contour:** Canny grows along 1-pixel contours after non-maximum suppression; we grow area blobs with `ndi.label`. State the connectivity used (8-connected is the closer analogue of following a contour in any direction). The `grow="seed"` (seed blob itself ≥ 2,500 m²) and `grow="grown"` variants are our extensions; Canny's rule is closest to "grown" with no size test (any point above high seeds its connected low segment).
- **Streaking analogue:** a thin cloud fringe whose rise hovers around 71 fragments into pieces under a single cut (some pass the 2,500 m² test, some don't) — exactly the failure hysteresis was designed for, which is the principled argument for task B.
- **Feasibility:** trivial (scipy.ndimage label / skimage.filters.apply_hysteresis_threshold(d, low, high) does exactly Canny's rule on an image), grey, no SAR/NIR.

## 4. Key quotes
- "If any part of a contour is above a high threshold, those points are immediately output, as is the entire connected segment of contour which contains the points and which lies above a low threshold." (p. 690)
- "The ratio of the high to low threshold in the implementation is in the range two or three to one." (p. 690)
- "the edge detector will be susceptible to streaking if it uses only a single threshold" (p. 689)
