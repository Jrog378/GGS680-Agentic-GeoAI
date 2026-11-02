"""Revision 1 item 1 (call-level outcome, adapted from M3R-CR, Xu et al. 2024 -- not their protocol: they score each
input against land-cover labels; here each arm's per-road flood calls are compared with the calls the same frozen
detector makes on the tone-matched NOAA image), outcome 6 (DINOv2 change cue per road strip) and item 8 (label gap).

Detector: production's flood model (sn8_stages.production_model(), "random forest (tuned)") on the 96 production columns,
fitted exactly as factorial arm c00 under spatial folds S at seed 662 (evidence 14): each fold trains on its training
roads that the production gate keeps (cached production features, satellite as is), and calls its held-out roads. The
fitted fold models are then frozen and call each held-out road again from features measured on each arm's after image
and on the NOAA image (before image unchanged). Reproduction check first: the cached-feature calls must equal the saved
c00__S__662 calls, road for road.
Features per road per image: sn8_refhaze.corrected_rows' recipe (line_features, lines_glcm, lines_texture, lines_dino),
with the after image replaced and the valid mask = the tile's score mask (satellite valid & NOAA valid & not NOAA
cloud/glare) for every image, so all arms and NOAA see the same pixels.
    nice -n 10 python3 -I s4_calls.py > s4_calls.log 2>&1
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C

import numpy as np
import pandas as pd

IMAGES = ["asis", "he", "td", "tdspot", "noaa"]
OUT = C.BIG / "roads"


def road_rows(tile_id):
    f = OUT / f"{tile_id}.csv"
    if f.exists():
        return pd.read_csv(f)
    from sn8 import tile
    from sn8_dino import DINO_CUES, lines_dino
    from sn8_glcm import GLCM_FEATURES, lines_glcm
    from sn8_lines import road_band
    from sn8_roads import FEATURES, _road_lines, line_features
    from sn8_texture import TEXTURE_FEATURES, lines_texture
    C.patch_tokens()
    C.cpu_backbone()
    z = np.load(C.BIG / "prep" / f"{tile_id}.npz", allow_pickle=True)
    p, before, after, valid = C.sat_tile(tile_id)
    s = z["score"]
    band = road_band()
    seg, seg_angle, seg_road, roads = _road_lines(tile(tile_id)["label"], (p["x0"], p["y0"]), s.shape)
    out = []
    for im in IMAGES:
        if im == "tdspot" and not bool(z["spotter_run"]):
            continue
        q = {**p, "before_grey": z["before"], "after_grey": z[im]}
        lines = line_features(tile_id, q, s, seg, seg_angle, seg_road, roads, band)
        glcm = lines_glcm(tile_id, q, s, seg, seg_road, roads, band)
        tex = lines_texture(tile_id, q, s, seg, seg_road, roads, band)
        dino = lines_dino(tile_id, q, s, seg, seg_road, roads, band)[0]
        for a, b, c, d in zip(lines, glcm, tex, dino):
            assert a["road_id"] == b["road_id"] == c["road_id"] == d["road_id"]
            out.append({"image": im, "tile_id": tile_id, "road_id": a["road_id"], **{k: a[k] for k in FEATURES},
                        **{k: b[k] for k in GLCM_FEATURES}, **{k: c[k] for k in TEXTURE_FEATURES},
                        **{k: d[k] for k in DINO_CUES}})
    df = pd.DataFrame(out, columns=None if out else ["image", "tile_id", "road_id"])   # fix 2026-10-30: tile without roads
    df["_n"] = df.groupby(["image", "tile_id", "road_id"]).cumcount()
    df.to_csv(f, index=False)
    return df


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    from scv_common import Setup, builders, load_npz, FLOOD_CALLS
    from sn8_models import FLOOD_MODELS
    S = Setup(build_x=False)
    roads, cols, y = S.roads, S.cols, S.y
    folds = builders()["S"](S.R, C.SEED)
    gate = S.gates["a"]
    make = FLOOD_MODELS[S.model_name]
    models, call0 = [], np.full(len(y), -1)
    fold_of = np.full(len(y), -1)
    for k, (tr, te, *_) in enumerate(folds):
        fit = tr[gate[tr]]
        m = make()
        m.set_params(**{p: 1 for p in m.get_params(deep=True) if p.endswith("n_jobs")})
        m.fit(roads.iloc[fit][cols], y[fit])
        models.append(m)
        call0[te] = m.predict(roads.iloc[te][cols])
        fold_of[te] = k
    saved, _ = load_npz(FLOOD_CALLS)
    ref = saved["c00__S__662"]
    agree = int((ref == call0).sum())
    print(f"reproduction of c00 S 662: {agree} / {len(y)} calls equal", flush=True)
    assert agree == len(y), "fold models differ from the saved spatial-CV calls"
    prep = pd.read_csv(C.HERE / "s2_prep.csv")
    scored = set((C.HERE / "scored_tiles.txt").read_text().split())
    use = [t for t in prep.tile_id[prep.coreg_ok.fillna(False).astype(bool)] if t in scored]
    cl = set(C.cloudy_tiles())
    use.sort(key=lambda t: (t not in cl, t))
    feats = []
    for i, t in enumerate(use):
        feats.append(road_rows(t))
        print(f"roads {i + 1}/{len(use)} {t} {round(time.time() - t0)} s", flush=True)
    F = pd.concat(feats, ignore_index=True)
    # line up with the 1,037 dev roads by (tile, road id, occurrence); ambiguous duplicates dropped
    base = roads[["tile_id", "road_id"]].copy()
    base["_n"] = base.groupby(["tile_id", "road_id"]).cumcount()
    base["pos"] = np.arange(len(base))
    dup = base.duplicated(["tile_id", "road_id"], keep=False)
    rows = []
    for im in IMAGES:
        fi = F[F.image == im]
        m = base[~dup].merge(fi, on=["tile_id", "road_id", "_n"], how="inner")
        pos = m.pos.to_numpy()
        calls = np.empty(len(pos), int)
        for k in range(len(models)):
            sel = fold_of[pos] == k
            if sel.any():
                calls[sel] = models[k].predict(m.loc[sel, cols])
        rows.append(pd.DataFrame({"pos": pos, "image": im, "call": calls,
                                  "dino_change_pooled": m.dino_change_pooled.to_numpy(),
                                  "dino_change_mean": m.dino_change_mean.to_numpy()}))
    L = pd.concat(rows, ignore_index=True)
    W = L.pivot_table(index="pos", columns="image", values=["call", "dino_change_pooled", "dino_change_mean"])
    W.columns = [f"{a}_{b}" for a, b in W.columns]
    W = W.reset_index()
    W["tile_id"] = roads.tile_id.to_numpy()[W.pos]
    W["road_id"] = roads.road_id.to_numpy()[W.pos]
    W["flooded_label"] = y[W.pos]
    W["kept_gate"] = gate[W.pos]
    W["thin_cloud"] = S.hazy[W.pos]
    W["cloudy"] = ~W.kept_gate
    W["call_cached_asis"] = call0[W.pos]
    W["block"] = S.block[W.pos]
    W.to_csv(C.HERE / "s4_road_calls.csv", index=False)
    print(f"{len(W)} roads with calls on {W.tile_id.nunique()} tiles; cloudy {int(W.cloudy.sum())}; "
          f"{round(time.time() - t0)} s", flush=True)


if __name__ == "__main__":
    main()
