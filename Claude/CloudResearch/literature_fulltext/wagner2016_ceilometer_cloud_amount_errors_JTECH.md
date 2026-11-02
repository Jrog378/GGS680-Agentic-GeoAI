# Coder handoff: Wagner & Kleiss (2016), error characteristics of ceilometer-based (ASOS/METAR) cloud amount

- **Citation:** Wagner, T. J., & Kleiss, J. M. (2016). Error characteristics of ceilometer-based observations of cloud
  amount. *Journal of Atmospheric and Oceanic Technology* 33(7), 1557–1567. https://doi.org/10.1175/JTECH-D-15-0258.1
- **Copy read:** published AMS version from the NOAA Institutional Repository,
  http://repository.library.noaa.gov/view/noaa/69344/noaa_69344_DS1.pdf (11 pages, journal pagination 1557–1567;
  page numbers below are the journal's).
- **PDF with summary:** `/Users/jusrogers/Masters/papers/wagner2016_ceilometer_cloud_amount_errors_JTECH-summary.pdf`
- **Validation:** real PDF (1.0 MB), 11 pages by pdfinfo and Read, matching pp. 1557–1567 (Crossref: vol. 33, issue 7,
  pp. 1557–1567, authors Wagner, Kleiss); conclusions and references present. PASS (published version).
- **Pages read:** 1557–1567 (all); Table 1 and Figs. 6–8 viewed as images.
- **Supports ranked fixes (evidence 21):** #12 (METAR/ERA5 as context only, not a feature); limits #11's cross-check
  (a METAR "CLR" cannot confirm a GOES or spotter "clear").

## What was done
1. Site: ARM Southern Great Plains Central Facility, north-central Oklahoma (p. 1559). Instruments: Vaisala ceilometer
   (CEIL; bases to 7,700 m, 10 m resolution, 3 layers), total sky imager (TSI; daylight only), micropulse lidar (MPL;
   532 nm, bases to 20 km).
2. ASOS emulation: CEIL bases > 3,660 m (12 kft) set to clear (p. 1559). Sky cover = time average of binary cloud
   presence: samples every 30 s over 30 min, last 10 min double weighted (p. 1558). METAR bins: CLR ≤ 5%, FEW 5–25%,
   SCT 25–50%, BKN 50–87%, OVC > 87% (p. 1558). Observations valid at :55 past the hour.
3. CEIL vs TSI: Jan 2002–Dec 2012, 14:55–21:55 UTC, > 25,000 pairs; TSI sky cover within 50° of zenith (100° FOV),
   15-min average (p. 1560).
4. Point-sampling error: 20 synthetic ceilometers (3 × 3 px modal cloud flag from the TSI cloud-decision image every
   30 s, ASOS-averaged) vs TSI 15-min 100° FOV cover; spots within 35° of the sun and cases with MPL base > 3,660 m
   removed; data after 9 Aug 2006 (pp. 1561–1563). The northern inner spots 5–8 are used as the estimate (p. 1564).
5. High-cloud error: MPL "ceilometer-like" sky cover with all clouds vs. only bases ≤ 3,660 m, every hour
   (pp. 1564–1566).

## Results (only numbers stated in the paper)
- CEIL vs TSI: Pearson r 0.754; 82.6% same or adjacent bin; CEIL clear 51.3% vs TSI 39.3%; of CEIL-clear, 69.2%
  TSI-clear and 9.5% TSI-overcast; agreement on FEW/SCT/BKN only 27.0% (CEIL-based) / 28.1% (TSI-based) (pp. 1560–1561).
- Synthetic ceilometer vs TSI: RMSE 0.161 → 0.0860 after removals; same bin 75.1% → 86.5% (p. 1563).
- **Table 1 (p. 1564), RMSE of cloud fraction:**

  | ASOS bin | sampling error | high-cloud error | total |
  |---|---|---|---|
  | CLR (0–0.05) | 0.054 | 0.588 | 0.642 |
  | FEW (0.05–0.25) | 0.153 | 0.596 | 0.749 |
  | SCT (0.25–0.5) | 0.151 | 0.387 | 0.538 |
  | BKN (0.5–0.87) | 0.138 | 0.197 | 0.335 |
  | OVC (0.87–1) | 0.036 | 0.021 | 0.057 |
  | all | 0.086 | 0.505 | 0.591 |

- MPL height-restricted vs CEIL: same bin 71.6%, same/adjacent 85.2%; full-height MPL: 45.3% / 62.6%. "Clear by CEIL,
  overcast by MPL" 0.51% → 14.1% of all observations (p. 1565).
- When CEIL says clear: MPL sees some cloud in 47.3%, overcast in 22.8%; mean/median lowest base 6,683 / 7,361 m;
  53.9% of all MPL cloud bases are above 3,660 m (p. 1565).
- Monthly agreement minimum 38.3% (June), maximum 57.2% (October); lower agreement by day, with the hourly minimum
  near 15 UTC in Fig. 8b (pp. 1565–1566).

## Key quotes
- "observations of clear sky or few clouds are often in error as the instrument cannot detect the presence of
  upper-level clouds" (abstract, p. 1557)
- "the greatest error at the SGP site happening in the morning and summer, respectively" (abstract, p. 1557)
- "when an ASOS station records an overcast observation, one may have high confidence that such an observation
  accurately reflects the sky condition at the time. The same cannot be said for other observation values" (p. 1566)
- "the quantitative results apply only to the conditions at the SGP site" (p. 1566)

## Limitations
- One inland site (Oklahoma); no coastal or tropical-cyclone conditions. Numbers will not transfer to Louisiana.
- Errors are in sky-cover fraction over the hemisphere/zenith, not in any satellite footprint; nothing on haze or
  aerosol optical depth.
- The 3,660 m limit was the ASOS reporting limit described in 2016; any later ASOS changes were not checked here.

## How to apply to our pipeline
- **Context only; no code change** in `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`, `sn8_texture.py` or
  `sn8_glcm.py`.
- **Fix 12 (methods text):** when reporting KMSY (CLR at 15:53/16:53/17:53 UTC on 31 Aug 2021, per evidence 21), state
  that CLR means "no cloud base ≤ 12 kft over the ceilometer in the last 30 min", not "no cloud". At SGP, CLR reports
  hid some cloud 47.3% of the time, overcast 22.8%, with a cloud-fraction RMSE of 0.642.
- **Fix 11 cross-check:** never use a METAR CLR/FEW to veto a spotter or GOES "cloudy" tile; only OVC (or low BKN) is
  a confident METAR call. Do not use METAR as a training label or a feature.
- **Feasibility (RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR):** trivially feasible (a few rows of IEM
  CSV), but it carries no pixel or tile information for our scenes.
