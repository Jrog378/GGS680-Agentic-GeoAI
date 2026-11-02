# 07: The cloud gate on either date, and faint haze (2026-10-25; exploratory, development data only)

Our own measurements, not literature.

**Setup:**
- **Plan:** written first, at 18:40 EDT, before any score: `outputs/preregistration_cloud_gate.md`.
- **Code:** GeoAI-Roads `5be95c2`. It adds the new module `ClaudeFunctions/sn8_cloudsym.py`; every existing module is
  unchanged.
- **Scripts and outputs:** in `evidence/pilot_scripts/cloudgate/`, with their logs, CSVs, `numbers.json` and PNGs.
  - `run_synthetic.py` took 309 s, `run_real.py` 331 s and `run_regression.py` 273 s.
  - The pre-registered tables come from `summarise.py`.
  - `posthoc.py` and `posthoc_airlight.py` are checks not in the plan, written after the results were seen. They are
    marked **post-hoc** below.
- **Data:**
  - the 226 training and validation tiles of `split_tables(662)`;
  - the 94 clear development tiles for the synthetic checks;
  - the 1,037 development roads.
  - No test tile, north negative tile, sealed area or HRC_WHU test image was read. `allow_held_out` was never passed.
  - Greyscale only.
- **Labels:** the flood labels were used only to split synthetic-haze pixels into changed and unchanged ground, and in
  one post-hoc diagnostic. The building footprints were used only for the houses check.
- **Status:** nothing is promoted. The production cloud rule (tile rule + road rule) stays.

## In short
**Evidence:**
- **Task A, either date, works on synthetic cloud.** Cloud put on the BEFORE image is found and removed about as well
  as cloud on the after image:
  - grey error 54.3 → 37.4, better on 92 of 94 tiles (2 ties), p = 4e-28;
  - detection F1 0.45 against 0.47 for the after image;
  - the after image is untouched (0% altered).
- **No regression.** `haze_recovery` reruns identically. On the 71 tiles with no before-date or both-date label, the
  after-image correction is identical, pixel for pixel. Mean grey error is 37.24 against 37.28.
- **Task A misfires on real data.** The before-cloud gate fires on 29 real development tiles whose before images are
  cloud-free (20 of them on the 94 clear tiles). The both-cloudy rule fires on bright calm water. On the development
  data, task A brings back **no** set-aside roads; its 20 moved roads go from ASSESS to CORRECT.
- **Task B, faint haze.** The hysteresis gate cuts the synthetic grey error significantly at every threshold:
  - 37.3 → 33.8 / 31.9 / 31.2 at 50 / 35 / 20;
  - Holm p ≤ 2e-17, better on 85-88 of 94 tiles;
  - the gap to single-image He shrinks from 10.0 to 6.5 / 4.6 / 3.9.
- **No threshold meets the plan's constraints.** Clear ground changed is 3.7% / 13% / 26%, against a limit of 1%.
- **On the real clear tiles, the seed rule adds no after-date gate at all.** Their gating comes from task A's
  before-date gate growing.
- **Set-aside roads:**
  - 151 of the 239 would come back under the existing two-date handle step already (136 CORRECT, 15 ASSESS);
  - 150 with either-date;
  - 144 / 145 / 117 with hysteresis.
  - So neither A nor B brings more roads back on these tiles. The hysteresis gate moves clear-sky roads into CORRECT
    instead (117-284 of the 798 assessable roads).

## Task A: cloud on either date

