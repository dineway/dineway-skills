# Security Boundaries

These boundaries apply to the root `dineway-seo` skill and every Dineway SEO child skill.

## Hosted Providers

- Use hosted Firecrawl/DataForSEO only through Forgeway `/api/firecrawl/*` and `/api/dataforseo/*`, normally via `dineway seo firecrawl ...` or `dineway seo dataforseo ...`.
- Resolve Forgeway through `DINEWAY_API_BASE_URL`; do not add an SEO-specific base URL setting.
- Require formal verified users or valid project API keys. Do not serve anonymous or shadow users.
- Do not add Dineway deployment-site, restaurant-claim, or other ownership binding fields to provider requests.
- Do not expose provider credentials, provider billing credentials, or BYOK fallback in Dineway.

## Request Safety

- Keep provider calls bounded by URL/query, location/language, limit, and crawl scope.
- Do not add local crawler, fetch, parse, render, or browser automation commands as part of v1 SEO workflows.
- Treat raw provider payloads as evidence. Do not claim unavailable facts, hidden ranking factors, private data, or unsupported competitor details.
- Record skipped/risky claims when evidence is incomplete, volatile, or source-limited.

## Application Safety

- Apply through existing Dineway content, media, SEO metadata, schema/settings, and rendering paths before proposing Astro patches.
- Keep generated or rewritten content draft-first unless the user explicitly asks to publish and an existing Dineway write path supports that safely.
- Do not use Forgeway AI quota for SEO image generation. Use the current agent image capability only when the user explicitly requests generated images.
