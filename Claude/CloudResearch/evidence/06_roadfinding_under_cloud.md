# Road finding under cloud: does de-hazing the after image help the road detector? (2026-10-25)

Source: Justin Rogers's GGS 662 roads side test (`~/Masters/GGS662/ProjectBranch`, private repo GeoAI-Roads).

| Item | Where |
|---|---|
| Test plan, written before any score | `outputs/preregistration_roadfinding_cloud.md` (18:40 EDT) |
| Module (new; no existing module edited) | `ClaudeFunctions/sn8_cloudroads.py` |
| Code the run used | GeoAI-Roads 5be95c2 + the new module |
| Script | `evidence/pilot_scripts/roadfinding/run_roadfinding.py` |
| Run log and every table | `run.log`, `numbers.json` |
| Per-road table | `roads_set_aside.csv` |
| Pictures | `0_14_6_*.png` |
| Post-hoc diagnostic | `posthoc_tbins.*` |

**Exploratory:** these are development tiles whose cloudy images had been looked at before.
- Development data only: the 186 training and 40 validation tiles from `split_tables(662)`.
- The test tiles, the north negative set, Germany and Louisiana-West were never read.
- `allow_held_out` was never set.

## What was measured
- **Question:** under the two-date cloud gate, does production's road detector find more OpenStreetMap (OSM) road cells
  on the after image once that image is de-hazed? Each arm's detector is trained and called on its own kind of image.
- **Detector:** production's random forest (300 trees), classical + DINOv2 cell features (44), cut-off 0.75.
  - Before any score, a reproduction check compared these features with `sn8_detect.tile_cells` and the cached
    `cell_dino_table("train")` on two training tiles. The largest difference was 0.0 for both.
- **Arms:**
  1. the after image as it is;
  2. two-date de-hazed (`dark_reference_dehaze`);
  3. single-image de-hazed (He et al. 2011, `dehaze`);
  4. the before image, as the upper bound.
- **Cells:** 2 m cells, fully valid on both dates. Road cells lie within 3.5 m of an OSM centreline; not-road cells
  lie beyond 8 m.
- **Groups**, from the two-date fit (label-free), by cell centre:
  - **correctable:** in the gate, t >= 0.2;
  - **opaque:** in the gate, t < 0.2;
  - **fade:** the 20 m margin just outside the gate;
  - **clear:** everything else.
- **Training and folds:** 5 folds by tile (StratifiedGroupKFold, seed 662) over the 226 tiles.
  - The training cells follow production's rule: up to 300 road cells and 3 times as many not-road cells per tile.
    That gives 251,428 cells, the same positions in every arm.
  - Every scored cell was called by a model that never saw its tile.
- **Statistics:**
  - **Scores:** weighted precision, recall and F1. All gate road cells are stored, not-road cells in the gate at 25%,
    clear cells at 5%, and the weights undo the sampling.
  - **Main uncertainty:** 95% intervals from 5000 resamples of whole tiles.
  - **Exact McNemar tests on cells:** secondary only. They overstate significance, because cells in one tile are
    correlated.
- **Run time:** 2 h 57 min (DINOv2 on the MPS GPU), with another agent's CPU jobs running at the same time.

## Evidence (numbers)

### Scored cells
| Group | Tiles | Road cells | Not-road cells stored (stand for) |
|---|---|---|---|
| correctable | 120 (66 with road cells) | 46,239 | 588,540 (2.35 M) |
| opaque | 74 (27 with road cells) | 26,120 | 197,338 (0.79 M) |
| fade | 122 | 22,617 | 182,995 (0.73 M) |
| clear | 222 | 16,240 (5% sample) | 735,916 (14.7 M) |

### Primary: road-cell F1 in the correctable cloud cells (120 tiles)
| Arm | Precision | Recall | F1 (95% CI) | F1 minus as it is (95% CI) |
|---|---|---|---|---|
| 1 as it is | 0.517 | 0.010 | 0.020 (0.004-0.047) | - |
| 2 two-date | 0.628 | 0.009 | 0.017 (0.003-0.039) | **-0.003 (-0.011 to +0.003)** |
| 3 single image (He) | 0.361 | 0.012 | 0.024 (0.006-0.053) | +0.004 (-0.000 to +0.009) |
| 4 before (upper bound) | 0.692 | 0.596 | 0.640 (0.586-0.690) | +0.620 (+0.559 to +0.672) |

