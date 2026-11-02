# Coder handoff: Arp, Hoos, van Bodegom, Francis, Wheeler, van Laar & Baratchi (2024), VPint2

- **Citation:** Arp, L., Hoos, H., van Bodegom, P., Francis, A., Wheeler, J., van Laar, D., & Baratchi, M. (2024). Training-free thick cloud removal for Sentinel-2 imagery using value propagation interpolation. *ISPRS JPRS* 216, 168–184. https://doi.org/10.1016/j.isprsjprs.2024.07.030
- **PDF:** `/Users/jusrogers/Masters/papers/arp2024_vpint2_training_free_cloud_removal_ISPRS-summary.pdf` (page 1 = AI summary, page 2 = Leiden repository cover, pages 3–19 = journal pp. 168–184)
- **Source:** publisher's version (CC BY 4.0) from Leiden University Scholarly Publications, https://hdl.handle.net/1887/4175578 (found via OpenAlex). Code: https://github.com/ADA-research/VPint2
- **Validation:** PDF 5.0 MB, 18 pages (Read tool; pdfinfo agrees; `file` misreported 26) = 1 cover + 17 journal pages = 168–184. Title, seven authors and DOI match Crossref; Concluding remarks (§7, p. 182) and references (pp. 183–184) present. PASS.
- **Read:** pp. 168–184 in full; reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
**Current cloudy image + one older clear reference image of the same place + a cloud mask.** Not single-image generation: values come from the clear part of the current image, structure from the older date. Thin cloud is not corrected: masked pixels are discarded and rebuilt ("since we aim to remove all types of clouds along with their shadows", p. 170).

## 1. Algorithm (§4, pp. 170–174)
Notation: O = cloudy target, F = older clear reference ("feature image"), C = cloud mask, T̂ = output. Per band, independently.
- Init: T̂ = O outside C; mean of O inside C.
- Spatial weight (eq. 3): `γ_ij^{i'j'} = f_ij / f_i'j'` from the reference — the ratio a neighbour must be multiplied by to give this pixel's value in F.
- Update (eq. 2): for (i,j) ∈ C, `t̂_ij^{τ+1} = (1/|N(i,j)|) Σ_{(i',j')∈N(i,j)} γ_ij^{i'j'} · t̂_i'j'^τ`, N = 4-neighbourhood; pixels outside C stay at o_ij. Iterate to equilibrium (typically ~20 iterations; auto-termination).
- **Identity priority** (eqs. 4–5): weight each neighbour's prediction by `λ = β·γ` if γ ≤ 1 else `β/γ`, normalised by Λ_ij = Σλ. Favours same-object neighbours (γ ≈ 1) because between-object relations change more over time ("temporal heterogeneity"). Cannot fix two objects that were one object in F (p. 173).
- **Elastic band resistance** (eq. 7): if the new value exceeds threshold μ, `t̂^{τ+1} = t̂^τ + Δt̂^{τ+1} − k·t̂^τ`; damps runaway ("exploding") values from faulty reference pixels. A hard clip (10,000 reflectance) is also used.
- **Auto-adaptation** (§4.3.3): β, μ, k chosen per patch and per band by grid/random search, scoring on a validation set of clear pixels re-masked (prioritising pixels with the biggest target–reference mismatch); the plain configuration is always tried first.
- Cost: O(e·h·w·4); 30–40 s per 256 × 256 × 12-band patch parallelised over bands (Fig. 7c).
- Requires ≥ 1 clear pixel; at 100% cover it returns the reference (p. 172).

## 2. Data and protocol (§5, pp. 174–177)
- **SEN2-MSI-T:** Sentinel-2 L2A, 12 bands resampled to 10 m; 20 scenes (cropland, forest, herbaceous, shrubs, urban × 4), worldwide; each = cloud-free target at s, a real cloud mask from a cloudy image near s, and references at s − 1 week, 1 month, 3 months, 6 months; 256 × 256 patches.
- **Mask-transfer evaluation:** the real cloud mask is pasted onto the clear target as missing values, so truth is exact and cloud shapes are realistic.
- Masks: S2 L2A cloud-probability band (SEN2-MSI-T), SEnSeIv2 (SEN12MS-CR-TS). "recall should be prioritised over precision for cloud masks"; "buffering cloud masks is recommended" (p. 175). L1C/SAR experiment masks buffered by 5 dilation passes (p. 176).
- Metrics: MAE, MAE on NDVI, MAPE, SSIM (+ PSNR, RMSE, SAM on SEN12MS-CR-TS). Significance: **one-sided Wilcoxon signed-rank, α = 0.05**.

