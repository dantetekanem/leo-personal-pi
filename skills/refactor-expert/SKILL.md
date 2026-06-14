---
name: refactor-expert
description: Behavior-preserving refactoring expert. Use whenever the user asks to refactor, clean up, simplify, reorganize, reduce duplication or complexity, clarify ownership/names, extract seams, split responsibilities, or improve code structure without adding features.
---

# Refactor Expert

Refactoring changes structure while preserving externally observable behavior. Treat that contract as the center of the work: understand the behavior, change one thing at a time, and prove nothing important changed.

## Preconditions

Before editing, establish the safety envelope:

1. **Goal**: state the refactor in one sentence, e.g. “isolate payment side effects” or “remove duplicated branching.”
2. **Behavior contract**: identify inputs, outputs, side effects, errors, ordering, persistence, authorization, performance-sensitive behavior, and public API expectations.
3. **Safety net**: prefer green tests. If coverage is thin, add or request characterization tests, golden outputs, fixtures, logs, or explicit manual checks before touching risky code.
4. **Blast radius**: list files and call sites likely to change. If the refactor crosses persistence, network, async, security, or UI boundaries, shrink scope or strengthen verification first.
5. **Approval boundary**: do not mix refactor with feature work, schema/data changes, broad formatting, commits, deploys, installs, or service starts unless User explicitly approves.

If current behavior is unclear, investigate first and report what must be characterized. Do not “improve” behavior inside a refactor without naming it as a behavior change.

## Seam-Finding Checklist

Map behavior-sensitive seams before moving code:

- Public methods, component props, routes, CLI/API contracts, events, and serialization formats.
- Database schema, callbacks, validations, transactions, scopes, migrations, and persisted enum/string values.
- Auth/authz checks, tenancy/account scoping, feature flags, configuration, and secrets.
- Jobs, queues, timers, retries, idempotency, cache keys, websockets, mailers, and webhooks.
- External APIs, file/storage operations, payment/email/SMS side effects, and network timeouts.
- Error classes/messages, logging/metrics relied on operationally, ordering, concurrency, and nil/empty edge cases.
- UI selectors, accessibility names, DOM structure used by tests, CSS hooks, and browser-visible behavior.

Seams are where accidental behavior changes hide. Preserve them until verification proves the new structure is equivalent.

## Small-Step Workflow

1. **Baseline**: run the narrowest relevant tests or record the manual/golden baseline before changing code.
2. **Name the step**: choose one mechanical transformation and know how to reverse it.
3. **Transform locally**: keep each diff small enough to review in isolation. Avoid simultaneous move + rename + logic rewrite.
4. **Verify frequently**: after meaningful steps, run targeted tests or the agreed manual check. If verification fails, stop and diagnose before continuing.
5. **Reduce risk before elegance**: extract seams around side effects first, then simplify pure logic behind those seams.
6. **Stop at clear improvement**: end when the stated goal is met and behavior is proven, not when every possible cleanup is exhausted.

## Transformation Menu

Prefer mechanical, behavior-preserving moves:

- Extract variable/method/function/class around a coherent concept.
- Inline indirection that no longer earns its keep.
- Move code to the owner of the data or policy it uses most.
- Rename narrowly when the new name captures existing behavior better.
- Split long methods by level of abstraction; keep orchestration separate from decisions and side effects.
- Replace duplicated conditionals with a lookup, strategy, policy object, or polymorphism only when multiple callers/variants justify it.
- Introduce a seam/adapter/facade around external side effects before changing internals.
- Preserve whole object or introduce a parameter object when argument lists obscure an existing concept.
- Delete dead code only after proving no runtime, reflection, template, or external caller uses it.

## Rollback Safety

- Keep a reversible path: small edits, narrow file sets, and frequent verification.
- Prefer preparatory refactors that leave old behavior reachable until the replacement is proven.
- Avoid cross-cutting rewrites, generated churn, mass formatting, and opportunistic cleanup.
- When a step fails, revert or isolate that step rather than layering fixes on top of uncertain changes.
- Call out any remaining risk instead of masking it with confidence.

## Rails Bias

In Rails apps, prefer Rails-native structure before inventing layers:

- Use models, associations, scopes, validations, controllers, jobs, mailers, helpers, partials, concerns, form objects, and POROs according to existing project conventions.
- Avoid service-object explosion unless the app already uses that style or the domain boundary clearly earns it.
- Keep database lifecycle, transactions, callbacks, and external side effects explicit and separately testable.
- Treat routes, params, strong parameters, view partial locals, Turbo/Stimulus behavior, and Active Job serialization as public seams.

## Pitfalls to Avoid

- “Cleaning up” by changing behavior, performance characteristics, errors, or data shape.
- Creating abstractions for one caller or speculative future variants.
- Renaming broadly because the new names feel nicer.
- Refactoring across untested persistence, network, async, auth, or payment boundaries.
- Hiding bug fixes inside a refactor instead of separating and naming them.
- Expanding into unrelated files, formatting churn, dependency changes, or architectural rewrites.
- Trusting type checks alone when runtime behavior depends on fixtures, callbacks, templates, or external consumers.

## Verification Discipline

Use the cheapest evidence that actually protects the seams touched:

- Targeted unit/component tests for pure logic and ownership moves.
- Integration/system/request tests for routes, controllers, UI flows, serialization, and auth seams.
- Characterization tests or golden outputs for legacy behavior.
- Mutation-by-inspection checks: compare before/after SQL shape, payloads, rendered HTML, job arguments, cache keys, or emitted events when relevant.
- Manual checks only when automated coverage is unavailable; document exact steps and observed results.

If verification cannot be run, say so plainly and explain what remains unproven.

## Report Template

```text
Refactor goal: <one sentence>
Behavior preserved: <tests/checks/baseline evidence>
Changes made: <small summary by responsibility>
Files inspected: <paths>
Files changed: <paths>
Verification: <commands/results or manual checks>
Risky seams: <remaining risks or “none identified”>
Follow-ups: <optional, out-of-scope improvements not done>
```

## Useful Principle

Make the change easy, then make the easy change. A refactor earns its keep when it makes the current system easier to understand, verify, or safely change without smuggling in new behavior.
