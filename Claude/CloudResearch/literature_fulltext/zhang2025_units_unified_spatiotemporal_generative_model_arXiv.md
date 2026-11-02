# Coder handoff: Zhang, Liang et al. (2025), UniTS (unified spatio-temporal generative model)

- **Citation:** Zhang, Y., Liang, S., Li, W., Ma, H., Xu, J., Ma, Y., Xie, J., Li, W., Zhang, M., Tao, R., & Xia, X.-G. (2025). UniTS: Unified spatio-temporal generative model for remote sensing. arXiv:2512.04461v2 [cs.CV] (v2, 6 Mar 2026). HKU (JC STEM Lab), BIT, U. Delaware. No venue stated; preprint. Project page: https://yuxiangzhang-bit.github.io/UniTS-website/
- **PDF:** `/Users/jusrogers/Masters/papers/zhang2025_units_unified_spatiotemporal_generative_model_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** https://arxiv.org/pdf/2512.04461 (v2).
- **Validation:** PDF 10.9 MB, 13 pages (Read tool; pdfinfo agrees; `file` misreported 6); pdfinfo title and 11 authors match the arXiv record; Conclusions (§V, p. 11) and 47 references present. No DOI beyond arXiv. **Appendices A–G (hyperparameters, qualitative results, band/class analyses for cloud removal) are cited but not in the PDF.** PASS (preprint, appendix missing).
- **Read:** pp. 1–13 in full; references skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
**Time series**: sequences of T = 8 Sentinel-2 frames (10 bands, 10 m) + Sentinel-1 (VV, VH), with date and lon/lat metadata. Cloud removal = real cloudy S2 sequence (+S1) → cloud-free sequence. Not a single image, not a one-clear-reference setting. Generative under cloud.

## 1. Algorithm (§III, pp. 3–7)
- Flow matching (eqs. 1–4): `x(t) = (1 − t) x0 + t x1`, target velocity `x1 − x0`, loss `E||f_θ(x(t), t) − (x1 − x0)||²`; inference by ODE (Dopri5, **10 steps**; 10–40 steps roughly equal, Table XIII).
- Backbone: DiT on raw pixel patches (no VAE), interleaved spatial and temporal attention blocks.
- **ACor** (eq. 7): `ĥ = γ(q)·GN(h) + β(q) + h`, γ, β from a 2D conv (spatial) or 1D conv (temporal) on the condition features.
- **STM** (eqs. 8–10): attention `softmax(QKᵀ/√d_k + M)V`, M = w1·(Manhattan-distance position prior) + w2·(auxiliary-data difference prior, from S1 or RGB/NIR).
- Metadata: DOY sinusoidal date embedding; lon/lat via random Fourier features.
- Training: AdamW, lr 1e-4 constant, inputs 128 × 128; details in the (missing) Appendix A.

## 2. Data (§II, Table I)
- Built from **AllClear** ROIs (2022; S2 L1C TOA, 10 bands; S1 GRD; Dynamic World land cover; s2cloudless cloud masks; AllClear shadow masks).
- **TS-S12:** 14,973 ROIs, 256 × 256 at 10 m, clear S2 (< 15% cloud, < 30% shadow) + S1 within ±3 days; sequences 8–97 (median 21); 10,481 / 4,492 train/test; reconstruction uses **binary cloud masks pasted** onto clear frames.
- **TS-S12CR:** 12,126 ROIs; real cloudy S2 + S1 within ±3 days of a clear S2 target; sequences 8–44; mean cloud 84.02%, shadow 87.54%; 8,488 / 3,638.
- Change detection: DynamicEarthNet (Planet RGBN, 3 m, monthly 2018–19, 6 LULC classes) and MUDS (Planet RGB, buildings).

## 3. Quantitative results
- Reconstruction (Table IV, pasted masks): UniTS S2+S1 **30.15 dB** / SSIM 0.926; SeedVR 29.06; U-TILISE 28.69; EMRDM 25.96; linear interpolation 20.87.
- Cloud removal (Table VI, real clouds): UniTS S2+S1 **20.29 dB** / 0.759; S2 only 19.19; U-TILISE 18.41; VDPS 17.65; EMRDM 15.13; "Closest" interpolator 13.24.
- **Pasted-mask vs real-cloud gap: −9.86 dB** for the same model: "the complexity of real cloud coverage scenarios far exceeds that of the simplified scenarios constructed through simulated cloud masks" (p. 9).
- Missing-frame sweep (Table V): 30% → 30.75 dB; 50% → 27.97; 70% → 24.43; 90% → 19.08.
- S1 removed at test: −0.85 dB (p. 10).
- Semantic change detection (Tables VII–VIII): mIoU 42.52 (DynamicEarthNet), 61.96 (MUDS); binary change score BC 12.45 / 8.54; foundation models (Scale-MAE, SatMAE++, SkySense) lower mIoU.
- Ablations (Tables XI–XII): ACor +1.44 dB on cloud removal; ACor beats concat and cross-attention.
- Single runs; no significance tests.

## 4. Stated limitations
None stated explicitly. Snow/ice reconstruct worst ("complicates their distinction from clouds", p. 8). Our reading: needs dense time series; 10 m; appendix (incl. band/class cloud-removal analyses) not public in the PDF.

## 5. How to apply to our pipeline
- **Method: not applicable** (needs a time series and ideally SAR; we have one clear before and one after image at 0.5 m; generative).
- **Usable without inventing content:**
  1. **Pasted binary masks overstate performance by ~10 dB vs real cloud.** Our planned mask-transfer test (VPint2 / Czerkawski style, E3) removes pixels cleanly; real thin cloud mixes signal and haze, and its edges are soft. So: (a) keep real-cloud, label-free checks (`sn8_cloudedge.ring_measures`) as the primary evidence; (b) if a synthetic test is used, paste **semi-transparent** haze (haze model with t < 1 and airlight, soft edges), not binary holes, and report it as an optimistic bound. This matches Justin's "hold off on synthetic until real clouds work" rule.
  2. **Degradation vs covered fraction** (Table V) is the right way to report: our risk–coverage curve by cloud share of a road's strip.
  3. Change detection results show generative backbones can do semantic change at 3 m, but binary change scores are low (BC ≈ 8–12) — no evidence for flood-change use.
- **Feasibility:** none for our data as is.

## 6. Key quotes
- "compared with the time series reconstruction results in Table IV, UniTS's PSNR drops by 9.86 dB. This large gap highlights that the complexity of real cloud coverage scenarios far exceeds that of the simplified scenarios constructed through simulated cloud masks" (p. 9)
- "Most studies focus on reconstructing time series using cloud masks, which oversimplify real-world conditions with variable cloud contamination." (p. 2)
