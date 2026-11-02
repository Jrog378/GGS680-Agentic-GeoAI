# Methodology v1: detecting, handling and reporting cloud in post-disaster change maps

Stage 4 of the Assignment 3 workflow (Methodology Agent). Claude wrote this on 2026-10-23, working alone from local
files. It covers the method and an eight-week work plan for the paper.

- **Question order:** Q2 leads, then Q3, then Q1 (`selected_questions.md`; Justin, 2026-10-23).
- **Justin's checkpoint:** he accepted Q2's hypothesis and scope "for now, we are just creating the outline"
  (`decision_log.md`). Everything below is a proposal he can change.
- **This is a plan.** It holds no new results. Every number comes from the evidence files, the earlier outputs, or a
  file I checked read-only today (section 0). All of it is development data. No sealed data was read.

Tags:
- **Evidence:** a number or statement found in a file. The file is named.
- **Inference:** my reasoning. It has not been measured.

Every agent in this workflow runs on the same model. Where this plan agrees with the critic, that is not independent
validation (AGENTS.md rule 4).

---

## 0. Inputs used

- **Rules and role:** `05_Project/AGENTS.md`; `05_Project/agents/methodology_agent.md`.
- **Problem and decisions:** `CloudResearch/input_card.md`; `CloudResearch/decision_log.md`.
- **Questions:** `outputs/selected_questions.md` (wording, order, "no" rules). `outputs/research_questions_refined_v3.md`
  (method detail). `outputs/question_review.md` (the critic). `outputs/abstract_v1.md`.