- **Primary result:** the two-date arm is not better than the after image as it is. The difference is -0.003 and its
  interval includes 0. By the plan's rule, it does not help.
- **Secondary 1, two-date against as it is:**
  - recall -0.0016 (-0.006 to +0.002);
  - precision +0.111 (-0.071 to +0.295).
  - McNemar on cells:
    - road cells found by two-date only 110, by as-it-is only 186 (p = 1.2e-5);
    - false alarms removed 84, added 32 (p = 1.5e-6).
- **Secondary 2:**
  - single image against as it is: recall +0.002 (-0.000 to +0.005), precision -0.156 (-0.350 to +0.032).
    McNemar on cells: found 152 against 60 (p = 2e-10); false alarms removed 36, added 176 (p = 2e-23);
  - two-date against single image: F1 -0.007 (-0.018 to +0.002), precision +0.267 (+0.018 to +0.462).
- **Secondary 3:** two-date closes -0.5% of the F1 gap between "as it is" and "before"; single image closes +0.6%.
- **Secondary 7, threshold-free ROC AUC in the correctable cells:**
  - as it is 0.665 (0.618-0.711);
  - two-date 0.655 (difference -0.010, -0.036 to +0.013);
  - single image 0.670 (+0.004, -0.016 to +0.027);
  - before 0.982 (0.974-0.989).
- **Secondary 8, each arm's own F1 cut-off** (out-of-fold training cells, real road share 0.022):

  | Arm | Own cut-off | F1 in correctable cells | Against as it is (95% CI) |
  |---|---|---|---|
  | as it is | 0.59 | 0.038 | - |
  | two-date | 0.60 | 0.039 | +0.001 (-0.012 to +0.019) |
  | single image | 0.55 | 0.045 | +0.007 (+0.002 to +0.014) |
  | before | 0.77 | 0.636 | - |

### Secondary 4, 5 and 9: the other groups (F1, and the difference from "as it is" with its 95% CI)
| Group | as it is | two-date | single image (He) | before |
|---|---|---|---|---|
| opaque (74 tiles) | 0.000 | 0.000 (±0) | 0.000 (±0) | 0.740 |
| fade margin (122) | 0.123 | 0.094 (-0.029; -0.059 to -0.003) | 0.100 (-0.023; -0.051 to +0.000) | 0.708 |
| clear, all tiles (222) | 0.314 | 0.313 (-0.001; -0.008 to +0.006) | 0.298 (**-0.016; -0.026 to -0.006**) | 0.700 |
| clear, gated tiles only (119) | 0.320 | 0.319 (-0.002; -0.016 to +0.012) | 0.297 (**-0.023; -0.039 to -0.010**) | 0.687 |

- No after-image arm found a single road cell in the opaque cells.
- **Harm, by the plan's rule (an interval wholly below 0):**
  - single-image de-hazing lowers F1 on clear cells;
  - two-date lowers it in the fade margin.
- Recall in clear sky: 0.21 for the after-image detector, against 0.68 on the before image.

### Secondary 6: flood confound (road-cell recall by the nearest OSM road's development flood label)
| Group | Label | Tiles | Road cells | as it is | two-date | single image | before |
|---|---|---|---|---|---|---|---|
| correctable | flooded = yes | 15 | 4,637 | 1.8% | 3.0% (+1.3 pts; -0.3 to +2.5) | 2.5% (+0.7; -0.9 to +3.1) | 59.8% |
| correctable | not labelled flooded | 56 | 41,602 | 0.9% | 0.6% (-0.3; -0.8 to -0.1) | 1.1% (+0.1; +0.0 to +0.4) | 59.6% |
| opaque | flooded = yes | 1 | 4 | 0% | 0% | 0% | 75% |
| opaque | not labelled flooded | 26 | 26,116 | 0% | 0% | 0% | 69.6% |
| clear | flooded = yes | 103 | 8,313 | 6.5% | 6.6% | 6.4% | 65.5% |
| clear | not labelled flooded | 158 | 7,927 | 37.0% | 36.7% | 34.4% (-2.6; -3.9 to -1.4) | 71.7% |

