---
name: dineway-content-pipeline
description: Orchestrate Dineway's run-first Research, Brief, Draft, Optimize, release, publish, Monitor, and Fix workflow through native stage-level transactions and exact-Draft governance.
---

# Dineway Content Pipeline

Use this Skill as the master Agent protocol. Specialist Skills perform research, writing, and
optimization judgment. Native Pipeline state owns Runs, Jobs, Assignments, Attempts, Results,
Handoffs, timing, and next actions. Dineway CMS owns Draft and Live Revisions. Local
`.dineway/content/` files are reconstructable working evidence only.

## Required references

Read `references/artifact-contract.md`, `references/workflow-policy.md`,
`references/local-scheduling.md`, and `references/listen-contract.md` before changing state.
Read `references/performance-benchmark.md` when measuring or reporting Pipeline speed.

## Invariants

- Read [`dineway-cli`](../dineway-cli/SKILL.md) before running the capability preflight below.
- Run exactly one `content_pipeline_capabilities_get` preflight before the first mutation (CLI:
  `dineway pipeline capabilities`). Proceed only when compact Context, batch Observations, Run Start,
  Stage Begin/Complete, Draft assembly, atomic quality completion, connection readiness, and actor
  write readiness are present. If `ready=false`, perform only the returned action. Do not retry
  diagnosis and do not fall back to granular lifecycle writes.
- Start or explicitly resume the native Run before Research creates its first artifact.
- Follow `content_pipeline_status_get.currentStage` and `.nextAction`; do not rebuild normal routing
  from local files.
- Use `content_pipeline_stage_begin` and `content_pipeline_stage_complete` for production work.
  Granular Job, Assignment, Attempt, Result-record, and Result-accept writes are internal invariants,
  not an Agent workflow.
- Treat every retry as at-least-once. Reuse stable idempotency keys, refresh native state after an
  ambiguous response, and never infer whether a write committed.
- Never copy article bodies into Pipeline Result authority. Writer and Fix Results bind the native
  content identity and exact Draft Revision.
- Never weaken exact-Draft Review, Quality Attestation, schema, media, calendar, role, CSRF, or
  release-authorization gates to save time.
- Deep GEO is optional unless `run.metadata.deepGeoEnabled` is exactly `true`.
- AI reasoning stays in specialist Skills. Deterministic surfaces persist, validate, coordinate,
  authorize, and report; they do not hide model execution.

## Entry and recovery

1. Run the single capability and authentication preflight above.
2. Call `content_pipeline_run_start` immediately. Pass `runId` only to resume an explicitly known
   compatible Run; never coalesce work by title or objective.
3. Call `content_pipeline_context_get` once. Use its bounded content identity, schema fingerprint and
   fields, Site Briefing entries, valid Observation summaries, accepted Result receipts, and wake
   action. Do not rediscover these through separate status, schema, policy, and identity reads.
4. Call `content_pipeline_status_get` only for explicit resume or recovery, using the default summary
   response. Request `full` only for diagnosis. If it reports Handoff,
   failed/blocked work, Draft drift, or overdue capacity, resolve that state before normal production.
5. Only for explicit recovery or Handoff, cache the native status plus current CMS content and
   release-readiness response in `.dineway/content/runs/<run-id>/native-state.json`, then run:

   ```bash
   python3 scripts/scan_content_work.py --workspace <site-root> --run <run-id> --write --pretty
   ```

6. On a healthy path, trust every Start/Begin/Complete response and do not insert status/scanner
   refreshes between Stages. Local scanner recovery actions may only
   require refreshing corrupt/missing cache artifacts or reconciling an authoritative Handoff,
   Assignment, Attempt, Draft, or calendar state.

## Standard four-stage protocol

The standard production lifecycle uses no more than nine state-changing lifecycle calls:

1. one `content_pipeline_run_start`;
2. Research Begin + Complete;
3. Brief Begin + Complete;
4. Writer Begin + Complete; and
5. Optimization Begin + Complete.

Each Begin atomically creates or reuses the compatible Job, active Assignment, and running Attempt.
Do specialist work outside the transaction. Each Complete atomically validates the typed payload,
derives SHA-256/UTF-8 byte receipts from canonical artifacts, records immutable provenance and
observations, finishes the Attempt and Assignment, applies acceptance policy, and returns the next
action. Each Complete validates the stage's compact decisions, source, assessment, or optional typed
artifact input. Never hand-build a Result envelope, byte count, hash, or acceptance write.

### Research

Call `content_pipeline_stage_begin` with stage `research` before collecting evidence. Run
`dineway-content-research`. For every Research type, use Dineway Tools to start organic SERP
analysis as the first evidence operation; only after it starts may keyword metrics, competitors,
questions, official sources, Site Context, and first-party inventory run concurrently. Record
explicit availability, numeric metrics or `null`, and bounded lineage in one idempotent Observation
batch. Complete with compact editorial decisions and the selected Observation IDs. The server
hydrates authoritative evidence, validates SERP-first ordering, compiles the canonical Research
Result, renders `research/evidence.json` and
`research/findings.md`, derives both receipts, and accepts Research. Do not perform free-form
browser research or send caller-built Result/artifact wrappers.

### Brief

Begin `brief`; native state resolves and binds the latest accepted Research Result. Run
`dineway-content-brief` using that Result as the only evidence authority. Return only editorial
selections: target keyword, audience/voice choices, required topics/guardrails, internal-link and
media choices, approved questions, and the ordered outline. The server copies metrics, evidence,
identity, locale, schema, and upstream bindings from authoritative state, compiles the Writer-ready
Brief, renders `brief/brief.md`, and derives its receipt. Brief
acceptance is the single human governance decision in this lifecycle: an authenticated human must
complete or replay the stage with `briefApproval.confirmed=true`. API-token and system actors cannot
approve it. Do not start Writer until native status returns `begin_writer`.

