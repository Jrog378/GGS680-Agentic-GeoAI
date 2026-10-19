# Stage 5: Methodology Critic: Review of Methodology v1

- **Source packet:** `outputs/prompt_packets/05_methodology_critic.md`
- **Inputs used:** H3 (selected question, hypothesis, scope); form A1–A3 and human notes; `outputs/methodology_v1.md` (§1–§12); the L1 reference list. Evidence excerpts were not re-read in depth because of time limits; no claim below depends on them.
- **Assumptions:** No data exist yet; all critiques concern the design as written. Agreement between this review and earlier LLM stages is not validation (AGENTS.md rule 4).

## Critiques (most important first)

1. **The core hypothesis cannot be falsified against P1/P2.** *(§5 key secondary; H3 hypothesis)* **Severity: blocking.**
   H3 claims the agent is "at least as accurate" as P1/P2, but §5 uses "estimation framing, no δ". Without a margin, every CI that includes 0 counts as success, so no result can refute "at least as accurate".
   *Action:* Pre-register a non-inferiority margin δ on presence-F1 (and on balanced accuracy) for agent − P2, plus the decision rule, before W4.

2. **The agent − VLM comparison mixes up tool grounding with access to tuned detectors.** *(§3 step 5, §4 arms A and V)* **Severity: major.**
   The agent receives numbers from a pretrained CNN and an LRT tuned on development AOIs. The VLM gets only rendered pixels, with no equivalent tuning budget. A win for A could come from the detectors, not from grounding or reasoning. Render choices (stretch, side-by-side layout) also affect V only (§11.1).
   *Action:* Give V an equal development-AOI budget for prompts and rendering. Add a "VLM + tool text" arm on a subsample, or state that agent − P2 is the only contrast that isolates reasoning.

3. **Too few clusters for the planned inference.** *(§2, §5 "Few clusters", §7.2)* **Severity: major.**
   The AOI is the independent unit, and there are 8–14 test AOIs. Cluster-bootstrap coverage with that few clusters is not supported [citation needed, as §5 already notes]. The W3 power simulation sets the number of cells, but the AOI count, which is the binding constraint, is fixed in W1.
   *Action:* Run the power simulation over AOIs and state the minimum detectable presence-F1 difference. Pre-specify a few-cluster method [citation needed]. Move as many eligible AOIs as possible to test.

4. **The target is poorly defined at 15 m resolution, and onset scoring is biased.** *(§2 target variables, §6 scale and temporal alignment)* **Severity: major.**
   A 100 m cell covers about 7 × 7 pixels at 15 m resolution. Labels are traced on about 4 m Planet imagery, and A_min is not set, so "presence" may include change that no arm can see in the 15 m pixels. Onset is resolved only to an interval of about 3 months. Labels mark visibility, while SAR change is expected to come first (§6), so SAR-driven arms will be scored as systematically early. Sentinel-1 is co-registered by hand, and its registration error is not reported.
   *Action:* Fix A_min on development AOIs from what the tools can detect in 15 m pixels. Report Sentinel-1 co-registration RMSE. Add a ±1-interval onset tolerance as a pre-registered secondary score.

5. **The fabrication endpoint favours the agent by design.** *(§3 step 7 unanswerable queries; §5 fabrication rate)* **Severity: major.**
   The unanswerable queries are mostly cloud-masked or missing chips, or date indices outside 1–8. The agent has a data-availability tool that reports these cases directly, while the VLM has to infer them from pixels. About 10 queries per AOI also gives very few fabrication events.
   *Action:* Build unanswerable queries that are equally detectable by both arms. Report the fabrication rate (share of non-abstaining answers) by query type. Include these queries in the power simulation.

6. **Leakage controls cover the agent but not the VLM.** *(§4 C1, §5 memory leakage, §6 spatial autocorrelation)* **Severity: major.**
   C1 checks only the agent. No packet evidence shows whether the candidate VLMs were trained on SpaceNet 7 imagery or nearby imagery [missing evidence]. Sampled cells only one cell apart have heavily overlapping 1 km chips. Clustered inference handles this, but it makes the effective sample within an AOI smaller.
   *Action:* Add a blank-image or shuffled-chip control for V. Document the training data of the chosen VLM and CNN. Increase spacing between sampled cells or report the chip overlap.

7. **Abstention handling and the primary metric are not yet fixed.** *(§3 step 6, §5 primary endpoint)* **Severity: major.**
   The design does not say how "abstain" counts in presence-F1. If abstentions are dropped, an arm can raise its F1 by abstaining on hard cells. Design-weighted F1 also depends on how the sample is allocated (X11). The primary endpoint still awaits Justin's confirmation.
   *Action:* Pre-register how abstentions are scored (count as wrong, or report a coverage–accuracy curve). Make balanced accuracy co-primary or the fixed secondary. Confirm the primary endpoint before W1 ends.

8. **The eight-week plan has no slack.** *(§12)* **Severity: major.**
   W1 has a lot of serial work: downloads, Sentinel-1 export and hand co-registration across 10–20 AOIs, choosing the VLM and CNN, and drafting the pre-registration. W2 has to build and validate five tools, including a new LRT adaptation (X13). There is no buffer week, and only two weeks are left for drafting and revision.
   *Action:* Add a go/no-go gate at the end of W2. Make C2, the CNN and the SAR-only secondary optional by default. Use a hosted VLM from W1. Keep one week as a buffer.

## Unresolved issues

VLM and CNN choice; A_min, guard bands, ±15-day tolerance, API cap; δ; whether enough test AOIs and conflict cells exist (needs the W1 inventory). External validation is impossible with MUDS as the only reference.

## Next scientific action

Justin sets δ, the abstention rule and the primary endpoint. Then the W1 inventory provides the number of eligible AOIs that the power simulation needs.

## Verdict: REVISE

The design has strong parts: the AOI-level holdout, the information-matched P2 baseline and the deterministic scoring. It needs a falsifiable non-inferiority margin, fairer arms for the agent − VLM and fabrication contrasts, and power at the AOI level before W4. The eight-week schedule is feasible only if the optional arms are cut and a W2 gate is added.
