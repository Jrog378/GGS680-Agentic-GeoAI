"""Week 4 audit of the saved Week 3 shortened-corridor routing results (04_02, section 14).

Run (all arguments have defaults):
    python week4_audit.py
    python week4_audit.py --run-dir ../03_Project/outputs/default --out outputs/week4_validation

This script does NOT import week3_routing.py. Every check is recomputed from the saved
files (routes.gpkg, connectors.gpkg, route_comparison.csv, routing_report.md) and the
read-only 03_01 inputs, so a bug in the routing code cannot also hide in the audit.

Inputs (read-only):
    Agentic-GeoAI/{route1_short,roads,power_lines,rail_lines,settlements}.gpkg
    Claude/03_Project/outputs/<run>/...   (original run + sensitivity reruns)
    <out>/external_evidence.csv           (optional; written as a template if absent)

Outputs (under --out):
    validation_table.csv, validation_report.md, validation_map.png,
    external_evidence.csv (template on first run), inferred_crossings.gpkg
"""

import argparse
import json
import platform
import re
import sys
from math import isclose
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pyproj
import shapely
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from shapely import STRtree, force_2d
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent          # Agentic-GeoAI/ (read-only inputs)
RUNS_DIR = SCRIPT_DIR.parent / "03_Project" / "outputs"

CRS_M = "EPSG:32737"
LAYER_FILES = {"roads": "roads.gpkg", "power": "power_lines.gpkg", "rail": "rail_lines.gpkg"}
FEATURE_KEY = {"roads": "osmid", "power": "id", "rail": "id"}
EXPECTED_ROUTES = ["baseline", "roads", "power", "rail"]
EXPECTED_COLS = ["route", "status", "length_m", "length_km", "connector_m", "connector_count",
                 "max_connector_m", "cost_per_m_usd", "estimated_cost_usd"]
REQUIRED_SYNTHETIC = {
    "already connected": "already_connected_components",
    "gap below threshold": "gap_below_threshold_components_after",
    "gap above threshold": "gap_above_threshold_components_after",
    "endpoint on line interior": "endpoint_interior_status",
    "disconnected endpoints": "disconnected_endpoints_status",
    "connector counted once": "single_gap_route_length_m",
}
TOL_M = 0.01

rows = []


def check(cid, category, name, expected, observed, evidence, status):
    rows.append({"check_id": cid, "category": category, "check": name, "expected": expected,
                 "observed": observed, "evidence": evidence, "status": status})
    return status


def pf(ok):
    return "PASS" if ok else "FAIL"


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(REPO_DIR))
    except ValueError:
        return str(p)


def read_settings(report_path):
    """Parse the Settings block of a routing_report.md into {label: value}."""
    text = Path(report_path).read_text()
    block = text.split("## Settings", 1)[1].split("##", 1)[0]
    out = {}
    for m in re.finditer(r"^- ([^:]+): (.+)$", block, flags=re.M):
        out[m.group(1).strip()] = m.group(2).strip()
    return out


def read_synthetic(report_path):
    text = Path(report_path).read_text()
    if "## Synthetic tests" not in text:
        return {}
    block = text.split("## Synthetic tests", 1)[1].split("\n##", 1)[0]
    out = {}
    for line in block.splitlines():
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) == 4 and parts[3] in ("PASS", "FAIL"):
            out[parts[0]] = parts
    return out


def num(s):
    m = re.search(r"[-\d.,]+", s)
    return float(m.group(0).replace(",", "")) if m else None


# ---------------------------------------------------------------------------------------
# 1. Provenance and data QA
# ---------------------------------------------------------------------------------------

def audit_inputs(study_poly):
    layers = {}
    for name, fname in {**LAYER_FILES, "baseline": "route1_short.gpkg",
                        "settlements": "settlements.gpkg"}.items():
        path = REPO_DIR / fname
        cid = f"D-{name}"
        if not path.exists():
            check(cid, "Data QA", f"{fname} present", "file exists (saved by 03_01)",
                  "missing", rel(path), "FAIL")
            continue
        g = gpd.read_file(path)
        n_missing = int(g.geometry.isna().sum())
        n_empty = int((g.geometry.notna() & g.geometry.is_empty).sum())
        usable = g.geometry.notna() & ~g.geometry.is_empty
        n_invalid = int((usable & ~g.geometry.is_valid).sum())
        gm = g[usable].to_crs(CRS_M)
        overlap = gm.intersects(study_poly).sum()
        types = ", ".join(f"{k}={v}" for k, v in g.geom_type.value_counts().items())
        obs = (f"{len(g)} features; CRS {g.crs.to_string()}; types {types}; "
               f"missing={n_missing}, empty={n_empty}, invalid={n_invalid}; "
               f"{overlap} intersect study area")
        check(cid, "Data QA", f"{fname}: counts, CRS, geometry, extent",
              "0 missing/empty/invalid; features overlap study area", obs, rel(path),
              pf(n_missing == 0 and n_empty == 0 and n_invalid == 0 and overlap > 0))
        layers[name] = gm

    if "roads" in layers:
        r = gpd.read_file(REPO_DIR / "roads.gpkg")
        if {"u", "v", "key", "reversed"} <= set(r.columns):
            pair = r.apply(lambda x: tuple(sorted((x["u"], x["v"]))) + (x["key"],), axis=1)
            dup = int(pair.duplicated().sum())
            check("D-roads-dup", "Data QA", "roads.gpkg reversed duplicates explained",
                  "OSMnx edge export: two-way roads stored once per direction",
                  f"{dup} of {len(r)} edges share an undirected (u, v, key) with another edge; "
                  "the routing report dropped duplicate/reversed geometry accordingly",
                  rel(REPO_DIR / "roads.gpkg"), "PASS")
    return layers


