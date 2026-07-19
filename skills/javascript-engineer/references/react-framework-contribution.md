# React Framework Contribution Reference

> Return to [SKILL.md](../SKILL.md) for core workflow, boundaries, and reference-selection rules.

Use these defect classes when preparing a change for `facebook/react`. Source permalinks are pinned to commit `172742b419bad2a79ac375c0d5ee15c7ac66bff2`; re-read current repository instructions before executing because contributor commands and release policy can change.

---

## 1. Fix designed before a reduced reproduction exists

**Failure mode.** A broad issue description (“Suspense sometimes hangs”) leads to edits across the reconciler without proving the trigger, owner, or observable contract. Reviewers cannot distinguish the bug from an application mistake.

**Concrete example.** A report includes a production stack but no component tree, React version, renderer, sequence of updates, or runnable case. The patch changes retry scheduling and several tests happen to pass.

**Expert rule.** Reduce the failure to the smallest runnable example or focused failing repository test before changing source. Record exact React build/version, renderer, environment, inputs, and expected versus actual behavior. Search known issues first; use the issue template and include a reproducer. A regression fix should add a test that fails on the parent commit for the same reason the reproduction fails.

**Evidence.** React's official contribution guide, [Bugs](https://legacy.reactjs.org/docs/how-to-contribute.html#bugs), [Reporting New Issues](https://legacy.reactjs.org/docs/how-to-contribute.html#reporting-new-issues), and [Where to Find Known Issues](https://legacy.reactjs.org/docs/how-to-contribute.html#where-to-find-known-issues).

## 2. Pull request based on the wrong branch or release channel

**Failure mode.** A contributor patches an old stable tag or release branch, then opens a PR whose context no longer matches `main`. Or experimental behavior is mistaken for the next stable contract.

**Concrete example.** A fix is written against `v18.2.0`; files and tests have moved on `main`, so the diff includes backport noise. Another change assumes code published from `main` immediately enters stable npm.

**Expert rule.** Base ordinary contributions on the latest `main` and keep the branch scoped to one change. Do not target a release branch or manufacture a backport unless a maintainer asks. Distinguish source branch from release channel: React publishes canary/experimental prereleases from `main`, while promotion to stable is a separate manual process.

**Evidence.** React's official guide, [Branch Organization](https://legacy.reactjs.org/docs/how-to-contribute.html#branch-organization), and source, [`scripts/release/README.md` describes main-tip prereleases and manual stable promotion](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/scripts/release/README.md#L17-L31).

## 3. Experimental or breaking behavior landed ungated

**Failure mode.** New semantics are enabled for every renderer and release channel as soon as the commit lands, leaving no kill switch or channel-specific validation path.

**Concrete example.** A new Suspense behavior is wired directly into reconciler branches with no flag. It works in DOM tests but regresses a native or test-renderer fork after merge.

**Expert rule.** For behavior not ready to become the universal stable contract, add or use the appropriate feature flag and gate both implementation and tests. Classify the flag consistently with the repository's categories: short-lived killswitch, land/remove, experiment, next-major, or deprecation chopping block. Plan removal or landing; flags are migration tools, not permanent configuration APIs.

**Evidence.** React's official guide, [Feature Flags](https://legacy.reactjs.org/docs/how-to-contribute.html#feature-flags), and source, [`ReactFeatureFlags.js` flag lifecycle categories](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/shared/ReactFeatureFlags.js#L10-L80).

## 4. Main feature flag changed without its renderer forks

**Failure mode.** A new export exists in `packages/shared/ReactFeatureFlags.js` but one or more fork modules omit it or assign the wrong channel value. Flow/build variants fail, or a renderer silently exercises different behavior.

**Concrete example.** `enableNewRetryPolicy` is added only to the default file. The test renderer fork imports the feature-flag type but does not export the field, and www/native builds disagree.

