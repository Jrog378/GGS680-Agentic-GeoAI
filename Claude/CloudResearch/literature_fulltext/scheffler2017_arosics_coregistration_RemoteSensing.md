# Coder handoff: Scheffler et al. 2017, AROSICS (Remote Sensing 9(7), 676)

**Citation:** Scheffler, D., Hollstein, A., Diedrich, H., Segl, K., & Hostert, P. (2017). AROSICS: An automated and
robust open-source image co-registration software for multi-sensor satellite data. *Remote Sensing* 9(7), 676.
doi:10.3390/rs9070676. **Copy:** publisher's CC BY version via HU Berlin edoc (MDPI itself returned 403). 21 pp.
PDF: `/Users/jusrogers/Masters/papers/scheffler2017_arosics_coregistration_RemoteSensing-summary.pdf` (page 1 = AI summary).
**Read:** pp. 1–21. Written by Claude, 2026-10-29. Software: GPLv3 (p. 18), `pip install arosics`.

## Algorithm (local co-registration), exact steps
1. **Input prep (pp. 4–6):** one band per image (reference band with minimum spectral distance to the target band, else
   band 1). No-data mask auto-derived (3×3 corner windows); combine with user cloud/shadow masks into 1-bit bad-data
   masks per image. "it is always reasonable to provide a mask of areas with non-opaque clouds" (p. 5). Overlap
   polygon from footprints.
2. **Grid equalisation (p. 6):** resample the **finer** image down to the coarser grid (cubic, not nearest, to avoid
   positional artefacts). Matching is done at the coarser resolution.
3. **Tie-point grid:** regular grid, user-set spacing (the only obligatory parameter besides the two images).
   Matching window default **256 × 256 px**, constant size; shrunk at overlap edges so it never contains no-data (p. 7).
   Nodes on bad-data are skipped.
4. **Shift per window (pp. 7–8):** FFT both windows; normalised cross-power spectrum; inverse FFT; integer shift = peak
   position minus centre. Move the target window by the integer shift, recompute cross-power, sub-pixel shift from the
   peak value v(0,0) and its X/Y neighbours v(1,0), v(0,1) (Eqs. 1–2, after Foroosh et al. 2002):
   Δx = v(1,0) / (v(1,0) ± v(0,0)), Δy = v(0,1) / (v(0,1) ± v(0,0)) (sign per Foroosh; see ref. [19]). Total shift =
   integer + sub-pixel, converted to map units.
5. **Validation (pp. 8–10), in order:**
   1. Integer-shift check: after applying the integer shift the recomputed integer shift must be 0; else iterate,
      max **5** iterations, else the node fails.
   2. Length cap: reject shifts > **5 reference pixels** (optional).
   3. Peak reliability (Eq. 3): μ_peak = mean of v over the 3×3 around the peak; μ_remain, σ_remain = mean and std of
      the rest of the spectrum; **R = 100 − 100·(μ_remain + 3σ_remain)/μ_peak**; reject R < **30 %**.
   4. MSSIM check: SSIM of the window pair before and after applying the sub-pixel shift; reject if it **decreases**.
   5. RANSAC with an affine model over all surviving points; inlier threshold tuned iteratively until **10 ± 2 %** of
      points are outliers.
6. **Correction (p. 10):** affine (from the surviving tie points), cubic warp, single resampling. Global mode instead
   applies one X/Y shift, optionally by geocoding only (no resampling).

## Results to compare to (pp. 11–17)
- INTER1 S2 (10 m) vs Landsat-8 (15 m pan-sharpened), ~50 % thick cloud, **no cloud mask**: false TPs removed by
  reliability 381, RANSAC 123, MSSIM 17; false TPs "almost exclusively located at cloudy positions" (p. 11). RMSE of
  detected shifts 34.63 m → 4.45 m (2.31 → 0.30 px).
- INTER2 RapidEye (5 m) vs Landsat-8 (30 m), mountains: 13.69 → 4.55 m (0.15 px at 30 m).
- INTRA2 TerraSAR-X multi-date: 11.54 → 0.89 m (0.32 px).
- **Caveat:** RMSE is computed from AROSICS's own re-detected shifts after correction (p. 15), i.e. internal
  consistency, not independent check points. No ground-truth accuracy assessment.
- Speed: ~2000 tie points in < 1 min on 32 cores.

## Stated limitations
- Assumes roughly matching, georeferenced inputs; affine model only: "deviations from the affine model, e.g., caused by
  topographic effects, decrease registration accuracy" (p. 17); residual directional patterns remain (p. 16).
- Rotation not handled (needs Fourier–Mellin; p. 18). Cloud masks may be misclassified (p. 10).
- Never tested at sub-metre resolution or with off-nadir building lean.

## How to apply to our pipeline / Ida test
- **Module:** `ProjectBranch/ClaudeFunctions/sn8_coreg.py` (currently: one translation per tile by phase correlation on
  gradient magnitude, quadrant agreement check, MAX_SHIFT_M cap). Add a local mode for the Ida test (pre-registration
  data-prep step 5 → Revision 1 item 4):
  - grid of windows over the tile (e.g. 256 px = 128 m at 0.5 m; spacing 128 px), skipping windows whose bad-data share
    (cloud gate on the satellite tile ∪ NOAA bright mask ∪ no-data) exceeds a fixed cap;
  - per window: our existing phase correlation (keep gradient magnitude input: helps with the RGB-aerial vs satellite
    tone difference); compute R (Eq. 3) and reject R < 30 %; reject if SSIM does not increase after the shift; reject
    length > 5 px (or our MAX_SHIFT_M);
  - RANSAC: fit translation (and optionally affine) to surviving vectors, 10 ± 2 % outliers;
  - **report per tile:** number of valid windows, median and spread of local shifts, RMSE of residual shifts after
    correction (label it "internal residual, AROSICS-style"), and drop tiles with residual > 1 px as Revision 1 says.
  - Prefer **translation only** for the score (no warping of image content) unless the residual pattern is clearly
    affine; an affine warp cannot fix building lean, so score road strips (Revision 1 item 5).
- **Option B:** run the `arosics` package itself (COREG_LOCAL with `mask_baddata_ref/tgt`). GPLv3: fine for a research
  script; do not vendor it into the library without Justin's OK.
- **Feasibility on our data:** good. Grey 0.5 m satellite vs NOAA RGB→grey resampled to 0.5 m; masks available. Risk:
  relief displacement from off-nadir view ⇒ local shifts differ on roofs vs ground; restrict windows to ground-heavy
  areas or use road-strip masks as the "good" mask.
