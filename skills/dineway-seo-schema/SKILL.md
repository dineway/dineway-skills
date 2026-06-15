---
name: dineway-seo-schema
description: Audit, plan, generate, or validate Dineway SEO schema and JSON-LD. Use for Restaurant, LocalBusiness, Organization, WebPage, Article, ImageObject, BreadcrumbList, ItemList, Product/Offer, Menu schema, deprecated rich-result checks, and Dineway schema apply plans.
---

# Dineway SEO Schema

Use this child skill for schema and JSON-LD work. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

## Required References

- Load `../dineway-seo/references/schema-jsonld.md`.
- Load `../dineway-seo/references/apply-loop.md` before recommending or applying Dineway changes.
- Load `../dineway-seo/references/security-boundaries.md` before using external-source evidence or recommending Astro patches.
- Load `../dineway-seo/references/content-brief.md` only when schema is part of a broader content plan.

## Workflow

1. Inventory current Dineway facts: content item fields, SEO metadata, media URLs, site settings, page metadata helpers, and existing JSON-LD contributors.
2. Detect existing schema where available and compare it to visible page facts.
3. Choose active schema types only when required facts are present.
4. Record missing facts instead of fabricating values.
5. Prefer Dineway settings, SEO Graph contributors, page metadata helpers, and media records before Astro patches.
6. Verify rendered JSON-LD parses and matches visible content.

## Boundaries

- Do not create schema solely to chase removed or restricted rich results.
- Do not invent ratings, reviews, opening hours, coordinates, prices, availability, images, or organization details.
- Do not inject time-sensitive schema only through delayed client JavaScript.
- Do not use local provider credentials, MCP provider tools, or local fetch/parse/render commands.

## Output

Use the root `dineway-seo` output contract. Include `Detected Schema`, `Recommended Schema`, `Required Facts`, `Missing Facts`, `Dineway Apply Target`, `Validation Steps`, and `Skipped or Risky Claims`.
