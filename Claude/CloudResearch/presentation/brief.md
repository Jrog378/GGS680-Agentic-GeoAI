# Design brief: "Seeing Through Clouds"

## The talk
- **Presenter:** Justin Rogers, MS student, George Mason University.
- **Course / venue:** GGS 662 Agentic GeoAI (Ed Oughton), Assignment 4: refined methods and preliminary research results.
- **Event:** class presentation, Friday 30 October 2026, 11am, with guest David Attaway of AWS. **4 minutes.**
  - The PDF is due Sunday 25 October 2026, 11:59pm.
  - 7 main slides, plus supporting slides after them.
  - Audience: classmates, the instructor and an industry guest. Treat it as a professional research briefing.
- **The project, in plain words:**
  - Clouds hide parts of the images taken after a disaster.
  - The human labels are wrong there too: SpaceNet 8's analysts only marked what they could see, so a road hidden by
    cloud reads as "not flooded".
  - Re-running the Assignment 3 research workflow (role agents + human decisions) turned this into a research area:
    detect cloud, handle it (see through it with the second image, or say "cannot assess"), and report what a map
    can reliably say.
  - Pilot so far:
    - the labels under cloud are biased;
    - greyscale cloud masks were checked against human cloud labels;
    - a two-date de-hazing prototype recovers some flooded roads.
- **Domain:** Earth observation / remote sensing (disaster change detection).
- **Theme:** reuse theme "night-pass" unchanged (the house style). The design specs are in `design/`; example
  slides are in `~/Masters/SchoolAgents/deck-designer/themes/night-pass/examples/`.
- **Output:** local files only (Justin: "use files in the CloudResearch folder not artifacts"). The deck is rendered
  to PNG and PDF with deckkit; nothing is published.

## Figures (Read them to see them)
Folder: `/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/presentation/assets/`. Every figure is
matplotlib on white. Colours are Night Pass roles: teal `#0A7570`, amber `#FCA50A`, crimson `#BC3754`, blue
`#23479A`, muted `#5C5A69`. Greyscale Maxar imagery inside. Frame them on a `surface` plate per the colour spec.

| File | Size | Content | src |
|---|---|---|---|
| F1_study_area.png | 2100×960 | Two panels: after-image mosaics of the development tiles (south scene: 102 tiles; west scene: 115 tiles), each tile outlined teal (clear), amber (thin cloud or haze) or crimson (opaque cloud). Legend at the bottom | /_blob/3330cec2c914cd3816e2c6d9c20b74c9 |
| F2_labels_under_cloud.png | 2100×930 | Left: tile 2_15_45 after image, thin-cloud mask in amber, roads crimson (labelled flooded) or light blue (no flood label). Right: bars of the share of roads labelled "flooded": 55% clear (798 roads), 26% thin cloud (93), 2% opaque-cloud tiles (146) | /_blob/3c57fa96313b6c88ec77cb7d50ff3c4d |
| F3_two_date_dehazing.png | 2250×900 | Tile 2_19_55: before (clear reference), after with thin cloud, after corrected from the before; bars: flooded found on 24 trusted flooded roads under thin cloud (as it is 71%, single-image 88%, two-date 83%) and accuracy on 175 clear roads on the same tiles (78%, 74%, 78%) | /_blob/b9993bb92fd3bc9b160e25296c56ff28 |
| F4_masks_vs_expert_labels.png | 1350×660 | Bars of F1 against HRC_WHU expert cloud masks by land cover, bright rule (grey) against the dark-channel mask (crimson): vegetation, water, urban, snow, barren | /_blob/64314718a1eae2e07ffe899ccfcd84d2 |

The images are local; deckkit maps the /_blob ids to the files.

## Renderer constraints
As in `reference/format.md` (the Slides subset). Inline styles only; ≥ 24px text; ≤ 4 fonts (the night-pass faces:
Archivo, IBM Plex Sans, IBM Plex Mono); no font changes on spans; footer row at bottom:64px.

## Colour-role vocabulary
The night-pass roles in `design/color_spec.md`. Actor accents for this deck:
- `accent-standard` crimson: **cloud / the problem**;
- `accent-validation` blue: **human cloud labels / checks**;
- `accent-agent` violet: **the agents and the gate**;
- `signal` amber: **key numbers on dark slides**;
- `confirmed` teal: **clear sky / passes**;
- `rejected` vermilion: **fails**.

## Slides (ids in order) and their content
Main talk: slides 1–7, about 30 s each. Supporting slides: 8–11.

**1 · cover**: "Seeing Through Clouds"
- **Subtitle:** "What a flood map can reliably say about roads it cannot see"
- Justin Rogers · GGS 662 Agentic GeoAI · Assignment 4 progress · 30 October 2026
- **Small line:** "Preliminary results on development data"
- **Notes:** introduce the problem in one breath. After a hurricane, the after image is often cloudy, and the map has
  to decide what it can and cannot see.

