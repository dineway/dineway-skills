---
name: building-restaurant-site
description: "Build high-quality Astro-first restaurant websites from real enriched place data, then integrate Dineway CMS for required restaurant columns: Blog, News, Menu, Reviews, and Gallery. Use when the user provides a restaurant name and city, optionally a placeId, and wants a polished Dineway/Astro restaurant site with local media, local SEO, JSON-LD, review-derived content, and production-grade UI. Requires restaurant name and city before execution."
---

# Building a Restaurant Site

Use this skill to create a polished Astro-first restaurant site from real place data, then bring the required restaurant content columns under Dineway CMS management. It is a self-contained restaurant-site workflow with data enrichment, review/theme extraction, content planning, media handling, reputation signals, local SEO, visual design, and CMS boundary planning.

## Hard Input Gate

Required user inputs:

- Restaurant name
- City, region, or city/country

Optional input:

- Google/Dineway `placeId`

If the restaurant name or city is missing, stop immediately. Do not fetch data, create files, infer the city, or start implementation. Ask for the missing value in one concise sentence. A `placeId` improves matching but is never required.

## Required Workflow

1. **Load supporting guidance**
   - Use `$enrich-place-details` for restaurant lookup and enrichment. Depend on that skill's public inputs and outputs, not on its internal files.
   - Invoke `$brainstorming` before deciding information architecture, visual direction, and CMS boundaries. Use it to compare options, then automatically adopt the best recommendation; do not merely imitate its process or ask the user to choose.
   - Use `$frontend-design` for the visible Astro site. If it is not already loaded, explicitly read the local `skills/frontend-design/SKILL.md` guidance before writing visible layout, components, or CSS.
   - Do not read, inspect, copy, or adapt Dineway `templates/` or `demos/` as reference material unless the user explicitly asks for that exact source.
   - If the current workspace already contains demo/template-like restaurant files, treat them as replaceable target files, not as a reference design or content source.

2. **Initialize planning files**
   - Create `.plan/<restaurant-slug>/task_plan.md`.
   - Create `.plan/<restaurant-slug>/findings.md`.
   - Create `.plan/<restaurant-slug>/progress.md`.
   - Keep them current throughout the run. Record data fields, missing fields, image decisions, IA decisions, implementation steps, validation results, and fallback choices.

3. **Fetch enriched place details**
   - Invoke `$enrich-place-details` with the restaurant name and city.
   - If the user provided `placeId`, pass it through as the optional authoritative place id.
   - Use the `placeDetailsPath` returned by `$enrich-place-details` and inspect the saved `places/${placeId}.json`.
   - Inspect reviews, `ugcPosts`, place posts, place videos, and photo/image lists before planning content.
   - Treat that JSON file as the source of truth. Do not invent website, opening hours, menu items, social links, FAQ, awards, or services that are absent.

