---
name: dineway-content-monitor
description: Collect and interpret source-attributed Dineway content performance, ranking, crawl integrity, traffic, and AI-citation observations. Use for scheduled monitoring, Google ranking changes, user-owned GSC evidence, ChatGPT/Perplexity/Claude/Gemini/Google AI visibility checks, content decay, anomaly review, or Fix-opportunity evaluation.
---

# Dineway Content Monitor

Observe content without mutating it. Store bounded local evidence, record normalized observations
through Content Pipeline MCP tools, and apply the active deterministic monitor policy. The
plugin, not the Agent, owns tier transitions and deduplicated Fix triggers; the master Skill owns
diagnosis, calendar priority, and the later Draft workflow.

Load `references/ai-visibility.md` and invoke `dineway-content-ai-visibility` before collecting or
interpreting AI-engine observations.

## Source boundaries

- Query GSC and other user-owned accounts through the user's local authenticated connector. Do not
  send those credentials to Forgeway.
- Observe ChatGPT, Perplexity, Claude, Gemini, Google AI Overviews, Grok, and DeepSeek through the
  user's local clients or Browser Use. These are client-owned compute, not Forgeway AI workloads.
- Crawl the first-party site locally; use Browser Use for rendered checks. Record internal links,
  orphan pages, duplicate topics, keyword conflict evidence, status, canonical, and structured data.
- Use Forgeway DataForSEO/Firecrawl only for managed API-key or infrastructure-scale evidence such
  as live SERP/rank/keyword datasets. Use `dineway-seo-providers` for bounded requests.

Every missing or failed source receives an explicit availability state. Never emit zero traffic,
rank, citation, or issue counts in place of unavailable data.

## Cadence

- Check new content during its first 30 days and other high-priority content every three days.
- Check stable content weekly and low-priority content monthly.
- Promote immediately after an anomaly. Demote only after three consecutive stable observations.
- Use the active versioned policy when it differs; record the policy version with evidence.

## Workflow

1. Read `content_pipeline_monitor_policy_get`, due
   `content_pipeline_monitor_state_list` entries, native content identity, locale, revisions,
   publication time, linked observations, score snapshots, and prior Fix opportunities.
2. Collect only sources due for this tier. Preserve raw local evidence in
   `.dineway/content/runs/<run-id>/jobs/<job-id>/monitor/evidence.json`; normalize each result into a native observation with freshness,
   availability, artifact reference, dedupe key, and either numeric `monitoring.metrics` or explicit
   `monitoring.integrity` facts. Unavailable sources use an empty payload.
3. Compare like-for-like windows and sources. Distinguish measurement gaps, seasonality, query/SERP
   changes, site integrity failures, and genuine content decay as Agent analysis; do not convert
   that diagnosis into caller-authored thresholds.
4. Run the reviewed `content_pipeline_monitor_observation_evaluate` command once for each
   stored observation. Preserve the returned evaluation, policy, tier, next due time, and optional
   trigger in the local monitor receipt. Exact replay must reuse the stored evaluation; an older new
   observation fails closed.
5. Record an explainable new priority snapshot when current evidence materially changes demand,
   authority gap, freshness risk, effort, or publication readiness.
6. If evaluation returns a trigger, read it with `content_pipeline_fix_trigger_get` and use its
   linked Fix opportunity. Do not manually create another Fix. Repeated evidence reuses one active
   Fix opportunity; after that opportunity is terminal, later evidence may create new work.
7. Return to `dineway-content-pipeline`. Do not create a duplicate content item, mutate the
   page, or enter the Draft pipeline before the linked Fix opportunity is accepted.
8. Record the completed Monitor Attempt as a typed `monitor` Result linked to observations,
   deterministic evaluation receipts, policy version, next due time, and optional Fix trigger.

## Output

Return source availability, observation IDs, comparable changes, anomaly classification, monitoring
tier decision, policy/evaluation/trigger IDs, score-snapshot rationale, linked Fix decision, and
next due check. If evidence is inconclusive, say so and retain the policy-derived next due time
rather than manufacturing certainty.
