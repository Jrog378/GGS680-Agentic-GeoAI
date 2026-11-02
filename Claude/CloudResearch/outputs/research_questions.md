# Research questions: clouds in post-disaster change detection

Stage 1 of the Assignment 3 workflow (research question agent). Written 2026-10-23 by Claude.
This is a proposal. It holds no new results. Every number below comes from `evidence/01_measured_results.md` or the
dev log, and all of it is **development data, never test results**.

## 1. Inputs used

- `Claude/05_Project/AGENTS.md` (rules) and `Claude/05_Project/agents/research_question_agent.md` (role).
- `CloudResearch/input_card.md`, with Justin's final problem statement:
  "Clouds can hide target areas in images taken after disasters. This can lead to labels being inaccurate compared to
  ground truth due to obscured parts of the imagery. How should we detect clouds in this imagery, handle them, and
  report them? The goal is results, such as maps of flooded roads, that people can trust."
- `CloudResearch/evidence/01_measured_results.md` (our measurements) and `02_cloud_literature_summary.md`.
- For read depth and detail:
  - `ProjectBranch/Literature/notes/clouds_review_web.md`;
  - `ProjectBranch/Literature/notes/clouds.md`, AnyTime-CD lines only;
  - `Project/docs/devlog.md`, the 2026-10-23 entries and the 2026-10-15 split entry.
- There was no earlier reviewer feedback.

## 2. Assumptions

- **Time.** The eight weeks start now, so submission is due by about 2026-12-18.
- **Data.** All work uses development data:
  - SpaceNet 8 Louisiana-East: 1,037 touched roads on 217 tiles;
  - the 120 HRC_WHU development images.
  The sealed sets get one logged look, by a frozen setup only:
  - the 40 test tiles and the north negative set;
  - Germany and Louisiana-West;
  - the 30 HRC_WHU test images.
- **Harness.** Runs go through Tilt (project rule). They use the existing 5 folds by tile and paired tests (McNemar,
  tile-block resampling).
- **Trusted labels.** These follow from the labelling rule:
  - a "flooded" label can be trusted anywhere;
  - a missing label means "dry" only on clear roads.
- **Cloud definition.** The dark-rise mask is the working cloud definition, though no two-date cloud labels have
  checked it.
- **Synthetic cloud.** HRC_WHU's expert masks may serve as cloud *shapes* for synthetic cloud. They are not used as
  flood labels. Justin should confirm this fits the labelled-data rule.
- **Scores.** Each criterion gets 1 (weak) to 5 (strong). The scores are my judgement, not validation. Another agent
  agreeing with them would not be independent evidence (AGENTS.md rule 4).

## 3. Ranked candidates

### Score summary

| Rank | Candidate | Course it mostly draws on | Importance | Novelty vs evidence | Testable | Data feasible | Spatial relevance | Tractable | Validation | Total /35 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | C1 Labels missing under cloud | GGS 680 (classical masks), scored with the GGS 662 harness | 5 | 3 | 4 | 5 | 5 | 4 | 3 | 29 |
| 2 | C2 Haze of known thickness on clear roads | GGS 662 (DINO) | 4 | 3 | 5 | 5 | 3 | 5 | 4 | 29 |
| 3 | C3 Where to abstain, and how to report it | GGS 662 (agentic gate) | 4 | 3 | 4 | 5 | 4 | 5 | 3 | 28 |
| 4 | C4 A two-date visibility test | GGS 680 (classical) | 3 | 3 | 3 | 4 | 4 | 4 | 2 | 23 |
| 5 | C5 Does the VLM talk about roads it cannot see? | CSI 709 (VLM) | 3 | 2 | 4 | 4 | 2 | 4 | 3 | 22 |

C1 and C2 tie. C1 ranks first for two reasons:

- it answers the label half of Justin's problem;
- its answer decides how C2 to C5 must be scored.

C2 is the safer lead if C1's checks in section 5 fail.

---

### Rank 1. C1: Labels missing under cloud [mostly GGS 680]

- **Research question.** Are cloud-hidden objects left unlabelled more often than clear objects nearby?
- **Hypothesis.**
  - Roads under cloud are less likely to carry a "flooded" label than clear roads nearby with similar flooding.
  - The gap is largest under opaque cloud.
  - Scoring these roads makes a model's accuracy look better than it is.
