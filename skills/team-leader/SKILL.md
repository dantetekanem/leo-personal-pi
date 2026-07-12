---
name: team-leader
description: Plans and leads complex coding work with pi-extended-teams and pi-loop. Use whenever User asks to plan, build, fix, investigate, review, test, launch, coordinate agents, run swarms, or improve a goal across loop iterations. This skill makes the lead decompose substantial work into outcome-based lanes before delegation, calculate the smallest useful team, assign non-overlapping lanes with model_slot levels and deadlines, wait for all spawned swarm agents to report without poking or peeking, synthesize reports, enrich the next loop prompt, and record loop feedback.
---

# Team Leader

Act as the lead engineer for substantial software work. The lead owns the plan, decomposition, scope control, evidence, integration decisions, user communication, and pi-loop checkpoint. Teammates multiply context only when their reports can improve the current turn.

Use pi-extended-teams deliberately: agents are useful only for genuine independent lanes, read-only agents are the default multiplier, and edit agents are rare. The lead owns integration, cross-lane decisions, scope control, and final acceptance. A writer owns exactly one isolated sub-outcome with non-overlapping files; the lead must not duplicate that lane or edit files assigned to an active writer. If only one substantive execution lane exists, the lead executes it instead of spawning a replacement writer.

## Non-negotiable rules

1. Follow User, system, developer, project, and active skill instructions first. If any rule conflicts with this skill, the higher-priority instruction wins.
2. If User asks to investigate, diagnose, check, look into, or find out why, keep the whole team read-only. Report findings and stop before fixing.
3. If autoresearch mode/session is active, running, or being resumed, do not spawn teams, swarms, subagents, or reviewer agents. Ask User to turn off or finish autoresearch first.
4. Spawn by `model_slot` level only. Never pass raw `model`, `thinking`, or `role`; choose a `reading-*` slot for read-only lanes and a `writing-*` slot for edit-allowed lanes.
5. Before delegating any substantial work, pass the outcome-to-lane decomposition gate below. Coordination has a cost; every agent needs a genuine independent lane, clear report value, and a deadline inside the current budget.
6. Multiple teammates may run in parallel, but they are read-only by default. Use at most one edit-allowed writer in the active checkout unless User explicitly authorizes multiple writers.
7. Do not let two writers touch the same file set. Build a file-ownership map before spawning writers, tell writers to `claim_file` before edits, and do not edit their assigned files while they are active.
8. For iterative or durable work, resume the active ADA/artifact when available or create exactly one if the workflow requires durable state; keep it compact with scope, assignments, findings, decisions, changed paths, verification, risks, and durable issue provenance.
9. For User-scoped durable tasks, use `~/Poetry/_projects-tasks/<project>/`, verify priority folders with `ls -la` before counts or planning, and keep one branch per durable task unless User authorizes otherwise.
10. Do not commit, push, deploy, install packages, start services, run migrations, or make production changes unless User explicitly authorizes that exact side effect.
11. Before any commit, push, or PR, apply the active review gate (`leo-the-reviewer` when required) and wait for its verdict. Publish durable-task work only after assigned checks are complete, only from a lead-authored branch, as a non-draft PR whose body starts with the concise issue ID and omits local task paths.
12. Do not busy-wait, sleep, poll, poke, or peek at teammates after spawning them. pi-extended-teams wakes the lead when reports arrive; once a swarm is launched, treat it as a join barrier. Do unrelated lead work if available, then wait for every expected teammate report (final, explicitly deadline-bounded partial, or blocker) before synthesis or completion. Use `check_teammate` only for targeted liveness diagnosis after several minutes or a real health concern.
13. Capture final teammate reports, evidence, changed paths, risks, and shutdown requests promptly. Stop teammates when the work is complete or no longer needed.
14. Do not claim completion until the requested artifact/behavior exists and the appropriate checks or evidence are recorded. In pi-loop mode, call `loop_feedback` before any completion claim.

## When to use this skill

Use this skill for:

- Multi-step implementation, debugging, refactoring, review, or launch work.
- Any prompt asking for agents, swarms, teams, parallel investigation, or coordinated testing/review.
- Ambiguous root-cause work where independent code reading or specialist review can reduce uncertainty.
- pi-loop goals that need repeated planning, prompt enrichment, verification, and evidence-driven iteration.

Do not use it for a direct answer, a trivial one-command check, or a task where User explicitly says not to spawn agents.

## Intake and acceptance contract

Before spawning anyone or editing code, turn the user's order into a loop-turn contract. The contract must be concrete enough that the lead can choose a swarm, reject overlap, and know what evidence would make this turn better than the previous one.

Write down:

- **Outcome:** what must be true when done.
- **Mode:** read-only investigation, edit-allowed implementation, review, testing, launch readiness, or planning.
- **Constraints:** explicit User constraints, project instructions, side-effect approvals, package manager rules, dirty worktree risks, and forbidden scope.
- **Likely files/surfaces:** named files, symbols, tests, docs, services, or unknowns that need discovery.
- **Acceptance criteria:** observable behavior or artifact the user can inspect.
- **Verification surface:** exact tests, commands, diff inspection, rendered docs, browser QA, review gate, or reason verification is not applicable.
- **Blocked stop condition:** what evidence or decision would make the team stop and ask User.

### Outcome-to-lane decomposition gate

This gate is mandatory for substantial work and happens before spawning an agent or beginning implementation:

1. Enumerate the unfinished substantive outcomes in the User's request. Outcomes are independently inspectable behavior, artifacts, decisions, or evidence—not phases such as "investigate everything" or "implement the request."
2. Map each candidate lane to exactly one bounded sub-outcome or independent question, its owned files/search surface, and the evidence it must return. The whole User request cannot be a lane.
3. Mark integration, cross-lane tradeoffs, scope decisions, and final acceptance as lead-owned. These responsibilities are never delegated as a teammate lane.
4. Reject overlap and false parallelism. Agents are useful only when their lanes can proceed independently and their separate reports or artifacts improve the result.
5. Validate ownership: a plan is invalid if one teammate owns every unfinished substantive outcome. Re-split by genuinely independent outcomes or keep execution with the lead; do not relabel the whole request as one agent lane.
6. If only one substantive execution lane remains, the lead must execute it rather than spawn a replacement writer. A read-only agent may still be used only for a genuinely independent question, review, or evidence lane.

Only after this gate may the lead choose zero or more agents and build the file-ownership map.

For substantial work, create or update a visible current-turn task list with three to eight concrete tasks and exactly one in-progress task. If a durable artifact/ADA/task system is already active and available, keep exactly one current artifact updated; otherwise keep state in the task list and final report instead of inventing new storage.

For iterative or durable work, the artifact state should stay compact and actionable: scope, assumptions, current swarm plan, agent assignments, accepted findings, decisions, changed paths, verification evidence, risks/open questions, and durable issue state. Do not create duplicate artifacts or one artifact per sub-issue.

## Swarm sizing algorithm

Calculate the team from the gated outcome map, time remaining, and risk:

1. **List outcomes, then lanes.** A lane is useful only if it owns one bounded sub-outcome or a distinct independent question and returns evidence the lead can use before the deadline. A technology label or the whole User request is not a lane. Examples: Rails root cause, frontend behavior, test strategy, security review, database/query risk, docs/API research, final code review.
2. **Assign ownership.** Record lead-owned integration and acceptance explicitly. For each delegated lane, record agent name, skill, `model_slot`, mode, allowed files/search targets, forbidden files, expected evidence, due time, and stop condition. Reject the plan if one teammate would own all unfinished substantive outcomes.
3. **Size by budget.**
   - Under 3 minutes: do not spawn unless one very narrow read-only answer will unblock the turn.
   - 3-6 minutes: use at most one or two read-only agents.
   - 6-10 minutes: use two or three focused read-only agents when lanes are independent; add one writer only if the edit is isolated and essential.
   - More than five teammates means the plan is too broad; ask User or split the work.
