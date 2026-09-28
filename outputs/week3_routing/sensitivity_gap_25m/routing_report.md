# Week 3 routing report

Run command: `python week3_routing.py --gap-tolerance-m 25.0 --out outputs/sensitivity_gap_25m`

Inputs read (read-only) from: `/Users/jusrogers/Masters/GGS662/Agentic-GeoAI`

Python 3.12.2; geopandas 1.1.4; shapely 2.1.2; networkx 3.6.1; pandas 2.3.3

## Settings

- CRS for measurement: EPSG:32737

- Study area margin: 3000 m

- Gap connector limit: 25 m

- Endpoint connector limit: 500 m

- Cost rate: USD 10.00 per metre (invented classroom value, not a construction estimate)

- Node coordinate rounding: 2 decimal places (~1 cm; small relative to the 25 m gap tolerance)


## Data cleaning (dropped features)

- **roads**: 4742 input features -> 4748 valid line parts -> 4748 after clipping to study area -> 2452 after removing duplicate/reversed geometry (2290 dropped in total).

- **power**: 15 input features -> 15 valid line parts -> 15 after clipping to study area -> 15 after removing duplicate/reversed geometry (0 dropped in total).

- **rail**: 77 input features -> 77 valid line parts -> 77 after clipping to study area -> 77 after removing duplicate/reversed geometry (0 dropped in total).


## Comparison

| route    | status           |   length_m |   length_km |   connector_m |   connector_count |   max_connector_m |   cost_per_m_usd |   estimated_cost_usd |
|:---------|:-----------------|-----------:|------------:|--------------:|------------------:|------------------:|-----------------:|---------------------:|
| baseline | ok               |    22896.8 |     22.8968 |       0       |                 0 |          0        |               10 |               228968 |
| roads    | ok               |    22897.6 |     22.8976 |       1.31387 |                 2 |          0.723269 |               10 |               228976 |
| power    | endpoint_too_far |      nan   |    nan      |     nan       |               nan |        nan        |               10 |                  nan |
| rail     | ok               |    25902.4 |     25.9024 |     567.54    |                 2 |        372.691    |               10 |               259024 |



## Component repair and endpoint attachment

- **roads**: 3 connected components before repair, 3 after gap repair; start endpoint distance to network 0.5906063057737416; end endpoint distance to network 0.7232685940537008; status = ok.

- **power**: 9 connected components before repair, 6 after gap repair; start endpoint distance to network 1839.1894870232877; end endpoint distance to network None; status = endpoint_too_far.

- **rail**: 3 connected components before repair, 1 after gap repair; start endpoint distance to network 194.8489019967794; end endpoint distance to network 372.69069401568873; status = ok.


## Validation checks

All successful routes passed endpoint agreement (<=0.01 m), continuity, study-area containment, geometry-vs-traversed-length agreement (<=0.01 m), connector-limit, and cost-equation checks.


## Synthetic tests

12 of 12 passed.

| case | expected | observed | status |
|:--|:--|:--|:--|
| already_connected_components | 1 | 1 | PASS |
| gap_below_threshold_components_after | 1 | 1 | PASS |
| gap_below_threshold_connectors | 1 | 1 | PASS |
| gap_above_threshold_components_after | 2 | 2 | PASS |
| gap_above_threshold_connectors | 0 | 0 | PASS |
| disconnected_endpoints_status | no_path | no_path | PASS |
| endpoint_interior_status | ok | ok | PASS |
| endpoint_interior_dist_m | 5.0 | 5.0 | PASS |
| endpoint_interior_split_node | (10.0, 0.0) | (10.0, 0.0) | PASS |
| endpoint_far_status | endpoint_too_far | endpoint_too_far | PASS |
| single_gap_route_length_m | 42.5 | 42.5 | PASS |
| single_gap_connector_edges_on_path | 1 | 1 | PASS |


## Connectors

4 connector(s) saved to connectors.gpkg.


## Result

**baseline** is the shortest and cheapest available route under this model: 22896.8 m (USD 228,967.56).


## Limitations

- This is a simplified geometric network: within-layer line crossings are assumed connectable in 2D, which can be wrong at bridges, tunnels, or other grade-separated crossings visible in the source OSM data but not checked here.
- Gap and endpoint connectors are hypothetical new construction, not evidence of a missing OSM feature or of any right to build along existing infrastructure.
- The cost model uses one uniform rate per metre for every candidate, so the shortest available route is always the cheapest here; it ignores terrain, permitting, equipment, and infrastructure-specific pricing.
- Proximity to roads, power lines, or railways does not establish permission to use that corridor for fiber.
- Unavailable candidates (`no_path`, `endpoint_too_far`, `empty_network`) reflect the combination of source-data coverage and the chosen thresholds, not proof that no real corridor exists.
