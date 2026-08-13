---
name: dineway-content-pipeline
description: Orchestrate Dineway's end-to-end Research, Brief, Draft, Optimize, Publish, Monitor, and Fix workflow. Use to start or resume shared Pipeline Runs, coordinate specialist Skills, manage Assignments and Handoffs, enforce exact CMS Draft Revision review, or execute dynamic content-calendar work.
---

# Dineway Content Pipeline

Coordinate the content workflow; do not absorb specialist judgment. Pipeline plugin state is the
shared authority for Runs, Jobs, Attempts, Results, Assignments, Handoffs, policies, calendar state,
and provenance. Dineway CMS is the authority for article Draft and Live Revisions. Local
`.dineway/content/` files are reconstructable evidence and working cache only.

## Required references

Read `references/artifact-contract.md`, `references/workflow-policy.md`,
`references/local-scheduling.md`, and `references/listen-contract.md` before changing state.

## Hard boundaries

- AI research, writing, classification, clustering, suggestions, and evidence-based dimension
  scoring belong to specialist Skills. CLI and MCP only read, persist, validate, and coordinate.
- Use the `content_pipeline_*` MCP tools inside an Agent. Use `dineway pipeline` for deterministic
  operator/script control only; it has no specialist execution command.
- Never trust local status over `content_pipeline_status_get` and exact CMS reads.
- Never let a stale or expired assignee submit. Every mutation uses the current Assignment and
  optimistic Job or Run version. A retry creates a new Attempt.
- Results are immutable candidates. Acceptance creates selection history; it never edits a Result.
- Never copy an article body into Pipeline Result authority. Writer and Fix Result payloads contain
  the native CMS identity and exact Draft Revision only.
- Never publish generated content directly. Exact-Draft rules, quality attestation, human review,
  release authorization, and calendar capacity remain separate gates.
- Do not implement NLWeb/Chat Listen. Record that source as `not_configured` or `not_observed` until
  its native owner exists.

## Session entry and recovery

1. Read the current Site Briefing, Site Context, bylines, schema, content identity, active Pipeline
   policies, and `content_pipeline_agent_wake_plan_get` response.
2. List Runs relevant to the selected opportunity/content. Create a Run only when no active Run
   represents the same work. Otherwise call `content_pipeline_status_get` and resume it.
3. Refresh `.dineway/content/runs/<run-id>/native-state.json` with the current Run status, Jobs,
   active Assignments, candidate/accepted Results, pending Handoffs, current CMS Draft, review,
   release, observations, and calendar state.
4. Run `python3 scripts/scan_content_work.py --workspace <site-root> --run <run-id> --write --pretty`.
   Follow recovery actions before stage work: refresh a mismatched Handoff/Result receipt, accept or
   reject a Handoff, reacquire expired responsibility, retry a failed Job, refresh a changed Draft,
   or reevaluate overdue calendar work.
5. Process due Monitor evidence before new creation. Recalculate queue priority from current
   evidence. Do not reuse yesterday's ordering.

## Job protocol

For every specialist stage:

1. Create one Job with the exact accepted input Result versions and current CMS identity where
   applicable. Never infer an input version from a local file.
2. Create or receive the single active Assignment. A different Agent must use a Handoff.
3. Start an Attempt with the current Job version. Use Attempt updates to record monotonic 0-99
   progress, bounded partial artifact references, and `running`/`blocked` state. Record a failed
   Attempt explicitly before retrying; completion to 100 happens only when a Result is recorded.
4. Invoke only the narrow child Skill. It must return control after recording one typed Result.
5. Record the candidate Result through `content_pipeline_result_record`, including provenance,
   source times, observation IDs, raw artifact reference, Assignment/Attempt identity, and exact
   Draft Revision where applicable.
6. Refresh authoritative status, save the returned Result unchanged as
   `jobs/<job-id>/result-receipt.json`, rerun the scanner, then accept or await approval as defined
   below.

