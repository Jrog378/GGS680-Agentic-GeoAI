"""Scoring (b): correction arms against the NOAA aerial reference, reusing the Ida test's frozen preparation read-only
(ida_clear_view_cache/prep/<tile>.npz: score mask, NOAA grey aligned and tone-matched to the after image, guard).

Per usable tile (prep row coreg_ok) with >= 2,000 thin pixels (thin = score & C0's gate & not opaque):
  secondary (every tile): grey error |arm - NOAA| and edge correlation (sn8_coreg._gradient) in thin and in the ring
     (score, outside C0's gate, 0-40 m from it); guard grey change |arm - as is| on the Ida guard.
  primary (budgeted): DINOv2 patch-feature distance to NOAA (1 - cosine of sn8_dino tokens, valid = the score mask for
     every image, as the Ida test) in thin and in the ring. Only the sn8_dino windows (2 x 2) holding thin or ring
     pixels are computed (identical to the full computation there); identical window inputs share tokens. Tiles in
     decreasing thin-pixel order, every arm on a tile before the next; stops when BUDGET_S of token time is spent.
     MPS only if the DINOv3 job has ended (pgrep spatialcv_gpu.py), else CPU.
Writes ida_rows.csv (per tile, arm, region) and BIG/ida/<tile>_feat.npz maps for the figures.
    nice -n 10 python3 -I run_ida.py [secondary|primary] > run_ida_<stage>.log 2>&1
"""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd

T0 = time.time()
PREP = C.IDA_BIG / "prep"
OUT = C.BIG / "ida"
BUDGET_S = 3 * 3600
MIN_THIN = 2000
RING_PX = 80


def gpu_free():
    return subprocess.run(["pgrep", "-f", "spatialcv_gpu.py"], capture_output=True).returncode != 0


_MODEL = {}


def model():
    if "m" not in _MODEL:
        import torch
        import sn8_dino as D
        if gpu_free():
            m, dev = D.backbone()
        else:
            orig = torch.backends.mps.is_available
            torch.backends.mps.is_available = lambda: False
            try:
                m, dev = D.backbone()
            finally:
                torch.backends.mps.is_available = orig
            torch.set_num_threads(3)
        _MODEL.update(m=m, dev=dev)
    return _MODEL["m"], _MODEL["dev"]


