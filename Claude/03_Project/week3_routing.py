"""Week 3 fiber routing comparison: baseline vs. roads/power/rail candidates.

Implements the method and connector rules in AGENTS.md and
03_02_ggs662_agentic_application_route_planning.ipynb, section 6 prompt, from the
Agentic-GeoAI course repo.

The course repo (Agentic-GeoAI) is treated as READ-ONLY: this script only reads the
GeoPackages it produced in 03_01. All generated files (script + outputs) live under
this Claude/03_Project/ folder instead, branching by run under outputs/.

Run:
    python week3_routing.py [--gap-tolerance-m 50] [--out outputs/default]

Inputs (read-only, produced by 03_01 in the Agentic-GeoAI repo root):
    route1_short.gpkg, roads.gpkg, power_lines.gpkg, rail_lines.gpkg

Outputs (under --out, default outputs/default relative to this script):
    routes.gpkg, connectors.gpkg (if any connectors used),
    route_comparison.csv, route_map.png, routing_report.md
"""

import argparse
import json
import itertools
import platform
import sys
from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import shapely
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely import force_2d
from shapely.geometry import LineString, Point, box
from shapely.ops import nearest_points, unary_union

CRS_M = "EPSG:32737"
STUDY_MARGIN_M = 3000.0
ENDPOINT_LIMIT_M = 500.0
COST_PER_M_USD = 10.0
PRECISION = 2  # node-coordinate rounding, in metres (1 cm) -- small vs. the 50 m gap tolerance

SCRIPT_DIR = Path(__file__).resolve().parent
# Read-only source of 03_01 outputs; never written to. This script lives at
# Agentic-GeoAI/Claude/03_Project/, so the repo root is two levels up.
INPUT_DIR = SCRIPT_DIR.parent.parent

CANDIDATE_FILES = {
    "roads": "roads.gpkg",
    "power": "power_lines.gpkg",
    "rail": "rail_lines.gpkg",
}


def round_pt(xy):
    return (round(xy[0], PRECISION), round(xy[1], PRECISION))


def load_study_inputs():
    route = gpd.read_file(INPUT_DIR / "route1_short.gpkg").to_crs(CRS_M)
    if len(route) != 1 or route.geom_type.iloc[0] != "LineString":
        raise ValueError("route1_short.gpkg must contain exactly one LineString.")
    route["geometry"] = route.geometry.apply(force_2d)
    baseline_line = route.geometry.iloc[0]
    coords = list(baseline_line.coords)
    c0, c1 = coords[0], coords[-1]
    # Easterly endpoint is the start, per AGENTS.md.
    start_pt, end_pt = (Point(c0), Point(c1)) if c0[0] > c1[0] else (Point(c1), Point(c0))

    minx, miny, maxx, maxy = route.total_bounds
    study_poly = box(minx - STUDY_MARGIN_M, miny - STUDY_MARGIN_M,
                      maxx + STUDY_MARGIN_M, maxy + STUDY_MARGIN_M)
    study_gdf = gpd.GeoDataFrame({"geometry": [study_poly]}, crs=CRS_M)

    return {
        "baseline_line": baseline_line,
        "baseline_length_m": baseline_line.length,
        "start_pt": start_pt,
        "end_pt": end_pt,
        "study_poly": study_poly,
        "study_gdf": study_gdf,
    }


