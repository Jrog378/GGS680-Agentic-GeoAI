# Coder handoff: Li, Guo & Elkan (2011), A positive and unlabeled learning algorithm for one-class classification of remote-sensing data

- **Citation:** Li, W., Guo, Q., & Elkan, C. (2011). A positive and unlabeled learning algorithm for one-class classification of remote-sensing data. *IEEE Transactions on Geoscience and Remote Sensing* 49(2), 717–725 (February 2011; "Date of publication August 30, 2010"). https://doi.org/10.1109/TGRS.2010.2058578
- **PDF:** `/Users/jusrogers/Masters/papers/li2011_pul-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`; the merge checked out, but deleting the staging copy was refused by the session's permission check, so it is still there for Justin to remove).
- **Validation:** `file` = PDF document, version 1.4; 1.6 MB; 9 pages (Read tool and pdfinfo) = journal pp. 717–725; page-1 title, authors (Wenkai Li, Qinghua Guo, Charles Elkan), TGRS vol. 49 no. 2 Feb 2011 and DOI 10.1109/TGRS.2010.2058578 match todo.tsv; §V Conclusion (p. 724) and 45 references (pp. 724–725) present. PASS.
- **Read:** PDF pp. 1–9 = journal pp. 717–725 in full (Read tool, page images), including Figs. 1–5, Tables I–II, references and biographies.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Notation (p. 718): y ∈ {1, −1} true class (positive = class of interest); s ∈ {1, 0} whether the pixel is labelled.

1. **Assumptions** (p. 718):
   - Only positives are labelled: `p(s = 1 | x, y = −1) = 0` (eq. 1).
   - **Selected completely at random (SCAR):** `p(s = 1 | x, y = 1) = p(s = 1 | y = 1) = c` (eq. 2), "the probability that a positive example is labeled is the same constant regardless of x".
2. **Train a "nontraditional" classifier** g(x) = p(s = 1 | x) on labelled (s = 1) vs unlabelled (s = 0) pixels. Then `f(x) = p(y = 1 | x) = g(x)/c` (eq. 3; lemma from Elkan & Noto 2008, ref. [13]).
3. **Estimate c** (p. 718–719): hold out a validation set V (25% of the training set, p. 719); P = labelled pixels in V; `e = (1/n) Σ_{x∈P} g(x)` (eq. 4), n = |P|.
4. **Decide:** positive if `f(x) = g(x)/c > 0.5`, i.e. `g(x) > 0.5·c` (p. 719, p. 723). "A reweighting approach generates similar output to the adjusting threshold, but it requires retraining the classifier and hence, is not implemented in this study" (p. 724).
5. **Classifier used for g** (p. 719): backpropagation neural network, regularised mean-squared-error objective, log-sigmoid output; trained 10 times with the same inputs and structure, outputs averaged. Layer sizes and regularisation weight not given. Any classifier with calibrated probabilities works (p. 724).

Baselines (pp. 719–720):
- **BSVM** (biased SVM, SVMlight): RBF kernel; grid c = 2⁻⁷, 2⁻⁶, …, 2⁰; j = 2³, 2⁴, …, 2⁸; γ = 2⁻⁴, 2⁻², …, 2¹⁰ (c = C₋, j = C₊/C₋); model selection by r²/Pr[f(X) = 1] on a 25% validation set (refs. [12], [38]).
- **OCSVM** (LIBSVM, positives only): RBF γ in (0, 1000] step 0.1, ν in (0, 1) step 0.01, **tuned on the test set** "to investigate its best achievable performance".
- **GDD** (dd_tools, positives only): θ and r in [0.01, 1] step 0.01, **tuned on the test set**.

