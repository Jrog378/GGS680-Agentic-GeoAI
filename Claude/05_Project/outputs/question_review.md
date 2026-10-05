# Stage 2 (revision): Scientific Critic: Review of the Three Refined Questions (Q-A, Q-B, Q-C)

- **Source packet:** `outputs/prompt_packets/02_scientific_critic.md` (generated 2026-10-04 22:32)
- **Item reviewed:** `outputs/research_questions.md` (Stage 1 revision: Q-A, Q-B, Q-C)
- **Revises:** `outputs/history/question_review__20261004-223227.md` (review of RQ1–RQ4, verdict REVISE)
- **Status:** Review only. Nothing here is a result. No novelty, causal, policy or external-validity claim is made, and none can be made without human approval (AGENTS.md rule 9).
- **Note on agreement:** Stage 1, the H1 decision log and this review are all LLM outputs. H1 was drafted by Claude Code and Justin has not reviewed it yet. Where they agree, that is not independent validation (rule 4).

---

## 0. Summary

| ID | Verdict | Main reason |
|---|---|---|
| Q-A | **REVISE** (recommended once revised; see §7) | It has the right target and a clean paired design. But both arms get the same inputs, so as written it compares an LLM's decision rule with one hand-tuned rule rather than testing "agency". The non-inferiority primary has no stated rationale, and the primary F1 depends on how the sample is allocated |
| Q-B | **REVISE** (keep as a secondary analysis of Q-A, not as the primary) | The sensor question does not need the agent: the pipeline answers it on every cell at no API cost. Making the agent's estimate primary puts the noisier estimate first and mixes sensor value with prompt and tool-menu effects. A shared optical modality and sensor-specific lags bias ΔF1 |
| Q-C | **REJECT** for this 8-week paper (defer to a follow-on) | It is well identified, thanks to the placebo arm. But the proposed layover mechanism is probably too small to matter at 100 m for typical new buildings, building heights are unknown, and it is the most expensive option (three agent arms and a new tool) |

**Single most serious issue (QA.1 with QA.2).** In Q-A the agent and the pipeline receive identical, deterministic tool outputs for one fixed question that five tools cover. The contrast therefore isolates the LLM's *decision rule over the same numbers*, not planning or tool choice. The comparator is a single hand-tuned fusion rule, which does not use the full per-cell series that the agent sees.
- A positive H-A2 could be matched by a better non-agentic rule over the same tool outputs.
- A positive H-A1 is consistent with the agent simply passing tool outputs through.
- A non-inferiority primary assumes the new method brings a compensating benefit, and none is measured. The agent costs more, is stochastic and depends on one backbone, and its claimed flexibility is never used.

As written, even a perfectly run Q-A would not show what agentic GeoAI adds. This is fixable without new data (§7): add an information-matched non-agentic comparator, pre-register trajectory-diversity reporting, and either justify δ or switch to an estimation framing. These changes touch H1 rows, so Justin must approve them.

**What has improved.** H1 and Stage 1 resolve most of the earlier blocking and major issues. There is now an independent monthly reference, an AOI-level split with cluster inference, one primary endpoint, opaque IDs and a layover sensitivity check, and the VLM and archive-size arms are gone (§11).

---

## 1. Inputs used

| Input | Used for | Caveat |
|---|---|---|
| AGENTS.md rules and Scientific Critic role (packet) | Review criteria and output schema | None |
| Form A1–A3 and human notes | Boundary conditions and data plan: MuRA-T Landsat-8 band 8, SpaceNet 7 / MUDS labels, Sentinel-1 GRD, 10–20 AOIs, whole-AOI hold-out | Nothing has been downloaded. Per-AOI Sentinel-1 coverage is "TO VERIFY" |
| H1 decision log (20 rows) | Constraints, treated as binding | Drafted by Claude Code; not yet reviewed by Justin |
| `outputs/research_questions.md` (Stage 1 revision) | The object of review | LLM output |
| Previous review (history file) | Baseline and issue tracking (§11) | LLM output |
| L1 references (10, all human-verified) and the evidence text | Spot-checks (§3) and evidence for the issues | Each paper is cut off at 20,000 characters, so results and appendices are mostly unseen |

## 2. Assumptions of this review

- **R-A1.** Feasibility is judged against the form's boundary: a paper *submittable* within 8 weeks, by one researcher using AI-assisted coding, with an unknown API budget.
- **R-A2.** H1 rows are treated as binding, as Stage 1 did. Where I recommend changing one, I say so, and the change needs Justin's approval.
- **R-A3.** Domain knowledge that is not in the supplied evidence is labelled *inference* and marked [citation needed].
- **R-A4.** Statements about the papers refer only to their visible, truncated text.
- **R-A5.** I review Q-A, Q-B and Q-C as written. I do not silently replace any of them. §7 proposes a revised Q-A for approval.

