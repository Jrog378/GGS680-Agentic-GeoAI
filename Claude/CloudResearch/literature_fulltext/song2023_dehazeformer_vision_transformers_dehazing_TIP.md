# Coder handoff: Song, He, Qian & Du (2023), Vision Transformers for Single Image Dehazing (DehazeFormer)

- **Citation:** Song, Y., He, Z., Qian, H., & Du, X. (2023). Vision transformers for single image dehazing. *IEEE TIP* 32, 1927–1941. https://doi.org/10.1109/TIP.2023.3256763 (DOI from Crossref; the published title has no "DehazeFormer:" prefix).
- **PDF:** `/Users/jusrogers/Masters/papers/song2023_dehazeformer_vision_transformers_dehazing_TIP-summary.pdf` (page 1 = AI summary)
- **Source:** **arXiv preprint version**, https://arxiv.org/pdf/2204.03883 (v1, 8 Apr 2022; the only arXiv version). 13 pages vs 15 published: the TIP article may contain revisions not in this copy. Title and authors match the published record.
- **Validation:** PDF, 11.3 MB, 13 pages (Read tool error "This PDF has 13 pages"; pdfinfo 13); first page title/authors match Crossref; Conclusion (§VI) and references present. PASS (preprint; numbers may differ from the journal version).
- **Read:** pp. 1–13 in full (references skimmed).
- **Prepared by:** Claude (AI), 2026-10-29. Code/data: https://github.com/IDKiro/DehazeFormer (not downloaded).

## 1. Method (§III, pp. 3–6)
- 5-stage U-Net of modified Swin blocks: **RescaleNorm** (normalise over (n,c), re-inject µ, σ via linear layers; eq. 7), **ReLU** (GELU/SoftReLU hurt: "invertibility … is essential"), **shifted windows by reflection padding** (no mask), **parallel conv on V** (DWConv K = 5 for T/S/B, ConvBlock K = 3 for M/L), **SK fusion** of skips, **soft reconstruction** J = K·I + B + I with K = 1/t − 1, B = −(1/t − 1)A (eq. 5).
- Training: L1 loss, 256 × 256 crops, AdamW + cosine LR (4→… ×10⁻⁴), batch 8–32. Variants T/S/B/M/L: 0.686M–25.44M params, 6.7–280 GMACs at 256² (Table I/IV).
- Inputs: 8-bit gamma-corrected RGB (default) or 16-bit linear multispectral (RS-Haze MS setting).

## 2. RS-Haze synthesis (§IV, pp. 6–7) — the remote-sensing part
- Clear: 76 Landsat-8 L1 scenes, FLAASH atmospheric correction; haze: cirrus band 9 reflectance of 108 cloudy scenes, 0.1% linear stretch to remove its dark level; t1 = 1 − ω ρ9 (eq. 15).
- Wavelength dependence: β = c0 λ^−γ, t_j = t1^(λ1/λj)^γ (eq. 13); γ from a cubic in ωρ9 (a0 = 6.537, a1 = −27.465, a2 = 41.224, a3 = −21.547, clipped to [0, 4]) (eq. 16, Table II).
- Airlight: mean of brightest 0.01% per channel, then rescaled by a reference from bands 6–7 (Fig. 6).
- Dense-haze fix: t' = 1 − ξ(1 − t), ξ = 1.25, clip [0,1] so dense haze erases ground information (eq. 17) — added because the first synthesis "works well in the dense haze region of the synthetic image, but performs poorly on the dense haze region of the real image" (p. 7).
- Sizes: 512 × 512 patches; L/M/D densities ω ∈ 0.1–0.399 / 0.4–0.699 / 0.7–0.999; 51,300 train / 2,700 test (Table III).

## 3. Quantitative results we could compare to (all synthetic)
- SOTS-indoor PSNR/SSIM: DehazeFormer-L 40.05/0.996; -B 37.84/0.994; FFA-Net 36.39/0.989; DCP 16.62/0.818 (Table IV).
- **RS-Haze-mix:** DCP 17.86/0.734; FFA-Net 39.39/0.969; DehazeFormer-B 39.87/0.971.
- DehazeFormer-S RGB vs MS (Table V): L 43.68 vs 55.44; M 39.58 vs 50.75; D 35.46 vs 43.66; mix 39.57/0.970 vs 49.95/0.993 dB.
- No real-haze evaluation in the paper.

## 4. Stated limitations
- Trained/tested on synthetic pairs only; ablation conclusions "not always consistent" across datasets (p. 9).
- Dense haze harder than light haze (Table V).

## 5. How to apply to our pipeline
- **Not a fit for the current pipeline:** single-date, RGB-trained on Landsat 30 m (or RESIDE photos), needs paired training data, does not use the clear before date, and our sealed/labelled-data rules forbid training on our own synthetic or pseudo labels for now (synthetic cloud generation is on hold). Domain gap 30 m → 0.5 m is large.
- **Usable pieces:**
  - The **RS-Haze synthesis recipe** (cirrus-band transmission, ξ = 1.25 dense-haze decay) is a published, citable way to make synthetic haze if Justin re-opens synthetic tests; `sn8_refhaze.synthetic_haze` could cite it. Note we have no cirrus band, so t1 would need another source (e.g. real dark-rise maps from cloudy tiles).
  - **Soft reconstruction** form J = K·I + B + I with K = 1/t − 1 is the haze model written as a residual; our corrected = (after − L)/t is the same with B = −L/t.
  - Table V is direct evidence that 8-bit RGB loses a lot versus 16-bit MS (≈ 10 dB PSNR) — a caveat to state about our uint8 Maxar tiles.
- **Feasibility:** running a released checkpoint on our RGB tiles is technically possible (no SAR/NIR), but would be an unvalidated cross-domain test; not recommended as a correction step without labels.

## 6. Key quotes
- "we propose a new synthetic remote sensing image dehazing dataset named RS-Haze for evaluating the method's capability to remove highly non-homogeneous haze" (p. 2)
- "the network trained with this dataset works well in the dense haze region of the synthetic image, but performs poorly on the dense haze region of the real image" (p. 7)
- "the additional information provided by more channels and larger bit depths does improve the performance of the method substantially" (p. 9)
