# React Craft Reference

> Return to [SKILL.md](../SKILL.md) for core workflow, boundaries, and reference-selection rules.

Use these defect classes when reviewing component state, identity, effects, context, reducers, or custom Hooks. Each class states the failure mode, a concrete example, and the expert rule.

---

## 1. Impure render functions

**Failure mode.** A component mutates a module-level array, writes to the DOM, starts a timer, or reads a changing value such as `Date.now()` while React is calculating JSX. Re-rendering can duplicate work or produce different output for the same props and state.

**Concrete example.** `StoryTray` calls `stories.push({id: 'create'})` during render. A parent update renders it again, so another “Create Story” item appears. Strict Mode's extra development render makes the mutation visible sooner.

**Expert rule.** Treat render as a pure calculation: the same inputs produce the same JSX, and render does not mutate pre-existing objects. Allocate and transform local data during render; put interaction-caused work in event handlers and external-system synchronization in Effects. React separates rendering from committing, so do not confuse “my component function ran” with “the DOM changed.”

**Evidence.** React, [Keeping Components Pure — Purity: Components as formulas](https://react.dev/learn/keeping-components-pure#purity-components-as-formulas), [Detecting impure calculations with Strict Mode](https://react.dev/learn/keeping-components-pure#detecting-impure-calculations-with-strict-mode), and [Render and Commit — Step 2: React renders your components](https://react.dev/learn/render-and-commit#step-2-react-renders-your-components).

## 2. State mistaken for a mutable variable

**Failure mode.** Code calls a setter and immediately reads the state variable expecting the new value. Delayed callbacks then appear “stale,” even though they correctly captured the render that created them.

**Concrete example.** With `count === 0`, a handler runs `setCount(count + 5)` and schedules `setTimeout(() => alert(count), 3000)`. The alert displays `0`, because that handler belongs to the render whose snapshot contained `0`.

**Expert rule.** Read state as an immutable snapshot for one render. A setter queues a later render; it does not mutate the current binding. Compute an explicit `nextCount` when the same event needs the proposed value. Use a ref only when the requirement is truly “read the latest mutable value without rendering,” not to defeat normal state flow.

**Evidence.** React, [State as a Snapshot — Rendering takes a snapshot in time](https://react.dev/learn/state-as-a-snapshot#rendering-takes-a-snapshot-in-time) and [State over time](https://react.dev/learn/state-as-a-snapshot#state-over-time).

## 3. Lost updates inside a batch

**Failure mode.** Several updates derived from the same snapshot replace one another. The UI increments once even though code called `setNumber(number + 1)` three times.

**Concrete example.** A “+3” button queues the value `1` three times because every expression reads `number === 0`. A request counter similarly undercounts when overlapping completions use a captured `pending` value.

**Expert rule.** When the next value depends on the previous queued value, pass an updater such as `setNumber(n => n + 1)`. React processes updater functions in queue order after the event handler, and batches updates so rendering happens after the handler finishes. Do not rely on setter call order to mutate the current render's variables.

**Evidence.** React, [Queueing a Series of State Updates — React batches state updates](https://react.dev/learn/queueing-a-series-of-state-updates#react-batches-state-updates) and [Updating the same state multiple times before the next render](https://react.dev/learn/queueing-a-series-of-state-updates#updating-the-same-state-multiple-times-before-the-next-render).

## 4. Derived state duplicated and allowed to drift

**Failure mode.** A value computable from props or state is copied into another state variable and synchronized in an Effect. The component first commits stale derived data, then schedules a second render; missed paths let the copies disagree.

**Concrete example.** `fullName` is state updated from `firstName` and `lastName` in an Effect, or `visibleTodos` is state updated whenever `todos` and `filter` change.

**Expert rule.** Keep the minimal source of truth and calculate derived values during render. Memoize only an actually expensive pure calculation; memoization replaces repeated computation, not state ownership. When selecting an object from a list, store a stable ID and derive the object so replacing the list cannot leave a stale object copy.

**Evidence.** React, [You Might Not Need an Effect — Updating state based on props or state](https://react.dev/learn/you-might-not-need-an-effect#updating-state-based-on-props-or-state), [Caching expensive calculations](https://react.dev/learn/you-might-not-need-an-effect#caching-expensive-calculations), and [Adjusting some state when a prop changes](https://react.dev/learn/you-might-not-need-an-effect#adjusting-some-state-when-a-prop-changes).

## 5. Effects modeled as component lifecycle callbacks

**Failure mode.** An Effect accumulates unrelated “on mount,” “on update,” and “on unmount” logic. Adding a dependency needed by one concern accidentally reconnects another system or repeats analytics.

**Concrete example.** One Effect both connects to a chat room and logs a room visit. Later, changing a server URL correctly reconnects the socket but incorrectly logs a second visit.

**Expert rule.** Model each Effect as one independent synchronization process: its body starts or updates synchronization with an external system, and its cleanup stops the exact synchronization created by that run. Think in repeatable start/stop cycles rather than component lifecycle names. Split Effects when deleting one process should not break the other.

**Evidence.** React, [Lifecycle of Reactive Effects — Thinking from the Effect's perspective](https://react.dev/learn/lifecycle-of-reactive-effects#thinking-from-the-effects-perspective) and [Each Effect represents a separate synchronization process](https://react.dev/learn/lifecycle-of-reactive-effects#each-effect-represents-a-separate-synchronization-process).

## 6. Dishonest Effect dependencies and stale closures

**Failure mode.** A developer suppresses `exhaustive-deps` or chooses `[]` to control frequency. The subscription keeps a handler from the first render, so it forever sees the initial prop or state.

**Concrete example.** A `pointermove` listener closes over `canMove === true`; the Effect claims no dependencies, so toggling the checkbox never installs a handler with the new value.

**Expert rule.** Dependencies are a description of the reactive values read by the Effect, not a scheduling preference. Include every prop, state value, and render-local value used. To remove a dependency, change the code so the value is provably non-reactive: move static values outside, construct dynamic objects inside the Effect, use a state updater, or separate non-reactive Effect Event logic where that API is available. Do not silence the linter to preserve an accidental schedule.

**Evidence.** React, [Removing Effect Dependencies — Dependencies should match the code](https://react.dev/learn/removing-effect-dependencies#dependencies-should-match-the-code), [To remove a dependency, prove that it's not a dependency](https://react.dev/learn/removing-effect-dependencies#to-remove-a-dependency-prove-that-its-not-a-dependency), and [Why is suppressing the dependency linter so dangerous?](https://react.dev/learn/removing-effect-dependencies#why-is-suppressing-the-dependency-linter-so-dangerous).

## 7. Cleanup that does not mirror setup

**Failure mode.** A component registers a listener, interval, observer, socket, or request but does not undo it before dependency changes or unmount. Re-synchronization leaks resources or lets stale work update current state.

**Concrete example.** Search requests for `h`, `he`, and `hello` race; the `he` response arrives last and overwrites results for `hello`. Or a chat changes rooms without disconnecting the old room.

**Expert rule.** Return cleanup that reverses the setup performed by that Effect run. For async work, abort when the API supports it and/or guard the result with an `ignore` flag so superseded work cannot commit state. Cleanup is required before re-synchronization as well as unmount, so test a dependency change, not only navigation away.

**Evidence.** React, [Lifecycle of Reactive Effects — How React re-synchronizes your Effect](https://react.dev/learn/lifecycle-of-reactive-effects#how-react-re-synchronizes-your-effect) and [You Might Not Need an Effect — Fetching data](https://react.dev/learn/you-might-not-need-an-effect#fetching-data).

## 8. Interaction logic routed through Effects

**Failure mode.** A click or submit first sets state, then an Effect observes that state and performs the action. Reloading or restoring state repeats an action that should have occurred only for the original interaction.

**Concrete example.** An Effect sends `/api/register` after `jsonToSubmit` changes, or displays “Added to cart” whenever `product.isInCart` is true. A restored cart triggers the notification again without a click.

**Expert rule.** Put logic caused by a specific interaction in that interaction's event handler. Reserve Effects for logic caused by the component being displayed or for keeping an external system synchronized with current reactive values. If two handlers share work, extract an ordinary function and call it from both; do not use state plus an Effect as an event bus.

**Evidence.** React, [Separating Events from Effects — Choosing between event handlers and Effects](https://react.dev/learn/separating-events-from-effects#choosing-between-event-handlers-and-effects), [Event handlers run in response to specific interactions](https://react.dev/learn/separating-events-from-effects#event-handlers-run-in-response-to-specific-interactions), and [You Might Not Need an Effect — Sending a POST request](https://react.dev/learn/you-might-not-need-an-effect#sending-a-post-request).

## 9. Strict Mode treated as the defect

**Failure mode.** Development shows two render calls or an Effect setup-cleanup-setup sequence, and code adds a ref guard to suppress the second setup. The guard hides a missing cleanup while leaving the real navigation bug intact.

**Concrete example.** A chat Effect logs connect, disconnect, connect on first display. Without a real disconnect cleanup, navigating away and back accumulates connections even if a `didRun` ref makes the initial duplicate disappear.

**Expert rule.** Make render pure and Effects resilient to repeated setup/cleanup. Strict Mode intentionally performs extra development checks: component functions are called again to expose impurity, and Effects are re-run to expose missing cleanup. Fix the non-idempotent render or incomplete cleanup; do not infer production will always mount exactly once.

**Evidence.** React, [StrictMode — Fixing bugs found by double rendering in development](https://react.dev/reference/react/StrictMode#fixing-bugs-found-by-double-rendering-in-development), [Fixing bugs found by re-running Effects in development](https://react.dev/reference/react/StrictMode#fixing-bugs-found-by-re-running-effects-in-development), and [Lifecycle of Reactive Effects — How React verifies that your Effect can re-synchronize](https://react.dev/learn/lifecycle-of-reactive-effects#how-react-verifies-that-your-effect-can-re-synchronize).

## 10. Identity errors from position, type, and keys

**Failure mode.** State is preserved for the wrong conceptual entity or reset on every render. Inputs retain another record's draft after reordering, or a nested component definition creates a new component type each render and loses its state.

**Concrete example.** A contact list uses array indexes as keys; after sorting, row state follows positions instead of contacts. A profile form should reset when `userId` changes but remains the same component in the same tree position.

**Expert rule.** State belongs to a component type at a position in the render tree. Use stable, data-derived keys among siblings to express entity identity; change a key deliberately to reset an entire subtree. Never generate keys during render, and do not define component functions inside another component when their state should persist. Index keys are acceptable only when item order and membership are genuinely static—this last condition is an engineering judgment derived from React's identity model.

**Evidence.** React, [Preserving and Resetting State — State is tied to a position in the render tree](https://react.dev/learn/preserving-and-resetting-state#state-is-tied-to-a-position-in-the-tree), [Resetting state with a key](https://react.dev/learn/preserving-and-resetting-state#option-2-resetting-state-with-a-key), and [Rendering Lists — Keeping list items in order with key](https://react.dev/learn/rendering-lists#keeping-list-items-in-order-with-key).

## 11. Context used before composition and ownership are clear

**Failure mode.** Context hides dependencies, makes reuse harder, or turns a local value into a tree-wide concern. Every consumer can now read a value even though only one branch needed it.

**Concrete example.** A `Layout` introduces `HeadingLevelContext` only to avoid passing a prebuilt `content` region, or an app puts every page's transient form values into one global context.

**Expert rule.** First try explicit props; if intermediate components do not need the data, try composition by passing JSX as `children` or named slots. Use context when distant descendants genuinely need the same tree-scoped value. Keep the provider near the owning state and make the dependency visible through a focused custom Hook. Choosing how finely to split contexts is engineering judgment: split when values have different ownership or update patterns, because that keeps contracts narrower.

**Evidence.** React, [Passing Data Deeply with Context — Before you use context](https://react.dev/learn/passing-data-deeply-with-context#before-you-use-context) and [Use cases for context](https://react.dev/learn/passing-data-deeply-with-context#use-cases-for-context).

## 12. State transitions scattered across handlers

**Failure mode.** Many handlers update related state fields in different orders, so adding a new transition requires editing several places and invalid intermediate combinations appear.

**Concrete example.** A task list has separate add, change, and delete handlers that each manipulate the array directly; an edit path forgets the normalization enforced by the add path.

**Expert rule.** Use a reducer when related transitions need one explicit state machine-like owner. Dispatch domain events from handlers; keep the reducer pure, return new state rather than mutate existing state, and make each action describe what happened. A reducer is not automatically better for one boolean—React explicitly presents it as a tradeoff in code size, readability, debugging, and testability.

**Evidence.** React, [Extracting State Logic into a Reducer — Consolidate state logic with a reducer](https://react.dev/learn/extracting-state-logic-into-a-reducer#consolidate-state-logic-with-a-reducer), [Comparing useState and useReducer](https://react.dev/learn/extracting-state-logic-into-a-reducer#comparing-usestate-and-usereducer), and [Writing reducers well](https://react.dev/learn/extracting-state-logic-into-a-reducer#writing-reducers-well).

## 13. Reducer and context coupled without an access boundary

**Failure mode.** State and dispatch are threaded through many layers, or raw contexts are imported everywhere. Provider absence yields opaque failures and consumers become coupled to representation details.

**Concrete example.** `TaskList` needs tasks while `AddTask` needs dispatch; both receive both props through unrelated layout components, then later import `TasksContext` directly from several files.

**Expert rule.** For a subtree-owned domain, combine `useReducer` with separate state and dispatch contexts, expose focused access Hooks, and place the provider in one module. Separate contexts let read-only consumers depend only on state and command-only consumers depend only on dispatch. Throw a clear error from access Hooks when the provider is missing; that last guard is engineering judgment, justified by making an otherwise implicit runtime precondition observable.

**Evidence.** React, [Scaling Up with Reducer and Context — Combining a reducer with context](https://react.dev/learn/scaling-up-with-reducer-and-context#combining-a-reducer-with-context), [Put state and dispatch into context](https://react.dev/learn/scaling-up-with-reducer-and-context#step-2-put-state-and-dispatch-into-context), and [Moving all wiring into a single file](https://react.dev/learn/scaling-up-with-reducer-and-context#moving-all-wiring-into-a-single-file).

## 14. Custom Hooks mistaken for shared state or generic lifecycle wrappers

**Failure mode.** `useMount`, `useEffectOnce`, or a vague `useData` wrapper hides dependencies and synchronization semantics. Two consumers are expected to share one state instance merely because they call the same Hook.

**Concrete example.** Two status badges call `useOnlineStatus()` and a developer assumes the Hook stores one shared `isOnline`; or a custom `useMount(fn)` suppresses dependency linting and captures old props.

**Expert rule.** Extract a custom Hook to share stateful *logic*, not state itself. Give it a concrete high-level purpose, keep its reactive inputs explicit, and preserve the underlying Hook rules. Each call is independent unless the Hook intentionally subscribes to shared external state or context. Prefer `useChatRoom({serverUrl, roomId})` over lifecycle-shaped wrappers that obscure what is synchronized.

**Evidence.** React, [Reusing Logic with Custom Hooks — Custom Hooks: Sharing logic between components](https://react.dev/learn/reusing-logic-with-custom-hooks#custom-hooks-sharing-logic-between-components), [Custom Hooks let you share stateful logic, not state itself](https://react.dev/learn/reusing-logic-with-custom-hooks#custom-hooks-let-you-share-stateful-logic-not-state-itself), and [Keep your custom Hooks focused on concrete high-level use cases](https://react.dev/learn/reusing-logic-with-custom-hooks#keep-your-custom-hooks-focused-on-concrete-high-level-use-cases).
