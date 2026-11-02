# Coder handoff: Pérez, Gangnet & Blake (2003), Poisson Image Editing

- **Citation:** Pérez, P., Gangnet, M., & Blake, A. (2003). *ACM Transactions on Graphics* 22(3), 313–318 (SIGGRAPH 2003). https://doi.org/10.1145/882262.882269
- **PDF:** `/Users/jusrogers/Masters/papers/perez2003_poisson_image_editing_TOG-summary.pdf` (page 1 = AI summary)
- **Source:** publisher-formatted copy (ACM copyright footer, pp. 313–318) on a Princeton University course page, https://www.cs.princeton.edu/courses/archive/fall14/cos526/papers/perez03.pdf . The ACM PDF is free to read (OpenAlex: bronze OA) but refused scripted download; no Microsoft Research-hosted PDF was found.
- **Validation:** PDF, 9.81 MB, 6 pages (Read tool last page = p. 318; pdfinfo 6) = published 313–318; title/authors/DOI match Crossref; Conclusion (§5) and references present (alphabetical list ends at Mallat & Zhong; every in-text citation is in it). PASS.
- **Read:** pp. 313–318 in full.
- **Prepared by:** Claude (AI), 2026-10-29. Authors at Microsoft Research UK (company paper).

## 1. Method (§2, eqs. 1–8, pp. 314–315)
Region Ω with boundary ∂Ω, destination f* outside Ω, guidance field v inside.
- Continuous: min_f ∬_Ω |∇f − v|² with f|∂Ω = f*|∂Ω (eq. 3) ⇔ **Δf = div v over Ω, f|∂Ω = f*|∂Ω** (eq. 4). Per channel independently (grey = one channel).
- If v = ∇g (seamless cloning, eq. 9–10): f = g + f̃ with **Δf̃ = 0, f̃|∂Ω = (f* − g)|∂Ω** (eq. 5): the correction is the membrane (harmonic) interpolant of the boundary mismatch.
- Discrete (eq. 7), 4-neighbours N_p:
```
for p in Ω:  |N_p| f_p − Σ_{q∈N_p∩Ω} f_q = Σ_{q∈N_p∩∂Ω} f*_q + Σ_{q∈N_p} v_pq ,   v_pq = g_p − g_q (cloning, eq. 11)
```
  Sparse SPD system; solved with Gauss–Seidel + SOR or V-cycle multigrid; 0.4 s for a 60,000-px disk (Pentium 4) (p. 315).
- Variants: **mixed gradients** v_pq = (f*_p − f*_q) if |f*_p − f*_q| > |g_p − g_q| else (g_p − g_q) (eq. 13); **texture flattening** v_pq = f_p − f_q only where an edge detector fires, else 0 (eq. 15); **local illumination** in log domain v = α^β |∇f*|^−β ∇f*, α = 0.2 × mean |∇f*| over Ω, β = 0.2 (eq. 16); **in-place cloning** after modifying the image inside Ω (new source) or outside (new boundary) (§4, local colour changes, seamless tiling).
- Scale: the equations are linear in intensity, so no scale constants except in the log-domain illumination variant.

## 2. Results and limitations
- Visual only (Figs. 2–12); no quantitative metrics.
- Linear mixing of source and destination gradients "has the effect of washing out the textures" (p. 315). Some "residual contamination of the destination image outside the object" in colour edits (p. 318). Burt–Adelson multiresolution blending mixes distant pixels ("long range mixing, which might be undesirable"), which Poisson cloning avoids (p. 314).

## 3. How to apply to our pipeline (seam where the correction stops)
- **Where:** `sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym._correct` output, tested as a new spread in `sn8_cloudedge.spread_t` (current options "fade", "soft", "datafade").
- **In-place seamless cloning (Pérez §4 form), arm "N2: Poisson seam":**
  1. Ω = gate dilated by the margin (or the soft gate); g = corrected after image (full-strength correction, no fade) on Ω; f* = uncorrected after image outside Ω.
  2. Solve Δf̃ = 0 in Ω with f̃ = (f* − g) on ∂Ω, output f = g + f̃. Equivalently (and better for us, since the field has no texture) do it on the **correction field** c = corrected − after (or L, or 1 − t): the outside value is 0, so the boundary mismatch is −c on ∂Ω; solve Δc̃ = 0 in Ω with c̃ = −c on ∂Ω and use c + c̃. This replaces the linear fade (1 − d/40) with the harmonic interpolant of the boundary mismatch: the correction's gradients inside Ω are kept and only the step at ∂Ω is spread smoothly.
  3. Guidance gradients must come from the **after** image (corrected), never the before image (that would import pre-flood edges — a "no change" bias).
- **Mixed gradients** are not appropriate for us (they pick whichever date has the stronger edge → imports before-image structure).
- **Solver:** scipy.sparse 5-point Laplacian on Ω, `scipy.sparse.linalg.spsolve` or `cg` with an incomplete-Cholesky/AMG preconditioner (pyamg if available); Ω of a few 10⁵ px solves in seconds. No-data pixels: exclude from Ω and treat as Neumann (drop their terms, |N_p| < 4 as the paper does for border pixels).
- **Caveat:** the harmonic correction also pulls the corrected values toward the uncorrected ones near ∂Ω (it distributes the mismatch over Ω). If ∂Ω sits inside residual haze, haze is partly kept there; place ∂Ω on clear ground (beyond the fringe) so the mismatch is small. Measure with the existing seam index and ring score guards.
- **Feasibility:** fully feasible, grey, no SAR/NIR, no other date needed.

## 4. Key quotes
- "the additive correction f̃ is a membrane interpolant of the mismatch (f* − g) between the source and the destination along the boundary ∂Ω" (p. 315)
- "With these classic tools, changes in the selected regions result in visible seams, which can be only partly hidden, subsequently, by feathering along the border of the selected region." (p. 313)
- "three Poisson equations of the form (4) are solved independently in the three color channels" (p. 314)
