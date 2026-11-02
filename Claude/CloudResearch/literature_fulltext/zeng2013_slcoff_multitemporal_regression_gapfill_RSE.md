# Coder handoff: Zeng, Shen & Zhang (2013), Recovering missing pixels for Landsat ETM+ SLC-off imagery (multi-temporal regression + regularization)

- **Citation:** Zeng, C., Shen, H., & Zhang, L. (2013). Recovering missing pixels for Landsat ETM+ SLC-off imagery using multi-temporal regression analysis and a regularization method. *Remote Sensing of Environment* 131, 182–194. https://doi.org/10.1016/j.rse.2012.12.012
- **PDF:** `/Users/jusrogers/Masters/papers/zeng2013_slcoff_multitemporal_regression_gapfill_RSE-summary.pdf` (page 1 = AI summary; Elsevier notice page; journal pp. 182–194)
- **Source:** Wuhan University SENDIMAGE lab (Shen's group, the authors' institution), https://sendimage.whu.edu.cn/wp-content/uploads/342013_Recovering-missing-pixels-for-Landsat-ETM-SLC-off-imagery-using-multi-temporal.pdf . It is the Elsevier "Author's personal copy" (publisher layout). **Note for Justin:** that copy's own cover page says it is for the authors' internal and educational use and that posting it to institutional websites is not permitted. It was found publicly on the authors' lab site and is used here for private study only; do not redistribute it.
- **Validation:** PDF, 14 pages (Read tool and pdfinfo) = 1 Elsevier notice page + 13 journal pages = published range 182–194; title/authors/DOI match Crossref (DOI printed p. 182); Discussion and conclusion (§4) and References present. PASS.
- **Read:** pp. 182–194 in full; eqs. 2–9 and Table 1 checked on page images (pp. 185–187); reference list skimmed.
- **Prepared by:** Claude (AI), 2026-10-29. Page numbers are the journal's.

## 1. Algorithm, step by step
Terms: **primary** = image with gaps; **fill** = auxiliary image from another date; **target pixel** = a missing pixel.
1. **Model** (eq. 1, p. 184): per band, `p_t = a · f_t + b` — primary value from fill value, with a, b fitted on "locally similar pixels". Motivation (Fig. 1, p. 183–184): between two dates the scatter is not one line, but pixels of the same ground type follow their own line.
2. **Similar pixels** (eqs. 2–3, p. 185): in the fill image, pixel i is similar to target t if `|f_i − f_t| ≤ T`, with T the local variation of the fill image in a **5 × 5** window (printed as `T = sqrt(Σ (f_i − μ)²)`), computed per pixel and per band. Only pixels valid in both primary and fill are used.
3. **Adaptive search window** (p. 185, 188): start at **7 × 7**, grow by 2 px until **N_R** similar pixels are found, up to **99 × 99**. N_R tested 2–90 (Fig. 4): more is better; **30–40 recommended**; N_R = 30 used.
4. **Weights** (eqs. 4–5, p. 185): `D_i = |f_i − f_t + α| · ((x_i − x_t)² + (y_i − y_t)²)`, α small; `W_i = (1/D_i) / Σ (1/D_j)`. The authors found the spatial term matters more than the spectral one (p. 193).
5. **Weighted least squares** (eqs. 6–7): `a = Σ W_i (p_i − p̄)(f_i − f̄) / Σ W_i (f_i − f̄)²`, `b = p̄ − a f̄` (p̄, f̄ means of similar pixels).
6. **Fallback** (eqs. 8–9): if the window maxes out with N_R not reached but > 2 similar pixels, WLR runs on what was found; with too few, the pixel is an "outlier": `a = μ_p / μ_f`, `b = 0` (ratio of window means of common pixels).
7. **Non-reference filling of leftovers** (eqs. 10–15, p. 185–187): minimise `||Q(p′ − p)||² + λ||L p||²` (Q diagonal: 1 valid, 0 missing; L Laplacian), **λ = 0.01**, conjugate-gradient iterations. Laplacian chosen over TV for speed, since 30 m ETM+ "seldom" has sharp edges.

