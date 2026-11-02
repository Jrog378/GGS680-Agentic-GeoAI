# Methodology v2: detecting, handling and reporting cloud in post-disaster change maps

Stage 4 of the Assignment 3 workflow, **revision pass** (Methodology Agent). Claude wrote this on 2026-10-24, working
alone from local files, with no sub-agents and no web search. It revises `methodology_v1.md` after the methodology
critic's review (`methodology_review.md`: verdict REVISE, 27 issues, 8 ranked changes). v1 is kept unchanged as the
audit trail (AGENTS.md rule 10).

- **Question order:** Q2 leads, then Q3, then Q1 (`selected_questions.md`; Justin, 2026-10-23).
- **The critic's changes:** Claude accepted them as defaults at the outline stage (`decision_log.md`, last row; Justin:
  "we are just creating the outline so I can change it later"). Justin may overrule any of them. Section 21 says where
  each one landed, and why any was changed or only partly taken.
- **This is a plan.** It holds one new result: the two-date de-hazing pilot, relayed by the coordinator on 2026-10-24.
  That result is **exploratory** (§6.4.5). Every other number comes from the evidence files, the earlier outputs, or a
  file I checked read-only today (§0). All of it is development data. No sealed data was read.

Tags:
- **Evidence:** a number or statement found in a file, or in the coordinator's pilot table. The source is named.
- **Inference:** my reasoning. It has not been measured.

Every agent in this workflow runs on the same model. Where this plan agrees with a critic, that is not independent
validation (AGENTS.md rule 4).

### At a glance: what changed from v1

1. **S1 is now the map's own rule** (tile rule + road rule). Its real-cloud test scores the bright tile rule on HRC_WHU
   patches. If S1 fails, Q2 has a pre-set answer (§6.1).
2. **Q1 has one primary test:** is family X closer to real cloud than the crude control? A label-free use-level check
   sits beside it. If realism fails, Q2's S2 and S3 drop to "range only" (§6.3, §6.1).
3. **The sampling frame is honest about dependence:** one after-image acquisition, cloud patches, spatial-block
   intervals, blocked folds in the same week as each result, and decision rules for the sealed look (§3).
4. **S2 and S3 are pinned down:** one scored set, recall and specificity beside them, and non-inferiority against clear
   sky within δ = 5 points. "Fails" is kept apart from "not shown" (§6.1, §8).
5. **§6.4 freezes the de-hazing code as it ran,** states every difference from v1's plan, adds a "change kept" veto,
   and makes "as reliable as clear sky" its primary outcome (§6.4.3–6.4.6).
6. **Justin's second idea is placed** as a two-pass design inside §6.4. Filled-in pixels never vote (§2.1, §6.4.2).
7. **A proposed definition of change** (§2.1). Justin has not ruled on it.
8. **The plan starts with Assignment 4:** slides due Sun 25 Oct, then a 4-minute pilot talk on Fri 30 Oct. See the box
   "What the Assignment 4 pilot shows" (§15.1).

---

## 0. Inputs used

- **Rules and role:** `05_Project/AGENTS.md`; `05_Project/agents/methodology_agent.md`.
- **Problem and decisions:** `CloudResearch/input_card.md`; `CloudResearch/decision_log.md` (its last row lists the
  critique changes accepted as defaults).
- **Questions:** `outputs/selected_questions.md`.
- **Under revision:** `outputs/methodology_v1.md`. **The critique:** `outputs/methodology_review.md`.
- **Evidence:** `evidence/01` to `05`, all read in full. File 05 covers filling in blocked imagery and two-pass designs.
- **New result:** the coordinator's pilot table for two-date de-hazing (task brief, 2026-10-24). **It is not yet in an
  evidence file.** It is cited as "pilot (coordinator, 2026-10-24)".
- **Checked read-only today.** No imagery, labels or outcomes read. Nothing run that scores anything.
  - `ProjectBranch/ClaudeFunctions/sn8_refhaze.py`, the prototype, read in full. SHA-256 begins `ff5a09bbf03aca62`.
    File time 2026-10-23 20:20.
  - The functions it imports from `sn8_clouds.py` (`dark_channel`, `cloud_thresholds`, `dehaze`, `_tile`) and their
    constants. `sn8_clouds.py` SHA-256 begins `6b64958daaae77e8`.
  - The module's cache folder (`ClaudeFunctions/.cache`): file names, times, and the row and tile counts of the
    corrected-feature tables. No feature values were looked at.
  - The RGB-to-grey weights in `sn8_grey.py` and `sn8_cloudref.py`.
  - A text search of `ProjectBranch/` and `Project/` for "refhaze" and "reference_dehaze".

**Evidence from these checks:**
- **Two two-date runs exist.** The cache holds two tables `road_corrected_refhaze_*.csv`, built on 2026-10-23 at 20:12
  and at 22:40. Each holds 268 roads on 39 tiles, in areas 0 and 2. The He arm also has two tables (20:04 and 20:28),
  with the same 268 roads on 39 tiles.
- **Inference:** 268 = 93 thin-cloud roads + 175 other roads, the pilot's three rows. The 39 tiles are the 39
  thin-cloud tiles (evidence 01). The cache key holds a hash of the fitting code, and the file was last edited at 20:20,
  between the two runs. So the 22:40 table is most likely the run after the fix. The coordinator reports that the
  numbers did not change.
- **The pilot's scoring script is not in the repository.** The text search found only the module itself and two
  review files. The code that turned these tables into the pilot's numbers (fold models, McNemar tests) must live in
  the coordinating session.
- **Greyscale:** SpaceNet 8 and HRC_WHU are both converted with 0.299 R + 0.587 G + 0.114 B (BT.601). This answers the
  critic's M27 point.
- **He de-hazing** (`sn8_clouds.dehaze`) uses one air light per tile, ω = 0.95, t₀ = 0.1 and a guided filter of
  radius 60 pixels.
- **Evidence 01's He result and the pilot's He result are different measurements.** Evidence 01's He row came from
  `dehazed_road_rows`, which recomputes classical and texture cues but no DINOv2 cues (code read). The pilot's He arm
  goes through `corrected_rows`, which recomputes all cues, DINOv2 included.
- The loaders refuse held-out tiles unless `allow_held_out=True` is passed (`_tile` and the others).

## 1. Assumptions

- **Time.**
  - Week 0 is today and tomorrow (Sat 24 – Sun 25 Oct). Assignment 4's slides are due Sunday 25 October.
  - Week 1 starts Monday 26 October. The 4-minute pilot presentation is Friday 30 October, in week 1.
  - Submission is Friday 18 December. US Thanksgiving (26 November) falls in week 5.
- **The model.** One frozen flood model: production as recorded in `production.json` on 2026-10-23. It is a random
  forest on classical, texture and DINOv2 change cues, with the tile rule + road rule cloud gate. **Evidence (01):**
  83.0% on 798 assessable roads; always "flooded" scores 55.3%. No promotions happen while the paper is being scored.
- **Labels.** Published SpaceNet 8 labels, unmodified. A "flooded" label is trusted anywhere. A missing label means
  "dry" only on clear roads, and even that is an assumption (§6.1 step 7).
- **Synthetic truth.** Scoring a mask against where we placed a synthetic cloud. **Justin has not ruled.** Both
  branches are pre-registered (§16).
  - Using the placement to choose which roads are clouded is the experiment's design, not a label. Scoring a mask
    against the placement is what needs the ruling.
- **HRC_WHU** outlines and cloud pixels for the generator. **Justin has not ruled.** Fallbacks are in §6.3 step 1.
- **The definition of change** in §2.1 is proposed. **Justin has not ruled.**
- **Rules are fixed before scoring.** The values in §8 are proposals. They are frozen in the pre-registration at the
  end of week 1 (Sun 1 Nov), after Gate 0. After that they never move.

---

## 2. The design on one page

### 2.1 Proposed definition of change (Justin has not ruled)

**The definition.**
- **Change means change on the ground** between the two dates. Water on a road is change. A damaged roof is change.
- **A cloud is not change. It is a blockage** between the sensor and the ground.
- A blockage is handled in one of two ways:
  - **see through it** where it is thin: correct the cloudy date with the clear reference date (§6.4), then call the
    object;
  - or report **"cannot assess"**.
- So every object gets one of three answers: **changed**, **not changed**, or **cannot assess**.

**Provenance: where each pixel's value comes from.** This is design 2 of evidence 05 §6.

| Class | Meaning | May vote in a change call? |
|---|---|---|
| Observed | No cloud flagged | Yes |
| Corrected | Cloud flagged, and the two-date haze rule accepted it (0.2 ≤ t̂ ≤ 1 and L̂ ≥ 0). Its fit residual is kept | Yes |
| Filled | A value supplied from somewhere else: another date, a neighbour, a generator | **No. It counts as "not observed"** |
| Not observed | Cloud flagged and not corrected (too thick, or the fit refused it) | No |

- **Rule, fixed now.** A filled pixel is never scored, never used as a cue, and never shown as observed. Filled images
  may appear in figures only, labelled "filled, not observed".
  - **Why (evidence 05 §6):** filling from the before date "paints the dry road back", so a flooded road becomes "no
    change". Single-image generators invent texture (Sui et al. 2024, unverified). No source was found that scores
    change through reconstructed pixels (05 §3).
  - **One exception, as a control:** the fill-from-before arm in §6.4.6 exists to show that filling erases floods and
    that the "change kept" veto catches it. It is reported only as a control. It never feeds a map.
- **A road is callable on the map** when less than 20% of its strip is "not observed". This reuses the road rule's
  existing 20% cut.

**What follows for each question (inference).**
- **Q2.** "Cannot assess" is statement S1. A road left unlabelled because it was hidden is "cannot assess", not "dry".
  This matches SpaceNet 8's rule to "only attribute what was visible" (Hänsch et al. 2022, evidence 01, unverified).
- **Q3.** Cloud on the before image blocks the reference. An after-only call reads the after state, not change. It is
  labelled a "state call". H3b measures where state and change part: water that was there before the storm.
- **Q1.** Synthetic cloud is a synthetic blockage. Justin's wording ("represent real-life blockages") already fits.
- **§6.4.** The change detector also responds to cloud. Under this definition that response is a nuisance. Pass 1 uses
  it to find the cloud. It is never reported as change.

**If Justin rejects it.** If change means "any change in the image", cloud becomes a change class the map reports.
Q2 would then need a "cloud appeared" statement, and §6.4's correction would become optional. The tests themselves
would not change.

### 2.2 The arc

Justin's three verbs (`input_card.md`):
- **Detect.** Tested in S1 (Q2) and in Q1's check 2. Q1 itself builds and checks the synthetic test bed (critic M25).
- **Handle.**
  - **Q3:** when only the before image is cloudy, map from the after image alone.
  - **§6.4:** when the after image is thinly clouded, see through it with the clear before date. This is Justin's
    two-pass design: find the cloud, correct ("scale") the image, run the change detector again.
- **Report (Q2, the lead).** What a map can say about hidden roads, in tiers, with limits fixed in advance.

### 2.3 How the parts depend on each other

- Q2's real-data parts need nothing new. They start in week 2, after the pre-registration.
- Q2's synthetic tier needs Q1's bed **and Q1's verdict.** A failed realism test drops S2 and S3 to "range only".
- Q3's clouded before images need Q1's frozen generator. Q3's clean gap and after-only score need nothing from Q1.
- §6.4's formal test needs the bed. Its pilot already exists (§6.4.5).
- **Build order:** rulings and Gate 0 (week 1) → Q2's real parts and the generator (week 2) → realism (week 3) → the
  bed, Q2's synthetic tier and §6.4 (week 4) → Q3 (week 5) → assembly and freeze (week 6) → the sealed look (week 7).
- **Paper order:** detect, handle, report.

### 2.4 The flow, in words

1. Development tiles → frozen production calls on every road, hidden roads included.
2. A frozen cloud generator → clouded copies of clear tiles (after image for Q1, Q2 and §6.4; before image for Q3).
3. Optional correction (§6.4) → recomputed cues → the same fold models' calls → scores against published labels on
   clear roads.
4. Realism tests decide whether the bed speaks for real cloud.
5. Tiers, ranges and the provenance map for Q2.
6. Everything frozen → one batched sealed look, with decision rules set in advance.

---

## 3. Data, sampling frame and the sealed check

### 3.1 Development data (the only data used in weeks 1–6)

| Data | What is used | Size | Source |
|---|---|---|---|
| SpaceNet 8 Louisiana-East, Hurricane Ida (2021) | Maxar before and after tiles, warped to one 0.5 m UTM grid, greyscale after the first step | 226 tiles: 186 training + 40 validation, pooled in the folds | Evidence 01; split file (v1 §0) |
| **Acquisitions** | **One after acquisition for all 226 tiles** (`10300100C46F5900`). Two before acquisitions: area 0 (`105001001A0FFC00`, 105 tiles) and area 2 (`10300100AF395C00`, 121 tiles) | — | Critic §2 (mapping file) |
| Road labels | OpenStreetMap centrelines; `flooded` is "yes" (487) or missing (593), never "no" | 1,037 touched roads on 217 tiles | Evidence 01 |
| Assessable roads (adopted rule) | Roads not gated by the tile rule or the road rule | 798 roads | Evidence 01 |
| Clear roads for the test bed | Less than 5% of the strip under the dark-rise mask | 769 roads on 190 tiles (433 flooded, 336 dry) | Evidence 03 |
| Real thin-cloud roads | At least 20% of the strip under dark rise | 93 roads on 39 tiles; 24 labelled flooded | Evidence 01; critic |
| Pilot roads (§6.4.5) | The 93 thin-cloud roads and the other 175 roads on the same 39 tiles | 268 roads on 39 tiles | Cache (today) |
| Opaque-cloud tiles | At least 20% of the tile under the bright mask | 17 tiles, 146 roads, 3 labelled flooded | Critic (earlier review) |
| Building labels (only if the week-1 counts pass) | Footprint polygons with a `flooded` field | Unknown on development tiles | v3 §4 |
| HRC_WHU (Li et al. 2019, unverified) | Google Earth RGB at 0.5–15 m, converted to grey; expert cloud masks; no shadows labelled | 120 development images, 24 per land-cover type | Evidence 01, 02; critic §2 |

### 3.2 One cloud field: the sampling frame (critic M1)

