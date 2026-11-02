# Coder handoff: Goldstein et al. (2021), interrater agreement for labels on NOAA post-storm aerial imagery

- **Citation:** Goldstein, E. B., Buscombe, D., Lazarus, E. D., Mohanty, S. D., Rafique, S. N., Anarde, K. A., et al.
  (25 authors) (2021). Labeling poststorm coastal imagery for machine learning: Measurement of interrater agreement.
  *Earth and Space Science* 8(9), e2021EA001896. https://doi.org/10.1029/2021EA001896
- **Copy read:** the published AGU/Wiley typeset version (CC BY), from University of Southampton EPrints,
  https://eprints.soton.ac.uk/452071/1/2021EA001896.pdf. It has 18 pages, numbered "1 of 18" to "18 of 18".
  - The two links we were given both returned HTML bot-check pages, not PDFs: Wiley `pdfdirect` (Cloudflare "Just a
    moment...", 5.5 kB) and the MBLWHOI archive ("Security Check", 3 kB; Unpaywall lists it as the *submitted*
    version). They were not used and the checks were not bypassed.
- **PDF with summary:** `/Users/jusrogers/Masters/papers/goldstein2021_labeling_poststorm_coastal_imagery_ESS-summary.pdf`
- **Validation:** real PDF (1.39 MB, 18 pages by the Read tool and pdfinfo). Title, the 25 authors, vol. 8, issue 9 and
  e-number match Crossref. Discussion, data availability statement and references are present. PASS.
- **Pages read:** 1–16 in full (text, equation, Tables 1–4, figure captions). References (pp. 16–18) were scanned for the
  data and code citations. Tables 2–3 were checked on the rendered pp. 7–8.
- **Data:** labels on Zenodo (v1.4 cited): https://doi.org/10.5281/zenodo.5172799 = https://zenodo.org/records/5172799.
  **Not downloaded.**
  - Labeller code: "Coastal image labeler" v2.1, https://doi.org/10.5281/zenodo.4973582.
  - Analysis code (R, `irr` package): https://doi.org/10.5281/zenodo.5212158.
  - ERI imagery: https://storms.ngs.noaa.gov. `psi-collect` (JOSS 2020) downloads it.
- **Supports (evidence 19):** plan item 9 (count the label gap on cloudy roads from NOAA photos, as descriptive
  evidence) and the Q1 note that NOAA photos are a reference image, not a label. It also supplies the method for any
  future human labelling of Ida NOAA photos. It supports no image-processing module.

## What the NOAA ERI labels are (pp. 3–6, Tables 1–2)
- **Imagery:** NOAA NGS Emergency Response Imagery, JPEG versions.
  - Florence 2018: flight 20180917a, coastal North Carolina.
  - Michael 2018: flight 20181011a, Florida Panhandle.
  - Isaias 2020: flight 20200804a, North and South Carolina.
- **Selection:** the 1,600 images were picked by an **active-learning washover detector**: a VGG16 on ImageNet weights,
  one FC layer, 50% dropout, trained on 388 earlier Florence labels (F1 0.92 on 140 Michael test images). The most
  uncertain images were sent to labellers, so the set is **not random** and is biased towards ambiguous coast scenes
  (p. 4).
- **Unit:** the **whole image**. Labels are image-level only; there are no pixel masks, polygons or bounding boxes.
- **Questions (Table 1):**
  - Quick "all water" button.
  - Development: "Undeveloped/Developed", changed to "Buildings/No buildings" in Experiments 2–3.
  - Washover: "Visible washover (active in this storm)".
  - Damage: infrastructure, changed to buildings.
  - Impact type checkboxes: swash, collision, overwash, inundation (Sallenger 2000 scale; optional, and skipping it was
    coded "no impact").
  - Terrain checkboxes: sandy coastline, marsh, river → estuary/bay, inland.
  - There is **no road or flood-water question**. "Inundation" means the Sallenger regime (a barrier island fully
    submerged), not street flooding.
- **Experiments:**
  - Experiment 1: 13 labellers, 900 images, 4,500 labels, no manual. 300 of these images were labelled by all 7
    labellers.
  - Experiment 2: 12 labellers, 600 images, 1,700 labels, 2–4 per image, refined questions plus a manual.
  - Experiment 3: 4 labellers, 25 Experiment-2 images quartered into 100 tiles.
  - Totals: 1,600 images, 6,600 labels, 22 coastal scientists.
  - Non-expert pilot: 4 people labelled 100 Experiment-2 images.
