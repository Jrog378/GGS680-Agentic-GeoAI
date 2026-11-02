# Coder handoff: Tarpanelli, Mondini & Camici 2022 (NHESS 22, 2473–2489)

**Citation:** Tarpanelli, A., Mondini, A. C., & Camici, S. (2022). Effectiveness of Sentinel-1 and Sentinel-2 for flood
detection assessment in Europe. *NHESS* 22, 2473–2489. doi:10.5194/nhess-22-2473-2022
**Copy:** publisher PDF (CC BY 4.0), 17 pp. PDF: `/Users/jusrogers/Masters/papers/tarpanelli2022_sentinel1_sentinel2_flood_detection_europe_NHESS-summary.pdf`
(page 1 = AI summary). **Read:** pp. 2473–2489 (all). Code + data: Zenodo doi:10.5281/zenodo.6939820. Claude, 2026-10-29.
Context paper (evaluation-bias argument); little to implement.

## Protocol (pp. 2475–2478)
1. 1,957 gauges (GRDC + Italian/Spanish authorities), basin > 100 km², max Q > 10 m³/s, ≥ 10 yr continuous daily Q
   (record years vary, 1913–2016; not Sentinel-era). Basin classes B1 < 500, B2 500–5000, B3 5000–15000, B4 > 15000 km².
2. Flood event: Q above the site's 95/97/99/99.5th percentile over the 10-yr window; peaks within 4 days merged.
3. Duration = width of the event hydrograph at half its height above the event baseflow minimum.
4. Revisit: S1 12 / 6 / 3 d; S2 10 / 5 / 2 d. Event observable if a pass falls within it.
5. S2: observable count × (1 − annual mean cloud fraction) at the site (Wilson & Jetz 2016, 1 km).
6. F = observable / total events. Peak discharge assumed simultaneous with peak inundation (p. 2477).

## Results (Table 2, p. 2480; conclusions p. 2485)
- All sites, 99th pct: S1A 20 %, S1ABad 58 %; S2A 9 %, S2ABad 29 % (abstract rounds to 58 % / 28 %).
- Large basins (B4): S1ABad up to 67 %, S2ABad up to 33 %. Mean event duration 2.5–3.5 d (Table 3).
- Real cases: Zaragoza ~32 % (S1A) vs ~10 % (S2); York S1A 32–50 %, S2 16–25 %; Moncalieri: S2 "full of clouds".

## Limitations (p. 2484–2485)
- Assumes every pass maps the flood: "an optimistic and unrealistic hypothesis".
- Cloud applied as annual mean, independent of floods; authors argue "clouds are concentrated during flood events
  rather than for low flows", so S2 is probably overestimated — **argued, not measured**.
- Thresholds arbitrary; not every peak floods; urban/vegetation detection problems ignored.

## How to apply to our pipeline / Ida test
- **No code change.** Cite in the label-gap finding (Revision 1 item 8; evidence 16) as context: optical
  observability of floods is low and probably biased toward drier conditions. Phrase it as the authors' modelled,
  optimistic estimate for European river floods; do not cite it as measuring that cloud and flooding coincide.
- Possible cheap addition for our own data (descriptive): across SpaceNet 8 Louisiana-East tiles, cross-tabulate
  per-road cloud share against flood label rate (we already have this in evidence 16) — that is the measurement this
  paper lacks; keep reporting it as ours.
- **Feasibility:** n/a (context only).
