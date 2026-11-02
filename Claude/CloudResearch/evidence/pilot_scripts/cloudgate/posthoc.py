"""POST-HOC descriptive checks (not in outputs/preregistration_cloud_gate.md; written after the results were seen, to
read them). No new scores: re-tabulations of real_tiles.csv / real_roads.csv and the cached road tables."""
import sys
from pathlib import Path
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd
OUT = Path(__file__).resolve().parent
pd.set_option("display.width", 200)
r = pd.read_csv(OUT / "real_tiles.csv")
s = pd.read_csv(OUT / "synthetic_tiles.csv")
clear = set(s.tile_id)
print("1. Real clear tiles (94): AFTER-date gate only (rise share), so task B is seen without task A's fall-gate alarms")
t = r[r.tile_id.isin(clear)].groupby("arm", sort=False).agg(rise_mean=("rise share", "mean"), rise_max=("rise share", "max"),
    tiles_with_rise=("rise share", lambda x: int((x > 0).sum())), fall_mean=("fall share", "mean"))
print(t.round(4).to_string(), "\n")
print("2. Development tiles with the largest fall-gate share (either-date)")
e = r[r.arm == "either-date"].sort_values("fall share", ascending=False)
print(e[["tile_id", "tile rule cloudy", "fall share", "both share", "rise share"]].head(12).round(4).to_string(index=False), "\n")
print("   tiles with both-cloudy pixels (either-date):")
print(e[e["both share"] > 0][["tile_id", "both share", "building cannot px"]].round(4).to_string(index=False), "\n")
from sn8_clouds import assessable, cloud_table
from sn8_roads import feature_table
from sn8_stages import production_cloud_rule
ft = pd.concat([feature_table("train"), feature_table("val")], ignore_index=True)
ct = pd.concat([cloud_table("train"), cloud_table("val")], ignore_index=True)
ft["cloud_dark_rise_road"], ft["dark_rise"] = ct.cloud_dark_rise_road, ct.dark_rise_road
ft["assessable"] = assessable(ft, production_cloud_rule())
ft["edge loss"] = ft.edge_before - ft.edge_after
print("3. Edge-loss definitions (the earlier 15% / 42% figures)")
for name, sub in (("all 1,037 development roads", ft), ("891 tile-rule roads", ft[~ft.cloudy.astype(bool)]),
                  ("798 assessable roads", ft[ft.assessable])):
    top = sub[sub["edge loss"] >= sub["edge loss"].quantile(0.75)]
    print(f"   {name}: top quarter {len(top)}; road rule (rise share >= 0.2) {100 * (top.cloud_dark_rise_road >= 0.2).mean():.0f}%; "
          f"set aside {100 * (~top.assessable).mean():.0f}%; dark rise > 20 {100 * (top.dark_rise > 20).mean():.0f}%; "
          f"dark rise 20-71 {100 * ((top.dark_rise > 20) & (top.dark_rise <= 71)).mean():.0f}%")
print()
rr = pd.read_csv(OUT / "real_roads.csv")
print("4. Roads on the B picture tile 2_16_37, by arm (label-free)")
x = rr[rr.tile_id == "2_16_37"].pivot_table(index=["n", "road_id"], columns="arm", values="decision", aggfunc="first")
print(x[["existing two-date", "either-date", "hysteresis 50, seed", "hysteresis 35, seed", "hysteresis 20, seed"]].to_string(), "\n")
print("5. Why hysteresis 20 sends roads to CANNOT ASSESS: tiles where the 'opaque' share grows most against either-date")
p = r.pivot_table(index="tile_id", columns="arm", values="cannot share")
d = (p["hysteresis 20, seed"] - p["either-date"]).sort_values(ascending=False)
g20 = r[r.arm == "hysteresis 20, seed"].set_index("tile_id")
print(pd.DataFrame({"cannot either-date": p["either-date"], "cannot h20": p["hysteresis 20, seed"],
                    "gated h20": g20["gated share"]}).loc[d.index[:8]].round(3).to_string())

print("\n6. Edge loss on the 891 tile-rule roads (the definition the earlier figures used): top quarter gated >= 20%")
ft["n"] = ft.groupby("tile_id").cumcount()
sub = ft[~ft.cloudy.astype(bool)]
top = sub[sub["edge loss"] >= sub["edge loss"].quantile(0.75)][["tile_id", "n"]]
for arm, g in rr.groupby("arm", sort=False):
    m = top.merge(g, on=["tile_id", "n"], how="left")
    print(f"   {arm}: {100 * (m.gated >= 0.2).mean():.0f}% of {len(m)}")

# 7. post-hoc picture: the development tile with the largest fall-gate share (what the before-cloudy label is on real data)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sn8_clouds import _tile, dark_channel
from sn8_cloudsym import either_date_dehaze
from sn8_lines import CREDIT
tid = "0_24_20"
p, before, after, valid = _tile(tid)
o = either_date_dehaze(before, after, valid)
db, da = dark_channel(before, valid), dark_channel(after, valid)
fig, ax = plt.subplots(1, 5, figsize=(28, 7.2))
for k, (img, name) in enumerate(((before, f"{tid} before"), (after, "after"), (o["before corrected"], "before, either-date corrected"))):
    ax[k].imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
    ax[k].set_title(name, fontsize=10)
ax[3].imshow(np.where(valid, before, 0), cmap="gray", vmin=0, vmax=255)
lab = np.ma.masked_where(o["labels"] == 0, o["labels"])
ax[3].imshow(lab, cmap=ListedColormap([(0, 0, 0, 0), "orange", "deepskyblue", "red"]), vmin=0, vmax=3, alpha=0.45, interpolation="nearest")
ax[3].set_title(f"labels over the before (blue = before cloudy, {100 * (o['labels'] == 2)[valid].mean():.0f}% of tile)", fontsize=10)
im = ax[4].imshow(np.where(valid, da - db, np.nan), cmap="RdBu_r", vmin=-120, vmax=120)
ax[4].set_title("dark-channel change, after - before", fontsize=10)
plt.colorbar(im, ax=ax[4], fraction=0.04)
for a in ax:
    a.axis("off")
fig.text(0.5, 0.01, CREDIT + ". POST-HOC picture (not in the plan): the development tile with the largest before-cloudy share.", ha="center", fontsize=8)
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "fig_posthoc_real_fall_gate.png", dpi=100)
print("saved fig_posthoc_real_fall_gate.png")

print("\n8. Diagnostic with the development flood labels (post-hoc): roads the either-date method moves, and roads whose")
print("   gated strip is mostly the BEFORE date (fall gate), against the base rate")
ex = rr[rr.arm == "existing two-date"].set_index(["tile_id", "n"])
for arm in ("either-date", "either-date, both smooth", "hysteresis 35, seed"):
    a = rr[rr.arm == arm].set_index(["tile_id", "n"])
    moved = a.decision != ex.decision
    before_date = (a.date == "before cloudy") & (a.gated >= 0.2)
    print(f"   {arm}: moved {int(moved.sum())}, of them labelled flooded {int(a['flooded label'][moved].sum())}; "
          f"roads gated mostly on the before date {int(before_date.sum())}, labelled flooded {int(a['flooded label'][before_date].sum())}")
base = ex["flooded label"].mean()
print(f"   base rate: {100 * base:.0f}% of the {len(ex)} development roads are labelled flooded")
