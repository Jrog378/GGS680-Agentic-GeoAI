# Question review: clouds in post-disaster change detection

Stage 2 of the Assignment 3 workflow (scientific critic). Written 2026-10-23 by Claude, working alone, from local
files only. It reviews the five candidates in `outputs/research_questions.md`.

It holds no new results. Every number below is development data, never a test result. Numbers come from the evidence
files or from the files they were built from (section 1).

I am a second agent on the same model as the Stage 1 agent. Where I agree with Stage 1, that is not independent
validation (AGENTS.md rule 4).

Tags used below:
- **Evidence:** a number or statement found in a file.
- **Inference:** my reasoning. It has not been measured.

---

## 1. Inputs used

- Rules and role: `Claude/05_Project/AGENTS.md`, `Claude/05_Project/agents/scientific_critic.md`.
- The problem: `CloudResearch/input_card.md`.
- Evidence: `CloudResearch/evidence/01_measured_results.md`, `02_cloud_literature_summary.md`.
- Under review: `CloudResearch/outputs/research_questions.md`.
- To check claims Stage 1 took from outside the two evidence files (read only, nothing changed or run):
  - `~/Masters/GGS662/Project/docs/devlog.md`: the 2026-10-23 entries (clouds, DINOv2, co-registration, night) and
    the 2026-10-15 split entry;
  - `~/Masters/GGS662/ProjectBranch/Code/clouds_test.ipynb`: the saved outputs of the label table, the neighbour
    check and the logged findings. This notebook is the source of evidence file 01;
  - `ProjectBranch/ClaudeFunctions/sn8_heldout.py` (how the folds are made) and `sn8_clouds.py` (how the neighbour
    check is defined);
  - `ProjectBranch/Literature/notes/clouds.md` and `clouds_review_web.md`, searched for read depth and search depth.
- I read no images, no sealed data and no web pages.

## 2. Assumptions

- **Time.** Eight weeks from now, so submission by about 2026-12-18 (same as Stage 1).
- **Baseline.** The adopted production rule (tile rule + road rule, 798 assessable roads) is the baseline for every
  candidate.
- **Trusted labels.** A "flooded" label is trusted anywhere. A missing label means "dry" only on clear roads. This is
  itself an assumption: no file checks that a missing label in clear sky always means dry.
- **Synthetic data are not labels.** Hazed copies of clear tiles keep their published flood labels unchanged. So I
  treat C2-style injection as allowed under the labelled-data rule. Justin still decides on HRC_WHU shapes (Stage 1's
  question).
- **Scores.** 1 = weak, 3 = adequate as written, 5 = strong. They are my judgement. My eight dimensions differ from
  Stage 1's seven, so the totals are not comparable.

## 3. Checks on Stage 1's facts

| Stage 1 claim | Where I found it | Status |
|---|---|---|
| 0 of 7 labelled flooded on a cloudy area-2 tile, against 79% on clear neighbours | notebook neighbour table (2_16_45: 0/7 against 11/14) | Correct |
| 10 roads handed back from cloudy tiles, called right half the time | dev log, clouds entry | Correct. But scored against untrusted dry labels (issue X5) |
| Absolute dark channel fired on 55 clear before images | dev log, night entry | Correct |
| Relief displacement 5–13 m on area-0 tanks | dev log, clouds entry | Correct |
| AnyTime-CD: 30% extra thick cloud cost about 3.6 F1 | `clouds.md` (PDF pp. 16–17 read) | Matches the note |
| Search depth: two arXiv queries (DINOv2 under haze); one web search + one arXiv query (risk–coverage) | `clouds_review_web.md` | Matches the note |
| Germany: winter, snowy, hazy before image against summer after images; class totals read before sealing | dev log, 2026-10-15 | Correct. The dev log says "1,248 flooded and 4,447 not". It does not say whether "not" is a stored "no" or a missing value, so Stage 1's open question stands |
| 87% clear against 67% under thin cloud, on 24 trusted flooded roads | notebook findings | Correct on the 891-road folds. On the 1,037-road folds the same 24 roads give 71% (dev log). That is one road |
| 487 "yes" + 593 missing | notebook: train + validation tiles only | No sealed label was read. But 487 + 593 = 1,080 label rows against 1,037 touched roads. The 43-row gap is not explained in the files I read. Minor |
| C1 "low power" quotes the interval −0.54 to +0.001 | evidence 01 | That interval is for the model's recall under cloud, not for the labelling odds ratio C1 tests. Minor mismatch |

New facts from the notebook that matter for C1 (**Evidence**, development data):
- The 17 opaque-cloud tiles hold 146 roads. Only **3** are labelled flooded.
- The 93 thin-cloud roads lie on 39 tiles. 24 are labelled flooded.
- Of the 17 opaque-cloud tiles:
  - 6 have no clear neighbour tile with roads;
  - 6 have clear neighbours with no flooded roads (mostly area 0);
  - only **5** have clear neighbours with flooded roads (2_18_44, 2_19_43, 2_16_45, 0_19_13, 2_20_43). Those 5 hold
    35 roads, 3 labelled flooded (9%), against 35 of 65 (54%) on their clear neighbours.
- Folds are `StratifiedGroupKFold` by tile, shuffled. So neighbouring tiles usually fall in different folds.

---

## 4. Issues that cut across candidates

### X1. The dark-rise mask's errors may follow flood state

- **ISSUE.** The thin-cloud mask may flag haze less often over floodwater, and may fire on non-cloud brightening that
  is more common on dry ground. Both push "cloudy" roads towards "dry".
- **LOCATION / TARGET.** C1 (thin-cloud contrast), C2 (realism target), C3 (the road rule), C4 (built on the same
  floor).
