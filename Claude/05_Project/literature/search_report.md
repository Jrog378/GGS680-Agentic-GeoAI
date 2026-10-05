# L1 literature search report: Agentic GeoAI for multi-temporal satellite imagery

Prepared by the `researcher` agent pipeline for Justin Rogers's GGS 662 Assignment 3 (research proposal), 2026-10-02. The pipeline ran in this order: search, relevance-checker, completeness-checker Mode 1, download, completeness-checker Mode 2, evidence copy, summary-annotator, narrator.

**Research question:** "How can Agentic GeoAI help interpret large sources of satellite imagery in an area of interest to understand patterns and changes over time?"

**Interest areas used to judge relevance:**
- vision-language models (VLMs) and multimodal LLMs (MLLMs) for interpretation;
- agentic automation, and what stays human;
- satellite image time series (SITS) and change detection;
- practical problems: co-registration (misalignment), differing resolutions, and gaps from clouds and revisit intervals.

**Scope update during the run:** Justin's study will start with **panchromatic and SAR** imagery, so I added 14 Primo queries and 3 arXiv queries on SAR and panchromatic imagery (Section 1). The shortlist was rebalanced toward SAR papers.

**Bottom line:**
- The **final L1 shortlist has 10 papers**. All are peer-reviewed, published 2023–2026, rated Relevant and downloaded, and all passed both completeness checks. Only these 10 are in `05_Project/evidence/`.
- 6 more downloaded peer-reviewed papers were moved to `evidence/.not_in_L1/` as background.
- 3 relevant IEEE papers still need Justin's GMU access (Section 5).
- **No peer-reviewed 2023–2026 paper on change detection, VLMs or agents for panchromatic imagery was found.** This is reported as a gap in Section 2c.
- Every metadata item comes from Crossref, OpenAlex, the CVF, the ICLR or NeurIPS proceedings, the ACL Anthology, OpenReview, the arXiv API, or the first page of the PDF itself. Nothing was typed from memory. Anything I could not verify is marked **TO VERIFY**.

---

## 1. Query log

Primo searches used the GMU Primo REST API with `qInclude=facet_rtype,exact,articles` and scope `MyInst_and_CI`, retrieving up to 50 records per query. The "Hits" column is Primo's reported total. That figure is inflated for broad multi-word queries, because Primo matches any of the words.

| # | Source | Breadth | Query | Hits (total) | Retrieved |
|---|---|---|---|---|---|
| 1 | GMU Primo (articles) | broad | remote sensing change detection deep learning | 3597 | 50 |
| 2 | GMU Primo (articles) | broad | satellite image time series | 10618 | 50 |
| 3 | GMU Primo (articles) | broad | GeoAI remote sensing | 348 | 50 |
| 4 | GMU Primo (articles) | broad | remote sensing foundation model | 38644 | 50 |
| 5 | GMU Primo (articles) | broad | vision language model remote sensing | 1559 | 50 |
| 6 | GMU Primo (articles) | broad | multimodal large language model earth observation | 102 | 50 |
| 7 | GMU Primo (articles) | narrow | LLM agent remote sensing | 122 | 50 |
| 8 | GMU Primo (articles) | narrow | agentic remote sensing image analysis | 8 | 8 |
| 9 | GMU Primo (articles) | narrow | remote sensing visual question answering | 251 | 50 |
| 10 | GMU Primo (articles) | narrow | change detection vision-language | 312 | 50 |
| 11 | GMU Primo (articles) | narrow | remote sensing change captioning | 145 | 50 |
| 12 | GMU Primo (articles) | narrow | satellite image time series foundation model | 913 | 50 |
| 13 | GMU Primo (articles) | narrow | co-registration error change detection | 44 | 44 |
| 14 | GMU Primo (articles) | narrow | cloud gap time series reconstruction | 162 | 50 |
| 15 | GMU Primo (articles) | narrow | human-in-the-loop remote sensing interpretation | 4 | 4 |
| 16 | GMU Primo (articles) | narrow | large language model remote sensing tool agent | 56 | 50 |
| 17 | GMU Primo (articles) | narrow | misregistration change detection | 175 | 50 |
| 18 | GMU Primo (articles) | narrow | multimodal large language model remote sensing benchmark | 212 | 50 |
| 19 | GMU Primo (articles) | narrow | temporal vision language model earth observation | 52 | 50 |
| 20 | GMU Primo (articles) | narrow | multitemporal multimodal large language model remote sensing | 4 | 4 |
| 21 | GMU Primo (articles) | narrow | TEOChat | 3 | 3 |
| 22 | GMU Primo (articles) | narrow | GeoChat remote sensing | 13 | 13 |
| 23 | GMU Primo (articles) | narrow | EarthDial | 7 | 7 |
| 24 | GMU Primo (articles) | narrow | irregular satellite image time series | 103 | 50 |
| 25 | GMU Primo (articles) | narrow | remote sensing image registration deep learning | 618 | 50 |
| 26 | GMU Primo (articles) | narrow | multi-resolution satellite image fusion deep learning | 33 | 33 |
| 27 | GMU Primo (articles) | narrow | human-AI collaboration remote sensing | 10 | 10 |
| 28 | GMU Primo (articles) | narrow | interactive remote sensing change interpretation | 59 | 50 |
| 29 | GMU Primo (articles) | narrow | Change-Agent remote sensing | 255 | 50 |
| 30 | GMU Primo (articles) | narrow | remote sensing large language model survey | 133 | 50 |
| 31 | arXiv API | cross-check | `abs:agent AND abs:"remote sensing" AND (abs:LLM OR abs:"language model")` | 56 | 30 |
| 32 | arXiv API | cross-check | `abs:agentic AND (abs:"earth observation" OR abs:satellite)` | 267 | 30 |
| 33 | arXiv API | cross-check | `(abs:"vision-language" OR abs:"multimodal large language") AND (abs:temporal OR abs:"time series") AND (abs:"remote sensing" OR abs:"earth observation")` | 48 | 30 |
| 34 | arXiv API | cross-check | `abs:"change detection" AND (abs:"large language model" OR abs:"vision-language") AND abs:"remote sensing"` | 30 | 30 |
| 35 | arXiv API | cross-check | `abs:"satellite image time series" AND abs:"foundation model"` | 5 | 5 |
| 36 | arXiv API | cross-check | `(abs:misregistration OR abs:"co-registration" OR abs:"registration error") AND abs:"change detection"` | 12 | 12 |
| 37 | GMU Primo (articles) | broad (SAR) | SAR change detection deep learning | 613 | 50 |
| 38 | GMU Primo (articles) | broad (SAR) | synthetic aperture radar image interpretation | 1625 | 50 |
| 39 | GMU Primo (articles) | broad (SAR) | SAR time series change detection | 826 | 50 |
| 40 | GMU Primo (articles) | broad (pan) | panchromatic image change detection | 181 | 50 |
| 41 | GMU Primo (articles) | broad (SAR) | SAR optical fusion change detection | 213 | 50 |
| 42 | GMU Primo (articles) | narrow (SAR) | SAR image interpretation large language model | 28 | 28 |
| 43 | GMU Primo (articles) | narrow (SAR) | SAR vision-language model | 69 | 50 |
| 44 | GMU Primo (articles) | narrow (SAR) | SAR visual question answering | 29 | 29 |
| 45 | GMU Primo (articles) | narrow (SAR) | multimodal large language model SAR | 81 | 50 |
| 46 | GMU Primo (articles) | narrow (SAR) | SAR image captioning | 20 | 20 |
| 47 | GMU Primo (articles) | broad (SAR) | SAR foundation model | 10373 | 50 |
| 48 | GMU Primo (articles) | broad (pan) | panchromatic satellite image deep learning | 261 | 50 |
| 49 | GMU Primo (articles) | narrow (SAR) | Sentinel-1 time series change detection | 458 | 50 |
| 50 | GMU Primo (articles) | narrow (SAR) | SAR agent large language model | 55 | 50 |
| 51 | arXiv API | cross-check (SAR) | `(abs:SAR OR abs:"synthetic aperture radar") AND (abs:"vision-language" OR abs:"multimodal large language" OR abs:"large language model")` | 88 | 30 |
| 52 | arXiv API | cross-check (SAR) | `(abs:SAR OR abs:"Sentinel-1") AND abs:"time series" AND abs:"change detection"` | 4 | 4 |
| 53 | arXiv API | cross-check (pan) | `abs:panchromatic AND abs:"change detection"` | 2 | 2 |

