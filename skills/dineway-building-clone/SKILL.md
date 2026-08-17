---
name: dineway-building-clone
description: Plan and execute pixel-faithful, CMS-backed Dineway website clones from one or more explicit URLs. First generates and validates a durable clone-specific agent plan containing the full reconnaissance, one-hop discovery, public source data-layer/API audit, field-aligned Dineway content modeling, component specification, focused builder, route assembly, visual QA, and hard-gate workflow; then hands execution to a Codex goal. Use whenever the user asks to clone, replicate, rebuild, reverse-engineer, copy, or migrate a website into Dineway or Astro.
---

# Plan and Execute a Dineway Website Clone

Convert every clone request into a durable, validated agent protocol before implementation. The
planning turn resolves scope and writes the agent. The goal follows that agent until every hard
gate is proven.

<HARD-GATE>
Do not write site implementation code, scaffold a Dineway Site, download implementation assets,
edit seed/schema, dispatch builders, or begin visual construction from this skill directly.

First generate a clone-specific agent file from
`references/clone-agent-template.md`, replace every placeholder with request- and source-specific
evidence, validate it with `scripts/validate_clone_agent.py`, and only then hand execution to a
goal. A regular chat plan, task list, `update_plan` call, or `OUTPUT_PLAN.md` is not a substitute for
the durable clone agent.
</HARD-GATE>

## Default Workflow

Use this workflow silently; do not ask the user to choose a template:

1. **Explore:** understand the explicit URLs, requested customizations, repository, and target root.
2. **Plan:** perform read-only URL discovery and resolve the route, artifact, content, and change-budget scope.
3. **Agent:** generate and validate `clone-agents/<slug>/agent-<slug>.md` from the bundled template.
4. **Refine:** apply requested changes only to the generated agent before execution.
5. **Execute:** after explicit post-plan confirmation, create a goal that follows the generated
   agent and implements until all gates pass.

Append exactly one of these progress lines at the end of every user-facing Agent or Refine phase
message, translated when useful. Keep it as the final line; do not omit it while awaiting execution
confirmation:

```text
✓ Explore  ● Plan  ○ Agent  ○ Refine  ○ Execute
✓ Explore  ✓ Plan  ● Agent  ○ Refine  ○ Execute
✓ Explore  ✓ Plan  ✓ Agent  ● Refine  ○ Execute
✓ Explore  ✓ Plan  ✓ Agent  ✓ Refine  ● Execute
```

## Step 1: Load Required Guidance

Read these before generating the agent:

1. `references/clone-agent-template.md` in full. It is the normative execution contract and retains
   the original clone workflow plus Dineway adaptations and failure gates.
2. `$dineway-brainstorming` for request, scope, and change-budget decisions. Use the
   source-fidelity-preserving recommendation when it is safe; ask only when the choice truly needs
   user authority or would materially change scope.
3. `$dineway-building-site` for current Dineway boundaries that affect the agent.

The generated agent must itself retain the template's required use of:

- `$dineway-brainstorming`
- `$dineway-frontend-design` in source-fidelity mode
- `$dineway-planning-with-files`
- `$dineway-building-site`
- `## Commit and PR Discipline`

Do not apply `$dineway-frontend-design` creatively during planning. The source site, not an
invented theme, is the visual authority.

## Step 2: Resolve the Clone Brief

Extract a dual-layer clone brief from the request and project evidence.

### User and source layer

Record:

- Original request and explicit HTTP(S) URLs
- Target identity/origin and approved Dineway Site root
- Requested customizations or exclusions
- Expected fidelity and user-visible done criteria
- Explicitly out-of-scope backend/private behavior

### Engineering and verification layer

Record:

- Astro SSR and Dineway content/runtime boundaries
- Existing routes, user-owned files, schema, seed, assets, and collision risks
- Public source data surfaces: document/hydration payloads, JSON-LD, REST or GraphQL read requests,
  response entities, field shapes, identifiers, relationships, filtering, ordering, and pagination
- A browser-produced, complete per-page visible-content snapshot covering text, media, links,
  navigation, and repeated items before any audit/model artifact is derived
- A source-to-Dineway field map that preserves source semantics and uses camelCase canonical Dineway
  CMS field names/labels plus explicit lower_snake_case `storageSlug` values required internally by
  the current schema runtime and the exact public `runtimeReadPath`
- Browser, build, seed, type, admin, route, interaction, and visual-diff verification
- Exact failure thresholds and evidence artifacts
- System impact and protected existing behavior

### Change budget

Create an explicit allowlist of approved differences. Everything else remains source-locked.

- A renamed brand does not permit a new palette, layout, information architecture, content section,
  type scale, interaction, or responsive behavior unless separately approved.