- **SEVERITY.** Blocking for C1's thin-cloud claim. Major for C2 and C3.
- **WHY IT MATTERS.**
  - **Inference, from the haze model the mask itself assumes** (He, Sun & Tang 2011): after = ground × t + air light ×
    (1 − t). The darkest pixel within 20 m (the floor) then rises by (air light − floor) × (1 − t) on a dry road. If
    floodwater makes the after-image floor darker than the before floor by some amount d, the rise on a flooded road
    is smaller by about d × t. So under the same haze, flooded roads are flagged less often.
  - With no haze, a flooded road's floor falls. So the mask never flags floodwater. That matches the one check done
    (0% on the most-flooded tile). **The check that was done is predicted by the same mechanism that predicts the
    missed haze. It cannot tell them apart.**
  - The floor is a minimum over 20 m, but the road band is 5.2 m. So floodwater anywhere within 20 m (a ditch, a yard)
    lowers the floor of a dry road too. The bias would be spatially clustered in flooded neighbourhoods.
  - A minimum filter also shrinks cloud: a pixel's floor rises only if its whole window is hazed. Cloud edges move in
    by up to the window, and cloud strips narrower than the window vanish. That matters for the "≥ 20% of the strip"
    rule.
  - Any non-cloud change that brightens the darkest pixels raises the floor. Flooding lowers it. So non-cloud false
    alarms also lean towards dry roads.
  - How big any of this is depends on real floor values, which nobody has measured.
- **EVIDENCE NEEDED.**
  - The after-image and before-image floors on clear flooded against clear dry roads (798 roads, development data).
    If the after floors match, the bias under even haze is near zero.
  - The dark-rise flag rate on clear flooded and clear dry roads after adding haze of known thickness.
  - The dark mask's recall (not only F1) by land cover on the 120 HRC_WHU development images, from the run already
    done. Lower recall on water scenes would be real-cloud evidence of the same effect. It is single-date only.
- **RECOMMENDED ACTION.** Run these three checks before any candidate uses the dark-rise mask as truth. They need no
  new data and no sealed data.

### X2. The real sample is tiles, not roads

- **ISSUE.** Roads on one tile share cloud, flooding and image conditions. Road-level tests overstate the evidence.
- **LOCATION / TARGET.** C1, C2's realism target, C3.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence:** the cloud effect on recall is p = 0.010 by roads (Fisher) but its tile-resampled interval
    (−0.54 to +0.001) reaches 0. At tile level the drop is not established.
  - **Evidence:** the opaque-cloud label contrast rests on 5 informative tiles and 3 flooded labels.
  - McNemar's test assumes independent roads.
- **EVIDENCE NEEDED.** For each primary test: the number of tiles that carry it, and the smallest difference a
  tile-block test could detect.
- **RECOMMENDED ACTION.** Make tile-block resampling the primary test everywhere. Report McNemar only as secondary.
  State the tile count beside every result.

### X3. There is no ground truth under cloud

- **ISSUE.** Justin's problem asks how labels compare with ground truth. Under cloud, no permitted source gives the
  truth: labels are missing there, own labels are not allowed, and no independent flood map is in the evidence files.
- **LOCATION / TARGET.** C1 ("accuracy looks better than it is"), C3 (risk under cloud), C4 (re-admitted roads).
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Any claim about how wrong the labels are, or how good the model is, under cloud can only be
  bounded, not measured.
- **EVIDENCE NEEDED.** None can be had within the rules. An independent flood map of the same date would help, but
  none is listed, and adding one needs Justin's OK and a source that passes the citation rule.
- **RECOMMENDED ACTION.** Phrase every under-cloud quantity as a range. Worst case: every unlabelled cloudy road is
  flooded. Best case: none is. Report where the truth would have to sit for a conclusion to flip.

### X4. Tile folds leave neighbours in different folds

- **ISSUE.** **Evidence:** folds are shuffled groups of tiles. **Inference:** a road's model is often fit on the tile
  next door, which shares the flood pattern and the cloud.
- **LOCATION / TARGET.** All absolute accuracies; C2 and C3 most.
- **SEVERITY.** Major for absolute numbers. Minor for differences between arms, if leakage affects arms equally.
- **WHY IT MATTERS.** Spatial autocorrelation can inflate the clean baseline. It can also make cloudy tiles easier to
  call from their neighbours than a truly new place would be.
- **EVIDENCE NEEDED.** The same results with folds made of blocks of adjacent tiles, or one area held out at a time.
- **RECOMMENDED ACTION.** Add one blocked-fold sensitivity run to each frozen design. Fix the block size before
  running.

### X5. Agreement with untrusted labels is used as accuracy

- **ISSUE.** Two pieces of evidence score the model against dry labels that cannot be trusted.
- **LOCATION / TARGET.** "Dry roads under cloud are kept dry 94%" (C1). "The 10 handed-back roads are called right
  half the time" (C3 evidence and hypothesis; C4's refutation test).
- **SEVERITY.** Major for C3 and C4.
- **WHY IT MATTERS.** On cloudy tiles a missing label may hide a flooded road. So "right half the time" is agreement
  with the labels, not accuracy. It rests on 10 roads.
- **EVIDENCE NEEDED.** How many of the 10 are labelled flooded (trusted), and the model's recall on just those.
- **RECOMMENDED ACTION.** Stop calling these numbers accuracy. Use only trusted-flooded recall under cloud, with its
  count.

### X6. Novelty rests on a thin search

- **ISSUE.** Each gap comes from local notes, one web search and a few arXiv queries. The GMU library round
  (`clouds.md` §5) has not been done.