**SAR and panchromatic queries (37–53):**
- These returned 324 unique records dated 2023–2026. Of those, 193 have SAR, radar, Sentinel-1 or panchromatic in the title.
- 29 candidates went to the relevance check after a title screen. The screen dropped SAR target-recognition and ship-detection papers, SAR simulation and analog-circuit hits.
- Several strong SAR VLM papers are still arXiv-only, so they are not L1-eligible. Examples: SARChat-Bench-2M (2502.08168), SARVLM (2510.22665), FUSAR-R1 (2607.16819) and FUSAR-GPT (2602.19190).

**Aggregation:**
- Queries 1–18 returned 717 unique records after deduplication by DOI or normalized title. Of these, 551 were dated 2023–2026.
- Queries 19–30 added further unique records, and the arXiv cross-check added more. I screened all of these by title.
- Clearly off-topic hits were dropped by title before the relevance check. Examples: dental CBCT, auroral imagery, drone swarms, and satellite scheduling.
- 71 candidates went to the relevance check. A supplementary check of 4 open-access co-registration papers followed later; see Section 2b.

**Existing material checked first:**
- `Personal/research/multimodal-models/pdfs/vlm-pretraining-remote-sensing-2505.11121-summary.pdf`: Adler et al., IGARSS 2025, DOI 10.1109/IGARSS55030.2025.11243285. Peer-reviewed, but rated Not relevant because it is about pretraining efficiency.
- `cagmc-defence-remote-sensing-rs17193300-summary.pdf`: Cui et al., *Remote Sensing* 2025, adversarial defence. Not relevant to this question, so it was not carried forward.
- Course readings in `Agentic-GeoAI/literature/`:
  - Akinboyewa et al. 2025 (GIS Copilot, *IJDE*) and Mansourian & Oucheikh 2026 (*IJDE*): peer-reviewed, Marginal, because they concern GIS rather than imagery.
  - Li et al. 2025 (*Annals of GIS*): peer-reviewed and Relevant, already held.
  - Yu et al. 2026 GeoAgentBench: arXiv only, so not peer-reviewed.
  - Kapoor et al. 2024 (AI Agents That Matter): the copy held is arXiv 2407.01502. Whether a peer-reviewed version exists is **TO VERIFY**. It is not on topic for L1.

**Access notes, important for anyone re-running this:**
- **OpenReview** returned a bot-challenge page to curl. The official ICLR and NeurIPS proceedings sites served the same camera-ready PDFs instead.
- **ScienceDirect, directly (not through the proxy):** showed a CAPTCHA in Chrome and returned an HTML page to curl. I did not attempt it.
- **ScienceDirect through the GMU EZproxy:** worked in Chrome with a live session and no login prompt.
- **IEEE Xplore through the EZproxy:** showed a bot-challenge page ("Max challenge attempts exceeded"). I reloaded once and then stopped; I did not try to get around it. IEEE open-access PDFs downloaded fine with curl from `stampPDF`.
- **MDPI:** blocked curl with "Access Denied", but worked through a normal Chrome download.

---

## 2. Candidates and relevance verdicts

The relevance-checker sub-agent judged all 71 candidates against the research question. Of the candidate set, 35 were rated Relevant, 33 Marginal and 3 Not relevant. All are dated 2023–2026.

Column keys:
- R = Relevant, M = Marginal, NR = Not relevant.
- PR = peer review:
  - J = journal;
  - C = main-track conference;
  - W = workshop;
  - F = ACL Findings;
  - X = arXiv only.
- Access:
  - OA = open access at the publisher;
  - green = the published version is licensed, with a free arXiv version;
  - lic = licensed.

### 2a. Main relevance check (71 candidates)

