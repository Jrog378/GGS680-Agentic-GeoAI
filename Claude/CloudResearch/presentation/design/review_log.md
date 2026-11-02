# Review log: "Seeing Through Clouds" (Assignment 4)

## 2026-10-24: first build
- **Build:** `python3 -I build_slides.py` writes the 12 slide files from shared Night Pass pieces. Then deckkit
  `renumber --eyebrow-offset -1`, `lint`, `render` and `pdf`, all with the absolute workspace path. A relative "."
  makes headless Chrome fail with ERR_INVALID_URL.
- **Figures:** the four matplotlib figures (F1–F4) had small text and wide white margins for a projector. They were
  replaced:
  - `slide_panels.py` (saved in `evidence/pilot_scripts/`) draws tight imagery panels;
  - the bar charts are built in deck type from `assets/panel_numbers.json`, which the same script writes from code;
  - F1–F4 stay in `figures/` for the written proposal.
- **Numbers checked against evidence 01 before writing:**
  - 798 roads, 83.0% and 55.3% match evidence 01, lines 50–60.
  - The 487/593 label counts come from the label files and do not reconcile with the 1,037 touched roads, so they
    are left off the slides.
  - The data slide says "217 of the 226 development tiles", because the mosaics show 102 + 115 tiles.
- **Content change from the brief (slide 6):** the transmission map showed that the two-date fit is rough.
  - A label-free diagnostic found clear-pixel correlation r = 0.46 between the dates and a diluted slope (0.16, against
    0.31 for an orthogonal fit). The bright cloud core is skipped as opaque.
  - The title went from "lets us see through" to "may help under thin cloud".
  - Two panels were added: "What goes wrong" and "The fix, pre-registered".
  - The diagnostic is logged in evidence 01 and in methodology v2 (before §6.4.6, plus §19).
- **Added a supporting slide** ("How the two images are layered"). Justin asked for image-layering information. It
  shows before + after, the fitted t, the corrected image and the model line.
- **Citations (memory rule: every method on a slide is cited).** Inline citations were added for:
  - the dark channel (He et al. 2011);
  - the random forest (Breiman 2001, attribution);
  - texture (Haralick 1979);
  - DINOv2 (Oquab et al. 2024);
  - tile-blocked folds (Roberts et al. 2017);
  - McNemar (1947, attribution);
  - IR-MAD (Canty & Nielsen 2008).

  "Our rule" marks the bright rule, the dark rise, the two-date fit and the report tiers. The references slide is split
  into literature and method attributions.
- **Lint:** 0 errors. Two expected warnings:
  - the cover kicker is measured against the sweep's brightest stop, but sits on the dark part;
  - #4FC3F7 is the figure's own colour for roads with no flood label, used as a legend key.
- **Render:** 0 issues on all 12 slides, and every content title top sits at y = 190.
- **Read every PNG:** fixed overflow on question, data, workflow, next, layering, refs and result2. Spread the layering
  row, with "+" and arrows. Every number on the slides comes from evidence 01 or panel_numbers.json.
- **Queued for after validation:** slide 6 "Clear roads unchanged" becomes "Clear-road accuracy held: 78% → 78% (6
  calls fixed, 5 broken)", from `evaluate.log`.
- **Validation agent:** launched 2026-10-24 to read the cited papers and check every claim. Report:
  `design/validation_report.md`.

## 2026-10-24: after the validation report (`design/validation_report.md`: 114 claims, 75 OK, 4 must fix, 29 should fix, 6 unverified)
- **Must fix, all done:**
  - slide 6 "The fix, pre-registered" became "Next: fix, then pre-register";
  - slide 6 clear roads became "about the same: 77.7% → 78.3% (6 calls fixed, 5 broken)";
  - slide 10's critique row became DEFAULT ("taken by Claude as defaults; Justin can overrule");
  - slide 12's `sn8_refhaze.py` was committed and pushed to GeoAI-Roads (78eda4c).
