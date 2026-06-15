# Schema and JSON-LD

Prefer server-rendered JSON-LD from Dineway content/settings/schema contributors. Use code patches only when current Dineway rendering cannot express the needed structured data.

## General Rules

- JSON-LD is preferred.
- Use only source-backed fields.
- Validate required and recommended properties before applying.
- Keep schema aligned with visible page content.
- Do not inject time-sensitive schema only through delayed client JavaScript.
- Never fabricate ratings, reviews, prices, availability, offers, opening hours, coordinates, images, or organization details.

## Common Active Types

- `Restaurant`
- `LocalBusiness`
- `Organization`
- `WebSite`
- `WebPage`
- `Article` / `BlogPosting` / `NewsArticle`
- `ImageObject`
- `BreadcrumbList`
- `ItemList`
- `Product` / `Offer` where product facts are real
- `Menu` and menu-related structures where real menu data exists

## Restricted or Low-Value Types

- `FAQPage`: do not recommend for ordinary commercial rich-result benefit. Use only when the page has real FAQ content and the business need is informational clarity, not rich-result chasing.
- `HowTo`: use only for actual step-by-step instructional content.
- `Review` / `AggregateRating`: use only with real ratings/review counts from allowed sources and visible context.
- `Event`: use only for real dated events.

## Deprecated or Removed Rich-Result Targets

Do not create schema solely to target removed or restricted rich results. Treat legacy FAQ/HowTo shortcuts as risk context, not primary strategy.

## Dineway Apply Targets

- Site settings and SEO Graph contributors for global entities.
- `DinewayHead`/page metadata helpers for page-level JSON-LD.
- Content item SEO fields for title, description, canonical, robots, and OG data.
- Media records for resolvable `image` and `ImageObject` data.

## Output

Return:

- `Detected Schema`
- `Recommended Schema`
- `Required Facts`
- `Missing Facts`
- `Dineway Apply Target`
- `Validation Steps`
