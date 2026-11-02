# Coder handoff: Zhang & Guindon (2003), Quantitative assessment of a haze suppression methodology for satellite imagery: effect on land cover classification performance

- **Citation:** Zhang, Y., & Guindon, B. (2003). Quantitative assessment of a haze suppression methodology for satellite imagery: Effect on land cover classification performance. *IEEE Transactions on Geoscience and Remote Sensing* 41(5), 1082–1089. https://doi.org/10.1109/TGRS.2003.811817
- **PDF:** `/Users/jusrogers/Masters/papers/zhang_guindon2003-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document, version 1.3; 1.16 MB; 8 pages (Read tool and pdfinfo) = published range 1082–1089; page-1 title, authors (Zhang, Guindon), TGRS vol. 41 no. 5, May 2003, and DOI 10.1109/TGRS.2003.811817 match todo.tsv; §VI Conclusion and References [1]–[17] (p. 1089) present. PASS. Note: Table II is cited on p. 1087 ("Table II summarizes these values for all band pair combinations") but is not printed anywhere in this PDF (only Tables I and III; confirmed with pdftotext).
- **Read:** PDF pp. 1–8 = journal pp. 1082–1089 in full (Read tool, page images), including Tables I and III, Figs. 1–13, references and biographies.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
This paper is an assessment; the procedure is summarised in §II (pp. 1082–1083, Fig. 1) and detailed in Zhang, Guindon & Cihlar 2002 (RSE; our handoff `zhang2002_haze_optimized_transformation_thin_cloud_landsat_RSE.md`). Only visible bands are corrected, "because of their enhanced sensitivity to haze vis-a-vis the infrared bands and in part because haze can be approximated as an additive effect on radiance in this portion of the spectrum" (p. 1082).

1. **Characterise clear areas (p. 1083; Fig. 1 box: "Visual inspection • Clear area sampling • Regression to define line • Water body exclusion").** Collect a sample of clear-area pixels; it should "span the full visible-band reflectance range". In blue–red DN space (TM1 vs TM3) clear pixels are highly correlated; fit the clear line (CL) by "simple linear regression". θ = slope angle of the CL.
2. **HOT image (eq. 1, p. 1083):** `HOT = B1 sin θ − B3 cos θ` (B1, B3 = TM band 1 and 3 DN). Not normalised: pixels on the CL have a nonzero HOT. **Differential HOT (ΔHOT)** = pixel HOT − CL HOT response; it is "the relative, intrascene haze level of a pixel". Raw HOT is noisy from quantisation; "spatial smoothing can be applied" since haze varies at low frequency vs 30 m pixels (p. 1083).
3. **Adjustment parameters (p. 1083):** an "assumed linear relationship between radiance adjustment and differential HOT level serves as a good first approximation". The scale factor comes from "dark target" subtraction: for each visible band, grey-level histograms of pixels in HOT intervals from clear to the haziest level for which adjustment is practical (haze thin enough to be translucent; enough pixels per interval to define the lower bound). "The rate of increase of histogram lower bound with HOT, estimated through linear regression, defines the required scale factor. Water body pixels are excluded from the histogram analysis."
   - So the 2003 form is: `ΔDN_b = s_b · ΔHOT`, `s_b` = regression slope of the per-interval histogram lower bound on HOT. (The 2002 paper's worked example subtracts the per-level lower-bound difference directly; our `a2_hot.py` follows the 2002 per-level lookup.) Interval width not stated here (2002: increments of 1).
4. **Adjust (p. 1083):** "the visible-band DNs of each land pixel can then be adjusted" (subtract ΔDN). Water pixels are not mentioned as adjusted.
5. **Operating limits from the assessment:**
   - Lower limit (p. 1085): clear-scene forest patches show a dispersion of "approximately two DNs. This in turn defines a lower limit … If a scene exhibits differential HOT values limited to this range, the scene should be deemed clear and not be subjected to haze compensation."
   - Upper limit: suppression "breaks down" above "differential HOT threshold values ranging from ten to 20 among the hazy scenes" (p. 1085); "effective radiometric restitution can be realized up to differential HOT levels of 15 to 20 for Landsat TM data" (p. 1089); classification agreement stays above 0.6 "until differential levels of about 20" (p. 1089).
- The paper does not say how water is identified (no band or threshold given in this paper). The 2002 paper uses a near-IR (TM4) threshold.
- Needs ≥ 2 visible bands: "The HOT-based approach can be readily applied to data from any imaging sensor with at least two visible bands" (p. 1083); applied also to Landsat MSS in green–red space (pp. 1082–1083).

## 2. Inputs, outputs, data needs
- Inputs: one image with blue and red (or green and red) bands, a clear-area sample, a water mask.
- Test data (Table I, p. 1085): WRS-2 15/29 Ottawa; hazy test scenes A (1999-July-28), B (2000-Aug-31), C (2001-Sep-3), D (2000-Aug-15), all L7 ETM+; benchmark clear E (1997-July-30, L5 TM, 15/29) and F (2001-Aug-25, L7 ETM+, 16/29).
- Invariant targets: 500 dense forest patches (200 conifer, 300 deciduous), 5 × 5 pixels, checked on 1:22 000 aerial photography of 1998 (p. 1084); patches with anomalously high radiance in scene F (< 5%) discarded as land cover change (p. 1085).
- Separability: three classes (conifer, new residential, old residential), 20 patches of 7 × 7 pixels each (p. 1085). Classification: TM3, TM4, TM5 → k-means with 75 clusters, manual labelling to water / forest / urban / agriculture; pixel-by-pixel comparison with the clear scene (p. 1087). For the classification study the haze suppression was "applied … only to TM3" (p. 1084).
- Output: dehazed visible bands; HOT/ΔHOT overlay.

## 3. Quantitative results
- Forest patch TM1–3 SDs: hazy ≈ 2 to 18, dehazed ≈ 2 to 6, consistent with the clear-scene SDs (Fig. 9, p. 1085).
- Dehazed patch means are systematically higher than the clear reference (different sensors E vs A–D; normalisation to each scene's clearest areas) (p. 1085).
- Separability `S = |M_i − M_j| / sqrt(SD_i² + SD_j²)` (eq. 2, p. 1087): improvement after dehazing "statistically significant for all cases at the 99% confidence level" (p. 1087); values in the missing Table II.
- Table III (p. 1088), agreement with the clear scene (left: fraction of clear-scene class pixels with the same label; right: same, based on image D's assignment):

| Class | Clear vs Hazy | | Clear vs De-Hazed | |
|---|---|---|---|---|
| Water | 0.839 | 0.894 | 0.915 | 0.865 |
| Forest | 0.472 | 0.784 | 0.712 | 0.790 |
| Urban | 0.564 | 0.139 | 0.495 | 0.311 |
| Agriculture | 0.774 | 0.710 | 0.765 | 0.741 |

- Fig. 13 (p. 1088): hazy-vs-clear agreement falls monotonically with ΔHOT (≈ 0.77 at ΔHOT −2/0 to ≈ 0.17–0.25 at 16–20); dehazed-vs-clear stays above 0.6 up to about 20 (p. 1089). (Values read from the plot; only "above 0.6" and "about 20" are printed in text.)
- Haze of "differential HOT of 10 to 15 are sufficient to result in forest and croplands being confused with urban targets" (p. 1089).

## 4. Stated limitations
- Haze suppression breaks down above ΔHOT of 10–20 (p. 1085); dense cloud features and a "residual dense contrail" are not recovered (p. 1088).
- Relative method: normalises to each scene's clearest areas, so interscene differences remain (p. 1085).
- Infrared bands not handled; shadowing not handled ("Work is currently underway", p. 1084).
- Urban agreement low (0.3–0.5) partly from fallow fields confused with urban across years (p. 1088).

## 5. How to apply to our pipeline
- **RGB-only feasibility: yes for RGB, no for grey.** HOT needs exactly blue and red, which our Maxar RGB has (p. 1083: any sensor with two visible bands). On grey tiles HOT cannot be computed; there the arm abstains or uses the RGB-derived ΔHOT map before greying.
- **Water is the blocker, as the bench said.** The paper excludes water from the clear-line fit and from the lower-bound regression and corrects only land pixels, but gives no water rule; the 2002 paper's rule needs NIR. For us water = the flood, so the mask decides whether we "dehaze" the flood away.
- **Two-date substitute for the water mask:** we have a clear pre-storm date. Pre-existing water can be found on it, and new water should show as a change the haze does not explain. That makes a usable proxy without NIR.
- **Units:** the ΔHOT limits (2, 15–20) are Landsat TM 8-bit DN. Our tiles are 8-bit display DN with a different stretch, so start from the printed values and also try the data-driven lower limit (the clear-pixel ΔHOT dispersion, which is how the paper derived its 2 DN).
- Ties to the bench: HOT already helps cloud *detection* (D1b, F1 +0.011); this arm tests HOT as a *correction*, against A1 Chavez k = 0 (the only haze arm closer to NOAA).

### Proposed bench arm: A2b Zhang HOT, lower-bound slope, two-date water proxy
1. **Clear sample** (after image): pixels outside production's dark-rise gate, outside the water proxy (step 3), not saturated (all bands < 250) and not near-black (grey > 5). Fit `R = a·B + c` by least squares; θ = atan(a).
2. **HOT** = `B sin θ − R cos θ` (eq. 1). CL HOT = `−c·cos θ` (exact for points on the line); `ΔHOT = HOT + c·cos θ`. Smooth ΔHOT with a 61 × 61 px (≈ 30 m, the paper's pixel size) median filter.
3. **Water proxy W** (replaces the NIR mask): (i) before-date water: before-image pixels with HOT_before (same θ, c) above the 95th percentile of the before tile **and** grey below the before tile's 20th percentile (dark and blue-shifted); (ii) after-date new water / flood candidates: pixels production's change step marks as darkened (its existing flood-candidate cue and threshold); dilate W by 4 px (2 m).
4. **Scale factors:** for each band b ∈ {R, G, B}, bin non-W pixels by integer ΔHOT; for bins in (2, 20] with ≥ 100 pixels take the lower bound = 1st percentile; `s_b` = least-squares slope of lower bound on bin ΔHOT (the 2003 "linear regression" rule). Abstain on the tile if fewer than 5 bins qualify or `s_b` < 0.
5. **Correct:** for non-W pixels with 2 < ΔHOT ≤ 20: `DN_b ← DN_b − s_b·(ΔHOT − 2)`; ΔHOT ≤ 2 unchanged (paper's clear limit); ΔHOT > 20 left as is and flagged "cannot assess" (paper's breakdown limit). W pixels not corrected (paper corrects land pixels only). Clip to [0, 255].
6. **Variants:** A2b-noW (no water proxy: measures how much flood gets "dehazed"); A2b-lookup (2002 per-level Δ lookup = current `a2_hot.py` with W supplied); A2b-auto (lower limit = 2 × MAD of ΔHOT on the clear sample instead of 2).
7. **Compare against** C0 and A1 Chavez k = 0: Ida primary (closeness to NOAA, paired, 54 tiles), guard, grey error thin, flood screen then 21-seed flood rule; plus the share of SN8 flood pixels inside W (proxy recall) and the flood-call change between A2b and A2b-noW.

## 6. Key quotes
- "effective haze reduction can be realized for differential HOT response levels of up to 20 for Landsat Thematic Mapper scenes." (abstract, p. 1082)
- "HOT = B1 sin Θ − B3 cos Θ" … "this transform is not normalized, i.e., it will have a nonzero value for pixels lying along the CL." (eq. 1, p. 1083)
- "an assumed linear relationship between radiance adjustment and differential HOT level serves as a good first approximation." (p. 1083)
- "The rate of increase of histogram lower bound with HOT, estimated through linear regression, defines the required scale factor. Water body pixels are excluded from the histogram analysis described above." (p. 1083)
- "The HOT-based approach can be readily applied to data from any imaging sensor with at least two visible bands." (p. 1083)
- "above differential HOT threshold values ranging from ten to 20 among the hazy scenes, haze suppression breaks down thereby defining the effectiveness limit of our procedure." (p. 1085)
- "If a scene exhibits differential HOT values limited to this range, the scene should be deemed clear and not be subjected to haze compensation." (p. 1085)
- "Haze corresponding to differential HOT levels of 10 to 15 are sufficient to result in forest and croplands being confused with urban targets even when the classification is based on a mix of visible and infrared bands." (p. 1089)
