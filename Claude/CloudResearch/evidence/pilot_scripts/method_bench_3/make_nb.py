"""Builds and executes the method-bench-3 notebooks (notebooks/method_bench_3/). The notebooks only load cached outputs
(nb_cache.py's BIG/nb/, bench3_numbers.json, bench3r_numbers.json, bench3_decisions.json, the kept-road tables) and plot.

Execution: `jupyter nbconvert --to notebook --execute --inplace` is the requested command, but nbconvert is not
installed here and installs are not allowed (no downloads); nbclient (installed, the engine nbconvert --execute uses)
executes each notebook in place and nbformat saves it with its outputs (logged as a deviation).
    python3 -I make_nb.py G      # 01_grey_arms, 02_grey_combos
    python3 -I make_nb.py R      # 03_rgb_arms, 04_rgb_vs_grey
"""
import json
import sys
import time
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
NBDIR = HERE.parents[2] / "notebooks" / "method_bench_3"
BIG = Path("/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache")
REL = "evidence/pilot_scripts/method_bench_3"

LOOK = {
    "thin cloud": "This tile has the **largest thin-cloud area** of the Ida tiles: the ground is still visible through "
                  "the haze. A good correction makes the hazy part look like the NOAA aerial photo (road edges and roofs "
                  "with normal contrast and brightness, no grey veil, no dark blotches). In the |image − NOAA| maps, "
                  "darker inside the cloud means closer to NOAA.",
    "thick cloud": "This tile has the **largest opaque share** (t < 0.2). Nothing can be recovered under opaque cloud: a "
                   "correction should leave it as it is, and a gate should flag it. Look for arms that paint dark "
                   "patches into the cloud, and for gates that miss the core.",
    "clear": "This is a **clear tile** (under 1% dark-rise and bright pixels). Every gate should flag (almost) nothing "
             "and every correction should leave the image unchanged. Any red in the gate panels is a false alarm.",
    "flooded": "This tile has the **most roads labelled flooded** among the tiles with a cloud gate. Check whether the "
               "flood calls (blue = flooded and called flooded, orange = flooded but missed, red = false flood call) "
               "change between arms, and whether a gate hides flooded roads (grey = not assessed).",
    "smoke tile": "One of the three **smoke-test tiles** (preregistration amendments). It is shown so the smoke notes can "
                  "be checked against the images.",
}


def md(s):
    return nbf.v4.new_markdown_cell(s)


def code(s):
    return nbf.v4.new_code_cell(s)


def setup_cell(phase):
    return code(f"""import sys, json
sys.path.insert(0, '../../{REL}')
import numpy as np, pandas as pd
import matplotlib
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 70
import nbviz as V
num = V.numbers('{phase}')
kept = V.kept_table('{phase}')
tiles = json.loads((V.NB / '{phase}_tiles.json').read_text())
print('tiles:', tiles['chosen'])""")


def execute(path):
    import nbclient
    nb = nbf.read(path, as_version=4)
    t = time.time()
    nbclient.NotebookClient(nb, timeout=600, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}}).execute()
    nbf.write(nb, path)
    print(f"executed {path.name} in {time.time() - t:.0f} s")


def fmt(x, nd=2, pct=False):
    if x is None:
        return "n/a"
    return f"{100 * x:+.{nd}f}" if pct else f"{x:+.{nd}f}"


def ci(r, pct=True, nd=2):
    return f"{fmt(r['mean_gain'] if 'mean_gain' in r else r['mean_diff'], nd, pct)} " \
           f"[{fmt(r['ci'][0], nd, pct)}, {fmt(r['ci'][1], nd, pct)}]"


def tile_md(kind, tid, info, extra=""):
    parts = [f"### {kind.capitalize()}: tile `{tid}`", "", LOOK.get(kind, ""), "",
             f"- Thin-cloud pixels (score ∩ C0 gate ∩ t ≥ 0.2): {info['thin_px'].get(tid, 0):,} "
             f"(source: `{REL}/ida_rows_secondary.csv`).",
             (f"- C0 opaque share of valid pixels: {100 * info['opaque_share'][tid]:.1f}% "
              f"(source: `BIG/tiles/{tid}.pkl`, `c0_diag`)." if info["opaque_share"].get(tid) is not None else
              "- Not an Ida prep tile, so no NOAA view and no opaque share is listed."),
             f"- Touched roads: {info['roads'].get(tid, 0)}; labelled flooded: {info['flooded_roads'].get(tid, 0)} "
             f"(source: SN8 published labels via `sn8_heldout.touched_roads`).", extra]
    return md("\n".join(parts))