---

## 3. Spot-check of Stage 1's use of the evidence

| Stage 1 statement | What the visible evidence shows | Assessment |
|---|---|---|
| Kao et al.: about 60% with reflexion on yes/no questions, "marginally above random chance". Xuan et al.: best DVL-Bench QA accuracy 34.1% | Both match | Accurate. But these numbers come from code-generating agents and VLMs, not curated-tool agents reading numbers. They motivate Q-A but do not predict its effect size |
| MUDS: 60 AOIs, about 4.77 m, 1024 × 1024 pixels, 24 months, 17–24 usable frames (Qu et al.) | Matches. Qu et al. describe per-time-point **building / non-building** labels | Accurate. Per-building IDs, which Q-A needs to date onsets, come from the form, not from Qu et al. Verify them at download |
| SAR tool: "a Gamma likelihood-ratio change test returning candidate change months … (the LRT framework in Lee et al., 2026)" | Lee et al. compute pairwise LRTs between time points to build a change criterion matrix for spectral clustering, after DespecKS filtering. No thresholded change-month detector or false-alarm calibration is visible | **Overstated.** The change-month tool is a new adaptation, not a reuse (X13) |
| Lee et al.: impulse changes come from temporary infrastructure and moving objects. Hou et al.: layover from side-looking geometry | Both match | Accurate |
| Raw band 8, not pan-sharpened, because Michel & Inglada call the scale-invariance hypothesis unrealistic | Their critique concerns *training* band-sharpening models with Wald's protocol | **Weak justification.** It does not show that pan-sharpening harms change detection. The choice itself is defensible on simplicity grounds |
| Q-B gap: Michel & Inglada fuse Landsat with Sentinel-2, not SAR; no supplied paper tests 15 m panchromatic + Sentinel-1 | True as stated. But Hou et al. treat SAR–optical synergy as an established multimodal paradigm, and Michel & Inglada cite work that conditions Sentinel-2 reconstruction on Sentinel-1 | **Gap overstated** (QB.3) |
| Kao et al. used an LLM to classify failures; this study uses fixed rules | Matches ("prompt Gemini-2.5-Flash to classify failures") | Accurate. The previous omission is fixed |
| Earth-Agent: ReAct loop and dual-level (trajectory and answer) evaluation | Matches. Feng et al.'s case for agents rests on multi-step choice among 104 tools across modalities | Accurate. This contrast with Q-A's five-tool, single-template setting matters (QA.1) |
| A5: AOI about 4.9 km, about 2,400 cells of 100 m | Correct at the nominal pixel size | Correct, but if the grid is Web Mercator (§3.2 of Stage 1), the ground footprint shrinks by cos(latitude). At 40° that is about 3.7 km and about 1,400 cells (inference) |

---

## 4. Scores (1 = poor, 5 = strong)

Novelty is judged **only against the 10 supplied papers**. No literature search was done. The scores are my judgements, and the Q-A-R row is a projection (inference).

| ID | Importance | Novelty / evidence gap | Testability | Identification strategy | Data adequacy | Spatial validity | Robustness / validation | Feasibility (8 wk) |
|---|---|---|---|---|---|---|---|---|
| Q-A (as written) | 4 | 3 | 4 | **3** | 3 | 3 | **3** | 4 |
| Q-B (as primary) | 3 | **2** | 4 | **2** | 3 | 3 | 3 | 4 |
| Q-C | 3 | 3 | 3 | 4 | **2** | 4 | 3 | **2** |
| Q-A-R (§7; projected) | 4 | 3 | 4 | 4 | 3 | 3 | 4 | 4 |
| *Previous RQ1-R projection, for comparison* | *4* | *3* | *4* | *3* | *3–4* | *3* | *4* | *3* |

Notes on the scores:
- **Feasibility rose** relative to the previous RQ1-R, because the reference now exists and no labelling is needed. It is still conditional on the W1 inventory (§9).
- **Data adequacy stays at 3.** The reference is strong, but Sentinel-1 coverage in 2017–2018 is unverified, and the panchromatic series is Level-1 with one scene per month.
- **Importance:** Hou et al. (2026) list multimodal SAR agents as a future direction, which supports Q-A's importance.

---

## 5. Issues

Numbering continues from the previous review (X1–X10), so the trajectory can be audited. Issues specific to one question are labelled QA, QB or QC.

### 5.1 Cross-cutting issues

