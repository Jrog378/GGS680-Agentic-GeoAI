# Coder handoff: Zhou et al. 2024, AllClear (NeurIPS 37, Datasets & Benchmarks)

**Citation:** Zhou, H., Kao, C.-H., Phoo, C. P., Mall, U., Hariharan, B., & Bala, K. (2024). AllClear: A comprehensive
dataset and benchmark for cloud removal in satellite imagery. *NeurIPS 37* (D&B), 53571–53597. doi:10.52202/079017-1696
**Copy read:** arXiv:2410.23891v1, 27 pp (= proceedings range 53571–53597, 27 pp; only one arXiv version).
PDF: `/Users/jusrogers/Masters/papers/zhou2024_allclear_cloud_removal_benchmark_NeurIPS-summary.pdf` (page 1 = AI summary).
**Read:** pp. 1–27 (main text, references, App. A–C, datasheet, checklist). Written by Claude, 2026-10-29.

## Evaluation protocol
1. **Target selection (p. 5):** for each sample, 3 cloudy S2 inputs u1..u3 and a clear target v with time order
   [u1, v, u2, u3] or [u1, u2, v, u3], so the target "does not include any novel or unseen changes that occurred after
   the capture of the cloudy images". Target cloud+shadow < 10 %.
2. **Masks:** s2cloudless probability; binary cloud = probability > 30 (channel 2, App. A); shadow = dark pixels (NIR
   threshold; main text says 1e-4 on p. 4, App. A lists dark-pixel thresholds 0.20/0.25/0.30, default channel 5) ∩
   projected cloud, water removed via SCL. (Internal inconsistency in the paper; not our concern.)
3. **Metrics:** MAE, RMSE, PSNR, SAM, SSIM, all "modified … to compute only over the cloud-free areas" of the target
   (p. 5). Values clipped (S2 [0, 10000], S1 VV [−25, 0], VH [−32.5, 0]) and scaled to [0, 1].
4. **Stratification:** by Dynamic World land-cover class of the target (Fig. 4) and by average / "consistent" (always
   covered) cloud and shadow percentage (Fig. 5–6).
5. **Simple baselines** (from Ebel et al. 2022/2023): *Least Cloudy* (input with least cloud+shadow) and *Mosaicing*
   (per pixel: copy the one clear input, average several, else 0.5).
6. **Downstream test (App. C.2, p. 19):** 2,000 train / 400 test 256×256 images from the AllClear test set with 9-class
   Dynamic World maps; a 2-D UNet trained "until convergence" on clear images; test inputs = clear target (UpperBound),
   pretrained UnCRtainTS output, 10 % and 100 % AllClear-trained outputs, LeastCloudy; metrics Jaccard, F1, accuracy,
   precision, recall against Dynamic World.
7. **Mask-robustness check (App. C.3):** add 10 % random false-positive mask pixels, or drop the masks; re-score.

## Numbers we could compare to
- Table 2 (p. 6): Least Cloudy PSNR 28.864 / SSIM 0.836 / SAM 6.982 / MAE 0.078; Mosaicing 29.824 / 0.754 / 23.58 /
  0.045; UnCRtainTS (SEN12MS-CR-TS) 29.009 / 0.898 / 5.972 / 0.039.
- Table 11 (p. 19) Jaccard: UpperBound 0.698; UnCRtainTS 0.479; LeastCloudy 0.514; 10 % AllClear 0.591; 100 % 0.604.
- **Rank flip:** UnCRtainTS beats LeastCloudy on all four pixel metrics but is lower on all five downstream metrics.
  Not discussed by the authors.
- Scaling (Table 4): 1 % / 3.4 % / 10 % / 100 % of training → PSNR 27.04 / 28.47 / 33.00 / 33.87.
- 12 input dates vs 3: PSNR 30.40 vs 28.47 (Table 5). Geographic hold-out (no N. America): 34.87 global vs 31.56
  N. America (Table 8).
- Mask corruption: PSNR drop ≤ 0.16 dB, ranking unchanged (Table 12).
- Checklist (p. 27): error bars "[No]". No significance tests anywhere.

## Stated limitations (p. 10)
"the largest limitation of AllClear is the lack of ground truth annotations" (cloud masks are algorithmic); L1C not
atmospherically corrected. Licence CC BY-NC 4.0 (pp. 25–26).

## How to apply to our pipeline / Ida test
- **Pre-registration data-prep step 6 + Revision 1 item 6:** AllClear is the precedent for excluding the reference
  image's own cloud/shadow from every metric. Also copy its **mask-robustness check**: re-score outcome 1 with the
  NOAA bright mask dilated (false positives) and with it removed (false negatives) and report whether arm ranking
  holds. Cheap; one extra loop in the Ida scoring script.
- **Arms:** "as is" is our Least-Cloudy analogue. AllClear shows trivial baselines are hard to beat when the
  reference is near in time (their conjecture, p. 5); our 0–2-day NOAA gap is the same situation, so an "as is ≈
  two-date" result is plausible and must be reportable without spin.
- **Stratify outcomes 1–3** by strip cloud share (their Fig. 5) and by surface class (their Fig. 4: water hardest).
- **Rank-flip check (Revision 1 item 2):** print the arm ranking under grey error (outcome 7) next to the ranking
  under feature distance and the call-level outcome; flag disagreement.
- **Error bars:** AllClear has none; our tile-block bootstrap (Statistics section) already exceeds it. Keep.
- **Feasibility:** protocol ideas feasible; data (10 m multispectral, CC BY-NC) and models not useful for our 0.5 m grey
  tiles.
