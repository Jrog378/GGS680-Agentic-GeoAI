# Coder handoff: Mohajerani & Saeedi (2020/2021), Cloud and cloud shadow segmentation via Filtered Jaccard Loss and parametric augmentation (Cloud-Net+, 95-Cloud)

- **Citation:** Mohajerani, S., & Saeedi, P. (2021). Cloud and cloud shadow segmentation for remote sensing imagery via filtered Jaccard loss function and parametric augmentation. *IEEE JSTARS* 14, 4254–4266. https://doi.org/10.1109/JSTARS.2021.3070786 — **arXiv preprint version** (arXiv:2001.08768v2, 23 Apr 2021). Our notes call this "Cloud-Net+ (95-Cloud), arXiv 2001.08768"; the published venue is JSTARS (found via OpenAlex; title/authors match).
- **PDF:** `/Users/jusrogers/Masters/papers/mohajerani2020_cloudnetplus_95cloud_jaccard_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** https://arxiv.org/pdf/2001.08768v2
- **Validation:** PDF 1.5, 8.8 MB, 12 pages (Read tool; last page read; pdfinfo 12) vs published 13 pages (4254–4266) — preprint layout. Conclusion + 71 references present. PASS (preprint).
- **Read:** all 12 pages (Tables I–VII); references skimmed. Page numbers below are the preprint's 1–12.
- **Type:** method + dataset (95-Cloud). Academic (SFU; MDA funding). Prepared by Claude (AI), 2026-10-29.

## 1. Datasets and label handling (§IV-B, pp. 5–6)
- **38-Cloud:** 18 train / 20 test Landsat 8 scenes, mostly North America, "GTs are manually extracted"; 8,400 train / 9,201 test patches 384 × 384; patches > 80% empty removed → 5,155 train.
- **95-Cloud:** + 57 manually labelled scenes (75 train), same 20-scene test set; chosen to include "soil, vegetation, urban areas, snow, ice, water, haze, and different cloud patterns"; ~50% average cloud cover; 34,701 train patches (21,502 non-empty). Public at github.com/SorourMo/95-Cloud-An-Extension-to-38-Cloud-Dataset (p. 6). No licence stated in the paper.
- **Biome 8:** thin cloud + cloud merged → cloud; everything else clear; for shadow, all non-shadow → clear.
- **SPARCS (as used here):** "80 patches of 1000×1000 extracted from complete Landsat 8 scenes", classes cloud, shadow, snow/ice, water, land, flooded (refs [48] Hughes & Kennedy 2019 and [67] Hughes & Hayes 2014).
- Thin cloud/haze: 38-/95-Cloud are binary; the paper's Fig. 3 text speaks of detecting "thick and thin clouds (haze) over snow" in 38-Cloud test patches, implying haze is labelled cloud there (p. 7). No explicit labelling rule is given.

## 2. Methods (§III, pp. 3–5)
- **Cloud-Net+:** 6 contracting / 5 expanding blocks; middle 3×3 conv removed in some blocks; 1×1 convs between 3×3 in contracting blocks; aggregation branch (6 bilinear upsamplings + 1×1 conv); 32.9 M params. Input 192 × 192 × 4 (R, G, B, NIR /65535).
- **Soft Jaccard** (eq. 1) over-penalises empty GTs (worked 2×2 example). **FJL** (eqs. 2–7): `FJL = k_G·G_L·LP(S) + k_J·J_L·HP(S)`, `S = Σ t_i`, sigmoid filters with m = 1000, cut-offs 0.5, k_G = k_J = 1; FJL1: G_L = inverted Jaccard on complements; FJL2: G_L = cross-entropy / Max (Max = 16.1180).
- **SDAA** (eq. 8): remove original shadows by histogram matching shadow to neighbourhood; shift clouds `y_sh = y_cl + r sin(θZ+θZO) cos(θA+θAO)`, `x_sh = x_cl + r sin(θZ+θZO) sin(θA+θAO)`; θAO ∈ {90, 180, 270}°, r ∈ {20…100} px, θZO = 0; darken by `i' = i^γ`, γ ∈ {0.8…0.975}; same-height clouds, flat ground. 11 best combinations kept.
- Training: Adam, lr 1e-4, ×0.3 after 15 epochs without improvement, to 1e-8, batch 12, 20% validation; flips/rotation/zoom; multiclass loss averaged with inverse-frequency weights. Inference threshold 0.5; ~30 s per scene on P100.

## 3. Metrics and numbers (pp. 6–10)
- Jaccard, precision, recall, accuracy **pooled over all test scenes** (sums of tp/fp/fn over M scenes).
- Table III (cloud): 38-Cloud — Fmask V3 85.91, U-Net 85.03, Cloud-Net 87.32, Cloud-AttU 88.72, Cloud-Net+ FJL1 **88.85**; 95-Cloud — Cloud-Net 90.83, Cloud-Net+ FJL1 **91.57**; SPARCS fold 1 — Fmask V3 73.01, Cloud-Net+ 84.00–85.11; Biome 8 fold 1 — Fmask V3 79.81, Cloud-Net+ 85.44.
- Table II (shadow, SPARCS): FJL1 60.59 → 63.44 Jaccard with SDAA.
- Table V (biomes, Biome 8 2CV): snow/ice Jaccard 51.8 (FJL1) / 47.4 (FJL2); others 85–95.
- **Buffer effect (p. 8):** the SPARCS CNN's results use a "two-pixel leeway buffer"; on SPARCS→Biome 8 its accuracy rises from 91.04% (no buffer) to 95.40% (buffer). Cloud-Net+ used no buffer.
- No significance tests; FJL1 vs FJL2 "not significantly different" stated without a test (p. 9).

## 4. Stated limitations
- Shadow detection much weaker than cloud (Jaccard ~36–64%); snow/ice hardest; SDAA assumes equal cloud heights and flat terrain.

## 5. How to apply to our pipeline
- **Empty-tile loss (sn8_cloudspot training):** most HRC_WHU/SN8 patches have little or no cloud; if we move from RF to a trainable probe/head, use FJL1 (or simply Dice + CE) so empty patches are scored fairly. For the RF, the analogue is reporting metrics on empty tiles separately (false-alarm rate on cloud-free tiles).
- **Synthetic shadow test (new arm; uses clear before images only):** adapt SDAA to grey 0.5 m tiles: take a cloud mask (real from `sn8_cloudsym` or synthetic), shift by r px along an azimuth, darken by γ ∈ [0.8, 0.975] on a *clear* tile, and check whether the flood/visibility pipeline calls the darkened road "flooded". Gives a labelled shadow-confusion test without touching sealed data. Note γ darkening ignores texture loss, so it is optimistic for shadow-vs-water separation.
- **Report scores with and without an edge buffer:** their 91.04 → 95.40 example shows edge leniency moves accuracy by ~4 points; always report both for our cloud masks.
- **Pooled vs per-scene metrics:** they pool over scenes; CloudSEN12 reports per-patch medians. State which one we use.
- **Feasibility:** concepts usable; model needs NIR and 30 m Landsat — not directly usable.

## 6. Key quotes
- "Soft Jaccard loss function, however, has a defect: over-penalization of images with no class '1' in their GTs." (p. 3)
- "Two pixels were considered by the authors of CNN SPARCS as a leeway buffer at boundaries ... Note that we used no buffer pixels for the evaluation of our method." (p. 8)
