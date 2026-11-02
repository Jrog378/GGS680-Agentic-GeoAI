# Coder handoff: Lowe (2004), Distinctive image features from scale-invariant keypoints (SIFT)

- **Citation:** Lowe, D. G. (2004). *IJCV* 60(2), 91–110. https://doi.org/10.1023/B:VISI.0000029664.99615.94
- **Copy read:** author's accepted manuscript ("Accepted for publication in the International Journal of Computer Vision,
  2004", dated 5 Jan 2004), https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf. It has 28 manuscript pages; the journal version
  has 20 (91–110). The manuscript layout differs, so page numbers below are the **manuscript's**.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/lowe2004_sift_scale_invariant_keypoints_IJCV-summary.pdf`
- **Validation:** real PDF; title and author match Crossref; conclusions, acknowledgements and references present. PASS
  (accepted manuscript, not the typeset version).
- **Pages read:** 1–28 (all). References were checked, not read entry by entry.
- **Supports ranked fixes (evidence 21):** #7 (haze-invariant texture: unit-normalised gradient-orientation histograms).

## What we need: the descriptor, used densely without keypoint detection (§6.1, pp. 14–16)
1. Smooth the image (Lowe uses the keypoint's Gaussian scale) and compute gradients with pixel differences (p. 13):
   `m = sqrt((L(x+1,y) − L(x−1,y))² + (L(x,y+1) − L(x,y−1))²)`, `θ = atan2(L(x,y+1) − L(x,y−1), L(x+1,y) − L(x−1,y))`.
2. Take a 16 × 16 sample window and weight m by a Gaussian with σ = half the window width.
3. Accumulate into a 4 × 4 grid of 8-bin orientation histograms (128-D), with trilinear interpolation (weight 1 − d per
   dimension).
4. Rotation: rotate coordinates and θ to the dominant orientation (36-bin histogram, Gaussian σ = 1.5 × scale; extra
   orientations within 80% of the peak). For roads, a fixed north-up frame may be preferable. That is our choice.
5. **Illumination step (p. 16):** normalise the vector to unit length → clip each element at **0.2** → renormalise.

Detector parameters, for reference only (not needed for dense features): DoG with s = 3 scales per octave, σ = 1.6
(p. 10), image doubled (p. 10), contrast threshold `|D(x̂)| < 0.03` discarded (p. 11), edge threshold r = 10,
`Tr(H)²/Det(H) < (r+1)²/r` (p. 12). Matching uses a ratio test of 0.8, which removes 90% of false matches and loses
< 5% of correct ones (p. 20).

## Invariance argument (p. 16) — key quotes
- "A change in image contrast in which each pixel value is multiplied by a constant will multiply gradients by the same
  constant, so this contrast change will be canceled by vector normalization."
- "A brightness change in which a constant is added to each image pixel will not affect the gradient values."
- "Therefore, the descriptor is invariant to affine changes in illumination."
- "However, non-linear illumination changes can also occur due to camera saturation or due to illumination changes that
  affect 3D surfaces with differing orientations by different amounts." The 0.2 clip reduces "the influence of large
  gradient magnitudes", and "the value of 0.2 was determined experimentally using images containing differing
  illuminations for the same 3D objects".
- For 3D objects "illumination change is more disruptive" (p. 25). Features use "only a monochrome intensity image"
  (p. 25).

## Limits that matter for haze
- **Detection is not contrast-invariant:** the 0.03 absolute threshold (p. 11) means hazy, low-contrast areas yield fewer
  keypoints. Use the descriptor densely on a grid, not SIFT keypoints.
- **Clipping at 0.2 is non-linear:** after normalisation it is applied to relative magnitudes, so it is still
  scale-invariant. It is only "invariant" if the gain is uniform over the 16 × 16 window.
- The paper's tests use synthetic brightness/contrast changes and noise on 32 natural images ("aerial photographs" among
  them, p. 8). There is no haze, blur or remote-sensing evaluation.

## How to apply to our pipeline
- **`sn8_texture.py` (fix 7):** add `dense_orientation_hist(g, valid, cell=4px, grid=4, bins=8)`, e.g.
  `skimage.feature.hog(..., block_norm='L2-Hys')`. L2-Hys = L2 normalise, clip at 0.2, renormalise, which is Lowe's
  scheme. Or write it directly.
  - Window: 16 × 16 px = 8 m at 0.5 m; also try 32 px = 16 m (road width plus margins).
  - Pair it with a separate magnitude/contrast channel (mean gradient magnitude), as with LBP + VAR.
- **Test the invariance on our data (evidence 20 agent's haze curves):** the normalised histogram should be flat in t
  while mean gradient magnitude scales roughly with t. Where it is not flat (blur at thin-cloud edges, 8-bit
  quantisation), report the t below which it breaks.
- **Haze model link (our derivation, not Lowe's):** within a window of constant t and A, I = tJ + A(1 − t) is affine, so
  the descriptor is unchanged. This needs t constant over 8–16 m, which is plausible for thin cloud interiors but not at
  edges.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** fully feasible on grey. With uint8 and t ≈ 0.3,
  local differences fall to a few DN, so orientation becomes noisy; add a minimum-magnitude guard.