Under cloud only "flooded = yes" is a trusted label. "Not labelled flooded" there mixes dry roads with roads the
analysts could not see.

### The roads that could come back (239 set aside by the cloud rule)
- **Decisions:** `road_handling` gives 15 ASSESS, 136 CORRECT and 88 CANNOT ASSESS, on 56 tiles. 55 of the CORRECT roads
  are on opaque-cloud (tile-rule) tiles. All 239 roads had cells of their own.
- **Rule:** a road is visible when at least 50% of its own cells are called road at 0.75.

| Roads | n | as it is | two-date | single image | before |
|---|---|---|---|---|---|
| **could come back (ASSESS + CORRECT)** | 151 | **7** | **5** | **7** | **89** |
| ASSESS | 15 | 3 | 3 | 3 | 6 |
| CORRECT | 136 | 4 | 2 | 4 | 83 |
| CORRECT, tile-rule-scored tiles | 81 | 3 | 2 | 3 | 53 |
| CORRECT, opaque-cloud tiles | 55 | 1 | 0 | 1 | 30 |
| CANNOT ASSESS | 88 | 0 | 0 | 0 | 50 |
| of the 151: labelled flooded = yes | 27 | 0 | 0 | 0 | 16 |
| of the 151: not labelled flooded | 124 | 7 | 5 | 7 | 73 |

- **Against "as it is", on the 151 roads (49 tiles):**
  - two-date: 0 newly visible, 2 lost (McNemar p = 0.5); share visible -0.013 (-0.036 to +0.000);
  - single image: 0 newly visible, 0 lost;
  - before: 84 newly visible, 2 lost.
- **Flood labels:** under cloud only "yes" is trusted, and the 55 roads on opaque-cloud tiles carry no flood label at
  all. No flood call is scored here.

### Pictures (tile 0_14_6, picked by the plan's rule: the most OSM road cells in the correctable part of the gate)
- `0_14_6_images_tile.png` and `0_14_6_images_zoom.png` (a 250 m window centred on the tile's correctable road
  cells):
  - the panels show the before image, the after image as it is, two-date de-hazed and single-image de-hazed;
  - orange is the gate boundary (the gate covers nearly the whole tile, so the small orange loops are holes in it);
  - red outlines the opaque part.
- `0_14_6_detections_tile.png` and `0_14_6_detections_zoom.png`: each arm's detected road cells on its own image
  against OSM (green found, red false alarm, blue missed).
- **What they show:**
  - de-hazing brings back the brightness: dark tree and field patches reappear;
  - the 2 m road structure does not come back. The main highway shows only faintly in the two-date image;
  - in the zoom, every after-image arm finds 0 of the 2,258 road cells in the gate, while the before image finds 1,320.

### Post-hoc diagnostic (not in the plan): recall in the correctable cells by the two-date fit's t
(`posthoc_tbins.csv`, `posthoc_tbins.png`)

| t (1 = clear) | Road cells | as it is | two-date | single image | before |
|---|---|---|---|---|---|
| 0.2-0.4 | 19,534 | 0.0% | 0.0% | 0.04% | 58.9% |
| 0.4-0.6 | 17,605 | 0.9% | 0.9% | 0.9% | 64.0% |
| 0.6-0.8 | 8,574 | 3.7% | 2.8% | 4.6% | 53.8% |
| 0.8-1.0 | 526 | 0.0% | 0.0% | 0.2% | 32.7% |

80% of the correctable road cells sit at t < 0.6. Even at t 0.6-0.8, the after-image detectors find under 5%.