- **Evidence:** `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, `03_pre_refinement_checks.md`,
  `04_research_question_guide.md`.
- **A new idea from Justin, relayed by the coordinator during this stage (2026-10-23):** reference-based (two-date)
  de-hazing, as a candidate method for the "handle" step. Written up as an option in section 6.4.
- **Checked read-only today, to say what exists.** I ran nothing that scores anything.
  - The roads side-test code in `~/Masters/GGS662/ProjectBranch/ClaudeFunctions/`: `sn8_heldout.py`, `sn8_clouds.py`,
    `sn8_cloudref.py`, `sn8_dino.py`, `sn8_roads.py`, `sn8_models.py`, `sn8_results.py`, `sn8_data.py`. I listed their
    functions and constants.
  - `ProjectBranch/Code/results/production.json`: the frozen production stages.
  - `Project/docs/datasets/splits/sn8_louisiana_east_stratified_2026-10-16.csv`: tile ids and split names only. I
    counted tiles per area.
  - The header of one HRC_WHU development image (`barren_1.tif`): its size and tags.
  - `Project/Tiltfile` and `Project/tilt/`: searched for roads side-test resources.
- No web, no sub-agents, no images viewed, no sealed data.

**Evidence from these checks:**
- Development tiles by area: **south (area 0) 105** (91 training + 14 validation); **west (area 2) 121** (95 + 26).
  Test tiles: south 22, west 18. The north negative set is all of area 1 (333 tiles). Development data therefore
  covers two areas only.
- Tile ids are `<area>_<column>_<row>` on the SpaceNet grid. The existing neighbour check (`sn8_clouds.neighbour_check`)
  already uses them to find the 8 tiles around a tile.
- `barren_1.tif` is 1280 × 720 pixels, RGB, 72 dpi, with no geographic tags. **So HRC_WHU files do not store their
  ground resolution.** It must come from Li et al. (2019) or the dataset page.
- The data module (`sn8_data.label_counts`) already counts buildings and flooded buildings per tile. Nobody has run
  it for this purpose, so the counts are still unknown.
- I found no roads side-test resource in `Project/Tiltfile` or `Project/tilt/` (searched for `sn8`, `ProjectBranch`
  and `roads`). The side test has run from notebooks in `ProjectBranch/Code/`.

## 1. Assumptions

- **Time.** Week 1 starts Monday 26 October 2026. Submission is Friday 18 December 2026. US Thanksgiving (26 November)
  falls in week 5.
- **The model.** One frozen flood model: production as recorded in `production.json` on 2026-10-23. It is a random
  forest on classical, texture and DINOv2 change cues, with the tile rule + road rule cloud gate. **Evidence (01):**
  83.0% on 798 assessable roads; always "flooded" scores 55.3%. No promotions happen while the paper is being scored.
- **Labels.** Published SpaceNet 8 labels, unmodified. A "flooded" label is trusted anywhere. A missing label means
  "dry" only on clear roads, and even that is untested (critic, issue X3; v3 §10 item 7).
- **Synthetic truth.** Scoring against where we placed a synthetic cloud is allowed. **Justin has not ruled on this**
  (v3 §10 item 2). If he rules it out, Q2's "synthetic only" tier is empty, and Q1's checks lose half their truth.
- **HRC_WHU.** Its outlines, and its cloud pixels for texture, may be used. **Justin has not ruled on this either.**
  A fallback that needs neither is given in step Q1.1.
- **Rules are fixed before scoring.** The ceilings and margins in section 8 are proposals. They are frozen in a
  pre-registration at the end of week 1, after a power check that uses no cloud outcomes. After that they never move.

---

## 2. The design on one page

**The arc** (Justin's three verbs; `input_card.md`):
- **Detect (Q1):** build synthetic clouds from real cloud outlines and check them against real cloud. This is the test
  bed.
- **Handle (Q3):** when only the before image is cloudy, test whether the after image alone finds change better than
  both images together.
  - **Option (Justin's idea; where it sits is his call):** reference-based de-hazing. Use the clear date to measure
    and undo thin cloud on the other date, without erasing real change (section 6.4).
- **Report (Q2, the lead):** sort what a map can say about hidden roads into "reliable", "synthetic only" and "range
  only", using limits fixed in advance.

**How the parts depend on each other:**
- Q2's real-data parts (H2a, H2b, real recall, the ranges) need nothing new. They can start in week 1.
- Q2's synthetic tier needs Q1's test bed.
- Q3's clouded before images need Q1's frozen generator. Its after-only score is a real-image measurement and needs
  nothing from Q1.
- So the **build order** is: Q2 real parts and Q1's generator first, then Q1's checks and bed, then Q3, then Q2's
  tiers. The **paper order** is detect, handle, report.

**The flow, in words:**
1. Development tiles and images → frozen production calls, kept on every road.
2. A frozen cloud generator → clouded copies of clear tiles (after image for Q1 and Q2; before image for Q3).
3. Recomputed cues → the same fold models' calls → scores against published labels on clear roads.
4. Realism checks decide whether the bed's numbers speak for real cloud.
5. Tiers, ranges and maps for Q2.
6. Everything frozen → one batched look at the sealed sets.

---

## 3. Data, split and the sealed final check

### 3.1 Development data (the only data used in weeks 1–6)

| Data | What is used | Size | Source |
|---|---|---|---|
| SpaceNet 8 Louisiana-East, Hurricane Ida (2021) | Maxar before and after tiles, warped to one 0.5 m UTM grid, greyscale after the first step | 226 tiles: 186 training + 40 validation, pooled in the folds | Evidence 01; split file |
| Road labels | OpenStreetMap centrelines; `flooded` is "yes" (487) or missing (593), never "no" | 1,037 touched roads on 217 tiles | Evidence 01 |
| Assessable roads (adopted rule) | Roads not gated by the tile rule or road rule | 798 roads | Evidence 01 |
| Clear roads for the test bed | Less than 5% of the strip under the dark-rise mask | 769 roads on 190 tiles (433 flooded, 336 dry) | Evidence 03 |
| Real thin-cloud roads | At least 20% of the strip under dark rise | 93 roads on 39 tiles; 24 labelled flooded | Evidence 01; critic §3 |
| Opaque-cloud tiles | At least 20% of the tile under the bright mask | 17 tiles, 146 roads, 3 labelled flooded | Critic §3 |
| Building labels (secondary, if they pass week 3) | Footprint polygons with a `flooded` field (null on the one tile read) | Unknown on development tiles | v3 §4 |
| HRC_WHU (Li et al. 2019, unverified) | Google Earth RGB at 0.5–15 m, converted to grey; expert cloud masks; no shadows labelled | 120 development images, 24 per land-cover type (barren, snow, urban, vegetation, water) | Evidence 01, 02; v3 §1 |

### 3.2 How the data is split

- **Folds (exist).** The 226 development tiles are pooled. Five folds by whole tile (`StratifiedGroupKFold`, shuffled,
  seed 662). No road is scored by a model that saw its tile. This is the harness in `sn8_heldout.py`.
- **Thresholds (exist).** The Otsu thresholds of the dark and dark-rise masks were learned on the 186 training tiles
  (98 and 71 grey levels; evidence 01). They use no labels. **Inference:** a small leak, because those tiles are
  also held out in turn. The blocked-fold run (section 10.3) re-learns them inside each fold, as a check.
- **HRC_WHU.** The authors' split (fingerprinted in `sn8_cloudref.py`). Development images only.
- **The test bed.** Production's fold models score held-out clear tiles. Only the held-out tile's images get cloud.
  No model is ever trained on synthetic cloud.
- **The frozen setup for the sealed look** is fitted on all 226 development tiles.

### 3.3 The sealed final check (named in advance)

One batched, logged look, in week 7, by setups frozen at the end of week 6.

- **In the look (proposed):**
  - **SpaceNet 8 Louisiana-East test tiles: 40** (south 22, west 18). Frozen model, generator, masks, after-only model
    and flag. All three questions are re-scored there.
  - **HRC_WHU test images: 30** (6 per land-cover type). Q1's check 2 and the single-date half of Q2's "hidden" row and
    Q3's flag.
- **Justin's call (AGENTS.md rule 9):**
  - **North negative set** (333 tiles; 1 of 1,437 roads flooded, per v3). A real false-alarm test for Q3's
    after-only call.
  - **Germany** (202 tiles). The only second event. **Inference:** it is confounded (a winter before image against
    summer after images on the one tile seen), its label coding is unknown, and it may hold no cloud.
- **Never used:** Louisiana-West (no labels, per the critic).
- **Inference: the test tiles are not an external test.** They come from the same two areas as the development tiles
  and were split at random by flood class. Many sit next to development tiles. So the sealed look guards against
  overfitting, not against a new place.

### 3.4 Licences

- SpaceNet 8 and HRC_WHU are research-only data (input card). HRC_WHU is "academic purposes only" (evidence 02).
  The loader already carries the credit line "HRC_WHU (Li et al., 2019; imagery Google Earth), academic use only".
- **Open point:** a journal figure that shows HRC_WHU crops shows Google Earth imagery. Whether that needs permission
  is not in the files. Check before submission (section 19).
- DINOv2 runs from local open weights in `~/Masters/models/` (`sn8_dino.py`). Record their licence from the model card
  in the data statement.

---

## 4. Units of analysis

| Question | Scored unit | Resampling unit (the real sample) | Reported at |
|---|---|---|---|
| Q2 | The road: the strip about 5 m either side of the centreline | The tile | Road; tile; area (south, west) for maps and flooded length in metres |
| Q3 | The mapped object: road strip (primary); building footprint plus a 10 m ring (secondary) | The tile | Object; tile |
| Q1, check 1 (realism on SpaceNet 8) | A fixed ground window under cloud: 14-pixel (7 m) cells for contrast and pattern; 64-pixel (32 m) windows for patchiness | The tile | Bin of dark-floor rise |
| Q1, check 2 (realism on HRC_WHU) | The image: real cloud and pasted synthetic cloud in the same image | The image, within land-cover type | Land-cover type |
| Q1, test bed | The mapped object | The tile | Grid cell; target |

- **Evidence (critic X2):** roads on one tile share cloud, flooding and image conditions. So the tile, not the road,
  is the sample size. Every result states its tile count.
- **Inference (MAUP and ecological fallacy):** a tile or area figure does not say what happened on one road. Example:
  "cloudy tiles in area 2 carry few flooded labels" does not mean any one hidden road was dry.

---

## 5. What already exists and what is new

| Piece | Status | Where |
|---|---|---|
| Held-out harness: 5 folds by tile, seed 662 | **Exists** | `sn8_heldout.py` |
| Tile-resampled 95% intervals for one model and for paired differences; McNemar's exact test | **Exists** | `held_out_report`, `paired_report` |
| "Cannot assess" handling: gated roads neither fitted nor scored | **Exists** | `gated_calls`, `gated_report` |
| Bright, dark and dark-rise masks; road and tile cloud shares; the adopted rule | **Exists** | `sn8_clouds.py` |
| He et al. de-hazing (guided filter) | **Exists** | `sn8_clouds.dehaze` |
| Neighbour check on the tile grid | **Exists** | `sn8_clouds.neighbour_check` |
| HRC_WHU loader, authors' split, single-date masks, per-image and per-type scores | **Exists** | `sn8_cloudref.py`; outputs in `Code/cloudref_test.ipynb` |
| Production model and its frozen stages | **Exists** | `sn8_models.flood_model`; `production.json` |
| Frozen DINOv2-L change cues, with pooled after-minus-before vectors per road | **Exists** (roads only) | `sn8_dino.py` |
| Road strip and 10 m ring owner maps; `_before`, `_after` and `_change` cue columns | **Exists** | `sn8_roads.py` |
| Run logs with code hashes | **Exists** | `sn8_results.py` |
| Per-tile building and flooded-building counts | **Code exists, not run** | `sn8_data.label_counts` |
| Uniform-haze injection (evidence 03) | **Exists, but in a past session's scratchpad** (`cloudresearch/mask_bias.py`). May be gone. Move into the repo | Evidence 03 |
| Fold models that also call hidden roads (needed for H2a and the ranges) | **New, small** | Extends `gated_calls` |
| Synthetic cloud generator: families M and X, uniform control, two placements, before or after image, seeded | **New** | — |
| HRC_WHU shape and texture pool, rescaled to 0.5 m | **New**; blocked until the resolution source is found | — |
| Realism statistics and matched-rise binning | **New** | — |
| Test-bed runner: cloud → recomputed cues (with DINOv2) → fixed fold models | **New** | — |
| After-only model on `_after` columns | **New, small** (columns exist) | — |
| Before-image cloud flag | **New** | — |
| Permanent-water mask on before images (classical, GGS 680) | **New** | — |
| Q2 tier scorer, ranges, flooded length per area, tipping points, cannot-assess map | **New** | — |
| Within-tile label test for Q2b | **New, small** | — |
| Blocked, buffered and leave-one-area-out folds | **New, small** | — |
| Minimum detectable differences from existing calls | **New, small** | — |
| Building table: footprint and ring owner maps, cues, cloud share, clean DINOv2 pass | **New, 1–2 weeks** (v3 §4); conditional | — |
| Co-registration of the two dates (about 0.6 m ground shift) | **Exists** | `sn8_coreg.py`; evidence 01 |
| Reference-based de-hazing fit (option, §6.4) | **New.** Being prototyped now in the coordinating session. Move it into the repo, with tests, before it is frozen | — |
| Inter-date gain and offset from clear ground, and the "change kept" measure (option, §6.4) | **New, small** | — |
| Tilt resources for every step (project rule) | **New, small** | `Project/Tiltfile` |

---

## 6. Analysis steps per question

### 6.1 Q2 (lead). What can a flood-road map reliably tell users about roads hidden by cloud?

**Outcome (the dependent variable).** For each statement a map could make about a hidden road, its error, or a range
where the error cannot be measured.

**Exposure (the explanatory variable).** Cloud over a road's strip in the after image. Levels set by the existing
masks, fixed before scoring:
- clear;
- thin: at least 20% of the strip under the dark-rise mask;
- opaque: the tile has at least 20% bright cloud.

**The five statements and how each is scored:**

| # | What the map says | Error measured | Where it can be measured |
|---|---|---|---|
| S1 | "This road is hidden; it cannot be assessed" | Missed hidden (cloud there, rule lets it through) and false hidden (no cloud, rule flags it) | Real: HRC_WHU expert masks, single-date masks only. Synthetic: the bed, two-date rule |
| S2 | "This hidden road is flooded" (thin cloud) | Share of "flooded" calls that are wrong | Synthetic: the bed. Real: only recall on the 24 trusted flooded roads, reported |
| S3 | "This hidden road is dry" (thin cloud) | Share of "dry" calls that are wrong | Synthetic: the bed only |
| S4 | Accuracy on hidden roads | None (no truth under cloud) | A range |
| S5 | Flooded road length in an area with hidden roads | None | A range, in metres |

S2 and S3 ask whether the map could call thin-cloud roads instead of abstaining. They use the fold models' calls on
hidden roads, which the map does not show today.

**Inference: what the rule allows by construction.** S2's and S3's errors need dry labels under cloud, which cannot
be trusted. So on real cloud they cannot be measured. **At best they reach "synthetic only".** Only S1's single-date
half can reach "reliable". This matches the predicted tiers in v3 and the "no" rule in `selected_questions.md`.

**Steps:**
1. **Fit once and keep every call.** Use production's fold models under the adopted rule. Also have each fold model
   call the hidden roads of its own fold (they are still not fitted on). **Exists:** the fit. **New:** calling hidden
   roads.
2. **Freeze the rules** (pre-registration, week 1): each statement's error, its ceiling, and which evidence may test it
   (section 8).
3. **Measure the real-data parts (week 1).**
   - **S1, single-date half.** Score the bright and dark masks on HRC_WHU in road-sized windows (about 10 m), flagged
     when 20% or more is under the mask, as the road rule does. Images too coarse for this are scored per pixel. Per
     land-cover type.
   - **S2, real recall.** Recall on the 24 trusted flooded roads under thin cloud. Reported, not tested (section 9).
   - **H2a.** Score the same calls twice: once on the 798 assessable roads, once on all 1,037 with missing labels read
     as dry. The rise is the inflation, with a tile-resampled interval.
   - **H2b.** On tiles that hold both clear and thin-cloud roads: are the cloudy roads less often labelled flooded?
     An exact test stratified by tile (Mantel–Haenszel type; needs citation), so geography between tiles drops out.
   - **Opaque tiles.** Described only (17 tiles, 3 flooded labels). Reported as a check that the dataset behaves as
     documented, not as a finding (critic C1-2).
4. **Measure the synthetic parts (week 4, on Q1's bed).**
   - **S1, two-date half.** On the bed, a road is "truly hidden" when its synthetic cloud is thick enough to spoil
     the flood call and covers at least 20% of its strip. "Thick enough" is the thinnest grid level at which the
     bed's error on family X rises more than 1.5 points above clean. **Why:** the real thin level comes from the
     dark-rise mask itself, so scoring the mask there would be circular. Missed-hidden and false-hidden rates are then
     read off. The false-hidden rate includes roads just outside a placed cloud, so it measures the 20 m window's edge
     effect (critic X1).
   - **S2 and S3.** At Q1's real thin level, on family X: the share of wrong "flooded" calls and wrong "dry" calls
     among roads the road rule flags. Also on all clouded roads, since the flagged set is chosen by the mask.
5. **Bound the rest.**
   - **S4.** Two bounds on accuracy on hidden roads: every missing label is flooded; every missing label is dry.
   - **S5.** Per area: low end = assessed flooded length; high end = that plus all cannot-assess length. In metres.
   - **Tipping points (critic X3).** For each conclusion, say where the truth under cloud would have to sit to flip it.
   - **No filling in from neighbours.** **Evidence (01):** in area 2, a cloudy tile had 0 of 7 roads labelled flooded
     beside clear neighbours at 79%; in area 0 the neighbours are dry too. **Evidence (03):** under thick haze the mask
     flags flooded roads more often (+13.2 points at t = 0.6). **Inference:** so the assessed roads under-represent
     flooded ones, and neighbours are a biased guide.
6. **Assign tiers and report.**
   - "Reliable": a real-imagery error, with a published truth, whose upper bound is below its ceiling.
   - "Synthetic only": the same, but measured only on the bed. If Q1's realism check fails for that family and level,
     it reads "synthetic only, realism not shown".
   - "Range only": no error can be measured.
   - The map shows cannot-assess roads by area, beside the flood share of their assessed neighbours. It keeps "can we
     see it?" apart from "is it flooded?", as WorldFloods v2 does (Portalés-Julià et al. 2023, unverified).
   - An optional risk–coverage figure, with the classifier fixed and only the abstention varied (critic C3-2).

**What counts as "no"** (`selected_questions.md`). Every statement except "this road is hidden" fails its ceiling. Then
the answer is that a map can say only where it cannot see.

### 6.2 Q3. When only the before image is cloudy, does the after image alone find change better than both images together?

**Outcome.** Balanced accuracy (missed floods and false floods weigh the same), on clear objects, against published
labels.

**Exposure.** Synthetic cloud on the before image only, at four levels fixed in advance: opaque full cover (primary;
Justin's case), Q1's real thin level, and two levels between. **Evidence (01):** no Louisiana-East before image is
cloudy, so the cloud must be synthetic.

**Arms.** The two-date production model (comparator); an after-only model; routing by a before-cloud flag
(secondary); abstaining on before-cloudy objects; always "flooded".

**Steps:**
1. **Fit the after-only model (week 2).** Production's random forest settings on the existing `_after` columns only,
   in the same five folds. No new cue is designed. Score it on every clear development road. **Inference:** this is a
   real-image measurement, because the model never reads the before image.
   - **Go/no-go:** section 8.
   - **Fairness check.** The after-only model has no DINOv2 cue: the cache holds after-minus-before vectors only. So
     also compare it with the two-date model without DINOv2 cues. **Evidence (01):** DINOv2 adds +1.2 points.
2. **Cloud the before images (week 5).** Q1's frozen generator, both families, on held-out clear tiles. After images
   untouched. Recompute the two-date cues, with DINOv2 (about 45 min of GPU per level; v3 §6).
   - **Leak check:** the after-only calls must be identical on clean and clouded copies.
3. **Primary test.** At opaque cover: after-only minus two-date balanced accuracy, paired on the same roads, with a
   tile-resampled 95% interval. Also report flooded recall, the dry-call rate, the thickness where the two cross, and
   what production does now with these roads. **Inference (v3):** today's gates would not notice. The tile rule reads
   the after image only, and the road rule looks for a rise from before to after, while before-only cloud gives a fall.
4. **H3b, state against change (week 5, real images).** Mark clear dry roads with permanent water in their 10 m ring
   in the clear before image (water covering at least 10% of the ring). The water mask is classical, label-free, and
   set on the training tiles before scoring. Compare false "flooded" rates of the two models inside and outside that
   group.
5. **H3c, routing (week 5; first to be cut if behind).** The flag: a fall of the dark floor from before to after, plus
   smoothness on the before image, with Otsu thresholds learned inside the training folds. Score oracle routing, flag
   routing and no routing, on clouded and on clean roads. Report the flag's rate on clean flooded and clean dry roads.
   **Inference:** floodwater also lowers the after floor, so the flag may fire on floods. Score the flag's
   single-date half (smoothness and brightness) on HRC_WHU, per land-cover type.
6. **Buildings** repeat steps 1–4 if they pass the week-3 go/no-go.

**What counts as "no."** The interval of (after-only − two-date) includes 0 or lies below it at every level, opaque
included. **Inference (v3):** this could happen, because the forest already holds the `_after` cues.

### 6.3 Q1. Can we use synthetic clouds to represent real-life blockages in satellite imagery?

**Outcome.** A match with real cloud, within margins fixed in advance, on two checks. A secondary outcome, H1b: on the
test bed, whether cloud's errors lean towards "no change".

**Steps:**
1. **Build the generator and freeze it (week 2).**
   - **Shapes.** HRC_WHU outlines, rescaled to 0.5 m by each image's resolution. **Evidence (today):** the image files
     do not store it. Use the resolution stated in Li et al. (2019) per image or per type. Images whose resolution
     cannot be established are left out. Report the size and edge sharpness of the shapes used (critic C2-5).
   - **Thickness.** Opaque inside the outline, thinning past its edge. The air light and edge fall-off are set from
     the bright cores of the 17 opaque-cloud tiles (label-free).
   - **Family M:** image × t + A × (1 − t), the model behind the dark channel (He, Sun & Tang 2011, unverified).
   - **Family X:** the same blend, plus a cloud texture taken from real HRC_WHU cloud pixels, air light that varies
     across the tile, and clipping. No tool tested on the bed inverts it exactly. **Fallback** if Justin does not allow
     cloud pixels: a procedural noise texture. It is still a process the tools do not invert.
   - **Uniform-haze control:** evidence 03's model, deliberately crude.
   - **Placements:** whole-tile cloud (primary; every object covered, most power); shaped clouds placed by a seeded
     rule (cover and distance from the cloud edge become covariates, not a level to tune).
   - **Frozen** with its settings file and code hash before any change call is scored on it. **Rule:** no realism
     statistic is ever used to set the generator.
2. **Fix the real thin level (week 1).** The median dark-floor rise under real thin cloud, measured on all thin-cloud
   ground, not on any target, before scoring. The 93 strips' value is reported beside it.
3. **Realism check 1, SpaceNet 8, no target (week 3).**
   - Put synthetic cloud on clear tiles. Pick real and synthetic cloudy windows by the same mask rule. Bin them by
     dark-floor rise.
   - Compare three statistics the generator does not set: contrast kept (local spread after over before); pattern
     kept (local before–after correlation); patchiness (the semivariogram of after − before).
4. **Realism check 2, HRC_WHU, per land-cover type (week 3).**
   - Paste synthetic clouds into clear parts of the development images. **Shapes come from other images** than the
     one they are pasted into, so a cloud is never compared with its own copy.
   - Score both single-date masks on these clouds and on the real cloud in the same image, paired by image.
   - **Circularity check:** section 8.
5. **The test bed and H1b (week 4).**
   - Production's fold models score held-out clear tiles whose after images carry cloud.
   - **Grid, fixed in advance:** families M and X × two placements × four levels (one thinner than the real thin
     level, the real thin level, one thicker, opaque) = 16 cells.
   - **Primary, per target:** at the real thin level, family X: recall loss on flooded roads minus loss on dry roads.
     Tile-resampled interval. Beside it: the 24 real trusted flooded roads, as a consistency check only (critic C2-1).
   - **X1 recheck:** the dark-rise flag rate on flooded and dry roads, per level, on family X.
   - Methods tried on the bed (de-hazing) count only on family X and never see the t map.
6. **Buildings** (if they pass week 3): the same bed on clear buildings.

**What counts as "no"** (`selected_questions.md`). The generator misses a margin; or it does no better than the
control. If the control passes too, the checks cannot tell good cloud from bad. Then realism is "untested", not
"shown". A land-cover type that misses its margin is excluded from the claim.

### 6.4 Option for the "handle" step: reference-based (two-date) de-hazing

**Justin's idea** (relayed by the coordinator, 2026-10-23): "since we have two images I want to see what we can do
about clouds when we have another image of the same location, can we align the pixels and potentially know how to
dehaze the cloud".

- **Where it sits is Justin's call.** It could be an extra arm inside Q3, or its own sub-question (say Q3d: *When one
  date is cloudy and the other clear, does fitting the cloudy image to the clear one recover flood calls without
  erasing the flood?*). It is not yet in `selected_questions.md` or the abstract.
- **Plain idea.** One date is cloudy; the other is clear. Where the ground has not changed, the clear date shows what
  the cloudy date should look like. So we can measure how much the cloud dimmed and brightened each place, and undo it.

**The model.**
- The cloudy date: I_c = t·J + L, with L = A·(1 − t). This is the haze model behind the dark channel (He, Sun & Tang
  2011, unverified).
- Where the ground has not changed: J ≈ a·R + b. R is the clear date. a and b are the normal difference between the two
  dates (sensor, sun angle, season).
- So, locally: I_c ≈ α·R + β, with α = t·a and β = t·b + L.
- Fit α and β by a robust local linear regression of the cloudy date on the clear date, from unchanged pixels only.
  Cloud varies smoothly, so α and β are smooth fields.
- **Undo only the cloud, not the normal difference between the dates.**
  - **Inference:** inverting α and β directly would map the cloudy date into the clear date's look. Unchanged ground
    would then match the reference exactly. A corrected tile would look less changed than a clean tile, and the fixed
    model, trained on clean tiles, would lean towards "dry".
  - So a and b are estimated separately: from clear parts of the same tile; or, when the whole tile is cloudy, from
    clear tiles of the same before–after scene pair (training tiles only).
  - Then t̂ = α̂ / â, L̂ = β̂ − t̂·b̂, and the corrected image Ĵ = (I_c − L̂) / t̂.
- **Thin cloud only.** Where t̂ falls below a floor fixed in advance (proposed 0.3; inference, no evidence), the cloud
  is opaque and the road stays "cannot assess". Dividing by a small t̂ only amplifies noise.

**Alignment is not the problem.**
- **Evidence (01):** ground shifts by about 0.6 m after co-registration, with no effect (`sn8_coreg.py` exists).
- **Evidence (critic §3):** relief displacement is 5–13 m on area-0 tanks. **Inference:** tall objects look different
  between the dates. They are outliers that a robust fit drops.

**The catch: real change breaks the reference.**
- Floodwater is a change. If flooded pixels enter the fit, α and β absorb the flood, and the corrected image looks like
  the clear date. **The flood is erased.**
- **Three guards, fixed in advance:**
  1. **Leave the object out.** α and β at a road are fitted only from pixels outside its strip and its 10 m ring. A
     road's own flood can never enter its own fit.
  2. **Robust fit.** Changed pixels are treated as outliers (a trimmed or reweighted regression). **Inference:** haze
     lifts dark pixels and floodwater mostly darkens them, so large negative residuals are dropped first.
  3. **A fit window much larger than a road.** Proposed: 100 m (200 pixels), with one sensitivity size of 50 m. Never
     tuned on outcomes.
- The guards use no change cue from the flood model. That would be circular.
- **Inference: the guards fail where flood covers most of the window.** Then most "unchanged" pixels are flooded. So
  the risk is highest on mostly flooded tiles. Every result is split by tile flood class (dry, partly flooded, mostly
  flooded; the class exists in `sn8_data`).

**Two directions.**
- **After image cloudy, before clear.** The real thin-cloud case, and Q1's bed. The reference is the before image.
- **Before image cloudy, after clear.** Q3's case. The reference is the after image, which holds the flood. The same
  guards apply.

**Comparators.**
- **No correction:** production as it is. Thin-cloud roads are "cannot assess" under the adopted rule; their calls are
  kept for this test, as in Q2 step 1.
- **Single-image de-hazing (He et al.):** exists (`sn8_clouds.dehaze`). **Evidence (01):** on the tile-rule roads it
  found 3 more of the 24 trusted flooded roads under cloud (not significant), and cost 1.7 points on the 766 shared
  roads (p 0.15).
- **The reference fit without its guards** (an ablation). It shows how much flood the guards save.
- **For the before-cloudy direction:** Q3's after-only call, and abstaining.
- **On the bed only:** the clean image, as an oracle upper reference.
- **Optional:** local dark-object subtraction after Makarau et al. (2014, unverified; evidence 02, abstract only). It is
  single-image and was built for uneven haze on VHR imagery.

**Circularity.**
- Family M is I = t·J + A·(1 − t). With the before image as reference, it fits the method's own model exactly. The
  method would undo it almost perfectly. **A test on family M is circular.**
- **Rule:** the method is scored on family X only (texture from real cloud pixels, air light that varies across the
  tile, clipping). Results on M appear only as an upper bound, marked circular.
- **Inference:** on the bed only the cloud is synthetic. The floods and the before–after differences are real. So the
  risk of erasing change is tested on real floods.
- **Inference:** statistics that compare the corrected image with its reference (pattern kept, say) are pushed up by
  the fit itself. They cannot judge this method, so they are not used for it.

**Outcomes and tests.**
- **Primary** (bed, family X, real thin level, whole-tile cloud): balanced accuracy of the reference arm minus the
  single-image de-hazing arm. Paired on the same roads, tile-resampled.
- **Recovery:** the share of cloud's loss won back: (corrected − cloudy) over (clean − cloudy), in balanced accuracy.
- **Change kept** (diagnostic, bed only): on flooded strips, the after − before grey difference after correction, over
  its clean value. Near 1, the flood is kept. Near 0, it is erased. Shown with pictures.
- **Safety on clear roads** (real images, no cloud added): run the correction on the tiles of the 769 clear roads.
  Flooded found must not drop by more than 1.5 points (upper bound), and balanced accuracy likewise. Split by flood
  class.
- **Real thin cloud:** flooded found on the 24 trusted flooded roads, against no correction and against He de-hazing.
  Reported, not tested: only effects of about 25 points or more can show (evidence 03). Dry calls under real cloud
  cannot be scored (untrusted labels).
- **The prototype now running** (coordinating session, development data) already looks at these 24 roads and at clear
  flooded roads. Its numbers are not in the evidence files and are not used here. **When logged, they count as
  exploratory**, because the method's settings may be shaped by that look. The formal tests are the bed (family X) and
  the sealed look.

**What counts as "no."**
- **The safety check fails:** the correction erases floods on clear tiles. Then the method is rejected, whatever it does
  under cloud.
- **Or** the primary interval includes 0 or lies below it: no better than single-image de-hazing.
- **Or** it works on family M but not on family X.

**What it would add to Q2 (inference).** If it passes, a thin-cloud road could carry a corrected flood call. Q2's S2
and S3 would then also be scored on corrected calls. Q2's scope does not change unless Justin says so.

**Limits.**
- The two-date fit's errors cannot be checked on real cloud: there are no real two-date cloud labels (critic C4-1).
  Its real-cloud evidence is recall on 24 trusted flooded roads only.
- This is the same validation limit that sank the critic's rejected C4 (a two-date visibility test). The difference:
  this method is scored on flood calls against published labels, not on a visibility class.
- **Prior work.** Hagolle et al. (2010, unverified; evidence 02, catalogue snippet only) use two dates to *detect*
  cloud, not to remove it. Reference-based de-hazing was not searched for. **Inference:** similar multi-date methods
  likely exist. No novelty is claimed.

**Cost (inference, at about 45 min of DINOv2 per cell).** The corrected images are new images, so their cues are
recomputed.
- After-image direction, family X, four levels, whole-tile cloud: about 3 h.
- Before-image direction, the same: about 3 h.
- The 39 real thin-cloud tiles: about 10 min. The clear-road safety check: about 45 min.
- The fits themselves run on CPU.

---

## 7. Baselines and comparators

| Question | Comparator | Why |
|---|---|---|
| Q2 | The usual report: one accuracy over all labelled roads, missing read as dry, no cannot-assess layer | The thing H2a tests |
| Q2 | The same model's calls on clear roads | The clear-sky error each hidden-road statement is judged against |
| Q2 | Production 83.0% on 798 roads; always "flooded" 55.3% | Evidence 01 |
| Q3 | Two-date production model, no routing | `selected_questions.md` |
| Q3 | Two-date model without DINOv2 cues | Fair match for the after-only model |
| Q3 | Abstaining on before-cloudy roads, with its coverage loss | What a cautious map would do |
| Q3 | Oracle routing | Upper reference for H3c |
| Q3 | Always "flooded" (balanced accuracy 0.50 by definition) | Floor for the go/no-go |
| Q1 | Uniform-haze control | Must fail at least one check |
| Q1 | Real cloud: SpaceNet 8 thin cloud found by the mask; HRC_WHU expert masks | What "represent" is measured against |
| Q1 bed | Each model's clean scores on the same objects | Paired by object |
| Option §6.4 | No correction; single-image He de-hazing; the reference fit without its guards; the clean image (bed only) | §6.4 |

---

## 8. Error ceilings and margins, fixed in advance

**Proposed now. Frozen in the pre-registration at the end of week 1. Justin may change any of them before then.**

**A derived reference: the clear-sky error of the map.** *Inference (arithmetic on evidence 01).* On the 798 assessable
roads, the tile rule + road rule scored 81.8% accuracy and found 87.8% of flooded roads; 55.3% are flooded. So about
441 flooded and 357 dry; about 387 floods found and 54 missed; about 266 dry roads kept dry and 91 false floods. Then:
- "flooded" calls wrong: about 19% (91 of 478);
- "dry" calls wrong: about 17% (54 of 320);
- balanced accuracy: about 0.81.

Production now scores 83.0%, so its rates are likely a little lower. Recompute them from the logged calls in week 1.

| Rule | Proposed value | Why |
|---|---|---|
| **Tier interval** (S1–S3) | One-sided upper bound of a 98.3% tile-resampled interval (5% split over three statements; Bonferroni) | Three statements get a chance to pass; adjust so one does not pass by luck |
| **S1** missed hidden | Upper bound ≤ 30% | Most hidden roads must be marked. **Evidence (01):** the one real-cloud figure, dark-mask recall 0.68 on HRC_WHU (pixel level), sits at this line. So the test can fail; it is not set to pass |
| **S1** false hidden (clear roads flagged) | Upper bound ≤ 10% | **Evidence (01):** the road rule flags 93 of 891 roads (10.4%). A 10% false-hidden rate would discard as many clear roads as the rule flags in all |
| **S2** "flooded" calls wrong | Upper bound ≤ 25% | Clear sky is about 19% (derived). **Evidence (03):** bed intervals at thin levels are about ±4 to ±7 points. A statement as good as clear sky then has an upper bound near 23–26%, so it can just pass. A 20% ceiling could be failed by noise alone |
| **S3** "dry" calls wrong | Upper bound ≤ 25% | Clear sky is about 17% (derived). Same reasoning |
| **S4, S5** | Range only, by design | No truth under cloud (critic X3). The range's width is the reported number |
| **"Truly hidden" on the bed** | The thinnest grid level where family X's error rises more than 1.5 points above clean, with at least 20% of the strip covered | Defines hidden by its effect on the call, not by the mask's own reading |
| **Q2a** inflation | Shown if the lower bound > +1.5 points. "No inflation" if the whole interval lies inside ±1.5. Otherwise inconclusive | **Evidence (03):** paired intervals are about ±1.1 to 1.3 points |
| **Q2b** | Exact test stratified by tile. Described only if fewer than 10 mixed tiles carry a flooded label | Tiles with no flooded label add nothing to a within-tile test. **Evidence (critic):** 5 informative opaque tiles were too few |
| **Q3 after-only go/no-go** | Lower bound of clean balanced accuracy ≥ 0.60 | Any constant call scores 0.50. The two-date model is about 0.81 (derived). This asks only whether the after image carries signal at all |
| **Q3 H3a** | Lower bound of (after-only − two-date) > 0 at opaque cover | `selected_questions.md` |
| **Q3 H3b** | Tested only if its minimum detectable difference is ≤ 15 points. Limit shown if the lower bound of (after-only − two-date false-flood rate near water) > 0 | **Evidence (03):** group gaps carry ±4 to ±12 points on large groups. **Evidence (v3, dev log 2026-10-11):** state-reading effects in the main project were large (72–89% of damaged buildings flagged on a no-change pair) |
| **Q3 H3c** | Clean-road cost upper bound ≤ 1.5 points; recovers at least half the oracle gain | **Evidence (03):** noise about 1.5 points; v3 |
| **Q1 check 1** | Per statistic and rise bin: the interval of (synthetic − real) median lies within ± half the real cloud's own effect (real thin cloud − clear ground, same statistic) | No values for these statistics exist in the evidence. A margin scaled to the real effect is fixed before any synthetic cloud is made. The synthetic cloud must sit closer to real cloud than halfway to clear sky |
| **Q1 check 2** | Per land-cover type, both masks: the interval of the per-image F1 difference (synthetic − real) lies within ±0.10 | **Evidence (01):** dark-mask F1 is 0.66 (urban) to 0.78 (vegetation), 0.74 on water, 0.48 on barren. A 0.10 margin is smaller than the gap between ground types |
| **Q1 control** | Must miss at least one margin | If it passes, the checks cannot discriminate |
| **Circularity flag on family M** | If dark-mask F1 on M exceeds F1 on real cloud by more than 0.10 (lower bound > 0), M is too close to the mask's model. M is then left out of every realism and method claim | Critic C2-1, C2-2 |
| **Q1 H1b** | Lean shown if the lower bound of (recall loss − dry-kept loss) > 0 at the real thin level, family X | `selected_questions.md` |
| **Buildings go/no-go (end of week 3)** | At least 150 clear flooded buildings on at least 50 tiles, **and** clean balanced accuracy lower bound ≥ 0.60 | Roads give 433 flooded on 190 tiles. **Evidence (03):** 24 flooded roads on 39 tiles could show only about 25-point effects. A third of the roads' count still allows moderate effects (inference) |
| **Blocked-fold block size** | Side = the range of the semivariogram of tile flood share on the tile grid, rounded up, at least 3 tiles | A rule fixed now; the number comes from the data in week 1. Three tiles covers the 8-neighbour ring the neighbour check uses |
| **Option §6.4, safety** | On clear tiles with no cloud added: loss of flooded found, and of balanced accuracy, upper bound ≤ 1.5 points | **Evidence (03):** the noise is about 1.5 points. A correction must not cost clear roads more than that |
| **Option §6.4, primary** | Lower bound of (reference arm − He de-hazing) balanced accuracy > 0, family X, real thin level | Single-image de-hazing already exists, so a new method must beat it |
| **Option §6.4, recovery** (secondary) | At least half of cloud's loss won back | Same bar as H3c's half of the oracle gain (v3) |
| **Option §6.4, settings** | Fit window 100 m (sensitivity 50 m); opaque floor t̂ = 0.3 | Inference; no evidence. Fixed before scoring, never tuned on outcomes |

---

## 9. Power

**The rule of thumb used here (Inference; needs citation).** At 80% power and a two-sided 5% test, the smallest
detectable difference is about 1.43 times the half-width of a 95% interval.

| Test | Objects and tiles | Interval known? | Smallest detectable difference | Plan |
|---|---|---|---|---|
| Q2a inflation | 798 vs 1,037 roads; 217 tiles | **Evidence (03):** ±1.1 to 1.3 points (paired, same roads) | About 1.6–1.9 points. To show "more than 1.5", the true rise must be about 3 points (inference) | Tested; may be inconclusive (v3) |
| Q2 real recall under thin cloud | 24 roads; 39 tiles | **Evidence (01):** −0.54 to 0.00 | **Evidence (03):** about 25 points or more. Inference: nearer 40 for 80% power | Reported, not tested |
| Q2 opaque labels | 3 flooded labels; 5 informative tiles | — | — | Described only |
| Q2b | Mixed tiles: count unknown | — | — | Count in week 1 |
| Q2 S2, S3 on the bed | About 769 roads; 190 tiles | Not computed | Inference: ±4–6 points | Compute in week 1 |
| Q1 H1b | 433 flooded + 336 dry; 190 tiles | **Evidence (03):** ±4 (t 0.9), ±7 (t 0.8), ±12 (t 0.7), for flag-rate gaps between the same groups | About 6–10 points at thin levels | Tested |
| Q1 check 2 | 24 images per type | Unknown | Compute from the per-image F1 spread already in `cloudref_test.ipynb` | If it exceeds 0.10, "match not shown" for that type |
| Q3 H3a | 769 roads; 190 tiles | **Inference (v3):** wider than ±1.3, because two different models disagree more | Compute from after-only vs production on clean roads | Large effect expected at opaque cover (inference) |
| Q3 H3b | Unknown | — | — | Tested only if ≤ 15 points |
| Buildings | Unknown | — | — | Go/no-go |
| Option §6.4, primary | 769 roads; 190 tiles | Not computed. **Inference:** two corrections of the same images may disagree on few roads, which narrows a paired interval | Compute in week 1 from the He arm's logged calls | Tested on the bed |
| Option §6.4, real recall | 24 roads; 39 tiles | As above | About 25 points or more (evidence 03) | Reported; exploratory, as the prototype has seen these roads |

**Rules:**
- **Tile-resampled intervals are the primary test everywhere** (critic X2). McNemar is secondary only, because it
  treats roads as independent.
- **Every result shows its tile count and its smallest detectable difference.**
- **Gate 0 (end of week 1):** any test whose smallest detectable difference exceeds its margin is relabelled
  "descriptive" before any cloud outcome is scored.
- **The margin rules are conservative.** "Match" and "reliable" need an interval inside a limit. Low power then gives
  "not shown", never a false "match". A "no" from a test that is too weak is reported as "inconclusive".
- **One primary test per question.** Secondary tests are Holm-adjusted within their question.

---

## 10. Spatial assumptions and GeoAI checks

### 10.1 CRS, units and scale

- **CRS.** SpaceNet 8 tiles are warped to one 0.5 m UTM grid (evidence 01). Units are metres. HRC_WHU has no CRS
  (evidence, today); it supplies cloud shapes, textures and mask scores, never locations.
- **Scales in play:**

| Scale | Size | Source |
|---|---|---|
| Pixel | 0.5 m | Evidence 01 |
| Road strip | About 5 m either side of the centreline | `selected_questions.md` |
| Ring around a road or building | 10 m | `sn8_roads.RING_M` |
| Dark-channel window | 41 pixels (20 m) | `sn8_clouds.DARK_WIN` |
| DINOv2 patch | 14 pixels (7 m) | `sn8_dino.PATCH` |
| HRC_WHU pixels | 0.5–15 m | Evidence 02 |

- **Inference (critic X1):** the 20 m window is wider than the strip. A minimum filter moves cloud edges inwards by up
  to the window, and cloud strips narrower than it vanish. The bed's false-hidden rate and the covariate "distance
  from the cloud edge" measure this.
- **Inference (critic C2-5):** an outline drawn at 15 m and pasted at 0.5 m would be up to 30 times too big and too
  smooth. Hence rescaling by resolution, and dropping images whose resolution is unknown.
- **Inference (v3):** a small house covers only a few 7 m DINOv2 patches. Buildings may carry weaker DINOv2 signal.

### 10.2 Tile clustering

- **Evidence (critic X2):** the recall drop under thin cloud is p = 0.010 by road (Fisher) but its tile interval
  reaches 0. Treating roads as independent overstates the evidence.
- So the tile is the resampling unit for SpaceNet 8, and the image for HRC_WHU.
- **Inference:** roads and buildings on one tile share cloud and flooding. Two targets on the same tiles are not two
  independent samples, and not two events.

### 10.3 Neighbouring tiles across folds (critic X4)

- **Evidence (critic §3):** folds are shuffled groups of tiles, so a tile's neighbours usually fall in other folds.
  **Inference:** a road's model is often fitted on the tile next door, which shares the flood pattern and the cloud.
  This can inflate absolute scores, and can make cloudy tiles easy to call from their neighbours.
- **Primary folds stay as they are.** Production and every logged result use them. Changing them would break the
  comparison.
- **One sensitivity run per frozen design (week 6), three schemes:**
  1. **Blocked folds:** square blocks of tiles on the grid (block side from section 8), assigned to five folds
     stratified by flood class. Otsu thresholds re-learned inside each fold.
  2. **Buffered folds:** the shuffled folds, but training drops every tile within one tile (the 8 around it) of any
     held-out tile.
  3. **Leave one area out:** fit on south (105 tiles), score on west (121), and the reverse. A stress test of
     transfer, not a decision rule.
- **What is reported:** absolute scores and each primary difference under all four schemes, in one figure.
- **What would weaken a claim:** a primary difference that changes sign or loses its interval under blocked or
  buffered folds.
- **Cheap:** the cues are cached, so these runs refit forests on CPU only.

### 10.4 Leakage

- No road is scored by a model that saw its tile (exists).
- No model is trained on synthetic cloud. Synthetic cloud never trains a detector that is then scored on synthetic
  data (critic C2-6).
- Generator settings come from label-free opaque cores, never from the realism statistics.
- HRC_WHU shapes are pasted into other images than their own.
- The loaders refuse held-out data unless `allow_held_out=True` is passed (exists in `sn8_clouds`, `sn8_cloudref`,
  `sn8_dino`). The sealed look is the only call that sets it.

### 10.5 Sampling bias, temporal alignment and transfer

- **Evidence (critic):** cloud is clustered in areas 0 and 2. Real thin cloud was picked by the dark-rise mask.
- **Inference:** the bed uses clear roads. Clear roads may differ from the ground under the clouds (other
  neighbourhoods, other flood depths). The bed's numbers carry over to cloudy places only by assumption. Report the
  flood share and cue distributions of clear roads beside those of thin-cloud roads.
- **Temporal.** Before and after images come from different dates and satellites. **Evidence (01):** ground shifts by
  about 0.6 m after co-registration, with no effect. **Inference (v3):** Q3's realism verdict comes from after-image and
  single-date cloud, and is carried over to before images taken on another date.
- **Transfer.** One event, one sensor, two areas, at most two targets. Five land-cover types for the cloud itself
  only. Claims stay there. Any wider claim needs Justin's approval (AGENTS.md rule 9).

---

## 11. Threats to validity

| Threat | Claim it hits | Evidence that would weaken the claim | What the plan does |
|---|---|---|---|
| No truth under cloud (critic X3) | Q2 S2–S5 | — (cannot be had within the rules) | Ranges; tiers; tipping points |
| "Missing = dry" in clear sky is untested | Q1 H1b; Q3 H3a, H3b; Q2 S2, S3 | A small tipping count: a few percent of wrong dry labels would flip the result | Tipping counts for every result that uses clear dry labels (section 12) |
| Synthetic cloud is not like real cloud | Q2's synthetic tier; Q3's thin levels | The control passes too; family X fails; the HRC_WHU test images fail | Two checks, a crude control, per-type claims, a sealed re-check |
| Circular haze (family M) | Any realism or method claim on M | M passes where X fails; the circularity flag fires | Method claims on X only; M flagged and dropped if circular |
| Real thin cloud was chosen by the mask | Check 1; the real thin level | Synthetic matches SpaceNet 8 thin cloud but not HRC_WHU's expert cloud | Check 2 uses expert masks, not the mask; "truly hidden" set by effect on the call |
| Two-date mask never checked on real two-date labels | S1's thin half | Stays "synthetic only" whatever the bed shows | Stated in the tier |
| Low power (critic X2) | Everything on real cloud | Smallest detectable difference above the effect of interest | Gate 0; "inconclusive" wording; detectable differences shown |
| Neighbour leakage (critic X4) | Absolute scores; differences | A primary difference changes under blocked or buffered folds | Three-scheme sensitivity run |
| Scale mismatch (HRC_WHU 0.5–15 m; 20 m window vs 5 m strip) | Q1 realism; S1 edges | Results change when only images near 0.5 m are used | Rescaling; drop unknown-resolution images; report shape sizes |
| Clear roads differ from cloudy ground | The bed's link to real cloud | Clear and thin-cloud roads differ in flood share or cues | Report both distributions |
| After-only model lacks DINOv2 | Q3 H3a | The gap vanishes against the two-date model without DINOv2 | Second comparator |
| The flag fires on floodwater | Q3 H3c | High flag rate on clean flooded roads | Flag rates on clean roads reported |
| The water mask is unmeasured | Q3 H3b | Results change with the water threshold | Threshold fixed on training tiles; H3b is secondary |
| One event, one sensor (critic X7) | Every "general" word | Germany, if spent, disagrees | Scoped claims; Germany is Justin's call |
| One model plays every agent role (rule 4) | Every judgement in this plan | — | Justin's review, the pre-registration, tests in code, the sealed look |
| Reference de-hazing erases real change (option §6.4) | Any gain it shows | Flooded found drops on clear tiles; "change kept" well below 1, worst on mostly flooded tiles | Three guards; the safety check is a veto; split by flood class |
| Reference de-hazing maps one date into the other's look (option §6.4) | Its calls lean "dry" | Corrected tiles score more "dry" calls than clean tiles | Undo only t and L; a and b estimated from clear ground |
| The prototype looked first (option §6.4) | Its real-cloud numbers | — | Those numbers are exploratory; the bed and the sealed look are the tests |
| Choices made after looking | Everything | — | Pre-registration; stop rule (section 16) |

---

## 12. The critic's open points

### Power (X2, C3-3)
- **What the plan does.** Tile-resampled intervals first. Every result shows its tile count and smallest detectable
  difference. Gate 0 turns weak tests into descriptions before scoring. The margin rules fail safe: low power gives
  "not shown", never a false pass.
- **Where power comes from.** **Inference:** the synthetic bed (769 roads, 190 tiles) is where most power lives. Real
  cloud gives 24 trusted flooded roads, so real-cloud numbers are reported, not tested.
- **What remains.** H2a sits near the noise. Q1's per-type checks have 24 images each.

### Circularity of the synthetic haze (C2-1, C2-2)
- **Family M** is the dark channel's own model. The dark mask, the dark-rise mask and He de-hazing all invert it. So
  scores on M flatter these tools.
- **Family X** adds real cloud texture (or the procedural fallback), air light that varies, and clipping. Every method
  claim uses X only.
- **The circularity flag** (section 8) drops M from realism claims if the dark mask finds M much more easily than real
  cloud.
- **Realism statistics** (contrast, pattern, patchiness) are things the generator does not set. They are never used to
  tune it. The dark-floor rise is used only to bin, never to judge a match.
- **The thickness levels** are defined in the mask's own units (dark-floor rise), which is circular. So levels are also
  reported in t, and "truly hidden" is defined by the effect on the flood call.
- **The real thin cloud** on SpaceNet 8 was chosen by the mask. Check 2 uses HRC_WHU's expert masks, which were not.
- **The control** must fail. If it passes, realism is "untested".
- **Reference de-hazing (option §6.4)** fits the same linear model that builds family M, so it is scored on family X
  only. On M its results are an upper bound, marked circular.

### Untrusted dry labels (X5, C3-1, C4-2)
- **Under real cloud, dry labels are never truth.** Only trusted flooded labels are scored there (recall). Agreement
  with missing labels is called agreement, never accuracy. It appears only in H2a, where it is the thing being
  measured.
- **The 10 handed-back roads** (critic X5) are not used as evidence.
- **In clear sky, "missing = dry" is an assumption.** For each result that uses clear dry labels (H1b, H3a, H3b, S2,
  S3), report a **tipping count**: how many dry labels would have to be wrong, and fall the worst way, to flip it.
  This is a calculation. No label is changed.
- **A descriptive check (published labels only).** Are clear "dry" roads that the model calls flooded with high
  confidence clustered beside labelled flooded roads? **Inference:** clustering would hint at missed labels in clear
  sky. Crops of such roads are shown as pictures only. They are never relabelled or counted.
- **HRC_WHU** labels thin cloud only where the ground cannot be seen (evidence 02). So its "real cloud" truth is itself
  conservative. Noted in check 2.

### Neighbour leakage (X4)
- Section 10.3: blocked, buffered and leave-one-area-out runs for every frozen design, with the block size set by a
  rule fixed now.
- **Inference:** the sealed test tiles sit among the development tiles, so the sealed look shares this leak. Only
  leave-one-area-out, and Germany if spent, test a new place.

### The critic's other points, briefly
- **X1 (mask bias by flood state).** **Evidence (03):** not present under uniform haze; under thick haze the mask flags
  flooded roads more, not less. The bed re-checks it on family X.
- **X6 (novelty).** None claimed. Every gap stays "not found in the sources read".
- **X7 (no second dataset).** Claims are scoped to Louisiana-East, Maxar greyscale, Ida.

---

## 13. AI-assisted coding and analysis tools

- **Claude Code (Anthropic)** writes the analysis code, runs it, builds the figures and drafts text, under Justin's
  direction. Justin makes and records every decision (`decision_log.md`).
- **The agent roles** (question agent, critic, methodology, writer, validation) run on the same model. Their agreement
  is not independent validation (AGENTS.md rule 4). The checks that are independent of the model: Justin's review,
  the pre-registration, tests written into the code, and the sealed look.
- **Code and runs.**
  - The private repository Jrog378/GeoAI-Roads (evidence 01).
  - Every run as a Tilt resource (project rule), in the background for long GPU passes.
  - Every run logged with its code hashes (`sn8_results.py`). Seed 662 throughout.
  - Production frozen in `production.json`.
- **Libraries in the existing code:** NumPy, SciPy, pandas, scikit-learn (random forest, `StratifiedGroupKFold`),
  matplotlib, and DINOv2-L with registers (`vit_large_patch14_reg4_dinov2.lvd142m`) from local weights.
- **DINOv2** detects change, inside the frozen model only. **Gemma** is not used in any score, label, tier or decision.
  If used at all, it only writes captions for figure crops, marked as AI-written (the CSI 709 thread).
- **The paper's AI-use statement** names general task types (writing and running analysis code, making figures,
  drafting and editing text, summarising literature). It names no files, and it stays truthful.

---

## 14. Figures (numbers come with pictures)

Every figure is built from development data, except those marked "sealed". No sealed image is shown before the look.
Error crops are picked by a rule fixed in advance: for example, the 12 most confident wrong calls per cell, ordered by
tile id.

| # | Figure | Numbers it carries | Question |
|---|---|---|---|
| 1 | Study area: development tiles by area, clear, thin and opaque roads; sealed tiles as grey outlines only | Tile and road counts | All |
| 2 | Label coding under cloud: example tiles with "yes" and missing labels on cloudy and clear roads | H2b odds ratio and tile count | Q2 |
| 3 | The masks: before, after, bright, dark and dark rise on example tiles; HRC_WHU per type with the expert outline | Mask scores per type | Q1, Q2 S1 |
| 4 | Real against synthetic cloud at 0.5 m: family M, family X and the control beside real cloud at matched rise, per land-cover type | — | Q1 |
| 5 | Realism checks: statistic distributions by rise bin, and per-type F1 differences, with the margins drawn | Check 1 and 2 verdicts | Q1 |
| 6 | Dose and response on the bed: recall and dry-call rate against thickness, per family and placement, with the real anchor | H1b | Q1 |
| 7 | What DINOv2 sees: change-cue heatmaps, clean against clouded | — | Q1, Q3 |
| 8 | Before-image cloud: clouded before, after, two-date call, after-only call; balanced accuracy against thickness with the crossover | H3a | Q3 |
| 9 | Permanent water: crops of dry roads near water before the storm, with both models' calls | H3b | Q3 |
| 10 | The tier table as a figure, and the cannot-assess map by area beside the assessed flood share | S1–S5; flooded-length ranges | Q2 |
| 11 | Optional risk–coverage curve, classifier fixed | Coverage and trusted-flooded misses | Q2 |
| 12 | Sensitivity: each primary difference under shuffled, blocked, buffered and leave-one-area-out folds | Differences with intervals | All |
| 13 | Sealed look: the primary results on the test tiles and HRC_WHU test images | Sealed numbers | All (sealed) |
| 13a | Reference de-hazing (option): clear reference, cloudy date, corrected date, clean date (bed only); the fitted t and L fields; the pixels left out of the fit; flooded-road crops before and after correction | Recovery, change kept, the safety check, by flood class | Option §6.4 |
| 14 | Error crops per primary cell | — | All |

---

## 15. The eight-week plan

| Week | Dates | Work | Output | Gate |
|---|---|---|---|---|
| **1** | 26 Oct – 1 Nov | Justin's rulings via the request page (section 19). Counts and power on development data, with no cloud outcome scored: buildings and their `flooded` coding (existing counter); SpaceNet 8's definition of a flooded building (Hänsch et al. 2022); HRC_WHU resolutions; the real thin level; mixed tiles (Q2b); dry roads near permanent water (H3b); interval widths; block size. Tilt resources set up. **Pre-registration written and frozen mid-week.** Then Q2's real-data parts: calls on hidden roads, H2a, H2b, real recall, ranges | Frozen pre-registration; counts table; Q2 real-data results | **Gate 0 (power):** weak tests become descriptive |
| **2** | 2 – 8 Nov | Generator (families M and X, control, two placements, before or after image), shape pool, frozen on Friday. After-only road model and its clean score. Building table started: owner maps, cues, clean DINOv2 pass (about 50 min). Methods section drafted from the pre-registration | Frozen generator with its hash; after-only clean score | **Gate 1:** after-only go/no-go (roads) |
| **3** | 9 – 15 Nov | Realism checks 1 and 2, the control, the circularity flag. Building model fitted and scored on clear buildings. Bed DINOv2 passes start in the background | Realism verdict per type; building verdict | **Gate 2: buildings in or out.** The realism verdict sets how later tiers are labelled (not a stop) |
| **4** | 16 – 22 Nov | The bed per target: 16 cells (about 12 h of GPU for roads). Q2's synthetic tier: S1 two-date half, S2, S3. X1 re-check on family X. Cover and edge distance as covariates | Dose and response; Q2 synthetic numbers | — |
| **5** | 23 – 29 Nov (Thanksgiving) | Q3: four before-image levels (about 3 h of GPU), the leak check, H3a; water mask and H3b; flag and H3c if time allows | Q3 results | Cut list applies if behind |
| **6** | 30 Nov – 6 Dec | Q2 assembly: tiers, ranges, flooded length per area, tipping points, map. Sensitivity runs (blocked, buffered, leave one area out) for every frozen design. All development figures. **Everything frozen on Friday**, with code hashes logged | Full development results; frozen bundle | **Gate 3: freeze** |
| **7** | 7 – 13 Dec | **The one batched sealed look on Monday**, logged once. Sealed figures. Results and discussion drafted. Critic and validation agents review against the evidence. Justin verifies the references; library search before any novelty wording | Sealed results; full draft | — |
| **8** | 14 – 18 Dec | Revisions; limitations; AI-use, data and licence statements; Justin's final read. **Submit Friday 18 December** | Submitted paper | — |

**Gates in more detail:**
- **Gate 0 (week 1).** Power, as in section 9. No outcome is scored before the pre-registration is frozen.
- **Gate 1 (week 2).** If the after-only model fails its go/no-go, Q3 becomes: "the after image alone cannot map roads
  here; the two-date model's loss under before-image cloud is reported, with abstaining as the only fallback".
- **Gate 2 (week 3).** Buildings stay only if they pass section 8's rule **and** the table is on time. Otherwise the
  paper says "shown for one target type; general in design only". If realism fails, the plan goes on. The bed's numbers
  are then labelled "synthetic only, realism not shown".
- **Gate 3 (week 6).** Nothing is added after the freeze.

**Where the reference de-hazing option fits, if Justin adopts it:**
- **Week 1:** its settings (guards, window, floor) go into the pre-registration. The prototype's results are logged as
  exploratory.
- **Week 2:** the prototype moves into the repo with tests and is frozen with the generator. The clear-road safety
  check runs (real images; about 45 min of GPU). **Its veto applies here:** if it erases floods on clear tiles, the
  option stops.
- **Week 4:** the after-image direction on the bed, family X, four levels (about 3 h of GPU).
- **Week 5:** the before-image direction, with Q3 (about 3 h).
- **Week 6:** its fold-scheme runs. It joins the sealed look only if frozen by then.

**Cut list, in order, if the plan slips** (Justin may reorder it):
1. H3c routing.
2. The shaped-cloud placement (keep whole-tile cloud).
3. The reference de-hazing option's before-image direction (keep the after-image direction).
4. Buildings.
5. Q3's thin levels (keep opaque cover).
6. The optional risk–coverage figure.

**Never cut:** the pre-registration, tile-resampled intervals, the blocked-fold run, the sealed look, and the figures
for the primary results.

**Compute.** *Inference from v3's timing (about 14 s of DINOv2 per tile).*
- About 45 min per grid cell over 190 tiles.
- Q1's 16 cells: about 12 h. Q3's 4 levels: about 3 h. The clean building pass: about 50 min.
- The sealed look: 40 tiles × 20 cells, about 3 h.
- The reference de-hazing option, if adopted: about 7 h more in all (§6.4).
- Pooling roads and buildings from one pass needs a code change (v3 §10 item 9).
- The fold-scheme runs refit forests on cached cues, on CPU.

---

## 16. Stopping and decision rules

- **Stop rule.** No new statistic, grid cell, target, metric or fold scheme after looking at the outcome it would
  affect. Anything added later is labelled exploratory.
- **A failed gate changes the claim, not the rule.**
- **Production stays frozen** for the paper. Any confirmed gain found along the way (routing, say) goes through the
  staged-promotion rule after the paper, not during it.
- **The sealed look happens once.** Its results are reported whatever they are. Nothing is re-tuned afterwards.
- **One primary test per question.** Secondaries are Holm-adjusted within their question. The tier rule uses 98.3%
  bounds.

---

## 17. Checklist against the methodology role

| Required component (`methodology_agent.md`) | Where |
|---|---|
| 1. Unit of analysis | §4 |
| 2. Study area and temporal scope | §3.1, §10.5 |
| 3. Dependent or target variables | §6 (each question's outcome; §6.4 for the option) |
| 4. Explanatory or predictor variables | §6 (exposure, arms, covariates); the flood model's cues are fixed (§1) |
| 5. Data provenance and resolution | §3.1, §10.1 |
| 6. Preprocessing | §3.2, §6.3 step 1 (greyscale, 0.5 m grid, Otsu thresholds, rescaled shapes) |
| 7. Model or algorithm | §1, §6 |
| 8. Baseline or comparator | §7 |
| 9. Spatial train/test or cross-validation | §3.2, §10.3 |
| 10. Uncertainty and sensitivity | §9, §10.3, §12 (tipping counts) |
| 11. External validation | §3.3. There is none unless Justin spends Germany. The sealed test tiles are held out, not external |
| 12. Stopping and decision criteria | §8, §15 (gates), §16 |
| GeoAI checks: CRS, autocorrelation, leakage, scale, MAUP, sampling bias, transfer | §4, §10 |

---

## 18. Assumptions most likely to change the conclusion

1. **"Missing = dry" holds in clear sky.** The bed, Q3 and S2–S3 all rest on it. If analysts also skipped flooded roads
   in clear sky, every error rate on clear roads is off.
2. **Synthetic cloud stands in for real thin cloud** (Q1, family X). If not, Q2's synthetic tier and Q3's thin levels
   say nothing about real cloud.
3. **The dark-rise mask's real errors resemble its synthetic ones.** No real two-date cloud labels exist to check this.
4. **Neighbour leakage affects the arms equally.** If not, differences shift under blocked folds.
5. **HRC_WHU shapes can be rescaled to 0.5 m.** The files do not store their resolution.
6. **Q3's opaque level depends little on realism** (v3). Opaque cloud removes the ground whatever its texture.
7. **The ceilings in section 8 are the right ones.** A ceiling 5 points lower or higher could move S2 or S3 between
   tiers. That is why they are frozen before scoring and every interval is shown.
8. **For the reference de-hazing option: a fit on unchanged ground can tell cloud from flood.** Where flood fills most
   of the fit window, it cannot. Then the method erases the very change it is meant to keep.

---

## 19. Unresolved issues and decisions for Justin

**Decisions (one at a time, on the request page):**
1. **Synthetic truth** as a scoring truth (Q1's checks, Q2's synthetic tier, Q3's flag). If no, the synthetic tier is
   empty.
2. **HRC_WHU outlines and cloud pixels** for the generator. If pixels are refused, family X uses procedural texture.
3. **The ceilings and margins** in section 8: accept or change before the end of week 1.
4. **The sealed look:** add the north negative set? Germany?
5. **The main project's post-only result** (Hurricane Ian, dev log 2026-10-11) as evidence in Q3 (v3 §10 item 6).
6. **The conference rule.** The project keeps JIF > 4 journals or company papers; AGENTS.md also accepts major
   conferences (Geifman & El-Yaniv 2017).
7. **HRC_WHU crops in a journal figure** (Google Earth imagery). Permission or attribution terms are not in the files.
8. **The target journal** (JIF ≥ 4).
9. **Reference-based de-hazing (§6.4):** adopt it? If so, as an arm inside Q3 or as its own sub-question (Q3d)? And
   where does it sit in the cut list?

**Facts still unknown:**
- Each HRC_WHU image's resolution. The image files do not store it (checked).
- Development building counts, their `flooded` coding, and SpaceNet 8's definition of a flooded building.
- The real thin level; the mixed-tile count (Q2b); the size of the permanent-water group (H3b); the interval widths in
  section 9.
- The 1,080 label rows against 1,037 roads (critic §3).
- Whether evidence 03's haze script still exists. It sat in a past session's scratchpad.
- The reference de-hazing prototype's code location and settings. Its results are not in the evidence files.

**Citations.** Methods used here but not cited in the evidence files need a citation before the paper: the stratified
exact test (Mantel–Haenszel type), the semivariogram, margin-based (equivalence) testing, the tile block bootstrap,
Bonferroni and Holm, and the power approximation. He, Sun & Tang 2011 was read at metadata level only. Olofsson et al.
2014 has no JIF recorded and its claim match is unchecked (critic C3-6).

## 20. Suggested next scientific action

1. **Justin rules on decisions 1–3** (synthetic truth, HRC_WHU use, the ceilings). These block the pre-registration.
   Decision 9 (reference de-hazing) should come before the pre-registration is frozen too, so its settings can go in.
2. **Run the week-1 counts through Tilt**, on development data, with no cloud outcome scored: buildings, HRC_WHU
   resolutions, the real thin level, mixed tiles, the water group, the interval widths, the block size.
3. **Write and freeze the pre-registration** from sections 6, 8, 9 and 16, with the numbers filled in.
4. **Then start Q2's real-data parts and the generator** in parallel.
5. **Next workflow stage:** the scientific critic reviews this plan against the evidence files, not only its prose
   (AGENTS.md rule 8).

---

## References (all unverified by Justin)

**From the input card:**
- Portalés-Julià et al. 2023, *Scientific Reports* 13:20316, DOI 10.1038/s41598-023-47595-7 (JIF 4.9). Separate
  "visible" and "flooded" outputs. (unverified)
- Qu, Li & Huang 2026, AnyTime-CD, *Remote Sensing of Environment* 334:115239, DOI 10.1016/j.rse.2026.115239 (JIF 12.3).
  Simulated cloud in change detection. (unverified)
- Song et al. 2023, DehazeFormer, *IEEE TIP* 32:1927–1941, DOI 10.1109/TIP.2023.3256763 (JIF 13.7; confirm in JCR). Its
  README's warning on synthetic haze. (unverified)
- Zou et al. 2025, Cloud-Adapter, *IEEE TGRS*, DOI 10.1109/TGRS.2025.3597410 (JIF 9.4). Frozen DINOv2 on HRC_WHU; context
  only. (unverified)

**From the evidence files (dataset and method attributions):**
- Hänsch et al. 2022, SpaceNet 8. The "only attribute what was visible" rule (evidence 01). Venue and JIF not in the
  files. (unverified)
- Li et al. 2019, HRC_WHU, *ISPRS JPRS* 150:197–212 (JIF 12.9, per evidence 02). (unverified)
- He, Sun & Tang 2011. Dark channel; family M; the masks; de-hazing (evidence 01). Metadata only. (unverified)
- Olofsson et al. 2014. Reporting the cannot-assess share (evidence 02). JIF and claim match unchecked. (unverified)
- Geifman & El-Yaniv 2017. Selective classification, for the optional coverage figure (evidence 02). Conference paper;
  rule conflict above. (unverified)
- Burgert, Ravanbakhsh & Demir 2022, *IEEE TGRS* 60 (JIF 9.4, per evidence 04). Synthetic noise justified against a
  cruder control, the pattern behind Q1's control. (unverified)
- Winiwarter et al. 2021, *Remote Sensing of Environment* (JIF 12.3, per evidence 04). Simulated data judged fit for a
  stated use. (unverified)
- Hagolle et al. 2010, *Remote Sensing of Environment* (evidence 02). Two-date cloud detection; read from a catalogue
  snippet only. Context for the §6.4 option. (unverified)
- Makarau et al. 2014, *IEEE TGRS* (DLR; evidence 02). Haze thickness map for uneven haze on VHR imagery; abstract only.
  An optional single-image comparator in §6.4. (unverified)
