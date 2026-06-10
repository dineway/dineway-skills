---
name: building-restaurant-site
description: "Build high-quality Astro-first restaurant websites from real enriched place data and the restaurant's official websiteUri when present, then integrate Dineway CMS for required restaurant columns: Blog, News, Menu, Reviews, and Gallery. Use when the user provides a restaurant name and city, optionally a placeId, and wants a polished Dineway/Astro restaurant site with local media, local SEO, JSON-LD, review-derived content, official-site facts, and production-grade UI. Requires restaurant name and city before execution."
---

# Building a Restaurant Site

Use this skill to create a polished Astro-first restaurant site from real place data and the official restaurant website when `websiteUri` is present, then bring the required restaurant content columns under Dineway CMS management. It is a self-contained restaurant-site workflow with data enrichment, official-site extraction, review/theme extraction, content planning, media handling, reputation signals, local SEO, visual design, and CMS boundary planning.

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
   - Treat that JSON file as the primary structured source of truth. Do not invent website, opening hours, menu items, social links, FAQ, awards, or services that are absent from the enriched JSON or the official website extraction below.

4. **Extract official website context when `websiteUri` is present**
   - If `placeDetails.websiteUri` is present, fetch the official website before brainstorming, content planning, media curation, or CMS seeding.
   - Normalize the URL, confirm it is an HTTP(S) URL, and record it in `.plan/<restaurant-slug>/findings.md`.
   - Crawl lightly and stay focused: homepage plus useful first-party pages linked from primary navigation such as Menu, About, Contact, Reservations, Order, Catering, Events, Gallery, Blog, News, or Press. Default to 6-10 pages. Stay on the same origin unless the official site intentionally links to a first-party ordering, reservation, menu, or social profile needed for guest actions.
   - Extract only useful, customer-safe, restaurant-owned facts: brand tagline/voice, exact menu item names/descriptions/prices when published, hours, phone/email, address notes, direct reservation/order links, catering/private-event details, accessibility/service notes, gift cards, official social links, newsletter links, awards/press mentions, announcements, FAQs, and first-party image candidates.
   - Do not copy long website paragraphs. Paraphrase marketing copy into fresh restaurant-site copy. Preserve exact factual strings only where accuracy matters, such as names, addresses, phone numbers, menu item names, prices, hours, URLs, and short attributed review or press snippets.
   - Save concise notes to `.plan/<restaurant-slug>/official-website.md` or an equivalent section in `findings.md` with source page URLs, extracted facts, rejected/internal-only material, and fetch failures.
   - Conflict handling: use the official site as authoritative for restaurant-owned facts, menu details, direct action links, brand voice, catering/events, and current announcements. Preserve enriched JSON for Google rating/review counts, Google Maps links, and place media. For NAP or hours conflicts, record the discrepancy and publish only the value with clear support; if neither is clearly current, use neutral visit guidance and avoid the conflicting detail.
   - If the site is unavailable, blocked, empty, unrelated, or clearly not the restaurant's official site, record the reason and continue from the enriched JSON. Do not ask the user unless the official site is required to resolve an otherwise blocking place match.

5. **Normalize data and brainstorm the site**
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
   - Extract content themes from real reviews, `ugcPosts`, place posts, place videos, categories, service flags, official website pages, and downloaded images. Record the extracted themes and source fields in `findings.md`.
   - Create a `Data Utilization Matrix` in `findings.md` before design. For every present enriched field family from [references/data-mapping.md](references/data-mapping.md), record how it will be used: public page copy, CMS content source, gallery/media source, local SEO/JSON-LD, CTA/action link, design direction, or internal guardrail. If a present field will not be used, record the reason.
   - When `websiteUri` is present, the `Data Utilization Matrix` must include an `Official website` row covering fetched pages, useful facts, action links, menu signals, media candidates, and rejected or unavailable material.
   - Hard gate: do not design or seed content until `Data Utilization Matrix` covers identity/category, address/location descriptors, rating/reviews, menu/menu images, `ugcPosts`, other posts, videos, image lists, service flags, payment/accessibility, map action links, SEO/schema fields, and official website context when present.
   - Create a `Brand Voice & Copy Tone Brief` in `findings.md` before generating public copy. It must define the restaurant's guest-facing voice, first-person usage, confidence level, warmth level, description length, and review-to-restaurant-copy transformation rules from [references/seo-and-design.md](references/seo-and-design.md).
   - Use official website copy and imagery to refine brand voice, but keep the final copy original, concise, and guest-facing.
   - Hard gate: do not write Astro page copy or CMS seed content until `Brand Voice & Copy Tone Brief` exists and is consistent with the customer visibility filter.
   - Before generating public copy or CMS seed content, apply the **customer visibility gate** from [references/seo-and-design.md](references/seo-and-design.md). For every planned section/article/menu/review/gallery caption, ask internally: "Is this useful and appropriate for a real restaurant guest to see on the public website?" Generate only content that passes. Keep source analysis, caveats, provenance, verification notes, and implementation rules in `.plan` only.
   - Hard gate: before writing public Astro content or CMS seed entries, `findings.md` must contain a `Customer Visibility Filter` section listing customer-safe themes, internal-only notes, and rejected phrasing patterns. If that section is missing, stop implementation and create it.
   - Record the chosen structure and rationale in `findings.md`.