## 3. Quantitative results
- Table 1 (L2A, all reference ages pooled), MAE: cropland VPint2 357.0 / replacement 614.2 / AutoML 460.2 / MNSPI 363.2; forest 199.3 / 421.4 / 402.3 / 214.4; herbaceous 192.9 / 549.8 / 264.3 / 222.9; shrubs 162.4 / 315.8 / 286.4 / 209.9; urban 314.6 / 553.2 / 590.2 / 388.5. SSIM urban 0.786 vs 0.718 (replacement). Better than all, significant except vs MNSPI on cropland and forest.
- Ablation: identity priority matters on urban and cropland; elastic band only on cropland (Table 1).
- Table 2 (L1C, 1-month reference, SAR baselines): VPint2 better than DSen2-CR and UnCRtain-TS except MAE on NDVI for cropland and urban.
- Table 3 (SEN12MS-CR-TS, a suitable subset only, not like-for-like): VPint2 PSNR 30.38, SSIM 0.928 vs UnCRtainTS 27.84, 0.866 on the full set.
- **Reference age (Fig. 7a):** VPint2 degrades mildly from 1 week to 6 months; temporal replacement is best at 1 week (MAE 140.97) but degrades fast.
- **Evaluation finding:** replacement with a 1-week reference (what near-date "ground truth" datasets implicitly assume) has MAE 141, comparable to the methods' own errors (196–292 across ages) — "the magnitude of the aleatoric uncertainty of the dataset would be comparable to the magnitude of the performance of cloud removal methods themselves" (p. 181).
- Oracle ensembles (Table 4): complementarity is at pixel, not patch, level.

## 4. Stated limitations
- Needs at least one clear pixel; "less suitable for cloud removal in smaller patches" (p. 172).
- Temporal heterogeneity and moved object borders inside the cloud cause wrong-colour gradients at object borders (p. 172–173).
- Advantage shrinks at very high cover; on par with the best alternative near 100% (p. 181).
- Hue differences on L1C (atmosphere differs between dates); designed for the same data type in target and reference (p. 176, 180).

## 5. How to apply to our pipeline
- **As a fill for the opaque part (t < T_MIN in `sn8_refhaze` / `sn8_cloudsym`): do not use for flood scoring.** VPint2 rebuilds the hidden after-pixels with the **before** image's structure, scaled to the surrounding **after** values. A flooded road that is entirely under cloud gets the dry road's shape back; the flood shows only if it reaches the clear edge, and then spreads by pre-flood structure (the "between-object relationship changed" failure the authors describe). It is better than copying the before pixels, but it is still the no-change assumption on structure. Keep "not observed" for opaque cloud in the scoring path; at most, a VPint2 fill could be a labelled display product.
- **Protocol to copy (the most useful part):**
  1. **Mask transfer** = evidence 05 / E3 plan: paste real cloud shapes (HRC_WHU masks, or our own dark-rise gates from other tiles) onto clear after-tiles with known flooded roads; truth is exact. VPint2 shows this beats near-date truth for reliability.
  2. **Paired one-sided Wilcoxon signed-rank tests per stratum**, as here, alongside our McNemar tests on road calls; report per land cover (urban vs vegetated behaved differently).
  3. **Masks: favour recall and buffer** before any fill or correction — supports `DARKREF_GATE_MARGIN_PX` and the 20 m fade in `sn8_refhaze`/`sn8_cloudedge`; the authors used 5 one-pixel dilation passes at 10 m (= 50 m).
- **Identity-priority idea for the tone curve / ring:** where `sn8_cloudedge` fades the correction past the gate, weight neighbour evidence by before-image similarity (γ ≈ 1 → same object) so a correction does not bleed across a road edge. Cheap to test as a ring arm.
- **Numerical caution for grey uint8:** γ = f/f' explodes on 0-valued or very dark pixels (shadows, water). Use an offset (f+1)/(f'+1) or work in float with a floor if ever implemented.
- **Feasibility:** fully feasible on RGB/grey 0.5 m with our one clear before date; no training, no SAR, no NIR. Code is public (Python). 

## 6. Key quotes
- "This method leverages previously sensed cloud-free images to represent the spatial structure of a region, which is then used to propagate up-to-date information from non-cloudy pixels to cloudy ones." (abstract, p. 168)
- "Our findings furthermore support a cloud removal evaluation approach founded on the transfer of cloud masks over the use of cloud-free previous acquisitions as ground truth." (abstract, p. 168)
- "recall should be prioritised over precision for cloud masks" (p. 175)
- "the magnitude of the aleotoric uncertainty of the dataset would be comparable to the magnitude of the performance of cloud removal methods themselves" (p. 181)