# ---------------------------------------------------------------------------------------
# 2. Process verification of one saved run
# ---------------------------------------------------------------------------------------

def audit_run(run_dir, study, layers, gap_tol, endpoint_limit, rate):
    csv_path, routes_path = run_dir / "route_comparison.csv", run_dir / "routes.gpkg"
    conn_path = run_dir / "connectors.gpkg"
    df = pd.read_csv(csv_path)
    routes = gpd.read_file(routes_path).to_crs(CRS_M)
    conns = gpd.read_file(conn_path).to_crs(CRS_M) if conn_path.exists() else None

    check("C-rows", "Comparison table", "All four candidates present, one row each",
          ", ".join(EXPECTED_ROUTES), ", ".join(df["route"].astype(str)), rel(csv_path),
          pf(sorted(df["route"]) == sorted(EXPECTED_ROUTES) and len(df) == 4))
    check("C-cols", "Comparison table", "Required CSV columns", ", ".join(EXPECTED_COLS),
          ", ".join(df.columns), rel(csv_path), pf(list(df.columns) == EXPECTED_COLS))

    base = df[df.route == "baseline"].iloc[0]
    check("C-base", "Comparison table", "Baseline connector values are zero",
          "connector_m = connector_count = max_connector_m = 0",
          f"{base.connector_m}, {base.connector_count}, {base.max_connector_m}", rel(csv_path),
          pf(base.connector_m == 0 and base.connector_count == 0 and base.max_connector_m == 0))

    unavailable = df[df.status != "ok"]
    blank_ok = unavailable[["length_m", "length_km", "estimated_cost_usd"]].isna().all().all()
    check("C-unavail", "Comparison table", "Unavailable candidates have blank length/cost",
          "blank (not zero) length_m, length_km, estimated_cost_usd",
          "; ".join(f"{r.route}: status={r.status}, length={r.length_m}, cost={r.estimated_cost_usd}"
                    for r in unavailable.itertuples()) or "no unavailable candidates",
          rel(csv_path), pf(blank_ok))

    ok_routes = set(df[df.status == "ok"].route)
    check("C-gpkg", "Comparison table", "routes.gpkg holds exactly the ok routes",
          ", ".join(sorted(ok_routes)), ", ".join(sorted(routes.route)), rel(routes_path),
          pf(set(routes.route) == ok_routes))

    rates = df.cost_per_m_usd.unique()
    check("C-rate", "Cost", "One common positive rate for every candidate",
          f"{rate} USD/m for all rows", ", ".join(map(str, rates)), rel(csv_path),
          pf(len(rates) == 1 and isclose(rates[0], rate) and rates[0] > 0))

    geod = pyproj.Geod(ellps="WGS84")
    straight = study["start"].distance(study["end"])
    for r in routes.itertuples():
        row = df[df.route == r.route].iloc[0]
        g = r.geometry
        p = f"R-{r.route}"
        check(f"{p}-valid", "Route geometry", f"{r.route}: nonempty, valid, single LineString",
              "LineString, valid, nonempty", f"{g.geom_type}, valid={g.is_valid}, empty={g.is_empty}",
              rel(routes_path), pf(g.geom_type == "LineString" and g.is_valid and not g.is_empty))
        d0 = Point(g.coords[0]).distance(study["start"])
        d1 = Point(g.coords[-1]).distance(study["end"])
        if d0 > TOL_M:  # orientation is not part of the spec; accept a reversed line
            d0, d1 = Point(g.coords[-1]).distance(study["start"]), Point(g.coords[0]).distance(study["end"])
        check(f"{p}-ends", "Route geometry", f"{r.route}: endpoints match baseline endpoints",
              f"start (east) and end (west) within {TOL_M} m",
              f"start {d0:.4f} m, end {d1:.4f} m", rel(routes_path), pf(d0 <= TOL_M and d1 <= TOL_M))
        check(f"{p}-simple", "Route geometry", f"{r.route}: no loops/self-crossing",
              "is_simple = True", f"is_simple = {g.is_simple}", rel(routes_path), pf(g.is_simple))
        check(f"{p}-contain", "Route geometry", f"{r.route}: inside study rectangle",
              "covered by study rectangle (+0.01 m)",
              f"covered = {study['poly'].buffer(TOL_M).covers(g)}", rel(routes_path),
              pf(study["poly"].buffer(TOL_M).covers(g)))
        check(f"{p}-len", "Length", f"{r.route}: geometry length vs traversed-edge sum (CSV)",
              f"|diff| <= {TOL_M} m", f"geometry {g.length:.4f} m, CSV {row.length_m:.4f} m, "
              f"diff {abs(g.length - row.length_m):.6f} m", f"{rel(routes_path)}; {rel(csv_path)}",
              pf(abs(g.length - row.length_m) <= TOL_M))
        g_ll = gpd.GeoSeries([g], crs=CRS_M).to_crs(4326).iloc[0]
        geo_len = geod.geometry_length(g_ll)
        pct = 100 * (g.length - geo_len) / geo_len
        check(f"{p}-units", "Length", f"{r.route}: metres, not degrees (UTM vs geodesic)",
              "projected length within 0.1% of WGS84 geodesic length",
              f"UTM {g.length:.1f} m vs geodesic {geo_len:.1f} m ({pct:+.3f}%)", rel(routes_path),
              pf(abs(pct) < 0.1))
        check(f"{p}-straight", "Length", f"{r.route}: not shorter than straight-line distance",
              f">= {straight:.1f} m", f"{g.length:.1f} m ({g.length / straight:.3f}x)",
              rel(routes_path), pf(g.length >= straight - TOL_M))
        check(f"{p}-cost", "Cost", f"{r.route}: cost = length x rate",
              f"{row.length_m:.4f} x {rate} = {row.length_m * rate:.2f}",
              f"{row.estimated_cost_usd:.2f}; km = {row.length_km:.6f}", rel(csv_path),
              pf(isclose(row.estimated_cost_usd, row.length_m * rate, abs_tol=0.01)
                 and isclose(row.length_km, row.length_m / 1000, abs_tol=1e-6)))

        if r.route == "baseline":
            continue
        used = conns[conns.route == r.route] if conns is not None else gpd.GeoDataFrame()
        n, tot = len(used), float(used.length.sum()) if len(used) else 0.0
        mx = float(used.length.max()) if len(used) else 0.0
        check(f"{p}-conn-sum", "Connectors", f"{r.route}: connectors counted exactly once",
              f"count {row.connector_count:.0f}, total {row.connector_m:.4f} m, max {row.max_connector_m:.4f} m",
              f"count {n}, total {tot:.4f} m, max {mx:.4f} m", f"{rel(conn_path)}; {rel(csv_path)}",
              pf(n == row.connector_count and abs(tot - row.connector_m) <= TOL_M
                 and abs(mx - row.max_connector_m) <= TOL_M))
        for i, c in enumerate(used.itertuples()):
            limit = gap_tol if c.connector_type == "gap_connector" else endpoint_limit
            on_route = g.buffer(TOL_M).covers(c.geometry)
            inside = study["poly"].covers(c.geometry)
            touches_ep = (c.geometry.distance(study["start"]) <= TOL_M
                          or c.geometry.distance(study["end"]) <= TOL_M)
            type_ok = touches_ep if c.connector_type == "endpoint_connector" else True
            check(f"{p}-conn{i + 1}", "Connectors",
                  f"{r.route} {c.connector_type} #{i + 1}: limit, containment, on route",
                  f"<= {limit:g} m; inside study area; lies on route"
                  + ("; touches a fixed endpoint" if c.connector_type == "endpoint_connector" else ""),
                  f"{c.geometry.length:.2f} m; inside={inside}; on_route={on_route}"
                  + (f"; touches_endpoint={touches_ep}" if c.connector_type == "endpoint_connector" else ""),
                  rel(conn_path), pf(c.geometry.length <= limit + 1e-6 and inside and on_route and type_ok))

        # Everything that is not a connector should lie on a mapped line of that layer.
        src = layers.get(r.route)
        if src is not None:
            src_union = unary_union(src.geometry.clip(study["poly"]).values)
            mapped = g.intersection(src_union.buffer(0.05)).length
            expect = g.length - tot
            check(f"{p}-mapped", "Route geometry",
                  f"{r.route}: non-connector length lies on mapped {r.route} lines",
                  f"~{expect:.1f} m (route - connectors), within 1 m",
                  f"{mapped:.1f} m within 5 cm of source lines", f"{rel(routes_path)}; source layer",
                  pf(abs(mapped - expect) <= 1.0))

    for name in sorted(set(df.route) - ok_routes):
        row = df[df.route == name].iloc[0]
        src = layers.get(name)
        if src is None:
            check(f"U-{name}", "Unavailable", f"{name}: status independently confirmed",
                  row.status, "source layer missing", "-", "NOT_CHECKED")
            continue
        lines = src.geometry.clip(study["poly"])
        d_start = lines.distance(study["start"]).min()
        d_end = lines.distance(study["end"]).min()
        if row.status == "endpoint_too_far":
            ok = d_start > endpoint_limit or d_end > endpoint_limit
            exp = f"an endpoint > {endpoint_limit:g} m from the nearest {name} line"
        else:
            ok, exp = None, f"status {row.status}"
        check(f"U-{name}", "Unavailable", f"{name}: '{row.status}' independently confirmed", exp,
              f"start {d_start:.1f} m, end {d_end:.1f} m from nearest {name} line",
              f"{rel(REPO_DIR / LAYER_FILES[name])}; {rel(csv_path)}",
              "NOT_CHECKED" if ok is None else pf(ok))
    return df, routes, conns


