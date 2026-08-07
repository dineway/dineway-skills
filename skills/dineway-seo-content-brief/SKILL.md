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
- When invoked from the Content Optimization loop, load
  `../dineway-content-optimization/references/artifact-contract.md` and the active Research pack.

## Workflow

1. Inventory current Dineway state: relevant collection, content item, SEO metadata, slug/status/revision, site context, brand voice, media, and internal links.
2. Classify intent and page type from current evidence first.
3. Use DataForSEO or Firecrawl only when current Dineway/user evidence is not enough.
4. Filter SERP/reference pages before drawing conclusions; skip irrelevant directories, social/forum noise, login/admin pages, and unsupported sources.
5. Produce a draft-first brief with Dineway write targets. Include the audience, locale/market,
   primary and mixed intent, page type, differentiation, evidence-backed outline, observed
   questions, claim/source map, exclusions, title/description guidance, internal-link targets by
   native content ID, structured-field targets, conversion goal, and measurable success criteria.
   Treat word count and competitor coverage as evidence, not mandatory imitation targets.
6. Define every needed image by purpose, placement, dimensions/aspect ratio, source or generation
   guidance, factual constraints, alt-text intent, caption need, and native schema field. Do not add
   decorative media merely to satisfy a count.
7. If applying changes, use the narrowest Dineway content/SEO/media/settings path and verify.

## Content loop artifact

When the master Content Optimization Skill invokes this Skill, write
`.dineway/content/work/<opportunity-id>/brief/brief.md`. Bind it to the exact opportunity,
collection, locale, byline, optional existing content ID/translation group, current native schema
fingerprint, and Research fingerprint. Every required section or claim must cite Research source or
observation IDs. The Brief must distinguish required scope from optional ideas and explicit
exclusions so Draft generation cannot silently expand unsupported material.

Do not create a hosted Brief object, CMS row, Assignment, or generated Draft from this Skill. Return
to the master Skill after writing the artifact so native state and fingerprints can be rescanned.

## Boundaries

- Do not publish generated content. Produce a Draft apply plan; native review and release
  authorization govern later scheduling/publication.
- Do not invent menu items, hours, awards, staff bios, reviews, prices, or local facts.
- Do not use provider BYOK credentials or third-party provider MCP servers. Local bounded crawl,
  Browser Use, and Dineway provider MCP/CLI evidence are allowed under the shared boundaries.
- Preserve existing URLs unless the plan includes redirects.

## Output

Use the root `dineway-seo` output contract. Include `Search Intent / Audience`, `Evidence Used`, `Recommended Dineway Changes`, `Provider Calls Used`, `Skipped or Risky Claims`, and `Verification Plan`.

Inside the Content Optimization loop, the required output is the artifact above; summarize its
evidence, scope, blockers, and fingerprint in the response rather than substituting a prose-only
brief.
