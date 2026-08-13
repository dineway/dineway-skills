# Local Agent Scheduling Contract

Codex Scheduled, Claude, or another local client is an activation adapter. Native Dineway
Pipeline Runs, Jobs, Attempts, Results, Assignments, Handoffs, opportunities, Monitor states,
calendar policy, reservations, reviews, and release grants remain the only shared workflow
authority.

## Recommended activation

- Configure the local client to open the `dineway-content-pipeline` Skill daily and whenever a
  normal Codex or Claude session becomes available.
- The activation prompt is: “Use `$dineway-content-pipeline` to query the current Dineway Agent
  wake plan and execute or resume eligible work. Exit cleanly when no work is eligible.”
- Read the native site timezone and call `content_pipeline_agent_wake_plan_get`. Never persist a
  private copy of yesterday's queue.
- The returned plan has a fixed 72-hour execution-window contract. It orders due Monitor collection
  before overdue reevaluation and current-day content execution so new signals can influence the
  queue before generation starts.
- `schedule_assignment` enters accepted work into one native Assignment and reserves current-day
  Draft capacity. `resume_assignment` uses that Assignment and its latest Handoff.
- `review_release` means inspect the current exact-Draft state; it never implies approval or
  publication permission.

## Failure and absence

- If the local client is unavailable, plugin Cron still expires elapsed Draft reservations and
  marks missed Assignments overdue. It never writes prose or invokes a model.
- On the next activation, process every `reevaluate_overdue` action with fresh evidence and choose
  `defer`, `dismiss`, `supersede`, or `resume`. Only `resume` creates replacement work and capacity.
- Treat activation as at-least-once. Reread native state and use the operation's native dedupe or
  idempotency key before every mutation.
- Create a Pipeline Job Handoff before the local client stops if specialist work remains. Preserve
  the native calendar Assignment separately when the item is still scheduled.

Do not install a daemon, store Agent credentials in Dineway, call a hidden hosted generation API,
or let the scheduler create Drafts or publish content without the master Skill and native gates.
