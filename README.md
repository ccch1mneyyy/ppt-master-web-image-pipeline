# PPT Master Web Image Pipeline

English | [中文](./README_CN.md)

`ppt-master-web-image-pipeline` is a Codex skill that bridges PPT Master's
Step 5 image generation workflow to logged-in web image tools such as Gemini,
Nano Banana, ChatGPT, Grok, and Doubao.

It is designed for users who already have access to browser-based image tools
but do not want to rely on API keys. The skill reads a PPT Master project,
builds prompt manifests, helps drive browser-based generation, cleans captured
assets, and writes the final files back into `project/images/`.

## What it does

- Extracts pending image rows from `design_spec.md`
- Builds `images/image_prompts.md` and `images/web_generation_manifest.json`
- Reuses an existing logged-in browser session to generate and capture images
- Cleans watermarks, corner marks, and screenshot artifacts
- Verifies image outputs and updates image status rows in `design_spec.md`

## Repository layout

```text
ppt-master-web-image-pipeline/
|-- SKILL.md
|-- agents/
|-- references/
`-- scripts/
```

## Installation

Copy the `ppt-master-web-image-pipeline/` folder from this repository into your
Codex skills directory:

```text
~/.codex/skills/
```

On Windows this is usually:

```text
C:/Users/<your-user>/.codex/skills/
```

Then restart Codex so the skill is reloaded.

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
- Diagram-like assets that require precise labels or vector fidelity should be
  routed back to PPT Master Executor or manual SVG work instead of web image
  generation.

## Included docs

- `技能介绍.md`: original Chinese introduction
- `ppt-master-web-image-pipeline/SKILL.md`: main skill entry
- `ppt-master-web-image-pipeline/references/`: workflow references
- `ppt-master-web-image-pipeline/scripts/`: helper scripts
