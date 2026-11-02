# Coder handoff: Ebel, Xu, Schmitt & Zhu (2022), SEN12MS-CR-TS

- **Citation:** Ebel, P., Xu, Y., Schmitt, M., & Zhu, X. X. (2022). SEN12MS-CR-TS: A remote-sensing data set for
  multimodal multitemporal cloud removal. *IEEE TGRS* 60, 1–14. https://doi.org/10.1109/TGRS.2022.3146246
- **PDF:** `/Users/jusrogers/Masters/papers/ebel2022_sen12ms_cr_ts_multitemporal_cloud_removal_TGRS-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv preprint version, https://arxiv.org/pdf/2201.09613 (v1, 24 Jan 2022, header "IEEE TGRS, IN PRESS").
  15 pages vs the journal's 14 (preprint pagination, page 15 = last author biography). Page numbers below are the
  preprint's 1–15.
- **Validation:** `file` = PDF 1.5, 18.6 MB; Read tool 15 pages (pdfinfo 15); title/authors on p. 1 match Crossref
  (TGRS 60, pp. 1–14, DOI 10.1109/TGRS.2022.3146246); Discussion, Conclusion, Appendix A and 49 references present.
  PASS (preprint pagination noted).
- **Read:** pp. 1–15 in full; reference list (pp. 12–14) skimmed; pages 7 and 10 also read as images for the metric
  equations and Tables I–V.
- **Companion:** SEN12MS-CR (single date) is in `ebel2021_sen12ms_cr_multisensor_cloud_removal_TGRS.md`. The
  "real-trained beats synthetic-trained" result belongs to that paper, not this one (see claim check).
- **Prepared by:** Claude (AI), 2026-10-29.

This is a **data-set paper** with two demonstration networks. Neither network is usable by us (both need SAR and/or a
long Sentinel-2 series). What we can use is the masking and evaluation protocol, the baselines, and the stated failure
cases.

## 1. Data set construction (§II, pp. 2–4; App. A p. 12–13)
- 53 regions of interest (ROI), each > 4000 × 4000 px (~40 × 40 km); 40 train, 13 test; > 80,000 km² total. Sampled at
  random from SEN12MS-CR's ROI; test/train splits are compatible with SEN12MS-CR (no ROI of one's train split in the
  other's test split) (p. 2).
- Per ROI: 30 time intervals evenly spaced through 2018; per interval one full-scene Sentinel-1 (GRD, VV+VH) and one
  Sentinel-2 L1C (13 bands, TOA reflectance) scene, paired within 14 days (mean 2.61 ± 2.41 days, Fig. 12). Single-pass
  cells to minimise mosaicking. Google Earth Engine plus "a custom semi-automatic processing pipeline"; "Each acquired
  image is inspected and quality-controlled manually" (p. 2).
- "the data set is curated without excluding any interval of cloud coverage" (p. 2); explicit contrast with STGAN's
  data, which drops scenes > 30% cloud (p. 2).
- Preprocessing (§II-B, p. 4): all bands to 10 m; non-overlapping 256 × 256 patches (15,578 patch locations × 30 dates,
  p. 11); S1 through the Sentinel-1 toolbox (border/thermal noise removal, calibration, orthorectification), dB.
  ResNet inputs: VV clipped [−25, 0], VH [−32.5, 0], rescaled to [0, 2]; S2 clipped [0, 10000], scaled to [0, 5].
  Other networks: clip then scale to [0, 1]. Evaluation: everything remapped to [0, 1].
- Size ~2 TB (p. 2).

## 2. Cloud detection and mask (§II-C, p. 4) — what we asked for
- Detector: **s2cloudless** (Zupanc 2017, Sentinel Hub; ref. [19]), run "on-the-fly" per optical image, giving a
  **binary** mask m ∈ {0, 1} (1 = cloud). Accuracy "reported to be on par with the multi-temporal classifier MAJA",
  but single-date; chosen because it is "lightweight", not because it is best; a dedicated CNN detector is named as an
  alternative.
- **No threshold, dilation or shadow handling is stated in this paper.** The companion SEN12MS-CR paper (2021, p. 4)
  thresholds the s2cloudless probability at 0.5 and smooths with a Gaussian σ = 2 to get a soft map; CR-TS does not
  say whether it reuses that. Cloud shadow is not mentioned anywhere in CR-TS.
- Cloud-cover statistics are computed from these masks on full scenes: train mean 44% (± 42%), test 50% (± 42%),
  bimodal from clear to total occlusion (Figs. 4–5, pp. 4). Discussion (p. 11): coverage spans "semitransparent haze to
  thick and dense clouds" — i.e. haze and thin cloud are counted as cloud by the binary mask, no thin/thick class.

## 3. Methods (demonstration only; §III, pp. 4–7)
- **Sequence-to-point** (Fig. 7): n Siamese branches of the DSen2-CR ResNet (Meraner 2020), each doing single-date
  cloud removal on (S1, S2)_t, pre-trained on SEN12MS-CR; feature maps stacked in time; 3D convolutions; one 13-band
  output with tanh. Replaces STGAN's pairwise 2D concatenation.
- Loss (eqs. 1–3, p. 8): `L_all = λ_L1·‖S2 − Ŝ2‖₁ + λ_perc·‖VGG16(S2) − VGG16(Ŝ2)‖₂`, λ_L1 = 100, λ_perc = 1;
  the VGG16 is trained on SEN12MS land-cover classification (13 bands), not ImageNet.
- Training (p. 8): 10 epochs, 1 tuple per location per train ROI; **input patches filtered to 0–50% cloud**; target =
  the patch with minimum cloud cover in the year, "not necessarily temporally preceding or following the input
  patches"; first 25,000 steps with the ResNet branches frozen; Adam lr 2·10⁻⁴, β (0.5, 0.999), batch 1.
- **Sequence-to-sequence** (Fig. 8, Algorithm 1, pp. 6–7, 10): 3D U-Net (from video-inpainting internal learning),
  trained from scratch **on the one target series only**, input S1 (or Gaussian noise for the ablation), output a
  13-band series. Loss masked to clear pixels (eqs. 4–6, p. 10):
  `L_all = λ_L2·‖S2·(1−m) − Ŝ2·(1−m)‖₂ + λ_perc·‖VGG16(S2)·(1−m) − VGG16(Ŝ2)·(1−m)‖₂`, λ_L2 = 1, λ_perc = 0.01;
  20 passes × 100 iterations, batches of n = 5 adjacent dates, Adam lr 0.01; stops "before the network overfits to
  internalizing the cloudy pixels" (no stopping rule given beyond iteration count). Framed as a learned
  low-rank + sparse decomposition (clouds = sparse part) (p. 6).

## 4. Evaluation protocol (§IV-A/B, pp. 7–8, 10) — the part we can reuse
- Metrics (p. 7) on [0, 1] data, **C = 3**, H = W = 256: NRMSE = √(mean (x − y)²); PSNR = 20·log10(1/NRMSE);
  SSIM; SAM = arccos(Σxy / √(Σx²·Σy²)). (The printed SSIM denominator lacks the squares of the standard formula; treat
  it as standard SSIM [Wang 2004].)
- **NRMSE three ways** (p. 7): (1) all pixels; (2) **cloudy = "visible in neither of any input optical sample"**
  (reconstruction of missing information); (3) **clear = "visible in at least one input optical patch"**
  ("quantifying preservation of information"). Masks from s2cloudless.
- **Baselines** (p. 7): "least cloudy" (forward the least-cloudy input unchanged; measures task difficulty);
  "mosaicing" (per pixel: copy the single clear value, mean of several clear values, **0.5 if no clear date** — a
  neutral fill "to avoid any extreme values"); single-date ResNet; STGAN.
- Test inputs span 0–100% cloud (p. 8). Table V bins by cloud cover with **all n inputs sampled from the same bin**.
- Sequence-to-sequence test (p. 10) is **simulated**: target S2_t = least-cloudy date; source S2_s = most-cloudy date;
  cloudy pixels of S2_s (mask m) are **alpha-blended** onto S2_t (copy-paste, after Rafique et al. 2019, ref. [3]);
  the prediction is scored against the original S2_t.

## 5. Quantitative results (Tables I–VI, pp. 9–11)
| Table | Setting | Numbers |
|---|---|---|
| I (seq2point, n = 3) | least cloudy / mosaicing / ResNet / STGAN / ours | NRMSE all 0.079 / 0.062 / 0.060 / 0.057 / **0.051**; NRMSE cloudy 0.082 / 0.064 / 0.062 / 0.059 / **0.052**; NRMSE clear **0.031** / 0.036 / 0.040 / 0.050 / 0.040; PSNR — / **31.68** / 26.04 / 25.42 / 26.68; SSIM 0.815 / 0.811 / 0.810 / 0.818 / **0.836**; SAM 0.213 / 0.250 / 0.212 / 0.219 / **0.186** |
| II | no S1 vs with S1 | NRMSE all 0.054 → 0.051; clear 0.054 → 0.040; PSNR 25.35 → 26.68 |
| III | no perceptual vs with | 0.052 → 0.051; PSNR 26.66 → 26.68 (tiny; SAM worse with it, 0.180 → 0.186) |
| IV | n = 3 / 4 / 5 | NRMSE all 0.051 / 0.049 / 0.048; PSNR 26.68 / 27.10 / 27.07 |
| V | by cloud cover, n = 3 | PSNR 28.59 (0–10%) → 24.79 (90–100%); SSIM 0.870 → 0.786; NRMSE all 0.041 → 0.063; not monotonic |
| VI (seq2seq, simulated) | RPCP / NMFISL / PNMF / MNMF / OSTD / ours no S1 / ours S1 | NRMSE 0.403 / 0.312 / 0.317 / 0.361 / 0.303 / 0.298 / **0.274**; PSNR 7.9–11.6 dB; SSIM 0.264–0.512 |
- Note the trivial baselines: **mosaicing has the best PSNR of all (31.68)** and **least-cloudy keeps clear pixels best
  (0.031)**; the network wins NRMSE/SSIM/SAM. The paper reports no standard deviations, confidence intervals or
  significance tests, so the small gaps (Table III, Table IV n = 4 vs 5) are not shown to be real.
- Apparent errors in the paper: Table V 50–60% row, NRMSE (cloudy) printed **0.494** (out of line with 0.048–0.063;
  likely 0.049); Table IV caption describes a sequence-to-sequence SAR ablation but the table is seq2point n = 3/4/5;
  the PSNR cell for "least cloudy" is blank; Conclusion says "practicality of SEN12MS-CR" (meaning CR-TS).

## 6. Stated limitations and failure cases
- Persistent cloud: "others are cloud-covered throughout the sequence and require spatial context or cloud-robust
  sensor information to be reconstructed" (Fig. 3 caption, p. 3); "When all input data is covered by thick clouds,
  then this poses a severe challenge for all approaches considered" (p. 8).
- Error grows strongly with cloud cover (Table V, p. 10).
- Matrix/tensor baselines leave "residual artifacts" and "discolorization" under large dense clouds (Fig. 10, p. 12).
- **Land-cover change across the series is not addressed.** The training target is the least-cloudy date anywhere in
  the year, so seasonal or real surface change between input and target is scored as reconstruction error; the paper
  neither measures nor discusses this (the companion 2021 paper does, App. D). Change detection is named only as a
  future use (pp. 1, 11).
- **No per-pixel uncertainty or flagging of filled pixels** in this paper (that is Ebel et al. 2023, UnCRtainTS).
  The only "flag" is the mosaicing baseline's constant 0.5 where no clear date exists.
- Pairing up to 14 days between S1 and S2 (p. 12).

## 7. How to apply to our pipeline
- **Evaluation of `sn8_refhaze` / `sn8_cloudsym` corrections (and any `either_date_dehaze` arm):** adopt the
  three-way split. With our two dates the analogue of their masks is: *cloudy-after & clear-before* (recoverable from
  before), *cloudy on both* (`sn8_cloudsym.cloud_dates` label 3: unrecoverable from time; must be abstained, like
  their 0.5 fill), *clear-after* (preservation: the correction must change these pixels by ~0). Report a
  "preservation" error on clear-after pixels for every arm; their network lost to "do nothing" on exactly this
  metric (0.040 vs 0.031), and our 20 m fade past the gate is where we would lose it too.
- **Baselines every arm must beat** (their Table I shows trivial methods win some metrics): (a) no correction
  (= "least cloudy"); (b) fill-from-before inside the cloud gate (= "mosaicing" with one clear date). Fill-from-before
  must never be scored on flood recall, because it copies the pre-storm road and erases the flood by construction —
  their target-date choice hides the same problem.
- **Report by cloud-cover bins** (Table V): bin roads/tiles by the share of the strip under the cloud gate
  (`sn8_clouds.cloud_table` shares) and give results per bin, not a single mean.
- **Abstain rule:** their "no clear date → 0.5" fill is the dataset-paper version of our T_MIN 0.2 abstain; keep
  abstention explicit and count abstained roads separately rather than filling them.
- **Synthetic test (on hold per the 2026-10-25 scope rulings):** if revived, their seq2seq protocol (alpha-blend the
  cloudy pixels of a real cloudy image onto a clear one, score against the clear original) is the same design as the
  evidence-05 plan to paste HRC_WHU cloud shapes onto clear Ida tiles. The companion paper warns such scores overstate
  real performance.
- **Cloud mask:** s2cloudless is a per-pixel classifier on Sentinel-2 L1C band reflectances (background knowledge,
  not described in this paper, which only cites a blog post); it cannot run on Maxar RGB. Nothing in the mask recipe transfers to `sn8_clouds` / `sn8_cloudspot`
  except the design choice to keep thin haze inside a single binary cloud class.
- **Internal learning (seq2seq):** a per-scene, no-training-data inpainter fitted on clear pixels only. With 2 dates
  and no SAR the input would be noise (their ablation, worse than SAR); not a candidate. Mentioned only because the
  masked loss `‖(x − x̂)·(1 − m)‖` is the right way to fit anything on our clear pixels.

## 8. Feasibility with our data
- **We have no SAR and no other dates** — only one clear pre-storm Maxar date and the post-storm date, RGB uint8 at
  0.5 m, no NIR. Both networks need S1 and/or 3–30 Sentinel-2 dates with 13 bands at 10 m; neither is feasible, and
  the data set (10 m Sentinel-2, ~2 TB) is not a training source for 0.5 m imagery.
- Usable: the masked evaluation protocol (all / cloudy / clear-preservation), the two trivial baselines, cloud-cover
  binning, explicit handling of pixels with no clear observation, and the simulated-cloud protocol if synthetic tests
  return. Numbers to compare against are not transferable (different sensor, scale and task), so none of Table I–VI
  should appear as a benchmark for our results.

## 9. Key quotes
- "the data set is curated without excluding any interval of cloud coverage" (p. 2)
- "Copying cloudy pixel values from one image to another clear-view one … captures the spectral properties of naturally
  cloudy observations more faithfully than synthetic noise … but neither precisely reproduce the statistics of
  satellite images containing natural cloud occurrences" (p. 2)
- NRMSE "only over cloud-free pixels (visible in at least one input optical patch) quantifying preservation of
  information" (p. 7)
- "in case no cloud-free time point exists, then a value of 0.5 is taken as a proxy" (p. 7)
- "The target S2 patch is selected to be the sample showing the minimum cloud coverage over the given time series, i.e.
  it is not necessarily temporally preceding or following the input patches." (p. 8)
- "When all input data is covered by thick clouds, then this poses a severe challenge for all approaches considered."
  (p. 8)
