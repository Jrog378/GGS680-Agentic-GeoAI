# Coder handoff: Heidinger & Straka (2020), NOAA Enterprise Cloud Mask (ECM) ATBD v1.2 (agency document)

- **Citation:** Heidinger, A., & Straka, W. (2020). *NOAA Enterprise Cloud Mask, Algorithm Theoretical Basis Document*,
  v1.2, 1 Oct 2020. NOAA/NESDIS/STAR and CIMSS. No DOI.
  https://www.goes-r.gov/s3/2025-12/ATBD_Enterprise_Cloud_Mask_v1.2_2020_10_01.pdf
- **PDF with summary:** `/Users/jusrogers/Masters/papers/heidinger2020_noaa_enterprise_cloud_mask_ATBD-summary.pdf`
- **Validation:** real PDF, 73 pages (pdfinfo; Read confirms 74 with the summary). Title page shows the NOAA NESDIS STAR
  ATBD, Heidinger and Straka, v1.2, 1 Oct 2020 (PDF created 6 Nov 2020). Complete: limitations, references and
  Appendices A–B present. Note: the table of contents numbers sections 1–12 while the body headings run 1–15 (e.g. TOC
  5.5 = body 7.5); page numbers below are PDF pages, which equal the printed page numbers.
- **Pages read:** 1–73 (all; numeric tables read; Appendix A equations not transcribed).
- **Supports ranked fixes (evidence 21):** #2 (calibrated probability + explicit uncertainty + a rule for cut-offs), #11
  (GOES tile prior/cross-check, and why it is weak for thin haze), #3 (state the rule for each constant).

## Algorithm (§7, pp. 25–40)
1. **Metrics per pixel:** reflectances, reflectance ratios (e.g. ref0.86/ref0.65), brightness-temperature differences,
   3 × 3 standard deviations, opaque-cloud height/temperature (from 11 µm + NWP + RTM), and clear-sky expected values.
   Naming in Table 5 (p. 35).
2. **Classifiers:** 1-D/2-D/3-D histograms (look-up tables) of each metric, per surface type (7 types: deep ocean,
   shallow water, land, snow, Arctic, Antarctic, desert; §7.7).
3. **Training truth:** CALIOP 5 km / 1 km cloud layer products within ±5 min. "CALIOP cloud phases were reclassified as
   clear if the CALIOP column optical depth was below a threshold. Currently, this threshold is set to 0.1" (p. 50).
   At least 1 year per sensor; train/test split by whole days, training 3× larger (p. 50).
4. **Naive Bayes (p. 28):** `R = Π_i C_no,i / C_yes,i` (class-conditional frequency ratio per bin). The posterior is
   printed as a garbled small equation; the standard form consistent with the text is `P_cloud = 1 / (1 + R·(1 − P_r)/P_r)`,
   with P_r the prior (our reading). Clear, water and ice probabilities are renormalised to sum to 1;
   `P_cloud = 1 − P_clear`.
5. **Prior (§7.6):** monthly 1° × 1° CALIPSO L3 cloud fraction, 2007–2015, gap-filled and smoothed.
6. **Classifier selection (§7.9):** greedy forward selection per surface type until gains are negligible ("assumed to
   reduce the impact of classifier correlation"). VIIRS LUT: 18 classifiers (Table 6).
7. **Outputs (§7.4–7.5, §8):**
   - Binary: cloudy if `P_cloud > 0.5`.
   - Uncertainty: `P_cloud` if called clear, `1 − P_cloud` if called cloudy (p. 29).
   - 4-level: confidently clear `[0, PCC)`, probably clear `[PCC, 0.5)`, probably cloudy `[0.5, PCD)`, cloudy `[PCD, 1]`.
     Earlier "PCC was set to 0.1 and Pcd was set to 0.9. These fixed thresholds resulted in varying amounts of
     confidently-clear for each surface type" (p. 29). Now "the ECM applies an approach that sets the PCC values to ensure
     that each surface type on average yields 25% of the binary-clear pixels as confidently clear"; PCD stays 0.9 (p. 30).
   - Cloud probability "is considered the primary output"; "users are encouraged to use this output for their
     applications by choosing appropriate thresholds" (pp. 15, 44).
   - Uniformity tests: RUT = 3 × 3 std of 0.65 µm reflectance > threshold (per surface; land max(0.5, index × clear-sky
     reflectance)); TUT = 3 × 3 std of 11 µm BT, threshold raised by 3·Γ·Z_std (Γ = 7 K/km). Optional filters that move
     clear → probably clear (§7.12, §8.4).
8. **Metrics (§10.2):** ACC = (TP + TN)/(P + N) is reported; BWACC is used for optimisation; WACC and BCE are monitored.
   (The printed BACC formula "(TP + TN)/2" is a typo for (TPR + TNR)/2.)

## Performance (pp. 49–60)
- Spec (Table 1, p. 15): global ACC 87% for COD > 0.4; snow-free land, day 90%.
- ABI/AHI (Tables 11–12): land, all times: ACC 0.93 (COD > 0.4); BACC 0.88 with no COD filter. Day land ACC 0.93,
  BACC 0.88. Truth vs ECM cloud fraction on land 0.69 vs 0.66: ECM "would miss more cloud than it falsely detects"
  (p. 52, stated for VIIRS).
- Hit rate > 90% for COD > 1. At COD 0.01: 30% (VIIRS), 45% (ABI/AHI), 35% (MODIS). 50% sensitivity at COD 0.1, 0.06 and
  0.03 respectively (pp. 57–59).
- VIIRS vs ABI binary agreement 87.85% for one global day (Table 16).
- Limitations: depends on NWP, RTM, snow maps and clear-sky reflectance (§12.1); striping affects the uniformity tests.
  "Experience has shown that there are superior ML methods"; NB is to be replaced by NN/AI (p. 63).

## How to apply to our pipeline
- **Fix 2 (`sn8_cloudspot.py` → `sn8_cloudsym.py`):** copy the *output contract*:
  1. A per-pixel `p_cloud` (calibrated; see the Guo 2017 handoff).
  2. `uncertainty = p if clear else 1 − p`.
  3. A 4-level mask whose confidently-clear cut is set by a **stated rule**, e.g. per tile or land-cover class, "the cut
     that keeps X% of binary-clear pixels as confidently clear", or a cut chosen from the risk–coverage curve.
  4. Report ACC and balanced accuracy (and BCE) on held-out folds.
  This replaces the unexplained t < 0.2.
- **Per-class cut-offs:** ECM's per-surface PCC is precedent for separate thresholds over water/flooded vs dry land vs
  urban, since our spotter's error differs by surface. Fit them on development folds only.
- **Uniformity filter (optional):** a 3 × 3 (scaled to ground size) reflectance-std test to downgrade "clear" to "probably
  clear" in heterogeneous areas. This is the RUT idea; at 0.5 m, urban texture will trigger it, so scale the window and
  threshold per class.
- **Fix 11 (GOES tile prior):** ABI ACM gives a 4-level mask (and per the ATBD a probability; check the distributed L2
  variables). Each 2 km IR pixel (0.5 km visible sub-pixels; "sixteen corresponding pixels", p. 42) covers about
  4,000 × 4,000 of our pixels. Training treated COD < 0.1 as clear, and the 50% hit rate is near COD 0.06. So GOES cannot
  see the haze that affects our texture; use it only as a tile-level cross-check.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** the algorithm itself is infeasible: it needs
  IR, NWP, RTM and CALIOP training. The output design, the per-class threshold rule and the metrics are fully feasible.