- **LOCATION / TARGET.** All five novelty statements.
- **SEVERITY.** Major for any novelty claim; minor for the plan.
- **WHY IT MATTERS.** AGENTS.md rule 9 needs Justin's approval for novelty. The input card says he verifies the
  references first.
- **EVIDENCE NEEDED.** The library search, and Justin's check of the candidate references.
- **RECOMMENDED ACTION.** Keep every statement as "not found in the sources read". Do not write any claim of being
  first.

### X7. No second dataset fits

- **ISSUE.** No permitted second dataset has flood labels and real cloud at about 0.5 m.
- **LOCATION / TARGET.** All candidates; the input card's universality goal.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - Germany is sealed (one look). Its cloud content is unknown. Its label coding is unknown. Its before images can be
    winter against summer after images.
  - Louisiana-West has no labels.
  - HRC_WHU has cloud labels but no change or flood labels.
  - So "any hazard, any sensor, any cloud" cannot be tested here. External validity needs Justin's approval anyway
    (AGENTS.md rule 9).
- **EVIDENCE NEEDED.** Whether Germany holds any cloud, which can only be learned by spending it.
- **RECOMMENDED ACTION.** Scope every claim to Louisiana-East, Maxar greyscale, Hurricane Ida. Treat Germany as one
  batched look by frozen setups, and say in advance that it may hold no cloud.

---

## 5. Score summary

| Candidate | Importance | Novelty / gap | Testability | Identification | Data adequacy | Spatial validity | Robustness / validation | Feasibility | Total /40 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 Labels missing under cloud | 4 | 2 | 3 | 2 | 2 | 2 | 2 | 5 | 22 | REVISE (not as lead) |
| C2 Haze of known thickness | 4 | 3 | 4 | 4 | 4 | 3 | 3 | 4 | 29 | REVISE (lead) |
| C3 Where to abstain, how to report | 4 | 3 | 3 | 3 | 2 | 4 | 2 | 5 | 26 | REVISE (merge with C1) |
| C4 Two-date visibility test | 3 | 2 | 2 | 2 | 2 | 3 | 1 | 3 | 18 | REJECT (salvage a narrow core) |
| C5 VLM and unseen roads | 2 | 2 | 3 | 3 | 3 | 1 | 2 | 4 | 20 | REJECT for this paper |

No candidate is accepted as written.

---

## 6. Review by candidate

### C1. Labels missing under cloud

**Score reasons.**
- Importance 4: it is the label half of Justin's problem, and SpaceNet 8 is a public benchmark.
- Novelty 2: the SpaceNet 8 paper states the rule and that its baseline learned it (p. 6).
- Testability 3: falsifiable in form, but the opaque test is close to certain to pass.
- Identification 2: the neighbour adjustment has little support, and the mask is confounded with flooding.
- Data adequacy 2: 3 flooded labels on opaque tiles, and 5 informative tiles.
- Spatial validity 2: the permutation scheme breaks the cloud's spatial structure.
- Robustness 2: no truth, and no second dataset with known label coding.
- Feasibility 5: all data are on hand.

**Required checks.**
- *What would falsify it?* Stage 1's test is the bright-mask odds ratio including 1. But under opaque cloud the
  documented rule predicts missing labels, so a pass says little. The informative test is the thin-cloud contrast,
  and X1 can produce that contrast on its own.
- *Scale.* The neighbour unit (8 tiles around) and the road unit differ. The 20 m floor is wider than the 5.2 m road.
  An elevation covariate would need to resolve road-scale relief.
- *Autocorrelation or leakage.* Cloud and flood are both clustered (areas 0 and 2). Not a leakage problem, since no
  model is fit, but a confounding one.
- *Causal claim.* "Cloud causes missing labels" is supported by the dataset's own rule for opaque cloud. For thin
  cloud it is not justified until X1 is checked.
- *Does the evidence discriminate?* No. Three explanations fit the thin-cloud 26% against 55%: analysts could not
  see, the mask under-flags flooded roads (X1), and cloud fell on less-flooded places.
- *Second dataset.* Germany only, sealed, label coding unknown.
- *Answerable?* The size of the gap can be bounded. Whether labels are "wrong against ground truth" cannot be
  answered (X3).

**Issues.**

**C1-1. The thin-cloud contrast cannot be told apart from the mask artefact.**
- **LOCATION / TARGET.** C1 hypothesis 1; "expected observable evidence", first bullet.
- **SEVERITY.** Blocking.
- **WHY IT MATTERS.** The thin-cloud contrast is the only part of C1 not already predicted by the documented rule.
  It is also the part X1 can fake.
- **EVIDENCE NEEDED.** The floor and injection checks in X1.
- **RECOMMENDED ACTION.** Do not interpret 26% against 55% until X1 is done. If X1 finds a floor difference, report
  the label finding only as a range.

**C1-2. The opaque test is close to a tautology and rests on 5 tiles.**
- **LOCATION / TARGET.** C1 hypothesis "gap largest under opaque cloud"; first refutation test.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** analysts were told to label only what was visible. So missing labels under
  opaque cloud are expected by design. **Evidence:** the contrast rests on 35 roads on 5 tiles (3 flooded against 54%
  on neighbours), mostly in area 2.
- **EVIDENCE NEEDED.** None beyond what exists. It confirms the documented rule.
- **RECOMMENDED ACTION.** Report it as a check that the dataset behaves as documented, not as a finding.

**C1-3. The neighbour adjustment has little support.**
- **LOCATION / TARGET.** C1 method: "flood share of clear roads within a fixed radius".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** 6 of the 17 opaque tiles have no clear neighbour roads at all. Cloud is
  contiguous, so cloudy roads sit beside other cloudy roads. Adjustment needs overlap that is mostly absent.
