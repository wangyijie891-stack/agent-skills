---
name: paper-ppt
description: Create academic paper-reading PPTs in any language requested by the user, for research papers from any field, using original paper figures, a restrained deep-blue template, detailed method and experiment explanations, speaker notes, and layout validation.
---

# Paper PPT

This skill turns a published academic paper into a compact, visual PPT for oral reporting in the language requested by the user. It is language-agnostic and field-agnostic: use it for any written or spoken language and for robotics, embodied AI, machine learning, computer vision, NLP, systems, or other empirical research papers. Adapt the method and metric explanations to the paper rather than forcing domain-specific terminology.

## Non-negotiable output rules

- Prefer the final published PDF and record venue, DOI, version, and page/figure/table references. If the user asks to avoid preprints, do not use an arXiv-only version when a proceedings or journal PDF exists.
- Use the paper's original figures and tables whenever they are available. Crop only the figure or table region from the PDF; do not replace an available original with a hand-drawn schematic. Editorial redraws are allowed only for relationships that the paper does not provide as figures, and must be labelled `Redrawn for this presentation`.
- Do not place surrounding body text, neighboring columns, or unrelated captions inside an image crop. Keep a crop manifest with the source PDF hash, page, coordinates, and meaning.
- Use the lightweight template specification in `assets/template-spec.md` together with `references/style-guide.md` as the visual reference. Keep the slide canvas 16:9, use a light gray background, dark navy headings, restrained blue accents, rectangular information blocks, and no decorative visual clutter. The template is a style reference, not a restriction on scientific content.
- Choose a font that supports the requested language and script. Microsoft YaHei remains the default for Chinese decks; for other scripts, choose an installed font with complete glyph coverage instead of allowing missing-glyph boxes. Keep the paper title prominent at the top-left of the first slide and place the subtitle or translation beneath it in the requested language when useful.
- Every slide gets fluent speaker notes in the requested language or language mix. Notes must explain the story represented by the figure before interpreting numbers; avoid positional phrases such as “left”, “right”, or “second figure” when the structure can be described by content.
- No text or image may cross the slide boundary. Keep tables readable and never squeeze a complete table into an unreadable thumbnail.

## Default four-slide story

Use this structure unless the user requests another page count:

1. **Problem and research question** — full paper title, concrete failure case or research gap, what prior systems miss, and the paper's central question or contribution.
2. **Method and training/inference modules** — one original framework figure, inputs → transformations → decisions → outputs or feedback, equations or labels needed to understand the method, and the training procedure when learning is involved.
3. **Experiment setup and core results** — original dataset, scene, or setup figure plus an original result table or chart; name baselines, data split or run count, metrics, denominators, and what each metric means.
4. **Mechanism evidence, ablations, and boundaries** — original qualitative comparison or ablation figure and table; connect results to the claimed mechanism, then state limitations and research directions.

For a three-page request, merge pages 1 and 4. For six or nine pages, expand each module while preserving the same narrative order.

## Language selection

Language is never fixed by this skill. Follow an explicit user request for one language, multiple languages, translation, or bilingual output. If no language is specified, use the language of the user's latest request. If the request is genuinely ambiguous, ask once before drafting. Keep technical names, equations, variable names, and quoted paper text when they improve fidelity, but explain surrounding content in the selected language. Apply the same language choice to headings, diagrams, captions, alt text, tables, and speaker notes.

## Working procedure

1. Confirm the paper identity and obtain the full published PDF. Read the abstract, introduction, overview figures, method, training or data construction, experiments, captions, tables, ablations, and conclusion. Do not infer missing numbers from an abstract.
2. Extract original figures and tables with `scripts/extract_original_figures.py` or the PyMuPDF recipe in `references/figure-extraction.md`. Use a 3–5× render scale, verify the crop text, and write `assets/original-figures-manifest.json`.
3. Draft the slide story from the evidence: problem → mechanism → experiment → mechanism evidence and limitations. Keep claims narrower than the paper's actual evaluation scope.
4. Build the deck with the reference template or an equivalent `python-pptx` script. Use `references/style-guide.md` for spacing, colors, type scale, font coverage, and safe image placement.
5. Add speaker notes from `references/notes-template.md`. Include a short interpretation of every key metric, including whether higher or lower is better and what the denominator is.
6. Run `scripts/validate_ppt.py` and `unzip -t` on the final PPTX. If LibreOffice rendering is available, export PDF or PNG and inspect every slide visually. If rendering is blocked by the runtime, report that only structural checks were completed; do not claim visual QA passed.

## Evidence discipline

Distinguish in both slide text and notes:

- **Paper statement**: what the authors define or claim;
- **Observed result**: the number, table, curve, or qualitative outcome actually reported;
- **Presentation interpretation**: the narrower interpretation supported by that evidence.

Do not turn a simulated metric into a general real-world guarantee. State whether a result is simulation, real robot, zero-shot transfer, ablation, or whole-system comparison.

## Supporting resources

- Read `references/style-guide.md` when creating or modifying the deck layout.
- Read `references/figure-extraction.md` when a published PDF must be cropped.
- Read `references/notes-template.md` before writing speaker notes.
- Use `scripts/extract_original_figures.py` for repeatable crops and `scripts/validate_ppt.py` for structural checks.
- `assets/template-spec.md` is a lightweight visual reference, not a source of paper evidence.
