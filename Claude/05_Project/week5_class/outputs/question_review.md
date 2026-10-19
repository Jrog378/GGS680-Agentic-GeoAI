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