- **Evidence (critic's check):** every development tile takes its after image from one acquisition. So all real cloud
  in the development data is one cloud field, imaged at one moment.
- **Inference:** the 39 thin-cloud tiles and the 17 opaque tiles are pieces of that one field. They are not independent
  draws of "real cloud". "Area" is the same as "before image".
- **What the plan does:**
  - Every real-cloud statement is scoped to **"the cloud in one Maxar acquisition"**.
  - **Week 1 counts the cloud patches:** connected groups of cloudy tiles on the tile grid, from the frozen bright and
    dark-rise masks. This is label-free. The patch count is reported beside every tile count.
  - **Real-cloud quantities are resampled by cloud patch, not by tile.** These are the real thin level, check 1's
    reference, the real side of the use-level check, and the 24-road recall. If there are fewer than 10 patches, those
    quantities are described, not tested.
  - Cloud variety comes from HRC_WHU, which is another imagery source (Google Earth). The paper says so each time.
  - Leave-one-area-out swaps the before image and the place. It never swaps the cloud. It is described that way.

### 3.3 Folds

- **Primary folds (exist).** Five folds by whole tile (`StratifiedGroupKFold`, shuffled, seed 662), in
  `sn8_heldout.py`. Production and every logged result use them. No road is scored by a model that saw its tile.
- **Blocked folds (critic M3).** Square blocks of tiles on the grid, assigned to five folds stratified by flood class.
  - **Block side:** the range of the semivariogram of tile flood share, rounded up; at least 3 tiles; **capped at 7
    tiles.** **Evidence (critic):** sides of 3, 5 and 7 tiles leave 61, 33 and 22 occupied blocks. If the range is
    longer than 7 tiles, use 7 and label every interval "may be too narrow".
  - **Run in the same week as each primary result,** not in week 6. The cues are cached, so this is CPU work only.
  - **Rule:** a tier or a primary claim stands only if it holds under both the shuffled and the blocked folds. The
    critic offered "blocked only" or "both". "Both" keeps the logged production comparison and adds the check.
- **Buffered folds and leave-one-area-out:** sensitivity runs in week 6, shown in figure 12.
- **The Otsu thresholds** (98 and 71 grey levels) were learned on the 186 training tiles, which are also held out in
  turn. **Inference:** a small leak. Production is frozen with these thresholds, and re-learning them would change
  which roads are assessable. So the primary keeps them. A sensitivity run re-learns them inside each fold and reports
  how many roads change status (critic M27; partly taken, see §21).
- **HRC_WHU:** the authors' split. Development images only.
- **The test bed:** production's fold models score held-out clear tiles. Only the held-out tile's images get cloud. No
  model is ever trained on synthetic cloud.
- **The frozen setup for the sealed look** is fitted on all 226 development tiles.

### 3.4 Intervals

- **Primary intervals: a spatial block bootstrap** over the same blocks as the blocked folds (critic M3). Two-sided 95%.
- The tile bootstrap (exists) is shown beside it.
- Real-cloud quantities are resampled by cloud patch (§3.2). HRC_WHU by image, within land-cover type.
- McNemar's exact test stays secondary, because it treats roads as independent.
- **One wording everywhere (critic M8).** "95% interval" means a two-sided 95% spatial-block bootstrap interval. A
  ceiling or a margin is met when the interval's upper end is below it. Secondary decisions use Holm's step-down on the
  bootstrap p-values within their question. The intervals shown stay at 95%.

### 3.5 The sealed check, with decision rules (critic M2)

One batched, logged look on **Monday 7 December** (week 7), by setups frozen on Friday 4 December.

- **In the look (proposed):** the 40 SpaceNet 8 Louisiana-East test tiles (south 22, west 18) and the 30 HRC_WHU test
  images.
- **What it is: "held-out, same scene".** Never "external". **Evidence (critic):** 39 of the 40 test tiles touch a
  development tile (4.4 of 8 neighbours on average).
- **Decision rule per primary result, fixed now:**
  - **Confirmed:** the sealed estimate has the same sign as the development estimate and lies inside the development
    95% interval.
  - **Not confirmed:** otherwise.
  - **Uninformative:** named at Gate 0, before the look. A sealed test is uninformative if its expected 95% interval
    (from the development calls, scaled to the sealed counts) would include 0 even if the true value equalled the
    development estimate. **Inference (critic):** sealed intervals are about 2.2 times wider than development ones.
- **Minimum cloud for Q2's real-data parts.** The sealed cloud is counted with the frozen masks inside the look. H2a,
  H2b and the real recall are re-scored only if the sealed tiles hold at least 10 thin-cloud tiles and at least 10
  trusted flooded roads under thin cloud. Otherwise: "not re-scored: too little cloud". **Inference (critic):** about 7
  thin-cloud and 3 opaque tiles are expected.
- **HRC_WHU test images are pooled** over urban, vegetation and water (18 images). Six per type cannot show a ±0.10
  margin. Snow and barren are described only.
- **§6.4's safety veto is re-run on the sealed clear tiles.** The development run is a screen, not proof, because the
  pilot has looked at some of those tiles.
- **Justin's call (decision 7; ask by week 3):** the north negative set (333 tiles; the only real false-alarm test for
  Q3's after-only call) and Germany (202 tiles; confounded, per v1).
- **Never used:** Louisiana-West (no labels).

### 3.6 Licences and release (critic M26)

- SpaceNet 8 and HRC_WHU are research-only data (input card). HRC_WHU is "academic purposes only" (evidence 02). The
  loader carries the credit line "HRC_WHU (Li et al., 2019; imagery Google Earth), academic use only".
- Bed images mix SpaceNet 8 tiles with HRC_WHU cloud. **Inference:** a derived image takes the stricter terms of its
  sources. **So the paper releases code and seeds, not bed images.**
- Whether a journal figure may show HRC_WHU crops (Google Earth imagery) is not in the files (decision 9).
- **Gemma stays out of the paper's figures** unless the target journal allows AI-written figure text. If used, the
  AI-use statement says so.
- DINOv2 runs from local open weights in `~/Masters/models/`. Its licence from the model card goes in the data
  statement.

---

## 4. Units of analysis

| Question | Scored unit | Resampling unit (the real sample) | Reported at |
|---|---|---|---|
| Q2 | The road: the strip about 5 m either side of the centreline | Spatial block of tiles; cloud patch for real-cloud quantities | Road; tile; area (metres of flooded road) |
| Q2, S1 real part | An HRC_WHU patch of 256 × 256 pixels | The image, within land-cover type | Urban, vegetation and water pooled; each type described |
| Q3 | Road strip (primary); building footprint plus a 10 m ring (only if buildings are in) | Spatial block | Object; tile |
| Q1, primary test and check 1 | Ground windows under cloud: 14-pixel (7 m) cells; 64-pixel (32 m) windows for patchiness | Spatial block (synthetic side); cloud patch (real side) | Rise bin (three bins) |
| Q1, check 2 | An HRC_WHU image, with real and pasted cloud | The image, within type | Type; band from the cloud edge; cloud area band |
| Q1, use-level check | Road strip | Spatial block (synthetic); cloud patch (real) | Rise bin |
| §6.4 | Road strip | Spatial block | Road; tile flood class |

- **Evidence (critic X2, M3):** roads on one tile share cloud, flooding and image conditions, and neighbouring tiles
  share them too. So every result states its tile count, its block count and, for real cloud, its patch count.
- **Inference (MAUP and ecological fallacy):** a tile or area figure does not say what happened on one road. Example:
  "cloudy tiles in area 2 carry few flooded labels" does not mean any one hidden road was dry.

---

## 5. What already exists and what is new

| Piece | Status | Where |
|---|---|---|
| Held-out harness: 5 folds by tile, seed 662 | **Exists** | `sn8_heldout.py` |
| Tile-resampled intervals; McNemar's exact test | **Exists** | `held_out_report`, `paired_report` |
| Spatial block bootstrap; blocked folds; cloud-patch counter | **New, small** | — |
| "Cannot assess" handling: gated roads neither fitted nor scored | **Exists** | `gated_calls`, `gated_report` |
| Bright, dark and dark-rise masks; the adopted rule | **Exists** | `sn8_clouds.py` |
| He de-hazing (one air light per tile) | **Exists** | `sn8_clouds.dehaze` |
| **Two-date de-hazing** (`reference_dehaze`, `corrected_rows`, `corrected_table`, `show_refhaze`) | **Exists** (prototype). Frozen as run (§6.4.3). No tests yet | `sn8_refhaze.py` |
| Corrected cue tables for the 39 thin-cloud tiles (two-date and He) | **Exist** (cache) | `ClaudeFunctions/.cache` |
| The pilot's scoring script | **Exists outside the repo.** Move it in, with its hash | Coordinating session |
| Fold models that also call hidden roads | **Exists for the 93 thin-cloud roads** (pilot). New for opaque-tile roads and for the bed | Extends `gated_calls` |
| Neighbour check on the tile grid | **Exists** | `sn8_clouds.neighbour_check` |
| HRC_WHU loader, authors' split, single-date masks, per-type scores | **Exists** | `sn8_cloudref.py`; `Code/cloudref_test.ipynb` |
| The bright tile rule scored on HRC_WHU patches (S1) | **New, small** | — |
| Production model and its frozen stages | **Exists** | `sn8_models.flood_model`; `production.json` |
| Frozen DINOv2-L change cues per road | **Exists** (roads only) | `sn8_dino.py` |
| Road strip and 10 m ring owner maps; `_before`, `_after`, `_change` cue columns | **Exists** | `sn8_roads.py` |
| Run logs with code hashes | **Exists** | `sn8_results.py` |
| Per-tile building and flooded-building counts | **Code exists, not run** | `sn8_data.label_counts` |
| Tree and shadow visibility gate (for the "missing = dry" check) | **Exists**; the stratified re-run is new, small | Evidence 01 |
| Uniform-haze injection (evidence 03) | **In a past session's scratchpad** (`cloudresearch/mask_bias.py`). May be gone. Move it into the repo | Evidence 03 |
| Synthetic cloud generator: families M, X and X-fast, uniform control, two placements, before or after image, seeded | **New** | — |
| Shape pool (HRC_WHU, rescaled to 0.5 m) or the fallback (procedural shapes) | **New** | — |
| Realism statistics, the pooled distance ΔD, check 2 by edge band | **New** | — |
| Use-level check (top cues and flood probability at matched rise) | **New, small** (cues exist) | — |
| Test-bed runner: cloud → recomputed cues (with DINOv2) → fixed fold models | **New** (the pilot's path is a start) | — |
| After-only model; mean-imputation arm | **New, small** (columns exist) | — |
| Before-image cloud flag; permanent-water mask and its picture audit | **New** | — |
| Provenance layer and map | **New, small** | — |
| Q2 tier scorer (non-inferiority), ranges, anchored tipping counts | **New** | — |
| Within-tile label test (Q2b) and its near-threshold check | **New, small** | — |
| "Change kept" measure; fill-from-before control arm | **New, small** | — |
| Co-registration of the two dates (about 0.6 m ground shift) | **Exists** | `sn8_coreg.py`; evidence 01 |
| Tilt resources for every step (project rule) | **New, small.** None exist yet for the roads side test (v1 §0) | `Project/Tiltfile` |

---

## 6. Analysis steps per question

### 6.1 Q2 (lead). What can a flood-road map reliably tell users about roads hidden by cloud?

**Outcome.** For each statement a map could make about a hidden road, its error, or a range where the error cannot be
measured.

**Exposure.** Cloud over a road's strip in the after image, at levels set by the existing masks before scoring:
- clear;
- thin: at least 20% of the strip under the dark-rise mask;
- opaque: the tile has at least 20% bright cloud.

**The five statements.**

| # | What the map says | Error measured | Where it can be measured | Empirical, or fixed by the label coding? | Best tier possible |
|---|---|---|---|---|---|
| S1 | "This road is hidden; it cannot be assessed." **Made by the frozen rule: tile rule + road rule** (critic M5) | Missed hidden; false hidden | **Tile-rule part:** real cloud, HRC_WHU patches (bright mask). **Road-rule part:** the bed only | Empirical | Tile-rule part: "reliable on HRC_WHU imagery". Road-rule part: "synthetic only" |
| S2 | "This hidden road is flooded" | Share of "flooded" calls that are wrong, minus the same roads' clean error | Bed only. Real cloud: recall on the 24 trusted flooded roads, reported | Bed: empirical. Real cloud: fixed by the label coding (dry labels untrusted) | "Synthetic only"; "range only" if realism fails |
| S3 | "This hidden road is dry" | Share of "dry" calls that are wrong, minus the same roads' clean error | Bed only | As S2 | As S2 |
| S4 | Accuracy on hidden roads | None (no truth under cloud) | A range | Fixed by the label coding. Its width is empirical | Range only |
| S5 | Flooded road length in an area with hidden roads | None | A range, in metres | Fixed by the label coding. Its width is empirical | Range only |

**Inference (critic M8): much of this table is fixed before any data.** So the paper marks each row "empirical" or
"fixed by the label coding". The empirical content is S1, the bed's S2 and S3, H2a, H2b, and the widths of the ranges.

**Primary test (named; critic M8).** S1's tile-rule part on HRC_WHU real cloud. Both of its rates must meet their
ceilings. Because both must pass, no adjustment is needed between them (an intersection–union rule; needs citation).

**Secondary tests (Holm within Q2).** S1's road-rule part on the bed; S2; S3; H2a; H2b. Justin may promote S2 and S3 to
co-primary (decision 4).

**Steps:**
1. **Fit once and keep every call.** Production's fold models under the adopted rule. Each fold model also calls the
   hidden roads of its own fold (they are still not fitted on). **Exists** for the 93 thin-cloud roads (pilot).
   **New** for opaque-tile roads.
2. **Freeze the rules** in the pre-registration at the end of week 1 (§8).
3. **S1, tile-rule part, on real cloud (week 2; primary).**
   - Cut the HRC_WHU development images into 256 × 256 pixel patches (the mirror's patch size; evidence 02).
   - A patch is **flagged** when at least 20% of it is under the bright mask (the tile rule's cut). It is **truly
     hidden** when at least 20% of it is under the expert cloud mask.
   - Missed hidden = the share of truly hidden patches not flagged. False hidden = the share of patches that are not
     truly hidden but are flagged.
   - Decided on urban, vegetation and water pooled. Barren and snow are described only. **Evidence (01):** the dark
     mask's false alarms are high on bright barren ground (F1 0.48). Neither type is part of the Louisiana use.
   - Shown by resolution band if week 1 finds the image resolutions. Otherwise the tier says "resolution not
     controlled".
   - The single-date dark mask is reported beside it, **only as a candidate for later promotion.** It is not S1,
     because the map does not use it and production is frozen.
   - **The tier names the imagery:** "measured on HRC_WHU (Google Earth, greyscale), not on Maxar".
   - **Inference (a prediction, stated so it can be wrong):** the bright mask's pixel recall is 0.28 (evidence 01).
     Unless the 20% patch rule changes that a great deal, the missed-hidden rate will exceed 30%. Then the pre-set
     reading below applies.
4. **Other real-data parts (week 2).**
   - **S2, real recall.** Flooded found on the 24 trusted flooded roads under thin cloud. Reported. **It carries no
     inferential weight anywhere** (critic §8). The pilot already has it: 70.8% with the after image as it is (§6.4.5).
   - **H2a, renamed (critic M8): "the change in the reported score from counting hidden roads".** Score the same calls
     twice: on the 798 assessable roads, and on all 1,037 with missing labels read as dry. The score can move either
     way. Read it beside the S4 bounds.
   - **H2b, with an identification check first (critic M9).**
     - **The check (label-free cue, published labels):** the dark-rise distribution near its threshold on clear
       flooded roads against clear dry roads. If dry roads sit much closer to the threshold, mask false alarms favour
       dry roads. Then a within-tile gap cannot be read as label omission.
     - **The test:** on tiles with both clear and thin-cloud roads, are the cloudy roads less often labelled flooded?
       An exact test stratified by tile (Mantel–Haenszel type; needs citation).
     - **Sensitivity:** keep only "cloudy" roads within 50 m of an opaque core (bright mask). **Inference:** those are
       more likely to be real cloud.
     - **Wording:** "roads the mask calls cloudy carry fewer flooded labels". "Omission" only if the check rules out
       false alarms.
   - **Opaque tiles.** Described only: 17 tiles, 3 flooded labels, one acquisition.
   - **Blocked folds** for each of these, in the same week.
5. **The bed parts (week 4).**
   - **S1, road-rule part.**
     - On the bed, a road is "truly hidden" when the placed cloud covers at least 20% of its strip at a level thick
       enough to spoil the call.
     - "Thick enough" = the thinnest of the four grid levels at which family X's **balanced accuracy** falls more than
       1.5 points below clean, **as a point estimate** (critic M27). The grid can land only on four values. The paper
       says so.
     - **Shaped placement only.** Whole-tile cloud has no "outside", so false hidden cannot be measured there (critic
       M22). The false-hidden rate includes roads just outside a placed cloud, so it measures the 20 m dark window's
       edge effect (critic X1).
   - **S2 and S3: one scored set (critic M6).** All roads in the **whole-tile cell**, family X, at the real thin
     level. Every road is hidden there, so the flooded share equals the clean share (433 of 769, 56%).
     - The measure: hidden error minus the same roads' clean error, paired.
     - **Recall and specificity are reported beside S2 and S3,** with the flooded share of each scored set. They do not
       move with the base rate.
     - Secondary sets: roads the road rule flags in that cell; covered roads in the shaped cell.
6. **Assign tiers (critic M6, M7).**
   - **Non-inferiority.** A statement is "as reliable as the clear-sky map" when the upper end of the 95% interval of
     (hidden error − clean error, same roads) is below **δ = 5 points** (§8).
   - **Three outcomes, kept apart:**
     - **shown:** the whole interval lies below δ;
     - **fails:** the whole interval lies above δ (the error is too high);
     - **not shown:** the interval straddles δ (too few roads to tell).
   - **Tier names:**
     - **"Reliable on [named imagery]":** a real-imagery error with a published truth, shown.
     - **"Synthetic only":** shown on the bed, **and** Q1's primary realism test and its use-level check both favour
       family X at the real thin level.
     - **"Range only":** no error can be measured, **or** Q1's realism fails for family X at the real thin level. The
       bed's S2 and S3 then go in as a sensitivity result, clearly marked (critic M7).
   - Every tier must hold under both the shuffled and the blocked folds (§3.3).
7. **Bound the rest.**
   - **S4.** Two bounds on accuracy on hidden roads: every missing label is flooded; every missing label is dry.
   - **S5.** Per area: low end = assessed flooded length; high end = that plus all cannot-assess length. In metres.
   - **The range widths are results** (critic M8). Pre-set note: a flooded-length range whose high end is more than
     twice its low end is "too wide to act on". **Inference;** Justin may change it.
   - **Tipping points (critic X3).** For each conclusion, where the truth under cloud would have to sit to flip it.
   - **"Missing = dry" in clear sky (critic M4; ranked change 8).**
     - **Sensitivity run, pre-set:** repeat S2, S3, H1b and H3a on clear roads whose visible share (from the existing
       tree and shadow gate) is at or above the clear roads' median.
     - **Tipping counts are reported as a share of clear dry roads,** beside two diagnostics: the visible share on clear
       flooded against clear dry roads; and, if buildings are counted in week 1, the share of clear "dry" roads that
       pass through the 10 m ring of a building labelled flooded.
     - **No label is changed.**
   - **No filling in from neighbours.** **Evidence (01):** in area 2, a cloudy tile had 0 of 7 roads labelled flooded
     beside clear neighbours at 79%; in area 0 the neighbours are dry too. **Evidence (03):** under thick haze the mask
     flags flooded roads more often (+13.2 points at t = 0.6). **Inference:** so the assessed roads under-represent
     flooded ones, and neighbours are a biased guide. Under §2.1, a value taken from neighbours is "filled".
8. **Report.**
   - **The provenance map:** per road, its observed, corrected and not-observed shares, and its answer (changed, not
     changed, cannot assess). Cannot-assess roads are shown by area beside the flood share of their assessed
     neighbours. This keeps "can we see it?" apart from "is it flooded?", as WorldFloods v2 does (Portalés-Julià et
     al. 2023, unverified).
   - An optional risk–coverage figure, with the classifier fixed and only the abstention varied.

**What counts as "no" (pre-set).**
- S1 shown, S2 and S3 fail: **"a map can say only where it cannot see"** (`selected_questions.md`).
- **S1 fails (new; critic M5): "a map cannot reliably say even where it cannot see."** S2 and S3 are still reported,
  but no hidden-road statement is called reliable.
- S2 or S3 "not shown": "these data cannot tell". That is not a "no".

### 6.2 Q3. When only the before image is cloudy, does the after image alone find change better than both images together?

**Outcome.** Balanced accuracy (missed floods and false floods weigh the same), on clear objects, against published
labels. **Claim wording in the paper (critic M25):** "maps flooded roads from the after image alone". Under §2.1, the
after-only call is a state call.

**Exposure.** Synthetic cloud on the before image only, at four levels fixed in advance: **opaque full cover
(primary;** Justin's case), Q1's real thin level, and two levels between. **Evidence (01):** no Louisiana-East before
image is cloudy, so the cloud must be synthetic.

**Arms.**
- The two-date production model (the comparator).
- **New (critic M11): the two-date model with its before-image and change cues set to their training-fold means.**
  This is the usual way to handle a missing input (needs citation). **Inference:** it is the fairer comparator at
  opaque cover.
- The after-only model.
- The two-date model without DINOv2 cues (a fair match for the after-only model, which has none).
- Routing by a before-cloud flag (secondary); abstaining; always "flooded".

**Steps:**
1. **After-only model and the clean gap (week 2; CPU only).**
   - Production's random forest settings on the existing `_after` columns only, in the same five folds, and in the
     blocked folds.
   - **The clean gap** = two-date minus after-only balanced accuracy, both on clean roads, paired by road. **This is a
     reported primary estimate (critic M11):** a real-image measure of what losing the before image costs. It is
     reported with its interval. It is not a test.
   - **Gate 1 (go/no-go):** the lower end of the after-only model's clean balanced accuracy is at least 0.60.
   - **Usefulness bar (critic M11).** The after-only call may stand in on a map only if its "flooded"-call and
     "dry"-call errors on clean roads are within δ = 5 points of the two-date model's errors on the same roads
     (non-inferiority, §8). If not, before-cloudy roads are "cannot assess", whatever H3a says.
2. **Cloud the before images (week 5).** Q1's frozen generator, families X and M, on held-out clear tiles. After images
   untouched. Recompute the two-date cues, with DINOv2 (about 45 min of GPU per level; v3 §6).
   - **Leak check:** the after-only calls must be identical on clean and clouded copies.
3. **H3a, decided at opaque cover only (critic M10).** After-only minus two-date balanced accuracy, paired on the same
   roads, with its 95% interval. The mean-imputation arm is reported beside it. The other three levels and the
   crossover thickness are secondary, Holm-adjusted. Also reported: flooded recall, the dry-call rate, and what
   production does now with these roads.
   - **Inference (critic M11):** at opaque cover the two-date model reads a blank before image. A win there shows how
     the forest behaves on input it never saw, not what the before image is worth. That is why the clean gap and the
     mean-imputation arm are reported.
   - **Inference (v3):** today's gates would not notice before-image cloud. The tile rule reads the after image only,
     and the road rule looks for a rise from before to after, while before-only cloud gives a fall.
4. **H3b, state against change (week 5; real images).**
   - Mark clear dry roads with permanent water in their 10 m ring in the clear before image (water covering at least
     10% of the ring). The water mask is classical and label-free. Its threshold is set on the training tiles before
     scoring.
   - Compare the false "flooded" rates of the two models inside and outside that group.
   - **Picture audit (critic M12):** 30 roads drawn from the water group with seed 662, shown to Justin as pictures
     only. If most are not water, H3b is reported as descriptive. No count from the audit enters any score.
   - Tested only if its minimum detectable difference is 15 points or less.
5. **H3c, routing (first to be cut).** As in v1: the flag is a fall of the dark floor from before to after, plus
   smoothness on the before image, with Otsu thresholds learned inside the training folds. Oracle routing, flag routing
   and no routing are scored on clouded and on clean roads. **Inference:** floodwater also lowers the after floor, so
   the flag may fire on floods. Its rate on clean flooded and clean dry roads is reported.
6. **Buildings** repeat steps 1–4 only if they pass the week-1 counts rule (§8) and the schedule holds.

**What counts as "no".** The interval at opaque cover includes 0 or lies below it. **Also a pre-set answer:** if H3a
passes but the usefulness bar fails, the answer is "the after image alone beats a blinded two-date model, but not well
enough to map; abstain".

### 6.3 Q1. Can we use synthetic clouds to represent real-life blockages in satellite imagery?

**Outcome.** **One primary test (critic M13):** is family X closer to real cloud than the crude control? Secondary:
the use-level check, the absolute match margins, and H1b (whether cloud's errors lean towards "no change").

**Steps:**
1. **Build the generator and freeze it (week 2; frozen Fri 6 Nov).**
   - **Shapes.** HRC_WHU outlines, rescaled to 0.5 m by each image's resolution. **Evidence (v1 §0):** the image files
     do not store it.
     - **Fallback, decided at the end of week 1 (critic M17).** If per-image resolutions cannot be established from Li
       et al. (2019) or the dataset page, the shapes are procedural, with a size spectrum taken from the bright-mask
       outlines of the 17 opaque tiles (native 0.5 m, same sensor).
     - **Inference:** using those outlines directly would make the bright mask's job easier on the bed. Using only
       their size spectrum lessens that.
     - The size and edge sharpness of the shapes used are reported.
   - **Thickness.** Opaque inside the outline, thinning past its edge. The air light and the edge fall-off are set from
     the bright cores of the 17 opaque-cloud tiles (label-free; one acquisition).
   - **Family M:** image × t + A × (1 − t), the model behind the dark channel (He, Sun & Tang 2011, unverified).
   - **Family X:** the same blend, plus a cloud texture from real HRC_WHU cloud pixels, air light that varies across the
     tile, and clipping. **Fallback** if Justin does not allow cloud pixels: a procedural noise texture.
     - **New (critic M19):** X's air-light variation scale is **measured from real cloud before any scoring**: the
       spread of brightness across the 17 opaque cores, or across HRC_WHU cloud pixels.
   - **New family X-fast (critic M19):** X plus blur, with air light that varies faster than §6.4's 64 m fit window
     (proposed scale: 20 m; inference). It is used only in §6.4's robustness cell, so that §6.4's result does not rest
     on one family that suits its own fit.
   - **Uniform-haze control:** evidence 03's model, deliberately crude.
   - **Placements:** whole-tile cloud, and shaped clouds placed by a seeded rule. Cover and distance from the cloud edge
     are covariates, not levels to tune.
     - **Under whole-tile placement, family M is the control in all but its air light (critic M13).** So that cell is
       labelled as the control.
   - **Seeds:** one per cell, plus **a second seed on each primary cell** (critic M27), so the generator's own
     randomness shows.
   - **Frozen** with its settings file and code hash before any change call is scored on it. **Rule:** no realism
     statistic is ever used to set the generator.
2. **The real thin level and the rise bins (week 1).**
   - **The real thin level is "the median dark-floor rise of mask-detected thin cloud"** (critic M15's wording),
     measured on all thin-cloud ground, not on any target, before scoring. The 93 strips' value is reported beside it.
   - **Sensitivity reference:** thin cloud within 50 m of an opaque core.
   - **Rise bins for check 1: three, fixed now,** at the tertiles of mask-detected thin cloud's rise (label-free;
     computed in week 1).
3. **The primary realism test (week 3; CPU only).**
   - **Placement:** shaped, for X and M. The control is uniform haze. **Inference (critic M13):** "pattern kept" is the
     same for M and the control inside a cloud, because a local correlation ignores a constant gain and offset. It
     differs only at edges, at clipping, through rounding and through noise. Hence shaped placement.
   - **The statistics** are three that the generator does not set: contrast kept (local spread, after over before);
     pattern kept (local before–after correlation); patchiness (the semivariogram of after − before). Real and
     synthetic cloudy windows are picked by the same mask rule.
   - **For each statistic and rise bin:** the absolute gap between the synthetic and real medians, divided by the real
     cloud's own effect. **That effect is measured within tile** (cloudy minus clear windows on the same tile; critic
     M15), not across places. Averaged over the 9 cells: **the pooled distance D.**
   - **The test: ΔD = D(X) − D(control),** paired by clear tile (same tiles, same seeds). Synthetic side resampled by
     spatial block; real side by cloud patch.
   - **"X represents real cloud better than a crude control"** when the upper end of the 95% interval of ΔD is below 0.
4. **The use-level check (week 4, on the bed's cues; critic M14).** Label-free.
   - At the real thin level and matched rise bins, compare two distributions between real thin-cloud strips (93 roads,
     one acquisition) and synthetic strips:
     - the forest's **top 10 cues**, by production's feature importances (the list is fixed in week 1, before scoring);
     - the **flood probability**.
   - Matched on strata of before-image cues, to control for the ground.
   - A pooled distance U; **ΔU = U(X) − U(control)**, read as for ΔD.
   - **Confound (inference):** real thin-cloud roads may hold a different flood share than clear roads. Matching on
     before-image cues reduces this but does not remove it. The paper says so.
5. **Secondary checks (Holm within Q1).**
   - **Check 1 margins:** per statistic and bin, the interval of (synthetic − real) lies within ± half the real effect
     (measured within tile).
   - **Check 2, HRC_WHU (critic M16).**
     - Paste synthetic clouds at the four thickness levels into clear parts of the development images. Shapes come
       from other images than the one they are pasted into.
     - Score the bright and dark masks on these clouds and on the real cloud in the same image, paired by image.
     - **Compare recall at matched cloud area and in fixed bands from the cloud edge** (0–20, 20–60 and over 60
       pixels; inference), not F1 over the whole image.
     - **The claim rests on urban, vegetation and water.** Snow and barren are descriptive.
     - Images kept within a factor of 4 of 0.5 m (2 m or finer) if the resolutions are known. Otherwise the result says
       "resolution not controlled".
     - Margin: ±0.10 in recall. **Corrected justification (critic M16):** it is a judgement of a usable match. v1's
       reason, "smaller than the gap between ground types", is false for some pairs (vegetation 0.78 against water
       0.74).
   - **Circularity flag on M:** if the dark mask's recall on M exceeds its recall on real cloud by more than 0.10
     (lower end > 0), M is too close to the mask's model and is left out of every realism and method claim.
6. **The test bed and H1b (week 4).**
   - Production's fold models score held-out clear tiles whose after images carry cloud.
   - **Grid, fixed in advance:** families M and X × whole-tile and shaped placement × four levels (one thinner than the
     real thin level, the real thin level, one thicker, opaque) = 16 cells. The M whole-tile cells are the control.
   - **H1b (primary within this step):** whole-tile cell, family X, real thin level: recall loss on flooded roads minus
     loss on dry roads. 95% interval. Beside it, the 24 real trusted flooded roads, as a consistency check only.
   - **X1 recheck:** the dark-rise flag rate on flooded and dry roads, per level, family X.
   - Methods tried on the bed count only on family X (and X-fast) and never see the t map.
7. **Buildings** (only if in): the same bed on clear buildings.

**What counts as "no" (pre-set).**
- **ΔD's interval includes 0 or lies above it:** X is not shown to represent real cloud better than a crude control.
  Q1's answer: "not shown".
- **ΔD passes but ΔU does not:** "matches real cloud on looks, not on use". Q2's S2 and S3 then drop to "range only"
  (§6.1 step 6).
- **Both pass:** "closer to real cloud than a crude control, on preset checks, in 0.5 m greyscale imagery of one
  acquisition". The secondary margins then say whether it also matches within margins.

### 6.4 The "handle" step: two-date correction and Justin's two-pass design

#### 6.4.1 Justin's two ideas

- **Idea 1** (decision log): "since we have two images I want to see what we can do about clouds when we have another
  image of the same location, can we align the pixels and potentially know how to dehaze the cloud".
- **Idea 2** (decision log): "if the change detected is a cloud then we can figure out a way to scale the image and put
  it back through the change detector to look for smaller scale changes like roads or houses".
- **Inference: the two ideas are one loop.** Idea 1 is the "scale" step of idea 2.
- **Where this step sits is Justin's call** (decision 3). **Default:** inside the "handle" step, as a sub-question,
  Q3d: *When one date is thinly clouded and the other clear, are flood calls on the corrected image as reliable as
  clear-sky calls, on synthetic cloud?* It is not yet in `selected_questions.md` or the abstract.

#### 6.4.2 The two-pass design

| Pass | What it does | Exists? | Source |
|---|---|---|---|
| **Pass 1: is the change a cloud?** | The frozen masks: bright (tile rule) and dark rise (road rule). A large change with a raised dark floor is read as cloud, a blockage, not as ground change (§2.1) | Exists | Evidence 01 |
| **Scale (radiometric)** | Inside the cloud, fit after ≈ α·before + β in 64 m windows on unchanged pixels. Undo only the cloud's dimming t and added light L (§6.4.3). Thin: "corrected". Too thick, or refused by the fit: "not observed" | Exists (prototype) | Evidence 05 §6, design 1 |
| **Pass 2: look again at object scale** | The frozen production detector (classical, texture and DINOv2 cues on road strips) runs again on the corrected after image | Exists (pilot) | `corrected_rows` |
| **Provenance** | Observed, corrected or not observed, per pixel. A filled pixel never votes | New, small | Evidence 05 §6, design 2 |
| Scale (spatial), **stated option** | Re-run DINOv2 on finer, upsampled crops inside corrected areas | New; **exploratory** (§6.4.8) | Evidence 05 §6, design 3 (indirect support only) |

- **Evidence (05 §4, §6):** no paper was found that detects cloud as change, corrects inside it, then re-detects small
  objects. The closest are IR-MAD's re-weighting loop and Bruzzone & Bovolo's (2013) VHR framework (both unverified).
  **No novelty is claimed.** Justin checks the literature before any novelty wording (AGENTS.md rule 9).
- **The pilot already ran this loop once on real thin cloud,** with the radiometric scale step (§6.4.5).
- **Houses:** the same loop applies to buildings if they come in. It has not been run on them.

#### 6.4.3 The method as run (frozen)

From `sn8_refhaze.py`, read today (SHA-256 begins `ff5a09bbf03aca62`). **This is the method the formal tests use.**

| Step | As run |
|---|---|
| Inputs | Greyscale before and after, 0–255, on the co-registered 0.5 m grid (ground shift about 0.6 m; evidence 01). Valid pixels only |
| Clear pixels | Dark rise (after minus before dark channel, 20 m window) at or below its Otsu threshold (71 grey levels; evidence 01) |
| Gain and offset between the dates (g, h) | Robust least squares of after on before, over the tile's clear pixels. Three passes. Each pass drops pixels beyond 2.5 robust SDs (1.4826 × the median absolute residual). Falls back to g = 1, h = 0 when there are 1,000 clear pixels or fewer. Stops at the last good estimate when the kept pixels spread by less than one grey level: **the reported fix for the ill-conditioned fit** |
| Local fit (α, β) | Weighted least squares in 129 × 129 pixel windows (64 m), by box filters. Three passes. Weights are reset each pass to drop pixels beyond 2.5 robust SDs (one SD for the whole tile). Local variance floored at 10⁻³ |
| Cloud terms | t̂ = α / g; L̂ = β − t̂ · h |
| Haze rule | Haze only where 0.2 ≤ t̂ ≤ 1 and L̂ ≥ 0. Everywhere else t̂ = 1 and L̂ = 0 (left alone) |
| Smoothing | t̂ and L̂ box-smoothed over 65 pixels (32 m), after the haze rule |
| Correction | Ĵ = (after − L̂) / max(t̂, 0.2), clipped to 1–255 |
| Pass 2 | Every production road cue recomputed on Ĵ: classical, GLCM, texture, DINOv2 |
| Scoring | Production's fold models (5 folds by tile; fitted on clear, assessable roads). The script is outside the repo |

**The freeze record (to complete in week 1).**
- The hash of `sn8_refhaze.py` and of the functions it calls in `sn8_clouds.py` (file hash begins
  `6b64958daaae77e8`).
  - **Inference (code read):** the module's own cache key hashes its five functions and its settings, but not the
    imported `dark_channel` and `cloud_thresholds`. A change in `sn8_clouds.py` would not rebuild the cache. Add them
    to the key.
- The pilot's scoring script, moved into the repo, with its hash. Then the pilot's three rows are re-run from the repo
  as a Tilt resource, with blocked folds.
- **The prototype's history (critic M18).** What the files show: two runs on 23 October (tables at 20:12 and 22:40); the
  code last edited at 20:20; one reported fix (an ill-conditioned fit) with unchanged numbers. **Inference:** the 20:20
  edit is likely the variance guard in `_robust_global`. **Which other settings were tried, and on which tiles, is not
  in the files.** The coordinator logs it before the pre-registration.
- **Tests in code (label-free):** on a clear tile, t̂ is near 1 almost everywhere; on a tile with uniform synthetic
  haze, t̂ recovers the set value away from edges.
- **Label-free diagnostics reported on every run:**
  - the share of tiles that fall back to g = 1, h = 0;
  - the share of pixels whose local variance is below one grey level squared. **Inference (code read):** in
    near-uniform 64 m windows the local slope is poorly determined, and the reported fix was in the global fit, not
    the local one.

#### 6.4.4 Differences between v1's plan, the run, and the formal test (critic M18–M20)

| Setting | v1 §6.4 (planned) | As run (pilot) | Formal test in v2 | Why |
|---|---|---|---|---|
| Fit window | 100 m; sensitivity 50 m | 64 m | **64 m.** Sensitivity: 128 m | Freeze what ran. A larger window guards against floods bigger than the window, the risk the docstring names |
| Opaque floor | t̂ = 0.3 | 0.2 | **0.2** | Freeze what ran |
| Guard 1: leave the road out of its own fit | Yes | No | **No.** Replaced by the "change kept" veto, which measures the harm guard 1 was meant to prevent | Freeze what ran; measure the risk instead |
| Guard 2: robust fit | Drop large negative residuals first (a sign heuristic) | Symmetric trimming at 2.5 robust SDs, three passes: an iterative invariant-pixel loop | **As run.** v1's sign heuristic is dropped. The full IR-MAD form (soft no-change weights, orthogonal regression; Nielsen 2007, Canty & Nielsen 2008, unverified) is a named sensitivity variant | The run is already IR-MAD-style in kind: it re-weights towards unchanged pixels. Swapping the primary after the pilot would be a choice made after looking |
| g and h when the whole tile is cloudy | From clear training tiles of the same before–after pair | From the tile's own clear pixels; else g = 1, h = 0 | **As run. The whole-tile cell is dropped for this method.** The formal test uses shaped placement, where the tile keeps clear ground | **Inference (critic §2):** under whole-tile cloud the run either corrects little, or maps the cloudy date onto the before image's look. The critic offered "implement the rule, or drop the cell". Dropping the cell keeps the frozen code |
| Sign rule (haze dims and adds light) | Not stated | t̂ ≤ 1 and L̂ ≥ 0 | **As run** | — |
| Primary outcome | Beat He de-hazing | — | **Corrected roads as reliable as their own clean calls, within δ** (§6.4.6) | Critic M19: beating He is a weak bar, and He already fails the safety bar |
| Change kept | A diagnostic | — | **A second veto** | Critic M20 |
| Safety veto | Development clear tiles | Partly seen: 175 roads on 39 tiles | A development screen, **re-run in the sealed look** | Critic M18 |
| Before-cloudy direction | Tested | Not run | **Exploratory,** unless a guard that works there is shown on the bed | Critic M20 |

- **Reading before the freeze:** Lin et al. (2015), the closest published match (evidence 05; TLDR only; unverified),
  in Justin's GMU session. **Rule:** anything changed after the pilot is a named variant. The as-run arm stays the
  primary, and is reported beside any variant.

#### 6.4.5 The pilot result (exploratory)

**Evidence (pilot; coordinator, 2026-10-24; development data only).** The production model, trained on clear roads in 5
folds by tile, called the roads of the 39 thin-cloud tiles three ways: with the after image as it is, de-hazed by He's
single-image method, and corrected by the two-date method (64 m window; robust re-weighting; gain and offset fitted on
clear pixels; haze accepted only where t ≤ 1 and L ≥ 0, and t ≥ 0.2 in the code). It was re-run after fixing an
ill-conditioned fit, and the numbers did not change.

| Roads | As it is | He single-image | Two-date |
|---|---|---|---|
| 24 trusted flooded under thin cloud: flooded found | 70.8% | 87.5% (4 gained, 0 lost; McNemar p 0.125) | 83.3% (3 gained, 0 lost; p 0.25) |
| 69 dry-labelled under thin cloud (labels untrusted): called dry | 91.3% | 68.1% (16 flipped to flooded) | 87.0% (3 flipped) |
| 175 clear roads on the same tiles: accuracy | 77.7% | 73.7% (−4.0 points; p 0.25) | 78.3% (+0.6 points; p 1.0) |

**Counts (my arithmetic from the percentages; inference).**
- Trusted flooded roads: 17, 21 and 20 of 24 found. Seven were missed as it is. He wins back 4 of them; the two-date
  method wins back 3.
- Dry-labelled roads: 63, 47 and 60 of 69 called dry.
- Clear roads: 136, 129 and 137 of 175 right.

**Why it is exploratory.**
- These 24 roads had already been looked at (v1 §6.4; critic M18). The method's settings may have been shaped by that
  look.
- Twenty-four roads can show only effects of about 25 points or more (evidence 03). The gains are 12.5 and 16.7 points.
  Neither is significant.
- McNemar treats roads as independent. All 39 tiles come from one cloud field (§3.2).
- The 175 "clear" roads are the other roads on the same tiles (inference: 268 − 93, from the cache). Their exact rule
  should be logged with the script.

**What it suggests (inference, to be tested on the bed).**
- On trusted floods, both corrections find more than no correction.
- Elsewhere, the two-date method changes far fewer calls: 3 flips against 16 on dry-labelled roads, and +0.6 against
  −4.0 points on clear roads.
- **The 69 dry labels cannot be trusted.** A flip there may be a hidden flood found, or a false flood. The pilot cannot
  tell. "Called dry" is agreement with a missing label, not accuracy.
- The clear-road row is the only scored check on false floods. He's −4.0 points there (not significant) points the same
  way as evidence 01's −1.7 (p 0.15). These are different measurements (§0).
- **So the two-date method may recover floods while disturbing little else.** This is a hypothesis for the bed, not a
  finding. The two arms overlap, so they are not ranked.

**Why 70.8% here and 67% in evidence 01, for the same 24 roads:** different fits. The pilot uses current production
(with DINOv2 cues, fitted under the adopted rule); evidence 01 used the tile-rule fit. Both are development data.

**Label-free diagnostic of the fit (coordinator, 2026-10-24, after v2 was written; evidence 01; script
`evidence/pilot_scripts/diag_core.py`).** Pixels only, no road labels.
- At 0.5 m the two dates barely agree pixel by pixel on clear ground: correlation r = 0.46 on tile 2_19_55 (the
  figure tile) and 0.09 on 2_15_45. Likely causes: look angle, shadows, stripped trees, residual shift.
- So the least-squares slopes are diluted toward 0: g = 0.16 on 2_19_55 (an orthogonal fit gives 0.31), and local α is
  0.03–0.05 everywhere.
- Consequence: the fit reads clear ground as hazy too (median t̂ 0.32 on clear pixels; 66% counted as haze), and about
  half of the cloud pixels fall below t̂ = 0.2 and are left alone as opaque. In the figure the bright core stays; the
  haze over the roads is lifted. What the as-run method does is closer to a local contrast stretch than a haze estimate.
- **Bearing on §6.4.4 (a decision for Justin, §19):** v2 keeps the as-run arm primary and the full IR-MAD form as a
  variant, to avoid a choice made after looking. The diagnostic is label-free, but it was made after the pilot. The
  options are (a) keep the as-run primary and report the IR-MAD/orthogonal fit as the named variant, as v2 says; or
  (b) pre-register the IR-MAD/orthogonal fit (at a scale where the dates agree) as the primary, before any bed
  scoring, and keep the as-run arm beside it. Either way the 24 pilot roads stay exploratory.
- **Conflict with the education briefing (reported, not acted on; found by the data + tool agent):** rule P3 advises
  no IR-MAD or other linear normalisation on the 8-bit visual product, because the dates' tone curves differ and are
  not linear. That cuts against option (b) as worded above and against the as-run linear model. A fix in that spirit
  matches the dates on unchanged pixels at a coarser scale with a tone match that need not be linear (for example a
  monotone curve), and uses IR-MAD's idea (unchanged pixels) without its linear transform. Justin rules (§19).
- Add these two numbers to the label-free diagnostics of every run: the clear-pixel correlation between the dates and
  the share of clear pixels counted as haze.

#### 6.4.6 The formal tests

All on the bed unless stated. **Scored set:** roads whose strip is at least 20% under the **placed** cloud in the
shaped cell. The set is chosen by placement, not by any mask. Every arm scores the same roads.

- **Arms.** No correction; the two-date method as run; He (secondary comparator); fill-from-before (a control that should
  fail); the identity (a control that should pass); the clean image (an oracle).
- **Primary (critic M19).** At the real thin level, family X, shaped placement: the corrected calls against the same
  roads' clean calls. **"As reliable as clear sky"** when the upper end of the 95% interval of (corrected error − clean
  error) is below δ = 5 points, for both the "flooded"-call and the "dry"-call errors. Both must pass.
- **Veto 1, safety on clear ground.** On the tiles of the 769 clear roads, with no cloud added: the loss of flooded found,
  and of balanced accuracy, must have an upper end of 1.5 points or less. Split by tile flood class.
  - **A development screen, re-run in the sealed look** on the sealed clear tiles (§3.5).
  - **Gate 0 checks that it can be passed:** the upper end expected under no effect, from the He arm's logged calls
    (critic M20).
- **Veto 2, change kept (critic M20).** On flooded strips: the after − before grey difference after correction, over its
  clean value. Near 1 the flood is kept; near 0 it is erased. **Its lower end on mostly flooded tiles must stay at or
  above 0.8.** Also shown by tile flood class, with pictures.
- **Positive controls for the vetoes (critic M20).** The fill-from-before arm must fail veto 2. The identity arm must
  pass veto 1. If either does not, the veto is broken. It is fixed before the method is scored.
- **Recovery (secondary):** (corrected − cloudy) over (clean − cloudy), in balanced accuracy. Half or more counts as
  useful.
- **Robustness (secondary; reported, never used to choose):** the primary cell repeated on family X-fast, with the 128 m
  window, and with the full IR-MAD variant.
- **Dose and response (secondary):** the four family-X shaped levels.
- **Provenance (secondary):** the share of covered roads that stay callable (less than 20% "not observed"), and the
  primary repeated on callable roads only.
- **Real thin cloud:** the pilot's three rows, re-run from the repo with blocked folds. Exploratory. No weight.
- **Circularity.** Family M is the method's own model, so it is scored on X only (results on M are an upper bound,
  marked circular). X-fast is added because X's smooth air light also suits a smooth fit (critic M19). **Inference:**
  statistics that compare the corrected image with its reference (pattern kept, say) are pushed up by the fit itself,
  so they are not used to judge this method.
- **Gate 0b, at the generator freeze (week 2):** count the covered roads in the shaped cell (label-free), and compute the
  primary's expected interval from the clean calls. If it is wider than δ, the shaped cell runs with two seeds and the
  covered roads are pooled. Fixed before any scoring.

#### 6.4.7 The before-cloudy direction (exploratory)

- The reference is then the flooded after image. **Inference (critic M20):** dry ground in the cloudy before image sits
  above what the dark water predicts. So changed pixels have positive residuals, the same sign as haze. The as-run haze
  rule cannot tell them apart.
- **Status:** exploratory, on the bed only, unless a guard that works there is shown. Third on the cut list.

#### 6.4.8 The spatial reading of "scale" (a stated option)

- **The idea:** inside corrected areas, run DINOv2 again on crops upsampled two times, so a 7 m patch becomes 3.5 m.
  **Inference:** haze lowers contrast, and small objects may need finer patches.
- **Support is indirect** (evidence 05 §4): multi-level and coarse-to-fine designs (Bruzzone & Bovolo 2013; Zhang, Peng
  & Huang 2017; Han et al. 2024; all unverified).
- **A limit (inference):** the frozen forest was trained on cues from 7 m patches. Cues from finer crops come from a
  different distribution, so they cannot feed the frozen model.
- **Status:** an exploratory figure on the bed only (critic M23): DINOv2 change heatmaps at 7 m and 3.5 m patches, on
  clean, clouded and corrected images of the primary cell. Pictures, no calls. Fourth on the cut list.

#### 6.4.9 Filled pixels

- §2.1's rule applies: a filled pixel is never scored, never a cue, never shown as observed.
- The fill-from-before arm is a control only. Its job is to show that filling erases floods, as evidence 05 warns.

#### 6.4.10 Prior work (evidence 05; no novelty claimed)

- The method is **relative radiometric normalisation**, a known family: IR-MAD (Nielsen 2007; Canty & Nielsen 2008),
  pseudo-invariant features (Du, Teillet & Cihlar 2002), and Lin et al. (2015), the closest match. All unverified, read
  at abstract, TLDR or metadata level.
- The stable-surface assumption "degrades when the landscape changes very quickly" (Hagolle et al. 2015, abstract,
  unverified). A flood is such a change. Veto 2 tests this.
- A between-date regression fitted on valid pixels is the gap-filling cousin of this fit (Zeng, Shen & Zhang 2013,
  unverified).
- **Evidence (05 §5):** no published reference-date de-hazing for single-band VHR that fits only on unchanged pixels in
  local windows was found. That is "not found in the sources read", not a novelty claim.
- **Evidence (05 §1 item 8; main project, buildings, development data):** local Wallis normalisation gave +0.036 AUC;
  global IR-MAD gave −0.004. **Inference:** this supports correcting in local windows.

#### 6.4.11 Cost (inference, at about 45 min of DINOv2 per bed cell)

- The as-run method on the four family-X shaped levels: about 3 h.
- He, fill-from-before and identity on the primary cell: about 1.5 h (identity reuses the clouded cues).
- X-fast (clouded and corrected), the 128 m window and the IR-MAD variant: about 3 h.
- The safety screen on the 190 clear-road tiles: about 45 min. The sealed safety re-run: about 10 min.
- The pilot's re-run from the repo: cached, unless the code changes.
- The fits themselves run on CPU.

#### 6.4.12 What counts as "no"

- **Veto 1 or veto 2 fires:** the method is rejected, whatever it does under cloud.
- **The primary fails or is not shown:** "the correction is not shown to make thin-cloud roads as reliable as clear
  ones". Thin-cloud roads stay "cannot assess".
- **It passes on X but not on X-fast:** "it works only where cloud varies as smoothly as its fit". Reported as a limit.

#### 6.4.13 What it would add to Q2 (inference)

If it passes, a thin-cloud road can carry a "corrected" call on the map. Q2's S2 and S3 are then also scored on
corrected calls (shaped cell). Q2's scope does not change unless Justin says so.

**Limits.** The two-date fit cannot be checked on real cloud: there are no real two-date cloud labels (earlier critic
C4-1). Its real-cloud evidence is the 24 trusted flooded roads, which carry no inferential weight.

---

## 7. Baselines and comparators

| Question | Comparator | Why |
|---|---|---|
| Q2 | The usual report: one accuracy over all labelled roads, missing read as dry, no cannot-assess layer | The thing H2a measures |
| Q2 | **The same model's clean calls on the same roads** | The reference for δ (non-inferiority) |
| Q2 | Production 83.0% on 798 roads; always "flooded" 55.3% | Evidence 01 |
| Q2, S1 | The single-date dark mask, as a candidate only | Critic M5 |
| Q3 | The two-date production model | `selected_questions.md` |
| Q3 | **The two-date model with before-image and change cues at their training means** | Critic M11 |
| Q3 | The two-date model without DINOv2 cues | A fair match for the after-only model |
| Q3 | Abstaining (with its coverage loss); oracle routing; always "flooded" (balanced accuracy 0.50) | A cautious map; an upper reference; a floor |
| Q1 | The uniform-haze control, inside ΔD and ΔU | Critic M13 |
| Q1 | Real cloud: SpaceNet 8 thin cloud found by the mask (one acquisition); HRC_WHU expert masks | What "represent" is measured against |
| Q1 bed | Each model's clean scores on the same objects | Paired by object |
| §6.4 | **The same roads' clean calls** (primary reference); no correction; He (secondary); fill-from-before and identity (controls); the clean image (oracle) | §6.4.6 |

---

## 8. Rules fixed in advance

**Proposed now. Frozen in the pre-registration at the end of week 1. Justin may change any of them before then.**

**A derived reference: the clear-sky error of the map.** *Inference (arithmetic on evidence 01, as in v1).* On the 798
assessable roads, the tile rule + road rule scored 81.8% and found 87.8% of flooded roads; 55.3% are flooded. So
"flooded" calls are wrong about 19% of the time (about 91 of 478), and "dry" calls about 17% (about 54 of 320). Balanced
accuracy is about 0.81. Production now scores 83.0%, so its rates are likely a little lower. Recomputed from the logged
calls in week 1.

| Rule | Proposed value | Why |
|---|---|---|
| **Interval wording** | Two-sided 95%, spatial block bootstrap; met when the upper end is below the limit | Critic M8: one wording everywhere |
| **Multiplicity** | One primary test per question. "Both must pass" rules need no adjustment between their parts. Secondaries: Holm within their question | Critic M8 |
| **S1 missed hidden** (primary, tile-rule part) | Upper end ≤ 30% | A user-cost judgement: at most 3 in 10 hidden patches unmarked. **No longer anchored on a mask score** (critic M5). Predicted to fail for the bright rule (inference, §6.1 step 3) |
| **S1 false hidden** | Upper end ≤ 10% | A coverage-cost argument, stated as one: flagging 1 in 10 clear patches discards about as much as the road rule flags overall (93 of 891 roads, 10.4%; evidence 01) |
| **S1 types** | Decided on urban, vegetation and water pooled; barren and snow described | Critic M5, M16 |
| **δ, non-inferiority** | 5 points, for S2, S3, §6.4's primary and Q3's usefulness bar | **Inference:** at most one extra wrong call in 20. Gate 0 checks that δ can be reached: if the interval expected under no effect is wider than δ, the statement is pre-labelled "cannot be shown with these roads" |
| **Outcomes** | Shown (interval below δ); fails (interval above δ); not shown (straddles) | Critic M6 |
| **"Truly hidden" on the bed** | The thinnest grid level where family X's balanced accuracy falls more than 1.5 points below clean (point estimate), with at least 20% of the strip covered | Critic M27 |
| **Q2a** (H2a) | Shown if the lower end > +1.5 points, or < −1.5. "No change" if the whole interval lies within ±1.5. Otherwise inconclusive. Its own width computed at Gate 0 | Evidence 03: paired intervals about ±1.1 to 1.3 points. Rule differences in evidence 01 were 0.7–1.7 points |
| **Q2b** | Exact test stratified by tile, after the near-threshold check. Described only if fewer than 10 mixed tiles carry a flooded label | Critic M9 |
| **Ranges** | "Too wide to act on" if the high end is more than twice the low end | Inference; critic M8 |
| **Q3 Gate 1** | Lower end of after-only clean balanced accuracy ≥ 0.60 | Any constant call scores 0.50 |
| **Q3 usefulness bar** | After-only errors within δ of the two-date model's, on the same clean roads | Critic M11 |
| **Q3 H3a** | Lower end of (after-only − two-date) > 0, **at opaque cover only** | Critic M10 |
| **Q3 H3b** | Tested only if its minimum detectable difference ≤ 15 points; descriptive if the picture audit fails | Evidence 03; critic M12 |
| **Q3 H3c** | Clean-road cost upper end ≤ 1.5 points; recovers at least half the oracle gain | Evidence 03; v3 |
| **Q1 primary (ΔD)** | Upper end of ΔD < 0 | Critic M13 |
| **Q1 use-level (ΔU)** | Upper end of ΔU < 0; binds Q2's synthetic tier together with ΔD | Critic M14, M7 |
| **Q1 rise bins** | Three, at the tertiles of mask-detected thin cloud's rise | Critic M13 |
| **Q1 check 1 margins** (secondary) | Interval of (synthetic − real) within ± half the real effect, measured within tile | Critic M15 |
| **Q1 check 2 margin** (secondary) | Recall difference within ±0.10, at matched area and edge band; urban, vegetation, water | Critic M16 |
| **Circularity flag on M** | Dark-mask recall on M exceeds real by more than 0.10 (lower end > 0) → M left out | Earlier critic C2-1, C2-2 |
| **Q1 H1b** | Lean shown if the lower end of (recall loss − dry-kept loss) > 0, family X, whole tile, real thin level | `selected_questions.md` |
| **Buildings** | Week 1, on counts: at least 150 clear flooded buildings on at least 50 tiles, or buildings are out. If in: clean balanced accuracy lower end ≥ 0.60 by the end of week 3 | Critic M21 |
| **Block side** | Semivariogram range of tile flood share, rounded up; 3 to 7 tiles | Critic M3 |
| **Cloud patches** | Fewer than 10 → real-cloud quantities described, not tested | Critic M1 (inference) |
| **Distance to an opaque core** (H2b and thin-level sensitivities) | 50 m | Inference |
| **Visible share** ("missing = dry" sensitivity) | At or above the clear roads' median | Critic M4 |
| **Sealed decision rule** | Confirmed / not confirmed / uninformative (§3.5); at least 10 thin-cloud tiles and 10 trusted flooded roads for Q2's real parts; HRC_WHU pooled over three types | Critic M2 |
| **§6.4 settings** | As run: 64 m window, floor 0.2, 2.5 robust SDs, three passes; sensitivity 128 m | Frozen code (§6.4.3) |
| **§6.4 primary** | Corrected minus clean error, upper end < δ, for both error kinds | Critic M19 |
| **§6.4 veto 1** (safety) | Upper end of the loss ≤ 1.5 points on clear tiles; re-run sealed | Evidence 03: the noise is about 1.5 points |
| **§6.4 veto 2** (change kept) | Lower end ≥ 0.8 on mostly flooded tiles | Critic M20 |
| **§6.4 recovery** (secondary) | At least half of cloud's loss won back | Same bar as H3c |

---

## 9. Power

**The rule of thumb used here (inference; needs citation).** At 80% power and a two-sided 5% test, the smallest
detectable difference is about 1.43 times the half-width of a 95% interval. Block intervals will be wider than the tile
intervals below.

| Test | Objects and tiles | Interval known? | Smallest detectable difference | Plan |
|---|---|---|---|---|
| Q2 S1, tile-rule part (primary) | 72 HRC_WHU images in the three types; about 10 patches per 1,280 × 720 image (inference, from the one header read) | No | Compute at Gate 0 from the per-image spread | Primary |
| Q2a | 798 against 1,037 roads; 217 tiles | Evidence 03: ±1.1 to 1.3 points (paired) | About 1.6–1.9 points | Tested; may be inconclusive |
| Q2 real recall under thin cloud | 24 roads; 39 tiles; one cloud field | Evidence 01: −0.54 to 0.00 | About 25 points or more (evidence 03) | Reported; no weight |
| Q2b | Mixed tiles: count unknown | — | — | Count in week 1 |
| Q2 S2, S3 (whole-tile cell) | 769 roads; 190 tiles | Not computed | Inference: about ±4–6 points | Against δ = 5; reachability at Gate 0 |
| Q2 S2, S3 on the flagged subset | About 35–120 roads (critic M6, from evidence 03) | — | Too few for δ (inference) | Secondary only |
| Q1 ΔD | 190 clear tiles (synthetic side); the real side's patch count unknown | No | Gate 0 | Primary |
| Q1 ΔU | 93 real strips, one acquisition | No | Weak on the real side (inference) | Binding check |
| Q1 check 2 | 24 images per type; the count after the resolution filter unknown | Unknown | From `cloudref_test.ipynb`'s per-image spread | Secondary |
| Q1 H1b | 433 flooded + 336 dry; 190 tiles | Evidence 03: ±4 (t 0.9), ±7 (t 0.8), ±12 (t 0.7) for flag-rate gaps | About 6–10 points at thin levels | Tested |
| Q3 H3a | 769 roads; 190 tiles | Inference (v3): wider than ±1.3 | From after-only against production on clean roads | Large effect expected at opaque cover (inference) |
| Q3 clean gap and usefulness bar | 769 roads | Not computed | Gate 0 | Reported; bar against δ |
| Q3 H3b | Unknown | — | — | Tested only if ≤ 15 points |
| Buildings | Unknown | — | — | Week-1 counts |
| §6.4 primary | Covered roads in the shaped cell (counted at Gate 0b) | Not computed | Gate 0b | Two seeds if needed |
| §6.4 veto 1 | 769 roads | From the He arm's logged calls | Gate 0 | Reachability checked |
| §6.4 veto 2 | Flooded strips on mostly flooded tiles (count unknown) | No | Gate 0 | Veto |
| §6.4 real thin cloud | 24 roads; 39 tiles | As above | About 25 points or more | Exploratory; already seen |
| Sealed look | 40 tiles; 18 HRC_WHU images pooled | Inference: about 2.2 times wider | Gate 0 names uninformative tests | Decision rule (§3.5) |

**Gate 0 (end of week 1)** computes, before any cloud outcome is scored:
- the block size, and the block-bootstrap widths it gives;
- the cloud patch count;
- the sizes of the S2 and S3 scored sets, and whether δ can be reached;
- the equivalence power for Q1's margins and §6.4's vetoes;
- the expected sealed widths, which name the uninformative sealed tests.

**Rules:**
- Spatial-block intervals are the primary test everywhere. McNemar is secondary only.
- Every result shows its tile, block and (for real cloud) patch counts, and its smallest detectable difference.
- Any test whose smallest detectable difference exceeds its margin is relabelled "descriptive" before scoring.
- The margin rules fail safe. Low power gives "not shown", never a false "match" or "reliable".
- One primary test per question. Secondaries are Holm-adjusted within their question.

---

## 10. Spatial assumptions and GeoAI checks

### 10.1 CRS, units and scale

- **CRS.** SpaceNet 8 tiles are warped to one 0.5 m UTM grid (evidence 01). Units are metres. HRC_WHU has no CRS (v1
  §0). It supplies cloud shapes, textures and mask scores, never locations.

| Scale | Size | Source |
|---|---|---|
| Pixel | 0.5 m | Evidence 01 |
| Road strip | About 5 m either side of the centreline | `selected_questions.md` |
| Ring around a road or building | 10 m | `sn8_roads.RING_M` |
| Dark-channel window | 41 pixels (20 m) | `sn8_clouds.DARK_WIN` |
| DINOv2 patch | 14 pixels (7 m); 3.5 m in the spatial option | `sn8_dino.PATCH` |
| §6.4 fit window | 129 pixels (64 m); sensitivity 128 m | `sn8_refhaze.REF_WIN` |
| §6.4 smoothing of t̂ and L̂ | 65 pixels (32 m) | `sn8_refhaze.py` |
| HRC_WHU patch (S1) | 256 pixels: 128 m at 0.5 m, far more at 15 m | Evidence 02 |
| HRC_WHU pixels | 0.5–15 m | Evidence 02 |

- **Inference (earlier critic X1):** the 20 m dark window is wider than the strip. A minimum filter moves cloud edges
  inwards by up to the window. The bed's false-hidden rate and the edge-distance covariate measure this.
- **Inference (critic M16):** a 41-pixel window covers 20 m at 0.5 m but about 600 m at 15 m. Hence resolution bands,
  or a cap at 2 m, for HRC_WHU.
- **Inference (§6.4):** a flood larger than the 64 m window is the method's known risk (docstring). Veto 2 by tile flood
  class and the 128 m sensitivity measure it.
- **Inference (v3):** a small house covers only a few 7 m DINOv2 patches. Buildings may carry weaker DINOv2 signal.

### 10.2 Dependence

- **One cloud field** (§3.2): real-cloud quantities are resampled by cloud patch.
- **Tiles are not independent** (critic M3): neighbouring tiles share flood and cloud. Hence the spatial block
  bootstrap and the blocked folds.
- **Evidence (earlier critic X2):** the recall drop under thin cloud is p = 0.010 by road (Fisher), but its tile
  interval reaches 0. Treating roads as independent overstates the evidence.
- **Inference:** roads and buildings on one tile share cloud and flooding. Two targets on the same tiles are not two
  independent samples, and not two events.

### 10.3 Neighbouring tiles across folds

- **Evidence (critic):** 225 of 226 development tiles have a development neighbour. Shuffled folds put neighbours in
  other folds.
- **Inference:** a road's model is often fitted on the tile next door, which can lower absolute error. The tiers use
  absolute rates, so leakage pushes them towards "pass" (critic M3).
- **What the plan does:** blocked folds in the same week as each primary result; a claim must hold under both schemes;
  buffered folds and leave-one-area-out in week 6.
- **What would weaken a claim:** a primary difference that changes sign or loses its interval under blocked folds.

### 10.4 Leakage

- No road is scored by a model that saw its tile (exists).
- No model is trained on synthetic cloud.
- Generator settings come from label-free opaque cores, never from realism statistics.
- HRC_WHU shapes are pasted into other images than their own.
- The loaders refuse held-out data unless `allow_held_out=True` is passed. The sealed look is the only call that sets it.
- **The pilot's look** (§6.4.5): its 268 roads include some of the clear roads behind veto 1. So veto 1 on development
  data is a screen, and the sealed re-run is the test.
- **Filled pixels never feed a call** (§2.1).

### 10.5 Sampling bias, temporal alignment and transfer

- **Evidence (critic):** cloud is clustered in areas 0 and 2, in one acquisition. Real thin cloud was picked by the
  dark-rise mask.
- **Inference:** the bed uses clear roads, which may differ from the ground under the clouds. The bed's numbers carry
  over to cloudy places only by assumption. The flood share and cue distributions of clear roads are reported beside
  those of thin-cloud roads.
- **Temporal.** Before and after images come from different dates and satellites. Ground shifts by about 0.6 m after
  co-registration, with no effect (evidence 01). Q3's realism verdict comes from after-image cloud and is carried over
  to before images taken on another date (inference).
- **Transfer.** One event, **one after-image acquisition**, two before acquisitions, two areas, at most two targets.
  Five land-cover types for the cloud itself only. Any wider claim needs Justin's approval (AGENTS.md rule 9).

---

## 11. Threats to validity

| Threat | Claim it hits | Evidence that would weaken the claim | What the plan does |
|---|---|---|---|
| No truth under cloud | Q2 S2–S5 | — | Ranges; tiers; tipping points |
| **One cloud field** (M1) | Every real-cloud number | Few cloud patches | Scope to one acquisition; patch resampling; HRC_WHU for variety |
| **Correlated tiles; absolute tiers** (M3) | Tiers; primary intervals | A result that differs under blocked folds | Block bootstrap; both-folds rule; same-week runs |
| **Sealed look: same scene, small** (M2) | "Confirmed" | Uninformative widths | Decision rule; uninformative tests named at Gate 0; "held-out, same scene" |
| "Missing = dry" in clear sky; **omission under trees** (M4) | S2, S3, H1b, H3a | Results differ on high-visibility roads; small tipping shares | Visible-share sensitivity; anchored tipping counts |
| **S1 measured on another imagery source** (M5) | S1 "reliable" | — | The tier names the imagery |
| **Base rate in the scored set** (M6) | S2, S3 | The scored set's flooded share differs from clean | One set; recall and specificity beside |
| Synthetic cloud is not like real cloud | Q2's synthetic tier; Q3's thin levels | ΔD or ΔU fails | One primary test; **binding** to Q2 (M7) |
| Circular haze (family M) | Any claim on M | The circularity flag fires | Claims on X only |
| Real thin cloud chosen by the mask (M15) | Check 1; the real thin level | Results change near opaque cores | Core-distance sensitivity; within-tile effect |
| Check 2 confounded by size and thickness (M16) | Q1 secondary | — | Matched area; edge bands; thickness grid |
| Two-date mask never checked on real two-date labels | S1's road-rule part | Stays "synthetic only" | Stated in the tier |
| **H3a against a blank before image** (M10, M11) | H3a | The mean-imputation arm closes the gap | Opaque-only decision; clean gap; usefulness bar |
| After-only model lacks DINOv2 | H3a | The gap vanishes against the two-date model without DINOv2 | Second comparator |
| The flag fires on floodwater | H3c | High flag rate on clean flooded roads | Rates reported |
| The water mask is unmeasured (M12) | H3b | Results change with the threshold; the audit fails | Picture audit; secondary |
| **The pilot looked first** (M18) | §6.4's real numbers; veto 1 on development data | — | Exploratory; sealed re-run of veto 1 |
| **Family X suits a smooth fit** (M19) | §6.4's primary | X-fast fails | X-fast cell; δ primary; X's air-light scale from real cloud |
| **Flood residuals with haze's sign** (M20) | §6.4 before-cloudy; bright floodwater | Change kept low | Veto 2; before-cloudy exploratory |
| **Floods larger than the 64 m window** | §6.4 | Veto 2 fails on mostly flooded tiles; the 128 m variant differs | Veto 2 by flood class; 128 m sensitivity |
| **Ill-conditioned local fit in uniform windows** (code read) | §6.4 | Many low-variance pixels | Diagnostic reported on every run |
| **Filled pixels mistaken for observations** | Any map | — | Provenance rule (§2.1) |
| **The definition of change is not ruled on** | The framing of every statement | Justin rejects it | Tests unchanged; statements re-labelled (§2.1) |
| Scale mismatch (HRC_WHU 0.5–15 m; 20 m window against a 5 m strip) | Q1; S1 | Results change when only images near 0.5 m are used | Rescaling or fallback shapes; resolution bands |
| Clear roads differ from cloudy ground | The bed's link to real cloud | Different flood shares or cues | Both distributions reported |
| One event, one acquisition | Every "general" word | Germany, if spent, disagrees | Scoped claims (§12) |
| One model plays every agent role (rule 4) | Every judgement here | — | Justin's review, the pre-registration, tests in code, the sealed look |
| Choices made after looking | Everything | — | Pre-registration; the stop rule (§16); post-pilot changes only as named variants |

---

## 12. Claim words, and the earlier critic's points

### 12.1 Claim words (critic M25)

| Claim word | What the tests support | Wording for the paper |
|---|---|---|
| "Reliably" (Q2) | Error no worse than the clear-sky map plus δ, on one scene; S1's real part on HRC_WHU | "as reliable as the clear-sky map, within a preset margin" |
| "Represent real-life blockages in satellite imagery" (Q1) | Closer to real cloud than a crude control, on preset checks, for one acquisition and the HRC_WHU types that pass | "closer to real cloud than a crude control, on preset checks, in 0.5 m greyscale imagery" |
| "Finds change" (Q3) | Reads the after state; tested against a blinded two-date model | "maps flooded roads from the after image alone" |
| "See through cloud" (§2.1, §6.4) | Synthetic family X (and X-fast), a clear-tile screen, a sealed safety re-run; real-cloud numbers exploratory | "corrects thin cloud on synthetic cloud; one real acquisition explored" |
| "One event, one sensor" | One after-image acquisition, two before acquisitions | "one after-image acquisition of one event" |
| "A tested rule for reporting hidden roads" (abstract) | Development data and a same-scene held-out set | "a rule tested on held-out tiles of the same scene" |
| "Detect" (Q1, in the arc) | Detection is tested in S1 and check 2 | Q1 "builds and checks the test bed" |

### 12.2 The earlier question critic's points (`question_review.md`), briefly

| Point | Where it stands in v2 |
|---|---|
| X1 mask bias by flood state | Absent under uniform haze (evidence 03); re-checked on family X (§6.3 step 6); false alarms without haze checked before H2b (§6.1 step 4) |
| X2 tiles, not roads | Now blocks and cloud patches (§3.4) |
| X3 no truth under cloud | Ranges, tiers, tipping points (§6.1) |
| X4 neighbour leakage | Blocked folds in the same week; both-folds rule (§3.3) |
| X5 untrusted agreement | Never called accuracy; the 10 handed-back roads are not used as evidence; the pilot's 69 dry-labelled roads are agreement only (§6.4.5) |
| X6 novelty | None claimed |
| X7 no second dataset | Scoped to one acquisition (§12.1); Germany is Justin's call |
| C2-1, C2-2 circular haze | Family X and X-fast; the circularity flag; ΔD against the control |
| C2-4 spatial component | Shaped placement is never cut (§15.4) |
| C2-5 HRC_WHU scale | Rescaling, or the fallback shapes (§6.3 step 1) |
| C3-2 fixed classifier | Fit once, keep every call |
| C4-1 no real two-date labels | Stated as a limit of S1 and §6.4 |

---

## 13. AI-assisted coding and analysis tools

- **Claude Code (Anthropic)** writes the analysis code, runs it, builds the figures and drafts text, under Justin's
  direction. Justin makes and records every decision (`decision_log.md`).
- **The agent roles** (question agent, critics, methodology, writer, validation) run on the same model. Their agreement
  is not independent validation (AGENTS.md rule 4). The checks that are independent of the model: Justin's review, the
  pre-registration, tests in code, and the sealed look.
- **Code and runs.** The private repository Jrog378/GeoAI-Roads (evidence 01). Every run as a Tilt resource (project
  rule), long GPU passes in the background. Every run logged with its code hashes (`sn8_results.py`). Seed 662
  throughout. Production frozen in `production.json`.
- **Libraries in the existing code:** NumPy, SciPy, pandas, OpenCV, scikit-learn (random forest,
  `StratifiedGroupKFold`), matplotlib, and DINOv2-L with registers (`vit_large_patch14_reg4_dinov2.lvd142m`) from local
  weights.
- **DINOv2** detects change, inside the frozen model only. **Gemma** is not used in any score, label, tier or decision,
  and stays out of the paper's figures unless the journal allows it (§3.6).
- **The paper's AI-use statement** names general task types (writing and running analysis code, making figures,
  drafting and editing text, summarising literature). It names no files, and it stays truthful.

---

## 14. Figures (numbers come with pictures)

Every figure is built from development data, except those marked "sealed". No sealed image is shown before the look.
Error crops and example tiles are picked by rules fixed in advance (for example, the 12 most confident wrong calls per
cell, ordered by tile id).

| # | Figure | Numbers it carries | Question |
|---|---|---|---|
| 1 | Study area: development tiles by area; clear, thin and opaque roads; **cloud patches**; sealed tiles as grey outlines only | Tile, block and patch counts | All |
| 2 | Label coding under cloud: tiles with "yes" and missing labels on cloudy and clear roads | H2b and its check | Q2 |
| 3 | The masks: before, after, bright, dark and dark rise on example tiles; HRC_WHU patches per type with the expert outline | S1's tile-rule part | Q2 S1 |
| 4 | Real against synthetic cloud at 0.5 m: families M, X, X-fast and the control beside real cloud at matched rise | — | Q1 |
| 5 | Realism: ΔD and ΔU with intervals; statistic distributions by rise bin; check 2 by edge band | Q1 verdicts | Q1 |
| 6 | Dose and response on the bed: recall and dry-call rate against thickness, per family and placement, with the real anchor | H1b | Q1 |
| 7 | What DINOv2 sees: change-cue heatmaps, clean against clouded (and, for the option, 7 m against 3.5 m patches) | — | Q1, §6.4 |
| 8 | Before-image cloud: clouded before, after, the calls of each arm; balanced accuracy against thickness | H3a; the clean gap | Q3 |
| 9 | Permanent water: crops of dry roads near water before the storm, with both models' calls; the picture audit | H3b | Q3 |
| 10 | The tier table as a figure, and **the provenance map**: observed, corrected, not observed, with the cannot-assess roads by area | S1–S5; flooded-length ranges | Q2 |
| 11 | Optional risk–coverage curve, classifier fixed | Coverage and trusted-flooded misses | Q2 |
| 12 | Sensitivity: each primary result under shuffled, blocked, buffered and leave-one-area-out folds | Results with intervals | All |
| 13 | Sealed look: the primary results with their verdicts (confirmed, not confirmed, uninformative) | Sealed numbers | All (sealed) |
| 13a | **Two-date correction:** before, hazy after, corrected after, t̂, and the pixels left out of the fit (`show_refhaze`); flooded-road crops before and after correction; change kept by flood class | The pilot (exploratory); the bed's primary and vetoes | §6.4 |
| 14 | Error crops per primary cell | — | All |

---

## 15. The eight-week plan

### 15.1 Box: What the Assignment 4 pilot shows

> **Slides due Sunday 25 October. A 4-minute pilot talk on Friday 30 October.**
> All of it is development data: SpaceNet 8 Louisiana-East, Hurricane Ida, one after-image acquisition. Nothing sealed
> was read. No new scored run is needed for the slides.
>
> | Pilot result that already exists | Source | Method step it covers | Still to do |
> |---|---|---|---|
> | Flood labels are "yes" or missing, never "no". Flooded share: 2% on opaque-cloud tiles, 26% under thin cloud, 55% in clear sky | Evidence 01 | Q2's premise: a hidden road is "cannot assess", not "dry" (§2.1); the S4 and S5 ranges (§6.1 step 7) | H2b's within-tile test and its false-alarm check |
> | Masks against expert cloud labels (HRC_WHU, pixel level): bright precision 0.81, recall 0.28; dark precision 0.62, recall 0.68 (F1 0.48 on barren to 0.78 on vegetation) | Evidence 01 | Pass 1, "is the change a cloud?" (§6.4.2); a first look at S1 | S1 as the map's own rule, on 256-pixel patches (§6.1 step 3) |
> | Thin cloud costs flood calls: 67% of 24 trusted flooded roads found, against 87% in clear sky (Fisher p 0.010; the tile interval, −0.54 to +0.001, just reaches 0) | Evidence 01 | Why the handle step matters; S2's real recall (reported, not tested) | — |
> | Cloud rules compared: none changes accuracy significantly; tile rule + road rule adopted. Production: 83.0% on 798 roads (always "flooded": 55.3%) | Evidence 01 | The frozen map rule and Q2's comparator (§6.1, §7) | — |
> | Under uniform synthetic haze the mask is not biased against flooded roads: +0.1 points at thin haze; it flags flooded roads more under thick haze (+13.2 at t = 0.6) | Evidence 03 | The bed's crude control (§6.3); the X1 check | Families M, X and X-fast; ΔD and ΔU |
> | Noise floor: paired intervals about ±1.1–1.3 points on 798 roads; 24 roads can show only effects of about 25 points | Evidence 03 | Gate 0 (§9) | Block-bootstrap widths |
> | DINOv2 change cues add +1.2 points (p 0.035) | Evidence 01 | Pass 2's detector (§6.4.2) | — |
> | **Two-date de-hazing on real thin cloud:** trusted floods found 70.8% → 83.3% (He: 87.5%); 3 of 69 dry-labelled roads flipped (He: 16); clear roads +0.6 points (He: −4.0). Nothing is significant | Pilot (coordinator, 24 Oct); **exploratory** | Justin's two ideas as one loop: pass 1 finds the cloud, the "scale" step corrects it with the clear before date, pass 2 runs the frozen detector again (§6.4.2–§6.4.5) | The bed on families X and X-fast; vetoes 1 and 2; the 769-road safety screen; the sealed re-run; the before-cloudy direction; the finer-crop option |
>
> **Not covered by any pilot yet:** synthetic cloud and the realism tests (Q1); the after-only model (Q3); S1 as the map's
> rule; H2a; H2b's within-tile test; blocked folds; the sealed look.
>
> **Safe to say (inference):** cloud hides floods twice, in the image and in the labels. A two-date correction looks
> promising: on 24 trusted flooded roads it found 3 of the 7 missed floods, and it changed few other calls. These roads
> had already been looked at, so this is a pilot, not a result. The tests come next.
>
> **Not safe to say:** "significant"; "recovers floods" as a finding; "accuracy" for the 69 dry-labelled roads (their
> labels are untrusted); "better than He" (the two overlap, so do not rank them); "external"; anything new to the field.
>
> **One figure from existing code:** `show_refhaze` (before, hazy after, corrected after, t̂, and the pixels left out)
> on one thin-cloud tile, chosen by a fixed rule: the tile with the most trusted flooded roads under thin cloud, ties
> broken by tile id. Run it as a Tilt resource (project rule). On the slide, cite the haze model (He, Sun & Tang 2011)
> and the normalisation family (Canty & Nielsen 2008), both unverified.

### 15.2 Weeks

| Week | Dates | Work | Output | Gate |
|---|---|---|---|---|
| **0** | Sat 24 – Sun 25 Oct | **Assignment 4 slides** from existing results only (box 15.1); the one figure from existing code, via Tilt | Slides (due Sun 25 Oct) | — |
| **1** | 26 Oct – 1 Nov | **Pilot talk, Fri 30 Oct (4 min).** Rulings 1–4, one at a time (§19). Label-free counts: acquisitions and cloud patches; dark rise near the threshold on clear flooded and dry roads; visible share; building counts and `flooded` coding; HRC_WHU resolutions (or the fallback); the real thin level and rise bins; the top-10 cue list; the block size; the 1,080 label rows against 1,037 roads. Move `sn8_refhaze.py` and the pilot's scoring script into the repo, with tests, Tilt resources and the history log; §6.4's label-free diagnostics. CPU timing of the classical and texture cues, from the pilot run's logs. Library search starts (Lin et al. 2015 first). **Gate 0. Pre-registration frozen Sun 1 Nov** | Frozen pre-registration (both synthetic-truth branches); counts table; buildings in or out | **Gate 0** |
| **2** | 2 – 8 Nov | Q2's real-data parts: S1's tile-rule part on HRC_WHU (primary), H2a, H2b after its check, the real recall, ranges, anchored tipping counts; blocked folds the same week. Q3's clean results: after-only model, clean gap, mean-imputation arm, usefulness bar (CPU). The generator (X, X-fast, M, control; both placements; both dates) **frozen Fri 6 Nov**; Gate 0b. Buildings table only if in | Q2 real results; Q3 clean results; frozen generator | **Gate 1** (after-only go/no-go) |
| **3** | 9 – 15 Nov | Q1: ΔD, check 1, check 2, circularity flag (CPU). Bed DINOv2 passes start in the background, shaped family X first. §6.4 safety screen on the 769 clear roads' tiles, with the positive controls. Methods drafted from the pre-registration | Realism verdict on looks; §6.4 screen | **Gate 2** (realism binds Q2's tier names) |
| **4** | 16 – 22 Nov | The bed's 16 cells finish. Q1's ΔU and H1b. Q2's synthetic tier: S1's road-rule part, S2, S3. §6.4's formal tests: primary, vetoes, He, controls, X-fast, 128 m and IR-MAD variants, dose. Blocked folds the same week. Q2 and §6.4 results drafted | Q2 synthetic tier; §6.4 verdict | §6.4 vetoes |
| **5** | 23 – 29 Nov (Thanksgiving) | Q3: before-image cloud at opaque cover (primary), the leak check, H3a; H3b with its picture audit; thin levels if on time; H3c and §6.4's before-cloudy direction only if on time | Q3 results | Cut list applies |
| **6** | 30 Nov – 6 Dec | Q2 assembly: tiers, ranges, flooded length per area, provenance map. Buffered and leave-one-area-out runs. All development figures. Sealed widths re-checked; uninformative sealed tests named. **Everything frozen Fri 4 Dec**, with hashes | Frozen bundle | **Gate 3** (freeze) |
| **7** | 7 – 13 Dec | **The one batched sealed look, Mon 7 Dec**, logged once, with §6.4's sealed safety re-run. Results and discussion. Critic and validation agents check against the evidence. Justin verifies the references | Sealed results; full draft | — |
| **8** | 14 – 18 Dec | Revisions; limitations; AI-use, data and licence statements; Justin's final read. **Submit Fri 18 Dec** | Submitted paper | — |

**Why this is more realistic than v1 (inference).**
- Week 1 now holds the pilot talk, so Q2's real-data results move to week 2. Week 1 holds only label-free counts, code
  moves and the pre-registration (critic M21).
- **If week 1 slips,** the pre-registration slips to Wed 4 Nov, and nothing is scored before it is frozen.
- Buildings are decided on week-1 counts, not in week 3 (critic M21). **Default: out,** unless the counts pass.
- H3c and §6.4's before-cloudy direction run only if week 5 is on time.
- Results are drafted from week 4, as each part freezes, not all in week 7 (critic §9).
- The library search and Justin's reference check run in weeks 1–3, so prior work found late cannot force a reframe in
  week 7 (critic M21).

### 15.3 Gates

- **Gate 0 (week 1).** Power, as in §9. No cloud outcome is scored before the pre-registration is frozen.
- **Gate 0b (week 2).** At the generator freeze: covered-road counts in the shaped cell; one or two seeds for §6.4's
  primary.
- **Gate 1 (week 2).** If the after-only model fails its go/no-go, Q3 becomes: "the after image alone cannot map roads
  here; the two-date model's loss under before-image cloud is reported, with abstaining as the only fallback".
- **Gate 2 (week 3).** Realism does not stop the plan. It sets the tier names: if ΔD or ΔU fails, Q2's S2 and S3 are
  "range only", and the bed's numbers are a marked sensitivity result.
- **§6.4 vetoes (week 3 screen; week 4 bed).** If veto 1 fires on the screen, or veto 2 on the bed, §6.4 stops and its
  remaining GPU time returns to the plan.
- **Gate 3 (week 6).** Nothing is added after the freeze.

### 15.4 Cut list (critic M22; Justin may reorder)

If the plan slips, cut in this order:
1. H3c routing.
2. Buildings (already decided on week-1 counts).
3. §6.4's before-image direction.
4. The finer-crop option of Justin's second idea (§6.4.8).
5. Q3's thin levels (keep opaque cover).
6. The optional risk–coverage figure.
7. §6.4's after-image direction.

**Never cut:** the pre-registration; spatial-block intervals; the blocked-fold runs; **shaped placement, at least for
family X**; the sealed look and its decision rules; the provenance rule; the figures for the primary results.

### 15.5 Compute

*Inference from v3's timing: about 14 s of DINOv2 per tile, so about 45 min per grid cell over 190 tiles.*
- Q1's bed, 16 cells: about 12 h.
- §6.4: about 8 h (§6.4.11).
- Q3's four levels: about 3 h.
- Buildings, if in: the clean pass, about 50 min.
- The sealed look: 40 tiles × about 20 cells, about 3 h, plus §6.4's sealed re-run.
- The spatial option's heatmaps: under 30 min (a few tiles).
- **In all, about 27 h of DINOv2 time,** run in the background.
- **Not yet costed:** CPU time for the classical and texture cues on every clouded tile (critic M27). Measured in week 1
  from the pilot run's logs.
- The fold-scheme runs refit forests on cached cues, on CPU.

---

## 16. Stopping and decision rules

- **Stop rule.** No new statistic, grid cell, target, metric or fold scheme after looking at the outcome it would
  affect. Anything added later is labelled exploratory.
- **The pilot is exploratory.** Any change to the two-date method after the pilot is a named variant. The as-run arm
  stays primary (§6.4.4).
- **Both synthetic-truth branches are pre-registered** (critic M24).
  - With synthetic truth: as written.
  - Without it: S1 keeps only its tile-rule part; S1's road-rule part, "truly hidden" and check 2's placed-cloud scoring
    drop; Q1 keeps ΔD, ΔU and check 1. The bed's flood scores are unaffected, because they use published labels.
- **A failed gate changes the claim, not the rule.**
- **Production stays frozen** for the paper. Any confirmed gain found along the way (the two-date correction, say)
  goes through the staged-promotion rule after the paper, not during it.
- **The sealed look happens once,** with its decision rules (§3.5). Its results are reported whatever they are. Nothing
  is re-tuned afterwards.
- **One primary test per question.** Secondaries are Holm-adjusted within their question.

---

## 17. Checklist against the methodology role

| Required component (`methodology_agent.md`) | Where |
|---|---|
| 1. Unit of analysis | §4 |
| 2. Study area and temporal scope | §3.1, §3.2, §10.5 |
| 3. Dependent or target variables | §6 (each question's outcome; §6.4.6 for the handle step) |
| 4. Explanatory or predictor variables | §6 (exposure, arms, covariates); the flood model's cues are fixed (§1) |
| 5. Data provenance and resolution | §3.1, §10.1 |
| 6. Preprocessing | §0 (greyscale weights), §3.3 (Otsu thresholds), §6.3 step 1 (shapes), §6.4.3 (the correction) |
| 7. Model or algorithm | §1, §6, §6.4.3 |
| 8. Baseline or comparator | §7 |
| 9. Spatial train/test or cross-validation | §3.3, §3.4, §10.3 |
| 10. Uncertainty and sensitivity | §3.4, §9, §6.1 step 7 (tipping counts), §6.4.6 (robustness) |
| 11. External validation | §3.5. There is none unless Justin spends Germany. The sealed set is "held-out, same scene" |
| 12. Stopping and decision criteria | §8, §15.3, §16 |
| GeoAI checks: CRS, autocorrelation, leakage, scale, MAUP, sampling bias, transfer | §4, §10 |

---

## 18. Assumptions most likely to change the conclusion

1. **"Missing = dry" holds in clear sky.** The bed, Q3, S2 and S3 rest on it. Trees and shadow may hide floods in clear
   sky too. The visible-share run tests this where it is weakest.
2. **Synthetic cloud stands in for real thin cloud** (ΔD and ΔU). The real reference is one cloud field, so a pass is a
   pass against that one field.
3. **The bright tile rule's error on HRC_WHU stands for Maxar.** S1's only real test is on another imagery source.
4. **Blocks of at most 7 tiles capture the dependence.** If dependence is longer, every interval is too narrow.
5. **The proposed definition of change** (§2.1). If Justin rejects it, the statements are re-labelled.
6. **For §6.4: floods are a minority of each 64 m window.** Where flood fills most of the window, the fit can read it as
   haze and erase it. Veto 2 tests this.
7. **δ = 5 points is the right margin.** A margin a few points wider or narrower could move S2, S3 or §6.4 between
   "shown" and "not shown".
8. **HRC_WHU shapes can be rescaled to 0.5 m,** or the fallback shapes are close enough.
9. **Q3's opaque level depends little on realism** (v3). Opaque cloud removes the ground whatever its texture.

---

## 19. Unresolved issues and decisions for Justin

**Blocking decisions, one at a time on the request page, in this order** (critic §14):
1. **Synthetic truth** as a scoring truth. Both branches are pre-registered either way (§16).
2. **HRC_WHU outlines and cloud pixels** for the generator. If pixels are refused, family X uses procedural texture.
3. **Where §6.4 sits** (default: Q3d inside the handle step), **and the two-pass design's spatial option** (default:
   an exploratory figure only).
4. **The rules in §8 as revised:** the S1 ceilings, δ = 5 points, ΔD and ΔU as binding, the sealed decision rule, and
   whether S2 and S3 are co-primary (default: secondary).

**Defaults recorded for the rest** (Justin may change any; asked later, one at a time):
5. **The proposed definition of change** (§2.1). Default: used as proposed until he rules.
6. **The cut order** (§15.4). Default: the critic's.
7. **The sealed look:** add the north negative set? Germany? Default: neither. Ask by week 3.
8. **The main project's post-only result** (Hurricane Ian, dev log 2026-10-11) as evidence in Q3. Default: not used.
9. **HRC_WHU crops in a journal figure** (Google Earth imagery). Default: no HRC_WHU crops until the terms are clear;
   masks and plots only.
10. **The conference rule.** Default: AGENTS.md's rule (major conferences, labelled as conference papers).
11. **The target journal** (JIF ≥ 4).

**Matching edits needed in other files (not made here).**
- `selected_questions.md`:
  - Q2's "reliable means" → non-inferiority against clear sky within δ; the new "S1 fails" reading; the 95% wording.
  - Q3's "no" → decided at opaque cover only; the clean gap and the usefulness bar.
  - Q1's "no" → the ΔD rule, with ΔU binding.
- `abstract_v1.md`: the claim words in §12.1.
- **The pilot table should go into an evidence file** (for example `evidence/06_two_date_pilot.md`), written by the
  coordinator or Justin. Agents do not modify the evidence folder (AGENTS.md).

**Facts still unknown.**
- Each HRC_WHU image's resolution (the files do not store it).
- The number of cloud patches.
- The dark-rise distribution near the threshold on clear flooded and dry roads.
- The visible share on clear flooded and dry roads.
- Development building counts, their `flooded` coding, and SpaceNet 8's definition of a flooded building.
- The real thin level; the mixed-tile count (Q2b); the water group's size (H3b); the block size; the interval widths.
- The 1,080 label rows against 1,037 roads.
- The prototype's full settings history, and the pilot's scoring script and its "clear" rule for the 175 roads.
- §6.4's fallback share and low-variance share.
- The CPU time of the classical and texture cues.
- Whether evidence 03's haze script still exists.

**Citations still needed** (methods used here but not cited in the evidence files): the stratified exact test
(Mantel–Haenszel type); the semivariogram; the spatial block bootstrap; equivalence and non-inferiority testing; the
intersection–union rule; Bonferroni and Holm; the power approximation; mean imputation of a missing input; McNemar's
test. He, Sun & Tang 2011 was read at metadata level only. Olofsson et al. 2014 has no JIF recorded and its claim match
is unchecked.

- **Added 2026-10-24 (coordinator): which de-hazing arm is primary.** The as-run fit (v2 §6.4.4) or an
  IR-MAD/orthogonal fit pre-registered before bed scoring, given the label-free diagnostic before §6.4.6.

## 20. Suggested next scientific action

1. **Before Sunday:** build the Assignment 4 slides from box 15.1 only, with the one rule-chosen figure run through Tilt.
2. **The coordinator logs the pilot:** the scoring script into the repo, the settings history, the "clear" rule, and an
   evidence file for the table.
3. **Justin rules on decisions 1–4,** one at a time.
4. **Run the week-1 label-free counts through Tilt** (development data, no cloud outcome scored), then Gate 0.
5. **Write and freeze the pre-registration** by Sun 1 Nov, from §6, §8, §9 and §16, with the numbers filled in and the
   hashes recorded.
6. **Next workflow stage:** the validation agent checks v2's numbers against the evidence files and the files named in
   §0 (AGENTS.md rule 8). The methodology critic may re-score v2.

---

## 21. Change log: the methodology critic's changes and where they landed

### 21.1 The ranked changes (`methodology_review.md` §12)

| Rank | Critic's change | Where it landed | Status |
|---|---|---|---|
| **1** | Redefine S1 as the frozen map rule; test exactly that; pre-set what Q2 says if S1 fails; say the real half is on HRC_WHU (M5) | §6.1: the statements table (S1 = tile rule + road rule), step 3 (bright tile rule on 256-pixel HRC_WHU patches, pooled over urban, vegetation and water; the dark mask as a candidate only; the tier names the imagery), "What counts as no" (the S1-fails reading). §8: S1 rows re-justified, no longer anchored on the dark mask. S1 named as Q2's primary test | Accepted |
| **2** | One primary realism test for Q1 (X against the control, shaped placement, secondaries Holm-adjusted); a label-free use-level check; realism failure drops S2 and S3 to "range only" (M13, M14, M7) | §6.3: step 1 (M whole-tile = the control), step 2 (three fixed rise bins), step 3 (ΔD, shaped placement, within-tile effect), step 4 (ΔU), step 5 (secondaries, Holm), "What counts as no". §6.1 step 6 (binding). §8 rows | Accepted |
| **3** | Fix the sampling frame: one after acquisition; spatial-block intervals and blocked folds for tiers and primaries, in the same week; a sealed decision rule and minimum (M1, M2, M3) | §3.1 (acquisitions row), §3.2 (one cloud field; patch count; patch resampling), §3.3 (blocked folds in the same week; block side capped at 7; both-folds rule), §3.4 (block bootstrap; one wording), §3.5 (decision rule; minimum cloud; pooled HRC_WHU; "held-out, same scene"), §4, §10.2 | Accepted. Of "blocked only" or "both", "both" was chosen, to keep the logged production comparison |
| **4** | Pin down S2 and S3: one scored set; recall and specificity beside; non-inferiority against clear sky recomputed at Gate 0; "not shown" apart from "fails" (M6) | §6.1 step 5 (whole-tile cell, family X, real thin level; recall, specificity and flooded share beside), step 6 (non-inferiority within δ; shown / fails / not shown). §8 (δ = 5 points; reachability at Gate 0). §9 | Accepted |
| **5** | §6.4: freeze one method in code and log its history; implement the whole-tile gain-and-offset rule (or drop the cell); primary outcome "corrected roads meet Q2's ceilings"; a change-kept veto; the safety veto re-run sealed; read Lin et al. (2015) and use invariant-pixel weighting (M18–M20) | §6.4.3 (the method as run, with hashes, the freeze record and the history so far), §6.4.4 (every difference from v1, with reasons), §6.4.6 (primary within δ against clean calls; veto 2 at 0.8; positive controls; sealed re-run of veto 1; Gate 0 reachability), §6.4.10 (05's anchors), §3.5 | **Mostly accepted.** Two choices: (a) the whole-tile cell is **dropped** for this method rather than the rule implemented, so the formal test uses the code that ran; (b) the as-run fit is already an iterative invariant-pixel re-weighting, so it stays the primary, and the full IR-MAD form is a **named sensitivity variant**. Making an un-piloted variant the primary would be a choice made after the pilot. Lin et al. (2015) is read before the freeze; any change it prompts is a named variant |
| **6** | Close the H3a loophole (opaque only); add the clean information-cost gap and a usefulness bar (M10, M11) | §6.2 (arms: the mean-imputation arm; step 1: clean gap and usefulness bar; step 3: H3a at opaque only; "no" and the pre-set "beats a blinded model but abstain" answer). §8 rows | Accepted. The clean gap is a reported estimate, not a test |
| **7** | Re-order the cut list; protect shaped placement; decide buildings in week 1; place Justin's two-pass idea, with a rule that filled pixels are never scored (M22, M23) | §15.4 (the critic's order; shaped placement never cut); §8 and §15.2 (buildings on week-1 counts, default out); §6.4.1–6.4.2 (the two-pass design), §6.4.8 (the spatial option, exploratory, cut fourth); §2.1 and §6.4.9 (the filled-pixel rule) | Accepted |
| **8** | Test "missing = dry" where it is weakest: stratify by the tree and shadow visibility gate; anchor the tipping counts (M4) | §6.1 step 7 (visible-share sensitivity for S2, S3, H1b, H3a; tipping counts as shares of clear dry roads, beside two diagnostics); §8 row | Accepted |

### 21.2 Every issue (M1–M27)

| Issue | Where it landed | Status |
|---|---|---|
| M1 All real cloud from one after image | §3.1, §3.2, §10.2, §10.5, §12.1 | Accepted |
| M2 Sealed look: not external, not powered, no rule | §3.5; §9 (expected sealed widths); decision 7 | Accepted |
| M3 Dependence; absolute tiers | §3.3, §3.4, §6.1 step 6, §10.3 | Accepted ("both" folds) |
| M4 "Missing = dry" mechanism; unanchored tipping counts | §6.1 step 7 | Accepted |
| M5 S1 scores masks the map does not use | §6.1, §8 | Accepted |
| M6 S2 and S3 not pinned down | §6.1 steps 5–6, §8, §9 | Accepted |
| M7 Q1's verdict does not bind Q2 | §6.1 step 6, §6.3 "no", §15.3 Gate 2 | Accepted |
| M8 Much fixed by design; primary unclear; wording | §6.1 (empirical-or-fixed column; primary named; H2a renamed; range widths as results), §3.4 (one wording), §8 | Accepted. S2 and S3 secondary by default; Justin may promote them (decision 4) |
| M9 H2b identification | §6.1 step 4 | Accepted |
| M10 H3a "no" rule gives four chances | §6.2 step 3, §8 | Accepted |
| M11 Opaque comparator is a blinded model | §6.2 (mean-imputation arm; clean gap; usefulness bar) | Accepted |
| M12 Unmeasured water mask | §6.2 step 4 | Accepted |
| M13 Q1's pass rule cannot discriminate | §6.3 steps 1–3 | Accepted |
| M14 Realism tested on statistics, not use | §6.3 step 4 | Accepted |
| M15 Check 1's reference chosen by the mask | §6.3 steps 2–3 | Accepted |
| M16 Check 2 confounds size and thickness | §6.3 step 5 | Accepted |
| M17 No shape fallback | §6.3 step 1 | Accepted (procedural shapes with the opaque outlines' size spectrum) |
| M18 Prototype and plan disagree; it looked first | §6.4.3, §6.4.4, §6.4.5, §3.5 | Accepted, with the whole-tile cell dropped (see rank 5) |
| M19 Family X tilts the contrast; He is a weak bar | §6.4.6 (primary within δ; He secondary), §6.3 step 1 (air-light scale from real cloud; X-fast) | Accepted |
| M20 Guards miss before-cloudy, bright floods, large floods | §6.4.4, §6.4.6 (veto 2; positive controls; reachability), §6.4.7, §6.4.10 | Partly: the IR-MAD-style loop is kept as run; the full IR-MAD form is a variant (see rank 5) |
| M21 Weeks 1–2 overloaded; rulings on the critical path | §15.2 (pre-registration at the end of week 1; Q2 real parts moved to week 2; buildings on counts; library search in weeks 1–3), §19 (four blocking rulings first) | Accepted. The plan also absorbs Assignment 4 (week 0 and Fri 30 Oct) |
| M22 Cut order | §15.4 | Accepted as proposed |
| M23 Justin's second idea not placed | §6.4.1, §6.4.2, §6.4.8, §2.1 | Accepted: the two-pass design is placed in §6.4; its spatial reading is an exploratory figure |
| M24 Synthetic truth is a label question | §1, §16 (both branches), decision 1 | Accepted |
| M25 Claims wider than the tests | §12.1 | Accepted. The abstract needs the matching edit (§19) |
| M26 Licences and release | §3.6 | Accepted |
| M27 Smaller fixes | "Truly hidden" metric and coarse grid: §6.1 step 5. Greyscale weights: §0. CPU cost: §15.5 (measured in week 1). Second seed: §6.3 step 1. 1,080 rows: week 1. DINOv2 and Gemma roles: no change needed. Otsu thresholds inside folds: §3.3 | Accepted, except Otsu in the primary: **partly.** Production is frozen with its thresholds, and re-learning them changes which roads are scored. So a sensitivity run reports the leak's size instead |

**Nothing was rejected outright.** Three items were taken in a different form, each for a stated reason: "both" folds
(M3), dropping the whole-tile cell for §6.4 (M18), and the full IR-MAD form as a variant (M20). One was partly taken:
Otsu thresholds in the primary folds (M27).

---

## References (all unverified by Justin)

**From the input card:**
- Portalés-Julià et al. 2023, *Scientific Reports* 13:20316, DOI 10.1038/s41598-023-47595-7 (JIF 4.9). Separate
  "visible" and "flooded" outputs. (unverified)
- Qu, Li & Huang 2026, AnyTime-CD, *Remote Sensing of Environment* 334:115239, DOI 10.1016/j.rse.2026.115239 (JIF 12.3).
  Simulated cloud in change detection. (unverified)
- Song et al. 2023, DehazeFormer, *IEEE TIP* 32:1927–1941, DOI 10.1109/TIP.2023.3256763 (JIF 13.7; confirm in JCR). Its
  README's warning on synthetic haze. (unverified)
- Zou et al. 2025, Cloud-Adapter, *IEEE TGRS*, DOI 10.1109/TGRS.2025.3597410 (JIF 9.4). Frozen DINOv2 on HRC_WHU; context
  only. (unverified)

**From the evidence files (dataset and method attributions):**
- Hänsch et al. 2022, SpaceNet 8. The "only attribute what was visible" rule (evidence 01). Venue and JIF not in the
  files. (unverified)
- Li et al. 2019, HRC_WHU, *ISPRS JPRS* 150:197–212 (JIF 12.9, per evidence 02). (unverified)
- He, Sun & Tang 2011. Dark channel; family M; the masks; He de-hazing; the haze model behind the two-date method
  (evidence 01). Metadata only. (unverified)
- Olofsson et al. 2014. Reporting the cannot-assess share (evidence 02). JIF and claim match unchecked. (unverified)
- Geifman & El-Yaniv 2017. Selective classification, for the optional coverage figure (evidence 02). Conference paper.
  (unverified)
- Burgert, Ravanbakhsh & Demir 2022, *IEEE TGRS* 60 (JIF 9.4, per evidence 04). Synthetic noise justified against a
  cruder control. (unverified)
- Winiwarter et al. 2021, *Remote Sensing of Environment* (JIF 12.3, per evidence 04). Realism judged per use.
  (unverified)
- Hagolle et al. 2010, *Remote Sensing of Environment* (evidence 02). Two-date cloud detection; catalogue snippet only.
  (unverified)
- Makarau et al. 2014, *IEEE TGRS* (DLR; evidence 02). Haze thickness for uneven haze on VHR imagery; abstract only.
  (unverified)
- Nielsen 2007, IR-MAD, *IEEE TIP*, DOI 10.1109/TIP.2006.888195 (JIF 13.7, per evidence 05). Abstract. (unverified)
- Canty & Nielsen 2008, *Remote Sensing of Environment* 112(3):1025–1036, DOI 10.1016/j.rse.2007.07.013 (JIF 12.3, per
  evidence 05). Re-weighting by no-change probability. Abstract. (unverified)
- Du, Teillet & Cihlar 2002, *Remote Sensing of Environment*, DOI 10.1016/S0034-4257(02)00029-9 (evidence 05).
  Pseudo-invariant features. Abstract. (unverified)
- Lin et al. 2015, *ISPRS JPRS*, DOI 10.1016/j.isprsjprs.2015.05.003 (evidence 05). Invariant-pixel normalisation and
  cloud detection; the closest match. TLDR only. (unverified)
- Hagolle et al. 2015, *Remote Sensing* 7:2668, DOI 10.3390/rs70302668 (4.3, confirm in JCR; evidence 05). The
  stable-surface limit. Abstract. (unverified)
- Zeng, Shen & Zhang 2013, *Remote Sensing of Environment*, DOI 10.1016/j.rse.2012.12.012 (evidence 05). Between-date
  regression. TLDR. (unverified)
- Bruzzone & Bovolo 2013, *Proc. IEEE*, DOI 10.1109/JPROC.2012.2197169 (confirm in JCR; evidence 05). Nuisance against
  change of interest in VHR. Abstract. (unverified)
- Zhang, Peng & Huang 2017, *IEEE GRSL*, DOI 10.1109/LGRS.2017.2763182 (confirm in JCR; evidence 05); Han et al. 2024,
  C2F-SemiCD, *IEEE TGRS*, DOI 10.1109/TGRS.2024.3370568 (evidence 05). Coarse-to-fine designs. Abstracts. (unverified)
- Sui et al. 2024, DE and CUHK-CR, *IEEE TGRS*, DOI 10.1109/TGRS.2024.3411671 (evidence 05). Generated texture may not
  match the scene. (unverified)
- Arp et al. 2024, VPint2, *ISPRS JPRS*, DOI 10.1016/j.isprsjprs.2024.07.030 (evidence 05). Evaluation by transferring
  cloud masks onto clear images, the bed's design. Abstract. (unverified)
