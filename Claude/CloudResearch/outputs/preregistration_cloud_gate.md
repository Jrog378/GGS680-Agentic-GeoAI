# Test plan: the cloud gate on either date, and faint haze (written before running)

Written 2026-10-25 18:40 EDT, before any score was computed. Only a crash test was run: one tile, timings and
column names printed, no values.

**Code:**
- GeoAI-Roads `5be95c2` adds the new module `ClaudeFunctions/sn8_cloudsym.py` (sha256 `cbe503f9…894d`).
- The existing modules are unchanged from `5d325d9`.

**Scripts** (in `evidence/pilot_scripts/cloudgate/`):
- `run_synthetic.py` (sha256 `43e05db5…b215`);
- `run_regression.py` (`dedd97ed…409f`);
- `run_real.py` (`69e7703f…ba65`);
- `summarise.py` and `figures.py`, written after this plan and before any output is read. They do only what this plan
  says.

**Justin (2026-10-25):**
- "Before images can still have clouds though".
- "This might help us to bring more roads into the visible pile rather than being placed aside".
- Design rule: if edges are present before but not after, it could be cloud. Then we should either leave it out of the
  analysis or try to see through it.

## Status
**Exploratory, development data only. Nothing is promoted.** The production cloud rule (tile rule + road rule) was
Justin's decision, and it stays.
- Nothing here changes after the results are seen. Every result is reported, whatever it is.
- Any departure from this plan is written up in `evidence/07_cloud_gate_either_date.md`, not by editing this file.
- Synthetic haze is used only for checks with a known answer, never as training labels. Whether it may ever be used
  as a label is Justin's ruling, and that ruling is still open.

## Data (development only)
- **Tiles:** the training and validation tiles of `split_tables(662)` (186 + 40 = 226).
  - No test tiles, no north negative set, no Germany, no Louisiana-West and no HRC_WHU test images.
  - `allow_held_out` is never passed.
  - The scripts assert that every tile they process is a training or validation tile.
- **Clear tiles for the synthetic checks:** `clear_tiles()`, the 94 development tiles with under 1% of their pixels
  under the dark-rise and bright masks. These are the same tiles, in the same order and with the same seeds, as
  `haze_recovery`.
- **Roads:** `feature_table` + `cloud_table` for train and val (1,037 roads in the earlier runs).
  - **Set-aside roads:** the roads that production's cloud rule (`assessable`, tile rule + road rule) leaves out.
    The earlier runs counted 239.
  - **Labels:** road geometry comes from the label files of development tiles (as `road_handling` does).
  - **Flood attribute:** used only to split synthetic-haze pixels into changed and unchanged ground (S1, S2). It never
    enters a gate or a decision.
  - **Building footprints** (published SpaceNet 8 labels, unmodified, development tiles): used only to check that
    houses do not come into the gate.
- **Greyscale** only.

## What is tested (`sn8_cloudsym.py`)
1. **Per-date cloud.**
   - **Change gates.** Let d = dark after − dark before.
     - A rise (d > 71, the dark-rise Otsu cut) means cloud in the after image.
     - A fall (−d > 71) means cloud in the before image.
     - Each gate keeps only blobs of at least 2,500 m².
   - **Single-date masks:** dark channel > 98 (the single-date Otsu cut), blobs of at least 2,500 m², on each date.
   - **Both cloudy:** where the two single-date masks overlap, in blobs of at least 2,500 m².
   - **Labels:** 3 = both cloudy; else 1 = after cloudy (rise); else 2 = before cloudy (fall); else 0 = clear.
2. **Correction.**
   - Each cloudy date is corrected inside its own gate, with the other date as the reference. The arithmetic is
     `dark_reference_dehaze`'s.
   - One difference: the clear pixels for the tone curve leave out every gate, not only the rise gate.
3. **Cannot assess:**
   - both dates cloudy;
   - opaque (t < 0.2) on either date;
   - or a gate on a tile with under 1,000 clear pixels.
