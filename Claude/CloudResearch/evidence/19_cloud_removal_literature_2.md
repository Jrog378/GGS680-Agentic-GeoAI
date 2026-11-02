# 19: Cloud removal, validation against a near-date reference, and flood truth under cloud. Literature, round 2 (2026-10-29)

**Request (Justin, 2026-10-29):** "I think we need some additional research to be done".
**Context:** evidence 16 (SpaceNet 8 labels cannot score cloud removal: analysts "only attribute what was visible"),
evidence 17 (NOAA NGS aerial photos, USGS high-water marks, 3DEP lidar over our area) and
`outputs/preregistration_ida_clear_view.md` (the Ida test plan, written before any photo is compared).
**Compiled by:** Claude (AI research assistant), working alone. This is a literature note, not our own measurements.

**Method:**
- **Not repeated here:** evidence 02, 05 and 10 already cover HRC_WHU, WorldFloods, PU learning, Hagolle, Makarau,
  He 2011/2013, Fmask buffers, IR-MAD, Lin 2013/2015, Shen 2015/2019, DE/CUHK-CR, GACR, DiffCR, EMRDM, VPint2,
  UnCRtainTS and You 2026. Where one of these answers a question below, I cite the earlier note's reading and do not
  re-read it.
- **About 45 web searches and page reads, open pages only.** Full texts: AllClear (arXiv HTML), SEN12MS-CR (arXiv PDF,
  read as text), M3R-CR (ar5iv) and FwDET v2.0 (NHESS HTML). Abstracts: from OpenAlex, arXiv, the NOAA institutional
  repository, the USGS publications page and FAO AGRIS. Where I saw only a search engine's summary of an abstract, the
  read depth says "search summary".
- **References:** every DOI was checked against its Crossref record (`api.crossref.org/works/<doi>`) on 2026-10-29.
  Requests carried a generic user agent only, with no email or other identifier.
- **Blocked, not bypassed:** MDPI full text (403, so Tiampo 2022 is abstract-only), the CVF open-access PDF for
  Sen1Floods11 (403), DOAJ (403), mediaTUM (429, so the SEN12MS-CR licence and size are unverified), the USGS STN web app
  (it renders by script, so the Ida high-water-mark count is unverified), and the NOAA repository PDF (larger than the
  fetch limit). No logins and no downloads; only landing pages and file listings were opened.
- **Labels:** read depth is *full text*, *abstract*, *search summary*, *metadata* or *prior note* (read in evidence 02,
  05 or 10). Venue JIFs are from `Project/docs/literature/journal_impact_factors.md`; "confirm in JCR" means the journal is
  not in that file. CVPR, ICCV, ECCV, NeurIPS and ICLR qualify without a JIF, as do company-led papers. Anything else is
  a method or data **attribution**. "States" is what the source did; "My read" is my inference.

---

## In short

1. **Pixel metrics on real cloudy/clear pairs are not well-defined, and the field says so.** SEN12MS-CR (TGRS) used
   pixel metrics (MAE, RMSE, PSNR, SSIM, SAM) only on synthetic data, which guarantees "perfect co-registration" and no
   land-cover change. For real pairs it used precision and recall in a VGG16 feature space. This supports our choice of
   DINOv2 feature distance as the primary outcome, with grey error secondary.
2. **The strongest design to copy is M3R-CR's downstream test** (TGRS 2024). It trains a segmenter on cloud-free images,
   runs it on cloud-free, cloudy and reconstructed inputs, and states "the closer they are to the results with the
   cloud-free images as input, the better". For us: run our road-flood detector on the NOAA photo as the cloud-free input,
   and score each arm by how closely its road calls match those calls.
3. **Pixel scores and downstream scores can rank methods differently.** In AllClear (NeurIPS 2024), UnCRtainTS has a
   higher PSNR than the LeastCloudy baseline (29.009 vs 28.864) but a lower land-use Jaccard (0.479 vs 0.514). The paper
   does not discuss this, and no error bars are reported. So do not pick an arm by grey error.
4. **Our 0–2 day gap is tight by the literature's standards.** Real-pair benchmarks use 2.8 days on average (M3R-CR,
   PlanetScope 3 m), 10–17 days (CUHK-CR, 0.5 m) or "the same meteorological season" (SEN12MS-CR). AllClear credits its
   short input–target gap for the strength of simple baselines. Nobody pairs aerial photos with satellite images for
   cloud-removal scoring.
5. **NOAA aerial photos as reference: one peer-reviewed precedent, for SAR flood extent, not cloud removal.**
   - Tiampo et al. (2022, *Remote Sensing* 4.3, abstract) compared Sentinel-1 Harvey flood maps with NOAA Remote Sensing
     Division aerial photos at 35–50 cm. How the reference was derived is not in the abstract.
   - NOAA's own metadata warns that "clouds may be present in the imagery". The Harvey record says "No consistency tests
     conducted", and its positional-accuracy field is blank. Those two points come from a search summary of the metadata.
6. **Change-aware cloud removal still needs SAR or an extra near-date image.**
   - You et al. (2026) uses multi-temporal SAR, by its keywords; its abstract is not in OpenAlex.
   - Shen et al. (2019) needs two extra near-date images.
   - Ref-Diff (CVPR 2024) is change-aware but does super-resolution, not cloud removal: it uses land-cover change priors
     so that reference texture is trusted only in unchanged areas.
   - I found no method for one grey band plus a clear prior date that avoids copying the reference over real change. Our
     rule stays: take only the cloud's gain and offset from the before date, never content.
7. **Per-pixel confidence for thin cloud exists only as learned uncertainty.**
   - Ding et al. (TGRS 2024, abstract) sample several restorations from a conditional VAE and call it an "uncertainty
     pipeline".
   - UnCRtainTS (workshop) predicts a variance per pixel.
   - No physics-based thin-cloud method I found outputs calibrated per-pixel confidence. Our t ≥ 0.2 / CANNOT ASSESS
     split remains our own rule (evidence 10).
8. **A depth from water surface minus lidar is a known method, with known error of about 0.2–0.5 m.**
   - FwDET v2.0: 0.18 m mean absolute difference from a hydrodynamic model (1 m lidar, coastal).
   - Lidar water surface against high-water marks: RMSE 30 cm (Iowa 2008).
   - NWM-HAND against Harvey high-water marks: mean depth error about 0.5 m.
   - FwDET's authors name roofs, highways, overpasses and dikes as error sources, which matters for roads.
   - I found **no published work that uses a per-road depth from high-water marks minus lidar as a scored reference
     label**. The closest is a New Jersey road-inundation report, which is not peer-reviewed.
