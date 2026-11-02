# Coder handoff: Li, Zheng, Zhu, Yao & Wu (2015), Weighted Guided Image Filtering

- **Citation:** Li, Z., Zheng, J., Zhu, Z., Yao, W., & Wu, S. (2015). *IEEE Transactions on Image Processing* 24(1), 120–129. https://doi.org/10.1109/TIP.2014.2371234
- **PDF:** `/Users/jusrogers/Masters/papers/li2015_weighted_guided_image_filtering_TIP-summary.pdf` (page 1 = AI summary)
- **Source:** accepted manuscript ("ieeetipwgif-double-3rdround.pdf"), A*STAR Open Access Repository, https://oar.a-star.edu.sg/storage/3/3jd018306e/ieeetipwgif-double-3rdround.pdf — pages numbered 1–10, not the journal's 120–129. Page numbers below are the copy's 1–10.
- **Validation:** PDF, 3.56 MB, 10 pages (Read tool and pdfinfo) = 10-page published range; title and all five authors match Crossref; Conclusion (§V) and 37 references present. PASS (accepted-manuscript pagination noted).
- **Read:** pp. 1–10 in full (references skimmed).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§III, eqs. 5–10, p. 3)
Inputs: image to filter X, guide G, window radius ζ1, regulariser λ. Same local linear model as the GIF: Ẑ(p) = a_p′ G(p) + b_p′ in Ω_ζ1(p′).
```
var3   = local variance of G in a 3x3 window                    # σ²_G,1
Gamma  = (var3 + eps) * mean(1 / (var3 + eps))                  # eq. 5: (σ²(p′)+ε) · (1/N) Σ_p 1/(σ²(p)+ε)
Gamma  = Gaussian-smoothed Gamma                                # "to prevent possible blocking artifacts" (sigma not given)
a = (mean(G*X) - mean(G)*mean(X)) / (var_ζ1(G) + λ / Gamma)     # eq. 7 (box means over radius ζ1)
b = mean(X) - a*mean(G)                                         # eq. 8
Ẑ = box_mean(a)*G + box_mean(b)                                 # eqs. 9-10
```
- **ε in Γ:** ε = (0.001 × L)², L = dynamic range of the input (p. 3). On [0,1] data ε = 10⁻⁶; on 0–255 data ε ≈ 0.065.
- Γ > 1 at edges, < 1 in flat areas (p. 3). Larger Γ → smaller effective regulariser → a closer to 1 → edge kept. Note eq. 5 normalises by the mean of 1/(σ²+ε), not the mean of σ² (read from the rendered equation, p. 3).
- Alternatives tested (eqs. 12–13): Sobel or Roberts gradient magnitude as Γ; the 3 × 3 variance preserves edges "slightly better" (Fig. 4, p. 4).
- Cost O(N), same as the GIF (p. 3). Grey guide by construction (scalar G); no colour-guide version is given.

## 2. Dehazing recipe (§IV-B, pp. 5–8)
1. Simplified dark channel: min over colours first, then one min filter Ψ_ζ2 (eq. 23). ζ2 for their own method is not stated; He 2011's ζ2 = 7 (15 × 15) is quoted (p. 6).
2. A_c = mean of the brightest dark-channel pixels per colour; A_min = min_c A_c.
3. t = 1 − (31/32) · dark(X) / A_min (eq. 27; ω = 0.969).
4. Filter t with the WGIF, **guide = the luminance of the hazy image**, **λ = 1/1000 "as in [14], [29]"**, **ζ1 = 60** (p. 6). λ = 10⁻³ is He 2013's ε on [0,1] intensities, so the scale is [0,1]. **No max filter** before filtering (unlike He 2013).
5. t ← t^(1+ς), ς = 0 / 0.03125 / 0.0625 for light / normal / heavy haze, "detected by using the histogram" (detection rule not given) (eq. 28, pp. 6–7).
6. Ẑ_c = (X_c − A_c)/t + A_c (eq. 29). Dehazing is "a type of spatially varying detail enhancement" with gain 1/t − 1 (eq. 30). No t0 floor is stated for their method; they argue a large floor keeps too much haze.

## 3. Quantitative results
- Detail enhancement: no-reference quality metric [25], Table I and Fig. 5 scores (GIF vs WGIF at θ = 1, 4, 9: 37.84/40.98, 38.37/55.97, 35.89/57.89; higher better) (p. 4).
- Dehazing: visual only (Figs. 8–10). Run times 0.80, 5.25, 13.7, 8.31 s vs GIF 0.86, 5.32, 13.62, 8.1 s at 600 × 450 to 2592 × 1944 (MATLAB, pp. 7–8). **No accuracy numbers to compare to.**
- 1-D figures: ζ1 = 15, λ = 1/64 (Fig. 3) and λ = 1/32 (Fig. 4); detail enhancement ζ1 = 16, λ = 1/128.

## 4. Stated limitations
- Γ can cause blocking, hence the Gaussian smoothing (σ unspecified) (p. 3).
- Hard to extend to the gradient domain (p. 10). No discussion of guides whose edges differ from the input's.

## 5. How to apply to our pipeline
- **`sn8_clouds.guided_filter`** → add `weighted_guided_filter(guide, src, radius, lam)`: compute `var3 = blur(g*g,(3,3)) - blur(g,(3,3))**2`, `eps = (0.001*L)**2` with L = 1 if the guide is /255 (as in our code), `Gamma = (var3+eps)*np.mean(1/(var3+eps))`, Gaussian-smooth Gamma (pick σ ≈ 1–2 px, state it is our choice), then `a = cov / (var + lam/Gamma)`. Mean of Γ over **valid pixels only** (no-data would bias it).
- **`sn8_cloudedge` arm (new "f: WGIF")**: t source = `t_data` (or `_opened` t, as arm e), filter with WGIF, **guide = the hazy AFTER image / 255** (never the before image: structure transfer), λ = 10⁻³, radius 60 px (the paper's ζ1; our tiles are larger than 600 × 450, so also try a radius scaled to the 41 px dark window, e.g. 20–50). Same guards (detail, seam, copy, clear-changed).
- Do **not** port step 5 (t^(1+ς)); it is a photographic sky fix with no stated detection rule.
- Why it might help the ring: WGIF keeps t's step where the after image has an edge (the cloud edge is often visible in grey) and smooths more in flat areas. Why it may not: our ring sits where the haze is faint, so the after image may show no edge there and Γ < 1 → more smoothing, not less.
- **Feasibility:** fully feasible with grey uint8 0.5 m, one date for the guide, no SAR/NIR. Cost ≈ the GIF plus one 3 × 3 pass.

## 6. Key quotes
- "the WGIF can avoid halo artifacts like the existing global smoothing filters" (abstract, p. 1)
- "halos are unavoidable for the GIF in [14] when it is forced to smooth edges" (pp. 2–3)
- "filtered by using the WGIF (5)-(10) with the guidance image as the luminance component of the haze image. The value of λ is set to 1/1000 as in [14], [29] and the value of ζ1 to 60" (p. 6)
- "ε is a small constant and its value is selected as (0.001×L)² while L is the dynamic range of the input image" (p. 3)
