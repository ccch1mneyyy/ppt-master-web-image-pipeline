#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ppt_master_web_common import dump_json, extract_project_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract PPT Master image resources from design_spec.md."
    )
    parser.add_argument("project_or_design_spec", help="Project directory or design_spec.md path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path. Defaults to project/images/web_generation_manifest.json",
    )
    parser.add_argument(
        "--include-non-pending",
        action="store_true",
        help="Include Existing and Placeholder rows instead of Pending rows only",
    )
    args = parser.parse_args()

    manifest = extract_project_manifest(
        args.project_or_design_spec,
        include_non_pending=args.include_non_pending,
    )
    output_path = args.output
    if output_path is None:
        output_path = Path(manifest["images_dir"]) / "web_generation_manifest.json"

    dump_json(output_path, manifest)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"\n[done] wrote manifest to {output_path}")


if __name__ == "__main__":
    main()
