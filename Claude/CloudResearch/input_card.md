# Input card: cloud research proposal

Run of the Assignment 3 research-proposal workflow (roles in `Claude/05_Project/agents/`, rules in
`Claude/05_Project/AGENTS.md`). Started 2026-10-23 at Justin's request: "lets take this idea and run with it".
Products go in `Claude/CloudResearch/`. Justin is the human in the loop.

## Broad research problem
Clouds can hide target areas in images taken after disasters. This can lead to labels being inaccurate compared to
ground truth due to obscured parts of the imagery. How should we detect clouds in this imagery, handle them, and
report them? The goal is results, such as maps of flooded roads, that people can trust.

(Justin's wording, 2026-10-23.)

## Scope
General framing (any object, any hazard), with flooded roads after Hurricane Ida (SpaceNet 8 Louisiana-East) as the
test case. This follows the project's universality goal: the pipeline must adapt to any hazard, sensor or cloud.

## Boundary conditions
- The problem must contain a meaningful spatial component.
- The investigation must be achievable with public or research-accessible data.
- The aim is a testable research question, not a descriptive mapping exercise.
- The methodology must contain an explicit validation strategy.
- The paper must be completable and submittable to a peer-reviewed journal within eight weeks, using AI-assisted
  coding and analysis.
- Imagery: very high resolution optical (about 0.5 m), used in greyscale after the first step (the project's rule).
  There are no SWIR or thermal bands.
- Development data only: SpaceNet 8 Louisiana-East training and validation tiles, and the HRC_WHU development images.
  These stay sealed until a frozen setup's one logged check: the SpaceNet 8 test tiles, the north negative set, the
  sealed areas (Germany, Louisiana-West) and the HRC_WHU test images.
- Labels: published human labels only, used unmodified, for training and scoring. No own, pseudo or VLM labels.
- Roles: DINO (open DINOv2 weights) detects change. A VLM (Gemma) may describe and interpret, but never makes the
  decision.
- Research-only data (CC BY-SA, academic use only) may be used now. The pipeline is made licence-compliant later.
- Citations: journals with a JIF of at least 4.0 (AGENTS.md), or major peer-reviewed conferences, labelled as
  conference papers. Datasets and older foundational methods are cited as attributions.

## Domain notes
- Measured results: `evidence/01_measured_results.md` (our own measurements, development data).
- Literature summary and cloud-label datasets: `evidence/02_cloud_literature_summary.md`.
- Full notes:
  - `~/Masters/GGS662/ProjectBranch/Literature/notes/clouds.md` and `clouds_review_web.md`;
  - the dev log, `~/Masters/GGS662/Project/docs/devlog.md` (2026-10-23 entries).
- Courses: classical cloud masks belong to GGS 680. DINO features and agentic gates or routing belong to GGS 662. The
  VLM reading and describing what is visible belongs to CSI 709.

## Candidate references (2023-2026; Justin verifies before any novelty claim)
- Portalés-Julià et al. 2023, Scientific Reports 13:20316, DOI 10.1038/s41598-023-47595-7 (JIF 4.9)
- Zou et al. 2025, Cloud-Adapter, IEEE TGRS, DOI 10.1109/TGRS.2025.3597410 (JIF 9.4)
- Qu, Li & Huang 2026, AnyTime-CD, Remote Sensing of Environment 334:115239, DOI 10.1016/j.rse.2026.115239 (JIF 12.3)
- Song et al. 2023, DehazeFormer, IEEE TIP 32:1927-1941, DOI 10.1109/TIP.2023.3256763 (JIF 13.7; confirm in JCR)
- Guo et al. 2024, SkySense, CVPR 2024, DOI 10.1109/CVPR52733.2024.02613 (conference; Ant Group)
- Hou et al. 2026, SAR foundation models review, Sci. China Inf. Sci. 69(8):180301, DOI 10.1007/s11432-026-5040-3
  (JIF 8.1, year unverified)

## Human decisions so far
See `decision_log.md`. In short: keep R2 as "What can a flood-road map reliably tell users about roads hidden by
cloud?". Rebuild R1 around generating synthetic clouds. Replace R3: no question framed on the 20% cut-off, and no
DINOv2-vs-classical comparison as the frame.

## Selected questions (Justin, 2026-10-23)
Order: **Q2 (lead), Q3, Q1.** Details are in `outputs/research_questions_refined_v3.md`; wording is to be checked against
`evidence/04_research_question_guide.md`.
1. **Q2 (lead):** What can a flood-road map reliably tell users about roads hidden by cloud?
2. **Q3:** When only the before image is cloudy, can the after image alone still show what changed?
3. **Q1 (last, Justin's wording):** Can we use synthetic clouds to represent real-life blockages in satellite imagery?