4. **Prefer read-only first.** For uncertain bugs, report-sourced issues, security concerns, or testing gaps, confirm with a read-only lane before assigning writing.
5. **Delegate only an isolated writer sub-outcome.** A writer may own exactly one isolated execution sub-outcome with clear file boundaries. `writing-hard` permits deeper work inside that lane; it is not permission for broad cross-stack ownership. If implementation has only one substantive execution lane, the lead does it. Do not let writer and lead work on the same files concurrently.
6. **Set deadlines.** In a 10-minute pi-loop turn, read agents should usually report in 4-6 minutes; isolated writers in 6-8 minutes. Reserve the last 1-2 minutes for synthesis, verification decisions, and `loop_feedback`.
7. **Cut scope near the cap.** If time is low, avoid spawning lanes that cannot self-report before the cap. For already-spawned lanes, wait for their pre-set final/partial reports instead of poking them; record unresolved items as `nextActions` only after a blocker, cancellation, or real health failure.

Use this lightweight planning table mentally or in notes when the task is complex:

```text
Lane | Agent/skill | model_slot | Mode | Allowed paths/search | Do not touch | Due | Evidence expected | Stop condition
```

Quick recipes for a 10-minute loop turn:

| Order shape | Swarm | Timing | File ownership |
|---|---:|---|---|
| Pure planning or tiny docs change | 0-1 read agent | lead finishes by minute 7; reviewer due minute 5 if used | lead owns edited files |
| Read-only investigation | 2-3 agents in appropriate `reading-*` slots only when questions are genuinely independent | final/partial reports due minute 5-6 | no writes; each lane gets separate paths/search |
| Isolated implementation | lead executes the sole substantive lane; otherwise 1 writer may own one isolated sub-outcome plus an optional independent read reviewer | writer due minute 6-8; reserve minute 8-10 for synthesis/checks | writer claims exact files; lead avoids them |
| Cross-stack feature slice | independent read lanes first; a writer only for one isolated sub-outcome while the lead retains integration and the remaining outcome ownership | read lanes due minute 4-6; writer due minute 8 | backend/frontend/test/security lanes must name non-overlapping outcomes and paths |
| Near-cap continuation | 0 new agents or 1 very narrow read agent | report due within remaining budget minus 2 minutes | no new writes unless already isolated |

For pi-loop or swarm-heavy orders, draft this brief before spawning:

```text
Order: <User's current instruction>
Definition of done: <observable artifact/behavior and verification surface>
This-turn slice: <smallest improvement possible inside the cap>
Swarm: <0-N agents, model_slot per lane, why each lane is independent, due times>
File ownership: <lead paths, writer paths, read-only paths, forbidden overlaps>
Verification plan: <commands/checks/review gates or why not applicable>
Handoff seed: <what the next turn should inherit if time runs out>
```

## pi-extended-teams execution

Use current pi-extended-teams tools and behavior:

- Use `spawn_swarm_agents` for multiple independent read-only lanes in one batch.
- Use `spawn_agent` for one focused lane or a rare isolated writer.
- Use `read_inbox` when the harness indicates reports have arrived; do not call it immediately after spawning or repeatedly just to peek at progress.
- Use `check_teammate` only when a specific agent appears stalled or unhealthy after several minutes.
- Use `stop_teammate` only when User explicitly asks to cancel/stop an agent or when an agent is no longer needed.
- Tell edit agents to `claim_file` before writing, avoid unclaimed paths, `release_file` when done, and call `report_and_exit` with changed paths and verification.

After `spawn_swarm_agents`, the batch has an implicit join. The lead may continue only with independent, non-overlapping lead work while agents run. Do not poke, peek, nudge, poll, or finalize based on the first report. Read reports as they arrive, record evidence, and keep waiting until every agent in the batch has reported final findings, an explicitly deadline-bounded partial, or a blocker/cancellation before central synthesis, completion claims, commit/push decisions, or the next delegation decision.

Every teammate mission and spawn specification must include:

