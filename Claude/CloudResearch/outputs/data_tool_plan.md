# Data and tool plan: cloud in post-disaster change maps

Stage 6 of 8 of the Assignment 3 workflow (Data + Tool Agent). Claude wrote this on 2026-10-24, working alone, with no
sub-agents. It maps `outputs/methodology_v2.md` (the revised methodology) to datasets and computational tools. It also
covers the AI-assisted coding and analysis tools, and what Justin must check by hand.

- **No new results.** I ran no model and scored nothing. I read code, documentation, file names, file sizes and one
  column header. No imagery, mask, label or outcome was read.
- **No downloads.** Nothing was downloaded. Three public pages were read to confirm licences (§1.3).
- **No sealed file was opened.** Section 1.2 lists exactly what I looked at.
- **Same model.** Every agent in this workflow runs on the same model. Where this plan agrees with the methodology or
  its critic, that is not independent validation (AGENTS.md rule 4).

Tags:
- **Evidence:** found in a file or on a page. The source is named (file and section, or URL).
- **Inference:** my reasoning or my estimate. It has not been measured.
- **TO VERIFY (Vn):** uncertain. Each one is listed in §6.1 with what would settle it.

---

## 1. Inputs used and assumptions

### 1.1 Files read

- **Role and rules:** `05_Project/agents/data_tool_agent.md`; `05_Project/AGENTS.md`.
- **Problem and decisions:** `CloudResearch/input_card.md`; `CloudResearch/decision_log.md`.
- **Questions:** `outputs/selected_questions.md` (Q2 leads, then Q3, then Q1).
- **The plan mapped here:** `outputs/methodology_v2.md`, read in full, including the label-free diagnostic added before
  §6.4.6 and the open decision in §19 on which de-hazing arm is primary.
- **The critique:** `outputs/methodology_review.md`, sections 0–2, M17, M26, M27, 9, 13 and 14 (the data, tool and
  feasibility points). The other sections were scanned by heading only.
- **Evidence:** `evidence/01_measured_results.md`, `02_cloud_literature_summary.md`, `03_pre_refinement_checks.md`,
  `05_reconstruction_literature.md`, all in full. The pilot scripts in `evidence/pilot_scripts/`: `evaluate.py`,
  `diag_core.py`, `evaluate.log`, `evaluate_v1_polyfit.log`, the header of `refhaze_calls.csv`, and the imports of
  `figures.py` and `slide_panels.py`.
- **Existing code (read only):** the module docstrings and top-level names of every `ProjectBranch/ClaudeFunctions/*.py`;
  `sn8_refhaze.py` and `sn8_cloudref.py` in full; `sn8_heldout.py` from line 20; parts of `sn8_clouds.py`,
  `sn8_dino.py`, `sn8_stages.py`, `sn8_models.py`, `sn8_data.py`, `sn8_texture.py`, `sn8_detect.py`, `sn8_cutoff.py`,
  `sn8_results.py`. The registry `ProjectBranch/Code/results/production.json`, in full.
- **Project rules and records:** `ProjectBranch/README.md`; `Project/CLAUDE.md` (it loaded when I opened the project's
  docs); `Project/docs/datasets/data_budget.md` (the sealed-data ledger); `open_data_manifest.md` (lines 1–71, licence
  records); `open_damage_datasets.md` (a keyword search for licences and open sources); the head of `Project/Tiltfile`
  and `tilt/scene_cloud.tiltfile`; the education agent's briefing
  (`~/Claude/Learning/RemoteEarthImagery/image_processing_course/AGENT_BRIEFING.md`), searched for cloud, haze and
  normalisation rules, as `Project/CLAUDE.md` requires before an image-processing step is designed.
- **Dataset documentation on disk:** the READMEs of `ProjectBranch/Images/SN8_Louisiana-East_Ida2021/` and
  `SN8_Louisiana-East_Ida2021_greyscale/`; the HRC_WHU documentation PDF (text only).

### 1.2 Read-only checks made today, and their limits

