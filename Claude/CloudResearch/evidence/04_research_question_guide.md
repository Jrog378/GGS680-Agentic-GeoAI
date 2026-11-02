# Style guide: writing research questions for the cloud proposal

Claude wrote this for Justin Rogers (GGS 662) on 2026-10-23, to learn how outside papers ask research questions. It took about 28 searches and page reads, on open pages only, with no logins and no PDFs saved.

- **Tags.** **Source:** what a source says. **My read:** my inference, not taken from any source.
- **Read depth.**
  - *Abstract.*
  - *Aims searched:* I searched the full text (PubMed Central XML or arXiv HTML) for aim, question and hypothesis sentences, and read only those passages.
  - *Page summary:* a whole web page, read through a fetch summary.
  - *Project notes:* an earlier Claude read in `ProjectBranch/Literature/notes/clouds.md`. Not re-read.
- **JIF.** From `Project/docs/literature/journal_impact_factors.md`. Where a journal is not listed: "confirm in JCR".

---

## 1. Frameworks

### 1.1 FINER

**Source** (Farrugia et al. 2010, *Can J Surg* 53(4):278–281, PMC2912019, confirm in JCR; page summary). FINER is credited there to Hulley et al., *Designing Clinical Research*. I did not read the book.
- **Feasible:** enough subjects, skill, time and money; a manageable scope.
- **Interesting:** to the investigator, to peers and to the community.
- **Novel:** it confirms, refutes or extends earlier findings.
- **Ethical:** a study a review board would approve.
- **Relevant:** to knowledge, to policy and to future research.

**My read (transfer).**
- **Feasible** means our 8 weeks, our compute (DINOv2 takes about 14 s a tile) and our power.
- **Novel** includes "confirms or refutes", so a realism check counts with no novelty claimed.
- **Ethical** means our data rules: licences, sealed data, published labels only.

### 1.2 PICOT and PECO

**Source (Farrugia et al. 2010).**
- **PICOT** stands for population, intervention, comparison, outcome and time (the follow-up period).
- A question comes from a gap in knowledge. The hypothesis is built from it and names the sample, intervention, comparison and outcome. The objective says actively how the study will answer the question.
- Use one primary question. Set secondary questions at the start, and never let them weaken the primary.
- State hypotheses before the study. Make them two-sided unless there is good reason not to.
- Questions built backwards from data already collected invite false positives from multiple testing.

