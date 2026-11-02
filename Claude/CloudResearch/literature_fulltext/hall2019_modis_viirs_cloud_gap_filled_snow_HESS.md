# Coder handoff: Hall, Riggs, DiGirolamo & Román (2019), Evaluation of MODIS and VIIRS cloud-gap-filled snow-cover products

- **Citation:** Hall, D. K., Riggs, G. A., DiGirolamo, N. E., & Román, M. O. (2019). *Hydrology and Earth System Sciences* 23(12), 5227–5241. https://doi.org/10.5194/hess-23-5227-2019
- **PDF:** `/Users/jusrogers/Masters/papers/hall2019_modis_viirs_cloud_gap_filled_snow_HESS-summary.pdf` (page 1 = AI summary)
- **Source:** open access, Copernicus (CC BY 4.0): https://hess.copernicus.org/articles/23/5227/2019/hess-23-5227-2019.pdf
- **Validation:** `file` = PDF; 6.1 MB; 15 pages (Read tool error message states 15; pdfinfo 15) = published range 5227–5241; title/4 authors/DOI match Crossref; "5 Discussion and conclusion" and references present. PASS.
- **Read:** pp. 5227–5239 in full (all text, figure captions, data availability); references pp. 5239–5241 skimmed.
- **Type:** product description + preliminary evaluation, not a new method.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§3, p. 5231–5232)
Inputs: today's daily snow map M*D10A1 (or VNP10A1) and yesterday's CGF map M*D10A1F with its CPC array.
```
for each pixel:
    if today == cloud (or missing day / orbit gap / missing scan line):
        CGF_today = CGF_yesterday          # most recent cloud-free value
        CPC_today = CPC_yesterday + 1
    else:
        CGF_today = today
        CPC_today = 0
start of series: CGF = daily map, CPC = 0 for clear, 1 for cloud
series restart: first day of the mission, then every 1 October (water year)
```
- "If the CPC for the current day is greater than or equal to one, it represents the count of days since the last 'non-cloud' observation" (p. 5232).
- Chosen for NASA "because of its ease-of-use, effectiveness, and because it relies on data from only one sensor at a time" (p. 5230).
- A missing day of input "is processed as if it were completely cloud-obscured" (p. 5232).

## 2. Inputs / outputs
- MODIS 500 m (Terra 10:30, Aqua 13:30 local), VIIRS 375 m (S-NPP 13:30); snow decision stored as NDSI, not fractional snow cover (C6/C6.1).
- Output: daily CGF NDSI snow map + CPC QA layer ("age of the observation in each pixel"); "no decision" pixels flagged (red in Figs. 7, 11).

## 3. Quantitative results we could compare to
- Spin-up from 4 Feb 2012: MODIS map nearly cloud-free by ~Day 8 (8.0% cloud); VIIRS by Day 5 (6.7%) (Fig. 3, p. 5232). Example day: MOD10A1 65.8% cloud vs VNP10A1 60.6%; after CGF 15.2% vs 16.6% snow (p. 5230–5231).
- MODIS vs VIIRS, 1 Feb–30 Apr 2012, 2,487,610 km²: VIIRS shows on average 11,070 km² (~0.45%) more snow per day (p. 5235).
- Terra vs Aqua CGF % snow: R = 1.0, mean bias 1.69 (Wind River, 22,171 km²); R = 0.96, bias 1.13 (Sierra Nevada, 109,575 km²); fully cloud-free by ~Day 20 and ~Day 10 respectively (p. 5235–5236).
- No error-vs-age curve is given; validation is by examples (NOAA snow depth in Utah, Sentinel-2A in Montana), explicitly "not validation" for the Sentinel comparison (p. 5233).

## 4. Stated limitations
- "Cloud-gap-filled snow-cover products … have all of the uncertainties of the original products that contain clouds, as well as additional uncertainties that are related to cloud-gap filling, such as the age of the snow observation" (p. 5238).
- "For each pixel, the uncertainty of the observation increases with time since the last clear view" (p. 5232) — stated, not measured.
- Uncertainty greater where clouds are persistent (NE US) than where gaps are frequent (Sierra Nevada) (p. 5238).
- Aqua cloud mask (no restored band 6) leaves many "no decision" pixels; Terra and VIIRS recommended.
- Snow can change within a day (melt), and clouds move between overpasses (p. 5231).

## 5. How to apply to our pipeline
- **We must not copy this fill.** Filling the post-storm date from the pre-storm date is CPC = "one event old" and assumes no change; the flood is the change. Do not let filled/abstained pixels vote "flooded".
- **Copy the provenance layer.** Add a per-pixel uint8 provenance array to the outputs of `sn8_refhaze.dark_reference_dehaze` and `sn8_cloudsym.either_date_dehaze`, mirroring CPC:
  - 0 = observed clear (outside gate and fade);
  - 1 = corrected (inside gate/fade, t ≥ `T_MIN`), store t alongside as the confidence;
  - 2 = not observed (t < `T_MIN`, abstained) — the analogue of a cloudy pixel with no fill;
  - (optional) 3 = before-date cloudy (from `cloud_dates` label 2/3).
  Then the road/flood scorer reads a user-set acceptance level (e.g. accept {0}, or {0, 1 with t ≥ x}), the CPC "how far back" choice applied to correction strength. `road_handling` / `either_date_handling` already produce assess/correct/cannot-assess per road; the pixel layer makes that decision reproducible and lets risk–coverage curves be drawn.
- **"No decision" class:** the paper keeps a separate no-decision flag rather than forcing snow/no-snow; same as our abstain.
- **Feasibility:** trivial with our data; it is bookkeeping, no extra imagery needed.

## 6. Key quotes
- "The CGF daily snow map is created by replacing cloud observations in the current day M*D10A1 with the most recent previous cloud-free observation" (p. 5231).
- "A user can decide how far back in time they would like to use an observation, and can easily develop a unique CGF map, utilizing the CPC information that is most appropriate for their application" (p. 5232).
- "For each pixel, the uncertainty of the observation increases with time since the last clear view" (p. 5232).
