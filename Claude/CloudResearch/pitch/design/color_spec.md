# Colour spec: "Night Pass"

## 1. Concept
**Night Pass: the deck is read off the inferno colorbar.** Dark slides sit at the floor of the inferno colormap, the violet-black of "no change" that also looks like the night side of the Earth from orbit. The warm roles are inferno samples: DINOv3 is inferno 0.50, so the standard and its heatmap share one hue, and the signal is the sodium-light amber at 0.80. Light slides are a neutral light-table grey with graticule hairlines, so the white matplotlib plates and the beige/brown Maxar scenes are not tinted. The reviewer's colours (Gemma blue, confirmed teal) sit outside the heat scale.

## 2. Roles
| role | hex | where it is used |
|---|---|---|
| bg-dark | #120F1E | cover base, imagery-viewer slides, demo; inferno floor |
| bg-light | #F0F1F2 | all content, figure and table slides |
| bg-alt | #E7EAED | bands, side panels, table header row (a panel tone, not a slide tone) |
| surface | #FFFFFF | cards on light; the plate behind every matplotlib figure |
| surface-dark | #1F1A2E | cards and panels on dark |
| ink | #16131F | headings and table headers on light |
| text | #2E2B3B | body on light |
| muted | #5C5A69 | captions, credits, footer, axis-style labels on light |
| ink-inverse | #F6F4EF | headings on dark/sweep; word inside dark chips |
| text-inverse | #D6D2DF | body on dark |
| muted-inverse | #A39EB2 | captions/footer on dark |
| accent-standard | #BC3754 | DINOv3: eyebrows, 8px card top-borders, chips (inferno 0.50) |
| accent-validation | #23479A | Gemma: eyebrows, borders, chips |
| accent-agent | #420A68 | agent: eyebrows, borders, question panel fill (inferno 0.20) |
| signal | #FCA50A | big numbers and key words on dark; marker bars/chips on light (inferno 0.80) |
| rule | #C9CED5 | hairlines, graticule, table rules, figure-plate border on light |
| rule-inverse | #3B3550 | hairlines, graticule, photo border, code-well border on dark |
| code-bg | #0B0913 | code blocks/command wells (on light and on dark) |
| code-text | #F4E3B0 | monospace text on code-bg ("phosphor cream", inferno 1.0 toned down) |
| confirmed | #0A7570 | verdict chip fill (word in ink-inverse); text on light |
| rejected | #E8602A | verdict chip fill (word in ink); text on dark |

**Inferno sweep (statement treatment):** `linear-gradient(120deg, #120F1E 0%, #160B39 40%, #420A68 70%, #6A176E 88%, #932667 100%)`
**Colorbar band (signature strip, never behind text):** `linear-gradient(90deg, #000004 0%, #280B53 14%, #65156E 29%, #9F2A63 43%, #D44842 57%, #F57D15 71%, #FAC228 86%, #FCFFA4 100%)` (true inferno at t = 0, 1/7 … 1)

## 3. Contrast (WCAG 2, computed). **Bold** = passes 4.5 (body); "3:1" = only at >= 44px; x = do not use
| text \ bg | bg-light | bg-alt | surface | bg-dark | surface-dark | code-bg |
|---|---|---|---|---|---|---|
| ink | **16.2** | **15.2** | **18.3** | x | x | x |
| text | **12.2** | **11.4** | **13.8** | x | x | x |
| muted | **5.9** | **5.6** | **6.7** | x | x | x |
| accent-standard | **4.9** | **4.6** | **5.5** | 3.4 (3:1) | 3.1 (3:1) | 3.6 (3:1) |
| accent-validation | **7.6** | **7.1** | **8.6** | x 2.2 | x 2.0 | x 2.3 |
| accent-agent | **12.6** | **11.8** | **14.2** | x 1.3 | x 1.2 | x 1.4 |
| confirmed | **4.9** | **4.6** | **5.5** | 3.4 (3:1) | 3.0 (3:1) | 3.6 (3:1) |
| rejected | 3.0 (3:1) | x 2.8 | 3.4 (3:1) | **5.5** | **4.9** | **5.8** |
| signal | x 1.8 | x 1.7 | x 2.0 | **9.5** | **8.5** | **9.9** |
| ink-inverse | x | x | x | **17.2** | **15.3** | **18.0** |
| text-inverse | x | x | x | **12.7** | **11.4** | **13.3** |
| muted-inverse | x | x | x | **7.3** | **6.5** | **7.6** |
| code-text | x | x | x | **14.8** | **13.2** | **15.5** |

