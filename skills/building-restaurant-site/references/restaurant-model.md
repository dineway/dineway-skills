# Restaurant Content and CMS Boundary Model

Use this reference for restaurant-specific IA, required content columns, Astro-first page planning, and Dineway CMS boundaries after `enrich-place-details` saves `places/${placeId}.json`. For Dineway mechanics, load the separate local references: `configuration.md`, `schema-and-seed.md`, `querying-and-rendering.md`, and `site-features.md`.

Do not load the generic Dineway site-building skill, templates, or demos as reference material. Build from the enriched place JSON and the target project's actual files.

## Build Order

1. Plan IA and visual direction from the real place JSON.
2. Download usable restaurant photos to local assets.
3. Use `$frontend-design` to build the visible Astro pages/components freely from the real data and local assets.
4. After the design works, add the required Dineway CMS-managed columns.
5. Seed Blog, News, Menu, Reviews, and Gallery from real reviews, posts, videos, menu signals, and downloaded images.

Do not stop after step 3. The final deliverable must include Dineway CMS-managed Blog, News, Menu, Reviews, and Gallery wired into the Astro site.

Before step 3, complete a `Data Utilization Matrix` in `.plan/<restaurant-slug>/findings.md`. It must cover every present enriched field family listed in `data-mapping.md` and classify it as public page copy, CMS content source, media source, SEO/schema input, design direction, internal guardrail, or intentionally unused with a reason.

## Required CMS Columns

For every generated restaurant site, keep promotional pages outside CMS but create these Dineway CMS-managed columns:

- Static Astro: Home, About/Snapshot, Contact/Location, rating trust signals, hero, CTAs, JSON-LD, and layout chrome.
- Dineway CMS: Blog, News, Menu, Reviews, and Gallery.

Do not create a generic `pages` collection just to manage the homepage or one-off marketing sections.

## Required Public Pages

The final public site must have distinct crawlable top-level pages at `/`, `/menu`, `/reviews`, `/gallery`, `/blog`, `/news`, and `/contact`.

Homepage previews may exist, but they do not satisfy the required pages. Primary navigation and footer must link to `/menu`, `/reviews`, `/gallery`, `/blog`, and `/news`. Homepage anchor links such as `/#menu`, `/#reviews`, or `/#gallery` may only be secondary preview links; they must not replace the top-level page links.

Each required CMS collection must contain seeded published content, and the corresponding public page must query and render that collection. Static or hardcoded fallback content alone does not satisfy a required CMS-managed column.

## Source Rules for Required Columns

- Blog: extract valuable themes from reviews, `ugcPosts`, restaurant place posts, and place videos. Rewrite from the restaurant's point of view and tone while preserving factual grounding.
- News: use menu-update signals, `ugcPosts`, and restaurant place posts. If the source does not prove a date, launch, seasonal special, or new item, write evergreen update-style content without fake recency.
- Menu: use real menu/menu-update data when present and review-backed dish, flavor, service, or dining-experience themes. Specific dish names are allowed only when present in reviews, posts, videos, or structured menu data.
- Reviews: curate distinctive real reviews to show the restaurant's character, service, atmosphere, food, and local trust. Keep quotes short and attributed when quoted.
- Gallery: select downloaded images that represent food quality, space, service, atmosphere, or signature visual details. Do not use generic or low-quality images just to fill a grid.

When richer enriched fields are present, use them before falling back to synthesized content:

- Menu uses `menuList` item names/descriptions/sections and `menuImages`.
- Reviews uses `reviews`, `extImageReviews`, `reviewImageList`, and `reviewVideoList`.
- Blog uses themes from `reviews`, `ugcPosts`, post media, and videos. When `ugcPosts` exists, include at least one customer-safe article/theme derived from it.
- News uses `ugcPosts`, post timestamps, post media, and real menu-update signals. When `ugcPosts` exists, include at least one customer-safe update-style item derived from it, without pretending it is an official announcement.
- Gallery uses downloaded place, review, menu, post, and video-still media with customer-safe captions.

## Section Planning

Choose sections from fields that are actually present:

- Identity: `displayName`, primary category, city, formatted address.
- Trust: `rating`, `userRatingCount`, distinctive reviews, editorial review themes grounded in real review text.
- Visits: phone, website, Google Maps URL, directions link, review link, coordinates, opening hours, payment, accessibility, restroom, lunch/dinner, groups, reservations, dine-in/takeout/delivery, and other service flags when present.
- Location context: `postalAddress`, `addressComponents`, `addressDescriptor.areas`, and `addressDescriptor.landmarks` for concise arrival/local-area guidance.
- Media: local downloaded place/review/menu/post/video-still media for Astro design; uploaded Dineway media only for CMS-managed images.
- Local SEO: address, geo coordinates, hours, phone, category/type labels, business status, same-as links, map action links, and local descriptors only when present.

## Page Responsibilities

- Home (`/`): Astro page with hero, category/location summary, rating/review count, key CTAs, review highlights, and gallery preview.
- Blog (`/blog`): CMS collection with review/`ugcPosts`/post/video-derived restaurant perspective articles.
- News (`/news`): CMS collection with verifiable updates from menu-update signals, `ugcPosts`, and place posts.
- Menu (`/menu`): CMS collection or structured CMS content with review-backed menu introduction and any real menu items that are present.
- Reviews (`/reviews`): CMS collection or seeded content with selected real reviews and theme summaries.
- Gallery (`/gallery`): CMS collection with representative downloaded and uploaded images.
- Contact/Location (`/contact`): Astro page with NAP, phone, maps link, coordinates, hours if present, route/call CTAs.

## Data-Density Decisions

- Sparse data: still include Blog, News, Menu, Reviews, and Gallery, but keep each concise and explicitly grounded in the limited source material.
- Reviews plus contact data: use the strongest reviews to drive Blog, Menu, and Reviews themes.
- Multiple downloaded photos: use the best images for Gallery and visual previews.
- No structured menu data: still include Menu as a review-backed menu introduction, but do not invent dish cards, prices, ingredients, or availability.

## Content Rules

When creating or updating Astro pages or `seed/seed.json`:

- Preserve exact factual fields such as name, address, phone, website, hours, rating, review count, coordinates, and Google Maps URL.
- Do not invent menu items, awards, social accounts, reservation links, delivery options, opening hours, or accessibility features.
- Use review, post, and video content carefully: summarize visible themes, keep quotes short, and omit claims that cannot be tied back to the saved JSON.
- Apply the `Brand Voice & Copy Tone Brief` from `findings.md`: use first-person restaurant perspective where natural, transform review praise into confident restaurant-owned copy, avoid hedging, keep warmth polished rather than casual, and keep descriptions concise and scannable.
- Before writing any public title, excerpt, body, caption, CTA, or metadata string, apply the customer visibility gate from `seo-and-design.md`. A line is allowed only when it is useful and appropriate for a real guest to read.
- Use local downloaded assets in static Astro pages. Use uploaded Dineway media values in CMS-managed content fields.
- Prefer fewer, better-supported pages over a large generic restaurant site.
- Schema-only CMS collections are incomplete. If a required collection has no published seed content or the public page does not render it, the restaurant site is not done.
- Do not publish internal source labels, verification caveats, implementation notes, or placeholders in public pages. Keep those notes in `.plan`, not in rendered site content.
