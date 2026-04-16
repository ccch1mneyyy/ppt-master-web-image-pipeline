#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

REQUIRED_IMAGE_HEADERS = {
    "filename",
    "dimensions",
    "purpose",
    "type",
    "status",
    "generation description",
}

SUPPORTED_PROVIDERS = ("auto", "gemini", "banana", "chatgpt", "grok", "doubao")

TYPE_PROVIDER_ORDER = {
    "Background": ["gemini", "banana", "grok", "chatgpt", "doubao"],
    "Photography": ["chatgpt", "grok", "doubao", "gemini", "banana"],
    "Illustration": ["chatgpt", "doubao", "gemini", "banana", "grok"],
    "Decorative": ["gemini", "banana", "chatgpt", "grok", "doubao"],
    "Diagram": ["chatgpt", "doubao", "grok", "gemini", "banana"],
}

NEGATIVE_PROMPTS = {
    "Background": "text, letters, watermark, logo, faces, busy patterns, high contrast details, provider UI chrome",
    "Photography": "watermark, logo, text overlay, artificial collage, CGI, illustration, distorted faces, provider UI chrome",
    "Illustration": "realistic photography, 3D render, watermark, logo, text, poster layout, provider UI chrome",
    "Diagram": "cluttered, messy, overlapping elements, dark background, photorealistic, watermark, logo, embedded labels",
    "Decorative": "busy, cluttered, high contrast, distracting, photorealistic, watermark, logo, text",
}

TYPE_STYLE_HINTS = {
    "Background": "presentation background, subtle abstraction, calm negative space",
    "Photography": "credible editorial photography, presentation-safe framing",
    "Illustration": "clean illustration, presentation-ready composition",
    "Diagram": "conceptual diagram aesthetic, simplified structure",
    "Decorative": "subtle decorative treatment, restrained visual support",
}

DIAGRAM_PRECISION_HINTS = {
    "label",
    "labels",
    "data",
    "table",
    "chart",
    "bar chart",
    "line chart",
    "pie chart",
    "workflow",
    "flowchart",
    "architecture",
    "sequence",
    "matrix",
    "timeline",
    "organization chart",
    "org chart",
}


def ensure_supported_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider '{provider}'. Supported values: {', '.join(SUPPORTED_PROVIDERS)}"
        )
    return normalized


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def resolve_project_paths(project_or_design_spec: str) -> tuple[Path, Path, Path]:
    source = Path(project_or_design_spec).expanduser().resolve()
    if source.is_dir():
        project_dir = source
        design_spec = project_dir / "design_spec.md"
    else:
        design_spec = source
        project_dir = design_spec.parent
    if not design_spec.exists():
        raise FileNotFoundError(f"design_spec.md not found: {design_spec}")
    images_dir = project_dir / "images"
    return project_dir, design_spec, images_dir


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_markdown(value: str) -> str:
    text = value.replace("\\|", "|")
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_field(value: str) -> str:
    plain = strip_markdown(value)
    lowered = plain.lower()
    placeholders = (
        "[filled by strategist]",
        "[to be filled]",
        "[todo",
        "[ratio]",
        "#......",
        "{project_name}",
    )
    if any(token in lowered for token in placeholders):
        return ""
    if plain in {"-", "[ ]", "[]"}:
        return ""
    return plain


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current = "__root__"
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(buffer).strip("\n")
            current = strip_markdown(line[3:].strip())
            buffer = []
        else:
            buffer.append(line)
    sections[current] = "\n".join(buffer).strip("\n")
    return sections


def find_section(sections: dict[str, str], phrase: str) -> str:
    target = phrase.lower()
    for name, content in sections.items():
        if target in name.lower():
            return content
    return ""


