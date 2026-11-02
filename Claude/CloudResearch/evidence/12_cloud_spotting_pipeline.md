# 12: Cloud spotting as a pipeline of tools (2026-10-26; EXPLORATORY, development data only)

Our own measurements, not literature.

**Why:**
- Justin (2026-10-26): "go ahead and test out dinov2 and dinov3 for cloud spotting as well. Use all these techniques
  together. it should be a pipeline of tools that all interact to get the optimal result test with and without them to
  understand their impacts strengths and weaknesses as well as the optimal combos".
- Later that night: "we will not use dinov3 in the library, it is only for research and benchmarking our other
  models".
- So the optimal combo is chosen from the library tools only (bright rule, dark channel, texture, DINOv2). The DINOv3
  arms are a benchmark: how close the library gets.

**Setup:**
- **Plan:** `outputs/preregistration_cloud_spotting_pipeline.md`, written at 00:20 EDT before any score was computed.
- **Code:** GeoAI-Roads `55c8fc2` adds the new module `ClaudeFunctions/sn8_cloudspot.py`.
  - It holds the library tools only and has no DINOv3 code.
  - It was committed before any arm was scored. Every existing module is unchanged.
- **Drivers:** in `evidence/pilot_scripts/cloud_spotting/`:
  - `extract_tokens.py`, `run_cv.py` (stages `library` and `benchmark`), `choose.py`, `summarise.py`, `run_gate.py`
    and `figures.py`, with their logs;
  - outputs: `counts_library.csv`, `counts_benchmark.csv`, `choice.json`, `numbers.json`, `gate_roads.csv` and
    `gate_numbers.json`;
  - post hoc, marked below: `posthoc_disagreement.py` and `posthoc_worst_images.py`.
- **DINOv3 (research only, uncommitted):**
  - `cloud_spotting/dinov3_source.py` wraps the other agent's `pilot_scripts/dinov3/dinov3_bench.tokens3`. It
    freezes that function's source hash when it is imported.
  - The tokens are cached as `ClaudeFunctions/.cache/cloudspot/research_hrc_dinov3_*.npy` (a git-ignored folder).
- **Run times** (shared machine):

  | Step | Time |
  |---|---|
  | DINOv2 tokens | 624 s |
  | DINOv3 tokens | 585 s |
  | Library cross-validation | 2,604 s |
  | Benchmark cross-validation | 3,200 s |
  | SpaceNet 8 gate | 3,031 s |

- **Checks** (each passed, or the run would have stopped):
  - **Scored grid against every pixel:** the fixed rules scored on the grid match every-pixel scoring within 0.0003
    F1. Bright 0.4111 against 0.4112; dark 0.6483 against 0.6485.
  - **Tonight's numbers reproduce:** these are the values in `mask_combo.csv`.
  - **Strip code:** it reproduces `cloud_dark_rise_road` exactly on all 1,037 roads (largest difference 0).
  - **Post-hoc refits:** they reproduce each image's cross-validation counts exactly.
- **Data:**
  - **HRC_WHU:** the 120 development images only (`hrc_images("train")`, 24 per land cover). Two of them are 720 x 1328
    px; the rest are 720 x 1280.
  - **SpaceNet 8:** the 226 Louisiana-East train + val tiles. `set(roads.split) <= {"train", "val"}` is asserted. The
    road table has 1,037 roads on 217 tiles, 468 of them labelled flooded.
  - Labels are the published labels, unmodified. Greyscale only.
- **Not read:** the 30 HRC_WHU test images and the SpaceNet 8 test, north negative, Germany and Louisiana-West tiles.
  `allow_held_out` was never passed.
- **Status:** nothing is promoted. The production cloud rule stays.

**Unit and learner** (fixed in the plan):
- **Pixels:**
  - 1,000 random training pixels per image.
  - Scoring on a fixed grid of every 4th row and column of the held-out images: 6.92 M pixels in all.
  - DINO tokens are reduced to 32 principal components, fitted inside each training fold. They are interpolated
    bilinearly from patch centres to pixels.
