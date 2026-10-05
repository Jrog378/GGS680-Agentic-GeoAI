# Candidate Research Questions — Drought and Inland Waterway Freight Resilience

**Agent:** Research Question Agent (`agents/research_question_agent.md`)
**Stage:** `problem` → `research_question`
**Packet:** `outputs/prompt_packets/01_research_question_agent.md`
**Date:** 2026-09-28

---

## 0. Inputs used

| Input | Status | Content available |
|---|---|---|
| `inputs/problem.md` | Present | Broad problem statement + 4 boundary conditions. **"Human notes" section is empty.** |
| `inputs/evidence/` | **Effectively empty** | Contains only `README.md` (a placeholder instruction, not evidence). No papers, datasets, or notes supplied. |
| Prior reviewer feedback | **Absent** | This is the first pass; no critic output exists in `outputs/`. |
| `AGENTS.md` | Present | Applied as binding constraint. |

### 0.1 Consequence for novelty claims

**No evidence corpus was supplied. Novelty is therefore not assessable for any candidate below,
and is recorded as `n/a` rather than scored.** Per AGENTS.md rule 9, no novelty, causal,
policy-relevance, or external-validity claim in this document is asserted as established; each is
flagged where a downstream agent would otherwise be tempted to assert one.

### 0.2 Evidence vs. inference in this document

- **Evidence:** only the text of `inputs/problem.md`. Nothing else in the repository constrains this artifact.
- **Inference / model background knowledge:** the domain framing, the named datasets, and the
  hydrologic and freight-system mechanisms cited below come from the model's background knowledge,
  **not** from supplied evidence. Every dataset named in §2 is listed in the
  **unverified-dataset register (§4)** and must be confirmed to exist, be accessible, and cover the
  required space–time domain before any of these questions is adopted. No citation is given because
  no paper was supplied, and inventing one is prohibited (rule 2).

---

## 1. Assumptions (explicit, revisable by the human supervisor)

| # | Assumption | Why stated | If wrong |
|---|---|---|---|
| A1 | **Study area:** the U.S. inland waterway system, primarily the Middle/Lower Mississippi with the Ohio and Illinois as comparison reaches. | `problem.md` names no study area. This choice maximizes public lock-throughput and gage coverage. | Q1–Q4 are portable in form but the data stack in §2 must be rebuilt; Q5 is unaffected in principle. |
| A2 | **Study period:** roughly 2000–present, at weekly or monthly resolution. | Needed so that more than one severe low-water episode falls inside the record. | Shorter records collapse the effective sample of extreme events and make Q2 and Q5 untestable. |
| A3 | "Drought" is operationalized as a **meteorological/hydrologic index** (e.g. SPI/SPEI, soil moisture, drought-monitor class), kept distinct from the **navigation-relevant hydraulic state** (river stage, controlling depth). | Conflating the two is the most likely silent error in this problem. | The entire causal chain in Q1–Q2 becomes unidentifiable. |
| A4 | The **operationally binding constraint is channel depth over controlling features**, of which gage stage is a proxy and satellite water extent a proxy-of-a-proxy. | Determines how far Q4 can actually go. | Q4's premise weakens substantially (see Q4 threat). |
| A5 | The unit of spatial analysis is the **river reach / lock-to-lock segment**, not the county or state. | Reduces (does not eliminate) MAUP and ecological-fallacy exposure. | Q1's breakpoint estimates become aggregation artifacts. |
| A6 | "Achievable with public or research-accessible data" permits datasets behind a research-access request, not only open downloads. | The boundary condition in `problem.md` is ambiguous on this point. | Q3 likely becomes infeasible (restricted-access freight microdata). |
| A7 | No causal claim is licensed without human approval; Q3 is framed as quasi-experimental but is **not** approved as causal. | AGENTS.md rule 9. | — |

---

## 2. Ranked candidate questions

Ranking criterion: expected scientific yield **per unit of tractability risk**, given that the
severe-event sample in any single basin is small. Q1 is ranked first because it is the only candidate
whose core claim can be tested on the ordinary hydrologic range rather than on a handful of extremes.

---

### Q1 — (Rank 1) Threshold, not slope: is the stage-throughput response piecewise, and is the breakpoint predictable from channel form?

