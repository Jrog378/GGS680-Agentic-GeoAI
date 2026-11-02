# Design spec: "Night Pass" (house theme)

Distilled from the GeoAI-Descriptions working-group deck (9 Oct 2026), the deck Justin liked. Colours come from
`color_spec.md` (palette and contrast table). Working slides are in `examples/`; copy their markup rather than
re-deriving it.

**Concept.** The deck is read off the inferno colorbar:
- dark slides sit at its violet-black floor, the night side of the Earth from orbit;
- warm accents are inferno samples;
- light slides are a neutral light-table grey, so white matplotlib plates and photos are not tinted.

It suits Earth observation, remote sensing and data-heavy science talks. For a different domain, keep the
structure and re-pick the colormap and motifs with the colour and design agents.

## Fonts (deck.json `faces`, 3 families)
| Family | Weights | Job |
|---|---|---|
| Archivo | 500–800 | cover title, slide titles, card titles, big numbers |
| IBM Plex Sans | 400, 600 | body, tables, captions (section default) |
| IBM Plex Mono | 400, 500 | eyebrows, footer, chips, code, metadata strips |

## Type scale (px)
| Use | Size and style |
|---|---|
| Cover title (h1) | 136, Archivo 800, line-height 1.0, letter-spacing −3px |
| Cover subtitle | 44, text-inverse |
| Slide title (h2) | 60, Archivo 700, line-height 1.1, letter-spacing −1px, ink |
| Eyebrow | 24, Plex Mono, uppercase, letter-spacing 2px, muted. Format `NN · Section · detail` (NN = page − 1) |
| Card title (h3) | 28–34, Archivo 700 |
| Body | 24–30, line-height 1.3–1.45 |
| Big number | 56–72, Archivo 800, with an optional 120×10px signal marker bar under it |
| Small part of a big number | 36, Archivo 800, muted. **Write it as a separate `<p>` in a flex row with `align-items:baseline`, never as a span.** |
| Footer | 24, Plex Mono, letter-spacing 1px, muted. Left: `DECK · COURSE · DATE`; right: `NN / TT` |

## Grid and skeleton
- **Content slide:** `<section>` with
  `background:bg-light; color:text; font-family:'IBM Plex Sans'; padding:128px 128px 160px; display:flex;`
  `flex-direction:column; gap:28px`.
- **Header:** the eyebrow `<p>`, then the `<h2>`. The title top lands at y ≈ 190 on every content slide.
- **Signature top bar:** the first child of each light content slide is a pinned 10px inferno colorbar strip:
  `position:absolute; left:0; top:0; width:1920px; height:10px; background:linear-gradient(90deg, #000004 0%, #280B53 14%, #65156E 29%, #9F2A63 43%, #D44842 57%, #F57D15 71%, #FAC228 86%, #FCFFA4 100%)`.
  Dark slides use the same strip, 14px, at the bottom.
- **Footer:** two pinned `<p>`s at `bottom:64px`, left 128px (width 1200) and right 128px (width 200, right
  aligned).
- **Vertical budget:** the body sits between y ≈ 290 and 920.

## Components (see examples/)
- **Card:**
  `background:surface; padding:24–36px; border:2px solid rule; border-top:10px solid <accent>; border-radius:4px`.
  The accent identifies the actor; an untinted card has no top colour.
- **Panel:** `background:bg-alt; padding:28–36px; border-radius:4px`, with no border.
- **Table:** `font-size:26px; background:surface; border:2px solid rule`. The header row is `bg-alt` with `ink`
  text. Set column widths with `width:N%` on every first-row cell. Status words are coloured cells or chips,
  always with the word.
- **Figure plate (white matplotlib PNGs, light slides only):** `background:surface; padding:12–20px;`
  `border:2px solid rule; border-radius:4px`, with a muted 24px caption below.
- **Photo frame (dark slides):** `border:2px solid rule-inverse; border-radius:2px`, with a mono 24px caption in
  muted-inverse under it.
- **Chip:** `<p>` in Plex Mono 24px 500, `padding:4px 12px; border-radius:2px`, filled with confirmed / standard /
  validation (ink-inverse word) or rejected / signal (ink word).
- **Code well:** `background:code-bg; color:code-text`, Plex Mono 26–28px, `padding:16px 24px;`
  `border:2px solid rule-inverse`.
- **Connectors:** `<x-connector … head="end" style="color:ink; border-width:3px">` between pipeline cards.
- **Cover:**
  - background: the inferno sweep gradient;
  - faint graticule (2px lines in ink-inverse at opacity 0.10) in the right third;
  - the 14px colorbar at the bottom;
  - a mono signal-coloured kicker line, the title, the subtitle, a mono metadata line, then the presenter line.

## Background rhythm
- A dark or sweep slide roughly every 4th slide: cover, the photo-heavy test-case slide, the hand-check slide,
  and the demo/closing slide.
- Everything else is bg-light.

## Do / don't
- **Do** keep one idea per slide: a title that states the finding, and the evidence under it.
- **Do** keep speaker notes conversational, as `<aside>`, ≥ 25 words.
- **Don't** put text on the colorbar strip or over the last 30% of the sweep.
- **Don't** add hues beyond `color_spec.md`.
- **Don't** set font sizes or families on spans.
- **Don't** use any text under 24px.
