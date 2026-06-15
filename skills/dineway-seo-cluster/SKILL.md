---
name: dineway-seo-cluster
description: Plan Dineway SEO topic clusters, hub-and-spoke architectures, internal link matrices, local intent clusters, and draft page/post targets. Use for seed keywords, content architecture, SERP-overlap clustering, pillar pages, spoke pages, and measurement plans.
---

# Dineway SEO Cluster

Use this child skill for topic clusters and content architecture. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

## Required References

- Load `../dineway-seo/references/topic-cluster.md`.
- Load `../dineway-seo/references/apply-loop.md` before recommending or applying Dineway changes.
- Load `../dineway-seo/references/security-boundaries.md` before using provider evidence or external-source recommendations.
- Load `../dineway-seo/references/provider-selection.md` when live keyword or SERP overlap evidence may be needed.
- Load `../dineway-seo/references/dataforseo.md` when using keyword suggestions or SERP results.

## Workflow

1. Inventory current Dineway collections, existing pages/posts, internal links, site context, and SEO settings.
2. Expand the seed into head terms, modifiers, local variants, comparison terms, questions, and seasonal/event variants.
3. Cluster by intent and SERP overlap, not wording alone.
4. Choose hub pages only when they can satisfy broad intent and naturally link to distinct spokes.
5. Map each hub/spoke to an existing Dineway collection or a proposed schema/content target.
6. If applying changes, create or update drafts first and verify links/metadata.

## Boundaries

- Do not create doorway pages or thin local pages.
- Do not write local HTML maps or unrelated local artifacts.
- Do not use local provider credentials, MCP provider tools, or local fetch/parse/render commands.
- Skip terms when there is no distinct source-backed Dineway value.

## Output

Use the root `dineway-seo` output contract. Include `Cluster Map`, `Hub Recommendation`, `Spoke Pages`, `Internal Link Matrix`, `Dineway Content Targets`, `Provider Evidence`, `Skipped Terms`, and `Measurement Plan`.