Chips (word on fill): ink-inverse on confirmed **5.0**, on standard **5.0**, on validation **7.8**, on agent **13.0**; ink on rejected **5.4**, on signal **9.2**. Sweep: at its brightest stop (#932667) ink-inverse **7.0**, text-inverse **5.2**, signal 3.9 (3:1), muted-inverse x 3.0. Through #420A68 (first 70%) every inverse role and signal is >= **5.4**.

## 4. Lightness (CIELAB L*)
Actors: agent **17.3**, validation **32.3**, standard **44.3** (steps of 15 and 12). Verdicts: confirmed **44.2**, rejected **57.7** (step of 13.6), and their chips have opposite polarity (light word on dark fill vs dark word on bright fill), so they still read apart in greyscale. Signal is **74.6**. The critical pairs are blue vs orange-red (Gemma blue vs DINOv3 crimson; confirmed teal vs rejected vermilion), not red vs green: under simulated deuteranopia/protanopia (Machado 2009) the smallest within-group difference is ΔE 17 (agent vs validation). One cross-group overlap: confirmed and standard share L* ≈ 44 (protan ΔE 10). They never mean the same thing and always carry their word.

## 5. Slide-type mapping (dark or statement every 4th slide: 1, 5, 9, 13)
- **Cover (1):** Inferno sweep, with the colorbar band as the one bright strip. Text goes in the left 60%.
- **Section/statement slides (if the designer adds any; max 2 sweeps in the deck):** Inferno sweep, ink-inverse headline, signal for the number.
- **Content (2 idea, 3 pipeline, 10 agent, 11 lessons, 12 next):** bg-light; cards on surface with an 8px accent top-border; panels in bg-alt.
- **Data/table (4 stack, 8 validation):** bg-light; table body on surface, header row bg-alt with ink, 2px rule lines; verdict column as confirmed chips.
- **Matplotlib-figure slides (6 standard, 7 iterations):** bg-light, figures on white plates (see 6).
- **Image-heavy satellite slides (5 testcase, 9 handcheck):** bg-dark, like an imagery viewer; actor names in ink-inverse, verdicts as chips.
- **Demo/closing (13):** bg-dark, commands in code-bg wells with a 2px rule-inverse border (code-bg is only 1.05:1 against bg-dark), "Questions?" in signal, colorbar band as the bookend.

## 6. Framing the figures
- **White matplotlib figures:** light slides only. Put each on a surface (#FFFFFF) plate with 16–24px padding, a 2px solid #C9CED5 border and a radius of 6px or less. The PNG's white blends into the plate, so the plate edge becomes the frame (plate vs bg-light is 1.13:1, so the border does the work). Never place a raw white PNG on bg-dark (18.9:1, it reads as a hole).
- **Satellite photos:** on bg-dark, no mat, a 2px #3B3550 hairline and a radius of 4px or less. On bg-light, no border. Overlay labels go in a code-bg (#0B0913) chip at 85–90% opacity with ink-inverse text, which matches the black date labels already burned into the chips.
- **Captions and credits:** muted (light) or muted-inverse (dark), 24px. Legend keys for figure colours use the figures' own colours: red outline #FF0000 (overview) / #FF2020 (chips), Gemma box #28E65A, always with the words ("red outline = finding").

## 7. Do / don't
1. **Do** keep actor colour-coding on light slides. On dark, name actors in ink-inverse: validation and agent fail as text on dark (2.2 and 1.3), and standard is 3:1 only.
2. **Do** render every verdict as a chip with its word: confirmed = #0A7570 fill + #F6F4EF word; rejected = #E8602A fill + #16131F word. Chips pass on every background, so no verdict is ever coloured running text.
3. **Do** use signal as text only on dark. On light it is a fill: an 8–12px marker bar under a big ink number, or a chip with ink text.
4. **Don't** frame or underline figures in standard, confirmed, rejected or any saturated colour. The figures' red and green outlines must be the only saturated lines on the plate.
5. **Don't** use actor accents for non-actor categories (for example storm vs control on slide 5). Use words, or a signal chip (storm = hot) vs a rule-inverse chip (control = calm).
6. **Don't** put text on the colorbar band or over the last 30% of the sweep.
7. **Don't** add hues. These 6 chromatic colours are the whole set. Opacity tints are allowed only for non-text fills and never on mats around imagery, since a tinted surround shifts how the satellite colours read.
