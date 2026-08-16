---
name: dineway-content-writer
description: Draft or revise schema-valid Dineway content from an approved Brief in a selected native byline voice. Use for the Draft stage, new articles/pages, localized variants, or Fix/refresh revisions that must preserve existing content identity and remain local until optimization.
---

# Dineway Content Writer

Produce one compact, schema-aware Writer source object from an accepted Brief. The Dineway backend
validates it and writes the native CMS Draft deterministically. Pipeline stores only the exact Draft
identity Result, never a second authoritative article body.

## Required inputs

- Read the artifact contract at
  `../dineway-content-pipeline/references/artifact-contract.md`.
- Read the current Run, Writer Job, Assignment, Attempt, exact accepted Research/Brief Result
  versions, Site Briefing, Site Context, collection schema, locale rules, selected byline profile,
  representative published samples, and derived Research/Brief artifacts.
- For update/Fix work, read the current native content, Draft/Live revisions, revision token, slug,
  translation family, links, media, and SEO fields.

## Workflow

1. Verify that the accepted Brief targets the same Run, collection, locale, byline, and content ID
   as current native state. Stop on input Result, Assignment, identity, or schema drift.
2. Build a field map from the live Dineway collection schema. Use semantic field roles where
   available; do not invent a parallel schema mapping.
3. Write in the selected byline's observed style without impersonating personal experiences,
   credentials, opinions, or claims not present in Site Context or source material.
4. Follow the evidence map. Make unsupported, risky, volatile, medical, legal, financial, allergen,
   pricing, availability, award, review, and staff claims explicit blockers or omissions.
5. Preserve the Brief's useful structure while favoring clarity over keyword repetition. Answer the
   primary intent early, use specific headings, include quotable source-backed statements, and keep
   transitions natural.
6. Add internal links only to verified native/public targets. Preserve stable slug/content identity
   for refresh and Fix work.
7. Emit fields by schema slug plus one ordered body model of sections and cards. Every referenced
   image must use a native media ID and non-empty `imageAlt`; include accessibility fields before
   submission, not as an Optimization patch.
8. Save that source object under the Run Job directory. With CLI, pass it as `--source-file`; the CLI
   reads and sends the JSON object in the same Stage Complete request. Never send a local path or
   arbitrary URL to a remote Dineway backend.
9. Return control to the master Pipeline. It calls `content_pipeline_stage_complete`, which validates
   schema/media, assembles Portable Text or JSON, creates or updates one Draft Revision, derives
   schema/content fingerprints, binds accepted upstream Results, and returns a compact Draft receipt
   atomically.

## Completion gate

- Every required schema field is present or explicitly blocked.
- Every factual claim maps to Research/Site Context evidence.
- Locale, byline, translation family, and existing content identity are preserved.
- No provider notes, prompts, internal rule text, or provenance instructions appear in public copy.
- Native status returns `begin_optimization`; the exact Draft is not ready for publication.
- Do not call granular Result mutation operations from this Skill.
