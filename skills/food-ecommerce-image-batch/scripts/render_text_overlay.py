#!/usr/bin/env python3
"""Overlay exact Chinese-friendly ecommerce copy with macOS sips.

The helper uses the source as an unchanged visual background and adds only a
deterministic text layer. Inspect the image first and choose a layout and
placement that do not cover the package, food, or visual evidence.
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from _image_utils import PngValidationError, validate_png


THEMES = {
    "light": {
        "title": "#FFFFFF",
        "subline": "#FFFFFF",
        "border": "#1A120E",
        "shadow": "#000000",
        "accent": "#F2B45F",
    },
    "dark": {
        "title": "#3A2418",
        "subline": "#3A2418",
        "border": "#FFFFFF",
        "shadow": "#FFFFFF",
        "accent": "#A53D2B",
    },
    "warm": {
        "title": "#FFF1D2",
        "subline": "#FFF1D2",
        "border": "#3A1F12",
        "shadow": "#000000",
        "accent": "#E06A32",
    },
}


TYPE_STYLES = {
    "modern-bold": {
        "font_family": "PingFang SC, Hiragino Sans GB, STHeiti, sans-serif",
        "headline_weight": 800,
        "support_weight": 500,
        "kicker_weight": 650,
        "headline_spacing": "0.01em",
        "support_spacing": "0.02em",
    },
    "craft-brush": {
        "font_family": "Kaiti SC, STKaiti, KaiTi, serif",
        "headline_weight": 700,
        "support_weight": 500,
        "kicker_weight": 600,
        "headline_spacing": "0.05em",
        "support_spacing": "0.03em",
    },
    "premium-serif": {
        "font_family": "Songti SC, STSong, serif",
        "headline_weight": 600,
        "support_weight": 450,
        "kicker_weight": 550,
        "headline_spacing": "0.08em",
        "support_spacing": "0.04em",
    },
    "warm-handwritten": {
        "font_family": "Hannotate SC, Kaiti SC, STKaiti, sans-serif",
        "headline_weight": 700,
        "support_weight": 500,
        "kicker_weight": 600,
        "headline_spacing": "0.04em",
        "support_spacing": "0.03em",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Add exact short sales copy to a validated PNG without redrawing it."
    )
    parser.add_argument("input", type=Path, help="Input PNG")
    parser.add_argument("output", type=Path, help="Output PNG")
    parser.add_argument("--headline", required=True, help="Exact one-line headline")
    parser.add_argument("--subline", default="", help="Optional exact one-line subline")
    parser.add_argument(
        "--require-subline",
        action="store_true",
        help="Fail when --subline is empty; required for publishable main images",
    )
    parser.add_argument("--kicker", default="", help="Optional short eyebrow above the headline")
    parser.add_argument("--proof", default="", help="Optional short evidence note below the subline")
    parser.add_argument(
        "--placement",
        choices=("top-left", "top-right", "bottom-left", "bottom-right"),
        default="top-left",
    )
    parser.add_argument("--theme", choices=tuple(THEMES), default="light")
    parser.add_argument(
        "--layout",
        choices=("corner", "centered", "editorial"),
        default="corner",
        help="Text block structure; centered uses placement only for top/bottom",
    )
    parser.add_argument(
        "--type-style",
        choices=tuple(TYPE_STYLES),
        default="modern-bold",
        help="Product-positioning typography preset used consistently across a set",
    )
    parser.add_argument(
        "--font-family",
        default="",
        help="Optional installed CJK font family override; otherwise use --type-style",
    )
    parser.add_argument(
        "--margin-percent",
        type=float,
        default=6.0,
        help="Outer margin as percent of image width (default: 6)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file",
    )
    return parser.parse_args()


def fail(message: str) -> "NoReturn":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def image_info(path: Path) -> tuple[int, int, str]:
    if path.suffix.lower() != ".png":
        fail("input must be a normalized PNG; convert camera JPEGs with an EXIF-aware decoder first")
    width, height = validate_png(path)
    return width, height, "image/png"


def visual_units(text: str) -> float:
    units = 0.0
    for char in text:
        units += 1.0 if unicodedata.east_asian_width(char) in {"W", "F", "A"} else 0.56
    return max(units, 1.0)


def letter_spacing_em(value: str) -> float:
    try:
        return float(value.removesuffix("em"))
    except ValueError:
        return 0.0


def font_size(
    text: str,
    width: int,
    height: int,
    max_height_ratio: float,
    width_ratio: float,
    letter_spacing: str,
) -> int:
    units = visual_units(text)
    effective_units = units + max(units - 1.0, 0.0) * letter_spacing_em(letter_spacing)
    max_by_height = height * max_height_ratio
    max_by_width = width * width_ratio / effective_units
    return max(20, int(min(max_by_height, max_by_width)))


def ensure_line_fits(
    *,
    label: str,
    text: str,
    size: int,
    width: int,
    width_ratio: float,
    letter_spacing: str,
) -> None:
    spacing_em = letter_spacing_em(letter_spacing)
    units = visual_units(text)
    estimated_width = units * size + max(units - 1.0, 0.0) * size * spacing_em
    if estimated_width > width * width_ratio:
        fail(
            f"{label} cannot fit the selected {width_ratio:.0%} one-line safe zone; "
            "shorten the copy or choose --layout centered"
        )


def clean_text(value: str, label: str, maximum: int) -> str:
    value = value.strip()
    if not value:
        fail(f"{label} cannot be empty")
    if len(value) > maximum:
        fail(f"{label} is too long ({len(value)} characters; max {maximum})")
    for char in value:
        if unicodedata.category(char).startswith("C") or unicodedata.category(char) in {"Zl", "Zp"}:
            fail(f"{label} must be one line and cannot contain control characters")
    return value


def text_svg(
    *,
    text: str,
    x: int,
    y: int,
    anchor: str,
    size: int,
    weight: int,
    fill: str,
    border: str,
    shadow: str,
    stroke_width: float,
    opacity: float,
    letter_spacing: str,
) -> str:
    escaped = html.escape(text)
    common = (
        f'x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-size="{size}" font-weight="{weight}" '
        f'letter-spacing="{letter_spacing}"'
    )
    shadow_offset = max(1, round(size * 0.020))
    return (
        f'<text {common} transform="translate({shadow_offset} {shadow_offset})" '
        f'fill="{shadow}" fill-opacity="0.20">{escaped}</text>'
        f'<text {common} fill="{fill}" fill-opacity="{opacity:.2f}" '
        f'stroke="{border}" stroke-opacity="0.22" stroke-width="{stroke_width:.2f}" '
        f'paint-order="stroke fill">{escaped}</text>'
    )


def main() -> int:
    args = parse_args()
    source = args.input.expanduser().resolve()
    target = args.output.expanduser().resolve()
    if not source.is_file():
        fail(f"input does not exist: {source}")
    if source == target:
        fail("input and output must be different files")
    if target.suffix.lower() != ".png":
        fail("output must use the .png extension")
    if target.exists() and not args.overwrite:
        fail(f"output already exists; choose a versioned name or pass --overwrite: {target}")
    if not 5.0 <= args.margin_percent <= 8.0:
        fail("--margin-percent must be between 5 and 8")
    sips = shutil.which("sips")
    if not sips:
        fail("macOS sips is required; use another deterministic text compositor on this host")

    headline = clean_text(args.headline, "headline", 12)
    subline = args.subline.strip()
    if subline:
        subline = clean_text(subline, "subline", 24)
    elif args.require_subline:
        fail("subline cannot be empty when --require-subline is set")
    kicker = args.kicker.strip()
    if kicker:
        kicker = clean_text(kicker, "kicker", 16)
    proof = args.proof.strip()
    if proof:
        proof = clean_text(proof, "proof", 32)
    try:
        width, height, media_type = image_info(source)
    except (OSError, PngValidationError, ValueError) as exc:
        fail(f"cannot decode input image: {exc}")
    if width <= 0 or height <= 0:
        fail("image dimensions must be positive")

    margin = round(width * args.margin_percent / 100.0)
    style = TYPE_STYLES[args.type_style]
    width_ratio = 0.70 if args.layout == "centered" else 0.46
    title_size = font_size(
        headline, width, height, 0.075, width_ratio, style["headline_spacing"]
    )
    subline_size = (
        font_size(subline, width, height, 0.035, width_ratio, style["support_spacing"])
        if subline
        else 0
    )
    kicker_size = (
        font_size(kicker, width, height, 0.025, width_ratio, style["support_spacing"])
        if kicker
        else 0
    )
    proof_size = (
        font_size(proof, width, height, 0.025, width_ratio, style["support_spacing"])
        if proof
        else 0
    )
    lines = []
    if kicker:
        lines.append(("kicker", kicker, kicker_size))
    lines.append(("headline", headline, title_size))
    if subline:
        lines.append(("subline", subline, subline_size))
    if proof:
        lines.append(("proof", proof, proof_size))

    for label, value, size in lines:
        spacing = (
            style["headline_spacing"] if label == "headline" else style["support_spacing"]
        )
        ensure_line_fits(
            label=label,
            text=value,
            size=size,
            width=width,
            width_ratio=width_ratio,
            letter_spacing=spacing,
        )

    line_heights = [round(size * 1.18) for _, _, size in lines]
    gaps = []
    for label, _, _ in lines[:-1]:
        gaps.append(round(height * (0.010 if label in {"kicker", "subline"} else 0.016)))
    accent_space = round(height * 0.020) if args.layout == "editorial" else 0
    block_height = accent_space + sum(line_heights) + sum(gaps)
    if block_height > height - 2 * margin:
        fail("text block cannot fit between the selected top and bottom safety margins")
    block_top = margin if args.placement.startswith("top") else height - margin - block_height
    left_side = args.placement.endswith("left")
    if args.layout == "centered":
        x = width // 2
        anchor = "middle"
    else:
        x = margin if left_side else width - margin
        anchor = "start" if left_side else "end"
    theme = THEMES[args.theme]
    selected_family = args.font_family.strip() or style["font_family"]
    font_family = html.escape(selected_family, quote=True)
    stroke_width = max(0.8, min(width, height) * 0.0011)

    text_layers = []
    if args.layout == "editorial":
        rule_width = round(width * 0.085)
        rule_y = block_top + round(accent_space * 0.30)
        rule_x1 = x if anchor == "start" else x - rule_width
        rule_x2 = x + rule_width if anchor == "start" else x
        text_layers.append(
            f'<line x1="{rule_x1}" y1="{rule_y}" x2="{rule_x2}" y2="{rule_y}" '
            f'stroke="{theme["accent"]}" stroke-width="{max(3, round(height * 0.005))}" '
            'stroke-linecap="round"/>'
        )

    cursor = block_top + accent_space
    for index, (label, value, size) in enumerate(lines):
        baseline = cursor + size
        is_headline = label == "headline"
        is_kicker = label == "kicker"
        weight = (
            style["headline_weight"]
            if is_headline
            else style["kicker_weight"]
            if is_kicker
            else style["support_weight"]
        )
        fill = theme["accent"] if is_kicker else theme["title"] if is_headline else theme["subline"]
        text_layers.append(
            text_svg(
                text=value,
                x=x,
                y=baseline,
                anchor=anchor,
                size=size,
                weight=weight,
                fill=fill,
                border=theme["border"],
                shadow=theme["shadow"],
                stroke_width=stroke_width if is_headline else max(0.6, stroke_width * 0.52),
                opacity=1.0 if is_headline else 0.94,
                letter_spacing=(
                    style["headline_spacing"] if is_headline else style["support_spacing"]
                ),
            )
        )
        cursor += line_heights[index]
        if index < len(gaps):
            cursor += gaps[index]

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".food-ecom-copy-", dir=target.parent) as temp_dir:
        temp = Path(temp_dir)
        image_data = base64.b64encode(source.read_bytes()).decode("ascii")
        svg = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<image width="{width}" height="{height}" preserveAspectRatio="none" '
            f'href="data:{media_type};base64,{image_data}"/>'
            f'<g font-family="{font_family}">{"".join(text_layers)}</g>'
            '</svg>'
        )
        svg_path = temp / "composite.svg"
        candidate = temp / "candidate.png"
        svg_path.write_text(svg, encoding="utf-8")
        result = subprocess.run(
            [sips, "-s", "format", "png", str(svg_path), "--out", str(candidate)],
            check=False,
            capture_output=True,
        )
        if result.returncode or not candidate.is_file():
            detail = (result.stderr or result.stdout).decode("utf-8", errors="replace").strip()
            fail(detail or "sips failed")
        try:
            candidate_width, candidate_height = validate_png(candidate)
        except PngValidationError as exc:
            fail(f"rendered output is not a valid PNG: {exc}")
        if (candidate_width, candidate_height) != (width, height):
            fail(
                f"rendered dimensions {candidate_width}x{candidate_height} do not match "
                f"source dimensions {width}x{height}"
            )
        os.replace(candidate, target)

    print(f"wrote: {target}")
    copy_parts = [part for part in (kicker, headline, subline, proof) if part]
    print(f"copy: {' / '.join(copy_parts)}")
    print(f"layout: {args.layout}; type-style: {args.type_style}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
