# Coder handoff: Shen, Li, Qian, Zhang & Yuan (2014), adaptive homomorphic thin-cloud removal (visible bands)

- **Citation:** Shen, H., Li, H., Qian, Y., Zhang, L., & Yuan, Q. (2014). An effective thin cloud removal procedure for
  visible remote sensing images. *ISPRS J. Photogramm. Remote Sens.* 96, 224–235. https://doi.org/10.1016/j.isprsjprs.2014.06.011
- **Copy read:** open author copy, https://sendimage.whu.edu.cn/wp-content/uploads/222014_An-effective-thin-cloud-removal-procedure-for-visible-remote-sensing.pdf
  (publisher layout, final version). PDF with summary: `/Users/jusrogers/Masters/papers/shen2014_thin_cloud_removal_visible_images_ISPRS-summary.pdf`
- **Validation:** PDF, 12 pages = pp. 224–235 (Crossref range), title/authors/DOI match Crossref; conclusion, acknowledgements
  and references present. The header labels it "Review Article", but it is a method paper.
- **Pages read:** 224–235 (all), equations checked on the rendered p. 227.
- **Supports ranked fixes (evidence 21):** #10 (visible-band physical correction arm), #1 (blue/red gradient colour
  feature), #7 (haze lowers gradients → texture), and the turbid-water check required by #1.

## Model and assumptions
- Image = illumination × reflectance: `f(x,y) = i(x,y) · r(x,y)` (Eq. 1). "The path radiance is neglected in the presented
  method and the effect of the thin cloud is attributed to the transmittance of the atmosphere" (p. 225).
  **Note:** this is multiplicative only, unlike He et al.'s `I = J t + A(1 − t)` (additive airlight). The two arms rest
  on different physics.
- Thin cloud is low-frequency: thin clouds "are usually assumed to locate in the low frequency of a cloudy image" (p. 225).
- Visible bands only: "only visible channels are concerned and treated in this paper" (p. 226).

## Algorithm (exact steps)
**Algorithm 1, classic HF (p. 225), per band:**
1. `z = ln f`.
2. `Z(u,v) = FFT(z)`.
3. `S = H(u,v) · Z` with a high-pass (low-suppress, high-enhance) filter `H` with cut-off frequency `D`.
   **The paper does not state the form of H** (Gaussian, Butterworth, etc.) or the gain levels. The coder must choose,
   e.g. Gaussian high-emphasis `H = (γH − γL)(1 − exp(−D(u,v)²/(2D0²))) + γL`; that choice is ours, not the paper's.
4. `s = IFFT(S)`, `g = exp(s)`.
5. Linear stretch to the input range (Eq. 2): `gL = a0 + (b0 − a0)/(b − a) · (g − a)`, `[a0,b0]` = input range,
   `[a,b]` = range of g.

**Stage 1, cut-off per band (§3.1, p. 226–227):**
- Mean gradient per band (Eq. 3):
  `Ḡ_i = 1/((M−1)(N−1)) · Σ_x Σ_y sqrt( ((F_i(x,y) − F_i(x+1,y))² + (F_i(x,y) − F_i(x,y+1))²) / 2 )`.
- Brightness-normalised (Eq. 4): `Ḡ_N,i = (B_r / B_i) · Ḡ_i`, `B` = band mean DN, reference band r = blue.
- Empirical rule (Eq. 5): `D_1 · Ḡ_N,1 ≈ D_2 · Ḡ_N,2 ≈ D_3 · Ḡ_N,3 = C`. Tune `D_blue` by hand, set `C = D_blue · Ḡ_N,blue`,
  then `D_i = C / Ḡ_N,i`.
- Table 1 values (four images, bands blue/green/red): D = 13/10/6, 20/16/11, 15/11/7, 8/6/3; C ≈ 35, 34, 21, 13.
  Units of D are not stated (frequency index). The cut-off "varies with the sub-images" (p. 234).

**Stage 2, high-fidelity removal (§3.2):**
1. *Cloud identification* (p. 228): `e = f − gL`; `e > 0` → cloudy, else clear. 3×3 continuity template: a centre pixel
   with `e < 0` whose 8 neighbours all have `e > 0` is set cloudy (hole filling).