4. **Task B, hysteresis.**
   - 71 stays the high threshold. The gate grows into connected pixels whose change (same sign) is above a low
     threshold of **50, 35 or 20** grey levels.
   - **"Seed" rule (primary):** the 2,500 m² minimum applies to the seed blob above 71, which is today's gate. Then
     that blob grows.
   - **"Grown" rule (secondary):** any blob above the low threshold with at least one pixel above 71, kept if it is at
     least 2,500 m² once grown.

### Arms
| Arm | What |
|---|---|
| as it is | no correction |
| existing two-date | `dark_reference_dehaze` (today's code: cloud only in the after image) |
| single image (He) | `dehaze` (He, Sun & Tang 2011), the published baseline |
| either-date | `either_date_dehaze`, both-cloudy rule "dark" (the module's default) |
| either-date, both smooth | the same, with both dates also locally smooth (local std < 10 in ~10 m) for both-cloudy |
| hysteresis 50 / 35 / 20, seed | either-date with the seed hysteresis gate (task B, primary) |
| hysteresis 50 / 35 / 20, grown | either-date with the grown hysteresis gate (task B, secondary) |

## Scenarios with a known answer (94 clear tiles; haze as `synthetic_haze`, t down to 0.35, A = 240)
- **S1, haze on the after image:** seed 662 + the tile's position (exactly `haze_recovery`'s). This is the
  no-regression check, and task B's test.
- **S2, haze on the before image:** the same haze field (same seed) on the before image, with the clear after image
  as the only other date. This is task A's test.
- **S3, haze on both dates:**
  - the before image gets field 662 + position;
  - the after image gets field 662 + position + 5000.
  - True labels per pixel: after only, before only, both (t < 0.95 on that date) or neither.

**Definitions** (as `haze_recovery`):
- **haze region:** true t < 0.95;
- **clear ground:** over 40 m from any true t < 0.999;
- **grey error:** RMSE against the clear original over the haze region, per tile, then the mean over tiles;
- **detail kept:** median local contrast (5 m) of the corrected image over that of the clear original, under the haze;
- **clear ground changed:** the share of clear-ground pixels with t < 0.95 for the date being corrected;
- **detection:** pixel F1 of the label for the hazed date (S1: "after cloudy"; S2: "before cloudy") against the haze
  region. TP, FP and FN are summed over tiles (pooled F1), and the median per-tile F1 is also given.
- **Changed and unchanged ground:**
  - changed: the haze region inside the strips of roads labelled flooded;
  - unchanged: the haze region inside the strips of roads not labelled flooded, on the same tiles. On these clear
    tiles those labels can be trusted.

## Outcomes, task A (either date)
**Primary:**
1. **A-1:** S2 grey error under the before-image haze, either-date against "as it is". "As it is" is also what today's
   code leaves, since it never corrects the before image. Exact two-sided sign test over the 94 tiles.
2. **A-2, symmetry:** pooled F1 of "before cloudy" in S2 against pooled F1 of "after cloudy" in S1, same arm, same haze
   fields. **Criterion:** they differ by at most 0.05.
3. **A-3, no regression:**
   - (i) `haze_recovery` rerun as it is (`run_regression.py`) matches the archived `haze_recovery.csv`: the largest
     per-tile difference is at most 0.001 in every column;
   - (ii) in S1, the either-date corrected after image is identical (max difference ≤ 0.001) to
     `dark_reference_dehaze`'s on every tile with no fall-gate and no both-cloudy pixels;
   - (iii) S1 means for either-date against existing two-date: grey error within 0.5, detail kept within 0.01, clear
     ground changed within 0.001. Any difference is reported with its cause.

**Secondary (descriptive):**
- S2 detail kept, t error and clear ground changed, against He.
- S2 share of the AFTER image altered (it should be 0).
- S2 and S3 with today's code, to show what it misses.
- **Changed ground, S2:** pooled grey error on flooded and on dry strips under the haze, per arm.
  - Per tile, the share of the error removed (1 − error ÷ error as it is) on flooded against dry strips, on tiles with
    at least 500 pixels of each. Paired sign test.
  - He's share on the same pixels, as a control, since He does not use the other date.
  - The same for S1, where the before image, the reference, shows the pre-flood ground.
- **S3:** the 4 × 4 label confusion matrix (truth × label), pooled.
  - The share of the true both-cloudy region marked cannot assess.
  - The share of one-date haze marked cannot assess.
  - The grey error of each date in its own one-date haze region.
  - Both both-cloudy rules.
- **Real development tiles (226), label-free.** Development before images are cloud-free, so every fall-gate or
  both-cloudy pixel there is a false alarm or faint before-image haze. Reported:
  - the share of pixels in each label and marked cannot assess (by reason);
  - the same on the 94 clear tiles;
  - the building pixels marked both cloudy or cannot assess.

## Outcomes, task B (faint haze)
**Primary:** S1 grey error, each seed hysteresis arm (50, 35, 20) against either-date (today's gate inside the
module). Exact two-sided sign test over the 94 tiles, Holm-adjusted over the three.

**Constraints:** a threshold meets the plan only if all of these hold, as well as the primary result:
- S1 clear ground changed, mean over tiles, at most 0.01;
- on the 94 real clear tiles, the mean share of pixels gated at most 0.01;
- on the same tiles, the share of building pixels gated (pooled) at most 0.01.

**Secondary (descriptive):**
- S1 detail kept, t error and detection F1;
- the gap to He (mean grey error minus He's);
- the grown arms;
- the hysteresis arms in S2;
- on all 226 real development tiles, the gated share and the building pixels gated.
- **Roads, label-free:**
  - every development road's decision (ASSESS / CORRECT / CANNOT ASSESS, `road_handling`'s rule: CANNOT ASSESS when at
    least 20% of its strip cannot be assessed, CORRECT when at least 20% is gated) under existing two-date and under
    each arm;
  - transition counts from existing two-date to each arm.
- **Set-aside roads (239):**
  - how many would come back under each arm. "Come back" means ASSESS or CORRECT;
  - split by why each was set aside: on a cloudy tile (tile rule), or by the road rule only.
  - This counts what the handle step would allow. It says nothing about whether their flood calls would be right,
    and they are not scored.
- **Edge loss** (Justin's design rule): edge loss = edge before − edge after (`−edge_change` from `feature_table`).
  - Among the quarter of development roads with the most edge loss: the share with at least 20% of the strip gated,
    per arm.
  - The earlier figures (15% caught by the cloud rule, 42% with the dark channel up by more than 20) are recomputed
    first, to check the definitions.

## Statistics
- **Sign tests:** exact two-sided binomial on the tiles where the two arms differ (ties dropped).
- **Mean differences:** a 95% interval from resampling whole tiles (5,000 resamples, seed 662).
- **Holm adjustment:** only for B's primary outcome.
- Everything else is descriptive.
- There is no road-level flood scoring in this test.

## Pictures (rules fixed now)
- **A, synthetic:** the clear tile with the most flooded-road strip pixels under the S2 haze.
  - Panels: before (the answer), before with synthetic cloud, after (the reference), labels over the hazy before,
    corrected before (either-date), single-image He, and the error maps.
- **A, real (what fires):** the development tile with the largest share labelled before cloudy or both cloudy by
  either-date.
  - Panels: before, after, labels, both dark channels.
- **B, real:** among the development tiles the tile rule scores (not cloudy), the one with the most pixels added by
  hysteresis 35 (seed) over either-date.
  - Panels: before, after, today's gate and the grown gates (50 / 35 / 20), corrected after with today's gate and
    with 35.
- **B, synthetic:** the clear tile whose S1 haze share is closest to the median haze share.
  - Panels: true t, today's gate, the grown gates, and the error maps for either-date, hysteresis 35 and He.
- Saved as PNGs in `evidence/pilot_scripts/cloudgate/` (imagery is not committed).

## Known before running (from reading the code, not from results)
- **Empty-gate quirk in `dark_reference_dehaze`.** With an empty gate, `distance_transform_edt(~gate)` has no zero to
  measure from, and scipy then returns finite distances from beyond the top-left corner. So the existing fit applies
  its t within about 40 pixels of that corner on tiles with no gate.
- `sn8_cloudsym` returns such tiles unchanged.
- In S1 every hazed tile is expected to have a gate, so this should not touch the regression check. It is reported
  if it does.
