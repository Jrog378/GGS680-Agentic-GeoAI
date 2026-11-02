# Refined research questions, third pass: synthetic clouds, what a map can say, and before-image cloud, for change detection in general

This is the third revision pass of Stage 1, the research question agent, in the Assignment 3 workflow. Claude wrote
it on 2026-10-23, working alone from local files. It answers Justin's feedback on the second pass
(`outputs/research_questions_refined_v2.md`): "redo 1 and 3 again but less road focused" (`decision_log.md`).

- **Q1 and Q3 are redone.** Each is now about post-disaster change detection in general: any target, any hazard.
  Flooded roads after Hurricane Ida are one test case. Flooded buildings on the same tiles are a possible second one.
- **Q2 is copied from v2 unchanged**, as Justin asked.

This is a proposal. It holds no new results. Every number comes from the evidence files or from the files named in
section 1, and all of it is development data. No sealed data was read.

Tags:
- **Evidence:** a number or statement found in a file.
- **Inference:** my reasoning. It has not been measured.

The critic and I run on the same model. Where we agree, that is not independent validation (AGENTS.md rule 4).

---

## 1. Inputs used

- Rules and role: `05_Project/AGENTS.md`, `05_Project/agents/research_question_agent.md`.
- The problem: `CloudResearch/input_card.md`.
- Justin's decisions: `CloudResearch/decision_log.md`.
- Evidence: `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, `03_pre_refinement_checks.md`.
- Earlier passes: `outputs/research_questions_refined_v2.md` (Q1–Q3) and `outputs/question_review.md` (the critic).
- Read for this pass, to check what the generality options would cost (read only; nothing run or changed):
  - **The HRC_WHU folder on disk.** The authors' split list gives 30 images of each of five land-cover types
    (barren, snow, urban, vegetation, water). The 120 development images are 24 of each; the 30 sealed test images
    are 6 of each.
  - **`ProjectBranch/Code/cloudref_test.ipynb`, saved outputs.** The masks' scores on HRC_WHU, by land-cover type.
  - **The dev log** (`Project/docs/devlog.md`):
    - 2026-10-15 and 10-16: SpaceNet 8 label totals, the split, Germany;
    - 2026-10-23 (night): the before-image point;
    - 2026-10-11: the main project's building-damage "post-only" controls (used in Q3).
  - **The road-cue code** (`ProjectBranch/ClaudeFunctions/sn8_roads.py`, `sn8_dino.py`). Every cue is averaged over
    an "owner" map: which road each pixel belongs to, within the strip or the ring around it. The DINOv2 cache holds
    pooled vectors per road, not the token maps.
  - **One development label file** (`labels/0_10_2.geojson`, a training tile). I read its field names only. Buildings
    are polygons. Their `flooded` field is present but null on this tile, never "no". I counted no flooded objects.
- No web, no sub-agents, no images, no sealed data.

## 2. Justin's decisions, and what this pass does with them

| Decision (`decision_log.md`) | What this pass does |
|---|---|
| Q1 changed: "redo 1 and 3 again but less road focused" | Q1 asks whether synthetic clouds can stand in for real cloud when testing change maps. Its realism checks no longer use road strips. They need no target at all, and the HRC_WHU check is split by land-cover type. The test bed runs per target. |
| Q2 kept (not asked to redo) | Copied unchanged. |
| Q3 changed: same words | Q3 asks whether the after image alone can show what changed when only the before image is cloudy, for any target. It adds a general limit: an after-only reading sees the after state, not the change. |
| R3 rejected: the 20% cut-off "isnt really a great frame" | Still out. No question tunes or tests it. Cloud cover is a covariate, not a level to tune. |
| R1 changed: keep cloud generation, drop DINOv2 against classical | Still out. DINOv2 appears only inside fixed models. Q3's arms differ by which image a cue reads, not by cue family. |
| The critic's rejections of C4 and C5 accepted | Not proposed again: no four-way split, no shadow class, no VLM question. |

## 3. Assumptions

- **Time.** Eight weeks from now, so submission by about 2026-12-18.
- **Baseline system for roads.** Production with the adopted rule (tile rule + road rule) scores 83.0% on 798
  assessable roads. Always calling "flooded" scores 55.3%.
- **Trusted labels, for every target.**
  - SpaceNet 8's analysts were told to "only attribute what was visible" (evidence 01). I assume this applies to
    buildings as to roads.
  - So a "flooded" label can be trusted anywhere. A missing or null label means "not flooded" only on clear objects,
    and even that is untested.
  - Synthetic cloud leaves the published labels unchanged. The critic reads that as allowed. Justin confirms.
- **Synthetic truth.** Scoring a mask against the place where we put a synthetic cloud uses a synthetic truth, not a
  published label. Q1 and Q3 do this. Justin should rule on it (section 10).
- **The generator is frozen first.** It is fixed before any change call is scored on it. A statistic used to set the
  generator is never used to test its realism.
- **Tests.** Tile-block resampling is the primary test everywhere, with the tile count beside every result (critic
  X2). Each frozen design gets one blocked-fold sensitivity run (critic X4).
- **What "general" can mean here.** The design is general: any target with a published object map and labels, any
  hazard with a clear after image. What can be shown is narrower:
  - one event (Hurricane Ida), one sensor (Maxar, greyscale, 0.5 m);
  - at most two target types, on the same tiles;
  - five land-cover types, for the cloud itself only (HRC_WHU).

  A second event needs Germany, which is sealed. Any wider claim needs Justin's approval (rule 9).
- **t** is the share of ground light that gets through the cloud: 1.0 means no cloud, near 0 means opaque.
- **Geospatial checks:**
  - scale: 0.5 m pixels, the 5.2 m road band, building footprints, the 20 m dark-floor window, 7 m DINOv2 patches,
    and HRC_WHU's 0.5–15 m;
  - spatial dependence: tile-block tests. Roads and buildings on one tile share cloud and flooding, so two targets
    are not two independent samples;
  - sampling bias: cloud is clustered in areas 0 and 2, and the real thin cloud was picked by a mask;
  - leakage: tile folds; synthetic cloud never trains a detector that is scored on the same data.

---

## 4. Generality: what data on disk can show it, and what it costs

All "new work" and "fits" entries are **Inference**.

| Option | What it would show | New work | Fits in 8 weeks? |
|---|---|---|---|
| **SpaceNet 8 buildings, Louisiana-East development tiles** | A second target type, from the same images and event | See below. About 1–2 weeks once, shared by Q1 and Q3 | **Tight.** Only as a secondary target, with a go/no-go at the end of week 3 |
| **HRC_WHU, five land-cover types** (24 development images each) | Whether the clouds and masks behave alike over barren, snow, urban, vegetation and water ground | Little: the per-type scoring exists for the masks | Yes |
| **SpaceNet 8 test tiles** (40; sealed) | The frozen setups' one check, for roads (and buildings if built) | None beyond frozen code | Yes, in the one batched look |
| **HRC_WHU test images** (30, six per type; sealed) | Realism (Q1) and the flag's single-date half (Q3) on unseen images | None | Yes, in the same look |
| **Germany** (202 tiles; sealed) | A second flood event, with roads and buildings | One look. Its label coding must be checked first | Yes, but it is confounded: a winter before image against summer after images on the one tile seen |
| **North negative set** (333 tiles; sealed) | Whether an after-only call calls objects flooded where almost nothing flooded (Q3) | None | Yes, if Justin agrees (it is set aside for negative testing) |
| Main project, Hurricane Ian building damage (development areas A, D, TFD) | A second hazard and target | Synthetic cloud through another pipeline in another repo; whether its imagery holds cloud is not in the files read | **No.** Only its existing post-only result is used, as evidence in Q3 |

**What the SpaceNet 8 buildings would need.** The current pipeline measures road strips. Buildings need footprint
polygons.
- **Evidence.** The label files hold building polygons with a `flooded` field (README; one tile read). Louisiana-East
  has 12,826 building rows against 10,837 road rows over all 599 tiles (dev log, 2026-10-15; totals only, with the
  sealed tiles). How many buildings lie on the 226 development tiles, and how many are flooded, is not in the files
  read.
- **Inference: the code reuse.**
  - Most cues average a pixel map over an owner map. So grey level, edges, local texture, contrast against the ring,
    the texture families and DINOv2 pooling should carry over once footprints are filled into an owner map.
  - The Hough cue (lines parallel to the road) and the centreline cues are road-only. They drop out.
- **The steps:**
  1. Fill each footprint onto the before image's grid, with a ring around it of a width fixed in advance. The road
     code uses 10 m.
  2. Run the cue families over footprint and ring.
  3. Give each building a cloud share.
  4. Build a label table with the same five tile folds, and fit the random forest.
  5. Run one clean DINOv2 pass, about 50 min for 226 tiles at about 14 s a tile. It is needed because the cache keeps
     pooled road vectors only.
- **A decision to make first.** What SpaceNet 8 means by a "flooded" building has to be read in Hänsch et al. (2022)
  before the unit is fixed. **Inference:** at 0.5 m from above, the water is likely around a building rather than on
  its roof, so the ring may carry the signal.
- **Scale (Inference).** A small house covers only a few 7 m DINOv2 patches.
- **If it does not fit:** the claim's stated limit becomes "shown for one target type (roads); general in design
  only".

---

## 5. The three questions

### Q1. Synthetic clouds as a stand-in for real cloud (redone from v2)

- **Question.** Can synthetic clouds stand in for real cloud when testing post-disaster change maps?
- **Hypothesis.**
  - **H1a, realism (primary; no target needed).** We build clouds from real cloud outlines, a thickness field and a
    haze model. They match real cloud, within margins fixed in advance, on two checks:
    1. two-date image statistics of ground under real thin cloud on SpaceNet 8 development tiles, at matched rise of
       the dark floor;
    2. how the bright and dark masks score on them, against real cloud in the same HRC_WHU images, **in each of the
       five land-cover types**.

    The uniform haze of evidence 03 is a deliberately crude control. It fails at least one check.
  - **H1b, the test bed (secondary; per target).** Take clear tiles, where labels can be trusted both ways. At the
    real thin level, synthetic cloud costs a fixed change model more recall on changed objects than calls on
    unchanged ones. In other words, its errors lean towards "no change". The test runs per target: roads first, then
    buildings if built.
    - **Evidence (roads):** under real thin cloud, recall on 24 trusted flooded roads fell from 87% to 67%. The
      tile-resampled interval runs from −0.54 to +0.001. The lean has never been measured on labels trusted both
      ways.
- **Unit and scope.**
  - **Realism.** The unit is the cloud: its outline and thickness field. The ground it covers is sampled in fixed
    windows (for example the 7 m DINOv2 patch grid), clustered by SpaceNet 8 tile or HRC_WHU image. No target is
    involved.
  - **Test bed.** The mapped object, clustered by tile. Two test cases:
    - flooded roads after Ida (the 5.2 m strip): primary, and ready to run;
    - flooded buildings on the same tiles (footprint and ring): secondary, and new work.
  - "Stands in" means on the statistics, masks and targets tested, not for every sensor or hazard.
- **Data (development only).**
  - **HRC_WHU, 120 development images (24 per land-cover type).**
    - Outlines give cloud shapes, and cloud pixels give texture. Both uses need Justin's OK.
    - Their real cloud is check 2's target.
    - Each image's resolution must be read first: the set spans 0.5–15 m.
  - **SpaceNet 8, 226 development tiles.**
    - Ground under real thin cloud (the dark-rise mask), for statistics only. At least the 39 tiles with thin-cloud
      roads; the full count is not in the files read.
    - The 17 opaque-cloud tiles: their bright cores set the air light and the edge fall-off. They are tuning inputs
      only.
    - Test bed, roads: the 769 clear roads on 190 tiles (433 flooded, 336 dry).
    - Test bed, buildings: the clear buildings on the same tiles. Count them first.
    - Real anchors, for consistency only: the 24 trusted flooded roads under thin cloud, and any trusted flooded
      buildings under thin cloud.
- **Sealed final check (one batched look).**
  - The 30 HRC_WHU test images: check 2, run once on the frozen generator, per type.
  - The 40 SpaceNet 8 test tiles: the test bed, run once with the frozen model and generator.
  - Germany is an option (Justin's call). **Inference:** a frozen Louisiana model may fail there for reasons that have
    nothing to do with cloud, such as the season change.
- **Method.**
  1. **Build the generator and freeze it.**
     - Shapes: HRC_WHU outlines rescaled to 0.5 m by each image's resolution.
     - Thickness: opaque inside the outline, thinning past its edge.
     - **Family M:** after × t + A × (1 − t), the model behind the dark channel (He, Sun & Tang 2011).
     - **Family X:** the same blend with a textured cloud layer taken from real cloud pixels, air light that varies
       across the tile, and clipping. No method tested on the bed inverts it exactly.
     - Two placements:
       - whole-tile cloud (primary): every object is covered, which gives the most power;
       - shaped clouds placed by a seeded rule: cover then falls where it falls and is recorded as a covariate.
  2. **Realism check 1 (SpaceNet 8; no target).**
     - Put synthetic cloud on clear tiles.
     - Pick real and synthetic cloudy windows by the same mask rule. Bin them by rise of the dark floor.
     - Compare three statistics the generator does not set directly:
       - contrast kept (local spread of the after image over that of the before image);
       - pattern kept (local before/after correlation);
       - patchiness (the semivariogram of after − before).
     - "Match": the tile-block interval of each median difference lies inside its margin.
  3. **Realism check 2 (HRC_WHU; per land-cover type).**
     - Paste synthetic clouds into clear parts of the development images.
     - Score both masks on these clouds and on the real cloud in the same image, paired by image, within each type.
     - **Circularity check.** If the dark mask scores far better on family M than on real cloud, M is too close to
       the mask's own model.
  4. **Run the test bed per target.**
     - Fit each target's fixed change model on clean tiles, in the existing five tile folds. Then add cloud to the
       after images of held-out clear tiles.
     - **Grid, fixed in advance:** both families and both placements at four thickness levels, so 16 cells:
       - the real thin level: the median rise of the dark floor under real thin cloud, measured on all thin-cloud
         ground, not on any target, before any scoring;
       - one thinner level;
       - one thicker level;
       - opaque.
     - **Primary, per target:** at the real thin level, recall loss minus loss on unchanged objects, with a
       tile-block interval. Beside it: the real anchors.
     - Methods tried on the bed (de-hazing, for example) count only on family X, and never see the t map.
     - **The building model's go/no-go,** fixed in advance and due by the end of week 3: it must beat always calling
       "flooded" on clear buildings by a margin. If it does not, buildings drop out.
  5. **Show it.**
     - Real and synthetic clouds side by side at 0.5 m, per land-cover type.
     - What each model receives.
     - Error crops picked by a rule fixed before looking.
- **Baseline.**
  - For the generator: the uniform-haze control.
  - For realism: real cloud (SpaceNet 8 thin cloud; HRC_WHU).
  - For the test bed: each model's clean scores on the same objects.
- **Validation (what would refute it).**
  - **H1a** fails if the full generator misses a margin on either check, or does no better than the control.
    - If the control passes too, the checks cannot tell good cloud from bad, and realism is untested, not shown.
    - If a land-cover type misses its margin, the stand-in is claimed only for the types that pass. **Inference:**
      barren and snow are the likely misses, since the dark mask already fires falsely there (precision 0.33 and
      0.57).
  - **H1b** fails, per target, if the interval of (recall loss − loss on unchanged objects) includes 0 or lies below
    it.
    - If roads and buildings disagree in sign, the bed's verdict depends on the target. That counts against "in
      general".
  - If H1a fails, every test-bed result holds for synthetic cloud only. Then Q2's synthetic tier and Q3's thin levels
    lose their link to real cloud.
- **Main threat.** The real targets for realism are few, and both are filtered.
  - SpaceNet 8's thin cloud was picked by the dark-rise mask, which is built on the haze model.
  - HRC_WHU is single-date Google Earth RGB turned grey, from other sensors. Its thin cloud is labelled only where
    the ground is hidden.
  - So "matches real cloud" means "matches the real cloud we can measure".
  - Two targets on one set of tiles are not two events.
- **Power.**
  - **Evidence (03):** on the 769 roads, the flooded − dry gap in flag rate had 95% intervals of about ±4 points at
    t = 0.9, ±7 at 0.8 and ±12 at 0.7. **Inference:** H1b compares the same two groups, so on roads only a lean of
    about 5–10 points or more will show.
  - **Evidence (03):** the 24 real trusted flooded roads can show only differences of about 25 points. So the anchor
    is a consistency check.
  - **Inference:** check 2 has 24 images per type. Only clear mismatches will show within a type. Compute the
    detectable difference before running.
  - **What a second target type adds (Inference):**
    - a second test of H1b, with its own count. Buildings may give more objects per tile, but the same 190 or so
      tiles cap the tile-block intervals. So the gain in power is smaller than the object count suggests;
    - a second real anchor;
    - a check that the bed's verdict is not road-specific.

    It adds no second event, place or sensor.
- **Course.** GGS 680: the haze model, the masks and the image statistics. The models under test are GGS 662's.
- **What changed from v2 and why.**
  - **The question names change maps, not flood-road maps** (Justin: "less road focused").
  - **Realism is target-free.** Check 1 samples ground under cloud in fixed windows instead of the 93 road strips.
    The real thin level is set on all thin-cloud ground; the 93 strips' value is reported beside it.
  - **Check 2 is split by land-cover type.** This is where generality over ground cover can be shown with data on
    disk.
  - **The test bed runs per target:** roads (ready) and buildings (new, with a go/no-go).
  - **Cover is now a covariate,** from shaped clouds, not a grid level. That keeps the cut-off frame out.
  - **Kept:** families M and X, the control, the frozen generator, the circularity rules, tile-block tests, and no
    DINOv2-against-classical frame.
  - **Novelty.** None claimed.
    - AnyTime-CD (Qu, Li & Huang 2026) already simulates thin and thick cloud for change detection.
    - DehazeFormer's README warns that models trained on synthetic haze may fail on real haze (evidence 02).
    - The sources read hold no check of synthetic cloud against real cloud at about 0.5 m in greyscale, by land
      cover. But nobody searched for one.

---

*Q2 below is copied from `research_questions_refined_v2.md` without change, as Justin asked. Its references to Q1's
test bed and real thin level still hold: Q1 keeps both, with roads as one of its test cases.*

### Q2. What a map can say about hidden roads (R2, refined)

- **Question.** What can a flood-road map reliably tell users about roads hidden by cloud?
- **Hypothesis.** Under cloud, only some statements meet a reliability rule fixed in advance. The predicted sorting:

  | What the map says | Predicted tier | What can test it |
  |---|---|---|
  | "This road is hidden; it cannot be assessed" | **Reliable**, with the mask's error stated | HRC_WHU (single-date masks, real cloud). The test bed (two-date mask, synthetic). No real two-date cloud labels exist |
  | "This hidden road is flooded" (thin cloud) | **Synthetic only**; the real recall is reported | Test-bed precision and recall. The 24 real trusted flooded roads, for recall only |
  | "This hidden road is dry" | **Range only** | Cannot be measured on real cloud, where dry labels are untrusted. The test bed only |
  | Accuracy on hidden roads | **Range only** | Two bounds: every missing label is flooded, or none is |
  | Flooded road length in an area with hidden roads | **Range only** | Low end: the assessed flooded length. High end: that plus all cannot-assess length |

  - **The reliability rule.** A statement is "reliable" if the tile-block upper bound of its error lies below a
    ceiling fixed in advance, measured on real roads with trusted labels.
    - If its error can be measured only on synthetic cloud, it is "synthetic only".
    - If its error cannot be measured at all, it is "range only".
  - **H2a, kept from R2.** Count hidden roads with missing labels as "dry". The reported accuracy then rises by more
    than the noise (about 1.5 points). So one number hides the cloud problem.
  - **H2b, kept from R2.** On tiles with both thin-cloud and clear roads, the cloudy roads carry fewer flooded labels
    than the clear roads on the same tile.
- **Unit and scope.**
  - The road, for scores. The tile and the area, for the map and the ranges.
  - One frozen classifier. Louisiana-East development roads.
  - The synthetic tier rests on Q1's test bed.
- **Data (development).**
  - 1,037 touched roads on 217 tiles.
  - The bright, dark and dark-rise masks, and production's held-out calls.
  - The 93 thin-cloud strips, 24 of them trusted flooded.
  - The 17 opaque-cloud tiles (146 roads, 3 flooded labels), described only.
  - The HRC_WHU mask scores, and Q1's test bed.
- **Sealed final check.** The frozen model's calls on the 40 SpaceNet 8 test tiles, scored by the frozen protocol.
  This is the same batched look as Q3's.
- **Method.**
  1. **Fit once.** Fit under the adopted rule, in the existing folds, and keep calls on every road (critic C3-2).
  2. **Fix the rules in advance.** For each row of the table: its ceiling, and which evidence may test it.
  3. **Measure what can be measured.**
     - **The masks' error.** On HRC_WHU, and on the test bed. The test bed also shows how far the 20 m floor window
       pulls cloud edges inwards (critic X1).
     - **Recall** on the 24 trusted flooded roads.
     - **The test bed's error rates.** Precision, recall and dry-call rate at Q1's real thin level.
     - **H2a**, by scoring the same calls again with the hidden roads counted as dry.
     - **H2b**, within tile, with the tile as a fixed effect.
  4. **Bound the rest.**
     - Give accuracy on hidden roads as a best case and a worst case.
     - Give flooded length per area as a range from low to high.
     - Say where the truth would have to sit for a conclusion to flip (critic X3).
     - Do not fill hidden roads in from their neighbours. Two reasons:
       - **Evidence:** in area 2, cloudy tiles carry few flooded labels beside heavily flooded clear neighbours (0 of
         7 against 79%). In area 0 the neighbours are dry too.
       - **Evidence (03):** under thick haze, the mask flags flooded roads more often (+13.2 points at t = 0.6). So
         the assessed roads under-represent flooded ones (**Inference**).
  5. **Draw the map and write the protocol.**
     - The map shows cannot-assess roads by area, beside the flood share of their assessed neighbours.
     - The protocol is the table above with its measured tiers. It keeps "can we see it?" separate from "is it
       flooded?", as WorldFloods v2 does (Portalés-Julià et al. 2023).
     - Check Olofsson et al. 2014 and Geifman & El-Yaniv 2017 against what each actually did before citing either.
- **Baseline.**
  - The usual report: one accuracy figure over all labelled roads, missing labels read as dry, and no cannot-assess
    layer.
  - Always "flooded": 55.3%.
  - Production: 83.0% on 798 roads.
- **Validation (what would refute it).**
  - The table can fail row by row:
    - if test-bed precision for "flooded" at the real thin level breaks its ceiling, that row drops to range only;
    - if the dry-call rate holds within its ceiling, "dry" rises to synthetic only.
  - **H2a** fails if its interval lies inside ±1.5 points. Then one number does not mislead at this cloud share.
  - **H2b** fails if the within-tile odds-ratio interval includes 1. Then label omission under thin cloud is not
    shown.
  - If Q1's realism check fails, the synthetic tier is empty. Only "where" and the real recall stay measured.
- **Main threat.**
  - There is no ground truth under cloud (critic X3).
  - "Missing = dry" in clear sky is untested.
  - The "where" row rests on a two-date mask that no real two-date labels have checked.
- **Power.**
  - **Evidence (03):** paired intervals of about ±1.1 to 1.3 points. So H2a sits near the limit.
  - **Inference:** R2's rough sum put the expected rise near that limit, so H2a may come out inconclusive. The tiers
    and ranges do not depend on it.
  - **Evidence (03):** 24 roads on 39 tiles can show only differences of about 25 points. So the real recall is
    reported, not tested.
  - The opaque contrast rests on 5 tiles and 3 labels, so it is described only.
  - **Unknown:** how many thin-cloud tiles hold both clear and cloudy roads. Count them first. If there are fewer than
    a number fixed in advance, H2b is described, not tested.
  - The synthetic tier has Q1's power: 769 roads.
- **Course.** GGS 662 (the gate and the reporting), using GGS 680's masks.
- **What changed and why.**
  - **The wording** is Justin's.
  - **"Reliably" now has a test:** the rule is fixed in advance, and the body sorts statements into reliable,
    synthetic only, and range only. That answers both halves of the question: what can be stated, and what only as a
    range.
  - **New: a synthetic tier from Q1.** There, labels are trusted both ways. So it measures error rates for "flooded"
    and "dry" under cloud, which real cloud cannot give.
  - **Dropped:** sweeping the abstention cut-off as a method. The 20% rule stays as adopted (Justin). A coverage
    figure may still go in the report.
  - **Kept:**
    - one fixed classifier;
    - ranges under cloud;
    - the within-tile label check;
    - no filling in from neighbours.
  - **Novelty.** None claimed. The only gap noted in the sources read is risk–coverage reporting for cloud
    abstention (evidence 02). This protocol was not searched for.

---

### Q3. Cloud on the before image only (redone from v2)

- **Question.** When only the before image is cloudy, can the after image alone still show what changed?
- **Hypothesis.**
  - **H3a (main).** Put opaque synthetic cloud on the before image only. On the same clear objects, an after-only call
    then scores a higher balanced accuracy than the two-date model. Tested per target: roads first, then buildings
    if built.
  - **H3b (the limit; the general part).** An after-only call reads the after state, not the change. So it works where
    the after state implies the change, and fails where that state also occurs without the event.
    - **Prediction for floods.** Take clear dry objects with water nearby that was already there in the clear before
      image (permanent water). On them, the after-only call makes more false "flooded" calls than the two-date model
      does.
    - **Evidence from a second hazard and target** (main project dev log, 2026-10-11; Hurricane Ian building damage;
      development data; not in the evidence files):
      - The after-only ("post-only") controls ranked damaged buildings about as well as the two-date pick on the
        event pair. The pick minus its control, in within-square AUC, was −0.006 (−0.034 to +0.016) on one footprint set. On the other it
        was below its control: −0.017 (−0.039 to −0.002).
      - But on a no-change pair of two post-storm dates, the controls flagged 72–89% of damaged buildings. The
        project's own reading: they read state.
  - **H3c (routing, secondary).** A before-cloud flag can send objects to the after-only call. Routing costs clean
    objects less than the noise (about 1.5 points).
  - **Why it might hold (Inference).**
    - Every change cue compares the two dates, so cloud on the before image corrupts all of them.
    - The current gates would not notice. The tile rule reads the after image only. The road rule flags a rise of the
      dark floor from before to after, and before-only cloud gives a fall (evidence 01).
  - **What part is real (Inference, true by design).** The after-only call never reads the before image. So its score
    on clear objects is a real-image measurement, and the same whatever the before image holds. Only the two-date
    model's loss, and the flag, need synthetic cloud.
- **Unit and scope.**
  - The mapped object, clustered by tile: the road strip (primary) and the building footprint and ring (secondary).
  - **A scope condition (Inference).** The object's place must come from a map or from the after image, not from the
    before image.
    - Mapped roads (OpenStreetMap) and footprints qualify.
    - Production's detected roads do not, because the road detector reads the before image. Nor does the visibility
      gate, for the same reason.
  - **What holds where.**
    - Claims about the two-date model's loss hold for synthetic before-image cloud only. No Louisiana-East before
      image is cloudy (evidence 01).
    - Claims about the after-only call are real-image claims.
  - General in design: any hazard whose after state can be read from one image. Shown here: Ida floods, with at most
    two target types.
- **Data (development only).**
  - The 769 clear roads on 190 tiles (433 flooded, 336 dry). The clear buildings on the same tiles, if built. Their
    before images get Q1's frozen generator, both families.
  - All 1,037 development roads, and all development buildings if built:
    - the after-only call's real score;
    - the cost of false routing on clean images.
  - The existing `_after` cue columns for roads, and the `_after` columns of the new table for buildings.
  - **HRC_WHU, 120 development images.** The flag's single-date half is scored against real cloud in each land-cover
    type.
    - **Evidence:** the absolute dark channel fired on 55 clear Louisiana before tiles, all bright calm water or bare
      ground (dev log).
    - **Evidence:** on HRC_WHU its precision is 0.33 on barren and 0.57 on snow.
- **Sealed final check (the same batched look as Q1's and Q2's).**
  - The 40 SpaceNet 8 test tiles. Their clear objects get the frozen before-image cloud. The frozen two-date model,
    after-only model and flag are scored.
  - The HRC_WHU test images, for the flag's single-date half.
  - **Options for Justin (rule 9):**
    - **The north negative set** (333 tiles; 1 of 1,437 roads flooded). This is a real test of false alarms: does
      the after-only call call roads flooded where almost none flooded? How much permanent water it holds is not in
      the files read.
    - **Germany.** It is the only real case of a degraded before image in the files read: a winter, snowy, hazy before
      image against summer after images, on the one tile seen. But it is sealed, its label coding is unknown, and
      season and snow confound it.
- **Method.**
  1. **Fit the after-only model per target.**
     - Use the `_after` columns only, the same five tile folds, and clean tiles. Design no new cue.
     - Score it on every clear development object. This is a real measurement.
     - **Go/no-go:** it must beat always calling "flooded" by a margin fixed in advance.
  2. **Add cloud to the before images.**
     - Run Q1's frozen generator on the before images of held-out clear tiles. Leave the after images untouched.
     - **Grid, fixed in advance:** opaque full cover (primary; Justin's case), Q1's real thin level, and two levels in
       between.
     - Recompute the two-date cues.
     - **Leak check:** the after-only calls must be identical on clean and clouded copies.
  3. **Run the primary test, per target.**
     - At opaque cover: after-only minus two-date balanced accuracy, paired, with a tile-block 95% interval.
     - Also report flooded recall, the dry-call rate and the crossover thickness.
     - Report what production does now with these objects.
  4. **Check state against change (H3b), on real images.**
     - Mark clear dry objects that have permanent water within their ring in the clear before image. The water mask is
       classical (GGS 680), label-free, and set on the training tiles before scoring.
     - Compare the false "flooded" rates of the after-only and two-date calls, inside and outside that group, with
       tile-block intervals.
  5. **Test the routing (H3c), and show it.**
     - **The flag** is a relative test (the floor falls from before to after) plus a smoothness test on the before
       image, with Otsu thresholds learned on the training folds.
     - **Score three systems:** oracle routing, routing by the flag, and no routing. Score each on clouded and on
       clean objects.
     - **Report the flag's rate on clean flooded and clean dry objects.** Floodwater also lowers the after floor
       (**Inference**), so the flag may fire on floods.
     - **Pictures:** the clouded before image, the after image, both calls, and error crops picked by a rule fixed
       before looking.
- **Baseline.**
  - The two-date model with no routing. For roads that is production: 83.0% on 798 roads. Its clean score on the 769
    roads comes from step 1. For buildings it is the new two-date building model.
  - Abstaining on objects with before-image cloud, with the coverage that loses.
  - Always calling "flooded": 55.3% on roads.
- **Validation (what would refute it).**
  - **Stop, per target.** If the after-only model's clean balanced accuracy does not beat always "flooded" by the
    margin, the after image alone cannot map that target. A "yes" for roads with a "no" for buildings is itself a
    limit on "any target".
  - **H3a is refuted** if, at every cell (opaque included), the interval of (after-only − two-date) includes 0 or lies
    below it. Then the two-date model copes, and routing is not needed. This could happen: the random forest already
    holds the `_after` cues.
  - **H3b is refuted** if the after-only call's false-flood rate near permanent water is not above the two-date
    model's (the interval includes 0). Then the after-only reading does not mistake state for change here. That would
    be good news for the fallback.
  - **Routing fails** if the flag costs clean objects more than about 1.5 points, or recovers less than half the
    oracle gain.
  - A result on family M that does not hold on family X is reported as specific to the generator.
- **Main threat.**
  - No real before-only cloud exists in Louisiana-East. So the two-date model's loss is shown on synthetic cloud only,
    and it leans on Q1's realism verdict.
  - That verdict comes from after-image and single-date cloud. Here it is carried over to before images taken on
    another date by another satellite (**Inference**).
  - **Inference:** this matters less at the primary cell. Opaque cloud removes the ground whatever its texture, so the
    opaque cell depends little on realism. The thin levels depend on it a lot.
  - Smaller threats: the flag may confuse cloud with floodwater. The standing-water group rests on a greyscale water
    mask whose errors have not been measured.
- **Power.**
  - **Evidence (03):** on about 800 roads, paired accuracy differences have intervals of about ±1.1 to 1.3 points.
    **Inference:** two different models disagree on more objects than production's arms did, so this interval will
    be wider. Compute it before running.
  - **Inference:** opaque before-image cloud should give a large effect, if there is one. So power matters most at
    thin levels and for the crossover.
  - **Evidence (03):** gaps in flag rate between groups had intervals of ±4 to ±12 points. So H3b and the flag's
    false routing show only gaps of roughly 5–10 points or more.
  - **H3b's count is unknown.** Count the clear dry objects near permanent water first. If there are fewer than a
    number fixed in advance, H3b is described, not tested.
  - **What a second target type adds (Inference):** a second test of H3a and H3b with its own count, and a check that
    the after-only fallback is not road-specific. Same tiles, so no second event. The main project's building-damage
    result is the only evidence here from a second hazard, and it comes from a different dataset and pipeline.
- **Course.** GGS 662: sending an object to a different call is agentic routing. The flag and the water group use
  GGS 680's masks.
- **What changed from v2 and why.**
  - **The question says "what changed", not "road"** (Justin: "less road focused").
  - **It runs per target:** roads (ready) and buildings (new, shared with Q1, with a go/no-go).
  - **New, H3b.** It states, for any target or hazard, when an after-only reading can stand in for change detection:
    when the after state implies the change. It is tested on real images. It links to the main project's post-only
    finding, which is evidence from a second hazard.
  - **Made explicit:**
    - the after-only score is real; only the two-date model's loss and the flag need synthetic cloud;
    - the scope condition: the object's place must come from a map or the after image.
  - **New:** HRC_WHU scores the flag's single-date half per land-cover type. The north negative set is a sealed
    option.
  - **Kept:**
    - Justin's case, opaque cloud on the before image, is the primary cell;
    - no 20% cut-off;
    - not DINOv2 against classical.
  - **Novelty.** None claimed. An after-only fallback under before-image cloud was not searched for.

---

## 6. Comparison

All rows are my judgement (**Inference**), not measurement.

| | Q1: synthetic clouds as a stand-in | Q2: what a map can say about hidden roads | Q3: cloud on the before image only |
|---|---|---|---|
| **Value** | **High.** The most general of the three: realism needs no target and is checked over five land-cover types. Q2's synthetic tier and Q3's thin levels rest on it. A measured realism gap is a finding too | **Medium to high.** It answers "results people can trust" most directly. It is worded for roads, so in a general paper it is the worked reporting case. Most results under cloud are ranges | **Medium to high.** It covers a likely blind spot of the current gates. H3b gives a general rule for when an after-only reading can be trusted. The after-only score is real |
| **Feasibility in 8 weeks** | **Medium.** The biggest build: the generator, two realism checks, and DINOv2 passes on clouded images. Roads: about 45 min of GPU per grid cell over 190 tiles, so about 12 h for 16 cells. Buildings could pool from the same passes if the code pools both targets at once | **High.** The calls, masks and labels exist. It is mostly analysis and maps | **High for roads.** The after-only cues exist. It needs about 45 min of GPU per cell, and a CPU water mask for H3b. Buildings share Q1's table |
| **Risk** | With so few real samples, the checks may not tell good cloud from bad. Per-type checks have only 24 images. If realism fails, claims hold for synthetic cloud only | No truth under cloud. H2a sits near the noise. It may read as a protocol note | The two-date model's loss is never seen on real cloud. The flag may fire on floodwater. The water group may be small |
| **What buildings add** | A second test of the bed and a second anchor | Nothing (unchanged; roads only) | A second test of H3a and H3b |
| **Depends on** | Justin's OK on HRC_WHU; each image's resolution | Q1 for its synthetic tier | Q1's generator. Its opaque cell and its real after-only score depend little on Q1's verdict |

**The eight weeks, honestly (Inference).** The v2 plan already had no slack. Buildings add about 1–2 weeks of work
once.
- They fit only under three conditions:
  - the building table is built in weeks 2–3, alongside the generator (CPU work beside GPU work);
  - its go/no-go passes by the end of week 3;
  - Q2 stays roads-only, as it is.
- If anything slips, buildings go first. The paper then says: "shown for one target type; general in design".
- HRC_WHU's per-type split costs almost nothing and should stay in either way.

## 7. How the three fit in one paper (Inference)

- **One frame.** Cloud in post-disaster change detection, for any target and hazard. Flooded roads after Hurricane
  Ida are the worked case, and flooded buildings a second case if they pass their go/no-go. The three questions
  follow Justin's three verbs:
  - **detect:** Q1 shows how cloud masks behave on clouds we can make, against real ones, over five ground covers.
    It also builds the test bed;
  - **handle:** Q3 asks whether an object should be routed to an after-only call instead of abstained when only the
    before image is cloudy, and when that is safe (H3b);
  - **report:** Q2 asks what the map can say about hidden objects, worked through on roads.
- **Sections:**
  1. **Methods:** the generator and its realism, by land-cover type (Q1, H1a).
  2. **Result 1:** what cloud does to change calls on trusted labels, per target (Q1, H1b).
  3. **Result 2:** before-image cloud, the after-only call and its limit (Q3).
  4. **Result 3:** what the map can state (Q2), using the bed's error rates and the coverage Q3 regains.
  5. **Limits:** one event and one sensor; results are synthetic only where realism fails; no truth under cloud.
- **One batched sealed look**, by frozen setups:
  - the HRC_WHU test images (Q1, Q3's flag);
  - the SpaceNet 8 test tiles (Q1, Q2, Q3);
  - Germany and the north negative set only if Justin agrees.
- **A rough schedule:**
  - week 1: the pre-registration and the cheap counts (section 11);
  - weeks 1–2: the generator, built and frozen; the building table started;
  - week 3: the realism checks; the building go/no-go;
  - week 4: the test bed;
  - week 5: Q3;
  - week 6: Q2 and the sealed look;
  - weeks 7–8: writing.

## 8. Recommendation (Justin decides)

**My recommendation: Q1 leads, with Q3 second and Q2 as the reporting section.** Buildings come in as a secondary
target only if they pass the week-3 go/no-go.
- Q1 is the part Justin said he likes. After this pass it is also the most general: its realism checks need no target
  and cover five land-cover types.
- Q2's synthetic tier and Q3's thin levels depend on its verdict.
- Its result is useful whichever way the realism check comes out.

**This is Justin's call.** Two alternatives:
- **Q3 leads,** if he wants the surest general result soon. Its after-only score and H3b are real-image
  measurements, and its opaque cell depends little on Q1.
- **Q2 leads,** if he wants the reporting half answered first. It needs nothing new, but it is the most road-bound.

---

## 9. Reference status

**Justin has verified none of these.** The input card says he checks them before any novelty claim.

| Reference | Source | Used for | Read depth |
|---|---|---|---|
| Portalés-Julià et al. 2023, Sci. Rep. (JIF 4.9) | input card | Q2: separate "visible" and "flooded" outputs | Full text searched by Claude |
| Qu, Li & Huang 2026, AnyTime-CD, RSE (JIF 12.3) | input card | Q1: earlier simulated cloud in change detection | Pages read, per `clouds.md` |
| Song et al. 2023, DehazeFormer, IEEE TIP (JIF 13.7, confirm in JCR) | input card | Q1: its README's warning about synthetic haze | README claim via evidence 02. Not used as a method (RGB) |
| Zou et al. 2025; Guo et al. 2024; Hou et al. 2026 | input card | Not used | — |
| Hänsch et al. 2022, SpaceNet 8 | evidence 01 | The labelling rule; what a "flooded" building means (dataset attribution) | Pages quoted for roads. **Read the building definition before the unit is fixed** |
| He, Sun & Tang 2011 | evidence 01 | Q1 family M; the masks (method attribution) | Metadata only |
| Li et al. 2019, HRC_WHU, ISPRS JPRS (12.9) | evidence 01, 02 | Q1: shapes, texture, the mask check by land cover; Q3: the flag's single-date half | Abstract, README and the split list on disk |
| Olofsson et al. 2014 | evidence 02 | Q2 reporting | On disk. JIF not recorded. Claim match unchecked |
| Geifman & El-Yaniv 2017 | evidence 02 | Q2 (optional coverage figure) | Abstract. Conference paper (rule conflict, section 10) |

The main project's post-only result (Q3) is our own measurement from the dev log, not a citation.

## 10. Unresolved issues

1. **HRC_WHU.**
   - Each image's resolution is not in the files read. Nor is the number of images near 0.5 m, or with clear parts
     to paste into, in each type.
   - Justin has not yet ruled on using its outlines and cloud pixels.
2. **Synthetic truth as a scoring truth** (Q1 checks 2 and 4; Q2's "where" row; Q3's flag). Is it allowed under the
   labelled-data rule? Justin decides.
3. **Buildings.**
   - How many buildings lie on the development tiles, and how many are flooded, is not known.
   - Whether "no" ever occurs in their `flooded` field has not been checked; on one tile it is null.
   - What SpaceNet 8 means by a "flooded" building has not been read.
   - The unit (footprint, ring or both) and the ring width are not set.
   - The building model's clean score is unknown. That is its go/no-go.
4. **The realism margins are not set.** The real samples are small, more so per land-cover type. The control may
   pass, and then the checks are uninformative.
5. **Q3's open points.**
   - The after-only model's clean score is unknown (the go/no-go).
   - The flag may fire on floodwater.
   - The water mask behind H3b is unmeasured, and its group may be small.
6. **Evidence from the main project.** Is the 2026-10-11 post-only result fair to use as evidence in this paper?
   Justin decides.
7. **What cannot be known.**
   - There is no truth under cloud (Q2).
   - Clear-sky "missing = not flooded" is untested, for every target.
   - The 1,080 road label rows against 1,037 roads are unexplained.
8. **Counts and intervals not yet computed:**
   - the real thin level (target-free), with the 93 strips' value beside it;
   - the interval for flooded recall on 433 roads;
   - the interval for a paired difference in balanced accuracy (Q3);
   - the number of thin-cloud tiles with both clear and cloudy roads (Q2);
   - the number of clear dry objects near permanent water (H3b).
9. **Compute.**
   - DINOv2 passes are needed on clouded copies, and one clean pass for buildings. The cache keeps pooled road vectors
     only.
   - Pooling both targets from one pass needs a code change.
10. **Citations.**
    - He et al.: metadata only. Olofsson: claim match and JIF unchecked.
    - Geifman: the project rule (JIF > 4, or company papers) conflicts with AGENTS.md (major conferences allowed).
11. **Decisions for Justin.**
    - Which question leads.
    - Whether buildings come in as a second target, with the week-3 go/no-go.
    - The use of HRC_WHU, synthetic truth and the main project's result (items 1, 2 and 6).
    - What the one batched sealed look holds. Whether Germany and the north negative set are in it.

## 11. Suggested next scientific action

1. **Justin picks the lead,** and whether buildings come in. He also rules on HRC_WHU, synthetic truth and the use of
   the main project's result.
2. **Cheap development-only checks through Tilt,** before anything is scored on synthetic cloud:
   1. Count the development buildings and the flooded ones. Check the `flooded` coding across the development tiles.
      Read SpaceNet 8's building definition.
   2. Read each HRC_WHU development image's resolution. Count, per type, the images near 0.5 m and those with clear
      parts.
   3. Measure the real thin level on all thin-cloud ground, and the 93 strips' value beside it.
   4. Fit the after-only road model and score it on the 769 clean roads (Q3's go/no-go).
   5. Count the clear dry roads, and buildings if built, near permanent water in the before image (H3b).
   6. Compute the tile-block interval widths named in section 10, item 8.
3. **Write a one-page pre-registration for the lead.** It fixes:
   - the generator's families and settings, the control and the placements;
   - the realism statistics and their margins, per land-cover type;
   - the grid and the primary cell, per target;
   - the building go/no-go and the after-only go/no-go;
   - the metrics and the tile-block test;
   - a stop rule: no new statistic, cell, target or metric after looking.
4. **Build the generator and freeze it.** It serves all three questions. Start the building table beside it.
