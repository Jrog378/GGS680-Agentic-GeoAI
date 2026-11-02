# Coder handoff: Sarukkai, Jain, Uzkent & Ermon (2020), STGAN (spatiotemporal generator networks for cloud removal)

- **Citation:** Sarukkai, V., Jain, A., Uzkent, B., & Ermon, S. (2020). Cloud removal in satellite images using spatiotemporal generative networks. *WACV 2020*, 1785–1794. https://doi.org/10.1109/WACV45572.2020.9093564
- **PDF:** `/Users/jusrogers/Masters/papers/sarukkai2020_stgan_spatiotemporal_cloud_removal_WACV-summary.pdf` (page 1 = AI summary)
- **Source:** CVF open access (published version), https://openaccess.thecvf.com/content_WACV_2020/papers/Sarukkai_Cloud_Removal_from_Satellite_Images_using_Spatiotemporal_Generator_Networks_WACV_2020_paper.pdf — page numbers 1796–1805 (CVF), IEEE Xplore lists 1785–1794. arXiv 1912.06838 also exists. The **supplementary appendix** (splits, hyperparameters, labelling heuristics, composite-filter figures) is a separate CVF file and was not downloaded.
- **Validation:** PDF 2.2 MB, 10 pages (Read tool: last page read, p. 1805, references end); pdfinfo agrees. First-page title and four authors (Stanford) match Crossref ("Cloud Removal in Satellite Images Using Spatiotemporal Generative Networks"; the CVF file name says "…from…Generator Networks"). Conclusion (§7) and 35 references present. 10 pages = 10-page IEEE range. PASS.
- **Read:** pp. 1796–1805 in full (references skimmed).
- **Prepared by:** Claude (AI), 2026-10-29.

## 0. Input (the question we were asked)
- **Single-image models (Pix2Pix, MCGAN):** one cloudy image.
- **STGAN:** **three cloudy images** of the same location from the previous 35 days (+ IR optionally). Label = a later clear image. **No clear reference input.** Generative under persistent cloud.
- Stated assumption: "We assume X_ℓ^t changes slowly over time, i.e., X_ℓ^t is close to X_ℓ^{t−1}" (p. 1797) — the training pairs (clear later image as truth for an earlier cloudy one) rely on it. A flood breaks this.

## 1. Data construction (§4, pp. 1797–1799)
- Sentinel-2, 32,270 tiles, 10 m; 100 crops of 256 × 256 per tile; RGB + IR only.
- Crop labels from a cloud-cover algorithm [12] + heuristics: **clear < 1%, cloudy 10–30%, > 30% discarded** ("insufficient visible ground upon manual inspection"); ocean ≤ 10% of data.
- Y_single: each clear crop + most recent cloudy crop within 35 days → **97,640 pairs, 17,800 tiles**.
- Y_temporal: each clear crop + 3 most recent cloudy crops → **3,101 sets, 945 tiles** (became Sen2_MTC_Old used by DiffCR).

## 2. Models (§5, pp. 1799–1800)
- Pix2Pix (U-Net + PatchGAN) and MCGAN on Y_single.
- STGAN Branched ResNet: three encoder–decoders (2 stride-2 convs, 9 residual blocks, 2 stride-½ convs), pairwise concatenation into three more, then a final encoder–decoder (Fig. 4a). Branched U-Net: three 8-block encoders, concatenated, one decoder with skip connections from all three (Fig. 4b). Shared or independent branch weights.
- Loss: `L_cGAN(G,D) + λ L_L1(G)`; λ and splits in the supplement (not read).

## 3. Quantitative results (Tables 1–3, pp. 1801–1803)
- Y_single test: Pix2Pix RGB 22.894 dB / 0.437; Pix2Pix RGB+IR 21.146 / 0.481; MCGAN 21.013 / 0.381; raw cloudy 8.778 / 0.398.
- Y_temporal test: STGAN ResNet (IR) **26.186 / 0.734**; STGAN ResNet RGB 26.000 / 0.573; U-Net RGB 25.822 / 0.564; mean filter 16.893 / 0.173; median 9.674 / 0.395; raw cloudy 8.289 / 0.422.
- Downstream (EuroSAT-trained classifier, hand-labelled test images, count not given): cloudy 72.48%, clear 98.66%, MCGAN 88.59%, Pix2Pix 90.60–91.27%, STGAN 93.96% (RGB and RGB+IR).
- Internal inconsistencies: text says Pix2Pix RGB PSNR "21.130" (table 22.894/23.130) and STGAN ResNet RGB "26.373" (table 26.000) (pp. 1801–1803). No variance or significance tests.

## 4. Stated limitations
- Single image: "Dense clouds make it challenging to learn mapping by using a single image" (Fig. 5).
- RGB-only models "tend to synthesize a variety of false artifacts" (p. 1802; Fig. 7).
- Composite (cloud-masked averaging) leaves "large swathes of missing pixels" under persistent cloud (p. 1802).

## 5. How to apply to our pipeline
- **Not usable as a fill for flood scoring.** It generates under cloud and its training assumes no ground change between dates.
- **Usable without inventing content:**
  1. **Pairing rule as a data recipe:** clear crop + cloudy crops of the same place within a short window, with explicit cover bands (< 1% clear, 10–30% cloudy, > 30% discarded). If we ever assemble real cloudy/clear 0.5 m pairs (e.g. other Maxar acquisitions), use cover bands and a time window, and state the no-change assumption explicitly.
  2. **RGB-only generators hallucinate more** (their Fig. 7): our data are RGB used as grey, so any generative arm would be at the worst end; supports keeping generation out of scoring.
  3. **Bounds protocol** for downstream checks (cloudy 72.5% / clear 98.7% / generated 94.0%): same structure as GACR's lower/upper bound; for us, flood recall on covered roads with uncorrected after, corrected after, and clear truth.
- **Feasibility:** dataset is 10 m Sentinel-2; nothing transfers directly to 0.5 m Maxar.

## 6. Key quotes
- "We assume X_ℓ^t changes slowly over time, i.e., X_ℓ^t is close to X_ℓ^{t−1} for all t and for all locations ℓ." (p. 1797)
- "We retain image crops with percentage cloud cover under 1% as clear and crops with percentage cloud cover between 10% and 30% as cloudy." (p. 1798)
- "the models using only RGB channels tend to introduce false artifacts" (Fig. 7 caption, p. 1803)