#### X11. The primary F1 depends on the sampling allocation
- **ISSUE:** The sample is about 60 cells per test AOI, stratified on reference status (new / existing built / never built) and on tool-output status, with fixed allocations. The conflict stratum is also oversampled for H-A2. The primary F1 (H-A1, H-B1, H-C1) is computed on this sample; population F1 is only secondary.
- **LOCATION / TARGET:** Stage 1 §3.7 and §3.5 ("near chance"); H-A1, H-A2, H-B1, H-C1.
- **SEVERITY:** major
- **WHY IT MATTERS:** *Inference (standard metric properties [citation needed]):*
  - Precision, and so F1, changes with the share of positives in the scored set. Under a chosen allocation, F1 and any margin δ on it describe the design, not the AOIs.
  - Always answering "yes" scores F1 = 2p/(1+p) for a positive share p, which is 0.5 at p = 1/3. So "near chance" is undefined for F1.
  - Oversampling the conflict stratum shifts the primary F1 again.
  - F1 pooled across AOIs is dominated by the AOIs with the most positives.
  - H-A1 uses F1 while H-A2 uses balanced accuracy.
- **EVIDENCE NEEDED:** None beyond the design.
- **RECOMMENDED ACTION:**
  - Weight the primary estimate by inverse inclusion probability, or pre-register a prevalence-free primary (sensitivity and specificity, or balanced accuracy) with weighted F1 as secondary.
  - Keep the conflict oversample as a separate scored set, or weight it.
  - Pre-specify whether F1 is pooled across AOIs or averaged per AOI.
  - Report the trivial baselines for every scored set.

#### X12. Window edges and sensor-specific lags are scored as errors
- **ISSUE:** A positive cell is one where a footprint appears between the first usable label month and the end of a window of about 24 months. Some changes are visible to the tools but not to the reference: clearing that starts before month 1, and structures that go up late but are not labelled by the end of the window.
- **LOCATION / TARGET:** Stage 1 §3.3 (positive cell, onset, lag); H-A1, H-B1, H-B3.
- **SEVERITY:** major for Q-B; minor for Q-A
- **WHY IT MATTERS:**
  - *Evidence:* Lee et al. separate down-steps (land clearing) from up-steps (construction), so SAR records phases that come before a footprint. The form notes that labels mark visibility, which is closer to completion. Qu et al. report 17–24 usable frames, so some label months are missing.
  - *Inference:* edge cells produce systematic false positives and misses. In Q-A both arms share the tools, so much of this cancels in the paired contrast. In Q-B the arms differ in sensor, and each sensor has its own lag (H-B3), so the censoring enters ΔF1 directly.
- **EVIDENCE NEEDED:** Lag distributions per sensor on development AOIs, and the number of reference onsets in the first and last *k* months.
- **RECOMMENDED ACTION:**
  - Restrict the tool series to the label window.
  - Pre-register guard bands: score presence on cells whose reference onset, if any, falls in the interior of the window, and report edge-onset cells as a separate stratum.
  - Fix *k* on development AOIs, with a sensitivity check at k = 0, 1 and 2 months.

#### X13. The core change tool is a new, unvalidated adaptation
- **ISSUE:** Every arm of every question depends on a SAR change-month tool that Stage 1 attributes to Lee et al. (§3).
- **LOCATION / TARGET:** Stage 1 §3.4; all arms.
- **SEVERITY:** major
- **WHY IT MATTERS:**
  - *Evidence:* Lee et al.'s visible method builds a pairwise LRT matrix for spectral clustering. Their F1 = 0.94 measures agreement with expert readings of the same SAR series, so it is no evidence for a change-month detector.
  - *Inference [citation needed]:* the change-month logic, its threshold, the equivalent-number-of-looks assumption for 10 m GRD, and multiple testing across about 24 months are all new design choices. A weak tool pulls every contrast toward zero and fills the conflict stratum with noise.
- **EVIDENCE NEEDED:** The tool's standalone F1 and onset error on development AOIs.
- **RECOMMENDED ACTION:**
  - Specify the test fully in the pre-registration and describe it as "adapted from" Lee et al.
  - Report the standalone performance of the SAR and panchromatic tools on development AOIs before freezing.
  - Pre-register a simpler fallback statistic in case the tool fails validation by the end of W2.

#### X14. So far, every decision in the chain is LLM-generated
- **ISSUE:** Claude Code drafted H1 and Justin has not reviewed it. Stage 1 treated H1 as binding, and this review responds to both.
- **LOCATION / TARGET:** H1; Stage 1 A1; this review.
- **SEVERITY:** blocking (for pre-registration only)
- **WHY IT MATTERS:**
  - The H1 rows that fix the primary endpoint, drop the VLM arm and select MuRA-T/MUDS shape every question.
  - Agreement among LLM outputs is not validation (rule 4).
  - Several recommendations here (QA.1, QA.2) would change H1 rows.
