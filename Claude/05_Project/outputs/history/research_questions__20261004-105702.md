# Stage 1: Research Question Agent: Ranked Candidate Research Questions

- **Source packet:** `outputs/prompt_packets/01_research_question_agent.md` (generated 2026-10-02 17:01)
- **Status:** Proposal only. Nothing here is a result. No novelty, causal, policy, or external-validity claim is made, and none can be made without human approval (AGENTS.md rule 9).
- **Broad problem (unchanged, form A1):** *How can Agentic GeoAI help interpret large sources of satellite imagery in an area of interest to understand patterns and changes over time?*

---

## 1. Inputs used

| Input | What it contributed | Caveat |
|---|---|---|
| Form A1–A3 (research problem, boundary conditions) | Scope: a spatial component, public or research-accessible data, a testable question, explicit validation, and a paper submitted within 8 weeks | None |
| Human note: "Panchromatic and SAR to start" | Sensor focus | The panchromatic sensor, AOI, time window and target phenomenon are **not specified** |
| Human decisions | None recorded | |
| Prior reviewer feedback | None supplied | |
| L1 references (10) | Citation pool | **All 10 are marked "NOT yet verified"** by the human |
| Evidence PDFs (10, same papers as L1) | Evidence base for question design | **Each paper is truncated at 20,000 characters** in the packet (about 12–40% of each paper). I saw abstracts, introductions, related work and part of the methods, but **most results, limitations and appendix sections were not visible**. Statements below are limited to the visible text |

## 2. Assumptions (all require human confirmation)

- **A1. Panchromatic source = Landsat 8/9 OLI panchromatic band (15 m) [citation needed].** This is the only public panchromatic archive that overlaps the Sentinel-1 era, as far as I can infer. If the human has access to sub-metre commercial panchromatic data through a research program, the data feasibility and the spatial unit of every question below change.
- **A2. SAR source = Sentinel-1 C-band GRD (IW mode, 10 m pixel spacing) from Google Earth Engine.** This is the configuration used by Lee et al. (2026): 133 ascending VV scenes over 2019–2023.
- **A3. "Agentic GeoAI" = an LLM that plans and calls predefined geospatial tools in a ReAct-style loop** (as in Earth-Agent, Feng et al., 2026). It does **not** mean training a new foundation model. Training at the scale of EarthDial (8× A100 GPUs, 11.11M instructions; Soni et al., 2025) is not feasible in 8 weeks.
- **A4. Target phenomenon = construction and urban land change.** I chose this because three supplied papers centre on it (Lee et al., 2026; Xuan et al., 2025; the MUDS dataset in Qu et al., 2026) and because construction produces SAR step and impulse signatures. **This narrows the broad problem and needs human approval.** The other "patterns and changes" in A1 (for example floods, agriculture or deforestation) would need different references and reference data.
- **A5. Single researcher, about 8 weeks, AI-assisted coding, modest compute.** The compute and LLM-API budget are unknown.
- **A6. One AOI is studied, with spatially separated development and test blocks.** Any generalisation beyond that AOI is out of scope unless a second AOI is added.

## 3. What the supplied evidence establishes and leaves open

Evidence is what the visible text states. Inference is my reading of it.

