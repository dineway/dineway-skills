# Content Loop Workflow Policy

## Eligibility and the three-day window

- Recompute the dynamic calendar from current native opportunities, score snapshots, monitoring,
  Listen/Research signals, reservations, source availability, and site timezone.
- Reserve work only when its Assignment enters the local three-day execution window.
- Respect the configured site target and every conjunctive site, collection, byline, and locale
  ceiling. Hard defaults are at most 100 Drafts and 100 Publishes per site per day and at most 10 of
  each per collection, byline, and locale per day.
- Never use these defaults as proof that capacity exists. Read the active versioned policy and
  reservation state.
- When active scheduled work is explicitly deferred, dismissed, or superseded, cancel its native
  Assignment and release its still-reserved Draft capacity in the same transaction. Keep consumed
  Draft capacity consumed because it records work already completed that calendar day.
- Mark missed work overdue. On the next Agent session, re-score and decide whether it still deserves
  Draft or Publish capacity; do not blindly catch up. Apply the decision through
  `content_pipeline_opportunity_reevaluate_overdue`. `resume` replaces the overdue Assignment
  and reserves current-day Draft capacity; `defer`, `dismiss`, and `supersede` detach terminal work
  without creating a replacement.

## Priority evidence

Explain, version, and cite every score snapshot. Use the active public four-factor policy:

- Impact: 35%;
- Inverse Effort: 25%;
- Speed: 20%; and
- Strategic Value: 20%.

Unavailable factors use a `null` value and zero confidence. The Agent supplies values and
explanations from linked evidence; the plugin renormalizes available weights, calculates the final
score, and atomically updates opportunity priority. Always record the policy version, expected
opportunity version, observation IDs, priority explanation, and rationale artifact reference.

## Stage invalidation

Re-run Research when material evidence expires, the target query/market changes, or source
availability invalidates a key conclusion. Invalidate later stages when their inputs change:

- Research change invalidates Brief, Draft, and Optimize.
- Brief scope, byline, locale, collection, or content identity change invalidates Draft and Optimize.
- Draft data or media change invalidates Optimize, deep GEO, quality attestation, and exact-Draft review.
- Accepted Result selection changes block downstream Jobs whose recorded input Result version is stale.
- Schedule-time or calendar-policy change invalidates release authorization, not unchanged editorial
  approval.
- Draft Revision change invalidates editorial approval and release authorization.

## Human gates

- Require an authenticated human to confirm the Brief inside Brief Stage Complete; that same
  transaction creates and accepts the immutable Brief Result before Writer starts.
- Store generated output immediately as a native Draft after Writer structural validation.
- Require accepted Optimization and any policy-required deep GEO Result to reference that exact
  current Draft Revision before quality attestation.
- Bind editorial approval to the exact Draft Revision and Live base.
- Bind release authorization to the approved Draft, operation, schedule time, timezone, actor, and
  active capacity policy.
- Treat unresolved rule conflicts, unavailable required evidence, missing media/accessibility data,
  stale native state, and exhausted capacity as blocking.

## Monitor and Fix

- Collect evidence locally or through an allowed managed data provider, but evaluate normalized
  observations only under the active versioned plugin policy.
- Let degraded evidence update availability without changing healthy metric baselines or
  suppressing other sources.
- Treat the monitor state cursor as ordered: replay the same observation; reject a different
  observation at or before the last evaluated time.
- Never let Monitor write content. A deterministic trigger may link one active Fix opportunity to
  the existing content ID; only an accepted Fix enters Research → Brief → Draft → Optimize.
- Complete Fix execution only after the native update path creates a Draft Revision different from
  the Assignment baseline for the same content ID.

## Recovery

- Use Pipeline Job Assignment and Handoff state for specialist ownership and cross-client resume;
  use native calendar Assignment state for scheduled opportunity capacity.
- Capture Assignment Handoffs with the exact Assignment reference. Native capture updates the
  Assignment's latest Handoff link; a fresh client resumes that exact snapshot and consumes its
  deterministic diff before continuing stage work.
- Use `.dineway/content/runs/<run-id>/jobs/<job-id>/` artifacts to avoid repeating reasoning, but
  verify their hashes, immutable Result receipts, and native inputs.
- Treat recurring execution as at-least-once. Use native dedupe keys and idempotency keys for every
  observation, opportunity, score, review, schedule, and publication mutation.
- On partial failure, refresh native state before retrying; do not infer whether a write committed.
