"""Writes the 3-slide investor pitch (Night Pass theme): motivation, method, prototype results.

    python3 -I build_pitch.py        # from this folder; then deckkit renumber / lint / render / pdf

Every number comes from the cloud research deck (../presentation/build_slides.py, assets/panel_numbers.json) and the
evidence files it cites (01, 12, 14, 15). No market, cost or funding figures: none were given.
"""
import hashlib
import json
import os

DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.join(DIR, "project", "slides")
N = json.load(open(os.path.join(DIR, "assets", "panel_numbers.json")))
amap = json.load(open(os.path.join(DIR, "assets.json")))


def blob(name):
    path = os.path.join(DIR, "assets", name)
    bid = "/_blob/" + hashlib.sha256(open(path, "rb").read()).hexdigest()[:32]
    amap[bid] = os.path.relpath(path, DIR)
    return bid


# ---------- theme pieces (design/design_spec.md, design/color_spec.md; as in the research deck) ----------
INK, TEXT, MUTED, BG, ALT, SURF, RULE = "#16131F", "#2E2B3B", "#5C5A69", "#F0F1F2", "#E7EAED", "#FFFFFF", "#C9CED5"
DARK, SURF_D, INK_I, TEXT_I, MUTED_I, RULE_I = "#120F1E", "#1F1A2E", "#F6F4EF", "#D6D2DF", "#A39EB2", "#3B3550"
STD, VAL, AGENT, SIGNAL, CONF, REJ = "#BC3754", "#23479A", "#420A68", "#FCA50A", "#0A7570", "#E8602A"
NOFLOOD = "#4FC3F7"
INFERNO = "#000004 0%, #280B53 14%, #65156E 29%, #9F2A63 43%, #D44842 57%, #F57D15 71%, #FAC228 86%, #FCFFA4 100%"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
ARCH = "font-family:'Archivo', Arial, sans-serif"
SANS = "font-family:'IBM Plex Sans', Arial, sans-serif"
TOTAL = 3
FOOT = "SEEING THROUGH CLOUDS · JUSTIN ROGERS · GEORGE MASON UNIVERSITY"
CREDIT = "Imagery: Maxar via SpaceNet 8"


def section(sid, body, notes, dark=False, extra=""):
    bg, col = (DARK, TEXT_I) if dark else (BG, TEXT)
    style = f"background:{bg};color:{col};{SANS};padding:128px 128px 160px;display:flex;flex-direction:column;gap:28px"
    bar = f'<div style="position:absolute;left:0;top:0;width:1920px;height:10px;background:linear-gradient(90deg, {INFERNO})"></div>'
    return f'<section id="{sid}"{extra} data-transition="fade" style="{style}">\n{bar}\n{body}\n{footer(dark)}\n<aside>{notes}</aside>\n</section>\n'


def footer(dark):
    c = MUTED_I if dark else MUTED
    return (f'<p style="position:absolute;left:128px;bottom:64px;width:1300px;{MONO};font-size:24px;letter-spacing:1px;color:{c}">{FOOT}</p>\n'
            f'<p style="position:absolute;right:128px;bottom:64px;width:200px;{MONO};font-size:24px;color:{c};text-align:right">00 / {TOTAL:02d}</p>')


def eyebrow(text, dark=False):
    return f'<p style="{MONO};font-size:24px;letter-spacing:2px;text-transform:uppercase;color:{MUTED_I if dark else MUTED}">00 · {text}</p>'


def h2(text, dark=False):
    return f'<h2 style="{ARCH};font-size:60px;font-weight:700;line-height:1.1;letter-spacing:-1px;color:{INK_I if dark else INK}">{text}</h2>'


def chip(word, fill):
    word_col = INK if fill in (SIGNAL, REJ, ALT) else INK_I
    return (f'<p style="align-self:start;{MONO};font-size:24px;font-weight:500;color:{word_col};background:{fill};'
            f'padding:4px 12px;border-radius:2px;white-space:nowrap">{word}</p>')


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


slides = {}

# ---------- 1 motivation (dark) ----------
fs = N["flooded_share"]
scale = 3.2
groups = [("clear roads", fs["clear"], CONF), ("thin cloud", fs["thin"], SIGNAL), ("opaque cloud", fs["opaque"], STD)]
bars = "\n".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:8px">{big(f"{g["pct"]:.0f}%", INK_I, 56)}'
                 f'<div style="width:150px;height:{max(round(g["pct"] * scale), 4)}px;background:{c}"></div></div>' for _, g, c in groups)
names = "\n".join(f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px"><p style="font-size:24px;color:{INK_I};text-align:center">{n}</p>'
                  f'<p style="font-size:24px;color:{MUTED_I};text-align:center">{g["roads"]} roads</p></div>' for n, g, _ in groups)
lkey = lambda c, t, op="": (f'<div style="display:flex;gap:10px;align-items:center"><div style="width:40px;height:8px;background:{c}{op}"></div>'
                            f'<p style="font-size:24px;color:{TEXT_I}">{t}</p></div>')