- **EVIDENCE NEEDED.** For thin cloud, how many of the 39 tiles hold both cloudy and clear roads.
- **RECOMMENDED ACTION.** For thin cloud, compare cloudy and clear roads within the same tile (tile as a fixed
  effect). That removes tile-level geography. It does not remove X1.

**C1-4. The permutation null is not valid.**
- **LOCATION / TARGET.** C1 method: "a permutation that shuffles cloud between tiles within each area".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Shuffling tiles breaks the cloud's contiguity, so the null has less spatial clustering than the
  data. That makes the observed effect look rarer than it is. With 5 informative tiles, there are also few distinct
  shuffles.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Use the tile-block resampling interval as the test. If a null is wanted, move the whole
  cloud pattern as a block rather than tile by tile.

**C1-5. "Accuracy looks better than it is" needs a truth that does not exist.**
- **LOCATION / TARGET.** C1 hypothesis 3.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** X3. Re-scoring the same calls with and without cloudy roads is sound and cheap. But it shows
  only how much the reported score depends on untrusted labels, not the true score.
- **EVIDENCE NEEDED.** None within the rules.
- **RECOMMENDED ACTION.** Keep the re-scoring. Report accuracy on cloudy roads as a range (X3). Move it into the
  reporting candidate (section 7, F2).

**C1-6. The plan spends sealed data on a label analysis.**
- **LOCATION / TARGET.** C1 "plausible data": one sealed look at the 40 test tiles and Germany.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** The boundary rule allows one logged look by a frozen setup. A label audit reads sealed images
  and labels, so it uses up that look. Germany may hold no cloud, and its label coding may differ, so the look could
  answer nothing.
- **EVIDENCE NEEDED.** Justin's ruling (Stage 1, unresolved issue 5).
- **RECOMMENDED ACTION.** Freeze the C1 code with the model and run both in the same batched look. Do not plan a
  separate look for C1.

**C1-7. Minor points.**
- **LOCATION / TARGET.** C1 "plausible data" (elevation layer); "main threat" (low power).
- **SEVERITY.** Minor.
- **WHY IT MATTERS.** A coarse elevation layer cannot resolve which streets flood. The quoted interval is for model
  recall, not the labelling effect (section 3).
- **EVIDENCE NEEDED.** The resolution of any elevation layer, before asking Justin to approve a download.
- **RECOMMENDED ACTION.** Drop the elevation covariate unless one at road-scale resolution is found. Fix the
  power statement.

**Verdict: REVISE.** C1 asks the right question for Justin's problem, but it should not lead. Its opaque-cloud result
is predicted by the dataset's own documented rule, so it confirms rather than discovers. Its thin-cloud result, the
only part that could add something, cannot yet be told apart from the dark-rise mask under-flagging flooded roads, or
from where the cloud happened to fall. The neighbour design has little overlap to work with, the permutation null is
not valid, and there is no ground truth to say how wrong the labels are. Split it: its re-scoring and bounds go into
the reporting candidate (F2), and its mask-artefact threat becomes a test of its own (F3).

---

### C2. Haze of known thickness on clear roads

**Score reasons.**
- Importance 4: it shows how cloud breaks the detector, with labels that can be trusted.
- Novelty 3: AnyTime-CD already simulates cloud in change detection. Frozen DINOv2 change cues at 0.5 m greyscale
  were not found tested.
- Testability 4: a controlled design with clear outcomes; the first hypothesis is weak.
- Identification 4: haze is an intervention, so the cause is known within the model.
- Data adequacy 4: **Evidence:** 798 clear roads on 193 tiles, 441 flooded.
- Spatial validity 3: haze per tile is not yet a spatial question; the HRC_WHU shape scale is off.
- Robustness 3: synthetic-to-real is not validated.
- Feasibility 4: the tools exist, and the DINOv2 cache exists.

**Required checks.**
- *What would falsify it?* The DINOv2 curve is not above the classical curve at a thickness fixed in advance (tile
  interval includes 0). Selective de-hazing, tested on haze it did not generate, recovers nothing.
- *Scale.* Haze is added per tile; roads are scored per strip. HRC_WHU shapes come from 0.5–15 m images. The floor
  window (20 m) and the DINOv2 patch (7 m) are both wider than the road band (5.2 m).
- *Autocorrelation or leakage.* X4. The clean baseline may be inflated, probably about equally across arms.
- *Causal claim.* "Synthetic haze causes the drop" is justified. "Real cloud causes the same drop" is not.
- *Does the evidence discriminate?* Yes, between DINOv2 and classical cues under the haze model. No, for real cloud.
- *Second dataset.* None permitted with real cloud and flood labels (X7).
- *Answerable?* Yes for synthetic haze. The real-cloud link is weak.

**Issues.**

**C2-1. The realism check cannot discriminate.**
- **LOCATION / TARGET.** C2 "expected observable evidence": the realism check against 87% → 67%.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence:** the real drop's tile-resampled interval runs from −0.54 to +0.001. Almost any synthetic curve,
    from no drop to a 54-point drop, would "reproduce" it.
  - **Evidence:** the target itself moves with fold assignment (67% or 71%: one road of 24).
  - **Inference:** the real cloud's "estimated thickness" would come from the dark channel, which is the same model
    used to add the haze. That is circular.
  - X1 also makes the 24 roads a non-random subset of flooded roads under cloud.
- **EVIDENCE NEEDED.** A realism check on image statistics, which needs no labels and can use all 93 thin-cloud
  strips: compare floor rise and local before/after contrast on real strips with synthetic strips at matched
  thickness.
- **RECOMMENDED ACTION.** Call the accuracy comparison a consistency check, not validation. Add the image-statistics
  check, with "match" defined before running.

