# Coder handoff: Czerkawski et al. (2022), deep image prior (internal learning) cloud inpainting

- **Citation:** Czerkawski, M., Upadhyay, P., Davison, C., Werkmeister, A., Cardona, J., Atkinson, R., Michie, C., Andonovic, I., Macdonald, M., & Tachtatzis, C. (2022). Deep internal learning for inpainting of cloud-affected regions in satellite imagery. *Remote Sensing* 14(6), 1342. https://doi.org/10.3390/rs14061342
- **PDF:** `/Users/jusrogers/Masters/papers/czerkawski2022_deep_image_prior_cloud_inpainting_RemoteSens-summary.pdf` (page 1 = AI summary)
- **Source:** publisher's version (CC BY 4.0), MDPI CDN https://mdpi-res.com/d_attachment/remotesensing/remotesensing-14-01342/article_deploy/remotesensing-14-01342.pdf (the www.mdpi.com/…/pdf link returned an "Access Denied" bot page). Code: https://github.com/cidcom/satellite-cloud-removal-dip ; data: https://doi.org/10.5281/zenodo.5897695
- **Validation:** PDF 61.7 MB, 18 pages (Read tool; pdfinfo agrees) = article "1 of 18" to "18 of 18"; title, ten authors and DOI match Crossref; Conclusions (§4, p. 14) and 52 references present. PASS. (Venue JIF: evidence 05 lists 4.3, "confirm in JCR"; not checked here.)
- **Read:** pp. 1–18 in full; reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
Per image, no pretraining. Modes (Fig. 2, p. 5): (a) **single cloudy image + mask only**; (b) residual vs SAR; (c) residual vs historical optical reference; (d) stacked + SAR (MS); (e) stacked + historical optical reference (MT); (f) both (MS-MT). The historical reference is a **static mean of all clear images of the previous year** (2019), not the last clear image (p. 5). So mode (e) is "clear older reference + cloudy date", close to ours; mode (a) is pure single-image inpainting.

## 1. Algorithm (§2.2, pp. 4–6)
- Deep image prior (Ulyanov et al.): a CNN with fixed noise input z is optimised so its output matches the known (non-masked) pixels; loss excludes the cloud mask; the masked region is whatever the network produces. In stacked modes the network outputs [target; supporting channels] and the supporting channels are fully supervised (mask applied only to the cloudy query) (p. 5).
- Adam (β1 0.9, β2 0.999, ε 1e-8), **lr 2 × 10⁻², 4,000 steps, regularisation noise 0.1**; ~2 min per 256 × 256 (2.5 × 2.5 km) patch on a Titan RTX; 4 repeats per mode, median-SSIM run shown (pp. 6, 14).
- Inputs: S2 L2A clipped [0, 10⁴] / 2000; S1 in dB, clipped (VV [−25, 0], VH [−32.5, 0]) shifted to [0, 2] (p. 4).

## 2. Data and protocol (§2.1, pp. 3–4)
- Two sites (Scotland, India), 2019 clear images = reference (18 / 34), 2020 clear images = test (20 / 30); **17 real S2 cloud masks (10–50% cover) pasted onto clear test images** → 340 / 510 cases with exact truth (Table 1). No train/test split needed (internal learning).
- Cover sweep: artificial masks 0.5–64% (Figs. 5–6).
- Blind test: 3 + 3 real cloudy L1C images, manually masked, compared qualitatively with DSen2-CR (§3.3).

## 3. Quantitative results (Table 2, p. 9; Fig. 5)
| Inpainted region SSIM / RMSE | Basic | MS-R | MT-R | MS | MT | MS-MT |
|---|---|---|---|---|---|---|
| Scotland | 0.66 / 0.15 | 0.41 / 0.23 | 0.71 / 0.15 | 0.65 / 0.14 | 0.76 / 0.12 | 0.76 / 0.11 |
| India | 0.61 / 0.13 | 0.42 / 0.21 | 0.64 / 0.15 | 0.60 / 0.12 | 0.69 / 0.11 | 0.70 / 0.09 |
- Whole-image SSIM 0.84–0.88 (the clear part is fitted directly, so whole-image scores flatter the method).
- Cover sweep: inpainted SSIM ≈ 0.8 (Scotland) / 0.75 (India) for 0.1–16% cover; drops beyond 16%, never below 0.6.
- Optical reference up to 1 year old still helped (p. 14). Finer-detail scenes (India) are harder.

## 4. Stated limitations (pp. 9, 13, 14)
- "The techniques presented all rely on the application of high-quality cloud masks"; "Leakage of cloud components outside the mask can affect the optimisation process" (p. 12).
- "the synthesised images can vary depending on the run" (p. 14).
- Snow (saturated, low variance) made MT optimisation unstable (p. 9). SAR adds texture distortions.

## 5. How to apply to our pipeline
- **As a fill for opaque cloud in the after image: do not use for flood scoring.** Mode (a) invents from surrounding texture; mode (e) fills with before-structure + surrounding after-context — the same no-change trap as VPint2 for a flooded road wholly under cloud.
- **Usable without inventing content:**
  1. **Mask transfer with exact truth + cover sweep** — identical in spirit to VPint2 and our E3 plan: paste real cloud masks (HRC_WHU or our own gates) onto clear after-tiles, and sweep covered fraction (0.5–64%) to find where correction/abstention breaks. Report the **masked-region** score separately from the whole tile (whole-tile scores are inflated by untouched pixels — applies to our flood recall too: score covered roads only).
  2. **Report run-to-run variance** for any stochastic arm (they ran 4 repeats; we should do the same for DINO/RF arms with random pixel sampling in `sn8_cloudspot`).
  3. **Mask leakage**: a gate that misses the thin cloud fringe corrupts any fit that treats outside-gate pixels as clean — the same mechanism as the haze ring in `sn8_cloudedge` (fringe outside the 71 cut). Supports the margin/fade and hysteresis-grow arms (`sn8_cloudsym` `low`).
- **Feasibility:** runs on our data (any channels, no training; ~2 min per 2.5 km patch on a 24 GB GPU; our tiles are smaller in area but 20× more pixels per km). Only sensible as a labelled display product.

## 6. Key quotes
- "The approach is restricted to model tasks where a significant part of the information required for reconstruction is not obscured in the source sample." (p. 2)
- "the benefit of the temporal reference was maintained even when the time difference between the synthesised image and the reference was as large as 1 y" (p. 14)
- "Leakage of cloud components outside the mask can affect the optimisation process of the proposed synthesis methods by distorting the texture distribution of the image." (p. 12)
- "the synthesised images can vary depending on the run" (p. 14)