- **Folds:** 5 by image, stratified by land cover, seed 662.
- **Primary learner:** a random forest (100 trees, sqrt features, at least 20 per leaf). Cloud is p ≥ 0.5.
- **Secondary learner:** a linear probe (logistic regression).
- **Intervals:** 2,000 resamples of whole images within land cover. Paired comparisons use the same resamples plus an
  exact sign test on per-image F1.

**Tools:**
| Tool | Features |
|---|---|
| **bright** | grey; local std over 21 px; the bright flag |
| **dark** | the dark channel (41 px); its flag at the SpaceNet 8 Otsu cut |
| **texture** | local range over 21 px; mean Sobel gradient over 21 px; local std over 41 px |
| **DINOv2** | ViT-L/14 with registers |
| **DINOv3** | ViT-L/16 SAT-493M (benchmark only) |

## In short
**Evidence (measured):**
1. **The chosen library spotter is bright + texture + DINOv2** (the arm "classical + DINOv2 − dark").
   - Held-out F1 **0.868 [0.848–0.885]**, IoU 0.767, precision 0.884, recall 0.853.
   - Production's dark rule scores F1 0.648 [0.611–0.686].
   - The paired difference is **+0.220 [+0.188, +0.250]**. The spotter is higher on 112 of the 120 images
     (sign test p = 1e-24).
2. **DINOv2 is the tool that matters.**
   - Alone it reaches F1 0.859.
   - Added to the classical cues it gains **+0.106 [+0.084, +0.128]**.
   - **Texture** is the classical tool that matters: added to bright + dark it gains **+0.146 [+0.122, +0.170]**.
   - Once DINOv2 is in, the classical cues add +0.006 [−0.002, +0.013]. That interval includes 0, although 87 of 120
     images go up (sign test p < 0.001).
   - Removing any one classical tool from classical + DINOv2 moves F1 by at most 0.0025.
3. **One classical tool learned alone scores below the fixed rule.**
   - Forest on the dark channel: F1 0.579, against 0.648 for the fixed cut. Forest on the bright cues: 0.593.
   - The forest buys precision with recall. Dark: recall 0.53, against 0.68 for the rule.
4. **Land cover.**
   - Every arm is weakest on **barren** (chosen spotter 0.781) and **snow** (0.833), and best on vegetation (0.935)
     and water (0.895).
   - On barren and snow, false alarms are 60% and 55% of the chosen spotter's wrong pixels (bright ground). On urban
     they are 11%: there the errors are missed thin cloud (recall 0.77).
   - Against the dark rule, DINOv2 gains most where that rule is worst: barren, +0.30 F1 (the dark rule's precision
     there is 0.33).
5. **DINOv3 benchmark (research only).**
   - DINOv3 alone: F1 **0.892**. Best arm, everything − dark: **0.894**.
   - The library spotter reaches **97.0%** of it. Gap +0.027 [+0.019, +0.035].
   - The gap is largest on barren (+0.04) and urban (+0.04).
   - Once DINOv3 is in, DINOv2 and every classical tool add nothing (≤ 0.0015 F1).
6. **On the SpaceNet 8 development roads, the spotter as the road cloud gate.**
   - **Agreement with the dark-rise road rule:** Jaccard 0.71 over all roads. The road rule flags 229, the spotter
     239, both 195.
   - **Roads set aside:** production 239 (27 flooded), the spotter 247 (18 flooded).
   - **Shared roads:** on the 757 roads both gates keep, the flood model trained under the spotter gate is right
     more often: **+1.85 points [+0.4, +3.4], 25 roads fixed / 11 broken, exact McNemar p = 0.029**.

**Inference (not measured):**
- **DINOv2 carries the pipeline.**
  - It sees what a cloud looks like in context, so it separates bright ground from cloud far better than any
    brightness or dark-channel cue.
  - The classical cues are nearly redundant once DINOv2 is in. Texture is the useful one without it.
- **The dark-channel features add nothing to the learned combos.** Removing them is slightly better here (−0.0025),
  but not image by image (57 / 63, p = 0.65). This is a tie, broken by the preregistered rule.
