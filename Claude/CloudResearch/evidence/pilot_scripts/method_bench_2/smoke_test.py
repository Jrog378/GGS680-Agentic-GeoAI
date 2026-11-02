"""Smoke test (unit test) of every bench-2 arm on 2-3 development tiles: shapes, ranges, abstentions, timing, and one
figure per arm in figures/method_bench_2/. NOT scoring: no flood labels, no NOAA, nothing chosen from these numbers.
A2 (HOT) is tested on synthetic haze only (it is not runnable on SN8 without a water mask).
    OMP_NUM_THREADS=2 nice -n 10 python3 -I smoke_test.py [tile ...] > smoke_test.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_common as B

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage as ndi

T0 = time.time()
OUT = B.HERE / "smoke_results.json"


def slug(name):
    import re
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def rng_of(img, m):
    v = img[m]
    return [float(v.min()), float(v.max())] if v.size else [None, None]


def summarise(name, tid, o, after, valid, sec):
    img = o["corrected"]
    assert img.shape == after.shape and img.dtype == np.float32, (name, img.shape, img.dtype)
    assert np.isfinite(img).all(), name
    assert (img[~valid] == 0).all(), f"{name}: no-data not 0"
    assert img[valid].min() >= 1 and img[valid].max() <= 255, f"{name}: range {rng_of(img, valid)}"
    t = np.nan_to_num(o["t"], nan=1.0)
    assert t.min() >= 0 and t.max() <= 1, name
    raw = np.where(valid, after, 0)
    info = {k: v for k, v in (o.get("info") or {}).items() if k not in ("passes",)}
    return {"arm": name, "tile": tid, "seconds": round(sec, 2), "gate_px": int(o["gate"].sum()),
            "opaque_px": int(o["opaque"].sum()), "changed_px": int((img != raw).sum()),
            "changed_share_valid": float((img != raw)[valid].mean()), "range_valid": rng_of(img, valid),
            "abstain": info.get("abstain"), "info": info}


def crop_box(gate, valid, size=500):
    if gate.any():
        r, c = ndi.center_of_mass(gate)
    else:
        r, c = np.array(valid.shape) / 2
    r0 = int(np.clip(r - size / 2, 0, valid.shape[0] - size))
    c0 = int(np.clip(c - size / 2, 0, valid.shape[1] - size))
    return slice(r0, r0 + size), slice(c0, c0 + size)


def main():
    from sn8_clouds import _maps, _tile
    from sn8_refhaze import dark_reference_dehaze, tone_curve
    from c_common import darkref_variant, CLEAR_MARGIN_PX
    import a1_chavez, g1_hysteresis, g2_lin_bluerise, n1_du, n2_schott, n3_lin, n4_ridge
    tiles = sys.argv[1:] or list(B.SMOKE_TILES)
    B.dev_guard_tiles(tiles)
    h0 = B.registry_hash()
    B.FIG.mkdir(parents=True, exist_ok=True)
    rows, gates, tones, chav = [], {}, {}, {}
    data = {}
    for tid in tiles:
        free, swap = B.wait_for_memory(T0)
        B.log(T0, f"{tid}: memory free {free}% swap {swap:.2f} GB")
        p, before, after, valid = _tile(tid)
        assert before.shape == after.shape == valid.shape and p["after_rgb"].shape == (*valid.shape, 3)
        c0 = dark_reference_dehaze(before, after, valid)
        mine = darkref_variant(before, after, valid)
        assert all(np.array_equal(c0[k], mine[k]) for k in ("corrected", "gate", "opaque")), "c_common != library"
        clear = valid & ~ndi.binary_dilation(c0["gate"], iterations=CLEAR_MARGIN_PX)
        rise = _maps(p, valid)["masks"]["dark rise"]
        data[tid] = (p, before, after, valid, c0, clear, rise)
        rows.append(summarise("C0", tid, c0, after, valid, 0.0))
        # ---- gates
        g = {}
        for name, blob in (("G1 hysteresis", None), ("G1b hysteresis + blob", 2500.0)):
            t1 = time.time()
            m, th = g1_hysteresis.gate(before, after, valid, blob)
            g[name] = m
            rows.append({"arm": name, "tile": tid, "seconds": round(time.time() - t1, 2), "gate_px": int(m.sum()),
                         "gate_share_valid": float(m[valid].mean()), "info": th,
                         "prod_rise_share_valid": float(rise[valid].mean()),
                         "c0_gate_share_valid": float(c0["gate"][valid].mean()),
                         "overlap_with_prod_rise": float((m & rise).sum() / max(m.sum(), 1))})
            B.log(T0, f"{tid} {name}: t_p {th['t_p']:.2f} (z_p {th['z_p']:.2f}, mean {th['mean']:.2f}, median "
                      f"{th['median']:.2f}) t_l {th['t_l']:.2f} t_h {th['t_h']:.2f}; share {m[valid].mean():.4f} "
                      f"(production dark rise {rise[valid].mean():.4f})")
        t1 = time.time()
        br, binfo = g2_lin_bluerise.blue_rise(p["before_rgb"], p["after_rgb"], valid)
        g["G2 blue rise (rise map)"] = br
        rows.append({"arm": "G2 blue rise", "tile": tid, "seconds": round(time.time() - t1, 2),
                     "rise_range_valid": rng_of(br, valid), "rise_p50_p99": np.percentile(br[valid], [50, 99]).tolist(),
                     "info": binfo})
        gates[tid] = g
        # ---- correction arms (C0 arithmetic, one step swapped)
        arms = {
            "N1 Du PIF": lambda: n1_du.correct(before, after, valid),
            "N2 Schott roofs+roads": lambda: n2_schott.correct(tid, p, before, after, valid, False),
            "N2b Schott roofs": lambda: n2_schott.correct(tid, p, before, after, valid, True),
            "N3 Lin wPCA": lambda: n3_lin.correct(before, after, valid, p["before_rgb"], p["after_rgb"]),
            "N4 Song ridge all": lambda: n4_ridge.correct(before, after, valid, False),
            "N4b Song ridge clear": lambda: n4_ridge.correct(before, after, valid, True),
            "G1 as correction gate": lambda: darkref_variant(before, after, valid, gate=g["G1 hysteresis"]),
            "G1b as correction gate": lambda: darkref_variant(before, after, valid, gate=g["G1b hysteresis + blob"]),
        }
        tones[tid] = {}
        for name, fn in arms.items():
            t1 = time.time()
            o = fn()
            r = summarise(name, tid, o, after, valid, time.time() - t1)
            if name.startswith("N2"):
                bld, road = n2_schott.footprints(tid, p, valid.shape, valid)
                r["info"]["buildings_px"], r["info"]["road_strip_px"] = int(bld.sum()), int(road.sum())
            rows.append(r)
            tones[tid][name] = o
            B.log(T0, f"{tid} {name}: {r['seconds']} s, changed {r['changed_share_valid']:.4f}, opaque {r['opaque_px']}, "
                      f"abstain {r['abstain']}, info {({k: v for k, v in r['info'].items() if k in ('gain', 'offset', 'slope', 'intercept', 'r', 'd', 'pif_px', 'eps_T', 'SL_reselected', 'SL_all_candidates', 'water_removed_share_of_clear')})}")
        chav[tid] = {}
        for k in a1_chavez.K:
            t1 = time.time()
            o = a1_chavez.correct(before, after, valid, p["after_rgb"], c0, k)
            r = summarise(f"A1 Chavez k={k}", tid, o, after, valid, time.time() - t1)
            if "corrected_rgb" in o:
                assert o["corrected_rgb"].shape == p["after_rgb"].shape
                assert o["corrected_rgb"].min() >= 0 and o["corrected_rgb"].max() <= 255
                # outside the gate + fade (t = 1) nothing may change
                t1m = np.nan_to_num(c0["t"], nan=1.0) >= 1
                r["max_change_where_t1"] = float(np.abs(o["corrected"] - np.where(valid, after, 0))[t1m & valid].max())
            rows.append(r)
            chav[tid][k] = o
            B.log(T0, f"{tid} A1 k={k}: A_rgb {[round(a, 1) for a in r['info'].get('A_rgb', [])]}, C0 grey A "
                      f"{c0['airlight']:.1f}, changed {r['changed_share_valid']:.4f}")
    # ---- G2 provisional threshold (SMOKE ONLY: Otsu over these tiles' pooled blue rise; the run uses the training tiles)
    from skimage.filters import threshold_otsu
    pooled = np.concatenate([gates[t]["G2 blue rise (rise map)"][data[t][3]][::16] for t in tiles])
    T_smoke = float(threshold_otsu(pooled))
    for tid in tiles:
        valid = data[tid][3]
        m = valid & (gates[tid]["G2 blue rise (rise map)"] > T_smoke)
        gates[tid]["G2 blue rise"] = m
        rows.append({"arm": "G2 blue rise (smoke threshold)", "tile": tid, "T_smoke": T_smoke,
                     "gate_share_valid": float(m[valid].mean()),
                     "overlap_with_prod_rise": float((m & data[tid][6]).sum() / max(m.sum(), 1))})
        B.log(T0, f"{tid} G2 (smoke T {T_smoke:.2f}): share {m[valid].mean():.4f}")
    # ---- A2 synthetic test (no SN8 water mask exists; synthetic image has no water)
    rows += a2_synthetic(data[tiles[1] if len(tiles) > 1 else tiles[0]])
    B.write_json(OUT, {"tiles": tiles, "rows": rows})
    figures(tiles, data, gates, tones, chav)
    assert B.registry_hash() == h0
    B.log(T0, "done")


def a2_synthetic(d):
    """Synthetic haze with a known answer on a before (pre-storm) RGB image: additive haze A_i (1 - t) in a smooth blob,
    A = (230, 235, 245) RGB, t from 1 down to 0.6; the arm subtracts per HOT level. Error inside the blob, before vs after
    correction. The 'water' mask is empty (synthetic scene; stated)."""
    import a2_hot
    p, _, _, valid = d[:4]
    clean = p["before_rgb"].astype(np.float64)
    h, w = valid.shape
    yy, xx = np.mgrid[0:h, 0:w]
    blob = np.exp(-(((yy - h * 0.5) / (h * 0.18)) ** 2 + ((xx - w * 0.5) / (w * 0.18)) ** 2))
    t = 1 - 0.4 * blob
    A = np.array([230.0, 235.0, 245.0])
    # additive part only (Zhang's model is a dark-object subtraction): haze_i = A_i (1 - t) * (lambda_i / lambda_b)^-1
    lam = np.array([0.66, 0.545, 0.48])
    add = (1 - t)[..., None] * A[None, None, :] * (lam / 0.48)[None, None, :] ** -1.0 * 0.25
    hazy = np.clip(clean + add, 0, 255)
    clear = valid & (blob < 0.01)
    water = np.zeros(valid.shape, bool)
    t1 = time.time()
    try:
        a2_hot.remove_haze(hazy, valid, clear, None)
        raised = False
    except ValueError:
        raised = True
    res = a2_hot.remove_haze(hazy, valid, clear, water)
    sec = time.time() - t1
    inside = valid & (blob > 0.3)
    err_before = np.abs(hazy - clean)[inside].mean(0)
    err_after = np.abs(res["rgb"] - clean)[inside].mean(0)
    # code check where the paper's assumption holds by construction: a grey surface (R = G = B), so HOT moves only
    # with haze and "similar dark targets are present under all haze conditions"
    g = np.repeat(B.grey601(p["before_rgb"])[..., None], 3, -1)
    hazy_g = np.clip(g + add, 0, 255)
    res_g = a2_hot.remove_haze(hazy_g, valid, clear, water)
    eg_before = np.abs(hazy_g - g)[inside].mean(0)
    eg_after = np.abs(res_g["rgb"] - g)[inside].mean(0)
    B.log(T0, f"A2 synthetic, grey surface: mean |error| RGB inside the blob {eg_before.round(2)} -> {eg_after.round(2)}")
    np.savez_compressed(B.BIG / "smoke_a2.npz", clean=clean.astype(np.uint8), hazy=hazy.astype(np.uint8),
                        out=res["rgb"].astype(np.uint8), hot=res["hot"].astype(np.float32)) if B.BIG.exists() else None
    a2_synthetic.res = (clean, hazy, res, blob)
    B.log(T0, f"A2 synthetic: raises without a water mask: {raised}; mean |error| RGB inside the blob {err_before.round(2)} "
              f"-> {err_after.round(2)}; CL slope {res['slope']:.3f}, h_clear {res['h_clear']}, {sec:.1f} s")
    return [{"arm": "A2 HOT (synthetic)", "tile": "synthetic on before RGB", "seconds": round(sec, 2),
             "raises_without_water_mask": raised, "err_rgb_before": err_before.tolist(),
             "err_rgb_after": err_after.tolist(), "grey_surface_err_before": eg_before.tolist(),
             "grey_surface_err_after": eg_after.tolist(), "cl_slope": res["slope"], "h_clear": res["h_clear"],
             "out_range": [float(res["rgb"].min()), float(res["rgb"].max())]}]


def figures(tiles, data, gates, tones, chav):
    from sn8_refhaze import tone_curve
    n = len(tiles)
    # gates
    for name in ("G1 hysteresis", "G1b hysteresis + blob", "G2 blue rise"):
        fig, ax = plt.subplots(n, 4, figsize=(16, 4 * n), squeeze=False)
        for i, tid in enumerate(tiles):
            p, before, after, valid, c0, clear, rise = data[tid]
            ax[i, 0].imshow(before, cmap="gray", vmin=0, vmax=255); ax[i, 0].set_title(f"{tid} before")
            ax[i, 1].imshow(after, cmap="gray", vmin=0, vmax=255); ax[i, 1].set_title("after")
            ax[i, 2].imshow(rise, cmap="magma"); ax[i, 2].set_title(f"production dark rise ({rise[valid].mean():.3f})")
            m = gates[tid][name]
            ax[i, 3].imshow(after, cmap="gray", vmin=0, vmax=255)
            ax[i, 3].imshow(np.ma.masked_where(~m, m), cmap="autumn", alpha=0.5)
            ax[i, 3].set_title(f"{name} ({m[valid].mean():.3f})")
        for a in ax.flat:
            a.set_xticks([]); a.set_yticks([])
        sub = " (SMOKE threshold: Otsu over these tiles, not the run's)" if name.startswith("G2") else ""
        fig.suptitle(f"Bench 2 smoke test: {name}{sub}. Share of valid pixels in brackets. Not scored.")
        fig.tight_layout()
        fig.savefig(B.FIG / f"smoke_{slug(name)}.png", dpi=70)
        plt.close(fig)
    # tone arms: density of before vs after (clear pixels) with C0's curve and the arm's line, + corrected crop
    for name in ("N1 Du PIF", "N2 Schott roofs+roads", "N2b Schott roofs", "N3 Lin wPCA", "N4 Song ridge all",
                 "N4b Song ridge clear", "G1 as correction gate", "G1b as correction gate"):
        fig, ax = plt.subplots(n, 4, figsize=(17, 4.2 * n), squeeze=False)
        for i, tid in enumerate(tiles):
            p, before, after, valid, c0, clear, rise = data[tid]
            o = tones[tid][name]
            H, xe, ye = np.histogram2d(before[clear], after[clear], bins=128, range=[[0, 256], [0, 256]])
            ax[i, 0].imshow(np.log1p(H.T), origin="lower", extent=[0, 256, 0, 256], cmap="Greys")
            tone, _, _ = tone_curve(before, after, clear)
            xs = np.arange(256)
            ax[i, 0].plot(xs, tone(xs), "c-", lw=1.5, label="C0 quantile curve")
            info = o.get("info") or {}
            g, off = info.get("gain", info.get("slope")), info.get("offset", info.get("intercept"))
            if g is not None and off is not None and not info.get("abstain"):
                ax[i, 0].plot(xs, g * xs + off, "r-", lw=1.5, label="arm line")
            ax[i, 0].set_xlim(0, 256); ax[i, 0].set_ylim(0, 256)
            ax[i, 0].set_xlabel("before grey"); ax[i, 0].set_ylabel("after grey"); ax[i, 0].legend(fontsize=7)
            ax[i, 0].set_title(f"{tid}: {'ABSTAIN: ' + info['abstain'] if info.get('abstain') else 'fit'}", fontsize=9)
            rs, cs = crop_box(o["gate"], valid)
            ax[i, 1].imshow(after[rs, cs], cmap="gray", vmin=0, vmax=255); ax[i, 1].set_title("after (crop)")
            ax[i, 2].imshow(c0["corrected"][rs, cs], cmap="gray", vmin=0, vmax=255); ax[i, 2].set_title("C0 corrected")
            ax[i, 3].imshow(o["corrected"][rs, cs], cmap="gray", vmin=0, vmax=255); ax[i, 3].set_title(f"{name}")
            for a in ax[i, 1:]:
                a.set_xticks([]); a.set_yticks([])
        fig.suptitle(f"Bench 2 smoke test: {name}. Density = C0's clear pixels. Not scored.")
        fig.tight_layout()
        fig.savefig(B.FIG / f"smoke_{slug(name)}.png", dpi=70)
        plt.close(fig)
    # Chavez: RGB crops for each k
    ks = list(chav[tiles[0]].keys())
    fig, ax = plt.subplots(n, len(ks) + 1, figsize=(3.4 * (len(ks) + 1), 3.6 * n), squeeze=False)
    for i, tid in enumerate(tiles):
        p, before, after, valid, c0, clear, rise = data[tid]
        rs, cs = crop_box(c0["gate"], valid)
        ax[i, 0].imshow(p["after_rgb"][rs, cs]); ax[i, 0].set_title(f"{tid} after RGB", fontsize=9)
        for j, k in enumerate(ks):
            o = chav[tid][k]
            img = o.get("corrected_rgb")
            if img is not None:
                ax[i, j + 1].imshow(img[rs, cs].astype(np.uint8))
                A = o["info"]["A_rgb"]
                ax[i, j + 1].set_title(f"k={k} A=({A[0]:.0f},{A[1]:.0f},{A[2]:.0f})", fontsize=9)
            else:
                ax[i, j + 1].set_title(f"k={k}: abstain", fontsize=9)
    for a in ax.flat:
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle("Bench 2 smoke test: A1 Chavez band-linked airlight (RGB, C0's t). Not scored.")
    fig.tight_layout()
    fig.savefig(B.FIG / "smoke_A1.png", dpi=70)
    plt.close(fig)
    # A2 synthetic
    clean, hazy, res, blob = a2_synthetic.res
    fig, ax = plt.subplots(1, 4, figsize=(18, 4.6))
    for a, img, t in zip(ax, (clean, hazy, res["rgb"]), ("clean (before RGB)", "synthetic haze", "A2 HOT-level removal")):
        a.imshow(img.astype(np.uint8)); a.set_title(t)
    im = ax[3].imshow(res["hot"], cmap="viridis"); ax[3].set_title("HOT"); plt.colorbar(im, ax=ax[3], fraction=0.046)
    for a in ax:
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle("Bench 2 smoke test: A2 Zhang 2002 HOT on SYNTHETIC haze (not runnable on SN8: no water mask)")
    fig.tight_layout()
    fig.savefig(B.FIG / "smoke_A2_synthetic.png", dpi=70)
    plt.close(fig)


if __name__ == "__main__":
    main()
