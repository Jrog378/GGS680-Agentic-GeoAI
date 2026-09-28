"""Close-up maps of the external-evidence sites, to guide the imagery check.

For each site in external_evidence.csv, draws what the model assumed (mapped OSM rail
lines, bridge-tagged segments, the rail route, the endpoint connector) over Esri World
Imagery, and prints links to open the same spot in independent imagery viewers.

These maps are a guide only: the basemap tile date is not shown here, so record your
observation and its image date from Esri Wayback or Google Earth, not from this PNG.

Run:
    python site_check_maps.py [--out outputs/week4_validation]

Outputs:
    <out>/site_<site_id>.png, plus <out>/site_<site_id>_bare.png for --bare sites
"""

import argparse
import sys
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import Point

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
RUN_DIR = SCRIPT_DIR.parent / "03_Project" / "outputs" / "default"


def links(lat, lon):
    return {
        "Esri Wayback": f"https://livingatlas.arcgis.com/wayback/#mapCenter={lon}%2C{lat}%2C18",
        "Google Maps satellite": f"https://www.google.com/maps/@{lat},{lon},250m/data=!3m1!1e3",
        "OSM (not independent)": f"https://www.openstreetmap.org/#map=18/{lat}/{lon}",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="outputs/week4_validation",
                        help="folder with external_evidence.csv (default: outputs/week4_validation)")
    parser.add_argument("--bare", nargs="*", default=["rail_crossing_1"],
                        help="site IDs that also get a circle-only copy, site_<id>_bare.png, so "
                             "the imagery is unobstructed (default: rail_crossing_1)")
    args = parser.parse_args()
    out = Path(args.out)
    if not out.is_absolute():
        out = SCRIPT_DIR / out

    sites = pd.read_csv(out / "external_evidence.csv", dtype=str)
    rail = gpd.read_file(REPO_ROOT / "rail_lines.gpkg").to_crs(3857)
    bridges = rail[rail["bridge"].fillna("").str.lower().isin(["yes", "viaduct"])]
    routes = gpd.read_file(RUN_DIR / "routes.gpkg").to_crs(3857)
    rail_route = routes[routes["route"] == "rail"]
    conns = gpd.read_file(RUN_DIR / "connectors.gpkg").to_crs(3857)
    conns = conns[conns["route"] == "rail"]

    for s in sites.itertuples():
        pt = gpd.GeoSeries([Point(float(s.lon), float(s.lat))], crs=4326).to_crs(3857).iloc[0]
        crossing = "crossing" in s.site_id
        half = 150 if crossing else 450  # metres (approx. in Web Mercator near the equator)
        # Every site gets the annotated map; --bare sites also get a circle-only copy.
        variants = [(False, f"site_{s.site_id}.png")]
        if s.site_id in args.bare:
            variants.append((True, f"site_{s.site_id}_bare.png"))
        for bare, filename in variants:
            fig, ax = plt.subplots(figsize=(9, 9))
            if not bare:
                rail.plot(ax=ax, color="yellow", linewidth=1.5, zorder=3)
                if len(bridges):
                    bridges.plot(ax=ax, color="orange", linewidth=4, zorder=3)
                rail_route.plot(ax=ax, color="magenta", linewidth=2, linestyle="-", zorder=4,
                                alpha=0.9)
                conns.plot(ax=ax, color="lime", linewidth=3, linestyle="--", zorder=5)
            ax.scatter([pt.x], [pt.y], s=500, facecolors="none", edgecolors="red", linewidths=2.5,
                       zorder=6)
            ax.set_xlim(pt.x - half, pt.x + half)
            ax.set_ylim(pt.y - half, pt.y + half)
            try:
                ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zorder=1,
                                attribution=False)
            except Exception as exc:
                print(f"Warning: basemap could not be added ({exc}).", file=sys.stderr)
            ax.set_axis_off()
            ax.set_title(f"{s.site_id}  ({s.lat}, {s.lon})\nClaim: {s.claim}", fontsize=9,
                         wrap=True)
            circle = Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="none",
                            markeredgecolor="red", markersize=14, label="Site to check")
            ax.legend(handles=[circle] if bare else [
                Line2D([0], [0], color="yellow", linewidth=1.5, label="OSM rail lines"),
                Line2D([0], [0], color="orange", linewidth=4, label="OSM rail tagged bridge"),
                Line2D([0], [0], color="magenta", linewidth=2, label="Model's rail route"),
                Line2D([0], [0], color="lime", linewidth=3, linestyle="--",
                       label="Endpoint connector (new construction)"),
                Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="none",
                       markeredgecolor="red", markersize=14, label="Site to check"),
            ], loc="lower left", fontsize=8, framealpha=0.9)
            fig.text(0.01, 0.01, "Imagery: Esri World Imagery (Esri, Maxar, Earthstar Geographics, "
                     "and the GIS User Community); date not shown."
                     + ("" if bare else " Rail data © OpenStreetMap contributors (ODbL)."),
                     fontsize=6)
            path = out / filename
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            print(f"{s.site_id}: saved {path.name}")
        for name, url in links(s.lat, s.lon).items():
            print(f"    {name}: {url}")


if __name__ == "__main__":
    main()