- **Expected observable evidence.**
  - An odds ratio below 1 for "labelled flooded" under cloud. It is adjusted for how flooded the clear neighbours
    are, and its tile-resampled interval stays below 1.
  - A larger effect with the bright (opaque) mask than with the dark-rise (thin) mask.
  - Accuracy rises, and recall on trusted flooded roads falls, when cloudy roads are scored. This uses the same
    model calls with and without those roads.
- **What we already measured.** This is evidence, development data.
  - Labels say "yes" (487 roads) or nothing (593). "No" never occurs.
  - Labelled flooded:
    - 2% on the 17 tiles with at least 20% thick cloud;
    - 26% under thin cloud;
    - 55% in clear sky.
  - In area 2, one cloudy tile has 0 of 7 roads labelled flooded, against 79% on its clear neighbours.
  - In area 0, the cloudy tiles' neighbours are dry too. That is geography, not missing labels.
  - Dry roads under cloud are "kept dry" 94% of the time.
  - SpaceNet 8's analysts were told to "only attribute what was visible" (Hänsch et al. 2022, p. 3).
- **Plausible data.**
  - Louisiana-East development roads and tiles.
  - The bright, dark and dark-rise masks.
  - Optional: a public elevation layer as a flood-risk covariate. It is not in the evidence files, and it would be
    a new download, so it needs Justin's OK.
  - One sealed look after freezing: the 40 test tiles and Germany.
- **Plausible method.**
  - A logistic model of "labelled flooded". Inputs:
    - cloud share on the road;
    - the flood share of clear roads within a fixed radius;
    - area.
    Tiles are clusters.
  - Tile-block resampling, plus a permutation that shuffles cloud between tiles within each area.
  - Each mask is run on its own.
  - The radius, thresholds and test are fixed before looking.
  - Optional cross-check: C2's synthetic haze gives the accuracy expected under cloud when the labels are true.
- **Spatial checks.**
  - Flooding is spatially dependent, hence the neighbour adjustment and the block resampling.
  - The cloud is clustered in areas 0 and 2, a sampling bias.
  - The neighbour radius changes the answer (a MAUP-like choice). Report results across a radius range fixed in
    advance.
- **Main threat to validity.**
  - **Confounding.** Storm cloud and flood extent are both clustered in space.
  - **A mask artefact.** Floodwater is dark. So the dark-rise mask may miss thin haze over flooded roads and flag it
    over dry ones. That alone would produce "cloud means dry".
    - We checked only that the masks do not fire on floodwater (0% on the most flooded tile). We did not check
      whether they miss haze over water.
  - **Low power.** Only 17 tiles have opaque cloud. The tile-resampled interval for the cloud effect on recall
    (−0.54 to +0.001) just reaches 0.
- **What would weaken or refute it.**
  - The odds-ratio interval includes 1 after the neighbour adjustment under the bright mask. The bright mask is the
    one least exposed to the water artefact.
  - Or the effect vanishes within the fixed radius range.
  - Or C2's injection shows the dark-rise mask finds haze less often over flooded roads.
- **Novelty.** The evidence shows only a gap in the sources read: "no peer-reviewed PU paper on flood or change
  labels under cloud" was found. The SpaceNet 8 paper itself already notes that its baseline learned the
  visible-only rule (p. 6). So the new part would be measuring the bias, not finding it. Any novelty claim needs
  Justin's approval.

---

### Rank 2. C2: Haze of known thickness on clear roads [GGS 662]

- **Research question.** How fast does change detection fail as haze thickens?
- **Hypothesis.**
  - Accuracy falls steadily as synthetic haze thickens on one date.
  - Frozen DINOv2 change cues lose less than classical cues.
  - De-hazing only where the mask fires wins back part of the loss.
- **Why clear roads.** Both "flooded" and "dry" labels can be trusted there. So adding haze gives a controlled test
  with valid labels.
- **Expected observable evidence.**
  - Accuracy, flooded recall and dry-call rate against haze thickness, for each cue family.
  - Paired McNemar tests at each thickness, Holm-corrected.
  - **A realism check.** At the real cloud's estimated thickness, the curve should reproduce the measured real drop:
    87% recall in clear sky against 67% under thin cloud, on 24 trusted flooded roads.
