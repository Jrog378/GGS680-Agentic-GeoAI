# Coder handoff: Domnich et al. (2021), KappaMask: AI-Based Cloudmask Processor for Sentinel-2

- **Citation:** Domnich, M., Sünter, I., Trofimov, H., Wold, O., Harun, F., Kostiukhin, A., Järveoja, M., Veske, M., Tamm, T., Voormansik, K., Olesk, A., Boccia, V., Longépé, N., & Cadau, E. G. (2021). *Remote Sensing* 13(20), 4100. https://doi.org/10.3390/rs13204100 (KappaZeta Ltd + ESA; company paper, ESA contract 4000132124/20/I-DT).
- **PDF:** `/Users/jusrogers/Masters/papers/domnich2021_kappamask_sentinel2_cloudmask_RemoteSens-summary.pdf` (page 1 = AI summary)
- **Source:** MDPI's own file server, https://mdpi-res.com/d_attachment/remotesensing/remotesensing-13-04100/article_deploy/remotesensing-13-04100-v2.pdf (found by web search; the www.mdpi.com PDF link returns "Access Denied" to scripts and was not bypassed). Article CC BY 4.0.
- **Validation:** PDF 1.7, 11.1 MB; Read tool and pdfinfo: 22 pages ("x of 22" footers; `file` wrongly said 10). Title, 14 authors, DOI match Crossref. Conclusions, Data Availability, references present. PASS. Note: the PDF's text layer includes hidden draft text inside embedded figures ("x FOR PEER REVIEW"), so pdftotext output is garbled; the rendered pages are clean and were read as images.
- **Read:** pp. 1–18 in full (pp. 4–18 from page images); appendix maps pp. 18–20 glanced; references pp. 20–22 skimmed.
- **Type:** method + dataset (KappaSet) paper. Prepared by Claude (AI), 2026-10-29.

## 1. Labelling rules (§2.2, p. 6)
Classes used in CVAT and Segments.ai:
- **0 MISSING:** "missing or invalid pixels"
- **1 CLEAR:** "pixels without clouds or cloud shadows"
- **2 CLOUD SHADOW:** "pixels with cloud shadows"
- **3 SEMI TRANSPARENT CLOUD:** "pixels with thin clouds through which the land is visible"
- **4 CLOUD:** "pixels with cloud"
- **5 UNDEFINED:** "pixels that the labeller is not sure which class they belong to". "Undefined class is used where the labeller is either not certain what is in the image or when the class borders are not clear. The UNDEFINED class is excluded from the model training and the predictor assigns the class with the highest confidence from the other five classes."
- Tools: CVAT polygons (6 Estonian products, all 484 sub-tiles each = 2,821 extra sub-tiles, training only); Segments.ai brush with model pre-labels, "all sub-tiles were still manually corrected" (~1,500 sub-tiles from 150 products); "peer-reviewed by labellers" (p. 6). Mixed tools argued to reduce labelling-style bias.
- Mapping to other products (Table 1, p. 6): CMIX 3 semi-transparent ↔ KappaMask 3; Sen2Cor 10 thin cirrus → 3; Sen2Cor 8/9 cloud medium/high → 4; Sen2Cor 7 unclassified → 5 undefined; Sen2Cor 0/1 no data/saturated → 0 missing.

