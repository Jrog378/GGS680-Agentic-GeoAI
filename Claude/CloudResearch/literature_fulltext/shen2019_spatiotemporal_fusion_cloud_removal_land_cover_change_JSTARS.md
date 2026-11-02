# Coder handoff: Shen, Wu, Cheng, Aihemaiti, Zhang & Li (2019), Spatiotemporal-fusion cloud removal under land-cover change

- **Citation:** Shen, H., Wu, J., Cheng, Q., Aihemaiti, M., Zhang, C., & Li, Z. (2019). A spatiotemporal fusion based cloud removal method for remote sensing images with land cover changes. *IEEE JSTARS* 12(3), 862–874. https://doi.org/10.1109/JSTARS.2019.2898348
- **PDF:** `/Users/jusrogers/Masters/papers/shen2019_spatiotemporal_fusion_cloud_removal_land_cover_change_JSTARS-summary.pdf` (page 1 = AI summary)
- **Source:** publisher-formatted copy hosted by the authors' group (WHU SENDIMAGE), https://sendimage.whu.edu.cn/wp-content/uploads/2019_A-Spatiotemporal-Fusion-Based-Cloud-Removal-Method-for-Remote-Sensing-Images-With-Land-Cover-Changes.pdf . OpenAlex lists the paper as closed; this is the authors' own posting. Page numbers below are the journal's 862–874.
- **Validation:** PDF, 7.1 MB; 13 pages by the Read tool and pdfinfo (`file` misreports 10) = the 13-page range 862–874; first-page title/authors/DOI match Crossref; Discussion, Conclusion and 46 references present. PASS.
- **Read:** pp. 862–873 in full (text, eqs. 1–7, Tables I–II from the page images, Figs. 1–8 captions and Fig. 6 plots); references pp. 873–874 and biographies skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (Fig. 1, p. 864; §II)
Inputs: cloudy fine target P_t (date t), clear fine reference P_r (date r), two clear coarse auxiliary images A_t, A_r (same or adjacent dates to t and r, upsampled to the fine grid, cubic convolution), and a cloud mask of P_t. Two preprocessing steps are required: upsampling the auxiliaries and getting the mask (p. 864). Cloud detection is out of scope; the real-cloud test uses a hand-drawn cloud and shadow mask (p. 871).
1. **Stage 1, spatiotemporal fusion (modified STNLFFM, Cheng et al. [40]).** For each cloudy pixel, and also for the pixels on the boundary just outside each cloud patch (needed by stage 2, p. 865):
   - candidates in a w × w window, **w = 41** ("trial-and-error", p. 865);
   - keep candidate i if it is spectrally similar in the reference (eq. 2) **and** shows the same coarse-image change as the centre pixel (eq. 3, "temporal consistency");
   - fit a, b by restricted least squares of A_t on A_r over the similar pixels (p. 865); the linear temporal model is "assumed to be scale-invariant", so coarse a, b apply to fine pixels (p. 864);
   - weight the similar pixels (eqs. 4–5) and predict (eq. 1).
   Modifications to STNLFFM: the "whole weight" term is dropped so that one coarse–fine pair suffices, and weights are per pixel, not per patch, for speed (p. 864).
2. **Stage 2, residual correction (Poisson image editing, Pérez et al. [41]).** Extract the external boundary ∂Ω of each cloud patch from the mask with a Laplacian kernel; compute the residual observed − fused on ∂Ω; solve Laplace's equation over Ω with that boundary value; add the residual to the fused patch; replace the cloudy pixels (p. 866).

## 2. Equations (pp. 864–865)
- (1) `P̂_t(x,y,B) = Σ_{i=1..N} W(x_i,y_i,B) · [a(x_i,y_i,B) · P_r(x_i,y_i,B) + b(x_i,y_i,B)]`; N = number of similar pixels, a, b = per-pixel conversion (temporal) coefficients from the coarse pair, B = band.
- (2) spectral similarity: `|P_r(x,y,B) − P_r(x_i,y_i,B)| < d × 2^{P_r(x,y,B)}` (exponent as printed), **d = 0.01** for Landsat TM (reflectance units), from [40].
- (3) temporal consistency: `| |A_t(x,y,B) − A_r(x,y,B)| − |A_t(x_i,y_i,B) − A_r(x_i,y_i,B)| | < σ`, **σ = 0.005** for MODIS (the uncertainty of the coarse temporal difference, from Gao et al. [39]). "it plays an important role in scenes with significant land cover changes" (p. 865).
- (4) `S(x_i,y_i,B) = exp(−|A_r(x_i,y_i,B) − A_t(x,y,B)| / h²)`, **h = 0.15** ("little influence", p. 865). (5) `W = S / Σ S`.
- (6) `min_f ∬_Ω |∇f − ∇g|²` with `f|∂Ω = f*|∂Ω` (g = fused patch, f* = observed clear pixels around Ω).
- (7) write f = g + f′: `Δf′ = 0 over Ω, f′|∂Ω = (f* − g)|∂Ω` ("membrane interpolation of the mismatch", p. 865).

