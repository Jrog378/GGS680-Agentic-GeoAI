# Coder handoff: Wen, Marshak, Cahalan, Remer & Kleidman (2007), 3-D aerosol-cloud radiative interaction in collocated MODIS and ASTER images

- **Citation:** Wen, G., Marshak, A., Cahalan, R. F., Remer, L. A., & Kleidman, R. G. (2007). *Journal of Geophysical Research: Atmospheres* 112(D13), D13204. https://doi.org/10.1029/2006JD008267
- **PDF:** `/Users/jusrogers/Masters/papers/wen2007_3d_aerosol_cloud_modis_aster_JGRA-summary.pdf` (page 1 = AI summary)
- **Source:** publisher typeset version as posted on NASA GSFC's climate site, retrieved from the UNT End-of-Term 2008 web archive: https://webarchive.library.unt.edu/eot2008/20080916201317id_/http://climate.gsfc.nasa.gov/publications/fulltext/2006JD008267.pdf (also on NTRS, 20070023463).
- **Validation:** `file` = PDF (its metadata says 10 pages — wrong, as the agent rules warn); Read tool shows page 14 "14 of 14"; pdfinfo 14; 1.17 MB; title/5 authors/DOI match Crossref; Summary and Discussions (§6) and references present; article numbered 1–14 of 14. PASS.
- **Read:** pp. 1–14 in full (references pp. 13–14 skimmed).
- **Type:** observation + 3-D radiative-transfer simulation study, not a method.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. How the distance profiles were obtained
- **Scenes (Table 1, p. 2):** MODIS Terra nadir, Brazil biomass-burning region, 80 × 68 km each, covering collocated ASTER 60 × 60 km.
  - Scene 1 "polluted": 25 Jan 2003, (0°N, 53.78°W), SZA 32°, SAZ 129°, cloud cover 53%, COD mean 12 (sd 10); dark uniform vegetation, albedo 0.011 / 0.025 / 0.055 at 0.47 / 0.65 / 2.13 µm (Table 2); MODIS AOT 0.37 (0.47 µm).
  - Scene 2 "pristine": 9 Aug 2001, (17.1°S, 42.16°W), SZA 41°, SAZ 38°, cloud 40%, COD 8 (sd 8); brighter, varied surface, albedo 0.039 / 0.079 / 0.163; AOT 0.09.
- **Observed (§3):** the 0.5 km pixels selected by the MODIS aerosol algorithm (after cloud mask, brightest 50% and darkest 20% rejected per 10 km box); their reflectance vs distance to the nearest cloud of the standard MODIS cloud mask. Scene 1: 82 pixels, 0.5–3.6 km from cloud (mean 2 km, sd 0.6). Scene 2: 340 pixels, mean 2.15 km (sd 0.97), tail to 6 km.
- **Simulated (§4–5):** I3RC-certified Monte Carlo 3-D code; enhancement Δρ = ρ3D − ρ1D (same aerosol, molecules, surface). Cloud fields: MODIS 1 km COD split to 0.5 km (cloud base 1 km, top from 11 µm Tb, linear LWC, r_eff 10 µm); and ASTER band 2 (0.66 µm) 15 m aggregated to **90 m** COD for two 2 sub-boxes of scene 1. Aerosol lognormal (modal r 0.13 µm, σ 0.6, SSA 0.9); scene 1 AOT 0.2 / 0.1, scene 2 0.07 / 0.05 at 0.47 / 0.66 µm.