## Research → Brief → Draft → Optimize

### Research

Run `dineway-content-research`. It writes `research/evidence.json` and `research/findings.md`, then
records a typed Research Result aligned to the source research contract. Valid Research is selected
automatically by the plugin in the same authoritative write after schema and score validation; the
Skill must validate source provenance and artifact receipt matching before submission. Missing
metrics remain `null` and unavailable sources remain explicit.

### Brief

Create the Brief Job with the accepted Research Result ID/version and run
`dineway-content-brief`. The Brief Result must preserve the exact Research input and outline
contract. Stop after candidate submission. A human operator reviews the artifact and explicitly
accepts it through a human-authenticated Dineway surface. Agent/API-token actors are rejected for
Brief acceptance and must not silently approve it.

### Draft

Create the Writer Job only from the accepted Brief version and run `dineway-content-writer`.
Immediately after structural/schema validation, use `dineway content create --draft` for new
content or `dineway content update --draft --rev <current-revision>` for an existing item. Record a
Draft Result containing only collection, content ID, exact Draft Revision ID, revision token, and
schema fingerprint. Refresh CMS state before acceptance.

### Optimize

Create the Optimization Job against that exact Draft Result and run
`dineway-content-optimize`. Its public Content Score is the rounded mean of measured SEO and GEO;
when only one is measured that value is retained, and when neither is measured the score is
`null`. Evidence-linked edits create explicit newer CMS Draft Revisions. Record every before/after
score and suggestion decision. The final Optimization Result must reference the current Draft.

Run `dineway-content-geo-optimize` as a separate Job when the active policy or content value calls
for deep citation analysis. Its independent GEO score covers quotability, answer structure,
citation readiness, and entity clarity; it does not replace the normal Content Score.

## Optional specialist Jobs

- `dineway-content-competition`: acquire competitor evidence, then reason locally about gaps,
  opportunity score, and clusters.
- `dineway-content-ai-visibility`: observe supported AI web clients through Browser Use or the
  user's own Agent client and record per-platform evidence.
- `dineway-content-atomization`: derive channel assets from an exact native Draft/Live Revision;
  atoms live in their Result, never as a duplicate article authority.
- `dineway-site-analysis`: learn site, bylines, inventory, internal links, crawl health, and
  cannibalization before or alongside the main flow.

## Review, release, and publish

After the current Optimization and required deep-GEO Results are accepted, reread the current CMS
Draft. Record quality attestation only when every accepted revision-bound Result references that
same Draft Revision, all mandatory gates pass, quality policy versions are current, and local
artifact receipts match native Results. Aggregate scores cannot bypass a failed gate.

Submit a native Review Request for the exact Draft. After approval and release authorization, use
`dineway content schedule` for the existing content ID and approved revision. Direct publication
requires an explicit operator decision and identical gates. Any material edit invalidates the
attestation, approval, and release readiness for the prior revision.

## Monitor and Fix

Run `dineway-content-monitor` only for due sources. It records observations and deterministic
evaluation receipts; it never edits content. A qualifying regression creates one deduplicated Fix
trigger and linked opportunity. Fix reuses the same CMS content identity, creates a new Run/Jobs as
needed, writes a new Draft Revision, and repeats Optimization, review, and release.

## Calendar and local activation

Codex Scheduled or an equivalent local scheduler may activate this Skill within the rolling
three-day execution opportunity. It does not own state. Respect hard daily ceilings of 100 Draft
and 100 Publish operations per site and 10 per collection, byline, or locale, plus lower active
targets. Mark missed work overdue and reevaluate it next session before resuming or publishing.

## Session exit

Refresh native state, rerun the scanner, and record the exact next action. If responsibility moves,
create a Pipeline Handoff rather than writing instructions only in a local note. Report separately:
completed Results, current Run/Job/Attempt, exact CMS Draft, blockers, human decisions, source
unavailability, and next action.
