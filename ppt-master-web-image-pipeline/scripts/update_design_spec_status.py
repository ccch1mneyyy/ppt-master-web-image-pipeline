#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ppt_master_web_common import (
    locate_image_table,
    normalize_status,
    resolve_project_paths,
    split_cells,
    strip_markdown,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update PPT Master Image Resource List statuses based on generated files."
    )
    parser.add_argument("project_or_design_spec", help="Project directory or design_spec.md path")
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=None,
        help="Override the images directory. Defaults to project/images",
    )
    parser.add_argument(
        "--status",
        default="Generated",
        help="Status to apply when a matching file exists. Default: Generated",
    )
    parser.add_argument(
        "--set",
        dest="explicit_updates",
        action="append",
        default=[],
        help="Explicit update in filename=Status form. Can be repeated.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing the file")
    args = parser.parse_args()

    _, design_spec, default_images_dir = resolve_project_paths(args.project_or_design_spec)
    images_dir = (args.images_dir or default_images_dir).resolve()

    explicit_updates: dict[str, str] = {}
    for raw in args.explicit_updates:
        if "=" not in raw:
            raise ValueError(f"Invalid --set value '{raw}'. Expected filename=Status")
        filename, status = raw.split("=", 1)
        explicit_updates[filename.strip()] = status.strip()

    lines = design_spec.read_text(encoding="utf-8", errors="replace").splitlines()
    _, row_start, row_end, headers = locate_image_table(lines)
    header_map = {strip_markdown(header).lower(): idx for idx, header in enumerate(headers)}
    filename_idx = header_map["filename"]
    status_idx = header_map["status"]

    changes: list[tuple[str, str, str]] = []

    for row_idx in range(row_start, row_end):
        cells = split_cells(lines[row_idx])
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        elif len(cells) > len(headers):
            cells = cells[: len(headers)]

        filename = strip_markdown(cells[filename_idx])
        current_status = normalize_status(cells[status_idx])
        requested_status = explicit_updates.get(filename)

        if requested_status is None:
            file_exists = (images_dir / filename).exists()
            if file_exists and current_status == "Pending":
                requested_status = args.status

        if not requested_status or requested_status == current_status:
            continue

        cells[status_idx] = requested_status
        lines[row_idx] = "| " + " | ".join(cells) + " |"
        changes.append((filename, current_status or "-", requested_status))

    if not changes:
        print("[done] no status changes needed")
        return

    if args.dry_run:
        print("[dry-run] planned updates:")
    else:
        design_spec.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[done] updated {design_spec}")

    for filename, before, after in changes:
        print(f"  - {filename}: {before} -> {after}")


if __name__ == "__main__":
    main()
