# Stage 4: Methodology Agent: Methodology v1

- **Source packet:** `outputs/prompt_packets/04_methodology_agent.md` (generated 2026-10-04 23:02)
- **Status:** Proposal only. No data have been downloaded and no results exist. No novelty, causal, policy or external-validity claim is made (AGENTS.md rule 9).
- **Inputs used:** H3 (followed as written); H1, with its latest rows overriding earlier ones (VLM comparison reinstated; VLM and agent tools get the same 1 km chips on the same 8 dates; a pretrained CNN change detector may be a tool or the fitted baseline; Landsat-8 panchromatic at 15 m resolution); form A1–A3 and human notes; `research_questions.md` (shared design §3); `question_review.md` (Q-A-R changes §7); `abstract_v1.md`; the ten human-verified L1 references (truncated evidence).
- **Caveat:** H1 rows were drafted by Claude; Stage 1–3 outputs are LLM outputs, so agreement among them is not validation (rule 4).

**Question (H3, unchanged).** In held-out SpaceNet 7 areas (2017–2020), does an LLM agent with built-in SAR and panchromatic tools detect new buildings (presence and month) in 100 m cells more accurately than a vision-language model that looks at the imagery directly, and than non-agent baselines given the same tool outputs? Does it fabricate fewer answers?

---

## 1. Data and access

| Layer | Source and access | Resolution | Role | Known issues |
|---|---|---|---|---|
| Panchromatic | Landsat-8 OLI band 8 from MuRA-T (GPL v3; Purdue download), Collection 1 Level-1 (L1TP), least-cloudy scene per month, QA band and cloud mask, co-registered to the SpaceNet 7 grid (form) | 15 m pixels | Chip input for VLM and tools | Level-1 radiometry needs relative normalisation (H1, X8); some months missing |
| SAR | Sentinel-1 C-band GRD (IW) from Earth Engine `COPERNICUS/S1_GRD` (or Planetary Computer `sentinel-1-rtc`) | 10 m pixels | Chip input for VLM and tools | Human co-registers it to the MuRA-T grid; scene count, orbit and polarisation vary by AOI (TO VERIFY) |
| Reference | SpaceNet 7 / MUDS monthly building footprints (CC BY-SA 4.0, AWS `spacenet-dataset`) | Traced on ~4 m Planet RGB | Labels only; never shown to any arm | Marks visibility (near completion), not construction start (form) |

- **Preprocessing (SAR).** Thermal-noise removal, calibration and orthorectification as in Lee et al. (2026); one orbit track per AOI (most scenes); record pass direction and incidence angle (H1, X5); a speckle filter fixed in advance; convert to dB for rendering.
- **Preprocessing (panchromatic).** Cloud-mask, then relative radiometric normalisation against pseudo-invariant pixels chosen on development AOIs [citation needed for the method]. Raw band 8 only, no pan-sharpening (Michel & Inglada, 2026, report that the scale-invariance assumption behind band-sharpening is unrealistic).
- **Fallback.** If MuRA-T fails, Landsat 8 Collection 2 band 8 from USGS or Earth Engine, self-co-registered (form). This adds misregistration risk (Qu et al., 2026).
- **Pretrained CNN change detector.** Not yet chosen [citation needed]. Hard requirement: its training data must not include SpaceNet 7 / MUDS imagery or labels, or it leaks the reference.