def prepare_layer(path, study_poly):
    """Clean, explode, clip, and de-duplicate a candidate infrastructure layer."""
    gdf = gpd.read_file(path)
    n_input = len(gdf)

    gdf = gdf.to_crs(CRS_M)
    gdf["geometry"] = gdf.geometry.apply(lambda g: force_2d(g) if g is not None else g)
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    gdf = gdf[gdf.geom_type.isin(["LineString", "MultiLineString"])]

    gdf = gdf.explode(index_parts=False)
    gdf = gdf[gdf.geometry.is_valid & (gdf.length > 0)]
    n_after_explode_valid = len(gdf)

    clipped = gpd.clip(gdf, gpd.GeoDataFrame({"geometry": [study_poly]}, crs=CRS_M))
    clipped = clipped[clipped.geom_type.isin(["LineString", "MultiLineString"])]
    clipped = clipped.explode(index_parts=False)
    clipped = clipped[clipped.geom_type == "LineString"]
    clipped = clipped[clipped.length > 0]
    n_after_clip = len(clipped)

    def geom_key(geom):
        pts = [round_pt(c[:2]) for c in geom.coords]
        return min(tuple(pts), tuple(reversed(pts)))

    clipped = clipped.copy()
    clipped["_key"] = clipped.geometry.apply(geom_key)
    clipped = clipped.drop_duplicates(subset="_key")
    n_after_dedupe = len(clipped)

    report = {
        "input_features": n_input,
        "kept_valid_line_parts": n_after_explode_valid,
        "kept_after_clip": n_after_clip,
        "kept_after_dedupe": n_after_dedupe,
        "dropped_total": n_input - n_after_dedupe,
    }
    return clipped.geometry.tolist(), report


def node_lines(lines):
    """Node lines at within-layer intersections (shared vertices + crossings)."""
    if not lines:
        return []
    merged = unary_union(lines)
    if merged.is_empty:
        return []
    if merged.geom_type == "LineString":
        return [merged]
    if merged.geom_type == "MultiLineString":
        return list(merged.geoms)
    return [g for g in merged.geoms if g.geom_type == "LineString"]


def build_graph(noded_lines, edge_type):
    """Consecutive-coordinate-pair edges; nodes are rounded coordinate pairs."""
    G = nx.Graph()
    for ln in noded_lines:
        coords = list(ln.coords)
        for i in range(len(coords) - 1):
            a, b = round_pt(coords[i][:2]), round_pt(coords[i + 1][:2])
            if a == b:
                continue
            seg = LineString([a, b])
            length = seg.length
            if length <= 0:
                continue
            if G.has_edge(a, b):
                if length < G[a][b]["length_m"]:
                    G[a][b].update(geometry=seg, length_m=length, edge_type=edge_type)
            else:
                G.add_edge(a, b, geometry=seg, length_m=length, edge_type=edge_type)
    return G


def split_edge_at_point(G, point):
    """Split whichever edge is closest to `point`, returning the (new) node there."""
    node = round_pt((point.x, point.y))
    if G.has_node(node):
        return node

    best = None
    for u, v, data in G.edges(data=True):
        d = data["geometry"].distance(point)
        if best is None or d < best[0]:
            best = (d, u, v, data)
    if best is None:
        raise ValueError("Cannot split an edge in an empty graph.")
    _, u, v, data = best
    geom = data["geometry"]
    edge_type = data["edge_type"]

    proj = geom.project(point)
    p_on_line = geom.interpolate(proj)
    node = round_pt((p_on_line.x, p_on_line.y))
    if node == u or node == v:
        return node

    seg1 = LineString([u, node])
    seg2 = LineString([node, v])
    G.remove_edge(u, v)
    if seg1.length > 0:
        G.add_edge(u, node, geometry=seg1, length_m=seg1.length, edge_type=edge_type)
    if seg2.length > 0:
        G.add_edge(node, v, geometry=seg2, length_m=seg2.length, edge_type=edge_type)
    return node


def component_union(G, comp):
    geoms = [data["geometry"] for u, v, data in G.edges(comp, data=True)]
    return unary_union(geoms) if geoms else None


