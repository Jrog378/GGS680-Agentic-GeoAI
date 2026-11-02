# Coder handoff: Ju, Ding, Ren, Yang, Zhang & Guo (2021), IDE, dehazing and exposure with an enhanced scattering model

- **Citation:** Ju, M., Ding, C., Ren, W., Yang, Y., Zhang, D., & Guo, Y. J. (2021). IDE: Image dehazing and exposure
  using an enhanced atmospheric scattering model. *IEEE Transactions on Image Processing* 30, 2180–2192.
  https://doi.org/10.1109/TIP.2021.3050643
- **Copy read:** final submitted manuscript, UTS OPUS, https://opus.lib.uts.edu.au/bitstream/10453/146170/2/IDE_final_submission.pdf
  (18.9 MB). There are 14 PDF pages: a 1-page IEEE copyright notice, then manuscript pp. 1–13, matching the 13 published
  pages. Page numbers below are the **manuscript's** (the header numbering).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ju2021_ide_enhanced_scattering_model_dehazing_TIP-summary.pdf`
- **Validation:** real PDF; title and 6 authors match Crossref (TIP 30, 2180–2192); conclusion, references and
  biographies present. PASS (author's final manuscript, not the typeset version).
- **Pages read:** all; Eqs. 1–22 checked on the rendered pp. 4–5; references skimmed.
- **Ties to ranked fixes (evidence 21):** context for gap 3a (how the scattering model is amended). It possibly gives an
  extra cheap dehazing arm beside fix 10 / `dark_reference_dehaze`. It is not evidence for any ranked fix on VHR data.

## Model (pp. 2–4)
- ASM (Eq. 1): I = A·ρ·t + A(1 − t); t = e^{−βd} (Eq. 2).
- Claimed limitation: ASM results look "too dim", worst at close range. The cause given is light "trapped/absorbed in
  textures", with "the light absorption rate … larger with a higher texture density" (p. 3). The evidence is
  qualitative: DCP and LT results vs Retinex-corrected versions, plus δ̂ = (ρ_real − ρ_ASM)/ρ_ASM, which falls with
  CAP-estimated depth (Eq. 3, Fig. 2).
- EASM (Eq. 4): I = A·(1 − α)·ρ·t + A·(1 − t), with α ∈ (0, 1]. The airlight term is unchanged.
- α = 1 − d/max(d) (Eq. 5) = 1 − ln t / ln t_min (Eq. 7), with t_min = e^{−β·max d}. Final form (Eq. 8):
  I = A·(ln t / ln t_min)·ρ·t + A(1 − t).

## IDE algorithm (Algorithm 1, p. 6)
Preset values: p1 = −0.397, p2 = 0.07747, ε = 0.02, δ = 4 (downsampling), s = 75 × 75 (patch).
1. A from the dark channel prior (He et al.).
2. Patch means over Ω (s × s) and channels: Î = mean of I^c over Ω and c; Â = mean of A^c over c (Eq. 10).
3. Grey-world prior: the patch mean albedo ρ̂ = 1/2 (Eq. 11), giving Î = Â·(ln t̃ / (2 ln t_min))·t̃ + Â(1 − t̃)
   (Eq. 12).
4. Replace ln t ≈ p1/(p2 + t) (Eq. 13) → quadratic λ1 t̂² + λ2 t̂ + λ3 = 0 (Eq. 15), with λ1 = Â ln t_min,
   λ2 = ln t_min (Î + Â p2 − Â) − ½ Â p1, λ3 = p2 ln t_min (Î − Â) (Eq. 16).
   Take t̂ = (−λ2 − √(λ2² − 4λ1λ3)) / (2λ1) (Eq. 17), then smooth it with a guided filter (Eq. 18).
5. Albedo (Eq. 20): ρ = (ln t_min / ln t̂)·(1 + (I − A)/(A·t̂)).
6. t_min (the only free scalar): argmin |Ψ(SF(…)) − ε| on the image downsampled by δ = 4. Ψ is the saturation
   (clipped share); ε = 0.02 means "we clip 2% of the pixel values in the shadows and in the highlights". It is solved by
   golden-section search (Eq. 22). The naive t_min = t at the airlight pixel (Eq. 21) fails when patches hold sky or one
   colour.
- **Patch size:** chosen on 4 RESIDE images by PSNR/NIQE over s ∈ {15, 35, 55, 75, 100, 125}. They note that "s = 75 ×
  75 may not be the best size for all images" (p. 6).

## Results (only numbers stated in the paper)
- Table II (dataset means). I-HAZE: IDE R 3.4282, NIQE 3.4009, FADE 0.6175, PSNR 15.7729 (best PSNR: MSCNN 16.5437).
  O-HAZE: IDE R 3.6363, NIQE 2.4359, FADE 0.3133, PSNR 14.1891 (best PSNR: EPDN 16.8753). IDE leads R, NIQE and FADE on
  both datasets, but not PSNR.
- Table I (10 images): the highest R for "almost all" and the best NIQE; FADE and PSNR not always the best. The authors
  explain: "the exposure makes the recovery results brighter than the ground truth images" (p. 9).
- Runtime (Tables III–IV): IDE is the fastest of the MATLAB methods; EPDN (Python) was not timed. Examples: 0.59 s at
  256 × 384; 0.34 s at 200 × 200.
- There are no significance tests and no remote-sensing images. One test image in Fig. 4 is an oblique city view.

## Key quotes
- ASM "has an intrinsic limitation which leads to a dim effect in the recovered results" (abstract, p. 1).
- "the light can be trapped/absorbed in textures and the light absorption rate changes with the texture density" (p. 3).
- "IDE does not require any training process or extra information related to scene depth" (abstract).
- "the employed GWA has a limitation, i.e., when a local patch contains the sky or single colour parts, the average
  albedo of this local patch should be different from the value (0.5)" (p. 5).

## How to apply to our pipeline
- **Do not adopt EASM/α for change detection.** α is tied to scene depth (near = more absorption), which is meaningless
  for nadir 0.5 m imagery. In our scenes t varies with haze thickness, not depth, so α would brighten the least-hazed
  pixels most. The "exposure" step deliberately moves results away from the true radiometry (lower PSNR). That
  conflicts with the two-date consistency that fixes 5–6 rely on.
- **Reusable pieces for `sn8_clouds.py` (dehaze arm, optional):**
  1. A closed-form transmission from the patch mean. In the plain ASM with the grey-world prior, ρ̂ = ½ gives
     Î = Â(½ t + 1 − t), so **t = 2(Â − Î)/Â**, smoothed by a guided filter. This is a low-frequency haze map of the
     kind evidence 21 gap 3a argues for, and it is cheap. However, the grey-world mean of 0.5 fails over floodwater,
     dark asphalt and bright roofs (the paper's own limitation). A better per-patch reference albedo would be the
     **before-image patch mean** (two-date): ρ̂ ≈ mean of the clear before image over Ω after fix 5 normalisation, an
     IHOT-like variant.
  2. A global one-scalar stretch: choose the free parameter so that 2% of pixels clip (ε = 0.02). This could replace a
     hand-set t0 / ω, but it optimises appearance, not accuracy. Score it by fold F1 / NOAA-visible tiles (fix 4).
- **Feasibility with RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR:** feasible (RGB, single image,
  training-free, fast). The physics is not appropriate to our setting, so use it only as an empirical arm.