- **What we already measured.** This is evidence, development data.
  - DINOv2 change cues add +1.6 points on the 798 assessable roads (p 0.019).
  - Whole-image de-hazing cost −1.7 points (p 0.15). It also found 3 more of the 24 trusted flooded roads under
    cloud, which is not significant.
- **Plausible data.**
  - Clear Louisiana-East development roads.
  - HRC_WHU development masks, used as cloud shapes only.
  - The same set-up with the dates swapped covers the "before image is cloudy" case. No Louisiana-East before image
    is cloudy.
  - One sealed look after freezing: the test tiles and Germany.
- **Plausible method.**
  - Add haze with the scattering model behind the dark channel (He, Sun & Tang 2011): image = ground × t +
    air light × (1 − t).
  - Use a fixed grid of t values, spread by HRC_WHU mask shapes with soft edges.
  - Train on clean tiles in the existing folds. Test on hazed copies of the held-out tiles.
  - Compare the classical, texture, DINOv2 and production feature sets.
  - Show pictures of the inputs, what DINOv2 receives, and the errors.
- **Spatial checks.**
  - Folds by tile limit leakage.
  - Haze is applied per tile, so neighbouring roads share it.
  - Co-registration error (about 0.6 m) is the same with and without haze.
- **Main threat to validity.**
  - **Realism.** Real cloud is not an even layer. It has texture and shadows, and its opacity varies.
  - **Circular de-hazing.** De-hazing with the same model used to add the haze will look better than it would on
    real haze.
- **What would weaken or refute it.**
  - The DINOv2 curve is not above the classical curve at any thickness, with intervals including 0.
  - Or the curve does not reproduce the real-cloud drop. Then synthetic haze cannot stand in for real cloud.
- **Novelty.** AnyTime-CD (Qu, Li & Huang 2026) already adds thin, semi-transparent and thick simulated cloud in
  change detection. Per the project's notes, 30% extra thick cloud cost about 3.6 F1 points there. The sources read
  found no test of DINOv2 change features under haze (two arXiv queries). That is a gap in the sources read, not a
  shown novelty.

---

### Rank 3. C3: Where to abstain, and how to report it [GGS 662]

- **Research question.** Should a change system skip cloudy objects one by one, or whole tiles?
- **Hypothesis.**
  - At the same coverage, skipping single roads by their own cloud share gives fewer errors on trusted labels than
    skipping whole tiles.
  - Roads handed back from cloudy tiles are less accurate than clear roads.
- **Expected observable evidence.**
  - Risk–coverage curves for road-level and tile-level rules, with tile-resampled bands.
  - A paired difference in the area under each curve.
  - A cannot-assess share reported by area.
- **What we already measured.** This is evidence, development data.
  - Flooded found, by rule:
    - tile rule: 85.8% of flooded roads, on 891 roads;
    - road rule: 87.4%, on 808 roads;
    - both rules: 87.8%, on 798 roads.
  - No rule changed accuracy significantly on the 766 roads all rules share.
  - The 10 roads handed back from cloudy tiles were called right only half the time.
- **Plausible data.** The same development roads and masks. The "both" rule is already in production.
- **Plausible method.**
  - Sweep the cloud-share cut-off per road and per tile.
  - Risk is defined two ways:
    - misses on trusted flooded roads, which are valid everywhere;
    - errors on clear roads only.
  - Selective classification framing: Geifman & El-Yaniv 2017, a conference paper.
  - Reporting the unassessed share: Olofsson et al. 2014.
  - Optional third route, "before cloudy, after clear": an after-only call, tested on C2's swapped-date haze.
- **Spatial checks.**
  - Tile, road and window are different units, so the choice of unit shapes the result (MAUP). This is the question
    itself.
  - Report every unit.
- **Main threat to validity.**
  - Error on dry roads under cloud cannot be measured, because those labels are not trusted. So the curve is
    partial.
  - The flooded roads left under cloud are few (24).
  - The fold assignment alone moves accuracy by about 1 point.
