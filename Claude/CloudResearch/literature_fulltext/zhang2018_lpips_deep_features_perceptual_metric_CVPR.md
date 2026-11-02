# Coder handoff: Zhang, Isola, Efros, Shechtman & Wang (2018), LPIPS, deep features as a perceptual metric

- **Citation:** Zhang, R., Isola, P., Efros, A. A., Shechtman, E., & Wang, O. (2018). The unreasonable effectiveness of
  deep features as a perceptual metric. *CVPR 2018*, 586–595. https://doi.org/10.1109/CVPR.2018.00068
- **Copy read:** CVF Open Access version,
  https://openaccess.thecvf.com/content_cvpr_2018/papers/Zhang_The_Unreasonable_Effectiveness_CVPR_2018_paper.pdf.
  10 pages, printed page numbers 586–595 (the proceedings pagination; page numbers below are these). The appendix the
  paper refers to is **not** in this copy; it is in arXiv 1801.03924 v2 (14 pages), cited below as "arXiv App.".
- **PDF with summary:** `/Users/jusrogers/Masters/papers/zhang2018_lpips_deep_features_perceptual_metric_CVPR-summary.pdf`
- **Validation:** real PDF (1.7 MB), 10 pages (Read tool and pdfinfo agree); title and all five authors match Crossref,
  which gives pp. 586–595 (= 10 pages); conclusions, acknowledgements and references present. PASS (CVF open-access
  copy of the published paper; IEEE typeset layout not checked).
- **Pages read:** 586–595 (all). Eq. 1 and Figs. 3–4 checked on rendered p. 591. arXiv App. A (text), B (training
  details, Eq. 2), C (TID2013) and D (changelog) read; App. Table 5 and Figs. 7–12 skimmed only.

## The metric (p. 591, Eq. 1; Fig. 3)
- Feed reference x and distorted x0 through a network F. Take features from L layers; **unit-normalise each spatial
  feature vector in the channel dimension** → ŷ^l, ŷ0^l ∈ R^{H_l×W_l×C_l}.
- `d(x, x0) = Σ_l 1/(H_l W_l) Σ_{h,w} || w_l ⊙ (ŷ^l_{hw} − ŷ0^l_{hw}) ||²₂`
  - w_l ∈ R^{C_l}: per-channel weights. "using w_l = 1 ∀l is equivalent to computing cosine distance" (p. 591).
  - Spatial **mean** per layer, then **sum** over layers. The output is a scalar per image pair; before the spatial mean
    you have a per-location map, which is the useful thing for us (see below).
- Layers used (p. 590): VGG — 5 conv layers; AlexNet — conv1–conv5; SqueezeNet — first conv layer and the subsequent
  "fire" modules.
- Variants (p. 591): **lin** = frozen pretrained F, learn w only ("for the VGG network, 1472 parameters are learned");
  **tune** = fine-tune all of F; **scratch** = train F from random weights. All three are called LPIPS.
- Learned weights are constrained non-negative ("projecting the weights into the constraint set at every iteration",
  arXiv App. B). For Alex-lin, conv1–5 have 64/192/384/256/256 channels, 1152 weights; 79.7/71.4/56.8/46.5/27.7% of the
  weights per layer are zero, i.e. most conv1–conv2 units are ignored (arXiv App. A).
- Training of w (arXiv App. B, Eq. 2): a small net G (two 32-channel FC-ReLU layers, a 1-channel FC, sigmoid) maps
  (d0, d1) to ĥ ∈ (0, 1); loss is binary cross-entropy against the human vote fraction h. 5 epochs at lr 1e-4, then
  5 epochs linear decay, batch 50. G is only used for training; the metric is d.
- **Not stated in the paper:** input value range, colour order, resizing, which version string corresponds to which
  weights. The `lpips` pip package (pointer only, not installed) documents RGB inputs scaled to [−1, 1] and ships
  "v0.1" lin weights for alex/vgg/squeeze; verify against its README before coding — these are package facts, not paper
  facts.

## Data the authors used (pp. 588–590, Tables 1–3)
- BAPPS: 64×64 RGB patches, 484k judgements. 2AFC train: 151.4k triplets, 2 judgements each (MIT-Adobe 5k). 2AFC val:
  9.4k distortions + 26.9k real-algorithm triplets, 5 judgements each (RAISE1k and the algorithm sets). JND: 9.6k pairs,
  3 judgements each.
