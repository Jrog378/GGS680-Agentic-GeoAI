# Reconstructing what cloud hides: literature for Justin's two-stage idea

**Request (Justin, 2026-10-23):** if the detected change is a cloud, scale the image and run it back through the change detector to find smaller changes (roads, houses). Find research on interpolating image areas that are blocked or cannot be seen.
**Compiled:** 2026-10-23 by Claude (AI research assistant), working alone. 37 searches or page reads; open pages only; no logins, no PDF downloads.
**Builds on:** `02_cloud_literature_summary.md`, `ProjectBranch/Literature/notes/clouds_review_web.md` and `clouds.md`. U-TILISE, TAMRF, Grich 2026, Hagolle 2010, Makarau 2014 and AnyTime-CD are covered there and only referred to here.
**Labels:**
- **Read depth:** *metadata*, *TLDR* (Semantic Scholar's machine summary, not the paper), *abstract* or *full text* (HTML).
- **Core:** a journal above JIF 4 in `journal_impact_factors.md` ("confirm in JCR" if not listed), or CVPR/ICCV/NeurIPS/ICLR/WACV. Anything else is a method attribution.
- **Voice:** "States" is what the source did; "My read" is my inference.

---

## 1. Summary

1. **Three of the five families are unavailable to us.** Spectral filling needs other bands, SAR fusion needs radar, and temporal filling of the *after* image needs a second post-event date. With one grey band and only the before date, what remains is spatial or generative filling, or filling from the before date.
2. **Filling from the before date assumes nothing changed, and here the change is the flood.**
   - Information cloning assumes land cover barely changes (Lin et al. 2013). Temporal methods do poorly under large land-cover change (Shen et al. 2019).
   - The methods that cope (Shen 2019; Liu, Huang & Cai 2023; You et al. 2026) add a near-date source to carry the change: auxiliary images, Sentinel-3 or SAR. We have none.
3. **0.5 m cloud removal exists, but only as single-image generation.** CUHK-CR (Jilin-1, 0.5 m, 4 bands) with DE (TGRS 2024) and GACR (ECCV 2026). Both see only the cloudy image, and DE's authors note that diffusion textures often fail to match the real scene. My read: under opaque cloud they can only invent.
4. **No paper found tests change, damage or flood mapping through reconstructed pixels.**
   - Evaluation is pixel fidelity (PSNR, SSIM, LPIPS, MAE) on held-out masks or near-date pairs, sometimes plus a downstream segmentation or classification task.
   - SpaceEye's flood example is qualitative only.
5. **Flags for filled pixels exist, but not in change products.**
   - UnCRtainTS predicts a variance per pixel and band. Discarding the most uncertain half of reconstructions almost halves the error.
   - NASA's cloud-gap-filled MODIS/VIIRS snow product records each pixel's age in days since its last clear view.
   - I found no change or flood product that marks filled pixels "not observed".
6. **Our two-date de-hazing is relative radiometric normalisation, not reconstruction.**
   - **Anchors:** IR-MAD normalisation on no-change pixels (Nielsen 2007; Canty & Nielsen 2008), PIF normalisation with quality control for change detection (Du et al. 2002), and Lin et al. (2015), which joins invariant-pixel normalisation and cloud detection (TLDR only).
   - **Same assumption, same limit:** Hagolle et al.'s multi-temporal aerosol method assumes the surface is stable, and it degrades when the landscape changes very quickly (2015 abstract). A flood is such a change.
7. **"Find the big change, remove it, look again" has partial precedents only.**
   - The closest are IR-MAD's re-weighting loop and Bruzzone & Bovolo's (2013) VHR framework. The framework models radiometric change types apart from changes of interest and uses multi-level object properties.
   - Nothing found detects cloud as change, corrects inside it, then re-detects small objects.
8. **The project's own result points to local correction.** On buildings (main project, development data), global IR-MAD gave no gain for DINOv3 (−0.004 AUC), local Wallis +0.036, and CLAHE helped in all four areas (`Project/docs/research/normalization.md`). My read: correct in local windows inside the cloud.

---

## 2. Q1. Missing-data reconstruction: the families

| Family | Needs | Fits 0.5 m grey, before + after only? | Usually evaluated by |
|---|---|---|---|
| Spatial (interpolation, inpainting) | The image itself | Runs, but invents content under cloud; anything fully hidden cannot be recovered (my read) | Synthetic masks on clear images |
| Spectral | Less-affected bands | No: one band | Simulated band loss |
| Temporal (other date, compositing, cloning, regression) | A clear date, ideally close; stable ground, or an extra near-date source | Only from the before date, which copies pre-flood ground | Masks on a clear target; PSNR, SSIM, CC |
| SAR-to-optical / SAR fusion | Co-registered SAR (mostly Sentinel-1, 10 m) and training pairs | No SAR | Real cloudy/clear pairs; a few downstream tasks |
| Generative (GAN, diffusion, flow) | Paired cloudy/clear training data | RGB/4-band 0.5 m exists (CUHK-CR); grey untested; invents under opaque cloud | PSNR, SSIM, LPIPS; a few downstream tasks |

**Anchors**
- **Shen et al. (2015).** Missing information reconstruction of remote sensing data: a technical review. *IEEE GRSM* 3(3):61–85. https://doi.org/10.1109/MGRS.2015.2441912
  - **Venue:** GRSM 13.7, core. **Read:** abstract. Needs GMU; an author PDF is on the WHU SENDIMAGE site (not opened).
  - **States:** it sorts algorithms into four main categories and compares them experimentally and theoretically. The category names were not verified in what I read.
- **Zhang et al. (2018).** STS-CNN. *IEEE TGRS*. https://doi.org/10.1109/TGRS.2018.2810208 ; arXiv 1802.08369
  - **Venue:** TGRS 9.4, core. **Read:** abstract.
  - **States:** one CNN takes spatial, spectral or temporal supplementary data and handles three tasks: MODIS band-6 dead lines, Landsat SLC-off stripes and thick cloud. Tested on simulated and real data.
  - **Fit:** for cloud it needs another date.

**Temporal**
- **Lin et al. (2013).** Information cloning. *IEEE TGRS*. https://doi.org/10.1109/TGRS.2012.2197682 (core; abstract; needs GMU). **States:** clones cloud-free patches from other dates via a Poisson equation, assuming land cover changes insignificantly over a short time. Landsat-7 ETM+, simulated clouds.
- **Sarukkai et al. (2020).** STGAN. WACV. https://doi.org/10.1109/WACV45572.2020.9093564 (core conference; abstract). **States:** a spatiotemporal GAN on 97,640 image pairs; improved downstream land-cover classification.
- U-TILISE, TAMRF and Grich: see `clouds.md` §3(c). U-TILISE sometimes misses abrupt changes inside a gap.

**SAR-to-optical and SAR fusion**
- **Meraner et al. (2020).** DSen2-CR. *ISPRS JPRS*. https://doi.org/10.1016/j.isprsjprs.2020.05.013 (12.9, core; open; abstract). **States:** a residual network fuses Sentinel-1 with Sentinel-2, with a cloud-adaptive loss that keeps the clear information; removes even thick cloud on real global pairs.
- **Ebel et al. (2020; 2022).** SEN12MS-CR and SEN12MS-CR-TS. *IEEE TGRS*. https://doi.org/10.1109/TGRS.2020.3024744 ; https://doi.org/10.1109/TGRS.2022.3146246
  - **Venue:** core; open. **Read:** abstracts.
  - **States:** global SAR plus cloudy and clear optical datasets (single date, then time series). Training on real clouds beat training on synthetic ones.
- **Zhao, Olsen & Chandra (2023).** Seeing through clouds (SpaceEye). *IEEE TGRS*. https://doi.org/10.1109/TGRS.2023.3239592
  - **Venue:** core. **Read:** full text (ar5iv).
  - **States:** Sentinel-1 plus 48-day Sentinel-2 sequences at 10 m. Scored only on held-out synthetic gaps; the authors say real ground truth does not exist. Limits: very cloudy scenes, and cloud-detector errors that spread.
- **Xu et al. (2024).** M3R-CR / Align-CR. *IEEE TGRS* 62. arXiv 2301.03432
  - **Venue:** core. **Read:** abstract.
  - **States:** high-resolution optical cloud removal guided by low-resolution SAR, with alignment for misregistration. Semantic meaningfulness is tested through segmentation.
- **Fuentes Reyes et al. (2019).** *Remote Sensing* 11:2067. https://doi.org/10.3390/rs11172067 (4.3, confirm in JCR; abstract). **States:** cGAN SAR-to-optical translation at high resolution (TerraSAR-X with ALOS PRISM), judged by SAR experts and by road extraction, with fundamental limits reported.

**Spatial and generative**
- **Czerkawski et al. (2022).** *Remote Sensing* 14:1342. https://doi.org/10.3390/rs14061342 (4.3, confirm in JCR; abstract). **States:** deep-image-prior inpainting with no training, tested on synthetic masks with exact truth and on real samples.
- **Arp et al. (2024).** VPint2. *ISPRS JPRS*. https://doi.org/10.1016/j.isprsjprs.2024.07.030 (core; open; abstract).
  - **States:** training-free interpolation. An older clear image gives the spatial structure, and current values spread in from clear pixels. Accuracy falls only slightly as the reference ages.
  - The authors back evaluating by transferring cloud masks onto clear images.
- **Sui et al. (2024).** Diffusion enhancement (DE), with the CUHK-CR benchmark. *IEEE TGRS*. https://doi.org/10.1109/TGRS.2024.3411671
  - **Venue:** core. **Read:** full text (arXiv HTML).
  - **States, data:** CUHK-CR is Jilin-1KF01B, pan-sharpened to 0.5 m, with blue, green, red and NIR. 668 thin-cloud and 559 thick-cloud images; cloudy and clear pairs 10–17 days apart.
  - **States, method:** the "reference prior" is the output of a pretrained cloud-removal network. Inference takes the single cloudy image.
  - **States, results:** best PSNR 26.18 (thin) and 24.35 (thick). Diffusion textures may not align with the actual scene.
  - **Not done:** no cross-sensor test.
- **Other diffusion models (abstracts):**
  - EMRDM, Liu et al. (2025), CVPR (core), https://doi.org/10.1109/CVPR52734.2025.01663 : a mean-reverting diffusion from cloudy to clear, single- or multi-date.
  - DiffCR, Zou et al. (2024), TGRS (core), https://doi.org/10.1109/TGRS.2024.3365806 : conditional diffusion, best on three benchmarks.
- **Wang et al. (2026).** GACR. ECCV 2026 (accepted per arXiv). arXiv 2607.02471
  - **Venue:** ECCV is top-tier but not on the brief's list; Justin's call. **Read:** full text (HTML, about 85%).
  - **States, data:** CUHK-CR-EXT (0.5 m, real cloud) plus synthetic clouds on ISPRS Potsdam and Vaihingen.
  - **States, method:** the model sees only the cloudy image. Downstream scoring uses frozen DINOv3 encoders on 12 tasks (classification, buildings, segmentation, height). **No change detection.**
  - **States, motivation:** earlier generative methods drift semantically under heavy occlusion.
- **Also seen** (abstracts; data or method attributions): RICE (arXiv 1901.00600), AllClear (NeurIPS 2024 Datasets and Benchmarks), UniTS (arXiv 2512.04461).

---

## 3. Q2. Can reconstructed pixels carry real change?

**Evidence that filling copies the reference date or misses change**
- **Lin et al. (2013).** No-change assumption stated (above).
- **Shen et al. (2019).** *IEEE JSTARS*. https://doi.org/10.1109/JSTARS.2019.2898348
  - **Venue:** 6.3, core. **Read:** abstract; needs GMU.
  - **States:** temporal methods suit only phenological change and do poorly with significant land-cover change. Two auxiliary near-date images capture the change.
- **Liu, Huang & Cai (2023).** *IEEE TGRS*. https://doi.org/10.1109/TGRS.2023.3236106
  - **Venue:** core. **Read:** abstract; needs GMU.
  - **States:** a near-target-date Sentinel-3 image supplies land-cover change under thick cloud. It helped most where change was distinctive and heterogeneous.
- **You et al. (2026).** Change-aware multi-temporal cloud removal. *Sci. China Inf. Sci.* https://doi.org/10.1007/s11432-025-4669-x
  - **Venue:** 8.1 per the input card; confirm in JCR. **Read:** TLDR only; needs GMU.
  - **TLDR:** uses SAR to detect change, so that it can choose which other dates to use.
- **Hagolle et al. (2015).** *Remote Sensing* 7:2668. https://doi.org/10.3390/rs70302668 (4.3, confirm in JCR; abstract). **States:** the multi-temporal aerosol method assumes stable surface reflectance and degrades when the landscape changes very quickly.
- **U-TILISE** misses abrupt changes (on disk; `clouds.md`).

**Evidence that filling carries change (only with an extra source)**
- SpaceEye says its reconstruction captured standing water on a cloudy day (Carnation, WA, 2020). This is visual only, with SAR in the input.
- My read: the change came from radar, not from the fill.

**Evidence of invention**
- DE and GACR, above.
- **Xu, Li & Shen (2026).** PhyVLM-CR. arXiv 2603.07074. Method attribution; abstract.
  - **States:** thin cloud is handled by physical inversion and thick cloud by a temporal reference. A VLM-derived "hallucination confidence map" gates between the two.

**Uncertainty and flags**
- **Ebel et al. (2023).** UnCRtainTS. CVPR Workshops. https://doi.org/10.1109/CVPRW59228.2023.00202
  - **Venue:** workshop, method attribution. **Read:** full text (ar5iv).
  - **States, method:** aleatoric variance per pixel and per band (13 bands), with Sentinel-1 as input and 3 dates. Calibration is measured by UCE. Ensembles add epistemic uncertainty.
  - **States, results:** discarding the most uncertain 50% of reconstructions almost halves error (Fig. 3).
  - **Not done:** no downstream task and no split by cloud thickness. Higher uncertainty is linked to persistent occlusion, shadow and changing crops.
- **Hall et al. (2019).** *Hydrol. Earth Syst. Sci.* 23:5227. https://doi.org/10.5194/hess-23-5227-2019
  - **Venue:** confirm in JCR. **Read:** full text.
  - **States, method:** cloudy pixels take the most recent clear value. A cloud-persistence count in the QA layer gives each observation's age, and users choose how old is acceptable.
  - **States, evaluation:** uncertainty is said to grow with age, but this is not measured.

**Answer**
- No source found runs change, damage or flood detection on reconstructed pixels.
- Temporal fillers copy the reference unless an extra near-date source carries the change. Single-image generators admit they invent texture.
- Per-pixel uncertainty (UnCRtainTS) and observation-age layers (MODIS CGF) are the published flags. No change product found labels filled pixels "not observed".

---

## 4. Q3. Separating large nuisance change from object change

- **Bruzzone & Bovolo (2013).** A novel framework for the design of change-detection systems for VHR images. *Proc. IEEE*. https://doi.org/10.1109/JPROC.2012.2197169
  - **Venue:** confirm in JCR; already cited in the project's research notes. **Read:** abstract; needs GMU.
  - **States:** a top-down design that models different radiometric changes explicitly, extracts their semantic meaning, picks out the changes of interest for the application, and uses multi-scale/multi-level object properties. Shown on a QuickBird pair over Trento.
  - My read: this is the theoretical home of "nuisance first, then objects".
- **Nielsen (2007).** IR-MAD. *IEEE TIP*. https://doi.org/10.1109/TIP.2006.888195 (13.7, 2024 value; abstract). **States:** MAD change is invariant to a separate gain/offset (affine) transform of each date; iterations up-weight pixels showing little change.
- **Canty & Nielsen (2008).** *RSE* 112(3):1025–1036. https://doi.org/10.1016/j.rse.2007.07.013 (12.3; in bib as `canty2008automatic`; abstract, DTU record).
  - **States:** re-weighting by no-change probability, then orthogonal regression; a substantial gain over the earlier method in scenes with much change.
  - **Project:** tested globally on 8-bit RGB with no gain (above).
- **Du, Teillet & Cihlar (2002).** *RSE*. https://doi.org/10.1016/S0034-4257(02)00029-9 (core; abstract, NRCan record; needs GMU). **States:** pseudo-invariant features chosen statistically, with PCA fits and quality control, for land-cover change detection.
- **Wu, Du & Zhang (2013).** Slow feature analysis. *IEEE TGRS*. https://doi.org/10.1109/TGRS.2013.2266673 (core; abstract). **States:** projects both dates onto the most time-invariant features, suppressing differences on unchanged pixels; includes an iterative variant.
- **Hierarchical and coarse-to-fine designs (abstracts):**
  - Liu et al. (2014), *IEEE TGRS* (core), https://doi.org/10.1109/TGRS.2014.2321277 : a hierarchy that separates change classes by spectral behaviour (hyperspectral).
  - Zhang, Peng & Huang (2017), *IEEE GRSL*, https://doi.org/10.1109/LGRS.2017.2763182 (confirm in JCR; abstract): multiscale object-based change detection run coarse to fine, on SPOT-5 and GF-1.
  - Han et al. (2024), C2F-SemiCD, *IEEE TGRS*, https://doi.org/10.1109/TGRS.2024.3370568 (core; abstract): a coarse-to-fine change network.
- **Already in the bib, not re-read:** `moghimi2021comparison` (JSTARS; keypoint-based relative normalisation).
- **Gap:** no two-pass design found that removes a detected cloud or haze change and then re-runs the detector for small objects.

---

## 5. Q4. Thin-cloud correction against a clear reference date

- **Lin et al. (2015).** Radiometric normalization and cloud detection of optical satellite images using invariant pixels. *ISPRS JPRS*. https://doi.org/10.1016/j.isprsjprs.2015.05.003
  - **Venue:** core. **Read:** TLDR only; ScienceDirect refused the page. Needs GMU.
  - **TLDR:** weighted PCA picks invariant pixels from a cloudy time series, then normalises the dates.
  - My read: this is the closest published match to our prototype. Read it first.
- **Hagolle et al. (2008).** Multi-temporal aerosol correction, Formosat-2. *RSE*. https://doi.org/10.1016/j.rse.2007.08.016
  - **Venue:** core. **Read:** metadata; needs GMU. The stable-surface assumption is stated in the open 2015 follow-up (Q2).
- **Zeng, Shen & Zhang (2013).** Multi-temporal regression for SLC-off gaps. *RSE*. https://doi.org/10.1016/j.rse.2012.12.012
  - **Venue:** core. **Read:** TLDR; needs GMU.
  - My read: a between-date regression fitted on valid pixels, the gap-filling cousin of our gain/offset fit.
- **Single-date physical models**, for contrast:
  - Zi et al. (2021), *IEEE JSTARS*, https://doi.org/10.1109/JSTARS.2021.3068166 (core; abstract): a thickness map per band, subtracted under an imaging model, trained on simulated thin cloud.
  - Makarau 2014 and He 2011 (prior notes).
- **Gap:** no published reference-date de-hazing for single-band VHR was found that fits only on unchanged pixels in local windows.

---

## 6. What this means for Justin's two-stage idea (My read)

**What "scale" can mean.** Radiometric: re-scale brightness and contrast inside the cloud (gain/offset), which is the de-hazing already prototyped. Spatial: look again at finer tiles. The literature supports the first well and the second only indirectly.

**Where filling in helps**
- **Thin haze.** The after image keeps its own signal. Use the before image only to estimate the cloud's gain and offset, never to supply content, so any flood found is the after image's own evidence.
- **Display.** A labelled-synthetic visual aid for people or for Gemma's description (CSI 709).

**Where it hides the change we want**
- **Opaque cloud, filled from the before date.** This paints the dry road back, so a flooded road becomes "no change". It follows from the no-change assumption (Lin 2013; Shen 2019).
- **Single-image generators.** DE and GACR invent plausible texture, which can produce false flood or false dry.
- **Spatial interpolation from clear neighbours.** It may extend a neighbouring flood into the gap. Plausible, but not observed.
- **A subtler trap.** If the gain/offset fit includes flooded pixels, it absorbs some of the flood's darkening as cloud effect. IR-MAD-style re-weighting exists to exclude changed pixels, and it was built for scenes with a lot of change (Canty & Nielsen 2008).

**How the literature evaluates it, and what we would add**
- The literature uses masks pasted onto clear images, near-date real pairs and occasionally frozen downstream models. Nobody scores change.
- We can paste real cloud shapes (HRC_WHU masks) and synthetic haze onto clear *after* tiles with known flooded roads. Then compare no correction, correction and fill-from-before, reporting flood recall on covered roads and the share of flooded roads turned "unchanged".
- This matches VPint2's mask-transfer evaluation and E3 in `clouds_review_web.md`. It would be new.

**The most promising designs**
1. **Correct, then re-detect, with an invariant-pixel loop.**
   - Pass 1 flags a large, smooth change region.
   - In windows inside it, fit after ≈ g·before + o with IR-MAD-style re-weighting, so flooded pixels drop out.
   - If the local before/after correlation is high (haze), invert and re-run DINO at road scale. If it is low (opaque), mark "not observed".
   - Abstain if a window has too few invariant pixels.
   - Sources: Canty & Nielsen 2008, Nielsen 2007, Du 2002, Lin 2015, Hagolle 2008/2015, Bruzzone & Bovolo 2013, and our local-beats-global result.
2. **A provenance layer that gates scoring.**
   - Each pixel is *observed*, *corrected* (with its fit residual), *filled* (with source date and age) or *not observed*.
   - Only observed and corrected pixels may vote "flooded".
   - Report risk–coverage.
   - Sources: UnCRtainTS, Hall et al. 2019, and WorldFloods v2's thin/bright split (prior note).
3. **Finer-scale re-detection inside corrected areas** (the spatial reading of "scale").
   - After correction, re-run DINO on finer, upsampled crops, where haze has lowered contrast.
   - The support is indirect (Bruzzone & Bovolo multi-level; coarse-to-fine networks). Test it on the simulated-haze set before trusting it.
- **Not recommended for scoring:** generative fills (DE, GACR, DiffCR) or fill-from-before.

---

## 7. For Justin's GMU session (paywalled, most useful first)

1. Lin et al. 2015, ISPRS JPRS. https://doi.org/10.1016/j.isprsjprs.2015.05.003 . The closest match to our prototype.
2. Hagolle et al. 2008, RSE. https://doi.org/10.1016/j.rse.2007.08.016 . The stable-surface assumption; check how it handles pixels that did change.
3. Bruzzone & Bovolo 2013, Proc. IEEE. https://doi.org/10.1109/JPROC.2012.2197169 . The nuisance-versus-change framework; confirm the JIF.
4. Shen et al. 2019, JSTARS. https://doi.org/10.1109/JSTARS.2019.2898348 . How temporal fillers fail under land-cover change.
5. You et al. 2026, Sci. China Inf. Sci. https://doi.org/10.1007/s11432-025-4669-x . Change-aware filling; read the abstract and method.
6. Shen et al. 2015, GRSM. https://doi.org/10.1109/MGRS.2015.2441912 . The four category names (an author PDF may be on the WHU SENDIMAGE site).
7. Lin et al. 2013, TGRS. https://doi.org/10.1109/TGRS.2012.2197682 .
8. Du, Teillet & Cihlar 2002, RSE. https://doi.org/10.1016/S0034-4257(02)00029-9 .
9. Liu, Huang & Cai 2023, TGRS. https://doi.org/10.1109/TGRS.2023.3236106 .
10. Zeng, Shen & Zhang 2013, RSE. https://doi.org/10.1016/j.rse.2012.12.012 .

**Open, not yet read in full:** STS-CNN (arXiv 1802.08369), SEN12MS-CR (arXiv 2009.07683), DSen2-CR and VPint2 (ScienceDirect), M3R-CR (arXiv 2301.03432), EMRDM (arXiv 2503.23717), Canty & Nielsen 2008 and Nielsen 2007 (DTU PDFs), Hagolle 2015 (MDPI).

**Already in the project:** `canty2008automatic`, `stucker2023utilise`, `grich2026evaluating` and `moghimi2021comparison` (bib); Bruzzone & Bovolo 2013 (research notes); `nielsen2007regularized` (brainstorming only, not in the bib). Nothing else above appears in the project's `.bib` or `.md` files.
