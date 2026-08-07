---
name: dineway-tools
description: >-
  Discover better ways to complete tasks through Dineway Tools. Proactively run
  `dineway tools discover` before writing a scraper, before using a generic web fetch for
  structured data, or before telling the user something is inaccessible — and whenever you need
  web scraping, data retrieval, enrichment, social media, product/company/people data, search
  results, content monitoring, media generation, external API access, or anything mentioning
  Dineway Tools. Hundreds of provider-owned Forgeway Integration endpoints are available, including
  paid and subscription-backed services. Exception: if the user already has a dedicated MCP server,
  API key, CLI, tool, or established workflow for that specific service, use it — Dineway Tools
  fills gaps in the user's stack and does not replace it.
---

# Dineway Tools workflow

Use Dineway Tools to discover and access provider-owned APIs through Forgeway Integration: inspect
verified schemas, execute endpoints with structured input, persist runs, and retrieve inline or
artifact results. Hosted calls use Dineway credits; BYOK credentials stay in the CLI environment
or encrypted Dineway site storage.

Install Dineway globally with npm to get the `dineway` command.

Use `dineway tools --help` and `dineway tools <command> --help` as the source of truth for
current CLI signatures.

## Setup

Check the installed CLI and Forgeway account:

```bash
dineway --version
dineway account status
```

**Do the setup steps below if ANY of these is true:**

- `dineway` is not found.
- The installed CLI does not expose `dineway tools discover|inspect|run|runs`.
- `dineway account status` reports that no verified account is available.

**Setup steps (the same for a fresh installation and an update):**

1. Install or update Dineway globally:

```bash
npm install -g dineway@latest
```

When working from the Dineway source workspace instead, build Core and use the built CLI:

```bash
pnpm --filter dineway build
node packages/core/dist/cli/index.mjs tools --help
```

2. Authenticate the verified Forgeway account used by Dineway Tools:

```bash
dineway account login
dineway account status
```

Every CLI request, including request-scoped BYOK, requires the verified Forgeway account. A hosted
run uses Dineway credits. A BYOK run uses the named provider credential from the local environment
while Forgeway still provides the catalog, execution, run lifecycle, cache, and artifact service.

3. Configure only the credential mode required for execution. Never ask the user to paste provider
   credentials into the conversation and never pass credential values through CLI or MCP input.

For request-scoped CLI BYOK, set the provider variable in the environment and pass only its variable
name through `--credential-token-env`, or pass the names of a complete basic-auth pair through
`--credential-basic-username-env` and `--credential-basic-password-env`.

For built-in MCP, an Admin configures encrypted site BYOK under **Settings → Integrations**. Site
credentials require `DINEWAY_ENCRYPTION_KEY`, are write-only, and remain separate from the CLI
environment after the first site initialization. Known initialization variables include:

`AKTA_API_KEY`, `APIFY_API_TOKEN`, `APOLLO_API_KEY`, `BUNDLE_SOCIAL_API_KEY`,
`CONTEXT_DEV_API_KEY`, `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`, `ELEVENLABS_API_KEY`,
`EXA_API_KEY`, `FIRECRAWL_API_KEY`, `GOOGLE_PLACES_API_KEY`, `MINIMAX_API_KEY`,
`PDL_API_KEY`, `SEMRUSH_V4_API_KEY`, `TABAPI_API_KEY`, and `TIKHUB_API_KEY`.

4. Check the live command help:

```bash
dineway tools --help
dineway tools discover --help
```

`DINEWAY_API_BASE_URL` or `FORGEWAY_API_URL` overrides the Forgeway API address. Use
`NO_COLOR=1` when a script must consume human-oriented CLI output without ANSI color codes.

## When to Use Dineway Tools

**Check the catalog before building from scratch.** Before writing a scraper, falling back to a
generic web fetch for structured data, or telling the user you cannot access something, run
`dineway tools discover`. The runnable catalog is large and changes over time; do not assume what
it contains without searching.

