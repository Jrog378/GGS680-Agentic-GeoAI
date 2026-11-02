# 16: How much could perfect cloud removal show on SpaceNet 8? (2026-10-29; EXPLORATORY, development data only)

Our own measurements, not literature. Computed from the saved per-road calls of the spatially blocked
cross-validation (`pilot_scripts/spatial_cv/spatial_cv_flood_calls.npz`, `spatial_cv_calls.csv`; evidence 14).

**Why:** Justin (2026-10-29): "can you compute the upside potential if we were able to fully remove clouds from the
imagery, using our current model performance on clear skys what is the expected increase in performance over all
imagery cloudy or not. This way we can compare whether or not a 1.16 % change is poor or actually pretty good".

**Setup:** production detector, no de-hazing (factorial arm c00: production gate · raw cues · production features),
spatial folds S, mean of 21 fold seeds. Every one of the 1,037 development roads gets a call: the model is trained on
the gate's roads and also calls the roads the gate leaves out.
- Clear (kept by the production gate): 798 roads, 441 marked flooded.
- Under cloud: 239 roads (23.0%), 27 marked flooded: thin cloud 93 (24 marked), opaque-cloud tiles 146 (3 marked).

## Results

| | Clear (798) | Thin cloud (93) | Opaque tiles (146) |
|---|---|---|---|
| Accuracy against the labels | 78.58% | 79.72% | 81.74% |
| Marked-flooded roads found | 85.2% | 76.8% | 7.9% |
| Called flooded | 60.3% | 34.1% | 16.5% |

1. **Against all labels, perfect cloud removal shows no gain.** The cloudy roads already score higher than the clear
   ones, because most are "not marked flooded" and the model also calls them not flooded. Bringing them to clear-sky
   accuracy moves all 1,037 roads from 79.12% (820.5 right) to 78.58% (814.8): 5.7 roads fewer.
2. **On the labels we trust, at most about +4 roads.** Only the 27 roads marked flooded under cloud are trustworthy
   (an analyst saw water). Today 18.7 are found; at the clear-sky rate (85.2%) 23.0 would be: +4.3 roads, +0.42 points
   over 1,037.
3. **For comparison, the DINOv2 change vector adds +8.76 roads** (597.9 → 606.6 of 757; 78.98% → 80.13%, +1.16
   points; higher in 20 of 21 seeds): about twice the most perfect cloud removal can show on these labels.
4. **The real-world upside cannot be measured here.** If cloudy roads flooded at the clear-road rate (55.3%), about
   132 of the 239 would be flooded against 27 marked: up to about 105 hidden floods, and up to about 94 more roads
   right (+9 points) with perfect removal. Part of the gap is geography (the south scene is dry around its cloudy
   tiles), so this is an upper bound, not an estimate.

## Conclusion: this dataset cannot test the method

SpaceNet 8's analysts "only attribute what was visible" (Hänsch et al. 2022), and the flood label is "yes" or missing,
never "no". Under cloud the labels are mostly missing, so a method that sees through cloud is scored against labels
that were made without seeing through it. **To truly test cloud removal we have to adopt a different dataset, test
area or study objective**, one where the ground under the cloud is known independently of the cloud:
- **Dataset:** labels made from a cloud-free image of the same date or a near date (another sensor, SAR, or a later
  clear pass), or a second event with per-road flood labels (`outputs/requirements_more_data_and_compute.md`, item 2).
- **Test area:** a scene where the same roads are labelled both under cloud and clear, so the two can be compared
  road for road.
- **Study objective:** one whose truth does not depend on what the analyst could see, for example recovering the
  clear-date image itself (pixel or feature error under real cloud against a near-date clear reference), or
  road finding under cloud against the mapped road network.

Until then, de-hazing results on SpaceNet 8 are exploratory, and the measurable gain is capped at about 4 roads.
Small groups: 24 marked-flooded roads under thin cloud and 3 under opaque cloud.
