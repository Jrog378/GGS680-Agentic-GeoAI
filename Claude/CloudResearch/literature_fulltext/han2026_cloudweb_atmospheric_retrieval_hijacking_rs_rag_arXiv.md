# Coder handoff: Han et al. (2026), From Clouds to Hallucinations: Atmospheric Retrieval Hijacking in Remote Sensing Vision-Language RAG ("CloudWeb")

- **Citation:** Han, J., Li, C., Hu, C., Zhang, Q., Sun, X., Wang, X., Zhang, F., Chen, X., Wei, Y., Long, J., & Guo, J. (2026). From clouds to hallucinations: Atmospheric retrieval hijacking in remote sensing vision-language RAG. arXiv:2605.07273v1 (8 May 2026). https://arxiv.org/abs/2605.07273
- **PDF:** `/Users/jusrogers/Masters/papers/han2026_cloudweb_atmospheric_retrieval_hijacking_rs_rag_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** arXiv, https://arxiv.org/pdf/2605.07273v1. Marked "Preprint"; acknowledgments "omitted for anonymized submission" (p. 10).
- **Identification:** evidence 02's "CloudWeb 2026: cloud-like overlays injected weather hallucinations into remote-sensing RAG answers" — the method is named CloudWeb in the abstract. Identified with confidence.
- **Validation:** PDF (25.6 MB), 40 pages (Read tool; pdfinfo 40); title/11 authors match arXiv metadata; Conclusion (§5), references and appendices A–I present. PASS (preprint).
- **Read:** main text pp. 1–9 and appendices B–F, I in full; Appendix A pseudocode, galleries G–H (case images) and references skimmed.
- **Venue rule:** arXiv → method attribution only.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. What it is
An **adversarial attack**, not a robustness benchmark of natural cloud. Threat model: attacker edits only the query image; retriever, generator, corpus fixed (§3.1, p. 4). Retrieval: cosine similarity of normalised CLIP embeddings, top-k (eqs. 1–4).

## 2. Overlay model (§3.2, p. 4)
- θ = (ρ severity, α opacity, β haze strength, σ edge softness, r texture seed) (eq. 6). Smooth cloud mask M_θ ∈ [0,1]^{H×W} (eq. 7); opacity map A_θ = α M_θ (eq. 8).
- Global haze: H_θ(x) = (1 − β) x + β C_θ (eq. 9), C_θ a smooth cloud/haze colour field.
- Render: x_θ = clip((1 − A_θ) ⊙ H_θ(x) + A_θ ⊙ C_θ) (eq. 10). (This is the same additive-airlight form as the dark-channel haze model, I = J t + A(1 − t), with t = (1 − A_θ)(1 − β).)
- Bounds (Table 3, p. 16): severity [0.35, 0.85], opacity [0.45, 0.95], haze [0, 0.15], edge softness [0, 10]; target coverage 0.18.

## 3. Objective and optimiser (§3.3–3.4, pp. 4–5; App. B)
- L = λ_tar L_tar + λ_src L_src + λ_rank L_rank + λ_nat L_nat + λ_area L_area (eq. 12); λ = 1.0 / 0.3 / 1.0 / 0.05 / 0.1; τ = 0.07; margin µ = 0.02.
- L_tar = −τ log Σ exp(v·t/τ) over weather texts; L_src = τ log Σ exp(v·u/τ) over scene texts; L_rank = E[µ − v·t + v·u]_+; L_nat = TV(M) + ‖M − G_σ(M)‖₁; L_area = (mean(M) − ρ₀)² (eqs. 13–17).
- Differential evolution: population 8, 8 iterations, F = 0.5, CR = 0.7, 2 local refinement steps; ~43 s/query on an RTX 4090 D.

## 4. Data and models (§4.1, p. 5)
- Sample100 = 100 queries each from NWPU-RESISC45, RSICD, RSVQA-LR, LEVIR-CC, **FloodNet**, RSIVQA-UCM, RSIVQA-Sydney (700). Retrievers: GeoRSCLIP B/32, RemoteCLIP B/32, OpenAI CLIP B/32 and L/14, OpenCLIP B/32. Generators: LLaVA-1.5, LLaVA-1.6, InstructBLIP, Qwen2.5-VL, GeoChat, H2RSVLM; top-3 evidence in the prompt; LLM judge = google/gemma-4-31b-it via OpenRouter (App. C).
- Generation evaluated only on **strong303**: 303 cases where GeoRSCLIP retrieval had already been hijacked (weather in top-5) — a conditional result, as the authors say (p. 7).

## 5. Results
- Retrieval W@5 (Table 1, p. 6): clean 0.43–0.86%; Gaussian blur 0.57–1.57%; brightness haze 0.71–1.14%; random noise cloud 1.14–15.29%; fixed (unoptimised) CloudWeb 6.43–22.14%; optimised CloudWeb 8.57% (RemoteCLIP) to **43.29% (GeoRSCLIP)**. T@5 (any change in top-5) is ~77–100% for nearly every perturbation, including blur.
- Generation WHR on strong303 (Table 2, p. 7): optimised 23.76% (GeoChat) to 61.39% (Qwen2.5-VL); random noise cloud 4.29–17.82%; blur/haze ≤ 2.31%.
- FloodNet W@5 (Table 5, p. 19): 4–40% by retriever (GeoRSCLIP 28%).
- Cloud semantics far easier to inject than fog-haze (Target@5 cloud 7–37% vs fog-haze 0.9–4.1%, Table 10, p. 22).
- Robust to JPEG/resize/blur: W@5 37.43–43.14% (p. 8). Best fixed cell opacity 0.9, severity 0.85 (p. 9).
- Perceptual audit (App. E): 19/37 VLMs and 21/30 humans judged the overlay artificial.

## 6. Limitations (App. I; observations)
- Failure cases: strong geometric scene anchors, reflection-like local optima, stable source manifolds (p. 37+). No comparison with unconstrained pixel attacks (p. 6). Overlays are visible ("plausibility here means ambiguity, not imperceptibility", p. 9). Synthetic; no real-cloud test set.

## 7. How to apply to our pipeline
- **Correct our note first:** the hallucinations come from *optimised adversarial* overlays and are measured only on already-hijacked queries; plain haze/blur barely injected weather text (< 2% W@5). It is evidence about CLIP-embedding sensitivity, not that natural thin cloud makes VLMs hallucinate weather.
- **Relevance to Gemma (CSI 709) and any DINOv2/CLIP retrieval:** low-frequency bright veils move embeddings toward "cloud" (App. F.1 argument). If Gemma or a retriever ever sees a hazy after tile, expect cloud/haze wording to dominate. The authors' defences (App. F.2) map onto what we already do:
  - "Atmospheric-risk screening … simple image statistics such as low-frequency energy, contrast attenuation, and bright veil coverage" → our `sn8_clouds` dark-channel / bright masks and `sn8_cloudspot` gate.
  - "Consistency-aware retrieval … the original image, a contrast-normalized image, a dehazed image" with Instab(q) = 1 − |R_k(q) ∩ R_k(T(q))| / |R_k(q) ∪ R_k(T(q))| (eq. 25) → a cheap check: run Gemma's description (or DINOv2 nearest-neighbour cells) on the hazy after tile and on our de-hazed tile (`sn8_refhaze` / `sn8_cloudsym` output) and log the Jaccard instability. High instability flags tiles where the description should not be trusted.
- **Do not** use the CloudWeb renderer to make synthetic training clouds (synthetic cloud is on hold, 2026-10-25 ruling). Its eq. 10 renderer could later serve as a labelled synthetic-haze test, since it is the same transmission/airlight form as our model.
- **Feasibility:** the instability check is feasible on RGB tiles; nothing here needs NIR/SAR.

## 8. Key quotes
- "On GeoRSCLIP ViT-B/32, Weather@5 increases from 0.71% to 43.29%." (abstract, p. 1)
- "Fixed CloudWeb also underperforms the optimized variant despite using the same rendering family, confirming that cloud- or haze-like appearance alone is insufficient." (p. 6)
- "This table should be read as a conditional propagation result under successful GeoRSCLIP retrieval-stage evidence hijacking" (p. 7)
- "changing the retrieval ranking is much easier than steering it toward a specific atmospheric concept." (p. 21)
