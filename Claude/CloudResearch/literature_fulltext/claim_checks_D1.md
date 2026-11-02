# Claim checks, batch D1 (seven GMU downloads against our notes)

Compiled by Claude (AI), 2026-10-30. Every place our notes cite one of these seven papers (grep on author/year in
`evidence/*.md` and `literature_fulltext/claim_checks_*.md`) is checked against the full text. Verdicts: **verified**,
**corrected** (the paper says something different; the correction is given), **superseded** (a read-depth or
"paywalled" note that is now out of date), or **addition** (something the full text adds that matters for coding).
Page numbers are the journal's. No evidence file or earlier claim-check file was edited.

## Du, Teillet & Cihlar 2002 (RSE) — `du2002_radiometric_normalization_multitemporal_quality_control_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 l.150 | "pseudo-invariant features chosen statistically, with PCA fits and quality control, for land-cover change detection" | **corrected (mechanism):** PCA is used to *select* PIFs (pixels within ±l of the two-date major axis) and for QC (major-axis slope SL ≈ 1). The normalisation itself is **mean/SD matching on the PIFs**, `gain = σ_ref/σ_j`, `offset = Q̄_ref − gain·Q̄_j` (eq. 17), not a PCA fit. "Statistically" still means analyst-tuned thresholds, difference limit and l, iterated until r ≥ .9 and SL ≈ 1. Change-detection purpose verified | pp. 126–128, eq. 17 p. 127 |
| 2 | 05 l.28 | Anchor: "PIF normalisation with quality control for change detection" | verified | pp. 123, 127–128 |
| 3 | 10 l.74, l.260 | Normalisation experts "normalise on time-invariant pixels" | verified | p. 124 (PIF assumptions), p. 126 |
| 4 | 10 l.100 (row 2) | Our all-clear-pixel quantile curve is "Partly" supported | verified "Partly", and narrower: Du's fit is **linear and global** ("the linear effects are spatially homogenous across the whole image"); nothing supports a nonlinear curve | pp. 124, 126 |
| 5 | 05 l.204 | Du 2002 is a source for the windowed (local) invariant-pixel loop | **corrected (scope):** Du assumes spatially homogeneous linear effects and fits one gain/offset per band per image; windowing is our extension. What does transfer: the acceptance rule "If a linear correlation coefficient is less than .9, the data set is not selected as PIFs" | p. 126, p. 127 |
| 6 | — | (not in notes) | addition: **water is removed before the fit** "because they can change quickly and independently of land cover change"; PIF assumption 4: "The consistently changed targets are not the majority of targets in each scene" — both bear directly on flooded tiles | p. 126, p. 124 |
| 7 | — | (not in notes) | addition: result |1 − SL| fell 4.0→0.9%, 11.2→0.9%, 7.4→1.6% (TM 3/4/5) with 0.7 px misregistration | pp. 128–132, Table 1 |
| 8 | 05 l.150; claim_checks_A l.89 | Read depth "abstract, NRCan record; needs GMU" / "paywalled, not checked" | superseded: full text read, pp. 123–134 | — |

