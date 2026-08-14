---
name: dineway-content-ai-visibility
description: Observe and analyze Dineway brand and content visibility in AI answer engines using the user's own Agent clients or Browser Use. Use for prompt monitoring, mentions, citations, exact answer evidence, share-of-voice inputs, platform gaps, trends, and alerts across ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews, Grok, and DeepSeek.
---

# Dineway Content AI Visibility

Collect AI-answer observations through user-owned clients or browser sessions. Dineway does not
proxy this model consumption through Forgeway. Keep per-response evidence and return a canonical
report plus typed AI Visibility payload to the active Pipeline Stage.

## Supported surfaces

ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews, Grok, and DeepSeek. A platform is supported
for observation, not guaranteed to be configured or automatable. Use explicit availability states.

## Prompt set

Track natural questions at least 10 characters long that reflect:

- primary product/service and topical questions;
- comparison and alternatives queries;
- best-of or recommendation queries;
- first-party or research-observed audience questions.

Bind each prompt to target brand, category, locale/market, selected platforms, and requested cadence
(daily, weekly, or manual). Version prompt text changes rather than mixing unlike history.

## Collection

1. Read the current Job, prior accepted AI Visibility Result, prompt set, Site Context, competitor
   names, content URLs, and due Monitor policy.
2. Execute the exact prompt separately on each due platform using the user's local Agent client or
   Browser Use. Do not bypass authentication, CAPTCHAs, access controls, or platform policy.
3. Store bounded raw answer evidence locally with platform, prompt, observed time, locale/account
   context when safe, answer artifact reference, brand mentioned, content cited, citation URLs, and
   competitor mentions. Never store cookies or session tokens.
4. Normalize each check into a native observation. A failed or unavailable platform records
   `cited: null`, not false.
5. Compare only equivalent prompt/platform/time windows. Diagnose content, authority, entity, or
   citation-structure gaps locally and cite observations.

## Metrics and Stage completion

Citation Score is measured citations divided by measured platform checks, expressed on 0-100. Do
not include unavailable checks in the denominator. Preserve `null` when nothing was measured.
Keep mentions distinct from citations.

Write `jobs/<job-id>/ai-visibility/report.json`, then return its canonical content and a typed
payload using the source-aligned normalized shape:

- `citationScore` and `overview` with `totalPrompts`, nullable `avgVisibilityScore`, `totalChecks`,
  `totalMentions`, `totalCitations`, and `periodDays`;
- `platformBreakdown` with checks, mentions, citations, and nullable 0-100 mention/citation rates;
- `promptResults` with nullable source result ID, prompt ID/text/category, target brand, platform,
  observed time, nullable mentioned/cited state, mention count, citation URLs, response snippet,
  sentiment/visibility scores, status, bounded answer artifact reference, and observation ID;
- `dailyTrend` with date and nullable visibility/check/mention/citation values.

The normalized fields map the source prompt overview and historical-result contracts; browser-only
evidence that has no source result ID uses `null`. Include source timestamps, observations,
provenance, and any bounded raw artifact reference.

Return to `dineway-content-pipeline`, which calls `content_pipeline_stage_complete` to derive the
receipt and create and accept the immutable AI Visibility Result. When invoked as evidence collection
for Monitor, return observations to `dineway-content-monitor` instead. Do not call granular Result
operations, edit content, create a Fix manually, or claim improvement without a comparable later
observation. Codex Scheduled may activate the master Pipeline Skill at the due time; the local
scheduler itself stores no authority.
