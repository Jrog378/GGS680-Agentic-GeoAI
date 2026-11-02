# Refined research questions, second pass: synthetic clouds, what a map can say, and before-image cloud

This is the second revision pass of Stage 1, the research question agent, in the Assignment 3 workflow. Claude
wrote it on 2026-10-23, working alone from local files. It answers Justin's feedback on the first revision
(`outputs/research_questions_refined.md`, R1–R3), recorded in `decision_log.md`.

This is a proposal. It holds no new results. Every number comes from the evidence files or from the files named in
section 1, and all of it is development data. No sealed data was read.

Tags:
- **Evidence:** a number or statement found in a file.
- **Inference:** my reasoning. It has not been measured.

The critic and I run on the same model. Where we agree, that is not independent validation (AGENTS.md rule 4).

---

## 1. Inputs used

- Rules and role: `05_Project/AGENTS.md`, `05_Project/agents/research_question_agent.md`.
- The problem: `CloudResearch/input_card.md`, including "Human decisions so far".
- Justin's decisions: `CloudResearch/decision_log.md`.
- Evidence: `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, `03_pre_refinement_checks.md`.
- Earlier passes:
  - `outputs/research_questions.md` (C1–C5);
  - `outputs/question_review.md` (the critic);
  - `outputs/research_questions_refined.md` (R1–R3).
- Two facts behind Q3, checked for this pass:
  - **The dev log**, entry of 2026-10-23 (night), a domain note on the input card. It records Justin's before-image
    point. No Louisiana-East before image is cloudy. On the before images, the absolute dark channel fired on 55
    tiles, all bright calm water or bare ground. The same log gives DINOv2's cost: about 14 s a tile, 7 m patches.
  - **The road-cue code** (`ProjectBranch/ClaudeFunctions/sn8_roads.py`, `sn8_glcm.py`, `sn8_texture.py`). Every
    classical and texture cue is stored three ways: `_before`, `_after` and `_change`. So an after-only model needs
    no new cue.
- **Numbers the critic took from the notebook.** They are not in the evidence files:
  - 93 thin-cloud roads on 39 tiles;
  - 17 opaque-cloud tiles: 146 roads, 3 labelled flooded, 5 informative tiles.
- No web, no sub-agents, no images, no sealed data.

## 2. Justin's decisions, and what this pass does with them

| Decision (`decision_log.md`) | What this pass does |
|---|---|
| R1 changed: "I just dont like R1 ... I like the synthetic data part where we generate clouds" | Q1 is about the cloud generator: is it realistic, and does it make a usable test bed? There is no contest between cue families. |
| R2 kept, as "What can a flood-road map reliably tell users about roads hidden by cloud?" | Q2 uses that wording. Its body sorts each thing a map says about a hidden road into three tiers: stated reliably, supported on synthetic cloud only, or given only as a range. |
| R3 rejected: "the 20% cut off is something we would end up doing anyways and isnt really a great frame" | Q3 is new, and it does not touch the cut-off. No question here tunes or tests the 20% rule; it stays as adopted. Each primary test condition is set from measured real cloud, not from the gate's pass rate. |
| The critic's rejections of C4 and C5 accepted | Not proposed again: no four-way split, no shadow class, no VLM question. |

## 3. Assumptions

- **Time.** Eight weeks from now, so submission by about 2026-12-18.
- **Baseline system.** Production with the adopted rule (tile rule + road rule) scores 83.0% on 798 assessable roads.
  Always calling "flooded" scores 55.3%.
- **Trusted labels.**
  - A "flooded" label can be trusted anywhere.
  - A missing label means "dry" only on clear roads, and even that is untested.
  - Synthetic cloud leaves the published flood labels unchanged. The critic reads that as allowed. Justin confirms.
- **A new rule question.** Scoring a cloud mask against the place where we put a synthetic cloud uses a synthetic
  truth, not a published label. Q1 and Q2 do this. Justin should rule whether it is allowed (section 9).
- **The generator is frozen first.** The cloud generator is fixed before any flood call is scored on it. A statistic
  used to set the generator is never used to test its realism.
- **Tests.**
  - Tile-block resampling is the primary test everywhere. McNemar is secondary.
  - The tile count goes beside every result (critic X2).
  - Each frozen design gets one blocked-fold sensitivity run (critic X4).
- **Sealed data.** All frozen setups share one batched look. Justin decides.
- **Scope of claims.**
  - Louisiana-East, Maxar 0.5 m greyscale on one UTM grid, Hurricane Ida.
  - For the realism checks: HRC_WHU development images, turned to greyscale.
  - Any wider claim needs Justin's approval (rule 9).
- **t** is the share of ground light that gets through the cloud: 1.0 means none, near 0 means opaque.
- **Geospatial checks in all three questions:**
  - scale: 0.5 m pixels, the 5.2 m road band, the 20 m dark-floor window, 7 m DINOv2 patches, and HRC_WHU's
    0.5–15 m;
  - spatial dependence: tile-block tests;
  - sampling bias: cloud is clustered in areas 0 and 2, and the real cloudy strips were picked by a mask;
  - leakage: tile folds, and synthetic cloud never trains a detector that is scored on the same data;
  - the unit question (MAUP): road against tile against area, in Q2.

---

## 4. The three questions

### Q1. Synthetic clouds as a test bed (rebuilt from R1)

- **Question.** Can synthetic clouds stand in for real cloud when testing flood-road maps?
- **Hypothesis.**
  - **H1a, realism (primary).** We build clouds from real cloud outlines, a thickness field and a haze model. They
    match real cloud, within margins fixed in advance, on two checks:
    1. image statistics on the 93 real thin-cloud strips, at matched dark-floor rise;
    2. how the two existing masks score on them, against real cloud in the same HRC_WHU images.

    A deliberately crude control fails at least one check. The control is evidence 03's uniform haze.
  - **H1b, test bed (secondary).** On the 769 clear roads, at the real thin cloud's level, synthetic cloud costs
    the fixed production model more flooded recall than dry-call rate. In other words, errors under cloud lean
    towards "dry".
    - **Evidence:** under real thin cloud, recall on 24 trusted flooded roads fell from 87% to 67%. The
      tile-resampled interval runs from −0.54 to +0.001.
    - **Evidence:** dry roads under cloud were "kept dry" 94% of the time, but the labelling rule inflates that
      figure.
    - The lean has never been measured on labels trusted both ways.
- **Unit and scope.**
  - For realism, the unit is the cloud: its outline and thickness field. Clusters are SpaceNet 8 tiles or HRC_WHU
    images.
  - For the test bed, the unit is the road strip (the 5.2 m band), clustered by tile.
  - Maxar greyscale after images on Louisiana-East development tiles. HRC_WHU development images.
  - "Behaves like real cloud" means on the statistics and masks tested, not in general.
- **Data (development).**
  - **HRC_WHU, 120 development images.**
    - Their outlines serve as cloud shapes and their cloud pixels as texture. Both uses need Justin's OK.
    - Their real cloud is the target for check 2.
    - Each image's resolution has to be read first: the set spans 0.5–15 m.
  - **SpaceNet 8.**
    - The 93 thin-cloud strips on 39 tiles: image statistics only.
    - The 17 opaque-cloud tiles: their bright-mask cores set the air light and the edge fall-off. They are tuning
      inputs only, never test targets.
    - The 769 clear roads on 190 tiles (433 flooded, 336 dry): the test bed.
    - The 24 trusted flooded roads under thin cloud: a consistency check only.
- **Sealed final check.** The 30 HRC_WHU test images. The frozen generator's mask check (step 3) is run there once.
- **Method.**
  1. **Build the generator and freeze it.**
     - **Shape.** HRC_WHU outlines, rescaled to 0.5 m by each image's resolution. Prefer images near 0.5 m. Report
       outline size and edge statistics by source resolution.
     - **Thickness.** A field t(x): opaque inside the outline, thinning past its edge. HRC_WHU marks thin cloud only
       where the ground cannot be seen clearly, so thin fringes lie outside its outlines.
     - **Family M.** after × t + A × (1 − t), the model behind the dark channel (He, Sun & Tang 2011).
     - **Family X.** The same blend, with three changes:
       - a textured cloud layer, taken from real cloud pixels, in place of the constant air light A;
       - air light that varies across the tile;
       - clipping at 255.
       No method tested on the bed inverts family X exactly.
  2. **Realism check 1: two-date strip statistics.**
     - Put synthetic cloud on clear tiles.
     - Pick synthetic strips by the mask rule that picked the 93 real ones. This is only so that both samples are
       picked the same way.
     - Bin strips by dark-floor rise. In each bin, compare three statistics the generator does not set directly:
       - contrast kept: the local spread of the after image over that of the before image;
       - pattern kept: the local before/after correlation;
       - patchiness: the semivariogram of after − before over the cloud.
     - "Match": the tile-block interval of each median difference lies inside its margin.
  3. **Realism check 2: how the masks behave (HRC_WHU).**
     - Paste synthetic clouds into clear parts of the development images. Use outlines from other images, rescaled
       to the host image's resolution.
     - Score the bright and dark masks on these clouds and on the real cloud in the same images. Both clouds share
       the scene, so this check avoids the scale problem.
     - Real development scores (**Evidence**): bright precision 0.81 and recall 0.28; dark precision 0.62 and
       recall 0.68.
     - "Match": synthetic scores lie within a margin of real ones, paired by image and split by land cover. Land
       cover matters because the dark mask fires falsely on barren ground (F1 0.48).
     - **Circularity check.** Suppose the dark mask scores far better on family M than on real cloud. Then M is too
       close to the mask's own model.
  4. **Use the test bed, on trusted labels.**
     - Add cloud to the after images of held-out clear tiles. Fit the fixed production model on clean tiles, in the
       existing 5 folds.
     - **Grid, fixed in advance.** Thickness has four levels:
       - the real thin level: the median floor rise of the 93 strips, measured before any scoring;
       - one thinner level;
       - one thicker level;
       - opaque.
       Cover has two levels: the 93 strips' median covered share, and the full strip. Both families run.
     - **Primary test (H1b), at the real thin level.** Recall loss minus dry-call loss, with a tile-block interval.
       Beside it, as a consistency check only: the real recall of 67% on 24 roads.
     - **Circularity rule for methods tested on the bed.** De-hazing (He et al.) is one example; as a whole-image
       step it lost 1.7 points.
       - A method counts only on family X.
       - It never sees the t map.
       - A gain on family M alone means the method is undoing the generator.
  5. **Show it.** Real and synthetic clouds side by side at 0.5 m, what the model receives, and error crops. Crops are
     picked by a rule fixed before looking.
- **Baseline.**
  - For the generator: the uniform-haze control.
  - For realism: real cloud (the 93 strips; HRC_WHU).
  - For the test bed: the same model's clean scores on the same 769 roads.
- **Validation (what would refute it).**
  - H1a fails if the full generator misses a margin on either check, or does no better than the control.
  - If the control passes too, the checks cannot tell good cloud from bad. The paper then says realism is untested,
    not shown.
  - H1b fails if the interval of (recall loss − dry-call loss) includes 0, or lies below it.
  - If H1a fails, test-bed results hold for synthetic cloud only. Q2's synthetic tier and Q3 lose their link to real
    cloud.
- **Main threat.** The real targets are few, and both are filtered.
  - The 93 strips were picked by the dark-rise mask, which is itself built on the haze model.
  - HRC_WHU is Google Earth RGB, from other sensors, turned grey. Its thin cloud is labelled only where the ground
    is hidden.
  - So "matches real cloud" means "matches the real cloud we can measure".
- **Power.**
  - **Evidence (03):** on the 769 roads, the flooded − dry gap in flag rate had 95% intervals of about ±4 points at
    t = 0.9, ±7 at 0.8 and ±12 at 0.7.
  - **Inference:** H1b compares the same two groups. So only a lean of about 5–10 points or more will show.
  - **Evidence (03):** the 24 real trusted flooded roads can show only differences of about 25 points. So the
    consistency check cannot catch small gaps.
  - **Inference:** the real side of the realism checks is 39 tiles and at most 120 images. Only clear mismatches will
    show. Compute the detectable difference before running. The control is what shows the test can fail.
- **Course.** GGS 680: the haze model, the masks and the image statistics. The model under test is GGS 662's.
- **What changed and why.**
  - **The frame.** Justin likes the cloud generation but not the DINOv2-against-classical frame. So the generator is
    now the subject. DINOv2 appears only inside the fixed production model.
  - **The primary level.** It is now the real thin cloud's measured floor rise and cover. R1 used t = 0.8, chosen from
    the gate's pass rate. That tied it to the cut-off frame.
  - **Realism can now fail.** It has two checks, test statistics kept apart from tuning, and a control that must
    fail. The mask check on HRC_WHU is new.
  - **Circularity.** Family X; methods count only on X; the t map is hidden from methods; synthetic cloud never
    trains a detector scored on the same data (critic C2-6).
  - **Scale.** Outlines are matched to 0.5 m (critic C2-5). Check 2 compares within each image, so it avoids the
    problem altogether.
  - **Novelty.** None claimed.
    - AnyTime-CD (Qu, Li & Huang 2026) already simulates thin and thick cloud for change detection.
    - DehazeFormer's README warns that models trained on synthetic haze may fail on real haze (evidence 02).
    - The sources read hold no check of synthetic cloud against real cloud at about 0.5 m in greyscale. But nobody
      searched for one.

---

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

### Q3. Cloud on the before image only (new; replaces R3)

- **Question.** When cloud hides a road only in the before image, can the after image alone still map it?
- **Hypothesis.**
  - **Main.** Put opaque synthetic cloud over a road's strip in the before image only. On the same clear roads, an
    after-only call then scores a higher balanced accuracy than the two-date production model.
  - **Secondary.**
    - The two-date model leads when the image is clean. That lead turns into a deficit at some thickness of before
      cloud: the crossover.
    - A before-cloud flag can route roads to the after-only call. Routing costs clean roads less than the noise
      (about 1.5 points).
  - **Why it might hold (Inference).**
    - The change cues compare the two dates, so cloud on the before image corrupts all of them.
    - The current gates would not notice. Per evidence 01, the tile rule reads the after image only. The road rule
      flags a rise in the dark floor from before to after, and before-only cloud gives a fall.
    - The after-only call's inputs do not change at all.
  - **How the two-date model would fail is open (Inference).**
    - Cloud on the before image makes the after image look darker than the before, which reads as flood.
    - It also makes the after image look more textured, which reads as dry.
    - So the model may lose flooded roads, as in Justin's example, or it may add false floods.
    - So the primary metric is balanced accuracy, which is valid here because clear roads' labels are trusted both
      ways. Flooded recall and dry-call rate are reported too. So is a count of the flooded roads the two-date model
      misses and the after-only call finds.
- **Unit and scope.**
  - The road strip, clustered by tile.
  - Louisiana-East development tiles, with synthetic cloud on before images only.
  - Claims hold for synthetic before-image cloud: no Louisiana-East before image is cloudy (evidence 01).
- **Data (development).**
  - The 769 clear roads on 190 tiles (433 flooded, 336 dry). Their before images get Q1's frozen generator, both
    families.
  - All 1,037 development roads, to measure what false routing costs on clean images.
  - The existing `_after` cue columns.
- **Sealed final check.** The 40 SpaceNet 8 test tiles.
  - Their clear roads get the frozen before-image cloud.
  - The frozen two-date model, after-only model and flag are scored.
  - This is the same batched look as Q2's.
- **A possible outside check (Justin's call, rule 9): Germany.**
  - The critic found in the dev log that the one Germany tile seen pairs a winter, snowy, hazy before image with
    summer after images.
  - That is the only real hazy-before case in the files read.
  - But Germany is sealed, its label coding is unknown, and season and snow confound it.
- **Method.**
  1. **Fit an after-only model.**
     - Use production's cue set, restricted to the columns that read only the after image (`*_after`).
     - Drop the before cues, the change cues and the DINOv2 change cues. Design no new cue.
     - Use the same 5 tile folds and clean tiles.
     - Report its clean score beside production's on the 769 roads.
  2. **Add cloud to the before images.**
     - Run Q1's frozen generator on the before images of held-out clear tiles. Leave the after images untouched.
     - **Grid, fixed in advance:**
       - opaque cloud over the full strip (primary). This is Justin's case: the road cannot be seen;
       - Q1's real thin level;
       - two levels in between.
       Strip cover and distance from the cloud edge are secondary axes.
     - Recompute the two-date cues (classical, texture, DINOv2) on the clouded copies.
     - **Leak check.** The after-only calls must be identical on clean and clouded copies. Any change is a leak.
  3. **Run the primary test.**
     - At opaque cloud over the full strip: after-only minus two-date balanced accuracy, paired, with a tile-block 95%
       interval.
     - Report flooded recall and dry-call rate separately.
     - Report the crossover thickness, with its interval.
     - Report what production does now with these roads. It may call them, or mark them as cannot be assessed for
       cloud. The visibility gate may also mark them as not visible, because its road detector reads the before
       image.
  4. **Test the routing.**
     - **The flag is built from what is known to fail.** The absolute dark channel fired on 55 clear before tiles,
       all bright calm water or bare ground (dev log). So the flag uses a relative test (the floor falling from
       before to after) plus a smoothness test on the before image. Thresholds are set by Otsu on the training
       folds, as for the existing masks.
     - **Three systems are scored:** oracle routing (the cloud's place is known), routing by the flag, and no
       routing. Each is scored on the clouded set and on clean roads.
     - **The flag's rate on clean flooded and dry roads is reported.** Floodwater also lowers the after floor
       (**Inference**, from the haze model; critic X1). So a "fall" test may fire on floods.
  5. **Show it.** The clouded before image, the after image, both models' calls, and error crops. Crops are picked
     by a rule fixed before looking.
- **Baseline.**
  - The two-date production model with no routing: 83.0% on 798 roads. Its clean score on the 769 roads comes from
    step 1.
  - Abstaining on roads with before-image cloud, with the coverage this loses.
  - Always "flooded": 55.3%.
- **Validation (what would refute it).**
  - **Stop.** The after-only model's clean balanced accuracy does not beat always "flooded" by a margin fixed in
    advance. Then the after image alone cannot map roads.
  - **Refuted.** At every cell, opaque included, the interval of (after-only − two-date) includes 0 or lies below it.
    Then the two-date model copes with before-image cloud, and routing is not needed.
    - This could happen. The random forest already holds the `_after` cues and may lean on them.
  - **Routing fails** if the flag costs clean roads more than about 1.5 points, or recovers less than half the oracle
    gain. Both margins are fixed in advance.
  - A result on family M that does not hold on family X is reported as generator-specific.
- **Main threat.**
  - No real before-only cloud exists in Louisiana-East, so nothing here is checked on real cloud.
  - The result leans on Q1's realism verdict. That verdict comes from after-image and single-date cloud. Here it is
    carried over to before images taken on another date (**Inference**).
  - Smaller threats: the flag may confuse cloud with floodwater, and the after-only model may be weak.
- **Power.**
  - **Evidence (03):** on about 800 roads, paired accuracy differences have intervals of about ±1.1 to 1.3 points.
  - **Inference:** two different models disagree on more roads than production's arms did, so this interval will be
    wider. Compute it before running.
  - **Inference:** opaque before-image cloud should give a large effect, if there is one. So power matters most at
    thin levels and for the crossover.
  - **Evidence (03):** flag-rate gaps between groups had intervals of ±4 to ±12 points. So the flag's flooded − dry
    gap in false routing shows only if it is roughly 5–10 points or more.
- **Course.** GGS 662: sending a road to a different call is agentic routing. The flag uses GGS 680's masks.
- **What changed and why.**
  - **New; replaces R3.** Justin rejected R3's frame: "the 20% cut off is something we would end up doing anyways
    and isnt really a great frame". Q3 does not touch the cut-off.
  - **It is Justin's own point** (dev log, 2026-10-23 night): "what if the before image has a cloud and the road isnt
    visible then the after image has a visibly flooded road". It is also on evidence 01's list of open questions.
  - **It is not DINOv2 against classical.** The two arms differ by which image a cue reads, not by cue family. The
    DINOv2 change cues leave the after-only arm only because they read both images.
  - **Novelty.** None claimed. An after-only fallback under before-image cloud was not searched for.

**Why this Q3, out of the options considered** (all **Inference**):

| Option | For | Against |
|---|---|---|
| **Before-only cloud, after-only call (chosen)** | Justin's example; open in evidence 01. Labels are trusted both ways. It is likely a blind spot of the current gates. In Louisiana-East, synthetic cloud is the only way to test it, so it shows what the generator is for. It is cheap: the after-only cues exist. The coverage it regains feeds Q2 | No real check in Louisiana-East |
| Local de-hazing to recover thin-cloud roads | Open in evidence 01. Justin's RD2 answer chose selective de-hazing as the next pipeline arm (dev log) | The measured hint is weak: whole-image de-hazing −1.7 points (p 0.15), 3 more of 24 roads found (not significant). Circularity is its core problem. It turns into a contest of methods. It stays as an example use of Q1's test bed, and the pipeline arm can still go ahead |
| Cloud shadows posing as floods | Open in evidence 01; a real risk at 0.5 m. RD2 also asked for a shadow check | The shadow class was part of C4, which the critic rejected and Justin accepted. No shadow labels exist anywhere in the files read (HRC_WHU has none). So a shadow generator cannot be checked against real shadow |
| Partial cover and distance from the cloud edge | Spatial | It is the 20% cut-off frame again. It stays as secondary axes in Q1 and Q3 |

---

## 5. Comparison

All rows are my judgement (**Inference**), not measurement.

| | Q1: synthetic clouds as a test bed | Q2: what a map can say about hidden roads | Q3: cloud on the before image only |
|---|---|---|---|
| **Value** | **High.** Q2's synthetic tier and Q3 both rest on it. Its result is useful either way: a measured realism gap is a finding too | **Medium to high.** It answers Justin's "results people can trust" most directly. It adds few new measurements, and most results under cloud are bounds | **Medium to high.** It probes a likely blind spot of the current gates, and can regain coverage. It covers only one case |
| **Feasibility in 8 weeks** | **Medium.** The biggest build: the generator, two realism checks, and DINOv2 passes on clouded after images. At about 14 s a tile (dev log), one grid cell over 190 tiles is about 45 min of GPU. So a 16-cell grid is about 12 h | **High.** The calls, masks and labels exist. It is mostly analysis and maps | **High once Q1's generator exists; medium alone.** The after-only cues exist. It needs DINOv2 passes on clouded before images, about 45 min a cell |
| **Risk** | With so few real samples, the checks may not tell good cloud from bad. If realism fails, claims hold for synthetic cloud only | No truth under cloud. H2a sits near the noise. It may read as a protocol note | No real check at all. The flag may fire on floodwater. The after-only model may be weak, but one cheap check settles that |
| **Depends on** | Justin's OK on HRC_WHU, and each image's resolution | Q1 for its synthetic tier. Without it: the real tier and the ranges only | Q1's generator and its realism verdict |

## 6. How the three fit in one paper (Inference)

- **One story.** The three questions follow Justin's three verbs:
  - **detect:** Q1 shows how the masks behave on clouds we can make, against real ones, and builds the test bed;
  - **handle:** Q3 asks whether a road should be routed instead of abstained when only the before image is cloudy;
  - **report:** Q2 asks what the map can say, and how sure it is.
- **Sections:**
  1. **Methods:** the generator and its realism (Q1, H1a).
  2. **Result 1:** what cloud does to flood calls on trusted labels (Q1, H1b).
  3. **Result 2:** before-image cloud and the after-only call (Q3).
  4. **Result 3:** what the map can state (Q2), using the test bed's error rates and the coverage Q3 regains.
  5. **Limits:** results are synthetic only wherever Q1's realism check fails, and there is no truth under cloud.
- **One batched sealed look**, by frozen setups: the HRC_WHU test images (Q1) and the SpaceNet 8 test tiles (Q2 and
  Q3). Justin decides.
- **A rough schedule:**
  - weeks 1–2: the generator and the pre-registration;
  - weeks 3–4: the realism checks and the test bed;
  - week 5: Q3;
  - week 6: Q2 and the sealed look;
  - weeks 7–8: writing.

## 7. Recommendation (Justin decides)

**My recommendation: Q1 leads.**
- It is the part Justin said he likes.
- Q2's synthetic tier and all of Q3 depend on its realism verdict.
- It tests on labels that can be trusted, with enough roads.
- Its result is useful whichever way the realism check comes out.

After Q1, Q3 is the cheapest addition, because it reuses the generator and existing cues. Q2 is then the reporting
section.

**This is Justin's call.** If he wants the label and reporting half answered first, or the cheapest and surest
result, Q2 should lead: it needs nothing new. Q3 should not lead alone. Without Q1, its synthetic cloud is
unchecked.

---

## 8. Reference status

**Justin has verified none of these.** The input card says he checks them before any novelty claim.

| Reference | Source | Used for | Read depth |
|---|---|---|---|
| Portalés-Julià et al. 2023, Sci. Rep. (JIF 4.9) | input card | Q2: separate "visible" and "flooded" outputs | Full text searched by Claude |
| Qu, Li & Huang 2026, AnyTime-CD, RSE (JIF 12.3) | input card | Q1: earlier simulated cloud in change detection | Pages read, per `clouds.md` |
| Song et al. 2023, DehazeFormer, IEEE TIP (JIF 13.7, confirm in JCR) | input card | Q1: its README's warning about synthetic haze | README claim via evidence 02. Not used as a method (RGB) |
| Zou et al. 2025; Guo et al. 2024; Hou et al. 2026 | input card | Not used | — |
| Hänsch et al. 2022, SpaceNet 8 | evidence 01 | The labelling rule (dataset attribution) | Pages quoted |
| He, Sun & Tang 2011 | evidence 01 | Q1 family M; the masks (method attribution) | Metadata only |
| Li et al. 2019, HRC_WHU, ISPRS JPRS (12.9) | evidence 01, 02 | Q1: shapes, texture, the mask check | Abstract and README |
| Makarau et al. 2014, TGRS (DLR) | evidence 02 | A possible method to test on Q1's bed | Abstract only. Read in full before use |
| Olofsson et al. 2014 | evidence 02 | Q2 reporting | On disk. JIF not recorded. Claim match unchecked |
| Geifman & El-Yaniv 2017 | evidence 02 | Q2 (optional coverage figure) | Abstract. Conference paper (rule conflict, section 9) |

## 9. Unresolved issues

1. **HRC_WHU.**
   - Each image's resolution is not in the files read.
   - Also unknown: how many images are near 0.5 m, and how many have clear parts to paste into.
   - Justin has not yet ruled on using its outlines and cloud pixels.
2. **Synthetic truth as a scoring truth.** Q1 checks 2 and 4 and Q2's "where" row score masks against the place
   where we put a cloud. Is that allowed under the labelled-data rule? Justin decides.
3. **The realism margins are not set.** The real samples are small. The control may pass, and then the checks are
   uninformative.
4. **The after-only model's clean score is unknown.** This is Q3's go/no-go.
5. **The before-cloud flag may fire on floodwater.** That is an inference, untested.
6. **What cannot be known.**
   - There is no truth under cloud (Q2).
   - Clear-sky "missing = dry" is untested.
   - The 1,080 label rows against 1,037 roads are unexplained.
7. **Counts and intervals not yet computed:**
   - the 93 real strips' median floor rise and covered share (they set the real thin level);
   - the interval for flooded recall on 433 roads;
   - the interval for a paired difference in balanced accuracy (Q3);
   - the number of thin-cloud tiles with both clear and cloudy roads (Q2).
8. **Compute.**
   - DINOv2 passes are needed on clouded copies. The cache covers clean images only (R1's note).
   - The cost of recomputing the classical and texture cues has not been measured.
9. **Citations.**
   - He et al.: metadata only. Makarau: abstract only.
   - Olofsson: claim match and JIF unchecked.
   - Geifman: the project rule (JIF > 4, or company papers) conflicts with AGENTS.md (major conferences allowed).
10. **Decisions for Justin.**
    - Which question leads.
    - The use of HRC_WHU, and synthetic truth (items 1 and 2).
    - Whether all frozen setups share one batched sealed look: the HRC_WHU test images and the SpaceNet 8 test tiles.
    - Whether Germany may serve as Q3's outside check.

## 10. Suggested next scientific action

1. **Justin picks the lead.** He also rules on HRC_WHU use and on synthetic truth.
2. **Four cheap development-only checks through Tilt,** before anything is scored on synthetic cloud:
   1. Read each HRC_WHU development image's resolution. Count the images near 0.5 m and those with clear parts.
   2. Measure the 93 real thin-cloud strips' median floor rise and covered share. They set the real thin level for
      Q1 and Q2.
   3. Fit the after-only model and score it on the 769 clean roads. This is Q3's go/no-go: it has to beat 55.3% by a
      margin.
   4. Compute the tile-block interval widths for flooded recall on 433 roads and for a paired difference in balanced
      accuracy. Count the thin-cloud tiles that hold both clear and cloudy roads.
3. **Write a one-page pre-registration for the lead.** It fixes:
   - the generator families and their settings, and the control;
   - the realism statistics and their margins;
   - the grid and the primary cell;
   - the metrics and the tile-block test;
   - a stop rule: no new statistic, cell or metric after looking.
4. **Build the generator and freeze it.** It serves all three questions.
