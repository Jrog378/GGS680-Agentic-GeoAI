# Stage 3: Scientific Writer: Proposed-Study Abstract (v1)

- **Source packet:** `outputs/prompt_packets/03_writer_abstract.md` (generated 2026-10-04 22:49)
- **Status:** Proposal only. No data have been downloaded and no results exist. No novelty, causal, policy or external-validity claim is made (AGENTS.md rule 9).
- **Inputs used:** H3 (selected question, hypothesis, scope; followed as written), H1 (decision log, including the last row reinstating the VLM comparison), H5 (journal scope only), the ten human-verified L1 references and their (truncated) evidence text, `outputs/research_questions.md` (Q-A design) and `outputs/question_review.md` (Q-A-R revisions).
- **Citation rule:** only the ten L1 references are cited. No impact factor is stated.

---

## Abstract

Vision-language models (VLMs) and tool-using large language model (LLM) agents are increasingly proposed for interpreting satellite image time series, yet their reliability remains low: coding agents reach about 60% on yes/no Earth observation questions even with reflexion (Kao et al., 2026), the best of 18 multimodal models scores 34.1% on a long-term urban benchmark (Xuan et al., 2025), and hallucinated change is a recognised failure (Zuo et al., 2026). None of the papers we reviewed tests whether grounding an LLM in deterministic sensor tools makes it more accurate, and less prone to fabrication, than a VLM reading the imagery directly, or what its reasoning adds beyond non-agent rules given the same tool outputs. We will test this in 10–20 SpaceNet 7 areas (2017–2020), holding whole areas out for testing. For each sampled 100 m cell, an LLM agent will call predefined Sentinel-1 and Landsat-8 15 m panchromatic time-series tools and report whether new buildings appeared and in which month, or abstain. On the same stratified cells it will be compared with a VLM shown about 1 km image chips (cell outlined, up to 8 dates), and with a tuned rule and a fitted rule that receive identical tool outputs. We hypothesise that tool grounding reduces hallucination: the agent will be more accurate than the VLM and fabricate fewer answers, and at least as accurate as the non-agent baselines, with gains where the tools disagree. Monthly SpaceNet 7 building footprints, traced on separate imagery, provide an independent reference. We will report presence-F1 and onset-error differences with area-cluster bootstrap confidence intervals, fabricated answers on pre-registered unanswerable queries, the VLM's input limits, and a tools-disabled control against memorised answers. The study will separate the value of tool grounding from that of LLM reasoning in multi-sensor change interpretation.

---

## Contribution

**Framing for the target journal (International Journal of Digital Earth).** The journal's stated scope (H5) covers Earth observation, big Earth data and AI-driven geospatial analysis. We frame the contribution as extending tool-using geospatial agents to interpreting multi-sensor satellite image time series, with a pre-registered, test-level comparison against a direct-imagery VLM and against non-agent baselines. Gap statements below refer only to the ten supplied papers ("not found in our search"); they are not novelty claims.

1. **Soni et al. (2025), EarthDial** (doi:10.1109/CVPR52734.2025.01334)
   - *Established:* a conversational EO VLM, instruction-tuned on over 11 million pairs spanning RGB, SAR and multispectral data, that handles bi- and multi-temporal sequences for change detection and outperforms generic and domain models on 44 datasets.
   - *This work adds:* a same-cell, same-label test of whether reading multi-temporal imagery directly, as such VLMs do, is more or less accurate and fabrication-prone than querying sensor tools for new-building presence and month.
2. **Irvin et al. (2025), TEOChat** (OpenReview pZz0nOroGv)
   - *Established:* a VLM for temporal EO sequences (including building change and damage) that outperforms earlier assistants and GPT-4o and Gemini 1.5 Pro on several temporal tasks; its training sequences are capped at 8 images for memory reasons.
   - *This work adds:* evaluates a direct-imagery VLM at that frame limit against an agent that reads the full monthly series through tools, and reports the VLM's input limits explicitly.
3. **Xuan et al. (2025), DynamicVL** (doi:10.52202/085713-1114)
   - *Established:* a benchmark of 18 multimodal LLMs on long-term urban dynamics in 42 U.S. cities (1 m imagery, 2005–2023); the best model reached 34.1% overall QA accuracy, exposing weak long-term temporal and quantitative reasoning.
   - *This work adds:* tests whether routing a narrow urban-change question through deterministic SAR and panchromatic tools, rather than direct image reading, improves accuracy, scored against an independent monthly reference.
4. **Hou et al. (2026), SAR foundation models review** (doi:10.1007/s11432-026-5040-3)
   - *Established:* a taxonomy of SAR foundation models (visual, multimodal including SAR–optical synergy and vision-language, and generative), a description of side-looking effects such as layover, and multimodal SAR agents as a future direction.
   - *This work adds:* an empirical test of one form of that direction, an LLM agent reading Sentinel-1 time-series tools, with layover handled by a look-direction neighbour sensitivity check.
