# Methodology review: methodology_v1 (Stage 5, Methodology Critic)

Stage 5 of the Assignment 3 workflow. Claude wrote this on 2026-10-23, working alone from local files, with no
sub-agents and no web search. It reviews `outputs/methodology_v1.md` as a skeptical scientific reviewer would: can the
plan support the inferences its questions claim?

- **Same model.** I run on the same model as the methodology's author and the earlier critic. Where I agree with
  either, that is not independent validation (AGENTS.md rule 4).
- **No new results.** I ran no model and scored nothing. My own checks read tile ids, source-image file names and code
  only (section 0). No imagery, labels or outcomes were read.

Tags:
- **Evidence:** a number or statement found in a file. The file is named.
- **Inference:** my reasoning. It has not been measured.

---

## 0. Inputs used

- **Rules and role:** `05_Project/AGENTS.md`; `05_Project/agents/scientific_critic.md` (and `methodology_agent.md`, to
  check the required components).
- **Problem and decisions:** `CloudResearch/input_card.md`; `CloudResearch/decision_log.md`.
- **Questions:** `outputs/selected_questions.md` (Q2 leads, then Q3, then Q1).
- **Under review:** `outputs/methodology_v1.md`.
- **Context:** `outputs/abstract_v1.md`; `outputs/question_review.md` (the earlier critique);
  `outputs/research_questions_refined_v3.md` (its Q2, Q3 and §10, to cross-check what the methodology cites).
- **Evidence:** `evidence/01` to `04`, and `evidence/05_reconstruction_literature.md`. File 05 appeared while I was
  working. I read it in full and use it.
- **My read-only checks** (no imagery, labels or outcomes):
  1. `Project/docs/datasets/splits/sn8_louisiana_east_stratified_2026-10-16.csv`: neighbours of the 40 sealed test
     tiles on the tile grid; grid extent of the development tiles.
  2. `ProjectBranch/Images/SN8_Louisiana-East_Ida2021/source/Louisiana-East_Training_Public_label_image_mapping.csv`:
     source-image ids, counted for the 226 development tiles only. **Disclosure:** the `head` preview of this file
     also printed one north-set row's file names. I did not use it.
  3. `Project/docs/datasets/splits/hrc_whu_authors_2026-10-23.csv`: images per land-cover type and split.
  4. `ProjectBranch/ClaudeFunctions/sn8_clouds.py`: the `dehaze` function (He et al. de-hazing).
  5. `ProjectBranch/ClaudeFunctions/sn8_refhaze.py`: the §6.4 prototype's code. Its file time (20:20) is after the
     methodology's (20:07). I read the settings and the fit, not any result.

## 1. Assumptions

- v1 is the plan that will be frozen in the week-1 pre-registration. So I judge it as a protocol, not as prose.
- Justin's pending rulings (synthetic truth, HRC_WHU use, the ceilings, where §6.4 sits, his two-pass idea) are open.
- Production stays frozen during the paper (v1 §16).
- "Reliable", "represent" and "finds change" are judged twice: against v1's own definitions, and against what a reader
  would take them to mean.

---

## 2. New facts from my checks

**Evidence (mapping file, development tiles only).**
- **One after image.** All 226 development tiles take their after image from one acquisition (id `10300100C46F5900`).
  No development tile has a second after image.
- **Two before images.** Area 0 (105 tiles) uses one before acquisition (`105001001A0FFC00`). Area 2 (121 tiles) uses
  another (`10300100AF395C00`).
- **Inference.** Every real cloud in the development data comes from one image, taken at one moment. The 39 thin-cloud
  tiles and the 17 opaque tiles are parts of one cloud field. "Area" is the same as "before image". So
  leave-one-area-out tests a new before image and a new place, never a new cloud scene.

**Evidence (split file).**
- **39 of the 40 sealed test tiles** have at least one development tile among their 8 neighbours. The mean is 4.4 of 8.
- 225 of the 226 development tiles have a development neighbour.
- With square blocks of 3, 5 and 7 tiles a side, the development tiles fill 61, 33 and 22 blocks (both areas).

**Evidence (HRC_WHU split file).** 24 development and 6 test images per land-cover type, for all five types. This
confirms v1's counts.

**Evidence (`sn8_clouds.dehaze`).** He et al. de-hazing estimates **one air light per tile**: the brightest pixel among
the haziest 0.1%.

**Evidence (`sn8_refhaze.py`, as read).** The prototype differs from §6.4 in several places:

| Setting | §6.4 (proposed) | Prototype (as read) |
|---|---|---|
| Fit window | 100 m (200 px); sensitivity 50 m | 64 m (129 px) |
| Opaque floor | t̂ = 0.3 | 0.2 |
| Guard 1: leave the road's strip and 10 m ring out of its own fit | Yes | **Not present.** The local fit uses all valid pixels, reweighted by residual only |
| Guard 2: robust fit | Trimmed; large negative residuals dropped first | Symmetric: drops \|residual\| > 2.5 robust SD, 3 passes |
| Gain and offset (a, b) when the whole tile is cloudy | From clear training tiles of the same before–after pair | From the tile's own pixels that the dark-rise mask calls clear; if fewer than 1,000, falls back to g = 1, h = 0 |
| Sign rule | Not stated | Only t ≤ 1 with L ≥ 0 counts as haze. Anything else is left alone |

- The docstring names the known risk itself: "a flood bigger than the window that also brightens would be read as haze
  and removed".
