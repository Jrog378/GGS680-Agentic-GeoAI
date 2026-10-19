# Broad research problem

How can Agentic GeoAI help interpret large sources of satellite imagery in an area of interest to understand patterns and changes over time?

## Initial boundary conditions

- The problem must contain a meaningful spatial component.
- The investigation should be achievable with public or research-accessible data.
- The aim is to produce a testable research question, not merely a descriptive mapping exercise.
- The methodology must contain an explicit validation strategy.
- The paper must be completable and submittable to a peer-reviewed journal within eight weeks, using AI-assisted coding and analysis.

## Human notes

I am hoping to use panchromatic (black-and-white) and SAR imagery to start. Proposed data (found with Claude Code on 2026-10-04 at my request; to be confirmed after download):

- **Panchromatic time series: MuRA-T** (Purdue Robot Vision Lab, https://engineering.purdue.edu/RVL/Database/murat/index.html).
  - **What it is:** monthly Landsat-8 and Sentinel-2 stacks added to the 60 SpaceNet 7 training AOIs worldwide.
  - **Time span:** about 24 months per AOI between 2017 and 2020. Each month uses the least-cloudy Landsat scene; some months are missing.
  - **Bands:** Landsat-8 OLI band 8 (panchromatic, 15 m, 0.50–0.68 µm) is included, along with bands 1–11, the QA band and a cloud mask.
  - **Alignment:** all bands are already co-registered to the SpaceNet 7 grid; the authors report sub-pixel alignment.
  - **Product and size:** Landsat Collection 1 Level-1 (L1TP). The Landsat archive is 1.5 GB and the Sentinel-2 archive 5.3 GB.
  - **Status:** GPL v3. It is described in a 2023 arXiv preprint (not peer-reviewed), so I treat it as a data source, not a reference.
- **Reference labels: SpaceNet 7 / MUDS** (the public, monthly-labelled dataset described by Qu et al., 2026).
  - **What it is:** monthly building-footprint polygons for the same AOIs, traced on about 4 m Planet RGB mosaics.
  - **Dating:** each building keeps one ID across months, so the month it first appears can be dated.
  - **Licence and access:** CC BY-SA 4.0, free on AWS Open Data (`spacenet-dataset` bucket).
  - **Independence:** the labels are traced on different imagery from the panchromatic and SAR data, so they are independent of both.
  - **Caveat:** a label marks when a building becomes visible, which is closer to completion than to the start of construction.
- **SAR: Sentinel-1 C-band GRD** for the same AOIs and months.
  - **Work needed:** I must download it and co-register it to the MuRA-T grid myself, e.g. from Google Earth Engine (`COPERNICUS/S1_GRD`) or Planetary Computer (`sentinel-1-rtc`).
  - **Coverage:** Sentinel-1A and 1B were both operating in 2018–2020. The number of scenes, the orbit direction and the polarisations vary by AOI (TO VERIFY per AOI).
- **Study area:** a subset of the 60 AOIs (e.g. 10–20), chosen for the most new buildings and the best Sentinel-1 coverage. Whole AOIs will be held out for testing, so training and test areas never overlap.
- **Time period:** the SpaceNet 7 window (about 24 monthly steps per AOI, 2017–2020).
- **Change of interest:** new buildings and urban development, which is what SpaceNet 7 labels.
- **Fallback if MuRA-T doesn't work:** Landsat 8/9 Collection 2 band 8 for the same AOIs, from USGS Level-1 products (EarthExplorer or the AWS `usgs-landsat` bucket) or Earth Engine's TOA collections. I would then co-register it myself. Level-2 surface reflectance products have no panchromatic band.

### References the agents may cite (read and verified by Justin; full PDFs in Claude/05_Project/evidence/)

- Soni, S., Dudhane, A., Debary, H., Fiaz, M., Munir, M. A., Danish, M. S., Fraccaro, P., Watson, C. D., Klein, L. J., Khan, F. S., & Khan, S. (2025). EarthDial: Turning multi-sensory earth observations to interactive dialogues. Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 14303–14313. DOI: 10.1109/CVPR52734.2025.01334
- Irvin, J. A., Liu, E. R., Chen, J. C., Dormoy, I., Kim, J., Khanna, S., Zheng, Z., & Ermon, S. (2025). TEOChat: A large vision-language assistant for temporal earth observation data. International Conference on Learning Representations (ICLR 2025). OpenReview: pZz0nOroGv
- Xuan, W., Wang, J., Qi, H., Chen, Z., Zheng, Z., Zhong, Y., Xia, J., & Yokoya, N. (2025). DynamicVL: Benchmarking multimodal large language models for dynamic city understanding. Advances in Neural Information Processing Systems 38 (Datasets and Benchmarks Track), 37321–37339. DOI: 10.52202/085713-1114
- Hou, Y., Wu, H., Zhang, Y., Liu, X., Ren, C., Lu, W., Yu, H., Huang, Y., Diao, W., Wang, Y., Li, Y., Han, B., & Sun, X. (2026). SAR foundation models: A comprehensive review of data, models, and applications. Science China Information Sciences, 69(8), 180301. DOI: 10.1007/s11432-026-5040-3
- Zuo, L., Sun, J., Li, J., Liu, F., Li, J., & Niu, G. (2026). Hallucination-resistant change detection in multimodal large models for autonomous land management agents. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 19, 6313–6327. DOI: 10.1109/JSTARS.2026.3656403
- Feng, P., Lv, Z., Ye, J., Wang, X., Huo, X., Yu, J., Xu, W., Zhang, W., Bai, L., He, C., & Li, W. (2026). Earth-Agent: Unlocking the full landscape of earth observation with agents. International Conference on Learning Representations (ICLR 2026). OpenReview: dkIXAbWuxO
- Kao, C.-H., Zhao, W., Lam, C., Umap, A., Revankar, S., Speas, S., Bhagat, S., Datta, R., Phoo, C. P., Mall, U., Vondrick, C., Bala, K., & Hariharan, B. (2026). Towards LLM agents for earth observation. Findings of the Association for Computational Linguistics: ACL 2026, 2597–2611. DOI: 10.18653/v1/2026.findings-acl.124
- Lee, B., Lee, Y.-K., & Kim, S.-W. (2026). Change type analysis for urban construction using time-series SAR data. IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing (early access; volume/pages not yet assigned). DOI: 10.1109/JSTARS.2026.3737141
- Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. Remote Sensing of Environment, 334, 115239. DOI: 10.1016/j.rse.2026.115239
- Michel, J., & Inglada, J. (2026). Temporal attention multi-resolution fusion of satellite image time-series, applied to Landsat-8/9 and Sentinel-2: All bands, any time, at best spatial resolution. Remote Sensing of Environment, 334, 115159. DOI: 10.1016/j.rse.2025.115159


## Human decision after stages 1–2 (Justin, the human supervisor)

The course critic recommended a fusion question (R1) and rejected the agent-vs-multimodal-model question (R3) as primary. I keep my own selection, from my Assignment 3 decision log (H3), and take the critic's fusion question as a secondary analysis, run both ways:

- Selected question (final wording): In held-out SpaceNet 7 areas (2017–2020), does a tool-grounded LLM agent detect new buildings in 100 m cells (presence and onset month) more accurately than a VLM viewing the same imagery and than non-agent baselines given the same tool outputs?
- Why it is the strongest of the three: It answers my core interest (VLMs vs tool-grounded agents) and the broad problem. The baselines isolate what the agent's reasoning adds. It is feasible at test level with existing labels. Q-B becomes a pipeline-first secondary analysis, and Q-C is deferred (fine, just not my favourite).
- Main hypothesis: Tool grounding reduces hallucination. The tool-using agent is more accurate than the VLM and fabricates fewer answers. Against non-agent baselines given the same tool outputs (a tuned rule and a fitted rule), it is at least as accurate (difference reported with an AOI-cluster confidence interval) and better where the tools disagree.
- Scope (study area, time period, unit of analysis): 10–20 MuRA-T / SpaceNet 7 areas (whole areas held out for testing), monthly 2017–2020, 100 m cells. The LLM agent and the VLM get exactly the same inputs: the same 1 km image chip (centred on the 100 m square being asked about, with that square outlined; Landsat-8 panchromatic at 15 m resolution, Sentinel-1 at 10 m pixel spacing, about 20 m resolution), the same 8 dates and the same question. New buildings only: development visible at 15 m resolution, not single houses. A test-level study on a stratified sample of cells.
(Wording drafted by Claude from Justin's decisions; approved by Justin 2026-10-04.)
