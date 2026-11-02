# Claim checks, batch D3 (GMU downloads of 2026-10-30, against full texts)

Compiled by Claude (AI), 2026-10-30, from seventeen full-text reads (16 IEEE papers plus Shendryk et al. 2019, ISPRS JPRS).
Each claim our notes make about a paper is checked against the full text and marked **verified in full text**,
**contradicted** (the paper says something different; what it says is given), or **not in paper**. Rows marked
**addition** record something the full text adds that matters for coding. Page numbers are the journal's (article pages
for TGRS/GRSL article-numbered papers). Sources searched: everything under `CloudResearch/` (grep on author names, method
names, years and DOIs). No evidence file, earlier claim-check file or code was edited. Each handoff
(`<name>_handoff.md` in this folder) lists the pages read; every paper was read in full, including its references.

Venue rule (JIF > 4 or company papers): IEEE SPL (Pan 2015) is likely below 4; IEEE GRSL (Li, Hu & Ai 2019; Zhang, Peng &
Huang 2018; Peter et al. 2022) is borderline at about 4; the others (TGRS, TIP, ISPRS JPRS, Trans. SMC) are above 4. These are
from general knowledge, not checked against JCR. See `ledger_D3.csv`.

## Lin, Tsai, Lai & Chen 2013 (IEEE TGRS) — lin2013
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev10 l. 306 | Lin, C.-H., Tsai, P.-H., Lai, K.-H., et al. (2013). *IEEE TGRS* 51(1), 232–241. https://doi.org/10.1109/TGRS.2012.2197682; read level "Abstract" | **verified in full text** (fourth author: J.-Y. Chen); read level now full text | p. 232 |
| 2 | ev10 l. 113 | "Reference-based cloud filling is posed as a Poisson equation for 'radiometric accuracy and consistency' (Lin)" | **verified in full text**: eqs. (4)–(9), Dirichlet boundary from the target image | abstract p. 232; pp. 234–235 |
| 3 | ev10 ll. 213–217 | "Lin et al. 2013 (TGRS; Poisson equation, global optimisation)"; "these replace thick cloud with another date's pixels" | **verified in full text**, with precision: the fill copies the other date's *gradients* (guidance field v_pq = I_R(p) − I_R(q)), not its pixel values; the level comes from the target's cloud border | eqs. (8)–(10), p. 235 |
| 4 | ev05 l. 17; ev05 l. 100 | "Information cloning assumes land cover barely changes (Lin et al. 2013)"; "No-change assumption stated" | **verified in full text**: "under the assumption that land covers change insignificantly over a short period of time" | abstract p. 232 |
| 5 | ev05 l. 57 | "clones cloud-free patches from other dates via a Poisson equation … Landsat-7 ETM+, simulated clouds" | **verified in full text**, with precision: also real clouds (Taiwan, Los Angeles, Taipei; cloud amounts 36–70%); simulated clouds only for the quantitative tests (Chiayi) | pp. 237–239 |
| 6 | ev05 l. 188 | Opaque cloud filled from the before date "paints the dry road back … It follows from the no-change assumption (Lin 2013; Shen 2019)" | **verified in full text** as support: the paper states it "cannot accurately reconstruct information when land covers change significantly"; change-area RMSE 8.75 vs 5.51 unchanged | Fig. 13, p. 239 |
| 7 | ev10 l. 355 | Reading-list item: "The Poisson seam treatment in full" | **verified in full text**: eqs. (4)–(11); seam between patches uses the mean of the two references' gradients (eq. 10); image-border case drops boundary terms (eq. 11). No solver or tolerance given ("iteratively solved until … converged") | pp. 235, 237 |
| 8 | ev23 ll. 16, 42, 53, 178, 217; method_bench_2/g2_lin_bluerise.py; bench2_numbers.json "G2 Lin blue rise" | A "Lin" blue-rise cloud gate with a threshold (T_blue = 240.8 from Otsu) | **not in paper** (for Lin 2013): Lin 2013 detects cloud with Huang et al. (2010) thermal-band "spectral-temperature" thresholding plus manual refinement; it prints no visible-band test, no threshold value and no Otsu step. The script correctly cites Lin et al. **2015** (ISPRS eq. 15), so this is a naming caution, not an error | p. 233 |
| 9 | — | SSIM constants for patch ranking | **addition**: C1 = (K1 L)², C2 = (K2 L)², L = 255, K1 = K2 = 0.01, α = β = γ = 1, C3 = C2/2; window size not stated | eqs. (1)–(3), p. 234 |
| 10 | — | Reference-patch veto | **addition**: a patch with cloud amount > 80% is not a candidate ("set to 80% for all experiments") | p. 234 |
| 11 | — | Multi-reference vs single | **addition**: multiple references RMSE 6.38 / PSNR 32.07 / SSIM 0.89 vs single 6.55 / 31.84 / 0.80 (Table II); misty reference patches make misty fills (Fig. 10) | pp. 238, 240 |

Corrections: none contradicted; read level of ev10 l. 306 is now full text; note that the "Lin blue rise" gate (G2) is Lin 2015, and Lin 2013 gives no visible-band cloud threshold at all.