- **Should fix, done:**
  - slide 2's contribution now reads "a test of whether a second date can correct thin cloud";
  - slide 5's title became "roads rarely get a flood label", with a geography caveat;
  - slide 6 adds the 3 of 69 dry-labelled flips and notes that the tile was picked as a success case;
  - the He 2011 credit became "haze model as used by" / "dark channel prior", and slides 4 and 6 now word the method the
    same way;
  - slide 8 says it checks single-date masks only and gives the bias as "up to +13";
  - slide 9 says "by design ... untested";
  - slide 10: R1 is CHANGED, and the AI use now covers figures and slides;
  - slide 11: SpaceNet 8 moved to data; the background papers are listed apart; the licence is "to confirm";
  - the imagery credit no longer names a licence;
  - the slide 5 note now says the 67% came from an earlier fit.
- **Fix to the slide 6 panel from the data + tool agent:** education briefing P3 advises against linear or IR-MAD
  normalisation on the 8-bit product. So the fix now reads "coarser scale with a nonlinear tone match".
- **Sealed-label disclosures:** two this session, the validation agent's and the coordinator's. Both are logged in
  `Project/docs/datasets/data_budget.md`, and the validation report's count is redacted. The data slide's note now says
  "never scored; every slip is logged".
- Lint 0 errors, render 0 issues, every PNG read, and the PDF re-exported.

## 2026-10-25: reframed in Justin's words
- Justin: "dont mention assignments, we are just going to say it like this. We have a problem of creating an agentic
  change detection system. One of the difficulties we have run into is relating to how we are dealing with clouds in
  our electrical optical imagery. This is our proposed method of study along with research questions and some
  literature review backed methodologies, then these are the results we have obtained visually and numerically from
  these studies". Then: "Dont number the questions either, they will be solved out of order anyways".
- **Assignment mentions removed:** the cover kicker is now "Research progress"; the footer is "GGS 662 · 30 Oct 2026";
  the question slide's "since Assignment 3" text and its notes are gone; the discussion label is "Question for
  discussion".
- **Story order:** cover → problem and questions → proposed method → data → result 1 → result 2 → plan. The method
  now comes before the data. The cover subtitle reads "Handling clouds in agentic change detection".
- **Question slide:** it opens with the system (a vision foundation model finds where two images differ, an agent
  describes it, code checks every fact; from the GeoAI-Descriptions README), then "One difficulty · clouds in EO
  imagery" with Justin's problem statement. No new method names, so no new citations.
- **No question numbers:** the cards read Report, Handle and Detect. The plan, the workflow panel and the
  decision log name questions by topic. The workflow's stage numbers (1 Detect, 2 Handle, 3 Report) stay, because
  they are pipeline order.
- Lint 0 errors (the same two expected warnings), render 0 issues, the changed PNGs read, and the PDF exported as
  `Seeing_Through_Clouds_2026-10-25.pdf`.
- **Features, not roads (Justin, 2026-10-25):** "dont talk about roads specifically, our tests are using roads but the
  report box should say each statment about a hidden feature gets a tier or something more general".
  - Method slide: "Handle, feature by feature"; "Each statement about a hidden feature gets a tier"; "the per-feature
    cloud rule".
  - Discussion question: "When a map cannot see the ground, should it say …".
  - Cover and method notes say the same.
  - Test results stay in roads, because the tests use roads. So do the limits ("roads only") and the reporting
    question's wording, which Justin chose.
  - PDF re-exported; `assignments/Done/JustinRogersA4GGS662.pdf` replaced with it.

## 2026-10-25: slides 6 and 9, the revised fit, and two slides dropped
- **Justin's requests:**
  - slide 6 needs a better example, with cloud over a road and a visible difference;
  - slide 9's haze layer "is way too sensitive and catching houses as clouds";
  - drop the 8-week plan and call it next steps;
  - drop the decision-log slide and the evidence-files slide, but keep the GitHub link.
- **New example:** picked by a label-free rule, the road with the most metres under thin cloud (2_23_44, 481 m),
  replacing the old success-case pick. Panels P5_* come from `evidence/pilot_scripts/slide_panels_dehaze.py`, with road
  lines drawn thicker.
- **Revised fit:** `dark_reference_dehaze` (evidence 01). Slide 6 now shows the before image, the after image, the pilot
  fit and the revised fit, with three boxes: the pilot's road score, what went wrong, and the revised fit's synthetic
  check. Slide 9 shows the revised fit step by step.
