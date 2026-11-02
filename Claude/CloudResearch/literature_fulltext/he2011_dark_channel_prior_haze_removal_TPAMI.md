# Coder handoff: He, Sun & Tang (2011), Single Image Haze Removal Using Dark Channel Prior

- **Citation:** He, K., Sun, J., & Tang, X. (2011). *IEEE TPAMI* 33(12), 2341–2353. https://doi.org/10.1109/TPAMI.2010.168
- **PDF:** `/Users/jusrogers/Masters/papers/he2011_dark_channel_prior_haze_removal_TPAMI-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** author copy, https://people.csail.mit.edu/kaiming/publications/pami10dehaze.pdf
- **Validation:** PDF, 13 pages = published range 2341–2353; title/authors/DOI match Crossref; references and Discussion present. PASS.
- **Read:** pp. 2341–2353 in full (text extraction; equations reconstructed from the extraction, all legible).
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm, step by step
1. **Haze model** (eq. 1, p. 2342): `I(x) = J(x) t(x) + A (1 − t(x))`.
   - `I` observed intensity; `J` scene radiance (haze-free); `A` global atmospheric light (one value per channel); `t ∈ [0,1]` transmission, "the portion of the light that is not scattered and reaches the camera".
   - Homogeneous atmosphere: `t(x) = exp(−β d(x))` (eq. 2), `β` scattering coefficient, `d` depth.
2. **Dark channel** (eq. 5, p. 2343): `J_dark(x) = min_{y∈Ω(x)} ( min_{c∈{r,g,b}} J_c(y) )`. Ω(x) is a square patch centred on x. The two minimum operators commute.
3. **Prior** (eq. 6): for a haze-free outdoor image, outside sky, `J_dark → 0`. Statistics (p. 2344): 5,000 Flickr images resized to max side 500 px, 15 × 15 patch: ~75% of dark-channel pixels are 0; 90% below 25 (8-bit).
4. **Transmission** (eqs. 7–11, p. 2345): normalise by A per channel, assume t constant in the patch (`t̃`), take the dark channel of both sides:
   `min_Ω min_c (I_c/A_c) = t̃ · min_Ω min_c (J_c/A_c) + (1 − t̃)` (eq. 8). Prior sets the J term to 0, so
   `t̃(x) = 1 − ω · min_Ω min_c (I_c(y)/A_c)` (eq. 12), **ω = 0.95** ("application based", fixed to 0.95 for all results).
   - Generalisation (eq. 13): `I = J t1 + A (1 − t2)`; the dark channel estimates t2 (the additive veil) only.
5. **Refinement, soft matting** (eqs. 15–17, p. 2345–2346): minimise `E(t) = tᵀ L t + λ (t − t̃)ᵀ (t − t̃)`, L the matting Laplacian (Levin et al. 2006) with regulariser ε in each window; **λ = 10⁻⁴**; solve `(L + λU) t = λ t̃` by PCG. Then "we perform a bilateral filter on t to smooth its small scale textures" (p. 2346).
   - Why: raw t̃ — "The main problems are some halos and block artifacts. This is because the transmission is not always constant in a patch" (p. 2345).
6. **Atmospheric light** (p. 2347): "pick the top 0.1 percent brightest pixels in the dark channel … Among these pixels, the pixels with highest intensity in the input image I are selected as the atmospheric light." Beats the brightest-pixel rule, which can land on "a white car or a white building".
7. **Recovery** (eq. 22, p. 2348): `J(x) = (I(x) − A) / max(t(x), t0) + A`, **t0 = 0.1** ("a typical value"), because where t → 0 "the directly recovered scene radiance J is prone to noise". Exposure is raised afterwards for display only.
8. **Patch size** (§4.5, p. 2348): 15 × 15 on 600 × 400 images. 3 × 3: prior less accurate, result "oversaturated"; large patch: "halos near depth edges may become stronger". 30 × 30 slightly hazier than 15 × 15. Min filter by van Herk's O(N) algorithm.
9. **Greyscale** (p. 2349): "Our approach also works for gray-scale images if there are enough shadows. Cityscape images usually satisfy this condition. In this case, we omit the operator min_c in the whole derivation." (Fig. 13.)

## 2. Inputs, outputs, data needs
- Input: one hazy RGB (or grey) image, 8-bit; no reference date, no SAR, no NIR. Output: J (dehazed), t (and depth up to scale).
- Runtime: 10–20 s for 600 × 400 on a Pentium 4 (soft matting dominates).

## 3. Quantitative results to compare against
- None numerical on dehazing quality: all comparisons are visual (Figs. 12–17, vs Tan, Fattal, Kopf, Photoshop auto-curve, unsharp mask, histogram equalisation). The only numbers are the prior's statistics (75% zeros, 90% < 25).

## 4. Stated limitations (p. 2352)
- Prior invalid "when the scene objects are inherently similar to the atmospheric light and no shadow is cast on them (such as the white marble)" → t underestimated, haze overestimated.
- "the constant-airlight assumption may be unsuitable when the sunlight is very influential" (Fig. 19).
- t is wavelength-dependent for thin haze at km distance; model assumes common t across channels.

## 5. How to apply to our pipeline
- **`sn8_clouds.dark_channel` (41 px min, then 41 px box blur):** the paper's dark channel is the min filter alone (eq. 5). The box blur is our addition. Refinement in the paper is soft matting + bilateral (2011) — not a box blur. Action: compute the raw min-filter dark channel for t; if smoothing is wanted, use the refinement step (see He 2013 handoff: max filter, then guided filter with the hazy image as guide).
- **Window size:** 15 px on 600 × 400 ≈ 2.5% of the short side. Our 41 px at 0.5 m (20 m) is our own choice; the paper's trade-off (small = oversaturation/noise, large = halos) is the knob. For the reference variant the "oversaturation" cost mostly disappears because J's dark channel is measured, so a smaller window near edges is defensible (evidence 10 arm d).
- **`sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym._correct`:** our `t = (A − dark(after)) / (A − tone(dark(before)))` is eq. 8 solved for t̃ with the J term measured from the before date instead of set to 0 — consistent with the paper's derivation. Keep `t ≥ t0`: paper clamps at 0.1; our T_MIN = 0.2 + abstain is stricter (fine).
- **`DARKREF_GUIDED = False`:** the paper says raw t gives halos; refinement is part of the method. Re-test with the published recipe (He 2013 handoff) before concluding refinement hurts.
- **Airlight (`AIRLIGHT_SHARE = 0.001`):** matches the paper exactly. Guard: on 0.5 m tiles a large white roof inside the top 0.1% dark channel could still win; consider taking A as the median of the top-0.1% set restricted to the cloud gate.
- **ω:** paper 0.95 for display; for analysis ω = 1 is our rule (paper: "application based").
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** fully feasible. Greyscale works "if there are enough shadows" — suburban 0.5 m tiles have tree/house shadows within 20 m, but flooded open fields and large roofs may not. Using RGB (min over channels) instead of grey would strengthen the prior; worth an arm since the Maxar tiles are RGB.

## 6. Key quotes
- "The main problems are some halos and block artifacts. This is because the transmission is not always constant in a patch." (p. 2345)
- "We set a small λ (10⁻⁴ in the experiments) so that t is softly constrained by t̃." (p. 2346)
- "If the patch size is too large, halos near depth edges may become stronger." (p. 2348)
- "Our approach also works for gray-scale images if there are enough shadows." (p. 2349)