### Writer

Begin `writer` with the target identity; native state resolves and binds the accepted Brief. Run
`dineway-content-writer` and write one schema-aware source object with ordered sections/cards, final
copy, media IDs, and required accessibility metadata such as `imageAlt`. With CLI, pass it through
`dineway pipeline stages complete --source-file <path>`; the CLI reads the file locally and submits
its object. The Dineway backend validates the database-owned schema and media, assembles canonical
CMS JSON deterministically, writes one Draft Revision, derives the content fingerprint, creates the
Writer Result, and returns only a compact receipt. Do not call CMS create/update separately.

### Optimization and content QA

Begin `optimization` against the exact Writer Draft. Run `dineway-content-optimize` as an audit by
default. Perform one complete content QA on that exact Draft:

- schema and identity;
- Brief coverage, heading structure, and required media/accessibility metadata;
- SEO metadata, canonical/robots, internal links, and structured data through native interfaces;
- source provenance and unresolved rules; and
- final SEO/GEO/brand/evidence/structure/readability scores.

This is content and governance QA through CLI, MCP, or native interfaces. Do not open a browser,
take screenshots, inspect lazy loading, test responsive layout, or perform interaction/rendering QA.

Complete with the compact assessment. When every mandatory check passes, do not submit content and
do not create another Draft. If blocking findings require content changes, include one consolidated
`remediationSource`; the backend permits one newer Draft and records the Writer source Draft → final
Draft lineage without a Writer rebind. If `deepGeoEnabled` is true, run a separate
`geo_optimization` Begin/Complete against the final Draft.

## Atomic final-quality boundary

The final Optimization Complete—or optional deep-GEO Complete—preflights current Draft identity,
schema, accepted upstream Results, explicit source/final lineage, media, evidence, scores, gates, and
server-derived fingerprint. It commits Result acceptance and Quality Attestation in one transaction
or commits neither, then returns `inspect_release_readiness`. There is no separate Agent Attestation
mutation. A later Draft, Schema, policy, accepted Result, media, or evidence change still invalidates
the Attestation fail-closed.

## Release readiness, Review, and publish

Before requesting approval or publishing, call the read-only `content_release_readiness` tool. It
returns current blockers and warnings separately, including actor/operation, exact Draft, Review,
release authorization, Quality Attestation, Schema/media evidence, calendar policy/capacity, and
schedule-time problems. It creates no grant, reservation, or approval state.

Quality Policy applicability comes only from accepted Pipeline Writer provenance. Never infer it
from whether the caller is a token, an API client, or a human-facing UI. Content with no accepted
Writer Result is manual and receives no Pipeline quality warning. Content with accepted Writer
provenance remains Pipeline-authored after later human edits; missing or stale exact-Draft quality
evidence is reported as a warning.

Resolve all blockers, submit one exact-Draft editorial Review Request, and wait for human approval.
For token actors, create and obtain approval for the exact release request. Re-run readiness with
the Review and release IDs. Token actors must never submit a policy override: resolve every warning,
then publish only when `ready=true` and the response says `publish`. A signed-in human Admin user may
separately confirm an exact overridable warning; Core binds that confirmation to the current Draft,
Review, warning fingerprint, policy, and authorizing user.

Use `content_publish` or `dineway content publish`. The successful response includes the durable
publication receipt derived from the consumed release grant: exact Draft/Live Revision IDs, Review,
release authorization, action hash, policy contributions, actor, and timestamps. Save that returned
receipt directly; do not assemble a local substitute or wait for a second receipt step.

## Post-publish verification

The full content QA already ran before release. After publish, verify only native publication
state:

1. expected title;
2. expected Live Revision ID;
3. expected card/item count where relevant;
4. required media references remain valid; and
5. no native publish or content error state.

Do not open a browser for this article workflow. Do not repeat the full crawl, schema audit, or
package check unless native state detects drift.

## Optional Jobs, Monitor, and Fix

- Competition, AI Visibility, Atomization, Site Analysis, and Monitor use their typed specialist
  Jobs when native status or the wake plan calls for them.
- Monitor records observations and deterministic evaluation only; it never edits content.
- A qualifying regression creates one deduplicated Fix opportunity for the existing content ID.
  Fix starts/resumes a Run, creates a new Draft Revision, and repeats the same stage, Attestation,
  Review, readiness, and release rules.
- Unsupported NLWeb/Chat Listen sources remain explicitly `not_configured` or `not_observed` until
  their native owner provides the contract.

## Exit

Read native status and CMS identity once for final reporting, save the returned native
Result/publication receipts, and use `scripts/benchmark_pipeline_trace.py` for equivalent-scenario
complete-session performance evidence. Run the local scanner only when recovery or Handoff state
requires it. Report:

- current Run and stage;
- accepted Results and exact Draft/Live Revision;
- Content-ready, Review-ready, benchmark-complete, optional publication, human wait, tool execution,
  Agent reasoning, orchestration, and QA timing;
- lifecycle writes, Agent-to-tool round trips, total tool-output bytes, retries, context compactions,
  rebinding Jobs, late Attestation failures, and browser-QA calls;
- all remaining readiness blockers and human decisions;
- source unavailability; and
- native next action.

If responsibility moves, create a native Handoff. Do not leave ownership only in a local note.
