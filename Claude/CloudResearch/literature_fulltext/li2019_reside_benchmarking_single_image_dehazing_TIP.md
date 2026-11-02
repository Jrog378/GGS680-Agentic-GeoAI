# Coder handoff: Li, Ren, Fu, Tao, Feng, Zeng & Wang (2019), RESIDE: benchmarking single-image dehazing and beyond

- **Citation:** Li, B., Ren, W., Fu, D., Tao, D., Feng, D., Zeng, W., & Wang, Z. (2019). Benchmarking single-image
  dehazing and beyond. *IEEE TIP* 28(1), 492–505. https://doi.org/10.1109/TIP.2018.2867951
- **Copy read:** arXiv:1712.04143v4 (22 Apr 2019, carrying the IEEE 2019 copyright notice), https://arxiv.org/pdf/1712.04143.
  13 pages; the journal has 14. Page numbers below are the **arXiv** pages.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/li2019_reside_benchmarking_single_image_dehazing_TIP-summary.pdf`
- **Validation:** real PDF; title, all 7 authors and DOI match Crossref; conclusions and references present. PASS.
- **Pages read:** 1–13 (all); detection Table X read in full; references checked.
- **Supports ranked fixes (evidence 21):** #4 (task-driven primary validation; synthetic haze only as a labelled secondary
  check), #10 (any dehazing arm must beat "no dehazing" on the task).

## Dataset construction (what "synthetic" means here, pp. 4, 8)
- Model: `I = J t + A(1 − t)`, `t = exp(−β d)` (Eqs. 1–2); inverse `J = (I − A)/t + A` (Eq. 3).
- ITS: 13,990 hazy images from 1,399 indoor depth images (NYU2, Middlebury), 10 per clear image,
  `A ~ U[0.7, 1.0]` per channel, `β ~ U[0.6, 1.8]`.
- SOTS: 500 indoor synthetic test images, generated the same way.
- HSTS: 10 synthetic outdoor + 10 real images for human rating.
- OTS: 72,135 outdoor images; depth from a monocular estimator; β ∈ {0.04 … 0.2}, A ∈ {0.8 … 1}.
- RTTS: 4,322 real hazy web images (traffic scenes) with 41,203 boxes (29,597 used, "difficult" ones excluded).

## Evaluation protocol worth copying
1. Full-reference scores (PSNR, SSIM) are reported only where a clean reference exists.
2. No-reference scores (SSEQ, BLIINDS-II, rescaled so higher is better).
3. Human pairwise comparison on two axes, *clearness* and *authenticity*, fitted with Bradley–Terry:
   `p(X ≻ Y) = 1/(1 + e^{s_Y − s_X})` (Eq. 4), with scores from maximum likelihood (Eq. 5).
4. Task-driven scoring: run a **fixed** downstream model on the dehazed output and report the task metric (mAP).

## Results to compare against
- SOTS (Table III): PSNR/SSIM. DCP 16.62/0.818; CAP 19.05/0.836; DehazeNet 21.14/0.847; AOD-Net 19.06/0.850;
  GRM 18.86/0.855.
- RTTS detection mAP (Table X, Faster R-CNN / YOLO-V2 / SSD-300 / SSD-512):
  - raw haze: 37.58 / 40.37 / 50.26 / 55.55
  - DCP: 40.58 / 39.81 / 49.40 / 55.71
  - BCCR: 41.56 / 40.65 / 51.57 / 57.17
  - GRM: 28.90 / 29.41 / 35.59 / 39.18
  Most methods change mAP by only a few points, and some make it worse.
- No-reference metrics correlate only weakly with detection mAP (Table XI vs X), and subjective and objective rankings
  diverge (Table V).

## Key quotes
- Most methods "rely on the full-reference PSNR and SSIM metrics, with assuming a synthetic testing set with known clean
  ground truth too … their practical applicability may be in jeopardy even a promising testing performance is achieved,
  due to the large content divergence between synthetic and real hazy images" (p. 3).
- "'under-dehazed' images might be preferred over 'over-dehazed' images, the latter potentially losing details and
  suffering from method artifacts" (p. 9).
- "there seems to be no single-best dehazing model for all criteria" (p. 11).
- Authors advocate evaluating "towards more dedicated criteria (e.g., subjective visual quality, or high-level target task
  performance), rather than solely PSNR/SSIM" (p. 11).

## How to apply to our pipeline
- **Validation design (fix 4):**
  - Primary score = task-driven: road-flood F1 from the fixed downstream classifier on Ida tiles where NOAA aerial
    imagery shows the ground (evidence 17), computed on (a) raw hazy input, (b) each dehazing arm, (c) abstention.
    RESIDE's RTTS shows that (a) can tie or beat (b), so (a) is a mandatory baseline.
  - Secondary = synthetic tests, labelled "circular" when the haze comes from our own `I = Jt + A(1−t)`. Prefer haze
    patterns from elsewhere (HRC_WHU thin-cloud mattes, or TIIN-style cirrus-band transmissions).
  - Optional: a two-axis human rating (clearness vs authenticity) of dehazed tiles with Bradley–Terry fitting. It is cheap
    for 20–40 tiles.
- **Dehazing strength:** the "under-dehazed is safer" observation supports keeping ω < 1 and t0 floors in `dehaze()` /
  `_correct()` (`sn8_clouds.py`, `sn8_cloudsym.py`) and sweeping strength against task F1, not PSNR.
- **Feasibility on 0.5 m RGB uint8, one pre-storm date, no NIR/SWIR/SAR:** the protocol is fully feasible. RESIDE data
  (ground-level photos) are not useful as training data for us, and the dataset is distributed through Google Drive and
  Baidu (evidence 21), so do not download it.