| Paper (supplied evidence) | Evidence (visible text) | Inference relevant to question design |
|---|---|---|
| Kao et al., 2026 (UnivEarth) | 408 yes/no EO questions answered with GEE code. The best zero-shot accuracy was 40.0%, and code failed to run over 44% of the time. Reflexion raised Claude-4.5-Sonnet, Gemini-2.5-Pro and GPT-5 to around 60%, "only marginally above random chance". Failure taxonomy: C1 empty collection, C2 no valid pixels (e.g., after cloud masking), C3 calculation failure, D code/syntax error. The main-source table lists Landsat, MODIS, VIIRS and others, and no SAR instrument appears in it | Free-form code generation is unreliable, so predefined tools are the safer design. Cloud-driven data-availability failures are a known failure mode. SAR is under-represented in this benchmark's main sources |
| Feng et al., 2026 (Earth-Agent) | MCP-based ReAct agent with 104 tools in 5 kits (Index, Inversion, Perception, Analysis, Statistics). Earth-Bench has 248 questions and 13,729 images spanning spectrum, products and RGB. Dual-level evaluation covers the reasoning trajectory and the final answer. Code is public | A reusable agent scaffold and evaluation protocol. SAR is not listed among the Earth-Bench modalities in the visible text |
| Xuan et al., 2025 (DynamicVL) | DVL-Suite: 14,871 NAIP images at 1.0 m, 42 U.S. cities, 2005–2023, about 6.7–6.9 frames per scene. Of 18 MLLMs, the best (o4-mini) reached only 34.1% overall QA accuracy. Tasks include change speed estimation and dense temporal captioning. Part of the response text is GPT-generated from human annotations | MLLMs are weak at long-term temporal and quantitative change questions. NAIP is a possible independent high-resolution reference in U.S. AOIs |
| Irvin et al., 2025 (TEOChat) | First VLM for temporal EO sequences. Sequences were limited to a maximum of 8 images because of memory. Data, model and code are public | Direct-VLM baselines cannot ingest a full multi-year archive, so archive size is a testable factor |
| Soni et al., 2025 (EarthDial) | 4B-parameter VLM whose instruction data covers RGB, SAR and multispectral imagery, with bi- and multi-temporal tasks. Code and models are public | The most plausible off-the-shelf direct-VLM baseline for SAR input. Its support for multi-temporal SAR specifically is **not confirmed** in the visible text |
| Zuo et al., 2026 (CVAHR-CD-LLM) | Bitemporal change-detection MLLM with a CVA-based iterative coordinate calibration loop and chain-of-thought self-consistency to reduce hallucination | A precedent for statistically grounding LLM change claims. Its quantitative results were not visible |
| Lee et al., 2026 (SAR change types) | Sentinel-1 GRD 2019–2023 over South Korea. DespecKS filtering, then a likelihood-ratio-test change criterion matrix (Gamma assumption), then spectral clustering into **8 classes** (unchanged, complex, down step, up step, spike impulse, long impulse, regular cycle, irregular cycle). 1,462 expert-labelled samples, overall F1 0.94. Up-step is linked to construction and down-step to land clearing. The authors state semantic associations "are demonstrated within the evaluated construction environments" | A physically grounded SAR tool chain that an agent could call. Transfer to another AOI is explicitly open. Whether the reference dataset is publicly available is **unknown** |
| Qu et al., 2026 (AnyTime-CD) | Irregular time series caused by cloud, orbit and tasking. Pixel misalignment creates pseudo-change. AOI-level 4:1:1 split to prevent spatial leakage. One-frame tolerance F1 | Precedents for spatial-split design, temporal-tolerance scoring and misregistration controls |
| Hou et al., 2026 (SAR FM review) | SAR is all-weather. Speckle, layover, foreshortening, shadow, and incidence-angle and polarisation dependence hinder transfer. Optical-style augmentations can corrupt SAR information. "Multimodal SAR agents" is listed as a future direction | Threats to validity for any SAR question. SAR agents are an acknowledged open direction (in this review only) |
| Michel & Inglada, 2026 (TAMRF) | Landsat-8/9 and Sentinel-2 time-series fusion. Band-sharpening (pan-sharpening) usually relies on a scale-invariance hypothesis that "several studies show" is unrealistic | If panchromatic data is used to sharpen multispectral bands, the sharpened product carries an untested assumption, so raw panchromatic data is preferable as tool input |

**Gap relative to supplied evidence (not a novelty claim):** none of the ten supplied papers evaluates an LLM agent that interprets a dense **SAR + panchromatic** time-series archive over one AOI, or compares it against both a direct VLM and a non-agentic pipeline. A literature search beyond these ten papers is required before any novelty statement, and human approval is required before claiming novelty.

---

## 4. Ranked summary

Ratings are my judgements against the seven required criteria (H = high, M = medium, L = low).

