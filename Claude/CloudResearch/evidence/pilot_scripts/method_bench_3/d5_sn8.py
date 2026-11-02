"""D5's conditional flood test (preregistration: run only if D5 passes its HRC rule; D5a did: pooled F1 not worse, boundary
band +0.0042 [+0.003, +0.006], hrc_d5_numbers.json). The D0 spotter and the D5a spotter (sample weights
w = 1 + exp(-d / 8)) are refitted on all 120 HRC_WHU development images (sn8_cloudspot.CloudSpotter's recipe), applied
to the 200 SN8 development tiles (CPU DINOv2 tokens, computed once per tile and shared), and each gives a spotter road
gate (tile rule & spot share < 0.2, sn8_cloudspot.spot_gate). D0's shares must reproduce cloud_spotting/gate_roads.csv
(spot_road) or the run stops. Flood calls: production's columns on each gate, 21 seeds, D5a paired against D0.
    OMP_NUM_THREADS=2 nice -n 10 python3 -I d5_sn8.py > d5_sn8.log 2>&1
"""
import json
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b3_common as K
import run_bench3 as RB

import numpy as np
import pandas as pd

T0 = time.time()
RB.T0 = T0
OUT = K.BIG / "d5_spot"


class WeightedSpotter:
    def __init__(self, columns, weighted):
        import sn8_cloudspot as S
        self.S, self.columns, self.weighted = S, list(columns), weighted

    def fit(self):
        S = self.S
        import hrc_d5
        names = S.hrc_images("train")
        self.basis_ = S.fit_basis(S.hrc_dinov2_tokens, names)
        cues = S._hrc_cues(names)
        cols = S.CUES + S.TOOLS["dinov2"]
        k = [cols.index(c) for c in self.columns]
        x = np.concatenate([S._features(n, i, "train", cues, {"v2": S.DINOV2}, {"v2": self.basis_}, ["v2"])
                            for i, n in enumerate(names)])
        y = np.concatenate([cues[f"{n}|train|y"] for n in names])
        m = S.forest()
        m.set_params(n_jobs=2)
        if self.weighted:
            em = hrc_d5.edge_maps(names)
            w = np.concatenate([1 + hrc_d5.ALPHA * np.exp(-em[f"{n}|train|d"] / hrc_d5.SIGMA) for n in names])
            m.fit(x[:, k], y, sample_weight=w)
        else:
            m.fit(x[:, k], y)
        self.model_ = m
        return self

    def proba_from(self, cue_maps, tok, valid, where):
        S = self.S
        r, c = np.nonzero(where & valid)
        x = np.concatenate([np.stack([cue_maps[n][r, c] for n in S.CUES], 1),
                            S.pcs_at(tok, self.basis_, r, c, S.PATCH)], 1)
        cols = S.CUES + S.TOOLS["dinov2"]
        x = x[:, [cols.index(n) for n in self.columns]]
        p = np.concatenate([self.model_.predict_proba(x[s:s + 200_000])[:, 1] for s in range(0, len(x), 200_000)])
        out = np.where(valid, np.nan, 0.0)
        out[r, c] = p
        return out


def main():
    import torch
    import torch._dynamo  # noqa: F401  (deviation 2: import before the patch; torch._dynamo reads __wrapped__)
    torch.backends.mps.is_available = lambda: False
    torch.set_num_threads(2)
    import sn8_cloudspot as S
    from sn8_clouds import _maps, _tile
    from sn8_dino import tokens
    from sn8_lines import road_band
    h0 = K.registry_hash()
    choice = json.loads((K.M1.PILOT / "cloud_spotting" / "choice.json").read_text())
    sp = {"D0": WeightedSpotter(choice["columns"], False).fit(), "D5a": WeightedSpotter(choice["columns"], True).fit()}
    K.log(T0, "spotters fitted on 120 HRC_WHU development images")
    order, roads = RB.dev_tiles()
    OUT.mkdir(parents=True, exist_ok=True)
    for i, tid in enumerate(order):
        f = OUT / f"{tid}.pkl"
        if f.exists():
            continue
        K.wait_for_memory(T0)
        K.dev_guard_tiles([tid])
        p, _, after, valid = _tile(tid)
        strip, rds, n, cpx = S._strip(tid, p, valid, road_band())
        rows = []
        if n:
            grid = np.zeros(valid.shape, bool)
            gr, gc = S.grid_pixels(valid.shape)
            grid[gr, gc] = True
            need = grid | (strip > 0)
            cue_maps = S.classical_cues(after, valid)
            tok = tokens(after, valid)
            masks = {k: np.nan_to_num(s.proba_from(cue_maps, tok, valid, need), nan=0.0) >= S.CUT for k, s in sp.items()}
            masks["rise"] = _maps(p, valid)["masks"]["dark rise"]
            rows = S.road_shares(tid, strip, rds, n, cpx, masks)
        K.atomic_bytes(f, pickle.dumps(rows))
        K.log(T0, f"{i + 1}/{len(order)} {tid}")
    spot = pd.read_csv(K.M1.PILOT / "cloud_spotting" / "gate_roads.csv")
    sh = pd.concat([pd.DataFrame(pickle.loads((OUT / f"{t}.pkl").read_bytes())) for t in order], ignore_index=True)
    D = RB.Data()
    al = RB.R2()._align(D.roads, sh)
    hit = al.D0.notna().to_numpy() & D.tile_rule
    gap = np.abs(al.D0.to_numpy()[hit] - spot.spot_road.to_numpy()[hit])
    num = {"D0_reproduction_max_gap": float(gap.max()), "D0_reproduction_share_exact": float((gap < 1e-9).mean())}
    K.log(T0, f"D0 spot_road reproduction: max gap {gap.max():.4g}, exact {100 * (gap < 1e-9).mean():.1f}%")
    from sn8_clouds import ROAD_CLOUD_CUT
    D.arms["D0 spotter gate"] = {"gate": D.tile_rule & (np.nan_to_num(al.D0.to_numpy()) < ROAD_CLOUD_CUT), "cols": list(D.cols)}
    D.arms["D5a spotter gate"] = {"gate": D.tile_rule & (np.nan_to_num(al.D5a.to_numpy()) < ROAD_CLOUD_CUT), "cols": list(D.cols)}
    done = RB.load_calls()
    prod = RB.reproduce(D, done)
    RB.fit_arms(D, ["D0 spotter gate", "D5a spotter gate"], K.M1.SEEDS, done)
    num["vs_production"] = RB.summarise(D, done, prod, ["D0 spotter gate", "D5a spotter gate"], label="spot ")
    d0 = np.stack([done[f"D0 spotter gate__{s}"] for s in K.M1.SEEDS])
    d5 = np.stack([done[f"D5a spotter gate__{s}"] for s in K.M1.SEEDS])
    shared = D.arms["D0 spotter gate"]["gate"] & D.arms["D5a spotter gate"]["gate"]
    num["D5a_vs_D0"] = K.M1.seed_avg(d5, d0, D.y, shared, D.block)
    num["D5a_vs_D0"]["kept_D0"] = int(D.arms["D0 spotter gate"]["gate"].sum())
    num["D5a_vs_D0"]["kept_D5a"] = int(D.arms["D5a spotter gate"]["gate"].sum())
    K.write_json(K.HERE / "d5_sn8_numbers.json", num)
    r = num["D5a_vs_D0"]
    K.log(T0, f"D5a vs D0 spotter gate: {100 * r['mean_gain']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}]")
    assert K.registry_hash() == h0
    K.log(T0, "done")


if __name__ == "__main__":
    main()