- **Inference.** Under whole-tile synthetic cloud (§6.4's primary cell), the tile's "clear" pixels are themselves
  hazed, or there are too few of them. Then either g and h absorb the haze (t̂ ≈ 1, so little is corrected), or the
  code falls back to g = 1, h = 0. In the second case the correction maps the cloudy date onto the before image's
  look. That is the failure §6.4 warns against ("a corrected tile would look less changed than a clean tile").

**Evidence (05, read in full).**
- §6.4 is **relative radiometric normalisation**, a known family: IR-MAD (Nielsen 2007; Canty & Nielsen 2008), PIF
  normalisation (Du et al. 2002). The closest match is Lin et al. (2015, ISPRS JPRS). It was read at TLDR level only.
- The stable-surface methods "degrade when the landscape changes very quickly" (Hagolle et al. 2015, abstract). A flood
  is such a change.
- Filling from the before date "paints the dry road back", so a flooded road becomes "no change" (05 §6).
- No paper was found that scores change, damage or flood mapping through reconstructed pixels (05 §3).
- Training on real clouds beat training on synthetic ones (Ebel et al., SEN12MS-CR; abstract).
- VPint2 (Arp et al. 2024) supports evaluation by transferring cloud masks onto clear images. That is the bed's design.

---

## 3. Summary judgement

v1 is careful. It has a pre-registration, tile-resampled intervals, margins that fail safe, three tiers, ranges where no
truth exists, tipping counts, a cut list and one sealed look. Most of the earlier critic's points are answered.

But several inferences are not yet supported. Some can be fixed by tighter definitions:
- S1 ("this road is hidden") is Q2's only statement that can reach "reliable". As written, its real-cloud test scores
  masks the map does not use, on imagery that is not Maxar.
- Q1's pass rule cannot tell good synthetic cloud from bad.
- Q1's verdict does not bind Q2's tiers.

Others need a different sampling frame:
- All real cloud comes from one after image.
- The sealed tiles sit among the development tiles.
- The tile is not an independent unit for cloud or for flood.

§6.4 is not ready to be a formal test. The prototype and the plan disagree, the development data it will be judged on
has already been looked at, and family X favours it over its comparator by construction.

---

## 4. Scores (1 = weak, 5 = strong; my judgement of what the plan can support)

| Part | Importance | Novelty / gap | Testability | Identification | Data adequacy | Spatial validity | Robustness / validation | Feasibility |
|---|---|---|---|---|---|---|---|---|
| Q2 (lead) | 4 | 3 | 3 | 2 | 2 | 3 | 3 | 4 |
| Q3 | 3 | 3 | 4 | 3 | 4 | 3 | 3 | 4 |
| Q1 | 4 | 3 | 2 | 2 | 2 | 3 | 2 | 3 |
| §6.4 option | 4 | 2 | 3 | 2 | 3 | 3 | 2 | 3 |

Reasons are in the issues below. The scores are not comparable with the earlier critic's, which scored candidates, not
a plan.

## 5. The role's required checks, per question

| Check | Q2 | Q3 | Q1 | §6.4 |
|---|---|---|---|---|
| What would falsify it? | S2/S3 bounds above their ceilings (reachable). What happens if S1 fails is **not defined** (M5) | Interval at opaque cover includes 0. But the "no" rule needs all four levels to fail (M10) | Any margin missed (near-certain); control passes too (near-impossible) (M13) | Safety veto fires; or no gain over He de-hazing; or gain on M only |
| Scale aligned? | Strip 5 m; dark window 20 m; HRC_WHU 0.5–15 m. S1's real half mixes pixel and 10 m windows across resolutions | Strip and 10 m ring; fine | 7 m cells, 32 m windows; HRC shapes rescaled (blocked) | 64 m or 100 m window against a flood that may be larger |
| Autocorrelation or leakage inflate it? | Yes. The tiers use **absolute** error rates, which neighbour leakage lowers (M3) | Mostly paired; small | Real-cloud reference is one cloud field (M1) | Prototype has seen the scoring roads (M18) |
| Causal claims justified? | H2b ("cloud causes missing labels") is not identified (M9) | Yes, for synthetic before-image cloud | "Represent" is a fit-for-use claim; the use is not tested (M14) | Only on synthetic cloud |
| Does the evidence discriminate alternatives? | H2b: label omission vs mask false alarms on dry ground; no | At opaque cover: information loss vs the forest's behaviour on out-of-range input; no (M11) | Good vs bad cloud: no, as the pass rule stands | Cloud vs flood in the fit: only where flood is a minority of the window |
| Second dataset? | HRC_WHU for S1's single-date half only; no second flood event (Germany, Justin's call) | North negative set (Justin's call) is the only real false-alarm test | HRC_WHU, a different imagery source | None |
| Answerable with the data? | Partly. S4/S5 by design are ranges | Yes | Partly | On synthetic cloud only |

---

## 6. Issues

### A. Across the questions

#### M1. All real cloud comes from one after image

- **ISSUE.** The tile is treated as the sample for real cloud. But every cloudy development tile is part of one
  acquisition's cloud field.
- **LOCATION / TARGET.** §3.1 (real thin-cloud and opaque rows); §4; §6.3 step 2 (the real thin level); §6.3 step 3
  (check 1); §10.2; §10.3 scheme 3; §10.5 ("one event, one sensor").
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (my check):** one after acquisition for all 226 tiles; one before acquisition per area.
  - **Inference:** the 39 thin-cloud tiles and the 17 opaque tiles are not independent draws of "real cloud". They are
    pieces of one weather moment. Tile-resampled intervals for real-cloud quantities are too narrow for any claim about
    cloud in general.
  - **Inference:** the real thin level, the generator's air light (from the 17 opaque cores) and check 1's real
    reference all describe one cloud scene.
  - **Inference:** leave-one-area-out swaps the before image and the place. It never swaps the cloud.
- **EVIDENCE NEEDED.** The cloud clusters on the tile grid: how many separate patches of real thin and opaque cloud
  there are. This is label-free and uses masks that already exist.
- **RECOMMENDED ACTION.**
  - Say in the data section: one after acquisition, two before acquisitions.
  - Scope every real-cloud statement to "the cloud in one Maxar acquisition".
  - Report the number of cloud patches beside the tile count.
  - For real-cloud quantities, resample by patch or spatial block, not by tile (see M3).
  - Lean on HRC_WHU for cloud variety, and say that it is another imagery source.

#### M2. The sealed look is neither external nor powered, and has no decision rule

- **ISSUE.** The one sealed look is the plan's only validation. It is interleaved with the development tiles. It is
  small. It has no rule for what counts as a confirmation or a failure.
- **LOCATION / TARGET.** §3.3; §15 week 7; §16 ("reported whatever they are").
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (my check):** 39 of 40 test tiles touch a development tile (mean 4.4 of 8 neighbours). The frozen
    setup is fitted on all 226 development tiles (v1 §3.2). So the sealed look shares the neighbour leakage. v1 says
    this already (§3.3, §12).
  - **Inference:** 40 tiles against 190 makes intervals about 2.2 times wider (√(190/40)). An H1b difference
    detectable at about 6–10 points on development data needs about 13–22 points on the sealed tiles.
  - **Inference:** by the development share (39 of 226 tiles with thin cloud), the 40 test tiles may hold about 7
    thin-cloud tiles and about 3 opaque ones. Q2's real-data parts (H2a, H2b, real recall) can say almost nothing there.
  - **Inference:** the 30 HRC_WHU test images give 6 per type. A per-type margin of ±0.10 cannot be shown on 6 images.
  - Without a pre-set rule, any sealed result can be read as "consistent".
- **EVIDENCE NEEDED.** The interval widths each sealed test would have, computed now from the development calls,
  scaled to the sealed counts.
- **RECOMMENDED ACTION.**
  - Pre-register a sealed decision rule per primary result. For example: "confirmed" if the sealed estimate has the
    same sign and lies inside the development interval; "not confirmed" otherwise; "uninformative" if the sealed
    interval is wider than a set limit.
  - Pool the HRC_WHU test images across types for the sealed check of Q1.
  - Do not re-score Q2's real-data parts on the sealed tiles unless they hold enough cloud. Count the sealed cloud
    with the frozen masks inside the same look, and apply a pre-set minimum.
  - Ask Justin early (decision 4) about the north negative set. It is the only real false-alarm test for Q3's
    after-only call.
  - Call the sealed look "held-out, same scene" in the paper, never "external".

#### M3. Tile resampling and shuffled folds overstate independence, and the tiers use absolute rates

- **ISSUE.** Two dependence problems remain:
  - The intervals resample tiles as if they were independent. Neighbouring tiles share flood and cloud.
  - The tier rule compares **absolute** error rates with ceilings. Neighbour leakage lowers absolute error.
- **LOCATION / TARGET.** §8 tier rule; §9 rules ("tile-resampled intervals are the primary test everywhere"); §10.3
  (sensitivity in week 6 only); §8 block-size rule.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (critic X4):** shuffled folds put neighbours in other folds, which can inflate absolute scores. The
    critic rated this major for absolute numbers.
  - **Evidence (my check):** 225 of 226 development tiles have a development neighbour.
  - **Inference:** S1 (on the bed, mask only) has no model, so leakage does not touch it. But S2, S3 and the Q3
    go/no-go are absolute rates of a fitted model. Leakage pushes them towards "pass".
  - **Inference:** a tile bootstrap with correlated tiles gives intervals that are too narrow. That also pushes upper
    bounds below ceilings.
  - **Evidence (my check):** blocks of 7 tiles a side leave only 22 occupied blocks. The rule "block side = the
    semivariogram range, at least 3 tiles" has no upper limit. A long range could leave too few blocks for five
    stratified folds.
- **EVIDENCE NEEDED.** The semivariogram range of tile flood share (planned for week 1). The interval widths from a
  spatial block bootstrap with that block size.
- **RECOMMENDED ACTION.**
  - Decide every tier on blocked-fold calls, or require a pass under both shuffled and blocked folds.
  - Use a spatial block bootstrap (same block size) for the tier bounds and the primary intervals. At least report it
    beside the tile bootstrap in figure 12.
  - Cap the block side (say at 7 tiles) and say what happens above the cap.
  - Move the blocked-fold run from week 6 to the same week as each primary result. A sign change found in week 6 has
    no time left to act on.

#### M4. "Missing means dry in clear sky" has a known mechanism against it, and the tipping counts have no anchor

- **ISSUE.** The bed, Q3, S2, S3 and H1b all treat a missing label on a clear road as "dry". v1 handles this with
  tipping counts and one descriptive check. It does not name the most likely cause of clear-sky omission, and a tipping
  count alone cannot say whether it is likely to be crossed.
- **LOCATION / TARGET.** §1 (labels); §11 row 2; §12 ("Untrusted dry labels"); §18 item 1.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (01):** analysts were told to "only attribute what was visible" (Hänsch et al. 2022, p. 3).
  - **Evidence (01, related checks):** a visibility gate for trees and shadow exists, from a road detector on the
    before image.
  - **Inference:** cloud is not the only thing that hides a road. Overhanging trees and building shadow do it in clear
    sky. By the same rule, a flooded road under trees may be left unlabelled. So clear "dry" roads may hold flooded
    roads, and the bias would cluster by neighbourhood.
  - **Evidence (my arithmetic on 01, as in v1 §8):** about 91 of about 357 dry-labelled assessable roads get a
    "flooded" call (about 25%). Some of these may be right.
  - **Inference:** a tipping count such as "12 wrong labels would flip it" means nothing unless the reader knows
    whether 12 is likely.
- **EVIDENCE NEEDED.**
  - The visible share (from the existing gate) on clear flooded against clear dry roads.
  - If buildings are counted in week 1: clear "dry" roads that pass through the 10 m ring of buildings labelled
    flooded. This uses published labels only, as a diagnostic, and changes none.
- **RECOMMENDED ACTION.**
  - Add a pre-set sensitivity run: repeat S2, S3, H1b and H3a on clear roads with a high visible share.
  - Report each tipping count as a share of clear dry roads, beside the diagnostic rates above.
  - Keep the rule that no label is changed.

### B. Q2 (the lead)

#### M5. S1's real-cloud test scores masks the map does not use, on imagery that is not Maxar

- **ISSUE.** S1 is the only statement v1 says can reach "reliable". Its real-cloud half scores the bright and the
  single-date dark masks on HRC_WHU. But the map's "hidden" statement comes from the tile rule (bright mask, tile
  level) plus the road rule (dark rise, two dates). The single-date dark mask is not part of that rule. The bright mask,
  which is part of it, has a recall of 0.28.