def split_cells(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_separator_line(line: str) -> bool:
    cells = split_cells(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_markdown_tables(block: str) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    lines = block.splitlines()
    index = 0
    while index < len(lines):
        if not lines[index].strip().startswith("|"):
            index += 1
            continue
        candidate: list[str] = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            candidate.append(lines[index].rstrip())
            index += 1
        if len(candidate) < 2 or not is_separator_line(candidate[1]):
            continue
        headers = [strip_markdown(cell) for cell in split_cells(candidate[0])]
        rows: list[dict[str, str]] = []
        for raw_row in candidate[2:]:
            cells = split_cells(raw_row)
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            elif len(cells) > len(headers):
                fixed = cells[: len(headers) - 1]
                fixed.append(" | ".join(cells[len(headers) - 1 :]))
                cells = fixed
            row = {headers[idx]: cells[idx].strip() for idx in range(len(headers))}
            if any(strip_markdown(value) for value in row.values()):
                rows.append(row)
        tables.append({"headers": headers, "rows": rows})
    return tables


def find_table_by_headers(tables: list[dict[str, Any]], headers: set[str]) -> dict[str, Any] | None:
    normalized_required = {header.lower() for header in headers}
    for table in tables:
        normalized_headers = {strip_markdown(header).lower() for header in table["headers"]}
        if normalized_required.issubset(normalized_headers):
            return table
    return None


def rows_to_map(rows: list[dict[str, str]], key_field: str, value_field: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in rows:
        key = strip_markdown(row.get(key_field, ""))
        value = row.get(value_field, "").strip()
        if key:
            result[key] = value
    return result


def extract_bullets(section_text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in section_text.splitlines():
        match = re.match(r"-\s*\*\*(.+?)\*\*:\s*(.+)", line.strip())
        if match:
            result[strip_markdown(match.group(1))] = match.group(2).strip()
    return result


def normalize_status(value: str) -> str:
    plain = strip_markdown(value).lower()
    if "generated" in plain:
        return "Generated"
    if "pending" in plain:
        return "Pending"
    if "existing" in plain:
        return "Existing"
    if "placeholder" in plain:
        return "Placeholder"
    return strip_markdown(value)


def normalize_image_type(raw_type: str, purpose: str, description: str) -> str:
    candidate = clean_field(raw_type)
    if candidate in TYPE_PROVIDER_ORDER:
        return candidate

    combined = f"{purpose} {description}".lower()
    if any(token in combined for token in ("background", "cover", "chapter", "backdrop")):
        return "Background"
    if any(token in combined for token in ("diagram", "workflow", "flowchart", "architecture", "chart", "matrix", "timeline")):
        return "Diagram"
    if any(token in combined for token in ("pattern", "texture", "border", "divider", "decorative", "accent")):
        return "Decorative"
    if any(token in combined for token in ("photo", "photography", "product", "portrait", "team", "people", "office", "real")):
        return "Photography"
    return "Illustration"


def parse_dimensions(value: str) -> tuple[int, int] | None:
    match = re.search(r"(\d+)\s*[xX]\s*(\d+)", value)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def ratio_from_dimensions(width: int, height: int) -> str:
    fraction = Fraction(width, height).limit_denominator(64)
    return f"{fraction.numerator}:{fraction.denominator}"


def infer_ratio(dimensions: str, raw_ratio: str) -> str:
    ratio = clean_field(raw_ratio)
    if ratio:
        return ratio
    parsed = parse_dimensions(dimensions)
    if not parsed:
        return ""
    return ratio_from_dimensions(*parsed)


def provider_order_for_type(image_type: str, forced_provider: str = "auto") -> list[str]:
    if forced_provider != "auto":
        return [forced_provider]
    return TYPE_PROVIDER_ORDER.get(image_type, TYPE_PROVIDER_ORDER["Illustration"])


def diagram_requires_manual_attention(image_type: str, purpose: str, description: str) -> bool:
    if image_type != "Diagram":
        return False
    combined = f"{purpose} {description}".lower()
    return any(token in combined for token in DIAGRAM_PRECISION_HINTS)


def locate_image_table(lines: list[str]) -> tuple[int, int, int, list[str]]:
    for header_idx in range(len(lines) - 1):
        if not lines[header_idx].strip().startswith("|"):
            continue
        headers = [strip_markdown(cell) for cell in split_cells(lines[header_idx])]
        normalized = {header.lower() for header in headers}
        if not REQUIRED_IMAGE_HEADERS.issubset(normalized):
            continue
        if header_idx + 1 >= len(lines) or not is_separator_line(lines[header_idx + 1]):
            continue
        row_start = header_idx + 2
        row_end = row_start
        while row_end < len(lines) and lines[row_end].strip().startswith("|"):
            row_end += 1
        return header_idx, row_start, row_end, headers
    raise ValueError("Image Resource List table not found in design_spec.md")


def build_color_directive(color_scheme: dict[str, str]) -> str:
    priorities = ("Primary", "Accent", "Secondary accent", "Background", "Secondary bg")
    parts: list[str] = []
    for role in priorities:
        value = clean_field(color_scheme.get(role, ""))
        if value:
            parts.append(f"{role.lower()} {value}")
    if not parts:
        return "color palette aligned with the deck"
    return "color palette: " + ", ".join(parts)


def derive_deck_style_anchor(manifest: dict[str, Any]) -> str:
    parts: list[str] = []
    design_style = clean_field(manifest.get("design_style", ""))
    tone = clean_field(manifest.get("tone", ""))
    theme = clean_field(manifest.get("theme", ""))
    if design_style:
        parts.append(design_style)
    if tone:
        parts.append(tone)
    if theme:
        parts.append(theme)
    parts.append(build_color_directive(manifest.get("color_scheme", {})))
    parts.append("cohesive presentation visual language")
    parts.append("high quality")
    return ", ".join(part for part in parts if part)


def build_subject_description(item: dict[str, Any]) -> str:
    description = clean_field(item.get("generation_description", ""))
    purpose = clean_field(item.get("purpose", ""))
    image_type = item.get("type", "Illustration")

    if description:
        return description
    if image_type == "Background":
        return f"presentation background for {purpose or item['filename']}"
    if purpose:
        return f"{purpose} visual"
    return f"presentation image for {item['filename']}"


def build_style_directive(manifest: dict[str, Any], item: dict[str, Any]) -> str:
    image_type = item.get("type", "Illustration")
    deck_style = clean_field(manifest.get("design_style", "")) or clean_field(manifest.get("tone", ""))
    type_style = TYPE_STYLE_HINTS.get(image_type, TYPE_STYLE_HINTS["Illustration"])
    if deck_style:
        return f"{type_style}, aligned with deck style {deck_style}"
    return type_style


def build_composition_directive(item: dict[str, Any]) -> str:
    image_type = item.get("type", "Illustration")
    purpose = clean_field(item.get("purpose", ""))
    description = clean_field(item.get("generation_description", ""))
    aspect_ratio = clean_field(item.get("aspect_ratio", "")) or "16:9"
    context = f"{purpose} {description}".lower()

    if image_type == "Background":
        if any(token in context for token in ("cover", "chapter", "title")):
            return f"{aspect_ratio} aspect ratio, slide-cover background, generous negative space for title and subtitle, low-clutter center and edges"
        return f"{aspect_ratio} aspect ratio, background plate with calm whitespace for text overlay"
    if image_type == "Photography":
        return f"{aspect_ratio} aspect ratio, one clear focal subject, balanced whitespace, no cropped essential content"
    if image_type == "Illustration":
        return f"{aspect_ratio} aspect ratio, clean readable composition, one quiet side for text if needed"
    if image_type == "Decorative":
        return f"{aspect_ratio} aspect ratio, subtle support element, not the dominant focal point"
    if diagram_requires_manual_attention(image_type, purpose, description):
        return f"{aspect_ratio} aspect ratio, conceptual diagram look only, no embedded labels, no dense data"
    return f"{aspect_ratio} aspect ratio, clear conceptual structure, simplified relationships, no embedded labels"


def build_quality_directive(item: dict[str, Any]) -> str:
    image_type = item.get("type", "Illustration")
    if image_type == "Photography":
        return "presentation-ready, believable lighting, crisp details, no text, no watermark, no logo"
    if image_type == "Background":
        return "presentation-ready, soft transitions, clean edges, no text, no watermark, no logo"
    return "presentation-ready, clean edges, high detail, no text, no watermark, no logo"


def build_negative_prompt(image_type: str) -> str:
    return NEGATIVE_PROMPTS.get(image_type, NEGATIVE_PROMPTS["Illustration"])


def build_alt_text(item: dict[str, Any]) -> str:
    purpose = clean_field(item.get("purpose", ""))
    description = clean_field(item.get("generation_description", ""))
    if purpose and description:
        return f"{purpose}: {description}"
    if description:
        return description
    if purpose:
        return purpose
    return item["filename"]


def build_prompt_entry(manifest: dict[str, Any], item: dict[str, Any], provider: str) -> dict[str, Any]:
    forced_provider = ensure_supported_provider(provider)
    providers = provider_order_for_type(item["type"], forced_provider=forced_provider)
    web_safe = not diagram_requires_manual_attention(item["type"], item["purpose"], item["generation_description"])
    note = ""
    if item["type"] == "Diagram" and not web_safe:
        note = "Precise labeled diagrams are weak candidates for web image generators. Prefer manual SVG or Executor construction."
    elif item["type"] == "Background":
        note = "Preserve calm negative space for overlaid slide titles."
    elif item["type"] == "Photography":
        note = "Keep one clean focal subject and avoid poster-like compositions."
    else:
        note = "Keep the deck's palette and visual language consistent."

    prompt_parts = [
        manifest["deck_style_anchor"],
        build_subject_description(item),
        build_style_directive(manifest, item),
        build_color_directive(manifest.get("color_scheme", {})),
        build_composition_directive(item),
        build_quality_directive(item),
    ]
    prompt = ", ".join(part for part in prompt_parts if part)

    return {
        "filename": item["filename"],
        "dimensions": item["dimensions"],
        "aspect_ratio": item["aspect_ratio"],
        "purpose": item["purpose"],
        "type": item["type"],
        "status": item["status"],
        "generation_description": item["generation_description"],
        "output_path": item["output_path"],
        "provider_order": providers,
        "prompt": prompt,
        "negative_prompt": build_negative_prompt(item["type"]),
        "alt_text": build_alt_text(item),
        "web_safe": web_safe,
        "note": note,
    }


def build_prompt_document(manifest: dict[str, Any], entries: list[dict[str, Any]], provider: str) -> str:
    lines: list[str] = []
    lines.append("# Image Generation Prompts")
    lines.append("")
    lines.append(f"> Project: {manifest.get('project_name') or manifest.get('project_dir')}")
    lines.append(f"> Generated: {utc_timestamp()}")
    lines.append(f"> Canvas: {manifest.get('canvas_format') or 'Unknown'}")
    lines.append(f"> Web provider mode: {provider}")
    lines.append(f"> Deck Style Anchor: {manifest['deck_style_anchor']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Image List Overview")
    lines.append("")
    lines.append("| # | Filename | Type | Dimensions | Recommended Web UI | Web Safe |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for index, entry in enumerate(entries, start=1):
        recommended = " > ".join(entry["provider_order"])
        web_safe = "yes" if entry["web_safe"] else "manual-review"
        lines.append(
            f"| {index} | {entry['filename']} | {entry['type']} | {entry['dimensions']} | {recommended} | {web_safe} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Prompts")
    lines.append("")
    for index, entry in enumerate(entries, start=1):
        lines.append(f"### Image {index}: {entry['filename']}")
        lines.append("")
        lines.append("| Attribute | Value |")
        lines.append("| --------- | ----- |")
        lines.append(f"| Purpose | {entry['purpose'] or '-'} |")
        lines.append(f"| Type | {entry['type']} |")
        lines.append(f"| Dimensions | {entry['dimensions']} ({entry['aspect_ratio'] or 'unknown'}) |")
        lines.append(f"| Original description | {entry['generation_description'] or '-'} |")
        lines.append("")
        lines.append("**Prompt**:")
        lines.append(entry["prompt"])
        lines.append("")
        lines.append("**Negative Prompt**:")
        lines.append(entry["negative_prompt"])
        lines.append("")
        lines.append("**Alt Text**:")
        lines.append(f"> {entry['alt_text']}")
        lines.append("")
        lines.append("**Recommended Web UI**:")
        lines.append(", ".join(entry["provider_order"]))
        lines.append("")
        lines.append("**Generation Note**:")
        lines.append(entry["note"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_project_manifest(project_or_design_spec: str, include_non_pending: bool = False) -> dict[str, Any]:
    project_dir, design_spec, images_dir = resolve_project_paths(project_or_design_spec)
    text = read_text(design_spec)
    sections = split_sections(text)

    project_info_section = find_section(sections, "Project Information")
    visual_theme_section = find_section(sections, "Visual Theme")
    image_section = find_section(sections, "Image Resource List")

    project_tables = parse_markdown_tables(project_info_section)
    project_table = find_table_by_headers(project_tables, {"Item", "Value"})
    project_info = rows_to_map(project_table["rows"], "Item", "Value") if project_table else {}

    visual_tables = parse_markdown_tables(visual_theme_section)
    color_table = find_table_by_headers(visual_tables, {"Role", "HEX", "Purpose"})
    color_scheme = rows_to_map(color_table["rows"], "Role", "HEX") if color_table else {}
    theme_bullets = extract_bullets(visual_theme_section)

    image_tables = parse_markdown_tables(image_section)
    image_table = find_table_by_headers(
        image_tables,
        {"Filename", "Dimensions", "Purpose", "Type", "Status", "Generation Description"},
    )
    if not image_table:
        raise ValueError("Image Resource List table with required headers was not found.")

    images: list[dict[str, Any]] = []
    for row in image_table["rows"]:
        normalized_row = {strip_markdown(key): value for key, value in row.items()}
        filename = clean_field(normalized_row.get("Filename", ""))
        if not filename:
            continue

        dimensions = clean_field(normalized_row.get("Dimensions", ""))
        ratio = infer_ratio(dimensions, normalized_row.get("Ratio", ""))
        purpose = clean_field(normalized_row.get("Purpose", ""))
        description = clean_field(normalized_row.get("Generation Description", ""))
        status = normalize_status(normalized_row.get("Status", ""))
        image_type = normalize_image_type(normalized_row.get("Type", ""), purpose, description)
        parsed_dimensions = parse_dimensions(dimensions) or (None, None)

        item = {
            "filename": filename,
            "dimensions": dimensions,
            "width": parsed_dimensions[0],
            "height": parsed_dimensions[1],
            "aspect_ratio": ratio,
            "purpose": purpose,
            "type": image_type,
            "status": status,
            "generation_description": description,
            "output_path": str((images_dir / filename).resolve()),
        }
        if include_non_pending or status == "Pending":
            images.append(item)

    manifest = {
        "project_name": clean_field(project_info.get("Project Name", "")),
        "project_dir": str(project_dir),
        "design_spec": str(design_spec),
        "images_dir": str(images_dir),
        "canvas_format": clean_field(project_info.get("Canvas Format", "")),
        "design_style": clean_field(project_info.get("Design Style", "")) or clean_field(theme_bullets.get("Style", "")),
        "target_audience": clean_field(project_info.get("Target Audience", "")),
        "use_case": clean_field(project_info.get("Use Case", "")),
        "theme": clean_field(theme_bullets.get("Theme", "")),
        "tone": clean_field(theme_bullets.get("Tone", "")),
        "color_scheme": {role: clean_field(value) for role, value in color_scheme.items() if clean_field(value)},
        "images": images,
        "generated_at": utc_timestamp(),
    }
    manifest["deck_style_anchor"] = derive_deck_style_anchor(manifest)
    return manifest
