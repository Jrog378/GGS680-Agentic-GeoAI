# Stage 1 (revision): Research Question Agent: Three Refined Research Questions

- **Source packet:** `outputs/prompt_packets/01_research_question_agent.md` (generated 2026-10-04 10:57)
- **Revises:** `outputs/history/research_questions__20261004-105702.md` (RQ1–RQ4), responding to `outputs/question_review.md` (Stage 2, verdict REVISE), the decision log H1 and the notes N1.
- **Status:** Proposal only. Nothing here is a result. No novelty, causal, policy or external-validity claim is made, and none can be made without human approval (AGENTS.md rule 9).
- **Broad problem (unchanged, form A1):** *How can Agentic GeoAI help interpret large sources of satellite imagery in an area of interest to understand patterns and changes over time?*
- **Caveat on H1:** The packet says the H1 rows were drafted by Claude Code and that Justin has not reviewed them yet. I treat them as binding for this revision. Wherever an option depends on an H1 row, or would change one, I say so, so the human can overturn it.
- **Caveat on agreement:** Where this revision agrees with the Stage 2 critic, that is not independent validation (rule 4). Both are LLM outputs that read the same truncated evidence.

---

## 1. Inputs used

| Input | Used for | Caveat |
|---|---|---|
| Form A1–A3 and human notes | Broad problem, boundary conditions, data plan: MuRA-T Landsat-8 band 8 (15 m), SpaceNet 7 / MUDS monthly building footprints, Sentinel-1 GRD; 10–20 AOIs; whole-AOI hold-out | Nothing downloaded yet. Per-AOI Sentinel-1 coverage is marked "TO VERIFY" |
| H1 decision log (20 rows) and N1 | Binding constraints: what was accepted, changed or rejected. N1 asks for three genuinely different options and a recommendation | Rows drafted by Claude Code; not yet reviewed by Justin |
| `outputs/question_review.md` (Stage 2) | Issues X1–X10 and Q1.1–Q4.3; the RQ1-R design | An LLM review. Agreeing with it is not validation |
| Previous Stage 1 output | Baseline for "what changed and why" | None |
| L1 references (10) | Citation pool | All 10 are now marked "read and verified by the human" (they were unverified in the previous round) |
| Evidence text (10 papers) | Facts cited below | Each paper is cut off at 20,000 characters. Results, limitations and appendices are mostly unseen |

## 2. Assumptions (all require human confirmation)

- **A1.** The H1 rows are binding for this revision, pending Justin's review.
- **A2.** "Agent" means an LLM that calls predefined, deterministic tools in a ReAct-style loop, as in Earth-Agent (Feng et al., 2026). There is no model training and no free-form code generation (H1, tools row). Conclusions therefore hold only for curated tool environments, which Kao et al. (2026) criticise as missing "in-the-wild" complexity.
- **A3.** One researcher, AI-assisted coding, and a paper *submitted* (not accepted) within 8 weeks. The LLM backbone and API budget are unknown. The budget is capped in the pre-registration (H1).
- **A4.** MuRA-T and SpaceNet 7 are as described in the form. Per-AOI scene counts, usable panchromatic months and counts of new-building cells are all unknown until download.
- **A5. Scale (inference).** Qu et al. (2026) describe MUDS images as 1024 × 1024 pixels at about 4.77 m, so an AOI is roughly 4.9 × 4.9 km. That gives about 2,400 cells of 100 m per AOI, with about 7 × 7 panchromatic pixels and 10 × 10 Sentinel-1 pixels per cell.
- **A6.** MuRA-T is used as a data source and is not cited as a reference (form).
- **A7.** Statements about the papers refer only to the visible, truncated text.

---

## 3. Shared design (applies to all three questions)

The three questions share one data pipeline, one reference and one set of tools. That shared base is what makes each of them feasible in 8 weeks. Only the arms and the primary contrast differ.