- **LOCATION / TARGET.** §6.1 table row S1 and step 3 (S1, single-date half); §8 S1 rows; §6.1 "What counts as no".
- **SEVERITY.** **Blocking** (for the pre-registration).
- **WHY IT MATTERS.**
  - **Evidence (01):** adopted rule = tile rule + road rule. The bright mask: precision 0.81, recall 0.28. The dark
    mask: precision 0.62, recall 0.68. "The two-date dark-rise mask cannot be checked on HRC_WHU (single date)."
  - **Evidence (v1 §8):** the S1 missed-hidden ceiling (≤ 30%) is justified by "dark-mask recall 0.68 on HRC_WHU".
  - **Inference:** if S1 means the map's actual rule, its real half can only test the bright part. At recall 0.28
    (72% missed) it very likely fails the 30% ceiling, unless the window rule changes recall a great deal. If S1 means
    the dark mask, the claim is about a mask the map does not use, and production is frozen.
  - **Inference:** the tile rule acts on a whole tile (at least 20% bright). Scoring the bright mask in 10 m windows
    does not reproduce it.
  - **Inference:** HRC_WHU is Google Earth imagery at 0.5–15 m, converted to grey. A pass there is a claim about that
    imagery, not about Maxar tiles from one acquisition.
  - **Inference:** v1's "no" ("every statement except 'this road is hidden' fails") assumes S1 passes. If S1 fails,
    the paper has no pre-set reading.
- **EVIDENCE NEEDED.** None new. A definition.
- **RECOMMENDED ACTION.**
  - Define S1 as the statement made by the frozen rule (tile rule + road rule). Test exactly that rule.
  - On HRC_WHU, test the bright tile rule at a tile-like unit (for example, 256 × 256 patches flagged at 20% bright),
    per type. Report the dark mask only as a candidate for later promotion, not as S1.
  - Pre-set what Q2 says if S1 fails: "a map cannot reliably say even where it cannot see".
  - State in the tier that the real half was measured on HRC_WHU imagery.
  - Decide per type or pooled before scoring. On barren and snow the dark mask's false alarms are known to be high
    (01; v3).

#### M6. S2 and S3: the scored set, the base rate and the cited interval are not pinned down

- **ISSUE.** S2 ("flooded" calls wrong) and S3 ("dry" calls wrong) are predictive error rates. They depend on how many
  flooded roads sit in the scored set. v1 scores them on "roads the road rule flags" and "also on all clouded roads",
  without saying which one decides the tier. The 25% ceiling is justified with intervals from a different statistic.
- **LOCATION / TARGET.** §6.1 step 4 (S2 and S3); §8 rows S2 and S3; §9 row "Q2 S2, S3 on the bed".
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (v1 §8):** "bed intervals at thin levels are about ±4 to ±7 points". **Evidence (03):** those are
    intervals for the flooded-minus-dry gap in flag rates, at 95%. The tier rule uses a 98.3% one-sided bound on an
    error share. Different statistic, different level.
  - **Evidence (03):** under uniform haze at t = 0.9 and 0.8, the road rule flags about 5% and 15% of the 769 clear
    roads. At t = 0.7 to 0.5 it flags flooded roads 7.5 to 13.2 points more often than dry ones.
  - **Inference (rough arithmetic; assumes clean-like call rates):** at t = 0.8, about 117 roads are flagged and about
    70 get a "flooded" call. A 19% error on 70 calls has a one-sided 98.3% bound near 29%. So S2 on the flagged set
    can fail its 25% ceiling from sample size alone. On all 769 clouded roads it can "just pass", as v1 says. **The
    choice of scored set decides the outcome.**
  - **Inference:** where the mask flags flooded roads more often, the flagged set holds more flooded roads. That
    lowers S2's error and raises S3's by arithmetic, with no change in the model.
  - **Inference:** a ceiling set at "clear-sky error plus noise" makes "reliable" mean "no worse than the clear-sky
    map". The clear-sky map is itself wrong about 1 time in 5 on "flooded" calls. Readers will hear more than that.
  - **Evidence (v1 §9):** "a 'no' from a test that is too weak is reported as 'inconclusive'". **Evidence (v1 §6.1):** a
    statement that misses its ceiling drops a tier. Two rules for the same event.
- **EVIDENCE NEEDED.** At Gate 0: the expected size of each scored set at the real thin level, and the 98.3% one-sided
  bound a clear-sky-like error would get there.
- **RECOMMENDED ACTION.**
  - Pre-set one scored set for the tier (I suggest all clouded roads in the whole-tile cell). Report the flagged set as
    secondary.
  - Report recall and specificity beside S2 and S3. They do not move with the base rate. Show the flooded share of each
    scored set.
  - Restate the tier as non-inferiority: "upper bound of (hidden error − clear error on the same roads) below δ", with
    δ fixed now. Write "as reliable as the clear-sky map" in the paper, not "reliable".
  - Split the outcome in two: "fails: error too high" and "not shown: interval too wide". Use only the first for Q2's
    "no".

#### M7. Q1's realism verdict does not change Q2's tiers

- **ISSUE.** If Q1 shows the synthetic cloud is not like real cloud, S2 and S3 stay "synthetic only", with a note. The
  question asks what a map can say about roads hidden by **real** cloud.
- **LOCATION / TARGET.** §6.1 step 6 ("synthetic only, realism not shown"); §15 Gate 2 ("not a stop").
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Inference:** an error rate measured on cloud shown to be unlike real cloud says nothing about
  real hidden roads. Keeping the tier name invites readers to treat it as evidence. The dependency on Q1 is then only a
  label.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Pre-set: if family X fails realism at the real thin level, S2 and S3 count as "range only"
  for Q2's answer. The bed's numbers go in as a sensitivity result, clearly marked.

#### M8. Much of Q2's answer is fixed by design, and its primary test is unclear

- **ISSUE.** By v1's own reasoning, S2 and S3 can at best reach "synthetic only", and S4 and S5 are ranges by design.
  So the table of tiers is largely known before any data. v1 also promises "one primary test per question" but Q2 has
  four or more ceilings.
