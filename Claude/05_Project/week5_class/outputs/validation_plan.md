# Validation Plan: methodology_v1 (with data/tool plan)

Source: prompt packet only; no web or other files. Approved question unchanged: does a tool-grounded LLM agent detect new buildings in 100 m cells (presence, onset) more accurately than a VLM and non-agent baselines on held-out SpaceNet 7 AOIs, using Landsat-8 band 8 at 15 m resolution (plus Sentinel-1)? Nothing has been run yet; every row below is planned. Self-review by an LLM is not independent validation.

## 1. Validation table

| What is validated | Check | Supporting evidence | Falsifying / weakening evidence |
|---|---|---|---|
| Provenance | Log MuRA-T version, Sentinel-1 scene IDs, label release, model IDs; hash code, prompts, tools | Every score traces to a logged scene, hash and pinned model ID | Unlogged scenes; model or preprint version changes mid-test (TO VERIFY) |
| Co-registration (input QA, C4) | Week-2 offset in metres between MuRA-T, Sentinel-1 and labels; edge-buffer rescoring | Offsets below one 15 m pixel; results unchanged with edge buffer | Offset of one 15 m pixel or more; rankings change under edge buffer. Pass threshold not stated (MISSING EVIDENCE) |
| Sentinel-1 consistency | Scenes, orbit, polarisation per AOI | At least 10 AOIs with one orbit/polarisation and an acquisition at each of the 8 dates | Fewer than 10 consistent AOIs: pivot to panchromatic primary |
| Cloud mask / availability flag | Cross-check flags against mask; inspect clear/cloudy strata | Flags match mask on development AOIs | Mask accuracy unknown (TO VERIFY); flag errors bias the optical-availability stratum |
| Label rasteriser and tools (process) | Synthetic chips: planted 450 m² footprint, one-pixel shift at 15 m pixels; hand-check cells; rerun gives identical outputs; hashes unchanged after freeze | Planted area recovered in the right cell; deterministic reruns | Area or presence mismatch; any tool edit after freeze |
| Leakage | Whole-AOI holdout audit; chip renderer strips IDs/coordinates (C7); coding assistant barred from test labels | Logs show no test-AOI data in prompts, thresholds or fitting | Any test-AOI access. Pretrained-model exposure to public SpaceNet 7 cannot be ruled out (MISSING EVIDENCE) |
| Agent grounding | Compare values cited in justifications with logged tool output | Cited values match logs | Cited values absent from logs (invented tool evidence) |
| Baseline fairness | VLM must beat majority floor on development AOIs; SAR ingestion check | VLM clearly above floor | VLM at floor (inflates H1); no VLM ingests SAR (MISSING EVIDENCE) |
| Information vs agency (C3) | Tool-fed LLM arm without tool calls vs agent | Agent presence F1 above tool-fed arm | Equal presence F1: gain is tool information, not agency |
| H1 (primary) | Agent − VLM presence F1 and fabrication rate; AOI-cluster bootstrap 95% confidence intervals; paired per-AOI permutation test | Presence F1 difference interval above 0 and fabrication rate difference interval below 0 | Agent presence F1 ≤ VLM presence F1; fabrication gain only with recall collapse |
| H2 | Agent − best-rule presence F1, lower 95% bound; tool-disagreement stratum | Lower bound above −0.05 F1; positive in disagreement stratum | Lower bound at or below −0.05 F1: rules suffice |
| Onset | Absolute error in date steps (C5); exact-date agreement | Agent onset error below VLM and rules | Errors explained by label visibility lag, not detection |
| Spatial sanity | Map claims vs labels per test AOI; 100 vs 200 m cells; 50 m offset; AOI-level inference only | Claims sit on labelled growth; ranking stable across cell size and offset | Ranking reverses under 200 m cells or offset (MAUP) |
| Sensitivity | A_min ∈ {225, 450, 900 m²}; two prompt paraphrases; 3-run spread; pan vs pan+SAR | Sign of presence F1 difference stable across all | Sign flips at any A_min or paraphrase; run-to-run spread in presence F1 exceeds the difference |
| Power (C1) | Power simulation with available test AOIs | Interval width allows detecting the expected presence F1 difference | Interval too wide: result inconclusive, not support |
| External validation | Blinded human audit on about 4 m imagery (label-audit disagreement rate); 3–5 out-of-selection AOIs with frozen prompts and rules | Low label-audit disagreement rate; ranking holds out of selection | Audit finds labels missing real buildings (fabrication rate overstated); ranking reverses on low-growth AOIs. Second label source MISSING EVIDENCE |
| Claim audit | Every write-up claim traced to a metric with an interval | No single-building claims; scope limited to SpaceNet 7-type sites, 2017–2020 | Claims beyond tested AOIs, period or 15 m resolution |

## 2. Primary falsification criterion

H1 is falsified if, on held-out test AOIs at the pre-registered A_min = 450 m², the agent's presence F1 score is less than or equal to the VLM's, or its lower fabrication rate comes only with a presence recall below the VLM's (recall collapse).

## 3. Levels of confidence

- **Generated:** the questions, methodology, tool plan, this plan, and agent/VLM justifications. Plausible text, not evidence. All current content is at this level.
- **Verified by workflow:** synthetic-chip tests, freeze hashes, co-registration gate, leakage audit, grounding check, hand-recomputed scoring. Checks the pipeline, not H1. None run yet.
- **Validated by evidence:** held-out presence F1 differences with AOI-cluster intervals, blinded human label audit, out-of-selection AOIs, stable sensitivity results. None obtained; one label source limits this level.