## 3. Parameters and data the authors used
- Landsat-5 TM bands 1–5, 7 (atmospherically corrected, resampled to 25 m) and MODIS MOD09GA C6 bands 3, 4, 1, 2, 6, 7 (500 m, resampled to 25 m); Lower Gwydir Catchment, Australia, 14 Landsat–MODIS pairs, Apr 2004 – Apr 2005 (p. 866).
- Simulated tests: two **500 × 500** subsets (156.25 km²); site 1 reference 28 Dec 2004, target 14 Feb 2005; site 2 reference 22 Aug 2004, target 3 Apr 2005 (longer gap, more fragmented, more change). The **same manual cloud mask, ≈35% of the image, in the centre**, was pasted on the clear target image; truth = the original clear image (pp. 866–867).
- Time series: reference fixed at 22 Aug 2004, the other 13 dates as targets with the same mask; phenological change before 12 Dec 2004, significant land-cover change after (pp. 869–870).
- Real cloud: 650 × 650 at 25 m (≈265 km²), target 29 Jan 2005 (thin enough to see the ground through it), reference 25 Oct 2004, visual mask (pp. 870–871).
- Metrics: RMSE, CC (simulated); plus AAD and UIQI (time series). Real cloud: visual only.
- Baselines: LLHM [22], MNSPI [23], WLR [24], PM-MTGSR [30] (temporal), STARFM [39] (fusion then replace).

## 4. Quantitative results (Tables I–II, p. 869; reflectance units)
| Mean over 6 bands | LLHM | MNSPI | WLR | PM-MTGSR | STARFM | Proposed |
|---|---|---|---|---|---|---|
| Site 1 RMSE | 0.025 | 0.022 | 0.020 | 0.017 | 0.018 | **0.016** |
| Site 1 CC | 0.756 | 0.749 | 0.778 | 0.812 | 0.829 | **0.855** |
| Site 2 RMSE (more change) | 0.073 | 0.035 | 0.045 | 0.028 | 0.029 | **0.026** |
| Site 2 CC | 0.323 | 0.640 | 0.558 | 0.747 | 0.797 | **0.808** |
- NIR is the exception: PM-MTGSR wins NIR on both sites (site 2 NIR RMSE 0.044 vs proposed 0.050; CC 0.726 vs 0.564), attributed to the MODIS/TM NIR bandwidth mismatch (841–876 vs 760–900 nm) (p. 869).
- Visible bands, site 2: proposed red/green/blue RMSE 0.012/0.016/0.020 against LLHM 0.024/0.027/0.045.
- Time series (Fig. 6, p. 870, read from the plots): during phenological change all methods are close (AAD ≈ 0.01–0.03 except LLHM); after 12 Dec 2004 the temporal methods' RMSE rises to ≈0.05–0.07 (MNSPI, WLR) and ≈0.10 (LLHM) while the fusion methods stay ≈0.035–0.045; PM-MTGSR is best before the change point. No significance tests; differences between STARFM and the proposed method are small ("slightly better", p. 870).
- No per-pixel uncertainty, confidence or flagging is produced; no paired test.

## 5. What fails under land-cover change (the paper's evidence; our main source on this)
- The cause, stated: temporal methods "assume that the spatial coverage of the land cover is fixed during the acquisition interval … appropriate for scenes with phenological changes, but they cannot handle cases with significant land cover changes (especially those with unfixed object boundaries)" (p. 863). Mechanism: "similar pixels in the reference image may experience different temporal variability during the acquisition interval" (p. 871).
- How it fails, by method (pp. 867–871): LLHM "serious directional artifacts" and "cannot capture the significant temporal changes" (all valid window pixels enter the fit "without any optimal filtration"); MNSPI and WLR "evident reconstruction mistakes … primarily caused by the incorrect temporal information borrowed from the adjacent areas with significant changes", and on site 2 "noise-like errors, and the changed spectral signature is not well recovered"; PM-MTGSR "fails to reconstruct the changed land cover" (site 2); on real cloud "none of the [temporal] methods effectively recover the white patch" (p. 871).
- The same holds for multisource optical fill from another sensor without a change source: "identical to the above-mentioned temporal-based methods … cannot generate satisfactory results when major land cover changes occur" (p. 863).
- Their own remedy also fails on small features: "MODIS observations with a 500-m spatial resolution are spectrally mixed in heterogeneous areas and are insufficient to provide temporal information of small features" (p. 869; also p. 871, zoom factor ≈20). For us, every road and house is a "small feature" at any coarse auxiliary resolution.
- Verification limit: "when major land cover changes occur, we cannot confirm what exactly the land covers have turned into … the recovered results of this kind of scene are often unverifiable" (p. 870).

## 6. Stated limitations (p. 872)
- The auxiliary source must match the target's wavelengths and have high revisit; such sources are coarse, so small features are lost.
- Inherent radiometric differences between sensors leave seams; Poisson correction "ease[s]" them; radiometric normalisation could be added.
- The paper is for thick cloud (gap filling); thin cloud is classed as a spectral-method problem (p. 863). The method is a "technical supplement" to temporal methods, not a replacement: choose temporal methods for phenological change and this one for "land cover changes having unfixed spatial tendency" (p. 871).