4. **Normalize data and brainstorm the site**
   - Read [references/data-mapping.md](references/data-mapping.md).
   - Optional helper:

   ```bash
   node skills/building-restaurant-site/scripts/restaurant_site_data.js \
     summarize places/PLACE_ID.json \
     --out .plan/restaurant/site-summary.json
   ```

   - Invoke `$brainstorming` to compare 2-3 information architecture, visual direction, and CMS boundary options, then adopt the best option automatically. Do not ask the user to choose among design options.
   - Only stop for user input when execution is impossible, such as missing restaurant name/city or an unresolved place match.
   - Hard gate: before writing any Astro or Dineway implementation files, `findings.md` must contain a `Design Comparison` section with 2-3 options, pros/cons, the selected recommendation, and how `$frontend-design` will express the chosen direction. If that section is missing, stop implementation and create it.
   - Treat the chosen visual direction as the design brief for `$frontend-design`.
   - The public site must include Blog, News, Menu, Reviews, and Gallery columns. Data density controls depth and layout, not whether these columns exist.
   - Extract content themes from real reviews, `ugcPosts`, place posts, place videos, categories, service flags, and downloaded images. Record the extracted themes and source fields in `findings.md`.
   - Create a `Data Utilization Matrix` in `findings.md` before design. For every present enriched field family from [references/data-mapping.md](references/data-mapping.md), record how it will be used: public page copy, CMS content source, gallery/media source, local SEO/JSON-LD, CTA/action link, design direction, or internal guardrail. If a present field will not be used, record the reason.
   - Hard gate: do not design or seed content until `Data Utilization Matrix` covers identity/category, address/location descriptors, rating/reviews, menu/menu images, `ugcPosts`, other posts, videos, image lists, service flags, payment/accessibility, map action links, and SEO/schema fields when present.
   - Create a `Brand Voice & Copy Tone Brief` in `findings.md` before generating public copy. It must define the restaurant's guest-facing voice, first-person usage, confidence level, warmth level, description length, and review-to-restaurant-copy transformation rules from [references/seo-and-design.md](references/seo-and-design.md).
   - Hard gate: do not write Astro page copy or CMS seed content until `Brand Voice & Copy Tone Brief` exists and is consistent with the customer visibility filter.
   - Before generating public copy or CMS seed content, apply the **customer visibility gate** from [references/seo-and-design.md](references/seo-and-design.md). For every planned section/article/menu/review/gallery caption, ask internally: "Is this useful and appropriate for a real restaurant guest to see on the public website?" Generate only content that passes. Keep source analysis, caveats, provenance, verification notes, and implementation rules in `.plan` only.
   - Hard gate: before writing public Astro content or CMS seed entries, `findings.md` must contain a `Customer Visibility Filter` section listing customer-safe themes, internal-only notes, and rejected phrasing patterns. If that section is missing, stop implementation and create it.
   - Record the chosen structure and rationale in `findings.md`.

5. **Download local images before design**
   - Read [references/media-pipeline.md](references/media-pipeline.md).
   - Extract image candidates from place, menu, review, post, video, and selected-place media fields according to [references/media-pipeline.md](references/media-pipeline.md).
   - Download only usable image URLs to local files before designing. Never put a Google photo reference, API resource name, or remote photo URL directly in site markup or Dineway content.
   - Use local image assets for the Astro-first design.
   - Upload images to Dineway for the required CMS-managed Gallery and for Blog, News, Menu, or Reviews entries that use images.
   - If no representative images can be downloaded, record the blocker and ask for restaurant photos before final delivery because Gallery is required. If CMS upload fails, keep the static Astro design and omit the CMS-managed image field until upload works.

6. **Design and build the Astro-first site**
   - Use `$frontend-design` to implement the visible restaurant site from the chosen design brief, enriched JSON, and downloaded local images.
   - Build promotional pages and sections as Astro pages/components first: Home, About/Snapshot, Location/Contact, trust signals, CTAs, SEO metadata, and JSON-LD.
   - Public Astro copy must be guest-facing restaurant copy. Do not render planning language, audit language, source labels, limitations, "real review" explanations, or notes about what was not verified.
   - Include visible navigation to Blog, News, Menu, Reviews, and Gallery.
   - Do not constrain the first design pass to Dineway CMS schemas, seed files, or editable blocks.
   - Keep static promotional content as standalone Astro code when it does not need ongoing CMS management.
   - This stage is not a deliverable stopping point. Never stop after static Astro output or offer to continue later.
   - Shared layout, navigation, footer, internal links, and SEO metadata must be consistent across pages.