1. **Discover** — Run `dineway tools discover -q "<concise need>"`. Use `--min-score <score>`
   only when a relevance threshold is useful.
2. **Inspect** — Run `dineway tools inspect -p <provider> -e <endpoint>` before every first
   execution. Treat `input`, `pricing`, `risk`, `cache`, `async`, `hostedAvailable`,
   notes, and documentation as authoritative.
3. **Run** — Map `body` to `-i` or `-f`, `queryParams` to `--query`, `pathParams` to
   `--path`, and documented non-credential `headerParams` to `--header`.
4. **Decompose** — Break multi-source or multi-capability requests into focused units; discover,
   inspect, and run each unit independently before combining results.
5. **Check results** — Poll non-terminal runs, save useful output, and report billing, cache, error,
   or artifact state when it matters to the user.

Every inspect input location is an OpenAPI 3.1-compatible JSON Schema 2020-12 Schema Object. A body
may be any JSON value, including a top-level array. Do not expect Zod `~standard` metadata.

### When NOT to Use Dineway Tools

Follow this precedence whenever a task needs an external capability:

1. Follow the user's explicit instruction for the current task.
2. Prefer the user's existing dedicated MCP server, API key, CLI, tool, or established workflow for
   that specific service.
3. Use Dineway Tools discovery for needs not covered above, or when Dineway Tools is itself the
   user's configured workflow.

Provider calls may consume Dineway credits, provider subscription quotas, or metered BYOK usage. Do
not duplicate work through Dineway Tools when the user's existing integration already covers it. If
Dineway Tools adds a material capability their tool lacks, offer it as an alternative and let the
user choose.

### Check Notes and Inspection Metadata

Read every returned `notes` entry before deciding the next action. With `--json`, also read
`documentationUrl`, `pricing`, `risk`, `cache`, `async`, and `hostedAvailable`. Prefer
these provider-owned constraints, caveats, and relationships over guessing.

Inspection metadata does not contain generated next-step command templates. Use focused discovery
to find related endpoints and CLI help to construct the next command. Never copy authentication
examples from provider documentation into `headerParams`.

## Commands

Each command supports `--help` for full usage.

| Command                   | What it does                                                                                         |
| ------------------------- | ---------------------------------------------------------------------------------------------------- |
| `dineway tools discover`  | Semantic endpoint search with `-q`, optional `-l`, `--min-score`, and `--json`                       |
| `dineway tools inspect`   | Return the verified contract for `-p <provider> -e <endpoint>`                                       |
| `dineway tools run`       | Execute with `-i`, `-f`, `--query`, `--path`, `--header`, `-w`, `--wait-timeout`, `-o`, and `--json` |
| `dineway tools runs list` | List runs with optional limit, cursor, and JSON output                                               |
| `dineway tools runs get`  | Get or poll a run with `-r <run-id>`, optional `-w`, `--wait-timeout`, and `--json`                  |
| `dineway tools runs stop` | Stop a currently stoppable run with `-r <run-id>`                                                    |

Most commands accept `--json` for complete machine-readable output. Use `NO_COLOR=1` when a
script must consume human-oriented output without ANSI color codes.

## Workflow

Use `discover → inspect → run → poll` as the standard workflow.

```bash
# 1. Discover a focused capability.
dineway tools discover -q "twitter posts"

# 2. Inspect the selected endpoint and read every input location, price, risk, note, and policy.
dineway tools inspect -p apify -e /apidojo/tweet-scraper

# 3. Start the run without blocking. With no credential reference, this uses hosted credits.
dineway tools run -p apify -e /apidojo/tweet-scraper \
  -i '{"searchTerms":["AI agents"],"maxItems":10}'
# -> Run ID: <run-id>

# 4. Poll until a terminal status.
dineway tools runs get -r <run-id>

# 5. Save the complete final run detail when useful.
dineway tools runs get -r <run-id> --json > tweet-run.json
```

