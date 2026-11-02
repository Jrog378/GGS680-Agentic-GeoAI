# Coder handoff: Götz, Wessel, Çayoğlu, Jahani, Debus, Cermak & Streit (2025), ordinal METAR cloud-cover classification in Sentinel-2

- **Citation:** Götz, M., Wessel, E., Çayoğlu, U., Jahani, B., Debus, C., Cermak, J., & Streit, A. (2025). Ordinal
  METAR cloud cover classification in Sentinel-2 satellite data. *IEEE Journal of Selected Topics in Applied Earth
  Observations and Remote Sensing* 18, 10674–10683. https://doi.org/10.1109/JSTARS.2025.3557931
- **Copy read:** accepted author version (CC BY 4.0) from KITopen, https://publikationen.bibliothek.kit.edu/1000180808/158669201.
  12 pages (two-column IEEE layout with header "author's version which has not been fully edited"); the typeset
  article is 10 pages (10674–10683). Page numbers below are the **manuscript's**.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/gotz2025_ordinal_metar_cloud_cover_sentinel2_JSTARS-summary.pdf`
- **Validation:** real PDF (5.3 MB), 12 pages by pdfinfo and Read (`file` said 6 — unreliable); title and the seven
  authors match Crossref (vol. 18, pp. 10674–10683); conclusion and references present. PASS (accepted manuscript;
  12 manuscript pages vs 10 published pages is consistent with the extra layout of the author version).
- **Pages read:** 1–8 in full (text, tables, figures; Figs. 4–5 viewed as images); pp. 8–12 references and author
  biographies skimmed.
- **Supports ranked fixes (evidence 21):** #12 (METAR as context only, not a feature or label).

## Method (pp. 3–6)
1. Data: Sentinel-2 L1C patches centred on METAR stations, radius 16 km (3,200 × 3,200 px at 10 m), downsampled to
   300 × 300 px; METAR from the Iowa Environmental Mesonet ASOS-AWOS archive; nearest Sentinel-2 product within ±30 min.
   Regions: California, Florida, Montana, Texas, Washington. 12,749 image–label pairs (p. 4).
2. Classes (Table II, p. 3): CLR (US: "No clouds below 12 000 ft"), FEW (1–2 oktas), SCT (3–4), BKN (5–7), OVC (8);
   NCD = sensor error. Highest-coverage layer used as the ordinal class (p. 4).
3. Input preprocessing (p. 5): `NDSI = (X_G − X_S)/(X_G + X_S)` (Eq. 1; S = B11, ~1.61 µm); `X* = [X_R, X_G, X_B] ·
   (1 − NDSI)` (Eq. 2). RGB = B4, B3, B2.
4. Model (pp. 4–5): EfficientNetV2-S (~20 M parameters), ImageNet-1k weights, all layers unfrozen, new 5-unit head;
   Adam lr 1e-3, momentum 0.9, batch 48. Ordinal target: class c → ones for indices 0..c, zeros above (e.g. SCT =
   (1,1,1,0,0)); loss = MSE; prediction = highest index with output > 0.5.
5. Split (p. 5): 80:10:10; patches of neighbouring stations that overlap are clustered (modified DBSCAN, Chebyshev
   distance, ε = patch width) and each cluster goes wholly into one split; non-overlapping patches assigned stratified.
6. Metrics (p. 6): precision, recall, F1 (Eq. 3); ranked-within-n accuracy `ACC_n` (Eqs. 4–5: correct if
   |true rank − predicted rank| ≤ n); `F1,1` (within-one F1) is the default score.
7. Manual relabelling: all 12,749 patches relabelled by visual inspection, then the model was retrained and evaluated on
   those labels (p. 7).

## Results (only numbers stated in the paper)
- Abstract (p. 1): METAR labels only → "F1-score of up to 0.6" and ranked-within-1 accuracy 93.5–99.1%; with visual
  labels → 0.75 and 98.4–100%. (These abstract figures are not broken down in the body.)
- METAR labels, with NDSI (Fig. 4, p. 7): per-class F1,1 CLR 0.99, FEW 0.99, SCT 0.94, BKN 0.93, OVC 0.95 (without
  NDSI 0.95 / 0.96 / 0.88 / 0.93 / 0.93); exact-class ACC0 (confusion diagonal) CLR 0.47, FEW 0.34, SCT 0.47,
  BKN 0.36, OVC 0.72. One-hot classification / class regression were worse (F1,1 as low as 0.651 / 0.871).
- Manual labels (Fig. 5, p. 8): F1,1 0.984–1.000; ACC0 CLR 0.62, FEW 0.74, SCT 0.72, BKN 0.75, OVC 0.83.
- Mean per-station METAR-vs-visual mismatch ≈ 15.9% (Fig. 6, p. 7); METAR "favor[s] the outer extremes" — Fig. 5a
  shows far more CLR in METAR than in the visual labels (bar heights read approximately, not tabulated).
- Resolution: 800 and 3,200 px gave no "noticeable increase" over 300 px (p. 7). Inference ≈ 320 images/s on one A100.
- Releases: code https://github.com/ErikWessel/MSCC/ ; model checkpoints 10.5281/zenodo.14750977; dataset
  10.5281/zenodo.14691473 (p. 5, p. 7). Zenodo metadata checked 2026-10-29 (no download): record 14691474,
  `dataset_16km_300_ndsi.zip` 9,357,564,288 B, CC BY 4.0; checkpoints record 14750978, two `.pt` files ≈ 82 MB each.

## Key quotes
- "ACC0 scores between 34% and 72%" on raw METAR (p. 7)
- "We attribute this difference majorly to the large time offset of a maximum of 30 minutes between the Sentinel-2
  satellite image capture and the corresponding METAR report." (p. 7)
- "the quality of METAR-provided varies strongly, partially containing inaccurate information … it demonstrates the
  necessity to carefully cleanse and refine METAR information before using it as ground-truth" (p. 8)

## Limitations
- No Louisiana/Gulf Coast station regions; no hurricane or haze cases discussed.
- The 0.6 → 0.75 gain compares models trained **and tested** on different truths (METAR vs manual labels), so it is not
  a like-for-like improvement on one test set.
- Patch-level (32 km) classification only; no pixel masks, no thin-cloud analysis. Input uses SWIR (B11) through NDSI.
- Cause of mismatches (time offset vs ceilometer height limit) is asserted, not tested; Wagner & Kleiss 2016 would
  predict part of the CLR excess from unseen high cloud.

## How to apply to our pipeline
- **Context only; no code change** in `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`, `sn8_texture.py` or
  `sn8_glcm.py`.
- **Fix 12:** cite this as evidence that METAR is a poor label even at 32 km: exact agreement 34–72% per class, and
  about one in six station labels disagree with the image. At 0.5 m, a single KMSY report cannot label tiles.
- **Labelled-data rule:** the "corrected" labels are the authors' own visual labels. Under Justin's rule (train/test on
  published human labels, unmodified) the released manual labels are published by the authors, but they are 10 m
  Sentinel-2 patch grades — no use to our 0.5 m Maxar pipeline. Not recommended for download.
- **Design hint only:** the cluster-aware split (overlapping footprints kept in one fold) mirrors what our HRC_WHU/Ida
  folds should already guarantee for overlapping tiles; nothing new to adopt.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** the model is not transferable (needs
  Sentinel-2 B11 for NDSI, 10 m patches, US mainland stations). Using METAR rows as context is trivially feasible.