| Rank | ID | Short title | Importance | Novelty vs. supplied evidence | Testability | Data feasibility | GeoAI/spatial relevance | Tractability (8 wk) | Validation strength |
|---|---|---|---|---|---|---|---|---|---|
| 1 | RQ1 | Tool-grounded agent vs. direct VLM vs. fixed pipeline for change presence and onset in a dense SAR + panchromatic archive | H | M–H (unverified) | H | H (reference labels are the bottleneck) | H | M–H | H |
| 2 | RQ2 | Statistical verification loop to suppress unsupported change claims in agent-written AOI change reports | H | M | H | H | M | H | H if the reference is SAR-independent |
| 3 | RQ3 | Do Lee et al.'s SAR change-type classes transfer to a new AOI, and does an agent interpret them better than a lookup? | M–H | M | M–H | M (AOI-dependent records) | H | M | M |
| 4 | RQ4 | Adaptive panchromatic/SAR sensor selection under cloud cover | M | L–M | H | H | H | H | H |

**Ranking rationale.** RQ1 most directly tests the broad problem: does an agentic layer improve interpretation of a large archive, and does it add anything beyond the tools it calls? It has the clearest falsification structure and needs no model training.

RQ2 is nearly as strong and cheaper, and it reuses RQ1's infrastructure. It ranks second because it addresses LLM behaviour more than spatial science, and because a CVA-calibration precedent already exists (Zuo et al., 2026).

RQ3 has the strongest geographic-science content, since it tests external validity explicitly left open by Lee et al. It carries reimplementation risk, because the packet truncates the method, and its reference data depends on the AOI.

RQ4's main effect is largely predictable by design, since SAR sees through cloud. It is best run as an ablation inside RQ1 rather than as a stand-alone paper.

**Recommended scope for 8 weeks:** RQ1 as the primary question, with RQ4 as a built-in ablation. Add RQ2 only if RQ1's test runs are frozen by about week 5.

---

## 5. Candidate questions

### RQ1 (Rank 1): Does a tool-grounded agent interpret a dense SAR + panchromatic archive more accurately than a direct VLM, and does it add anything beyond a fixed pipeline?

**Research question.** In a single AOI, consider a multi-year Sentinel-1 GRD archive (about 100+ scenes; cf. 133 scenes for 2019–2023 in Lee et al., 2026) together with the Landsat 8/9 panchromatic observations. Does an LLM agent that answers change questions by calling predefined statistical time-series tools identify (a) whether construction-related change occurred in a grid cell and (b) the date it began, more accurately than:
- (i) a multi-temporal VLM given the imagery directly, and
- (ii) the same tools run as a fixed, non-agentic pipeline?

**Candidate hypotheses** (thresholds to be pre-registered by the human before any test-set run):
- **H1a.** The agent beats the direct VLM on change-presence F1 and on median onset-date error.
- **H1b (archive size).** As the number of scenes supplied grows (e.g., 8 → 32 → full archive), the VLM's accuracy does not improve. The agent's accuracy is stable or improves. The 8-scene level matches TEOChat's training maximum (Irvin et al., 2025).
- **H1c (agentic value).** Across a set of varied natural-language question templates, the agent is **non-inferior** to a hand-built pipeline for each template, within a pre-set margin (e.g., 5 F1 points; the human sets the margin). If H1c fails, the agent's value is limited to the interface rather than the analysis. That is still a reportable result.

**Expected observable evidence.**
- Per-cell correctness and onset error in days and in acquisition intervals, scored with a one-frame tolerance as in Qu et al. (2026).
- Bootstrap confidence intervals.
- Agent tool-call trajectories scored separately from final answers, following the dual-level evaluation of Feng et al. (2026).
- Failure counts using the UnivEarth taxonomy (C1/C2/C3/D; Kao et al., 2026).

**Plausible data.**
- Sentinel-1 GRD IW, VV (plus VH if available), one orbit track, from GEE (as in Lee et al., 2026).
- Landsat 8/9 panchromatic band (15 m) [citation needed], with QA cloud mask [citation needed].
- **Reference data (independent of the tested tools):**
  - Human-interpreted change presence and onset bracket from an optical archive, e.g., Sentinel-2 L2A [citation needed].
  - NAIP 1 m if the AOI is in the U.S. (the archive used by Xuan et al., 2025).
  - Dated building-footprint or permit records where they exist [citation needed].
