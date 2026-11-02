# Claim checks, batch C (evidence 21 against full texts)

Compiled by Claude (AI), 2026-10-29. Each claim evidence 21 makes about a paper is checked against the full text and
marked **verified**, **corrected** (the paper says something different; the correction is given), **not found**, or
**addition** (something the full text adds that matters for coding). Page numbers are the journal's. Evidence 21 was not
edited.

## Shen, Li, Qian, Zhang & Yuan 2014 (ISPRS JPRS) — `shen2014_thin_cloud_removal_visible_images_ISPRS`
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Thin clouds cause "high brightness and a low gradient" | verified | p. 226 §3.1 |
| 2 | "with the increase in the wavelength, the influence of the thin clouds decreases so that the details, including edges and textures, increase" (strongest in blue) | verified | p. 227 |
| 3 | Adaptive homomorphic filter; cloudy pixels detected and handled separately | verified | pp. 226–228 §3.2, Eqs. 6–7 |
| 4 | Applied to "2 meters spatial resolution" GaoFen-1 | verified, with a caveat: the 2 m results are visual only (Fig. 11), no numbers | p. 227, p. 234 |
| 5 | "turbid water" needs special treatment; HF brightness change "will cause serious radiometric distortion of the water surface" | verified | p. 228 §3.2.3 |
| 6 | First cut-off frequency "is tuned manually" | verified; the seam width L is also manual | p. 234–235 |
| 7 | "is limited to remove thin clouds" | verified | p. 234 |
| 8 | Fix 1 item 4: "blue-to-red gradient ratio (Shen 2014: haze lowers the blue gradient most)" | corrected (scope): the paper uses a *scene-mean*, brightness-normalised gradient per band (Eqs. 3–4) to set cut-offs, not a per-pixel feature. A local ratio is our adaptation | p. 227 |
| 9 | Gap 3a "my read": the satellite literature keeps the additive-plus-multiplicative form | addition: Shen 2014 does not; it models `f = i·r` and explicitly neglects path radiance | p. 225 |
| 10 | — | addition: the filter shape H(u,v) is never specified; no clear-reference accuracy test; fidelity measured only as R on clear samples | pp. 225, 232 |