- **EVIDENCE NEEDED:** Justin's review of H1.
- **RECOMMENDED ACTION:** Justin reviews H1 and the changes proposed in §7 before any pre-registration is written.

#### X15. The pilot is too small to drive the switch rule, and power is unknown
- **ISSUE:**
  - The switch rule tests an agent–pipeline disagreement rate against 5%, and a conflict-stratum count against about 10 per AOI. Both come from a 20-cell pilot on two development AOIs.
  - The same 4 development AOIs also tune the normalisation, thresholds, fusion rule and prompts.
- **LOCATION / TARGET:** Stage 1 §4 (switch rule) and §3.1 (split); Q-A method step 3.
- **SEVERITY:** major
- **WHY IT MATTERS:** *Inference:*
  - With 20 cells, one disagreement is 5%, so one or two cells decide the rule.
  - With 8–14 test clusters, the cluster bootstrap may be unreliable (Stage 1 flags this [citation needed]), and H-A2 rests on a few dozen discordant cells.
  - Tuning many choices on 4 AOIs risks overfitting them. Any shift between development and test AOIs affects the pipeline's fitted thresholds and the agent's prompt differently.
- **EVIDENCE NEEDED:** The disagreement rate and conflict-stratum size on all sampled development cells.
- **RECOMMENDED ACTION:**
  - Run the pilot on the full development sample, about 4 × 60 episodes.
  - Simulate power for H-A1 and H-A2 by resampling development AOIs, and set the minimum conflict-stratum size from that simulation.
  - Report how stable the pipeline thresholds are when each development AOI is left out in turn.

### 5.2 Q-A issues

#### QA.1. The contrast measures an LLM decision rule over fixed inputs, not agency (part of the most serious issue)
- **ISSUE:** Both arms receive the same deterministic tool outputs. The query is one fixed template, and five cheap tools fully cover it. The agent sees whole per-cell series, while the pipeline applies one fusion rule to summary outputs.
- **LOCATION / TARGET:** Q-A research question, arms 1–2, H-A1 and H-A2; "Main threat to validity".
- **SEVERITY:** major
- **WHY IT MATTERS:**
  - *Evidence:* Feng et al. (2026) argue the case for agents from multi-step choice among 104 tools across modalities, with trajectories evaluated alongside answers. Kao et al. (2026) argue that curated tool environments leave out the hard parts, such as choosing data and sensors.
  - *Inference:* if the agent calls all five tools in every episode, it is a zero-shot classifier over tool outputs. "Agentic" then names the system but explains nothing about the result.
  - *Inference:* an H-A2 gain could come from using more of the series than the pipeline does. A non-agentic rule over the same features could reproduce that, so a positive H-A2 would show that the pipeline was under-specified, not that agency helps. This is the strawman risk the previous review found in the VLM arm, one level down.
- **EVIDENCE NEEDED:** Trajectory diversity on development AOIs, and the performance of an information-matched rule.
- **RECOMMENDED ACTION:**
  1. **Add comparator P2.** P2 is a pre-specified, low-capacity rule or classifier, fitted on development AOIs to every feature the agent can see. This needs Justin's approval, because H1 says nothing is trained. The current pipeline is already fitted, so P2 extends it rather than adding a new kind of method.
  2. **Pre-register trajectory metrics:** the share of episodes that follow the most common tool sequence, and calls per episode. State that any claim about planning requires non-trivial variation.
  3. **Name the estimand plainly:** "LLM orchestration vs fixed rules, given identical tool outputs".

#### QA.2. The non-inferiority primary has no stated rationale
- **ISSUE:** H-A1 asks whether the agent loses no more than δ of F1. δ is unset and has nothing to anchor it.
- **LOCATION / TARGET:** H-A1; the H1 row "Pre-register one primary endpoint".
- **SEVERITY:** major
- **WHY IT MATTERS:** *Inference [citation needed]:*
  - A non-inferiority margin accepts a small loss of accuracy in exchange for a benefit the new method brings, such as lower cost or wider applicability. Here the agent costs more, is stochastic and depends on one pinned backbone.
  - The agent's claimed benefit is answering varied natural-language questions without re-engineering. That benefit is never exercised, because there is only one template.
  - Given the wrapper risk, H-A1 will probably pass and say little, and a reviewer can fairly ask why any loss should be accepted.