**C2-2. The de-hazing arm is circular.**
- **LOCATION / TARGET.** C2 hypothesis 3; "main threat" (circular de-hazing).
- **SEVERITY.** Major.
- **WHY IT MATTERS.** He et al. de-hazing inverts the very model that would add the haze, so it will look better than
  on real haze. Stage 1 names this but does not fix it.
- **EVIDENCE NEEDED.** Recovery on haze made by a different process.
- **RECOMMENDED ACTION.** Make an independent haze arm a design rule. Options: air light that varies across the tile,
  added cloud texture, or cloud pixels taken from HRC_WHU development images (Justin's OK, as for shapes). Also score
  the de-hazer on the 24 real trusted flooded roads, and say it is low power.

**C2-3. The first hypothesis is close to certain.**
- **LOCATION / TARGET.** C2 hypothesis 1, "accuracy falls steadily".
- **SEVERITY.** Minor.
- **WHY IT MATTERS.** A test that cannot fail adds nothing. The risky claim is DINOv2 against classical.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Make the primary hypothesis the DINOv2 against classical contrast. Start both at matched
  clean accuracy. **Evidence:** DINOv2 cues + vector 83.3% against the classical pipeline 83.1% on 891 clear roads.
  Fix the primary thickness, metric (flooded recall and dry-call rate) and test (tile-block) before running. Holm
  over the rest.

**C2-4. The spatial part is thin.**
- **LOCATION / TARGET.** C2 as a whole; boundary condition "meaningful spatial component".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Haze per tile is a radiometric test. The spatial question is how much of a road's strip the
  cloud covers, and how far the road is from the cloud's edge. **Inference:** the files read show no test behind the
  20% strip cut-off that production now uses.
- **EVIDENCE NEEDED.** Accuracy against strip coverage (0–100%) and thickness together, and against distance from the
  cloud edge.
- **RECOMMENDED ACTION.** Add a coverage × thickness grid. It calibrates the road rule's 20% cut-off, which links C2
  to the reporting candidate. Note the floor filter's edge shrink (X1) when comparing masked share with true share.

**C2-5. HRC_WHU cloud shapes are at the wrong scale.**
- **LOCATION / TARGET.** C2 "plausible data" and method (shapes with soft edges).
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** HRC_WHU spans 0.5–15 m. **Inference:** a cloud outline drawn at 15 m and pasted
  at 0.5 m is up to 30 times too large and too smooth. Edge sharpness and size drive partial cover, the thing C2-4
  tests.
- **EVIDENCE NEEDED.** Each HRC_WHU image's resolution. It is not in the files read.
- **RECOMMENDED ACTION.** Use only images near 0.5 m, or rescale each shape by its stated resolution. Report the size
  and edge statistics of the shapes used.

**C2-6. Other points.**
- **LOCATION / TARGET.** C2 tests; swapped-date arm; novelty.
- **SEVERITY.** Minor.
- **WHY IT MATTERS.**
  - Paired McNemar at each thickness treats roads as independent (X2). Many thicknesses × feature sets × metrics
    inflate false positives.
  - No real "before cloudy" case exists in Louisiana-East. So the swapped-date arm has no real check at all.
  - AnyTime-CD covers cloud robustness in change detection in general. The gap is narrow and lightly searched (X6).
  - The injected cloud's location is known by construction. It must never train a cloud detector that is then scored
    on the same synthetic data.
- **EVIDENCE NEEDED.** None beyond the design.
- **RECOMMENDED ACTION.** Tile-block test primary. State that the swapped-date arm is synthetic only. Keep the novelty
  wording as "not found in the sources read".

**Verdict: REVISE (lead).** C2 has the strongest identification of the five. It changes one thing on purpose, on
roads whose labels can be trusted, with enough tiles to detect moderate differences. Its weaknesses are fixable. The
realism check cannot discriminate as written. The de-hazing arm is circular unless the haze comes from a different
process. The first hypothesis cannot fail. The spatial component needs to be the strip coverage, not only the
thickness. HRC_WHU shapes must be matched to 0.5 m. Even revised, its results speak for synthetic haze on
Louisiana-East, and any wider claim needs Justin's approval.

---

### C3. Where to abstain, and how to report it

**Score reasons.**
- Importance 4: it is the "report them" part of Justin's problem, and decides what a user of the map is told.
- Novelty 3: no remote-sensing risk–coverage paper for cloud was found, but the search was thin (X6).
- Testability 3: the curves can be drawn, but half the risk cannot be measured under cloud.
- Identification 3: rule comparisons are paired, but the rules change both the fitted model and the scored set.
- Data adequacy 2: 24 trusted flooded roads under cloud; the rules differ on few roads.
- Spatial validity 4: the unit choice (MAUP) is the question itself, and is stated.
- Robustness 2: no truth under cloud (X3), and no second dataset (X7).
- Feasibility 5: the calls and masks exist.

**Required checks.**
- *What would falsify it?* The road-level and tile-level curves overlap, with the difference interval including 0.
  Stage 1 admits the present evidence leans this way.
- *Scale.* Road, tile and window are different units. Good that all are reported.
- *Autocorrelation or leakage.* X4 inflates absolute risk; differences less so.
- *Causal claim.* None needed; it compares rules.
- *Does the evidence discriminate?* Only on trusted flooded roads, so only on misses. False alarms under cloud cannot
  be scored.
- *Second dataset.* None (X7).
- *Answerable?* As a ranking of rules, probably not at this sample size. As a reporting method, yes.

**Issues.**

**C3-1. Only half the risk can be measured under cloud.**
- **LOCATION / TARGET.** C3 method: risk defined as misses on trusted flooded roads, or errors on clear roads only.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** On cloudy roads a "flooded" call against a missing label may be right. A "dry" call may be a
  miss. So misses alone show half the error, and clear-road errors do not change with a cloud cut-off.
- **EVIDENCE NEEDED.** None within the rules (X3).
- **RECOMMENDED ACTION.** Report misses on trusted flooded roads as measured. Report accuracy on cloudy roads with
  missing labels as a range (X3). State plainly which part of the curve is unmeasurable.

**C3-2. The curves mix two effects.**
- **LOCATION / TARGET.** C3 method: sweep the cut-off. **Evidence:** in the code, each rule's "cannot assess" roads
  are neither fitted nor scored.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Changing the rule changes the model and the scored set at once. A risk–coverage curve, as in
  selective classification, keeps the classifier fixed and varies only what it abstains on.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Fit once, under the adopted rule. Vary only the abstention cut-off. Report the fitting effect
  separately (it is already measured: no rule differs on the 766 shared roads).

**C3-3. The rule comparison is likely underpowered.**
- **LOCATION / TARGET.** C3 hypothesis 1 ("fewer errors at the same coverage").
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** rule differences on the 766 shared roads are 0.7–0.9 points, below the about-1-point
  fold noise. There are 24 trusted flooded roads under thin cloud. Equivalence cannot be shown either.
- **EVIDENCE NEEDED.** A tile-block minimum detectable difference for the planned contrast.
- **RECOMMENDED ACTION.** Reframe C3 as a reporting protocol, not a ranking. Show overlapping curves with intervals and
  do not rank them (the project's own rule).

**C3-4. Abstention is not at random in space.**
- **LOCATION / TARGET.** C3 "expected observable evidence": cannot-assess share by area.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** cloud clusters in areas 0 and 2. **Inference:** the assessed roads are then a
  biased sample. A flooded-road length taken from the assessed map is too low or too high, depending on what lies
  under the cloud. That matters for "results people can trust".
- **EVIDENCE NEEDED.** A map of cannot-assess roads beside the flood share of their assessed neighbours.
- **RECOMMENDED ACTION.** Report a cannot-assess map, not only a share. Report flooded road length as a range: the
  assessed flooded length, up to that plus all cannot-assess length.

**C3-5. The second hypothesis rests on untrusted labels.**
- **LOCATION / TARGET.** C3 hypothesis 2; "the 10 roads handed back ... half the time".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** X5.
- **EVIDENCE NEEDED.** The trusted-flooded count among the 10, and recall on them.
- **RECOMMENDED ACTION.** Drop hypothesis 2, or restate it on trusted flooded roads only, with the count.

**C3-6. Citation checks.**
- **LOCATION / TARGET.** C3 method: Geifman & El-Yaniv 2017; Olofsson et al. 2014.
- **SEVERITY.** Minor.
- **WHY IT MATTERS.**
  - Geifman & El-Yaniv is a conference paper. AGENTS.md and the input card accept major conferences; the project's
    own rule keeps only JIF > 4 journals or company papers. Stage 1 flagged this.
  - Olofsson et al. 2014 has no JIF recorded in the evidence. **Inference:** it is a guide to accuracy assessment and
    area estimation. Whether it says anything about a no-data or cannot-assess share must be checked in the paper
    before it is cited for that.
- **EVIDENCE NEEDED.** Justin's ruling on conferences; a read of the Olofsson passages; its JIF.
- **RECOMMENDED ACTION.** Cite each only for what it actually did.

**Verdict: REVISE (merge with C1).** C3 serves the reporting half of Justin's problem better than any other candidate,
and its data are on hand. But as a contest between road-level and tile-level abstention it will most likely return
overlapping curves. The rules differ on few roads, only 24 trusted flooded roads sit under cloud, and half the risk
cannot be scored there. The curves also mix a change of model with a change of scored set. Revised as a reporting
protocol, it is sound: a fixed classifier, measured misses, ranges for what cannot be measured, and a map of where the
system abstains. Taking in C1's re-scoring makes it the place where the label problem is reported honestly.

---

### C4. A two-date visibility test

**Score reasons.**
- Importance 3: it would recover roads, but only if it could be checked.
- Novelty 2: the two-date test is Hagolle et al.'s. The four-way split is new but cannot be checked.
- Testability 2: real-data checks need labels that do not exist.
- Identification 2: floodwater and opaque cloud can look the same to it.
- Data adequacy 2: no two-date cloud labels; 24 trusted flooded roads.
- Spatial validity 3: window size and co-registration are stated.
- Robustness 1: the only check is circular synthetic truth.
- Feasibility 3: buildable, but the method rests on two abstracts.

**Required checks.**
- *What would falsify it?* Failure on synthetic pairs. But passing them proves little (circular).
- *Scale.* A 10–20 m window against a 5.2 m road; relief displacement (5–13 m) and about 0.6 m shifts lower the
  correlation with no cloud.
- *Autocorrelation or leakage.* Thresholds are learned on training tiles. Fine if Otsu-style; if learned against
  synthetic truth, that is training on synthetic labels.
- *Causal claim.* None.
- *Does the evidence discriminate?* No. Opaque cloud and bright floodwater both lose the pattern and raise the floor.
- *Second dataset.* HRC_WHU for the single-date part only.
- *Answerable?* Not on real cloud within the rules.

**Issues.**

**C4-1. It cannot be checked on real cloud.**
- **LOCATION / TARGET.** C4 as a whole; "main threat", first and third bullets.
- **SEVERITY.** Blocking.
- **WHY IT MATTERS.** No two-date cloud labels at this resolution were found. HRC_WHU is single-date and has no
  shadows. A real-data check of the four classes would need our own labels, which the rules forbid.
- **EVIDENCE NEEDED.** A published two-date cloud and shadow reference near 0.5 m. None is in the evidence.
- **RECOMMENDED ACTION.** Do not pursue the four-way split as a research question.

**C4-2. Roads moved back cannot be scored for "dry".**
- **LOCATION / TARGET.** C4 hypothesis: "some of the 93 roads can be assessed again without more errors".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Even if the haze call is right, the labels on those roads were made through the haze. Missing
  labels there are still untrusted. Only recall on trusted flooded roads can be checked (24 roads).
- **EVIDENCE NEEDED.** None within the rules.
- **RECOMMENDED ACTION.** Any recovery arm is scored on trusted-flooded recall only, with the count stated.

**C4-3. Bright floodwater and opaque cloud look alike to it.**
- **LOCATION / TARGET.** C4 four kinds: "opaque: strong rise, pattern lost"; "floodwater: surface replaced".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Inference:** dark floodwater lowers the floor, but bright floodwater (turbid or glinting) raises
  it, and both lose the ground pattern. Thin haze over floodwater gives a small rise with the pattern lost. So the
  target class can be routed to "cannot assess".
- **EVIDENCE NEEDED.** Floor rise and correlation on clear flooded roads (no haze), against opaque-cloud strips.
- **RECOMMENDED ACTION.** If kept as a component, measure this on clear flooded roads first.

**C4-4. The method rests on abstracts, and its refutation test on untrusted labels.**
- **LOCATION / TARGET.** C4 method (Hagolle et al. 2010; Makarau et al. 2014); refutation test 2 (the 10 roads).
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** Hagolle was read from a catalogue snippet; Makarau from an abstract. The window,
  thresholds and handling of real surface change are unknown. The 10-road test uses untrusted labels (X5).
- **EVIDENCE NEEDED.** Full reads of both papers.
- **RECOMMENDED ACTION.** Read them before any method rests on them. Replace the refutation test with trusted-flooded
  recall.

**Verdict: REJECT (as a research question).** C4 cannot be validated on real cloud within the rules: there are no
two-date cloud labels at this resolution, the shadow class has no labels anywhere, and a real-data check would need
labels we may not make. Its synthetic check uses the model it assumes. Roads it would give back cannot be scored for
"dry" anyway, and bright floodwater can look like opaque cloud to it. Its narrow core is worth keeping: whether a
two-date test's errors depend on flood state. That merges with C1's mask threat into F3.

---

### C5. Does the VLM talk about roads it cannot see?

**Score reasons.**
- Importance 2: it matters for CSI 709 and for the role rule, less for this paper.
- Novelty 2: the sources are all preprints or workshop papers, so no gap can be shown under the citation rule.
- Testability 3: synthetic opaque cloud gives a clean truth for visibility.
- Identification 3: paired arms on the same crops.
- Data adequacy 3: crops and the local model exist.
- Spatial validity 1: the unit is a crop; there is no spatial question.
- Robustness 2: prompt wording and the text parser both sway the result.
- Feasibility 4: runs locally within the memory limits.

**Required checks.**
- *What would falsify it?* Gemma rarely claims a flood state without the mask, or the rate does not fall with it.
- *Scale.* Crop size sets what Gemma can see; not stated.
- *Autocorrelation or leakage.* Not relevant; nothing is trained.
- *Causal claim.* "The mask in the prompt reduces claims" is justified by the paired design. It is a claim about
  prompt compliance, not perception.
- *Does the evidence discriminate?* Between arms, yes. About whether Gemma can see cloud, only the no-mask arm says
  anything.
- *Second dataset.* None.
- *Answerable?* Yes, but the answer is close to expected.

**Issues.**

**C5-1. No meaningful spatial component.**
- **LOCATION / TARGET.** C5 "spatial checks: few"; boundary condition.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** The input card requires one.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Do not carry it as a candidate for this paper.

**C5-2. The main hypothesis tests prompt compliance.**
- **LOCATION / TARGET.** C5 hypothesis 2.
- **SEVERITY.** Major.
- **WHY IT MATTERS.** Telling a model a road is hidden and then finding fewer claims about it is expected. The
  informative arm is Gemma's own visibility word, without the mask, on roads hidden by synthetic opaque cloud.
  Comparing that word with the dark-rise mask is not accuracy, because the mask is unvalidated (X1).
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** If ever run, lead with the no-mask arm. Use synthetic opaque cloud and the bright mask as
  references only.

**C5-3. Sources and measurement.**
- **LOCATION / TARGET.** C5 "main threat".
- **SEVERITY.** Minor here (major if C5 were a paper).
- **WHY IT MATTERS.** Kethavath & Hu, RemoteShield and CloudWeb are preprints or workshop papers. A free-text parser
  adds error. Any human coding of Gemma's text would be our own annotation.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Use forced-choice JSON answers parsed by code, as the project already does. Keep it out of
  this paper.

**Verdict: REJECT (for this paper).** C5 has no meaningful spatial component, which the input card requires. Its main
hypothesis mostly tests whether Gemma follows its prompt. Its supporting sources cannot carry a novelty claim under the
citation rule. The one informative part, whether Gemma on its own says a hidden road cannot be seen, belongs to the
CSI 709 thread. At most it is a short optional appendix in the reporting candidate, with forced-choice answers.

---

## 7. What goes forward to the refinement pass

### F1 (lead): C2 revised. Graded haze and partial cover on clear roads

**Question.** On clear roads with trusted labels, how do flooded recall and the dry-call rate fall as haze thickens
and covers more of a road's strip? Do frozen DINOv2 change cues lose less than classical cues, from matched clean
accuracy?

**Must change.**
1. Primary hypothesis: DINOv2 against classical, from matched clean accuracy (83.3% against 83.1%). Drop "falls
   steadily" as a hypothesis.
2. Add strip coverage and distance from the cloud edge to the thickness grid. Use it to check the 20% road rule.
3. Make the haze for the de-hazing arm by a process the de-hazer does not invert.
4. Replace the accuracy realism check with an image-statistics check on all 93 thin-cloud strips. Keep the accuracy
   comparison as a consistency check only.
5. Match HRC_WHU shapes to 0.5 m.
6. Tile-block test primary. Fix the primary thickness, metric and stop rule before running. One blocked-fold
   sensitivity run.
7. Scope claims to synthetic haze on Louisiana-East.

### F2: C3 + C1 merged. Scoring and reporting flood-road maps when labels go missing under cloud

**Question.** How much does a reported flood-road score depend on labels that cloud left missing? What should a map
report so a user knows where it abstains and what that hides?

**Must change.**
1. Use a fixed classifier. Vary only the abstention cut-off.
2. Report misses on trusted flooded roads as measured. Report everything under cloud as a range (X3).
3. Bring in C1's re-scoring of the same calls with and without cloudy roads.
4. Add a cannot-assess map and a range for flooded road length.
5. Report the labelling result as a check of the dataset's documented rule, not as a discovery.
6. Drop hypotheses that rest on untrusted labels (the 10 roads).
7. No ranking of overlapping curves.
8. Check the Olofsson and Geifman citations against what each paper did.
9. Any sealed use goes in the same batched look as the frozen model.

### F3: C1's mask threat + C4's narrow core. Is the cloud mask's error independent of flood state?

**Question.** Does the two-date dark-rise mask flag haze less often over floodwater (or near it) than over dry
ground? If so, does a two-date correlation test, after Hagolle et al., reduce that bias?

**Why it goes forward.** F1's realism check and F2's road rule both use this mask. If its errors follow flood state,
both inherit a bias. This question can be answered within the rules: synthetic haze on clear roads, real floor values,
and HRC_WHU recall by land cover.

**Must change.**
1. Scope it to the bias question only. No four-way split; no shadow class.
2. Start with the three X1 checks.
3. Read Hagolle et al. 2010 and Makarau et al. 2014 in full before using them.
4. Fix the "equal flag rate" margin before running.
5. Expect it may become a methods section of F1 or F2, not its own paper. If X1 finds no floor difference, it
   shrinks to one paragraph.

**Not carried forward:** C4 as written, and C5 (optional appendix to F2 at most).

---

## 8. Unresolved issues

1. **Mask validity (X1).** The dark-rise mask is unvalidated, and its errors may follow flood state. Nothing can be
   built on it as truth until the X1 checks are done.
2. **No truth under cloud (X3).** Under cloud, labels can only be bounded.
3. **Power (X2).** The opaque-cloud label contrast rests on 5 tiles and 3 flooded labels. The recall drop under
   cloud is not established at tile level.
4. **Spatial leakage (X4).** Shuffled tile folds put neighbours in different folds. Absolute numbers may be
   optimistic.
5. **External validity (X7).** No permitted second dataset with real cloud and flood labels at 0.5 m. Germany's
   cloud content and label coding are unknown and can only be learned by spending it.
6. **Label count.** 1,080 label rows against 1,037 touched roads (both development data). The gap is not explained in
   the files read.
7. **Clear-sky "missing = dry".** Untested. If analysts also missed flooded roads in clear sky, the trusted-label
   rule is weaker than assumed.
8. **Citations.** Hagolle and Makarau read as abstracts only; Cloud-Adapter values from a page-fetch summary;
   Olofsson's JIF and claim match unchecked; the conference rule conflict (Geifman).
9. **Novelty (X6).** Waits for the GMU library round and Justin's check of the references.
10. **Decisions for Justin** (beyond Stage 1's list):
    - May cloud pixels (not only outlines) from HRC_WHU development images be used to make synthetic haze?
    - Is treating a missing label under cloud as "unknown" in scoring still "unmodified labels"? (His road-rule
      decision suggests yes.)
    - Should all frozen analyses (model, F2 scoring, F3 mask) share one batched sealed look?

## 9. Suggested next scientific action

Run three cheap checks on development data, through Tilt, before the refinement pass. They need no new data and no
sealed data.

1. **Floor check (X1).** On the 798 clear roads, compare the after-image and before-image floors (darkest pixel
   within 20 m) on flooded against dry roads. Then add even haze at a few thicknesses fixed in advance and record the
   dark-rise flag rate on each group. Use a tile-block interval and an "equal" margin set before running.
2. **HRC_WHU recall by land cover.** From the existing run on the 120 development images, report the dark mask's
   recall (not only F1) on water scenes against vegetation scenes.
3. **Power.** Compute the tile-block minimum detectable difference for F1's primary contrast (798 roads, 193 tiles)
   and for trusted-flooded recall under cloud (24 roads).

**Go/no-go.**
- If check 1 shows no floor difference, F3 shrinks to a paragraph. F1 leads, and F2 reports the label finding as a
  range.
- If it shows a difference, F3 must be done before F2's numbers or F1's real-cloud comparison mean anything. F1 still
  leads, because its clear-road labels and synthetic haze do not depend on the mask.

Then write a one-page pre-registration for F1: hypotheses, the haze generators, the thickness × coverage grid, the
primary test and the stop rule.

This differs from Stage 1, which proposed pre-registering C1 first. My reason: C1's identification is the weakest of
the three that go forward. Even if its two checks pass, its opaque result is predicted by the dataset's own rule.
