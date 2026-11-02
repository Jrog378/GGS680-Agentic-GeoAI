# Coder handoff: Zhu, Wang & Woodcock (2015), Improvement and expansion of the Fmask algorithm (Fmask 3.2)

- **Citation:** Zhu, Z., Wang, S., & Woodcock, C. E. (2015). Improvement and expansion of the Fmask algorithm: cloud, cloud shadow, and snow detection for Landsats 4–7, 8, and Sentinel 2 images. *Remote Sensing of Environment* 159, 269–277. https://doi.org/10.1016/j.rse.2014.12.014
- **PDF:** `/Users/jusrogers/Masters/papers/zhu2015_improvement_expansion_fmask_landsat_sentinel2_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** GERS Lab (UConn, Zhe Zhu's lab) copy in publisher layout: https://gerslab.cahnr.uconn.edu/wp-content/uploads/sites/2514/2021/06/Improvement-and-expansion-of-the-Fmask-algorithm-cloud-cloud-shadow-and-snow-detection-for-Landsats-4–7-8-and-Sentinel-2-images.pdf (OpenAlex lists no OA copy)
- **Validation:** PDF, 9 pages (Read tool on p. 9 and pdfinfo) = published range 269–277; title/authors/DOI match Crossref (DOI printed on p. 269); §4 Discussion, §5 Conclusion and references present. PASS. Supplementary tables/figures (6 other sites) are online only and were not read.
- **Read:** pp. 269–277 in full; reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm changes, step by step (Fmask 3.2 vs 1.6; §2.1, pp. 272–273)
1. **Cloud detection:** the 2012 rule "cloud if land cloud probability > 99% regardless of spectral tests" is **removed** (it committed bright, white, cold clear pixels such as high-altitude snow).
2. **Cloud over water:** fixed 0.5 → **dynamic threshold = 82.5th percentile of cloud probability over clear-water pixels + 0.2** (mirrors eq. 17 of 2012 for land).
3. **Potential shadow:** flood-fill difference **> 0.02 in both NIR and SWIR1 (1.65 µm)** (was NIR only), to cut false potential shadow where many dark objects exist.
4. **Shadow match:** height search continues until similarity drops to **95%** of the max (was 98%), avoiding premature stops at local maxima.
5. **Snow I:** BT screen 277 K → **283 K** (MODIS C5).
6. **Snow II / buffers:** "The pixels surrounding clouds and cloud shadows are masked out in the Fmask algorithm because many of these pixels may still be influenced by the thin edges of clouds and their shadows (Zhu & Woodcock, 2012)." New: snow is also dilated, 8-connected, "for a user-specified distance (can be any positive integer based on the user's preference)". **No buffer width is given in the paper** for cloud, shadow or snow.

**Landsat 8 expansion (§2.2.1, p. 274)**
7. First-pass cirrus test: cirrus band (B9, 1.36–1.38 µm) TOA > **0.01** → PCP (0.01 = lowest 1% of simulated cloudy-sky reflectance, Wilson & Oreopoulos 2013; MODIS uses 0.03; L8 QA used 0.02). Thermal: Band 10 only (Band 11 "ghosting").
8. Cirrus probability (eq. 1): `cirrus / 0.04` (linear, exceeds 1 above 0.04). Added to the 2012 probabilities: water `brightness + cirrus` (eq. 2), land `variability + cirrus` (eq. 3) — as printed; for Landsat 8 the thermal temperature probabilities still apply ("almost all … the same as for Landsats 4–7").

**Sentinel 2 prototype (§2.2.2, p. 274)**
9. Thermal steps dropped; cloud probability by eqs. 2–3; cloud height range **fixed 200–1,200 m**, cloud = **flat plate**; no temperature screen for snow. Stated cost: thick clouds' matched shadows may have the wrong shape; more snow commission.

## 2. Inputs, outputs, data needs
- Landsat 4–7: TOA bands 1–5, 7 + BT. Landsat 8: adds cirrus. Sentinel 2 scenario: optical + cirrus, no thermal. Sun/view geometry for shadow matching. Single date.
- Output: cloud / shadow / snow / clear masks.

## 3. Quantitative results to compare against (§3, pp. 274–276)
- Design: 7 Landsat 8 scenes worldwide; Landsats 4–7 and Sentinel 2 **simulated** by band subsetting. At each site **200 random points inside the area where two scenarios disagree**, labelled manually. So accuracies are for the disagreement area only, not whole-scene accuracy.
- Amazon (P233/R61, captions sometimes print P223): Landsats 4–7 vs Sentinel 2 disagreement area — 3% vs **91%** overall (L4–7 missed all 186 cloud points; S2 missed 8) (Tables 3–4). Disagreement: 28.35% of the scene is L4–7 clear / S2 cloud (Table 2).
- Sentinel 2 vs Landsat 8 at the same site: 3% vs **89%** (S2 missed 191 of 193 cloud points; L8 missed 18) (Tables 6–7); disagreement ~10% of the image across sites.
- S2 > L4–7 at all 7 sites; L8 > S2 at 6 of 7 (mountain site P45/R30 the exception, cold high terrain inflating temperature probability). (Note: the text's sentence on the exception says "Landsat 8 … is better than … Sentinel 2", which contradicts the preceding "6 of the tested sites"; read as a typo.)
- Thin cirrus with cirrus TOA 0.01–0.03 is "almost invisible in the false color composite" (Fig. 2).

## 4. Stated limitations (p. 276)
- Small sample (7 images); Sentinel 2 simulated, not real; more environments needed.
- "optically thin clouds are difficult to detect as they may have spectral signatures similar to the Earth surface underneath" (p. 269).

## 5. How to apply to our pipeline
- **Gate margin / fade (`sn8_refhaze.DARKREF_GATE_MARGIN_PX` = 40 px, `DARKREF_CLEAR_MARGIN_PX` = 20 px; `sn8_cloudedge` arms):** the paper supports treating pixels next to cloud as contaminated by "thin edges" — but (i) it gives **no width** (the 3 px default is from the Fmask software README, not this paper), (ii) the band is **masked**, not corrected. So cite this paper for *having* a buffer and for excluding near-cloud pixels from the tone fit (supports `DARKREF_CLEAR_MARGIN_PX`); the 20 m fade width and correcting through the band stay our own rules. A defensible width would be measured on our tiles (residual-haze vs distance, `sn8_cloudedge.ring_measures`), not copied (3 Landsat px = 90 m; Sentinel-2 users often 0).
- **Scene-learned thresholds:** the dynamic water threshold shows the authors moved *toward* per-scene percentile + constant cuts. Same arm as in the 2012 handoff for `sn8_clouds.cloud_thresholds`: per-tile cut = 82.5th percentile of dark rise over provisional-clear pixels + margin.
- **Shadow (two-band agreement):** their fix for too many dark objects was to require darkening in two bands. Our analogue: a potential cloud shadow must be dark in the after image *and* darker than the before image (two-date agreement), so roof/tree shadows present on both dates drop out. Pair with geometry (2012 handoff) and the 95% stop rule.
- **No-thermal setting (Sentinel 2):** closest to ours. Without thermal they fix cloud height to 200–1,200 m and use flat plates: copy that for shadow projection with the Maxar sun angles (cumulus bases near 1 km are typical of the Gulf coast in summer — our assumption, not the paper's).
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** spectral tests (cirrus, thermal, NIR/SWIR flood-fill) not feasible. Buffer principle, scene-learned cuts, flat-plate shadow projection with fixed height range: feasible.

## 6. Key quotes
- "In particular, optically thin clouds are difficult to detect as they may have spectral signatures similar to the Earth surface underneath" (p. 269).
- "The pixels surrounding clouds and cloud shadows are masked out in the Fmask algorithm because many of these pixels may still be influenced by the thin edges of clouds and their shadows (Zhu & Woodcock, 2012)." (p. 273)
- "we dilate the pixels surrounding snow in 8-connected directions for a user-specified distance (can be any positive integer based on the user's preference)" (p. 273).
- "the threshold used for cloud detection in water areas is a dynamic threshold derived by adding the upper level (82.5 percentile) of cloud probability of all clear water pixels with a constant of 0.2" (p. 272).
- "if you have to choose between a cirrus band and a thermal band for cloud detection, a cirrus band is preferable" (p. 276).
