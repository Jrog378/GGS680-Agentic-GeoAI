# Coder handoff: Hänsch et al. 2022, SpaceNet 8 (CVPRW 2022, EarthVision)

**Citation:** Hänsch, R., Arndt, J., Lunga, D., Gibb, M., Pedelose, T., Boedihardjo, A., Petrie, D., & Bacastow, T. M.
(2022). SpaceNet 8 – The detection of flooded roads and buildings. *CVPRW 2022*, 1471–1479.
doi:10.1109/CVPRW56347.2022.00153. **Copy:** CVF Open Access, 9 pp = 1471–1479 (OpenAlex lists it closed; the CVF copy
is open). PDF: `/Users/jusrogers/Masters/papers/hansch2022_spacenet8_flooded_roads_buildings_CVPRW-summary.pdf` (page 1 = AI
summary). **Read:** pp. 1–9. Affiliations DLR, ORNL, Maxar (company paper). Claude, 2026-10-29.

## Label protocol (p. 3) — the facts our tests depend on
- Pre-event image: analysts draw building footprints and road centrelines (road type, paved/unpaved, lanes).
- Post-event image: attribute **road segments** "flooded" if "visibly covered with water or rubble"; **buildings**
  "flooded" if flood water is in immediate proximity (proxy).
- Cloud: "analysts were instructed to only attribute what was visible, and not make any assumptions where features
  could not be seen"; Sect. 5: "if an area is not visible in the post-event image due to cloud cover, the flood
  attribute is omitted" (p. 6). In the released labels an omitted attribute is indistinguishable from "not flooded"
  (our evidence 16 reading; the paper does not spell out the encoding).
- Imagery: Maxar Open Data pan-sharpened RGB 0.3–0.8 m, CC BY-NC 4.0 (p. 2). Tiles 1300×1300 px on the **pre** grid;
  post tiles cover the same ground at a different pixel size (p. 4). Pre/post differ in look angle and light (Figs. 1, 3).
- AOIs: Germany (July 2021), Louisiana (Ida, late Aug 2021), hidden test AOI. ~850 km², ~32k buildings, ~1,300 km
  roads; ~13 % / 15 % flooded.

## Baseline + metric (pp. 4–6)
- Foundation net: U-Net/ResNet34, road speed (7 bins + binary) and buildings; L = 0.5·BCE + 0.5·(0.75·focal +
  0.25·Dice). Flood net: Siamese U-Net/ResNet34 on pre/post, 4-class mask; Adam 1e-4, 50 epochs, batch 2.
- Vectorisation: majority vote of flood pixels per feature; **no prediction → non-flooded**.
- Scoring: 3×3 IoU matrix (flooded / non-flooded / no building); APLS on traversable and non-traversable networks.
- Results: hidden-AOI APLS 0.12, mean IoU 0.42; with half the hidden AOI in training 0.45 / 0.66; trained on two AOIs
  and tested on Germany "breaks down". The network reproduces the cloud omission (Fig. 5 last row, p. 6).

## How to apply to our pipeline / Ida test
- **Label-gap finding (Revision 1 item 8):** cite p. 3 and p. 6 directly: the labels omit flood status under cloud by
  design, and a model trained on them learns to omit it too. Our NOAA count of "cloudy roads that look flooded"
  measures what that rule hides.
- **"Rubble" counts as flooded** in SpaceNet 8. When the frozen detector is run on NOAA images (Revision 1 item 1) or
  roads are judged visually in NOAA, use the same definition (water **or** rubble) so the comparison matches the label
  semantics; record water vs rubble separately.
- **Grids:** labels live on the pre-image grid; post tiles have a different GSD. Any NOAA reprojection (data-prep
  step 3) must target the same grid our post tiles were resampled to, and the reported shift is relative to that.
- **Feasibility:** directly applicable (our data).
