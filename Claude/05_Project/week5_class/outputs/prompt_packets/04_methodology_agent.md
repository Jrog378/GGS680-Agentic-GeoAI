# AGENT ROLE

# 🧭 Methodology Agent

## Role
You are a GeoAI methodologist.

## Goal
Design a methodology that can actually test the approved research question/hypothesis.

## Required components
1. unit of analysis;
2. study area and temporal scope;
3. dependent/target variables;
4. explanatory/predictor variables;
5. data provenance and resolution;
6. preprocessing;
7. model/algorithm;
8. baseline/comparator;
9. spatial train/test or cross-validation strategy;
10. uncertainty/sensitivity analysis;
11. external validation;
12. stopping/decision criteria.

## GeoAI-specific checks
Explicitly consider:
- CRS and units;
- spatial autocorrelation;
- spatial/temporal leakage;
- scale/resolution mismatch;
- MAUP/ecological inference where relevant;
- spatial sampling bias;
- transferability beyond the study area.

## Output
Write `methodology_v1.md` plus a short list of assumptions most likely to change the conclusion.


# CURRENT TASK

Design a GeoAI methodology capable of testing the approved hypothesis.

# CURRENT RESEARCH STATE / EVIDENCE

## FILE: inputs/problem.md

# Broad research problem

How can Agentic GeoAI help interpret large sources of satellite imagery in an area of interest to understand patterns and changes over time?

## Initial boundary conditions

- The problem must contain a meaningful spatial component.
- The investigation should be achievable with public or research-accessible data.
- The aim is to produce a testable research question, not merely a descriptive mapping exercise.
- The methodology must contain an explicit validation strategy.
- The paper must be completable and submittable to a peer-reviewed journal within eight weeks, using AI-assisted coding and analysis.

## Human notes

I am hoping to use panchromatic (black-and-white) and SAR imagery to start. Proposed data (found with Claude Code on 2026-10-04 at my request; to be confirmed after download):

