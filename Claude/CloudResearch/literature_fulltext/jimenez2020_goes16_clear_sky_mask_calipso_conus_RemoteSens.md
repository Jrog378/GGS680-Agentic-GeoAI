# Coder handoff: Jiménez (2020), GOES-16 Clear Sky Mask (ACM) assessed against CALIPSO over CONUS

- **Citation:** Jiménez, P. A. (2020). Assessment of the GOES-16 Clear Sky Mask product over the contiguous USA using
  CALIPSO retrievals. *Remote Sensing* 12(10), 1630. https://doi.org/10.3390/rs12101630
- **Copy read:** NASA author manuscript NIHMS1710516 (PMC8243760), fetched from the PMC open-data S3 bucket
  (`https://pmc-oa-opendata.s3.amazonaws.com/PMC8243760.1/PMC8243760.1.pdf`). 24 pages: text pp. 1–11 (references pp.
  10–11), figures one per page pp. 12–24. Page numbers below are the **manuscript's**. The MDPI PDF link returned an
  Akamai "Access Denied" stub to curl, so it was not used.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/jimenez2020_goes16_clear_sky_mask_calipso_conus_RemoteSens-summary.pdf`
- **Validation:** real PDF (3.9 MB), 24 pages by pdfinfo and Read; title and sole author match Crossref (vol. 12, issue
  10, article 1630); discussion, acknowledgements and references present. PASS (author manuscript; MDPI typeset
  layout differs; licence CC BY 4.0, p. 1).
- **Pages read:** 1–24 (all); Figures 5, 8 and 9 viewed as images.
- **Supports ranked fixes (evidence 21):** #11 (GOES-16 ACM tile prior and cross-check flag) — mainly as a limit on how
  much a GOES call can be trusted; #12 indirectly (context only).

## What was done (pp. 3–5)
1. ACM product: "binary clear-sky mask (clear or cloudy) every 10 min (full disk), at 2 km of horizontal resolution at
   the satellite subpoint"; nine channels; four test groups (IR, SWIR, solar reflectance, clear-sky uniformity);
   thresholds tuned on SEVIRI–CALIPSO; designed so that "no more than 2% of cloud over-detection" is allowed (p. 2,
   citing the 2012 ATBD).
2. Truth: CALIPSO cloud layer product, 1 km, V3.40. A shot is cloudy if a cloud top is reported **and** CAD score > 30
   (p. 4).
3. Both are averaged onto a 9 km CONUS grid (the MAD-WRF grid). Need ≥ 2 CALIPSO shots per cell. Binary rule for both:
   `cloudy if cloud fraction > 0, clear if = 0` (p. 4).
4. Time match: ACM time over CONUS = scan start + 1/8 of scan duration; matched if within 600 s of the CALIPSO
   mid-pass time (p. 4). 1,371,012 matched cell pairs, 2018–2019.
5. Metric: "accuracy" = correct / total, computed separately for all cells, CALIPSO-cloudy cells and CALIPSO-clear cells
   (i.e. per-class recall). Kuiper's skill score `KSS = hit rate − false alarm rate` (range −1 to 1; p. 6). Maps use a
   15 × 15 cell moving window (p. 6).
6. Error heights: CALIPSO cloud-top for missed clouds; ACHA (10 km) cloud-top for false clouds (p. 5).

## Results (only numbers stated in the paper)
- All sky 86.0%, cloudy 90.9%, clear 74.8% (p. 5). Prior ATBD (SEVIRI, 8 weeks): 91.4% all-sky, 3.7% false cloud, 4.9%
  false clear (pp. 3–4). McCandless & Jiménez 2020 on the same grid: 85.7 / 93.0 / 67.7% (p. 3).
- Sample: 69.3% cloudy cells (950,350), 30.7% clear (420,662) (p. 5).
- Time offset 1 h: cloudy 88.0%, clear 69.0% (p. 5).
- Day: cloudy 95.9%, clear 66.6%; all-sky max 87.6% at threshold 0.20 (87.2% at 0). Night: cloudy 85.8%, clear 82.5%,
  all-sky 84.7% (p. 6).
- Summer daytime clear-sky accuracy "somewhat low (around 0.6)" with little latitude dependence (p. 7; Fig. 8c);
  winter daytime clear-sky collapses north of row ~150 (~36 N), near 0.5 beyond row 250 (~44 N) (p. 7).
- KSS > 0.8 in the south, down to 0.4 in the north (p. 6).
- ACHA-based binary mask: 82.9 / 91.2 / 64.8% (p. 7).
- Missed clouds: mostly boundary-layer, tops near 1 km AGL; false clouds also low (daytime peak near the surface)
  (pp. 7–8).
- April 2018 GHI test: MAD-WRF with the GOES mask gave MAE < 100 W m⁻² at most sites south of 36 N, vs > 100 W m⁻² at
  most sites for WRF-Solar (p. 9; one month only).

## Key quotes
- "The lower performance of clear sky retrievals is a result of missdetections during daytime. This is especially clear
  for summer, and for regions to the north of parallel 36 during winter." (p. 8)
- "The high (low) accuracy for cloud (clear sky) conditions suggests a cloud over-detection during daytime." (p. 6)
- "The majority of the missdetections are associated with low clouds." (p. 8)
- "regions to the south of parallel 36 show acceptable performance during both daytime and nighttime" (p. 8)

## Limitations (stated or evident)
- Validation is at 9 km with an "any cloud → cloudy" rule; this inflates cloudy calls for both sources and says nothing
  about sub-km accuracy.
- No stratification by cloud optical depth; thin cirrus, haze and aerosol are not analysed. The COD-dependent numbers
  in evidence 21 (COD 0.4, 45% at 0.01) come from the ATBD, not this paper.
- CALIPSO is treated as error-free (p. 4).
- The text describes the ACM as binary; the 4-level output (clear / probably clear / probably cloudy / cloudy) is not
  discussed.
- Summer daytime result (~0.6 clear) is read from Fig. 8c, not tabulated; the "acceptable south of 36 N" statement is an
  all-season conclusion.

## How to apply to our pipeline
- **Context and validation only; no algorithm to port.** It does not change `sn8_clouds.py`, `sn8_cloudsym.py`,
  `sn8_cloudspot.py`, `sn8_texture.py` or `sn8_glcm.py` directly.
- **Fix 11 design rules it implies** (for a future GOES tile-prior helper next to `sn8_cloudspot.tile_spot`, which
  already returns a per-tile `spot_tile` share):
  - Treat a GOES "cloudy"/"probably cloudy" call in summer daytime as weak evidence: Jiménez found ~40% of
    CALIPSO-clear daytime summer cells flagged cloudy at 9 km. In the cross-check flag (arm 7-ii), "GOES cloudy, spotter
    clear" should go to human review, not override the spotter.
  - "GOES clear, spotter cloudy" is the more informative disagreement (cloud detection 95.9% by day), but missed clouds
    are mainly low (~1 km) — exactly the small cumulus that shades roads.
  - Match the GOES scan to the Maxar pass time; the paper shows clear-sky agreement drops 7.7 points with a 1 h offset,
    so use the 5-min CONUS scan nearest the (still unconfirmed) pass time.
  - Score the prior as evidence 21 proposes (AUC against `spot_tile` and NOAA-visible tiles); do not quote Jiménez's
    86% as an expected accuracy for our tiles — the grid, truth source and rule all differ.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** feasible as an external tile-level
  input — GOES needs no bands from our imagery, only tile footprints and the pass time. One 2 km GOES pixel spans about
  4,000 × 4,000 of our pixels, so it can at most label whole tiles or tile groups.