- **Two pictures, chosen after seeing the result, suggest how the gates differ** (section 7):
  - the dark-rise rule reads pale turbid floodwater as cloud (2_15_50: 6 roads labelled flooded set aside);
  - it misses thin cloud streaks that the spotter finds (0_17_13).
  - If that holds generally, the spotter gate keeps trusted flooded roads and drops untrusted dry-labelled ones. That
    fits the counts: 19 of the 33 roads only it keeps are flooded, against 10 of the 41 roads only production keeps.
    Two tiles are not proof.
- **The shared-roads gain is in training, not in which roads are scored.**
  - The same 757 roads are scored under both gates. Only the training roads differ: 41 out, 33 in.
  - Labels under cloud cannot be trusted, so a better score on these labels does not prove better cloud spotting.
- **The spotter's accuracy on SpaceNet 8 pixels is unmeasured.** HRC_WHU is Google Earth imagery at 0.5–15 m, turned
  grey; SpaceNet 8 is Maxar at 0.5 m; and SpaceNet 8 has no cloud labels. The spotter calls over 5% of the grid cloud
  on 87 of 217 tiles.
- **Licence:** HRC_WHU is "academic purpose only", so the fitted spotter is research-only until it is retrained on
  open cloud labels.

## 1. Every arm on HRC_WHU (random forest, held out; 95% intervals from resampled images)
| Arm | Tools | Precision | Recall | F1 [95% CI] | IoU [95% CI] | F1 − dark rule [95% CI] | images higher / lower |
|---|---|---|---|---|---|---|---|
| rule: bright | fixed | 0.812 | 0.275 | 0.411 [0.365–0.457] | 0.259 [0.223–0.297] | −0.237 [−0.288, −0.187] | 20 / 98 |
| **rule: dark (production)** | fixed | 0.618 | 0.682 | **0.648** [0.611–0.686] | 0.480 [0.440–0.522] | — | — |
| rule: bright OR dark | fixed | 0.616 | 0.684 | 0.648 [0.611–0.686] | 0.480 [0.440–0.522] | −0.000 [−0.001, +0.000] | 51 / 27 |
| rule: bright AND dark | fixed | 0.818 | 0.274 | 0.411 [0.364–0.457] | 0.258 [0.223–0.296] | −0.238 [−0.289, −0.188] | 20 / 98 |
| 1 bright | B | 0.627 | 0.561 | 0.593 [0.558–0.626] | 0.421 [0.387–0.456] | −0.056 [−0.078, −0.033] | 38 / 82 |
| 2 dark | D | 0.639 | 0.530 | 0.579 [0.545–0.612] | 0.408 [0.374–0.441] | −0.069 [−0.086, −0.053] | 24 / 95 |
| 3 bright + dark | B D | 0.642 | 0.587 | 0.613 [0.580–0.647] | 0.442 [0.408–0.479] | −0.035 [−0.056, −0.014] | 37 / 81 |
| 4 classical | B D T | 0.768 | 0.751 | 0.760 [0.728–0.790] | 0.612 [0.573–0.653] | +0.111 [+0.082, +0.139] | 102 / 17 |
| 5 DINOv2 | V2 | 0.879 | 0.840 | 0.859 [0.840–0.876] | 0.753 [0.724–0.779] | +0.211 [+0.177, +0.243] | 110 / 10 |
| 6 classical + DINOv2 (library primary) | B D T V2 | 0.879 | 0.852 | 0.865 [0.845–0.883] | 0.763 [0.732–0.791] | +0.217 [+0.187, +0.247] | 112 / 8 |
| 7 6 − bright | D T V2 | 0.877 | 0.849 | 0.863 [0.843–0.881] | 0.759 [0.729–0.787] | +0.215 [+0.183, +0.245] | 112 / 8 |
| **8 6 − dark (chosen)** | **B T V2** | **0.884** | **0.853** | **0.868** [0.848–0.885] | **0.767** [0.736–0.794] | **+0.220** [+0.188, +0.250] | **112 / 8** |
| 9 6 − texture | B D V2 | 0.878 | 0.849 | 0.863 [0.843–0.882] | 0.760 [0.729–0.788] | +0.215 [+0.184, +0.245] | 112 / 8 |
| *10 DINOv3 (benchmark)* | V3 | 0.911 | 0.873 | 0.892 [0.874–0.906] | 0.804 [0.776–0.829] | +0.243 [+0.208, +0.278] | 109 / 10 |
| *11 DINOv2 + DINOv3* | V2 V3 | 0.912 | 0.873 | 0.892 [0.874–0.907] | 0.805 [0.776–0.830] | +0.244 [+0.208, +0.278] | 110 / 10 |
| *12 classical + DINOv3* | B D T V3 | 0.909 | 0.875 | 0.891 [0.874–0.906] | 0.804 [0.777–0.829] | +0.243 [+0.209, +0.276] | 109 / 10 |
| *13 everything (benchmark primary)* | B D T V2 V3 | 0.912 | 0.875 | 0.893 [0.876–0.908] | 0.807 [0.779–0.832] | +0.245 [+0.210, +0.278] | 110 / 9 |
| *14 13 − bright* | D T V2 V3 | 0.911 | 0.875 | 0.893 [0.875–0.908] | 0.806 [0.777–0.831] | +0.244 [+0.209, +0.278] | 111 / 8 |
| *15 13 − dark* | B T V2 V3 | 0.914 | 0.876 | **0.894** [0.877–0.909] | 0.809 [0.781–0.834] | +0.246 [+0.211, +0.280] | 110 / 9 |
| *16 13 − texture* | B D V2 V3 | 0.911 | 0.874 | 0.892 [0.875–0.908] | 0.806 [0.777–0.831] | +0.244 [+0.209, +0.278] | 109 / 10 |

