# Coder handoff: Zhang, Guindon & Cihlar (2002), An image transform to characterize and compensate for spatial variations in thin cloud contamination of Landsat images (HOT)

- **Citation:** Zhang, Y., Guindon, B., & Cihlar, J. (2002). *Remote Sensing of Environment* 82(2–3), 173–187. https://doi.org/10.1016/S0034-4257(02)00034-2
- **PDF:** `/Users/jusrogers/Masters/papers/zhang2002_haze_optimized_transformation_thin_cloud_landsat_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document; 1.33 MB; 15 pages (Read tool and pdfinfo) = published range 173–187; page-1 title, authors (Zhang, Guindon, Cihlar), journal 82 (2002) 173–187 and PII S0034-4257(02)00034-2 match the citation/DOI; §6 Conclusions (pp. 185–186) and References (pp. 186–187) present. PASS.
- **Read:** pp. 173–187 in full (Read tool, page images), including Tables 1–3 and Figs. 1–12.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
Design criteria (p. 174): (a) a band space where clear-sky responses of different covers are highly correlated → a "clear line" (CL); (b) haze affects the bands differently, so haze moves pixels off the CL; (c) the transform is the direction orthogonal to the CL.

1. **Band pair:** TM1 (blue) and TM3 (red), in **digital numbers** (eq. 1 and MODTRAN radiances converted to DN with Landsat-5 gains/offsets, p. 175). Simulated clear-sky correlation of the 12 cover types r = .993 (p. 175). For MSS, "the green and red bands can be employed" (p. 186).
2. **Clear line (§5.1, p. 179):** "The scene is visually inspected to locate its clearest regions. Example subimages in this region and TM1 and TM3 DNs of their constituent pixels are regressed to define the CL". Slope S_CL = tan Θ (TM3 against TM1). Observed S_CL 1.32–1.73, r_CL .87–.94 over seven scenes (Table 2, p. 178).
3. **HOT** (eq. 1, p. 175): `HOT = B1·sinΘ − B3·cosΘ`, the perpendicular displacement from the CL. Relative only: Θ "will vary somewhat scene-to-scene", and HOT is used for "a relative, not absolute intra-scene balancing" (p. 175). In the example the clear area sits at HOT ≈ 30, haze at 30–40 (p. 182) — the absolute value is not centred.
4. **Histograms by HOT level (§5.3, p. 182):** for each visible band, DN histograms of pixels grouped in HOT increments of 1, from the clearest to the haziest level.
5. **Adjustment (§5.4, p. 182), a per-HOT-level dark-object subtraction:** for band b, `Δ_b(h) = lowerbound_b(h) − lowerbound_b(h_clear)`; subtract Δ_b(HOT(pixel)) from the pixel. Worked example: TM1 lower bound ≈ 20 DN at HOT = 30; a pixel at HOT = 40 lies in a histogram with lower bound 27, so subtract 7 DN. Lower bound vs HOT is monotonic for TM1–3 (Fig. 9).
   - Assumption: "similar dark targets are present under all haze conditions" (p. 182).

## 2. Inputs, outputs, data needs
- Input: a single date's blue and red DNs (any two visible bands with the stated properties), plus an analyst-chosen clear region.
- Output: HOT image (haze map) and haze-adjusted visible bands.
- No ancillary atmospheric data; MODTRAN used only for design/sensitivity.

## 3. Quantitative results
- Seven TM/ETM+ Canadian scenes (Table 2–3): jet contrails, cirrus, thin stratus/fog, cumulus, mist (p. 178–179).
- Clear vs hazy difference in one "clear-looking" scene ≈ 5 DN in TM1 (P21/R26-b, p. 179).
- Adjustment test (P55/R18, windows 1–3 vs clear window C, similar covers): mean HOT differences 7.7, 6.0, 5.4; mean TM3 DN differences 7.8, 6.1, 4.1; haze contribution 15.0%, 12.3%, 10.8% (band 3) and 16.9%, 13.5%, 11.8% (band 1) (p. 185, Fig. 12). Evaluation is visual plus window-mean histograms; no independent reference image.
- Simulation (pp. 177–178): for conifer forest, haze trajectories of cirrus, stratus and four aerosol types nearly coincide in TM1/TM3, so "knowledge of haze type is not needed to undertake a first order HOT-based radiometric compensation", but HOT "cannot be used to infer optical depth without additional information".

## 4. Stated limitations
- Not completely surface-insensitive: haze-trajectory slopes "monotonically decrease for surface classes of increasing absolute reflectance" → second-order surface-dependent adjustment may be needed (p. 176, p. 186).
- Spurious HOT (p. 179): (a) snow and shadows over snow, deep in the high-haze region; (b) some water bodies, from "sediment in shallow water or by wind-induced waves"; (c) bare soil gives a *low* HOT ("fallow fields are dark in the HOT image"). Fix suggested: snow mask (TM5) and water mask (threshold TM4 near-IR).
- Fourth Tasselled Cap confuses bright urban/road/bare soil with haze; HOT "is much less sensitive to these targets" (p. 179) — a comparison, not a claim of immunity.
- Compensation pulls pixels back to the CL, "eliminating residual thematic discrimination differences between these bands" (p. 186).
- CL from visual inspection of the clearest region; not automated in this paper.

## 5. How to apply to our pipeline
- **Evidence 20 arm (c) HOT** already matches eq. 1 (`HOT = B sinθ − R cosθ`, CL fitted on least-hazy pixels). Differences from the paper: (i) we fit the CL automatically per tile (paper: one CL per scene from a visually chosen clear region); (ii) we centre HOT on the fit pixels (paper leaves it uncentred; equivalent for relative use). Both are our adaptations, not the paper's.
- **The paper is DN-based, not reflectance-based.** Fmask's TOA-reflectance HOT test (`B1 − 0.5·B3 − 0.08`) is a later adaptation; the original HOT is defined on 8-bit TM DNs, which is closer to our 8-bit display RGB than Fmask's version. The non-linear display stretch question remains (HOT assumes linear DN–radiance).
- **The removal step (not yet in our code):** a candidate dehaze arm, per tile or per scene:
  1. compute HOT per pixel (RGB: B = blue, R = red) and round to integer bins (or quantile bins on our scale);
  2. per bin and per band, lower bound = a low percentile (e.g. 1st, robust to noise; paper uses the histogram lower bound);
  3. Δ_b(bin) = lowerbound_b(bin) − lowerbound_b(clear bin); smooth Δ monotonically across bins (Fig. 9 is monotonic);
  4. subtract Δ_b from each pixel. Exclude water (flood!) and shadow from the bins first — the paper flags water as a false-HOT source and needs a near-IR water mask, which we do not have.
- **Flood risk:** turbid floodwater raises HOT (our evidence 20 already saw this on `2_14_51`); the paper explains it (sediment, waves; p. 179). Without NIR, use the before-date water/flood prior or the dark-rise sign to exclude water from the CL fit and the bins.
- **Two-date variant (ours):** fit the CL on the clear before image (no haze), apply to the after image; the paper is single-date.

## 6. Key quotes
- "HOT = B1 sinΘ − B3 cosΘ where B1 and B3 are the pixel's bands 1 and 3 digital numbers (DNs), respectively." (p. 175)
- "the proposed method can only be applied in a relative rather than absolute sense" (p. 175)
- "the proposed HOT is not completely insensitive to surface reflectance and may require, as a second-order term, a surface-dependent adjustment" (p. 176)
- "knowledge of haze type is not needed to undertake a first order HOT-based radiometric compensation. On the other hand, the HOT value cannot be used to infer optical depth without additional information." (p. 178)
- "The scene is visually inspected to locate its clearest regions. Example subimages in this region and TM1 and TM3 DNs of their constituent pixels are regressed to define the CL" (p. 179)
- "this form of histogram analysis assumes that similar dark targets are present under all haze conditions" (p. 182)
