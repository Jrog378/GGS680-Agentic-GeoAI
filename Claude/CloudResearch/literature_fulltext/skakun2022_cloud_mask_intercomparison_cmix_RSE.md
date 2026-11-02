# Coder handoff: Skakun et al. (2022), Cloud Mask Intercomparison eXercise (CMIX)

- **Citation:** Skakun, S., Wevers, J., Brockmann, C., Doxani, G., Aleksandrov, M., Batič, M., Frantz, D., Gascon, F., Gómez-Chova, L., Hagolle, O., López-Puigdollers, D., Louis, J., Lubej, M., Mateo-García, G., Osman, J., Peressutti, D., Pflug, B., Puc, J., Richter, R., Roger, J.-C., Scaramuzza, P., Vermote, E., Vesel, N., Zupanc, A., & Žust, L. (2022). Cloud Mask Intercomparison eXercise (CMIX): An evaluation of cloud masking algorithms for Landsat 8 and Sentinel-2. *Remote Sensing of Environment* 274, 112990. https://doi.org/10.1016/j.rse.2022.112990
- **PDF:** `/Users/jusrogers/Masters/papers/skakun2022_cloud_mask_intercomparison_cmix_RSE-summary.pdf` (page 1 = AI summary)
- **Source:** NASA NTRS 20220006382, https://ntrs.nasa.gov/api/citations/20220006382/downloads/rse-2022-112990.pdf (publisher version, CC BY open access).
- **Validation:** PDF, 22 pages (pdfinfo; Read tool gives 23 for the merged file = 22 + summary; `file` wrongly said 1 page); article 112990 runs 22 pages; title/25 authors/DOI match Crossref; Conclusion (§6) and References present. PASS.
- **Read:** pp. 1–22. Large result tables (Tables 6–14) skimmed for averages and the cells cited here; the Table 15 strengths/weaknesses grid read through its text; references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Article page numbers 1–22. CEOS WGCV exercise (NASA, ESA, CNES, DLR, USGS, companies).
- **Type:** evaluation/benchmark paper. Sections below keep what we can use: protocol, buffer practice, thin-cloud findings, MAJA's multi-temporal tests.

## 1. Protocol (§2, p. 2–10)
- 10 algorithms (Table 3, p. 9): ATCOR (DLR, spectral, buffer 100 m), CD-FCNN (Valencia, U-Net ~96k params, no buffer), Fmask 4.0 (USGS, buffer L8 90 m / S2 60 m), FORCE (buffer 300 m), IdePix (no buffer used), InterSSIM (Sinergise, multi-temporal, 160 m), LaSRC (NASA/UMD, adjacency 5 px: L8 150 m / S2 50 m), **MAJA (CNES/CESBIO, multi-temporal, run at 240 m, buffer 240 m)**, s2cloudless (Sinergise, 160 m), Sen2Cor (ESA, no dilation).
- 5 reference datasets (Table 1, §2.1): CESBIO (30 S2 scenes, active-learning full classification, 60 m), GSFC (6 L8 + 28 S2, polygons guided by ground sky-camera photos, **cloud boundaries excluded**), Hollstein (59 S2 scenes, 1.59 M hand-picked pixels), L8Biome (96 L8 scenes, full manual labels; thin clouds by analyst judgement, no threshold), PixBox (S2 29 scenes/17,351 px; L8 11 scenes/20,500 px; expert-sampled, hard cases included).
- Binary cloud vs non-cloud; **shadows excluded**; metrics OA, balanced OA (BOA = mean of cloud and non-cloud recall), cloud PA (1 − omission), cloud UA (1 − commission) (Tables 4–5, p. 10). Confusion matrices pooled over all pixels of all scenes.

## 2. MAJA (multi-temporal, our design family) as described here (§2.2.9, p. 10; Table 15, p. 18)
- "The main cloud test detects the pixels for which the surface reflectance in the blue band increases sharply."
- Correlation test (Table 15): each cloud neighbourhood is correlated with previous observations; "If the correlation is high, it is not a cloud".
- Cirrus: cirrus > 0.007 + 0.007·h² (h altitude, km).
- Buffer: masks "dilated by 240 m, firstly to account for the parallax effects due to differences in observation angles between spectral bands, and secondly for the adjacency effects of clouds and for their 'fuzzy' borders" (p. 10).
- Weaknesses listed (Table 15): very rapid vegetation change can be flagged; less efficient where cloudiness is extremely high; needs dense time series (only processed 10/28 GSFC, 14/29 PixBox S2 scenes).

