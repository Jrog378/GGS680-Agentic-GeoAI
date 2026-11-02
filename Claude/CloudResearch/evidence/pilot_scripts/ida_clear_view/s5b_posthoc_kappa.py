"""POST-HOC (not pre-registered; added 2026-10-30 after reading s5): the call-level agreement rises with each arm's share
of 'flooded' calls while the detector calls 87-91% of cloudy roads flooded on the NOAA image, so raw agreement partly
measures the flooded-call rate. Chance-corrected agreement (Cohen's kappa) per arm and group, with the same 3 x 3 block
bootstrap (2,000 resamples, seed 662) as s5. Writes s5b_kappa.json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ida_common as C
import numpy as np, pandas as pd
import s5_stats as S
from sklearn.metrics import cohen_kappa_score

S.BLOCK = S.blocks()
W = pd.read_csv(C.HERE / "s4_road_calls.csv")
out = {}
for grp, m in (("cloudy", W.cloudy), ("thin", W.thin_cloud), ("clear (ceiling)", ~W.cloudy)):
    x = W[m]
    for a in ("asis", "he", "td", "tdspot"):
        xx = x.dropna(subset=[f"call_{a}", "call_noaa"])
        p, q = xx[f"call_{a}"].to_numpy(int), xx.call_noaa.to_numpy(int)
        k0 = cohen_kappa_score(p, q) if len(set(p) | set(q)) > 1 else np.nan
        tt = xx.tile_id.to_numpy(); tiles = np.unique(tt); idx = {t: np.flatnonzero(tt == t) for t in tiles}
        bs = []
        for ii in S.boot_idx(list(tiles), np.random.default_rng(C.SEED)):
            sel = np.concatenate([idx[tiles[i]] for i in ii])
            bs.append(cohen_kappa_score(p[sel], q[sel]) if len(set(p[sel]) | set(q[sel])) > 1 else np.nan)
        out[f"{grp}|{a}"] = {"roads": int(len(xx)), "kappa": float(k0), "lo": float(np.nanpercentile(bs, 2.5)),
                             "hi": float(np.nanpercentile(bs, 97.5))}
        print(f"{grp:16s} {a:7s} kappa {k0:+.3f} [{out[f'{grp}|{a}']['lo']:+.3f}, {out[f'{grp}|{a}']['hi']:+.3f}] n {len(xx)}")
(C.HERE / "s5b_kappa.json").write_text(json.dumps(out, indent=1))
