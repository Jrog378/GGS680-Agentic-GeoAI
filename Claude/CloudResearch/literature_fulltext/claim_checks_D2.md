# Claim checks, batch D2 (GMU downloads of 2026-10-30, against full texts)

Compiled by Claude (AI), 2026-10-30. Each claim our notes make about a paper is checked against the full text and
marked **verified**, **corrected** (the paper says something different; the correction is given), **not found**, or
**addition** (something the full text adds that matters for coding). Page numbers are the journal's (article pages
for SCIS, JARS and IJGI). Sources searched: `CloudResearch/evidence/*.md` and `literature_fulltext/claim_checks_*.md`
(grep on author and year). No evidence file or earlier claim-check file was edited. All seven papers were read in full;
see each handoff in this folder for the pages read.

## You, Xu, Pan, Dong, Yang & Xia 2026 (Sci. China Inf. Sci.) — `you2026_change_aware_multitemporal_cloud_removal_SCIS`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev05 l. 18 | The methods that cope with change "(… You et al. 2026) add a near-date source to carry the change: … SAR" | verified, with precision: SAR is required on **every** date, including the target date; the change cue is the cosine similarity of SAR features between each date and the target (eq. 10) | pp. 4, 6, 8 |
| 2 | ev05 l. 109; claim_checks_A l. 833 | TLDR: "uses SAR to detect change, so that it can choose which other dates to use" | **corrected**: it does not choose dates. Auxiliary dates "are randomly selected from the remaining time steps" (SEN12MS-CR-TS) or are the AllClear neighbours. The SAR change map is turned into **soft per-location attention weights** over all given dates (L-TAE), and the weighted features are summed | p. 8; eqs. 10–12, pp. 6–7 |
| 3 | ev05 l. 108, l. 223 | Read level "TLDR only; needs GMU" / "read the abstract and method" | corrected (read level): full text read, 15 pp. | — |
| 4 | ev19 l. 54 | "uses multi-temporal SAR, by its keywords; its abstract is not in OpenAlex" | verified (keywords include "optical and SAR images, multi-temporal"); read level now full text | p. 1 |
| 5 | ev19 l. 192 | Input "Multi-temporal SAR + optical"; change-aware Yes; fits one grey band + clear before date: No (needs SAR) | verified. Inputs are Sentinel-2 + Sentinel-1 on every date. Without SAR the model drops to 29.84 dB, below its full 31.79 dB | p. 8; Table 3, p. 13 |
| 6 | ev19 l. 206 | "The only change-aware cloud removers need SAR or extra near-date images" | verified for this paper (its change cue is SAR-only, eq. 10) | p. 6 |
| 7 | ev19 l. 483 | Ref row: You, G., Xu, F., Pan, J., Dong, R., Yang, W., & Xia, G.-S. (2026), SCIS 69(3), DOI; "8.1 (year unverified)"; read "Metadata + keywords" | verified (authors, volume, issue, DOI); addition: article 132306, pp. 1–15; received 17 Mar 2025, published online 20 Jan 2026. JIF not checkable from the paper. Read level → full text | p. 1 |
| 8 | claim_checks_A l. 833 | Authors per OpenAlex: Guochu You, Fang Xu, Jun Pan, Runmin Dong (+ others) | verified; the others are Wen Yang and Gui-Song Xia (all Wuhan University except Dong, Sun Yat-sen) | p. 1 |
| 9 | — | (not in notes) | addition: the abstract's "about 2.0 dB" gain on SEN12MS-CR-TS is over UnCRtainTS (31.79 vs 29.76); over the best method in Table 1 (HDRSA-Net) it is 1.03 dB, SSIM tied at 0.903. The SAR change term is worth 1.63 dB (ablation). No significance tests; rapid change shown only qualitatively | Table 1, p. 9; Table 2, p. 10; p. 11 |

