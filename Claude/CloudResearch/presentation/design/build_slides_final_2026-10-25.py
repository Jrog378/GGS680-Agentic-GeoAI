"""Writes the cloud research deck's slide files (Night Pass theme) from brief.md's content.

    python3 -I build_slides.py        # from this folder; then deckkit renumber / lint / render / pdf

Every number comes from assets/panel_numbers.json (drawn by the panel script) or from evidence/01_measured_results.md.
Images are registered in assets.json under local /_blob/<sha256 prefix> ids so deckkit can render them.
"""
import hashlib
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.join(DIR, "project", "slides")
N = json.load(open(os.path.join(DIR, "assets", "panel_numbers.json")))

# ---------- assets ----------
amap = json.load(open(os.path.join(DIR, "assets.json")))


def blob(name):
    path = os.path.join(DIR, "assets", name)
    bid = "/_blob/" + hashlib.sha256(open(path, "rb").read()).hexdigest()[:32]
    amap[bid] = os.path.relpath(path, DIR)
    return bid


# ---------- theme pieces (design/design_spec.md, design/color_spec.md) ----------
INK, TEXT, MUTED, BG, ALT, SURF, RULE = "#16131F", "#2E2B3B", "#5C5A69", "#F0F1F2", "#E7EAED", "#FFFFFF", "#C9CED5"
DARK, SURF_D, INK_I, TEXT_I, MUTED_I, RULE_I = "#120F1E", "#1F1A2E", "#F6F4EF", "#D6D2DF", "#A39EB2", "#3B3550"
STD, VAL, AGENT, SIGNAL, CONF, REJ = "#BC3754", "#23479A", "#420A68", "#FCA50A", "#0A7570", "#E8602A"
CODE_BG, CODE_TX = "#0B0913", "#F4E3B0"
NOFLOOD = "#4FC3F7"  # the figure's own colour for roads with no flood label (legend key only)
INFERNO = "#000004 0%, #280B53 14%, #65156E 29%, #9F2A63 43%, #D44842 57%, #F57D15 71%, #FAC228 86%, #FCFFA4 100%"
SWEEP = "linear-gradient(120deg, #120F1E 0%, #160B39 40%, #420A68 70%, #6A176E 88%, #932667 100%)"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
ARCH = "font-family:'Archivo', Arial, sans-serif"
SANS = "font-family:'IBM Plex Sans', Arial, sans-serif"
TOTAL = 14
FOOT = "SEEING THROUGH CLOUDS · GGS 662 · 30 OCT 2026"
CREDIT = "Imagery: Maxar via SpaceNet 8"


def section(sid, body, notes, dark=False, extra=""):
    bg, col = (DARK, TEXT_I) if dark else (BG, TEXT)
    style = f"background:{bg};color:{col};{SANS};padding:128px 128px 160px;display:flex;flex-direction:column;gap:28px"
    bar = f'<div style="position:absolute;left:0;top:0;width:1920px;height:10px;background:linear-gradient(90deg, {INFERNO})"></div>'
    return f'<section id="{sid}"{extra} data-transition="fade" style="{style}">\n{bar}\n{body}\n{footer(dark)}\n<aside>{notes}</aside>\n</section>\n'


def footer(dark):
    c = MUTED_I if dark else MUTED
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1200px;{MONO};font-size:24px;letter-spacing:1px;color:{c}">{FOOT}</p>\n'
            f'<p style="position:absolute;right:128px;bottom:64px;width:200px;{MONO};font-size:24px;color:{c};text-align:right">00 / {TOTAL:02d}</p>')


def eyebrow(text, dark=False):
    return f'<p style="{MONO};font-size:24px;letter-spacing:2px;text-transform:uppercase;color:{MUTED_I if dark else MUTED}">00 · {text}</p>'


def h2(text, dark=False):
    return f'<h2 style="{ARCH};font-size:60px;font-weight:700;line-height:1.1;letter-spacing:-1px;color:{INK_I if dark else INK}">{text}</h2>'


def chip(word, fill, extra=""):
    word_col = INK if fill in (SIGNAL, REJ, ALT) else INK_I
    border = f"border:2px solid {RULE};" if fill == ALT else ""
    return (f'<p style="align-self:start;{MONO};font-size:24px;font-weight:500;color:{word_col};background:{fill};{border}'
            f'padding:4px 12px;border-radius:2px;white-space:nowrap{extra}">{word}</p>')


def label(text, color=MUTED):
    return f'<p style="{MONO};font-size:24px;font-weight:500;letter-spacing:2px;text-transform:uppercase;color:{color}">{text}</p>'


def card(inner, accent=None, extra="", pad=28):
    top = f"border-top:10px solid {accent};" if accent else ""
    return (f'<div style="display:flex;flex-direction:column;gap:12px;background:{SURF};padding:{pad}px;border:2px solid {RULE};{top}'
            f'border-radius:4px{extra}">{inner}</div>')


def panel(inner, dark=False, extra="", pad="24px 28px"):
    return (f'<div style="display:flex;flex-direction:column;gap:8px;background:{SURF_D if dark else ALT};padding:{pad};'
            f'border-radius:4px{extra}">{inner}</div>')


def body(text, size=26, color=None, extra=""):
    c = f"color:{color};" if color else ""
    return f'<p style="font-size:{size}px;line-height:1.38;{c}{extra}">{text}</p>'


def big(text, color=INK, size=64):
    return f'<p style="{ARCH};font-size:{size}px;font-weight:800;line-height:1.0;color:{color}">{text}</p>'


def pct(x):
    return f"{x:.0f}%"


slides = {}

# ---------- 1 cover ----------
grat = "".join(f'<div style="position:absolute;left:{x}px;top:0;width:2px;height:1080px;background:{INK_I};opacity:0.10"></div>\n'
               for x in (1180, 1440, 1700))
grat += "".join(f'<div style="position:absolute;left:1180px;top:{y}px;width:740px;height:2px;background:{INK_I};opacity:0.10"></div>\n'
                for y in (300, 560, 820))
slides["cover"] = f'''<section id="cover" data-section="Main talk: the problem, the questions, the method, the data, three preliminary results and the plan." data-transition="fade" style="background:{SWEEP};color:{INK_I};{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:32px">
{grat}<div style="position:absolute;left:0;bottom:0;width:1920px;height:14px;background:linear-gradient(90deg, {INFERNO})"></div>
<img src="{blob("P3_after.png")}" alt="After image of tile 2_19_55, Louisiana, after Hurricane Ida: forest and houses under a thin cloud, roads drawn in red" style="position:absolute;left:1272px;top:236px;width:520px;height:520px;object-fit:cover;border:2px solid {RULE_I};border-radius:2px">
<p style="{MONO};font-size:26px;font-weight:500;letter-spacing:3px;text-transform:uppercase;color:{SIGNAL};width:1080px">GGS 662 Agentic GeoAI · Research progress</p>
<h1 style="{ARCH};font-size:128px;font-weight:800;line-height:1.0;letter-spacing:-3px;color:{INK_I};width:1100px">Seeing Through Clouds</h1>
<p style="font-size:44px;line-height:1.3;color:{TEXT_I};width:1000px">Handling clouds in agentic change detection</p>
<p style="{MONO};font-size:26px;letter-spacing:1px;color:{TEXT_I}">TEST CASE: HURRICANE IDA 2021 · SPACENET 8 · 0.5 M EO</p>
<p style="font-size:30px;font-weight:600;color:{INK_I}">Justin Rogers · George Mason University · 30 October 2026</p>
<p style="font-size:26px;color:{TEXT_I};width:1080px">Preliminary results on development data · {CREDIT}</p>
<aside>We are building an agentic change detection system for satellite images taken after disasters. One difficulty we have run into is clouds in our electro-optical imagery: before the system can say what changed, it has to decide whether it can see the ground at all. I will show our proposed method of study, with the research questions and the literature behind each step, then the results so far, as pictures and as numbers. Everything here is preliminary and on development data.</aside>
</section>
'''

