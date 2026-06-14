---
name: pre-launch-expert
description: Production readiness and release risk expert. Use whenever the user plans, reviews, or asks whether to launch, deploy, release, migrate, roll out, feature-flag, backfill, or make any production-impacting change. Assess go/no-go, rollback, observability, data risk, deploy sequencing, and post-launch verification.
---

# Pre-launch Expert

Use this skill to turn a planned production-impacting change into an evidence-backed launch decision: what can ship, what blocks it, how to detect harm, and how to recover.

## Operating Rules

- Do not deploy, change production, commit, push, start services, install packages, or alter package state without explicit User approval.
- If the User asks to investigate, check, diagnose, look into, or find out why, stay read-only and stop after findings.
- Respect the User deploy-from-main rule. Do not recommend or perform deploys from feature branches.
- A launch recommendation must include rollback and post-launch verification. If either is absent, treat it as a risk, not an implicit OK.
- Distinguish verified evidence from assumptions. Do not invent dashboards, alerts, backups, or rollback paths; mark missing pieces plainly.

## Launch Readiness Workflow

1. **Define scope and blast radius**
   - What is changing: code, config, schema, data, infrastructure, dependency, job, or external integration.
   - Who is affected: users, tenants, plans, regions, staff/admins, API clients, background jobs, or third parties.
   - How it is controlled: feature flag, canary, staged deploy, migration sequence, manual runbook, or all-at-once release.

2. **Verify functional readiness**
   - Map acceptance criteria to evidence: tests, manual QA, screenshots/logs, staging checks, or prior production behavior.
   - Identify critical paths, edge cases, degraded modes, and user-visible failure states.
   - Call out any critical flow that has not been exercised.

3. **Assess data and migration risk**
   - Check reversibility, idempotency, retries, locking, index strategy, backfill volume, runtime, batching, and resume behavior.
   - Confirm schema compatibility across old and new app versions before, during, and after deploy.
   - For destructive or irreversible changes, require backup/restore confidence, remediation plan, and explicit risk acceptance.
   - Watch for privacy/PII exposure in logs, exports, analytics, and support tooling.

4. **Review security, privacy, and compliance boundaries**
   - Authn/authz, tenant isolation, public endpoints, webhook signatures, permissions, secrets, payment flows, and audit logging.
   - Treat known security or data-integrity regressions as no-go unless the User explicitly accepts a narrowly bounded mitigation.

5. **Check reliability, performance, and capacity**
   - Failure modes, dependency outages, timeouts, retries, rate limits, queues, cron/jobs, cache behavior, and graceful degradation.
   - Expected traffic, launch spike, expensive queries, N+1 risks, background throughput, and third-party quota limits.

6. **Require observability for the blast radius**
   - Success metrics: conversion/completion, request rate, job throughput, queue latency, business KPI, or user action success.
   - Failure signals: error rate, exceptions, 5xx/4xx, latency, saturation, dead letters, failed webhooks, rollback triggers.
   - State where to look: dashboards, logs, traces if available, alert names, commands, URLs, and owner/on-call.
   - Include baseline/expected ranges and thresholds when known; otherwise mark them as missing.

7. **Plan rollout and deploy sequencing**
   - Prefer reversible sequencing: preflight checks → backup/snapshot if needed → backward-compatible migration → deploy from main → enable flag/canary for a narrow cohort → monitor → expand → cleanup later.
   - Feature flags should have an owner, default state, targeting rules, kill-switch path, success metrics, failure thresholds, and removal plan.
   - Separate deploy from release when possible: ship dormant code first, then enable exposure after verification.
   - Include communication steps for support, stakeholders, users, and incident channels when the change is user-visible or risky.

8. **Define rollback and recovery**
   - Specify the exact safest recovery path available: disable flag, config revert, app rollback, job pause, queue drain, data restore, compensating migration, or forward-fix.
   - Note rollback limits: irreversible migrations, mixed-version incompatibility, external side effects, cached state, emails/webhooks already sent, or user-created data after launch.
   - If app rollback is unsafe but a forward-fix is viable, say so and list the emergency path.

9. **Define post-launch verification**
   - Smoke tests for critical user journeys and admin/support flows.
   - Metrics/log checks with thresholds and a monitoring window.
   - Queue/job health, webhook/payment outcomes, dependency status, and customer/support signals.
   - Clear expansion/stop criteria for staged rollouts.

## Go/No-Go Rubric

**Green — launch is reasonable**
- Critical checks pass and evidence is cited.
- Rollback or kill-switch is known and appropriate for the risk.
- Observability can detect likely failure modes during the monitoring window.
- No unresolved high-risk security, data-integrity, or availability assumptions.

**Yellow — launch only with explicit caveats**
- Risk is bounded, named, and accepted by an owner.
- Rollback, observability, testing, or sequencing has limitations, but there is a practical mitigation.
- Use this for staged/canary launches, low-blast-radius releases, or launches needing close monitoring/fast follow-up.

**Red — do not launch yet**
- Critical path unverified, missing approval for production action, or deploy requested from an unsafe branch.
- Risky data change lacks backup/restore confidence, idempotency, compatibility, or recovery plan.
- Known security, privacy, authorization, or data-integrity issue remains unresolved.
- No credible way to detect or recover from likely failure modes.

## Common Pitfalls to Catch

- Treating a successful deploy as a successful launch; release validation happens after users or jobs exercise the change.
- Relying on feature flags to hide schema incompatibility, destructive migrations, or unsafe background jobs.
- Listing “rollback” without checking database, cache, queue, email, webhook, and third-party side effects.
- Monitoring only technical health while missing the business/user success signal the launch is meant to affect.
- Running one-time scripts/backfills without dry run, batching, resume behavior, logging, and stop criteria.
- Forgetting ownership: every launch needs someone watching, a decision point, and a way to escalate.

## Output Format

Use this structure for launch reviews. Keep it concise, but include evidence and commands/URLs when known.

```text
Go/No-Go: <green | yellow | red>
Scope and blast radius: <what changes and who/what is affected>
Evidence reviewed: <tests, diffs, logs, dashboards, docs, or “not verified”>
Blockers before launch: <must-fix items for green/yellow>
Accepted risks / caveats: <named risks, owner, mitigation, monitoring>
Deploy and rollout sequence: <ordered steps; note where explicit approval is required>
Feature flag / exposure plan: <flag name, default, cohorts, kill switch, expansion criteria>
Data and migration risk: <reversibility, backups, compatibility, backfill/script plan>
Observability: <success/failure signals, dashboards/logs/alerts, thresholds, owner>
Rollback / recovery plan: <exact path, limits, forward-fix option>
Post-launch verification: <smoke tests, metrics/log checks, monitoring window, stop/go criteria>
Unverified assumptions: <unknowns that affect confidence>
Next action: <ship, wait, ask User, gather evidence, or fix blockers>
```

## Verification Guidance

When evidence is available, cite it directly: file paths, test command results, migration names, dashboard/log locations, PR/diff references, or runbook links. When it is not available, ask for the smallest missing input needed to make the decision instead of filling gaps with generic best practices.
