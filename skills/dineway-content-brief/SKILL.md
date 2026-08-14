---
name: dineway-content-brief
description: Create an evidence-backed Dineway content Brief from an accepted Research Result. Use for source-aligned outlines, target keywords, search intent, questions, unique angles, audience context, topic guardrails, internal links, image plans, and a human-approved handoff to Writer.
---

# Dineway Content Brief

Execute one Brief Stage from the accepted Research Result after the master Pipeline has begun it.
Return the canonical Brief artifact and typed payload, then stop for authenticated-human Stage
completion before Writer may start.

## Required inputs

- Current Run, Brief Job, Assignment, Attempt, and exact accepted Research Result ID/version.
- Research `evidence.json` and `findings.md` only as derived aids; native Result is authoritative.
- Site Briefing, Site Context, byline, locale/market, current schema, native content identity for
  refresh work, and applicable template/playbook context.
- Load `../dineway-seo/references/content-brief.md`, `apply-loop.md`,
  `security-boundaries.md`, and provider/schema references only when relevant.

Stop if the Research selection changed, source freshness expired, or local Research artifacts do not
match the accepted Result provenance.

## Workflow

1. Preserve Research topic, target keywords, intent, market, audience, evidence, competitor gaps,
   and unique differentiation. Do not rerun hidden research inside Brief.
2. Choose `blog`, `guide`, `landing`, `product`, `comparison`, or `listicle`. Record a target word
   count from 500-10000 only when evidence supports it; otherwise use `null`.
3. Build at most 50 outline sections. Each section uses the source-aligned fields `heading`, level
   1-4, `keyPoints`, nonnegative `suggestedWordCount`, `generationMode` (`ai` or `manual`), and
   evidence observation IDs.
4. Record competitor URLs, nullable notes, questions to answer, unique angle, target language and
   country, authority source, and relevant blog/guide format.
5. Record audience role, expertise (`beginner`, `intermediate`, `expert`), pain point, funnel stage
   (`awareness`, `consideration`, `decision`), and required/excluded topic guardrails.
6. Add verified internal links by stable public URL/native identity and an image plan by purpose,
   placement, dimensions, provenance, alt-text intent, caption need, and schema field.
7. Distinguish required scope, optional ideas, risky claims, and exclusions. Never invent menu,
   hours, pricing, allergen, award, review, staff, medical, legal, or financial facts.

## Artifact and Stage completion

Write `.dineway/content/runs/<run-id>/jobs/<job-id>/brief/brief.md`. Bind it to the Run, Job,
Research Result ID/version, collection, locale, byline, optional existing content ID/translation
group, and schema fingerprint.

Return a typed payload containing the exact Research Result reference, topic, keywords, content
type, nullable intent/word count, objective, outline, competitor URLs, notes, questions, unique
angle, market fields, authority/format fields, audience context, guardrails, internal links, image
plan, artifact ref, provenance, and observations.

An authenticated human reviews the artifact and calls `content_pipeline_stage_complete` with
`briefApproval.confirmed=true`. That transaction derives the artifact receipt, creates and accepts
the immutable Brief Result, and returns `begin_writer`. API-token and system actors are rejected.
Do not call granular Result/accept operations or write a CMS Draft from this Skill.