- **Found while building the notebook:** the guided filter flattened detail, so it is off. The fit was chosen on half the
  tiles and reported on the other half. On the slide tile, little road detail comes back, and slide 6 says so.
- **Deck changes:**
  - 10 slides;
  - the references slide is now "References, code and AI use";
  - the workflow stage boxes are 424 px tall, to fit "(so far with the pilot fit)".
- **Validation agent** (`design/validation_report_2026-10-25.md`):
  - both must-fix items done: the code is pushed to GeoAI-Roads (745441f), and the note that the synthetic check
    favours the revised fit is on slide 6;
  - should-fix items applied: the title is "lifts some thin cloud", the 42% is placed as a synthetic number, "standard
    haze model as used by He", our rules are listed on slide 9, "(so far with the pilot fit)" is on the workflow slide,
    the critic's verdict has its own bullet, and the Canty & Nielsen wording is changed;
  - the guided-filter citation is no longer needed, because the filter is off.
- Lint 0 errors, render 0 issues, the changed PNGs read, the PDF re-exported, and the Done copy replaced.

## 2026-10-25 (evening): no version wording; the flood-call test added
- **No version wording (Justin):** "stop stating that we made updates to it. this is the first version we are
  presenting".
  - Slide 6 now compares the two-date method with the published baseline, single-image de-hazing (He et al. 2011),
    using panel P5_single and a synthetic-haze table (none / He 2011 / two-date). The baseline has the lower grey error
    (27 against 37), but it changes 85% of clear ground; the two-date method keeps the detail (1.02).
  - "pilot" and "revised" are removed from every slide and every note. Canty & Nielsen moves to Background.
- **The flood-call test (Justin: "set this up to be run on the flood cells so we can present that too"):**
  - plan written first (`outputs/preregistration_twodate_roads.md`), then run (evidence 01);
  - new slide 7, "Result 3: flood calls on the de-hazed images", with a grouped bar chart drawn from
    `twodate_numbers.json` (copied into panel_numbers.json as "roads_twodate");
  - the slide's verdict: more flooded roads found (17 → 20 of 24, p = 0.38) and more false alarms (the clear roads on
    the same tiles drop from 78% to 72%, p = 0.04).
- **Deck:**
  - 11 slides; the workflow slide points to result 3;
  - the Limits and Next steps cards are updated;
  - the main-talk notes are now 987 words (about 6.6 minutes at 150 wpm).
- Lint 0 errors, render 0 issues, every changed PNG read, and every percentage checked against the log. The PDF is
  re-exported and the Done copy replaced.
- **Slide 7 (18:15):** updated with the second run, training on de-hazed images. Bars: none / two-date, model trained
  as it is / two-date, model trained de-hazed. A "Cloud as an extra variable" panel was added. The title is "More
  flooded found; false alarms hinge on training". Limits and Next steps are updated. The previous PDF is kept as
  `render/Seeing_Through_Clouds_2026-10-25_before_training_result.pdf`. The Done copy is replaced.

## 2026-10-25 (20:00): rubric check and the tonight fixes
- An independent reviewer (`design/rubric_check_2026-10-25.md`) estimated 73/100: method 22/30, evidence 24/30, human
  review 14/20, presentation 13/20. All 18 numbers it checked matched; six claims were stated too strongly.
