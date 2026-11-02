# Coder handoff: Frey, Ackerman, Holz, Dutcher & Griffith (2020), the Continuity MODIS-VIIRS Cloud Mask (MVCM)

- **Citation:** Frey, R. A., Ackerman, S. A., Holz, R. E., Dutcher, S., & Griffith, Z. (2020). The Continuity
  MODIS-VIIRS Cloud Mask. *Remote Sensing* 12(20), 3334. https://doi.org/10.3390/rs12203334
- **Copy read:** published MDPI version (CC BY 4.0) from the NOAA Institutional Repository,
  http://repository.library.noaa.gov/view/noaa/69642/noaa_69642_DS1.pdf (18 pages; page numbers below are the
  article's "x of 18").
- **PDF with summary:** `/Users/jusrogers/Masters/papers/frey2020_continuity_modis_viirs_cloud_mask_RemoteSens-summary.pdf`
- **Validation:** real PDF (4.8 MB), 18 pages by pdfinfo and Read (`file` said 10 — unreliable, as the checker notes);
  title and authors match Crossref (vol. 12, issue 20, article 3334; five authors incl. Griffith); conclusions and
  references present. PASS (published version).
- **Pages read:** 1–16 in full; references pp. 16–18 skimmed. Fig. 4 (p. 12) viewed as an image.
- **Supports ranked fixes (evidence 21):** #11 (external satellite cloud product as a tile prior / cross-check; MODIS
  is the polar-orbiter alternative to GOES); #1 indirectly (turbid water as a false-cloud source).

## Algorithm (pp. 2–5)
1. Heritage: MODIS cloud mask Collection 6 (MxD35). Per-pixel spectral threshold tests, each giving a confidence of
   clear sky, combined by "fuzzy logic" (details in Ackerman et al. 1998 and the ATBD; not restated here) (p. 2).
2. Bands: 14 shared MODIS/VIIRS bands (Table 1, p. 3): 0.412, 0.443, 0.555, 0.645, 0.859, 1.24, 1.375, 1.64, 2.13,
   3.75 (VIIRS) / 3.96 (MODIS), 8.55, 11.03, 12.02 µm. The **0.645 µm band is the land-surface cloud test** (Table 1).
   MODIS water-vapour/CO₂ bands (6.7, 7.3, 13.3, 13.9 µm; 0.905/0.936 µm) are dropped (Table 2).
3. Output: four classes — clear, probably clear, probably cloudy, cloudy (p. 5). Nominal L2 resolution 1 km (MODIS),
   750 m (VIIRS) (p. 2).
4. New tests (p. 4):
   - 1.6/2.1 µm ocean-day threshold test (thin clouds, partial pixels, edges over dark water).
   - **Turbid-water clear-sky test** (after Chen & Zhang): "Bottom and suspended sediments in near-shore waters can have
     strong reflectance signals in VNIR bands and result in false cloud determinations." Standard deviation of 2.1 µm
     reflectance in a 3 × 3 window; below a threshold → clear.
   - Snow over vegetation: NDVI threshold as a function of NDSI (Klein et al.).
5. Thresholds (pp. 4–5):
   - Daytime land 1.38 µm cirrus thresholds lowered from {0.040, 0.035, 0.030} to {0.0375, 0.0250, 0.0125} (low,
     middle, high confidence of clear).
   - Daytime water thresholds as a polynomial in solar zenith angle, Eq. (1): `thr = c0 + c1·sza + c2·sza² + c3·sza³ + …`
     (high-confidence-clear threshold; middle/low are offsets), fitted to collocated CALIOP.
   - View-angle scaling, Eq. (2): `thr_vza = thr · (1/cos(vza))^p`, p = 0.75 (VIIRS), 0.50 (MODIS) for 0.86 and
     1.38 µm; p = 0.25 for VIIRS 1.6 µm.
   - GDAS precipitable water used to drop pixels from the 1.38 µm test in very dry air (p. 15).
6. Evaluation metric, Eq. (3): `OvHR = (n_tp + n_tn) / n_total × 100` vs CALIOP 1 km cloud product; ≤ 5 min apart;
   only fully clear or fully cloudy CALIOP shots used (p. 7).

## Results (only numbers stated in the paper)
- Table 3 (p. 8), JJA 2018 hit rates (MYD35 / MVCM Aqua MODIS / MVCM SNPP VIIRS / MVCM NOAA-20 VIIRS):
  global 88.2 / 87.5 / 86.8 / 86.8; 60S–60N 90.7 / 90.5 / 90.1 / 90.3; 60S–60N land day 90.1 / 90.4 / 89.7 / 89.4;
  60S–60N water day 91.4 / 90.6 / 90.4 / 90.6; polar night 76.9 / 73.5 / 73.9 / 73.7.
- DJF 2017–18 global: 88.1 / 86.6 / 86.3 / 86.5 (NOAA-20 Jan–Feb only).
- Day-to-day 1° cloud-fraction differences (60S–60N, mean/SD %): MODIS−SNPP day 0.68/0.55, night 0.94/0.64;
  NOAA-20−SNPP day −0.20/0.50, night 0.44/0.82 (Table 4, p. 11).
- 1.38 µm test (Fig. 4, Julys 2013–2016, "hit" = cloud confidence > 0.5): for CALIOP COD > 0.25, hit rates > 0.9 for
  cirrus tops ~7–15 km; lower for "thin" clouds (lidar sees both cloud and surface) and over land; cirrus detection
  "about 20% higher over water" (pp. 11–12).

## Key quotes
- "the setting of thresholds is still largely subjective even when 'ground truth' (e.g., CALIOP cloud data) is used"
  (p. 14)
- CALIOP "is capable of detecting very optically thin clouds, it also provides a severe test of cloud masks derived from
  passive sensors" (p. 7)
- "Terra MODIS outputs have not yet been produced by the MVCM." (p. 2)

## Limitations
- Validation statistics are global/zonal; no per-region (e.g. Gulf Coast) or per-COD overall hit rates.
- Aqua and VIIRS only; **Terra MOD35 is not evaluated** here.
- CALIOP footprint 80 m vs 750–1000 m imager pixels; CALIOP nadir only, no sunglint (p. 7).

## How to apply to our pipeline
- **Context/validation only for code.** No test can be ported: the thin-cirrus skill rests on 1.375 µm, and the cloud
  tests use NIR/SWIR/TIR that our RGB uint8 Maxar tiles lack. No change to `sn8_clouds.py`, `sn8_cloudsym.py`,
  `sn8_cloudspot.py`, `sn8_texture.py`, `sn8_glcm.py`.
- **Fix 11:** if a polar-orbiter cross-check is added beside GOES, prefer the four-level MVCM/MxD35 class per tile
  (fraction of probably-cloudy + cloudy 1 km pixels over the tile footprint) and treat it like GOES: a prior/flag scored
  by AUC against `sn8_cloudspot.tile_spot`'s `spot_tile`, never a label. Check overpass time (nominal equator-crossing times are
  general knowledge, not from this paper — verify from the granule): Aqua and SNPP pass around 13:30 local, hours after
  the late-morning Maxar pass; Terra (~10:30) is closer but is not the sensor validated here.
- **Fix 1 (turbid water):** the paper confirms that sediment-laden near-shore water is a known false-cloud source in
  visible/NIR. Keep reporting turbid-floodwater false positives of the spotter separately, as evidence 21 already plans.
  The MVCM remedy needs 2.1 µm, so it is not available to us; an RGB analogue would be a new idea, not something this
  paper supports.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** product use is feasible (external
  ~1 km grid; one pixel ≈ 2,000 × 2,000 of ours); algorithm reuse is not.
