# Coder handoff: Kaufman (1984), Atmospheric effect on spatial resolution of surface imagery

- **Citation:** Kaufman, Y. J. (1984). Atmospheric effect on spatial resolution of surface imagery. *Applied Optics* 23(19), 3400–3408. https://doi.org/10.1364/AO.23.003400
- **PDF:** `/Users/jusrogers/Masters/papers/kaufman1984_atmospheric_effect_spatial_resolution_surface_imagery_AO-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** publisher (Optica) PDF downloaded through Justin's GMU session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out).
- **Validation:** real PDF (`file`: PDF document; 1.1 MB). Read tool and pdfinfo: 9 pages = published range 3400–3408. Page-1 title and sole author match; the DOI is not printed on this 1984 scan, but the PDF metadata title/author and the running footer "APPLIED OPTICS / Vol. 23, No. 19 / 1 October 1984" with p. 3400 match the citation. §V Conclusions (pp. 3406–3407), appendices A–B and 32 references (pp. 3407–3408) present. PASS.
- **Read:** pp. 3400–3408 in full (page images), including figures, tables, appendices and references.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the journal's. NASA Goddard author (agency).

## 1. Model, step by step
1. **Radiance split** (eq. 1, p. 3401): `L = L0 + Ls + LD`. L0 = path radiance (independent of surface; "causes a loss of contrast"); Ls = surface radiance directly transmitted (the signal); LD = radiance reflected by the surface **elsewhere** and scattered into the field of view (adjacency effect), which "diffuses radiation between fields, thus reducing the apparent spatial resolution".
2. **Transfer fraction ξ** (eqs. 2–3, p. 3401): for a square field of edge x and reflectance ρf in a background ρB, `Lf(x) = Lu(ρB)·ξ(x) + Lu(ρf)·[1 − ξ(x)]`, so `ξ(x) = [Lf(x) − Lu(ρf)] / [Lu(ρB) − Lu(ρf)]`. With `L ≈ L0 + Tρ` (eq. 4): `Lf(x) ≈ L0 + T[ξ(x)ρB + (1 − ξ(x))ρf]` (eq. 5).
3. **Empirical ξ** (eq. 6, p. 3402), valid for τA 0–0.7, 400–1600 nm, abs. error < 0.04:
   `ξ(x) = 0.7 τR exp(−x / 2H_R) + τA [0.37 exp(−x / H_A) + 0.32 exp(−x / 6H_A)]`
   τR Rayleigh optical thickness, τA aerosol optical thickness, H_R and H_A molecular and aerosol scale heights (H_A = 1 km in Fig. 3). **The length scales of the adjacency kernel are H_A to 6H_A, i.e. kilometres.**
4. **Atmospheric noise** (p. 3402–3403): background variability makes `NEΔρ = σ(Lf)/T = ξ σ(ρB)` and `signal/noise = [1 − ξ] ρ̄f / (ξ σ(ρB))` (eq. 7); for average haze ξ ≈ 0.16 so S/N ≈ 5 ρ̄f/σ(ρB).
5. **Atmospheric MTF** (eq. 8, p. 3403): `M(k) = F[L^N(x)] / F[ρ(x)]`. Empirical normalised form (eq. 9, valid 470–1650 nm, error ΔM < 0.04):
   `M^N(k) = 1 − 0.5 τR [1 − exp(−2.5 k H_R)] − 0.7 λ^(−0.2) τA [1 − exp(−1.3 k H_A)]` (λ in µm; the printed eq. shows `exp(1.3kH_A)`, which must be a sign typo since M^N(0) = 1 is required).
   **Shape:** M^N = 1 at k = 0 and falls to a **flat plateau** `1 − 0.5τR − 0.7λ^(−0.2)τA` for k above about 1 cycle/km (Figs. 4–6, p. 3404). All spatial frequencies finer than about 1 km are attenuated by the **same** factor.
6. **Absolute MTF** (eq. 10, Appendix A): `M(0) = F_D [exp(−τ0) + t] / (π F0 μ0)`; system MTF = sensor MTF × atmospheric MTF (p. 3404). Simulation of an image (eq. 13): `L(x,y) = L0 + F⁻¹{M*(k) F⁺[ρ(x,y)]} F0 μ0`.
7. **Uniform-surface correction** (Appendix B, p. 3407): dividing by M(0) gives `M*(k) = M(k)/M(0)` (eq. B5). It "reconstructs the contrasts between very large fields" but "only partially corrects the contrasts of fields" of 100–2000 m (p. 3405).

## 2. Inputs, outputs, data needs
- Inputs to the formulas: τR, τA, H_R, H_A, λ, solar zenith; sensor MTF (from square-wave response, eq. 14).
- Simulations: λ = 550 nm, τA = 0.5 ("common atmospheric haziness in the Eastern United States during the summer", p. 3404), solar zenith 20°, power-law aerosol size distribution. Monte Carlo reference: Pearce 1977.
- Nadir view only (p. 3401).

## 3. Quantitative results to compare against
- **Table II (p. 3405), resolution (m) at MTF thresholds 0.35 / 0.5:**

| Sensor | Sensor only | Sensor + atmosphere | Sensor + uniform-surface correction |
|---|---|---|---|
| MSS | 70 / 90 | 170 / 790 | 95 / 140 |
| TM | 30 / 40 | **100** / **830** | 50 / 85 |
| Advanced (15 m) | 15 / 20 | 50 / 710 | 22 / 45 |

  The abstract's "30 m … reduce[d] to 100 m" is the **0.35 threshold** row for τA = 0.5, 550 nm. At the 0.5 threshold the same atmosphere gives 830 m, because the plateau of the combined MTF sits near 0.5 (Fig. 9).
- **Transfer fraction vs field size** (Fig. 12, p. 3406): for fields > 200 m the atmospheric transfer fraction exceeds the MSS and TM sensor fractions; for fields smaller than the pixel the sensor fraction "increases sharply toward 1, thus exceeding the atmospheric value".
- **Noise:** NEΔρ ≈ 0.003 visible, 0.01 near IR for average haze; atmospheric S/N 8–130 (p. 3407). The body text gives 0.03 for band 4 at τA = 0.4 (p. 3403), which conflicts with the 0.003 in the conclusion and with Fig. 3's scale; 0.003 looks right.
- Table I (p. 3403): ρ̄f/σ(ρB) from a Landsat 3 scene, 8/20/82, e.g. Washington DC band 4: 7.6 (0.34 km box) to 13.0 (3 km).

## 4. Stated limitations
- Nadir view only; empirical fits to one Monte Carlo study; τA ≤ 0.7.
- Corrections that assume a uniform surface cannot restore field contrast at 100–2000 m; "atmospheric corrections must be based on the nonuniform surface pattern" (p. 3405).

## 5. How to apply to our pipeline (0.5 m Maxar, 64 m windows)
- **Correction to our gap-5 argument.** We wrote that "the adjacency blur (Kaufman) removes fine texture rather than scaling it". Kaufman's model says the opposite at our scales: the adjacency kernel has km length scales (H_A, 6H_A; eq. 6) and the atmospheric MTF is **flat** above about 1 cycle/km (eq. 9, Figs. 4–6). Every frequency we measure texture at (0.5–64 m, i.e. 15–2000 cycles/km) sits on the plateau, so the atmosphere **scales** fine texture by one constant (plus the adjacency adds a smooth, nearly uniform background from the surroundings). That supports the affine model `t·J + A(1−t)` inside a window and the invariance argument for LBP / normalised gradients (gap 5). Fine-texture loss must then come from the other two causes we listed (8-bit quantisation, non-linear stretch) or from sensor MTF, not from the adjacency effect.
- **"30 m → 100 m" is a threshold effect, not a blur width.** Cite it as: at τA = 0.5, 550 nm, the TM system MTF falls below 0.35 at 100 m because the whole high-frequency plateau is lowered (Table II). Do not convert it into a blur kernel for 0.5 m data.
- **Usable formulas (numpy):**
  - Plateau gain per band: `g = 1 − 0.5*tauR − 0.7*lam_um**-0.2*tauA`. For Ida, τA would come from an aerosol product (not in hand); as an arm, fit g per window as the ratio of after/before local std on invariant pixels (the paper's model predicts one g per window, flat across scales). Test: compare g at 2, 8, 32 m scales (Laplacian-pyramid band energy ratios). Flat → Kaufman holds; rising with scale → something else is blurring.
  - Adjacency background: `ξ(x)` with x = distance; at x ≪ H_A, ξ ≈ 0.7τR + 0.69τA (constant). So within a tile the adjacency term is ~uniform and folds into A(1−t). Near a cloud edge it is not: a bright cloud as "background" adds radiance with km-scale decay. That is consistent with the cloud-edge brightening ring (evidence 09) extending far from the cloud, and gives a functional form to try: `ring(d) ≈ a·[0.37 exp(−d/H) + 0.32 exp(−d/6H)]` with H fitted.
- **Evidence weight:** Applied Optics, NASA GSFC author, single-scattering-era Monte Carlo fits; context and physics, not a VHR validation.

## 6. Key quotes
- "Photons that were reflected by the surface out of the field of view are scattered by the atmosphere into the field of view (adjacency effect). As a result the apparent field of view is increased." (abstract, p. 3400)
- "It is found that the 30-m resolution of the Landsat Thematic Mapper (TM) is reduce to 100 m by a hazy atmosphere." (abstract, p. 3400; "reduce" sic)
- "L0 … is independent of surface reflectance and causes a loss of contrast on the satellite image" (p. 3401).
- "Although this correction reconstructs the contrasts between very large fields, it only partially corrects the contrasts of fields with more common sizes of 100–2000-m diam." (p. 3405)
- "for fields >200 m in diameter, the atmospheric transfer fraction is greater than that of the Landsat MSS sensor and that of the Landsat TM sensor" (pp. 3406–3407).
