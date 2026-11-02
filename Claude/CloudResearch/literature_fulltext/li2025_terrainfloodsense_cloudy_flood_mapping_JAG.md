# Coder handoff: Li, Xu & Weng (2025), TerrainFloodSense, terrain + water-occurrence fusion to fill cloud gaps in flood maps

- **Citation:** Li, Z., Xu, S., & Weng, Q. (2025). TerrainFloodSense: Improving seamless flood mapping with cloudy
  satellite imagery via water occurrence and terrain data fusion. *International Journal of Applied Earth Observation
  and Geoinformation* 144, 104855. https://doi.org/10.1016/j.jag.2025.104855
- **Copy read:** the published open-access version (Elsevier typeset, CC BY-NC-ND) from the PolyU Institutional Research
  Archive, https://ira.lib.polyu.edu.hk/bitstream/10397/116859/1/1-s2.0-S1569843225005023-main.pdf. It has 13 pages.
  Page numbers below are the journal's. The supplementary file (Fig. A1, Table A1) was not read.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/li2025_terrainfloodsense_cloudy_flood_mapping_JAG-summary.pdf`
- **Validation:** real PDF (10.1 MB, 13 pages by the Read tool and pdfinfo). Title, authors, volume and article number
  match Crossref. The full Crossref title ends "...terrain data fusion"; our evidence-19 reference drops "data fusion".
  Conclusions, data availability and references are present. PASS.
- **Pages read:** 1–13 (all); Eqs. 3–9 checked on the rendered p. 5.
- **Code:** https://github.com/RCAIG/TerrainFloodSense (p. 1). Data availability: "Data will be made available on
  request" (p. 11). No dataset release.
- **Supports (evidence 19):** the Q4 strand (non-image geospatial priors for flood under cloud) and plan item 8 (a
  terrain-based reference with an "uncertain" band and structure flags). Plan item 9 is supported indirectly: cloud gaps
  bias composed flood products (Fig. 5).

## Algorithm (pp. 3–6)
1. **Inputs, all 30 m:** HLS (Landsat-8/9 + Sentinel-2), GSW occurrence (Pekel 2016; 0–100, 1984–2021), ALOS AW3D30 DSM,
   and global 30 m HAND (Donchyts 2016).
2. **Terrain inundation index** (Eq. 2): `I = α·norm(DSM) + (1−α)·norm(HAND)`. `norm` is min–max normalisation, and
   α = 0.3 was chosen by a 0–1 sweep in steps of 0.1 (best OA). HAND (Eq. 1) = `H_pixel − H_drainage`. α = 0 and α = 1
   (one terrain layer only) were both "suboptimal" (p. 4).
3. **Bayesian fusion → fused water occurrence (FWO)** (Eqs. 3–8). With `Pwo` = GSW occurrence scaled to [0, 1], for each
   unique index value h:
   - `P(terrain=h | inundation) = Σ Pwo(terrain=h) / Σ Pwo` (Eq. 4)
   - `P(inundation) = Σ Pwo / (Σ Pwo + Σ(1−Pwo))` (Eq. 6)
   - `P(terrain=h) = [Σ Pwo(h) + Σ(1−Pwo(h))] / [Σ Pwo + Σ(1−Pwo)]` (Eq. 7)
   - Simplified (Eq. 8): `P_fwo(h) = Σ Pwo(h) / [Σ Pwo(h) + Σ(1−Pwo(h))]`. This is just the **mean occurrence of all
     pixels sharing index value h**, stored as a lookup table.
4. **Blend** (Eq. 9): mean–variance normalise FWO to [0, 1], then `P_final = α·P_fwo + (1−α)·Pwo` with **α = 0.5**. This
   is a *different* α from Eq. 2; the paper reuses the symbol.
5. **Restrict and tidy:** fuse **only where GSW occurrence < 5** (elsewhere keep GSW). Histogram-match FWO to GSW, then
   quantise to **500 levels** (GSW has 100). The result is the enhanced water occurrence (EWO).
