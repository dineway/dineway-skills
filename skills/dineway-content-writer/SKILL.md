---
name: dineway-content-writer
description: Draft or revise schema-valid Dineway content from an approved Brief in a selected native byline voice. Use for the Draft stage, new articles/pages, localized variants, or Fix/refresh revisions that must preserve existing content identity and remain local until optimization.
---

# Dineway Content Writer

Produce a schema-valid article from an accepted Brief and write it immediately as a native CMS
Draft after structural validation. Pipeline stores only the exact Draft identity Result, never a
second authoritative article body.

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
7. Represent rich text in the format required by the current schema. Keep media references in the
   media manifest until native media IDs exist.
8. After structural validation, call `dineway content create --draft` for new content or `dineway
content update --draft --rev <current-revision>` for an update/Fix. Save the unchanged CMS
   response in `.dineway/content/runs/<run-id>/jobs/<job-id>/cms/draft-receipt.json`.
9. Refresh the CMS item and record a `draft` Result containing only `collection`, `contentId`, exact
   `draftRevisionId`, revision token, and current `schemaFingerprint`. Bind the same identity at
   Result level with provenance and accepted input Result versions.

## Completion gate

- Every required schema field is present or explicitly blocked.
- Every factual claim maps to Research/Site Context evidence.
- Locale, byline, translation family, and existing content identity are preserved.
- No provider notes, prompts, internal rule text, or provenance instructions appear in public copy.
- The exact native Draft Result is ready for `dineway-content-optimize`, not for publication.
