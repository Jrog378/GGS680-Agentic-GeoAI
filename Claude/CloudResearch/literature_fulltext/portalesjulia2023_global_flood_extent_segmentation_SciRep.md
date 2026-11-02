# Coder handoff: Portalés-Julià, Mateo-García, Purcell & Gómez-Chova (2023), Global flood extent segmentation in optical satellite images (WorldFloods v2)

- **Citation:** Portalés-Julià, E., Mateo-García, G., Purcell, C., & Gómez-Chova, L. (2023). *Scientific Reports* 13, 20316. https://doi.org/10.1038/s41598-023-47595-7
- **PDF:** `/Users/jusrogers/Masters/papers/portalesjulia2023_global_flood_extent_segmentation_SciRep-summary.pdf` (page 1 = AI summary)
- **Source:** publisher open-access PDF, https://www.nature.com/articles/s41598-023-47595-7.pdf (article CC BY 4.0).
- **Validation:** PDF 1.4, 5.3 MB, 14 pages (Read tool and pdfinfo); title, 4 authors and DOI match Crossref; Discussion, Methods, 53 references present; article number 20316, pages 1–14. PASS.
- **Read:** pp. 1–14 in full (references pp. 12–13 skimmed; Figs. 5 and 6 read as images). Supplementary Information (training details, band-combination figures, BR-threshold PR curves) not downloaded.
- **Type:** dataset + method paper. Prepared by Claude (AI), 2026-10-29.

## 1. What the paper does
- Extends WorldFloods (v1, Mateo-Garcia 2021) to events up to 2023, drops "low-quality flood maps that were mostly covered by clouds or presented significant labeling errors", hand-curates "more than 200 maps", builds new hand-picked validation and test splits (p. 6). Result: 13-band Sentinel-2 L1C patches from "more than 180 different flood events", ≈ 75,000 tiles of 256 × 256 (p. 6). Training set: 475 flood maps, 119 events, ≈ 65,000 patches (p. 11).
- **Label design (p. 6):** "Instead of one layer containing three, mutually exclusive classes (land, water, and cloud), we generated two independent binary reference masks, one for the clear/cloud problem and another for the land/water problem." Water is labelled under semitransparent cloud. How the v2 cloud reference itself was produced is **not stated in the main text**; it cites KappaMask and CloudSEN12 (refs 44, 45) as "newly developed cloud detection algorithms" the split lets them use.
- Leakage control (p. 11): all flood maps of an event with any map in val/test are excluded from training (EMSR342 example).

## 2. Model and the thin/thick rule (Fig. 5, p. 6; p. 7)
- U-Net ("Unet++" in the Fig. 5 box), two sigmoid outputs: P(cloud), P(water). Loss = BCE, weights 0.8 water / 0.2 cloud, water pixels weighted by inverse class frequency; lr 10⁻⁴, reduce after 2 epochs, early stop 4 epochs; flips + 90° rotations (pp. 11–12).
- Brightness: `BR = sqrt(B2² + B3² + B4²)` (visible TOA reflectance, Fig. 5).
- Prediction rule (Fig. 5):
```
'cloud'  if P(cloud) > th_cloud and BR > th_BR
'water'  if not 'cloud' and P(water) > th_water
'land'   otherwise
```
- Defaults: th_cloud = th_water = 0.5; **th_BR "experimentally" 0.35** (p. 7), but the paper later says "**0.3** is a reasonable brightness threshold to fully exploit the available observations without sacrificing precision" (p. 8) and uses 0.3 for scoring and the thin-cloud class. Inconsistent within the paper; 0.3 is the recommended value. th_BR = 0 → cloud mask = the network's cloud output alone (p. 9).
- Best-IoU water threshold on the evaluation set is **0.7**, not 0.5 (p. 7).

## 3. How cloud is excluded from scoring (Methods, p. 12)
- "We compute these metrics for each flood map in the test and validation dataset masking invalid pixels and bright clouds (pixels that are labeled as clouds and have a brightness above 0.3), since the surface information in this case is totally blocked."
- So thin cloud (labelled cloud, BR ≤ 0.3) **stays in** the scored pixels; water under it is expected. A "Thin cloud" stratum = cloud label ∧ BR ≤ 0.3 (p. 7).
- Metrics per flood map, then mean across floods. Eq. 3 is printed as IoU = TP/(TP + FP + **TN**), a typo for FN (p. 12); use the standard definition.

