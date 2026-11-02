# Coder handoff: Ju, Ding, Zhang & Guo (2018), gamma-correction-based dehazing model (GDM)

- **Citation:** Ju, M., Ding, C., Zhang, D., & Guo, Y. J. (2018). Gamma-correction-based visibility restoration for
  single hazy images. *IEEE Signal Processing Letters* 25(7), 1084–1088. https://doi.org/10.1109/LSP.2018.2839580
- **Copy read:** accepted manuscript ("SUBMITTED TO IEEE SIGNAL PROCESSING LETTERS" header), UTS OPUS,
  https://opus.lib.uts.edu.au/bitstream/10453/128577/4/Original%2baccepted%2bversion.pdf. There are 6 PDF pages: a
  1-page IEEE copyright notice, then manuscript pp. 1–5, matching the 5 published pages. Page numbers below are the
  **manuscript's**.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ju2018_gamma_correction_dehazing_SPL-summary.pdf`
- **Validation:** real PDF (2.98 MB); title and 4 authors match Crossref (SPL 25(7), 1084–1088); conclusion and
  references present. PASS (accepted manuscript, not the typeset version).
- **Pages read:** all (cover + pp. 1–5, Table I, references); Eqs. 1–10 checked on the rendered pp. 2–3.
- **Ties to ranked fixes (evidence 21):** #9 (γ-linearisation sensitivity arm, gap 3b), as context only. Also a
  possible extra arm beside #10 (an alternative to the dark channel). Not a remote-sensing paper.

## Algorithm (pp. 2–3)
1. Model: I = A·ρ·e^{−βd} + A(1 − e^{−βd}) (ASM, Eq. 2). Gamma correction: I_G = I^Γ (Eq. 1).
2. Assume I_G also obeys the ASM with A_G = A^Γ ("the GC process does not change the location of the atmospheric
   light"). Assume (ρ − 1)e^{−βd} ≈ 0 and linearise (1 + x)^a ≈ 1 + a·x. (The paper prints "(1 + x)^a ≅ a·x", which is
   a typo.) This gives β_G ≅ β − ln(Γ)/d (Eq. 5).
3. A haze-free result (β_G = 0) needs a **per-pixel** exponent Γ̌ = e^{βd} (Eq. 6). The GDM is ρ = (I/A)^{Γ̌} =
   (I/A)^{e^{βd}} (Eq. 7), applied per colour channel (dividing by A per channel restores hue).
4. Depth proxy: d = δ·Mean(Ī) (Eq. 8). Ī is the brightness component and Mean is a mean (box) filter, size 45. The
   justification is that "the scene brightness is increased along with the change of the scene depth".
5. So ρ = (I/A)^{e^{τ·Mean(Ī)}} with **one unknown scalar** τ = βδ (Eq. 9).
6. τ = argmin(−Σ_{c∈{R,G,B}} ‖∇((I^c/A^c)^{e^{τ·Mean(Ī)}})‖²₂) (Eq. 10), the maximum contrast principle, solved over
   the **whole image** by golden-section search.
7. A is estimated as in He et al. (DCP).
- **Parameters:** mean filter 45 px; A from DCP. The search bracket for τ and the definition of "brightness component"
  (for example the mean of RGB or the V channel) are **not stated**.

## Why no halo (p. 3, Fig. 4)
In the GDM, the albedo changes more slowly with e^{βd} than in the ASM inverse ρ = 1 − (1 − I/A)e^{βd}. So errors in d
near edges move ρ less, and an unrefined mean filter "does not visually introduce halo artifacts".

## Results (Table I, p. 4; only numbers in the paper)
Four benchmark ground photos. Metrics: e (newly visible edges), SSIM, T (s), and UIQI (rows 1–2 only, where ground
truth exists).
- Proposed: row 1 e 0.3651, SSIM 0.9136, T 0.2114, UIQI 0.8176; row 2 e 1.0866, SSIM 0.8926, T 0.2131, UIQI 0.8779;
  row 3 e 0.1572, SSIM 0.9466, T 0.3377; row 4 e 0.5820, SSIM 0.9560, T 0.5895.
- DCP for comparison: SSIM 0.8355 / 0.7251 / 0.8799 / 0.7673; T 0.88–3.00 s.
- Proposed has the highest SSIM in all 4 rows and the highest UIQI in both. Its e is below DCP (0.7445) and BCCR (0.7790)
  on row 4; the authors put this down to their pseudo-edges. MATLAB 2010, i5 laptop.
- All results are on ground-level photos. There is **no remote-sensing image and no statistical test**.

## Key quotes and limits
- GC "is difficult to achieve an optimal trade-off between the over-saturation of close-range regions and the complete
  dehazing of long-range regions" (p. 2).
- "GDM is the key contribution in this letter and it bridges the relationship between GC and traditional ASM" (p. 2).
- Limits: the depth-from-brightness prior is a ground-scene assumption; the derivation needs (ρ − 1)e^{−βd} ≈ 0 (thick
  haze or albedo near 1); the input is assumed to obey the ASM directly, so the camera/display gamma of the input is not
  discussed.

## How to apply to our pipeline
- **Gap 3b / fix 9 (stretch linearisation):** this paper does **not** model a display stretch applied before dehazing.
  It uses a power law *as* the dehazing operator. It therefore gives no support for linearising Maxar DRA output before
  the dark channel. Arm 3-iii (γ ∈ {1.0, 1.8, 2.2}) stays our own sensitivity test. The one transferable result is
  Eq. 5: a power law applied to an ASM image is approximately another ASM image with a depth-dependent change in β.
  Gamma therefore changes the apparent haze thickness non-uniformly. This is consistent with evidence 21's point that a
  non-linear stretch breaks the affine haze model.
- **Optional arm beside `sn8_clouds.dehaze` (dark channel + guided filter):** a GDM-style one-parameter correction,
  `J = (I/A)^{exp(τ · box45(Ī))}`, with τ chosen per tile by golden-section search on the gradient energy. It is cheap
  (no guided filter) and halo-tolerant. Replace "depth" with a **haze-thickness proxy** suited to overhead imagery
  rather than brightness: for example the dark channel, the HOT distance (fix 1) or the residual haze map (fix 6).
  Brightness alone would treat bright roofs, concrete and turbid floodwater as hazy. Note that maximising gradient energy
  also rewards over-enhancement (the paper's own e-score caveat). Score it as in fix 4 (NOAA-visible tiles, fold F1),
  not by contrast.
- **Feasibility with RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR:** feasible. It is single-image,
  RGB-only and fast. The physical premise (depth-driven haze, brightness ∝ depth) does not hold for nadir VHR imagery,
  so treat it as an empirical arm only. Venue: SPL, which is commonly reported below the JIF > 4 bar (confirm in JCR).
  Context, not slide evidence.
