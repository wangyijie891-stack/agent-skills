# Original Figure Extraction Guide

## PyMuPDF crop workflow

```python
import fitz

doc = fitz.open("published-paper.pdf")
page = doc[2]  # zero-based page index
clip = fitz.Rect(x0, y0, x1, y1)
pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, alpha=False)
pix.save("assets/paper-fig2.png")
```

## Crop checks

1. Locate the figure or table with `page.get_text("blocks")` or `page.search_for("Figure N")`.
2. For two-column papers, confirm which column contains the figure before selecting coordinates.
3. Use `page.get_text("text", clip=clip)` to verify that the crop contains the intended figure, legend, axes, and table headers.
4. Render at 3–5× so labels remain readable in a projected presentation.
5. Keep the paper figure number in the filename, for example `paper-fig2-framework.png` or `paper-table1-results.png`.
6. Record the PDF SHA-256, page, coordinates, figure number, meaning, and image size in `original-figures-manifest.json`.

## Figure and table discipline

- Do not guess chart mappings from unordered text extraction. Use coordinates to match labels, legends, and values.
- Preserve table headers, units, and conditions such as Easy or Hard. If a table is wide, crop the complete original table instead of manually transcribing values that may become misaligned.
- If an original image is difficult to read, add explanatory text beside it; do not silently replace it with a redraw.