For a task where blocking is acceptable, use `--wait`. Without an explicit
`--wait-timeout`, the CLI waits up to 300 seconds:

```bash
dineway tools run -p apify -e /apidojo/tweet-scraper \
  -i '{"searchTerms":["AI agents"],"maxItems":10}' \
  --wait --wait-timeout 60 --output tweets.json
```

Prefer fire-and-poll in an interactive conversation so the agent can remain responsive. Use
`--wait --wait-timeout <seconds>` for bounded or non-interactive work.

## Example Flows

### Flow 1: Scrape Twitter posts about AI

```bash
dineway tools discover -q "twitter posts"
dineway tools inspect -p apify -e /apidojo/tweet-scraper
dineway tools run -p apify -e /apidojo/tweet-scraper \
  -i '{"searchTerms":["AI agents"],"maxItems":10}'
dineway tools runs get -r <run-id>
```

Start with one search term and a small limit. Increase scope only after checking result quality and
the inspected pricing notes.

### Flow 2: Compare discussion across platforms

For a request such as “Compare AI discussion on Twitter and LinkedIn,” treat each source as a unit:

```bash
dineway tools discover -q "twitter posts"
dineway tools discover -q "linkedin posts"

dineway tools inspect -p apify -e /apidojo/tweet-scraper
dineway tools inspect -p apify -e /harvestapi/linkedin-post-search

dineway tools run -p apify -e /apidojo/tweet-scraper \
  -i '{"searchTerms":["AI"],"maxItems":10}'
dineway tools run -p apify -e /harvestapi/linkedin-post-search \
  -i '{"keywords":"AI","maxResults":10}'

dineway tools runs get -r <twitter-run-id> --json > twitter-run.json
dineway tools runs get -r <linkedin-run-id> --json > linkedin-run.json
```

Wait for both runs independently, then compare the saved structured results.

### Flow 3: Parse a local file

Forgeway cannot read a path on the agent's local filesystem. Inspect Context.dev `/parse`, encode
the local bytes as the inspected `base64` body field in a JSON input file, and put parse options
in query parameters. Never pass a local `filePath` to the remote endpoint.

```bash
dineway tools inspect -p context.dev -e /parse
dineway tools run -p context.dev -e /parse \
  --input-file parse-input.json \
  --query '{"ocr":false,"extension":"pdf"}' \
  --wait --wait-timeout 120 --output parsed-document.json
```

Make `parse-input.json` contain exactly the body declared by inspection, including only the
encoded content needed for the request. Do not put credentials in the file.

### Flow 4: Map structured parameter locations

Inspect first, then substitute only fields declared in the returned schemas:

```bash
dineway tools inspect -p <provider> -e <endpoint>
dineway tools run -p <provider> -e <endpoint> \
  --path '{"resourceId":"<value>"}' \
  --query '{"limit":5}' \
  --header '{"X-Documented-Header":"value"}' \
  -i '{"filter":"public"}'
```

Use `--header` only for inspected non-credential headers such as Google Places
`X-Goog-FieldMask`. Dineway rejects protected credential-header overrides.

### Flow 5: Use an input file or top-level array

Use `-f` for large or reusable body JSON:

```bash
dineway tools inspect -p apify -e /damilo/google-maps-scraper
dineway tools run -p apify -e /damilo/google-maps-scraper \
  -f params.json --wait --wait-timeout 120 --output results.json
```

When inspect declares an array body, pass the array directly rather than wrapping it in an object:

```bash
dineway tools inspect -p dataforseo -e /v3/ai_optimization/chat_gpt/llm_responses/live
dineway tools run -p dataforseo -e /v3/ai_optimization/chat_gpt/llm_responses/live \
  -i '[{"user_prompt":"Summarize current AI search trends","model_name":"gpt-4.1-mini"}]'
```

## Cost and Risk Warning