slides["motivation"] = section("motivation", f'''{eyebrow("Motivation · Hurricane Ida, Louisiana, 2021", True)}
{h2("After a disaster, cloud hides the flooded roads", True)}
<div style="display:flex;gap:56px;align-items:start">
<div style="width:400px;display:flex;flex-direction:column;gap:12px">
<img src="{blob("P2_tile_2_15_45.png")}" alt="Tile 2_15_45 after Hurricane Ida: thin cloud, tinted amber, covers the right half; every road labelled flooded, in crimson, lies on the clear left side" style="width:400px;height:400px;object-fit:cover;border:2px solid {RULE_I};border-radius:2px">
<div style="display:flex;gap:18px;flex-wrap:wrap">{lkey(STD, "flooded")}{lkey(SIGNAL, "thin cloud", ";opacity:0.6")}{lkey(NOFLOOD, "no flood label")}</div>
</div>
<div style="flex:1;display:flex;flex-direction:column;gap:16px">
{body("Satellite images taken after a disaster are often cloudy. Clouds hide the ground, so a flood map can be wrong exactly where it is needed.", 28, INK_I)}
{label("Roads labelled “flooded” by expert analysts, by cloud", SIGNAL)}
<div style="height:250px;display:flex;align-items:flex-end;gap:28px;border-bottom:2px solid {RULE_I}">
{bars}
</div>
<div style="display:flex;gap:28px">
{names}
</div>
{body("Analysts “only attribute what was visible” (Hänsch et al. 2022): under cloud a flooded road reads as dry, and models trained on those labels learn the same blind spot.", 24, TEXT_I)}
</div>
</div>
{panel(label("The opportunity", SIGNAL) + body("Flood maps people can trust under cloud: see through thin cloud with a second image, and say “cannot assess” where nothing can be seen.", 26, INK_I), True, "", "16px 28px")}''',
    f"After a disaster, the first satellite images are often cloudy, and clouds hide exactly the ground a flood map has to describe. In SpaceNet 8's Hurricane Ida data, {fs['clear']['pct']:.0f} percent of clear roads are labelled flooded, but only {fs['thin']['pct']:.0f} percent under thin cloud and {fs['opaque']['pct']:.0f} percent under opaque cloud. Part of that is geography, but the labelling rule matters: analysts only marked what they could see, so a flooded road under cloud reads as dry, and a model trained on those labels learns the same blind spot. In an earlier fit, our detector found 67 percent of flooded roads under thin cloud against 87 percent in clear sky. The opportunity is a flood map people can trust under cloud: see through thin cloud using a second image, and say plainly where the ground cannot be seen. {CREDIT}.", dark=True)

# ---------- 2 method ----------
def stage(n, accent, title, inner):
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:10px;background:{SURF};padding:22px;border:2px solid {RULE};'
            f'border-top:10px solid {accent};border-radius:4px">{label(n, accent)}'
            f'<h3 style="{ARCH};font-size:30px;font-weight:700;line-height:1.15;color:{INK}">{title}</h3>{inner}</div>')


crow = lambda word, fill, text: (f'<div style="display:flex;flex-direction:column;gap:4px">{chip(word, fill)}'
                                 f'<p style="font-size:24px;line-height:1.25">{text}</p></div>')
stages = [stage("1 · Detect", STD, "Find the cloud",
                body("A trained cloud spotter: brightness rule + texture (Haralick 1979) + DINOv2 features (Oquab et al. 2024).", 24)),
          stage("2 · Which date", VAL, "Tell which image is cloudy",
                body("Cloud lifts the darkest pixels; floods barely move them. A rise means cloud after, a fall cloud before.", 24)),
          stage("3 · See through", AGENT, "Correct from the clear date",
                body("Two-date de-hazing (our rule, after He et al. 2011): the clear image shows how dark the ground should be.", 24)),
          stage("4 · Handle", CONF, "Decide road by road",
                crow("ASSESS", CONF, "clear sky") + crow("CORRECT", SIGNAL, "thin cloud, seen through") + crow("CANNOT ASSESS", REJ, "opaque cloud"))]
arrows = "".join(f'<x-connector x1="{x}" y1="470" x2="{x + 28}" y2="470" head="end" style="color:{INK};border-width:3px"></x-connector>\n'
                 for x in (514, 924, 1334))
img = lambda f, alt, c: (f'<div style="display:flex;flex-direction:column;gap:8px"><img src="{blob(f)}" alt="{alt}" '
                         f'style="width:168px;height:168px;object-fit:cover;border:2px solid {RULE};border-radius:2px">'
                         f'<p style="{MONO};font-size:24px;color:{MUTED}">{c}</p></div>')
