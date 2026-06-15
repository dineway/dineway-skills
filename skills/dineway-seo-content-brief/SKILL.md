---
name: dineway-seo-content-brief
description: Create or improve Dineway SEO content briefs, outlines, page refresh plans, metadata recommendations, and Dineway draft apply plans. Use for target keywords, local/service/menu/blog page briefs, existing-page improvements, search intent analysis, and evidence-backed content planning.
---

# Dineway SEO Content Brief

Use this child skill for content briefs and page improvement plans. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

## Required References

- Load `../dineway-seo/references/content-brief.md`.
- Load `../dineway-seo/references/apply-loop.md` before recommending or applying Dineway changes.
- Load `../dineway-seo/references/security-boundaries.md` before using provider evidence or external-source recommendations.
- Load `../dineway-seo/references/provider-selection.md` when live SERP, keyword, competitor, or page extraction data may be needed.
- Load `../dineway-seo/references/schema-jsonld.md` when the brief includes schema recommendations.

## Workflow

1. Inventory current Dineway state: relevant collection, content item, SEO metadata, slug/status/revision, site context, brand voice, media, and internal links.
2. Classify intent and page type from current evidence first.
3. Use DataForSEO or Firecrawl only when current Dineway/user evidence is not enough.
4. Filter SERP/reference pages before drawing conclusions; skip irrelevant directories, social/forum noise, login/admin pages, and unsupported sources.
5. Produce a draft-first brief with Dineway write targets.
6. If applying changes, use the narrowest Dineway content/SEO/media/settings path and verify.

## Boundaries

- Do not publish generated content unless explicitly requested and safely supported by the existing write path.
- Do not invent menu items, hours, awards, staff bios, reviews, prices, or local facts.
- Do not use local provider credentials, MCP provider tools, or local fetch/parse/render commands.
- Preserve existing URLs unless the plan includes redirects.

## Output

Use the root `dineway-seo` output contract. Include `Search Intent / Audience`, `Evidence Used`, `Recommended Dineway Changes`, `Provider Calls Used`, `Skipped or Risky Claims`, and `Verification Plan`.
