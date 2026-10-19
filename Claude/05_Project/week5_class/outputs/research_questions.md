# Candidate Research Questions (Research Question Agent)

Source: `inputs/problem.md` and the human notes/references in the prompt packet only. No other evidence used. Novelty is **not** claimed for any candidate: the packet lists references but supplies no content from them, so overlap cannot be assessed (MISSING EVIDENCE).

Shared setup assumed by all candidates: Landsat-8 band 8 panchromatic at 15 m resolution (MuRA-T, ~24 monthly steps, 2017–2020), Sentinel-1 C-band GRD co-registered to the same grid, SpaceNet 7 / MUDS monthly building footprints as independent reference labels, 10–20 AOIs with whole AOIs held out for testing.

---

## Rank 1 — Does adding SAR to panchromatic imagery improve monthly detection of new buildings at 15 m resolution?

- **Research question:** In held-out AOIs, does fusing Sentinel-1 backscatter with Landsat-8 panchromatic time series at 15 m pixels detect newly appearing buildings (as dated by SpaceNet 7 first-appearance month) more accurately than panchromatic imagery alone?
- **Candidate hypothesis:** Pan+SAR fusion yields a higher F1 score for "new-building pixel/cell in month *t*" than pan-only, because SAR is unaffected by cloud gaps (missing MuRA-T months) and responds to built structure geometry.
- **Expected observable evidence:** Higher F1 (and higher recall at matched precision) for the fusion model across held-out AOIs; the gain concentrated in AOIs/months with missing or cloudy optical scenes.
- **Plausible data:** MuRA-T band 8 + cloud mask; Sentinel-1 GRD (VV/VH where available) from Earth Engine or Planetary Computer; SpaceNet 7 footprints rasterised to the 15 m grid as fraction of each pixel newly covered.
- **Plausible method:** Per-pixel or small-patch temporal classifier (e.g., gradient boosting or a light temporal CNN) trained on pan-only vs pan+SAR features; leave-AOI-out cross-validation; paired comparison per AOI.
- **Main threat to validity:** Scale mismatch — buildings traced on ~4 m imagery are often smaller than one 15 m pixel, so labels must be thresholded/aggregated, and the threshold choice can drive the result. Secondary: Sentinel-1 coverage varies by AOI (TO VERIFY), which could confound "SAR helps" with "SAR coverage is good here."
- **Weakening/refuting result:** No improvement in F1 for fusion over pan-only across held-out AOIs (paired test across AOIs not significant), or gains that vanish when restricted to months with clear optical scenes.
- **Criteria notes:** Importance high (all-weather monitoring); testability high; data feasibility moderate (SAR co-registration is unfinished work); spatial relevance high; tractable in eight weeks if AOI count stays near 10.

## Rank 2 — Does SAR backscatter change precede the labelled appearance of new buildings?

- **Research question:** For buildings first appearing in SpaceNet 7 in month *t*, does Sentinel-1 backscatter in the containing 15 m pixels change significantly in months before *t*, and by how many months?
- **Candidate hypothesis:** SAR backscatter change leads the SpaceNet 7 first-appearance month by at least one month on average, consistent with the packet's caveat that labels mark visibility (closer to completion) rather than construction start.
- **Expected observable evidence:** A positive median lead time (months) between the SAR change-point and the label month in new-building pixels, with no comparable change-point distribution in stable (never-built) control pixels.
- **Plausible data:** Sentinel-1 GRD monthly composites; SpaceNet 7 building IDs with first-appearance month; stable-pixel controls drawn from the same AOIs.
- **Plausible method:** Per-pixel change-point detection on backscatter time series (e.g., CUSUM or a Bayesian change-point model); compare lead-time distributions against controls; repeat for pan band 8 to compare SAR vs optical lead.
- **Main threat to validity:** Speckle and variable orbit/polarisation per AOI may create false change-points; ~24 months limits detection of long construction phases near series edges.
- **Weakening/refuting result:** Median lead time of zero or negative, or a lead-time distribution indistinguishable from the control-pixel distribution.
- **Criteria notes:** Scientifically interesting (timing of construction phases); fully testable with independent labels; no claim that this is new — the Lee et al. (2026) SAR construction-type paper may overlap, but its content is not in the packet (MISSING EVIDENCE).