**Source** (Morgan et al. 2018, *Environ Int* 121:1027–1031, https://doi.org/10.1016/j.envint.2018.07.015, confirm in JCR; page summary).
- **PECO** swaps "intervention" for "exposure". It is for exposures nobody assigns on purpose. There, the exposure and the comparator are the hard parts.
- Five ways to set the comparator:
  1. graded steps of exposure;
  2. cut-offs taken from the data, fixed in a protocol in advance;
  3. an outside reference level;
  4. an established threshold;
  5. a level an intervention could realistically reach.
- State the comparator explicitly. Say in advance what size of change counts as harm.

**Not read.** The CEE guidelines (HTTP 403). An EcoEvoRxiv preprint, which a search summary says allows only P and O for correlational studies.

**My read (transfer).**
- **Cloud is an exposure, not an intervention.** Our methods are the interventions: the generator and the after-only call. The shape: under exposure E, does intervention I beat comparator C on outcome O?
- **Morgan's options match our designs.** The thickness grid is option 1. The real thin-cloud level is option 3. The 20% rule is option 4, which Justin ruled out.
- **P** becomes unit and scope. **T** becomes which date is clouded and which split is scored. **O** must name its truth: published labels or synthetic truth.

### 1.3 From gap to question to hypothesis

- **Source** (Alvesson & Sandberg 2011, *Academy of Management Review* 36(2):247–271, https://doi.org/10.5465/amr.2009.0188, confirm in JCR; abstract).
  - Most research questions come from spotting gaps.
  - Questions that challenge the literature's assumptions ("problematization") are more likely to lead to influential work.
- **Source** (Elsevier Author Services; search summary only, as the page returned 404).
  - Phrases such as "has not been studied" signal a gap.
  - Hypotheses can take if/then forms, and testability comes first.
- **Source** (NeurIPS 2026 Paper Checklist; page summary).
  - Claims in the abstract and introduction must match the scope of the results.
  - Limitations get their own section.
  - Main claims need error bars or tests that say what variability they capture.
- **Source** (Mensh & Kording 2017, *PLoS Comput Biol* 13(9):e1005619, confirm in JCR; abstract). Build the paper around its main idea.

**My read.** Q2 and Q1 already problematize two project assumptions: that a missing label means dry, and that synthetic cloud is a valid test. The NeurIPS claims rule is our best single guard: words such as "reliably", "represent" and "any hazard" must not claim more than the test shows.

---

## 2. Examples

Key: T target, C condition, Cmp comparator, O outcome, S scope.

| # | Paper (venue, JIF) | DOI | Stated aim (paraphrased) | T / C / Cmp / O / S | Good / weak | Depth |
|---|---|---|---|---|---|---|
| 1 | Portalés-Julià et al. 2023, *Sci Rep* 13:20316 (4.9) | 10.1038/s41598-023-47595-7 | Fix three limits of flood mapping (cloud, accuracy, generalisation) with one system. Separate cloud and water masks find water under thin cloud | C thin vs thick cloud. Cmp spectral-index thresholds. O accuracy on 11 hand-labelled events | **Good:** condition and comparator named; visibility is its own output. **Weak:** three problems in one aim | Aims searched |
| 2 | Mateo-Garcia et al. 2021, *Sci Rep* 11:7249 (4.9) | 10.1038/s41598-021-86650-z | Investigate how cheap CubeSats with on-board machine learning could serve flood response | Cmp linear models; per-image optimal NDWI threshold. O accuracy; chip runtime. S 119 events | **Good:** a best-case comparator. **Weak:** "investigate how … could" is open-ended | Aims searched |
| 3 | Skakun et al. 2022, *RSE* 274:112990 (12.3) | 10.1016/j.rse.2022.112990 | Compare 10 cloud masks for Landsat 8 and Sentinel-2 against several reference datasets | C thick vs thin. Cmp each other. S 10–30 m | **Good:** the reference data changed the ranking, so name the truth. **Weak:** descriptive; no hypothesis | Abstract |
| 4 | Mateo-García et al. 2020, *ISPRS JPRS* 160:1–17 (12.9) | 10.1016/j.isprsjprs.2019.11.024 | Can cloud models trained on one sensor's labels work on another? Three directions | Cmp each sensor's operational mask (FMask on Biome). O accuracy | **Good:** each sub-question has a comparator and a number. **Weak:** no margin in advance | Abstract |
| 5 | Zou et al. 2025, *IEEE TGRS* 63 (9.4) | 10.1109/TGRS.2025.3597410 | Adapt a frozen foundation model, training few parameters, for more accurate and robust cloud masks | O mIoU; 0.6% of parameters trained. S 4 datasets | **Good:** outcome and cost measured. **Weak:** the project notes record no cross-dataset test, so "robust" outruns it | Aims searched + project notes |
| 6 | Francis 2024, *IEEE TGRS* 62 (9.4) | 10.1109/TGRS.2024.3391625 | Loosen models' tie to sensors and label schemes. Case: cloud and shadow masks learned from 8 datasets labelled differently | C partial or mismatched labels; many band sets | **Good:** names the limit loosened. **Weak:** the abstract gives no comparator or metric | Abstract |
| 7 | Qu, Li & Huang 2026, *RSE* 334:115239 (12.3) | 10.1016/j.rse.2026.115239 | Self-supervised change detection on time series of any length. One analysis adds simulated thin to thick cloud | C added cloud share and type. Cmp no added cloud. O F1 | **Good:** cloud as a graded dose. **Weak:** the notes record no check against real cloud | Project notes (PDF pp. 1–5, 16–17) |
| 8 | Burgert, Ravanbakhsh & Demir 2022, *IEEE TGRS* 60 (9.4) | 10.1109/TGRS.2022.3226371 | How do missing, extra and mixed label noise affect classification? Also adapts 3 robust methods, injects realistic synthetic noise, and tests metrics | C noise type and rate. Cmp uniform injection | **Good:** synthetic noise is justified against a cruder control. **Weak:** four aims; the outcome is "guidelines" | Abstract |
| 9 | Kondylatos et al. 2025, *Sci Rep* 15:35890 (4.9) | 10.1038/s41598-025-19781-2 | Model label noise with probabilistic machine learning on 4 tasks, and test whether its uncertainty is reliable | Cmp deterministic models. O accuracy; a Discard Test: drop the least-sure cases in steps, and error should fall | **Good:** uncertainty gets a pass/fail rule, which is an abstention test. **Weak:** "take a step in this direction" is vague | Aims searched |
| 10 | Singh et al. 2024, *Sci Rep* 14:16166 (4.9) | 10.1038/s41598-024-65954-w | Review how Earth-observation datasets report uncertainty; build conformal-prediction tools | O share of datasets with uncertainty information (22.5%) | **Good:** a countable outcome. **Weak:** "show versatility" is not a test | Aims searched + abstract |
| 11 | Toker et al. 2022, *CVPR* (conference) | 10.1109/CVPR52688.2022.02048 | Daily imagery with monthly change labels; two baseline families; a new metric (SCS) | Cmp semi-supervised vs spatio-temporal | **Good:** defines a metric where none fits. **Weak:** a dataset paper with no question | Abstract |
| 12 | Bountos et al. 2024, *NeurIPS* (conference; D&B track unconfirmed) | 10.52202/079017-1204 | A hand-labelled SAR flood dataset (43 events) and benchmark | C series length × elevation input. O F1 | **Good:** a clean factor design. **Weak:** "we hypothesize" comes after the result | Aims searched |
| 13 | Winiwarter et al. 2021, *RSE* 112772 (12.3) | 10.1016/j.rse.2021.112772 | An open laser-scanning simulator. Simulated data needs a use it is fit for | O runtime and memory | **Good for Q1:** realism is judged per use, "specific to the given research question". **Weak:** realism is not tested | Abstract |

---

## 3. Patterns and pitfalls

**Source** (the examples). All 13 state aims or contribution lists, not research questions. A search of the four target journals' abstracts for "research questions" found only off-topic papers. One, an RSE 2024 forest-floor study (10.1016/j.rse.2024.114486; abstract), splits an exploratory question from a predictive one.

**My read.** In remote-sensing method papers the question is usually implicit, but good ones still name the comparator, condition and metric. The course wants an explicit question, so we borrow FINER and PICO/PECO.

**Shapes.** Examples are in brackets; the templates are my wording.
1. **Comparison:** does X beat Z on M under C? [1, 4]
2. **Dose and response:** how does M change as C grows? [7, 8]
3. **Intercomparison:** how do A to N rank, and does the reference change the ranking? [3]
4. **Fit for use:** is simulation S good enough for use U, within a margin set first? [8, 13]
5. **Reliable uncertainty:** does error fall as the least-sure cases are dropped? [9]
6. **"To what extent …?":** use this when the answer is a size with an interval.

**Pitfalls.**
- **Vague verbs:** "investigate", "explore", "take a step" [2, 9]. They name an activity, not an answer.
- **"How should …?"** cannot be tested. Justin already swapped "should" for "can".
- **Bundling:** several aims in one [1, 8]. **Source (Farrugia):** use one primary question.
- **Claim words wider than the test:** "robust" [5], "global", "reliably". **Source (NeurIPS):** claims must match the results.
- **Questions or hypotheses made after the data** [12; Farrugia's warning].
- **No named truth:** the ranking moves with the reference data [3].
- **A missing or weak comparator:** a strong one, like the best-case NDWI threshold in [2], makes a win mean more.
- **My read:** "Can X …?" is answered yes by any single success. "Does X … better than Z?" sets a rule for winning, so it is easier to test.

---

## 4. Checklist

1. One primary question in one short sentence. Secondary questions go below it, fixed before any scoring.
2. Name the target and the scope: unit, sensor, place and event.
3. Name the condition (the exposure) and how its levels are set.
4. Name the comparator.
5. Name one outcome and the truth that scores it: published labels or synthetic truth.
6. Say what result means "no": a margin or an interval, fixed in advance.
7. Keep claim words ("reliably", "robust", "any hazard") no wider than the test.
8. Pass FINER: doable in 8 weeks; confirms, refutes or extends something; allowed by the licences and the sealed-data rules; useful to the people who use flood maps.

---

## 5. Our Q1–Q3, graded

All of this section is **My read**. It grades the current wordings:
- **Q1:** Justin's own, from the decision log (Refinement 3, 2026-10-23). It moves Q1 to the back, and v3 does not hold it yet.
- **Q2:** unchanged in v3.
- **Q3:** from `outputs/research_questions_refined_v3.md`.

In v2, Q1 and Q3 were tied to roads. v3 fixes that.

| Item | Q1. Can we use synthetic clouds to represent real-life blockages in satellite imagery? | Q2. What can a flood-road map reliably tell users about roads hidden by cloud? | Q3. When only the before image is cloudy, can the after image alone still show what changed? |
|---|---|---|---|
| 1. One question | **Partly.** v3's body holds two: H1a, realism; H1b, errors leaning to "no change" | **Partly.** H2a and H2b are separate questions | **Yes.** H3b and H3c are labelled secondaries |
| 2. Scope | **Partly.** "Satellite imagery", with no unit | **Yes** | **Yes.** Any target; roads and buildings are the test cases |
| 3. Condition | **Yes** | **Yes** | **Yes** |
| 4. Comparator | **Partly.** "Real-life blockages" is implied | **Partly.** The usual one-number report is in the body only | **No.** The two-date model is in the body only |
| 5. Outcome | **No.** "Represent" is unmeasured until the body | **Partly.** "Reliably" becomes a fixed error ceiling in the body | **Partly.** "Show what changed" becomes balanced accuracy in the body |
| 6. "No" result | **Yes.** Margins, and a control that must fail | **Yes.** Rows fail one by one | **Yes.** Stop and refutation rules |
| 7. Claim width | **No.** The tests cover 0.5 m greyscale and HRC_WHU; the sentence says all satellite imagery | **Partly.** "Users" and "reliably" are wide | **Partly.** By H3b, an after-only call reads the after state, not the change |
| 8. FINER | Feasible: medium. Novel: extends, not searched. Ethical: pending (HRC_WHU licence; the synthetic-truth ruling). Relevant: high | Feasible: high. Novel: small. Ethical: fine. Relevant: high | Feasible: high for roads. Novel: not searched. Ethical: fine. Relevant: medium to high |

**Suggested wordings** (My read). Each is a one-sentence label; the margins and data stay in each question's body.

- **Q1:** Justin chose this wording after rejecting a sharpened "match real cloud" version, so it stands, as Q2 does. If he wants an option that keeps his "blockages" idea and adds a comparator: *Do synthetic clouds block satellite images the way real clouds do?*
- **Q2:** Justin's own wording, which he kept. A tighter option: *Which things can a flood map say about cloud-hidden roads within an error limit set first?*
- **Q3:** *When only the before image is cloudy, does the after image alone find change better than both images together?*
  - This names the comparator, and "better" maps to balanced accuracy.

---

## Sources (web pages read)

- Pages: https://pmc.ncbi.nlm.nih.gov/articles/PMC2912019/ (Farrugia), https://pmc.ncbi.nlm.nih.gov/articles/PMC6908441/ (Morgan), https://neurips.cc/public/guides/PaperChecklist, and https://scientific-publishing.webshop.elsevier.com/research-process/what-is-research-gap/ (search summary only).
- Metadata and abstracts: OpenAlex and Semantic Scholar.
- Full text searched: PubMed Central PMC10661555, PMC8012608, PMC12521547 and PMC11246475; arXiv HTML 2311.12056v3 and 2411.13127v2.
- Not read: the CEE guidelines (HTTP 403); the Hulley et al. book.
