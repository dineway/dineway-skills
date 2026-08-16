---
name: dineway-content-optimize
description: Optimize one exact Dineway Draft, then produce the canonical native content-only QA report used by Quality Attestation.
---

# Dineway Content Optimize

Run one consolidated SEO/GEO optimization pass against the exact current CMS Draft, then perform one
final deterministic content QA and rescore. Use `dineway-content-geo-optimize` only when the Run
explicitly enables deep GEO.

## Inputs

- Current Pipeline Run, Optimization Job, active Assignment/Attempt, and accepted input Result
  versions.
- Exact collection, content ID, Draft Revision ID, revision token, schema fingerprint, content
  fingerprint, and full Draft content.
- Accepted Research, Brief, and Writer Results; current SERP/competitor evidence; Site Context;
  selected byline; media; persisted Observations; and active quality/rule policy.
- Read `references/optimization-methodology.md`, `../dineway-seo/references/apply-loop.md`, and the
  Pipeline workflow/artifact contracts.

Stop on stale Assignment, changed Research/Brief selection, schema drift, or Draft drift.

## Consolidated audit and optional remediation

1. Establish one fixed evidence baseline from the approved Brief, current SERP evidence, schema,
   links, media, Site Context, and byline samples.
2. Produce evidence-linked dimensions and suggestions with stable IDs, type, title, description,
   optional proposed content, auto-applyability, priority, Observation IDs, decision, and dismissal
   reason.
3. Prioritize missing topics, unsupported/thin sections, heading hierarchy, metadata, verified links,
   and voice. Reject keyword stuffing, competitor imitation, unsupported expansion, and voice damage.
4. Audit only by default. When the current Draft passes mandatory checks, do not submit content and
   do not write CMS.
5. When blocking findings require changes, produce one consolidated `remediationSource` using the
   Writer source contract. The backend may create exactly one final Draft Revision and records its
   lineage from the Writer source Draft. Do not patch cards or accessibility fields one by one.

## Score contract

- `seoScore` measures SERP-relative topical coverage and on-page search readiness.
- `geoScore` measures direct-answer potential, citation worthiness, structured information, and
  observed question coverage at normal Optimize depth.
- `score` is `round((seoScore + geoScore) / 2)` when both are measured, the measured side when only
  one is available, and `null` when neither is available.
- `scoreCoverage` is the measured component count divided by two.
- Preserve unavailable values as `null`, never zero.

## Canonical content QA

Build exactly one `contentQa` report for the final exact Draft through CLI, MCP, and native
interfaces. It contains checked time, collection, content ID, Draft Revision ID,
schema fingerprint, issues, and every required check:

- exact Draft identity and unique content identity;
- schema and Research/Brief coverage;
- persisted evidence lineage;
- heading/section structure;
- SEO metadata and canonical/robots data;
- internal links and media references;
- accessibility metadata and structured data;
- unresolved rules; and
- final scores.

Each check records `passed`, an actionable message only when failed, and persisted Observation IDs.
The report is the only QA authority consumed by Optimization and derived Quality Attestation. Do not
submit separate `mandatoryGates` or an `artifactRef` inside the payload.

Do not open a browser, take screenshots, inspect lazy loading, test responsive/viewport layout,
evaluate visual rendering, or test interactive behavior. There is no browser fallback in this
article-content workflow.

## Stage completion

Return the compact assessment: source Draft ID, dimensions, suggestions/decisions, and the exact-Draft
content-QA checks. Include `remediationSource` only for the one blocking remediation path. The server
calculates scores, compiles the canonical Optimization Result/report, derives the final fingerprint,
and records explicit source/final Draft lineage.

Return to `dineway-content-pipeline`, which refreshes the exact CMS Draft and calls
`content_pipeline_stage_complete`. That transaction validates the report identity and lineage,
derives the artifact receipt and atomically creates/accepts Optimization plus Quality Attestation
when this is the final quality stage. It otherwise routes to optional deep GEO. Do not call granular
Result operations, attest quality separately, approve, schedule, or publish here.
