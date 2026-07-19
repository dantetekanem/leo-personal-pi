# React Concurrency and Performance Reference

> Return to [SKILL.md](../SKILL.md) for core workflow, boundaries, and reference-selection rules.

Use these defect classes for responsive updates, Suspense, memoization, code loading, SSR, and hydration. Source permalinks are pinned to React commit `172742b419bad2a79ac375c0d5ee15c7ac66bff2` so implementation claims remain auditable.

---

## 1. Concurrent rendering mistaken for parallel application code

**Failure mode.** Code treats “concurrent” as “two component functions run at the same time” or assumes every render reaches the DOM. It performs side effects during render, so an interrupted or restarted render leaks work that was never committed.

**Concrete example.** Rendering a search result mutates a cache or emits analytics. A transition render is superseded by another input update; React discards the first render, but the mutation remains.

**Expert rule.** Concurrent rendering is React's interruptible scheduling model, not permission to make render impure. React may start, pause, continue, or abandon render work and commits only a completed result. Mark non-urgent state updates with a concurrent feature such as a Transition; keep urgent input updates outside it. The reconciler represents sync, input, default, transition, retry, hydration, idle, and offscreen work as distinct lanes.

**Evidence.** React, [React v18 — What is Concurrent React?](https://react.dev/blog/2022/03/29/react-v18#what-is-concurrent-react), and source, [`ReactFiberLane.js` lane definitions](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react-reconciler/src/ReactFiberLane.js#L43-L100).

## 2. Transition used as a delayed setter

**Failure mode.** `startTransition` is treated like a timeout or debounce. Code expects it to postpone calling the action, or puts the urgent controlled-input update inside it.

**Concrete example.** An input's `onChange` wraps `setQuery(e.target.value)` in `startTransition`, making the input lag or fail to track each keystroke as expected.

**Expert rule.** The action passed to `startTransition` runs immediately; state updates synchronously scheduled while it runs are marked non-blocking Transition work. Update the controlled input urgently, and transition the expensive result state or navigation. Use `useTransition` when the component must expose pending feedback; standalone `startTransition` does not provide `isPending`.

**Evidence.** React, [`startTransition` — startTransition(action)](https://react.dev/reference/react/startTransition#starttransitionaction), [`startTransition` — Caveats](https://react.dev/reference/react/startTransition#caveats), [`useTransition` — Updating an input in a Transition doesn't work](https://react.dev/reference/react/useTransition#updating-an-input-in-a-transition-doesnt-work), and source, [`ReactStartTransition.js` installs and restores transition context](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactStartTransition.js#L45-L98).

## 3. Transition pending state disconnected from the action

**Failure mode.** A UI sets a separate `isLoading` boolean around a transitioned async action. Errors, overlapping actions, or an early return leave the boolean wrong; pending UI no longer represents React's scheduled work.

**Concrete example.** A tab button calls `setIsLoading(true)`, awaits navigation, then sets it false. A second tab click overlaps the first and the first completion hides pending feedback for the second.

**Expert rule.** Prefer `const [isPending, startTransition] = useTransition()` at the boundary that renders feedback, and put the Action inside that transition. Pending state covers the transition work and lets the control communicate progress. If action completion order is itself a data-integrity requirement, add request identity or use framework action abstractions; Transition scheduling alone does not impose last-write-wins ordering.

**Evidence.** React, [`useTransition` — Displaying a pending visual state](https://react.dev/reference/react/useTransition#displaying-a-pending-visual-state), [`useTransition` — Exposing action prop from components](https://react.dev/reference/react/useTransition#exposing-action-prop-from-components), and source, [`ReactHooks.js` public transition tuple](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactHooks.js#L170-L180).

## 4. Async Transition boundaries marked incompletely

**Failure mode.** Code assumes every update after an `await` automatically keeps Transition priority, or assumes rejected async Actions can be ignored.

**Concrete example.** `startTransition(async () => { const data = await save(); setPage(data); })` works for some surrounding pending behavior, but a post-`await` state update that must be marked as a Transition is not wrapped as required by the documented caveat.

**Expert rule.** Follow the installed React version's async Transition contract. Current React docs require wrapping state updates after an `await` in another `startTransition` to guarantee they are marked as Transitions, and describe this as a known limitation. Handle action failures explicitly. React core detects thenable returns, tracks them for development diagnostics, and attaches rejection handling rather than treating an async function as synchronous.

**Evidence.** React, [`startTransition` — Caveats](https://react.dev/reference/react/startTransition#caveats), [`useTransition` — React doesn't treat my state update after await as a Transition](https://react.dev/reference/react/useTransition#react-doesnt-treat-my-state-update-after-await-as-a-transition), and source, [`ReactStartTransition.js` thenable handling](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactStartTransition.js#L75-L95).

## 5. Suspense boundary placed at a code seam instead of a reveal seam

**Failure mode.** Every lazy component gets its own spinner, producing flicker and a “popcorn” sequence, or one boundary wraps the entire page and hides useful shell content for one slow child.

**Concrete example.** A biography and albums panel should reveal together, but independent boundaries flash two spinners. Conversely, a route-level boundary replaces navigation, header, and already-visible content when only the results panel suspends.

**Expert rule.** Place boundaries around the loading sequence the product intends users to see. Nest boundaries for progressive reveal; group content that should reveal together. Suspense activates the nearest boundary when a descendant suspends. Boundary placement is a product/design judgment, but the reasoning must name which shell remains interactive and which content reveals together.

**Evidence.** React, [`<Suspense>` — Revealing content together at once](https://react.dev/reference/react/Suspense#revealing-content-together-at-once), [Revealing nested content as it loads](https://react.dev/reference/react/Suspense#revealing-nested-content-as-it-loads), and [Preventing already revealed content from hiding](https://react.dev/reference/react/Suspense#preventing-already-revealed-content-from-hiding).

## 6. Suspense expected to preserve all local state before first mount

**Failure mode.** A child suspends before it mounts, and code expects local state or layout Effects from that abandoned attempt to survive. Or a re-suspending visible tree keeps a layout subscription that describes hidden DOM.

**Concrete example.** A chart measures itself in a layout Effect, suspends, and is later retried. Code assumes the first attempted mount's state and measurement are retained.

**Expert rule.** Do not attach correctness to an initial render that suspended before mount. React documents that it does not preserve state for renders that suspend before first mount; it retries from scratch. When already-visible content is hidden because it suspends again, React cleans up layout Effects and runs them again when content is shown. Put durable state above the boundary or in an external owner when it must outlive the suspended subtree.

**Evidence.** React, [`<Suspense>` — Caveats](https://react.dev/reference/react/Suspense#caveats).

## 7. `useDeferredValue` mistaken for debounce or request cancellation

**Failure mode.** A deferred query is expected to reduce network requests. Every keystroke still fetches, and stale results are rendered without any visual indication.

**Concrete example.** `SearchResults` receives `deferredQuery`; typing `react` starts requests for each intermediate query. The old results remain until the background render completes, but the UI looks current.

**Expert rule.** Use `useDeferredValue` to let a slow subtree lag behind an urgent value while React attempts interruptible background renders. It does not prevent requests and does not impose a fixed delay. Make staleness visible (for example, dim the results), combine it with cache/deduplication supplied by the data layer, and still make response ordering race-safe.

**Evidence.** React, [`useDeferredValue` — Showing stale content while fresh content is loading](https://react.dev/reference/react/useDeferredValue#showing-stale-content-while-fresh-content-is-loading), [How does deferring a value work under the hood?](https://react.dev/reference/react/useDeferredValue#how-does-deferring-a-value-work-under-the-hood), and source, [`ReactHooks.js` deferred-value dispatcher](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactHooks.js#L178-L180).

## 8. Memoization used as a correctness boundary

**Failure mode.** Code depends on a `useMemo` value never being recomputed, uses `useCallback` to repair a stale closure, or assumes `memo` prevents every child render.

**Concrete example.** A connection object is created with `useMemo` and treated as a durable resource. React discards the cache for a documented reason, the object changes, and correctness breaks. Or a memoized child still re-renders because it consumes changing context.

**Expert rule.** Treat `useMemo`, `useCallback`, and `memo` only as performance optimizations. Correct the state/effect model first. `memo` can skip parent-driven renders when props are `Object.is`-equal, but state and consumed context can still re-render the component. `useCallback` caches a function identity, not its result and not a live closure. `useMemo` caches a pure calculation but React may discard the cache.

**Evidence.** React, [`memo` — Caveats](https://react.dev/reference/react/memo#caveats), [`useMemo` — Caveats](https://react.dev/reference/react/useMemo#caveats), and [`useCallback` — The difference between useCallback and declaring a function directly](https://react.dev/reference/react/useCallback#the-difference-between-usecallback-and-declaring-a-function-directly).

## 9. Memoization added without a stable dependency graph

**Failure mode.** A component is wrapped in `memo`, but every render passes a new object, array, or function. Comparison work is added and no render is skipped; one “always new” prop defeats the boundary.

**Concrete example.** `<List options={{sort: 'name'}} onSelect={() => select(id)} />` is memoized. Both props change identity on every parent render, so `memo` cannot help.

**Expert rule.** First localize transient state and remove unnecessary Effects that trigger update chains. Then profile a production build. If a slow subtree repeatedly renders with semantically unchanged inputs, stabilize only the identities that cross that measured memo boundary. Prefer accepting the minimum primitive props over a custom deep comparator. If using `arePropsEqual`, compare every prop including functions and prove the comparator is cheaper than rendering.

**Evidence.** React, [`memo` — Minimizing props changes](https://react.dev/reference/react/memo#minimizing-props-changes), [Specifying a custom comparison function](https://react.dev/reference/react/memo#specifying-a-custom-comparison-function), and [`useCallback` — Should you add useCallback everywhere?](https://react.dev/reference/react/useCallback#should-you-add-usecallback-everywhere).

## 10. Performance optimized from development anecdotes

**Failure mode.** A developer counts console logs in Strict Mode or measures an unoptimized development build, then spreads memoization across the tree without identifying the slow interaction.

**Concrete example.** A list “renders twice” in development, so every row receives `memo`, `useMemo`, and `useCallback`; production interaction time is unchanged while dependency complexity grows.

**Expert rule.** Define an observable slow interaction, profile with React Developer Tools, and confirm with a production build on representative hardware. Distinguish render work from commit work and network delay. Add one optimization, remeasure, and retain it only when the relevant metric improves. This evidence-first sequence is expert judgment, supported by React's guidance to use the Profiler and to avoid unnecessary memoization.

**Evidence.** React, [`<Profiler>` — Measuring rendering performance programmatically](https://react.dev/reference/react/Profiler#measuring-rendering-performance-programmatically), [`useMemo` — How to tell if a calculation is expensive?](https://react.dev/reference/react/useMemo#how-to-tell-if-a-calculation-is-expensive), and [`useCallback` — Should you add useCallback everywhere?](https://react.dev/reference/react/useCallback#should-you-add-usecallback-everywhere).

## 11. Large lists rendered in full

**Failure mode.** Thousands of rows are mounted and reconciled even though only a small viewport is visible. Memoization reduces some row computation but does not remove DOM, layout, style, and accessibility-tree cost.

**Concrete example.** A 50,000-row audit table creates every `<tr>` and becomes slow on initial render and scroll despite memoized row components.

**Expert rule.** Window long lists so only a bounded visible slice plus overscan is rendered. Preserve stable item keys, keyboard/focus behavior, semantic counts, and scroll position. The choice of virtualization library and overscan is engineering judgment and must be tested with the app's variable row sizes and accessibility requirements; React's official performance guide recommends windowing for long-list rendering cost.

**Evidence.** React, [Optimizing Performance — Virtualize Long Lists](https://legacy.reactjs.org/docs/optimizing-performance.html#virtualize-long-lists), and [Rendering Lists — Keeping list items in order with key](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key).

## 12. Code splitting without a deliberate loading and failure boundary

**Failure mode.** A route imports its entire feature eagerly, or `lazy()` is declared inside a component and resets state. A rejected dynamic import has no nearby error handling, so a loading optimization becomes a broken route.

**Concrete example.** `const Editor = lazy(() => import('./Editor'))` is created during `Article` render. Each render creates a new component type; editor state resets and loading behavior repeats.

**Expert rule.** Declare `lazy` components at module scope. The loader must return a thenable resolving to a module with a `default` component export. Render the lazy component under a Suspense boundary aligned with the intended loading experience and an error boundary/framework route boundary for rejected loads. Split at meaningful route or feature seams, not every component; that seam choice is engineering judgment based on bundle and interaction measurements.

**Evidence.** React, [`lazy` — lazy(load)](https://react.dev/reference/react/lazy#lazy), [`lazy` — My lazy component's state gets reset unexpectedly](https://react.dev/reference/react/lazy#my-lazy-components-state-gets-reset-unexpectedly), and source, [`ReactLazy.js` validates and returns the default export](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactLazy.js#L191-L239).

## 13. Hydration output diverges between server and client

**Failure mode.** The server emits one tree and the first client render emits another. Event handlers may attach incorrectly, React may regenerate a subtree on the client, and startup work increases.

**Concrete example.** Render branches on `typeof window !== 'undefined'`, calls `Date.now()` or `Math.random()`, formats a date in different locales, reads changing external data without serializing a snapshot, or produces invalid HTML nesting.

**Expert rule.** Make the first client render structurally and textually match the server output. Serialize the same data snapshot, make locale/time-zone decisions explicit, and move browser-only divergence to an Effect after hydration or to a client-only boundary supported by the framework. Treat `suppressHydrationWarning` as a narrow escape hatch for a known unavoidable one-level difference, not a repair. React core's mismatch error enumerates the common divergence classes and regenerates the affected tree.

**Evidence.** React, [`hydrateRoot` — Pitfall: server and client output must be identical](https://react.dev/reference/react-dom/client/hydrateRoot#pitfall), [`hydrateRoot` — Suppressing unavoidable hydration mismatch errors](https://react.dev/reference/react-dom/client/hydrateRoot#suppressing-unavoidable-hydration-mismatch-errors), and source, [`ReactFiberHydrationContext.js` mismatch causes](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react-reconciler/src/ReactFiberHydrationContext.js#L388-L415).

## 14. Server/client module boundary left implicit

**Failure mode.** A server-rendered or Server Component module imports `window`, `document`, `localStorage`, event handlers, or client-only Hooks. The code crashes on the server or forces a much larger client bundle than intended.

**Concrete example.** A mostly static product page is marked `'use client'` at the route root just so one purchase button can use state; all transitive imports become part of the client graph.

**Expert rule.** In frameworks that implement React Server Components, place `'use client'` on the narrowest module boundary whose exported components need client capabilities. Props crossing from server to client must be serializable. Keep browser APIs and interactivity below that boundary; keep data access and non-interactive rendering on the server when the framework supports it. Boundary granularity is framework-specific engineering judgment—verify the installed framework's bundling and routing contract.

**Evidence.** React, [`'use client'` — Reference](https://react.dev/reference/rsc/use-client#reference), [How `'use client'` marks client code](https://react.dev/reference/rsc/use-client#how-use-client-marks-client-code), and [Serializable types returned by Server Components](https://react.dev/reference/rsc/use-client#serializable-types-returned-by-server-components).

## 15. Streaming SSR treated as one all-or-nothing response

**Failure mode.** The server waits for every slow data dependency before sending any HTML, or aborts the entire response when a nested boundary is slow. Time to first shell is tied to the slowest component.

**Concrete example.** A product shell and navigation are ready, but reviews are slow. `renderToString` waits or emits only fallback behavior that cannot progressively reveal the review section as it resolves.

**Expert rule.** When the framework/server integration supports it, stream a shell with `renderToPipeableStream` (Node streams) or `renderToReadableStream` (Web Streams), and use Suspense boundaries to define reveal units. Set status and begin piping at the appropriate shell callback, handle shell errors separately, and enforce an abort timeout. Prefer the framework's integration because data loading, asset discovery, status codes, and hydration are cross-cutting concerns.

**Evidence.** React, [`renderToPipeableStream` — Streaming more content as it loads](https://react.dev/reference/react-dom/server/renderToPipeableStream#streaming-more-content-as-it-loads), [Recovering from errors outside the shell](https://react.dev/reference/react-dom/server/renderToPipeableStream#recovering-from-errors-outside-the-shell), and source, [`react-dom` package owns both DOM and server renderer entry points](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react-dom/README.md#L1-L45).
