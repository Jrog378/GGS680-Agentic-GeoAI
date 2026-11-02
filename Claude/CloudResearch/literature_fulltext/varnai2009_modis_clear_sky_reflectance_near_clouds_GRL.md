# Coder handoff: Várnai & Marshak (2009), MODIS observations of enhanced clear sky reflectance near clouds

- **Citation:** Várnai, T., & Marshak, A. (2009). *Geophysical Research Letters* 36(6), L06807. https://doi.org/10.1029/2008GL037089
- **PDF:** `/Users/jusrogers/Masters/papers/varnai2009_modis_clear_sky_reflectance_near_clouds_GRL-summary.pdf` (page 1 = AI summary)
- **Source:** publisher typeset version as posted on NASA GSFC's climate site, retrieved from the UNT End-of-Term 2008 web archive: https://webarchive.library.unt.edu/eot2008/20090511171808id_/http://climate.gsfc.nasa.gov/publications/fulltext/Varnai_Marshak_GRL_2009.pdf
- **Validation:** `file` = PDF, 5 pages; 239 KB; Read tool shows page "5 of 5" as last page; pdfinfo 5 pages; p. 1 title/authors/DOI match Crossref; Summary (§4) and references present; GRL article numbered "1 of 5 … 5 of 5", consistent. PASS.
- **Read:** pp. 1–5 in full; Figs. 1–3 read from the page images.
- **Type:** atmospheric observation study, not a method. Sections below keep what we can use.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. How the distance profile was measured (§2, p. 1–2)
- Data: MODIS Terra, **1 km** reflectances at 0.47, 0.53, 0.68, 0.86, 2.13 µm and 11 µm brightness temperature; 1 km and 250 m cloud masks; 1 km cloud optical thickness; 5 km cloud-top pressure.
- Area/time: NE Atlantic, 45–50°N, 5–25°W (ocean, dark surface), 14–29 September, 2000–2007, all daytime Terra overpasses; view zenith < 10° (swath centre), so solar zenith **48° ± 2°**.
- Clear pixel = 1 km mask "confident clear" **and** all 16 sub-pixels "clear" at 250 m; only pixels with low cloud (top pressure > 700 hPa) within their 20 × 20 km surroundings.
- **Distance definition:** "the distance to the nearest pixel where clouds were not only detected but were even suitable for optical thickness retrievals" (p. 2). So distance is to a fairly thick cloud, not to the cloud-mask edge.
- Detector lag (latency) removed by using only clear pixels whose nearest cloud lies **downscan** (half the data).
- Profile = mean reflectance per 1 km distance bin, 1–20 km; enhancement = R(d) − R(20 km) (Fig. 2) or R(d) − R(10 km) (Fig. 3, by cloud optical thickness, only to 10 km because of sampling noise).

## 2. Measured numbers (text; figure values are my reads of the plots, marked ≈)
- "over two thirds of all cloud-free pixels are within 20 km of clouds and … the histogram of clear pixels peaks about 5 km away from the nearest clouds" (p. 2).
- "reflectance enhancements extending to about 15 km away from clouds, and the enhancements being stronger at shorter wavelengths" (p. 2); repeated in Summary: "The enhancements extend up to about 15 km away from clouds and are stronger near illuminated cloud sides than near shadowy ones" (p. 4).
- Fig. 1a (all downscan clear pixels): mean clear reflectance at 20 km ≈ 0.105 (0.47 µm), ≈ 0.065 (0.53), ≈ 0.035 (0.68), ≈ 0.02 (0.86), ≈ 0.01 (2.13); the near-cloud rise is visible at 0.47 µm as ≈ 0.01 above the 20 km line at 1–2 km.
- Fig. 2 (R − R(20 km)): 0.47 µm illuminated ≈ 0.008 at ~2 km, ≈ 0.004 at 5 km, ≈ 0.0015 at 10 km, ≈ 0 by 15–20 km; 0.86 µm illuminated ≈ 0.0045 near; shadowy sides about half the illuminated values (≈ 0.003–0.004 at 0.47 µm). Relative to the 20 km background this is roughly 8% at 0.47 µm and 20% at 0.86 µm near clouds (my arithmetic from figure reads; ocean background is very dark, so relative values would be much smaller over land).
- Fig. 3 (by cloud optical thickness τ, R − R(10 km)): illuminated 0.47 µm ≈ 0.0085 at 2 km for τ 13–30 vs ≈ 0.0055 for τ 0–2. Near shadowy sides of thick clouds the enhancement is smaller and "may even have a negative sign"; "The transition occurs at about 3–4 km away from clouds, which is comparable to the length of shadows expected for 48° solar zenith angle and 3 km cloud altitude" (p. 3).
- 11 µm brightness temperature: "well pronounced, but symmetric cooling near clouds" (inset Fig. 2: ≈ −0.7 K at 1 km, recovering by ~15–20 km).
- Su et al. (2008, cited p. 1) lidar: only a 10–15% increase in aerosol optical thickness near clouds, i.e. the aerosol change itself is small; 3-D simulations of Wen et al. (2007) made 1-D retrievals overestimate AOT by 50–140% (p. 3).