9. **Cloud and flooding go together, so a cloud-free-only evaluation samples the wrong floods.**
   - On average, Sentinel-2 could observe only 28% of European flood events because of cloud, against 58% for Sentinel-1
     (Tarpanelli et al. 2022, NHESS; search summary).
   - Sen1Floods11 codes "No Data / Not Valid" as −1, and AllClear computes metrics "only over the cloud-free areas".
   - I found **no paper that measures how much excluding cloud-covered pixels inflates flood-map scores**. Evidence 16 is
     our own measurement of that gap.

---

## Q1. Validating cloud removal against a near-date clear reference from another sensor

**Sources**
- **Ebel, Meraner, Schmitt & Zhu (2021). SEN12MS-CR.** *IEEE TGRS* 59:5866 (9.4, core). Full text (arXiv version).
  - **States, pairing:** Sentinel-2 L1C cloudy and cloud-free images and Sentinel-1, "acquired within the same
    meteorological season to limit surface changes".
  - **States, metrics on real pairs:** "improved precision and recall" in a "high-dimensional feature embedding space"
    (VGG16, second fully connected layer). The footnote says other pretrained networks gave "virtually identical
    results".
  - **States, pixel metrics:** used only on synthetic data, which guarantees "perfect co-registration, no atmospheric
    disturbances other than the simulated noise, control for no landcover and daylight changes … ensuring that
    pixel-wise metrics are well-defined".
  - **States, limits:** strict ground-truth correspondence "may only be guaranteed by simulating synthetic data". On
    real test data, models trained on real observations "consistently outperform" those trained on synthetic data.
- **Xu et al. (2024). M3R-CR / Align-CR.** *IEEE TGRS* 62 (core). Full text (ar5iv preprint).
  - **States, data:** PlanetScope 3 m cloudy/clear pairs, on average 2.8 days apart; Sentinel-1 on average 2.2 days
    from the cloudy image.
  - **States, alignment:** pixel-level alignment is "very hard to achieve" because of resolution and imaging
    differences. Align-CR learns the alignment implicitly with deformable convolution.
  - **States, metrics:** MAE, PSNR, SAM and SSIM per land-cover class, and NDVI RMSE.
  - **States, downstream test:** DeepLabv3+ is trained on cloud-free images with WorldCover labels, then run on
    cloud-free, cloudy and predicted images. mIoU and pixel accuracy are reported; closer to the cloud-free result is
    better.
- **Zhou et al. (2024). AllClear.** NeurIPS 37, Datasets and Benchmarks (core). Full text (arXiv HTML).
  - **States, data:** 23,742 regions. Sentinel-2 is the target; Sentinel-1 and Landsat 8/9 are auxiliary, matched
    within two days. Everything is resampled to 10 m UTM; images with NaNs are dropped. There is no explicit cross-sensor
    co-registration step.
  - **States, metrics:** MAE, RMSE, PSNR, SAM and SSIM, computed "only over the cloud-free areas" of targets with less
    than 10% cloud. No LPIPS.
  - **States, downstream:** a 9-class land-use UNet; Jaccard 0.698 on ground truth, 0.479 UnCRtainTS, 0.514 LeastCloudy,
    0.604 for the AllClear-trained model. No error bars.
  - **States, date gap:** SEN12MS-CR-TS targets can be "as large as a year" from the input. AllClear credits the "small
    temporal gap" for the strength of the simple baselines (untested).
- **Sui et al. (2024). DE and CUHK-CR.** *IEEE TGRS* 62 (core). Prior note (evidence 05, full text).
  - 0.5 m Jilin-1 pairs, 10–17 days apart, scored with PSNR, SSIM and LPIPS. The authors note that diffusion textures
    may not match the real scene.
