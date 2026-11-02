# Coder handoff: Chen, Chen, Chen, Jia, Cao & Liu (2016), An Iterative Haze Optimized Transformation (IHOT) for Automatic Cloud/Haze Detection of Landsat Imagery

- **Citation:** Chen, S., Chen, X., Chen, J., Jia, P., Cao, X., & Liu, C. (2016). An iterative haze optimized transformation for automatic cloud/haze detection of Landsat imagery. *IEEE Transactions on Geoscience and Remote Sensing* 54(5), 2682–2694. https://doi.org/10.1109/TGRS.2015.2504369 (published online 18 Dec 2015)
- **PDF:** `/Users/jusrogers/Masters/papers/chen2016_ihot-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded via GMU (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** `file` = PDF document 1.4; 7.8 MB; 13 pages (Read tool and pdfinfo) = journal pp. 2682–2694; title, six authors, TGRS vol. 54 no. 5, May 2016 and DOI 10.1109/TGRS.2015.2504369 (printed p. 2682) match todo.tsv. §IV Discussion and Conclusion, Appendix and References [1]–[32] present (pp. 2692–2693). PASS.
- **Read:** PDF pp. 1–13 = journal pp. 2682–2694 in full (Read tool, page images), including Tables I–III, Figs. 1–12, the Appendix and the biographies.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's.

## 1. Algorithm, step by step
All quantities are TOA reflectance of Landsat TM/ETM+ (6 bands at 30 m) or OLI (7 bands, cirrus band 9 excluded) (p. 2683).
The hazy image and the clear image are of the same scene, at different times.

1. **HOT** (eq. 1, p. 2683): `HOT = sin θ · R1 − cos θ · R3` (R1 = blue, R3 = red for TM/ETM+; OLI bands 2 and 4). θ is the
   angle of the "clear line", a linear regression in blue–red space fitted on haze-free areas, "(or clear-sky image if
   available)" (p. 2683). In the experiment: "the initial haziness index, i.e., HOT … was applied to the hazy image …
   after the clear line was defined from the clear image" (p. 2684).
2. **THOT** (eqs. 2–3, p. 2683): ΔR_i = R_hi − R_ci (hazy minus clear, band i, i = 1..n). Fit by multivariate least
   squares `HOT = Σ k_i ΔR_i + c + ε` (eq. 3); THOT = the fitted value `Σ k_i ΔR_i + c` (eq. 2). Land-cover change and
   phenology in ΔR are taken as independent of HOT, so the regression removes them (p. 2683).
3. **iHOT** (eqs. 4–5, p. 2684): fit `THOT = Σ k′_i R_i + c′ + ε′` on **the hazy and the clear image data together**. For
   clear-image pixels THOT = c, because ΔR = 0. iHOT = the fitted value `Σ k′_i R_i + c′` (eq. 4). "iHOT should be well
   correlated with THOT for the hazy image and should be constant for the clear image" (p. 2684).
4. **Iteration** (§II-D and Fig. 2, p. 2684):
   1) iHOT^(0) = HOT.
   2) THOT^(t) from eq. 2, with k from regressing iHOT^(t) on ΔR (eq. 3).
   3) iHOT^(t+1) from eq. 4, with k′ from regressing THOT^(t) on R (eq. 5).
   4) C^(t) = correlation(THOT^(t), iHOT^(t+1)). Repeat 2–3 "until the correlation between THOT and iHOT stops
      increasing (the change is less than 0.001)", i.e. |C^(t) − C^(t−1)| < 0.001 (Fig. 2). IHOT = the final iHOT.
5. **Saturation** (p. 2686–2687): for the TM urban pair, "pixels with digital number equal to 255 in the blue band
   recorded the heaviest haze" (decided beforehand).
6. **No threshold.** IHOT is a continuous haze-thickness index. The paper gives no cloud/haze cut. Where clouds are
   compared with MTCD and Fmask (binary), IHOT is shown as a grey map (Fig. 9). For removal it is fed to dark-object
   subtraction (DOS) (p. 2690).
7. **Why it works** (Appendix, pp. 2692–2693): with ΔR_i = ΔH_i + ΔD_i (haze + land-cover/phenology) and an ideal haze
   index IHI, the regression residual ε is independent of the other terms, so ε_THOT < ε_HOT (A1–A5) and ε_iHOT < ε_THOT
   (A6–A8).

**Parameters:** convergence 0.001 (the only constant); no window, no threshold. Learned coefficients differ by landscape
(Fig. 8, p. 2689). OLI cropland/desert: band 1 ≈ +1.6/+1.8, band 2 ≈ −1.2/−1.6, other bands near 0. TM urban: band 2 ≈
0.72, band 3 ≈ −0.55 (read from the plot). Coefficients are similar across seasons (Fig. 10, p. 2690).

**Blue/red only, or RGB?** The paper uses all 30 m bands, never tests fewer, and states that HOT itself uses only blue
and red (p. 2682). The algebra works for any n ≥ 1 co-registered bands present on both dates. With n = 2 (B, R) or n = 3
(R, G, B), it runs unchanged, but how well is untested. The OLI weights rely mostly on the coastal-vs-blue contrast
(bands 1 and 2), which RGB lacks.

## 2. Inputs, outputs, data needs
- Inputs: hazy image and a clear image of the same scene, co-registered, same bands, TOA reflectance. One clear image
  can serve several hazy dates of different seasons (Table II, p. 2689: one 2014-03-21 clear date for four hazy dates).
- Output: IHOT map (continuous); the coefficients k, k′.
- Cost: "less than 3 min" per Landsat scene, IDL 8.0, i5-4590, 32 GB (p. 2692).

## 3. Quantitative results
- **Iteration** (Fig. 3(f), p. 2685): correlation 0.946 at iteration 1, about 0.961 at 2, levelling at about 0.966 by
  iteration 11 (read from the plot), on a 400 × 400 OLI subset (Shandong, hazy 2014-04-22, clear 2014-03-21).
- **Test scenes** (Table I, p. 2685): 122/34 OLI cropland 3545 × 3239; 122/44 TM urban 2758 × 2362 (hazy 2004-08-16, clear
  2011-11-02); 140/41 OLI glacier/snow 2830 × 3521; 143/31 OLI desert 2881 × 2106. The evaluations are visual (Figs. 4–7).
- **Cirrus check** (Fig. 11, p. 2691; scene 143/31): correlation with OLI band 9: IHOT r = 0.9753, HOT r = 0.8435, BSHTI
  r = 0.6240.
- **DOS restoration RMSE** against a same-season clear image (Table III, p. 2692; 122/34, hazy 2014-04-22, reference
  2014-05-06), HOT / BSHTI / IHOT:

| Band | HOT | BSHTI | IHOT |
|---|---|---|---|
| 1 Coastal | 0.0078 | 0.0111 | 0.0063 |
| 2 Blue | 0.012 | 0.0177 | 0.0081 |
| 3 Green | 0.021 | 0.0275 | 0.0196 |
| 4 Red | 0.019 | 0.0242 | 0.0176 |
| 5 NIR | 0.0337 | 0.0294 | 0.0284 |
| 6 SWIR 1 | 0.0165 | 0.0152 | 0.0154 |
| 7 SWIR 2 | 0.0137 | 0.0136 | 0.0136 |

  IHOT is lowest "in most spectral bands, except band 6" (p. 2691).
- **Seasons** (Fig. 9, p. 2690): MTCD missed most thin cloud; Fmask marked turbid water as cloud (Dec 15 image); IHOT
  "performs better than MTCD and Fmask" (judged visually).
- No ground-truth cloud masks, no F1, no significance tests.

## 4. Stated limitations (p. 2692)
1. Hill shade is not eliminated: hill-shade areas differ between dates because of solar altitude (Fig. 6(a)).
2. Striping noise appears when the short-blue and blue coefficients are large with opposite signs; IHOT can "enlarge
   Landsat 8 OLI sensor hardware defects".
3. "IHOT may not work that well if there is great land cover changes between clear-sky and hazy images. However,
   usually, the change areas account for a small proportion of the whole image, which can be tolerated in IHOT."
4. IHOT estimates haze thickness only, without removal. DOS works for thin cloud; thick cloud needs more.

## 5. How to apply to our pipeline
- **D1b is IHOT's step 0, not IHOT.** D1b fits the clear line on the clear date (SN8: the before date; HRC_WHU: the
  fold's clear pixels) and uses HOT. IHOT adds the two alternating regressions, which need **both dates**. HRC_WHU has
  no clear partner image, so IHOT can be tested only on SN8/Ida pairs.
- **Units:** the paper uses TOA reflectance. We have 8-bit display DN with date-specific tone curves. The regressions
  are linear and fitted per pair, so gains and offsets are absorbed, but a nonlinear tone difference is not. Work in
  float DN and keep C0's tone mapping out of it (fit on raw DN).
- **Flood risk:** floodwater is real change in ΔR, and it is large on SN8 flood tiles. The paper tolerates change only
  as a "small proportion" of the image. Fit the regressions on pixels unlikely to be flood, then apply them to all.
- **Haze is the fitted value, not the residual.** Our notes' "residual haze map, in the IHOT spirit" (ev21) inverts
  this: in IHOT the residual is discarded as error.
- **Saturation:** 8-bit after-date blue at 255 under thick cloud. Follow the paper and set those pixels to the maximum
  iHOT.

### Proposed bench arm: D1e IHOT-RGB (two-date iterated HOT as a spotter feature and as a gate field)
1. **Data:** SN8 Louisiana-East development tiles (train + val) and the 132 Ida prep tiles, read-only. Per tile: before
   RGB (clear), after RGB (possibly cloudy), valid mask; float DN 0–255. Subsample every 16th valid pixel for fitting.
   Apply to all pixels.
2. **Step 0 (= D1b):** clear line R = k·B + b fitted on the before tile (as `d1_colour.clear_line`); θ = atan(k);
   HOT^(0) = B sin θ − R cos θ on the after tile.
3. **Fit mask F:** valid & not likely flood. Starting rule: exclude pixels whose grey **falls** by more than a fall cut learned
   on training tiles (the H3c fall flag idea, ev07; start at 2 SD of the tile's grey change), or whose before-date dark channel is below the water-like 5th percentile. Variant D1e-all fits on
   all valid pixels, to measure the flood leakage.
4. **THOT step:** OLS on F, `iHOT^(t) ~ k_R ΔR + k_G ΔG + k_B ΔB + c` (ΔX = after − before). THOT^(t) = fitted value on all
   pixels.
5. **iHOT step:** stack after pixels (target THOT^(t)) and before pixels (target c) on F, then OLS
   `target ~ k′_R R + k′_G G + k′_B B + c′`. iHOT^(t+1) = fitted value on the after tile.
6. **Stop** when |corr(THOT^(t), iHOT^(t+1)) − previous| < 0.001 (the paper's rule), with a cap of 30 iterations (log the
   count). Set after-blue = 255 pixels to the tile's max iHOT.
7. **Variants:** D1e-BR (blue and red only, n = 2) and D1e-RGB (n = 3).
8. **Use A, spotter feature:** add the iHOT map in place of, then next to, D1b's HOT in the spotter's feature stack.
   **Use B, gate field:** threshold iHOT with the EM/Bayes cut of `bruzzone2000_handoff.md` (arm B1 steps 2–4), since the
   paper gives no cut.
9. **Compare against:** D1b HOT, D0 (current spotter) and the production dark-rise gate. Measure Ida precision/recall vs
   satellite–NOAA disagreement (132 tiles, tile-block bootstrap paired with D1b), share flagged on the 94 clear tiles,
   and the road-gate flood gain (21 seeds) when SN8 tokens exist. Show the images: HOT vs iHOT maps on
   0_13_5, 2_21_42 and 2_23_44, plus the fitted k′ per tile.
10. **Diagnostics to log:** iterations to converge; final correlation; share of F excluded; corr(iHOT, dark rise) on clear
    tiles (it should be low, since IHOT should be flat on clear ground).

## 6. Key quotes
- "Most previous haze/cloud detection methods for Landsat imagery, e.g., haze optimized transformation (HOT), cannot adequately suppress land surface information and, in particular, often overestimate haze thickness over bright surfaces." (abstract, p. 2682)
- "With an iterative procedure of regressions among HOT, the reflectance difference at the top of atmosphere (TOA) between hazy and clear images, and TOA reflectances of hazy and clear images, the land surface information can be removed" (abstract, p. 2682)
- "a 'clear line' in the blue–red spectral space is defined by a linear regression fitting to data from the haze-free areas (or clear-sky image if available)." (p. 2683)
- "iHOT should be well correlated with THOT for the hazy image and should be constant for the clear image." (p. 2684)
- "Repeat steps 2 to 3 until the correlation between THOT and iHOT stops increasing (the change is less than 0.001)." (p. 2684)
- "it was decided beforehand that the pixels with digital number equal to 255 in the blue band recorded the heaviest haze." (pp. 2686–2687)
- "IHOT may not work that well if there is great land cover changes between clear-sky and hazy images. However, usually, the change areas account for a small proportion of the whole image, which can be tolerated in IHOT." (p. 2692)
- "also performed robustly for hazy images that were acquired at different seasons when using the same reference clear image." (abstract, p. 2682)
