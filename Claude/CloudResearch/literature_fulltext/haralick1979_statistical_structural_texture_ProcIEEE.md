# Coder handoff: Haralick (1979), statistical and structural approaches to texture

- **Citation:** Haralick, R. M. (1979). Statistical and structural approaches to texture. *Proceedings of the IEEE*
  67(5), 786–804. https://doi.org/10.1109/PROC.1979.11328
- **Copy read:** the published IEEE Xplore PDF (GMU-licensed download that Justin placed in `~/Masters/papers/`). 23 PDF
  pages: the 19 article pages (786–804) plus 4 appended higher-resolution figure plates (Figs. 1, 8, 9, 10–11). The
  OCR text layer is noisy; the equations and Fig. 7 were checked on the rendered page (p. 792).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/haralick1979_statistical_structural_texture_ProcIEEE-summary.pdf`
- **Validation:** real PDF; title, author, volume, issue and pages 786–804 match Crossref; conclusion and references
  present. PASS (published version).
- **Pages read:** 786–804 in full; the reference list (pp. 802–804) skimmed; the plates viewed.
- **Supports ranked fix (evidence 21):** #7, haze-invariant texture. It gives invariance theory only, with no haze
  experiment.

## What the paper is
A survey. It contains no new experiment; the accuracies it quotes are other studies' results. Texture = tonal
primitives + their spatial organisation (p. 786). "When a small-area patch of an image has little variation of tonal
primitives, the dominant property of that area is tone. When a small-area patch has wide variation of tonal primitives,
the dominant property of that area is texture" (p. 786).

## Grey-tone co-occurrence (GLCM), exact definition (pp. 791–792)
- Image I: L_r × L_c → G, with G = {1, …, N_g} quantized grey tones.
- Unnormalised counts for distance d and angle a ∈ {0°, 45°, 90°, 135°}, e.g. 0°:
  `P(i, j, d, 0°) = #{((k,l),(m,n)) : k − m = 0, |l − n| = d, I(k,l) = i, I(m,n) = j}`.
  45°: (k − m = d, l − n = −d) or (k − m = −d, l − n = d). 90°: |k − m| = d, l − n = 0. 135°: (k − m = d, l − n = d) or
  (k − m = −d, l − n = −d).
- The matrices are symmetric, P(i, j; d, a) = P(j, i; d, a). Distance metric: ρ((k,l),(m,n)) = max{|k − m|, |l − n|}.
- Worked example: a 4×4 image with 4 grey tones, all four distance-1 matrices (Fig. 6, p. 792).

## Features listed (Fig. 7, p. 792), P_ij = normalised co-occurrence probability
| Feature | Formula as printed |
|---|---|
| Uniformity or energy | Σ P_ij² |
| Entropy | Σ P_ij log P_ij (printed without the minus sign) |
| Maximum probability | max P_ij |
| Contrast | Σ \|i − j\|^k (P_ij)^λ |
| Inverse difference moment | Σ_{i≠j} (P_ij)^λ / \|i − j\|^k |
| Correlation | Σ (i − μ)(j − μ) P_ij / σ² |
| Probability of a run of length n for grey tone i (Markov assumption) | (P_i − P_ii)² P_ii^{n−1} / P_i^n, with P_i = Σ_j P_ij |

The paper uses general exponents k and λ. The common forms (contrast with k = 2, λ = 1; "homogeneity" 1/(1 + (i − j)²))
are later conventions, not printed here. Note: **"homogeneity" and "ASM" do not appear under those names in this paper.**

## Other definitions that may be useful
- **Textural transform (pp. 793–795):** J(i, j) = sum over the 4 directions of h_a(I(i,j), neighbour), with each h_a
  = the co-occurrence probability for that direction. White = common local pattern, black = rare. A per-pixel "how
  typical is this texture" map (Landsat band 5, 100 × 100 subimages).
- **Run lengths (p. 797, Galloway):** p(i, j) = number of runs of grey tone i and length j; short-run emphasis, long-run
  emphasis, grey-level non-uniformity, run-length non-uniformity, in 4 directions. The OCR of these formulas is unusable;
  only the names were confirmed.
- **Edge per unit area (p. 800):** mean gradient magnitude in a window ("a defocused gradient image").
- **Relative extrema density (p. 800):** count 1-D relative minima g(i) < g(i ± 1) and maxima per window; count a
  plateau once (1/N per pixel of an N-pixel plateau); heights and widths of extrema as extra properties (Fig. 15).
