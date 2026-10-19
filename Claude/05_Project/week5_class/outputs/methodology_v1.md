# Methodology v1

Source: prompt packet only. Gaps are marked MISSING EVIDENCE or TO VERIFY. The approved question is unchanged.

**Approved question:** In held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery and than non-agent baselines given the same tool outputs?

**Hypotheses.** H1: the agent has higher presence F1 score and lower fabrication rate than the VLM. H2: the agent's presence F1 is at least as high as the tuned and fitted rules (non-inferiority, AOI-cluster confidence interval) and higher where the tools disagree. Secondary: panchromatic-only vs panchromatic+SAR inputs, run for both the agent and the VLM.

## 1. Unit of analysis
A 100 m × 100 m cell. Each sampled cell is one question: a 1 km chip centred on it, cell outlined, 8 dates. The inference unit is the held-out AOI, because cells are clustered.

## 2. Study area and temporal scope
10–20 of the 60 SpaceNet 7 / MuRA-T AOIs, chosen by new-building count and Sentinel-1 coverage; about 24 monthly steps, 2017–2020. Before any modelling, AOIs are split into development AOIs (about one third: prompt design, rule tuning, fitted-rule training) and test AOIs (never overlapping). The 8 dates per AOI follow a fixed rule: evenly spaced across the window, each the nearest month with a clear MuRA-T scene and a Sentinel-1 acquisition.

## 3. Target variables
- **Presence:** 1 if newly covered footprint area in the cell (buildings first appearing after date 1, by date 8) is ≥ A_min. Primary A_min = 450 m² (two 15 m pixels), matching "development visible at 15 m resolution, not single houses". Cells with 0 < area < A_min are excluded from presence scoring and counted.
- **Onset:** the first of the 8 dates at which cumulative new area reaches A_min.
- **Fabrication:** a claimed new-building cell with zero labelled new footprint area.

## 4. Input/predictor variables
Per date: Landsat-8 band 8 panchromatic chip (15 m pixels); Sentinel-1 VV, plus VH where available (10 m pixel spacing, about 20 m resolution); MuRA-T cloud mask. Tool outputs (agent and baselines only): panchromatic change score, SAR log-ratio change score, change-point date per sensor, optical availability flag, cross-sensor agreement flag.

## 5. Data provenance and resolution
| Data | Source | Resolution | Status |
|---|---|---|---|
| Landsat-8 band 8 | MuRA-T, Collection 1 L1TP, on SpaceNet 7 grid | 15 m resolution | preprint; sub-pixel alignment TO VERIFY |
| Sentinel-1 C-band GRD | Earth Engine `COPERNICUS/S1_GRD` or Planetary Computer `sentinel-1-rtc` | 10 m pixel spacing (about 20 m resolution) | scenes, orbit, polarisation per AOI TO VERIFY |
| Labels | SpaceNet 7 / MUDS, CC BY-SA 4.0 | traced on about 4 m Planet RGB | independent of both inputs |
| Fallback | Landsat 8/9 Collection 2 band 8, Level-1 | 15 m resolution | self co-registration |

## 6. Preprocessing
- **CRS:** the grid CRS is not stated in the packet (TO VERIFY). Cells, areas and distances are computed in the local UTM zone (metres, m²).
- **Panchromatic:** per-scene normalisation against stable pixels to remove sun-angle and seasonal shifts in Level-1 values; stable pixels are chosen without test labels.
- **SAR:** one orbit direction and polarisation per AOI; terrain correction, speckle filter, dB; monthly median if several scenes; co-registered to the MuRA-T grid.
- **Labels:** polygons rasterised to new area per cell, area-weighted where 15 m pixels straddle cell edges.
- **Chips:** one fixed rendering (stretch, outline) shared by agent and VLM.

## 7. Models
- **Tools** (deterministic, frozen before testing): the change scores, change-points and flags in Section 4.
- **Agent:** a pinned multimodal LLM that views the chips, calls the tools and returns presence, onset date and a justification citing tool output.
- **VLM:** the same pinned model where possible; same chips and question, no tools. Whether any VLM accepts SAR chips is MISSING EVIDENCE.
- Lowest available temperature; 3 repeated runs per cell; prompt fixed on development AOIs.

## 8. Baselines
- **Tuned rule:** presence if either change score exceeds thresholds tuned on development AOIs; onset = first date over threshold.
- **Fitted rule:** logistic regression on the same tool outputs, trained on development AOIs with leave-AOI-out cross-validation.
- **Floor:** majority class.

