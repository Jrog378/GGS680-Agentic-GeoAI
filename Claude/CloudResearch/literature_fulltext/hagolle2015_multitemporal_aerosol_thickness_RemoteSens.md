# Coder handoff: Hagolle, Huc, Villa Pascual & Dedieu (2015), Multi-temporal and multi-spectral AOT estimation (MACCS)

- **Citation:** Hagolle, O., Huc, M., Villa Pascual, D., & Dedieu, G. (2015). A multi-temporal and multi-spectral method to estimate aerosol optical thickness over land, for the atmospheric correction of FormoSat-2, LandSat, VENµS and Sentinel-2 images. *Remote Sensing* 7(3), 2668–2691. https://doi.org/10.3390/rs70302668
- **PDF:** `/Users/jusrogers/Masters/papers/hagolle2015_multitemporal_aerosol_thickness_RemoteSens-summary.pdf` (page 1 = AI summary)
- **Source:** MDPI open access (CC BY), fetched from mdpi-res.com (the www.mdpi.com PDF link returned "Access Denied" to scripts).
- **Validation:** PDF, 24 pages (Read tool and pdfinfo) = published range 2668–2691; title/authors/DOI match Crossref; Conclusions (§5) and References present. PASS.
- **Read:** pp. 2668–2691 in full; references skimmed. Figures seen through captions only.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Processing chain (§3.2, p. 2674–2675)
1. Gas absorption correction (SMAC; ozone, water vapour, pressure from ancillary data).
2. Cloud and shadow detection with MTCD (Hagolle 2010), processed in date order; a **composite of the most recent cloud-free pixels** is updated each date and used for both cloud detection and the MT aerosol method. Water and snow excluded from AOT.
3. AOT estimation at coarse resolution: **100 m (FormoSat-2), 240 m (Landsat)**; each estimate uses a **7 × 7 coarse-pixel neighbourhood**, computed every third coarse pixel → AOT map at ~300 m / ~720 m.
4. Gap filling, **15 × 15 Gaussian** smoothing at coarse resolution, bilinear interpolation to full resolution.
5. Correction per pixel with successive-orders-of-scattering LUTs; continental aerosol model only (Table 3). Adjacency and topographic corrections exist but are not described.

## 2. The multi-temporal (MT) method (§3.3.1, p. 2676–2677) — the part closest to us
- **Assumptions:** "the AOT varies faintly with distance; the surface reflectance varies slowly with time." AOT constant within the neighbourhood; surface reflectance equal at D and the reference date Dr.
- **Pixel screening (how changed pixels are handled):**
  - exclude cloud, snow, water;
  - "we discard the pixels for which the NIR (FormoSat-2) or SWIR (LandSat) reflectance has changed too much since the reference date" — chosen because these bands are "less sensitive to AOT variations and more sensitive to surface reflectance variations". **The threshold value is not given.**
  - exclude AOT-insensitive pixels: if the corrected surface reflectance changes by < 0.01 when AOT changes by 0.2, the pixel is invalid (the "critical" reflectance, ~0.25 in blue, where path radiance gain cancels transmission loss).
  - **≥ 40% valid pixels** in the neighbourhood, otherwise no estimate.