- B = bright, D = dark, T = texture, V2 = DINOv2, V3 = DINOv3. Arms in italics are the research benchmark.
- "images higher / lower" counts images where the arm's F1 is above / below the dark rule's. All sign-test p < 0.001.
- Precision and recall intervals are in `numbers.json` and `summary.log`.

## 2. Strengths and weaknesses by land cover (F1 [95% CI], resampled within the type; random forest)
| Arm | barren | snow | urban | vegetation | water |
|---|---|---|---|---|---|
| rule: bright | 0.570 [0.436–0.673] | 0.203 [0.080–0.326] | 0.246 [0.122–0.397] | 0.537 [0.459–0.603] | 0.450 [0.359–0.532] |
| **rule: dark (production)** | 0.480 [0.396–0.559] | 0.645 [0.544–0.727] | 0.659 [0.551–0.754] | 0.776 [0.720–0.819] | 0.738 [0.667–0.794] |
| bright | 0.493 | 0.471 | 0.576 | 0.740 | 0.688 |
| dark | 0.503 | 0.521 | 0.538 | 0.695 | 0.638 |
| bright + dark | 0.503 | 0.497 | 0.598 | 0.753 | 0.720 |
| classical | 0.606 [0.508–0.695] | 0.637 [0.534–0.724] | 0.763 [0.683–0.834] | 0.895 [0.863–0.920] | 0.856 [0.818–0.883] |
| DINOv2 | 0.783 [0.700–0.847] | 0.830 [0.780–0.866] | 0.841 [0.804–0.876] | 0.928 [0.912–0.939] | 0.876 [0.841–0.904] |
| classical + DINOv2 | 0.778 | 0.831 | 0.852 | 0.934 | 0.893 |
| **chosen: bright + texture + DINOv2** | **0.781** [0.697–0.848] | **0.833** [0.774–0.874] | **0.856** [0.818–0.891] | **0.935** [0.920–0.946] | **0.895** [0.859–0.921] |
| *DINOv3 (benchmark)* | 0.821 [0.750–0.876] | 0.832 [0.773–0.876] | 0.898 [0.870–0.925] | 0.944 [0.925–0.957] | 0.916 [0.883–0.936] |
| *best benchmark: everything − dark* | 0.824 [0.751–0.880] | 0.852 [0.793–0.891] | 0.895 [0.865–0.922] | 0.946 [0.928–0.958] | 0.916 [0.883–0.938] |