# ------------------------------------------------------------------------------------------------ Phase G notebooks
def build_01():
    num = json.loads((HERE / "bench3_numbers.json").read_text())
    sel = json.loads((BIG / "nb" / "G_tiles.json").read_text())
    import pickle
    corr = ["P1 Pan C tile", "P1w Pan C local", "S1 sphere DCP", "S1p sphere + Pan C", "M1 median DCP", "L1 Poisson seam"]
    gates = ["rise", "T1", "T1b", "B1", "B1p", "B2-1.3"]
    cells = [md(f"""# Method bench 3, Phase G (greyscale): every arm alone, on {len(sel['chosen'])} development tiles

**What this is.** The batch-D3 papers put into practice on the BT.601 grey tiles, each arm alone against the current
pipeline. Plan: `outputs/preregistration_method_bench_3.md` (written before any score). Numbers:
`{REL}/bench3_numbers.json`. Results write-up: `evidence/24_method_bench_3.md`. This notebook only **loads cached
outputs** (`/Volumes/USB2025/GeoAI-Descriptions/data/method_bench_3_cache/nb/`) and plots them; nothing is recomputed.

**Arms shown.**
- Gates (which pixels count as cloud; a road with ≥ 20% of its strip flagged is "cannot assess"): `rise` = production's
  dark-rise mask; **T1** Otsu on the grey rise (cut 108.8, the fallback, because η* = 0.547 < 0.65; the 0.65 is ours);
  **T1b** T1 + 2,500 m² blobs; **B1** EM/Bayes hysteresis per tile; **B1p** the same cuts pooled over training tiles;
  **B2** ICM-MRF (β 1.3; 1.6 and 1.8 are identical on the smoke tiles). **U1** (Dempster–Shafer) works per road, so it
  appears only in the road maps.
- Corrections (inside C0's gate, C0's 20 m fade, t < 0.2 left as is): **P1** Pan C-shift (C from the clear pre-storm
  date), **P1w** local C, **S1** sphere dark channel, **S1p** sphere + Pan's C, **M1** median dark channel, **L1**
  Poisson seam.
- Decision side: **Q1** (change ÷ t) and **PUL** (positive-unlabelled cut) change only the flood calls.

**How the tiles were chosen** (rule fixed in the preregistration before any result): the largest thin-cloud area, the
largest opaque share, a clear tile with the most roads, the tile with the most flooded roads, plus the smoke tiles.

**Colours in the road maps:** green = not flooded and called not flooded; blue = flooded and called flooded; red =
false flood call; orange = missed flood; grey = the arm's gate does not assess the road. Calls are seed 662 (the
spatial fold seed of the reproduction check); the road tables give the share of the 21 seeds that call each road
flooded."""), setup_cell("G"),
             code(f"CORR = {corr!r}\nGATES = {gates!r}\n"
                  "GATE_ARMS = ['production', 'T1 Otsu grey rise', 'B1 EM-Bayes hysteresis', 'B1p EM-Bayes pooled', "
                  "'B2 ICM-MRF beta 1.3', 'U1 DS certain gate', 'U1s DS strict']\n"
                  "CORR_ARMS = ['production', 'C0 current two-date'] + CORR + ['Q1 1/t on C0 current two-date', 'PUL', "
                  "'PULb binned c']")]
    for kind, tid in sel["chosen"]:
        f = BIG / "tiles" / f"{tid}.pkl"
        extra = ""
        if f.exists():
            r = pickle.loads(f.read_bytes())
            sh = r["tile_share"]
            extra = "- Share of valid pixels flagged: " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in sh.items()) + \
                    f" (source: `BIG/tiles/{tid}.pkl`)."
        cells += [tile_md(kind, tid, sel["info"], extra),
                  code(f"d = V.load('G', '{tid}')\nV.panel_images(d, CORR, 'tile {tid}: before, after, C0 and the "
                       f"Phase G corrections')\nV.panel_t(d, CORR)"),
                  md("**Gate masks** (red = flagged as cloud). Compare each arm with production's `rise`."),
                  code("V.panel_masks(d, GATES)"),
                  md("**Against the NOAA aerial view** (|image − NOAA| inside the Ida score mask; the title number is the "
                     "mean over C0's thin-cloud pixels on this tile, for orientation only: the scored statistic is the "
                     "DINOv2 feature distance over all 54–73 tiles, in notebook 02)."),
                  code("V.panel_noaa(d, CORR)"),
                  md("**Flood calls on the roads** (seed 662). Top: gates. Bottom: corrections and decision arms."),
                  code("V.panel_calls(d, GATE_ARMS, kept)\nV.panel_calls(d, CORR_ARMS[:5], kept)\n"
                       "V.panel_calls(d, CORR_ARMS[5:], kept)\n"
                       "V.road_table(d, ['production', 'B1 EM-Bayes hysteresis', 'U1 DS certain gate', 'P1 Pan C tile', "
                       "'PUL'], kept)")]
    cells += [md(f"""## Each arm alone: the numbers behind the pictures
Flood gain = accuracy minus production's, in points, mean over 21 seeds on the roads both keep, with a 3 × 3 block
bootstrap 95% interval (source: `{REL}/bench3_numbers.json`, key `flood`). Ida = DINOv2 feature distance to NOAA in thin
cloud, arm minus C0, per tile (key `ida_primary_vs_C0`); negative = closer to NOAA."""),
              code("""rows = []
for n, r in num['flood'].items():
    s = r['seeds']
    rows.append({'arm': n, 'roads kept': r['kept'], 'added': r.get('added', 0), 'removed': r.get('removed', 0),
                 '21-seed gain (pts)': round(100 * s['mean_gain'], 2),
                 '95% interval': f"[{100 * s['ci'][0]:+.2f}, {100 * s['ci'][1]:+.2f}]",
                 'seeds better': s['seeds_better'], 'seeds worse': s['seeds_worse'],
                 'accuracy on added roads': (round(r['added_acc']['mean'], 3) if 'added_acc' in r else None)})
pd.DataFrame(rows)"""),
              code("""rows = []
for a, r in (num.get('ida_primary_vs_C0') or {}).items():
    if r:
        g = (num.get('ida_grey_err_thin_vs_C0') or {}).get(a)
        rows.append({'arm': a, 'tiles': r['tiles'], 'feature distance vs C0': round(r['mean_diff'], 4),
                     '95% interval': f"[{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}]", 'guard ok': r.get('guard_ok'),
                     'grey error thin vs C0': (round(g['mean_diff'], 1) if g else None)})
pd.DataFrame(rows)""")]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = NBDIR / "01_grey_arms.ipynb"
    nbf.write(nb, p)
    return p


