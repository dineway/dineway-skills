---
name: dineway-content-research
description: Build and persist source-attributed Dineway content research. Use for general, topic, competitor, gap, or SERP research; keywords, live results, evidence, content gaps, competitor structures, topic directions, subtopics, and keyword clusters before a Brief.
---

# Dineway Content Research

Execute one Research Job and return control to `dineway-content-pipeline`. The authoritative output
is a typed immutable Research Result; `evidence.json` and `findings.md` are derived, inspectable
artifacts.

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

## Artifacts and Result

Write:

- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/evidence.json`
- `.dineway/content/runs/<run-id>/jobs/<job-id>/research/findings.md`

Then record a `research` Result with `query`, `researchType`, nullable `depth`, language, country,
nullable summary, findings, sources, keywords, SERP results, evidence, content gaps, competitors,
topic directions, subtopics, keyword clusters, and both artifact refs. Add Result-level provenance,
source timestamps, observation IDs, raw artifact reference, Assignment, Attempt, and input Result
versions. Provenance uses the strict fields `skill`, nullable `skillVersion`, `agentClient`, nullable
`model`, `collector`, source timestamp records, and artifact receipts with exact ref, SHA-256, and
byte count. The evidence and findings receipts must exactly cover both Research artifact refs.

The plugin auto-selects valid Research in the same immutable Result write only when the contract has
at least one available timestamped attributed source, source timestamps, and matching receipts.
Do not make a separate accept call or create a Brief, Draft, or CMS mutation from this Skill.