### 3.1 Data and AOI selection
- **Panchromatic.** Landsat-8 OLI band 8 (15 m) from MuRA-T: Collection 1 Level-1 (L1TP), the least-cloudy scene per month, with the QA band and cloud mask, co-registered to the SpaceNet 7 grid (form). Relative radiometric normalisation is applied before any change statistic (H1, X8), for example against pseudo-invariant pixels chosen on development AOIs [citation needed]. Raw band 8 is used, with no pan-sharpening, because Michel & Inglada (2026) report that the scale-invariance hypothesis behind band-sharpening is unrealistic.
- **SAR.** Sentinel-1 C-band GRD (IW) from Earth Engine. Lee et al. (2026) used the same collection: thermal-noise removal, calibration and orthorectification, with 10 m pixels. Use one orbit track per AOI (the one with the most scenes), and record the pass direction and incidence-angle range (H1, X5). The human co-registers it to the MuRA-T grid. A one-pixel shift is tested as a robustness check, because Qu et al. (2026) show that misalignment creates pseudo-change.
- **Reference.** SpaceNet 7 / MUDS monthly building footprints. Qu et al. (2026) describe MUDS as 60 AOIs with 24 monthly PlanetScope frames at about 4.77 m and building labels at every time point, with 17–24 usable frames per AOI after cloud and haze filtering. The labels are traced on imagery separate from both tested sensors (form).
- **AOIs.** Choose 10–20 of the 60 AOIs with a rule that is pre-registered before any tool runs: at least N₁ Sentinel-1 scenes on one track within the label window, at least N₂ new-building cells, and at least N₃ usable panchromatic months. *Inference:* selecting on reference prevalence limits external validity, but it does not bias the paired comparisons.
- **Split.** Whole AOIs are assigned to development (prompt iteration, threshold tuning, pilots) or to test (run once, after freezing) (H1). *Inference:* nothing is trained, so a larger test share than Qu et al.'s 4:1:1 split is defensible, for example 4 development and 8–14 test AOIs.

### 3.2 Grid, CRS and scale
- **Cells.** 100 m cells. The query unit is the scoring unit: one cell per query (H1).
- **CRS check (inference, [citation needed]).** About 4.77 m is the nominal equatorial pixel size of a Web-Mercator zoom level, so the SpaceNet 7 grid may be Web Mercator. If it is, a "100 m" cell measured in grid units is smaller on the ground away from the equator, by a factor of cos(latitude). Define cells in metres in a local UTM zone, or report the true cell area per AOI. Resample every layer once, with a stated method.
- **Scale limits.** About 7 × 7 panchromatic pixels per cell. No claims are made about individual buildings.
- **MAUP.** Repeat each question's primary metric at 200 m, and nothing else.

### 3.3 Reference and onset (H1, X3)
- **Positive cell.** A cell is new-building positive if at least A_min m² of footprint that was absent in the first usable label month appears inside it during the window. A_min is pre-registered, and footprints that straddle cells are split by area. Cells that are already built at month 1 and gain no new footprint are negative, kept as a separate "existing built" stratum. Demolitions (footprints that disappear) are reported separately.
- **Onset.** The first month a SpaceNet 7 footprint appears in the cell. Error is measured in months. Where label months are missing, the onset is a bracket, and its width is reported.
- **Lag.** The signed difference between the estimated onset and the reference onset is reported as its own estimand (H1). *Inference:* the labels mark visibility, which is closer to completion than to the start of construction (form), and Lee et al. (2026) link SAR up-steps to construction. SAR onsets are therefore expected to lead the label.

### 3.4 Tools and outputs
- **Tools.** All tools are predefined and deterministic, and they are identical wherever arms share them:
  - a Sentinel-1 per-cell series (VV, plus VH where available) with a speckle filter fixed in advance;
  - a Gamma likelihood-ratio change test returning candidate change months and a statistic (the LRT framework in Lee et al., 2026);
  - a normalised panchromatic per-cell series with its cloud mask;
  - a panchromatic change magnitude and month;
  - a data-availability tool (scene counts, missing months).
- **Outputs.** Tools return numbers and short text, not images. This keeps cost low, and no VLM is involved (H1).
- **Answer schema.** `{presence: yes | no | abstain, onset_month | null, evidence_cited}`. Scoring is deterministic. Failures are classified by fixed rules adapted from Kao et al.'s C1/C2/C3/D categories (Kao et al. used an LLM to classify them; this study does not).
- **Trajectories.** Tool-call trajectories are logged and summarised descriptively, following the dual-level evaluation of Feng et al. (2026).

### 3.5 Leakage and prior-knowledge controls
- **Opaque inputs.** The agent sees opaque cell IDs only, never coordinates, SpaceNet AOI codes or place names (H1, X6). *Suggestion (needs human decision):* express dates as month indices within the window, which closes the route from calendar dates to remembered events.
- **Tools-disabled control.** A tools-disabled agent runs on a subsample (H1). Its accuracy should be near chance. If it approaches the full agent's accuracy, the comparison is invalid.
- **Freezing.** Prompts, thresholds, margins and strata bands are frozen before any test-AOI run. Test AOIs are not inspected while prompts are designed (X7).

### 3.6 Inference
- **Primary inference.** The AOI-level cluster bootstrap (H1). McNemar's test (presence) and the Wilcoxon test (onset) are secondary only.
- **Few clusters.** With 8–14 test AOIs, bootstrap coverage may be poor [citation needed]. Report the number of test AOIs, the per-AOI estimates, and a mixed model with an AOI random effect as a sensitivity check.
- **One primary endpoint** per question (X9). Everything else is labelled secondary or exploratory.
- **Runs.** One pinned LLM backbone, with run dates logged. Run 3 repeats on the test sample, or, if the budget cap binds, 1 run on all cells plus 3 repeats on a 20% subsample.