| # | ID | Paper (venue, year) | PR | Access | Verdict | Reason |
|---|---|---|---|---|---|---|
| 1 | T2 | Liu et al., Remote Sensing Spatiotemporal VLMs survey (IEEE GRSM, 2026) | J | green | R | Sits exactly where VLMs meet multi-temporal change: covers change captioning, question answering, grounding, datasets and metrics |
| 2 | T1 | Irvin et al., TEOChat (ICLR, 2025) | C | OA | R | VLM that reasons over temporal sequences of Earth-observation images |
| 3 | T10 | Xuan et al., DynamicVL (NeurIPS D&B, 2025) | C | OA | R | 42 cities, 2005–2023; MLLMs fail at long-term, quantitative change |
| 4 | A1 | Liu et al., Change-Agent (IEEE TGRS, 2024) | J | green | R | The standard design: an LLM controller plus change-detection and captioning tools for interactive change interpretation |
| 5 | A20 | Feng et al., Earth-Agent (ICLR, 2026) | C | OA | R | Agent that calls tools through MCP for quantitative spatiotemporal EO analysis; evaluates each reasoning step |
| 6 | A26 | Kao et al., Towards LLM Agents for EO (Findings ACL, 2026) | F | OA | R | Measured agent failure rates, which ground the argument for what can't be automated yet |
| 7 | V8 | Soni et al., EarthDial (CVPR, 2025) | C | OA | R | VLM that handles multiple sensors, resolutions and time steps |
| 8 | S11 | Michel & Inglada, TAMRF-SITS (RSE, 2026) | J | OA | R | Fuses Landsat and Sentinel-2 across resolutions and dates; ignores clouds |
| 9 | S1 | Miller et al., DL for SITS review (IEEE GRSM, 2024) | J | green | R | The standard review of deep learning for SITS |
| 10 | S12 | Qu et al., AnyTime-CD (RSE, 2026) | J | lic | R | Change detection on dense time series of any length; handles uneven time gaps and spatial misalignment |
| 11 | S2 | Dumeur et al., ALISE: FMs for irregular and unaligned SITS (IEEE TGRS, 2025) | J | green | R | Foundation model for irregular, unaligned time series (the gaps problem) |
| 12 | S4 | Shu et al., RESTORE-DiT (RSE, 2025) | J | OA | R | Uses SAR time series to rebuild cloudy optical time series |
| 13 | V6 | Yuan et al., ChatEarthBench (IEEE GRSM, 2026) | J | OA | R | Zero-shot test of MLLMs on EO tasks; shows their limits |
| 14 | A9 | ChangeGPT, LLM agent for urban change analysis (Automation in Construction, 2025) | J | green | R | LLM plus vision foundation models for multi-step change questions |
| 15 | A10 | Forest-Chat (Ecological Informatics, 2026) | J | OA | R | Extends the Change-Agent approach to forest change |
| 16 | A6 | RemoteAgent (IEEE TGRS, 2026) | J | green | R | Decides when the model answers itself and when it calls a tool |
| 17 | A7 | Zuo et al., Hallucination-resistant change detection (IEEE JSTARS, 2026) | J | OA | R | Calibration and self-consistency safeguards against hallucination |
| 18 | S20 | Schwartz et al., FORMSpoT (RSE, 2026) | J | green | R | National 1.5 m time series; co-registers and denoises before detecting change |
| 19 | T3 | Jain et al., TimeSenCLIP (ISPRS J., 2026) | J | OA | R | VLM for Sentinel-2 pixel time series |
| 20 | A17 | Li et al., Autonomous GIS agenda (Annals of GIS, 2025) | J | OA | R | Five levels of autonomy, a framing for what stays human; already held |
| 21 | A24 | Human-in-the-loop GeoAI–GIS workflow (Sustainability, 2026) | J | OA | R | Measures expert review of AI outputs; weaker venue |
| 22 | A5 | LLM multi-agent system for RS analysis (Big Earth Data, 2026) | J | OA | R | Compares agent outputs against human experts |
| 23 | V5 | Vision-Language Modeling Meets RS (IEEE GRSM, 2025) | J | green | R | The authoritative classification of RS VLMs |
| 24 | V12 | RS VLM review (IEEE JSTARS, 2026) | J | OA | R | Treats VLMs as the perception parts of agents; overlaps V5 |
| 25 | S15 | Sample-efficient change-detection survey (IEEE GRSM, 2025) | J | green | R | Time-series change detection when labels are scarce |
| 26 | V1 | Kuckreja et al., GeoChat (CVPR, 2024) | C | OA | R | Foundational grounded RS VLM (single images) |
| 27 | A2 | RS-Agent (Sci. China Inf. Sci., 2026) | J | green | R | LLM controller, toolkit and expert procedures |
| 28 | S7 | Deep-learning change-detection review (JAG, 2025) | J | OA | R | Recent change-detection classification; covers multi-resolution data |
| 29 | S3 | Stucker et al., U-TILISE (IEEE TGRS, 2023) | J | OA | R | Fills cloud gaps in Sentinel-2 time series |
| 30 | S6 | Seamless HLS reconstruction (RSE, 2024) | J | free (bronze) | R | Fills gaps in combined Landsat and Sentinel-2 time series |
| 31 | T7 | DeltaVLM (Remote Sensing, 2026) | J | OA | R | Multi-turn change question answering; two dates only |
| 32 | S9 | URCNet, joint registration and change detection (IEEE TGRS, 2024) | J | lic | R | Registers and detects change in one network |
| 33 | S16 | Grich et al., Sentinel-2 gap-filling evaluation (Sci. Rep., 2026) | J | OA | R | Compares gap-filling methods head to head |
| 34 | A19 | ThinkGeo (CVPR 2026 workshop) | W | OA | R | Agent benchmark; workshop only, so background |
| 35 | A21 | Talemi et al., Agentic AI in RS survey (WACV 2026 workshop) | W | OA | R | First survey of RS agents; workshop only, so background |
| 36 | T5 | SITS change captioning (IEEE GRSL, 2024) | J | lic | M | Short letter, covered by T1, T2 and T10 |
| 37 | S18 | Multi-modal image registration review (PE&RS, 2026) | J | lic | M | Focuses on matching optical to SAR images |
| 38 | S10 | IGmLs, change detection with unregistered images (IJCV, 2026) | J | lic | M | Cross-sensor and niche |
| 39 | S5 | AnytimeFormer (RSE, 2026) | J | lic | M | Overlaps S4 and S11 |
| 40 | A12 | SR2A RS agent verification (IEEE GRSL, 2026) | J | lic | M | Single-image letter |
| 41 | S17 | Irregular SITS with Gaussian processes (IEEE JSTARS, 2024) | J | OA | M | Earlier version of S2 |
| 42 | S14 | Change-detection review (Remote Sensing, 2024) | J | OA | M | Covers the same ground as S7 |
| 43 | A23 | Urban park LLM agents (IGARSS, 2025) | C | green | M | 4-page proceedings paper; A9 is stronger |
| 44 | A4 | RS agent paradigm (Remote Sensing, 2026) | J | OA | M | Conceptual only |
| 45 | A14 | RingMo-Agent (IEEE TPAMI, 2026) | J | green | M | No time dimension |
| 46 | V9 | FMs for GeoAI vision paper (ACM TSAS, 2024) | J | OA | M | General, pre-agent |
| 47 | A11 | GeoAgentic-RAG (JAG, 2026) | J | OA | M | Answers questions by retrieval, not imagery over time |
| 48 | A18 | Autonomous GIS (IJDE, 2023) | J | OA | M | Superseded by A17 |
| 49 | A15 | GIS Copilot (IJDE, 2025) | J | OA | M | GIS rather than imagery; already held |
| 50 | A16 | Mansourian & Oucheikh (IJDE, 2026) | J | OA | M | GIS rather than imagery; already held |
| 51 | A22 | GeoAgentBench (arXiv, 2026) | X | OA | M | Not peer-reviewed; already held |
| 52 | V2 | EarthGPT (IEEE TGRS, 2024) | J | lic | M | V8 covers the same ground and is OA |
| 53 | V4 | VLMs in RS (IEEE GRSM, 2024) | J | lic | M | Older survey |
| 54 | V10 | RS foundation models survey (IEEE GRSM, 2025) | J | lic | M | Broad |
| 55 | V7 | RingMoGPT (IEEE TGRS, 2025) | J | lic | M | Covered by T1 and V8 |
| 56 | T8 | Change-LISA (IEEE TGRS, 2026) | J | lic | M | Two dates only |
| 57 | T4 | ChangeCLIP (ISPRS J., 2024) | J | lic | M | Model detail, not workflow |
| 58 | T9 | Changen2 (IEEE TPAMI, 2025) | J | lic | M | Synthetic training data |
| 59 | T11 | Change captioning review (IJMIR, 2025) | J | lic | M | Covered by T2 |
| 60 | T12 | Multi-temporal captioning with an LLM (Remote Sensing, 2026) | J | OA | M | Two-date captioning |
| 61 | A3 | RescueADI (IEEE TGRS, 2025) | J | lic | M | Single-image disaster interpretation |
| 62 | A13 | RS-Claw (IEEE TGRS, 2026) | J | lic | M | Tool-selection engineering |
| 63 | A25 | Chat-RSC (IJDE, 2025) | J | OA | M | No time dimension |
| 64 | V3 | RemoteCLIP (IEEE TGRS, 2024) | J | lic | M | Retrieval backbone only |
| 65 | V11 | VLM review (Remote Sensing, 2025) | J | OA | M | Covers the same ground as V5 and V12 |
| 66 | S8 | SAR change detection with co-registration errors (IEEE GRSL, 2024) | J | lic | M | SAR-only letter |
| 67 | S13 | Forest FMs with Sentinel-2 time series (IEEE GRSL, 2025) | J | lic | M | Application letter |
| 68 | A8 | Agentic tropical rainforest change (IEEE JSTARS, 2026) | J | OA | M | A Siamese CNN labeled "agentic"; close to a keyword-only match |
| 69 | T6 | CTMTNet change detection and captioning (IEEE TGRS, 2024) | J | lic | NR | Architecture tweak |
| 70 | V13 | Data-centric VLM survey (IEEE GRSM, 2026) | J | lic | NR | About building fine-tuning datasets |
| 71 | V14 | Adler et al., redundancy-aware VLM pretraining (IGARSS, 2025) | C | OA | NR | Keyword match only; already summarized |

