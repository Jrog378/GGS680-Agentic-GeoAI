# Coder handoff: Hagolle et al. (2008), Correction of aerosol effects on multi-temporal images with constant viewing angles (Formosat-2)

- **Citation:** Hagolle, O., Dedieu, G., Mougenot, B., Debaecker, V., Duchemin, B., & Meygret, A. (2008). Correction of aerosol effects on multi-temporal images acquired with constant viewing angles: Application to Formosat-2 images. *Remote Sensing of Environment* 112(4), 1689–1701. https://doi.org/10.1016/j.rse.2007.08.016
- **PDF:** `/Users/jusrogers/Masters/papers/hagolle2008_multitemporal_aerosol_correction_formosat2_RSE-summary.pdf` (page 1 = AI summary; HAL cover + manuscript follow)
- **Source:** author's revised manuscript on HAL (CNES/CESBIO), https://hal.science/hal-00265400 (file `Formosat2_aerosols_rse_rev_2.pdf`)
- **Validation:** PDF, 43 pages (Read tool and pdfinfo agree) = HAL cover + 42 double-spaced manuscript pages (text pp. 1–22, appendix p. 23, references pp. 24–26, figure captions pp. 27–40, Tables 1–2 pp. 41–42). Published range is 13 journal pages; difference is manuscript layout. Title/authors/DOI match Crossref; Conclusions (§4) and References present. PASS (author manuscript, not the journal typeset version).
- **Read:** entire manuscript. Figures seen only through captions. Citations below are **manuscript page numbers** (ms p.).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Model and assumptions
- First-order radiative transfer (eq. 1, ms p. 3): `ρ_TOA = t_g · (ρ_surf · T_atm(AOP) + ρ_atm(AOP))` — t_g gas transmission, T_atm atmospheric transmittance, ρ_atm path reflectance, AOP aerosol optical properties. (Same structure as He's haze model: transmission × ground + added light.)
- Two assumptions (ms p. 5): "the aerosol optical properties (AOP) vary quickly with time but usually slowly with location"; "the surface reflectance varies quickly with location but slowly with time (with exceptions that need to be detected before aerosol inversions)".
- Adjacency effect not addressed (ms p. 7).

## 2. Algorithm, step by step
1. **LUTs** (ms p. 6–7): successive-orders-of-scattering code; inverse model = 3rd-degree polynomial fit ρ_surf ↔ ρ_TOA per (AOT, angles, wavelength, altitude). Fixed continental aerosol model (modal radius 0.10 µm, n = 1.44 − 0.003i).
2. **Cost function v1** (eq. 2, ms p. 8): over pixels (i, j) of a neighbourhood and bands λ,
   `Cost = Σ [atmcor(ρ_TOA(i,j,λ,D), AOP_D) − atmcor(ρ_TOA(i,j,λ,D+2), AOP_D+2)]²`, minimised by Levenberg–Marquardt for the two AOTs. Fails when |ΔAOT| < ~0.1 (undetermined: "when TOA reflectances of day D and D+2 are identical, any constant value of the AOT produces identical surface reflectances", ms p. 9), and retrievals are biased low there (appendix: noise after correction grows with AOT).
3. **Cost function v2** (eq. 3, ms p. 10): `K · (eq. 2 term) + Σ [atmcor(D) − ρ̂_surf(D)]² + Σ [atmcor(D+2) − ρ̂_surf(D)]²`, where ρ̂_surf(D) comes from the previous iteration (dates D−2, D). **K ∝ mean TOA change between D and D+2**: big change → the two-date term dominates; small change → the prior keeps it determined. Initial prior: first image corrected with AOT = 0.2. Converges within ~10 images after a 0.15 AOT initial error (Fig. 4).
4. **Formosat-2 processing** (§3, ms p. 14–16):
   - georeference, register, calibrate, remove cloud and shadow; SMAC gas correction;
   - **subsample to 100 m** "to reduce noise and registration errors, and to smooth very local variation of surface reflectances";
   - **7 × 7 neighbourhood of 100 m pixels** (700 m) as the constant-AOT unit;
   - **change screen:** "a threshold on the variation of near-infrared TOA reflectance between two consecutive images. Since the near infrared band is not too sensitive to the aerosol content, a high variation of the TOA reflectance is very likely to come from variations of surface reflectance" (ms p. 15). Causes found: ploughing, harvest, rain-darkened bare soil, spring growth. **The threshold value is not given.**
   - **abstain rule:** "If the number of clear and stable pixels in the neighbourhood is too low (less than 50%), aerosol inversion is not attempted" (ms p. 15; e.g. Tensift after heavy rain);
   - bands used: **488 and 560 nm only** (aerosol-sensitive, surface stable); 650/830 nm made AOT "much more sensitive to surface reflectance variations".
   - each date gets two AOT estimates (as D and as D+2); they agree well.

## 3. How changed pixels are handled (our key question)
- Screened out before the fit by an NIR-change threshold (haze-insensitive band), then the neighbourhood must keep ≥ 50% clear-and-stable pixels or the date is skipped there.
- Residual change acts as "landscape noise": simulations show AOT error rises sharply below a landscape SNR of 100 (Table 1: SNR 50 → RMSE 0.053, bias −0.075; SNR 100 → 0.037, −0.022; SNR 400 → 0.030, −0.004). The authors conclude "an algorithm for detecting abrupt changes in surface reflectance is required" (ms p. 20).
- Semi-transparent cloud missed by the mask is absorbed as aerosol; corrected visible bands look fine but NIR is wrong (Muret forest, 9 Sep and 18 Nov; ms p. 17–18).

## 4. Quantitative results to compare against
- Simulations (Table 2, ms p. 42): nominal AOT RMSE 0.037; uniform landscape (green reflectance std 0.04 → 0.01) RMSE 0.052, bias −0.072; brighter landscape (+0.1 reflectance) RMSE 0.043; one band only 0.052; 5% calibration bias barely affects AOT (0.031) but biases surface reflectance.
- Formosat-2 vs AERONET RMS AOT difference: Muret ~0.08, La Crau ~0.09, Tensift ~0.12 (ms p. 18). Days with unstable AERONET AOT (std > 0.03) excluded.

## 5. Stated limitations
- Cannot run at full resolution (averaging needed) (ms p. 20).
- Uniform or bright surfaces: weaker sensitivity and bias; "probably not adapted to very uniform desert sites" (ms p. 21).
- Fixed aerosol model; dust (Tensift summer) poorly handled.
- Long data gaps need re-initialisation (ms p. 18).

## 6. How to apply to our pipeline
- **`sn8_refhaze` / `sn8_cloudsym` two-date correction:** our method is this paper's v1 idea in image space: choose t so the corrected after-image matches the reference ground (we set the dark channel of the ground from the before date instead of fitting AOT). Lessons:
  1. **Screen changed pixels with a haze-insensitive cue before estimating t.** Their cue is NIR change; we have none. Arms to test: before/after local correlation or gradient-orientation agreement in the window (haze lowers contrast but keeps structure; flood/debris change it). Exclude failing pixels from the t estimate.
  2. **Abstain below 50% stable pixels per window** (their rule). Our current abstain is T_MIN = 0.2 and a 1,000-clear-pixel tile rule; add a per-window stable-share rule with 50% as the starting value.
  3. **Estimate at reduced resolution over a neighbourhood** (100 m pixels, 700 m window, at 8 m native). We estimate t through a 20 m dark-channel window at 0.5 m; the paper supports coarse, smooth haze fields and explicitly says full resolution does not work.
  4. **Bright/uniform ground is weak:** where the before-image dark channel is high or the window is uniform (big roofs, open water, bare fields), expect biased t; flag rather than correct.
  5. **Thin cloud as haze:** the paper shows thin cloud passing the mask gets "corrected" as aerosol with wrong results in some bands. For greyscale this is less of an issue, but our gate's faint fringe (task B hysteresis) is where it applies.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** physical AOT retrieval not feasible (no calibration, no LUT, no time series for the v2 prior; our pre-storm and post-Ida dates are far further apart than their 10–15 days, with a flood in between). The structural lessons (change screen, ≥ 50% stable share, coarse estimation, abstain on bright/uniform ground) are directly codeable. Their v2 prior term needs a third date: not available.

## 7. Key quotes (manuscript pages)
- "the surface reflectance varies quickly with location but slowly with time (with exceptions that need to be detected before aerosol inversions)" (ms p. 5)
- "If the number of clear and stable pixels in the neighbourhood is too low (less than 50%), aerosol inversion is not attempted" (ms p. 15)
- "it is not possible to use this method at full resolution" (ms p. 20)
