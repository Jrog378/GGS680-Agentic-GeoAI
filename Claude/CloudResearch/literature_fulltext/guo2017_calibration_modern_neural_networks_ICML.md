# Coder handoff: Guo, Pleiss, Sun & Weinberger (2017), On calibration of modern neural networks

- **Citation:** Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *ICML
  2017*, PMLR 70, 1321–1330 (pages confirmed on proceedings.mlr.press/v70/guo17a.html). No DOI (PMLR). arXiv:1706.04599.
- **Copy read:** arXiv v2 (3 Aug 2017, "ICML 2017"), https://arxiv.org/pdf/1706.04599v2. It is 14 pages: the 10-page
  conference paper (8 text + 2 references) plus a 4-page supplement (S1–S4).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/guo2017_calibration_modern_neural_networks_ICML-summary.pdf`
- **Validation:** real PDF; title and authors match PMLR; conclusion, references and supplement present. PASS.
- **Pages read:** arXiv pp. 1–14 (main text, Table 1, supplement). Numeric supplement Tables S1–S3 were skimmed, not
  transcribed. Page numbers below are arXiv pages.
- **Supports ranked fixes (evidence 21):** #2 (calibrated probability + risk–coverage abstention instead of t < 0.2), #3
  (choose cut-offs from data, not by hand).

## Definitions (p. 2)
- Perfect calibration (Eq. 1): `P(Ŷ = Y | P̂ = p) = p` for all p.
- Reliability diagram: M equal-width bins of confidence, `acc(B_m)` against `conf(B_m)`.
- **ECE** (Eq. 3): `ECE = Σ_m (|B_m|/n) · |acc(B_m) − conf(B_m)|`, with M = 15 in all tables.
- **MCE** (Eq. 5): `max_m |acc(B_m) − conf(B_m)|`. The supplement calls it "very sensitive to the binning scheme and is
  less suited for small test sets" (Table S1 caption).
- **NLL** (Eq. 6): `−Σ log π̂(y_i | x_i)`.
- Binary case: confidence = probability of the positive class, `p̂ = σ(z)`.

## Calibrators (§4, pp. 3–4). All are fitted on a held-out validation set with the model frozen
- **Histogram binning:** bin p̂ (equal width or equal mass); `θ_m` = fraction of positives in bin m (Eq. 7).
- **Isotonic regression:** monotone piecewise-constant `f(p̂)` minimising squared loss; jointly optimised bins.
- **BBQ:** Bayesian average over binning schemes (Beta prior).
- **Platt scaling:** `q̂ = σ(a z + b)`, with a and b fitted by NLL.
- **Temperature scaling:** `q̂ = max_k softmax(z/T)` with a single T > 0 fitted by NLL (Eq. 9). It does not change the
  argmax, so "temperature scaling does not affect the model's accuracy" (p. 4). For binary logits it is Platt scaling with
  b = 0.
- Assumption: "the training, validation, and test sets are drawn from the same distribution" (p. 3).

## Results to compare against (pp. 5–6, Table 1, ECE %, M = 15)
- Typical uncalibrated ECE is "between 4 to 10%". Example: CIFAR-100 ResNet-110 (SD) 12.67 → 0.96 with temperature
  scaling, 2.46 with histogram binning and 4.16 with isotonic regression (Fig. 4).
- Temperature scaling "outperforms all other methods on the vision tasks, and performs comparably to other methods on the
  NLP datasets".
- Binning methods "tend to change class predictions which hurts accuracy". Matrix scaling overfits with many classes.
- Causes of miscalibration (Fig. 2): depth, width, batch normalisation and low weight decay. Networks overfit NLL while
  0/1 error still falls (Fig. 3).

## Limitations
- Evidence is from deep CNNs, LSTMs and DANs on natural-image and text benchmarks. Nothing on random forests, pixels or
  remote sensing.
- Same-distribution assumption for validation and test.

## How to apply to our pipeline
- **`sn8_cloudspot.py` (fix 2):** the spotter's learners are a random forest and a linear probe (`LEARNERS`).
  - Add a `calibrate(scores, labels, method)` step fitted on HRC_WHU development folds (out-of-fold scores only).
  - Methods: `isotonic` (sklearn `IsotonicRegression`) and `platt` (logistic on the logit or score). For the linear probe,
    temperature scaling on its logit equals Platt with b = 0.
  - Report ECE (M = 15) and a reliability diagram per method on held-out folds.
  - The paper's "temperature scaling wins" result is for deep nets. For an RF, test isotonic vs Platt rather than assume.
- **Abstention (`sn8_cloudsym.py`, T_MIN = 0.2 "opaque"):** replace the fixed t-cut with a cut on calibrated P(cloud):
  sweep p* and plot risk (road-flood error) against coverage (share of roads assessed). Pick p* for an error budget set in
  advance. Compare with the t < 0.2 rule at matched coverage.
- **Domain-shift check:** calibration fitted on HRC_WHU may not hold on Ida. Also check reliability on the
  NOAA-visible Ida tiles (evidence 17) before trusting p*. If it is off, refit on a separate Ida calibration split, never
  the test split.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** fully feasible. It is a post-hoc step on
  existing scores and needs only labelled held-out pixels.