## Chen, Krajewski, Goska & Young 2017 (J. Hydrol.) — `chen2017_lidar_surveys_document_floods_2008_iowa_JHYDROL`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev19 l. 291; claim_checks_C l. 459 | *J. Hydrology* 553:338; read "Abstract"; "Claims not checked" | verified (553, 338–349); read level now full text | p. 338 |
| 2 | ev19 ll. 292–293 | "Lidar flown during the 2008 Iowa flood: water points classified, a water surface built, the bare-earth DTM subtracted" | verified, with addition: flown 19–20 June 2008, about 3.5 days after the 15 June crest, on the recession. Water points = elevations within channel level ± 2σ (σ = 0.09 m); 2 m natural-neighbour water surface; depth = surface − 2 m Iowa bare-earth DTM | pp. 339–346 |
| 3 | ev19 l. 294 | "Water-surface RMSE against high-water marks is 30 cm" | verified, with caveat: 22 HWMs; HWMs record the crest, and Fig. 9 compares them with the LiDAR profile **raised by 0.9 m** to crest stage | pp. 338, 344–345 |
| 4 | ev19 ll. 294–295 | "Extent agrees with SPOT at 72% (81% after removing isolated ponds)" | verified, with wording correction: the 72% is the index F = A/(A+B+C) (a critical-success / IoU-type score of the wet class), not percent agreement. SPOT was two days before the LiDAR | eq. 2, p. 344; p. 345 |
| 5 | ev19 l. 316 | "Accuracy is checked against … high-water marks (Zheng; Chen)" | verified; Chen also checks extent against the SPOT map and visually against aerial photos | pp. 344–347 |
| 6 | ev19 l. 317; ll. 404–405 | "Reported depth errors run from about 0.2 to 0.5 m"; the 0.5 m margin "follows the reported depth errors of 0.18–0.5 m (Cohen et al. 2019; **Chen et al. 2017**; Zheng et al. 2022)" | **corrected**: Chen reports **no depth error**. The 0.30 m is a water-surface profile RMSE against HWMs. The authors state: "an unsolvable weakness of our LiDAR survey … is the absence of data assessing the accuracy of height measurements of water points". 7% of residual (depth) pixels were negative and dropped. Remove Chen from the depth-error citation, or cite it as "water-surface RMSE 0.30 m vs HWMs" | pp. 346–347 |
| 7 | ev19 l. 426 | 3DEP 1 m DEM is "Used in Zheng et al. 2022 and Chen et al. 2017-type depth methods" | corrected (detail): Chen used the Iowa 2 m LiDAR bare-earth DTM (P-Library, ±18 cm, hydro-conditioned), not 3DEP 1 m. "Chen-type" is acceptable only as a method label | p. 342, p. 346 |
| 8 | ev19 l. 455 | Ref row: Chen, B., Krajewski, W. F., Goska, R., & Young, N. (2017), J. Hydrology 553, 338–349, DOI | verified | p. 338 |

## Kaufman 1984 (Applied Optics) — `kaufman1984_atmospheric_effect_spatial_resolution_surface_imagery_AO`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 255 | Applied Optics 23:3400; "context, NASA author"; read "Abstract" | verified (23(19), 3400–3408; NASA Goddard); read level now full text | p. 3400 |
| 2 | ev21 l. 256 | Photons reflected outside the field of view "are scattered by the atmosphere into the field of view (adjacency effect)" | verified | abstract, p. 3400 |
| 3 | ev21 ll. 257–258; l. 72; ll. 398–399 | "The 30-m resolution of the Landsat TM is reduce[d] to 100 m by a hazy atmosphere"; "one hazy atmosphere coarsened Landsat TM's 30 m resolution to 100 m" | verified, with scope: the 100 m is the resolution at which the TM+atmosphere MTF falls to **0.35**, for aerosol optical thickness 0.5 at 550 nm. At an MTF threshold of 0.5 the same case gives **830 m**. It is a threshold on a lowered high-frequency plateau, not a 100 m blur width | Table II, p. 3405; Fig. 9 |
| 4 | ev21 l. 258; l. 398 | He derives an "atmospheric modulation transfer function" | verified: normalised atmospheric MTF, eq. 9; absolute MTF, eq. 10 / Appendix A | pp. 3403–3404, 3407 |
| 5 | ev21 l. 72 | "The adjacency effect blurs as well as brightens" | verified in the paper's sense (transfer fraction ξ moves radiance between fields, reducing apparent resolution) | eqs. 1–3, p. 3401 |
| 6 | ev21 l. 429 (gap 5, "my read") | "The adjacency blur (Kaufman) removes fine texture rather than scaling it" | **corrected**: in Kaufman's model the atmospheric MTF falls from 1 at zero frequency to a **flat plateau** (1 − 0.5τR − 0.7λ^−0.2 τA) above roughly 1 cycle/km, with adjacency length scales of H_A to 6H_A (kilometres). At our 0.5–64 m scales every frequency is on the plateau, so the adjacency effect **scales** fine texture by one constant (and adds a near-uniform background); it does not remove fine texture selectively. Fine-texture loss must come from the other listed causes (quantisation, stretch) or the sensor MTF | eqs. 6, 9, pp. 3402–3403; Figs. 4–6, p. 3404 |
| 7 | ev21 l. 656 | Ref row: Kaufman, Y. J. (1984), Applied Optics 23(19), 3400, DOI 10.1364/AO.23.003400 | verified (the scan carries no DOI; title, author, volume, issue and pages match) | p. 3400, p. 3408 |
| 8 | — | (not in notes) | addition: a uniform-surface correction "only partially corrects the contrasts of fields with more common sizes of 100–2000-m diam."; corrections must use the non-uniform surface pattern | p. 3405 |

