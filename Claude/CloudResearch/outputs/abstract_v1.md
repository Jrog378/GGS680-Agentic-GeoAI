# Abstract and expected contribution, first draft (Q2 leads, then Q3 and Q1)

Stage 3, the Scientific Writer, in the Assignment 3 workflow. Claude wrote this on 2026-10-23, working alone from
local files. It is a **proposed study**. It reports no findings. The one measured statement in the abstract
(sentence 3) is marked "preliminary". It is our own development-data measurement from the evidence files, not a
result of this paper.

- **Question order and wording:** `outputs/selected_questions.md` (Q2 leads, then Q3, then Q1).
- **The arc:** Justin's problem statement (`input_card.md`): detect (Q1), handle (Q3), report (Q2).
- **References:** Justin has verified none of them. Each is marked "(unverified)".

---

## Working title

What can a flood map say about roads it cannot see? Detecting, handling and reporting cloud after a disaster

## Abstract

Clouds can hide the ground in satellite images taken after disasters. Labels and maps made from them can be wrong
there. In preliminary checks on development data, SpaceNet 8 road labels say "flooded" or nothing, so hidden roads
read as dry. The sources we read show no remote-sensing study of how error changes as a map skips cloudy ground.

We ask: what can a flood-road map reliably tell users about roads hidden by cloud? It is the last of three steps:
detect, handle, report.

We use SpaceNet 8 image pairs (Hurricane Ida, 2021; 0.5 m, greyscale), published labels and one frozen flood model.
Detect: we build a test bed of synthetic clouds from real cloud outlines (HRC_WHU). Do they match real cloud better
than plain haze? Handle: if only the before image is cloudy, does the after image alone find change better than both
images? Report: we score each thing a map could say about a hidden road, such as "flooded" or "dry".

A statement is reliable only if the top of its error's 95% interval stays below a preset limit. Intervals resample
whole tiles. If only synthetic cloud can test a statement, it is "synthetic only". Untestable ones are given as
ranges. We also test whether counting hidden roads as dry inflates the usual accuracy figure. Rules are fixed before
scoring. The frozen setup gets one check on sealed data. If only "this road is hidden" passes, a map can say only
where it cannot see.

Either way, the study would give a tested rule for reporting hidden roads. It would also show how well synthetic
clouds stand in for real ones, and when the after image alone is enough. Claims cover one event, one sensor and roads.
Other cases are general in design only.

*296 words; 23 sentences, the longest 21 words (target 200–300 words).*

**The five parts, by paragraph:**
1. Background and problem.
2. Gap and question. The gap sentence closes paragraph 1 because it leads straight into the question.
3. Proposed data and methods.
4. Validation strategy.
5. Expected contribution.

---

## Contribution

What the paper would add. Each bullet is traced to its source. No novelty is claimed beyond what the literature
summary supports.

- **A tested rule for reporting cloud-hidden roads (Q2, the lead).**
  - **What it adds.** Each thing a map can say about a hidden road is sorted by a limit fixed before scoring:
    "reliable", "synthetic only" or "range only". The statements are:
    - "this road is hidden";
    - "this hidden road is flooded";
    - "this hidden road is dry";
    - accuracy on hidden roads;
    - flooded road length.

    The map then shows which roads cannot be assessed, beside its flood calls.
  - **Source.** `selected_questions.md`, Q2. `research_questions_refined_v3.md` §5, Q2, method steps 2–5.
  - **Related work.** Keeping "can we see it?" apart from "is it flooded?" follows WorldFloods v2, which uses separate
    cloud and water masks (Portalés-Julià et al. 2023, unverified; evidence 02, §1 item 1).
  - **Novelty limit.** The sources read found no remote-sensing paper that reports risk–coverage curves for cloud
    abstention (evidence 02, §1 item 8). That is the only gap they support. The full reporting rule was not searched
    for (v3, Q2 "Novelty").