**2 · question**: "The question, refined since Assignment 3"
- **Problem** (Justin's own wording, quote it): "Clouds can hide target areas in images taken after disasters. This
  can lead to labels being inaccurate compared to ground truth due to obscured parts of the imagery. How should we
  detect clouds in this imagery, handle them, and report them? The goal is results, such as maps of flooded roads,
  that people can trust."
- **Since Assignment 3:**
  - Assignment 3 asked what an agent adds to reading change.
  - Re-running that agent workflow showed the first thing a system must decide: can it see the ground at all?
- **Three questions:**
  - **Lead, report:** What can a flood-road map reliably tell users about roads hidden by cloud?
  - **Handle:** When only the before image is cloudy, does the after image alone find change better than both images
    together?
  - **Detect:** Can we use synthetic clouds to represent real-life blockages in satellite imagery?
- **Contribution (expected):**
  - a tested rule for what a change map may say under cloud: stated reliably, synthetic-only, or a range;
  - a measured label bias;
  - a two-date way to see through thin cloud.
- **Notes:** the refinement is the point. Assignment 3's agent question led here. Q2 leads, Q3 handles, Q1 is the test
  bed. A cloud is a change in the image but not on the ground, so it is a blockage to see through or report.

**3 · data**: "Study area and data"
- **Image:** F1 (left, large).
- **Data card (right):**
  - SpaceNet 8 Louisiana-East, Hurricane Ida 2021: Maxar before and after, 0.5 m, used in greyscale.
  - Split: 186 train / 40 validation / 40 test tiles; a 333-tile north negative set; the test, negative and two other
    areas are sealed.
  - Development: 226 tiles, 1,037 mapped roads (OpenStreetMap centrelines).
  - Cloud labels: HRC_WHU (Li et al. 2019), 150 Google Earth images at 0.5–15 m with expert cloud masks; 120
    development, 30 sealed; academic use only.
- **Quality issues:**
  - flood labels are "yes" (487) or missing (593), never "no";
  - 17 tiles have opaque cloud;
  - all development tiles share one after image.
- **Notes:** say what was checked (the label values, the split fingerprint) and that the sealed sets were never read.

**4 · workflow**: "Workflow: detect, handle, report"
- **A diagram** (build it with shapes and connectors, not an image) of three stages in a row:
  1. **Detect** (GGS 680, classical): greyscale cloud masks per date (bright cores, dark channel, dark-channel rise
     before → after).
  2. **Handle** (GGS 662, the agent gate): per road, choose one of
     - **assess** (clear);
     - **correct** (thin cloud + a clear reference date → two-date de-hazing → back through the change detector);
     - **cannot assess** (opaque cloud).

     Filled-in pixels count as "not observed".
  3. **Report:** each statement about a hidden road gets a tier (reliable, synthetic-only, or range only).
- **Under the stages:**
  - **Change detector:** a random forest on classical, texture and frozen DINOv2 cues (83.0% on the 798 assessable
    development roads; always "flooded" 55.3%).
  - **Baselines:** the tile cloud rule and no correction.
  - **Checks:** 5 folds by tile, tile-resampled 95% intervals, paired McNemar tests, one sealed final check.
- **Human decisions** (from the decision log), as a side strip:
  - the problem wording;
  - the order Q2, Q3, Q1;
  - adopting the road cloud rule;
  - research-only data allowed now, compliance later.
- **Agent roles** (small): research-question agent, scientific critic, writer, methodology agent, methodology
  critic, literature agents.
- **Notes:** walk the three stages; the agents propose and critique, Justin decides.

**5 · result1**: "Under cloud, the labels say “dry” for roads nobody could see"
- **Image:** F2, full width.
- **Takeaway line:** analysts "only attribute what was visible" (Hänsch et al. 2022), so hidden roads read as dry: 55%
  of clear roads are labelled flooded, against 26% under thin cloud and 2% on opaque-cloud tiles.
- **Label:** "Preliminary · development data".
- **Notes:**
  - Scoring a model on these roads rewards it for calling cloud "dry".
  - Under thin cloud the model found 67% of flooded roads against 87% in clear sky.
  - The cloud mask was checked for bias under synthetic haze: it does not miss flooded roads more than dry ones.
  - Part of the gap is geography (the south scene is dry around its cloudy tiles).

**6 · result2**: "The second image lets us see through thin cloud"
- **Image:** F3, full width.
- **Takeaway:** two-date de-hazing fits how the cloud dims and brightens each 64 m window against the clear before
  image, using only pixels that did not change. It found 83% of 24 trusted flooded roads under thin cloud (71%
  uncorrected; +3 roads, none lost), and left 175 clear roads unchanged (78% → 78%). Single-image de-hazing found 88%
  but cost clear roads 4 points.
- **Label:** "Preliminary · exploratory: McNemar p = 0.25 on 24 roads, which were looked at before".
- **Notes:** the published ancestor is IR-MAD normalisation (Canty & Nielsen 2008); doing it locally inside cloud is
  the new part. Filled-in pixels never count as observed.

**7 · next**: "Feasibility, limits and next steps"
- **Feasible:**
  - the data are on disk;
  - the held-out test harness, the masks and the de-hazing prototype run;
  - HRC_WHU masks: the dark-channel mask scores F1 0.65 against 0.41 for the old bright rule (supporting slide 8).
- **Limits:**
  - one event, one sensor and roads only;
  - all real cloud is in one after image;
  - the sealed test tiles sit next to development tiles;
  - only 24 trusted flooded roads lie under thin cloud;
  - the de-hazing result is exploratory;
  - the methodology critic's verdict is REVISE (test the map's own cloud rule; one realism test for synthetic cloud;
    blocked folds).