- **EVIDENCE NEEDED:** A measured benefit, or a decision to change the framing.
- **RECOMMENDED ACTION:** Choose one of these:
  - **(a) Estimation framing:** make the primary a two-sided estimate of weighted ΔF1 with its AOI-cluster CI, read against a pre-registered δ.
  - **(b) Justified non-inferiority:** keep non-inferiority, but justify δ from a benefit that is actually measured. For example, add a second pre-registered template that the agent answers without code changes. This costs more.

  Either way, use one metric family for H-A1 and H-A2 (X11). Both options change an H1 row and need Justin's approval.

#### QA.3. The abstention test (H-A3) measures prompt compliance and has no comparator
- **ISSUE:** Unanswerable queries are cells or months with no valid data, and the data-availability tool reports these directly.
- **LOCATION / TARGET:** H-A3.
- **SEVERITY:** minor
- **WHY IT MATTERS:** *Inference:*
  - Given that tool, a one-line rule abstains perfectly, so H-A3 cannot show any value from agency.
  - Sentinel-1 is all-weather (Hou et al., 2026) and rarely lacks data, so these queries have to be constructed.
  - The test still counts fabrications, which matter given Kao et al.'s C1/C2 failure categories.
- **RECOMMENDED ACTION:** Keep H-A3 as secondary and descriptive. Report a pipeline that applies an availability rule alongside it, and score unanswerable queries separately from the F1 sample.

#### QA.4. The tools-disabled control cannot detect leakage when IDs are opaque
- **ISSUE:** With opaque IDs and month indices, a tools-disabled agent has nothing to recall, so its answers just reflect the base rate the prompt implies.
- **LOCATION / TARGET:** Stage 1 §3.5; Q-A arm 3.
- **SEVERITY:** minor
- **WHY IT MATTERS:** *Inference:* the opaque-ID design already closes the main leakage route (X6), so this control mostly confirms that. The open question is whether answers depend on the queried cell's own evidence. In addition, F1 has no fixed chance level (X11).
- **RECOMMENDED ACTION:** Add an evidence-shuffled control, in which the agent gets the tool outputs of a different cell from the same stratum and AOI. Keep the tools-disabled control as optional, and report trivial baselines.

#### QA.5. Arms, cost and repeats are specified inconsistently
- **ISSUE:** §3.7 and §4 say Q-A needs one agent arm, but arm 4 adds a SAR-only agent. Stage 1 also does not say how the 3 repeats become one answer per cell.
- **LOCATION / TARGET:** Stage 1 §3.6 "Runs", §3.7, §4 item 4; Q-A arm 4.
- **SEVERITY:** minor
- **RECOMMENDED ACTION:** State the SAR-only agent's sample and cost. Pre-register the repeat rule (score each run and average, or take a majority vote), and report run-to-run agreement.

### 5.3 Q-B issues

#### QB.1. The sensor question does not need the agent
- **ISSUE:** H-B1 makes the agent's ΔF1 (SAR+pan vs SAR-only) the primary, and the pipeline's ΔF1 (H-B4) secondary.
- **LOCATION / TARGET:** Q-B H-B1 and H-B4; the switch rule in Stage 1 §4.
- **SEVERITY:** major
- **WHY IT MATTERS:** *Inference:*
  - The pipeline estimates the same sensor contrast on every cell of the test AOIs at no API cost. It covers far more cells and has no stochastic or prompt effects.
  - The agent's ΔF1 mixes sensor information with prompt length, tool-menu effects (which Stage 1 notes) and how well the agent uses each tool. A null could mean the agent failed; a gain could be a menu effect.
  - H1 requires that "the paper must show whether panchromatic adds anything". Q-A's secondary analysis already meets that requirement.
  - The switch rule promotes Q-B exactly when the agent behaves like the pipeline, which is when the agent's version of Q-B adds least.
- **RECOMMENDED ACTION:** Do not make Q-B the primary. If it is chosen anyway, make the pipeline's ΔF1 primary, and the agent's ΔF1 and the agent × sensor interaction secondary. Retarget the switch rule to match.

#### QB.2. A shared optical modality and sensor-specific lags bias ΔF1
- **ISSUE:** The reference is traced on optical imagery, panchromatic is optical, and the two sensors lag the label month by different amounts.
- **LOCATION / TARGET:** Q-B "Main threat to validity"; H-B2, H-B3.
- **SEVERITY:** major
- **WHY IT MATTERS:**
  - *Evidence:* the labels are traced on about 4 m Planet RGB imagery and mark when a building becomes visible (form). Qu et al. (2026) describe illumination-driven pseudo-change in optical series.
  - *Inference:* panchromatic and reference errors are probably correlated, for example through haze, illumination and bright bare soil. That inflates panchromatic's apparent value.
  - *Inference [citation needed]:* at 15 m, the clearest panchromatic signal may be land clearing, which comes before the label.
  - Window-edge censoring (X12) differs between the two sensors.
  - There is no second, non-optical reference in this design.
