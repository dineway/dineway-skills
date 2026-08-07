---
name: dineway-seo-providers
description: Use Dineway Tools through CLI or built-in MCP for Firecrawl and DataForSEO research. Use for provider selection, Firecrawl scrape/map/crawl/search, DataForSEO SERP/maps/keywords/competitors/AI visibility, raw provider response interpretation, credit- or BYOK-aware research, and evidence-backed SEO recommendations.
---

# Dineway SEO Providers

Use this child skill for Firecrawl and DataForSEO research through Dineway Tools. It may be invoked directly, but it must preserve the shared Dineway SEO boundaries.

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
5. Use only Dineway Tools. Run `dineway tools discover`, inspect the selected contract, and then use
   `dineway tools run` for human, script, or CI control. Use the generic `tools_discover`,
   `tools_inspect`, and `tools_run` MCP operations only when CLI is unavailable.
6. Interpret raw provider payloads as evidence, then route recommendations to content brief, cluster, competitor, schema, image, or apply-loop workflows.

## Boundaries

- Never ask for or store Firecrawl/DataForSEO secret values. CLI BYOK may reference environment
  variable names; built-in MCP may use encrypted site BYOK.
- Do not use third-party provider MCP servers. Dineway's built-in generic Tools MCP surface is
  allowed. First-party/local crawling and Browser Use belong to the calling Skill; this Skill
  handles Forgeway Integration evidence only.
- Do not expose provider credentials, billing secrets, or internal cache details.
- Treat provider cost/status/task metadata as operational evidence, not visitor-facing copy.
- Do not perform unbounded crawling or broad audits without explicit limits.
- Hosted provider use requires verified Forgeway account access. MCP requires an Author-or-higher
  actor with `tools:read` and `tools:run`, or `admin`; anonymous/shadow users are out of scope.

## Output

Use the root `dineway-seo` output contract. Include `Provider Chosen`, `Reason`, `Command/API Family`, `Inputs and Limits`, `Relevant Raw Response Fields`, `Dineway Implications`, `Provider Calls Used`, `Skipped or Risky Claims`, and `Verification Plan`.