**Expert rule.** Trace every fork under `packages/shared/forks`, update all required exports with intentional values, and run Flow plus the relevant renderer/channel tests. Do not copy values blindly: forks exist precisely because products and renderers can differ. Keep the main and fork types aligned; the fork imports the main flag module's type surface to make omissions observable.

**Evidence.** React's official guide, [Feature Flags](https://legacy.reactjs.org/docs/how-to-contribute.html#feature-flags), and source, [`ReactFeatureFlags.test-renderer.js` type imports and forked values](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/shared/forks/ReactFeatureFlags.test-renderer.js#L1-L36).

## 5. Change placed in the wrong monorepo package

**Failure mode.** A renderer-specific concern leaks into public React core, DOM behavior is implemented in the shared reconciler, or scheduling semantics are patched in a DOM adapter because that is where a failing test was found.

**Concrete example.** Validation specific to HTML attributes is added to `packages/react`, making native renderers depend on DOM concepts. Or a Hook's public API is added in `react-dom` even though it is renderer-independent.

**Expert rule.** Put the public component/Hook surface and renderer-independent React API in `packages/react`; DOM client/server renderer entry points and DOM integration in `packages/react-dom`/`react-dom-bindings`; shared scheduling and tree reconciliation in `packages/react-reconciler`; renderer host behavior in its host config. Trace from public entry point through dispatcher/reconciler to host config before choosing the owner.

