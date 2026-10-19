# Stage 4: Methodology Agent: Methodology v1 (revision)

- **Source packet:** `outputs/prompt_packets/04_methodology_agent.md`
- **Status:** Proposal only; no data downloaded, no results. No novelty, causal or external-validity claim (AGENTS.md rule 9).
- **Inputs used:** H3 (as written); H7 (all 8 methodology critiques accepted); H1 (latest rows override earlier ones); previous v1; `methodology_review.md`. H1 rows were drafted by Claude and stage outputs are LLM outputs, so agreement among them is not validation (rule 4).

**Question (H3, unchanged).** In held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery and than non-agent baselines given the same tool outputs?

## 1. Data and access

| Layer | Source | Resolution | Role |
|---|---|---|---|
| Panchromatic | Landsat-8 band 8 from MuRA-T (Collection 1 Level-1, co-registered to SpaceNet 7; Purdue download) | 15 m pixels | Chip input |
| SAR | Sentinel-1 IW GRD, Earth Engine `COPERNICUS/S1_GRD` | 10 m pixel spacing (about 20 m resolution) | Chip input |
| Reference | SpaceNet 7 / MUDS monthly footprints (AWS `spacenet-dataset`) | Traced on ~4 m Planet imagery | Labels only; never shown to any arm |

- **SAR preprocessing:** noise removal, calibration, orthorectification (Lee et al., 2026); one orbit track per area; pass direction and incidence angle recorded; fixed speckle filter. Co-registered to the MuRA-T grid by hand; **co-registration RMSE (metres) reported per area** (H7.4).
- **Panchromatic preprocessing:** cloud mask; relative radiometric normalisation on pseudo-invariant pixels [citation needed]; no pan-sharpening.
- **Fallback:** Landsat 8 Collection 2 band 8, self-co-registered (higher misregistration risk; Qu et al., 2026).
- **Model training data (H7.6):** the chosen VLM's and CNN's training data are documented; any model trained on SpaceNet 7 imagery or labels is excluded [missing evidence for candidate models].

## 2. Study area and unit of analysis

- **Areas.** 10–20 SpaceNet 7 areas meeting a pre-registered rule (minimum Sentinel-1 scenes on one track, new-building cells, usable panchromatic months). Whole areas are assigned to development (prompts, thresholds, P2 fitting, pilot) or test. Following H7.3, as many eligible areas as possible go to test (e.g. 4 development, the rest test).
- **Period.** Monthly, 2017–2020; per area, 8 shared dates chosen from data availability only (never labels), given to arms as date indices 1–8.
- **Unit.** One 100 m cell per query (scored unit = queried unit); the **area is the independent unit** for inference.
- **Input.** The same 1 km chip centred on the cell, with the cell outlined, on the same 8 dates, for every arm that sees imagery (H3). A 100 m cell spans about 7 × 7 pixels at 15 m resolution.
- **Positive cell.** **≥ A m² of new footprint** absent in the first label month. A is fixed on development areas as the smallest new-footprint area the tools detect reliably in 15 m pixels (H7.4); results are also reported by change size. Existing-built cells form a negative stratum.
- **Onset.** The first label month with footprint in the cell, mapped to the interval between consecutive chip dates.

## 3. Analytical steps

1. **Inventory (W1):** count usable months, Sentinel-1 scenes, new-building cells per area; apply the area rule.
2. **Grid:** 100 m cells in local UTM metres; every layer reprojected once with a stated resampling method.
3. **Reference:** intersect footprints with cells; derive presence (≥ A m²) and onset interval.
4. **Chips:** per sampled cell and date, a 1 km panchromatic and Sentinel-1 frame, fixed stretch, cell outlined; 8 frames per query.
5. **Tools (predefined, deterministic; Kao et al., 2026):** SAR likelihood-ratio change test (adapted from Lee et al., 2026; validated standalone); panchromatic change series; neighbour statistics (layover; Hou et al., 2026); data availability; optional pretrained CNN.
6. **Answer schema (all arms):** `{presence: yes | no | abstain, onset_interval | null, evidence}`; the same abstain option for all arms; deterministic scoring, no LLM grader.
7. **Sampling:** per test area, cells stratified by reference status × tool agreement, **spaced at least 300 m apart** (or chip overlap reported) (H7.6); plus pre-registered unanswerable queries (§5).
8. **Pilot and gate:** full pilot on development areas; **area-level power simulation** (H7.3); then set A, the margin δ, n and the API cap.
9. **Freeze and pre-register** prompts, rules, A, δ, abstention scoring and sample **before any test run**.

## 4. Arms

| Arm | Inputs | Isolates |
|---|---|---|
| **A. Tool-using LLM agent** | Tools over the 8 chips, question, opaque cell ID | Test system |
| **V. VLM** | The same 8 frames as images, same question | Direct image reading (main contrast) |
| **VT. VLM + tool outputs as text** | V's frames plus A's tool outputs as text (subsample) | Tool access vs agentic reasoning (H7.2) |
| **P1. Tuned rule** | Same tool outputs; thresholds tuned on development areas | Reasoning vs a hand-tuned rule |
| **P2. Fitted rule** | Same tool outputs as features in logistic regression fitted on development areas | Reasoning vs an information-matched learned rule |
| **C1. Tools-disabled agent** | Question and opaque ID only (subsample) | Agent memory leakage |
| **C2. Blank-image VLM** | Blank frames, same question (subsample) | VLM memory or prior leakage (H7.6) |

