# Coder handoff: Weir et al. 2019, SpaceNet MVOI (ICCV 2019)

**Citation:** Weir, N., Lindenbaum, D., Bastidas, A., Van Etten, A., McPherson, S., Shermeyer, J., Kumar, V., & Tang, H.
(2019). SpaceNet MVOI: A multi-view overhead imagery dataset. *ICCV 2019*, 992–1001. doi:10.1109/ICCV.2019.00108
**Copy:** CVF Open Access PDF, 10 pp = 992–1001. PDF: `/Users/jusrogers/Masters/papers/weir2019_spacenet_mvoi_multiview_overhead_ICCV-summary.pdf`
(page 1 = AI summary). **Read:** pp. 1–10 (supplement not read). Affiliations: In-Q-Tel CosmiQ Works, Accenture Federal,
Intel AI Lab (imagery from Maxar; **no Maxar co-authors**). Dataset licence stated in paper: CC BY-SA 4.0 (p. 2).
Claude, 2026-10-29.

## Data facts (pp. 2–5)
- WorldView-2, Atlanta, 22 Dec 2009, one pass in ~5 min, 27 looks, 7.8°–54° off-nadir, azimuth 17°–182.8°; sign =
  look direction (negative south-facing). Same 665 km².
- Pan-sharpened RGB(+NIR), 16-bit truncated at 3000 → 8-bit; resampled to a common 0.5 m grid (native 0.46–1.67 m);
  900×900 px tiles (450 m). Also PAN and 8-band MS.
- Footprints labelled on the 7.8° image, "geospatially accurate", shared by all looks — roofs are displaced off-nadir.
- Split 80/20 by location (all looks of a location in one split).

## Results (Tables 3–6)
- TernausNet (all-angle training) F1: NADIR 0.62, OFF 0.43, VOFF 0.22. Mask R-CNN seg 0.47/0.34/0.07; YOLT
  0.49/0.37/0.20.
- Resolution control: all views at 1.67 m → F1 0.41 vs 0.43 (Table 4): view effects dominate.
- Train NADIR → test OFF 0.32 vs train OFF 0.44. Generalisation G (F1_unseen / F1_matched): TernausNet ~0.42,
  Mask R-CNN ~0.78.
- South-facing (shadowed) looks worse; image-translation off-nadir→nadir "failed" (anecdotal, p. 8).

## How to apply to our pipeline / Ida test
- **Revision 1 item 5 (road strips first; buildings/trees separately; record off-nadir angle):** MVOI is the citation
  (ICCV) that look angle alone changes appearance, independent of resolution. Keep road strips as primary region.
- **New measurable noise floor (feasible, cheap; descriptive):** download 2–3 MVOI looks of the same tiles (e.g. 7.8°,
  ~30°, ~50°; PAN or RGB→grey, already 0.5 m), co-register with `sn8_coreg`, and compute the same DINOv2 patch-feature
  cosine distance used in outcome 1 on (a) road pixels (OSM or SpaceNet-3-style road masks; MVOI has only building
  labels, so derive roads from OSM), (b) building footprint pixels, (c) other. This gives "distance due to view angle
  only" on unchanged ground, per region type. Report it beside the Ida clear-ground guard. Dataset ~7 GB per look
  (evidence 19 tested the S3 listing) — **new big download: ask Justin first**.
- **Record the Ida satellite look angle** (catalog 10300100C46F5900 metadata: off-nadir, target azimuth) and the sun
  azimuth; MVOI shows direction (north/south-facing) matters, not just magnitude.
- **Feasibility:** good for the noise-floor experiment (grey 0.5 m, unchanged ground by construction); no training.