def repair_gaps(G, study_poly, gap_tolerance_m):
    """Bridge disconnected components with bounded straight connectors, smallest gap first."""
    connectors = []
    # Pairs are keyed by a stable node from each component (its min node), not by list
    # position, because component indices shift after every merge.
    excluded_pairs = set()

    while True:
        comps = list(nx.connected_components(G))
        if len(comps) <= 1:
            break

        comp_geoms = [component_union(G, c) for c in comps]
        comp_ids = [min(c) for c in comps]
        best = None
        for i, j in itertools.combinations(range(len(comps)), 2):
            if frozenset((comp_ids[i], comp_ids[j])) in excluded_pairs:
                continue
            g1, g2 = comp_geoms[i], comp_geoms[j]
            if g1 is None or g2 is None:
                continue
            p1, p2 = nearest_points(g1, g2)
            d = p1.distance(p2)
            if d <= gap_tolerance_m and (best is None or d < best[0]):
                best = (d, i, j, p1, p2)

        if best is None:
            break

        d, i, j, p1, p2 = best
        pair_key = frozenset((comp_ids[i], comp_ids[j]))
        connector_line = LineString([p1, p2])
        if not study_poly.covers(connector_line):
            excluded_pairs.add(pair_key)
            continue

        node1 = split_edge_at_point(G, p1)
        node2 = split_edge_at_point(G, p2)
        if node1 == node2:
            # Nearest points round to the same node, so there is nothing to add; exclude
            # the pair so the loop cannot retry it forever.
            excluded_pairs.add(pair_key)
            continue
        G.add_edge(node1, node2, geometry=connector_line, length_m=connector_line.length,
                    edge_type="gap_connector")
        connectors.append({"type": "gap_connector", "length_m": connector_line.length,
                            "geometry": connector_line})

    return connectors


def attach_endpoint(G, point, limit_m):
    """Attach a fixed endpoint to the nearest network point; report status."""
    point = Point(point.x, point.y)  # force 2D to match graph geometry dimensionality
    if G.number_of_edges() == 0:
        return None, None, "empty_network", None

    best = None
    for u, v, data in G.edges(data=True):
        d = data["geometry"].distance(point)
        if best is None or d < best[0]:
            best = (d, u, v, data)
    _, u, v, data = best
    geom = data["geometry"]
    proj = geom.project(point)
    p_on_line = geom.interpolate(proj)
    dist_to_line = point.distance(p_on_line)

    if dist_to_line > limit_m:
        return None, dist_to_line, "endpoint_too_far", None

    line_node = split_edge_at_point(G, p_on_line)
    ep_node = round_pt((point.x, point.y))
    connector = None
    if ep_node != line_node:
        connector_geom = LineString([point, p_on_line])
        if connector_geom.length > 0:
            G.add_edge(ep_node, line_node, geometry=connector_geom,
                        length_m=connector_geom.length, edge_type="endpoint_connector")
            connector = {"type": "endpoint_connector", "length_m": connector_geom.length,
                         "geometry": connector_geom}
        else:
            ep_node = line_node
    else:
        ep_node = line_node

    return ep_node, dist_to_line, "ok", connector


def reconstruct_route(G, path_nodes):
    geoms = []
    total = 0.0
    for a, b in zip(path_nodes[:-1], path_nodes[1:]):
        data = G[a][b]
        seg = data["geometry"]
        # orient segment a -> b
        if round_pt(seg.coords[0]) != a:
            seg = LineString(list(seg.coords)[::-1])
        geoms.append(seg)
        total += data["length_m"]
    coords = []
    for seg in geoms:
        pts = list(seg.coords)
        if coords and coords[-1] == pts[0]:
            pts = pts[1:]
        coords.extend(pts)
    route_geom = LineString(coords)
    return route_geom, total


