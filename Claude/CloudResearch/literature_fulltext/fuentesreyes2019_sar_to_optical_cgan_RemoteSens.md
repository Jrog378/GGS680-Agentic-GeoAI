# Coder handoff: Fuentes Reyes, Auer, Merkle, Henry & Schmitt (2019), SAR-to-Optical Image Translation with cGANs — Optimization, Opportunities and Limits

- **Citation:** Fuentes Reyes, M., Auer, S., Merkle, N., Henry, C., & Schmitt, M. (2019). SAR-to-Optical Image Translation Based on Conditional Generative Adversarial Networks—Optimization, Opportunities and Limits. *Remote Sensing* 11(17), 2067. https://doi.org/10.3390/rs11172067
- **PDF:** `/Users/jusrogers/Masters/papers/fuentesreyes2019_sar_to_optical_cgan_RemoteSens-summary.pdf` (page 1 = AI summary; paper pp. 1–19 follow)
- **Source:** MDPI open access (CC BY), fetched from the MDPI resource server https://mdpi-res.com/d_attachment/remotesensing/remotesensing-11-02067/article_deploy/remotesensing-11-02067.pdf (the www.mdpi.com/…/pdf link returned an "Access Denied" HTML stub to curl; that stub was not kept). Published version, pages "1 of 19" to "19 of 19".
- **Validation:** `file` = PDF 1.5, 14.5 MB; 19 pages (Read tool and pdfinfo agree); title, five authors (DLR Remote Sensing Technology Institute; TUM) and DOI match Crossref; Conclusions (§7, p. 16–17) and 37 references (pp. 17–19) present; 19 pages = article-number format, no page range to compare. PASS.
- **Read:** pp. 1–19 in full (text extraction; reference list skimmed). Figures 3–7 described from captions and text only.
- **Venue:** *Remote Sensing* (MDPI). Our notes give JIF 4.3, "confirm in JCR"; not confirmed here (no JCR access in this run).
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. What this paper is (and is not)
A SAR-interpretation paper, not a cloud-removal paper. A CycleGAN turns a single-channel TerraSAR-X image into an "optical-looking" panchromatic image so humans can read SAR more easily. No cloud, no haze, no gap filling, no multi-date data. The authors argue from the outset that full translation is impossible (p. 2): "we hypothesize that it is not possible to go the full path from SAR to actual optical data, and that the translation will always end up at a certain point in between." For us it is evidence about **how far generated pixels can be trusted** for road mapping and interpretation, and gives an **evaluation protocol**.

## 1. Algorithm (§4, pp. 4–7; §5.2, p. 9)
- Architecture: CycleGAN (Zhu et al. 2017), generator from Johnson et al. (downsample → residual blocks → upsample, Fig. 2), PatchGAN discriminator from pix2pix. Objective (eq. 2, p. 5):
  `L(G, F, D_X, D_Y) = L_GAN(G, D_Y, X, Y) + L_GAN(F, D_X, Y, X) + λ L_cyc(G, F)`, with cycle consistency F(G(x)) ≈ x and G(F(y)) ≈ y. G: SAR → optical, F: optical → SAR, D_X, D_Y the discriminators, λ the cycle weight (value not stated).
- Changes from default CycleGAN (pp. 6–7, 9):
  - **12 residual blocks** (default 9); 15 tested, "not significant changes", so stopped at 12 to avoid overfitting.
  - **1 input / 1 output channel** ("both domains are panchromatic, and additional colors can not be learned", p. 6).
  - **Xavier initialisation**; **learning rate 0.0005**; **80 epochs** (default 200).
  - **Unpaired training** (paired gave the same quality, p. 5 and p. 6; results shown are unpaired).
  - **Patches 512 × 512 with 50% overlap**; larger patches gave "more appealing" grey distributions; the whole image cannot be processed, and per-patch grey distributions give "significant" radiometric differences at patch borders (p. 6).
- SAR pre-processing (p. 7, p. 9): log scale, then clip the lower and upper **2%** of intensities to the min/max, normalise per image (all patches of one image together). The authors credit the log scaling with reducing "fiction" significantly and image-wide normalisation with removing "most of it" (p. 7).

