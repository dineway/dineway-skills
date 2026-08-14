---
name: dineway-content-competition
description: Collect and analyze current competitors for Dineway content. Use for live SERP comparisons, competitor page evidence, content and structural gaps, opportunity scoring, competitor evolution, and evidence-backed topic clusters where acquisition is deterministic and Agent judgment remains local.
---

# Dineway Content Competition

Treat crawl and SERP retrieval as evidence acquisition; perform gap diagnosis, clustering,
prioritization, and recommendations locally in the Agent. Return one canonical report and typed
Competition payload to the active Pipeline Stage.

## Inputs and acquisition

- Target URL or planned topic, locale, market, industry context, site inventory, and accepted
  Research Result when present.
- Current SERP observations and up to three direct comparison URLs for a focused page analysis.
- Local HTTP crawl and Browser Use first. Use Forgeway DataForSEO/Firecrawl only for managed-key or
  infrastructure-heavy live SERP/page acquisition. Never require the user to configure provider
  keys when Dineway owns the connector.

Record URL, title, domain, rank, word count, headings, internal/external links, collected time,
availability, and raw artifact reference. Filter irrelevant directories, login pages, social noise,
copied pages, and non-comparable intent before analysis.

## Workflow

1. Confirm target intent and comparison set. A ranking page with different intent is evidence, not
   a valid template.
2. Compare topic coverage, section depth, heading structure, questions, tables, media, citations,
   entity clarity, freshness, and links.
3. Separate strengths from gaps. Link every conclusion to observation IDs; do not call crawler
   output a semantic fact.
4. Calculate an opportunity score only when all four factor inputs are measured: impact 35%,
   inverse effort 25%, speed 20%, strategic value 20%. Otherwise retain missing factors and score
   as unmeasured under the active Pipeline scoring policy.
5. Cluster related keywords/topics locally. Each cluster records members and rationale. Use
   `dineway-seo-cluster` if the recommendation becomes a formal Dineway content architecture.
6. Recommend differentiated scope, not imitation. Identify quick wins, growth work, and strategic
   work as views over measured evidence rather than separate authorities.

## Stage completion contract

Write `jobs/<job-id>/competition/report.json`, then return its canonical content and a typed payload
containing target URL, `manualCompetitorUrls`, location and industry context, opportunity score,
competitors with title/rank/strengths/gaps/observation IDs, local clusters, and recommendations.
Preserve the source analysis phases as bounded artifact references: `pageCrawlArtifactRef`,
`rankingQueriesArtifactRef`, `serpCompetitorsArtifactRef`, `competitorAnalysisArtifactRef`, and
`gapAnalysisArtifactRef`; use `null` when a phase is unavailable. Include source timestamps, all
observation IDs, provenance, and any bounded raw artifact reference.

Return to `dineway-content-pipeline`, which calls `content_pipeline_stage_complete` to derive the
receipt and create and accept the immutable Competition Result. Do not call granular Result operations
or create a Brief, Draft, cluster, or CMS change from this Skill without a separate Stage and owning
Skill.