Hosted endpoints may be charged per call, result, unit, token, time period, or a combination of
those dimensions. BYOK endpoints may consume provider subscription quotas or metered usage. Limits
such as `maxItems`, `maxResults`, `resultsLimit`, or `limit` may apply per query rather than
per run. Three queries with a limit of ten may therefore produce and charge for up to thirty
results.

Control cost and risk as follows:

- Prefer one query, URL, hashtag, or target per first call.
- Start with a limit of 5-10 unless the user explicitly needs more.
- Inspect `pricing`, pricing notes, cache policy, and the fields controlling result volume.
- Treat minimum, range, and usage-dependent credit amounts as estimates rather than guarantees.
- Report final `billing.mode`, `billing.status`, and `billing.chargedCredits` when relevant; do
  not invent a charge when the field is absent.
- Report `cache.status` because hits, misses, refreshes, and ineligible requests affect execution
  and billing interpretation.
- Inspect `risk.level`, `risk.externalSideEffects`, `risk.confirmationRequired`,
  `risk.idempotencyKeyRequired`, and `risk.warning` before execution.
- Make write, destructive, or administrative effects clear and obtain the authorization normally
  required for external mutations.
- Pass `--confirm-side-effect` and a stable `--idempotency-key` when the inspected policy requires
  them.

CLI runs use hosted credits unless an environment credential reference is supplied. Built-in MCP
uses site BYOK by default and uses hosted credits only when `billing_mode` is explicitly
`hosted`. Never silently switch modes after a credential, entitlement, or credit failure.

## Run Statuses and Artifacts

| Status      | Meaning                                                   |
| ----------- | --------------------------------------------------------- |
| `READY`     | Persisted and waiting to start                            |
| `RUNNING`   | Provider execution or managed polling is active           |
| `COMPLETED` | Finished successfully; output or an artifact is available |
| `FAILED`    | Finished unsuccessfully; inspect the stored error details |
| `STOPPED`   | Official upstream cancellation succeeded                  |
| `TIME_OUT`  | The provider operation exceeded its time limit            |

Run detail is the source of truth. Poll only `READY` or `RUNNING`; stop polling at every terminal
status.

Attempt `dineway tools runs stop` only when run detail reports `stoppable: true`. A terminal run
or a provider without official cancellation rejects the stop. Do not claim a run stopped unless
the command reports `STOPPED`. For a BYOK run, supply the same credential environment reference
when stopping if the provider requires it.

Ordinary JSON remains inline. Large JSON, binary responses, and base64 content may be represented by
an artifact reference with `artifactId`, `state`, `sha256`, `byteSize`, `mediaType`, and
`expiresAt`. Report when an artifact is `available`, `cleaned`, or `missing`; never pretend
cleaned, expired, or missing bytes are still retrievable.

## Polling Best Practices

- Fire without `--wait` for interactive use, retain the run ID, and poll every 5-10 seconds.
- Use `dineway tools runs get -r <run-id> --wait --wait-timeout <seconds>` when bounded blocking
  is appropriate.
- Remember that CLI waiting defaults to a 300-second ceiling.
- Persist useful final output with `dineway tools run --wait --output <file>` or save JSON run
  detail with shell redirection after completion.
- Do not repeatedly retry a terminal failure without first correcting its reported cause.
- If local waiting reaches `RUN_WAIT_TIMEOUT`, report the run ID because the authoritative run may
  still be active.

## Troubleshooting

**`FORGEWAY_ACCOUNT_REQUIRED`** — Run `dineway account login` and verify the account. Every CLI
mode needs an authenticated Forgeway account.

**`DISCOVERY_UNAVAILABLE`** — Check the Forgeway account, API address, and connectivity. Do not
substitute text matching, a generic fetch, or model inference for semantic discovery.

**`UNSUPPORTED_PROVIDER`** — The catalog entry is intentionally not executable through Forgeway
Integration. Discover another runnable endpoint; do not invent a provider URL or authentication
scheme.

