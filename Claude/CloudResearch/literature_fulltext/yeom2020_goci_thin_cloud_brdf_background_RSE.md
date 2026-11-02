# Coder handoff: Yeom, Roujean, Han, Lee & Kim (2020), GOCI thin-cloud detection against a BRDF-modelled clear background

- **Citation:** Yeom, J.-M., Roujean, J.-L., Han, K.-S., Lee, K.-S., & Kim, H.-W. (2020). Thin cloud detection over land
  using background surface reflectance based on the BRDF model applied to Geostationary Ocean Color Imager (GOCI)
  satellite data sets. *Remote Sensing of Environment* 239, 111610. https://doi.org/10.1016/j.rse.2019.111610
- **Copy read:** the published Elsevier open-access version (CC BY-NC-ND 4.0), deposited on HAL:
  https://hal.science/hal-04732916v1/file/1-s2.0-S0034425719306303-main.pdf. 14 PDF pages = HAL cover + article pp. 1–13.
  Page numbers below are the **article's** printed numbers.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/yeom2020_goci_thin_cloud_brdf_background_RSE-summary.pdf`
- **Validation:** real PDF (4.97 MB); title and five authors match Crossref (vol. 239, article 111610); discussion,
  conclusions and references present. PASS (published version).
- **Pages read:** 1–13 (all text, tables and equations); reference list skimmed. Flowchart (Fig. 3, p. 5) checked on the
  rendered page.
- **Supports ranked fixes (evidence 21):** context for #11/#12 (gap 7: it is a geostationary product, but at 500 m);
  design support for #1 (HOT distance against a before-image clear line), #5 and #6 (signed residual against a clear
  reference, with a margin from model error).

## Algorithm (Section 3, pp. 3–5; Fig. 3)
1. Atmospherically correct each GOCI band to surface reflectance (SFC) with a 6S look-up table; aerosol, water vapour
   and profile inputs from MODIS MOD04/05/07, COMS MI as back-up (p. 3). Clear pixels for this step come from the
   conventional threshold mask.
2. Per pixel, per band: invert the kernel BRDF model (Eq. 1) by multiple linear regression over the cloud-free
   observations in a 16-day window. Fit **only if at least seven clear observations** exist (p. 4).
3. Simulate background surface reflectance `BRDF_i` (they also write ρ_model) for each hourly geometry (8 per day). View
   angles are fixed per pixel (geostationary); the solar angles vary with time, latitude and longitude.
4. **Step 1, thick cloud:** "simple threshold method using each of single band and band ratio" (p. 4). **The threshold
   values are not given in the paper.**
5. **Step 2, thin cloud**, mainly on band 1 (0.412 µm), because surface reflectance is lowest at short wavelengths (p. 4):
   - `DIFF_i = TOA_i − BRDF_i + |e_i|`, i = −16 … 0 (Eq. 5); `e_i = BRDF_i − SFC_i` (Eq. 6), the BRDF model error.
   - `MIN = min(DIFF_i)`, i = −16 … −1 (Eq. 7), computed separately for each hour so the solar geometry matches (p. 5).
   - `DIFF_0 < 0` → **shadow** (shadow checked with band 8, 0.865 µm).
   - `DIFF_0 > MIN + |e|` → **thin cloud**.
   - `MIN − |e| < DIFF_0 < MIN + |e|` → **probably clear**.
   - `DIFF_0 < MIN − |e|` → **certainly clear**.
6. No moving windows or spatial-variance tests, so the mask keeps the 500 m pixel (p. 6).
7. Validation only: parallax correction of CALIPSO cloud footprints to the GOCI view (Eqs. 8–11), nearest-hour matching
   (≤ 30 min).

## Equations (symbols)
- Eq. 1: `ρ(θs, θv, φ) = f_iso + f_geo·k_geo(θs, θv, φ) + f_vol·k_vol(θs, θv, φ)`. θs is the solar zenith angle, θv the
  view zenith angle and φ the relative azimuth. k_vol is Ross-Thick (Eq. 2), k_geo is Li-Sparse-Reciprocal (Eq. 4,
  following Lucht et al. 2000). The paper does not state the h/b and b/r shape ratios.
- Eq. 2: `k_vol = 4/(3π) · [(π/2 − ξ) cos ξ + sin ξ] / (cos θs + cos θv) − 1/3`. Eq. 3: `cos ξ = cos θs cos θv +
  sin θs sin θv cos φ`.
- Eqs. 12–14 (p. 10): `POD = A/(A+C)`, `FAR = B/(A+B)`, `MAR = C/(A+C)`. A = both cloudy, B = mask cloud / CALIPSO
  clear, C = mask clear / CALIPSO cloud.

