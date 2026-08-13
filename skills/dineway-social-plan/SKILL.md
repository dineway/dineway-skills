---
name: dineway-social-plan
description: Create a local social content plan from an existing Dineway restaurant site. Use when turning site, menu, review, local SEO, or restaurant context into campaign briefs, captions, posting suggestions, and source-backed social planning without publishing or calling paid social-trending APIs.
---

# Dineway Social Plan

Use this skill to produce a local, owner-reviewable social media plan from already available Dineway site evidence.

This is a planning workflow only. It does not post to social platforms, does not automate social accounts, and does not add billing, checkout, credit, upgrade, or membership logic to generated sites or Dineway Admin.

## Boundaries

- Do not call paid Social Media Trending APIs or scrape social platforms for trend data.
- Do not invent menu items, prices, offers, awards, staff names, hours, reviews, ratings, events, or local facts.
- Do not publish generated captions or write back to Dineway content unless the user explicitly asks for a separate apply step.
- Do not require a local dev server for unpublished sites.
- Do not use generated-site Admin account state, subscription state, billing state, credits, or upgrade status as inputs.
- Use only evidence from the deployed public site, local Dineway SQLite database, checked-in content/seed files, and user-provided notes.

## Source Selection

1. Locate the project root from the current working directory. Prefer the directory containing `.dineway/deploy.json`, `src/live.config.ts`, `astro.config.mjs`, or `package.json`.
2. If `.dineway/deploy.json` exists and contains `targets.forgeway.siteDomain`, use the deployed public site as the primary source:
   - Build `https://${siteDomain}/`.
   - Fetch the homepage and likely public pages such as `/menu`, `/reviews`, `/gallery`, `/blog`, `/news`, `/about`, and `/contact` when linked or present.
   - Record each fetched URL as a source reference.
3. If no deployed site domain is available, use local SQLite directly:
   - Prefer an explicit Dineway database URL from project env files when present.
   - Otherwise try `data.db`, `.dineway/data.db`, `db.sqlite`, and `database.sqlite` in the project root.
   - Open the database with Dineway core database connectors such as `createDatabase({ url: "file:<path>" })`.
   - Read site settings from `options` keys prefixed with `site:`.
   - Read collection definitions from `_dineway_collections`; for each relevant enabled collection, query its `ec_<slug>` table.
   - Prioritize restaurant identity, menu items, reviews/testimonials, posts/news/events, gallery captions/alt text, SEO titles/descriptions, and site context entries.
   - Record local database path and table names as source references.
4. If neither deployed data nor a readable local database exists, stop and ask for a site path, database path, deployed URL, or source notes.

## Evidence Extraction

Extract only claims that are backed by sources:

- restaurant name, tagline, cuisine, location, and customer-facing voice;
- menu highlights, seasonal or high-margin items, and dietary-friendly items when present;
- review or testimonial themes without quoting private or unsupported reviewer text;
- local SEO themes such as neighborhood, occasions, service types, and nearby intent;
- existing blog/news/event hooks;
- image or gallery subjects that can support visual post ideas.

For every major recommendation, keep a short source note such as `deployed:/menu`, `db:ec_menu_items`, `db:options(site:title)`, or `user-provided`.

## Planning Workflow

1. Define the campaign goal and audience from evidence: weekday covers, catering inquiries, tasting menu interest, local discovery, review recovery, event promotion, or another source-backed goal.
2. Choose channels from available evidence. Default to Instagram, Facebook, and Google Business Profile when the user has not specified channels.
3. Create a 7-day plan unless the user asks for a different duration.
4. For each planned post, include:
   - channel;
   - objective;
   - caption draft;
   - visual direction using existing site/gallery/menu evidence;
   - call to action;
   - source references.
5. Include posting-time suggestions based on restaurant use cases, not trend APIs:
   - lunch intent: late morning;
   - dinner intent: mid-afternoon;
   - weekend bookings: Thursday or Friday afternoon;
   - events/catering: early week planning windows.
6. Add an owner-review checklist for factual approval before posting.

## Output File

Create the output directory if needed and write:

```txt
./output/social-plans/YYYY-MM-DD-{slug}.md
```

Use a lowercase kebab-case slug from the restaurant/site name or campaign goal. If no name is known, use `dineway-social-plan`.

The Markdown must include:

- `# Social Plan: {restaurant or campaign name}`
- `Generated`
- `Campaign Brief`
- `Evidence Used`
- `Platform Copy`
- `Posting-Time Suggestions`
- `Source References`
- `Owner Review Checklist`

After writing the file, print the output path and a concise summary with the number of posts, channels, and main evidence sources.

## Dry-Run Validation

Before finalizing, verify:

- deployed-site mode works against a fixture or existing `.dineway/deploy.json` with `siteDomain`;
- unpublished mode works against a local SQLite fixture without starting a dev server;
- the Markdown contains campaign brief, platform copy, posting-time suggestions, and source references;
- no paid social-trending API, provider credential, checkout, billing, credits, or generated-site Admin dependency is used.
