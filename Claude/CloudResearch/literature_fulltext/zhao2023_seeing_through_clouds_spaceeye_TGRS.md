# Coder handoff: Zhao, Olsen & Chandra (2023), Seeing Through Clouds in Satellite Images (SpaceEye)

- **Citation:** Zhao, M., Olsen, P. A., & Chandra, R. (2023). Seeing through clouds in satellite images. *IEEE TGRS* 61, 1–16. https://doi.org/10.1109/TGRS.2023.3239592 — **arXiv preprint version** (2106.08408v1, 15 June 2021, "Preprint. Under review."; v1 is the only arXiv version).
- **PDF:** `/Users/jusrogers/Masters/papers/zhao2023_seeing_through_clouds_spaceeye_TGRS-summary.pdf` (page 1 = AI summary; preprint pages follow)
- **Source:** https://arxiv.org/pdf/2106.08408v1 (OpenAlex best OA location; no open copy of the TGRS version found, one web search).
- **Validation:** PDF, 24.8 MB, 28 pages (Read tool; pdfinfo agrees); title and authors match Crossref (Zhao, Olsen, Chandra; TGRS 61:1–16, 2023). Conclusion ("Summary & Future Work", p. 9), references (pp. 10–13) and supplement (pp. 14–25, own references pp. 26–28) present. The preprint is in NeurIPS format, 9 + supplement pages, not the 16-page TGRS layout: **the published text may differ** (numbers below are the preprint's). PASS (preprint).
- **Read:** pp. 1–28 in full (plain-text extraction; Table 1/2 and pp. 8–9 checked on the PDF images). Reference lists pp. 10–13 and 26–28 skimmed. Supplement figure pages 15–22 are image grids (Pullman/Quincy, WA); captions read.
- **Affiliations:** Zhao — MIT; Olsen, Chandra — Microsoft (Research). Company paper by the brief's rule (2 of 3 authors at Microsoft).
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the preprint's.

## 1. Algorithm, step by step
1. **Inputs** (§4, §5, p. 4–6): a stack of T = 48 daily Sentinel-2 images (10 bands, Level-1C top-of-atmosphere reflectance, scaled to [0, 1]) and the co-registered Sentinel-1 VV/VH images (dB, scaled to [−1, 1]), all resampled to 10 m (bicubic; supp. p. 22). Days with no acquisition are empty; missing and cloudy pixels are set to 0 and flagged by the cloud mask m (1 = clear).
2. **Coarse network, encoders** (§4.1, p. 4): one encoder per modality, 9 conv layers (3 × 3, BatchNorm, LeakyReLU), each date encoded separately, spatial size reduced to 1/8.
3. **Multi-modal masked attention** (eqs. 1–2, p. 4):
   `h_i = (1 / C(r, m)) Σ_j a(r_i, r_j, m_j) · V(o_j)`, `a(r_i, r_j, m_j) = exp(K(r_j)ᵀ Q(r_i)) · m_j`.
   - i: output position in space-time; j: every space-time position; r: SAR encoding; o: multispectral encoding; V: value from o; K, Q: key and query **from SAR only**; C normalises (softmax). m_j = 0 removes cloudy positions, so a hidden pixel copies optical features from the clear places/dates whose **radar** looks like its radar.
4. **Decoder:** 3 up-sampling layers, each followed by two 3 × 3 convs (p. 5).
5. **Refinement network** (§4.2, p. 5): 3-D (space-time) U-Net, 7 down blocks (3 × 4 × 4 kernels; first 3 stride 2 × 2 × 2, rest 1 × 2 × 2), 7 up blocks, skip connections.
6. **Adversarial training with partial observations** (§4.3, eq. 4, p. 5): `E_{x,m∼p_data} log D(x·m) + E_{x∼p_model} E_m log(1 − D(x·m))`. Real images are seen only through their own cloud masks; generated ones through a random real cloud mask. Discriminator: five 3-D partial convolutions (3 × 4 × 4, stride 1 × 2 × 2).
7. **Synthetic-cloud supervision** (§4.4, p. 5–6): take a training sequence, sample **another real cloud mask from the training set**, set the union of the original and sampled mask to zero, and score L1 on the newly hidden (known) pixels. "We don't need to render synthetic clouds in the original image, since all cloudy pixels are set to zeros before being passed to the model." Loss = adversarial + 20 × (L1 coarse + L1 refine).
8. **Variants / baselines** (§4.5, eq. 5, p. 6; supp. C, pp. 24–25): pixels × (time·channels) matrix Y with mask M; `min_{rank(X) ≤ τ} ‖M ∘ (X − Y)‖²_F + α Σ_t ‖X_{t+1} − X_t‖²_F`. Without the rank cap this is "damped interpolation": per pixel and band; as α → 0 it becomes linear interpolation in time with constant extrapolation past the first/last clear date. Solved by alternating minimisation on GPU.

## 2. Parameters the authors used
- Training crops 256 × 256 × 48 days; 32,000 regions from 29 Sentinel-2 tiles (Europe, Iowa, Washington; Jan 2018–Aug 2020); validation 30 regions from 3 other tiles; test **1,000 regions 448 × 448 × 48 days** from non-overlapping tiles in Washington, Iowa, Europe, Rwanda and Australia (p. 6–7).
- Adam, 60,000 iterations, batch 4 on 2 GPUs, lr 2e-5, ×0.1 every 15,000 iterations; 2 days training (p. 6).
- Baselines: SpaceEye-MC τ = 35 (best rank N_r = 35 of full rank 576), α = 3; damped interpolation α = 0.5 (p. 7; supp. p. 25).
- Time step 1 day for the reported test set; for very cloudy places with no clear pixel in 48 days, a 2-day step over 96 days was used in processing (supp. p. 22, footnote 2).
- **Cloud mask** (supp. B.2, p. 23): S2Cloudless (pixel-wise LightGBM trained on the Hollstein point labels) with two edits: (a) remove connected cloud and clear regions under **400 pixels** (400 px at 10 m = 0.04 km²); (b) drop pixels S2Cloudless calls cloudy "much more frequently than the Sentinel-2 native cloud-mask", because "persistently white object-like buildings was masked out in images for all time points, which guaranteed failure of the reconstruction algorithm at these locations". Missing (no-data) pixels are merged into the cloud mask.
- **Shadow mask** (supp. p. 24): ExtraTrees on Hollstein labels (recall 99%, low precision), then kept only pixels "significantly darker (90%)" than the mean clear luminance of the same pixel over the 20 temporally closest images. Fails on topographic shadow and long cloudy spells. Authors: "Our cloud and cloud-shadow detectors are far from state-of-the-art".

## 3. Quantitative results to compare against (Table 1, p. 8; 10 bands, reflectance in [0, 1])
| Method | inputs | temporal | all PSNR | all MAE | all R² | syn PSNR | syn MAE | syn R² |
|---|---|---|---|---|---|---|---|---|
| SpaceEye | optical + SAR | yes | 34.84 | 0.007 | 0.960 | 29.92 | 0.015 | 0.866 |
| SpaceEye-MC | optical + SAR | yes | 26.23 | 0.019 | 0.926 | 21.31 | 0.040 | 0.759 |
| Damped interp. | optical | yes | 26.93 | 0.014 | 0.938 | 21.20 | 0.041 | 0.752 |
| DSen2-CR | optical + SAR | no | 26.05 | 0.020 | 0.924 | 20.45 | 0.053 | 0.681 |
| DeepFill v2 | optical | no | 24.07 | 0.019 | 0.887 | 18.20 | 0.074 | 0.589 |
| SAR2optical | SAR | no | 19.43 | 0.056 | 0.593 | 19.91 | 0.054 | 0.621 |
- "syn" = held-out synthetic-cloud pixels only; "all" = synthetic gaps **plus the clear pixels** the model was given (so "all" is inflated by copying inputs). Use the syn columns.
- Per band (Table 2, "all"): SpaceEye blue 35.63, green 35.81, red 34.65; lowest NIR/NNIR ~33.1–33.4.
- **R²** is described as "Pearson correlation coefficient (R²)" (p. 8) — ambiguous (r or r²).
- **Inconsistency in the preprint:** the Introduction says SpaceEye "achieves a peak signal-to-noise ratio (PSNR) of 28.9" (p. 2), Table 1 says 29.92 (syn) / 34.84 (all). The "8 dB" claim (abstract, p. 9) matches 29.92 − 21.31 ≈ 8.6 (syn) or 34.84 − 26.93 ≈ 7.9 (all).
- **Error vs cloud fraction** (Fig. 7, p. 8): 1,000 test sequences grouped by cloud fraction 0.3–0.95; median and 25–75% MAE. Temporal methods' median error and spread rise with cloud fraction; single-scene SAR methods are flat; DSen2-CR beats MC and damped interpolation at very high cloud fraction. Fig. 5: "There is not a single sequence that is cloud-free, and in fact, a very low fraction of the data has a cloud cover below 50%."
- No significance tests, no per-region breakdown, no evaluation on real (non-synthetic) cloud.

## 4. Stated limitations (§6.4, p. 9; supp. pp. 23–25)
- "cannot handle extremely cloudy situations nor gracefully recover from cloud-detection errors." When clear patches are lacking, the attention "cannot accurately reconstruct"; proposed fix: widen the attention window in time or space with cloud amount (not done).
- "Due to the attention mechanism, failures in the cloud-detector can propagate beyond its original location. This is an effect we have observed for large water bodies where the cloud-detector is less accurate." (No figure or number.)
- Water colour/quality changes are invisible to C-band, so "our system is not well suited to monitor water quality"; snow is hard (supp. p. 24–25).
- Related-work note (p. 2): optical-only multi-temporal systems "assume little change between cloud-free observations and cannot detect abrupt changes" — the authors' reason for adding SAR.
- **No per-pixel uncertainty, confidence or "filled" flag** is produced anywhere in the paper.

## 5. Case studies (all qualitative: pictures, no ground truth, no scores)
- **Flood, Fig. 1 (p. 2):** "a flooded area in Carnation, WA in 2020"; dates 02/07–02/17 (2020). Claim: "it captures the extent of the standing water on February 7th, despite the fact that the multispectral image on the same day was covered in clouds. It also shows how the flood water gradually drained off after mid-February." SAR images for those days are inputs. No flood map, no reference water extent, no metric.
- **Derecho, Fig. 9 (p. 9):** Luther, Iowa, 8/9/2020; SpaceEye predictions 8/8 and 8/10 and a "Changes" map. Change detection on reconstructed images, pictures only.
- **Wildfire, Fig. 10 (p. 9):** Bridgeport, WA, Sept 2020; NBR change vs previous year from SpaceEye. Pictures only.
- **Agriculture, Fig. 8 and supp. A:** NDVI/NDWI time series (Quincy and Pullman, WA, 2019). Pictures and curves only.
- Supp. B.3.1 (p. 24): C-band SAR "is reflected off of standing water ... ideally suited to detect flooding" — the water signal in Fig. 1 comes through the radar.

## 6. How to apply to our pipeline
- **Model: not usable.** It needs a SAR sequence and many optical dates. We have neither.
- **Evaluation protocol (the main transferable piece) — new arm for `sn8_cloudsym` / `sn8_refhaze` / any filler:**
  1. Take clear after-pixels (outside our cloud gate) on development tiles.
  2. Paste a **real** cloud mask taken from another tile (our dark-rise blobs ≥ 2,500 m², or HRC_WHU masks from `sn8_cloudspot` training) — union with the existing mask, exactly as §4.4.
  3. For a filler/reconstruction, zero those pixels and score only them (MAE, PSNR on 0–255 or /255, correlation), separately from clear pixels ("syn" vs "all"). Never report the "all" number alone.
  4. Bin results by cloud fraction of the tile and plot median and 25–75% band (Fig. 7 format).
  - Caveat for **de-hazing** (not filling): a pasted binary mask has no haze, so it tests a filler, not `_correct`. To test de-hazing we must also render haze inside the mask (e.g. `I = J t + A(1 − t)` with a known t field); SpaceEye deliberately avoids rendering — say this when reporting.
  - Paste masks only where the after date is clear; on flooded pixels the "truth" is the flooded after image, which is exactly what the before date does not know. Score flooded and dry clear pixels separately (a before-date filler should fail on flooded ones).
- **Cloud-mask hygiene (`sn8_clouds`, `sn8_cloudsym.cloud_dates`):** two of their edits match ours or suggest arms. (a) Minimum blob size: theirs 400 px at 10 m (0.04 km² = 40,000 m²); ours 2,500 m². (b) "Persistent cloud" check: a pixel flagged cloud on both dates in the same place is more likely a bright roof than cloud — our both-date label (3) should get the same suspicion (`both="smooth"` partly does this). Merge no-data into the "cannot assess" mask, as they do.
- **Water warning (`sn8_cloudspot`, dark-rise mask):** their detector failed over large water and the error spread. For us: measure false cloud on flooded water in the after image before trusting any fill/correction there; keep abstaining (T_MIN, "cannot assess") rather than filling.
- **Flag filled pixels:** SpaceEye has no flag. Our output should keep a per-pixel provenance layer (observed / corrected / filled-from-before / abstained) so road decisions on non-observed pixels can be excluded or reported separately.

## 7. Feasibility with our data
- **No SAR, no other dates:** we have one clear pre-storm Maxar date and the post-storm date, RGB uint8 0.5 m, used mostly as grey, no NIR. SpaceEye's attention needs a SAR key at every date and clear optical values at other dates; damped interpolation needs ≥ 2 clear observations of the same pixel. With two dates, "temporal filling" collapses to copying the before date, which by the authors' own related-work remark "cannot detect abrupt changes" — the flood is the change. **Not feasible as a method.**
- **Feasible:** the synthetic-gap protocol (real masks pasted on clear pixels, score held-out pixels only, by cloud fraction), mask cleaning by blob size and persistence, and the explicit warning that cloud-mask errors over water spread.
- **Flood example:** qualitative only, SAR in the input, 10 m Sentinel scale; it shows nothing about optical-only or 0.5 m reconstruction of flooding.

## 8. Key quotes
- "there are no ground truth cloud-free images that can be used during training." (p. 2)
- "We generate the synthetic cloud mask by randomly sampling another cloud mask from the training set. We update the cloud mask to the union of the original cloud mask and the newly sampled cloud mask." (p. 6)
- "we used the concept of synthetic clouds where we hold out (i.e., set to zeros) parts of the clear images." (p. 8)
- "[these systems] assume little change between cloud-free observations and cannot detect abrupt changes." (p. 2)
- "Due to the attention mechanism, failures in the cloud-detector can propagate beyond its original location. This is an effect we have observed for large water bodies where the cloud-detector is less accurate." (p. 9)
- "persistently white object-like buildings was masked out in images for all time points, which guaranteed failure of the reconstruction algorithm at these locations." (supp. p. 23)