**Research question.**
Does barge freight throughput respond to river stage as a **reach-specific threshold (breakpoint)
function** rather than a smooth monotone one, and can the breakpoint location be predicted from
observable channel and dredging characteristics of the reach?

**Candidate hypothesis.**
H1: For each reach there exists a stage threshold below which throughput declines sharply
(draft and tow-size restrictions bind), and a piecewise model fits out-of-sample better than a linear
or smooth-monotone model. H1b: Breakpoint stage, converted to depth, is ordered across reaches by the
reach's controlling depth and dredging frequency — shallower or less-maintained reaches break first.

**Expected observable evidence.**
- Segmented-regression breakpoints detected with confidence intervals excluding the endpoints of the observed stage range, in most reaches.
- Out-of-sample error of the piecewise model below that of the linear/smooth baseline.
- Positive rank correlation between estimated breakpoint depth and independently documented reach controlling depth.

**Plausible data** (all unverified — see §4).
USACE Lock Performance Monitoring System lockage and tonnage records; USGS NWIS stage and discharge;
NWS/AHPS low-water reference stages; USACE channel-condition and dredging records; AIS vessel tracks
(Marine Cadastre / USCG) as an independent movement measure.

**Plausible method.**
Reach-level segmented regression, in a hierarchical (multilevel) Bayesian formulation so reaches with
thin records borrow strength; breakpoint estimates then regressed on channel covariates, with
spatial-lag or spatial-error terms because adjacent reaches are not independent. GeoAI component:
a river-network graph learner predicting breakpoints for unmonitored reaches, evaluated against
reaches held out **whole**.

**Main threat to validity.**
Confounding by the agricultural calendar — harvest-season demand peaks and low-water season partly
coincide, so a fitted "threshold" may encode seasonality. Secondary threats: stage is not draft, and
the gage-to-controlling-feature offset varies; lockage counts measure lock use, not tonnage moved past
a shoal; MAUP in reach delineation; datum shifts and channel-bed change make a fixed stage threshold
non-stationary over a two-decade record.

**What would weaken or refute it.**
Piecewise models failing to beat the smooth baseline out of sample once seasonality and commodity
demand are controlled; breakpoint confidence intervals so wide as to be uninformative; breakpoint
depths showing no ordering with respect to controlling depth (refutes H1b while leaving H1 open).

**Validation strategy.** Blocked cross-validation by reach *and* by year; placebo test on reaches with
no documented draft restriction; AIS-derived throughput as an independent outcome measure.

---

### Q2 — (Rank 2) Does upstream basin drought state add forecast skill beyond the local gage, and does the skill pattern match hydrologic travel time?

**Research question.**
Can a spatio-temporal model over the river network, using **upstream and basin-wide drought
predictors**, forecast lock-level throughput anomalies at 2–8 week lead times with more skill than a
baseline using only local stage history — and does any skill gain increase with upstream contributing
area in the way hydrologic routing lag would imply?

**Candidate hypothesis.**
H2: Upstream drought state carries information about downstream navigability that local stage
persistence does not already contain, so skill gain grows with lead time up to roughly the basin's
routing lag, and is larger for reaches with larger upstream contributing area.

**Expected observable evidence.**
- Positive skill gain (MAE/CRPS) over persistence and local-AR baselines under leave-one-event-out evaluation.
- Skill gain rising then falling with lead time, peaking at a lag ordered by upstream area across reaches.

**Plausible data** (unverified — §4).
U.S. Drought Monitor classes; gridded meteorology and SPEI (gridMET-class products); modeled or
remotely sensed soil moisture (NLDAS-class reanalysis, SMAP); GRACE/GRACE-FO terrestrial water
storage; snowpack (SNOTEL) for the upper basin; USGS NWIS; LPMS throughput; HydroSHEDS/MERIT network
topology for upstream-area computation.

**Plausible method.**
Graph neural network or other spatio-temporal learner on the river-network graph, benchmarked against
persistence, local AR/ARIMA, and a non-spatial gradient-boosted model given identical features.
Evaluation by **blocked space-time cross-validation** and leave-one-event-out.