- **LOCATION / TARGET.** §6.1 ("what the rule allows by construction"); §8 tier interval; §9 and §16 ("one primary
  test per question"); abstract sentence 19.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Inference:** a reviewer may say the lead question's result follows from the label coding, not from the data.
    The empirical content is in S1, the bed's S2 and S3, H2a, H2b and the width of the ranges.
  - **Evidence (v1 §8):** the Bonferroni split covers "three statements". S1 alone has two rates (missed and false
    hidden), and two halves (single-date, two-date). So there are at least four ceilings, more if halves count
    separately.
  - **Evidence:** `selected_questions.md` and the abstract say "95% interval". §8 says "98.3% one-sided". Not the same.
  - **Inference (H2a wording):** reading missing labels as dry can raise the score (dry calls on unlabelled flooded
    roads count as right) or lower it (flooded calls on them count as wrong). "Inflation" names one direction only.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.**
  - Mark each row of the tier table as "empirical" or "fixed by the label coding".
  - Name Q2's primary test. I suggest S1 as defined in M5, with the bed's S2 and S3 as co-primary only if Justin
    agrees.
  - Count every ceiling in the multiplicity rule. Use one confidence wording everywhere.
  - Call H2a "the change in the reported score from counting hidden roads", and read it beside the S4 bounds.
  - Report the S4 and S5 range widths as results, with a pre-set note on what width a user could act on.

#### M9. H2b does not separate label omission from mask false alarms on dry ground

- **ISSUE.** H2b asks whether cloudy roads on a tile carry fewer flooded labels than clear roads on the same tile. The
  "cloudy" roads are chosen by the dark-rise mask. Non-cloud brightening also raises the dark floor, and floodwater
  lowers it.
- **LOCATION / TARGET.** §6.1 step 3 (H2b); §8 row Q2b.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (critic X1):** "any non-cloud change that brightens the darkest pixels raises the floor. Flooding lowers
    it. So non-cloud false alarms also lean towards dry roads."
  - **Evidence (03):** the uniform-haze check tested how the mask reacts to haze. It did not test false alarms without
    haze.
  - **Inference:** so a within-tile gap can come from the mask flagging changed dry ground, not from analysts skipping
    hidden floods. The tile stratum removes geography between tiles, not within them.
- **EVIDENCE NEEDED.** The dark-rise distribution on clear flooded against clear dry roads with no cloud, near the
  threshold (label-free cues, published labels, development data). If dry roads sit much closer to the threshold, false
  alarms favour dry.
- **RECOMMENDED ACTION.**
  - Run that check in week 1, before H2b is scored.
  - As a pre-set sensitivity, restrict H2b's cloudy roads to those within a fixed distance of an opaque core (bright
    mask). Those are more likely to be real cloud.
  - Word H2b as "roads the mask calls cloudy carry fewer flooded labels". Do not claim omission unless the check rules
    out false alarms.

### C. Q3

#### M10. The "no" rule for H3a gives four chances to pass

- **ISSUE.** v1's primary test for H3a is at opaque cover. But its "no" needs the interval to include 0 "at every
  level, opaque included". So a pass at any one of four levels counts as "yes".
- **LOCATION / TARGET.** §6.2 "What counts as no"; §8 row H3a; `selected_questions.md` Q3 "no".
- **SEVERITY.** Major.
- **WHY IT MATTERS.** **Evidence:** §8 tests H3a "at opaque cover"; §6.2 needs failure at all four levels;
  `selected_questions.md` states a single interval. **Inference:** four uncorrected looks raise the chance of a false
  "yes".
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** Decide H3a at opaque cover only. Report the other three levels and the crossover as
  secondary, Holm-adjusted.

#### M11. At opaque cover the comparator is a model fed a blank before image

- **ISSUE.** At opaque before-image cloud, the two-date model gets a flat before image. Whether it then does better or
  worse than the after-only model mostly reflects how the random forest behaves on input it never saw. It is not a
  measure of how much the before image is worth. And a pass says nothing about whether the after-only call is good
  enough to put on a map.
- **LOCATION / TARGET.** §6.2 steps 1 and 3; §8 Q3 go/no-go (lower bound ≥ 0.60) and H3a.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (v1 §9):** "Large effect expected at opaque cover (inference)". **Evidence (v1 §6.2):** the "no" "could
    happen, because the forest already holds the `_after` cues". So the result depends on the forest's response to
    out-of-range before cues.
  - **Inference:** a go/no-go of 0.60 is a low bar against the two-date model's clean balanced accuracy of about 0.81
    (v1 §8, derived). An after-only model at 0.62 could "win" against a broken two-date model and still be worse than
    abstaining.
  - **Evidence (v3, Q3):** the main project's post-only controls flagged 72–89% of damaged buildings on a no-change
    pair. They read state, not change.
- **EVIDENCE NEEDED.** The clean gap between the after-only and two-date models on the same roads (planned in week 2).
- **RECOMMENDED ACTION.**
  - Make the clean gap (two-date minus after-only, both clean) a reported primary quantity. It is a real-image
    measurement of what losing the before image costs.
  - Add a comparator that handles the missing date in the usual way: the two-date model with its before-image and
    change cues set to their training means.
  - Add a usefulness bar: the after-only call may stand in on a map only if its errors meet Q2's S2/S3 ceilings (or the
    non-inferiority δ of M6). Otherwise the answer is "abstain".

#### M12. H3b rests on an unmeasured water mask

- **ISSUE.** The permanent-water group comes from a classical greyscale water mask whose errors are unknown. The group
  size is unknown.
- **LOCATION / TARGET.** §6.2 step 4; §8 row H3b.
- **SEVERITY.** Minor (H3b is secondary, and v1 gates it on power).
- **WHY IT MATTERS.** **Evidence (01):** on before images, an absolute dark-channel mask fired on bright calm water
  and bare ground. **Inference:** grey water masks confuse water with dark or smooth ground, so the group may be
  impure.
- **EVIDENCE NEEDED.** The group size and a picture audit of a pre-set random sample, as pictures only.
- **RECOMMENDED ACTION.** Keep the power gate. Fix the threshold on training tiles, as planned. Report H3b only as
  descriptive if the picture audit shows the mask is mostly not water.

### D. Q1

#### M13. Q1's pass rule cannot tell good synthetic cloud from bad

- **ISSUE.** The generator must meet every margin. The control must miss at least one. There are many margins. So the
  generator is very likely to fail somewhere, and the control is very likely to miss something, whatever their realism.
  There is no direct test of "X is closer to real cloud than the control". And under whole-tile placement, family M is
  the control.
- **LOCATION / TARGET.** §6.3 steps 1, 3, 4 and "What counts as no"; §8 rows Q1 check 1, check 2, control.
- **SEVERITY.** **Blocking** (for the pre-registration).
- **WHY IT MATTERS.**
  - **Evidence (v1):** check 1 has 3 statistics × an unstated number of rise bins. Check 2 has 5 types × 2 masks = 10
    margins.
  - **Inference (illustration):** with 3 bins there are about 19 margins. If each equivalence test had 80% power and
    they were independent, a truly matching generator would pass all of them with probability about 0.8^19 ≈ 1%. A
    control that is truly within the margins would still miss at least one most of the time.
  - **Inference:** per-type exclusion ("a type that misses its margin is excluded") lets some types pass by chance.
  - **Evidence (v1 §6.3):** family M is "image × t + A × (1 − t)". The control is "evidence 03's model", the same
    formula, uniform. **Inference:** with whole-tile placement and a fixed t, M is the control with a different A.
  - **Inference (maths):** a local before–after correlation does not change when one image is scaled and shifted by
    constants. So inside a cloud, "pattern kept" is the same for M and the control. It changes only at edges, at
    clipping, through rounding and through noise.
- **EVIDENCE NEEDED.** None new. A rule.
- **RECOMMENDED ACTION.**
  - Name **one primary realism test**: for family X, a direct paired contrast of distance to real cloud against the
    control's distance, on a pooled statistic, with a pre-set rule.
  - Treat the per-statistic and per-type margins as secondary, Holm-adjusted.
  - Fix the number of rise bins now.
  - Say which placement each check uses. Use shaped placement for the realism checks, so that M and the control
    differ.
  - Keep the control rule only in this form: "the control must be farther from real cloud than X, by the pre-set rule".

#### M14. Realism is tested on image statistics, not on the use

- **ISSUE.** Q1's role is to let the bed speak for real cloud in flood calls. The checks test image statistics and
  mask scores. The only use-level check is the 24 trusted flooded roads, which cannot detect less than about 25–40
  points.
- **LOCATION / TARGET.** §6.3 steps 3–5; §11 row "Synthetic cloud is not like real cloud".
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (04, Winiwarter et al. 2021):** realism is judged per use, "specific to the given research question".
  - **Evidence (05):** SEN12MS-CR found training on real clouds beat training on synthetic ones (Ebel et al.,
    abstract). Synthetic cloud can match on looks and differ in use.
  - **Inference:** the forest reads many cues (GLCM, Gabor, LBP, Laws, wavelet, semivariogram, DINOv2). Matching three
    low-level statistics does not show that these cues shift the same way.
