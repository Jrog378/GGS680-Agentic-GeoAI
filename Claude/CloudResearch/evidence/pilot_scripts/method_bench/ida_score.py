"""Scoring (b) statistics: per tile, arm minus C0 (feature distance to NOAA: primary; grey error, edge r: secondary), in
thin and in the ring; 95% intervals from 2,000 resamples of the 3 x 3 tile blocks (spatial_folds.fold_table(662));
Wilcoxon signed-rank as a check; guard grey change. Writes ida_numbers.json.
    python3 -I ida_score.py > ida_score.log 2>&1
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mb_common as C

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


def paired_tiles(df, metric, region, arm, base="C0"):
    a = df[(df.arm == arm) & (df.region == region)].set_index("tile_id")[metric]
    b = df[(df.arm == base) & (df.region == region)].set_index("tile_id")[metric]
    j = a.index.intersection(b.index)
    d = (a.loc[j] - b.loc[j]).dropna()
    if len(d) < 3:
        return None
    from spatial_folds import fold_table
    ft = fold_table(662)
    blk = d.index.map(dict(zip(ft.tile_id, ft.block))).to_numpy()
    bt = C.Boot(blk, np.ones(len(d), bool))
    dist = bt.mean(d.to_numpy())
    try:
        wp = float(wilcoxon(d.to_numpy()).pvalue) if (d != 0).any() else 1.0
    except ValueError:
        wp = 1.0
    return {"tiles": int(len(d)), "mean_diff": float(d.mean()), "ci": [float(np.percentile(dist, 2.5)),
            float(np.percentile(dist, 97.5))], "tiles_lower": int((d < 0).sum()), "tiles_higher": int((d > 0).sum()),
            "wilcoxon_p": wp, "mean_arm": float(a.loc[j].mean()), "mean_base": float(b.loc[j].mean())}


def main():
    num = {}
    sec = pd.read_csv(C.HERE / "ida_rows_secondary.csv")
    sec = sec[sec.arm != "-"]
    arms = [a for a in sec.arm.unique() if a not in ("C0",)]
    num["secondary_tiles"] = int(sec.tile_id.nunique())
    for metric in ("grey_err", "edge_r"):
        for region in ("thin", "ring"):
            num[f"{metric}_{region}_vs_C0"] = {a: paired_tiles(sec, metric, region, a) for a in arms}
    g = sec[sec.region == "guard"].groupby("arm").grey_change.mean()
    num["guard_grey_change_mean"] = g.to_dict()
    pf = C.HERE / "ida_rows_primary.csv"
    if pf.exists():
        pri = pd.read_csv(pf)
        num["primary_tiles"] = sorted(pri.tile_id.unique().tolist())
        num["primary_vs_C0"] = {}
        for a in [x for x in pri.arm.unique() if x != "C0"]:
            r = paired_tiles(pri, "feat", "thin", a)
            if r:
                r["guard_ok"] = bool(abs(num["guard_grey_change_mean"].get(a, 0)) <= 1.0)
            num["primary_vs_C0"][a] = r
        num["primary_ring_vs_C0"] = {a: paired_tiles(pri, "feat", "ring", a) for a in pri.arm.unique() if a != "C0"}
        num["primary_C0_vs_asis"] = paired_tiles(pri, "feat", "thin", "C0", base="as is")
    C.write_json(C.HERE / "ida_numbers.json", num)
    for k, v in num.items():
        if isinstance(v, dict) and k.endswith("vs_C0"):
            print(f"\n{k}")
            for a, r in v.items():
                if r:
                    print(f"  {a:24s} n={r['tiles']:3d} diff {r['mean_diff']:+.4f} [{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}] "
                          f"lower {r['tiles_lower']} higher {r['tiles_higher']} W p={r['wilcoxon_p']:.3g}")
    print("\nguard grey change:", {k: round(v, 3) for k, v in num["guard_grey_change_mean"].items()})


if __name__ == "__main__":
    main()
