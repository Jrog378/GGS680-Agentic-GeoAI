# Rubric check: "Seeing Through Clouds" against GGS 662 Assignment 4 (2026-10-25)

- **Inputs read:** the assignment PDF (Tables 1 and 2 and the formatting rules); all 11 render PNGs; every `<aside>`; evidence 01 and 03;
  `panel_numbers.json`; both validation reports; the review log; the decision log; `sn8_refhaze.haze_recovery`; and the GeoAI-Roads git state.
- **The submitted PDF:** `assignments/Done/JustinRogersA4GGS662.pdf` is byte-identical to `render/Seeing_Through_Clouds_2026-10-25.pdf`.
  It is image-only, so I graded from the PNGs.
- **The author's choices:** no assignment mentions, no question numbers, no version wording, no decision-log or evidence slide.
  I treat these as choices, not errors. Where the rubric costs points for one, I say so and give a way to recover the points
  that keeps the choice.
- **Estimated score: 73 / 100** (a strict range is 70–78). With the "tonight" fixes it would be about 82. With the timing cut and
  the Friday fixes it would be about 86.

## 1 · Table 2, criterion by criterion

| Criterion (weight) | Score | Evidence on the slides | What loses points |
|---|---|---|---|
| Refined research method (30) | **22** | **S2:** problem, three questions (Report, Handle, Detect) and the expected contribution. **S3:** workflow (Detect → Handle → Report), detector (RF + texture + DINOv2, 83.0% on 798 roads), baselines (tile rule, no correction), checks (tile-blocked folds, McNemar, one sealed check) and human decisions. **S4:** data, split, sample and quality issues. **S6/S9/S10:** published baselines (He 2011, the bright rule) and the method in detail. | (a) **No justified improvements since the proposal.** The rubric asks for this by name (author's choice; recover with fix T7). (b) **The results do not map to the questions as worded.** The Handle card asks about *before-image* cloud, but no Louisiana-East before image is cloudy (ev. 01 l.39). Results 2–3 test after-image thin cloud corrected from the before image, and no question card says so. (c) The unit of analysis (road strip; tile as the fold unit) and the spatial assumptions are implicit. (d) Agent roles are one phrase. "The agent gate" is coded rules, and the slide does not say whether an LLM acts. (e) The detector's 83.0% has no trivial baseline (always "flooded" = 55.3%, ev. 01 l.61–62). |
| Preliminary evidence and feasibility (30) | **24** | A real executed pilot. **S4:** data inspected and tiles classed by cloud (17 opaque). **S5:** label gap 55/26/2% on 1,037 roads. **S6:** two-date against He on 94 synthetic tiles, plus one real tile. **S7:** flood calls with paired McNemar tests. **S9:** masks against expert labels (F1 0.65 vs 0.41) and the mask-bias check. Preliminary or exploratory is labelled on S1 and S5–S7. | (a) The **S7 title overstates** the result (§5). (b) **The S7 chart leaves out the published baseline.** It sits in the caption, and with the same training it matches or beats two-date (21 vs 20 found, 74% vs 72% clear). (c) No intervals on any bar, and n = 24 means one road is 4 points. (d) On the real S6 tile "little road detail returns". This is honest, but it is the only real-imagery result for the method. (e) The feasibility box lists what runs, not time, compute or scale. |
| Critical human review (20) | **14** | Honest caveats throughout: "part of the gap is geography" (S5); "synthetic haze … favours it" (S6); "the 24 flooded roads had been looked at before" and the p-values (S7); limits including "critic's verdict: revise" (S8). Also S3 "Agents propose, I decide", S11 AI use and "agreement between agents is not validation". | (a) **AI-output decisions are not documented** (the log slide was dropped; recover with fix T6). (b) The AI statement names no checks Justin did himself, only the validation agent's. (c) The plan is an undated list with no effort sizes ("realistic plan" is only partly met). (d) S4's "stay sealed" is stronger than the record (§5). |
| Presentation quality and delivery (20) | **13** | A professional, consistent house style. Slide numbers 02–11. Takeaway titles. Legends and n on the S5, S7 and S9 charts. Imagery credited on S1, S5 and S6. An AI statement names Claude Code. | (a) **The main-talk notes run about 6.8 min against 4:00** (§4). (b) The references are not full (no titles, volumes, pages or DOIs). Hänsch 2022 is cited on S4–S5 but missing from the cited list. "Haralick 1979 (not yet read)" is printed. SpaceNet 8 says "licence to confirm". (c) The S6 table metrics have no definitions or units. (d) The S4 map has no locator, north arrow or dates. (e) The eyebrow numbers (01–10) are one off from the page numbers (02–11). |

## 2 · Table 1, component by component

| Component | Item | Status | Slide · note |
|---|---|---|---|
| Question and progress | Question pursued | Present | S2; three questions, only partly matched by the results |
| | Refined since the proposal | **Missing** | Author's choice; recover with T7 ("design choices and why") |
| | Overall contribution | Present | S2 "Expected contribution …" |
| Refined method | Study area | Partial | S4 tile map, scale bar and legend; no locator, north arrow or acquisition dates |
| | Unit of analysis | Partial | S3 "feature by feature", S5 roads; the strip and the fold unit are not named |
| | Data preparation | Partial | S4 "0.5 m … greyscale"; the common grid, co-registration and strip are not stated |
| | Analytical steps | Present | S3 and S10 (the formula, 2,500 m² gate, 20 m fade, t < 0.2) |
| | Agent roles | Partial | S3 "Role agents draft and critique"; roles not named; S2's describing agent not shown |
| | Human decisions | Partial | S3 and S11 name three decisions; no accepted/changed/rejected record |
| | Workflow diagram | Present | S3 three-stage flow; it does not show where agents, the human or the checks enter |
| | Baseline | Present | S3, S6, S7 (caption only), S9; the 55.3% detector baseline is missing |
| | Verification / validation | Present | S3 blocked folds and McNemar; S9 HRC_WHU and the mask bias; S6 synthetic; sealed sets |
| | Spatial assumptions | Partial | Scattered (S3 folds, S10 blob size, S8 "sealed tiles sit next to development tiles"); never stated as assumptions |
| Data and pilot | Sources | Present | S4 (Maxar/SpaceNet 8, OSM, HRC_WHU) |
| | Coverage | Partial | S4 tile counts; no km² or dates |
| | Sample size | Present | S4 (1,037 roads, 226 tiles, 120+30 images); S5 and S7 n per bar |
| | Quality issues | Present | S4 (labels yes/missing, 17 opaque tiles, one after image) |
| | Code or tools | Partial | S11 private repo (graders cannot open it); S3 methods; no software named |
| Results and graphics | What was measured | Present | S5, S7, S9; S6 metrics undefined |
| | Comparison with baseline | Present | S6 table, S9 chart; S7 has the baseline in the caption only, with unequal training |
| | Feasibility comment | Partial | S8 "Feasible" lists what runs; no time or compute (runs took 16 and 45 min, ev. 01) |
| | Labelled preliminary | Present | S1, S5 "preliminary", S6–S7 "exploratory" |
| Limits and next steps | What remains untested | Present | S8 Limits |
| | Failed checks / changes needed | Partial | S6 "little road detail returns", S8 "verdict: revise"; the S7 clear-road drop (p = 0.04) is not shown |
| | Realistic plan | Partial | S8 ordered list; no dates or effort (the 8-week grid was dropped by choice; recover with T5) |
| | One focused question | Present | S8: "cannot assess", a range, or fill from another date. Good. |

## 3 · Formatting rules

| Rule | Status | Note |
|---|---|---|
| Slide numbers | Present | "02 / 11" to "11 / 11"; the cover is unnumbered (fine). The eyebrows "01 ·"–"10 ·" are off by one, which will confuse in Q&A. |
| Consistent formatting | Present | One house style; the dark slides (S6, S10) are deliberate imagery slides. |
| Source acknowledgments | Partial | Imagery is credited on S1, S5 and S6. Missing on the S4 map, S7 (labels) and S10 (imagery). |
| AI disclaimer: tools, contributions, own checks | Partial | Tool and contributions are there. The **author's own checks are missing**: "Justin chose…" lists decisions, and "a validation agent checked…" is an AI check. |
| Supporting: full references | Partial | S11 gives author, year and journal only. Hänsch 2022 is missing from the list. The headers carry internal jargon ("JIF above 4", "below the JIF rule"). |
| Supporting: methodological details | Present | S9 masks; S10 layering and formula. |
| Supporting: evidence files | Missing | Dropped by choice. The repo is private. Recover with one line in the Code box (T9). |
| Graphic takeaway | Present | S5, S6, S7 and S9 titles are takeaways. The S7 takeaway overclaims. |
| Readable labels | Present | Fine at 1080p. The grey 22–24 px captions (S5, S7) will be faint on a projector. |
| Units | Partial | % and F1 are fine. **S6 "grey error", "detail kept" and "clear changed" are undefined.** Per `haze_recovery`: RMS grey levels against the clear image; median 5 m local contrast ÷ the clear image's (1 = all); share of clear ground read as haze. |
| Legends | Present | S4, S5, S6 (text legend), S7, S9. |
| Data sources on graphics | Partial | S7 and S10 have none. |

## 4 · Delivery: spoken length

| Slide | 1 cover | 2 question | 3 workflow | 4 data | 5 result1 | 6 result2 | 7 flood | 8 next | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| Words now | 81 | 147 | 101 | 119 | 128 | 153 | 168 | 120 | **1,017** |
| Target | 35 | 75 | 70 | 60 | 80 | 70 | 90 | 90 | **570** |

- **Length now:** 1,017 words ÷ 150 wpm = **6.8 min (about 6:47)**, 70% over 4:00. Even at 170 wpm it is 6.0 min.
- **Cut to about 570 words** (3:48), which leaves room for pauses.
- **What to cut first:**
  1. **Flood (S7), 168 → 90.** Drop the cloud-as-variable sentences; they stay on the slide for Q&A.
  2. **Result 2 (S6), 153 → 70.** Drop the mechanism (S10 covers it) and the table walk-through. Keep: the road picked by rule; the
     baseline alters 85% of clear ground and ours none; the check favours us; the core stays "cannot assess".
  3. **Question (S2), 147 → 75.** The system description repeats the cover's notes. Drop "In my own words…" and the working definition.
  4. **Data (S4), 119 → 60.** Replace the sealing mechanics with "test tiles and other areas are sealed and never scored".
  5. **Result 1 (S5), 128 → 80.** Drop the earlier-fit 67%/87% sentence and the mask check (S9, for Q&A).
  6. **Cover, 81 → 35.**
- **If rehearsal still runs over:** show S6 as a 15-second visual only.

## 5 · Accuracy spot checks (slides 5–8)

| # | Slide · claim | Evidence | Verdict |
|---|---|---|---|
| 1 | S5 55% of 798 clear roads | panel 55.3%, 798; ev. 01 l.61–62 | OK |
| 2 | S5 26% of 93 thin; 2% of 146 opaque | panel 25.8%/93, 2.1%/146; 798+93+146 = 1,037 | OK |
| 3 | S5 title "roads **rarely** get a flood label" | 26% under thin cloud is not "rarely"; geography is partly the cause (ev. 01 l.23–25) | **Overstated** → "far fewer". The S5 tile was hand-picked (val. 10-24, 5.6); call it "an example tile". |
| 4 | S6 481 m, tile 2_23_44 | panel P5 m_under 480.9 | OK |
| 5 | S6 grey error 57 / 27 / 37; detail 0.82 / 0.84 / 1.02 | panel synthetic 56.93/27.29/37.24; 0.817/0.844/1.024 | OK |
| 6 | S6 clear changed 0% / 85% / 0% | panel 0.0 / 0.852; ev. 01 l.111 "0% by design, because of the gate" | **Overstated as a measured advantage.** The 0% is built in (val. 10-25, 6.2); say "by design". |
| 7 | S6 found: 20 two-date, 17 as it is, 21 He | panel roads_twodate 20/17/21 | OK. Note that the **baseline found more**. |
| 8 | S7 found 71 / 83 / 83% | 17, 20 (twodate), 20 (cloudvars arm 2) of 24 | OK |
| 9 | S7 dry-labelled called flooded 9 / 57 / 43% | 6, 39, 30 of 69 | OK |
| 10 | S7 clear roads right 78 / 72 / 77% | 77.7, 72.0, 76.6% of 175 | OK |
| 11 | S7 4 fixed / 1 broken, p = 0.38; 7 / 9, p = 0.80 | cloudvars "vs arm 1": 4/1 p 0.375; 7/9 p 0.8036 (exact binomial recomputed: 0.375, 0.804) | OK |
| 12 | S7 19 vs 20 found; 30 → 4; arm 6 = 7 | cloudvars arms 4, 2, 6 | OK |
| 13 | S7 caption: He 21 of 24, 74% | 21; 73.7% | OK |
| 14 | S7 title "**More flooded found**" | +3 net of 24, McNemar p = 0.375, 95% CI +0.000 to +0.316 | **Overstated.** Not significant. It also breaks the "significant results, not improvements" rule. |
| 15 | S7 title "false alarms **hinge on** training" | ev. 01 l.196: "a post-hoc reading of arm 2, to be confirmed". Trained de-hazed still flags 30 of 69 cloudy dry-labelled roads vs 6 (0 fixed, 24 broken). Only clear-road accuracy recovers. | **Overstated, causal and post hoc.** The supporting number (trained as it is vs none, clear roads 5/15, p = 0.041) is not on the slide. |
| 16 | S7 two-date vs the baseline | With the same training, He ≥ two-date on every bar: found 21 vs 20 (p = 1.0), clear 73.7 vs 72.0%, dry-labelled flagged 22 vs 39 | **Missing comparison.** Only two-date gets the retrained arm, so the S6 + S7 framing favours it. |
| 17 | S8 F1 0.65 vs 0.41; 24 trusted roads | panel hrc pooled 0.649 / 0.411 | OK |
| 18 | S4 "test tiles … stay sealed" | val. 10-24 disclosure 1: up to 400 label files possibly including test/north were opened; counts redacted; slip logged | **Stronger than the record.** The notes already say "never been scored". Use that on the slide. |

The code claim is now true: 2ec5346 and later are on origin/main. Note that 5d325d9 and 5be95c2 and evidence 07 are
post-submission (after 18:14).

## 6 · Fix list, ranked by points gained per minute

| # | When | Pts / min | Change (exact wording) |
|---|---|---|---|
| T1 | Tonight | +0.5 / 1 | **S3** "83.0% on 798 roads." → "83.0% on 798 roads (always "flooded": 55.3%)." |
| T2 | Tonight | +0.5 / 1 | **S4** "…Louisiana-West stay sealed" → "…Louisiana-West have never been scored" |
| T3 | Tonight | +0.5 / 2 | **S5 title** → "Under cloud, far fewer roads get a flood label". **Caption** "Left: tile 2_15_45" → "Left: an example tile, 2_15_45" |
| T4 | Tonight | +2 / 6 | **S7 title** → "De-hazing finds 3 more of 24 flooded roads (not significant)". **"Trained de-hazed vs none" box:** add "Trained as it is vs none, clear roads: 5 fixed, 15 broken (p = 0.04)." **Caption:** replace the He sentence with "Baseline (He 2011), same training as the orange bars: 21 of 24 found, 74% of clear roads right, at least as good as two-date; not yet retrained on its own output." **S6 last box:** "False alarms hinge on training: result 3." → "Clear-road accuracy depends on training: result 3." |
| T5 | Tonight | +1 / 3 | **S8 Feasible box**, add: "Each test runs in under an hour (16–45 min)" and "Expected by semester end: a frozen cloud rule and report tiers, tested once on sealed tiles". Gives an expected outcome and feasibility without a dated plan. |
| T6 | Tonight | +2.5 / 10 | **S11 AI use**, replace the 2nd and 3rd paragraphs with: "Justin chose the problem, the questions and the cloud rule; 29 decisions on AI suggestions are logged (11 changed, 6 rejected). His own checks: he inspected the haze maps and example tiles, which changed the method twice (a minimum cloud size so houses are not read as haze; a label-free tile pick). A validation agent checked claims against the papers; agreement between agents is not validation." The counts come from `decision_log.md`. This recovers the dropped log slide's points. |
| T7 | Tonight | +2 / 8 | **S2, under "Expected contribution"**, add: "Design choices: cloud is judged per road, not per tile, because labels under cloud cannot be trusted; a second date corrects thin cloud, because the before image shows how dark the ground really is." This justifies the refinements without naming an assignment or a version. |
| T8 | Tonight | +1.5 / 5 | **S2 Handle card**, add the line "Tested so far: thin cloud on the after image, corrected from the clear before image." **Eyebrows:** S5 "· REPORT QUESTION ·", S6–S7 "· HANDLE STEP ·", S9 "· DETECT STEP ·". |
| T9 | Tonight | +0.7 / 3 | **S11 Code box:** "(private)" → "(private; access and evidence files (numbers, logs, test plans) on request)" |
| T10 | Tonight | +1 / 5 | **S6 table footnote** → "He 2011 = single-image de-hazing (baseline). Grey error: RMS against the clear image, grey levels 0–255. Detail kept: local contrast ÷ the clear image's (1 = all). Clear changed: clear ground altered; 0% for two-date by design (it works only inside the cloud mask)." |
| T11 | Tonight | +1.5 / 10 | **S4 table**, add a row "Unit and assumptions": "One road = OSM centreline plus a learned band (~5 m each side); the tile is the fold unit; dates co-registered (~0.6 m residual shift); cloud blobs ≥ 2,500 m²." The 5.14 m half-width comes from `ClaudeFunctions/.cache/road_band.json`; confirm it is the current entry. |
| T12 | Tonight | +1 / 15 | **S11 references:** add "Hänsch et al. 2022 · SpaceNet 8 flood and road labels · CVPR Workshops (EarthVision)". Read Haralick 1979 and delete "(not yet read)", or drop the citation. Confirm the SpaceNet 8 licence and state it in place of "licence to confirm". Rename the headers to "Cited on these slides" and "Method attributions". |
| F1 | Friday | +3 / 60 | **Cut the main-talk notes 1,017 → about 570 words** per §4, then rehearse twice with a timer. This is the largest single gain. |
| F2 | Friday | +0.7 / 15 | **S3 agent roles:** "Role agents draft and critique." → "Question, critic, methods-critic and validation agents draft and critique; in this pilot the handle gate is coded rules, not an LLM." Confirm the gate wording against the code first. |
| F3 | Friday | +0.3 / 5 | Drop the eyebrow numbers "01 ·"–"10 ·", or align them with the page numbers. |
| F4 | Friday | +1 / 30 | **S4 map:** add a locator inset (state outline plus AOI box), a north arrow and the before/after acquisition dates from the SpaceNet 8 metadata. Credit the imagery on the map, S7 and S10. |
| F5 | Friday | +1 / 25 | **S7 chart:** add the He arm as a fourth bar (same training) and 95% intervals (they are in `panel_numbers.json`). Optionally pre-register and run "He, trained de-hazed" (about 45 min) for a fair baseline. Mark it "added after submission". |
| F6 | Friday | required | Mark anything from evidence 07 or code after 2ec5346 "added after the 25 Oct submission". If the S6–S7 numbers are rerun on 5d325d9 or later, mark them "changed since submission". |
| F7 | Friday | +0.5 / 30 | Expand S11 to full references (title, venue, volume, pages, DOI) on a second supporting slide. |

## Round 2 (2026-10-25, about 20:10): the 14-slide deck, `render/Seeing_Through_Clouds_round2.pdf`

- **Read:** all 14 PNGs and every note. Main-talk notes: 38+78+60+63+76+70+87+83 = **555 words = 3.7 min**, which fits 4:00.
- **Done copy:** `assignments/Done/JustinRogersA4GGS662.pdf` is still the **19:47 11-page build** (byte-identical to
  `render/Seeing_Through_Clouds_2026-10-25.pdf`), not round 2. **Copy round 2 to Done before 23:59.** **Score: 85 / 100.**

| Criterion | R1 | R2 | Gained | Still lost |
|---|---|---|---|---|
| Refined method (30) | 22 | **26** | Design-choices line, Tested-so-far line, Unit row, 55.3% baseline, agent roles named | Refinement only implied (−1); Handle question has no real before-cloud data (−1); spatial assumptions partial, cloud shadows absent (−1); "THE AGENT GATE" eyebrow vs "coded rules", and "old rule" wording (−1) |
| Evidence and feasibility (30) | 24 | **26** | Honest S7 title, baseline stated, paired tests, run time, expected outcome | No intervals (−1.5); He baseline not in the chart and not retrained (−1); one real tile with little detail back, n = 24 (−1); corner quirk under S6–S7 undisclosed (−0.5) |
| Critical human review (20) | 14 | **16** | Own checks, decision counts, "never been scored", open-items slide | Plan undated (−1.5); critic's "revise" vague, and its five changes were accepted as defaults by Claude, not by Justin (decision log row 22) (−1); "in his words / rewritten" slightly overstated (−0.5); S6 notes lost the "favours us" caveat (−1) |
| Presentation and delivery (20) | 13 | **17** | 3.7 min notes, full references with DOIs, licence conflict, aligned eyebrows, units, coordinates, credits | S4 image date ambiguous (−0.5); Haralick abstract only (−0.5); no source line on S7 or S10 (−0.5); no intervals on S7 (−0.5); delivery not yet rehearsed (−1, assumed) |

### R2 spot checks of the new claims (all OK unless marked)
- **S3 and S4:** 55.3% matches ev. 01 l.62. The coordinates match the development-tile georeference (0_18_13 at
  29.67°N 89.97°W; 2_15_45 and 2_23_44 at 29.76°N 90.08–90.13°W). "~5 m band" matches `road_band.json` (5.14 m).
- **S4 image date — imprecise:** "(end of August 2021)" reads as the date of the before images too. The paper gives
  event timing only, and the pre-event catalog dates are unverified (ev. 08 §2a).
- **S7 and S8:** "5 fixed, 15 broken (p = 0.04)" matches panel 0.0414; the He caption (21/24, 74%) is OK; "under an
  hour" matches the run times (16 and 45 min).
- **S11:** the counts 28 / 10 / 6 match `decision_log.md`. But 2 of the 28 rows have no quote from Justin, and the
  "10" are "Changed", not "rewritten".
- **S12–S13:** they match ev. 08 (Crossref).
- **S14:** "29 clear tiles", "1% limit" and the corner quirk all match ev. 07. The quirk touches the corrected image of
  **103 of 226 development tiles**, so the S7 "trained de-hazed" features and the S6 "0%" rest on it.

### R2 remaining fixes, exact wording (cheap ones first)

| # | Slide | Change |
|---|---|---|
| A | Done copy | Copy `render/Seeing_Through_Clouds_round2.pdf` over `assignments/Done/JustinRogersA4GGS662.pdf` before 23:59. |
| B | S8, S9, masks notes | Version wording. S8: "F1 0.65 against 0.41 for the old rule (HRC_WHU)" → "F1 0.65 against 0.41 for the bright rule (HRC_WHU)". S9 legend: "bright rule (our old tile rule)" → "bright rule (tile-rule baseline)". masks notes: "The old bright rule" → "The bright rule". |
| C | S3 eyebrow | "GGS 662 · THE AGENT GATE" → "GGS 662 · THE HANDLE GATE". This removes the clash with "the handle gate is coded rules". |
| D | S11 AI use | "28 decisions on AI suggestions are logged in his words (10 rewritten, 6 rejected)." → "28 decisions on AI suggestions are logged, most in his own words (10 changed, 6 rejected)." |
| E | S6 table | Two-date "clear altered": "0%" → "<0.1%". This matches val. 10-25 1.4 and the corner quirk on S14. |
| F | S6 notes | After "leaves clear ground alone." add: "This test favours our method, because the fake haze follows our model." The notes go to 568 words, 3.8 min. |
| G | S7 caption | Append: "Labels: SpaceNet 8 (Hänsch et al. 2022); imagery: Maxar via SpaceNet 8." |
| H | S10 footnote | Append: "Imagery: Maxar via SpaceNet 8, tile 2_23_44." |
| I | S4 Imagery row | → "Maxar Open Data before and after Hurricane Ida (landfall 29 Aug 2021), 0.5 m; image dates unconfirmed; used in greyscale" |
| J | S8 Limits, 1st bullet | → "One event, one sensor, roads only; all real cloud in one after image; cloud shadows untested" (ev. 01 open question) |
| K | S8 Limits, last bullet | "The method critic's verdict on the plan: revise" → "Methods critic's five changes: adopted as defaults, not yet reviewed by me" |
| L | S14 backend | "De-hazer nudges a corner of cloud-free tiles; fix with a test" → "De-hazer edits a 20 m corner of cloud-free tiles (103 of 226); fix, then rerun result 3". Add the row "RUNNING · He baseline trained on de-hazed images, with 95% intervals (result 3)". |
| M | S7, when the run lands | Add the 4th bar. Add whiskers, with the caption "Whiskers: 95% interval, tiles resampled (n = 24 / 69 / 175)". Replace the He sentence with the new arm's numbers. If the run lands after the upload, tag the slide "Added after the 25 Oct submission". **Run it on code with the corner fix**, or footnote that the two-date bars predate the fix. Otherwise the new bar is not like-for-like. Recheck that the title still holds. |

### Losses that need new work or the author's decision (candidates for S14; do not chase)

| Loss | Needs | Proposed S14 row (or why not) |
|---|---|---|
| Handle question is untestable on real data (no cloudy before image in Louisiana-East, ev. 01 l.39, ev. 07) | Data | "DATA · An event with a cloudy before image, to test the handle question on real cloud" |
| He baseline not retrained; no intervals | Run (in progress) | "RUNNING" row (fix L) |
| Corner quirk under the S6–S7 numbers | Code fix and rerun | Reworded TO FIX row (fix L) |
| Only 24 trusted flooded roads; one event and one sensor; one real tile | Data | Already on S8 Limits; nothing to add |
| Critic's five changes accepted by Claude, not by Justin | Author's decision | "DECIDE · The methods critic's five changes (now defaults)" |
| Plan has no dates (he dropped the 8-week grid) | Author's decision | Not for S14 unless he wants it. If he agrees, add to the next notes: "Each step is a run of under an hour, so these fit before the paper." |
| Refinement since the proposal is only implied | Author's decision (no assignment or version wording) | Not for S14. The "Design choices" line already recovers most of it. |
| Pre-event acquisition dates | Access (Maxar Ida page down; catalog IDs in ev. 08) | "ACCESS · Dates for the four Maxar catalog IDs" |
| Haralick 1979 full text | Access | Already on S14 (GMU login) |
| SpaceNet 8 licence conflict | Answer from the data owner | Already on S14 |
| Delivery and timing | Rehearsal | Not for S14. Rehearse twice with a timer before Friday. |

**After the cheap fixes (A–K), the estimate is about 88.** With the pending run (M) on fixed code, it is about 89–90.

## Round 3 (2026-10-25, about 22:15): `render/Seeing_Through_Clouds_2026-10-25_final.pdf`, 14 slides

- **Read:** all 14 PNGs, every note, `he_dehazed_numbers.json` and its plan (the logged deviation is fine), evidence 06,
  and the decision-log rulings.
- **Done copy:** `assignments/Done/JustinRogersA4GGS662.pdf` is **still the 19:47 11-page build**. Copy the final PDF over it
  before 23:59.
- **Main-talk notes:** 38+94+60+63+76+89+103+100 = **623 words = 4.2 min**. Round 2 was 555.
- **Score: 87 / 100.** Slide and notes edits alone (§R3-A) reach about 93. Justin's four inputs (§R3-B) reach about 96.

| Criterion | R2 | R3 | Gained | Still lost |
|---|---|---|---|---|
| Refined method (30) | 26 | **27** | The Handle question now matches the method (either date, seen through in preprocessing); "Working rules" define change; Detect on hold is stated | S3 "one sealed check" contradicts the no-sealed-look ruling (−1); the question's benchmark "as well as under clear sky" is shown nowhere (−1); He 2011 is missing from S3's baselines (−0.5); "Working rules" give no reason, where round 2's "Design choices" did (−0.5) |
| Evidence and feasibility (30) | 26 | **26.5** | A fair baseline (He trained de-hazed), 95% whiskers, paired tests both ways, a source line, the road-finding result | Our method does not beat the baseline, and there is no rule for what happens if it never does (−1); n = 24 and one event (−1, needs data); the two-date bars predate the corner fix (−0.5, rerun running); no clear-sky benchmark (−0.5); the whiskers sit beside the bars, not on them (−0.5) |
| Critical human review (20) | 16 | **16** | Justin's rulings logged and shown (S14 DECIDED); "two-date not yet better than He" stated; plan written first, with the deviation logged | **S14 notes are stale** (−1); the critic's five changes are still unreviewed (−1); the plan is undated (−1); the AI-use count is stale (−0.5); "no difference" on S7 for a non-significant result (−0.5) |
| Presentation and delivery (20) | 17 | **17.5** | S7 is now a strong graphic; "single image" wording fixed; text ≥ 24 px throughout | Notes 4.2 min, over (−1); rehearsal not done (−1); S7 is dense (−0.5); Haralick abstract only (−0.5) |

### R3 spot checks
- **S7 matches `he_dehazed_numbers.json`:**
  - 71/83/92% (17/20/22 of 24); 9/43/13% (6/30/9 of 69); 78/77/77% (136/134/135 of 175);
  - two-date 4 fixed / 1 broken, p 0.375; He 5/0, p 0.0625; clear roads p 0.80 and 1.00;
  - He vs two-date: flooded 2/0, p 0.50; clear 14/13, p 1.0; dry-labelled 24/3, p < 0.001;
  - cloud variable: arm 3 vs arm 1, 16 vs 17 found and 3 vs 6 called flooded.
- **S6 flood box:** 20 / 22 / 17 is OK.
- **S14:** F1 0.020 → 0.017 matches evidence 06 l.64–65 (before image 0.640).
- **S11:** **28 → 33 decisions, 10 → 11 changed.** The log now has 34 rows; 33 exclude the Claude-default row.
  There are 6 rejected and 3 decided. Two rows have no quote from Justin, so "most in his own words" holds.
- **New number (reviewer-computed, log it before use):** on the same 39 tiles, the clear-sky benchmark is
  **81 of 95 flooded roads found (85.3%) in all three arms.** On all 798 assessable roads it is 88%.
  - I computed it row-wise from `cloudvars_calls.csv` (arms 1 and 2) and `he_dehazed_calls.csv`, whose rows align
    1:1. Those files hold development calls only; no label file was opened.
  - Under thin cloud the three arms are 71 / 83 / 92%, so de-hazing reaches the clear-sky level. This directly answers
    the new Handle question, within wide intervals: "none" (42–88%) also covers 85%.

### R3-A · Slide and notes edits, no new work (ranked; paste-ready)

| # | Where | Exact change |
|---|---|---|
| 1 | Done copy | Copy `render/Seeing_Through_Clouds_2026-10-25_final.pdf` over `assignments/Done/JustinRogersA4GGS662.pdf` |
| 2 | S3 Baselines and checks | "Tile cloud rule; no correction. Tile-blocked folds (Roberts et al. 2017), McNemar tests (McNemar 1947), one sealed check." → "Tile cloud rule; no de-hazing; He 2011. Tile-blocked folds (Roberts et al. 2017), McNemar tests (McNemar 1947); a second event as the final test." |
| 3 | S7 caption | "Production flood model, 5 folds by tile, trained on the kind of image it is tested on (trained on uncorrected images, two-date cost clear roads: 5 fixed, 15 broken, p = 0.04)." → "Each model is trained on the kind of image it is tested on (5 folds by tile). Clear sky, same tiles: 81 of 95 flooded roads found (85%). Two-date rerun after a code fix: slide 14." This is 6 words shorter. Better still, also draw a dashed line at 85% across the first group, labelled "clear sky 85%". Log the number in evidence 01 first. |
| 4 | S14 notes | Replace all of them with: "This slide lists what is still open. Road finding under cloud is done: de-hazing gave no gain. The corner fix and a smoother cloud edge are running; before-date cloud and the faint-haze gate need fixing. Decided: sealed tiles stay untouched, synthetic clouds wait, change means anything but lighting, floods only. Still open: the critic's five changes, the report-tier cut-offs, a second event, and three access items." |
| 5 | Notes cut, 623 → about 575 | Question: delete "; for now that feeds a flood model for roads" and "Synthetic clouds as a test bed wait until we can see through real cloud." Flood: delete ", and each model is trained on the kind of image it is tested on" and "Cloud as an extra variable found no more flooded roads."; add "On clear roads of the same tiles it finds 85 percent." Next: delete ", then tie it back into the road and flood work". |
| 6 | S11 AI use | "28 decisions on AI suggestions are logged, most in his own words (10 changed, 6 rejected)." → "33 decisions are logged, most in his own words (11 changed, 6 rejected)." |
| 7 | S7 "Two-date against He 2011" box | "no difference" → "no significant difference" |
| 8 | S2 Working rules | "Cloud in either image is seen through first, as a preprocessing step." → "Cloud in either image is seen through in preprocessing, so the detector never reads cloud as change." This restores the justification. |
| 9 | S14 DONE row | → "Road finding under cloud vs OSM: no gain (F1 0.020 → 0.017; before image 0.64)". Without the 0.64 the detector looks broken. |
| 10 | S11 method attributions | The S7 whiskers use a tile bootstrap. Add "Efron 1979, bootstrap (Annals of Statistics)" and, on S12, "Efron, B. (1979). Bootstrap methods: Another look at the jackknife. *Ann. Statist.* 7(1), 1–26. doi:10.1214/aos/1176344552". Check it against Crossref first. |
| 11 | S7 cloud-variable box | "as cloudy roads were labelled dry" → "likely because cloudy roads were labelled dry" (it is an inference) |
| 12 | S7 chart (generator) | Centre each whisker on its bar instead of beside it. |

### R3-B · Needs Justin (decisions or actions; not slide wording)
1. **The critic's five changes** (decision_log row 22). His rulings tonight already settle two of them:
   - (2), the synthetic realism test, is on hold;
   - the sealed-look rule in (3) is dropped;
   - (4), non-inferiority against clear sky, is now the Handle question itself.
   If he rules "(1), (4), (5) adopted; (2) and the sealed part of (3) dropped", then the S8 Limits bullet and the
   S14 DECIDE row can both go (+1, and fewer words).
2. **A method decision rule** if two-date never beats He. For example, the S8 next step "Freeze the de-hazer; test it
   on a second event" → "Freeze the better de-hazer (two-date or He 2011); test it on a second event" (+0.5–1).
   It is his method choice.
3. **Rehearse twice with a timer** at under 4:00 (+1).
4. **GMU login** for the Haralick full text, then delete "(abstract checked)" (+0.5).
5. **Optional:** a target week per next step. He dropped the 8-week grid, so this stays at −1 unless he wants it.

### R3-C · Needs new runs or data (cannot be fixed by edits; leave on S14)
- **The corner-fix rerun (RUNNING).** When it lands, update the S7 two-date bars and the S6 flood box. If it lands
  after the upload, tag them "Changed after the 25 Oct submission" (about +0.5).
- **A second event, ideally with a cloudy before image (DATA).** n = 24, one event and one sensor stay at −1.5 to −2
  until then. This is the main reason 98+ is out of reach by Friday.
- **The ring at the cloud edge (RUNNING), and the before-date and faint-haze fixes (TO FIX).** These are method work.
  The S6 real tile ("little road detail returns") improves only with them.
- **Pre-event image dates (ACCESS).** Worth −0.25; accept it.

## Round 4 (2026-10-25, about 22:25): `render/Seeing_Through_Clouds_round4.pdf` (= `Done/JustinRogersA4GGS662_update.pdf`)

- **Read:** all changed PNGs (S2, S3, S7, S8, S11, S12, S14) and every main-talk note.
- **Main-talk notes:** 38+71+60+63+76+89+90+92 = **579 words = 3.9 min**.
- **Benchmark:** the clear-sky 81 of 95 is logged in evidence 01 l.212.
- **Applied correctly:** fixes 2–8 and every small item. Efron sits correctly under method attributions (below the JIF
  rule). Keeping the whiskers offset is accepted: it is readable, and I count it −0.25.
- **Which file gets graded:** `Done/JustinRogersA4GGS662_final.pdf` is byte-identical to round 3 (22:08). If that is
  the file uploaded, the graded slides are the round-3 deck (87). Round 4 then counts only as "improved before
  presenting", and its new result must be tagged (fix 2).
- **Score: 93 / 100 for round 4.**

| Criterion | R3 | R4 | Gained | Still lost |
|---|---|---|---|---|
| Refined method (30) | 27 | **29** | No sealed check; He in the baselines; working rules give a reason; the clear-sky benchmark answers the Handle question | The workflow diagram does not show where the agents, Justin or the checks act (−0.5); the Detect question is on hold, leaving two active questions (−0.5) |
| Evidence and feasibility (30) | 26.5 | **28** | The 85% dashed line, the rerun-pending note, and the "freeze the better de-hazer" rule (feasibility no longer rests on two-date winning) | n = 24, one event and one sensor (−1, data); little real-tile recovery (−0.5, method work); corner rerun pending (−0.25); offset whiskers (−0.25) |
| Critical human review (20) | 16 | **18** | Fresh S14 notes; 33/11/6; "no significant difference"; a stated decision rule | Critic's five changes unreviewed (−1, Justin); plan undated (−1, Justin's choice). The decision rule is a coordinator default under his standing rule; it holds unless he overrules it. |
| Presentation and delivery (20) | 17.5 | **18** | 3.9 min notes; Efron cited and listed in full | Rehearsal not yet done (−1, Justin; graded live); Haralick abstract only (−0.5, Justin); S7 caption is 5 dense lines (−0.25); one ambiguous note line (−0.25) |

