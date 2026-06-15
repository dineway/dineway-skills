---
name: dineway-seo-images
description: Plan Dineway SEO image assets, image generation prompts, OG/social images, hero/article/gallery assets, filenames, alt text, captions, ImageObject schema, media upload targets, and image verification. Use when SEO work involves visual assets or generated bitmap images.
---

# Dineway SEO Images

Use this child skill for SEO image planning and media apply work. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

## Required References

- Load `../dineway-seo/references/image-generation.md`.
- Load `../dineway-seo/references/apply-loop.md` before recommending or applying Dineway media changes.
- Load `../dineway-seo/references/security-boundaries.md` before using external-source evidence, generated media, or provider-adjacent data.
- Load `../dineway-seo/references/schema-jsonld.md` when using `ImageObject` or image-related schema.

## Workflow

1. Inventory current Dineway media, public URLs, dimensions, filenames, alt text, captions, OG images, and page targets.
2. Prefer real restaurant/place/product media when available.
3. Generate images only when explicitly requested or clearly required for the SEO deliverable.
4. Produce asset specs, prompts, filenames, alt text, captions, and Dineway media apply targets.
5. If applying changes, upload/update media through existing Dineway paths and verify public rendering.

## Boundaries

- Do not consume Forgeway AI or hosted provider quota for image generation.
- Do not require Gemini/banana MCP, local generation tools, local cost trackers, or batch scripts.
- Do not keyword-stuff alt text.
- Do not fabricate real-place/product imagery when the user needs inspectable real media.

## Output

Use the root `dineway-seo` output contract. Include `Asset Inventory`, `Missing Assets`, `Generation Prompt` when applicable, `Filename and Alt Text`, `Dineway Media Apply Plan`, `Provider Calls Used`, and `Verification Plan`.