## Lv, Wang & Shen 2016 (RSE) — `lv2016_empirical_radiative_transfer_thin_cloud_removal_RSE`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 ll. 252–254 | RSE 179:183–195; "the title says it combines empirical and radiative-transfer modelling for visible bands"; read "Metadata plus a search-snippet" | verified; read level now full text | p. 183 |
| 2 | ev21 ll. 684–686 | Context row: Lv, H., Wang, Y., & Shen, Y. (2016), RSE 179, 183–195, DOI; "no claims are taken from it" | verified (citation); the "no claims" caveat can now be lifted | p. 183 |
| 3 | ev21 ll. 697–698 | GMU priority 1: "the radiative-transfer visible-band thin-cloud algorithm (gap 1/3a)" | verified, with addition that matters: the algorithm needs **TOA reflectance, ≥ 2 visible bands plus one NIR band, and water pixels under thin cloud** (NIR over water isolates cloud reflectance). It cannot run on our Maxar RGB as published | eqs. 1–13, pp. 184–187; p. 194 |
| 4 | — | (not in notes) | addition: transmission T is **one constant per band for the whole scene** (eq. 13); cloud reflectance across visible bands is assumed linear (R² 0.885–0.993 over cloudy water). Quantitative test is one Landsat-8 scene vs a reference 16 days earlier: cloud-pixel bias 0.053–0.057 → 0.018–0.023; the 1.85 m WorldView-2 test is visual only | Tables 2–5, pp. 186–189; p. 191; pp. 192–194 |

## Byun & Han 2018 (J. Appl. Remote Sens.) — `byun2018_relative_radiometric_normalization_flood_change_detection_JARS`
Supersedes the abstract-only rows in claim_checks_C (ll. 336–350).
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 285; claim_checks_C #1 | MAD-based normalisation with a weighting function "based on open water features" (NDWI) | verified, with correction of detail: the weight is the product of a Gaussian of the before–after **NDWI difference** (σ = 0.0001) **and** a logistic of **post-flood NIR reflectance** (k = 3, midpoint = 3rd quartile). It is **not iterative**; PIF threshold t = 0.99; orthogonal regression | eqs. 3–10, pp. 6–7; p. 14 |
| 2 | ev21 l. 286; claim_checks_C #2 | KOMPSAT-2 imagery | verified: 1 m pan-sharpened (4 m MS: B, G, R, NIR), 10-bit; Chad 2010 vs 2012, Sudan 2012 vs 2013 | Table 1, p. 3 |
| 3 | ev21 l. 286; claim_checks_C #3 | Flood change-detection accuracy rose by "1.8% and 12.6%" over IR-MAD at two sites | verified, resolving C's open questions: these are **percentage points of overall accuracy** with the **CVA** detector (81.79 → 83.62; 63.25 → 75.91). With the MAD detector the gains are 0.03 and 5.45 points, and Chad stays at about 51%. Flood **omission rose** with the new method (CVA: 10.2 → 13.3%, 5.95 → 16.47%) while commission fell | Tables 6–7, pp. 15–16; pp. 14, 17 |
| 4 | ev21 l. 288; claim_checks_C #4 | "Needs NIR for NDWI, which we lack" | verified, and stronger: both weight terms need NIR; the authors call it "sensitive to the NIR band" | pp. 6, 14–15 |
| 5 | ev21 l. 288; claim_checks_C #5 | "Only flood-specific VHR normalisation found" | not checkable (search-scope statement) | — |
| 6 | ev21 l. 683; claim_checks_C A2 | J. Appl. Remote Sens. 12(2), 026021, DOI; "context only, not for slides"; Crossref pages 1–19 | verified; the PDF is 20 pp. (SPIE cover + 026021-1 to -19). CC BY 3.0 | cover, p. 1 |
| 7 | — | (not in notes) | addition: IR-MAD failed every hold-out t/F test at both sites; the new method passed all at Chad and all but the band-4 variance at Sudan (P = 0.042). Before/after dates are 1.6–2.3 years apart; references are hand-drawn salient river flood only | Tables 2–5, pp. 10–12; p. 3; p. 13 |

