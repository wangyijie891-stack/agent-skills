# 论文原生图裁取规范

## PyMuPDF 裁图流程

```python
import fitz

doc = fitz.open("published-paper.pdf")
page = doc[2]  # 0-based page index
clip = fitz.Rect(x0, y0, x1, y1)
pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), clip=clip, alpha=False)
pix.save("assets/paper-fig2.png")
```

## 裁剪前后检查

1. 先用 `page.get_text("blocks")` 或 `page.search_for("Figure N")` 定位图和表。
2. 两栏论文要确认图属于哪一栏，避免把邻栏正文放入图片。
3. 用 `page.get_text("text", clip=clip)` 检查裁剪区是否包含目标图、图例、坐标轴和表头。
4. 以 3–5× 渲染，保证投影时图中文字仍可读。
5. 图像文件名保留图号，例如 `paper-fig2-framework.png`、`paper-table1-results.png`。
6. 记录 PDF SHA-256、页码、PDF 坐标、图号、含义和尺寸到 `original-figures-manifest.json`。

## 图表纪律

- 不根据文本提取结果猜柱状图/曲线映射；必要时用坐标核对图例和数值。
- 表格必须保留表头、单位和 Easy/Hard 等条件；若整表太宽，裁取完整原表，不要手工抄成可能错位的简表。
- 若原图不可读，允许在旁边增加内容性文字解释，但不要用重绘图悄悄替换原图。
