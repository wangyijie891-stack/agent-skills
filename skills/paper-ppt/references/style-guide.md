# Deep-Blue Academic PPT Style Guide

## Canvas and colors

- Canvas: 16:9, 13.333 × 7.5 inches.
- Background: `#F3F5F7`.
- Main heading: `#12395B`; accent blue: `#1B5A85`; body text: `#263F57`; secondary text: `#647789`; border: `#C9D3DC`; pale blue fill: `#EAF1F6`.
- Avoid large gradients, heavy shadows, decorative illustrations, colorful bars, or icons without information value.
- Use rectangular information blocks by default. Use large rounded cards only when the user explicitly requests them.

## Type hierarchy

- Full paper title on slide 1: 16–20 pt, navy, bold.
- Localized title or subtitle: 20–24 pt when it is the main title, navy, bold.
- Regular slide title: 20–22 pt, navy, bold.
- Section heading: 12–14 pt, navy, bold.
- Body text: 10.5–12 pt; table notes: 8.5–10 pt; header metadata: 9–11 pt.
- Use a font with complete glyph coverage for the requested language. Microsoft YaHei is the default for Chinese; other scripts require an appropriate installed font. Keep font hierarchy and weight consistent across the deck.

## Layout constraints

- Reserve about 0.2–0.85 inches for the top header and start the main title near 1.0 inches. Keep at least 0.35 inches of bottom safe area.
- Use no more than two or three information zones per slide. Each zone should answer one question.
- Use contain-style placement for original figures. Do not stretch or crop axes, legends, table headers, or key annotations.
- Put one visible explanatory sentence beside every original figure. The sentence must tell the audience what to inspect and why it matters.
- When figures and text share a slide, give the figure enough area first and compress decoration before shrinking explanatory text.
- For long formulas, long table headers, or many metrics, split the content or use the original table crop instead of allowing overflow.

## Original-figure labels

- Label a native crop as `Original Figure N` or `Original Table N`.
- Label a redraw as `Redrawn for this presentation · Original Figure N` so it is never mistaken for the paper figure.
- Do not include two-column body text or neighboring-column content inside a figure crop. If the caption cannot be separated, retain the caption but exclude surrounding paragraphs.

## Speaker-note structure

Organize notes as: problem → figure evidence → method or metric → conclusion → boundary.

Avoid positional phrases such as “look left”, “look right”, or “second figure”. Use content-based names such as “task translation pipeline”, “risk prediction module”, or “hard real-robot setting”.
