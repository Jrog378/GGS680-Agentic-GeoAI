"""Phase A extra checks: (i) share of kept roads above the null's 90th/95th percentiles; (ii) tile-wide haze that the
tone curve absorbs: the tile's raw (untoned) dark-channel rise against the held-out errors, label as covariate.
    nice -n 10 /opt/miniconda3/bin/python -I extra_checks.py > extra_checks.log 2>&1"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import analyze_A as A
from sklearn.linear_model import LogisticRegression

r, calls = A.load()
k = r[r.kept].reset_index(drop=True)
out = {}
for name, (a, b) in A.PRIMARY.items():
    nullv = -k[a].to_numpy() if b is None else k[b].to_numpy()
    out[name] = {f"share above null p{q}": float((k[a] > np.nanpercentile(nullv, q)).mean()) for q in (90, 95, 99)}
    out[name]["median after / null"] = [float(np.nanmedian(k[a])), float(np.nanmedian(nullv))]
t = pd.read_csv(A.HERE / "haze_tiles.csv")
k["tile_raw_rise"] = k.tile_id.map(dict(zip(t.tile_id, t.raw_rise_med)))
err = 1 - k.right_share.to_numpy(); yk = k.flooded.astype(int).to_numpy()
h = k.tile_raw_rise.to_numpy(); zh = (h - h.mean()) / h.std()
def fit(idx):
    X = np.column_stack([zh[idx], yk[idx]]); n = len(idx)
    m = LogisticRegression(C=1e6, max_iter=1000).fit(np.vstack([X, X]), np.r_[np.ones(n), np.zeros(n)],
                                                       sample_weight=np.r_[err[idx], 1 - err[idx]] * 21)
    return m.coef_[0][0]
c = fit(np.arange(len(k)))
bs = [fit(b) for b in A.block_boot(k.block.to_numpy(), seed=663)]
out["tile raw rise vs error (log-odds per SD, label covariate)"] = {"coef": float(c), "95% CI": A.ci(bs)}
u = k[~k.flooded.astype(bool)]
ch = [c for c in k.columns if c.endswith("_change")]
rho = u[ch].corrwith(u.tile_raw_rise, method="spearman")
out["tile raw rise vs change features on unchanged roads (spearman), median |rho|"] = float(rho.abs().median())
out["tile raw rise: kept-road tiles, median / p90"] = [float(np.median(h)), float(np.percentile(h, 90))]
print(json.dumps(out, indent=1)); (A.HERE / "phaseA_extra.json").write_text(json.dumps(out, indent=1))
