# Coder handoff: Otsu (1979), A Threshold Selection Method from Gray-Level Histograms

- **Citation:** Otsu, N. (1979). A threshold selection method from gray-level histograms. *IEEE Transactions on Systems, Man, and Cybernetics* SMC-9(1), 62–66. https://doi.org/10.1109/TSMC.1979.4310076
- **PDF:** `/Users/jusrogers/Masters/papers/otsu1979-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.3; 3.1 MB; 5 pages (Read tool and pdfinfo) = journal pp. 62–66; title, author (Nobuyuki Otsu), journal, vol. SMC-9, no. 1, January 1979 match todo.tsv. The DOI is not printed (1979); the code line "0018-9472/79/0100-0062$00.75" is (p. 62). References [1]–[5] present (p. 66). It is a Correspondence item: p. 62 also carries the end of the previous article, and p. 66 the start of "Book Reviews". PASS.
- **Read:** PDF pp. 1–5 = journal pp. 62–66 in full (Read tool, page images), including Figs. 1–3 with their printed statistics.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Problem framing (p. 62): valley-seeking fails when the valley "is flat and broad, imbued with noise, or when the two peaks are extremely unequal in height". Parametric Gaussian-sum fits need "considerably tedious and sometimes unstable calculations", and Gaussians are "a meager approximation of the real modes". Otsu proposes a nonparametric, unsupervised criterion (abstract, p. 62).

1. **Histogram** (eq. 1, p. 63): L grey levels [1, …, L], n_i pixels at level i, N = Σ n_i; p_i = n_i / N.
2. **Split at level k:** C0 = levels [1, …, k], C1 = [k+1, …, L].
3. **Cumulative moments** (eqs. 6–8): ω(k) = Σ_{i≤k} p_i; μ(k) = Σ_{i≤k} i·p_i; μ_T = μ(L).
   Class probabilities ω0 = ω(k), ω1 = 1 − ω(k) (eqs. 2–3); means μ0 = μ(k)/ω(k), μ1 = (μ_T − μ(k))/(1 − ω(k)) (eqs. 4–5).
4. **Criteria** (eqs. 12–15): λ = σ_B²/σ_W², κ = σ_T²/σ_W², η = σ_B²/σ_T², with
   σ_W² = ω0σ0² + ω1σ1² (eq. 13), σ_B² = ω0(μ0 − μ_T)² + ω1(μ1 − μ_T)² = ω0ω1(μ1 − μ0)² (eq. 14), σ_T² = Σ (i − μ_T)² p_i (eq. 15).
   σ_W² + σ_B² = σ_T² (eq. 16), so all three criteria give the same k; η is the simplest because it needs only first-order statistics (p. 63).
5. **Optimal threshold** (eqs. 17–19, p. 63): η(k) = σ_B²(k)/σ_T²;
   `σ_B²(k) = [μ_T·ω(k) − μ(k)]² / (ω(k)[1 − ω(k)])` (eq. 18); `k* = argmax_{1≤k<L} σ_B²(k)` (eq. 19), searched over the
   "effective range" S* = {k : 0 < ω(k) < 1} (p. 63). A maximum always exists.
6. **Separability** (p. 64): η* = η(k*), 0 ≤ η* ≤ 1; invariant under affine grey-scale maps g′ = a·g + b. η* = 0 only for a
   single constant grey level; η* = 1 only for two-valued pictures. It "can be used as a measure to evaluate the
   separability of classes (or ease of thresholding) for the original picture or the bimodality of the histogram".
   No cut-off on η* is given.
7. **By-products** (p. 64): ω0, ω1 estimate the class areas; μ0, μ1 the class mean levels.
8. **Multithresholding** (p. 64): e.g. two thresholds, σ_B²(k1*, k2*) = max over 1 ≤ k1 < k2 < L. Needs M − 1 thresholds for M
   classes (the Gaussian-sum alternative needs 3M − 1 parameters). Thresholds "become less credible as the number of
   classes to be separated increases"; M = 2 and 3 "cover almost all practical applications".
9. **Behaviour of η(k)** (p. 66, §III-D): "always smooth and unimodal" in the experiments; "The rigorous proof of the
   unimodality has not yet been obtained."

Parameters: none besides the number of grey levels L (the paper's examples use 16, 64, 32 and 256 levels; p. 64).

## 2. Inputs, outputs, data needs
- Input: one grey-level histogram. Nothing else (no spatial information, no labels).
- Output: k* (or k1*, k2*), η*, ω0/ω1, μ0/μ1.
- Note for coders: the paper's histogram is over integer grey levels of a picture. `skimage.filters.threshold_otsu` (0.26.0
  here) builds a 256-bin histogram between the data's min and max for float input. That binning is the library's choice,
  not the paper's, and with heavy-tailed float data the bins get wide.

## 3. Quantitative results (all 64 × 64 pictures; pp. 64–65)
| Figure | Grey levels | k* | η* | ω0 / ω1 | μ0 / μ1 | μ_T, σ_T² |
|---|---|---|---|---|---|---|
| Fig. 1(d) character "A", new ribbon | 16 | 6 | 0.894 | 0.818 / 0.182 | 2.8 / 10.1 | 4.2, 8.831 |
| Fig. 1(h) character "A", old ribbon | 16 | 6 | 0.853 | 0.858 / 0.142 | 3.4 / 9.4 | 4.3, 5.052 |
| Fig. 2(d) texture (broad flat valley) | 64 | 33 | 0.887 | 0.478 / 0.522 | 14.2 / 52.8 | 34.4, 418.033 |
| Fig. 2(h) texture (unimodal peak) | 64 | 32 | 0.767 | 0.266 / 0.734 | 20.8 / 44.6 | 38.3, 143.982 |
| Fig. 3(d) cells, 2 thresholds | 32 | 7, 15 | 0.873 | 0.633 / 0.296 / 0.071 | 4.3 / 10.5 / 20.2 | 7.3, 23.347 |
| Fig. 3(h) cells, 2 thresholds | 256 | 61, 136 | 0.893 | 0.395 / 0.456 / 0.149 | 24.1 / 99.2 / 174.0 | 80.7, 3043.561 |

No error rates, no ground truth, no comparison with other methods; results are judged "of satisfactory practical use"
(p. 66).

## 4. Stated limitations
- Thresholds "become less credible" with more classes (p. 64).
- No proof that η(k) is unimodal (p. 66).
- The paper does not discuss rare classes, heavy tails or outliers. Its smallest class share in the examples is 0.071
  (Fig. 3(d), third class) and 0.142 for a two-class split (Fig. 1(h)). The well-known bias of Otsu's cut toward the
  larger class when class sizes or variances are very unequal is from later literature, not this paper (general
  knowledge, not checked here).

## 5. How to apply to our pipeline
**Why Otsu on the pooled blue rise gave T_blue = 240.8 (bench 2, G2).**
- Otsu maximises ω0·ω1·(μ1 − μ0)² (eq. 14). A small class far from the bulk can win, because the squared distance grows
  faster than the class share falls.
- G2's blue rise is a float field, `after_blue − (gain·before_blue + offset)`, with no clipping (`g2_lin_bluerise.py`).
  In the bench-2 tile cache (200 development tiles, read 2026-10-30, `mask_info["G2"]`), the N3-selector blue gains run
  from 0.063 to 24.4. Their 10th / 50th / 90th percentiles are 0.186 / 1.07 / 5.51, and six tiles have gains above 17
  with offsets from −875 to −1449 (0_18_20: gain 24.4, offset −1366). On those tiles the mapped before-blue spans
  thousands of DN, so the pooled rise has tails of ± thousands.
- `threshold_otsu` then bins min..max into 256 bins. The 8-bit bulk falls in a handful of wide bins, and σ_B² is maximised
  by splitting off the tail. On the smoke tiles (no extreme gains) the same rule gave 19.05, and on one dry-run tile
  2.63. So 240.8 is set by the mis-normalised tiles, not by cloud. This agrees with ev23 "What goes wrong" #2, and the
  cache gains (above 20) are larger than the 3.4 at the 90th percentile quoted there for cloudy tiles.
- Otsu's own diagnostic, η*, was never computed. With a heavy-tailed unimodal bulk it would show whether the histogram
  is two-class at all.

**Production cuts 98 (dark) and 71.4 (dark rise).** They are Otsu on pooled training pixels. The dark rise is bounded
(8-bit, about −255..255), so the binning problem does not arise. But the cloud class is rare on most tiles, so the cut
may sit where the bulk's own tail is split. Report η* and ω1 for both cuts and plot the pooled histograms (already
planned, data_tool_plan R6).

### Proposed bench arm: Otsu-η check and robust cut for the gate thresholds (T1)
1. **Inputs:** the same pooled training-tile fields bench 2 used: (a) G2 blue rise, (b) dark rise. Training tiles only
   (186), every 16th valid pixel, as before.
2. **Sanity transform:** for the blue rise, (i) clip the blue gain to [0.5, 2.0] and fall back to mean/SD matching outside
   it, and (ii) clip the rise to [−255, 255]. Record how many tiles are clipped.
3. **Otsu on integer levels**, as in the paper: histogram over integer DN levels (−255..255, 511 levels), not 256 min–max
   bins. Report k*, η*, ω1, μ0 and μ1 (eqs. 17–19).
4. **Bimodality gate:** accept the Otsu cut only if η* ≥ 0.65. That figure is the bimodality test used in the SAR
   flood-thresholding work our Tiampo 2022 handoff cites (its refs [37, 38]), not Otsu's; Otsu gives no number.
   Otherwise use the alternatives in step 5.
5. **Alternatives compared on the same pooled sample:** (a) the 99th percentile of the field on production-clear pixels
   (ev23 fix #2); (b) the Bruzzone & Fernández Prieto EM/Bayes cut (see `bruzzone2000_handoff.md`, arm B1).
6. **Compare** G2 with each cut against G2 as run (240.8) on: Ida precision/recall vs satellite–NOAA disagreement (132
   tiles), mean share flagged on the 94 clear tiles, and the road-gate flood gain (21 seeds, paired, 3 × 3 block
   bootstrap). Same for the dark rise: a cut that differs from 71.4 by more than 5 DN is a candidate gate arm. Otherwise
   71.4 is confirmed.

## 6. Key quotes
- "An optimal threshold is selected by the discriminant criterion, namely, so as to maximize the separability of the resultant classes in gray levels." (abstract, p. 62)
- "the valley is flat and broad, imbued with noise, or when the two peaks are extremely unequal in height, often producing no traceable valley." (p. 62, on valley methods)
- "Thus we adopt η as the criterion measure to evaluate the 'goodness' (or separability) of the threshold at level k." (p. 63)
- "it can be used as a measure to evaluate the separability of classes (or ease of thresholding) for the original picture or the bimodality of the histogram." (p. 64)
- "the selected thresholds generally become less credible as the number of classes to be separated increases." (p. 64)
- "the histograms typically show the difficult cases of a broad and flat valley (c) and a unimodal peak (g)." (p. 66)
- "The rigorous proof of the unimodality has not yet been obtained." (p. 66)
