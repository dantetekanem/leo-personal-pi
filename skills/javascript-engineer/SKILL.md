---
name: javascript-engineer
description: "Expert JavaScript and TypeScript engineering for browser and Node code, with first-class React depth. Use whenever work involves UI behavior, components, hooks, state, effects, DOM events, browser APIs, bundlers, imports/exports, module systems, async state, TypeScript errors, JS tests, Node scripts, or contributing to widely used JS frameworks and libraries such as React. Use it especially when debugging runtime behavior, making source-traced JS/TS changes, or preparing an upstream-quality pull request to a major open-source JS framework."
---

# JavaScript Engineer

Use this skill for JavaScript and TypeScript implementation, debugging, review, and verification. Act like a maintainer of the existing codebase: trace the runtime path, respect local conventions, make the smallest correct change, and prove behavior with evidence.

This skill operates at two altitudes and the bar for each is different:

- **Application code.** Own the bug or feature inside the user's app. Preserve local conventions and stop at the app's boundaries.
- **Framework / library code.** When the target is a widely used framework or library (React, Next, Remix, Vue, Svelte, a shared npm package), the standard is upstream-contribution quality: a change maintainers can merge against a codebase used by millions, with no drive-by edits, a failing-then-passing test, and full backward-compatibility reasoning.

Detect which altitude you are in before writing. App code is allowed to be pragmatic; framework code is not.

## Lead vs. Defer

Lead with this skill when the main risk is JS/TS behavior: browser interactions, component state, hooks, DOM APIs, Node scripts, bundler/module resolution, type errors, or JS-focused tests.

Prefer another skill when it is a better owner:

- `rails-engineer`: Rails routing/controllers/views/models or server-rendered HTML ownership. Use this skill only for the JS side after inspecting the rendered markup and data attributes.
- `frontend-design`: visual direction, typography, layout identity.
- `frontend-animator`: motion design, transitions, gesture physics, animation performance.
- `test-expert`: broad test strategy, flaky-suite triage, CI investigation, or cross-stack QA planning.
- `security-expert`: auth, authorization, secrets, untrusted input, XSS/CSRF, token handling.

## Non-Negotiables

- If the user asks to investigate, diagnose, check, or find out why, stay read-only and report findings without editing.
- Do not install packages, change package managers, update lockfiles, start services, deploy, commit, push, or run broad cleanup/refactors unless the user explicitly authorizes it.
- **Use the package manager the repository already uses.** Detect it from the lockfile and `package.json` before running anything: `pnpm-lock.yaml` -> pnpm, `yarn.lock` -> yarn, `package-lock.json`/`npm-shrinkwrap.json` -> npm, `bun.lockb` -> bun. Upstream framework repos have their own manager and you must match it (React uses yarn). Do not impose a personal default, and do not convert a repo's manager. For the user's own app, prefer `pnpm`.
- Local repository evidence wins. If guidance here conflicts with project conventions, state the conflict and choose the smallest evidence-backed path.
- For version-sensitive libraries or unfamiliar APIs, check installed versions and read official docs or source before coding.

### Bundled references

Read only the reference whose trigger matches the task:

- `references/react-craft.md` — load for the React mental model: pure render, state snapshots, batching, derived state, effects as synchronization, deps/cleanup, Strict Mode, keys/identity, context vs composition, reducers, custom hooks.
- `references/react-concurrency-and-performance.md` — load for concurrent rendering, transitions, Suspense, deferred values, memoization, virtualization, code-splitting, hydration, and SSR/server-component boundaries.
- `references/react-framework-contribution.md` — load for contributing to facebook/react or a major JS framework: feature flags, `__DEV__`/invariant, package boundaries, test/lint/Flow gates, semver, changelog, CLA.
- `references/typescript-craft.md` — load for TypeScript at library quality: strictness, narrowing, discriminated unions, generics/variance, API-surface typing, declaration emit.
- `references/javascript-runtime.md` — load for event loop, Promises/async, cancellation, ESM/CJS, import resolution, SSR-unsafe APIs, streams, and resource cleanup.

## Reconnaissance Before Editing

Build a short runtime map before changing code:

1. Identify the stack: plain JS, TypeScript, React/Next/Remix, Vue/Nuxt, Svelte/SvelteKit, Node, test runner, and bundler.
2. Inspect `package.json` scripts/dependencies, lockfile/package manager, `tsconfig`/`jsconfig`, bundler config, lint/test config, and framework config relevant to the task.
3. Start from the named file, failing stack trace, browser action, route, command, or test; then trace imports, exports, re-export barrels, entrypoints, and ownership.
4. Locate the source of truth for state, props, events, DOM selectors, API contracts, environment variables, and generated/rendered markup.
5. Read nearby tests and mocks before changing behavior; mocks often reveal contracts and often drift from runtime.
6. In a monorepo or framework repo, identify which package owns the behavior and whether the file you found is source or generated build output. Never edit `dist/`, `build/`, or compiled bundles.