# ---------- 2 question ----------
problem = ("“Clouds can hide target areas in images taken after disasters. This can lead to labels being inaccurate "
           "compared to ground truth due to obscured parts of the imagery. How should we detect clouds in this imagery, "
           "handle them, and report them? The goal is results, such as maps of flooded roads, that people can trust.”")
qs = [("Report", VAL, "What can a flood-road map reliably tell users about roads hidden by cloud?"),
      ("Handle", AGENT, "When either image is cloudy, can seeing through it with the other date find change as well as under clear sky?"),
      ("Detect · the test bed", STD, "Can we use synthetic clouds to represent real-life blockages in satellite imagery?")]
TESTED = {"Handle": "Tested so far: thin cloud on the after image, corrected from the clear before image.",
          "Detect · the test bed": "On hold until we can reliably see through real cloud."}
qcards = "\n".join(card(label(l, c) + f'<h3 style="{ARCH};font-size:28px;font-weight:700;line-height:1.2;color:{INK}">{q}</h3>'
                        + (body(TESTED[l], 24, MUTED) if l in TESTED else ""), c, pad=18) for l, c, q in qs)
slides["question"] = section("question", f'''{eyebrow("Problem and research questions")}
{h2("Clouds hide what our change detector must see")}
<div style="display:flex;gap:40px">
<div style="width:800px;display:flex;flex-direction:column;gap:12px">
{body("<b>The system.</b> A vision foundation model finds where two images differ, an agent describes the change, and code checks every fact. For now, flood analysis: each road's features go into our model, which predicts flooded or not.", 24)}
{panel(label("One difficulty · clouds in EO imagery") + body(problem, 24, TEXT), pad="28px 32px")}
{body("Expected contribution: a tested rule for what a change map may say under cloud, a measured label gap, and a test of whether a second date can correct thin cloud.", 24, MUTED)}
{body("<b>Working rules.</b> Change is anything that differs between dates, except lighting. Cloud in either image is seen through first, as a preprocessing step.", 24)}
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:14px">
{qcards}
</div>
</div>''', "We are building an agentic change detection system: a vision foundation model finds where two satellite images differ, an agent describes what changed, and code checks every fact. One difficulty we have run into is clouds in our electro-optical imagery. In my own words: clouds hide parts of the after image, and the human labels are shaped by the same cloud. That gives three research questions, which we will work on in whatever order the work allows. Reporting: what can a map reliably say about roads it cannot see. Handling: whether the after image alone does better when only the before image is cloudy. Detection: whether synthetic clouds behave like real ones, because they are our test bed. The working definition, which I am still settling, is that change means change on the ground, so a cloud is something to see through or report, not a change.")

# ---------- 3 data ----------
south, west = N["tiles_south"], N["tiles_west"]
h = 412
ws, ww = round(h * N["P1_south_aspect"]), round(h * N["P1_west_aspect"])
key = lambda c, t: (f'<div style="display:flex;gap:10px;align-items:center"><div style="width:28px;height:28px;border:4px solid {c}"></div>'
                    f'<p style="font-size:24px">{t}</p></div>')
rows = [("Imagery", "Maxar Open Data before and after Hurricane Ida (landfall 29 Aug 2021), 0.5 m; image dates unconfirmed; greyscale"),
        ("Roads", "1,037 OpenStreetMap roads with SpaceNet 8 flood labels (Hänsch et al. 2022), on 217 of the 226 development tiles"),
        ("Split", "186 train · 40 validation · 40 test tiles, plus a 333-tile north negative set; the test tiles, the negative set, Germany and Louisiana-West have never been scored"),
        ("Cloud labels", "HRC_WHU (Li et al. 2019): 150 Google Earth images, 0.5–15 m, expert cloud masks; 120 development, 30 sealed; academic use only"),
        ("Unit", "One road = its OSM line plus a ~5 m band each side; tiles are the fold unit; dates aligned to ~0.6 m"),
        ("Quality issues", "Flood labels are “yes” or missing, never “no” · 17 tiles under opaque cloud · one after image for all development tiles")]
trs = "\n".join(f'<tr><td style="width:24%;color:{STD if k == "Quality issues" else INK}"><b>{k}</b></td><td style="width:76%">{v}</td></tr>' for k, v in rows)
slides["data"] = section("data", f'''{eyebrow("Data · SpaceNet 8 Louisiana-East · development tiles only")}
{h2("Study area and data")}
<div style="display:flex;gap:40px;align-items:start">
<div style="display:flex;flex-direction:column;gap:12px;width:{ws + ww + 24 + 36}px">
<div style="display:flex;gap:24px;background:{SURF};padding:16px;border:2px solid {RULE};border-radius:4px">
<img src="{blob("P1_south.png")}" alt="Mosaic of the south scene's {south["total"]} development tiles after the storm, each outlined by cloud class" style="width:{ws}px;height:{h}px;object-fit:contain">
<img src="{blob("P1_west.png")}" alt="Mosaic of the west scene's {west["total"]} development tiles after the storm, each outlined by cloud class" style="width:{ww}px;height:{h}px;object-fit:contain">
</div>
<div style="display:flex;gap:20px;flex-wrap:wrap">{key(CONF, "clear")}{key(SIGNAL, "thin cloud or haze")}{key(STD, "opaque")}</div>
{body(f"South ({south['total']} tiles) and west ({west['total']} tiles) after images, north up, bar 2 km; 29.7°N 90.0°W and 29.8°N 90.1°W · {CREDIT}", 24, MUTED)}
</div>
<table style="width:{1664 - 40 - (ws + ww + 60)}px;font-size:26px;color:{TEXT};background:{SURF};border:2px solid {RULE}">
{trs}
</table>
</div>''', f"The data are SpaceNet 8's Louisiana-East scenes from Hurricane Ida: Maxar images before and after the storm at half a metre, used in greyscale. Each outline is a development tile coloured by its cloud: {south['opaque'] + west['opaque']} tiles are under opaque cloud and many more under thin cloud or haze. The roads come from OpenStreetMap with SpaceNet 8's flood labels. Two checks matter: the flood label is either yes or missing, never no, and the split's fingerprint is logged, so the test tiles, the north negative set and the other areas have never been scored; every slip is logged in the data ledger. For cloud itself I use HRC_WHU, a set of expert cloud masks, with its test images sealed too.")

