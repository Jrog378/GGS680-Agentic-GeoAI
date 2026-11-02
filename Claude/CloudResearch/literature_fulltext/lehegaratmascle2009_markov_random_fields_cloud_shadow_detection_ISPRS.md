# Coder handoff: Le Hégarat-Mascle & André (2009), Use of Markov Random Fields for automatic cloud/shadow detection on high resolution optical images

- **Citation:** Le Hégarat-Mascle, S., & André, C. (2009). *ISPRS Journal of Photogrammetry and Remote Sensing* 64(4), 351–366. https://doi.org/10.1016/j.isprsjprs.2008.12.007
- **PDF:** `/Users/jusrogers/Masters/papers/lehegaratmascle2009_markov_random_fields_cloud_shadow_detection_ISPRS-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 3.62 MB; 16 pages (Read tool and pdfinfo) = published range 351–366; page-1 title, authors (Le Hégarat-Mascle, André) and journal 64 (2009) 351–366 match; "doi:10.1016/j.isprsjprs.2008.12.007" printed on p. 351. §6 Conclusions (pp. 363–364), Appendices A–B (pp. 364–366) and References (p. 366) present. PASS. (`file` metadata says 6 pages; ignored.)
- **Read:** pp. 351–366 in full (Read tool, page images), including Tables 1–6, Figs. 1–12 and Appendices A–B.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Three physical properties (p. 351): **P1** clouds and shadows are connected objects; **P2** "Knowing the geometry of the acquisition and the sun location, the image location of the shadow of a cloud is known, but for one parameter (the cloud altitude)"; **P3** "Each cloud and its associated shadow have the same shape and area (but for the deformations due to relief)". Flowchart: Fig. 8, p. 359.

1. **Cloud observation field (inter-calibration, §4.1.1–4.1.2, pp. 355–356).** Green and MIR reflectances of soil are correlated; cloud breaks that line. `y_diff = y_G − a·y_MIR − b` (eq. 16; "A similar approach was proposed in Zhang et al. (2002)", i.e. HOT-like). The line (a, b) is estimated robustly: for each MIR histogram class, the modal Green value (eq. 17), then a Viterbi (dynamic-programming) path through the 2-D (MIR, Green) histogram that maximises summed joint probability with a maximum jump K between neighbouring classes (eqs. 18–20); then a linear regression on that path.
2. **Pixel-level MRF for cloud/mist = hysteresis thresholding** (eqs. 5–7, Table 2, pp. 354–355). Data energies are piecewise constant in y_diff with low/high thresholds t_l^c, t_h^c; Potts-type clique term γ over 8-connected order-2 cliques. Provided `β_i > 0, 0 < β1 − β3 < γ < β2/n_connex`, local minimisation **is exactly hysteresis thresholding**, so β and γ need not be tuned (p. 354).
3. **Cloud thresholds from the image** (p. 357, Fig. 6): y_diff of clear pixels is symmetric about its median ≈ 0 because shadows hardly affect y_diff. `z_p` = p-percentile of y_diff (p = 0.1), `t_p = |z_p|`, `t_h^c = c_h·t_p`, `t_l^c = c_l·t_p`, c_h = 1.25, c_l = 0.95 (example: z_p = −17, t_p = 19, t_h = 24, t_l = 18).
4. **Mist vs cloud (property Π, §4.4.1, p. 358):** per detected object, from the share of its pixels with y_diff between t_l and t_h versus above t_h, compared with t_b = 10³ (the printed formula's layout is partly garbled in the PDF; read the page image before coding). Mist objects are not used for shadow validation.
5. **Shadow direction** (eq. 21, Fig. 5, p. 357): `tan θ = −(sin φα tan φβ + sin φω tan φμ) / (cos φα tan φβ − cos φω tan φμ)` with sun azimuth φα, sun incidence φβ, view angle φμ, orbit tilt (π/2 − φω). Only the direction is known; altitude (distance) is not.
6. **Approximate shadow location ω** (pp. 357–358): translate the cloud's binary mask B_C along θ in steps i; ω = B_C(θ, ĩ) with `ĩ = argmin_i mean MIR reflectance over B_C(θ, i)` (pixels of the cloud itself excluded). Search domain excludes translations that re-select a shadow already given to another cloud; clouds processed in **decreasing size** order.
7. **Shadow shape: pixel MRF = region growing** (eqs. 8–10): MIR band only; germ = pixels in ω below t_l^sh; growth to neighbours below t_h^sh; `t_l^sh = y_min(ω)`, `t_h^sh = y_min(ω) + c_sh·σ(ω)`, c_sh = 1.
8. **Object-level MRF = mutual validation** (eqs. 11–15, Table 3, Fig. 7, p. 355, 358): for cloud R_c and shadow R_sh, with n_sh (shadow only), n_c (projected cloud only), n_c∩sh (both): predicate H true if `n_sh/n_c∩sh < t_v` and `n_c/n_c∩sh < t_v`, t_v = 0.75. If not validated, **both** cloud and shadow are removed. "cloud and shadow are valid by default and they may be invalidated only if H predicate can be estimated … H is true by default if it cannot be estimated. It allows dealing with the cases where a cloud masking a shadow prevents the mutual validation and the cases where cloud or shadow is outside the image" (p. 355).
9. **Six parameters, fixed for all 39 images:** (p, c_h, c_l, c_sh, t_b, t_v) = (0.1, 1.25, 0.95, 1, 10³, 0.75) (p. 358).

## 2. Inputs, outputs, data needs
- SPOT4 HRVIR, 20 m, green/red/NIR/MIR reflectance; cloud uses Green + MIR, shadow uses MIR only (p. 355).
- Acquisition geometry: sun azimuth and elevation, view angle, orbit tilt.
- 39 AMMA images (Benin, Mali, Nigeria, 2005–2006, Table 1); "ground truth" = photo-interpreted masks (p. 352).
- Output: cloud, mist and shadow masks.

## 3. Quantitative results (cloud only)
- MRF over 39 images (p. 359–360, Fig. 10): mis-detection rate B/(B+D) median **8.33%** (Q1 2.33%, Q3 12.23%); false-alarm rate vs clear pixels median 0.0% (Q3 0.0016%); false-alarm rate vs detections median **8.47%** (Q1 0.16%, Q3 100%, the 100% being clear images where a small cloud was detected).
- Simple threshold at (t_h + t_l)/2 (Table 5): mis-detection median 17.7%, false alarms vs detections median 54.0% → "The proposed method mainly is efficiently reducing the false alarms" (p. 360).
- Sensitivity (Table 6): ±10% on each parameter changes error rates mostly by < 1%; "the shadow thresholding being the most critical parameter" (p. 361).
- **Shadows were not scored:** "even if we have not performed quantitative evaluation of the algorithm performance on shadow" (p. 363).
- Marked Point Process alternative (5 images only): fewer mis-detections, more false alarms, ~1000× slower, 12 parameters (pp. 361–363).
- Residual errors: false alarms on bright areas whose missing shadow was excused by the scene border or masking; misses = small clouds over bright soil (p. 359).

## 4. Stated limitations
- Object level cannot recover a cloud missed at pixel level (fixed node count) (p. 362).
- Relief deforms shadow shape; small clouds and bright fields/buildings create false shadow associations (p. 358).
- MIR is required for shadow; Green–MIR for cloud.

## 5. How to apply to our pipeline
- **Shadow pairing at 0.5 m (evidence 02 §6, K4, C3):** the paper's geometry needs only sun azimuth/elevation and view angles, which Maxar metadata gives per image. θ from eq. 21; distance unknown, so search along θ. At 0.5 m a cumulus at 1–2 km altitude and ~45° sun casts its shadow ~1–2 km away = 2,000–4,000 px, larger than one SN8 tile (1300 px); the search must run on a mosaic of neighbouring tiles, not per tile.
- **The paper's default answers our "shadow outside the tile" worry:** H defaults to true (cloud kept) when the shadow cannot be checked. So mutual validation only *removes* cloud/shadow pairs that disagree; it never requires the pair. Adopt the same rule: keep unpaired clouds, use pairing only to veto bright-roof false clouds that have no shadow where one should be (and is in view).
- **Hysteresis = MRF:** our cloud gate's single cut + blob filter could become hysteresis thresholding on the dark-rise map with thresholds set from the clear-pixel distribution (t_p = |p-th percentile below the median|, t_h = 1.25 t_p, t_l = 0.95 t_p), the paper's exact rule. This is a cheap arm; the paper shows hysteresis halves misses and cuts false alarms vs a single mid threshold (Table 5).
- **Shadow mask on RGB:** no MIR; use the darkest translated-mask search on the after-date grey or dark-channel *drop* relative to before (two-date), then region growing with t_l = min(ω), t_h = min(ω) + σ(ω). Flood water is also dark: require the candidate shadow to keep texture (before/after local std ratio) — our own addition, untested.
- **Inter-calibration idea:** the Viterbi-on-modal-values robust line fit (eqs. 17–20) is an alternative robust estimator for our two-date tone line (before vs after), resistant to cloud points.

## 6. Key quotes
- "Knowing the geometry of the acquisition and the sun location, the image location of the shadow of a cloud is known, but for one parameter (the cloud altitude)" (p. 351)
- "H is true by default if it cannot be estimated. It allows dealing with the cases where a cloud masking a shadow prevents the mutual validation and the cases where cloud or shadow is outside the image." (p. 355)
- "the local minimization of the global energy corresponds, in terms of label decision, to a threshold with hysteresis" (p. 354)
- "The proposed method mainly is efficiently reducing the false alarms" (p. 360)
- "even if we have not performed quantitative evaluation of the algorithm performance on shadow" (p. 363)