## 2. How changed pixels are handled (our key question)
- The paper splits between-date differences into (1) observation conditions, (2) regular change (seasonal), (3) **abrupt change** (urban expansion etc.). The regression handles (1)–(2) locally. On (3): "As abrupt scene changes are unpredictable, like most studies, we do not discuss this issue in the recovery approach" (p. 183); the conclusion repeats "The recovered result may be unsatisfactory when the scenes change abruptly" (p. 192).
- There is **no change detection or change screen**: whatever was in the fill image is mapped into the gap.

## 3. Quantitative results to compare against (Table 1, p. 187; Wuhan simulated gaps; fill date 29 Dec 2001, primary 19 Mar 2002)
| metric | LLHM (USGS) | NSPI | WLR |
|---|---|---|---|
| r, bands 1–5, 7 | 0.833–0.861 | 0.868–0.911 | 0.898–0.921 |
| ARE % (B1 … B7) | 2.97 … 17.51 | 2.46 … 12.21 | 2.26 … 11.18 |
| UIQI | 0.829–0.854 | 0.868–0.911 | 0.898–0.923 |
| mean spectral angle | 4.456 | 3.178 | 2.861 |
- NDVI from filled pixels vs truth R²: 0.731 (LLHM), 0.859 (NSPI), 0.908 (WLR) (p. 189). Classification OA/kappa also highest for WLR (Table 2).
- Real SLC-off scenes: visual only. ~5× LLHM run time.

## 4. Stated limitations (p. 192–193)
- Precondition: features change regularly; abrupt change not handled.
- Regularisation cannot restore complex texture over large gaps.
- Only local similar pixels; non-local information is future work. Slow.

## 5. How to apply to our pipeline
- **Do NOT use it to fill opaque cloud (T < T_MIN) from the before date.** This is the "paint the dry road back" failure in our notes; the paper states it does not handle abrupt change. Keep "cannot assess" for opaque cloud.
- **Tone curve in `sn8_refhaze.dark_reference_dehaze` / `sn8_cloudsym` (global quantile matching on clear pixels):** the paper's main result is that a **local, similar-pixel weighted regression** beats local linear histogram matching (the USGS method, closest to our quantile matching) especially at edges and across seasonal change. Arm: replace the single global tone curve with a local WLR map before→after estimated from clear pixels only (outside every gate + margin), similar pixels chosen by the before-image value within the local variation, N_R ≈ 30, window grown from 7 px up to a cap (e.g. 99 px ≈ 50 m), weights inverse to spectral difference × squared distance. Use it to predict `tone(dark(before))` (or tone(before)) inside the gate from the surrounding clear ring.
  - Caveat: our before/after clear-ground correlation at 0.5 m is low (r = 0.46, 0.09 on two tiles), which hurts any regression; similar-pixel selection is exactly the paper's remedy (per ground type), so test it on the synthetic-haze benchmark (`haze_recovery`) before trusting it.
  - The ratio fallback (a = μ_p/μ_f, b = 0) is a reasonable abstain-lite for windows with too few similar clear pixels.
- **Laplacian regularisation** (λ = 0.01) is a cheap inpainting for small holes in a t-map or HTM (e.g. over bright-object masks), not for imagery under cloud.
- **Feasibility with our data (RGB uint8 0.5 m, one clear pre-storm date, no SAR, no NIR):** WLR is band-wise and works on 8-bit integers (the paper used 8-bit L1G data), so greyscale or RGB is fine; one fill date is enough (their Maryland example used one). Cost: per-pixel window search; restrict to gate + margin pixels.

## 6. Key quotes
- "As abrupt scene changes are unpredictable, like most studies, we do not discuss this issue" (p. 183)
- "there are obvious linear relationships for the pixels belonging to similar ground features." (p. 183)
- "The recovered result may be unsatisfactory when the scenes change abruptly." (p. 192)