- **EVIDENCE NEEDED:** Lag distributions and standalone F1 for each sensor on development AOIs.
- **RECOMMENDED ACTION:**
  - Apply the X12 guard bands separately for each sensor.
  - Report ΔF1 separately for onsets in the interior of the window and onsets at the edges.
  - Describe the result as agreement with an optical footprint reference, not as information about buildings, and state this limitation.

#### QB.3. The evidence gap is narrower than stated
- **ISSUE:** Q-B's novelty rests on the fact that no supplied paper tests 15 m panchromatic together with Sentinel-1.
- **LOCATION / TARGET:** Q-B criteria item 2.
- **SEVERITY:** minor
- **WHY IT MATTERS:** *Evidence:* Hou et al. (2026) treat SAR–optical synergy as an established multimodal paradigm, and Michel & Inglada (2026) cite work that conditions Sentinel-2 reconstruction on Sentinel-1. *Inference:* the general question "does an optical channel add to SAR?" has prior answers [citation needed]. Only this sensor pair and the agent setting may be new.
- **RECOMMENDED ACTION:** Score novelty low until a wider search is done, and frame Q-B as a check on sensor value inside an agentic study.

### 5.4 Q-C issues

#### QC.1. The layover mechanism is probably too small at 100 m
- **ISSUE:** H-C3(i) assumes that layover moves building signal across cell edges.
- **LOCATION / TARGET:** Q-C H-C3(i); the third "Main threat" bullet.
- **SEVERITY:** major
- **WHY IT MATTERS:**
  - *Evidence:* Hou et al. (2026) describe layover and shadow caused by side-looking geometry, and their dependence on incidence angle.
  - *Inference [citation needed]:* the horizontal displacement grows with building height and incidence angle and is roughly the building's height at mid-range angles. For low-rise buildings that is one or two Sentinel-1 pixels, so only buildings that close to a cell edge spill over, which is a small share of a 100 m cell.
  - SpaceNet 7 provides footprints, not heights.
  - The more likely benefit of neighbourhood context is that development clusters in space, and the placebo arm separates that only partly.
- **EVIDENCE NEEDED:** The incidence-angle range, and a count on development AOIs of reference-negative cells that lie on the look-direction side of positive cells and show SAR change.
- **RECOMMENDED ACTION:** Add that count to the W1 inventory. If the subset is small, drop H-C3(i).

#### QC.2. Cost and scope exceed the eight-week envelope
- **ISSUE:** Q-C needs a new tool, two extra agent arms (adjacent and placebo), and about nine times the per-episode context for the neighbour summaries.
- **LOCATION / TARGET:** Q-C arms; Stage 1 §3.7.
- **SEVERITY:** major (for this paper)
- **WHY IT MATTERS:** *Inference:* Q-C has the highest API cost and the most new code. Its spatial claim can also be tested without the agent, using H-C4's rule.
- **RECOMMENDED ACTION:** Defer Q-C. Optionally, run the H-C4 spatial-rule pipeline inside Q-A as an exploratory analysis that costs no API calls.

#### QC.3. The placebo arm needs a minimum distance
- **ISSUE:** "Non-adjacent" cells can still lie inside the same multi-cell construction site.
- **LOCATION / TARGET:** H-C2.
- **SEVERITY:** minor
- **RECOMMENDED ACTION:** Draw placebo cells from beyond a pre-set distance, for example outside a 5 × 5 window (inference). Match token counts and format exactly.

---

## 6. Required checks

