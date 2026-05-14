# SEO and Design Rules

## Local SEO

Every generated page must have:

- One `<h1>`.
- Page-specific `<title>` and meta description.
- Crawlable navigation and contextual internal links.
- Mobile-first layout.
- Lazy-loaded non-critical images.

Use `Restaurant` JSON-LD when restaurant-specific fields are available. Use `LocalBusiness` only when the category is not clearly restaurant/cafe/food. Include only real fields:

- `name`
- `address`
- `telephone`
- `aggregateRating.ratingValue`
- `aggregateRating.reviewCount`
- `geo.latitude` and `geo.longitude`
- `url` or `sameAs` for Google Maps/website when present
- `servesCuisine` or category text when supported by real categories
- `openingHoursSpecification` only when real hours are present
- `image` only for downloaded local assets or uploaded media with a resolvable public URL

Use enriched local signals outside JSON-LD as well:

- Use `addressDescriptor.areas` and `addressDescriptor.landmarks` for concise local-area and arrival guidance.
- Use `googleMapsLinks.directionsUri`, `reviewsUri`, `photosUri`, and `writeAReviewUri` for appropriate CTAs.
- Use `businessStatus` as an internal guardrail and metadata signal; never imply the restaurant is open if the source says otherwise.
- Use `postalAddress`, `addressComponents`, coordinates, and category/type labels to make titles, descriptions, contact content, and local SEO specific.

## Information Architecture

Compare 2-3 options by invoking `$brainstorming` before implementation:

- Compact homepage plus required Blog, News, Menu, Reviews, and Gallery columns for sparse details.
- Separate Reviews, Menu, Blog, and News pages when source material deserves clearer scan paths.
- A visually rich Gallery route when downloaded image quality can lift perceived restaurant quality.

Choose automatically and record the reasoning. Do not ask the user to choose among design options. Stop for user input only when execution is impossible, such as missing restaurant name/city or an unresolved place match.

Build the visible experience Astro-first with `$frontend-design`. Keep promotional pages and sections as Astro code unless they need ongoing editorial management. Add Dineway CMS for required Blog, News, Menu, Reviews, and Gallery columns.

Blog must reinterpret review themes, `ugcPosts`, place posts, and videos from the restaurant's point of view. News must use menu-update signals, `ugcPosts`, and place posts. Menu must use real menu/menu-update data and review-backed food or experience themes. Reviews must use selected real reviews to create authenticity. Gallery must elevate the design with representative downloaded images, including usable `ugcPosts` media when present.

Implementation may not start until `.plan/<restaurant-slug>/findings.md` has a `Design Comparison` section with 2-3 options, pros/cons, selected recommendation, and frontend-design execution notes.

## Visual Direction

Infer style from real signals:

- Cafe, bakery, brunch, warm review language: refined local cafe.
- Restaurant, bar, fine dining, atmosphere/service-heavy reviews: editorial dining or luxury.
- Takeaway, fast service, convenience-heavy categories/reviews: casual urban service.

Use a 60-30-10 color system with restrained accents. Avoid generic template sections, oversized marketing heroes for operational pages, one-note palettes, fake decorative imagery, and visual claims not supported by data.

Actual UI implementation should produce a distinctive, production-ready restaurant site rather than a CMS-shaped wireframe. Let the restaurant data and downloaded images drive the design before adding Dineway CMS boundaries.

Use enriched media density to drive layout choices. Many strong place/review/menu images can justify a visual Gallery-led design; strong review/post text can justify editorial Blog/Review pathways; structured menu data can justify a Menu-forward navigation path.

## Copy

- Ground all copy in categories, location, ratings, review language, images, and service flags.
- Short synthesized summaries are allowed when they are clearly inferred from real data.
- Do not fabricate menu items, FAQs, social proof, external links, press, awards, chef bios, or opening hours.
- Keep review quotes attributed and concise.
- Do not fabricate post/video/news recency, menu updates, or specific dishes. If source material is thin, write concise source-grounded content instead of filler.
- Never expose internal provenance or rule text to visitors. Do not render labels such as "source:", "from public review text", "review-visible facts", "not verified", "for replacement later", "placeholder", "based on extracted comments", or "only from scraped reviews".
- Rewrite source-grounded insights into polished restaurant-facing copy. The public page should sound like the restaurant's editorial voice, not an audit trail.
- Validation must include searching rendered source/content for internal-rule phrases and replacing them before delivery.

## Brand Voice and Copy Tone

Before writing public Astro copy or CMS seed content, record a `Brand Voice & Copy Tone Brief` in `.plan/<restaurant-slug>/findings.md`. Base it on the restaurant category, reviews, `ugcPosts`, menu signals, service flags, location, and selected visual direction.

Apply these tone rules:

- Use first-person restaurant perspective when it sounds natural: "We serve", "Our kitchen", "Our team", and "Join us" are appropriate for owned promotional copy, CTAs, Menu introductions, About/Snapshot sections, Blog, and News. Use neutral third-person only for structured facts, attributed reviews, metadata, and legal/operational clarity.
- Translate review praise into confident restaurant copy instead of audit-style summaries. For example, a review signal like "Guests love our 8-grain dessert" can become "Indulge in our award-winning 8-grain dessert" only when the award claim is actually supported; otherwise write a confident supported version such as "Indulge in our guest-loved 8-grain dessert."
- Avoid hedging language in public copy. Do not write "appears to", "seems to", "may offer", "reviewers mention", or "based on reviews". Be definitive about offerings and experiences that are present in the source data; omit uncertain claims instead of qualifying them.
- Maintain warmth without becoming overly casual. Prefer polished hospitality language over slang, jokes, excessive exclamation, or social-media chatter.
- Keep descriptions concise and scannable. Favor short paragraphs, focused captions, crisp card copy, and specific menu/review highlights over long generic prose.
- Use the same voice across Home, Menu, Reviews, Gallery, Blog, News, Contact, SEO descriptions, and CMS excerpts. Adjust density by context, not personality.

## Customer Visibility Gate

Before generating any public Astro copy or CMS seed content, classify each planned content idea:

- **Customer-safe:** A real guest would naturally expect or benefit from seeing it on a restaurant website. Examples: what the dining experience feels like, signature dishes that exist in source data, useful visit guidance, atmosphere, service strengths, location context, concise attributed review highlights, and polished restaurant updates.
- **Internal-only:** Useful for planning but inappropriate for visitors. Examples: source/provenance labels, extraction notes, verification caveats, field names, scraper/API language, confidence notes, missing-data warnings, implementation TODOs, placeholders, and explanations that the copy comes from reviews/posts.
- **Reject or rewrite:** Any sentence that sounds like an audit trail, compliance rule, generation instruction, dataset limitation, or note to a future editor. Rewrite it into restaurant-facing copy only if the underlying fact is useful to guests; otherwise remove it.

Use this internal question for every section, article, menu item description, review summary, gallery caption, CTA, and SEO string: "Would this be appropriate and useful for a final restaurant customer to read?" If the answer is not clearly yes, do not render it.

Record the result in `.plan/<restaurant-slug>/findings.md` under `Customer Visibility Filter` with:

- customer-safe themes to use;
- internal-only notes to keep out of rendered pages;
- rejected phrases/patterns to search for during validation.