**Precision / recall** (random forest):
| Arm | barren | snow | urban | vegetation | water |
|---|---|---|---|---|---|
| rule: dark | 0.33 / 0.88 | 0.57 / 0.74 | 0.87 / 0.53 | 0.94 / 0.66 | 0.80 / 0.68 |
| classical | 0.49 / 0.79 | 0.60 / 0.67 | 0.92 / 0.65 | 0.97 / 0.83 | 0.92 / 0.80 |
| chosen | 0.75 / 0.82 | 0.82 / 0.85 | 0.96 / 0.77 | 0.96 / 0.91 | 0.89 / 0.90 |
| DINOv3 | 0.84 / 0.80 | 0.87 / 0.80 | 0.95 / 0.85 | 0.94 / 0.94 | 0.91 / 0.92 |

**The chosen spotter's wrong pixels** (pooled, scored grid):
| Land cover | False alarms | Misses | False-alarm share |
|---|---|---|---|
| barren | 92,570 | 61,972 | 0.60 |
| snow | 68,328 | 56,605 | 0.55 |
| water | 58,069 | 55,746 | 0.51 |
| vegetation | 21,157 | 44,957 | 0.32 |
| urban | 14,608 | 115,349 | 0.11 |

**Measured:**
- **The dark rule:**
  - Its weak spot is barren (F1 0.48, precision 0.33): bright bare ground lifts the dark channel. This repeats
    tonight's `mask_combo` result.
  - On urban it misses about half the cloud (recall 0.53).
- **The bright rule** is precise on urban, vegetation and water (1.0) but finds only 14–37% of the cloud.
  On snow it fails both ways (0.35 / 0.14).
- **Texture** lifts every land cover: +0.10 to +0.17 F1 over bright + dark, each interval above 0.
- **DINOv2 added to classical** gains most on snow (+0.195 [+0.142, +0.253]) and barren (+0.172 [+0.100, +0.248]),
  and least on vegetation (+0.039) and water (+0.037).
- **The chosen spotter's three worst images** (per-image F1):
  - barren_15, 0.11: it finds 6% of a 43% cloud cover. The dark rule scores 0.51 there, DINOv3 0.35.
  - snow_24, 0.40: it calls bright snow cloud (precision 0.25).
  - barren_14, 0.44: it calls bright ground cloud (precision 0.28).

  Pictures of the first two: section 7.

## 3. Impact of each tool (random forest; F1 with the tool minus without, paired over the same images)
| Impact | ΔF1 [95% CI] | images up / down | sign test p |
|---|---|---|---|
| dark added to bright | +0.021 [+0.014, +0.028] | 86 / 34 | < 0.001 |
| bright added to dark | +0.034 [+0.019, +0.048] | 88 / 31 | < 0.001 |
| **texture added to bright + dark** | **+0.146 [+0.122, +0.170]** | 112 / 7 | < 0.001 |
| **DINOv2 added to classical** | **+0.106 [+0.084, +0.128]** | 102 / 18 | < 0.001 |
| classical added to DINOv2 | +0.006 [−0.002, +0.013] | 87 / 33 | < 0.001 |
| loss when bright is removed from classical + DINOv2 | +0.0025 [−0.001, +0.005] | 76 / 44 | 0.0045 |
| loss when dark is removed from classical + DINOv2 | −0.0025 [−0.005, −0.001] | 57 / 63 | 0.65 |
| loss when texture is removed from classical + DINOv2 | +0.0021 [−0.000, +0.004] | 81 / 39 | 0.0002 |
| loss when DINOv2 is removed from classical + DINOv2 | +0.106 [+0.084, +0.128] | 102 / 18 | < 0.001 |
| *DINOv3 added to classical* | +0.132 [+0.109, +0.155] | 109 / 10 | < 0.001 |
| *DINOv3 added to DINOv2* | +0.033 [+0.025, +0.041] | 106 / 14 | < 0.001 |
| *DINOv3 added to classical + DINOv2* | +0.028 [+0.019, +0.037] | 101 / 19 | < 0.001 |
| *classical added to DINOv3* | −0.000 [−0.004, +0.003] | 70 / 49 | 0.066 |
| *loss when bright is removed from everything* | +0.000 [−0.001, +0.002] | 64 / 55 | 0.46 |
| *loss when dark is removed from everything* | −0.0015 [−0.002, −0.001] | 50 / 69 | 0.099 |
| *loss when texture is removed from everything* | +0.0006 [−0.000, +0.001] | 68 / 51 | 0.14 |
| *loss when DINOv2 is removed from everything* | +0.0015 [−0.001, +0.005] | 55 / 64 | 0.46 |
| *loss when DINOv3 is removed from everything* | +0.028 [+0.019, +0.037] | 101 / 19 | < 0.001 |