- **What would weaken or refute it.**
  - The road-level and tile-level curves overlap across coverage, with an interval for the difference including 0.
  - Present evidence leans this way. Abstaining would then rest on label validity alone, not on fewer errors.
- **Novelty.** The sources read found no remote-sensing paper with risk–coverage curves for cloud abstention (one
  extended web search, one arXiv query). That is a gap in the sources read only.

---

### Rank 4. C4: A two-date visibility test [GGS 680]

- **Research question.** Can comparing the after image with the clear before image tell haze from opaque cloud?
- **Hypothesis.**
  - Local before/after statistics on one grey band sort windows into four kinds:
    - **haze:** the dark floor is raised, but the pattern is kept;
    - **opaque cloud:** a strong rise, and the pattern is lost;
    - **shadow:** darker, with the pattern kept;
    - **floodwater:** the surface is replaced.
  - Then some of the 93 cloudy roads can be assessed again without more errors.
- **Expected observable evidence.**
  - How many of the 93 roads move from opaque to haze.
  - Recall on the 24 trusted flooded roads, no lower than now.
  - No change on clear roads.
  - Few false alarms on bright calm water and bare ground. These are where the absolute dark channel fired on 55
    clear before images.
- **Plausible data.**
  - Louisiana-East development tiles.
  - HRC_WHU development images, for the single-date parts only.
  - C2's synthetic pairs, where the truth is known.
- **Plausible method.**
  - Windows of about 10–20 m along each road strip.
  - Two tests after Hagolle et al. 2010: the rise of the local dark floor, and the local before/after correlation.
  - Thresholds are learned on the training tiles, then frozen.
  - Optional local de-hazing of haze windows (Makarau et al. 2014, or He et al. 2011).
- **Spatial checks.**
  - The window size is a scale choice.
  - Co-registration (about 0.6 m) and lean of tall structures (5–13 m on area-0 tanks) lower the correlation without
    any cloud.
- **Main threat to validity.**
  - No two-date cloud labels at this resolution were found, so checks on real cloud are indirect.
  - Synthetic truth uses the same haze model the test assumes, so that check is circular.
  - No shadow labels exist: HRC_WHU did not label shadows.
  - Floods also lower the correlation, so opaque cloud and floodwater can be confused.
- **What would weaken or refute it.**
  - The four kinds do not separate even on synthetic pairs.
  - Or roads moved back to "assessable" are called worse than clear roads, like the 10 handed-back roads (50%).
- **Evidence caveat.** Hagolle et al. 2010 was read only as an abstract, from a catalogue snippet. Makarau et al.
  2014 was read only as an abstract. Both need a full read before the method rests on them.

---

### Rank 5. C5: Does the VLM talk about roads it cannot see? [CSI 709]

- **Research question.** Does giving Gemma the cloud mask stop it describing roads it cannot see?
- **Hypothesis.**
  - Without the mask, Gemma often states a flood state for roads under opaque cloud.
  - With the mask result in the prompt, it does so less often.
  - Its descriptions of clear roads stay the same.
- **Expected observable evidence.**
  - The rate of flood claims on roads hidden by synthetic opaque cloud. These are hidden by construction, so any
    claim about them is unsupported.
  - The same rate on real bright-mask roads.
  - How often Gemma's "visible / partly / not visible" word agrees with the mask.
- **Plausible data.** Development road crops, C2's synthetic cloud, and the local `gemma4:12b` (num_ctx 4096).
- **Plausible method.**
  - Two arms on the same crops: mask in the prompt, or not.
  - Neutral fixed prompts, temperature 0.
  - Code parses the answers. Paired McNemar.
  - Gemma describes only. Its words are measured, never used as labels or decisions.
- **Spatial checks.** Few. The unit is the road crop. Pick crops by a rule fixed before looking.
- **Main threat to validity.**
  - The supporting sources are all preprints or workshop papers: Kethavath & Hu 2026, RemoteShield 2026,
    CloudWeb 2026. They are method attributions, not citable evidence under the JIF rule.
  - The parser that codes free text is itself a measuring tool with errors.
  - Prompt wording sways the answers.
- **What would weaken or refute it.**
  - Gemma rarely makes such claims even without the mask.
  - Or the rate does not fall with the mask.
- **Fit.** Too thin for a JIF > 4 paper on its own. It fits better as one section of C3.

