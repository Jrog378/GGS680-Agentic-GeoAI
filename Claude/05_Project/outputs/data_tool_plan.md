# Stage 6: Data and Tool Agent: Data and Tool Plan

- **Source packet:** `outputs/prompt_packets/06_data_tool_agent.md` (generated 2026-10-04 23:37)
- **Inputs used:** H3; H7 (all 8 critiques accepted, applied here); H1 (latest rows override earlier ones); form A1–A3 and human notes; `methodology_v1.md`; `methodology_review.md`; L1 references. Evidence excerpts were not re-read (time limit).
- **Status:** Proposal only. No data downloaded, no results. Anything not stated in the packet is marked **TO VERIFY**. Agreement with earlier LLM stages is not validation (rule 4).

## 1. Datasets

| Dataset | Role | Access | Licence | TO VERIFY |
|---|---|---|---|---|
| **MuRA-T** Landsat-8 OLI band 8 (Collection 1 L1TP; 15 m pixels; least-cloudy scene per month; QA band + cloud mask; co-registered to the SpaceNet 7 grid) | Primary panchromatic input: 1 km chips for every arm and every tool | Purdue RVL download (form); Landsat archive about 1.5 GB | GPL v3 (form) | Download works; usable months per AOI; claimed sub-pixel alignment; Level-1 radiometry needs relative normalisation (method [citation needed]); source is a non-peer-reviewed preprint, used as data only |
| **Sentinel-1 C-band GRD (IW)**, 10 m pixel spacing (about 20 m resolution) | Primary SAR input: 1 km chips (VV, VH where available) | Earth Engine `COPERNICUS/S1_GRD` or Planetary Computer `sentinel-1-rtc` | **TO VERIFY** (not stated in packet) | Scenes per track per AOI, orbit direction, polarisation; 2017 coverage outside Europe [citation needed]; scene within ±15 days of each pan date; co-registration RMSE to the MuRA-T grid (H7.4) |
| **SpaceNet 7 / MUDS** monthly building footprints (traced on about 4 m Planet RGB; one ID per building) | Reference labels only; never shown to any arm | AWS Open Data `spacenet-dataset` | CC BY-SA 4.0 (form) | Per-building IDs present in all chosen AOIs; grid CRS (possibly Web Mercator, about 4.77 m); onsets near window edges; labels mark visibility, not construction start |
| **Fallback:** Landsat 8 Collection 2 band 8 (USGS EarthExplorer, AWS `usgs-landsat`, or Earth Engine TOA) | Replaces MuRA-T only if it fails | As listed (form) | **TO VERIFY** | Self co-registration error (Qu et al., 2026, misregistration risk); Landsat 9 is outside the 2017–2020 window |
| **Pretrained CNN change detector** | Optional tool and P2 feature (H7.8) | Not chosen [citation needed] | **TO VERIFY** | Training data must exclude SpaceNet 7 / MUDS (H7.6); transfer to 15 m pixels |
| **VLM under test** (TEOChat, EarthDial, or a hosted general-purpose VLM) | Arm V and new arm V+T | Not chosen; hosted VLM is the low-risk fallback | **TO VERIFY** | Training data documented, no SpaceNet 7 (H7.6); 8-frame input limit (TEOChat: 8-image training cap, Irvin et al., 2025) |
| **LLM agent backbone** (pinned) | Arm A, C1, optional C2 | API, not chosen | **TO VERIFY** (terms of use) | Version pinned and logged; API cap set in pre-registration |

No external validation dataset exists: MUDS is the only reference (limitation).

**Key preprocessing.** UTM 100 m grid; one reprojection with a stated resampling method. Footprints split by area into cells. **A_min** is set on development AOIs from what 15 m pixels can show (H7.4), not from the 4 m labels. SAR: noise removal, calibration, orthorectification (Lee et al., 2026), one track per AOI, fixed speckle filter, dB. Pan: cloud mask, then normalisation against pseudo-invariant pixels. Sampled cells spaced further apart than one cell, chip overlap reported (H7.6).