slides["method"] = section("method", f'''{arrows}{eyebrow("Method · a cloud-aware flood-road pipeline")}
{h2("See through thin cloud, flag what cannot be seen")}
<div style="display:flex;gap:28px">
{"".join(stages)}
</div>
<div style="flex:1"></div>
<div style="display:flex;gap:28px;align-items:end">
{img("P5_before.png", "Before the storm, tile 2_23_44: clear forest, houses and roads", "BEFORE")}
{img("P5_after.png", "After the storm, the same tile under thin cloud with a thick core", "AFTER · CLOUD")}
{img("P5_revised.png", "Two-date correction: the thin cloud lifted, the thick core marked opaque in orange", "SEEN THROUGH")}
{panel(label("Then the flood call", VAL) + body("A random forest (Breiman 2001) compares each road before and after on classical, texture and DINOv2 change cues. Every road gets a flood call or an honest “cannot assess”.", 24), extra=";flex:1", pad="20px 28px")}
</div>''', f"The method is a pipeline with four steps. First, detect the cloud with a trained spotter that combines a simple brightness rule, texture, and features from Meta's DINOv2 foundation model. Second, tell which date is cloudy: cloud lifts the darkest pixels in an image, while floods barely move them. Third, see through the cloud using the clear image as a reference: it tells us how dark the ground's darkest pixels should be, so we can estimate and remove the haze. Where the haze is too thick, below a transmission of 0.2, we do not invent ground. Fourth, decide road by road: assess, correct, or cannot assess. Then the flood detector, a random forest on classical, texture and DINOv2 change cues, makes the flood call. Example: tile 2_23_44, {CREDIT}.")

# ---------- 3 prototype results ----------
stat = lambda n, c, t: f'<div style="display:flex;flex-direction:column;gap:4px">{big(n, c, 64)}{body(t, 24)}</div>'
c3 = [("Flood calls in new areas", VAL,
       stat("78.6%", INK, "of 798 roads called right, in areas the model never trained on")
       + body("Always guessing “flooded” gets 55.3%. Spatially blocked folds (Roberts et al. 2017), 21 fold seeds.", 24, MUTED)),
      ("Cloud detection", STD,
       stat("0.87", INK, "F1 for our cloud spotter against expert cloud masks, vs 0.65 for the standard dark channel")
       + body("+0.22 (95% CI +0.19 to +0.25); better on 112 of 120 images (Li et al. 2019).", 24, MUTED)),
      ("Foundation-model gain", CONF,
       stat("+1.3", INK, "points of accuracy from the DINOv2 change vector (95% CI +0.4 to +2.4)")
       + body("Better in 21 of 21 fold seeds. A newer model (DINOv3, Siméoni et al. 2025) reaches 83.0% as a research benchmark: room to grow.", 24, MUTED))]
slides["results"] = section("results", f'''{eyebrow("Prototype results · Hurricane Ida · development data")}
{h2("A working prototype, scored where it never trained")}
<div style="display:flex;gap:28px">
{"".join(card(label(t, c) + inner, c, ";flex:1;gap:16px", 28) for t, c, inner in c3)}
</div>
<div style="flex:1"></div>
<div style="display:flex;gap:28px">
{panel(label("Where it stands", STD) + body("One event, one sensor, roads only. De-hazing helps under thin cloud but is not yet significant. Today's models are research-only: SpaceNet 8 and HRC_WHU limit commercial use.", 24), extra=";flex:1", pad="20px 28px")}
{panel(label("Next", AGENT) + body("Test on a second disaster; retrain on licence-clean data; then one final test on held-out areas that have never been scored.", 24), extra=";flex:1", pad="20px 28px")}
</div>''', "These are prototype results on Hurricane Ida development data. The flood detector calls 78.6 percent of 798 roads right in areas it never trained on, against 55.3 percent for always guessing flooded; we score in held-out areas because splitting by tile overstated accuracy by about 4 points. Our cloud spotter reaches an F1 of 0.87 against expert cloud masks, against 0.65 for the standard dark-channel method, better on 112 of 120 images. Features from Meta's DINOv2 foundation model add 1.3 points, in every one of 21 fold splits, and a newer model, DINOv3, reaches 83 percent as a research benchmark, so there is room to grow. The limits are honest ones: one event, one sensor, roads only; the de-hazing gain under thin cloud is not yet significant; and the current models are research-only because of the training data's licences. Next: a second disaster, licence-clean training data, then one final test on areas that have never been scored.")

ORDER = ["motivation", "method", "results"]
for sid in ORDER:
    open(os.path.join(SLIDES, f"{sid}.html"), "w").write(slides[sid])
deck = json.load(open(os.path.join(DIR, "project", "deck.json")))
deck["order"] = ORDER
deck["sections"] = {"s1": {"description": "Investor pitch: motivation, method and prototype results.", "start": "motivation"}}
json.dump(deck, open(os.path.join(DIR, "project", "deck.json"), "w"), indent=2, ensure_ascii=False)
json.dump(amap, open(os.path.join(DIR, "assets.json"), "w"), indent=2)
print("wrote", ", ".join(ORDER))
