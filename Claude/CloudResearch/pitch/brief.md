# Design brief: "<deck title>"

## The talk
- **Presenter:** <name, role, institution>.
- **Course / venue:** <course or event>.
- **Event:** <what, date, time>. About <N> minutes, <N> slides. Audience: <who>.
- **The project, in plain words:** <3–6 bullets: what it does, the actors/components, the result so far>.
- **Domain:** <the field whose visual language the design should draw on, e.g. Earth observation, numerical
  analysis, epidemiology>.
- **Tone:** professional and research-grade, but distinctive and specific to the domain, not a generic corporate
  template.
- **Theme:** <new concept | reuse theme "<name>" | restyle an existing deck>.

## Figures and photos (Read them to see them)
Folder: `<abs path>/assets/`

| File | Size | Content and main colours | src for `<img>` |
|---|---|---|---|
| fig1.png | 1600×600 | <e.g. matplotlib on white, inferno heatmap, red outlines> | /_blob/<id> (after upload) or the file name |

The theme must frame these well (mats, borders, captions) and must not clash with their colours.

## Renderer constraints (hard rules; the full subset is in reference/format.md)
- One `<section>` per slide on a fixed **1920×1080** canvas, **all styles inline**:
  - no classes, `<style>`, `margin`, `z-index`, `var()`, em/rem/vw;
  - lengths in px.
- **Elements:**
  - h1 h2 h3 p ul/ol>li br b i u a, div, img, table/tr/th/td, hr;
  - `span` (colour only; **no font change on spans**);
  - inline `<svg>` (no text inside; labels are HTML on top);
  - `x-shape`, `x-connector`, `x-icon`.
- **Fonts:** Google Fonts only, at most **4 families**, declared once in deck.json `faces`.
- **Text:** ≥ 24px everywhere. Text wraps only at spaces, so size boxes to the longest word (≈ 0.6 × font-size
  per character).
- **Contrast:**
  - body text ≥ 4.5:1;
  - ≥ 3:1 only at ≥ 44px;
  - colours that must be told apart also differ in lightness;
  - never say something with colour alone.
- **Layout:**
  - margins 128px;
  - footer row pinned at bottom:64px;
  - ≤ 200 elements per slide;
  - ≤ 24 positioned children per div.

## Shared colour-role vocabulary (both specs use these names)
`bg-dark`, `bg-light`, `bg-alt`, `surface`, `surface-dark`, `ink`, `text`, `muted`, `ink-inverse`,
`text-inverse`, `muted-inverse`, `accent-1` … `accent-3` (one per actor or concept the deck must colour-code:
<name them>), `signal` (key numbers), `rule`, `rule-inverse`, `code-bg`, `code-text`, `status-good`,
`status-bad`.

## Slides (ids in order) and their content
For each slide: the id, the title, the content (bullets, table rows, images, code), the speaker-note intent, and
any `data-section` sentence.

**1 · cover**: "<title>"
- …

## Facts that may be used as motif text (true values only)
<e.g. coordinates, dates, sensors, sample sizes, version numbers>