def build_02():
    num = json.loads((HERE / "bench3_numbers.json").read_text())
    dec = json.loads((HERE / "bench3_decisions.json").read_text())
    sel = json.loads((BIG / "nb" / "G_tiles.json").read_text())
    combo = num.get("combo", {})
    top = sorted(combo, key=lambda n: -combo[n]["mean_gain"])[:3]
    car = num.get("carry", {})
    cells = [md(f"""# Method bench 3, Phase G: combinations, forest plots and the decision table

**Carry rule** (preregistered so the factorial cannot stall): the top 2 arms per family by the family's primary metric
go into a 3 × 3 × 3 factorial (baseline, top-1, top-2 per family), labelled **exploratory** when they did not help alone.
Carried (source: `{REL}/bench3_numbers.json`, key `carry`): gates {car.get('gate')}, corrections {car.get('corr')},
decision arms {car.get('thr')}; exploratory: {car.get('exploratory')}.

**Interaction** = gain of the cell − the sum of its members' gains alone (all against production, on the cell's roads);
positive means the parts help each other. p-values are Holm-adjusted and quoted only where significant."""),
             setup_cell("G"),
             md("## Forest plots\nFlood calls: 21-seed accuracy gain vs production (points). Blue = interval above 0, "
                "red = below 0, grey = includes 0."),
             code("""rows = [(n, 100 * r['seeds']['mean_gain'], 100 * r['seeds']['ci'][0], 100 * r['seeds']['ci'][1])
        for n, r in num['flood'].items()]
V.forest(rows, 'Each arm alone: flood calls (21 seeds)', 'accuracy gain vs production (points)')"""),
             code("""rows = [(n, r['mean_diff'], r['ci'][0], r['ci'][1]) for n, r in (num.get('ida_primary_vs_C0') or {}).items() if r]
V.forest(rows, 'Corrections vs C0: DINOv2 feature distance to NOAA (thin cloud; < 0 = closer)', 'arm - C0')"""),
             code("""rows = [(n.replace('COMBO ', ''), 100 * r['mean_gain'], 100 * r['ci'][0], 100 * r['ci'][1]) for n, r in num.get('combo', {}).items()]
V.forest(rows, 'Factorial cells: flood calls (21 seeds)', 'accuracy gain vs production (points)')"""),
             code("""rows = [(n.replace('COMBO ', ''), 100 * r['interaction'], 100 * r['interaction_ci'][0], 100 * r['interaction_ci'][1]) for n, r in num.get('combo', {}).items()]
V.forest(rows, 'Interactions (cell gain - sum of member gains)', 'points')"""),
             md("## The top 3 cells on the same tiles\nFor each cell: its correction's output, its gate's mask and its "
                "flood calls at seed 662.")]
    for name in top:
        mem = combo[name]["members"]
        cells.append(md(f"### `{name.replace('COMBO ', '')}`: gain {ci(combo[name])} points vs production; interaction "
                        f"{100 * combo[name]['interaction']:+.2f} [{100 * combo[name]['interaction_ci'][0]:+.2f}, "
                        f"{100 * combo[name]['interaction_ci'][1]:+.2f}] (source: `bench3_numbers.json`, `combo`)."))
        corr_m = [m for m in mem if m in ("P1 Pan C tile", "P1w Pan C local", "S1 sphere DCP", "S1p sphere + Pan C",
                                          "M1 median DCP", "L1 Poisson seam")]
        gate_key = {"T1 Otsu grey rise": "T1", "T1b Otsu grey rise + blob": "T1b", "B1 EM-Bayes hysteresis": "B1",
                    "B1p EM-Bayes pooled": "B1p", "B2 ICM-MRF beta 1.3": "B2-1.3", "B2 ICM-MRF beta 1.6": "B2-1.6",
                    "B2 ICM-MRF beta 1.8": "B2-1.8"}
        gk = [gate_key[m] for m in mem if m in gate_key]
        for kind, tid in sel["chosen"][:4]:
            cells.append(code(f"d = V.load('G', '{tid}')\nprint('{kind}: {tid}')\n"
                              + (f"V.panel_images(d, {corr_m!r})\n" if corr_m else "")
                              + (f"V.panel_masks(d, ['rise'] + {gk!r})\n" if gk else "")
                              + f"V.panel_calls(d, ['production', {name!r}], kept)"))
    cells += [md(f"## Decision table (for Justin; nothing is promoted)\nRules (preregistration): **KEEP** helps alone and in "
                 f"combination with an interval excluding 0; **MAYBE** helps on one metric only, or within noise; **DROP** "
                 f"no help or harms; **NOT RUN** not runnable or conditional. Source: `{REL}/bench3_decisions.json`."),
              code("pd.set_option('display.max_colwidth', 200)\n"
                   "pd.DataFrame(json.loads((V.HERE / 'bench3_decisions.json').read_text())['phase_G'])")]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = NBDIR / "02_grey_combos.ipynb"
    nbf.write(nb, p)
    return p


def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "G"
    NBDIR.mkdir(parents=True, exist_ok=True)
    if phase == "G":
        for b in (build_01, build_02):
            execute(b())
    else:
        sys.path.insert(0, str(HERE))                  # fix: python -I drops the script folder from sys.path
        import make_nb_r
        for b in (make_nb_r.build_03, make_nb_r.build_04):
            execute(b())


if __name__ == "__main__":
    main()
