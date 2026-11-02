# Coder handoff: Gibson, Vo & Nguyen (2012), An investigation of dehazing effects on image and video coding

- **Citation:** Gibson, K. B., Vo, D. T., & Nguyen, T. Q. (2012). *IEEE Transactions on Image Processing* 21(2), 662–673. https://doi.org/10.1109/TIP.2011.2166968
- **PDF:** `/Users/jusrogers/Masters/papers/gibson2012-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 1.24 MB; 12 pages (Read tool and pdfinfo) = published range 662–673; page-1 title, authors (Gibson, Vo, Nguyen; UCSD and Samsung), TIP vol. 21 no. 2 Feb 2012 and DOI 10.1109/TIP.2011.2166968 match todo.tsv; Conclusion (p. 671), 36-item reference list (p. 672) and biographies (pp. 672–673) present. PASS.
- **Read:** PDF pp. 1–12 = journal pp. 662–673 in full (Read tool, page images), including Tables I–II, Figs. 1–11 and eqs. 1–59.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.
- **Venue / JIF rule:** IEEE TIP, above 4 (approx. 10+; general knowledge, not checked against JCR). Co-author Vo is at Samsung (company affiliation), p. 662.

## 1. Algorithm, step by step
**A. Median dark channel prior (MDCP) dehazer** (§III, pp. 663–665)
1. Dichromatic model (eq. 1, p. 663): `x̂(m,n) = x(m,n) t(m,n) + a (1 − t(m,n))`, `t = e^{−β d}`; β spatially invariant, wavelength-independent (footnote 1, p. 663).
2. He's DCP for reference (eq. 2, p. 663): `θ_D = min_{Ω} min_c x̂(k,l,c)/a(c)`, "Ω is a square shape of sizes 5 × 5 or 7 × 7"; `t_D = 1 − w θ_D`, **w = 0.95** "for most scenes" (eq. 3). Unrefined recovery (eq. 9, p. 664): `x_D = (x̂ − a) / max(t_D, ε) + a`, **ε = 0.01**.
3. **MDCP** (eq. 10, p. 664): `θ_M(m,n) = med_{k,l∈Ω(m,n)} ( min_c x̂(k,l,c)/a(c) )`, i.e. per-pixel min over channels, then a **median** (not min) over the window. The text gives the window as a **single median filter of 11 × 11** ("reduces the complexity from using at minimum two median filter passes with large kernel sizes (41 × 41) to a single median filter with a smaller kernel size (11 × 11)", p. 664).
4. `t_M = 1 − w θ_M`, **w = 0.95** (eq. 11, p. 664). Recovery `x_M = (x̂ − a) / max(t_M, ε) + a` (eq. 12), ε = 0.01. **No refinement step** (no matting, no guided filter).
5. Why it limits halos (eqs. 14–17, p. 664): in a window straddling an occlusion edge, the min picks the foreground pixel (`w(0)`) while the median picks the majority side (`w((N²−1)/2)`). Airlight estimation is not specified in this paper (it follows [13]).

**B. Compression analysis** (§IV–V, pp. 665–670), on luminance y = r₁ᵀx (eq. 19)
6. Hazy luminance `ŷ = y t + a_y (1 − t)` (eq. 19). With t constant in an N × N DCT block, every **AC coefficient is attenuated by t**: `f̂ᶻ(ν) = t_{i,j} fᶻ(ν)`, 1 ≤ ν ≤ N² − 1 (eq. 29, p. 666).
7. Uniform quantisation `f^q = ⌊f/q + 1/2⌋` (eq. 30). An AC coefficient is zeroed when |f| < q/2 (eq. 31). Hence `P[|f̂ᶻ| < q/2] = P[|fᶻ| < q/(2t)] > P[|fᶻ| < q/2]` (eqs. 34–36): **hazy blocks lose more AC coefficients, so ringing is more likely in Post** (p. 666).
8. Blocking (eqs. 37–48, pp. 666–667): with a perfect dehazer `D(ĥ) = (ĥ − a_y)/t + a_y` (eq. 42):
   - Pre: `D^Pre = y + ε_n/t` (eq. 43); after coding `+ ε_r` (eq. 45); `var = σ_y² + σ_n²/t² + σ_r²` (eq. 46).
   - Post: `D^Post = y + (ε_n + ε_r)/t` (eq. 44); `var = σ_y² + (σ_n² + σ_r²)/t²` (eq. 47).
   - `SNR^Pre ≥ SNR^Post`, equal only at t = 1 (eq. 48). The noise "is spatially varying and dependent on the depth of the scene", so blocking worsens as distance/β grow (p. 667).
9. Motion estimation (eqs. 49–59, pp. 668–669): with t constant, `SAD̂ = t · SAD` (eq. 51), so a fixed threshold τ on hazy video equals a threshold γ = τ/t on clear video (eq. 57): **haze admits more false match candidates** (eq. 59). The paper uses a 32 × 32 search region; β = 0.2–0.4 km⁻¹ in fog; with β = 0.3 km⁻¹ a 1% transmission change corresponds to ≈ 33 m depth change (eq. 56, p. 669).

## 2. Inputs, outputs, data needs
- JPEG experiment: synthetic haze on the WILD database (scene depth known) with an "arbitrarily chosen airlight"; a perfect dehazer (eq. 42) applied before or after JPEG (p. 667).
- Real image: a house photo, MDCP dehazer, both versions about 17 kB (JPEG quality 20 Pre, 45 Post) (p. 668).
- Video: real hazy coastal sequence, 728 frames, 720 × 480; H.264 High profile Level 3.0 (3.1 at 8000 kb/s, 3.2 at 10,000 kb/s); GOP IPBPB… with only 4 I frames (p. 669).
- Blocking metric: no-reference measure of [26] (Liu & Bovik 2002) (pp. 667, 670).

## 3. Quantitative results
- JPEG, matched sizes: quality 48 → 83.1 kB (Pre) vs quality 70 → 84.7 kB (Post); Post shows more ringing at building edges and more blocking in the sky (Figs. 4–5, p. 667).
- JPEG quality 5–100: Pre has "significantly fewer blocking artifacts than the Post method, particularly at smaller image sizes" (Fig. 6, p. 667).
- With deblocking [28] applied "after decompression in the Pre method and after dehazing in the Post method", luminance PSNR against the uncompressed dehazed image: "the Pre method has w [sic] higher performance close to 5 dB over the Post method" (Fig. 7, p. 668).
- Real house: blocking measure Pre 0.07, Post 0.08 (p. 668).
- H.264: Pre has higher PSNR at every bitrate (Fig. 9) and fewer blocking artefacts at every bitrate (Fig. 10) (p. 670). Table I (p. 670): Post/Pre motion-vector bits 0.99–1.27; Post/Pre residual bits 0.97–1.00.
- Subjective SCACJ test, 20 observers, 1 rejected (p. 670); Table II ITU-R averaged marks (p. 671): no compression 7.06; Pre 1000 kb/s 6.51, 750 6.31, 500 6.09, 250 4.78; Post 1000 kb/s 4.21, 750 4.17, 500 3.80, 250 2.04. Overlaps: uncompressed vs Pre 1000, and Pre 250 vs Post 1000 ("a significant compression difference by a factor of 4", p. 671).

## 4. Stated limitations
- Model assumes homogeneous, wavelength-independent scattering and "is suitable for overcast lighting. Typically, dehazing methods break down in shadow areas that are caused by direct lighting." (p. 663)
- The analysis is on luminance only (chroma subsampling ignored, p. 665), assumes t constant within a block (p. 665) and within the motion-search region (p. 669), and uses a perfect dehazer for the derivation (p. 667).
- Intra-prediction is not analysed (p. 668).

## 5. How to apply to our pipeline
**Practical rule.** The paper's rule is **dehaze before compression** (p. 671). We cannot do that: the Maxar tiles reach us already compressed, so every correction we apply is "Post". What follows for us:
1. **Detail lost under haze is gone.** AC coefficients are zeroed with probability rising as t falls (eq. 36), before we ever see the tile. No dehazer can restore road edges or water texture there. This supports our gate (t ≥ 0.2, otherwise CANNOT ASSESS) over "correct everything".
2. **Dehazing amplifies coding noise by 1/t** (eq. 44); its variance grows as 1/t² (eq. 47). Any change threshold applied after a haze correction should scale with 1/t. That is the same form as Gibson's eq. 57 for motion search (γ = τ/t).
3. **Blocking and ringing get worse after dehazing in low-t areas** (Fig. 4(e), Fig. 5(d)). Our DINOv2 feature distance and the grey guard may be reading 8 × 8 block artefacts as texture in corrected hazy areas. Where possible, check C1-type arms visually for block grids.
4. **Store our own intermediates losslessly** (PNG/npy). Never re-JPEG a dehazed tile; that is a second Post compression.
5. **Min-filter dark channels pick up coding artefacts.** Ringing creates dark undershoots next to edges, and the patch minimum selects them. A median (MDCP) or Li–Hu–Ai's mean − σ is more robust (our inference; the paper's argument for the median is about occlusion edges, p. 664).
6. Halos: the MDCP is the paper's halo fix. It is evidence 10's "median operation" source, verified here (abstract p. 662; eqs. 14–17 p. 664; Fig. 2 p. 665).

### Proposed bench arm: M1 median dark channel (MDCP)
1. On the after image: `m = min_c (I_c / A_c)` per pixel (grey: `I / A`); A by He's top-0.1% rule (same as C1).
2. `θ = median11×11(m)`; `t = 1 − 0.95 θ`; **no guided filter**; clip t to [0.01, 1] for recovery as in the paper, but keep our t ≥ 0.2 gate for decisions.
3. Recover `J = (I − A)/max(t, 0.01) + A`, then C0's tone curve as in C1.
4. Variant M1g: 11 × 11 median followed by C1's guided filter (to separate the median from the refinement).
5. **Compare against:** C1 He 2013 (min + guided filter) and C0. Score the Ida primary in **thin cloud and especially the 0–40 m ring** (halo zone), paired per tile, 3 × 3 block bootstrap, with the grey guard ≤ 1 and the 21-seed flood screen.

### Proposed bench arm: G1 1/t-scaled change threshold
1. Wherever a correction arm (C0, C1, P1, S1, M1) produced J from t, replace the flood/change threshold τ with `τ / t` (cap at τ / 0.2, below which the gate abstains anyway).
2. Starting τ = the production threshold; no new tuning.
3. **Compare against:** the same arm with fixed τ, on the 21-seed flood screen (McNemar per seed), reporting omission and commission under thin cloud separately. Gibson's eq. 47 predicts fewer false flood calls in low-t areas at little cost to recall.

## 6. Key quotes
- "We conclude that better dehazing performance with fewer artifacts and better coding efficiency is achieved when the dehazing is applied before compression." (abstract, p. 662)
- "It operates at a faster speed than current methods and can avoid halo effects by using the median operation." (abstract, p. 662)
- "This reduces the complexity from using at minimum two median filter passes with large kernel sizes (41 × 41) to a single median filter with a smaller kernel size (11 × 11)." (p. 664)
- "depending on the quantization, the probability of ringing artifacts with the Post method is greater than the probability of ringing using a Pre method." (p. 666)
- "the blocking artifacts will become more severe as distance and/or scattering β are increased" (p. 667)
- "it is best to enhance before JPEG compression, i.e., Pre, in order to minimize blocking and ringing artifacts." (p. 668)