- **EVIDENCE NEEDED.** None new. The cues and calls exist.
- **RECOMMENDED ACTION.** Add a label-free, use-level check: at matched rise, compare the distribution of the
  forest's top cues, and of its flood probability, on real thin-cloud strips against synthetic ones. Match on before-image
  cues to control for ground. Fix the cue list from production's feature importances before scoring.

#### M15. Check 1's real reference is chosen by the mask, in one image

- **ISSUE.** Check 1's "real thin cloud" is whatever the dark-rise mask flags. The real thin level is the median rise
  of flagged ground. Both inherit the mask's selection.
- **LOCATION / TARGET.** §6.3 steps 2 and 3; §8 row Q1 check 1.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Inference:** the flagged set holds only cloud thick enough to cross the threshold. Its median rise is therefore
    biased thick. Real thin cloud the mask misses is never in the reference.
  - **Inference:** the flagged set may include non-cloud brightening (M9). Then "real cloud" statistics are partly
    statistics of changed ground.
  - **Inference:** the margin ("half the real cloud's own effect") compares cloudy windows with clear windows in
    other places. Cloud and flood cluster by area, so that effect is confounded with ground.
  - **Evidence (my check):** one acquisition (M1).
- **EVIDENCE NEEDED.** The distribution of rise around the threshold on thin-cloud tiles; the number of cloud patches.
- **RECOMMENDED ACTION.**
  - Say the real thin level is "the median of mask-detected thin cloud".
  - Add a sensitivity reference: thin cloud within a fixed distance of an opaque core.
  - Measure the "real effect" for the margin on the same tile (cloudy against clear windows within a tile), not across
    tiles.

#### M16. Check 2 confounds realism with cloud size and thickness

- **ISSUE.** Check 2 pairs real and pasted clouds in the same HRC_WHU image and compares mask F1. F1 depends on cloud
  area and thickness. The pasted cloud's thickness comes from Louisiana opaque cores. Its shape comes from another
  image. Neither is matched to the real cloud it is compared with.
- **LOCATION / TARGET.** §6.3 step 4; §8 row Q1 check 2; §9 row "Q1 check 2".
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Inference:** a large opaque pasted cloud is easy for any mask. A small, thin real one is hard. The F1 gap would
    then measure the size and thickness mismatch, not realism.
  - **Inference:** matching thickness to the image's real cloud would break v1's own rule ("no realism statistic is
    ever used to set the generator"). The rule and a fair comparison pull against each other.
  - **Evidence (my check):** 24 development images per type. **Inference:** after dropping images of unknown or coarse
    resolution, and images without room to paste, fewer remain. The effective count is unknown.
  - **Evidence (01):** HRC_WHU spans 0.5–15 m. **Inference:** if the HRC_WHU run uses the same 41-pixel dark window, it
    covers 20 m at 0.5 m but about 600 m at 15 m. Pooling resolutions inside a type then mixes scales.
  - **Evidence (v1 §8):** the 0.10 margin is "smaller than the gap between ground types". **Evidence (01):** vegetation
    0.78 against water 0.74 is a gap of 0.04; urban 0.66 against water 0.74 is 0.08. So the claim is true only for some
    pairs.
  - **Inference:** snow and barren ground are not part of the Louisiana use.
- **EVIDENCE NEEDED.** Per type: the number of usable images, their resolutions, and the per-image F1 spread (already
  in `cloudref_test.ipynb`).
- **RECOMMENDED ACTION.**
  - Compare recall at matched cloud area and in fixed bands from the cloud edge, not F1 over the whole image.
  - Paste at a thickness grid fixed in advance and compare at each level.
  - Name urban, vegetation and water as the types that matter for the claim. Report snow and barren as descriptive.
  - Report by resolution band, or keep images within a fixed factor of 0.5 m.
  - Correct the 0.10 justification.

#### M17. The generator has no fallback if HRC_WHU resolutions cannot be found

- **ISSUE.** Shapes must be rescaled by each image's resolution. The files do not store it. If Li et al. (2019) give
  only a range, the generator is blocked in week 2.
- **LOCATION / TARGET.** §6.3 step 1; §5 (shape pool "blocked"); §19 "Facts still unknown".
- **SEVERITY.** Major (feasibility).
- **WHY IT MATTERS.** **Evidence (v1 §0):** `barren_1.tif` has no geographic tags. **Inference:** v1's rule "images
  whose resolution cannot be established are left out" could leave no shapes at all.
- **EVIDENCE NEEDED.** What Li et al. (2019) or the dataset page actually state about per-image resolution.
- **RECOMMENDED ACTION.** Pre-set a fallback shape source now. Options: bright-mask outlines from the 17 opaque tiles
  (native 0.5 m, same sensor; note the circularity for the bright mask), or procedural shapes with a size spectrum
  taken from those outlines. Decide in week 1 which one applies.

### E. The reference de-hazing option (§6.4)

#### M18. The prototype and the plan disagree, and the prototype has already looked at the scoring data

- **ISSUE.** The plan will freeze settings and guards the prototype does not use. The prototype is being shaped on the
  same development roads the formal checks will use, including the clear flooded roads behind the safety veto.
- **LOCATION / TARGET.** §6.4 (model, guards, settings, "the prototype now running"); §8 rows "Option §6.4"; §15
  "Where the reference de-hazing option fits".
- **SEVERITY.** Major. **Blocking if §6.4 is adopted as a tested arm.**
- **WHY IT MATTERS.**
  - **Evidence (my check):** window 64 m, not 100 m; floor 0.2, not 0.3; no leave-the-object-out guard; symmetric
    trimming; a different source for g and h; a sign rule the plan does not mention (section 2 table).
  - **Evidence (v1 §6.4):** the prototype "already looks at these 24 roads and at clear flooded roads".
  - **Inference:** the safety veto runs on "the tiles of the 769 clear roads". If the prototype's settings were chosen
    while looking at those flooded roads, the veto on development data is not an independent test.
  - **Inference:** on whole-tile cloud, the prototype's g and h either absorb the haze or fall back to (1, 0) (section
    2). Its primary cell is exactly where it is weakest.
- **EVIDENCE NEEDED.** The prototype's change history: which settings were tried, on which tiles, and what was seen.
- **RECOMMENDED ACTION.**
  - Keep one source of truth: freeze one method in code, with its hash, and list every earlier setting tried.
  - Implement §6.4's rule for g and h under whole-tile cloud (clear training tiles of the same before–after pair) or
    drop the whole-tile cell for this method.
  - Run the safety veto again in the sealed look, on the sealed clear tiles. Treat the development veto as a screen,
    not as proof.

#### M19. Family X favours the reference fit over its comparator, and the comparator is already "unsafe"

- **ISSUE.** Family X adds air light that varies smoothly across the tile. The reference fit models exactly that (smooth
  α and β fields). He de-hazing assumes one air light per tile. So on family X the primary contrast (reference minus He)
  is tilted towards the reference by construction. And He de-hazing already fails the plan's own safety bar.
- **LOCATION / TARGET.** §6.4 "Circularity" and "Outcomes and tests" (primary); §8 rows "Option §6.4, primary" and
  "safety".
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (my check):** `sn8_clouds.dehaze` uses one air light per tile.
  - **Evidence (01; `sn8_clouds.dehazed_table`):** He de-hazing, applied to every after image, cost 1.7 points of
    accuracy on the 766 shared roads (p 0.15). Its flooded-found share fell from 85.8% to 83.9%. The §6.4 safety veto
    allows at most 1.5 points (upper bound). So on these point estimates the comparator would fail the veto.
  - **Inference:** "beats He" is then a weak bar. The real decision for a thin-cloud road is "correct and call" against
    "cannot assess", the adopted rule.
  - **Inference:** "not inverted exactly by any tool" (v1 §6.3) is not the same as "neutral between tools".
- **EVIDENCE NEEDED.** The scale of air-light variation in real cloud (from the opaque cores or HRC_WHU cloud pixels),
  set before the bed is scored.