## Gebrehiwot & Hashemi-Beni 2021 (ISPRS IJGI) — `gebrehiwot2021_3d_inundation_mapping_uav_segmentation_dsm_IJGI`
Supersedes the "not checked" rows in claim_checks_C (ll. 403–414). The handoff name differs from the one C anticipated (`…_inundation_mapping_…`).
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev19 l. 296, l. 463; claim_checks_C #1 | ISPRS IJGI 10(3):144; read "Abstract" | verified; read level now full text (14 pp., CC BY) | p. 1 |
| 2 | ev19 l. 297; claim_checks_C #2 | "UAV deep-learning flood polygons plus a pre-flood lidar DEM (Hurricane Matthew, Princeville NC)" | verified, with a caveat from the paper itself: abstract and p. 4 say Matthew 2016, but p. 5 says the model was trained on Matthew images of **Lumberton** and tested on "the Hurricane **Florence** image collected over the city of Princeville". LiDAR 2014, 2 pts/m², 9.25 cm RMSE; UAV 2.6 cm RGB | pp. 1, 4, 5 |
| 3 | ev19 l. 298; claim_checks_C #3 | "Depth RMSE against USGS gauge levels: 0.26 m (DEM method), 0.34 m (SfM)" | verified; the number of gauges and the comparison times are **not reported** | pp. 1, 10, 11–12 |
| 4 | ev19 l. 316; claim_checks_C #4 | Accuracy checked against gauges (Gebrehiwot) | verified | §3.4, p. 7 |
| 5 | — | (not in notes) | addition: DEM method = one constant water level per flood polygon, the mean DEM at shoreline vertices, **excluding water–vegetation and water–building edges**; two methods differ by 0.2 m on average (SD 0.1 m); max depths 1.86 / 2.2 m in the river | p. 6, p. 10 |

## Hersbach et al. 2020 (QJRMS, ERA5) — `hersbach2020_era5_global_reanalysis_QJRMS`
Supersedes the Crossref-only rows in claim_checks_C (ll. 330–334).
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 527, l. 652; claim_checks_C #1 | QJRMS 146(730), 1999–2049, DOI 10.1002/qj.3803; "ECMWF, agency"; read "Metadata" | verified (51 pp., CC BY); read level now full text | p. 1999, p. 2049 |
| 2 | ev21 ll. 527–528; claim_checks_C #2 | "The hourly 0.25° `total_cloud_cover` field" | **corrected (partly)**: hourly output is verified (Table 2). The **0.25° grid is a regridding** of the ~31 km (TL639) native reduced-Gaussian grid for the CDS copy. The paper never names `total_cloud_cover`; the field's existence rests on the ARCO bucket listing, not on this paper | Table 2, p. 2003; p. 2008 |
| 3 | ev21 l. 611 | ARCO-ERA5: "Hourly 0.25° reanalysis, including `total_cloud_cover`, 1959 onwards" | corrected (source): the paper describes 1979 onwards as public, with 1950–1978 to be released in 2020; "1959" is a property of the ARCO store, not of this paper. Licence: the article is CC BY; the data licence is not stated in the paper | pp. 2001, 2008, 2039 |
| 4 | ev21 ll. 574–575 | Use ERA5 as context only: "ERA5's 0.25° grid is coarser than both scenes together" | verified, and stronger: native resolution ~31 km, radiation computed on a grid 2.5× coarser; cloud is a parametrised model variable (Tiedtke-based scheme); **no cloud-cover observation is assimilated**; the paper presents **no cloud-cover validation** | Table 2, p. 2003; p. 2009; pp. 2010–2019; Fig. 4, p. 2015 |
| 5 | ev21 l. 595 | Fix 12 "METAR/ERA5 reported as context", evidence "Weak" | verified (supports "weak"/context-only, per row 4) | — |
| 6 | — | (not in notes) | addition: ensemble spread "mainly samples random errors" and should be read as synoptic-situation quality, not systematic error; known issues include jumps at 12-h window boundaries (e.g. 0.25 m/s in 10 m wind at 10 UTC) and smoothed extremes (storm Lothar gusts 42 vs 59 m/s observed) | pp. 2025, 2030–2031, 2038, 2042 |

## Summary of corrections (for the evidence files' owners)
1. **You 2026:** it weights all dates softly from SAR change; it does not choose dates (dates are random) (p. 8; eqs. 10–12).
2. **Chen 2017:** no depth error is reported; 0.30 m is a water-surface RMSE vs 22 HWMs, with the profile raised 0.9 m to crest. Drop it from the "0.18–0.5 m depth errors" citation (pp. 345–347). Its 72% is a CSI-type F, not percent agreement (eq. 2).
3. **Kaufman 1984:** "30 m → 100 m" holds only at MTF 0.35 (830 m at 0.5) (Table II, p. 3405); and the atmospheric MTF is flat at sub-km scales, so the adjacency effect scales fine texture rather than removing it (eq. 9; Figs. 4–6).
4. **Lv 2016:** needs NIR over water and TOA reflectance; T is per scene (eqs. 9–13).
5. **Byun 2018:** gains are OA percentage points with CVA; weights also need post-flood NIR; flood omission got worse (Tables 6–7).
6. **Gebrehiwot 2021:** paper is internally inconsistent about Matthew vs Florence for the test image (p. 5); gauge count not reported.
7. **Hersbach 2020:** 0.25° is a regridded product of ~31 km; `total_cloud_cover` and "1959 onwards" are not in the paper; no cloud-cover validation (pp. 2003, 2008).
