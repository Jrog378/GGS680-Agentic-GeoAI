# Coder handoff: Tarel & Hautière (2009), Fast Visibility Restoration from a Single Color or Gray Level Image

- **Citation:** Tarel, J.-P., & Hautière, N. (2009). *ICCV 2009*, 2201–2208. https://doi.org/10.1109/ICCV.2009.5459251
- **PDF:** `/Users/jusrogers/Masters/papers/tarel2009_fast_visibility_restoration_ICCV-summary.pdf` (page 1 = AI summary)
- **Source:** author copy, http://perso.lcpc.fr/tarel.jean-philippe/publis/jpt-iccv09.pdf (HAL hal-00435982 holds metadata only, no file). Pages are unnumbered; cited below as pp. 1–8 (= 2201–2208).
- **Validation:** PDF, 4.93 MB, 8 pages (Read tool last page = p. 8 with Conclusion and references [1]–[13]; pdfinfo 8) = 8-page published range; title/authors/DOI match Crossref. PASS (author copy, no page numbers).
- **Read:** pp. 1–8 in full.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. Algorithm (§2, pp. 2–4)
Model (eq. 2): I = R(1 − V/Is) + V, V = atmospheric veil, Is = sky intensity. **Intensities normalised to [0, 1]**, Is = (1,1,1) after white balance (§2.1).
```
W = min_c(I)                     # whiteness; W = I for grey
A = median_sv(W)                 # edge-preserving local average (median = robust bilateral)
B = A - median_sv(|W - A|)       # subtract robust local std: textured areas are probably not foggy
V = max(min(p*B, W), 0)          # eq. 4
R = (I - V) / (1 - V/Is)         # eq. 5
s = int(1/(1 - V/Is)), capped at si;  R = median_{s×s}(R)   # §2.5: smoothing adapted to the contrast gain γ
tone map (§2.6): match log mean/std of the bottom third, then T = U / (1 + (1/255 - 1/M_G) G)   # [0,255]
```
- **Why median, not erosion:** "We also experiment with the erosion and we found that it suffers of halo. This is why a refinement using matting is requested in [5]." (p. 3)
- Median of median along lines (§2.3): n_v line segments of length s_v at uniform orientations, median along each, then median of those; preserves edges and obtuse corners (n_v = 5 in Fig. 3).

## 2. Parameters
- **p** = fraction of veil removed, "usually between 90 and 95%" (p. 3); p = 0.98 too strong, 0.7 too weak (Fig. 4).
- **s_v** = median window, and "the larger size of the assumed white objects. Any close to white object with a size larger than sv is assumed to be white because of the fog" (p. 3). Used: 41 (Figs. 2, 6; Tables), 61 (road scenes), **11 for inhomogeneous fog** (Fig. 7). In pixels.
- **s_i** = max adapted-smoothing window: 1 (off) or 5–19.
- Quantitative runs: s_v = 41, s_i = 1, p = 0.9, local white balance (p. 5).

## 3. Quantitative results we could compare to
- Speed: 0.17 s for 759 × 574, s_v = 61 (fast O(N) median [9]) (p. 5).
- Blind contrast indicators [3] on 4 images (Tables 1–3): new-edge rate e (−0.01 to 0.07), mean gradient ratio r̄ 1.87–2.09 (Tan 2.08–2.34, He 1.33–1.65), saturated pixels Σ = 0.0% on all four (He 0.0–0.007).
- Lane-marking (12 labelled foggy images): max Dice 75% with restoration vs 73% without (SLT detector); best threshold 50 vs 23 (p. 6).
- The e / r̄ / Σ indicators (visible edges at a 5% contrast threshold; gradient ratio; % pixels clipped) are a **label-free protocol** we could run on our corrected after images.

## 4. Stated limitations
- Fog between small leaves not removed: whiteness is decided by a "geometric criterion" (object size), not colour (p. 5).
- Large white objects bigger than s_v are removed as fog (by design).
- Assumes white fog and prior white balance.

## 5. How to apply to our pipeline
- **`sn8_clouds.dark_channel` / `sn8_cloudedge` (new arm "i: median veil"):** our dark channel is a 41 px erosion + 41 px box blur — exactly the operator Tarel reports as haloing. Arm: replace erosion+blur with `A = median(W, sv)`, `B = A − median(|W − A|, sv)`; in the two-date fit use the same operator on both dates so `t = (A_air − veil(after)) / (A_air − tone(veil(before)))`. OpenCV `cv2.medianBlur` handles uint8 with any odd ksize (fast); work on 0–255 and divide by 255 at the end, or on [0,1] float with ksize ≤ 5 only (OpenCV limit for float) — so stay in uint8.
- **Window at 0.5 m:** s_v is also the largest "naturally white" object. Bright roofs and concrete pads at 0.5 m are often 20–60 m (40–120 px), so s_v = 41 px would call them haze in a single-date setting. In the two-date setting the before image cancels that (a roof is bright on both dates), which is our dark-rise logic. Try s_v ∈ {21, 41, 81}.
- **p:** our analysis rule removes all haze (ω = 1); Tarel keeps 5–10% for visual quality. Keep p = 1 for analysis, note the difference.
- **Label-free check:** add Σ (share of valid pixels clipped to 0 or 255 after correction) and r̄ (gradient ratio at visible edges) to `sn8_cloudedge.ring_measures` as guards; they are from the dehazing literature (Hautière et al. 2008 [3]).
- **Feasibility:** grey-native, single date or two dates, no SAR/NIR; fastest arm.

## 6. Key quotes
- "Another advantage is the possibility to handle both color images or gray level images since the ambiguity between the presence of fog and the objects with low color saturation is solved by assuming only small objects can have colors with low saturation." (abstract, p. 1)
- "We also experiment with the erosion and we found that it suffers of halo." (p. 3)
- "Any close to white object with a size larger than sv is assumed to be white because of the fog." (p. 3)
