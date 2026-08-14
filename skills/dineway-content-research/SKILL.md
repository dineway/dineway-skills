---
name: dineway-content-research
description: Build and persist source-attributed Dineway content research. Use for general, topic, competitor, gap, or SERP research; keywords, live results, evidence, content gaps, competitor structures, topic directions, subtopics, and keyword clusters before a Brief.
---

# Dineway Content Research

Execute one Research Stage that the master Pipeline already began, then return canonical artifacts
and the typed payload to `dineway-content-pipeline`. Native Stage Complete creates the authoritative
immutable Research Result; `evidence.json` and `findings.md` remain inspectable working artifacts.

## Inputs

- Pipeline Run, Research Job, active Assignment/Attempt, objective, locale/market, and site identity.
- Research type: `general`, `topic`, `competitor`, `gap`, or `serp`.
- Query, optional depth, language, country, competitor domains, audience, objective, and focus.
- Site Briefing, Site Context, schema, published inventory, byline context, prior observations, and
  explicit first-party-question availability.

## Evidence order

1. Native Dineway content, Site Context, published pages, and available first-party questions.
2. User-owned GSC or analytics through the user's local authenticated connector.
3. Bounded local crawl and Browser Use for site, competitor, SERP, and AI-answer evidence.
4. Forgeway DataForSEO/Firecrawl only for managed-key or infrastructure-heavy acquisition.

Never place credentials, cookies, private exports, or unbounded page bodies in artifacts. Record
unavailable sources explicitly; a missing metric is `null`, not zero.

## Workflow

1. Restate the research question, type, audience, locale, objective, focus, and completion criteria.
2. Collect and normalize source records with URL, title, snippet, domain, collected time,
   availability, observation ID, and bounded raw artifact reference.
3. Produce source-aligned findings with title, content, 0-1 relevance when measurable, and source
   URLs.
4. For general research, collect:
   - keywords with search volume, `Low|Medium|High` difficulty, CPC, intent, category, and evidence;
   - SERP results with URL, title, domain, rank, word count, site/competitor flags, and headings;
   - evidence items classified as `stat`, `fact`, or `quote` with attribution;
   - content gaps with high/medium/low impact and competitor count.
5. For competitor research, retain competitor domain, URL, title, rank, word count, headings, and
   observation IDs. Use `dineway-content-competition` for deeper gap judgment.
6. For topic research, retain topic directions with angle/difficulty, subtopics with relevance and
   search volume, and keyword clusters with total volume.
7. Identify current search/visitor intent, risky claims, differentiation, and internal-link
   candidates in `findings.md`; do not add non-contract fields to normalized JSON when raw evidence
   can preserve them losslessly.

## Artifacts and Stage completion

Write:

- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/evidence.json`
- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/findings.md`

Return both artifact contents plus a typed payload containing `query`, `researchType`, nullable
`depth`, language, country, nullable summary, findings, sources, keywords, SERP results, evidence,
content gaps, competitors, topic directions, subtopics, keyword clusters, and both artifact refs.
Also return strict provenance, source timestamps, observation IDs, and any bounded raw artifact
reference. Do not calculate artifact hashes or byte counts.

The master calls `content_pipeline_stage_complete`, which derives receipts, finishes the native
Attempt and Assignment, creates the immutable Research Result, and accepts it only when at least one
available timestamped attributed source and matching evidence are present. Do not call granular
Result or acceptance operations or create a Brief, Draft, or CMS mutation from this Skill.