### 2b. Supplementary co-registration check (4 OA candidates)

Every one of the relevance-checker's practical-problem picks first appeared unfetchable, so I ran this extra check to find an open-access, peer-reviewed paper on co-registration.

| DOI | Paper | Verdict | Reason |
|---|---|---|---|
| 10.3390/rs17071160 | Simarro et al., UOrtos (Remote Sensing, 2025) | R | Co-registers a whole 2020–2023 Sentinel-2 and Landsat stack to subpixel accuracy and separates misregistration from real change. Its method is classical, not deep learning. |
| 10.3390/app16021113 | Im & Lee, multi-resolution registration (Applied Sciences, 2026) | R (secondary) | Aligns images from different sensors at different resolutions to under 0.5 px. Weak venue and no time series. |
| 10.3390/s25051380 | DVF-NET (Sensors, 2025) | M | Two dates only; weaker venue |
| 10.3390/rs17172949 | OFNet (Remote Sensing, 2025) | NR | Uses optical flow to find changes, not to align images |

### 2c. SAR and panchromatic check (29 candidates, after the scope update)

The relevance-checker rated these 29: 11 Relevant, 17 Marginal and 1 Not relevant. Access was checked through OpenAlex and Crossref.

| ID | Paper (venue, year) | DOI | Access | Verdict | Reason |
|---|---|---|---|---|---|
| SV4 | Hou et al., SAR foundation models: a comprehensive review (Sci. China Inf. Sci., 2026) | 10.1007/s11432-026-5040-3 | OA (CC BY) | **R, L1** | First classification of SAR foundation models, including vision-language and SAR-optical approaches |
| SV2 | SAREval: benchmark of VLMs on SAR (Remote Sensing, 2025) | 10.3390/rs18010082 | OA | R, alternate | 11 VLMs on 20 SAR tasks; large failures |
| SV7 | SAR Strikes Back: A New Hope for RSVQA (IEEE JSTARS, 2025) | 10.1109/JSTARS.2025.3596678 | OA | R, background | SAR versus optical versus fused inputs for visual question answering; models from before LLMs |
| SV1 | SARLANG-1M (IEEE TGRS, 2026) | 10.1109/TGRS.2026.3652099 | lic (IEEE) | M | On topic, but behind IEEE's login wall |
| SV3 | RadarMind (IEEE TAES, 2026) | 10.1109/TAES.2026.3719218 | lic (IEEE) | M | Step-by-step reasoning with a human in the loop for SAR; behind a login wall |
| SV5 | SARCLIP (IEEE TGRS, 2025) | 10.1109/TGRS.2025.3630131 | lic | M | Licensed; SV4 covers it |
| SV6 | Multimodal large models for SAR image captioning (IEEE JSTARS, 2025) | 10.1109/JSTARS.2025.3603036 | OA | M | Aircraft targets only |
| SV8 | Multi-agent scheduling for SAR interpretation (Sensors, 2026) | 10.3390/s26113311 | OA | M | Its "agents" are scheduling units, not LLM agents |
| SV10 | LLM-enhanced detection of radio interference in multi-date SAR (IEEE JSTARS, 2026) | 10.1109/JSTARS.2026.3699595 | OA | M | A niche automated quality check |
| SV9 | FSAR-Cap (IEEE GRSL, 2026) | 10.1109/LGRS.2026.3663901 | lic | NR | Dataset letter, superseded by SV1 and SV2 |
| ST4 | Lee, Lee & Kim, Change type analysis for urban construction using time-series SAR (IEEE JSTARS, 2026) | 10.1109/JSTARS.2026.3737141 | OA | **R, L1** | Sentinel-1, 2019–2023; classifies change by direction, duration and periodicity, i.e. patterns over time |
| ST1 | SAMSR: vision foundation model for forest disturbance from Sentinel-1 time series (RSE, 2025) | 10.1016/j.rse.2025.114775 | lic (GMU proxy works) | R, alternate | SAM adapted to SAR time series at 4 sites worldwide |
| ST5 | Bayesian near-real-time forest loss from Sentinel-1 (RSE, 2025) | 10.1016/j.rse.2025.115037 | OA | R, background | Unsupervised SAR time-series change; adjusts for seasons |
| ST6 | High-resolution optical pair plus long SAR series for built-up change (IJDE, 2024) | 10.1080/17538947.2024.2316109 | OA | R, background | The setup closest to Justin's high-resolution-plus-SAR start |
| ST8 | Unsupervised flood detection on SAR time series with a VAE (JAG, 2024) | 10.1016/j.jag.2023.103635 | OA | R, background | Single flood events |
| ST12 | SAR change screening, then optical identification (Remote Sensing, 2026) | 10.3390/rs18081103 | OA | R, background | SAR flags candidates, then optical imagery confirms them; a triage workflow an agent could run |
| ST13 | Optical and SAR image fusion review (Remote Sensing, 2025) | 10.3390/rs18010073 | OA | R, background | Points toward fusion driven by multimodal large models |
| ST17 | SAR-SIFT time-series change detection (Remote Sensing, 2023) | 10.3390/rs15235533 | OA | R, background | Co-registers the whole SAR stack first; the SAR counterpart of UOrtos |
| ST2 | Bayesian change points for floods, Sentinel-1 (IEEE TGRS, 2025) | 10.1109/TGRS.2025.3620907 | green | M | IEEE; only the preprint is free |
| ST3 | SAR-TSCC: long SAR time-series change and pattern analysis (IEEE TGRS, 2023) | 10.1109/TGRS.2023.3243900 | lic | M | On target, but behind a login wall |
| ST7 | Semi-supervised urban change detection with Sentinel-1 and Sentinel-2 (Remote Sensing, 2023) | 10.3390/rs15215135 | OA | M | Two dates only |
| ST9 | Fuzzy spatiotemporal fusion for unsupervised flood mapping (IEEE TGRS, 2023) | 10.1109/TGRS.2023.3324066 | lic | M | One event; licensed |
| ST10 | Optical-SAR change detection with frequency-spatio-temporal learning (JAG, 2026) | 10.1016/j.jag.2026.105534 | OA | M | Two-date architecture |
| ST11 | MARC-Net: two-date change detection with a missing optical image (Remote Sensing, 2026) | 10.3390/rs18172960 | OA | M | Cropland only |
| ST14 | Began+: clear-sky reconstruction from SAR and optical (RSE, 2026) | 10.1016/j.rse.2025.115171 | lic | M | S4 covers this and is OA |
| ST15 | ConvLSTM-Siamese flood detection with Sentinel-1 (ISPRS Archives, 2026) | 10.5194/isprs-archives-L-4-W1-2026-181-2026 | OA | M | Papers reviewed on the abstract only; "misalignment" here means a gap between dates |
| P1 | Pan-sharpening (panchromatic + multispectral fusion) review (Information Fusion, 2023) | 10.1016/j.inffus.2022.12.026 | OA | M | Strong venue, but preprocessing only |
| P2 | Cloud detection in panchromatic imagery (IEEE JSTARS, 2026) | 10.1109/JSTARS.2025.3639193 | OA | M | Useful cloud masking for panchromatic images, but niche |
| P3 | Canopy height from sub-meter panchromatic imagery (MLST, 2025) | 10.1088/2632-2153/ada47e | OA | M | No change detection |

