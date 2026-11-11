#!/usr/bin/env python3
"""Structural QA for a paper-reading PPTX."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx", type=Path)
    ap.add_argument("--font", default="Microsoft YaHei")
    ap.add_argument("--min-original-images", type=int, default=1)
    args = ap.parse_args()
    with zipfile.ZipFile(args.pptx) as zf:
        bad = zf.testzip()
        if bad:
            raise SystemExit(f"corrupt ZIP member: {bad}")
    prs = Presentation(args.pptx)
    if not prs.slides:
        raise SystemExit("PPTX contains no slides")
    errors = []
    for i, slide in enumerate(prs.slides, 1):
        pictures = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE]
        if len(pictures) < args.min_original_images:
            errors.append(f"slide {i}: only {len(pictures)} picture(s)")
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if not notes:
            errors.append(f"slide {i}: missing speaker notes")
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0:
                errors.append(f"slide {i}: negative shape position: {shape.name}")
            if shape.left + shape.width > prs.slide_width + 2:
                errors.append(f"slide {i}: horizontal overflow: {shape.name}")
            if shape.top + shape.height > prs.slide_height + 2:
                errors.append(f"slide {i}: vertical overflow: {shape.name}")
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.font.name and args.font.lower() not in run.font.name.lower():
                            errors.append(f"slide {i}: font {run.font.name!r} in {shape.name}")
    if errors:
        print("FAIL")
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(prs.slides)} slides, notes present, picture count and bounds valid")


if __name__ == "__main__":
    main()