### S2, synthetic haze on the BEFORE image (94 clear tiles)
| Arm | Grey error | Detail kept | t error | Clear ground changed | Detection F1 (P / R) |
|---|---|---|---|---|---|
| as it is | 54.3 | 0.78 | - | - | - |
| existing two-date (today's code) | 54.3 | 0.78 | 0.28 | 0% | 0 (it never looks) |
| single image (He) | 27.8 | 0.87 | 0.13 | 91% | - |
| either-date | 37.4 | 0.97 | 0.16 | 1.4% | 0.45 (0.95 / 0.30) |
| either-date, both smooth | 37.3 | 0.97 | 0.16 | 1.4% | 0.45 |

- **A-1 (primary):** either-date against as it is. Better on 92 tiles, worse on 0, 2 ties. p = 4.0e-28. Mean −16.9
  grey levels (95% CI −18.7 to −15.0).
- **Against He:** He is lower on 70 of 94 tiles (p = 2e-6, mean +9.6). This is the same gap as in the after-image case,
  where it is 10.0.
- **Today's code** leaves before-image cloud alone. It also does not touch the after image (0% altered), so the
  only failure is that it is blind.
- **The either-date method alters 0% of the after image** in S2. The grown hysteresis arms alter 1.7-7%, because
  they grow small after-date blobs.
- **A-2, symmetry (pooled F1):**
  - before cloudy 0.453 against after cloudy 0.474, a difference of −0.021. **The criterion (|difference| ≤ 0.05)
    holds.**
  - It holds for every arm (−0.048 to +0.009).
  - Recall is only 0.30 in both directions. The 71 cut catches the haze core, not the fringe (true t up to 0.95).
    That is task B.
- **Clear ground changed 1.4%.** In S2 this comes from real before-date gates on the clear tiles (see "Real tiles"
  below), not from the synthetic haze.

### A-3: no regression (S1, synthetic haze on the after image)
- **(i)** `haze_recovery` rerun as it is against the archived `haze_recovery.csv`:
  - the largest per-tile difference in any column is 4e-6 (float rounding);
  - every mean is the same (as it is 56.93; He 27.28; two-date 37.24, detail 1.024, clear ground 0.0002).
  - **Holds.**
- **(ii)** Tiles with no before-date gate and no both-cloudy pixels: 71 of 94. On all 71 the either-date corrected
  after image is identical to `dark_reference_dehaze`'s (largest difference 0.000). The after-date (rise) gate is
  identical on all 94. **Holds.**
- **(iii)** Means, either-date against existing:
  - grey error 37.28 against 37.24;
  - detail kept 1.023 against 1.024;
  - clear ground changed 0.00018 against 0.00018.
  - All are within tolerance. **Holds.**
- **The 23 tiles that differ** (in their means) differ for two reasons:
  - both-cloudy pixels are left as they are (cannot assess under the haze, 4.9% against 2.7%);
  - the tone curve now leaves out the before-date gates.

### Changed ground: does the method fail where a flood changed the ground?
The test pixels are the synthetic haze over the strips of roads labelled flooded. The comparison is the strips of
roads not flooded, on the same tiles. Only 12 tiles have at least 500 pixels of each.

| Pooled grey error under the haze | flooded strips: as it is → corrected | dry strips: as it is → corrected |
|---|---|---|
| S2 (before hazy; after = the flooded reference), either-date | 39.9 → 26.3 (−34%) | 37.3 → 24.8 (−33%) |
| S2, single image (He) | 39.9 → 22.2 | 37.3 → 25.1 |
| S1 (after hazy; before = the pre-flood reference), either-date | 55.4 → 38.1 (−31%) | 54.6 → 37.8 (−31%) |

- **Per tile**, either-date removes a median 23% of the strip error on flooded strips and 21% on dry ones. Flooded is
  worse on 6 tiles and better on 6 (p = 1.0; mean difference −0.05, CI −0.25 to +0.16).
- **Against He,** the difference-in-differences is not significant (7 against 5 tiles, p = 0.77).
- **Evidence:** no measurable extra failure on flooded ground. Only 12 tiles were available, so this is low power.
- **Inference:** only the reference's dark channel enters t, and floods barely move the dark channel. So a flooded
  reference does little harm to t.
- **Not tested:** a flood that brightens, or one bigger than the tone-curve's clear ground.

### S3: synthetic haze on BOTH dates (pooled pixels; row shares)
| Truth \ label | clear | after cloudy | before cloudy | both cloudy (cannot assess) |
|---|---|---|---|---|
| clear | 0.982 | 0.000 | 0.011 | 0.007 |
| after only | 0.690 | 0.277 | 0.001 | 0.032 |
| before only | 0.653 | 0.000 | 0.288 | 0.059 |
| both | 0.637 | 0.080 | 0.093 | 0.191 |

- **The both-smooth rule:** the true-both row becomes 0.754 / 0.080 / 0.094 / 0.071, and the false both-cloudy share
  on clear pixels falls from 0.007 to 0.000.
- **In one-date haze**, each date is corrected about as in S1 and S2:
  - after only, 52.7 → 36.5;
  - before only, 52.9 → 36.7.
- **Where both dates are hazy:**
  - only 19% is marked cannot assess (7% with the smooth rule);
  - 17% is corrected against a reference that is itself hazy;
  - 64% is called clear, because equal haze cancels in the change and the single-date cut (98) catches only thick
    haze.

### Real development tiles (226): what the before-cloudy and both-cloudy labels catch
Development before images are cloud-free, so every pixel these labels catch is a false alarm (or faint before-date
haze we cannot confirm).

| Either-date | All 226 tiles | 94 clear tiles |
|---|---|---|
| tiles with before-date (fall) gate pixels | 29 | 20 |
| mean share of pixels in the fall gate | 0.55% | 1.2% |
| tiles with both-cloudy pixels (dark / smooth rule) | 17 / 3 | 9 / 1 |
| mean share both cloudy (dark / smooth) | 0.48% / 0.02% | 0.98% / 0.02% |
| building pixels marked cannot assess | 4.44% (the same as existing: opaque cores) | 0% |

**Pictures:**
- `fig_A_real_what_fires.png` (rule: the largest before- or both-cloudy share) is 0_19_11.
  - 34% of that tile is "both cloudy". It is a bright, calm water surface seen on both dates. This is the known
    weakness of an absolute dark-channel mask.
  - The smooth rule cuts it to 2.2% of the tile (inference: the after water is textured, so it is not smooth on both
    dates).
- `fig_posthoc_real_fall_gate.png` (**post-hoc**: the largest fall share) is 0_24_20, 17% before cloudy.
  - The before image shows a bright open field and water. The after image is much darker there, and the dark-channel
    change is negative across the whole tile.
  - The before image is then "corrected" toward the after.
  - The fall gates cluster in area 0 (0_24_20, 0_23_20, 0_22_19, 0_14_16, ...).
  - **Post-hoc label check:** 7 of the 20 roads gated mostly on the before date are labelled flooded, against 45% of
    all roads. So this is not a flood signature.
  - **Inference:** it is a tone difference between the dates (the after date is darker) that the raw difference
    reads as cloud leaving.

### Roads (label-free; ASSESS / CORRECT / CANNOT ASSESS as `road_handling`)
- **Check:** this script's decisions for today's two-date gate match `road_handling` on every road (0 mismatches).
- **Existing two-date → either-date:** 21 of 1,037 roads move:
  - 20 go from ASSESS to CORRECT, all from the before-date gate;
  - 1 goes from CORRECT to CANNOT ASSESS (both cloudy).
  - With the smooth rule, 20 move (ASSESS to CORRECT).
- **Set-aside roads (239):**

| Arm | Come back (ASSESS + CORRECT) | of 146 on cloudy tiles | of 93 set aside by the road rule only | CANNOT ASSESS |
|---|---|---|---|---|
| existing two-date | 151 (15 + 136) | 66 | 85 | 88 |
| either-date | 150 | 66 | 84 | 89 |
| either-date, both smooth | 151 | 66 | 85 | 88 |

- **Evidence:** on the development tiles, the either-date method brings back no road that today's two-date handle
  step does not already allow.
- **Inference:** the before images here are clear, so there is nothing for A to recover.
- **What brings 151 roads back** is the handle step itself: correct instead of set aside. Whether those corrected roads
  are then called right is not tested here. The earlier road test found 20 of 24 trusted flooded roads, but with more
  false alarms (evidence 01).

## Task B: faint haze (hysteresis gate)

### S1, synthetic haze on the after image (94 clear tiles)
| Arm | Grey error | Gap to He | Detail kept | t error | Clear ground changed | Detection F1 (P / R) | Better than He (tiles) |
|---|---|---|---|---|---|---|---|
| as it is | 56.9 | +29.7 | 0.82 | - | - | - | - |
| single image (He) | 27.3 | 0 | 0.84 | 0.14 | 85% | - | - |
| either-date (today's gate) | 37.3 | +10.0 | 1.02 | 0.15 | 0.0% | 0.47 (1.00 / 0.31) | 15 |
| hysteresis 50, seed | 33.8 | +6.5 | 1.06 | 0.13 | 3.7% | 0.62 (0.91 / 0.47) | 22 |
| hysteresis 35, seed | 31.9 | +4.6 | 1.09 | 0.13 | 13.2% | 0.66 (0.76 / 0.59) | 27 |
| hysteresis 20, seed | 31.2 | +3.9 | 1.11 | 0.13 | 25.7% | 0.66 (0.63 / 0.70) | 31 |
| hysteresis 50, grown | 32.7 | +5.4 | 1.08 | 0.13 | 4.5% | 0.64 | - |
| hysteresis 35, grown | 30.6 | +3.4 | 1.11 | 0.12 | 14.7% | 0.68 | - |
| hysteresis 20, grown | 30.0 | +2.8 | 1.13 | 0.12 | 27.1% | 0.68 | - |

**Primary** (seed rule against today's gate, grey error, sign test, Holm over three):

| Threshold | Tiles better / worse | Mean change (95% CI) | Holm p |
|---|---|---|---|
| 50 | 87 / 6 | −3.5 (−4.1 to −2.8) | 3e-19 |
| 35 | 88 / 5 | −5.4 (−6.5 to −4.4) | 3e-20 |
| 20 | 85 / 8 | −6.1 (−7.5 to −4.7) | 2e-17 |

- **The grown rule** (secondary) gives −4.6 / −6.6 / −7.2.
- **In S2** (before-date haze), hysteresis does about the same: 37.4 → 34.4 / 32.8 / 31.8.

**Constraints** (all must hold to meet the plan):

| Threshold (seed) | S1 clear ground changed (≤ 1%) | Real clear tiles gated (≤ 1%) | Building pixels gated on those tiles (≤ 1%) | Meets the plan |
|---|---|---|---|---|
| 50 | 3.7% | 3.8% | 0.06% | no |
| 35 | 13.2% | 5.8% | 1.6% | no |
| 20 | 25.7% | 10.0% | 6.5% | no |

- **Post-hoc split of the real-clear gating by date:** with the seed rule, the after-date (rise) gate adds **0%** on
  all 94 real clear tiles. Those tiles have no 2,500 m² seed above 71.
  - All of the 3.8-10% is task A's before-date gate, grown.
  - The grown rule does add after-date gates on clear tiles: 1.6% / 4.6% / 12.2% on 24-34 tiles.
- **Evidence:**
  - the seed rule's real false gating comes from the before-date side;
  - its synthetic "clear ground changed" comes from the grown gate spreading from a real haze blob into nearby clear
    ground. There the dark channel naturally rose by 20-70 between the dates.
- **Caveat:** the "clear" tiles were picked with the 71 cut, so faint haze below it may be real there. The 1%
  constraint treats all of it as error.

### Real tiles and roads
- **Gated share of all 226 development tiles:** 17.1% (existing), 18.1% (either-date), and 26.3% / 34.1% / 42.7%
  (seed 50 / 35 / 20).
- **Building pixels gated:** 19% → 32% / 43% / 55%.
  - On the tiles the tile rule scores: 12% → 26% / 37% / 51%.
  - On cloudy tiles: 89% → 92% / 93% / 95%.
  - A grown gate takes in the houses under the haze along with everything else. That is correct only if the haze is
    real.

**Decisions, existing two-date → hysteresis (seed):**

| | 50 | 35 | 20 |
|---|---|---|---|
| ASSESS → CORRECT | 124 | 205 | 294 |
| CORRECT → CANNOT ASSESS | 7 | 9 | 33 |
| ASSESS → CANNOT ASSESS | 0 | 1 | 9 |
| CANNOT ASSESS → CORRECT | 0 | 3 | 0 |
| set-aside roads back (of 239) | 144 | 145 | 117 |
| assessable roads (of 798) that would become CORRECT | 117 | 196 | 284 |

- **Why 20 loses roads (post-hoc):**
  - on 8 tiles the grown gate covers 98-100% of the tile;
  - so fewer than 1,000 clear pixels are left for the tone curve, and the whole gate is marked opaque (e.g. 2_16_36:
    0% → 100% cannot assess).
- **Edge loss** (Justin's design rule; the quarter of roads with the most edge loss before minus after):
  - **Post-hoc:** the earlier 15% / 42% figures are reproduced on the 891 tile-rule roads (not on all 1,037).
  - On those roads, the share with at least 20% of the strip gated: 15% (existing), 17% (either-date), and
    29% / 39% / 48% (seed 50 / 35 / 20) or 33% / 48% / 61% (grown).
  - On all 1,037 roads (the plan's set): 31% → 33% → 43% / 52% / 57%.
  - So the grown gate takes in the faint-haze roads that lose their edges.
- **Picture** `fig_B_real_faint_haze.png` (rule: the scored tile with the most pixels added at 35) is 2_16_37.
  - The whole after image is under thin haze.
  - Today's gate covers 8.3% of the tile, hysteresis 35 covers 91.1%, and its one road moves from ASSESS to CORRECT.
  - The corrected image is darker, but the forest and road detail come back only faintly.
- **Picture** `fig_B_synthetic.png` (rule: the median haze share) is 0_18_16.
  - Today's gate leaves a ring of uncorrected fringe; the grown gate removes most of it (error 56 → 48; He 35).
  - The thick core is left opaque.

## Pictures
All are in `evidence/pilot_scripts/cloudgate/`, kept out of git.
- `fig_A_synthetic_before_cloud.png` (0_19_18; rule: the most flooded-road strip under the S2 haze):
  - the before-date cloud is found (blue) and lifted, error 45 → 33 (He 26);
  - the after image is a flooded field, and the strip error is worst along the flooded roads at the bottom right.
- `fig_A_real_what_fires.png` (0_19_11): both cloudy on bright calm water.
- `fig_posthoc_real_fall_gate.png` (0_24_20, **post-hoc**): before cloudy on a field that is darker on the after date.
- `fig_B_real_faint_haze.png` (2_16_37) and `fig_B_synthetic.png` (0_18_16): above.

## What goes wrong
1. **False before-date cloud on real tiles.**
   - The fall gate uses the raw change in the dark channel. A darker after date, or wet or flooded ground, reads as
     cloud leaving.
   - It fires on 29 of 226 development tiles, clustered in area 0. The before image is then "corrected" toward the
     after.
   - Inference: where the change is real, that would wash out the very change we want to see.
2. **False both-cloudy on bright water.**
   - The single-date mask (dark channel above 98) fires on bright calm water and large bright ground seen on both
     dates (0_19_11, 34% of the tile).
   - The smooth rule cuts this from 17 tiles to 3. It also halves the true both-cloudy detection in S3 (19% → 7%).
3. **Both dates cloudy is mostly missed.**
   - 64% of truly both-hazy pixels are called clear (S3), and 17% are corrected against a hazy reference.
4. **The gate catches only the cores** (recall 0.30) in either direction. This is B's gap, and why the two-date
   method stays above He.
5. **The hysteresis gate runs across clear ground.**
   - It spreads from a haze blob into nearby clear ground wherever the dark channel rose by 20-70 between the dates
     (S1 clear ground changed 3.7-26%).
   - It also grows A's false before-date gates.
   - At 20, gates covering whole tiles leave no clear ground for the tone curve, so whole tiles go opaque.
6. **Opaque cores in synthetic haze** (post-hoc; inference supported by `posthoc_airlight.log`).
   - The estimated airlight averages 208, against the true 240. So t is underestimated (median 0.27 where the truth
     is 0.35-0.4), and 34% of the thickest haze is left as "cannot assess".
   - The airlight rule (the brightest pixel among the haziest 0.1%) is He's, and the same in today's code.
7. **Empty-gate quirk in `dark_reference_dehaze`** (found by reading the code, before the run).
   - With no gate, scipy's distance transform measures from beyond the top-left corner, so the fit still applies t
     within about 40 px of that corner.
   - This applies to 103 of the 226 development tiles (its corrected image only; the decisions do not use it).
   - `sn8_cloudsym` returns such tiles unchanged. It was not fixed in the existing module, as the rule for this phase
     says.

## What to fix next (proposals, not tested)
- **Before-date gate:**
  - gate on the change after tone matching, dark after − tone(dark before), rather than the raw difference;
  - learn the fall cut on falls (Otsu on the training tiles);
  - then re-measure the real false-alarm rate. The aim is under 1% of the clear tiles' pixels.
  - With no cloudy before image in Louisiana-East, a real before-cloud check needs other data (to be asked for).
- **Both cloudy:** keep the smooth rule (fewer false alarms), and add a water test or a both-dates bright-smooth core,
  so that bright water is not "both cloudy". Measure S3 recall again.
- **Hysteresis:**
  - keep the seed rule;
  - cap how far a gate may grow from its seed (e.g. 40-80 m);
  - when the grown gate leaves too little clear ground, fall back to the seed gate instead of marking the whole gate
    opaque.
  - Then re-test 50 and 35 against the same constraints, on tiles not used to choose the cap.
- **Airlight:** the high quantile of the gated hazy pixels, or a cap from the clear-ground brightest pixels. Test it on
  the same synthetic check.
- **Fix the empty-gate quirk** in `dark_reference_dehaze` when the cloud code moves to its own repo.
- **Bringing roads back** is the handle step's job (correct instead of set aside: 151 of 239 already). The open
  question is whether the corrected roads are called right. That is a road test to pre-register on roads not looked at.

## Departures from the plan (disclosed)
- **Post-hoc analyses**, all marked above: `posthoc.py` and `posthoc_airlight.py`.
  - the rise/fall split on real clear tiles;
  - the largest fall-gate tile and its picture;
  - the edge-loss definition on the 891 tile-rule roads;
  - the flood-label diagnostic of the before-date roads;
  - the opaque mechanism at 20;
  - the airlight check and the empty-gate count.
- **Figures:** `figures.py` was rerun once with taller panels, so that a title was not clipped. The tiles, rules and
  data are unchanged.
- **Code:** the module was not changed after the plan; it is still `5be95c2`.