## 2. Inputs, outputs, data needs
- Data (p. 719): Leica ADS40 aerial photograph, 2004, **0.3 m**, three bands R (610–660 nm), G (535–585 nm), B (430–490 nm). 15 features: mean, variance, homogeneity, contrast and second moment of each of R, G, B, computed in ENVI with a 3 × 3 template, rescaled to [0, 1].
- Scene one: Richmond, CA, 350 m × 350 m, 1 366 561 pixels (urban, tree, grass, soil, water). Scene two: El Cerrito, CA, 500 m × 500 m, 2 778 889 pixels (urban, tree, grass, soil).
- Per class (p. 719): 5000 labelled pixels by manual interpretation (3000 positive, 2000 negative) + 5000 randomly selected background pixels as the unlabelled set. Training: 1000 positive + the unlabelled set; testing: 2000 positive + 2000 negative. Labelled pixels < 0.4% of the image. 10 random realisations.
- Output: binary map of the one class; OA and kappa.

## 3. Quantitative results
Table I, scene one (p. 722), mean (SD) over 10 draws:
| Class | PUL OA | PUL κ | BSVM OA | BSVM κ | OCSVM OA | OCSVM κ | GDD OA | GDD κ |
|---|---|---|---|---|---|---|---|---|
| Urban | 89.71 (0.72) | 0.79 (0.01) | 88.49 (0.55) | 0.77 (0.01) | 74.43 (1.05) | 0.49 (0.02) | 74.71 (1.54) | 0.49 (0.03) |
| Tree | 80.56 (0.87) | 0.61 (0.02) | 78.76 (1.01) | 0.58 (0.02) | 75.30 (0.58) | 0.51 (0.01) | 72.96 (0.66) | 0.46 (0.01) |
| Grass | 86.53 (0.57) | 0.73 (0.01) | 84.05 (1.38) | 0.68 (0.03) | 76.06 (0.67) | 0.52 (0.01) | 76.21 (0.54) | 0.52 (0.01) |
| Water | 96.51 (0.32) | 0.93 (0.01) | 95.17 (0.44) | 0.90 (0.01) | 87.33 (1.06) | 0.75 (0.02) | 90.97 (0.46) | 0.82 (0.01) |
| Soil | 85.44 (0.52) | 0.71 (0.01) | 84.86 (1.24) | 0.70 (0.02) | 75.73 (0.84) | 0.51 (0.02) | 73.86 (0.87) | 0.48 (0.02) |

Table II, scene two (p. 723):
| Class | PUL OA | PUL κ | BSVM OA | BSVM κ | OCSVM OA | OCSVM κ | GDD OA | GDD κ |
|---|---|---|---|---|---|---|---|---|
| Urban | 91.04 (0.60) | 0.82 (0.01) | 89.77 (0.62) | 0.80 (0.01) | 70.34 (1.00) | 0.41 (0.02) | 70.97 (0.92) | 0.42 (0.02) |
| Tree | 84.64 (0.59) | 0.69 (0.01) | 82.98 (0.45) | 0.66 (0.01) | 77.33 (0.69) | 0.55 (0.01) | 76.33 (0.66) | 0.53 (0.01) |
| Grass | 94.00 (0.36) | 0.88 (0.01) | 94.19 (0.30) | 0.88 (0.01) | 80.69 (0.57) | 0.61 (0.01) | 87.21 (0.79) | 0.74 (0.02) |
| Soil | 88.15 (0.49) | 0.76 (0.01) | 87.58 (1.01) | 0.75 (0.02) | 75.51 (1.12) | 0.51 (0.02) | 75.80 (1.11) | 0.52 (0.02) |

- Training time per realisation: BSVM parameter tuning ~80 min; PUL ~2 min (Windows Server 2008, Intel Quad-Core 2.50 GHz, 8 GB) (p. 724).
- PUL vs BSVM gaps are small (e.g. grass scene two: BSVM OA higher, κ tied). No significance tests; the 10 draws are re-samples of one labelled pool per scene.
- The test set has 50% positives (2000/2000), not the image's class balance, so OA/κ are not map accuracies.

