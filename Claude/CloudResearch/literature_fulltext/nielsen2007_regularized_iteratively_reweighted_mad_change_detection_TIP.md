# Coder handoff: Nielsen (2007), The regularized iteratively reweighted MAD method for change detection in multi- and hyperspectral data

- **Citation:** Nielsen, A. A. (2007). *IEEE Transactions on Image Processing* 16(2), 463–478. https://doi.org/10.1109/TIP.2006.888195
- **PDF:** `/Users/jusrogers/Masters/papers/nielsen2007_regularized_iteratively_reweighted_mad_change_detection_TIP-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** author copy, DTU IMM publication database: http://www2.imm.dtu.dk/pubdb/edoc/imm4695.pdf (landing http://www2.imm.dtu.dk/pubdb/p.php?4695, OpenAlex green OA)
- **Validation:** PDF, 16 pages (Read tool and pdfinfo) = published range 463–478, IEEE journal layout with page headers 463–478; title/author/DOI match Crossref (DOI printed on p. 463); §VI Conclusion, Appendix and references present. PASS.
- **Read:** pp. 463–478 in full; equations (6)–(17) read from the PDF page images (text extraction drops them); reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm, step by step
1. **Setting** (p. 463): "nontrivial" change = non-affine change. Gain/offset shifts, linear calibration or normalisation, PCA/MAF-type transforms "are not detected".
2. **CCA** (eqs. 6–8, p. 465): X (p bands, date 1), Y (q bands, date 2, p ≤ q); `Σ12 Σ22⁻¹ Σ21 a = ρ² Σ11 a`, `Σ21 Σ11⁻¹ Σ12 b = ρ² Σ22 b`; canonical variates aᵢᵀX, bᵢᵀY with unit variance, ρ1² ≥ … ≥ ρp² ≥ 0, positive correlations requested.
3. **MAD** (eq. 9): `[X; Y] → [a_pᵀX − b_pᵀY; …; a_1ᵀX − b_1ᵀY]` (reverse order, so MAD1 is the least-correlated pair = most change). Dispersion `D{aᵀX − bᵀY} = 2(I − R)` (eq. 10), `σ²_MADi = 2(1 − ρ_{p−i+1})` (eq. 11). Invariant to affine transforms of either date (p. 465).
4. **Chi-square statistic** (eq. 12): `T_j = Σ_{i=1..p} (MAD_ij / σ_MADi)² ∈ χ²(p)` approximately for no-change pixel j (CLT + independence). "The standardization should ideally be done by means of the standard deviation of the no-change observations … Below, we use the standard deviation for all observations for simplicity. Provided that the proportion of changed pixels is small, this will have minimal effect." (Canty & Nielsen 2008 later switched to the re-weighted σ.)
5. **Labels** (p. 466): e.g. "change" for T above the 99% χ² percentile, "no-change" below the 1% percentile; no-change pixels "are suitable for carrying out an automated normalization" (detail in [38] = Canty et al. 2004).
6. **IR-MAD weights** (eq. 13): `w_j = P{χ²(p) > T_j}` (∈ [0, 1], "avoids very high weights").
7. **Weighted statistics** (eqs. 14–15): `X̄_i = Σ_j w_j X_ji / Σ_j w_j`; `S_kl = Σ_j w_j (X_jk − X̄_k)(X_jl − X̄_l) / ((N − 1) Σ_j w_j / N)`.
8. **Iterate** CCA → MAD → weights "until the largest absolute change in the canonical correlations becomes smaller than some preset small value ε, e.g., 10⁻⁶". Only the final iteration's weights are used (no boosting committee).
9. **Regularisation** (§IV-B, eqs. 16–17): add `λΩ` to Σ11 and Σ22, `Ω = LᵀL`, L the (p−2) × p second-difference matrix (rows [1 −2 1]) → curvature penalty across wavelength. λ guess `trace Σ11 / trace Ω` (~10⁻¹ for HyMap); cross-validation suggested 10⁻² to 10⁻⁴; 10⁻³ gave "quite wiggly" weights; λ = 0.1 used. Alternative: reduce non-overlapping groups of adjacent bands to one projection (max spatial autocorrelation) first; MAF keeps affine invariance.
10. Note (p. 468): when only MAD1 carries change, the χ² sum in eq. 13 "should start with" fewer terms for a better no-change measure.

## 2. Inputs, outputs, data needs
- Two co-registered images of the same area, any number of bands (can differ between dates); no reference data. Geometric correction is out of scope (p. 464).
- Output: MAD variates (change images ordered by similarity), the χ² change statistic T, the no-change probability w per pixel.

## 3. Quantitative results to compare against (all descriptive; no labelled accuracy)
- Landsat TM, N. Sweden, 512 × 512, 25 m, 6 bands, 1988 strip (512 × 128) pasted into 1986: IR-MAD after 30 iterations shows no change in the 512 × 384 no-change region better than MAD (Tables II–IV); "most of the action takes place in the first 5–7 iterations"; mean T ≈ 6 = p over the whole image for both (Table IV).
- SPOT HRV, Kenya, 512 × 512, 20 m, 3 bands: converged in 12 iterations ("most of the action … first 3–4"); no-change measure mean autocorrelation 0.67 (MAD) vs 0.73 (IR-MAD); IR-MAD3 autocorrelation 0.57 → 0.77 (Table V).
- HyMap, 126 bands, 5 m, 400 × 270: plain MAD gives NaN; 43 groups + λ = 0.1 converges to within 0.001 in 22 iterations (~16.5 s/iteration, P-III 1 GHz); without curvature penalty 100 iterations stabilise to < 0.005, and large changes continue to ~150 iterations.

## 4. Stated limitations
- Two dates only; multiset CCA would be needed for > 2 dates (p. 474).
- σ standardisation from all pixels is only safe when few pixels changed (p. 465).
- At 5 m, leading change variates "are dominated by edge effects caused primarily by buildings, individual trees and groves combined with the difference in solar angles and possible geometric misregistrations" (p. 472).
- With little regularisation, convergence can be slow ("some precaution concerning convergence seems wise", p. 472). λ and Ω choice open.

## 5. How to apply to our pipeline
- **Invariant-pixel selection for `sn8_refhaze.tone_curve` / `_robust_global` (and `sn8_cloudsym._correct`)**: see the Canty & Nielsen 2008 handoff for the normalisation recipe. This paper adds the exact weight and stop rule: `w = chi2.sf(T, df=p)`, weighted stats with eqs. 14–15, stop at max |Δρ| < 1e-6 (practically 1e-4 is plenty for N = 1–3; cap at 30 iterations). For p = 1 (grey): `T = ((b̃ − ã)/σ)²` with b̃, ã the weighted-standardised dates; for RGB p = 3 run real CCA (`scipy.linalg.eigh(Σ12 Σ22⁻¹ Σ21, Σ11)`).
- **σ choice:** this paper uses σ of all pixels; Canty & Nielsen 2008 use the re-weighted σ for change-dominated scenes. Flood tiles are change-heavy: use the re-weighted σ, and log which was used.
- **Edge effects at VHR (p. 472):** at 0.5 m, roof and tree edges, sun-angle shadows and the ~1 px misregistration will get low w. That is harmless for picking invariant pixels (conservative), but do not use IR-MAD T as the cloud or flood signal directly. Optional: erode the invariant mask by 1–2 px or drop pixels with high local gradient before fitting.
- **Cloud/flood gate:** IR-MAD gives a principled change probability that is blind to gain/offset; dark-rise sign then tells cloud (rise) from flood (fall). An arm for `sn8_cloudsym.change_gate`: gate = (1 − w > 0.99) ∩ dark rise > 0, vs the current Otsu cut on dark rise.
- **Regularisation:** not needed for 1–3 bands.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** feasible and cheap. The method needs exactly two co-registered dates. Using RGB (p = 3) rather than grey gives MAD something to separate; with grey, IR-MAD is a robust standardised difference with χ²₁ weights.

## 6. Key quotes
- "large weights being assigned to observations that show little change, i.e., for which the sum of squared, standardized MAD variates is small" (abstract, p. 463).
- "the MAD variates are invariant to affine transformations (including linear scaling), which means that they are sensitive to neither, for example, changes in gain settings and offset in a measuring device, nor to linear (affine) radiometric and atmospheric correction schemes" (p. 465).
- "Since the MAD transformation is invariant to linear (affine) transformations these no-change observations are suitable for carrying out an automated normalization between the two points in time." (p. 466)
- "Iterations are performed until the largest absolute change in the canonical correlations becomes smaller than some preset small value ε, e.g., 10⁻⁶." (p. 466)
- "dominated by edge effects caused primarily by buildings, individual trees and groves combined with the difference in solar angles and possible geometric misregistrations" (p. 472).
