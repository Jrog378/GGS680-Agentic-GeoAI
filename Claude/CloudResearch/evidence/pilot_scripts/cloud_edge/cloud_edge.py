"""The cloud-edge ring (evidence 09; exploratory, development data only, real cloud, label-free). Stages, in order:

    python3 -I cloud_edge.py tiles      # gate tiles, the two halves, picture tiles and crop windows (geometry only)
    python3 -I cloud_edge.py arms       # every tile x (as it is + ARMS a-d): measures -> arms_tiles.csv
    python3 -I cloud_edge.py arms_e     # arm e (He 2013 recipe, added after evidence 10) -> arms_e_tiles.csv
    python3 -I cloud_edge.py select     # choose half only: one setting per arm, the combination -> chosen.json
    python3 -I cloud_edge.py combo      # the combination on every tile -> combo_tiles.csv
    python3 -I cloud_edge.py report     # tables, both halves, paired tests -> report.log, numbers.json
    python3 -I cloud_edge.py figures    # crops and the band profile -> CloudResearch/figures/ring/

Plan, fixed before any arm was run (the arms and guards are in sn8_cloudedge, committed first):
- tiles: sn8_cloudedge.gate_tiles() (tile-rule tiles of train + val with a non-empty gate), halves by
  split_halves (SHA-256 order of the id, alternate). Choose a setting on "choose", report on "report".
- selection per arm (a, b, c, d, e): the lowest median ring score on the choose half among the settings that pass every
  guard (sn8_cloudedge GUARD_*). If none passes, the arm is reported as failing, with its lowest-score setting.
- combination: the chosen spread of (a)/(b) with the lower ring score, with the chosen source of (c)/(d)/(e) with the
  lowest grey ring score (c, d and e act at the inner edge, which the 41 px residual cannot resolve), built only if
  that source beats the current fit on the grey ring score on the choose half and passes the guards.
- arm (e), He, Sun & Tang 2013's own recipe (opening of the dark channel, then the guided filter guided by the hazy
  after image), was added at the coordinator's request after the literature check (evidence 10), while the a-d run was
  in progress and before any arm's outcome had been looked at. Its grid: r 20 (He's) and 50 (scaled to our tiles),
  eps 1e-3 (He's) and 1e-2.
- the best variant: the lowest median ring score on the choose half among the chosen settings and the combination that
  pass every guard. Reported on the report half against the current fit: tiles better / worse, sign test, median and
  mean difference with a 95% interval from resampling tiles; the same for the grey ring score.
- cause checks (descriptive, every gate tile): residual haze of the after image as it is by band (does the fringe
  reach past the 40 px margin?), the share of it the current fit removes by band against the fade's own 1 - d / 40,
  and inside-edge against deep-inside residual.
- pictures: 2_23_44 (the deck's example) and the two report-half tiles with the longest gate edge; crop by
  sn8_cloudedge.edge_crop (geometry only).
No flood label is read. No test, negative or sealed tile is opened.
"""
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
import pandas as pd

from sn8_clouds import _tile
from sn8_cloudedge import (ARMS, GUARD_CLEAR_CHANGED, GUARD_COPY, GUARD_DETAIL, GUARD_SEAM, RING_BANDS, BANDS_PX,
                           as_it_is, edge_crop, edge_dehaze, edge_parts, gate_edge_px, gate_tiles, ring_measures,
                           split_halves)
from sn8_data import split_tables

OUT = Path(__file__).resolve().parent
FIG = Path("/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/figures/ring")
EXAMPLE = "2_23_44"
WORKERS = 3
SEED = 662


def dev_ids():
    """The train + val tile ids by name (split_tables), to check every tile used is development data."""
    _, train, val, _, _ = split_tables()
    return set(train.tile_id) | set(val.tile_id)


def stage_tiles():
    t0 = time.time()
    tiles = gate_tiles()
    assert set(tiles) <= dev_ids()
    halves = split_halves(tiles)
    rows = []
    for tid in tiles:
        _, before, after, valid = _tile(tid)
        parts = edge_parts(before, after, valid)
        rows.append({"tile_id": tid, "half": halves[tid], "fit": parts is not None,
                     "gate share": float(parts["gate"][valid].mean()) if parts else np.nan,
                     "gate edge px": gate_edge_px(parts["gate"], valid) if parts else 0,
                     "crop": edge_crop(parts, valid) if parts else None})
    d = pd.DataFrame(rows)
    rep = d[(d.half == "report") & d.fit & (d.tile_id != EXAMPLE)].sort_values(["gate edge px", "tile_id"],
                                                                                ascending=[False, True])
    pics = [EXAMPLE] + rep.tile_id.head(2).tolist()
    d["picture"] = d.tile_id.isin(pics)
    d.to_csv(OUT / "tiles.csv", index=False)
    print(f"{len(d)} gate tiles ({d.fit.sum()} with a fit), choose {int((d.half == 'choose').sum())}, "
          f"report {int((d.half == 'report').sum())}; {EXAMPLE} in the {d.set_index('tile_id').half.get(EXAMPLE)} "
          f"half; pictures {pics}; {time.time() - t0:.0f} s")