- **A check on the usual single accuracy figure (Q2's secondary questions, Q2a and Q2b).**
  - **What it adds.** A measure of how much counting hidden roads as "dry" raises the reported accuracy (Q2a). Also, a
    within-tile test of whether cloudy roads carry fewer flooded labels than clear roads (Q2b).
  - **Source.** `selected_questions.md`, Q2 secondary questions.
  - **Why it matters (preliminary evidence, development data).**
    - SpaceNet 8 road labels are "yes" or missing; "no" never occurs (evidence 01, "Labels under cloud").
    - Labelled flooded: 2% of roads on thick-cloud tiles, 26% under thin cloud, 55% on clear roads (same section).
      Geography plays a part too: in area 0 the clear neighbours are dry as well (same section).
    - Mask bias does not explain the low share under cloud, though that was tested with uniform synthetic haze only
      (evidence 03, §1).
  - **Limit.** Differences under about 1.5 points cannot be told from noise (evidence 03, §3). v3 expects Q2a near that
    limit, so it may come out inconclusive (v3, Q2 "Power").
  - **Needs citation:** whether other flood datasets label cloud-hidden objects the same way.

- **A synthetic-cloud test bed, checked against real cloud (Q1, the "detect" step).**
  - **What it adds.** Clouds built from real cloud outlines are compared with real cloud at 0.5 m in greyscale, per
    land-cover type. Plain (uniform) haze is a crude control the generator must beat. On clear tiles the published
    labels are taken as trusted both ways, so the bed can measure errors that real cloud cannot. That rests on
    "missing means dry" in clear sky, which is untested (v3 §10, item 7).
  - **Source.** `selected_questions.md`, Q1. v3 §5, Q2 "What changed" (the synthetic tier).
  - **Existing groundwork (preliminary evidence).** The bright and dark masks are already scored on HRC_WHU's expert
    labels, by land cover (evidence 01, "Cloud masks").
  - **Data.** HRC_WHU is the only human-labelled cloud set in the sources read that reaches 0.5 m (Li et al. 2019,
    unverified; evidence 02, §1 item 5 and §3).
  - **Related work.**
    - AnyTime-CD adds simulated thin to thick cloud in change detection (Qu, Li & Huang 2026, unverified). The notes
      record no check of that cloud against real cloud (evidence 04, §2 table, row 7).
    - DehazeFormer's README warns that models trained on synthetic haze may fail on real haze (Song et al. 2023,
      unverified; evidence 02, §1 item 4).
  - **Novelty limit.** The sources read hold no check of synthetic cloud against real cloud at about 0.5 m in
    greyscale, but nobody searched for one (v3, Q1 "Novelty"). None is claimed.

