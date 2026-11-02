# Coder handoff: Liu, Bruzzone, Bovolo & Du (2015), Hierarchical Unsupervised Change Detection in Multitemporal Hyperspectral Images

- **Citation:** Liu, S., Bruzzone, L., Bovolo, F., & Du, P. (2015). *IEEE TGRS* 53(1), 244–260 (published online 29 May 2014; our notes cite it as "Liu et al. 2014"). https://doi.org/10.1109/TGRS.2014.2321277
- **PDF:** `/Users/jusrogers/Masters/papers/liu2015_hierarchical_unsupervised_change_detection_hyperspectral_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** authors' accepted manuscript, University of Trento RSLab: https://rslab.disi.unitn.it/papers/10.1109TGRS.2014.2321277.pdf — IEEE cover sheet + manuscript pages numbered 1–39. Page numbers below are the manuscript's.
- **Validation:** `file` = PDF; 2.4 MB; 40 pages (Read tool and pdfinfo agree); cover and p. 1 title/4 authors/DOI match Crossref; Discussion and Conclusion (pp. 32–34) and references present; 40 manuscript pages vs 17 journal pages expected for a single-column accepted manuscript. PASS (accepted-manuscript pagination noted).
- **Read:** pp. 1–34 in full (incl. Tables I–III); references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§III, pp. 12–21, Figs. 2–6)
Inputs X1, X2 (B bands, P × Q), radiometrically corrected and co-registered. `X_D = X2 − X1` (eq. 1); each pixel's spectral change vector (SCV) `x_i`.
1. **Pseudo-binary CD (§III.A):** magnitude `ρ_i = sqrt(Σ_b (X_D^b)²)` (eq. 2). Threshold T by Bayes minimum error with EM-estimated 2-Gaussian mixture. Margin δ around T gives three classes (eq. 3): changed `Ω_c` if ρ ≥ T + δ; uncertain `Ω_u` if T − δ ≤ ρ < T + δ; unchanged `Ω_n` if ρ < T − δ. δ set "such that the u class includes 25% of the pixels in n" (p. 25).
2. **HSCVA (§III.B):**
   - Homogeneity test of a node: SAD of each SCV to the node mean `S`, `θ(x_i, S) = arccos(Σ x_i^b S^b / (‖x_i‖‖S‖))` (eq. 4); node is one change endmember if `std(θ) < T_θ`.
   - Else: PCA on the node's SCVs only; keep PCs holding > 95% of change information; x-means clustering (BIC split/merge) in range `U = [k0, k0 + t]`, `t = 3` in experiments; `k0` (≥ 2) = number of modes of the compressed change direction `β(P_i) = arccos( Σ_m P_i^m / (√M ‖P_i‖) )` (eq. 5).
   - Recurse on each child until all leaves pass the test. Endmembers can stop at different depths.
3. **Uncertain pixels (§III.C):** assign each `x_i ∈ Ω_u` to `argmin_{e_j ∈ {e, e_n}} θ(x_i, S_{e_j})` (eq. 6).

## 2. Parameters used
- T_θ = 0.05 (simulated), 0.13 (Hyperion Oregon), 0.15 (Hyperion Yancheng) — "a user dependent parameter" controlling homogeneity (p. 25, 29, 31).
- δ: u = 25% of n; t = 3; PCs to 95%; baselines k-means/FCM given the proposed method's k, 200 runs averaged.

## 3. Data
- Simulated: Nuance FX camera, 31 bands 420–720 nm, 1392 × 1040, Harvard scene; 8 tiles pasted elsewhere → 10 change endmembers; "changes associated either to the material transitions or to the same material transitions but affected by different illumination conditions" (p. 21). Three pairs.
- Hyperion (30 m), Hermiston OR, 211 × 396, 1 May 2004 / 8 May 2007, 159 bands; Yancheng China wetland, 252 × 526, 3 May 2006 / 23 Apr 2007, 132 bands. Pre-processing: stripe repair, atmospheric correction, co-registration (0.5 px residual), radiometric correction "to mitigate differences in illumination conditions … thus reducing changes that are mainly irrelevant to the application" (p. 22). **No ground truth** for either Hyperion pair.

## 4. Results
- Simulated (Table I, mean of 3): κ 0.9930 ± 0.0009 (proposed), 0.9772 (PCA k-means), 0.9002 (PCA FCM); multi-class Bhattacharyya 5.91 / 5.28 / 5.03.
- One simulated case (Table II): errors 650 vs 1,367 vs 2,218 px; tree 3 levels, 14 nodes, 10 leaves.
- Hyperion Oregon: 15 endmembers, tree 4 levels/20 nodes; Bhattacharyya 4.12 vs 3.78 vs 3.65. Yancheng: 17 endmembers, 5 levels/27 nodes; 3.89 vs 3.49 vs 3.30. Validated "by the detailed photointerpretation", qualitatively.

## 5. Stated limitations (pp. 33–34)
- Magnitude compression in step 1 can lose change information → missed alarms.
- T_θ must be tuned to the user's sensitivity; no automatic choice.
- Future: test "on the available multitemporal HS images showing differences in illumination conditions and no real change"; add spatial information; data with exhaustive ground truth.

## 6. Nuisance vs change of interest (what the user asked for)
- **Not addressed by the method.** "We assume that the considered images are all radiometric corrected, thus change endmembers are only related to the application and the end-user. Note that the external factors (e.g., illumination conditions, seasonal effects) might have impacts on the detected change endmembers (causing differences) but will not be identified as one of them due to its low change magnitude" (p. 12). Nuisance is assumed removed by pre-processing and the magnitude threshold.
- In the simulated test, illumination-only differences are scored as **real change endmembers** (subtle changes), the opposite of treating them as nuisance.

## 7. How to apply to our pipeline
- **Three-way decision with a margin** (useful): in `sn8_cloudsym.change_gate` / `cloud_dates` and in `sn8_refhaze` gating, replace a single cut on dark-rise by `cloud` (≥ T + δ), `uncertain` (T ± δ), `clear` (< T − δ), with T from EM + Bayes on the dark-rise histogram and δ set so `uncertain` is a fixed share (paper: 25% of the clear count). Then assign uncertain pixels by similarity to the cloud-class mean vs the clear-class mean of a per-pixel change vector (e.g. RGB difference after − tone(before)), i.e. eq. 6 with 3 bands. This is a principled version of the current hysteresis (`HYSTERESIS_LOWS`).
- **Spectral-angle split of the change class (RGB):** compute the RGB change vector after − tone(before). Haze/thin cloud lifts all three bands with a blue-heavy direction (Várnai 2009); floodwater darkens (and shifts toward blue-green/brown). A two-level split (k-means/x-means on the 3-D change vectors of changed pixels, with the angle-homogeneity stop rule) can separate a haze branch from a flood branch before correction. With only 3 bands the "subtle change" depth will be 1–2 levels.
- **Feasibility:** feasible on RGB uint8; greyscale removes the direction information and leaves only magnitude, which is exactly the paper's step 1 that it says loses information. No SAR/NIR needed.

## 8. Key quotes
- "We assume that the considered images are all radiometric corrected, thus change endmembers are only related to the application and the end-user." (p. 12)
- "In order to reduce the effect of possible thresholding errors and obtain conservative results that do not propagate significant errors in the next steps, a margin δ is set on the threshold" (p. 14).
- "we progressively decompose the complex problem into several specific sub-problems" (p. 33).