def run_tile(args):
    """Every arm on one tile. Checks that the "current" arm reproduces dark_reference_dehaze exactly."""
    tid, arms = args
    _, before, after, valid = _tile(tid)
    parts = edge_parts(before, after, valid)
    base = parts["base"]
    rows = []
    for name, (source, spread) in arms.items():
        out = as_it_is(after, valid) if name == "as it is" else edge_dehaze(parts, before, after, valid, source, spread)
        if name == "current":
            diff = float(np.abs(out["corrected"] - base["corrected"])[valid].max())
            assert diff < 1e-3 and np.array_equal(out["opaque"], base["opaque"]), (tid, diff)
        rows.append({"tile_id": tid, "arm": name, **ring_measures(parts, before, after, valid, out, base["opaque"]),
                     "soft added share": float((out["region"] & ~parts["gate"])[valid].mean())})
    return rows


def run(arms, path):
    d = pd.read_csv(OUT / "tiles.csv")
    tiles = d.tile_id[d.fit].tolist()
    assert set(tiles) <= dev_ids()
    t0 = time.time()
    with Pool(WORKERS) as pool:
        rows = [r for part in pool.imap(run_tile, [(t, arms) for t in tiles]) for r in part]
    out = pd.DataFrame(rows).merge(d[["tile_id", "half"]], on="tile_id")
    out.to_csv(path, index=False)
    print(f"{len(tiles)} tiles x {len(arms)} arms in {time.time() - t0:.0f} s -> {path.name}")


def summary(d, half):
    """Per arm on one half: medians over tiles of the scores, and the guards against the current fit."""
    h = d[d.half == half] if half != "all" else d
    cur = h[h.arm == "current"].set_index("tile_id")
    rows = []
    for arm, g in h.groupby("arm", sort=False):
        g = g.set_index("tile_id")
        rows.append({"arm": arm, "tiles": len(g), "ring score": g["ring score"].median(),
                     "grey ring score": g["grey ring score"].median(), "hazy excess": g["hazy excess"].median(),
                     "clear ground changed (mean)": g["clear ground changed"].mean(),
                     "clear ground changed (max)": g["clear ground changed"].max(),
                     "tiles over 1%": int((g["clear ground changed"] > 0.01).sum()),
                     "far ground changed (mean)": g["far ground changed"].mean(),
                     "area changed beyond margin (mean)": g["area changed beyond margin"].mean(),
                     "detail kept vs current": (g["detail inside gate"] / cur["detail inside gate"]).median(),
                     "seam vs current": (g["seam index"] / cur["seam index"]).median(),
                     "seam index": g["seam index"].median(), "texture copied": g["texture copied"].median(),
                     "opaque share of gate": g["opaque share of gate"].median()})
    s = pd.DataFrame(rows).set_index("arm")
    s["passes guards"] = ((s["clear ground changed (mean)"] <= GUARD_CLEAR_CHANGED)
                          & (s["detail kept vs current"] >= GUARD_DETAIL) & (s["seam vs current"] <= GUARD_SEAM)
                          & (s["texture copied"] <= GUARD_COPY))
    return s


def arm_rows():
    """arms a-d and, when run, arm e (its own file: it was added later), one table."""
    d = pd.read_csv(OUT / "arms_tiles.csv")
    if (OUT / "arms_e_tiles.csv").exists():
        d = pd.concat([d, pd.read_csv(OUT / "arms_e_tiles.csv")], ignore_index=True)
    return d


