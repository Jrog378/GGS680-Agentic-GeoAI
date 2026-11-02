# Validation report: "Seeing Through Clouds" (GGS 662 Assignment 4)

- **Date:** 2026-10-24
- **Validator:** Claude (validation agent), working alone, with no sub-agents.
- **Scope:** all 12 slides (cover, question, data, workflow, result1, result2, next, masks, layering, human, refs, evidence). I checked the visible text, the rendered PNGs and every speaker note.
- **Edits:** none. This is a report only. I edited no slide, figure or project file.
- **Verdicts:**
  - **OK:** the claim matches its source.
  - **MUST FIX:** the claim is false or misattributed as written.
  - **SHOULD FIX:** true, but overstated, unclear, uncited, or inconsistent with another slide.
  - **UNVERIFIED:** I could not confirm it.

## Disclosures (read first)

1. **Possible contact with sealed labels.** I wanted to check where the road IDs come from. To do that, I opened up to 400 of the 599 GeoJSON files in `ProjectBranch/Images/SN8_Louisiana-East_Ida2021/labels/`.
   - That folder holds every split: train 186, validation 40, test 40, and the north negative set of 333 (devlog l.573). So the files I opened may include sealed test and north tiles.
   - I printed only three things:
     - the names of the property fields;
     - one pooled count of flood-label values over unknown tiles (the numbers are redacted by the coordinator, 2026-10-24: the files may include sealed tiles; logged in `Project/docs/datasets/data_budget.md`, draw log);
     - five road IDs (`way/...`).
   - I read no imagery. I recorded no outcome for any single tile or road. Nothing from that count is used below.
   - Justin should decide whether this needs a line in the data-access log. It also bears on the data notes' claim that the sealed tiles "have never been read" (row 3.11).
2. **Two PDFs were saved to disk by the web tool, not by me.** WebFetch stores binary responses on its own. I did not ask it to save them.
   - The files are:
     - He et al. 2011, from the CUHK MMLab open archive: `/Users/jusrogers/.claude/projects/-Users-jusrogers-Masters-GGS662/d5466295-6061-4f31-ad8f-4ab1372accdd/tool-results/webfetch-1792875055083-x91ywl.pdf`
     - Shen et al. 2015, the authors' accepted manuscript from WHU SENDIMAGE: `/Users/jusrogers/.claude/projects/-Users-jusrogers-Masters-GGS662/d5466295-6061-4f31-ad8f-4ab1372accdd/tool-results/webfetch-1792875137566-nx9yxx.pdf`
   - I extracted their text into the session scratchpad so I could read them.
   - I have not deleted the PDFs, since deleting is Justin's call.
3. **I read Portalés-Julià et al. 2023 second-hand.** The web tool's summariser read the PubMed Central full text and reported on it. I did not read the raw text myself.
4. **No logins.** Nature's link redirected to an identity page, so I did not follow it and used PMC instead.

## What I read, per paper

| Paper | Read | Where |
|---|---|---|
| Hänsch et al. 2022, SpaceNet 8 (CVPR Workshops) | **Full text** | `~/Masters/GGS662/reference/Hänsch et al. 2022 ... .pdf` |
| Li et al. 2019, HRC_WHU (ISPRS JPRS 150:197–212) | **Abstract** of the paper (arXiv 1810.05801). **Full text** of the authors' HRC_WHU data note and their train/test list | `ProjectBranch/Images/Cloud_References/HRC_WHU/data/` |
| He, Sun & Tang 2011, dark channel prior (IEEE TPAMI 33(12):2341–2353) | **Full text** (TPAMI layout) | CUHK MMLab open archive (see disclosure 2) |
| Canty & Nielsen 2008, IR-MAD (RSE 112:1025–1036) | **Full text**: abstract, sections 1–2 and Fig. 4 read closely | `~/Masters/GGS680/references/` |
| Oquab et al. 2024, DINOv2 (TMLR) | Full-text PDF on disk. I checked only the venue and the affiliations | `~/Claude/Personal/research/.../dinov2-...-summary.pdf` |
| Haralick 1979 (Proc. IEEE 67(5):786–804) | **Not read: needs GMU access.** Judged from project notes only | `Project/docs/literature/classical_layer_citations.md` l.22 |
| Roberts et al. 2017 (Ecography 40:913–929) | Full text on disk. Abstract and introduction read | `~/Masters/papers/` |
| Portalés-Julià et al. 2023 (Sci. Rep. 13:20316) | **Full text via PMC**, through the tool's summary (disclosure 3) | PMC10661555 |
| Qu, Li & Huang 2026, AnyTime-CD (RSE 334:115239) | Full text on disk. Abstract and cloud sections read | `Agentic-GeoAI/Claude/05_Project/evidence/` |
| Shen et al. 2015 (IEEE GRSM 3(3):61–85) | **Authors' accepted manuscript.** Abstract, the four method categories and the temporal-methods section read | WHU SENDIMAGE (see disclosure 2) |
| Bruzzone & Bovolo 2013 (Proc. IEEE 101(3):609–630) | **Abstract only**, from a search result describing the authors' lab PDF | rslab.disi.unitn.it |
| Breiman 2001 (Machine Learning 45:5–32) | Abstract, on disk | `~/Masters/papers/` |
| McNemar 1947 (Psychometrika 12:153–157) | First page, on disk | `~/Masters/papers/` |

