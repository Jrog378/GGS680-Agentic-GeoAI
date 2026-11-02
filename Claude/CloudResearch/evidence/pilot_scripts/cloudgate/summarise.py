"""The numbers outputs/preregistration_cloud_gate.md asks for, from synthetic_tiles.csv, synthetic_confusion.json,
haze_recovery_rerun.csv, real_tiles.csv and real_roads.csv. Writes numbers.json and prints every table."""
import json
import sys
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd
from scipy.stats import binomtest

OUT = Path(__file__).resolve().parent
SEED = 662
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
numbers = {}


def sign_test(a, b):
    """a against b per tile (lower is better): tiles better, worse, exact two-sided p, mean difference and its 95%
    interval from resampling whole tiles."""
    d = np.asarray(a, float) - np.asarray(b, float)
    better, worse = int((d < 0).sum()), int((d > 0).sum())
    p = binomtest(better, better + worse).pvalue if better + worse else 1.0
    rng = np.random.default_rng(SEED)
    boots = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(5000)]
    return {"better": better, "worse": worse, "ties": int((d == 0).sum()), "p": float(p),
            "mean difference": float(d.mean()), "95% CI": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}


def holm(ps):
    order = np.argsort(ps)
    adj, running = np.empty(len(ps)), 0.0
    for rank, k in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[k]))
        adj[k] = running
    return adj.tolist()