## 2. Data (§5.1, pp. 8–9; Tables 1–2)
- Optical: ALOS PRISM, **2.5 m**, panchromatic. SAR: TerraSAR-X stripmap, **1.25 m**, "up-sampled to 2.5 m to match" (wording as in the paper; it is a resampling to the coarser grid).
- 46 image pairs, 13 European cities in 7 countries (Urban Atlas project), manual alignment, error **≈ 3 m**. **7,437** training patches, **1,005** test patches; split by file (train 9 cities, development London/Portsmouth, test Rzeszow, Stara Zagora, Wirral).
- Second test only: SEN1-2 (Sentinel-1 VV, 5 m × 20 m; Sentinel-2 RGB, < 1% cloud), applied without retraining.
- Compute: GTX Titan X / Titan X (12 GB); 10–15 days per training, 12 days for the reported model (p. 9).

## 3. Results we could compare to
**Visual (§5.3, pp. 9–12).** Speckle removed; main roads, their junctions and field blocks preserved. Failures:
- buildings "merged, others erased and a few more are generated because of the context, but do not represent a building in the real scene (fiction)" (p. 9); speckle read as small scatterers → "houses are hallucinated by the generator" (p. 10);
- dense urban areas blur ("content vanishing", p. 10); large buildings not recovered;
- grey-level inversion of large areas and water "could not be learned" (p. 10); adjacent crop-field boundaries lost;
- CycleGAN hides information in near-invisible high frequencies (steganography, citing Chu et al. 2017) and may lack robustness to noise (p. 12);
- SEN1-2 (no retraining): "big amount of fiction", urban elements where forest is expected (p. 12).
- Compared with DRIT (another GAN): DRIT more fiction in semi-urban/rural, less in dense urban. Compared with NL-SAR (classical non-local despeckling): keeps almost all structure, "has no freedom to create image content", but interpretability not necessarily better (p. 11).

**Expert judgement (§6.1, p. 13).** Protocol: 20 test samples; each shows original SAR, optical reference and the three outputs (CycleGAN, DRIT, NL-SAR) in **random positions**; question: which generated image gives a better understanding of the original SAR. Respondents grouped as SAR experts, optical experts, both. Result: CycleGAN 177 votes (55.45%), DRIT 86 (26.95%), NL-SAR 54 (16.92%), 2 undecided, "320 votes". CycleGAN first in all three groups; SAR experts put NL-SAR second. Experts preferred CycleGAN in weak-context scenes (rural, semi-urban, nature) and **NL-SAR in urban areas** where SAR structure is strong. No significance test.
- Inconsistencies in the paper: "a survey with 12 experts" but 20 samples × respondents = 320 votes implies 16 respondents, and the question was also put to "people outside the field of study"; the four counts sum to 319, not 320 (percentages match ≈ 319). Treat it as a small, informal preference poll.

**Road extraction (§6.2, pp. 13–14; Table 3).**
- Detector: DeepLabv3+, trained **separately on each image type** (original SAR, NL-SAR-filtered, CycleGAN-translated), 50 epochs, on the road set of Henry et al. 2018: two TerraSAR-X images of the Lincoln (England) countryside, **1 m/px**, train 16,384 × 12,288 px, test 4,096 × 12,288 px; labels = variable-thickness lines over highways, country roads and dirt paths.
- Metrics (eqs. 3–5): pixel IoU = Σyp / Σ(y + p − yp), precision = Σyp / Σp, recall = Σyp / Σy, with p = road probability thresholded at **0.5**.
- | Input | IoU | Precision | Recall |
  |---|---|---|---|
  | CycleGAN | 35.63% | 61.63% | 45.78% |
  | NL-SAR | 38.58% | 63.24% | 49.72% |
  | original SAR | **40.45%** | **65.08%** | **51.66%** |
- What broke roads (p. 14): differences come "from missing and superfluous segments, as well as connectivity issues at intersections"; "In CycleGAN images, shallow edges were visibly smoothed out or even erased during the SAR to optical style transfer"; "SAR imagery contains critical information that less sharp imagery does not preserve, as is the case with NL filtering and our method." Conclusion (p. 16): roads keep sharp edges "in most cases but the thicker ones sometimes vanish".
- Not stated: whether the CycleGAN (trained at 2.5 m) was retrained for the 1 m road images; no confidence intervals or tests; one test image.
- §6.3 (p. 15): best use was **overlaying roads detected on the original SAR onto the generated image** for human context, not detecting on the generated image. "Fiction is present in the CycleGAN scene but does not affect the expression of the scene topic."

