#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_size(value: str) -> tuple[int, int]:
    width, height = value.lower().split("x", 1)
    return int(width), int(height)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crop and optionally resize a web-generated image for PPT Master use."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input image path")
    parser.add_argument("--output", required=True, type=Path, help="Output image path")
    parser.add_argument("--crop-left", type=int, default=0, help="Pixels to crop from the left edge")
    parser.add_argument("--crop-top", type=int, default=0, help="Pixels to crop from the top edge")
    parser.add_argument("--crop-right", type=int, default=0, help="Pixels to crop from the right edge")
    parser.add_argument("--crop-bottom", type=int, default=0, help="Pixels to crop from the bottom edge")
    parser.add_argument(
        "--resize-back",
        action="store_true",
        help="Resize the cropped image back to the original size",
    )
    parser.add_argument(
        "--target-size",
        default=None,
        help="Optional resize target in WIDTHxHEIGHT form. Overrides --resize-back",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(args.input) as image:
        original_size = image.size
        left = args.crop_left
        top = args.crop_top
        right = image.width - args.crop_right
        bottom = image.height - args.crop_bottom

        if left < 0 or top < 0 or right <= left or bottom <= top:
            raise ValueError("Invalid crop values for the input image size.")

        result = image.crop((left, top, right, bottom))

        if args.target_size:
            target_size = parse_size(args.target_size)
            result = result.resize(target_size, Image.Resampling.LANCZOS)
        elif args.resize_back:
            result = result.resize(original_size, Image.Resampling.LANCZOS)

        if args.output.suffix.lower() in {".jpg", ".jpeg"} and result.mode in {"RGBA", "LA"}:
            flattened = Image.new("RGB", result.size, color="white")
            flattened.paste(result, mask=result.getchannel("A"))
            result = flattened

        result.save(args.output)

    print(f"[done] saved cleaned image to {args.output}")


if __name__ == "__main__":
    main()
