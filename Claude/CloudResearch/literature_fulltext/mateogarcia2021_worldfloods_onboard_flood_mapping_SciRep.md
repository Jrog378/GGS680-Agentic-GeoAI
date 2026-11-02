# Coder handoff: Mateo-Garcia et al. (2021), Towards global flood mapping onboard low cost satellites with machine learning (WorldFloods v1)

- **Citation:** Mateo-Garcia, G., Veitch-Michaelis, J., Smith, L., Oprea, S. V., Schumann, G., Gal, Y., Baydin, A. G., & Backes, D. (2021). *Scientific Reports* 11, 7249. https://doi.org/10.1038/s41598-021-86650-z (DOI from Crossref).
- **PDF:** `/Users/jusrogers/Masters/papers/mateogarcia2021_worldfloods_onboard_flood_mapping_SciRep-summary.pdf` (page 1 = AI summary)
- **Source:** publisher open-access PDF, https://www.nature.com/articles/s41598-021-86650-z.pdf (OpenAlex: gold OA; article CC BY 4.0).
- **Validation:** PDF 1.6, 3.0 MB, 12 pages (Read tool and pdfinfo); title, 8 authors, DOI match Crossref; "Discussion and conclusions", 66 references present; article 7249, pp. 1–12. PASS.
- **Read:** pp. 1–12 in full (references pp. 10–11 skimmed). Supplementary material not downloaded.
- **Type:** dataset + method (onboard ML) paper. Prepared by Claude (AI), 2026-10-29.

## 1. Dataset construction (pp. 4–6)
- 422 flood extent maps, 119 events, Nov 2015–Mar 2019, from Copernicus EMS, UNOSAT, GloFIMR; maps "created by photo-interpretation either manually or semi-automatically, where a human validated machine-generated maps" (p. 4).
- Each map paired with "the raw 13-band S2 image closest in time after the event"; all bands resampled to 10 m by nearest neighbour; labels rasterised at 10 m into **cloud, water, land** (p. 4). Table 1 also has an **invalid** fraction (training 3.81%); the only definition in the text is manual checks for "invalid intensities" (p. 4).
- **Cloud labels:** "We generated cloud masks using s2cloudless" (p. 4) — automatic, not human. No thin/thick distinction, no shadow class.
- Label caveats (p. 4): "there are still mislabeled pixels specially in narrow streams, partially inundated crop fields and in the borders of clouds and water bodies"; temporal misalignment because most maps came from radar (Fig. 5); S2 image is always after the map.
- They avoid "ground truth": labels "have not been validated by ground measurements" (p. 4).
- Splits (Table 1, p. 6): train 108 events / 407 maps / 182,413 patches (cloud 50.25%); val 6/6/1,132; test 5/11/2,029 (flood water 20.23%, cloud 16.21%). Test maps derived from S2 with no misalignment, hand-fixed; no spatial overlap and same-event maps removed from train/val (p. 5).

## 2. Models and training (p. 6)
- Three exclusive output classes (land, water/flood, cloud), 2 bits/pixel. Linear, SCNN (4 conv layers, 0.26 M params, receptive field 9 × 9), U-Net (7.8 M).
- 40 epochs from scratch, 13 bands, 256 × 256 (10 m) or 64 × 64 (80 m); loss = class-frequency-weighted cross-entropy + Dice; augmentation flips/rotations, channel jitter, Poisson noise, brightness/contrast.
- Baselines: NDWI (B3, B8) at 0 and at −0.22 (IoU-best with recall > 94% on the test data, i.e. an optimistic baseline); **NDWI given s2cloudless as perfect cloud masking** (p. 6).

## 3. How cloud enters scoring
- Metrics are precision, recall, IoU of the water class (and recall split flood/permanent by JRC). The main text does **not** state that cloud pixels are removed from scoring; cloud is a predicted class, and water hidden under a predicted cloud counts as a missed water pixel in principle. Cloud occurrence is deliberately lower in val/test "to provide more meaningful results of flood segmentation" (p. 6).
- Recall is prioritised: "missing flooded areas (false negatives) is more problematic than over-predicting floods"; IoU is a good compromise "if recall is sufficiently high (over 94%)" (p. 6).

## 4. Numbers (Table 2, p. 7; total water, test set)
| 10 m | IoU | Recall |
|---|---|---|
| NDWI −0.22 | 65.12 | 95.75 |
| NDWI 0 | 39.99 | 44.84 |
| Linear | 64.87 | 95.55 |
| SCNN | 71.12 | 94.09 |
| U-Net | 72.42 | 95.42 |
- 80 m: U-Net 70.22, SCNN 68.87; 80 m with HyperScout-2 overlapping bands only (no SWIR): SCNN 65.82, U-Net 65.43, linear 50.27.
- Training on all (noisy) maps beat S2-labelled-only maps (Fig. 8, leave-one-event-out).
- Speed: SCNN on Myriad2 segments 12 MP in < 1 min (p. 7).

## 5. Stated limitations
- "our models tend to over-predict water content; a common failure mode is to identify dark regions as water. False positives are mostly clustered in the surroundings of water bodies and in cloud shadows" (p. 7).
- Fixed-threshold NDWI "will incorrectly retrieve buildings and cloud shadows as water" (p. 8).
- Data card: "some labels in the training and validation datasets have significant errors" (p. 10).

## 6. Licence / usage
- Article CC BY 4.0. Data released at https://tinyurl.com/worldfloods; code and checkpoints on GitLab (frontierdevelopmentlab/disaster-prevention/cubesatfloods) (p. 10). **No dataset licence is stated in the paper.** Figure captions say Sentinel-2 imagery and Copernicus EMS products "are provided as public domain" (pp. 2, 5).

## 7. How to apply to our pipeline
- **Mostly a design precedent, not code.** The exclusive land/water/cloud output is what v2 abandoned because it throws away water under thin cloud; do not build our road output as a single exclusive "cloud" class (keep `sn8_cloudspot`/`sn8_clouds` visibility separate from the flood decision).
- **Cloud shadow as false flood:** their main false-positive source. For us, a shadow on the after date darkens a road like water. Add a shadow-specific check in the road tables (dark-rise without the texture loss of water: `sn8_texture` LBP/Gabor before vs after) before the flood vote; report shadow-flagged roads separately.
- **Automatic cloud labels are noisy at edges:** treat any cloud label we generate (dark-rise gate in `sn8_cloudsym`, spotter outputs) as noisy at borders; score cloud masks against HRC_WHU human labels, not against our own masks.
- **Evaluation protocol:** clean, hand-checked, event-disjoint test set; recall-first reporting with IoU — consistent with our sealed-data rule.
- **Feasibility:** the method needs 13-band S2 (SWIR matters); not usable on RGB uint8 0.5 m. Protocol and failure modes transfer.

## 8. Key quotes
- "We generated cloud masks using s2cloudless" (p. 4)
- "there are still mislabeled pixels specially in narrow streams, partially inundated crop fields and in the borders of clouds and water bodies" (p. 4)
- "False positives are mostly clustered in the surroundings of water bodies and in cloud shadows" (p. 7)