**Main threat to validity.**
**Effective sample size.** Skill in this problem is decided by a handful of severe low-water episodes;
with only three or four in the record, apparent skill is dominated by which episode landed in the test
fold, and conventional error bars will understate uncertainty. Compounding threats: spatial leakage
from nearby gages appearing in both folds; temporal autocorrelation inflating random-split skill;
GRACE's coarse footprint and latency; and upstream reservoir operations intervening between drought
signal and downstream stage, so the mechanism may be regulation policy rather than hydrology.

**What would weaken or refute it.**
No skill gain over the local baseline under leave-one-event-out; skill gain present in random splits
but vanishing under blocked splits (diagnoses leakage, not signal); a skill-versus-lead-time profile
unrelated to upstream area; gain disappearing once reservoir-release data are added as a control
(which reassigns the mechanism rather than refuting prediction).

**Validation strategy.** Pre-register the baseline set and the event folds before fitting; report skill
per event, not pooled only; ablate the spatial graph to confirm the spatial structure, not merely the
extra features, is doing the work.

---

### Q3 — (Rank 3) Is modal substitution during low water spatially rationed by intermodal access?

**Research question.**
During low-water episodes, does freight substitute from barge to rail and truck, and is the magnitude
of substitution constrained by an origin region's **network accessibility to intermodal terminal
capacity**?

**Candidate hypothesis.**
H3: Substitution is spatially uneven — origin regions with poorer multimodal access to rail loading
and intermodal capacity show larger transport-cost shocks and smaller volume reallocation than
comparably river-dependent regions with good access.

**Expected observable evidence.**
- Barge volume declines coinciding with rail volume increases in affected origin regions.
- Barge-rate spikes whose size is inversely related to an accessibility measure, holding river dependence fixed.

**Plausible data** (unverified — §4).
USDA AMS Grain Transportation Report (barge and rail rate series); USACE Waterborne Commerce
Statistics; AAR weekly rail traffic; STB Carload Waybill Sample (**restricted access — see A6**);
BTS / National Transportation Atlas intermodal facility locations; Freight Analysis Framework for
baseline flows.

**Plausible method.**
Event study / difference-in-differences comparing river-dependent origin regions against matched
non-river-dependent controls, interacted with a network-based accessibility index computed on a
multimodal graph.

**Main threat to validity.**
**This is a causal design and is not approved as causal (A7, rule 9).** Identification is threatened
by contemporaneous shocks hitting the same regions — fuel-price swings, rail service degradation,
export-demand shifts — any of which can mimic substitution. Further: accessibility is endogenous
(terminals were built where freight already moved); the Waybill Sample's aggregation and access rules
may prevent the needed spatial resolution; county- or region-level inference invites ecological fallacy
about firm-level behavior; and the Freight Analysis Framework is itself modeled, not observed, so using
it as an outcome would be circular.

**What would weaken or refute it.**
Substitution magnitude statistically indistinguishable across accessibility strata; pre-trends present
in the event study (which invalidates the design outright); the rail response explained away once
rail-side service metrics are controlled; effects appearing equally in control regions.

**Validation strategy.** Pre-trend and placebo-period tests; a falsification outcome that drought
should not move; sensitivity analysis on the accessibility specification; explicit human sign-off
before any causal or policy statement.

---

### Q4 — (Rank 4) Can satellite-observed river geometry stand in for gages where gages are sparse — and where does that substitution break?

**Research question.**
Can satellite-derived water-surface extent, width, and elevation predict navigability-relevant
hydraulic state in **gage-sparse reaches** accurately enough to support low-water monitoring, and does
the error scale with channel gradient, braiding, and bank vegetation?

**Candidate hypothesis.**
H4: In low-gradient, single-thread reaches, remotely sensed width and surface elevation reproduce
gage-derived low-water thresholds within an operationally useful tolerance; accuracy degrades
systematically with braiding index and channel slope.

**Expected observable evidence.**
- On **entirely held-out gages**, predicted stage or threshold class matching observations within a pre-declared tolerance.
- Residual magnitude ordered by morphologic covariates rather than randomly distributed.

**Plausible data** (unverified — §4).
Sentinel-1 SAR (GRD); Sentinel-2 and Landsat optical; SWOT river products for water-surface
elevation and slope; USGS NWIS as ground truth; MERIT Hydro / HydroSHEDS and channel-morphology
products for covariates.

