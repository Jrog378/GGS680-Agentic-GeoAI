# Coder handoff: Meng, Wang, Duan, Xiang & Pan (2013), Efficient Image Dehazing with Boundary Constraint and Contextual Regularization (BCCR)

- **Citation:** Meng, G., Wang, Y., Duan, J., Xiang, S., & Pan, C. (2013). *ICCV 2013*, 617–624. https://doi.org/10.1109/ICCV.2013.82
- **PDF:** `/Users/jusrogers/Masters/papers/meng2013_boundary_constraint_dehazing_ICCV-summary.pdf` (page 1 = AI summary)
- **Source:** CVF open access, https://openaccess.thecvf.com/content_iccv_2013/papers/Meng_Efficient_Image_Dehazing_2013_ICCV_paper.pdf (proceedings pagination 617–624).
- **Validation:** PDF, 1.45 MB, 8 pages (Read tool last page = p. 624; pdfinfo 8) = published range; title/5 authors/DOI match Crossref; Discussion and Conclusion (§V) and 15 references present. PASS.
- **Read:** pp. 617–624 in full.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§II–III, pp. 618–621)
1. **Airlight A:** min-filter each colour channel (moving window), A_c = max of that channel (p. 620). (A "modified version of He et al.'s method".)
2. **Boundary constraint map** (eq. 7, per pixel): `t_b = min_c( max( (A_c − I_c)/(A_c − C0_c), (A_c − I_c)/(A_c − C1_c) ), 1 )`, so that J = (I − A)/t + A stays inside [C0, C1]. Grey: drop min_c.
3. **Patch transmission** (eq. 9): `t_hat = closing(t_b)` = min over patch of max over patch (morphological closing). He's t̃ is the max filter alone (eq. 8); the closing "allows the transmissions in a local patch to be slightly different" and gives "fewer halo artifacts" (p. 619).
4. **Contextual weights** (eqs. 17–18), with D_j = 8 Kirsch operators + 1 Laplacian (Fig. 4): colour form `W_j = exp(−Σ_c |D_j ⊗ I_c|² / 2σ²)` or log-luminance form `W_j = (|D_j ⊗ ℓ|^α + ε)^−1`, ε = 0.0001. Experiments use the **log-luminance form, α = 0.5** (p. 621) → grey-native.
5. **Objective** (eq. 19): `λ/2 ‖t − t_hat‖² + Σ_j ‖W_j ∘ (D_j ⊗ t)‖₁`.
6. **Solver** (eqs. 20–26): split u_j ≈ D_j ⊗ t; loop β from 1 to 2⁸, ×2√2 each round, one inner iteration:
```
u_j = sign(a)*max(|a| - W_j/beta, 0),  a = D_j ⊗ t                      # eq. 23 (soft threshold)
t   = IFFT( (λ/β F(t_hat) + Σ conj(F(D_j))∘F(u_j)) / (λ/β + Σ |F(D_j)|²) )   # eq. 26 (circular boundary)
```
7. **Recover:** J = (I − A)/[max(t, ε)]^δ + A, ε = 0.0001, δ = 1 by default ("fine-tuning", eq. 3).

## 2. Parameters and scale
- **C0 = (20,20,20)ᵀ, C1 = (300,300,300)ᵀ** — on the **0–255 scale** (C1 above 255 on purpose, so the upper bound rarely binds) (pp. 619–621).
- **λ = 1.0** for all examples; **α = 0.5**; patch **7 × 7** (Fig. 5), **17 × 17** in Fig. 3; δ = 1.0; σ (colour weights) not given.
- No run-time numbers despite "efficient" (FFT solve, a few iterations).

## 3. Quantitative results
- None. Visual comparisons with Tan, Tarel (ICCV'09 and IV'10), Fattal, Kratz, Ancuti, He (Figs. 7–10). Claimed: smaller halos than He at depth jumps, better sky.

## 4. Stated limitations (p. 624)
- "Single image dehazing often suffers from the problem of ambiguity between image color and depth … some white objects in the scene often have a confusing color with the hazes" → "excessive or inadequate enhancements". The boundary constraint is "a much weak constraint"; tighter radiance envelopes or scene geometry could help.
- Circular boundary in the FFT (wrap-around at tile borders: pad our tiles).

## 5. How to apply to our pipeline
- **`sn8_cloudedge` arm (new "h: BCCR refine"):** replace the 41 px window t + linear fade with a per-pixel data term + L1 edge-aware smoothing:
  - data term t_hat: our current data t (`parts["t_data"]`, which already uses the before image's tone-matched dark channel as J's dark channel) after a **closing** (`cv2.dilate` then `cv2.erode`, 7–17 px; Meng's order is max-then-min on t, i.e. closing of t), not a max filter alone;
  - weights from the **after** image's log-luminance (`np.log(after/255 + 1e-4)`), Kirsch ×8 + Laplacian, α = 0.5;
  - solve eq. 19 with λ = 1 via the FFT scheme (pad by reflection to kill wrap-around; mask no-data by setting its weights to 0 and its data weight small).
  - L1 + edge weights let t keep a step where the after image shows a cloud edge and stay smooth elsewhere; unlike the guided filter, t is not a linear function of the guide, so after-image texture is not copied into t.
- **Two-date boundary constraint (our extension, not in the paper):** the before image gives a per-pixel radiance estimate J_ref = tone(before). Bounds C0 = J_ref − k, C1 = J_ref + k (k from the clear-pixel residual spread) give a per-pixel t_b that stops the correction from pushing a pixel outside what the clear date makes plausible. Careful: on flooded pixels J truly changed, so k must be generous or the bound copies the before date.
- **Scale:** if coding on [0,1] data divide C0, C1 by 255 (20/255 ≈ 0.078, 300/255 ≈ 1.18).
- **Feasibility:** fully feasible, grey, no SAR/NIR; FFT solve on a 1300² tile is well under a second per iteration in numpy.

## 6. Key quotes
- "the patch-wise transmission t̃(x) based on this assumption in [5] is often underestimated" (p. 619)
- "Instead of using the integral of L2-norm for the regularization, we employ the integral of L1-norm. This is because that L1-norm is generally more robust to outliers than L2-norm." (p. 620)
- "some white objects in the scene often have a confusing color with the hazes" (p. 624)
