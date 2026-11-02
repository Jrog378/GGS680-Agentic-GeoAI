# Coder handoff: Olofsson et al. (2014), Good practices for estimating area and assessing accuracy of land change

- **Citation:** Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E., & Wulder, M. A. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment* 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015
- **PDF:** `/Users/jusrogers/Masters/papers/olofsson2014_good_practices_area_accuracy_land_change_RSE-summary.pdf` (page 1 = AI summary)
- **Source:** local publisher PDF already on disk, `/Users/jusrogers/Masters/GGS662/reference/Olofsson et al. 2014. Good practices for estimating area and assessing accuracy of land change.pdf` (left in place; copied). Journal pagination 42–57.
- **Validation:** PDF (12.3 MB), 16 pages (Read tool; pdfinfo agrees) = 42–57; title, six authors, volume, pages and DOI match Crossref; Summary (§6) and references present. PASS.
- **Read:** pp. 42–57 in full (reference list pp. 56–57 skimmed).
- **Prepared by:** Claude (AI), 2026-10-29.
- **Type:** review / protocol paper, not an image method. Sections below keep what we can use.

## 1. The three components (§1.1, p. 44)
- **Sampling design:** how units for assessment are chosen. **Response design:** how each unit gets its reference label and how agreement is defined. **Analysis:** estimators of accuracy and area with uncertainty.
- Before the rigorous assessment: "a basic visual assessment should be conducted to identify obvious errors" (p. 43).

## 2. Sampling design rules (§2, pp. 44–47)
- Probability sampling: inclusion probability known for sampled units and > 0 for every unit in the region of interest (p. 44). Without it "the probabilistic basis for design-based inference … is forfeited" (p. 45).
- **Cloud as a deviation (p. 45):** "persistent cloud coverage or lack of useable imagery for portions of the ROI may prevent obtaining the reference classification for some sample units … If the reference classification for a sample unit cannot be obtained, the inclusion probability is zero for that unit. All deviations … should be documented and quantified … the proportion of the selected sample units for which cloud cover prevented assessment of the unit should be reported". When a large share is unavailable, representativeness "must be addressed by subjective judgment".
- Stratified random with map classes as strata is the recommended design (§2.2, p. 47). Allocation: 50–100 units per rare change stratum (eq. 6 to size it), rest roughly proportional to area (pp. 53, 55). Simple random is preferred to systematic if unbiased variance is a priority (p. 46–47).
- Sample size for overall accuracy, simple random (eq. 12, p. 53): n = z² O(1−O)/d², z = 1.96 (95%) or 1.645 (90%), d = CI half-width. Stratified (eq. 13): n ≈ (Σ W_i S_i / S(Ô))², S_i = √(U_i(1−U_i)).

## 3. Response design rules (§3, pp. 47–51)
- Unit can be pixel, polygon or block; "the spatially explicit character of the accuracy assessment must be retained" (p. 47). Different units give different estimates.
- Reference must be of higher quality than the map, or, with the same source, made by a more accurate process (p. 47; §6.3).
- Reference period must be synchronous with the map's change period; mismatched periods are "a major source of reference data error" (p. 49).
- Labelling: specify a minimum mapping unit; allow primary + secondary labels; record interpreter confidence (low/moderate/high); interpretation keys; consistency among interpreters (pp. 49–50, §6.3).
- Reference uncertainty: geolocation error (co-registration) and interpreter bias/variability; "Small errors in the reference data set can lead to large biases of the estimators" (p. 50, citing Foody 2010, 2013).
- VHR note: < 1 m is VHSR; 0.5 m panchromatic "closely resemble[s] large scale aerial photography" (p. 48).