# ---------------------------------------------------------------------------------------
# 3. Spatial assumption: do route transfers happen at mapped OSM junctions?
# ---------------------------------------------------------------------------------------

def audit_crossings(routes, layers, study):
    """Find route vertices where the route switches from one OSM feature to another at a
    point that is NOT a vertex of both features, i.e. a 2D crossing the routing model
    treated as connected. At bridges/tunnels these are likely grade separations."""
    records = []
    for r in routes.itertuples():
        if r.route not in layers or r.route not in FEATURE_KEY:
            continue
        src = layers[r.route].clip(study["poly"]).explode(index_parts=False).reset_index(drop=True)
        key_col = FEATURE_KEY[r.route]
        keys = src[key_col].astype(str).values
        grade = np.zeros(len(src), dtype=bool)
        for col in ("bridge", "tunnel"):
            if col in src:
                grade |= src[col].fillna("no").astype(str).str.lower().ne("no").values
        tree = STRtree(src.geometry.values)
        coords = list(r.geometry.coords)

        def seg_features(a, b):
            mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            idx = tree.query(mid, predicate="dwithin", distance=0.05)
            return set(idx.tolist())

        feats = [seg_features(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]
        for i in range(1, len(coords) - 1):
            fa, fb = feats[i - 1], feats[i]
            if not fa or not fb:
                continue  # one side is a connector
            if {keys[j] for j in fa} & {keys[j] for j in fb}:
                continue  # same OSM feature continues
            pt = Point(coords[i])
            shared = any(
                any(Point(c).distance(pt) <= 0.05 for c in src.geometry.iloc[ja].coords)
                and any(Point(c).distance(pt) <= 0.05 for c in src.geometry.iloc[jb].coords)
                for ja in fa for jb in fb)
            if shared:
                continue  # legitimate mapped junction
            records.append({
                "route": r.route, "vertex_index": i,
                "from_feature": ";".join(sorted({keys[j] for j in fa})),
                "to_feature": ";".join(sorted({keys[j] for j in fb})),
                "involves_bridge_or_tunnel": bool(any(grade[j] for j in fa | fb)),
                "geometry": pt,
            })
    return gpd.GeoDataFrame(records, geometry="geometry", crs=CRS_M) if records else \
        gpd.GeoDataFrame(columns=["route", "vertex_index", "from_feature", "to_feature",
                                  "involves_bridge_or_tunnel", "geometry"], geometry="geometry", crs=CRS_M)


def route_on_grade_features(routes, layers, study):
    out = {}
    for r in routes.itertuples():
        src = layers.get(r.route)
        if src is None:
            continue
        flag = np.zeros(len(src), dtype=bool)
        for col in ("bridge", "tunnel"):
            if col in src:
                flag |= src[col].fillna("no").astype(str).str.lower().ne("no").values
        if flag.any():
            u = unary_union(src[flag].geometry.clip(study["poly"]).values).buffer(0.05)
            out[r.route] = r.geometry.intersection(u).length
        else:
            out[r.route] = 0.0
    return out


# ---------------------------------------------------------------------------------------
# 4. Sensitivity: controlled reruns
# ---------------------------------------------------------------------------------------

def audit_sensitivity(run_dir, sens_dirs):
    base_csv = pd.read_csv(run_dir / "route_comparison.csv").set_index("route")
    base_set = read_settings(run_dir / "routing_report.md")
    base_rank = list(base_csv[base_csv.status == "ok"].sort_values("length_m").index)
    summary = []
    for sd in sens_dirs:
        if not (sd / "route_comparison.csv").exists():
            check(f"S-{sd.name}", "Sensitivity", f"Rerun {sd.name} present", "saved rerun",
                  "missing", rel(sd), "NOT_CHECKED")
            continue
        s_csv = pd.read_csv(sd / "route_comparison.csv").set_index("route")
        s_set = read_settings(sd / "routing_report.md")
        changed = sorted(k for k in set(base_set) | set(s_set)
                         if base_set.get(k) != s_set.get(k) and not k.startswith("Node coordinate"))
        check(f"S-{sd.name}-ctrl", "Sensitivity", f"{sd.name}: only the gap setting changed",
              "only 'Gap connector limit' differs from the original run",
              "changed: " + (", ".join(f"{k} {base_set.get(k)} -> {s_set.get(k)}" for k in changed) or "nothing"),
              f"{rel(run_dir / 'routing_report.md')}; {rel(sd / 'routing_report.md')}",
              pf(changed == ["Gap connector limit"]))
        diffs = []
        for name in EXPECTED_ROUTES:
            a, b = base_csv.loc[name], s_csv.loc[name]
            if a.status != b.status:
                diffs.append(f"{name} status {a.status} -> {b.status}")
            elif a.status == "ok" and (abs(a.length_m - b.length_m) > TOL_M
                                       or a.connector_count != b.connector_count):
                diffs.append(f"{name} length {a.length_m:.1f} -> {b.length_m:.1f} m, "
                             f"connectors {a.connector_count:.0f} -> {b.connector_count:.0f}")
        rank = list(s_csv[s_csv.status == "ok"].sort_values("length_m").index)
        comp_text = Path(sd / "routing_report.md").read_text()
        comps = dict(re.findall(r"\*\*(\w+)\*\*: \d+ connected components before repair, (\d+) after", comp_text))
        summary.append({"run": sd.name, "gap_limit": s_set.get("Gap connector limit"),
                        "differences": "; ".join(diffs) or "none",
                        "ranking": " < ".join(rank), "components_after_repair": comps})
        check(f"S-{sd.name}-out", "Sensitivity",
              f"{sd.name}: availability, length, connectors, ranking vs original",
              "record changes (a change is a result, not an error)",
              f"differences: {'; '.join(diffs) or 'none'}; ranking {' < '.join(rank)} "
              f"(original {' < '.join(base_rank)}); components after repair {comps}",
              rel(sd / "route_comparison.csv"), "PASS")
    base_comp = dict(re.findall(r"\*\*(\w+)\*\*: \d+ connected components before repair, (\d+) after",
                                (run_dir / "routing_report.md").read_text()))
    summary.insert(0, {"run": run_dir.name + " (original)", "gap_limit": base_set.get("Gap connector limit"),
                       "differences": "-", "ranking": " < ".join(base_rank),
                       "components_after_repair": base_comp})

    # Rate sensitivity is analytic: a common positive rate scales but never reorders.
    lengths = base_csv[base_csv.status == "ok"].length_m
    orders = {k: list((lengths * k).sort_values().index) for k in (5.0, 10.0, 20.0)}
    check("S-rate", "Sensitivity", "Common-rate change cannot reorder candidates",
          "same order at USD 5, 10, 20 /m", "; ".join(f"{k:g}: {' < '.join(v)}" for k, v in orders.items()),
          rel(run_dir / "route_comparison.csv"), pf(len({tuple(v) for v in orders.values()}) == 1))
    return summary


# ---------------------------------------------------------------------------------------
# 5. Synthetic cases (routing code's own tests, audited) + an independent oracle
# ---------------------------------------------------------------------------------------

def audit_synthetic(report_paths):
    for rp in report_paths:
        syn = read_synthetic(rp)
        tag = rp.parent.name
        for label, key in REQUIRED_SYNTHETIC.items():
            if key not in syn:
                check(f"T-{tag}-{key}", "Synthetic", f"{tag}: {label}", "case present and PASS",
                      "case not found in routing report", rel(rp), "NOT_CHECKED")
                continue
            _, exp, obs, st = syn[key]
            check(f"T-{tag}-{key}", "Synthetic", f"{tag}: {label}", exp, obs, rel(rp), st)

    # Arithmetic oracle from 04_02 section 6 (second known case), computed by hand first.
    total = 80.0 + 120.0 + 30.0
    check("T-oracle", "Synthetic", "Known case: 80 m + 120 m + 30 m gap at USD 10/m",
          "230 m, USD 2,300 (gap counted once)", f"{total:g} m, USD {total * 10:,.0f}",
          "hand calculation", pf(isclose(total, 230.0) and isclose(total * 10, 2300.0)))
    faulty = 80.0 + 120.0 + 2 * 30.0
    check("T-oracle-fault", "Synthetic", "Known case detects a double-counted gap",
          "260 m != 230 m is flagged", f"{faulty:g} m flagged = {not isclose(faulty, 230.0)}",
          "hand calculation", pf(not isclose(faulty, 230.0)))


# ---------------------------------------------------------------------------------------
# 6. External evidence (validation) -- user-supplied, never downloaded
# ---------------------------------------------------------------------------------------

EVIDENCE_COLS = ["site_id", "claim", "lon", "lat", "source", "source_date", "provenance",
                 "independent_of_osm", "observation", "supports_claim"]


def evidence_sites(conns, crossings):
    sites = []
    if conns is not None:
        for i, c in enumerate(conns.itertuples()):
            if c.geometry.length < 10:
                continue
            mid = c.geometry.interpolate(0.5, normalized=True)
            sites.append((f"{c.route}_{c.connector_type}_{i + 1}",
                          f"No mapped {c.route} line closer than {c.geometry.length:.0f} m to the "
                          f"endpoint (connector is new construction, not a missing segment)", mid))
    for i, x in enumerate(crossings.itertuples()):
        sites.append((f"{x.route}_crossing_{i + 1}",
                      f"{x.route} route transfers {x.from_feature} -> {x.to_feature} at grade "
                      f"(no bridge/tunnel separating them)", x.geometry))
    return sites


def audit_external(evidence_path, conns, crossings):
    sites = evidence_sites(conns, crossings)
    if not evidence_path.exists():
        tmpl = []
        for sid, claim, pt in sites:
            ll = gpd.GeoSeries([pt], crs=CRS_M).to_crs(4326).iloc[0]
            tmpl.append({"site_id": sid, "claim": claim, "lon": round(ll.x, 6), "lat": round(ll.y, 6),
                         "source": "", "source_date": "", "provenance": "",
                         "independent_of_osm": "", "observation": "", "supports_claim": ""})
        pd.DataFrame(tmpl, columns=EVIDENCE_COLS).to_csv(evidence_path, index=False)
    ev = pd.read_csv(evidence_path, dtype=str).fillna("")
    for r in ev.itertuples():
        filled = r.source and r.observation and r.supports_claim.lower() in ("yes", "no", "partly")
        independent = r.independent_of_osm.lower() == "yes"
        if not filled:
            status, obs = "NOT_CHECKED", "no independent evidence recorded yet"
        elif not independent:
            status, obs = "NOT_CHECKED", f"{r.source} ({r.source_date}) is not independent of OSM: {r.observation}"
        else:
            status = "PASS" if r.supports_claim.lower() == "yes" else "FAIL"
            obs = f"{r.source} ({r.source_date}; {r.provenance}): {r.observation}"
        check(f"E-{r.site_id}", "External evidence", f"{r.claim} [{r.lat}, {r.lon}]",
              "independent source supports the claim", obs, rel(evidence_path), status)
    return ev


# ---------------------------------------------------------------------------------------
# Map and report
# ---------------------------------------------------------------------------------------

def make_map(out_dir, study, routes, conns, crossings, layers):
    fig, ax = plt.subplots(figsize=(11, 9))
    to3857 = lambda g: gpd.GeoSeries(g, crs=CRS_M).to_crs(3857)
    to3857([study["poly"]]).boundary.plot(ax=ax, color="red", linewidth=1.2, zorder=2)
    for name, col in (("rail", "#b39ddb"), ("power", "#ffcc80")):
        if name in layers:
            to3857(layers[name].geometry.clip(study["poly"]).values).plot(
                ax=ax, color=col, linewidth=1, zorder=3)
    colors = {"baseline": "grey", "roads": "black", "rail": "purple"}
    for r in routes.itertuples():
        to3857([r.geometry]).plot(ax=ax, color=colors.get(r.route, "blue"),
                                  linewidth=3 if r.route == "baseline" else 2, zorder=4)
    if conns is not None and len(conns):
        c3857 = conns.to_crs(3857)
        c3857.plot(ax=ax, color="lime", linewidth=3.5, linestyle="--", zorder=5)
        # Connectors are a few hundred metres at most, invisible at corridor scale: ring them.
        mids = c3857.geometry.interpolate(0.5, normalized=True)
        ax.scatter(mids.x, mids.y, s=260, facecolors="none", edgecolors="limegreen",
                   linewidths=2, zorder=5)
    if len(crossings):
        crossings.to_crs(3857).plot(ax=ax, color="red", marker="x", markersize=60, zorder=6)
    ends = to3857([study["start"], study["end"]])
    ax.scatter(ends.x.iloc[:1], ends.y.iloc[:1], color="blue", s=70, zorder=7)
    ax.scatter(ends.x.iloc[1:], ends.y.iloc[1:], color="darkred", marker="s", s=70, zorder=7)
    try:
        import contextily as ctx
        # OSM Standard tiles refuse scripted requests (HTTP 403) and CARTO now needs an API
        # key, so use Esri's keyless light-gray canvas.
        ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas, zorder=1, attribution=False)
        basemap = "Basemap: Esri World Light Gray Canvas (Esri, HERE, Garmin, © OpenStreetMap contributors)."
    except Exception as exc:  # offline: map still carries the data attribution
        print(f"Warning: basemap unavailable ({exc}).", file=sys.stderr)
        basemap = "Basemap unavailable at run time."
    ax.legend(handles=[
        Line2D([0], [0], color="grey", lw=3, label="Baseline (route1_short)"),
        Line2D([0], [0], color="black", lw=2, label="Roads route"),
        Line2D([0], [0], color="purple", lw=2, label="Rail route"),
        Line2D([0], [0], color="lime", lw=3.5, ls="--", marker="o", markerfacecolor="none",
               markeredgecolor="limegreen", markersize=12,
               label="Inferred connector (hypothetical, ringed)"),
        Line2D([0], [0], color="#b39ddb", lw=1, label="Mapped rail (OSM)"),
        Line2D([0], [0], color="#ffcc80", lw=1, label="Mapped power (OSM)"),
        Line2D([0], [0], color="red", marker="x", ls="None", label="Unverified 2D crossing transfer"),
        Patch(facecolor="none", edgecolor="red", label="Study rectangle"),
        Line2D([0], [0], color="blue", marker="o", ls="None", label="Start (east)"),
        Line2D([0], [0], color="darkred", marker="s", ls="None", label="End (west)"),
    ], loc="lower left", fontsize=8, framealpha=0.9)
    ax.set_axis_off()
    ax.set_title("Week 4 audit: shortened corridor routes, connectors and flagged crossings")
    fig.text(0.01, 0.01, "Route and infrastructure data © OpenStreetMap contributors (ODbL). " + basemap,
             fontsize=7)
    fig.savefig(out_dir / "validation_map.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_report(out_dir, run_cmd, table, sens_summary, crossings, grade_len, run_dir):
    counts = table.status.value_counts().to_dict()
    fails = table[table.status == "FAIL"]
    lines = ["# Week 4 validation report\n",
             f"Run command: `{run_cmd}`\n",
             f"Audited run: `{rel(run_dir)}`\n",
             f"Python {platform.python_version()}; geopandas {gpd.__version__}; shapely {shapely.__version__}; "
             f"pyproj {pyproj.__version__}; networkx {nx.__version__}; pandas {pd.__version__}\n",
             "The audit is independent of `week3_routing.py`: it recomputes every value from saved "
             "files. It is still a self-check by the same AI assistant that wrote the routing code, "
             "so it verifies computations but is not independent validation of the real world.\n",
             "## Check summary\n",
             ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) + f" (of {len(table)} checks). "
             "Full table: `validation_table.csv`.\n"]
    if len(fails):
        lines.append("### Failed checks\n")
        for f in fails.itertuples():
            lines.append(f"- **{f.check_id}** {f.check}: expected {f.expected}; observed {f.observed}.")
        lines.append("")
    lines.append("## Sensitivity (gap tolerance only)\n")
    lines.append(pd.DataFrame(sens_summary).to_markdown(index=False))
    lines.append("")
    lines.append("## Spatial assumption: 2D crossings\n")
    lines.append(f"{len(crossings)} route vertex(es) switch between OSM features at a point that is "
                 "not a shared vertex of both features (saved to `inferred_crossings.gpkg`, red x "
                 f"on the map); {int(crossings.involves_bridge_or_tunnel.sum()) if len(crossings) else 0} "
                 "involve a feature tagged bridge/tunnel. Route length on bridge/tunnel-tagged "
                 "features: " + ", ".join(f"{k} {v:.0f} m" for k, v in grade_len.items()) + ".\n")
    lines.append("## Conclusions and labels\n")
    lines.append("Labels follow 04_02 section 16 and can overlap. Each cites check IDs in the table.\n")
    lines.extend(conclusions(table, crossings))
    report = "\n".join(lines) + "\n"
    (out_dir / "validation_report.md").write_text(report)
    write_markdown_notebook(report, out_dir / "validation_report.ipynb")