# ---------- 4 workflow ----------
def stage(x, w, accent, course, title, inner):
    return (f'<div style="position:absolute;left:{x}px;top:296px;width:{w}px;height:404px;display:flex;flex-direction:column;gap:10px;'
            f'background:{SURF};padding:24px;border:2px solid {RULE};border-top:10px solid {accent};border-radius:4px">'
            f'{label(course, accent)}<h3 style="{ARCH};font-size:32px;font-weight:700;color:{INK}">{title}</h3>{inner}</div>')


def crow(word, fill, text, w=220):
    return (f'<div style="display:flex;gap:14px;align-items:center"><div style="width:{w}px;display:flex">{chip(word, fill)}</div>'
            f'<p style="flex:1;font-size:24px;line-height:1.3">{text}</p></div>')


detect = stage(128, 380, STD, "GGS 680 · classical", "1 · Detect",
               body("Greyscale masks on each date: bright cores (our rule), the dark channel (He et al. 2011), and its rise from before to after (our rule).", 24))
handle = stage(580, 700, AGENT, "GGS 662 · the handle gate", "2 · Handle, feature by feature",
               crow("ASSESS", CONF, "clear sky") + crow("CORRECT", SIGNAL, "thin cloud + clear second date")
               + crow("CANNOT ASSESS", REJ, "opaque cloud")
               + f'<p style="font-size:24px;line-height:1.3;color:{MUTED}">Correct = two-date de-hazing inside the cloud mask (our rule, after He et al. 2011), then the detector again (result 3). Filled pixels count as not observed.</p>')
report = stage(1352, 440, VAL, "What the map may say", "3 · Report",
               body("Each statement about a hidden feature gets a tier:", 24)
               + f'<div style="display:flex;flex-direction:column;gap:10px">{chip("RELIABLE", CONF)}{chip("SYNTHETIC ONLY", SIGNAL)}{chip("RANGE ONLY", ALT)}</div>')
conn = "".join(f'<x-connector x1="{a}" y1="498" x2="{b}" y2="498" head="end" style="color:{INK};border-width:3px"></x-connector>\n'
               for a, b in ((508, 580), (1280, 1352)))
bottom = [("Change detector", MUTED, "Random forest (Breiman 2001) on classical, texture (Haralick 1979) and DINOv2 (Oquab et al. 2024) cues: 83.0% on 798 roads (always “flooded”: 55.3%)."),
          ("Baselines and checks", MUTED, "Tile cloud rule; no correction. Tile-blocked folds (Roberts et al. 2017), McNemar tests (McNemar 1947), one sealed check."),
          ("Agents propose, I decide", AGENT, "Question, critic and validation agents draft and check; the handle gate is coded rules. Decided by hand: the problem, the questions, the cloud rule.")]
bpanels = "\n".join(panel(label(t, c) + f'<p style="font-size:24px;line-height:1.3">{x}</p>', extra=";flex:1", pad="20px 28px") for t, c, x in bottom)
slides["workflow"] = section("workflow", f'''{detect}
{handle}
{report}
{conn}{eyebrow("Proposed method · each step cited or marked “our rule”")}
{h2("Proposed method: detect, handle, report")}
<div style="flex:1"></div>
<div style="display:flex;gap:24px">
{bpanels}
</div>''', "Three stages. Detect uses classical greyscale masks from GGS 680: bright cloud cores, the dark channel, and how much the dark channel rises from the before image to the after image. Handle is the agent gate from GGS 662: for each feature it decides to assess it, correct it with the second image and run the detector again, or say cannot assess. Report gives every statement about a hidden feature a tier: reliable, synthetic only, or a range. The detector underneath is a random forest on classical, texture and DINOv2 cues. The agents propose questions and critiques; I make the decisions.")

# ---------- 5 result1 ----------
fs = N["flooded_share"]
scale = 4.2
groups = [("clear roads", fs["clear"], CONF), ("thin cloud on the road", fs["thin"], SIGNAL), ("opaque-cloud tiles", fs["opaque"], STD)]
bars = "\n".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:8px">{big(pct(g["pct"]), INK, 56)}'
                 f'<div style="width:200px;height:{max(round(g["pct"] * scale), 4)}px;background:{c}"></div></div>' for _, g, c in groups)
names = "\n".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px"><p style="font-size:24px;color:{INK};text-align:center">{n}</p>'
                  f'<p style="font-size:24px;color:{MUTED};text-align:center">{g["roads"]} roads</p></div>' for n, g, _ in groups)
lkey = lambda c, t, op="": (f'<div style="display:flex;gap:10px;align-items:center"><div style="width:40px;height:8px;background:{c}{op}"></div>'
                            f'<p style="font-size:24px">{t}</p></div>')
slides["result1"] = section("result1", f'''{eyebrow("Result 1 · report · labels under cloud · preliminary")}
{h2("Under cloud, far fewer roads get a flood label")}
<div style="display:flex;gap:64px;align-items:start">
<div style="width:500px;display:flex;flex-direction:column;gap:12px">
<img src="{blob("P2_tile_2_15_45.png")}" alt="Tile 2_15_45 after the storm: thin cloud, tinted amber, covers the right half; every road labelled flooded, in crimson, lies on the clear left side, and the roads under the cloud carry no flood label" style="width:500px;height:500px;object-fit:cover">
<div style="display:flex;gap:20px;flex-wrap:wrap">{lkey(STD, "labelled “flooded”")}{lkey(SIGNAL, "thin cloud", ";opacity:0.6")}{lkey(NOFLOOD, "no flood label (reads as dry)")}</div>
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:12px">
{label("Roads labelled “flooded”, by cloud on the road")}
<div style="height:300px;display:flex;align-items:flex-end;gap:32px;border-bottom:2px solid {RULE}">
{bars}
</div>
<div style="display:flex;gap:32px">
{names}
</div>
{body("Analysts “only attribute what was visible” (Hänsch et al. 2022), so a flooded road under cloud reads as dry.", 28, INK, ";padding:12px 0 0 0")}
{body(f"Part of the gap is geography: the south scene is dry around its cloudy tiles. Left: an example tile, 2_15_45, after image · {CREDIT}", 24, MUTED)}
</div>
</div>''', f"The first result is about the labels, not the model. SpaceNet 8's analysts were told to only attribute what was visible, and the flood label is yes or missing, never no. So a road under cloud reads as dry. On clear roads {pct(fs['clear']['pct'])} are labelled flooded; under thin cloud only {pct(fs['thin']['pct'])}, and on opaque-cloud tiles {pct(fs['opaque']['pct'])}. Part of that gap is geography, but on this tile every flooded label sits on the clear side. Scoring a model on these labels rewards it for calling cloud dry. And under thin cloud an earlier fit of the model found 67% of the flooded roads against 87% in clear sky. I checked the cloud mask with synthetic haze: under thin haze it does not miss flooded roads more than dry ones.")

