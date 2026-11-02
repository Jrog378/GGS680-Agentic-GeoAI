# Coder handoff: Hagolle, Huc, Villa Pascual & Dedieu (2010), A multi-temporal method for cloud detection (MTCD)

- **Citation:** Hagolle, O., Huc, M., Villa Pascual, D., & Dedieu, G. (2010). A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images. *Remote Sensing of Environment* 114(8), 1747–1755. https://doi.org/10.1016/j.rse.2010.03.002
- **PDF:** `/Users/jusrogers/Masters/papers/hagolle2010_multitemporal_cloud_detection_RSE-summary.pdf` (page 1 = AI summary; HAL cover + preprint follow)
- **Source:** author's final preprint on HAL (CNES/CESBIO), https://hal.science/hal-00489793 (file `Landsat_Formosat2_preprint_final.pdf`)
- **Validation:** PDF, 26 pages (Read tool and pdfinfo agree) = HAL cover + 25-page double-spaced, line-numbered manuscript (lines 1–380) with tables and figures at the end. Published range is 9 journal pages; the difference is manuscript layout, not missing content. Title/authors/DOI match Crossref; abstract, conclusions (§5) and references present. PASS (preprint, not the journal typeset version).
- **Read:** whole preprint (lines 1–380, Tables 1–2, all figure captions). Figures seen only through captions. Citations below are **manuscript line numbers** (l.), since the preprint has no journal page numbers.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm, step by step (§3, l. 138–220)
1. **Inputs per date D:** TOA reflectance corrected for Rayleigh scattering, blue and red bands (plus green and 1.6 µm SWIR on Landsat for snow). Images orthorectified and co-registered; constant viewing angle (same orbit track).
2. **Work at reduced resolution:** 100 m for FORMOSAT-2 (8 m native), 240 m for Landsat — "mainly for computing performance reasons, but also to avoid possible image registration errors" (l. 152–154).
3. **Reference = composite**, not one image: "for each pixel the most recent cloud free reflectance obtained in the time series before date D" (l. 151–152). Dr = date of that value per pixel.
4. **Main test, blue rise** (eq. 1, l. 156):
   `ρ_blue(D) − ρ_blue(Dr) > 0.03 · (1 + (D − Dr)/30)`, D − Dr in days. Threshold 0.03 reflectance for consecutive dates, 0.06 at 30 days (to allow real surface change, l. 159–161).
5. **Water excluded first** (l. 163–165): water reflectance jumps with sunglint, turbidity, foam. (How water is masked is not described in this paper.)
6. **Veto (i), red rise much larger than blue rise** (eq. 2, l. 173–178): pixel is NOT cloudy if
   `ρ_red(D) − ρ_red(Dr) > 1.5 · (ρ_blue(D) − ρ_blue(Dr))`. Catches ploughing, harvest, quick drying of vegetation (Fig. 3).
7. **Veto (ii), neighbourhood correlation** (l. 179–195): pixel is NOT cloudy if "the reflectances in the pixel neighborhood are well correlated with those of the same neighborhood in one of the ten images acquired before date D" (after Lyapustin et al. 2008). Rationale: "it is very unlikely that a cloud stays at the same place with a constant shape, a good correlation coefficient can only be due to a good transparency of the atmosphere" (l. 181–182). Using the ten previous raw images (not the composite) lets a persistent false alarm (plastic greenhouses) be cleared after one date.
   - **Not given in the preprint:** the neighbourhood size, which bands enter the correlation, and the correlation threshold. Do not cite numbers for these from this paper. (They may be in the MACCS/MAJA ATBD; not checked.)
   - Side effects stated: high-AOT images pass as clear, but "it sometimes reclassifies as unclouded the images with very thin clouds" (l. 191–192). Empirically AOT < 0.7 at 550 nm → clear, AOT > 1 → mostly cloudy (few cases, l. 192–195).
8. **Recursion and initialisation** (l. 196–205): images processed in date order; cloudy pixels do not update the composite. First image: a high, conservative blue threshold (value not given), then "backward processing" of the first 6–10 images in reverse order to get a good first mask.
9. **Snow (Landsat only)** (l. 210–217): NDSI = (ρ_green − ρ_SWIR1.6)/(ρ_green + ρ_SWIR1.6); a bright pixel is snow if NDSI > 0.6 (after Irish 2000).
10. **Dilation** (l. 218–220): "the cloud masks are dilated since it is very common to observe thin clouds at the edge of thicker clouds. Dilatation is 2-pixel wide at reduced resolution, ie 200m for FORMOSAT-2 and 480m for LANDSAT."
11. Cloud shadows: geometric projection of detected clouds; "out of the scope of the paper" (l. 88–91).

