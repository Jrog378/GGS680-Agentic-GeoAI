# 21: Fixing the fundamentals of our cloud handling. Literature for seven gaps (2026-10-29)

**Request (Justin, 2026-10-29):** "lets try to find literature that fixes all of those issues". The issues are six gaps
in our cloud handling: colour discarded, no problem taxonomy, physics stretched, hand-tuned thresholds, texture
distorted by sub-threshold haze, and circular synthetic validation. Gap 7 was added later the same day: "I like the
idea of external weather data on cloud coverage, that could be useful in predicting whether a cloud is there or not".
**Out of scope:** cloud shadows (Justin moved them to a later 3D-geometry stage).
**Compiled by:** Claude (AI research assistant). This is a literature note, not our own measurements. No code, slide or
other file was changed.

**Method:**
- **Prior rounds re-used, not repeated.** Evidence 02, 05, 10 and 19 (19 appeared while this note was being written).
  Sources those notes already cover (He et al. 2011/2013, Zhu & Woodcock 2012/2015, Shen et al. 2015, Lin et al. 2015,
  Hagolle et al. 2010, Canty & Nielsen 2008, Koren 2007, Várnai & Marshak 2009, Cloud Score+, SEN12MS-CR, CUHK-CR) are
  cited here only with a pointer.
- **Disk.** Read from `~/Masters/papers/`: Ojala et al. 2002 and Haralick 1979 (the passages used). Read from
  `~/Masters/GGS680/references/`: Zhu & Woodcock 2012 (Fmask), the whiteness, HOT and dynamic-threshold passages.
- **Full text from open author or agency copies:**
  - Shen, Li et al. 2014 (WHU SENDIMAGE PDF).
  - Li, Shen, Weng et al. 2022 review (WHU SENDIMAGE PDF).
  - Ma et al. 2022 TIIN (Lancaster eprint).
  - Li et al. 2019 RESIDE (arXiv).
  - Lowe 2004 (author page).
  - The NOAA Enterprise Cloud Mask ATBD v1.2, 2020 (goes-r.gov).
  - Wilson & Jetz 2016 (PLOS, open access; only its abstract and data page were used).
- **Abstracts** came from OpenAlex, Semantic Scholar, USGS Publications (Chavez 1988), the UNC CPC bibliography (Song
  et al. 2001) and arXiv (Guo et al. 2017).
- **References.** Every DOI was checked against its Crossref record (`api.crossref.org/works/<doi>`) on 2026-10-29. The
  one exception is the Zenodo dataset DOI, which is a DataCite DOI; it was checked at `api.datacite.org`. No email or
  other identifier was sent.
- **Data-access tests** used anonymous bucket listings, HTTP HEAD requests and 16-byte ranged GETs. No dataset was
  downloaded. Two tiny text queries returned a few rows of observations as a side effect of testing the APIs: four
  KMSY METAR rows and one KLCH sounding header. They are reported in gap 7 as access checks, not as analysis.
- **Blocked, not bypassed:**
  - ScienceDirect abstract pages returned 403 (abstracts for Lv 2016, Zhang 2002 and Chavez 1988 came from other
    sources or are marked as missing).
  - The NRCan HOT preprint returned 404, and its abstract mirror timed out.
  - The University of Wyoming sounding page returned 404 and then 400.
  - IEEE Xplore returned an empty page for the JSTARS 2025 review, so it was read at abstract level only.
  - The textbooks (Richards 2022; Schowengerdt 2007) have no open copy. Only their Crossref metadata and chapter titles
    were seen.
  - The WHU HRC_WHU landing page rendered only a site index.

