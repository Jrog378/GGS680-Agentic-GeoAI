# Coder handoff: Aybar et al. (2022), CloudSEN12, a global dataset for semantic understanding of cloud and cloud shadow in Sentinel-2

- **Citation:** Aybar, C., Ysuhuaylas, L., Loja, J., Gonzales, K., Herrera, F., Bautista, L., Yali, R., Flores, A., Diaz, L., Cuenca, N., Espinoza, W., Prudencio, F., Llactayo, V., Montero, D., Sudmanns, M., Tiede, D., Mateo-García, G., & Gómez-Chova, L. (2022). *Scientific Data* 9, 782. https://doi.org/10.1038/s41597-022-01878-2
- **PDF:** `/Users/jusrogers/Masters/papers/aybar2022_cloudsen12_cloud_shadow_dataset_SciData-summary.pdf` (page 1 = AI summary)
- **Source:** publisher open-access PDF, https://www.nature.com/articles/s41597-022-01878-2.pdf (article CC BY 4.0). The PDF's dates line reads "Published: xx xx xxxx" (publisher placeholder); content is the final article.
- **Validation:** PDF 1.4, 5.3 MB, 17 pages (Read tool and pdfinfo); title, 18 authors and DOI match Crossref; Technical Validation, Usage Notes, 78 references present; article 782, pp. 1–17. PASS.
- **Read:** pp. 1–17 in full (references pp. 14–16 skimmed). Supplementary Figs. S1–S3 not downloaded.
- **Type:** dataset (Data Descriptor) + benchmark. Prepared by Claude (AI), 2026-10-29.

## 1. Labelling rules (Table 3, p. 5; pp. 4–5)
| Code | Class | Superclass 1 | Superclass 2 | Definition | Priority |
|---|---|---|---|---|---|
| 0 | Clear | non-cloud | valid | "Pixels without cloud and cloud shadow contamination." | 4 |
| 1 | Thick cloud | cloud | invalid | "Opaque clouds that block all the reflectance from the Earth's surface." | 1 |
| 2 | Thin cloud | cloud | invalid | "Semitransparent cloud that alters the surface spectral signal but still allows to recognize the background." | 3 |
| 3 | Cloud shadow | non-cloud | invalid | "Dark pixels thrown by a thick or thin cloud." | 2 |
- Priority = which class wins in overlaps (lower = more relevant): thick > shadow > thin > clear.
- **"Invalid" here = thick + thin + shadow** (Superclass 2). Thin cloud is invalid in this superclass even though "still allows to recognize the background".
- Thin vs thick has "no overall consensus on quantitative approaches delimiting when one class begins and the other ends; thus, it is so far inherently subjective to the image interpreter" (p. 1).
- Shadows of **thin** low clouds are labelled shadow (rule changed after the first QC round, p. 5).
- Edges: "Since there are no quantitative criteria to distinguish between boundaries in semantic classes, the labelers always attempt to maximize the sensitivity score under ambiguous edges" (p. 5) — i.e. edges are drawn generously toward cloud/shadow.
- Patch selection prioritised "Atypical clouds such as contrails, ice clouds, and haze/fog" (p. 3).

## 2. Protocol (pp. 3–5, 8)
1. 25,000 ROIs (5,090 m squares; 5,000 hand-added for snow/built-up) → filters (no saturated/no-data, S1–S2 ≤ 2.5 days, > 15 S2 scenes) → 12,121 → at least one patch per cover class → **9,880 ROIs**, 5 patches each (0%, 0–25%, 25–45% [also written 25–65% on p. 3], 45–65%, > 65%). 509 × 509 px at 10 m (patch size from evidence 02; the paper gives 5,090 m ROIs and 512 × 512 network input).
2. Annotation split: 2,000 ROIs dense (≈150 min each), 2,000 scribble (16 min; 1 min at class centroids then 3 min at cloud/shadow edges), 5,880 only the cloud-free patch annotated.
3. Human calibration: 35 hard patches, labellers confer; trained when OA > 90%; validation on 10 patches without conferring; below 90% → back to calibration (Fig. 4).
4. Dense labelling in IRIS: LightGBM seeded with s2cloudless > 0.7 = thick, < 0.3 = clear; labeller corrects and adds thin cloud/shadow; retrain; repeat; manual fine-tuning. Auto check: GBDT training accuracy > 0.95.
5. QC: two visual reviews by two other experts; patches with difficulty > 4 reviewed by the whole group using a time-series web app (cloudApp).
6. Split: spatially stratified hexagon blocks (50,000 km²; Roberts et al.), stratified by difficulty: 1,827 ROIs train / 173 test (×5 patches).

