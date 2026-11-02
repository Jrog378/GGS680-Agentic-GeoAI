# Coder handoff: Makarau, Richter, Müller & Reinartz (2014), Haze Detection and Removal in Remotely Sensed Multispectral Imagery

- **Citation:** Makarau, A., Richter, R., Müller, R., & Reinartz, P. (2014). *IEEE TGRS* 52(9), 5895–5905. https://doi.org/10.1109/TGRS.2013.2293662
- **PDF:** `/Users/jusrogers/Masters/papers/makarau2014_haze_detection_removal_multispectral_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** DLR institutional repository (elib), https://elib.dlr.de/85644/1/06697865.pdf — IEEE early-access version ("Content is final as presented, with the exception of pagination"), pages numbered 1–11.
- **Validation:** PDF, 11 pages (Read tool and pdfinfo; `file` wrongly said 0 pages) = published range 5895–5905 (11 pages); title/authors/DOI match Crossref (DOI printed on p. 1); Conclusion (§IV) and references present. PASS.
- **Read:** pp. 1–11 in full, including the pseudocode, figure captions, references and biographies. Page numbers below are the early-access 1–11 (journal page = 5894 + n).
- **Prepared by:** Claude (AI), 2026-10-29. DLR (agency).

## 1. Algorithm, step by step
1. **Haze model, additive** (eqs. 1–2, p. 2): `L_sensor = L0 + HR`; per band in DN: `DN_sensor_i(x,y) = DN_i(x,y) + HR_i(x,y)`, with HR_i = HTM_i, the haze thickness map. Justified by a small field of view (constant sensor–object distance). **No transmission (dimming) term**, unlike He et al.
2. **HTM by local dark-object search** (eq. 3, p. 2–4): `HTM(x,y) = DARK_PIX_SEARCH(Band_b, w)` = minimum in each **non-overlapping** w × w window; result stored at 1/w size, **median filtered (usually 3 × 3)** and **cubic-interpolated** back to full size, "therefore, the possible haze overestimation is suppressed" (p. 3).
   - Window: "w usually takes values ranging from 3 to 9. With w = 3, reasonable results" on Landsat 7/8, AVNIR, AVIRIS, WorldView-2, RapidEye (p. 4). Rule: "the minimum window size should be three times higher than the sensor GSD", e.g. WorldView-2 (2 m) → 6 m (p. 3).
   - Trade-off (Fig. 2, p. 3): larger window finds dark pixels more easily but smooths haze borders and structure → underestimates HTM; smaller window keeps structure but may select non-dark pixels outside haze.
   - The HTM includes clear-scene aerosol; compensated in step 6.
3. **Synthetic short band** (eq. 4, §II-C, p. 4–5): using blue directly over-dehazes blue (Fig. 4). Extrapolate to a shorter wavelength from the first two bands. Landsat 8 (pseudocode, p. 7): `Band_extrapol = (B_0.443 + (B_0.443 − 0.95·B_0.4825)) > 0` (λ ≈ 0.423 µm). Median filter if noisy.
4. **Large bright objects** (p. 3, Fig. 3): mean-shift segmentation of the **red** band, threshold at the mean → `bright_obj`; HTM values there are replaced by **triangulation interpolation**. Fully uniform bright scenes (snow) → HTM impossible.
5. **Haze mask** (p. 4): a second HTM with a large window (**w = 21**, "GSD ∗ 20", coefficient found experimentally), thresholded at its **mean**; water under haze removed with NIR. Used only to choose pixels for the band regressions and the clear-area offset; "does not necessarily have to be precise".
6. **Per-band haze** (eqs. 5–8, p. 5–6): HTM_i from each band; slope k_i of HTM_i vs HTM over haze-mask pixels; enforce decreasing k with wavelength (k_{i+1} < k_i, steps ≤ 0.1, empirical); linearly scale K to [1, 0] from the shortest band to 2.2 µm; `HTM_i = HTM · k_i`.
   - **Inconsistency in the paper:** eq. 5 text says w = 21 for HTM_i; the pseudocode computes k_i with w = 3 (p. 7).
7. **Dehaze and clear-scene compensation** (eqs. 9–10, p. 6): `DN_i = DN_sensor_i − HTM_i`, then add back `|mean(DN_sensor_i[non_haze]) − mean(DN_i[non_haze])|` so haze-free areas keep their original level.
8. **WorldView-2 parallax** (p. 9): bands 1, 4, 6, 8 and 2, 3, 5, 7 see haze shifted (two focal-plane groups); compute HTM1 and HTM2 separately and match HTM1 to HTM2 with a local 10 × 10 linear stretch.

## 2. Inputs, outputs, data needs
- Input: one hazy multispectral image (DN or radiance); ideally two short-wavelength bands for extrapolation, red band for segmentation, NIR for water. No reference date, no SAR.
- Output: HTM, haze mask, dehazed bands.

## 3. Quantitative results to compare against
- No accuracy score. Evaluation by spectral shape and profiles against a haze-free Landsat 8 scene of the same area **7 days apart** (14 vs 7 July 2013, Montelimar; Figs. 8–10, p. 7–8). K for Landsat 8 = [1.0, 0.901, 0.816, 0.886, 0.781, 0.402, 0.1] (note 0.886 for red breaks the decreasing trend as printed); WorldView-2 K = [1.0, 0.908, 0.783, 0.673, 0.580, 0.463, 0.274, 0.1].
- Clear scene test: ATCOR visibility 19.9 km (original) vs 20.6 km (after dehazing) (p. 10).
- Runtime ~1 min per subset (IDL, Core 2 Duo).

## 4. Stated limitations
- "in rare cases of scenes with absolutely flat and highly reflective surfaces (desert and snow), it could be impossible to locate dark objects" (p. 11).
- Triangulation border effects (future work). Negative values can appear after subtraction (Fig. 7 caption).

## 5. How to apply to our pipeline
- **`sn8_clouds.dark_channel` (41 px min filter + 41 px box blur):** Makarau's HTM is the greyscale dark channel computed in **non-overlapping blocks**, then **3 × 3 median** at block scale and **cubic interpolation**. Arm: replace the box blur with block-min → median → bicubic upsample. The median at block scale removes isolated "no dark pixel in this block" overestimates (a roof filling a block), which is exactly the false-haze-on-houses complaint.
- **Window size:** their rule (≥ 3 × GSD; w = 3 px) is for 2–30 m data where a 3-px block already holds a shadow. At 0.5 m, 3 px = 1.5 m holds no shadow; our 20 m (40 px) choice is driven by needing a dark object in every window, which matches their larger-window logic. Their trade-off statement (big window smooths haze borders, underestimates) is the same as He's halo trade-off.
- **Bright-object infill:** segment large bright, uniform regions (roofs, concrete, bright water), and replace the HTM/dark channel there by interpolation from surrounding windows instead of trusting the local minimum. Codeable with our greyscale: threshold a mean-shift/SLIC segmentation at the mean, as they do with red.
- **Haze mask by mean threshold on a coarse HTM:** a cheap alternative to our Otsu cut for a first single-date haze mask; their claim is that precision is not needed because the mask only selects pixels for statistics.
- **Clear-area offset (eq. 10):** after subtracting the haze map, re-add the mean difference over non-haze pixels so clear ground keeps its level. Our `dehaze` uses He's A-based recovery; for an additive arm, use their offset.
- **Additive vs transmission model:** Makarau subtracts haze only; we divide by t. Under thin haze the two are close; under thicker haze the additive model leaves contrast low (no un-dimming). For our two-date variant, test an additive arm: HTM = dark(after) − tone(dark(before)) inside the gate, corrected = after − HTM (+ offset) — simpler and more stable where t is ill-conditioned, at the cost of contrast.
- **Two-date note:** the same-area clear image is used **only for evaluation**, not as an input. The "two-date reference" use is our extension.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** the single-band HTM, median/interpolation, bright-object infill, mean-threshold haze mask and clear-area offset are directly feasible on greyscale. Band extrapolation and per-band k need multispectral bands; with RGB we could compute the HTM on blue (or a blue–green extrapolation) and scale red/green by fitted k, but uint8 display tones make the physical interpretation weak. The WorldView-2 parallax note may matter if the Maxar RGB tiles were pansharpened from band groups with a time offset (unknown; check for colour fringes at cloud edges).

## 6. Key quotes
- "The dark-object subtraction method is further developed to calculate a haze thickness map" (abstract, p. 1)
- "the minimum window size should be three times higher than the sensor GSD" (p. 3)
- "Therefore, the possible haze overestimation is suppressed." (p. 3, after median filtering and interpolation)
