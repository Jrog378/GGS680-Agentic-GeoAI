# Coder handoff: Wang, Wang, He, Ma, Wang, Zhang, Cheng & Pun (2026), GACR (observation-anchored residual flow)

- **Citation:** Wang, Z., Wang, M., He, Y., Ma, X., Wang, Z., Zhang, H., Cheng, Y., & Pun, M.-O. (2026). Interpretation-oriented cloud removal via observation-anchored residual flow with geo-contextual alignment. ECCV 2026 (arXiv comment: "accepted by ECCV 2026"). arXiv:2607.02471v1 (2 Jul 2026). No DOI yet; Crossref check not possible.
- **PDF:** `/Users/jusrogers/Masters/papers/wang2026_gacr_observation_anchored_cloud_removal_ECCV-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint, https://arxiv.org/pdf/2607.02471 . Code: https://github.com/wzy6055/GACR
- **Validation:** PDF 6.3 MB, 34 pages (Read tool; pdfinfo agrees; `file` misreported 1). pdfinfo title/authors and first page match the arXiv record (CUHK-Shenzhen, Shanghai AI Lab, SWJTU; Man-on Pun corresponding, also a DE author). Conclusion (§5) and references present; supplementary appendices A–E follow. PASS (preprint; camera-ready may differ).
- **Read:** main text §1–5 (paper pp. 1–15) and appendices B–E in full; Appendix A derivation and the reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
**Single cloudy image only.** The velocity net is `Net_θ(x_t, t, x_c)` with x_c the cloudy image (eq. 9); the DINOv3 "prior" is used only in the training loss on the clear target. No reference date at inference. Under opaque cloud it generates ("the stochastic component ε provides generative flexibility for semantic completion", p. 6).

## 1. Algorithm (§3, pp. 5–8; Table 5)
- Forward interpolant (eq. 4): `x_t = α_t x* + β_t x_c + σ_t ε`, with α_0 = 1, β_0 = 0, σ_0 = 0, α_T = 0, β_T > 0 (eq. 5); linear schedule `α_t = 1 − t, β_t = ρ t, σ_t = t` (eq. 6). **ρ = 3** (Table 11: ρ 0 → 3 raises PSNR 32.26 → 33.02 dB on Vaihingen-thick; larger ρ slightly worse).
- Flow matching: target velocity `v_t = E[α̇ x* + β̇ x_c + σ̇ ε | x_t]` (eq. 8); loss `L_vel = E||u_t(x_t) − α̇ x* − β̇ x_c − σ̇ ε||²` (eq. 11); inference Euler steps `x̂_{t−1} = x̂_t + Δt u_t(x̂_t)` (eq. 10), **4 sampling steps**.
- GCPA: `z* = f_vfm(x*)` (frozen DINOv3 ViT-L/16, SAT-300M or LVD-1689M weights) (eq. 12); `z_t = MLP(RE(AP(h_t)))` from the HDiT bottleneck (eq. 13); `L_GCI = −E[(1/N) Σ_n cos(z*^[n], z_t^[n])]` (eq. 14); `L = L_vel + λ L_GCI`, **λ = 0.5** (eq. 15, Table 4).
- Backbone: HDiT, depth [2,2,2,2], widths [128..1024], neighbourhood attention kernel 7, patch p = 2 (p = 1 better but 4× FLOPs). 73.8 M params, 56 GFLOPs (Table 6). 200k steps, batch 4, AdamW 1e-4, one A800; images **resized to 256 × 256**.
- Downstream evaluators (App. B): frozen DINOv3 + light decoders trained **on clear images**; upper bound = clear test images, lower bound = cloudy test images, "end-to-end" = decoders trained and tested on cloudy images.

## 2. Data (§4.1, App. C)
- **CUHKCR-EXT** (from [48], DFCFormer authors): Jilin-1, 0.5 m, Guangzhou (31 images 3600², "primarily covered by thin clouds") and Changsha (34 images 3000², "higher proportion of thick clouds"); 3686/922 and 2800/700 train/test 256 px tiles. Land-cover (6 LCZ types) labels; building masks drawn by the authors in CVAT on areas kept apart from the CR split.
- **Synthetic:** ISPRS Potsdam (5 cm, RGB used) and Vaihingen (9 cm, IR-R-G) with clouds from the atmospheric scattering model + Czerkawski et al.'s cloud generator, **extended with a scalar thickness parameter**; same cloud shape at different thicknesses within an image (thin and thick variants). Resized to 256 px, so the effective GSD is not 0.5 m.
- No validation split is listed (Table 5 gives training/test only), yet "validation every 10k steps to select the model with the best performance" (App. D.1); baselines also "correspond to the checkpoints achieving the best validation performance" (App. D.2). Which data were used is not stated.

## 3. Quantitative results
- **CR fidelity** (Table 1, PSNR dB / SSIM): CUHKCR-EXT-GZ (thin, real) GACR-SAT/1 26.10/0.744 vs EMRDM 25.86/0.747, Restormer 25.84/0.743; CUHKCR-EXT-CS (thick, real) 24.35/0.713 vs DFCFormer 23.88/0.711. Synthetic: Potsdam thin 33.64 vs 31.41; Potsdam thick 31.05 vs 28.83; Vaihingen thin 36.92 vs 33.62; Vaihingen thick 34.05 vs 30.40. **Gains on real cloud: 0.2–0.5 dB; on synthetic: 2–4 dB.**
- **Downstream** (Table 2, frozen DINOv3-LVD evaluators): GACR-SAT/2 best among CR methods on most tasks (e.g. SEG-4 0.737 vs EMRDM 0.692; HE-2 RMSE 2.014 vs 2.133). But **end-to-end training on cloudy images**: CLS-1 0.833 = GACR 0.833; **CLS-2 0.876 vs GACR 0.781**; BLD-1 0.691 vs 0.704; BLD-2 0.698 vs 0.710. With DINOv3-SAT evaluators (Table 7) end-to-end beats GACR on CLS-1 (0.830 vs 0.753), CLS-2 (0.890 vs 0.729) and BLD-2 (0.709 vs 0.707).
- Lower bound (cloudy, no CR) vs upper bound (clear) SEG-2 0.490 vs 0.733 (LVD): cloud costs a lot on dense tasks and CR recovers most of it on synthetic data.
- VFM for GCPA (Table 10, Vaihingen-thick PSNR): DINOv3 33.02 (Table 4), DINOv2 32.55, CLIP 32.20, MAE 31.10, baseline 28.98.
- Single runs, no variance, no significance tests.

## 4. Stated limitations / motivation
- Diffusion models "lack explicit observation anchoring, frequently resulting in geographically inconsistent structures or semantic drift in heavily occluded regions" (p. 2).
- "the end-to-end approach can achieve performance comparable to, or even better than, most CR-based preprocessing pipelines" for classification (App. E.2).
- Change detection is named as a motivating downstream task (abstract) but **not tested**.

## 5. How to apply to our pipeline
- **Do not use GACR output as input to the flood detector.** Single-image generation; under thick cloud it completes semantics from training data. Consistent with evidence 05.
- **Usable without inventing content:**
  1. **Synthetic thin vs thick with one cloud shape at several thicknesses** (Czerkawski generator + scalar thickness). For `sn8_refhaze.haze_recovery` and the E3 mask-transfer plan: hold the cloud shape fixed and sweep opacity, so the point where correction must give way to abstention (our T_MIN = 0.2) can be measured directly on clear after-tiles with known flooded roads. (Justin has put synthetic clouds on hold until real-cloud see-through works — this is for when that changes.)
  2. **Bounds protocol for any correction:** report flood calls on (a) clear truth tiles = upper bound, (b) the cloudy/hazy tile uncorrected = lower bound, (c) corrected, and (d) "end-to-end" = a detector trained with hazy examples. GACR's own tables show (d) can rival (c) — for us this means testing a DINO change detector fine-tuned/thresholded on hazy pairs as an arm against de-haze-then-detect.
  3. **Score correction by a frozen downstream model, not only PSNR.** Same idea as our flood-recall-on-covered-roads metric; they used frozen DINOv3 (research-only for us) — we would use our DINOv2 detector.
- **Feasibility:** retraining needs paired cloudy/clear 0.5 m data (CUHKCR-EXT is Jilin-1; the paper does not say which bands GACR uses on it, and uses RGB / IR-R-G on Potsdam / Vaihingen); one A800-class GPU for 200k steps. Not worth implementing for scoring.

## 6. Key quotes
- "their inherent stochastic sampling process lacks explicit observation anchoring, frequently resulting in geographically inconsistent structures or semantic drift in heavily occluded regions" (p. 2)
- "In thick-cloud regions, the stochastic component ϵ provides generative flexibility for semantic completion." (p. 6)
- "the end-to-end approach can achieve performance comparable to, or even better than, most CR-based preprocessing pipelines" (App. E.2)
