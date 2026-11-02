# Coder handoff: Ackerman, Strabala, Menzel, Frey, Moeller & Gumley (1998), MODIS cloud mask (MOD35)

- **Citation:** Ackerman, S. A., Strabala, K. I., Menzel, W. P., Frey, R. A., Moeller, C. C., & Gumley, L. E. (1998).
  Discriminating clear sky from clouds with MODIS. *Journal of Geophysical Research: Atmospheres* 103(D24),
  32141–32157. https://doi.org/10.1029/1998JD200032
- **Copy read:** the authors' final manuscript, hosted by UW-Madison CIMSS (the authors' institute):
  https://cimss.ssec.wisc.edu/dbs/China2011/Day2/Lectures/MODIS_MOD35_cloud_mask_reference.pdf.
  - Word file "JGRFINAL.DOC", created 8 Jan 1999; header says "Manuscript submitted 28 November 1997".
  - 49 double-spaced pages. Page numbers below are the **manuscript's**.
  - The Wiley bronze-OA PDF returned a Cloudflare bot-check page to curl and was not used.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ackerman1998_modis_cloud_mask_clear_sky_JGR-summary.pdf`
- **Validation:** real PDF (0.91 MB, 49 pp.); title and all six authors match Crossref (103(D24), 32141–32157, a
  17-page article, consistent with 49 double-spaced pages). Summary, acknowledgments, references, tables and figures
  present. PASS as an **author manuscript**. The typeset wording and figures may differ slightly.
- **Pages read:** 1–49 (all). References (pp. 32–36) skimmed. Eq. 2 checked on the rendered p. 12.
- **Supports ranked fixes (evidence 21):** #2 (graded confidence + abstention; the strongest tie); context for #11/#12
  (gap 7: MOD35 as an external coarse cross-check).

## Algorithm (Sect. 3–4, pp. 6–22)
1. **Processing path** per pixel (bits 3–7): day/night (day = solar zenith < 85°), sun glint (reflected angle θr 0–36°,
   Eq. 3), snow/ice, land/water/coast/desert. The path chooses the tests (Table 3) and thresholds.
2. **Each test → a confidence F in [0, 1]** (Fig. 2, p. 6). There are three thresholds: α = high-confidence cloudy (F = 0),
   β = pass/fail, γ = high-confidence clear (F = 1). F rises linearly between α and γ. Range tests (e.g.
   0.9 < r0.87/r0.66 < 1.1) need six thresholds. Example: BT11 over ocean, α/β/γ = 267/270/273 K (p. 17).
3. **Groups** by cloud type (p. 8):
   - I, thick high cloud: BT11, BT13.9, BT6.7.
   - II, thin cloud: BT11−BT12, BT8.6−BT11, BT11−BT3.9, BT11−BT6.7.
   - III, low cloud: r0.87, r0.65, r0.936, reflectance ratio, BT3.9−BT3.7.
   - IV, upper-tropospheric thin cirrus: r1.38.
   - V, cirrus: BT11−BT12, BT12−BT4, BT13.7−BT13.9.
4. **Combine** (p. 12):
   - Eq. 1: `G_i = min_j F_j` (the minimum test confidence within group i).
   - Eq. 2: `Q = (∏_{i=1}^{N} G_i)^{1/N}`, the **N-th root of the product** (geometric mean). Any F = 0 forces Q = 0.
     The authors say this "will err on the side of too many cloudy reports".
5. **Output levels** (bits 1–2): confident clear Q > 0.99; probably clear Q > 0.95; undecided Q > 0.66; cloudy
   Q ≤ 0.66. Internally there are four more levels (Q > 0.34, > 0.05, > 0.01, ≤ 0.01) (p. 21).
6. **Second pass for inconclusive pixels** (0.05 < Q < 0.95):
   - A spatial-uniformity test on 3×3 BT11 (ocean only). It raises the level by one if all neighbours are within
     0.5 °C (p. 22).
   - A temporal test against an 8-day, 25 km composite of high-confidence (Q > 0.95) clear BT11 (min/mean/max). Below
     the minimum, confidence drops by 2 levels; between minimum and mean, by 1; it is raised symmetrically
     (pp. 20–21).
7. **Extra flags:**
   - Heavy aerosol (bit 8).
   - Thin cirrus from 1.38 µm (bit 9). "it is possible to indicate both high confident clear and presence of thin
     cirrus" (p. 16).
   - Shadow (bit 10): r0.94 < 0.12 and r0.87/r0.66 > the ocean threshold (p. 16).
   - Adjacency (bit 12).
   - Per-test yes/no bits 13–25.
   - A 250 m visible-only (0.66/0.88 µm) yes/no mask with 16 sub-pixels per 1 km (bits 32–47).

## Visible-only tests (the only ones near our band set)
- Visible reflectance (bit 20): 0.66 µm over land. "does well for discriminating bright clouds over dark surfaces …
  and poorly for clouds over bright surfaces" (p. 19).
- Reflectance ratio (bit 21): r0.87/r0.66 between 0.8 and 1.1 in cloud (AVHRR); the authors prefer a GEMI-based η.
  It is not run over desert or coast (pp. 19–20). **It needs NIR, which we do not have.**

## Results (pp. 23–28): qualitative only
- Pre-launch, so there is no POD/FAR/accuracy table.
- Weather stations (Fig. 8): "generally doing a satisfactory job, particularly for clear skies" (p. 27).
- SUCCESS cloud lidar vs MAS (Fig. 9, p. 28):
  - "Nearly all of the CLS labeled clear scenes are identified as high confident clear".
  - "Essentially all … thick cloud scenes are labeled as cloudy".
  - "A majority of the thin cloud cases are labeled as either confident clear or cloudy".
  - There are few "uncertain" labels, and those occur mainly near cloud edges.
- Summary (p. 31): most observations have Q > 0.95 or Q < 0.05. Intermediate Q occurs "at cloud boundaries … or over
  certain land surfaces such as desert".

## Key quotes and limits
- "Thresholds are never global. There are always exceptions" (p. 7).
- "it seems unrealistic to label a pixel with a reflectance of 6.1 as cloudy, and a neighboring pixel with the
  reflectance of 6.0 as non-cloudy" (p. 7). This is the motivation for confidence ramps.
- Thin cirrus with optical depth below about 0.1 is flagged for regions "where land property retrieval algorithms should
  incorporate a cloud correction" (p. 26).
- Thresholds were expected to need "considerable adjustment" after launch (p. 31). Operational MOD35 C6.1 differs;
  see Frey et al. 2020 for its validated numbers.

## How to apply to our pipeline
- **Fix 2, calibrated confidence + abstention.** This is the template. In `sn8_cloudspot.py` (`classical_cues`,
  `CloudSpotter`) and the road rule in `sn8_clouds.py` (`ROAD_CLOUD_CUT = 0.2`, `assessable`):
  - Give each classical cue (whiteness, HOT distance, dark channel, blue/red ratio from fix 1) an α/β/γ linear ramp,
    with the α and γ set from HRC_WHU dev-fold quantiles (for example, the 5th/95th percentile of clear and cloudy
    pixels).
  - Group the cues by what they detect: brightness/whiteness, haze/transmission, and two-date residual (fix 6). Take
    the min within each group and the geometric mean across groups.
  - Report four levels (confident clear / probably clear / undecided / cloudy). Roads whose strip falls in
    "undecided" abstain.
  - Compare against the random-forest probability, calibrated (Platt or isotonic), on risk–coverage curves and
    road-flood F1 at matched coverage.
  - Treat MOD35's 0.99/0.95/0.66 cut-offs as *structure*, not values to copy. Our Q needs its own calibration.
- **A "thin haze but usable" flag:** MOD35 lets a pixel be clear *and* thin-cirrus-flagged. That suits roads in our
  pipeline: dehaze and assess when the haze flag is set but the confidence is clear, rather than abstain
  (`sn8_clouds.dehaze`, `sn8_cloudsym.either_date_dehaze`).
- **Temporal and spatial second pass only for undecided pixels:** in our setting the temporal analogue is the
  before-date residual (fixes 5–6). The spatial analogue is a local-uniformity check, but MOD35 does *not* run it over
  land because land is heterogeneous. At 0.5 m over urban/rural Louisiana that warning applies even more strongly.
- **Gap 7 (fixes 11/12):** the MOD35_L2 granule for 2021-243 is only a ~1 km cross-check of whether the scene was
  cloudy. It cannot resolve sub-metre haze. Not a feature.
- **Texture (`sn8_texture.py`, `sn8_glcm.py`):** not addressed.
- **Feasibility:** the spectral tests are infeasible (no TIR/SWIR/NIR). The confidence-combination logic is fully
  feasible on RGB cues.
