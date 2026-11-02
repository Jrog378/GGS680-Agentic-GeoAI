"""Phase R notebooks: 03_rgb_arms.ipynb (every RGB arm alone, the same tiles as Phase G) and 04_rgb_vs_grey.ipynb (R
combinations, forest plots, decisions, and grey-best vs RGB-best side by side with error crops where they disagree).
Built and executed by make_nb.py R. Loads cached outputs only."""
import json

import nbformat as nbf

from make_nb import BIG, HERE, LOOK, NBDIR, REL, ci, code, md, setup_cell, tile_md


def build_03():
    num = json.loads((HERE / "bench3r_numbers.json").read_text())
    cfg = json.loads((HERE / "carry_R.json").read_text())
    sel = json.loads((BIG / "nb" / "G_tiles.json").read_text())
    corr = ["A2b HOT lower-bound", "A2b-noW no water proxy", "A2b-auto MAD limit"] + [f"RGB {a}" for a in cfg["corr"]]
    gates = ["rise", "D1e IHOT-RGB", "D1e-BR IHOT blue-red"] + [f"RGB {g}" for g in cfg["gates"]
                                                               if not g.startswith("U1")]
    fl = list(num.get("flood", {}))
    cells = [md(f"""# Method bench 3, Phase R (RGB): every arm alone, on the same tiles as Phase G

**What this is.** Phase R uses the colour bands. **R0** is the colour baseline: production's 93 road features computed
per band (R, G, B) in place of grey, same forest, folds and seeds. Every Phase R arm is compared with R0 and with
production. Plan: `outputs/preregistration_method_bench_3.md`; numbers: `{REL}/bench3r_numbers.json`; carry-overs from
Phase G: `{REL}/carry_R.json` (gates {cfg['gates']}, corrections {cfg['corr']}, decision arms {cfg['thr']}).

**Arms shown.**
- Gates: **D1e** IHOT on RGB pairs (two-date iterated haze index, Chen 2016) with the EM/Bayes cut, **D1e-BR** blue and
  red only, and the Phase G gates carried over in RGB form (dark channel = minimum over bands).
- Corrections: **A2b** Zhang & Guindon HOT haze correction (lower-bound slope over ΔHOT in (2, 20], two-date water proxy;
  pixels above 20 are "cannot assess"), **A2b-noW** without the water proxy, **A2b-auto** with a data-driven lower
  limit, and the Phase G corrections carried over in colour.
- Cue: **ISFA** (iterative slow feature analysis, Wu 2014) change magnitude added to R0's columns; ISFA-grey control.

RGB corrections are shown in colour and scored as their grey copy against the grey NOAA view (one yardstick for both
phases). Road colours as in notebook 01."""), setup_cell("R"),
             code(f"CORR = {corr!r}\nGATES = {gates!r}\nFLOOD = {fl!r}")]
    for kind, tid in sel["chosen"]:
        cells += [tile_md(kind, tid, sel["info"]),
                  code(f"""d = V.load('R', '{tid}')
fig, ax = plt.subplots(1, 2 + len([c for c in CORR if 'rgb|' + c in d]), figsize=(15, 3.4))
ax[0].imshow(d['before_rgb'][::2, ::2]); ax[0].set_title('before (RGB)', fontsize=8)
ax[1].imshow(d['after_rgb'][::2, ::2]); ax[1].set_title('after (RGB, as is)', fontsize=8)
k = 2
for c in CORR:
    if 'rgb|' + c in d:
        ax[k].imshow(d['rgb|' + c][::2, ::2]); ax[k].set_title(c[:28], fontsize=8); k += 1
for a in ax: a.axis('off')
plt.tight_layout(); plt.show()"""),
                  md("**Gate masks** (red = flagged), the iHOT haze index (bright = hazy) and the ISFA change magnitude "
                     "(bright = changed)."),
                  code("V.panel_masks(d, GATES)\n"
                       "fig, ax = plt.subplots(1, 2, figsize=(7, 3.3))\n"
                       "for a, k, t in zip(ax, ['ihot', 'isfa_iwd'], ['iHOT (D1e)', 'ISFA change (IWD)']):\n"
                       "    (a.imshow(d[k][::2, ::2], cmap='magma') if k in d else a.text(0.3, 0.5, 'abstained'))\n"
                       "    a.set_title(t, fontsize=8); a.axis('off')\nplt.tight_layout(); plt.show()"),
                  md("**Against the NOAA aerial view** (grey copies)."),
                  code("V.panel_noaa(d, CORR)"),
                  md("**Flood calls** (seed 662): production, R0 and the Phase R arms."),
                  code("V.panel_calls(d, ['production', 'R0 colour baseline'] + [g for g in GATES[1:] if g in FLOOD][:3], kept, phase='R')\n"
                       "V.panel_calls(d, ['R0 colour baseline'] + [c for c in CORR if c in FLOOD][:4], kept, phase='R')\n"
                       "V.panel_calls(d, ['R0 colour baseline', 'ISFA-RGB IWD + SFA1', 'ISFA-grey control'], kept, phase='R')")]
    cells += [md(f"## Each Phase R arm alone (source: `{REL}/bench3r_numbers.json`, key `flood`; vs R0 = `vs_base`)"),
              code("""rows = []
for n, r in num['flood'].items():
    s = r['seeds']; vb = r.get('vs_base', {}).get('seeds')
    rows.append({'arm': n, 'kept': r['kept'], '21-seed gain vs production': round(100 * s['mean_gain'], 2),
                 '95% interval': f"[{100 * s['ci'][0]:+.2f}, {100 * s['ci'][1]:+.2f}]",
                 'gain vs R0': (round(100 * vb['mean_gain'], 2) if vb else None),
                 'vs R0 interval': (f"[{100 * vb['ci'][0]:+.2f}, {100 * vb['ci'][1]:+.2f}]" if vb else None)})
pd.DataFrame(rows)"""),
              code("""rows = []
for a, r in (num.get('ida_primary_vs_C0') or {}).items():
    if r:
        rows.append({'arm': a, 'tiles': r['tiles'], 'feature distance vs C0': round(r['mean_diff'], 4),
                     '95% interval': f"[{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}]", 'guard ok': r.get('guard_ok')})
pd.DataFrame(rows)""")]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = NBDIR / "03_rgb_arms.ipynb"
    nbf.write(nb, p)
    return p