- **RECOMMENDED ACTION.**
  - Make the primary outcome: do corrected thin-cloud roads meet Q2's S2/S3 ceilings (or the non-inferiority δ)?
    That is the question a map faces.
  - Keep He as a secondary comparator.
  - Set X's air-light variation scale from real cloud, before scoring, and report the reference fit's gain against
    that scale.
  - Add a third generator variant with blur and with air light that varies faster than the fit window, so the result
    does not rest on one family that matches one method.

#### M20. The guards do not cover the before-cloudy direction, bright floodwater or large floods

- **ISSUE.** Guard 2's reasoning ("haze lifts dark pixels and floodwater mostly darkens them, so large negative
  residuals are dropped first") holds only for the after-cloudy direction. "Change kept" is only a diagnostic. The
  safety veto may be too tight to pass, or too easy, depending on unstated choices.
- **LOCATION / TARGET.** §6.4 "The catch", "Two directions", "Outcomes and tests"; §8 row "Option §6.4, safety".
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Inference (before-cloudy direction):** the reference is the flooded after image. Dry ground in the cloudy before
    image sits above what the dark water predicts. So changed pixels have **positive** residuals, the same sign as haze.
    Guard 2 then cannot tell flood from cloud.
  - **Evidence (critic C4-3):** turbid or glinting floodwater can be bright. **Inference:** bright floodwater gives
    positive residuals in the after-cloudy direction too.
  - **Evidence (05):** stable-surface methods degrade under very fast landscape change (Hagolle et al. 2015). IR-MAD
    re-weighting by no-change probability was built for scenes with much change (Canty & Nielsen 2008).
  - **Evidence (prototype docstring):** "a flood bigger than the window that also brightens would be read as haze and
    removed".
  - **Inference (veto):** on clear tiles a good fit gives t̂ ≈ 1, so the veto may pass trivially. Where it does change
    calls, a 1.5-point upper bound on recall over 433 flooded roads may fire on noise. Either way it is not shown to
    measure flood loss under cloud, where the risk is.
- **EVIDENCE NEEDED.** On the bed: change kept on flooded strips by tile flood class. At Gate 0: the veto's expected
  upper bound under no effect, from the He arm's logged calls.
- **RECOMMENDED ACTION.**
  - Make "change kept" a second veto on the bed: its lower bound on mostly flooded tiles must stay above a pre-set
    value (for example 0.8).
  - Use an invariant-pixel weighting (IR-MAD or PIF style; 05) in place of the sign heuristic. Read Lin et al. (2015)
    before freezing (05 §7 puts it first).
  - Treat the before-cloudy direction as exploratory unless a guard that works there is shown on the bed.
  - Check at Gate 0 that the veto can be passed by a method that changes nothing harmful, and failed by one that does.
  - Replace "not searched" in §6.4's prior work with 05's anchors. Claim no novelty for the method family.

### F. Feasibility

#### M21. Weeks 1 and 2 are overloaded, and Justin's rulings sit on the critical path

- **ISSUE.** Week 1 holds four or more rulings, all counts and power, Tilt set-up, a frozen pre-registration by
  mid-week, and Q2's real-data results. Week 2 holds the generator (two families, control, two placements, both
  dates), the shape pool, the after-only model, the building table, the methods draft, and (if adopted) moving the
  §6.4 prototype into the repo with tests and running its safety check.
- **LOCATION / TARGET.** §15 weeks 1–2; §19; §20.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (decision log):** Justin asked to be asked "one question at a time". v1 lists 9 decisions.
  - **Evidence (v1 §0):** no roads side-test Tilt resources exist yet. The project rule runs every script through Tilt.
  - **Inference:** if a ruling arrives late, the pre-registration slips, and every gate behind it slips.
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.**
  - Ask the four blocking rulings first, in order: synthetic truth, HRC_WHU use, the ceilings, §6.4's place. Default
    the rest and record the defaults.
  - Freeze the pre-registration at the end of week 1, not mid-week.
  - Decide buildings on the week-1 counts (they need no cloud outcome), not at week 3.
  - Move the library search and Justin's reference check to weeks 1–3. Finding prior work in week 7 leaves no time to
    reframe.

#### M22. The cut order removes the spatial core early and keeps the costliest extra late

- **ISSUE.** The shaped-cloud placement is second to be cut. Buildings, the largest new build, are fourth. §6.4's
  after-image direction and Justin's two-pass idea are not in the cut list.
- **LOCATION / TARGET.** §15 cut list.
- **SEVERITY.** Major.
- **WHY IT MATTERS.**
  - **Evidence (v1 §6.1 step 4):** S1's false-hidden rate "includes roads just outside a placed cloud, so it measures
    the 20 m window's edge effect". Whole-tile cloud has no "outside".
  - **Evidence (critic C2-4):** the spatial question is strip cover and distance from the cloud's edge. Per-tile haze is
    a radiometric test.
  - **Inference:** cutting shaped placement removes S1's two-date false-hidden rate, the edge effect, the difference
    between M and the control (M13), and much of the "meaningful spatial component" the input card requires.
  - **Evidence (v1 §5):** the building table is "new, 1–2 weeks".
- **EVIDENCE NEEDED.** None.
- **RECOMMENDED ACTION.** New cut order, for Justin to approve:
  1. H3c routing.
  2. Buildings (decided in week 1 on counts).
  3. §6.4's before-image direction.
  4. Justin's finer-scale re-detection (M23), if adopted.
  5. Q3's thin levels (keep opaque).
  6. The optional risk–coverage figure.
  7. §6.4's after-image direction.

  Keep shaped placement on the never-cut list, or at least on one family (X).

#### M23. Justin's second idea is not placed

- **ISSUE.** The decision log adds a second idea: when the detected change is cloud, rescale the image and run the
  change detector again for smaller changes, and look into filling in blocked areas. v1 does not mention it.
- **LOCATION / TARGET.** v1 §0 and §19; `decision_log.md` last row; evidence 05.
- **SEVERITY.** Major (completeness; it changes scope).
- **WHY IT MATTERS.**
  - **Evidence (05 §6):** filling from the before date "paints the dry road back", so a flooded road becomes "no
    change". Generative fills invent texture. Neither is recommended for scoring.
  - **Evidence (05 §6):** "scale" can mean re-scaling brightness inside the cloud (§6.4 already) or looking again at
    finer crops. The second has only indirect support.
  - **Evidence (05 §6):** a provenance layer (observed, corrected, filled, not observed) is suggested, with only
    observed and corrected pixels allowed to vote "flooded".
  - **Inference:** the time is used up by the current plan. A new arm would need a cut.
- **EVIDENCE NEEDED.** Justin's ruling.
- **RECOMMENDED ACTION.**
  - Put it to Justin as one decision.
  - Add a fixed rule now: no filled pixel is ever scored or shown as observed.
  - The provenance layer is cheap and fits Q2's map. Consider it there.
  - Treat finer-scale re-detection as out of scope for this paper, or as an exploratory figure on the bed only.

### G. Rules and claims

#### M24. Synthetic truth is a label question the plan depends on

- **ISSUE.** S1's two-date half, "truly hidden", and Q1's check 2 score masks against where synthetic cloud was placed.
  The project's label rule allows published human labels only.
- **LOCATION / TARGET.** §1 (synthetic truth); §19 decision 1.
- **SEVERITY.** Major. v1 already lists it as blocking the pre-registration; I agree.
- **WHY IT MATTERS.** **Evidence (input card):** "published human labels only, used unmodified, for training and
  scoring. No own, pseudo or VLM labels." **Inference:** a placed-cloud mask is an own label in all but name. The flood
  scores on the bed are not affected: they use published labels.
- **EVIDENCE NEEDED.** Justin's ruling.
- **RECOMMENDED ACTION.** Ask it first. Pre-register both branches: with synthetic truth, and without (then S1 has
  only its real half, and Q1 has check 1 plus the use-level check of M14).

#### M25. Several claims are wider than the tests

- **ISSUE.** Words in the questions and the abstract promise more than the plan can show.
- **LOCATION / TARGET.** `selected_questions.md`; abstract sentences 5, 8, 20, 21; v1 §6.4 sub-question wording.
- **SEVERITY.** Major.
- **WHY IT MATTERS AND RECOMMENDED ACTION.**

