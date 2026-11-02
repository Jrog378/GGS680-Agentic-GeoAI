# Coder handoff: Fu, Tamir, Sundaram, Chai, Zhang, Dekel & Isola (2023), DreamSim, learned human visual similarity

- **Citation:** Fu, S., Tamir, N., Sundaram, S., Chai, L., Zhang, R., Dekel, T., & Isola, P. (2023). DreamSim: Learning
  new dimensions of human visual similarity using synthetic data. *Advances in Neural Information Processing Systems 36*,
  50742–50768. https://doi.org/10.52202/075280-2208
- **Copy read:** NeurIPS proceedings camera-ready PDF,
  https://papers.nips.cc/paper_files/paper/2023/file/9f09f316a3eaf59d9ced5ffaefe97e0f-Paper-Conference.pdf. 27 pages
  (main text 1–10, references 11–15, appendix 16–27); page numbers below are the PDF's own. arXiv 2306.09344 v3
  (8 Dec 2023) also has 27 pages; not compared line by line.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/fu2023_dreamsim_human_visual_similarity_NeurIPS-summary.pdf`
- **Validation:** real PDF (41 MB, image-heavy), 27 pages (Read tool and pdfinfo agree); title and seven authors match
  Crossref (the 10.52202 DOI is registered with **Crossref**, publisher "Neural Information Processing Systems
  Foundation"; it resolves to proceedings.com, Curran's print edition), pp. 50742–50768 = 27 pages; discussion,
  limitations, references and appendix present. PASS.
- **Pages read:** 1–27 (all); references (pp. 11–15) scanned. Table 5 (p. 20) checked on the rendered page.

## The metric (pp. 5–6, 18; Fig. 3)
- Per backbone: `D(x, x̃; f) = 1 − cos(f(x), f(x̃))` on a **single global vector per image**: the last-layer CLS token
  for DINO (before layer norm) and MAE (after layer norm); the image embedding for CLIP/OpenCLIP (p. 5). LPIPS and DISTS
  are used "as-is".
- **DreamSim** = concatenation of DINO, CLIP and OpenCLIP features ("the best-performing models": DINO ViT-B/16,
  CLIP ViT-B/32, OpenCLIP ViT-B/32, p. 7), LoRA-tuned, then cosine distance on the concatenated vector. (Table 5, p. 20,
  labels the ensemble "ViT B/16, Mixed".) PCA to ~500 components keeps most of the score (Table 9: 1 comp 63.4%,
  512 → 95.7, 768 → 96.1, 1792 → 96.2; p. 24), so the full ensemble vector is ~1792-D.
- Loss (Eq. 2, p. 6): `L = max(0, m − Δd·ȳ)`, Δd = d0 − d1, ȳ ∈ {−1, 1}, margin **m = 0.05** (equivalent to a triplet
  loss).
- LoRA: rank r = 16, α = 0.5, dropout 0.3, ~0.67% of parameters tuned (p. 6). Adam, lr 3e-4, weight decay 0, batch 16
  for ensembles (512 single models); DreamSim trained 6 epochs, ~30 min/epoch on one RTX 3090 / TITAN RTX (p. 18).
- **Input size:** NIGHTS images are 768×768, **resized to 224×224** (p. 18). Input value range and normalisation are
  **not stated** in the paper; the `dreamsim` pip package (pointer only, not installed) handles its own preprocessing —
  check its README.
- **No spatial map:** unlike LPIPS, there is no per-location distance; one number per image pair.

## Data (pp. 3–5, 17–18; Tables 1–3)
- NIGHTS: Stable Diffusion v1.4, prompt "An image of a <category>", categories from ImageNet (~55%), CIFAR-10/100,
  Oxford 102 Flower, Food-101, SUN397 (pp. 3–4). 100,000 triplets → 10 rounds of AMT 2AFC keeping unanimous votes →
  20,019 triplets (≥6 unanimous votes, avg ~7), split 15,941 / 1,958 / 2,120 (Table 3). JND: 411 test triplets, 3 votes
  per pair.
- Human faces < 0.5% (p. 17); "the dataset has a large focus on object-centric domains" (p. 27).
- **No remote-sensing, nadir, hazy or degraded-image data.**

## Results to compare against (numbers as stated)
- NIGHTS test 2AFC (Table 5, p. 20): PSNR 57.1, SSIM 57.3, LPIPS (AlexNet-linear) 70.7, DISTS 86.0, CLIP B/32 83.1,
  DINO B/16 90.1, MAE B/16 82.1, OpenCLIP B/32 87.6, untuned ensemble 90.8, MLP-tuned ensemble 93.4, **DreamSim (LoRA
  ensemble) 96.2**. Five seeds: 95.9 ± 0.416 (Table 4, p. 19).
- IQA SROCC (Table 8, p. 23), TID2013 / KADID-10k: PSNR 0.687/0.676, SSIM 0.720/0.724, MS-SSIM 0.798/0.802,
  FSIM 0.851/0.854, **LPIPS 0.838/0.883**, DISTS 0.794/0.867, DINO 0.722/0.753, OpenCLIP 0.764/0.841, ensemble
  0.757/0.812, **DreamSim 0.814/0.868**. "LPIPS and FSIM remain best-performing overall."
- Tuning on NIGHTS raises BAPPS (low-level) alignment, lowers THINGS (category) alignment (p. 7, Fig. 14).
- Retrieval user study: preferred 36.8% (ImageNet-R) and 33.6% (COCO) of the time (p. 9). ObjectNet k-NN top-1 max
  30.92% vs OpenCLIP 22.48% (p. 24).

## Key quotes and limits
- Abstract (p. 1): it "focuses heavily on foreground objects and semantic content while also being sensitive to color
  and layout", and "outperforms both prior learned metrics and recent large vision models **on these tasks**"
  (retrieval and reconstruction).
- "Compared to LPIPS & DISTS, our model is more sensitive to objects that appear in individual instances ('things') and
  the presence of people, and less sensitive to 'stuff' categories, such as sky and road" (p. 8, Fig. 7).
- "Removing the background has a smaller impact on model alignment compared to removing the foreground" (p. 8).
- It is "fairly robust to orientation, and more impacted by changes in color, shading, or structure" (p. 7, Fig. 6).
- "The resulting dataset and model does not capture the full range of human similarity judgements, but only the
  variations that we can capture in our synthetically-generated dataset" (p. 27).

## How to apply to our pipeline
- **Role:** at most a secondary, **tile-level** sanity check that a dehazed / two-date-corrected 0.5 m tile still
  "looks like the same scene" as the reference (NOAA aerial or clear pre-storm Maxar). Primary scores stay PSNR/SSIM on
  clear invariant pixels, LPIPS spatial maps, and flooded-road F1.
- **Why not primary:** (1) one global number at 224×224 — a 0.5 m tile resized to 224 loses the road-scale texture we
  care about, and errors cannot be masked to road strips or invariant pixels; (2) it down-weights "stuff" like road and
  sky (p. 8), which is our target class; (3) on low-level IQA distortions LPIPS beats it (Table 8), and haze is a
  low-level degradation; (4) trained on object-centric synthetic photos, not nadir imagery.
- **If used:** crop tiles to 224×224 windows (no resize) over road-rich areas and average; replicate greyscale to
  3 channels (our assumption, untested in the paper); convert uint8 per the package's documented preprocessing; mask
  windows with true change (flood, debris) or remaining cloud. Use only to rank arms on identical windows.
- **Caveats:** date gap, misregistration, building lean and sun angle will move the score; DINO branch dominates the
  attention maps (p. 26). Note our DINOv3-research-only rule does not apply here (DreamSim uses DINO v1 ViT-B/16), but
  the weights are a model download and need the usual OK and the `~/Masters/models/` location.
- **Feasibility with RGB uint8 0.5 m, one clear pre-storm date, no NIR/SWIR/SAR:** feasible to run (inference only,
  three ViT-B backbones), but low expected value for haze evaluation; LPIPS is the better-matched perceptual metric for
  this task. Pointer: pip package `dreamsim` (not installed).