- **Plan to the paper** (8 weeks):
  - weeks 1–2: pre-register, freeze the cloud generator and the de-hazer;
  - weeks 3–4: realism checks and the synthetic test bed;
  - week 5: before-image cloud (Q3);
  - week 6: report tiers and maps;
  - week 7: one sealed look;
  - week 8: write and submit.
- **One question for the class** (a draft; Justin may change it): "When a map cannot see a road, would you rather it
  say ‘cannot assess’, show a range, or fill it in from another date?"
- **Notes:** end on the question.

**8 · masks** (supporting): "Cloud masks against human cloud labels"
- **Image:** F4.
- **Text:**
  - Dark-channel mask F1 0.65 (precision 0.62, recall 0.68) against 0.41 for the bright rule (precision 0.81, recall
    0.28) on 120 HRC_WHU development images.
  - Best on vegetation 0.78 and water 0.74; bright barren ground is its false alarm (0.48).
  - The threshold learned on SpaceNet 8 is near the best on HRC_WHU.
- **Mask-bias check** (synthetic haze on 769 clear roads): under thin haze the mask flags flooded and dry roads
  alike; under thick haze it flags flooded roads more (+13 points), not less.

**9 · human** (supporting): "Critical human review and AI use"
- **Decision log** (accepted / changed / rejected), short rows:
  - Problem statement: **changed**, Justin rewrote it.
  - R1 (DINOv2 vs classical under haze): **rejected**.
  - R3 (the 20% cut-off frame): **rejected**.
  - Q1: **changed**, moved last, in Justin's words.
  - Q2 leads: **Justin's choice** (Claude had suggested Q3).
  - Methodology critique: **accepted as defaults** at outline stage.
- **AI statement:**
  - Claude Code (Anthropic) agents drafted research questions, critiques, literature notes and analysis code.
  - Justin made the decisions above.
  - Code and numbers were run and checked on development data; citations are listed as unverified until read.
  - Agreement between agents is not treated as validation.
- **Notes:** state that every number on the slides was produced by code on development data.

**10 · refs** (supporting): "References"
- Hänsch et al. 2022, SpaceNet 8 (CVPR Workshops) · Li et al. 2019, HRC_WHU (ISPRS JPRS) · He, Sun & Tang 2011, dark
  channel (IEEE TPAMI) · Canty & Nielsen 2008, IR-MAD (Remote Sensing of Environment) · Portalés-Julià et al. 2023
  (Scientific Reports) · Qu, Li & Huang 2026, AnyTime-CD (Remote Sensing of Environment) · Shen et al. 2015
  (missing-data reconstruction review, IEEE GRSM) · Bruzzone & Bovolo 2013 (Proceedings of the IEEE).
- **Note line:** "Under verification; see the evidence files."
- **Data:** SpaceNet 8 (CC BY-SA 4.0; imagery Maxar) · HRC_WHU (academic use only).

**11 · evidence** (supporting): "Evidence files"
- **Paths** (one line each), all under `Agentic-GeoAI/Claude/CloudResearch/`:
  - `input_card.md`;
  - `decision_log.md`;
  - `outputs/` (research questions, critiques, abstract, methodology);
  - `evidence/` (measured results, literature summaries, research-question guide, reconstruction literature);
  - `figures/`.
- **Code** (the private repo github.com/Jrog378/GeoAI-Roads): `sn8_clouds.py`, `sn8_refhaze.py`, `sn8_cloudref.py`,
  and the stage notebooks.

## Facts usable as motif text (true values only)
- Hurricane Ida, 2021
- UTM 15N
- 0.5 m
- greyscale
- 226 development tiles
- 1,037 roads
- 798 assessable roads
- 24 trusted flooded roads under thin cloud
- HRC_WHU 120 / 30
- F1 0.65
- 83% vs 71%