- An excluded banner removes that banner and its occupied space only; it does not justify redesigning
  the header or surrounding sections.
- Rewritten editorial content may change only the approved text/media while preserving measured
  geometry unless the user explicitly approved a structural change.

Do not invent high-risk requirements. Keep unresolved material questions visible and ask only when
the source evidence plus a safe recommendation cannot resolve them.

## Step 3: Perform Read-Only Scope Discovery

Browser automation is mandatory. Before writing the agent:

1. Normalize and open every explicit URL.
2. Preserve meaningful explicit query/fragment states.
3. Collect rendered same-origin anchors from each explicit page only.
4. Normalize discovered targets by pathname and remove query/fragment.
5. Exclude search, pagination, authentication, admin, non-HTML, downloads, `mailto:`, `tel:`,
   `javascript:`, and cross-origin targets unless explicitly supplied.
6. Do not discover links from discovered pages.
7. Inspect each planned page's public, browser-visible data layer: HTML and script hydration payloads,
   JSON-LD, XHR/fetch requests, and public REST or GraphQL reads. Record endpoint, method, parameters,
   pagination/filter/sort behavior, response entity, field name, observed type/nullability, identifiers,
   relationships/cardinality, media shape, locale/status behavior, and the UI region consuming it.
   First capture every visible text/media/link/repeated item directly from the fully rendered browser
   into `SOURCE_DOCUMENT_SNAPSHOT.json`; never synthesize that snapshot from the later audit.
8. Sample anonymous public read operations only. Do not reuse an existing browser login. Never bypass
   authentication, replay mutations, submit forms, expose tokens/cookies, probe private endpoints,
   or retain secrets, personal/account data, or private PII. If a required source is not anonymous,
   record an evidence gap and request separate explicit authorization rather than sampling it.
9. Record each URL's origin, explicit/discovered status, explicit parent, destination route or route
   family, collection/entry mapping, keys, artifact paths, and collisions.

This pass establishes executable scope. Full screenshots, interaction sweeps, computed styles,
content extraction, and asset downloads remain part of goal execution. During execution, capture
every source master screenshot with `scripts/capture-source-screenshots.mjs`; it must scroll through
the rendered page, wait for image decode and stable document height, capture viewport tiles, and
invoke `scripts/stitch-browser-screenshots.py` before the screenshot becomes evidence.

## Step 4: Resolve the Agent Path

Create a concise 2-5 word kebab-case slug using lowercase letters, numbers, and hyphens only, with
no leading/trailing hyphen and at most 50 characters.

Write the agent under the approved site root:

```text
clone-agents/<slug>/agent-<slug>.md
```

If that path exists, append `-2`, `-3`, and so on. Do not overwrite an existing agent.

## Step 5: Generate the Durable Clone Agent

Copy `references/clone-agent-template.md` into the new agent file and replace every double-brace
placeholder with concrete evidence. Preserve the template's order and every normative section.

Requirements:

- Do not replace the execution contract with “follow `$dineway-building-clone`” or links to docs.
- Do not summarize, omit, rename, or reorder its reconnaissance, Dineway foundation,
  extract/spec/dispatch/merge, assembly, QA, checklist, anti-pattern, or completion sections.
- Keep the route/artifact plan concrete and exhaustive; one generic route-family bullet is not a
  substitute for per-URL rows.
- Fill `## Source Data Layer Audit` and `## Dineway CMS Content Model` with concrete source evidence.
  Every visible source-backed entity and field must have a source/API location, Dineway owner,
  canonical camelCase CMS field name/label, runtime `storageSlug` when it becomes a collection field,
  exact `runtimeReadPath`, Dineway type,
  required/nullability rule, relationship/cardinality, media ownership, and seed/render consumer.
- Preserve source field semantics rather than copying an endpoint response wholesale or inventing a
  frontend-only content shape. Record unknown or inaccessible fields as evidence gaps.
- Inventory every public record with a stable record ID and ordered field tuple. Generate exact
  source-record-to-seed JSON Pointer bindings; distinct-value membership is not record closure.
- Fill both `### Source Record Inventory` and `### Source Record Binding Plan` with deterministic,
  duplicate-preserving rows that match the later JSON artifacts byte-for-value.
- Use only strict anonymous read operations, resolve every response entity and evidence path, reject
  signed URLs/private account data, and keep the agent tables aligned with the execution JSON artifacts.
- Follow the real Dineway runtime contract: custom storage slugs are lower_snake_case, settings media
  uses an imported live `{ mediaId, alt }` reference, collection media uses `$media`, and observed
  many-valued relationships use a link collection rather than an unsupported multi-reference field.
- Require bidirectional closure: every source field/record maps into Dineway and every clone-owned
  custom seed field, data key, and mapped-owner entry maps back to source evidence.
