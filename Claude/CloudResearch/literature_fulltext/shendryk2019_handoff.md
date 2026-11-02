# Coder handoff: Shendryk, Rist, Ticehurst & Thorburn (2019), Deep learning for multi-modal classification of cloud, shadow and land cover scenes in PlanetScope and Sentinel-2 imagery

- **Citation:** Shendryk, Y., Rist, Y., Ticehurst, C., & Thorburn, P. (2019). *ISPRS Journal of Photogrammetry and Remote Sensing* 157, 124–136. https://doi.org/10.1016/j.isprsjprs.2019.08.018
- **PDF:** `/Users/jusrogers/Masters/papers/shendryk2019-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 15.36 MB; 13 pages (Read tool and pdfinfo) = published range 124–136; page-1 title, authors (Shendryk, Rist, Ticehurst, Thorburn; CSIRO), journal 157 (2019) 124–136 and DOI 10.1016/j.isprsjprs.2019.08.018 match the citation; Conclusions (p. 135) and References (pp. 135–136) present. Open access, CC BY-NC-ND 4.0 (p. 124 footer). PASS. (`file` metadata says 1 page; ignored.)
- **Read:** pp. 124–136 in full (Read tool page images, numbers cross-checked against `pdftotext -layout`), including Tables 1–7 and Figs. 1–8.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

**Bottom line for us:** this is **scene-level (chip) classification, not pixel-level** (abstract, p. 124). One label set per
128 × 128 px chip. Inputs are always 6 layers (R, G, B, NIR, NDVI, GNDVI); **no RGB-only result exists**. Haze was not
learned (ensemble per-label F2 0.00). Cloudy/clear chip labels work well (F2 ≈ 0.90); shadow is weak (shaded F2 0.45).

## 1. Algorithm, step by step
1. **Data and chips** (§2.1, pp. 126–127).
   - A-PS: Kaggle "Understanding the Amazon from Space" PlanetScope set, 40,479 chips of 256 × 256 px (800 × 800 m), 17 original labels; rare labels and 'road' dropped, 'cultivation' merged into 'agriculture'. **Left uncalibrated, in DN** (p. 127). No shade labels; more haze than the Australian sets.
   - T-PS / T-S2: Wet Tropics of Australia, 1 Dec 2016 – 1 Nov 2017. 246 PlanetScope orthorectified tiles and 169 Sentinel-2 Level-1C tiles. Sentinel-2 trimmed to RGB + NIR and **resampled to 3.125 m** to match PlanetScope (GSD 3.125 m). Gridded into 128 × 128 px chips (400 × 400 m); random sample of 2.5 % (PS) and 0.5 % (S2) of chips per time step → **4943 (T-PS) and 4993 (T-S2)** chips. Converted to TOA reflectance (p. 127). Labelled manually for this study.
   - Labels (Table 1, p. 127), 12 in all: cloud group {clear, partly cloudy, cloudy, haze} (mutually exclusive, one per chip), shade group {unshaded, partly shaded, shaded} (one per chip), land cover {forest, agriculture, water, bare ground, habitation} (multi-label).
   - Split (p. 126–127): fixed train/test; test needs ≥ 75 chips per label; 20 % test. Haze: n = 115 in T-PS + T-S2; all 22 T-PS haze chips went to test and all but 13 T-S2 haze chips went to test, so **only 13 haze training chips** (p. 127, p. 133).
2. **Extra bands** (p. 127): eq. (1) `NDVI = (Red − NIR)/(Red + NIR)`, eq. (2) `GNDVI = (Green − NIR)/(Green + NIR)` — *as printed; the sign is the reverse of the usual NDVI. Fig. 7 (p. 133) shows positive NDVI ≈ 0.6–0.8 over sugarcane, so the code almost certainly used the standard (NIR − Red)/(NIR + Red). Use the standard form.* Chip tensor 256 × 256 × 6 (A-PS) or 128 × 128 × 6.
3. **Pre-processing** (p. 127, Fig. 1 p. 127): standardise each chip to zero mean, unit SD; augmentation by random 90° rotations and flips; for DenseNet201 and ResNet50 resample chips to 224 × 224 (p. 128).
4. **Networks** (§2.2, p. 128, Fig. 3): DenseNet201, ResNet50, and "VGG10" (VGG13-style blocks with one conv block and one dense layer removed). VGG10 shapes from Fig. 3: 128×128×6 → 128×128×32 → 125×125×32 → [max-pool] 31×31×32 → 31×31×64 → 30×30×64 → [pool] 15×15×64 → 15×15×128 → 14×14×128 → [pool] 7×7×128 → 7×7×256 → 6×6×256 → [pool] 3×3×256 → FC 512 → 12 outputs. ReLU everywhere; stride 1 for every conv layer. Each architecture is **trained three times**: a softmax model for the cloud group, a softmax model for the shade group, a sigmoid model for land cover; the three together act as one 12-label classifier.
5. **Training** (p. 128, Fig. 1): TensorFlow; Adam, batch size 128; categorical cross-entropy (softmax) / binary cross-entropy (sigmoid); "exp. decay schedule" (Fig. 1; no learning-rate values or epoch counts given). Pre-trained on A-PS-train, then fine-tuned on T-PS / T-S2 (p. 128–129). Hardware: 4 × NVIDIA Tesla P100 16 GB, 256 GB RAM (p. 127).
6. **Ensemble** (§2.3, p. 128): per label l, ridge regression eq. (5) `min_u ‖Ẑ_l u_l − y_l‖² + ‖u_l‖²`, l = 1…12, where Ẑ_l is N × 3 (probabilities from the three architectures); weight penalty = 1. Ensemble score = Ẑ_l u_l*.
7. **Per-label threshold** (p. 128): random search maximising F2. Proposal ~ Normal(current best, σ = σ0 · 10^(−α t)), σ0 = 0.25, α = 0.001, t = iteration; accept if F2 improves; 1000 iterations.
8. **Metrics** (p. 128): eq. (3) `OA = (TP+TN)/(TP+TN+FP+FN)`; eq. (4) `F2 = 5TP/(5TP + 4FN + FP)` (recall-weighted). Per-sample (averaged over chips) and per-label.
9. **Benchmark against pixel masks** (§2.5, p. 129, Table 3): Sen2Cor (SNAP) and MACCS (Sen2Agri) pixel masks aggregated to chips: cloudy > 90 % cloud pixels, partly cloudy 10–90 %, clear < 10 %; same for shaded / partly shaded / unshaded. Sen2Cor cloud = medium + high probability + thin cirrus. "modifying this classification rule by ± 5% did not change the performance scores by a significant margin" (p. 129). The authors say these rules match their manual labelling rule (p. 129).

## 2. Inputs, outputs, data needs
- **Input:** a 128 × 128 chip (400 × 400 m at 3.125 m), 6 layers: R, G, B, NIR, NDVI, GNDVI; TOA reflectance (T-sets) or DN (A-PS). Standardised per chip.
- **Output:** 12 scores → thresholds → one cloud label, one shade label, any number of land-cover labels per chip. No pixel mask.
- **Data needs:** ~4000 labelled training chips sufficed for the T-sets ("as few as ~4000 pre-labeled training scenes", pp. 131 and 133); a ~40,000-chip pre-training set (A-PS). The paper states "overly deep architectures (> 50 layers) require more training data (> 10,000 scenes)" (p. 133).
- **Availability:** the paper gives **no download link and no data licence** for T-PS / T-S2 (searched every page). A-PS is the public Kaggle competition set (ref. Kaggle 2017a, p. 135). The article is CC BY-NC-ND 4.0. Our note's Mendeley link (`data.mendeley.com/datasets/6gdybpjnwh/1`) comes from OpenSICDR, not from this paper; its licence/content is unverified (not checked; no web access in this pass).

## 3. Quantitative results
**Table 4 (p. 130), ensemble generalisation, per-sample F2 (OA):**
| # | Pre-train | Train | Test | F2 | OA |
|---|---|---|---|---|---|
| 1 | – | A-PS-train | A-PS-test | 0.90 | 0.90 |
| 2 | – | A-PS-train | T-PS | 0.72 | 0.74 |
| 3 | – | A-PS-train | T-S2 | 0.69 | 0.77 |
| 4 | A-PS-train | T-PS-train | T-PS-test | 0.83 | 0.80 |
| 5 | A-PS-train | T-PS-train | T-S2 | 0.76 | 0.76 |
| 6 | A-PS-train | T-S2-train | T-S2-test | 0.83 | 0.84 |
| 7 | A-PS-train | T-S2-train | T-PS | 0.76 | 0.76 |
| 8 | A-PS-train | T-S2-train + T-PS-train | T-S2-test + T-PS-test | 0.82 | 0.79 |
(#1–3 have no shade labels.)

**Table 5 (p. 130), experiment #8, per-label F2 (OA):**
| Label | DenseNet201 | ResNet50 | VGG10 | Ensemble |
|---|---|---|---|---|
| Clear | 0.88 (0.74) | 0.87 (0.72) | 0.92 (0.85) | 0.91 (0.82) |
| Haze | 0.33 (0.79) | 0.42 (0.87) | 0.30 (0.45) | 0.00 (0.95) |
| Partly cloudy | 0.73 (0.64) | 0.73 (0.64) | 0.69 (0.62) | 0.73 (0.67) |
| Cloudy | 0.91 (0.90) | 0.89 (0.90) | 0.90 (0.92) | 0.90 (0.91) |
| Unshaded | 0.93 (0.76) | 0.93 (0.75) | 0.93 (0.75) | 0.93 (0.76) |
| Partly shaded | 0.67 (0.68) | 0.62 (0.60) | 0.68 (0.68) | 0.69 (0.69) |
| Shaded | 0.50 (0.70) | 0.47 (0.69) | 0.57 (0.75) | 0.45 (0.90) |
| Agriculture | 0.88 (0.70) | 0.87 (0.69) | 0.88 (0.75) | 0.88 (0.71) |
| Bare ground | 0.69 (0.68) | 0.71 (0.66) | 0.70 (0.57) | 0.70 (0.72) |
| Habitation | 0.69 (0.78) | 0.72 (0.78) | 0.77 (0.82) | 0.76 (0.83) |
| Forest | 0.85 (0.64) | 0.83 (0.66) | 0.85 (0.67) | 0.84 (0.65) |
| Water | 0.72 (0.92) | 0.71 (0.93) | 0.66 (0.89) | 0.72 (0.93) |
| Per-sample | 0.81 (0.74) | 0.80 (0.74) | 0.81 (0.73) | 0.82 (0.80) |

Note the haze ensemble OA 0.95 with F2 0.00: the ensemble simply never predicts haze; the ridge weights for haze are 0.00 / 0.02 / 0.00 (Table 6, p. 130). Text: haze "per-label F2 of < 0.42", shaded "< 0.57" (p. 129).

**Table 6 (p. 130), ridge weights DenseNet201 / ResNet50 / VGG10:** clear 0.01/0.59/1.30; haze 0.00/0.02/0.00; partly cloudy 0.35/0.30/0.91; cloudy 0.44/0.16/0.46; unshaded 0.24/0.27/0.67; partly shaded 0.21/0.24/1.04; shaded 0.11/0.07/0.69; agriculture 0.23/0.54/0.45; bare ground 0.25/0.54/0.18; habitation 0.34/0.57/0.91; forest 0.34/0.54/0.25; water 0.33/0.52/0.30.

**Table 7 (p. 130), benchmark on T-S2 (4993 chips), CNN trained on T-PS-train (3943 chips), per-label F2 (OA):**
| Label | Sen2Cor | MACCS | CNN ensemble |
|---|---|---|---|
| Clear | 0.92 (0.87) | 0.83 (0.84) | 0.92 (0.82) |
| Partly cloudy | 0.60 (0.83) | 0.29 (0.73) | 0.68 (0.79) |
| Cloudy | 0.82 (0.91) | 0.81 (0.81) | 0.74 (0.93) |
| Unshaded | 0.94 (0.78) | 0.85 (0.78) | 0.91 (0.79) |
| Partly shaded | 0.15 (0.78) | 0.27 (0.75) | 0.40 (0.73) |
| Shaded | 0.08 (0.98) | 0.44 (0.89) | 0.34 (0.76) |
| Per-sample | 0.79 (0.86) | 0.70 (0.80) | 0.79 (0.80) |
Haze excluded from the benchmark (p. 130). No significance tests anywhere in the paper.

**Other numbers:** single models trained and tested on A-PS (~40,000 chips): per-sample F2 (OA) 0.89 (0.88) DenseNet201, 0.88 (0.87) ResNet50, 0.86 (0.83) VGG10 (p. 133). Ensemble gain over single models 0.01–0.07 F2 (p. 133). MACCS dilates masks by 480 m (p. 130). Fig. 8 (p. 134) shows the model applied to 96 × 96 px (300 × 300 m) chips, with no labels to score it (p. 135).

## 4. Stated limitations
- Scene level loses location: "there is a substantial loss of information in image scenes labeled as, for example, 'partly cloudy' or 'partly shaded' if these masks were to be used for masking cloudy and shaded areas" (p. 130).
- Haze not learned (13 training chips); suggested fixes: more haze chips, haze removal (ATCOR, dark channel) before labelling, more augmentation (p. 133).
- Fully shaded chips lack context, hence low shaded F2 (p. 129).
- Cross-dataset loss partly from different chip scale (A-PS chips rescaled to a quarter of the area) and inconsistent label definitions ('agriculture', 'forest') between A-PS and the T-sets (p. 133); scale mattered more than GSD (p. 133).
- Comparison with pixel methods is approximate: aggregation of pixel masks, MACCS dilation, and different cloud class definitions (p. 134).
- Ensemble via ridge fails when a label has too few true positives (p. 133). Hyperparameters were not tuned (p. 133). Scene-to-pixel translation left to future work (p. 135).
- Claimed scope: "applicable to any high-resolution (< 10 m) satellite imagery containing RGB + NIR bands" (p. 134) — i.e. NIR is assumed.

## 5. How to apply to our pipeline
- **Fit:** our tiles are Maxar RGB uint8 at ~0.5 m, often grey, no NIR, two dates. The paper's models need NIR (4 of 6 input layers depend on it) and 3 m data; **the trained weights are not released** and there is no RGB-only ablation, so nothing transfers directly. A 128 × 128 chip at 0.5 m is 64 × 64 m, far smaller than the paper's 400 m; the paper found chip scale mattered more than GSD (p. 133), so a different scale is a real risk.
- **What transfers is the design, not the model:** (a) a 3-way chip label per date — clear (< 10 % cloud), partly cloudy (10–90 %), cloudy (> 90 %) (Table 3, p. 129) — as a tile-level gate: clear → run as is, partly cloudy → pixel masking, cloudy → **abstain**; this fits our universality rule ("quality layer abstains"); (b) a small shallow net (VGG10) beat deeper ones with ~4000 chips (p. 133); (c) per-label F2 threshold tuning by random search (p. 128); (d) the 10/90 rule is a published way to derive chip labels from pixel masks, so chip labels can be built from published HRC_WHU masks without hand labelling (a deterministic aggregation of unmodified labels — confirm this counts as "published labels, unmodified" under the labelled-data rule).
- **What does not transfer:** haze (F2 0.00) and shadow (shaded 0.45, partly shaded 0.69 / 0.40 cross-sensor). The haze problem in our post-storm tiles is exactly what this paper failed at; do not expect a chip classifier to flag haze without many haze examples. HRC_WHU has no shadow labels, so only the cloud group can be tested.
- **Tie to bench:** D1b HOT already gives a per-pixel cloud score with F1 +0.011 on HRC_WHU; the cheapest gate is to aggregate that map with the 10/90 rule, no CNN needed. Our abstain paths so far come from fit failures (N2/N4/Lin abstentions), not from a cloud-cover estimate; a chip gate would give an independent, explicit abstain reason.

### Proposed bench arm: G-scene (chip-level cloud gate, 10/90 rule)
1. Data: HRC_WHU train folds (published masks, unmodified) for fitting; HRC_WHU test fold for scoring. Cut 0.5–15 m images into 128 × 128 px chips (also try 256 × 256 as the paper's A-PS scale).
2. Reference chip labels from the masks with Table 3's rule: clear < 10 % cloud pixels, partly cloudy 10–90 %, cloudy > 90 %.
3. Arm G-scene-a (no learning): run D1b HOT pixel cloud map, aggregate the predicted cloud fraction per chip with the same 10/90 cuts.
4. Arm G-scene-b (learned): VGG10 as in Fig. 3 but 3-channel RGB (and a 1-channel grey variant), softmax over the 3 cloud labels, Adam, batch 128, chip standardisation, 90° rotations + flips; threshold per label by the random search of p. 128 (σ0 = 0.25, α = 0.001, 1000 iterations) on a validation fold only.
5. Score: per-label F2 and OA (eqs. 3–4) and per-sample F2 on the HRC_WHU test fold; compare a-vs-b with McNemar on chip-level correct/incorrect; report the paper's 3 m numbers (clear 0.91, partly cloudy 0.73, cloudy 0.90, Table 5) only as context, not as a target.
6. Then, gated pipeline on SN8 dev tiles (spent data only): cloudy → abstain, partly cloudy → current masking, clear → as is; compare flood calls against C0 (ungated) with the existing flood screen and report how many tiles abstain. Show chip-gate overlays on images with error crops.
- Compared against: C0 (no gate) and D1b HOT pixel map; success = chip gate reaches ≥ the pixel-aggregate on F2 and the gated pipeline does not lose flood calls on clear tiles.

## 6. Key quotes
- "Multi-label classification at the scene level (a.k.a. image indexing), as opposed to the pixel level, allows for faster performance, higher accuracy (although at the cost of detail) and higher generalizability." (abstract, p. 124)
- "The T-PS and T-S2 datasets were generated by splitting satellite imagery with a grid of 128 × 128 pixels (i.e. 400 × 400 m) into image scenes" (p. 126)
- "Due to the low number of training scenes (n = 13) with the 'haze' label in the T-PS + T-S2 dataset, we expected a low accuracy for detecting this class." (p. 127)
- "Finally, the A-PS dataset was left uncalibrated in digital number (DN) format, as no metadata necessary for radiometric calibration were available." (p. 127)
- "For example, if < 10% of pixels within a scene were classified as 'cloudy', such scene was reclassified to be 'clear'." (p. 129)
- "The weighting towards a shallower model (i.e. VGG10) might suggest that the training set was too small for training deeper networks." (p. 129)
- "Our ensemble CNN model was ineffective in identifying image scenes with 'haze' labels due to a small training size (n = 13)." (p. 133)
- "Moreover, our CNN models are expected to be applicable to any high-resolution (< 10 m) satellite imagery containing RGB + NIR bands" (p. 134)