- **Wang et al. (2026). GACR.** ECCV 2026 (core per the brief's list; the earlier note left it for Justin to decide).
  Prior note (evidence 05). Downstream scoring with frozen DINOv3 encoders on 12 tasks; no change detection.
- **Tiampo et al. (2022).** *Remote Sensing* 14:2261 (4.3, narrow). Abstract (NOAA repository record).
  - **States:** Sentinel-1 Harvey flood maps (amplitude thresholding and DeepLabv3+) were compared with "high-resolution
    aerial optical images over this time period, acquired by the NOAA Remote Sensing Division", and with Sentinel-2
    NDWI.
  - **Search summary of the full text:** the photos were 35–50 cm, flown at 2,500–5,000 ft with a Trimble DSS.
  - **Not seen:** co-registration, date gap and how the reference was derived.
- **Scheffler et al. (2017). AROSICS.** *Remote Sensing* 9:676 (4.3, narrow; already in the bib as
  `scheffler2017arosics`). Abstract (OpenAlex).
  - **States:** phase-correlation sub-pixel co-registration, inter- and intra-sensor, on a moving-window grid of shift
    vectors.
  - It can mask clouds and shadows out of shift detection, and is described as robust to high cloud cover and to
    land-cover change. RMSE was "around 0.3 pixels or better".
- **Weir et al. (2019). SpaceNet MVOI.** ICCV (core; Maxar/CosmiQ co-authors). Abstract.
  - **States:** 27 looks of one area, −32.5° to 54°. Changing the view angle "adds distortions, alters resolution, and
    changes lighting", and models "generalize poorly to unseen views".
  - Disaster first looks are often more than 40° off nadir.
- **Feature metrics (attributions for metric choice):**
  - LPIPS (Zhang et al. 2018, CVPR; metadata): similarity from deep-network features.
  - DreamSim (Fu et al. 2023, NeurIPS; abstract): trained on human judgements. It "outperforms both prior learned
    metrics and recent large vision models" and weights semantic content and layout over low-level colour and texture.
- **Attribution only:** Brill et al. (2021, DLR poster; abstract) validated Harvey satellite flood masks with a 50 cm
  aerial image. Satellite emergency products "hardly avoid underdetection" in urban and vegetated areas.

**Answers**
- **Co-registration:**
  - Benchmarks either resample to one grid and accept residual error (AllClear, SEN12MS-CR) or learn the alignment
    (Align-CR).
  - AROSICS is the established open tool for local, multi-sensor, cloud-masked shift estimation.
  - I found nothing on aligning aerial orthophotos to off-nadir VHR satellite images for cloud-removal scoring.
- **Tone and radiometry:**
  - The benchmarks do almost nothing beyond clipping and normalising one sensor's reflectance (AllClear).
  - Cross-sensor tone matching is not addressed in any cloud-removal benchmark I found. Our per-tile monotone tone curve
    on clear pixels is our own step. Evidence 10 says to fit it on invariant pixels.
- **Date gap:** handled by choosing near-date pairs (2.8 days, 10–17 days, same season) and by excluding cloudy target
  pixels. No paper measures the error from the gap itself.
- **View angle and parallax:**
  - M3R-CR names imaging differences as the cause of misalignment.
  - MVOI shows that off-nadir views change appearance and hurt models.
  - No cloud-removal benchmark corrects for building lean.
- **Metrics:**
  - Pixel metrics: PSNR, SSIM, SAM, MAE, RMSE.
  - Perceptual: LPIPS (DE).
  - Feature distribution: VGG precision/recall (SEN12MS-CR); frozen DINOv3 downstream tasks (GACR).
  - Downstream tasks: segmentation mIoU (M3R-CR, AllClear).
  - I found no paper using a per-pixel DINO or CLIP feature *distance* to a reference as the score.
- **NOAA NGS as ground truth:** only Tiampo 2022, for SAR flood extent (abstract), plus a DLR poster with an unnamed
  50 cm aerial image. I found none for cloud removal.
  - The Goldstein et al. (2021) labels on NOAA photos (Florence, Michael, Isaias) are image-level, not pixel-level.
    Their venue, *Earth and Space Science*, has a JIF of 3.3, so they are a data attribution only.

**What this means for us (My read).**
- Our plan's choices are each supported separately: feature distance as primary, tile as the unit, clear ground as the
  guard.
- But no paper has done exactly this, so we should report it as a new evaluation design, not as replicating a standard.
- Two additions would bring it closer to precedent:
  1. M3R-CR's downstream comparison: run our detector on the NOAA image and score each arm against those calls.
  2. A measured noise floor. The guard plays that role, and a NOAA-vs-NOAA comparison where two flights overlap would
     add the date-gap part.
- The off-nadir geometry of a WorldView "first look" against a near-vertical aerial frame will make buildings and trees
  disagree even on clear ground. Road strips, which lie on the ground, are the fairer region to score.

---

## Q2. State of the art 2024–2026 for cloud and thin-haze removal on very-high-resolution optical images

| Method (venue) | Input | Change-aware? | Fits one grey band + clear before date? | Read |
|---|---|---|---|---|
| DE + CUHK-CR (TGRS 2024) | Single cloudy RGB+NIR 0.5 m image; "reference prior" is a pretrained network's output | No | No (single-image generator; 4 bands) | prior note, full text |
| EMRDM (CVPR 2025) | Cloudy image, single- or multi-date | Not stated | Single-date mode could run on one band only after retraining (untested) | prior note, abstract. A search summary of its table gives the best PSNR on CUHK-CR (27.28 thin, 24.59 thick) |
| DiffCR (TGRS 2024) | Conditional diffusion on cloudy image | No | Retraining needed | prior note, abstract |
| GACR (ECCV 2026) | Single cloudy image | No; motivated by "semantic drift" | No | prior note, full text |
| Ding et al. cVAE (TGRS 2024) | Single hazy/thin-cloud image; several samples fused | No | Single-image; bands not stated in abstract | abstract |
| You et al. (Sci. China Inf. Sci. 2026) | Multi-temporal SAR + optical (keywords) | **Yes** | No (needs SAR) | metadata (no abstract in OpenAlex) |
| Shen et al. (JSTARS 2019) | Reference + two auxiliary near-date images | **Yes** | No (needs extra near-date images) | prior note, abstract |
| Ref-Diff (CVPR 2024) | Low-res current + high-res reference (super-resolution, not cloud) | **Yes**: change priors guide denoising | Idea transfers; method is not cloud removal | abstract |
| VPint2 (ISPRS 2024) | Cloudy image + older clear image, training-free | No (structure from the reference) | **Runs on one band**, but copies reference structure | prior note, abstract |
| PhyVLM-CR (arXiv 2026) | Physics for thin cloud, temporal reference for thick, VLM "hallucination confidence map" | Partly | No (VLM, multispectral) | attribution; prior note, abstract |
| Prithvi cloud-gap imputation (Godwin et al. 2024) | HLS multispectral time series | No | No | attribution; venue unverified (search summary) |
| SADER (arXiv 2026) | Multi-temporal diffusion | Not addressed | No | attribution; abstract |

**Sources:** Sui et al. 2024; Liu et al. 2025 (EMRDM); Zou et al. 2024 (DiffCR); Wang et al. 2026 (GACR); Ding et al.
2024; You et al. 2026; Shen et al. 2019; Dong et al. 2024 (Ref-Diff); Arp et al. 2024 (VPint2).

**What this means for us (My read).**
- The 2024–2026 leaders are single-image diffusion models trained on 4-band 0.5 m pairs (CUHK-CR). They invent texture
  under opaque cloud (DE's own caveat; GACR's motivation).
- The only change-aware cloud removers need SAR or extra near-date images, and we have neither.
- Nothing published fits "one grey band plus a clear before date" and is change-aware. Our two-date de-hazing, which
  takes only the cloud's gain and offset from the before date, remains the defensible design.
- Ref-Diff's idea (trust the reference only where a change prior says "unchanged") is the closest published logic to our
  guard. It is cited as a top-venue precedent for the principle, not as a method we use.
- Any diffusion arm would be research-only. It would also need RGB+NIR training data and our grey band, an untested
  domain shift.

---

## Q3. Thin cloud and haze, not thick cloud

**Sources**
- **He, Sun & Tang (2011; 2013).** *IEEE TPAMI* (18.6, 2024 value; Microsoft Research). Prior note (evidence 10, full
  text).
  - Halos come from assuming the transmission is constant within a patch. The fix is soft matting, later the guided
    filter.
  - t is bounded below at t0 = 0.1 because the restored image "is prone to noise" where t is small.
- **Makarau et al. (2014).** *IEEE TGRS* 52:5895 (9.4; DLR). Prior notes (abstract). Local dark-object haze-thickness
  map, tested on WorldView-2; fails on uniform, bright land cover.
- **Ding et al. (2024).** *IEEE TGRS* 62 (9.4). Abstract (OpenAlex).
  - **States:** deterministic restoration is "highly ill-posed". A conditional VAE generates multiple restorations
    ("uncertainty pipeline"), and a dynamic fusion network combines them. It outperforms prior methods "by a significant
    margin" on dehazing and thin-cloud benchmarks.
  - Data and bands are not in the abstract.
- **Ebel et al. (2023). UnCRtainTS.** CVPR Workshops (attribution). Prior note: per-pixel variance; discarding the most
  uncertain 50% almost halves error.
- **Pasquarella et al. (2023). Cloud Score+.** CVPRW (Google-led, company). Prior note: a continuous per-pixel quality
  score for Sentinel-2, so the user sets the threshold.
- **Portalés-Julià et al. (2023). WorldFloods v2.** *Sci. Rep.* 13:20316 (4.9). Prior note: separate clear/cloud and
  land/water masks, so water can be called under thin cloud; bright opaque cloud is excluded.
- **Zhu, Wang & Woodcock (2015). Fmask.** *RSE* (12.3). Prior note: pixels around clouds are masked because "the thin
  edges of clouds" still affect them.
- **Attributions found this round (not read beyond search snippets):**
  - Guided-Pix2Pix (JSTARS 2021) jointly refines a transmission map and reports fewer edge halos.
  - PM-CycleGAN (GRSL 2022) decomposes into a clear image plus a thickness map, trained on unpaired data.

**Answers**
- **Physics-based vs learned:**
  - Physics-based methods (dark channel, local dark-object subtraction) give an explicit thickness or transmission map
    per pixel, which is a natural gate.
  - Learned methods (cVAE, diffusion) give better benchmark scores on RGB, but no thickness map unless built in
    (PM-CycleGAN).
- **Halos and rings:** handled by edge-aware refinement of the transmission map (guided filter, matting, learned
  refinement) and by buffering cloud edges (Fmask). See evidence 10 for the ranked fixes.
- **Per-pixel confidence and abstention:**
  - Learned: sampled restorations (Ding), predicted variance (UnCRtainTS).
  - Operational: continuous quality scores (Cloud Score+) and separate visibility masks (WorldFloods v2).
  - I found no thin-cloud method that outputs a calibrated per-pixel "cannot assess".

**What this means for us (My read).**
- Our t map already gives a physics-based per-pixel confidence. The Ida test (outcome 4) is the first place it can be
  checked against independent truth: does low t mark the ground we failed to recover?
- If it does, that is a small, reportable result the literature lacks.
- Ding's sampling idea suggests a cheap check: the spread of the de-hazed value across a few plausible gate settings
  (for example t0, the window and the fade) as an uncertainty map. This is untested.

---

## Q4. Flood mapping under cloud with non-image geospatial data

**Sources**
- **Cohen et al. (2018). FwDET v1.** *JAWRA* 54:847 (confirm in JCR). Search summary of the abstract.
  - Depth is estimated from an inundation map and a DEM alone, and checked against hydraulic-model depth for a large
    event (10 m DEM) and a small one (1 m lidar).
  - Bias appears where the mapped extent does not fit the terrain; urban areas are among the difficult cases.
- **Cohen et al. (2019). FwDET v2.0.** *NHESS* 19:2053 (confirm in JCR). Full text.
  - **States, method:** the water surface for each flooded cell is the DEM elevation of its nearest flood-boundary cell.
    Coastal boundary cells at or below zero are dropped.
  - **States, validation:** against calibrated hydrodynamic models ("assumed here to be the true water depth"), not
    high-water marks. Mean absolute difference 0.18 m (coastal, 1 m lidar) and 0.31 m (riverine, 10 m DEM). Mean
    difference −0.16 m in both.
  - **States, limits:** roofs make "non-flooded islands"; highways, overpasses and dikes cause large overestimates. For
    operational events, "there are insufficient ground-based observations to make a quantitative accuracy
    determination".
- **Peter et al. (2022). FwDET-GEE.** *IEEE GRSL* 19 (confirm in JCR). Search summary of the abstract. A GEE port,
  validated for comparability with FwDET v2.0.
- **Zheng, D'Angelo, Maidment & Passalacqua (2022).** NWM-HAND / GeoFlood applied to Hurricane Harvey. *JAWRA* 58:149
  (confirm in JCR). Abstract (OpenAlex).
  - **States:** validated against high-water marks and observed extents. Mean depth error about 0.5 m; extent covers
    more than 90% of the high-water-mark-derived inundation.
  - Calibrated roughness and lidar reduce the depth error but change the extent less.
- **Johnson et al. (2019).** NWM-HAND evaluation. *NHESS* 19:2405 (confirm in JCR). Search summary.
  - Compared with 28 remotely sensed inundation maps. It underpredicts in low-order reaches.
  - It should be used "with caution" for deciding whether a cell is wet or dry.
- **Chen, Krajewski, Goska & Young (2017).** *J. Hydrology* 553:338 (confirm in JCR). Abstract.
  - Lidar flown during the 2008 Iowa flood: water points classified, a water surface built, the bare-earth DTM
    subtracted.
  - Water-surface RMSE against high-water marks is 30 cm. Extent agrees with SPOT at 72% (81% after removing isolated
    ponds).
- **Gebrehiwot & Hashemi-Beni (2021).** *ISPRS IJGI* 10:144 (confirm in JCR). Abstract.
  - UAV deep-learning flood polygons plus a pre-flood lidar DEM (Hurricane Matthew, Princeville NC).
  - Depth RMSE against USGS gauge levels: 0.26 m (DEM method), 0.34 m (SfM).
- **Li, Xu & Weng (2025). TerrainFloodSense.** *Int. J. Appl. Earth Obs. Geoinf.* 144:104855 (8.2, core). Abstract.
  - Bayesian fusion of DSM, HAND and historical water occurrence fills cloud gaps in optical water maps.
  - Overall accuracy +2.95 to +8.86 points and F1 +0.038 to +0.087 over existing methods, on simulated experiments and
    large flood cases. The reference data are not named in the abstract.
- **Attributions (not peer-reviewed or not read):**
  - A Rutgers/NOAA Digital Coast report estimates roadway inundation extent and depth from lidar road-surface
    elevations (New Jersey). It notes that ground-level estimates are unreliable for elevated roads and bridges.
  - A USGS Port Neches product built a flood-elevation surface from high-water marks and peak stage, then subtracted
    lidar.
  - FEMA's Harvey depth grid used lidar plus high-water marks from HCFCD and USGS.
  - All of these are from search summaries.

**Answers**
- **DEM and water-level methods:**
  - FwDET takes the water surface from the flood edge.
  - HAND/NWM takes it from forecast stage over a drainage-relative DEM.
  - High-water-mark or lidar-surface methods interpolate observed levels.
  - Accuracy is checked against hydrodynamic models (FwDET), high-water marks (Zheng; Chen) or gauges (Gebrehiwot).
  - Reported depth errors run from about 0.2 to 0.5 m. The extent is reliable mainly on open floodplains; urban
    structures and elevated roads are named failure cases.
- **Fusion with SAR:** FwDET, Kundu et al. 2022 (search summary only) and Tiampo 2022 take extents from SAR. That is not
  an option for us without SAR.
- **Per-road depth as a reference label:** I found no peer-reviewed paper that scores a road-level flood product against
  "interpolated water surface minus lidar road elevation". The ingredients are published and validated, at 0.2–0.5 m
  error. Using them as a road label would be our own construction.

**What this means for us (My read).**
- A high-water-mark surface minus 3DEP road elevation is a defensible *physical* reference, but only with a margin.
- A road should count as flooded only if the computed depth clearly exceeds the method's error (for example above
  0.5 m), dry only if clearly below zero, and "uncertain" in between.