- **A measured test of an after-image-only call (Q3, the "handle" step).**
  - **What it adds.** When only the before image is cloudy, it tests whether the after image alone finds change better
    than both images together. It also tests a known limit: false "flooded" calls next to water that was there before.
  - **Source.** `selected_questions.md`, Q3.
  - **Why it is open (preliminary evidence).** Evidence 01 lists "what to do when only the before image is cloudy" as
    an open question. No Louisiana-East before image is cloudy, so the cloud must be synthetic (evidence 01, "Cloud
    masks").
  - **What is real.** The after-only model never reads the before image. So its score is a real-image measurement
    (`selected_questions.md`, Q3 "Outcome").
  - **Novelty limit.** Not searched for (v3, Q3 "Novelty"). **Needs citation** before any claim.

- **A stated scope.**
  - **What it adds.** The claims cover one event (Hurricane Ida), one sensor (Maxar, 0.5 m, greyscale) and roads.
    Other targets, sensors and hazards are general in design only.
  - **Source.** `selected_questions.md`, each question's "How far the claim reaches". `input_card.md`, "Scope".
  - **Rule.** Any wider claim needs Justin's approval (AGENTS.md rule 9).

---

## Claims audit

One row per abstract sentence, in order.

**Kinds:**
- background;
- proposed method (the question and validation sentences are listed here, with a note);
- expected contribution;
- preliminary evidence.

| # | Sentence | Kind | Source |
|---|---|---|---|
| 1 | Clouds can hide the ground in satellite images taken after disasters. | Background | `input_card.md`, "Broad research problem" (Justin's statement). **Needs citation** for the paper. A candidate for the flood case: Portalés-Julià et al. 2023 (unverified) names cloud as one limit of flood mapping (evidence 04, §2 table, row 1) |
| 2 | Labels and maps made from them can be wrong there. | Background | `input_card.md`, "Broad research problem" ("labels being inaccurate compared to ground truth"). For SpaceNet 8 roads: evidence 01, "Labels under cloud". **Needs citation** for the general claim |
| 3 | In preliminary checks on development data, SpaceNet 8 road labels say "flooded" or nothing, so hidden roads read as dry. | Preliminary evidence | Evidence 01, "Labels under cloud": `flooded` is "yes" (487) or left out (593), never "no". The labelling rule: Hänsch et al. 2022, p. 3 (unverified; quoted in evidence 01) |
| 4 | The sources we read show no remote-sensing study of how error changes as a map skips cloudy ground. | Background (literature gap) | Evidence 02, §1 item 8: "no remote-sensing paper that reports risk–coverage curves for cloud abstention". One IGARSS reject-option paper surfaced, read at metadata level only. Limited to the sources read; not a systematic search |
| 5 | We ask: what can a flood-road map reliably tell users about roads hidden by cloud? | Proposed method (the question) | `selected_questions.md`, Q2 (Justin's wording); `decision_log.md`, "Selection" |
| 6 | It is the last of three steps: detect, handle, report. | Proposed method (study design) | `input_card.md`, "Broad research problem" (detect, handle, report); v3 §7 (Q1 detect, Q3 handle, Q2 report) |
| 7 | We use SpaceNet 8 image pairs (Hurricane Ida, 2021; 0.5 m, greyscale), published labels and one frozen flood model. | Proposed method (data) | `selected_questions.md`, Q2 "Target and scope"; `input_card.md`, "Boundary conditions"; evidence 01, "Data and setting" |
| 8 | Detect: we build a test bed of synthetic clouds from real cloud outlines (HRC_WHU). | Proposed method | `selected_questions.md`, Q1 "Condition"; v3 §5, Q1 method step 1. Data: Li et al. 2019 (unverified; evidence 01, 02) |
| 9 | Do they match real cloud better than plain haze? | Proposed method | `selected_questions.md`, Q1 "Comparator" and "What counts as no" |
| 10 | Handle: if only the before image is cloudy, does the after image alone find change better than both images? | Proposed method | `selected_questions.md`, Q3 (checklist wording, shortened: "both images together" to "both images") |
| 11 | Report: we score each thing a map could say about a hidden road, such as "flooded" or "dry". | Proposed method | `selected_questions.md`, Q2 "Outcome and its truth" |
| 12 | A statement is reliable only if the top of its error's 95% interval stays below a preset limit. | Proposed method (validation) | `selected_questions.md`, Q2 "Reliable means" |
| 13 | Intervals resample whole tiles. | Proposed method (validation) | `selected_questions.md`, Q2 "Reliable means" (tile-resampled); v3 §3, "Tests" |
| 14 | If only synthetic cloud can test a statement, it is "synthetic only". | Proposed method (validation) | `selected_questions.md`, Q2 "Reliable means" |
| 15 | Untestable ones are given as ranges. | Proposed method (validation) | `selected_questions.md`, Q2 "Reliable means" |
| 16 | We also test whether counting hidden roads as dry inflates the usual accuracy figure. | Proposed method (validation) | `selected_questions.md`, Q2 "Comparator" and Q2a |
| 17 | Rules are fixed before scoring. | Proposed method (validation) | `selected_questions.md`, Q2 "Condition" and "Reliable means"; v3 §11, item 3 (the pre-registration) |
| 18 | The frozen setup gets one check on sealed data. | Proposed method (validation) | `input_card.md`, "Boundary conditions" (sealed data, one logged check); v3 §7, "One batched sealed look" |
| 19 | If only "this road is hidden" passes, a map can say only where it cannot see. | Proposed method (validation: what counts as "no") | `selected_questions.md`, Q2 "What counts as no" |
| 20 | Either way, the study would give a tested rule for reporting hidden roads. | Expected contribution | `selected_questions.md`, Q2 (each statement gets a tier whether it passes or fails); v3 §5, Q2 "Power" (the tiers and ranges do not depend on Q2a) |
| 21 | It would also show how well synthetic clouds stand in for real ones, and when the after image alone is enough. | Expected contribution | `selected_questions.md`, Q1 (realism, per land-cover type) and Q3 (the after-only test and its permanent-water limit) |
| 22 | Claims cover one event, one sensor and roads. | Expected contribution (scope) | `selected_questions.md`, each "How far the claim reaches" |
| 23 | Other cases are general in design only. | Expected contribution (scope) | `selected_questions.md`, Q2 "How far the claim reaches"; `input_card.md`, "Scope"; AGENTS.md rule 9 |

No abstract sentence states a result of this paper. Sentence 3 is the only measured statement. It is labelled
preliminary and comes from development data.

---

## References used (all unverified by Justin)

**From the input card's candidate list:**
- Portalés-Julià et al. 2023, *Scientific Reports* 13:20316, DOI 10.1038/s41598-023-47595-7 (JIF 4.9, per the input
  card). (unverified)
- Qu, Li & Huang 2026, AnyTime-CD, *Remote Sensing of Environment* 334:115239, DOI 10.1016/j.rse.2026.115239 (JIF 12.3,
  per the input card). (unverified)
- Song et al. 2023, DehazeFormer, *IEEE TIP* 32:1927–1941, DOI 10.1109/TIP.2023.3256763 (JIF 13.7; the input card says
  confirm in JCR). Used only for its README's warning. (unverified)

**Named in the evidence files (dataset attributions):**
- Hänsch et al. 2022, SpaceNet 8: the labelling rule (evidence 01). Venue and JIF are not in the evidence files.
  (unverified)
- Li et al. 2019, HRC_WHU, *ISPRS JPRS* 150:197–212 (JIF 12.9, per evidence 02). (unverified)

**Not cited:**
- The other input-card candidates: Zou et al. 2025; Guo et al. 2024; Hou et al. 2026.
- He, Sun & Tang 2011 (evidence 01). It sits behind the masks and generator family M, but no abstract sentence needs it.

---

## Inputs used

- Rules and role: `05_Project/AGENTS.md`; `05_Project/agents/writer.md`.
- The problem and decisions: `CloudResearch/input_card.md`; `CloudResearch/decision_log.md`.
- The questions: `outputs/selected_questions.md` (order and wording); `outputs/research_questions_refined_v3.md`
  (method detail).
- Evidence: `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, `03_pre_refinement_checks.md`,
  `04_research_question_guide.md`.
- No web search, no sub-agents, no sealed data.

## Assumptions

- **Q3's wording** is the checklist wording in `selected_questions.md` ("does the after image alone find change better
  than both images together?"). The input card still holds the older v3 wording ("can the after image alone still show
  what changed?"). The task named `selected_questions.md` as the approved wording.
- **Roads only.** The abstract leaves out buildings. Q3 adds them only if they pass a week-3 go/no-go
  (`selected_questions.md`, Q3 "Target and scope").
- **Synthetic truth is allowed** as a scoring truth for the "synthetic only" tier. The abstract assumes this, but
  Justin has not ruled on it yet (v3 §10, item 2).
- **HRC_WHU outlines may be used** to build clouds. Justin has not ruled on this either (v3 §10, item 1).
- **Plain-language swaps.** These everyday words stand in for the technical terms. The exact terms stay in
  `selected_questions.md`.
  - "skips cloudy ground": a risk–coverage curve for cloud abstention.
  - "plain haze": the uniform-haze control.
  - "preset limit": the ceiling fixed before scoring.
  - "inflates the usual accuracy figure": Q2a's "raises the reported accuracy by more than the noise (about 1.5
    points)".
  - "sealed data": the one batched look at the frozen setup (SpaceNet 8 test tiles, HRC_WHU test images, and any other
    sealed set Justin adds).

## Unresolved issues

1. **References.** None is verified. Sentences 1 and 2 need a citation for the paper. The candidate list has none
   that states the general claim. Portalés-Julià et al. 2023 covers only the flood-mapping case.
2. **The gap sentence (4) rests on one narrow gap.** It covers risk–coverage reporting for cloud abstention, found in
   a limited reading (evidence 02). Q2's full reporting rule, Q1's realism check and Q3's after-only call were not
   searched for. A literature search is needed before any novelty claim (AGENTS.md rule 9).
3. **Two of Justin's rulings are pending:** HRC_WHU outlines, and synthetic truth.
   - If synthetic truth is ruled out, the "synthetic only" tier is empty.
   - Then sentences 8, 9 and 14 change.
4. **The limits and realism margins are not set yet.** The abstract says they are fixed in advance. That must be true
   before scoring starts (v3 §11, item 3).
5. **What the sealed check holds is not decided.** Whether Germany or the north negative set joins it is Justin's call
   (v3 §10, item 11).
6. **The word "users"** in Justin's Q2 wording is wider than the test (evidence 04, §5, checklist item 7). It is kept
   because it is his wording. Sentences 22 and 23 limit the claim.
7. **Why the flooded shares are not in the abstract.** Evidence 01 gives 26% flooded under thin cloud against 55% on
   clear roads. These were left out of the abstract because geography also plays a part (area 0). So on their own
   they do not show that labels were left out under cloud. They sit in the Contribution section with that caveat.
   Q2b is the test that would tell the two apart.

## Suggested next scientific action

1. **Justin reads the abstract.**
   - Check the plain-language swaps above.
   - Rule on synthetic truth and on HRC_WHU outlines.
2. **The scientific critic reviews the abstract** against the evidence files, not only its prose (AGENTS.md rule 8).
   Use the claims audit as the checklist.
3. **Verify the references.**
   - Justin checks the five cited references.
   - Then run a targeted search for prior work on each of the three questions.
   - Only after that may the contribution section claim anything new.
