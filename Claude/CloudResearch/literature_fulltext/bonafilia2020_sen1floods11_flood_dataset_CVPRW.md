# Coder handoff: Bonafilia, Tellman, Anderson & Issenberg (2020), Sen1Floods11

- **Citation:** Bonafilia, D., Tellman, B., Anderson, T., & Issenberg, E. (2020). Sen1Floods11: A georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1. *CVPR Workshops*, 835–845. https://doi.org/10.1109/CVPRW50498.2020.00113 (Cloud to Street, company-led; Tellman also Columbia).
- **PDF:** `/Users/jusrogers/Masters/papers/bonafilia2020_sen1floods11_flood_dataset_CVPRW-summary.pdf` (page 1 = AI summary)
- **Source:** CVF open access, https://openaccess.thecvf.com/content_CVPRW_2020/papers/w11/Bonafilia_Sen1Floods11_A_Georeferenced_Dataset_to_Train_and_Test_Deep_Learning_CVPRW_2020_paper.pdf. This copy carries no proceedings page numbers (only "1" on p. 1); pages cited below as 1–11 of the PDF.
- **Validation:** PDF 1.3, 1.9 MB, 11 pages (Read tool and pdfinfo) = 835–845 (11 pages); title, 4 authors and DOI match Crossref; Discussion/Conclusion and ~61 references present. PASS.
- **Read:** all 11 pages (Fig. 1 viewed as image); references skimmed.
- **Type:** dataset + baseline paper. Prepared by Claude (AI), 2026-10-29.

## 1. Data construction (§2, pp. 3–5)
- 11 DFO flood events with Sentinel-1 and Sentinel-2 ≤ 2 days apart (5 same day, 4 within 1 day, 2 within 2 days; Cambodia and Spain added by news search). All bands at 10 m; S1 VV, VH; S2 13 bands.
- **Weak S1 labels:** 1 km grid on VH, high-variance cells → histogram → Otsu threshold, applied to a focal-mean-smoothed VH (p. 4).
- **Weak S2 labels:** NDVI threshold 0.2 and MNDWI = (B12 − B3)/(B12 + B3) threshold 0.3 (expert-defined). "Clouds were identified using a blue band reflectance threshold of less than 0.2" (as printed; presumably > 0.2 is cloud). "Cloud shadows were removed by projecting the shadows based on potential cloud heights, the solar azimuth angle, and solar zenith angle" (p. 4).
- **Chip selection:** analysts chose flood-dominated subsets; 512 × 512 non-overlapping chips; "Chips with majority cloud cover were removed from the selection process" (p. 4).
- **Hand labels (446 chips; stratified 75% with > 0.02 km² S2 water, 25% with ≤ 0.02 km²):** GUI in Earth Engine with S1 VH, two S2 false-colour composites (B12/B8/B4 and B8/B11/B4) and the S2 water map. Analysts "marked areas to remove from the water classification, add to the water classification, and marked areas they could not confidently identify as 'no data'" (p. 4). **This is an explicit abstain label.** The paper does not say cloud is coded "no data", and gives no numeric coding (no −1/0/1 in the paper). Fig. 1 (p. 2) shows the cloud patches of the S2 composite as blank (white) in the "Validation Classification", consistent with cloud → no data, but that is my reading of one figure.
- **JRC permanent water labels:** "permanent" transition class = water; never-water = not water; other water classes ignored "since we cannot be sure if these are true positive examples" (p. 3) — a second ignore-label precedent.
- Splits: Bolivia held out entirely (its S2 maps also withheld from training, S1 weak labels kept); other hand labels random 60/20/20; 4,385 weak chips for training (abstract says 4,370 automatically labelled in one place and 4,385 in another; 336 + 112 = 448 ≠ 446 — small internal inconsistencies).

## 2. Model and metrics (§3, p. 5)
- FCN with ResNet50 backbone, GroupNorm, AdamW lr 5e-4, wd 1e-2, cosine warm restarts (T0 = 1, Tmult = 2), random 256 crops, flips; normalisation means [0.6851, 0.5235], stds [0.0820, 0.1102] (VV, VH).
- **Mean IoU per chip (equal weight)**, plus omission and commission rates, separately for permanent (PW), flood (FW) and all water (AW). Ignored/no-data pixels are presumably excluded (not stated explicitly).

## 3. Numbers (Tables 1–4, pp. 5–6)
| Model | Test 10 events PW / FW / AW IoU | Bolivia PW / FW / AW IoU |
|---|---|---|
| S1 weak | .2872 / .2422 / .3092 | .2506 / .3296 / .3871 |
| S2 weak | .3818 / **.3389** / **.4084** | .1946 / .2738 / .3160 |
| Hand-labelled | .2570 / .2421 / .3125 | .2300 / .2905 / .3524 |
| Permanent water (JRC) | .3391 / .1693 / .2452 | .2881 / .2684 / .3422 |
| Otsu VH | **.4571** / .2850 / .3591 | .2859 / .3239 / .3862 |
- Otsu flood omission on Bolivia 0.3756 (high OA from dry land dominance, p. 5).

## 4. Stated limitations
- Small (11 events); no urban floods in validation ("Sentinel-1 algorithms often struggle to map floods in urban areas", p. 7). Cloud shadows confused for water (Fig. 5, p. 7). Weak S2 > hand labels likely due to quantity, not quality (p. 6).

## 5. Licence / usage
- Dataset and code at https://github.com/cloudtostreet/Sen1Floods11 (abstract). **No licence is stated in the paper.** Bucket name (`gs://sen1floods11`) in evidence 02 is not in the paper.

## 6. How to apply to our pipeline
- **Abstain label precedent for scoring:** a published flood dataset where annotators mark "areas they could not confidently identify" as no data. Use it, together with WorldFloods v2's bright-cloud mask, to justify excluding our "cannot assess" roads from accuracy and reporting coverage separately (`sn8_refhaze.road_handling`, `sn8_cloudsym.either_date_handling`).
- **Ignore-label in training:** JRC non-permanent water "treated as pixels to ignore" — the same move as keeping cloudy SN8 "not flooded" roads out of the negatives (ignore index in the loss).
- **Shadow projection** (cloud height + sun geometry) is their shadow rule; at 0.5 m with tiles smaller than cloud-shadow offsets this needs the cloud in view (see Fmask/SPARCS); for us a two-date shadow test is more realistic.
- **Protocol:** event-level hold-out (Bolivia) and per-chip mean IoU + omission/commission are a standard we can mirror at tile-group level.
- **Feasibility:** labelling/scoring rules transfer; models (S1 SAR, S2 multispectral, 10 m) do not.

## 7. Key quotes
- "marked areas they could not confidently identify as 'no data'" (p. 4)
- "Chips with majority cloud cover were removed from the selection process." (p. 4)
- "Cloud shadows have similar spectral signatures as floods, and thus are crucial to mask for accurate optical flood mapping." (p. 4)
- "hand labeled data remains essential to validate and compare different models" (p. 6)