- Roads on embankments, overpasses and bridges should be flagged, because FwDET's authors name exactly these structures
  as error sources. Check whether the 3DEP DEM is bare-earth at those structures.
- High-water marks record the *peak*. The satellite and NOAA passes come 1–4 days after landfall, when water may have
  receded. So a depth label says "was flooded at peak", not "is flooded in this image". This mismatch must be stated.
- This stays Justin's decision under the "published labels, unmodified" rule.

---

## Q5. Evaluation pitfalls: label bias under cloud

**Sources**
- **Hänsch et al. (2022). SpaceNet 8.** CVPRW (Maxar co-authors). Prior note (evidence 08, full text). Annotators
  "were instructed to only attribute what was visible".
- **Bonafilia et al. (2020). Sen1Floods11.** CVPRW (Cloud to Street, company). The README (opened) gives the label values
  "-1: No Data / Not Valid", "0: Not Water", "1: Water". How clouds are coded is not stated on the README.
  - A NeurIPS 2022 slide deck (attribution) says the −1 class covers cloud-obscured pixels. It attributes weak results on
    cloudy scenes partly to these missing labels.
- **Zhou et al. (2024). AllClear.** As above: metrics "only over the cloud-free areas".
- **Portalés-Julià et al. (2023). WorldFloods v2.** Prior note: scoring leaves out invalid pixels and bright opaque cloud;
  scenes with much thin cloud go to human review.