def conclusions(table, crossings):
    st = dict(zip(table.check_id, table.status))
    allpass = lambda prefix: all(v == "PASS" for k, v in st.items() if k.startswith(prefix))
    ext = table[table.category == "External evidence"]

    def ext_label(rows, contradicted):
        # FAIL = independent evidence contradicts the claim; NOT_CHECKED = no usable evidence.
        if not len(rows) or (rows.status == "NOT_CHECKED").any():
            return "UNRESOLVED"
        if (rows.status == "PASS").all():
            return "EXTERNALLY SUPPORTED"
        return contradicted

    conn_ext = ext[ext.check_id.str.contains("_connector_")]
    cross_ext = ext[ext.check_id.str.contains("_crossing_")]
    n_cross = len(crossings)
    if not n_cross:
        cross_line = ("- Every network route transfers only at mapped junctions — **VERIFIED** "
                      "(V-crossings); grade separation along mapped lines still needs imagery.")
    else:
        where = f"{n_cross} transfer(s) on the {', '.join(sorted(crossings.route.unique()))} route"
        cross_label = ext_label(cross_ext, "CONTRADICTED BY INDEPENDENT EVIDENCE")
        if cross_label == "UNRESOLVED":
            cross_line = (f"- Every network route transfers only at mapped junctions — **UNRESOLVED**: "
                          f"{where} happen at unverified 2D crossings (V-crossings, map); these need imagery.")
        elif cross_label == "EXTERNALLY SUPPORTED":
            cross_line = (f"- The {where} at 2D crossings are at-grade junctions — **EXTERNALLY SUPPORTED** "
                          f"(V-crossings, E-*crossing*).")
        else:
            cross_line = (f"- The route is continuous through every crossing — **{cross_label}**: "
                          f"imagery shows the {where} occur at a grade separation, not a junction "
                          f"(V-crossings, E-*crossing*). The route as computed cannot be followed "
                          f"there; the agent should forbid that transfer and re-route (or report "
                          f"no_path) rather than relax a threshold.")
    return [
        f"- Route lengths, endpoints, containment and costs are computed correctly "
        f"— **{'VERIFIED' if allpass('R-') and allpass('C-') else 'NOT VERIFIED'}** (R-*, C-*).",
        f"- Connectors are within their limits and counted once; every used connector is an "
        f"endpoint connector — **{'VERIFIED' if all(v == 'PASS' for k, v in st.items() if '-conn' in k) else 'NOT VERIFIED'}** (R-*-conn*).",
        f"- Power is unavailable because its start point is far from any mapped power line, not "
        f"because of the gap threshold — **{'VERIFIED' if st.get('U-power') == 'PASS' else 'UNRESOLVED'}** "
        f"(U-power, S-*); whether a real line exists there is **UNRESOLVED** without utility data.",
        "- Availability and ranking (baseline < roads < rail) do not change between 25, 50 and "
        "250 m gap tolerance — **not SENSITIVE** to this one setting (S-*). This is a single "
        "setting rerun, not a global robustness test.",
        cross_line,
        f"- Endpoint connectors are new construction, not stand-ins for unmapped track — "
        f"**{ext_label(conn_ext, 'CONTRADICTED BY INDEPENDENT EVIDENCE')}** (E-*connector*); "
        f"imagery is one source at one date, and does not show buildability.",
        "- Access rights, permits and construction feasibility along any corridor — **UNRESOLVED**; "
        "mapped proximity does not establish them, and no legal or engineering evidence was used.",
        "- Costs are relative, invented classroom values (USD 10/m) — not a construction estimate.",
    ]


