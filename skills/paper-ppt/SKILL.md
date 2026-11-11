---
name: paper-ppt
description: Create Chinese academic paper-reading PPTs for research papers from any field, using original paper figures, a restrained deep-blue template, detailed method/experiment explanations, speaker notes, and layout validation.
---

# Paper PPT

This skill turns a published academic paper into a compact, visual PPT for Chinese oral reporting. It is field-agnostic: use it for robotics, embodied AI, machine learning, computer vision, NLP, systems, or other empirical research papers. Adapt the method and metric explanations to the paper rather than forcing an embodied-safety vocabulary.

## Non-negotiable output rules

- Prefer the final published PDF and record venue, DOI, version, and page/figure/table references. If the user says “不要预印本”, do not use an arXiv-only version when a proceedings/journal PDF exists.
- Use the paper's original figures and tables whenever they are available. Crop only the figure/table region from the PDF; do not replace an available original with a hand-drawn schematic. Editorial redraws are allowed only for a relationship that the paper does not provide as a figure, and must be labelled `本文重绘`.
- Do not place surrounding body text, neighboring columns, or unrelated captions inside an image crop. Keep a crop manifest with source PDF hash, page, coordinates, and meaning.
- Use the lightweight template specification in `assets/template-spec.md` together with `references/style-guide.md` as the visual reference. Keep the slide canvas 16:9, light gray background, dark navy headings, restrained blue accents, rectangular information blocks, and no decorative visual clutter. The template is a style reference, not a restriction on scientific content.
- All editable slide text uses Microsoft YaHei / 微软雅黑. Keep the paper title prominent at the top-left of the first slide; put the Chinese subtitle or translation beneath it in a smaller size.
- Every slide gets fluent Chinese speaker notes. Notes must explain the story represented by the figure before interpreting numbers; avoid phrases such as “左侧/右侧/第二幅图” when the structure can be described by content.
- No text or image may cross the slide boundary. Keep tables readable and never squeeze a complete table into a tiny unreadable thumbnail.

## Default four-slide story

Use this structure unless the user requests another page count:

1. **痛点与问题定义** — full English title + Chinese title, concrete failure case or research gap, what prior systems miss, and the paper's central question/contribution.
2. **方法与训练/推理模块** — one original framework figure, inputs → transformations → decisions → outputs/feedback, equations or labels needed to understand the method, and the training procedure if learning is involved.
3. **实验设置与核心结果** — original dataset/scene/setup figure plus original result table/chart; name baselines, data split or run count, metrics, denominators, and what each metric means.
4. **机制证据、消融与边界** — original qualitative comparison/ablation figure and table; connect the result to the claimed mechanism, then state limitations and research direction.

For a three-page request, merge pages 1 and 4. For six or nine pages, expand each module while preserving the same narrative order.

## Working procedure

1. Confirm the paper identity and obtain the full published PDF. Read abstract, introduction, overview figures, method, training/data construction, experiments, captions, tables, ablations, and conclusion. Do not infer missing numbers from an abstract.
2. Extract the original figures/tables with `scripts/extract_original_figures.py` or the PyMuPDF recipe in `references/figure-extraction.md`. Use a 3–5× render scale, verify the crop text, and write `assets/original-figures-manifest.json`.
3. Draft the slide story from the evidence: problem → mechanism → experiment → mechanism evidence/limitations. Keep claims narrower than the paper's actual evaluation scope.
4. Build the deck with the reference template or an equivalent `python-pptx` script. Use `references/style-guide.md` for spacing, colors, type scale, and safe image placement.
5. Add speaker notes from `references/notes-template.md`. Include a short interpretation of every key metric (for example, whether higher or lower is better and what the denominator is).
6. Run `scripts/validate_ppt.py` and `unzip -t` on the final PPTX. If LibreOffice rendering is available, export PDF/PNG and inspect every slide visually. If rendering is blocked by the runtime, report that only structural checks were completed; do not claim visual QA passed.

## Evidence discipline

Distinguish in both slide text and notes:

- **论文陈述**: what the authors define or claim;
- **观测结果**: the number, table, curve, or qualitative outcome actually reported;
- **汇报解读**: the narrower interpretation supported by that evidence.

Do not turn a simulated collision metric into a general physical-safety guarantee. State whether a result is simulation, real robot, zero-shot transfer, ablation, or whole-system comparison.

## Supporting resources

- Read `references/style-guide.md` when creating or modifying the deck layout.
- Read `references/figure-extraction.md` when a published PDF must be cropped.
- Read `references/notes-template.md` before writing speaker notes.
- Use `scripts/extract_original_figures.py` for repeatable crops and `scripts/validate_ppt.py` for structural checks.
- `assets/deep-blue-paper-ppt-reference.pptx` is a visual reference, not a source of paper evidence.