- **Tarpanelli, Mondini & Camici (2022).** *NHESS* 22:2473 (confirm in JCR). Search summary of the abstract.
  - 10 years of discharge at about 2,000 European sites. On average, 58% of flood events are potentially observable by
    Sentinel-1 and 28% by Sentinel-2, "due to the cloud coverage".
- **Olofsson et al. (2014).** *RSE* 148:42 (12.3). On disk (evidence 02). Accuracy and area estimates need a probability
  sample of reference units; a convenience sample, such as only visible pixels, does not give unbiased accuracy.
- **Li, Guo & Elkan (2011), PU learning.** *IEEE TGRS* (core). Prior note (evidence 02).

**Answers**
- **How papers handle it:**
  - They exclude the obscured pixels from the scoring (Sen1Floods11 −1, AllClear, WorldFloods v2).
  - They send cloudy scenes to human review (WorldFloods v2).
  - In training, they treat missing labels as unlabelled rather than negative (PU learning).
- **How papers measure it:** I found no paper that measures the bias. Tarpanelli shows the precondition: the floods that
  optical sensors miss are not a random subset, because cloud and flooding coincide.

**What this means for us (My read).**
- Evidence 16 is a direct measurement of this bias on SpaceNet 8: 27 marked-flooded roads under cloud, against up to
  about 132 expected at the clear-road rate. The literature lacks such a measurement, so it is worth reporting as a
  finding in its own right.
- In the Ida test, the NOAA photo can *show* how many of the 230 cloudy roads look flooded. That is visual evidence of
  the label gap, but not a label. Turning it into a label needs Justin's decision.

---

## What to change in our Ida test plan

These are proposals for `outputs/preregistration_ida_clear_view.md`. They are written here, not edited into the plan, and
are to be decided before any photo is compared.

1. **Add a downstream outcome copied from M3R-CR.** Run the frozen production road detector on the tone-matched NOAA
   grey image as the "cloud-free input". Then score each arm (as is, He 2011, two-date, two-date + spotter) by agreement
   of its per-road calls with those calls on cloudy roads, and against the same agreement on clear roads as the ceiling.
   (Xu et al. 2024: "closer … to the results with the cloud-free images as input, the better"; AllClear runs the same
   kind of downstream test.) This makes outcome 6 a call-level test, not only a Spearman correlation of cues.
2. **Keep feature distance primary and say why.** Pixel metrics are well-defined only with perfect co-registration and
   no change (SEN12MS-CR). Report grey error as secondary, and do not choose an arm on it: pixel and downstream rankings
   disagree in AllClear.
3. **Measure a date-gap noise floor.** Where two NOAA flights (for example 30 Aug and 2 Sep) cover the same tile,
   compute NOAA-vs-NOAA feature distance on clear ground. Report it beside the satellite-vs-NOAA clear guard. No
   benchmark measures its gap error (AllClear, CUHK-CR, M3R-CR), and ours varies by flight.
4. **Use local, cloud-masked co-registration and report the residual.** Replace or check "one shift per tile" against a
   moving-window shift grid of the AROSICS kind (Scheffler et al. 2017; about 0.3 px on its tests), with cloud masked
   out of the shift search. Report the per-tile residual shift. Drop tiles whose local shifts disagree, as now.
5. **Score road strips first and treat off-ground pixels separately.** Building lean and tree tops differ between an
   off-nadir satellite first look and an aerial frame (Weir et al. 2019). Make road strips the primary region for
   outcomes 1–3. Report building and tree pixels apart, or mask them with OSM footprints. Record the satellite off-nadir
   angle from the Maxar metadata.
6. **Mask NOAA's own cloud before fitting the tone curve.** NOAA metadata warns that clouds may be present. AllClear
   excludes cloudy target pixels. The plan already does this (item 6); also exclude those pixels from the tone-curve fit
   and from alignment.
7. **Fit the tone curve on invariant pixels only.** Exclude pixels whose local before–after correlation is low (likely
   flood change) from the fit, in the spirit of IR-MAD and PIF normalisation (evidence 10: Canty & Nielsen 2008; Du et al.
   2002). Otherwise flood darkening is absorbed into the tone map.
8. **If Justin approves the depth label, pre-register a margin and a structure flag.** Count a road as flooded only if
   the water surface minus 3DEP road elevation is above about 0.5 m, and dry only if below 0. Everything else is
   uncertain. Flag bridges, overpasses and embankments. This margin follows the reported depth errors of 0.18–0.5 m
   (Cohen et al. 2019; Chen et al. 2017; Zheng et al. 2022) and FwDET's named failure cases. State that high-water marks
   record the peak, not the pass date. Confirm that the 3DEP project used was flown before Ida.
9. **Report the label-gap count as a finding.** Count the cloudy roads that look flooded in NOAA photos against the 27
   marked. Report it as descriptive evidence of visible-only labelling (Hänsch et al. 2022; Tarpanelli et al. 2022), not
   as a score.
10. **Optional uncertainty check (Ding et al. 2024 idea).** Compute the spread of the two-date output across a small,
    pre-fixed set of gate settings. Test whether high spread predicts high distance to NOAA, alongside outcome 4 (t as
    the gate).

---

## Datasets found

Justin's rule (2026-10-29): document only datasets whose files I have *tested* to be fetchable, without downloading
them. Each test is either an anonymous bucket or API listing showing real files and sizes, or an HTTP HEAD on one real
data file returning 200 with a Content-Length. All tests ran on 2026-10-29 with `curl`; no data body was fetched. Datasets
already documented in evidence 02 (HRC_WHU, CloudSEN12, WorldFloods, Sen1Floods11 and others) are not repeated.

