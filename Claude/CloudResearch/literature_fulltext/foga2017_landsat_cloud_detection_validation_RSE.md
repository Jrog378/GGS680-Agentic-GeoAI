# Coder handoff: Foga et al. (2017), Cloud detection algorithm comparison and validation for operational Landsat data products (L8 Biome)

- **Citation:** Foga, S., Scaramuzza, P. L., Guo, S., Zhu, Z., Dilley, R. D., Beckmann, T., Schmidt, G. L., Dwyer, J. L., Hughes, M. J., & Laue, B. (2017). *Remote Sensing of Environment* 194, 379–390. https://doi.org/10.1016/j.rse.2017.03.026 (USGS EROS; agency paper).
- **PDF:** `/Users/jusrogers/Masters/papers/foga2017_landsat_cloud_detection_validation_RSE-summary.pdf` (page 1 = AI summary)
- **Source:** accepted manuscript ("made available under the Elsevier user license", p. 1), hosted by co-author Zhe Zhu's GERS lab: https://gerslab.cahnr.uconn.edu/wp-content/uploads/sites/2514/2021/06/1-s2.0-S0034425717301293-Steve_Foga_cloud_detection_2017.pdf. USGS Pubs Warehouse (70186881) has no PDF of its own.
- **Validation:** PDF 1.5, 1.2 MB, 54 pages (Read tool, pdfinfo) — accepted manuscript, double-spaced; published version is 12 pages (379–390), so the difference is expected. Title, 10 authors, DOI match Crossref; Conclusion + references present. PASS (accepted-manuscript pagination). Page numbers below are the manuscript's.
- **Read:** pp. 1–45 in full (eqs. 1–3, 7–8 from page images); references pp. 45–53 skimmed.
- **Type:** validation / benchmark-dataset paper. Prepared by Claude (AI), 2026-10-29.

## 1. Labelling rules ("L8 Biome", §3.3, pp. 11–13)
- Classes: **fill, clear, thin cloud, cloud, cloud shadow** (p. 8). One analyst (to avoid the ~7% between-analyst error reported earlier), Photoshop + Wacom, 16-bit bands composited (normal clouds 5-3-2; snow 6-3-2; fog 6-5-3; supplementary 7, 9 cirrus, 10, 11 thermal as grey).
- Workflow: (1) remove fill; (2) composite; (3) stretch until clouds "appeared both bright and opaque"; (4) magic wand / select-by-colour for clouds → layer; (5) **remove bright clouds, re-stretch, select thin clouds** → own layer; (6) close gaps in thin cloud by expand-then-contract 1 px; (7) manually remove false detections — "bright targets in areas such as urban landscapes, snow-covered mountains, and rivers"; (8) digitise shadows "if easily identified".
- "Clouds that were not immediately obvious were determined foremost by their adjacent shadow, otherwise by their shape and texture" (p. 11).
- "a quantitative threshold does not exist to distinguish thin cloud and transparent features such as haze or aerosols, making thin cloud identification inherently subjective to any analyst" (p. 12).
- Shadows: "we passed up shadow digitization on scenes that had low illumination or high relief areas" (p. 8) — Biome shadow labels are incomplete ("some" in Table 1).
- **L8 SPARCS** (p. 5–6): 80 sub-scenes 1000 × 1000 at 30 m, hand-labelled "without using spectral thresholding or pre-classification" as cloud, shadow, snow/ice, water, flooded, clear by one interpreter; snow/ice, water and flooded relabelled clear here; 6 sub-scenes re-labelled independently with **96% agreement** ("at least 4% of pixels in the dataset are ambiguous"). No thin-cloud class.
- **L7 Irish**: 102 validation masks (of 207), cloud + thin cloud.
- Scene sampling: 8 IGBP biomes (incl. **Urban**, Water) × 3 cloud bins (clear < 35%, mid 35–65%, cloudy > 65%) × 4 = 96; ~25% of random path/rows redrawn to reduce clustering (pp. 9–11).

