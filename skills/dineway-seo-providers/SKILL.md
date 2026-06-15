---
name: dineway-seo-providers
description: Use Dineway's hosted SEO provider workflows for Firecrawl and DataForSEO research. Use for provider selection, Firecrawl scrape/map/crawl/search, DataForSEO SERP/maps/keywords/competitors/AI visibility, raw provider response interpretation, quota-aware research, and evidence-backed SEO recommendations.
---

# Dineway SEO Providers

Use this child skill for hosted Firecrawl and DataForSEO research. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

## Required References

- Load `../dineway-seo/references/provider-selection.md`.
- Load `../dineway-seo/references/security-boundaries.md` before every provider call.
- Load `../dineway-seo/references/firecrawl.md` for Firecrawl scrape/map/crawl/search.
- Load `../dineway-seo/references/dataforseo.md` for DataForSEO SERP/maps/keywords/competitors/AI visibility.
- Load `../dineway-seo/references/apply-loop.md` before turning provider evidence into Dineway changes.

## Workflow

1. Decide whether provider data is necessary; use current Dineway state and user-supplied facts when enough.
2. Choose DataForSEO for SERP, maps, keywords, competitor-domain, and AI visibility data.
3. Choose Firecrawl for scrape, map, bounded crawl jobs, and search plus markdown extraction.
4. Keep every request bounded by URL/query, location/language, and limit.
5. Use only Forgeway-hosted endpoints through `dineway seo firecrawl ...` or `dineway seo dataforseo ...`.
6. Interpret raw provider payloads as evidence, then route recommendations to content brief, cluster, competitor, schema, image, or apply-loop workflows.

## Boundaries

- Never ask for or store local Firecrawl/DataForSEO credentials.
- Do not use local provider MCP servers, provider BYOK fallback, or local crawler/fetch/render commands.
- Do not expose provider credentials, billing secrets, or internal cache details.
- Treat provider cost/status/task metadata as operational evidence, not visitor-facing copy.
- Do not perform unbounded crawling or broad audits without explicit limits.
- Hosted provider use requires formal Forgeway credentials or valid project API-key access; anonymous/shadow users are out of scope.

## Output

Use the root `dineway-seo` output contract. Include `Provider Chosen`, `Reason`, `Command/API Family`, `Inputs and Limits`, `Relevant Raw Response Fields`, `Dineway Implications`, `Provider Calls Used`, `Skipped or Risky Claims`, and `Verification Plan`.
