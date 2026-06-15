# SEO Image Workflow

Use this for image planning, generation prompts, alt text, file naming, OG/social assets, and schema image fields.

## Boundaries

- Generate images only when the user explicitly asks or the task clearly requires an AI-created bitmap asset.
- Do not use Forgeway AI quota for SEO image generation.
- Do not require Gemini/banana MCP, local cost trackers, or provider-specific generation tools.
- For restaurants and local businesses, prefer real downloaded/uploaded media when available.

## Asset Types

| Asset             | Ratio        | Minimum Size          | Notes                                                |
| ----------------- | ------------ | --------------------- | ---------------------------------------------------- |
| OG image          | 1.91:1       | 1200x630              | Include brand/place/product signal; avoid tiny text. |
| Hero              | 16:9 or 3:2  | 1600px wide           | Show the real product/place/state when possible.     |
| Article feature   | 16:9 or 4:3  | 1200px wide           | Match page intent.                                   |
| Gallery thumbnail | 1:1 or 4:3   | 800px wide            | Crop consistently.                                   |
| Schema image      | source ratio | 1200px wide preferred | Must resolve publicly.                               |

## SEO Checklist

- Descriptive filename with lowercase words and hyphens.
- Accurate alt text describing the image, not keyword stuffing.
- Caption only when helpful for visitors.
- WebP/AVIF when the pipeline supports it, with sensible fallbacks.
- Lazy-load non-critical images.
- Include width/height to reduce layout shift.
- Use `ImageObject` only for real public image URLs.

## Output

Return:

- `Asset Inventory`
- `Missing Assets`
- `Generation Prompt` when applicable
- `Filename and Alt Text`
- `Dineway Media Apply Plan`
- `Verification`
