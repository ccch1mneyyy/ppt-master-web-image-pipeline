#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ppt_master_web_common import (
    build_prompt_document,
    build_prompt_entry,
    dump_json,
    ensure_supported_provider,
    extract_project_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build PPT Master image_prompts.md and a browser-generation manifest."
    )
    parser.add_argument("project_or_design_spec", help="Project directory or design_spec.md path")
    parser.add_argument(
        "--provider",
        default="auto",
        help="Default provider order anchor: auto, gemini, banana, chatgpt, grok, doubao",
    )
    parser.add_argument(
        "--include-non-pending",
        action="store_true",
        help="Include non-pending rows in the prompt document",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Markdown output path. Defaults to project/images/image_prompts.md",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=None,
        help="JSON manifest output path. Defaults to project/images/web_generation_manifest.json",
    )
    args = parser.parse_args()

    provider = ensure_supported_provider(args.provider)
    manifest = extract_project_manifest(
        args.project_or_design_spec,
        include_non_pending=args.include_non_pending,
    )
    entries = [build_prompt_entry(manifest, item, provider) for item in manifest["images"]]

    markdown_path = args.output or (Path(manifest["images_dir"]) / "image_prompts.md")
    json_path = args.manifest_output or (Path(manifest["images_dir"]) / "web_generation_manifest.json")

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(build_prompt_document(manifest, entries, provider), encoding="utf-8")

    dump_json(
        json_path,
        {
            **manifest,
            "provider_mode": provider,
            "items": entries,
        },
    )

    print(f"[done] wrote prompt document to {markdown_path}")
    print(f"[done] wrote web manifest to {json_path}")


if __name__ == "__main__":
    main()
