# Coder handoff: Zhang & Xiao (2014), cloud detection in RGB colour aerial photographs

- **Citation:** Zhang, Q., & Xiao, C. (2014). Cloud detection of RGB color aerial photographs by progressive refinement
  scheme. *IEEE TGRS* 52(11), 7264–7275. https://doi.org/10.1109/TGRS.2014.2310240
- **Copy read:** authors' accepted manuscript (LaTeX, dated 5 Mar 2014), http://graphvision.whu.edu.cn/papers/qing2014.pdf
  (found through Semantic Scholar's open-access field). 12 pages; the published range 7264–7275 is also 12 pages.
  Page numbers below are the **manuscript's** 1–12, not the journal's.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/zhang2014_cloud_detection_rgb_aerial_photographs_TGRS-summary.pdf`
- **Validation:** real PDF; title and authors match Crossref; conclusion, references and biographies present. The
  manuscript header carries template boilerplate ("received April 19, 2005"), so the dates are not meaningful.
- **Pages read:** 1–12 (all); equations checked on rendered pp. 3 and 6.
- **Supports ranked fixes (evidence 21):** #1 (RGB colour features: brightness/hue significance), #3 (soft edge instead
  of a fixed fade; component-size threshold), #2/#3 (Otsu clamped by data-derived bounds as an example of a
  constrained threshold), #7 (low-detail cue = haze attenuates texture).

## Algorithm (exact steps)
**0. RGB → HSI (Eqs. 1–3, p. 3)**
```
I  =  (R + G + B)/3
V1 = −(√6/6)R − (√6/6)G + (√6/3)B
V2 =  (1/√6)R − (2/√6)G
S  = sqrt(V1² + V2²)
H  = (atan(V2/V1) + π) · 255/(2π)     (printed condition "if V1 ≠ 1" — almost certainly a typo for V1 ≠ 0; use atan2)
```
(The text also swaps "intensity-equivalent" and "hue-equivalent"; ignore it.)

**1. Significance map (Eq. 4, p. 3):** `W = (I + ε)/(H + ε)`, with I and H scaled to [0, 1] and ε = 1.0. Apply a bilateral
filter to W, then rescale it to [0, 255].

**2. Coarse mask (Eqs. 5–7, pp. 4–5):**
- Find the Otsu threshold `T_Global` on the histogram of W.
- Clamp it: `T_opt = 100 if T_Global < 100; 150 if T_Global > 150; else T_Global`.
- `R_coarse = (W ≥ T_opt) AND (50 ≤ H ≤ 80)`, with H on the 0–255 scale.
- Bounds come from 500 cloudy photos (Flickr and search engines) with hand-cut cloud: ">95% of the true cloud pixels have
  intensity not less than 100"; hue "almost all … between 50 and 80" (p. 4).

**3. Detail map (Eqs. 8–15, pp. 5–7):**
- Iterated bilateral filter on intensity, I'_0 = I. The window Ω is 7 (p. 6).
- Spatial σ: σs,0 = 2, σs,1 = √3·σs,0, σs,j = 2^(j−1)·σs,j−1.
- Range σ: σr,0 = R/10, where R is the max intensity; σr,j = σr,j−1.
- Detail levels: `D_j = I'_j − I'_{j−1}`, j = 1..M, with M = 4.
- `I_detail = (1/λ) Σ_{j=2..M} ω_j D_j`, with `λ = Σ ω_j` and `ω_j = G_{σd} * exp(|D_j|)` (Gaussian-smoothed, σd = 7).
  D_1 is skipped because of noise. The printed formula sums signed D_j. Use |D_j| or the magnitude of the result, because
  the paper's intent is "amount of detail".
- Dilate I_detail twice with a 7×7 structuring element.
- Otsu threshold → `R_detail = I_detail < T_detail` (low detail = cloud-like).
- `R_finer = R_coarse ∩ R_detail`. Then apply a median filter, drop connected components under `T_size = 120` px ("a
  larger T_Size can be selected if the aerial photographs having high resolution", p. 7), and fill holes (`imfill`).

**4. Guided feathering (Eqs. 16–19, pp. 7–8):** guided filter (He et al.), with input P = R_finer, guide = the colour
photo, radius = 60 and ε = 1e-6. Threshold the soft output at `T_binary = 60` (0–255 scale). A smaller value gives more
semitransparent pixels plus more false positives (p. 8).

## Outputs
Binary cloud mask, plus the soft guided-filter matte (usable as a per-pixel cloud-edge weight).

## Results to compare against (pp. 8–11)
- Error rate `ER = (CN + NC)/TN` (Eq. 20), on 5 photos (Table I): ours 1.73, 4.73, 1.85, 4.03 and 1.41%. k-means scored
  13.8–33.1%, mean-shift 12.6–27.1% and graph-based 26.3–41.6%.
- On 4 photos (Table II): ours 1.34, 5.18, 2.14 and 5.71%, with no user input. Graph-cut scored 3.4–17.7% and robust
  matting 2.0–13.0%, both with scribbles.
- Runtime: under 2 s per 1 Mpx (Tables III–IV).
- Only nine evaluation images; no GSD stated; no public dataset; no separate thin-cloud score.

## Limitations (stated, p. 11)
- "bright non-cloud regions that have little details": these "basically meet the properties … higher intensity, smoother,
  lower chromatic, and appearing in terms of clusters", so are mistaken for cloud.
- "When clouds in aerial photographs are extremely thin, we will fail to get an accurate detail map, and we will miss some
  cloud regions."

## Key quotes
- "cloud pixels in color aerial photographs usually have higher intensities and lower hues" (p. 1).
- Property 3: "the ground covered by cloud veil usually has little details as the ground object features are attenuated by
  cloud veil" (p. 3).
- Property 5: "Semitransparent cloud pixels are often present around the boundaries of cloud regions" (p. 3).

## How to apply to our pipeline
- **`sn8_cloudspot.py` → `classical_cues()` (fix 1):** add per-pixel `W = (I+1)/(H+1)` (I and H in [0, 1]), hue H, and
  saturation S from the RGB tile as extra cues. Let the random forest learn the cut-offs instead of hard-coding 100/150
  and 50–80. Those constants were tuned on internet photos and should only be used as a rule-based baseline arm.
- **Rule-based baseline arm:** implement the full four-stage pipeline as `zhang_xiao_mask(rgb, valid)` and score it on
  HRC_WHU folds with the same McNemar setup. It is cheap and gives a published RGB-only reference point.
- **Edge fade (fix 3):** replace the fixed 20 m fade by the guided-feathering matte. `guided_filter()` already exists in
  `sn8_clouds.py`. Use the RGB tile as the guide (He 2013: RGB guides beat grey). At 0.5 m, radius 60 px = 30 m. Sweep the
  radius and T_binary and report the curve rather than fixing them.
- **Minimum blob (fix 3):** the paper's T_size = 120 px is for unknown-GSD photos. Our 2,500 m² = 10,000 px at 0.5 m; this
  paper gives no physical basis for either value. Sweep it, as fix 3 says.
- **Texture (fix 7):** Property 3 is the same claim as Shen 2014's "low gradient". The detail map (multiscale bilateral
  residual) is a candidate haze-sensitive texture cue for `sn8_texture.py`.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** fully feasible; the paper needs only RGB.
  Main risk: turbid floodwater, wet bare soil and bright roofs are "bright, smooth, low-chroma". Report false positives on
  flooded tiles separately (fix 1). The before date can veto: low detail in *both* dates means smooth ground, not cloud
  (our extension).