## Zhang, Guindon & Cihlar 2002 (RSE, HOT) — `zhang2002_haze_optimized_transformation_thin_cloud_landsat_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 21 l.126 | Fragment: HOT developed "for the detection and characterization of haze/cloud spatial distributions in Landsat scenes"; a method to "radiometrically compensate visible band imagery" | verified (abstract wording exact) | p. 173 |
| 2 | 21 l.129; claim_checks_A; claim_checks_C | Via Fmask: HOT "is built empirically from regression of DN values from clear-sky pixels" | verified: `HOT = B1 sinΘ − B3 cosΘ` on "digital numbers"; the CL comes from regressing TM1 and TM3 DNs of subimages in the clearest region. Addition: that region is chosen **by visual inspection**, one CL per scene | eq. 1 p. 175; §5.1 p. 179 |
| 3 | 21 l.130 | "So it was designed on DNs, not reflectance" | verified (MODTRAN radiances were converted to DN with Landsat-5 gains/offsets for the design) | p. 175 |
| 4 | 10 refs #29 | "needs blue and red, so not used for greyscale" | verified (TM1, TM3). Addition: "the green and red bands can be employed" for MSS, so any two visible bands with different haze response | pp. 174–175, p. 186 |
| 5 | 20 l.52 (HOT arm c) | "The clear line red = k·blue + b is fitted per tile on the least-hazy pixels … HOT = B sinθ − R cosθ, centred on the fit pixels" | verified for the equation. **corrected (scope):** the paper fits one CL per *scene* on an analyst-chosen clear region and leaves HOT uncentred (clear area ≈ 30, haze 30–40); per-tile automatic fitting and centring are our adaptations | eq. 1 p. 175; p. 179; p. 182 |
| 6 | 20 l.52 | Caveat "this is 8-bit display RGB, not reflectance" | addition: the original HOT is DN-based (8-bit TM), so the reflectance caveat belongs to Fmask's TOA version, not to Zhang. The caveat that remains is a non-linear display stretch | p. 175 |
| 7 | 20 l.52 | "Water, shadow and bright roofs also move HOT" | **partly verified:** the paper lists snow and **shadows over snow**, some **water bodies** ("sediment in shallow water or … wind-induced waves") and bare soil (low HOT). It does **not** list bright urban: it says HOT is "much less sensitive to these targets" (building complexes, roads, bare ground) than the 4th Tasselled Cap. "Bright roofs" comes from Fmask/Qiu 2019, not Zhang | p. 179 |
| 8 | 20 l.125 | `2_14_51`: "a flooded road (HOT rises over turbid water)" | consistent with the paper's water explanation (sediment, waves); the paper's fix is a NIR (TM4) water mask, which we lack | p. 179 |
| 9 | claim_checks_A (Fmask p. 84) | Clear-line idea "fails when the surface reflectance is bright, as is the case for rocks, snow, ice, sand" | **corrected (attribution):** Zhang reports snow only; bare soil gives a *low* HOT. Addition: haze trajectories "monotonically decrease for surface classes of increasing absolute reflectance", so HOT is not fully surface-insensitive (second-order effect) | p. 176, p. 179 |
| 10 | 10 l.353; 21 l.699 | "The HOT removal step (only the detection side was read)" | superseded: removal read. It is a dark-object subtraction stratified by HOT level: per band, `Δ(h) = lowerbound(h) − lowerbound(clear)` from histograms in HOT steps of 1, subtracted per pixel; assumes "similar dark targets are present under all haze conditions". Haze = 10.8–16.9% of window means in the test | §5.3–5.4 p. 182; p. 185 |

## Schott, Salvaggio & Volchok 1988 (RSE) — `schott1988_radiometric_scene_normalization_pseudoinvariant_features_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 l.74, l.260; 21 l.280 | Normalisation on pseudo-invariant pixels | verified. PIFs are man-made: "road surfaces, rooftops, parking lots"; segmented by NIR/red ratio AND a SWIR threshold (urban ON, vegetation and water OFF); gain = σ1/σ2, offset from PIF means (eq. 8) | pp. 4–6 |
| 2 | 10 l.100 (row 2) | "Partly" support for our quantile matching | verified "Partly". Addition: Schott computed histogram matching on PIFs only as a **diagnostic**, found it "nearly identical" to the linear form (≤ 1 DC visible/NIR, up to 2.8 DC longer wave) and used the linear transform "exclusively"; segmentation accepted if mean difference < 2 DC in all bands | pp. 7–8, 12, Table 1 |
| 3 | 21 l.588 (fix 5) | Strong in-principle support for invariant-pixel two-date normalisation | verified, with a **flood-specific caveat (addition):** "the transformation should only be attempted when the impervious surfaces that predominate the PIF population can be assumed to be reasonably dry … surface moisture can remain present for several days following any sort of precipitation". A post-hurricane after date breaks this for roads and roofs | p. 14 |
| 4 | — | (not in notes) | addition: residual ≈ 1 reflectance unit (TM, urban Rochester); 0.42–0.62 %R visible for 10 m air photos; robust to 2:1 resolution and to a rural subscene with few PIFs | pp. 12–14, Tables 2–5 |
| 5 | 10 refs #22; 21 refs #31; claim_checks_A l.103 | Read depth "Metadata"; RIT record gives pp. 1–14 | superseded: full text read. Pages are 1–16 (RIT's 1–14 is wrong); the PDF's 17th page is an unnumbered colour plate (Fig. 6) between pp. 14 and 15 | — |

