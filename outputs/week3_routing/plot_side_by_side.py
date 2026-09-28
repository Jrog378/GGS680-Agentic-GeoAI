"""Side-by-side map: baseline route vs. each Week 3 candidate (roads, power, rail).

Reads the saved outputs of week3_routing.py (it does not rerun the routing) and the
read-only power_lines.gpkg from the Agentic-GeoAI repo root, for the power panel.

Run:
    python plot_side_by_side.py [--run outputs/default]

Output:
    <run>/route_side_by_side.png
"""

import argparse
import sys
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import box

CRS_M = "EPSG:32737"
STUDY_MARGIN_M = 3000.0

SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_DIR = SCRIPT_DIR.parent.parent  # read-only course repo root

CANDIDATES = [("roads", "black"), ("power", "darkorange"), ("rail", "purple")]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", default="outputs/default",
                        help="run folder produced by week3_routing.py (default: outputs/default)")
    args = parser.parse_args()
    run_dir = Path(args.run)
    if not run_dir.is_absolute():
        run_dir = SCRIPT_DIR / run_dir

    routes = gpd.read_file(run_dir / "routes.gpkg").to_crs(CRS_M)
    comparison = pd.read_csv(run_dir / "route_comparison.csv").set_index("route")
    conn_path = run_dir / "connectors.gpkg"
    connectors = gpd.read_file(conn_path).to_crs(CRS_M) if conn_path.exists() else None

    baseline = routes[routes["route"] == "baseline"]
    base_len = comparison.loc["baseline", "length_m"]
    coords = list(baseline.geometry.iloc[0].coords)
    c0, c1 = coords[0], coords[-1]
    start, end = (c0, c1) if c0[0] > c1[0] else (c1, c0)  # easterly endpoint is the start

    minx, miny, maxx, maxy = baseline.total_bounds
    study = gpd.GeoDataFrame(geometry=[box(minx - STUDY_MARGIN_M, miny - STUDY_MARGIN_M,
                                           maxx + STUDY_MARGIN_M, maxy + STUDY_MARGIN_M)],
                             crs=CRS_M)
    power_lines = gpd.read_file(INPUT_DIR / "power_lines.gpkg").to_crs(CRS_M)
    power_lines = gpd.clip(power_lines, study)

    ends = gpd.GeoSeries(gpd.points_from_xy([start[0], end[0]], [start[1], end[1]]),
                         crs=CRS_M).to_crs(epsg=3857)
    study_3857 = study.to_crs(epsg=3857)
    bx0, by0, bx1, by1 = study_3857.total_bounds

    fig, axes = plt.subplots(1, 3, figsize=(18, 8.2))
    for ax, (name, color) in zip(axes, CANDIDATES):
        study_3857.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=1, zorder=2)
        # Baseline as a wide translucent band underneath, so an overlapping route stays visible.
        baseline.to_crs(epsg=3857).plot(ax=ax, color="deepskyblue", linewidth=7, alpha=0.45,
                                        zorder=3)
        status = comparison.loc[name, "status"]
        if status == "ok":
            routes[routes["route"] == name].to_crs(epsg=3857).plot(
                ax=ax, color=color, linewidth=1.8, zorder=4)
            if connectors is not None:
                c = connectors[connectors["route"] == name]
                if len(c):
                    c.to_crs(epsg=3857).plot(ax=ax, color="lime", linewidth=3,
                                             linestyle="--", zorder=5)
            length = comparison.loc[name, "length_m"]
            conn_m = comparison.loc[name, "connector_m"]
            subtitle = (f"{length:,.1f} m ({length - base_len:+,.1f} m vs baseline)\n"
                        f"connectors {conn_m:,.1f} m · USD {comparison.loc[name, 'estimated_cost_usd']:,.0f}")
        else:
            # No route: show the mapped lines so the gap to the endpoint is visible.
            if len(power_lines):
                power_lines.to_crs(epsg=3857).plot(ax=ax, color=color, linewidth=1.5,
                                                   linestyle=":", zorder=4)
            subtitle = f"status: {status}\nno route; mapped power lines shown dotted"
        ax.scatter([ends.iloc[0].x], [ends.iloc[0].y], color="blue", s=60, zorder=6)
        ax.scatter([ends.iloc[1].x], [ends.iloc[1].y], color="darkred", s=60, marker="s",
                   zorder=6)
        ax.set_xlim(bx0, bx1)
        ax.set_ylim(by0, by1)
        try:
            ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas, zorder=1,
                            attribution=False)
        except Exception as exc:
            print(f"Warning: basemap could not be added ({exc}).", file=sys.stderr)
        ax.set_axis_off()
        ax.set_title(f"Baseline vs {name}\n{subtitle}", fontsize=10)

    legend = [
        Line2D([0], [0], color="deepskyblue", linewidth=7, alpha=0.45,
               label=f"Baseline ({base_len:,.1f} m)"),
        Line2D([0], [0], color="black", linewidth=1.8, label="Roads route"),
        Line2D([0], [0], color="darkorange", linewidth=1.5, linestyle=":",
               label="Mapped power lines (no route)"),
        Line2D([0], [0], color="purple", linewidth=1.8, label="Rail route"),
        Line2D([0], [0], color="lime", linewidth=3, linestyle="--",
               label="Endpoint connector (new construction)"),
        Line2D([0], [0], color="red", linewidth=1, label="Study area"),
        Line2D([0], [0], marker="o", linestyle="None", color="blue", label="Start (east)"),
        Line2D([0], [0], marker="s", linestyle="None", color="darkred", label="End (west)"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=4, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, 0.03))
    fig.suptitle(f"Week 3 routes vs baseline — {run_dir.name} run "
                 "(uniform USD 10/m classroom rate)", fontsize=13)
    fig.text(0.01, 0.005,
             "Route network data © OpenStreetMap contributors (ODbL). Basemap: Esri World "
             "Light Gray Canvas (Sources: Esri, HERE, Garmin, © OpenStreetMap contributors, "
             "and the GIS User Community).", fontsize=7)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.84, bottom=0.12, wspace=0.03)
    out = run_dir / "route_side_by_side.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