## 4. Stated limitations (pp. 2, 10, 15–17)
- Ill-posed one-channel colourisation; different physics (wavelength, roughness, permittivity); different geometry: SAR range-dependent distortion and multiple-reflection signatures that "often do not correspond to physically existing structures" (p. 1); correcting them "requires prior knowledge about the geometry of scenes, e.g., based on digital surface models", which is "not available in the default SAR-to-optical translation task" (p. 2). (The word "layover" is not used.)
- Fiction (invented houses/roads) cannot be fully steered: "deep learning-based approaches are difficult to steer. This opens ways to alternative and creative data representations but also to fiction" (p. 4).
- Patch-border radiometric jumps; enlarging patches only moves them (p. 15).
- Over-smoothing; quality varies by land cover (good rural, poor dense urban) (p. 16).
- "There are currently no suitable metrics to evaluate the result in terms of interpretability" (p. 13).

## 5. How to apply to our pipeline
Nothing here is code to port. What carries over:
- **Rule: generated pixels must not be scored as observed pixels for roads or change.** A detector trained and tested on generated images lost 4.8 IoU points against the raw input, with errors at faint edges and junctions, and the generator invented buildings. This is direct support for `sn8_refhaze` / `sn8_cloudsym` **abstaining** where t < T_MIN (0.2) rather than filling under opaque cloud, and for keeping any generative filler (DE, GACR, etc. from evidence 05) out of the road-decision path.
- **Corrected-vs-uncorrected road test (template for `sn8_refhaze.corrected_table` / `road_handling`):** score the same road labels on (a) the raw after image, (b) the de-hazed after image, (c) any other processed version, with the same detector setup per arm; report IoU, precision and recall at a fixed 0.5 threshold, and inspect misses at **junctions** and **faint/narrow edges** specifically, the failure mode they found. Our metric convention adds paired tests (McNemar per road) which the paper lacks.
- **Smoothing kills faint roads:** the same mechanism applies to any smoothing in our correction (the guided filter, the 41 px box blur in `sn8_clouds.dark_channel`, the 20 m fade). When a correction arm smooths, check narrow/unpaved road recall separately from main roads.
- **Patch seams:** per-patch normalisation creates radiometric jumps at patch borders (p. 6, p. 15). If a correction or a DINOv2 feature step normalises per tile/crop, check road scores near tile edges.
- **Display, not decision:** their §6.3 overlay (detect on the observed image, show on the enhanced one) is the safe use of a pretty-but-invented image, e.g. for Gemma scene descriptions or slides, labelled as such.
- **Human-judgement protocol** (if we ever ask Justin or others to compare correction arms): randomise the position of the arms per sample, include the original and the reference, ask one fixed question, record respondent group, and report per-land-cover preferences. Use more than ~16 people or report it as qualitative.

## 6. Feasibility with our data
**The method itself does not apply.** It needs co-registered SAR (TerraSAR-X) and thousands of training patches; we have **no SAR**, no NIR and **no other dates** — only one clear pre-storm Maxar date and the post-storm date, RGB uint8 at 0.5 m used mostly as grey. Its resolution (2.5 m, with 1 m for the road test) is also 2–5× coarser than ours. What we can use is §3–§5 above: the road scoring setup, the observed failure modes (invented buildings, erased faint edges, junction breaks, wrong large-area grey levels, patch seams), and the conclusion that generated content helps context but hurts local feature extraction. A two-date analogue (before → after translation) would copy pre-flood ground, which is the change we must detect.

## 7. Key quotes
- "we hypothesize that it is not possible to go the full path from SAR to actual optical data, and that the translation will always end up at a certain point in between." (p. 2)
- "This might create elements such as houses, roads, forests, etc., in regions where these do not really exist, misleading the interpretation of the users." (p. 7)
- "In CycleGAN images, shallow edges were visibly smoothed out or even erased during the SAR to optical style transfer, making the road detection more challenging." (p. 14)
- "training on CycleGAN images does not increase the raw performance of a segmentation network" (p. 14)
- "Altogether, CycleGAN unfolds its advantages in the expression of context, not locally." (p. 16)