- Distortions: photometric (lightness, colour shift, contrast, saturation), several noise types, Gaussian/bilateral blur,
  spatial (shift, affine, homography, warps, ghosting, chromatic aberration), JPEG; 20 distortions and 308 sequential
  compositions (p. 589). Plus 96 CNN "denoising autoencoders" as distortions.
- Real algorithms: super-resolution (NTIRE 2017, ×2/×3/×4), frame interpolation, video deblurring, colorization.
  **No haze, dehazing, remote-sensing or overhead imagery anywhere.**

## Results to compare against (numbers as stated)
- Averaged over 6 test sets: humans 73.9%; SqueezeNet/AlexNet/VGG (ImageNet, uncalibrated) 68.6/68.9/67.0%; L2, SSIM,
  FSIM 63.2/63.1/63.8% (p. 592).
- Real algorithms, uncalibrated: Squeeze/Alex/VGG 64.0/65.0/62.6%; lin improved 11 of 12 per-task scores, by
  1.1/0.3/1.5 points on average (p. 593). Tune **lowered** transfer to real algorithms (p. 593).
- 2AFC vs JND correlation ρ = .928 (p. 592). On distortions, Alex-tune and VGG-tune reach 80.6% and 81.4% vs human
  82.6% (arXiv App. B).
- Random-weight networks give little gain; self-supervised (BiGAN, puzzle, split-brain) and even stacked k-means beat
  classic metrics (p. 592).

## Key quotes and limits
- "deep embeddings appear to be more sensitive to blur" (p. 593, Fig. 6). "BiGAN tends to perceive correlated noise
  patterns to be a smaller distortion than SSIM" (p. 593).
- "Despite its common use, SSIM was not designed for situations where geometric distortion is a large factor" (p. 592).
- "starting with a pre-trained network and tuning throughout lowers transfer performance" (p. 593).
- Patches were deliberately small "to mitigate the effect of differing 'respects of similarity' that may be influenced
  by high-level semantics" (p. 590), i.e. LPIPS is a **low-level** similarity metric.
- Judgements were crowd-sourced on Amazon Mechanical Turk, not in a lab (p. 590).
- Minor inconsistency in the CVF text: p. 592 refers to "Table 5" for the task-correlation table that is printed as
  Table 4.

## How to apply to our pipeline
- **Role:** an extra full-reference score for dehazing / two-date correction outputs on 0.5 m RGB tiles, reported next
  to PSNR/SSIM and the downstream flooded-road F1 — never alone. Reference = NOAA aerial (where co-registered) or the
  clear pre-storm Maxar date on invariant pixels.
- **Use the spatial map, not only the scalar:** compute the per-location distance before the spatial mean (the package
  exposes a spatial option) and average it only over clear, invariant, non-flood pixels. This lets us mask out true
  change (flood water, debris) and cloud we did not try to correct.
- **Input handling:** uint8 → float, then the range the package expects (documented [−1, 1]); greyscale tiles →
  replicate to 3 channels (the networks were ImageNet-trained on RGB; replication is our assumption, not tested in the
  paper). Fix one backbone (AlexNet-lin is the package default; VGG-lin is the common alternative for losses) and keep
  it fixed across all arms.
- **Caveats:**
  - Domain shift: calibrated on natural-photo 64×64 patches and human 2AFC votes; no overhead imagery. Absolute values
    are not comparable to published natural-image LPIPS; use it only to rank our arms on the same tiles.
  - Registration: LPIPS includes spatial distortions as part of what humans see, so sub-pixel to multi-pixel
    misregistration, building lean (off-nadir) and shadow-direction differences between dates **will raise the
    score** independent of haze quality. Register (e.g. AROSICS-style) and compare arms against the same reference.
  - Date gap: real change between dates counts as dissimilarity; mask it.
  - Blur sensitivity is a feature for us (haze and over-smoothing lower texture), but correlated-noise artefacts may be
    under-penalised relative to SSIM (p. 593).
  - Not a radiometric metric: tone/colour shifts are only one of many distortion types it was trained on.
- **Feasibility with RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR:** fully feasible as an evaluation
  metric (inference only, small pretrained networks: SqueezeNet 2.8 MB, AlexNet 9.1 MB, VGG 58.9 MB of conv weights,
  p. 592). Re-calibrating w on overhead imagery would need our own human 2AFC judgements; not planned. Pointer: pip
  package `lpips` (not installed; any model weights it downloads count as a model download and need the usual OK and the
  `~/Masters/models/` location).