def build_04():
    num = json.loads((HERE / "bench3r_numbers.json").read_text())
    gv = num.get("grey_vs_rgb", {})
    sel = json.loads((BIG / "nb" / "G_tiles.json").read_text())
    bg, br = gv.get("best_grey"), gv.get("best_rgb")
    r = gv.get("rgb_minus_grey")
    r0 = gv.get("R0_vs_production")
    cells = [md(f"""# Method bench 3: RGB combinations, and the best grey set-up against the best RGB set-up

**Best grey** (highest 21-seed gain vs production in Phase G, single arm or factorial cell): `{bg}`.
**Best RGB** (same rule in Phase R): `{br}`.
**RGB minus grey** on the roads both assess: {ci(r) if r else 'n/a'} points (21 seeds, 3 × 3 block bootstrap; source:
`{REL}/bench3r_numbers.json`, key `grey_vs_rgb`). **R0 vs production:** {ci(r0) if r0 else 'n/a'} points.

Below: the Phase R forest plots and interactions, the decision table, then the two best set-ups side by side on the same
tiles, with **error crops** where their calls disagree."""), setup_cell("R"),
             code("""rows = [(n, 100 * r['seeds']['mean_gain'], 100 * r['seeds']['ci'][0], 100 * r['seeds']['ci'][1]) for n, r in num['flood'].items()]
V.forest(rows, 'Phase R arms alone: flood calls vs production (21 seeds)', 'points')
rows = [(n, 100 * r['vs_base']['seeds']['mean_gain'], 100 * r['vs_base']['seeds']['ci'][0], 100 * r['vs_base']['seeds']['ci'][1])
        for n, r in num['flood'].items() if 'vs_base' in r]
V.forest(rows, 'Phase R arms alone: flood calls vs R0 (21 seeds)', 'points')"""),
             code("""rows = [(n.replace('COMBO R ', ''), 100 * r['mean_gain'], 100 * r['ci'][0], 100 * r['ci'][1]) for n, r in num.get('combo', {}).items()]
if rows: V.forest(rows, 'Phase R factorial cells vs production', 'points')
rows = [(n.replace('COMBO R ', ''), 100 * r['interaction_vs_R0'], 100 * r['interaction_ci'][0], 100 * r['interaction_ci'][1]) for n, r in num.get('combo', {}).items()]
if rows: V.forest(rows, 'Phase R interactions (vs R0)', 'points')"""),
             code("pd.set_option('display.max_colwidth', 200)\n"
                  "pd.DataFrame(json.loads((V.HERE / 'bench3_decisions.json').read_text()).get('phase_R', []))"),
             md(f"## `{bg}` (grey) against `{br}` (RGB) on the same tiles\nLeft: the grey set-up's calls; right: the "
                f"RGB set-up's calls. Below each tile: crops (about 100 m) around the roads where the two disagree, "
                f"with the label.")]
    for kind, tid in sel["chosen"]:
        cells.append(code(f"""d = V.load('R', '{tid}')
print('{kind}: {tid}')
V.panel_calls(d, ['production', {bg!r}, {br!r}], kept, phase='R')
rd = d['roads']
cg, cr = rd.get('call662|{bg}'), rd.get('call662|{br}')
if cg is not None and cr is not None:
    ka = [bool(kept[V.KEPT_ALIAS.get(c, c)].iloc[int(i)]) if V.KEPT_ALIAS.get(c, c) in kept.columns else True
          for c in ({bg!r}, {br!r}) for i in rd.road_row]
    n = len(rd)
    both = np.array(ka[:n]) & np.array(ka[n:])
    dis = rd[(cg != cr) & both]
    print(len(dis), 'roads assessed by both set-ups where their seed-662 calls disagree')
    for _, x in dis.head(4).iterrows():
        ys, xs = np.nonzero(d['strip'] == x.strip_id)
        cy, cx = int(ys.mean()), int(xs.mean()); h = 100
        sl = (slice(max(cy - h, 0), cy + h), slice(max(cx - h, 0), cx + h))
        fig, ax = plt.subplots(1, 3, figsize=(8, 2.8))
        ax[0].imshow(d['before_rgb'][sl]); ax[0].set_title('before', fontsize=8)
        ax[1].imshow(d['after_rgb'][sl]); ax[1].set_title('after', fontsize=8)
        ax[2].imshow(d['after_rgb'][sl]); ax[2].contour(d['strip'][sl] == x.strip_id, colors='yellow', linewidths=0.8)
        ax[2].set_title(f"road {{x.road_id}}: label {{'flooded' if x.flooded else 'not flooded'}}; grey calls {{int(x['call662|{bg}'])}}, RGB calls {{int(x['call662|{br}'])}}", fontsize=7)
        for a in ax: a.axis('off')
        plt.tight_layout(); plt.show()"""))
    cells += [md("## Error crops across all development tiles\nRoads assessed by both set-ups where their **21-seed "
                 "majority** calls differ (calls: `BIG/bench3_flood_calls.npz`, `BIG/bench3r_flood_calls.npz`; labels: "
                 "SN8 published). Up to 8 roads, ordered by tile; each crop is ~100 m around the road (yellow outline). "
                 "Only these tiles' images are read (development tiles)."),
              code(f"""import sys
sys.path.append('/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions')
zg, zr = np.load(V.BIG / 'bench3_flood_calls.npz'), np.load(V.BIG / 'bench3r_flood_calls.npz')
cg = np.stack([zg[f'{bg}__{{s}}'] for s in V.SEEDS]); cr = np.stack([zr[f'{br}__{{s}}'] for s in V.SEEDS])
mg, mr = (cg == 1).mean(0) > 0.5, (cr == 1).mean(0) > 0.5
kg = kept[V.KEPT_ALIAS.get({bg!r}, {bg!r})].to_numpy().astype(bool) if V.KEPT_ALIAS.get({bg!r}, {bg!r}) in kept.columns else kept['production (refit)'].to_numpy().astype(bool)
kr = kept[{br!r}].to_numpy().astype(bool) if {br!r} in kept.columns else kept['production (refit)'].to_numpy().astype(bool)
idx = np.flatnonzero(kg & kr & (mg != mr))
y = kept.flooded.to_numpy()
print(len(idx), 'roads (of', int((kg & kr).sum()), 'assessed by both) where the majority calls differ;',
      int((mg[idx] == y[idx]).sum()), 'of them the grey set-up is right,', int((mr[idx] == y[idx]).sum()), 'the RGB set-up')
from sn8_clouds import _tile
from sn8_cloudspot import _strip
from sn8_lines import road_band
for i in idx[:8]:
    tid, rid = kept.tile_id.iloc[i], kept.road_id.iloc[i]
    p, b, a, v = _tile(tid)
    strip, roads, n, cpx = _strip(tid, p, v, road_band())
    ks = [k + 1 for k in range(n) if roads[k + 1]['road_id'] == rid]
    if not ks: continue
    m = strip == ks[0]
    ys, xs = np.nonzero(m); cy, cx = int(ys.mean()), int(xs.mean()); h = 100
    sl = (slice(max(cy - h, 0), cy + h), slice(max(cx - h, 0), cx + h))
    fig, ax = plt.subplots(1, 3, figsize=(8, 2.8))
    ax[0].imshow(p['before_rgb'][sl]); ax[0].set_title(f'{{tid}} before', fontsize=8)
    ax[1].imshow(p['after_rgb'][sl]); ax[1].set_title('after', fontsize=8)
    ax[2].imshow(p['after_rgb'][sl]); ax[2].contour(m[sl], colors='yellow', linewidths=0.8)
    ax[2].set_title(f"label {{'flooded' if y[i] else 'not flooded'}}; grey {{'flooded' if mg[i] else 'dry'}}, RGB {{'flooded' if mr[i] else 'dry'}}", fontsize=7)
    for q in ax: q.axis('off')
    plt.tight_layout(); plt.show()""")]
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = NBDIR / "04_rgb_vs_grey.ipynb"
    nbf.write(nb, p)
    return p