- **Cost** (eqs. 1–4, blue band only, since blue "have a lower temporal variation"):
  `cost_MT = Σ_valid (K1² err1² + K2² err2²)`,
  `err1 = atcor(ρTOA(D), τ) − atcor(ρTOA(Dr), τr)` (both dates' corrected reflectances should agree),
  `err2 = atcor(ρTOA(D), τ) − ρsurf(Dr)` (agree with the previously corrected reference; needed because err1 ≈ 0 whenever τ = τr regardless of the absolute AOT).
  `atcor` = LUT atmospheric correction; τ, τr AOT at D and Dr. K2 = 1; K1 ∝ mean |blue TOA(D) − blue TOA(Dr)|. Solved by Levenberg–Marquardt for τ and τr.
- **Stated weaknesses:** less accurate with lower revisit or fast vegetation change; less sensitive over bright surfaces; cannot retrieve aerosol model.

## 3. Multi-spectral (MS) and hybrid (§3.3.2–3.3.3, p. 2678–2682)
- MS (dark dense vegetation variant): blue surface reflectance predicted from red, chosen because blue–red scatter is at least half that of SWIR pairs (Table 4, e.g. Landsat-5 RMSE 0.012 vs 0.025–0.029). FormoSat-2: `ρblue = 0.465 ρred − 0.006` (eq. 7); Landsat-5 `0.568 ρred + 0.002`; Landsat-7 `0.479 ρred + 0.007`. Valid pixels: not cloud/shadow/water/snow, **NDVI > 0.2**; weight K = NDVI.
- Hybrid cost (eq. 10): `Σ K_MT² err_MT² + Σ K_MS² err_MS²`, K_MS = 1, **K_MT = 1200 / ((D − Dr)² + 800)** (eq. 11): weight halves between 20 and 40 days.
- **Dark-object upper bound** (§3.3.4, p. 2682): darkest blue pixel (excluding cloud and topographic shadow, and required to be dark on the previous image too, "to avoid undetected cloud shadows") assumed surface reflectance **0.01** (0.03 for arid sites); the AOT that explains its TOA value is a soft ceiling; AOT ≥ 0 is a hard floor.
- **Gap filling** (§3.3.5, p. 2683): morphological opening removes isolated estimates; then iterative averaging with windows growing from a few hundred metres to 20 km; beyond 20 km, the image mean.

## 4. Quantitative results to compare against (§4, Table 5, p. 2683–2687)
- Validation vs AERONET at 13 sites, "stable cases" (AERONET AOT std < 0.02 within ±1 h; < 10% cloud within 20 km; < half the neighbourhood gap-filled).
- RMSE AOT(550 nm): MT and MS individually ~0.07 (FormoSat-2), ~0.09 (Landsat); hybrid overall 0.06 (FormoSat-2), 0.08 (Landsat). Per site e.g. La Crau hybrid 0.02 / MT 0.07 / MS 0.03; Boulder 0.08 / 0.08 / 0.13.
- Requirement derived in §3.1: AOT error std below 0.04 (green sites) or 0.08 (arid) keeps surface reflectance error within 0.005 + 0.05ρ.
- AOT in the test data never above 0.7 (and ≤ 0.4 for Landsat stable cases) (p. 2673): **only light haze was tested.**

## 5. Stated limitations
- MT "needs two clear dates separated by less than two months" (Howland failed, p. 2684).
- Fast landscape change breaks MT: Yaqui in May, "all of the vegetation is quickly drying, and the assumption of stable reflectances is not valid" (p. 2686).
- Both methods weaker over bright surfaces; constant aerosol model per site.

## 6. How to apply to our pipeline
- **`sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym._correct`:** our t = (A − dark(after)) / (A − tone(dark(before))) is the image-space analogue of err1/err2: "corrected after should match the clear reference". MACCS adds safeguards we can copy:
  1. **Change screen in a haze-insensitive cue.** MACCS drops pixels whose NIR/SWIR changed. We have no NIR. Candidate substitutes to test as arms: local gradient/edge structure (haze lowers contrast but keeps edge positions; a flood moves/erases them), or before–after local correlation (Hagolle 2010 veto). Pixels failing the screen should not inform t.
  2. **Minimum valid share per window:** require ≥ X% screened-valid pixels in each estimation window before estimating t; else abstain ("cannot assess"). MACCS uses 40%. Ours today: a tile-level 1,000 clear-pixel rule only.
  3. **Insensitive-pixel rule:** MACCS rejects pixels whose corrected value hardly depends on the haze. Our analogue: where tone(dark(before)) is close to A (bright ground), t = (A − dark_after)/(A − ref) is ill-conditioned; reject or abstain when A − tone(dark(before)) is below a margin, rather than relying on T_MIN alone.
  4. **Estimate t coarse, then smooth and interpolate** (MACCS: 7 × 7 coarse neighbourhoods, 15 × 15 Gaussian, bilinear upsampling). This supports a smooth, low-resolution haze field, consistent with our finding that a texture-following t flattens detail (guided filter off).
  5. **Dark-object ceiling:** an upper bound on haze from the darkest pixels (assumed reflectance ~0.01), also required dark on the reference date. Analogue: cap the haze in a window by the darkest after-pixel that was also dark before (shadows), which is close to what the dark channel already does.
  6. **Gap filling by growing windows** for windows that abstain, if a full haze map is wanted; MACCS fills up to 20 km.
- **Flood caveat (direct statement in the paper):** rapid whole-landscape change breaks the stable-surface assumption. A flood is that case; keep "cannot assess" where the change screen fails.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** the MT idea transfers (two dates, fixed view is roughly true for our aligned tiles). No physical AOT retrieval is possible (no calibration, no LUT). The MS blue–red relation is a reflectance-space relation and does not transfer to uint8 display tones. Safeguards 2, 3, 4 and 6 are directly codeable; 1 needs a substitute cue to be tested.

## 7. Key quotes
- "a multi-temporal method that assumes that the surface reflectances are stable with time" (abstract, p. 2668)
- "we discard the pixels for which the NIR (FormoSat-2) or SWIR (LandSat) reflectance has changed too much" (p. 2676)
- "A minimum of 40% of useful pixels within the neighborhood is required" (p. 2676)
- "the assumption of stable reflectances is not valid." (p. 2686, Yaqui drying)