# ---------- 6 result2 (dark) ----------
dz, sy, P5 = N["dehaze"], N["synthetic"], N["P5"]
RC = N.get("roads_twodate")          # the road test (outputs/preregistration_twodate_roads.md), once it has run
cap = lambda t: f'<p style="{MONO};font-size:24px;color:{MUTED_I}">{t}</p>'
img3 = lambda f, alt, c: (f'<div style="display:flex;flex-direction:column;gap:10px"><img src="{blob(f)}" alt="{alt}" '
                          f'style="width:216px;height:216px;object-fit:cover;border:2px solid {RULE_I};border-radius:2px">{cap(c)}</div>')
SI, TD = "single image (He)", "revised fit"
ge = lambda m, k: f"{sy[f'{m} under haze: {k}']:.0f}"
dk = lambda k: f"{sy[f'detail kept under haze: {k}']:.2f}"
cg = lambda k: f"{100 * sy[f'clear ground read as haze: {k}']:.0f}%"
cell = lambda t, w, b=False, c=TEXT_I: f'<td style="width:{w}px;color:{c}">{"<b>" + t + "</b>" if b else t}</td>'
trow = lambda name, a, s_, t: f"<tr>{cell(name, 270, c=MUTED_I)}{cell(a, 95)}{cell(s_, 130)}{cell(t, 135, c=INK_I)}</tr>"
syn_table = (f'<table style="width:630px;font-size:24px;color:{TEXT_I}">'
             f'<tr>{cell("", 270)}{cell("none", 95, c=MUTED_I)}{cell("He 2011", 130, c=MUTED_I)}{cell("two-date", 135, c=MUTED_I)}</tr>'
             + trow("grey error (0–255)", ge("grey error", "as it is"), ge("grey error", SI), ge("grey error", TD))
             + trow("detail kept (1 = all)", dk("as it is"), dk(SI), dk(TD))
             + trow("clear altered", "0%", cg(SI), "<0.1%") + "</table>")
if RC:
    _t = "trusted flooded roads under thin cloud"
    _a = lambda k: ((N.get("roads_cornerfix") or N["roads_he"]) if k == "two-date · trained de-hazed" else N["roads_he"])[_t]["arms"][k]["count"]
    roads_box = (f"Flooded roads under thin cloud found, model trained on de-hazed images: {_a('two-date · trained de-hazed')} of 24 two-date, "
                 f"{_a('He 2011 · trained de-hazed')} He 2011, {_a('none')} with none. Not significant: result 3.")
    roads_label = "Flood calls · exploratory"
else:
    roads_box = "Flood calls on the 93 roads under thin cloud: running now, with the test written down first."
    roads_label = "Flood calls"
slides["result2"] = section("result2", f'''{eyebrow("Result 2 · handle · two-date de-hazing · exploratory", True)}
{h2("A second image lifts some thin cloud", True)}
<div style="display:flex;gap:20px;align-items:start">
{img3("P5_before.png", f"Before the storm, tile {P5['tile']}: clear forest, houses and roads", "BEFORE · CLEAR")}
{img3("P5_after.png", "After the storm, the same tile: thin cloud over the upper road, a thick core over the road on the right", "AFTER · CLOUD")}
{img3("P5_single.png", "He 2011 de-hazing of the after image alone: the whole tile changed, the cloud still bright", "HE 2011")}
{img3("P5_revised.png", "Two-date de-hazing: the thin cloud lifted, clear ground left alone, the thick core marked opaque in orange", "TWO-DATE")}
<div style="flex:1;display:flex;flex-direction:column;gap:12px;padding:0 0 0 12px">
{body(f"Road picked by a fixed rule: the most metres under thin cloud ({P5['m_under']:.0f} m, tile {P5['tile']}).", 24, TEXT_I)}
{body("Red = labelled flooded · blue = no flood label · orange = opaque, cannot assess.", 24, MUTED_I)}
{body("Haze model as used by He et al. (2011), whose de-hazing needs no before image: the baseline. Two-date de-hazing is our rule. Imagery: Maxar via SpaceNet 8.", 24, MUTED_I)}
</div>
</div>
<div style="flex:1"></div>
<div style="display:flex;gap:24px">
{panel(label(f"Synthetic haze · {sy['tiles']} clear tiles", SIGNAL) + syn_table + body("He 2011: de-hazes without the before image.", 24, MUTED_I), True, ";width:690px", "16px 24px")}
{panel(label("Caveat", REJ) + body("The synthetic haze follows our model (favours it), and two-date leaves clear ground alone by design; faint haze outside the mask is left alone. Here, little road detail returns.", 24, TEXT_I), True, ";flex:1", "16px 24px")}
{panel(label(roads_label, INK_I) + body(roads_box, 24, TEXT_I), True, ";flex:1", "16px 24px")}
</div>''', f"This is the two-date idea, on the road with the most metres under thin cloud. The before image tells us how dark the ground's darkest pixels should be, so how much they brightened gives the haze, and we only correct inside the cloud mask. The baseline is single-image de-hazing from He and colleagues, which has to assume the darkest pixel is black. On synthetic haze over {sy['tiles']} clear tiles, where we know the answer, single-image de-hazing gets closer on brightness, but it changes {cg(SI)} of the clear ground and keeps less detail; ours leaves clear ground alone and keeps the detail. That haze follows our model, so the check favours us, and faint haze outside the cloud mask is left alone. On this tile the haze lifts but little road detail comes back, and the thick core stays opaque: cannot assess. " + ("The flood calls on the de-hazed images are on the next slide." if RC else "The flood calls on these roads are the next test, written down before it is run."), dark=True)

# ---------- 7 flood calls on the de-hazed images (result 3) ----------
RC, CV, HE, FX = N["roads_twodate"], N["roads_cloudvars"], N["roads_he"], N.get("roads_cornerfix")
TF, DRY, CTL = ("trusted flooded roads under thin cloud", "dry-labelled roads under thin cloud (labels untrusted)",
                "control: assessable roads on the same tiles")
A1, A3 = "1 as it is · production", "3 as it is + cloud vars"
TDK, HEK = "two-date · trained de-hazed", "He 2011 · trained de-hazed"
# two-date arm: the rerun without the corner edit (outputs/preregistration_twodate_cornerfix.md) once it has run
src7 = lambda k: FX if (FX and k == TDK) else HE
arm7 = lambda g, k: src7(k)[g]["arms"][k]
vsn = lambda g, k: [r for r in src7(k)[g]["vs none"] if r["features"] == k][0]
HVT = N["he_vs_twodate"] if FX else {g: HE[g]["He vs two-date (both trained de-hazed)"][0] for g in (TF, DRY, CTL)}
arms = [("no de-hazing", MUTED, "none"), ("two-date (ours)", CONF, TDK), ("He 2011 (no before image needed)", VAL, HEK)]
SC = 2.2   # px per percentage point
def wbar(a, c):
    v, lo, hi = 100 * a["share"], 100 * a["lo"], 100 * a["hi"]
    return (f'<div style="position:relative;width:96px;height:{round(100 * SC) + 44}px">'
            f'<div style="position:absolute;left:6px;bottom:0px;width:58px;height:{max(round(v * SC), 4)}px;background:{c}"></div>'
            f'<div style="position:absolute;left:76px;bottom:{round(lo * SC)}px;width:4px;height:{max(round((hi - lo) * SC), 3)}px;background:{INK}"></div>'
            f'<div style="position:absolute;left:68px;bottom:{round(hi * SC)}px;width:20px;height:3px;background:{INK}"></div>'
            f'<div style="position:absolute;left:68px;bottom:{round(lo * SC)}px;width:20px;height:3px;background:{INK}"></div>'
            f'<p style="position:absolute;left:0px;bottom:{round(max(v, hi) * SC) + 8}px;width:96px;font-size:24px;font-weight:600;color:{INK};text-align:center">{v:.0f}%</p></div>')