def route_candidate(name, path, study, gap_tolerance_m):
    lines, clean_report = prepare_layer(path, study["study_poly"])
    noded = node_lines(lines)
    G = build_graph(noded, name)
    n_components_before = nx.number_connected_components(G) if G.number_of_nodes() else 0

    repair_gaps(G, study["study_poly"], gap_tolerance_m)
    n_components_after = nx.number_connected_components(G) if G.number_of_nodes() else 0

    result = {
        "route": name,
        "status": None,
        "length_m": None,
        "length_km": None,
        "connector_m": 0.0,
        "connector_count": 0,
        "max_connector_m": 0.0,
        "cost_per_m_usd": COST_PER_M_USD,
        "estimated_cost_usd": None,
        "geometry": None,
        "connectors": [],
        "clean_report": clean_report,
        "components_before_repair": n_components_before,
        "components_after_repair": n_components_after,
        "endpoint_dist": {},
    }

    start_node, start_dist, start_status, _ = attach_endpoint(G, study["start_pt"], ENDPOINT_LIMIT_M)
    result["endpoint_dist"]["start"] = start_dist
    if start_status != "ok":
        result["status"] = start_status
        return result

    end_node, end_dist, end_status, _ = attach_endpoint(G, study["end_pt"], ENDPOINT_LIMIT_M)
    result["endpoint_dist"]["end"] = end_dist
    if end_status != "ok":
        result["status"] = end_status
        return result

    if not nx.has_path(G, start_node, end_node):
        result["status"] = "no_path"
        return result

    path_nodes = nx.shortest_path(G, source=start_node, target=end_node,
                                   weight="length_m", method="dijkstra")
    route_geom, total_len = reconstruct_route(G, path_nodes)

    used_connectors = []
    for a, b in zip(path_nodes[:-1], path_nodes[1:]):
        data = G[a][b]
        if data["edge_type"] in ("gap_connector", "endpoint_connector"):
            used_connectors.append({"route": name, "connector_type": data["edge_type"],
                                     "length_m": data["length_m"], "geometry": data["geometry"]})

    conn_m = sum(c["length_m"] for c in used_connectors)
    conn_count = len(used_connectors)
    max_conn = max((c["length_m"] for c in used_connectors), default=0.0)

    result.update({
        "status": "ok",
        "length_m": total_len,
        "length_km": total_len / 1000.0,
        "connector_m": conn_m,
        "connector_count": conn_count,
        "max_connector_m": max_conn,
        "estimated_cost_usd": total_len * COST_PER_M_USD,
        "geometry": route_geom,
        "connectors": used_connectors,
    })
    return result


def validate_result(res, study, gap_tolerance_m):
    issues = []
    if res["status"] != "ok":
        return issues
    geom = res["geometry"]
    if geom is None or geom.is_empty or not geom.is_valid:
        issues.append("route geometry missing/invalid")
    ends = (Point(geom.coords[0]), Point(geom.coords[-1]))
    d_start = min(ends[0].distance(study["start_pt"]), ends[1].distance(study["start_pt"]))
    d_end = min(ends[0].distance(study["end_pt"]), ends[1].distance(study["end_pt"]))
    if d_start > 0.01 or d_end > 0.01:
        issues.append(f"endpoint mismatch: start={d_start:.4f} m end={d_end:.4f} m")
    if not study["study_poly"].buffer(0.01).contains(geom):
        issues.append("route leaves study area")
    if abs(geom.length - res["length_m"]) > 0.01:
        issues.append(f"geometry length {geom.length:.3f} != traversed-edge sum {res['length_m']:.3f}")
    if abs(res["estimated_cost_usd"] - res["length_m"] * COST_PER_M_USD) > 1e-6:
        issues.append("cost equation mismatch")
    for c in res["connectors"]:
        limit = gap_tolerance_m if c["connector_type"] == "gap_connector" else ENDPOINT_LIMIT_M
        if c["length_m"] > limit + 1e-6:
            issues.append(f"{c['connector_type']} length {c['length_m']:.2f} m exceeds limit {limit} m")
    return issues