- **Not reconciled:** "we released all the labels" (p. 14). Users must choose a rule: majority vote, relabel or drop,
  a loss-aware model, or "at least one yes", which they used for washover.

## Metric (p. 6–7)
- Percent agreement, plus Krippendorff's alpha: `α = 1 − D_o / D_e`. D_o is the observed disagreement and D_e the
  disagreement expected by chance, both from coincidence matrices.
- Multi-select questions were split into binary questions. Computed with R `irr`.
- Interpretation cited: Krippendorff's > 0.8 ideal and 0.67–0.8 for tentative conclusions; Landis & Koch's bands are "arbitrary"
  (p. 10).

## Results to compare against (Tables 3–4; numbers as printed)
- **Experiment 1 → 2 (percent / alpha):**

  | Question | Experiment 1 | Experiment 2 |
  |---|---|---|
  | All water | 95 / 0.82 | 98 / 0.91 |
  | Buildings | 81 / 0.78 | 92 / 0.89 |
  | Damage | 78 / 0.48 | 88 / 0.75 |
  | Washover | 66 / 0.51 | 64 / 0.47 |
  | Inundation | 88 / 0.09 | 86 / 0.13 |
  | Swash | 51 / 0.25 | 59 / 0.14 |
  | Sandy coastline | 89 / 0.87 | 95 / 0.89 |

- **Experiment 3, full 25 → 100 quarters:** washover 64/0.44 → 86/0.61; overwash 0.33 → 0.52; all water 0.75 → 0.89;
  inundation 92/0.69 → 88/0.20; damage 0.86 → 0.75. "We admit that this is a small experiment" (p. 8).
- **Prevalence (Table 2):** "all water" had at least one yes in 10% (Experiment 1), 11% (Experiment 2) and 42%
  (quarters) of images.
- No confidence intervals or significance tests are given.

## Key quotes and limits
- "errors in input label data become irreducible model errors" (p. 2).
- "detecting visible features ... had higher agreement than inferring the physical processes" (p. 12).
- "it is difficult to determine from an aerial image if dunes were just recently eroded, or if a region was inundated in
  the past several days" (p. 12).
- "even perfect agreement is different from an actual ground-truth" (p. 14). They also warn of "false positives where
  labelers all agree on the wrong label" for process labels (p. 14).
- "a small sliver of land in the corner of an image with water can be missed" (p. 11).
- The non-expert pilot is "not possible to be conclusive" (p. 16).

## How to apply to our pipeline
- **Validation and labels, not a module.** It does not touch `sn8_clouds.py`, `sn8_cloudsym.py`, `sn8_cloudspot.py`,
  `sn8_texture.py` or `sn8_glcm.py`.
- **The released labels cannot score SpaceNet 8 / Ida.** They are image-level, from other storms (Florence, Michael,
  Isaias), coast-focused, and have no road or flood question. Under the "published labels, unmodified" rule they could
  only serve as a sanity set, for example for an "all water" image-level check on ERI JPEGs. Keep it as data
  attribution.
- **Protocol if we ever label Ida NOAA ERI photos** (for example the plan-item-9 label-gap count on cloudy roads):
  - Ask **visible-feature** questions per road segment ("standing water on road surface: yes/no/can't see"), not process
    questions ("was flooded").
  - Write a short manual with example crops.
  - Use **small crops** around each road so no zooming is needed. Their quarters raised washover alpha from 0.44 to
    0.61.
  - Use ≥ 2 raters per segment and keep the raw votes. Report percent agreement and Krippendorff's alpha (Python:
    `krippendorff` package, nominal).
  - Pre-register the reconciliation rule.
  - Record the ERI flight ID and time against the Maxar pass, because labels say "visible in this photo", not "at
    peak".
- **Feasibility with 0.5 m RGB uint8, one clear pre-storm date, no NIR/SWIR/SAR:**
  - Fully feasible. The method needs only RGB photos and people.
  - The cost is human time, and Justin must decide whether our own labels are allowed. They would count as "own labels"
    under the labelled-data rule.