| Claim word | What the test supports | Suggested wording |
|---|---|---|
| "Reliably" (Q2) | Error no worse than the clear-sky map plus a margin, on one scene; S1's real half on HRC_WHU | "as reliable as the clear-sky map, within a preset margin" |
| "Represent real-life blockages in satellite imagery" (Q1) | Named statistics, matched to cloud in one Maxar acquisition and in the HRC_WHU types that pass | "match real cloud in 0.5 m greyscale imagery on preset checks" |
| "Finds change" (Q3) | Reads the after state; tested against a model fed a blank before image | "maps flooded roads from the after image alone" |
| "Without erasing the flood" (§6.4) | Synthetic family X and a clear-tile screen; real-cloud numbers exploratory | "on synthetic cloud" |
| "One event, one sensor" (abstract, v1 §10.5) | One after acquisition, two before acquisitions | "one after-image acquisition of one event" |
| "A tested rule for reporting hidden roads" (abstract) | Tested on development data and a same-scene held-out set | "a rule tested on held-out tiles of the same scene" |
| "Detect" for Q1 (the arc) | Q1 tests synthetic cloud, not detection. Detection is tested in S1 and check 2 | Keep Justin's arc, but say that "detect" is tested in S1 and check 2, and that Q1 builds and checks the test bed |

- **EVIDENCE NEEDED.** None.

#### M26. Licences and data release

- **ISSUE.** Bed images mix SpaceNet 8 tiles with HRC_WHU cloud texture (academic use only; Google Earth imagery).
  Figure permission for HRC_WHU crops is open (v1 §3.4). Gemma captions on figures would be AI-written content.
- **LOCATION / TARGET.** §3.4; §13; §14.
- **SEVERITY.** Minor.
- **WHY IT MATTERS.** **Inference:** a derived image takes the more restrictive terms of its sources. A data release of
  bed images could break HRC_WHU's terms.
- **EVIDENCE NEEDED.** HRC_WHU and Google Earth terms for figures; the target journal's policy on AI-written figure
  text.
- **RECOMMENDED ACTION.** Release code and seeds, not bed images. Keep Gemma out of figures unless the journal allows
  it, and name it in the AI-use statement if used.

#### M27. Smaller consistency fixes

- **ISSUE, LOCATION AND ACTION, one line each.** Severity: minor.
  - "Truly hidden" (§6.1 step 4; §8): name the metric (balanced accuracy?) and say whether "rises more than 1.5
    points" is a point estimate or a bound.
  - The four-level grid is coarse for "the thinnest level where error rises". State that it can only land on four
    values.
  - Greyscale: use the same RGB-to-grey weights for HRC_WHU as for SpaceNet 8. State them.
  - Compute (§15): the classical and texture cues on clouded tiles run on CPU and are not costed. Cost them.
  - One seed per cell: generator randomness is not in the intervals. Add a second seed on the primary cell, or say so.
  - §3.2: re-learning Otsu thresholds inside folds in the blocked run is good. Do it in the shuffled primary too, or
    state the size of the leak.
  - The 1,080 label rows against 1,037 roads (critic §3) is still unexplained. Resolve it before H2a, which counts
    roads.
  - DINOv2's role (cues inside the forest) and Gemma's (captions only) comply with the role rule. No change needed.
- **WHY IT MATTERS.** Each is small, but the pre-registration freezes them.
- **EVIDENCE NEEDED.** None.

---

## 7. The ceilings and margins (§8): justified, or set to pass?

No ceiling is set from scored outcomes, and several fail safe. But some rest on evidence for a different quantity, some
are close to certain to pass or to fail, and one compares against a method that already fails the plan's own bar.

| Rule | Value | Justified from the evidence? | Pass or fail built in? | Fix |
|---|---|---|---|---|
| Tier interval | 98.3% one-sided | The multiplicity logic is sound. It counts 3 statements; there are at least 4 ceilings. The questions say "95%" | No | Count all ceilings; one wording (M8) |
| S1 missed hidden | ≤ 30% | Anchored on the dark mask, which the map does not use (M5) | Bright mask (used): very likely **fail** (recall 0.28). Dark mask: at the line, so the 10 m / 20% window choice decides it | Test the frozen rule (M5) |
| S1 false hidden | ≤ 10% | Anchored on the overall flag share (10.4%), not on a false-hidden rate. A coverage-cost argument, not stated as one | Likely fail on barren and snow (01) | Say per type or pooled; state the cost argument |
| S2 | ≤ 25% | Cites ±4–7 points from flag-rate gaps at 95%, not the error share at 98.3% (M6) | Depends on the scored set: can fail from size alone on the flagged set; can "just pass" on all roads | Pre-set the set; non-inferiority; recall and specificity beside (M6) |
| S3 | ≤ 25% | As S2 | Base-rate shift pushes it towards fail where the mask favours flooded roads (03, t ≤ 0.7) | As S2 |
| S4, S5 | Range only | Yes (critic X3) | Fixed by design | Report width as the result (M8) |
| "Truly hidden" | Error rise > 1.5 points | Reasonable; metric and statistic unstated | No | M27 |
| Q2a | ±1.5 points | Noise-based. Close to the size of rule differences in 01 (0.7–1.7 points), which is a better reason | Likely inconclusive (v1 says so) | Compute its own width at Gate 0; reword (M8) |
| Q2b | ≥ 10 informative tiles | Reasonable | No | Identification first (M9) |
| Q3 go/no-go | Clean BA lower bound ≥ 0.60 | Fine as a gate | Near-certain **pass** (inference) | Add a usefulness bar (M11) |
| H3a | Lower bound > 0 at opaque | Yes | Four looks via the "no" rule (M10) | Opaque only (M10) |
| H3b | MDD ≤ 15 points | Yes | No | Keep |
| H3c | Cost ≤ 1.5; ≥ half oracle | Yes | No | Keep; cut first |
| Q1 check 1 | ± half the real effect | Principled. The "real effect" is measured across places, so it is confounded (M15) | Hard to pass on "pattern kept" if real thin cloud keeps the pattern | Measure the effect within tile; fix the bins (M13, M15) |
| Q1 check 2 | ±0.10 F1 | Plausible. "Smaller than the gap between ground types" is false for some pairs | Confounded by size and thickness (M16) | Matched-area recall; thickness grid (M16) |
| Q1 control | Must miss ≥ 1 margin | Pattern from Burgert et al. (04) | Near-certain to be met, so it does not discriminate (M13) | Direct X-versus-control contrast (M13) |
| Circularity flag (M) | F1 on M > real + 0.10 | Yes | No | Keep |
| H1b | Lower bound > 0 | Yes | No | Keep |
| Buildings | ≥ 150 flooded on ≥ 50 tiles; BA ≥ 0.60 | Reasonable | No | Decide in week 1 (M21) |
| Block side | Semivariogram range, ≥ 3 tiles | Rule is good; no cap | Could leave too few blocks | Cap at 7 tiles (M3) |
| §6.4 safety | Loss upper bound ≤ 1.5 | Strict. He de-hazing would fail it on its point estimates (−1.7 accuracy, −1.9 flooded found; 01). Development check already seen by the prototype | May be trivial on clear tiles, or fire on noise | Gate 0 reachability; sealed re-run; add "change kept" veto (M18, M20) |
| §6.4 primary | Lower bound (reference − He) > 0 | Tilted by family X's smooth air light (M19) | Built-in advantage for the reference fit | Primary = corrected roads meet Q2's ceilings (M19) |
| §6.4 recovery | ≥ half of cloud's loss | Same bar as H3c | No | Keep, secondary |
| §6.4 settings | 100 m; t̂ 0.3 | No evidence (v1 says so). The prototype uses 64 m and 0.2 | — | Freeze one; log the history (M18) |

---

## 8. Power and the named sample sizes

| Sample | What it can support | What v1 does | My view |
|---|---|---|---|
| **24 trusted flooded roads under thin cloud** (39 tiles, one acquisition) | Only effects of about 25 points (03), nearer 40 for 80% power (v1 §9). Clustered in one cloud field | Reported, not tested, in Q2, Q1 and §6.4 | Right. Add: §6.4's prototype has already looked at them, so for §6.4 they carry no weight at all. Say in the paper that these 24 roads carry no inferential weight anywhere |
| **3 flooded labels on 17 opaque tiles** (5 informative tiles) | A check that the dataset behaves as documented | Described only | Right. The 17 tiles also set the generator's air light; say they come from one image |
| **24 HRC_WHU images per type** (6 sealed) | Per-type equivalence at ±0.10 only if the per-image spread is small and few images drop out | Power computed at Gate 0 | Good. Add the effective count after resolution filtering (M16), and pool across types for the sealed look (M2) |
| Flagged subset on the bed at the real thin level | Possibly only 35–120 roads (03, uniform haze) | Not distinguished from all clouded roads | Pre-set the scored set (M6) |
| 769 clear roads on 190 tiles (the bed) | Most of the plan's power | Primary everywhere | Good, but tile-bootstrap intervals are too narrow if tiles correlate (M3) |
| 40 sealed tiles | About 2.2 times wider intervals; few cloudy tiles | Re-scores all three questions | Needs a decision rule and a minimum (M2) |

