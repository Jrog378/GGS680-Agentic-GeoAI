# Coder handoff: Ma, Wang, Tong & Atkinson (2022), TIIN, temporal information injection network for haze removal

- **Citation:** Ma, X., Wang, Q., Tong, X., & Atkinson, P. M. (2022). A deep learning model for incorporating temporal
  information in haze removal. *Remote Sensing of Environment* 274, 113012. https://doi.org/10.1016/j.rse.2022.113012
- **Copy read:** author's accepted manuscript, Lancaster EPrints, https://eprints.lancs.ac.uk/id/eprint/170270/1/TIIN.pdf.
  It has 43 double-spaced, line-numbered pages. Page numbers below are the **manuscript's**.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/ma2022_tiin_temporal_information_haze_removal_RSE-summary.pdf`
- **Validation:** real PDF; title and authors match Crossref (article 113012, vol. 274); conclusions, acknowledgements and
  references present. PASS (accepted manuscript; the typeset layout differs).
- **Pages read:** 1–43 (all); Eqs. 4–10 checked on rendered pp. 14–15.
- **Supports ranked fixes (evidence 21):** #4 (synthetic haze from *external* patterns, not our model), #9 (band-linked
  transmission across RGB), #5/#6 (two-date use, with the small-change assumption made explicit).

## Most reusable part: the haze simulation (pp. 14–15), usable without the network
- Transmission (Eq. 4): `t(x) = exp(−β(λ, γ(x)) d)`; scattering (Eq. 5): `β = T λ^{−γ(x)}`, with γ "ranges from 0 to 4"
  (citing Chavez 1988).
- Band link (Eqs. 7–9): `ln t_i(x) = (λ_1/λ_i)^{γ(x)} · ln t_1(x)`, i.e. `t_i = t_1^{(λ_1/λ_i)^γ}`. Then
  `I_i = J_i t_i + A (1 − t_i)`.
- Reference transmission from a **real cirrus band** (Eq. 10): `t_1(x) = 1 − ω c(x)`. c = cirrus band from a cloudy
  region, ω ∈ [0, 1] in steps of 0.1 (bigger = heavier); "35 cirrus maps of Landsat-8 OLI from different cloudy regions"
  were used (p. 15).
- In training, γ = 1, the band centre wavelengths were used for λ_i, and A followed Guo et al. (2020b) (value not stated
  here).

## Network (pp. 8–13), for reference only
- Two parallel branches (hazy, temporal neighbour). Each has 2 shallow 3×3 convolutions → a group convolution (1×1, 3×3,
  5×5, 32 channels each) → 3 TII blocks (channel attention SE-style, reduction 4, on the neighbour features, concatenated
  into the hazy branch) → fusion → modified spatial attention (3×3 and 5×5 then 7×7 convolutions, sigmoid) → Retinex
  multiplicative global residual → 3×3 convolution to 7 bands.
- Loss: MSE. Adam (0.9, 0.999, 1e-8), lr 1e-4. 33,635 patches of 32×32 → 100,905 after augmentation; 10% validation;
  about 4 h on a 2080 Ti.

## Results to compare against
- Simulated Case 1, Region 1 (Table 3): CC/UIQI/RMSE. AOD-Net 0.716/0.653/0.064; RSDehazeNet 0.718/0.617/0.074;
  TIIN 0.886/0.813/0.054.
- NDVI-class OA (Table 4, Region 1): 0.759 / 0.805 / 0.927.
- Ablation (Table 5): without TII, CC 0.759; full TIIN 0.886. Without the neighbour (TIIN w/o T2), accuracy is lower
  (Fig. 12).
- Accuracy declines with haze in the neighbour (Fig. 10) and with time gap (Fig. 11, neighbours up to about 21 months).
- Real haze (Regions 7–11): **visual only**, with no reference metrics.

## Key quotes and limits
- The neighbour's "spatial distribution prior … is usually not the same as for the target hazy images due to land cover
  changes. However, the proportion of land cover changes is generally small, as most changes … are driven by vegetation
  phenology and the condition of data acquisition" (pp. 34–35).
- "the simulated haze is similar to but not equivalent to real haze" (p. 36).
- "The key requirement for TIIN is the need for temporally neighboring images, which may not be as straightforward to
  produce for aerial images" (p. 36).

## How to apply to our pipeline
- **Synthetic haze generator (fix 4):** in a test harness (not in production modules), make hazy versions of clear Ida or
  HRC_WHU RGB tiles with `t_B = 1 − ω·c(x)`.
  - c(x) is an *external* pattern: HRC_WHU thin-cloud masks smoothed into soft mattes, or real Landsat/Sentinel cirrus
    maps rescaled. TIIN used Landsat cirrus.
  - Then `t_G = t_B^{(λ_B/λ_G)^γ}` and `t_R = t_B^{(λ_B/λ_R)^γ}`, with Maxar/WorldView band centres (look them up;
    roughly 0.48/0.55/0.66 µm) and γ ∈ {0.5, 1, 2} as a sweep.
  - Label results "external pattern" vs "own model" per evidence 21.
- **Band-linked correction (fix 9) in `sn8_clouds.py` / `sn8_cloudsym.py`:** estimate t on blue (or the dark channel) and
  derive green and red transmission with the same power law, instead of a single grey t. Compare by fold F1.
- **Two-date logic (fixes 5–6):** the TIIN premise, that change is small and mostly phenology, fails for floods. Use the
  before image only through invariant (non-water, non-flood-label) pixels, as evidence 21 proposes.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** the simulator and the band-link rule are
  feasible. The trained network is not: it needs 7-band Landsat reflectance and paired training. Retraining on RGB would
  be a project of its own with simulated pairs only.