## 2. Scoring rules (Table 4, p. 25; eqs. 1–8)
| Reference | Algorithm correct if | False if | Ambiguous if |
|---|---|---|---|
| Thick | Thick | Clear or Shadow | Ambig or Medium |
| **Thin** | **Thick or Ambig or Medium** | Clear or Shadow | – |
| Clear | Clear or Shadow | Thick | Ambig or Medium |
| Shadow | Clear or Shadow | Thick | Ambig or Medium |
- `%Correct = (thick_as_thick + thin_as_thick + clear_as_clear + shadow_as_shadow)/npix` (eq. 1; npix = valid, non-fill pixels).
- `%Omission = (total_cloud − cloud_as_cloud)/total_cloud × 100` (eq. 2); `%Commission = (clear_as_cloud + shadow_as_cloud)/(total_clear + total_shadow) × 100` (eq. 3). Shadow versions eqs. 4–6.
- Suitability: `%Correct − (%Omission + %Commission + %Ambiguous)` (eq. 7); shadow without ambiguous (eq. 8).
- Thin cloud thus counts as cloud; calling it thick is never penalised; calling it clear is.

## 3. Numbers (Tables 5–6, pp. 25–28; all three mask sets)
| Algorithm | % correct | % ambig | Omission | Commission |
|---|---|---|---|---|
| CFMask (dilated 3 px) | 89.29 | 0.00 | 2.72 | 12.02 |
| CFMask confidence (no dilation) | 90.45 | 1.38 | 3.65 | 10.06 |
| AT-ACCA (best non-thermal) | 87.52 | 1.27 | 12.42 | 9.83 |
| ACCA | 83.83 | 9.78 | 6.66 | 5.85 |
| See5 | 85.79 | 2.50 | 14.83 | 5.71 |
| CFMask NT (no thermal) | 79.15 | 0.00 | 34.56 | 8.38 |
| LaSRC CCA | 73.07 | 7.91 | 4.70 | 23.90 |
- Shadow (Table 6): CFMask 96.17% correct, omission 13.39, commission 1.32; LaSRC 93.85 / 26.06 / 4.77.
- By biome (Table 7): CFMask Urban 92.05% correct, commission 13.94; Water 86.36 / 26.99; Snow/Ice worst (64.09).
- Dilation (Fmask default 3 px, 8-connected): "Dilation reduces ambiguity of a cloud-contaminated pixel at the cost of potentially high commission error" (p. 17).
- CFMask confidence: low < 12.5, medium 12.5–22.5, high > 22.5 potential-cloud score (p. 18).

## 4. Stated limitations / known issues (pp. 39–42)
- Commission over smoke ("smoke resembles the shape and spectral response of thin clouds"), sun glint, coastal foam, terrain shadow, snow/ice.
- Multi-date verification is "vulnerable to interference from phenomena such as weather, seasonality, natural disaster, anthropomorphic modification" (p. 40) — directly relevant to our two-date gate on a flood.
- Shadow omission dominated by errors in the cloud objects from which shadows are projected.

## 5. Licence / usage
- Manuscript: Elsevier user license. All three mask sets "provided online at no cost" (USGS 2016a–c; pp. 5–6, 13). No other licence stated.

## 6. How to apply to our pipeline
- **Scoring rule for our cloud masks (sn8_cloudspot on HRC_WHU; any SN8 hand-checked tiles):** adopt Table 4's asymmetric thin-cloud rule. If our reference has a thin class, count thin → cloud/"cannot assess" as correct and thin → clear as false. Report %correct, omission, commission, %ambiguous, and eq. 7 suitability per tile group, to line up with Table 5.
- **Ambiguous output as a category:** their "medium confidence" = our "corrected/uncertain" band; report its share like %Ambig rather than forcing it into clear or cloud.
- **Edge buffer (sn8_cloudsym 20 m fade; sn8_cloudedge arms):** cite the 3-px dilation trade explicitly (omission down, commission up) when reporting the ring/fade arms; measure both.
- **Labelling recipe for any hand-checked SN8 cloud tiles:** two-pass digitising (bright cloud first, remove, re-stretch, then thin cloud), explicit removal of bright urban targets, shadows only where unambiguous. One labeller for consistency, a second on a subset for agreement (their 96%).
- **Two-date caution:** their own warning that multi-date checks are confounded by natural disasters — keep our dark-rise test signed and texture-checked so flood water is not called cloud.
- **Feasibility:** protocol fully usable; algorithms need Landsat multispectral/thermal bands — not usable on RGB 0.5 m.

## 7. Key quotes
- "a quantitative threshold does not exist to distinguish thin cloud and transparent features such as haze or aerosols, making thin cloud identification inherently subjective to any analyst" (p. 12)
- "Dilation reduces ambiguity of a cloud-contaminated pixel at the cost of potentially high commission error" (p. 17)
- "Six sub-scenes were labeled by an independent interpreter with 96% agreement, implying that at least 4% of pixels in the dataset are ambiguous." (p. 6)
