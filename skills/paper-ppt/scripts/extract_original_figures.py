#!/usr/bin/env python3
"""Extract verified original figures and tables from a published PDF.

Example:
  python extract_original_figures.py --pdf paper.pdf --out-dir assets \
    --crop fig2=3,54,54,558,297 --crop table1=5,130,53,482,143
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError as exc:  # pragma: no cover - handled as a friendly CLI error
    fitz = None
    FITZ_IMPORT_ERROR = str(exc)
else:
    FITZ_IMPORT_ERROR = None

CAPTION_RE = re.compile(r"\b(?:figure|fig\.|table)\s+\d+\s*:", re.IGNORECASE)


def parse_crop(value: str):
    if "=" not in value:
        raise ValueError(f"invalid crop {value!r}; expected name=page,x0,y0,x1,y1")
    name, raw = value.split("=", 1)
    if not name.strip():
        raise ValueError("crop name cannot be empty")
    parts = raw.split(",")
    if len(parts) != 5:
        raise ValueError(f"invalid crop {value!r}; expected name=page,x0,y0,x1,y1")
    try:
        page = int(parts[0])
        box = tuple(float(x) for x in parts[1:])
    except ValueError as exc:
        raise ValueError(f"crop {value!r} contains a non-numeric page or coordinate") from exc
    if not all(math.isfinite(x) for x in box):
        raise ValueError(f"crop {value!r} contains a non-finite coordinate")
    return name.strip(), page, box


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--scale", type=float, default=4.0)
    parser.add_argument("--crop", action="append", required=True,
                        help="name=1-based-page,x0,y0,x1,y1; repeat for each crop")
    parser.add_argument("--allow-caption", action="store_true",
                        help="allow a caption-like text block inside a crop")
    args = parser.parse_args()
    try:
        if fitz is None:
            raise ValueError(
                "PyMuPDF is not installed; install the 'pymupdf' package before extracting figures"
            )
        if not args.pdf.exists():
            raise ValueError(f"PDF file not found: {args.pdf}")
        if args.scale <= 0 or not math.isfinite(args.scale):
            raise ValueError("--scale must be a positive finite number")
        crops = [parse_crop(raw) for raw in args.crop]
        args.out_dir.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(args.pdf)
        manifest = {
            "version": 2,
            "pdf": str(args.pdf),
            "pdf_sha256": sha256_file(args.pdf),
            "scale": args.scale,
            "assets": [],
        }
        for name, page_no, box in crops:
            if page_no < 1 or page_no > len(doc):
                raise ValueError(f"crop {name!r}: page {page_no} is outside the PDF range 1-{len(doc)}")
            page = doc[page_no - 1]
            page_rect = page.rect
            clip = fitz.Rect(box)
            if clip.x0 < page_rect.x0 or clip.y0 < page_rect.y0 or clip.x1 > page_rect.x1 or clip.y1 > page_rect.y1:
                raise ValueError(
                    f"crop {name!r}: coordinates {box} exceed page bounds "
                    f"(0, 0, {page_rect.width:.1f}, {page_rect.height:.1f})"
                )
            if clip.width <= 0 or clip.height <= 0:
                raise ValueError(f"crop {name!r}: crop width and height must be positive")
            area_ratio = (clip.width * clip.height) / (page_rect.width * page_rect.height)
            if area_ratio > 0.85:
                raise ValueError(
                    f"crop {name!r}: crop covers {area_ratio:.1%} of the page; "
                    "select the figure/table region instead of the full page"
                )
            clip_text = page.get_text("text", clip=clip)
            caption_in_crop = bool(CAPTION_RE.search(clip_text))
            if caption_in_crop and not args.allow_caption:
                raise ValueError(
                    f"crop {name!r}: caption-like text detected; tighten the crop or rerun with --allow-caption"
                )
            output = args.out_dir / f"{name}.png"
            pix = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), clip=clip, alpha=False)
            pix.save(output)
            manifest["assets"].append({
                "file": output.name,
                "sha256": sha256_file(output),
                "page": page_no,
                "bbox": list(box),
                "page_size": [page_rect.width, page_rect.height],
                "clip_area_ratio": area_ratio,
                "size": [pix.width, pix.height],
                "caption_in_crop": caption_in_crop,
                "allow_caption": bool(args.allow_caption),
                "clip_text": clip_text,
            })
        (args.out_dir / "original-figures-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Extracted {len(manifest['assets'])} verified crop(s) to {args.out_dir}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
