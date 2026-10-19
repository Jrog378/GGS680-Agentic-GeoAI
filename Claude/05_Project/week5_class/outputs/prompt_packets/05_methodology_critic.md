# AGENT ROLE

# 🧪 Scientific Critic Agent

## Role
You are a skeptical scientific reviewer, not a copy editor.

## Goal
Challenge questions, hypotheses, methods, and claims using scientific criteria.

## Review dimensions
Score 1–5:
- importance;
- novelty/evidence gap;
- testability;
- identification strategy;
- data adequacy;
- spatial validity;
- robustness/validation;
- feasibility.

## Required checks
Ask:
- What evidence would falsify the claim?
- Is the spatial/temporal scale aligned with the question?
- Could spatial autocorrelation or leakage inflate performance?
- Are causal claims justified?
- Does the proposed evidence discriminate among alternative explanations?
- Is a second dataset or independent benchmark available?
- Is the question answerable with the proposed data?

## Output schema
For each issue:
- ISSUE
- LOCATION / TARGET
- SEVERITY: minor | major | blocking
- WHY IT MATTERS
- EVIDENCE NEEDED
- RECOMMENDED ACTION

End with: ACCEPT / REVISE / REJECT and a one-paragraph rationale.


# CURRENT TASK

Critique the methodology as a scientific reviewer, emphasizing spatial validity and falsifiability.

# CURRENT RESEARCH STATE / EVIDENCE

## FILE: outputs/methodology_v1.md

# Methodology v1

Source: prompt packet only. Gaps are marked MISSING EVIDENCE or TO VERIFY. The approved question is unchanged.

**Approved question:** In held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery and than non-agent baselines given the same tool outputs?

**Hypotheses.** H1: the agent has higher presence F1 score and lower fabrication rate than the VLM. H2: the agent's presence F1 is at least as high as the tuned and fitted rules (non-inferiority, AOI-cluster confidence interval) and higher where the tools disagree. Secondary: panchromatic-only vs panchromatic+SAR inputs, run for both the agent and the VLM.

## 1. Unit of analysis
A 100 m × 100 m cell. Each sampled cell is one question: a 1 km chip centred on it, cell outlined, 8 dates. The inference unit is the held-out AOI, because cells are clustered.

## 2. Study area and temporal scope
10–20 of the 60 SpaceNet 7 / MuRA-T AOIs, chosen by new-building count and Sentinel-1 coverage; about 24 monthly steps, 2017–2020. Before any modelling, AOIs are split into development AOIs (about one third: prompt design, rule tuning, fitted-rule training) and test AOIs (never overlapping). The 8 dates per AOI follow a fixed rule: evenly spaced across the window, each the nearest month with a clear MuRA-T scene and a Sentinel-1 acquisition.

## 3. Target variables
- **Presence:** 1 if newly covered footprint area in the cell (buildings first appearing after date 1, by date 8) is ≥ A_min. Primary A_min = 450 m² (two 15 m pixels), matching "development visible at 15 m resolution, not single houses". Cells with 0 < area < A_min are excluded from presence scoring and counted.
- **Onset:** the first of the 8 dates at which cumulative new area reaches A_min.
- **Fabrication:** a claimed new-building cell with zero labelled new footprint area.

## 4. Input/predictor variables
Per date: Landsat-8 band 8 panchromatic chip (15 m pixels); Sentinel-1 VV, plus VH where available (10 m pixel spacing, about 20 m resolution); MuRA-T cloud mask. Tool outputs (agent and baselines only): panchromatic change score, SAR log-ratio change score, change-point date per sensor, optical availability flag, cross-sensor agreement flag.

## 5. Data provenance and resolution
| Data | Source | Resolution | Status |
|---|---|---|---|
| Landsat-8 band 8 | MuRA-T, Collection 1 L1TP, on SpaceNet 7 grid | 15 m resolution | preprint; sub-pixel alignment TO VERIFY |
| Sentinel-1 C-band GRD | Earth Engine `COPERNICUS/S1_GRD` or Planetary Computer `sentinel-1-rtc` | 10 m pixel spacing (about 20 m resolution) | scenes, orbit, polarisation per AOI TO VERIFY |
| Labels | SpaceNet 7 / MUDS, CC BY-SA 4.0 | traced on about 4 m Planet RGB | independent of both inputs |
| Fallback | Landsat 8/9 Collection 2 band 8, Level-1 | 15 m resolution | self co-registration |

