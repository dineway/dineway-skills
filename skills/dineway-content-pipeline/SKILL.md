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

1. Read the Site Briefing, Site Context, schema, bylines, current content identity, active Pipeline
   policies, and `content_pipeline_agent_wake_plan_get`.
2. Call `content_pipeline_run_start` immediately. Pass `runId` only to resume an explicitly known
   compatible Run; never coalesce work by title or objective.
3. Call `content_pipeline_status_get`. If it reports Handoff, failed/blocked work, Draft drift, or
   overdue capacity, resolve that state before normal production.
4. Cache the native status plus current CMS content and release-readiness response in
   `.dineway/content/runs/<run-id>/native-state.json`, then run:

   ```bash
   python3 scripts/scan_content_work.py --workspace <site-root> --run <run-id> --write --pretty
   ```

5. Trust native `currentStage`, `nextAction`, and timing. Local scanner recovery actions may only
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
action. Never hand-build a Result envelope, byte count, hash, or acceptance write.

### Research

Call `content_pipeline_stage_begin` with stage `research` before collecting evidence. Run
`dineway-content-research`, recording explicit source availability and observation IDs. Complete
with canonical `research/evidence.json` and `research/findings.md` content plus the typed Research
payload and source timestamps. Valid Research is accepted in that Complete boundary.

### Brief

Begin `brief`; native state resolves and binds the latest accepted Research Result version. Run
`dineway-content-brief` and complete with `brief/brief.md` plus the typed Brief payload. Brief
acceptance is the single human governance decision in this lifecycle: an authenticated human must
complete or replay the stage with `briefApproval.confirmed=true`. API-token and system actors cannot
approve it. Do not start Writer until native status returns `begin_writer`.

### Writer

Begin `writer` with the target identity; native state resolves and binds the accepted Brief version.
Run `dineway-content-writer`. After structural validation, create or update the native CMS Draft
once. Complete with the CMS Draft receipt artifact and a Draft Result containing collection, content
ID, exact Draft Revision ID, revision token, and schema fingerprint. Refresh CMS state before
Complete.

### Optimization and Preview QA

Begin `optimization` against the exact Writer Draft. Run `dineway-content-optimize`; evidence-linked
edits may create newer Draft Revisions. Perform one complete Preview QA on the final exact Draft:

- schema and identity;
- rendered structure and required media/accessibility;
- SEO crawl and package checks;
- source provenance and unresolved rules; and
- final SEO/GEO/brand/evidence/structure/readability scores.

Complete Optimization once with the final report, suggestion decisions, score history, mandatory
gate results, and exact current Draft identity. If `deepGeoEnabled` is true, run a separate
`geo_optimization` Begin/Complete against the same Draft; otherwise proceed directly to Attestation.

## Derived Quality Attestation

Call `content_pipeline_quality_attestation_derive` after Optimization and optional deep GEO are
accepted. Supply only:

- Run ID;
- collection and content ID;
- additional non-derivable QA observation IDs; and
- an idempotency key.

The service derives the current Draft Revision, Schema fingerprint, active policy version, accepted
Research/Brief/Writer/Optimization and optional GEO Result IDs, canonical artifact fingerprints,
media IDs, mandatory gates, scores, and Result observation lineage. Never submit those stable
bindings manually. A Draft, Schema, policy, accepted Result, media, or evidence change invalidates
the Attestation fail-closed.

## Release readiness, Review, and publish

Before requesting approval or publishing, call the read-only `content_release_readiness` tool. It
returns every current blocker in one response, including actor/operation, exact Draft, Review,
release authorization, Quality Attestation, Schema/media evidence, calendar policy/capacity, and
schedule-time problems. It creates no grant, reservation, or approval state.

Resolve all blockers, submit one exact-Draft editorial Review Request, and wait for human approval.
For token actors, create and obtain approval for the exact release request. Re-run readiness with
the Review and release IDs. Publish only when `ready=true` and the response says `publish`.

Use `content_publish` or `dineway content publish`. The successful response includes the durable
publication receipt derived from the consumed release grant: exact Draft/Live Revision IDs, Review,
release authorization, action hash, policy contributions, actor, and timestamps. Save that returned
receipt directly; do not assemble a local substitute or wait for a second receipt step.

## Post-publish verification

The full Preview QA already ran before release. After publish, perform only a lightweight live
check:

1. expected title;
2. expected Live Revision ID;
3. expected card/item count where relevant;
4. required images load; and
5. no visible error state.

Do not repeat the full crawl, schema audit, or package check unless the live check detects drift.

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

Refresh native status and CMS identity, save the returned native Result/publication receipts,
rerun the scanner, and use `scripts/benchmark_pipeline_trace.py` for equivalent-scenario performance
evidence. Report:

- current Run and stage;
- accepted Results and exact Draft/Live Revision;
- elapsed, Agent-work, and orchestration timing;
- all remaining readiness blockers and human decisions;
- source unavailability; and
- native next action.

If responsibility moves, create a native Handoff. Do not leave ownership only in a local note.
