---
name: ppt-master-web-image-pipeline
description: >
  Bridge PPT Master Step 5 Image_Generator to logged-in web image tools such as
  Gemini, Nano Banana, ChatGPT, Grok, and Doubao. Use when a PPT Master project
  has a `design_spec.md` with pending image rows, the user wants browser-based
  generation instead of API keys, or Codex must build `images/image_prompts.md`,
  capture and download clean assets from web UIs, handle watermarks or corner
  badges, save exact filenames into `project/images`, update image statuses, and
  hand the project back to PPT Master Executor.
version: 0.1.0
homepage: https://github.com/ccchimneyyy/ppt-master-web-image-pipeline
---

# PPT Master Web Image Pipeline

Use this skill as a companion to `ppt-master` Step 5. It does not replace Strategist or Executor. It reads the project design spec, prepares prompts and manifests, drives logged-in image websites, cleans captured assets, and returns a project whose `images/` folder is ready for Executor.

## Preconditions

- The project contains `design_spec.md` and an `images/` directory.
- Section VIII includes an Image Resource List.
- The user is logged into at least one supported website in Chrome.
- If `ppt-master` is installed in `$CODEX_HOME/skills/ppt-master` or `~/.codex/skills/ppt-master`, read:
  - `references/image-generator.md`
  - `references/image-layout-spec.md`
  - `templates/design_spec_reference.md`
- Read `references/ppt-master-bridge.md` before first use.
- Read `references/web-providers.md` when choosing or operating a provider.
- Read `references/capture-and-watermarks.md` when download fidelity or cleanup matters.

## Workflow

### 1. Extract pending image resources

```bash
python ${SKILL_DIR}/scripts/extract_image_resource_list.py <project-or-design_spec>
```

- Default to pending rows only.
- Keep exact filenames from the resource list.
- If the image table is missing required columns, stop and fix `design_spec.md` before generating anything.

### 2. Build `image_prompts.md` and the web manifest

```bash
python ${SKILL_DIR}/scripts/build_ppt_image_prompts.py <project-or-design_spec> --provider auto
```

This writes:

- `images/image_prompts.md`
- `images/web_generation_manifest.json`

The JSON manifest is the operational checklist for website generation and capture.

### 3. Choose the website

- Respect explicit user preference first.
- Otherwise choose by image type:
  - `Background`: Gemini, Nano Banana, Grok
  - `Photography`: ChatGPT, Grok, Doubao
  - `Illustration`: ChatGPT, Doubao, Gemini, Nano Banana
  - `Decorative`: Gemini, Nano Banana, ChatGPT
  - `Diagram`: only use web generators for atmospheric or conceptual diagrams; for precise labeled charts, route back to Executor or manual SVG work
- Generate one image at a time.
- Keep deck-level visual coherence. Reuse the same provider across a run unless one prompt clearly needs a different website.

### 4. Generate and capture

- Reuse the user's logged-in web session.
- Prefer original or full-size download.
- If direct download fails or produces an empty file, use DevTools network or blob capture.
- If the site only exposes a rendered `blob:` image, open it in a new tab, capture the clean image rectangle, and save it under the exact PPT Master filename in `project/images/`.
- Never rely on browser download folder names.

### 5. Clean the asset

- Do not accept visible platform UI chrome, badges, or watermarks in final deck assets.
- For Gemini or Nano Banana corner mark removal, prefer PPT Master's `gemini_watermark_remover.py` if available.
- For simple edge markers, framing issues, or screenshot cleanup, run:

```bash
python ${SKILL_DIR}/scripts/postprocess_web_image.py --input <raw> --output <final> --crop-right 48 --crop-bottom 48 --resize-back
```

- If a watermark is baked into the main subject area and clean removal would damage the image, regenerate instead of heavy editing.

### 6. Verify and update status

```bash
python ${SKILL_DIR}/scripts/verify_ppt_images.py <project-or-design_spec> --require-no-pending
python ${SKILL_DIR}/scripts/update_design_spec_status.py <project-or-design_spec>
```

- Verify exact filenames and aspect-ratio fit.
- Move a row from `Pending` to `Generated` only after the file exists in `project/images/`.

### 7. Hand back to Executor

Before leaving this skill, confirm:

- `images/image_prompts.md` exists
- `images/web_generation_manifest.json` exists
- required image files exist in `project/images/`
- `design_spec.md` image rows are updated
- remaining diagram-like or manually blocked items are explicitly called out

## Rules

- Treat this as a Step 5 companion only. Do not edit SVG slides here.
- Keep filenames, dimensions intent, and type semantics from `design_spec.md`.
- Use the deck's color and style system. Do not generate random unrelated art directions.
- For cover and chapter backgrounds, reserve negative space for titles.
- For mixed text-image slides, bias composition toward one quiet side.
- Do not parallelize website generations or downloads.
- Do not change `Existing` assets unless the user asks.

## Scripts

- `scripts/extract_image_resource_list.py`
- `scripts/build_ppt_image_prompts.py`
- `scripts/update_design_spec_status.py`
- `scripts/verify_ppt_images.py`
- `scripts/postprocess_web_image.py`

## References

- `references/ppt-master-bridge.md`
- `references/web-providers.md`
- `references/capture-and-watermarks.md`
