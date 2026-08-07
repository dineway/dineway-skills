# Security Boundaries

These boundaries apply to the root `dineway-seo` skill and every Dineway SEO child skill.

## Forgeway Integration Providers

- Use Firecrawl/DataForSEO only through Dineway Tools: CLI-first `discover` → `inspect` → `run`, or
  the generic built-in `tools_*` MCP lifecycle when CLI is unavailable.
- Resolve Forgeway through `DINEWAY_API_BASE_URL` or `FORGEWAY_API_URL`; do not add an SEO-specific base URL setting.
- Require formal verified users or valid project API keys. Do not serve anonymous or shadow users.
- Require `tools:read` plus `tools:run`, or `admin`, and Author-or-higher for token-authenticated MCP calls.
- Do not add Dineway deployment-site, restaurant-claim, or other ownership binding fields to provider requests.
- Do not expose provider credentials or billing secrets. Use CLI environment references or encrypted
  site BYOK without silent fallback to hosted credits.

## Request Safety

- Keep provider calls bounded by URL/query, location/language, limit, and crawl scope.
- Crawl first-party pages locally with same-origin, include/exclude, page, byte, timeout, and
  concurrency bounds. Use Browser Use only when rendering or interaction is required.
- Agents may inspect bounded competitor pages locally. Use Forgeway for managed API-key data or
  infrastructure-scale crawling; choose hosted credits or BYOK explicitly.
- Treat Dineway Tools CLI and generic MCP as equivalent deterministic provider transports. Keep
  interpretation, recommendations, and generation in Skills.
- Treat raw provider payloads as evidence. Do not claim unavailable facts, hidden ranking factors, private data, or unsupported competitor details.
- Record skipped/risky claims when evidence is incomplete, volatile, or source-limited.

## Application Safety

- Apply through existing Dineway content, media, SEO metadata, schema/settings, and rendering paths before proposing Astro patches.
- Keep generated or rewritten content Draft-only until exact-Draft editorial approval and release
  authorization pass through native Dineway publication paths.
- Do not use Forgeway AI quota for SEO image generation. Use the current agent image capability only when the user explicitly requests generated images.