| Check | Q-A | Q-B | Q-C |
|---|---|---|---|
| What evidence would falsify the claim? | The refutation rules for H-A1–A3 are clear. But H-A1 is expected to pass under pass-through, and a better rule could match a positive H-A2 (QA.1, QA.2) | A ΔF1 CI that includes 0. But a null could reflect the agent rather than the sensor (QB.1) | The rules for H-C1 and H-C2 are clear. H-C3(i) may have too few cases to test (QC.1) |
| Is the spatial/temporal scale aligned? | Mostly. 100 m cells vs 10/15 m pixels is reasonable; the monthly reference sets the temporal resolution; the grid CRS is unverified (Stage 1 §3.2) | As Q-A. 15 m Level-1 panchromatic gives about 44 pixels per cell; the lags differ by sensor (X12) | Layover distance vs the 100 m cell is the crux (QC.1) |
| Could autocorrelation or leakage inflate performance? | The AOI hold-out and cluster bootstrap address spatial leakage, and opaque IDs address recall from memory. The residual risk is tuning on 4 development AOIs (X15) | Yes: the optical–optical correlation with the reference (QB.2) | Sampled cells can be each other's neighbours; AOI clustering handles this |
| Are causal claims justified? | A manipulation claim is justified for "the decision layer, given these tools", not for "agency" in general (QA.1) | Justified for the pipeline. In the agent, it is confounded with tool-menu effects | The placebo supports an adjacency claim; the mechanism claim is only associational |
| Does the evidence discriminate among alternative explanations? | Not between pass-through, reasoning and a better rule, unless P2 and trajectory metrics are added | Not between sensor information, how the agent uses it, and optical correlation, unless the pipeline is primary and scoring is lag-aware | Adjacency vs context length: yes. Layover vs clustering: only weakly |
| Is a second dataset or independent benchmark available? | No. MUDS is the only reference (H1); DynamicEarthNet labels land cover | As Q-A, and no non-optical reference exists | As Q-A |
| Is the question answerable with the proposed data? | Presence: yes, if the inventory passes. Onset: to monthly resolution | Yes, with the optical-reference caveat | Uncertain without building heights |

---

## 7. Recommended question: Q-A-R (revised Q-A; requires Justin's approval)

This revises Q-A and does not silently replace it. The data, sensors, query unit, reference, split and agent definition are unchanged.

**Q-A-R.** In held-out SpaceNet 7 AOIs, an LLM agent chooses and reads predefined Sentinel-1 and Landsat-8 panchromatic tools for one 100 m cell. Both comparators receive the same tool outputs. The questions are:
- **(a)** How does its new-building presence accuracy differ from (P1) the tuned fusion rule and (P2) an information-matched non-agentic rule?
- **(b)** Is it more accurate where the tools conflict?
- **(c)** Does it abstain when the data cannot support an answer?

**Changes to pre-register.** Each change is tied to an issue.