def window_slices(shape):
    from sn8_dino import PATCH, WINDOWS
    n_r, n_c = -(-shape[0] // PATCH), -(-shape[1] // PATCH)
    rows, cols = np.array_split(np.arange(n_r), WINDOWS), np.array_split(np.arange(n_c), WINDOWS)
    return n_r, n_c, [(r, c) for r in rows for c in cols]


_TOK = {}


def window_tokens(grey, valid, need):
    """sn8_dino.tokens restricted to the windows listed in `need` (indices into window_slices); others zero.
    Same fill (the valid mean of the whole image), normalisation and window split as sn8_dino.tokens."""
    import hashlib
    import torch
    from sn8_dino import MEAN, PATCH, STD
    m, dev = model()
    n_r, n_c, wins = window_slices(grey.shape)
    g = np.full((n_r * PATCH, n_c * PATCH), grey[valid].mean(), np.float32)
    g[: grey.shape[0], : grey.shape[1]] = np.where(valid, grey, grey[valid].mean())
    x = np.stack([(g / 255 - mu) / s for mu, s in zip(MEAN, STD)]).astype(np.float32)
    out = np.zeros((n_r, n_c, m.embed_dim), np.float32)
    for k in need:
        r, c = wins[k]
        win = x[:, r[0] * PATCH:(r[-1] + 1) * PATCH, c[0] * PATCH:(c[-1] + 1) * PATCH]
        h = hashlib.sha256(win.tobytes()).hexdigest()
        if h not in _TOK:
            with torch.inference_mode():
                f = m.forward_features(torch.from_numpy(win[None]).to(dev))[0, m.num_prefix_tokens:]
            _TOK[h] = f.float().cpu().numpy().reshape(len(r), len(c), -1)
        out[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = _TOK[h]
    return out


def cosdist(a, b):
    num = (a * b).sum(-1)
    den = np.linalg.norm(a, axis=-1) * np.linalg.norm(b, axis=-1)
    return 1 - num / np.maximum(den, 1e-12)


def patch_to_px(d, shape):
    from sn8_dino import PATCH
    return np.repeat(np.repeat(d, PATCH, 0), PATCH, 1)[: shape[0], : shape[1]]


def edge_r(a, b, m):
    from sn8_coreg import _gradient
    if m.sum() < 50:
        return np.nan
    ga, gb = _gradient(a, m), _gradient(b, m)
    x, y = ga[m], gb[m]
    if x.std() < 1e-6 or y.std() < 1e-6:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def usable_tiles():
    rows = []
    for f in sorted(PREP.glob("*.npz")):
        z = np.load(f, allow_pickle=True)
        r = z["row"].item()
        if r.get("coreg_ok") and "score" in z.files:
            rows.append(r["tile_id"])
    return rows


def tile_regions(tile_id, outs):
    from scipy import ndimage as ndi
    z = np.load(PREP / f"{tile_id}.npz", allow_pickle=True)
    s, guard, noaa = z["score"], z["guard"], z["noaa"]
    c0 = outs["C0"]
    gate = c0["gate"]
    thin = s & gate & ~c0["opaque"]
    d = ndi.distance_transform_edt(~gate) if gate.any() else np.full(gate.shape, np.inf)
    ring = s & ~gate & (d > 0) & (d <= RING_PX) & ~z["bright"]
    return z, s, guard, noaa, thin, ring


def main():
    from run_corr import arm_images
    stage = sys.argv[1] if len(sys.argv) > 1 else "secondary"
    h0 = C.registry_hash()
    OUT.mkdir(parents=True, exist_ok=True)
    tiles = usable_tiles()
    C.dev_guard_tiles(tiles)
    C.log(T0, f"{len(tiles)} usable prepped tiles; MPS free: {gpu_free()}")
    sec_f = C.HERE / "ida_rows_secondary.csv"
    pri_f = C.HERE / "ida_rows_primary.csv"
    sec = pd.read_csv(sec_f) if sec_f.exists() else pd.DataFrame(columns=["tile_id"])
    pri = pd.read_csv(pri_f) if pri_f.exists() else pd.DataFrame(columns=["tile_id"])
    spent = float(pri.attrs.get("spent", 0)) if len(pri) else 0.0
    thin_px = {}
    if stage == "secondary":
        new = []
        for t in tiles:
            if t in set(sec.tile_id):
                continue
            from sn8_clouds import _tile
            from sn8_refhaze import dark_reference_dehaze
            _, b0, a0, v0 = _tile(t)
            z, s, guard, noaa, thin, ring = tile_regions(t, {"C0": dark_reference_dehaze(b0, a0, v0)})
            if thin.sum() < MIN_THIN:
                new.append({"tile_id": t, "arm": "-", "region": "thin", "px": int(thin.sum())})
                C.log(T0, f"{t}: thin {int(thin.sum())} px, skipped")
                continue
            outs, (p, before, after, valid) = arm_images(t)
            asis = z["asis"]
            for arm, o in [("as is", {"corrected": np.where(valid, after, 0)})] + list(outs.items()):
                img = o["corrected"]
                for rn, m in (("thin", thin), ("ring", ring)):
                    new.append({"tile_id": t, "arm": arm, "region": rn, "px": int(m.sum()),
                                "grey_err": float(np.abs(img - noaa)[m].mean()) if m.sum() >= 50 else np.nan,
                                "edge_r": edge_r(img, noaa, m)})
                new.append({"tile_id": t, "arm": arm, "region": "guard", "px": int(guard.sum()),
                            "grey_change": float(np.abs(img - asis)[guard].mean())})
            C.log(T0, f"{t}: thin {int(thin.sum())} px, ring {int(ring.sum())} px")
            sec = pd.concat([sec, pd.DataFrame(new)], ignore_index=True); new = []
            sec.to_csv(sec_f, index=False)
        sec = pd.concat([sec, pd.DataFrame(new)], ignore_index=True)
        sec.to_csv(sec_f, index=False)
    else:
        sec = pd.read_csv(sec_f)
        th = sec[(sec.region == "thin") & (sec.arm != "-")].groupby("tile_id").px.first().sort_values(ascending=False)
        budget_log = C.HERE / "ida_primary_spent.txt"
        spent = float(budget_log.read_text()) if budget_log.exists() else 0.0
        for t in th.index:
            if t in set(pri.tile_id):
                continue
            if spent >= BUDGET_S and not gpu_free():
                C.log(T0, f"budget spent ({spent:.0f} s); stopping before {t}")
                break
            t1 = time.time()
            outs, (p, before, after, valid) = arm_images(t)
            z, s, guard, noaa, thin, ring = tile_regions(t, outs)
            from sn8_dino import PATCH
            n_r, n_c, wins = window_slices(s.shape)
            need = []
            for k, (r, c) in enumerate(wins):
                sl = (slice(r[0] * PATCH, (r[-1] + 1) * PATCH), slice(c[0] * PATCH, (c[-1] + 1) * PATCH))
                if (thin[sl].sum() + ring[sl].sum()) > 0:
                    need.append(k)
            tok_noaa = window_tokens(noaa, s, need)
            rows = []
            maps = {}
            for arm, o in [("as is", {"corrected": np.where(valid, after, 0)})] + list(outs.items()):
                tok = window_tokens(o["corrected"].astype(np.float32), s, need)
                dist = patch_to_px(cosdist(tok, tok_noaa), s.shape)
                if arm in ("as is", "C0", "C1 He 2013", "C2 IR-MAD tone", "C3a fitted fade"):
                    maps[arm] = dist.astype(np.float16)
                for rn, m in (("thin", thin), ("ring", ring)):
                    rows.append({"tile_id": t, "arm": arm, "region": rn, "px": int(m.sum()),
                                 "feat": float(dist[m].mean()) if m.sum() >= 50 else np.nan})
            np.savez_compressed(OUT / f"{t}_feat.npz", **{k.replace(" ", "_"): v for k, v in maps.items()})
            spent += time.time() - t1
            budget_log.write_text(str(spent))
            pri = pd.concat([pri, pd.DataFrame(rows)], ignore_index=True)
            pri.to_csv(pri_f, index=False)
            _TOK.clear()
            C.log(T0, f"{t}: {len(need)} windows, {time.time() - t1:.0f} s (spent {spent:.0f} s)")
    assert C.registry_hash() == h0
    C.log(T0, "done")


if __name__ == "__main__":
    main()
