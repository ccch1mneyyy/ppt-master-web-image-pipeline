# PPT Master Web Image Pipeline

English | [中文](./README_CN.md)

`ppt-master-web-image-pipeline` is a Codex skill that bridges PPT Master's
Step 5 image generation workflow to logged-in web image tools such as Gemini,
Nano Banana, ChatGPT, Grok, and Doubao.

It is designed for users who already have access to browser-based image tools
but do not want to rely on API keys. The skill reads a PPT Master project,
builds prompt manifests, helps drive browser-based generation, cleans captured
assets, and writes the final files back into `project/images/`.

This repository now also includes a minimal `ppt-master` patch bundle so the
main PPT Master skill can recognize and route Step 5 to this companion flow
more naturally.

## What it does

- Extracts pending image rows from `design_spec.md`
- Builds `images/image_prompts.md` and `images/web_generation_manifest.json`
- Reuses an existing logged-in browser session to generate and capture images
- Cleans watermarks, corner marks, and screenshot artifacts
- Verifies image outputs and updates image status rows in `design_spec.md`

## Repository layout

```text
ppt-master-patch/
|-- README.md
|-- SKILL.md
`-- references/

ppt-master-web-image-pipeline/
|-- SKILL.md
|-- agents/
|-- references/
`-- scripts/
```

## Installation

1. Copy the `ppt-master-web-image-pipeline/` folder from this repository into
   your Codex skills directory:

```text
~/.codex/skills/
```

On Windows this is usually:

```text
C:/Users/<your-user>/.codex/skills/
```

2. If you want the main `ppt-master` skill to route Step 5 to the web
   companion automatically, copy the files from `ppt-master-patch/` into your
   local `ppt-master/` skill folder and overwrite the matching files:

```text
~/.codex/skills/ppt-master/SKILL.md
~/.codex/skills/ppt-master/references/image-generator.md
~/.codex/skills/ppt-master/references/strategist.md
```

3. Restart Codex so both skills are reloaded.

## Dependencies

The bundled Python scripts use Pillow:

```bash
pip install -r requirements.txt
```

## Recommended usage

1. Prepare a PPT Master project with `design_spec.md` and `images/`.
2. Use the skill to extract pending image resources.
3. Generate prompt manifests.
4. Reuse your logged-in browser session for web image generation.
5. Verify the generated images and update the project status.

## Notes

- This is a Step 5 companion skill for PPT Master. It does not replace the
  main PPT Master Strategist or Executor flows.
- The `ppt-master-patch/` directory only contains the files that were changed
  to integrate this web-generation route. It is intentionally a minimal patch,
  not a full mirror of the upstream PPT Master skill.
- Diagram-like assets that require precise labels or vector fidelity should be
  routed back to PPT Master Executor or manual SVG work instead of web image
  generation.

## Included docs

- `技能介绍.md`: original Chinese introduction
- `ppt-master-patch/`: minimal PPT Master patch bundle for Step 5 routing
- `ppt-master-web-image-pipeline/SKILL.md`: main skill entry
- `ppt-master-web-image-pipeline/references/`: workflow references
- `ppt-master-web-image-pipeline/scripts/`: helper scripts
