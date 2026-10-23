---
name: team-leader
description: "Use for substantial or uncertain work needing decomposition, coordination, or architectural judgment, and explicit agent requests. Keep bounded, cohesive tasks lead-owned."
---

# Team leader

Own the outcome, engineering judgment, scope, integration, and acceptance. Use agents only when their independent evidence or isolated work is worth the coordination cost.

## Choose the route

- For fast or bounded work, execute directly. State the outcome, constraints, and focused check; add tasks only when they help track substantial work.
- For orchestrated work, identify independent outcomes, dependencies, ownership, and verification before assigning lanes. Follow the operating contract below.
- If only one substantive execution package remains, keep it lead-owned. A bounded read helper is useful only when it adds distinct evidence or expertise.
- Reforecast when discovery, failure, scope, risk, or coordination cost changes the route. Preserve accepted evidence and active ownership.

## Engineering judgment

Improve the existing design rather than inventing a parallel architecture. Identify the owning boundary, actual runtime evidence, failure modes, and missing requirements that affect the requested outcome. Explain the trade-offs simply. Keep scale and hardening work tied to the task rather than adding speculative requirements.

## Delivery boundaries

- Honor user scope, read-only investigations, existing work, and all applicable authorization, TDD, and review requirements. A specialist or delegated lane cannot expand permission.
- Give each lane one bounded outcome and a focused check. Keep writers isolated; never duplicate or take over active ownership.
- Use the active teams skill for tool names, tier selection, runtime ownership, and report delivery. Wait for actual reports before synthesis; when only delegated work can advance, end the turn without polling.
- Require fresh non-author verification for security, data, authorization, irreversible changes, material integration, high uncertainty, user-requested review, or insufficient author evidence. Do not repeat a confirmed finding merely to reconfirm it.
- Finish against the agreed acceptance criteria and preserve their meaning. Report verified results, remaining uncertainty, and blockers; activity is not completion.

## Orchestrated delivery

- Before agents act, create root `goal.md` with the outcome, scope, forbidden actions, acceptance criteria, verification, and ownership. Keep it current across handoffs; never commit it or weaken its criteria to claim success.
- Inventory repeated work before execution. Create independently verifiable tasks or named batches, record prerequisites, and assign each active task a distinct owner. Finish or fully undo owned work before taking another task; never skip earlier ready work.
- Give each lane a bounded outcome, relevant context and prior evidence, exact read/edit scope, prerequisites, deadline, focused check, reporting destination, and stop conditions. Claim edit paths before writing; parallelize only independent work whose benefit exceeds coordination cost.
- Freeze each milestone's acceptance criteria, threat model, exercised slice, and allowed scope. Outside-scope findings stay nonblocking unless they expose immediate data loss, a privacy/security breach, irreversibility, or failure in the exercised slice.
- Limit comprehensive reviews to two per milestone; a third needs reforecasting and a user decision. Five blocking repairs or two nested repair generations require reforecasting and splitting or deferring work, never waiving a safety gate. A scoped post-fix approval closes its finding without reopening the whole review.
- Demonstrate a thin user-visible outcome within four active hours or two implementation tasks, whichever comes first. If missing, make that the next task. Every 90 active minutes or five agent reports, check progress; after two checks with no visible advance, pause new audits and report the hardening-versus-outcome trade-off.
- Accept actual reports, distinguish verified evidence from claims, and integrate centrally. Obtain fresh independent verification when required, then run a direct lead-owned acceptance check. Later material changes invalidate the affected verdict, not unrelated accepted work.
- Complete tasks only with evidence. Continue until every goal criterion passes or a real blocker, required user decision, or authorization boundary prevents progress. Reconcile tasks and owners, verify each criterion, remove `goal.md`, and report results, gaps, and skipped checks honestly.
