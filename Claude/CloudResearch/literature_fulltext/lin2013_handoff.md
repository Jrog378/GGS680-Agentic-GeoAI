# Coder handoff: Lin, Tsai, Lai & Chen (2013), Cloud removal from multitemporal satellite images using information cloning

- **Citation:** Lin, C.-H., Tsai, P.-H., Lai, K.-H., & Chen, J.-Y. (2013). Cloud removal from multitemporal satellite images using information cloning. *IEEE Transactions on Geoscience and Remote Sensing* 51(1), 232–241. https://doi.org/10.1109/TGRS.2012.2197682
- **PDF:** `/Users/jusrogers/Masters/papers/lin2013-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document, version 1.4; 2.10 MB; 10 pages (Read tool and pdfinfo) = published range 232–241; page-1 title, authors (Lin, Tsai, Lai, Chen), TGRS vol. 51 no. 1, January 2013, and DOI 10.1109/TGRS.2012.2197682 match todo.tsv; §IV Conclusion and References [1]–[25] (p. 240) present. PASS.
- **Read:** PDF pp. 1–10 = journal pp. 232–241 in full (Read tool, page images), including Tables I–II, Figs. 1–14, references and author biographies. Key constants re-checked with pdftotext.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Setting (p. 233): one cloudy **target** image `I_T` and n **reference** images `{I_R1 … I_Rn}` of the same place on other dates. Three steps (Fig. 1, p. 233).

1. **Cloud and cloud-shadow detection (p. 233), semi-automatic.**
   - Automatic part = Huang et al. (2010) [ref. 20, IJRS 31(20)]: "relying on the physical fact that clouds are bright and cold in the thermal band, a thresholding-based approach is adopted to define the cloud boundaries in the spectral-temperature space." Shadows are "roughly predicted according to the cloud location and the solar illumination direction"; "dark and connected components" near the predicted shadow are taken as shadow.
   - Then **manual refinement**: "users are allowed to refine the cloud detection results through an interface with simple selection and erasion operations."
   - **No threshold value, no visible-band rule and no way of setting a threshold is given in this paper.** There is no blue-rise test and no Otsu step. (Our G2 "Lin blue rise" gate is Lin et al. **2015**, ISPRS JPRS, eq. 15, 0.03 ToA reflectance; see `lin2015_radiometric_normalization_cloud_detection_invariant_pixels_ISPRS.md`.) Automatic thin-cloud detection is listed as future work (p. 240).
2. **Image-quality assessment / reference ranking by SSIM (pp. 233–234).**
   - Eq. (1): `L = (2 μ_T μ_R + C1)/(μ_T² + μ_R² + C1)`, `C = (2 σ_T σ_R + C2)/(σ_T² + σ_R² + C2)`, `S = (σ_TR + C3)/(σ_T σ_R + C3)`.
   - Eq. (2): `SSIM = L^α C^β S^γ`; α = β = γ = 1.0 and C3 = C2/2 (following Wang et al. [19]), giving eq. (3): `SSIM = (2 μ_T μ_R + C1)(2 σ_TR + C2) / ((μ_T² + μ_R² + C1)(σ_T² + σ_R² + C2))`.
   - Constants (p. 234): `C1 = (K1·L)²`, `C2 = (K2·L)²`, L = 255 for an 8-bit channel, **K1 = K2 = 0.01** (note: not Wang's K2 = 0.03). SSIM range 1.0 (most similar) to −1.0.
   - SSIM is "calculated for the cloud-free regions" between target and each reference (p. 234). Window size and whether SSIM is local or global are **not stated**.
   - **Cloud-amount constraint (p. 234):** a reference patch is not a candidate "if the amount of cloud in a patch is greater than a defined threshold (set to 80% for all experiments)". Fig. 3: candidate references drop from six to four.
   - Several patches from several references may fill one cloud region; the "cloud-free patches in the reference images with the highest rank are utilized" (p. 237). Patch quality is shown normalised 0 (worst) – 100 (best) (p. 237). How a "patch"/"working area" is delimited is not specified beyond the cloud region.
3. **Information reconstruction = Poisson cloning (Pérez et al. 2003 [21]) (pp. 234–237).** Γ = cloud region in `I_T`, ∂Γ its boundary, f = unknown intensity on Γ, f* = target image outside Γ, **V** = guidance field = gradient of the selected reference patch(es).
   - Eq. (4): `min_f ∬_Γ |∇f − V|²` with `f|∂Γ = f*|∂Γ`.
   - Eq. (5): forward differences `∂f/∂x = f(x+1,y) − f(x,y)`, `∂f/∂y = f(x,y+1) − f(x,y)`.
   - Eq. (6): `Δf = div V over Γ`, with `f|∂Γ = f*|∂Γ` (Poisson equation, Dirichlet boundary).
   - Eq. (7): `∂²f/∂x² = f(x+1,y) + f(x−1,y) − 2f(x,y)` (same in y).
   - Eq. (8), discrete: `min_f Σ_{⟨p,q⟩∩Γ≠∅} (f(p) − f(q) − v_pq)²`, with `f(s) = f*(s)` for all s ∈ ∂Γ; N_p = 4-connected neighbours; `v_pq = I_R(p) − I_R(q)` (p. 235).
   - Eq. (9), the linear system solved: `|N_p| f(p) − Σ_{q∈N_p∩Γ} f(q) = Σ_{q∈N_p∩∂Γ} f*(q) + Σ_{q∈N_p} v_pq` for all p ∈ Γ. "Iteratively solved until the unknown function f is converged" (p. 235); solver and tolerance not given.
   - Eq. (10), seams between patches from two references R_i, R_j: `v_pq = ((P_Ri(p) − P_Ri(q)) + (P_Rj(p) − P_Rj(q)))/2` (p. 235).
   - Eq. (11), cloud touching the image border (extrapolation, Fig. 5 right): border pixels use `|N_p| f_p − Σ_{q∈N} f_q = Σ_{q∈N} v_pq` (boundary terms removed); other pixels use eq. (9) (p. 237).
   - Applied per band (Fig. 9 shows bands 1–5 and 7 separately, p. 237).

## 2. Inputs, outputs, data needs
- Inputs: co-registered target + several reference dates of the same sensor; a thermal band for the automatic cloud step plus a human for refinement; 8-bit channels (L = 255).
- Data used: Landsat-7 ETM+; real clouds near eastern Taiwan (8 Aug 1999), Los Angeles (4 July 2000) and Taipei (Nov 2000), with seven or more reference images (p. 237; Figs. 7–9); cloud amounts 36%, 46%, 53%, 63%, 70% (Fig. 10, p. 238); simulated clouds near Chiayi (target 26 Oct 2002, references 14 Jan 2003 and 3 Mar 2003; Fig. 11) and a change/no-change test (target 27 May 2003, references 3 July 1999 – 11 May 2003; Fig. 13).
- Output: cloud-free target image (cloud pixels replaced by Poisson-reconstructed values) and a per-patch quality map.

## 3. Quantitative results
Table I (p. 239), simulated clouds, values for reference A / reference B; approaches A = patch replacement, B = radiometric correction, C = radiometric correction + local colour blending ([16]–[18]):

| Area | Index | A | B | C | Lin 2013 |
|---|---|---|---|---|---|
| 1 (urban + cropland) | RMSE | 7.52 / 7.04 | 7.01 / 6.65 | 6.99 / 6.61 | 6.28 / 6.26 |
| | PSNR | 29.85 / 29.95 | 30.98 / 30.99 | 31.01 / 31.02 | 32.24 / 32.25 |
| | SSIM | 0.80 / 0.80 | 0.83 / 0.83 | 0.83 / 0.83 | 0.85 / 0.85 |
| 2 (large cropland) | RMSE | 8.11 / 7.72 | 7.79 / 7.13 | 7.77 / 7.11 | 7.25 / 6.96 |
| | PSNR | 29.28 / 30.15 | 30.30 / 31.11 | 30.39 / 31.14 | 31.01 / 31.35 |
| | SSIM | 0.55 / 0.60 | 0.58 / 0.63 | 0.58 / 0.63 | 0.64 / 0.65 |
| 3 (small cropland) | RMSE | 7.21 / 5.82 | 6.85 / 5.41 | 6.81 / 5.36 | 6.54 / 5.23 |
| | PSNR | 30.50 / 32.72 | 31.15 / 33.27 | 31.20 / 33.29 | 31.91 / 33.80 |
| | SSIM | 0.59 / 0.73 | 0.62 / 0.77 | 0.62 / 0.77 | 0.64 / 0.77 |
| 4 (small mountain) | RMSE | 2.88 / 3.61 | 2.61 / 3.12 | 2.60 / 3.11 | 2.54 / 3.05 |
| | PSNR | 38.75 / 38.01 | 39.89 / 38.39 | 39.95 / 38.41 | 40.11 / 38.51 |
| | SSIM | 0.88 / 0.86 | 0.91 / 0.88 | 0.91 / 0.88 | 0.91 / 0.88 |

- Text (p. 239): area 1 RMSE "improved from 6.99 to 6.28 (11.3%)", area 4 "from 2.60 to 2.54 (2.3%)" vs approach C.
- **Change vs no change (Fig. 13, p. 239):** average RMSE 8.75 (vegetation-growth change area) vs 5.51 (unchanged mountain area). Using the references of 11 May 2003 and 9 April 2003 gives RMSE 7.5 and 7.43, "close to the worst case of nonchange-area reconstruction".
- Table II (p. 240): single reference (RI_C) RMSE 6.55, PSNR 31.84, SSIM 0.80; multiple references (RI_A, RI_B, RI_C) RMSE 6.38, PSNR 32.07, SSIM 0.89.
- No significance tests; single simulated scene for Tables I–II.

## 4. Stated limitations
- "our approach cannot accurately reconstruct information when land covers change significantly over a short period of time. It is a limitation of multitemporal-based approaches" (p. 239).
- Results in Fig. 10 "are misty because some misty patches are selected as reconstruction candidates" (p. 238): thin cloud in a reference leaks into the fill.
- Cloud detection needs manual refinement; automatic (incl. thin) cloud detection and thin-cloud reconstruction are future work (p. 240).

## 5. How to apply to our pipeline
- **Fit:** we have one pre-storm reference (clear) and one post-storm target (possibly cloudy), RGB uint8 at 0.5 m, no thermal, no NIR. Step 1 cannot be ported (thermal + human). Step 2 (SSIM, L = 255) ports directly. Step 3 ports directly per band (or on grey), but filling the after image from the before date copies pre-storm ground into the flood: the paper's own Fig. 13 shows the fill degrades under change (8.75 vs 5.51 RMSE), and our notes (ev05, ev10 §5) already rule such fills out for flood calls.
- **The bench's T_blue = 240.8 is not a Lin 2013 problem:** Lin 2013 publishes no visible threshold. The G2 gate follows Lin 2015 (0.03 ToA). Nothing in Lin 2013 helps set T_blue; ev23's fix (99th percentile of blue rise on production-clear pixels) stays the right next step.
- **What transfers:** (a) the Poisson seam (eqs. 8–9) as a replacement for the linear 20 m fade at the edge of any correction field (ev10 §5 "N2"); (b) SSIM(before, after) on clear pixels (eq. 3) as a per-tile/per-patch "is the before date a usable reference" score; (c) the 80% cloud-amount rule as a reference-patch veto.

### Proposed bench arm: L1 Poisson seam for the correction (in-rule)
Replaces C0's linear fade at the gate border; does not import before-date content.
1. Inputs per tile: after RGB `A`, C0's corrected after image `A_c` (inside the production gate Γ plus its 20 m fade band), production gate mask Γ (dilated by the current fade width, 40 px).
2. Per band b, solve eq. (9) on Γ with `v_pq = A_c(p) − A_c(q)` (guidance = gradient of the corrected image) and Dirichlet boundary `f* = A` on ∂Γ (the uncorrected ring). Use a direct sparse solve (4-neighbour Laplacian, `scipy.sparse.linalg.spsolve`) or conjugate gradient to relative residual 1e-6; record the iterations.
3. Clip to [0, 255]; regions touching the tile edge use eq. (11) for border pixels.
4. Compare against C0 (linear fade) and C0 with no fade: Ida primary (closeness to NOAA, 54 tiles, paired), guard, grey error thin, and the flood screen / 21-seed flood rule. Also report the seam metric: mean |∇| jump across ∂Γ.

### Proposed bench arm: L2 Lin cloning from the before date (diagnostic only, never feeds flood calls)
Tests how much the paper's no-change assumption costs on our data.
1. Γ = production's opaque-cloud gate on the after image (dilated 4 px); skip the tile if Γ covers > 80% of it (the paper's cloud-amount rule, applied to the target here since the before date is clear).
2. Reference quality: SSIM(before, after) by eq. (3) on pixels outside Γ (K1 = K2 = 0.01, L = 255; window not given in the paper, use 11 × 11 and record it as our choice). Abstain if SSIM < 0.5 (our starting value).
3. Map the before image onto the after radiometry outside Γ with C0's tone curve (Poisson only fixes the boundary offset, not gain), then per band solve eq. (9) with `v_pq = B'(p) − B'(q)` and `f* = A` on ∂Γ.
4. Score: NOAA closeness inside Γ vs leaving the cloud as is and vs plain patch replacement (B' pasted, the paper's "approach A"); then, on SN8 flood labels, the share of flooded pixels inside Γ that the filled image calls dry (flood omission caused by the fill). Expected: closer to NOAA on unchanged ground, flood omission high. Result goes in the "why we abstain under opaque cloud" evidence, not production.

## 6. Key quotes
- "The basic idea is to clone information from cloud-free patches to their corresponding cloud-contaminated patches under the assumption that land covers change insignificantly over a short period of time." (abstract, p. 232)
- "relying on the physical fact that clouds are bright and cold in the thermal band, a thresholding-based approach is adopted to define the cloud boundaries in the spectral-temperature space." (p. 233)
- "users are allowed to refine the cloud detection results through an interface with simple selection and erasion operations." (p. 233)
- "if the amount of cloud in a patch is greater than a defined threshold (set to 80% for all experiments), then the patches will not be selected as candidates." (p. 234)
- "Equation (9) is iteratively solved until the unknown function f is converged." (p. 235)
- "our approach cannot accurately reconstruct information when land covers change significantly over a short period of time." (p. 239)
- "In the future, an automatic cloud (including thin cloud) detection approach and a reconstruction approach for thin cloud are planned to be developed." (p. 240)