| Name | Paper | Contents | Labels / truth and how made | Download test (URL · method · status · size) | Licence (as stated) | Size | What we could compare or replicate | How it might help us | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **NOAA NGS Emergency Response Imagery, Hurricane Ida 2021** | Program data; Tiampo et al. 2022 used the Harvey collection the same way | Aerial RGB GeoTIFF tiles. Prefixes for 8 flights (20210830a/b, 20210831a/b, 20210901a/b, 20210902a/b) plus `downloads/` | None: a reference image, not a label. NOAA metadata warns clouds may be present | `https://noaa-eri-pds.s3.amazonaws.com/?list-type=2&prefix=2021_Hurricane_Ida/` · anonymous S3 ListObjectsV2 · 200, files listed with sizes. HEAD `.../2021_Hurricane_Ida/20210830a_RGB/20210830aC0895915w295145n.tif` · 200 · Content-Length 28,432,249 | "open to the public and can be used as desired" (NOAA NODD, AWS registry page) | About 26 GB over our area (evidence 17) | Tiampo's Harvey comparison (abstract only; no numbers seen). Our pipeline runs on it after RGB→grey and resampling | The clear-view reference under cloud: the core of the Ida test | **High** |
| **USGS 3DEP 1 m DEM** (LA_CoastalLouisiana_2020; LA_2021GreaterNewOrleans) | Used in Zheng et al. 2022 and Chen et al. 2017-type depth methods | Bare-earth lidar DEM, 1 m GeoTIFF tiles | Lidar survey | TNM API `https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Digital Elevation Model (DEM) 1 meter&bbox=-90.03,29.62,-89.93,29.75` · GET (metadata JSON) · 16 products. HEAD `https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/LA_CoastalLouisiana_2020_D20/TIFF/USGS_1M_15_x78y329_LA_CoastalLouisiana_2020_D20.tif` · 200 · Content-Length 323,139,068 | US public domain (USGS; licence page not opened) | About 5–10 GB over our area (evidence 17) | FwDET-style depth (Cohen et al. 2019: 0.18 m against a model at 1 m) | Road elevation for a depth reference; flag elevated roads | **High**. Confirm whether the 2021 Greater New Orleans project was flown before Ida |
| **CUHK-CR** (CUHK-CR1 thin, CUHK-CR2 thick) | Sui et al. 2024, TGRS | Jilin-1KF01B pan-sharpened 0.5 m, RGB + NIR as separate files; 668 thin and 559 thick-cloud images; cloudy/clear pairs 10–17 days apart (evidence 05) | Real cloudy and near-date clear pairs; no human labels | `https://huggingface.co/api/models/littlebeen/DE/tree/main` · HF API listing · 200: `C-CUHK.rar` 1,458,346,878 B, `pretrain-DE.rar` 273,106,311 B. HEAD `https://huggingface.co/littlebeen/DE/resolve/main/C-CUHK.rar` (follow redirect) · 302 → 200 · Content-Length 1,458,346,878. Not gated (no login) | **Not stated** on the GitHub repo or HF page: treat as research-only until clarified | 1.46 GB data (+ 273 MB weights) | DE: PSNR 26.18 (thin) / 24.35 (thick) (evidence 05); EMRDM 27.28 / 24.59 (search summary). Our two-date de-hazer can run: the near-date clear image plays the reference date, and RGB is converted to grey | The only real 0.5 m thin-cloud pair set: test the de-hazer, the t gate and the CANNOT ASSESS split against a real clear reference outside Ida | **High** (licence unknown) |
| **AllClear** | Zhou et al. 2024, NeurIPS D&B | Sentinel-2 L1C + Sentinel-1 + Landsat 8/9, 10 m; 23,742 regions | Real near-date clear targets (<10% cloud); land-use labels for the downstream test | HEAD `https://allclear.cs.cornell.edu/dataset/allclear_test_proi1_v1.zip` · 200 · Content-Length 24,077,107,758. HEAD `.../s2p_tx3_test_3k_1proi_v1.json` · 200 · 3,028,617. No registration | **CC BY-NC 4.0** (non-commercial) | Test set about 24 GB; full size not stated | Pixel metrics and downstream Jaccard (0.698 on ground truth); not runnable for us (10 m multispectral) | Evaluation design only (cloud-free-only metrics, downstream check) | Low |
| SpaceNet 4 / MVOI (off-nadir) | Weir et al. 2019, ICCV | WorldView-2 Atlanta, 27 looks from −32.5° to 54°; PAN, MS and pan-sharpened tiles | 126,747 human building footprints | `https://spacenet-dataset.s3.amazonaws.com/?list-type=2&prefix=spacenet/SN4_buildings/tarballs/` · anonymous S3 listing · 200, per-look tarballs about 7.0–7.5 GB each. HEAD `.../SN4_buildings_AOI_6_Atlanta_test_public.tar.gz` · 200 · Content-Length 6,240,703,533 | "Various" on the AWS registry; the SpaceNet licence page was not opened (unverified) | About 7 GB per look; 27 looks | Building detection against off-nadir angle. Our DINOv2 features run on pan/grey | Measure how much the view angle alone moves DINOv2 features on unchanged ground: a parallax noise floor for the NOAA comparison (plan change 5) | Med |
| Labels for NOAA ERI (Florence, Michael, Isaias) | Goldstein et al. 2021, *Earth Space Sci.* (3.3; data attribution) | CSV labels for about 1,600 NOAA aerial images | Image-level labels (all water, damage, washover, development) by trained coastal scientists; inter-rater agreement measured | `https://zenodo.org/api/records/5172799` · Zenodo files API · 200: `ReleaseData_v3.csv` 618,200 B, `ReleaseDataNCE.csv` 40,733 B, `ReleaseDataQuads.csv` 38,567 B. HEAD `.../files/ReleaseData_v3.csv/content` · 200 · 618,200 | **CC BY 4.0** | 697.5 kB | Inter-rater agreement; image-level only, other events | Precedent and template if we ever label Ida NOAA photos for flooding | Low–Med |

**Not tested / not openly downloadable**
- **SEN12MS-CR / SEN12MS-CR-TS** (Ebel et al.): the landing page `mediatum.ub.tum.de/1554803` returned 429 (rate
  limit). A request to the dataserv share with the public credentials printed on the project page returned 401. No file
  was reached, and the licence is unverified.
- **M3R-CR / Planet-CR** (Xu et al. 2024): the repository `github.com/zhu-xlab/Planet-CR` gives a data loader and sample
  CSVs but no download link. PlanetScope terms likely apply.
