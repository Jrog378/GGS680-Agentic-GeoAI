"""Phase A step 2 pictures: roads production calls clear that carry elevated haze scores, and clean controls.
Before RGB / after RGB / dark-channel rise / HOT / contrast attenuation, cropped around the road, strip outlined.
    nice -n 10 /opt/miniconda3/bin/python -I fig_panels.py > fig_panels.log 2>&1"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from haze_common import FIG, HERE, tile_maps

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

PAD_PX = 120          # 60 m around the strip
N_HAZY, N_CTRL = 6, 2


def pick():
    e = pd.read_csv(HERE / "phaseA_elevated.csv")
    el = e[[c for c in e if c.startswith("elev_")]].sum(1)
    e["n_el"] = el
    e["score"] = e.rise_med.rank(pct=True) + e.hot_post_med.rank(pct=True)
    chosen = []                                       # the 3 highest-rise and 3 highest-HOT kept roads, one per tile
    for col, kind in (("rise_med", "highest rise, gate says clear"), ("hot_post_med", "highest HOT, gate says clear")):
        n = 0
        for _, r in e.sort_values(col, ascending=False).iterrows():
            if r.tile_id in {c[0].tile_id for c in chosen}:
                continue
            chosen.append((r, kind))
            n += 1
            if n == N_HAZY // 2:
                break
    ctrl = e[(e.n_el == 0) & (e.cloud_dark_rise_road == 0) & ~e.flooded].sort_values("score")
    ctrl = ctrl[~ctrl.tile_id.isin([c[0].tile_id for c in chosen])].drop_duplicates("tile_id").head(N_CTRL)
    return chosen + [(r, "clean control") for _, r in ctrl.iterrows()]


def strip_of(t, road_id, tile_rows_before):
    from sn8_roads import MIN_ROAD_PX
    ks = [k for k in range(len(t["roads"]) - 1) if t["centre"][k] >= MIN_ROAD_PX]
    ids = [t["roads"][k + 1]["road_id"] for k in ks]
    j = ids.index(road_id)
    return t["strip"] == ks[j] + 1


def main():
    items = pick()
    fig, axes = plt.subplots(len(items), 5, figsize=(22, 4.3 * len(items)))
    for row, (r, kind) in zip(axes, items):
        t = tile_maps(r.tile_id)
        s = strip_of(t, r.road_id, None)
        rr, cc = np.nonzero(s)
        r0, r1 = max(rr.min() - PAD_PX, 0), min(rr.max() + PAD_PX, s.shape[0])
        c0, c1 = max(cc.min() - PAD_PX, 0), min(cc.max() + PAD_PX, s.shape[1])
        sl = (slice(r0, r1), slice(c0, c1))
        edge = s & ~ndi.binary_erosion(s, iterations=2)
        p = t["p"]
        panels = [(p["before_rgb"][sl], "before (RGB)", None), (p["after_rgb"][sl], "after (RGB)", None),
                  (t["rise"][sl], "dark-channel rise (grey levels)", (-30, 30)),
                  (t["hot_post"][sl], "HOT, after (Zhang 2002)", (-15, 15)),
                  (t["atten"][sl], "contrast attenuation (log)", (-1, 1))]
        for ax, (img, title, lim) in zip(row, panels):
            if lim is None:
                ax.imshow(img)
            else:
                im = ax.imshow(img, cmap="RdBu_r", vmin=lim[0], vmax=lim[1])
                plt.colorbar(im, ax=ax, fraction=0.04)
            ov = np.ma.masked_where(~edge[sl], edge[sl])
            ax.imshow(ov, cmap="autumn", alpha=1, interpolation="nearest")
            ax.set_title(title if ax is not row[0] else "", fontsize=9)
            ax.axis("off")
        row[0].set_title(f"{kind}: {r.tile_id} {r.road_id}\n{'flooded' if r.flooded else 'not marked flooded'}; "
                         f"rise {r.rise_med:.1f}, HOT {r.hot_post_med:.1f}, atten {r.atten_med:.2f}, "
                         f"spot {r.spot_post_mean:.2f}; dark-rise mask {100 * r.cloud_dark_rise_road:.0f}%\nbefore (RGB)",
                         fontsize=9, loc="left")
    fig.text(0.5, 0.003, "Imagery: Maxar, via SpaceNet 8 (SpaceNet LLC), CC BY-SA 4.0. Yellow/red outline: the road "
             "strip. Rise and HOT: red = hazier after the storm.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.01, 1, 1))
    fig.savefig(FIG / "A2_hazy_roads_panels.png", dpi=90)
    print("saved", FIG / "A2_hazy_roads_panels.png")
    for r, kind in items:
        print(kind, r.tile_id, r.road_id, bool(r.flooded), round(r.rise_med, 2), round(r.hot_post_med, 2))


if __name__ == "__main__":
    main()