### 3.7 Sample, budget and schedule
- **Sample.** Per test AOI, a stratified sample of about 60 cells (illustrative). The strata cross reference status (new / existing built / never built) with tool-output status (concordant / conflict-or-borderline). Allocations are fixed, and design weights are recorded so that population-level F1 can be reported as a secondary result. The pilot sets the final n.
- **Cost (illustrative).** 10 test AOIs × 60 cells × 3 repeats = 1,800 episodes per agent arm. Q-A needs one agent arm plus small controls. Q-B and Q-C each need two arms, and Q-C adds a placebo arm on a subsample. Tokens per episode come from the pilot.
- **Schedule (any option).**

| Week | Work |
|---|---|
| W1 | Download the data; inventory the AOIs; feasibility check (§10); draft the pre-registration |
| W2 | Build the grid and rasterise the reference; build the tools and the pipeline |
| W3 | Development-AOI runs; 20-cell pilot; prompt iteration |
| W4 | Freeze and pre-register; run the test AOIs |
| W5 | Analysis and robustness checks |
| W6 | Draft |
| W7 | Internal review and revision |
| W8 | Submission buffer |

---

## 4. Ranked summary and recommendation

Each option isolates a different part of an agentic GeoAI system: **the reasoning layer** (Q-A), **the second sensor** (Q-B) or **spatial context** (Q-C). They are three different scientific claims, not three wordings of one. Ratings are my judgements (H = high, M = medium, L = low).

| Rank | ID | Short title | Contrast | Primary endpoint | Importance | Novelty vs supplied evidence | Testability | Data feasibility | GeoAI / spatial relevance | Tractability (8 wk) | Validation |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Q-A** | Agent vs fixed pipeline with the same tools | Agentic layer on/off | Presence-F1 non-inferiority (as fixed in H1) | H | M (unverified) | H | H | M–H | M–H | H |
| 2 | **Q-B** | Does 15 m panchromatic add to Sentinel-1? | Panchromatic tools on/off, inside the agent | ΔF1 (SAR+pan − SAR-only) | H for this project | M (unverified) | H | H | H | H | M–H |
| 3 | **Q-C** | Does neighbourhood context help? | Adjacent-cell tool on/off/placebo, inside the agent | ΔF1 (context − cell-only) | M–H | M (unverified) | H | H | H | M | H |

**Recommendation: Q-A.**
1. It is the only option that answers the broad problem's core question, *what does agentic GeoAI add?*, with a contrast in which agency is the only difference between arms (Q1.1–Q1.3).
2. It keeps every H1 decision as written, including the primary endpoint. The only open human inputs are δ, the borderline band and the abstention threshold.
3. Q-B's contrast is already inside Q-A as the required secondary analysis (H1), so choosing Q-A still answers "does panchromatic add anything?", only not as the headline.
4. It has the lowest API cost: one agent arm, because the pipeline arms are free.

**Proposed switch rule (needs human approval; thresholds illustrative).** In the W3 development pilot, the agent might disagree with the pipeline on fewer than 5% of cells, and there might be fewer than about 10 conflict/borderline cells per AOI. If so, Q-A's superiority test is underpowered and its non-inferiority test is close to trivial, so promote Q-B to primary. Choosing Q-B or Q-C would replace H1's primary endpoint, which requires Justin's explicit approval. Q-C is better kept as a follow-on paper unless the shared infrastructure is finished by the end of W3.

---

## 5. Q-A (Rank 1, recommended): Does an LLM agent add anything over a fixed pipeline that uses the same SAR and panchromatic tools?

**Research question.** In held-out SpaceNet 7 AOIs, an LLM agent answers pre-registered questions about one 100 m cell at a time: "Did new buildings appear in this cell during the window? If so, in which month?" It answers by calling predefined Sentinel-1 and Landsat-8 panchromatic time-series tools.
- (a) Is its new-building presence-F1 **non-inferior** to a fixed pipeline that uses the same tools, with a fusion rule and thresholds tuned on development AOIs?
- (b) Is it **more accurate** than that pipeline on cells where the tools give conflicting or borderline evidence?
- (c) Does it **abstain** when the data cannot support an answer?

