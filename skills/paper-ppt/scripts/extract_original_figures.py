#!/usr/bin/env python3
"""Repeatably crop original figures/tables from a published PDF.

Example:
  python extract_original_figures.py --pdf paper.pdf --out-dir assets \
    --crop fig2=3,54,54,558,297 --crop table1=5,130,53,482,143
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz


def parse_crop(value: str):
    name, raw = value.split("=", 1)
    parts = raw.split(",")
    if len(parts) != 5:
        raise ValueError(f"crop must be name=page,x0,y0,x1,y1: {value}")
    page, x0, y0, x1, y1 = parts
    return name, int(page), tuple(float(x) for x in (x0, y0, x1, y1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--scale", type=float, default=4.0)
    ap.add_argument("--crop", action="append", required=True,
                    help="name=1-based-page,x0,y0,x1,y1; repeat for each crop")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(args.pdf)
    manifest = {
        "pdf": str(args.pdf),
        "sha256": hashlib.sha256(args.pdf.read_bytes()).hexdigest(),
        "scale": args.scale,
        "assets": [],
    }
    for raw in args.crop:
        name, page_no, box = parse_crop(raw)
        page = doc[page_no - 1]
        clip = fitz.Rect(box)
        output = args.out_dir / f"{name}.png"
        pix = page.get_pixmap(matrix=fitz.Matrix(args.scale, args.scale), clip=clip, alpha=False)
        pix.save(output)
        manifest["assets"].append({
            "file": output.name,
            "page": page_no,
            "bbox": list(box),
            "size": [pix.width, pix.height],
            "clip_text": page.get_text("text", clip=clip),
        })
    (args.out_dir / "original-figures-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Extracted {len(manifest['assets'])} crops to {args.out_dir}")


if __name__ == "__main__":
    main()