## 3. Human-level agreement (p. 5, Fig. 7) — a ceiling for our masks
- Before vs after QC: **95.7%** all classes; **98.3%** if thin cloud discarded.
- Producer's agreement: clear 99.1%, thick 96.6%, **thin 78%**, shadow 91.8%. "the detection of semi-transparent clouds remained unclear (21%)"; "thin clouds were always the source of the most contention".

## 4. Benchmark metrics and numbers (pp. 9–14, Table 6)
- Per patch: `PA = TP/(TP+FN)`, `UA = TP/(TP+FP)`, `BOA = 0.5·(PA + TN/(TN+FP))` (eq. 1). PA/UA set to NaN on cloudless patches. Summary: median BOA; % of patches with PA (UA) < 0.1, 0.1–0.9, > 0.9.
- Three experiments on 975 test patches: (a) cloud (thick+thin) vs non-cloud (clear+shadow); (b) cloud shadow; (c) valid vs invalid.
- Table 6a (cloud/no cloud, median BOA): human 0.99; UNetMobV2 0.92; Fmask 0.84; KappaMask L1C 0.82; s2cloudless 0.79; KappaMask L2A 0.77; CD-FCNN 0.72; Sen2Cor 0.71; QA60 0.58.
- Table 6b (shadow): UNetMobV2 0.89; KappaMask L1C 0.74; Fmask 0.72; KappaMask L2A 0.64; Sen2Cor 0.51. PA_low from 8.88% (UNetMobV2) to 64.5% (Sen2Cor).
- Table 6c (valid/invalid): UNetMobV2 0.91; KappaMask L1C 0.81; Fmask 0.81; KappaMask L2A 0.75; Sen2Cor 0.67.
- Error sources: "the omission of small and thin clouds is the primary cause of PAlow values, whereas PAmiddle is mainly attributable to cloud borders misinterpretation"; "Low-thickness clouds, such as cirrus and haze, tend to produce more omission errors independent of the cloud detection algorithm" (p. 10).
- Fmask settings used: cloud/shadow/snow dilation 3/3/0 px, cloud probability 20% (p. 6).

## 5. Licence / usage
- Article CC BY 4.0 (p. 17). Data on Science Data Bank (ref. 57); code at github.com/cloudsen12; Python package `cloudsen12`; total size "up to 1 TB" (p. 13). **The paper states no data licence.** The CC-BY-NC-4.0 in evidence 02 is from the Hugging Face card.

## 6. Stated limitations
- Thin-cloud boundary subjective; shadows rarely co-located perfectly with reference; DL models handle target shift poorly, so other datasets (PixBox, Hollstein) are needed (p. 13); KappaMask/UNet results lack image-boundary context (p. 13).

## 7. How to apply to our pipeline
- **Class map for our outputs (sn8_cloudsym labels, sn8_refhaze.road_handling):** thick cloud → "cannot assess"; thin cloud → "corrected + assessed" (our extension: CloudSEN12 calls thin cloud *invalid*, so correcting through it is our choice, consistent with WorldFloods v2); cloud shadow → separate "shadow" flag (also invalid in CloudSEN12). Apply their overlap priority thick > shadow > thin > clear when combining our masks.
- **Edge rule:** they draw ambiguous edges toward cloud ("maximize the sensitivity"). Our dark-rise gate + 20 m fade is the same direction; label any hand-checked masks of ours the same way so comparisons are like with like.
- **Evaluation of sn8_cloudspot on HRC_WHU:** add per-image PA, UA, BOA with their summary (median BOA; % of images with PA < 0.1 and > 0.9). Report alongside F1/omission/commission (Cloud Score+ protocol). Treat **78% thin-cloud human agreement** as the ceiling for any thin-haze labels.
- **Spatial block split** (hexagons, Roberts et al.) matches our tile-group split rule; cite it.
- **Feasibility:** protocol, class definitions, metrics are fully usable. Data are Sentinel-2 10 m multispectral; a grey/RGB-only model trained on CloudSEN12 RGB would not match 0.5 m Maxar texture. Not a training source for us.

## 8. Key quotes
- "Semitransparent cloud that alters the surface spectral signal but still allows to recognize the background." (Table 3, p. 5)
- "there is no overall consensus on quantitative approaches delimiting when one class begins and the other ends; thus, it is so far inherently subjective to the image interpreter" (p. 1)
- "the labelers always attempt to maximize the sensitivity score under ambiguous edges" (p. 5)
- "For some applications, such as object detection or disaster response, images contaminated with thin clouds are still helpful." (p. 1)
