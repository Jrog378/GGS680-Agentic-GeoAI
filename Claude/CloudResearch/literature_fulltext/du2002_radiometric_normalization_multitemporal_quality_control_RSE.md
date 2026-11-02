# Coder handoff: Du, Teillet & Cihlar (2002), Radiometric normalization of multitemporal high-resolution satellite images with quality control for land cover change detection

- **Citation:** Du, Y., Teillet, P. M., & Cihlar, J. (2002). *Remote Sensing of Environment* 82(1), 123–134. https://doi.org/10.1016/S0034-4257(02)00029-9
- **PDF:** `/Users/jusrogers/Masters/papers/du2002_radiometric_normalization_multitemporal_quality_control_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 1.01 MB; 12 pages (Read tool and pdfinfo) = published range 123–134; page-1 title, authors (Du, Teillet, Cihlar), journal 82 (2002) 123–134 and PII S0034-4257(02)00029-9 match the citation/DOI; §6 Conclusions (p. 133) and References (pp. 133–134) present. PASS. (`file` metadata says 10 pages; ignored.)
- **Read:** pp. 123–134 in full (Read tool, page images), including Table 1 and Figs. 1–5.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Premise (p. 124): "linear effects are much greater than nonlinear effects". "PIF assumptions" (p. 124): (1) PIF reflectance invariant over the period; (2) variations in DN are linear and spatially homogeneous for all PIFs; (3) the effects are independent and add linearly; (4) "The consistently changed targets are not the majority of targets in each scene."

1. **Model** (eqs. 1, 7, p. 125): `Q_j(i) = L_j(i)·a_j + b_j` (DN = radiance × gain + offset, image j = 1…m). The standardised PIF value `A_j(i) = (Q_j(i) − Q̄_j)² / σ²_Qj` (eq. 8) is independent of a and b.
2. **Normalisation** (eqs. 10–17, pp. 125–127): `N_j(i) = Q_j(i)·α_j + β_j` with
   `gain_j = σ_Qref / σ_Qj`, `offset_j = Q̄_ref − (σ_Qref / σ_Qj)·Q̄_j` (eq. 17), where Q̄ and σ are the **mean and SD of the selected PIFs**. This is mean/SD matching on PIFs, not a regression fit.
3. **Reference level chosen to keep radiometric resolution** (p. 127): set `σ_Qref = max_j(σ_Qj)` and `Q̄_ref = max_j((σ_Qref/σ_Qj)·Q̄_j)` so that every gain ≥ 1 and offset ≥ 0 (no lost DN levels in integer storage). In the application: "The maximum mean and standard deviation in each band was selected as the reference" (p. 128).
4. **PIF selection** (p. 126, flowchart Fig. 2 p. 128), per band, per image pair:
   a. Thresholds reject cloudy pixels; water pixels are also removed "because they can change quickly and independently of land cover change (Guindon, 1997)". Thresholds used (Table 1a, p. 130), e.g. band 3: 15 < Q < 55/60; band 4: 25–30 < Q < 110–130; band 5: 20–22 < Q < 100.
   b. Difference limit: a pixel whose DN difference between the two dates exceeds "some value" is not a candidate (value not given).
   c. PCA on the remaining pixels (both dates of the same band, i.e. "multitemporal mode", p. 126) → primary major axis.
   d. Keep pixels within ±l of the major axis (minor-axis coordinate in (−l, l)); re-run PCA → improved major axis. l = 1.25 (band 3), 2.0 (bands 4, 5) (Table 1d).
   e. Accept the PIF set only if the linear correlation r between dates ≥ 0.9 (p. 127); otherwise tighten thresholds, difference limit and l and repeat. Achieved r = 0.945–0.990 (Table 1c).
5. **Quality control** (pp. 127–128):
   - Stage 1: r ≥ .9 as above.
   - Stage 2: apply gains/offsets, re-run PCA on the normalised PIFs; the slope of the major axis (SL) should be ≈ 1; iterate parameters "until a slope very close to unity is obtained". Accuracy reported as `mean |1 − SL|`.
   - Multi-image consistency: with 3 images, image A gets two gain/offset sets (via B and via C); their difference is an extra QC check (Table 1f: gain differences 0.0008–0.019, offset 0.19–0.63 DN).

## 2. Inputs, outputs, data needs
- Input: m ≥ 2 co-registered images, same bands. Paper: three Landsat-5 TM scenes, WRS-2 path 37 row 22, 11 Aug 1986, 30 Aug 1987, 9 Aug 1991; bands 3, 4, 5 (1 and 2 "similar, not shown"); common area 1355 × 1404 px; nearest-neighbour registration to image 1, misregistration ≈ 0.7 px (p. 128).
- No ground reference, no atmospheric data.
- Output: per-image per-band gain/offset to a common reference scale; SL quality figures.

## 3. Quantitative results
- SL before normalisation 0.853–1.150 (Table 1b); after 0.971–1.017 (Table 1g).
- Mean |1 − SL|: band 3 4.0% → 0.9%, band 4 11.2% → 0.9%, band 5 7.4% → 1.6% (pp. 130–132).
- NDVI differences then show a fire-like patch (1986→87) and its recovery (1987→91) (pp. 132–133). No accuracy assessment of change detection itself; "More detailed discussion of land cover change detection … beyond the scope" (p. 133).

## 4. Stated limitations
- "residual error is hard to avoid even after radiometric normalization because of nonlinear effects, including phenological change, misregistration, and atmospheric effects" (p. 132).
- "it is still an approximate method because the PIFs are selected by statistical analysis and linearity assumptions are involved" (p. 133).
- Linear effects assumed spatially homogeneous across the whole image (p. 126): one global gain/offset per band.
- The thresholds, difference limit and l are tuned iteratively by the analyst against the r and SL criteria; "objective" here means repeatable criteria, not parameter-free.

## 5. How to apply to our pipeline
- **Our tone fit (`sn8_refhaze.tone_curve`, quantile matching on all `clear` pixels):** Du et al. fit on PIFs only and drop water by threshold before fitting, because water changes independently. In a flood scene that is exactly the flooded ground. Arm "Du-PIF tone":
  1. Candidates = clear & not water-like on either date (a dark-value threshold on grey, as Table 1a's lower bounds do) & |before − after| < D (start D = 2·MAD of the difference).
  2. PCA of [before, after] over candidates (2×2 covariance eigen-decomposition); keep pixels with |minor-axis coordinate| < l (start l = 1.25–2.0 in DN units as the paper, or scale to our noise); repeat PCA once.
  3. Require r ≥ 0.9; if not, tighten D and l (bounded loop, e.g. 5 passes), else fall back to the tile fit.
  4. gain = σ_before/σ_after, offset = μ_before − gain·μ_after on the PIFs (eq. 17), map after → before scale. For 8-bit display data the "keep resolution" rule (gain ≥ 1) does not matter if we work in float.
  5. QC: SL of the PCA major axis on normalised PIFs; report |1 − SL| and r per tile. Paper's achieved |1 − SL| ≤ 1.6% is a sanity target.
- **Global vs local:** the paper assumes spatially homogeneous linear effects. Thin cloud/haze is not spatially homogeneous, so this normalisation removes the date-wide offset only; the local haze stays for the haze model.
- **Linear vs our nonlinear quantile curve:** the paper gives no support for a nonlinear tone curve; a linear mean/SD map on PIFs is the published form.
- **Feasibility (RGB uint8 0.5 m, one pre-storm date, no NIR):** feasible; uses only the two dates per band. Misregistration in the paper was 0.7 px; ours ≈ 1 px, which widens the PCA minor axis, so l may need to be larger.

## 6. Key quotes
- "The consistently changed targets are not the majority of targets in each scene." (p. 124, PIF assumption 4)
- "water pixels will be removed on the basis of thresholds because they can change quickly and independently of land cover change" (p. 126)
- "If a linear correlation coefficient is less than .9, the data set is not selected as PIFs" (p. 127)
- "the quality control parameters (difference limit, thresholds, and range l) can be improved iteratively based on the SL until a slope very close to unity is obtained" (p. 128)
- "it is still an approximate method because the PIFs are selected by statistical analysis and linearity assumptions are involved" (p. 133)
