# Coder handoff: Koren, Remer, Kaufman, Rudich & Martins (2007), On the twilight zone between clouds and aerosols

- **Citation:** Koren, I., Remer, L. A., Kaufman, Y. J., Rudich, Y., & Martins, J. V. (2007). *Geophysical Research Letters* 34(8), L08805. https://doi.org/10.1029/2007GL029253
- **PDF:** `/Users/jusrogers/Masters/papers/koren2007_twilight_zone_clouds_aerosols_GRL-summary.pdf` (page 1 = AI summary)
- **Source:** publisher typeset version as posted on NASA GSFC's climate site, retrieved from the UNT End-of-Term 2008 web archive: https://webarchive.library.unt.edu/eot2008/20080916201317id_/http://climate.gsfc.nasa.gov/publications/fulltext/koren_twilight_2007GL029253.pdf (the Wiley/AGU free copy sits behind a browser challenge).
- **Validation:** `file` = PDF, 5 pages; 301 KB; Read tool pages 1–4 read as images, page 5 text = references ending "5 of 5"; pdfinfo 5; title/authors (5)/DOI match Crossref; Discussion (§3) and references present. PASS.
- **Read:** pp. 1–5 in full (pp. 1–4 from page images incl. Figs. 1–4; p. 5 references).
- **Type:** atmospheric observation study, not a method.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. How the distance/time profiles were measured
- **MODIS (p. 1–2, Fig. 2):** clouds identified "based on spatial variability" by the MODIS aerosol algorithm (Martins et al. 2002). For **20 MODIS cases over the global oceans**, all seasons, different cloud fields and aerosol loadings, the mean reflectance of cloud-free pixels is computed against the distance to the nearest cloud. Fig. 2 (right) plots the **870 nm** average reflectance against log distance (1 to ~30 km). Pixel size is not stated in the text.
- **AERONET (p. 2–3, Figs. 3–4):** 15 stations, 3–5 years each, high sun only (10 am–2 pm). Measurements every ≤ 15 min; a missing sun measurement = cloud. Each observation tagged with time since the nearest cloud; mean AOD (440, 870 nm) and Ångström exponent (440/870) computed against that time. Stations in three groups: Amazon dry-season biomass burning, clean islands, polluted urban/industrial.
- **Ground camera (Fig. 1):** a dissipating cumulus; subtracting the background (mostly Rayleigh) and masking the obvious cloud shows the "optical influence extends far beyond the borders of the cloud".

## 2. Measured numbers
- MODIS, 3 km vs 20 km from the nearest cloud, average of 20 cases (± standard error): **+5.6% ± 0.1% at 0.47 µm, +10.6% ± 0.1% at 0.66 µm, +13.0% ± 0.1% at 2.13 µm** (p. 1–2).
- "the enhanced reflectance decays up to **30 km** away from the nearest cloud (Figure 2) with an **e-folding distance of 10 km**" (p. 4). "decays **linearly with the logarithm of the distance** from the nearest cloud and extends tens of kilometers into the 'cloud-free' atmosphere" (p. 4).
- Fig. 2 (my read): 870 nm mean clear reflectance ≈ 0.053 at ~1 km falling to ≈ 0.033 at ~30 km.
- AERONET: AOD decreases linearly with ln(time since cloud) at all 15 stations; mean drop from the first sample near a cloud to the second (< 15 min later) **13% ± 2% (440 nm), 22% ± 2% (870 nm)**; to the third (< 30 min later) **15% ± 2% and 27% ± 2%** (p. 4). The first two samples are > 60% of the clear-sky data; the first three ~70% ("70% of the data is within 45 minutes of a cloud").
- Steeper decay where aerosol loading is higher: slope d(AOD)/d ln T vs mean AOD 870 nm is linear, from ≈ 0 at clean sites to ≈ −0.047 at AOD ≈ 0.73 (Fig. 4a).
- Ångström exponent rises from ≈ 1.20 near clouds to ≈ 1.30 at ~100 min (Fig. 4b): larger particles near clouds.
- Area: for global cloud fraction 0.51, a 10 km border around detectable clouds covers **17% of the globe (34% of the cloud-free area)**; a 30 km border **30% (60%)** (p. 4).

## 3. Authors' interpretation and caveats
- The enhancement near clouds is "clearly 'both'" undetected cloud and humidified aerosol (p. 3).
- Stray light and 3-D effects contribute within "the first 3 km of the cloud" in MODIS; AERONET is used because it is not affected (p. 2). "most of the signal shown in the MODIS images is real and is not instrumental nor a 3D effect. This is especially true 3 km and more from clouds" (p. 4).
- "Any cloud detection method … will encounter a 'gray area' where the cloud signal is weak" and "there is no perfect mask that will unambiguously determine the cloud" (p. 2, 4).
- A forming cumulus with downdrafts may have little twilight zone; the same cloud 10–20 min later produces a large one (p. 4).

## 4. Limitations
- MODIS part: 20 ocean cases; cloud edge from a variability test (not stated resolution); 3-D/stray light not separated within 3 km.
- AERONET part is in time, not distance.

## 5. How to apply to our pipeline
- **Distance scale does not transfer:** e-folding 10 km ≫ a 512 × 512 px tile at 0.5 m (256 m). Near a cloud our whole tile is in the first ~1–3% of the e-folding distance, i.e. in the region where the authors say MODIS is also affected by 3-D scattering/stray light. So the paper cannot give us a fade width in metres. It supports:
  1. **Log-distance fade arm in `sn8_cloudedge`:** replace the 20 m linear fade (`DARKREF_GATE_MARGIN_PX`) by a fade linear in log(distance) past the gate, fitted per tile: `excess(d) = a − b·ln(d)`, fitted on bins of distance to the gate edge from `dark(after) − tone(dark(before))` on pixels outside the gate; fade weight `w(d) = clip(excess(d)/excess(d0), 0, 1)`. This is the functional form Koren measured; compare against the current linear 20 m arm on the existing ring measures.
  2. **Scene haze loading sets the width:** steeper/stronger decay with higher aerosol loading. In code: let the fitted slope b vary per tile (do not share one fade across tiles); tiles with higher far-field dark-rise get a wider fade.
  3. **The tone-curve fit (sn8_refhaze `tone_curve`, `DARKREF_CLEAR_MARGIN_PX` = 10 m clear margin):** "clear" pixels 10 m from the gate are in the twilight zone by this paper; widen the margin, or fit the tone curve only on pixels in the far distance bins (largest distance from any gate in the tile), and record the tile-level far distance.
  4. **Abstain rule:** where the tile's far-field excess is still significantly above zero (no clean far bin), the whole tile is "inside the twilight zone"; mark corrections there as lower confidence (provenance layer, evidence 05 design 2).
- **Feasibility:** feasible with RGB uint8 + one clear before date (before gives the per-pixel zero). The wavelength dependence (larger *relative* excess at 0.66 than 0.47 µm here, whereas Várnai & Marshak 2009 report a larger *absolute* excess at shorter wavelengths; the two are not directly comparable) is a possible aerosol-vs-3D cue in RGB, but 2.13 µm and NIR are not available to us.

## 6. Key quotes
- "clouds are surrounded by a 'twilight zone' – a belt of forming and evaporating cloud fragments and hydrated aerosols extending tens of kilometers from the clouds into the so-called cloud-free zone" (abstract, p. 1).
- "the enhanced reflectance decays up to 30 km away from the nearest cloud (Figure 2) with an e-folding distance of 10 km" (p. 4).
- "there is no perfect mask that will unambiguously determine the cloud" (p. 2).
