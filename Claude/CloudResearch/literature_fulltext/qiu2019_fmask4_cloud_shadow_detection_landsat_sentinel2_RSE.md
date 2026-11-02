# Coder handoff: Qiu, Zhu & He (2019), Fmask 4.0: Improved cloud and cloud shadow detection in Landsats 4–8 and Sentinel-2 imagery

- **Citation:** Qiu, S., Zhu, Z., & He, B. (2019). *Remote Sensing of Environment* 231, 111205. https://doi.org/10.1016/j.rse.2019.05.024
- **PDF:** `/Users/jusrogers/Masters/papers/qiu2019_fmask4_cloud_shadow_detection_landsat_sentinel2_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** GERS Lab (UConn) copy in publisher layout, https://gerslab.cahnr.uconn.edu/wp-content/uploads/sites/2514/2021/06/Fmask4.pdf (29 MB; downloaded with curl)
- **Validation:** PDF, 20 pages (Read tool and pdfinfo; article number 111205, page footers 1–20); title/authors/DOI match Crossref (DOI printed on p. 1); §5 Discussions and conclusion and references present. PASS. (`file` metadata says 1 page; ignored.) Supplementary tables (S1–S4) not read.
- **Read:** pp. 1–20 in full; reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the article's 1–20.

## 1. Algorithm changes, step by step (§3, pp. 5–11; flowchart Fig. 5)
1. **Water test with GSWO** (eq. 1, p. 5): `(NDVI < 0.01 ∧ NIR < 0.11) ∨ (NDVI < 0.1 ∧ NIR < 0.05) ∨ (GSWO > O_water ∧ ¬snow)`, `O_water = 17.5th percentile of GSWO occurrence over spectrally derived water − 5%`. GSWO at 150 m is enough; DEM at 1 km (GTOPO30) is enough (Fig. 7, p. 7).
2. **Cirrus normalisation** (p. 6): per 100 m elevation zone, subtract a dark-cirrus value taken from a low percentile of clear (non-PCP) pixels' cirrus TOA. Thermal BT is DEM-normalised as in MFmask.
3. **Spectral variability** (p. 7–8): adds NDBI to NDVI, NDSI and whiteness.
4. **HOT-based cloud probability (Sentinel-2)** (eqs. 2–3, p. 8):
   - `HOT = Blue − 0.5·Red − 0.08` (TOA reflectance).
   - `lHOT = (HOT − (HOT_low − 0.04)) / ((HOT_high + 0.04) − (HOT_low − 0.04))`, `(HOT_low, HOT_high)` = 17.5th and 82.5th percentiles of **clear-sky land** pixels' HOT; "Assuming the HOT values of clear-sky pixels differ within 0.04"; built like the 2012 temperature probability.
   - Valid "Except for very bright land surfaces, such as urban and snow/ice, the higher the HOT values, the more likely they are clouds."
5. **Probability combination** (Table 2, p. 8): L4–7 land `lVar·lTemp`, water `wTemp·wBright`; L8 land `lVar·lTemp + 0.3·Cir`, water `wTemp·wBright + 0.3·Cir`; S2 land `lVar·lHOT + 0.5·Cir`, water `wBright + 0.5·Cir`. Cirrus weights chosen by minimum overlap of cloud vs clear distributions (Fig. 9).
6. **Threshold** (p. 9): still `82.5th percentile of clear-sky probability + c`, with **c = 0.1 (L4–7), 0.175 (L8), 0.2 (S2)** (was 0.2 for all), chosen for highest OA on 90 images (Fig. 10). "global optima but not regional optima. Users are welcome to adjust the threshold" (p. 16); Fig. 21 shows the omission/commission trade-off.
7. **Snow (SCSI)** (eq. 4, p. 9): `SCSI_n = SD_n(Green) · (1 − NDSI)`, n = 10 km window (333 Landsat px); snow if SCSI10 < 0.0009.
8. **Potential false-positive cloud pixels (PFPCPs)** (p. 10–11): urban = NDBI > 0 ∧ NDBI > NDVI, line-enhanced with four 3×3 directional line kernels (max response) (Fig. 13); cold cloud pixels removed by an Otsu threshold on BT (Landsat) or CDI < −0.8 (S2); urban dilated by a 500 m window (8-connected); mountain snow = potential snow ∧ slope > 20°, dilated 500 m; flat snow added undilated.
9. **Morphological elimination** (p. 11, Fig. 15): within PFPCPs, **erode with a disk**, then **dilate twice with the same disk**, "The dilated pixels cannot exceed the initial extent of clouds". Radius **150 m (5 px) L4–7; 90 m (3 px) L8; 90 m (S2)** (Fig. 16). Rationale: bright surfaces "show isolation, line, rectangle, and sharp shapes, which have an extremely large perimeter-to-area ratio, but clouds are usually the opposite." S2 extra: PFPCP objects < 10,000 px removed if their min CDI > −0.5.
10. **Shadow:** inherited from MFmask (Qiu et al. 2017) — not re-described here.

## 2. Inputs, outputs, data needs
- TOA reflectance (+ BT for Landsat), GSWO, DEM (+ slope/aspect). Output at 30 m (Landsat) or 20 m (S2). 1.5–10 min per image (p. 18).

## 3. Quantitative results to compare against (§4, pp. 11–16)
- Training/calibration: 90 L8 Biome images (6 excluded of 96); 17 snow/cloud-only images for SCSI.
- Validation: 2 locations × 8 biomes = 16 images per sensor; 100 random px per image; **unsure samples (often thin cloud) excluded**; L4–7 1,553, L8 1,552, S2 1,527 samples.
- L4–7 (Table 3): OA **92.40%** vs 90.73% (Fmask 3.3); cloud PA 88.04 vs 84.42; cloud UA 99.06 vs 99.84; shadow PA 72.58 vs 67.74, UA 50.56 vs 46.67.
- L8 (Table 4): OA **94.59%** vs 93.30%; cloud PA 95.77 vs 95.04, UA 97.48 vs 96.88; shadow PA 69.44 vs 55.56, UA 62.50 vs 53.33.
- S2 (Table 5): OA **94.30%** vs Sen2Cor 2.5.5 87.10%; cloud PA 93.65 vs 83.43, UA 97.27 vs 93.35; shadow PA 69.64 vs 39.29, UA 62.90 vs 73.33.
- **Evaluation protocol (p. 11): "we evaluate our cloud and cloud shadow results by dilating 3 pixels for cloud shadow pixels, but no dilation for cloud pixels."** Shadow UA "relatively low mainly because of the 3 pixels' dilation" (p. 13).

## 4. Stated limitations (pp. 16–18)
- Thresholds are global, not regional, optima.
- Erosion "may also remove some small clouds and result in some omission errors" — judged less serious than persistent commission.
- S2 version calibrated on L8-simulated data; processed at 20 m, so "missing very small clouds and their cloud shadows".
- Shadow omissions follow from cloud-object errors; wetlands, burned areas and terrain shadow confuse shadows.
- Validation sample small (16 locations); confident samples only.

## 5. How to apply to our pipeline
- **HOT cue (`sn8_cloudspot.classical_cues`, `sn8_clouds`):** HOT uses only blue and red, which our Maxar RGB tiles have. New cue, per tile:
  1. Compute on RGB (not grey): `hot = B − 0.5·R − k` (k irrelevant after normalisation; drop it).
  2. Clear-land set = pixels not in the dark-rise gate (and not water; flood is a problem — use the *before* image for the percentiles, which is clear).
  3. `lHOT = (hot − (p17.5 − m)) / ((p82.5 + m) − (p17.5 − m))` with m refit on our 0–255 scale (the paper's 0.04 is reflectance; start at the clear-pixel IQR × 0.5, tune on HRC_WHU).
  4. Two-date version (ours): `ΔHOT = hot_after − hot_before` normalised the same way on clear pixels → haze rise cue, complementary to dark rise. Caveat: Maxar visual product is colour-balanced 8-bit, not TOA; HOT's clear-sky line may not hold — test on HRC_WHU before trusting.
- **Bright-surface clean-up (`sn8_cloudsym._keep_blobs`, `DARKREF_MIN_CLOUD_M2`):** the erode-then-double-dilate (capped at the original mask) is a published alternative to our area floor for removing roofs, roads and debris: erode the dark-rise gate with a disk of radius r, dilate twice with the same disk, AND with the original gate. Their r ≈ 3–5 px at 30 m (90–150 m); at 0.5 m, r must be set by the size of the false positives (roofs ~10–20 m → r ≈ 10–20 m = 20–40 px) and tested; small real clouds will be lost (their stated cost).
- **Threshold offset knob (`sn8_clouds.cloud_thresholds`):** Fmask 4.0 keeps the per-scene "82.5th percentile of clear + c" form but tunes c per sensor and hands users the omission/commission curve (Fig. 21). Do the same: per-tile percentile + c, choose c from an omission/commission curve on development tiles, report it.
- **Buffers:** Fmask 4.0's own evaluation does **not** dilate cloud (only shadow, 3 px). The 500 m dilations here are for urban and mountain snow (to catch false positives near them), not for clouds. This weakens the "every Fmask version dilates cloud" reading in our notes; cloud dilation is a user option of the software, not part of the published accuracy.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** HOT cue — feasible (needs RGB, refit constants). Morphology clean-up — feasible. GSWO land/water — feasible as a prior (GSWO is 30 m, free) but floods are exactly where GSWO is wrong; use only for permanent water. Cirrus/thermal/NDBI/SCSI — not feasible.

## 6. Key quotes
- "Except for very bright land surfaces, such as urban and snow/ice, the higher the HOT values, the more likely they are clouds." (p. 8)
- "Assuming the HOT values of clear-sky pixels differ within 0.04, Fmask 4.0 makes this normalization process similar as how the temperature probability is calculated based on the thermal band" (p. 8).
- "these bright surfaces normally show isolation, line, rectangle, and sharp shapes, which have an extremely large perimeter-to-area ratio, but clouds are usually the opposite." (p. 10)
- "The dilated pixels cannot exceed the initial extent of clouds as we do not want to increase commission errors." (p. 11)
- "we evaluate our cloud and cloud shadow results by dilating 3 pixels for cloud shadow pixels, but no dilation for cloud pixels." (p. 11)
- "those thresholds are global optima but not regional optima. Users are welcome to adjust the threshold" (p. 16).
