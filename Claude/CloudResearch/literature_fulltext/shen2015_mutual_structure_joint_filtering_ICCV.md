# Coder handoff: Shen, Zhou, Xu & Jia (2015), Mutual-Structure for Joint Filtering

- **Citation:** Shen, X., Zhou, C., Xu, L., & Jia, J. (2015). Mutual-structure for joint filtering. *ICCV 2015*, 3406–3414. https://doi.org/10.1109/ICCV.2015.389
- **PDF:** `/Users/jusrogers/Masters/papers/shen2015_mutual_structure_joint_filtering_ICCV-summary.pdf` (page 1 = AI summary)
- **Source:** CVF open access, https://openaccess.thecvf.com/content_iccv_2015/papers/Shen_Mutual-Structure_for_Joint_ICCV_2015_paper.pdf (proceedings pagination 3406–3414).
- **Validation:** PDF, 1.82 MB, 9 pages (Read tool last page = p. 3414, pdfinfo 9) = published range; title/authors/DOI match Crossref; Conclusion (§7) and 32 references present. PASS.
- **Read:** pp. 3406–3414 in full (references skimmed).
- **Prepared by:** Claude (AI), 2026-10-29.
- Code: authors' project page http://www.cse.cuhk.edu.hk/leojia/projects/mutualstructure/ (not downloaded, per rules).

## 1. Idea and algorithm (§4–5, Algorithm 1, pp. 3408–3410)
Target I0 (to be filtered), reference G0. Both are optimised: outputs I (filtered target) and G (reference reduced to mutual structure). Channels processed separately (p. 3408), so a grey pair is native.
- Patch similarity (eqs. 2–7): e(I_p, G_p)² = min over (a1, a0) of (1/|N|) Σ (a1 I_q + a0 − G_q)², and symmetrically e(G_p, I_p)². Claim 1: e(I_p,G_p) = σ(G_p)(1 − ρ²) with ρ = NCC. Sum: **S = (σ(I_p)² + σ(G_p)²)(1 − ρ²)²** (eq. 7). Small for common edges (|ρ|→1, magnitude and polarity free) and for smooth patches; large for edges in only one image.
- Objective (eq. 11): E = E_S + E_d + E_r with
  - E_S = Σ_p f(I,G,a_p) + f(G,I,b_p) (eq. 8),
  - E_d = Σ λ‖G_p − G0,p‖ + β‖I_p − I0,p‖ (L2; eq. 9),
  - E_r = Σ ε1 a1_p² + ε2 b1_p² (ridge; eq. 10).
- Alternating closed-form updates (box filters):
```
a1 = cov(I,G)/(var(I)+ε1);  a0 = mean(G) - a1*mean(I)          # eq. 12
b1 = cov(G,I)/(var(G)+ε2);  b0 = mean(I) - b1*mean(G)          # eq. 13
G  = (J_G * I + K_G + λ G0) / M_G                              # eq. 14-17, J_G = μ(b1)+μ(a1), K_G = μ(a0) - μ(b1 b0),
I  = (J_I * G + K_I + β I0) / M_I                              #   M_G = λ/|N| + μ(b1 b1) + 1 (as printed; text extraction garbled, check the PDF)
```
- Initialisation: I(0), G(0) = rolling-guidance-filtered I0, G0 (faster convergence) (p. 3411). ~20 iterations.

## 2. Parameters (p. 3411)
- **λ, β ∈ 30–300** ("control the deviation to G0 and I0"); **ε1, ε2 ≈ 1E−5** (smoothness). Intensity scale not stated; ε ≈ 10⁻⁵ only makes sense on [0,1] data (on 0–255 multiply by 255² ≈ 6.5 × 10⁴ → ≈ 0.65). **Patch size |N| not stated** in the paper.
- Run time ~5 s for 800 × 600, 20 iterations, MATLAB single thread.
- Inputs must be aligned; for non-rigid displacement they use their own multi-modal registration [21].

## 3. Quantitative results
- RGB/depth restoration (Fig. 6, one image): JBF 34.02, GF 34.68, WMF 35.12, Lu et al. [13] 36.15, ours **37.19 dB**. On 20 Middlebury pairs "0.2% higher PSNRs" than [13] on average (that is the paper's wording; a small gain), 50+ times faster (Fig. 7).
- Stereo aggregation (Fig. 8, one pair, error = share of pixels off by > 1 px): BF 1.81, GF 2.50, tree 1.58, ours 1.42.
- Nothing on haze, cloud or remote sensing.

## 4. Stated limitations / caveats
- Iterative and global, so slower than a single GF (5 s vs ~40 ms/Mp). Needs alignment. Few parameter details. Reverse polarity counts as mutual structure (|ρ|), so a road that turns dark (flood) still counts as a "common edge" if the boundary stays put.

## 5. How to apply to our pipeline
- **The risk statement for `sn8_cloudedge` arm (c)** (guide = BEFORE): "Previous joint/guided filters directly transfer the structural information in the reference image to the target one … there may be completely different edges in the two images" (abstract). Arm (c) should be dropped or kept only as a negative control; arms (e) and any WGIF arm guide with the after image.
- **New arm (optional, more work): mutual-structure guide.** Run the mutual-structure iteration on the pair (before/255, after/255), take the resulting G (before reduced to edges shared with after) or I as the guide for the guided filter on t. Parameters to start: λ = β = 100, ε1 = ε2 = 10⁻⁵ on [0,1], patch radius = 2–4 px (our choice; unstated), 20 iterations. Cost on a 1300 × 1300 tile in numpy: tens of seconds; acceptable as a Tilt resource.
- **Outlier / "do not trust" map:** per-patch S (eq. 7) between before and after is a cheap, grey, label-free map of edges present on one date only (changed structure or cloud-hidden structure). Could feed `sn8_cloudsym` as a guard: in high-S patches inside the gate, never take structure from the before date. This is our extension, not tested in the paper.
- **Feasibility:** grey, two aligned dates (we have ~0.6 m alignment), no SAR/NIR. Fully feasible; speed is the only cost.

## 6. Key quotes
- "Previous joint/guided filters directly transfer the structural information in the reference image to the target one … there may be completely different edges in the two images. Simply passing all patterns to the target could introduce significant errors." (abstract, p. 3406)
- "almost all joint image filters identify important structures based on the reference image. These methods work best when the reference data contain all useful information." (p. 3407)
- "We set λ and β in range 30 − 300 … ε1 and ε2 … We set them around 1E − 5." (p. 3411)
