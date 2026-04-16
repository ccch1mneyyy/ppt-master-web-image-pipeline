#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

from ppt_master_web_common import extract_project_manifest, parse_dimensions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify that PPT Master images exist and fit the requested aspect ratios."
    )
    parser.add_argument("project_or_design_spec", help="Project directory or design_spec.md path")
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=None,
        help="Override the images directory. Defaults to project/images",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.03,
        help="Allowed relative aspect-ratio difference. Default: 0.03",
    )
    parser.add_argument(
        "--require-no-pending",
        action="store_true",
        help="Fail if any row still has Pending status after verification",
    )
    args = parser.parse_args()

    manifest = extract_project_manifest(args.project_or_design_spec, include_non_pending=True)
    images_dir = (args.images_dir or Path(manifest["images_dir"])).resolve()

    required_statuses = {"Generated", "Existing"}
    missing: list[str] = []
    mismatched: list[str] = []
    present_but_pending: list[str] = []
    pending_rows: list[str] = []

    for item in manifest["images"]:
        filename = item["filename"]
        path = images_dir / filename
        status = item["status"]

        if status == "Pending":
            pending_rows.append(filename)

        if not path.exists():
            if status in required_statuses:
                missing.append(filename)
            continue

        if status == "Pending":
            present_but_pending.append(filename)

        expected = parse_dimensions(item["dimensions"])
        if not expected:
            continue

        with Image.open(path) as image:
            actual_width, actual_height = image.size

        expected_ratio = expected[0] / expected[1]
        actual_ratio = actual_width / actual_height
        ratio_diff = abs(actual_ratio - expected_ratio) / expected_ratio
        if ratio_diff > args.tolerance:
            mismatched.append(
                f"{filename} expected ratio {expected_ratio:.4f} from {expected[0]}x{expected[1]} but got {actual_width}x{actual_height}"
            )

    print("Verification summary")
    print(f"  Images directory: {images_dir}")
    print(f"  Missing required files: {len(missing)}")
    print(f"  Aspect mismatches: {len(mismatched)}")
    print(f"  Present but still pending: {len(present_but_pending)}")
    print(f"  Pending rows: {len(pending_rows)}")

    if missing:
        print("\nMissing required files:")
        for item in missing:
            print(f"  - {item}")

    if mismatched:
        print("\nAspect ratio mismatches:")
        for item in mismatched:
            print(f"  - {item}")

    if present_but_pending:
        print("\nFiles present but status still Pending:")
        for item in present_but_pending:
            print(f"  - {item}")

    should_fail = bool(missing or mismatched)
    if args.require_no_pending and pending_rows:
        should_fail = True
        print("\nPending rows still remain:")
        for item in pending_rows:
            print(f"  - {item}")

    if should_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
