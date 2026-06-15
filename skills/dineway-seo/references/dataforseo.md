# DataForSEO Provider Workflow

Use Forgeway-hosted DataForSEO through the Dineway CLI only:

- `dineway seo dataforseo serp`
- `dineway seo dataforseo maps`
- `dineway seo dataforseo keywords`
- `dineway seo dataforseo competitors`
- `dineway seo dataforseo ai-scrape`
- `dineway seo dataforseo ai-mentions`

## When to Use

- Organic SERP analysis for search intent and ranking competitors.
- Google Maps SERP analysis for local visibility.
- Keyword suggestions for cluster and brief planning.
- Competitor-domain discovery for comparison and market context.
- AI scraper and AI mentions for answer-engine visibility checks.

## Rules

- Use Forgeway `/api/dataforseo/*`; never ask for local DataForSEO credentials.
- Use live endpoints for v1.
- Keep limits bounded.
- Use the raw DataForSEO response fields returned by Forgeway.
- Do not expose provider credentials.
- Treat cost metadata as operational, not public copy.

## Interpretation

- SERP rank is evidence of current search surface, not proof of quality.
- Keyword volume and CPC are directional.
- Competitor data must be combined with source inspection before writing claims.
- AI mentions are visibility evidence, not endorsement.

## Output Use

Record:

- keyword/domain/platform;
- location and language;
- provider status and task identifiers when useful;
- top useful results;
- search intent;
- implications for Dineway pages/content/schema;
- limitations.
