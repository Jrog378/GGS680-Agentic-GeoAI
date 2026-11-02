# Coder handoff: Wu, Du & Zhang (2014), Slow feature analysis for change detection in multispectral imagery

- **Citation:** Wu, C., Du, B., & Zhang, L. (2014). Slow feature analysis for change detection in multispectral imagery. *IEEE Transactions on Geoscience and Remote Sensing* 52(5), 2858–2874 (May 2014; "Date of publication July 3, 2013"). https://doi.org/10.1109/TGRS.2013.2266673
- **PDF:** `/Users/jusrogers/Masters/papers/wu2014_slow_feature_analysis_change_detection_TGRS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document, version 1.4; 4.7 MB; 17 pages (Read tool and pdfinfo) = journal pp. 2858–2874; page-1 title, authors (Chen Wu, Bo Du, Liangpei Zhang), TGRS vol. 52 no. 5 May 2014 and DOI 10.1109/TGRS.2013.2266673 match todo.tsv; §V Conclusion (p. 2872) and 56 references (pp. 2873–2874) present. PASS.
- **Read:** PDF pp. 1–17 = journal pp. 2858–2874 in full (Read tool, page images), including Figs. 1–31, Tables I–II, references and biographies.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Notation (p. 2860): bitemporal pixel pair x^i = [x^i_1 … x^i_N], y^i = [y^i_1 … y^i_N], i = 1…P pixels, N = number of bands.

1. **Standardise each band of each date** (eq. 12, p. 2860): `x̂_j = (x_j − μ_xj)/σ_xj`, `ŷ_j = (y_j − μ_yj)/σ_yj`. The text calls σ "the variance"; dividing by it is the usual z-score, so use the standard deviation. "This process also plays a similar role to relative radiometric normalization" (p. 2860).
2. **Two matrices** (eqs. 17–18, p. 2860):
   - `A = (1/P) Σ_i (x̂^i − ŷ^i)(x̂^i − ŷ^i)^T = Σ_Δ` (covariance of the band-wise difference)
   - `B = (1/2P)[Σ_i x̂^i x̂^iT + Σ_i ŷ^i ŷ^iT] = ½(Σ_x + Σ_y)`
3. **Generalised eigenproblem** (eq. 10, p. 2859): `A W = B W Λ`; objective `w^T A w / w^T B w` (eq. 19). Sort eigenvalues λ_1 ≤ … ≤ λ_N; the smallest = slowest = most invariant feature (eq. 11, p. 2859). Constraints (eqs. 14–16): zero mean, unit variance (`w^T B w = 1`), decorrelated outputs. With scipy: `scipy.linalg.eigh(A, B)` returns ascending eigenvalues and B-normalised eigenvectors.
4. **SFA variables** (eq. 20, p. 2860): `SFA_j = w_j^T x̂ − w_j^T ŷ`, j = 1…N. Output band 1 (smallest λ) "contain[s] more change information" (p. 2862): the projection is chosen so unchanged pixels have small differences, so change shows as large |SFA|.
5. **Three training variants** (pp. 2860–2862):
   - **USFA:** A and B from all pixels (Fig. 2). Works when change is a small minority.
   - **SSFA:** A and B from hand-picked unchanged samples (394 px = 0.25% of Taizhou, p. 2863; 714 px = 0.11% of Kunshan, p. 2869).
   - **ISFA** (iterative, pp. 2861–2862):
     a. Start with all weights v^i = 1.
     b. Weighted mean and SD per band (eqs. 23–24): `μ_xj = Σ v^i x^i_j / Σ v^i`, `σ_xj = Σ v^i (x^i_j − μ_xj)² / Σ v^i` (same for y); re-standardise with eq. 12.
     c. Weighted matrices (eqs. 25–26): `A = Σ v^i (x̂^i − ŷ^i)(x̂^i − ŷ^i)^T / Σ v^i`; `B = [Σ v^i x̂^i x̂^iT + Σ v^i ŷ^i ŷ^iT] / (2 Σ v^i)`.
     d. Solve eq. 10, compute SFA_j (eq. 20).
     e. **Change statistic: iterative weighted distance (IWD)** (eq. 27, p. 2862): `T^i = Σ_j (SFA^i_j)² / sqrt(λ_j)`.
     f. **Weights** (eq. 22, p. 2862): `v^i = P{χ²(N) > T^i}`, i.e. `v = scipy.stats.chi2.sf(T, df=N)`. "IWD is then used to calculate the weights with (22)" (p. 2862).
     g. Repeat b–f "until the largest absolute change in √λ is smaller than a small predefined threshold, such as 10⁻⁶" (p. 2862). Converged at iteration 16 (Taizhou, p. 2863) and 24 (Kunshan, p. 2869).
   - Background for the chi-square (eq. 21, p. 2861): `T^i = Σ_j (SFA^i_j / σ_SFAj)² ∈ χ²(N)`, assuming Gaussian SFA variables; "The normalization should ideally be done by the standard deviation of the unchanged pixels." Note for coding: eq. 27 divides by sqrt(λ_j), not by a variance, so T from eq. 27 is not a true χ² variable; the paper uses it in eq. 22 anyway. A cleaner variant is to divide by the weighted variance of SFA_j (eq. 21) for the weights and keep eq. 27 only as the detection image; that is our choice, not the paper's.
6. **Thresholding the final change image** (p. 2867): two-class **k-means** on the one-band IWD image ("Two-class k-means clustering in a one-band image is equal to selecting a threshold"). The chi-square is used only for the weights, **not** as the final change threshold.
7. **Comparison settings** (p. 2867): CVA and difference-PCA ran on ETM data relatively normalised "by bandwise linear regression"; "ED" = Euclidean distance on top-m output bands, "ND" = distance on normalised output bands, IWD for MAD and SFA. For MAD "the rank is reversed" (p. 2868).

## 2. Inputs, outputs, data needs
- Input: two co-registered dates, N bands each, per-pixel vectors. No training labels for USFA/ISFA; SSFA needs unchanged samples.
- Paper data (p. 2863, p. 2868): Landsat-7 ETM+, 30 m, six bands (1–5 and 7). Taizhou, Jiangsu: 400 × 400 px, 17 March 2000 and 6 Feb 2003 (urban expansion). Kunshan, Jiangsu: 800 × 800 px, 2000 and 2003 (urban expansion, farmland to pools).
- Test samples by visual analysis: Taizhou 3172 city expansion, 564 soil change, 490 water change, 16 890 unchanged; change classes merged = 4227 (pp. 2864, 2867). Kunshan 9558 city expansion, 6506 farmland change, 48 119 unchanged; merged = 16 064 (pp. 2870, 2872).
- Output: N SFA bands, IWD image (eq. 27), ISFA weight image (no-change probability, Fig. 10 p. 2864), binary map by k-means.
- **Band count matters.** With N bands the method returns N features and the χ² has N degrees of freedom. With **one grey band**, A and B are scalars, the single SFA variable is a multiple of x̂ − ŷ (the standardised difference) and the eigenproblem has nothing to choose; ISFA reduces to "re-standardise each date on high-weight pixels, recompute the difference, re-weight with χ²(1)". It is then an iteratively re-weighted relative normalisation of the difference, essentially IR-MAD in one band. With **three RGB bands** SFA can pick colour directions in which unchanged pixels agree across dates. In the paper, accuracy with only the top 1 output band was low for every method and rose sharply at 2 bands (Fig. 18, p. 2868; Fig. 30, p. 2872; read from graphs).
- Cost: 4.8 s for 16 iterations on 400 × 400 × 6 (p. 2863); about 27 s for 24 iterations on 800 × 800 × 6 (p. 2869); Core i3 3.07 GHz, 6 GB RAM.

## 3. Quantitative results
Maximum kappa (number of top bands in parentheses) and AUC, threshold **adjusted to the best kappa** ("we adjusted the threshold and only show the highest kappa coefficient", p. 2867):

Table I, Taizhou (p. 2868):
| Method | ED kappa | ED AUC | ND kappa | ND AUC | IWD kappa | IWD AUC |
|---|---|---|---|---|---|---|
| CVA | 0.7804 (5) | 6.2013 (6) | 0.7777 (6) | 5.9793 (6) | — | — |
| PCA | 0.7767 (6) | 6.2019 (5) | 0.7660 (3) | 6.2779 (2) | — | — |
| MAD | 0.8784 (2) | 7.8506 (2) | 0.8606 (4) | 7.6340 (2) | 0.8606 (4) | 7.6340 (2) |
| IRMAD | 0.9540 (2) | 8.7019 (2) | 0.9063 (2) | 8.1873 (2) | 0.9472 (2) | 8.7656 (2) |
| USFA | 0.9105 (4) | 8.0498 (4) | 0.8919 (4) | 7.7326 (2) | 0.9059 (5) | 8.0690 (4) |
| SSFA | 0.9312 (2) | 8.3138 (2) | 0.9492 (3) | 8.8960 (3) | 0.9518 (3) | 8.6398 (3) |
| ISFA | 0.9575 (2) | 8.7660 (2) | 0.9410 (3) | 8.6822 (3) | 0.9622 (4) | 8.9086 (3) |

Table II, Kunshan (p. 2872):
| Method | ED kappa | ED AUC | ND kappa | ND AUC | IWD kappa | IWD AUC |
|---|---|---|---|---|---|---|
| CVA | 0.6711 (6) | 4.6852 (6) | 0.6876 (6) | 4.7548 (6) | — | — |
| PCA | 0.6711 (6) | 4.6852 (6) | 0.6419 (4) | 4.3219 (2) | — | — |
| MAD | 0.8591 (2) | 6.8367 (2) | 0.8666 (2) | 6.9111 (2) | 0.8666 (2) | 6.9111 (2) |
| IRMAD | 0.9196 (2) | 8.0372 (2) | 0.9177 (2) | 7.8760 (2) | 0.9327 (2) | 8.1824 (2) |
| USFA | 0.9002 (2) | 7.6154 (2) | 0.9051 (2) | 7.6308 (2) | 0.9032 (6) | 7.6335 (2) |
| SSFA | 0.9378 (2) | 8.2993 (2) | 0.9242 (2) | 7.9785 (2) | 0.9432 (2) | 8.3116 (2) |
| ISFA | 0.9192 (2) | 8.0369 (2) | 0.9232 (2) | 7.9873 (2) | 0.9264 (4) | 8.1295 (2) |

- The AUC column is on a 0–9 scale in Figs. 19 and 31 ("Area under Curve is the area under the Receiver operating characteristic logarithm curves", p. 2867); it is not the usual 0–1 AUC.
- **Automatic (k-means) binary maps:** Taizhou kappa USFA 0.7190, SSFA 0.7771, ISFA 0.8514 (p. 2867). Kunshan kappa USFA 0.8235, SSFA 0.5752, ISFA 0.5903 (p. 2871): with the automatic threshold ISFA was far below USFA on the harder scene.
- On Kunshan, ISFA is below IR-MAD on ED (0.9192 vs 0.9196) and IWD (0.9264 vs 0.9327); SSFA is best (p. 2872).
- No significance tests; one pair of dates per scene; test samples visually selected (selected pixels, not a probability sample).

## 4. Stated limitations
- USFA assumes most of the scene is unchanged; widespread real change "will obviously affect the transformation matrix and reduce the accuracy" (p. 2861).
- SSFA depends on "the quality and quantity of the training samples" and is "not automatic and self-adaptive" (pp. 2861, 2868).
- ISFA weights can be wrong in complex scenes: "the unchanged city regions were not highlighted … because the changes in the study scene are so complex that the weight may not be assigned correctly in the unsupervised iterative process" (p. 2870).
- Automatic thresholding: "we need to look for a more effective automatic threshold method" (p. 2871).
- It is impossible to choose the best output bands automatically, hence IWD over all bands (p. 2868).

## 5. How to apply to our pipeline
- **Feasibility.** Uses only the two dates' pixel values; no NIR, no labels (USFA/ISFA). Works on uint8 after casting to float. A tile of 0.5 m RGB is fine computationally (3 × 3 matrices). Constraints: (a) with grey only it collapses to a standardised difference (see §2), so run it on RGB; (b) the transform is **global per tile** (one W for the whole tile), so it can cancel a haze colour cast that is the same over the tile, not a spatially varying haze thickness; (c) clouded pixels are change to SFA. Opaque cloud will get low weight in ISFA (good: it is excluded from the fit) but will also score as change in the IWD image. So SFA cannot be the cloud/flood separator; the cloud mask (HOT D1b) must remove clouded pixels before the flood statistic is read.
- **Tie to the bench.** Our IR-MAD tone arm (C2) diverged on 7 tiles in bench 1 and was dropped (evidence 22). ISFA has the same re-weighting loop (χ² no-change weights), so expect the same failure mode on tiles where change or cloud dominates; reuse C2's "IR-MAD failed → abstain" guard. The difference from MAD: SFA minimises the difference covariance relative to the pooled covariance (eq. 19), while MAD maximises the variance of differences of canonical variates; on Taizhou SFA's IWD beat IR-MAD, on Kunshan it did not (Tables I–II).
- **Why it may help on RGB.** If haze adds roughly the same colour vector to every unchanged pixel in the after image, the band-wise difference of unchanged pixels lies near one direction; the slowest SFA directions are those nearly orthogonal to it. That is a HOT-like idea (HOT also picks a direction in colour space) learned from the data instead of fixed. This is our inference, not tested in the paper (the paper's nuisance sources are named as atmosphere, illumination and calibration, p. 2858, but no haze experiment is run).

### Proposed bench arm: ISFA-RGB change cue
1. Inputs: before RGB and after RGB of one tile, float32; drop pixels flagged cloud by the production cloud mask (D1b HOT) and saturated pixels (any band ≥ 250) from the **fit** only.
2. Run ISFA (§1 step 5): weights start at 1; weighted z-score per band (eqs. 23–24, 12); A, B (eqs. 25–26); `eigh(A, B)`; SFA (eq. 20); IWD `T = Σ SFA_j² / sqrt(λ_j)` (eq. 27); `v = chi2.sf(T, 3)` (eq. 22). Stop when max |Δ sqrt(λ)| < 1e-6 (p. 2862) or after 50 iterations; if A or B is singular or not converged → abstain (reuse the C2 guard).
3. Two cue variants: (a) IWD over all 3 bands (paper default); (b) |SFA_1| only (slowest feature), which is the most haze-invariant if the cast is a single direction.
4. Aggregate to the DINOv2 patch grid (mean over each 14 × 14 patch, ~7 m) so the cue is on the same grid as the DINOv2 change heatmap.
5. Compare on the same tiles and roads as the frozen bench: (i) the DINOv2 change cue alone (production); (ii) ISFA cue alone; (iii) a grey standardised difference (the one-band SFA, to show what the RGB directions add); (iv) DINOv2 + ISFA cue as an extra feature. Score flood calls with the bench's 21-seed flood gain and exact McNemar against production; also show ISFA weight images and IWD heatmaps next to the DINOv2 heatmap on hazy tiles (show-imagery rule).
6. Report the binary-threshold step separately: k-means 2-class on IWD (p. 2867) vs the production threshold. Expect k-means to be unstable (Kunshan ISFA kappa 0.5903, p. 2871).
- Starting parameters: χ² df = 3; convergence 1e-6 on sqrt(λ); max 50 iterations; no hand-picked samples.

### Possible later arm: SSFA with labelled unchanged roads
SSFA learns W from unchanged samples only. Our published SN8 labels give non-flooded roads/buildings: use those pixels (cloud-free, train split only) as the unchanged set to fit W, then apply to the tile. This uses human labels unmodified (labelled-data-only rule). On Kunshan SSFA was the best method (Table II).

## 6. Key quotes
- "SFA extracts the most temporally invariant component from the multitemporal images to transform the data into a new feature space. In this feature space, the differences in the unchanged pixels are suppressed so that the changed pixels can be better separated." (p. 2858, abstract)
- "the SFA change detection algorithm aims to find a function that obtains the lowest covariance of the difference values between the temporally invariant samples across different times while containing the most information." (p. 2860)
- "The weight is then assigned to measure the probability of nonchange, which is the probability of the value being greater than T in the χ² distribution" (p. 2862)
- "Iterations are performed until the largest absolute change in √λ is smaller than a small predefined threshold, such as 10⁻⁶." (p. 2862)
- "Two-class k-means clustering in a one-band image is equal to selecting a threshold to separate the image." (p. 2867)
- "the changes in the study scene are so complex that the weight may not be assigned correctly in the unsupervised iterative process." (p. 2870)
- "This indicates that we need to look for a more effective automatic threshold method to satisfy these results in our future work." (p. 2871)