- Require `SETTINGS_MEDIA_PROOF.json` with normalized read-only media/settings GET results for every
  settings media mapping, followed by fresh live GET verification; never accept a ULID or prose
  attestation alone and never persist authentication material.
- Require `SOURCE_DOCUMENT_SNAPSHOT.json` to be a fresh browser-produced visible DOM inventory and
  require `RUNTIME_CONTENT_PROOF.json` to prove every mapped editable field drives its declared SSR
  selector through a reversible local Dineway edit/read/render/restore check.
- Require source and comparison master screenshots to use `capture-source-screenshots.mjs` at exact
  viewports. Reject a capture unless its adjacent `.capture.json` reports decoded rendered images,
  zero `failedImages`, stable final document height, DPR 1 tile dimensions, and a stitched output
  matching that final height.
- Run the artifact closure gate in `--phase foundation` before component dispatch, then require a
  caller-trusted local clone URL and occurrence-level `RUNTIME_CONTENT_PROOF.json` in
  `--phase completion` after the reversible sentinel checks.
- Require query helpers to be imported from Dineway, content reads to apply the returned `cacheHint`,
  localized mappings to match bound seed locales, and every routable entry to resolve to a planned
  destination plus an executable exact or dynamic Astro route.
- Keep approved customizations in the change budget rather than silently changing the execution
  contract.
- Preserve `## Required Skills`, `## Commit and PR Discipline`, and every hard failure gate verbatim
  except for resolved placeholders. Put repository-specific commands inside the
  `{{ENGINEERING_CONSTRAINTS}}` placeholder rather than altering the normative contract.
- Use the user's language for request-specific prose. Keep commands, paths, field names, thresholds,
  and normative identifiers exact.
- Do not write implementation code during this phase.

The agent file is a durable execution protocol, not the live checklist. Goal execution stores
mutable state under `.plan/<slug>/` through `$dineway-planning-with-files`.

## Step 6: Validate Before Goal Handoff

Run:

```bash
python3 <skill-root>/scripts/validate_clone_agent.py clone-agents/<slug>/agent-<slug>.md
```

The validator must prove:

- No unresolved template placeholder remains
- Required skills and commit discipline remain present
- Every original clone phase and Dineway requirement remains present
- Public data-layer evidence, CMS entity mapping, and camelCase/storage-slug naming contracts remain
  present
- Structured `SOURCE_DOCUMENT_SNAPSHOT.json`, `FIELD_MAPPING.json`, and `SETTINGS_MEDIA_PROOF.json`
  contracts plus their bidirectional source/seed/runtime validator remain present
- Foundation and completion validation remain separate so runtime proof is mandatory at completion
  without blocking the foundation build that produces the runnable clone
- Record-level source tuples, exact seed bindings, reference/media validity, and agent/artifact
  alignment remain mandatory
- Every hard gate and visual threshold remains present
- Image-complete tiled source capture and its stitch/readiness metadata remain mandatory
- At least one explicit HTTP(S) URL and a concrete route/artifact plan are present

If validation fails, modify only the agent file and run the validator again. Never create a goal
for an invalid agent.

## Step 7: Refine or Execute

If the user requested only a plan, report that the agent is ready and allow free-form refinement.
During refinement, modify only the generated agent file and revalidate after every change.

After every new or refined agent validates, report that it is ready and wait for explicit
post-plan confirmation to execute. The initial clone/build request authorizes planning and agent
generation, but is not a substitute for this confirmation. A clear response such as “execute”,
“start”, or “implement this agent” authorizes goal creation.

After that confirmation, create a goal with this objective:

```text
Follow clone-agents/<slug>/agent-<slug>.md and implement. Preserve source fidelity, choose the
source-faithful recommended decision whenever safe, do not ask unless permissions, destructive or
external side effects, or a genuinely high-risk unresolved choice require it, and continue until
every hard failure gate is proven green.
```

After goal creation, stop the planning flow and let the goal execute the agent. Do not also begin
implementation in the same planning turn. If the user has not confirmed execution, do not create a
goal and do not start implementation.

If the goal tool is unavailable, return the exact fallback prompt above for the user to run. Do
not silently fall back to an untracked implementation.

## Plan-Phase Completion Report

Before handoff, report:

- Outcome first: the validated agent is ready for review/refinement or explicit Execute confirmation
- Explicit and one-hop discovered URL counts
- Target root and route families
- Audited public source data surfaces and mapped Dineway content types/fields
- Approved change budget and protected invariants
- Required skills preserved
- Commit/PR discipline preserved
- Agent path and validation result as supporting detail, not the primary next step
- Awaiting explicit Execute confirmation, goal handoff, or fallback prompt

Never describe the website clone itself as complete during the plan phase.
