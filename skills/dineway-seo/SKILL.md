---
name: dineway-seo
description: Plan and execute Dineway SEO, local SEO, GEO, and answer-engine visibility workflows. Use when creating content briefs, topic clusters, competitor/comparison pages, schema JSON-LD, SEO image assets, or hosted Firecrawl/DataForSEO research for Dineway sites.
---

# Dineway SEO

Dineway SEO is a skill-first workflow for search, local, and answer-engine optimization. Use it to gather evidence, design changes, and apply them through existing Dineway content, media, SEO metadata, schema/settings, rendering, and code-patch paths.

## Boundaries

- Do not install or require Claude Code plugins, slash commands, subagents, MCP servers, local provider credentials, or local crawler/fetch/render commands.
- Do not add admin UI, plugin/admin routes, public local crawler commands, or provider BYOK fallback.
- Hosted live provider data must go through Forgeway `/api/firecrawl/*` or `/api/dataforseo/*` via `dineway seo firecrawl ...` or `dineway seo dataforseo ...`.
- Use raw Firecrawl/DataForSEO payloads returned by Forgeway, but do not expose provider credentials or billing details.
- Image generation is a skill workflow. Use the current agent image capability only when the user explicitly asks for generated images; do not consume Forgeway AI quota for SEO images.
- Apply work draft-first unless the user explicitly asks to publish and the existing Dineway write path supports it safely.

## Child Skills

Use this root skill for broad, mixed, or ambiguous SEO/GEO work. When the task clearly matches one workflow, use the matching child skill directly:

- `dineway-seo-content-brief`: content briefs, outlines, page refresh plans, metadata recommendations.
- `dineway-seo-cluster`: topic clusters, hub/spoke plans, internal link matrices.
- `dineway-seo-competitor-pages`: alternatives, comparison, roundup, and feature/price comparison pages.
- `dineway-seo-schema`: schema/JSON-LD audits, recommendations, validation, and Dineway schema apply plans.
- `dineway-seo-images`: SEO image planning, generation prompts, alt text, filenames, media apply plans.
- `dineway-seo-providers`: hosted Firecrawl/DataForSEO research, provider choice, and evidence interpretation.

Child skills must still use the shared Dineway apply loop and provider/security boundaries in `references/apply-loop.md`, `references/security-boundaries.md`, `references/provider-selection.md`, `references/firecrawl.md`, and `references/dataforseo.md` when relevant.

## Workflow

1. Identify the job type and load only the relevant reference:
   - content brief: `references/content-brief.md`
   - topic cluster: `references/topic-cluster.md`
   - competitor/comparison page: `references/competitor-pages.md`
   - FLOW operating model: `references/flow-framework.md`
   - schema/JSON-LD: `references/schema-jsonld.md`
   - image asset planning: `references/image-generation.md`
   - Firecrawl research: `references/firecrawl.md`
   - DataForSEO research: `references/dataforseo.md`
   - provider choice: `references/provider-selection.md`
   - provider/security boundaries: `references/security-boundaries.md`
   - applying changes: `references/apply-loop.md`
2. Inventory current Dineway state before proposing changes:
   - collections and `hasSeo` support;
   - current content item, slug, title, excerpt, SEO metadata, status, and revision;
   - site SEO settings, canonical/base URL, locale/hreflang, and JSON-LD contributors;
   - relevant media assets, alt text, captions, and public URLs;
   - site-context briefing, brand voice, policies, seasonal strategy, and human-in-the-loop notes.
3. Decide whether live provider data is needed. Use DataForSEO for SERP, keyword, competitor, maps, and AI visibility data; use Firecrawl for page extraction, URL discovery, crawl jobs, and search+scrape.
4. Produce a finding set before changes:
   - source evidence and dates;
   - prioritized opportunities;
   - skipped/risky claims;
   - Dineway write targets;
   - verification steps.
5. Apply through the narrowest existing surface:
   - content CRUD for page/post/menu/review/news/gallery copy;
   - SEO metadata fields for title, description, OG, canonical, noindex, and robots;
   - media upload/update for images, alt, captions, and dimensions;
   - site settings and SEO Graph contributions for global metadata and schema;
   - Astro code patches only when Dineway content/settings cannot express the needed rendering.
6. Verify rendered output and data consistency. Separate applied changes from recommendations that still need human approval or unavailable data.

## Output Contract

For planning tasks, return:

- `Goal`
- `Evidence Used`
- `Search Intent / Audience`
- `Recommended Dineway Changes`
- `Provider Calls Used`
- `Skipped or Risky Claims`
- `Verification Plan`

For applied tasks, return:

- `Applied Changes`
- `Files or Content Items Changed`
- `Provider Calls Used`
- `Verification Results`
- `Remaining Risks`

Do not include internal implementation instructions in public-facing copy.