**Labels.**
- **Read depth:** *full text*, *passage* (named section read in full), *abstract*, *metadata*, *secondary* (another
  source's account of it).
- **Venue:** JIF values come from `Project/docs/literature/journal_impact_factors.md`. Venues missing from that table
  are marked "confirm in JCR". Agency documents and products are labelled **agency**, and textbooks **textbook**.
  Papers in journals below 4 are kept only as **context**.
- **Voice:** "States" is what the source did or wrote. "My read" is my inference.

---

## In short

1. **Colour can come back cheaply, and the visible-band literature supports it.**
   - Fmask's "Whiteness" and HOT tests use only the blue, green and red bands.
   - Shen et al. (2014, ISPRS JPRS) correct thin cloud from visible bands alone, including 2 m GaoFen-1 data. They
     state that thin clouds cause "high brightness and a low gradient", strongest in blue.
   - Zhang & Xiao (2014, TGRS) detect cloud in RGB aerial photographs.
   - Our spotter's training set, HRC_WHU, is itself RGB (Li et al. 2019).
   - Both Fmask and Shen et al. warn that turbid water mimics haze, so a colour test must be checked on flooded tiles.
2. **There is an authoritative taxonomy to adopt.**
   - Li, Shen, Weng et al. (2022, ISPRS JPRS, full text) split cloud processing into "dehazing/thin cloud removal, cloud
     detection, and thick cloud removal". They class detection features as mono-temporal, multi-temporal or
     multi-source.
   - They state that multi-temporal methods suit only "areas with small or periodic land cover changes". A flood breaks
     that condition.
3. **The haze model we borrowed is used on satellite data, but with known amendments.**
   - Haze is wavelength-dependent (Chavez 1988). Pan et al. (2015) add a translation term for non-uniform haze in
     remote sensing. The adjacency effect blurs as well as brightens: one hazy atmosphere coarsened Landsat TM's 30 m
     resolution to 100 m (Kaufman 1984).
   - Makarau et al. (2014, DLR) state their haze-thickness method works on "calibrated and uncalibrated" data. That is
     the closest published support for running a haze model on non-reflectance products.
4. **The two-date fix is to normalise on invariant pixels, then model the residual haze.**
   - Song et al. (2001) state that relative correction is enough for change detection, provided both dates are "in the
     same relative scale".
   - IHOT (Chen et al. 2016, TGRS) regresses the hazy image on a clear one to remove land-surface signal from the haze
     map.
   - Every two-date source assumes little land-cover change. The flood is exactly the change, so the invariant pixels
     must exclude water and flooded ground.
5. **Thresholds can be learned or reported as curves.**
   - Fmask sets its thresholds by sensitivity analysis over 142 reference scenes, plus a scene-adaptive percentile.
   - NOAA's operational cloud mask outputs a naive-Bayes posterior probability and sets its confidence cut-offs per
     surface type (agency ATBD).
   - Bruzzone & Prieto (2000) choose a change threshold by EM and Bayes rule.
   - Modern networks are "poorly calibrated", and temperature scaling fixes that cheaply (Guo et al. 2017).
6. **For texture, the literature gives an invariance argument, not an empirical study.**
   - I found no JIF > 4 study that measures how haze changes GLCM, Gabor or LBP features in VHR imagery.
   - LBP is "invariant against any monotonic transformation of the gray scale" (Ojala et al. 2002). Unit-normalised
     gradient descriptors are "invariant to affine changes in illumination" (Lowe 2004).
   - My read: within a window of constant transmission, the haze model is an affine map, so these descriptors should
     survive haze while GLCM contrast and filter energies shrink. Blur and 8-bit quantisation limit that.
7. **Validation on synthetic haze from our own model is circular, and the dehazing benchmark says so.**
   - RESIDE (Li et al. 2019, TIP) warns that synthetic-test success may not transfer "due to the large content
     divergence between synthetic and real hazy images", and adds task-driven evaluation.
   - TIIN (Ma et al. 2022, RSE) draws its synthetic haze patterns from real cirrus-band images rather than from its own
     model.
   - Evidence 19 covers validation against a reference image.
8. **External weather data can give at most a tile-level prior, and is weakest where we need it.**
   - The GOES-16 clear-sky mask has a 2 km IR pixel and a 5-minute CONUS cadence. The files for 31 Aug 2021 are listed
     on AWS. Its required accuracy applies to clouds with optical depth above 0.4. Its hit rate falls to about 45% at
     optical depth 0.01, and its 50% sensitivity is at about 0.06 (ATBD).
   - A two-year CALIPSO check over the contiguous US found clear-sky detection weaker (74.8%) than cloudy (90.9%).
   - Li et al. (2022) state that auxiliary data "usually have low resolution" and suit "low- and medium-resolution
     images". Ceilometer cloud reports miss upper-level cloud (Wagner & Kleiss 2016).

---

## Gap 1. We discarded colour

**Problem in our pipeline:** the spotter and the haze model run on a greyscale copy, although the source is 3-band RGB.
That throws away the blue–red contrast that haze tests rely on.

**Sources**
- **Zhu & Woodcock (2012). Fmask.** *RSE* 118:83–94 (12.3). Passage read in full (disk).
  - **States, whiteness:** MeanVis = (B1 + B2 + B3)/3, and the test is Σ|(Band i − MeanVis)/MeanVis| < 0.7. "As clouds
    always appear white due to their 'flat' reflectance in the visible bands", the index captures that property. The
    test "may also include some pixels of bare soil, sand, and snow/ice".
  - **States, HOT:** HOT Test = Band1 − 0.5·Band3 − 0.08 > 0, because "the spectral response to haze and thin cloud is
    different between the blue and red wavelengths". It "may also include some bright pixels like rocks, turbid water".
  - **My read:** both tests use visible bands only, so they can run on our RGB. Their constants are set for TOA
    reflectance, so on 8-bit display values the constants must be refitted (gaps 3b and 4).
- **Zhang, Guindon & Cihlar (2002). HOT.** *RSE* 82:173–187 (12.3). Secondary (Fmask's account) plus an abstract
  fragment seen in search results.
  - **States (fragment):** HOT is developed "for the detection and characterization of haze/cloud spatial
    distributions in Landsat scenes". A method that uses the transformed image to "radiometrically compensate visible
    band imagery" is also presented.
  - **States (Fmask's account):** the HOT in Zhang et al. "is built empirically from regression of DN values from
    clear-sky pixels". So it was designed on DNs, not reflectance.
- **Chen, Chen, Chen et al. (2016). Iterative HOT (IHOT).** *IEEE TGRS* 54(5):2682–2694 (9.4). Abstract.
  - **States:** HOT "often overestimate[s] haze thickness over bright surfaces". IHOT uses "a corresponding clear
    image", iterating regressions between the hazy and clear images, so "the land surface information can be removed".
- **Shen, Li, Qian, Zhang & Yuan (2014). Thin cloud removal for visible images.** *ISPRS JPRS* 96:224–235 (12.9).
  Full text (author copy).
  - **States:** "thin clouds cause two changes in visible images: high brightness and a low gradient". Across the blue,
    green and red bands, "with the increase in the wavelength, the influence of the thin clouds decreases so that the
    details, including edges and textures, increase".
  - **States, method and data:** an adaptive homomorphic filter; cloudy pixels are detected and handled separately; it
    was also applied to "2 meters spatial resolution" GaoFen-1 images.
  - **States, water:** "turbid water" needs special treatment, because the filter's brightness change "will cause
    serious radiometric distortion of the water surface".
  - **States, limitations:** the first cut-off frequency "is tuned manually"; the method "is limited to remove thin
    clouds".
- **Zhang & Xiao (2014). Cloud detection in RGB colour aerial photographs.** *IEEE TGRS* 52(11):7264–7275 (9.4).
  Abstract.
  - **States:** the method builds a "significance map", applies an "optimal threshold setting", refines the result with
    a multiscale bilateral "detail map", and finishes with "guided feathering" that "detects semitransparent cloud pixels
    around the boundaries of cloud regions".
- **Li, Shen, Cheng et al. (2019). MSCFF / HRC_WHU.** *ISPRS JPRS* 150:197–212 (12.9). Abstract; dataset in evidence
  02.
  - **States:** validated on images "with spatial resolutions ranging from 0.5 to 50 m", including "high-resolution
    images exported from Google Earth". It has "obvious advantages" over rule-based methods "especially in bright surface
    covered areas".
- Also relevant, from earlier notes: CUHK-CR, 0.5 m Jilin-1 thin and thick cloud, RGB + NIR (evidence 19); Makarau et
  al. 2014 (gap 3).

**Fix we could adopt (testable)**
- **What to add.** Restore the RGB originals and add four colour features to the spotter's feature stack (currently
  bright + texture + DINOv2; evidence 12):
  1. Fmask-style whiteness on 8-bit RGB.
  2. A HOT distance. Fit the blue–red "clear line" per tile on the *before* image's clear pixels (the IHOT idea). The
     feature is each after-pixel's distance from that line.
  3. The dark channel taken as a minimum over R, G and B. That is He et al.'s original definition; ours runs on grey.
  4. The blue-to-red gradient ratio (Shen et al. 2014: haze lowers the blue gradient most).
- **Baseline:** the current chosen spotter.
- **Scoring:**
  - Same HRC_WHU development folds and McNemar test as evidence 12, plus pixel F1 on its thin-cloud boundaries.
  - Then, on Ida, compare against NOAA aerial "ground visible" tiles (evidence 17).
  - **Required check:** report false positives on flooded, turbid-water tiles separately. Both Fmask and Shen et al.
    warn about turbid water.

---

## Gap 2. No explicit problem taxonomy

**Problem in our pipeline:** detection, thin-cloud correction and "cannot assess" were built step by step. We never
placed them in a recognised framework, so method choices were not justified by setting.

**Sources**
- **Li, Shen, Weng, Zhang, Dou & Zhang (2022). CCS detection review.** *ISPRS JPRS* 188:89–108 (12.9). Full text
  (author copy).
  - **States, stages:** "the commonly called cloud detection usually does not include the detection of thin clouds like
    haze, instead, direct dehazing and thin cloud removal is performed". "The processing of clouds usually consists of
    three parts, including dehazing/thin cloud removal, cloud detection, and thick cloud removal, which are usually
    performed independently or partially coupled".
  - **States, feature types:** spectral, spatial, temporal and multi-source features, extracted from "mono-temporal,
    multi-temporal, and multi-source data". Algorithm families: "physical-rule based, temporal-change based,
    variational-model based, and machine-learning based".
  - **States, when to use multi-temporal:** such methods "usually outperform mono-temporal based methods" and "can
    alleviate the common problems of thin cloud omission and high-bright objects commission". But they "may generate
    errors in areas with rapid and significant land cover changes" and are "only suitable for areas with small or
    periodic land cover changes".
  - **States, VHR:** "for high-resolution images with insufficient spectral information, spectral, geometric, and
    textural features, usually need to be combined".
  - **States, validation:** four reference types: manually labelled masks, cloud mask products, collocated lidar or
    radar, and ground-based cameras.
- **Shen, Li, Cheng et al. (2015). Missing-information reconstruction review.** *IEEE GRSM* 3(3):61–85 (13.7). Full
  text in evidence 10.
  - **States:** "missing" means information "completely obscured or not observed". Temporal methods "are sensitive to
    land-cover changes, especially abrupt changes".
- **Ning, Xie, Yin & Liu (2025). Cloud removal review.** *IEEE JSTARS* 18:15914–15930 (6.3). Abstract.
  - **States:** classifies removal methods "based on the type of auxiliary data used: single-image, multimodal, and
    multitemporal". It also outlines "benchmark datasets and evaluation metrics".
- **Textbooks, metadata only (not read; no open copy):**
  - Richards (2022), *Remote Sensing Digital Image Analysis*, 6th ed. (single author; earlier editions were Richards &
    Jia). Chapter 2 is "Correcting and Registering Images" and Chapter 4 "Radiometric Enhancement of Images".
  - Schowengerdt (2007), *Remote Sensing: Models and Methods for Image Processing*, 3rd ed., Academic Press/Elsevier.
  - Their treatment of haze correction was not checked. GMU access is needed before citing them on any specific point.

**Fix we could adopt:** write a one-page taxonomy into the methodology, using Li et al.'s three parts crossed with
their data settings, and place each of our steps in a cell:

| Stage (Li et al. 2022) | Our step | Data setting | Family | Evidence that the setting fits |
|---|---|---|---|---|
| Cloud detection | spotter (bright + texture + DINOv2; + colour, gap 1) | mono-temporal | spectral-spatial + machine learning | VHR needs "spectral, geometric, and textural features" |
| Thin cloud removal | `dark_reference_dehaze` + tone curve | mono-temporal physics + a reference date | hybrid | the reference part needs invariant pixels (gap 3c) |
| Thick cloud | abstain ("cannot assess") | none | none | Shen 2015 "completely obscured"; temporal filling is unsafe under abrupt change |

**Test:** this is a document fix, scored by review. For each cell, state the assumption the literature attaches to it
(e.g., "small land-cover change"), and name the experiment that checks it on Ida.

---

## Gap 3. Physics stretched

**Problem in our pipeline:** we apply He et al.'s I = J·t + A(1 − t) to thin cloud seen from orbit, on 8-bit stretched
display data rather than reflectance.

### 3a. Is the scattering model valid for thin cloud from orbit, and how does it fail?

- **Chavez (1988). Improved dark-object subtraction.** *RSE* 24:459–479 (12.3). Abstract (USGS record).
  - **States:** "atmospheric scattering is highly wavelength-dependent in the visible part of the electromagnetic
    spectrum and the scattering values are correlated with each other". Haze values "must be corrected with haze values
    that are spectral band dependent". The method picks "a relative atmospheric scattering model" to predict every
    band's haze from one starting band, and "normalizes the predicted haze values for the different gain and offset
    parameters used by the imaging system".
- **Pan, Xie, Jiang & Yin (2015). Deformed haze imaging model.** *IEEE SPL* 22:1806–1810 (confirm in JCR; probably
  below 4, so context). Abstract.
  - **States:** the model is "deformed by introducing a translation term". The transmission estimate is "insensitive to
    the texture of ground objects", and handling of "nonuniform haze is more satisfactory".
- **Li, Hu & Ai (2019). Sphere-model dark channel prior.** *IEEE GRSL* 16:472–476 (confirm in JCR). Abstract.
  - **States:** "haze and cloud are highly related to the illumination component and mainly located in the low
    frequency of an image". The DCP transmission "is very sensitive to noise". The method targets "uneven haze, thick
    haze, and thin cloud".
- **Makarau, Richter, Müller & Reinartz (2014). Haze detection and removal.** *IEEE TGRS* 52:5895–5905 (9.4; DLR).
  Abstract.
  - **States:** "inhomogeneous haze detection and removal in medium- and high-resolution" multispectral images. Dark-object
    subtraction is extended to a "haze thickness map", allowing "spectrally consistent haze removal on calibrated and
    uncalibrated satellite multispectral data". It was tested on WorldView-2. "Rare scenes with a uniform and highly
    reflecting landcover result in limitations".
- **Lv, Wang & Shen (2016). Thin clouds in visible bands.** *RSE* 179:183–195 (12.3). Metadata plus a search-snippet
  summary only, so not used for specific claims. The title says it combines empirical and radiative-transfer modelling
  for visible bands.
- **Kaufman (1984). Atmospheric effect on spatial resolution.** *Applied Optics* 23:3400 (confirm in JCR; context, NASA
  author). Abstract.
  - **States:** photons reflected from outside the field of view "are scattered by the atmosphere into the field of view
    (adjacency effect)". "The 30-m resolution of the Landsat Thematic Mapper (TM) is reduce[d] to 100 m by a hazy
    atmosphere". He derives an "atmospheric modulation transfer function".
- **Ju, Ding, Ren et al. (2021). Enhanced scattering model.** *IEEE TIP* 30:2180–2192 (13.7). Abstract. Ground-level
  photos.
  - **States:** the atmospheric scattering model "has an intrinsic limitation which leads to a dim effect". The authors
    add a "light absorption coefficient".
- From earlier notes: near-cloud brightening extends well past detected clouds (Koren et al. 2007; Várnai & Marshak
  2009; evidence 10). He et al. bound t at t0 = 0.1 because the result "is prone to noise" (evidence 10).
- **My read:** the satellite literature keeps the additive-plus-multiplicative form, but amends three things:
  1. **Airlight varies in space and by band.** Use a haze-thickness map and band-linked haze values rather than one A.
  2. **Haze lives at low frequency.**
  3. **Adjacency adds blur.** I = J·t + A(1 − t) is per-pixel and cannot represent blur.

  The ring at cloud edges (evidence 09) is consistent with both the brightening and the blur.

### 3b. Working with non-reflectance, dynamic-range-adjusted VHR products

- **Song, Woodcock, Seto, Lenney & Macomber (2001).** *RSE* 75:230–244 (12.3). Abstract.
  - **States:** "atmospheric correction is unnecessary as long as the training data and the data to be classified are
    in the same relative scale". In other cases, "corrections are mandatory to put multitemporal data on the same
    radiometric scale". "More complicated algorithms do not necessarily lead to improved performance". "Simple dark
    object subtraction… or relative atmospheric correction are recommended for classification and change detection".
- **Schott, Salvaggio & Volchok (1988)** and **Canty & Nielsen (2008, IR-MAD)**, both *RSE*. Normalisation on
  pseudo-invariant or no-change pixels; evidence 10.
- **Byun & Han (2018). Relative radiometric normalisation of bitemporal VHR images for flood change detection.** *J.
  Appl. Remote Sens.* 12:026021 (context; below 4). Abstract.
  - **States:** a MAD-based normalisation with a weighting function "based on open water features" (NDWI). On KOMPSAT-2,
    flood change-detection accuracy rose by "1.8% and 12.6%" over IR-MAD at two sites.
  - **My read:** this is the only flood-specific VHR normalisation found. It needs NIR for NDWI, which we lack.
- **Ju, Ding, Zhang & Guo (2018). Gamma-correction-based dehazing model.** *IEEE SPL* 25:1084–1088 (confirm in JCR;
  context). Abstract.
  - **States:** the model "explicitly describes the inner relationship between the gamma correction (GC) and the
    traditional scattering model".
- **My read:**
  - No JIF > 4 source was found that analyses dark-channel dehazing on stretched 8-bit satellite products.
  - Makarau's "uncalibrated" data and Chavez's gain/offset normalisation cover *linear* rescaling only.
  - A non-linear display stretch (gamma or piecewise) breaks the affine form of the haze model. Ju et al. (2018) treat
    gamma explicitly for ground photos.
  - Whether the SpaceNet 8 RGB went through a non-linear stretch is not stated in the sources read here. That needs to
    be found out (Maxar product documentation was not read).

### 3c. Principled two-date (reference-based) haze correction

- **IHOT (Chen et al. 2016)**, above: regression against a clear image removes land-surface signal from the haze map.
  **States:** it performed "robustly for hazy images that were acquired at different seasons when using the same
  reference clear image".
- **Lin, Lin, Lee & Chen (2015).** *ISPRS JPRS* 106:107–117 (12.9). Invariant-pixel normalisation and cloud detection;
  evidence 10 (abstract).
- **Ma, Wang, Tong & Atkinson (2022). TIIN.** *RSE* 274:113012 (12.3). Full text (author copy).
  - **States:** temporal neighbours give a "spatial distribution prior". But that prior "is usually not the same as for
    the target hazy images due to land cover changes". The method relies on "the proportion of land cover changes" being
    "generally small, as most changes… are driven by vegetation phenology". It uses Landsat-8 with seven bands.
- **Zhang & Guindon (2003).** *IEEE TGRS* 41:1082–1089 (9.4). Abstract.
  - **States:** they evaluated HOT "visible-band correction" against "reference or 'benchmark' clear scenes". Radiometry
    was checked on "pseudoinvariant features (dense forest stands)".
- **My read:** every two-date method assumes little change between dates, and Ida violates that by design. The
  defensible version is:
  1. Fit the before→after radiometric mapping only on invariant pixels: IR-MAD no-change pixels, excluding water,
     roads in flood zones and anything our flood labels touch.
  2. Then estimate haze as the residual from that mapping, in the IHOT spirit.

  Our current tone curve fits on all clear pixels (evidence 10).

**Fix we could adopt (testable)**
- **Arm 3-i, invariant-pixel normalisation.** Replace the all-clear-pixel tone curve with an IR-MAD fit on no-change,
  non-water pixels, per channel in RGB. Score by fold-wise road-flood F1 against the current tone curve. Add a direct
  check: the residual before/after difference on NOAA-visible clear tiles should be near zero.
- **Arm 3-ii, residual haze map.**
  - Define haze = after − f(before), where f is the 3-i mapping, and smooth it at low frequency (Shen 2014; Li et al.
    2019).
  - Compare it with our dark-channel t, by correlation on the same tiles and by edge-ring magnitude (evidence 09 metric).
  - Use it as t only where the residual exceeds what the clear-sky fit predicts.
- **Arm 3-iii, linearisation sensitivity.** Run the dark-channel step on display values raised to the power γ, for γ in
  {1.0, 1.8, 2.2}, and invert after. If road-flood F1 moves by more than the fold-to-fold spread, the stretch matters,
  and we should find the product's DRA documentation.
- **Arm 3-iv, band-linked haze.** Estimate airlight per channel with a Chavez-style relative-scattering constraint
  (blue > green > red), instead of a single grey A.

---

## Gap 4. Hand-tuned thresholds

**Problem in our pipeline:** a 20 m fade at cloud edges, a transmission cut-off of t < 0.2 and a 2,500 m² minimum blob
were chosen by hand.

**Sources**
- **Zhu & Woodcock (2012). Fmask.** Passage read in full.
  - **States:** for the whiteness threshold, "we let the 'Whiteness' threshold vary from 0.5 to 0.9 (at 0.1 intervals)
    and chose the one with the highest average cloud overall accuracy", on "142 Landsat reference images".
  - **States, scene-adaptive threshold:** the land cloud threshold is the "82.5 percentile of lCloud_Prob (Clearsky Land
    pixels) + 0.2".
- **Heidinger & Straka (2020). NOAA Enterprise Cloud Mask ATBD v1.2.** **Agency.** Full text, sections 2, 3, 7.5 and
  10.4.
  - **States, method:** it is "a naive bayesian approach trained on NASA CALIPSO Data" and produces "a cloud probability
    and a 4-level cloud mask".
  - **States, uncertainty:** uncertainty = P_cloud if the mask is clear, and 1 − P_cloud if cloudy.
  - **States, cut-offs:** earlier fixed cut-offs (0.1 and 0.9) "resulted in varying amounts of confidently-clear for
    each surface type". The current mask "sets the PCC values" per surface type, to a target share of confidently clear
    pixels.
- **Bruzzone & Prieto (2000).** *IEEE TGRS* 38:1171–1182 (9.4). Abstract.
  - **States:** empirical or "manual trial-and-error" thresholds "affect both the accuracy and the reliability".
    Instead, EM estimates the changed and unchanged distributions, and the threshold is chosen to minimise "the overall
    change detection error probability". An MRF variant adds spatial context.
- **Otsu (1979).** *IEEE Trans. SMC* 9:62–66 (confirm in JCR). Metadata. Already used for the dark flag (evidence 12).
- **Zhang & Xiao (2014)**, gap 1: "optimal threshold setting" plus "guided feathering" for semitransparent cloud edges.
- **Guo, Pleiss, Sun & Weinberger (2017). On calibration of modern neural networks.** *ICML* (top conference). Abstract
  (arXiv).
  - **States:** "modern neural networks, unlike those from a decade ago, are poorly calibrated", and "temperature
    scaling" is "surprisingly effective" on most datasets.
- From earlier notes: Cloud Score+ gives a continuous per-pixel score and lets the user set the threshold. UnCRtainTS
  reports error almost halved when the most uncertain 50% is discarded (evidence 19). All operational masks dilate
  cloud, but the buffer size is an operational choice and differs between products (evidence 10).
- **My read:** none of our three numbers is physics. The literature's answers are:
  1. Output a calibrated probability and choose the cut-off from a risk–coverage curve.
  2. Make any remaining constant scene-adaptive (a percentile) or estimate it from data (EM).
  3. When a constant is fixed, publish the sensitivity sweep that chose it, as Fmask does.

**Fix we could adopt (testable)**
- **t < 0.2 → calibrated abstention.**
  - Temperature-scale or isotonic-calibrate the spotter on HRC_WHU development folds (reliability diagram, ECE).
  - Abstain on P(cloud) > p*, with p* read off the risk–coverage curve at an error budget set in advance.
  - Score on Ida: road-flood F1 against the share of roads assessed, compared with the current t < 0.2 rule at matched
    coverage.
- **20 m fade → measured edge profile.**
  - On Ida after-tiles, plot the median spotter probability, HOT distance (gap 1) and dark channel against distance
    from the opaque-cloud edge.
  - Set the fade to the distance where the distribution becomes indistinguishable from clear-tile pixels (two-sample
    KS test).
  - Report the curve; the brief's 20 m becomes a result or is replaced.
- **2,500 m² blob → sensitivity sweep.** Sweep the minimum blob (e.g., 0–10,000 m²) and plot object-level F1 on the
  HRC_WHU folds, as Fmask did. Alternatively, drop it and keep objects whose *mean* calibrated probability passes p*.

---

## Gap 5. Sub-threshold haze distorts texture

**Problem in our pipeline:** haze too thin to trip the gate still changes texture and contrast features (local std,
Sobel, range) before change detection. A separate agent is measuring this on our data.

**Sources**
- **Kaufman (1984)**, gap 3a: the adjacency effect acts as an "atmospheric modulation transfer function". One hazy
  atmosphere took Landsat TM from 30 m to an effective 100 m.
- **Shen et al. (2014)**, gap 1: thin cloud gives "a low gradient". Edges and textures recover as wavelength increases
  (blue is worst).
- **Zhang & Guindon (2003)**, gap 3c: the assessment covered "improvement in interclass separability". Haze strong
  enough to cause "significant thematic class confusion" made "visible-band radiances of vegetated areas… at levels
  normally associated with urban features".
- **Haralick (1979). Statistical and structural approaches to texture.** *Proc. IEEE* 67:786–804 (confirm in JCR).
  Passage (disk).
  - **States:** spatial-frequency texture procedures "are not invariant under even a monotonic transformation of gray
    tone". "To compensate for this, probability quantizing can be employed", at the price of "loss of gray tone
    precision". For co-occurrence, he writes that it characterises gray-tone relationships "in a way that is invariant
    under monotonic gray tone transformations".
- **Ojala, Pietikäinen & Mäenpää (2002). LBP.** *IEEE TPAMI* 24:971–987 (18.6). Passage (disk).
  - **States:** the operator "is, by definition, invariant against any monotonic transformation of the gray scale".
    Texture has "two orthogonal properties: spatial structure (pattern) and contrast". LBP "discards… contrast", which
    can be added back with a separate variance measure.
- **Lowe (2004). SIFT.** *IJCV* 60:91–110 (confirm in JCR). Passage (author copy).
  - **States:** "a change in image contrast in which each pixel value is multiplied by a constant will multiply
    gradients by the same constant, so this contrast change will be canceled by vector normalization". A constant offset
    "will not affect the gradient values". So the descriptor "is invariant to affine changes in illumination". But
    "non-linear illumination changes" and "camera saturation" break this.
- **Not found:** a JIF > 4 study that measures haze or thin-cloud effects on GLCM, Gabor, LBP or wavelet features in
  VHR imagery, or that normalises texture for atmospheric attenuation before change detection. Searches returned only
  low-tier or unrelated papers. This is a gap in the literature, not just in our reading.
- **My read (an argument, not a source):**
  - Within a window where t and A are constant, the haze model maps J to t·J + A(1 − t), an affine map with gain
    t < 1.
  - So local std, Sobel magnitude, Gabor and wavelet energies scale by t, and GLCM contrast by roughly t². LBP and
    unit-normalised gradient histograms are unchanged.
  - Three things break the invariance:
    1. The adjacency blur (Kaufman) removes fine texture rather than scaling it.
    2. 8-bit quantisation squeezes J's range into about t × 255 levels.
    3. A non-linear display stretch (gap 3b).

**Fix we could adopt (testable)**
- **Arm 5-i, invariant descriptors.** Replace local std/range/Sobel with LBP-riu2 histograms (Ojala) and unit-normalised
  gradient-orientation histograms (Lowe-style) over the same windows. Keep a separate contrast channel so DINOv2 and the
  classifier can still use it.
- **Arm 5-ii, attenuation normalisation.** Divide the contrast features by the estimated t̂: the gap 3 dark-channel t or
  the 3-ii residual haze map. This is our own extension, with no paper behind it.
- **Scoring:**
  - Use the other agent's measured haze–texture curves. Plot feature change against estimated t on the same pixels; a
    good descriptor should be flat in t until blur dominates.
  - Then score road-flood F1 under spatial folds against the current texture stack.

---

## Gap 6. Validation without a reference (brief)

**Problem in our pipeline:** synthetic haze generated with our own model is used to test a correction built on the same
model.

- **Li, Ren, Fu, Tao et al. (2019). RESIDE.** *IEEE TIP* 28:492–505 (13.7). Full text (arXiv).
  - **States:** most methods "rely on the full-reference PSNR and SSIM metrics, with assuming a synthetic testing set".
    "Their practical applicability may be in jeopardy even [if] a promising testing performance is achieved, due to the
    large content divergence between synthetic and real hazy images".
  - **States, remedies:** adds no-reference metrics, human ratings and a "task-driven" set of 4,322 real hazy images
    with object annotations.
- **Ma et al. (2022). TIIN**, gap 3c.
  - **States:** to simulate realistic non-uniform haze, "a cirrus band from a cloudy region was employed as reference"
    transmission, using "35 cirrus maps".
  - **States, real cases:** "four real hazy images" were also tested against references.
- **Li et al. (2022)**, gap 2: physical models "can also be used to stimulate [simulate] cloud samples" for *training*.
- **Evidence 19, Q1:** pixel metrics are well defined only on synthetic data, while models trained on real observations
  "consistently outperform" synthetic-trained ones (SEN12MS-CR). Not repeated here.
- **Fix we could adopt:**
  - Make the primary score task-driven: road-flood F1 on Ida tiles where the NOAA aerial photo shows the ground
    (evidence 17).
  - Keep synthetic tests only as a secondary check. Their haze *pattern* should not come from our model, e.g. use
    HRC_WHU thin-cloud alpha mattes or transmission maps estimated on other scenes.
  - Report "synthetic on own model" separately and label it as circular.

---

## Gap 7. External weather data as a prior for cloud presence (and cloud height)

**Problem in our pipeline:** cloud presence is judged from the image alone. Independent atmospheric evidence (satellite
cloud products, airport reports, reanalysis) is not used, even as a sanity check.

**Sources**
- **Heidinger & Straka (2020). NOAA Enterprise Cloud Mask (ECM) ATBD v1.2.** **Agency.** Full text, sections 2, 3, 7.5
  and 10.4. The ABI Clear Sky Mask (ACM) uses this algorithm.
  - **States, resolution:** the ABI visible band has a "native resolution of 0.5km", with "sixteen corresponding pixels
    that are contained within a single 2km IR pixel" (used for sub-pixel uniformity tests).
  - **States, accuracy requirement:** "the overall global ACC requirement for the ECM is 87% for clouds with an optical
    depth (COD) greater than 0.4". Snow-free land by day: 90%.
  - **States, thin cloud:** "for the smallest optical depths analyzed (0.01), the hit rates fall to 30%, 45% and 35% for
    VIIRS, ABI-AHI and MODIS". Optical-depth sensitivity, where the hit rate drops to 50%, is "0.1, 0.06 and 0.03".
  - **States, ancillary inputs:** NWP surface temperature and other fields enter its clear-sky expectations.
- **GOES-R product page (goes-r.gov). Agency.** Read.
  - **States:** the clear sky mask classifies each pixel as "cloudy, probably cloudy, clear, or probably clear".
  - **States, cloud top height:** retrieved from IR bands. It supplements "upper-level cloud information to the
    ground-based Automated Surface Observing System (ASOS)".
- **Jiménez (2020). GOES-16 ACM vs CALIPSO over the contiguous US.** *Remote Sensing* 12:1630 (4.3, narrow). Abstract.
  - **States:** two years, compared on a 9 km grid. "Probability of detection… of all sky conditions of 86.0%"; cloudy
    "90.9%", clear "74.8%". Clear-sky errors come from "missdetections during daytime", especially in summer. "Regions
    to the south of parallel 36 show acceptable performance".
- **Ackerman et al. (1998). MODIS cloud mask (MOD35).** *JGR-Atmospheres* 103:32141 (3.4, below; NASA/UW operational
  algorithm, context). Abstract.
  - **States:** each test "returns a confidence level that the pixel is clear"; the product of group confidences gives
    clear-sky confidence.
- **Frey et al. (2020). Continuity MODIS-VIIRS Cloud Mask.** *Remote Sensing* 12:3334 (4.3, narrow). Abstract.
  - **States:** against collocated CALIOP lidar, combined clear and cloudy hit rates were "88.2%… 86.8%" for
    June–August 2018.
- **Wilson & Jetz (2016). Global 1 km cloud frequency.** *PLOS Biology* 14:e1002415 (confirm in JCR). Abstract and data
  page.
  - **States:** "monthly cloud frequencies from 15 y of twice-daily" MODIS images, at about 1 km.
  - **My read:** this is climatology only. It can say how often August is cloudy at our location, not whether a cloud
    was there on 31 Aug.
- **Wagner & Kleiss (2016). Ceilometer cloud-amount errors.** *J. Atmos. Oceanic Technol.* 33:1557 (confirm in JCR;
  probably below 4, context). Abstract; NOAA repository copy available.
  - **States:** errors "caused by the limited vertical range" dominate those from limited areal coverage. "Observations
    of clear sky or few clouds are often in error as the instrument cannot detect the presence of upper-level clouds".
    The largest errors occur "in the morning and summer".
- **Götz, Wessel, Çayoğlu, Jahani et al. (2025). METAR labels for Sentinel-2 cloud cover.** *IEEE JSTARS* 18:10674
  (6.3). Abstract.
  - **States:** they trained on "ordinal point labels from ground-based weather stations (METAR)". Station labels alone
    gave "an F1-score of up to 0.6". Adding visually corrected labels "to correct for station-satellite mismatches"
    raised it to 0.75.
- **Yeom, Roujean, Han et al. (2020). GOCI geostationary thin-cloud detection.** *RSE* 239:111610 (12.3). Abstract.
  - **States:** a 500 m geostationary sensor without thermal bands. Clouds are detected against a BRDF-modelled clear
    background, because "surface BRDF varies slowly with time compared to that of clouds". Against CALIPSO, probability
    of detection was 0.831 (MODIS 0.772), and 0.849 for thin cirrus.
- **Li et al. (2022) review**, gap 2.
  - **States:** auxiliary data such as "ice/snow data… surface temperature… DEMs… synthetic cloud-free images… land
    cover maps… water occurrences" improve detection, and multi-source methods "outperform mono-temporal methods".
  - **States, limits:** "auxiliary data usually have low resolution, these methods are more suitable for low- and
    medium-resolution images". MODIS MOD35 is "considered a benchmark or standard reference cloud mask".
- **Hersbach et al. (2020). ERA5.** *QJRMS* 146:1999–2049 (confirm in JCR; ECMWF, **agency**). Metadata. The hourly
  0.25° `total_cloud_cover` field was seen in the public ARCO-ERA5 bucket (below).
- **Not found:** a JIF > 4 paper that fuses geostationary or reanalysis cloud information into *sub-metre* cloud masks
  and reports a gain. The fusion literature found works at 30 m or coarser, or uses auxiliary data other than weather.
- **My read:**
  - One GOES 2 km IR pixel covers about 4,000 × 4,000 of our 0.5 m pixels, so GOES can be at most a **tile-level prior
    or cross-check**.
  - It is weakest exactly where we need help: thin cloud and haze below optical depth 0.4, with a hit rate near 45% at
    0.01.
  - Clear-sky calls in daytime summer are its least reliable class (Jiménez 2020). Ida fell in daytime summer.
  - Cloud-top height (ACHA) could feed the deferred 3D/shadow stage and a parallax correction of the GOES pixel
    position. The displacement size was not computed here.
  - METAR at airports is point-sampled and blind above the ceilometer's range.

**Access for Ida (29 Aug–2 Sep 2021; 29.6–29.85 N, 89.9–90.15 W).** Tested 2026-10-29, no data downloaded.

| Source | What | Test | Result |
|---|---|---|---|
| **GOES-16 ABI L2 on AWS** (`noaa-goes16`) | ACMC (clear sky mask), ACHAC (cloud-top height), CODC (cloud optical depth), CONUS | anonymous S3 listing, prefixes `ABI-L2-{ACMC,ACHAC,CODC}/2021/243/16/` | 200. Files every 5 min (e.g., `OR_ABI-L2-ACMC-M6_G16_s20212431601171…nc`, 386,420 B; ACHAC 302,332 B; CODC 4,321,576 B). Day 243 = 31 Aug 2021, hour 16 UTC |
| **MODIS MOD35_L2 (LAADS)** | Terra cloud mask granules | JSON listing of `/archive/allData/61/MOD35_L2/2021/243`, plus a HEAD on one granule | listing 200; HEAD 200, 3,134,458 B. Not tested whether a full GET needs an Earthdata token |
| **IEM ASOS/METAR** | KMSY and KNEW sky cover and heights | `asos.py` CSV request, 31 Aug 2021 | KMSY returned CLR at 15:53, 16:53 and 17:53 UTC, then FEW 3,400 ft / SCT 7,000 ft at 18:53. KNEW returned no rows |
| **Soundings** | Slidell LIX (72233) | IEM `raob.py` for KLIX and LIX, 30 Aug 12Z, 31 Aug 12Z, 1 Sep 00Z | empty profiles. KLCH (Lake Charles) 31 Aug 12Z exists. The NCEI IGRA file `USM00072233-data.txt.zip` gave HEAD 200, 93,267,280 B (period of record; whether 31 Aug 2021 is inside was not checked). U. Wyoming: 404/400 |
| **ERA5** | hourly 0.25° total cloud cover | Google public bucket `gcp-public-data-arco-era5`, prefix `ar/full_37-1h-0p25deg-chunk-1.zarr-v3/total_cloud_cover/` | listing 200 (`.zarray`, `.zattrs`). The Copernicus CDS page loads (200), but CDS downloads need an account |

**Caveats.**
- The pass time of Maxar catalog `10300100C46F5900` is unconfirmed (evidence 17: probably 31 Aug 2021, local late
  morning, i.e., roughly 15–17 UTC).
- KMSY reporting CLR while our after-image shows cloud is *not* a contradiction:
  1. The airport sits west of both scenes.
  2. Ceilometers miss upper-level cloud (Wagner & Kleiss 2016).
  3. The pass time is unknown.
- That this check alone cannot settle the question is itself evidence for the "sanity check only" role.

**Fix we could adopt (testable)**
- **Arm 7-i, GOES tile prior and feature.**
  - For each development tile, take the ACM 4-level value, the cloud probability (if the distributed L2 files carry it;
    the ATBD describes one, but the file variables were not checked), COD and ACHA. Use the 2 km pixel(s) covering the
    tile in each 5-minute scan from 15:00 to 18:00 UTC on 31 Aug.
  - Summarise per tile as the maximum, and as the value at the nearest scan once the pass time is known.
  - **Scoring:**
    - AUC of the GOES tile cloud value against our spotter's tile cloud fraction.
    - AUC against "ground visible in NOAA aerial" tiles (evidence 17).
    - The sensitivity of both to the assumed scan time.
  - Add it to the spotter's stacker only if the AUC beats the spotter on held-out folds. HRC_WHU images carry no
    time or location, so this can be trained and tested only on Ida tiles.
- **Arm 7-ii, cross-check flag.** Flag tiles where the spotter says clear but GOES says confidently cloudy with COD
  > 0.4, and the reverse, for human review. Report how many there are and what the NOAA photo shows.
- **Arm 7-iii, METAR and ERA5 as context only.** Report the KMSY/KNEW sky condition and ERA5 total cloud cover at the
  pass hour in the methods text. Do not use them as features: METAR is point-sampled and range-limited, and ERA5's
  0.25° grid is coarser than both scenes together.

---

## Ranked fix list (most evidence and most feasible first)

| # | Fix | Gap | Evidence strength | Effort | Needs | Replaces / scored by |
|---|---|---|---|---|---|---|
| 1 | Add RGB colour features (whiteness, HOT distance against a before-image clear line, RGB dark channel, blue/red gradient ratio) to the spotter | 1 | Strong: Fmask, HOT/IHOT, Shen 2014, Zhang & Xiao 2014, MSCFF (RSE/ISPRS/TGRS) | S | RGB only (HOT distance also uses the before date) | grey spotter; HRC_WHU folds + McNemar, NOAA-visible Ida tiles, turbid-water false positives reported separately |
| 2 | Calibrated probability + risk–coverage abstention instead of t < 0.2 | 4 | Strong: NOAA ECM posterior/4-level, Guo 2017, Cloud Score+, UnCRtainTS | S–M | none beyond HRC_WHU dev labels | t < 0.2; road-flood F1 at matched coverage |
| 3 | Sensitivity sweeps for the fade and the minimum blob; edge-profile measurement of the fade | 4 | Medium–strong: Fmask sweep; operational dilation practice (evidence 10) | S | none | 20 m and 2,500 m²; object F1 curves, KS test on edge profiles |
| 4 | Task-driven primary validation on NOAA-visible tiles; synthetic haze only with external patterns, labelled circular otherwise | 6 | Strong: RESIDE (TIP), TIIN (RSE), evidence 19 | M | NOAA aerial tiles (evidence 17) | synthetic-on-own-model scores |
| 5 | Invariant-pixel two-date normalisation (IR-MAD on no-change, non-water pixels) before dehazing | 3b/3c | Strong in principle: Song 2001, Schott 1988, Canty & Nielsen 2008, Lin 2015; flood-specific only in a low-JIF venue | M | reference (before) date | all-clear-pixel tone curve; road-flood F1, residual on clear tiles |
| 6 | Residual haze map (after − f(before)), low-frequency, compared with dark-channel t | 3c | Medium: IHOT (TGRS), TIIN (RSE); all assume small change | M | reference date + fix 5 | dark-channel t; correlation, edge-ring metric |
| 7 | Haze-invariant texture (LBP-riu2, normalised gradient histograms) + t̂-normalised contrast | 5 | Medium: invariance theory from Ojala, Lowe, Haralick; no empirical haze study found | M | RGB/grey | std/Sobel/range stack; flat-in-t curves (other agent's data), fold F1 |
| 8 | Taxonomy table in the methodology | 2 | Strong: Li 2022, Shen 2015, Ning 2025 | S | none | document review |
| 9 | Band-linked airlight (Chavez constraint) and γ-linearisation sensitivity arms | 3a/3b | Medium for band-linking (Chavez, Makarau); weak for the stretch (only low-JIF gamma papers) | S | RGB | single grey A; fold F1 spread |
| 10 | Visible-band physical thin-cloud correction (adaptive homomorphic filter, Shen 2014) as an alternative arm to the dark channel | 1/3a | Medium: ISPRS full text, 2 m GaoFen-1 shown, needs one manual cut-off | M–L | RGB | `dark_reference_dehaze`; same scoring as fix 4 |
| 11 | GOES-16 ACM/COD/ACHA tile prior and cross-check flag | 7 | Weak for VHR: agency ATBD and CONUS validation, but sensitivity collapses below COD 0.4 and Li 2022 says auxiliary data suit low/medium resolution | M | external data (AWS, tested) + the Maxar pass time | spotter-only tile calls; AUC against the spotter and NOAA-visible tiles |
| 12 | METAR/ERA5 reported as context | 7 | Weak: Wagner & Kleiss 2016, Götz 2025 F1 ≤ 0.75 | S | IEM (tested), ARCO-ERA5 (tested) | none (not a feature) |

---

## Datasets found

Justin's rule (2026-10-29): a dataset is listed only if its files were *tested* as fetchable without downloading them.
Tests were anonymous listings, HEAD requests or 16-byte ranged GETs, run on 2026-10-29 with `curl`. Datasets already
documented elsewhere are not repeated: HRC_WHU in evidence 02 (already in use); NOAA ERI aerial, 3DEP and CUHK-CR in
evidence 17 and 19.

| Name | Paper | Contents | Labels / truth, how made | Download test (URL · method · status · size) | Licence (as stated) | Size | What we could compare or replicate | How it helps our problem | Fit |
|---|---|---|---|---|---|---|---|---|---|
| **GOES-16 ABI L2 Clear Sky Mask (ACMC), Cloud Top Height (ACHAC), Cloud Optical Depth (CODC)** | Heidinger & Straka 2020 ATBD (agency); Jiménez 2020 | Geostationary ABI, 2 km IR (0.5 km visible used inside), CONUS every 5 min; 4-level mask, cloud-top height, COD | Algorithm output (naive Bayes trained on CALIPSO), not human labels | `https://noaa-goes16.s3.amazonaws.com/?list-type=2&prefix=ABI-L2-ACMC/2021/243/16/` · S3 listing · 200 · files 386,420 B (ACMC), 302,332 B (ACHAC), 4,321,576 B (CODC) | NOAA NODD: "open to the public and can be used as desired"; attribution requested; no implied endorsement (AWS registry page) | about 0.3–4.3 MB per 5-min file; 36 scans per product for 15–18 UTC | Jiménez 2020: 86.0% all-sky agreement with CALIPSO. We cannot replicate that (no CALIPSO), but we can compare ACM with our spotter per tile | Tile prior and cross-check for cloud presence; ACHA for the deferred 3D stage | Med |
| **MODIS Terra MOD35_L2 cloud mask, C6.1** | Ackerman et al. 1998; Frey et al. 2020 | Swath cloud-mask granules with clear-sky confidence levels (pixel size and granule length not verified in the sources read) | Algorithm output | `https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/MOD35_L2/2021/243/MOD35_L2.A2021243.0000.061.2021243153611.hdf` · HEAD · 200 · 3,134,458 B (directory JSON listing also 200) | NASA EOSDIS (not read on this page); a full GET may need an Earthdata login (unverified) | about 3 MB per granule | Frey 2020: CALIOP hit rates about 87–88%. Not replicable here | Second independent coarse cloud call near the Terra pass (Terra's morning pass; whether a granule covers our area on 31 Aug was not checked) | Low–Med |
| **EarthEnv Global 1 km Cloud Frequency (MODCF)** | Wilson & Jetz 2016, PLOS Biol | Monthly mean cloud frequency from 15 years of twice-daily MODIS, about 1 km, global GeoTIFFs | Derived from the MODIS cloud flags | `https://data.earthenv.org/cloud/MODCF_monthlymean_08.tif` · HEAD 200, Content-Length 882,577,061 B; ranged GET 0–15 → 206 | CC BY-NC 4.0 (**non-commercial**) | about 0.88 GB per monthly global file | No metric to replicate | August climatological prior only; not event-specific | Low |
| **ARCO-ERA5 (Google public bucket)** | Hersbach et al. 2020 (ECMWF, agency) | Hourly 0.25° reanalysis, including `total_cloud_cover`, 1959 onwards (Zarr) | Model reanalysis | `https://storage.googleapis.com/storage/v1/b/gcp-public-data-arco-era5/o?prefix=ar/full_37-1h-0p25deg-chunk-1.zarr-v3/total_cloud_cover/` · JSON listing · 200 · `.zarray` 373 B | Not read on the bucket (ERA5's Copernicus licence presumably applies; unverified) | Chunked Zarr; a point time series needs only a few chunks | None | Context for the pass hour (fix 12) | Low |
| **IEM ASOS/METAR archive** | Data source for Götz et al. 2025 type labels (they collected METAR; the source archive was not checked) | Hourly and special airport obs: sky cover layers and heights (KMSY, KNEW) | Automated ceilometer | `https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=MSY…` · GET of a 1-day CSV (a few rows) · 200 | Not stated on the request page (unverified) | KB per day | Götz 2025 F1 0.6–0.75 for METAR-labelled Sentinel-2 tiles; not replicable at VHR | Sanity check of sky state at the pass time | Low |
| **NCEI IGRA radiosondes, station 72233 (Slidell)** | Context for gap 7 (no paper here) | Period-of-record sounding text file | Radiosonde | `https://www.ncei.noaa.gov/data/integrated-global-radiosonde-archive/access/data-por/USM00072233-data.txt.zip` · HEAD · 200 · 93,267,280 B | NOAA (not read) | 93 MB zip | None | Cloud-layer and height context; the IEM copy shows no LIX profile for 30 Aug–1 Sep | Low |
| **Sentinel-2 Cloud Mask Catalogue** | Francis, Mrziglod & Sidiropoulos 2020 (listed by Li et al. 2022) | Sentinel-2 L1C subscenes with masks (subscene count, resolution and bands **unverified**; README not read) | Cloud masks plus classification tags (how they were made **unverified**; README not read) | `https://zenodo.org/api/records/4172871` · Zenodo files API · 200 · `masks.zip` 7,241,097 B, `subscenes.zip` 15,197,196,473 B, `classification_tags.csv` 77,940 B | CC BY 4.0 (Zenodo metadata) | about 15.4 GB | Could test whether our RGB colour features (fix 1) generalise to another sensor; not a VHR test | Second-sensor check of the colour tests (whether the tags separate thin cloud is unverified) | Low–Med |

**Not tested / not openly downloadable**
- **RESIDE** (Li et al. 2019): the project site lists Google Drive and Baidu Pan links only. No file size could be read
  by script; Baidu needs an account.
- **MSCFF validation data / HRC_WHU** (Li et al. 2019): the WHU landing pages rendered only a site index. HRC_WHU is
  documented and in use via evidence 02.
- **Sphere-model DCP data** (Li, Hu & Ai 2019): the abstract says the code and datasets are public, but no URL was
  located (a guessed GitHub path gave 404).
- **TIIN Landsat-8 pairs** (Ma et al. 2022): built from USGS Landsat Collection 2; no packaged release located.
- **METAR–Sentinel-2 dataset** (Götz et al. 2025): described as "custom-collected"; no release located.
- **CALIPSO/CALIOP layer products** (used by Jiménez 2020, the ATBD and Yeom 2020): NASA ASDC, Earthdata login; not
  tested.
- **ERA5 via the Copernicus CDS:** account required (the ARCO copy above was tested instead).
- **University of Wyoming soundings:** 404/400 on 2026-10-29.
- **Zhang & Xiao 2014 RGB aerial cloud photos:** no release found.
- **L7 Irish, L8 Biome, WHUS2_CD, GF1_WHU, Levir_CS** (listed in Li et al. 2022): not tested this round. All are 16 m
  or coarser and multispectral. Li et al. keep a catalogue at `github.com/dr-lizhiwei/OpenSICDR`, whose page returned
  200.

---

## References (DOIs checked against Crossref, 2026-10-29)

| # | Reference | Venue / JIF | Read depth |
|---|---|---|---|
| 1 | Ackerman, S. A., Strabala, K. I., Menzel, W. P., Frey, R. A., et al. (1998). Discriminating clear sky from clouds with MODIS. *J. Geophys. Res. Atmos.* 103(D24), 32141–32157. https://doi.org/10.1029/1998JD200032 | JGR-A 3.4 (aggregator, evidence 10), below; NASA/UW operational algorithm, context | Abstract |
| 2 | Bruzzone, L., & Prieto, D. F. (2000). Automatic analysis of the difference image for unsupervised change detection. *IEEE TGRS* 38(3), 1171–1182. https://doi.org/10.1109/36.843009 | TGRS 9.4 | Abstract |
| 3 | Canty, M. J., & Nielsen, A. A. (2008). Automatic radiometric normalization of multitemporal satellite imagery with the iteratively re-weighted MAD transformation. *RSE* 112(3), 1025–1036. https://doi.org/10.1016/j.rse.2007.07.013 | RSE 12.3 | Full text (evidence 10) |
| 4 | Chavez, P. S. (1988). An improved dark-object subtraction technique for atmospheric scattering correction of multispectral data. *RSE* 24(3), 459–479. https://doi.org/10.1016/0034-4257(88)90019-3 | RSE 12.3; USGS | Abstract (USGS record) |
| 5 | Chen, S., Chen, X., Chen, J., Jia, P., Cao, X., & Liu, C. (2016). An iterative haze optimized transformation for automatic cloud/haze detection of Landsat imagery. *IEEE TGRS* 54(5), 2682–2694. https://doi.org/10.1109/TGRS.2015.2504369 | TGRS 9.4 | Abstract |
| 6 | Frey, R. A., Ackerman, S. A., Holz, R. E., Dutcher, S., et al. (2020). The Continuity MODIS-VIIRS Cloud Mask. *Remote Sensing* 12(20), 3334. https://doi.org/10.3390/rs12203334 | Remote Sensing 4.3 (narrow) | Abstract |
| 7 | Götz, M., Wessel, E., Çayoğlu, U., Jahani, B., et al. (2025). Ordinal METAR cloud cover classification in Sentinel-2 satellite data. *IEEE JSTARS* 18, 10674–10683. https://doi.org/10.1109/JSTARS.2025.3557931 | JSTARS 6.3 | Abstract |
| 8 | Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *ICML 2017* (PMLR 70). arXiv:1706.04599 | ICML (top conference) | Abstract (arXiv) |
| 9 | Hagolle, O., Huc, M., Pascual, D. V., & Dedieu, G. (2010). A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images. *RSE* 114(8), 1747–1755. https://doi.org/10.1016/j.rse.2010.03.002 | RSE 12.3; CNES | Abstract (evidence 10) |
| 10 | Haralick, R. M. (1979). Statistical and structural approaches to texture. *Proc. IEEE* 67(5), 786–804. https://doi.org/10.1109/PROC.1979.11328 | Proc. IEEE (confirm in JCR) | Passage (disk) |
| 11 | He, K., Sun, J., & Tang, X. (2011). Single image haze removal using dark channel prior. *IEEE TPAMI* 33(12), 2341–2353. https://doi.org/10.1109/TPAMI.2010.168 | TPAMI 18.6; MSRA | Full text (evidence 10) |
| 12 | Heidinger, A., & Straka, W. (2020). *NOAA Enterprise Cloud Mask, Algorithm Theoretical Basis Document*, v1.2, 1 Oct 2020. NOAA/NESDIS/STAR. https://www.goes-r.gov/s3/2025-12/ATBD_Enterprise_Cloud_Mask_v1.2_2020_10_01.pdf | **Agency** | Full text (sections 2, 3, 7.5, 10.4) |
| 13 | Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., et al. (2020). The ERA5 global reanalysis. *Q. J. R. Meteorol. Soc.* 146(730), 1999–2049. https://doi.org/10.1002/qj.3803 | QJRMS (confirm in JCR); ECMWF, agency | Metadata |
| 14 | Jiménez, P. A. (2020). Assessment of the GOES-16 Clear Sky Mask product over the contiguous USA using CALIPSO retrievals. *Remote Sensing* 12(10), 1630. https://doi.org/10.3390/rs12101630 | Remote Sensing 4.3 (narrow) | Abstract |
| 15 | Ju, M., Ding, C., Zhang, D., & Guo, Y. J. (2018). Gamma-correction-based visibility restoration for single hazy images. *IEEE Signal Processing Letters* 25(7), 1084–1088. https://doi.org/10.1109/LSP.2018.2839580 | SPL (confirm in JCR; context) | Abstract |
| 16 | Ju, M., Ding, C., Ren, W., Yang, Y., et al. (2021). IDE: Image dehazing and exposure using an enhanced atmospheric scattering model. *IEEE TIP* 30, 2180–2192. https://doi.org/10.1109/TIP.2021.3050643 | TIP 13.7 | Abstract |
| 17 | Kaufman, Y. J. (1984). Atmospheric effect on spatial resolution of surface imagery. *Applied Optics* 23(19), 3400. https://doi.org/10.1364/AO.23.003400 | Applied Optics (confirm in JCR; context); NASA author | Abstract |
| 18 | Li, B., Ren, W., Fu, D., Tao, D., et al. (2019). Benchmarking single-image dehazing and beyond. *IEEE TIP* 28(1), 492–505. https://doi.org/10.1109/TIP.2018.2867951 | TIP 13.7 | Full text (arXiv) |
| 19 | Li, J., Hu, Q., & Ai, M. (2019). Haze and thin cloud removal via sphere model improved dark channel prior. *IEEE GRSL* 16(3), 472–476. https://doi.org/10.1109/LGRS.2018.2874084 | GRSL (confirm in JCR) | Abstract |
| 20 | Li, Z., Shen, H., Cheng, Q., Liu, Y., et al. (2019). Deep learning based cloud detection for medium and high resolution remote sensing images of different sensors. *ISPRS JPRS* 150, 197–212. https://doi.org/10.1016/j.isprsjprs.2019.02.017 | ISPRS 12.9 | Abstract; dataset in evidence 02 |
| 21 | Li, Z., Shen, H., Weng, Q., Zhang, Y., Dou, P., & Zhang, L. (2022). Cloud and cloud shadow detection for optical satellite imagery: Features, algorithms, validation, and prospects. *ISPRS JPRS* 188, 89–108. https://doi.org/10.1016/j.isprsjprs.2022.03.020 | ISPRS 12.9 | Full text (author copy) |
| 22 | Lin, C.-H., Lin, B.-Y., Lee, K.-Y., & Chen, Y.-C. (2015). Radiometric normalization and cloud detection of optical satellite images using invariant pixels. *ISPRS JPRS* 106, 107–117. https://doi.org/10.1016/j.isprsjprs.2015.05.003 | ISPRS 12.9 | Abstract (evidence 10) |
| 23 | Lowe, D. G. (2004). Distinctive image features from scale-invariant keypoints. *IJCV* 60(2), 91–110. https://doi.org/10.1023/B:VISI.0000029664.99615.94 | IJCV (confirm in JCR) | Passage (author copy, §6.1) |
| 24 | Ma, X., Wang, Q., Tong, X., & Atkinson, P. M. (2022). A deep learning model for incorporating temporal information in haze removal. *RSE* 274, 113012. https://doi.org/10.1016/j.rse.2022.113012 | RSE 12.3 | Full text (author copy) |
| 25 | Makarau, A., Richter, R., Müller, R., & Reinartz, P. (2014). Haze detection and removal in remotely sensed multispectral imagery. *IEEE TGRS* 52(9), 5895–5905. https://doi.org/10.1109/TGRS.2013.2293662 | TGRS 9.4; DLR | Abstract |
| 26 | Ning, J., Xie, L., Yin, J., & Liu, Y. (2025). Cloud removal advances: A comprehensive review and analysis for optical remote sensing images. *IEEE JSTARS* 18, 15914–15930. https://doi.org/10.1109/JSTARS.2025.3580718 | JSTARS 6.3 | Abstract |
| 27 | Ojala, T., Pietikäinen, M., & Mäenpää, T. (2002). Multiresolution gray-scale and rotation invariant texture classification with local binary patterns. *IEEE TPAMI* 24(7), 971–987. https://doi.org/10.1109/TPAMI.2002.1017623 | TPAMI 18.6 | Passage (disk) |
| 28 | Otsu, N. (1979). A threshold selection method from gray-level histograms. *IEEE Trans. Systems, Man, and Cybernetics* 9(1), 62–66. https://doi.org/10.1109/TSMC.1979.4310076 | IEEE SMC (confirm in JCR) | Metadata |
| 29 | Pan, X., Xie, F., Jiang, Z., & Yin, J. (2015). Haze removal for a single remote sensing image based on deformed haze imaging model. *IEEE Signal Processing Letters* 22(10), 1806–1810. https://doi.org/10.1109/LSP.2015.2432466 | SPL (confirm in JCR; context) | Abstract |
| 30 | Richards, J. A. (2022). *Remote Sensing Digital Image Analysis* (6th ed.). Springer. https://doi.org/10.1007/978-3-030-82327-6 | **Textbook** | Metadata (chapter titles) |
| 31 | Schott, J. R., Salvaggio, C., & Volchok, W. J. (1988). Radiometric scene normalization using pseudoinvariant features. *RSE* 26(1), 1–16. https://doi.org/10.1016/0034-4257(88)90116-2 | RSE 12.3 | Metadata (evidence 10) |
| 32 | Schowengerdt, R. A. (2007). *Remote Sensing: Models and Methods for Image Processing* (3rd ed.). Academic Press/Elsevier. https://doi.org/10.1016/B978-0-12-369407-2.X5000-1 | **Textbook** | Metadata |
| 33 | Shen, H., Li, H., Qian, Y., Zhang, L., & Yuan, Q. (2014). An effective thin cloud removal procedure for visible remote sensing images. *ISPRS JPRS* 96, 224–235. https://doi.org/10.1016/j.isprsjprs.2014.06.011 | ISPRS 12.9 | Full text (author copy) |
| 34 | Shen, H., Li, X., Cheng, Q., Zeng, C., et al. (2015). Missing information reconstruction of remote sensing data: A technical review. *IEEE GRSM* 3(3), 61–85. https://doi.org/10.1109/MGRS.2015.2441912 | GRSM 13.7 | Full text (evidence 10) |
| 35 | Song, C., Woodcock, C. E., Seto, K. C., Lenney, M. P., & Macomber, S. A. (2001). Classification and change detection using Landsat TM data: When and how to correct atmospheric effects? *RSE* 75(2), 230–244. https://doi.org/10.1016/S0034-4257(00)00169-3 | RSE 12.3 | Abstract (UNC CPC bibliography) |
| 36 | Wagner, T. J., & Kleiss, J. M. (2016). Error characteristics of ceilometer-based observations of cloud amount. *J. Atmos. Oceanic Technol.* 33(7), 1557–1567. https://doi.org/10.1175/JTECH-D-15-0258.1 | JTECH (confirm in JCR; context) | Abstract |
| 37 | Wilson, A. M., & Jetz, W. (2016). Remotely sensed high-resolution global cloud dynamics for predicting ecosystem and biodiversity distributions. *PLOS Biology* 14(3), e1002415. https://doi.org/10.1371/journal.pbio.1002415 | PLOS Biol (confirm in JCR) | Abstract + data page |
| 38 | Yeom, J.-M., Roujean, J.-L., Han, K.-S., Lee, K.-S., et al. (2020). Thin cloud detection over land using background surface reflectance based on the BRDF model applied to GOCI satellite data sets. *RSE* 239, 111610. https://doi.org/10.1016/j.rse.2019.111610 | RSE 12.3 | Abstract |
| 39 | Zhang, Q., & Xiao, C. (2014). Cloud detection of RGB color aerial photographs by progressive refinement scheme. *IEEE TGRS* 52(11), 7264–7275. https://doi.org/10.1109/TGRS.2014.2310240 | TGRS 9.4 | Abstract |
| 40 | Zhang, Y., & Guindon, B. (2003). Quantitative assessment of a haze suppression methodology for satellite imagery: Effect on land cover classification performance. *IEEE TGRS* 41(5), 1082–1089. https://doi.org/10.1109/TGRS.2003.811817 | TGRS 9.4 | Abstract |
| 41 | Zhang, Y., Guindon, B., & Cihlar, J. (2002). An image transform to characterize and compensate for spatial variations in thin cloud contamination of Landsat images. *RSE* 82(2–3), 173–187. https://doi.org/10.1016/S0034-4257(02)00034-2 | RSE 12.3 | Secondary (Fmask) + abstract fragment |
| 42 | Zhu, Z., & Woodcock, C. E. (2012). Object-based cloud and cloud shadow detection in Landsat imagery. *RSE* 118, 83–94. https://doi.org/10.1016/j.rse.2011.10.028 | RSE 12.3 | Passages (disk) |

**Context only (below 4 or unconfirmed, not for slides):** Byun, Y., & Han, D. (2018). Relative radiometric
normalization of bitemporal very high-resolution satellite images for flood change detection. *J. Appl. Remote Sens.*
12(2), 026021. https://doi.org/10.1117/1.JRS.12.026021 (abstract). Lv, H., Wang, Y., & Shen, Y. (2016). *RSE* 179,
183–195. https://doi.org/10.1016/j.rse.2016.03.034 (RSE 12.3, but only a search-snippet summary was seen, so no claims
are taken from it).

**Dataset DOI (DataCite, not Crossref):** Francis, A., Mrziglod, J., & Sidiropoulos, P. (2020). *Sentinel-2 Cloud Mask
Catalogue*. Zenodo. https://doi.org/10.5281/zenodo.4172871

**Agency web pages read:** GOES-R product definitions (https://www.goes-r.gov/products/baseline-clear-sky-mask.html);
AWS Open Data registry, NOAA GOES (https://registry.opendata.aws/noaa-goes/); EarthEnv cloud
(https://www.earthenv.org/cloud).

## For a GMU session (paywalled, most useful first)
1. Lv, Wang & Shen 2016, RSE: the radiative-transfer visible-band thin-cloud algorithm (gap 1/3a). Only metadata was
   seen.
2. Zhang, Guindon & Cihlar 2002, RSE: the HOT removal step on DNs (gap 1).
3. Makarau et al. 2014, TGRS: how "uncalibrated" data are handled (gap 3b).
4. Song et al. 2001, RSE: the relative-correction comparison in full (gap 3b).
5. Richards 2022, ch. 2 and 4, and Schowengerdt 2007: textbook guidance on haze correction (gap 2).
6. Chen et al. 2016 (IHOT), TGRS: the regression and iteration details (fix 6).
7. Zhang & Xiao 2014, TGRS: the "optimal threshold setting" and guided feathering (gaps 1 and 4).
