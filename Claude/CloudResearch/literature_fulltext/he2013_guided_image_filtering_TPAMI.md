# Coder handoff: He, Sun & Tang (2013), Guided Image Filtering

- **Citation:** He, K., Sun, J., & Tang, X. (2013). *IEEE TPAMI* 35(6), 1397–1409. https://doi.org/10.1109/TPAMI.2012.213
- **PDF:** `/Users/jusrogers/Masters/papers/he2013_guided_image_filtering_TPAMI-summary.pdf` (page 1 = AI summary)
- **Source:** author's accepted copy, https://people.csail.mit.edu/kaiming/publications/pami12guidedfilter.pdf — pages numbered 1–13 (header "VOL. 35, NO. X"), not the journal's 1397–1409. Page numbers below are the copy's 1–13.
- **Validation:** PDF, 13 pages = 13-page published range; title/authors/DOI match Crossref; Conclusion and 59 references present. PASS (accepted-manuscript pagination noted).
- **Read:** pp. 1–13 in full (references pp. 12–13 scanned).
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (Algorithm 1, p. 4; eqs. 4–10)
Inputs: filtering input p, guide I, radius r (square window ω of side 2r+1), regulariser ε. Model: `q_i = a_k I_i + b_k` for all i in ω_k (eq. 4); ∇q = a ∇I, so q has an edge only where I does.
```
mean_I  = f_mean(I);   mean_p = f_mean(p)
corr_I  = f_mean(I.*I); corr_Ip = f_mean(I.*p)
var_I   = corr_I - mean_I.*mean_I
cov_Ip  = corr_Ip - mean_I.*mean_p
a = cov_Ip ./ (var_I + ε)          # eq. 7
b = mean_p - a.*mean_I             # eq. 8
q = f_mean(a).*I + f_mean(b)       # eqs. 9-10 (average over overlapping windows)
```
- ε meaning (§3.2, p. 4): "patches with variance (σ²) much smaller than ε are smoothed, whereas those with variance much larger than ε are preserved"; correspondence r ↔ σ_s, ε ↔ σ_r² of the bilateral filter. In flat regions the filter is two cascaded box means.
- Colour guide (eqs. 19–21, p. 6): `a_k = (Σ_k + εU)⁻¹ ( (1/|ω|) Σ I_i p_i − μ_k p̄_k )`, Σ_k the 3×3 covariance. "A color guidance image can better preserve the edges that are not distinguishable in gray-scale (see Fig. 8)"; "the local linear model is more likely to be valid in the RGB color space than in gray-scale" (p. 6–7).
- Gaussian guided filter (eq. 17): replace f_mean by Gaussians, σ_g = σ_s/√2; the authors use the box version in all experiments.
- Relation to soft matting (§3.7, p. 8): guided filter output = one Jacobi iteration of the matting-Laplacian system used in He 2011.
- Speed: 40 ms/Mp grey (I = p); colour 300 ms/Mp (I ≠ p) (p. 9).

## 2. Dehazing recipe (§5, p. 11, Fig. 16)
- "we simply filter the raw transmission map under the guidance of the hazy image (we first apply a max filter to counteract the morphological effects of the min filter (see [11]), and consider this as the filtering input of the guided filter)."
- Parameters: **r = 20, ε = 10⁻³** (minus sign lost in extraction; Fig. 16 caption), image **600 × 400**, intensities scaled to [0, 1] (Fig. 2 caption states the [0,1] convention). Results "visually similar" to matting Laplacian; 40 ms vs 10 s.
- Other parameter sets in the paper, for scale: feathering r = 60, ε = 10⁻⁶; detail enhancement r = 16, ε = 0.1²; flash/no-flash r = 8, ε = 0.2².

## 3. Quantitative results
- Only timing tables (Tables 1–3) and a PSNR table comparing guided vs bilateral outputs (Fig. 2; not ground truth). No dehazing accuracy numbers. Alphamatting benchmark: best filtering-based matting method (June 2012, with global sampling).

## 4. Stated limitations (p. 11)
- "it may exhibit halos near some edges … Halos are unavoidable for local filters when the filters are forced to smooth some edges." Global optimisers (WLS) suppress halos "at the price of global intensity shifting".
- Box window gives slight x/y-axis bias (Fig. 4), fixable with the Gaussian variant.
- Grey guide: halos where an edge is "not distinguishable in gray-scale" (Fig. 8).

## 5. How to apply to our pipeline
- **`sn8_refhaze.dark_reference_dehaze` (DARKREF_GUIDED = False) and `sn8_cloudedge` arm (c):** implement the published recipe as a new arm, all three parts together:
  1. t_raw from the **un-blurred** min-filter dark channel (drop `cv2.blur` in `sn8_clouds.dark_channel` for this path);
  2. **max filter (dilate) with the same 41 px window** on t_raw's haze term (equivalently an opening of the dark channel: `cv2.dilate(cv2.erode(g, k), k)`; `sn8_cloudedge._opened` already exists — check it is applied before t, not after);
  3. guided filter with **guide = the hazy after image**, scaled to [0,1], **ε ≈ 10⁻³** (our `sn8_clouds.dehaze` already divides the guide by 255, so ε is on the paper's scale), **r ≈ the dark-channel half-window scaled to image size**: 20 px on 600 × 400 is ~5% of the short side; for us r = 20–60 px are reasonable arms.
  Our earlier test was guide = after, r = 60, ε = 10⁻⁴, no max filter, with the box blur — ε ten times smaller than the paper's copies more texture (patches with variance > ε are preserved), which matches "t followed texture and flattened detail". That test is not evidence against the recipe.
- **Guide choice in change detection:** "It can transfer the structures of the guidance image to the filtering output" (abstract, p. 1; §3.6). Never guide with the BEFORE image when the output feeds the change detector; the guide's edges become t's edges and print pre-flood structure into the corrected after image.
- **RGB guide:** the Maxar tiles are RGB; a colour guide (eqs. 19–21) is cheap (300 ms/Mp) and the authors say it avoids grey-only halos. An RGB-guide arm is feasible; the correction can still be applied to grey.
- **`sn8_clouds.dehaze` (single-date path):** already uses guide = after/255 but without the max filter; add it.
- **Feasibility:** fully feasible with RGB uint8 0.5 m, no reference date, no SAR, no NIR. OpenCV has `cv2.ximgproc.guidedFilter` (contrib) if the hand-written version needs a cross-check.

## 6. Key quotes
- "we first apply a max filter to counteract the morphological effects of the min filter" (p. 11)
- "Halos are unavoidable for local filters when the filters are forced to smooth some edges." (p. 11)
- "the local linear model is more likely to be valid in the RGB color space than in gray-scale" (p. 7)
