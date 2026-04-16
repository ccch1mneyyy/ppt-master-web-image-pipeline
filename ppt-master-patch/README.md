# PPT Master Patch Bundle

This folder contains the minimal `ppt-master` files that were updated so the
main PPT Master skill can cooperate with `ppt-master-web-image-pipeline`
during Step 5 image generation.

## Included files

- `SKILL.md`
- `references/image-generator.md`
- `references/strategist.md`

## What changed

- The core pipeline now explicitly mentions the Step 5 web companion branch.
- Step 5 routing now prefers `ppt-master-web-image-pipeline` when the user has
  logged-in web image memberships but no usable API keys.
- The Image_Generator reference now documents the web companion workflow,
  supported websites, required manifest output, and watermark cleanup
  expectations.
- The Strategist handoff now tells PPT Master to choose between the API branch
  and the web companion branch based on the user's setup.

## How to install

Copy these files over the matching paths inside your local `ppt-master` skill:

```text
~/.codex/skills/ppt-master/SKILL.md
~/.codex/skills/ppt-master/references/image-generator.md
~/.codex/skills/ppt-master/references/strategist.md
```

On Windows this is usually:

```text
C:/Users/<your-user>/.codex/skills/ppt-master/
```

Then restart Codex so the updated Step 5 routing takes effect.