6. **Download local images and curate before design**
   - Read [references/media-pipeline.md](references/media-pipeline.md).
   - Extract image candidates from place, menu, review, post, video, selected-place media fields, and first-party official website images according to [references/media-pipeline.md](references/media-pipeline.md).
   - Download up to 20 candidates ranked by source priority and resolution signals. Never put a Google photo reference, API resource name, or remote photo URL directly in site markup or Dineway content.
   - After downloading, inspect the actual downloaded images to evaluate visual quality, content diversity, and resolution. Select 8-10 of the best images using the `select` subcommand or by editing the manifest.
   - Use selected local image assets for the Astro-first design.
   - Upload only selected images to Dineway for the required CMS-managed Gallery and for Blog, News, Menu, or Reviews entries that use images.
   - If no representative images can be downloaded, record the blocker and ask for restaurant photos before final delivery because Gallery is required. If CMS upload fails, keep the static Astro design and omit the CMS-managed image field until upload works.

7. **Design and build the Astro-first site**
   - Use `$frontend-design` to implement the visible restaurant site from the chosen design brief, enriched JSON, and downloaded local images.
   - Build promotional pages and sections as Astro pages/components first: Home, About/Snapshot, Location/Contact, trust signals, CTAs, SEO metadata, and JSON-LD.
   - Public Astro copy must be guest-facing restaurant copy. Do not render planning language, audit language, source labels, limitations, "real review" explanations, or notes about what was not verified.
   - Include visible navigation to Blog, News, Menu, Reviews, and Gallery.
   - Hard page gate: the final public site must have distinct crawlable top-level pages at `/`, `/menu`, `/reviews`, `/gallery`, `/blog`, `/news`, and `/contact`. Homepage previews may exist, but homepage sections or anchors do not satisfy these required pages.
   - Primary navigation and footer must link to `/menu`, `/reviews`, `/gallery`, `/blog`, and `/news`. Homepage anchor links such as `/#menu`, `/#reviews`, or `/#gallery` may only be secondary preview links; they must not replace the top-level page links.
   - Do not constrain the first design pass to Dineway CMS schemas, seed files, or editable blocks.
   - Keep static promotional content as standalone Astro code when it does not need ongoing CMS management.
   - This stage is not a deliverable stopping point. Never stop after static Astro output or offer to continue later.
   - Shared layout, navigation, footer, internal links, and SEO metadata must be consistent across pages.

8. **Add Dineway CMS only where content needs management**
   - Read [references/restaurant-model.md](references/restaurant-model.md).
   - For implementation details, read only the relevant local Dineway references from this skill:
     - [references/configuration.md](references/configuration.md)
     - [references/schema-and-seed.md](references/schema-and-seed.md)
     - [references/querying-and-rendering.md](references/querying-and-rendering.md)
     - [references/site-features.md](references/site-features.md)
   - Create the site independently for this restaurant. Do not search for, copy, adapt, or reference Dineway templates or demo sites.
   - Blog, News, Menu, Reviews, and Gallery are required Dineway CMS-managed columns.
   - Each required CMS collection must contain seeded published content, and the corresponding public page must query and render that collection. Static or hardcoded fallback content alone does not satisfy a required CMS-managed column.
   - Blog content must come from valuable themes extracted from reviews, `ugcPosts`, restaurant place posts, place videos, and official website pages, rewritten from the restaurant's point of view without unsupported claims.
   - News content must come from menu-update signals, `ugcPosts`, restaurant place posts, official website announcements, and other verifiable update-style source material. Do not fabricate dates, launches, specials, or announcements.
   - Menu content must combine real menu/menu-update signals, official website menu pages, and review-backed dish, flavor, service, or dining-experience themes. Do not invent dishes, prices, ingredients, or availability.
   - Reviews content must feature selected real reviews and use them to reinforce the restaurant's character and authenticity.
   - Gallery content must use representative downloaded images that improve the restaurant's perceived quality; inspect and select images before upload. First-party official website images may be used only after downloading locally, inspecting, and recording the source page.
   - Every generated CMS title, excerpt, body, caption, CTA, and metadata string must pass the customer visibility gate before it is written to seed/content files.
   - Do not put hero, about, NAP/contact, static review summaries, or one-off promotional sections into Dineway CMS just because the project uses Dineway.
   - Upload local images into Dineway before using them in CMS-managed image fields; use `dineway/ui` `Image` for those Dineway image objects.
   - Preserve the completed Astro design and wire CMS content into it only at the boundaries selected above.
   - Hard completion gate: do not send a final answer until the distinct required pages, primary nav/footer links, Dineway collections, seeded published content, media upload where relevant, collection queries, and rendered CMS-backed pages for Blog, News, Menu, Reviews, and Gallery are implemented and validated.

