# Coder handoff: Kethavath & Hu (2026), Low-Data Supervised Adaptation Outperforms Prompting for Cloud Segmentation Under Domain Shift

- **Citation:** Kethavath, H., & Hu, W. (2026). Low-data supervised adaptation outperforms prompting for cloud segmentation under domain shift. arXiv:2604.08956v1 (10 Apr 2026). https://arxiv.org/abs/2604.08956
- **PDF:** `/Users/jusrogers/Masters/papers/kethavath2026_low_data_adaptation_vs_prompting_cloud_segmentation_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv, https://arxiv.org/pdf/2604.08956v1. The PDF prints no venue. The code repo is `github.com/uga-gaim/2026_CVPRW_CloudPrompts` (p. 1) and secondary web pages list it as a CVPR 2026 workshop (EarthVision) paper; not confirmed from the PDF.
- **Identification:** matches evidence 02's "Kethavath & Hu 2026", CLIPSeg, 60 prompts, 0.255 mIoU baseline — identified with confidence.
- **Validation:** PDF (3.1 MB), 10 pages (Read tool last page = refs [18]–[23], page "10"; pdfinfo 10); title/authors (University of Georgia) match; Conclusion (§5) and 23 references present. PASS (preprint).
- **Read:** pp. 1–10 in full (references pp. 8–10 skimmed).
- **Venue rule:** arXiv / workshop → method attribution only.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Setup (§3, pp. 2–4)
- Data: CloudSEN12+ high-quality subset, Sentinel-2, 10 m, 509 × 509 patches; 8,490 train / 535 val / 975 test; classes clear / thick cloud / thin cloud / cloud shadow. **RGB only (B4, B3, B2)** (p. 3).
- Model: CLIPSeg `clipseg-rd64-refined` (CLIP ViT-B/16 frozen, decoder dim 64, ~1.1M trainable params, input 352 × 352) (p. 3).
- Zero-shot baseline: argmax over logits of four prompts "clear, thick cloud, thin cloud, cloud shadow" (p. 3, Table 2 caption). CLIPSeg is binary per prompt, so multiclass = argmax over prompts.
- FFT: lr grid {1,2,5,10}×10⁻⁵ → 5×10⁻⁵; 20 epochs; weight decay 0.02; warm-up 0.06. LoRA on decoder W_q, W_k, W_v, W_o: lr {5,10,20}×10⁻⁵ → 2×10⁻⁴, rank {8,16,32} → 32, α = 2r, dropout 0.05, wd 0.01, warm-up 0.03, 15 epochs (Table 1, p. 3).
- Loss (§3.5, p. 4): L = 0.8·Focal(α = 0.75, γ = 2) + 1.0·Tversky(α_T = 0.3, β_T = 0.7) + 0.1·Boundary (pixels near class edges weighted ×2 via morphological edge detection).
- Metric: IoU_c = TP/(TP+FP+FN), mIoU = unweighted mean of 4 classes; global confusion matrix over the 975 test images (p. 4).
- Low-data sweep: 0.1% (~8 images) to 100%, 10 random subsets per budget, mean reported (p. 5).

## 2. Results
- Prompts (§4.1, Table 2, Fig. 1, p. 4): all 60 variants < 0.255; worst 0.068 (V7: "ground below / cloud / faded cloud / dark patch"); examples V1 0.222, V8 0.216. Negations ("not cloud", "not haze") worst. Cumulative context prompts also worse.
- Data budget (§4.2, Fig. 2–3, p. 5): both beat zero-shot at 0.1%. FFT 0.57 (10%) / 0.66 (100%); LoRA 0.48 / 0.60. Peak marginal gain at 2.5%; < 3% marginal gain after 30%. LoRA unstable at 0.5% ("treat 1% labeled data as a practical minimum"). 5–10% (~425–850 images) ≈ 85% of max mIoU.
- Class level at 100% (§4.3, Fig. 4, p. 6): zero-shot thick cloud → thin cloud 50% of the time; shadow recall spread 0.28/0.09/0.34/0.28. Correct rate clear 0.59 → 0.92 (LoRA) / 0.93 (FFT); thick 0.32 → 0.88 both; thin 0.49 (LoRA) vs 0.61 (FFT); shadow 0.56 vs 0.69.
- Per-class IoU at 100% (§4.4, p. 6): clear 0.83–0.85, thick 0.75–0.79, **thin 0.38–0.47**, shadow 0.44–0.52. "Supervision dip": thin cloud and shadow fall below zero-shot at 0.5–1% before recovering at 2.5–5%.

## 3. Stated limitations (§4.5, p. 7)
- One architecture family (frozen CLIP encoder); one dataset/sensor; RGB only (SWIR/NIR would need architecture changes); learnable prompts (CoOp, CoCoOp, ensembling) not evaluated; low-data subsets not stratified, so minority classes are sparse at 0.5–1%.

## 4. How to apply to our pipeline
- **Gemma / VLM role:** supports the current rule that a VLM describes and the mask decides. A text-prompted CLIP segmenter does not localise cloud on satellite RGB; thin cloud is the class it confuses most. Do not use CLIPSeg-style prompting as a cloud gate arm; if a reviewer asks, cite this as the negative result.
- **`sn8_cloudspot` (HRC_WHU, frozen DINOv2 tokens + RF):** consistent with the paper's message that a small expert-labelled set beats prompting. Two concrete checks to borrow:
  1. Report **per-class** scores, not just overall: our spotter's thin-cloud recall should be shown separately, since aggregate scores can hide a class getting worse ("supervision dip", p. 6–7).
  2. When sweeping the number of HRC_WHU training images, use stratified subsets that guarantee thin-cloud pixels (their suggested mitigation, p. 7), and run ≥ 5–10 random subsets per budget.
- **Thin-cloud ceiling:** even fully fine-tuned, thin-cloud IoU stayed 0.38–0.47 at 10 m. A thin-cloud IoU in that range on our data would not be unusual; it argues for the two-date route (using the clear before image) rather than single-date thin-cloud segmentation.
- **Feasibility:** nothing to implement directly; the evaluation protocol points are cheap. CLIPSeg itself would run on RGB uint8 but the paper says it should not be used zero-shot.

## 5. Key quotes
- "every variant underperforms the zero-shot baseline (0.255 mIoU), with engineered prompts scoring as low as 0.07 mIoU" (abstract, p. 1)
- "Negative formulations such as “not cloud” and “not haze” produced the worst results across all variants." (p. 4)
- "Practitioners using LoRA should treat 1% labeled data as a practical minimum." (p. 5)
- "practitioners fine-tuning with fewer than 1% labeled samples should monitor per-class performance rather than aggregate mIoU" (p. 7)
