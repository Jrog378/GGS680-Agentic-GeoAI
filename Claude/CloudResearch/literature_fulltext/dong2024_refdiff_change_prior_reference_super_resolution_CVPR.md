# Coder handoff: Dong et al. 2024, Ref-Diff (CVPR 2024)

**Citation:** Dong, R., Yuan, S., Luo, B., Chen, M., Zhang, J., Zhang, L., Li, W., Zheng, J., & Fu, H. (2024). Building
bridges across spatial and temporal resolutions: Reference-based super-resolution via change priors and conditional
diffusion model. *CVPR 2024*, 27674–27684. doi:10.1109/CVPR52733.2024.02614
**Copy:** CVF Open Access PDF ("identical to the accepted version" except watermark), 11 pp = 27674–27684.
PDF: `/Users/jusrogers/Masters/papers/dong2024_refdiff_change_prior_reference_super_resolution_CVPR-summary.pdf`
(page 1 = AI summary; paper PDF page n = file page n+1). **Read:** PDF pp. 1–11 (supplement not read). Claude, 2026-10-29.
Code/data: github.com/dongrunmin/RefDiff.

## What it is
Reference-based **super-resolution** (8×, 16×), not cloud removal. Relevant to us only for the change-gated use of a
prior-date reference.

## Method
- EDM diffusion (Karras et al. 2022): loss E[λ(σ)‖D(y+n;σ) − y‖²]; D_θ(x;σ) = c_skip(σ)x + c_out(σ)F_θ(c_in(σ)x; c_noise(σ))
  (Eq. 2, p. 3).
- Inputs concatenated to the noisy image: LR (upsampled), Ref (HR, other date), **multi-class change mask** (no-change +
  "changed to class k"). In training and in the headline results the mask is **ground truth**: "we use the ground truth
  of the land cover change mask as the condition" (p. 4).
- Decoder: two modified SFT modules, F_{i+1} = γ_i(F_e ⊕ F_i)·F_i + β_i(F_e ⊕ F_i) (p. 4): semantics-guided (mask + LR)
  for changed areas; Ref-texture-guided (mask + Ref) for unchanged areas; applied iteratively. Guidance is concatenated
  with current features because practical change maps are "usually between 60% to 80%" accurate (p. 4). So the gate is
  **soft and learned**, not a hard copy/no-copy switch.
- LR synthesis: blur (iso/aniso/motion), resize, Gaussian noise, JPEG. 256² crops, batch 48, Adam 1e-4, 500k it.,
  dropout 0.2, 4×A800.

## Evaluation
- SECOND (0.5–1 m, multi-sensor, 7 classes; 2,668 train / 1,200 test) and CNAM-CD (0.5 m Google Earth 2013–2022, 6
  classes incl. "others: clouds, hard shadows"; 2,258 / 1,000).
- Metrics: LPIPS (AlexNet) and FID only, as they "better quantify both fidelity and perceptual quality than PSNR and
  SSIM" (p. 6). No PSNR/SSIM, no significance tests.

## Numbers (Tables 1–3, PDF pp. 6–7)
| Setting | Ref-Diff GT mask LPIPS / FID | Predicted mask (ChangeFormer, F1) | Best baseline LPIPS / FID |
|---|---|---|---|
| SECOND 8× | 0.2642 / 32.60 | 0.2657 / 33.15 (F1 87.7) | HSR-Diff 0.2689; EDM* FID 34.58 |
| SECOND 16× | 0.3433 / 33.97 | 0.3404 / 35.05 (F1 84.9) | HSR-Diff 0.3437; EDM* FID 37.56 |
| CNAM-CD 8× | 0.2791 / 43.02 | 0.3159 / 48.33 (F1 87.1) | HSR-Diff **0.3045**; EDM* FID 53.15 |
| CNAM-CD 16× | 0.3519 / 45.65 | 0.3889 / 56.79 (F1 87.2) | HSR-Diff **0.3771**; EDM* FID 59.43 |
- With predicted masks the paper says it "still outperforms the comparison methods" (p. 7): true for FID; **false for
  LPIPS on CNAM-CD** (HSR-Diff is better).
- Ablation (Table 2, SECOND 8×): LR only 0.3115 → +Ref 0.2886 → +mask 0.2785 → both SFTs 0.2642 LPIPS.
- Failure modes (Fig. 4, p. 8): missed change (FN) "may lead to the introduction of false textures"; false positives
  also degrade output.

## How to apply to our pipeline / Ida test
- **Principle only; no code to port.** Our two-date de-hazing (`sn8_cloudsym.either_date_dehaze`) borrows from the clear
  date only the cloud's gain/offset, never content. Ref-Diff is the CVPR precedent for the rule "trust reference
  texture only where a change prior says unchanged" and quantifies what happens when the change prior is wrong (FN →
  copied reference texture). Cite it in the methods text for why we never copy content, and for why any future
  content-borrowing arm would need a change gate.
- **Concrete check for the Ida test (new, cheap):** within thin cloud, compute per road strip the DINOv2 distance of the
  two-date output to the **pre** image and to the **NOAA** image. If an arm moves cloudy flooded roads toward the pre
  (dry) image rather than toward NOAA, it is leaking reference content — the Ref-Diff FN failure. Report the count of
  strips where dist(arm, pre) < dist(arm, NOAA) on roads NOAA shows as changed, per arm.
- **Metric:** supports LPIPS/feature distances over PSNR at 0.5 m (pre-registration outcome 1 primary; outcome 7
  secondary). Could add LPIPS (AlexNet) as a second feature metric beside DINOv2, to show the outcome is not a DINOv2
  artefact. Grey→3-channel repeat, as for DINOv2.
- **Feasibility:** method infeasible (training, multi-class change labels, RGB); the leak check and LPIPS are feasible.