## Chen, Chen, Chen, Jia, Cao & Liu 2016 (IEEE TGRS) — chen2016_ihot
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 78–79 | "IHOT (Chen et al. 2016, TGRS) regresses the hazy image on a clear one to remove land-surface signal from the haze map" | **verified in full text**, with a precision on the mechanism: it does not regress one image on the other. It regresses HOT on the band differences hazy − clear (eq. 3), then regresses that fitted THOT on single-date reflectance of both images stacked (eq. 5), and alternates the two | pp. 2683–2684, eqs. 2–5, Fig. 2 |
| 2 | ev21 l. 131; ev21 l. 644; ledger_C l. 12 | Chen, S., Chen, X., Chen, J., Jia, P., Cao, X., & Liu, C. (2016), *IEEE TGRS* 54(5), 2682–2694, DOI 10.1109/TGRS.2015.2504369; read level "Abstract" / "none" | **verified in full text** (authors, volume, issue, pages, DOI). Read level is now full text (13 pp.). "TGRS 9.4" JIF is not checkable from the paper | p. 2682 |
| 3 | ev21 l. 132–133 | HOT "often overestimate[s] haze thickness over bright surfaces"; IHOT uses "a corresponding clear image", iterating regressions so "the land surface information can be removed" | **verified in full text** (abstract wording). The iteration is "among HOT, the reflectance difference … and TOA reflectances of hazy and clear images", not just "between the hazy and clear images" | p. 2682 |
| 4 | ev21 l. 162 | "Fit the blue–red 'clear line' per tile on the *before* image's clear pixels (the IHOT idea)" | **verified in full text** for the clear-line part: the clear line is fitted on haze-free areas "(or clear-sky image if available)", and in the experiment "the clear line was defined from the clear image". This is only IHOT's starting HOT (iHOT^(0)), though: the IHOT step itself is the iterated regression, which D1b does not do. Per-tile fitting is ours | pp. 2683, 2684 |
| 5 | ev21 l. 301–302 | IHOT performed "robustly for hazy images that were acquired at different seasons when using the same reference clear image" | **verified in full text** (abstract). Shown on four 2013–2014 hazy dates against one 2014-03-21 clear date, judged visually | p. 2682; Table II, Fig. 9, pp. 2689–2690 |
| 6 | ev21 l. 316–317 | "Then estimate haze as the residual from that mapping, in the IHOT spirit" | **contradicted**: in IHOT the haze index is the regression's **fitted value** (THOT eq. 2, iHOT eq. 4). The residuals ε and ε′ are what is discarded as error (Appendix A3–A8). A haze map defined as after − f(before) is closer to ΔR, which is THOT's input, not to IHOT | pp. 2683–2684, 2692–2693 |
| 7 | prereg_method_bench l. 74–75 | "the IHOT residual-haze map (Chen 2016 read at abstract level only, so not coded)" | **contradicted** (description): IHOT is not a residual map (see #6). The read level is now full text, so the "not coded" reason no longer holds | pp. 2683–2684 |
| 8 | ev21 l. 589 (fix 6 row) | Residual haze map support: "IHOT (TGRS) … all assume small change" | **verified in full text** for the small-change part: "IHOT may not work that well if there is great land cover changes … change areas account for a small proportion of the whole image, which can be tolerated". The urban pair (2004 vs 2011, large change) is shown to work, visually. The "residual" framing is wrong (#6) | p. 2692; pp. 2686–2687 |
| 9 | ev21 l. 584 (fix 1 row) | HOT/IHOT listed as "Strong" support for adding a HOT distance against a before-image clear line | **verified in full text** for HOT with a clear-image clear line (IHOT's step 0). IHOT's own evidence is visual plus one cirrus correlation and one RMSE table, with no detection accuracy | pp. 2684, 2689–2692 |
| 10 | ju2021 handoff l. 71 | A before-image patch mean as the reference albedo is "an IHOT-like variant" | **verified in full text** only in the loose sense that IHOT uses a clear image of another date as the reference; IHOT does not use patch means | p. 2684 |
| 11 | — | (not in notes) | **addition:** IHOT is a continuous haze-thickness index; the paper gives **no** cloud/haze threshold, so any binary use needs our own cut | pp. 2684–2692 |
| 12 | — | (not in notes) | **addition:** convergence rule \|C^(t) − C^(t−1)\| < 0.001 on corr(THOT, iHOT); correlation 0.946 → about 0.966 over 11 iterations | Fig. 2, p. 2684; Fig. 3(f), p. 2685 |
| 13 | — | (not in notes) | **addition:** bands: all 30 m bands (6 TM, 7 OLI; cirrus excluded). Blue/red-only or RGB is not tested. The OLI weights rest mainly on coastal (+) vs blue (−) | p. 2683; Fig. 8, p. 2689 |
| 14 | — | (not in notes) | **addition:** blue DN = 255 pixels were set as heaviest haze (saturation rule) | pp. 2686–2687 |
| 15 | — | (not in notes) | **addition:** cirrus-band correlation r = 0.9753 (IHOT), 0.8435 (HOT), 0.6240 (BSHTI). DOS RMSE is lowest for IHOT except SWIR 1 (0.0154 vs BSHTI 0.0152) | Fig. 11, p. 2691; Table III, p. 2692 |

Corrections: IHOT's haze map is the regression's fitted value, not a residual (ev21 l. 316–317; prereg_method_bench l. 74–75). D1b is IHOT's starting step only. Read level → full text.

## Zhang & Guindon 2003 (IEEE TGRS) — zhang_guindon2003
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 679; ledger_C l. 30 | Zhang, Y., & Guindon, B. (2003). *IEEE TGRS* 41(5), 1082–1089. https://doi.org/10.1109/TGRS.2003.811817; 8 pages expected; read level "Abstract" | **verified in full text** (8 pages); read level now full text | p. 1082 |
| 2 | ev21 ll. 310–312 | Evaluated HOT "visible-band correction" against "reference or 'benchmark' clear scenes"; radiometry checked on "pseudoinvariant features (dense forest stands)" | **verified in full text**: two benchmark scenes E and F (Table I); 500 dense forest patches, 200 conifer + 300 deciduous, 5 × 5 px | abstract p. 1082; pp. 1084–1085 |
| 3 | ev21 ll. 402–404 | Assessment covered "improvement in interclass separability"; haze strong enough for "significant thematic class confusion", vegetated radiances "at levels normally associated with urban features" | **verified in full text**; the level is differential HOT up to 20 (abstract), and 10–15 is enough for forest/cropland → urban confusion (conclusions) | pp. 1082, 1089 |
| 4 | ev23 l. 119, l. 198; method_bench_2/a2_hot.py docstring | A2 Zhang HOT haze removal "needs a water mask" | **verified in full text** (2003 also requires it): "Water body pixels are excluded from the histogram analysis"; Fig. 1 lists "Water body exclusion" when characterising clear areas; only "land" pixels are adjusted. The 2003 paper gives no water rule (the NIR threshold is from the 2002 paper) | p. 1083 |
| 5 | ev20 l. 52; haze_texture/haze_common.py l. 18 | HOT = B sinθ − R cosθ with the clear line red = k·blue + b fitted by regression on clear pixels, centred on the fit pixels | **verified in full text** (eq. 1; blue–red TM1/TM3 space; "differential HOT" = pixel HOT minus CL HOT). Precision: the paper picks the clear sample by visual inspection and wants it to span the full visible range | eq. (1), p. 1083 |
| 6 | method_bench_2/a2_hot.py step 4 | Correction = per-HOT-level lower-bound difference Δ_b(h), monotone lookup (from the 2002 paper) | **addition**: the 2003 paper describes a *linear* model: the slope of the histogram lower bound vs HOT, "estimated through linear regression, defines the required scale factor" (ΔDN ∝ ΔHOT). Not a contradiction of the 2002-based script; a variant to test | p. 1083 |
| 7 | — | Operating limits | **addition**: clear-scene dispersion ≈ 2 DN sets a lower limit ("deemed clear and not be subjected to haze compensation"); breakdown above ΔHOT 10–20 (p. 1085), effective up to 15–20 (p. 1089) | pp. 1085, 1089 |
| 8 | — | Band needs | **addition**: "any imaging sensor with at least two visible bands" (also MSS green–red); for the classification study it was applied only to TM3 | pp. 1083–1084 |
| 9 | — | Missing table | **addition**: Table II (separability for all band pairs) is cited but not printed in the publisher PDF; only "statistically significant for all cases at the 99% confidence level" is given | p. 1087 |

Corrections: none.

## Li, Hu & Ai 2019 (IEEE GRSL) — li_hu_ai2019
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 21_fundamentals_fixes_literature.md l. 242 | Li, Hu & Ai 2019, *IEEE GRSL* 16:472–476 (confirm in JCR); read = Abstract | **verified in full text** (vol. 16 no. 3, March 2019, pp. 472–476); JIF not stated in the paper; read level → full text | p. 472 |
| 2 | 21_fundamentals_fixes_literature.md ll. 243–245 | States: "haze and cloud are highly related to the illumination component and mainly located in the low frequency of an image"; DCP transmission "is very sensitive to noise"; targets "uneven haze, thick haze, and thin cloud" | **verified in full text** (abstract, verbatim) | p. 472 |
| 3 | 21_fundamentals_fixes_literature.md l. 621 | "the abstract says the code and datasets are public, but no URL was located (a guessed GitHub path gave 404)" | addition: the paper's footnote 1 gives the URL http://www.escience.cn/people/lijiayuan/index.html (not visited in this pass; no downloads) | p. 472 |
| 4 | 21_fundamentals_fixes_literature.md l. 658; ledger_C l. 26 | Ref row: Li, J., Hu, Q., & Ai, M. (2019) … GRSL 16(3), 472–476, DOI 10.1109/LGRS.2018.2874084 | **verified in full text** | p. 472 |
| 5 | — | — | addition: sphere transmission t = 1 − w·min_c(u_c − σ), u = patch mean of I/A, σ = mean of the three channel SDs (eq. 17); S_Ω = 15 × 15, w = 0.95, t0 = 0.1, HF Gaussian high-pass σ = 10; refinement filter (matting vs guided) and the colour-transfer step are **not specified** | pp. 474–475 |
| 6 | — | — | addition: the evidence is no-reference (IL-NIQE 28.52, BRISQUE 25.42) plus colour-drift MAE on 8 Gaofen-1 images (9.56/7.26/7.73 vs DCP 25.39/23.36/23.88); parameters were scanned on the evaluation images; no significance tests | pp. 474–476 |

Corrections: none (ev21 l. 621 can now cite the footnote URL).

## Pan, Xie, Jiang & Yin 2015 (IEEE SPL) — pan2015
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 21_fundamentals_fixes_literature.md l. 70 | "Haze is wavelength-dependent (Chavez 1988). Pan et al. (2015) add a translation term for non-uniform haze in remote sensing." | **contradicted**: the translation term C corrects the dark-channel statistics of remote sensing images (their haze-free dark channel averages 27.28, not ≈ 0); it is not a term for non-uniform haze. Better handling of non-uniform haze is a claimed result. Pan also assumes the **opposite** of the preceding sentence: scattering is "generally assumed to be independent of wavelength", and A is equal in R, G, B | pp. 1807–1808 |
| 2 | 21_fundamentals_fixes_literature.md l. 238 | Pan et al. 2015, *IEEE SPL* 22:1806–1810; "probably below 4, so context"; read = Abstract | **verified in full text** (vol. 22 no. 10, Oct 2015, pp. 1806–1810); JIF not stated in the paper; read level → full text | p. 1806 |
| 3 | 21_fundamentals_fixes_literature.md ll. 239–241 | States: model "deformed by introducing a translation term"; transmission "insensitive to the texture of ground objects"; handling of "nonuniform haze is more satisfactory" | **verified in full text** (abstract wording; support is visual, Figs. 3–4) | pp. 1806, 1808–1809 |
| 4 | 21_fundamentals_fixes_literature.md l. 668; ledger_C l. 7 | Ref row: Pan, X., Xie, F., Jiang, Z., & Yin, J. (2015) … SPL 22(10), 1806–1810, DOI 10.1109/LSP.2015.2432466 | **verified in full text** | p. 1806 |
| 5 | — | — | addition: C = 27 (mean dark channel 27.28 of 5000 haze-free 400 × 400 Google Earth images, 15 × 15 patch); A = A0·[1,1,1] with A0 = mean of He's A; t = (A0 − dark)/(A0 − C) (eq. 12) with **no ω**; guided filter r = 20, ε = 10⁻³; C is sensor-specific (C = 33 ALOS, C = 0 outdoor) | pp. 1807–1809 |
| 6 | — | — | addition: the only numbers are BIQI on two images (He 34.78/38.43, Long 29.95/39.42, Pan 29.73/35.97) and run time; no reference images, no significance tests | p. 1808 |

Corrections: ev21 l. 70: Pan's translation term corrects remote-sensing dark-channel statistics (not non-uniform haze), and Pan assumes wavelength-independent, grey haze, so it should not be cited beside Chavez as support for wavelength dependence.

## Otsu 1979 (IEEE Trans. SMC) — otsu1979
Uses of "Otsu" as a tool name were not listed: production cuts 98/71/71.36, `threshold_otsu` calls, the Otsu thresholds in methodology_v1/v2, data_tool_plan R6/R26/R27, research_questions, preregistrations, evidence 01/07/12/20, and the hagolle2010, canny1986, makarau2014, zhu2012, nielsen2007, qiu2019 and bonafilia2020 handoffs. Only statements about what Otsu's method is or does are checked.

| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 361; ev21 l. 667; ledger_C l. 28 | Otsu, N. (1979). *IEEE Trans. Systems, Man, and Cybernetics* 9(1), 62–66, DOI 10.1109/TSMC.1979.4310076; read level "Metadata" | **verified in full text** (vol. SMC-9, no. 1, January 1979, pp. 62–66; the DOI is not printed, and the code 0018-9472/79/0100-0062 matches). Read level → full text. The JIF note "confirm in JCR" still stands | p. 62 |
| 2 | data_tool_plan l. 306 | "Otsu is only safe on two-peaked histograms (briefing P7)" | **not in paper**. The paper presents a "unimodal peak" histogram (Fig. 2(e)–(h), k* = 32, η* = 0.767) and a broad flat valley as handled cases, and claims no failure mode. It does give η* as a check of "bimodality of the histogram". The caution is reasonable from later literature, but it should not be attributed to Otsu 1979 | pp. 64–66 |
| 3 | question_review l. 523; bruzzone2013 handoff l. 68 | Otsu-style thresholds are label-free ("Fine if Otsu-style"; EM/Bayes is "a reasonable label-free alternative to Otsu cuts") | **verified in full text**: "A nonparametric and unsupervised method"; it uses only the histogram | p. 62 |
| 4 | claim_checks_C l. 37 | In Zhang & Xiao's rule "only Otsu is adaptive" | **verified in full text** for Otsu: k* is recomputed from each histogram (eqs. 18–19) | p. 63 |
| 5 | tiampo2022 handoff l. 28 | "bimodality if max normalised between-class variance > 0.65" (Tiampo's refs [37, 38]) | **verified in full text** for the definition: η = σ_B²/σ_T² is Otsu's normalised between-class variance, offered as a bimodality measure. The 0.65 cut is **not in paper** (Otsu gives no cut-off on η*) | eqs. 12, 17, pp. 63–64 |
| 6 | ev23 l. 16, l. 217–220 | "Otsu on the pooled blue rise gave T_blue = 240.8 DN … a rise that large can only occur where the before→after blue map is badly wrong" | **verified in full text** as consistent with the criterion: Otsu maximises ω0ω1(μ1 − μ0)² (eq. 14), so a far tail can capture the cut. **addition** from the bench-2 tile cache (200 development tiles): N3 blue gains reach 24.4 (offset −1366), the 90th percentile is 5.51, and six tiles exceed 17. The rise is unclipped float, and `threshold_otsu` bins min..max into 256 bins (a library choice, not the paper's integer grey levels). Smoke-tile Otsu gave 19.05 and one dry-run tile 2.63. η* was never computed | p. 63; cache `mask_info["G2"]`; smoke_results.json; dry_run.log |
| 7 | — | (not in notes) | **addition:** exact criterion: k* = argmax σ_B²(k) = [μ_T ω(k) − μ(k)]² / (ω(k)[1 − ω(k)]) over 0 < ω(k) < 1. Equivalent to maximising λ, κ or η, because σ_W² + σ_B² = σ_T² | eqs. 12–19, p. 63 |
| 8 | — | (not in notes) | **addition:** η* ∈ [0, 1] is invariant to affine grey-scale maps, so it can be compared across tiles with different gains. Multithreshold cuts "become less credible as the number of classes … increases". η(k) is unimodal only empirically ("rigorous proof … not yet been obtained") | pp. 64, 66 |
| 9 | — | (not in notes) | **addition:** no accuracy figures, ground truth or comparisons. All examples are 64 × 64 pictures with 16–256 levels; the smallest two-class minority share shown is 0.142 | pp. 64–65 |

Corrections: "Otsu is only safe on two-peaked histograms" is not from Otsu 1979; cite later literature or ev23's own result. The 0.65 bimodality cut is Tiampo's sources', not Otsu's. Read level → full text.

## Bruzzone & Fernández Prieto 2000 (IEEE TGRS) — bruzzone2000
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev21 l. 86 | "Bruzzone & Prieto (2000) choose a change threshold by EM and Bayes rule" | **verified in full text**. EM fits a two-Gaussian mixture (eqs. 2–4), and the Bayes minimum-error threshold is the root of eq. 7, under the pixel-independence assumption | pp. 1172–1173 |
| 2 | ev21 l. 357; ev21 l. 641; ledger_C l. 13 | Bruzzone, L., & Prieto, D. F. (2000). *IEEE TGRS* 38(3), 1171–1182, DOI 10.1109/36.843009 | **verified in full text** (volume, issue, pages, May 2000). The second author's byline is "Diego Fernàndez Prieto"; the running head prints "Bruzzone and Prieto", so "Prieto, D. F." follows IEEE's own indexing. ledger_C's "Fernandez Prieto" also matches the byline. JIF "9.4" not checkable from the paper. Read level → full text | p. 1171 |
| 3 | ev21 l. 358 | Empirical or "manual trial-and-error" thresholds "affect both the accuracy and the reliability" | **verified in full text** (abstract) | p. 1171 |
| 4 | ev21 l. 359–360 | EM estimates the changed and unchanged distributions, and the threshold minimises "the overall change detection error probability"; "An MRF variant adds spatial context" | **verified in full text**, with conditions: minimum error holds under Gaussian class densities and independent pixels. The MRF uses an 8-neighbourhood Gibbs prior weighted by β, solved by ICM; β is set by hand (1.6–1.8 Elba, 1.3 synthetic) | pp. 1171, 1173–1175, 1178 |
| 5 | — | (not in notes) | **addition:** EM initialisation T_n = M_D(1 − α), T_c = M_D(1 + α), α ∈ (0, 1). M_D is printed as [max − min]/2 but called the "middle value". Estimates are stable for α = 0.3–0.7 | p. 1173; Table I, p. 1176 |
| 6 | — | (not in notes) | **addition:** Elba: automatic T̂_o = 82 vs the minimum-error T_o = 84, errors 438 vs 424. MRF β = 1.6 gives 176 errors (missed 282 → 38). Synthetic 0 dB: 940 vs 899; MRF 157 | pp. 1177–1180; Tables II, IV |
| 7 | — | (not in notes) | **addition:** printed inconsistency: p. 1180 text gives the 0 dB minimum-error total as "889"; Table IV and p. 1179 give 899 | pp. 1179–1180 |
| 8 | — | (not in notes) | **addition:** stated limit: the Gaussian model "might turn out to be inappropriate" with many change types or active sensors. Changed-class priors in the tests were only 0.02–0.03, and an absent changed class was never tested | pp. 1176, 1179, 1181 |

Corrections: none.

## Gibson, Vo & Nguyen 2012 (IEEE TIP) — gibson2012
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 10_ring_and_cloud_removal_literature.md l. 232 | The median operation "can avoid halo effects" (Gibson, Vo & Nguyen 2012, IEEE TIP; abstract) | **verified in full text** (abstract quote; mechanism eqs. 14–17; Fig. 2 caption says halos are "not as dominant", i.e. reduced rather than absent) | pp. 662, 664–665 |
| 2 | 10_ring_and_cloud_removal_literature.md ll. 231–232 | "The top-venue edge-aware alternatives avoid the patch altogether: … or the median operation" | **contradicted** for Gibson: the MDCP keeps a patch; it replaces the min over the window with a median over an 11 × 11 window (eq. 10). It avoids the refinement step, not the patch | p. 664 |
| 3 | 10_ring_and_cloud_removal_literature.md l. 296; ledger_A l. 45 | Ref row: Gibson, K. B., Vo, D. T., & Nguyen, T. Q. (2012) … IEEE TIP 21(2), 662–673, DOI 10.1109/TIP.2011.2166968; "TIP 13.7 (2024 value)"; read = Abstract | **verified in full text** (metadata); JIF not checkable from the paper; read level → full text | p. 662 |
| 4 | 10_ring_and_cloud_removal_literature.md ll. 356–357 | To-do: read Gibson et al. 2012 for "Halo-free alternatives in full" | **verified in full text**: the paper does give a halo-reducing dehazer (MDCP, eqs. 10–12): 11 × 11 median, w = 0.95, ε = 0.01, no refinement | pp. 664–665 |
| 5 | claim_checks_A l. 500 | Evidence 10's quote "stays unverified"; "the median-dark-channel parameters are unknown" | **verified in full text** (quote now checked); addition: parameters are 11 × 11 median window, w = 0.95, ε = 0.01; DCP comparison windows 5 × 5 or 7 × 7 | pp. 662–664 |
| 6 | claim_checks_A l. 517 | Berman attributes the median/ellipsoid idea to Gibson & Nguyen 2013 (EURASIP JIVP), not to Gibson, Vo & Nguyen 2012 (TIP) | addition: the 2012 TIP paper itself defines the median dark channel (MDCP, eq. 10), so it is a valid primary source for the median idea (the ellipsoid part is not in it) | p. 664 |
| 7 | — | — | addition (compression): dehazing after decompression ("Post") divides coding noise by t, so variance (σ_n² + σ_r²)/t² (eq. 47), more ringing (eq. 36) and more blocking; Pre ≈ 5 dB higher PSNR on JPEG, every Pre video rated above every Post video. Rule: dehaze before compression. Our Maxar tiles are already compressed, so we are always Post | pp. 666–671 |

Corrections: ev10 l. 231: the median dark channel does not avoid the patch; it uses an 11 × 11 median window and drops the refinement step.

## Ding, Xie, Qiu, Zhang & Shi 2024 (IEEE TGRS) — ding2024_cvae_haze
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev19 l. 61 | Ding et al. "sample several restorations from a conditional VAE and call it an 'uncertainty pipeline'" | **verified in full text** ("In this uncertainty pipeline", abstract; n = 6 samples, p. 6) | pp. 1, 6 |
| 2 | ev19 l. 60 (item 7 heading) | "Per-pixel confidence for thin cloud exists only as learned uncertainty", with Ding as the example | **not in paper**: Ding outputs one fused image; it produces no per-pixel confidence, variance or uncertainty map, and never measures sample spread | pp. 4–7, 13 |
| 3 | ev19 l. 191 | Table row: single hazy/thin-cloud image; several samples fused; change-aware No; "bands not stated in abstract" | **verified in full text**; addition: RGB (T-CLOUD = Landsat 8 RGB), also retrained and tested on single coastal and NIR bands (Table III) | pp. 6–7, 9 |
| 4 | ev19 ll. 226–230 | *IEEE TGRS* 62 (9.4); states deterministic restoration is "highly ill-posed"; cVAE gives multiple restorations, dynamic fusion combines them; outperforms "by a significant margin" | **verified in full text** (quotes from the abstract; "significant" is not statistical: no tests or error bars). JIF 9.4 not checkable from the paper | p. 1; Tables II, IV pp. 8, 11 |
| 5 | ev19 l. 247 | "Learned methods (cVAE, diffusion) give better benchmark scores on RGB, but no thickness map unless built in" | **verified in full text** for Ding (e.g. RS-Haze 39.52 dB vs DCP 17.86 dB; no transmission/thickness output) | Table IV p. 11; Fig. 1 p. 4 |
| 6 | ev19 ll. 410–412 | "Optional uncertainty check (Ding et al. 2024 idea)": spread of the two-date output across fixed gate settings as a predictor of distance to NOAA | **not in paper**: Ding never uses the spread of samples as uncertainty; its simple average of the samples is its worst fusion (28.12 dB vs DFN 29.63, Table VI). The spread check is our idea, inspired by Ding's multiple samples | p. 12 |
| 7 | outputs/preregistration_ida_clear_view.md l. 99 | "spread of the two-date output … as an uncertainty … (after Ding et al. 2024)" | **not in paper** (as row 6) | p. 12 |
| 8 | pilot_scripts/ida_clear_view/s3_score.py ll. 3, 137 | "optional spread check (Ding et al. 2024 idea)" | **not in paper** (as row 6; code comment only, no change needed to code behaviour) | p. 12 |
| 9 | ev19 l. 458; ledger_B l. 7; ledger_C l. 33 | Ref row: Ding, H., Xie, F., Qiu, L., Zhang, X., & Shi, Z. (2024) … IEEE TGRS 62, 1–16, DOI 10.1109/TGRS.2024.3349779 | **verified in full text**; addition: article number 5604616 | p. 1 |
| 10 | claim_checks_C l. 460 | "the open CVF paper by Ding et al. (ACCV 2022) is a different, earlier paper" | **verified in full text**: the TGRS article calls itself "an expanded version of our previous conference paper [32]" (ACCV 2022, pp. 469–485), adding the dynamic fusion network and dehazing | pp. 2, 14 |
| 11 | ev19 l. 502 | Needs GMU login for "data and bands" | addition (now answered): T-CLOUD 2,939 Landsat 8 RGB pairs 16 days apart, 256 × 256; also RICE-I, WHUS2-CR, SateHaze1k, RS-Haze; 5.91 M params, 34.40 GFLOPs; trained on an A100; **no code or weights release stated** | pp. 6–8 |

Corrections: ev19 item 7 / item 10, the preregistration l. 99 and s3_score.py should say the sample-spread uncertainty check is our own idea, inspired by Ding's multiple samples. Ding produces no per-pixel uncertainty and never uses spread.

## He, Sun, Yan & Fu 2022, online 2021 (IEEE TGRS) — `he2021_dabnet`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02_cloud_literature_summary.md l. 47 | "He, Sun, Yan & Fu 2021, DABNet, IEEE TGRS, https://doi.org/10.1109/TGRS.2020.3045474" | **contradicted** (year only): printed as TGRS **vol. 60, 2022**, article 5601216 (16 pp.); "Date of publication January 5, 2021" is the online date. Authors, title and DOI verified | p. 1 |
| 2 | 02_cloud_literature_summary.md l. 47 | Venue "(9.4, core)" | not in paper (JIF is not stated in the article; venue IEEE TGRS verified) | p. 1 |
| 3 | 02_cloud_literature_summary.md l. 47 | AIR-CD: "Cloud only, pixel level, by experts" | verified in full text: "experts manually labeled the position of the cloud in the image pixel by pixel"; "only cloud is labeled in the reference mask"; iterative inspection and correction | p. 8 |
| 4 | 02_cloud_literature_summary.md l. 47 | AIR-CD: "Gaofen-2 PMS, 4 m, NIR + visible, 34 scenes of 7,300 × 6,908 px" | verified in full text (34 full scenes, GF-2 PMS1 and PMS2, Feb–Nov 2017, NIR and visible bands, 4 m, 7300 × 6908 px) | p. 8 |
| 5 | 02_cloud_literature_summary.md l. 47 | Licence "Not found" | verified (no licence in the paper; it says only that the set "will be open to the community") | pp. 2, 8 |
| 6 | 02_cloud_literature_summary.md l. 47 | Size "Not found; a search snippet says only part is uploaded" | not in paper (no size and nothing about partial upload; the paper says the reference cloud mask "has been digitally annotated and available online") | p. 8 |
| 7 | 02_cloud_literature_summary.md l. 47 | URL https://github.com/AICyberTeam/AIR-CD | verified in full text (printed lower-case: https://github.com/aicyberteam/air-cd) | pp. 2, 8 |
| 8 | claim_checks_A l. 720 | Crossref: TGRS vol. 60 (2022), pp. 1–16; 2021 the early-access year; DOI correct | verified in full text; addition: article number 5601216 | p. 1 |
| 9 | claim_checks_A l. 721 | Abstract says the public GF-1 WFV set and "a self-built GF-2 dataset"; whether that GF-2 set is AIR-CD is not confirmed | verified, and now confirmed: the self-built GF-2 set is AIR-CD | pp. 1, 2, 8 |
| 10 | ledger_A.csv l. 67 | "He, Sun, Yan & Fu (2022; online Jan 2021) … IEEE TGRS 60:1-16", DOI 10.1109/TGRS.2020.3045474 | verified in full text | p. 1 |
| 11 | li2022_cloud_shadow_detection_review_ISPRS.md l. 55 | AIR-CD = Gaofen-2, 4 m, 34 scenes (as listed in the Li et al. 2022 review) | verified in full text (consistent with DABNet's own description) | p. 8 |
| 12 | — | (not in notes) Is HRC_WHU used? | addition: **no**. Datasets are GF-1 WFV (108 scenes, 16 m, 70/30) and AIR-CD (25 train / 9 test). MSCFF, the HRC_WHU paper's model, is only a retrained comparison. No number is comparable with our spotter's HRC_WHU F1 | pp. 7–8, 11 |
| 13 | — | (not in notes) input bands | addition: "All models use RGB images as input and only detect clouds, excluding cloud shadows." RGB-only results: AIR-CD MIoU/OA/F1 92.08/97.69/96.95; GF-1 WFV 90.68/96.52/94.85 (single runs, no significance tests) | p. 9; Table VI p. 11 |
| 14 | — | (not in notes) BW loss as printed | addition: ρ_i (eq. 10) **sums** the distances to all boundary pixels, and w_i = softmax(−ρ) + 1 (eq. 11) normalises over all p pixels. Taken literally, almost every weight is ≈ 1 (the extra weights sum to 1 per image). An implementation must reinterpret it, e.g. as the nearest-boundary distance. Table IV BCE → BW: F1 94.39 → 96.95; its BCE row (MIoU 91.26) does not match the BCE model of Tables II–III (89.75) | p. 7; Tables II–IV pp. 9–10 |
| 15 | — | (not in notes) code / weights | addition: neither is released; only the AIR-CD data link. Training: 321² slices, batch 16, Adam (0.9, 0.999, 1e−8), learning rate printed "1e^−6", halved every 10 epochs, 50 epochs | pp. 2, 9 |

Corrections: ev02 l. 47 gives the year as 2021; the printed citation is TGRS 60 (2022), article 5601216 (online 5 Jan 2021). "Only part is uploaded" is not from the paper. claim_checks_A #2's open question is settled: AIR-CD is the self-built GF-2 set.

## Zhu, Li & Shen 2024 (IEEE TGRS) — `zhu2024_gfms_whu`
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | 02_cloud_literature_summary.md l. 48 | GF2MS-WHU / GF1MS-WHU from "Zhu, Li & Shen 2024, IEEE TGRS 62" | verified in full text (vol. 62, 2024, article 5609518) | p. 1 |
| 2 | 02_cloud_literature_summary.md l. 48 | Venue "(9.4, core)" | not in paper (JIF is not stated; venue verified) | p. 1 |
| 3 | 02_cloud_literature_summary.md l. 48 | "Binary cloud. 29 GF-2 and 33 GF-1 images well annotated; the rest unlabelled" | verified in full text (33 labelled + 141 unlabelled GF1-MS; 29 labelled + 163 unlabelled GF2-MS; cloud labelled 255 by Photoshop lasso). Note: p. 10 says 134 unlabelled GF2-MS images were used for fine-tuning, not 163 | p. 2; Table I p. 6; p. 10 |
| 4 | 02_cloud_literature_summary.md l. 48 | "GF-2 MS 4 m; GF-1 PMS 8 m" | verified in full text (both 4-band MS: blue, green, red, NIR) | Table I p. 6; p. 7 |
| 5 | 02_cloud_literature_summary.md l. 48 | Licence "Repo states none. Mirror card: CC-BY-NC-4.0" | not in paper (no licence stated) | — |
| 6 | 02_cloud_literature_summary.md l. 48 | Mirror zips 1.74 GB (GF-2), 0.94 GB (GF-1) | not in paper; the paper gives patch counts instead: "10 428 and 21 917 fully labeled image patches" | p. 2 |
| 7 | 02_cloud_literature_summary.md l. 48 | URL https://github.com/whu-ZSC/GF1-GF2MS-WHU | verified in full text | p. 2 |
| 8 | 02_cloud_literature_summary.md l. 48 | "(Baidu Disk)" | not in paper | — |
| 9 | claim_checks_A l. 726 | Title "Transferring deep models for cloud detection in multisensor images via weakly supervised learning", TGRS 62:1–18, DOI 10.1109/TGRS.2024.3358824; dataset–paper link not from the paper text | verified in full text; the paper itself introduces both datasets ("Two novel datasets, GF1MS-WHU and GF2MS-WHU, are introduced") | pp. 1–2 |
| 10 | claim_checks_A l. 727 | GF1: 33 labelled + 141 unlabelled, 8 m; GF2: 29 labelled + 163 unlabelled, 4 m (DataPort); "paper itself not read" | verified in full text | p. 2; Table I p. 6 |
| 11 | ledger_A.csv l. 68 | "Zhu, Li & Shen (2024) … IEEE TGRS 62:1-18 (GF1MS-WHU/GF2MS-WHU)", DOI | verified in full text; addition: article 5609518; published 14 Feb 2024 | p. 1 |
| 12 | claim_checks_A l. 235 | Evidence 02's "Shen" entries include Zhu, Li & Shen 2024 | verified (cross-reference only; no content claim) | — |
| 13 | — | (not in notes) Is HRC_WHU used? | addition: **no**. Source = GF1-WHU (GF-1 WFV, 108 scenes, 16 m); targets GF1MS-WHU, GF2MS-WHU, WHUS2-CD. No number is comparable with our HRC_WHU F1 | p. 6; Table I p. 6 |
| 14 | — | (not in notes) input bands | addition: all models use blue, green, red **and NIR**; no RGB-only CNN result. The RGB-only spectral mask (WI-HSI) has precision 0.9387, recall 0.4589, F1 0.6077 | p. 8; Table VI p. 12 |
| 15 | — | (not in notes) headline numbers | addition: TransMCD F1 gains over pretrained = 1.23–2.81 (GF1MS), 3.31–5.40 (GF2MS), 5.26–9.63 (WHUS2-CD) points. It stays below training on the target's own labels except in the region-transfer test (0.8999 vs 0.8922; 0.8873 vs 0.8802). Single runs, no significance tests | Tables III–V pp. 9–11; Table X p. 14 |
| 16 | — | (not in notes) code / weights | addition: neither is released; dataset link only | p. 2 |

Corrections: none to the citation or the dataset facts. Licence, mirror sizes and "Baidu Disk" in ev02 l. 48 come from the repository or mirror, not the paper.

## Shendryk, Rist, Ticehurst & Thorburn 2019 (ISPRS JPRS) — shendryk2019
Searched: `grep -rnIEi "shendryk|isprsjprs\.2019\.08\.018|Ticehurst|Thorburn|\bRist\b"` and `planetscope|T-PS|T-S2|6gdybpjnwh` over all of CloudResearch/. Content claims are in ev02 l. 49, claim_checks_A ll. 729–732 and ledger_A l. 69. overnight_plan_2026-10-29.md ll. 48 and 53 are download-status notes only (Shendryk needed a manual/GMU download); they are now out of date: the full text was obtained and read 2026-10-30.

| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev02 l. 49 | Dataset T-PS / T-S2 from "Shendryk et al. 2019 (venue not verified)" | **verified in full text** (first author and year); venue is now verified: ISPRS JPRS 157, 124–136, DOI 10.1016/j.isprsjprs.2019.08.018 | p. 124 |
| 2 | ev02 l. 49 | "Block level (cloud, shadow, land-cover scene labels), per OpenSICDR" | **verified in full text**: scene-level (chip) multi-label classification, "as opposed to the pixel level"; label groups cloud {clear, partly cloudy, cloudy, haze}, shade {unshaded, partly shaded, shaded}, land cover {forest, agriculture, water, bare ground, habitation} | p. 124; Table 1, p. 127 |
| 3 | ev02 l. 49 | "PlanetScope 3 m RGB + NIR (4,943 subscenes)" | **verified in full text** (GSD stated as 3.125 m; 4943 scenes from 246 PlanetScope tiles, 2.5 % random sample per time step) | p. 126 |
| 4 | ev02 l. 49 | "Sentinel-2 (4,993)" | **verified in full text**, with precision: 4993 scenes from 169 Level-1C tiles, trimmed to RGB + NIR and **resampled from 10 m to 3.125 m** | p. 126 |
| 5 | ev02 l. 49 | Chip size "512 × 512" | **contradicted**: T-PS / T-S2 chips are **128 × 128 px (400 × 400 m)**; the Amazon A-PS chips are 256 × 256 px (800 × 800 m); DenseNet/ResNet inputs resampled to 224 × 224. No 512 × 512 anywhere | pp. 126–128 |
| 6 | ev02 l. 49 | Download URL https://data.mendeley.com/datasets/6gdybpjnwh/1 | **not in paper**: the paper gives no data link or data-availability statement for T-PS / T-S2 (A-PS is cited as the Kaggle 2017a competition). The Mendeley link comes from OpenSICDR and remains unverified | all pages; refs p. 135 |
| 7 | ev02 l. 49 | Licence "Not read" | addition: the paper states no data licence. The article itself is open access CC BY-NC-ND 4.0 | p. 124 |
| 8 | claim_checks_A l. 732 | Citation: Shendryk, Rist, Ticehurst & Thorburn (2019), ISPRS JPRS 157:124–136, doi 10.1016/j.isprsjprs.2019.08.018, title as given | **verified in full text** | p. 124 |
| 9 | claim_checks_A l. 732 | Open access CC BY-NC-ND 4.0 | **verified in full text** | p. 124 (footer) |
| 10 | claim_checks_A l. 732 | Label details "(block-level, 4,943/4,993 subscenes) remain unverified" | **verified in full text** (now read; see rows 2–4) | pp. 124, 126 |
| 11 | ledger_A l. 69 | Citation string (authors, title, ISPRS JPRS 157:124-136, DOI); status open_access_download_blocked | **verified in full text** (metadata); status superseded: publisher PDF obtained via GMU and read in full 2026-10-30 | p. 124 |
| 12 | — | — | addition: **inputs are always 6 layers (R, G, B, NIR, NDVI, GNDVI); no RGB-only model or ablation is reported**; authors scope the method to "RGB + NIR" imagery | pp. 127, 134 |
| 13 | — | — | addition: **haze was not learned** — ensemble per-label F2 0.00 (OA 0.95); single models 0.30–0.42; only 13 haze training chips. Shaded F2 0.45 (ensemble). Cloudy 0.90, clear 0.91, partly cloudy 0.73 | Table 5, p. 130; pp. 127, 133 |
| 14 | — | — | addition: chip labels from pixel masks use clear < 10 %, partly 10–90 %, cloudy > 90 % (same rule for shade); ± 5 % change did not alter scores significantly | Table 3, p. 129 |
| 15 | — | — | addition: eqs. (1)–(2) print NDVI = (Red − NIR)/(Red + NIR) and GNDVI = (Green − NIR)/(Green + NIR), the reverse of the usual sign; Fig. 7 shows positive NDVI, so the printed sign is likely a typo — code the standard form | p. 127; Fig. 7, p. 133 |
| 16 | — | — | addition: no trained weights or code released; learning rate and epochs not given (only "Adam, batch 128, exp. decay schedule") | Fig. 1, p. 127; p. 128 |

Corrections: ev02 l. 49 chip size "512 × 512" is wrong (128 × 128 px, 400 × 400 m; A-PS 256 × 256); its Mendeley URL is not from the paper; venue now verified (ISPRS JPRS 157:124–136); ledger_A/todo status "open_access_download_blocked" is superseded.

## Wu, Du & Zhang 2014 (IEEE TGRS) — wu2014_slow_feature_analysis_change_detection_TGRS
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev05 l. 151 | Year "Wu, Du & Zhang (2013)" | **contradicted** (metadata): issue is TGRS 52(5), May **2014**, pp. 2858–2874; 2013 is only the online date ("Date of publication July 3, 2013") | p. 2858 |
| 2 | ev05 l. 151 | "projects both dates onto the most time-invariant features, suppressing differences on unchanged pixels" | **verified in full text** (generalised eigenproblem AW = BWΛ on difference vs pooled covariance, smallest eigenvalues = most invariant) | eqs. 10, 17–20, pp. 2859–2860; abstract p. 2858 |
| 3 | ev05 l. 151 | "includes an iterative variant" | **verified in full text** (ISFA: χ² no-change weights v = P{χ²(N) > T}, weighted mean/variance/A/B, stop when max change in √λ < 10⁻⁶) | eqs. 22–27, p. 2862 |
| 4 | ev05 l. 151 | DOI 10.1109/TGRS.2013.2266673; venue IEEE TGRS; read level "abstract" | DOI and venue **verified in full text**; read level now full text (17 pp.) | p. 2858 |
| 5 | ledger_A l. 75 | "IEEE TGRS 52(5):2858-2874" (2014; online 2013) | **verified in full text** | p. 2858 |
| 6 | — | (not in notes) | addition: the χ² is used only for the iteration weights; the final binary map is two-class k-means on the weighted distance T = Σ SFA²/√λ (eq. 27). With k-means, ISFA kappa was 0.8514 (Taizhou) but 0.5903 (Kunshan), below USFA 0.8235 | pp. 2862, 2867, 2871 |
| 7 | — | (not in notes) | addition: the table maxima are best-threshold kappas ("we adjusted the threshold and only show the highest kappa"). On Kunshan, ISFA (IWD 0.9264) is below IR-MAD (0.9327); SSFA is best (0.9432). Data were 30 m Landsat-7 ETM+ with 6 bands; with one band SFA reduces to a standardised difference | Tables I–II, pp. 2868, 2872; p. 2867 |

Corrections: ev05 l. 151 year should be 2014 (online 2013); read level is now full text.

## Zhang, Peng & Huang 2018 (IEEE GRSL) — zhang2018_object_based_cd_multiscale_uncertainty_GRSL
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev05 l. 154; methodology_v2 l. 830, l. 1498 | Year "Zhang, Peng & Huang (2017)" | **contradicted** (metadata): GRSL 15(1), January **2018**, pp. 13–17; 2017 is the online date ("Date of publication December 13, 2017") | p. 13 |
| 2 | ev05 l. 154 | "multiscale object-based change detection run coarse to fine, on SPOT-5 and GF-1" | **verified in full text** (scales {40, 80, 120} and {30, 60, 100}; uncertain objects refined coarse to fine with SVM; SPOT-5 2.5 m and GF-1 2 m) | pp. 14–16 |
| 3 | ev05 l. 154; methodology_v2 l. 1498 | DOI 10.1109/LGRS.2017.2763182, IEEE GRSL; read level "abstract" | DOI and venue **verified in full text**; read level now full text (5 pp.) | p. 13 |
| 4 | methodology_v2 ll. 829–830 | Cited as indirect support for running DINOv2 again on 2× upsampled crops ("the spatial reading of scale") | **contradicted** (scope): the paper's "scale" is the eCognition segmentation scale parameter (object size) on native-resolution images; it never resamples the images. It supports only the general coarse-to-fine refinement of uncertain areas | pp. 14–15 |
| 5 | methodology_v2 l. 1499 | "Coarse-to-fine designs. Abstracts. (unverified)" | coarse-to-fine **verified in full text**; read level now full text | p. 14 |
| 6 | claim_checks_A l. 855; ledger_A l. 84 | Catalogue facts: title; GRSL 15(1):13–17, 2018; stacked bi-temporal multiscale segmentation, Dempster–Shafer fusion of pixel- and object-based results, multiscale uncertainty analysis with SVM; SPOT-5 and GF-1 | **verified in full text** | pp. 13–16 |
| 7 | — | (not in notes) | addition: uncertainty = Dempster–Shafer-fused belief below T = 0.75 for both classes (eq. 9; "proved to perform best", tuned on the scored scenes); RBF SVM with C, γ by grid search; MRS shape 0.2, compactness 0.7; best OA/kappa 97.59%/0.9006 (DS1) and 97.47%/0.8731 (DS2); no significance tests; method named OB-MSUA in the text and OB-MUSA in the conclusion | eqs. 5–9, p. 15; p. 16; Table I, p. 17 |

Corrections: year 2018 (online 2017) in ev05 l. 154 and methodology_v2 ll. 830, 1498; methodology_v2 §6.4.8 should not cite it as support for upsampled crops (its "scale" is segment size); read level now full text.

## Li, Guo & Elkan 2011 (IEEE TGRS) — li2011_pul
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev02 l. 12; claim_checks_A l. 708 | "PU learning has a remote-sensing precedent in TGRS (Li, Guo & Elkan 2011)" | **verified in full text** (PUL one-class classification of a 0.3 m RGB aerial photograph; not change detection, not flood) | pp. 717–719 |
| 2 | ev02 l. 11–13 | Placed as the precedent for treating SpaceNet 8 "yes or missing" flood labels under cloud as PU, next to the fix "keep cloudy 'missing' labels out of the negatives in the training loss only" | **not in paper** (the fix): PUL keeps unlabelled pixels in training as class s = 0 and corrects the threshold to g(x) > 0.5·c (re-weighting mentioned, not implemented). It requires the selected-completely-at-random assumption, which the authors say is "difficult to satisfy and/or verify"; labels missing under cloud violate it | eqs. 1–4, pp. 718–719; pp. 723–724 |
| 3 | ev19 l. 354 | "Li, Guo & Elkan (2011), PU learning. IEEE TGRS (core)" | **verified in full text** | p. 717 |
| 4 | ev19 l. 360 | "In training, they treat missing labels as unlabelled rather than negative (PU learning)" | **verified in full text** for the general PU idea (unlabelled ≠ negative; traditional BP with 0.5 threshold is "trained on positive and pseudonegative data"). Caveat: in this paper the unlabelled set is 5000 random background pixels, not labels missing for a reason such as cloud | pp. 719, 723 |
| 5 | claim_checks_A l. 708; ledger_A l. 65 | Title, venue TGRS 49(2):717–725, DOI 10.1109/TGRS.2010.2058578 | **verified in full text** (Feb 2011; online 30 Aug 2010) | p. 717 |
| 6 | outputs/research_questions l. 319; claim_checks_A l. 705 | Read level "Metadata only" / "paywalled, not read" | **contradicted** (read level): full text read, 9 pp. | — |
| 7 | — | (not in notes) | addition: c is estimated as the mean of g over held-out labelled positives (eq. 4; 25% hold-out); g was a BP neural network averaged over 10 trainings; PUL beat BSVM by small margins (e.g. urban κ 0.79 vs 0.77, 0.82 vs 0.80; grass scene two tied 0.88) and OCSVM/GDD by large margins, although those two were tuned on the test set; ~2 min vs ~80 min training | p. 719; Tables I–II, pp. 722–723; p. 724 |

Corrections: ev02 §2's drop-from-negatives fix is not Li et al.'s method (PUL is a threshold correction that needs SCAR, which cloud-missing labels break); read level now full text.

## Liu, Huang & Cai 2023 (IEEE TGRS) — liu2023_thick_cloud_removal_land_cover_change_TGRS
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev05 l. 18 | "The methods that cope (Shen 2019; Liu, Huang & Cai 2023; You et al. 2026) add a near-date source to carry the change: auxiliary images, Sentinel-3 or SAR. We have none." | **verified in full text**, with precision: Liu uses a near-target-date **cloud-free** Sentinel-3 OLCI image (~300 m) plus an older clear Sentinel-2 reference; no SAR (the authors argue SAR "suffer[s] from speckle noise") | pp. 3, 6, 17 |
| 2 | ev05 l. 104–105 | Liu, Huang & Cai (2023), *IEEE TGRS*, DOI 10.1109/TGRS.2023.3236106; "Venue: core. Read: abstract; needs GMU." | **verified in full text** (venue, DOI); read level now full text (18 pp.) | p. 1 |
| 3 | ev05 l. 106 | "a near-target-date Sentinel-3 image supplies land-cover change under thick cloud. It helped most where change was distinctive and heterogeneous." | **verified in full text**: "the more heterogeneous and unpredictable the land cover changes, the more significant the contribution of the temporal Sentinel-3 data"; more effective for Paris and Darlag, less for Tianjin and Xi'an | p. 10; Table III, p. 9 |
| 4 | ev05 l. 227 | Reading-list entry: Liu, Huang & Cai 2023, TGRS, DOI | **verified in full text** (addition: vol. 61, article 5601218, 18 pp.; published 11 Jan 2023) | p. 1 |
| 5 | ledger_A l. 80 | Title "Thick cloud removal under land cover changes using multisource satellite imagery and a spatiotemporal attention network", IEEE TGRS 61:1-18 | **verified in full text** (article 5601218, pp. 1–18) | p. 1 |
| 6 | claim_checks_A l. 829 | Target Sentinel-2 with a Sentinel-2 reference and a near-target-date Sentinel-3 image as guidance; spatiotemporal attention network; compared with ResUnet, CRN, STS-CNN, DSen2-CR; vol. 61, article 5601218 | **verified in full text** | pp. 1, 3, 8 |
| 7 | claim_checks_A l. 829 | "also removes thin cloud and cloud shadow" | **verified in full text**, with precision: thin cloud and shadow are not corrected; they are masked and regenerated like thick cloud ("all cloud shadows, thin clouds, and thick clouds were treated as thick clouds") | p. 13 |
| 8 | — | (not in notes) | addition: the "pre-date paste" baseline (our fill-from-before idea) had the worst average RMSE, 528.881 vs 179.923 for STAN (simulated); unseen tiles 1162.141 vs 278.141 (STAN fine-tuned). Networks without S3 "are blind to the temporal changes, so that only homogeneous changes can be generated" | Table III p. 9; Table VIII p. 15; p. 11 |
| 9 | — | (not in notes) | addition: the S3 guide must be cloud-free; the paper never tests a cloudy guide. 47-day S3 gap still beat no-S3 networks (RMSE 211.375). S3-to-S2 resolution gap is ~30× and small parcels were already lost; ours would be ~600× (300 m → 0.5 m). Real-cloud results visual only; no significance tests | Table VI p. 14; pp. 13, 17 |
| 10 | — | (not in notes) | addition: Table VI note gives S2 dates "2020/09/01 and 2020/03/06", inconsistent with Table II (2020/09/17, 2021/03/06); Table II also lists the Paris S3 as 2020/03/06 for the 2021/03/06 target. Printed inconsistencies, not ours | Table II p. 7; Table VI p. 14 |

Corrections: none contradicted; update ev05 read level to full text and note that thin cloud is masked, not corrected (row 7).

## Peter, Cohen, Lucey, Munasinghe, Raney & Brakenridge 2022 (IEEE GRSL) — peter2022_fwdet_gee
| # | Where | Claim | Verdict | Full text (page) |
|---|---|---|---|---|
| 1 | ev19 l. 281 | "Peter et al. (2022). FwDET-GEE. *IEEE GRSL* 19 (confirm in JCR). Search summary of the abstract." | **verified in full text** (GRSL vol. 19, 2022, article 1501005); read level now full text (5 pp.). Published online 28 Oct 2020 | p. 1 |
| 2 | ev19 l. 281–282 | "A GEE port, validated for comparability with FwDET v2.0." | **verified in full text**, with addition: comparability was shown against a hydrodynamic model (iRIC-FaSTMECH, Brazos River May 2016, 10 m, 484 384 px): RMSE 0.62 m (GEE) vs 0.68 m (v2.0); GEE vs v2.0 RMSE 0.70 m. It is a "conceptual replication", not a line-by-line port (cumulative-cost gap fill replaces ArcGIS Cost Allocation; new modified z-score DEM outlier filter) | pp. 1–3 |
| 3 | ev19 l. 473 | Ref row: Peter, B. G., Cohen, S., Lucey, R., et al. (2022) … *IEEE GRSL* 19, 1–5. DOI 10.1109/LGRS.2020.3031190; read "Search summary of abstract" | **verified in full text** (authors, title, volume, DOI; 5 pages). Addition: article number 1501005 is the citable page identifier; read level now full text | p. 1 |
| 4 | ledger_B l. 19; ledger_C l. 35 | Authors Peter, Cohen, Lucey, Munasinghe, Raney & Brakenridge; GRSL 19, 1-5; "5 (expected)" pages | **verified in full text** | p. 1 |
| 5 | ev19 l. 313; l. 316 | "FwDET takes the water surface from the flood edge"; "Accuracy is checked against hydrodynamic models (FwDET)" | **verified in full text** for FwDET-GEE: nearest-boundary-cell elevation; validation only against iRIC HM; ground verification is "a near-term goal" | pp. 1, 3, 5 |
| 6 | ev19 l. 319 | "FwDET … take[s] extents from SAR" | **not in paper** for FwDET-GEE: it accepts extents "from any source"; the examples are a hydrodynamic-model extent (Brazos), a Landsat 8 optical map by DFO (Michigan) and the EnviroAtlas 100-year flood model (Alabama). No SAR extent is used | pp. 2–3 |
| 7 | ev19 l. 70; l. 329 | "FwDET's authors name roofs, highways, overpasses and dikes as error sources" | **not in paper** (Peter et al. do not name these; the statement rests on Cohen 2019, v2.0). Peter et al. name only cumulative-cost "striping artifacts" and DEM outliers | p. 3 |
| 8 | ev19 l. 66, l. 317, l. 322, l. 405 | Depth error "about 0.2–0.5 m"; margin "follows the reported depth errors of 0.18–0.5 m (Cohen et al. 2019; …)" | addition (not a contradiction; Peter is not cited there): on the same 10 m Brazos test FwDET-GEE RMSE is 0.62 m and v2.0 RMSE 0.68 m, and ~9.2% of cells err by > 1 m. The 0.18/0.31 m figures are mean absolute differences, a different metric. A 0.5 m margin is below one RMSE of this method | p. 3 |
| 9 | claim_checks_C l. 460 | "NOAA repository noaa_58788 is Cohen et al. 2022 (Remote Sens.), not Peter et al. 2022" | **not in paper** (cannot be checked from this PDF; the paper's own code archive is Harvard Dataverse doi 10.7910/DVN/JQ4BCN, and the FwDET archive https://sdml.ua.edu/models/fwdet/) | p. 5 |
| 10 | — | (not in notes) | addition for coding: DEM outlier filter = modified z-score (eq. 1) in a 3 × 3 window, threshold 3.5, replace by median of the 8 neighbours; second pass on flood-border pixels; depth smoothed by a low-pass filter (size not stated). Filtering gained only 0.0007 m on flat Brazos. All tests used USGS NED 10 m | pp. 2–3, 5 |

Corrections: none contradicted; update ev19 l. 281 and l. 473 read level to full text, add RMSE 0.62 m (GEE) / 0.68 m (v2.0) to the depth-error range, and note that FwDET-GEE extents in this paper are optical/model, not SAR.

## Summary of contradictions (for the evidence files' owners)
1. **Chen 2016 (IHOT):** the haze index is the regression's fitted value, not a residual (eqs. 2, 4; App. A3–A8, pp. 2683–2684, 2692–2693). This contradicts ev21 ll. 316–317 and prereg_method_bench ll. 74–75. D1b is only IHOT's step 0.
2. **Pan 2015:** the translation term C corrects remote-sensing dark-channel statistics (C = 27 on 0–255, p. 1808), not non-uniform haze. Pan also assumes grey, wavelength-independent airlight, which contradicts ev21 l. 70 where it sits beside Chavez.
3. **Gibson 2012:** the median dark channel uses an 11 × 11 median window and only drops the refinement step; it does not avoid the patch. This contradicts ev10 l. 231.
4. **He et al. (DABNet):** the printed citation is TGRS 60 (2022), article 5601216, online 5 Jan 2021. ev02 l. 47 gives 2021.
5. **Wu, Du & Zhang (SFA):** TGRS 52(5), 2014 (online 2013). ev05 l. 151 gives 2013.
6. **Zhang, Peng & Huang (GRSL):** the year is 2018 (online 2017), not 2017 as in ev05 l. 154 and methodology_v2 ll. 830, 1498. Also, its "multiscale" means segment size on native-resolution images, so it does not support methodology_v2 §6.4.8's upsampled-crop step.
7. **Li, Guo & Elkan 2011 (PUL):** "keep cloudy missing labels out of the negatives" (ev02 §2) is not this paper's method. PUL keeps unlabelled pixels and corrects the threshold (g > 0.5·c), which assumes labels are missing at random.
8. **Shendryk 2019:** chips are 128 × 128 px (400 × 400 m), with 256 × 256 for the Amazon set, not 512 × 512 (ev02 l. 49).

Not in paper (attribution fixes):
- **Ding 2024:** the sample-spread uncertainty idea is ours, not Ding's (ev19 l. 60, ll. 410–412; preregistration_ida_clear_view l. 99; s3_score.py comments).
- **Otsu 1979:** "Otsu is only safe on two-peaked histograms" and the 0.65 bimodality cut are not from Otsu.
- **G2 naming:** the bench's "Lin blue rise" gate (G2) is Lin 2015. Lin 2013 uses thermal-band thresholds plus manual refinement and has no visible-band threshold.

Batch notes:
- Handoffs in this batch are named `<key>_handoff.md` (as requested), unlike earlier batches, which used `<long_name>.md`.
- The staged originals of `li2011_pul` and `zhang2018_object_based_cd_multiscale_uncertainty_GRSL` are still in `papers/_incoming_gmu/`, because the permission check refused `rm`. Their merged copies were verified (original + 1 pages).
