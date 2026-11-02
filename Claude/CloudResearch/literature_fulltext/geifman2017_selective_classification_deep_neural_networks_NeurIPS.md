# Coder handoff: Geifman & El-Yaniv (2017), Selective Classification for Deep Neural Networks

- **Citation:** Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. *Advances in Neural Information Processing Systems 30* (NeurIPS 2017), 4878–4887. arXiv preprint version: https://arxiv.org/abs/1705.08500 (v2, 1 Jun 2017).
- **PDF:** `/Users/jusrogers/Masters/papers/geifman2017_selective_classification_deep_neural_networks_NeurIPS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/1705.08500 (12 pages, single column). The NeurIPS proceedings version is 10 pages (4878–4887, two-column); same title, authors, algorithm and tables. Page numbers below are the arXiv copy's 1–12. No DOI for the NeurIPS paper; arXiv DOI 10.48550/arXiv.1705.08500 (OpenAlex).
- **Validation:** PDF (614 KB), 12 pages (Read tool; pdfinfo agrees); first page title/authors match; Concluding Remarks (§6) and 19 references present. Page count differs from the 10-page proceedings range because this is the arXiv layout. PASS (preprint version noted).
- **Read:** pp. 1–12 in full (references pp. 11–12 skimmed).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Definitions (§2, p. 3)
- Selective classifier (f, g): f classifier, g: X → {0,1}; output f(x) if g(x)=1, "don't know" if g(x)=0.
- Coverage φ(f,g) = E_P[g(x)] (share accepted). Selective risk (eq. 1): R(f,g) = E_P[ℓ(f(x),y) g(x)] / φ(f,g) (error on accepted cases).
- Risk-coverage curve = selective risk as a function of coverage, swept over thresholds θ.
- Goal (eq. 2): choose g so that Pr_{S_m}{ R(f,g) > r* } < δ, maximising coverage. r* = target risk, δ = confidence parameter, S_m = labelled calibration set of m i.i.d. samples.

## 2. Algorithm: Selection with Guaranteed Risk (SGR) (Algorithm 1, p. 4)
Inputs: trained classifier f, confidence-rate function κ_f (only needs to *rank* cases, p. 3), δ, r*, labelled set S_m.
```
g_θ(x) = 1 if κ_f(x) >= θ else 0                        # eq. 3
sort S_m by κ_f ascending (index = rank)
z_min = 1; z_max = m
for i in 1..k, k = ceil(log2 m):
    z = ceil((z_min + z_max)/2)
    θ = κ_f(x_z); g_i = g_θ
    r̂_i = empirical selective risk of (f, g_i) on S_m       # errors among accepted / n accepted
    b*_i = B*(r̂_i, δ/k, g_i(S_m))                          # Lemma 3.1, eq. 4
    if b*_i < r*: z_max = z      # bound OK -> try accepting more (lower θ)
    else:         z_min = z
