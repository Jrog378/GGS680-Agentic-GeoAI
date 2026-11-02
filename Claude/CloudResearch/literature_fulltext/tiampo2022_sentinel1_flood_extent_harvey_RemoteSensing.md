# Coder handoff: Tiampo et al. 2022, Sentinel-1 flood extent for Harvey (Remote Sensing 14(9), 2261)

**Citation:** Tiampo, K. F., Huang, L., Simmons, C., Woods, C., & Glasscoe, M. T. (2022). Detection of flood extent
using Sentinel-1A/B synthetic aperture radar: An application for Hurricane Harvey, Houston, TX. *Remote Sensing* 14(9),
2261. doi:10.3390/rs14092261. **Copy:** publisher version (CC BY 4.0) via NOAA Institutional Repository
(repository.library.noaa.gov/view/noaa/52029); MDPI blocks scripted access. 21 pp.
PDF: `/Users/jusrogers/Masters/papers/tiampo2022_sentinel1_flood_extent_harvey_RemoteSensing-summary.pdf` (page 1 = AI summary).
**Read:** pp. 1–21. Claude, 2026-10-29.

## What they did with the NOAA photos (the reason we read it)
- NOAA Remote Sensing Division imagery, Harvey, flown 27 Aug – 3 Sep 2017, 2,500–5,000 ft, Trimble DSS, GSD 35–50 cm,
  mosaicked and tiled (pp. 3–4; NGS metadata page cited).
- Section 2.1: "These data were used to identify flooded polygons for ground truthing of our results" (p. 4).
- **In the results, NOAA appears only as side-by-side pictures** for three sub-regions (Figs. 11–13), with the SAR
  maps (no GWM removed there since NOAA shows permanent + temporary water). Discussion: NOAA offers "a unique
  opportunity to assess the qualitative advantages" (p. 15); conclusions: "Although it is difficult to quantify …
  visual comparison with NOAA optical imagery suggests …" (p. 18). **No digitised polygons, no co-registration, no
  date matching, no NOAA-based score.**
- The only numbers (Table 1, Fig. 14, p. 15–16) use **Sentinel-2 NDWI (> 0)** from 30 Aug / 1 Sep as the reference
  over −96.25 to −95.20 E, 29.25 to 30.25 N:
  - Thresholding: P 0.79, R 0.55, F1 0.65; DeepLabv3+ (SAR): 0.38 / 0.27 / 0.31; DeepLabv3+ (VV/VH false RGB):
    0.40 / 0.42 / 0.41. No intervals or tests.
  - Authors acknowledge NDWI is 1–3 days later and water likely receded.

## Methods (for reference)
- S1 GRD 29 Aug 2017 (Path 34, Frames 90/95) → SNAP: orbit, border noise, calibration σ0, speckle filter, terrain
  correction; 10 m.
- Thresholding (after refs [37,38]): tile; bimodality if max normalised between-class variance > 0.65; per s×s
  sub-window threshold = local minimum between modes (or mode); tile threshold = mean; permanent water removed with the
  Global Surface Water map.
- False RGB: R = VH dB, G = VV dB, B = VH/VV; 99th-percentile clip; min–max to [0,1].
- DeepLabv3+ Xception65 (ImageNet), 535 hand-drawn polygons on the same image, ~10,000 tiles 90/10, 30k iterations,
  batch 8, lr 0.007 — trained and evaluated on the same scene (no independent test region).

## Findings relevant to roads
- Thresholding "misidentifies large roadways as flooded pixels, probably because they are wet, with similar backscatter
  properties to a flat water surface" (p. 13).

## How to apply to our pipeline / Ida test
- **Citation framing (pre-registration intro / slides):** do *not* say "following Tiampo et al. we use NOAA photos as
  ground truth". Say: NOAA ERI photos have been used as a **qualitative** visual reference for Harvey flood maps
  (Tiampo et al. 2022); no published quantitative, co-registered protocol exists, so our Ida test defines one
  (pre-registration steps 1–6 + Revision 1).
- **Data facts reusable for Ida:** NOAA ERI GSD 35–50 cm, low-altitude frames, mosaicked tiles, flight dates spanning
  days → our step 2 (choose flight per tile, report gap) is needed; Tiampo did not do it.
- **Wet-road caution for outcome 6 / label-gap count (Revision 1 item 8):** flat wet pavement can read as water; in
  NOAA RGB, wet asphalt is dark too. When counting "cloudy roads that look flooded in NOAA", require standing-water
  evidence (e.g. continuity with adjacent water, reflections, submerged kerbs) or report "dark/wet" separately.
- **Feasibility:** n/a for code (SAR); framing and protocol only.