def run_synthetic_tests(gap_tolerance_m):
    """Synthetic checks of the graph/connector logic, independent of real data.

    Returns {case: (expected, observed, "PASS"/"FAIL")} covering the five AGENTS.md cases
    (already connected, gap below/above threshold, endpoint on a line interior,
    disconnected endpoints) plus connector-counted-once and far-endpoint checks.
    """
    results = {}
    study_poly = box(-1000, -1000, 1000, 1000)

    def record(name, expected, observed):
        if isinstance(expected, float):
            ok = observed is not None and abs(observed - expected) <= 0.01
        else:
            ok = observed == expected
        results[name] = (expected, observed, "PASS" if ok else "FAIL")

    lines = [LineString([(0, 0), (10, 0)]), LineString([(10, 0), (20, 0)])]
    G = build_graph(node_lines(lines), "test")
    record("already_connected_components", 1, nx.number_connected_components(G))

    # Second segment points AWAY from the first, so its nearest point is its
    # own start coordinate and the true gap equals the stated offset exactly.
    gap_below = gap_tolerance_m / 2
    lines = [LineString([(0, 0), (10, 0)]),
             LineString([(10 + gap_below, 0), (10 + gap_below + 20, 0)])]
    G = build_graph(node_lines(lines), "test")
    conns = repair_gaps(G, study_poly, gap_tolerance_m)
    record("gap_below_threshold_components_after", 1, nx.number_connected_components(G))
    record("gap_below_threshold_connectors", 1, len(conns))

    gap_above = gap_tolerance_m + 50
    lines = [LineString([(0, 0), (10, 0)]),
             LineString([(10 + gap_above, 0), (10 + gap_above + 20, 0)])]
    G = build_graph(node_lines(lines), "test")
    conns = repair_gaps(G, study_poly, gap_tolerance_m)
    record("gap_above_threshold_components_after", 2, nx.number_connected_components(G))
    record("gap_above_threshold_connectors", 0, len(conns))

    # Disconnected endpoints: each endpoint attaches to its own component -> no_path.
    s_node, _, s_status, _ = attach_endpoint(G, Point(0, 0), ENDPOINT_LIMIT_M)
    e_node, _, e_status, _ = attach_endpoint(G, Point(10 + gap_above + 20, 0), ENDPOINT_LIMIT_M)
    disconnected = "no_path" if not nx.has_path(G, s_node, e_node) else "ok"
    record("disconnected_endpoints_status", "no_path", disconnected)

    lines = [LineString([(0, 0), (20, 0)])]
    G = build_graph(node_lines(lines), "test")
    node, dist, status, conn = attach_endpoint(G, Point(10, 5), ENDPOINT_LIMIT_M)
    record("endpoint_interior_status", "ok", status)
    record("endpoint_interior_dist_m", 5.0, dist)
    record("endpoint_interior_split_node", (10.0, 0.0), node if conn is None else
           round_pt(conn["geometry"].coords[-1]))

    lines = [LineString([(0, 0), (20, 0)])]
    G = build_graph(node_lines(lines), "test")
    node, dist, status, conn = attach_endpoint(G, Point(10, ENDPOINT_LIMIT_M + 50), ENDPOINT_LIMIT_M)
    record("endpoint_far_status", "endpoint_too_far", status)

    # Connector counted once: 10 m line + gap + 20 m line.
    lines = [LineString([(0, 0), (10, 0)]),
             LineString([(10 + gap_below, 0), (10 + gap_below + 20, 0)])]
    G = build_graph(node_lines(lines), "test")
    repair_gaps(G, study_poly, gap_tolerance_m)
    s_node, _, _, _ = attach_endpoint(G, Point(0, 0), ENDPOINT_LIMIT_M)
    e_node, _, _, _ = attach_endpoint(G, Point(10 + gap_below + 20, 0), ENDPOINT_LIMIT_M)
    path = nx.shortest_path(G, s_node, e_node, weight="length_m", method="dijkstra")
    _, total_len = reconstruct_route(G, path)
    conn_edges = sum(1 for a, b in zip(path[:-1], path[1:]) if G[a][b]["edge_type"] == "gap_connector")
    record("single_gap_route_length_m", float(10 + gap_below + 20), total_len)
    record("single_gap_connector_edges_on_path", 1, conn_edges)

    return results