**Late human decision (relayed by the coordinator, 2026-10-04; overrides H3's last sentence).** The agent and the VLM get exactly the same inputs: the same 1 km chip centred on the queried 100 m cell, with that cell outlined; the same 8 dates; and the same question text. The secondary run in which the tools use all months is dropped and appears only under future work (§10).

---

## 2. Study area, period and unit of analysis

- **Study area.** 10–20 of the 60 SpaceNet 7 AOIs. Selection rule, pre-registered before any tool runs: at least N₁ Sentinel-1 scenes on one track, at least N₂ new-building cells, at least N₃ usable panchromatic months (Stage 1 §3.1). Whole AOIs are assigned to development (prompts, thresholds, P2 fitting, CNN choice, pilot) or test (run once, after freezing), e.g. 4 development and 8–14 test AOIs (H1). Selecting AOIs with many new buildings limits external validity but does not bias the paired comparisons (inference).
- **Period.** The SpaceNet 7 window, about 24 monthly steps per AOI, 2017–2020.
- **Unit of analysis.** One 100 m cell per query; the queried unit is the scored unit (H1). The independent unit for inference is the AOI.
- **Input unit.** For each sampled cell, a 1 km × 1 km chip centred on it: about 67 × 67 panchromatic pixels (15 m pixels) and 100 × 100 Sentinel-1 pixels (10 m pixels). The cell itself spans about 7 × 7 panchromatic pixels, so the target is development visible at 15 m resolution, not single houses (H3, H1).
- **Eight dates.** Chosen per AOI from data availability only (never from labels): the first and last usable months plus six months spread as evenly as possible between them, each requiring a usable panchromatic scene and a Sentinel-1 scene within ±15 days (tolerance to be fixed on development AOIs). Both arms see the same 8 dates, expressed as date indices 1–8, not calendar dates (Stage 1 §3.5 suggestion; closes the route to remembered events).
- **Target variables.** (i) Presence: did at least A_min m² of new footprint, absent in the first label month, appear in the cell? (ii) Onset: the first label month with footprint in the cell, mapped to the date interval (between consecutive chip dates) that contains it. With 8 dates, onset is resolved to an interval of about 3 months, not to a month. Cells built at month 1 with no new footprint form an "existing built" negative stratum; demolitions are reported separately (Stage 1 §3.3).
- **Predictor variables.** For the agent and the rules: tool outputs computed from the chips only (§3). For the VLM: the rendered chips.

---

## 3. Analytical steps

1. **Inventory (W1).** Download MuRA-T and SpaceNet 7; export Sentinel-1; count per AOI the usable panchromatic months, Sentinel-1 scenes per track, new-building cells, onsets near the window edges, and whether labels carry per-building IDs. Apply the pre-registered AOI rule.
2. **Grid and CRS.** Build 100 m cells in metres in the local UTM zone. The ~4.77 m SpaceNet 7 pixel may be a Web-Mercator grid, in which case grid-unit cells shrink on the ground by cos(latitude) (Stage 1 §3.2, inference). Reproject every layer once, with a stated resampling method.
3. **Reference rasterisation.** Intersect footprints with cells (straddling footprints split by area); derive presence, onset month and onset interval per cell.
4. **Chip rendering (shared input).** For each sampled cell and each of the 8 dates, cut a 1 km panchromatic chip and a 1 km Sentinel-1 chip (VV, plus VH where available), apply a fixed stretch, and draw the 100 m cell outline. One frame per date shows panchromatic and SAR side by side, so the sequence is exactly 8 frames, within TEOChat's 8-image training cap (Irvin et al., 2025). This frame layout is an assumption for Justin to confirm (§11). The same image files are the agent's tool inputs and the VLM's inputs.
5. **Tools (predefined, deterministic; no free-form code, per H1 and Kao et al., 2026, who report code failing over 44% of the time).** Each tool reads only the 8-date chips:
   - SAR cell series and a Gamma likelihood-ratio change test returning the candidate change interval and a statistic (adapted from Lee et al., 2026; a new adaptation, validated standalone, X13);
   - normalised panchromatic cell series, change magnitude and interval, with the cloud mask;
   - the pretrained CNN change detector, returning a change score for the outlined cell between date pairs;
   - a neighbour tool returning the same statistics for the 8 surrounding cells (needed for layover, Hou et al., 2026);
   - a data-availability tool (missing or cloudy dates).
   Tools return numbers and short text, not images.
6. **Answer schema (all arms).** `{presence: yes | no | abstain, onset_interval: 1–7 | null, evidence}`. Identical question text for agent and VLM. Scoring is deterministic; failures are classed by fixed rules adapted from Kao et al.'s categories, not by an LLM.
7. **Sampling.** Per test AOI, about 60 cells stratified by reference status (new / existing built / never built) × tool status (concordant / conflict-or-borderline), plus about 10 pre-registered unanswerable queries (e.g. a cell whose 8 chips are mostly cloud-masked or missing, or a question about a date index outside 1–8). Design weights are recorded. Final n is set by the W3 power simulation.
8. **Runs.** One pinned agent backbone and one pinned VLM; run dates logged; 3 repeats per query, or 1 run plus 3 repeats on a 20% subsample if the API cap binds (Stage 1 §3.6). Agent trajectories are logged and summarised at trajectory and answer level, following Feng et al. (2026).
9. **Freeze and pre-register** prompts, thresholds, A_min, guard bands, P1 and P2, the CNN choice and the sample before any test-AOI run.

---

## 4. Arms and comparators

| Arm | What it gets | What it isolates | API cost |
|---|---|---|---|
| **A. Tool-using LLM agent** | The 8-frame chip set via tools (ReAct-style loop, Feng et al., 2026), the question, opaque cell ID | The test system | Yes |
| **V. Direct VLM** | The same 8 frames as images, the same question, an explicit abstain option | Direct image reading vs tool grounding (main comparison, H1) | Yes |
| **P1. Tuned rule** | The same tool outputs; a fixed fusion rule with thresholds tuned on development AOIs | Agent reasoning vs a hand-tuned rule | None |
| **P2. Fitted rule / CNN** | The same tool outputs (including the CNN score) as features in a simple classifier (e.g. logistic regression) fitted on development AOIs | Agent reasoning vs an information-matched learned rule (QA.1) | None |
| **C1. Tools-disabled agent** | Question and opaque ID only, on a ~20% subsample | Memorised or prior answers; should be near chance | Small |
| **C2. Evidence-shuffled agent (optional)** | Tool outputs from a different cell, on a subsample | Whether the agent actually uses the evidence (QA.4) | Small |
| **Trivial baselines** | Always-no; prevalence-matched random | Floor for weighted F1 (X11) | None |

- **CNN placement.** Following H1, the pretrained CNN is offered as an agent tool and its score is a P2 feature, which keeps P2 information-matched. If the CNN is not ready by the end of W2, it is dropped from both, and the switch is recorded. A CNN-alone baseline (thresholded score) is reported as secondary.
- **What the VLM is.** Not yet chosen: a temporal EO VLM such as TEOChat (Irvin et al., 2025) or EarthDial (Soni et al., 2025), or a general-purpose VLM. H1 flagged setup time as a schedule risk; a hosted general-purpose VLM is the low-risk fallback. Its input limits are reported.
- **Required secondary (H1).** SAR-only vs SAR+panchromatic, answered with P1 and P2 on all sampled test cells (no API cost); a SAR-only agent on a subsample is exploratory (QB.1).

---

## 5. Endpoints and validation checks

- **Primary endpoint (proposed; Justin to confirm, abstract item 2).** Design-weighted presence-F1 difference, agent − VLM, with a 95% AOI-cluster bootstrap CI (H1). One primary only (X9).
- **Key secondary.** Agent − P1 and agent − P2 presence-F1 with AOI-cluster CIs (estimation framing, no δ; H1); the same on the conflict stratum; fabrication rate = share of non-abstaining answers on unanswerable queries, agent vs VLM; for the agent only, unsupported evidence (cited values that do not match the logged tool outputs); onset-interval accuracy and error in intervals. McNemar and Wilcoxon tests are secondary only.
- **Prevalence-free metrics.** Balanced accuracy and per-stratum recall, because weighted F1 depends on the allocation (X11).

| Check | Pass condition |
|---|---|
| Tool validation (W2) | Each tool's standalone F1 and onset error on development AOIs reported; pre-registered fallback statistic if the SAR change test fails (X13) |
| CNN leakage | Pretraining data documented and free of SpaceNet 7 |
| Memory leakage | C1 near chance; opaque IDs and date indices only; no coordinates or AOI codes (H1, X6) |
| Evidence use | C2 accuracy drops clearly below A |
| Registration | Results stable under a one-pixel shift (Qu et al., 2026) |
| Radiometry | Pseudo-invariant pixels show no trend after normalisation |
| Window edges | Guard bands fixed on development AOIs; results with and without (X12) |
| Repeatability | Agreement across the 3 repeats reported per arm |
| Few clusters | Per-AOI estimates and a mixed model with an AOI random effect [citation needed for few-cluster bootstrap coverage] |
| External validation | None available: MUDS is the only reference (Stage 2 §6); stated as a limitation |

---

## 6. Spatial assumptions

- **CRS and units.** All cells, chips and distances in metres in local UTM; the true cell area is reported per AOI.
- **Scale.** 100 m cells ≈ 7 × 7 panchromatic pixels at 15 m resolution and 10 × 10 Sentinel-1 pixels; claims are about development at that scale, not buildings. MAUP: the primary metric is repeated at 200 m only.
- **Spatial autocorrelation.** Sampled cells in one AOI share context and their 1 km chips overlap; the AOI is the independent unit and inference is clustered. Sampled cells are kept at least one cell apart.
- **Layover.** Building returns can shift into neighbouring cells along the look direction (Hou et al., 2026); sensitivity check allows one neighbour along the look direction (H1, X5).
- **Temporal alignment.** SAR within ±15 days of each panchromatic date; label onset lags visibility, and SAR change is expected to lead the label (Lee et al., 2026, inference); the lag is reported as its own estimate.
- **Sampling bias and transferability.** AOIs are chosen for many new buildings and good Sentinel-1 coverage; results are not claimed beyond them, nor beyond this backbone, VLM and tool set (curated tools only, Kao et al., 2026).

---

## 7. Key risks

1. **Data.** MuRA-T download or Sentinel-1 coverage fails for enough AOIs (especially 2017 outside Europe [citation needed]); fewer than 8 usable shared dates in some AOIs.
2. **Too few clusters.** 8–14 test AOIs may give wide CIs; the main contrasts may be inconclusive.
3. **Tool failure.** The adapted LRT tool or the CNN performs poorly at 15 m resolution on 1 km chips, so the agent inherits weak evidence.
4. **VLM setup.** EarthDial or TEOChat setup overruns (H1); render choices (stretch, side-by-side layout) may favour or hurt the VLM.
5. **Few conflict cells.** If tools rarely disagree, the conflict-stratum contrast is underpowered (switch rule, Stage 1 §4).
6. **Cost.** About 10 AOIs × 70 queries × 3 repeats ≈ 2,100 episodes per LLM arm (illustrative); the API cap is set in the pre-registration.

## 8. What evidence would weaken the claim

- The agent − VLM CI includes 0 or favours the VLM, or the VLM fabricates no more often than the agent.
- The agent − P2 CI is clearly negative, or the agent beats P1 but not P2 (the gain is better use of tool outputs, not reasoning).
- No agent gain on the conflict stratum.
- C1 (tools-disabled) approaches A's accuracy, or C2 (shuffled evidence) barely lowers it: the agent is not using the tools.
- Results flip under the one-pixel shift, the 200 m grid, guard bands or the layover check.
- Trajectories show near-identical tool calls on every query: the agent is a fixed pipeline, so no claim about planning is made (QA.1).

## 9. AI-assisted coding tools

- Claude Code (and similar assistants) is used to write the download, gridding, chip-rendering, tool, harness and analysis code. Every generated function is reviewed by Justin and tested on synthetic rasters with known change before real data.
- Prompts and code are version-controlled; intermediate artifacts are kept in `outputs/` (rule 10).
- No LLM scores answers, classifies failures or edits labels.
- The paper discloses AI-assisted coding and writing. The agent and VLM under test are separate pinned models, not the coding assistant.

## 10. Future work (not in this paper)

- A run in which the tools read all monthly images (dropped by the late human decision).
- Sharper commercial panchromatic; other backbones and VLMs; Q-C neighbourhood attribution (H1).

## 11. Assumptions most likely to change the conclusion

1. **Shared 8-frame input.** Side-by-side panchromatic + SAR frames and the stretch choices; a different rendering could change VLM accuracy.
2. **Primary contrast** is agent vs VLM (Justin to confirm).
3. **The 8 dates** are enough to locate onset; a 3-month interval may blur onset scoring.
4. **The CNN is not trained on SpaceNet 7** and transfers to 15 m panchromatic.
5. **A_min and the unanswerable-query definition** set what counts as presence and as fabrication.
6. **Enough test AOIs and conflict cells** after the inventory.

**Unresolved:** VLM choice; CNN choice; A_min, guard bands, borderline band, ±15-day tolerance, API cap; grid CRS; target-journal fit (IJDE) for a possible null result; evidence was truncated and no wider literature search was done.

**Next scientific action:** Justin confirms the primary contrast, the VLM and the frame layout; then the W1 inventory and pre-registration draft go to `outputs/`.

---

## 12. Eight-week work plan

| Week | Tasks | Deliverable | Main risk |
|---|---|---|---|
| W1 | Download MuRA-T, SpaceNet 7, Sentinel-1; AOI inventory and selection; choose VLM and CNN; draft pre-registration | Inventory table, AOI split, pre-registration draft | MuRA-T or Sentinel-1 coverage insufficient |
| W2 | UTM grid, reference rasterisation, 8-date selection, chip rendering; build and validate tools standalone on development AOIs | Chip set, tool library, tool-validation report | LRT or CNN fails validation at 15 m resolution |
| W3 | Agent and VLM harness; tune P1, fit P2; full development pilot of all arms; power simulation; set n and API cap | Pilot results, frozen prompts and rules | VLM setup overruns; too few conflict cells |
| W4 | Freeze and pre-register; run A, V, C1, C2 on test AOIs; run P1, P2 and SAR-only vs SAR+pan pipelines | Pre-registration, raw test outputs and logs | API cost or rate limits |
| W5 | Score; cluster-bootstrap CIs; robustness (shift, 200 m, guard bands, layover, mixed model); trajectory summary | Results tables and figures | Wide CIs from few test AOIs |
| W6 | Draft methods, results, discussion, limitations | Full manuscript draft | Over-claiming beyond the evidence |
| W7 | Critic review; check claims against results and L1 references; revise | Revised manuscript, claim audit | Review uncovers an analysis error |
| W8 | Final checks; package code and data; format; submit | Submitted paper, code and data archive | Journal formatting or scope mismatch |
