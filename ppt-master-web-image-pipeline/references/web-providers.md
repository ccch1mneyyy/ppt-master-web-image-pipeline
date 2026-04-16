# Web Providers

This skill supports browser-based image generation through logged-in sessions. Use the user's existing subscriptions instead of API keys when possible.

## Provider Matrix

| Provider | Best for | Common save path | Typical risk | Notes |
| --- | --- | --- | --- | --- |
| Gemini | Backgrounds, abstract plates, polished illustrations | Full-size download or blob capture | corner mark, empty download, browser chrome | Good for presentation backdrops and calm composition |
| Nano Banana | Gemini-family or Banana-style image generation workflows | Original image download or blob capture | same family watermark and corner mark risks | Treat as Gemini-family if the workflow runs inside a Google UI |
| ChatGPT | Photography, crisp product scenes, stylized illustrations | open image, original download, network capture | chat chrome in screenshots | Strong for focal-subject images |
| Grok | Photography, dramatic backgrounds, visual concepts | original image or open-in-new-tab | chat card overlays | Good for high-contrast or cinematic scenes |
| Doubao | Illustration, friendly product visuals, mixed Chinese prompt workflows | original save, network capture if needed | UI stickers or overlay chrome | Strong when the prompt is Chinese-first |

## Selection Heuristics

Default ordering when the user does not choose a site:

- `Background`: Gemini, Nano Banana, Grok, ChatGPT, Doubao
- `Photography`: ChatGPT, Grok, Doubao, Gemini, Nano Banana
- `Illustration`: ChatGPT, Doubao, Gemini, Nano Banana, Grok
- `Decorative`: Gemini, Nano Banana, ChatGPT, Grok, Doubao
- `Diagram`: do not default to websites for precise labeled charts

## Provider Notes

### Gemini

- Prefer native full-size download first.
- If the download is empty or corrupted, inspect the rendered image element and capture the real `blob:` source.
- If the resulting image has the known Gemini corner mark and PPT Master is installed, prefer PPT Master's `gemini_watermark_remover.py`.

### Nano Banana

- If Banana is exposed through a Gemini or Google-hosted interface, follow the Gemini rules above.
- If Banana is a separate image site, still preserve the same capture contract: exact filename, full-size download first, blob capture fallback second.

### ChatGPT

- Avoid saving screenshots with chat bubbles or toolbar chrome.
- If the UI only offers an in-chat image card, open the image itself before downloading or capturing.
- Favor ChatGPT for photoreal scenes, packaged products, or controlled hero imagery.

### Grok

- Prefer opening the generated asset in its own view before saving.
- Watch for card-level overlays or framing bars around the real image.
- Favor Grok for cinematic scenes, moody backgrounds, and concept-heavy photography.

### Doubao

- Keep prompts explicit and concrete. Chinese prompts often work well.
- Use the original image save path when possible.
- If the UI exposes only an in-page rendered element, fall back to network or blob capture and save locally under the PPT Master filename.