---

### Reference status

None of these references is verified by Justin yet.

**From the input card.** The card says Justin verifies these before any novelty claim.

| Reference | Status |
|---|---|
| Portalés-Julià et al. 2023 | Full text searched by Claude. |
| Qu, Li & Huang 2026 (AnyTime-CD) | On disk; pages read per `clouds.md`. |
| Zou et al. 2025 (Cloud-Adapter) | Table values come from a page-fetch summary. Confirm them in the PDF. |
| Song et al. 2023 (DehazeFormer) | JIF still to confirm in JCR. Not used here: it works on RGB and trains on synthetic haze. |
| Guo et al. 2024 (SkySense) | Not used. |
| Hou et al. 2026 | Not used. SAR is outside the greyscale-optical rule. |

**From the evidence files.**

| Reference | Status |
|---|---|
| Hänsch et al. 2022 (SpaceNet 8) | On disk; pages quoted. Its venue is not given, so it is a dataset attribution. |
| He, Sun & Tang 2011 | Metadata only. |
| Li et al. 2019 (HRC_WHU) | Abstract and README. |
| Mateo-Garcia et al. 2021 | Full text searched. |
| Hagolle et al. 2010 | Abstract snippet only. |
| Makarau et al. 2014 | Abstract only. |
| Li, Guo & Elkan 2011 | Metadata only. |
| Olofsson et al. 2014 | On disk. |
| Geifman & El-Yaniv 2017 | Abstract; a conference paper. |
| `whitehead2022reliable` | ECCV; borderline. |
| `wen2025know` | TACL; kept. |
| Kethavath & Hu 2026, RemoteShield 2026, CloudWeb 2026 | Preprints or workshop papers: method attributions only. |
| Xia et al. 2021 | Workshop paper: method attribution only. |

## 4. Unresolved issues

1. **The dark-rise mask is unchecked.** No real two-date cloud labels exist for it. HRC_WHU is single-date. Its
   images also span 0.5–15 m and are Google Earth RGB turned into grey.
2. **The floodwater artefact.** The dark-rise mask may miss haze over dark floodwater. That could fake C1's effect.
   It is untested.
3. **Power.** There are only 17 opaque-cloud tiles and 24 trusted flooded roads under thin cloud. How much cloud the
   40 sealed test tiles hold is unknown.
4. **Germany as the outside check.**
   - How much cloud it has is unknown.
   - The one tile seen pairs a winter, snowy, hazy before image with summer after images.
   - Its class totals were read before sealing (this is disclosed).
   - The evidence does not say whether its labels store an explicit "not flooded" value. Louisiana-East's never do.
     If Germany's do, C1's label pattern may not carry over.
   - Louisiana-West has no labels, so it cannot be scored.
5. **Decisions for Justin.**
   - May HRC_WHU masks serve as cloud shapes for synthetic haze?
   - May we download an elevation layer for C1?
   - Does C1's label analysis on the sealed sets count as the one logged check?
   - May a person look at hidden roads as an audit, or is that "own labels"?
6. **Citation rules disagree.** AGENTS.md and the input card accept major conferences. The project's memory rule
   keeps only JIF > 4 journals or company papers. This decides whether Geifman & El-Yaniv 2017 is evidence or an
   attribution.
7. **Cloud shadows are untested.** Whether they pose as floods at 0.5 m is unknown, and no shadow labels exist at
   this resolution.
8. **Small effects.** Effects under about 1 point cannot be read, because the fold assignment alone moves accuracy
   that much.

## 5. Suggested next scientific action

Write a one-page pre-registration for C1: the neighbour radius range, the masks, the model, the test and a stop rule.
Then run two development-only checks through Tilt.

1. **Power.** With 17 opaque-cloud tiles and 93 thin-cloud roads, what odds ratio could a tile-block test detect?
2. **The floodwater artefact.** Add haze of known thickness (C2's tool) over clear flooded and clear dry roads. Does
   the dark-rise mask find it equally often over both?

**Go/no-go.**
- If C1 has useful power and the mask finds haze equally often over both, lead with C1. Use C2 as its controlled
  check and C3 as its reporting method.
- If not, lead with C2, and report C1's label finding as a limitation.
