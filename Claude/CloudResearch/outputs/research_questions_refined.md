# Refined research questions: clouds in post-disaster change detection

Stage 1 redo, the revision pass of the research question agent (Assignment 3 workflow). Written 2026-10-23 by Claude,
working alone from local files. It answers the critic's review (`outputs/question_review.md`) and the new checks
(`evidence/03_pre_refinement_checks.md`).

This is a proposal. It holds no new results. Every number comes from the evidence files and is development data,
unless marked otherwise. No sealed data was read.

Tags:
- **Evidence:** a number or statement found in a file.
- **Inference:** my reasoning. It has not been measured.

The critic and I run on the same model. Where we agree, that is not independent validation (AGENTS.md rule 4).

---

## 1. Inputs used

- Rules and role: `05_Project/AGENTS.md`, `05_Project/agents/research_question_agent.md`.
- Problem, scope and boundaries: `CloudResearch/input_card.md`.
- Evidence: `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, and the new
  `03_pre_refinement_checks.md`.
- My first pass: `outputs/research_questions.md`.
- The critic's review: `outputs/question_review.md`. A few numbers come only from it. The critic read them in the dev
  log or the notebook; they are not in the evidence files:
  - matched clean accuracy: DINOv2 cues + vector 83.3% against the classical pipeline 83.1%, on 891 roads;
  - the opaque-cloud counts: 17 tiles, 146 roads, 5 informative tiles, 3 flooded labels;
  - the DINOv2 patch size, about 7 m.
- No web, no sub-agents, no images, no sealed data.

## 2. Assumptions

- **Time.** Eight weeks from now, so submission by about 2026-12-18.
- **Baseline system.** The adopted rule (tile rule + road rule): 83.0% on 798 assessable roads. Always calling
  "flooded" scores 55.3%.
- **Trusted labels.** A "flooded" label is trusted anywhere. A missing label means "dry" only on clear roads. That
  "missing = dry" holds in clear sky is itself untested.
- **Synthetic haze is not a label.** Hazed copies of clear tiles keep their published labels unchanged. The critic
  reads this as allowed under the labelled-data rule. Justin confirms. Using HRC_WHU outlines as cloud shapes also
  needs his OK.
- **Tests.** Tile-block resampling is the primary test everywhere. McNemar is secondary. The tile count goes beside
  every result (critic X2).
- **Sealed data.** Whatever goes ahead shares one batched look by frozen setups (critic's advice; Justin decides).
- **Scope of claims.** Louisiana-East, Maxar 0.5 m greyscale, Hurricane Ida. The methods are written for any object
  strip and any hazard, to fit the universality goal. Any wider claim needs Justin's approval (rule 9).
- **t** below is the share of ground light that gets through the haze: 1.0 is no haze, 0.5 is thick.

---

## 3. What the new checks change, and the decision on F3

**What evidence 03 shows** (**Evidence**; uniform synthetic haze on 769 clear development roads, 190 tiles):
- Under thin haze (t = 0.9 and 0.8), the mask flags flooded and dry roads alike: +0.1 and −0.2 points.
- Under thick haze it flags **flooded** roads more: +13.2 points at t = 0.6 and +7.5 at t = 0.5. Both intervals sit
  above 0.
- The cause: flooded roads start from a lower dark floor in the before image (40 against 47 grey levels).
- The mask flags few roads under thin haze: about 5% at t = 0.9 and 15% at t = 0.8.
- On HRC_WHU, the single-date dark mask finds cloud over water (recall 0.68) about as well as over vegetation (0.66).
- Caveat in the file: this is uniform synthetic haze, not real cloud.

**Decision: F3 is replaced.** Its bias check shrinks to a methods check inside the new R3. Its result is reported in
R2. Reasons:
1. F3 asked whether the mask flags haze less often over floodwater. On uniform haze it does not. It is neutral under
   thin haze and leans the other way under thick haze. The premise failed.
2. What is left of it is a check on a tool, not a question that can carry a paper:
   - uneven haze;
   - partial cover;
   - floodwater within 20 m lowering a dry road's floor;
   - the minimum filter shrinking cloud edges.
   The critic foresaw this: "it shrinks to one paragraph".
3. The same check raised a question that does matter. The gate flags only about 15% of roads at t = 0.8. If haze that
   thin already spoils the flood calls, the gate lets bad calls through (**Inference**). Nothing in the files tests
   the 20% strip cut-off (critic C2-4). R3 asks this.

**Knock-on changes to the other two:**
- **R1.** The primary thickness is t = 0.8. It is the thickest haze the gate still mostly passes, so it is the haze
  the detector actually meets.
- **R2.** Under thick haze the gate removes flooded roads more often than dry ones. So the roads that stay assessed
  under-represent flooded roads (**Inference**). The map must report flooded road length as a range. It must not fill
  in cloudy roads from their neighbours.
- **The thin-cloud label gap** (26% flooded under thin cloud against 55% clear) can no longer be blamed on the mask,
  at least under uniform haze. Two readings remain: label omission and geography. R2's within-tile check addresses
  geography.

**Not carried forward.**
- **C4 as a question.** No four-way split, no shadow class, no road recovery by a two-date test. Its blocking problem
  is not fixed: it cannot be checked on real cloud within the rules.
- **C5 for this paper.** It still has no spatial component, it tests prompt compliance, and its sources are preprints.
  It belongs to the CSI 709 thread.

---

## 4. The three refined questions

### R1 (from F1). Haze on clear roads: DINOv2 against classical cues

- **Question.** Does haze hurt DINOv2 change cues less than classical cues?
- **Main hypothesis.**
  - Start both models from matched clean scores.
  - Add haze of t = 0.8 over the whole strip.
  - The DINOv2-cue model then loses less flooded recall than the classical-cue model.
  - Its dry-call rate is no worse, within a margin fixed in advance.
- **Unit and scope.**
  - Unit: one road strip (the 5.2 m band). Tiles are the clusters for every test.
  - Scope: Louisiana-East, 0.5 m greyscale, synthetic haze on the after image.
  - Claims hold for synthetic haze only.
- **Data.**
  - **Development:**
    - 769 clear roads on 190 tiles (433 flooded, 336 dry), from evidence 03;
    - HRC_WHU development outlines as cloud shapes (Justin's OK). Use only images near 0.5 m, or rescale each outline
      by its image's resolution;
    - the 93 real thin-cloud strips, for image statistics only (no labels).
  - **Sealed final check:** the 40 SpaceNet 8 test tiles. Their clear roads get the same frozen haze and the frozen
    models.
  - **Germany.** It could add an outside check, because R1 needs no real cloud. That is Justin's call (rule 9).
    Its label coding is unknown.
- **Method.**
  1. **Build a haze engine.**
     - Model: after × t + air light × (1 − t), the model behind the dark channel (He, Sun & Tang 2011).
     - A fixed grid: t from 1.0 to 0.5; strip cover from 0 to 100%; distance from the cloud edge.
     - A second, independent haze that no arm inverts: air light that varies across the tile, plus cloud texture.
  2. **Fit the models.** Fit the classical, texture, DINOv2 and production cue sets on clean tiles, in the existing 5
     tile folds. Score hazed copies of the held-out tiles. First confirm that clean scores match on the 769 roads.
  3. **Run the primary test.**
     - The contrast: the drop in flooded recall, DINOv2 minus classical, at t = 0.8 and full cover.
     - A tile-block 95% interval.
     - The dry-call rate as a guard.
     - Holm over the other grid cells.
     - One sensitivity run with blocked folds (critic X4).
  4. **Look at space.**
     - Plot each model's loss against strip cover and against distance from the cloud edge.
     - **Inference:** DINOv2's 7 m patches and whole-crop context can see cloud next to the strip, which the classical
       strip cues cannot. So DINOv2 may lose *more* when cloud is near the road but not on it.
  5. **Check realism, then the secondary arm.**
     - At matched floor rise, compare local before/after contrast on synthetic strips with the 93 real thin-cloud
       strips. Define "match" in advance.
     - The real recall drop (87% to 67%, 24 roads) is a consistency check only.
     - Secondary arm: selective de-hazing (Makarau et al. 2014, or He et al.), scored on the independent haze only.
     - Show pictures: the inputs, what DINOv2 receives, and the errors.
- **Baseline / comparator.**
  - The classical-cue model (83.1% clean) against DINOv2 cues + vector (83.3% clean). Both are on 891 roads, from the
    dev log via the critic.
  - Production (83.0% on 798 roads) as the reference system.
  - Each model's own clean score.
- **Validation (what would refute it).**
  - The tile-block interval for the difference in recall drop at t = 0.8 includes 0, or lies below 0.
  - Or the DINOv2 advantage shows on the scattering-model haze but not on the independent haze.
  - Or synthetic strips fail the pre-set match with real strips. Then the result holds for synthetic haze only, and
    the paper says so.
- **Main threat.** Synthetic haze is not real cloud. Real cloud has texture, shadows and uneven opacity. The
  image-statistics check is the only bridge to real cloud.
- **Power.**
  - **Evidence (03):** paired accuracy differences on about 800 roads have 95% intervals of about ±1.1 to 1.3 points.
    So effects above about 1.5 points can be seen.
  - **Evidence (03):** synthetic haze on the 769 clear roads avoids the 24-road limit that real cloud imposes.
  - **Inference:** flooded recall rests on 433 roads, so its interval will be wider than accuracy's. Compute it before
    running.
- **Course.** GGS 662 (DINOv2 features), with GGS 680's classical cues as the comparator.
- **What changed and why.**
  - The primary hypothesis is now DINOv2 against classical, from matched clean scores (critic C2-3). "Accuracy falls
    steadily" is dropped, because it could not fail.
  - The primary thickness is fixed at t = 0.8. This is new from evidence 03: the gate passes about 85% of roads there.
  - Strip cover and edge distance are added (C2-4). The check of the 20% cut-off moved to R3, so R1 tests one
    contrast.
  - Also fixed:
    - independent haze for the de-hazing arm (C2-2);
    - realism by image statistics at matched floor rise, which avoids the circular thickness estimate (C2-1);
    - shapes matched to 0.5 m (C2-5);
    - tile-block tests primary, plus blocked folds (X2, X4).
  - **Novelty.** AnyTime-CD (Qu, Li & Huang 2026) already simulates thin and thick cloud in change detection. The
    sources read found no test of frozen DINOv2 change cues under haze at 0.5 m in greyscale. That is a gap in the
    sources read, not a shown novelty (X6).

---

### R2 (from F2). Reporting the roads that cloud hides

- **Question.** What should a flood-road map tell users about roads hidden by cloud?
- **Main hypothesis.**
  - Take the same model calls.
  - Count cloud-hidden roads with missing labels as "dry".
  - The reported accuracy then rises by more than the noise (about 1.5 points).
  - So a single accuracy number hides the cloud problem.
  - **The label check** (a pre-registered second test): on tiles with both thin-cloud and clear roads, the cloudy
    roads carry fewer flooded labels than the clear roads on the same tile.
- **Unit and scope.**
  - The road, for scores. The tile and the area, for the map.
  - One frozen classifier. Louisiana-East development roads.
- **Data.**
  - **Development:** 1,037 touched roads on 217 tiles; the bright and dark-rise masks; production's held-out calls.
  - **Sealed final check:** the frozen model's calls on the 40 test tiles, scored by the frozen protocol. This goes in
    the same batched look as R1, not a separate one (critic C1-6).
- **Method.**
  1. **Fit once.** Fit under the adopted rule, in the existing folds, and keep calls on every road. Then vary only the
     abstention cut-off, never the model (critic C3-2).
  2. **Score the same calls in three ways.**
     - Clear roads only.
     - All roads, with missing = dry.
     - Two bounds: every cloudy missing label is flooded, or none is (X3).
     Use tile-block intervals.
  3. **Run the label check.**
     - Compare flooded-label shares of thin-cloud and clear roads within the same tile, with the tile as a fixed
       effect (C1-3).
     - Report the opaque-cloud gap (3 flooded labels, 5 informative tiles) only as "the dataset follows its
       documented rule".
  4. **Draw the map.**
     - Show cannot-assess roads by area, beside the flood share of their assessed neighbours.
     - Give flooded road length as a range: the assessed flooded length at the low end; that plus all cannot-assess
       length at the high end.
     - Draw risk–coverage curves with the measured misses on trusted flooded roads, and mark the part that cannot be
       measured.
  5. **Write the protocol.**
     - A short checklist of what to report.
     - It follows WorldFloods v2's split between "can we see it?" and "is it flooded?" (Portalés-Julià et al. 2023).
     - Before citing Olofsson et al. 2014 and Geifman & El-Yaniv 2017, check each against what it actually did (C3-6).
- **Baseline / comparator.**
  - The usual report: one accuracy figure on all labelled roads, with missing labels read as dry.
  - Always "flooded": 55.3%.
- **Validation (what would refute it).**
  - The tile-block interval of the re-scoring difference lies inside ±1.5 points. Then a single number is not
    misleading at this cloud share, and the protocol's value rests on the map and the ranges alone.
  - For the label check: the within-tile odds-ratio interval includes 1. Then thin-cloud label omission is not shown.
- **Main threat.** There is no ground truth under cloud (X3). Every quantity there is a bound, not a measurement.
  "Missing = dry" in clear sky is also untested.
- **Power.**
  - **Evidence (03):** differences above about 1.5 points can be seen.
  - **Inference:** a rough sum from evidence 01 puts the expected rise near that limit. Cloudy dry-labelled roads are
    "kept dry" 94% of the time, against 83% accuracy overall. So the main test may come out inconclusive. This is a
    back-of-envelope figure, not a result. The map and the ranges do not depend on it.
  - **Evidence (01, 03):** trusted-flooded recall under thin cloud rests on 24 roads on 39 tiles. Only differences of
    about 25 points or more can be seen. So it is reported, not tested.
  - The opaque contrast rests on 5 tiles and 3 flooded labels: descriptive only.
  - **Unknown:** how many of the 39 thin-cloud tiles hold both clear and cloudy roads. Count them first. If there are
    fewer than a number fixed in advance, report the label check descriptively.
- **Course.** GGS 662 (the gate and the reporting), using GGS 680's masks.
- **What changed and why.**
  - C3 and C1 are merged, as the critic asked:
    - one fixed classifier;
    - ranges under cloud;
    - a cannot-assess map;
    - no ranking of overlapping curves;
    - the 10-road hypothesis dropped, because it rested on untrusted labels (X5).
  - The label check is now within-tile. Evidence 03 removes the mask-bias reading, under uniform haze. So a
    within-tile gap points to label omission, or to geography inside the tile.
  - New from evidence 03: under thick haze the gate drops flooded roads more often. So the range must be reported,
    not filled in from neighbours.
  - **Novelty.** The sources read found no remote-sensing paper with risk–coverage curves for cloud abstention (one
    web search, one arXiv query). That is a gap in the sources read only.

---

### R3 (replaces F3). Does the cloud gate stop the haze that matters?

- **Question.** Does the cloud mask stop roads before haze spoils their flood calls?
- **Main hypothesis.**
  - The adopted gate mostly passes some band of haze.
  - In that band, flooded recall on the roads the gate passes is already down by more than a margin fixed in advance.
  - **Evidence behind it:** the road rule flags only about 5% of roads at t = 0.9 and 15% at t = 0.8. Whether recall
    falls at those levels has not been measured.
- **Unit and scope.**
  - Unit: the road strip and the gate's decision on it. Tiles are the clusters.
  - Scope: Louisiana-East development tiles, synthetic haze.
  - The gate under test: dark rise above the Otsu threshold (71) on at least 20% of the strip, plus the tile rule.
- **Data.**
  - **Development:**
    - the 769 clear roads (190 tiles) under R1's haze engine;
    - HRC_WHU development outlines (Justin's OK);
    - all real development roads, to count the coverage a new cut-off would cost.
  - **Sealed final check:** the 40 test tiles in the same batched look, with the cut-off and the haze frozen.
- **Method.**
  1. **Reuse R1's haze engine.** Use both haze types, on the grid of thickness, strip cover and edge distance.
  2. **Record two things in every cell.** The gate's decision, and the fixed production model's call on the held-out
     hazed copy.
  3. **Plot two curves on one thickness axis.**
     - The share of roads the gate flags.
     - Flooded recall and dry-call rate on the roads it passes.
     - Mark any band where the gate passes most roads but recall falls outside the margin.
  4. **Calibrate the gate.**
     - Choose the rise threshold and strip share on the training folds, to close that band.
     - Test them on the held-out folds.
     - Report the coverage this would cost on real development roads.
     - Report recall on the 24 real trusted flooded roads under thin cloud, as a consistency check only.
  5. **Run the methods check (what is left of F3).**
     - The flooded − dry flag-rate difference under partial, uneven cover, against a margin set in advance.
     - Flag rates on dry roads with and without floodwater within 20 m.
     - The masked share against the true covered share. The 20 m minimum filter shrinks cloud edges (critic X1).
     - The results feed R2's ranges.
- **Baseline / comparator.**
  - The adopted gate.
  - No gate: production on every road.
  - The calibrated gate.
- **Validation (what would refute it).**
  - There is no unsafe band. Wherever the gate passes at least half the roads, passed-road recall and dry-call rate
    stay within the margin of clean, with tile-block intervals inside it. Then the adopted gate is adequate for this
    haze. That null result would still be the first test behind the 20% cut-off.
  - Or the calibrated cut-off fails on held-out folds, or costs more coverage than a limit set in advance.
- **Main threat.**
  - **Circularity.** The dark-rise mask assumes the same haze model that adds the haze. So its flag rates on that
    haze are likely optimistic.
  - The independent haze and the real-strip image check (from R1) are the guards.
  - R1's synthetic-to-real gap applies here too.
- **Power.**
  - **Evidence (03):** the 95% intervals of the flooded − dry flag difference were about ±4 points at t = 0.9, ±7 at
    0.8 and ±12 at 0.7. So "equal" cannot be claimed with a margin tighter than about 5 to 10 points.
  - **Inference:** at t = 0.8 about 85% of the 433 flooded roads pass the gate (roughly 370). So passed-road recall
    rests on a few hundred roads. Compute its interval before running.
- **Course.** GGS 680 (the classical mask) and GGS 662 (the gate).
- **What changed and why.**
  - It replaces F3. F3's premise, that the mask under-flags flooded roads, was not found under uniform haze
    (evidence 03). F3's check survives as step 5.
  - The new question comes from the same check: the mask misses most thin haze. Whether that matters is untested.
    The 20% cut-off has no test behind it (critic C2-4).
  - It is not C4 again:
    - no four-way split;
    - no shadow class;
    - no road recovery;
    - no method resting on Hagolle et al. 2010 (read as an abstract only).
    Its quantities can be measured on clear roads with trusted labels. Being unmeasurable was C4's blocking problem.
  - **Novelty.** None claimed. Gate calibration was not searched for specifically.

---

## 5. Side by side

All rows are my judgement (**Inference**), not measurement.

| | R1: haze, DINOv2 against classical | R2: reporting what cloud hides | R3: does the gate stop harmful haze? |
|---|---|---|---|
| **Scientific value** | **High.** Strongest identification: one deliberate change, trusted labels, about 770 roads. It speaks to a wider question (foundation-model features under haze). It holds for synthetic haze only. | **Medium to high** for Justin's "results people can trust". It is the only one that deals with the labels and the report. It makes few new measurements, and most results under cloud are bounds. | **Medium.** It tests the gate the pipeline already uses. A null still matters: it would be the first test of the 20% cut-off. It is of narrower interest outside the project. |
| **Feasibility in 8 weeks** | **Medium.** The biggest build: the haze engine, plus new DINOv2 passes on every hazed copy (the cache covers clean images only). | **High.** Calls, masks and labels exist. It is mostly analysis and maps. One count is still unknown (tiles for the label check). | **High if R1 runs; medium alone.** It needs the same engine and the same hazed DINOv2 passes as R1. |
| **Risk** | The synthetic-to-real gap. A null contrast (DINOv2 about equal to classical) is possible. It can still be reported, but it makes a weaker paper. | No truth under cloud. Low power under cloud. The main test sits near the detection limit. It may read as a protocol note rather than a research paper. | Circularity of mask and haze model. It depends on R1's engine. A null shrinks it to a section. |
| **Shares with** | The engine with R3; the sealed look with R2 and R3 | The frozen model and the sealed look with R1 | The engine and passes with R1; its step 5 feeds R2 |

## 6. Recommendation (Justin decides)

**My recommendation: R1 as the lead question.**
- It has the cleanest test. It changes one thing on purpose, on roads whose labels can be trusted, with enough roads
  to see moderate effects.
- It does not lean on the unvalidated mask.
- Evidence 03 makes its primary thickness well motivated: t = 0.8 is haze the gate lets through.

R3 is the cheapest addition, because it reuses R1's engine and passes. R2 can then be the reporting section. Together
they would cover Justin's three verbs: detect (R3), handle (R1) and report (R2). That combination is my inference
about the paper's shape, not a tested plan.

**This is Justin's call.** If he wants the paper to answer the label and reporting half of his problem first, R2 should
lead. It is also the cheapest of the three to run.

---

## 7. Reference status

**None of these references has been verified by Justin.** The input card says he verifies them before any novelty
claim.

| Reference | Source | Used for | Read depth |
|---|---|---|---|
| Portalés-Julià et al. 2023, Sci. Rep. (JIF 4.9) | input card | R2: separate "visible" and "flooded" outputs | Full text searched by Claude |
| Qu, Li & Huang 2026, AnyTime-CD, RSE (JIF 12.3) | input card | R1: prior simulated cloud in change detection | Pages read, per `clouds.md` |
| Zou et al. 2025, Cloud-Adapter; Song et al. 2023, DehazeFormer; Guo et al. 2024, SkySense; Hou et al. 2026 | input card | Not used (RGB, synthetic-trained, or SAR) | — |
| Hänsch et al. 2022, SpaceNet 8 | evidence 01 | The labelling rule (dataset attribution) | Pages quoted |
| He, Sun & Tang 2011 | evidence 01 | Dark channel and haze model (method attribution) | Metadata only |
| Li et al. 2019, HRC_WHU, ISPRS JPRS | evidence 01, 02 | Cloud shapes (R1, R3) | Abstract and README |
| Makarau et al. 2014, TGRS (DLR) | evidence 02 | R1 de-hazing arm | Abstract only; read in full before use |
| Olofsson et al. 2014 | evidence 02 | R2 reporting | On disk; JIF not recorded; claim match unchecked |
| Geifman & El-Yaniv 2017 | evidence 02 | R2 risk–coverage | Abstract; conference paper (rule conflict, below) |
| Hagolle et al. 2010 | evidence 02 | Dropped with C4 | Abstract snippet only |

## 8. Unresolved issues

1. **Synthetic to real.** It affects R1 and R3. The image-statistics check on the 93 real strips is the only bridge.
2. **Evidence 03 used uniform haze only.** Uneven haze, partial cover and the effect of floodwater within 20 m are
   untested. R3 step 5 covers them.
3. **No truth under cloud** (R2). Under cloud, results can only be bounds.
4. **Counts and intervals not yet computed:**
   - the flooded-recall interval on 433 roads (R1);
   - the passed-road recall interval (R3);
   - the number of thin-cloud tiles that hold both clear and cloudy roads (R2).
5. **HRC_WHU resolution.** The resolution of each image is not in the files read. R1 and R3 need it to match shapes
   to 0.5 m.
6. **Clear-sky "missing = dry"** is untested. The 1,080 label rows against 1,037 roads are unexplained (critic).
7. **Citations.**
   - Makarau and Olofsson need full reads.
   - The project rule (JIF > 4 or company papers) conflicts with AGENTS.md (which accepts major conferences). This
     decides Geifman & El-Yaniv.
8. **Decisions for Justin.**
   - Which question leads.
   - Whether HRC_WHU outlines may serve as shapes, and its cloud pixels as texture.
   - Whether all frozen setups share one batched sealed look.
   - Whether Germany may serve as R1's outside check.

## 9. Suggested next scientific action

1. Justin picks the lead question.
2. Run two cheap development-only counts through Tilt:
   - the tile-block interval width for flooded recall on the 433 clear flooded roads;
   - the number of thin-cloud tiles holding both clear and cloudy roads.
   Also read each HRC_WHU image's resolution.
3. Write a one-page pre-registration for the lead question. For R1 it fixes:
   - the haze generators and the grid;
   - t = 0.8 and full cover as the primary cell;
   - flooded recall as the primary metric and the dry-call guard margin;
   - the tile-block test;
   - the realism "match" rule;
   - a stop rule: no new thickness or metric after looking.
4. Then build the haze engine. It serves R1 and R3.
