# Data and Tool Plan: methodology_v1 (with review C1–C8)

Source: prompt packet only; no web or other files. Unstated items are TO VERIFY. The approved question is unchanged.

## 1. Datasets

| Name | Role | Access | Licence | TO VERIFY |
|---|---|---|---|---|
| MuRA-T Landsat-8 band 8 panchromatic (Collection 1 L1TP on the SpaceNet 7 grid; 15 m pixels; about 24 monthly steps, 2017–2020; the 60 SpaceNet 7 AOIs) | Primary optical input for agent, VLM, tools and baselines; supplies the 8 dates per AOI | Preprint release; download route TO VERIFY | TO VERIFY | Sub-pixel alignment to labels; clear-scene count per AOI; grid CRS; preprint versioning |
| MuRA-T cloud mask | Optical availability flag; 8-date rule; clear vs cloudy stratum | Assumed shipped with MuRA-T (TO VERIFY) | TO VERIFY | Mask accuracy and grid match with band 8 |
| Sentinel-1 C-band GRD, VV plus VH where available (10 m pixel spacing (about 20 m resolution)) | SAR input for the SAR change score and change-point; pan vs pan+SAR secondary test | Earth Engine `COPERNICUS/S1_GRD` or Planetary Computer `sentinel-1-rtc` | TO VERIFY | Scenes, orbit direction and polarisation per AOI; revisit per month; whether 20 AOIs (review C1) have consistent coverage; whether GRD and RTC catalogues give comparable values |
| SpaceNet 7 / MUDS building footprints (monthly polygons traced on about 4 m Planet RGB) | Ground truth for presence, onset and fabrication; AOI selection; tuning on development AOIs only | Download route TO VERIFY | CC BY-SA 4.0 (stated in packet) | Labels mark visibility, not construction start; polygon offset vs MuRA-T in metres; share-alike terms for derived cell labels |
| SpaceNet 7 Planet RGB imagery (about 4 m) | Blinded label audit only (validation), never a model input | Assumed shipped with SpaceNet 7 (TO VERIFY) | TO VERIFY | Redistribution terms for audit chips |
| Landsat 8/9 Collection 2 band 8, Level-1 (15 m resolution) | Fallback if MuRA-T is unusable | Provider route TO VERIFY | TO VERIFY | Geometric accuracy after self co-registration |
| Out-of-selection SpaceNet 7 AOIs (3–5) | External validation with frozen prompts and rules | As SpaceNet 7 | CC BY-SA 4.0 | Enough positives in low-growth AOIs to score |
| Second label source | Independent validation | MISSING EVIDENCE | — | None identified; none invented |

Preprocessing (from packet): pan stable-pixel normalisation without test labels; SAR terrain correction, speckle filter, dB, monthly median, co-registered to MuRA-T; labels rasterised per 100 m cell in local UTM metres.

## 2. Tools

Libraries and model names are not given in the packet (TO VERIFY). All deterministic tools are frozen on development AOIs before test runs.

| Tool | What it does | Deterministic? | Human check |
|---|---|---|---|
| Pan change score | Change score from the 8 normalised band 8 chips at 15 m resolution | Yes | Inspect scores on planted-change and stable cells |
| SAR log-ratio change score | Log-ratio change across dates in dB | Yes | Compare against visible change on development AOIs |
| Change-point date per sensor | First date of change per sensor | Yes (method TO VERIFY) | Spot-check dates against labels on development AOIs |
| Optical availability and cross-sensor agreement flags | Clear/cloudy flag from the mask; pan–SAR agreement | Yes | Cross-check flags against the cloud mask |
| Co-registration check (C4) | Offset in metres between MuRA-T, Sentinel-1 and labels | Yes | Week-2 gate: pass or switch to pan primary (C8) |
| Label rasteriser | Polygons to new area per cell; presence at A_min ∈ {225, 450, 900 m²}; onset in date steps (C5); edge-buffer variant | Yes | Hand-check rasterised cells on development AOIs |
| Chip renderer | 1 km chip, cell outline, fixed stretch; strips AOI IDs and coordinates (C7) | Yes | Prompt audit for identifiers |
| Tuned rule, fitted rule (logistic regression, leave-AOI-out), majority floor | Non-agent baselines | Yes (seeded) | Confirm no test-AOI data used |
| Tool-fed LLM arm, no tool calls (C3) | Separates information from agency | No (lowest temperature, 3 runs) | Same pinned model as agent (TO VERIFY) |
| Agent (pinned multimodal LLM) | Views chips, calls tools, returns presence, onset, justification | No (lowest temperature, 3 runs) | Check cited values match logged tool output |
| VLM (same pinned model, no tools) | Same chips and question | No | Must beat the floor on development AOIs; SAR ingestion MISSING EVIDENCE |
| Scoring and inference | Weighted F1, onset error, fabrication rate; AOI-cluster bootstrap; paired per-AOI permutation test; power simulation (C1) | Yes (seeded) | Recompute one AOI by hand |
| Earth Engine / Planetary Computer queries | Sentinel-1 inventory and export | Yes if pinned; catalogue updates TO VERIFY | Log scene IDs per AOI |

## 3. AI-assisted coding tools

- An AI coding assistant (product and version TO VERIFY) may draft preprocessing, tool, harness and scoring code. It is separate from the agent under test.
- Permitted: write and refactor code; run on development AOIs and synthetic data. Not permitted: read test-AOI labels, tune prompts or thresholds, or edit tools after freeze.
- Checks: human review of every tool before freeze; unit tests on synthetic chips (a planted 450 m² footprint, a one-pixel shift at 15 m pixels); version-pin and hash code, prompts and model IDs; log all calls; disclose AI assistance in the code and data statement.

## 4. Top 3 data risks

1. **Co-registration at 15 m pixels (C4).** MuRA-T sub-pixel alignment and Sentinel-1 (10 m pixel spacing, about 20 m resolution) resampling are TO VERIFY; a one-pixel shift moves a 450 m² footprint across a cell edge. Mitigation: measure offsets by week 2, edge-buffer scoring, fallback band 8.
2. **Sentinel-1 coverage consistency.** Orbit and polarisation per AOI are TO VERIFY; fewer than 10 consistent AOIs forces pan primary and worsens the AOI-count problem (C1).
3. **Label validity and leakage (C5–C7).** One label source; labels mark visibility, not construction; AOIs chosen from labels; pretrained models may have seen public SpaceNet 7 (contamination unknown). Mitigation: date-step onset scoring, label-lag tolerance, blinded audit, stripped identifiers, per-AOI prevalence.