fgroups = [("flooded roads under thin cloud found", f"{HE[TF]['roads']} roads, labels trusted", TF),
           ("dry-labelled roads under thin cloud called flooded", f"{HE[DRY]['roads']} roads, labels untrusted", DRY),
           ("clear roads on the same tiles called right", f"{HE[CTL]['roads']} roads", CTL)]
fcols = "\n".join(f'<div style="flex:1;display:flex;justify-content:center;align-items:flex-end;gap:10px">{"".join(wbar(arm7(g, k), c) for _, c, k in arms)}</div>'
                  for _, _, g in fgroups)
fnames = "\n".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px"><p style="font-size:24px;color:{INK};text-align:center">{a}</p>'
                   f'<p style="font-size:24px;color:{MUTED};text-align:center">{b}</p></div>' for a, b, _ in fgroups)
pick = lambda rep, name: [r for r in rep if r["features"] == name][0]
pa = pick(RC[CTL]["vs as it is"], "two-date")
cf = lambda g, k: CV[g]["called flooded"][k]
n_found = lambda k: arm7(TF, k)["count"]
gain = sorted({n_found(TDK) - n_found("none"), n_found(HEK) - n_found("none")})
gtxt = f"{gain[0]}–{gain[-1]}" if gain[0] != gain[-1] else f"{gain[0]}"
fx = lambda g, k: f"{vsn(g, k)['roads fixed']} fixed, {vsn(g, k)['roads broken']} broken (p = {vsn(g, k)['McNemar p']:.2f})"
pv = lambda p: "p < 0.001" if p < 0.001 else f"p = {p:.2f}"
slides["flood"] = section("flood", f'''{eyebrow("Result 3 · handle · flood calls on de-hazed images · exploratory")}
{h2(f"De-hazing finds {gtxt} more of 24 flooded roads, not significant")}
<div style="display:flex;gap:48px;align-items:start">
<div style="flex:1;display:flex;flex-direction:column;gap:12px">
<div style="display:flex;gap:24px;flex-wrap:wrap">{"".join(f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:{c}"></div><p style="font-size:24px">{lab}</p></div>' for lab, c, _ in arms)}</div>
<div style="display:flex;align-items:flex-end;gap:24px;border-bottom:2px solid {RULE}">
{fcols}
</div>
<div style="display:flex;gap:24px">
{fnames}
</div>
{body(f"Change is always found by comparing the before and after images; only the de-hazing of the after image differs. Whiskers: 95% interval, tiles resampled. Production flood model, 5 folds by tile, trained on the kind of image it is tested on (trained on uncorrected images, two-date cost clear roads: {pa['roads fixed']} fixed, {pa['roads broken']} broken, p = {pa['McNemar p']:.2f}). Plans written first; the 24 flooded roads were seen before. Labels: SpaceNet 8 (Hänsch et al. 2022); imagery: Maxar via SpaceNet 8.", 24, MUTED, ";padding:8px 0 0 0")}
</div>
<div style="width:540px;display:flex;flex-direction:column;gap:18px">
{panel(label("Against no de-hazing") + body(f"Flooded found: two-date {fx(TF, TDK)}; He {fx(TF, HEK)}. Clear roads: {pv(vsn(CTL, TDK)['McNemar p'])} and {pv(vsn(CTL, HEK)['McNemar p'])}.", 24), pad="18px 24px")}
{panel(label("Two-date against He 2011", STD) + body(f"Flooded found and clear roads: no difference ({pv(HVT[TF]['McNemar p'])}; {pv(HVT[CTL]['McNemar p'])}). He calls fewer cloudy dry-labelled roads flooded ({arm7(DRY, HEK)['count']} against {arm7(DRY, TDK)['count']}, {pv(HVT[DRY]['McNemar p'])}), but those labels are untrusted.", 24), pad="18px 24px")}
{panel(label("Cloud as an extra variable", AGENT) + body(f"No more flooded found ({cf(TF, A3)} of 24 against {cf(TF, A1)}); fewer cloudy dry-labelled roads called flooded ({cf(DRY, A3)} against {cf(DRY, A1)}), as cloudy roads were labelled dry.", 24), pad="18px 24px")}
</div>
</div>''', "notes in NOTES")