**Candidate hypotheses** (the human sets δ, the borderline band and the abstention threshold before any test run):
- **H-A1 (primary, non-inferiority).** F1_agent − F1_pipeline > −δ, meaning the lower bound of the 95% AOI-cluster bootstrap CI lies above −δ.
- **H-A2 (secondary, superiority on the conflict stratum).** The stratum is defined from tool outputs only, before any reference is consulted: cells where the SAR and panchromatic tools disagree on presence, or where the LRT statistic lies within the pre-set band around the pipeline threshold. On this stratum, the agent's balanced accuracy exceeds the pipeline's.
- **H-A3 (secondary, abstention).** On pre-registered unanswerable queries (cells or months with no valid data, or months outside the archive; analogues of Kao et al.'s C1/C2), the agent abstains at or above the pre-set rate. Fabricated answers are counted.

**Expected observable evidence.**
- Paired per-cell correctness for both arms, and ΔF1 with an AOI-cluster CI.
- Agent–pipeline agreement rate, and override accuracy: the share of the agent's departures from the pipeline that are correct.
- Conflict-stratum accuracy, and abstention and fabrication counts.
- Onset error in months on reference-positive cells, with misses penalised. Detection-conditional error is also reported, together with detection coverage (Q1.5).
- The signed SAR-to-label lag.
- SAR-only vs SAR+pan for both arms (the secondary analysis required by H1).
- Tools-disabled control accuracy.

**Plausible data and arms.** Shared design (§3).
1. Agent with SAR + panchromatic tools.
2. Fixed pipeline with the same tools.
3. Tools-disabled agent on a subsample.
4. SAR-only variants of arms 1 and 2 for the H1 secondary analysis: the pipeline on every sampled cell, and the agent on a subsample if the budget cap binds.

**Plausible method.**
1. Build the tools and the pipeline. Tune the pipeline's fusion rule on development AOIs.
2. Write the question templates, including the unanswerable ones. Iterate on prompts using development AOIs only.
3. Run a 20-cell pilot: agreement rate, parse rate, tokens per query. Apply the switch rule (§4).
4. Freeze everything. Pre-register δ, the band, the thresholds, the sample allocation and the primary endpoint.
5. Run the test AOIs once and score deterministically.
6. Robustness, for H-A1 only: 200 m cells (MAUP), a one-neighbour tolerance along the look direction (H1), and a one-pixel misregistration shift.
7. Limitation paragraph: no direct VLM is evaluated. TEOChat is capped at 8 input images (Irvin et al., 2025), and EarthDial describes temporal processing for RGB sequences (Soni et al., 2025). The arm was dropped by H1.

**Main threat to validity: the "wrapper" outcome.** If the agent simply copies the pipeline's tool outputs, H-A1 holds trivially and the conflict stratum stays small. The study then cannot show positive value, or tell reasoning apart from pass-through (Q1.3).
- Report the agreement rate and override accuracy.
- Oversample the conflict stratum. This is legitimate because the stratum is defined from tool outputs only.
- Pre-register a minimum stratum size and the switch rule.

Secondary threats: few test AOIs give wide CIs, and conclusions hold only for curated tool environments (A2).

**What would weaken or refute it.**
- If the lower CI bound of ΔF1 falls below −δ, H-A1 is refuted: the agent costs accuracy.
- If the conflict-stratum CI includes 0 or favours the pipeline, H-A2 is refuted.
- Override accuracy at or below 50% means the agent's departures do harm.
- If the tools-disabled agent comes close to the full agent's accuracy, leakage invalidates the comparison.
- Agreement near 100% makes H-A1 uninformative. That weakens the study rather than refuting the hypothesis.

**What changed from the previous version (RQ1), and why.**

| Previous RQ1 | Q-A | Why |
|---|---|---|
| Agent vs direct VLM (H1a), confirmatory | VLM arm removed entirely; mentioned as a limitation | H1: confounded and close to predetermined; a 100 m cell is about 7 × 7 pan pixels; no time to set up a VLM (Q1.1) |
| Archive-size factor (H1b) | Removed | H1: true by construction (Q1.2) |
| Agent vs pipeline, non-inferiority only (H1c) | Non-inferiority primary, plus conflict-stratum superiority and abstention | H1 accepted RQ1-R: this gives the agent a real chance to show value (Q1.3). Abstention is folded in from RQ2 |
| One AOI with development/test blocks; 300–500 hand-labelled cells; NAIP | 10–20 SpaceNet 7 AOIs with a whole-AOI split; SpaceNet 7 labels | H1: the AOI is the independent unit; no labelling; NAIP unfit for onset (X2, X4) |
| Onset bracket from optical interpretation; one-frame tolerance | Onset = first label month; error in months; lag as its own estimand | H1, X3 |
| McNemar and Wilcoxon as main tests | AOI-cluster bootstrap primary | H1, X4 |
| DEM-based layover mask | Orbit and incidence recorded; look-direction neighbour sensitivity | H1, X5 (a terrain DEM does not contain buildings) |
| No prior-knowledge control | Opaque IDs; tools-disabled control | H1, X6 |
| Landsat 8/9 panchromatic, product level unstated | MuRA-T Landsat-8 band 8, Level-1, normalised | H1, X8 |
| RQ4 as an optional ablation | SAR-only vs SAR+pan as a required secondary analysis | H1 |
| Per-template non-inferiority; many endpoints | One query unit; one primary endpoint | H1, Q1.6, Q1.7, X9 |

**Criteria evaluation.**
1. **Importance (H).** It asks directly what the agentic layer adds. The supplied evidence shows large reliability gaps: about 60% with reflexion on yes/no EO questions, "only marginally above random chance" (Kao et al., 2026), and a best overall QA accuracy of 34.1% on DVL-Bench (Xuan et al., 2025).
2. **Novelty (M, supplied evidence only).** None of the ten papers compares an agent with a same-tool pipeline on SAR + panchromatic time series. This was "not found in our search"; it is not a novelty claim.
3. **Testability (H).** A paired design with a pre-registered margin.
4. **Data feasibility (H)**, if the AOI inventory passes.
5. **Spatial relevance (M–H).** Per-cell location and timing, AOI hold-out, and layover and MAUP checks. The contrast itself is not spatial.
6. **Tractability (M–H).** One agent arm, no training, no labelling.
7. **Validation (H).** Independent reference, AOI hold-out, deterministic scoring and leakage controls.

---

## 6. Q-B (Rank 2): Does 15 m panchromatic imagery add anything to Sentinel-1 for an agent detecting new buildings?

**Research question.** In held-out SpaceNet 7 AOIs, does giving a tool-using LLM agent Landsat-8 panchromatic tools, in addition to Sentinel-1 tools, change how accurately it identifies 100 m cells that gain new buildings? If it does, does the change come from fewer SAR false alarms (precision), from buildings that SAR misses (recall), or from dating?

**Candidate hypotheses.**
- **H-B1 (primary).** ΔF1 = F1(agent, SAR+pan) − F1(agent, SAR-only) > 0, meaning the lower bound of the 95% AOI-cluster bootstrap CI is above 0. The two-sided CI is reported. A CI that includes 0 is the informative negative result.
- **H-B2 (mechanism, secondary).** The gain lies mainly in precision: fewer false positives among reference-negative cells whose SAR series show a change. *Inference:* two error sources are specific to SAR, and a near-nadir optical channel does not share them. Lee et al. (2026) attribute impulse-type changes to temporary infrastructure and moving objects, and Hou et al. (2026) describe layover from side-looking geometry.
- **H-B3 (exploratory).** Each sensor has its own signed onset lag relative to the label month. A direction is predicted for SAR only: SAR onsets lead the label (median signed error < 0). No direction is pre-registered for panchromatic.
- **H-B4 (secondary).** The same ΔF1 for the fixed pipeline, computed on every cell of the test AOIs at no API cost. Comparing it with the agent's ΔF1 shows whether the agent exploits panchromatic as well as a tuned fusion rule does. The interaction is exploratory.

**Expected observable evidence.**
- ΔF1 with a CI, plus Δprecision and Δrecall.
- Confusion-matrix shifts in two pre-defined subsets: reference-negative cells where SAR shows a change, and reference-positive cells with a small new-footprint area.
- Per-AOI ΔF1 plotted against usable panchromatic months. This is descriptive only, because cloudiness is confounded with season and terrain (Q4.3).
- Sensor-specific lag distributions.
- Pipeline ΔF1 on the full grid.

**Plausible data and arms.** Shared design (§3).
1. SAR-only agent.
2. SAR+pan agent (the same arm as Q-A's agent).
3. SAR-only and SAR+pan pipelines on all cells of the test AOIs.
4. Tools-disabled control.

Both agent arms use the same sampled cells, so the comparison is paired.

**Plausible method.** Follow Q-A's steps 1–6 with the arms above. The SAR-only agent gets the same prompt without the panchromatic tool descriptions. The pipeline's fusion rule is tuned on development AOIs. The panchromatic tool's standalone F1 is reported, to separate tool quality from the agent's use of it.

**Main threat to validity: panchromatic radiometric quality and the shared optical modality.**
- **Pseudo-change.** MuRA-T provides Level-1 Collection 1 data with one least-cloudy scene per month, which can create pseudo-change from illumination and season (X8). Qu et al. (2026) show that illumination-induced misalignment creates pseudo-change. If so, ΔF1 measures normalisation quality, not information content. Mitigation: fix the normalisation on development AOIs and report the tool's standalone F1.
- **Shared optical modality.** The reference is traced on optical Planet RGB imagery. Panchromatic data and the reference share optical failure modes, and both record visibility rather than structure. *Inference:* panchromatic may look useful partly because it sees what the annotator saw (as in Q2.3).
- **Prompt asymmetry.** The two agent arms differ in prompt length and tool menu, so ΔF1 also includes how the agent behaves with one tool versus two. H-B4 (the pipeline) gives an agent-free estimate.

**What would weaken or refute it.**
- If the ΔF1 CI includes 0 or is negative, panchromatic adds nothing, or does harm, at 100 m for this agent. That is reportable, and it answers the project's own framing directly (H1).
- A gain in the pipeline but not in the agent means the agent fails to exploit panchromatic.
- A gain only in recall, not in precision, refutes H-B2.
- If the panchromatic tool's standalone F1 is near chance, the tool is the bottleneck, not the agent.

**What changed from the previous version (RQ4), and why.**
- **Origin.** Q-B comes from RQ4 (adaptive panchromatic/SAR selection under cloud). RQ4 was rejected as a standalone question because its main effect was predictable by design, since SAR fills cloud gaps (Q4.1). H1 changed it into a required SAR-only vs SAR+pan secondary analysis.
- **Direction reversed.** RQ4 asked whether SAR rescues panchromatic. Q-B asks whether panchromatic adds anything to SAR. *Inference:* the design does not fix this outcome, because 15 m Level-1 panchromatic data may add only noise.
- **Removed.** Adaptive selection and the cost non-inferiority test (H4b) are dropped (H1, Q4.2). The cloud moderator becomes descriptive only (Q4.3).
- **Elevated to primary.** H1 states that "the paper must show whether panchromatic adds anything". Making this the primary question would **replace H1's primary endpoint** (presence-F1 non-inferiority) and needs explicit human approval.

**Criteria evaluation.**
1. **Importance:** H for this project, because it tests the human's sensor framing; M for the general agentic-GeoAI question.
2. **Novelty (M, supplied evidence only).**
   - Lee et al. use SAR only.
   - Michel & Inglada fuse Landsat-8/9 with Sentinel-2, not with SAR.
   - Kao et al.'s main-source table lists no SAR instrument.
   - Earth-Bench lists spectrum, product and RGB modalities.

   I found no supplied paper that tests 15 m panchromatic + Sentinel-1 for new buildings. This is "not found in our search", not a novelty claim.
3. **Testability (H).**
4. **Data feasibility (H).**
5. **Spatial relevance (H).** Side-looking vs near-nadir geometry; 15 m pixels inside 100 m cells.
6. **Tractability (H).** One extra agent arm; the pipeline arms cost no API calls.
7. **Validation (M–H).** The optical–optical correlation with the reference is the weak point.

---

## 7. Q-C (Rank 3): Does neighbourhood context let an agent attribute change to the right cell?

**Research question.** In held-out SpaceNet 7 AOIs, give a tool-using LLM agent a neighbourhood tool. The tool returns the same SAR and panchromatic change summaries for the eight cells around the queried 100 m cell, labelled by relative position and by whether each cell lies toward or away from the radar. Does this improve the agent's presence-F1 for new-building cells, compared with the same agent limited to the queried cell? And is any gain due to spatial adjacency, rather than to having more context in the prompt?

**Candidate hypotheses.**
- **H-C1 (primary).** ΔF1 = F1(agent + adjacent context) − F1(agent, cell only) > 0, meaning the lower bound of the AOI-cluster CI is above 0.
- **H-C2 (identification control).** F1(agent + adjacent context) > F1(agent + placebo context). The placebo arm receives eight *non-adjacent* cells from the same AOI, in the same summary format and with the same token count. This separates spatial information from "more numbers in the prompt".
- **H-C3 (mechanism, secondary).** Gains concentrate in two subsets, defined in advance:
  - (i) reference-negative cells on the look-direction side of reference-positive cells, where layover moves building signal into the neighbour (X5; Hou et al., 2026). Context should give *fewer false positives* here.
  - (ii) reference-positive cells with a small new-footprint area next to cells with a strong change, which is what multi-cell construction sites look like. Context should give *more true positives* here.
- **H-C4 (secondary).** A fixed spatial rule tuned on development AOIs, such as attribution along the look direction plus a 3 × 3 majority, achieves the same gain. If so, spatial context matters but the agent is not needed to use it.

**Expected observable evidence.**
- ΔF1 for adjacent vs cell-only context and for adjacent vs placebo context, with CIs.
- Changes in false positives and true positives within the two H-C3 subsets.
- Trajectories showing whether the agent calls and cites the neighbour tool.
- F1 of the spatial-rule pipeline.
- Results by orbit direction and incidence angle (descriptive).

**Plausible data and arms.** The shared design (§3), plus one tool. The neighbour summaries are built from the existing per-cell tools and contain no labels.
1. Cell-only agent (Q-A's agent arm).
2. Agent with adjacent context.
3. Agent with placebo context (on a subsample if the budget cap binds).
4. Spatial-rule pipeline on all cells.

**Plausible method.**
- Follow Q-A's steps 1–6, and also define the look direction per AOI from orbit metadata.
- Define the H-C3 subsets from the reference geometry, for scoring only. They are never shown to the agent.
- Limit each neighbour summary to a change month and a statistic, to keep token counts bounded.
- Report results under both strict scoring and H1's one-neighbour look-direction tolerance, because the tolerance forgives exactly the displacement that context is meant to fix.

**Main threat to validity: spatial over-smoothing, and interaction between scoring and context.**
- An agent told that its neighbours changed may answer "yes" for negative cells next to construction. Recall and false positives would then rise together, so ΔF1 could hide two opposite effects. Report precision and recall separately.
- Sampled cells can be each other's neighbours. The agent sees the neighbours' *tool outputs*, not their labels, so this is not label leakage. AOI-level clustering handles the dependence.
- The effect may be small at 100 m if layover from typical new buildings rarely crosses cell edges [citation needed]. The building heights in the SpaceNet 7 AOIs are unknown.

**What would weaken or refute it.**
- If the H-C1 CI includes 0, context does not help.
- If H-C2 fails, the gain comes from context length, not adjacency.
- If the gains do not concentrate in the H-C3 subsets, the proposed mechanism is unsupported.
- If the spatial rule (H-C4) matches the agent, the gain is spatial but not agentic.

**What changed from the previous version, and why.**
- **New question.** The third option could not be drawn from the earlier candidates. RQ2 was deferred and its abstention test folded into Q-A, RQ3 was rejected, and the VLM contrast was dropped (all in H1). N1 asks for three genuinely different options.
- **Where it comes from.** The previous RQ1's spatial notes (a DEM layover mask) and the critic's X5: a terrain DEM does not contain buildings, so it cannot mask building-induced layover, and the signal moves into neighbouring cells. H1 accepted X5 as a scoring sensitivity check. Q-C turns it into a testable hypothesis about whether an agent can reason about the displacement.
- **H1 constraints kept.** The one-cell query unit at 100 m, opaque IDs and the whole-AOI split.

**Criteria evaluation.**
1. **Importance (M–H).** Spatial reasoning is the "Geo" in GeoAI. The supplied agent benchmarks (Feng et al., 2026; Kao et al., 2026) do not visibly test neighbourhood reasoning over SAR series.
2. **Novelty (M, supplied evidence only; no claim).**
3. **Testability (H).** The placebo arm provides identification.
4. **Data feasibility (H).** No new data is needed.
5. **Spatial relevance (H).** Adjacency, look direction and MAUP.
6. **Tractability (M).** One more tool and two more agent arms: the highest API cost of the three.
7. **Validation (H).**

---

## 8. Disposition of the previous candidates

| Previous | H1 decision | Where it went |
|---|---|---|
| RQ1 | Revised (RQ1-R accepted) | Became **Q-A** |
| RQ2 (verification loop) | Deferred | Its abstention test became H-A3. The verification loop is not re-proposed, because it mostly repeats the agent-vs-pipeline estimand and adds little beyond Zuo et al. (2026) |
| RQ3 (transfer of change types) | Rejected | Not re-proposed. Lee et al.'s Gamma-LRT framework is used only as a tool |
| RQ4 (adaptive sensor selection) | Changed | SAR-only vs SAR+pan is a secondary analysis in Q-A and the primary contrast in **Q-B**. Adaptive selection is dropped |
| Direct-VLM arm | Dropped entirely | Limitation paragraph only (Q-A, method step 7) |
| Archive-size factor | Rejected | Not re-proposed in any form |
| Hand labelling; NAIP | Rejected | SpaceNet 7 labels only |

---

## 9. Unresolved issues and missing inputs

1. **H1 is unreviewed.** Justin has not reviewed the H1 rows, and every option depends on them.
2. **No data inventory.** None of the following is known yet: MuRA-T download success, Sentinel-1 scene counts per track in each AOI's label window, usable panchromatic months, counts of new-building cells, and onset-month distributions.
3. **Power is unknown.** It depends on the number of test AOIs. With few clusters, bootstrap CIs may be unreliable [citation needed].
4. **Unset parameters.** δ, the borderline band, the abstention threshold, A_min, the sample allocation and the API cap are all still to be set by the human.
5. **Grid CRS unverified.** The Web-Mercator inference about the SpaceNet 7 grid (§3.2) needs checking [citation needed].
6. **Panchromatic normalisation.** No method has been chosen [citation needed].
7. **Backbone and budget.** The LLM backbone and the API budget are unknown.
8. **Endpoint change.** Choosing Q-B or Q-C changes H1's primary endpoint and needs explicit approval.
9. **Truncated evidence.** Results sections are unseen, for example Zuo et al.'s results, Kao et al.'s results by category, and Lee et al.'s methods after the change criterion matrix.
10. **Target journal unspecified.** It matters whether a non-inferiority or negative result is in scope.
11. **No wider search.** Nothing was searched beyond the ten supplied papers, so there are no novelty claims. The panchromatic gap is worded as "not found in our search" (H1).
12. **Licences [to verify].** SpaceNet 7 is CC BY-SA 4.0 and MuRA-T is GPL v3 (form). Check the share-alike terms before redistributing derived cell labels or rasters.

## 10. Suggested next scientific action

1. **Human decision (W1).** Justin reviews H1, chooses Q-A, Q-B or Q-C, approves or edits the switch rule (§4), and sets δ, the band, the abstention threshold, A_min and the API cap.
2. **Feasibility check (1–2 days).**
   - Download MuRA-T and SpaceNet 7 for the candidate AOIs.
   - Count Sentinel-1 scenes per track within each AOI's label window, and usable panchromatic months per AOI.
   - Rasterise the labels to 100 m cells, then count new-building cells and onset months.
   - Confirm the grid CRS.
   - Apply the pre-registered AOI selection rule and the development/test split.
3. **Pilot (W3).** Build the tools on two development AOIs and run the 20-cell pilot: agreement rate, conflict-stratum size, parse rate and tokens per query. Apply the switch rule.
4. **Pre-registration.** Write it to `outputs/`, covering the endpoint, margins, strata, allocation, cap and robustness checks, before any test-AOI run. Then pass it to the next stage.

## 11. References cited (human-verified list L1)

- Feng, P., Lv, Z., Ye, J., Wang, X., Huo, X., Yu, J., Xu, W., Zhang, W., Bai, L., He, C., & Li, W. (2026). Earth-Agent: Unlocking the full landscape of earth observation with agents. International Conference on Learning Representations (ICLR 2026). OpenReview: dkIXAbWuxO
- Hou, Y., Wu, H., Zhang, Y., Liu, X., Ren, C., Lu, W., Yu, H., Huang, Y., Diao, W., Wang, Y., Li, Y., Han, B., & Sun, X. (2026). SAR foundation models: A comprehensive review of data, models, and applications. Science China Information Sciences, 69(8), 180301. DOI: 10.1007/s11432-026-5040-3
- Irvin, J. A., Liu, E. R., Chen, J. C., Dormoy, I., Kim, J., Khanna, S., Zheng, Z., & Ermon, S. (2025). TEOChat: A large vision-language assistant for temporal earth observation data. International Conference on Learning Representations (ICLR 2025). OpenReview: pZz0nOroGv
- Kao, C.-H., Zhao, W., Lam, C., Umap, A., Revankar, S., Speas, S., Bhagat, S., Datta, R., Phoo, C. P., Mall, U., Vondrick, C., Bala, K., & Hariharan, B. (2026). Towards LLM agents for earth observation. Findings of the Association for Computational Linguistics: ACL 2026, 2597–2611. DOI: 10.18653/v1/2026.findings-acl.124
- Lee, B., Lee, Y.-K., & Kim, S.-W. (2026). Change type analysis for urban construction using time-series SAR data. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing (early access). DOI: 10.1109/JSTARS.2026.3737141
- Michel, J., & Inglada, J. (2026). Temporal attention multi-resolution fusion of satellite image time-series, applied to Landsat-8/9 and Sentinel-2: All bands, any time, at best spatial resolution. Remote Sensing of Environment, 334, 115159. DOI: 10.1016/j.rse.2025.115159
- Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. Remote Sensing of Environment, 334, 115239. DOI: 10.1016/j.rse.2026.115239
- Soni, S., Dudhane, A., Debary, H., Fiaz, M., Munir, M. A., Danish, M. S., Fraccaro, P., Watson, C. D., Klein, L. J., Khan, F. S., & Khan, S. (2025). EarthDial: Turning multi-sensory earth observations to interactive dialogues. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 14303–14313. DOI: 10.1109/CVPR52734.2025.01334
- Xuan, W., Wang, J., Qi, H., Chen, Z., Zheng, Z., Zhong, Y., Xia, J., & Yokoya, N. (2025). DynamicVL: Benchmarking multimodal large language models for dynamic city understanding. Advances in Neural Information Processing Systems 38 (Datasets and Benchmarks Track), 37321–37339. DOI: 10.52202/085713-1114
- Zuo, L., Sun, J., Li, J., Liu, F., Li, J., & Niu, G. (2026). Hallucination-resistant change detection in multimodal large models for autonomous land management agents. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 19, 6313–6327. DOI: 10.1109/JSTARS.2026.3656403

Data sources named in the form and not cited as references: MuRA-T (an arXiv preprint, not peer-reviewed), SpaceNet 7 / MUDS (AWS Open Data) and Sentinel-1 GRD (Earth Engine `COPERNICUS/S1_GRD`).

**[citation needed] items:** pseudo-invariant relative radiometric normalisation; the SpaceNet 7 grid CRS and the Web-Mercator inference; cluster-bootstrap coverage with few clusters; typical Sentinel-1 layover extent for new buildings; the Landsat-8 band 8 specification beyond what the form states.