## 2. Data and training (§2, pp. 3–8)
- Pre-train on Sentinel-2 Cloud Mask Catalogue (Francis et al.; 513 subscenes 1022 × 1022 at 20 m, IRIS semi-automatic labels) resampled to 10 m; fine-tune on KappaZeta set: 150 products × 10 sub-tiles of 512 × 512 at 10 m, Northern Europe, April–October, ten stratus/cumulus/cirrus products per month; sub-tiles chosen by **active learning: a human picked sub-tiles where the overlaid prediction looked most wrong** (p. 5).
- Inputs: L2A 12 bands + AOT + WVP (text says 13 features, Fig. 11 shows 14); L1C 13 bands incl. B10 cirrus. Resampled to 10 m (Blackman-windowed sinc). Min–max normalised.
- 5-level U-Net, Dice loss (cross-entropy kept improving F1 after overfitting), Adam, LR reduction and early stopping; train/val random 80/20; inference on 512 tiles with 32 px overlap (pp. 7–8). Depth/filter sweep in Table 10 (5 levels, 64 filters ≈ 84% val Dice; U-Net++ 75.9%).
- **Test set:** 15 separate products (Apr–Aug, one stratus, cumulus, cirrus per month), and from each "the 10 most complicated sub-tiles ... for which the model gave the most errors" (p. 7). Deliberately hard; selected with the pre-trained model.

## 3. Numbers (Tables 2–9, pp. 10–14)
- Dice (L2A / L1C / Sen2Cor / Fmask / MAJA): clear 82/75/72/75/56; shadow 72/69/52/49/–; semi-transparent 78/75/49/–/–; cloud 86/84/62/60/46; all 80/76/59/61/51.
- Precision all classes: 81/78/71/54/50; recall all: 79/74/58/65/58; OA all: 91/88/82/81/71.
- Clear vs cloud only (Tables 6–9): Dice L2A 84, L1C 80, s2cloudless 63, DL_L8S2_UV 62.
- Confusion (Fig. 8, L2A): true semi-transparent → clear 0.16, → cloud 0.10; true shadow → clear 0.19; Fmask sends 77% of semi-transparent to cloud. "16% out of 37% false negative errors in KappaMask L2A output appear with semi-transparent clouds. However, semi-transparent clouds are often very thin and their borders often not visible with human eye, making them difficult to delineate." (p. 11)
- Timing (Table 11): full L1C product 3:57 GPU, 10:08 CPU; Fmask 6:32; s2cloudless 17:34.
- No confidence intervals or significance tests.

## 4. How cloud/invalid are scored
- Missing class removed from confusion matrices "to make matrices easier to read" (Fig. 8). Undefined pixels are excluded from training; how they are treated in test scoring is not stated.

## 5. Stated limitations
- "The model has not been tested outside of this scope" (Northern Europe, April–October; p. 16). L1C weaker than L2A. Future: global, winter.

## 6. Licence / usage
- Article CC BY 4.0 (p. 1). Data: "publicly available from https://zenodo.org/record/5095024" (p. 17). Predictor code open source (ref. 20). **No dataset licence stated in the paper.**

## 7. How to apply to our pipeline
- **Add an "undefined / unsure" label and ignore it in the loss (sn8_cloudspot training on HRC_WHU, any hand-checked SN8 cloud tiles):** when we hand-check cloud on SN8 tiles, use KappaMask's 6-class scheme (missing, clear, shadow, thin, cloud, undefined), and use `ignore_index` for undefined in the random-forest / probe training (drop those pixels from fit and from scoring, report their share).
- **Output classes for our gate:** map our outputs to their scheme so they line up with CMIX: thick → 4, thin → 3, shadow → 2, clear → 1, no data → 0.
- **Reporting:** per-class Dice, precision, recall, OA plus a confusion matrix, with thin-cloud → clear leakage called out. Their test-set bias (hardest tiles) means their numbers are a pessimistic reference, not a target.
- **Shadow:** their shadow recall is the weakest class (≤ 64%) even with 13 bands; expect worse from grey-only cues.
- **Feasibility:** label scheme and protocol fully usable; model needs Sentinel-2 bands (B10 cirrus helps thin cloud), not usable on RGB 0.5 m.

## 8. Key quotes
- "3—SEMI TRANSPARENT CLOUD: pixels with thin clouds through which the land is visible" (p. 6)
- "The UNDEFINED class is excluded from the model training" (p. 6)
- "semi-transparent clouds are often very thin and their borders often not visible with human eye, making them difficult to delineate" (p. 11)
