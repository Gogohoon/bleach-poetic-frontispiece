#!/usr/bin/env python3
"""Normalize an approved generated chapter page to the skill's exact PNG contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

TARGET_SIZE = (1168, 1702)
TARGET_RATIO = 584 / 851
PAPER_WHITE = (255, 255, 255)
INK = 32
HALFTONE_GREY = 181


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Visually approved generated image")
    parser.add_argument("--output", required=True, type=Path, help="Final .png path")
    parser.add_argument(
        "--max-ratio-error",
        type=float,
        default=0.01,
        help="Maximum allowed absolute source-ratio error (default: 0.01)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing output")
    return parser.parse_args()


def open_on_white(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(f"Input image not found: {path}")
    with Image.open(path) as source:
        rgba = source.convert("RGBA")
    paper = Image.new("RGBA", rgba.size, (*PAPER_WHITE, 255))
    paper.alpha_composite(rgba)
    return paper.convert("RGB")


def contain_on_paper(source: Image.Image) -> Image.Image:
    resized = ImageOps.contain(source, TARGET_SIZE, method=Image.Resampling.LANCZOS)
    page = Image.new("RGB", TARGET_SIZE, PAPER_WHITE)
    offset = ((TARGET_SIZE[0] - resized.width) // 2, (TARGET_SIZE[1] - resized.height) // 2)
    page.paste(resized, offset)
    return page


def quantize_to_three_tones(source: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(source)
    lookup = [INK if value < 112 else HALFTONE_GREY if value < 210 else 255 for value in range(256)]
    tones = grayscale.point(lookup, mode="L")
    return Image.merge("RGB", (tones, tones, tones))


def main() -> None:
    args = parse_args()
    if args.max_ratio_error <= 0:
        raise ValueError("--max-ratio-error must be positive")
    if args.output.suffix.lower() != ".png":
        raise ValueError("Output must use the .png extension")
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"Output already exists: {args.output}; use --overwrite to replace it")

    source = open_on_white(args.input)
    source_ratio = source.width / source.height
    ratio_error = abs(source_ratio - TARGET_RATIO)
    if ratio_error > args.max_ratio_error:
        raise ValueError(
            f"Source ratio {source_ratio:.6f} differs from {TARGET_RATIO:.6f} by {ratio_error:.6f}; regenerate it."
        )

    normalized = quantize_to_three_tones(contain_on_paper(source))
    if normalized.size != TARGET_SIZE:
        raise AssertionError(f"Unexpected normalized size: {normalized.size}")
    if not set(normalized.get_flattened_data()).issubset({PAPER_WHITE, (INK, INK, INK), (HALFTONE_GREY,) * 3}):
        raise AssertionError("Palette normalization failed")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    normalized.save(args.output, format="PNG", optimize=True)
    print(
        f"Wrote {args.output} | size={TARGET_SIZE[0]}x{TARGET_SIZE[1]} "
        f"| ratio_error={ratio_error:.6f} | palette=#FFFFFF,#202020,#B5B5B5"
    )


if __name__ == "__main__":
    main()
