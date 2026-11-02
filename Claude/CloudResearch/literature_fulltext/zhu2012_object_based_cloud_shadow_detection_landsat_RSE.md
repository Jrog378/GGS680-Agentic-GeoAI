# Coder handoff: Zhu & Woodcock (2012), Object-based cloud and cloud shadow detection in Landsat imagery (Fmask 1)

- **Citation:** Zhu, Z., & Woodcock, C. E. (2012). *Remote Sensing of Environment* 118, 83–94. https://doi.org/10.1016/j.rse.2011.10.028
- **PDF:** `/Users/jusrogers/Masters/papers/zhu2012_object_based_cloud_shadow_detection_landsat_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF already on disk, copied from `/Users/jusrogers/Masters/GGS680/references/Zhu & Woodcock 2012. Object-based cloud and cloud shadow detection in Landsat imagery.pdf` (original left in place)
- **Validation:** PDF, 12 pages (Read tool and pdfinfo) = published range 83–94; title/authors/DOI match Crossref; Discussion and conclusion (§5) and references present. PASS. (`file` reports "13 pages" from metadata; ignored, as the checker rules say.)
- **Read:** pp. 83–94 in full (text extraction; equations legible apart from glyph substitutions ¼ = "=", b = "<"); reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm, step by step
Inputs are TOA reflectance of TM/ETM+ bands 1, 2, 3, 4, 5, 7 (blue, green, red, NIR, SWIR1, SWIR2) and band 6 brightness temperature BT in °C (from LEDAPS) (p. 84).

**Pass one: Potential Cloud Pixels (PCP)** (pp. 85–86)
1. Basic test (eq. 1): `B7 > 0.03 and BT < 27 and NDSI < 0.8 and NDVI < 0.8`; `NDSI = (B2 − B5)/(B2 + B5)`, `NDVI = (B4 − B3)/(B4 + B3)`.
2. Whiteness (eq. 2): `MeanVis = (B1 + B2 + B3)/3`; `Σ_{i=1..3} |(Bi − MeanVis)/MeanVis| < 0.7`. 0.7 chosen by sweeping 0.5–0.9 on the 142 reference scenes (Fig. 1; accuracy varies only 96.2–96.45%).
3. HOT test (eq. 3): `B1 − 0.5·B3 − 0.08 > 0` (TOA reflectance version of Zhang et al. 2002's haze-optimised transform; "especially helpful for separating haze and thin cloud from clear-sky pixels"; also catches rocks, turbid water, snow).
4. B4/B5 test (eq. 4): `B4/B5 > 0.75` (ACCA used 1; lowered to keep thin cloud; removes bright rock).
5. Water test (eq. 5): `(NDVI < 0.01 and B4 < 0.11) or (NDVI < 0.1 and B4 < 0.05)`.
6. `PCP = Basic ∧ Whiteness ∧ HOT ∧ B4/B5` (eq. 6). If PCP > 99.9% of the scene, PCP is the final mask (pass two needs ≥ 0.1% clear, "approximately 50,000 pixels").

**Pass two: cloud probability from the scene's own clear pixels** (pp. 86–87)
7. Water: clear water = Water ∧ B7 < 0.03 (eq. 7); `T_water` = 82.5th percentile of their BT (eq. 8); `wTemperature_Prob = (T_water − BT)/4` (eq. 9; 4 °C scale, may exceed 1); `Brightness_Prob = min(B5, 0.11)/0.11` (eq. 10); `wCloud_Prob = wTemp × Brightness` (eq. 11); cloud over water if > 0.5.
8. Land: clear land = ¬PCP ∧ ¬Water (eq. 12); `T_low, T_high` = 17.5th and 82.5th percentiles of clear-land BT (eq. 13; if clear land < 0.1% of scene, use all clear pixels); `lTemperature_Prob = (T_high + 4 − BT)/(T_high + 4 − (T_low − 4))` (eq. 14).
   - `Variability_Prob = 1 − max(|mNDVI|, |mNDSI|, Whiteness)` (eq. 15); mNDSI = 0 if B2 saturated and B5 > B2; mNDVI = 0 if B3 saturated and B4 > B3.
   - `lCloud_Prob = lTemperature_Prob × Variability_Prob` (eq. 16).
   - **Scene-based land threshold (eq. 17): `Land_threshold = 82.5th percentile of lCloud_Prob over clear-land pixels + 0.2`** (0.2 from sensitivity analysis).
9. Potential cloud layer (eq. 18): `(PCP ∧ Water ∧ wCloud_Prob > 0.5) ∨ (PCP ∧ ¬Water ∧ lCloud_Prob > Land_threshold) ∨ (lCloud_Prob > 0.99 ∧ ¬Water) ∨ (BT < T_low − 35)`.
10. **Spatial clean-up:** "sets a pixel to cloud if five or more pixels in its 3-by-3 neighborhood are cloud pixels; otherwise, the pixel stays clear" (p. 87).

**Shadow and snow layers** (p. 87)
11. Potential shadow (eq. 19): flood-fill (morphological reconstruction by erosion; Soille) of B4; `filled B4 − B4 > 0.02`. Scene border filled with the 17.5th percentile of clear-land B4 so edge shadows are caught.
12. Potential snow (eq. 20): `NDSI > 0.15 ∧ BT < 3.8 ∧ B4 > 0.11 ∧ B2 > 0.1`.

**Object-based cloud–shadow match** (pp. 87–88, Fig. 3)
13. Cloud objects = 8-connected components of the potential cloud layer.
14. Base-height range per object (eq. 21): `H_base ∈ [max(0.2, (T_low − 4 − T_base)/9.8), min(12, T_high + 4 − T_base)]` km (dry lapse 9.8 K/km for the lower bound; a reduced 1 K/km for the upper bound, to catch thin-cloud shadows).
15. Cloud-base BT (eq. 22): object assumed round, `R = sqrt(N/(2π))`; if R ≥ 8, `T_base` = the `100·(R − 8)²/R²` percentile of the object's BT; else min BT. Edge pixels warmer than T_base are set to T_base (eq. 23) ("8 cloud edge pixels are influenced by the neighboring warm surface"). Top height `H_top = H_base + 6.5·(T_base − T_top)` (eq. 24; wet lapse 6.5 K/km).
16. Iterate H_base from min to max, project each object along the sun–view direction, similarity = overlap of the projected shadow with (potential cloud ∪ potential shadow) / projected shadow area, cloud object itself excluded. Continue while similarity increases or stays ≥ 98% of the maximum; accept if max similarity > **0.3** (0.2–0.5 give similar results).
17. Matched shadow is **buffered by 3 pixels (8-connected)** "to fill those small holes", then intersected with the potential shadow layer (p. 88).
18. **Cloud objects < 3 pixels are removed** from the cloud mask and not matched ("most of them are misidentification of small bright cold noncloud pixels", p. 88).
19. Label priority: cloud > shadow > snow.

Note: **this 2012 paper does not buffer/dilate the cloud mask.** The only buffer is on matched shadows (step 17). Cloud dilation enters in Zhu, Wang & Woodcock 2015 (see that handoff).

## 2. Inputs, outputs, data needs
- Input: one Landsat TM/ETM+ L1T scene as TOA reflectance + BT (thermal essential: temperature probability, height range). Sun zenith/azimuth and view angle for shadow geometry. No reference date.
- Output: per-pixel labels cloud / shadow / snow / clear and a continuous cloud-probability layer (users may pick their own cut, e.g. 50%, p. 92).
- Runtime: 0.5–6 min per scene, Matlab 1.6.0, 8-core Linux (p. 92).

## 3. Quantitative results to compare against (pp. 89–92)
- Reference: ACCA set, 212 scenes, 9 latitude zones, USGS analysts' manual Photoshop masks; 70 excluded for poor masks → **142 scenes** for cloud; **26** for shadow. Inter-analyst difference ~7% (11 scenes, 3 analysts).
- Cloud overall accuracy **96.41% (SD 3.2)** vs ACCA pass one 84.8% (SD 11.9).
- Cloud producer's **92.1% (SD 13.3)** vs 72.1% (SD 26.5); user's **89.4% (SD 9.8)** vs 91.8% (SD 12.3). PA/UA not computed for scenes < 5% cloud.
- Scene cloud %: R² > 0.99, slope 1.00, intercept 0.83%, RMSE 3.25% (ACCA: R² 0.95, slope 0.95, intercept 0.39%, RMSE 6.56%).
- Shadow PA > 70%, UA ≈ 50% (scenes with < 1% shadow excluded); over-estimation "mainly caused by the 3 pixels buffered".
- Note eq. 27 in print defines user's accuracy with "omission" in the denominator; it must be commission (typo in the paper; eq. 29 for shadow has commission).

## 4. Stated limitations (p. 92)
- Misses cloud that is "both thin and warm" — "usually thin and warm 'clouds' are actually haze or aerosols and they can be further removed by atmospheric correction".
- Commits "very bright and cold land features (salt pans, cold snow etc.)".
- "as Fmask uses a scene-based threshold … it may not work well for some images with very complex surface reflectances."
- Would improve with land/water mask, DEM, multi-temporal data. Open question: should smoke, thick aerosol, haze be in the cloud mask?

## 5. How to apply to our pipeline
- **Spectral tests: not transferable.** We have no thermal, NIR or SWIR, and Maxar 8-bit visual product is not TOA reflectance, so eqs. 1, 3, 4, 5 and the thresholds are meaningless on our tiles. Whiteness (eq. 2) can be computed on our RGB, but only if we stop collapsing to grey; it would be a new cue for `sn8_cloudspot.classical_cues` (thresholds must be learned on HRC_WHU, not copied).
- **Scene-learned threshold (eq. 17) → `sn8_clouds.cloud_thresholds` / `sn8_cloudsym.change_gate`:** Fmask's cut = 82.5th percentile of the score over the scene's own clear pixels + a margin. Our Otsu cut (71 on dark rise) is learned across training tiles. An arm: per tile, cut = q-th percentile of dark rise over pixels already called clear + margin; Fmask's q = 82.5 is a starting value, margin to be tuned on development tiles. Fmask itself names the weakness: a single scene-wide threshold on complex surfaces.
- **Minimum object size (step 18) → `DARKREF_MIN_CLOUD_M2` = 2,500 m²:** Fmask's is a noise rule (< 3 px of 30 m = < 2,700 m²), for bright cold non-cloud. Our value is a roofs/debris rule. The paper supports having a size floor, not the number.
- **3 × 3 majority (step 10):** cheap pre-blob clean-up of the dark-rise mask before `_keep_blobs`; at 0.5 m this would have to be scaled (e.g. majority over a window of comparable ground size) — our own adaptation.
- **Shadow (steps 11, 13–17):** flood-fill on a dark band works on grey too (`skimage.morphology.reconstruction(seed, image, method='erosion')`, threshold on fill − image); at 0.5 m every building and tree shadow is a regional minimum, so it must be gated by geometric match to a detected cloud object using the Maxar sun azimuth/elevation and off-nadir (check the SN8 metadata for these). Cloud heights are unknown without thermal: iterate over a height range and keep the best overlap (similarity > 0.3, stop below 98% of max) exactly as Fig. 3.
- **Reporting:** follow p. 89 — report producer's accuracy as primary; omission costs more than commission for change detection. Supports our abstain-when-unsure rule.
- **No cloud buffer here:** do not cite this paper for the 20 m fade or for dilating the gate; cite Zhu et al. 2015 (cloud dilation) and treat Fmask 2012's 3-px buffer as a *shadow* hole-filling step.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** the algorithm as published: not feasible. The design patterns (loose pass then scene-learned cut, object filtering, geometric shadow match, PA-first reporting): feasible. Our two-date setting is actually better placed than Fmask, which lists multi-temporal data as the missing ingredient (p. 92).

## 6. Key quotes
- "The identification of thin semitransparent clouds is difficult as their signal includes both clouds and the surface underneath" (p. 83).
- "For cloud objects less than 3 pixels, Fmask excludes them from cloud mask and does not match cloud shadows for them as most of them are misidentification of small bright cold noncloud pixels." (p. 88)
- "Fmask buffers by 3 pixels in 8-connected directions for each of the matched cloud shadow pixel to fill those small holes." (p. 88)
- "If clouds or cloud shadows are missed they will greatly undermine future analyses like change detection or image classification. However if clear areas are masked as clouds or cloud shadows, the only consequence is a little lost data." (p. 89)
- "We think commission is better than omission in cloud detection" (p. 92).
- "usually thin and warm 'clouds' are actually haze or aerosols" (p. 92).
