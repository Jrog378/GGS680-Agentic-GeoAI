# Coder handoff: Ham, Cho & Ponce (2018), Robust Guided Image Filtering Using Nonconvex Potentials (SD filter)

- **Citation:** Ham, B., Cho, M., & Ponce, J. (2018). *IEEE TPAMI* 40(1), 192–207. https://doi.org/10.1109/TPAMI.2017.2669034
- **PDF:** `/Users/jusrogers/Masters/papers/ham2018_robust_guided_image_filtering_nonconvex_TPAMI-summary.pdf` (page 1 = AI summary)
- **Source:** author's revised manuscript on HAL (not arXiv; no arXiv version found), https://hal.science/hal-01279857/file/sdfilter_revised_v2.pdf (hal-01279857v3, linked from the authors' project page https://www.di.ens.fr/willow/research/sdfilter). Header "SUBMISSION TO IEEE TPAMI, 2016"; pages 1–15 plus a HAL cover page. Page numbers below are the manuscript's 1–15. (HAL's cover misprints the range as "pp. 291-207".)
- **Validation:** PDF, 7.49 MB, 16 pages (Read tool error message "This PDF has 16 pages"; pdfinfo 16) = 1 HAL cover + 15 manuscript pages vs 16 published pages (192–207): accepted-manuscript layout, consistent. Title/authors/DOI match Crossref; Discussion (§6), appendices A–B, 65 references and biographies present. PASS.
- **Read:** all 16 PDF pages (references and biographies skimmed).
- **Prepared by:** Claude (AI), 2026-10-29. Code: https://github.com/bsham/SDFilter (MATLAB; not downloaded).

## 1. Model and algorithm (§3, eqs. 1–14, Algorithm 1, pp. 4–6)
Input f, static guide g, output u (= dynamic guide), confidence c_i ≥ 0, 8-neighbourhood N.
- **Objective (eq. 1–4):** E(u) = Σ_i c_i (u_i − f_i)² + λ Σ_{i,j∈N} φ_µ(g_i − g_j) ψ_ν(u_i − u_j), with φ_µ(x) = exp(−µx²) (guide weight; Algorithm 1 writes the µ explicitly) and **Welsch** ψ_ν(x) = (1 − φ_ν(x))/ν (saturates at 1/ν: large output gradients are cheap, so edges of u persist).
- **MM solver:** surrogate Ψ_ν^y(x) = ψ_ν(y) + (x² − y²)(1 − νψ_ν(y)) (eq. 9). Each step:
```
Wg  = exp(-mu*(g_i-g_j)^2)  on 8-neighbour pairs           # fixed
for k in range(K):
    Wu = exp(-nu*(u_i-u_j)^2)                               # from current output
    W  = Wg * Wu ;  L = diag(W.sum(1)) - W                  # dynamic Laplacian
    u  = solve((C + lam*L), C @ f)                          # eq. 11, sparse Cholesky
```
- **Initialisation:** u0 = WLS solution (l2) or the l1 solution of Σ φ_µ(g_i−g_j) α|u_i−u_j| (IRLS) (eqs. 13–14). l1 converges in ~5 steps, l2 in ~30–35 (Table 2).
- **Scale:** λ sets the scale (random-walk-with-restart interpretation, eqs. 15–18). **Intensities normalised to [0, 1]** (footnote 5, p. 7).

## 2. Parameters used (pp. 8–13)
- Depth upsampling: **µ = 60, ν = 30, k = 10**; λ = 0.1 (synthetic) or 5 (real ToF); c_i = 1 where data exist, 0 elsewhere. PBP nearly flat for λ 0.001–1 (Table 1).
- Scale-space / texture removal: µ = 5, ν = 40, k = 5, c_i = 1; λ 5×10 to 5×10⁴; texture removal guide g = Gaussian(σ = 1–2) of f.
- RGB/NIR: λ = 10, µ = 60, ν = 30, k = 5; flash/no-flash λ = 15.
- Run time: 5 steps ≈ 2.5 s on 500 × 300 (MATLAB CHOLMOD), l1/l2 init 1.2/0.4 s; 0.1 s with a fast WLS solver (footnote 4, p. 6).

## 3. Quantitative results we could compare to (none in our domain)
- Middlebury ×8 depth upsampling PBP (δ = 1): GF 19.85, WModF 8.96, WMF 9.84, **SD 7.07** (Table 3); near discontinuities Tsukuba 10.4 vs GF 43.2 (Table 4).
- BSDS300 boundary localisation of scale-space: ODS 0.621 vs RGF 0.553 vs WLS 0.514 (Table 6).
- No haze, cloud, or remote-sensing tests. Dehazing is only mentioned as an application of joint filtering in general (p. 1, citing He 2013).

## 4. Stated limitations
- No closed form; local minimum depends on initialisation (§3.3.3). "Although nonconvex potentials preserve some noise, the static guidance g with high SNR in our model alleviates this problem" (p. 4).
- On Shen et al. 2015 (mutual structure): "the local filtering formulation of the filter introduces halo artifacts and limits the applicability" (p. 3) — note that Shen's method is itself an iterative global objective; this is Ham's characterisation.

## 5. How to apply to our pipeline
- **Transmission refinement in `sn8_refhaze.dark_reference_dehaze` / `sn8_cloudedge` (new arm "g: SD filter"):** f = raw t (t_data or opened t), g = AFTER grey / 255, c_i = 1 on valid pixels (0 on no-data, which the confidence handles cleanly), µ = 60, ν = 30, λ ≈ 0.1–5 (sweep), k = 5 from an l2 (WLS) start. The Welsch term lets t keep its own step at the cloud edge even where the after image shows no edge (faint fringe), which a static guided filter cannot do; it also resists copying after-image texture into t (our "t followed texture" complaint).
- **Do not use the before image as g.** If a two-date guide is wanted, the paper's framework says use the target's own structure (dynamic) plus a guide whose structure is trustworthy.
- **Cost:** a 1300 × 1300 tile is ~1.7 Mpx: scipy.sparse `spsolve`/`cholmod` per step, roughly 10–60 s per tile in Python for 5 steps (our estimate, scaled from 2.5 s at 0.15 Mpx). Downsample t by 4 (t is smooth; 2 m pixels) to make it fast, then upsample with a guided filter. Run as a Tilt resource.
- **Feasibility:** fully feasible on grey [0,1] data, one date, no SAR/NIR. Most expensive of the refinement arms.

## 6. Key quotes
- "The main drawbacks of such a data-dependent framework are that it does not consider structural differences between guidance and input images, and that it is not robust to outliers." (abstract, p. 1)
- "this approach does not handle differences in structure between depth and color images, transferring all the structural information of the color image to the depth image" (p. 3)
- "We normalize the intensity range to [0, 1]." (footnote 5, p. 7)