**The panchromatic gap:**
- No peer-reviewed 2023–2026 paper turned up on change detection, VLMs/MLLMs or agents for panchromatic imagery. Primo query 40 returned no such paper, and arXiv query 53 returned 2 hits, both on pan-sharpening.
- The relevance-checker's view is that the proposal can cite this as a novelty gap, with a caveat: a search that comes up empty does not prove no such paper exists.
- Very-high-resolution change-detection benchmarks are mostly built from pan-sharpened imagery. So S12 (AnyTime-CD, 3–4.8 m PlanetScope) and T10 (DynamicVL, 1 m NAIP) are the closest L1 stand-ins.
- P1 and P2 are background for the resolution-merging and cloud-masking steps.

---

## 3. Final L1 shortlist (10 papers)

All 10 are peer-reviewed, published 2023–2026, rated Relevant, downloaded, and passed completeness Mode 1 and Mode 2. The relevance-checker chose them after the SAR scope update, preferring SAR papers over weaker optical-only candidates.

Base paths:
- PDFs: `/Users/jusrogers/Claude/Personal/research/agentic-geoai-satellite-imagery/pdfs/`
- audio: `/Users/jusrogers/Claude/Personal/research/agentic-geoai-satellite-imagery/audio/`
- evidence: `/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/05_Project/evidence/`

Evidence copies are the clean originals, with no AI summary page. "Summary PDF" is the copy with an AI summary page prepended.

