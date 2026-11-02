# Checks run before the refinement pass (2026-10-23, development data only)

The Stage 2 critic asked for three cheap checks before refining the questions. Our own measurements follow; the
scripts are in the session scratchpad (`cloudresearch/mask_bias.py`).

## 1. Is the dark-rise cloud mask biased by flood state?
Concern (critic, inference): under the same haze, floodwater might raise a road's dark floor less, so flooded
roads would be flagged as cloud less often, and the low flooded share under cloud could then be the mask's doing.

Test: 769 clear roads on 190 development tiles (production-assessable, < 5% of the strip under dark rise; 433
flooded, 336 dry). A uniform synthetic haze I*t + A*(1 - t) (airlight A = 220) was added to each after image at
transmission t from 1.0 (none) to 0.5 (thick), and the dark-rise mask recomputed. "Flagged" = >= 20% of the strip
under the mask (production's road rule). Differences are flooded minus dry, with 95% intervals from resampling tiles.

| haze (t) | flagged, dry | flagged, flooded | flooded - dry | 95% CI |
|---|---|---|---|---|
| 0.9 (thin) | 4.8% | 4.8% | +0.1 | -3.9 to +4.4 |
| 0.8 | 15.5% | 15.2% | -0.2 | -7.1 to +6.8 |
| 0.7 | 36.3% | 45.5% | +9.2 | -2.5 to +20.9 |
| 0.6 | 59.5% | 72.7% | +13.2 | +2.4 to +23.5 |
| 0.5 (thick) | 78.0% | 85.5% | +7.5 | +0.2 to +14.6 |

- The predicted bias is **not** there. Under thin haze the mask flags flooded and dry roads alike. Under thick haze
  it flags **flooded** roads more often, not less. Flooded roads start from a lower dark floor in the before image
  (mean 40 against 47 grey levels), so the same haze gives them a larger rise.
- So mask bias cannot explain why roads under real cloud are mostly labelled dry (26% flooded against 55% clear). If
  anything it works the other way. The label-omission reading (SpaceNet 8's "only attribute what was visible") stays
  the simpler explanation. Caveat: uniform synthetic haze, not real cloud.

## 2. The dark mask's recall on water against vegetation (HRC_WHU, 120 development images)
From `ProjectBranch/Code/cloudref_test.ipynb`: recall 0.68 on water, 0.66 on vegetation (precision 0.81 and 0.94).
The single-date mask finds cloud over water about as well as over vegetation.

## 3. What differences the tests can detect (from the paired results already logged)
- Accuracy on the 798 assessable roads, paired, tile-resampled: 95% intervals of a difference are about +/-1.1 to
  1.3 points wide each side. So differences under about 1.5 points cannot be told from noise.
- Flooded found on the 24 trusted flooded roads under thin cloud (39 tiles): the interval of the clear-vs-cloud
  difference ran from -0.54 to 0.00. With so few roads, only very large effects (about 25 points or more) are
  detectable. Synthetic haze on the 769 clear roads (433 flooded) avoids this limit.