- **Panchromatic time series: MuRA-T** (Purdue Robot Vision Lab, https://engineering.purdue.edu/RVL/Database/murat/index.html).
  - **What it is:** monthly Landsat-8 and Sentinel-2 stacks added to the 60 SpaceNet 7 training AOIs worldwide.
  - **Time span:** about 24 months per AOI between 2017 and 2020. Each month uses the least-cloudy Landsat scene; some months are missing.
  - **Bands:** Landsat-8 OLI band 8 (panchromatic, 15 m, 0.50–0.68 µm) is included, along with bands 1–11, the QA band and a cloud mask.
  - **Alignment:** all bands are already co-registered to the SpaceNet 7 grid; the authors report sub-pixel alignment.
  - **Product and size:** Landsat Collection 1 Level-1 (L1TP). The Landsat archive is 1.5 GB and the Sentinel-2 archive 5.3 GB.
  - **Status:** GPL v3. It is described in a 2023 arXiv preprint (not peer-reviewed), so I treat it as a data source, not a reference.
- **Reference labels: SpaceNet 7 / MUDS** (the public, monthly-labelled dataset described by Qu et al., 2026).
  - **What it is:** monthly building-footprint polygons for the same AOIs, traced on about 4 m Planet RGB mosaics.
  - **Dating:** each building keeps one ID across months, so the month it first appears can be dated.
  - **Licence and access:** CC BY-SA 4.0, free on AWS Open Data (`spacenet-dataset` bucket).
  - **Independence:** the labels are traced on different imagery from the panchromatic and SAR data, so they are independent of both.
  - **Caveat:** a label marks when a building becomes visible, which is closer to completion than to the start of construction.
- **SAR: Sentinel-1 C-band GRD** for the same AOIs and months.
  - **Work needed:** I must download it and co-register it to the MuRA-T grid myself, e.g. from Google Earth Engine (`COPERNICUS/S1_GRD`) or Planetary Computer (`sentinel-1-rtc`).
  - **Coverage:** Sentinel-1A and 1B were both operating in 2018–2020. The number of scenes, the orbit direction and the polarisations vary by AOI (TO VERIFY per AOI).
- **Study area:** a subset of the 60 AOIs (e.g. 10–20), chosen for the most new buildings and the best Sentinel-1 coverage. Whole AOIs will be held out for testing, so training and test areas never overlap.
- **Time period:** the SpaceNet 7 window (about 24 monthly steps per AOI, 2017–2020).
- **Change of interest:** new buildings and urban development, which is what SpaceNet 7 labels.
- **Fallback if MuRA-T doesn't work:** Landsat 8/9 Collection 2 band 8 for the same AOIs, from USGS Level-1 products (EarthExplorer or the AWS `usgs-landsat` bucket) or Earth Engine's TOA collections. I would then co-register it myself. Level-2 surface reflectance products have no panchromatic band.

### References the agents may cite (read and verified by Justin; full PDFs in Claude/05_Project/evidence/)

- Soni, S., Dudhane, A., Debary, H., Fiaz, M., Munir, M. A., Danish, M. S., Fraccaro, P., Watson, C. D., Klein, L. J., Khan, F. S., & Khan, S. (2025). EarthDial: Turning multi-sensory earth observations to interactive dialogues. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 14303–14313. DOI: 10.1109/CVPR52734.2025.01334
- Irvin, J. A., Liu, E. R., Chen, J. C., Dormoy, I., Kim, J., Khanna, S., Zheng, Z., & Ermon, S. (2025). TEOChat: A large vision-language assistant for temporal earth observation data. International Conference on Learning Representations (ICLR 2025). OpenReview: pZz0nOroGv
- Xuan, W., Wang, J., Qi, H., Chen, Z., Zheng, Z., Zhong, Y., Xia, J., & Yokoya, N. (2025). DynamicVL: Benchmarking multimodal large language models for dynamic city understanding. Advances in Neural Information Processing Systems 38 (Datasets and Benchmarks Track), 37321–37339. DOI: 10.52202/085713-1114
- Hou, Y., Wu, H., Zhang, Y., Liu, X., Ren, C., Lu, W., Yu, H., Huang, Y., Diao, W., Wang, Y., Li, Y., Han, B., & Sun, X. (2026). SAR foundation models: A comprehensive review of data, models, and applications. Science China Information Sciences, 69(8), 180301. DOI: 10.1007/s11432-026-5040-3
- Zuo, L., Sun, J., Li, J., Liu, F., Li, J., & Niu, G. (2026). Hallucination-resistant change detection in multimodal large models for autonomous land management agents. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 19, 6313–6327. DOI: 10.1109/JSTARS.2026.3656403
- Feng, P., Lv, Z., Ye, J., Wang, X., Huo, X., Yu, J., Xu, W., Zhang, W., Bai, L., He, C., & Li, W. (2026). Earth-Agent: Unlocking the full landscape of earth observation with agents. International Conference on Learning Representations (ICLR 2026). OpenReview: dkIXAbWuxO
- Kao, C.-H., Zhao, W., Lam, C., Umap, A., Revankar, S., Speas, S., Bhagat, S., Datta, R., Phoo, C. P., Mall, U., Vondrick, C., Bala, K., & Hariharan, B. (2026). Towards LLM agents for earth observation. Findings of the Association for Computational Linguistics: ACL 2026, 2597–2611. DOI: 10.18653/v1/2026.findings-acl.124
- Lee, B., Lee, Y.-K., & Kim, S.-W. (2026). Change type analysis for urban construction using time-series SAR data. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing (early access; volume/pages not yet assigned). DOI: 10.1109/JSTARS.2026.3737141
- Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. Remote Sensing of Environment, 334, 115239. DOI: 10.1016/j.rse.2026.115239
- Michel, J., & Inglada, J. (2026). Temporal attention multi-resolution fusion of satellite image time-series, applied to Landsat-8/9 and Sentinel-2: All bands, any time, at best spatial resolution. Remote Sensing of Environment, 334, 115159. DOI: 10.1016/j.rse.2025.115159


## Human decision after stages 1–2 (Justin, the human supervisor)

The course critic recommended a fusion question (R1) and rejected the agent-vs-multimodal-model question (R3) as primary. I keep my own selection, from my Assignment 3 decision log (H3), and take the critic's fusion question as a secondary analysis, run both ways:

- Selected question (final wording): In held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery and than non-agent baselines given the same tool outputs?
- Why it is the strongest of the three: It answers my core interest (VLMs vs tool-grounded agents) and the broad problem. The baselines isolate what the agent's reasoning adds. It is feasible at test level with existing labels. Q-B becomes a pipeline-first secondary analysis, and Q-C is deferred (fine, just not my favourite).
- Main hypothesis: Tool grounding reduces hallucination. The tool-using agent is more accurate than the VLM and fabricates fewer answers. Against non-agent baselines given the same tool outputs (a tuned rule and a fitted rule), it is at least as accurate (difference reported with an AOI-cluster confidence interval) and better where the tools disagree.
- Scope (study area, time period, unit of analysis): 10–20 MuRA-T / SpaceNet 7 areas (whole areas held out for testing), monthly 2017–2020, 100 m cells. The LLM agent and the VLM get exactly the same inputs: the same 1 km image chip (centred on the 100 m square being asked about, with that square outlined; Landsat-8 panchromatic at 15 m resolution, Sentinel-1 at 10 m pixel spacing, about 20 m resolution), the same 8 dates and the same question. New buildings only: development visible at 15 m resolution, not single houses. A test-level study on a stratified sample of cells.
(Wording drafted by Claude from Justin's decisions; approved by Justin 2026-10-04.)


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


## FILE: outputs/question_review.md

# Scientific Critic Review: Candidate Research Questions

Source: prompt packet only (`inputs/problem.md`, `outputs/research_questions.md`). Reference contents are not in the packet, so novelty is unassessed (MISSING EVIDENCE).

## Scores (1–5)

| Dimension | R1 Pan+SAR fusion | R2 SAR lead time | R3 Agent vs direct MLLM | R4 Min. footprint |
|---|---|---|---|---|
| Importance | 4 | 4 | 4 | 3 |
| Novelty/evidence gap | 2 (unassessed) | 2 (unassessed) | 2 (unassessed) | 2 (unassessed) |
| Testability | 4 | 4 | 3 | 4 |
| Identification strategy | 3 | 3 | 2 | 2 |
| Data adequacy | 3 | 3 | 2 | 3 |
| Spatial validity | 3 | 3 | 3 | 2 |
| Robustness/validation | 4 | 3 | 2 | 3 |
| Feasibility (8 weeks) | 4 | 3 | 2 | 4 |

## Rank 1: Pan+SAR fusion vs pan-only

**ISSUE 1: Label-to-pixel rule undefined**
- LOCATION / TARGET: R1 data/method; "Missing evidence" list.
- SEVERITY: blocking
- WHY IT MATTERS: Buildings traced on ~4 m imagery are often smaller than one 15 m pixel (225 m²). The covered-fraction threshold defines the positive class and can decide whether fusion "wins."
- EVIDENCE NEEDED: Distribution of new-building footprint area and per-pixel covered fraction in candidate AOIs.
- RECOMMENDED ACTION: Fix the threshold before any model run; report 2–3 pre-set thresholds as sensitivity analysis. Consider 3×3 blocks of 15 m pixels as a secondary scoring unit.

**ISSUE 2: Mechanism confounded with optical gaps and SAR coverage**
- LOCATION / TARGET: R1 hypothesis ("SAR unaffected by cloud gaps"); threat to validity.
- SEVERITY: major
- WHY IT MATTERS: A fusion gain could come from filling missing MuRA-T months, SAR structural signal, or good Sentinel-1 coverage; the design does not separate these.
- EVIDENCE NEEDED: Per-AOI Sentinel-1 scene count, orbit direction and polarisation (TO VERIFY); per-month optical availability from the MuRA-T cloud mask.
- RECOMMENDED ACTION: Make the clear-month vs missing/cloudy-month stratification a primary test, not a footnote. Select AOIs with consistent orbit/polarisation or model coverage as a covariate.

**ISSUE 3: Inferential unit and power**
- LOCATION / TARGET: R1 "paired comparison per AOI"; 10–20 AOIs.
- SEVERITY: major
- WHY IT MATTERS: Pixels within an AOI are spatially autocorrelated, so pixel-level tests overstate certainty. The effective sample is 10–20 held-out AOIs, giving low power.
- EVIDENCE NEEDED: Expected F1 difference and between-AOI variance in F1.
- RECOMMENDED ACTION: Keep leave-AOI-out; test per-AOI F1 differences (e.g., Wilcoxon signed-rank) with bootstrap confidence intervals over AOIs; pre-state the minimum meaningful F1 gain.

**ISSUE 4: Temporal target and Level-1 radiometry**
- LOCATION / TARGET: "new-building pixel in month t"; MuRA-T is Collection 1 Level-1 (L1TP).
- SEVERITY: major
- WHY IT MATTERS: Labels mark visibility (closer to completion), so exact-month scoring penalises earlier true detections. Level-1 panchromatic values shift with sun angle and season, creating false change.
- EVIDENCE NEEDED: Lag between detections and label month; seasonal variation in never-built pixels.
- RECOMMENDED ACTION: Score with a stated ±1-month tolerance and also report exact-month F1; normalise pan values per scene against stable control pixels.

**ISSUE 5: Metric under class imbalance**
- LOCATION / TARGET: R1 hypothesis (F1).
- SEVERITY: minor
- WHY IT MATTERS: New-building pixels are rare; F1 at one operating point can flip with the decision threshold.
- EVIDENCE NEEDED: Positive-class prevalence per AOI.
- RECOMMENDED ACTION: Report F1 plus precision–recall AUC and recall at matched precision.

**ISSUE 6: Single reference; agentic link absent**
- LOCATION / TARGET: R1 overall; problem statement ("How can Agentic GeoAI help…").
- SEVERITY: major
- WHY IT MATTERS: SpaceNet 7 is the only reference, so its errors go unchecked. R1 tests sensor fusion, not an agentic claim, so it only partly answers the problem.
- EVIDENCE NEEDED: A second label source for the same AOIs (none in packet: MISSING EVIDENCE).
- RECOMMENDED ACTION: Hand-check a random sample of labelled and detected events per AOI on the ~4 m imagery. State that the agent runs the workflow (download, co-registration, model runs) but is not the tested hypothesis; add R3 only if time allows.

## Rank 2: SAR lead time before label month

**ISSUE 7: Change-points from acquisition, not construction**
- LOCATION / TARGET: R2 per-pixel change-point method.
- SEVERITY: major
- WHY IT MATTERS: Speckle and month-to-month switches in orbit direction or polarisation can create change-points unrelated to building.
- EVIDENCE NEEDED: Per-AOI Sentinel-1 acquisition consistency (TO VERIFY); false change-point rate in stable control pixels.
- RECOMMENDED ACTION: Use one orbit direction and polarisation per AOI; compare against matched controls from the same AOI and months.

**ISSUE 8: Censoring and possible overlap**
- LOCATION / TARGET: ~24-month window; Lee et al. (2026).
- SEVERITY: major
- WHY IT MATTERS: Buildings labelled early have no pre-period and long build phases are truncated, biasing lead time toward zero. Overlap with Lee et al. (2026) is unknown.
- EVIDENCE NEEDED: Count of new buildings with an adequate pre-label period; Lee et al. (2026) content (MISSING EVIDENCE).
- RECOMMENDED ACTION: Restrict to buildings with a pre-set minimum pre-period; run R2 as a secondary analysis on the R1 stack.

## Rank 3: Agent vs direct multimodal model

**ISSUE 9: Baseline fairness and dependency**
- LOCATION / TARGET: R3 design.
- SEVERITY: blocking (as primary question)
- WHY IT MATTERS: The agent's tools are the R1 detector, so R3 waits on R1. A multimodal model not built for 15 m panchromatic or SAR inputs is a weak baseline; stochastic outputs threaten reproducibility.
- EVIDENCE NEEDED: Whether any listed model accepts these inputs (MISSING EVIDENCE); run-to-run variance.
- RECOMMENDED ACTION: Defer to an optional extension; if run, pin model versions, repeat runs, and report event-level precision and recall together.

## Rank 4: Minimum detectable footprint

**ISSUE 10: Area confounded with density; unit ambiguity**
- LOCATION / TARGET: R4 logistic model.
- SEVERITY: major
- WHY IT MATTERS: In 15 m pixels, adjacent small buildings merge, so building vs cluster detection is ambiguous and area tracks neighbourhood density.
- EVIDENCE NEEDED: Local building density per new building; label positional error relative to the 15 m grid.
- RECOMMENDED ACTION: Define the detection unit before analysis; add local density as a covariate with an AOI random effect. Keep as secondary to R1.

## Required checks

- Falsification: R1 fails if per-AOI F1 shows no gain, or the gain vanishes in clear-sky months.
- Scale: 15 m resolution vs ~4 m labels is the main mismatch; monthly steps match label cadence.
- Autocorrelation/leakage: whole-AOI holdout prevents spatial leakage; inference must be AOI-level.
- Causal claims: not justified; frame R1 as a predictive comparison.
- Alternative explanations: only discriminated if Issue 2 stratification is done.
- Second benchmark: none in packet (MISSING EVIDENCE).
- Answerable with data: R1, R2, R4 yes once MuRA-T and Sentinel-1 are confirmed; R3 uncertain.

## Verdicts

- R1: REVISE (recommended primary)
- R2: REVISE (secondary analysis)
- R3: REJECT as primary (optional extension)
- R4: ACCEPT as secondary, conditional on R1

**Recommended question (revised R1, changes explicit):** In held-out AOIs, does fusing Sentinel-1 backscatter with Landsat-8 panchromatic time series at 15 m resolution raise per-AOI F1 for detecting newly labelled buildings (pre-set pixel-coverage threshold, ±1-month tolerance) above panchromatic alone, and is any F1 gain concentrated in months without a clear optical scene?

## Overall: REVISE

R1 is strongest: independent reference, falsifiable paired comparison, whole-AOI holdout, feasible in eight weeks. It is not testable as written because the label-to-pixel threshold is undefined (blocking), and a fusion gain cannot be attributed to SAR rather than optical gaps or Sentinel-1 coverage without stratification. With 10–20 AOIs, inference is AOI-level and low-powered. Fix threshold and tolerance, stratify by optical availability, verify Sentinel-1 per AOI and audit labels; then accept R1, with R4 and R2 secondary and R3 deferred.


## FILE: outputs/abstract_v1.md

# Abstract v1 (proposed study, no results)

Researchers are building temporal vision-language models (VLMs) and agents for Earth observation (Irvin et al., 2025; Xuan et al., 2025; Feng et al., 2026; Kao et al., 2026), including work on hallucination in change detection (Zuo et al., 2026). Whether grounding an agent in deterministic tools reduces fabricated change claims at 15 m resolution is untested in the supplied evidence (novelty unassessed). This study will ask: in held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery, and than non-agent baselines given the same tool outputs? We will use 10–20 MuRA-T / SpaceNet 7 areas, holding out whole areas for testing. For each sampled cell, the agent and the VLM will receive identical inputs: a 1 km chip centred on the outlined 100 m cell, with Landsat-8 panchromatic at 15 m pixels and Sentinel-1 C-band at 10 m pixel spacing (about 20 m resolution), the same 8 dates and the same question. The non-agent baselines will be a tuned rule and a fitted rule applied to the agent's tool outputs. Reference labels will be SpaceNet 7 monthly building footprints traced on about 4 m Planet imagery, independent of both input sensors. Validation will score a stratified sample of cells by F1 score for presence, onset-month error (exact and ±1 month) and fabrication rate (claimed new-building cells with no labelled building). Differences will be reported with AOI-cluster confidence intervals and stratified by tool agreement. Model versions will be pinned, runs repeated, and a label sample hand-checked. As a secondary analysis, panchromatic-only and panchromatic-plus-SAR inputs will be compared. The expected contribution is a controlled test of what agent reasoning adds beyond direct viewing and the tools themselves.

## Assumptions

- MuRA-T band 8 and its reported sub-pixel alignment are usable as downloaded (preprint claim, to be confirmed).
- Sentinel-1 coverage, orbit direction and polarisation per AOI are adequate (TO VERIFY per AOI).
- "New buildings" means development visible at 15 m resolution, not single houses; labels mark visibility, closer to completion than construction start.
- The label-to-cell rule and the tolerance for onset month will be fixed before testing.
- At least one VLM can accept the panchromatic and SAR chips (MISSING EVIDENCE).
- "Run both ways" is read as running the secondary sensor comparison for both the agent and the VLM (interpretation; to confirm).


# EXECUTION REQUIREMENT

Work only from the supplied state and clearly label missing evidence.
Return the requested structured artifact. Do not silently change the research question.