## Deviations and problems (disclosed)
- **The two-date image changes some tiles that have no gate.**
  - The plan expected arm 2 to be identical to arm 1 on tiles with no gate. It is not identical on 75 of the 103
    gate-free tiles. There, up to 68 pixels within 20 m of the tile's top-left corner change, by up to 4 grey levels.
  - **Cause, an edge case in the existing `dark_reference_dehaze`:** with an empty gate,
    `ndi.distance_transform_edt(~gate)` has no zero pixels. SciPy then measures distance from outside the top-left
    corner, so the 20 m fade switches on there.
  - Not fixed: existing modules were not to be edited. It touches only clear cells; the clear control on gated tiles
    is unaffected and agrees.
  - It also means the flood-call tables built with `corrected_table(..., "darkref")` carry the same small corner
    change on gate-free tiles.
- **Three gated tiles are unchanged** (2_20_42, 2_18_41, 2_20_41). They have too little clear ground, so the whole gate
  is opaque and the image is left as it is.
- **Code moved on before the run.** HEAD moved from 5d325d9, the commit named in the plan, to 5be95c2 when another
  agent added `sn8_cloudsym.py`. No existing module changed: `git diff 5d325d9 5be95c2 -- ClaudeFunctions` lists only
  that file, and no module file changed during the run.
- **Docstring added after the run.** The results paragraph in `sn8_cloudroads.py`'s docstring was written after the
  run. The cache keys hash the functions, not the docstring.
- **Smoke test.** Before the full run, a 12-tile smoke test caught a print-format bug. Only its error lines were read;
  its numbers were not used.
- **`posthoc_tbins` was written after the results** and is labelled post hoc.

## Inference (what the numbers suggest; not tested further)
- **No method recovers the roads, and the detector is the bottleneck.** Under correctable cloud, the after-image
  detectors find about 1% of OSM road cells, de-hazed or not.
  - The threshold-free AUC (0.66 against 0.98 on the before image) says the after-image features carry little
    road signal under the gate. It is not just a cut-off problem.
- **The two-date correction lifts brightness but not 2 m detail.** This matches the 2026-10-25 local-contrast check on
  real cloud: 2.1 as it is, 3.5 corrected, 7.4 before. Edge, ridge and linear features need that detail.
- **The after-image detector is weak even in clear sky** (recall 0.21 against 0.68 before). Two likely reasons
  (inference):
  1. flooded roads really do disappear on the after image (6.5% found against 37% for roads not labelled flooded);
  2. its training cells include cloudy and flooded road cells, which teach it to be conservative.
  So "find roads on the after image" mixes three causes of invisibility: water (real change), cloud and look angle.
- **Single-image de-hazing:** it calls a few more road cells, but with more false alarms and a measurable loss in clear
  sky. Two-date leaves clear sky alone (by design) but is slightly worse in the fade margin.
- **Per road:** de-hazing makes none of the 151 set-aside roads visible to the detector. The before image sees 89 of
  them. So a road's location under cloud has to come from the before image or the map, not from the after image.

## What goes wrong, and what to fix
1. **Using the after image to say where a road is cannot work under cloud with this detector.** For the cloud
   decision, locate roads from the before image or OSM (as production does). Keep the after image for change only.
   - This test supports keeping CORRECT roads as "cannot assess" for road finding.
   - Whether the de-hazed after image is good enough for a flood call is the separate flood-call test (evidence 01).
2. **If after-image road finding is wanted (e.g. new roads), train the detector on clear, unflooded after-image
   cells.** The labels for cloudy and flooded cells say "road" where nothing visible is road. Then re-test under thin
   cloud, with a plan written first.
3. **Recover 2 m detail, not just brightness.** Options from the reconstruction literature (evidence 05):
   - reference-guided detail transfer, which uses the before image's structure and needs a no-copy safeguard;
   - learned de-hazing.
   Judge any option first label-free, with local contrast against the before image, before scoring it on roads.
4. **Fix the empty-gate edge case in `dark_reference_dehaze`:** set fade = 0 when the gate is empty. Do it in the
   cloud repo when the cloud code moves, then rebuild the "darkref" caches.
5. **Report "cannot assess" honestly.** Under the gate, even the best after-image arm sees under 5% of road cells
   where t is 0.6-0.8, and none where t is below 0.4.
