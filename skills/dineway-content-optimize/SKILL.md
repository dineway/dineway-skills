---
name: dineway-content-optimize
description: Score and optimize an exact Dineway CMS Draft Revision for combined SEO and GEO performance. Use for SERP-relative 0-100 Content Score, evidence-linked breakdowns, prioritized suggestions, apply or dismiss decisions, iterative Draft revisions, score history, and quality-gate readiness.
---

# Dineway Content Optimize

Run the normal SEO/GEO optimization workflow against the exact current CMS Draft. Produce the
familiar combined 0-100 Content Score plus independent SEO and GEO values. Use
`dineway-content-geo-optimize` for deeper citation inspection.

## Inputs

- Current Pipeline Run, Optimization Job, Assignment, Attempt, and accepted input Result versions.
- Exact CMS collection, content ID, Draft Revision ID, revision token, schema fingerprint, and full
  Draft content.
- Accepted Research, Brief, and Draft Results; current SERP/competitor evidence; Site Context;
  selected byline; media; observations; and active quality/rule policy.
- Read `references/optimization-methodology.md`,
  `../dineway-seo/references/apply-loop.md`, and the Pipeline workflow/artifact contracts.

Stop on stale Assignment, changed Research/Brief selection, schema drift, or Draft drift.

## Public score contract

- `seoScore` measures SERP-relative topical coverage and on-page search readiness.
- `geoScore` measures direct-answer potential, citation worthiness, structured information, and
  observed question coverage at normal Optimize depth.
- `score` is `round((seoScore + geoScore) / 2)` when both are measured. If only one is measured,
  use it. If neither is measured, use `null`.
- `scoreCoverage` is measured component count divided by two.
- Use `scoreBasisVersion: dineway-content-score-v1`. The Pipeline recalculates and rejects a
  caller-authored mismatch.

Normalize source values expressed on 0-1 to 0-100 before recording. Preserve every unmeasured
component as `null`; never use zero for unavailable evidence.

## Workflow

1. Establish a fixed evidence baseline for the pass. Compare the Draft with the approved Brief,
   current top SERP pages, schema, links, media, Site Context, and byline samples.
2. Produce evidence-linked breakdown dimensions and suggestions. Preserve source-aligned suggestion
   fields: `id`, `type`, `title`, `description`, nullable proposed `content`, `autoApplyable`,
   priority, observation IDs, decision, and dismissal reason.
3. Prioritize missing topics, unsupported/thin sections, heading hierarchy, metadata, and verified
   links. Treat word count contextually. Reject keyword stuffing, competitor imitation, unsupported
   expansion, and voice damage.
4. Apply coherent blocking/high-impact changes through `dineway content update --draft --rev
<current-revision>`. Every material pass creates a newer native Draft Revision. Refresh the Job
   target and evidence before rescoring.
5. Re-score the complete Draft after each pass, record exact Draft Revision and observation IDs in
   `scoreHistory`, and stop after three broad passes. Do not chase 100.
6. Evaluate mandatory gates separately: `schemaValid`, `identityUnique`, `requiredMediaValid`,
   `accessibilityValid`, `sourceProvenanceValid`, and `rulesResolved`. A score cannot override one.

## Interpretation

- 80-100: excellent; minor tweaks only.
- 70-79: good and competitive.
- 50-69: important gaps remain.
- 30-49: major revision or a fresh Brief may be needed.
- 0-29: not competitive against the selected evidence set.
- `null`: unmeasured.

Use stricter active policy targets for high-value/competitive work, while treating 70 as the normal
minimum guidance. Optimize selectively; readability and evidence remain primary.

## Stage completion

Write `.dineway/content/runs/<run-id>/jobs/<job-id>/optimize/report.json`. Return its canonical
content plus a typed payload with Content Score fields, dimensions, suggestions, applied suggestion
IDs, mandatory gates, score history, artifact ref, collection/content/Draft Revision, content
fingerprint, observations, source times, provenance, and any bounded raw artifact reference.

Return to `dineway-content-pipeline`, which refreshes the exact CMS Draft and calls
`content_pipeline_stage_complete`. That transaction derives the receipt, creates and accepts the
immutable Optimization Result, and routes to optional deep GEO or derived Attestation. Do not call
granular Result operations, attest quality, approve, schedule, or publish here.