| # | Change | Issue |
|---|---|---|
| 1 | Name the estimand as LLM orchestration given identical tool outputs | QA.1 |
| 2 | Use two comparators: P1, the tuned rule, and P2, an information-matched rule fitted on development AOIs | QA.1 (touches the H1 "nothing trained" row) |
| 3 | Make the primary endpoint weighted ΔF1 vs P1 with an AOI-cluster CI. Either keep non-inferiority with a justified δ, or use an estimation framing; Justin decides | QA.2, X11 (touches the H1 primary-endpoint row) |
| 4 | Score the primary sample and the conflict oversample separately. Add prevalence-free secondary metrics and trivial baselines | X11 |
| 5 | Add guard bands at the window edges, fixed on development AOIs | X12 |
| 6 | Validate the SAR and panchromatic tools standalone, and pre-register a fallback change statistic | X13 |
| 7 | Add an evidence-shuffled control; the tools-disabled control becomes optional | QA.4 |
| 8 | Report trajectory diversity, and make claims about planning conditional on it | QA.1 |
| 9 | Run the pilot on the full development sample, simulate power, and retarget the switch rule to a pipeline-primary Q-B | X15, QB.1 |
| 10 | Answer the panchromatic question (H1's required secondary) with the pipeline, SAR-only vs SAR+pan on all test cells. Run the SAR-only agent on a subsample; the agent × sensor interaction is exploratory | QB.1, QB.2 |
| 11 | Optionally, run H-C4's look-direction / 3 × 3 rule as an exploratory pipeline analysis | QC.2 |

**Feasibility.** P2 and all pipeline analyses cost no API calls; the extra work is about 1–2 days in W2–W3 (inference). The critical path is W2: Sentinel-1 export and co-registration for 10–20 AOIs, panchromatic normalisation, and the change tool. If the tool fails validation by the end of W2, use the fallback and record the switch.

**What Q-A-R still cannot claim without human approval:**
- novelty (no search beyond the 10 papers);
- generality across LLM backbones or tool environments;
- validity beyond the selected AOIs, which are chosen for many new buildings and good Sentinel-1 coverage.

---

## 8. Unresolved issues

1. **H1 is unreviewed** (X14).
2. **No data inventory yet.** Still unknown:
   - whether MuRA-T downloads successfully;
   - Sentinel-1 scenes per track in each AOI's window, especially in 2017 outside Europe [citation needed];
   - usable panchromatic months;
   - counts of new-building cells and the onset distribution, including onsets near the window edges;
   - whether the labels carry per-building IDs.
3. **Grid CRS is unverified**, which affects the cell count and cell area (§3).
4. **Unset parameters:** the primary framing or δ, A_min, the guard band *k*, the borderline band, the abstention threshold, the allocation and the API cap.
5. **Methods not yet chosen:** the change-tool specification and the panchromatic normalisation method [citation needed].
6. **LLM backbone and API budget** are unknown.
7. **Target journal** is unspecified, which matters if the result is an estimation or negative result.
8. **Truncated evidence:** the rest of Lee et al.'s methods and results, Kao et al.'s results by category, and Feng et al.'s backbone comparisons are unseen.
9. **No wider literature search** (QB.3).

## 9. Suggested next scientific action (W1)

1. **Human decisions.** Justin reviews H1 and §7. He decides two things:
   - whether the primary stays non-inferiority (with a justified δ) or becomes an estimate (QA.2);
   - whether P2 is allowed under the H1 "nothing trained" row (QA.1).
2. **Feasibility inventory (1–2 days).** Follow Stage 1 §10, and add:
   - per-building IDs and missing label months;
   - the positions of onsets relative to the window edges (X12);
   - the QC.1 count, but only if Q-C is kept as a follow-on.
3. **Tool validation (W2).** Build the SAR and panchromatic tools, and report their standalone F1 and onset error on development AOIs (X13).
4. **Pilot (W3).** Run the full development sample through all arms (X15). Use it to simulate power, then set the minimum conflict-stratum size and the switch rule.
5. **Pre-registration.** Write it to `outputs/` with the items in §7 before any test-AOI run, then pass it to the next stage.

---

## 10. Verdict: **REVISE**

- **Q-A: REVISE** (recommended, in the revised form Q-A-R, §7)
- **Q-B: REVISE.** Keep it as Q-A's secondary analysis, with the pipeline estimate first. Do not make it the paper's primary.
- **Q-C: REJECT** for this 8-week paper; defer it to a follow-on

**Rationale.** Q-A is the right question for the broad problem, and H1 has removed the earlier blocking problems. The reference is independent and needs no labelling, inference is at the AOI level with whole-AOI hold-out, there is one primary endpoint, and the VLM and archive-size arms are gone. Its remaining weakness is construct validity. The agent and pipeline see identical tool outputs for one fixed question, so the contrast measures an LLM's decision rule against one hand-tuned rule. A positive superiority result could come from using more of the tool output, which a non-agentic rule could also do. A passing non-inferiority test is expected even if the agent only relays tool outputs, and non-inferiority has no rationale because the agent's compensating benefits are never measured. The primary F1 also depends on the sampling allocation, window-edge censoring adds systematic errors, the core SAR change tool is unvalidated, and a 20-cell pilot is too small to drive the switch rule. All of this can be fixed in the pre-registration without new data. Q-B asks a fair question, but the pipeline answers it better and at no API cost, and the agent version mixes sensor value with prompt effects and with the reference's optical bias. Q-C is well identified, but its physical premise is doubtful at 100 m, and its cost does not fit eight weeks. None of these judgements is validated by agreement with Stage 1 or H1, which are also LLM outputs. Every claim of novelty, causality or external validity still needs human approval.

---

## 11. What changed from the previous version

1. **Object of review.** This version reviews Q-A, Q-B and Q-C (the Stage 1 revision) instead of RQ1–RQ4. Sections 3–10 are rewritten for the new questions.
2. **Status of earlier issues** (via H1, pending Justin's review, and Stage 1):
   - **Resolved:** X1 (its process risk carries on as X14), X2, X4 (power remains open, X15), X7, Q1.1, Q1.2, Q1.6 and Q1.7.
   - **Adopted, with follow-ups:** X3 (extended by X12), X5 (Q-C builds on it; QC.1), X6 (the control is weak; QA.4), X8 (normalisation method still open), X9 (metric issue, X11), Q1.4 and Q1.5.
   - **Partly resolved:** Q1.3, by H-A2; taken further in QA.1 and QA.2.
   - **X10:** the references are now verified, but the evidence is still truncated.
   - **Closed by H1:** Q2.x, Q3.x and Q4.x.

3. **New issues:** X11–X15, QA.1–QA.5, QB.1–QB.3 and QC.1–QC.3.
4. **Scores updated.** The RQ1-R projection is replaced by Q-A-R. Feasibility rose from 3 to 4 because the reference now exists.
5. **Recommendation.** The core of the earlier recommendation is kept: agent vs pipeline, AOI-level inference and one primary endpoint. It now adds an information-matched comparator (P2), a decision on the primary framing, weighted metrics, guard bands, tool validation and a full-development pilot.
6. **Process caveat added.** Stage 1, H1 and this review are all LLM outputs (X14).