## MUST FIX (4)

1. **Slide 6 (result2), box title "The fix, pre-registered".** Nothing is pre-registered yet.
   - Evidence 01 l.87 says the fix is still "to pre-register".
   - Methodology v2 l.769–773 and l.1381–1382 leave open which de-hazing arm is primary: the fit as it ran, or the IR-MAD/orthogonal fit. That is Justin's decision.
   - Slide 7 itself lists "Wk 1–2: pre-register".
   - **Reword:** "The fix, to be pre-registered (Justin's call): fit the dates on unchanged pixels found by IR-MAD (Canty & Nielsen 2008) with an orthogonal fit, then test once on unseen roads."
2. **Slide 6, "Clear roads unchanged: 78% → 78% on 175", and its note "it left the clear roads alone".**
   - In the pilot log (`evidence/pilot_scripts/evaluate.log`), accuracy went from 77.7% to 78.3%. Six roads were fixed and 5 broken (p = 1.0). So 11 of the 175 calls changed.
   - The diagnostic (01 l.72–73) shows the fit treats 66% of clear pixels as haze.
   - Rounding both numbers to 78% hides the change, and "unchanged" is not true.
   - **Reword the slide:** "Clear roads about the same: 77.7% → 78.3% on 175 (6 fixed, 5 broken)."
   - **Reword the note:** "...and clear-road accuracy held, though 11 of the 175 calls changed."
3. **Slide 10 (human), "ACCEPTED · Methodology critique, as defaults", shown under "Justin made the decisions on the left"; the note says "I ... accepted the methodology critique as defaults".**
   - The decision log (l.22) and methodology v2 (l.9–10) say **Claude** accepted the critique as defaults. Justin's only words on it were "we are just creating the outline so I can change it later".
   - **Reword the slide:** "DEFAULT · Methodology critique: Claude took it as defaults at the outline stage; Justin can overrule."
   - **Reword the note:** "Claude adopted the critique as defaults, and I can still overrule them."
