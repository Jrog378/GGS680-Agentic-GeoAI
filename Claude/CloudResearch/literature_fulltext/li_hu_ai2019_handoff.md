# Coder handoff: Li, Hu & Ai (2019), Haze and thin cloud removal via sphere model improved dark channel prior

- **Citation:** Li, J., Hu, Q., & Ai, M. (2019). *IEEE Geoscience and Remote Sensing Letters* 16(3), 472–476. https://doi.org/10.1109/LGRS.2018.2874084
- **PDF:** `/Users/jusrogers/Masters/papers/li_hu_ai2019-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 4.06 MB; 5 pages (Read tool and pdfinfo) = published range 472–476; page-1 title, authors (Jiayuan Li, Qingwu Hu, Mingyao Ai; Wuhan University), GRSL vol. 16 no. 3 March 2019 and DOI 10.1109/LGRS.2018.2874084 match todo.tsv; Conclusion and 19-item reference list (p. 476) present. PASS.
- **Read:** PDF pp. 1–5 = journal pp. 472–476 in full (Read tool, page images), including Tables I–VII, Figs. 1–2, eqs. 1–17.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.
- **Venue / JIF rule:** IEEE GRSL, borderline ~4 (general knowledge, not checked against JCR).

## 1. Algorithm, step by step
Two stages (Fig. 1, p. 473): (A) haze distribution enhancement by homomorphic filtering (HF); (B) sphere-model DCP.

**A. Homomorphic filtering** (eqs. 1–4, p. 473)
1. Illumination–reflectance model `I(x) = J(x) L(x)` (eq. 1).
2. `Γ{ln I} = Γ{ln J} + Γ{ln L} = F_J + F_L` (eq. 2), Γ = Fourier transform.
3. `F_Î = g(x) F_J + g(x) F_L` (eq. 3), with g a **Gaussian high-pass filter, standard deviation σ_g(x) = 10** (p. 475).
4. `Î = exp(Γ⁻¹{F_Î})` (eq. 4). Î replaces I in all later steps (p. 473).
- **Underspecified:** no high/low gain (γ_H, γ_L), no frequency units for σ_g, no per-band vs luminance choice, and no rescaling after exp. A pure Gaussian high-pass removes the DC term, so the image mean is lost. A coder must choose, e.g. `H = (γ_H − γ_L)(1 − exp(−D²/(2σ²))) + γ_L`. **That form and its gains are our assumption, not the paper's.**

**B. Sphere-model DCP** (eqs. 5–17, pp. 473–474)
5. Haze model `I = J t + A (1 − t)` (eq. 5). Standard DCP: `t̃ = 1 − w min_c min_{Ω} (I_c/A_c)` (eq. 8), with w the haze-keeping constant (0 < w < 1).
6. **Sphere model:** in each patch Ω(x), take the normalised pixels `m = [Î_r/A_r, Î_g/A_g, Î_b/A_b]`. Approximate their cloud in RGB space by a sphere `(m − u)ᵀ(m − u) ≤ R²` (eq. 11), where **u = mean vector of m in Ω** and **R = σ = (σ_r + σ_g + σ_b)/3**, σ_c being the standard deviation of channel c in Ω (p. 474).
7. The minimum of coordinate c on the sphere is u_c − σ (eqs. 12–16). Hence
   **`t̃(x) = 1 − w · min_{c∈{r,g,b}} (u_c − σ)`** (eq. 17, p. 474).
   So the patch minimum becomes a local "mean minus mean standard deviation". With a box filter it is O(1) per pixel.
8. Refinement: "DCP uses soft matting or guided filtering" (p. 474). **Which one the authors used is not stated**; use the guided filter.
9. Recovery (eq. 9, p. 474): `J = (Î − A) / max(t, t0) + A`, **t0 = 0.1** (p. 474).
10. "Finally, we use a color transfer algorithm to remove color drifts" (p. 474). **No method or citation is given.**
11. A estimation: not specified; it is implied to follow DCP [1] (He's top-0.1% rule).

**Parameters** (p. 475, Tables II–IV): σ_g(x) = 10, S_Ω = 15 × 15, w = 0.95, t0 = 0.1. "All parameters are fixed throughout the experiment."
- Table II (σ_g at S_Ω 15, w 0.95), IL-NIQE / BRISQUE: σ 5: 29.72 / 25.95; **10: 28.52 / 25.42**; 15: 29.23 / 25.88; 20: 30.56 / 27.04 (p. 474).
- Table III (S_Ω at σ_g 10, w 0.95): 5: 31.66 / 27.99; **15: 28.52 / 25.42**; 25: 28.84 / 25.69; 45: 29.61 / 26.11 (p. 474).
- Table IV (w at S_Ω 15, σ_g 10): 0.35: 36.72 / 32.16; 0.55: 34.93 / 30.17; 0.75: 30.18 / 26.33; **0.95: 28.52 / 25.42** (p. 475).

## 2. Inputs, outputs, data needs
- Single image, three bands (natural or false colour). Data (Table I, p. 474): SkySat-1 10 images (0.8 m, 1500 × 1500, false colour); Landsat 8 10 (30 m, 1500 × 1500); Gaofen-2 15 (1 m, 1000 × 1000); IKONOS 5 (1 m, 580 × 380); Gaofen-1 8 (2 m, 1920 × 965). 48 in total (p. 474).
- MAE (colour drift) on the 8 Gaofen-1 images, "since these images contain both hazy regions and clear regions"; the exact MAE protocol is not described. The other 40 images are scored with IL-NIQE and BRISQUE (p. 474).
- Code and data: footnote 1 (p. 472), http://www.escience.cn/people/lijiayuan/index.html (not visited; no downloads in this pass).

## 3. Quantitative results
- Table V MAE (R / G / B, p. 476): non-local dehazing 36.16 / 38.33 / 42.62; DCP 25.39 / 23.36 / 23.88; GRS-HTM 12.52 / 11.03 / 13.29; **ours 9.56 / 7.26 / 7.73**.
- Table VI (p. 476): IL-NIQE observed 37.78, non-local 34.89, DCP 35.22, GRS-HTM 29.37, **ours 28.52**; BRISQUE 34.96, 28.95, 29.36, 26.87, **25.42**.
- Table VII time, total s (HF + dehazing): 250² 0.3; 500² 0.77; 1000² 2.51; 1500² 6.83; 2000² 12.36. HF is the slow part (e.g. 4.51 of 6.83 s at 1500²). Hardware: laptop i5 2.5 GHz (pp. 474, 476).
- No error bars, no significance tests. Parameters were scanned on the same images that are scored (our observation).

## 4. Stated limitations
- "Our dehazed image may look dim. This is expected, because pixels with influence of atmosphere have always higher digital values." (p. 476)
- On the smoke image "The result only contains a little thin smoke" (p. 476).
- HF is the time bottleneck; a C/C++ rewrite would help (p. 476).

## 5. How to apply to our pipeline
- **The sphere statistic is the transferable part.** Our dark channel is erosion (patch min) plus a box blur. The minimum is driven by single dark pixels (shadows, dark roofs, JPEG ringing; see Gibson 2012), which the paper names as DCP's weakness ("very sensitive to noise", p. 472). `u − σ` uses every pixel in the window and is cheap: two box filters per band.
- **Grey:** with one band, eq. 17 is `t = 1 − w (box_mean(I/A) − box_std(I/A))`. It runs unchanged.
- **The homomorphic stage is not recommended for us.** It flattens all low-frequency content, including real flood darkening over large areas, which is our signal. It is also underspecified. If tested at all, apply it only inside the cloud/haze gate.
- **Colour transfer:** unspecified, so not reproducible. Our C0 tone curve plays this role.
- **Why it might beat C1:** He's min-filter over-estimates haze on textured 0.5 m ground. That is a candidate cause of C1's move away from NOAA (evidence 22). Mean − σ is less extreme than the min (it is ≥ the min whenever the local distribution is not too skewed), so t is larger and the correction gentler.

### Proposed bench arm: S1 sphere-DCP transmission
1. A: He's top-0.1% rule on the after image (same as C1); grey: one value.
2. For each band c: `n_c = I_c / A_c`; `u_c = box15(n_c)`; `s_c = sqrt(box15(n_c²) − u_c²)`; `σ = mean_c s_c` (grey: σ = s).
3. `t̃ = 1 − 0.95 · min_c (u_c − σ)`; clip to [0.1, 1].
4. Guided filter refinement with the same r/ε as C1. Recover with eq. 9, t0 = 0.1. No HF, no colour transfer (C0's tone curve after, as in C1).
5. Variant S1p (our combination, not in either paper): use the sphere value as the dark channel in Pan's eq. 12, i.e. `D_s = A0 · min_c(u_c − σ)` (back in grey levels), `t̃ = (A0 − D_s) / (A0 − C_tile)`, with C_tile from the before image's D_s on clear ground (see pan2015 handoff, arm P1).
6. **Compare against:** C1 He 2013 (same pipeline, min-filter dark channel), C0 and "as is". Use the Ida primary (DINOv2 distance to NOAA, thin + ring, paired per tile, 3 × 3 block bootstrap), the grey guard ≤ 1 grey level and the 21-seed flood screen. The key contrast is S1 − C1 (only the transmission estimator differs).

## 6. Key quotes
- "haze and cloud are highly related to the illumination component and mainly located in the low frequency of an image" (abstract, p. 472)
- "the transmission estimated by DCP is very sensitive to noise" (abstract, p. 472)
- "In the proposed method, we set R = σ = (σ_r + σ_g + σ_b)/3, where σ_c is the standard deviation of a channel of the local patch." (p. 474)
- "Thus, we set σ_g(x) to 10, S_Ω to 15 × 15 pixels, and w = 0.95. All parameters are fixed throughout the experiment." (p. 475)
- "Finally, we use a color transfer algorithm to remove color drifts." (p. 474)
- "Similar to other DCP-based methods, we set t0 = 0.1." (p. 474)