- If the AOI is one of the 42 DVL-Suite cities, DVL-Bench labels might serve as a secondary reference. **Their release format and licence are unverified.**

**Plausible method.**
1. **Grid.** Choose one AOI with known construction during the Sentinel-1 era. Tile it into cells of about 100 m in a local UTM CRS. Repeat key metrics at about 200 m as a MAUP sensitivity check.
2. **Reference set.**
   - Draw a stratified random sample of cells (change / no-change strata from a pre-screen that uses none of the tested tools). The order of magnitude is 300–500 cells, with the final number set by a power calculation from pilot discordance rates.
   - Label blind to all model outputs. Lee et al. (2026) kept their labels independent of algorithm outputs in the same way.
   - Record onset as a bracket: last clear "before" date to first clear "after" date.
   - Re-label 10–20% after a delay to measure intra-rater agreement, because only one annotator is available.
3. **Tools** (predefined, not free-form GEE code, given the >44% code-failure rate reported by Kao et al., 2026). Possibly as MCP tools on the public Earth-Agent scaffold:
   - Sentinel-1 per-cell series extraction.
   - Speckle filtering.
   - LRT-based change test returning candidate change dates and statistics.
   - Panchromatic per-cell series with cloud mask.
   - A panchromatic change-magnitude tool.
   - A plot renderer.
4. **Arms.**
   - **(A) Agent:** one LLM backbone at minimum; a second if budget allows.
   - **(B) Direct VLM:** EarthDial, which lists SAR in its training data (Soni et al., 2025), and/or TEOChat. Image sequences are subsampled to each model's input limit. A fairness arm also gives the VLM its best-supported optical input.
   - **(C) Fixed pipeline:** the same tools with thresholds tuned on development blocks only.
5. **Spatial split.** Use spatially separated development blocks (prompt and threshold tuning) and test blocks (evaluation only), following the leakage logic of the AOI-level split in Qu et al. (2026).
6. **Statistics.**
   - McNemar's test (paired) for presence correctness.
   - Wilcoxon signed-rank test for onset error.
   - Spatial-block bootstrap confidence intervals.
   - At least 3 repeated agent runs to quantify run-to-run variance.
   - Log the model version and date for every run.
7. **Archive-size factor.** Rerun arms A and B with 8, 32 and all scenes.

**Main threat to validity: baseline fairness and construct validity.**
- VLMs receive out-of-distribution inputs (15 m panchromatic, C-band VV SAR, more frames than they were trained on). "Agent beats VLM" could therefore reflect a mismatched baseline rather than an advantage of agentic design. The fairness arm mitigates this but does not remove it.
- **Secondary threat:** the onset reference is bracketed by gaps in clear optical observations. Onset differences finer than the bracket width cannot be resolved. Report error relative to bracket width, and exclude or flag wide brackets.

**What would weaken or refute it.**
- Agent vs. VLM differences whose confidence intervals include zero refute H1a.
- VLM accuracy that improves with more scenes as much as the agent's does refutes H1b.
- An agent that falls below the pipeline by more than the margin refutes H1c, meaning the agentic layer adds cost but not accuracy.
- If most agent errors trace to tool-selection or parameter mistakes in the trajectories, that weakens any claim that the agent's reasoning is reliable, even if final accuracy is acceptable.

**Criteria evaluation.**
1. **Importance (H):** this is the core of the broad problem. The supplied evidence shows a large reliability gap: 34.1% best MLLM QA in Xuan et al. (2025), and 40% zero-shot / about 60% with reflexion in Kao et al. (2026).
2. **Novelty (M–H, unverified):** see the gap statement in §3. It is not a novelty claim.
3. **Testability (H):** a paired design with pre-registered margins.
4. **Data feasibility (H):** Sentinel-1 and Landsat are public. The reference labelling is the cost.
5. **Spatial relevance (H):** per-cell location and timing, with an explicit MAUP check.
6. **Tractability (M–H):** no training. The cost lies in about 2 weeks of reference labelling plus tool building.
7. **Validation (H):** independent optical reference, spatial block split, repeated runs, and deterministic scoring.

