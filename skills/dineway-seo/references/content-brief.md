# Content Brief Workflow

Use this for new pages/posts or improving existing Dineway content.

## Inputs

- Target keyword/topic and geography.
- Existing URL/content item when improving a page.
- Business model, audience, offer, and conversion goal.
- Current Dineway site-context briefing, brand voice, and SEO settings.
- Relevant collections and fields.

## Evidence

Prefer this order:

1. Current Dineway content and SEO metadata.
2. Site context, settings, schema, and internal links.
3. DataForSEO organic SERP for live competitors and SERP features.
4. Firecrawl scrape/map for the target page and selected competitor pages.
5. Public facts from cited sources.

Filter SERP competitors before analysis. Exclude directories, social networks, forums, maps, app stores, generic encyclopedias, irrelevant marketplaces, login/admin pages, PDFs unless the page type demands them, and direct non-business noise. Keep real competing pages and useful intent references.

## Brief Structure

- Search intent: informational, commercial, transactional, local, navigational, or mixed.
- Page type: homepage, service, local landing, menu/category, blog, comparison, roundup, review, guide, FAQ support page, or news/update.
- Primary and secondary keywords with natural usage guidance.
- Title and meta description options.
- H1 and heading outline.
- Required evidence, facts, examples, and information gain.
- Internal links to existing Dineway pages/content.
- Media needs with alt text.
- Schema recommendations from `schema-jsonld.md`.
- Draft-first Dineway write targets.

## Dineway Adaptation

- For restaurants, ground copy in real categories, location, menu, reviews, place data, media, and service flags.
- Do not invent opening hours, menu items, awards, chef bios, press, or FAQs.
- If source data is thin, write a concise content plan and identify missing facts instead of padding.
- Prefer updating `hasSeo` metadata and content fields before code patches.
- For existing pages, preserve the current URL unless the brief explicitly includes a redirect plan.

## Output

Return a brief with:

- `Summary`
- `Intent`
- `Competitor/Reference Pages`
- `Recommended Outline`
- `SEO Metadata`
- `Internal Links`
- `Media`
- `Schema`
- `Dineway Apply Plan`
- `Verification`