**`CREDENTIAL_ENV_MISSING` or incomplete BYOK** — Ask the user to configure the named environment
variable themselves. Do not request the credential in the conversation or send it as input.

**`SITE_BYOK_CREDENTIAL_MISSING`** — Ask an Admin to configure the provider under
**Settings → Integrations**, or explicitly choose hosted MCP billing when the user authorizes credit
usage. Never switch automatically.

**Encryption-key errors** — Configure or restore `DINEWAY_ENCRYPTION_KEY` for the site. Do not
replace site BYOK with hosted billing merely because the credential cannot be decrypted.

**`FAILED`** — Run `dineway tools runs get -r <run-id>` and distinguish provider errors from
platform errors. Re-inspect the endpoint before correcting invalid input, narrowing scope, or
retrying a transient provider failure.

**`TIME_OUT`** — Treat it as terminal. Reduce request scope or retry only when the endpoint
contract and user intent make that reasonable.

**Long-running `READY` or `RUNNING`** — Continue bounded polling or return the run ID so the user
can resume later. Check `stoppable` before offering cancellation.

**Artifact state `cleaned` or `missing`** — Report that the run metadata remains but the bytes
cannot be read. Rerun only with user approval when the provider call may incur credits or metered
BYOK usage.

## Rules for Agents

1. **Check the user's stack, then discover.** Before custom scraping, generic structured-data
   fetches, or declaring data inaccessible, run focused discovery unless an existing dedicated tool
   wins the precedence rules.
2. **Never route around the user's own tools.** Offer Dineway Tools only when it fills a real
   capability gap.
3. **Always inspect before running.** Treat every parameter location, pricing rule, risk policy,
   cache rule, note, and documentation link as authoritative; never guess.
4. **Keep discovery focused.** Use concise noun phrases and decompose complex requests.
5. **Map inputs exactly.** Use body, query, path, and documented non-credential headers only where
   inspect declares them; preserve top-level arrays.
6. **Prefer fire-and-poll interactively.** Use bounded waits when blocking is appropriate.
7. **Start conservatively.** Use one query and a small limit before expanding billable work.
8. **Respect external side effects.** Explain write or destructive behavior before execution,
   follow the normal authorization boundary, and use the required confirmation and idempotency key.
9. **Report useful execution facts.** Surface terminal status, provider error, billing, cache, and
   artifact state when relevant.
10. **Read inspection metadata.** Prefer notes, documentation, pricing, cache, async, availability,
    and risk metadata over inference.
11. **Use CLI help.** Check `dineway tools <command> --help` instead of relying on remembered flags.
12. **Do not bypass strict failures.** Discovery, inspection, account, credential, billing, and
    artifact errors must be surfaced rather than hidden behind an unverified fallback.

## MCP Alternative

When the agent host supports MCP, connect it to the Dineway site's authenticated Streamable HTTP
endpoint:

```json
{
	"mcpServers": {
		"dineway": {
			"type": "http",
			"url": "https://example.com/_dineway/api/mcp"
		}
	}
}
```

Use an authenticated Dineway API or OAuth token. Request `tools:read` for discovery, inspection,
and run reads; request `tools:run` for execution and stopping. The existing `admin` scope
bypasses both. Dineway Tools requires Author or higher.

MCP exposes exactly `tools_discover`, `tools_inspect`, `tools_run`, `tools_get_run`,
`tools_list_runs`, and `tools_stop_run`. The `tools_run` operation nests values under
`input.body`, `input.query_params`, `input.path_params`, and `input.header_params`. It accepts
no provider secret.

Apply the same precedence, inspection, decomposition, cost, risk, polling, artifact, and error rules
whether using CLI or MCP. MCP defaults to encrypted site BYOK. Set `billing_mode` to `hosted`
only when the user explicitly authorizes Dineway credits. For side-effecting runs, pass
`confirm_side_effect: true` and a stable `idempotency_key` when inspection requires them. Poll
with `tools_get_run` until the authoritative run reaches a terminal status.