## Lin, Lin, Lee & Chen 2015 (ISPRS JPRS) — `lin2015_radiometric_normalization_cloud_detection_invariant_pixels_ISPRS`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 l.165 | TLDR: "weighted PCA picks invariant pixels from a cloudy time series, then normalises the dates" | verified: weights = scatterplot point density × spectral similarity (ED, spectral angle, spectral correlation), CDF-enhanced; invariant = within ±d of the weighted major axis; correlation > 0.75 (reference pixels) / > 0.9 (PIFs); normalisation by Du 2002's mean/SD equations | eqs. 7–12 pp. 110–111; eqs. 1–3 p. 108 |
| 2 | 05 l.166; 10 l.347 | "the closest published match to our prototype" | verified as structure (normalise on invariant pixels → cloud = rise against a clear reference). **Caveats (addition):** it needs a **time series** (6–24 images) to compose references; its cloud test is a **blue ToA-reflectance rise > 0.03** (Hagolle 2010), not a dark-channel rise; with two dates the reference collapses to the before image | p. 109, eqs. 13–15 pp. 111–112 |
| 3 | 10 l.91 | Quote: multi-temporal cloud detection "mainly relies on the successful radiometric correction/normalization and reference image quality" | verified wording; **corrected (context):** the sentence describes *previous* methods (the problem the paper sets out to solve), not a finding | p. 107 (abstract) |
| 4 | 10 l.91 | "builds the reference from weighted invariant pixels" | verified: time-gap and temporal-coherence weights, bilinear fill for empty pixels | eqs. 13–14 p. 111 |
| 5 | 10 l.105 (row 3) | Lin is a source for "Clear references from other dates, for cloud detection and for aerosol (haze) correction" | **corrected:** Lin uses the clear reference for **cloud detection only**; it does no haze/aerosol correction (that part is Hagolle) | pp. 111–112, 116 |
| 6 | claim_checks_A l.149 | Abstract facts: Landsat-7 ETM+ time series; F-measure gains of 1.1–6.9% | verified; the gains are percentage points against an **existing cloud-free reference image**: 92.0 vs 90.9 (stable area II), 87.9 vs 81.0 (area I with significant land-cover change) | p. 107; Table 3 p. 116 |
| 7 | 05 l.204 | Lin is a source for the windowed invariant-pixel loop | **corrected (scope):** Lin fits per image pair, globally; windows are ours. Limitation it states: "limited when images are almost covered by clouds … only a few invariant pixels can be extracted" (same abstain logic as our design) | p. 116 |
| 8 | 21 l.588 (fix 5) | Strong in-principle support | verified (invariant-pixel normalisation that needs no cloud/water mask; major-axis RMSE 2.55 vs ≥ 6.40 for the competitor) | Table 2 p. 114 |
| 9 | 05 l.28 "(TLDR only)"; 10 refs #15 "abstract via a search summary"; 21 l.304; claim_checks_A l.149 | Read depth / paywalled | superseded: full text read, pp. 107–117 | — |

## Le Hégarat-Mascle & André 2009 (ISPRS JPRS) — `lehegaratmascle2009_markov_random_fields_cloud_shadow_detection_ISPRS`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §6 l.26 | Pairs a shadow with its cloud through sun and view geometry | verified: P2 "the image location of the shadow of a cloud is known, but for one parameter (the cloud altitude)"; direction θ from sun azimuth/incidence, view angle and orbit tilt (eq. 21); distance found by sliding the cloud mask along θ to the darkest mean MIR | p. 351; eq. 21 p. 357; pp. 357–358 |
| 2 | claim_checks_A l.700 (snippet) | Same shape and area; two-level (pixel/object) MRF on SPOT HRVIR | verified (P3; pixel graph + object graph; SPOT4 HRVIR 20 m, 39 AMMA images) | pp. 351–352, 355 |
| 3 | 02 §6 "my read" | At 0.5 m a cumulus shadow can fall outside the tile, so geometric pairing fails | addition: the paper anticipates this: "H is true by default if it cannot be estimated … the cases where cloud or shadow is outside the image". Pairing only **vetoes** mismatched pairs; it never requires the shadow in view | p. 355 |
| 4 | — | (not in notes) | addition: pixel-level MRF minimisation = **hysteresis thresholding**, thresholds from the clear-pixel distribution (p = 0.1, c_h = 1.25, c_l = 0.95); cloud mis-detection median 8.33%, false alarms vs detections median 8.47%, vs 17.7% / 54.0% for one threshold | p. 354, p. 357, pp. 359–361, Table 5 |
| 5 | — | (not in notes) | addition: **shadow accuracy was never scored** ("even if we have not performed quantitative evaluation of the algorithm performance on shadow"); needs MIR for shadow | p. 363, p. 355 |
| 6 | claim_checks_A l.700 | "paywalled, not read" | superseded: full text read, pp. 351–366 | — |