**Evidence.** Source package contracts: [`packages/react/README.md`](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/README.md#L1-L9), [`packages/react-dom/README.md`](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react-dom/README.md#L1-L45), and [`packages/react-reconciler/README.md`](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react-reconciler/README.md#L1-L24).

## 6. Type annotations written for the contributor's preferred type system

**Failure mode.** TypeScript syntax or declarations are added to Flow-owned React core source, producing a locally plausible patch that violates the host repository's checks and conventions.

**Concrete example.** A contributor changes `ReactStartTransition.js` to TypeScript-style parameter annotations or introduces a `.ts` helper beside Flow modules.

**Expert rule.** Match the host package's type system. React core source is predominantly Flow-annotated JavaScript; update Flow types and run `yarn flow`. TypeScript may appear in compiler tooling or published type-related work, but that does not authorize converting an unrelated core module. Infer ownership from the target file, neighboring modules, configs, and package scripts—not from the consumer ecosystem.

**Evidence.** Source, [`ReactStartTransition.js` Flow annotations](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactStartTransition.js#L9-L47), and [`package.json` Flow commands](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/package.json#L134-L150).

## 7. Recoverable misuse warning implemented as a production failure

**Failure mode.** A developer mistake that React can continue past throws in production, or an unconditional `console.error` adds production byte cost and output.

**Concrete example.** A malformed development-only diagnostic for `lazy()` is changed to `throw new Error`, turning an explanatory warning into an application crash even though the eventual module access already defines failure behavior.

**Expert rule.** For actionable developer misuse that does not make continued execution invalid, follow local warning conventions: guard `console.error`/`console.warn` with a literal `if (__DEV__)` block and test the warning. React's lint rule intentionally permits only warning/error console calls in that exact guard. Never weaken an actual invariant merely to avoid an error code; classify recoverable warning versus impossible/corrupt state from runtime responsibility.

**Evidence.** Source, [`no-production-logging.js` requires literal `if (__DEV__)` guards](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/scripts/eslint-rules/no-production-logging.js#L12-L73), and [`ReactLazy.js` dev-only diagnostics](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactLazy.js#L191-L220).

## 8. Hard failure added without a production error code

**Failure mode.** A new unconditional `Error` embeds a long message in production bundles or bypasses React's error decoder. Lint/build gates reject it, or bundle size grows.

**Concrete example.** Reconciler code throws `new Error('Expected the hydration parent to ...')` with a new message but does not add the corresponding entry to `scripts/error-codes/codes.json`.

**Expert rule.** Use the repository's normal hard-failure pattern for conditions that must hold in every build, and add the message to the production error-code map when required by the lint rule. Preserve useful development text; the build replaces eligible messages with minified codes and a decoder URL. Do not disable `react-internal/prod-error-codes` unless the nearby code documents a legitimate exceptional boundary.

**Evidence.** Source, [`formatProdErrorMessage.js` explains build-time message replacement](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/shared/formatProdErrorMessage.js#L9-L25), and [`prod-error-codes.js` enforces a codes.json entry](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/scripts/eslint-rules/prod-error-codes.js#L42-L81).

## 9. Test passes only in development mode

**Failure mode.** A patch relies on `__DEV__` behavior, warning output, or unminified branches. `yarn test` passes, but the production test environment exposes a semantic or error-code difference.

**Concrete example.** A regression test expects a development warning and accidentally makes its runtime assertion conditional on that warning. The production path takes a different branch and fails.

**Expert rule.** During iteration run the narrowest matching test pattern in development. Before handoff, run the relevant suite in both normal and production environments: `yarn test <pattern>` and `yarn test --prod <pattern>` when supported. Assert warning behavior only in the repository's established dev-only test style while keeping semantic assertions valid in production. Expand to renderer/channel variants when the changed package or flag crosses them.

**Evidence.** React's official guide, [Development Workflow](https://legacy.reactjs.org/docs/how-to-contribute.html#development-workflow), and source, [`jest-cli.js` defines `--prod` as `NODE_ENV=production`](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/scripts/jest/jest-cli.js#L45-L68).

## 10. Repository gates guessed instead of read

**Failure mode.** A contributor runs generic Jest, Prettier, ESLint, or TypeScript commands directly. React's wrappers, transforms, release channels, custom lint rules, and Flow configs are bypassed.

**Concrete example.** `yarn jest` is run directly, but root Jest configuration deliberately points to `dont-run-jest-directly.js`. Changed files look formatted locally while React's wrapper still reports generated or version-specific differences.

**Expert rule.** Use React's own Yarn 1 scripts. The official contributor gates are `yarn test` (and relevant `--prod`), `yarn prettier`, `yarn lint`, and `yarn flow`; `yarn linc` is the faster changed-files lint during iteration. Run the narrowest useful checks first, then every gate implicated by the diff. Do not claim the full suite passed when only a test pattern ran.

**Evidence.** React's official guide, [Development Workflow](https://legacy.reactjs.org/docs/how-to-contribute.html#development-workflow), and source, [`package.json` canonical scripts and Yarn version](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/package.json#L122-L165), [`linc.js` passes `onlyChanged: true`](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/scripts/tasks/linc.js#L10-L24).

## 11. Public compatibility treated as an implementation detail

**Failure mode.** A refactor changes observable timing, warning text, accepted input, export shape, or renderer behavior while preserving internal types. The patch is called “non-breaking” because no public function was removed.

**Concrete example.** A Hook now throws where it warned, a Suspense fallback appears at a different time, or an export moves between entry points. Existing consumers break without a compile error.

**Expert rule.** Enumerate the observable contract before editing: public exports, runtime behavior, scheduling/reveal semantics, warning/error behavior, renderer differences, and server output. Follow semantic versioning and obtain maintainer agreement for a public API or breaking behavior before heavy implementation. Compatibility includes behavior, not only signatures. Add regression tests for every intentionally preserved observation.

**Evidence.** React's official guide, [Semantic Versioning](https://legacy.reactjs.org/docs/how-to-contribute.html#semantic-versioning) and [Proposing a Change](https://legacy.reactjs.org/docs/how-to-contribute.html#proposing-a-change).

## 12. Deprecation and removal collapsed into one release

**Failure mode.** An old API or behavior disappears without a prior migration signal, making the first observable notice a production break.

**Concrete example.** A legacy API is removed from stable with no earlier development warning or upgrade guidance. Consumers cannot discover the replacement while still on a compatible release.

**Expert rule.** Treat staged deprecation as the default engineering judgment for a shipped API: introduce a focused development warning and documented replacement, allow an adoption window, then remove only in an appropriate major/release plan approved by maintainers. React's own React 19 upgrade guide distinguishes APIs deprecated with warnings from APIs removed after earlier deprecation; use the current release plan rather than inventing a schedule.

**Evidence.** React, [React 19 Upgrade Guide — New deprecations](https://react.dev/blog/2024/04/25/react-19-upgrade-guide#new-deprecations) and [Removed deprecated React APIs](https://react.dev/blog/2024/04/25/react-19-upgrade-guide#removed-deprecated-react-apis), plus the official [Semantic Versioning](https://legacy.reactjs.org/docs/how-to-contribute.html#semantic-versioning) policy.

## 13. User-visible change omitted from release communication

**Failure mode.** A behavior fix, new API, deprecation, or security hardening lands with tests but no durable user-facing record. Release authors and consumers cannot tell whether an observed change is intentional.

**Concrete example.** A hydration mismatch diagnostic changes materially, but the eventual release notes contain no entry and the PR summary only describes internal Fiber flags.

**Expert rule.** State the user-visible effect in the PR summary and identify whether changelog/release-note work is required by current maintainer process. When an entry is appropriate, describe observable behavior and migration impact, not internal mechanics. The exact choice to edit root `CHANGELOG.md` in the same PR is process-dependent engineering judgment; inspect current neighboring entries and maintainer instructions rather than adding release prose mechanically.

**Evidence.** Source, [`CHANGELOG.md` records releases by user-facing area and links changes](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/CHANGELOG.md#L1-L49), and React's official guide, [Sending a Pull Request](https://legacy.reactjs.org/docs/how-to-contribute.html#sending-a-pull-request).

## 14. Pull request asks reviewers to reconstruct scope and proof

**Failure mode.** A large diff arrives without the reduced reproduction, failing-before/passing-after test, compatibility analysis, flag matrix, or exact command results. Review cost exceeds implementation cost.

**Concrete example.** The PR says “fix concurrent mode bug,” mixes renames and formatting with reconciler logic, and reports “tests pass” without naming dev/prod patterns.

**Expert rule.** Keep one concern per PR and remove drive-by edits. Explain the failure, root cause, why this package owns it, observable behavior before/after, compatibility and flag/channel effects, and exact verification commands. Link the reproduction and show that the regression test fails without the patch. This responsibility-first PR shape is explicit engineering judgment: it follows from React's request for focused proposals, prerequisite checks, and a reviewable pull request.

**Evidence.** React's official guide, [Proposing a Change](https://legacy.reactjs.org/docs/how-to-contribute.html#proposing-a-change), [Contribution Prerequisites](https://legacy.reactjs.org/docs/how-to-contribute.html#contribution-prerequisites), and [Sending a Pull Request](https://legacy.reactjs.org/docs/how-to-contribute.html#sending-a-pull-request).

## 15. CLA and community prerequisites discovered after technical review

**Failure mode.** A technically ready PR cannot be accepted because the contributor has not completed the license agreement or has ignored project conduct and contribution prerequisites.

**Concrete example.** Review concludes, but merge remains blocked while the first-time contributor completes the CLA and rewrites a PR that did not follow submission guidance.

**Expert rule.** Read the contribution guide before implementation, follow the Code of Conduct, and complete the Meta/Facebook CLA once when submitting a first contribution. Treat these as acceptance prerequisites, not code-quality substitutes. Never claim that passing tests implies the project can legally accept the contribution.

**Evidence.** React's official guide, [Contributor License Agreement (CLA)](https://legacy.reactjs.org/docs/how-to-contribute.html#contributor-license-agreement-cla), [Code of Conduct](https://legacy.reactjs.org/docs/how-to-contribute.html#code-of-conduct), and source, [`CONTRIBUTING.md` routes contributors to the official guide](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/CONTRIBUTING.md#L1-L5).
