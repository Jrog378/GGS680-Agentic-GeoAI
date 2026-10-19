# Methodology Review (Scientific Critic): methodology_v1

Source: prompt packet only (methodology_v1.md, research_questions.md). MISSING EVIDENCE / TO VERIFY items carried from the packet.

**Scores (1–5):** importance 4 · novelty/evidence gap 2 (references not supplied; MISSING EVIDENCE) · testability 4 · identification 3 · data adequacy 3 · spatial validity 3 · robustness/validation 3 · feasibility 2.

## C1. Too few test AOIs for AOI-cluster inference
- **Where:** §2, §9, §12 (H2); Assumption 6.
- **Severity:** blocking (for H2)
- **Why:** 10–20 AOIs minus one third for development leaves about 7–13 test AOIs. A cluster bootstrap over so few clusters under-covers, and a non-inferiority lower bound above −0.05 F1 is unlikely to be reachable, so H2 is inconclusive by design. The tool-disagreement stratum is a small slice of ~60 cells per AOI.
- **Evidence needed:** simulated interval width for presence F1 differences at 7, 10 and 13 test AOIs, using development-AOI variance.
- **Action:** Pre-register a power simulation and minimum detectable F1 difference; use 20 AOIs (5 development) and add a paired per-AOI permutation test.

## C2. Decision rules leave a gap and an unfalsifiable escape
- **Where:** §12.
- **Severity:** major
- **Why:** "Supported" uses confidence intervals but "Refuted" uses the point estimate (agent F1 ≤ VLM F1); an interval spanning 0 with a positive point estimate is neither. No rule refutes H2. "Recall collapse" is undefined, so the fabrication-rate result cannot be falsified. Rankings may flip across A_min ∈ {225, 450, 900 m²} with no rule for that case.
- **Evidence needed:** a written three-outcome rule per hypothesis.
- **Action:** Pre-register supported / refuted / inconclusive for H1 and H2 by CI position; define recall collapse (e.g., agent − VLM recall CI entirely below −0.10 recall); require sign stability across all three A_min values.

## C3. Agent vs VLM confounds information with agency; VLM may be a strawman
- **Where:** §7, §8, H1; Assumption 2.
- **Severity:** major
- **Why:** The agent receives precomputed multi-date change scores; the VLM must infer change visually from panchromatic chips at 15 m resolution it was likely not trained on, and SAR ingestion is MISSING EVIDENCE. A positive H1 shows "derived features help", not "agentic tool use helps". H2 baselines are rules, not an LLM with the same information.
- **Evidence needed:** VLM presence F1 vs the majority-class floor on development AOIs; confirmation one pinned model serves both arms.
- **Action:** Add an LLM arm given the same tool outputs in the prompt without tool calling, and require the VLM to beat the floor on development AOIs before test runs.

## C4. Co-registration and cell-edge error at 15 m pixels
- **Where:** §3 (A_min), §5–6, GeoAI scale check.
- **Severity:** major
- **Why:** MuRA-T sub-pixel alignment is TO VERIFY; SAR at about 20 m resolution is resampled to 15 m pixels; labels are traced on about 4 m imagery. A one-pixel shift moves a 450 m² footprint (two 15 m pixels) across a 100 m cell edge, producing a miss in one cell and a fabrication in its neighbour. The cell-size/offset sensitivity does not isolate this error.
- **Evidence needed:** measured offset (metres) between MuRA-T, Sentinel-1 and label polygons on development AOIs.
- **Action:** Measure registration error on development AOIs; score with an edge buffer (tolerate neighbour-cell matches for footprints within one 15 m pixel of an edge) and report both scorings.

## C5. Label timing penalises correct early detection
- **Where:** §3, §9; Assumptions 3, 5.
- **Severity:** major
- **Why:** SpaceNet 7 marks visibility, not construction start; site clearing can change SAR/pan signals earlier. A cell changing by date 8 but labelled later counts as a fabrication. Eight dates give about a 3-month step, so "±1 month" is near-meaningless.
- **Evidence needed:** count of claimed cells labelled new within a few months after date 8.
- **Action:** Score onset in date steps (exact, ±1 step); report fabrication rate with and without a post-window label-lag tolerance.

## C6. Weak independent validation; unblinded audit
- **Where:** §11.
- **Severity:** major
- **Why:** One label source (second source MISSING EVIDENCE). The audit checks "claimed events", so the auditor sees which system claimed what and may favour fluent agent justifications.
- **Evidence needed:** audit protocol with system identity hidden.
- **Action:** Blind the audit (mix labelled, claimed and random cells; hide source) and report label-audit disagreement rate per stratum.

## C7. Selection and contamination leakage
- **Where:** §2; GeoAI leakage/sampling checks.
- **Severity:** minor
- **Why:** AOIs are chosen by new-building counts from labels, including test AOIs, raising prevalence and inflating F1. Pretrained-model exposure to SpaceNet 7 is unknown; AOI names or coordinates in prompts could cue memorised context.
- **Evidence needed:** prompt audit; prevalence per test AOI.
- **Action:** Strip AOI IDs and coordinates from prompts; report per-AOI prevalence beside F1.

## C8. Eight-week plan lacks go/no-go gates
- **Where:** work plan; §12 pivots.
- **Severity:** major
- **Why:** Weeks 1–2 rest on two TO VERIFY items (MuRA-T alignment, Sentinel-1 consistency). Week 5 runs 3 runs × agent and VLM × pan vs pan+SAR × 2 paraphrases on roughly 400–800 test cells (thousands of multi-turn calls). Any slip erases week 7, which carries the robustness claims.
- **Evidence needed:** per-call cost and time from the week-4 pilot.
- **Action:** Gate: SAR registration verified by end of week 2 or pan becomes primary; run paraphrases and pan+SAR on a subsample; freeze scope after the pilot.

## Verdict: REVISE

The question is important and falsifiable in outline, with a sound whole-AOI holdout. As specified, however, it cannot deliver a decisive answer: too few test AOIs for AOI-cluster intervals and a −0.05 F1 non-inferiority margin (C1), decision rules with an undefined inconclusive zone (C2), and an agent–VLM contrast that confounds information with agency (C3). Spatial validity at 15 m resolution hinges on unverified co-registration (C4), and label timing turns early detections into fabrications (C5). All are fixable on development AOIs; resolve C1–C5 and add the week-2 gate (C8) before freezing the protocol.
