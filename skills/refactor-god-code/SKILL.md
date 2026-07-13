---
name: refactor-god-code
description: >-
  Big-refactor specialist for whole-project god code: huge files, agent-created monoliths, god classes/modules, tangled responsibilities, giant services/controllers/components, and repo-wide decomposition work. Use this when the user asks to refactor a massive file, split a 1000+ LOC file, organize code across a project, break up god objects, undo agent-generated mega-files, apply SOLID at project scale, or create focused modules/mixins/composition boundaries. Do not use for tiny cleanup.
---

# Refactor God Code

This skill is for large, focused, behavior-preserving refactors: whole projects, giant files, god classes, mega services, tangled modules, and agent-created dumps of code that need real architecture.

The job is not to polish. The job is to make the codebase easier to change by putting each responsibility in the right home, with explicit boundaries and proof that behavior stayed intact.

## Use This For

Use this skill when the work is big enough that a normal local cleanup is not enough:

- A 1000+ LOC file, controller, model, component, service, script, or extension.
- A “god” object that owns unrelated policies, I/O, orchestration, formatting, state, and framework glue.
- A project where many features have been shoved into one layer or one directory.
- Agent-generated code that works but is structurally unacceptable.
- A refactor that must split responsibilities across many files while preserving behavior.
- A request to organize code with modules, mixins, concerns, traits, composition, services, policies, adapters, or SOLID boundaries.

Do not use this for small rename/extract-method cleanup. Use the ordinary refactor skill for that.

## Non-Negotiables

1. Preserve behavior unless the user explicitly asks for behavior changes.
2. Make a map before editing. Big refactors without a map become rewrites.
3. Split by responsibility and reason-to-change, not by line count.
4. Keep public seams stable until the final migration step.
5. Prefer explicit composition over hidden coupling.
6. Use mixins/concerns/traits only for cohesive capabilities with explicit host contracts.
7. Never create dumping grounds: no generic `utils`, `helpers`, `common`, `misc`, or “shared” pile unless the project already has a clear convention and the new module is cohesive.
8. Verify each slice. If there are no tests, add or request the smallest characterization safety net before risky moves.
9. Keep the refactor focused. Do not mix in feature work, style churn, dependency upgrades, or opportunistic cleanup.

## Research Backbone

Apply these ideas tersely; do not turn the answer into an essay.

- Parnas: decompose around hidden design decisions, not procedural flowcharts.
- Fowler/Beck: large classes/files are change-risk smells; refactor in small, compiling, tested steps.
- Cohesion/coupling: code that changes together belongs together; unrelated change reasons must separate.
- SOLID: use SRP, ISP, and DIP to reduce change blast radius; use OCP only where real variants exist.
- Composition over inheritance: default to explicit collaborators; use inheritance/mixins only when the contract is obvious and stable.

## Operating Model for Big Refactors

### 1. Freeze the scope

State the refactor goal in one sentence.

Good:

```text
Goal: Split the 1800-line extension entrypoint into command registration, tmux orchestration, task state, model resolution, and UI formatting while preserving all current commands and behavior.
```

Bad:

```text
Goal: Clean up the code.
```

Also state what is out of scope.

### 2. Inventory the god code

Before editing, identify:

- Public entry points: exported symbols, routes, commands, CLI flags, jobs, callbacks, events, props, APIs.
- Side effects: database writes, network calls, filesystem, process spawning, timers, caches, telemetry, logs.
- State: mutable fields, global state, singleton state, stores, sessions, contexts.
- Responsibility clusters: groups of functions/classes that serve one purpose.
- Coupling hazards: circular imports, implicit host methods, shared mutable state, broad interfaces.
- Existing safety nets: tests, type checks, lint, snapshots, fixtures, manual smoke checks.

For whole-project work, delegate read-only inventory/review agents when available. Use one writer unless the user explicitly approves multiple writers.

### 3. Produce the target shape

Write a concrete file/module plan before moving code.