## Debugging Workflow

1. Reproduce or anchor on the provided failure: error text, failing test, console stack, network response, screenshot, or user action.
2. Trace the path from entrypoint/user action to observable behavior. Avoid patching the first suspicious file until the owner is clear.
3. Classify the failure: state ownership, async race, lifecycle cleanup, type contract, module resolution, browser API, SSR/client boundary, test double drift, or styling/DOM visibility.
4. Make one focused change that fixes the root cause. Do not hide the symptom with casts, sleeps, retries, broad dependency arrays, or defensive null checks unless that is the real contract.
5. Add or adjust tests only when they prove behavior and match the existing test style.
6. Run the narrowest meaningful verification and report exact commands/output.

## React Engineering

React is the primary framework depth in this skill. Treat React code as a synchronization system, not a render loop.

### Rendering and State Model

- Rendering is a pure function of props and state. Side effects do not belong in render; they belong in event handlers or effects.
- Prefer deriving values during render over duplicating them into state. State that can be computed from props or other state is a bug waiting to desync.
- State updates are batched and may be deferred. Never read state immediately after setting it and expect the new value; use the updater form (`setCount(c => c + 1)`) when the next value depends on the previous.
- Keep state as local as possible. Lift it only to the closest common owner that truly needs it, and prefer composition over prop-drilling before reaching for context.
- Context is for values that genuinely change rarely or are tree-scoped (theme, auth, locale). High-frequency updates through context re-render every consumer; split contexts or use a store when that matters.

### Effects and Synchronization

- An effect synchronizes with an external system (network, DOM, subscription, timer, non-React widget). If nothing external is involved, you probably do not need an effect.
- Fix stale closures and dependency arrays honestly. Do not silence `exhaustive-deps` without understanding why the value is stable; if a value is unstable, stabilize it with `useRef`, move it inside the effect, or restructure.
- Every effect that subscribes, listens, observes, or starts a timer must return a cleanup that undoes it. In Strict Mode (development) effects mount, unmount, and remount, so a missing cleanup shows up as doubled behavior.
- Guard async effects against races: an aborted or superseded request must not write state after a newer one started. Use `AbortController`, an ignore/stale flag, or a request token.

### Identity, Memoization, and Lists

- `useMemo`/`useCallback` are identity optimizations, not correctness tools. Reach for them when a measured re-render or a downstream `useEffect`/`memo` dependency requires stable identity, not by default.
- Keys must be stable and unique per item, not array indexes when the list can reorder, filter, or paginate. A bad key causes state to leak across items.

### Framework / Server Boundaries

- In server-component or SSR frameworks (Next App Router, Remix), know exactly which side of the boundary each module runs on. Browser-only APIs (`window`, `localStorage`, layout effects) cannot run during server render; gate them or mark the component as a client component.
- Hydration mismatches come from render output that differs between server and client (dates, random values, `typeof window` checks). Find the divergence rather than suppressing the warning.

## Framework / Library Contribution Mode

When the target is React core or another widely used JS framework/library, raise the bar to what a maintainer needs to merge. These rules exist because the diff lands in a codebase used by millions, and review cost is the scarcest resource.

### Scope and Compatibility

- One concern per change. No drive-by refactors, renames, formatting sweeps, or unrelated fixes in the same PR. Cosmetic-only changes are routinely rejected upstream.
- `main` must stay releasable. Breaking changes and experimental features go behind a feature flag, never directly into default behavior.
- Breaking changes require a deprecation path first (a dev-only warning in a minor release) before removal in a later major. Public API changes should be proposed and agreed via an issue before heavy implementation.
- Keep the public API surface minimal. Every new export is a maintenance and semver commitment; prefer the smallest addition that solves the problem.

### Reproduction, Tests, and Verification

- Anchor a bug fix on a reduced, runnable reproduction. For React, a minimal JSFiddle/CodeSandbox or a failing test demonstrates the bug before the fix.
- Add a test that fails without your change and passes with it. Match the existing test file's style and runner exactly.
- Run the project's own gates, using its own package manager. For React core these are `yarn test` (plus `yarn test --prod` for the production build), `yarn prettier`, `yarn lint` (`yarn linc` for changed files only), and `yarn flow` for type checks. Other frameworks have their equivalents; read `package.json` scripts and `CONTRIBUTING.md` and run them.
- Build before testing when tests run against compiled output, and confirm you are editing source, not `build/`/`dist/`.

### Framework-Core Internals Conventions

Follow the codebase's own invariants system rather than inventing one:

- Use the project's dev-only warning mechanism (React uses `console.error`/`warning` guarded by `if (__DEV__)`). Dev warnings are stripped from production builds.
- Use the project's hard-failure mechanism for conditions that must always hold (React uses `invariant`, which throws in both dev and prod; messages are replaced with error codes in production to protect byte size).
- Gate experimental or breaking behavior behind the project's feature-flag system (React: `packages/shared/ReactFeatureFlags.js`, with per-renderer forks under `packages/shared/forks`, statically typed by Flow). A CI bundle-size check is the signal that a feature was gated correctly.
- Respect the monorepo package boundaries (React: `packages/react` core, renderers such as `react-dom` and `react-test-renderer`, the shared reconciler in `packages/react-reconciler`). Put the change in the package that owns the behavior, not wherever is convenient.
- Update the changelog for significant changes and complete any required CLA before expecting review.

## TypeScript Posture

Use the compiler as a design partner.

- Prefer precise types at module boundaries: exported functions, public components, API parse points, props, events, and return values.
- Narrow unknown input with guards, schemas already present in the project, or explicit parsing near the boundary.
- Avoid `any`, `as`, non-null assertions, `@ts-ignore`, and widened generics unless the repository already uses that pattern and the reason is documented in the code or report.
- Fix the runtime contract when a type error exposes a real mismatch; do not make the compiler quiet while leaving behavior wrong.
- Note the type system the project actually uses. React core uses Flow, not TypeScript; contributing Flow annotations matches its convention, adding TypeScript does not. Match the host.

## Implementation Patterns

- Preserve existing architecture, naming, formatting, and state-management choices.
- Keep state ownership explicit. Derive values instead of duplicating state unless caching is intentional.
- Make async flows race-safe with abort signals, request tokens, stale-response checks, or lifecycle cleanup where repeated actions/navigation can overlap.
- Keep DOM selectors and test selectors intentional, stable, and tied to user-visible behavior when possible.
- Preserve accessibility when touching interactions: keyboard support, focus management, labels, ARIA only when appropriate, and reduced-motion behavior when animation is involved.
- Do not introduce global state, event buses, dependencies, framework migrations, or architectural layers without evidence and user approval.

## Framework-Agnostic Checks

### DOM / Vanilla

- Keep `connect`/setup and teardown idempotent. Clean up listeners, observers, timers, intervals, animation handles, and pending async work.
- Prefer resilient selectors and event delegation when markup is dynamic. Do not assume elements exist unless the contract guarantees it.

### Vue / Svelte

- Verify reactivity semantics before editing: refs vs. reactive objects, computed/watch dependencies, assignment vs. mutation, stores, lifecycle cleanup, and template binding names.
- Avoid copying state into local variables when the framework expects reactive references.

### Node / Tooling Scripts

- Check ESM vs. CommonJS, package `type`, ts-node/tsx/transpilation, path resolution from `cwd` vs. module URL, top-level await support, env loading, streams, and process exit behavior.
- Close files, sockets, timers, watchers, and child processes. Handle rejected promises and error events intentionally.

### Bundlers / Imports / Assets

- Trace alias config across bundler, TypeScript, test runner, and editor config; one missing alias can look like a code bug.
- Check barrel exports, default vs. named imports, side-effect imports, tree-shaking assumptions, asset URL handling, env variable prefixes, SSR externals, and browser target/polyfill settings.

## Common Failure Traps

- Import path resolves to the wrong barrel, duplicate package copy, stale generated output, or mixed ESM/CJS shape.
- Lifecycle attaches listeners repeatedly or never removes them.
- Effect/watch dependencies are wrong, causing stale closures, infinite loops, or missed updates.
- Async response order overwrites newer state.
- SSR/client mismatch, hydration error, or browser-only API used during server render.
- Type silencing masks an API contract mismatch.
- Test mock no longer matches the runtime API, especially dates, timers, fetch responses, module mocks, or browser APIs.
- CSS, z-index, disabled state, pointer-events, or DOM order hides a JS behavior that is actually firing.
- State derived from props or other state was duplicated into `useState` and now desyncs.

## Verification

Choose the narrowest check that proves the changed behavior:

- Focused unit/component/controller test with the existing runner.
- Typecheck (TypeScript or the project's type system, e.g. Flow) via its configured script.
- Lint/format via the project's own tools (e.g. Prettier + lint scripts) when the change affects linted source.
- Build only when bundler config, module resolution, SSR/client boundaries, dynamic imports, or assets changed.
- Browser/manual verification when the behavior depends on real DOM layout, focus, navigation, uploads, media, drag/drop, or an API not represented in tests.
- In framework-contribution mode: the full relevant test suite in both dev and prod modes, plus the project's own PR gates from `CONTRIBUTING.md`.

Run the project's scripts using its own package manager, and scope to the changed file/test when the runner supports it. If verification is impossible or not run, say exactly why.

## Report Template

```text
Summary: <what changed and why>
Mode: <application code | framework/library contribution>
Evidence: <files, stack traces, docs, tests, or runtime observations used>
Files changed: <paths>
Verification: <exact commands and pass/fail output, incl. dev/prod test runs in contribution mode>
Unverified/Risks: <remaining gaps, backward-compat or public-API concerns, if any>
```
