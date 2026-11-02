# Coder handoff: Li, Shen, Weng, Zhang, Dou & Zhang (2022), cloud and cloud-shadow detection review

- **Citation:** Li, Z., Shen, H., Weng, Q., Zhang, Y., Dou, P., & Zhang, L. (2022). Cloud and cloud shadow detection for
  optical satellite imagery: Features, algorithms, validation, and prospects. *ISPRS J. Photogramm. Remote Sens.* 188,
  89–108. https://doi.org/10.1016/j.isprsjprs.2022.03.020
- **Copy read:** open author copy (publisher layout), https://sendimage.whu.edu.cn/wp-content/uploads/2022-Cloud-and-cloud-shadow-detection-for-optical-satellite-imagery-Features-algorithms-validation-and-prospects.pdf
- **PDF with summary:** `/Users/jusrogers/Masters/papers/li2022_cloud_shadow_detection_review_ISPRS-summary.pdf`
- **Validation:** PDF, 20 pages = pp. 89–108; title, authors and DOI match Crossref; conclusions, appendices and
  references are present.
- **Pages read:** 89–105 (all text, tables, Appendices A–B), in full. References (pp. 105–108) were checked for
  completeness only.
- **Supports ranked fixes (evidence 21):** #8 (taxonomy), #1 (spectral-spatial features for VHR), #11 and #12 (limits of
  auxiliary data), #4 (validation reference types). It is a review with no new experiments, so it supplies framing, not
  numbers.

## What to take for code: no algorithm, but these design rules
1. **Taxonomy (p. 90, Fig. 1; p. 100):**
   - Features: spectral; spectral-spatial; spectral-temporal; spectral-spatial–temporal; multi-source. They come from
     mono-temporal, multi-temporal or multi-source data.
   - Algorithms: physical-rule; temporal-change; variational-model; machine-learning (deep learning included).
   - Processing: "dehazing/thin cloud removal, cloud detection, and thick cloud removal, which are usually performed
     independently or partially coupled" (p. 100). "the commonly called cloud detection usually does not include the
     detection of thin clouds like haze" (p. 100).
2. **Cloud cues, Table 1 (p. 92):** spectral, "High brightness, White color, Low temperature, High elevation"; spatial,
   "Spatially smoothing, Weak edge, Relatively low complexity in shape, Sparsity in distribution"; temporal, "A sharp
   increase in reflectance". With RGB only, we can use brightness, whiteness, smoothness, weak edges, shape and the
   temporal increase.
3. **Generic rule forms:**
   - Physical rule, Eq. 1 (p. 96): `R > t1 and/or R < t2`.
   - Temporal change, Eq. 2 (p. 96): `(R − R*) > t1 and/or (R − R*) < t2`, with R* the cloud-free reference.
   - Variational, Eq. 3 (p. 97): `min λ1 J1(C) + λ2 J2(B) s.t. I = C + B, B ≥ 0`, with the cloud component C smooth and
     sparse and the clean series B low-rank.
   Our two-date gate in `sn8_cloudsym.py` is an instance of Eq. 2 with a single reference date.
4. **Multi-temporal caveat (p. 94):** such methods "usually outperform mono-temporal based methods" and alleviate "thin
   cloud omission and high-bright objects commission". But they "may generate errors in areas with rapid and significant
   land cover changes" and are "only suitable for areas with small or periodic land cover changes and images with a high
   temporal resolution". We have neither: one pre-storm date, and a flood.
5. **VHR with few bands (p. 96):** "For high-resolution images with insufficient spectral information, spectral,
   geometric, and textural features, usually need to be combined", e.g. MFC. Spatial features help "especially for images
   that only contain visible and near-infrared bands" (p. 93).
6. **Thresholds (p. 96):** physical rules "rely on empirical determination and parameter sensitivity analysis", with
   "difficulties in achieving parameter adaption and global optimality". This supports fix 2 (calibrated probability) and
   fix 3 (published sweeps).
7. **Known failure classes (p. 100):** thin cloud and "translucent clouds in the transition region between thick clouds
   and the clear sky surface"; "high bright surfaces, including snow/ice, built-up areas, and bright water bodies".
8. **Multi-source data (p. 94):** auxiliary data improve accuracy, "outperform mono-temporal methods", but "auxiliary data
   usually have low resolution, these methods are more suitable for low- and medium-resolution images".
9. **Validation (p. 99):** four reference types: manual labels, cloud mask products, collocated lidar/radar, and
   ground-based cameras. Product-based evaluation is "not very reliable and are susceptible to the accuracy of the
   reference cloud mask products". MOD35 is "considered a benchmark or standard reference cloud mask". Lidar cannot
   validate shadows.
10. **Physics + data (p. 100):** "the physical model such as atmospheric scattering law can also be used to stimulate
    [simulate] cloud samples" for training deep models.
11. **Datasets (Appendix B, pp. 102–105):** HRC_WHU, "150 globally distributed high-resolution images (0.5 m to 15 m
    resolution, three RGB channels)", is the only RGB VHR set listed. Also listed: AIR-CD (Gaofen-2, 4 m, 34 scenes) and
    WDCD (Gaofen-1/Ziyuan-3).

## How to apply to our pipeline
- **Methodology table (fix 8):** use items 1 and 3:
  - `sn8_cloudspot.py` = mono-temporal, spectral-spatial (+ DINOv2), machine learning.
  - `sn8_cloudsym.py` two-date gate = temporal-change (Eq. 2) with one reference date. It is outside the review's stated
    validity condition, so say so and show the invariant-pixel safeguard (fix 5).
  - `dehaze()` / dark-reference dehaze in `sn8_clouds.py` = dehazing/thin-cloud removal, a separate stage per the review.
  - "Cannot assess" = the thick-cloud stage, where we abstain rather than remove.
- **Features (fix 1):** add whiteness/colour and weak-edge/smoothness cues from Table 1 to `classical_cues()`; they are
  the RGB-feasible rows.
- **False-positive audit:** report "bright water bodies" and built-up areas separately; the review names both.
- **External weather (fixes 11–12):** item 8 supports keeping GOES/ERA5 as a tile-level prior or cross-check only.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** all framing is usable. Cirrus (1.38 µm),
  thermal and elevation tests are unavailable, so we lose the strongest physical cues, and the review's
  "spectral + geometric + texture" recipe is the relevant one.