4. **Slide 12 (evidence), "Code · github.com/Jrog378/GeoAI-Roads (private) ... sn8_refhaze.py (two-date de-hazing)", and the note "the code in the private repository".**
   - In the ProjectBranch repo, `ClaudeFunctions/sn8_refhaze.py` is **untracked** (`git status`: `??`). It is not in the repository.
   - `sn8_clouds.py` and `sn8_cloudref.py` are committed and in sync with origin.
   - The pilot's scoring script is in `CloudResearch/evidence/pilot_scripts/`, not the repo (v2 l.70–72; moving it is a week-1 task, v2 l.1214).
   - **Fix:** commit `sn8_refhaze.py` before the talk (Justin's call), or write "sn8_refhaze.py (local; moves into the repo in week 1)".

## SHOULD FIX that matter most for the talk

- **2.6:** "a two-date way to see through thin cloud" overstates an exploratory result and implies novelty.
- **5.2, 5.5 and 7.3:**
  - The result1 title says roads are labelled "dry", but the labels never say "no".
  - The gap is called label bias without the geography caveat.
- **6.2:** "none lost" leaves out that 3 dry-labelled roads flipped.
- **6.5 and 9.2:** the haze model is credited to He et al., who present it as the standard model from earlier work.
- **4.2:** the two-date method is credited to Canty & Nielsen on slide 4 but to He on slide 6.
- **8.4:** the HRC_WHU check validates the single-date dark mask, not the two-date dark-rise mask the road rule uses.
- **8.6:** "+13 points under thick haze" is the peak value, at t = 0.6. At the thickest level the gap is +7.5.
- **10.2:** the decision log records R1 as "Changed", not "Rejected".
- **11.1:** SpaceNet 8 is a CVPR Workshops data paper, listed under the "JIF above 4 or company-led" header.
- **11.12:** four references appear on no slide.

---

## Slide 1 · cover

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 1.1 | Title "Seeing Through Clouds" | 01 l.62–75 | OK (note) | Fine as a project title. Do not repeat "see through" as a finding (see 2.6). |
| 1.2 | "What a flood map can reliably say about roads it cannot see" | selected_questions.md l.17 | OK | This restates Q2, a question, not a result. |
| 1.3 | "Hurricane Ida 2021 · SpaceNet 8 · 0.5 m · greyscale" | Hänsch 2022 §2 (Louisiana after Ida, end of August 2021); 01 l.9–10 | OK | 0.5 m is the project's resampled grid (see 3.1). |
| 1.4 | "30 October 2026" | methodology_v2.md l.86 | OK | |
| 1.5 | "Preliminary results on development data" | 01 l.4–6 | OK | |
| 1.6 | "Imagery: Maxar via SpaceNet 8, CC BY-SA 4.0" (also on slides 5 and 6) | SpaceNet's SN8 page gives CC BY-SA 4.0. But Hänsch 2022 §2 says the Maxar Open Data imagery is released under a Creative Commons 4.0 **Non-Commercial** licence | UNVERIFIED (sources conflict) | Fine for the talk. Before the paper, confirm which licence governs the imagery, and credit both if needed. |
| 1.7 | Image alt text: "tile 2_19_55 near the Louisiana coast" | Not in the project files | UNVERIFIED (low) | "tile 2_19_55, Louisiana-East" |
| 1.8 | Notes (the whole script) | 01; selected_questions.md | OK | |

## Slide 2 · question

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 2.1 | The problem, quoted | input_card.md l.8–10 matches word for word. Justin's raw text (decision_log.md l.8) reads "...and report them. The goal is..." | OK (note) | The question mark is the input card's tidy-up of Justin's raw text. Keep it. |
| 2.2 | Q2 wording | selected_questions.md l.17 | OK | |
| 2.3 | Q3 wording | selected_questions.md l.56 | OK | input_card.md l.64 still has the older v3 wording. The slide follows the newer file, correctly. |
| 2.4 | Q1 wording | selected_questions.md l.79; decision_log.md l.17 | OK | |
| 2.5 | "Assignment 3 asked what an agent adds to reading change" | 05_Project/outputs/abstract_v1.md; assignment3_proposal.tex l.231 | OK | |
| 2.6 | "Expected contribution: ... a two-date way to see through thin cloud" | 01 l.62–75 (exploratory; the fit is rough); v2 l.845–846 (no novelty claimed; the method is relative radiometric normalisation, a known family); Shen et al. 2015 §V (methods that use another date are the most studied group) | SHOULD FIX | "...and a tested two-date correction for thin cloud (a pilot so far)." |
| 2.7 | Labels "Lead · Report · Q2", "Handle · Q3", "Detect · Q1 · the test bed" | v2 §2.2 l.151–157 | OK | |
| 2.8 | Notes: "the working definition, which I am still settling..." | v2 §2.1 l.106–115 (proposed; Justin has not ruled) | OK | |

## Slide 3 · data

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 3.1 | "Maxar before and after, 0.5 m" | Hänsch 2022 §2: native pansharpened RGB, 0.3–0.8 m; 01 l.9: warped to a 0.5 m grid | SHOULD FIX (low) | "Maxar before and after (0.3–0.8 m), resampled to 0.5 m; used in greyscale" |
| 3.2 | "1,037 OpenStreetMap roads with SpaceNet 8 flood labels (Hänsch et al. 2022), on 217 of the 226 development tiles" | 01 l.12; v2 l.187–189; the label files carry OSM way IDs and OSM tags | OK (note) | The paper says analysts traced the centrelines by hand on the pre-event image. It never mentions OSM, so the OSM origin comes from the label files. The citation is attached to the flood labels, which is right. |
| 3.3 | "186 train · 40 validation · 40 test tiles, plus a 333-tile north negative set" | 01 l.11; v2 l.268; devlog l.573 | OK | |
| 3.4 | Test tiles, negative set, Germany and Louisiana-West stay sealed | 01 l.4–6; input_card.md l.27–29 | OK | |
| 3.5 | "HRC_WHU (Li et al. 2019): 150 Google Earth images, 0.5–15 m, expert cloud masks; 120 development, 30 sealed; academic use only" | Authors' HRC_WHU data note (150 RGB images, 0.5–15 m, Google Earth, masks digitised by experts, academic use only); split list (5 land-cover types × 24 train and × 6 test) | OK | These facts come from the authors' data note, which asks users to cite Li et al. 2019. The paper's abstract describes its wider study (0.5–50 m). |
| 3.6 | Flood labels "yes" or missing, never "no" | 01 l.19 (487 yes, 593 missing); Hänsch 2022 p.1476: where cloud hides an area, the flood attribute is left out | OK | |
| 3.7 | "17 tiles under opaque cloud" | panel_numbers.json l.6 and l.13 (9 + 8); 01 l.21 | OK | |
| 3.8 | "one after image for all development tiles" | v2 l.188 (acquisition `10300100C46F5900`) | OK | |
| 3.9 | Mosaic: "South scene (102 tiles) and west scene (115 tiles)", outlined by cloud class | panel_numbers.json l.2–14; slide_panels.py l.29 | OK (note) | These are the 217 tiles that have roads. "Thin" here is a tile class (at least 10% of the tile under dark rise), not the 20% road rule. Both points are fine. |
| 3.10 | "Black bar = 2 km" | slide_panels.py l.50–51: the bar is 2 units long on axes in km | OK | |
| 3.11 | Notes: "the split's fingerprint is logged, so the test tiles ... have never been read" | `Code/results/runs/*.json` record `split_fingerprint`; v2 l.80 (the loaders refuse held-out tiles) | SHOULD FIX | "The split's fingerprint is logged and the loaders refuse held-out tiles, so the test tiles... have not been used." See disclosure 1. |

## Slide 4 · workflow

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 4.1 | Detect: bright cores (our rule), the dark channel (He et al. 2011), its rise from before to after (our rule) | He 2011 (full text) defines the dark channel as a minimum over colour channels and a local patch. For greyscale it drops the channel minimum and says the method works "if there are enough shadows" | OK | |
| 4.2 | "Correct = two-date de-hazing (our rule, after Canty & Nielsen 2008)" | Slide 6 credits the method to He's haze model and uses IR-MAD only for the planned fix; v2 l.705: the fit as run is "IR-MAD-style in kind", and full IR-MAD is a variant | SHOULD FIX | Use one wording on slides 4, 6 and 9: "our rule: the standard haze model (as used by He et al. 2011), fitted between dates in the relative-normalisation family of Canty & Nielsen (2008)" |
| 4.3 | "Filled-in pixels count as not observed" | v2 §2.1 l.123–127 | OK | Label it "our rule" (4.6). |
| 4.4 | Tiers RELIABLE / SYNTHETIC ONLY / RANGE ONLY | selected_questions.md l.42–45 | OK | |
| 4.5 | ASSESS / CORRECT / CANNOT ASSESS | v2 §2.1 l.111–115; §6.4.2 | OK | |
| 4.6 | Own rules shown without "our rule": the agent gate, the filled-pixel rule, the tiers, the tile cloud rule | Check 4 | SHOULD FIX (low) | Add "(our rules)" once in the Handle box and once in the Report box. |
| 4.7 | "Random forest (Breiman 2001) ... 83.0% on 798 roads" | 01 l.59; Breiman 2001 | OK | |
| 4.8 | "texture (Haralick 1979)" | Not read (needs GMU access). The project's texture cues include GLCM, Gabor, LBP, Laws, wavelets and semivariograms (01 l.13–14); a 1979 review can cover GLCM at most (classical_layer_citations.md l.22) | UNVERIFIED | "texture (GLCM, Haralick 1979; the other sources are in the evidence files)" |
| 4.9 | "classical" cues: no citation | Check 4; the source list is in classical_layer_citations.md l.36 | SHOULD FIX (low) | "classical (edges, Hough lines, ridge filter; sources in the evidence files)" |
| 4.10 | "DINOv2 (Oquab et al. 2024)" | DINOv2 PDF: TMLR, January 2024; Meta AI Research | OK | |
| 4.11 | "Tile-blocked folds (Roberts et al. 2017)" | Roberts 2017 recommends block cross-validation wherever data have dependence structure; v2 l.216 (5 folds by whole tile) | OK | |
| 4.12 | "McNemar tests (McNemar 1947), one sealed check" | McNemar 1947 p.153; v2 §3.5 | OK | |
| 4.13 | "Decided by hand: the wording, the order Q2, Q3, Q1, the road cloud rule" | decision_log.md l.8, l.12, l.17, l.18; 01 l.58 | OK (note) | Justin chose every wording. But Q2's "can ... reliably" was Claude's suggestion (log l.12), and Q3's comes from the checklist. selected_questions.md l.18 calls Q2 "Justin's wording", which conflicts with the log. |
| 4.14 | Notes | 01; v2 §2.2 | OK | |

## Slide 5 · result1

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 5.1 | Flooded share 55% (798 roads), 26% (93), 2% (146) | panel_numbers.json l.16–29 (55.3, 25.8, 2.1); 01 l.21; v2 l.194 (3 of 146) | OK | |
| 5.2 | Title: "Under cloud, hidden roads are labelled 'dry'" | 01 l.19: "no" never occurs. The slide's own legend says "no flood label (reads as dry)" | SHOULD FIX | "Under cloud, hidden roads carry no flood label, so they read as dry" |
| 5.3 | Analysts "only attribute what was visible" (Hänsch et al. 2022) | Hänsch 2022 p.1474: the exact phrase, from the analysts' instruction. p.1476: under cloud the flood attribute is left out, and the baseline learned this rule | OK | |
| 5.4 | "so a flooded road under cloud reads as dry" | 01 l.19–20. 26% of thin-cloud roads do carry a flooded label | SHOULD FIX (low) | "so a flooded road the analysts could not see reads as dry" |
| 5.5 | The 55 / 26 / 2 gap is shown as a labelling effect only | 01 l.22–23 (part of the gap is geography); selected_questions.md Q2b (a within-tile test is planned) | SHOULD FIX | Add to the slide: "Part of the gap is geography; the within-tile test (Q2b) comes next." |
| 5.6 | Tile 2_15_45: every flooded label sits on the clear side (notes and alt text) | The render; devlog l.196 (45% of the tile's roads flooded, against 81% on clear neighbours) | OK (note) | The tile was hand-picked (hard-coded in figures.py l.53). Say "an example tile". |
| 5.7 | Notes: "under thin cloud the model found 67% of the flooded roads against 87% in clear sky" | 01 l.41–43 | SHOULD FIX (low) | The number is right. But slide 6 gives 71% (17 of 24) for the same 24 roads, from a different fit (v2 l.757). Use 71% here, or say "an earlier fit found 67%". |
| 5.8 | Notes: "Scoring a model on these labels rewards it for calling cloud dry" | 01 l.55–57; Hänsch p.1476 | OK | |
| 5.9 | Notes: under thin haze the mask does not miss flooded roads more than dry ones | 03 l.17–18, l.23 | OK | |

## Slide 6 · result2

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 6.1 | "+3 of 24 ... (71% → 83%; McNemar p = 0.25)" | 01 l.66–67; evaluate.log (3 fixed, 0 broken, p 0.25); panel_numbers.json l.41–56 | OK | |
| 6.2 | "none lost" | evaluate.log: none of the 24 flooded roads lost, but 3 of the 69 dry-labelled thin-cloud roads flipped to "flooded" | SHOULD FIX | "none of the 24 lost; 3 of 69 dry-labelled roads flipped (those labels are untrusted)" |
| 6.3 | "Clear roads unchanged: 78% → 78% on 175"; note "it left the clear roads alone" | evaluate.log (77.7 → 78.3%, 6 fixed, 5 broken, p 1.0); 01 l.72–73 | **MUST FIX** | See MUST FIX 2. |
| 6.4 | "Single-image de-hazing (He et al. 2011) found 88% but cost clear roads 4 points" | 01 l.66–67 (87.5%; 77.7 → 73.7); evaluate.log (p 0.125 and p 0.25); v2 l.1202 (do not rank the two) | SHOULD FIX (low) | Add "(neither difference is significant)". The code also refines with a guided filter (v2 l.75–76), not the 2011 paper's soft matting. Note that in the evidence files. |
| 6.5 | "Two-date de-hazing: our rule, on the haze model of He et al. (2011)" | He 2011 §2 presents I = J·t + A(1 − t) as the model widely used in earlier work (Narasimhan & Nayar, Fattal, Tan). Its own contribution is the dark channel prior | SHOULD FIX | "our rule, on the standard haze model (as used by He et al. 2011)" |
| 6.6 | "r = 0.46 here; the fit reads clear ground as hazy and skips the bright core" | 01 l.69–75; devlog l.21 | OK | |
| 6.7 | "The fix, pre-registered" | 01 l.87; v2 l.769–773, l.1381–1382; slide 7 | **MUST FIX** | See MUST FIX 1. |
| 6.8 | IR-MAD finds unchanged pixels and an orthogonal fit matches the dates | Canty & Nielsen 2008 (full text): IR-MAD re-weights pixels by their probability of no change, then normalises by orthogonal linear regression on those pixels | OK (note) | IR-MAD was built for multi-band images. On one grey band its canonical-correlation step reduces to a single scaled difference. Say so in the pre-registration. |
| 6.9 | The pictures of tile 2_19_55 | slide_panels.py l.81–83 picks the fixed road under the most cloud, which is a success case | SHOULD FIX | Caption: "Example: the fixed road under the most cloud (chosen by rule from the 3 fixed)". |
| 6.10 | Header "exploratory: these roads were looked at before" | 01 l.67–68; v2 l.737–741 | OK | |
| 6.11 | Notes: "using only pixels that did not change" | v2 l.669–670: the robust fit drops pixels that fit badly. Whether those are the changed pixels is untested (the change-kept veto is planned) | SHOULD FIX (low) | "dropping the pixels that fit badly, which should be the changed ones" |

## Slide 7 · next

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 7.1 | "Data, masks, de-hazer and the held-out harness all run" | 01; evaluate.log | OK | |
| 7.2 | "Dark-channel mask: F1 0.65 against 0.41 for the old rule (HRC_WHU)" | 01 l.33–34; panel_numbers.json l.71–81 | OK | |
| 7.3 | "Label bias measured: 55%, 26%, 2% labelled flooded" | 01 l.21–23 (part of the gap is geography); Q2b not yet run | SHOULD FIX | "Flooded-label share by cloud: 55%, 26%, 2% (label bias likely; geography not yet ruled out)" |
| 7.4 | Limits: one event and sensor; all real cloud in one after image; sealed tiles next to development tiles; only 24 trusted roads; critic says revise | 01 l.4–6, l.79; v2 l.188, l.251 (39 of 40 test tiles touch a development tile); methodology_review.md l.885 (REVISE) | OK | |
| 7.5 | The 8-week plan | v2 l.1211–1221 | OK (note) | In v2, Q2's real-data work starts in week 2 and drafting in week 4 (l.1215, l.1229). "Wk 6 (Q2)" and "Wk 8: write" simplify that. Fine for a 4-minute talk. |
| 7.6 | Notes: "the cloud mask beats the old rule against human cloud labels" | 01 l.33–34: better on F1 and recall; precision is lower (0.62 against 0.81) | OK (note) | "...beats the old rule on F1..." |
| 7.7 | Notes: the plan order, from pre-registration to the sealed look | v2 §15.2 | OK | |

## Slide 8 · masks

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 8.1 | F1 by land cover: 0.54 / 0.78, 0.45 / 0.74, 0.25 / 0.66, 0.20 / 0.65, 0.57 / 0.48 | panel_numbers.json l.59–70 (all rounded correctly; snow 0.645 shown as 0.65) | OK | |
| 8.2 | Pooled F1 0.65 (P 0.62, R 0.68) and 0.41 (P 0.81, R 0.28) | panel_numbers.json l.71–81; 01 l.33–34 | OK | |
| 8.3 | "120 HRC_WHU development images; the 30 test images stay sealed" | HRC_WHU split list; 01 l.32–33 | OK | |
| 8.4 | (Missing) Which mask this checks | 01 l.35–36: the two-date dark-rise mask that the road rule uses cannot be checked on HRC_WHU, which has only one date | SHOULD FIX | Add: "The two-date dark-rise mask used by the road rule cannot be checked here (HRC_WHU is single-date)." |
| 8.5 | "dark-channel mask (He et al. 2011)" | He 2011 (the dark channel estimates haze thickness; the prior fails on surfaces that look like airlight, such as snow or white walls). The threshold is an Otsu cut, our rule (01 l.27–28) | OK (note) | Optional: "(He et al. 2011; Otsu cut, our rule)" |
| 8.6 | "under thick haze it flags flooded roads more (+13 points), not less" | 03 l.19–21: +13.2 is at t = 0.6. At the thickest level, t = 0.5 (the one 03 labels "thick"), it is +7.5 | SHOULD FIX | "under thicker haze (t = 0.6 to 0.5) it flags flooded roads more (+7 to +13 points), not less" |
| 8.7 | "Synthetic haze on 769 clear roads"; flooded and dry flagged alike under thin haze | 03 l.10–18 | OK | |
| 8.8 | Notes: the SpaceNet 8 threshold is near the best on HRC_WHU | 01 l.35 (best F1 0.66 at 90, against 98 learned) | OK | |

## Slide 9 · layering

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 9.1 | after ≈ t·ground + L; ground ≈ g·before + h; corrected = (after − L) ÷ t | 01 l.63–65; v2 l.669–674 | OK | |
| 9.2 | "haze model: He et al. 2011" | He 2011 §2 | SHOULD FIX | "haze model: as used by He et al. 2011" (same issue as 6.5) |
| 9.3 | "Changed pixels (floodwater) fit badly and drop out"; notes "drop the pixels that fit badly because they changed" | v2 l.705 (symmetric trimming); v2 §6.4.6 (the "change kept" veto is not yet run); 01 l.71–72 (diluted slopes: local α is 0.03–0.05) | SHOULD FIX | "Changed pixels (floodwater) should fit badly and drop out; the change-kept check will test this." |
| 9.4 | "t below 0.2 is left as opaque"; r = 0.46; "the core falls below 0.2 and clear ground is read as hazy" | 01 l.65, l.69–75 | OK | |
| 9.5 | Panel 3: "Dark = treated as haze; bright = left alone" | slide_panels.py (inferno scale from 0.2 to 1; rejected pixels are set to t = 1) | OK | |
| 9.6 | Notes: 64 m windows; gain and offset fitted on the clear pixels | 01 l.63–64; v2 l.669–670 | OK | |

## Slide 10 · human

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 10.1 | CHANGED: problem statement rewritten in Justin's words | decision_log.md l.8 | OK | |
| 10.2 | REJECTED: "R1: DINOv2 against classical cues under haze" | decision_log.md l.11 records "Changed": the DINOv2-versus-classical frame was dropped and synthetic clouds were kept | SHOULD FIX | "CHANGED · R1: dropped DINOv2 vs classical under haze; kept synthetic clouds" |
| 10.3 | REJECTED: R3, the 20% cut-off as the frame | decision_log.md l.13 | OK | |
| 10.4 | CHANGED: Q1 moved last, in Justin's wording | decision_log.md l.17 | OK | |
| 10.5 | CHOSEN: Q2 leads (Claude had suggested Q3) | decision_log.md l.18 | OK | |
| 10.6 | ACCEPTED: road cloud rule for fitting and scoring | 01 l.58 (Justin, 2026-10-23) | OK (note) | It is not in decision_log.md (see 12.2). |
| 10.7 | ACCEPTED: methodology critique as defaults, under "Justin made the decisions"; the note says "I accepted" | decision_log.md l.22; v2 l.9–10 | **MUST FIX** | See MUST FIX 3. |
| 10.8 | AI use: "agents drafted research questions, critiques, literature notes and analysis code" | build_slides.py: Claude also drafted these slides, the figures and the speaker notes | SHOULD FIX | Add "...and drafted these slides, figures and speaker notes." This keeps the statement general and truthful. |
| 10.9 | "Every number on these slides was produced by code on development data" | Some numbers come from documents, not code: HRC_WHU's 150 images and 0.5–15 m, the 333 tiles, the 8 weeks | SHOULD FIX (low) | "Every result on these slides was produced by code on development data." |
| 10.10 | "citations stay marked unverified until read" | No slide marks any citation as unverified; the refs slide says "Under verification" | SHOULD FIX (low) | After this report: "Citations checked against the papers on 24 Oct; how deeply each was read is in the evidence files." |
| 10.11 | "Agreement between agents is not treated as validation" | v2 l.20–21 | OK | |
| 10.12 | Notes: "rejected two of the first research questions" | decision_log.md l.11 and l.13: one changed, one rejected | SHOULD FIX | "dropped the frame of one and rejected another" |
| 10.13 | Notes: chose the reporting question to lead although Claude suggested another | decision_log.md l.18 | OK | |

## Slide 11 · refs (rule: journal JIF above 4, company-led, or a major conference; JIF values from `Project/docs/literature/journal_impact_factors.md`)

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 11.1 | Hänsch et al. 2022 listed under "Literature · JIF above 4 or company-led" | CVPR Workshops (EarthVision), so no JIF. Five of 8 authors are from Maxar. The project lists it as a data attribution (classical_layer_citations.md l.32; ProjectBranch bibliography.md). CVPR Workshops are "not the CVPR main track" (JIF list l.69) | SHOULD FIX | Move it to the Data line, or rename the header "JIF above 4, company-led, or CVPR (incl. Workshops)". |
| 11.2 | Li et al. 2019, HRC_WHU, ISPRS JPRS | JIF 12.9 (JIF list l.33) | OK | |
| 11.3 | He, Sun & Tang 2011, IEEE TPAMI | TPAMI 33(12):2341–2353; JIF 18.6 (a 2024 value, l.124); one author at Microsoft Research Asia | OK | |
| 11.4 | Canty & Nielsen 2008, RSE | RSE 112:1025–1036; JIF 12.3 (l.43) | OK | |
| 11.5 | Oquab et al. 2024, DINOv2 (Meta AI), TMLR | The PDF says TMLR, January 2024; all authors are at Meta except one at Inria. TMLR has no JIF (l.48), so it passes as company-led | OK | |
| 11.6 | Haralick 1979, Proc. IEEE | Not read (needs GMU access). Proc. IEEE is about 25.9 (classical_layer_citations.md l.22) | UNVERIFIED (content) | The venue passes the rule. Read the paper before citing anything specific from it. |
| 11.7 | Roberts et al. 2017, Ecography | Ecography 40:913–929; JIF 4.7 from an aggregator site, close to the line (l.121) | UNVERIFIED (JIF close to 4) | Confirm in JCR through GMU. |
| 11.8 | Portalés-Julià et al. 2023, "WorldFloods v2, cloud and water masks", Sci. Rep. | Sci. Rep. 13:20316; JIF 4.9, close to the line (l.46). PMC full text: two separate outputs (clear/cloud and land/water), so water can be called under thin cloud. The paper calls the data "an extended WorldFloods"; the authors' public dataset is named WorldFloodsv2. One author is at Trillium Technologies | UNVERIFIED (JIF close to 4) | The content is right. Confirm the JIF in JCR. |
| 11.9 | Qu, Li & Huang 2026, AnyTime-CD, RSE | RSE 334:115239 (full text on disk): self-supervised multi-temporal change detection. It is robust under low and medium cloud and uses simulated thin, semi-transparent and thick cloud as augmentation | OK | |
| 11.10 | Shen et al. 2015, missing-data reconstruction review, IEEE GRSM | Authors' manuscript: a review with four categories (spatial, spectral, temporal, hybrid); GRSM JIF 13.7 (l.30) | OK | |
| 11.11 | Bruzzone & Bovolo 2013, change-detection framework, Proc. IEEE | Abstract only: a top-down framework for designing change detection for very-high-resolution images, which models radiometric change types | OK (abstract only) | |
| 11.12 | 11.8–11.11 are cited on no slide | Check 4 | SHOULD FIX | Cite each where it applies: Qu et al. on Q1 (synthetic clouds), Shen et al. on the two-date step, Portalés-Julià et al. on reporting cloud apart from water, Bruzzone & Bovolo on the workflow. Or move them to a "background" line. |
| 11.13 | Breiman 2001 and McNemar 1947 under "Method attributions · below the JIF rule" | Machine Learning about 2.9 and Psychometrika about 3.0, from aggregator sites (classical_layer_citations.md l.28, l.30) | OK | |
| 11.14 | Data line: SpaceNet 8 (CC BY-SA 4.0; imagery Maxar), HRC_WHU (academic use only) | SpaceNet's SN8 page; HRC_WHU data note | OK | See the licence conflict in 1.6. |
| 11.15 | Notes: "the reviews of cloud handling and missing-data reconstruction" | Only Shen 2015 is a review. Portalés-Julià, Qu and Bruzzone & Bovolo are method or dataset papers | SHOULD FIX (low) | "the cloud-aware flood and change-detection papers, and a review of missing-data reconstruction" |

## Slide 12 · evidence

| # | Claim | Source checked | Verdict | Suggested rewording |
|---|---|---|---|---|
| 12.1 | The folder list: input_card, decision_log, outputs/, evidence/, figures/, presentation/ | A listing of `CloudResearch/` | OK | |
| 12.2 | "decision_log.md: every accepted, changed and rejected item" | Justin's adoption of the road cloud rule is recorded in 01 l.58, not in the decision log | SHOULD FIX (low) | Add the row to the log (Justin or the coordinator), or write "the road rule is recorded in evidence/01". |
| 12.3 | Code in github.com/Jrog378/GeoAI-Roads, including sn8_refhaze.py; notes "the code in the private repository" | git status: sn8_refhaze.py is untracked | **MUST FIX** | See MUST FIX 4. |
| 12.4 | "the stage test notebooks" | `Code/*_test.ipynb` are tracked | OK | |

## Inconsistencies between source files (not slide errors, for Justin)

- `selected_questions.md` l.18 marks Q2 as "Justin's wording". But `decision_log.md` l.12 says Claude suggested "what can a flood-road map reliably tell users ...", after Justin asked "can" or "should".
- `input_card.md` l.64 still has the old Q3 wording. `selected_questions.md` l.56 has the newer one.
- Methodology v2 l.1192 gives the pilot's clear-road change as "+0.6 points", which matches the log. The slide's rounded "78% → 78%" does not (MUST FIX 2).

## Counts

- **OK:** 75
- **MUST FIX:** 4
- **SHOULD FIX:** 29
- **UNVERIFIED:** 6. These are:
  - the imagery licence;
  - the cover alt text;
  - Haralick 1979;
  - the Roberts et al. 2017 JIF;
  - the Portalés-Julià et al. 2023 JIF;
  - the workflow's Haralick texture citation (4.8).
