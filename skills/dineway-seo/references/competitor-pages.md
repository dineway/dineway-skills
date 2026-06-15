# Competitor and Comparison Pages

Use this for alternatives, X-vs-Y, best-of, roundup, and feature/price comparison pages.

## Allowed Page Types

- `X vs Y`
- `Best X alternatives`
- `Best X in <location/category>`
- `Feature or service comparison`
- `Roundup with transparent criteria`

## Guardrails

- Use only verifiable public claims.
- Cite source URLs and record access dates for volatile facts such as pricing and availability.
- Disclose affiliation, sponsorship, or owned-product bias when relevant.
- Present strengths and limits fairly.
- Skip unsupported claims instead of guessing.
- Do not fabricate screenshots, customer counts, awards, prices, ratings, or product capabilities.
- Avoid defamatory framing and unverifiable negative claims.

## Schema

- Use `ItemList` for roundups when items are real and ordered by explicit criteria.
- Use `Product`, `SoftwareApplication`, `Restaurant`, or `LocalBusiness` only when the page and facts support the type.
- Do not add FAQPage for ordinary commercial rich-result benefit; see `schema-jsonld.md`.

## Dineway Apply Targets

- Create drafts in an appropriate collection.
- Store title, meta description, canonical, OG fields, and noindex decisions in SEO metadata.
- Add comparison tables only when data is sourced.
- Keep citations in editorial/source fields if available; otherwise include a source appendix in the draft body.

## Output

Return:

- `Page Type`
- `Audience and Intent`
- `Comparison Criteria`
- `Sources`
- `Draft Outline`
- `SEO Metadata`
- `Schema`
- `Skipped Claims`
- `Dineway Apply Plan`