## 4. Analysis: equations (§4, pp. 51–52)
Symbols: q classes; rows i = map class, columns j = reference class; n_ij sample counts; n_i· sample size in map stratum i; W_i = mapped area proportion of class i; A = total map area.
```
p̂_ij = W_i * n_ij / n_i·                                      # eq. 4 (stratified by map class; post-stratified for SRS)
O    = Σ_j p_jj                                              # eq. 1  overall accuracy
U_i  = p_ii / p_i·                                           # eq. 2  user's accuracy (1 - commission)
P_j  = p_jj / p_·j                                           # eq. 3  producer's accuracy (1 - omission)
V(Ô)   = Σ_i W_i² Û_i(1-Û_i)/(n_i·-1)                         # eq. 5
V(Û_i) = Û_i(1-Û_i)/(n_i·-1)                                  # eq. 6
V(P̂_j) = (1/N̂_·j²) [ N_j·² (1-P̂_j)² Û_j(1-Û_j)/(n_j·-1)
                     + P̂_j² Σ_{i≠j} N_i·² (n_ij/n_i·)(1-n_ij/n_i·)/(n_i·-1) ]   # eq. 7
       N̂_·j = Σ_i (N_i·/n_i·) n_ij ;  N_i· = map pixels (units) in class i
p̂_·k = Σ_i W_i n_ik / n_i·                                   # eq. 9 stratified area proportion (reference-based)
S(p̂_·k) = sqrt( Σ_i (W_i p̂_ik - p̂_ik²)/(n_i·-1) )            # eq. 10
Â_k = A p̂_·k ;  S(Â_k) = A S(p̂_·k) ;  95% CI = Â_k ± 1.96 S(Â_k)   # eq. 11
95% CI for accuracies = ± 1.96 sqrt(V̂)
```
- Report the error matrix "in terms of these estimated area proportions, p̂_ij, and not in terms of sample counts, n_ij" (p. 51).
- Area should be estimated from the reference column total p_·k, not the map row total p_k· (pixel counting), because p_k· "is known with certainty but likely biased because of classification error" (p. 52).
- Kappa: "strongly discouraged" (p. 51).
- Variance formulas assume pixel unit with hard map and reference labels; "would not apply to a polygon assessment unit or to a mixed pixel situation" (p. 52).

## 5. Worked example numbers (§5, pp. 52–55; Tables 5–9)
- 10,000,000 Landsat pixels; deforestation W = 0.020, forest gain 0.015, stable forest 0.320, stable non-forest 0.645. n = 641 from eq. 13 (target S(Ô) = 0.01); chosen Alloc2 = 75/75/165/325 (640 in Table 8).
- Results: U deforestation 0.88 ± 0.07, forest gain 0.73 ± 0.10, stable forest 0.93 ± 0.04, stable non-forest 0.96 ± 0.02; P deforestation 0.75 ± 0.21, gain 0.85 ± 0.23, stable 0.93 ± 0.03 / 0.96 ± 0.01; O = 0.95 ± 0.02. Deforestation area 21,158 ± 6,158 ha vs 18,000 ha mapped (p. 54).
- Use these as a unit test: feeding Table 8 counts and W_i into our implementation must reproduce Table 9 and these CIs.

## 6. Stated limitations (pp. 50–52)
- Covers two-date change with discrete classes; not continuous map variables (p. 51); little work on multi-period strata (p. 47).
- Variance estimators are for pixel units with hard labels (p. 52).
- "most projects will not satisfy every recommendation. Documenting and justifying deviations … are expected" (p. 44).

## 7. How to apply to our pipeline
- **Reporting module (new; e.g. a helper beside `sn8_results.py`, which is read-only):** `good_practice_report(map_labels, ref_labels, strata, W)` returning the area-proportion error matrix (eq. 4), O/U/P with 95% CIs (eqs. 5–7), and reference-based area of "flooded road" with CI (eqs. 9–11). Unit-test against Tables 8–9.
- **Unit = road segment (or road length).** Our scored unit is the labelled road. If we weight by length, use length shares for W_i. State that SpaceNet 8 tiles were not a probability sample of the storm area; per the paper this is a deviation to document, not a fatal flaw.
- **"Cannot assess" share:** report it exactly as p. 45 asks, as the proportion of units for which cloud prevented assessment, separately per class (flooded vs not flooded by label) and per tile, alongside the accuracies on the assessed units. This pairs with the Geifman SGR handoff: coverage there = 1 − cannot-assess share here.
- **Error matrix rows/columns:** rows = our call (flooded / not flooded / cannot assess), columns = SpaceNet 8 label. Report the cannot-assess row; do not drop it silently.
- **Kappa:** if any of our tables or slides report kappa, replace with U/P/O (p. 51, §6.4).
- **Independence:** test sample "separate from (independent of) the data used to train or develop the classification" (§6.1, p. 55) — matches the sealed-data rule.
- **Reference quality caveat:** SpaceNet 8 labels are our reference; the paper's warning that small reference errors bias estimates (p. 50) applies. Analysts "only attribute what was visible" (evidence 10), so under cloud the reference itself is incomplete, which is why PU framing matters.
- **Feasibility:** fully feasible; pure statistics on per-road labels. No image data requirement.

## 8. Key quotes
- "the proportion of the selected sample units for which cloud cover prevented assessment of the unit should be reported" (p. 45)
- "the error matrix should be reported in terms of these estimated area proportions, p̂ij, and not in terms of sample counts, nij" (p. 51)
- "the use of kappa is strongly discouraged" (p. 51)
- "we recommend that area estimation should be based on p⋅k, the proportion of area derived from the reference classification" (p. 52)
- "The sample used for accuracy assessment and area estimation is separate from (independent of) the data used to train or develop the classification." (p. 55)
