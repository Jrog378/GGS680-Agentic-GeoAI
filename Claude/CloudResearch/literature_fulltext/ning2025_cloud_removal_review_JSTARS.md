# Coder handoff: Ning, Xie, Yin & Liu (2025), cloud removal review for optical remote sensing

- **Citation:** Ning, J., Xie, L., Yin, J., & Liu, Y. (2025). Cloud removal advances: A comprehensive review and
  analysis for optical remote sensing images. *IEEE JSTARS* 18, 15914–15930.
  https://doi.org/10.1109/JSTARS.2025.3580718
- **Copy read:** published version, gold open access (CC BY 4.0), from IEEE Xplore
  (`https://ieeexplore.ieee.org/ielx8/4609443/10766875/11039671.pdf?arnumber=11039671`, the PDF link in Crossref).
  17 pages = 15914–15930.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ning2025_cloud_removal_review_JSTARS-summary.pdf`
- **Validation:** real PDF (5.7 MB); title, 4 authors, volume and pages match Crossref; conclusion and references
  present. PASS (published version).
- **Pages read:** 15914–15925 in full (text, Tables I–V and Figs. 8–9 viewed as images); conclusion p. 15925;
  references (≈ 15925–15930) skimmed.
- **Ties to ranked fixes (evidence 21):** #8 (taxonomy table), primarily. #4 (it warns about synthetic pairs) and
  #5/#6 (multitemporal methods fail under ground change) as supporting context only.

## Taxonomy (the reusable part)
| Class | Sub-class | Notes from the paper |
|---|---|---|
| Single-image | Statistical/physical: spatial, frequency (low-pass), physical (ASM priors) | Spatial: only "speckled clouds". Frequency: "determining the optimal cutoff frequency … is typically challenging" and may lose low-frequency information in clear regions. Physical: e.g. Zhang et al. 2002 (HOT, "clear line"; limitation "requirement for manual sample selection") and DCP ("darker than the real truth and often over-saturated"), Table I (p. 15916) |
| Single-image | Deep learning: CNN/U-Net, GAN, CycleGAN | Needs synthetic paired data; poor generalisation to real clouds (p. 15917) |
| Multimodal | Multispectral (conventional, deep learning) | Exploits band sensitivity; requires accurate physical parameters (p. 15918) |
| Multimodal | SAR fusion (GAN, non-GAN) | Thick cloud; speckle noise causes artifacts; registration effort (p. 15919) |
| Multitemporal | Non-blind (needs a cloud mask): similarity, model-driven (low-rank/tensor), deep learning | Model-driven methods "presuppose a minimal ground change"; mask errors degrade results (pp. 15920–15921) |
| Multitemporal | Blind (no mask): model-driven, data-driven, SAR-fusion hybrids | Usually needs more than two dates with varied cloud cover (p. 15921) |

## Benchmark experiment (pp. 15922–15924; only numbers stated)
- Data: RICE1 (500 pairs, synthetic semitransparent haze, 512 × 512), RICE2 (736 cloud/mask/clear triplets, thick
  cloud), SEN12MS-CR-TS (53 sites, 15,578 samples, 30 time steps, 13-band S2 + 2-band S1, 256 × 256).
- Training: the 10 single-image methods were "trained for 1000 iterations"; the multimodal/multitemporal methods "for
  60 iterations". This is very short, so the numbers are not comparable to the original papers.
- Table IV (RICE1 SSIM / PSNR / RMSE / LPIPS): DCP 0.86 / 17.17 / 10.363 / 0.09; FFA 0.94 / 28.59; ChaIR 0.959 / 32.41
  / 5.294 / 0.038. RICE2: DCP 0.826 / 17.06; ChaIR 0.91 / 34.6.
- Table V (SEN12MS-CR-TS SSIM / PSNR / RMSE / LPIPS): DSen2-CR 0.881 / 29.94; GLF-CR 0.886 / 30.16; TASANet 0.894 /
  30.93; DiffCR 0.895 / 31.13 / 5.387 / 0.204; U-TAE 0.879 / 29.12; CR-TS Net 0.882 / 29.72; UnCRtainTS 0.892 / 30.27 /
  5.913 / 0.247.
- Quality caveats: single runs, no variance and no significance tests. Table IV's caption says "CIEDE" but its columns
  are RMSE. Citation numbers in Tables III–IV do not always match the text numbering (e.g. FFA [150] in the table vs
  [152] in the text).

## Key quotes (page)
- Single-image methods "excel in scenarios with haze and semitransparent clouds" (p. 15924); they perform "poorly when
  faced with thick or irregularly distributed cloud cover" (p. 15914).
- Multitemporal methods are "not suitable for areas with significant ground feature changes" (p. 15914). "an extended
  interval could see changes in terrestrial and spectral properties that adversely affect the restoration process"
  (p. 15922).
- Synthetic pairs: "These synthetic image pairs tend to exhibit substantial generalization errors, significantly
  diminishing their effectiveness in cloud removal when applied to actual cloudy images" (p. 15925).
- "some research discard multispectral information by converting ORS images into RGB three-channel images" (p. 15925).

## How to apply to our pipeline
- **Fix 8 (methodology table):** use the review's first split (single-image / multimodal / multitemporal) and the
  multitemporal non-blind/blind split. Place our steps as follows:
  - `sn8_clouds.dehaze` (dark channel): single-image / physical.
  - `sn8_cloudsym.either_date_dehaze` (dark-reference using the other date): multitemporal, non-blind (it uses our
    cloud gate as the mask).
  - `sn8_cloudspot` (spotter): cloud *detection*, which this review does not cover; cite Li et al. 2022 for that stage.
  - Multimodal: not available (no SAR/NIR); state that this is a data limitation.
- **Fix 4:** quote the synthetic-pair warning as supporting evidence that synthetic scores are not the primary
  validation.
- **Fixes 5/6:** the review backs the "small change" caveat for two-date methods. Our flood change violates it, which
  argues for invariant-pixel fitting.
- **No code to lift.** The benchmarked deep models need paired training data and multispectral/SAR inputs.
- **Feasibility with RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR:** context/taxonomy only. JSTARS is
  above the JIF > 4 bar as listed in evidence 21 (6.3; not re-checked in JCR here).
