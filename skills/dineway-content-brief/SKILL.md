---
name: dineway-content-brief
description: Convert an accepted Dineway Research Result into one Writer-ready, evidence-linked Brief Result with human approval.
---

# Dineway Content Brief

Execute one Brief Stage that the master Pipeline already began. Use only the accepted Research
Result as evidence authority. Return one structured Brief payload; Stage Complete renders the
canonical Markdown and derives its receipt.

## Required inputs

- Current Run, Brief Job, active Assignment/Attempt, and exact accepted Research Result ID/version.
- Accepted Research payload, plus its derived `evidence.json` and `findings.md` only as readable
  projections.
- Native collection/content identity, locale/market, byline, current schema fingerprint, Site
  Briefing, Site Context, applicable template, and public content inventory.

Stop if the accepted Research selection changed, required evidence expired, or native provenance
does not match the derived Research projections. Do not rerun hidden research inside Brief.

## Writer-ready Brief

1. Preserve Research topic, market, audience, objective, keyword metrics, intent, relevant
   questions, competitor gaps, and evidence lineage.
2. Choose exactly one primary target keyword. Secondary keywords preserve their Research metrics,
   intent, category, and Observation IDs. Record primary and secondary search intent explicitly.
3. Define audience role, expertise, pain point, funnel stage, voice, objective, unique angle,
   subjects, required topics, exclusions, and risky-claim guardrails.
4. Produce a single ordered outline with these required section types:
   - exactly one `direct_answer`;
   - exactly one `at_a_glance`;
   - one `subject` section per declared subject, grouped under `subject_sections`;
   - exactly one `methodology`;
   - optional `faq` using only Research questions marked `included` and `includeInFaq=true`; and
   - exactly one `cta`.
5. Give every section a stable ID, heading, level, format, required key points, evidence Observation
   IDs, question bindings, and word budget. Required key points must have Observation
   lineage. Section budgets must total within ten percent of the target word count.
6. Carry only approved Research questions. Rejected questions retain their reason in Research and
   cannot enter Brief, the outline, or FAQ.
7. Add verified internal-link candidates by stable public URL plus media purpose, alt-text intent,
   optional generation prompt, and whether each item is required.
8. Bind the Brief to the exact Research Result, collection, optional existing content ID,
   translation group, locale, byline, and schema fingerprint.

Never invent menu, hours, price, allergen, award, review, staff, medical, legal, or financial facts.
Do not hide optional ideas among required scope.

## Stage completion

Return only the typed Brief payload, provenance, source timestamps, and the union of persisted
Observation IDs. Do not build an `artifactRef`, Result envelope, Markdown wrapper, hash, byte count,
or acceptance write.

An authenticated human reviews the structured Brief and calls `content_pipeline_stage_complete`
with `briefApproval.confirmed=true`. API-token and system actors cannot approve it. The transaction
validates Research inheritance and outline completeness, renders:

- `.dineway/content/runs/<run-id>/jobs/<job-id>/brief/brief.md`;

then derives its receipt, verifies every Observation, creates schema-version-2 Brief, accepts it,
and returns `begin_writer`. Do not call granular Result/accept operations or mutate a CMS Draft from
this Skill.