## 6. Preprocessing
- **CRS:** the grid CRS is not stated in the packet (TO VERIFY). Cells, areas and distances are computed in the local UTM zone (metres, m²).
- **Panchromatic:** per-scene normalisation against stable pixels to remove sun-angle and seasonal shifts in Level-1 values; stable pixels are chosen without test labels.
- **SAR:** one orbit direction and polarisation per AOI; terrain correction, speckle filter, dB; monthly median if several scenes; co-registered to the MuRA-T grid.
- **Labels:** polygons rasterised to new area per cell, area-weighted where 15 m pixels straddle cell edges.
- **Chips:** one fixed rendering (stretch, outline) shared by agent and VLM.

## 7. Models
- **Tools** (deterministic, frozen before testing): the change scores, change-points and flags in Section 4.
- **Agent:** a pinned multimodal LLM that views the chips, calls the tools and returns presence, onset date and a justification citing tool output.
- **VLM:** the same pinned model where possible; same chips and question, no tools. Whether any VLM accepts SAR chips is MISSING EVIDENCE.
- Lowest available temperature; 3 repeated runs per cell; prompt fixed on development AOIs.

## 8. Baselines
- **Tuned rule:** presence if either change score exceeds thresholds tuned on development AOIs; onset = first date over threshold.
- **Fitted rule:** logistic regression on the same tool outputs, trained on development AOIs with leave-AOI-out cross-validation.
- **Floor:** majority class.

## 9. Spatial split and metrics
Whole-AOI holdout: no test-AOI cell informs prompts, thresholds or fitting. In each test AOI a seeded stratified sample (about 60 cells: labelled new with early or late onset, built-stable, never-built, tool-disagreement) is drawn; metrics use inverse-inclusion weights. Metrics: presence F1, precision and recall; precision–recall AUC for scored baselines; onset absolute error in months, exact-date agreement and share within ±1 month; fabrication rate (fabricated claims ÷ all positive claims). Differences carry 95% confidence intervals from an AOI-cluster bootstrap over test AOIs.

## 10. Uncertainty and sensitivity
- Run-to-run spread across the 3 runs, plus majority vote.
- A_min ∈ {225, 450, 900 m²}.
- Cell size 100 m vs 200 m, and a 50 m grid offset.
- Two prompt paraphrases.
- Strata: tool agreement, optical availability (clear vs cloudy/missing months), AOI.
- Secondary: panchromatic-only vs panchromatic+SAR for agent, VLM and baselines.

## 11. External validation
- **Label audit:** random labelled and claimed events per test AOI hand-checked on the about 4 m imagery; report label-audit disagreement rate.
- **Out-of-selection AOIs:** 3–5 non-selected SpaceNet 7 AOIs (low growth or weak Sentinel-1 coverage) scored with frozen prompts and rules.
- A second label source is MISSING EVIDENCE.

## 12. Decision criteria (pre-registered)
- **H1 supported** if the 95% confidence interval of agent − VLM presence F1 lies above 0 and that of fabrication rate lies below 0.
- **H2 supported** if the lower 95% confidence bound of agent − best-rule presence F1 is above −0.05 F1, and the difference is positive in the tool-disagreement stratum.
- **Refuted** if agent F1 ≤ VLM F1, or the fabrication gain comes only from a recall collapse.
- **Pivot:** MuRA-T unusable → fallback band 8; fewer than 10 AOIs with consistent Sentinel-1 → panchromatic primary; no VLM ingests SAR → SAR comparison on agent and baselines only.

## GeoAI checks
- **CRS/units:** UTM metres; areas in m².
- **Spatial autocorrelation:** neighbouring chips overlap; inference is AOI-level only.
- **Leakage:** AOI holdout; test labels unseen; tools use only the 8 supplied dates; pretrained models may have seen public SpaceNet 7 data (contamination unknown).
- **Scale mismatch:** about 4 m labels, 15 m pixels, about 20 m SAR resolution, 100 m cells; handled by A_min sensitivity.
- **MAUP:** cell-size and offset tests; no single-building claims.
- **Sampling bias:** AOIs chosen for growth and SAR coverage raise prevalence; checked with out-of-selection AOIs.
- **Transferability:** limited to SpaceNet 7-type sites, 2017–2020.

## Assumptions most likely to change the conclusion
1. A_min = 450 m² defines the positive class; another threshold could reverse rankings.
2. Some VLM accepts panchromatic and SAR chips (MISSING EVIDENCE); a weak VLM inflates H1.
3. 8 dates resolve onset only to about a 3-month step; "±1 month" may need re-reading as ±1 date step (to confirm).
4. MuRA-T alignment and Sentinel-1 consistency hold (TO VERIFY).
5. SpaceNet 7 labels are accurate; they mark visibility, not construction start.
6. 10–20 AOIs give enough power for AOI-cluster intervals.

