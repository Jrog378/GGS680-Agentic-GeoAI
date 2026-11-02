# Claim checks, batch A (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Each claim the evidence files make about a paper is checked against the full text
and marked **verified**, **corrected** (the paper says something different; the correction is given) or **not found**.
Page numbers are the journal's. The evidence files themselves were not edited.

## He, Sun & Tang 2011 (TPAMI) — `he2011_dark_channel_prior_haze_removal_TPAMI`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | Raw t's "main problems are some halos and block artifacts. This is because the transmission is not always constant in a patch"; fixed with soft matting | verified | p. 2345 (§4.1 end), soft matting §4.2 p. 2345–2346 |
| 2 | 10 | "The dark channel of a hazy image approximates the haze denseness" (§4.3), used to find the most haze-opaque region | verified | p. 2347 §4.3; also p. 2344 ("rough approximation of the thickness of the haze") |
| 3 | 10 | 15 × 15 on 600 × 400; larger patch makes the prior more valid but "if the patch size is too large, halos near depth edges may become stronger" (§4.5) | verified | p. 2348 §4.5 |
| 4 | 10 | Smaller patch: prior "is less accurate for a small patch, and the recovered scene radiance is oversaturated" | verified | p. 2348 |
| 5 | 10 | He's dark channel is the minimum filter alone (our box blur is an addition) | verified (eq. 5 is min over channels then min filter; the refinement in 2011 is soft matting + a bilateral filter, not a box blur) | p. 2343, p. 2346 |
| 6 | 10 | ω = 0.95 keeps "a very small amount of haze for the distant objects"; "the value of ω is application based" | verified | p. 2344–2345 |
| 7 | 10 | Airlight: top 0.1% brightest dark-channel pixels, then highest intensity in I; beats brightest pixel which can be "a white car or a white building" | verified | p. 2347 |
| 8 | 10 | J = (I − A)/max(t, t0) + A, "a typical value of t0 is 0.1", J "prone to noise" where t ≈ 0 | verified | p. 2348 §4.4 |
| 9 | 10 | Eqs. 8–11 and 13 (t constant in patch; t1, t2 generalisation) | verified | p. 2345 |
| 10 | 10 | Fails where objects are "inherently similar to the atmospheric light" (white marble); "the constant-airlight assumption may be unsuitable when the sunlight is very influential" | verified | p. 2352 §6 |
| 11 | 10 (by implication, "greyscale" row cites only He 2013 and Tarel) | — | addition | p. 2349: the 2011 paper itself says the method "also works for gray-scale images if there are enough shadows", omitting min_c. Our notes do not cite this; it is direct support for the greyscale rule, with the shadow condition |
| 12 | 10 | Soft matting λ (not stated in notes) | addition | λ = 10⁻⁴, then a bilateral filter on t (p. 2346) |

## He, Sun & Tang 2013 (TPAMI) — `he2013_guided_image_filtering_TPAMI`
Page numbers are the author copy's 1–13.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | Before guided filtering the raw transmission, "we first apply a max filter to counteract the morphological effects of the min filter", guide = the hazy image (§5) | verified | p. 11, §5 "Single image haze removal" |
| 2 | 10 | Dehazing parameters r = 20, ε = 10⁻³ on a 600 × 400 image | verified (Fig. 16 caption; "this 600 × 400 image" in text). Note: intensities are in [0, 1] (Fig. 2 caption), so ε = 10⁻³ ≈ 65 grey-levels² on 0–255 data | p. 11 |
| 3 | 10 | The guide "can be the input image itself or another different image"; the filter "can transfer the structures of the guidance image to the filtering output" | verified | abstract p. 1; §3.6 p. 7 |
| 4 | 10 | Local linear model "is more likely to be valid in the RGB color space than in gray-scale"; grey guide gives halos where an edge is not distinguishable in grey (§3.5, Fig. 8) | verified | p. 6–7 |
| 5 | 10 | Limitations: "may exhibit halos near some edges"; "Halos are unavoidable for local filters when the filters are forced to smooth some edges" | verified | p. 11 |
| 6 | 10 | Our earlier test (r 60, ε 10⁻⁴, no max filter) "was not He's recipe" | verified as a comparison: the paper's ε is 10× larger, r smaller relative to image, max filter first | p. 11 |
| 7 | 10 | He 2013 is "MSRA; company" | verified (He and Sun at Microsoft Research Asia; Tang at CUHK) | p. 1 footnote |

<!-- group g1 -->
# Claim checks, group g1 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (the paper says something different; the
correction is given), **not found**, **addition** (something the paper says that our notes should use). Page numbers are
the journal's unless stated. The evidence files themselves were not edited.

## Zhu & Woodcock 2012 (RSE) — `zhu2012_object_based_cloud_shadow_detection_landsat_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§1 step 1, blobs ≥ 2,500 m²) | "For cloud objects less than 3 pixels, Fmask excludes them from cloud mask … as most of them are misidentification of small bright cold noncloud pixels"; 3 × 30 m px = 2,700 m² | verified (quote and page correct; strictly, objects of < 3 px are removed, so the smallest kept object is 3 px = 2,700 m²) | p. 88 |
| 2 | 10 (§1 step 6, reporting) | Producer's accuracy matters more; missed cloud "will greatly undermine future analyses like change detection … the only consequence is a little lost data" | verified | p. 89 |
| 3 | 10 (§2 arm a) | Zhu & Woodcock 2012 "prefer commission to omission" | verified ("We think commission is better than omission in cloud detection") | p. 92 (and p. 89) |
| 4 | 10 (§1 step 5, t faded over 20 m) and §2 N3 | Cited with Zhu 2015 and Claverie 2018 for "operational masks treat the near-cloud band as contaminated and remove it"; N3 lists "Fmask" among systems that "remove the dilated band" | **corrected** for the 2012 paper: Fmask 2012 does **not** dilate or buffer the cloud mask. Its only buffer is 3 px (8-connected) on *matched cloud shadows*, "to fill those small holes", and it is what makes Fmask over-estimate shadow (p. 91). Cloud clean-up in 2012 is a 3 × 3 majority rule (≥ 5 of 9 → cloud). Cite Zhu, Wang & Woodcock 2015 (and the software README) for cloud dilation, not 2012 | p. 87, p. 88, p. 91 |
| 5 | 02 (item 6) | Fmask pairs a shadow with its cloud through sun and view geometry | verified (object matching along the projected direction over a BT-derived height range; similarity threshold 0.3) | pp. 87–88, Fig. 3 |
| 6 | 10 (§2 N3) | Fmask's "stated reason" for removing the band is that missed cloud "will greatly undermine future analyses like change detection" | **corrected**: that sentence is the paper's argument for weighting producer's over user's accuracy in assessment (p. 89), not a stated reason for a buffer (2012 has no cloud buffer) | p. 89 |
| 7 | — | (not in notes) | addition: Fmask's land threshold is scene-learned: 82.5th percentile of cloud probability over the scene's clear-land pixels + 0.2 (eq. 17); a direct precedent for learning our cut per tile from its own clear pixels | p. 87 |
| 8 | — | (not in notes) | addition: Fmask misses "thin and warm" cloud and calls it "actually haze or aerosols" to be removed by atmospheric correction, i.e. the 2012 mask deliberately leaves haze to a correction step, matching our detect-opaque/correct-thin split | p. 92 |
| 9 | — | (not in notes) | addition: the HOT test used in Fmask is `B1 − 0.5·B3 − 0.08 > 0` on TOA reflectance (eq. 3), a fixed-slope version of Zhang et al. 2002's HOT | p. 85 |

## Canty & Nielsen 2008 (RSE) — `canty2008_automatic_radiometric_normalization_irmad_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§1 step 2) | Relative normalisation assumes a linear relation over "regions of constant reflectance"; "the critical aspect is the determination of suitable time-invariant features" | verified | p. 1025 |
| 2 | 10 (§1 step 2) | Cloud pixels were "correctly identified as change" | verified (exact: "all cloud and cloud shadow pixels are correctly identified as change", April 2001 ASTER image, Iran) | p. 1032 |
| 3 | 05 (line 191) | IR-MAD re-weighting excludes changed pixels and "was built for scenes with a lot of change" | verified ("Substantial improvement … for scenes which exhibit a high proportion of change"); add the paper's own caveat: below some number of truly invariant pixels it "will fail", converging to whatever is most correlated and in the majority (Jülich May–Aug) | abstract p. 1025; p. 1034 |
| 4 | 05 (line 28), 10 (§3 item 4) | IR-MAD normalisation on no-change pixels; experts normalise on invariant pixels | verified (no-change probability > 95%, then orthogonal regression) | p. 1028 |
| 5 | 05 (line 146–147, 230) | Read depth "abstract, DTU record" / "not yet read in full" | superseded: now read in full (evidence 10 already says full text) | — |
| 6 | 05 (line 201) | Fit `after ≈ g·before + o` "with IR-MAD-style re-weighting" in windows | partly: the paper's fit is global per image pair and uses **orthogonal**, not ordinary, regression; weights are χ² no-change probabilities iterated to convergence (20–30 iterations). Windowed use is our extension | pp. 1028, 1035 |
| 7 | — | (not in notes) | addition: the paper standardises the MAD variates with the **re-weighted** σ (eq. 4), departing from Nielsen 2007, because it worked "considerably better" when change dominates; quality control = paired t-test and F-test on held-out invariant pixels | p. 1028, p. 1031 |

