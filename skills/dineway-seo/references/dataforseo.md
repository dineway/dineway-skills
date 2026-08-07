# DataForSEO Provider Workflow

Use DataForSEO through Dineway Tools. Discover the endpoint from the requested capability instead of
guessing a provider path.

### CLI

- `dineway tools discover -q "DataForSEO <SERP, maps, keywords, competitors, or AI visibility need>"`
- `dineway tools inspect -p dataforseo -e <discovered-endpoint>`
- `dineway tools run -p dataforseo -e <inspected-endpoint> ...`
- For CLI BYOK, pass only the `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` environment variable names.

### Native MCP

- `tools_discover`
- `tools_inspect`
- `tools_run`
- `tools_get_run`
- `tools_list_runs`

Prefer CLI for agents, humans, scripts, and CI. Use built-in MCP only when CLI is unavailable. Both
routes use the Forgeway Integration catalog and authoritative run lifecycle.

## When to Use

- Organic SERP analysis for search intent and ranking competitors.
- Google Maps SERP analysis for local visibility.
- Keyword suggestions for cluster and brief planning.
- Competitor-domain discovery for comparison and market context.
- AI scraper and AI mentions for answer-engine visibility checks.

## Rules

- Inspect once before the first run in the task; never guess a DataForSEO endpoint or input shape.
- Never ask for DataForSEO secret values. Use CLI environment references or encrypted site BYOK.
- Require `tools:read` plus `tools:run`, or `admin`, and Author-or-higher for token-authenticated MCP calls.
- Keep limits bounded.
- Use the raw DataForSEO response fields returned by Forgeway.
- Do not expose provider credentials.
- Treat cost metadata as operational, not public copy.
- Keep interpretation, recommendations, and generation in the calling Skill; the CLI/MCP bridge
  returns evidence only.

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