A "loss" is F1 with the tool minus F1 without it, so a negative loss means the arm did better without the tool. By
land cover, every row is in `numbers.json` ("impacts by land cover").

**Measured:**
- Removing dark from classical + DINOv2 helps a little on every land cover (−0.001 to −0.003). No single type's
  interval is clearly below 0.
- Classical cues added to DINOv3 hurt barren (−0.007 [−0.013, −0.002]) and help snow (+0.012 [+0.002, +0.022]).

## 4. The optimal library combo (preregistered rule)
| Arm | F1 | best − arm [95% CI] | candidate? |
|---|---|---|---|
| bright | 0.593 | +0.247 to +0.304 | no |
| dark | 0.579 | +0.262 to +0.315 | no |
| bright + dark | 0.613 | +0.225 to +0.282 | no |
| classical | 0.760 | +0.086 to +0.132 | no |
| DINOv2 | 0.859 | +0.002 to +0.014 | no |
| classical + DINOv2 | 0.865 | +0.001 to +0.005 | no |
| classical + DINOv2 − bright | 0.863 | +0.003 to +0.007 | no |
| **classical + DINOv2 − dark** | **0.868** | best | **yes: chosen** |
| classical + DINOv2 − texture | 0.863 | +0.002 to +0.007 | no |

- Every other arm's paired interval excludes 0, so the rule had no simpler tie to fall back on.
- The intervals are tight because every arm is scored on the same images. The five DINOv2 arms lie within 0.009 F1
  of each other. DINOv2 alone (one tool) is 0.009 below the chosen arm.
- **Benchmark:** the best DINOv3 arm (everything − dark, 0.894) is ahead of the chosen spotter by +0.027
  [+0.019, +0.035]. The chosen spotter reaches 97.0% of it.

## 5. The secondary learner (linear probe; reported, not used for the choice)
| Arm | F1 [95% CI] |
|---|---|
| dark | 0.576 [0.534–0.615] |
| classical | 0.715 [0.680–0.750] |
| DINOv2 | 0.854 [0.832–0.873] |
| classical + DINOv2 | 0.866 [0.844–0.884] |
| chosen (B T V2) | 0.865 [0.842–0.884] |
| *DINOv3* | 0.895 [0.877–0.909] |
| *everything* | **0.901** [0.884–0.916] |

- The linear probe matches the forest on the DINOv2 arms and is 0.045 lower on the classical arm.
- On the DINOv3 arms it is 0.003–0.008 higher.
- The order of the families is the same: single classical tools < classical < DINOv2 combos < DINOv3 combos.
- Within a family the top arm differs: the probe puts classical + DINOv2 (0.866) and everything (0.901) on top.

## 6. On SpaceNet 8: the chosen spotter as the road cloud gate (226 development tiles)
**The spotter:** bright + texture + DINOv2, refitted on all 120 HRC_WHU development images.
- It runs on each tile's grey after image. Cloud is p ≥ 0.5.
- A road is cloudy when ≥ 20% of its strip is under the mask: the same strip and the same cut as the production road
  rule.