**Spatial-specific notes.**
- Sentinel-1 (10 m) and panchromatic (15 m) data must be resampled to a common grid. State the method and test sensitivity to a one-pixel shift, since Qu et al. (2026) show that misregistration creates pseudo-change.
- Mask SAR layover and shadow with a DEM [citation needed], following Hou et al. (2026) on geometry effects.
- Check that the Sentinel-1 scene density is stable across the window, because constellation changes may alter revisit [citation needed].

---

### RQ2 (Rank 2): Does a statistical verification loop reduce unsupported change claims in agent-written AOI reports?

**Research question.** When an LLM agent writes a structured change report for an AOI (where, when and what kind of change), does it gain claim precision at matched recall if every claim must pass a statistical verification tool before inclusion? The tool would be a SAR LRT change test plus panchromatic change magnitude, analogous to the CVA-based calibration loop of Zuo et al. (2026). The comparison is against:
- (i) unverified reports, and
- (ii) self-consistency aggregation alone (the other mechanism used by Zuo et al., 2026).

**Candidate hypothesis.**
- **H2.** The verification loop raises claim precision at matched recall relative to unverified reports.
- Self-consistency alone yields a smaller gain.
- The two mechanisms combined are at least as good as either alone.

**Expected observable evidence.**
- Precision–recall curves and area under the precision–recall curve per arm.
- Precision at a pre-set matched recall.
- The share of claims with traceable tool provenance.
- The number of claims per report, to detect "gains" that come only from saying less.

**Plausible data.** The same AOI, archives and independent optical reference as RQ1. RQ2 shares RQ1's infrastructure.

**Plausible method.**
- A 2×2 factorial design: verification on/off × self-consistency on/off, with identical prompts and k samples per report.
- Claims are forced into a structured schema (cell or polygon, date interval, change type), so scoring against the reference is deterministic. **No LLM-as-judge is used for primary metrics**, because agreement between LLMs is not validation (AGENTS.md rule 4).
- Include a **threshold-only, non-LLM baseline:** the verification tool's own output thresholded into a change map.
- Use the same spatial dev/test split and paired tests as RQ1.
- Optionally, add a narrative-level variant modelled on DVL-Bench dense temporal captioning (Xuan et al., 2025), scored only on its extracted structured claims.

**Main threat to validity: circularity and conservatism.**
- If the reference labels or the sampling frame were derived from the same SAR test used for verification, "verified" claims will look correct trivially. The reference must be SAR-independent.
- A loop can also raise precision simply by suppressing claims. This is why the comparison must be at matched recall or by area under the precision–recall curve, not at a single operating point.

**What would weaken or refute it.**
- No precision gain at matched recall refutes H2.
- If the threshold-only baseline matches the verified agent, the loop adds nothing beyond a threshold map, which weakens the agentic contribution.
- A recall collapse that makes reports less useful than the unverified ones also weakens it.

**Criteria evaluation.**
1. **Importance (H):** hallucinated change claims are a central barrier (Zuo et al., 2026; Xuan et al., 2025).
2. **Novelty (M):** Zuo et al. already apply CVA calibration to bitemporal change-detection MLLMs. Extension to multi-temporal SAR + panchromatic agent reports is not covered in the supplied evidence.
3. **Testability (H).**
4. **Data feasibility (H).**
5. **Spatial relevance (M):** claims are spatial and temporal, but the treatment acts on LLM behaviour.
6. **Tractability (H):** it reuses RQ1's tools and needs no training.
7. **Validation (H, conditional on a SAR-independent reference).**

---

### RQ3 (Rank 3): Do SAR temporal change-type classes transfer to a new AOI, and does an agent interpret them better than a lookup?

**Research question.**
- Reproduce on Sentinel-1 in a different AOI the eight temporal change classes of Lee et al. (2026): unchanged, complex, down step, up step, spike impulse, long impulse, regular cycle and irregular cycle. Do they correspond to construction-related stages identified independently from panchromatic/optical imagery and records?
- Does an LLM agent that combines the class, the backscatter profile and panchromatic image chips assign stage labels more accurately than a fixed class-to-stage lookup table?