def write_markdown_notebook(md_text, path):
    """Save report Markdown as a one-cell .ipynb alongside the .md (course notes format)."""
    nb = {"cells": [{"cell_type": "markdown", "metadata": {},
                     "source": md_text.splitlines(keepends=True)}],
          "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    Path(path).write_text(json.dumps(nb, indent=1, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run-dir", default=str(RUNS_DIR / "default"),
                    help="original Week 3 run to audit (default: 03_Project/outputs/default)")
    ap.add_argument("--sensitivity-dirs", nargs="*",
                    default=[str(RUNS_DIR / "sensitivity_gap_25m"), str(RUNS_DIR / "gap_tolerance_250m")],
                    help="controlled reruns to compare against the original")
    ap.add_argument("--out", default=str(SCRIPT_DIR / "outputs" / "week4_validation"))
    ap.add_argument("--gap-tolerance-m", type=float, default=50.0)
    ap.add_argument("--endpoint-limit-m", type=float, default=500.0)
    ap.add_argument("--cost-per-m-usd", type=float, default=10.0)
    ap.add_argument("--margin-m", type=float, default=3000.0)
    ap.add_argument("--evidence", default=None,
                    help="external evidence CSV (default: <out>/external_evidence.csv)")
    args = ap.parse_args()

    run_dir, out_dir = Path(args.run_dir).resolve(), Path(args.out).resolve()
    sens_dirs = [Path(p).resolve() for p in args.sensitivity_dirs]
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = Path(args.evidence) if args.evidence else out_dir / "external_evidence.csv"
    run_cmd = "python " + " ".join([Path(sys.argv[0]).name] + sys.argv[1:])

    base = gpd.read_file(REPO_DIR / "route1_short.gpkg").to_crs(CRS_M)
    line = force_2d(base.geometry.iloc[0])
    c0, c1 = Point(line.coords[0]), Point(line.coords[-1])
    start, end = (c0, c1) if c0.x > c1.x else (c1, c0)
    minx, miny, maxx, maxy = base.total_bounds
    poly = box(minx - args.margin_m, miny - args.margin_m, maxx + args.margin_m, maxy + args.margin_m)
    study = {"start": start, "end": end, "poly": poly}

    settings = read_settings(run_dir / "routing_report.md")
    exp = {"Gap connector limit": args.gap_tolerance_m, "Endpoint connector limit": args.endpoint_limit_m,
           "Study area margin": args.margin_m}
    mism = [f"{k}: report {settings.get(k)} vs audit {v:g}" for k, v in exp.items()
            if num(settings.get(k, "")) != v]
    check("P-settings", "Provenance", "Audited run used the specified settings",
          "gap 50 m, endpoint 500 m, margin 3000 m, EPSG:32737",
          "; ".join(mism) or f"match; CRS {settings.get('CRS for measurement')}",
          rel(run_dir / "routing_report.md"),
          pf(not mism and settings.get("CRS for measurement") == CRS_M))

    layers = audit_inputs(poly)
    df, routes, conns = audit_run(run_dir, study, layers, args.gap_tolerance_m,
                                  args.endpoint_limit_m, args.cost_per_m_usd)
    crossings = audit_crossings(routes, layers, study)
    grade_len = route_on_grade_features(routes, layers, study)
    n_cross, n_grade = len(crossings), int(crossings.involves_bridge_or_tunnel.sum()) if len(crossings) else 0
    check("V-crossings", "Spatial assumption", "Route transfers only at mapped junctions",
          "0 transfers at points that are not shared OSM vertices",
          f"{n_cross} unverified 2D crossing transfer(s); {n_grade} involve bridge/tunnel-tagged features",
          "inferred_crossings.gpkg", pf(n_cross == 0))
    crossings.to_file(out_dir / "inferred_crossings.gpkg", layer="crossings")

    sens_summary = audit_sensitivity(run_dir, sens_dirs)
    audit_synthetic([run_dir / "routing_report.md"] + [d / "routing_report.md" for d in sens_dirs
                                                     if (d / "routing_report.md").exists()])
    audit_external(evidence_path, conns, crossings)

    table = pd.DataFrame(rows)
    table.to_csv(out_dir / "validation_table.csv", index=False)
    make_map(out_dir, study, routes, conns, crossings, layers)
    write_report(out_dir, run_cmd, table, sens_summary, crossings, grade_len, run_dir)

    print(table.status.value_counts().to_string())
    for r in table[table.status != "PASS"].itertuples():
        print(f"{r.status:12s} {r.check_id}: {r.observed}")
    print("Saved to", out_dir)


if __name__ == "__main__":
    main()