- The spotter gate is the tile rule + this road rule. It replaces only the dark-rise road rule.

**Roads flagged by each road rule (strip share ≥ 0.2):**
| Scope | Roads | Road rule | Spotter | Both | Road rule only | Spotter only | Jaccard | Flooded among road rule only | Flooded among spotter only |
|---|---|---|---|---|---|---|---|---|---|
| all roads | 1,037 | 229 | 239 | 195 | 34 | 44 | 0.71 | 19 | 11 |
| roads the tile rule keeps | 891 | 93 | 101 | 60 | 33 | 41 | 0.45 | 19 | 10 |

The spotter's share of a tile against the tile's mean road dark-rise share: Spearman 0.68.

**The production flood model** (tuned random forest, 96 production features) **under each gate**: 5 folds by tile,
seed 662, the same folds for both gates, held-out calls on the kept roads.

| Gate | Kept | Set aside | Flooded set aside | TP | FN | FP | TN | Accuracy [95% CI] | Flooded found | Dry kept dry | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| production (tile rule + dark-rise road rule) | 798 | 239 | 27 | 390 | 51 | 91 | 266 | 0.822 [0.79–0.86] | 0.884 | 0.745 | 0.640 |
| spotter (tile rule + spotter road rule) | 790 | 247 | 18 | 416 | 34 | 88 | 252 | 0.846 [0.81–0.88] | 0.924 | 0.741 | 0.686 |

**Shared roads** (kept by both, 757):
- accuracy 0.824 under production and 0.843 under the spotter;
- difference **+0.0185 [+0.004, +0.034]** (tiles resampled);
- 25 roads fixed / 11 broken, **exact McNemar p = 0.029**.

