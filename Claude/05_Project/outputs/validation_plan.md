# Stage 7: Validation Agent: Validation Plan

- **Source packet:** `outputs/prompt_packets/07_validation_agent.md`
- **Inputs used:** H3; H7 (all 8 critiques accepted); H1 (latest rows override earlier ones); `methodology_v1.md` (revision); `data_tool_plan.md`; `methodology_review.md`. Evidence excerpts not re-read (time limit).
- **Status:** Plan only. No data downloaded, no results exist, so nothing below is VERIFIED yet. This is LLM self-review, not independent validation (rule 4).

## 1. Validation checks

| What is validated | Check | Supports the claim | Falsifies / weakens it |
|---|---|---|---|
| Provenance | Packets, prompts, code, area split and pre-registration version-controlled; pre-registration dated before any test run | Frozen prompts, rules, A, δ, abstention scoring, sample before test outputs exist | Any prompt, threshold or δ changed after test outputs were seen |
| Input QA: panchromatic | Cloud mask; relative radiometric normalisation on pseudo-invariant pixels | Pseudo-invariant pixels show no trend after normalisation | Residual trend that tracks predicted "change" (pseudo-change) |
| Input QA: Sentinel-1 | One orbit track per area; co-registration RMSE (metres) per area | RMSE well under one 15 m pixel | RMSE of a pixel or more; results driven by high-RMSE areas |
| Detectability | A (min. new-footprint m²) fixed on development areas from what 15 m pixels show | Tools' standalone presence-F1 rises with change size; results reported by size | No size at which tools detect change reliably (fails W2 gate) |
| Process: tools | Standalone presence-F1 and onset error of SAR and panchromatic tools on development areas; synthetic rasters with known change | Tools beat the trivial baseline in balanced accuracy | Tools near chance; agent then has nothing to ground on |
| Process: scoring | Deterministic scorer, no LLM grader; abstentions on answerable cells scored wrong | Scorer reproduces hand-checked answers | Scoring rule edited after outcomes |
| Leakage | C1 (tools-disabled agent), C2 (blank-image VLM); opaque cell IDs; VLM/CNN training data documented (no SpaceNet 7) | C1 and C2 balanced accuracy near the trivial baseline | C1 or C2 balanced accuracy well above trivial |
| Spatial sanity | One-pixel shift; 200 m grid (MAUP); layover tolerance of one neighbour along look direction; cells ≥ 300 m apart | Agent − VLM and agent − P2 differences keep sign and similar size | Differences flip or vanish under shift, 200 m grid or layover check |
| Main contrast (co-primary) | Agent − VLM in presence-F1 and balanced accuracy, area-cluster CI (few-cluster method), whole held-out areas | Lower CI bound > 0 on both | CIs include 0 on both, or VLM higher |
| Reasoning vs tool access | Agent − VT; agent − P1; agent − P2 non-inferiority (presence-F1 and balanced accuracy, margin δ) | Agent non-inferior to P2 (lower CI bound > −δ); agent > VT | Agent fails non-inferiority vs P2; VT matches agent (gain is tool access, not reasoning) |
| Fabrication | Unanswerable queries detectable by both arms; fabrication rate (share of non-abstaining answers) by query type | VLM fabrication rate higher than agent's | VLM fabrication rate no higher than agent's |
| Onset | Exact-interval and ±1-interval onset accuracy; label-lag distribution | Agent ±1-interval onset accuracy ≥ VLM's | Onset accuracy at chance, or lag so wide onset is unscoreable |
| Repeatability | Answer agreement across 3 repeats per arm | High agreement; conclusions unchanged across repeats | Low agreement; sign of agent − VLM difference changes across repeats |
| External validity | None possible (MUDS / SpaceNet 7 only) | n/a | Stated as a limitation; no transfer claim |

## 2. Primary falsification criterion

The main claim is falsified if, on the held-out test areas under the pre-registered protocol, the agent − VLM difference has an area-cluster confidence interval that includes or lies below 0 for both co-primary metrics (presence-F1 and balanced accuracy), or the agent fails pre-registered non-inferiority against the fitted rule P2 (lower CI bound of agent − P2 presence-F1 at or below −δ).

## 3. Three levels of confidence

| Level | Status now |
|---|---|
| **What the agents generated** | Question, hypothesis, methodology v1, critique, data/tool plan and this plan. All LLM outputs; agreement among them is not evidence. Open placeholders: δ, A, n, API cap, VLM/CNN choice, few-cluster method [citation needed], radiometric normalisation [citation needed], Sentinel-1 licence (TO VERIFY). |
| **What the workflow verified** | Only process facts: human checkpoints H3/H4/H7 passed; references L1 human-verified; H1 rows drafted by Claude and not yet reviewed by Justin. No data downloaded, no tool validated, no result produced. |
| **What evidence would validate** | W1 inventory with enough eligible areas; W2 gate passed (tools beat trivial balanced accuracy at 15 m resolution; Sentinel-1 RMSE under one 15 m pixel); dated pre-registration before test runs; C1/C2 near trivial; co-primary CIs above 0; P2 non-inferiority met; lower agent fabrication rate (share of non-abstaining answers); results stable under shift, 200 m grid, layover and repeats. Even then, claims stay limited to these SpaceNet 7 areas, these models and curated tools (no external validity; human approval needed per rule 9). |

**Unresolved:** δ and A undefined until pilot; whether ≥ 8 test areas exist; VT only on a subsample (power unclear).
**Next action:** run the W1 inventory, then the area-level power simulation to fix A, δ and n.
