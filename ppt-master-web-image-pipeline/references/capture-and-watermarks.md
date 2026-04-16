# Capture And Watermarks

The final deck asset must be clean. Visible provider branding, chat chrome, badges, or screenshot framing are not acceptable in `project/images/`.

## Capture Order

Use this order every time:

1. original or full-size download from the website
2. open the generated image in its own view and save that asset
3. inspect DevTools network responses for the image request
4. inspect the page for a `blob:` image source and open it directly
5. screenshot plus crop only as a last resort

## Screenshot Fallback

Only use screenshot capture when the real binary asset cannot be obtained.

Rules:

- capture only the image rectangle, not chat UI
- crop tightly
- resize back to the intended working dimensions when needed
- save under the final PPT Master filename, not a temporary download name

## Watermark Policy

- If a provider logo or watermark is visible in the exported image, do not accept it as final.
- Prefer regeneration over aggressive editing when the mark overlaps the main subject.
- Prefer cleanup scripts only for edge marks, corner badges, and simple framing issues.

## Cleanup Tactics

### Gemini and Nano Banana

- If the image shows the known Gemini-family corner mark and PPT Master is installed, try:

```bash
python <ppt-master>/scripts/gemini_watermark_remover.py <image_path>
```

- Use `postprocess_web_image.py` afterward only if a light edge crop is still needed.

### Generic Corner Badge Or Edge Marker

Use:

```bash
python ${SKILL_DIR}/scripts/postprocess_web_image.py \
  --input <raw> \
  --output <final> \
  --crop-right 48 \
  --crop-bottom 48 \
  --resize-back
```

Adjust crop values per asset. Keep the crop minimal.

## Do Not Do

- Do not keep a visible provider logo in the final deck.
- Do not use a low-resolution screenshot when a full-size asset is available.
- Do not save platform-assigned filenames into the project.
- Do not hide a watermark under text if the image is supposed to be reusable elsewhere in the deck.