**Candidate hypotheses.**
- **H3a (transfer).** The associations reported by Lee et al. (2026), up-step with building construction and down-step with land clearing, hold in the new AOI, with association strength (e.g., Cramér's V) above a pre-set value.
- **H3b (agent).** The agent's stage labels achieve higher macro-F1 than the lookup table against the independent reference.

**Expected observable evidence.**
- A class × reference-stage contingency table, with Cramér's V or mutual information.
- Per-stage F1 for agent vs. lookup.
- The class composition of construction vs. non-construction cells.

**Plausible data.**
- Sentinel-1 GRD (GEE) and Landsat 8/9 panchromatic data.
- Reference stages from NAIP, Sentinel-2 or panchromatic visual interpretation, plus dated building footprints or permit records where the AOI has them [citation needed].
- Lee et al. used optical imagery, building footprints and official construction records in their study area.

**Plausible method.**
1. Reimplement the Lee et al. (2026) chain: DespecKS spatiotemporal filtering (two-sample KS test, 95% level), LRT-based change criterion matrix under a Gamma assumption, and spectral clustering.
2. Assign classes, then sample cells stratified by class and label stages blind.
3. Compare the agent with the lookup.
4. Report agreement with Lee et al.'s class definitions as a reproduction check before any transfer claim.

**Main threat to validity: reproduction fidelity.**
- The packet truncates Lee et al. at about one third of the paper, so clustering parameters and class-assignment rules were not visible.
- If the reproduction deviates, a transfer failure cannot be separated from an implementation error.
- **Secondary threat:** differences in orbit direction, incidence angle, building typology and climate between AOIs alter backscatter responses (Hou et al., 2026). This confounds "transfer failure" with "different sensing geometry".

**What would weaken or refute it.**
- Weak class–stage association (below the pre-set threshold) in the new AOI refutes H3a.
- Agent ≤ lookup refutes H3b.
- Failing the reproduction check against Lee et al.'s class definitions means neither hypothesis can be tested as posed.

**Criteria evaluation.**
1. **Importance (M–H):** Lee et al. restrict their semantic claims to the evaluated environments, so external validity is explicitly open.
2. **Novelty (M):** the transfer test and the agent layer are absent from the supplied evidence.
3. **Testability (M–H).**
4. **Data feasibility (M):** the stage reference depends on records in the chosen AOI. Lee et al.'s 1,462-sample reference set has unknown availability.
5. **Spatial relevance (H):** a geographic transfer test.
6. **Tractability (M):** reimplementation risk.
7. **Validation (M):** stage labels from one annotator are coarse.

---

### RQ4 (Rank 4): Does adaptive panchromatic/SAR sensor selection improve onset dating under cloud cover?

**Research question.** For change-onset questions in a cloud-affected AOI, does an agent that can choose between Landsat panchromatic and Sentinel-1 tools:
- (i) reduce data-availability failures (C1 empty collection, C2 no valid pixels; Kao et al., 2026), and
- (ii) reduce onset error relative to a panchromatic-only agent, while being non-inferior to a fixed rule that always queries both sensors?

**Candidate hypotheses.**
- **H4a.** SAR access reduces failures and onset error relative to the panchromatic-only agent, and the gain grows as local clear-sky observation density falls.
- **H4b.** Adaptive selection is non-inferior to always-both at lower tool-call and token cost.

**Expected observable evidence.**
- Failure counts by class.
- Onset error modelled against per-cell clear-observation count (arm × density interaction).
- Tool calls and tokens per question.

**Plausible data.** As RQ1, with per-cell cloud frequency from the Landsat QA band [citation needed].

**Plausible method.**
- Three agent arms: panchromatic-only, adaptive, and always-both.
- Use the same reference, split and paired tests as RQ1.
- Fit a regression of onset error on arm × clear-observation density.

**Main threat to validity: confounding of cloudiness with terrain and land cover.**
- Persistently cloudy cells may also be hilly or vegetated, where SAR layover, shadow and moisture effects degrade the signal (Hou et al., 2026). The moderator effect could therefore reflect terrain, not cloud. Include slope and land cover as covariates.
- The main effect (SAR helps where optical data is missing) is partly predictable by design, so the contribution rests on H4b.

**What would weaken or refute it.**
- Fewer failures but no reduction in onset error weakens H4a. That pattern would suggest SAR false onsets from moisture, speckle or geometry offset the coverage gain.
- Adaptive selection inferior to always-both refutes H4b.

**Criteria evaluation.**
1. **Importance (M).**
2. **Novelty (L–M).**
3. **Testability (H).**
4. **Data feasibility (H).**
5. **Spatial relevance (H):** cloud climatology varies spatially.
6. **Tractability (H):** it is an ablation of RQ1.
7. **Validation (H).**

**Recommendation:** run RQ4 inside RQ1 rather than as a separate paper.

---

## 6. Cross-cutting design requirements (apply to every RQ)

- **Independent reference.** No reference label may be derived from a tool, model or threshold under test. Label blind to outputs, and report intra-rater agreement. A second annotator, if one is available, would allow inter-rater agreement as in Lee et al. (2026).
- **Spatial leakage.** Separate development blocks (prompt engineering, threshold tuning) from test blocks, with a buffer. Test blocks are run once, after freezing.
- **Spatial dependence.** Use spatial-block bootstrap confidence intervals, not i.i.d. intervals.
- **CRS and scale.** Use one projected CRS (local UTM) and a common grid. State the resampling method. Repeat at two cell sizes for MAUP. Make no individual-building claims at 10–15 m.
- **Temporal alignment.** Express all onsets as dates. Score with a tolerance window and report the reference bracket width. Panchromatic and SAR acquisition dates differ and must not be treated as simultaneous.
- **Sampling bias.** Use stratified sampling (change / no-change and, where relevant, change class) with design weights when reporting area-level estimates. Construction AOIs are rare-event settings.
- **LLM non-determinism.** Run repeated trials and report variance. Pin model versions and record run dates.
- **No LLM-as-judge for primary metrics.** Use structured outputs and deterministic scoring. Kao et al. (2026) used an LLM to derive final answers. Avoid that for primary outcomes here.
- **Pre-registration.** Fix hypotheses, metrics, margins and sample size in `outputs/` before the first test-block run.
- **External validity.** With one AOI, no generalisation claim is possible without human approval and, ideally, a second holdout AOI.

### Indicative 8-week schedule (RQ1 + RQ4 ablation)

| Week | Work |
|---|---|
| W1 | Human decisions (AOI, panchromatic source, window, LLM). Verify references. Inventory scenes and clear-sky counts |
| W2 | Reference-labelling protocol, grid, dev/test blocks, pre-registration |
| W3 | Reference labelling. Build the tools |
| W4 | Agent, VLM and pipeline arms on development blocks only |
| W5 | Freeze the design and run the test blocks |
| W6 | Analysis and robustness checks (MAUP, misregistration) |
| W7 | Draft |
| W8 | Review and submission |

The schedule is tight. It assumes no model training and one LLM backbone.

---

## 7. Unresolved issues and missing inputs

1. **AOI not specified.** Every question depends on it, both for reference-data availability and for cloud climatology.
2. **Panchromatic sensor not specified.** Landsat 15 m (assumed) and sub-metre commercial data imply different spatial units, access terms and questions.
3. **Time window not specified.** It must overlap the Sentinel-1 era.
4. **Target phenomenon not specified.** Construction and urban change is my assumption (A4) and needs approval.
5. **No reference or ground-truth source identified.** This is the critical path. Lee et al.'s labelled dataset has unknown availability, and DVL-Bench's label release and licence are unverified.
6. **LLM backbone, API budget and GPU access not specified.** These affect the number of arms and repeats, and whether EarthDial or TEOChat can be run locally.
7. **All 10 references are "NOT yet verified"** by the human.
8. **Evidence truncated at 20,000 characters per paper.** Results and limitations sections are mostly unseen, e.g., Zuo et al.'s quantitative results, Lee et al.'s full clustering procedure, and EarthDial's multi-temporal SAR capability.
9. **Target journal not specified.** This affects scope, length and whether a negative H1c result is publishable as framed.
10. **Single annotator.** Inter-rater reliability cannot be established without a second annotator.
11. **No human decisions or prior reviewer feedback recorded.**

## 8. Suggested next scientific action

1. **Human decisions:** choose the AOI, panchromatic source, time window and target phenomenon. Approve or reject assumption A4. Verify the 10 references.
2. **One- to two-day feasibility check before committing to RQ1:**
   - For the chosen AOI and window, count Sentinel-1 scenes per track and Landsat panchromatic scenes with clear-sky fraction per cell.
   - Confirm that an independent reference source exists (Sentinel-2/NAIP coverage, dated footprints or permits) that can bracket construction onset to within a few months.
   - Confirm that at least one direct-VLM baseline (EarthDial or TEOChat) runs on the available compute.
3. If the check passes, pre-register RQ1 (with RQ4 as an ablation) and pass it to Stage 2.

---

## 9. References cited (supplied evidence; all marked NOT yet human-verified)

- Feng, P., Lv, Z., Ye, J., Wang, X., Huo, X., Yu, J., Xu, W., Zhang, W., Bai, L., He, C., & Li, W. (2026). Earth-Agent: Unlocking the full landscape of earth observation with agents. ICLR 2026. OpenReview: dkIXAbWuxO
- Hou, Y., Wu, H., Zhang, Y., Liu, X., Ren, C., Lu, W., Yu, H., Huang, Y., Diao, W., Wang, Y., Li, Y., Han, B., & Sun, X. (2026). SAR foundation models: A comprehensive review of data, models, and applications. Science China Information Sciences, 69(8), 180301. DOI: 10.1007/s11432-026-5040-3
- Irvin, J. A., Liu, E. R., Chen, J. C., Dormoy, I., Kim, J., Khanna, S., Zheng, Z., & Ermon, S. (2025). TEOChat: A large vision-language assistant for temporal earth observation data. ICLR 2025. OpenReview: pZz0nOroGv
- Kao, C.-H., Zhao, W., Lam, C., Umap, A., Revankar, S., Speas, S., Bhagat, S., Datta, R., Phoo, C. P., Mall, U., Vondrick, C., Bala, K., & Hariharan, B. (2026). Towards LLM agents for earth observation. Findings of ACL 2026, 2597–2611. DOI: 10.18653/v1/2026.findings-acl.124
- Lee, B., Lee, Y.-K., & Kim, S.-W. (2026). Change type analysis for urban construction using time-series SAR data. IEEE JSTARS (early access). DOI: 10.1109/JSTARS.2026.3737141
- Michel, J., & Inglada, J. (2026). Temporal attention multi-resolution fusion of satellite image time-series, applied to Landsat-8/9 and Sentinel-2: All bands, any time, at best spatial resolution. Remote Sensing of Environment, 334, 115159. DOI: 10.1016/j.rse.2025.115159
- Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. Remote Sensing of Environment, 334, 115239. DOI: 10.1016/j.rse.2026.115239
- Soni, S., Dudhane, A., Debary, H., Fiaz, M., Munir, M. A., Danish, M. S., Fraccaro, P., Watson, C. D., Klein, L. J., Khan, F. S., & Khan, S. (2025). EarthDial: Turning multi-sensory earth observations to interactive dialogues. CVPR 2025, 14303–14313. DOI: 10.1109/CVPR52734.2025.01334
- Xuan, W., Wang, J., Qi, H., Chen, Z., Zheng, Z., Zhong, Y., Xia, J., & Yokoya, N. (2025). DynamicVL: Benchmarking multimodal large language models for dynamic city understanding. NeurIPS 38 (Datasets and Benchmarks Track), 37321–37339. DOI: 10.52202/085713-1114
- Zuo, L., Sun, J., Li, J., Liu, F., Li, J., & Niu, G. (2026). Hallucination-resistant change detection in multimodal large models for autonomous land management agents. IEEE JSTARS, 19, 6313–6327. DOI: 10.1109/JSTARS.2026.3656403

Items marked [citation needed] are needed for: Landsat 8/9 panchromatic band specification and QA cloud mask; Sentinel-2 L2A; DEM-based SAR layover/shadow masking; dated building-footprint and permit datasets; Sentinel-1 constellation revisit changes.
