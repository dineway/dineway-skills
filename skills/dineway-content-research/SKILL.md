---
name: dineway-content-research
description: Build a complete SERP-first, source-attributed Dineway Research Result for any content Research type before Brief.
---

# Dineway Content Research

Execute one Research Stage that the master Pipeline already began. Batch-record normalized evidence,
then return compact editorial decisions to `dineway-content-pipeline`. The server hydrates the
Observations and compiles the authoritative Research Result; Stage Complete renders canonical
evidence JSON and findings Markdown and derives their receipts.

## Required inputs

- Pipeline Run, Research Job, active Assignment/Attempt, objective, locale/market, and site identity.
- Research type: `general`, `topic`, `competitor`, `gap`, or `serp`.
- Query plus required audience, objective, and focus.
- Site Briefing, Site Context, schema, published inventory, byline context, prior observations, and
  explicit first-party-question availability.
- The `dineway-tools` and `dineway-seo-providers` contracts for provider discovery and execution.

Every Research type uses the full bundle below. A specialized type changes emphasis; it never skips
SERP, keyword metrics, competitors, questions, official sources, Site Context, or first-party
inventory.

## Mandatory SERP-first evidence order

1. Use Dineway Tools `discover -> inspect -> run -> poll` to start bounded DataForSEO organic SERP
   analysis. This must be the first evidence operation. Record provider, availability, start/end time,
   requested/returned counts, limitations, task identity in bounded raw evidence, and Observation IDs.
2. Only after the SERP request has started, collect the remaining independent areas concurrently:
   - DataForSEO numeric keyword volume, difficulty score (0-100), CPC, and intent;
   - DataForSEO SERP competitors, ranks, word counts, headings, and relevant questions;
   - Firecrawl bounded competitor and official-source pages;
   - native Site Context, published inventory, internal-link candidates, and user-owned signals.
3. Do not guess provider endpoints. Preserve the inspected operation, billing/cache status, and
   limitations. Do not place credentials, cookies, or unbounded page bodies in prompts or Results.
4. If a provider is unavailable, record the attempted coverage as `not_configured`,
   `temporarily_unavailable`, `permission_denied`, or `unsupported`. Returned count must be zero and
   unavailable numeric values remain `null`, never zero.

Do not use Browser Use, screenshots, or free-form browsing for this workflow.

## Normalized evidence and decisions

Record the evidence fields below in typed Observation payloads:

- `scope`: self-contained audience, objective, and focus;
- `coverage`: required `serp`, `keywordMetrics`, `competitors`, `questions`, `officialSources`,
  `siteContext`, and `firstPartyInventory` records;
- findings with stable IDs, relevance, and Observation lineage;
- normalized sources with source kind, primary/secondary/community authority, URL/domain,
  availability, collected time, and Observation IDs;
- keywords with numeric volume, 0-100 difficulty, CPC, intent, category, and Observation IDs;
- organic SERP results with rank, word count, headings, own-site/competitor flags, and Observation IDs;
- relevant and rejected questions. Rejected questions remain in Research with a reason and cannot flow
  into Brief;
- facts bound to normalized sources, content gaps, and competitors, all with Observation lineage;
- topic directions with numeric difficulty plus evidence-linked subtopics and keyword clusters.

Every available source-derived keyword, SERP result, question, fact, gap, competitor, subtopic, and
cluster must cite persisted Observation IDs. Record independent evidence together through
`content_pipeline_observation_record_batch`. Then submit only the research type, scope, query,
selected evidence IDs, summary, chosen directions, and recommendations. Do not duplicate normalized
evidence in Stage Complete.

## Stage completion

Return compact decisions, strict provenance, source timestamps, the union of selected Observation
IDs, and only bounded raw evidence references when needed. Do not build `artifactRefs`, Result
envelopes, Markdown/JSON wrappers, hashes, or byte counts.

The master calls `content_pipeline_stage_complete`. It validates SERP-first ordering and coverage,
renders:

- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/evidence.json`; and
- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/findings.md`.

The same transaction derives receipts, verifies every Observation exists, finishes the Attempt and
Assignment, creates Research, and accepts it. Do not call granular Result/accept
operations or create a Brief, Draft, or CMS mutation from this Skill.