2. *Adaptive HF* (Eqs. 6–7): clear pixels keep `f`; cloudy pixels take the HF output re-stretched to the dynamic range of
   the **clear** pixels, with the top and bottom 2% excluded (p. 228).
3. *Turbid water* (§3.2.3): spectral-angle classification against class centres (turbid water class required); within
   water, a pixel is cloudy if `DN_i > mean clear-water DN_i` in all bands, clear if ≤ in all, else uncertain. Cloudy:
   moment matching `DN' = σ'/σ · (DN − μ) + μ'` (Eq. 8; μ, σ of cloudy water pixels, μ', σ' of clear water samples).
   Uncertain: `F = t·DN + (1 − t)·DN'`, `t = n/N` = share of bands where `DN ≤` clear-water mean (Eq. 9).

**Stage 3, mosaicking (§3.3):** process only cloudy sub-images; at each seam, blend `F_M = k f + (1 − k) F`, `k = d/L`
(Eq. 10) as written; d = distance to the seam, L = adjustment width, "tuned manually".
(As printed, k = d/L weights the *original* f more with distance, while the text says pixels further from the seam should
be closer to the corrected value; one of the two is a typo. Implement the text's intent: weight on the corrected value
rises with d.)

## Parameters / defaults
- `D_blue`: manual. `L` (seam width): manual. 2% trim for the target range. 3×3 template. No other constants.

## Data needs / outputs
- Input: visible bands, DN values (no calibration). Output: corrected image; a binary cloud map (from `e > 0`) as a
  by-product; water class map.

## Results to compare against
- Clear-pixel fidelity factor `R = Σ|f − F| / M` over manually chosen clear samples (Eq. 11). Adaptive HF lowest in all
  bands on three Landsat ETM+ images (Table 2), e.g. image 2: HOT 2.18/2.21/2.92 vs adaptive HF 0.31/0.40/0.96.
- No accuracy against a clear reference image; GaoFen-1 2 m results (Fig. 11) are visual only.

## Limitations (stated)
- "The method is limited to remove thin clouds" (p. 234); "no information is under the thick clouds" (p. 227).
- First cut-off and seam width are manual (p. 234–235).
- Turbid water: HF brightness decrease "will cause serious radiometric distortion of the water surface" (p. 228).

## Key quotes
- "thin clouds cause two changes in visible images: high brightness and a low gradient" (p. 226).
- "with the increase in the wavelength, the influence of the thin clouds decreases so that the details, including edges
  and textures, increase" (p. 227).
- "the average gradient is positively related to the wavelength, and the cut-off frequency is negatively related to the
  wavelength" (p. 227).

## How to apply to our pipeline
- **Module:** a new arm next to `dehaze()` in `ProjectBranch/ClaudeFunctions/sn8_clouds.py` (and as an alternative to the
  dark-reference correction in `sn8_cloudsym.py`), e.g. `homomorphic_dehaze(rgb, valid, d_blue, ...)`.
- **Feasibility on 0.5 m RGB uint8, one clear pre-storm date, no NIR/SWIR/SAR:** high. Needs only the three visible bands
  and works on DN. Work on float `log(rgb + 1)`. Mask invalid pixels (fill them before the FFT, e.g. with the band mean,
  to avoid edge ringing). At 0.5 m, a cloud is hundreds of pixels across, so `D` must be re-tuned; Landsat/GaoFen values
  cannot be copied.
- **Use the before date to tune D_blue** instead of by eye: choose D_blue that minimises after-vs-before difference on
  invariant clear pixels (ties to fix 5). That is our extension.
- **Turbid water is the main risk:** flooded roads are exactly the bright, homogeneous, low-gradient surface that this filter
  darkens. The paper's water step needs a supervised turbid-water class; for us, a flood/water mask from the before
  date + DINO change would have to stand in. Report flooded-tile errors separately (fix 1 requirement).
- **Colour feature for `sn8_cloudspot.py` (fix 1, item 4):** compute Eq. 3 per band in a local window and use
  `Ḡ_N,blue / Ḡ_N,red`. The paper uses scene-level gradients; a per-window ratio is our adaptation.
- **Texture (fix 7):** cite this paper for "haze lowers gradients", supporting the attenuation argument for
  `sn8_texture.py`/`sn8_glcm.py` features.
- **Scoring:** same as fix 4 (task-driven, NOAA-visible tiles); also report Shen's R on clear tiles as a fidelity check.
