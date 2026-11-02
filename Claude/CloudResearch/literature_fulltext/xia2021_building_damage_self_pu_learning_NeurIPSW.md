# Coder handoff: Xia, Yokoya & Adriano (2021), Building Damage Mapping with Self-Positive Unlabeled Learning

- **Citation:** Xia, J., Yokoya, N., & Adriano, B. (2021). Building damage mapping with self-positive unlabeled learning. *AI for Humanitarian Assistance and Disaster Response Workshop, NeurIPS 2021*. arXiv:2111.02586. No DOI (arXiv DOI 10.48550/arXiv.2111.02586).
- **PDF:** `/Users/jusrogers/Masters/papers/xia2021_building_damage_self_pu_learning_NeurIPSW-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv v1 (4 Nov 2021), https://arxiv.org/pdf/2111.02586v1. Footer on p. 1: "Artificial Intelligence for Humanitarian Assistance and Disaster Response Workshop, NeurIPS 2021." Workshop papers have no page range; the arXiv copy is the workshop paper.
- **Validation:** PDF (1.97 MB), 7 pages (Read tool, last page = refs [21]–[22], page "7"; pdfinfo 7); title/authors (RIKEN; U. Tokyo) match; Conclusion (§6), Application Context (§7) and 22 references present. PASS.
- **Read:** pp. 1–7 in full.
- **Venue rule:** workshop paper, method attribution only (evidence 02 already marks it excluded from citations).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Setting (§4, p. 3)
- Binary: damaged (+1, positive) vs survived (−1). X = 6 bands = pre- and post-event RGB stacked. D = D_P (n_P labelled positives) + D_U (n_U unlabelled, mix of positives and negatives). π_p = p(Y=+1), π_n = 1 − π_p.
- PU setting built from labelled data: r% of damaged as P (r = 10, 20, 30); remaining (1−r)% damaged + 100% survived as U (§5, p. 4).

## 2. Algorithm (Self-PU, after Chen et al. 2020 [6]; Fig. 1, eqs. 1–8, pp. 3–4)
1. Warm-up 10 epochs.
2. Trusted set D_trust: the n most confident positives and negatives in D_U by the model's positive probability; size grows linearly from 0 to 20% of D_U, "with the 75% bootstrap size of training set" (p. 4). Two selection variants tried: fixed size (drop low-confidence) and without replacement.
3. Hybrid loss (eq. 1): L_hybrid = Σ_{x∈D_trust} L_CE(x,y) + Σ_{x∈D_U−D_trust} L_nnPU(x).
4. Two students g1, g2 (same data, same architecture) distil into each other: L_MSE(g1,g2,x) = ‖f(g1(x)) − f(g2(x))‖², f = sigmoid (eqs. 2–3); applied only on hard samples: L_S = L_MSE when L_nnPU(x) > α·L_MSE, else 0 (eq. 4).
5. Two teachers G1, G2 as moving averages of the students, Θ_t = θ_{t−1} + β θ_t (eqs. 5–6, as printed; parameter β), and L_teacher = Σ ‖f(G_k(x)) − f(g_k(x))‖² (eq. 7).
6. Total L = L_hybrid + L_student + L_teacher (eq. 8).
- **nnPU is not written out in this paper** (cited as [7], Kiryo et al. 2017). For coding, the standard nnPU risk is R = π_p·R̂_P⁺(g) + max(0, R̂_U⁻(g) − π_p·R̂_P⁻(g)), which needs the class prior π_p. **The paper does not say how π_p was set.**

## 3. Parameters
- VGG11 (8 conv + 3 FC), SGD momentum 0.9, batch 16, 100 epochs, one V100 (p. 4). Splits 4/3/3 train/val/test. α ∈ {10,20,30,40} → best 20 (0.79); β ∈ {0.3,0.4,0.5,0.5} → best 0.5 (Table 3; β = 0.5 is printed twice with 0.79 and 0.78, an error in the table). Learning rate not stated.

## 4. Data
- ABCD (Tohoku 2011 tsunami): 160 × 160 patch pairs, 4,253 damaged / 4,253 survived (p. 2).
- xBD (WorldView): 128 × 128 patches; Palu tsunami 2018: 7,645 (27% damaged); Hurricane Michael 2018: 9,214 (29% damaged). Major damage + destroyed → damaged; no + minor → survived (pp. 2–3).

## 5. Results (Table 1, accuracy, mean of 5 runs, p. 5)
| Data | r | Full PN | Std PN | Small PN | PU (U as N) | nnPU | Self-PU |
|---|---|---|---|---|---|---|---|
| ABCD | 10/20/30 | 0.94 | 0.72/0.75/0.77 | 0.64/0.67/0.69 | 0.53/0.54/0.55 | 0.74/0.78/0.80 | 0.79/0.81/0.87 |
| Palu | 10/20/30 | 0.95 | 0.74/0.76/0.81 | 0.71/0.73/0.75 | 0.64/0.66/0.66 | 0.79/0.82/0.85 | 0.82/0.87/0.89 |
| Michael | 10/20/30 | 0.92 | 0.76/0.78/0.80 | 0.67/0.69/0.72 | 0.59/0.60/0.59 | 0.79/0.84/0.86 | 0.82/0.84/0.86 |
- Ablation (Table 2, ABCD, r = 10 presumably — the table does not say which r): nnPU 0.74, L_hybrid 0.76, + L_student 0.77, full Self-PU 0.79.
- Only overall accuracy; no F1, no per-class, no variance across runs; no significance tests. Hurricane Michael (the closest to our storm) shows Self-PU = nnPU at r = 20 and 30.

## 6. Limitations (stated and observed)
- Stated: future work to combine past-disaster labels with few new positives (p. 5).
- Observed: buildings not roads; patch classification not segmentation; unknown π_p; workshop-level evaluation.

## 7. How to apply to our pipeline
- **The useful finding is the baseline gap, not Self-PU:** naive "unlabelled = negative" is the worst arm on all three disasters (0.53–0.66), and plain nnPU recovers most of the gap to supervised. For SpaceNet 8 roads under cloud, "not flooded" labels are partly unlabelled (analysts "only attribute what was visible", evidence 10).
- **Arms for the road flood classifier (wherever the per-road model is trained, e.g. `sn8_models.py`; read-only, so new wrapper code):**
  1. Baseline: current training (cloudy "not flooded" roads as negatives).
  2. Exclude: drop roads with cloud share above the gate from the negatives in training only (evidence 02's "cheapest fix"); scored set unchanged.
  3. nnPU: treat cloudy "not flooded" roads as U and clear-sky labelled roads as P/N; nnPU on U. π_p estimated from the clear-sky flooded share (an assumption to state).
  - Compare by McNemar on the same scored roads, per the significance rule. Self-PU's two-student/two-teacher distillation is not worth it for a random-forest / small-feature model.
- **Cloud mask feeds the U set:** `sn8_cloudspot.spot_table` or `sn8_clouds.cloud_table` share per road decides who is U.
- **Feasibility:** feasible; needs only labels and per-road cloud share. Uses SpaceNet 8 published labels unmodified (cloudy roads are re-weighted, not relabelled), consistent with the labelled-data rule.

## 8. Key quotes
- "The fully-supervised model with PU setting obtained the worst results because the training label is very noisy, especially for the negative labels." (p. 4)
- "nnPU makes further improvements in all cases. Self-PU improves the performance on all three disaster datasets." (p. 4)
- "we can obtain nearly the accuracies of 90% using only 30% positive damaged class as the input." (p. 4)
