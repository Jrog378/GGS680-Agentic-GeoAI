"""Smoke test (NOT scored, not used to choose anything): every Phase G arm on the 3 smoke tiles (2_23_44, 2_15_45,
2_19_55): shapes, ranges, abstentions, timings, and one figure per family. Writes smoke_results.json and
figures/method_bench_3/smoke_*.png. No labels, no NOAA, no flood calls are read.
    OMP_NUM_THREADS=2 nice -n 10 python3 -I smoke_test.py > smoke_test.log 2>&1
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b3_common as K

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

T0 = time.time()


def main():
    from sn8_clouds import _tile
    from sn8_cloudspot import _strip
    from sn8_lines import road_band
    from sn8_refhaze import dark_reference_dehaze
    import g3_corr, g3_gates
    K.dev_guard_tiles(list(K.SMOKE_TILES))
    TH = g3_gates.thresholds(T0)
    K.FIG.mkdir(parents=True, exist_ok=True)
    out = {"thresholds": TH, "tiles": {}}
    for tid in K.SMOKE_TILES:
        K.wait_for_memory(T0)
        p, b, a, v = _tile(tid)
        t1 = time.time()
        masks, minfo = g3_gates.masks(p, b, a, v, TH)
        tg = time.time() - t1
        c0 = dark_reference_dehaze(b, a, v)
        t1 = time.time()
        outs = g3_corr.outputs(b, a, v, c0)
        tc = time.time() - t1
        band = road_band()
        strip, roads, n, cpx = _strip(tid, p, v, band)
        u1, u1i = g3_gates.u1_cues(tid, p, b, a, v, strip, roads, n, cpx) if n else ([], {})
        rec = {"gate_seconds": tg, "corr_seconds": tc, "share": minfo["share"], "B1": minfo["B1"],
               "B2": {k: minfo[k] for k in minfo if k.startswith("B2")}, "T1": minfo["T1"],
               "C0_gate_px": int(c0["gate"].sum()), "u1_roads": u1, "u1_em": u1i.get("em"), "corr": {}}
        raw = np.where(v, a, 0)
        for arm, o in outs.items():
            img = o["corrected"]
            g = c0["gate"] & v
            rec["corr"][arm] = {"info": o["info"], "opaque_px": int(o["opaque"].sum()),
                                "min": float(img[v].min()), "max": float(img[v].max()),
                                "mean_in_gate": float(img[g].mean()) if g.any() else None,
                                "C0_mean_in_gate": float(c0["corrected"][g].mean()) if g.any() else None,
                                "after_mean_in_gate": float(a[g].mean()) if g.any() else None,
                                "mean_abs_vs_C0": float(np.abs(img - c0["corrected"])[v].mean()),
                                "t_median_in_gate": float(np.median(o["t"][g])) if g.any() else None,
                                "changed_share": float((img != raw)[v].mean())}
        out["tiles"][tid] = rec
        K.log(T0, f"{tid}: gates {tg:.1f} s, corrections {tc:.1f} s; shares {minfo['share']}")
        # figure 1: gates
        keys = ["rise", "T1", "T1b", "B1", "B1p", "B2-1.6"] + (["T1d"] if "T1d" in masks else [])
        fig, ax = plt.subplots(1, len(keys) + 1, figsize=(3.2 * (len(keys) + 1), 3.4))
        ax[0].imshow(a, cmap="gray", vmin=0, vmax=255); ax[0].set_title(f"{tid} after")
        for i, k in enumerate(keys, 1):
            ax[i].imshow(a, cmap="gray", vmin=0, vmax=255)
            ax[i].imshow(np.ma.masked_where(~masks[k], masks[k]), cmap="autumn", alpha=0.45)
            ax[i].set_title(f"{k}: {100 * masks[k][v].mean():.1f}%")
        for x in ax:
            x.axis("off")
        fig.tight_layout(); fig.savefig(K.FIG / f"smoke_gates_{tid}.png", dpi=80); plt.close(fig)
        # figure 2: corrections
        arms = ["C0"] + list(outs)
        fig, ax = plt.subplots(2, len(arms) + 1, figsize=(3.0 * (len(arms) + 1), 6.2))
        ax[0, 0].imshow(b, cmap="gray", vmin=0, vmax=255); ax[0, 0].set_title("before")
        ax[1, 0].imshow(a, cmap="gray", vmin=0, vmax=255); ax[1, 0].set_title("after (as is)")
        for i, arm in enumerate(arms, 1):
            o = c0 if arm == "C0" else outs[arm]
            ax[0, i].imshow(o["corrected"], cmap="gray", vmin=0, vmax=255); ax[0, i].set_title(arm[:22], fontsize=8)
            ax[1, i].imshow(np.where(v, o["t"], np.nan), cmap="viridis", vmin=0, vmax=1); ax[1, i].set_title("t")
        for x in ax.ravel():
            x.axis("off")
        fig.tight_layout(); fig.savefig(K.FIG / f"smoke_corr_{tid}.png", dpi=70); plt.close(fig)
    K.write_json(K.HERE / "smoke_results.json", out)
    K.log(T0, "done")


if __name__ == "__main__":
    main()