| # | APA citation | Year | Venue | Peer review | DOI | Theme / gap filled | Access | Status | Evidence copy | Summary PDF | Audio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Soni, S., Dudhane, A., Debary, H., Fiaz, M., Munir, M. A., Danish, M. S., Fraccaro, P., Watson, C. D., Klein, L. J., Khan, F. S., & Khan, S. (2025). EarthDial: Turning multi-sensory earth observations to interactive dialogues. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition* (pp. 14303–14313). | 2025 | CVPR | Conference (main) | 10.1109/CVPR52734.2025.01334 | **VLM for SAR + multispectral + multi-date + multi-resolution input**; the closest match to Justin's data mix | OA (CVF) | Downloaded | `evidence/earthdial-multisensory-eo-dialogue-cvpr2025-2412.15190.pdf` | `pdfs/earthdial-multisensory-eo-dialogue-cvpr2025-2412.15190-summary.pdf` | `audio/earthdial-multisensory-eo-dialogue-cvpr2025-2412.15190-summary.m4a` |
| 2 | Irvin, J. A., Liu, E. R., Chen, J. C., Dormoy, I., Kim, J., Khanna, S., Zheng, Z., & Ermon, S. (2025). TEOChat: A large vision-language assistant for temporal earth observation data. In *International Conference on Learning Representations (ICLR 2025)*. https://proceedings.iclr.cc/paper_files/paper/2025/hash/ac3af725ae398b6184faae0828bdbd6c-Abstract-Conference.html | 2025 | ICLR | Conference (main) | none (OpenReview pZz0nOroGv) | **VLM reasoning over image time sequences** (change, damage, temporal classification) | OA | Downloaded | `evidence/teochat-temporal-eo-vlm-iclr2025-2410.06234.pdf` | `pdfs/teochat-temporal-eo-vlm-iclr2025-2410.06234-summary.pdf` | `audio/teochat-temporal-eo-vlm-iclr2025-2410.06234-summary.m4a` |
| 3 | Xuan, W., Wang, J., Qi, H., Chen, Z., Zheng, Z., Zhong, Y., Xia, J., & Yokoya, N. (2025). DynamicVL: Benchmarking multimodal large language models for dynamic city understanding. In *Advances in Neural Information Processing Systems 38* (Datasets and Benchmarks Track, pp. 37321–37339). | 2025 | NeurIPS (D&B) | Conference | 10.52202/085713-1114 | **MLLM limits on long-term, quantitative change** (42 cities, 2005–2023); motivates tools and human checks | OA | Downloaded | `evidence/dynamicvl-mllm-dynamic-city-neurips2025-2505.21076.pdf` | `pdfs/dynamicvl-mllm-dynamic-city-neurips2025-2505.21076-summary.pdf` | `audio/dynamicvl-mllm-dynamic-city-neurips2025-2505.21076-summary.m4a` |
| 4 | Hou, Y., Wu, H., Zhang, Y., Liu, X., Ren, C., Lu, W., Yu, H., Huang, Y., Diao, W., Wang, Y., Li, Y., Han, B., & Sun, X. (2026). SAR foundation models: A comprehensive review of data, models, and applications. *Science China Information Sciences, 69*(8), 180301. | 2026 | Sci. China Inf. Sci. | Journal (review) | 10.1007/s11432-026-5040-3 | **State of the art for SAR foundation models and SAR vision-language models**, including SAR-optical fusion | OA (CC BY) | Downloaded (through Chrome; Springer served curl a challenge page) | `evidence/sar-foundation-models-review-scis-s11432-026-5040-3.pdf` | `pdfs/sar-foundation-models-review-scis-s11432-026-5040-3-summary.pdf` | `audio/sar-foundation-models-review-scis-s11432-026-5040-3-summary.m4a` |
| 5 | Zuo, L., Sun, J., Li, J., Liu, F., Li, J., & Niu, G. (2026). Hallucination-resistant change detection in multimodal large models for autonomous land management agents. *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 19*, 6313–6327. | 2026 | IEEE JSTARS | Journal | 10.1109/JSTARS.2026.3656403 | **MLLM change detection on optical and radar pairs, with checks against hallucination**; links SAR, change detection and safe automation | OA (CC BY) | Downloaded | `evidence/hallucination-resistant-cd-land-agents-jstars.2026.3656403.pdf` | `pdfs/hallucination-resistant-cd-land-agents-jstars.2026.3656403-summary.pdf` | `audio/hallucination-resistant-cd-land-agents-jstars.2026.3656403-summary.m4a` |
| 6 | Feng, P., Lv, Z., Ye, J., Wang, X., Huo, X., Yu, J., Xu, W., Zhang, W., Bai, L., He, C., & Li, W. (2026). Earth-Agent: Unlocking the full landscape of earth observation with agents. In *International Conference on Learning Representations (ICLR 2026)*. https://proceedings.iclr.cc/paper_files/paper/2026/hash/5b4a459db23e6db9be2a128380953d96-Abstract-Conference.html | 2026 | ICLR | Conference (main) | none (OpenReview dkIXAbWuxO) | **Agent that calls tools** (MCP, 104 tools) for quantitative spatiotemporal EO analysis; audits each reasoning step | OA | Downloaded | `evidence/earth-agent-eo-agents-iclr2026-2509.23141.pdf` | `pdfs/earth-agent-eo-agents-iclr2026-2509.23141-summary.pdf` | `audio/earth-agent-eo-agents-iclr2026-2509.23141-summary.m4a` |
| 7 | Kao, C.-H., Zhao, W., Lam, C., Umap, A., Revankar, S., Speas, S., Bhagat, S., Datta, R., Phoo, C. P., Mall, U., Vondrick, C., Bala, K., & Hariharan, B. (2026). Towards LLM agents for earth observation. In *Findings of the Association for Computational Linguistics: ACL 2026* (pp. 2597–2611). | 2026 | ACL Findings | Conference (Findings track) | 10.18653/v1/2026.findings-acl.124 | **What stays human:** measured agent failure rates on real Google Earth Engine data, including cloud and coverage failures | OA | Downloaded | `evidence/llm-agents-earth-observation-acl2026-findings.124.pdf` | `pdfs/llm-agents-earth-observation-acl2026-findings.124-summary.pdf` | `audio/llm-agents-earth-observation-acl2026-findings.124-summary.m4a` |
| 8 | Lee, B., Lee, Y.-K., & Kim, S.-W. (2026). Change type analysis for urban construction using time-series SAR data. *IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing*. Advance online publication. | 2026 | IEEE JSTARS | Journal (early access) | 10.1109/JSTARS.2026.3737141 | **SAR time-series change detection:** Sentinel-1, 2019–2023, change typed by direction, duration and periodicity | OA (CC BY-NC-ND) | Downloaded. **Early-access version**: volume and pages are not yet assigned, so cite by DOI | `evidence/sar-time-series-urban-change-types-jstars.2026.3737141.pdf` | `pdfs/sar-time-series-urban-change-types-jstars.2026.3737141-summary.pdf` | `audio/sar-time-series-urban-change-types-jstars.2026.3737141-summary.m4a` |
| 9 | Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. *Remote Sensing of Environment, 334*, 115239. | 2026 | RSE | Journal | 10.1016/j.rse.2026.115239 | **Co-registration and uneven gaps:** aligns images in feature space; handles variable-length dense high-resolution series without labels | Licensed (Elsevier) | Downloaded through the live GMU EZproxy session | `evidence/anytime-cd-dense-sits-change-detection-rse.2026.115239.pdf` | `pdfs/anytime-cd-dense-sits-change-detection-rse.2026.115239-summary.pdf` | `audio/anytime-cd-dense-sits-change-detection-rse.2026.115239-summary.m4a` |
| 10 | Michel, J., & Inglada, J. (2026). Temporal attention multi-resolution fusion of satellite image time-series, applied to Landsat-8/9 and Sentinel-2: All bands, any time, at best spatial resolution. *Remote Sensing of Environment, 334*, 115159. | 2026 | RSE | Journal | 10.1016/j.rse.2025.115159 | **Differing resolutions, cloud gaps and irregular dates:** one model predicts any band at any date at 10 m | OA (CC BY) | Downloaded (through the GMU proxy in Chrome; direct ScienceDirect showed a CAPTCHA) | `evidence/tamrf-multires-sits-fusion-landsat-s2-rse.2025.115159.pdf` | `pdfs/tamrf-multires-sits-fusion-landsat-s2-rse.2025.115159-summary.pdf` | `audio/tamrf-multires-sits-fusion-landsat-s2-rse.2025.115159-summary.m4a` |

**Coverage of Justin's interest areas:**
- **VLMs and MLLMs:** #1, #2, #3, #4 and #5. SAR is specifically covered by #1, #4 and #5.
- **Agentic automation and what stays human:** #5, #6 and #7.
- **SITS and change detection:** #2, #3, #8, #9 and #10. SAR time series is specifically covered by #8.
- **Practical problems:** co-registration in #9; resolutions in #1 and #10; cloud and revisit gaps in #9 and #10, plus the failures #7 reports.
- **Panchromatic:** a gap; see Section 2c.

### 3a. Downloaded, but not in L1 (background; moved to `evidence/.not_in_L1/`)

These are peer-reviewed, published 2023–2026 and validated. Their evidence copies were moved, not deleted, to `05_Project/evidence/.not_in_L1/`, which keeps them out of the course agents' prompts. Their summary PDFs and audio are in the library under the same base names.