## 2. Measured / simulated numbers
- **Observed slopes (scene 1, Fig. 4):** reflectance falls ~**0.0009 per km at 0.47 µm** and **0.0003 per km at 0.66 µm** with distance (0.5–3.6 km). ASTER check: no sub-pixel cloud in those pixels (p. 5). Scene 2: surface too variable for a detectable trend (p. 4).
- **0.5 km simulation, scene 1 (Figs. 6–7):** mean enhancement 0.015 (0.47) and 0.004 (0.66). Large variability within 1 km of cloud (sunlit side bright, shadows small or negative). At 0.66 µm the mean rises from 0.002 at 0.5 km to a max of 0.006 at 1 km, then decreases; at 0.47 µm near-monotonic decrease. **Asymptote ≈ 0.01 (0.47) and 0.004 (0.66) reached about 3 km from cloud.** 90% of clear pixels within ~1.6 km of cloud edges; < 1% beyond 3 km (p. 8). AOT bias 50% / 40%.
- **0.5 km simulation, scene 2 (Figs. 8–9):** variable band within 1.5 km (wider than scene 1 because of the larger SZA, p. 9); maximum at 1.5 km; **asymptote 0.006 / 0.003 about 3 km out**; "even at a distance about 6–8 km away from clouds, the enhancement does not vanish" (p. 10). AOT bias +86% / +60%.
- **90 m ASTER simulation (Figs. 11–12):** "enhancement has a large variability within the first 1 km from cloud edges, and reaches asymptotic values beyond 1 km" (p. 12). Asymptotes: thin cloud (COD ~7) 0.012 / 0.0046; thick cloud (COD ~14) 0.019 / 0.014 at 0.47 / 0.66 µm. AOT bias ~50% (thin), 100% / 140% (thick).
- Coarse resolution widens the apparent near-cloud band: "At a resolution coarser than the true shadow size, the entire pixel would be a shadowed pixel even if it were partly shadowed" (p. 8).

## 3. Authors' conclusions (§6, p. 12–13)
- Enhancement is larger (1) nearer cloud, (2) next to thicker cloud, (3) at shorter wavelength, (4) over brighter surfaces. Shadowing (negative) is stronger at 0.66 µm and over bright surfaces.
- MODIS pixel selection does not remove the enhancement (selected pixels 0.001–0.002 *higher* than all clear pixels).
- 3-D bias in 1-D AOT: 50–140%, expected "to apply in most situations of broken cumulus".
- Limitation stated: "The results in this study are based on two images" (p. 13).

## 4. How to apply to our pipeline
- **Two-part model of the near-cloud excess** (the useful result for us):
  1. a **variable edge band ~1 km wide** (90 m sim) to ~1.5–3 km (0.5 km sim): sunlit side brighter, shadow side darker;
  2. a **non-zero, nearly uniform offset** over all clear gaps in a broken cumulus field (asymptote), still present 6–8 km away.
- **`sn8_refhaze.tone_curve` / `dark_reference_dehaze`:** part 2 is an additive brightening of the whole "clear" area of a cloudy after tile. Quantile matching on clear pixels absorbs it into the tone curve, which is what we want for change detection (it is an acquisition nuisance, Bruzzone's Atm). Check that the fitted curve's offset is larger on cloudy tiles than on cloud-free ones; if so, that is this effect, not ground change.
- **`sn8_cloudedge` fade:** part 1 is 1 km ≈ 2,000 px at 0.5 m, so the 20 m linear fade covers ≤ 2% of the band. Within a 256 m tile the excess past the gate will look like a slow ramp or a constant, not a decay to zero. Arms to test:
  - fade to the tile's **asymptotic excess** instead of to zero (fit `excess(d) = c + a·f(d)` on distance bins; correct `c` everywhere as part of the tone fit, and the `a·f(d)` term near the gate);
  - **sun-side split**: compute distance separately in the sun-facing half-plane (toward the sun azimuth from the gate) and the anti-sun half-plane; apply a wider positive fade on the sun side and a shadow correction (dark-rise negative) on the anti-sun side. SN8 image metadata gives sun azimuth/elevation.
- **Surface brightness matters:** "the larger the surface albedo, the larger the enhancement" and the stronger the shadow reduction. Bright roofs/concrete next to clouds will show more excess than dark vegetation/water; a per-pixel fade weighted by before-image brightness is a physically motivated arm.
- **Feasibility:** all measurements feasible on RGB uint8 with one clear before date; we cannot run 3-D radiative transfer, and we do not need to. No SAR/NIR needed. Blue (0.47) carries the larger, steadier signal; red the more variable one.

## 5. Key quotes
- "The enhancement is too large to be ignored" (abstract, p. 1).
- "clouds enhance reflected solar radiation almost everywhere except in shadowed pixels" (p. 6).
- "enhancement has a large variability within the first 1 km from cloud edges, and reaches asymptotic values beyond 1 km" (p. 12, 90 m).
- "even at a distance about 6–8 km away from clouds, the enhancement does not vanish" (p. 10).
