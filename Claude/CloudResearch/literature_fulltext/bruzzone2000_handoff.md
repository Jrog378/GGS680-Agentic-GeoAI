# Coder handoff: Bruzzone & Fernández Prieto (2000), Automatic Analysis of the Difference Image for Unsupervised Change Detection

- **Citation:** Bruzzone, L., & Fernández Prieto, D. (2000). Automatic analysis of the difference image for unsupervised change detection. *IEEE Transactions on Geoscience and Remote Sensing* 38(3), 1171–1182. https://doi.org/10.1109/36.843009 (the byline prints "Diego Fernàndez Prieto"; the running head and IEEE indexing use "Prieto")
- **PDF:** `/Users/jusrogers/Masters/papers/bruzzone2000-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.2; 0.47 MB; 12 pages (Read tool and pdfinfo) = journal pp. 1171–1182; title, authors, TGRS vol. 38 no. 3, May 2000 and PII S 0196-2892(00)04130-9 match todo.tsv/DOI 10.1109/36.843009. §VIII Conclusions and References [1]–[38] present (pp. 1180–1182). PASS.
- **Read:** PDF pp. 1–12 = journal pp. 1171–1182 in full (Read tool, page images), including Tables I–IV, Figs. 1–11 and the biographies.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Setting (p. 1172): two co-registered, radiometrically corrected images X1, X2 (I × J). The difference image X_D is the
CVA magnitude, with values in [0, …, G − 1]. A generalisation to other difference images is "straightforward".

1. **Mixture model** (eq. 1, p. 1172): p(X) = p(X|ω_n)P(ω_n) + p(X|ω_c)P(ω_c); ω_n = unchanged, ω_c = changed. Both class
   densities are Gaussian, (μ_n, σ_n²) and (μ_c, σ_c²) (p. 1173).
2. **EM updates** (eqs. 2–4, p. 1173), for class ω_n (ω_c analogous). With posterior
   w_n(x) = P^t(ω_n) p^t(x|ω_n) / p^t(x):
   - P^{t+1}(ω_n) = Σ_x w_n(x) / IJ (eq. 2)
   - μ_n^{t+1} = Σ w_n(x)·x / Σ w_n(x) (eq. 3)
   - (σ_n²)^{t+1} = Σ w_n(x)·(x − μ_n^t)² / Σ w_n(x) (eq. 4). As printed, the variance uses the current mean μ_n^t.
   Iterate "until convergence" (no numeric tolerance given); each iteration increases the log-likelihood to a local
   maximum (p. 1173).
3. **Initialisation** (p. 1173, Fig. 1): T_n = M_D(1 − α), T_c = M_D(1 + α), where M_D is "the middle value of h(X)",
   printed as "M_D = [max{X_D} − min{X_D}]/2", and α ∈ (0, 1). S_n = {X < T_n} and S_c = {X > T_c} give the initial
   estimates. (The printed formula equals the midpoint only when min = 0. Code `(max + min)/2` and note the choice.)
   Values used: α = 0.3–0.7 (Elba, Table I), α = 0.5 (synthetic, p. 1178).
4. **Bayes minimum-error threshold, pixels independent** (§III, eqs. 5–7, p. 1173): assign each pixel to argmax
   P(ω_i)p(X|ω_i). The threshold T_o solves P(ω_c)/P(ω_n) = p(X|ω_n)/p(X|ω_c) (eq. 6). In the Gaussian case this is the
   quadratic (eq. 7):
   `(σ_n² − σ_c²)T² + 2(μ_n σ_c² − μ_c σ_n²)T + μ_c² σ_n² − μ_n² σ_c² − 2σ_n² σ_c² ln[σ_c P(ω_n) / (σ_n P(ω_c))] = 0`
   Take the root between μ_n and μ_c.
5. **Context: MRF** (§IV, eqs. 8–14, pp. 1174–1175):
   - Second-order (8-pixel) neighbourhood, N = {(±1,0), (0,±1), (1,±1), (−1,±1)} (Fig. 2).
   - Prior: Gibbs, U_context = Σ_{neighbours} β·δ_k(C(i,j), C(g,h)), with δ_k = −1 if the labels are equal and 0 otherwise
     (eqs. 11–12).
   - Data term (Gaussian): U_data = ½ ln|2π σ²_{C(i,j)}| + ½ (X(i,j) − μ_{C(i,j)})² / σ²_{C(i,j)} (eq. 14), with the EM
     estimates.
   - Minimise U = Σ [U_data + U_context] (eq. 13) by ICM: (1) initialise each pixel to the class minimising U_data (the
     per-pixel Bayes label); (2) update each pixel to the class minimising eq. 13; (3) repeat (2) until convergence
     (p. 1175).
   - β: 1.6, 1.7, 1.8 on Elba (Table II); 1.3 on synthetic (p. 1178). Set by hand; automatic β selection is future work
     (p. 1180).
6. Note (p. 1180): "other decision strategies could also be adopted… (e.g., the Bayes rule for minimum cost)", meaning
   unequal costs for missed and false alarms.

## 2. Inputs, outputs, data needs
- Input: one scalar difference image (CVA magnitude). Real data: Landsat-5 TM, Elba, Aug vs Sep 1994, 414 × 326 px,
  bands 4 and 7, 3 × 3 running-mean filter on both images, no radiometric correction needed (pp. 1175–1176). Synthetic:
  Daedalus 1268 ATM band 5, Feltwell UK, 250 × 350 px, inserted changes, a histogram shift and zero-mean Gaussian noise
  at SNR 10, 5, 2, 1, 0 dB (p. 1175).
- Output: P(ω_n), P(ω_c), μ, σ per class; T_o; per-pixel map; optional MRF-smoothed map.
- No labels needed. The reference maps are used only to score.

## 3. Quantitative results
- **Elba, EM estimates** (Table I, p. 1176): α = 0.3–0.7 gives μ_n 25.30–25.32, σ_n 18.44–18.46, P(ω_n) 0.98, μ_c
  109.31–110.65, σ_c 36.83–37.36, P(ω_c) 0.02. True values: μ_n 25.47, σ_n 18.64, P(ω_n) 0.98, μ_c 120.73, σ_c 30.31,
  P(ω_c) 0.02. Converges in about six iterations (Fig. 6, p. 1177).
- **Elba, threshold:** T̂_o = 82 for every α against the minimum-error T_o = 84 (manual search). Errors 438 against 424
  (218 false + 220 missed, against 142 false + 282 missed) (p. 1177–1178; Fig. 7).
- **Elba, MRF** (Table II, p. 1178): β = 1.6 gives 138 false, 38 missed, 176 total; β = 1.7 gives 133 / 40 / 173; β = 1.8 gives
  124 / 80 / 204. The minimum-error threshold gives 142 / 282 / 424.
- **Synthetic, EM** (Table III, p. 1179): P(ω_c) 0.03 estimated = true at every SNR; the largest error is μ_c at SNR 1 dB
  (168.00 against 163.78). Iterations: 3 at 10 dB up to 26 at 0 dB (Fig. 10, p. 1179).
- **Synthetic, threshold** (p. 1179): the worst case is SNR 0 dB, T̂_o = 144 against T_o = 142. Errors 940 (839 missed + 101
  false) against 899 (733 + 166).
- **Synthetic, MRF** (Table IV, p. 1180): overall error with context against T_o: 10 dB 5 vs 10; 5 dB 9 vs 137; 2 dB 29 vs 502;
  1 dB 90 vs 685; 0 dB 157 vs 899. The text on p. 1180 says "889" for the 0 dB T_o error; Table IV and p. 1179 say 899.
- No significance tests; one real scene.

## 4. Stated limitations
- Gaussian class densities: reasonable for passive sensors, but "when the number of different typologies of land cover
  changes to be identified increases or when active sensors are used… the Gaussian model might turn out to be
  inappropriate" (p. 1181). Semiparametric or nonparametric mixtures are suggested ([22], [23], [38]).
- The accuracy of T̂_o "depends on the accuracies of the estimates provided by the EM algorithm" (p. 1174).
- β is chosen by trial (Table II); automatic selection is left to future work (p. 1180).
- The usual n·σ_D thresholding assumes "only a few changes occurred", and n is set by trial and error (p. 1172).

## 5. How to apply to our pipeline
Our gates threshold one scalar two-date field: the dark-channel rise (cloud) or the grey or dark fall (flood). That is
exactly the paper's "difference image". The method is feasible on 8-bit grey or RGB with one pre-storm date, and it
needs no NIR. Three differences from the paper:
- Our "changed" class (cloud) is rare on many tiles and absent on clear ones. With P(ω_c) → 0, EM can split clear-ground
  noise into two Gaussians. The paper's P(ω_c) was 0.02–0.03, so it never tested an absent class.
- The dark rise has a long negative tail from parallax and misregistration (ev23 #1). Fit on rise ≥ 0 only, or as a
  three-component mixture (fall / no change / rise).
- The paper fits per scene (one difference image). Per tile at 0.5 m means a few hundred thousand pixels, which is
  enough for EM. Pooled over training tiles matches how production learned 71.4.

### Proposed bench arm: B1 EM/Bayes hysteresis gate (replaces the Le Hégarat-Mascle cuts in G1b)
1. **Field:** the production dark rise y (after − before dark channel, 20 m), valid pixels, per tile.
2. **Fit:** a two-Gaussian EM on y (eqs. 2–4). Initialise with α = 0.5 around the midpoint of [p1, p99.9] of y. A
   fixed-seed alternative: ω_n from y ≤ 71.4 and ω_c from y > 71.4. Stop when the relative log-likelihood change is
   below 1e−6, or after 100 iterations.
3. **Abstain (no cloud) if** P(ω_c) < 0.002, or (μ_c − μ_n)/σ_n < 2, or μ_c < 71.4 − 2σ_n. Starting values; record how
   often each fires on the 94 clear tiles.
4. **Cuts from the posterior:** t_h = the y where P(ω_c|y) = 0.9; t_l = T̂_o from eq. 7, where P(ω_c|y) = 0.5. Then the
   same 8-connected hysteresis as G1, plus G1b's 2,500 m² blob filter.
5. **Variant B1-pooled:** fit once on the pooled 186 training tiles (every 16th pixel), as production did. Report T̂_o next
   to 71.4 as a check of the production Otsu cut.
6. **Variant B1-MRF:** replace hysteresis and blob with the paper's ICM-MRF (eq. 13), using β = 1.6 (Elba) and 1.3
   (synthetic) as starting values and 8 neighbours.
7. **Compare against** production's dark-rise gate (71.4), G1b, and ev23's fix ("t_h = 71.4, t_l from clear-ground
   spread"). Measure Ida precision/recall vs satellite–NOAA disagreement (132 tiles); share flagged on the 94 clear
   tiles and the count with more than 1%; and the road-gate flood gain (21 seeds, paired, 3 × 3 block bootstrap), plus
   the accuracy on the added roads (ev23 fix #6).

### Second arm (lower priority): B2 EM/Bayes on the blue rise for G2
Same as B1 on G2's blue rise after clipping (otsu1979_handoff, arm T1 step 2). Bayes T̂_o replaces the Otsu 240.8 cut.

### Possible later use: flood fall
The same EM/Bayes split on the grey or dark **fall** inside clear ground gives a label-free "darkened" map. It would be a
candidate DINOv2-free baseline for flood change calls, scored on SN8 labels with McNemar against production. It is not
proposed now, because the flood model is the frozen production path.

## 6. Key quotes
- "the decision threshold is fixed at nσ_n from the mean value of the difference image… n being a real number derived by a trial-and-error procedure" (p. 1172)
- "Let us assume that both p(X/ω_n) and p(X/ω_c) can be modeled by Gaussian distributions (this is a reasonable assumption for many applications involving images acquired by passive sensors)." (p. 1173)
- "At convergence, a local maximum of the log-likelihood function is reached" (p. 1173)
- "this is equivalent to thresholding the difference image at the ML boundary T_o between the classes ω_n and ω_c" (p. 1173)
- "the estimates evolve from wrong initial values to accurate final ones in only six iterations" (p. 1177)
- "for β = 1.6, the number of missed alarms decreased from 282 to only 38, and the number of false alarms reduced from 142 to 138." (p. 1178)
- "the Gaussian model might turn out to be inappropriate. In these cases, more general approaches to the mixture density estimation problem … may represent powerful tools" (p. 1181)