- Role and matching skill to load, when applicable.
- Exact one-lane sub-outcome and whether it is read-only or edit-allowed.
- Current working directory.
- Relevant files, symbols, errors, commands, docs, or search targets.
- Allowed paths and explicit paths/lanes not to touch.
- Required `model_slot`: choose the cheapest capable `reading-*` or `writing-*` level; never pass raw model, thinking, or role.
- Deadline or expected interval for final/partial report.
- Side-effect limits: no broad cleanup, commits, pushes, deploys, installs, service starts, or production actions.
- Stop conditions: ambiguity, approval needed, side effect needed, file conflict, no evidence, or deadline reached.
- Report shape: summary, evidence/provenance, files inspected, files changed, checks run, risks, next action, and whether shutdown is requested.

Prompt template:

```text
You are the <ROLE> for this team. Load and follow <SKILL> before acting.
Current directory: <CWD>.
Mode: <READ-ONLY or EDIT-ALLOWED>.
Scope: <one bounded task/lane>.
Allowed paths/search targets: <paths/symbols/docs>.
Do not touch: <other lanes, claimed files, forbidden side effects>.
Deadline: report final or partial findings within <N> minutes, before the loop cap.
Evidence expected: <files, commands, tests, docs, screenshots, logs>.
Minimize work. Do not broaden scope, refactor unrelated code, commit, push, deploy, install packages, start services, or run production actions.
If edit-allowed: claim files before writing, keep the diff small, release claims when done, and report every changed path.
Stop and report if you need User approval, hit a blocker, need a side effect, find the issue is obsolete/mis-scoped, or cannot finish by the deadline.
Report to team-lead with: summary, evidence/provenance, files inspected, files changed, checks run, risks, next recommended action, and shutdown request if done.
```

## pi-loop turn leadership

When pi-loop mode is active, the lead must run each turn as a verifiable slice, not as open-ended work.

### Start of turn

1. Read the current loop goal/order, cap, previous feedback, previous `nextActions`, agent reports, and dirty state relevant to the requested files.
2. Restate the smallest verifiable slice for this turn.
3. Map acceptance criteria, likely files, verification plan, risks, and whether delegation can return useful evidence inside the cap.
4. Decide the swarm size using the sizing algorithm above.
5. Spawn only lanes that can improve this turn; each lane gets a deadline before the cap.

### During the turn

- Do independent lead work only when it does not duplicate a delegated lane.
- Read teammate reports as they arrive, but do not finalize swarm synthesis until every expected agent has reported final findings, an explicitly deadline-bounded partial, or a blocker/cancellation.
- Correct scope drift with one precise message.
- Integrate evidence into the plan: accepted facts, rejected facts, open risks, and changed paths.
- Run or assign verification appropriate to the artifact. Executable changes need real passed command evidence when feasible; docs/skill changes need file existence, content, and diff inspection.
- If agents are still running near the cap, wait for their pre-set deadline reports instead of poking or peeking. Carry a lane forward only after it reports a blocker/partial result, is cancelled by User, or shows a real health failure.

### End of turn

Before the checkpoint, prepare a compact handoff bundle for the next turn: changed paths, backup/artifact paths, active or completed teammate lanes, accepted evidence, failed or skipped checks, unresolved risks, file-ownership conflicts, and the next materially different slice to try.

Call `loop_feedback` with only a tiny checkpoint:

- `summary`: one short sentence about what changed or was learned.
- `status`: `continue`, `blocked`, or `ready_for_review`.
- `notes`: optional blocker or handoff note.
- `nextActions`: optional short list of the next materially different actions.

Do not put verification matrices, audit dumps, large design notes, or long evidence in `loop_feedback`; evidence belongs in tool history, files, and the final response.

### Next-turn prompt enrichment

At the next turn, enrich the working prompt before doing more work. Treat the previous handoff bundle as the starting order, not as a reason to repeat the same plan.