**Plausible method.**
Water-extent segmentation (thresholding baseline, then a CNN), width extraction along centerline
cross-sections, and a width/elevation-to-stage regression; **spatial block cross-validation holding
out whole reaches**, never individual pixels or dates.

**Main threat to validity.**
**The conceptual gap in A4:** satellites observe the water *surface*; navigation is constrained by
*depth over the controlling bar*. A model can predict stage well and still say nothing about whether a
given draft clears. Also: revisit and cloud gaps at the timescale on which a low-water event evolves;
SAR ambiguity from vegetation, wind roughening, and bank shadow; severe spatial leakage risk if
"held-out" reaches sit adjacent to training reaches on the same hydrograph; and the fact that low
water is exactly the regime in which width-change signal is smallest in a confined channel.

**What would weaken or refute it.**
Held-out-reach error exceeding the navigability decision tolerance; no improvement over a
climatological or interpolated-gage baseline; error uncorrelated with morphology (refutes the scaling
claim); performance collapsing when leakage-safe blocking replaces random splits.

**Validation strategy.** Declare the tolerance **before** fitting, tied to a stated draft decision;
compare against an interpolated-gage baseline rather than against zero skill; report performance
separately for the low-water tail, since that is the only regime that matters here.

---

### Q5 — (Rank 5) Do drought-throughput response functions transfer between basins, and does transfer error scale with dissimilarity?

**Research question.**
Do drought-navigability-throughput relationships learned in one inland waterway system transfer to
another, and is transfer error predictable from a measurable **hydroclimatic and institutional
dissimilarity** between systems?

**Candidate hypothesis.**
H5: Transfer degrades monotonically in a dissimilarity index built from flow-regime statistics, degree
of channel regulation (lock and dam density, reservoir storage ratio), and fleet draft characteristics.

**Expected observable evidence.**
Leave-one-basin-out transfer error rank-correlated with the dissimilarity index across the available
systems.

**Plausible data** (unverified — §4).
U.S.: LPMS, NWIS. Rhine: German and Dutch federal waterway authority gage records (the Kaub gage is
the conventional navigation reference) and Rhine-commission market observation reporting.
Paraná–Paraguay: Argentine and Paraguayan waterway authority level and traffic records. Plus global
runoff and reservoir datasets for regime and regulation descriptors.

**Plausible method.**
Fit the Q1/Q2 response models per basin; evaluate cross-basin transfer; regress transfer error on the
dissimilarity index.

**Main threat to validity.**
**Statistical power is the fatal risk.** With a handful of comparable basins, the regression of
transfer error on dissimilarity has essentially no degrees of freedom, and any monotone pattern found
may be unfalsifiable narrative fitting. Additional threats: throughput is measured and reported
differently in each jurisdiction (lockages vs. tonnage vs. vessel counts), so "transfer error" may
partly measure reporting-convention mismatch; institutional response (dredging budgets, rate
regulation) is a hidden moderator; and this question concerns **external validity, which rule 9 places
behind human approval**.

**What would weaken or refute it.**
Transfer error uncorrelated with dissimilarity; within-basin temporal variation in error exceeding
between-basin variation (the index then explains nothing); harmonization of throughput definitions
erasing the apparent pattern.

**Validation strategy.** Treat as exploratory and descriptive; report the number of independent basins
as the sample size in every result; pre-specify the dissimilarity index before seeing transfer results.

---

## 3. Ranking summary

Scores are the agent's judgment on a 1–5 scale (5 = strongest), not measurements.
Novelty is `n/a` for all candidates because no evidence corpus was supplied (§0.1).

| Rank | Question | Importance | Novelty | Testability | Data feasibility | Spatial / GeoAI relevance | Tractability | Validation strategy |
|---|---|---|---|---|---|---|---|---|
| 1 | Q1 Threshold response and predictable breakpoints | 4 | n/a | 5 | 4 | 4 | 5 | 5 |
| 2 | Q2 Upstream drought forecast skill | 5 | n/a | 4 | 4 | 5 | 3 | 4 |
| 3 | Q3 Spatially rationed modal substitution | 5 | n/a | 3 | 2 | 4 | 2 | 3 |
| 4 | Q4 Satellite proxy in gage-sparse reaches | 3 | n/a | 4 | 4 | 5 | 3 | 4 |
| 5 | Q5 Cross-basin transferability | 4 | n/a | 2 | 2 | 4 | 1 | 2 |