## Nielsen 2007 (IEEE TIP) — `nielsen2007_regularized_iteratively_reweighted_mad_change_detection_TIP`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 (line 146) | MAD change is invariant to a separate gain/offset (affine) transform of each date | verified | abstract p. 463; p. 465 |
| 2 | 05 (line 146), 10 (§1 step 2) | Iterations give "large weights … to observations that show little change", so the fit is driven by no-change pixels | verified (weight = P{χ²(p) > T}, eq. 13) | p. 463; p. 466 |
| 3 | 05 (line 28) | "IR-MAD normalisation on no-change pixels (Nielsen 2007 …)" | partly: Nielsen 2007 is a change-detection paper; it only says no-change pixels "are suitable" for normalisation and refers to Canty et al. 2004 for it. The normalisation recipe (95% threshold, orthogonal regression, t/F tests) is Canty & Nielsen 2008 | p. 466 |
| 4 | 10 (refs #18), 05 | Read depth "abstract" | superseded: now read in full | — |
| 5 | — | (not in notes) | addition: σ in the χ² statistic is the SD of **all** observations here ("minimal effect" only if few pixels changed); Canty & Nielsen 2008 replaced it with the re-weighted σ for change-dominated scenes — relevant to flood tiles | p. 465 |
| 6 | — | (not in notes) | addition: at 5 m (HyMap) the leading change variates were dominated by building/tree edge effects, sun-angle differences and misregistration — expect the same at 0.5 m | p. 472 |
| 7 | — | (not in notes) | addition: stop rule = max |Δρ| < ε, e.g. 10⁻⁶; labels by χ² percentiles (change > 99%, no-change < 1%) | p. 466 |

## Zhu, Wang & Woodcock 2015 (RSE) — `zhu2015_improvement_expansion_fmask_landsat_sentinel2_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 ("In short" 2; §2 arm a) | "The pixels surrounding clouds and cloud shadows are masked out in the Fmask algorithm because many of these pixels may still be influenced by the thin edges of clouds and their shadows" | verified (exact quote). Context our notes omit: it sits in the "Snow Detection II" paragraph as background for the new *snow* dilation, it cites Zhu & Woodcock 2012 for the cloud/shadow buffer (which the 2012 paper does not actually describe for cloud — see 2012 row 4), and **no buffer width is given** | p. 273 |
| 2 | 10 (§1 step 1, thin edge; §2 limits) | "Optically thin clouds are difficult to detect as they may have spectral signatures similar to the Earth surface underneath" | verified | p. 269 |
| 3 | 10 (§1 step 2, clear pixels 10 m from the gate) | Cited for "pixels next to clouds are still influenced by thin edges" | verified as a principle; the paper gives no distance, so the 10 m margin remains our own value | p. 273 |
| 4 | 10 (§1 step 5, fade) | Cited with 2012 for "operational masks treat the near-cloud band as contaminated and remove it" | verified for 2015 (masked out, not corrected); width user-set ("any positive integer") — stated in the paper for snow; for cloud the 3 px default is from the software README only | p. 273 |
| 5 | 10 (§2 arm a, limits) | Newest Fmask README recommends less dilation | not in this paper (README claim; not checked here) | — |
| 6 | — | (not in notes) | addition: cloud over water now uses a scene-learned cut (82.5th percentile of clear-water probability + 0.2), and the "> 99% probability = cloud" shortcut was removed for commission on bright cold ground | p. 272 |
| 7 | — | (not in notes) | addition: reported accuracies (91%, 89%, 3%) are on 200 points sampled **only inside disagreement areas** between two simulated band scenarios — not whole-scene accuracy; do not quote them as Fmask accuracy | pp. 274–276 |
| 8 | — | (not in notes) | addition: without thermal (Sentinel 2 scenario) shadow matching uses a fixed 200–1,200 m cloud height and flat-plate clouds — the setting closest to ours | p. 274 |

## Du, Teillet & Cihlar 2002 (RSE) — paywalled, not checked
OpenAlex: closed, no repository copy. The NRCan preprint (GEOSCAN 219814,
`download-telecharger.services.geo.ca/.../219/219814/13115.pdf`, found by web search) returns HTTP 404, as do the
`ftp.maps.canada.ca` / `ftp.geogratis.gc.ca` mirrors; no Wayback snapshot. Status `paywalled`: needs Justin's GMU login.
Our notes (evidence 05 line 150, evidence 10 refs #4) correctly flag their read depth as abstract only.

## Zhang, Guindon & Cihlar 2002 (RSE, HOT) — paywalled, not checked
OpenAlex: closed. The NRCan preprint (GEOSCAN 219820, `.../219/219820/13121_1.pdf`) is still 404 (also on the two FTP
mirrors; no Wayback snapshot). Status `paywalled`: needs Justin's GMU login. Indirect check only: Fmask 2012 (p. 85)
uses a TOA-reflectance HOT test `B1 − 0.5·B3 − 0.08 > 0` and states that Zhang et al.'s HOT "is built empirically from
regression of DN values from clear-sky pixels" (the clear-sky line), and Fmask 2012 (p. 84) says the clear-line idea
"fails when the surface reflectance is bright, as is the case for rocks, snow, ice, sand". Evidence 10's note that only
HOT's detection side was read (through Fmask) stands; the compensation (removal) step remains unread.

## Schott, Salvaggio & Volchok 1988 (RSE) — paywalled, not checked
OpenAlex: closed. RIT Digital Archive record (handle 1850/4360) is metadata only (it gives pp. 1–14; Crossref/our notes
1–16). No open full text found. Status `paywalled`: needs Justin's GMU login. Our notes (evidence 10 refs #22) correctly
list it as metadata only; the only verified content is via Canty & Nielsen 2008 (p. 1025), which cites it among the
invariant-feature normalisation methods.

## Qiu, Zhu & He 2019 (RSE, Fmask 4.0) — `qiu2019_fmask4_cloud_shadow_detection_landsat_sentinel2_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (refs #32, line 363) | Read depth "metadata"; author PDF too large to fetch | superseded: downloaded with curl (29 MB) and read in full | — |
| 2 | 10 (§2 arm a "For": "every operational mask dilates cloud") | Implied to hold for Fmask generally | **corrected** for the published Fmask 4.0 method: its accuracy assessment uses "no dilation for cloud pixels" (shadow dilated 3 px). The 500 m dilations in the paper are around urban and mountain snow false positives, not around cloud. Cloud dilation is a software option, not part of the published method's numbers | p. 11, p. 10 |
| 3 | 10 (§2 arm a, limits) | Newest Fmask README recommends 1 px (L8–9) / 0 px (S2) cloud dilation | not in this paper (README claim; consistent with item 2) | — |
| 4 | — | (not in notes) | addition: a HOT-based cloud probability using only blue and red, normalised between the 17.5th and 82.5th percentiles of clear-land HOT ± 0.04, replaces temperature for Sentinel-2 and recovers low clouds; HOT is unreliable on "very bright land surfaces, such as urban" | p. 8 |
| 5 | — | (not in notes) | addition: bright-surface false positives are removed by disk erosion then two dilations capped at the original mask (radius 90–150 m at 30 m); erosion costs small clouds | pp. 10–11, 17 |
| 6 | — | (not in notes) | addition: threshold offset now sensor-specific (0.1 / 0.175 / 0.2), "global optima but not regional optima"; validation excluded unsure (often thin-cloud) samples, so reported OA overstates thin-cloud performance | pp. 9, 5, 16 |

<!-- group g2 -->
# Claim checks, group g2 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (the paper says something different; the
correction is given), **not found**, or **addition** (useful content our notes lack). Evidence files were not edited.

## Hagolle, Huc, Villa Pascual & Dedieu 2010 (RSE) — `hagolle2010_multitemporal_cloud_detection_RSE`
Locations are manuscript line numbers (l.) of the HAL preprint.
| # | Evidence | Claim | Verdict | Full text (location) |
|---|---|---|---|---|
| 1 | 02, 10 | Flags cloud from a per-pixel jump in blue reflectance | verified, with detail our notes lack: the jump is against a per-pixel composite of the most recent clear value (not simply "the previous image"), threshold 0.03·(1 + (D − Dr)/30) in Rayleigh-corrected reflectance, computed at 100 m (FORMOSAT-2) / 240 m (Landsat), not at native 8 m | l. 148–161, eq. 1 |
| 2 | 02, 10 | "together with a test of how linearly correlated pixel neighbourhoods are between successive images" | corrected in role: the correlation test is a **veto**, not a second detection cue. A pixel that passes the blue test is un-flagged if its neighbourhood correlates well with the same neighbourhood in any of the **ten previous images**. The window size and correlation threshold are not given in the preprint | l. 179–195 |
| 3 | 10 | "implemented in CNES's MAJA" | not found as stated: the paper (2010) says MTCD "will be included in VENµS operational level 2 processing" and "will be proposed for SENTINEL-2"; MAJA is not named | l. 84–85, 28–29, 290–292 |
| 4 | 10 (l. 349) | Open question: does it dilate the mask? | answered: yes, "Dilatation is 2-pixel wide at reduced resolution, ie 200m for FORMOSAT-2 and 480m for LANDSAT", because thin cloud fringes thick cloud | l. 218–220 |
| 5 | 02 | Applied to "FORMOSAT-2 at 8 m and others" | verified, but processing is at 100 m, so it is not an 8 m pixel-level detector | l. 152–154 |
| 6 | — | — | addition: a second veto, not in our notes: red rise > 1.5 × blue rise → surface change (ploughing, harvest, drying), not cloud | l. 173–178, eq. 2 |
| 7 | — | — | addition: water must be masked first; high AOT (< 0.7) passes as clear, AOT > 1 flagged; the correlation veto "sometimes reclassifies as unclouded the images with very thin clouds" | l. 162–165, 191–195 |
| 8 | 10 | "Partly: a precedent for 'rise against a clear reference'" | verified as a fair rating. Validation in the paper is visual and catalogue cloud-percentage only (no pixel accuracy) | l. 221–263 |

## Claverie et al. 2018 (RSE) — `claverie2018_harmonized_landsat_sentinel2_RSE`
Source used: NASA NTRS publisher copy (not the local file with the earlier summary prepended).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | LaSRC: "Adjacency cloud is applied over 150 m windows (i.e., five 30 m pixels with the window size selected empirically) surrounding cloudy pixels" (§3.3.1) | verified (quote exact). Note: this is the **Landsat 8** LaSRC mask only; HLS Sentinel-2 products use Fmask (no buffer width stated in this paper) | p. 148 |
| 2 | 10 | "Operational masks treat the near-cloud band as contaminated and remove it" (row 5) | verified for L30 (hard buffer). The paper does not describe a fade or any correction inside the buffer, consistent with our note that correcting in the buffer is our own extension | p. 148 |
| 3 | 10 | Read in full from disk (§3.3) | corrected source: this batch used the NTRS open copy (17 pp., 145–161), which matches the journal; the earlier on-disk file had a summary page prepended | — |
| 4 | — | — | addition: QA "presence" rule — any flagged pixel in the inner 2 × 2 of the resampling kernel flags the output, "to avoid introduction of new cloud masking omission errors" | p. 149 |
| 5 | — | — | addition: LaSRC L8 cloud thresholds = AOT-inversion residual 0.05 and TIRS BT 305 K; cited performance 4.7% omission / 24% commission (Foga et al. 2017) | p. 148 |
| 6 | — | — | addition: authors flag the S-2 (Fmask, no thermal) mask as the main known issue (omissions), and say temporal outlier filters can mistake "real surface changes" for cloud; they name MACCS/MAJA (Hagolle 2010) as promising but needing better-than-monthly clear revisits | p. 154–159 |

## Lin, Lin, Lee & Chen 2015 (ISPRS JPRS) — paywalled, needs Justin's GMU login
OpenAlex: closed, no repository copy; Semantic Scholar: closed; two web searches found only the abstract (NASA MODIS
publications page) and a related NCKU master's thesis record (Lin Bo-Yi, 2014, no full text). Claims not checked.
Abstract-level facts seen in search results (not verified against full text): weighted PCA selects invariant pixels
from a cloudy Landsat-7 ETM+ time series; reference images built from them; cloud-detection F-measure gains of 1.1–6.9%.

## Lin, Tsai, Lai & Chen 2013 (IEEE TGRS) — paywalled, needs Justin's GMU login
OpenAlex and Semantic Scholar: closed; one web search found only abstract/metadata pages. Claims not checked.

## Hagolle, Huc, Villa Pascual & Dedieu 2015 (Remote Sensing) — `hagolle2015_multitemporal_aerosol_thickness_RemoteSens`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05, 10 | MT method "assumes that the surface reflectances are stable with time" | verified (abstract wording exact); §3.3.1 states two assumptions: AOT varies faintly with distance, surface reflectance varies slowly with time | p. 2668, 2676 |
| 2 | 05, 10 | Degrades for "a very quick variation of landscape" | verified; worked example is the Yaqui plain drying in May (four dates with AOT error > 0.1) | p. 2668, 2685–2686 |
| 3 | 10 | Multi-temporal haze correction is established (CNES) | verified: MACCS, used at the THEIA land data centre for Landsat 5/7/8 and FormoSat-2, planned for VENµS/Sentinel-2. Note it estimates **AOT** for a radiative-transfer correction, not an image-space haze/transmission map | p. 2670, 2688 |
| 4 | 05 | "A flood is such a change" (our inference) | consistent with the paper's stated failure mode; floods are not discussed in the paper | p. 2686 |
| 5 | — | — | addition: how changed pixels are handled: pixels whose NIR (FormoSat-2) or SWIR (Landsat) reflectance "has changed too much" are excluded (threshold not given); ≥ 40% valid pixels per 7 × 7 coarse neighbourhood; AOT-insensitive (bright, ~0.25 blue) pixels excluded | p. 2676–2677 |
| 6 | — | — | addition: MT needs two clear dates < ~2 months apart; temporal weight 1200/((D − Dr)² + 800); dark-object ceiling (darkest blue pixel, also dark on previous date, assumed 0.01 reflectance) | p. 2681–2682, 2684 |
| 7 | — | — | addition: tested AOT never above 0.7 (≤ 0.4 Landsat stable cases), so performance under heavy haze is untested | p. 2673 |
| 8 | 10 | Journal JIF "4.3 (narrow)" | not checked (not in the paper) | — |

## Hagolle, Dedieu, Mougenot, Debaecker, Duchemin & Meygret 2008 (RSE) — `hagolle2008_multitemporal_aerosol_correction_formosat2_RSE`
Locations are manuscript page numbers (ms p.) of the HAL author manuscript.
| # | Evidence | Claim | Verdict | Full text (location) |
|---|---|---|---|---|
| 1 | 05 | "Multi-temporal aerosol correction, Formosat-2" (title-level) | verified | ms p. 1 |
| 2 | 05 (l. 220) | Open question: "The stable-surface assumption; check how it handles pixels that did change" | answered: pixels are excluded by a threshold on the **NIR TOA reflectance change** between consecutive images (value not given), because NIR is "not too sensitive to the aerosol content"; inversion is skipped if fewer than **50%** of the 7 × 7 (100 m) neighbourhood is clear and stable | ms p. 15 |
| 3 | 05 (l. 204) | Cited as a source for "abstain if a window has too few invariant pixels" | verified: the 50% clear-and-stable rule is exactly that | ms p. 15 |
| 4 | — | — | addition: the two-date cost alone is undetermined when the AOT barely changes (|ΔAOT| < ~0.1); a prior from the previous iteration is needed. With only two dates we are in the v1 situation, but we avoid it by fixing the ground's dark channel from the clear date rather than fitting both dates' atmospheres | ms p. 9–10 |
| 5 | — | — | addition: simulations show error rising sharply when landscape-change noise exceeds SNR 100; uniform and bright ground bias the estimate; method cannot run at full resolution (100 m used for 8 m data) | ms p. 11–13, 20; Tables 1–2 |
| 6 | — | — | addition: semi-transparent cloud missed by the cloud mask is absorbed as aerosol | ms p. 17–18 |

## Makarau, Richter, Müller & Reinartz 2014 (IEEE TGRS) — `makarau2014_haze_detection_removal_multispectral_TGRS`
Page numbers are the early-access 1–11 (journal page = 5894 + n).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02, 10 | Builds a haze-thickness map for uneven haze by extending dark-object subtraction locally | verified: minimum in non-overlapping w × w windows (w = 3 typical), 3 × 3 median, cubic interpolation | p. 1–4 |
| 2 | 02, 10 | "Tested on WorldView-2" | verified, but only qualitatively (spectra inside/outside haze, Munich scene); the only same-area haze-free comparison is on **Landsat 8** (7 days apart). No numeric accuracy for either | p. 7–10 |
| 3 | 02 | Stated limit: uniform, highly reflective land cover | verified ("absolutely flat and highly reflective surfaces (desert and snow)") | p. 11, also p. 3 |
| 4 | 02, 10 | "Closest published match for selective de-hazing on VHR" / "the closest VHR haze-thickness method" | partly corrected: it is a **single-date, multispectral, additive** method (no transmission term). Its WorldView-2 data are the 2 m multispectral bands, not 0.5 m pan; it needs at least two short-wavelength bands for the extrapolated band. "Closest at VHR" is fair; "selective" fits only in that the HTM is spatially varying (there is no cloud/haze gate — every pixel is corrected, with a mean-threshold haze mask used only for statistics) | p. 2–7 |
| 5 | 10 (l. 351) | Open question: how the HTM handles haze edges on WorldView-2 | answered: window trade-off only (larger window smooths haze borders and underestimates HTM; Fig. 2); the WorldView-2-specific edge issue is band-group **parallax** shifting the haze, solved by two HTMs and a local 10 × 10 stretch. Triangulation border effects are listed as future work | p. 2–3, 9, 11 |
| 6 | — | — | addition: eq. 10 clear-area offset re-adds the mean haze-free-area difference so clear-scene aerosol is not removed; ATCOR visibility 19.9 vs 20.6 km shows clear scenes are barely changed | p. 6, 10 |
| 7 | — | — | addition (paper inconsistency): eq. 5 says w = 21 for per-band HTMs, pseudocode uses w = 3; printed Landsat K has red (0.886) above green (0.816), contrary to the stated monotone rule | p. 5, 7 |

## Zeng, Shen & Zhang 2013 (RSE) — `zeng2013_slcoff_multitemporal_regression_gapfill_RSE`
Source: Elsevier "author's personal copy" on the authors' WHU lab site (its cover notice restricts posting; private study only).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "Multi-temporal regression for SLC-off gaps" | verified | p. 182 |
| 2 | 05 | Hagolle 2008 and Zeng 2013 "needs GMU" | corrected: both have open copies (Hagolle 2008 on HAL; Zeng 2013 on the authors' lab site); same for Hagolle 2010 (HAL) and Makarau 2014 (DLR elib) | — |
| 3 | 05 | "a between-date regression fitted on valid pixels, the gap-filling cousin of our gain/offset fit" | partly corrected: the regression is **local and per target pixel**, fitted only on **spectrally similar** valid pixels (adaptive threshold from 5 × 5 local variation, N_R = 30 similar pixels, window 7 → 99 px, inverse spectral-difference × squared-distance weights). It is not one global gain/offset; its benefit over global/histogram methods comes from that locality | p. 184–185 |
| 4 | 05 | Listed under "thin-cloud correction against a clear reference date" | corrected in scope: the paper fills **missing** pixels (SLC-off stripes); it does no cloud or haze correction, and it explicitly does not handle abrupt change ("we do not discuss this issue"). Relevant to us only as a between-date tone-mapping method | p. 183, 192 |
| 5 | — | — | addition: WLR beats USGS local linear histogram matching in every band (r 0.898–0.921 vs 0.833–0.861; spectral angle 2.86 vs 4.46) on a seasonal (Dec→Mar) pair | p. 187, Table 1 |

## Skakun et al. 2022, CMIX (RSE) — `skakun2022_cloud_mask_intercomparison_cmix_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | "Ten operational algorithms agreed on thick, opaque cloud, 'in contrast to thin/semi-transparent clouds detection'" | verified (quote exact). Minor correction: not all ten are operational (CD-FCNN is a research U-Net; InterSSIM and s2cloudless are company tools) | p. 1, 5–10 |
| 2 | 10 | "CEOS team with CNES, ESA, DLR, NASA, USGS and companies" | verified (USGS EROS via KBR; companies Brockmann Consult, Sinergise, Telespazio, Thales) | p. 1 |
| 3 | 04 | "the reference data changed the ranking, so name the truth" | verified: S2 average BOA 80.0% (PixBox) to 89.4% (Hollstein); L8 79.8% to 97.6%; authors attribute it to how references were made | p. 16–20 |
| 4 | 10 | "the fringe is where every mask is least sure" (our reading) | supported: thin/semi-transparent cloud PA averaged 40.6 ± 27.4% vs 95.9 ± 3.6% opaque (PixBox L8); GSFC excluded cloud boundaries as too uncertain to label; CMIX recommends agreeing a dilation | p. 4, 15, 19 |
| 5 | 10 | CMIX PDF blocked (roderic 403); NTRS 20220006382 suggested | resolved: NTRS copy is the full publisher PDF (CC BY) | — |
| 6 | 04, 10 | Read status "Abstract" | now full text | — |
| 7 | — | — | addition: MAJA's described tests = blue surface-reflectance sharp increase, correlation veto ("If the correlation is high, it is not a cloud"), cirrus > 0.007 + 0.007·h², 240 m dilation for parallax, adjacency and fuzzy borders; run at 240 m in CMIX | p. 10, 18 (Table 15) |
| 8 | — | — | addition: buffers in use 0–300 m (FORCE 300 m, MAJA 240 m, LaSRC 5 px, ATCOR 100 m, Fmask 60–90 m); urban bright targets cause false clouds for all algorithms | p. 7–10, 14 |

<!-- group g3 -->
# Claim checks, group g3 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Ebel et al. 2021 (SEN12MS-CR) and Xu et al. 2024 (M3R-CR) were skipped: already in ledger_B.csv with handoffs.

## Shen, Li, Cheng et al. 2015 (GRSM) — `shen2015_missing_information_reconstruction_review_GRSM`
Page numbers are the author manuscript's 1–22 (journal 61–85).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Sorts algorithms into four main categories, compared experimentally and theoretically; "category names were not verified" | verified; names now confirmed: spatial-based, spectral-based, temporal-based, hybrid (by source of complementary information) | p. 1, p. 3 |
| 2 | 05 | Read status "abstract; needs GMU; author PDF … not opened" | corrected (status only): the author manuscript is open on SENDIMAGE and is now read in full; evidence 10 already used it | p. 1–19 |
| 3 | 10 | Missing data is information "completely obscured or not observed"; thin cloud and haze are a different, "partially missing" kind (cited as §VIII-A and §VIII-E) | verified; both quotes are in §VIII-E (not §VIII-A). The review explicitly does not treat thin cloud/haze ("it is not discussed in this paper") | p. 18 |
| 4 | 10 | Temporal methods "are sensitive to land-cover changes, especially abrupt changes" | verified (§VIII-A) | p. 17 |
| 5 | 10 | USGS EROS filled SLC-off gaps with "a simple histogram matching method", then local linear histogram matching (LLHM) in a moving window; it "can perform well in most regions if the input scenes are of high quality" but "has difficulty with heterogeneous landscapes" (§V-A) | verified; the full sentence adds "where the features are smaller than the local moving window size" and that it is "more sensitive with regard to data selection". Fig. 15(e) shows LLHM artifacts at a river edge: "a simple linear algorithm using all the common pixels is unsatisfactory" | p. 10 |
| 6 | 10 | Temporal replacement "may result in an aliasing phenomenon" from registration errors and abrupt land-cover change | verified | p. 10 |
| 7 | 05 (summary point 2, cites Shen 2019 not 2015) | Temporal methods do poorly under large land-cover change | consistent; the 2015 review states the same as a taxonomy: temporal methods suit observation-condition and phenological differences, not abrupt change (new buildings) | p. 9 |
| 8 | — | (not in our notes) mask rule | addition: missing a cloud pixel is "a fatal failure", false alarms are tolerable, masks are "appropriately" dilated; task-oriented evaluation and an "error map to convey the reconstruction reliability" ([43] Benabdelkader & Melgani) | p. 17 |
| 9 | — | (not in our notes) numbers | addition: dead-line test TV 41.96 dB/SSIM 0.983 best (Table I); simulated cloud CC 0.703 spatial / 0.838 temporal / 0.865 hybrid with a different-season reference (Fig. 23) | p. 6, p. 15 |

## Shen, Wu, Cheng, Aihemaiti, Zhang & Li 2019 (JSTARS) — `shen2019_spatiotemporal_fusion_cloud_removal_land_cover_change_JSTARS`
Page numbers are the journal's 862–874. Evidence 02 and 10 do not mention this paper (their "Shen" entries are Shen et al. 2015 GRSM/ICCV and Zhu, Li & Shen 2024).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 (§3 Q2) | Temporal methods "suit only phenological change and do poorly with significant land-cover change" | verified | abstract p. 862 ("only suitable for scenes with phenological changes, while they perform poorly in cases with significant land cover changes"); p. 863 adds "(especially those with unfixed object boundaries)"; p. 871 same |
| 2 | 05 (§3 Q2) | "Two auxiliary near-date images capture the change" | verified, with a precision our note lacks: the two auxiliaries are **coarse images from another sensor** (MODIS 500 m, upsampled), one on/near the target date and one on/near the reference date, plus the clear fine reference; they supply the change through a scale-invariant linear model. They are not two extra fine images | pp. 862, 864 |
| 3 | 05 (§1 item 2) | "Temporal methods do poorly under large land-cover change (Shen et al. 2019)" | verified. Numbers: site 2 (most change) mean RMSE LLHM 0.073, WLR 0.045, MNSPI 0.035, PM-MTGSR 0.028 vs proposed 0.026; mean CC 0.323–0.747 vs 0.808. Note the gap to the best temporal method (PM-MTGSR) is small on the means, and PM-MTGSR wins NIR on both sites; the clearer evidence is visual (temporal methods "fail to reconstruct the changed land cover", p. 868) and the time series (Fig. 6) | Tables I–II p. 869; pp. 867–871 |
| 4 | 05 (§1 item 2) | Methods that cope add a near-date source to carry the change: auxiliary images (Shen 2019) | verified | pp. 863–864 |
| 5 | 05 (§3 "where it hides") | Filling opaque cloud from the before date paints the dry road back; this "follows from the no-change assumption (Lin 2013; Shen 2019)" | verified as reasoning, not as a tested result: the paper states the fixed-coverage assumption (p. 863) and shows temporal fillers copy "incorrect temporal information" from changed areas (p. 867) and miss a changed white patch on real cloud (p. 871). Flood/road behaviour is our inference; the paper tests farmland change in Landsat | pp. 863, 867, 871 |
| 6 | 05 (references) | "Read: abstract; needs GMU" | corrected: an author-hosted full copy exists (WHU SENDIMAGE); now read in full | — |
| 7 | 05 (§3 Q2, implied) | — | addition: under phenological change the temporal method PM-MTGSR beat both fusion methods in the 13-date series; the authors recommend temporal methods for "phonological changes with fixed spatial tendency" and theirs only for change with "unfixed spatial tendency". Our notes cite only the negative half | Fig. 6 p. 870; p. 871 |
| 8 | 05 (implied, Q2) | — | addition: the paper says changed scenes under real cloud are "often unverifiable" even with multitemporal references (p. 870), so its real-cloud result is visual only; its quantitative evidence is all simulated (one manual mask, ≈35%, pasted on clear images) | pp. 866–870 |

## Meraner, Ebel, Zhu & Schmitt 2020 (ISPRS JPRS) — `meraner2020_dsen2_cr_sar_optical_cloud_removal_ISPRS`
Evidence 02 and 10 do not mention this paper; only evidence 05 does (§SAR fusion, line 62; "open, not yet read in full", line 230; summary item 1).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "a residual network fuses Sentinel-1 with Sentinel-2" | verified (SAR VV/VH concatenated with the 13 optical bands; long skip adds the cloudy input, so the network predicts a correction) | pp. 335–337, Fig. 3 |
| 2 | 05 | "with a cloud-adaptive loss that keeps the clear information" | verified, with a qualification: CARL is a training loss that pulls clear pixels toward the input (and still includes λ = 1 × L1 to the other-date target); it does not leave them unchanged. Reproduction MAE drops 49% (0.0398 → 0.0204), not to zero | eq. 3 p. 339; λ p. 340; Table 1 p. 339; pp. 342–343 |
| 3 | 05 | "removes even thick cloud" | corrected (overstated): that is the abstract's wording, but the Discussion says that where "the cloud cover is optically very thick" over complex scenes "the network fails to provide a detailed and fully accurate reconstruction"; urban scenes only "on a coarse scale". The thick-cloud gain comes from SAR (Fig. 6). No result is split by cloud thickness | abstract p. 333; p. 341; p. 345 |
| 4 | 05 | "on real global pairs" | verified (SEN12MS-CR: 169 ROIs worldwide, all seasons, real cloudy + clear pairs in the same season; test = 10 held-out ROIs; no simulated clouds). Note: the "pairs" are different dates, so the target contains real surface change | pp. 334–335 |
| 5 | 05 | "(12.9, core; open)" | verified for open (CC BY, p. 333) and core venue; JIF 12.9 not checkable from the paper (consistent with the other ISPRS JPRS entries) | p. 333 |
| 6 | 05 | "Open, not yet read in full: … DSen2-CR … (ScienceDirect)" | now read in full (published version from Helmholtz PuSH repository) | — |
| 7 | 05 (summary 1) | SAR fusion is unavailable to us because it needs radar | verified: the gain under thick cloud is from the SAR input; without SAR, reconstruction MAE 0.0282 vs 0.0266 and urban scenes are "not reconstructed at all" | Table 1 p. 339; p. 341 |
| 8 | — | — | addition | Training on plain L1 to the other-date target makes the network "predict and apply unwanted surface changes" (p. 339; Fig. 7 rapeseed yellow → green, p. 340): direct evidence for our rule not to copy the before date into the gate |
| 9 | — | — | addition | Cloud/shadow mask thresholds were set "in a conservative manner to reduce false negative detections" (p. 340): support for a dilated gate |


## Ebel, Xu, Schmitt & Zhu 2022 (TGRS 60), SEN12MS-CR-TS — `ebel2022_sen12ms_cr_ts`
Full text pp. 1–15 (arXiv v1 preprint; journal pp. 1–14). Evidence 02 and 10 do not mention this paper (grep for
Ebel / SEN12MS / CR-TS / "real cloud": no hits; evidence 02's CloudSEN12 rows are a different data set). Only
evidence 05 (line 63–65) cites it, jointly with SEN12MS-CR.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "Ebel et al. (2020; 2022) … *IEEE TGRS* … https://doi.org/10.1109/TGRS.2022.3146246" | verified (DOI, TGRS 60, pp. 1–14 per Crossref) | p. 1 |
| 2 | 05 | "Venue: core; open" | verified (TGRS; open via arXiv 2201.09613) | p. 1 |
| 3 | 05 | "global SAR plus cloudy and clear optical datasets (single date, then time series)" | verified, with a nuance: CR-TS is the time-series extension (53 global ROI, 30 paired S1/S2 dates through 2018, 0–100% cloud). It does not hold separate "cloudy" and "clear" images; the clear target is whichever date is least cloudy | pp. 2, 8 |
| 4 | 05 | "Training on real clouds beat training on synthetic ones" | **corrected (misattributed)**: this result is from SEN12MS-CR (Ebel, Meraner, Schmitt & Zhu 2021, TGRS 59, Table IV and Conclusion p. 10; verified in claim_checks_B). CR-TS runs no real-vs-synthetic training experiment. It only states, in related work, that copy-paste clouds capture spectral properties better than Perlin noise "but neither precisely reproduce the statistics of satellite images containing natural cloud occurrences", and its own sequence-to-sequence test is itself simulated (cloudy pixels alpha-blended onto the least-cloudy date) | p. 2; p. 10 |
| 5 | 05 | "Read: abstracts" | superseded: now read in full | pp. 1–15 |
| 6 | — | — | addition | Cloud masks: binary s2cloudless, no threshold stated (the 0.5 threshold + Gaussian σ = 2 is from the 2021 paper). Evaluation splits NRMSE into all / cloudy-in-every-input / clear-in-at-least-one ("preservation"); trivial baselines win PSNR (mosaicing 31.68 vs 26.68) and clear-pixel preservation (least cloudy 0.031 vs 0.040); no significance tests (pp. 4, 7, 9) |

## Ebel, Sainte Fare Garnot, Schmitt, Wegner & Zhu 2023 (CVPRW) — `ebel2023_uncrtaints_uncertainty_cloud_removal_CVPRW`
Page numbers are the proceedings' (2086–2096). Only evidence 05 mentions this paper (lines 24, 123–127, 136, 209); evidence 02 and 10 do not.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Aleatoric variance per pixel and per band (13 bands) | verified. Diagonal Gaussian covariance, `u_j = [σ²_1 … σ²_K]`, K = 13, C_out = 26, softplus on the variance channels; loss `Σ log|Σ_j| + Mahalanobis` (eq. 4) | p. 2088–2089 (eqs. 2–5) |
| 2 | 05 | Sentinel-1 as input and 3 dates | verified (T = 3, C_in = 15 = 13 S2 + 2 S1). Note: T = 1 (SEN12MS-CR) and T = 2/4 (ensemble, Tab. 6) are also run, and a no-SAR ensemble exists (Tab. 5) | p. 2088, 2089, 2092 |
| 3 | 05 | Calibration is measured by UCE | verified, with detail our notes lack: UCE = Σ_p (N_p/N)·|RMSE(B_p) − RMV(B_p)|, P = 20 bins (eqs. 6–7, after Guo et al. 2017); also an image-level UCE_im. Values: UCE 0.007, UCE_im 0.010 | p. 2090, Tab. 1 |
| 4 | 05 | Ensembles add epistemic uncertainty | verified: deep ensemble M = 5, total variance = mean member variance + spread of member means (eqs. 8–9); best UCE 0.002 | p. 2092, Tab. 5 |
| 5 | 05 (lines 24, 126) | Discarding the most uncertain 50% of reconstructions almost halves error (Fig. 3) | verified, but **corrected in scope**: the ranking is of whole test **images** (text: "sorted by increasing UCE_im"; axis: "sorted ascendingly by variance"), not pixels, and error is squared error (fit 0.001 + 0.003x, ≈0.0036 at 100% vs ≈0.002 at 50% read off the plot). Line 24's "variance per pixel … discarding the most uncertain half" reads as pixel-level discarding; it was image-level | p. 2090–2091, Fig. 3 (p. 2091) |
| 6 | 05 | Not done: no downstream task | verified (only RMSE/PSNR/SSIM/SAM/UCE; downstream use is argued, not tested) | whole paper; p. 2092–2093 |
| 7 | 05 | Not done: no split by cloud thickness | verified for quantitative results; Fig. 4 shows four cover levels (mild distortion, semi-transparent haze, partly dense, no visibility) qualitatively only | p. 2093, Fig. 4 |
| 8 | 05 | Higher uncertainty linked to persistent occlusion, shadow and changing crops | verified: Fig. 1 caption ("persistent occlusion, cloud shadow, or with specific land cover types", p. 2086); p. 2092 ("waves breaking on a shore or the coloring of maturing crops"); Fig. 4 caption ("ocean's white wash, changing crops as well as clouds and cloud shadow", p. 2093). Our notes omit waves/white wash and that the model flags any transient across inputs, i.e. real change too | p. 2086, 2092, 2093 |
| 9 | 05 | Venue: workshop, method attribution; read full text (ar5iv) | verified (CVPR Workshops, EarthVision). This check used the CVF open-access PDF | p. 2086 |
| 10 | — | — | addition | Our notes omit: without SAR, ensemble UCE rises 0.002 → 0.014 (Tab. 5, p. 2092); T = 2 gives UCE 0.004 (Tab. 6); diagonal vs isotropic variance cuts UCE 0.023 → 0.007 ("three-fold", p. 2092); the NLL loss costs 0.002 RMSE vs L2 (0.051 vs 0.049, p. 2090). All argue our two-date, no-SAR setting will be worse calibrated |


## Zhang, Yuan, Zeng, Li & Wei 2018 (TGRS) — `zhang2018_sts_cnn_missing_data_reconstruction_TGRS`
Page numbers are the arXiv preprint's 1–14 (journal 4274–4288). Evidence 02 and 10 do not mention this paper; all claims are from 05 (lines 51–54, 230).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "one CNN takes spatial, spectral or temporal supplementary data" | corrected | One architecture, but a **separate model is trained per task** ("the corresponding training data are employed independently to train the specific models", p. 6). The damaged image is the "spatial" input y1; the supplementary input y2 is spectral (MODIS) or temporal (SLC-off, cloud), not spatial (p. 5) |
| 2 | 05 | Handles MODIS band-6 dead lines, Landsat SLC-off stripes and thick cloud | verified | abstract p. 1; §IV pp. 7–11. Also a combined SLC-off + cloud case (Table IV, p. 9) |
| 3 | 05 | Tested on simulated and real data | verified, with a caveat | p. 7–11. Real-data tests are visual only (Figs. 14–16); every number is from simulated masks on clear images |
| 4 | 05 | "Fit: for cloud it needs another date" | verified | "input y2 is another temporal image without cloud" (p. 5). Spectral mode cannot do thick cloud: it "leads to the absence of all the spectral bands" (p. 2) |
| 5 | 05 (table, Temporal row) | Evaluation = masks on a clear target; PSNR, SSIM, CC | verified | p. 7: mPSNR, mSSIM, CC and SAM; masks pasted on a clear 400 × 400 × 6 TM crop, 10 repeats |
| 6 | 05 (Venue) | TGRS, core | verified (Crossref); impact factor 9.4 not checkable from the paper | — |
| 7 | — | (abstract-level impression that STS-CNN beats all baselines) | addition / correction | On simulated **cloud** STWR has the higher mPSNR (27.014 vs 26.805 dB, Table III, p. 9); STS-CNN wins only mSSIM, CC, SAM, by ≤0.002 / 0.002 / 0.009, with no significance test |
| 8 | — | Land-cover change between dates | addition | Never tested. The only statements: temporal differences "are major obstacles" (p. 3) and cloud removal with temporal data "results in some spectral distortion and blurring" (p. 13). No flag on filled pixels |
| 9 | — | Figure errors | addition | Fig. 12 caption labels are copied from Fig. 11 ("Simulated SLC-off", 2001.10.23/2001.11.8) though it shows cloud blobs on another scene (p. 9); text says both real cloud images "contained thick cloud" while Fig. 16b is labelled "without clouds" (p. 11) |

## Zhao, Olsen & Chandra 2023 (IEEE TGRS) — `zhao2023_seeing_through_clouds_spaceeye_TGRS`
Checked against the arXiv preprint 2106.08408v1 (June 2021, 28 pp. with supplement); page numbers are the preprint's. The TGRS text may differ.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Sentinel-1 plus 48-day Sentinel-2 sequences at 10 m | verified (T = 48 daily steps; S2 L1C TOA, 10 bands, all resampled to 10 m; S1 VV/VH). Note: for regions with no clear pixel in 48 days the processing used a 2-day step over 96 days, but the reported test set used 1-day steps | p. 6 §4.4, §5; supp. p. 22 and fn. 2 |
| 2 | 05 | Scored only on held-out synthetic gaps | verified, with nuance: Table 1 reports "syn" (held-out gaps) and "all" (gaps plus the clear input pixels). Quoting 34.84 dB would be the inflated "all" figure; the gap-only PSNR is 29.92. No score on real cloud | p. 8 Table 1 |
| 3 | 05 | "the authors say real ground truth does not exist" | verified, narrower wording: "there are no ground truth cloud-free images that can be used during training" | p. 2 |
| 4 | 05 | Limits: very cloudy scenes, cloud-detector errors that spread | verified, plus a detail our notes miss: the spreading "is an effect we have observed for large water bodies where the cloud-detector is less accurate" (directly relevant to floods). Qualitative statement, no number | p. 9 §6.4 |
| 5 | 05 | Standing water captured on a cloudy day, Carnation, WA, 2020; visual only, SAR in the input | verified (Fig. 1: dates 02/07–02/17/2020, standing water on 7 Feb, drained after mid-February; SAR sequence is an input; no metric or reference water map) | p. 2 Fig. 1 |
| 6 | 05 §1 item 4 | "SpaceEye's flood example is qualitative only" | verified | p. 2 |
| 7 | 05 §1 item 4 | "No paper found tests change, damage or flood mapping through reconstructed pixels" | corrected (partly): SpaceEye *demonstrates* change detection on reconstructed images — derecho damage, Luther, Iowa, 8/9/2020 (Fig. 9) and wildfire NBR change, Bridgeport, WA (Fig. 10) — but only as pictures, with no truth or score. "No paper *tests* (quantitatively)" stays true for this paper | p. 9 Figs. 9–10 |
| 8 | 05 | "My read: the change came from radar, not from the fill" | consistent with the paper (keys/queries from SAR only, eqs. 1–2; supp.: C-band "is reflected off of standing water ... ideally suited to detect flooding"); still an inference, the paper runs no SAR-off ablation | p. 4–5; supp. p. 24 |
| 9 | 05 | Venue core; read full text (ar5iv) | verified that the full text is the arXiv v1 preprint (NeurIPS-format, "Under review"), not the 16-page TGRS version; numbers should be cited as preprint numbers. Preprint is internally inconsistent: Introduction says PSNR 28.9, Table 1 says 29.92 (syn) / 34.84 (all) | p. 2; p. 8 |
| 10 | — | (not in notes) | addition: no per-pixel uncertainty or "filled" flag is produced. Cloud mask = S2Cloudless with blobs < 400 px (10 m) removed and pixels flagged far more often than the native mask dropped, because persistently white buildings were masked on every date | supp. p. 23 |
| 11 | — | (not in notes) | addition: synthetic gaps are real cloud masks sampled from another training scene and unioned with the scene's own mask; the gap pixels are zeroed, no cloud is rendered | p. 5–6 §4.4 |

## Fuentes Reyes, Auer, Merkle, Henry & Schmitt 2019 (Remote Sensing) — `fuentesreyes2019_sar_to_optical_cgan`
Page numbers are the article's "n of 19". Only evidence 05 mentions this paper (line 72); evidence 02 and 10 do not.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | cGAN SAR-to-optical translation | verified (an adapted CycleGAN, trained unpaired; 12 residual blocks, 1-channel in/out) | pp. 4–7 |
| 2 | 05 | "at high resolution (TerraSAR-X with ALOS PRISM)" | verified with detail: TerraSAR-X stripmap 1.25 m resampled to the 2.5 m ALOS PRISM panchromatic grid; a low-resolution Sentinel-1/2 (SEN1-2) test is also included. "High resolution" here means 2.5 m, five times coarser than our 0.5 m | pp. 8–9, Table 1 |
| 3 | 05 | "judged by SAR experts" | corrected: a preference poll of SAR experts, optical experts, mixed and "people outside the field of study"; text says "12 experts" but reports 320 votes on 20 samples (implies 16 respondents; counts sum to 319). CycleGAN preferred 177, DRIT 86, NL-SAR 54; NL-SAR preferred in urban scenes. No significance test | p. 13 |
| 4 | 05 | "and by road extraction" | verified, with the result our note omits: DeepLabv3+ trained separately per image type on a different TerraSAR-X set (Lincoln, 1 m) scored IoU 35.63% on CycleGAN images vs 38.58% NL-SAR vs 40.45% original SAR; generation hurt extraction (faint edges erased, junction breaks) | pp. 13–14, Table 3 |
| 5 | 05 | "with fundamental limits reported" | verified: ill-posed 1-channel translation, different physics, SAR range-dependent geometry needing a DSM, "fiction" (invented/merged/erased buildings), patch-border radiometric jumps, wrong large-area grey levels. Mostly argued and shown qualitatively, not measured | pp. 2, 4, 9–12, 15–16 |
| 6 | 05 | Placed under "SAR-to-optical and SAR fusion" in the reconstruction (cloud-filling) families; family row says needs "mostly Sentinel-1, 10 m", evaluated on "real cloudy/clear pairs" | corrected (scope): the paper is not about cloud removal or gap filling at all; it translates whole SAR scenes for human interpretation, uses TerraSAR-X, and has no cloudy/clear pairs. It belongs in our notes as evidence about trusting generated pixels, not as a reconstruction method | pp. 1–3, 8 |
| 7 | 05 | Venue JIF 4.3 "confirm in JCR" | not checked (no JCR access in this run); journal confirmed as *Remote Sensing* 11(17):2067 via Crossref | — |
| 8 | 05 (read level) | "abstract" | upgraded: full text now read, pp. 1–19 | — |


<!-- group g4 -->
# Claim checks, group g4 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected**, **not found**, **addition**. The evidence
files were not edited.

## Li, Shen, Cheng, Liu, You & He 2019 (ISPRS JPRS) — `li2019_mscff_cloud_detection_hrc_whu_ISPRS`
Page numbers are the arXiv manuscript's 1–37.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 | 150 Google Earth RGB images at 0.5–15 m, cloud outlined by experts | verified (1280 × 720 × 3; experts in RS interpretation, Wuhan University) | p. 15 Table 2; p. 16 |
| 2 | 02 | "Thin cloud counts as cloud only where the ground cannot be seen clearly" | verified, with the second condition: thin cloud labelled cloud "if they were visually identifiable and the underlying surface could not be seen clearly". Consequence our notes do not state: see-through haze is labelled clear (0) | p. 17 |
| 3 | 02 | No shadows labelled, "because shadows were rare and hard to outline in high-resolution images" | verified ("rare and hard to accurately select") | p. 17; p. 24 |
| 4 | 02 | Photoshop lasso + magic wand | verified; add: contrast stretched first, magic-wand tolerance 5–30 | pp. 16–17 |
| 5 | 02 | 5 land-cover types; 120 train / 30 test (attributed to the mirror) | verified from the paper itself: 120 of 150 scenes trained (6,000 overlapping 256 px patches), 30 test balanced across land-cover types; Fig. 8 shows 5 HR types. The split is the authors', not only the mirror's | pp. 17–18, 25 |
| 6 | 02 | Official licence "academic purposes only" | not found in the paper (it only says the data are "available online"); licence comes from the repository, not checked here | p. 16 |
| 7 | — | — | addition: MSCFF on the 30 HR test scenes: OA 95.99%, cloud IoU 0.903, F 0.949; PRS (rule-based) 0.696 and "only detects the thick clouds" | p. 20, p. 24 |
| 8 | — | — | addition: HR imagery mixes satellite and aerial photography with no accurate geolocation; resolution per image not given | p. 16 |

## Sui, Ma, Yang, Zhang, Pun & Liu 2024 (TGRS) — `sui2024_diffusion_enhancement_cloud_removal_cuhk_cr_TGRS`
Page numbers are the arXiv v1's 1–13.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | CUHK-CR is Jilin-1KF01B, pan-sharpened to 0.5 m, blue, green, red and NIR | verified | p. 3–4, Table II |
| 2 | 05 | 668 thin-cloud and 559 thick-cloud images | verified (512 × 512; split 534/134 and 448/111) | p. 2, p. 3 |
| 3 | 05 | Cloudy and clear pairs 10–17 days apart | verified (Table III: 10, 17 and 10 days; clear image after the cloudy one at two sites, before it at Hangzhou) | p. 4 |
| 4 | 05 | The "reference prior" is the output of a pretrained cloud-removal network; inference takes the single cloudy image | verified (x0,E = E(y), MemoryNet or MSDA-CR) | p. 5–6, eq. 11 |
| 5 | 05 | Best PSNR 26.18 (thin) and 24.35 (thick) | verified (DE-MemoryNet 26.183 / 24.348). Add: only ~0.1 dB above MemoryNet alone | p. 7 Table V |
| 6 | 05 | "DE's authors note that diffusion textures often fail to match the real scene" / "may not align with the actual scene" | corrected: the authors say this of **pure** diffusion ("textures generated only by the diffusion model"), as the motivation for anchoring DE to a reference network; they do not concede it of DE. That DE still invents under opaque cloud is our read | p. 2, p. 5 |
| 7 | 05 | No cross-sensor test | verified; they do test cross-resolution (train 1–2 m, test 0.5 m, Table VII) | p. 11 |
| 8 | — | — | addition: thin/thick split criterion not stated; the Cloud-Net detector "fails to differentiate between thin and thick cloud layers"; fully obscured images removed by eye | p. 4 |

## Zou, Zhang, Li, Wang, Xing, Jin, Lang & Tao 2025 (TGRS) — `zou2025_cloud_adapter_frozen_dinov2_cloud_segmentation_TGRS`
arXiv 2411.13127v2; page numbers are the preprint's 1–13.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 | Adapts a frozen DINOv2-L | verified, with a qualification: backbone weights are frozen, but trained cross-attention adapters modulate the output of all 24 layers, so the features used are not the frozen features | pp. 3–4, Table V |
| 2 | 02 | "about 0.6% extra parameters" | verified (1.82 M, 0.6% of the backbone; the Mask2Former head is not counted) | Table II, Table VI |
| 3 | 02 | 89.05 mIoU on HRC_WHU against 83.44 for the best baseline | verified (HRCloudNet 83.44). Add: this mIoU is the mean of clear and cloud IoU, not comparable to Li 2019's cloud-only 0.903; MSCFF is not among the baselines | p. 7–8 Table VII; eq. 7, p. 5 |
| 4 | 02 | It did not test across datasets | verified (one model per dataset) | pp. 4–9 |
| 5 | — | — | addition: frozen DINOv2-L with head only = 73.10 mIoU vs 74.18 full (CloudSEN12 L1C): the adapter adds ~1.1 points | p. 7 Table VI |
| 6 | — | — | addition: HRC_WHU has no validation split in their setup (120 / – / 30) while training validates every 4,000 steps; checkpoint selection set not stated | p. 5 Table I |
| 7 | — | — | addition: thin cloud IoU only 56.15 (L1C) / 54.97 (L2A) / 44.41 (L8 Biome) | Tables X–XII |

## Arp, Hoos, van Bodegom, Francis, Wheeler, van Laar & Baratchi 2024 (ISPRS JPRS) — `arp2024_vpint2_training_free_cloud_removal_ISPRS`
Page numbers are the journal's 168–184.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Training-free interpolation | verified | p. 168 abstract, p. 170 |
| 2 | 05 | An older clear image gives the spatial structure; current values spread in from clear pixels | verified (γ = f_ij / f_i'j' from the reference; eqs. 2–3) | pp. 171–172 |
| 3 | 05 | Accuracy falls only slightly as the reference ages | verified (1 week to 6 months; "only decreases marginally") | p. 168, p. 180, Fig. 7a |
| 4 | 05 | The authors back evaluating by transferring cloud masks onto clear images | verified; add their reason: near-date "truth" error (MAE 141 for 1-week replacement) is comparable to method errors (196–292) | p. 168, pp. 180–181 |
| 5 | 05 | Listed under "Spatial and generative" | corrected (classification): the authors call it "a multi-temporal (single reference image) interpolation method"; it is temporal + spatial, not single-image | p. 170 |
| 6 | — | — | addition: masks should favour recall and be buffered; significance by one-sided Wilcoxon signed-rank, α = 0.05; not significant vs MNSPI on cropland and forest | p. 175, p. 178 Table 1, p. 179 |

## Wang, Wang, He, Ma, Wang, Zhang, Cheng & Pun 2026 (ECCV, arXiv 2607.02471) — `wang2026_gacr_observation_anchored_cloud_removal_ECCV`
Page numbers are the preprint's (main pp. 1–15; appendices labelled App.).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | ECCV 2026 (accepted per arXiv) | verified (arXiv comment "accepted by ECCV 2026") | arXiv abs page |
| 2 | 05 | Data: CUHK-CR-EXT (0.5 m, real cloud) plus synthetic clouds on ISPRS Potsdam and Vaihingen | verified; add: CUHKCR-EXT-GZ mostly thin, -CS more thick; synthetic via Czerkawski generator + thickness scalar; all resized to 256 px | p. 9; App. C |
| 3 | 05 | The model sees only the cloudy image | verified (Net_θ(x_t, t, x_c)) | p. 7 eq. 9 |
| 4 | 05 | Downstream scoring uses frozen DINOv3 encoders on 12 tasks (classification, buildings, segmentation, height); no change detection | verified; change detection is named as motivation in the abstract but not tested | p. 1, pp. 8–9, App. B |
| 5 | 05 | Earlier generative methods drift semantically under heavy occlusion | verified (authors' motivation) | p. 2 |
| 6 | 05 | "0.5 m cloud removal exists ... GACR" | corrected in part: only the CUHKCR-EXT half of GACR's evaluation is 0.5 m real cloud, and there its PSNR gain is 0.2–0.5 dB; the large gains (2–4 dB) are on synthetic clouds over 5–9 cm aerial images resized to 256 px | p. 10 Table 1; App. C |
| 7 | — | — | addition: decoders trained directly on cloudy images ("end-to-end") match or beat every cloud-removal pipeline on classification (CLS-2 0.876 vs GACR 0.781) and are close on buildings | p. 11 Table 2; App. E.2–E.3 |
| 8 | — | — | addition: only train/test splits listed, yet checkpoints chosen by "best validation performance"; single runs, no significance tests | App. D.1–D.2, Table 5 |

## Liu, Li, Guan, Zhou & Zhang 2025 (CVPR) — `liu2025_emrdm_mean_reverting_diffusion_cloud_removal_CVPR`
arXiv 2503.23717v1; main-paper pages 1–8.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "a mean-reverting diffusion from cloudy to clear" | verified (forward SDE with the cloudy image as mean; ODE backward) | pp. 3–4, eqs. 3–11 |
| 2 | 05 | "single- or multi-date" | verified with a correction of meaning: "multi-temporal" = L = 3 cloudy acquisitions (+ IR) fused, outputs averaged; no clear reference date in any setting, so it is not the two-date (clear before) case | p. 4, p. 6 Alg. 2, Table 4; supp. Table 5 |
| 3 | 05 | Listed only as "Other diffusion models (abstracts)" | addition: EMRDM is the strongest published result on CUHK-CR (thin 27.28, thick 24.59 dB), above DE (26.18 / 24.35) — evidence 05 quotes DE's numbers as "best PSNR" without it | p. 6 Table 1 |
| 4 | — | — | addition: thick-cloud gain at 0.5 m only ~0.25 dB; conditioning on the cloudy image is worth +5.5 dB over pure noise (ablation) | p. 6–7 Tables 1–2 |

## Zou, Li, Xing, Zhang, Wang, Jin & Tao 2024 (TGRS) — `zou2024_diffcr_fast_conditional_diffusion_cloud_removal_TGRS`
arXiv 2308.04417v1; page numbers 1–13.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "conditional diffusion" | verified (conditional DDPM, decoupled condition encoder, data prediction, 1-step sampling) | pp. 3–7 |
| 2 | 05 | Listed with single-image generators (implicitly single-date) | corrected: the main setting is **three cloudy Sentinel-2 dates** as input (multi-temporal); single-image (N = 1) appears only in an ablation, 4 dB worse | p. 3 §III-A; p. 8 Table II |
| 3 | 05 | "best on three benchmarks" | corrected for the version read: the arXiv v1 reports **two** benchmarks (Sen2_MTC_Old, Sen2_MTC_New). EMRDM (2025) cites DiffCR numbers on SEN12MS-CR, so the published TGRS version may add a third; not verified (paywalled version not read) | p. 7 §IV-A, p. 9 Table VI |
| 4 | — | — | addition: stated failure — dark lakes confused with cloud shadow and filled with cloud | p. 11 Fig. 7 |

## Czerkawski et al. 2022 (Remote Sensing 14:1342) — `czerkawski2022_deep_image_prior_cloud_inpainting_RemoteSens`
Page numbers are the article's 1–18.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Deep-image-prior inpainting with no training | verified (internal learning, 4,000 steps per image) | pp. 2, 4–6 |
| 2 | 05 | Tested on synthetic masks with exact truth and on real samples | verified, with detail: "synthetic" = 17 real S2 cloud masks pasted onto clear images (340 + 510 cases); "real samples" = 6 cloudy L1C images, qualitative only | pp. 3–4 Table 1; §3.3 pp. 12–13 |
| 3 | 05 | Listed under "Spatial and generative" (single-image) | corrected (scope): the best modes use a historical optical reference (mean of the previous year's clear images) and/or SAR; image-only mode is the weakest (inpainted SSIM 0.66 / 0.61 vs 0.76 / 0.69 with the reference) | p. 5 Fig. 2, p. 9 Table 2 |
| 4 | — | — | addition: depends on leak-free masks; results vary run to run; stable to ~16% cover | pp. 8, 12, 14 |

## Sarukkai, Jain, Uzkent & Ermon 2020 (WACV) — `sarukkai2020_stgan_spatiotemporal_cloud_removal_WACV`
CVF pages 1796–1805.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "a spatiotemporal GAN on 97,640 image pairs" | corrected: 97,640 pairs is the **single-image** set (used for Pix2Pix/MCGAN); STGAN was trained on the temporal set of **3,101** clear images each with 3 cloudy images (945 tiles) | p. 1799 §4.3 |
| 2 | 05 | "improved downstream land-cover classification" | verified (EuroSAT classifier: cloudy 72.48%, clear 98.66%, STGAN 93.96%); test-set size not given in the main paper | p. 1803 Table 3 |
| 3 | 05 | Listed under temporal / reference-date methods (implicitly) | addition: input is three **cloudy** dates, no clear reference; training assumes the ground "changes slowly over time" | p. 1797 §3 |
| 4 | — | — | addition: text and tables disagree on two PSNR values (21.130 vs 22.894; 26.373 vs 26.000) | pp. 1801–1803 |

## Lin, Xu, Wang, Wang, Sun & Fu 2019 (arXiv 1901.00600) — `lin2019_rice_cloud_removal_dataset_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "RICE (arXiv 1901.00600)" listed as a data attribution (abstract) | verified as to identity; addition: RICE-I clouds are the Google Earth cloud display layer toggled on/off (not real acquisitions); RICE-II is Landsat 8 bands 6-5-4 false colour with LandsatLook cloud/shadow/cirrus masks, clear image < 15 days apart | pp. 3–4 |
| 2 | (DE, used in our notes via evidence 05) | RICE2 has 736 images, 30 m, 3 bands (DE Table I) | corrected: the RICE paper says RICE2 has **450** sets; RICE-I resolution is not stated | p. 1 abstract, p. 3 |

## Zhang, Liang et al. 2025 (arXiv 2512.04461v2) — `zhang2025_units_unified_spatiotemporal_generative_model_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "UniTS (arXiv 2512.04461)" listed as a data/method attribution (abstract) | verified as to identity: unified flow-matching model for time-series reconstruction, cloud removal, semantic change detection and forecasting; Sentinel-1/2 time series at 10 m; no venue | pp. 1–3 |
| 2 | — | — | addition (bears on evidence 05's mask-transfer plan and VPint2's recommendation): the same model scores 30.15 dB with pasted binary masks but 20.29 dB on real clouds; the authors say simulated masks "oversimplify real-world conditions" | p. 2, p. 9 Tables IV, VI |
| 3 | — | — | addition: datasets built from AllClear ROIs; change detection only on Planet 3 m LULC/buildings, not floods | pp. 3, 10 |

<!-- group g5 -->
# Claim checks, group g5 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (the paper says something different), **not found**, **addition** (in the paper, missing from our notes).

## Li, Zheng, Zhu, Yao & Wu 2015 (TIP) — `li2015_weighted_guided_image_filtering_TIP`
Page numbers are the accepted manuscript's 1–10.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (5b; §3 "better-supported forms") | WGIF "can avoid halo artifacts" | verified (abstract wording). Note the body hedges to "halo artifacts can be reduced/avoided", and evidence is visual only (no halo metric) | p. 1, p. 7 |
| 2 | 10 (§6 plan item 6) | WGIF is an edge-aware alternative relevant to dehazing | verified: §IV-B applies it to dehazing, guide = luminance of the hazy image, λ = 1/1000, ζ1 = 60 | p. 6 |
| 3 | — | — | addition: their dehazing uses no max filter, a 31/32 factor, and t^(1+ς) sky compensation; ε in Γ is (0.001·L)², so the scale must match the data's range | pp. 3, 6 |
| 4 | — | — | addition: WGIF is defined with a scalar (grey) guide; works with our greyscale rule unchanged | p. 3 |

## Shen, Zhou, Xu & Jia 2015 (ICCV) — `shen2015_mutual_structure_joint_filtering_ICCV`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§3 "against this guide") | Joint/guided filters "directly transfer the structural information in the reference image to the target one … there may be completely different edges in the two images. Simply passing all patterns to the target could introduce significant errors" | verified (abstract, verbatim) | p. 3406 |
| 2 | 10 (§3 "better-supported forms") | Mutual structure "uses only the structure both images share" | verified (§3–4: mutual structure = edges common to both patches, magnitude and polarity free) | pp. 3407–3408 |
| 3 | — | — | addition: tested on RGB/depth, stereo, RGB/NIR, day/night; never on haze or remote sensing, so "better-supported" for our use is an analogy. Parameters λ, β 30–300, ε ≈ 1e-5; patch size unstated | pp. 3411–3413 |

## Ham, Cho & Ponce 2018 (TPAMI) — `ham2018_robust_guided_image_filtering_nonconvex_TPAMI`
Page numbers are the HAL manuscript's 1–15.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§3 "against this guide") | Classic joint filtering "does not consider structural differences between guidance and input images" | verified (abstract: "it does not consider structural differences between guidance and input images, and … it is not robust to outliers") | p. 1 |
| 2 | 10 (line 64) | Ham et al. "make the same point" as Shen 2015 | verified (§3.1, Fig. 2: static guidance transfers "all the structural information" of the colour image) | p. 3 |
| 3 | 10 (§9 sources) | Open copy is "arXiv" | corrected: no arXiv version found; the open copy is HAL hal-01279857v3 (author manuscript) | — |
| 4 | — | — | addition: never tested on dehazing/cloud; intensities in [0,1]; µ = 60, ν = 30 typical; global solver ~2.5 s per 0.15 Mpx | pp. 6–8 |

## Meng, Wang, Duan, Xiang & Pan 2013 (ICCV) — `meng2013_boundary_constraint_dehazing_ICCV`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§6 "against") | "a boundary constraint with weighted L1 regularisation" | verified | abstract p. 617; eq. 19 p. 620 |
| 2 | 10 (§6) | Top-venue edge-aware alternatives "avoid the patch altogether" | **corrected**: Meng still uses a patch. The data term t̂ is a morphological closing of the boundary map over a patch (7 × 7 in Fig. 5, 17 × 17 in Fig. 3); the L1 contextual term then refines it. It relaxes He's constant-t assumption, it does not drop the patch | p. 619 eq. 9; p. 621 Fig. 5 |
| 3 | — | — | addition: settings C0 = (20,20,20), C1 = (300,300,300) on the 0–255 scale, λ = 1, α = 0.5 (log-luminance weights, grey-native); no quantitative results, visual only | pp. 619–621 |

## Tarel & Hautière 2009 (ICCV) — `tarel2009_fast_visibility_restoration_ICCV`
Page numbers are the author copy's unnumbered 1–8.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (row "3, greyscale") | Handles "both color images or gray level images" | verified (abstract; W = I for grey, p. 2) | p. 1 |
| 2 | 10 | Steps: "atmospheric veil inference, restoration, smoothing, tone mapping" | verified (abstract; §2.2–2.6; white balance is a prerequisite step, §2.1) | pp. 1–4 |
| 3 | 10 | "Shows that grey-level dehazing is a recognised setting" | verified; the paper also tests on grey road images and a grey video (Fig. 4, p. 6) | pp. 4, 6 |
| 4 | — | — | addition (important for the ring): the authors tried an erosion-based veil and "found that it suffers of halo"; they use median filters instead. Our dark channel is erosion + box blur | p. 3 |
| 5 | — | — | addition: s_v is also the largest object assumed white by nature; at 0.5 m, bright roofs larger than the window would be read as haze in single-date use | p. 3 |

## Gibson, Vo & Nguyen 2012 (TIP) — not checked (paywalled)
No open copy found (OpenAlex: closed, no repository copy; one web search: IEEE Xplore only; a 2010 OCEANS conference precursor exists on Scribd, not used). Needs Justin's GMU login: https://doi.org/10.1109/TIP.2011.2166968 . Evidence 10's quote that the median operation "can avoid halo effects" (§6, abstract-level) stays unverified against the full text; the median-dark-channel parameters are unknown. Tarel & Hautière 2009 (full text, above) independently supports the median-instead-of-erosion idea ("we found that it suffers of halo", p. 3).

## Pérez, Gangnet & Blake 2003 (TOG) — `perez2003_poisson_image_editing_TOG`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (row "5, the seam") | Poisson editing gives "seamless editing of image regions" | verified (abstract: "a variety of novel tools are introduced for seamless editing of image regions") | p. 313 |
| 2 | 10 (row 5) | "The experts' seam fix is gradient-domain or global, not a linear ramp" | verified for this paper: it contrasts Poisson cloning with feathering ("visible seams, which can be only partly hidden … by feathering") and with multiresolution blending | pp. 313–314 |
| 3 | 10 (§5 "Fit") | The transferable part is making the correction field continuous at its border | consistent with the paper's own reading: the correction f̃ is the "membrane interpolant of the mismatch" along ∂Ω (eq. 5). Applying it to haze is our extension | p. 315 |
| 4 | — | — | addition: Microsoft Research UK authors (company); grey = one channel; visual results only | p. 313–314 |

## Berman, Treibitz & Avidan 2020 (TPAMI) — `berman2020_haze_lines_single_image_dehazing_TPAMI`
DOI from Crossref: 10.1109/TPAMI.2018.2882478 (42(3):720–734). Page numbers are the early-access copy's.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 (item 4) | Haze-lines "needs RGB colour clusters" | verified: the prior is "a few hundred distinct colors, which form tight clusters in RGB space"; in one grey band all pixels share one haze-line, so it cannot run on grey | abstract p. 1; §3.2 p. 3; §4.2 p. 5 |
| 2 | 02 (item 4) | Makarau 2014 is "a better fit than haze-lines" for us | consistent (our judgement; Berman is a single-date RGB photo method on linear radiance, tested on O-HAZE and natural photos) | p. 3, Table 1 p. 12 |
| 3 | — | — | addition: the constrained WLS (t ≥ t_LB) is the paper's own fix and gives the best SSIM on O-HAZE (0.781); errors ≈ 50% at t = 0.15 support our T_MIN = 0.2; A estimation works without visible sky ("aerial photos") | pp. 8, 12–13 |
| 4 | — | — | note: Berman attributes the median/ellipsoid idea to Gibson & Nguyen 2013 (EURASIP JIVP), not to Gibson, Vo & Nguyen 2012 (TIP), and says it "cannot reliably estimate the transmission of fine structures such as leaves" | p. 1 |

## Song, He, Qian & Du 2023 (TIP; arXiv v1) — `song2023_dehazeformer_vision_transformers_dehazing_TIP`
Published DOI 10.1109/TIP.2023.3256763, TIP 32:1927–1941 (title without the "DehazeFormer:" prefix). Checked against the arXiv v1 preprint.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 (item 4) | DehazeFormer is RGB | partly corrected: the default setting is 8-bit RGB, but the paper also trains/tests on 16-bit multispectral (Table V, much better: 49.95 vs 39.57 dB) | pp. 8–9 |
| 2 | 02 (item 4) | "its own README warns that models trained on synthetic haze may fail on real haze" | not found in the paper (README not read, per rules). The paper's closest statement is about its own first synthesis: worked on synthetic dense haze, "performs poorly on the dense haze region of the real image", fixed with ξ = 1.25; and the paper reports no real-haze evaluation at all | p. 7 |
| 3 | 02 (line 61) | RS-Haze gives "synthetic hazy/clear RGB pairs" | verified, with addition: 51,300/2,700 512² patches from Landsat-8 (30 m) with cirrus-band haze; RGB and MS versions | pp. 6–7 |

## Li, Shen, Cheng, Li & Zhang 2019 (Remote Sensing) — `li2019_thick_cloud_removal_stepwise_radiometric_RemoteSens`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (row "5, the seam") | Li refines the mask "to ensure that the labeled cloud boundaries go through homogeneous areas … to ensure a seamless reconstruction" | verified (abstract, verbatim; method §2.1: SLIC superpixels on the stacked two-date image, N = 50) | pp. 1, 3–5 |
| 2 | 10 (row 5) | then a "residual correction based on global optimization" | verified (abstract; §2.3: gradient + λ·intensity fidelity, Dirichlet boundary, solved as a boundary-value problem, 3 iterations; λ only "a small value") | pp. 1, 7–8, 15 |
| 3 | 10 (§5 "Fit") | These methods "replace thick cloud with another date's pixels, which our rule forbids" | verified: step 2 replaces cloud pixels with locally mean/std-matched auxiliary pixels (r = 80) | p. 6 |
| 4 | 05 (land-cover change) | Temporal fillers fail under large land-cover change | consistent; this paper states it directly: "cannot be accurately recovered under the condition that abrupt land-cover changes have occurred" | p. 16 |
| 5 | — | — | addition: the paper's "high resolution" is 4–10 m (Beijing-2, Gaofen-2, Sentinel-2), not sub-metre; Pérez-style cloning is extended with an intensity term because gradient-only cloning propagates boundary error to the centre | pp. 7, 10–13 |

## Canny 1986 (TPAMI) — `canny1986_computational_approach_edge_detection_TPAMI`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 (§2 arm a) | Hysteresis is Canny 1986 §VI: points above a high threshold are kept, "as is the entire connected segment … which lies above a low threshold" | verified (verbatim, §VI "Noise estimation and thresholding") | p. 690 |
| 2 | 10 (§2) | "This lowers both breaks and isolated false points" | verified: streaking "greatly reduced"; "probability of isolated false edge points is reduced" | p. 690 |
| 3 | 10 (§2 limits) | "No JIF > 4 paper applies hysteresis to cloud masks. The support is the principle (Canny)" | consistent: Canny applies it to edge contours on photographs; nothing about clouds or areas | pp. 689–690 |
| 4 | — | — | addition (actionable): Canny's high:low ratio is "two or three to one"; for our high = 71 that is low ≈ 24–36, so of HYSTERESIS_LOWS (50, 35, 20) only 35 is inside his range | p. 690 |
| 5 | — | — | addition: Canny's thresholds are noise-adaptive (global histogram of a Wiener-filtered response, low percentiles ≈ noise); ours are fixed Otsu cuts | pp. 689, 697 |


<!-- group g6 -->
# Claim checks, group g6 (dataset/benchmark papers; evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (correction given), **not found**, **addition**.
Evidence files were not edited.

## Portalés-Julià et al. 2023 (Sci. Rep.) — `portalesjulia2023_global_flood_extent_segmentation_SciRep`
Page numbers are the article's 1–14.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §1.1, 10 | v2 splits labels into two independent binary masks, clear/cloud and land/water, so water can be called under thin cloud | verified | p. 6 ("two independent binary reference masks"), p. 1 abstract |
| 2 | 02 §1.1, 10 row 6 | Scores leave out only invalid pixels and bright opaque cloud | verified; precise rule: pixels "labeled as clouds and have a brightness above 0.3" are masked, BR = sqrt(B2²+B3²+B4²) | p. 12 Methods; Fig. 5 p. 6 |
| 3 | 02 §1.1 | Scenes with much thin cloud go to human review | verified (worded as a recommendation: "shall be validated by human experts ... regardless of the selected method", not an implemented pipeline step) | p. 8 |
| 4 | 10 row 6 | Water is segmented "even in areas covered by semitransparent clouds" | verified | abstract p. 1 |
| 5 | 02 table | "manually labelled evaluation set of 11 events" | verified, with detail: 17 flood maps from 11 events | p. 7 |
| 6 | 02 table | "Sentinel-2 (+ Landsat), 509 image–mask pairs" | corrected: 509 is not in the paper. Paper: >180 events, ≈75,000 tiles of 256×256; training 475 maps from 119 events (≈65,000 patches). Training input is Sentinel-2 L1C only; the S2-to-L8 model can be *applied* to Landsat 8/9 | p. 6, p. 11 |
| 7 | 02 table | Licence CC-BY-NC-4.0 (dataset card) | not found in paper: the paper gives Zenodo record 8153514 and no data licence; the article is CC BY 4.0. Keep the card as the licence source | p. 12, p. 14 |
| 8 | 02 table | Flood maps from Copernicus EMS and others | verified (CEMS, UNOSAT, GloFIMR harmonised, inherited from v1) | p. 5 |
| 9 | 05 (provenance layer) | "WorldFloods v2's thin/bright split" | verified: the split is P(cloud) > 0.5 AND brightness > th_BR. Note the paper gives th_BR = 0.35 (p. 7) and recommends/uses 0.3 (pp. 7–8, 12); internal inconsistency | pp. 6–8 |
| 10 | — | — | addition: best-IoU water threshold is 0.7 not 0.5; RGBNIR model IoU 48.57 vs 57.89 with SWIR; thin cloud 4.54% of pixels; eq. 3 IoU has a typo (TN for FN) | pp. 7, 8, 12 |

## Mateo-Garcia et al. 2021 (Sci. Rep.) — `mateogarcia2021_worldfloods_onboard_flood_mapping_SciRep`
Page numbers are the article's 1–12.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §1.1, table | v1 adds cloud as a third output class (land, water, cloud) | verified (three exclusive classes, 2 bits/pixel) | p. 4 |
| 2 | 02 §1.1, table | Cloud labels made automatically with s2cloudless | verified | p. 4, Fig. 4 caption p. 5 |
| 3 | 02 table | "Land, water, cloud (+ invalid)" | verified as a Table 1 column; the paper never defines "invalid" beyond manual checks for "invalid intensities" | p. 4, p. 6 |
| 4 | 02 table | Sentinel-2, 13 bands, 10 m; 256 × 256 tiles | verified (bands >10 m resampled to 10 m by nearest neighbour) | pp. 4, 6 |
| 5 | 02 table | About 266 GB; https://tinyurl.com/worldfloods | verified | p. 4, p. 10 |
| 6 | 02 table | "v2 card says the WorldFloods database is CC-BY-NC" | not found in this paper: no data licence stated; captions call S2 and CEMS products "public domain"; article CC BY 4.0 | pp. 2, 5, 12 |
| 7 | — | — | addition: 422 maps / 119 events (2015–2019); most labels from radar maps with a time gap; NDWI baseline was given s2cloudless as "perfect cloud masking"; cloud shadows are the main false-water source | pp. 4–7 |

## Hänsch et al. 2022 (CVPRW) — `hansch2022_spacenet8_flooded_roads_buildings_CVPRW`
Page numbers are the CVF copy's printed 1472–1480 (IEEE: 1471–1479).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 §1.4, row 6 | Analysts "were instructed to only attribute what was visible" under cloud | verified (full sentence adds "and not make any assumptions where features could not be seen"; it applies to features obscured by cloud in the post-event image) | p. 1474 |
| 2 | 10 row 6 | "Supported: the labels themselves abstain" | **corrected**: the labels do not abstain. There is no cloud/unknown class; "the flood attribute is omitted", which in the 4-channel label scheme and in Fig. 5 means the feature is non-flooded. Scoring has no cloud mask. The rule creates missing positives (PU), it is not an abstention | pp. 1474, 1477, Fig. 5 p. 1478 |
| 3 | 10 ref 8 | CVPRW 2022, 1471–1479; Maxar co-authors; company co-led | verified (Maxar 5 authors, DLR, ORNL); CVF copy prints 1472–1480 | p. 1472 |
| 4 | 02 §1.2 | SN8's "yes or missing" flood labels are a positive-unlabelled problem under cloud | verified in substance: hidden features get no flood attribute and default to non-flooded | pp. 1474, 1477 |
| 5 | — | — | addition: road flooded = "visibly covered with water or rubble"; building flooded = water in immediate proximity; nothing on thin cloud/haze; imagery CC 4.0 Non-Commercial; pansharpened RGB 0.3–0.8 m; pre/post tiles differ in pixel size | pp. 1473–1475 |

## Pasquarella et al. 2023 (CVPRW) — `pasquarella2023_cloud_score_plus_quality_assessment_CVPRW`
Page numbers are 2125–2135.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 §2 (ring fixes) | Occlusion "is better treated as a regression problem rather than a discretized classification problem" | verified (verbatim, abstract) | p. 2125 |
| 2 | 10 §2 | "That supports a graded edge over a hard gate" (our inference) | verified as inference: the paper argues for continuous per-pixel QA and notes CMIX-I found "vague definitions of clouds (including semi-transparent clouds and cloud boundaries)" problematic for discrete classifiers. It says nothing about cloud edges or buffers specifically | pp. 2125–2126 |
| 3 | 10 ref 19 | CVPRW 2023, 2125–2135; Google-led | verified (all 4 authors Google LLC) | p. 2125 |
| 4 | 10 (blocked list) | CVF page for Cloud Score+ blocked (403) | no longer true: the CVF PDF downloaded on 2026-10-29 | — |
| 5 | — | — | addition: eq. 1 is the same linear corruption model as haze (q ≈ t); evaluation sweeps thresholds in 0.01 steps and picks balanced omission/commission; best thresholds 0.64 (Tarrio) vs 0.50 (CMIX-I); weakness: cloud shadows over water | pp. 2127, 2129–2131 |

## Aybar et al. 2022 (Sci. Data) — `aybar2022_cloudsen12_cloud_shadow_dataset_SciData`
Page numbers are the article's 1–17.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | Classes clear, thick cloud, thin cloud, cloud shadow | verified (Table 3, with superclasses cloud/non-cloud and valid/invalid) | p. 5 |
| 2 | 02 table | 14 domain experts with active learning and a four-step quality check | verified (14 CDE experts, IRIS active learning, "four-step quality control protocol") | pp. 2, 5 |
| 3 | 02 table | Labellers recalibrated if overall accuracy fell below 90% | verified | pp. 4–5, Fig. 4 |
| 4 | 02 table | 10,000 high-quality patches, 10,000 scribble, rest unlabelled | verified (2,000 ROIs × 5 = 10,000 each; 29,250 unlabelled) | p. 2 |
| 5 | 02 table | Sentinel-2 L1C/L2A (10 m) + Sentinel-1 | verified (plus DEM, land cover, water, 8 detectors' outputs) | pp. 2–3, Table 2 |
| 6 | 02 table | About 49,400 patches (paper also says 49,250) | verified: both numbers appear (abstract/usage 49,400; p. 2 49,250); Table 1 lists 46,697 scenes | pp. 1, 2, 13 |
| 7 | 02 table | 509 × 509 px | not found in paper: ROIs are 5,090 × 5,090 m (= 509 px at 10 m, consistent); network input is 512 × 512 | pp. 3, 9 |
| 8 | 02 table | Article CC-BY 4.0; data CC-BY-NC-4.0 on HF card; up to 1 TB | partly verified: article CC BY 4.0 and "up to 1 TB" are in the paper; no data licence is stated in the paper | pp. 13, 17 |
| 9 | 02 table | JIF not in file | not checked (outside the paper) | — |
| 10 | — | — | addition: human agreement 95.7% (98.3% without thin); thin cloud PA only 78%; edges drawn to "maximize the sensitivity"; thin cloud is "invalid" in their valid/invalid superclass; UNetMobV2 median BOA 0.92 vs Fmask 0.84 | pp. 5, 9–14 |

## Bonafilia et al. 2020 (CVPRW) — `bonafilia2020_sen1floods11_flood_dataset_CVPRW`
Page numbers are the CVF PDF's 1–11.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | Hand labels: −1 no data / not valid, 0 not water, 1 water (446 chips) | partly verified: 446 hand-labelled chips and a "no data" category for areas analysts "could not confidently identify" are in the paper; the numeric coding (−1/0/1) is **not in the paper** (it must come from the repo/README) | p. 4 |
| 2 | 02 table | Whether cloud is coded −1 is unconfirmed | still unconfirmed by the text; Fig. 1 shows cloud areas blank in the hand label, consistent with no data. Also: chips with majority cloud were dropped, and weak S2 labels mask cloud (blue threshold) and projected shadow | pp. 2, 4 |
| 3 | 02 table | Sentinel-1 VV/VH + Sentinel-2 L1C (13 bands); 4,831 chips of 512 × 512 | verified (L1C level not stated in the paper; "13 bands") | pp. 1, 3–4 |
| 4 | 02 table | Company-led (Cloud to Street) | verified (3 of 4 authors Cloud to Street; Tellman also Columbia) | p. 1 |
| 5 | 02 table | About 14 GB; gs://sen1floods11 | not found in paper (only the GitHub URL is given) | p. 1 |
| 6 | — | — | addition: JRC non-permanent water is "ignored" in training labels; Bolivia event hold-out; weak S2 labels beat hand labels for training; cloud shadows confused for water | pp. 3–7 |

## Domnich et al. 2021 (Remote Sens.) — `domnich2021_kappamask_sentinel2_cloudmask_RemoteSens`
Page numbers are the article's 1–22.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | Classes clear, cloud shadow, semi-transparent (thin) cloud, cloud, invalid (abstract) | verified, plus a sixth labelling class **UNDEFINED** (labeller unsure), excluded from training; invalid = "0 MISSING: missing or invalid pixels" | abstract p. 1; p. 6 |
| 2 | 02 table | Labelling method not read | now read: CVAT polygons + Segments.ai model-assisted brush, all tiles manually corrected and peer-reviewed; sub-tiles chosen by human-judged active learning | pp. 5–6 |
| 3 | 02 table | 4,403 blocks of 512 × 512 from 155 images, Northern Europe | not found as stated: the paper gives 150 products × 10 sub-tiles (~1,500) plus 2,821 sub-tiles from 6 fully labelled Estonian products (training only); 4,403/155 likely comes from the Zenodo record | p. 5–6 |
| 4 | 02 table | Remote Sensing 13:4100; KappaZeta Ltd (company) | verified (KappaZeta + ESA authors; ESA-funded) | p. 1 |
| 5 | 02 table | Licence not read (Zenodo blocked) | paper: article CC BY 4.0; data at zenodo.org/record/5095024; no data licence stated | pp. 1, 17 |
| 6 | 10 (blocked list) | MDPI blocked | the www.mdpi.com PDF is still blocked to scripts; the same v2 PDF is served from mdpi-res.com (MDPI's file server) | — |
| 7 | — | — | addition: Dice L2A 80% vs Sen2Cor 59, Fmask 61, MAJA 51; thin cloud 16% leaked to clear; test set = the hardest sub-tiles | pp. 10–12 |

## Foga et al. 2017 (RSE) — `foga2017_landsat_cloud_detection_validation_RSE`
Page numbers are the accepted manuscript's 1–54 (published 379–390).
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | L8 Biome: manual masks; thick, thin and shadow | verified (classes fill, clear, thin cloud, cloud, shadow; manual Photoshop digitising by one analyst) | pp. 8, 11–12 |
| 2 | 02 table | Shadow in 32 of 96 scenes (OpenSICDR) | not stated in the paper: it says only that shadows were digitised where "clearly identifiable" and skipped in low-sun/high-relief scenes; Table 1 marks Biome shadow as "some" | pp. 7–8 |
| 3 | 02 table | Landsat 8 OLI/TIRS, 30 m, 96 scenes | verified (8 biomes × 3 cloud bins × 4) | pp. 10–11 |
| 4 | 02 table | RSE 194:379–390 | verified (Crossref) | — |
| 5 | 02 table | USGS page states no licence | consistent: paper says datasets are "provided online at no cost"; no licence | pp. 5–6, 13 |
| 6 | 02 §1.6 | Fmask, SPARCS pair a shadow with its cloud through geometry | verified for CFMask: "Cloud shadows are derived from the dilated cloud objects"; shadow omission tied to cloud-object errors | pp. 17, 27 |
| 7 | — | — | addition: thin cloud scored as cloud (thin→thick correct, thin→clear false); CFMask 89.3% / conf 90.5%; dilation trades omission for commission; multi-date checks confounded by "natural disaster" | pp. 17, 22–25, 40 |

## Hughes & Hayes 2014 (Remote Sens.) — `hughes2014_sparcs_cloud_shadow_neural_network_RemoteSens`
Page numbers are 4907–4926.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | SPARCS: Landsat 8, 30 m, 80 subsets of 1,000 × 1,000 | **corrected**: the 2014 paper uses **Landsat 7 ETM+** (2001) — 48 training + 12 test sub-scenes of 1000 × 1000. The 80-scene Landsat 8 "L8 SPARCS" set is the later Landsat 8 extension (described in Foga et al. 2017, p. 5), not in this paper | pp. 4910–4911 |
| 2 | 02 table | Cloud and cloud shadow (no thin class) | verified: thin and core cloud merged into one cloud class; classes cloud, shadow, water, snow/ice, clear | p. 4910 |
| 3 | 02 table | Labelling method not read | now read: training = USGS manual masks + hand-edited water/snow; test = k-means (100 clusters), operator class assignment, hand correction | pp. 4910–4911 |
| 4 | 02 §1.6 | SPARCS pairs a shadow with its cloud through sun and view geometry | verified (rule iii: cloud membership shifted away from the sun for 1,800–2,700 m cloud heights, blurred 15 × 15, multiplied into shadow membership); note it uses sun direction and elevation; "view" geometry is not used | p. 4913 |
| 5 | 02 table | Remote Sensing 6:4907 | verified | — |
| 6 | — | — | addition: scoring ignores a 3-px buffer around labelled cloud/shadow; overall 98.8% vs Fmask 95.3%; thin cloud + shadows missed by both; water-edge rule | pp. 4914, 4918, 4923 |

## Mohajerani & Saeedi 2019 (IGARSS; arXiv 1901.10077) — `mohajerani2019_cloudnet_38cloud_landsat8_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | 38-Cloud: binary cloud, manual | verified (binary cloud/clear; training GTs redone manually; test GTs from the earlier dataset, 1 replaced) | p. 3 |
| 2 | 02 table | **Thin cloud (haze) counts as cloud** | not found in this paper (no thin/haze rule stated); the Cloud-Net+ paper implies it (Fig. 3 text, "thick and thin clouds (haze)") | — |
| 3 | 02 table | Landsat 8 RGB + NIR, 30 m; 38 scenes → 8,400 train + 9,201 test patches (384 × 384) | verified | pp. 2–3 |
| 4 | 02 table | Repo Apache-2.0; Kaggle needs an account | not found in paper: it says "publicly available to the research community by request" | pp. 1, 3 |
| 5 | — | — | addition: binarisation threshold 0.047; Cloud-Net Jaccard 78.50 vs Fmask 75.16 here, but 87.32 vs 85.91 in the authors' 2021 paper (different evaluation) | p. 3 |

## Mohajerani & Saeedi 2021 (JSTARS; arXiv 2001.08768) — `mohajerani2020_cloudnetplus_95cloud_jaccard_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 table | 95-Cloud in Cloud-Net+ (arXiv 2001.08768) | verified, and **published as IEEE JSTARS 14:4254–4266 (2021)** — cite the journal version; arXiv title is "Cloud and Cloud Shadow Segmentation ... Filtered Jaccard Loss ..." (not "Cloud-Net+") | p. 1 |
| 2 | 02 table | 95-Cloud adds 57 training scenes (34,701 patches); same test set | verified (21,502 after removing empty patches) | p. 6 |
| 3 | 02 table | Thin cloud (haze) counts as cloud | partly verified: Biome 8 thin + thick merged into cloud by the authors; for 38-/95-Cloud only implied by Fig. 3 text ("thick and thin clouds (haze)") | pp. 6–7 |
| 4 | 02 table | None stated (95-Cloud licence) | consistent: GitHub URL given, no licence | p. 6 |
| 5 | — | — | addition: 2-px edge buffer raised SPARCS CNN accuracy 91.04 → 95.40; SDAA synthetic shadows; snow/ice worst biome | pp. 4–9 |

<!-- group g7 -->
# Claim checks, group g7 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (the paper says something different; the
correction is given) or **not found**. Evidence files were not edited.

## Geifman & El-Yaniv 2017 (NeurIPS) — `geifman2017_selective_classification_deep_neural_networks_NeurIPS`
Page numbers are the arXiv v2 copy's 1–12.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §8 | Geifman & El-Yaniv (2017) "build a selective classifier at a risk level the user sets" | verified (SGR: user sets target risk r* and confidence δ; the true selective risk exceeds r* with probability < δ, Theorem 3.2). Note the selector is built on top of an already trained classifier, not trained jointly | abstract p. 1; Alg. 1 p. 4; Thm 3.2 p. 5 |
| 2 | 02 §8 (implied) | Usable as the risk–coverage procedure for "cannot assess" | verified with limits: the guarantee controls total 0/1 error only and assumes i.i.d. calibration/test; FP/FN control is named as open | §2 p. 3; §6 p. 11 |
| 3 | 05 §6 ("Report risk–coverage") | Risk–coverage reporting | verified: the paper defines the risk–coverage curve as "the entire performance profile" of a selective classifier | p. 3 |

## Olofsson, Foody, Herold et al. 2014 (RSE) — `olofsson2014_good_practices_area_accuracy_land_change_RSE`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §8 | Olofsson et al. (2014) is "on disk" | verified (`GGS662/reference/Olofsson et al. 2014 ….pdf`, publisher copy, 16 pp.) | — |
| 2 | 02 §8 | Usable "for reporting the cannot-assess share" | verified, and stronger than our note: the paper names cloud explicitly — "the proportion of the selected sample units for which cloud cover prevented assessment of the unit should be reported"; such units have inclusion probability zero and are a documented deviation | p. 45 |
| 3 | — (addition) | — | addition: report accuracy as an area-proportion error matrix with U/P/O and 95% CIs; estimate area from reference totals, not pixel counting; kappa "strongly discouraged"; test sample independent of training | pp. 51–52, 55 |
| 4 | — (caveat) | — | addition: estimators assume a probability sample with known inclusion probabilities; SpaceNet 8 tiles are not one, which must be stated as a deviation | pp. 44–45 |

## Le Hégarat-Mascle & André 2009 (ISPRS JPRS) — paywalled, not read
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §6 | Pairs a shadow with its cloud through sun and view geometry | not checked (no open copy; HAL hal-04113803 is a metadata-only notice). A search snippet says the method uses the property that each cloud casts a shadow of similar shape and area, and is a two-level (pixel/object) MRF on SPOT HRVIR — consistent with the claim but unverified | — |

## Li, Guo & Elkan 2011 (IEEE TGRS) — paywalled, not read
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §2 | PU learning has a TGRS remote-sensing precedent | not checked against full text; metadata confirms title, venue (TGRS 49(2):717–725) and the PU one-class topic | — |

## Xia, Yokoya & Adriano 2021 (NeurIPS workshop) — `xia2021_building_damage_self_pu_learning_NeurIPSW`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §2 | A PU precedent "in damage mapping (Xia, Yokoya & Adriano 2021; workshop paper)" | verified: AI+HADR workshop, NeurIPS 2021; building damage (Tohoku, Palu, Hurricane Michael), Self-PU with nnPU | p. 1 footer; pp. 2–4 |
| 2 | 02 §2 | Keeping cloudy "missing" labels out of the negatives is the cheapest fix | supported indirectly: treating unlabelled as negative was the worst arm on all three datasets (0.53–0.66 acc.), nnPU alone recovered most of the gap. The paper does not test the "exclude" arm, and it is about missing labels in general, not cloud | Table 1, p. 5; p. 4 |
| 3 | — (caveat) | — | addition: Self-PU tied nnPU on Hurricane Michael at r = 20, 30; only accuracy reported; class prior for nnPU not stated | Table 1 p. 5 |

## He, Sun, Yan & Fu, DABNet (IEEE TGRS) — paywalled, not read
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §3 table | "He, Sun, Yan & Fu 2021, DABNet, IEEE TGRS" | corrected (citation only): Crossref gives **TGRS vol. 60 (2022), pp. 1–16**; 2021 is the early-access year. DOI 10.1109/TGRS.2020.3045474 is correct | Crossref |
| 2 | 02 §3 table | AIR-CD = GF-2 PMS 4 m, 34 scenes, cloud-only pixel labels by experts | not checked (no open full text). A search snippet of the abstract says experiments used "the public GF-1 WFV" set and "a self-built GF-2 dataset"; whether that GF-2 set is AIR-CD is not confirmed | — |

## Zhu, Li & Shen 2024 (IEEE TGRS 62) — paywalled, not read
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §3 table | GF2MS-WHU/GF1MS-WHU from "Zhu, Li & Shen 2024, IEEE TGRS 62" | identified: **"Transferring deep models for cloud detection in multisensor images via weakly supervised learning", TGRS 62:1–18, doi 10.1109/TGRS.2024.3358824** (Crossref; the dataset–paper link is from a dataset BibTeX entry and IEEE DataPort 10.21227/8vc2-yf66, not from the paper text) | Crossref |
| 2 | 02 §3 table | 29 GF-2 and 33 GF-1 images well annotated, rest unlabelled; 4 m / 8 m | consistent with the IEEE DataPort record (GF1: 33 labelled + 141 unlabelled, 8 m; GF2: 29 labelled + 163 unlabelled, 4 m); paper itself not read | DataPort |

## Shendryk et al. 2019 — open access, download blocked
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §3 table | "Shendryk et al. 2019 (venue not verified)" | corrected: **Shendryk, Rist, Ticehurst & Thorburn (2019), ISPRS JPRS 157:124–136, doi 10.1016/j.isprsjprs.2019.08.018**, title as given; open access CC BY-NC-ND 4.0 (Crossref). ScienceDirect refused scripted PDF download (HTML/bot page), so the full text was not read and label details (block-level, 4,943/4,993 subscenes) remain unverified | Crossref, OpenAlex |

## Kethavath & Hu 2026 (arXiv 2604.08956) — `kethavath2026_low_data_adaptation_vs_prompting_cloud_segmentation_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §7 | Prompting CLIPSeg to segment cloud failed: every one of 60 prompts scored below the 0.255 mIoU zero-shot baseline | verified, with a nuance our note loses: the 0.255 baseline is itself a prompt (four simple class names), so the finding is that *engineered* prompts are worse than plain labels and that zero-shot is poor (thick cloud called thin 50% of the time). Data are Sentinel-2 10 m RGB | abstract p. 1; §4.1 p. 4; §4.3 p. 6 |
| 2 | 02 §7 | "academic preprints or workshop papers" | verified: arXiv preprint; venue not printed (code repo named 2026_CVPRW) | p. 1 |
| 3 | — (addition) | — | addition: fine-tuning on ~8 labelled images beats zero-shot; thin-cloud IoU stays 0.38–0.47 even at 100% data | pp. 5–6 |

## Min et al. 2026, RemoteShield (arXiv 2604.17243) — `min2026_remoteshield_robust_mllm_earth_observation_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §7 | "cloud and fog perturbations 'significantly impair' remote-sensing MLLMs (RemoteShield 2026)" | corrected (attribution of cause): the quoted phrase is in the abstract, but "these perturbations" are **synthetic cloud/fog overlays coupled with reworded text queries**; the main tables perturb image and text together, so the paper does not show cloud alone causes the drop. The only image-strength sweep (Fig. 4) is on grounding. Clouds are generated, not real | abstract p. 1; §3.1–3.2 pp. 3–4; Fig. 4 p. 9 |
| 2 | 02 §7 | Preprint (method attribution) | verified: arXiv v1, no venue printed | p. 1 |
| 3 | 02 §7 (My read) | Supports "Gemma describes visibility; the mask decides" | consistent: RS-specialised MLLMs were often more brittle than a general model (GeoChat grounding RPD 70.78) | p. 5; Tables 1–3 |

## Han et al. 2026, CloudWeb (arXiv 2605.07273) — `han2026_cloudweb_atmospheric_retrieval_hijacking_rs_rag_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02 §7 | "cloud-like overlays injected weather hallucinations into remote-sensing RAG answers (CloudWeb 2026)" | corrected (overstated): the overlays are **adversarially optimised per image against a known retriever** (differential evolution on a retrieval loss). Unoptimised cloud-like overlays from the same renderer reached only 6–22% W@5, and plain haze/blur < 2%. Answer-level hallucination (24–61%) was measured only on 303 queries already hijacked at retrieval, a conditional result per the authors. It is an attack paper, not evidence that natural cloud causes weather hallucination | abstract p. 1; Table 1 p. 6; Table 2 and text p. 7 |
| 2 | 02 §7 (My read) | Supports "Gemma describes visibility; the mask decides" | partly: shows CLIP embeddings are pulled toward "cloud" by bright low-frequency veils; the authors' own defences are haze screening and comparing outputs on original vs dehazed copies, which matches our design | App. F.1–F.2 pp. 24–25 |

## Zi, Xie, Zhang, Jiang, Zhu & Zhang 2021 (IEEE JSTARS 14:3811–3823) — `zi2021_thin_cloud_removal_cnn_imaging_model_JSTARS`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 §5 | "a thickness map per band, subtracted under an imaging model" | verified: x_gi = x_si − α_i x_c0; per-band maps are one reference map scaled by a per-band coefficient α_i (not independent maps per band) | eqs. 1–3b p. 3812 |
| 2 | 05 §5 | "trained on simulated thin cloud" | verified: 5,000 simulated sets; thickness maps extracted from real cloudy Landsat scenes by a 3×3 dark-pixel search and added to real clear patches | §IV p. 3816; §V-A p. 3816–3817 |
| 3 | 05 §5 | Listed as "core; abstract" | updated: full text now read; open access CC BY 4.0. Note the method needs Landsat bands 1–5 (incl. coastal, NIR); not best on real images (2nd DC, 3rd ΔH of 10 methods) | Table IV p. 3821 |
| 4 | 05 §5 | Single-date physical model "for contrast" | verified: single image, no reference date | p. 3811 |

<!-- group g8 -->
# Claim checks, group g8 (evidence 02, 05, 10 against full texts)

Compiled by Claude (AI), 2026-10-29. Verdicts: **verified**, **corrected** (paper says something different), **not found**, or **addition**. The evidence files were not edited.

## Bruzzone & Bovolo 2013 (Proc. IEEE) — `bruzzone2013_change_detection_framework_vhr_ProcIEEE`
Page numbers are the accepted manuscript's 1–48.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Top-down design that models different radiometric changes explicitly, extracts their semantic meaning, picks out the changes of interest for the application, uses multi-scale/multi-level object properties | verified (abstract) | p. 1; framework p. 10 |
| 2 | 05 | Shown on a QuickBird pair over Trento | verified; 450 × 400 px pan-sharpened crop, view angles 1.14°/9.8°. Dates inconsistent in the paper itself (text July 2005/Oct 2006, captions Oct 2005/July 2006) | p. 27, 30 |
| 3 | 05 (Q1 item 7) | "models radiometric change types apart from changes of interest" | verified: taxonomy Rad = {Acq, Grd}, Acq = {Atm, Sys}; architecture "by cancellation" subtracts non-relevant changes | pp. 12–14, 18–19 |
| 4 | 05 (My read) | "the theoretical home of 'nuisance first, then objects'" | verified as a reading, with a caveat: the worked example's nuisances are **shadow change and registration noise**, not cloud or haze. Cloud appears only in the taxonomy, with "clouds should be extracted at a higher level of processing with proper cloud-detection algorithms" | p. 13, 28–30 |
| 5 | 05 (design 1 sources) | Supports "find the big change, remove it, look again" | partly verified: the cancellation architecture has a **tuning** step that re-applies the whole procedure on the candidate parcels to re-tune the threshold after nuisances are removed (missed alarms down ~1,600 px). It re-thresholds; it does not correct pixels and re-detect small objects | p. 19, 34, 37 |
| 6 | 05 (design 3) | Indirect support for finer-scale re-detection (multi-level) | partly: multi-level = pixel/primitive/object meta-levels of abstraction, not finer spatial scale. The example uses only pixel and primitive levels | pp. 21–22, 32 |
| 7 | 05 | "Read: abstract; needs GMU" | corrected: an open accepted manuscript exists at the Trento RSLab site; now read in full | — |
| 8 | — | Numbers not in our notes | addition: false alarms 5,005 (pixel CVA) / 3,537 (parcel CVA) / 1,470 (proposed); OA 90.86 / 91.56 / 93.91%; one 450 × 400 crop, no significance test, 8,480 of 14,081 change pixels still missed | p. 37, Table I |

## Wu, Du & Zhang 2014 (TGRS) — paywalled
Not checked: no open copy found (OpenAlex no OA location; web search found only catalogue records). Note for evidence 05: the issue year is **2014** (vol. 52(5):2858–2874); 2013 is the online-first year.

## Várnai & Marshak 2009 (GRL) — `varnai2009_modis_clear_sky_reflectance_near_clouds_GRL`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | Clear-sky brightening "extends to about 15 km away from clouds" | verified | abstract p. 1; p. 2 [11]; Summary p. 4 |
| 2 | 10 | Effect is "stronger … near optically thicker clouds and … near illuminated cloud sides" | verified; also stronger at shorter wavelengths | abstract; Figs. 2–3, p. 3 |
| 3 | 10 | Near-cloud contamination measured against distance from the nearest cloud, decays gradually | verified; precise: distance is to the nearest pixel with a cloud **thick enough for an optical-thickness retrieval**, 1 km bins, excess vs the 20 km value | p. 2 [8], Fig. 1–2 |
| 4 | 10 | "Two NASA GRL studies find haze and brightening extending well past detected clouds" | partly corrected: this paper attributes "a large portion" of the brightening to **3-D radiative scattering** (light reflected by clouds scattered by air molecules), not to haze/aerosol; undetected cloud and aerosol are listed as other contributors. It is reflectance enhancement, not necessarily haze | pp. 1–4 |
| 5 | 10 | Studies at 250 m–1 km pixels, km-scale effect means a whole tile may sit inside the zone (My read) | verified as a reading: 1 km reflectance pixels (250 m used only for the mask); ocean only, low cloud, solar zenith 48° | p. 1–2 |
| 6 | 10 | "Read: abstract" | corrected: full text now read (archived NASA copy) | — |
| 7 | — | Not in our notes | addition: near shadowy sides of thick clouds the enhancement can go **negative within ~3–4 km** (cloud shadow), matching shadow length at 48° sun and 3 km cloud height; >2/3 of clear pixels lie within 20 km of cloud, histogram peak at ~5 km; 11 µm cooling near cloud is symmetric | p. 2–3 |
| 8 | — | Magnitude (not in notes) | addition (figure reads): 0.47 µm excess ≈ 0.008 reflectance at ~2 km near sunlit sides, ≈ 0.004 at 5 km, ~0 by 15 km; shadowy sides about half | Fig. 2, p. 3 |

## Koren, Remer, Kaufman, Rudich & Martins 2007 (GRL) — `koren2007_twilight_zone_clouds_aerosols_GRL`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | Clouds surrounded by "a belt of forming and evaporating cloud fragments and hydrated aerosols extending tens of kilometers" | verified | abstract p. 1 |
| 2 | 10 | Haze/brightening "tens of km" past detected clouds | verified, with numbers: MODIS reflectance excess decays "up to 30 km" with an **e-folding distance of 10 km**, linear in log(distance); 3 km vs 20 km: +5.6% (0.47 µm), +10.6% (0.66), +13.0% (2.13) | p. 1–2, p. 4, Fig. 2 |
| 3 | 10 | Pixels next to clouds still influenced; "clear pixels kept only 10 m from the gate … no published basis" (My read) | verified as a reading; the paper also says "there is no perfect mask that will unambiguously determine the cloud" | p. 2, 4 |
| 4 | 10 | Venue/affiliation "NASA GSFC/Weizmann; abstract" | verified affiliations; corrected read level: full text now read (archived NASA copy) | p. 1 |
| 5 | — | Not in notes | addition: within the first ~3 km, MODIS excess is partly 3-D scattering and stray light; the AERONET (ground) data, AOD −13% ± 2% (440 nm) / −22% ± 2% (870 nm) from the first to the second sample after a cloud, show the signal is real beyond that | p. 2, 4 |
| 6 | — | Not in notes | addition: decay is steeper where aerosol loading is higher (slope vs AOD linear, Fig. 4a) — scene haze sets the width | p. 3, Fig. 4a |
| 7 | — | Not in notes | addition: a 10 km border around detectable cloud = 34% of the cloud-free area of the globe; 30 km = 60% | p. 4 |

## Wen, Marshak, Cahalan, Remer & Kleidman 2007 (JGR-Atmospheres) — `wen2007_3d_aerosol_cloud_modis_aster_JGRA`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10 | Studied the effect with collocated MODIS and ASTER images | verified; two Brazil cumulus scenes. Note the observed part is MODIS 0.5 km pixels; ASTER is used only to build cloud fields (15 m → 90 m) for **simulations** and to check for sub-pixel cloud | pp. 2–3, 11 |
| 2 | 10 | "ASTER's visible bands are 15 m" (flagged as my addition) | verified by the paper: "15-m resolution ASTER band 2 (0.66 µm)", aggregated to 90 m for the computations | p. 3, 10 |
| 3 | 10 | Calls the cloud-induced enhancement "too large to be ignored" | verified | abstract p. 1 |
| 4 | 10 | Atmospheric study at 250 m–1 km pixels, not dehazing | partly corrected: this one goes down to **90 m** (simulation), the finest of the three; and it is a 3-D radiative-transfer (not haze/aerosol) effect | p. 10–12 |
| 5 | 10 (Várnai row context) | Near-cloud contamination decays gradually with distance | corrected for this paper: enhancement varies strongly within ~1 km (90 m) to ~3 km (0.5 km) and then **levels off to a non-zero asymptote** (0.003–0.019 reflectance) that "does not vanish" 6–8 km away; it does not decay to zero | p. 8–10, 12 |
| 6 | 10 | JGR-A 3.4, below the threshold; context only | not checked (JIF not in the paper) | — |
| 7 | — | Not in notes | addition: observed reflectance of MODIS-selected clear pixels falls ~0.0009/km (0.47 µm), ~0.0003/km (0.66 µm) from 0.5 to 3.6 km; shadows give negative enhancement, stronger at 0.66 µm and over brighter surfaces; enhancement larger over brighter surfaces; 1-D AOT bias 50–140% | p. 4–5, 12–13 |

## Hall, Riggs, DiGirolamo & Román 2019 (HESS) — `hall2019_modis_viirs_cloud_gap_filled_snow_HESS`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Cloudy pixels take the most recent clear value | verified ("replacing cloud observations in the current day M*D10A1 with the most recent previous cloud-free observation") | p. 5231 |
| 2 | 05 | A cloud-persistence count in the QA layer gives each observation's age in days since its last clear view | verified (CPC reset to 0 when clear, +1 per cloudy or missing day) | p. 5231–5232, Fig. 4 |
| 3 | 05 | Users choose how old is acceptable | verified | p. 5232, p. 5238 |
| 4 | 05 | Uncertainty is said to grow with age, but this is not measured | verified: stated on p. 5232; no error-vs-CPC analysis anywhere; evaluation is by examples and product comparisons | p. 5232–5236 |
| 5 | 05 | "Venue: confirm in JCR. Read: full text" | verified read status (full text, open). JIF not stated in the paper | — |
| 6 | 05 (Q2 answer) | "NASA's cloud-gap-filled MODIS/VIIRS snow product" | verified; note the products are MOD10A1F/MYD10A1F (500 m) and VNP10A1F (375 m); the paper recommends Terra + VIIRS, not Aqua (Aqua cloud mask leaves many "no decision" pixels) | p. 5227, 5237 |
| 7 | — | Not in notes | addition: missing data and orbit gaps are treated as cloud; series restart each 1 October; spin-up to ~8% cloud in ~8 days (MODIS) | p. 5232 |

## Liu, Huang & Cai 2023 (TGRS) — paywalled
Not checked against full text (no OA location in OpenAlex; HKU Scholars Hub record 10722/329921 exists but is blocked to scripted access). From catalogue/abstract only: the target is Sentinel-2, with a Sentinel-2 reference image and a near-target-date **Sentinel-3** image as guidance, spatiotemporal attention network; also removes thin cloud and cloud shadow; compared with ResUnet, CRN, STS-CNN, DSen2-CR. Our note (Sentinel-3 helps most where change is distinctive/heterogeneous under large clouds) is consistent with the abstract wording "heterogeneous land cover change under large-scale cloud cover" — **not verified against the full text**. Published article number 5601218, vol. 61.

## You et al. 2026 (Sci. China Inf. Sci.) — paywalled
Not checked: no open copy found (OpenAlex no OA; web search found nothing). Authors per OpenAlex: Guochu You, Fang Xu, Jun Pan, Runmin Dong (+ others), vol. 69(3). Our TLDR ("uses SAR to detect change, so that it can choose which other dates to use") remains **unverified**.

## Xu, Li & Shen 2026 (arXiv 2603.07074) — `xu2026_phyvlm_cr_all_cloud_removal_arXiv`
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | Thin cloud handled by physical inversion, thick cloud by a temporal reference | verified | p. 1, 3 (eqs. 8, 10) |
| 2 | 05 | A VLM-derived "hallucination confidence map" gates between the two | **corrected**: the hallucination confidence map U(x) weights the VLM's low-frequency colour correction (eq. 9) and the guided filtering of t. The gate between physical inversion and the temporal reference is a separate **visibility weight ω = exp(−4(1 − t))** computed from the transmission t (eq. 11). The abstract's wording ("Leveraging this confidence map as a continuous soft gate") is looser than the method section | p. 1 vs pp. 2–3 |
| 3 | 05 | Listed under "Evidence of invention" | partly: the raw VLM (Qwen-Image-Edit) does invent ("non-existent land-cover patterns and even spurious characters"); PhyVLM-CR uses it only as a prior and keeps observed high frequencies | p. 5 |
| 4 | 05 | "Method attribution; abstract" | corrected read level: full text read (5 pp.); venue is arXiv only (no journal) | — |
| 5 | — | Not in notes | addition: evaluation truth is the nearest clear date 5–45 days away, reference 20–50 days; six Sentinel-2 scenes in China; PSNR 18.8–27.2 dB vs 15.5–19.7 (mask-based physical); no significance test or ablation; α, β, t0 unreported | p. 4, Tables I–II |

## Liu, Bruzzone, Bovolo & Du 2015 (TGRS; online 2014) — `liu2015_hierarchical_unsupervised_change_detection_hyperspectral_TGRS`
Page numbers are the accepted manuscript's.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "Liu et al. (2014), IEEE TGRS" | corrected citation: issue year **2015**, 53(1):244–260; online 29 May 2014 | cover sheet; Crossref |
| 2 | 05 | "a hierarchy that separates change classes by spectral behaviour (hyperspectral)" | verified: hierarchical spectral change vector analysis (spectral-angle homogeneity test + PCA + x-means, recursively) | pp. 12–21 |
| 3 | 05 (Q3 listing) | Listed as support for separating large nuisance change from object change | **corrected**: the method does not separate nuisance from change of interest. It assumes radiometric correction has removed illumination/seasonal effects and that leftovers fall below the magnitude threshold; in the simulated data illumination-only tile swaps are counted as change endmembers | p. 12, p. 21 |
| 4 | 05 (design 3 support "coarse-to-fine networks") | Coarse-to-fine | partly: coarse-to-fine in the **spectral** sense (major → subtle changes), not spatial scale | pp. 10–11, 33 |
| 5 | — | Not in notes | addition: three-class pseudo-binary step (changed / uncertain / unchanged) with a margin δ so u = 25% of n; uncertain pixels assigned later by minimum spectral angle | pp. 13–14, 20, 25 |
| 6 | — | Not in notes | addition: real (Hyperion) results have no ground truth; quantitative results are only on simulated pairs (κ 0.993 vs 0.977/0.900) | pp. 22–31 |

## Zhang, Peng & Huang 2018 (GRSL; online 2017) — paywalled
Not checked against full text (no OA location; web search found only catalogue records). Catalogue facts: title "Object-Based Change Detection for VHR Images Based on Multiscale Uncertainty Analysis", IEEE GRSL **15(1):13–17, 2018** (evidence 05 says 2017). Abstract-level description (stacked bi-temporal multiscale segmentation, Dempster–Shafer fusion of pixel- and object-based results, multiscale uncertainty analysis with SVM; SPOT-5 and GF-1) is consistent with our note "multiscale object-based change detection run coarse to fine, on SPOT-5 and GF-1" — **unverified against full text**.

## Han, Wu, Hu, Li & Chen 2024 (TGRS) — `han2024_c2f_semicd_coarse_to_fine_semisupervised_cd_TGRS` (arXiv preprint version)
Page numbers are the arXiv PDF's 1–20.
| # | Evidence | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 05 | "a coarse-to-fine change network" | verified, with precision: C2FNet decodes change features from coarse (16 × 16 × 512) to fine (256 × 256) inside one network, trained semi-supervised with a mean teacher | pp. 1, 3–5, Fig. 5 |
| 2 | 05 (design 3) | Indirect support for finer-scale re-detection inside corrected areas | **corrected/weakened**: no two-pass detect–remove–re-detect step and no correction of inputs; "coarse-to-fine" is decoder feature scale only. It is not evidence for re-running a detector on corrected, upsampled crops | pp. 3–5 |
| 3 | 05 | "(core; abstract)" | corrected read level: full text read (arXiv version). Note the paper is mainly about **semi-supervised** learning (5–30% labels), which our note omits | pp. 1–2 |
| 4 | — | Nuisance vs change (task focus) | addition: no explicit nuisance model; the authors only say existing methods need to better distinguish "changes of interest from the changes of irrelevant", and rely on labels and attention | p. 2 |
| 5 | — | Not in notes | addition: F1 80.9–85.1% (GoogleGZ-CD, 0.55 m) at 5–30% labels vs 86.9% fully supervised; not best on WHU-CD at 5–10% labels; single runs, no significance tests | Tables II–IV |
