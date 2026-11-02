# Coder handoff: Pan, Xie, Jiang & Yin (2015), Haze removal for a single remote sensing image based on deformed haze imaging model

- **Citation:** Pan, X., Xie, F., Jiang, Z., & Yin, J. (2015). *IEEE Signal Processing Letters* 22(10), 1806–1810. https://doi.org/10.1109/LSP.2015.2432466
- **PDF:** `/Users/jusrogers/Masters/papers/pan2015-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 735 kB; 5 pages (Read tool and pdfinfo) = published range 1806–1810; page-1 title, authors (Pan, Xie, Jiang, Yin; Beihang University), SPL vol. 22 no. 10 Oct 2015 and DOI 10.1109/LSP.2015.2432466 match todo.tsv; Conclusion (p. 1809) and 23-item reference list (p. 1810) present. PASS.
- **Read:** PDF pp. 1–5 = journal pp. 1806–1810 in full (Read tool, page images), including Figs. 1–6 and eqs. 1–13.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.
- **Venue / JIF rule:** IEEE SPL, likely below 4 (approx. 3–4; general knowledge, not checked against JCR). Use as context/method source, not as a headline citation.

## 1. Algorithm, step by step
Inputs are RGB intensities; the paper's statistics (C = 27, Fig. 1 axis 0–255) are on the **0–255 scale** (p. 1807–1808).

1. **Haze model** (eq. 1, p. 1806): `I(x) = J(x) t(x) + A (1 − t(x))`. Recovery (eq. 4, p. 1807): `J(x) = (I(x) − A) / max(t(x), t0) + A`. The paper cites t0 = 0.1 from He et al. [3] ("experimentally fixed to 0.1 in [3]", p. 1807) and does not restate its own t0 in §IV; use 0.1.
2. **Assumption:** scattering is wavelength-independent, so t is the same in R, G, B (p. 1807), and haze is grey, so A is the same in all channels (p. 1807).
3. **Deformed model** (eqs. 5–6, p. 1807): subtract `C t(x)` from both sides:
   `I(x) − C t(x) = (J(x) − C) t(x) + A (1 − t(x))`, with C > 0 "derived from a kind of statistics of haze-free remote sensing images".
4. **Airlight** (eq. 7, p. 1807): run He's estimator. Take the top 0.1% brightest pixels of the dark channel, then take the highest-intensity input pixels among them as the RGB vector A. Then set `A = A0·[1, 1, 1]ᵀ` with **A0 = mean of He's three A values**.
5. **Dark channel of the shifted scene** (eq. 8, p. 1807): `(J − C)^dark(x) = min_{y∈Ω(x)} min_{c∈{r,g,b}} max(J^c(y) − C, 0)`, assumed = 0 (eq. 10, p. 1808).
6. **Transmission** (eqs. 9–12, p. 1807–1808): with t constant in the patch,
   `min_Ω min_c I^c(y) − C t̃ = A0 (1 − t̃)` (eq. 11), so
   **`t̃(x) = (A0 − min_{y∈Ω(x)} min_c I^c(y)) / (A0 − C)`** (eq. 12).
   No ω (haze-keeping factor) appears in eq. 12. The paper does not say to clip t̃. Because the dark channel can fall below C, t̃ can exceed 1: **clip to [t0, 1]** (our addition).
7. **Refinement** (eq. 13, p. 1808): guided filter (He 2013 [22]) with the **hazy image as guide**, **window radius 20**, **ε = 10⁻³** (p. 1808). The ε value follows He's convention of a guide scaled to [0, 1] (our reading; the paper does not state the guide's scale). Use a grey guide or a colour guide (not stated).
8. **Recover** J by eq. 4 with A = A0·[1, 1, 1].

**Parameters (p. 1808, §IV):** C = 27 (from the average dark-channel intensity **27.28** of 5000 haze-free 400 × 400 Google Earth images, 15 × 15 patches, Fig. 1(b)); dark-channel patch **15 × 15**; guided filter r = 20, ε = 10⁻³. Other values: C = 0 for an outdoor photo (Fig. 5) and C = 33 for an ALOS image (Fig. 6), each "from the statistics of their corresponding haze-free images" (p. 1809).

## 2. Inputs, outputs, data needs
- Input: one RGB hazy image (8-bit range). Output: dehazed RGB image, and t̃ map.
- C needs dark-channel statistics of haze-free images **of the same sensor/type** (p. 1809: "different type of images has different C").
- Hardware: 3.1 GHz Core i5, Matlab 2013a (p. 1808).

## 3. Quantitative results
- BIQI (blind, lower = better), Fig. 2 top/bottom images: He 34.78 / 38.43; Long 29.95 / 39.42; proposed 29.73 / 35.97 (p. 1808). Two images only; Long is better than He on the top image but worse on the bottom one.
- Time per 400 × 400 image: about 0.1 s (He), 0.5 s (Long), 0.1 s (proposed) (p. 1808).
- Non-uniform haze (Figs. 3–4) and transmission texture (Fig. 4): visual only (pp. 1808–1809).
- No reference images, no full-reference metrics, no significance tests.

## 4. Stated limitations
- "the proposed method can further be improved on the automatic determination of C for the purpose of being adaptive to different situations. That is our future research work." (p. 1809)
- C is sensor/type-specific (p. 1809).
- Assumes wavelength-independent scattering (p. 1807). That conflicts with Chavez 1988's band-dependent haze.

## 5. How to apply to our pipeline
- **What it fixes:** He's DCP assumes the clear-scene dark channel ≈ 0. At 0.5 m over towns and vegetation it is not (Pan measured mean 27.28 on Google Earth imagery). He's recipe then over-estimates haze, which gives dim, colour-drifted output. This is a plausible mechanism for our bench finding that **C1 He 2013 moved features away from NOAA** (+0.0127 [+0.0049, +0.0213], evidence 22). Pan's shift is the published remote-sensing fix for exactly that bias.
- **Two-date advantage:** Pan needs a global C from haze-free statistics. We have the clear pre-storm tile of the same place, so C can be measured per tile (or per window) from the before image. That turns Pan's global constant into a local reference.
- **Grey:** with one channel, eq. 12 is `t = (A0 − minΩ I) / (A0 − C)`; it runs unchanged.
- **Flood caveat:** water is dark. Under haze, a newly flooded road has a lower dark channel than the before-date C assumes, so t̃ is over-estimated (less correction), which is the safe direction. Where the before date is water and the after date is not, the opposite holds. Report both.

### Proposed bench arm: P1 Pan C-shift (before-date C)
1. On each tile, compute the before image's dark channel `D_b = minΩ min_c I_b` (15 × 15, same erosion code as C0/C1). Set **C_tile = mean(D_b over clear-ground pixels)** (variant P1g: Pan's global C = 27; variant P1w: C(x) = box-mean of D_b in a 61 × 61 window, a local C).
2. On the after image, estimate A by He's top-0.1% rule and set A0 = mean over RGB (grey: the value itself).
3. `t̃ = clip((A0 − D_a) / (A0 − C), t0, 1)`, with D_a = after-image dark channel, t0 = 0.1. Refine with the guided filter, r = 20 px, ε = 1e-3 on a [0, 1] guide (the after image).
4. Recover by eq. 4. Apply the existing t ≥ 0.2 / CANNOT ASSESS gate unchanged.
5. **Compare against:** C0, "as is" and C1 He 2013 on the bench-1 Ida primary (DINOv2 feature distance to NOAA, thin cloud and ring, paired per tile with C0, 3 × 3 block bootstrap), with the grey guard (≤ 1 grey level) and the 21-seed flood screen. Pre-register: P1 is "closer than C1" if Δ(P1 − C1) < 0 with CI excluding 0, and promotable only if it also beats C0 or "as is".
6. Expected direction: P1 should sit between C1 and "as is", because a larger C means larger t̃ and less correction. If P1 ≈ "as is", the result says that the DCP family is not the problem; the haze model is.

## 6. Key quotes
- "the dark channel prior has been developed originally according to the statistics of outdoor haze-free images which are very different from remote sensing images because of the different imaging distance. Therefore, it often causes color drift phenomenon when applied to remote sensing images directly." (p. 1806)
- "Obviously, the average intensity of remote sensing images' dark channel is low, but not close to zero." (p. 1807)
- "the value of C is set to 27 according to the average intensity, 27.28, of dark channels for 5000 haze-free remote sensing images" (p. 1808)
- "The patch size of dark channel is 15 × 15 pixels, and for the guided filter, the radius of a window is 20 and ε is 10⁻³." (p. 1808)
- "parameter C reflects the statistics feature of images' dark channels, and different type of images has different C." (p. 1809)