9. **Validate SEO, design, CMS boundaries, and runtime**
   - Read [references/seo-and-design.md](references/seo-and-design.md).
   - Each page gets one `<h1>`, page-specific title and description, crawlable internal links, mobile-first responsive layout, and lazy-loaded images.
   - Add `Restaurant` or `LocalBusiness` JSON-LD only with fields present in the enriched JSON or the official website extraction.
   - Verify static Astro promotional pages still render without CMS content.
   - Validate seed/content only for the CMS-managed pieces that were actually added.
   - Public copy must not expose internal rules, provenance labels, verification disclaimers, implementation notes, or placeholders. Remove phrases such as "source:", "based on real reviews", "from public review text", "review-visible facts", "not verified", "replace later", "placeholder", "extracted", "scraped", "verified facts", and similar wording from rendered pages.
   - Search the rendered/source content for the rejected phrasing patterns recorded in `Customer Visibility Filter`; revise any match into customer-safe restaurant copy or remove it.
   - Validate required routes and navigation before final delivery:

   ```bash
   for path in / /menu /reviews /gallery /blog /news /contact; do
     curl -fsSI "http://localhost:4321$path" >/dev/null
   done

   if rg 'href="/#(menu|reviews|gallery|blog|news)"' src/components src/layouts 2>/dev/null; then
     echo "Replace required shared nav/footer anchors with top-level page links." >&2
     exit 1
   fi
   ```

   If homepage preview anchors exist, keep separate top-level page links visible in nav/footer.
   - Validate seeded published content for each required CMS collection. For local SQLite projects, confirm each count is greater than zero:

   ```bash
   sqlite3 .dineway/data.db "
   select 'blog', count(*) from ec_blog where status = 'published'
   union all select 'news', count(*) from ec_news where status = 'published'
   union all select 'menu', count(*) from ec_menu where status = 'published'
   union all select 'reviews', count(*) from ec_reviews where status = 'published'
   union all select 'gallery', count(*) from ec_gallery where status = 'published';
   "
   ```

   - Run the relevant Dineway typecheck/lint gates, start the dev server with `bgproc` when needed, and browser-test the rendered pages.
   - Never finish with "I can continue to Dineway CMS if you want". The Dineway CMS integration is required for completion.

## Helper Script

`scripts/restaurant_site_data.js` is a Node.js helper for repeated data tasks:

```bash
# Summarize real place data and produce a planning input.
node skills/building-restaurant-site/scripts/restaurant_site_data.js summarize places/PLACE_ID.json

# Download usable image URLs from the enriched JSON (ranked by quality).
node skills/building-restaurant-site/scripts/restaurant_site_data.js download places/PLACE_ID.json \
  --out public/assets/restaurant-name \
  --max 20 \
  --manifest .plan/restaurant/downloaded-media.json

# After inspecting downloaded images, select the best 8-10.
node skills/building-restaurant-site/scripts/restaurant_site_data.js select \
  .plan/restaurant/downloaded-media.json \
  --pick 1,3,5,6,8,10,12,15 \
  --out .plan/restaurant/selected-media.json

# Upload selected files for required CMS-managed Gallery and any CMS entry that uses images.
node skills/building-restaurant-site/scripts/restaurant_site_data.js upload \
  .plan/restaurant/selected-media.json \
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