| APA citation | DOI | Why not L1 | Summary PDF | Audio |
|---|---|---|---|---|
| Yuan, Z., Xiong, Z., Dujardin, T., Li, X., Mou, L., & Zhu, X. X. (2026). ChatEarthBench: Benchmarking multimodal large language models for Earth observation. *IEEE Geoscience and Remote Sensing Magazine, 14*(2), 64–84. | 10.1109/MGRS.2026.3650840 | **First alternate.** A top-venue finding that zero-shot MLLMs are weak, and weaker on Sentinel-1 SAR than on optical | `pdfs/chatearthbench-mllm-eo-benchmark-mgrs.2026.3650840-summary.pdf` | `audio/chatearthbench-mllm-eo-benchmark-mgrs.2026.3650840-summary.m4a` |
| Kuckreja, K., Danish, M. S., Naseer, M., Das, A., Khan, S., & Khan, F. S. (2024). GeoChat: Grounded large vision-language model for remote sensing. In *CVPR 2024* (pp. 27831–27840). | 10.1109/CVPR52733.2024.02629 | Superseded by EarthDial (#1); single images, RGB only | `pdfs/geochat-grounded-rs-vlm-cvpr2024-2311.15826-summary.pdf` | `audio/geochat-grounded-rs-vlm-cvpr2024-2311.15826-summary.m4a` |
| Stucker, C., Sainte Fare Garnot, V., & Schindler, K. (2023). U-TILISE: A sequence-to-sequence model for cloud removal in optical satellite time series. *IEEE Transactions on Geoscience and Remote Sensing, 61*, Article 5408716. | 10.1109/TGRS.2023.3333391 | Covered by #10 (which compares against it); optical only | `pdfs/u-tilise-cloud-removal-sits-tgrs.2023.3333391-summary.pdf` | `audio/u-tilise-cloud-removal-sits-tgrs.2023.3333391-summary.m4a` |
| Grich, S., Elfarkh, J., Ouaadi, N., Ait Hssaine, B., Halim, H., & Chehbouni, A. (2026). Evaluating Sentinel-2 gap filling techniques for cloud removal and data reconstruction. *Scientific Reports, 16*, 9464. | 10.1038/s41598-026-39488-2 | Optical only; single site | `pdfs/sentinel2-gap-filling-evaluation-s41598-026-39488-2-summary.pdf` | `audio/sentinel2-gap-filling-evaluation-s41598-026-39488-2-summary.m4a` |
| Simarro, G., Calvete, D., Ribas, F., Castillo, Y., & Puig-Polo, C. (2025). UOrtos: Methodology for co-registration and subpixel georeferencing of satellite imagery for coastal monitoring. *Remote Sensing, 17*(7), 1160. | 10.3390/rs17071160 | Was only needed while #9 looked unfetchable; optical only; classical method | `pdfs/uortos-coregistration-subpixel-satellite-rs17071160-summary.pdf` | `audio/uortos-coregistration-subpixel-satellite-rs17071160-summary.m4a` |
| Im, Y., & Lee, Y. (2026). Robust multi-resolution satellite image registration using deep feature matching and super resolution techniques. *Applied Sciences, 16*(2), 1113. | 10.3390/app16021113 | Weaker venue; one urban site; optical only | `pdfs/multires-satellite-registration-superres-app16021113-summary.pdf` | `audio/multires-satellite-registration-superres-app16021113-summary.m4a` |

### 3b. Alternates (Relevant and peer-reviewed; not downloaded)

The relevance-checker ranked these in this order:
1. **ChatEarthBench** (above; already downloaded).
2. **Shu, Q., Zhu, X., Xu, S., Wang, Y., & Liu, D. (2025).** RESTORE-DiT: Reliable satellite image time series reconstruction by multimodal sequential diffusion transformer. *Remote Sensing of Environment, 328*, 114872. https://doi.org/10.1016/j.rse.2025.114872.
   - Access: OA at Elsevier. It can be fetched through the GMU-proxy route that worked for #9 and #10.
   - Uses SAR to fill cloudy optical time series. Swap it in for #10 if the study area is cloud-prone.
3. **ST1 SAMSR.** A vision foundation model-based method for large-scale forest disturbance mapping using time series Sentinel-1 SAR. *Remote Sensing of Environment* (2025). https://doi.org/10.1016/j.rse.2025.114775.
   - Access: licensed; the GMU proxy works.
   - Full author list **TO VERIFY**; it was not pulled into this report.
4. **SV2 SAREval.** A multi-dimensional, multi-task benchmark for evaluating visual language models on SAR image understanding. *Remote Sensing* (published online 2025-12-25). https://doi.org/10.3390/rs18010082.
   - Access: OA.
   - Volume and article number **TO VERIFY**.

Already in Justin's course readings: Li, Z., Ning, H., Gao, S., Janowicz, K., et al. (2025). GIScience in the era of Artificial Intelligence: A research agenda towards Autonomous GIS. *Annals of GIS, 31*(4), 501–536. https://doi.org/10.1080/19475683.2025.2552161. It frames levels of autonomy, which bears on what stays human.

## 4. Non-peer-reviewed or workshop-only background (not eligible for L1)

| Item | Status | Link |
|---|---|---|
| Yu, B., Yang, C., Hou, D., et al. (2026). GeoAgentBench: A dynamic execution benchmark for tool-augmented agents in spatial analysis. | arXiv preprint only (course reading) | arXiv:2604.13888 |
| Shabbir, A., Munir, M. A., Dudhane, A., et al. ThinkGeo: Evaluating tool-augmented agents for remote sensing tasks. | CVPR 2026 Workshop (MONTI) paper. Workshop peer review only; an ICLR 2026 submission was withdrawn | arXiv:2505.23752 |
| Talemi, N. A., Boone, J., & Afghah, F. (2026). Agentic AI in remote sensing: Foundations, taxonomy, and emerging systems. | WACV 2026 Workshops (GeoCV), pp. 786–799. Workshop | arXiv:2601.01891 |
| Munir, M. A., Sheikh, M. U., Shabbir, A., et al. Agentic AI for remote sensing: Technical challenges and research directions. | arXiv position paper, 2026 | arXiv:2604.24919 |
| Lee, C., Paramanayakam, V., Karatzas, A., et al. (2025). Multi-agent geospatial copilots for remote sensing workflows. | arXiv preprint | arXiv:2501.16254 |
| Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2024). AI agents that matter. | Copy held is arXiv; peer-reviewed version **TO VERIFY** | arXiv:2407.01502 |
| SARChat-Bench-2M: A multi-task vision-language benchmark for SAR image interpretation (2025) | arXiv only; strong SAR-VLM benchmark | arXiv:2502.08168 |
| SARVLM: A vision language foundation model for semantic understanding in SAR imagery (2025) | arXiv only | arXiv:2510.22665 |
| FUSAR-R1: A large-scale reasoning model for intelligent interpretation of SAR images (2026) | arXiv only | arXiv:2607.16819 |
| FUSAR-GPT: A spatiotemporal feature-embedded and two-stage decoupled visual language model for SAR imagery (2026) | arXiv only; SAR + time series + VLM | arXiv:2602.19190 |

Author lists for the four SAR arXiv items were not pulled. Check them on arXiv before citing.

Free arXiv versions of the three shortlisted IEEE papers that need a login are also available for reading: Liu et al. survey 2412.02573, Change-Agent 2403.19646 and Miller et al. 2404.03936. Cite the published IEEE versions.

---

## 5. Papers still needing Justin's GMU login

All three are IEEE Xplore papers. GMU's EZproxy session was live, but IEEE answered the automated browser with a bot-challenge page. I did not try to get past it. Opening these in Justin's own browser through the GMU proxy should work.

| Paper | GMU proxy link | Free preprint (for reading only) |
|---|---|---|
| Liu et al. (2026), Remote sensing spatiotemporal VLMs: A comprehensive survey, *IEEE GRSM* | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/MGRS.2025.3598283 | https://arxiv.org/abs/2412.02573 |
| Liu et al. (2024), Change-Agent, *IEEE TGRS* | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/TGRS.2024.3425815 | https://arxiv.org/abs/2403.19646 |
| Miller, Pelletier & Webb (2024), Deep learning for SITS analysis: A review, *IEEE GRSM* | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/MGRS.2024.3393010 | https://arxiv.org/abs/2404.03936 |