## Rank 3 — Does a tool-calling agent make fewer false change claims than a direct multimodal model?

- **Research question:** When asked "where and when did new buildings appear?" for a held-out AOI, does an agentic workflow (LLM that calls deterministic change-detection tools on the pan/SAR stack) produce fewer unsupported change claims than a multimodal LLM answering directly from the imagery?
- **Candidate hypothesis:** The tool-calling agent achieves higher precision of reported change events (claims verified against SpaceNet 7) than the direct-answer baseline, at similar recall.
- **Expected observable evidence:** Higher event-level precision and lower false-claim count per AOI for the agent; agent errors traceable to tool outputs rather than invented changes.
- **Plausible data:** Same stack as Rank 1; SpaceNet 7 labels converted to event lists (location cell + month).
- **Plausible method:** Fixed prompt set per AOI; score each claimed event against labels at a defined spatial tolerance (e.g., 3×3 pixels at 15 m resolution) and temporal tolerance (±1 month).
- **Main threat to validity:** Most multimodal models are not built for 15 m panchromatic or SAR inputs, so a weak baseline could inflate the agent's advantage; LLM outputs are stochastic and model versions change.
- **Weakening/refuting result:** Equal or lower precision for the agent, or precision gains entirely explained by the agent reporting far fewer events (recall collapse).
- **Criteria notes:** Most directly "Agentic GeoAI"; relevant references (Zuo et al., 2026; Earth-Agent; Kao et al., 2026; TEOChat) are listed but their findings are not supplied (MISSING EVIDENCE), so novelty is unassessed. Tractability is the main risk: baseline selection and prompt design could consume the eight-week window.

## Rank 4 — What is the smallest new-building footprint reliably detectable at 15 m resolution?

- **Research question:** How does detection probability of a new building (or cluster) vary with its footprint area relative to a 15 m pixel (225 m²), for pan-only, SAR-only and fused inputs?
- **Candidate hypothesis:** Detection probability rises monotonically with footprint area, and the area at which detection recall reaches 0.5 is lower for fused input than for either sensor alone.
- **Expected observable evidence:** Logistic detection curves (recall vs footprint area) per input type, with the fused curve shifted toward smaller areas.
- **Plausible data:** SpaceNet 7 polygon areas (from ~4 m tracing) linked to detector outputs from Rank 1.
- **Plausible method:** Logistic regression of detected/not-detected on footprint area, sensor type and AOI random effect.
- **Main threat to validity:** Area is confounded with building density and neighbourhood context; label positional error relative to the 15 m grid.
- **Weakening/refuting result:** Flat detection curves (no area dependence) or overlapping curves across input types.
- **Criteria notes:** Useful practical result (sets limits of 15 m pixels for urban change); depends on Rank 1 outputs, so best as a secondary analysis in the same paper.

---

## Ranking rationale

1. **Rank 1** best fits the boundary conditions: clear spatial component, public data, an independent reference, a falsifiable comparison, and leave-AOI-out validation built in.
2. **Rank 2** is equally testable and uses the label-timing caveat as a hypothesis rather than a weakness; ranked second because SAR quality per AOI is unverified.
3. **Rank 3** is closest to the course theme but carries the highest tractability and baseline-fairness risk.
4. **Rank 4** is low-risk but derivative of Rank 1; recommended as a secondary analysis.

A combined paper could pair Rank 1 (primary) with Rank 4 (secondary), with Rank 3 as the agentic layer if time allows.

## Missing evidence / to verify

- MuRA-T download, band 8 integrity and claimed sub-pixel alignment (stated by a non-peer-reviewed preprint).
- Sentinel-1 scene counts, orbit direction and polarisations per AOI (marked TO VERIFY in the notes).
- Number of new buildings per AOI (needed to pick the 10–20 AOIs).
- Content of the listed references: none is summarised in the packet, so no novelty or prior-result claims are made.
- Label-to-pixel conversion rule (threshold on fraction of a 15 m pixel covered) is undecided and must be fixed before testing.
