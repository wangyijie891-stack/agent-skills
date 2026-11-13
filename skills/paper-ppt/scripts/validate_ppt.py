#!/usr/bin/env python3
"""Validate a paper-reading PPTX without imposing a fixed page count.

The first slide may be text-only. If original figure provenance is supplied,
the validator checks the crop manifest, image hashes, crop captions, and
original-image markers instead of merely counting picture shapes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

CAPTION_RE = re.compile(r"\b(?:figure|fig\.|table)\s+\d+\s*:", re.IGNORECASE)


class ValidationFailure(Exception):
    """A user-facing validation error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_manifest(pptx: Path, explicit: Path | None) -> Path | None:
    if explicit:
        return explicit
    candidates = [
        pptx.parent / "assets" / "original-figures-manifest.json",
        pptx.parent / "original-figures-manifest.json",
    ]
    return next((p for p in candidates if p.exists()), None)


def load_manifest(path: Path | None) -> tuple[dict | None, list[str]]:
    if path is None:
        return None, []
    if not path.exists():
        raise ValidationFailure(f"manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationFailure(f"invalid manifest JSON: {path} ({exc.msg})") from None
    assets = data.get("assets")
    if not isinstance(assets, list):
        raise ValidationFailure("manifest must contain an 'assets' list")
    errors: list[str] = []
    for index, asset in enumerate(assets, 1):
        if not isinstance(asset, dict) or not asset.get("file"):
            errors.append(f"manifest asset {index}: missing file")
            continue
        clip_text = str(asset.get("clip_text", ""))
        if CAPTION_RE.search(clip_text) and not asset.get("allow_caption", False):
            errors.append(
                f"manifest asset {asset['file']}: caption text detected in crop; "
                "use a tighter crop or set allow_caption=true with justification"
            )
        ratio = asset.get("clip_area_ratio")
        if isinstance(ratio, (int, float)) and ratio > 0.85:
            errors.append(
                f"manifest asset {asset['file']}: crop covers {ratio:.1%} of the page; "
                "a full-page crop is not accepted"
            )
    return data, errors


def font_declarations(run) -> tuple[str | None, str | None]:
    """Return exact latin and East Asian typefaces from the run XML."""
    rpr = run._r.find(qn("a:rPr"))
    if rpr is None:
        return None, None
    latin = rpr.find(qn("a:latin"))
    east_asian = rpr.find(qn("a:ea"))
    return (
        latin.get("typeface") if latin is not None else None,
        east_asian.get("typeface") if east_asian is not None else None,
    )


def parse_slide_list(value: str | None) -> set[int]:
    if not value:
        return set()
    result: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item.isdigit() or int(item) < 1:
            raise ValidationFailure(f"invalid slide list item: {item!r}")
        result.add(int(item))
    return result


def validate(args: argparse.Namespace) -> list[str]:
    pptx = args.pptx
    if not pptx.exists():
        raise ValidationFailure(f"PPTX file not found: {pptx}")
    try:
        with zipfile.ZipFile(pptx) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise ValidationFailure(f"corrupt PPTX archive member: {bad_member}")
    except zipfile.BadZipFile:
        raise ValidationFailure(f"not a valid PPTX ZIP archive: {pptx}") from None
    try:
        prs = Presentation(pptx)
    except Exception as exc:
        raise ValidationFailure(f"cannot open PPTX: {exc}") from None
    if len(prs.slides) < args.min_slides:
        raise ValidationFailure(
            f"PPTX has {len(prs.slides)} slide(s); at least {args.min_slides} required"
        )

    ratio = prs.slide_width / prs.slide_height
    expected = 16 / 9
    if abs(ratio - expected) > args.aspect_tolerance:
        raise ValidationFailure(
            f"slide canvas is {ratio:.4f}:1, expected 16:9 within ±{args.aspect_tolerance:.3f}"
        )

    manifest_path = find_manifest(pptx, args.manifest)
    manifest, manifest_errors = load_manifest(manifest_path)
    errors = list(manifest_errors)
    warnings: list[str] = []
    if manifest is None and args.require_original_slides:
        errors.append("original-figure validation requested but no manifest was found")
    assets_by_file = {}
    if manifest:
        for asset in manifest.get("assets", []):
            if isinstance(asset, dict) and asset.get("file"):
                assets_by_file[Path(asset["file"]).name] = asset
                image_path = (manifest_path.parent / asset["file"]).resolve()
                if not image_path.exists():
                    errors.append(f"manifest image file not found: {image_path}")
                elif asset.get("sha256"):
                    actual = sha256_bytes(image_path.read_bytes())
                    if actual != asset["sha256"]:
                        errors.append(f"manifest hash mismatch: {asset['file']}")

    required_original_slides = parse_slide_list(args.require_original_slides)
    for slide_index, slide in enumerate(prs.slides, 1):
        pictures = [s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.PICTURE]
        validated_originals = 0
        for picture in pictures:
            marker = picture.name.removeprefix("ORIGINAL:").strip() if picture.name.startswith("ORIGINAL:") else None
            if picture.name.startswith("DECORATIVE:"):
                continue
            blob_hash = sha256_bytes(picture.image.blob)
            matching_asset = None
            if assets_by_file:
                matching_asset = next(
                    (asset for asset in assets_by_file.values() if asset.get("sha256") == blob_hash),
                    None,
                )
            if matching_asset is None and marker:
                matching_asset = assets_by_file.get(Path(marker + ".png").name) or assets_by_file.get(Path(marker).name)
            if manifest and args.strict_original and matching_asset is None:
                errors.append(
                    f"slide {slide_index}: picture {picture.name!r} is not linked to a manifest asset"
                )
            elif manifest and matching_asset is not None:
                validated_originals += 1
            elif not manifest:
                warnings.append(
                    f"slide {slide_index}: picture {picture.name!r} has no provenance manifest"
                )

        if slide_index in required_original_slides and validated_originals == 0:
            errors.append(f"slide {slide_index}: no validated original figure/table")

        notes = slide.notes_slide.notes_text_frame.text.strip()
        if args.require_notes and not notes:
            errors.append(f"slide {slide_index}: missing speaker notes")
        for shape in slide.shapes:
            if shape.left < 0 or shape.top < 0:
                errors.append(f"slide {slide_index}: negative shape position: {shape.name}")
            if shape.left + shape.width > prs.slide_width + 2:
                errors.append(f"slide {slide_index}: horizontal overflow: {shape.name}")
            if shape.top + shape.height > prs.slide_height + 2:
                errors.append(f"slide {slide_index}: vertical overflow: {shape.name}")
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if not run.text.strip():
                            continue
                        latin, east_asian = font_declarations(run)
                        if not latin and not east_asian:
                            errors.append(f"slide {slide_index}: missing explicit font in {shape.name}")
                        if args.font and args.font not in {latin, east_asian}:
                            errors.append(
                                f"slide {slide_index}: font mismatch in {shape.name}; "
                                f"expected exact {args.font!r}, got latin={latin!r}, ea={east_asian!r}"
                            )
    if warnings and args.fail_on_warning:
        errors.extend(warnings)
    if errors:
        print("FAIL")
        for message in errors:
            print(f"- {message}")
        if warnings and not args.fail_on_warning:
            print("WARNINGS")
            for message in warnings:
                print(f"- {message}")
        return 1
    print(f"PASS: {len(prs.slides)} adaptive slides, notes and bounds valid")
    if warnings:
        print("WARNINGS")
        for message in warnings:
            print(f"- {message}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--font", default=None, help="exact font name expected in latin or ea declarations")
    parser.add_argument("--min-slides", type=int, default=2)
    parser.add_argument("--aspect-tolerance", type=float, default=0.02)
    parser.add_argument("--require-original-slides", default=None, help="comma-separated slide numbers, e.g. 2,3,4")
    parser.add_argument("--strict-original", action="store_true", help="reject pictures not linked to the manifest")
    parser.add_argument("--require-notes", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args()
    try:
        return validate(args)
    except ValidationFailure as exc:
        print(f"FAIL: {exc}")
        return 1
    except OSError as exc:
        print(f"FAIL: file system error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
