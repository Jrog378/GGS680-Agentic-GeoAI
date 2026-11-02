# Coder handoff: Sui et al. 2024, Diffusion Enhancement (DE) + CUHK-CR (IEEE TGRS 62)

**Citation:** Sui, J., Ma, Y., Yang, W., Zhang, X., Pun, M.-O., & Liu, J. (2024). Diffusion enhancement for cloud
removal in ultra-resolution remote sensing imagery. *IEEE TGRS* 62, 1–14. doi:10.1109/TGRS.2024.3411671
**Copy:** arXiv:2401.15105v1 (25 Jan 2024), 13 pp; only v1 exists; **pre-review submission**, published version is 14 pp
and may differ (numbers below are v1's). PDF: `/Users/jusrogers/Masters/papers/sui2024_diffusion_enhancement_cuhk_cr_TGRS-summary.pdf`
(page 1 = AI summary). **Read:** pp. 1–13. Code/data: github.com/littlebeen/Diffusion-Enhancement-for-CR (data on
HF `littlebeen/DE`, per evidence 19). Claude, 2026-10-29.

## CUHK-CR (the part most useful to us)
- Jilin-1KF01B push-broom, pan-sharpened 2 m MS → 0.5 m; bands B, G, R, NIR (Table II, p. 4).
- Sites (Table III, p. 4): Shenzhen 35.72 km² (cloudy 2022-08-24, clear 2022-09-03 = 10 d), Jinan 34.76 km² (08-24 /
  09-10 = 17 d), Hangzhou 25.62 km² (2023-01-31 / 01-21 = 10 d, **clear image before cloudy**).
- CUHK-CR1 thin: 668 images (534 train / 134 test); CUHK-CR2 thick: 559 (448 / 111); 8:2 split, random (not spatially
  blocked — tiles from the same 25–36 km² scene are in both splits).
- Masks: Cloud-Net binary, no thin/thick distinction; mean cloud coverage probability 50.7 % (CR1), 42.5 % (CR2).
  Fully obscured images removed by eye (p. 4).
- **No co-registration** between cloudy and clear images is described (searched "regist", "align": none).
- Licence: not stated in the paper.

## DE method (p. 5–6)
- DDPM forward q(x_t|x_0) = N(√ᾱ_t x_0, (1−ᾱ_t)I); noise predictor ε̂_θ(x_t, t, y) conditioned on cloudy y;
  L_DDPM = E‖ε − ε̂_θ‖².
- x_{0,ε,t} = (x_t − √(1−ᾱ_t) ε_t)/√ᾱ_t; reference prior x_{0,E} = E(y) from a pretrained end-to-end remover
  (MemoryNet or MSDA-CR); blend **x_{0,t} = (1 − W) ⊙ x_{0,ε,t} + W ⊙ x_{0,E}** (Eq. 13), W from a UNet "Weight
  Allocation" net, clamped to [η, 1], η = 0.3 at inference; W falls toward 0 over denoising steps (Fig. 9).
- L_WA = |x̃_0 − x_{0,t}| (stop-grad on diffusion branch); L_joint = λ L_DDPM + L_WA, λ = 1; lr 1e-5; 64→256 px
  coarse-to-fine; DDIM 50 steps; one RTX 4090.

## Numbers (Table V, p. 7; Table VII, p. 11)
| | CUHK-CR1 thin PSNR / SSIM / LPIPS | CUHK-CR2 thick |
|---|---|---|
| MemoryNet | 26.073 / 0.7741 / 0.0315 | 24.224 / 0.6838 / 0.0403 |
| DE-MemoryNet | **26.183** / 0.7746 / **0.0290** | **24.348** / 0.6843 / **0.0369** |
| MSDA-CR | 25.435 / 0.7483 / 0.0374 | 23.755 / 0.6661 / 0.0433 |
| DE-MSDA | 25.739 / 0.7592 / 0.0321 | 23.968 / 0.6737 / 0.0372 |
| CVAE | 24.252 / 0.7252 / 0.1075 | 22.631 / 0.6302 / 0.0489 |
- DE gain over its own reference net: +0.11 to +0.30 dB. No error bars/significance.
- Training resolution matters: 1 m- vs 2 m-trained models on 0.5 m test differ by 1.2 dB PSNR (Table VII).
- Pure diffusion "often fail[s] to precisely align with the actual scene" (p. 5); "undesirable fake textures" (p. 2).

## How to apply to our pipeline / Ida test
- **Outside-Ida test bed (thin cloud, 0.5 m, real pairs):** use CUHK-CR1 test images (RGB → grey with the SpaceNet
  weights) to score **single-image arms** (`sn8_clouds.dehaze`, He 2011) and the **t gate** (pre-registration outcome 4
  analogue: does low t predict large distance to the clear image?), and the cloud masks (dark-rise/spotter F1 vs
  Cloud-Net masks, caveat: Cloud-Net is not human truth).
- **Do not score the two-date arm against the same clear image it uses as reference** (circular: gain/offset fitted on
  the scoring image). Evidence 19's dataset row suggested exactly this ("the near-date clear image plays the reference
  date"); that design leaks. A valid two-date test needs a third, independent clear date per site (not in CUHK-CR) or
  must be restricted to checking that clear ground does not move (guard only).
- **Register first:** CUHK-CR has no stated co-registration; run `sn8_coreg.tile_shift`-style (or the AROSICS-style
  local mode) on clear pixels before any metric, and report the residual.
- **Spatial leakage:** random 8:2 split within 3 scenes; if we ever train on CUHK-CR (e.g. the spotter), re-split by
  spatial blocks.
- **Licence unknown:** research-only until clarified (as evidence 19 said).
- **DE itself:** not adoptable (4-band training, invents texture, conflicts with our gain/offset-only rule). Possible
  research-only comparison arm on CUHK-CR only, using the released weights; never in the library.