5. **Zuo et al. (2026), hallucination-resistant change detection** (doi:10.1109/JSTARS.2026.3656403)
   - *Established:* a fine-tuned multimodal LLM with a change-vector-analysis calibration loop and self-consistency that suppresses hallucination in change detection and improves prediction precision.
   - *This work adds:* tests tool grounding without fine-tuning as a hallucination control, counting fabricated answers on pre-registered unanswerable queries and comparing the agent with a direct-imagery VLM.
6. **Feng et al. (2026), Earth-Agent** (OpenReview dkIXAbWuxO)
   - *Established:* a ReAct-style EO agent integrating 104 specialised tools across RGB and spectral modalities, evaluated at both trajectory and answer level on Earth-Bench.
   - *This work adds:* applies the curated-tool agent design to SAR plus panchromatic time series, and adds tuned and fitted non-agent baselines given identical tool outputs, isolating what the LLM's reasoning contributes beyond the tools.
7. **Kao et al. (2026), LLM agents for EO** (doi:10.18653/v1/2026.findings-acl.124)
   - *Established:* on 408 yes/no EO questions, Earth Engine coding agents reached 40.0% with code failing over 44% of the time; reflexion raised accuracy to about 60%, still only marginally above chance.
   - *This work adds:* tests whether predefined, deterministic tools (no free-form code) yield reliable answers, with failures and abstentions scored by fixed rules adapted from their categories; conclusions are limited to curated tool environments.
8. **Lee et al. (2026), SAR time-series urban change types** (doi:10.1109/JSTARS.2026.3737141)
   - *Established:* fine-grained construction change types from Sentinel-1 GRD time series (2019–2023) using likelihood-ratio testing and spectral clustering, with an overall F1 of 0.94 on their reference and links to construction phases.
   - *This work adds:* adapts their likelihood-ratio framework into a per-cell change-month tool (a new adaptation, validated standalone) and estimates the lag between SAR change and independent monthly building labels.
9. **Qu et al. (2026), AnyTime-CD** (doi:10.1016/j.rse.2026.115239)
   - *Established:* self-supervised change detection for arbitrary-length dense high-resolution time series that approaches or exceeds supervised methods; it describes the monthly-labelled MUDS (SpaceNet 7) data and shows that misalignment creates pseudo-change.
   - *This work adds:* uses the MUDS labels as an independent reference for coarser 10–15 m sensors and for agent and VLM answers at 100 m and monthly scale, with a one-pixel misregistration robustness check.
10. **Michel & Inglada (2026), TAMRF-SITS** (doi:10.1016/j.rse.2025.115159)
    - *Established:* a general masked-autoencoder fusion of variable-length Landsat-8/9 and Sentinel-2 series that predicts all bands at the best resolution and any date, on par with or better than ad hoc methods on four tasks.
    - *This work adds:* keeps the raw Landsat-8 panchromatic band and Sentinel-1 as separate tool outputs and asks, as a secondary pipeline analysis on all test cells, whether panchromatic adds anything to SAR for new-building detection.

---

## Assumptions and unresolved items

1. **Which VLM, and which imagery it sees.** H3 says the VLM "looks at the imagery directly" but does not name the model or say whether it sees panchromatic chips, rendered SAR chips, or both. The abstract assumes the same panchromatic and SAR imagery the tools read. H1 earlier flagged VLM setup (e.g. EarthDial or TEOChat) as a schedule risk; that risk returns with the reinstated arm.
2. **Primary endpoint.** H1 fixed presence-F1 against the pipeline as the single primary endpoint, then replaced the non-inferiority margin with an estimation framing, and finally reinstated the VLM as the "main comparison". The abstract reports differences with confidence intervals and leads with agent vs VLM; Justin should confirm which contrast is primary before pre-registration.
3. **Baselines.** "Tuned rule" = the fusion rule tuned on development areas (P1); "fitted rule" = the information-matched rule fitted on the same tool outputs (P2), as accepted in H1.
4. **Fabrication.** Assumed to be measured as non-abstaining answers on pre-registered unanswerable queries (no valid data, or months outside the archive). How the VLM is offered an abstain option, and whether fabrication also covers unsupported evidence citations, is not yet defined.
5. **Data and power unknown.** Nothing has been downloaded. Sentinel-1 coverage per area, usable panchromatic months, new-building cell counts, per-building IDs and the grid CRS are unverified; with 8–14 test areas, cluster-bootstrap intervals may be wide [citation needed for few-cluster coverage].
6. **Tools.** The SAR change-month tool is a new adaptation of Lee et al.'s framework and the panchromatic normalisation method is unchosen [citation needed]; both need standalone validation.
7. **Process caveats.** The H1 rows were drafted by Claude and only partly reviewed by Justin; Stage 1, Stage 2 and this abstract are all LLM outputs, so their agreement is not validation. Evidence text was truncated at 20,000 characters per paper. No search beyond the ten papers was done, so the gap sentence in the abstract is limited to those papers.
8. **Excluded by instruction.** The three IJDE papers named in H5 are not cited, and no impact factor is stated.

**Next scientific action:** Justin confirms the VLM model, its inputs and the primary contrast, then the W1 data inventory and a pre-registration are written to `outputs/` before any test-area run.