def stage_select():
    d = arm_rows()
    s = summary(d, "choose")
    pd.set_option("display.width", 250)
    print("CHOOSE HALF\n", s.round(4).to_string())
    chosen = {}
    for letter in "abcde":
        g = s[s.index.str.startswith(letter + ":")]
        ok = g[g["passes guards"]]
        pick = (ok if len(ok) else g)["ring score"].idxmin()
        chosen[letter] = {"setting": pick, "passes guards": bool(len(ok) > 0)}
    spread = min((chosen[k] for k in "ab" if chosen[k]["passes guards"]), key=lambda c: s.loc[c["setting"], "ring score"],
                 default=None)
    source = min((chosen[k] for k in "cde" if chosen[k]["passes guards"]),
                 key=lambda c: s.loc[c["setting"], "grey ring score"], default=None)
    combo = None
    if spread and source and s.loc[source["setting"], "grey ring score"] < s.loc["current", "grey ring score"]:
        combo = {"name": f"combo: {spread['setting']} + {source['setting']}",
                 "source": list(ARMS[source["setting"]][0]), "spread": list(ARMS[spread["setting"]][1])}
    out = {"chosen": chosen, "combination": combo, "choose half": json.loads(s.to_json(orient="index"))}
    (OUT / "chosen.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"chosen": chosen, "combination": combo}, indent=1))


def stage_combo():
    c = json.loads((OUT / "chosen.json").read_text())["combination"]
    if c is None:
        print("no combination (the plan's condition does not hold)")
        return
    run({c["name"]: (tuple(c["source"]), tuple(c["spread"]))}, OUT / "combo_tiles.csv")


def all_rows():
    d = arm_rows()
    if (OUT / "combo_tiles.csv").exists():
        d = pd.concat([d, pd.read_csv(OUT / "combo_tiles.csv")], ignore_index=True)
    return d


def paired(d, arm, col, half):
    """arm against current on one half, per tile: better / worse, sign test, median and mean difference (95% CI)."""
    from scipy.stats import binomtest
    h = d[d.half == half]
    x = h[h.arm == arm].set_index("tile_id")[col]
    y = h[h.arm == "current"].set_index("tile_id")[col]
    diff = (x - y).dropna()
    better, worse = int((diff < -1e-9).sum()), int((diff > 1e-9).sum())
    rng = np.random.default_rng(SEED)
    boot = [rng.choice(diff.to_numpy(), len(diff)).mean() for _ in range(5000)]
    return {"tiles": len(diff), "better": better, "worse": worse,
            "sign p": binomtest(better, better + worse, 0.5).pvalue if better + worse else 1.0,
            "median diff": float(diff.median()), "mean diff": float(diff.mean()),
            "mean diff 95% CI": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]}


def stage_report():
    d = all_rows()
    chosen = json.loads((OUT / "chosen.json").read_text())
    pd.set_option("display.width", 250)
    names = [chosen["chosen"][k]["setting"] for k in "abcde"]
    if chosen["combination"]:
        names.append(chosen["combination"]["name"])
    choose = summary(d, "choose")
    ok = choose.loc[names][choose.loc[names, "passes guards"]]
    best = ok["ring score"].idxmin() if len(ok) else None
    print("best variant (choose half):", best)
    numbers = {"best": best, "chosen": chosen["chosen"], "combination": chosen["combination"]}
    for half in ("choose", "report"):
        s = summary(d, half)
        print(f"\n{half.upper()} HALF (medians over tiles; guards against the current fit)")
        print(s.loc[["as it is", "current"] + names].round(4).to_string())
        numbers[half] = json.loads(s.to_json(orient="index"))
    print("\nREPORT HALF, every setting (shown for the trade-off only; nothing is chosen from this table)")
    print(summary(d, "report").round(4).to_string())
    numbers["paired, report half"] = {a: {c: paired(d, a, c, "report") for c in ("ring score", "grey ring score",
                                                                                 "hazy excess")} for a in names}
    print("\nPAIRED, REPORT HALF, against the current fit")
    print(json.dumps(numbers["paired, report half"], indent=1))
    # bands, medians over tiles
    for half in ("report", "all"):
        h = d if half == "all" else d[d.half == half]
        rows = []
        for arm in ["as it is", "current"] + ([best] if best else []):
            g = h[h.arm == arm]
            for k in ("residual", "hazy share", "grey residual", "detail"):
                rows.append({"arm": arm, "measure": k, **{b: g[f"{k} | {b}"].median() for b in BANDS_PX}})
        t = pd.DataFrame(rows)
        print(f"\nBANDS, {half} (median over tiles of each tile's band median / share)")
        print(t.round(3).to_string(index=False))
        numbers[f"bands {half}"] = t.to_dict(orient="records")
    # cause checks (descriptive, every gate tile): how much of the as-it-is excess the current fit removes, by band
    raw = d[d.arm == "as it is"].set_index("tile_id")
    cur = d[d.arm == "current"].set_index("tile_id")
    cause = {}
    for k in ("residual", "grey residual"):
        rem = {}
        for b in RING_BANDS + ("out 80-120",):
            ex_raw = raw[f"{k} | {b}"] - raw[f"{k} | far"]
            ex_cur = cur[f"{k} | {b}"] - cur[f"{k} | far"]
            m = ex_raw > 2
            rem[b] = {"tiles with excess > 2": int(m.sum()), "median share removed": float((1 - ex_cur / ex_raw)[m].median()),
                      "median excess as it is": float(ex_raw.median()), "median excess current": float(ex_cur.median())}
        cause[k] = rem
    cause["inside edge vs deep, current"] = {k: {"edge 0-20": float(cur[f"{k} | inside, edge 0-20"].median()),
                                                 "deep": float(cur[f"{k} | inside, deep"].median())}
                                             for k in ("residual", "grey residual")}
    fade = {b: 1 - np.mean(BANDS_PX[b]) / 40 if BANDS_PX[b][1] <= 40 else 0.0 for b in RING_BANDS + ("out 80-120",)}
    cause["fade's own share removed (band middle)"] = fade
    print("\nCAUSE CHECKS (every gate tile)")
    print(json.dumps(cause, indent=1))
    numbers["cause"] = cause
    (OUT / "numbers.json").write_text(json.dumps(numbers, indent=1, default=float))