```text
Target structure:
- src/commands/register.ts — registers public commands and keeps command IDs stable.
- src/tmux/session-manager.ts — owns tmux process/session lifecycle.
- src/tasks/task-store.ts — owns task persistence and status transitions.
- src/models/model-resolver.ts — owns model/category resolution rules.
- src/ui/message-format.ts — owns user-facing formatting only.
- src/index.ts — thin facade that wires modules together.
```

Every destination needs a responsibility. If you cannot write the responsibility clearly, do not create the file yet.

### 4. Choose the migration strategy

Pick the safest path for the codebase:

- **Facade first:** keep the old public file/API and move internals behind it.
- **Leaf extraction:** move pure helpers, parsers, formatters, constants, and mappers before orchestrators.
- **Adapter extraction:** isolate filesystem, network, database, process, time, randomness, and vendor APIs.
- **Policy extraction:** move rules/decisions into named policies or strategies when variants exist.
- **State extraction:** move state plus invariants together; do not leave state in the god object while behavior moves away.
- **Strangler refactor:** route one behavior at a time to the new structure while the old path remains compatible.

Avoid big-bang rewrites unless the user explicitly accepts the risk.

### 5. Execute in slices

A slice is only valid if it can be reviewed and verified independently.

For each slice:

1. Move one responsibility.
2. Keep the old public seam working.
3. Make dependencies explicit through parameters, constructors, injected collaborators, or narrow interfaces.
4. Remove dead code only after the new path is wired and verified.
5. Run the narrowest useful check.
6. Record what moved and why.

Do not batch many unrelated moves just because they are in the same file.

## Boundary Rules

### Good boundaries

A good extracted module owns one of these:

- A domain rule or invariant.
- A workflow step with its own state and side effects.
- A policy or strategy that changes independently.
- An adapter around an external system.
- A parser, serializer, mapper, formatter, or presenter.
- A query/repository/store boundary when that matches project convention.
- A UI component/hook/controller boundary with a clear rendering or interaction responsibility.
- A cohesive capability shared by multiple hosts.

### Bad boundaries

Reject these:

- `utils.ts` containing unrelated leftovers.
- Files split as `part1`, `part2`, `more`, `extra`, `shared`, or `helpers`.
- Modules that exist only to reduce LOC but hide no decision.
- Mixins that require undocumented host methods or mutate host state invisibly.
- A “service” that still does everything the god file did.
- Abstract factories/interfaces for a single concrete case with no variant pressure.
- Circular imports introduced by extraction.

## Mixins, Modules, Concerns, Traits

Use them when the extracted behavior is a cohesive capability that naturally attaches to a host.

Before using one, write the host contract:

```text
Capability: <name>
Host must provide: <methods/state/callbacks>
Adds: <methods/callbacks>
Does not own: <excluded responsibilities>
Tests prove: <behavior through a real host>
```

If the contract is long, use composition instead.

Prefer composition when the extracted code has its own dependencies, lifecycle, state, variants, or side effects.

## Whole-Project Refactor Plan Format

For big refactors, produce this before editing:

```text
Refactor goal:
<one sentence>

Out of scope:
- <explicit non-goals>

Current god-code map:
- <path>: <responsibilities currently mixed together>

Public seams to preserve:
- <seam>

Target structure:
- <path>: <responsibility>

Slice plan:
1. <small move> — verify with <check>
2. <small move> — verify with <check>
3. <small move> — verify with <check>

Risks:
- <risk and mitigation>
```

If editing immediately would be unsafe, stop after the plan and ask for approval.

## Final Report Format

After edits, report only what matters:

```text
Goal: <refactor goal>
Changed structure:
- <path>: <responsibility>

Behavior preserved by:
- <tests/checks/manual evidence>

Important boundaries:
- <boundary>: <why this is now isolated>

Remaining risk:
- <risk or “none found”>
```

Keep it focused. The user wants the god code killed, not a lecture.