## 3. Interpretation by the authors
- 3-D radiative effects (cloud-reflected light scattered toward the sensor by air molecules in the clear gap) are "an important factor in the reflectance enhancements at shorter wavelengths" (p. 3). Undetected cloud and instrument blur likely contribute, "especially important at 2.1 µm" (p. 2).
- They do not give the 3-D share of the total; the sunlit-minus-shadowy difference is a lower limit (p. 4).

## 4. Stated limitations
- Ocean only, one region and season, one sun angle, low cloud only; 1 km pixels.
- Blurring (point-spread function) contribution not quantified ("future study").

## 5. How to apply to our pipeline
- **The 15 km number does not transfer to the fade width.** At 0.5 m, 15 km is 30,000 px; every SN8 tile next to a cloud is inside this zone. What does transfer is the **shape and the method**:
  1. **`sn8_cloudedge` / `sn8_refhaze` fade (DARKREF_GATE_MARGIN_PX, the 20 m linear fade):** fit the fade from the data the way this paper does: for clear (outside the gate) pixels, bin by distance to the gate edge (`cv2.distanceTransform` on ~gate), compute mean(dark(after) − tone(dark(before))) per bin, and set the fade where the excess reaches the far-field level. This is exactly arm "b: data fade" in `sn8_cloudedge.ARMS`; this paper is its published precedent. Fit per tile, use the excess at a far distance (paper: 20 km; us: the tile's far band, `FAR_PX`) as the zero.
  2. **Distance to a thick cloud, not to the mask edge.** The paper measures distance to retrieval-quality cloud. Our gate (dark-rise blobs ≥ 2,500 m²) is likewise a "thick" edge, so a measurable excess just past it is expected, not a fit failure.
  3. **Sun-side asymmetry:** enhancement is larger next to sunlit cloud sides and can be negative (shadow) within ~3–4 km of shadowy sides at 48° sun. In our tiles the cloud shadow falls on the anti-sun side; a one-sided fade (wider on the sun side, shadow handling on the other) is a testable arm. Shadow length ≈ cloud height × tan(solar zenith); Ida post-storm imagery metadata gives the sun azimuth/elevation.
  4. **Wavelength:** stronger at blue than red/NIR. Our tiles are RGB; computing the dark-rise per band (blue minus red excess) is a cheap haze-vs-cloud-edge cue for `sn8_cloudspot` that greyscale throws away.
- **Feasibility:** the measurement recipe is fully feasible on RGB uint8 0.5 m with one clear before date (the before date gives the per-pixel zero, better than the paper's far-field mean). No SAR/NIR needed.

## 6. Key quotes
- "3-D effects are responsible for a large portion of the observed increase, which extends to about 15 km away from clouds and is stronger (i) at shorter wavelengths (ii) near optically thicker clouds and (iii) near illuminated cloud sides" (abstract, p. 1).
- "we calculate a cloud-free pixel's distance to the nearest cloud as the distance to the nearest pixel where clouds were not only detected but were even suitable for optical thickness retrievals" (p. 2).
- "avoiding the most affected areas near clouds reduces data coverage and representativeness" (p. 4).
