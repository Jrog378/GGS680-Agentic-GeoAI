# Claim checks, batch B: evidence 19 vs full text

Compiled by Claude (AI research assistant), 2026-10-29. Each row compares what
`evidence/19_cloud_removal_literature_2.md` says about a paper with the paper's full text.
Evidence 19 itself is not edited. Status: **verified** (full text says it), **corrected** (full text says
something different; correction given), **not found** (could not locate in the full text; pages searched given).

## Xu et al. 2024, M3R-CR (TGRS 62), full text pp. 1–15 (arXiv v2)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| PlanetScope 3 m cloudy/clear pairs on average 2.8 days apart; S1 on average 2.2 days from the cloudy image | verified | p. 5 |
| Pixel-level alignment "very hard to achieve" because of resolution and imaging differences | verified, with context | p. 6. The alignment discussed is **SAR-to-optical**, not cloudy-to-clear optical; the optical pair is only orthorectified and treated as aligned (p. 4–5) |
| Align-CR learns alignment implicitly with deformable convolution | verified | p. 6–7 (PCD deformable conv) |
| Metrics: MAE, PSNR, SAM, SSIM per land-cover class, and NDVI RMSE | corrected (minor) | Only MAE and SAM are split by class; PSNR and SSIM are overall (Table II, p. 8–9). NDVI RMSE **and** NDVI-class mIoU (Table IV, p. 12) |
| DeepLabv3+ trained on cloud-free images with WorldCover labels, run on cloud-free, cloudy, predicted; mIoU and PA; closer to cloud-free is better | verified | p. 10–11, Table III, quote p. 11 |
| (In short #2 / plan change 1) "score each arm by how closely its road calls match those calls" framed as copying M3R-CR | corrected (nuance) | M3R-CR scores every input against **WorldCover labels** and compares the scores (Fig. 6 = mIoU difference); it does not measure direct agreement with the cloud-free-input predictions. Our agreement metric is an adaptation |
| Not in evidence 19, worth adding | new | Rank flips inside M3R-CR itself (SAR-Opt-cGAN; Align-CR vs w/o Align at 80–100 % cloud), p. 11: same lesson as AllClear, from a TGRS paper |

## Ebel et al. 2021, SEN12MS-CR (TGRS 59), full text pp. 1–13 (arXiv v1, accepted manuscript)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| S2 L1C cloudy and cloud-free + S1, "acquired within the same meteorological season to limit surface changes" | verified | p. 5 |
| Real pairs scored by "improved precision and recall" in a VGG16 feature space (2nd FC layer) | verified, with nuance | p. 6, p. 9–10 (App. B). It is a **set-level k-NN manifold metric** (k = 10), not a per-pair feature distance. Evidence 19 "In short #1" says it "supports our choice of DINOv2 feature distance": supports feature space over pixels, but is not a precedent for a paired distance |
| Footnote: other pretrained networks gave "virtually identical results" | corrected (attribution) | p. 10: the footnote cites this to [28] (Kynkäänniemi et al.), not to tests in this paper |
| Pixel metrics only on synthetic data, quote "perfect co-registration … pixel-wise metrics are well-defined" | verified | p. 7; Table IV p. 8 (real data gets only precision/recall/F1) |
| Strict correspondence "may only be guaranteed by simulating synthetic data" | verified | p. 10 (App. D) |
| Real-trained models "consistently outperform" synthetic-trained on real test data | verified | p. 10 (Conclusion) |
| Reference list: authors/venue/DOI/pages 5866–5878 | verified | Crossref + first page |

## Zhou et al. 2024, AllClear (NeurIPS 37 D&B), full text pp. 1–27 (arXiv v1)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| 23,742 regions; S2 target, S1 and Landsat 8/9 auxiliary matched within two days | verified | p. 1, p. 5 ("within a two-day difference") |
| Everything resampled to 10 m UTM; images with NaNs dropped; no explicit cross-sensor co-registration | verified | p. 4; no co-registration step described anywhere (searched pp. 1–27) |
| Metrics MAE, RMSE, PSNR, SAM, SSIM "only over the cloud-free areas" of targets with < 10 % cloud; no LPIPS | verified | p. 5 (cloud **and shadow** < 10 %) |
| Downstream 9-class land-use UNet; Jaccard 0.698 GT, 0.479 UnCRtainTS, 0.514 LeastCloudy, 0.604 AllClear-trained | verified, location added | Appendix C.2, Table 11, p. 19 (not in the main text). Labels are Dynamic World (model-made), not human |
| UnCRtainTS PSNR 29.009 vs LeastCloudy 28.864 | verified | Table 2, p. 6 |
| Paper does not discuss the rank flip; no error bars | verified | Not discussed (pp. 5–6, 19); checklist "(c) Did you report error bars … [No]", p. 27 |
| SEN12MS-CR-TS targets "as large as a year" from the input | verified | p. 3 |
| AllClear credits "small temporal gap" for simple baselines (untested) | verified | p. 5, "we conjecture" |
| Licence CC BY-NC 4.0 (datasets table) | verified | pp. 25–26 |

## Scheffler et al. 2017, AROSICS (Remote Sensing 9, 676), full text pp. 1–21 (publisher version)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| Phase-correlation sub-pixel co-registration, inter- and intra-sensor, moving-window grid of shift vectors | verified | pp. 1, 3–8 |
| Can mask clouds and shadows out of shift detection | verified | pp. 1, 5, 10 |
| Robust to high cloud cover and land-cover change | partly verified | Cloud: tested (INTER1, ~50 % thick cloud, no mask; p. 11). Land-cover change: asserted from cited literature (p. 3), not tested as such |
| RMSE "around 0.3 pixels or better" | verified, caveat added | pp. 1, 15–17: 0.30, 0.15, 0.32 px; these are **internal residuals re-detected by AROSICS**, not independent check points, at 2.75–30 m resolution |
| Plan change 4: "about 0.3 px on its tests" as a standard for our alignment | corrected (scope) | Never tested below 2.75 m or with off-nadir parallax; affine model; "deviations from the affine model … decrease registration accuracy" (p. 17) |
| Venue "Remote Sensing 4.3 (narrow)" | not checkable in paper | JIF not in full text |

## Dong et al. 2024, Ref-Diff (CVPR 2024), full text PDF pp. 1–11 (CVF open access)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| Change-aware, does super-resolution, not cloud removal | verified | pp. 1–4 |
| Uses land-cover change priors so that reference texture is trusted only in unchanged areas | verified, nuance | pp. 1, 4. The gate is soft (learned SFT modulation combining mask and features), multi-class, and **ground-truth masks** are used for training and the headline results (p. 4) |
| (Q2 table) "change priors guide denoising"; "idea transfers" | verified | p. 4 |
| Not in evidence 19 | new | With predicted change masks, Ref-Diff's LPIPS on CNAM-CD is worse than the HSR-Diff baseline (Tables 1 and 3, pp. 6–7), contrary to the text's "still outperforms" (p. 7). Missed changes copy false reference texture (p. 8) |
| Datasets SECOND / CNAM-CD, no licence stated, Google Drive/Baidu links | not checked here | Paper gives only the GitHub URL |

## Ebel et al. 2023, UnCRtainTS (CVPRW 2023), full text PDF pp. 1–11 (CVF open access)
| Evidence 19 / prior-note claim | Status | Full text |
|---|---|---|
| Workshop paper (attribution) | verified | CVPR 2023 Workshops (EarthVision), p. 1 |
| Predicts a variance per pixel | verified | per pixel **and per band** (diagonal covariance), pp. 3–4 |
| Discarding the most uncertain 50 % almost halves error | verified, nuance | Fig. 3, p. 6; the ranking/discarding is of **whole images**, not pixels |
| AllClear note: UnCRtainTS trained only on < 50 % cloud inputs | not in this paper | AllClear attributes it to Ebel et al. 2023; this paper does not state a cloud threshold (searched pp. 1–8) |
| Not in evidence 19 | new | Uncertainty also flags real transients between dates (waves, crops), p. 7; calibration metric UCE with 20 bins, p. 5 |

## Sui et al. 2024, DE + CUHK-CR (TGRS 62), full text pp. 1–13 (arXiv v1, pre-review)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| 0.5 m Jilin-1 pairs, 10–17 days apart | verified | Table III, p. 4 (10, 17, 10 days; Hangzhou clear image is 10 days **before** the cloudy one) |
| Scored with PSNR, SSIM, LPIPS | verified | p. 6 |
| Authors note diffusion textures may not match the real scene | verified | "often fail to precisely align with the actual scene", p. 5; "fake textures", p. 2 |
| Single cloudy RGB+NIR image; "reference prior" is a pretrained network's output | verified | pp. 5–6, Eq. 11–13 |
| DE PSNR 26.18 thin / 24.35 thick | verified (v1) | Table V, p. 7 (DE-MemoryNet). Published version not checked (paywalled) |
| 668 thin / 559 thick images | verified | p. 3–4 |
| Dataset row: "the near-date clear image plays the reference date" for our two-date de-hazer | **corrected (method flaw)** | Using the clear target as both reference and truth is circular; CUHK-CR has one clear image per site. Valid only for single-date arms, the t gate and the clear-ground guard |
| Not in evidence 19 | new | No co-registration between cloudy and clear images described; split is random within 3 scenes (spatial leakage risk); licence not stated |

## Cohen et al. 2019, FwDET v2.0 (NHESS 19), full text pp. 2053–2065 (publisher PDF)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| Water surface per flooded cell = DEM elevation of nearest flood-boundary cell; coastal boundary cells ≤ 0 dropped | verified | pp. 2054–2055 (also cells **adjacent** to ≤ 0 are dropped) |
| Validated against calibrated hydrodynamic models, "assumed here to be the true water depth", not high-water marks | verified | p. 2056 (the coastal model itself was checked against 18 USGS HWMs, RMSE 9.73 cm) |
| MAD 0.18 m (coastal, 1 m lidar) and 0.31 m (riverine, 10 m DEM); mean diff −0.16 m both | verified | pp. 2057, 2059 |
| (In short #8 / plan change 8) 0.18 m used as the method's known error for a depth margin | **corrected (scope)** | The 0.18/0.31 m figures use a flood extent **derived from the model itself** (p. 2056), i.e. a perfect extent. With image-derived extents no accuracy figure exists ("insufficient ground-based observations", p. 2059) and maxima reached 41.7 m |
| Roofs make "non-flooded islands" | corrected (quote) | Paper's words: "non-flooded areas within the flooded domain" and "false elevation reflections of sometimes multistory building roofs" (p. 2057); "islands" is not the paper's term |
| Highways, overpasses and dikes cause large overestimates | verified | "highways, overpasses, dikes … considerable overestimations", p. 2057 |
| Operational events: "insufficient ground-based observations to make a quantitative accuracy determination" | verified | p. 2059 |
| Not in evidence 19 | new | Authors name flood-map accuracy and timing relative to the peak as "the greatest source of uncertainty" (p. 2064): supports the peak-vs-pass caveat |

## Tarpanelli, Mondini & Camici 2022 (NHESS 22), full text pp. 2473–2489 (publisher PDF)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| ~2,000 European sites, 10 years of discharge | verified | 1,957 gauges, ≥ 10 yr continuous daily record (p. 2476); the 10-yr windows are mostly **pre-Sentinel** years |
| On average 58 % of flood events potentially observable by S1, 28 % by S2, "due to the cloud coverage" | verified | Abstract p. 2473; conclusions p. 2485 (two satellites, ascending + descending) |
| (Q5 Answers) "Tarpanelli shows the precondition: the floods that optical sensors miss are not a random subset, because cloud and flooding coincide" | **corrected** | The study applies an **annual-average** cloud-free probability, independent of floods (p. 2478). That cloud concentrates during floods is the authors' argument for why S2 is likely **overestimated** (p. 2485), not something they measured. The figures are a modelled optimistic upper bound ("optimistic and unrealistic hypothesis", p. 2485) |
| Read depth "search summary" in evidence 19 | upgraded | Full text now read |

## Tiampo et al. 2022 (Remote Sensing 14, 2261), full text pp. 1–21 (publisher version via NOAA repository)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| Read depth "abstract; MDPI 403" | upgraded | Full publisher text obtained from the NOAA Institutional Repository (no login) |
| Compared Sentinel-1 Harvey flood maps (thresholding, DeepLabv3+) with NOAA RSD aerial images and Sentinel-2 NDWI | verified, **scope corrected** | The NOAA comparison is **visual only** (Figs. 11–13; "qualitative advantages", p. 15; "difficult to quantify", p. 18). All numbers (Table 1) are against **Sentinel-2 NDWI**, not NOAA |
| (In short #5) "one peer-reviewed precedent [of NOAA photos as reference], for SAR flood extent" | corrected | It is a precedent for *showing* NOAA photos beside flood maps, not for scoring against them. Our Ida test would be the first quantitative use we know of |
| Photos 35–50 cm, flown at 2,500–5,000 ft with a Trimble DSS (search summary) | verified | pp. 3–4; flown 27 Aug – 3 Sep 2017 |
| "Not seen: co-registration, date gap and how the reference was derived" | resolved | None of these is done in the paper: no co-registration, no per-pixel date matching; p. 4 says NOAA data "were used to identify flooded polygons for ground truthing", but no polygons or scores are reported |
| Abstract "statistical testing suggests the amplitude thresholding technique is the most effective" | corrected (meaning) | The "statistical testing" is precision/recall/F1 from a confusion matrix vs NDWI, without significance tests or intervals (pp. 15–16) |
| Not in evidence 19 | new | Thresholding flags wet roadways as flood (p. 13) |

## Weir et al. 2019, SpaceNet MVOI (ICCV 2019), full text pp. 1–10 (CVF open access)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| 27 looks of one area, −32.5° to 54° | verified | Abstract p. 1; 7.8°–54° off-nadir, sign = look direction (p. 4) |
| Changing view "adds distortions, alters resolution, and changes lighting"; models "generalize poorly to unseen views" | verified | Abstract p. 1 |
| Disaster first looks often > 40° off-nadir | verified | p. 1 (example: San Juan after Maria, 51.9°) |
| Venue note "ICCV (core; Maxar/CosmiQ co-authors)" | corrected | Authors are from In-Q-Tel CosmiQ Works, Accenture Federal Services and Intel AI Lab; **no Maxar authors**. Imagery is Maxar WorldView-2. ICCV qualifies regardless |
| Dataset licence "Various" / unverified | resolved (paper) | Paper states CC BY-SA 4.0 for imagery and labels (p. 2) |
| Not in evidence 19 | new | Resolution-equalised control shows view angle, not resolution, drives the drop (Table 4, p. 6) |

## Hänsch et al. 2022, SpaceNet 8 (CVPRW 2022), full text pp. 1–9 (CVF open access)
| Evidence 19 claim | Status | Full text |
|---|---|---|
| Annotators "were instructed to only attribute what was visible" | verified | p. 3 ("…and not make any assumptions where features could not be seen") |
| CVPRW; Maxar co-authors | verified | p. 1 (Maxar Technologies, DLR, ORNL) |
| Not in evidence 19 | new | Flooded road = water **or rubble** (p. 3); the baseline learned the cloud-omission rule (Fig. 5, p. 6); post tiles have a different pixel size from pre tiles (p. 4); imagery CC BY-NC 4.0 (p. 2) |

## Note on overlap with batch A (2026-10-29, Claude batch B)
Sui 2024, UnCRtainTS and SpaceNet 8 were also handled by agent A, whose ledger rows came first. For UnCRtainTS and
SpaceNet 8 both agents used the same file names, so batch B's summary PDFs and handoff notes replaced agent A's at the
same paths. The batch-B versions are complete full-text summaries, but agent A's original wording for those two is
lost. The claim-check sections above for those three papers stand as a second, independent reading.