## Eight-week work plan
| Week | Headline | Deliverable |
|---|---|---|
| 1 | Data access and AOI screening | MuRA-T and labels downloaded; Sentinel-1 inventory; AOIs selected; split frozen |
| 2 | Co-registration and label-to-cell rules | SAR on MuRA-T grid; cell grid; A_min and 8-date rule pre-registered |
| 3 | Tools and baselines | Frozen tools; tuned and fitted rules on development AOIs |
| 4 | Agent and VLM harness | Pinned models; prompts fixed; pilot on development AOIs |
| 5 | Held-out test runs | 3 runs per cell for all systems; label audit |
| 6 | Scoring and hypothesis tests | F1, onset error, fabrication rate; AOI-cluster intervals; strata |
| 7 | Sensitivity and external validation | Thresholds, MAUP, prompts, pan vs pan+SAR; out-of-selection AOIs |
| 8 | Write-up and submission | Manuscript, code and data statement submitted |


## FILE: outputs/research_questions.md

# Candidate Research Questions (Research Question Agent)

Source: `inputs/problem.md` and the human notes/references in the prompt packet only. No other evidence used. Novelty is **not** claimed for any candidate: the packet lists references but supplies no content from them, so overlap cannot be assessed (MISSING EVIDENCE).

Shared setup assumed by all candidates: Landsat-8 band 8 panchromatic at 15 m resolution (MuRA-T, ~24 monthly steps, 2017–2020), Sentinel-1 C-band GRD co-registered to the same grid, SpaceNet 7 / MUDS monthly building footprints as independent reference labels, 10–20 AOIs with whole AOIs held out for testing.

---

## Rank 1 — Does adding SAR to panchromatic imagery improve monthly detection of new buildings at 15 m resolution?

- **Research question:** In held-out AOIs, does fusing Sentinel-1 backscatter with Landsat-8 panchromatic time series at 15 m pixels detect newly appearing buildings (as dated by SpaceNet 7 first-appearance month) more accurately than panchromatic imagery alone?
- **Candidate hypothesis:** Pan+SAR fusion yields a higher F1 score for "new-building pixel/cell in month *t*" than pan-only, because SAR is unaffected by cloud gaps (missing MuRA-T months) and responds to built structure geometry.
- **Expected observable evidence:** Higher F1 (and higher recall at matched precision) for the fusion model across held-out AOIs; the gain concentrated in AOIs/months with missing or cloudy optical scenes.
- **Plausible data:** MuRA-T band 8 + cloud mask; Sentinel-1 GRD (VV/VH where available) from Earth Engine or Planetary Computer; SpaceNet 7 footprints rasterised to the 15 m grid as fraction of each pixel newly covered.
- **Plausible method:** Per-pixel or small-patch temporal classifier (e.g., gradient boosting or a light temporal CNN) trained on pan-only vs pan+SAR features; leave-AOI-out cross-validation; paired comparison per AOI.
- **Main threat to validity:** Scale mismatch — buildings traced on ~4 m imagery are often smaller than one 15 m pixel, so labels must be thresholded/aggregated, and the threshold choice can drive the result. Secondary: Sentinel-1 coverage varies by AOI (TO VERIFY), which could confound "SAR helps" with "SAR coverage is good here."
- **Weakening/refuting result:** No improvement in F1 for fusion over pan-only across held-out AOIs (paired test across AOIs not significant), or gains that vanish when restricted to months with clear optical scenes.
- **Criteria notes:** Importance high (all-weather monitoring); testability high; data feasibility moderate (SAR co-registration is unfinished work); spatial relevance high; tractable in eight weeks if AOI count stays near 10.

## Rank 2 — Does SAR backscatter change precede the labelled appearance of new buildings?

- **Research question:** For buildings first appearing in SpaceNet 7 in month *t*, does Sentinel-1 backscatter in the containing 15 m pixels change significantly in months before *t*, and by how many months?
- **Candidate hypothesis:** SAR backscatter change leads the SpaceNet 7 first-appearance month by at least one month on average, consistent with the packet's caveat that labels mark visibility (closer to completion) rather than construction start.
- **Expected observable evidence:** A positive median lead time (months) between the SAR change-point and the label month in new-building pixels, with no comparable change-point distribution in stable (never-built) control pixels.
- **Plausible data:** Sentinel-1 GRD monthly composites; SpaceNet 7 building IDs with first-appearance month; stable-pixel controls drawn from the same AOIs.
- **Plausible method:** Per-pixel change-point detection on backscatter time series (e.g., CUSUM or a Bayesian change-point model); compare lead-time distributions against controls; repeat for pan band 8 to compare SAR vs optical lead.
- **Main threat to validity:** Speckle and variable orbit/polarisation per AOI may create false change-points; ~24 months limits detection of long construction phases near series edges.
- **Weakening/refuting result:** Median lead time of zero or negative, or a lead-time distribution indistinguishable from the control-pixel distribution.
- **Criteria notes:** Scientifically interesting (timing of construction phases); fully testable with independent labels; no claim that this is new — the Lee et al. (2026) SAR construction-type paper may overlap, but its content is not in the packet (MISSING EVIDENCE).