7. **Add Dineway CMS only where content needs management**
   - Read [references/restaurant-model.md](references/restaurant-model.md).
   - For implementation details, read only the relevant local Dineway references from this skill:
     - [references/configuration.md](references/configuration.md)
     - [references/schema-and-seed.md](references/schema-and-seed.md)
     - [references/querying-and-rendering.md](references/querying-and-rendering.md)
     - [references/site-features.md](references/site-features.md)
   - Create the site independently for this restaurant. Do not search for, copy, adapt, or reference Dineway templates or demo sites.
   - Blog, News, Menu, Reviews, and Gallery are required Dineway CMS-managed columns.
   - Blog content must come from valuable themes extracted from reviews, `ugcPosts`, restaurant place posts, and place videos, rewritten from the restaurant's point of view without unsupported claims.
   - News content must come from menu-update signals, `ugcPosts`, restaurant place posts, and verifiable update-style source material. Do not fabricate dates, launches, specials, or announcements.
   - Menu content must combine real menu/menu-update signals with review-backed dish, flavor, service, or dining-experience themes. Do not invent dishes, prices, ingredients, or availability.
   - Reviews content must feature selected real reviews and use them to reinforce the restaurant's character and authenticity.
   - Gallery content must use representative downloaded images that improve the restaurant's perceived quality; inspect and select images before upload.
   - Every generated CMS title, excerpt, body, caption, CTA, and metadata string must pass the customer visibility gate before it is written to seed/content files.
   - Do not put hero, about, NAP/contact, static review summaries, or one-off promotional sections into Dineway CMS just because the project uses Dineway.
   - Upload local images into Dineway before using them in CMS-managed image fields; use `dineway/ui` `Image` for those Dineway image objects.
   - Preserve the completed Astro design and wire CMS content into it only at the boundaries selected above.
   - Hard completion gate: do not send a final answer until Dineway collections/seed/content, media upload, queries, and rendered routes/sections for Blog, News, Menu, Reviews, and Gallery are implemented and validated.

8. **Validate SEO, design, CMS boundaries, and runtime**
   - Read [references/seo-and-design.md](references/seo-and-design.md).
   - Each page gets one `<h1>`, page-specific title and description, crawlable internal links, mobile-first responsive layout, and lazy-loaded images.
   - Add `Restaurant` or `LocalBusiness` JSON-LD only with fields present in the enriched JSON.
   - Verify static Astro promotional pages still render without CMS content.
   - Validate seed/content only for the CMS-managed pieces that were actually added.
   - Public copy must not expose internal rules, provenance labels, verification disclaimers, implementation notes, or placeholders. Remove phrases such as "source:", "based on real reviews", "from public review text", "review-visible facts", "not verified", "replace later", "placeholder", "extracted", "scraped", "verified facts", and similar wording from rendered pages.
   - Search the rendered/source content for the rejected phrasing patterns recorded in `Customer Visibility Filter`; revise any match into customer-safe restaurant copy or remove it.
   - Run the relevant Dineway typecheck/lint gates, start the dev server with `bgproc` when needed, and browser-test the rendered pages.
   - Never finish with "I can continue to Dineway CMS if you want". The Dineway CMS integration is required for completion.

## Helper Script

`scripts/restaurant_site_data.js` is a Node.js helper for repeated data tasks:

```bash
# Summarize real place data and produce a planning input.
node skills/building-restaurant-site/scripts/restaurant_site_data.js summarize places/PLACE_ID.json

# Download usable image URLs from the enriched JSON.
node skills/building-restaurant-site/scripts/restaurant_site_data.js download places/PLACE_ID.json \
  --out assets/restaurant-name \
  --max 6 \
  --manifest .plan/restaurant/downloaded-media.json

# Upload downloaded files for required CMS-managed Gallery and any CMS entry that uses images.
node skills/building-restaurant-site/scripts/restaurant_site_data.js upload \
  .plan/restaurant/downloaded-media.json \
  --url http://localhost:4321 \
  --out .plan/restaurant/uploaded-media.json
```

Use the helper when it saves time, but still inspect the JSON and make the final content/design decisions yourself.

## Reference Documents

| File                                                                             | Use                                                             |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [references/data-mapping.md](references/data-mapping.md)                         | Field mapping from `enrich-place-details` payloads              |
| [references/media-pipeline.md](references/media-pipeline.md)                     | Local photo download and Dineway upload workflow                |
| [references/restaurant-model.md](references/restaurant-model.md)                 | Required columns, Astro-first design, and CMS boundary rules    |
| [references/configuration.md](references/configuration.md)                       | Local Dineway/Astro configuration and runtime setup             |
| [references/schema-and-seed.md](references/schema-and-seed.md)                   | Seed schema, fields, menus, sections, media, and validation     |
| [references/querying-and-rendering.md](references/querying-and-rendering.md)     | Dineway content queries, Portable Text, Image, and cache rules  |
| [references/site-features.md](references/site-features.md)                       | Settings, menus, taxonomies, widgets, search, and SEO helpers   |
| [references/seo-and-design.md](references/seo-and-design.md)                     | Local SEO, JSON-LD, IA, copy, and visual direction rules        |
