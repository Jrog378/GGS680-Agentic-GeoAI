# Coder handoff: Hughes & Hayes (2014), SPARCS — Automated detection of cloud and cloud shadow in single-date Landsat imagery using neural networks and spatial post-processing

- **Citation:** Hughes, M. J., & Hayes, D. J. (2014). *Remote Sensing* 6(6), 4907–4926. https://doi.org/10.3390/rs6064907
- **PDF:** `/Users/jusrogers/Masters/papers/hughes2014_sparcs_cloud_shadow_neural_network_RemoteSens-summary.pdf` (page 1 = AI summary)
- **Source:** MDPI file server, https://mdpi-res.com/d_attachment/remotesensing/remotesensing-06-04907/article_deploy/remotesensing-06-04907.pdf (open access; www.mdpi.com blocks scripts).
- **Validation:** PDF 1.6, 3.2 MB, 20 pages (Read tool, pdfinfo) = 4907–4926; title, both authors, DOI match Crossref; Conclusions + references present. PASS.
- **Read:** pp. 4907–4924 in full (Tables 1, Sec. 3.2–3.3 checked on page images); references skimmed.
- **Type:** method paper (with its own small evaluation set). Prepared by Claude (AI), 2026-10-29.

## 1. Data and labelling (§3.1, pp. 4910–4911)
- **Sensor: Landsat 7 ETM+ (2001, pre-SLC-off)**, TOA reflectance + dark-object subtraction; thermal B6 rescaled `B̂6 = B6/100 − 2` (eq. 2).
- **Training:** USGS LDCM CCA manual masks; "The core-cloud and thin-cloud classes, which were separate in the USGS data, were combined into a single cloud class" (p. 4910). 12 scenes (of 18 with > 1% cloud and shadow; 6 rejected as inaccurate) × four 1000 × 1000 sub-scenes = 48. Water and snow/ice added by NDSI / tasseled-cap thresholds then hand-edited; precedence: cloud unchanged; clear → water/snow if flagged; shadow over water hand-set; "Cloud shadows over water were labeled as cloud shadow where a distinction could be made."
- **Test:** 12 other scenes, one 1000 × 1000 sub-scene each, labelled by k-means (100 clusters) → operator assigns each cluster to a class → hand-correct mislabelled regions (p. 4911). Not used in training.
- No thin-cloud class anywhere in SPARCS output.

## 2. Algorithm (§3.2–3.3, pp. 4912–4914)
1. NN (MATLAB patternnet, scaled conjugate gradient), inputs ETM+ 1–5, 7, B̂6; 30 hidden nodes, no spatial inputs chosen. Training: up to 1,500 px per class per sub-scene (166,639 samples).
2. Six post-processing rules on the continuous membership images:
   - (i) 3 × 3 median on cloud and shadow memberships;
   - (ii) lower cloud/shadow/snow membership **within 3 px of large water bodies** (shallow water ~ cloud/snow, wet soil ~ shadow);
   - (iii) **shadow feasibility zone:** shift cloud membership away from the sun by the distance for cloud height 2,250 m, dilate for 1,800–2,700 m, expand + blur with a 15 × 15 filter, multiply into shadow membership (raises shadow inside, lowers outside = terrain shadow);
   - (iv) ambiguous shadow/water pixels surrounded by high shadow → shadow;
   - (v) ambiguous cloud/snow pixels surrounded by cloud → cloud;
   - (vi) uncertainty = variance between memberships (rescaled 0–1); uncertain pixels blended toward a certainty-weighted Gaussian (σ = 2 px) neighbour average.
- TVR (eq. 1, `min ‖u − f‖² + 2α|∇u|`, α = 0.05/0.10) and 5 × 5 / 9 × 9 means were tested as inputs; no significant gain before post-processing (ANOVA Table 2, p = 0.198).

## 3. Scoring (§3.4, p. 4914)
- Crisp class = max membership. **"a three-pixel buffer around the areas labeled as cloud and cloud shadow in the evaluation masks was constructed. Pixels within this buffer were scored as correct if they were labeled as either cloud or cloud shadow ... or the label in the evaluation mask"**; raised accuracy ~2% for all methods.
- Omission = cloud/shadow labelled clear; commission = clear (outside buffer) labelled cloud/shadow; cloud↔shadow confusion excluded from omission/commission.
- Multiway ANOVA + Tukey HSD on 540 accuracy scores (45 networks × 12 sub-scenes).

## 4. Numbers (Tables 4–5, pp. 4918–4921)
- Post-processing: accuracy ~94.5% → ~97%. Final overall 98.8% (SPARCS) vs 95.3% (Fmask) (p. 4923).
- Table 4: shadow → clear 3.2% (Fmask 8.0%); cloud → clear 1.3% (0.9%); clear → shadow 0.5% (2.4%); clear → cloud 0.2% (2.8%); Fmask confuses 20.9% of shadow as cloud.
- Per-scene (Table 5): hardest scenes Antofagasta (missed cloud 18.0%), Jammu & Kashmir (missed shadow 19.2%), NSW (missed cloud 11.2%).

## 5. Stated limitations
- Thin clouds and their shadows missed by both methods: "the spectral signal of areas contaminated with thin clouds and their shadows is a mixture ... especially difficult to detect"; "Successful methods typically use multi-temporal image stacks" (p. 4918).
- Over-shadowing of dark water near clouds; bright land called cloud (p. 4918).
- Both methods have "a halo of commission error around cloud and cloud shadow objects" from deliberate mask expansion — "a trade-off between commission and omission errors" (p. 4919).
- Inconsistency: composite weight eq. 4 uses 255 and 60 while the text says day 225 and σ = 30 days (p. 4915).

## 6. Licence / usage
- Article open access (MDPI, 2014). The paper states no data licence; it does not release the 80-scene L8 SPARCS dataset (that is the later Landsat 8 extension described in Foga et al. 2017, p. 5).

## 7. How to apply to our pipeline
- **Shadow gate (new; relevant to SN8 false floods):** implement rule (iii) in grey: from the cloud mask (`sn8_cloudsym` gate or `sn8_cloudspot`), project along the anti-sun azimuth (from Maxar metadata, if present in the tile GeoTIFF/JSON; else estimate from building shadows) over a height range, dilate + blur, and only allow "cloud shadow" inside that zone. At 0.5 m, a 2 km cloud height gives offsets of km scale — the shadow often lies outside a 650 m tile, as the project already found; use it where the cloud is in view and fall back to the two-date texture test otherwise.
- **Water-edge rule (ii):** reduce cloud/shadow scores within a few pixels of permanent water (pre-storm water mask from the before image) — directly addresses flood/shadow confusion along channels.
- **Uncertainty output (vi):** expose the membership-variance analogue (e.g. RF class-probability variance in `CloudSpotter`) as an uncertainty map; smooth uncertain pixels toward certain neighbours.
- **Scoring:** a 3-px (≈ 1.5 m at 0.5 m; scale it: their 3 px = 90 m) edge buffer excluded from commission is a published precedent for not scoring the cloud edge; report results with and without it.
- **Feasibility:** spatial rules are feasible on grey 0.5 m; the network needs 7 Landsat bands incl. thermal — not usable.

## 8. Key quotes
- "The core-cloud and thin-cloud classes, which were separate in the USGS data, were combined into a single cloud class." (p. 4910)
- "a three-pixel buffer around the areas labeled as cloud and cloud shadow in the evaluation masks was constructed" (p. 4914)
- "Both methods have a halo of commission error around cloud and cloud shadow objects that results from design decisions to reduce contaminated pixels by expanding those masks slightly." (p. 4919)
