# Coder handoff: Ebel et al. 2021, SEN12MS-CR (IEEE TGRS 59(7))

**Citation:** Ebel, P., Meraner, A., Schmitt, M., & Zhu, X. X. (2021). Multisensor data fusion for cloud removal in
global and all-season Sentinel-2 imagery. *IEEE TGRS* 59(7), 5866–5878. doi:10.1109/TGRS.2020.3024744
**Copy read:** arXiv:2009.07683v1 (16 Sep 2020), accepted manuscript ("This work has been accepted by IEEE TGRS"),
13 pp = published 5866–5878 (13 pp). PDF: `/Users/jusrogers/Masters/papers/ebel2021_sen12ms_cr_multisensor_cloud_removal_TGRS-summary.pdf`
(page 1 = AI summary). **Read:** pp. 1–13 incl. appendices A–D. Written by Claude, 2026-10-29.

## Evaluation protocol (the part relevant to us)
- **Real pairs:** cloudy + cloud-free S2 L1C + S1, "acquired within the same meteorological season to limit surface
  changes" (p. 5). Co-registration inherited from SEN12MS (orthorectified, UTM); no further alignment step described.
- **Metric on real data = "improved precision and recall"** (Kynkäänniemi et al. 2019), Appendix B, p. 9–10:
  - Embed every image with a pretrained network M: VGG16, second fully connected layer (footnote, p. 10).
  - For a set of embeddings Φ, each φ′ gets a hypersphere of radius ‖φ′ − N_k(φ′)‖ (distance to its k-th nearest
    neighbour in the same set). f(φ, Φ) = 1 if φ falls inside any hypersphere of Φ, else 0.
  - precision(Φ_r, Φ_g) = mean over generated φ_g of f(φ_g, Φ_r); recall(Φ_r, Φ_g) = mean over real φ_r of f(φ_r, Φ_g);
    F1 = 2·P·R/(P+R).
  - k = 10, |Φ| = 7893 (test size); k chosen because patches overlap 50 %, so the target and its 8 overlapping
    neighbours are excluded.
  - **This is a set-to-set (distribution) metric**, not a per-pair or per-pixel distance. Precision asks "is each
    output plausible among the clear images", not "is it close to *its own* reference".
  - "virtually identical results" with other networks is cited from [28] (Kynkäänniemi), not tested in this paper.
- **Pixel metrics** MAE, RMSE, PSNR, SSIM, SAM (equations p. 7; x, y ∈ [0,1], C = 3, H = W = 256) **only on synthetic
  data**, because synthesis guarantees "perfect co-registration, no atmospheric disturbances other than the simulated
  noise, control for no landcover and daylight changes … ensuring that pixel-wise metrics are well-defined" (p. 7).
- **Baselines worth copying:** score the raw cloudy input (and raw SAR) with the same metric as a lower bound (Table III).
  The cloudy input got the *highest recall* (0.705): a diversity metric can reward clouds. Always show the as-is arm.

## Method (not runnable on our data; ideas only)
- Cloud map m: s2cloudless continuous output, values < 0.5 dropped, Gaussian σ = 2 → m ∈ [0,1] (p. 4).
- Generator output Ŝ2 = tanh(atanh(S2) + S2_res) (residual on the cloudy input); a 3×3 conv regresses m̂ from S2_res.
- Losses (p. 4): L_adv (LSGAN); L_cyc = ‖m·(S1 − S̆1)‖₁ + ‖(1−m)·(S2 − S̆2)‖₁; L_idt = ‖m·(S1 − Ṡ1)‖₁ + ‖m·(S2 − Ṡ2)‖₁;
  L_aux = ‖(1−m)·(m − m̂)‖₁; weights λ_adv 5, λ_cyc 10, λ_idt 1, λ_aux 10. L_aux makes the residual ~0 on clear pixels.
- Training: Adam lr 2e-4, β (0.5, 0.999), 50 + 25 decay epochs, 200×200 crops, 10,000-image subset; 7–12 days on one
  RTX 2080.

## Quantitative results (Table III, real test split; Table IV synthetic)
- Precision / recall / F1: cloudy S2 0.161 / 0.705 / 0.267; ours-0 0.560 / 0.491 / 0.523; ours-100 0.564 / 0.551 /
  0.557. Without the cloud map: 0.181 / 0.572 / 0.279 and 0.232 / 0.535 / 0.323.
- Synthetic-trained models on real test: F1 0.194–0.514, all below real-trained (Table IV). Synthetic test PSNR 24.75–
  35.80 dB.
- No significance tests or error bars.

## Stated limitations (Appendix D, p. 10)
Change in land cover / atmosphere / time of day between dates ("strict ground truth correspondence is challenging to
establish and may only be guaranteed by simulating synthetic data"); imperfect cloud masks (non-zero probability on
clear images); dense cloud → hallucinated content ("urban-like landcover was predicted in place of agricultural areas").
RGB-only generator.

## How to apply to our pipeline / Ida test
- **Pre-registration outcome 1 (DINOv2 distance primary) and Revision 1 item 2:** this paper is the citation for "pixel
  metrics are not well-defined on real cross-date pairs". Cite it for that, but **do not say we copy its feature
  metric**: ours is a per-tile paired distance; theirs is set-level precision/recall.
- **Optional extra outcome (cheap):** compute improved precision/recall of DINOv2 *tile embeddings* (mean-pooled patch
  tokens, or CLS) of each arm's thin-cloud tiles against the NOAA tiles, k chosen so that a tile's own overlapping
  neighbours are excluded (their k = 10 rule). This gives a literature-standard set-level number beside our paired
  distance. Note the recall trap: the as-is arm can score high recall.
- **Guard design (outcome 3):** their L_aux (residual ≈ 0 where m ≈ 0) is the learned analogue of our rule that clear
  ground must not move. Our guard tests it explicitly; cite this as precedent for "minimise change to cloud-free pixels".
- **Synthetic tests:** if we ever add synthetic haze to clear Ida tiles (copy-paste blending of a real thin-cloud
  pattern onto a clear tile is the closer of their two simulations), pixel metrics are valid there, but results will
  overstate real performance (Table IV). Synthetic is currently on hold (cloud scope rulings 2026-10-25).
- **Feasibility:** metric ideas feasible on RGB/grey 0.5 m; the model is not (SAR + multispectral + training).
- Modules: evaluation script only; `sn8_cloudsym.py` unchanged.