V and VT get the same development-area budget for prompt and rendering tuning as A. **Optional (H7.8):** shuffled-evidence agent, the CNN tool/feature, and the SAR-only vs SAR + panchromatic secondary.

## 5. Endpoints

- **Co-primary (H7.7):** presence-F1 and balanced accuracy, agent − VLM, each with an area-cluster CI.
- **Non-inferiority (H7.1):** agent − P2 on presence-F1 and balanced accuracy against a **margin δ pre-registered after the pilot and before any test run**; non-inferior if the lower CI bound exceeds −δ. Agent − P1 and agent − VT reported with CIs; conflict stratum secondary.
- **Abstention scoring (H7.7):** pre-registered; abstentions on answerable cells count as wrong in the co-primary metrics; risk–coverage curves reported.
- **Fabrication (H7.5):** unanswerable queries built so both arms can detect them equally (e.g. a question naming a date index or band not supplied, or frames with the outlined cell blanked in every image, so the gap is visible to the VLM and reported by the tools alike). **Fabrication rate = share of non-abstaining answers**, reported by query type; queries included in the power simulation.
- **Onset (H7.4):** exact-interval accuracy plus **±1-interval accuracy** (pre-registered secondary); label-lag distribution reported.
- **Inference (H7.3):** few clusters, so a pre-specified few-cluster method (e.g. wild cluster bootstrap [citation needed]); minimum detectable presence-F1 difference stated from the area-level simulation.

## 6. Validation checks

| Check | Pass condition |
|---|---|
| Tool validation | Standalone presence-F1 and onset error on development areas; pre-registered fallback if the SAR test fails |
| Leakage | C1 and C2 near the trivial baseline in balanced accuracy; no coordinates or area codes shown |
| Registration | Results stable under a one-pixel shift (Qu et al., 2026); Sentinel-1 RMSE reported |
| Radiometry | Pseudo-invariant pixels show no trend after normalisation |
| Repeatability | Answer agreement across 3 repeats reported per arm |
| External validation | None possible (MUDS only); stated as a limitation |

## 7. Spatial assumptions

UTM metres throughout; claims concern development at 15 m resolution, not single houses; 200 m grid as MAUP check; areas are the independent unit (autocorrelation); layover sensitivity allows one neighbour along the look direction; SAR change expected to lead labels (Lee et al., 2026, inference); no transfer beyond these areas, models and curated tools.

## 8. Key risks and what would weaken the claim

- **Risks:** too few eligible test areas; weak tools at 15 m resolution; VLM setup overrun; few conflict cells; API cost.
- **Weakening evidence:** agent − VLM CIs include 0 on both co-primaries; VT matches A (gain is tool access, not reasoning); agent fails non-inferiority against P2; VLM fabrication rate no higher than the agent's; C1 or C2 well above the trivial baseline; results flip under shift, 200 m grid or layover checks.

## 9. AI-assisted coding tools

Claude Code drafts download, gridding, chip, tool, harness and analysis code; Justin reviews every function and tests it on synthetic rasters with known change. Code and prompts are version-controlled; no LLM scores answers or edits labels; AI assistance is disclosed.

## 10. Eight-week plan

| Week | Tasks | Deliverable | Main risk |
|---|---|---|---|
| W1 | Downloads; area inventory and split; pick hosted VLM; document VLM training data; draft pre-registration | Inventory, area split | Too few eligible areas |
| W2 | Grid, reference, chips, Sentinel-1 RMSE; build and validate core tools; fix A. **Go/no-go gate:** ≥ 8 test areas and tools pass validation, else cut to SAR-only or fewer arms | Chip set, tool report, gate decision | SAR test fails at 15 m resolution |
| W3 | Harness for A, V, VT, C1, C2; tune P1, fit P2; pilot; area-level power simulation | Pilot results, δ, n, API cap | Few conflict cells |
| W4 | Pre-register; run all required arms on test areas | Pre-registration, raw outputs | API limits |
| W5 | Score; few-cluster CIs; robustness | Results tables and figures | Wide CIs |
| W6 | Optional extras (shuffled evidence, CNN, SAR-only) only if on schedule; draft manuscript | Draft | Scope creep |
| W7 | Critic review; claim audit; revise | Revised draft | Analysis error found |
| W8 | **Buffer (first half)**; package code; submit | Submitted paper | Slippage absorbed |

## What changed from v1

1. Non-inferiority margin δ for agent vs P2, set after the pilot, before testing (H7.1).
2. Added VT (VLM + tool outputs as text) and equal tuning budget (H7.2).
3. Power simulation over areas; minimum detectable presence-F1 difference; few-cluster method; more areas to test (H7.3).
4. A fixed from 15 m pixels; Sentinel-1 RMSE; ±1-interval onset (H7.4).
5. Unanswerable queries detectable by both arms; fabrication rate by query type (H7.5).
6. Blank-image VLM control; training-data documentation; wider cell spacing (H7.6).
7. Abstention scoring pre-registered; balanced accuracy co-primary (H7.7).
8. Week-2 gate; shuffled evidence, CNN and SAR-only optional; buffer (H7.8).