## 2. Computational tools

| Tool | What it does | Deterministic? | What Justin must check by hand |
|---|---|---|---|
| Grid and chip renderer (Python geospatial stack; libraries TO VERIFY) | UTM 100 m cells; 1 km chips for 8 dates, cell outlined, pan + SAR side by side | Yes | Cell area on the ground per AOI; outline on the right cell; same files go to A, V and V+T |
| Reference rasteriser | Footprint-cell intersection; presence (≥ A_min), onset month and interval | Yes | 10+ cells per AOI against the polygons; straddling footprints split correctly |
| SAR cell series + Gamma likelihood-ratio test (adapted from Lee et al., 2026) | Candidate change interval and statistic | Yes | Standalone F1 and onset error on development AOIs; fallback statistic if it fails (W2 gate) |
| Pan cell series + change magnitude | Normalised series, change interval, cloud mask | Yes | Pseudo-invariant pixels show no trend after normalisation |
| Neighbour tool | Same statistics for the 8 surrounding cells (layover) | Yes | Look direction and incidence angle recorded per AOI |
| Data-availability tool | Missing or cloudy dates | Yes | Matches the QA band; unanswerable queries equally detectable by V (H7.5) |
| CNN change detector (optional) | Change score for the outlined cell | Yes at inference (fixed weights) | Training data free of SpaceNet 7; dropped from A and P2 together if not ready |
| P1 tuned rule / P2 fitted classifier (e.g. logistic regression) | Non-agent baselines on the same tool outputs | Yes (fixed seed) | Fitted on development AOIs only |
| Agent harness (ReAct-style, Feng et al., 2026) and VLM harness | Run A, V, V+T, C1, blank-image control; log trajectories | **No** (stochastic models; 3 repeats) | Opaque cell IDs and date indices only; no coordinates or AOI codes in any prompt |
| Scorer | Answer schema, abstention rule, presence-F1 and balanced accuracy (co-primary, H7.7), fabrication rate by query type, ±1-interval onset | Yes | Abstention rule pre-registered; spot-check scores on 20 answers |
| Statistics | AOI-level power simulation, minimum detectable difference, few-cluster method, cluster bootstrap, mixed model, δ test | Yes (fixed seed) | δ set after the pilot, before any test run (H7.1); few-cluster method [citation needed] |

**New or changed arms from H7:** V+T (VLM given tool outputs as text, H7.2); blank-image control for V (H7.6); C2 shuffled-evidence arm, CNN and SAR-only analysis are optional (H7.8).

## 3. AI-assisted coding tools

- **Claude Code** (or a similar assistant) writes download, gridding, chip, tool, harness, scoring and statistics code. It is not the agent or VLM under test.
- **How output is checked:** Justin reviews every generated function; each tool is tested on synthetic rasters with known change before real data; scoring and statistics are checked by hand on small worked examples; all code and prompts are version-controlled and intermediate files kept in `outputs/` (rule 10).
- **Not allowed:** no LLM scores answers, classifies failures, sets δ or A_min, or edits labels.
- The paper discloses AI-assisted coding and writing.

## 4. Top 3 data risks

1. **Coverage:** too few AOIs with usable MuRA-T months and Sentinel-1 scenes for 8 shared dates. This is checked at the W1 inventory, with a go/no-go gate at the end of W2.
2. **Detectability and registration:** 4 m labels include change that 15 m pixels cannot show, and hand co-registration of Sentinel-1 adds error. Mitigated by A_min, the co-registration RMSE and the one-pixel shift check.
3. **Leakage:** the VLM or CNN may have been trained on SpaceNet 7. Mitigated by documenting training data, the blank-image control and C1.

**Unresolved:** the VLM, CNN and backbone choices; δ; A_min; the API cap; the Sentinel-1 licence. **Next action:** run the W1 inventory, then the AOI-level power simulation.