def f1(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else np.nan


s = pd.read_csv(OUT / "synthetic_tiles.csv")
s["f1"] = [f1(a, b, c) for a, b, c in zip(s.tp.fillna(0), s.fp.fillna(0), s.fn.fillna(0))]
s.loc[s.tp.isna(), "f1"] = np.nan


def per_tile(scen, arm, col):
    g = s[(s.scenario == scen) & (s.arm == arm)].set_index("tile_id")[col]
    return g


def arm_table(scen):
    rows = []
    for arm, g in s[s.scenario == scen].groupby("arm", sort=False):
        r = {"arm": arm, "tiles": len(g), "grey error": g["grey error"].mean(), "detail kept": g["detail kept"].mean()}
        for c in ("t error", "clear ground changed", "cannot under haze", "cannot on clear ground",
                  "detected on clear ground"):
            r[c] = g[c].mean() if c in g and g[c].notna().any() else np.nan
        if g.tp.notna().any():
            r["pooled F1"] = f1(g.tp.sum(), g.fp.sum(), g.fn.sum())
            r["precision"] = g.tp.sum() / max(g.tp.sum() + g.fp.sum(), 1)
            r["recall"] = g.tp.sum() / max(g.tp.sum() + g.fn.sum(), 1)
            r["median tile F1"] = g.f1.median()
        for strip in ("flooded strip", "dry strip"):
            r[f"{strip} error (pooled)"] = np.sqrt(g[f"{strip} sse"].sum() / max(g[f"{strip} px"].sum(), 1))
        rows.append(r)
    return pd.DataFrame(rows)


print("=" * 100, "\nSYNTHETIC CHECKS (94 clear development tiles)\n")
for scen in ("S1 after haze", "S2 before haze"):
    t = arm_table(scen)
    numbers[scen] = t.round(4).to_dict("records")
    print(scen)
    print(t.round(3).to_string(index=False), "\n")
extra = s[s.scenario == "S2 before haze"].groupby("arm", sort=False)[["after altered", "rise share", "both share", "gate share"]].mean()
print("S2: share of the AFTER image altered, rise-gate and both-cloudy shares (means over tiles)")
print(extra.round(4).to_string(), "\n")
numbers["S2 side effects"] = extra.round(5).reset_index().to_dict("records")
extra1 = s[s.scenario == "S1 after haze"].groupby("arm", sort=False)[["before altered", "fall share", "both share"]].mean()
print("S1: share of the BEFORE image altered, fall-gate and both-cloudy shares (means over tiles)")
print(extra1.round(4).to_string(), "\n")
numbers["S1 side effects"] = extra1.round(5).reset_index().to_dict("records")

# ---------- task A primary ----------
print("=" * 100, "\nTASK A\n")
a1 = sign_test(per_tile("S2 before haze", "either-date", "grey error"), per_tile("S2 before haze", "as it is", "grey error"))
a1he = sign_test(per_tile("S2 before haze", "either-date", "grey error"), per_tile("S2 before haze", "single image (He)", "grey error"))
print("A-1 S2 grey error, either-date against as it is:", a1)
print("    (secondary) either-date against He:", a1he)
numbers["A-1"] = a1
numbers["A-1 secondary vs He"] = a1he
s1t, s2t = arm_table("S1 after haze").set_index("arm"), arm_table("S2 before haze").set_index("arm")
a2 = {arm: {"F1 after cloudy (S1)": float(s1t.loc[arm, "pooled F1"]), "F1 before cloudy (S2)": float(s2t.loc[arm, "pooled F1"]),
            "difference": float(s2t.loc[arm, "pooled F1"] - s1t.loc[arm, "pooled F1"])}
      for arm in s1t.index if arm in s2t.index and pd.notna(s1t.loc[arm].get("pooled F1")) and pd.notna(s2t.loc[arm].get("pooled F1"))}
print("A-2 symmetry (pooled F1):")
print(pd.DataFrame(a2).T.round(4).to_string())
numbers["A-2"] = a2
# A-3 regression
rerun = pd.read_csv(OUT / "haze_recovery_rerun.csv")
old = pd.read_csv(OUT.parent / "haze_recovery.csv")
assert list(rerun.tile_id) == list(old.tile_id)
diff = (rerun.drop(columns="tile_id") - old.drop(columns="tile_id")).abs().max()
print("\nA-3 (i) haze_recovery rerun against the archived run, largest per-tile difference per column:")
print(diff.to_string())
numbers["A-3 (i) max difference"] = diff.round(6).to_dict()
ed = s[(s.scenario == "S1 after haze") & (s.arm == "either-date")]
eligible = ed[(ed["fall share"] == 0) & (ed["both share"] == 0)]
same = eligible[eligible["max diff vs existing"] <= 1e-3]
print(f"\nA-3 (ii) tiles with no fall-gate and no both-cloudy pixels: {len(eligible)}; corrected after identical "
      f"(max diff <= 0.001) on {len(same)}; largest max diff among them {eligible['max diff vs existing'].max():.6f}")
print("    tiles with fall or both pixels:", len(ed) - len(eligible), "; their max diff:",
      ed.loc[~ed.index.isin(eligible.index), "max diff vs existing"].round(2).tolist()[:20])
print("    tiles whose rise gate differs from the existing gate:", int((ed["gate differs vs existing"] > 0).sum()))
ex = s1t.loc["existing two-date"]
eo = s1t.loc["either-date"]
a3 = {"eligible tiles": len(eligible), "identical tiles": len(same),
      "max diff on eligible": float(eligible["max diff vs existing"].max()),
      "tiles with fall or both pixels": int(len(ed) - len(eligible)),
      "grey error existing / either-date": [float(ex["grey error"]), float(eo["grey error"])],
      "detail kept existing / either-date": [float(ex["detail kept"]), float(eo["detail kept"])],
      "clear ground changed existing / either-date": [float(ex["clear ground changed"]), float(eo["clear ground changed"])],
      "archived haze_recovery means (revised fit)": {c: float(old[f"{c}: revised fit"].mean()) for c in
                                                      ("grey error under haze", "detail kept under haze",
                                                       "clear ground read as haze")}}
a3["within tolerances"] = bool(abs(a3["grey error existing / either-date"][0] - a3["grey error existing / either-date"][1]) <= 0.5
                               and abs(a3["detail kept existing / either-date"][0] - a3["detail kept existing / either-date"][1]) <= 0.01
                               and abs(a3["clear ground changed existing / either-date"][0] - a3["clear ground changed existing / either-date"][1]) <= 0.001)
print("A-3 (iii)", json.dumps(a3, indent=1))
numbers["A-3"] = a3

# changed against unchanged ground
print("\nChanged ground (haze inside flooded-road strips) against unchanged (haze inside dry-road strips)")
cg = {}
for scen in ("S2 before haze", "S1 after haze"):
    g = s[s.scenario == scen]
    base = g[g.arm == "as it is"].set_index("tile_id")
    ok = base[(base["flooded strip px"] >= 500) & (base["dry strip px"] >= 500)].index
    out = {"tiles with both": len(ok)}
    removed = {}
    for arm in ("either-date", "single image (He)", "existing two-date"):
        a = g[g.arm == arm].set_index("tile_id").loc[ok]
        b = base.loc[ok]
        rf = 1 - np.sqrt(a["flooded strip sse"] / a["flooded strip px"]) / np.sqrt(b["flooded strip sse"] / b["flooded strip px"])
        rd = 1 - np.sqrt(a["dry strip sse"] / a["dry strip px"]) / np.sqrt(b["dry strip sse"] / b["dry strip px"])
        removed[arm] = (rf, rd)
        out[arm] = {"error removed, flooded strips (median tile)": float(rf.median()),
                    "error removed, dry strips (median tile)": float(rd.median()),
                    "flooded worse than dry (sign test on removed share)": sign_test(-rf.to_numpy(), -rd.to_numpy())}
    dd = (removed["either-date"][0] - removed["either-date"][1]) - (removed["single image (He)"][0] - removed["single image (He)"][1])
    out["either-date minus He, (flooded - dry) removed share"] = {"median": float(dd.median()), **sign_test(-dd.to_numpy(), np.zeros(len(dd)))}
    cg[scen] = out
    print(scen, json.dumps(out, indent=1))
numbers["changed ground"] = cg

# S3
conf = json.load(open(OUT / "synthetic_confusion.json"))
conf = list(conf.values())[0]
names = ["clear", "after", "before", "both"]
print("\nS3 haze on both dates: confusion, rows = truth, columns = label (pooled pixels; row shares)")
s3 = {}
for arm, m in conf.items():
    m = np.array(m)
    share = m / np.maximum(m.sum(1, keepdims=True), 1)
    print(arm)
    print(pd.DataFrame(share, index=[f"true {n}" for n in names], columns=[f"label {n}" for n in names]).round(3).to_string())
    s3[arm] = {"counts": m.tolist(), "row shares": share.round(4).tolist()}
g3 = s[s.scenario == "S3 both dates"].groupby("arm", sort=False)[["after-only error as it is", "after-only error",
                                                                  "before-only error as it is", "before-only error",
                                                                  "cannot in both", "cannot in one-date haze"]].mean()
print(g3.round(3).to_string())
s3["means"] = g3.round(4).reset_index().to_dict("records")
numbers["S3"] = s3

# ---------- task B primary ----------
print("=" * 100, "\nTASK B\n")
seed_arms = [f"hysteresis {lo}, seed" for lo in (50, 35, 20)]
base = per_tile("S1 after haze", "either-date", "grey error")
tests = {arm: sign_test(per_tile("S1 after haze", arm, "grey error").loc[base.index], base) for arm in seed_arms}
adj = holm([tests[a]["p"] for a in seed_arms])
for a, p in zip(seed_arms, adj):
    tests[a]["Holm p"] = p
grown = {arm: sign_test(per_tile("S1 after haze", arm, "grey error").loc[base.index], base)
         for arm in [f"hysteresis {lo}, grown" for lo in (50, 35, 20)]}
he = s1t.loc["single image (He)", "grey error"]
print("B primary, S1 grey error against either-date (today's gate):")
print(pd.DataFrame(tests).T.to_string())
print("grown arms (secondary):")
print(pd.DataFrame(grown).T.to_string())
gap = {arm: float(s1t.loc[arm, "grey error"] - he) for arm in s1t.index}
print("gap to He (mean grey error minus He's):", {k: round(v, 2) for k, v in gap.items()})
numbers["B primary"] = tests
numbers["B grown"] = grown
numbers["B gap to He"] = gap

# ---------- real tiles ----------
print("=" * 100, "\nREAL DEVELOPMENT TILES\n")
r = pd.read_csv(OUT / "real_tiles.csv")
clear_ids = set(s.tile_id)
assert r.tile_id.nunique() == 226, r.tile_id.nunique()
print("road_handling mismatches (existing arm, should be 0):", int(r.drop_duplicates("tile_id")["road_handling mismatches"].sum()))
real = {}
for name, sub in (("94 clear tiles", r[r.tile_id.isin(clear_ids)]), ("all 226 development tiles", r),
                  ("tiles the tile rule scores", r[~r["tile rule cloudy"]])):
    rows = []
    for arm, g in sub.groupby("arm", sort=False):
        row = {"arm": arm, "tiles": len(g), "gated share (mean)": g["gated share"].mean(),
               "gated share (max)": g["gated share"].max(), "fall share (mean)": g["fall share"].mean(),
               "tiles with fall px": int((g["fall share"] > 0).sum()), "both share (mean)": g["both share"].mean(),
               "tiles with both px": int((g["both share"] > 0).sum()), "cannot share (mean)": g["cannot share"].mean(),
               "building px gated (pooled)": g["building gated px"].sum() / max(g["building px"].sum(), 1),
               "building px cannot (pooled)": g["building cannot px"].sum() / max(g["building px"].sum(), 1)}
        for c in ("cannot: both cloudy share", "cannot: opaque after share", "cannot: opaque before share"):
            if c in g:
                row[c.replace(" share", "") + " (mean)"] = g[c].mean()
        rows.append(row)
    t = pd.DataFrame(rows)
    real[name] = t.round(5).to_dict("records")
    print(name)
    print(t.round(4).to_string(index=False), "\n")
numbers["real tiles"] = real
cl = r[r.tile_id.isin(clear_ids)].set_index("arm")
constraints = {}
for arm in seed_arms + [f"hysteresis {lo}, grown" for lo in (50, 35, 20)]:
    g = r[(r.arm == arm) & r.tile_id.isin(clear_ids)]
    c = {"S1 clear ground changed": float(s1t.loc[arm, "clear ground changed"]),
         "real clear tiles gated share (mean)": float(g["gated share"].mean()),
         "real clear tiles building px gated": float(g["building gated px"].sum() / max(g["building px"].sum(), 1))}
    c["constraints hold"] = bool(c["S1 clear ground changed"] <= 0.01 and c["real clear tiles gated share (mean)"] <= 0.01
                                 and c["real clear tiles building px gated"] <= 0.01)
    if arm in tests:
        c["primary holds"] = bool(tests[arm]["Holm p"] < 0.05 and tests[arm]["better"] > tests[arm]["worse"])
        c["meets the plan"] = c["constraints hold"] and c["primary holds"]
    constraints[arm] = c
print("B constraints:")
print(pd.DataFrame(constraints).T.to_string())
numbers["B constraints"] = constraints

# ---------- roads ----------
from sn8_clouds import assessable, cloud_table
from sn8_roads import feature_table
from sn8_stages import production_cloud_rule

ft = pd.concat([feature_table("train"), feature_table("val")], ignore_index=True)
ct = pd.concat([cloud_table("train"), cloud_table("val")], ignore_index=True)
assert ft.tile_id.equals(ct.tile_id) and ft.road_id.equals(ct.road_id)
ft["cloud_dark_rise_road"], ft["dark_rise_road"] = ct.cloud_dark_rise_road, ct.dark_rise_road
ft["n"] = ft.groupby("tile_id").cumcount()
ft["assessable"] = assessable(ft, production_cloud_rule())
ft["set aside why"] = np.where(ft.assessable, "", np.where(ft.cloudy.astype(bool), "tile rule (cloudy tile)", "road rule only"))
rr = pd.read_csv(OUT / "real_roads.csv")
print("=" * 100, f"\nROADS: {len(ft)} development roads; assessable {int(ft.assessable.sum())}; set aside {int((~ft.assessable).sum())}")
print(ft.loc[~ft.assessable, "set aside why"].value_counts().to_string())
dec = {}
for arm, g in rr.groupby("arm", sort=False):
    m = ft[["tile_id", "n", "road_id"]].merge(g, on=["tile_id", "n"], how="left", suffixes=("", "_r"))
    assert m.road_id.astype(str).equals(m.road_id_r.astype(str)), f"{arm}: roads do not line up"
    assert m.decision.notna().all(), f"{arm}: missing decisions"
    dec[arm] = m
arms = list(dec)
counts = pd.DataFrame({a: dec[a].decision.value_counts() for a in arms}).fillna(0).astype(int).T
print("\nDecisions per arm (all development roads)")
print(counts.to_string())
numbers["road decisions"] = counts.to_dict("index")
trans = {}
for a in arms[1:]:
    x = pd.crosstab(dec["existing two-date"].decision, dec[a].decision)
    trans[a] = x.to_dict()
    moved = int((dec["existing two-date"].decision != dec[a].decision).sum())
    print(f"\nexisting two-date (rows) -> {a} (columns): {moved} roads move")
    print(x.to_string())
numbers["road transitions"] = trans
aside = ~ft.assessable.to_numpy()
back = {}
for a in arms:
    d = dec[a].decision.to_numpy()
    b = {"set aside": int(aside.sum()), "come back (ASSESS or CORRECT)": int((aside & (d != "CANNOT ASSESS")).sum()),
         "ASSESS": int((aside & (d == "ASSESS")).sum()), "CORRECT": int((aside & (d == "CORRECT")).sum()),
         "CANNOT ASSESS": int((aside & (d == "CANNOT ASSESS")).sum())}
    for why in ("tile rule (cloudy tile)", "road rule only"):
        w = aside & (ft["set aside why"].to_numpy() == why)
        b[f"{why}: set aside"] = int(w.sum())
        b[f"{why}: come back"] = int((w & (d != "CANNOT ASSESS")).sum())
    keep = ft.assessable.to_numpy()
    b["assessable roads that would become CANNOT ASSESS"] = int((keep & (d == "CANNOT ASSESS")).sum())
    b["assessable roads that would become CORRECT"] = int((keep & (d == "CORRECT")).sum())
    back[a] = b
print("\nSet-aside roads under each arm")
print(pd.DataFrame(back).T.to_string())
numbers["set-aside roads"] = back
# edge loss
ft["edge loss"] = ft.edge_before - ft.edge_after
top = ft["edge loss"] >= ft["edge loss"].quantile(0.75)
check = {"top-quartile roads": int(top.sum()), "caught by the cloud rule (set aside)": float((~ft.assessable[top]).mean()),
         "caught by the road rule (dark-rise share >= 0.2)": float((ft.cloud_dark_rise_road[top] >= 0.2).mean()),
         "dark channel up by more than 20 (strip mean)": float((ft.dark_rise_road[top] > 20).mean()),
         "median edge loss": float(ft["edge loss"][top].median())}
for a in arms:
    check[f"gated >= 20% of the strip: {a}"] = float((dec[a].gated.to_numpy()[top.to_numpy()] >= 0.2).mean())
print("\nEdge loss, the quarter of development roads with the most:", json.dumps(check, indent=1))
numbers["edge loss"] = check
json.dump(numbers, open(OUT / "numbers.json", "w"), indent=1, default=float)
print("\nwritten numbers.json")
