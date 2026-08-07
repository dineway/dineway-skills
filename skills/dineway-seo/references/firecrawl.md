# Firecrawl Provider Workflow

Use Firecrawl through Dineway Tools. Discover the endpoint from the requested capability instead of
guessing a provider path.

### CLI

- `dineway tools discover -q "Firecrawl <scrape, map, crawl, or search need>"`
- `dineway tools inspect -p firecrawl -e <discovered-endpoint>`
- `dineway tools run -p firecrawl -e <inspected-endpoint> ...`
- `dineway tools runs get -r <run-id> --wait` for an asynchronous crawl

### Native MCP

- `tools_discover`
- `tools_inspect`
- `tools_run`
- `tools_get_run`
- `tools_stop_run` when the inspected asynchronous endpoint is cancellable

Prefer CLI for agents, humans, scripts, and CI. Use built-in MCP only when CLI is unavailable. Both
routes use the Forgeway Integration catalog and authoritative run lifecycle.

## When to Use

- Scrape a target page into markdown for content improvement.
- Map a site to find crawlable URLs and candidate internal links.
- Start or check bounded crawl jobs.
- Search the web and optionally scrape result markdown.

## Rules

- Inspect once before the first run in the task; never guess a Firecrawl endpoint or input shape.
- Never ask for or store a Firecrawl secret value. Use CLI environment references or encrypted site BYOK.
- Require `tools:read` plus `tools:run`, or `admin`, and Author-or-higher for token-authenticated MCP calls.
- Keep limits small and intentional.
- Use the raw Firecrawl response fields returned by Forgeway.
- Do not expose provider credentials.
- Use only endpoints returned by Forgeway discovery and inspection.
- Keep interpretation, recommendations, and generation in the calling Skill; the CLI/MCP bridge
  returns evidence only.

## Output Use

- Turn scrape output into findings, outlines, metadata, or Dineway draft updates.
- Turn map output into internal-link and crawlability recommendations.
- Treat search output as evidence candidates, then verify source relevance.

## Verification

Record:

- provider/endpoint, inspected contract, and command used;
- URL/query;
- provider status or job identifiers when useful;
- relevant pages/results;
- skipped or truncated output.
