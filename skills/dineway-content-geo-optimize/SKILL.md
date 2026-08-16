---
name: dineway-content-geo-optimize
description: Run a deep, evidence-linked GEO and AEO inspection of an exact Dineway CMS Draft Revision. Use for quotability, answer structure, citation readiness, entity clarity, cross-platform citation evidence, citation-gap diagnosis, and an independent deep GEO 0-100 Result.
---

# Dineway Content GEO Optimize

Optimize an exact Dineway Draft Revision for AI extraction and citation. This is deeper than the
GEO component inside normal `dineway-content-optimize`; it produces an independent typed GEO Result
and never replaces SEO/GEO Content Score or publication gates.

## Inputs

- Current Pipeline Run, GEO Job, Assignment, Attempt, and accepted input Result versions.
- Exact CMS collection, content ID, Draft Revision ID, revision token, and schema fingerprint.
- Accepted Research, Brief, Draft, and Optimization Results plus their observations.
- Current Site Context, byline profile, cited sources, structured fields, and AI Visibility evidence.

Stop on stale Assignment, Draft drift, missing required input Result, or unverifiable material claim.

## Method

1. Establish the current AI Visibility baseline without manufacturing observations. Use
   `dineway-content-ai-visibility` when fresh cross-platform evidence is required.
2. Score four independently evidenced dimensions on 0-100:
   - `quotabilityScore`: concise, attributable, source-backed claims and definitions;
   - `answerStructureScore`: direct answers, headings, FAQs, tables, lists, and summaries that match
     observed questions;
   - `citationReadinessScore`: source authority, corroboration, freshness, attribution, and claim
     boundaries;
   - `entityClarityScore`: unambiguous entities, relationships, terminology, byline expertise, and
     relevant structured data.
3. Use `null` when a dimension cannot be measured. Deep GEO Score is the rounded mean of measured
   dimensions; `scoreCoverage` is measured dimension count divided by four. Never substitute zero.
4. Diagnose each citation gap as content, authority, entity, or citation-structure gap and cite the
   exact platform/prompt observations.
5. Prioritize suggestions as critical, high, medium, or low. Preserve source-aligned fields:
   `id`, `type`, `title`, `description`, optional `content`, `autoApplyable`, evidence IDs,
   apply/dismiss decision, and dismissal reason.
6. Keep deep GEO audit-only. Record source-supported suggestions against the exact Optimization final
   Draft, but do not create another Draft Revision at this optional stage.
7. Stop after three broad passes. Record score history by exact Draft Revision.

## Stage completion contract

Write `jobs/<job-id>/geo/report.json`, then return its canonical content and a typed payload with:

- `geoScore` and `scoreCoverage`;
- the four dimension scores and per-platform scores;
- citation gaps with query, platform, diagnosis, and observation IDs;
- suggestions and score history;
- top-level collection, content ID, unchanged current Draft Revision ID, content fingerprint, source times,
  observation IDs, provenance, and raw artifact reference.

The master calls `content_pipeline_stage_complete`; the Pipeline validator recalculates the
aggregate, validates the final Draft chain, derives the artifact receipt, and creates/accepts both
the immutable GEO Result and final Quality Attestation atomically. A mismatched score or Draft
Revision fails. Return to `dineway-content-pipeline`; do not call granular Result operations,
attest separately, approve, schedule, or publish.

## Interpretation

- 70+: well structured for citation; maintain and monitor.
- 50-69: measurable readiness with important gaps.
- Below 50: major restructuring or evidence work is needed.
- `null`: unmeasured, not poor performance.

Never chase a score by adding unsupported statistics, fake quotations, decorative FAQs, or generic
platform stereotypes.
