# Firecrawl Provider Workflow

Use Forgeway-hosted Firecrawl through the Dineway CLI only:

- `dineway seo firecrawl scrape`
- `dineway seo firecrawl map`
- `dineway seo firecrawl crawl`
- `dineway seo firecrawl search`

## When to Use

- Scrape a target page into markdown for content improvement.
- Map a site to find crawlable URLs and candidate internal links.
- Start or check bounded crawl jobs.
- Search the web and optionally scrape result markdown.

## Rules

- Use Forgeway `/api/firecrawl/*`; never ask for or store a local Firecrawl API key.
- Keep limits small and intentional.
- Use the raw Firecrawl response fields returned by Forgeway.
- Do not expose provider credentials.
- Do not use Firecrawl parse/interact/monitor/account APIs in v1.

## Output Use

- Turn scrape output into findings, outlines, metadata, or Dineway draft updates.
- Turn map output into internal-link and crawlability recommendations.
- Treat search output as evidence candidates, then verify source relevance.

## Verification

Record:

- command used;
- URL/query;
- provider status or job identifiers when useful;
- relevant pages/results;
- skipped or truncated output.