- **USGS STN high-water marks, Ida 2021 (Louisiana):** the old STN service redirects (301) to `apps.usgs.gov/stnweb`, a
  script-rendered app, so no file was reached. The USGS New Jersey Ida release (CC0, 139 marks) was seen only as a
  landing page, and it is outside our area.
- **Harvey high-water marks used by Zheng et al. 2022:** not located or tested.
- **SECOND / CNAM-CD as repackaged by Ref-Diff:** Google Drive and Baidu links only (Baidu needs a password). Not tested
  by script, and no licence is stated.
- **TerrainFloodSense:** code on GitHub per the abstract; no dataset release located.

---

## References (DOIs checked against Crossref, 2026-10-29)

| # | Citation | Venue / rule | Read depth |
|---|---|---|---|
| 1 | Arp, L., et al. (2024). Training-free thick cloud removal for Sentinel-2 imagery using value propagation interpolation. *ISPRS J. Photogramm. Remote Sens.* 216, 168–184. https://doi.org/10.1016/j.isprsjprs.2024.07.030 | ISPRS 12.9 | Prior note (abstract) |
| 2 | Bonafilia, D., Tellman, B., Anderson, T., & Issenberg, E. (2020). Sen1Floods11. *CVPRW 2020*. https://github.com/cloudtostreet/Sen1Floods11 | CVPRW; Cloud to Street (company) | README only (CVF PDF 403) |
| 3 | Brill, F., Schlaffer, S., Martinis, S., Schröter, K., & Kreibich, H. (2021). Re-learning observed flood extents can improve remote sensing products. Poster, Natural Hazards and Risks in a Changing World, Potsdam. https://elib.dlr.de/144729/ | Poster: attribution | Abstract |
| 4 | Chen, B., Krajewski, W. F., Goska, R., & Young, N. (2017). Using LiDAR surveys to document floods: A case study of the 2008 Iowa flood. *J. Hydrology* 553, 338–349. https://doi.org/10.1016/j.jhydrol.2017.08.009 | Confirm in JCR | Abstract |
| 5 | Cohen, S., Brakenridge, G. R., Kettner, A., et al. (2018). Estimating floodwater depths from flood inundation maps and topography. *JAWRA* 54(4), 847–858. https://doi.org/10.1111/1752-1688.12609 | Confirm in JCR | Search summary of abstract |
| 6 | Cohen, S., Raney, A., Munasinghe, D., et al. (2019). The Floodwater Depth Estimation Tool (FwDET v2.0) for improved remote sensing analysis of coastal flooding. *NHESS* 19, 2053–2065. https://doi.org/10.5194/nhess-19-2053-2019 | Confirm in JCR | Full text |
| 7 | Ding, H., Xie, F., Qiu, L., Zhang, X., & Shi, Z. (2024). Robust haze and thin cloud removal via conditional variational autoencoders. *IEEE TGRS* 62, 1–16. https://doi.org/10.1109/TGRS.2024.3349779 | TGRS 9.4 | Abstract |
| 8 | Dong, R., Yuan, S., Luo, B., et al. (2024). Building bridges across spatial and temporal resolutions: Reference-based super-resolution via change priors and conditional diffusion model. *CVPR 2024*, 27674–27684. https://doi.org/10.1109/CVPR52733.2024.02614 | CVPR | Abstract |
| 9 | Ebel, P., Meraner, A., Schmitt, M., & Zhu, X. X. (2021). Multisensor data fusion for cloud removal in global and all-season Sentinel-2 imagery. *IEEE TGRS* 59(7), 5866–5878. https://doi.org/10.1109/TGRS.2020.3024744 | TGRS 9.4 | Full text (arXiv 2009.07683 version) |
| 10 | Ebel, P., et al. (2023). UnCRtainTS. *CVPRW 2023*, 2086–2096. https://doi.org/10.1109/CVPRW59228.2023.00202 | Workshop: attribution | Prior note (full text) |
| 11 | Fu, S., Tamir, N., Sundaram, S., et al. (2023). DreamSim: Learning new dimensions of human visual similarity using synthetic data. *NeurIPS 36*, 50742–50768. https://doi.org/10.52202/075280-2208 | NeurIPS | Abstract |
| 12 | Gebrehiwot, A. A., & Hashemi-Beni, L. (2021). Three-dimensional inundation mapping using UAV image segmentation and digital surface model. *ISPRS Int. J. Geo-Inf.* 10(3), 144. https://doi.org/10.3390/ijgi10030144 | Confirm in JCR | Abstract |
| 13 | Goldstein, E. B., et al. (2021). Labeling poststorm coastal imagery for machine learning: Measurement of interrater agreement. *Earth and Space Science* 8. https://doi.org/10.1029/2021EA001896 ; data https://zenodo.org/records/5172799 | ESS 3.3: data attribution | Metadata + Zenodo page |
| 14 | Hänsch, R., et al. (2022). SpaceNet 8 – The detection of flooded roads and buildings. *CVPRW 2022*, 1471–1479. https://doi.org/10.1109/CVPRW56347.2022.00153 | CVPRW; Maxar co-authors | Prior note (full text) |
| 15 | He, K., Sun, J., & Tang, X. (2011). Single image haze removal using dark channel prior. *IEEE TPAMI* 33(12), 2341–2353. https://doi.org/10.1109/TPAMI.2010.168 | TPAMI 18.6 (2024); Microsoft Research | Prior note (full text) |
| 16 | Johnson, J. M., Munasinghe, D., Eyelade, D., & Cohen, S. (2019). An integrated evaluation of the National Water Model (NWM)–Height Above Nearest Drainage (HAND) flood mapping methodology. *NHESS* 19, 2405–2420. https://doi.org/10.5194/nhess-19-2405-2019 | Confirm in JCR | Search summary of abstract |
| 17 | Li, Z., Xu, S., & Weng, Q. (2025). TerrainFloodSense: Improving seamless flood mapping with cloudy satellite imagery via water occurrence and terrain. *Int. J. Appl. Earth Obs. Geoinf.* 144, 104855. https://doi.org/10.1016/j.jag.2025.104855 | JAG 8.2 | Abstract |
| 18 | Liu, Y., et al. (2025). Effective cloud removal for remote sensing images by an improved mean-reverting denoising model with elucidated design space (EMRDM). *CVPR 2025*, 17851–17861. https://doi.org/10.1109/CVPR52734.2025.01663 | CVPR | Prior note (abstract); PSNR from a search summary |
| 19 | Makarau, A., Richter, R., Müller, R., & Reinartz, P. (2014). Haze detection and removal in remotely sensed multispectral imagery. *IEEE TGRS* 52(9), 5895–5905. https://doi.org/10.1109/TGRS.2013.2293662 | TGRS 9.4; DLR | Prior note (abstract) |
| 20 | Olofsson, P., Foody, G. M., Herold, M., et al. (2014). Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment* 148, 42–57. https://doi.org/10.1016/j.rse.2014.02.015 | RSE 12.3 | Prior note (on disk) |
| 21 | Pasquarella, V. J., Brown, C. F., Czerwinski, W., & Rucklidge, W. J. (2023). Comprehensive quality assessment of optical satellite imagery using weakly supervised video learning (Cloud Score+). *CVPRW 2023*, 2125–2135. https://doi.org/10.1109/CVPRW59228.2023.00206 | Google-led (company) | Prior note (abstract) |
| 22 | Peter, B. G., Cohen, S., Lucey, R., et al. (2022). Google Earth Engine implementation of the Floodwater Depth Estimation Tool (FwDET-GEE) for rapid and large scale flood analysis. *IEEE GRSL* 19, 1–5. https://doi.org/10.1109/LGRS.2020.3031190 | Confirm in JCR | Search summary of abstract |
| 23 | Portalés-Julià, E., Mateo-García, G., Purcell, C., & Gómez-Chova, L. (2023). Global flood extent segmentation in optical satellite images. *Scientific Reports* 13, 20316. https://doi.org/10.1038/s41598-023-47595-7 | Sci. Rep. 4.9 | Prior note (abstract) |
| 24 | Scheffler, D., Hollstein, A., Diedrich, H., Segl, K., & Hostert, P. (2017). AROSICS: An automated and robust open-source image co-registration software for multi-sensor satellite data. *Remote Sensing* 9(7), 676. https://doi.org/10.3390/rs9070676 | Remote Sensing 4.3 (narrow) | Abstract |
| 25 | Shen, H., et al. (2019). [Cloud removal with land-cover change, two auxiliary images]. *IEEE JSTARS* 12(3). https://doi.org/10.1109/JSTARS.2019.2898348 | JSTARS 6.3 | Prior note (abstract) |
| 26 | Sui, J., et al. (2024). Diffusion enhancement for cloud removal in ultra-resolution remote sensing imagery. *IEEE TGRS* 62, 1–14. https://doi.org/10.1109/TGRS.2024.3411671 | TGRS 9.4 | Prior note (full text) |
| 27 | Tarpanelli, A., Mondini, A. C., & Camici, S. (2022). Effectiveness of Sentinel-1 and Sentinel-2 for flood detection assessment in Europe. *NHESS* 22, 2473–2489. https://doi.org/10.5194/nhess-22-2473-2022 | Confirm in JCR | Search summary of abstract |
| 28 | Tiampo, K. F., Huang, L., Simmons, C., Woods, C., & Glasscoe, M. T. (2022). Detection of flood extent using Sentinel-1A/B synthetic aperture radar: An application for Hurricane Harvey, Houston, TX. *Remote Sensing* 14(9), 2261. https://doi.org/10.3390/rs14092261 | Remote Sensing 4.3 (narrow) | Abstract (NOAA repository record); MDPI 403 |
| 29 | Wang et al. (2026; author list as in evidence 05, not re-checked). GACR. *ECCV 2026* (accepted per arXiv). arXiv 2607.02471 | ECCV | Prior note (full text, about 85%) |
| 30 | Weir, N., Lindenbaum, D., Bastidas, A., et al. (2019). SpaceNet MVOI: A multi-view overhead imagery dataset. *ICCV 2019*. https://doi.org/10.1109/ICCV.2019.00108 | ICCV; CosmiQ/Maxar | Abstract |
| 31 | Xu, F., Shi, Y., Ebel, P., et al. (2024). Multimodal and multiresolution data fusion for high-resolution cloud removal: A novel baseline and benchmark (M3R-CR). *IEEE TGRS* 62, 1–15. https://doi.org/10.1109/TGRS.2023.3337845 | TGRS 9.4 | Full text (ar5iv preprint) |
| 32 | You, G., Xu, F., Pan, J., Dong, R., Yang, W., & Xia, G.-S. (2026). Change-aware multi-temporal cloud removal. *Sci. China Inf. Sci.* 69(3). https://doi.org/10.1007/s11432-025-4669-x | 8.1 (year unverified) | Metadata + keywords (no abstract) |
| 33 | Zhang, R., Isola, P., Efros, A. A., Shechtman, E., & Wang, O. (2018). The unreasonable effectiveness of deep features as a perceptual metric (LPIPS). *CVPR 2018*, 586–595. https://doi.org/10.1109/CVPR.2018.00068 | CVPR; Adobe co-authors | Metadata |
| 34 | Zheng, X., D'Angelo, C., Maidment, D. R., & Passalacqua, P. (2022). Application of a large-scale terrain-analysis-based flood mapping system to Hurricane Harvey. *JAWRA* 58(2), 149–163. https://doi.org/10.1111/1752-1688.12987 | Confirm in JCR | Abstract (OpenAlex) |
| 35 | Zhou, H., et al. (2024). AllClear: A comprehensive dataset and benchmark for cloud removal in satellite imagery. *NeurIPS 37* (Datasets and Benchmarks), 53571–53597. https://doi.org/10.52202/079017-1696 | NeurIPS D&B | Full text (arXiv HTML) |
| 36 | Zhu, Z., Wang, S., & Woodcock, C. E. (2015). Improvement and expansion of the Fmask algorithm. *RSE* 159, 269–277. https://doi.org/10.1016/j.rse.2014.12.014 | RSE 12.3 | Prior note (full text) |
| 37 | Zou, X., et al. (2024). DiffCR: A fast conditional diffusion framework for cloud removal from optical satellite images. *IEEE TGRS* 62, 1–14. https://doi.org/10.1109/TGRS.2024.3365806 | TGRS 9.4 | Prior note (abstract) |

**Agency and program sources (operational practice, not peer-reviewed):**
- NOAA Open Data Dissemination, NOAA ERI registry: https://registry.opendata.aws/noaa-eri/
- NOAA NGS ERI metadata (Isaias; Harvey): https://www.fisheries.noaa.gov/inport/item/62679 ;
  https://storms.ngs.noaa.gov/storms/harvey/download/metadata.html (search summaries)
- USGS NJ Ida high-water marks:
  https://www.usgs.gov/data/high-water-marks-new-jersey-following-hurricane-ida-and-associated-floods-september-2021
- USGS STN Flood Event Viewer: https://apps.usgs.gov/stnweb (not readable by script)
- Rutgers / NOAA Digital Coast, roadway flood estimates (NJ): https://coast.noaa.gov/digitalcoast/stories/flood-estimates.html
  (search summary)

**Needs GMU login (most useful first):** Tiampo et al. 2022 (MDPI blocked, but open access; how the NOAA reference was
derived), Zheng et al. 2022 (how high-water marks became a depth surface), You et al. 2026 (the change-aware method),
Ding et al. 2024 (data and bands), Chen et al. 2017.