- **Generalised co-occurrence (p. 802):** P(t1, t2) = #{(q1, q2) ∈ S : f(q1) = t1, f(q2) = t2} / #S over primitives Q
  (regions), with property f and spatial relation S.

## Invariance statements (the part evidence 21 uses), with pages
- Spatial-frequency approaches: "one of the inherent problems is in regard to gray tone calibration of the image. The
  procedures are not invariant under even a monotonic transformation of gray tone. To compensate for this, probability
  quantizing can be employed. But the price paid for the invariance of the quantized images under monotonic gray tone
  transformations is the resulting loss of gray tone precision in the quantized image" (p. 787).
- Co-occurrence: "it characterizes the spatial interrelationships of the gray tones in a textural pattern and can do so
  in a way that is invariant under monotonic gray tone transformations. Its weakness is that it does not capture the
  shape aspects of the tonal primitives. Hence, it is not likely to work well for textures composed of large-area
  primitives" (p. 787).
- Relative extrema: "Because of their invariance under any monotonic gray scale transformation, relative extrema
  primitives are likely to be very important" (p. 801).
- Scale: "For any smooth gray-tone surface, there exists a scale such that when the surface is examined, it has no
  texture" (p. 788).

**Coder's caution.** The co-occurrence invariance holds only when the quantization is tied to the grey-tone
distribution (probability quantizing), so that a monotonic change only relabels levels in order. With fixed bins,
contrast and correlation use the level values i and j and do change. Haralick states the invariance without spelling
this out. He also does not discuss haze, blur, noise or the loss of distinct levels when a range is compressed.

## Comparable results (quoted from reviewed studies; not new experiments)
- Co-occurrence features: 82% on 8 aerial terrain classes; 84% on Landsat Monterey Bay with spectral + textural
  features, 64 × 64 subimages, 7 classes; 89% on 5 sandstone classes (p. 793).
- Run lengths (Galloway): about 83% on 6 categories (p. 797).
- Kirvida & Johnson: 74% spectral only → 99% with transform texture, 8 × 8 Landsat subimages (p. 789).
- Weszka, Dyer & Rosenfeld: spatial-frequency features "perform significantly poorer" than the others (p. 787).

## How to apply to our pipeline
- **`sn8_glcm.py` already follows Haralick's remedy.** `quantize()` uses 32 equal-probability levels per date, which is
  his "probability quantizing". But the quantiles are taken over the **whole tile's** valid pixels. That cancels one
  global monotonic change per date (exposure, a DRA stretch). It does **not** cancel haze that varies across the tile:
  a hazy patch is squeezed into fewer of the tile's quantile levels, so contrast and entropy fall there.
  - **Arm 7-a (cheap, testable):** quantize per window (or per road strip) instead of per tile, with equal-probability
    levels computed inside the window. Under an affine haze map within the window (t, A constant), the quantized window
    is unchanged except for ties, so all five props should be flat in t. Cost: the window's own grey-level contrast is
    lost (Haralick's "loss of gray tone precision"), so keep one separate contrast channel (local std, or std / t̂), as
    in evidence 21's arm 5-i.
  - Measure on the other agent's haze–texture data: plot each prop against estimated t for tile-level vs window-level
    quantizing.
  - Caveat: equal-probability levels need enough distinct grey values. In haze with t ≈ 0.3 on uint8, a window may span
    only about 0.3 × its clear range, so 32 levels may exceed the distinct values and produce ties. Try 8 or 16 levels
    as a sweep.
- **`sn8_texture.py`:** LBP (already there) is the other monotonic-invariant family. Relative-extrema density (p. 800)
  is a third, very cheap invariant feature (count local maxima/minima per window, plateaus counted once). It could be
  added as one more family; it is noise-sensitive, so smooth first (Mitchell et al., as cited on p. 800).
- **Semivariogram, Gabor, Laws, wavelet energies in `sn8_texture.py`** are spatial-frequency/variance measures. Haralick
  says these are not invariant even under monotonic changes; they scale with t. They are the ones to normalise by t̂
  (fix 7's "t̂-normalised contrast") or to accept as haze-sensitive.
- **Not useful here:** structural-element morphology (binary images only), autoregressive and mosaic models.
- **Feasibility with RGB uint8 0.5 m, one pre-storm date, no NIR/SWIR/SAR:** fully feasible. Everything is single-band
  greyscale and needs no second date. The paper offers no haze evidence, so the effect must be measured on our tiles.