## Rank 3 — Does a tool-calling agent make fewer false change claims than a direct multimodal model?

- **Research question:** When asked "where and when did new buildings appear?" for a held-out AOI, does an agentic workflow (LLM that calls deterministic change-detection tools on the pan/SAR stack) produce fewer unsupported change claims than a multimodal LLM answering directly from the imagery?
- **Candidate hypothesis:** The tool-calling agent achieves higher precision of reported change events (claims verified against SpaceNet 7) than the direct-answer baseline, at similar recall.
- **Expected observable evidence:** Higher event-level precision and lower false-claim count per AOI for the agent; agent errors traceable to tool outputs rather than invented changes.
- **Plausible data:** Same stack as Rank 1; SpaceNet 7 labels converted to event lists (location cell + month).
- **Plausible method:** Fixed prompt set per AOI; score each claimed event against labels at a defined spatial tolerance (e.g., 3×3 pixels at 15 m resolution) and temporal tolerance (±1 month).
- **Main threat to validity:** Most multimodal models are not built for 15 m panchromatic or SAR inputs, so a weak baseline could inflate the agent's advantage; LLM outputs are stochastic and model versions change.
- **Weakening/refuting result:** Equal or lower precision for the agent, or precision gains entirely explained by the agent reporting far fewer events (recall collapse).
- **Criteria notes:** Most directly "Agentic GeoAI"; relevant references (Zuo et al., 2026; Earth-Agent; Kao et al., 2026; TEOChat) are listed but their findings are not supplied (MISSING EVIDENCE), so novelty is unassessed. Tractability is the main risk: baseline selection and prompt design could consume the eight-week window.

## Rank 4 — What is the smallest new-building footprint reliably detectable at 15 m resolution?

- **Research question:** How does detection probability of a new building (or cluster) vary with its footprint area relative to a 15 m pixel (225 m²), for pan-only, SAR-only and fused inputs?
- **Candidate hypothesis:** Detection probability rises monotonically with footprint area, and the area at which detection recall reaches 0.5 is lower for fused input than for either sensor alone.
- **Expected observable evidence:** Logistic detection curves (recall vs footprint area) per input type, with the fused curve shifted toward smaller areas.
- **Plausible data:** SpaceNet 7 polygon areas (from ~4 m tracing) linked to detector outputs from Rank 1.
- **Plausible method:** Logistic regression of detected/not-detected on footprint area, sensor type and AOI random effect.
- **Main threat to validity:** Area is confounded with building density and neighbourhood context; label positional error relative to the 15 m grid.
- **Weakening/refuting result:** Flat detection curves (no area dependence) or overlapping curves across input types.
- **Criteria notes:** Useful practical result (sets limits of 15 m pixels for urban change); depends on Rank 1 outputs, so best as a secondary analysis in the same paper.

---

## Ranking rationale

1. **Rank 1** best fits the boundary conditions: clear spatial component, public data, an independent reference, a falsifiable comparison, and leave-AOI-out validation built in.
2. **Rank 2** is equally testable and uses the label-timing caveat as a hypothesis rather than a weakness; ranked second because SAR quality per AOI is unverified.
3. **Rank 3** is closest to the course theme but carries the highest tractability and baseline-fairness risk.
4. **Rank 4** is low-risk but derivative of Rank 1; recommended as a secondary analysis.

A combined paper could pair Rank 1 (primary) with Rank 4 (secondary), with Rank 3 as the agentic layer if time allows.

## Missing evidence / to verify

- MuRA-T download, band 8 integrity and claimed sub-pixel alignment (stated by a non-peer-reviewed preprint).
- Sentinel-1 scene counts, orbit direction and polarisations per AOI (marked TO VERIFY in the notes).
- Number of new buildings per AOI (needed to pick the 10–20 AOIs).
- Content of the listed references: none is summarised in the packet, so no novelty or prior-result claims are made.
- Label-to-pixel conversion rule (threshold on fraction of a 15 m pixel covered) is undecided and must be fixed before testing.


# EXECUTION REQUIREMENT

Work only from the supplied state and clearly label missing evidence.
Return the requested structured artifact. Do not silently change the research question.