## Chavez 1988 (RSE) — `chavez1988_improved_dark_object_subtraction_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 21 l.232–238 | Quotes: scattering "highly wavelength-dependent … correlated"; haze values "spectral band dependent"; "a relative atmospheric scattering model" predicts all bands from one starting band; "normalizes the predicted haze values for the different gain and offset parameters" | verified (abstract wording exact) | p. 459 |
| 2 | 21 l.70 | "Haze is wavelength-dependent (Chavez 1988)" | verified: λ^−4 (very clear) … λ^−0.5 (very hazy); real clear atmospheres λ^−2 to λ^−0.7 | pp. 466–467 |
| 3 | 21 l.293 | "Chavez's gain/offset normalisation cover[s] linear rescaling only" | verified: `DN = GAIN·Rad + OFFSET` | eq. 1 p. 471 |
| 4 | 21 l.333 (arm 3-iv) | "Chavez-style relative-scattering constraint (blue > green > red)" | **corrected:** the constraint is a **power law λ^−k in radiance units** (k from 0, "complete scattering (e.g., complete cloud cover)", to 4), then mapped to DN by each band's gain/offset. In DN the ordering is **not** guaranteed: "because of the gain differences it is possible for the final haze value for a longer wavelength band … to have a larger value than a shorter wavelength band". On display RGB with unknown gains, apply the power law before any DN mapping, and include k = 0 (grey) for cloud | p. 466; p. 475 (Table 4 note); p. 477 |
| 5 | 21 l.592 (fix 9) | "Medium" support for band-linking | verified "Medium"; note the paper's evaluation is **visual only** (Saudi Arabia composites vs field photos); constant haze per image ("assumes a constant haze value throughout the entire image, which is often not the case") | pp. 460, 468–470 |
| 6 | claim_checks_C #6 (Ma 2022) | "γ ranges from 0 to 4" citing Chavez 1988 | verified: "this relationship can vary from λ^0 to λ^−4" | p. 466 |
| 7 | — | (not in notes) | addition: local histograms over-correct ("a real minimum or dark-object may not be found"); TM 5/7 predictions too high, use 0–1 DN | p. 466, p. 476 |
| 8 | 21 l.26, l.35, l.232, refs #4 | Read depth "Abstract (USGS record)" | superseded: full text read, pp. 459–479 | — |

## Song, Woodcock, Seto, Lenney & Macomber 2001 (RSE) — `song2001_classification_change_detection_landsat_atmospheric_correction_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 21 l.275–279 | Quotes: "atmospheric correction is unnecessary as long as the training data and the data to be classified are in the same relative scale"; "corrections are mandatory to put multitemporal data on the same radiometric scale"; "More complicated algorithms do not necessarily lead to improved performance"; "Simple dark object subtraction… or relative atmospheric correction are recommended" | verified (abstract wording exact; conclusions repeat it) | p. 230; p. 242 |
| 2 | 21 l.76 | "Song et al. (2001) state that relative correction is enough for change detection, provided both dates are 'in the same relative scale'" | **corrected (quote misapplied):** "in the same relative scale" is the condition under which *no correction at all* is needed (training data vs data to be classified). The support for relative correction is separate: the Ridge Method ranked **3rd of 9** (sum of ranks 38.5 vs DOS3 29.5, DOS1 34, raw 84.5) and is "a viable option"; and "accurate estimation of surface reflectance is not necessary" | p. 230, p. 232; Table 5 p. 240; p. 242 |
| 3 | 21 l.588 (fix 5) | Song 2001 gives strong in-principle support for invariant-pixel (IR-MAD-style) two-date normalisation | **corrected:** Song's relative method is the **Ridge Method on all pixels** (dense ridge of the two-date density plot), which "circumvents the difficulty in identifying PIFs" — not invariant-pixel selection. It supports relative normalisation in general, and warns that "substantial changes … such as … land use/land cover change, may compromise the utility of the Ridge Method"; the authors **excluded the substantially changed area** when building the plots. For a flood, that supports excluding changed pixels, and it is the closest published analogue of our all-clear-pixel tone curve | p. 235 |
| 4 | — | (not in notes) | addition: image differencing needs normalisation when the method "assume[s] a zero mean for stable classes"; with empirical thresholds the offset is absorbed | pp. 232–233 |
| 5 | — | (not in notes) | addition: when training and testing come from the same image, all corrections including raw give the same accuracy | Table 6 p. 241 |
| 6 | 21 l.26, l.275, l.701 | Read depth "Abstract" (UNC CPC bibliography) / "read … in full (gap 3b)" | superseded: full text read, pp. 230–244 | — |

## Summary of corrections
1. **Du 2002:** the fit is PIF mean/SD matching, not a PCA fit; PCA selects PIFs and checks quality. Global, not local (pp. 126–127).
2. **Zhang 2002:** one visually chosen clear line per scene, uncentred HOT; the paper does not list bright urban as a HOT failure (it lists snow, shadow over snow, sediment-laden water, low HOT over bare soil) (pp. 175, 179, 182).
3. **Schott 1988:** PIFs must be dry; post-storm wet roads and roofs break the method (p. 14).
4. **Lin 2015:** the "mainly relies on" quote describes prior methods; the reference is for cloud detection, not haze correction; the method is global and needs a time series (pp. 107, 111–112, 116).
5. **Le Hégarat-Mascle 2009:** clouds without a visible shadow are kept by default; shadows were never scored (pp. 355, 363).
6. **Chavez 1988:** band-linking is a λ^−k power law in radiance; DN ordering blue > green > red is not guaranteed (pp. 466, 475).
7. **Song 2001:** "same relative scale" is about when no correction is needed; its relative method is a whole-image density ridge, not invariant pixels, and it was used with the changed area excluded (pp. 230, 235, 240).
