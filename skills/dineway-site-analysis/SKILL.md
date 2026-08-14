---
name: dineway-site-analysis
description: Learn a Dineway site's brand, bylines, content inventory, internal-link graph, competitors, locales, collections, and opportunity gaps. Use before content planning, when onboarding a site, refreshing brand/byline understanding, auditing crawl health, finding cannibalization or orphan pages, or establishing the Before Loop context.
---

# Dineway Site Analysis

Build a source-attributed view of how the site writes, what it covers, how its pages connect, and
who currently competes for priority demand. Keep analysis in the Agent; persist only deterministic
evidence and approved Site Context updates.

## Workflow

1. Read the native Site Briefing, Site Context, collections, field schemas, locales, bylines, and
   published content inventory.
2. Crawl the site's public pages locally with bounded same-origin scope. Prefer direct HTTP parsing;
   use Browser Use only for pages that require rendering or interaction. Record URL, status,
   canonical, title, headings, metadata, structured data, word count, internal links, locale,
   collection/content identity when known, and collection time.
3. Detect deterministic inventory findings: broken links, redirect chains, canonical conflicts,
   missing metadata, isolated pages, weak inbound links, duplicate topics, and probable keyword
   conflict. Treat semantic conflict as an Agent conclusion linked to page evidence, not crawler
   truth.
4. Learn each byline separately. Read its native profile and a representative set of published
   work; document tone, point of view, sentence rhythm, vocabulary, evidence habits, openings,
   transitions, calls to action, and prohibited imitation shortcuts. Do not collapse distinct
   bylines into one brand voice.
5. Map current topic coverage, translation families, clusters, conversion paths, and content
   strengths. Use `dineway-seo-cluster` when a formal cluster/internal-link plan is needed.
6. For priority markets, obtain live SERP and competitor evidence. Use bounded local/Browse
   collection where practical; use Forgeway DataForSEO or Firecrawl for infrastructure-scale or
   API-key data. Separate raw evidence from competitive conclusions.
7. Record source-attributed observations through the Content Pipeline MCP tools. Create or
   update Site Context only through native reviewed paths.
8. Request `content_pipeline_source_snapshot_get` for the source kinds used in the analysis.
   Resolve `not_observed` entries by collecting evidence or recording the actual unavailable state,
   then capture the final snapshot in the evidence manifest. Follow
   `../dineway-content-pipeline/references/listen-contract.md` for validity and suppression.

## Output

Return:

- `Site and Schema Inventory`
- `Byline Profiles and Samples`
- `Content and Internal-Link Map`
- `Technical/Crawl Findings`
- `Competitor and SERP Evidence`
- `Source Availability`
- `Opportunity Inputs`
- `Site Context Proposals`

For use inside the master loop, store derived evidence under
`.dineway/content/site-analysis/<analysis-key>/`. When executed as a Pipeline Stage, return the
canonical artifact contents and a typed `site_analysis` payload with artifact refs, provenance,
source timestamps, and observation IDs. The master calls `content_pipeline_stage_complete` to
derive receipts and create and accept the immutable Result. Never call granular Result operations or
store credentials, private PII, or unbounded page dumps.

## Boundaries

- Do not add a top-level deterministic `sites analyze` command; this analysis is Agent reasoning.
- Do not use hosted first-party crawling when local crawl or Browser Use can collect the data.
- Do not route user-owned GSC credentials through Forgeway.
- Do not fabricate traffic, rank, citation, or competitor metrics when a source is unavailable.
- Do not rewrite content during analysis. Produce evidence and opportunities for the master loop.
