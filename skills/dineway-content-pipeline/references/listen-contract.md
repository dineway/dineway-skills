# Listen Source Contract

Listen composes native Dineway context with source-attributed observations. It does not ask a
deterministic tool to infer intent, recommend work, or cluster topics. The Agent supplies semantic
factor values; the plugin only applies the public active weighting policy.

## Session inputs

Read these native resources at the start of every Listen pass:

1. `site_briefing_get` for site scope and, when known, the target collection or content scope.
2. Current Site Context entries, schema, bylines, locales, published content, Activity, Assignments,
   and Handoffs included by or linked from the briefing.
3. `content_pipeline_source_snapshot_get` for the required observation source kinds and scope.

Site Briefing and Site Context remain native inputs. Do not duplicate them as Content Pipeline
observations merely to make one combined object.

## Source matrix

| Input                            | Acquisition owner                                                                                                                                    | Observation kind       | Default validity | Missing or failed behavior                                                                                                |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Visitor question aggregates      | Owning Dineway NLWeb/Chat subsystem                                                                                                                  | `first_party_question` | 7 days           | Record `not_configured` until the owner exposes a queryable aggregate contract; never add a second raw-conversation store |
| First-party pages and link graph | Native inventory plus bounded `dineway seo crawl local`                                                                                              | `local_crawl`          | 24 hours         | Record the actual failure state with an empty payload                                                                     |
| Search performance               | User-owned Google connector/account                                                                                                                  | `gsc`                  | 48 hours         | Record `not_configured`, `permission_denied`, or `temporarily_unavailable`; do not route credentials through Forgeway     |
| Live Google results              | Dineway Tools DataForSEO organic SERP                                                                                                                 | `google_serp`          | 24 hours         | Suppress only conclusions that require current SERP evidence                                                              |
| Keyword metrics                  | Dineway Tools DataForSEO keyword metrics                                                                                                              | `keyword_evidence`     | 7 days           | Keep demand values unknown rather than zero                                                                               |
| Competitor page evidence         | Dineway Tools DataForSEO SERP structure plus bounded Firecrawl extraction                                                                             | `competitor_page`      | 7 days           | Preserve the failed URL/source and continue with available competitors                                                    |
| AI answers and citations         | `dineway-content-ai-visibility` through Browser Use or the user's ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews, Grok, or DeepSeek access | matching engine kind   | 24 hours         | Record each engine independently; one unavailable engine does not suppress the others                                     |

The active versioned workflow policy may shorten these windows. It must not silently extend an
observation after `validUntil`.

## Availability semantics

- `available`: current evidence is present in the payload.
- `stale`: last-known evidence may be used only with an explicit stale warning.
- `temporarily_unavailable`, `not_configured`, `permission_denied`, and `unsupported`: payload must
  be empty. These values are not numeric zero.
- `not_observed`: returned only by a source snapshot when no matching observation exists at or
  before the requested time. It is not persisted. Collect the source or record its actual
  unavailable state before using a dependent score component.
- An observation whose `validUntil` is before the snapshot time is effectively `expired` even if
  its immutable stored freshness was `current` when collected.

## Listen sequence

1. Read the native Site Briefing and narrower native state.
2. Request a source snapshot with the sources required for this opportunity or monitoring pass.
3. For a content Research Job, start Dineway Tools organic SERP as the first evidence operation,
   then collect the remaining full Research bundle concurrently. For other Listen work, collect
   missing or expired evidence in the order required by its specialist contract.
4. Record one immutable observation per source contribution. Use stable dedupe keys, bounded raw
   artifact references, normalized UTC collection times, explicit validity, and empty payloads for
   unavailable states.
5. Request the source snapshot again at the same decision time. Any remaining `not_observed` source
   is an unresolved evidence gap, not implicit availability.
6. In a Research Job, return one typed Research payload with source availability and returned
   Observation IDs. Stage Complete deterministically renders `research/evidence.json` and
   `research/findings.md` and derives their receipts.
7. The Agent may recommend a deduplicated opportunity and explain a score only from linked
   observations. Record Impact, Inverse Effort, Speed, and Strategic Value with explicit
   availability/confidence, then record the opportunity score snapshot after the rationale artifact
   exists. The plugin calculates the final priority and updates the opportunity atomically.

## Suppression rules

- Missing GSC suppresses GSC-dependent quick-win, traffic-loss, and ranking-change claims. It does
  not suppress crawl-integrity, first-party-question, keyword, competitor, or AI-citation work.
- Missing one AI engine suppresses claims about that engine only. Cross-engine claims require the
  cited engines to be usable.
- Missing visitor questions removes first-party-demand support. New-content work may still proceed
  when other current demand evidence supports it and the rationale says first-party questions were
  unavailable.
- Expired crawl evidence cannot support current broken-link, orphan, canonical, or duplicate-page
  claims.
- A source failure never creates an opportunity by itself unless the opportunity is specifically
  to restore the owning integration and that work is in scope.

Keep semantic clustering, gap classification, opportunity selection, factor values, and rationale
in the Agent. The versioned 35/25/20/20 weights are public deterministic policy; the snapshot is an
evidence gate and calculation record, not a recommendation engine.