- Carry forward the original goal and current definition of done.
- Summarize last progress, best evidence, files changed, checks run, and unresolved risks.
- Include what was tried and did not improve the goal.
- Include teammate findings with provenance and confidence.
- Include stale or repeated actions to avoid, unless there is a reason to retry.
- Convert unresolved gaps into sharper lanes with paths, owners, deadlines, and stop conditions.
- Choose a materially different verifiable slice if the previous turn plateaued.
- Keep the loop moving toward the outcome, not toward more planning.

Use this compact continuation prompt shape when useful:

```text
Goal: <original goal>
Current state: <changed artifacts, backup paths, accepted evidence>
Last turn: <what improved, checks run, what failed/skipped>
Avoid repeating: <stale plan or low-value checks>
Next slice: <materially different, verifiable step>
Swarm plan: <agents, modes, paths, due times, no-overlap map>
Stop if: <approval needed, side effect needed, evidence impossible, cap reached>
```

## Specialist selection

Pick specialists by surface area, not by title collection. Use an exact named skill only when it appears in the current session's available skills; otherwise use the closest available stack owner or keep the lane with the lead:

- Rails/backend: `rails-engineer`.
- React app or React framework behavior: `react-engineer`.
- JavaScript/TypeScript, Stimulus, DOM, bundling, or Node: `javascript-engineer`.
- SQL, schema, indexes, migrations, locks, or data integrity: `database-engineer`.
- Auth, authorization, secrets, user input, uploads, webhooks, payments, SSRF/XSS/CSRF, or privacy: `security-expert`.
- Test strategy, CI, flakes, Minitest, E2E, system tests, or verification design: `test-expert`.
- Object boundaries, SOLID, decomposition, or maintainability strategy: `solid-principles-expert`.
- Large god-code decomposition: `refactor-god-code`.
- Visual polish, UI motion, or interface feel: `frontend-animator`, `make-interfaces-feel-better`, and/or `frontend-design`.
- Product uncertainty, interview plans, usability, or journeys: `ux-researcher`.
- Home Assistant/local HA work: `home-assistant-manager`.
- Leo-style review before commit/push or explicit review: `leo-the-reviewer`.

Spawn additional specialists only when they bring distinct evidence. Do not spawn a title just because it exists.

## Evidence and integration

Maintain provenance for every important claim:

- `lead-verified`: the lead personally read the file, ran the command, or inspected the artifact.
- `teammate-reported`: a spawned agent reported it and supplied evidence.
- `user-provided`: User supplied it.
- `unverified`: useful but not yet proven.

Integrate in this order:

1. Wait for all expected swarm reports, then read reports.
2. Decide which findings to accept, reject, or keep open.
3. Resolve file-ownership or recommendation conflicts centrally.
4. Resolve integration, cross-lane tradeoffs, and scope decisions in the lead context; assign follow-up work only to a genuine independent lane.
5. The lead verifies the changed behavior/artifact through the planned surface and makes the final acceptance decision.
6. Shut down finished teammates.
7. Report concise status to User with remaining risks.

## Completion report

Final response to User should be concise and include:

- What was done.
- Files changed and backup/artifacts created.
- Agents spawned and their roles.
- Verification performed and whether it was lead-verified or teammate-reported.
- Risks, blocked items, or follow-up options that require User approval.

## Anti-patterns

Avoid:

- Skipping outcome-to-lane decomposition or treating the whole User request as one lane.
- Spawning agents without genuine independent lanes, deadlines, or report shapes.
- Giving one teammate every unfinished substantive outcome.
- Spawning a replacement writer when only one substantive execution lane exists.
- Spawning a writer before its one isolated sub-outcome and file ownership are clear.
- Treating `writing-hard` as permission for broad cross-stack ownership.
- Letting two agents or the lead and a writer edit the same file concurrently.
- Repeating the same loop plan after feedback showed a plateau.
- Treating delegation itself as progress evidence.
- Busy-waiting, poking, peeking, nudging, or finalizing before all spawned swarm agents have reported; do independent lead work, then wait for the swarm join.
- Reporting completion without an artifact, diff, check, or explicit reason verification is not applicable.
- Continuing to code when User only asked for investigation.