# ---------- 7 next ----------
li = lambda items: (f'<ul style="font-size:24px;line-height:1.35">'
                    + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
c7 = [("Feasible", CONF, ["Data, masks, de-hazer and the held-out harness all run",
                          "Dark-channel mask: F1 0.65 against 0.41 for the bright rule (HRC_WHU)",
                          f"Label gap measured: {pct(fs['clear']['pct'])}, {pct(fs['thin']['pct'])}, {pct(fs['opaque']['pct'])} labelled flooded (partly geography)",
                          "Each test runs in under an hour",
                          "By semester end: a frozen see-through step for thin cloud, and report tiers"]),
      ("Limits", STD, ["One event, one sensor, roads only; all real cloud in one after image; cloud shadows untested",
                       "Two-date not yet better than He 2011 on flood calls",
                       "De-hazing: only 24 trusted flooded roads, seen before; cloudy dry-labelled roads flagged", "Methods critic\'s five changes: adopted as defaults, not yet reviewed by me"]),
      ("Next steps", AGENT, ["See through cloud on either date, as a preprocessing step", "Smooth the ring at the cloud edge",
                             "Freeze the de-hazer; test it on a second event", "Tie it back into road detection and the flood model",
                             "Report tiers and maps", "Later: synthetic clouds, once real cloud can be seen through"])]
cards7 = "\n".join(card(f'<h3 style="{ARCH};font-size:30px;font-weight:700;color:{INK}">{t}</h3>' + li(items), c, ";flex:1", 26) for t, c, items in c7)
slides["next"] = section("next", f'''{eyebrow("Feasibility, limits and next steps")}
{h2("Feasibility, limits and next steps")}
<div style="display:flex;gap:28px">
{cards7}
</div>
<div style="flex:1"></div>
<div style="display:flex;flex-direction:column;gap:8px;background:{AGENT};padding:26px 36px;border-radius:4px">
{label("Question for discussion", SIGNAL)}
<p style="font-size:30px;line-height:1.35;color:{INK_I}">When a map cannot see the ground, should it say “cannot assess”, show a range, or fill it in from another date?</p>
</div>''', "The pieces all run: the data, the masks, the de-hazer and the held-out test harness, and the cloud mask beats the old rule against human cloud labels. The limits are real: one event, one sensor, roads only, all the real cloud in one after image, and only 24 trusted flooded roads under thin cloud. The methodology critic's verdict was revise, and those changes are in the next steps: pre-register first, build and check the synthetic test bed, test before-image cloud, set the report tiers, then one look at the sealed data. I'll end with a question for you: when a map cannot see the ground, should it say cannot assess, show a range, or fill it in from another date?")

# ---------- 8 masks (supporting) ----------
hr = N["hrc"]
types = ["vegetation", "water", "urban", "snow", "barren"]
sc = 330
pair = lambda t: "".join(f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px"><p style="font-size:24px;color:{INK}">{hr["by_type"][f"{m}|{t}"]:.2f}</p>'
                         f'<div style="width:64px;height:{round(hr["by_type"][f"{m}|{t}"] * sc)}px;background:{c}"></div></div>' for m, c in (("bright", MUTED), ("dark", STD)))
mbars = "\n".join(f'<div style="flex:1;display:flex;justify-content:center;align-items:flex-end;gap:8px">{pair(t)}</div>' for t in types)
mnames = "\n".join(f'<p style="flex:1;font-size:24px;color:{INK};text-align:center">{t}</p>' for t in types)
sq = lambda c, t: (f'<div style="display:flex;gap:10px;align-items:center"><div style="width:24px;height:24px;background:{c}"></div>'
                   f'<p style="font-size:24px">{t}</p></div>')
pb, pd = hr["pooled"]["bright"], hr["pooled"]["dark"]
slides["masks"] = section("masks", f'''{eyebrow("Supporting · detect · cloud masks against human cloud labels")}
{h2("Cloud masks against human cloud labels")}
<div style="display:flex;gap:64px;align-items:start">
<div style="flex:1;display:flex;flex-direction:column;gap:14px">
{label("F1 against expert cloud masks, by land cover")}
<div style="display:flex;gap:28px">{sq(MUTED, "bright rule (tile-rule baseline)")}{sq(STD, "dark-channel mask (He et al. 2011)")}</div>
<div style="height:340px;display:flex;align-items:flex-end;gap:16px;border-bottom:2px solid {RULE}">
{mbars}
</div>
<div style="display:flex;gap:16px">
{mnames}
</div>
</div>
<div style="width:640px;display:flex;flex-direction:column;gap:18px">
<div style="display:flex;flex-direction:column;gap:6px">{big(f"{pd['F1']:.2f}", STD, 56)}{body(f"F1, dark-channel mask (precision {pd['P']:.2f}, recall {pd['R']:.2f})", 24)}</div>
<div style="display:flex;flex-direction:column;gap:6px">{big(f"{pb['F1']:.2f}", MUTED, 56)}{body(f"F1, bright rule (precision {pb['P']:.2f}, recall {pb['R']:.2f})", 24)}</div>
{body(f"{hr['images']} HRC_WHU development images (Li et al. 2019; 30 sealed). HRC_WHU has one date per scene, so only masks that need one date are checked here.", 24, MUTED)}
{panel(label("Mask-bias check") + body("Synthetic haze on 769 clear roads: under thin haze the mask flags flooded and dry roads alike; under thick haze it flags flooded roads more (up to +13 points), not less.", 24))}
</div>
</div>''', f"This is the check on the cloud masks against human cloud labels, HRC_WHU's expert masks on {hr['images']} development images. The bright rule is precise but finds only about a quarter of the cloud; the dark-channel mask finds about two thirds with F1 {pd['F1']:.2f}. It is best on vegetation and water and its false alarms are bright bare ground. The threshold learned on SpaceNet 8 is close to the best one on HRC_WHU. I also checked whether the mask hides floods selectively, using synthetic haze on clear roads: under thin haze it does not; under thick haze it flags flooded roads more, not less.", extra=' data-section="Supporting slides: the mask check, how the two images are layered, references, code and AI use, full references, and what is still open."')

# ---------- 9 layering (supporting, dark) ----------
img4 = lambda f, alt, step, c: (f'<div style="width:330px;display:flex;flex-direction:column;gap:10px"><img src="{blob(f)}" alt="{alt}" '
                                f'style="width:330px;height:330px;object-fit:cover;border:2px solid {RULE_I};border-radius:2px">'
                                f'<p style="{MONO};font-size:24px;font-weight:500;color:{SIGNAL}">{step}</p>{body(c, 24, TEXT_I)}</div>')
slides["layering"] = section("layering", f'''
<p style="position:absolute;left:458px;top:404px;width:115px;{ARCH};font-size:72px;font-weight:800;line-height:1.0;color:{SIGNAL};text-align:center">+</p>
<x-connector x1="917" y1="449" x2="1004" y2="449" head="end" style="color:{SIGNAL};border-width:4px"></x-connector>
<x-connector x1="1362" y1="449" x2="1449" y2="449" head="end" style="color:{SIGNAL};border-width:4px"></x-connector>
{eyebrow("Supporting · two-date de-hazing, step by step", True)}
{h2("How the two images are layered", True)}
<div style="display:flex;justify-content:space-between;align-items:start">
{img4("P5_before.png", f"Before image of tile {P5['tile']}, clear", "1 · BEFORE", "Clear reference: the ground's darkest pixels")}
{img4("P5_after.png", "After image of the same tile with cloud", "2 · AFTER", "Ground dimmed by t, plus airlight A(1 − t)")}
{img4("P5_t_revised.png", "Fitted haze t in the inferno colour scale: bright yellow (t = 1, clear) over the forest and houses, darker under the cloud, black over the thick core", "3 · HAZE t", "Inside the cloud mask only; houses stay at 1")}
{img4("P5_revised.png", "The corrected after image, with the opaque core in orange", "4 · CORRECTED", "Orange: opaque (t below 0.2), cannot assess")}
</div>
<p style="{MONO};font-size:24px;color:{CODE_TX};background:{CODE_BG};border:2px solid {RULE_I};padding:12px 24px;border-radius:4px">t = (A − dark after) ÷ (A − tone(dark before))  ·  corrected = (after − A) ÷ t + A</p>
{body("Standard haze model and dark channel as used by He et al. (2011). Our rules: the before image\'s darkest pixels in place of He\'s zero assumption, the tone curve, a 2,500 m² cloud minimum, a 20 m fade past the mask, and t below 0.2 left as opaque. Imagery: Maxar via SpaceNet 8, tile 2_23_44.", 24, TEXT_I)}''', "This is how the two images are layered. The haze model says a hazy pixel is the ground dimmed by t, plus the airlight A times one minus t. The dark channel, the darkest pixel in a 20 metre square, is the key: under cloud even the darkest pixel brightens. He's method, which de-hazes the after image without the before image, assumes the ground's darkest pixel is black. We have the before image, so we know how dark it really was, once the two dates' grey levels are matched with a curve on clear pixels. How much it brightened gives t. We only do this inside the cloud mask, fading out over 20 metres past it, and only for cloud blobs of at least 2,500 square metres, so a changed roof is not read as haze. Where t drops below 0.2 the ground cannot be recovered, so that part is cannot assess.", dark=True)

# ---------- 10 refs, code and AI use (supporting) ----------
lit = [("Li et al. 2019", "HRC_WHU cloud masks · ISPRS J. Photogramm. Remote Sens."),
       ("He, Sun &amp; Tang 2011", "Dark channel prior · IEEE TPAMI"), ("Oquab et al. 2024", "DINOv2 (Meta AI) · TMLR"), ("Haralick 1979", "Texture features · Proc. IEEE (abstract checked)"),
       ("Roberts et al. 2017", "Blocked cross-validation · Ecography")]
background = ("Canty &amp; Nielsen 2008 (Remote Sensing of Environment) · Portalés-Julià et al. 2023 (Scientific Reports) · Qu, Li &amp; Huang 2026 (Remote Sensing of Environment) · "
              "Shen et al. 2015 (IEEE Geoscience and Remote Sensing Magazine) · Bruzzone &amp; Bovolo 2013 (Proc. IEEE)")
attributions = "Breiman 2001, random forests (Machine Learning) · McNemar 1947, paired proportions (Psychometrika)"
row = lambda a, b: (f'<div style="display:flex;gap:24px"><p style="width:290px;font-size:24px;font-weight:600;color:{INK}">{a}</p>'
                    f'<p style="flex:1;font-size:24px">{b}</p></div>')
rrows = "\n".join(row(a, b) for a, b in lit)
ai = ["Claude Code (Anthropic) agents drafted questions, critiques, notes, code, figures and slides.",
      "Justin chose the problem, questions and cloud rule; 28 decisions on AI suggestions are logged, most in his own words (10 changed, 6 rejected).",
      "His checks of the haze maps set a minimum cloud size (houses are not haze) and a label-free tile pick.",
      "A validation agent checked claims against the papers; agent agreement is not validation."]
slides["refs"] = section("refs", f'''{eyebrow("Supporting · references, code and AI use")}
{h2("References, code and AI use")}
<div style="display:flex;gap:48px;align-items:start">
<div style="flex:1;display:flex;flex-direction:column;gap:20px">
<div style="display:flex;flex-direction:column;gap:2px">
{label("Cited on these slides")}
{rrows}
</div>
<div style="display:flex;flex-direction:column;gap:2px">{label("Background")}{body(background, 24)}</div>
<div style="display:flex;flex-direction:column;gap:2px">{label("Method attributions")}{body(attributions, 24)}</div>
{body("Data: SpaceNet 8 flood and road labels, Hänsch et al. 2022 (licences differ: see full references) · HRC_WHU (academic use only)", 24, MUTED)}
</div>
<div style="width:620px;display:flex;flex-direction:column;gap:20px">
{panel(label("Code") + body("github.com/Jrog378/GeoAI-Roads (private; access on request): masks, de-hazing, notebooks", 24), pad="24px 28px")}
{panel(label("AI use") + "".join(body(a, 24) for a in ai), pad="20px 26px")}
</div>
</div>''', "These are the sources behind the slides: the methods cited on them, the background papers, the two method attributions and the data. The code is in the private GeoAI-Roads repository. Claude Code agents drafted much of the material; I made the decisions, every result comes from code on development data, and a validation agent checked the claims against the papers.")

# ---------- 11b, 11c full references (supporting; verified against Crossref / TMLR / CVF, evidence/08) ----------
CITED = [
    "He, K., Sun, J. &amp; Tang, X. (2011). Single image haze removal using dark channel prior. <i>IEEE TPAMI</i> 33(12), 2341–2353. doi:10.1109/TPAMI.2010.168",
    "Li, Z., Shen, H., Cheng, Q., et al. (2019). Deep learning based cloud detection for medium and high resolution remote sensing images of different sensors. <i>ISPRS J. Photogramm. Remote Sens.</i> 150, 197–212. doi:10.1016/j.isprsjprs.2019.02.017",
    "Oquab, M., Darcet, T., Moutakanni, T., et al. (2024). DINOv2: Learning robust visual features without supervision. <i>Transactions on Machine Learning Research</i>. openreview.net/forum?id=a68SUt6zFt",
    "Haralick, R. M. (1979). Statistical and structural approaches to texture. <i>Proc. IEEE</i> 67(5), 786–804. doi:10.1109/PROC.1979.11328",
    "Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. <i>Ecography</i> 40(8), 913–929. doi:10.1111/ecog.02881",
    "Hänsch, R., Arndt, J., Lunga, D., et al. (2022). SpaceNet 8 – The detection of flooded roads and buildings. <i>CVPR Workshops</i>, 1471–1479. doi:10.1109/CVPRW56347.2022.00153",
    "Breiman, L. (2001). Random forests. <i>Machine Learning</i> 45(1), 5–32. doi:10.1023/A:1010933404324",
    "McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. <i>Psychometrika</i> 12(2), 153–157. doi:10.1007/BF02295996"]
BACKGROUND = [
    "Canty, M. J. &amp; Nielsen, A. A. (2008). Automatic radiometric normalization of multitemporal satellite imagery with the iteratively re-weighted MAD transformation. <i>Remote Sens. Environ.</i> 112(3), 1025–1036. doi:10.1016/j.rse.2007.07.013",
    "Portalés-Julià, E., Mateo-García, G., Purcell, C., et al. (2023). Global flood extent segmentation in optical satellite images. <i>Scientific Reports</i> 13, 20316. doi:10.1038/s41598-023-47595-7",
    "Qu, Y., Li, J. &amp; Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. <i>Remote Sens. Environ.</i> 334, 115239. doi:10.1016/j.rse.2026.115239",
    "Shen, H., Li, X., Cheng, Q., et al. (2015). Missing information reconstruction of remote sensing data: A technical review. <i>IEEE Geosci. Remote Sens. Mag.</i> 3(3), 61–85. doi:10.1109/MGRS.2015.2441912",
    "Bruzzone, L. &amp; Bovolo, F. (2013). A novel framework for the design of change-detection systems for very-high-resolution remote sensing images. <i>Proc. IEEE</i> 101(3), 609–630. doi:10.1109/JPROC.2012.2197169"]
refp = lambda t: f'<p style="font-size:24px;line-height:1.28">{t}</p>'
cols2 = lambda items: (f'<div style="display:flex;gap:40px;align-items:start">'
                       + "".join(f'<div style="flex:1;display:flex;flex-direction:column;gap:14px">{"".join(refp(t) for t in half)}</div>'
                                 for half in (items[:(len(items) + 1) // 2], items[(len(items) + 1) // 2:])) + "</div>")
slides["fullrefs"] = section("fullrefs", f'''{eyebrow("Supporting · full references, cited on the slides")}
{h2("Full references: cited")}
{cols2(CITED)}
{body("Checked against Crossref, TMLR and the CVF open-access copy (evidence 08). Breiman and McNemar are method attributions.", 24, MUTED)}''', "The full references for every method cited on the slides, checked against the publishers' records.")
slides["bgrefs"] = section("bgrefs", f'''{eyebrow("Supporting · full references, background")}
{h2("Full references: background")}
{cols2(BACKGROUND)}
{body("Data: SpaceNet 8 imagery from the Maxar Open Data Program; the paper states a Creative Commons 4.0 non-commercial licence, the SpaceNet site CC BY-SA 4.0. HRC_WHU: academic use only.", 24, MUTED)}''', "The background papers for the proposal, and the data licences: the SpaceNet 8 paper and the SpaceNet site state different licences, so the imagery is treated as non-commercial.")

# ---------- 12 what is still open (supporting) ----------
backend = [("DONE", CONF, "Road finding under cloud vs OSM: no gain (F1 0.020 → 0.017)"),
           ("TO FIX", REJ, "Before-date cloud: fires on 29 clear tiles"),
           ("TO FIX", REJ, "Faint-haze gate: none kept clear ground within 1%"),
           (("TO COMMIT", REJ, "De-hazer corner edit on cloud-free tiles: result 3 rerun without it; library fix and test") if FX else
            ("RUNNING", VAL, "Result 3 rerun without the de-hazer's 20 m corner edit on cloud-free tiles")),
           ("TO BUILD", ALT, "Cloud code as its own library (GeoAI-Clouds)"),
           ("TO BUILD", ALT, "Cloud mask in GeoAI-Descriptions (cloud = cannot assess)"),
           ("RUNNING", VAL, "Smoother edge for the de-hazer (the ring at the cloud edge)"),
           ("TO BUILD", ALT, "Stage notebooks that rerun these tests")]
inputs = [("DECIDE", SIGNAL, "The methods critic's five changes (now defaults)"),
          ("DECIDE", SIGNAL, "Report-tier cut-offs"),
          ("DATA", AGENT, "A second event, ideally with a cloudy before image"),
          ("ACCESS", ALT, "Haralick full text: GMU login with Justin"),
          ("ACCESS", ALT, "Dates for the four Maxar catalog IDs"),
          ("ACCESS", ALT, "SpaceNet 8 licence: paper and site differ"),
          ("DECIDED", CONF, "Sealed tiles untouched; synthetic clouds wait for real see-through; change = anything but lighting; floods only")]
orow = lambda w, f, t: (f'<div style="display:flex;gap:14px;align-items:start"><div style="width:170px;display:flex">{chip(w, f)}</div>'
                        f'<p style="flex:1;font-size:24px;line-height:1.3">{t}</p></div>')
slides["open"] = section("open", f'''{eyebrow("Supporting · backend work and inputs needed")}
{h2("What is still open")}
<div style="display:flex;gap:40px;align-items:start">
{card(label("Backend · code and runs", VAL) + "".join(orow(*b) for b in backend), VAL, ";flex:1.25", 24)}
{card(label("Decisions and access needed", AGENT) + "".join(orow(*b) for b in inputs), SIGNAL, ";flex:1", 24)}
</div>''', "This slide lists what is still open. On the backend: the road-finding test against the OSM roads is running; cloud on the before date and the faint-haze gate both need fixing before use; and the cloud code is moving into its own library, which GeoAI-Descriptions will also use. The decisions are mine: whether to spend the one look at the sealed tiles, whether synthetic haze may count as truth for training, the definition of change, the report-tier cut-offs, the journal, and two access questions.")

# ---------- spoken notes for the 4-minute talk (about 560 words; the long version is in design/notes_long_2026-10-25.md) ----------
NOTES = {
    "cover": "We are building an agentic change detection system for satellite images after disasters. One difficulty is cloud in our electro-optical imagery. Here is our method, our questions, and what we have found so far, all on development data.",
    "question": "The system finds where two images differ, describes what the change looks like, and checks the facts in code; for now that feeds a flood model for roads. Change means anything on the ground, not lighting. Cloud breaks this: it hides the ground, and the human labels are shaped by the same cloud. So we ask what a map can reliably report under cloud, and whether seeing through cloud with the other date finds change as well as clear sky. Synthetic clouds as a test bed wait until we can see through real cloud.",
    "workflow": "The method has three steps. Detect: classical greyscale cloud masks on each date. Handle: feature by feature, assess it, correct it with the second date, or say cannot assess. Report: every statement about a hidden feature gets a tier. Underneath is our random forest flood detector, at 83 percent on clear roads. Agents draft and critique; I make the decisions.",
    "data": "The test case is Hurricane Ida in Louisiana: Maxar before and after images at half a metre, and 1,037 OpenStreetMap roads with SpaceNet 8 flood labels, on development tiles only. The test tiles and the other areas have never been scored. Two quality issues matter: flood labels are yes or missing, never no, and all the real cloud sits in one after image.",
    "result1": "The first result is about the labels. Under cloud, far fewer roads carry a flood label: 55 percent of clear roads, 26 percent under thin cloud, 2 percent on opaque tiles. Part of that is geography, but analysts only labelled what they could see, so a flooded road under cloud reads as dry. On this tile every flood label sits on the clear side. A model scored on these labels is rewarded for calling cloud dry.",
    "result2": "The second result is the two-date idea. The clear before image tells us how dark the ground's darkest pixels should be, so how much they brightened measures the haze, and we correct only inside the cloud mask. On synthetic haze, He's method, which does not use the before image, gets closer on brightness but changes most of the clear ground; ours keeps the detail and leaves clear ground alone. This test favours our method, because the fake haze follows our model. On this tile little road detail comes back.",
    "flood": f"Then the flood calls, each test written down before it ran. Change is always found by comparing the before and after images; only the de-hazing differs, and each model is trained on the kind of image it is tested on. Under thin cloud, two-date de-hazing finds {n_found(TDK)} of the 24 flooded roads and He's de-hazing {n_found(HEK)}, against {n_found('none')} with none; neither gain is significant, and clear roads stay near {100 * arm7(CTL, 'none')['share']:.0f} percent. So far our two-date method does not beat the baseline on flood calls. Cloud as an extra variable found no more flooded roads. These roads were seen before, so this is exploratory.",
    "next": "Everything runs, and each test takes under an hour. The limits: one event and one sensor, only 24 trusted flooded roads under cloud, and two-date is not yet better than the He baseline on flood calls. Next: see through cloud on either date as a preprocessing step, smooth the ring at the cloud edge, freeze the de-hazer and test it on a second event, then tie it back into the road and flood work. My question for you: when a map cannot see the ground, should it say cannot assess, show a range, or fill it in from another date?",
}
import re as _re
for _sid, _text in NOTES.items():
    slides[_sid] = _re.sub(r"<aside>.*?</aside>", lambda _m: f"<aside>{_text}</aside>", slides[_sid], flags=_re.S)

ORDER = ["cover", "question", "workflow", "data", "result1", "result2", "flood", "next", "masks", "layering", "refs", "fullrefs", "bgrefs", "open"]
assert len(ORDER) == TOTAL and set(ORDER) == set(slides)
os.makedirs(SLIDES, exist_ok=True)
for sid in ORDER:
    with open(os.path.join(SLIDES, f"{sid}.html"), "w", encoding="utf-8") as f:
        f.write(slides[sid])
json.dump(amap, open(os.path.join(DIR, "assets.json"), "w"), indent=1)
dpath = os.path.join(DIR, "project", "deck.json")
d = json.load(open(dpath))
d.update(order=ORDER, cover="cover",
         sections={"s1": {"description": "Main talk: the problem, the questions, the method, the data, three preliminary results and the plan.", "start": "cover"},
                   "s2": {"description": "Supporting slides: the mask check, how the two images are layered, references, code and AI use, full references, and what is still open.", "start": "masks"}})
json.dump(d, open(dpath, "w"), indent=2)
print("wrote", len(ORDER), "slides")