## 4. Stated limitations
- "One limitation of the proposed PUL is that the selected-completely-at-random assumption is difficult to satisfy and/or verify in some applications … future research is needed to study the effect of biased samples on performances of PUL and strategies to debias the training samples." (p. 724)
- "The limitation of this work is that we only test the new algorithm on a high-spatial-resolution aerial photograph data set" (p. 724).
- "We labeled training data through manual interpretation, and thus, misclassifications were inevitable" (p. 724).
- Traditional BP treating all unlabelled as negative is "trained on positive and pseudonegative data"; its accuracy "is significantly affected by how noisy its negative set is" (p. 723).

## 5. How to apply to our pipeline
- **What it is and is not.** A one-class **land-cover classification** paper on single-date RGB aerial imagery at 0.3 m (close to our 0.5 m Maxar). It is not change detection, not flood, not about cloud. It is a valid remote-sensing precedent for PU learning (as evidence 02 says).
- **Mapping to SN8 labels.** SN8 labels every annotated road/building as flooded or not flooded; that part is ordinary supervised data. The PU framing in evidence 02 is about flooded roads that are *missing or unmarked under cloud*. Li et al.'s method requires SCAR: labelled positives a random sample of all positives. Under cloud that fails, because labels go missing where cloud is, and cloud and flooding coincide (Tarpanelli, evidence 19). Then e (eq. 4), estimated on labelled = visible floods, overstates the labelling rate under cloud and the 0.5·c threshold is miscalibrated there. The paper names exactly this as its limitation (p. 724) and offers no fix.
- **Labelled-data-only rule.** PUL uses only human-made positive labels plus unlabelled pixels; it creates no pseudo-labels, so it fits the rule. The unlabelled set must be a random sample of the area (the paper used 5000 random background pixels).
- **What it says about our "cheapest fix"** (evidence 02 §2: keep cloudy missing labels out of the negatives in the training loss). That fix is not Li et al.'s method: PUL keeps unlabelled pixels in training as class s = 0 and corrects by threshold (or re-weighting, p. 724). Dropping them is a different, simpler fix that does not need SCAR. Our notes should cite Li et al. only for "PU learning has a remote-sensing precedent", not for the drop-from-negatives fix.
- **Feasibility:** cheap; any calibrated classifier (our per-road classifier, if it outputs probabilities) can be the g(x). Needs a held-out set of labelled positives to estimate c.

### Proposed bench arm: PUL threshold on clear-sky flood labels (stratified c)
1. Population: LA-East train roads (bench split). Positives (s = 1) = roads labelled flooded and visible (cloud fraction below the production cut). Unlabelled (s = 0) = all other roads, including not-flooded and clouded ones. No labels are changed; only the class definition for training.
2. Train g(x) with the current per-road classifier and features, on s, with 25% of the train roads held out (p. 719).
3. Estimate c as the mean g over held-out labelled positives (eq. 4). Also compute c separately in cloud-fraction bins (our extension, to test SCAR directly: under SCAR the binned c should be flat).
4. Call flooded if g > 0.5·c (p. 719); variant with bin-wise c.
5. Compare against production (supervised flooded vs not-flooded with cloudy roads abstaining) and against the evidence-02 "drop cloudy missing from negatives" arm, on flood calls with the bench's 21-seed flood gain and exact McNemar; report recall on clouded flooded roads separately.
6. Expected: if binned c falls with cloud fraction, SCAR is violated as predicted and PUL's single-c threshold is wrong under cloud; that result itself is the finding.

## 6. Key quotes
- "A 'selected-completely-at-random' assumption is required: The labeled examples are chosen completely randomly from all positive examples." (p. 718)
- "which shows that the desired classifier f(x) and the trained classifier g(x) differ by only a constant factor" (p. 718)
- "the correct threshold is g(x)/c = 0.5." (p. 719)
- "Traditional BP used 0.5 as the threshold, so the classifier was actually trained on positive and pseudonegative data since it assumes all of the unlabeled data to be negative. By contrast, PUL used 0.5 × c as the threshold" (p. 723)
- "A reweighting approach generates similar output to the adjusting threshold, but it requires retraining the classifier and hence, is not implemented in this study." (p. 724)
- "One limitation of the proposed PUL is that the selected-completely-at-random assumption is difficult to satisfy and/or verify in some applications." (p. 724)