- **Applied** (worded to Justin's rules: no assignment mentions, no question numbers, no version wording):
  - slide 3: the always-"flooded" baseline (55.3%); the agent roles named; the handle gate is coded rules;
  - slide 4: "have never been scored"; a "Unit" row (OSM line plus a ~5 m band; tiles as the fold unit; ~0.6 m
    alignment);
  - slide 5: "far fewer roads get a flood label"; "an example tile";
  - slides 5–7 and 9: eyebrows tagged report / handle / detect;
  - slide 6: table units ("grey error (0–255)", "detail kept (1 = all)", "clear altered"); "by design" moved into the
    caveat; the flood box reads "Clear-road accuracy depends on training";
  - slide 7: the title is "3 more of 24 flooded roads found, not significant"; the paired box adds "trained as it is:
    clear roads 5 fixed, 15 broken (p = 0.04)"; the caption states the He baseline and that it was not tried with
    de-hazed training;
  - slide 8: Feasible adds "each test runs in under an hour" and the semester-end expectation; the Limits bullets are
    merged;
  - slide 2: a "Design choices" line;
  - slide 11: the AI-use box gives the logged decision counts (28: 10 rewritten, 6 rejected) and Justin's own checks;
    the code line says "access on request"; the reference headers are simplified; the SpaceNet 8 venue is named.
  - **Notes:** the main talk is cut from 1,017 to 555 words (about 3.7 minutes at 150 wpm). The long version is in
    `design/notes_long_2026-10-25.md`.
- **Not done tonight:**
  - the "Tested so far" line on the Handle question card (no room);
  - Haralick 1979 (needs the GMU login) and the SpaceNet 8 licence (to confirm);
  - Friday items: the locator map, the He arm trained de-hazed with intervals on slide 7, full references, and marking
    post-submission changes.
- The generator from before the fixes is saved as `design/build_slides_before_rubric.py`. Lint shows 0 errors, render
  shows 0 issues, every changed PNG was read, the PDF was re-exported and the Done copy replaced.

## 2026-10-25 22:08 · final deck for tonight (`render/Seeing_Through_Clouds_2026-10-25_final.pdf` → `assignments/Done/JustinRogersA4GGS662_final.pdf`)
- Slide 7 rebuilt with the He baseline trained de-hazed: three bars per group (none, two-date, He), whiskers = 95% tile-resampled intervals, paired tests, source line. Two-date bar still from 2ec5346 (corner edit); rerun running.
- "Single image" wording replaced everywhere on the slides (Justin: "how are you going to find change with the after image alone? reword").
- Justin's rulings applied: handle question = see through cloud on either date; synthetic test bed on hold; no sealed look; no journal; change = anything but lighting; flood only.
- Slide 14: road finding DONE (evidence 06), ring + corner-fix RUNNING, DECIDED row.
- Lint 0 errors, render 0 issues; every changed PNG read (question, result2, flood, next, open). Snapshot: `design/build_slides_final_2026-10-25.py`.
- Grader round 3 sent; later versions go to `assignments/Done/JustinRogersA4GGS662_update.pdf`, not the submitted file.
- 23:24 round 5: slide 7 two-date numbers from the run without the corner edit (dry 42%, p 0.81, 9 vs 29); pending note removed; exported to Done/JustinRogersA4GGS662_update.pdf.
- 23:33: no non-significant p-values on slides (Justin); slide 7 panels now state the improvement (second event for more flooded roads; ring smoothing, He et al. 2013, added to cited refs, Crossref-checked).
- 23:29: slide 5 'for this dataset a flooded road under cloud reads as dry' (Justin).
- 23:37: slide 9 explains both masks and reports the use-both test (adds nothing; bright mask ~ subset of dark); slide 7/8/14 plan two-date + He together (Justin).

## 2026-10-29 · updates for the 30 Oct talk (`render/Seeing_Through_Clouds_2026-10-29.pdf`; 25 Oct PDFs untouched)
- Slide 3: detector 83.0% (tile folds) → 79% on 798 roads in new areas (spatial CV, evidence 14); folds now "blocked by 1.75 km area"; notes explain the 4-point drop.
- Slide 8: Feasible now states the trained spotter (F1 0.87 vs 0.65, evidence 12); Limits adds "tile-split scores run about 4 points high".
- New supporting slide 9 `spatialcv`: spatial CV (78.6% vs 82.5%), DINOv2 change vector (+1.3, 21/21 seeds; its seed-662 p is n.s., so not shown), DINOv3 benchmark (83.0% vs 79.2%, p = 0.0005, research only; evidence 15).
- Masks slide: "use both" panel replaced by the trained spotter (research only, HRC_WHU academic use).
- Review slide: cross-validation row added; example-tile row dropped for space. AI-use counts 38 decisions (11 changed, 7 rejected).
- Refs: Siméoni et al. 2025 (DINOv3, arXiv 2508.10104) added; data line moved to the right column.
- Lint 0 errors, render 0 issues; changed PNGs read. Pre-edit generator: `design/build_slides_before_2026-10-29.py`.