Relevant SAR papers behind IEEE's login wall. They were not attempted, because the coordinator said to skip anything behind a login wall. All three were rated Marginal only because they could not be fetched; on topic, each is strong.

| Paper | GMU proxy link |
|---|---|
| SARLANG-1M: A benchmark for vision-language modeling in SAR image understanding, *IEEE TGRS* (2026) | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/TGRS.2026.3652099 |
| RadarMind: Explainable chain-of-thought reasoning for SAR image interpretation with large vision-language models, *IEEE TAES* (2026) | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/TAES.2026.3719218 |
| SAR-TSCC: A novel approach for long time series SAR image change detection and pattern analysis, *IEEE TGRS* (2023) | https://mutex.gmu.edu/login?url=https://doi.org/10.1109/TGRS.2023.3243900 |

Once a paper is saved, put it in `Personal/research/agentic-geoai-satellite-imagery/pdfs/` and re-run the pipeline from completeness Mode 2. If it joins L1, copy the clean original into `05_Project/evidence/` before the summary step.

---

## Pipeline verification log

- **Relevance check:** the relevance-checker sub-agent rated 71 candidates, then 4 supplementary co-registration candidates, then 29 SAR and panchromatic candidates. It produced the final 10-paper L1.
- **Completeness Mode 1 (pre-save):**
  - The 14 curl or browser downloads were checked in staging against expected page ranges and first-page titles. All passed.
  - S12 (18 pages) and S11 (35 pages) were checked in the Chrome PDF viewer. Both passed.
  - SV4 (40 pages, a Springer download through Chrome) and ST4 (11 pages, IEEE OA, early access) were checked in staging. Both passed.
  - Earlier failures were caught before saving: OpenReview (12 KB challenge pages), ScienceDirect (HTML), MDPI (409-byte "Access Denied") and UPCommons (HTML).
- **Completeness Mode 2 (post-save):** all 14 library files passed. Each was checked by the Read tool's page count, `file`, size and page-1 title.
  - All 16 library files passed.
  - Page counts: TEOChat 29, Earth-Agent 65, DynamicVL 19, EarthDial 11, GeoChat 10, Kao et al. 15, Zuo et al. 15, ChatEarthBench 21, U-TILISE 16, Grich et al. 26, UOrtos 23, Im & Lee 29, AnyTime-CD 18, TAMRF 35, SAR FM review 40, SAR change types 11.
  - For TAMRF, the last page was confirmed to be references, so the file is not truncated.
- **Evidence copies:** each copy is byte-identical (`cmp`) to the validated original. The copies were made *before* the summary-annotator ran, so they have no AI summary page.
  - `05_Project/evidence/` holds exactly the 10 L1 PDFs, plus the pre-existing `.gitkeep`.
  - The 6 non-L1 downloads were moved, not deleted, to `05_Project/evidence/.not_in_L1/`.
- **Summary and audio:** the summary-annotator built each summary page with one shared layout script. The narrator then made macOS `say` audio from the summary prose only.
- **Plain originals left in `pdfs/`:** the pipeline normally deletes each plain original once its `-summary.pdf` is verified. For some files, the auto-mode permission classifier blocked that `rm`. I did not get around the block. The affected originals are still in `Personal/research/agentic-geoai-satellite-imagery/pdfs/` next to their `-summary.pdf`. Byte-identical clean copies are in `evidence/` or `evidence/.not_in_L1/`, so Justin can safely delete these leftovers himself or keep them. The 8 leftover originals are:
  - `chatearthbench-mllm-eo-benchmark-mgrs.2026.3650840.pdf`
  - `earthdial-multisensory-eo-dialogue-cvpr2025-2412.15190.pdf`
  - `hallucination-resistant-cd-land-agents-jstars.2026.3656403.pdf`
  - `llm-agents-earth-observation-acl2026-findings.124.pdf`
  - `multires-satellite-registration-superres-app16021113.pdf`
  - `sar-foundation-models-review-scis-s11432-026-5040-3.pdf`
  - `tamrf-multires-sits-fusion-landsat-s2-rse.2025.115159.pdf`
  - `teochat-temporal-eo-vlm-iclr2025-2410.06234.pdf`
- **Final counts:**
  - 16 `-summary.pdf` files and 16 `.m4a` narrations of 3.2–4.0 minutes each, all verified with `file` and `afinfo`.
  - 10 L1 PDFs in `evidence/` and 6 in `evidence/.not_in_L1/`.
  - Every path cited in this report was checked on disk.

## Points to check when reading

The summary-annotators flagged these from their full reads. Each one comes from the paper itself, not from the summary.

**Internal inconsistencies:**
- **Grich et al. 2026:** the text says SSRF has R-squared of 0.95 or above for all bands except B11. Fig. 14c shows about 0.86–0.94 for B02–B04.
- **EarthDial:** the text says band fusion improves average accuracy by 13.5%. The Table 13 caption says 9.5%.
- **Im & Lee 2026:** the abstract says all deep matchers stay below 0.5 px. Table 3 shows 0.51 px for SPSG on the KOMPSAT-3A to KOMPSAT-3 pair.
- **Kao et al. 2026:** the limitations section calls the benchmark "OpenEARTH" instead of UnivEARTH.
- **Lee, Lee & Kim 2026 (ST4, L1 #8):**
  - The regular-cycle row of Table II sums to 176, but the text gives n = 174, so the table totals 1,464 rather than 1,462.
  - The per-class F1 values quoted in the text (1.00 and 0.97) do not match Table II, which gives about 0.968 and 0.958.
  - The headline "overall F1 0.94" is never defined. It matches the 8-class macro F1.
- **Hou et al. 2026 (SV4, L1 #4):**
  - The conclusion gives SAR-optical gains as "about 5–6 mAP", but Section 5 gives 6.1 mAP for CROMA.
  - The text says SSL4EO-S12 has "millions" of SAR patches, while Table 4 lists 246,000.
- **Qu, Li & Huang 2026 (AnyTime-CD, L1 #9):**
  - The abstract's "+4.44% / +9.09% over SOTA" uses two different baselines.
  - The "+30% thin cloud" row of Table 11 is identical to the "+10%" row.
  - The cloud-robustness test uses a variant that does spatial alignment only.
  - The data are available only on request, and no code is released.
- **Michel & Inglada 2026 (TAMRF, L1 #10):**
  - Image counts in Section 3.1 conflict with Table 3; the table's figures add up.
  - The BRISQUE "always lowest" claim is contradicted by Table A.14 for bands B2 and B3.
  - The "gain of 0.01 RMSE" holds only for the visible bands.

**Earth-Agent:**
- Some appendix worked examples are scored Acc 100% even though a tool call failed (Figs. 29, 33 and 34).
- Change detection is only 13 of its 248 questions.
- There is no co-registration or resampling tool in its 104-tool kit.

**Missing information:**
- **UOrtos:** the paper gives no number for the size of the rotation it recovered at Gandia.
- **Zuo et al. 2026:** the LLM backbone is not named.

**Scope:** DynamicVL's 19-page proceedings PDF points to appendices that sit in a separate supplement, which was not downloaded.