6. **Initial water map:** a fine-tuned Prithvi-100M-Sen1Floods11 on HLS. Clouds and shadows come from the HLS QA band.
7. **Fill cloud pixels** (Eq. 10): `W(x,y) = 1 if P_ewo(x,y) > T else 0`.
   - T is set per pixel in a local window that grows until there are enough valid neighbours.
   - T comes from a "ratio curve" of occurrence-value pixel counts in cloud-free vs inundated areas (the "submaximal
     stability" assumption of Li et al. 2024a, ISPRS 216:185). It is smoothed by a moving average because EWO adds terrain
     noise.
   - A global threshold is the fallback. The exact window sizes and the ratio-curve formula are **not** given here;
     they are in Li et al. 2024a and the code.
8. **Flood map:** subtract the pre-flood maximum water extent from pre-flood HLS. Classes: floodwater, pre-flood water,
   non-water.

## Evaluation and results (pp. 6–8, Table 1)
- **Reference:** six cloud-free HLS patches of 1000 × 1000 px (900 km²), flood and non-flood dates, over Assam 2022,
  Sindh 2022 and Rio Grande do Sul 2023. They were "manually labeled with high confidence through visual interpretation
  ... assisted by high-resolution satellite imagery (e.g., Sentinel-2 and PlanetScope when available), and validated
  using local flood reports and expert hydrological knowledge" (p. 6).
- **Simulated clouds:** real HLS QA cloud masks at low (<30%), medium (30–60%) and high (>60%) cover, four per level,
  giving 72 experiment groups.
- **Scenarios:** "extreme flooding" pixels have GSW < 5, including pixels never seen wet. "Regular inundation" is the
  rest.
- **Table 1 (OA / Precision / Recall / mIoU / F1):**
  - Overall: Zhao & Gao 2018 89.00/70.39/90.58/0.656/0.792; Ours-WO 93.07/83.54/87.24/0.744/0.854; Ours-EWO
    94.31/87.21/88.36/0.782/0.878.
  - Extreme: 80.78/75.86/80.32/0.640/0.780; 86.69/91.20/75.99/0.708/0.829; 89.64/95.42/79.42/0.765/0.867.
  - Regular: 92.88/70.16/99.93/0.701/0.824; 95.96/81.81/97.51/0.801/0.890; 96.44/84.46/96.51/0.820/0.901.
- The headline "+2.95 to +8.86 % OA, +0.038 to +0.087 F1" is the **extreme-flooding scenario only**, against the two
  baselines. Overall gains are +1.24 OA / +0.024 F1 vs WO and +5.31 / +0.086 vs Zhao & Gao (p. 7). No significance test
  is reported.
- **Large-area case** (Rio Grande do Sul, full HLS tile, 2023-09-29 in the Fig. 4 caption; the text says September 9):
  **visual only**, against a same-day 3 m PlanetScope image about an hour apart, and its NDVI. "large-area quantitative
  validation remains challenging due to the absence of consistent reference data" (p. 8).

## Key quotes and limits
- Zhao & Gao's higher recall comes from "their global thresholding strategy, which tends to over-include uncertain
  pixels" (p. 7).
- "the precision of the generated EWO data is subject to the quality of the DSM data used" (p. 9). The failure case is
  Xinxiang, Henan 2021 (Fig. 6), where observed inundation had no matching DSM relief.
- "exceptions exist ... such as areas with above-ground rivers or artificial structures" (p. 10).
- The method has no hydrodynamics. It "primarily considers statistical inundation probability priors" (pp. 9–10).
- Cloud gaps cause "significant spatial inconsistencies and underestimation errors" in composed flood-duration maps
  (Fig. 5, p. 10).

## How to apply to our pipeline
- **Not a cloud/haze module.** The method does not restore pixels under haze. It predicts water under cloud from priors.
  It does not belong in `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`, `sn8_texture.py` or `sn8_glcm.py`.
- **Validation and label support.** It can be a terrain prior beside the flood/road labels:
  - Build an index from the 3DEP 1 m DEM (bare earth, *not* a DSM) and a HAND layer at the road scale. Bin the index
    (e.g. 100–500 quantile bins).
  - Per bin, compute the mean of a historical water layer (GSW is 30 m, so resample it) to get an Eq. 8 lookup table.
  - Use the table only to tag cloudy road segments as likely-wet / uncertain / likely-dry, in a separate report column.
  - Do not train or score on it (the "published labels, unmodified" rule). Do not overwrite SpaceNet 8 labels.
- **Design ideas worth copying:**
  - (a) Apply the prior only where history is uninformative (GSW < 5).
  - (b) Use local adaptive thresholds, not one global threshold. Their global baseline inflated recall and lost
    precision.
  - (c) Split metrics by "rarely-wet" vs "regular" pixels, because overall numbers hide the hard cases.
- **Feasibility with 0.5 m RGB uint8, one clear pre-storm date, no NIR/SWIR/SAR:**
  - The prior itself needs no imagery: DEM, HAND and GSW are all free.
  - Their water extraction (Prithvi on 6-band HLS) and the HLS QA cloud mask cannot transfer. Our cloud mask and water
    calls must come from our own RGB pipeline.
  - Scale mismatch: GSW is 30 m and roads are about 10 m wide, so the prior is coarse for single-road calls.
  - Louisiana roads on embankments, levees and bridges are the "artificial structures" the authors name as failures.
    Flag them, as in evidence-19 plan item 8.
