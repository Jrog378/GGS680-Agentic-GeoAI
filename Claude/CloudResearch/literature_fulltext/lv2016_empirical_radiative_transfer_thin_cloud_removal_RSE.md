# Coder handoff: Lv, Wang & Shen (2016), An empirical and radiative transfer model based algorithm to remove thin clouds in visible bands

- **Citation:** Lv, H., Wang, Y., & Shen, Y. (2016). An empirical and radiative transfer model based algorithm to remove thin clouds in visible bands. *Remote Sensing of Environment* 179, 183–195. https://doi.org/10.1016/j.rse.2016.03.034
- **PDF:** `/Users/jusrogers/Masters/papers/lv2016_empirical_radiative_transfer_thin_cloud_removal_RSE-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher PDF downloaded through Justin's GMU session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** real PDF (`file`: PDF document; 4.2 MB). Read tool and pdfinfo: 13 pages = published range 183–195. Page-1 title, three authors and DOI match. §6 Conclusions (p. 194) and references (pp. 194–195) present. PASS.
- **Read:** pp. 183–195 in full (page images), including all figures and tables.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's. Co-author Y. Wang: East Carolina University; part-funded by USGS AmericaView.

## 1. Algorithm, step by step (§2, pp. 184–187)
Model (eq. 1, from Gao et al. 1998): `ρ*_j = ρ_cj + T_j ρ_j`, with ρ*_j the TOA reflectance of band j, ρ_cj the cloud reflectance, T_j the two-way transmission through the cloud, ρ_j the surface reflectance. Inverse: `ρ_j = (ρ*_j − ρ_cj) / T_j` (eq. 2).

Three assumptions:
1. **Clear-sky bands are linearly related** (eq. 3): `ρ_j = a_ij ρ_i + b_ij` for any two visible bands.
2. **Cloud reflectance across visible bands is linearly related** (eq. 4): `ρ_cj = c_ij ρ_ci + d_ij`.
3. **Over water, cloud reflectance in visible bands is linear in NIR** (eq. 9): `ρ_cNIR = k1 ρ_ci + k2`, `ρ_cNIR = k3 ρ_cj + k4`, and under cloud over water ρ*_NIR ≈ ρ_cNIR because "Water absorbs entirely the solar radiation at NIR band" and visible water reflectance is small (p. 187).

Solving:
- Combine eqs. 1, 3, 4: `ρ*_j = c_ij ρ_ci + d_ij + a_ij T_j ρ_i + b_ij T_j` (eq. 5); with `ρ_ci = ρ*_i − T_i ρ_i` (eq. 7):
  **`ρ_i = (c_ij ρ*_i − ρ*_j + b_ij T_j + d_ij) / (c_ij T_i − a_ij T_j)`** (eq. 8). Per pixel this is a linear combination of two TOA bands.
- **a_ij, b_ij**: least squares on clear pixels (Fmask) of band j vs band i (p. 187). Keep the four pairs with highest R² (used: a12/b12, a23/b23, a34/b34, a43/b43; Table 1, p. 185, e.g. a12 = 1.278, b12 = −0.059, R² 0.973).
- **k1…k4**: least squares of NIR (band 5) vs each visible band on **thin-cloud-covered water pixels** (Table 2, p. 186: 1.122/−0.138, 1.080/−0.100, 1.105/−0.050, 1.066/−0.021; R² ≥ 0.937 on 264,320 px).
- **c_ij = k1/k3, d_ij = (k2 − k4)/k3** (eq. 11, p. 187).
- **T_i, T_j** from clear pixels where ρ* = ρ (eq. 12) solved with eq. 3: **`T_i = 1 − a_ij d_ij / (b_ij c_ij)`, `T_j = 1 − d_ij / b_ij`** (eq. 13). **T is one constant per band for the whole scene**, not a per-pixel map.
- Apply eq. 8 to every pixel (cloud and clear). Thick cloud (red box) masked out.
- **Assessment** (eq. 14, p. 188): averaged spectral bias `ASB_i = mean |ρ_input − ρ_reference|` against a clear reference image of the same path 16 days earlier (one revisit), plus mean/SD, histograms and spatial correlation.

## 2. Inputs, outputs, data needs
- **TOA reflectance**, ≥ 2 visible bands **plus one NIR band**, an Fmask cloud mask, and **water pixels under thin cloud** somewhere in the scene (needed for k1–k4).
- Main test: Landsat-8 OLI path 41/36, 8 Jan 2014 (7,901 × 7,761 px), Los Angeles/Mojave; reference: 23 Dec 2013 clear image (pp. 188). Also Landsat-8 40/37 10 April 2015 (1000 × 1000) and **WorldView-2 18 Oct 2010, 1.85 m**, Blounts Bay, coastal North Carolina, bands 1–5 (pp. 192–194).
- Output: cloud-removed surface reflectance per visible band.

## 3. Quantitative results to compare against
- Whole scene (Table 4, p. 187): ASB before 0.0153–0.0168, after 0.0131–0.0149 (bands 1–4).
- **Cloud-covered pixels** (14,825,494 px; p. 191): ASB 0.056/0.057/0.053/0.054 → **0.019/0.018/0.020/0.023**. Spatial correlation with the reference (Table 5, p. 189): 0.496/0.547/0.656/0.730 → **0.782/0.822/0.840/0.885**.
- Clear pixels: mean change 0.0006/0.0004/0.0003/0.0003 (Fig. 8, p. 191), i.e. clear pixels preserved.
- Areas A–D (500 × 500 each; Table 6, p. 192): ASB after 0.013–0.038; urban area D improves least (band 1: 0.042 → 0.038).
- vs HF, HOT, IHS (Table 7, p. 194): e.g. area A band 1 ASB 0.072 (HF), 0.124 (HOT) vs 0.016 (this method). Run time on the full scene: 95 s vs HF 1,874 s, HOT 649 s, IHS 1,947 s.
- **WorldView-2 and the April Landsat scene: visual only, no numbers** (pp. 192–194).
- No significance tests; one reference date; reference 16 days apart assumed unchanged.

## 4. Stated limitations / caveats
- Built for sensors with "multiple visible bands and one NIR band" (p. 194). Not for thick cloud (masked).
- The authors do not discuss limits further. From the method (our reading): T constant per scene means spatially varying cloud thickness is absorbed by the additive ρ_c term only; the water-pixel step needs cloud over water.

## 5. How to apply to our pipeline (Maxar RGB uint8, 0.5 m, no NIR, not TOA reflectance)
- **Direct use: not feasible as published.** It needs NIR to isolate cloud reflectance over water (assumption 3) and TOA reflectance. Our tiles are display-stretched RGB with no NIR.
- **What transfers:**
  1. **Assumption 1 on the before date.** With a clear before image we do not need the band-pair regression (eq. 3) to stand in for the surface; we have the surface. But the same linear inter-band fit on clear pixels is a cheap check of whether our RGB is still roughly linear after the Maxar stretch: fit R vs G, G vs B on clear pixels and report R² (paper: 0.90–0.98 in TOA reflectance).
  2. **Assumption 2 (cloud colour is linear across bands)** is the RGB part we can use. Arm "Lv cloud line": on after-image pixels the spotter calls thin cloud, regress the after−(gain·before) residual in band j on band i; a tight line (R² > 0.9, like Table 3's 0.885–0.993) means one haze colour per scene and supports a band-linked A in `I = J·t + A(1−t)`. Replace NIR-over-water with the **before-date** surface to get ρ_c: `ρ_c ≈ ρ*_after − T·ρ_before` on invariant pixels. This is our adaptation, not their method.
  3. **Constant T per scene** is the paper's choice; our per-window t is the more flexible model. Their good results with a global T suggest testing a global-T arm as a baseline (fewer parameters, less overfitting to flood darkening).
  4. **Metric:** ASB (eq. 14) = mean absolute error vs a clear reference, per band; spatial correlation before/after. Both are trivial in numpy and match what we already compute.
- **Water caution:** their method *uses* water as the dark target. In our flood scene, new water is the change we want to detect, so any step that treats dark water as "known surface" must use the before-date water only.
- **Evidence weight:** RSE (JIF > 4). Quantitative evidence is one Landsat-8 scene against one reference date; the WorldView-2 (closest to our VHR case) result is visual only.

## 6. Key quotes
- "We first assume that under the clear sky condition, the TOA reflectance values from ground targets within any two visible bands are linearly related." (p. 185)
- "The second assumption is that the influence among visible bands caused by thin clouds is linearly related as well" (p. 185).
- "Water absorbs entirely the solar radiation at NIR band. ρNIR is about 0, or ρcNIR = ρcNIR*." (p. 187)
- "In cloud-free areas, the algorithm did not alter spectral characteristics of cloud-free pixels." (abstract, p. 183)
- "The proposed method is developed to remove thin clouds in visible band images acquired by sensors that have multiple visible bands and one NIR band." (p. 194)