## 2. How changed pixels are handled (our key question)
- The threshold grows with the time gap (eq. 1) to tolerate slow surface change.
- Fast surface change is handled only by the two vetoes: spectral shape (red ≫ blue → land change) and spatial structure (neighbourhood still correlated with a past image → land change, not cloud).
- A change that brightens blue more than red and also breaks local correlation **will be flagged as cloud**. The paper does not discuss floods.
- Persistent changes are released by veto (ii) after one date (greenhouse example, l. 184–190); with only two dates we cannot do that.

## 3. Inputs, outputs, data needs
- Needs: blue (and red) calibrated reflectance, a time series (composite of last clear values; up to ten previous images for veto ii), constant viewing angle, co-registration. SWIR only for snow; no thermal.
- Output: binary cloud mask (dilated), snow mask (Landsat), per-image cloud percentage.

## 4. Quantitative results to compare against
- No pixel-level accuracy. Validation is visual over >300 FORMOSAT-2 and >100 Landsat images (l. 230–232) and cloud-percentage scatter against NSPO operators (Fig. 4) and Landsat ACCA (Fig. 6).
- Case values (Fig. 5, 7–10 captions): e.g. MTCD 80% vs NSPO 20% (thin cloud missed by operator); MTCD 37% vs NSPO 85% where "the thin cloud cover is underestimated by our cloud mask because the previous image in the time series is quite old"; Landsat 5 Columbia ACCA 10% vs MTCD 49%; Boulder ACCA 4% vs MTCD 73%.
- One parameter set for both sensors (l. 272–273).

## 5. Stated limitations
- Inland water; thin cloud vs aerosol confusion; abrupt surface change (crops, fire, snow, drying) (l. 162–169).
- An old reference reduces sensitivity (Fig. 5 middle right).
- Strict by design: "This algorithm has been tuned to flag even very thin clouds" (l. 285); some thin semi-transparent cloud still missed (Fig. 8).
- Must run in date order (no parallelism) (l. 288–290).

## 6. How to apply to our pipeline
- **`sn8_refhaze.cloud_gate` / `sn8_cloudsym` rise gate (dark-channel rise, Otsu 71, blobs ≥ 2,500 m²):** MTCD is the closest published precedent: a rise against a clear reference. Differences to state honestly: MTCD thresholds blue reflectance (physical units, Rayleigh-corrected), we threshold the 8-bit dark-channel rise; MTCD's reference is a per-pixel composite of the last clear values, ours is one before image; MTCD works at 100–240 m to absorb misregistration, we work at 0.5 m with a 20 m dark-channel window (which plays the same role).
- **Add veto (ii) as an arm** (most useful idea here): inside each dark-rise blob, compute the local Pearson correlation between before and after (greyscale, e.g. 16–32 m windows; window and threshold are ours to learn since the paper gives none). High correlation → atmosphere transparent → not cloud (the "changed roof / debris" case). Caveat: at 0.5 m our clear-ground before/after correlation is already low (r = 0.46 and 0.09 on two tiles, sn8_refhaze docstring), so the threshold must be learned on our tiles, and floods (low correlation) will not be vetoed — that is the correct direction for us (flood under cloud stays "cannot assess" rather than "clear").
- **Veto (i) analogue on RGB:** cloud adds a roughly grey veil (blue rise ≳ red rise); surface change often raises red more than blue (bare soil, debris, muddy water). An arm: in a dark-rise blob, reject as cloud if Δred > 1.5·Δblue on the RGB tiles. Our tiles are 8-bit display products, not reflectance, so the 1.5 factor will not transfer as-is; learn it.
- **Time-gap threshold:** our dates are fixed (pre-storm vs Ida), so the (D − Dr)/30 term is a constant; with a long gap MTCD would double its threshold. Our Otsu-learned cut already absorbs this.
- **Dilation:** MTCD dilates by 2 coarse pixels (200–480 m). Our 20 m linear fade past the gate is the analogous step, at our scale; MTCD's dilation is a hard mask, not a fade.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** main test feasible in form (rise vs reference) but not in units (no calibrated blue reflectance; uint8 tone curves differ by date — we already quantile-match). Veto (i) feasible on RGB with a learned factor. Veto (ii) feasible with one reference date. Composite, backward initialisation, ten-image release and NDSI snow test: not applicable (one reference, no SWIR).

## 7. Key quotes (manuscript line numbers)
- "Our clear image is a composite image that contains for each pixel the most recent cloud free reflectance obtained in the time series before date D." (l. 151–152)
- "When dates are very close, the threshold tends to 0.03, but this value doubles when Dr and D are separated by 30 days" (l. 159–160)
- "a good correlation coefficient can only be due to a good transparency of the atmosphere." (l. 182)
- "it is very common to observe thin clouds at the edge of thicker clouds." (l. 218–219)