**Roads only one gate keeps** (scored by that gate's model):
| Roads | n | Flooded | Dry | Called flooded | Right | Median dark-rise share | Median spotter share |
|---|---|---|---|---|---|---|---|
| kept by production only | 41 | 10 | 31 | 9 | 32 (78%) | 0.000 | 0.392 |
| kept by spotter only | 33 | 19 | 14 | 22 | 30 (91%) | 0.547 | 0.003 |

**About the labels:** under cloud a road's flood label cannot be trusted. SpaceNet 8 analysts labelled only what they
could see, so a hidden flooded road reads as "not flooded".
- The spotter gate keeps 33 roads the dark-rise rule calls cloudy. If they really are under haze, their 14 dry labels
  are suspect. Their 19 flooded labels can be trusted.
- The 41 roads the spotter sets aside and production keeps are mostly dry-labelled (31). If the spotter is right that
  they are under cloud, those dry labels are suspect too, and production trains and scores on them.
- So the scores above compare gates on labels that are least reliable exactly where the gates disagree. The +1.85
  points on the shared roads come only from the different training roads: the same 757 roads are scored.

## 7. Pictures (`figures/cloud_spotting/`)
**Preregistered:**
- **`hrc_barren_1.png` and `hrc_vegetation_1.png`:** the first barren and the first vegetation image (fixed rule).
  - Panels: grey; expert mask; dark rule; DINOv3 alone (benchmark); the chosen spotter. Green = found, red = false
    alarm, blue = missed.
  - The dark rule finds the bright cores and misses the cloud's thinner margins (F1 0.65 and 0.66). The chosen
    spotter scores 0.95 and 0.92, and DINOv3 0.95 and 0.95.
  - Both images turn out to be easy cases, so the post-hoc pictures below show the hard ones.
- **`sn8_2_23_44_gates.png`:** before, after, the dark-rise mask (38% of the tile), the spotter mask (44%) and what
  each gate does.
  - The tile has 3 roads. Both gates set aside the one under the cloud: 71% of its strip is under dark rise and 70%
    under the spotter, and it is labelled not flooded. Both keep the two on the clear left side, labelled flooded.
  - The spotter also marks patches over the dark forest at the lower left, where no road runs. Whether that is thin
    haze or false alarm cannot be told without labels.

**Post hoc (chosen after seeing the results):**
- **`posthoc_sn8_2_15_50_spotter_keeps.png`:** the tile with the most roads only the spotter keeps (6, all labelled
  flooded).
  - The dark-rise mask covers 38% of the tile. Its shape follows the pale water around the houses and the road, and
    the before image has dark tree cover there. The spotter calls 2%.
  - What it looks like: turbid floodwater raises the dark channel, and the dark-rise rule reads it as haze.
- **`posthoc_sn8_0_17_13_production_keeps.png`:** the tile with the most roads only production keeps (6, all labelled
  not flooded).
  - Thin cloud streaks lie over the highway lanes on the left of the after image. The spotter flags those roads
    (strip shares 0.21–0.71); the dark-rise rule does not (≤ 0.04).
- **`posthoc_hrc_barren_15_worst.png` and `posthoc_hrc_snow_24_worst.png`:** the chosen spotter's two lowest
  per-image F1 images.
  - Each image is predicted by its held-out fold's model, refitted and checked against the cross-validation counts.
  - **barren_15** (43% cloud): wide, thin, streaky cloud over bare ground of almost the same grey. Every method misses
    most of it, and none makes a false alarm (precision 1.00). Recall: the dark rule 0.35 (F1 0.51), DINOv3 0.21
    (0.35), the spotter 0.06 (0.11). This is the one kind of image where the fixed dark rule beats both backbones.
  - **snow_24** (11% cloud): cloud lying over a white snowfield. All three call the snowfield cloud. The dark rule
    marks nearly the whole image (precision 0.15, F1 0.26); DINOv3 and the spotter mark large patches of it
    (precision 0.27 and 0.26, F1 0.40 each). In greyscale, snow and cloud look alike to every tool.

## Departures from the plan
1. **The DINOv3 token code came from the other agent:** `dinov3_bench.tokens3`, in the research folder. Its settings
   are the preregistered ones: the sat493m mean and std from the checkpoint's own timm config, 2 x 2 windows, 16 px
   patches and the 5 prefix tokens dropped. `dinov3_source.py` freezes its source hash when imported.
2. **`choose.py` was added** so the SpaceNet 8 run could start before the benchmark finished.
   - It applies the same `choose` to the same library counts. `summarise.py` recomputes the choice and asserts it
     agrees, and it did.
   - `run_gate.py` and `figures.py` read the choice from `choice.json` rather than `numbers.json`.
3. **`figures.py` was refactored into functions** after the first render, because the SpaceNet 8 panel titles were
   clipped. The panels are the same.
4. **Two post-hoc scripts** were added (section 7). They are marked in the file names and the figure captions.
5. **The spotter on SpaceNet 8 predicts only on the strips and the scored grid** (every 4th pixel), except on the
   pictured tiles, which use every pixel. The road shares are identical to scoring every pixel. The tile share is on
   the grid.

## What stays uncertain
- **Pixel accuracy on SpaceNet 8.** Only the agreement with the dark-rise rule and two pictures are measured; there
  are no cloud labels for these tiles.
- **Transfer from Google Earth to Maxar.** HRC_WHU images range from 0.5 to 15 m while the windows are in pixels, and
  greyscale from different sensors differs. The spotter is trained on one and applied to the other.
- **Whether the shared-roads gain (+1.85 points, p = 0.029) holds on unseen roads.** It is one exploratory test on
  development roads, and it is driven by the 74 roads where the gates disagree, where the labels are least reliable.
- **Whether a learned cut that targets F1 would rescue the single classical tools.** The cut was fixed at p ≥ 0.5 and
  not tuned.
- **Ties among the DINOv2 combos.** Their differences (≤ 0.009 F1) are much smaller than the differences between land
  covers. "−dark" won by the preregistered rule, but a second dataset could reorder them.
- **Licence.** HRC_WHU is academic use only: the spotter stays research-only until it is retrained on open cloud
  labels. DINOv3 stays out of the library.
- **No HRC_WHU test image was opened.** These are cross-validated development numbers only.