return (f, g_k), b*_k
```
- **B\* (eq. 4, Lemma 3.1, Gascuel & Caraux 1992):** with n accepted samples and empirical error r̂, B* is the b solving Σ_{j=0}^{n·r̂} C(n,j) b^j (1−b)^{n−j} = δ — i.e. the exact one-sided binomial (Clopper–Pearson) upper bound. Then Pr{R > B*} < δ. "the numerical bound of Lemma 3.1 is the tightest possible in this setting"; Hoeffding-type bounds "incur some slack" (p. 5). In code: `scipy.stats.beta.ppf(1 - δ/k, e + 1, n - e)` with e = number of errors (the standard Clopper–Pearson form of the same equation), or solve eq. 4 with `scipy.optimize.brentq` on `binom.cdf(e, n, b) - δ/k`.
- **Theorem 3.2 (p. 5):** union bound over the k iterations, hence δ/k in each test.
- Footnote 1 (p. 6): "if κ is severely skewed (far from ideal), the bound of the resulting selective classifier can be far from the target risk."
- Footnote 2 (p. 8): with δ = 0.001 and 6–7 rows per table they did not apply a Bonferroni correction across the different r* values.

## 3. Confidence-rate functions (§4, p. 6)
- **Softmax response (SR):** κ = max_j f(x|j). Only ranking matters: "the ideal confidence-rate function should only provide coherent ranking rather than absolute probability values".
- **MC-dropout:** several forward passes with dropout in the last FC layer; κ = −variance of the top-class neuron.
- An ideal κ satisfies κ(x1) ≤ κ(x2) iff loss(x1) ≥ loss(x2); the risk-coverage curve is the way to judge a κ.

## 4. Parameters and data the authors used (§5, pp. 6–10)
- δ = 0.001 throughout. Calibration (S_m) = random half of the validation set; the other half held out to test the bound. CIFAR: ~5,000 / ~5,000; ImageNet: ~25,000 / ~25,000.
- Models: VGG-16 (CIFAR-10 validation accuracy 93.54), VGG-16 and ResNet-50 on ImageNet.

## 5. Quantitative results (test risk / test coverage, bound b*)
- CIFAR-10 (Table 1, p. 8): r* 0.01 → 0.0092 / 0.7856 (b* 0.0099); r* 0.02 → 0.0149 / 0.8466; r* 0.05 → 0.0486 / 0.9596.
- CIFAR-100 (Table 2, p. 9): r* 0.02 → 0.0187 / 0.2134; r* 0.10 → 0.0938 / 0.5952; r* 0.25 → 0.2395 / 0.8826.
- ImageNet VGG-16 top-5 (Table 4, p. 10): r* 0.02 → 0.0179 / 0.5351. ResNet-50 top-5 (Table 6): r* 0.02 → 0.0189 / 0.5935.
- Test risk never exceeded b* in any table. SR ≈ MC-dropout on CIFAR; on ImageNet top-1 at 60% coverage SR ~10% error vs MC-dropout >20% (p. 7).
- These are image-classification numbers; nothing remote-sensing. They are not comparison targets for us, only evidence that the bound is tight with thousands of calibration samples.

## 6. Stated limitations (§6, pp. 10–11)
- f is trained first and g learned afterwards; training both jointly "would be the most challenging open question".
- Only 0/1 loss; extending "to fully control false-positive and false-negative rates" is left open.
- Guarantee assumes calibration and test are i.i.d. from the same P (§2–3). (Our inference: a shift between storms, sensors or cloud regimes breaks it.)

## 7. How to apply to our pipeline
- **Where:** the road-level decision `assess / correct / cannot assess` in `sn8_refhaze.road_handling` and `sn8_cloudsym.either_date_handling`, and the cloud gate fed by `sn8_cloudspot` (`spot_table`). Today "cannot assess" is set by fixed cuts (T_MIN = 0.2 on t; bright-mask share; spotter share). SGR replaces a hand-set cut with one chosen to meet a stated error target.
- **Recipe (new helper, e.g. `sgr_threshold(kappa, correct, r_star, delta)` in a new module; the listed modules are read-only):**
  1. Pick a per-road confidence κ that ranks roads by how assessable they are. Candidates already computed per road: minimum or 10th-percentile t on the road strip (`sn8_refhaze`), 1 − cloud-spotter share (`sn8_cloudspot.spot_table`), 1 − dark/bright mask share (`sn8_clouds.cloud_table`), and the flood classifier's margin |p − 0.5|. Each candidate is an arm; compare their risk-coverage curves (and AURC, area under the curve) on development roads.
  2. "Correct" = the flood call for that road matches the SpaceNet 8 label. Calibration set = labelled development roads (A/D splits per the reserve-data rule); the bound is then checked on a separate labelled split, as the paper did with the held-out half.
  3. Run SGR for r* in e.g. {0.05, 0.10, 0.15} with δ = 0.05 or 0.01 (δ = 0.001 needs thousands of roads). Report r*, b*, test risk, test coverage per row, in the paper's Table 1 format.
  4. Report coverage = share of roads assessed; 1 − coverage = the "cannot assess" share (feeds the Olofsson-style reporting).
- **Caveat on size:** with n accepted roads the binomial bound is wide. Rough guide (Clopper–Pearson, our arithmetic, not from the paper): 0 errors in 100 roads gives an upper bound of about 3% at δ = 0.05; 5 errors in 100 gives about 10%. With a few hundred development roads, targets below ~5% will force very low coverage.
- **Class balance:** the paper controls total 0/1 error only. Flooded roads are the minority, so a low total risk can hide a high miss rate on flooded roads. Run SGR separately on the flooded-label subset (or use a FNR target) — the paper names FP/FN control as open, so this is our extension.
- **Do not** pick κ or r* on the held-out data used to test the bound (eq. 2 is over calibration samples only).
- **Feasibility:** fully feasible with our data; needs only per-road scores and labels, no extra bands or dates. Cost is trivial.

## 8. Key quotes
- "Our method allows a user to set a desired risk level. At test time, the classifier rejects instances as needed, to grant the desired risk (with high probability)." (abstract, p. 1)
- "The entire performance profile of such a classifier can be specified by its risk-coverage curve" (p. 3)
- "if κ is severely skewed (far from ideal), the bound of the resulting selective classifier can be far from the target risk." (footnote 1, p. 6)
- "the test risk is always bounded above by the bound b∗, as required." (p. 8)
- "It would be of great importance to extend our techniques to other loss functions and specifically to regression, and to fully control false-positive and false-negative rates." (p. 11)