def save_outputs(out_dir, study, baseline_geom, baseline_len, results):
    out_dir.mkdir(parents=True, exist_ok=True)

    route_rows = [{"route": "baseline", "status": "ok", "length_m": baseline_len,
                   "geometry": baseline_geom}]
    for name, res in results.items():
        if res["status"] == "ok":
            route_rows.append({"route": name, "status": "ok",
                                "length_m": res["length_m"], "geometry": res["geometry"]})
    routes_gdf = gpd.GeoDataFrame(route_rows, crs=CRS_M)
    routes_gdf.to_file(out_dir / "routes.gpkg", layer="routes")

    conn_rows = []
    for name, res in results.items():
        conn_rows.extend(res["connectors"])
    connectors_path = out_dir / "connectors.gpkg"
    if conn_rows:
        conn_gdf = gpd.GeoDataFrame(conn_rows, crs=CRS_M)
        conn_gdf.to_file(connectors_path, layer="connectors")
        connectors_note = f"{len(conn_rows)} connector(s) saved to connectors.gpkg."
    else:
        if connectors_path.exists():
            connectors_path.unlink()
        connectors_note = "No connectors were used by any successful route; connectors.gpkg omitted."

    csv_rows = [{
        "route": "baseline", "status": "ok", "length_m": baseline_len,
        "length_km": baseline_len / 1000.0, "connector_m": 0.0, "connector_count": 0,
        "max_connector_m": 0.0, "cost_per_m_usd": COST_PER_M_USD,
        "estimated_cost_usd": baseline_len * COST_PER_M_USD,
    }]
    for name, res in results.items():
        csv_rows.append({
            "route": name, "status": res["status"],
            "length_m": res["length_m"], "length_km": res["length_km"],
            "connector_m": res["connector_m"] if res["status"] == "ok" else None,
            "connector_count": res["connector_count"] if res["status"] == "ok" else None,
            "max_connector_m": res["max_connector_m"] if res["status"] == "ok" else None,
            "cost_per_m_usd": COST_PER_M_USD,
            "estimated_cost_usd": res["estimated_cost_usd"],
        })
    comparison_df = pd.DataFrame(csv_rows)
    comparison_df.to_csv(out_dir / "route_comparison.csv", index=False)

    fig, ax = plt.subplots(figsize=(11, 11))
    study_3857 = study["study_gdf"].to_crs(epsg=3857)
    study_3857.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=1.5, zorder=2)

    color_map = {"baseline": "grey", "roads": "black", "power": "orange", "rail": "purple"}
    gdf_all = routes_gdf.to_crs(epsg=3857)
    for _, row in gdf_all.iterrows():
        lw = 3 if row["route"] == "baseline" else 2.2
        gpd.GeoSeries([row.geometry], crs="EPSG:3857").plot(
            ax=ax, color=color_map.get(row["route"], "blue"), linewidth=lw, zorder=4)

    if conn_rows:
        conn_gdf_3857 = gpd.GeoDataFrame(conn_rows, crs=CRS_M).to_crs(epsg=3857)
        conn_gdf_3857.plot(ax=ax, color="lime", linewidth=3, linestyle="--", zorder=5)

    start_3857 = gpd.GeoSeries([study["start_pt"]], crs=CRS_M).to_crs(epsg=3857).iloc[0]
    end_3857 = gpd.GeoSeries([study["end_pt"]], crs=CRS_M).to_crs(epsg=3857).iloc[0]
    ax.scatter([start_3857.x], [start_3857.y], color="blue", s=80, zorder=6, marker="o")
    ax.scatter([end_3857.x], [end_3857.y], color="darkred", s=80, zorder=6, marker="s")

    try:
        ctx.add_basemap(ax, source=ctx.providers.Esri.WorldStreetMap, zorder=1,
                        attribution=False)
    except Exception as exc:
        print(f"Warning: basemap could not be added ({exc}).", file=sys.stderr)

    legend_elements = [
        Line2D([0], [0], color="grey", linewidth=3, label="Baseline route"),
        Line2D([0], [0], color="black", linewidth=2.2, label="Roads route"),
        Line2D([0], [0], color="orange", linewidth=2.2, label="Power route"),
        Line2D([0], [0], color="purple", linewidth=2.2, label="Rail route"),
        Line2D([0], [0], color="lime", linewidth=3, linestyle="--", label="Connector (gap/endpoint)"),
        Patch(facecolor="none", edgecolor="red", linewidth=1.5, label="Study area"),
        Line2D([0], [0], marker="o", linestyle="None", markerfacecolor="blue",
               markeredgecolor="blue", markersize=8, label="Start (east)"),
        Line2D([0], [0], marker="s", linestyle="None", markerfacecolor="darkred",
               markeredgecolor="darkred", markersize=8, label="End (west)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8)
    ax.set_axis_off()
    ax.set_title("Week 3 Fiber Route Comparison — Mombasa–Taveta Corridor")
    fig.text(0.01, 0.01,
             "Route network data © OpenStreetMap contributors (ODbL). Basemap: Esri World "
             "Street Map (Sources: Esri, HERE, Garmin, USGS, NGA, © OpenStreetMap "
             "contributors, and the GIS User Community).",
             fontsize=6, wrap=True)
    fig.savefig(out_dir / "route_map.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    return comparison_df, connectors_note, conn_rows


def write_report(out_dir, comparison_df, results, connectors_note, gap_tolerance_m,
                  clean_reports, synthetic_results, validation_issues, run_cmd):
    ok_rows = comparison_df[comparison_df["status"] == "ok"].copy()
    if len(ok_rows):
        ok_rows = ok_rows.sort_values("length_m")
        best = ok_rows.iloc[0]
        best_line = (f"**{best['route']}** is the shortest and cheapest available route "
                     f"under this model: {best['length_m']:.1f} m "
                     f"(USD {best['estimated_cost_usd']:,.2f}).")
    else:
        best_line = "No candidate route was available under the current thresholds."

    lines = []
    lines.append("# Week 3 routing report\n")
    lines.append(f"Run command: `{run_cmd}`\n")
    lines.append(f"Inputs read (read-only) from: `{INPUT_DIR}`\n")
    lines.append(f"Python {platform.python_version()}; "
                 f"geopandas {gpd.__version__}; shapely {shapely.__version__}; "
                 f"networkx {nx.__version__}; pandas {pd.__version__}\n")
    lines.append("## Settings\n")
    lines.append(f"- CRS for measurement: {CRS_M}\n")
    lines.append(f"- Study area margin: {STUDY_MARGIN_M:.0f} m\n")
    lines.append(f"- Gap connector limit: {gap_tolerance_m:.0f} m\n")
    lines.append(f"- Endpoint connector limit: {ENDPOINT_LIMIT_M:.0f} m\n")
    lines.append(f"- Cost rate: USD {COST_PER_M_USD:.2f} per metre "
                 f"(invented classroom value, not a construction estimate)\n")
    lines.append(f"- Node coordinate rounding: {PRECISION} decimal places "
                 f"(~1 cm; small relative to the {gap_tolerance_m:.0f} m gap tolerance)\n")

    lines.append("\n## Data cleaning (dropped features)\n")
    for name, rep in clean_reports.items():
        lines.append(f"- **{name}**: {rep['input_features']} input features -> "
                     f"{rep['kept_valid_line_parts']} valid line parts -> "
                     f"{rep['kept_after_clip']} after clipping to study area -> "
                     f"{rep['kept_after_dedupe']} after removing duplicate/reversed geometry "
                     f"({rep['dropped_total']} dropped in total).\n")

    lines.append("\n## Comparison\n")
    lines.append(comparison_df.to_markdown(index=False))
    lines.append("\n")

    lines.append("\n## Component repair and endpoint attachment\n")
    for name, res in results.items():
        lines.append(f"- **{name}**: {res['components_before_repair']} connected components "
                     f"before repair, {res['components_after_repair']} after gap repair; "
                     f"start endpoint distance to network "
                     f"{res['endpoint_dist'].get('start')}; "
                     f"end endpoint distance to network "
                     f"{res['endpoint_dist'].get('end')}; status = {res['status']}.\n")

    lines.append("\n## Validation checks\n")
    if any(validation_issues.values()):
        for name, issues in validation_issues.items():
            if issues:
                lines.append(f"- **{name}**: " + "; ".join(issues) + "\n")
    else:
        lines.append("All successful routes passed endpoint agreement (<=0.01 m), continuity, "
                     "study-area containment, geometry-vs-traversed-length agreement "
                     "(<=0.01 m), connector-limit, and cost-equation checks.\n")

    lines.append("\n## Synthetic tests\n")
    n_fail = sum(1 for _, _, st in synthetic_results.values() if st != "PASS")
    lines.append(f"{len(synthetic_results) - n_fail} of {len(synthetic_results)} passed.\n")
    lines.append("| case | expected | observed | status |\n|:--|:--|:--|:--|")
    for k, (exp, obs, st) in synthetic_results.items():
        lines.append(f"| {k} | {exp} | {obs} | {st} |")
    lines.append("")

    lines.append(f"\n## Connectors\n\n{connectors_note}\n")

    lines.append("\n## Result\n")
    lines.append(best_line + "\n")

    lines.append("\n## Limitations\n")
    lines.append(
        "- This is a simplified geometric network: within-layer line crossings are assumed "
        "connectable in 2D, which can be wrong at bridges, tunnels, or other grade-separated "
        "crossings visible in the source OSM data but not checked here.\n"
        "- Gap and endpoint connectors are hypothetical new construction, not evidence of a "
        "missing OSM feature or of any right to build along existing infrastructure.\n"
        "- The cost model uses one uniform rate per metre for every candidate, so the shortest "
        "available route is always the cheapest here; it ignores terrain, permitting, "
        "equipment, and infrastructure-specific pricing.\n"
        "- Proximity to roads, power lines, or railways does not establish permission to use "
        "that corridor for fiber.\n"
        "- Unavailable candidates (`no_path`, `endpoint_too_far`, `empty_network`) reflect the "
        "combination of source-data coverage and the chosen thresholds, not proof that no real "
        "corridor exists.\n"
    )

    report = "\n".join(lines)
    (out_dir / "routing_report.md").write_text(report)
    write_markdown_notebook(report, out_dir / "routing_report.ipynb")


def write_markdown_notebook(md_text, path):
    """Save report Markdown as a one-cell .ipynb alongside the .md (course notes format)."""
    nb = {"cells": [{"cell_type": "markdown", "metadata": {},
                     "source": md_text.splitlines(keepends=True)}],
          "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    Path(path).write_text(json.dumps(nb, indent=1, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gap-tolerance-m", type=float, default=50.0)
    parser.add_argument("--out", type=str, default="outputs/default")
    args = parser.parse_args()

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = (SCRIPT_DIR / out_dir).resolve()

    run_cmd = "python week3_routing.py" + (
        f" --gap-tolerance-m {args.gap_tolerance_m}" if args.gap_tolerance_m != 50.0 else ""
    ) + (f" --out {args.out}" if args.out != "outputs/default" else "")

    study = load_study_inputs()

    results = {}
    clean_reports = {}
    validation_issues = {}
    for name, fname in CANDIDATE_FILES.items():
        path = INPUT_DIR / fname
        if not path.exists():
            results[name] = {
                "route": name, "status": "missing_input", "length_m": None, "length_km": None,
                "connector_m": None, "connector_count": None, "max_connector_m": None,
                "cost_per_m_usd": COST_PER_M_USD, "estimated_cost_usd": None,
                "geometry": None, "connectors": [], "clean_report": {},
                "components_before_repair": None, "components_after_repair": None,
                "endpoint_dist": {},
            }
            print(f"Missing input for '{name}': expected {fname} (produced by 03_01).",
                  file=sys.stderr)
            continue
        res = route_candidate(name, path, study, args.gap_tolerance_m)
        results[name] = res
        clean_reports[name] = res["clean_report"]
        validation_issues[name] = validate_result(res, study, args.gap_tolerance_m)
        print(f"{name}: status={res['status']} "
              f"length_m={res['length_m']} cost_usd={res['estimated_cost_usd']}")

    synthetic_results = run_synthetic_tests(args.gap_tolerance_m)
    failed = [k for k, (_, _, st) in synthetic_results.items() if st != "PASS"]
    if failed:
        print("Synthetic test FAILURES: " + ", ".join(failed), file=sys.stderr)

    comparison_df, connectors_note, conn_rows = save_outputs(
        out_dir, study, study["baseline_line"], study["baseline_length_m"], results)

    write_report(out_dir, comparison_df, results, connectors_note, args.gap_tolerance_m,
                 clean_reports, synthetic_results, validation_issues, run_cmd)

    print("\nSaved outputs to", out_dir)
    print(comparison_df.to_string(index=False))


if __name__ == "__main__":
    main()