## Parameters and data needs
- 16-day window; at least 7 clear observations; hourly GOCI (09:00–16:00 local); blue band 0.412 µm for thin cloud;
  NIR 0.865 µm for shadow; 6S LUT plus MODIS atmospheric products.
- Study period: 1 Jan 2014 – 30 Jun 2015, Northeast Asia (GOCI disk, 2500 × 2500 km).

## Results to compare against (Table 3, p. 10; CALIPSO VFM as reference)
| Exp. | Sensor | CALIPSO class | POD step 1 | POD step 1+2 | FAR | MAR | n |
|---|---|---|---|---|---|---|---|
| 1 | GOCI | all cloud | 0.638 | 0.831 | 0.034 | 0.169 | 200,869 |
| 2 | MODIS MYD35 | all cloud | – | 0.772 | 0.019 | 0.228 | 140,425 |
| 3 | GOCI | thin (altostratus + cirrus) | 0.338 | 0.849 | – | 0.151 | 44,296 |
| 4 | MODIS MYD35 | thin (altostratus + cirrus) | – | 0.849 | – | 0.091 | 24,996 |

- Note: Table 3 gives thin-cloud POD 0.849 for MODIS while the MAR is 0.091, so POD and MAR do not sum to 1 for
  experiment 4 (they do for experiments 1–3). That is as printed; we have not resolved it.
- GOCI vs MODIS directly (along the CALIPSO track, p. 11): POD 0.855, with FAR "increased over 0.167".
- No overall accuracy, kappa or significance test is reported.

## Key quotes and limits
- "surface BRDF varies slowly with time compared to that of clouds" (abstract, p. 1).
- "we calculated the minimum DIFFi … in the previous 16 days to find the atmospherically clearest day on the assumption
  that at least one day might be a clear day" (p. 5).
- "the cloud shadow makes TOA reflectance … abnormally lower than the simulated surface reflectance" (p. 5).
- Bright desert: "the proposed algorithm misclassified these areas as cloud areas although they were under clear sky
  conditions … the bright reflectance of desert areas reduces the difference in reflectance" (p. 11).
- Aerosol: GOCI flagged areas that CALIPSO called aerosol; "thick aerosols also increase with atmospheric reflectance …
  similar to cloud optical properties" and "the discrimination of thin cloud and aerosol is also very challenging"
  (p. 9).
- The abstract's "only thin cirrus" is, in Table 3, altostratus + cirrus (p. 10).

## How to apply to our pipeline
- **Not a drop-in algorithm.** It needs a 16-day, ≥ 7-clear-observation time series, angular sampling for a BRDF
  inversion, and atmospheric correction. We have one clear pre-storm Maxar date, uint8 RGB at 0.5 m, no NIR/SWIR/SAR.
- **Transferable logic for fixes 1, 5 and 6 (`sn8_cloudsym.py`, `sn8_cloudspot.py`):**
  - Background = the before image after invariant-pixel normalisation (fix 5), i.e. `f(before)`. Signed residual
    `D = after − f(before)` per band, low-pass filtered (fix 6).
  - Margin |e| = a robust spread (e.g. MAD) of D on pixels judged clear *and* unchanged, mirroring Eq. 6's
    model-error margin. Four classes: D < −|e| → darker than expected (shadow, *or water*); |D| ≤ |e| → clear;
    D > |e| → candidate haze/thin cloud. Report the margin used.
  - Use **blue** as the primary band (shortest wavelength, lowest surface contrast), as Yeom does with 0.412 µm. Maxar
    blue is much broader and longer (roughly 0.45–0.51 µm), so the gain will be smaller; test it as an arm against grey.
  - This can feed `change_gate`/`cloud_dates` in `sn8_cloudsym.py` and add a "residual vs before" column to
    `classical_cues` in `sn8_cloudspot.py`. Score with HRC_WHU folds + McNemar and NOAA-visible Ida tiles (fix 4).
- **Failure modes to expect here:** the paper's two false-positive sources map directly onto ours.
  - Bright surfaces → bright debris, roofs, sediment-laden water.
  - Aerosol vs cloud → haze vs thin cloud; we do not need to separate them for the road task.
  - Real change (flooding) breaks the "background is stable" premise; Yeom's 16-day minimum assumes no change.
    Exclude change-gated pixels from the margin estimate.
- **Gap 7 (fix 11/12):** this is evidence that geostationary visible-only masks can reach MODIS-level thin-cloud POD at
  **500 m**. It does not show transfer to sub-metre imagery, so it does not raise the strength of fix 11.
- **Texture (`sn8_texture.py`, `sn8_glcm.py`):** not addressed.