## 4. Numbers we could compare to (Fig. 6a, p. 7; flood water; mean over test floods)
| Model | Recall | Precision | IoU |
|---|---|---|---|
| MNDWI (B11, B3; threshold 0) | 55.36 | 66.71 | 40.95 |
| U-Net multiclass (v1) | 79.80 | 54.02 | 48.27 |
| U-Net multioutput (13 bands) | 75.71 ± 2.16 | 63.45 ± 9.57 | 52.67 ± 6.34 |
| U-Net multioutput S2-to-L8 (RGB+NIR+SWIR) | 75.48 ± 1.49 | 70.81 ± 3.07 | **57.89 ± 1.43** |
| U-Net multioutput RGBNIR | 72.42 ± 3.14 | 60.18 ± 3.12 | 48.57 ± 1.27 |
- Thin clouds are 2.0% of the test set (Fig. 6c) and 4.54% of all WorldFloods pixels; flood water 3.36% (p. 8). Built-up (1.6% of test) is among the worst land-cover strata (Fig. 6c, IoU ≈ 0.2).
- Fig. 9: on a thin-cloud-rich subset, multioutput IoU is "significantly higher" than multiclass (no significance test reported; per-event bars only).
- These are 10 m water-pixel IoUs, not road-level flood scores; use them as context, not as a target.

## 5. Stated limitations
- Accuracy is lower in thin-cloud scenes: "if the image has many thin clouds, these scenes shall be validated by human experts before utilizing them to produce the final flood extent product, regardless of the selected method" (p. 8).
- Raising th_BR lowers precision ("more (thick) cloudy observations ... treated as thin clouds", p. 8).
- Cloud shadows are "challenging" (p. 8); built-up and forest worst (p. 8); RGBNIR-only models "slightly worse", SWIR "crucial" (p. 11). Models also detect flood traces (mud) from temporal misalignment of labels (p. 10).

## 6. Licence / usage
- Article: CC BY 4.0 (p. 14). Data: "WorldFloods extended flood maps and Pakistan flood maps can be found at Zenodo (https://zenodo.org/record/8153514)" (p. 12); code ml4floods on GitHub/PyPI. **The paper does not state a dataset licence**; our evidence-02 note of CC-BY-NC-4.0 comes from the Hugging Face card, not the paper.

## 7. How to apply to our pipeline
- **Two-part abstain rule (sn8_cloudspot + sn8_clouds + sn8_refhaze/sn8_cloudsym):** copy the structure "cannot assess = cloud-like AND bright"; "cloud-like but not bright = thin, correct and assess". Concretely: P(cloud) from `CloudSpotter` (or the dark-rise gate in `sn8_cloudsym`) ∧ grey brightness above a threshold → cannot assess; otherwise pass to the two-date de-hazing. Their BR is a reflectance norm; for us use grey level on the after tile, and pick the threshold from HRC_WHU / our labelled tiles with a PR sweep, not 0.3. Report a PR curve over the brightness threshold, as they do (Supplementary Fig. 5).
- **Scoring protocol (road tables in sn8_refhaze.road_handling / sn8_cloudsym.either_date_handling):** score with "bright cloud" and invalid removed, keep thin-cloud roads in, and report a separate thin-cloud stratum (their Fig. 6c). Report per-event (per-tile-group) means as they do, plus our paired tests.
- **Training labels:** their separate cloud and water targets support keeping cloudy "missing" SN8 labels out of the negatives in the loss; the paper does this for cloud via separate masks, not by a PU loss.
- **Threshold choice:** their best water threshold (0.7) differs from default (0.5); tune our flood threshold on development tiles only.
- **Feasibility:** the label/rule structure is fully feasible on RGB uint8 0.5 m with one before date. The learned model is not usable (Sentinel-2 13/6/4 bands, 10–30 m; SWIR matters).

## 8. Key quotes
- "optimally distinguish between thin semitransparent clouds, where the surface can still be observed, and opaque thick ones" (p. 2)
- "The brightness threshold is included to distinguish between bright clouds were we assume surface cannot be observed and thin clouds." (p. 7)
- "masking invalid pixels and bright clouds (pixels that are labeled as clouds and have a brightness above 0.3), since the surface information in this case is totally blocked" (p. 12)
- "if the image has many thin clouds, these scenes shall be validated by human experts" (p. 8)