## 7. How to apply to our pipeline
- **Rule (all de-hazing modules):** do not fill an opaque core (`t < T_MIN` in `sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym._correct`) with before-date content. This paper shows that a reference-only fill copies the pre-change state wherever the change has "unfixed object boundaries", which a flood is. Keep "cannot assess" for opaque pixels; the paper offers no way round it without a near-date change source.
- **Temporal-consistency selection (eq. 3) → `sn8_refhaze` tone curve / local fit.** Our analogue of their similar-pixel screen is the choice of "clear" pixels for the quantile tone curve and the local alpha/beta fit. Their point is that spectral similarity in the reference alone is not enough; candidates must also share the centre pixel's change. We have no coarse pair, but outside the cloud gate the after image itself is observed, so a pixel's own before→after change is known there: exclude pixels whose |tone(before) − after| is large (changed ground, e.g. flood) from the tone-curve and fit samples. This is the same idea as the IR-MAD re-weighting already noted in evidence 05. Arm: tone curve on all clear pixels vs on clear pixels with small two-date change; compare the ring/seam measures in `sn8_cloudedge.ring_measures`.
- **Poisson residual correction (eqs. 6–7) → `sn8_cloudedge` new arm.** Their seam fix is a direct alternative to our 20 m linear fade: compute the residual between the observed after image and our corrected value on the gate's outer boundary, solve Laplace's equation inside the gate with that boundary value, add it. It removes a boundary mismatch smoothly without a geometric fade, which is the ring problem in `sn8_cloudedge` (cause 2, "the fade is geometric"). Implementation: `scipy.sparse` 5-point Laplacian over the gate pixels, Dirichlet boundary from the ring just outside (or `cv2.seamlessClone` with `NORMAL_CLONE` on a 3-channel copy for a quick check). Caveat for us: the residual on the boundary is part cloud fringe, part real change; if the boundary crosses floodwater the membrane will spread flood-vs-dry offset into the cloud. Restrict to boundary pixels with small two-date change, or report it as an arm only.
- **Evaluation protocol → `sn8_refhaze.haze_recovery` / synthetic tests.** Their simulated protocol (one manual mask, ≈35% of the image, pasted on a clear target; truth = the clear image; RMSE and CC per band; same mask for every date) is what our synthetic-haze recovery already does for thin haze. Add their stratification: score separately on pixels that changed between the dates and on pixels that did not (they show the methods separate only where change occurred). Note the standing ruling that synthetic cloud is on hold until real cloud works; this protocol is for when it resumes.
- **Uncertainty/flagging:** the paper produces none. The nearest usable idea is that a pixel's estimate is trustworthy only if enough candidates pass the similarity tests (too small a window "cannot identify enough similar pixels", p. 865). We can flag corrected pixels whose local window had few clear, unchanged samples, as a confidence map alongside t.

## 8. Feasibility with our data
- **The method itself is not feasible.** It needs two clear coarse auxiliary images on (or next to) the target and reference dates, with matching bands. We have no SAR, no NIR, no other dates and no coarse daily sensor in the pipeline: only one clear pre-storm Maxar date and the post-storm date (0.5 m RGB uint8, used as grey). Their own suggested auxiliaries (MODIS, Sentinel-3 OLCI, Sentinel-2) are 10 m–500 m, i.e. 20–1000 × our pixel; the paper itself reports losing small features at a ≈20× zoom factor. Roads and houses would be lost.
- **Feasible pieces:** (a) the simulated-mask protocol with known truth, stratified by changed/unchanged ground; (b) a two-date-change screen on the samples used to fit the tone curve (the eq. 3 idea with the after image standing in outside the gate); (c) Poisson boundary residual correction as an alternative to the linear fade; (d) an "enough clean samples" confidence flag. All run on grey 0.5 m with the existing two dates.
- Scope mismatch to keep in mind: the paper is about thick-cloud gap filling in reflectance (0–1) with atmospheric correction; our thin-haze de-hazing works on 8-bit display grey with nonlinear tone curves. Their d, σ, h values are in reflectance and do not transfer.

## 9. Key quotes
- "the temporal-based methods assume that the spatial coverage of the land cover is fixed during the acquisition interval" (p. 863)
- "they cannot handle cases with significant land cover changes (especially those with unfixed object boundaries)" (p. 863)
- "the temporal consistency condition further removes those pixels which exhibit different temporal variability from the missing pixel, and it plays an important role in scenes with significant land cover changes" (p. 865)
- "when major land cover changes occur, we cannot confirm what exactly the land covers have turned into, even if we had multitemporal images as a reference, so the recovered results of this kind of scene are often unverifiable" (p. 870)
- "The temporal-based group is more suitable for phonological changes with fixed spatial tendency, whereas the proposed method is recommended for land cover changes having unfixed spatial tendency" (p. 871)