**Why Q1 leads.** It is the only candidate identifiable from the ordinary hydrologic range rather than
from a few extreme episodes, so its power does not depend on the small-N problem that limits Q2, Q3,
and Q5. It also yields a reusable quantity — a reach-level breakpoint — that both Q2 and Q4 can
consume as a target or label.

**Note on Q1 + Q2 as a pair.** Q1 supplies the outcome definition that Q2 would forecast. If the human
supervisor wants one line of work rather than five, Q1 then Q2 is the coherent sequence.

---

## 4. Unverified-dataset register

Every dataset named in §2 is asserted from model background knowledge, **not** from supplied evidence.
Before any question is adopted, each must be checked for: existence under the stated name; access
terms; spatial coverage of the study reaches; temporal coverage of A2; and native resolution versus
the intended analysis resolution. The known-risky entries:

| Dataset | Specific risk to confirm |
|---|---|
| STB Carload Waybill Sample | Access restrictions and spatial aggregation may defeat Q3 entirely. |
| GRACE / GRACE-FO | Footprint likely too coarse for reach-scale attribution; latency may break the operational framing in Q2. |
| SWOT river products | Record length may be far shorter than A2 requires. |
| USACE dredging / channel-condition records | May not exist in consistent digital form across A2's period. |
| AIS (Marine Cadastre / USCG) | Inland-reach coverage, and barge-versus-tow identification, are both uncertain. |
| Freight Analysis Framework | Modeled, not observed — must not be used as an outcome variable. |
| Non-U.S. gage and traffic records (Q5) | Availability, language, and licensing all unverified. |

---

## 5. Unresolved issues

1. **No evidence corpus.** Novelty is unassessable; any of these questions may already be settled in the literature. This is the single largest gap in this artifact.
2. **No human notes.** Study area (A1), period (A2), and accessibility scope (A6) are agent choices, not supervisor decisions.
3. **Drought-definition ambiguity.** `problem.md` says "drought" without specifying meteorological, hydrologic, or operational. A3 picks a convention; the supervisor should ratify it, because Q1 and Q2 are different studies under different conventions.
4. **Outcome-variable ambiguity.** Lockages, tonnage, vessel transits, and freight rates are distinct outcomes with distinct sources and distinct threats. No candidate can be finalized until one is designated primary.
5. **Small-N of extreme events.** This constrains Q2, Q3, and Q5 more than any modeling choice does. It should be quantified — count the qualifying episodes in the record — before committing to any of them.
6. **Depth versus surface (A4).** Unresolved for Q4, and it may be a reason to demote Q4 rather than a detail to handle later.
7. **Spatial-leakage discipline.** Q2 and Q4 will produce optimistic results under random splits. A leakage-safe evaluation protocol must be fixed before modeling, not after.
8. **Non-stationarity.** Channel-bed change, datum revisions, fleet composition change, and lock rehabilitation all mean a two-decade record is not a sample from one stable system. No candidate currently addresses this.
9. **No agreement-based validation.** Per rule 4, if the Scientific Critic agent endorses this ranking, that endorsement is **not** evidence. Confirmation must come from the literature or from data.

---

## 6. Suggested next scientific action

**Primary:** route this document to the **Scientific Critic** (`agents/scientific_critic.md`, packet
`02_scientific_critic.md`), with the explicit instruction to attack the *evidence basis* rather than
the prose (rule 8) — specifically the §4 register and issues 3, 4, and 5.

**Blocking prerequisites the human supervisor should resolve first** (decisions the agent should not
make silently):

1. Ratify or replace **A1 (study area)** and **A3 (drought definition)**.
2. Designate the **primary outcome variable** (issue 4).
3. Populate `inputs/evidence/` with at least a minimal literature set, so that novelty becomes assessable and §0.1 can be retired.

**Cheapest decisive test before any modeling** — a feasibility probe, not an analysis: pull the stage
record for two or three reaches and count how many distinct severe low-water episodes actually fall
inside A2's window. If that count is very small, Q2, Q3, and Q5 should be demoted on power grounds
regardless of how strong they look on paper, and Q1 becomes the only defensible starting point.

**Not authorized at this stage** (rule 9): any claim of novelty, causal effect, policy relevance, or
external validity drawn from this document.
