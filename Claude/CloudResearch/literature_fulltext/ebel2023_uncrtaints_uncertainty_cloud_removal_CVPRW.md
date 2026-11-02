# Coder handoff: Ebel et al. 2023, UnCRtainTS (CVPRW 2023, EarthVision)

**Citation:** Ebel, P., Sainte Fare Garnot, V., Schmitt, M., Wegner, J. D., & Zhu, X. X. (2023). UnCRtainTS: Uncertainty
quantification for cloud removal in optical satellite time series. *CVPRW 2023*, 2086–2096.
doi:10.1109/CVPRW59228.2023.00202. **Copy:** CVF Open Access (identical to accepted version), 11 pp = 2086–2096.
PDF: `/Users/jusrogers/Masters/papers/ebel2023_uncrtaints_uncertainty_cloud_removal_CVPRW-summary.pdf` (page 1 = AI summary).
**Read:** PDF pp. 1–11. Workshop paper (attribution tier under the JIF rule). Code: patrickTUM.github.io/cloud_removal.
Claude, 2026-10-29.

## Uncertainty formulation (pp. 3–4)
- Per pixel j, prediction ŷ_j ∈ R^K (K = 13 bands); noise model N(y_j | ŷ_j, Σ_j), Σ_j diagonal = diag(σ²_1..σ²_K).
- Loss (Eq. 4): L_NLL ∝ Σ_j [ log|Σ_j| + (ŷ_j − y_j)ᵀ Σ_j⁻¹ (ŷ_j − y_j) ]. Network outputs 2K channels: sigmoid for
  ŷ, softplus for σ². Uncertainty u_j = [σ²_1..σ²_K].
- Ensemble (M = 5, p. 7): ŷ^M = mean ŷ^m; (σ^M)² = mean(σ^m)² + mean(ŷ^m)² − (ŷ^M)² (aleatoric + epistemic).

## Calibration metric (p. 5) — directly reusable
- **UCE(e,u) = Σ_{p=1..P} (N_p/N)·|e(B_p) − u(B_p)|**, P = 20 bins of predicted uncertainty;
  e(B_p) = RMSE of the N_p pixels in bin p; u(B_p) = RMV = sqrt( (1/N_p) Σ_{j∈B_p} (1/K) Σ_k u_j^k ).
- UCE_im: same after averaging RMSE and RMV per image.
- **Error-vs-discard curve (Fig. 3, p. 6):** sort test images by predicted uncertainty, accumulate squared error from
  least to most uncertain; "Discarding the top 50% of uncertain reconstructions almost halves prediction error".
  (Text says sorted by "UCEim" on p. 5, figure axis says "by variance": minor inconsistency. Either way, image level.)

## Results (Tables 1, 4–6)
- SEN12MS-CR-TS, T = 3: RMSE 0.051, PSNR 27.84, SSIM 0.866, SAM 10.16; UCE 0.007, UCE_im 0.010. Least cloudy RMSE
  0.079, SSIM 0.815. No-σ variant RMSE 0.049. 0.5 M parameters.
- Isotropic Σ: UCE 0.023 (3× worse). Ensemble: UCE 0.002, PSNR 28.19. Ensemble without SAR: UCE 0.014.
- T = 2/3/4: PSNR 27.78 / 28.19 / 28.41.
- Mono-temporal SEN12MS-CR: MAE 0.027, PSNR 28.90, SSIM 0.880 (2nd to GLF-CR 0.885).
- Uncertainty also high at **transients** (waves, maturing crops), not only cloud/shadow (Fig. 4, p. 7).
- No significance tests, no error bars.

## How to apply to our pipeline / Ida test
- **Pre-registration outcome 4 (honest gate) — strengthen with UnCRtainTS's two diagnostics, using t as the
  uncertainty proxy (u = 1 − t, or u = spread across gate settings per the optional Ding-style check):**
  1. *Discard curve:* within the cloud gate, sort pixels (or road strips, or tiles) by t ascending; plot mean DINOv2
     distance (and grey error) to NOAA of the retained set as the lowest-t fraction is discarded (0, 10, …, 90 %). A
     monotone fall = t ranks recoverability. Report the error at 50 % discarded vs 0 %.
  2. *Binned calibration:* 20 bins of u; per bin, the observed error to NOAA vs the bin's mean u. UCE needs u and error
     in the same units, so for t use the binned relationship (reliability diagram) and Spearman, not raw UCE, unless we
     map t to a predicted grey error (e.g. fitted on clear-guard pixels).
  - Unit of analysis stays the tile for inference (Statistics section); the curves are descriptive.
- **Floods = transients:** high uncertainty at real change is expected (p. 7). In our gate, flood darkening could look
  like "low t"/uncertain; report outcome 4 separately on NOAA-flooded vs NOAA-dry road strips.
- **Arms:** "least cloudy" baseline ≈ our "as is"; keep it.
- **Module:** evaluation script for the Ida test; optional helper `uncertainty_curves(t_map, err_map, mask)` in
  `sn8_cloudsym.py` or a new eval module. No change to the de-hazing itself.
- **Feasibility:** metrics feasible now; the network is not (S2 time series + S1).