## 9. Spatial split and metrics
Whole-AOI holdout: no test-AOI cell informs prompts, thresholds or fitting. In each test AOI a seeded stratified sample (about 60 cells: labelled new with early or late onset, built-stable, never-built, tool-disagreement) is drawn; metrics use inverse-inclusion weights. Metrics: presence F1, precision and recall; precision–recall AUC for scored baselines; onset absolute error in months, exact-date agreement and share within ±1 month; fabrication rate (fabricated claims ÷ all positive claims). Differences carry 95% confidence intervals from an AOI-cluster bootstrap over test AOIs.

## 10. Uncertainty and sensitivity
- Run-to-run spread across the 3 runs, plus majority vote.
- A_min ∈ {225, 450, 900 m²}.
- Cell size 100 m vs 200 m, and a 50 m grid offset.
- Two prompt paraphrases.
- Strata: tool agreement, optical availability (clear vs cloudy/missing months), AOI.
- Secondary: panchromatic-only vs panchromatic+SAR for agent, VLM and baselines.

## 11. External validation
- **Label audit:** random labelled and claimed events per test AOI hand-checked on the about 4 m imagery; report label-audit disagreement rate.
- **Out-of-selection AOIs:** 3–5 non-selected SpaceNet 7 AOIs (low growth or weak Sentinel-1 coverage) scored with frozen prompts and rules.
- A second label source is MISSING EVIDENCE.

## 12. Decision criteria (pre-registered)
- **H1 supported** if the 95% confidence interval of agent − VLM presence F1 lies above 0 and that of fabrication rate lies below 0.
- **H2 supported** if the lower 95% confidence bound of agent − best-rule presence F1 is above −0.05 F1, and the difference is positive in the tool-disagreement stratum.
- **Refuted** if agent F1 ≤ VLM F1, or the fabrication gain comes only from a recall collapse.
- **Pivot:** MuRA-T unusable → fallback band 8; fewer than 10 AOIs with consistent Sentinel-1 → panchromatic primary; no VLM ingests SAR → SAR comparison on agent and baselines only.

## GeoAI checks
- **CRS/units:** UTM metres; areas in m².
- **Spatial autocorrelation:** neighbouring chips overlap; inference is AOI-level only.
- **Leakage:** AOI holdout; test labels unseen; tools use only the 8 supplied dates; pretrained models may have seen public SpaceNet 7 data (contamination unknown).
- **Scale mismatch:** about 4 m labels, 15 m pixels, about 20 m SAR resolution, 100 m cells; handled by A_min sensitivity.
- **MAUP:** cell-size and offset tests; no single-building claims.
- **Sampling bias:** AOIs chosen for growth and SAR coverage raise prevalence; checked with out-of-selection AOIs.
- **Transferability:** limited to SpaceNet 7-type sites, 2017–2020.

## Assumptions most likely to change the conclusion
1. A_min = 450 m² defines the positive class; another threshold could reverse rankings.
2. Some VLM accepts panchromatic and SAR chips (MISSING EVIDENCE); a weak VLM inflates H1.
3. 8 dates resolve onset only to about a 3-month step; "±1 month" may need re-reading as ±1 date step (to confirm).
4. MuRA-T alignment and Sentinel-1 consistency hold (TO VERIFY).
5. SpaceNet 7 labels are accurate; they mark visibility, not construction start.
6. 10–20 AOIs give enough power for AOI-cluster intervals.

## Eight-week work plan
| Week | Headline | Deliverable |
|---|---|---|
| 1 | Data access and AOI screening | MuRA-T and labels downloaded; Sentinel-1 inventory; AOIs selected; split frozen |
| 2 | Co-registration and label-to-cell rules | SAR on MuRA-T grid; cell grid; A_min and 8-date rule pre-registered |
| 3 | Tools and baselines | Frozen tools; tuned and fitted rules on development AOIs |
| 4 | Agent and VLM harness | Pinned models; prompts fixed; pilot on development AOIs |
| 5 | Held-out test runs | 3 runs per cell for all systems; label audit |
| 6 | Scoring and hypothesis tests | F1, onset error, fabrication rate; AOI-cluster intervals; strata |
| 7 | Sensitivity and external validation | Thresholds, MAUP, prompts, pan vs pan+SAR; out-of-selection AOIs |
| 8 | Write-up and submission | Manuscript, code and data statement submitted |