**Gate 0** is the right tool. It needs three additions:
- the equivalence version of power for Q1's margins and the §6.4 veto;
- the sizes of the scored sets for S2 and S3;
- the sealed look's expected widths.

---

## 9. Feasibility: the plan, the cut order and the compute

- **Eight weeks.** The arc is sound, but weeks 1–2 are overloaded (M21) and the writing has about 1.5 weeks after the
  sealed look. **Inference:** a journal paper with three questions and an option is at the edge of eight weeks. Draft
  results progressively from week 4, as each part freezes.
- **The cut order** should protect shaped placement and drop buildings earlier (M22).
- **Compute.** **Inference from v1's figures:** about 12 h (Q1 bed) + 3 h (Q3) + 7 h (§6.4) + 3 h (sealed) + 1 h
  (buildings) ≈ 26 h of DINOv2 time, run in the background. That is feasible. Two things are missing: CPU time for the
  classical and texture cues on every clouded tile, and Tilt set-up time.
- **Do the stated risks match the design?** v1's threat table (§11) is good. It misses these:
  - one after acquisition (M1);
  - the interleaved, underpowered sealed look (M2);
  - absolute tiers and dependence (M3);
  - clear-sky omission under trees (M4);
  - S1's construct (M5);
  - the scored set and base rate in S2 and S3 (M6);
  - realism not binding (M7);
  - the H3a loophole (M10);
  - Q1's pass rule (M13);
  - the prototype mismatch and its look (M18);
  - family X's tilt (M19);
  - the before-cloudy guard (M20);
  - Justin's second idea (M23).

  Two listed mitigations are partial:
  - "Check 2 uses expert masks" cannot check the dark-rise selection on SpaceNet 8. It is another dataset and a single
    date.
  - The blocked-fold run comes in week 6, too late to change anything.

---

## 10. What v1 fixed from the earlier critique

| Earlier point | v1's answer | Status |
|---|---|---|
| X1 mask bias by flood state | Evidence 03; re-check on family X | Answered for haze; false alarms without haze still open (M9) |
| X2 tiles, not roads | Tile intervals primary | Answered; dependence between tiles open (M3) |
| X3 no truth under cloud | Ranges, tiers, tipping points | Answered |
| X4 neighbour leakage | Three-scheme sensitivity | Partly; the tiers use absolute rates (M3) |
| X5 untrusted agreement | Not used as accuracy | Answered |
| X6 novelty | None claimed | Answered |
| X7 no second dataset | Scoped claims | Answered; scope should say one acquisition (M1) |
| C2-1 realism check cannot discriminate | Image-statistics checks | Partly (M13, M14) |
| C2-2 circular de-hazing | Family X | Partly; X now tilts §6.4 (M19) |
| C2-4 spatial component | Shaped placement, edge distance | At risk from the cut list (M22) |
| C2-5 HRC_WHU scale | Rescaling | Blocked without a fallback (M17) |
| C3-2 fixed classifier | Fit once, keep every call | Answered |
| C4-1 no real two-date labels | Stated as a limit of §6.4 | Answered as a limit |

---

## 11. Verdict

**REVISE.**

The methodology is well built and honest about its limits. Its pre-registration, tile intervals, fail-safe margins,
tiers and sealed look are the right tools. But as written it cannot yet support three of its central inferences:
- The lead question's only "reliable" statement (S1) is tested on masks the map does not use, on non-Maxar imagery.
  The mask the map does use would very likely fail.
- Q1's pass rule cannot tell good synthetic cloud from bad, and its verdict does not bind the Q2 tiers that rest on it.
- The design treats tiles as independent and calls the sealed look a check. Yet all real cloud comes from one after
  image, and 39 of 40 sealed tiles touch development tiles.

The §6.4 option is not ready for a formal test. The prototype and the plan differ on window, floor, guards and the
source of gain and offset. The development data behind its safety veto has already been looked at. Family X favours it
over He de-hazing by construction. Most of these are definitional fixes that can go into the week-1 pre-registration
without new data. None needs sealed data. Fix them, and re-check the plan's feasibility, before freezing.

## 12. The changes that matter most, ranked

1. **Redefine S1 as the frozen map rule** (tile rule + road rule). Test exactly that. Pre-set what Q2 says if it fails.
   Say the real half is on HRC_WHU imagery (M5).
2. **Give Q1 one primary realism test.** A direct contrast of X against the control, on shaped placement, with
   per-statistic and per-type margins as Holm-adjusted secondaries. Add a label-free use-level check (cue and
   probability distributions). Make a realism failure drop S2 and S3 to "range only" (M13, M14, M7).
3. **Fix the sampling frame.** State one after acquisition. Use spatial-block intervals and blocked folds for the
   tiers and primary results, in the same week as each result. Pre-register a decision rule and a minimum for the
   sealed look (M1, M2, M3).
4. **Pin down S2 and S3.** One scored set. Recall and specificity beside the error shares. A non-inferiority margin
   against clear sky, recomputed at Gate 0 from the right statistic. "Not shown" kept apart from "fails" (M6).
5. **If §6.4 is adopted:** freeze one method in code and log the prototype's history. Implement the whole-tile gain
   and offset rule. Make the primary outcome "corrected roads meet Q2's ceilings". Add a "change kept" veto. Re-run the
   safety veto in the sealed look. Read Lin et al. (2015) and use invariant-pixel weighting (M18–M20).
6. **Close the H3a loophole** (decide at opaque cover only). Add the clean information-cost gap and a usefulness bar
   for the after-only call (M10, M11).
7. **Re-order the cut list.** Protect shaped placement. Decide buildings in week 1. Place Justin's two-pass idea, with
   a rule that filled pixels are never scored (M22, M23).
8. **Test "missing = dry" where it is weakest.** Stratify clear roads by the existing tree and shadow visibility gate.
   Anchor the tipping counts to diagnostic rates (M4).

---

## 13. Unresolved issues

- **Justin's rulings that block the pre-registration:** synthetic truth (M24), HRC_WHU use, the ceilings (now with
  the fixes above), §6.4's place, and his two-pass idea (M23).
- **Facts not in the files:**
  - HRC_WHU per-image resolution (M17);
  - the number of real cloud patches (M1);
  - the dark-rise distribution near the threshold on clear flooded and dry roads (M9);
  - the prototype's settings history (M18);
  - the 1,080 label rows against 1,037 roads (M27).
- **Literature:** Lin et al. 2015, Hagolle et al. 2008 and Canty & Nielsen 2008 are read at TLDR, metadata or abstract
  level only (05). Justin has verified none of the references.
- **My limits:**
  - I read the prototype's code, not its results.
  - I counted acquisitions for development tiles only. I did not check the sealed tiles' source images.
  - My power figures are rough arithmetic, labelled as inference.

## 14. Suggested next scientific action

1. **Justin rules on the blocking decisions,** one at a time: synthetic truth, then HRC_WHU use, then §6.4's place
   (with M18–M20), then the ceilings as revised here.
2. **Three label-free checks in week 1, through Tilt, development data only:**
   - the cloud patch count and acquisition table (M1);
   - the dark-rise distribution near the threshold on clear flooded and dry roads (M9);
   - the visible share on clear flooded and dry roads (M4).
3. **The methodology agent writes v2.** It should take in M5, M6, M7, M10, M13 and the sealed decision rule (M2), and
   compute Gate 0 with the additions in section 8.
4. **Then freeze the pre-registration,** with hashes, at the end of week 1.
5. **Next workflow stage:** the validation agent checks v2's numbers against the evidence files, and this review's
   checks against the files named in section 0 (AGENTS.md rule 8).
