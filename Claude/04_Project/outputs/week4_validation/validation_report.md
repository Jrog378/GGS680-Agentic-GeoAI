# Week 4 validation report

Run command: `python week4_audit.py`

Audited run: `Claude/03_Project/outputs/default`

Python 3.12.2; geopandas 1.1.4; shapely 2.1.2; pyproj 3.8.0; networkx 3.6.1; pandas 2.3.3

The audit is independent of `week3_routing.py`: it recomputes every value from saved files. It is still a self-check by the same AI assistant that wrote the routing code, so it verifies computations but is not independent validation of the real world.

## Check summary

FAIL: 1, NOT_CHECKED: 3, PASS: 71 (of 75 checks). Full table: `validation_table.csv`.

### Failed checks

- **V-crossings** Route transfers only at mapped junctions: expected 0 transfers at points that are not shared OSM vertices; observed 1 unverified 2D crossing transfer(s); 1 involve bridge/tunnel-tagged features.

## Sensitivity (gap tolerance only)

| run                 | gap_limit   | differences   | ranking                 | components_after_repair                   |
|:--------------------|:------------|:--------------|:------------------------|:------------------------------------------|
| default (original)  | 50 m        | -             | baseline < roads < rail | {'roads': '3', 'power': '3', 'rail': '1'} |
| sensitivity_gap_25m | 25 m        | none          | baseline < roads < rail | {'roads': '3', 'power': '6', 'rail': '1'} |
| gap_tolerance_250m  | 250 m       | none          | baseline < roads < rail | {'roads': '3', 'power': '1', 'rail': '1'} |

## Spatial assumption: 2D crossings

1 route vertex(es) switch between OSM features at a point that is not a shared vertex of both features (saved to `inferred_crossings.gpkg`, red x on the map); 1 involve a feature tagged bridge/tunnel. Route length on bridge/tunnel-tagged features: baseline 0 m, roads 160 m, rail 84 m.

## Conclusions and labels

Labels follow 04_02 section 16 and can overlap. Each cites check IDs in the table.

- Route lengths, endpoints, containment and costs are computed correctly — **VERIFIED** (R-*, C-*).
- Connectors are within their limits and counted once; every used connector is an endpoint connector — **VERIFIED** (R-*-conn*).
- Power is unavailable because its start point is far from any mapped power line, not because of the gap threshold — **VERIFIED** (U-power, S-*); whether a real line exists there is **UNRESOLVED** without utility data.
- Availability and ranking (baseline < roads < rail) do not change between 25, 50 and 250 m gap tolerance — **not SENSITIVE** to this one setting (S-*). This is a single setting rerun, not a global robustness test.
- Every network route transfers only at mapped junctions — **UNRESOLVED**: 1 transfer(s) on the rail route happen at unverified 2D crossings (V-crossings, map); these need imagery.
- Connector sites and crossings match reality on the ground — **UNRESOLVED** (E-*).
- Access rights, permits and construction feasibility along any corridor — **UNRESOLVED**; mapped proximity does not establish them, and no legal or engineering evidence was used.
- Costs are relative, invented classroom values (USD 10/m) — not a construction estimate.
