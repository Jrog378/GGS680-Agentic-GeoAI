# Coder handoff: Ojala, Pietikäinen & Mäenpää (2002), multiresolution grey-scale and rotation invariant LBP

- **Citation:** Ojala, T., Pietikäinen, M., & Mäenpää, T. (2002). Multiresolution gray-scale and rotation invariant texture
  classification with local binary patterns. *IEEE TPAMI* 24(7), 971–987. https://doi.org/10.1109/TPAMI.2002.1017623
- **Copy read:** publisher PDF already in `~/Masters/papers/` (IEEE Xplore, downloaded through GMU on 2026-10-23, so not
  a new download).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ojala2002_lbp_rotation_invariant_TPAMI-summary.pdf`. The plain
  copy was deleted after the 18-page check.
- **Validation:** PDF, 17 pages = pp. 971–987; title, authors and DOI match Crossref; discussion and references present.
- **Pages read:** 971–987 (all); Tables 4–6 read from the rendered pp. 982–983.
- **Supports ranked fixes (evidence 21):** #7 (haze-invariant texture: LBP-riu2 plus a separate contrast channel).

## Algorithm (exact)
1. **Neighbourhood:** P points at radius R around the centre g_c: `g_p = (−R sin(2πp/P), R cos(2πp/P))`.
   Off-grid points are bilinearly interpolated (p. 973, Fig. 1).
2. **LBP (Eq. 7):** `LBP_{P,R} = Σ_{p=0}^{P−1} s(g_p − g_c) 2^p`, with `s(x) = 1 if x ≥ 0 else 0` (Eq. 6).
3. **Rotation invariance (Eq. 8):** `LBP^{ri} = min_i ROR(LBP, i)`.
4. **Uniformity (Eq. 10):** U = number of 0/1 transitions around the circle.
5. **riu2 code (Eq. 9):** `LBP^{riu2} = Σ s(g_p − g_c) if U ≤ 2, else P+1`. That gives P+2 labels. Label P = all ones,
   i.e. "flat area or dark spot"; label 0 = bright spot; 1..P−1 = edges and curvature (p. 974).
6. **Contrast (Eq. 11):** `VAR_{P,R} = (1/P) Σ (g_p − μ)²`, with `μ = (1/P) Σ g_p`. It is shift-invariant, not
   scale-invariant. Quantise VAR into B bins with equal-frequency cuts from the pooled training data (p. 975).
7. **Features:** histograms of riu2 codes (P+2 bins), optionally joint with VAR bins (2-D histogram).
   Rule of thumb: about 10 entries per bin on average (p. 975).
8. **Classifier (Eq. 12):** `L(S, M) = Σ_b S_b log M_b`, a simplified G-statistic (Eq. 13). Multiresolution sums L over
   operators (Eq. 14), assuming independence.
9. **Settings used:** (P, R) = (8, 1), (16, 2), (24, 3) "as a reasonable starting point … no guarantee that they produce
   the optimal operator" (p. 982). In a sweep of 189 operators the best was LBP^{riu2}_{22,4} at 97.2% (p. 982).
   Pre-processing in experiment 2: RGB→I = 0.299R + 0.587G + 0.114B (Eq. 15, which prints "0.114R", a typo for B), then
   each 128 × 128 sample normalised to mean 128 and s.d. 20 (pp. 980–981).

## Results to compare against
- Uniform share of 3 × 3 patterns: 87.2% (Brodatz) and 89.7% (Outex) for LBP_{8,1} (p. 976).
- Brodatz, trained at one angle: average accuracy 98.3% (16,2) and 98.5% (24,3) (p. 980).
- Outex TC_00010, rotation only (Table 4): LBP riu2 (8,1) 85.1, (16,2) 88.5, (24,3) 94.6%. VAR: 91.2, 90.7, 86.2%.
  Joint: 95.4, 97.2, 97.8%. Best overall 97.9% (8,1 + 24,3 joint). Wavelet baseline 80.4% (p. 984).
- **Outex TC_00012, rotation + different illuminant (Table 6):** LBP (8,1) 67.5/62.7, (16,2) 81.2/74.1,
  (24,3) 84.0/80.5% for tl84/horizon. Joint (24,3) 86.6/87.2%. "classification performance deteriorated clearly when the
  classifier was evaluated with samples captured under different illumination" (p. 984).

## Invariance statement and its limits (key quotes)
- "LBP_{P,R} operator is by definition invariant against any monotonic transformation of the gray scale, i.e., as long as
  the order of the gray values in the image stays the same, the output … remains constant" (p. 973).
- Texture has "two orthogonal properties: spatial structure (pattern) and contrast"; LBP "by definition, discards the
  other important property of local image texture, i.e., contrast" (p. 972).
- Under a real illuminant change, which alters spectra and local shadowing and is therefore not monotonic, accuracy drops
  by 10–23 points (Table 6). The authors could not separate spectral from geometric causes (p. 984).
- "our operators may not be suitable for discriminating textures where the dominant features appear at a very large
  scale" → increase R (p. 985).

## How to apply to our pipeline
- **Current code:** `sn8_texture.py` already computes `local_binary_pattern(g8, 8, 2, method="uniform")`, i.e. riu2 with
  P = 8, R = 2 px = 1 m, plus `lbp_entropy`, `lbp_flat` and `lbp_edge`. skimage's "uniform" matches Eq. 9.
- **Fix 7 arm (haze-invariant texture):**
  1. Add multiresolution riu2 histograms at (8,1), (16,2) and (24,3) px, plus a ground-scale set (e.g. R = 4 and 8 px =
     2 and 4 m) because 0.5 m roads and debris are larger than 1.5 px.
  2. Feed the full P+2-bin histograms per window, not only the entropy, into the RF.
  3. Keep `VAR_{P,R}` (or local std) as a **separate** contrast channel, as the paper does, so haze attenuation shows in
     VAR and not in LBP.
  4. Test invariance directly. On the other agent's haze–texture data (evidence 20), plot each feature against estimated t.
     LBP histograms should be flat in t until blur and quantisation dominate; VAR should scale about t².
- **Watch for:** with 8-bit data and thin haze, the local range is compressed to about t·range. In flat areas many
  differences become 0, and s(0) = 1, so codes drift toward label P ("flat"). Consider a small tolerance, s(x) = 1 if
  x ≥ τ (an extension, not in this paper), and report its effect.
- **Normalisation:** the paper normalises each sample to mean 128 and s.d. 20 before LBP/VAR. For VAR on hazy vs clear
  windows, do **not** normalise, or the haze signal is removed (our choice, contrary to the paper's setup).
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** fully feasible on grey or per channel. The
  paper is greyscale only; per-channel LBP is an extension.