| Check | What I saw | What I did not do |
|---|---|---|
| `ls` of `ProjectBranch/Images/` | Folders `Cloud_References/`, `Sealed Images/`, `SN8_Louisiana-East_Ida2021/`, `SN8_Louisiana-East_Ida2021_greyscale/` | Did not list inside `Sealed Images/` |
| `ls` of the greyscale copy | Sub-folders `train`, `val`, `test`, `negative`, plus `tiles.csv` and `README.md` | Did not list or open `test/` or `negative/` |
| `du -sh` | Raw SN8 folder 3.9 GB; greyscale `train` 364 MB, `val` 78 MB; HRC_WHU 557 MB | No size of any sealed folder |
| Column header of the greyscale `tiles.csv` | `tile_id, split, region, flood_class, roads, roads_flooded, buildings, buildings_flooded, pre, post, label` | **No row was read.** The file holds rows for the sealed `test` and `negative` tiles too (see §3.2 D7) |
| HRC_WHU folder | `data/HRC_WHU/` holds 300 files; a documentation PDF; `List of training and test data.txt`; `source/HRC_WHU dataset.rar` (176,765,748 bytes) | No image, mask or list row opened |
| HRC_WHU documentation PDF (text) | "resolution varying from 0.5 to 15 m", "shared for academic purpose only", no per-image resolution | — |
| Model folder | `~/Masters/models/huggingface/hub/models--timm--vit_large_patch14_reg4_dinov2.lvd142m/snapshots/*/model.safetensors`, 1,217,515,128 bytes | — |
| `~/.cache/huggingface` | 506 MB of `docling` models (not this project's) | Did not move or change anything |
| Python environments (`pip list`) | Base Miniconda Python 3.14.7 (`/opt/miniconda3/bin/python3`) and `Project/.venv` (Python 3.12.2); MPS available in base | — |
| `df -h ~` | 29 GB free of 228 GB (87% used) | — |
| Cache folder `ClaudeFunctions/.cache` | 35 files, 200 MB; the corrected-cue tables are about 513 KB each (268 roads, 98 columns) | No feature value read |
| `sha256` | `sn8_refhaze.py` `ff5a09bb…`, `sn8_clouds.py` `6b64958d…`, the same as methodology v2 §0 | — |
| A file search for `mask_bias.py` | Found only in this session's scratchpad (§4.2) | — |

### 1.3 Web pages read (public pages only; no login)

1. https://huggingface.co/datasets/csaybar/CloudSEN12-high: the card's licence field is `cc-by-nc-4.0`.
2. https://www.usgs.gov/landsat-missions/landsat-8-cloud-cover-assessment-validation-data: no licence stated; data
   citation doi:10.5066/F7251GDH.
3. https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits: "USGS-authored or produced data
   and information are considered to be in the U.S. Public Domain."

### 1.4 Assumptions

1. Methodology v2 is the plan to map. Where it is open (synthetic truth, HRC_WHU use, §6.4's place, the primary
   de-hazing arm), I map every branch and choose none.
2. Production stays frozen during the paper (v2 §16). No tool here retrains or promotes it.
3. The roads side test keeps its own code base (`ProjectBranch`, private repo Jrog378/GeoAI-Roads; evidence 01) and the
   main project's rules (`Project/CLAUDE.md`): Tilt for every run, a log entry after each step, pictures with every
   number.
4. "Exists" means the code is in `ProjectBranch/ClaudeFunctions/` or the evidence folder today. "Must be written" means
   it is not there. Sizes ("small", "medium") are my estimates (inference).
5. Compute figures marked "inference" are mine. The ones with a log behind them say so.

---

## 2. Requirement → dataset/tool map

One row per methodology step, in v2's order. "Exists" names the code that does it today. "New" is what must be
written. Datasets are named by their code in §3 (D1–D8). The last column says what is specific to this event, sensor or
target. Under the universality rule (input card) those values belong in a task file, not in the code.

| # | Step (v2 §) | Requirement | Data | Exists | New | Event-specific parts |
|---|---|---|---|---|---|---|
| R1 | §2.1 | Per-pixel provenance: observed, corrected, filled, not observed; a filled pixel never votes; a road is callable below 20% "not observed" | D1 | `sn8_clouds._maps` (dark-rise mask); `sn8_refhaze.reference_dehaze` (haze rule; `used` pixels) | Provenance raster and per-road shares; a code check that no filled pixel reaches a cue | None in the rule. The 20% cut is the road rule's |
| R2 | §3.1 | Development tiles, labels and HRC_WHU development images | D1, D2, D3 | `sn8.tile`; `sn8_data.guard_split`, `check_split`; `sn8_grey`; `sn8_torchgeo.tile_pair`; `sn8_coreg`; `sn8_cloudref` | — | SN8 file layout; tile ids `<area>_<column>_<row>`; UTM 15N |
| R3 | §3.2 | Acquisition table; cloud-patch count (label-free) | D7 mapping file (development rows only); D1 masks | `sn8_clouds.cloud_table` (tile shares); `neighbour_check` (tile-grid logic) | Tile-grid raster from tile ids; connected groups with `scipy.ndimage.label` | The tile grid |
| R4 | §3.3 | Primary folds: 5 by tile, seed 662 | D1 | `StratifiedGroupKFold(5, shuffle=True, random_state=662)` as in `evaluate.py` | — | — |
| R5 | §3.3 | Blocked folds; block side from the semivariogram of tile flood share (3–7 tiles) | D1, D2 (development only) | scikit-learn `StratifiedGroupKFold` (groups = block id) | Empirical semivariogram of tile flood share and a range fit (NumPy, SciPy); block assignment | Block side is in tiles of about 550 m |
| R6 | §3.3 | Otsu thresholds re-learned inside folds (sensitivity) | D1 training tiles | `sn8_clouds.cloud_thresholds` (all training tiles, cached) | Per-fold variant; count of roads that change status | Thresholds are scene- and sensor-specific |
| R7 | §3.4 | Spatial block bootstrap (primary); tile bootstrap; patch bootstrap; McNemar (secondary); Holm | Calls | `paired_report`, `held_out_report`, `gated_report` (tile bootstrap; McNemar by `scipy.stats.binomtest`) | Block, patch and HRC_WHU image-within-type bootstraps; Holm step-down | — |
| R8 | §3.5 | One batched sealed look, logged first; decision rules; minimum cloud | D6 (sealed) | Guards: `sn8.tiles(allow_sealed=…)`, `guard_split`, `_tile(allow_held_out=…)`, `hrc_images(allow_held_out=…)` | One sealed-look script, the only place a guard flag is set; expected-width calculator; ledger entry | — |
| R9 | §3.6 | Licences, credits, release of code and seeds only | D1, D3 | `sn8_lines.CREDIT`; `sn8_cloudref.CREDIT` | Data statement; credit lines on every figure | Per dataset |
| R10 | §6.1 step 1 | Fit once; each fold model also calls its own fold's hidden roads | D1 | `gated_calls`; the pattern in `evaluate.py` (one fit per fold, every arm predicted) | Extend to opaque-tile roads; store every call with its fold id | — |
| R11 | §6.1 step 2; §8; §16 | Freeze the rules and the code before scoring | — | `sn8_results.code_hashes`, `new_run`, `save_run`; `production.json` | Pre-registration file with hashes, including scripts outside `ClaudeFunctions` | — |
| R12 | §6.1 step 3 | **S1 tile-rule part on HRC_WHU 256-pixel patches (Q2 primary)** | D3 (120 development images; 72 in urban, vegetation and water) | `sn8_cloudref.hrc_image`, `single_date_masks`, `bright_mask`, `mask_scores` | Patch cutter; "flagged" and "truly hidden" rules; per-image bootstrap within type; resolution bands if V1 is settled | Bright mask (grey > 200, local SD < 10) is tuned to 8-bit Maxar |
| R13 | §6.1 step 4 | S2 real recall on the 24 trusted flooded roads | D1 | `evidence/pilot_scripts/evaluate.py`, `refhaze_calls.csv` | Move into the repo; re-run with blocked folds | — |
| R14 | §6.1 step 4 | H2a: score the same calls on 798 and on 1,037 roads | D1, D2 | `gated_report` | Q2a decision rule | SN8's "yes or missing" coding |
| R15 | §6.1 step 4 | H2b: near-threshold check; stratified exact test; 50 m core sensitivity | D1 (dark rise per road), D2 | `cloud_table`, `lines_cloud` (`dark_rise_road`) | Near-threshold plot; stratified exact test (statsmodels is not installed; V18); distance to an opaque core (`scipy.ndimage.distance_transform_edt`) | 50 m; SN8 label coding |
| R16 | §6.1 step 5 | S1 road-rule part on the bed (shaped placement) | D5 | `sn8_clouds._maps`, `lines_cloud` (re-run on clouded after images) | Bed runner; "truly hidden" rule | 20% cut; 20 m window set in pixels |
| R17 | §6.1 step 5 | S2, S3: one scored set (whole-tile, family X, real thin level) | D5 | Fold models; `corrected_rows` pattern | Bed runner; paired error difference; recall and specificity | — |
| R18 | §6.1 step 6 | Tiers: non-inferiority within δ; shown / fails / not shown; both fold schemes | Calls | — | Tier scorer | δ = 5 points is a user judgement (task file) |
| R19 | §6.1 step 7 | S4, S5 ranges; tipping points; "too wide" flag | D2 (road lengths) | `pyproj`, `shapely` installed; `length_m` in SpaceNet's reference CSV (README) | Bounds; tipping counts; range-width flag | — |
| R20 | §6.1 step 7 | "Missing = dry" sensitivity by visible share | D1 before images | `sn8_detect.road_visibility`; `sn8_cutoff.oof_visibility`; `visibility_test.ipynb` | Stratified re-run of S2, S3, H1b, H3a | Road detector trained on SN8 |
| R21 | §6.1 step 7 | Share of clear "dry" roads inside a flooded building's 10 m ring | D2 buildings | `sn8_roads.RING_M` (10 m; roads) | Building ring overlay | Target-specific |
| R22 | §6.1 step 8 | Provenance map; optional risk–coverage curve | All | matplotlib; `sn8_results.show_calls_map` | Provenance map; risk–coverage | — |
| R23 | §6.2 step 1 | After-only model; clean gap; Gate 1; usefulness bar; mean-imputation arm; no-DINOv2 arm | D1 (`_after` cue columns exist) | `sn8_models.tuned_random_forest`; `sn8_stages.production_features` | Column selectors; mean imputation inside folds | The hazard must be readable from one image |
| R24 | §6.2 step 2 | Cloud the before image only; leak check | D5 (before-image mode) | `sn8_refhaze._corrected_pair` (after image only) | Before-image variant of the runner; an assertion that after-only calls do not change | — |
| R25 | §6.2 step 3 | H3a at opaque cover; secondary levels with Holm | D5 | `paired_report` | Holm | — |
| R26 | §6.2 step 4 | H3b: permanent-water mask (label-free, threshold set on training tiles); 30-road picture audit | D1 clear before images | `skimage.filters.threshold_otsu`; `dark_channel` | Water mask; ring overlap; audit sheet (seed 662) | Flood-specific |
| R27 | §6.2 step 5 | H3c routing flag (fall of the dark floor + smoothness) | D1, D5 | `dark_channel` | Flag; Otsu inside folds | Flood-specific |
| R28 | §6.2 step 6; §8 | Buildings go/no-go on week-1 counts | D2; D7 `tiles.csv` building columns (**development rows only**) | `sn8_data.label_counts`; `tiles.csv` columns | Clear-building count (needs building masks); building strip and ring cues (roads only today) | Target-specific |
| R29 | §6.3 step 1 | **Generator:** families M, X, X-fast, uniform control; shapes; texture; placements; two seeds; freeze | D3 masks and cloud pixels (pending ruling 2); D4 (17 opaque cores) | `mask_bias.py` (uniform haze; scratchpad only); `bright_mask`; `skimage.measure.regionprops` | Generator module, settings file and hash; procedural shapes and noise (NumPy FFT) as fallbacks | Air light, edge fall-off and size spectrum are scene- and sensor-specific |
| R30 | §6.3 step 2 | Real thin level; three rise bins (label-free) | D4 thin-cloud pixels | `cloud_maps` | Median rise; tertiles | Scene-specific |
| R31 | §6.3 step 3 | **ΔD (Q1 primary):** contrast kept, pattern kept, patchiness; within-tile real effect | D1 clear tiles + D5; D4 | `sn8_texture.semivariogram` (V8) | Three statistics in 14-pixel cells and 64-pixel windows; ΔD with block × patch bootstrap | — |
| R32 | §6.3 step 4 | ΔU: top-10 cues and flood probability, matched on before-image cues | D5 cues; 93 real strips | Random forest `feature_importances_`, `predict_proba` | Matched-strata distances; ΔU | Cue list is model-specific |
| R33 | §6.3 step 5 | Check 1 margins; check 2 (paste into HRC_WHU; edge bands; matched area); circularity flag on M | D3 | `single_date_masks`, `mask_scores` | Paste tool (shapes from other images); edge-band recall | — |
| R34 | §6.3 step 6 | Bed grid (16 cells); H1b; X1 recheck | D1 (190 clear tiles), D5 | `corrected_rows` (all cues, DINOv2 included); the `evaluate.py` fold pattern | Grid runner; H1b | — |
| R35 | §6.4.2 | Pass 1 (masks), scale (two-date fit), pass 2 (frozen detector) | D1 | `sn8_clouds` masks; `reference_dehaze`; `corrected_rows`, `corrected_table` | Provenance (R1) | Sign rule assumes the hazard darkens; 64 m window set in pixels |
| R36 | §6.4.3 | Freeze record; cache key; tests in code; label-free diagnostics per run | — | `code_hashes`; `diag_core.py` (pilot) | Cache key that also hashes `dark_channel` and `cloud_thresholds`; two label-free tests; four diagnostics | — |
| R37 | §6.4.5; §19 | **Primary de-hazing arm: (a) as run, or (b) IR-MAD / orthogonal fit** | D1 | (a) exists; (b) only an orthogonal slope inside `diag_core.py` | (b) module, if pre-registered | See §4.7 |
| R38 | §6.4.6 | Formal tests: six arms, veto 1, veto 2, positive controls, recovery, robustness, dose, provenance, real-cloud re-run, Gate 0b | D5 shaped cells; 190 clear tiles; 39 thin tiles | `corrected_table(…, "refhaze" / "dehaze" / "none")` (the identity arm) | Fill-from-before arm; change-kept measure; X-fast; 128 m window; Gate 0b counter | — |
| R39 | §6.4.7 | Before-cloudy direction (exploratory) | D5 | — | Variant with the dates' roles swapped | — |
| R40 | §6.4.8 | Finer crops: DINOv2 heatmaps at 7 m and 3.5 m (figure only) | D5, a few tiles | `sn8_dino.tokens`, `show_dino` | 2× upsampled crops | — |
| R41 | §9 | Gate 0: block widths, patch count, scored-set sizes, reachability of δ, sealed widths | Logged calls | Bootstrap code above | Expected-width and smallest-difference calculator | — |
| R42 | §10.3 | Buffered folds; leave-one-area-out (week 6) | D1 | scikit-learn `LeaveOneGroupOut`, `StratifiedGroupKFold` | Buffer rule | "Area" = before acquisition |
| R43 | §14 | Figures with every number; crops picked by preset rules | Development only | `figures.py`, `slide_panels.py` (pilot); `show_*` functions | `cpu_only` Tilt figure resources | Credit lines |
| R44 | §15.2 | Week-1 label-free counts (one task list) | D1, D2 (development only), D7 | R3, R15, R20, R28, R30, R32, R5 | The 1,080 label rows against 1,037 roads; timing per stage | — |
| R45 | §15.5 | Compute timing, GPU passes in the background | — | Pilot logs (§4.11) | A timed run per stage | — |
| R46 | §13; §15 | Every run as a Tilt resource, logged with hashes | — | `Project/tilt/lib.tiltfile` (`track_script`); `sn8_results` | `tilt/roads_cloud.tiltfile` (none exists for the roads side test) | — |

---

## 3. Datasets

### 3.1 Summary

| Code | Dataset | Role | On disk? | Path | Size |
|---|---|---|---|---|---|
| D1 | SpaceNet 8 Louisiana-East, development tiles (186 train + 40 validation) | **Primary** | Yes | `ProjectBranch/Images/SN8_Louisiana-East_Ida2021/` (raw, all 599 tiles); `…_greyscale/train`, `…/val` | 3.9 GB raw; 364 + 78 MB grey |
| D2 | SpaceNet 8 labels on D1 (roads; buildings) | **Primary** (published human labels, unmodified) | Yes | `…/labels/<tile>.geojson`; `…/source/` CSVs | Inside D1 |
| D3 | HRC_WHU development images (120) | **Validation** (S1, check 2); generator source if ruling 2 allows | Yes | `ProjectBranch/Images/Cloud_References/HRC_WHU/` | 557 MB (archive + extracted) |
| D4 | Real-cloud layers derived from D1 (17 opaque tiles, 39 thin-cloud tiles, cloud patches) | **Reference** for Q1; generator settings | Derived on demand | From `sn8_clouds` | — |
| D5 | Synthetic test bed (clouded copies of clear D1 tiles) | **Primary** for Q1's bed, Q2's synthetic tier, Q3, §6.4 | Not yet built | Cue tables only (§4.11) | — |
| D6 | Sealed pools: SN8 test 40 tiles; north negative 333 tiles; Germany 202 tiles; Louisiana-West 406 tiles; HRC_WHU test 30 images | **Sealed** | Yes (never opened) | `…_greyscale/test`, `…/negative`; `Images/Sealed Images/`; HRC_WHU test list | Not measured |
| D7 | Metadata on disk (mapping CSV, `tiles.csv`, split files, `resolutions.txt`) | Support | Yes | See D7 | Small |
| D8 | Not used by default (main project's Hurricane Ian post-only result; LEVIR-CD; Gemma output) | Excluded | Some on disk | — | — |
| O1–O9 | Open-licence alternatives for release | **Control / release route, later** | No | — | §3.3 |

### 3.2 Dataset cards

#### D1. SpaceNet 8 Louisiana-East, development tiles (primary)

| Field | Value |
|---|---|
| Provider | SpaceNet LLC; imagery Maxar (SN8 README; evidence 01) |
| Content | Before and after RGB images per tile, 8-bit GeoTIFF; used in greyscale after the first step (BT.601: 0.299 R + 0.587 G + 0.114 B; `sn8_grey.py`; v2 §0) |
| Spatial resolution | Before about 0.39–0.52 m, after about 0.31–0.79 m, by satellite (SN8 README). Warped to one 0.5 m UTM 15N grid by TorchGeo (`sn8_torchgeo`; evidence 01). After-to-before ground shift about 0.6 m after co-registration (evidence 01) |
| Temporal resolution | One after acquisition for all 226 tiles (`10300100C46F5900`). Two before acquisitions: area 0 (`105001001A0FFC00`, 105 tiles), area 2 (`10300100AF395C00`, 121 tiles) (critic §2). No tile has a second after image (SN8 README). Acquisition dates: **TO VERIFY (V4)** |
| Geographic coverage | Louisiana-East after Hurricane Ida (2021): south (area 0) and west (area 2) scenes; tiles about 550 m square (SN8 README; `sn8_data`) |
| Access | On disk. Downloaded 2026-10-15 from the public bucket `s3://spacenet-dataset/spacenet/SN8_floods/Louisiana-East_Training_Public/`; size and md5 checked (`manifest.tsv`; SN8 README) |
| Licence / constraints | CC BY-SA 4.0 (SpaceNet LLC; imagery Maxar). Research-only under the project's open-source rule: anything tuned on it is research-only (SN8 README; input card). Share-alike also applies to the greyscale copy (its README) |
| Expected preprocessing | Greyscale; warp to the shared grid; histogram-match after to before for the classical cues (`sn8_lines`); co-registration shift (`sn8_coreg`); valid mask eroded 6 px (`sn8_clouds._tile`); **no data is 0, but every before image declares 255 as no data**, so readers must override it (`SN8Image.nodata = 0`; SN8 README) |
| Known limitations | All real cloud is one cloud field (one after acquisition; v2 §3.2). Area = before acquisition. Neighbouring tiles fall in different folds (225 of 226 have a development neighbour; critic §2). Cloud clusters in areas 0 and 2 (v2 §10.5). The raw folder holds **all 599 tiles**, sealed ones included; only the loaders' guards keep them out |
| Role | Primary (development) for Q1, Q2, Q3 and §6.4 |
| On disk vs not | On disk: raw images, labels, source CSVs; the greyscale development copy; cached cue tables (`ClaudeFunctions/.cache`, 200 MB). Not built: D5 |
| Open-licence alternative | O1 (NOAA after imagery) + O2 (NAIP before imagery). **TO VERIFY (V11, V12)** |

#### D2. SpaceNet 8 labels on the development tiles (primary truth)

| Field | Value |
|---|---|
| Provider | SpaceNet 8 analysts; road geometry from OpenStreetMap (SN8 README: roads carry OSM tags such as `way/…`, `highway`) |
| Content | Road centrelines (LineString) and building polygons. `flooded` is "yes" on flooded objects; otherwise left out, never "no" (evidence 01: 487 "yes", 593 missing). Analysts were told to "only attribute what was visible" (Hänsch et al. 2022, p. 3; evidence 01). Pixel copies in `source/Louisiana-East_Training_Public_reference.csv` with `length_m` for roads (SN8 README) |
| Spatial resolution | Vector, CRS84 (lon/lat) in the GeoJSON (SN8 README). Scored as the road strip (about 5 m either side) and a 10 m ring (`sn8_roads`) |
| Temporal resolution | One label state per tile, for the after date |
| Geographic coverage | As D1. 1,037 touched roads on 217 tiles (evidence 01) |
| Access | On disk with D1 |
| Licence / constraints | As D1 (CC BY-SA 4.0). OSM-derived geometry: OSM is ODbL, a share-alike licence (project survey, `open_damage_datasets.md`) |
| Expected preprocessing | None to the labels (rule: published labels, unmodified). Reprojection to UTM for strips (`sn8_lines._TO_UTM`) |
| Known limitations | Under cloud a "flooded" label can be trusted and a missing label cannot (evidence 01). 1,080 label rows against 1,037 roads is unexplained (v2 §19). SpaceNet 8's definition of a flooded building is not in the files (**V10**) |
| Role | Primary truth for every flood score. Never used to set the generator |
| Open-licence alternative | No openly licensed flood-road labels for Ida were found in the files (**V14**). Road geometry: TIGER roads, "not copyrighted" per the project survey (O3, **V13**). Building damage: FEMA's Ida crowd labels exist, but their licence is unclear (project survey, card S21) and they are buildings, not roads |

#### D3. HRC_WHU development images (validation; possible generator source)

| Field | Value |
|---|---|
| Provider | SENDIMAGE Lab, Wuhan University (Li et al. 2019, *ISPRS JPRS* 150:197–212; JIF 12.9 per evidence 02; unverified by Justin) |
| Content | Google Earth RGB images, 1280 × 720 px, with expert cloud masks (`*_ReferenceMask.tif`). Thin cloud is cloud only where the ground cannot be seen clearly; no shadows labelled (evidence 02; `sn8_cloudref.py`) |
| Spatial resolution | 0.5–15 m, varying by image (dataset PDF on disk). **Per-image resolution is not in the files or the PDF (V1)** |
| Temporal resolution | Single date per image. Acquisition dates not given (inference: Google Earth mosaics may also be composites) |
| Geographic coverage | "Different global regions"; 30 images in each of five land-cover types: water, vegetation, urban, snow, barren (`sn8_cloudref.py`). The PDF's sentence names six types ("water, vegetation, wetlands, urban, snow/ice, and barren") while saying five (**V2**) |
| Access | On disk. Downloaded 2026-10-23 from the authors' link with Justin's OK; archive 176,765,748 bytes, sha256 `e161ff380e0b11bf…` (`data_budget.md`). Mirror `hrc_whu.zip` on Hugging Face, 115.5 MB, as 256 × 256 patches (evidence 02) |
| Licence / constraints | "Shared for academic purpose only" (dataset PDF; no licence file). Mirror card CC-BY-NC-4.0 (evidence 02). Imagery from Google Earth: figure use is open (decision 9; **V3**) |
| Expected preprocessing | BT.601 greyscale (as SN8; v2 §0). 256 × 256 patches for S1. Shapes rescaled to 0.5 m by each image's resolution (blocked by V1), or the procedural fallback (v2 §6.3 step 1). Resolution bands or a 2 m cap for check 2 |
| Known limitations | Not Maxar, not 0.5 m throughout: the masks' windows are set in pixels for 0.5 m, so a 41-pixel window spans about 600 m at 15 m (v2 §10.1). Single date: the two-date dark-rise mask cannot be checked here (evidence 01). 24 development images per type (critic §2) |
| Role | Validation: S1's real-cloud test (Q2 primary), check 2. Generator source for shapes and texture only if Justin allows it (ruling 2). The 30 test images are sealed (D6) |
| Open-licence alternative | No openly licensed cloud labels at 1 m or finer were found (evidence 02 §3, citing the OpenSICDR catalogue). Coarser candidates in O5–O8. For the generator, the procedural fallback needs no data licence (O9) |

#### D4. Real-cloud layers derived from D1 (reference; label-free)

- **Content.** The bright-mask cores of the 17 opaque tiles (at least 20% bright cloud; 146 roads, 3 labelled flooded);
  the 39 thin-cloud tiles (93 roads at ≥ 20% dark rise; 24 labelled flooded); cloud patches, counted in week 1 (v2 §3.1,
  §3.2; evidence 01).
- **Uses.** Air light, edge fall-off and size spectrum for the generator (v2 §6.3 step 1); the real thin level and rise
  bins (step 2); the real side of ΔD and ΔU (steps 3–4).
- **Limits.** One acquisition. Picked by the masks, so the real reference is mask-selected (critic M15). If fewer than 10
  patches, real-cloud quantities are described, not tested (v2 §3.2).
- **Tools.** `sn8_clouds.cloud_maps`, `bright_mask`, `dark_channel`; `skimage.measure.label`/`regionprops` (installed).
- **Licence.** Derived from D1, so CC BY-SA, research-only (inference).

#### D5. Synthetic test bed (generated; primary for the bed)

- **Content.** Clear held-out development tiles (190 tiles, 769 clear roads; evidence 03) with synthetic cloud added to
  the after image (Q1, Q2, §6.4) or the before image (Q3). Families M, X, X-fast and the uniform control; whole-tile and
  shaped placement; four levels; seeded (v2 §6.3).
- **Truth.** Published labels (D2) on clear roads. The placement map is the "synthetic truth" only if Justin allows it
  (ruling 1; both branches pre-registered, v2 §16).
- **Storage.** Cue tables only; bed images are regenerated from the seed, not stored (§4.11; inference).
- **Licence.** Mixes D1 with D3 cloud material if ruling 2 allows. A derived image takes the stricter terms, so code and
  seeds are released, not images (v2 §3.6).

#### D6. Sealed pools (never opened; not counted here)

| Pool | Size (tiles or images) | Where | May be opened by |
|---|---|---|---|
| SN8 Louisiana-East test | 40 tiles (south 22, west 18; v2 §3.5) | `…_greyscale/test/`; raw files mixed into `SN8_Louisiana-East_Ida2021/` | The one sealed look (Mon 7 Dec), through `allow_held_out=True` |
| SN8 north negative set | 333 tiles | `…_greyscale/negative/` | Justin's call (decision 7) |
| SN8 Germany | 202 tiles | `Images/Sealed Images/` | Justin's call (decision 7) |
| SN8 Louisiana-West | 406 tiles, no labels | `Images/Sealed Images/` | Never used (v2 §3.5) |
| HRC_WHU test | 30 images (6 per type) | HRC_WHU folder, authors' test list | The one sealed look, `hrc_images("test", allow_held_out=True)` |

- **Rule for this plan.** I record sizes only. The ledger (`data_budget.md`) holds disclosed class totals for some of
  these pools. This plan does not repeat them, and no tool may use them for a cut-off, prior or rule.
- **Cloud in the sealed tiles** is counted only inside the look, with the frozen masks (v2 §3.5).

#### D7. Metadata on disk (support; with guards)

| File | Use | Guard Justin should check |
|---|---|---|
| `SN8_Louisiana-East_Ida2021/source/Louisiana-East_Training_Public_label_image_mapping.csv` | Acquisition ids per tile (R3) | Filter to the 226 development tiles **before** printing. The critic's `head` preview showed one north-set row (critic §0) |
| `…_greyscale/tiles.csv` | Split, flood class, road and **building counts** per tile (R28) | It has rows for `test` and `negative`. Filter `split ∈ {train, val}` first; never print, group or plot the whole file |
| `SN8_Louisiana-East_Ida2021/tiles.csv` | Catalog ids and `pre_max_gsd_m`, `post_max_gsd_m` (V5) | Same: development rows only |
| `Project/docs/datasets/splits/sn8_louisiana_east_stratified_2026-10-16.csv` | The split (fingerprint `1008636ac61ddbc0`) | `check_split` stops on a mismatch |
| `Project/docs/datasets/splits/hrc_whu_authors_2026-10-23.csv` | HRC_WHU split (fingerprint `bfc45539e731761c`) | `hrc_split` checks the fingerprint |

#### D8. Not used by default

- The main project's Hurricane Ian post-only result (dev log 2026-10-11): not used in Q3 (decision 8, default).
- LEVIR-CD's test split (on disk, academic use only; `data_budget.md`): not a damage set; not used.
- Gemma (VLM) output: never a label, score or decision (input card). Out of figures unless the journal allows it
  (v2 §3.6).

### 3.3 Open-licence alternatives (the release route; later, not now)

The input card allows research-only data now and asks for a licence-compliant pipeline later. "Open" here means the
project's Route 2 rule: CC BY, CC0, public domain, CDLA-Permissive or similar; share-alike and non-commercial terms do
not count (`Project/CLAUDE.md`).

| Code | Replaces | Candidate | Licence (source) | Fit and limits | Status |
|---|---|---|---|---|---|
| O1 | D1 after image | NOAA Emergency Response Imagery, Hurricane Ida (AWS `noaa-eri-pds`) | ERI collections CC0-1.0 per NOAA InPort (project survey, `open_damage_datasets.md`); the confirmed record in `open_data_manifest.md` is for the Ian flight | Aerial, 15–30 cm; whole Ida collection 703 GB (survey). Aerial flights may hold little cloud, so real cloud may be absent (inference) | **TO VERIFY (V11)** |
| O2 | D1 before image | NAIP Louisiana, 2019-09 | Public domain (survey) | 0.6 m; about two years before Ida; free on the Planetary Computer (survey). "No NOAA pre-event flight exists for 2021" (survey) | **TO VERIFY (V12)** |
| O3 | D2 road geometry | TIGER roads (US Census) | "Not copyrighted" (survey) | Centrelines only; no flood attribute | **TO VERIFY (V13)** |
| O4 | D2 flood labels | None found | — | No open flood-road label set for Ida in the files | **Gap (V14)** |
| O5 | D3 real cloud labels | L8 Biome (USGS, doi:10.5066/F7251GDH) | Page states no licence (URL 2, §1.3); USGS-produced data are public domain (URL 3). Inference: the masks are USGS-produced | Landsat 8, 30 m, 96 scenes; thick, thin and shadow labels per evidence 02. 60 times coarser than 0.5 m | **TO VERIFY (V15)** |
| O6 | D3 | 38-Cloud / 95-Cloud | Repo Apache-2.0 (evidence 02); data licence not confirmed | Landsat 8, 30 m; thin haze counts as cloud; Kaggle needs an account | **TO VERIFY (V15)** |
| O7 | D3 | CloudSEN12-high | Hugging Face card `cc-by-nc-4.0` (URL 1, §1.3): **not open** under Route 2. Science Data Bank licence not read | Sentinel-2, 10 m; clear, thick, thin, shadow (evidence 02) | Not open unless V15 shows otherwise |
| O8 | D3 | SPARCS; KappaSet; Radiant cloud cover | SPARCS and KappaSet licences not read (evidence 02); Radiant CC BY 4.0, but the survey lists it under "model-made or generator labels" | 30 m and 10 m; Radiant may break the "published human labels" rule | **TO VERIFY (V15)** |
| O9 | D3 for the generator | Procedural shapes and noise texture (v2 §6.3 step 1 fallbacks) | No data licence needed | Already pre-registered as the fallback | Ready to write |

- **DINOv2 is already open:** `timm/vit_large_patch14_reg4_dinov2.lvd142m`, Apache-2.0; the weight file matched its Hub
  sha256 (`open_data_manifest.md`, stage 2; `sn8_dino.py` docstring).
- **Inference.** No open source matches D1 + D2 for this question today. An open release would keep the method and code,
  but would need new open labels to score flooded roads. The cloud tests would rest on the synthetic bed (O9), plus an
  open real-cloud check at 10–30 m, not 0.5 m.

---

## 4. Tools

### 4.1 Existing `sn8_*` modules (in `ProjectBranch/ClaudeFunctions/`)

Every module is read-only here. "Permitted" applies to this project until the sealed look.

| Module | Why needed | Permitted action | Inputs → outputs | Failure mode | Verification check |
|---|---|---|---|---|---|
| `sn8.py`, `sn8_data.py` | Find tiles; check the split; guard held-out data | Read development tiles. Never pass `allow_sealed` or `allow_held_out` outside the sealed-look script | Tile id → paths, catalog ids; split table | A new script globs `labels/` or `tiles.csv` without the split filter and reads sealed rows | `grep -rn "allow_held_out=True\|allow_sealed=True"` over the repo before the freeze: only the sealed-look script |
| `sn8_grey.py`, `sn8_torchgeo.py`, `sn8_coreg.py` | Greyscale (BT.601); the 0.5 m UTM 15N grid; the co-registration shift | Use as frozen | RGB tiles → grey pair on one grid; shift per tile | Before images declare 255 as no data, which drops bright cloud and roofs if a reader honours it (SN8 README) | `SN8Image.nodata = 0` stays set; one picture per run of the warped pair |
| `sn8_lines.py`, `sn8_roads.py` | Road band, strips, 10 m ring, classical cues; `CREDIT` | Use as frozen | Labels + grey pair → per-road cues | Road rows misaligned between tables | Row order asserts (as in `touched_roads`) |
| `sn8_glcm.py`, `sn8_texture.py` | Texture cues (GLCM, Gabor, LBP, Laws, wavelet, semivariogram) | Use as frozen; `semivariogram` may be reused for ΔD's patchiness (V8) | Strip pixels → texture columns | Reuse with a different region definition changes the statistic | Unit test on a synthetic field with a known semivariogram |
| `sn8_dino.py` | Frozen DINOv2 change cues (§4.5) | Inference only; no training or fine-tuning | Grey pair → `DINO_CUES` per road | See §4.5 | See §4.5 |
| `sn8_clouds.py` | Bright, dark and dark-rise masks; Otsu thresholds; He de-hazing; `assessable`; `neighbour_check`; `under_cloud_report` | Use as frozen. The Otsu thresholds (98, 71) stay as learned (v2 §3.3) | Grey pair → masks, per-road shares, de-hazed after | Thresholds learned on training tiles also held out in turn (a small leak; v2 §3.3). Otsu is only safe on two-peaked histograms (briefing P7) | Plot the pooled histograms once (development only); the per-fold sensitivity run (R6) |
| `sn8_refhaze.py` | Two-date correction, arm (a) (§4.7) | Frozen as run (SHA-256 `ff5a09bb…`) | Grey pair → corrected after, t̂, L̂, used pixels; corrected cue tables | Cache key misses imported functions (v2 §6.4.3); flood bigger than the 64 m window read as haze (docstring) | Key fix; the two label-free tests; four diagnostics per run (R36) |
| `sn8_cloudref.py` | HRC_WHU loader, authors' split, single-date masks, scores | Development images only | Image name → RGB, grey, expert mask, type; pixel scores | Masks' pixel windows meet 0.5–15 m imagery | Resolution bands if V1 is settled; otherwise "resolution not controlled" (v2 §6.1 step 3) |
| `sn8_heldout.py` | Touched roads; tile bootstrap; McNemar; gated calls | Development only | Roads + calls → reports | Tile bootstrap treats tiles as independent (critic M3) | Report beside the block bootstrap (R7) |
| `sn8_models.py`, `sn8_stages.py` | The frozen flood model (tuned random forest: 300 trees, depth 10, `random_state=662`) and the registry | Read the registry; never `promote` during the paper (v2 §16) | Features → fold models | A refit differs from logged production calls | Refit once and compare with the logged production run's calls; they must match |
| `sn8_detect.py`, `sn8_cutoff.py` | Road visibility (trees, shadow) for the "missing = dry" sensitivity | Use as frozen | Before image → visible share per road | Detector errors become the stratifier | Report the visible share on flooded and dry clear roads (v2 §6.1 step 7) |
| `sn8_results.py` | Run logs with code hashes | Log every run | Results → `Code/results/runs/*.json` | `code_hashes` hashes only `ClaudeFunctions/*.py`, not runner scripts elsewhere | Put new modules in `ClaudeFunctions`, and log runner-script hashes too |
| `sn8_reduce.py`, `sn8_canny.py`, `sn8_dino_cells.py`, `fetch_sn8.py` | Not needed for this plan | — | — | — | — |

### 4.2 Pilot scripts (in the evidence folder or the scratchpad; not in the repo)

| Script | What it does | Status | Action needed (by the coordinator, with Justin's OK) |
|---|---|---|---|
| `evidence/pilot_scripts/evaluate.py` (+ `evaluate.log`, `evaluate_v1_polyfit.log`, `refhaze_calls.csv`) | The pilot's scoring: three arms, 5 folds by tile, models fitted on assessable roads, every arm predicted by the same fold model | Exists since 2026-10-24 16:44 (evidence 01). Methodology v2 §0 still says "not in the repository": the repo still lacks it | Copy into the repo with its hash; re-run as a Tilt resource with blocked folds (v2 §6.4.3) |
| `evidence/pilot_scripts/diag_core.py` | The label-free fit diagnostic: clear-pixel correlation, least-squares and orthogonal slopes, t̂ on clear and cloud pixels, two tiles | Exists | Turn into the per-run diagnostics (R36) |
| `evidence/pilot_scripts/figures.py`, `slide_panels.py` | Assignment 4 figures | Exist | Reuse for §14's figures through `cpu_only` resources |
| `cloudresearch/mask_bias.py` in this session's scratchpad (`/private/tmp/claude-501/-Users-jusrogers-Masters-GGS662/d5466295-6061-4f31-ad8f-4ab1372accdd/scratchpad/cloudresearch/mask_bias.py`) | Evidence 03's uniform-haze check, the bed's crude control (I·t + A·(1 − t), A = 220) | **Exists only in a temporary folder.** It can be lost when the session ends | Move into the repo now. It is the control's only implementation |

**Evidence (`evaluate.py`), answering a v2 §19 open fact.** The 175 "clear roads on the same tiles" are the
production-assessable roads (tile rule + road rule) on the 39 tiles. **Inference:** that rule allows up to 20% of a
strip under dark rise, so these are not "clear" by the bed's < 5% rule. The pilot's control row and veto 1 use
different "clear" sets.

### 4.3 Stage notebooks (`ProjectBranch/Code/`; listed, outputs not opened)

`index.ipynb` (production; reports no results), `data_test`, `lines_test`, `texture_test`, `glcm_test`, `canny_test`,
`selection_test`, `models_test`, `detector_test`, `dino_test`, `dino_cells_test`, `clouds_test` (the cloud rule run,
`2026-10-23T141222`), `coreg_test`, `pca_test`, `visibility_test`, `cloudref_test` (HRC_WHU scores, run
`2026-10-23T171143`); `results/results.ipynb`; `archive/index_2026-10-23_before_split.ipynb`.

- **Kernel (evidence, notebook metadata):** "base", Python 3.14.7. **Inference:** the Miniconda base interpreter
  (`/opt/miniconda3/bin/python3`, the only Python 3.14.7 found).
- **Role in this plan (inference).** They are the record of the stage tests. New scored steps should be scripts run by
  Tilt, logged by `sn8_results`. A notebook may then display the logged outputs.

### 4.4 Libraries and the Python environment

| Library | Version (base Python 3.14.7) | Used for | Gap |
|---|---|---|---|
| NumPy, SciPy | 2.5.3, 1.18.1 | Everything; `binomtest`, `fisher_exact`, `ndimage`, `optimize` | SciPy has no stratified exact (Mantel–Haenszel type) test (inference; V18) |
| pandas | 3.0.6 | Tables | — |
| scikit-learn | 1.9.1 | Random forest; `StratifiedGroupKFold`; `LeaveOneGroupOut` | — |
| scikit-image | 0.26.0 | `threshold_otsu`, `regionprops` | — |
| OpenCV (headless) | 5.0.0 | Box filters (`sn8_refhaze`), resizing | — |
| torch (MPS available), timm, safetensors | 2.14.1, 1.0.30, 0.8.0 | DINOv2 | — |
| torchgeo, rasterio, pyproj, shapely, geopandas, tifffile | 0.10.1, 1.5.2, 3.8.0, 2.2.0, 1.2.0, 2026.9.20 | Grid, reading, reprojection, lengths | — |
| matplotlib | 3.11.2 | Figures | — |
| statsmodels | **Not installed** | Would give Holm and a Mantel–Haenszel test | Write in NumPy/SciPy, or download (§6.2) |
| pytest | **Not in base** (it is in `Project/.venv`) | v2's "tests in code" | Plain assert scripts under Tilt, or download (§6.2) |

- **Evidence (`pip list`).** `Project/.venv` (Python 3.12.2) has NumPy, SciPy, rasterio, torch, timm and pytest, but no
  pandas, scikit-learn, OpenCV or TorchGeo. The `sn8_*` modules import those.
- **Evidence (`Project/CLAUDE.md`).** The Tiltfile's `VENV` is `.venv/bin/`. "Never build `.venv` from Miniconda's base
  Python (3.14)." "Don't add packages to `geoai-py3122`."
- **Inference: a decision for Justin.** The roads Tilt track can call the base interpreter the notebooks used
  (`/opt/miniconda3/bin/python3 -I`), which has every library above and matches the logged runs. The rule against base
  Python concerns building `.venv`, but this is still a choice he should make, not me.

### 4.5 DINOv2 (the change detector's deep cues)

| Field | Value |
|---|---|
| Why needed | Pass 2's detector includes frozen DINOv2 change cues (+1.2 points, p 0.035; evidence 01). Every clouded or corrected image needs its cues recomputed (v2 §6.4.3) |
| Model | DINOv2 ViT-L/14 with registers, `timm/vit_large_patch14_reg4_dinov2.lvd142m`, Apache-2.0 (`open_data_manifest.md`) |
| Where | `~/Masters/models/huggingface/hub/…/model.safetensors` (1.2 GB). Loaded with `HF_HUB_OFFLINE=1` from an explicit file path (`sn8_dino.backbone`). Not in `~/.cache` |
| Permitted action | Inference only, frozen (no training, no fine-tuning); on the Mac GPU (MPS), natively, never in Docker (no GPU there; `Project/CLAUDE.md`). Never on the GPU at the same time as the main project's Gemma or DINOv3 jobs |
| Inputs → outputs | Greyscale repeated to three channels, ImageNet mean and SD; 2 × 2 windows of about 640 px; 14 px = 7 m patches → three cues per road (`dino_change_pooled`, `_mean`, `_max`) and the 1024-d change vector (PCA inside each fold) |
| Failure modes | Thermal throttling on the fanless M2 in long runs (inference); a slow-down of unknown cause in the pilot (§4.11, V7); no-data filled with the date's valid mean, which shifts under synthetic cloud (inference); finer crops (§6.4.8) give tokens from a different distribution, so they cannot feed the frozen forest (v2 §6.4.8; briefing P4) |
| Verification check | Re-running `corrected_table(tiles, "none")` must reproduce the cached cues exactly (the identity arm); prefix tokens dropped by the model's own count (`model.num_prefix_tokens`; read today; briefing P9); the run log records MPS and timing per tile |
| Status | Exists |
| Event-specific parts | None in the model. The patch size in metres depends on the 0.5 m grid |

Note: `backbone()` uses `os.environ.setdefault("HF_HOME", …)`. If `HF_HOME` is already set elsewhere, that value
stays (code read). The weights still load from the explicit path. Set `HF_HOME` and `HF_HUB_OFFLINE=1` in the Tilt
resource anyway (V23).

### 4.6 Synthetic-cloud generators (all new except the control)

| Generator | Why needed (v2 §6.3) | Inputs → outputs | Failure mode | Verification check | Status |
|---|---|---|---|---|---|
| Uniform-haze control | The deliberately crude control inside ΔD and ΔU | Grey after → I·t + A·(1 − t) | Lost from the scratchpad | Reproduces evidence 03's table on the 769 roads | `mask_bias.py` (scratchpad only) |
| Family M | The haze model behind the dark channel; circular for the masks and §6.4 | Clear after, t map, A → clouded after | Circularity (scored on X only) | Circularity flag on the dark mask's recall (v2 §6.3 step 5) | New, small |
| Family X | Main family: M plus cloud texture, air light varying across the tile, clipping | + texture (HRC_WHU cloud pixels if ruling 2 allows, else procedural noise) | Air-light scale suits a smooth fit (critic M19) | Air-light scale measured from real cloud before scoring; pictures beside real cloud at matched rise (figure 4) | New, medium |
| Family X-fast | Robustness cell for §6.4 only: blur, air light varying faster than 64 m (proposed 20 m) | As X | — | Used only in §6.4's robustness cell | New, small |
| Shape pool (HRC_WHU) | Real cloud outlines, rescaled to 0.5 m | D3 masks + per-image resolution (V1) | V1 unresolved: no rescaling possible | Size and edge sharpness reported | New; blocked by V1 and ruling 2 |
| Shape fallback (procedural) | Licence-free shapes with the size spectrum of the 17 opaque tiles' outlines | D4 outlines → seeded shapes | Using the outlines directly would favour the bright mask (v2 §6.3 step 1) | Size spectrum compared with D4; pictures | New, small |
| Placement and seeds | Whole-tile and shaped placement; one seed per cell, two on primary cells | Clear tile + seed → cloud map, t map | Seeds re-used across arms by mistake | Same tiles and seeds across arms, asserted; generator frozen with settings file and hash before any change call (v2 §6.3 step 1) | New, small |
| Before-image mode | Q3's clouded before images | Clear before → clouded before | After image touched by mistake | The leak check: after-only calls identical on clean and clouded copies (v2 §6.2 step 2) | New, small |

- **Rules carried into code (v2 §6.3).** No realism statistic sets the generator. No model is trained on synthetic cloud.
  HRC_WHU shapes are pasted into other images than their own. Methods on the bed never see the t map.
- **Briefing (P3, advice):** "Normalization does not remove cloud, haze or shadow; mask or tag them." The bed tests
  exactly whether the correction can see through thin haze. This is a conflict to report, not a rule to act on.
- **What Justin checks by hand:** the generator's pictures beside real cloud before the freeze (Fri 6 Nov).
- **Event-specific parts:** air light, edge fall-off, the size spectrum and the thickness levels come from this scene
  (D4). They belong in the task file. The families' formulas are general.

### 4.7 The two de-hazing arms (v2 §6.4.5, §19): mapped side by side, not chosen

| | Arm (a): as run (v2's default primary) | Arm (b): IR-MAD / orthogonal fit at a scale where the dates agree |
|---|---|---|
| What it is | `sn8_refhaze.reference_dehaze`: robust least squares of after on before over the tile's clear pixels (g, h), then weighted local least squares in 129 × 129 px (64 m) windows (α, β), three passes trimming at 2.5 robust SDs; t̂ = α/g, L̂ = β − t̂h; haze only where 0.2 ≤ t̂ ≤ 1 and L̂ ≥ 0 (v2 §6.4.3) | Invariant pixels chosen by an IR-MAD-style no-change weight; an orthogonal (total least squares) fit for the dates' relation; fitted on coarser windows or smoothed images (evidence 01, "fix to pre-register"; v2 §6.4.5) |
| Code | **Exists**, frozen, SHA-256 `ff5a09bb…` | **Must be written.** Only an orthogonal slope exists, inside `diag_core.py` (`np.linalg.eigh` of the covariance) |
| Label-free evidence so far | Clear-pixel correlation r = 0.46 on 2_19_55 and 0.09 on 2_15_45; g = 0.16 (orthogonal 0.31); local α 0.03–0.05; median t̂ 0.32 on clear pixels; 66% of clear pixels read as haze; about half the cloud pixels fall below t̂ = 0.2 (evidence 01; `diag_core.py`). "Closer to a local contrast stretch than a haze estimate" | None yet. The scale at which the dates agree is not measured (V20) |
| Settings to pre-register | As run; sensitivity 128 m (v2 §8) | The scale; the no-change weight and its cut; iterations and stop rule; whether the haze rule and the 0.2 floor stay. All fixed from label-free diagnostics before any bed scoring |
| Single-band issue | Linear fit on 8-bit visual products | IR-MAD with one band has one degree of freedom (inference; V19) |
| Education briefing (P3, advice) | "No IR-MAD or other linear normalization on the 8-bit visual product … our dates have different non-linear tone curves" | The same rule names IR-MAD directly |
| Compute | CPU fit; one DINOv2 pass per cell (about 45 min per 190-tile cell; v2 §6.4.11) | Same per cell. If (b) is primary, it needs the four levels, veto 1 and the sealed re-run (inference: about 4 h more) |
| Failure modes | Reads clear ground as haze; floods larger than 64 m read as haze (docstring); tuned after the pilot looked (critic M18) | A coarser scale blurs road-scale haze; the variant is new and un-piloted; chosen after a post-pilot diagnostic (v2 §6.4.5) |
| Verification checks (both) | On a clear tile, t̂ near 1 almost everywhere; under uniform synthetic haze, t̂ recovers the set value away from edges (v2 §6.4.3); positive controls: identity passes veto 1, fill-from-before fails veto 2 (v2 §6.4.6); four diagnostics per run: fallback share, low-variance share, clear-pixel correlation, clear pixels counted as haze | Same |
| Event-specific parts | The sign rule assumes the hazard darkens (floodwater); a brightening hazard breaks it (docstring). Window in pixels (64 m at 0.5 m) | The same sign assumption, if kept |

- **What is the same in both:** pass 1 (frozen masks), pass 2 (frozen detector and fold models), the bed cells, the
  vetoes, the scored set, and the rule that the 24 pilot roads stay exploratory (v2 §6.4.5).
- **Whichever is primary, the other is reported beside it** (v2 §6.4.4, §6.4.5). Justin decides (v2 §19).
- **Conflict to report:** the briefing's P3 rule speaks against both arms, and names (b) directly. The briefing is
  advice; it does not override Justin's decisions (`Project/CLAUDE.md`).

### 4.8 Statistics tools

| Tool | Why needed (v2 §) | Status | Failure mode | Verification check |
|---|---|---|---|---|
| Spatial block bootstrap | Primary intervals (§3.4) | New, small (NumPy) | Too few blocks (22 at side 7; critic §2) gives unstable ends | On synthetic data with known dependence, coverage near 95%; report block count with every interval |
| Blocked folds | Same-week check on every primary result (§3.3) | New, small (scikit-learn groups) | Block side longer than 7 tiles: intervals too narrow | Label every interval "may be too narrow" if the range exceeds 7 tiles (§3.3) |
| Semivariogram range fit | Block side (§3.3) | New, small (NumPy, SciPy) | Unstable fit on about 226 tiles | Report the empirical curve and the fitted range in a figure |
| Cloud-patch bootstrap | Real-cloud quantities (§3.2) | New, small | Fewer than 10 patches | Describe, do not test (§3.2) |
| Tile bootstrap; McNemar exact | Secondary (§3.4) | Exists (`paired_report`) | Roads treated as independent (McNemar) | Shown beside the block intervals only |
| Holm step-down | Secondaries within a question (§3.4, §8) | New, a few lines | Wrong family | Unit test against a hand-worked example |
| Non-inferiority within δ | S2, S3, §6.4 primary, Q3 usefulness bar (§6.1 step 6) | New, small | "Fails" and "not shown" mixed up | Three-outcome unit test |
| Stratified exact test (Mantel–Haenszel type) | H2b (§6.1 step 4) | New (SciPy has none; statsmodels not installed) | Wrong conditioning on tile margins | Test against a small hand-worked table; method and citation still needed (V18; v2 §19) |
| Equivalence margins (check 1, check 2) | Q1 secondaries (§6.3 step 5) | New, small | Low power reads as a match | Fail-safe rule (§9): low power gives "not shown" |
| Power and expected widths (Gate 0) | §9 | New, small | Rule of thumb (1.43 × half-width) uncited | Compare with a simulation on the logged calls |
| Tipping points | §6.1 step 7 | New, small | — | Hand check on one conclusion |
| Risk–coverage curve | Optional (§6.1 step 8) | New, small | — | Classifier fixed; only abstention varied |

All of these are general: none is event-specific.

### 4.9 Orchestration, logging and freezing

| Tool | Why needed | Status | Verification check |
|---|---|---|---|
| Tilt (v0.37.8; `/opt/homebrew/bin/tilt`) | Every run is a Tilt resource (project rule; v2 §13) | **No resource exists for the roads side test** (search of `Project/Tiltfile` and `tilt/`). `tilt/lib.tiltfile` has `track_script()` | `tilt get uiresources` lists the roads track; GPU resources serial (`allow_parallel` off), figures `cpu_only` |
| `tilt/roads_cloud.tiltfile` | The track's own file (per-track rule, `Project/CLAUDE.md`) | New, small | Each resource names its interpreter (§4.4), `HF_HOME`, `HF_HUB_OFFLINE=1` |
| `sn8_results` run logs | Code hashes and calls per run | Exists | Every result in the paper traces to a run JSON |
| Pre-registration file | Rules, settings and hashes frozen before scoring (v2 §8, §16) | New | Justin reads and signs it off |
| Dev log and ledger | Living docs; the sealed draw logged first (`data_budget.md` rule 2) | Exist (`Project/docs/devlog.md`; `data_budget.md`) | The draw row is written before the look |

### 4.10 Code to write, in build order (inference: sizes are estimates)

| Week (v2 §15.2) | Item | Size |
|---|---|---|
| 1 | Move `evaluate.py`, `diag_core.py`, `mask_bias.py` into the repo, with hashes | Small |
| 1 | Cache key fix in `sn8_refhaze` (adds `dark_channel`, `cloud_thresholds`); two label-free tests; four diagnostics | Small |
| 1 | Tilt track file; interpreter decision | Small |
| 1 | Week-1 counts: acquisitions, patches, near-threshold dark rise, visible share, buildings (development rows only), real thin level and rise bins, top-10 cues, block size, 1,080 against 1,037, timing | Medium |
| 1–2 | Block bootstrap, blocked folds, Holm, non-inferiority, Gate 0 calculator | Small–medium |
| 2 | S1 patch scorer on HRC_WHU; H2a; H2b test; ranges; tipping points | Medium |
| 2 | After-only model, mean-imputation arm, clean gap | Small |
| 2 | Generator (M, X, X-fast, control, both placements, both dates, seeds, settings file), frozen Fri 6 Nov | Medium–large |
| 2 (if ruled) | Arm (b) module | Medium |
| 3 | ΔD statistics; check 2 paste tool; circularity flag | Medium |
| 3–4 | Bed runner (cloud → cues with DINOv2 → fixed fold models), provenance layer, fill-from-before arm, change-kept measure | Medium |
| 4 | ΔU; H1b; tier scorer | Small–medium |
| 5 | Water mask and audit sheet; routing flag | Small–medium |
| 6 | Buffered folds; leave-one-area-out; figures | Small |
| 6 | Sealed-look script (the only guard flags), expected widths | Small |

### 4.11 Compute and storage

**Evidence (pilot logs; times are cumulative from the script's start):**

| Arm (39 tiles, all cues including DINOv2) | `evaluate_v1_polyfit.log` | `evaluate.log` |
|---|---|---|
| He de-hazing | 435 s (about 11 s per tile) | 435 s (about 11 s per tile) |
| Two-date | 893 − 435 = 458 s (about 12 s per tile) | 8,414 − 435 = 7,979 s (**about 205 s per tile**) |

- The cache file times match these runs (tables at 20:04 and 20:12, then 20:28 and 22:40).
- **Inference.** In three of four arm runs, every cue cost about 11–12 s per tile, close to v2's 14 s of DINOv2 per tile.
  This partly answers the critic's M27 point: the CPU cues are inside that time. The fourth run was about 17 times
  slower. Its code change was a closed-form global fit, which should cost little. So the cause is most likely the
  machine (sleep, throttling or a shared GPU), but this is not shown (**V7**). If the slow rate were real, the 16-cell
  bed would take about 170 h, which is not feasible. Measure per-stage times on a few tiles in week 1.

**v2's budget (§15.5, §6.4.11; inference there):** bed 16 cells about 12 h; §6.4 about 8 h; Q3 four levels about 3 h;
buildings about 50 min; sealed look about 3 h; heatmaps under 30 min. In all, about 27 h of DINOv2 time.

**My additions (inference):**
- **Cells that may be missing from the budget (V22):** the control's cue pass for ΔU; the second seeds on primary
  cells; arm (b)'s cells if it becomes primary. Each cell costs about 35–45 min at 11–14 s per tile.
- **Q3 cell count (V21):** §6.2 step 2 clouds the before image with families X and M, at four levels (8 cells, about
  6 h). §15.5 costs four levels at about 3 h.
- **Fanless M2:** allow 1.5–2× for sustained runs, so plan for 40–55 h of wall time across weeks 3–5. Run overnight, one
  GPU job at a time, never beside the main project's Gemma or DINOv3 jobs (`Project/CLAUDE.md`).
- **Memory:** DINOv2-L weights are 1.2 GB; windows of about 640 px keep activations small (`sn8_dino` docstring). Well
  inside the 10.7 GB Metal working set (`Project/CLAUDE.md`).
- **Storage:** 29 GB free. A corrected-cue table is about 0.5 MB per 268 roads (evidence, cache), so about 2 MB per
  bed cell, well under 1 GB in all. Do not store bed images; one 190-tile cell of greyscale images would be roughly
  0.3 GB. Regenerate them from the seed.
- **CPU only:** fits, bootstraps, fold refits and HRC_WHU scoring. They can run beside a GPU job.

### 4.12 Generality: what is event-specific in each tool

The pipeline must stay general (input card; v2): hazard specifics in task files, and a quality layer that abstains.

| Part | General | Event-, sensor- or target-specific (belongs in a task file) |
|---|---|---|
| Loaders (`sn8*`, `sn8_torchgeo`) | Guards; split fingerprints | SN8 layout; tile ids; UTM 15N; credit line |
| Cloud masks (`sn8_clouds`) | Dark-channel idea; dark rise against a reference date | Bright rule (grey > 200, SD < 10); Otsu thresholds 98 and 71; 41 px window (20 m at 0.5 m) |
| Road cues (`sn8_roads`, texture, GLCM) | Strip and ring logic | Roads; band width; 10 m ring |
| Flood model | Fold design; frozen-model rule | Trained on SN8 flood labels: hazard- and event-specific |
| DINOv2 | The backbone | Patch size in metres (grid-dependent) |
| Two-date correction | Haze model; robust fit; provenance classes | Sign rule (the hazard darkens); window in pixels |
| Generator | Families M, X, X-fast and the control | Air light, fall-off, sizes and levels from this scene |
| Quality layer (cannot assess; provenance) | The rule "filled never votes"; "not observed" counts against callability | The 20% cut is a target rule |
| H3b water mask; routing flag | — | Flood-specific |
| Statistics | All | δ and the ceilings are user judgements |

**Inference:** a task file (for example `tasks/ida_flood_roads.yaml`) can hold the right-hand column. Then the code
holds only the left. This is a suggestion, not something v2 requires.

---

## 5. AI-assisted coding and analysis tools

All of these run on Anthropic's Claude models. Their agreement with each other is not independent validation (AGENTS.md
rule 4). The independent checks are Justin's review, the pre-registration, tests in code and the sealed look (v2 §13).

| Tool | What it does in this project | What Justin must check by hand |
|---|---|---|
| **Claude Code (the coordinating session)** | Writes the new modules (§4.10), the Tilt track and the runner scripts; runs them through Tilt; logs runs with hashes; builds figures; drafts text | (1) That no script sets `allow_held_out=True` or `allow_sealed=True` except the sealed-look script (one `grep` before the freeze). (2) That week-1 scripts filter to `train` and `val` before reading `tiles.csv`, the mapping CSV or label files. (3) That every number in the paper traces to a run JSON. (4) That the generator, error crops and audit sheets look right as pictures. (5) One primary result, re-run from a clean cache, gives the same number |
| **Workflow agents** (research-question agent, scientific critic, methodology agent, this data + tool agent, validation agent, writer; `05_Project/agents/`) | Propose, critique, map, check and draft | Each accept, change or reject goes in `decision_log.md` in his words. He checks that "evidence" items really are in the named file and section (the validation agent checks too, but on the same model) |
| **Validation agent** (stage 7) | Checks v2's numbers and this plan's facts against the files (AGENTS.md rule 8) | Spot-check three numbers himself against the source files |
| **Writer agent / `paper-builder` skill** | Assembles text. `paper-builder` relocates his own sentences verbatim (its `SKILL.md`) | That claim words match v2 §12.1 ("held-out, same scene", not "external"; no novelty). That the AI-use statement names general task types only and is truthful |
| **Literature agents** (researcher; relevance-checker; completeness-checker; summary-annotator) | Search, screen and summarise papers | He logs in to GMU himself; agents never do. He checks each cited claim matches what the paper did, and each journal's JIF ≥ 4 (or a major conference) in JCR. None of the references is verified yet (v2 references) |
| **`deck-designer` skill** | Builds the Assignment 4 slides from box 15.1 | Every slide claim is in box 15.1's "safe to say" list; nothing "significant" or "better than He" |
| **`/code-review` skill** (optional) | Reviews the new statistics code for bugs | The unit tests' hand-worked answers are right; the review is the same model |
| **Education agent's briefing** | Advice on image-processing steps (read before designing the generator or the correction; `Project/CLAUDE.md`) | Whether to follow P3 (no linear normalisation on 8-bit products) for either de-hazing arm (§4.7). The briefing never overrides his decisions |
| **Gemma (VLM, via Ollama)** | Not used in any score, label, tier or decision (input card). Possibly CSI 709 descriptions later | If any Gemma text reaches a figure, the journal allows it and the AI-use statement says so (v2 §3.6) |

**General checks for Justin, whatever tool did the work:**
- Rulings 1–4 (v2 §19), one at a time, before the pre-registration.
- The pre-registration file: every value in v2 §8, every hash, both synthetic-truth branches.
- Licences and credit lines on every figure (D1: SpaceNet 8, Maxar, CC BY-SA 4.0; D3: "HRC_WHU (Li et al., 2019;
  imagery Google Earth), academic use only").
- The sealed draw: logged in the ledger and the dev log before the look, run once, reported whatever it shows.

---

## 6. Gaps, TO VERIFY, unresolved issues and next action

### 6.1 TO VERIFY (25 items)

| # | Item | Why it matters | How to settle it |
|---|---|---|---|
| V1 | Per-image resolution of HRC_WHU | Shape rescaling (v2 §6.3 step 1); resolution bands (S1, check 2). Not in the dataset PDF (read today) | Li et al. 2019 (ISPRS JPRS; paywalled) in Justin's GMU session; else the fallback by the end of week 1 |
| V2 | HRC_WHU types: five, or six with "wetlands" | The pooled S1 types | Count file prefixes in the development list (no pixels) |
| V3 | Whether a journal figure may show HRC_WHU crops (Google Earth) | Figures 3 and 4 (decision 9) | Google's attribution terms; default no crops |
| V4 | Acquisition dates of the SN8 before and after images | Temporal scope in the paper | SpaceNet source CSVs or Maxar catalog metadata, development rows only |
| V5 | Per-tile pixel sizes of the two dates | Scale reporting | `pre_max_gsd_m`, `post_max_gsd_m` in the raw `tiles.csv`, development rows only |
| V6 | 1,080 label rows against 1,037 roads | H2a counts roads (critic M27) | Week-1 check, development only |
| V7 | Cause of the pilot's 17× slow-down in the two-date arm | The whole compute plan | Timed Tilt run on a few tiles, per stage |
| V8 | Whether `sn8_texture.semivariogram` fits ΔD's patchiness statistic | Reuse against new code | Read the function; unit test |
| V9 | Whether `tiles.csv`'s building columns are filled for development tiles and match `label_counts` | Buildings go/no-go | Development rows only |
| V10 | SpaceNet 8's definition of a flooded building | Buildings in Q3 | Hänsch et al. 2022 |
| V11 | NOAA ERI Ida: licence record, frames over the SN8 footprint, cloud present, window sizes | Open route (O1) | NOAA InPort record; storm page |
| V12 | NAIP Louisiana 2019 coverage and sizes | Open route (O2) | Planetary Computer catalogue |
| V13 | TIGER roads licence and match to OSM | Open route (O3) | Census page |
| V14 | Any openly licensed flood-road labels for Ida | Open route (O4) | Literature and catalogue search |
| V15 | Open cloud labels: L8 Biome masks USGS-produced; 38-Cloud data licence; SPARCS, KappaSet, Science Data Bank (CloudSEN12) licences; whether Radiant's labels are human-made | Open alternative to D3 | Each dataset page |
| V16 | DINOv2 licence wording from the model card itself | Data statement (v2 §3.6) | The Hub card |
| V17 | Wheel sizes of statsmodels and pytest, if wanted | Download decision (§6.2) | PyPI pages |
| V18 | Stratified exact test: method and citation | H2b (v2 §6.1 step 4, §19) | A statistics reference meeting the citation rule |
| V19 | Whether IR-MAD applies with one band | Arm (b) | Nielsen 2007; Canty & Nielsen 2008, full text |
| V20 | The scale at which the two dates agree | Arm (b)'s settings | Label-free correlation against window size on development tiles |
| V21 | Q3: four cells or eight (families X and M) | Compute | Methodology agent clarifies |
| V22 | Cells missing from §15.5 (control for ΔU; second seeds; arm b) | Compute | Methodology agent clarifies |
| V23 | Whether `HF_HOME` is set in Justin's shell | Weights path hygiene | `echo $HF_HOME` in the Tilt resource |
| V24 | Whether the "base" kernel is `/opt/miniconda3/bin/python3` | Interpreter for Tilt | Print `sys.executable` from a notebook |
| V25 | Whether an independent, published permanent-water layer (for example USGS hydrography) exists for these parishes at a useful scale | H3b's water mask is unmeasured (critic M12). JRC surface water is 30 m, coarser than a 10 m ring (project survey) | Optional; dataset page and licence. Not needed by v2 |

### 6.2 Downloads: decisions for Justin

- **Nothing must be downloaded for the development work (weeks 1–7).** D1, D2, D3 and the DINOv2 weights are on disk.
- **Optional, small, tooling (default: no download).**
  - statsmodels, from PyPI, into the base environment. Size TO VERIFY (V17; inference: about 10 MB). Gives Holm and an
    asymptotic Mantel–Haenszel test. Default: write the few functions in NumPy/SciPy, with tests.
  - pytest, from PyPI, into the base environment. Size TO VERIFY (V17; inference: under 2 MB with dependencies). Default:
    plain assert scripts run by Tilt.
- **Later, for the open-licence route (not now; input card).** Each needs his OK, the file list, source and size first:
  - NOAA ERI Ida windows over the SN8 footprint: AWS `noaa-eri-pds`; the whole collection is 703 GB (project survey); the
    windows are far smaller, size TO VERIFY (V11).
  - NAIP Louisiana 2019 quarter-quads: Planetary Computer; "hundreds of MB per quarter-quad, unconfirmed" (survey; V12).
  - TIGER roads for the parishes: US Census; size TO VERIFY (V13).
  - An open cloud-label set at 10–30 m, for example L8 Biome (doi:10.5066/F7251GDH); size TO VERIFY (V15).
- **Not a download by me:** the papers for Justin's GMU session (Li et al. 2019 for V1; Lin et al. 2015 before the
  §6.4 freeze).

### 6.3 Conflicts to report (not acted on)

1. **Education briefing P3 against both de-hazing arms** (§4.7). The briefing is advice. Justin decides.
2. **Interpreter.** The roads code runs on the Miniconda base Python 3.14.7 (inference, V24). `Project/CLAUDE.md` warns
   against building `.venv` from that Python, and `.venv` lacks four libraries the code needs (§4.4). He picks the
   interpreter for the Tilt track.
3. **Methodology v2 §0 is out of date on one point:** the pilot's scoring script now exists in
   `evidence/pilot_scripts/`. It is still not in the repo.
4. **Model-weight hygiene.** `~/.cache/huggingface` holds 506 MB of `docling` models. They are not this project's, but
   the rule says no weights in `~/.cache`. DINOv2's weights are correctly in `~/Masters/models/`.

### 6.4 Unresolved issues

- **Rulings 1–4** (v2 §19): synthetic truth; HRC_WHU outlines and cloud pixels; where §6.4 sits; the §8 rules. Plus
  the new one: which de-hazing arm is primary.
- **No open flood-road labels** (V14) and **no open VHR cloud labels** (V15) were found. The open release can keep the
  method, not the scores.
- **The compute plan rests on V7.**
- **`mask_bias.py`** exists only in a temporary folder.
- **Fact gaps still open from v2 §19,** now with a tool named for each: cloud patches (R3), near-threshold dark rise
  (R15), visible share (R20), building counts (R28, V9), real thin level (R30), mixed-tile count (R15), water group
  size (R26), block size (R5), interval widths (R41), 1,080 against 1,037 (V6), §6.4's fallback and low-variance shares
  (R36).
- **Answered today:** the pilot's "clear" rule for the 175 roads is production-assessable, not < 5% dark rise (§4.2).
  The CPU cues are inside the pilot's 11–12 s per tile (§4.11), unless V7 says otherwise.

### 6.5 Suggested next scientific action

1. **Before any scoring:** move `mask_bias.py`, `evaluate.py` and `diag_core.py` into the repo, with hashes (one
   coordinator step, Justin's OK).
2. **Justin rules, one at a time:** synthetic truth; HRC_WHU use; §6.4's place; the primary de-hazing arm (with the
   briefing's P3 in view); the Tilt interpreter.
3. **Week 1, through Tilt, development data only:** a timed run on a few tiles (V7); then the label-free counts (R44),
   with the split filter checked by Justin.
4. **Gate 0** from those counts and the new bootstrap code, then the pre-registration (Sun 1 Nov).
5. **Next workflow stage:** the validation agent checks this plan's evidence items against the files named in §1.
