# Test plan: does the cloud pipeline recover the ground NOAA's aircraft saw? (written before any photo is compared)

Written 2026-10-29, while the NOAA photos are still downloading. No photo has been aligned or compared with a
satellite tile; only metadata and four low-resolution previews have been looked at (evidence 17). Results and
deviations go in `evidence/18_ida_clear_view.md`, not here.

Justin (2026-10-29): "lets note somewhere that to truly test this method we have to adopt a different dataset / test
area / study objective" · "look further into the strongest combination suggestion" · "go ahead with the ida plan".

## Status
**Exploratory, development data only** (Louisiana-East train + val, 226 tiles). Test, north negative and sealed tiles
(Germany, Louisiana-West) are not read. Nothing is promoted from this test on its own; every result is reported,
whatever it shows.

## Objective and truth
- **New study objective:** recover what the ground looked like under the cloud, instead of scoring flood labels that
  were made without seeing under it (evidence 16).
- **Truth:** NOAA NGS emergency-response aerial photos of Hurricane Ida (public domain; flights 30 Aug – 2 Sep 2021;
  `/Volumes/USB2025/GeoAI-Descriptions/data/ida/noaa_eri_ida2021/`). They were flown below the cloud. They are a
  reference image, not a human label; the label rule is not involved.
- **Target variable:** per pixel and per road strip, how close the post image is to the NOAA photo of the same place:
  (primary) DINOv2 patch-feature distance, the representation our change detector uses; (secondary) grey-level error
  and edge agreement.
- **Not in this test:** flood depth per road from USGS high-water marks and 3DEP lidar. It is a derived label; it waits
  for Justin's decision.

## Data preparation (fixed before comparing)
1. **Tiles:** development tiles whose post image is at least 50% covered by valid NOAA pixels (no-data excluded).
   Cloudy tiles are the 56 with cloudy roads (production gate); clear tiles serve as the guard.
2. **Flight:** for each tile, the flight with the most valid pixels; ties go to the earlier date. The satellite date
   (catalog `10300100C46F5900`) is confirmed first if possible; the gap per tile is reported.
3. **Resampling:** NOAA RGB reprojected to each tile's grid (its CRS and 0.5 m-class pixels), averaging (area) down.
4. **Grey and tone:** NOAA RGB to grey with the same weights as the SpaceNet greyscale copy; then a monotone tone
   curve from NOAA grey to satellite grey, fitted per tile on pixels that no cloud mask flags and that are valid in
   both. The curve is fitted once and frozen for every arm.
5. **Alignment:** one shift per tile by phase correlation on clear pixels (the existing co-registration module),
   applied only where its quadrants agree, as in production. Tiles that fail alignment are reported and dropped.
6. **NOAA's own cloud and glare:** NOAA pixels flagged by the bright rule are excluded from every metric.

## Arms (all on the same tiles and pixels)
- **as is:** the satellite post image, no de-hazing.
- **He 2011:** single-image de-hazing (sn8_clouds.dehaze), the published baseline.
- **two-date:** production's two-date de-hazing with the 20 m fade (sn8_cloudsym.either_date_dehaze).
- **two-date + spotter gate:** two-date inside the trained spotter's mask instead of the dark-rise gate (research only:
  HRC_WHU licence).

## Regions scored
- **Thin cloud:** inside the cloud gate with t ≥ 0.2 (what the pipeline corrects).
- **Opaque:** t < 0.2 (what the pipeline calls CANNOT ASSESS).
- **Clear guard:** outside every cloud mask.
- Each also per road strip (the learned road band around each OSM road).

## Outcomes
1. **Primary:** mean DINOv2 patch-feature cosine distance to the NOAA photo inside thin cloud, two-date minus as is.
   Pass: negative (closer), with a 95% interval below 0.
2. **Against the baseline:** the same, two-date minus He 2011 (reported both ways; no direction assumed).
3. **Guard:** on clear ground, two-date must not move the image away from NOAA: difference to as is within ±0.01
   (feature distance) and grey change below 1 grey level on average. He 2011 is reported on the same guard.
4. **Honest gate:** within the cloud gate, feature distance after two-date should be larger where t < 0.2 than where
   t ≥ 0.2 (CANNOT ASSESS marks ground that was not recovered): AUC of t for "recovered" (distance below the clear
   guard's 95th percentile), reported with its interval.
5. **Cloud detection:** where the tone-matched satellite and NOAA disagree beyond the clear guard's 99th percentile,
   F1 of the dark-rise mask and of the spotter. Caveat: disagreement also includes real change in the 0–2 days between
   passes, parallax and moving objects, so this is an upper-noise check, not a cloud label.
6. **Change seen under cloud:** per road strip, the DINOv2 change cue pre vs post for each arm, against pre vs NOAA:
   Spearman correlation over cloudy roads, and the same on clear roads as the ceiling.
7. **Secondary:** grey error and edge (gradient) correlation, same regions and arms.

## Statistics
- Unit: the tile (pixels within a tile are not independent). Per-tile means, paired across arms.
- 95% intervals: 2,000 bootstrap resamples of the 3 × 3 tile blocks from evidence 14; Wilcoxon signed-rank across
  tiles as a check. Holm's correction across the three pairwise arm comparisons in outcome 1–2.
- A p-value goes on a slide only if it is significant; otherwise the slide says what we will do next.

## Known risks (reported, not fixed after the fact)
- Different sensor, view angle and resolution: tone matching and alignment may leave residual error everywhere; the
  clear guard measures it.
- Date gap: water receding or debris moved between passes reads as error; reported per flight.
- Partial NOAA coverage and no-data; tiles below 50% coverage are dropped and listed.

## Revision 1 (2026-10-29, still before any photo is aligned or compared; from evidence 19)
Adopted:
1. **Call-level outcome (after M3R-CR, Xu et al. 2024 TGRS).** Run the frozen production road detector on the
   tone-matched NOAA grey image; per arm, agreement of per-road calls with the NOAA-image calls on cloudy roads, with
   clear roads as the ceiling. Reported next to the primary outcome.
2. **No arm is chosen on grey error** (SEN12MS-CR; AllClear rank flips between pixel and task metrics). Feature
   distance stays primary.
3. **Date-gap noise floor:** where two NOAA flights overlap a tile, NOAA against NOAA on clear ground.
4. **Local co-registration:** a moving-window shift grid with cloud masked out (AROSICS-style), residual shift reported
   per tile; replaces the single shift per tile in step 5 of data preparation. Tiles with residual > 1 px are reported
   and dropped.
5. **Road strips first;** building and tree pixels reported separately (view-angle lean). The satellite's off-nadir
   angle is recorded if it can be found.
6. **NOAA's own cloud and glare masked before** the tone fit and the alignment, not only in the metrics.
7. **Tone curve on unchanged pixels only:** IR-MAD/PIF-style no-change selection, so flood darkening is not absorbed.
8. **Label gap reported as a finding:** count cloudy roads that look flooded in the NOAA image (by the frozen
   detector) against the 27 marked flooded under cloud. Not used as a score.
Optional (if time): spread of the two-date output across a fixed set of gate settings as an uncertainty, tested as a
predictor of distance to NOAA (after Ding et al. 2024).
Not adopted now: the flood-depth margin (0.5 m / 0 m, bridges flagged, peak vs image day, lidar date) waits for
Justin's decision on derived labels.
