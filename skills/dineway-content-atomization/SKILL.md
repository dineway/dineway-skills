---
name: dineway-content-atomization
description: Break an exact Dineway long-form content revision into reviewable atomic assets for social, email, ads, threads, summaries, LinkedIn carousels, newsletters, and Instagram carousels. Use for single or batch repurposing, structured export, and channel-specific content banks.
---

# Dineway Content Atomization

Create channel assets from a proven Dineway content revision. Atomization is a specialist Pipeline
Job; it does not create a second article authority and it does not publish to external channels.

## Inputs

- Active Run/Job/Assignment/Attempt and accepted input Result versions.
- Exact source collection, content ID, Draft or Live Revision ID, byline, locale, Site Context, and
  full native content read.
- Requested formats and tone constraints. Prefer high-performing or evergreen source content when
  evidence exists.

Supported format families include `social`, `email`, `ad`, `thread`, `summary`,
`linkedin_carousel`, `twitter_thread`, `newsletter`, and `instagram_carousel`. Map them to an
explicit channel; do not assume one generic post fits every platform.

## Workflow

1. Verify the exact source revision is current and authorized for reuse. Do not atomize stale local
   text or unpublished sensitive material without operator intent.
2. Extract the source's claims, examples, evidence, voice, and conversion goal. Preserve meaning and
   attribution; do not invent facts to make an atom more engaging.
3. Generate each requested format within its channel conventions and requested tone. Record a
   stable atom ID, type, channel, content, character/segment count, source section, evidence IDs,
   call to action, and review status in metadata.
4. Review for truncation, lost context, unsupported certainty, byline drift, accessibility, and
   platform-sensitive claims. Spread scheduling recommendations across days/weeks rather than
   dumping all atoms at once.
5. For batch work, create one Job per source revision unless the parent Run explicitly records all
   source revision inputs. Failed sources must not erase completed Results.

## Stage completion and export

Write `jobs/<job-id>/atomization/manifest.json`, then return its canonical content and a typed
payload containing `sourceCollection`, `sourceContentId`, `sourceDraftRevisionId`, and the atom
array. Identity must match the same exact CMS Draft Revision. Include source timestamps,
observation IDs, provenance, and any bounded raw artifact reference.

The master calls `content_pipeline_stage_complete` to derive the receipt and create/accept the
immutable Atomization Result. The manifest can be transformed locally to JSON, Markdown, text, or
CSV for downstream tools, but exports remain derived from native state. Do not call granular Result
operations, post, email, schedule, or advertise without the owning reviewed integration.