### R4 · Remaining fixes, exact wording
1. **Upload choice (Justin, tonight, highest value).**
   - It is still 25 Oct, so the round-4 PDF can be the upload. That lifts the graded slides from about 87 to about 93,
     and no "added after submission" tags are needed.
   - Keep the 19:47 and `_final` files for comparison, as he asked; just upload `_update`.
   - If `_final` stays the upload, apply fix 2.
2. **Tag the new result (only if `_final` is the upload).** S7 caption: "Dashed: clear sky on the same tiles, 81 of 95
   flooded roads found (85%)." → "Dashed, added after submission: clear sky on the same tiles, 81 of 95 flooded roads
   found (85%)." The other round-4 changes are wording, citation or plan changes, not results, so they need no tag.
3. **Flood notes.** "On clear roads of the same tiles it finds 85 percent." → "Under clear sky on the same tiles, it
   finds 85 percent of flooded roads." This stops it being heard as the 78% "clear roads" accuracy one sentence before.
4. **After Justin rules on the critic (R3-B 1):**
   - S8 Limits: "Methods critic's five changes: adopted as defaults, not yet reviewed by me" → "Methods critic: three
     changes adopted, two set aside by my rulings". Deleting the bullet instead is shorter.
   - S14: delete the "DECIDE · The methods critic's five changes (now defaults)" row, and add "; critic's changes ruled"
     to the DECIDED row.
5. **After the GMU login:** S11 "Texture features · Proc. IEEE (abstract checked)" → "Texture features · Proc. IEEE".

### R4 · Honest ceiling
- **Without Justin's inputs: about 94.** That is 93 plus fix 3 and fix 2 if needed. Neither the critic's review, the
  rehearsal, the Haralick full text nor dated steps can come from slide edits.
- **With Justin, by Friday: about 96–97.**
  - critic ruling +1, rehearsed under 4:00 +1, Haralick +0.5 (96.5);
  - +1 more if he allows a target week per next step;
  - +0.25 when the corner-fix rerun lands, re-tagged "changed after submission" if it moves the S6–S7 numbers.
- **Above 97 needs new data:** a second event, and more than 24 trusted flooded roads under cloud. That cannot happen by
  Friday, so about 2 points stay on the table, and that is the correct place to leave them (S14 DATA row).