def stage_figures():
    """Crops of the cloud edge on the picture tiles, the whole of 2_23_44, and the band profile (report half). Shown:
    the current fit, the best variant (passes every guard), and the chosen settings of (a) and (b), which remove most
    of the ring but fail the clear-ground guard (shown so the trade-off can be seen; marked on the panels)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import ndimage as ndi
    from sn8_cloudedge import CHANGED_T, DARKREF_GATE_MARGIN_PX, HAZY_SHARE_CUT, residual_haze
    numbers = json.loads((OUT / "numbers.json").read_text())
    best, ch = numbers["best"], numbers["chosen"]
    shown = {"current fit": "current", f"best variant (passes guards):\n{best}": best,
             f"{ch['a']['setting']}\n(FAILS the clear-ground guard)": ch["a"]["setting"],
             f"{ch['b']['setting']}\n(FAILS the clear-ground guard)": ch["b"]["setting"]}
    tiles = pd.read_csv(OUT / "tiles.csv")
    note = "Imagery: Maxar via SpaceNet 8"
    size = 384
    for _, r in tiles[tiles.picture].iterrows():
        tid = r.tile_id
        _, before, after, valid = _tile(tid)
        parts = edge_parts(before, after, valid)
        cut = parts["cut"]
        outs = {k: edge_dehaze(parts, before, after, valid, *ARMS[a]) for k, a in shown.items()}
        y, x = (int(v) for v in r.crop.strip("()").split(","))
        s = (slice(y, y + size), slice(x, x + size))
        edge = parts["gate"] & ndi.binary_dilation(valid & ~parts["gate"])
        clear = valid & (parts["sd"] > DARKREF_GATE_MARGIN_PX) & (parts["rise"] <= HAZY_SHARE_CUT * cut)
        fig, axes = plt.subplots(2, 6, figsize=(25, 10.8))
        imgs = [(before, "before (clear reference)"), (after, "after, as it is")] + [(o["corrected"], k) for k, o in
                                                                                     outs.items()]
        hazes = [(residual_haze(parts, np.where(valid, after, 0).astype(np.float32), valid), "haze left: as it is")] + [
            (residual_haze(parts, o["corrected"], valid), "haze left: " + k.split("\n")[0].split(" (")[0])
            for k, o in outs.items()]
        for ax, (img, title) in zip(axes[0], imgs):
            ax.imshow(np.where(valid, img, 0)[s], cmap="gray", vmin=0, vmax=255)
            ax.set_title(title, fontsize=9)
        axes[1, 0].imshow(np.where(clear, 0.35, 0)[s] + np.where(valid & ~clear & ~parts["gate"], 0.65, 0)[s]
                          + np.where(parts["gate"], 1.0, 0)[s], cmap="gray", vmin=0, vmax=1)
        axes[1, 0].set_title("white: cloud gate; light grey: margin,\nor hazy past it; dark grey: guard's clear ground",
                             fontsize=9)
        for ax, (img, title) in zip(axes[1, 1:], hazes):
            ax.imshow(np.where(valid, np.clip(img, 0, cut), 0)[s], cmap="gray", vmin=0, vmax=cut)
            ax.contour(edge[s], levels=[0.5], colors="white", linewidths=0.6, linestyles="dotted")
            ax.set_title(title, fontsize=9)
        for k, o in outs.items():
            if "FAILS" in k:
                ch_px = clear & (o["t"] < CHANGED_T)
                ax = axes[1, 1 + list(outs).index(k) + 1]
                ax.contour(ch_px[s], levels=[0.5], colors="white", linewidths=0.5)
                ax.set_title(ax.get_title() + f"\nsolid line: guard-clear pixels it changes ({ch_px[clear].mean():.1%} "
                             "of the tile's)", fontsize=9)
        for ax in axes.ravel():
            ax.axis("off")
        fig.suptitle(f"{tid}: the cloud edge, a {size // 2} m crop (rows {y}-{y + size}, columns {x}-{x + size}). Haze "
                     f"left = dark channel of the corrected after minus tone(dark channel of the before): black 0, "
                     f"white {cut:.0f} (the gate's cut) or more; dotted = gate edge", fontsize=10)
        fig.text(0.5, 0.008, note, ha="center", fontsize=9)
        fig.subplots_adjust(left=0.005, right=0.995, top=0.88, bottom=0.03, wspace=0.03, hspace=0.32)
        fig.savefig(FIG / f"ring_{tid}.png", dpi=100)
        plt.close(fig)
        print("saved", f"ring_{tid}.png")
        if tid == EXAMPLE:      # the whole tile, as on the deck, with the crop outlined
            fig, axes = plt.subplots(1, 5, figsize=(27, 7.0))
            for ax, (img, title) in zip(axes, imgs[1:]):
                ax.imshow(np.where(valid, img, 0), cmap="gray", vmin=0, vmax=255)
                ax.add_patch(plt.Rectangle((x, y), size, size, fill=False, ec="white", lw=1, ls="--"))
                ax.set_title(title, fontsize=10)
                ax.axis("off")
            fig.text(0.5, 0.01, note + ". Dashed box = the crop in ring_2_23_44.png.", ha="center", fontsize=9)
            fig.subplots_adjust(left=0.005, right=0.995, top=0.88, bottom=0.04, wspace=0.03)
            fig.savefig(FIG / f"ring_{tid}_whole_tile.png", dpi=90)
            plt.close(fig)
            print("saved", f"ring_{tid}_whole_tile.png")
    # band profile, report half
    d = all_rows()
    h = d[d.half == "report"]
    bands = list(BANDS_PX)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    styles = {"as it is": dict(color="0.65", ls="--", marker="s"), "current": dict(color="0.35", ls="-", marker="o"),
              best: dict(color="0.0", ls="-", marker="D", lw=2.2),
              ch["a"]["setting"]: dict(color="0.2", ls=":", marker="^"),
              ch["b"]["setting"]: dict(color="0.5", ls="-.", marker="v")}
    for ax, k, ylab in ((axes[0], "residual", "haze left (dark channel), grey levels"),
                        (axes[1], "grey residual", "corrected minus tone(before), grey levels")):
        for arm, st in styles.items():
            g = h[h.arm == arm]
            label = arm + (" (fails clear-ground guard)" if arm in (ch["a"]["setting"], ch["b"]["setting"]) else "")
            ax.plot(range(len(bands)), [g[f"{k} | {b}"].median() for b in bands], label=label, ms=7, lw=st.pop("lw", 1.6),
                    **st)
        ax.set_xticks(range(len(bands)))
        ax.set_xticklabels([b.replace("inside, ", "in: ").replace("out ", "") for b in bands], fontsize=8)
        ax.set_xlabel("band from the gate edge (pixels of 0.5 m; inside on the left)")
        ax.set_ylabel(ylab)
        ax.axhline(0, color="0.85", lw=0.8)
        ax.axvline(1.5, color="0.85", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle(f"Report half ({h.tile_id.nunique()} tiles): median over tiles of each band's median. "
                 "A ring-free edge would sit level with 'far'.", fontsize=10)
    fig.text(0.5, 0.01, "Measured on imagery from Maxar via SpaceNet 8", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(FIG / "ring_band_profile.png", dpi=120)
    plt.close(fig)
    print("saved ring_band_profile.png")


if __name__ == "__main__":
    stage = sys.argv[1]
    if stage == "arms":
        run({"as it is": (None, None), **{k: v for k, v in ARMS.items() if not k.startswith("e:")}},
            OUT / "arms_tiles.csv")
    elif stage == "arms_e":
        run({k: v for k, v in ARMS.items() if k.startswith("e:")}, OUT / "arms_e_tiles.csv")
    else:
        {"tiles": stage_tiles, "select": stage_select, "combo": stage_combo, "report": stage_report,
         "figures": stage_figures}[stage]()
