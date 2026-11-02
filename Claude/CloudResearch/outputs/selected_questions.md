# Selected research questions (checked against the research-question checklist)

Order chosen by Justin on 2026-10-23: **Q2 (lead), Q3, Q1** (see `decision_log.md`). Each question is one sentence.
Its body fixes the parts the checklist asks for (`evidence/04_research_question_guide.md`):
- target and scope;
- condition and levels;
- comparator;
- outcome and the truth that scores it;
- what counts as "no";
- how far the claim reaches.

The methods and numbers behind each are in `outputs/research_questions_refined_v3.md`. Evidence and inference are
kept apart there.

---

## Q2 (lead). What can a flood-road map reliably tell users about roads hidden by cloud?
*Justin's question. Justin asked "can" or "should"; "what can ... reliably" was Claude's suggestion, which Justin kept
(decision log, refinement 1).*

- **Target and scope.** Mapped road segments (the strip about 5 m either side of the centreline) on SpaceNet 8
  Louisiana-East, Hurricane Ida 2021: 0.5 m greyscale Maxar pairs. One frozen flood model, the production model.
  Development data only.
- **Condition (exposure) and levels.** Cloud over a road's strip in the after image. The levels are set by the masks,
  which are fixed before any scoring:
  - clear;
  - thin: at least 20% of the strip under the dark-rise mask;
  - opaque: the tile has at least 20% bright cloud.
- **Comparator.** The same model's calls on clear roads, and the usual single accuracy number that counts hidden roads
  with missing labels as "dry".
- **Outcome and its truth.** For each kind of statement a map could make about a hidden road, its error, scored
  against published labels where they can be trusted:
  - flooded labels can be trusted everywhere;
  - dry labels only on clear roads;
  - synthetic truth, from Q1's test bed, where no trusted label exists.

  The statements:
  - "this road is hidden";
  - "this hidden road is flooded";
  - "this hidden road is dry";
  - accuracy on hidden roads;
  - flooded road length.
- **Reliable means:** the upper end of the error's tile-resampled 95% interval is below a ceiling fixed before
  scoring.
  - A statement whose error can only be measured on synthetic cloud is "synthetic only".
  - One whose error can't be measured at all can be given only as a range.
- **What counts as "no".** Every statement except "this road is hidden" fails its ceiling. Then the answer is that a
  map can say only where it cannot see.
- **How far the claim reaches.** These roads, this sensor and this event. Other targets, sensors and hazards are
  general in design only.
- **Secondary questions (fixed now):**
  - **Q2a.** Does counting cloud-hidden roads as "dry" raise the reported accuracy by more than the noise (about 1.5
    points)?
  - **Q2b.** On tiles with both clear and cloudy roads, do the cloudy roads carry fewer flooded labels than the clear
    ones?

## Q3. When only the before image is cloudy, does the after image alone find change better than both images together?
*The checklist's wording. v3 read "can the after image alone still show what changed". It now names the comparator.*

- **Target and scope.** Mapped objects whose position comes from a map, not from the before image:
  - roads (primary);
  - building footprints (secondary, if they pass a go/no-go check by week 3).

  On the same Louisiana-East tiles, development data only.
- **Condition and levels.** Opaque synthetic cloud on the before image only, at levels fixed in advance. No
  Louisiana-East before image is really cloudy.
- **Comparator.** The two-date production model on the same objects. The cloud-free scores of both models serve as
  the reference.
- **Outcome and its truth.** Balanced accuracy (missed floods and false floods weigh the same), scored against
  published labels on clear objects. The after-only model never reads the before image, so its score is a real-image
  measurement.
- **What counts as "no".** The tile-resampled interval of the after-only minus two-date difference includes 0 or
  falls below it.
- **How far the claim reaches.** Hazards whose after state can be read from one image. A known limit (H3b) is tested
  too: an after-only call should make more false "flooded" calls next to water that was already there before.
- **Secondary questions.**
  - **Q3b.** The permanent-water limit, as above.
  - **Q3c.** Does sending only before-cloudy objects to the after-only call cost clean objects less than the noise?

## Q1 (last). Can we use synthetic clouds to represent real-life blockages in satellite imagery?
*Justin's wording.*

- **Target and scope.** Cloud as it appears in 0.5 m greyscale VHR imagery: SpaceNet 8 Louisiana-East and HRC_WHU's
  five land-cover types.
- **Condition and levels.** Synthetic clouds built from real HRC_WHU cloud outlines, thickness fields and a haze
  model, in two generator families. Thickness levels are set from real thin cloud's measured dark-floor rise.
- **Comparator.** Real cloud in the same imagery, and a deliberately crude control (uniform haze).
- **Outcome and its truth.**
  - **"Represent" means a match** with real cloud, within margins fixed in advance, on two checks:
    - image statistics under cloud (contrast kept, ground pattern kept, patchiness);
    - how the cloud masks score, per land-cover type.
  - **The truth:**
    - real cloud: HRC_WHU's expert masks, and SpaceNet 8 thin cloud found by the mask;
    - synthetic cloud: where the cloud was placed.
- **What counts as "no".**
  - The generator misses a margin.
  - Or it does no better than the crude control.
  - If the control passes as well, the checks can't tell good cloud from bad. Realism is then untested, not shown.
- **How far the claim reaches.** 0.5 m greyscale imagery and the land-cover types that pass, not "satellite imagery"
  in general.
- **Its role in the paper.** Q2's "synthetic only" statements and Q3's cloud both rest on Q1. That is why it is
  tested, even though it comes last.
