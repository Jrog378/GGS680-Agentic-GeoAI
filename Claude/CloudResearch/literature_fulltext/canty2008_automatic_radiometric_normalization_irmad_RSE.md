# Coder handoff: Canty & Nielsen (2008), Automatic radiometric normalization of multitemporal satellite imagery with the iteratively re-weighted MAD transformation

- **Citation:** Canty, M. J., & Nielsen, A. A. (2008). *Remote Sensing of Environment* 112(3), 1025–1036. https://doi.org/10.1016/j.rse.2007.07.013
- **PDF:** `/Users/jusrogers/Masters/papers/canty2008_automatic_radiometric_normalization_irmad_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF already on disk, copied from `/Users/jusrogers/Masters/GGS680/references/Canty & Nielsen 2008. Automatic radiometric normalization of multitemporal satellite imagery with the IR-MAD transformation.pdf` (original left in place)
- **Validation:** PDF, 12 pages (Read tool and pdfinfo) = published range 1025–1036; title/authors/DOI match Crossref; §6 Discussion and conclusions and references present. PASS. (`file` metadata says 13; ignored.)
- **Read:** pp. 1025–1036 in full (text extraction; equations rebuilt from garbled glyphs and checked against the definitions in the text); reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm, step by step
Premise (p. 1025): relative normalisation assumes "the relationship between the at-sensor radiances recorded at two different times from regions of constant reflectance can be approximated by linear functions. The critical aspect is the determination of suitable time-invariant features".

1. **Data:** two co-registered N-band images F (reference date) and G (target), means removed. Registration in the paper: RMS < 0.5 px (p. 1029).
2. **CCA** (eq. 1, p. 1027): solve `Σfg Σgg⁻¹ Σgf a = ρ² Σff a` and `Σgf Σff⁻¹ Σfg b = ρ² Σgg b`. Canonical variates `Ui = aiᵀF`, `Vi = biᵀG`, ordered by canonical correlation ρ1 ≥ … ≥ ρN.
3. **MAD variates** (eq. 2): `Mi = U_{N−i+1} − V_{N−i+1}`, i = 1…N (reverse order). Uncorrelated (eq. 3), `var(Mi) = σ²_Mi = 2(1 − ρ_{N−i+1})` (eq. 4) (variates scaled to unit variance). Invariant to an affine transform of either image (p. 1028), so gain/offset differences between dates do not count as change.
4. **Change statistic** (eq. 5): `Z = Σ_{i=1..N} (Mi/σ_Mi)²`; for no-change pixels Z ~ χ²_N.
5. **No-change probability** (eq. 6): `Pr(no change) = 1 − P_χ²;N(z)` — probability a χ²_N draw is at least as large.
6. **Iterate** (p. 1028): start with weights = 1; weighted mean and covariance → CCA → MAD → new weights from eq. 6; stop when the canonical correlations "cease to change significantly". σ_Mi in eq. 5 are the **re-weighted** values from eq. 4 (Nielsen 2007 used the SD of all observations; the re-weighted version "was found to lead to considerably better performance … in which change dominates").
   - Converges "usually … within 20–30 iterations"; ~10 s per iteration for 1000 × 1000 × 6 in IDL on a 2.4 GHz P4 (p. 1035). For full scenes, run on a representative subset.
7. **Invariant set:** pixels with `Pr(no change) > t`, **t "typically 95%"** (p. 1028). This keeps only pixels with very small χ², so they look "spatially incoherent" / randomly scattered over the no-change areas (p. 1034).
8. **Normalisation:** per band, **orthogonal (total least squares) regression** of reference on target over the invariant pixels → slope and intercept (p. 1028–1029). Hold out a random fraction of invariant pixels.
9. **Quality control:** on hold-out pixels, paired t-test for equal means and F-test for equal variances, reference vs normalised; accept for P above a preset level, traditionally 5% (p. 1031).

## 2. Inputs, outputs, data needs
- Input: two co-registered multispectral images (paper: Landsat ETM+ 6 bands, ASTER 9 bands at 15 m), no ancillary data, no reference reflectance. N = 1 (greyscale) is not discussed in the paper; mathematically CCA of one band each reduces to correlating the two standardised bands, `M = (f/σf − g/σg)` up to sign and scale, and Z ~ χ²₁.
- Output: per-band gain/offset, the no-change probability map, MAD change variates.

## 3. Quantitative results to compare against
- Morocco (arid, little change; ETM+ 729 × 754): one MAD iteration adequate. Table 1 (MAD, 7,850 hold-out px) and Table 2 (IR-MAD, 6,671 px): all t-test and F-test P ≥ 0.24.
- Iran (ASTER, strong change, 2001 vs 2005): single MAD — means OK but variance F-tests **P = 0.000 in all 9 bands** (Table 3, 7,700 px); IR-MAD — all bands pass, means P 0.35–0.92, variances P 0.21–0.82 (Table 4, 8,400 px).
- Jülich (ETM+ June vs August 2001): IR-MAD all bands pass, P 0.39–0.95 (Table 5, 5,850 px); single MAD "did not give acceptable P-values" (p. 1032). 11,700 invariant pixels selected; no-change fraction ≈ 30% (area of central Gaussian in a 3-Gaussian fit) (p. 1034).
- Simulated: a copied 10% subset was found as the no-change set; < 10% copied → iteration goes to the real no-change pixels instead (pp. 1030, 1034).
- **Cloud:** "the substantial cloud cover in the April 9, 2001 image has no effect on the quality of its normalization as all cloud and cloud shadow pixels are correctly identified as change" (p. 1032).

## 4. Stated limitations (pp. 1034–1035)
- The iteration is "attracted to those pixels which are most strongly linearly correlated in the two acquisitions and which are in the majority". There is "a lower limit on the number of truly invariant pixels … below which the IR-MAD algorithm will fail", "highly scene-dependent". Jülich May 25 vs Aug 29: unsuitable regressions with "satellite" clusters; a stricter threshold did not fix it.
- No invariant pixels in hilly forest (BRDF / local incidence angle).
- Linear (gain + offset) per band, one global fit per image pair.

## 5. How to apply to our pipeline
- **`sn8_refhaze.tone_curve` (quantile matching over `clear` = valid & not within 10 m of the gate):** the paper supports fitting the date relation on *invariant* pixels only, selected automatically; our `clear` set includes flooded ground. Arm "IR-MAD tone": on the clear pixels, run single-band IR-MAD:
  1. w = 1; loop: weighted means/SDs of before b and after a; `M = (b − μb)/σb − (a − μa)/σa`; σ_M² = weighted variance of M (equivalently 2(1 − ρ) with ρ the weighted correlation); `Z = (M/σ_M)²`; `w = 1 − chi2.cdf(Z, df=1)` (scipy.stats); stop when |Δρ| < 1e-4 or 30 iterations.
  2. Invariant = clear & (w > 0.95).
  3. Either fit the paper's orthogonal regression on the invariant set (`np.linalg.svd` of centred [b, a] → slope = −v[0]/v[1] of the smallest singular vector), or keep our quantile curve but compute it only on invariant pixels (our nonlinear variant; the paper is linear).
  4. QC exactly as the paper: hold out 30% of invariant pixels, report paired t and F (`scipy.stats.ttest_rel`; F = var ratio with `scipy.stats.f`), pass if P > 0.05.
- **`sn8_refhaze._robust_global` (MAD-of-residuals trimming at REF_K = 2.5, 3 passes):** this is an ordinary-least-squares robust fit with hard rejection; the paper's choices differ on two counts: **orthogonal** regression (both dates noisy) and **χ² probability weights** iterated to convergence. Swap in as an arm; keep the `vx < 1` guard (flat area).
- **Cloud gate:** the paper's observation that cloud/shadow fall out as change means a single IR-MAD run gives both a no-change mask and a change map; low w inside a dark-rise blob = cloud or flood. It cannot tell them apart on its own (our dark-rise sign does).
- **Local version (`REF_WIN` 64 m windows):** the paper is global per image pair; local IR-MAD in windows is our extension (evidence 05's local-beats-global result). Danger flagged by the paper: in a window that is mostly flood, IR-MAD converges to the majority (the flood), not the invariant ground. Require a minimum invariant count per window and fall back to the tile fit.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** fully feasible; needs only the two co-registered dates. N = 1 grey weakens it (one MAD variate, less separation of change types); running on RGB (N = 3, χ²₃) is a cheap arm since the tiles are RGB. Registration: paper < 0.5 px; our ~0.6 m misregistration at 0.5 m is ~1 px, which inflates M at edges and pushes edge pixels out of the invariant set (acceptable: it makes the set conservative).

## 6. Key quotes
- "The critical aspect is the determination of suitable time-invariant features upon which to base the normalization" (p. 1025).
- "For radiometric normalization purposes, one can select all pixels which satisfy Pr (no change) > t where t is a decision threshold, typically 95%." (p. 1028)
- "The preferred method for performing the actual normalizations is then to determine the necessary transformations from orthogonal – as opposed to ordinary – linear regression on the invariant pixels" (p. 1028).
- "all cloud and cloud shadow pixels are correctly identified as change" (p. 1032).
- "It may be expected that there will be a lower limit on the number of truly invariant pixels in a bitemporal scene below which the IR-MAD algorithm will fail" (p. 1034).