## Zhang, Guindon & Cihlar 2002 (RSE, HOT) — paywalled
No open copy: the NRCan preprint URL returned HTTP 404 (an 88-byte HTML error page, caught by validation), and two NRCan
mirrors also returned 404. Claims (HOT is "built empirically from regression of DN values from clear-sky pixels", via
Fmask's account) **not checked**. On the GMU list.

## Zhang & Xiao 2014 (TGRS) — `zhang2014_cloud_detection_rgb_aerial_photographs_TGRS`
Page numbers are the accepted manuscript's 1–12.
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Detects cloud in RGB aerial photographs | verified ("color aerial photographs with just RGB bands information") | p. 1 |
| 2 | Builds a "significance map" | verified: W = (I + 1)/(H + 1) in HSI, bilateral-filtered | p. 3, Eq. 4 |
| 3 | "optimal threshold setting" | verified, with the detail that matters: it is Otsu clamped to [100, 150] plus a hue band of 50–80. Bounds come from 500 web photos, not an optimisation, so "optimal" is the authors' label only | pp. 4–5, Eq. 7 |
| 4 | Refines with a multiscale bilateral "detail map" | verified (M = 4, levels 2–4 weighted) | pp. 5–7 |
| 5 | "guided feathering" that "detects semitransparent cloud pixels around the boundaries of cloud regions" | verified (radius 60, ε 1e-6, threshold 60) | pp. 7–8 |
| 6 | Ranked fix 1 cites it as "Strong" evidence for RGB colour features | corrected (strength): evaluation is 9 photos, error rate only, no GSD, no dataset, no thin-cloud score. It shows that RGB cues are usable, but it is weak quantitative evidence | pp. 8–11 |
| 7 | Gap 4 lists it under learned or optimal thresholds | corrected (scope): its thresholds are fixed constants (100/150, 50–80, 120 px, 60), set from web-photo statistics; only Otsu is adaptive | pp. 4–8 |
| 8 | — | addition: the authors state it misses "extremely thin" cloud, and confuses bright, smooth, low-chroma ground with cloud | p. 11 |

## Li, Shen, Weng, Zhang, Dou & Zhang 2022 (ISPRS JPRS) — `li2022_cloud_shadow_detection_review_ISPRS`
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "the commonly called cloud detection usually does not include the detection of thin clouds like haze, instead, direct dehazing and thin cloud removal is performed" | verified | p. 100 §6.2 |
| 2 | "three parts, including dehazing/thin cloud removal, cloud detection, and thick cloud removal, which are usually performed independently or partially coupled" | verified | p. 100 §6.2 |
| 3 | Features: spectral, spatial, temporal, multi-source, from "mono-temporal, multi-temporal, and multi-source data" | verified (the review's five feature classes are spectral, spectral-spatial, spectral-temporal, spectral-spatial–temporal and multi-source) | p. 90 |
| 4 | Algorithm families: "physical-rule based, temporal-change based, variational-model based, and machine-learning based" | verified | p. 90, §4 p. 94 |
| 5 | Multi-temporal "usually outperform mono-temporal based methods"; "can alleviate the common problems of thin cloud omission and high-bright objects commission" | verified | p. 94 §3.3 |
| 6 | "may generate errors in areas with rapid and significant land cover changes"; "only suitable for areas with small or periodic land cover changes" | verified; the full sentence continues "and images with a high temporal resolution", a second condition we also fail | p. 94 |
| 7 | "for high-resolution images with insufficient spectral information, spectral, geometric, and textural features, usually need to be combined" | verified; it is stated within the physical-rule algorithm section (example: MFC) | p. 96 §4.1 |
| 8 | Validation by four reference types | verified; the review adds that product-based validation is "not very reliable" | p. 99 §5 |
| 9 | Physical models "can also be used to stimulate [simulate] cloud samples" for training | verified | p. 100 |
| 10 | Auxiliary data list (ice/snow, surface temperature, DEMs, synthetic cloud-free images, land cover, water occurrence); multi-source methods "outperform mono-temporal methods" | verified | p. 94 §3.5 |
| 11 | "auxiliary data usually have low resolution, these methods are more suitable for low- and medium-resolution images" | verified | p. 94 §3.5 |
| 12 | MOD35 is "considered a benchmark or standard reference cloud mask" | verified | p. 99 §5.2 |
| 13 | — | addition: Table 1 lists cloud cues usable on RGB (brightness, white colour, smoothness, weak edge) and names "bright water bodies" as a false-positive class; Fmask's cloud-shadow accuracy is "only about 70%" | pp. 92, 100 |

## Zhu & Woodcock 2012 (RSE, Fmask) — done by another agent; checked here against its handoff and the full text
Outputs: `zhu2012_object_based_cloud_shadow_detection_landsat_RSE.md` and the `-summary.pdf` (another batch). The quotes
were re-checked in the publisher PDF (`GGS680/references/Zhu & Woodcock 2012…pdf`).
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Whiteness: MeanVis = (B1+B2+B3)/3; Σ\|(Bi − MeanVis)/MeanVis\| < 0.7; "As clouds always appear white due to their 'flat' reflectance in the visible bands" | verified | p. 85, Eq. 2 |
| 2 | Whiteness "may also include some pixels of bare soil, sand, and snow/ice" | verified | p. 85 |
| 3 | HOT test B1 − 0.5·B3 − 0.08 > 0; blue/red response to haze differs | verified | p. 85, Eq. 3 |
| 4 | HOT "may also include some bright pixels like rocks, turbid water" | verified (snow/ice is also named) | p. 85 |
| 5 | HOT in Zhang et al. 2002 "is built empirically from regression of DN values from clear-sky pixels" | verified; Fmask adds that regressing on TOA reflectance gives Eq. 3 "for most of the Landsat images", so the 0.5 and 0.08 constants are reflectance-specific | p. 85 |
| 6 | Whiteness threshold swept 0.5–0.9 at 0.1, best average cloud overall accuracy, on 142 reference images | verified; accuracy varied only 96.2–96.45% across the sweep (handoff, Fig. 1), so the choice barely matters | p. 85 |
| 7 | Land threshold = "82.5 percentile of lCloud_Prob (Clearsky Land pixels) + 0.2" | verified | p. 87, Eq. 17 |
| 8 | Gap 1 "my read": both tests use visible bands only, so they can run on RGB | corrected (partly): whiteness and HOT are visible-only, but in Fmask they are ANDed with the basic test (SWIR B7, thermal BT, NDSI, NDVI) and the B4/B5 test (Eq. 6). On RGB alone they are much weaker than in Fmask; Fmask's own accuracy figures do not transfer | p. 85–86, Eq. 6 |
| 9 | Evidence 10 / gap 4 context: buffers | addition (from the handoff): Fmask 2012 buffers only *matched shadows* by 3 px; it does not dilate clouds. Do not cite it for the 20 m fade | p. 88 |

## Makarau, Richter, Müller & Reinartz 2014 (TGRS) — done by A (`makarau2014_haze_detection_removal_multispectral_TGRS.md`); full text also read by C
Page numbers are the IEEE early-access 1–11 (journal page = 5894 + n).
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "inhomogeneous haze detection and removal in medium- and high-resolution" multispectral images | verified | p. 1, abstract |
| 2 | DOS extended to a "haze thickness map", allowing "spectrally consistent haze removal on calibrated and uncalibrated satellite multispectral data" | verified | p. 1 |
| 3 | Tested on WorldView-2 | verified, but WorldView-2 *multispectral* at 2 m GSD (8 bands), not 0.5 m pan or RGB display products; the WorldView-2 result is visual only | pp. 3, 9 |
| 4 | "Rare scenes with a uniform and highly reflecting landcover result in limitations" | verified | p. 1, p. 11 |
| 5 | Evidence 21 calls it "the closest published support for running a haze model on non-reflectance products" | verified with a limit: "uncalibrated" means raw DN under "a linear nature of the DN to radiance conversion" (Eq. 2). That confirms evidence 21's own gap-3b reading: only linear rescaling is covered, not a display stretch | p. 2 |
| 6 | — | addition: the model is purely additive (DN = DN0 + HTM), with no transmission term, unlike He et al. | p. 2, Eqs. 1–2 |
| 7 | — | addition: WorldView-2 band groups see haze at shifted positions (parallax), so two HTMs had to be built. This is relevant if Maxar RGB is built from both groups | p. 9 |
| 8 | — | addition: no error metrics. Evaluation is by spectra and profiles against a clear Landsat 8 image 7 days apart, plus ATCOR visibility of 19.9 vs 20.6 km on clear data | pp. 7–10 |

## Guo, Pleiss, Sun & Weinberger 2017 (ICML) — `guo2017_calibration_modern_neural_networks_ICML`
Page numbers are arXiv v2's.
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "modern neural networks, unlike those from a decade ago, are poorly calibrated" | verified | p. 1, abstract |
| 2 | "temperature scaling" is "surprisingly effective" on most datasets | verified ("on most datasets, temperature scaling … is surprisingly effective") | p. 1 |
| 3 | Fix 2 cites it for calibrating *our spotter* | corrected (scope): all evidence is on deep CNN/LSTM/DAN classifiers of natural images and text. Our spotter is a random forest or linear probe on handcrafted + DINOv2 features. The paper supports post-hoc calibration on held-out data in general; for an RF, isotonic or Platt (both defined in the paper) should be tested rather than temperature scaling assumed | pp. 3–6 |
| 4 | — | addition: calibrators assume validation and test "are drawn from the same distribution"; HRC_WHU→Ida is a shift, so calibration must be re-checked on Ida | p. 3 |
| 5 | Evidence 21 reference list gives "ICML 2017 (PMLR 70)" without pages | addition: PMLR 70:1321–1330 | proceedings.mlr.press |

## Ojala, Pietikäinen & Mäenpää 2002 (TPAMI) — `ojala2002_lbp_rotation_invariant_TPAMI`
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | The operator "is, by definition, invariant against any monotonic transformation of the gray scale" | verified | p. 971 abstract, p. 973 |
| 2 | Texture has "two orthogonal properties: spatial structure (pattern) and contrast" | verified | p. 972 |
| 3 | LBP "discards… contrast", which can be added back with a separate variance measure | verified (VAR_{P,R}, Eq. 11; joint LBP/VAR) | pp. 972, 974–975 |
| 4 | Gap 5 "my read": LBP should be unchanged by haze within a window of constant t | corrected (strength): the paper proves invariance only to monotonic grey-level maps. Its own test under a real illuminant change, which is not monotonic (spectra, local shadowing), lost 10–23 points (Table 6: LBP_{24,3} 94.6 → 84.0/80.5%; LBP_{8,1} 85.1 → 67.5/62.7%). Haze with blur or quantisation is likely to behave like that case, not like the ideal | p. 983 Table 6, p. 984 |
| 5 | Ranked fix 7 "LBP-riu2" | addition: the paper's default (P, R) = (8,1), (16,2), (24,3) "as a reasonable starting point … no guarantee"; a 189-operator sweep found (22,4) best. Our code uses (8, 2) only | p. 982 |

## Lowe 2004 (IJCV) — `lowe2004_sift_scale_invariant_keypoints_IJCV`
Page numbers are the accepted manuscript's 1–28 (§6.1 = p. 16).
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "a change in image contrast in which each pixel value is multiplied by a constant will multiply gradients by the same constant, so this contrast change will be canceled by vector normalization" | verified | p. 16 §6.1 |
| 2 | A constant offset "will not affect the gradient values" | verified | p. 16 |
| 3 | The descriptor "is invariant to affine changes in illumination" | verified | p. 16 |
| 4 | "non-linear illumination changes" and "camera saturation" break this | verified; Lowe's remedy is the 0.2 clip, which is itself an empirical non-linear step | p. 16 |
| 5 | Gap 5 "my read": unit-normalised gradient descriptors should survive haze | corrected (scope): the invariance covers the *descriptor* only. SIFT *keypoint detection* discards extrema with \|D\| < 0.03, an absolute contrast threshold, so hazy low-contrast regions lose keypoints. Use the descriptor densely, not SIFT keypoints. The paper has no haze or blur test | p. 11, p. 16 |
| 6 | Reference list: "IJCV (confirm in JCR)" | addition: the manuscript differs from the 20-page journal version in pagination; cite journal pages 91–110 | — |

## Li, Ren, Fu, Tao et al. 2019 (TIP, RESIDE) — `li2019_reside_benchmarking_single_image_dehazing_TIP`
Page numbers are arXiv v4's.
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Most methods "rely on the full-reference PSNR and SSIM metrics, with assuming a synthetic testing set" | verified | p. 3 |
| 2 | "practical applicability may be in jeopardy even [if] a promising testing performance is achieved, due to the large content divergence between synthetic and real hazy images" | verified | p. 3 |
| 3 | Adds no-reference metrics, human ratings and a "task-driven" set of 4,322 real hazy images with object annotations | verified (RTTS: 41,203 boxes, 5 traffic classes) | pp. 4–5, 9 |
| 4 | — | addition: on real RTTS images, dehazing changed detection mAP only slightly and sometimes made it worse (Faster R-CNN 37.58 raw vs 28.90–41.56 after dehazing). This is evidence that a "no dehazing" baseline is mandatory | p. 10, Table X |
| 5 | — | addition: "'under-dehazed' images might be preferred over 'over-dehazed' images" for recognition | p. 9 |

## Ma, Wang, Tong & Atkinson 2022 (RSE, TIIN) — `ma2022_tiin_temporal_information_haze_removal_RSE`
Page numbers are the accepted manuscript's 1–43.
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Temporal neighbours give a "spatial distribution prior" that "is usually not the same as for the target hazy images due to land cover changes" | verified | pp. 6, 34–35 |
| 2 | Relies on "the proportion of land cover changes" being "generally small, as most changes… are driven by vegetation phenology" | verified | p. 35 §4.1 |
| 3 | Uses Landsat-8 with seven bands | verified | p. 13 |
| 4 | "a cirrus band from a cloudy region was employed as reference" transmission, using "35 cirrus maps" | verified | p. 15 |
| 5 | "four real hazy images" were also tested *against references* | corrected: the real-haze cases (Regions 7–11, five regions in the text despite "four real hazy images" on p. 16) are judged **visually only**. Reference-based metrics (CC, UIQI, RMSE) exist only for simulated haze | pp. 16, 31–34 |
| 6 | — | addition: the simulation's band link `t_i = t_1^{(λ_1/λ_i)^γ}` (γ = 1 in training; "γ ranges from 0 to 4" citing Chavez 1988) is a concrete formula for fix 9's band-linked haze | pp. 14–15 |
| 7 | — | addition: authors concede "the simulated haze is similar to but not equivalent to real haze" | p. 36 |

## Heidinger & Straka 2020, NOAA ECM ATBD v1.2 (agency) — `heidinger2020_noaa_enterprise_cloud_mask_ATBD`
PDF pages (= printed pages).
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "a naive bayesian approach trained on NASA CALIPSO Data", producing "a cloud probability and a 4-level cloud mask" | verified | pp. 11, 14 |
| 2 | Uncertainty = P_cloud if the mask is clear, 1 − P_cloud if cloudy | verified | p. 29 |
| 3 | Earlier fixed cut-offs (0.1, 0.9) "resulted in varying amounts of confidently-clear for each surface type"; the current mask "sets the PCC values" per surface type to a target share of confidently clear | verified; the target is 25% of binary-clear pixels per surface type, PCD stays 0.9, and the binary cut is P_cloud = 0.5 | pp. 29–30 |
| 4 | ABI visible "native resolution of 0.5km", "sixteen corresponding pixels … within a single 2km IR pixel" | verified | p. 42 |
| 5 | "overall global ACC requirement for the ECM is 87% for clouds with an optical depth (COD) greater than 0.4"; snow-free land by day 90% | verified (Table 1) | p. 15 |
| 6 | Hit rates at COD 0.01 fall to "30%, 45% and 35%"; 50% sensitivity "0.1, 0.06 and 0.03" | verified | pp. 57, 59 |
| 7 | NWP surface temperature enters clear-sky expectations | verified (GFS 3/6/9 h forecasts; RTM clear-sky BTs) | pp. 22–23 |
| 8 | Evidence 21 cites "sections 2, 3, 7.5 and 10.4" | corrected (citation detail): the document's TOC numbering (1–12) and body headings (1–15) disagree; the uncertainty text is body §7.5 / TOC §5.5 on p. 29, and the optical-depth sensitivity is body §10.4 ("ECM Sensitivity to Optical Depth", unnumbered in the body) on pp. 57–59. Cite page numbers | — |
| 9 | — | addition: training relabels CALIOP columns with optical depth < 0.1 as clear, so by design ECM treats the thinnest haze as clear; ECM under-calls cloud relative to CALIOP | pp. 50, 52 |
| 10 | — | addition: ABI/AHI land ACC 0.93 (COD > 0.4); BACC 0.88 with no COD filter | pp. 53–54 (Tables 11–12) |

## Papers done by agent A: evidence-21 claims checked against A's handoffs (and, for MSCFF, A's summary PDF text)
| Paper | Claim in evidence 21 | Verdict | Source |
|---|---|---|---|
| He et al. 2011 | t bounded at t0 = 0.1 because the result "is prone to noise" | verified | A handoff, eq. 22, p. 2348 |
| He et al. 2011 | Dark channel defined as the minimum over R, G, B ("He et al.'s original definition; ours runs on grey") | verified; A adds that the paper says the method "also works for gray-scale images if there are enough shadows" (p. 2349) | claim_checks_A.md #5, #11 |
| He et al. 2013 | pointer only, no specific claim in evidence 21 | — | — |
| Canty & Nielsen 2008 | normalisation on no-change pixels (IR-MAD) | verified (time-invariant features; MAD invariant to affine transforms of either image) | A handoff, pp. 1025, 1028 |
| Hagolle et al. 2010 | pointer only | — | — |
| Shen et al. 2015 | "missing" means information "completely obscured or not observed" | verified; the review explicitly excludes thin cloud and haze ("not discussed in this paper") | A handoff, p. 18 |
| Shen et al. 2015 | temporal methods "are sensitive to land-cover changes, especially abrupt changes" | verified | A handoff, p. 17 |
| Li et al. 2019 (MSCFF) | validated on images "with spatial resolutions ranging from 0.5 to 50 m", including "high-resolution images exported from Google Earth" | verified | arXiv p. 1 (abstract) |
| Li et al. 2019 (MSCFF) | "obvious advantages" over rule-based methods "especially in bright surface covered areas" | corrected (wording): the arXiv version A read says MSCFF "achieves a higher accuracy than the traditional rule-based cloud detection methods and the state-of-the-art deep learning models, especially in bright surface covered areas". "obvious advantages" does not appear there; it may be in the journal abstract (not checked) | arXiv p. 1 |
| Li et al. 2019 (MSCFF) | HRC_WHU is RGB (gap 1) | verified: 150 Google Earth RGB images, 0.5–15 m, mixed satellite and aerial sources, no accurate geolocation | A handoff, Table 2 |

---

# Part 2: rest of evidence 21 (claims from evidence 21; checked by Claude workers within batch C)

## Haralick 1979 (Proc. IEEE) — `haralick1979_statistical_structural_texture_ProcIEEE` (claims from evidence 21)

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Spatial-frequency texture procedures "are not invariant under even a monotonic transformation of gray tone" | verified (exact quote; it refers to the spatial-frequency approaches, as evidence 21 says) | p. 787 |
| 2 | "To compensate for this, probability quantizing can be employed", at the price of "loss of gray tone precision" | verified | p. 787 |
| 3 | Co-occurrence characterises grey-tone relationships "in a way that is invariant under monotonic gray tone transformations" | verified, with a qualification: the same passage says its weakness is that it "does not capture the shape aspects of the tonal primitives" and "is not likely to work well for textures composed of large-area primitives". The invariance in practice needs distribution-tied (probability) quantizing; fixed-bin contrast/correlation change under monotonic maps. | p. 787 |
| 4 | Ranked fix 7: "invariance theory from … Haralick; no empirical haze study found" | verified: the paper is a survey with no haze, atmospheric or blur discussion | pp. 786–804 |
| 5 | (addition) Relative-extrema primitives are invariant "under any monotonic gray scale transformation" — a third invariant family besides LBP | addition | p. 801 |
| 6 | (addition) Scale: "For any smooth gray-tone surface, there exists a scale such that when the surface is examined, it has no texture" — relevant to the adjacency-blur argument (blur removes fine texture rather than scaling it) | addition | p. 788 |
| 7 | (addition) sn8_glcm.py's docstring names "homogeneity" and "asm" as Haralick features; Haralick 1979 prints energy, entropy, max probability, contrast (general exponents k, λ), inverse difference moment, correlation, run probability. The names homogeneity/ASM come from other papers (e.g., Haralick et al. 1973). | addition (naming only) | p. 792, Fig. 7 |

Reference row (#10): citation, volume, issue, pages and DOI correct (Crossref). Venue "Proc. IEEE (confirm in JCR)": JCR not checked here; Proc. IEEE's JIF is commonly reported at about 20+, well above 4, but confirm in JCR. "Passage (disk)" can now be upgraded to "Full text (disk)".

## Ju, Ding, Zhang & Guo 2018 (IEEE SPL) — `ju2018_gamma_correction_dehazing_SPL` (claims from evidence 21)

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | The model "explicitly describes the inner relationship between the gamma correction (GC) and the traditional scattering model" | verified (abstract wording) | p. 1 (abstract) |
| 2 | "Ju et al. (2018) treat gamma explicitly for ground photos" (in the argument that a non-linear display stretch breaks the affine haze model) | corrected: ground photos, yes, but gamma here is the *dehazing operator* (I_G = I^Γ with a per-pixel Γ = e^{βd}), not a display stretch or a camera gamma applied to the input. The paper assumes the input obeys the ASM directly and never discusses linearising a stretched input. Eq. 5 (β_G ≅ β − ln Γ / d) does show that a power law changes the apparent haze non-uniformly, which supports the "breaks the affine form" point only indirectly. | pp. 2–3, Eqs. 1–7 |
| 3 | Fix 9: "weak for the stretch (only low-JIF gamma papers)" | verified: the paper gives no evidence on stretch linearisation, and the venue is below the bar (see below) | — |
| 4 | (addition) It is a one-parameter method: ρ = (I/A)^{exp(τ·Mean(Ī))}, with τ from a whole-image golden-section search maximising gradient energy; mean filter 45 px; A from DCP. Fast (0.21–0.59 s), highest SSIM on 4 benchmark ground photos (Table I). No remote-sensing images. | addition | pp. 2–4 |
| 5 | (addition) Depth is proxied by mean-filtered brightness ("scene brightness is increased along with the change of the scene depth"), which does not hold for nadir VHR imagery | addition | p. 2, Eq. 8 |

Reference row (#15): citation, volume, issue, pages and DOI correct (Crossref). "SPL (confirm in JCR; context)" is right to flag. IEEE SPL is commonly reported at a JIF of about 3–4, i.e. below the > 4 bar (not checked in JCR here), so it is context only. Evidence 21 says "Abstract"; the full text (accepted manuscript) has now been read.

## Ju, Ding, Ren, Yang, Zhang & Guo 2021 (IEEE TIP) — `ju2021_ide_enhanced_scattering_model_dehazing_TIP` (claims from evidence 21)

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | The atmospheric scattering model "has an intrinsic limitation which leads to a dim effect" | verified (abstract wording) | p. 1 |
| 2 | The authors add a "light absorption coefficient" | verified: α ∈ (0, 1] multiplies the direct term only, I = A(1 − α)ρt + A(1 − t); α = 1 − ln t / ln t_min | pp. 3–4, Eqs. 4–8 |
| 3 | "Ground-level photos" | verified, mostly: ground-level real images plus RESIDE, I-HAZE and O-HAZE; one oblique city view (Fig. 4); no satellite or nadir images | pp. 5–9 |
| 4 | (addition) The absorption term is justified by depth and texture density ("light … trapped/absorbed in textures", near scenes absorb more), so it has no physical basis for nadir VHR imagery. The exposure step lowers PSNR against the ground truth by design (I-HAZE 15.77 vs MSCNN 16.54; O-HAZE 14.19 vs EPDN 16.88) | addition | pp. 3, 9; Table II |
| 5 | (addition) Reusable: a grey-world patch-mean transmission in closed form (75 × 75 patches) and a global one-scalar search targeting 2% clipping; no training; fastest of the MATLAB methods timed | addition | pp. 4–6, 10 |

Reference row (#16): citation, volume, pages and DOI correct (Crossref). The JIF given (TIP 13.7) was not checked in JCR here; TIP is above 4 under any recent JCR year. Evidence 21 says "Abstract"; the full text (final manuscript) has now been read. Evidence 21 uses this paper only as context for amending the ASM (gap 3a), which is consistent with the full text.

## Ning, Xie, Yin & Liu 2025 (IEEE JSTARS) — `ning2025_cloud_removal_review_JSTARS` (claims from evidence 21)

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Classifies removal methods "based on the type of auxiliary data used: single-image, multimodal, and multitemporal" | verified (abstract wording); sub-classes are statistical/physical vs deep learning (single-image), multispectral vs SAR fusion (multimodal), non-blind (mask) vs blind (multitemporal) | p. 15914; Tables I–III |
| 2 | It also outlines "benchmark datasets and evaluation metrics" | verified: RICE1/2, SEN12MS-CR, SEN12MS-CR-TS; SSIM, PSNR, RMSE, LPIPS | p. 15922 |
| 3 | Ranked fix 8: "Strong: Li 2022, Shen 2015, Ning 2025" for the taxonomy table | verified as a taxonomy source, with a caveat: the review covers cloud *removal* only (no detection stage), and its benchmark is weak (single runs, 1000 / 60 training iterations, no significance tests, Table IV caption says CIEDE but the columns are RMSE, table/text citation numbering mismatches) | pp. 15922–15924 |
| 4 | (addition) Multitemporal methods are "not suitable for areas with significant ground feature changes"; model-driven multitemporal methods "presuppose a minimal ground change" — supports the small-change caveat in gap 3c / fixes 5–6 | addition | pp. 15914, 15921 |
| 5 | (addition) Synthetic pairs "tend to exhibit substantial generalization errors" on real clouds — supports fix 4 | addition | p. 15925 |
| 6 | (addition) Table I lists Zhang et al. 2002 (HOT) with the limitation "requirement for manual sample selection" and DCP as "darker than the real truth and often over-saturated" | addition | p. 15916 |

Reference row (#26): citation, volume, pages and DOI correct (Crossref); open access CC BY 4.0. JSTARS 6.3 not re-checked in JCR here (above the 4 bar either way). Evidence 21 says "Abstract"; the full text has now been read.

## Jiménez 2020 (Remote Sensing 12(10), 1630) — `jimenez2020_goes16_clear_sky_mask_calipso_conus_RemoteSens` (claims from evidence 21)

Copy read: NASA author manuscript NIHMS1710516 (PMC8243760), 24 pp.; page numbers are the manuscript's.

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | (l. 104) "A two-year CALIPSO check over the contiguous US found clear-sky detection weaker (74.8%) than cloudy (90.9%)." | verified | p. 5 and p. 8: all sky 86.0%, cloud 90.9%, clear 74.8%, 2018–2019 |
| 2 | (l. 493) "two years, compared on a 9 km grid" | verified | pp. 3–4: 2018–2019; ACM and CALIPSO both averaged to a 9 km CONUS grid; 1,371,012 matched pairs |
| 3 | (l. 493) "Probability of detection… of all sky conditions of 86.0%"; cloudy "90.9%", clear "74.8%" | verified | p. 1 abstract; p. 5 |
| 4 | (l. 494) Clear-sky errors come from "missdetections during daytime", especially in summer | verified | p. 1, p. 8. Day: cloud 95.9%, clear 66.6%; night 85.8% / 82.5% (p. 6). Note the full sentence also names "regions to the north of parallel 36 during winter" |
| 5 | (l. 494) "Regions to the south of parallel 36 show acceptable performance" | verified, with a caveat (addition) | p. 8. This is an all-season conclusion; for **summer daytime** clear-sky accuracy is "somewhat low (around 0.6)" with "little dependence on the latitude" (p. 7, Fig. 8c), so it applies to Ida's latitude too |
| 6 | (l. 536) "Clear-sky calls in daytime summer are its least reliable class (Jiménez 2020)." | corrected | Jiménez's "clear sky accuracy" is the share of CALIPSO-clear cells that the ACM calls clear. Low values mean the ACM **over-detects cloud** by day ("suggests a cloud over-detection during daytime", p. 6). So the unreliable call is a GOES **"cloudy"** over truly clear sky; GOES "clear" calls are rarely wrong (cloud detection 95.9% by day). Also, in Fig. 8 winter north of 36 N is worse (~0.3–0.5) than summer (~0.6); summer is the monthly minimum of the daytime clear-sky median (p. 6, Fig. 6b), and the worst season at southern latitudes (Fig. 8) |
| 7 | (l. 608, dataset row) ACM cited with Jiménez 2020: "2 km IR … CONUS every 5 min"; "naive Bayes trained on CALIPSO" | partly not found | Jiménez gives "every 10 min (full disk), at 2 km" (p. 3) and describes the ACM as threshold tests with thresholds tuned on SEVIRI–CALIPSO, citing the **2012** ATBD (pp. 2–3). The 5-min CONUS cadence and the naive-Bayes description are not in this paper (they come from the AWS listing and the 2020 ECM ATBD). Whether the 2021 operational ACM was the naive-Bayes ECM should be checked before citing both together |
| 8 | (l. 625) CALIPSO/CALIOP layer products used by Jiménez 2020 | verified | p. 4: CALIPSO cloud layer product, 1 km, V3.40; cloudy if a cloud top is reported and CAD score > 30 |
| 9 | (l. 492, l. 653) read level "Abstract" | update | Now full text (24 pp. manuscript) |
| 10 | — | addition | Missed clouds are mostly low boundary-layer clouds with tops near 1 km AGL; false clouds are also low (pp. 7–8). A 1 h time offset drops clear-sky accuracy to 69.0% (p. 5): match the GOES scan to the Maxar pass time |
| 11 | — | addition | The paper does not stratify by cloud optical depth; the COD-0.4 / 45%-at-0.01 numbers in evidence 21 belong to the ATBD only, not to Jiménez |

Reference row (l. 653): authors, title, venue, volume 12(10), article 1630 and DOI all match Crossref. JIF 4.3 not checked here.

## Wagner & Kleiss 2016 (J. Atmos. Oceanic Technol. 33(7), 1557–1567) — `wagner2016_ceilometer_cloud_amount_errors_JTECH` (claims from evidence 21)

Copy read: published AMS version, NOAA Institutional Repository (noaa/69344), 11 pp.; journal page numbers.

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | (l. 106, l. 556) "Ceilometer cloud reports miss upper-level cloud" | verified | p. 1558: ASOS records bases only ≤ 3,660 m (12 kft); p. 1565: when the ceilometer said clear the MPL saw some cloud 47.3% and overcast 22.8% of the time, mean base 6,683 m |
| 2 | (l. 509) errors "caused by the limited vertical range" dominate those from limited areal coverage | verified | abstract p. 1557 ("these errors are small compared to those caused by the limited vertical range"); Table 1 p. 1564: all-cases RMSE 0.086 sampling vs 0.505 high-cloud |
| 3 | (l. 510) "Observations of clear sky or few clouds are often in error as the instrument cannot detect the presence of upper-level clouds" | verified | abstract p. 1557 (exact wording; original lower-case "observations"). Table 1: total RMSE CLR 0.642, FEW 0.749 |
| 4 | (l. 511) The largest errors occur "in the morning and summer" | verified, with caveat (addition) | abstract p. 1557 says "at the SGP site" (Oklahoma); p. 1566: "quantitative results apply only to the conditions at the SGP site". Monthly agreement minimum 38.3% in June; hourly minimum near 15 UTC (Fig. 8b, p. 1566) |
| 5 | (l. 539) "METAR at airports is point-sampled and blind above the ceilometer's range" | verified | p. 1558 (single zenith point, time-averaged; 3,660 m reporting limit although the instrument senses to 7,700 m) |
| 6 | (l. 508) venue "J. Atmos. Oceanic Technol. 33:1557 (confirm in JCR; probably below 4, context)" | verified (bibliographic); JIF not checked | Crossref and the PDF: 33(7), 1557–1567 |
| 7 | (l. 508, l. 675) read level "Abstract" | update | Now full text (all 11 pp.) |
| 8 | — | addition | Only OVC reports are reliable (RMSE 0.057; p. 1566: "one may have high confidence"); CLR/FEW are the least reliable. So a METAR CLR (as at KMSY 15:53–17:53 UTC) cannot confirm clear sky over our scenes — supports fix 12 "context only" |
| 9 | — | addition | Point-sampling (spatial) error alone: CLR/OVC RMSE < 0.06, partial cloud 0.14–0.15 (p. 1564) |

Reference row (l. 675): authors, title, volume/issue/pages and DOI all correct.

## Frey, Ackerman, Holz, Dutcher & Griffith 2020 (Remote Sensing 12(20), 3334) — `frey2020_continuity_modis_viirs_cloud_mask_RemoteSens` (claims from evidence 21)

Copy read: published MDPI version (CC BY 4.0), NOAA Institutional Repository (noaa/69642), 18 pp.

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | (l. 501) against collocated CALIOP lidar, combined clear and cloudy hit rates were "88.2%… 86.8%" for June–August 2018 | verified | p. 1 abstract; Table 3 p. 8: global JJA 2018 88.2 (MYD35), 87.5 (MVCM Aqua MODIS), 86.8 (SNPP VIIRS), 86.8 (NOAA-20 VIIRS). The 88.2% is MYD35, the operational Aqua mask, not the MVCM |
| 2 | (l. 609, dataset row) MOD35_L2 (Terra) C6.1 listed with "Ackerman et al. 1998; Frey et al. 2020"; "Frey 2020: CALIOP hit rates about 87–88%" | corrected | Frey 2020 validates **Aqua** MYD35 and MVCM (Aqua MODIS, SNPP and NOAA-20 VIIRS) only; "Terra MODIS outputs have not yet been produced by the MVCM" (p. 2). The 87–88% therefore does not directly describe the Terra MOD35 granule tested in evidence 21; at 60S–60N JJA the figure is 90.1–90.7%, land day 89.4–90.4% (Table 3) |
| 3 | (l. 609) "pixel size and granule length not verified in the sources read" | addition (now partly verified) | p. 2: "Nominal spatial resolution of the MVCM L2 product is 1 km for MODIS and 750 m for VIIRS"; p. 5: an example Aqua granule is "5 min" |
| 4 | (l. 609 / gap 7) mask has clear-sky confidence levels | verified | p. 5: four classes — clear, probably clear, probably cloudy, cloudy; fuzzy-logic confidence of clear sky (p. 2) |
| 5 | (l. 500, l. 645) venue Remote Sensing 12:3334 (4.3, narrow); read level "Abstract" | verified (bibliographic); update read level | Crossref: 12(20), 3334, five authors (Frey, Ackerman, Holz, Dutcher, Griffith). Now full text. JIF not checked |
| 6 | — | addition | Thin-cirrus skill depends on the 1.38 µm band; for COD > 0.25 the 1.38 µm test hits > 0.9 for cirrus tops ~7–15 km, lower for thin clouds and over land (Fig. 4, pp. 11–12). Supports evidence 21's "weak for VHR / thin haze" verdict on external products |
| 7 | — | addition | Turbid near-shore water gives false cloud in VNIR (p. 4); MVCM adds a 2.1 µm 3 × 3 std clear-sky test. Relevant to our flood-water false positives (fix 1 reporting) |
| 8 | — | addition | Thresholds are expert-set and "still largely subjective" even when tuned on CALIOP (p. 14) |

Reference row (l. 645): title, venue, volume/issue/article and DOI correct; "et al." hides one author (Griffith, Z.).

## Götz, Wessel, Çayoğlu, Jahani, Debus, Cermak & Streit 2025 (IEEE JSTARS 18, 10674–10683) — `gotz2025_ordinal_metar_cloud_cover_sentinel2_JSTARS` (claims from evidence 21)

Copy read: accepted author version (CC BY 4.0), KITopen 1000180808, 12 pp.; page numbers are the manuscript's.

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | (l. 515) trained on "ordinal point labels from ground-based weather stations (METAR)" | verified | p. 1 abstract; p. 4 (12,749 Sentinel-2 L1C patches, ±30 min, CA/FL/MT/TX/WA) |
| 2 | (l. 516) Station labels alone gave "an F1-score of up to 0.6" | verified (abstract only) | p. 1. The body reports per-class within-one F1 (F1,1) 0.93–0.99 and exact per-class accuracy 34–72% (Fig. 4, p. 7); the 0.6 itself is not broken down in the body |
| 3 | (l. 516–517) Adding visually corrected labels "to correct for station-satellite mismatches" raised it to 0.75 | corrected (nuance) | p. 1 abstract wording verified, but p. 7: **all** 12,749 patches were relabelled by eye and the model was trained **and evaluated** on the manual labels. So 0.6 → 0.75 compares different ground truths, not a gain on the same test set |
| 4 | (l. 595, fix 12) "Götz 2025 F1 ≤ 0.75" | verified | abstract p. 1 |
| 5 | (l. 612, IEM row) "Data source for Götz et al. 2025 type labels (they collected METAR; the source archive was not checked)" | corrected | p. 4: METAR "obtained from the Iowa State University, Iowa Environmental Mesonet (IEM) – ASOS-AWOS database [24]" — the same archive evidence 21 tested |
| 6 | (l. 624) METAR–Sentinel-2 dataset "described as 'custom-collected'; no release located" | corrected | Contributions (p. 1) list "a publicly available dataset"; p. 7 footnote 5: https://doi.org/10.5281/zenodo.14691473. Zenodo metadata (checked 2026-10-29, nothing downloaded): record 14691474, `dataset_16km_300_ndsi.zip` 9,357,564,288 B, CC BY 4.0. Code: github.com/ErikWessel/MSCC; checkpoints 10.5281/zenodo.14750977 (record 14750978, 2 × ~82 MB) |
| 7 | (l. 513, l. 646) venue IEEE JSTARS 18:10674 (6.3) | verified (bibliographic); JIF not checked | Crossref: vol. 18, pp. 10674–10683, 7 authors. The JIF 6.3 could not be confirmed here — check in JCR |
| 8 | (l. 513, l. 646) read level "Abstract" | update | Now full text |
| 9 | — | addition | Mean per-station METAR-vs-visual mismatch ≈ 15.9% (p. 7); METAR over-reports the extremes, especially CLR (Fig. 5a). Consistent with Wagner & Kleiss 2016 (unseen high cloud), though Götz attribute it mainly to the ±30 min offset |
| 10 | — | addition | The input needs Sentinel-2 B11 (SWIR) via NDSI (Eqs. 1–2, p. 5); patches are 32 km at 300 px; higher resolution did not help (p. 7). Not transferable to 0.5 m RGB |

Reference row (l. 646): title, venue, volume, pages and DOI correct.

## Yeom, Roujean, Han, Lee & Kim 2020 (RSE) — `yeom2020_goci_thin_cloud_brdf_background_RSE` (claims from evidence 21)
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | GOCI is "a 500 m geostationary sensor without thermal bands" (line 519) | verified | Abstract and Sect. 2.1, pp. 1–2: 500 m, 6 visible + 2 NIR bands, "lack of thermal bands" |
| 2 | Clouds detected "against a BRDF-modelled clear background" because "surface BRDF varies slowly with time compared to that of clouds" | verified (quote exact) | Abstract, p. 1; Sect. 3.2, pp. 4–5 |
| 3 | Against CALIPSO, POD 0.831 (MODIS 0.772) | verified | Table 3, p. 10 (all cloud; GOCI FAR 0.034, MAR 0.169; MODIS FAR 0.019, MAR 0.228) |
| 4 | "0.849 for thin cirrus" | corrected | The abstract says "only thin cirrus", but Table 3 (p. 10) defines thin cloud as CALIPSO **altostratus + cirrus**. MODIS also scored 0.849 on the same class, so it is a tie, not a GOCI advantage. GOCI MAR 0.151 vs MODIS 0.091 |
| 5 | (addition) Step 2 is what does the work: thin-cloud POD rose from 0.338 (threshold step only) to 0.849; all-cloud from 0.638 to 0.831 | addition | Table 3, p. 10 |
| 6 | (addition) Thin cloud uses mainly the 0.412 µm blue band; class rule DIFF_0 > MIN + abs(e); DIFF_0 < 0 = shadow; 16-day window, at least 7 clear observations for the BRDF fit | addition | Eqs. 5–7, Fig. 3, pp. 4–5 |
| 7 | (addition) Known false positives: bright desert (Horqin sand land) and thick aerosol, which CALIPSO called aerosol | addition | pp. 9, 11 |
| 8 | (addition) Step-1 thick-cloud threshold values are not published | addition | p. 4 |
| 9 | Evidence 21 "Read" column: "Abstract" | corrected | Now read in full (HAL copy of the published version). Venue/volume/article number/DOI in reference row 38 match Crossref. The RSE JIF 12.3 was not checked here. Crossref lists a fifth author (Kim, H.-W., corresponding), covered by "et al." |

## Ackerman, Strabala, Menzel, Frey, Moeller & Gumley 1998 (JGR-Atmospheres) — `ackerman1998_modis_cloud_mask_clear_sky_JGR` (claims from evidence 21)
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Each test "returns a confidence level that the pixel is clear" (line 498) | verified (quote exact) | Abstract, p. 1; Fig. 2 and p. 6: confidence 0–1 via alpha/beta/gamma thresholds with a linear ramp |
| 2 | "the product of group confidences gives clear-sky confidence" (line 499) | corrected | The abstract says "product", but Eq. 2 (p. 12, checked on the rendered page) is the **N-th root of the product** of the group confidences (a geometric mean). Each group's confidence is the **minimum** of its tests (Eq. 1). Output levels: Q > 0.99 confident clear, > 0.95 probably clear, > 0.66 undecided, <= 0.66 cloudy |
| 3 | MOD35 is the "NASA/UW operational algorithm, context" | verified, with a caveat | The paper is the **pre-launch** algorithm description ("Routine and reliable production … anticipated in late 1998", p. 31). It has no accuracy statistics. Operational C6.1 numbers come from Frey et al. 2020, as evidence 21 already does at line 609 |
| 4 | (addition) A pixel can be both confident clear and thin-cirrus flagged (optical depth below about 0.1), meant for cases where land retrievals "should incorporate a cloud correction" | addition | pp. 16, 26 |
| 5 | (addition) Thin-cloud lidar comparison: most thin-cloud cases were labelled either confident clear or cloudy, so thin cloud is where the mask is least decisive | addition | p. 28, Fig. 9 |
| 6 | (addition) The visible reflectance test does well for bright cloud over dark surfaces and poorly over bright surfaces. The spatial-uniformity test is not run over land | addition | pp. 19, 22 |
| 7 | Reference row 1 (line 640): venue, volume, issue, pages and DOI | verified | Matches Crossref. Crossref lists six authors (Moeller, Gumley), covered by "et al." JIF 3.4 was not checked here. "Read" column was "Abstract"; now read in full from the authors' final manuscript (CIMSS copy, 49 pp.) |

## Wilson & Jetz 2016 (PLOS Biology) — `wilson2016_global_1km_modis_cloud_frequency_PLOSBiol` (claims from evidence 21)
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "monthly cloud frequencies from 15 y of twice-daily" MODIS images, at about 1 km (line 505) | verified (quote exact) | Abstract, p. 1. Methods (p. 11) give Feb 2000 – Mar 2014 Terra + Aqua; the climatology is labelled 2000–2014 |
| 2 | "this is climatology only … not whether a cloud was there on 31 Aug" (line 506–507) | verified | pp. 11–12: monthly proportion of cloudy days averaged over years; binary flag, no confidence |
| 3 | Dataset table (line 610): "Derived from the MODIS cloud flags" | corrected (sharpen) | Specifically bit 10 of MOD09GA/MYD09GA `state_1km`, the MOD09 internal cloud mask (MIRA + 1.38 µm + thermal). The authors explicitly reject MOD35 as "unsuitable" for consistent 1 km maps (p. 11). Do not describe EarthEnv as MOD35-derived |
| 4 | Dataset table (line 610): licence "CC BY-NC 4.0 (non-commercial)" | not found | The paper does not state the dataset licence (the article is CC BY). The value must come from the EarthEnv data page, which was not re-checked here |
| 5 | Dataset table: "No metric to replicate" | corrected | The paper reports validation against 5,388 synoptic stations: R² 0.78, RMSE 7.99% (2000–2009, n = 17,021); monthly R² 0.66–0.84; full record R² 0.74 (p. 12). These are climatology-level metrics, not replicable or relevant for our scene |
| 6 | (addition) A RGB-brightness cloud product is "problematic over high-albedo surfaces (such as urban areas or snow)" | addition | p. 3 (and S1 Table caption, p. 15) |
| 7 | Source note (line 25): "only its abstract and data page were used"; reference row 37 "Abstract + data page" | corrected | Now read in full (published PDF, 20 pp.). Citation fields match Crossref. JIF not checked here ("confirm in JCR" stands) |

## Hersbach et al. 2020 (QJRMS) — not read (claims from evidence 21)
| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Reference row 13: QJRMS 146(730), 1999–2049, DOI 10.1002/qj.3803 | verified against Crossref only | Crossref: same title, volume, issue and pages; 43 authors; licence CC BY 4.0 (hybrid OA). Full text not read: the Wiley PDF gave curl a Cloudflare bot check, and the Ifremer mirror returned 403 |
| 2 | Hourly 0.25° `total_cloud_cover` (lines 527–528, 611) | not checked | Needs the full text (or the ECMWF/C3S ERA5 documentation). The claim rests on the ARCO bucket listing, which evidence 21 already tested |

## Byun & Han 2018 (J. Appl. Remote Sens.) — `byun2018_relative_radiometric_normalization_flood_jars` (claims from evidence 21)

Status: FULL TEXT NOT OBTAINED. The CC BY publisher PDF (only OA location per Unpaywall/OpenAlex/Semantic Scholar; no repository copy) returns a 212-byte Incapsula bot-check HTML stub to curl. The Chrome extension was not connected, and I did not try to get past the bot wall. Checks below are against the publisher abstract only (Crossref/OpenAlex/Semantic Scholar metadata, identical text). Crossref: vol 12, issue 02, pages 1-19, CC BY 4.0, published 2018-05-25.

| # | Claim in evidence 21 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | MAD-based normalisation with a weighting function "based on open water features" (NDWI) | verified (abstract) | Abstract: weights "based on open water features, which are estimated by the normalized difference water index", used in the covariance matrices of the MAD transform. Page not checked. |
| 2 | KOMPSAT-2 imagery | verified (abstract) | Abstract: "Experimental results on KOMPSAT-2 bitemporal VHR images". |
| 3 | Flood change-detection accuracy rose by "1.8% and 12.6%" over IR-MAD at two sites | verified (abstract), with a caveat | Abstract: "increased the overall accuracy of flood change detection by 1.8% and 12.6% for the two study sites". The metric is overall accuracy (evidence 21 just says "accuracy"; say "overall accuracy"). The abstract does not say whether these are percentage points or relative gains, or which change detector (CVA or MAD) produced them. Needs the full text. |
| 4 | "Needs NIR for NDWI, which we lack" (My read) | verified (inference) | NDWI needs green + NIR. KOMPSAT-2 MS has NIR. |
| 5 | "Only flood-specific VHR normalisation found" (My read) | not checkable | Search-scope statement, not a paper claim. |
| A1 | — | addition | The comparison used two change detectors, CVA and MAD-based, plus statistical tests of normalisation quality (abstract). |
| A2 | Reference row / context paragraph | verified | Venue J. Appl. Remote Sens. 12(2) 026021, DOI correct, JIF below 4 is right (JARS is about 1.4–1.7; I did not check JCR). "context only, not for slides" is right. Crossref gives article pages 1-19. |

---

# Part 3: batch B remainder (claims from evidence 19, 19_cloud_removal_literature_2.md), added at the coordinator's request

## Cohen et al. 2018 (JAWRA 54(4):847–858) — `cohen2018_fwdet_floodwater_depth_JAWRA` (claims from evidence 19)

Copy read: the publisher's typeset early-view PDF (CSDMS repository), all 12 pages. Page numbers are the copy's (journal page = 846 + p).

| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | L268: "FwDET v1 … JAWRA 54:847 … Search summary of the abstract" | corrected | Now read in full (12 pp). Update the source note to "Full text (publisher early-view PDF, CSDMS copy)". |
| 2 | L269: "Depth is estimated from an inundation map and a DEM alone" | verified | "based solely on an inundation map and a digital elevation model (DEM)" (p. 1). |
| 3 | L269–270: "checked against hydraulic-model depth for a large event (10 m DEM) and a small one (1 m lidar)" | verified, with an addition | iRIC-FaSTMECH: Brazos 10 m, St. Vrain 1 m lidar (pp. 4–5). **Addition:** the *model's own extent* was the FwDET input, "to remove model-related errors" (p. 5), so the agreement excludes extent-mapping error. |
| 4 | L271: "Bias appears where the mapped extent does not fit the terrain" | verified | "considerable bias in locations where the inundation extent does not align well with the DEM" (p. 1); also from "projection or grid-cell alignment issues" (p. 8). |
| 5 | L271: "urban areas are among the difficult cases" | verified | "Complex inundation patterns and urban flooding are prone to localized hotspots of overestimation" (p. 11, conclusion 3). |
| 6 | (none) v1 numbers are absent from evidence 19 | addition | Brazos: means 1.95 vs 1.49 m, max 12.4 vs 12.5 m, "RMSD" 0.37 m (p. 6). St. Vrain: means 0.72 vs 1.28 m, max 4.64 vs 4.26 m, RMSD 0.38 m (p. 7). The paper defines "RMSD" as the average absolute difference (p. 6). My arithmetic: the differences of the means (0.46, 0.56 m) exceed the stated RMSD, so the cell sets differ. Do not combine these numbers. Both values fall within the "about 0.2–0.5 m" range of L317/L404. |
| 7 | L70 and L327–329: "FwDET's authors name roofs, highways, overpasses and dikes as error sources" | verified for v2.0 only | v1 does not name these. v1's named failures are narrow valleys (overestimate), reservoirs and large channels (underestimate), and urban/complex patterns, ponds and ditches (overestimate hotspots) (pp. 8, 11). The claim correctly cites v2.0; do not attribute it to v1. |
| 8 | L313/L316: "FwDET takes the water surface from the flood edge"; "Accuracy is checked against hydrodynamic models (FwDET)" | verified (for v1 too) | Nearest-boundary-cell elevation (pp. 3–4); validation against hydraulic models only. HWM validation is stated as future work (p. 11). |
| 9 | L456 reference row: authors, title, JAWRA 54(4), 847–858, DOI | verified | Matches Crossref. Online 17 Nov 2017; the copy's footer says "2017 … JAWRA 1-12". The "Search summary of abstract" status → Full text. |

## Zheng, D'Angelo, Maidment & Passalacqua 2022 (JAWRA 58(2):149–163) — `zheng2022_terrain_analysis_flood_mapping_harvey_JAWRA` (claims from evidence 19)

Copy read: the author's accepted manuscript (NOAA IR noaa:57036), all 34 pages. Page numbers are the manuscript's.

| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | L283–284: "Abstract (OpenAlex)" | corrected | Now read in full (accepted manuscript, 34 pp). |
| 2 | L285: "validated against high-water marks and observed extents" | verified, with a caveat | 1,072 USGS peak-summary points (pp. 6, 10). The "observed" extent is **reconstructed by running HAND with HWM depths** (p. 13), not an independently observed map. The only independent extent is DFO, and agreement with it is weak (overlap 26%, 21% statewide; p. 16). |
| 3 | L69 and L285: "Mean depth error about 0.5 m" | corrected | "about 0.5 m" is a **signed mean** (conclusion, p. 17), with "standard deviation around 2 to 3 m". As stated: uncalibrated −0.45 m (SD 3.60); reach-calibrated −0.68 m (SD 2.20), hit rate 41.9%; stream-order −0.39 m (SD 3.05); positive-depth points only +0.57 m (SD 0.94) (pp. 11–12, Table 1). With 1 m lidar and positive depths only: 0.27 m (SD 0.35), n = 30/49 (p. 14). |
| 4 | L285–286: "extent covers more than 90% of the high-water-mark-derived inundation" | corrected | 91.3% is the **ratio of total areas** (5,526 / 6,049 km²), not the share of the HWM extent that is overlapped. Per site, only 48.8% have an area ratio between 0.5 and 1.5, and "nearly 20%" are more than double (p. 13). On the lidar subset it is 72.5% (p. 15). |
| 5 | L286: "Calibrated roughness and lidar reduce the depth error but change the extent less" | verified | The lidar depth mean improves (−0.74 → −0.33 m, stream-order). Extent 72.5% vs 70.4% (pp. 14–15). Abstract: "does not affect as much the inundation extent estimation" (p. 2). |
| 6 | L316: "Accuracy is checked against … high-water marks (Zheng …)" | verified | pp. 9–10, Eqs. 2–5. |
| 7 | L317 / L404–405: "Reported depth errors run from about 0.2 to 0.5 m"; margin of 0.5 m "follows the reported depth errors of 0.18–0.5 m (… Zheng et al. 2022)" | corrected | For Zheng, 0.5 m is a signed mean with SD 2–3.6 m on the 10 m NED. Only the lidar positive-depth subset (49 points) gives 0.27 ± 0.35 m. A 0.5 m margin is not supported as an *error bound* by this paper. Base the margin on a spread (lidar SD) and on our own 3DEP ground check. |
| 8 | L329: flag roads on embankments, overpasses, bridges; "Check whether the 3DEP DEM is bare-earth at those structures" | verified (supporting addition) | "Many of the high-water marks were collected on roads and bridges across rivers in flood, whose elevations are not retained in the DEM" (hydro-enforcing; p. 14). |
| 9 | L330: "High-water marks record the peak" | verified | "the highest water levels (peak height of high water) during a flood" (p. 5). |
| 10 | L426 dataset table: 3DEP 1 m DEM "Used in Zheng et al. 2022" | corrected | Zheng used the **TNRIS 2017 lidar 1 m DEM** (Texas StratMap), plus the 1/3″ NED (p. 8). 3DEP is not named. Say "a 1 m lidar DEM, as in Zheng et al. 2022". |
| 11 | L441: "Harvey high-water marks used by Zheng et al. 2022: not located or tested" | addition | The data statement gives HydroShare resource 2836494ee75e43a9bfb647b37260e461 (p. 19). Located, not tested; no download per the rules. |
| 12 | (none) | addition | The DFO satellite maximum extent contains only 281/1,072 = 26.2% of HWMs (p. 16). This is direct evidence for visible-only or under-detected satellite flood labels (supports rec. #9). The HWM set also covers 3 SW Louisiana parishes (p. 6), which the paper did not use. |
| 13 | L485 reference row: authors, title, JAWRA 58(2), 149–163, DOI | verified | Matches Crossref (online 30 Jan 2022). |

## Johnson, Munasinghe, Eyelade & Cohen 2019 (NHESS) — `johnson2019_nwm_hand_flood_mapping_evaluation_NHESS` (claims from evidence 19)
| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Johnson et al. (2019), NWM–HAND evaluation, *NHESS* 19:2405 (l. 288; ref. table #16, l. 467) | verified | Title, authors, NHESS 19, 2405–2420 match the PDF and Crossref. Read depth is now full text, not "search summary" |
| 2 | "Compared with 28 remotely sensed inundation maps" (l. 289) | verified | 28 USFIMR maps (Landsat 5/7/8, Sentinel-1) plus 54 gauged reach catchments (abstract, p. 2405; Table A1, p. 2418) |
| 3 | "It underpredicts in low-order reaches" (l. 289) | verified (wording) | Abstract: underpredicts "in 4th-order and lower-order reaches" (p. 2405). Body defines lower-order as Strahler ≤ 3 (p. 2412). Floodplain means: 19% accurate, 27% over, 53% under (Table 2, p. 2409). In gauged (mostly high-order) catchments it over-predicts (44–47% vs 28–31%, Table 3, p. 2410) |
| 4 | Should be used "with caution" for deciding whether a cell is wet or dry (l. 290) | verified | "should be used with caution when identifying flood boundaries or making decisions of whether a cell is dry or wet" (abstract, p. 2405) |
| 5 | "HAND/NWM takes it [water level] from forecast stage over a drainage-relative DEM" (l. 314) | verified | NWM flow → synthetic rating curve (Manning, N = 0.05 CONUS-wide) → stage; depth = stage − HAND (pp. 2406–2407, Eq. 1, Fig. 1) |
| 6 | "NWM-HAND against Harvey high-water marks: mean depth error about 0.5 m" (l. 69) | not found (in Johnson) | Johnson evaluates **extent only** ("2-D fitness statistic", p. 2409); no depth, no high-water marks, no Harvey event. Evidence 19 attributes this number to Zheng et al. (2022) at l. 283–285, which is consistent; l. 69 should not be read as Johnson's result |
| 7 | Accuracy for depth/water-level methods is checked against hydrodynamic models, high-water marks or gauges (l. 316) | addition | Johnson checks against **satellite-classified extents** (USFIMR), plus gauge flows used as model input; a fourth reference type that l. 316 omits (p. 2408) |
| 8 | — | addition | Cell-level accuracy is low: floodplain mean A = 0.19 (Table 2); catchment mean A = 25% even with observed flow (Table 3). "HAND is not a physical model, it is unable to conserve volume" (p. 2413). Low relief is the named worst case: one reach floods "for any stage exceeding 0.5 m"; NED vertical accuracy 2.44 m (p. 2413). Relevant to flat coastal Louisiana |
| 9 | — | addition | Reference-map errors named by the authors: dark vegetation classified as water, Landsat 7 scan gaps, and a 40%-cloud Landsat scene (Flood ID 5) (pp. 2415–2416). Comparison is "at the time of image capture (not necessarily peak flooding)" (p. 2409). Supports evidence 19's peak-vs-pass caveat (rec. 8) |

## Gebrehiwot & Hashemi-Beni 2021 (ISPRS IJGI) — `gebrehiwot2021_3d_inundation_uav_segmentation_dsm_IJGI` (claims from evidence 19)
Full text **not obtained** (2026-10-29): the MDPI open-access PDF URL returned a 413-byte Akamai "Access Denied" HTML page
to curl (bot block, not a paywall; the article is gold OA, CC BY). A second route was refused as bot-check circumvention
and not pursued. OpenAlex lists no other PDF location (DOAJ entry is a landing page only). No claim could be checked
against the full text, so none is marked verified or corrected.

| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | Gebrehiwot & Hashemi-Beni (2021), *ISPRS IJGI* 10(3):144 (l. 296; ref. table #12, l. 463) | verified (metadata only) | Crossref: title, both authors, vol. 10, issue 3, article 144 match. Full text not read |
| 2 | UAV deep-learning flood polygons plus a pre-flood lidar DEM (Hurricane Matthew, Princeville NC) (l. 297) | not checked | Full text not obtained |
| 3 | Depth RMSE against USGS gauge levels: 0.26 m (DEM method), 0.34 m (SfM) (l. 298) | not checked | Full text not obtained |
| 4 | Accuracy checked against gauges (Gebrehiwot) (l. 316) | not checked | Full text not obtained |

## Li, Xu & Weng 2025 (Int. J. Appl. Earth Obs. Geoinf.) — `li2025_terrainfloodsense_cloudy_flood_mapping_JAG` (claims from evidence 19)
| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "Bayesian fusion of DSM, HAND and historical water occurrence fills cloud gaps in optical water maps" (l. 300) | verified | Inundation index = 0.3·norm(DSM) + 0.7·norm(HAND) (Eq. 2, p. 4); Bayesian fusion with GSW occurrence → EWO (Eqs. 3–9, p. 5); cloud pixels filled by a local adaptive threshold on EWO (Eq. 10, p. 6). Fusion is applied only where GSW occurrence < 5 (p. 5). |
| 2 | "Overall accuracy +2.95 to +8.86 points and F1 +0.038 to +0.087 over existing methods, on simulated experiments and large flood cases" (ll. 301–302) | corrected | These ranges are for the **extreme-flooding scenario only** (pixels with GSW < 5), from the **72 simulated experiments**, against two baselines: Zhao & Gao 2018 and the authors' own GSW-only method (Table 1, p. 7). Over all pixels the gains are +1.24 OA / +0.024 F1 vs the GSW-only method and +5.31 / +0.086 vs Zhao & Gao. The large-area case (Rio Grande do Sul) was checked **visually only**, against PlanetScope and NDVI, with no numbers (pp. 7–8). No significance test is reported. |
| 3 | "The reference data are not named in the abstract" (ll. 302–303) | addition | Full text: six cloud-free 1000×1000-px HLS patches, manually labelled by visual interpretation with Sentinel-2/PlanetScope help and checked against local flood reports (p. 6). Real HLS QA cloud masks (<30%, 30–60%, >60%) were overlaid on them. |
| 4 | "TerrainFloodSense: code on GitHub per the abstract; no dataset release located" (l. 444) | verified | Code: github.com/RCAIG/TerrainFloodSense (p. 1). Data availability: "Data will be made available on request" (p. 11). |
| 5 | Reference-table title "...via water occurrence and terrain." (l. 468) | corrected | The Crossref and article title ends "...via water occurrence and terrain **data fusion**" (p. 1). Vol. 144, article 104855 and DOI are correct. |
| 6 | Evidence row "Abstract" basis (l. 468) | addition | The full text has now been read (13 pp., published OA version). Inputs are all 30 m (HLS, GSW, AW3D30 DSM, global HAND); the water maps come from Prithvi-100M-Sen1Floods11. Named limits: DSM quality, and "above-ground rivers or artificial structures" (pp. 9–10). |

## Goldstein et al. 2021 (Earth and Space Science) — `goldstein2021_labeling_poststorm_coastal_imagery_ESS` (claims from evidence 19)
| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | "The Goldstein et al. (2021) labels on NOAA photos (Florence, Michael, Isaias) are image-level, not pixel-level" (l. 167) | verified | Each whole NOAA ERI image gets answers to fixed questions (Table 1, p. 6). There are no masks or boxes; bounding boxes are only proposed as future work (p. 16). Flights: 20180917a (Florence, NC), 20181011a (Michael, FL), 20200804a (Isaias, NC/SC) (p. 3). |
| 2 | Labels for "about 1,600 NOAA aerial images" (l. 430) | verified | "A total of 1,600 images were labeled by at least two or as many as seven coastal scientists" (p. 1). Total 6,600 labels (p. 5). Addition: the images were chosen by an active-learning washover model, so they are not random (pp. 3–4). |
| 3 | "Image-level labels (all water, damage, washover, development)" (l. 430) | corrected | The questions also cover the **impact regime** (swash, collision, overwash, inundation; Sallenger scale) and **terrain** (sandy coastline, marsh, river → estuary/bay, inland). "Development" became "Buildings" and "damage to infrastructure" became "damage to buildings" in Experiments 2–3 (Table 1, p. 6). There is no road or street-flood question. |
| 4 | "by trained coastal scientists; inter-rater agreement measured" (l. 430) | verified | 22 coastal scientists; percent agreement and Krippendorff's alpha (pp. 3, 6). Caveat in the paper: their "specific areas of expertize may not be interpretation of poststorm aerial images" (p. 5). A pilot with 4 non-experts on 100 images was also run (p. 15). |
| 5 | "CSV labels"; Zenodo files `ReleaseData_v3.csv`, `ReleaseDataNCE.csv`, `ReleaseDataQuads.csv`; CC BY 4.0 (l. 430) | not found | The paper cites the Zenodo dataset v1.4 (doi 10.5281/zenodo.5172799, p. 17) but gives no file names, format or dataset licence. The article itself is CC BY (p. 1). Not re-checked, since no download was allowed. |
| 6 | Use: "Precedent and template if we ever label Ida NOAA photos for flooding" (l. 430) | addition | The full text gives concrete protocol evidence. A manual plus refined questions raised damage alpha from 0.48 to 0.75. Image quarters raised washover alpha from 0.44 to 0.61 (Tables 3–4, pp. 8, 10). Process labels are weak: "inundation" alpha was 0.09 / 0.13 (p. 8). Labels were released **unreconciled** (p. 14). |
| 7 | Reference row: "Earth and Space Science 8"; DOI; data https://zenodo.org/records/5172799; basis "Metadata + Zenodo page" (l. 464) | verified | Vol. 8, issue 9, e2021EA001896; DOI correct (p. 1). The full text has now been read (18 pp., published version from Southampton EPrints). |

## Zhang, Isola, Efros, Shechtman & Wang 2018 (CVPR) — `zhang2018_lpips_deep_features_perceptual_metric_CVPR` (claims from evidence 19)

| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | L137: "LPIPS (Zhang et al. 2018, CVPR; metadata): similarity from deep-network features." | verified (read level should now be "Full text") | Eq. 1, p. 591: channel-unit-normalised activations from L layers, scaled per channel by w_l, squared L2, averaged over space, summed over layers; w_l = 1 is cosine distance. LPIPS = this distance with w (lin) or the network (tune/scratch) trained on human 2AFC judgements (p. 591). |
| 2 | L484 reference row: Zhang, Isola, Efros, Shechtman & Wang (2018), CVPR 2018, 586–595, DOI 10.1109/CVPR.2018.00068; "CVPR; Adobe co-authors"; read = Metadata | verified (update read level to Full text) | Crossref and CVF copy: title, five authors, pp. 586–595 match. Affiliations p. 586: UC Berkeley (Zhang, Isola, Efros), OpenAI (Isola), Adobe Research (Shechtman, Wang). |
| 3 | L164: "I found no paper using a per-pixel DINO or CLIP feature *distance* to a reference as the score." | addition | Literally true for this paper (it uses SqueezeNet/AlexNet/VGG and self-supervised AlexNet variants, p. 590, not DINO/CLIP). But LPIPS is itself a **per-location deep-feature distance to a reference**, spatially averaged (Eq. 1, p. 591), so it is the closest precedent for our "feature distance as primary" design (L171) and should be cited as such. |
| 4 | L171: "feature distance as primary" is supported | addition (scope) | Support is from natural-photo 64×64 patches only: uncalibrated ImageNet features agree with humans 68.6/68.9/67.0% (Squeeze/Alex/VGG) vs L2/SSIM/FSIM 63.2/63.1/63.8%, human ceiling 73.9% (p. 592). No overhead, hazy or remote-sensing imagery in BAPPS (pp. 588–590). |
| 5 | (not in evidence 19) | addition | Deep features are "more sensitive to blur" than SSIM, and BiGAN treats correlated noise as a smaller distortion than SSIM does (p. 593); spatial distortions (shift, warp) are part of the training distortions (p. 589), so misregistration/building lean will raise LPIPS. |
| — | L110 (AllClear "No LPIPS"), L116 and L161 (DE uses LPIPS) | not checkable here | These concern other papers' use of LPIPS; nothing in Zhang 2018 bears on them. |

## Fu, Tamir, Sundaram, Chai, Zhang, Dekel & Isola 2023 (NeurIPS) — `fu2023_dreamsim_human_visual_similarity_NeurIPS` (claims from evidence 19)

| # | Claim in evidence 19 | Verdict | Full text (page) |
|---|---|---|---|
| 1 | L138: DreamSim (Fu et al. 2023, NeurIPS; abstract) is "trained on human judgements". | verified, with addition | Trained on NIGHTS: 20,019 **synthetic Stable Diffusion v1.4** triplets with unanimous AMT 2AFC votes (pp. 3–5, 17–18); LoRA-tuned DINO+CLIP+OpenCLIP ensemble with hinge loss, margin 0.05 (p. 6). Read level should now be "Full text". |
| 2 | L138–139: It "outperforms both prior learned metrics and recent large vision models" | corrected (scope) | The abstract ends "…on these tasks", i.e. retrieval and reconstruction on real images (p. 1). On human 2AFC alignment it also leads (NIGHTS 96.2% vs LPIPS 70.7, DISTS 86.0, DINO 90.1; Table 5, p. 20), but on IQA benchmarks **LPIPS beats it** (SROCC TID2013 0.838 vs 0.814; KADID-10k 0.883 vs 0.868; "LPIPS and FSIM remain best-performing overall", Table 8, p. 23). |
| 3 | L139: it "weights semantic content and layout over low-level colour and texture" | corrected | Abstract: it "focuses heavily on foreground objects and semantic content while also being **sensitive to color and layout**" (p. 1). Colour and layout are things it is sensitive to, not things it de-weights; vs DINO/OpenCLIP "color explains more of our model's decisions"; vs LPIPS/DISTS it aligns less with RGB-histogram similarity (p. 8, Fig. 7). Ablating colour, shading or structure hurts it; orientation does not (p. 7). |
| 4 | L462 reference row: Fu, Tamir, Sundaram et al. (2023), NeurIPS 36, 50742–50768, DOI 10.52202/075280-2208; read = Abstract | verified (update read level to Full text) | Crossref record matches title, 7 authors (Fu, Tamir, Sundaram, Chai, Zhang, Dekel, Isola), pp. 50742–50768 (= 27 pages = the proceedings PDF). The DOI is Crossref-registered (publisher NeurIPS Foundation) and resolves to proceedings.com. Co-author R. Zhang is Adobe Research (p. 1). |
| 5 | L164: "I found no paper using a per-pixel DINO or CLIP feature *distance* to a reference as the score." | verified, with addition | DreamSim does use DINO and CLIP feature distance to a reference, but as **one global cosine distance per image** (CLS/embedding vector, p. 5), not per pixel, so the statement stands. It is the nearest precedent for "DINO/CLIP feature distance as a similarity score" on natural images. |
| 6 | (not in evidence 19) | addition | Directly relevant caveat: DreamSim is "less sensitive to 'stuff' categories, such as sky and road" than LPIPS/DISTS (p. 8, Fig. 7), and background removal matters less than foreground removal (p. 8). Inputs are resized to 224×224 (p. 18). Dataset is object-centric (p. 27). This argues against DreamSim as a road-focused haze-removal score. |

## Ding 2024 (TGRS), Chen 2017 (J. Hydrol.), Peter 2022 (GRSL) — evidence 19
Re-checked author/lab sites on 2026-10-29: no open copy (see ledger_C rows). Claims not checked; on the GMU list. Note the open CVF paper by Ding et al. (ACCV 2022) is a different, earlier paper, and NOAA repository noaa_58788 is Cohen et al. 2022 (Remote Sens.), not Peter et al. 2022.