## 3. Quantitative results to compare against
- **Reference choice dominates:** average S2 BOA 80.0 ± 5.3% (PixBox) to 89.4 ± 2.4% (Hollstein); L8 BOA 79.8 ± 7.1% (PixBox), 90.0 ± 1.3% (L8Biome), 97.6 ± 0.8% (GSFC) (p. 16–20).
- **Thin cloud is the gap:** GSFC S2, all clouds: mean cloud PA 73.7 ± 5.6% excluding LaSRC; without thin clouds BOA +7.4 ± 2.6, PA +14.8 ± 5.2 points (p. 11). PixBox L8: opaque-cloud PA 95.9 ± 3.6% vs semi-transparent **40.6 ± 27.4%** (p. 15). Removing thin clouds raises OA by +1.5 to +7.4 points across datasets (p. 20).
- No S2 algorithm averaged PA > 90% and UA > 90% (p. 16). Five (Fmask, FORCE, IdePix, MAJA, s2cloudless) averaged both > 80%.
- **Urban bright targets:** all algorithms worst on clear urban pixels (PixBox S2, Fig. 14, p. 14); parallax tricks only partly help.
- Buffers trade UA for PA (MAJA PixBox S2: PA 88.6%, UA 80.2%, "in part due to the dilation", p. 11–12).

## 4. Stated limitations and recommendations (§5, p. 19–20)
- Need a **quantitative cloud definition** (e.g. cloud optical depth; Mejia et al.: thick τc > 30, thin τc ~ 1).
- New references should label edges and thin cloud; agree a **dilation** to apply to both references and algorithms ("Defining a proper dilation of cloud masks", p. 19); add shadows; collect time series; consider sample-based and area-based metrics; **application-based validation** (score the downstream product).
- Commercial VHR imagery is named as future scope (not covered).

## 5. How to apply to our pipeline
- **Scoring our cloud gate / `sn8_cloudspot` on HRC_WHU:** report cloud PA and UA separately plus BOA, pooled over pixels; state the reference and its cloud definition (HRC_WHU: thin cloud counts only where ground is unclear). Report thick and thin/edge strata separately where labels allow; CMIX shows that the headline number moves 2–15 points on that choice alone.
- **Edges:** GSFC excluded cloud boundaries from its reference; we can do the same (score with a ±k px boundary band excluded) and report both. This matches the ring/edge problem in evidence 10.
- **Buffer sizes for the record:** operational buffers range 0–300 m (MAJA 240 m, LaSRC 5 px, FORCE 300 m, ATCOR 100 m, Fmask 60–90 m, s2cloudless dilation 11 px at 10 m ≈ 110 m). Our 20 m fade is far smaller, at 0.5 m GSD it is 40 px. CMIX states the buffer should be agreed and applied equally to reference and algorithm when comparing.
- **Two-date gate (`sn8_refhaze.cloud_gate`, `sn8_cloudsym`):** MAJA's described tests are the same three ideas as our design: rise against earlier clear data, correlation veto, buffer. See the Hagolle 2010 handoff for thresholds.
- **Application-based validation** (their recommendation) is what we already do by scoring flood calls on roads; cite CMIX for it.
- **Bright urban false clouds:** expect our single-date masks to over-fire on roofs (all CMIX algorithms do on 10–30 m data); the two-date rise is our defence.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** none of the algorithms transfer directly (all need multispectral TOA, most need SWIR/cirrus/thermal; MAJA needs a dense series). The protocol, metrics, strata and buffer practice transfer fully.

## 6. Key quotes
- "The algorithms were in good agreement for thick cloud detection … in contrast to thin/semi-transparent clouds detection." (abstract, p. 1)
- "The main cloud test detects the pixels for which the surface reflectance in the blue band increases sharply." (p. 10)
- "An overall accuracy of 90% yields twice less errors than an overall accuracy of 80%." (p. 20)
