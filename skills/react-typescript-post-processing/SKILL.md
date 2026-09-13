---
name: react-typescript-post-processing
description: Post-process JavaScript and TypeScript source and tests, including React, services, tools and schemas, after implementation. Improve naming, layout, function boundaries, data shapes and test clarity while preserving behavior, ownership and public contracts. Apply to the whole selected codebase when requested.
---

# JavaScript, TypeScript and React post-processing

Work on the complete selected implementation after the feature is done. Include JavaScript and TypeScript source and tests: services, tools, parsers, schemas and React code. When the user requests the whole codebase, inventory every first-party JS/TS file, including `.mjs` tests, and read whole files rather than only the diff. Otherwise, stay within the selected change and its necessary context. Read callers and installed runtime or framework configuration before changing their contracts.

The result should be pleasant to read and straightforward to maintain. A reader should be able to follow the control flow, inspect data shapes and understand each operation without unpacking dense expressions or reconstructing hidden setup. Preserve behavior, ownership and existing architectural boundaries while improving how the code communicates them.

A small diff is not the goal of this pass. Budget for the requested scope and reforecast if it needs more work; do not compress statements or stop short of a justified improvement to meet a self-imposed line count. Clear code may stay unchanged, but green checks alone do not establish clarity. Extra helpers, types and modules must earn their navigation cost.

The comparisons distinguish hidden assumptions, explicit contracts and structures that protect useful invariants. They are alternatives, not a ladder that requires choosing the most abstract version. Some bad examples expose behavioral defects. Identify those separately from equivalent rewrites; apply a behavioral correction only when authorized, with a focused regression check. React-specific sections apply only to React code.

## Make the code readable on the page

Keep one meaningful operation per statement and give separate steps their own lines. Use blank lines to separate setup, decisions, effects and results. Give nontrivial branches, callbacks and cleanup visible bodies instead of packing them behind punctuation. Short expressions can stay short when they are immediately clear.

Lay out multi-field objects, schemas and returned records so their fields, defaults and optional values can be inspected vertically. Break a long condition into visible clauses or ordered guards. Name an intermediate decision when the name explains a domain rule; do not introduce a boolean for every comparison. Preserve short-circuiting, evaluation order and side effects while restructuring.

Use names that explain the operation or value at the reader's current level. A function should perform one cohesive operation. Split at a real domain decision, reusable policy or independently readable transformation, not at an arbitrary line count. Keep a short sequence together when extracting helpers would force readers to jump around to understand it. Keep validation, orchestration and persistence distinguishable without building a new framework.

Use the project's existing formatter where configured. Formatting helps expose structure; it does not repair vague names or mixed responsibilities. When no formatter is configured, use consistent indentation and ordinary expanded code rather than copying locally compressed code or installing tooling just for this pass.

## Make tests explain the scenario

Read existing tests as code that other people must maintain. Give setup, the action and assertions visible separation. Name fixtures and results for what they represent. Expose the fields that matter to the scenario; keep incidental defaults in an existing or small domain-focused fixture when that reduces noise. Inspect those defaults so they do not hide the condition being tested.

For example, with an existing `makeCart` fixture and `calculateShipping` as the function under test:

```js
test("shipping is free when the subtotal reaches 50", () => {
  const cart = makeCart({ subtotal: 50 });

  const shippingCost = calculateShipping(cart);

  assert.equal(shippingCost, 0);
});
```

Keep assertions, isolation, timing and fixture lifetimes intact. Expand dense setup and assertion chains before deciding whether a helper is needed. A test builder that hides the scenario is worse than a clear local literal. Do not add tests just to prove that code was reformatted.

## Let types describe reachable states

The following excerpts use `Item` as a small application type:

```ts
type Item = { id: string; name: string };
```

Use the application's vocabulary. Name callbacks for their meaning and pass the value consumers need. Keep required values required, represent genuine absence, and let local inference handle obvious types. Use generics when they preserve an actual relationship, not to make a concrete component appear reusable.

Here, loading, ready, and failed are mutually exclusive. Only ready has items; only failed has an error.

**Bad — independent fields allow contradictory states.**

```ts
type ResultState = {
  loading: boolean;
  items?: readonly Item[];
  error?: Error;
};
```

**Good — one field names the current phase.**

```ts
type ResultState = {
  status: "loading" | "ready" | "failed";
  items?: readonly Item[];
  error?: Error;
};
```

**Great — narrowing the phase also establishes its payload.**

```ts
type ResultState =
  | { status: "loading" }
  | {
      status: "ready";
      items: readonly Item[];
    }
  | {
      status: "failed";
      error: Error;
    };
```

Use the union where consumers otherwise need assertions or repeated defensive checks. If the product intentionally displays previous results while refreshing, model that reachable state too. Do not erase it to simplify the type. Preserve exported names and accepted prop combinations unless changing them is in scope. Types and `satisfies` do not validate runtime input.

## Store decisions; derive their consequences

Keep each state value with its owner. Controlled props remain authoritative; `default` or `initial` values seed local state. Preserve intentional drafts and reset behavior. A copied prop is not automatically redundant, but a value entirely determined by current inputs usually is.

These excerpts use current `items` and `query`; filtering has no delayed-update contract.

**Bad — an effect maintains a second copy of derived data.**

```tsx
const [visibleItems, setVisibleItems] = useState<readonly Item[]>([]);

useEffect(() => {
  setVisibleItems(items.filter(item =>
    item.name.toLowerCase().includes(query.trim().toLowerCase())
  ));
}, [items, query]);
```

**Good — the rendered value follows the current inputs directly.**

```ts
const visibleItems = items.filter(item =>
  item.name.toLowerCase().includes(query.trim().toLowerCase())
);
```

**Great — a meaningful local separates query normalization from matching.**

```ts
const searchText = query.trim().toLowerCase();
const visibleItems = items.filter(item =>
  item.name.toLowerCase().includes(searchText)
);
```

The normalization policy stays intact. Add memoization only for demonstrated computation cost or a meaningful identity consumer; preserve existing identity dependencies when removing it. A memoized value is not durable state.

Use functional updates when the next value depends on pending state. Copy the collection being changed and preserve unaffected references. When one operation changes related values, keep its invariant together: removing an item may also need to remove its selection. Do not replace the existing state system merely to express that operation differently.

## Validate at the boundary; trust the established contract inside

Accept `unknown` at an unvalidated boundary and narrow it through real checks. Reuse the project's schema or parser when available. Avoid `any`, non-null assertions, and casts that conceal missing evidence; do not spread repeated validation throughout rendering code.

This boundary accepts JSON with string identifiers and names and returns those two fields. Empty-string policy is a separate domain rule.

**Bad — a cast supplies no runtime evidence.**

```ts
function readItem(text: string): Item {
  const value = JSON.parse(text) as Item;
  return { id: value.id, name: value.name };
}
```

**Good — the boundary checks every field it exposes.**

```ts
function readItem(text: string): Item {
  const value: unknown = JSON.parse(text);

  if (typeof value !== "object" || value === null) {
    throw new TypeError("Invalid item");
  }

  if (!("id" in value) || typeof value.id !== "string") {
    throw new TypeError("Invalid item");
  }

  if (!("name" in value) || typeof value.name !== "string") {
    throw new TypeError("Invalid item");
  }

  return {
    id: value.id,
    name: value.name,
  };
}
```

**Great — several entry points can share one validation contract.**

```ts
function parseItem(value: unknown): Item {
  if (typeof value !== "object" || value === null) {
    throw new TypeError("Invalid item");
  }

  if (!("id" in value) || typeof value.id !== "string") {
    throw new TypeError("Invalid item");
  }

  if (!("name" in value) || typeof value.name !== "string") {
    throw new TypeError("Invalid item");
  }

  return {
    id: value.id,
    name: value.name,
  };
}

function readItem(text: string): Item {
  return parseItem(JSON.parse(text));
}
```

Keep good for a single isolated boundary. Keep existing error presentation and recovery outside the parser. Do not introduce a validation dependency, coercion policy, or silent fallback merely for this pass.

## Give each effect one resource lifetime

Use effects to synchronize with external systems. Put interaction-triggered work in its event path when that is the existing contract, and calculate derived values during rendering. Keep hooks unconditional and dependencies truthful.

Assume `feed.subscribe(topic, onUpdate)` returns a disposer. The feed, topic, and callback are reactive inputs.

**Bad — the subscription leaks and keeps its initial inputs.**

```tsx
useEffect(() => {
  feed.subscribe(topic, onUpdate);
}, []);
```

**Good — acquisition and release share their exact inputs.**

```tsx
useEffect(() => {
  return feed.subscribe(topic, onUpdate);
}, [feed, topic, onUpdate]);
```

**Great — repeated subscription behavior gains a small, named boundary.**

```tsx
type Feed = {
  subscribe(topic: string, onUpdate: () => void): () => void;
};

function useFeedSubscription(
  feed: Feed,
  topic: string,
  onUpdate: () => void
) {
  useEffect(() => {
    return feed.subscribe(topic, onUpdate);
  }, [feed, topic, onUpdate]);
}
```

Define the hook at module scope and call `useFeedSubscription(feed, topic, onUpdate)` unconditionally inside the consuming component. Keep good when extraction adds no useful concept. Do not conceal dependencies behind a generic “run once” hook. Use supported effect-event APIs only for genuinely nonreactive behavior; they are not a way to silence dependency checks.

Cleanup must release the resource actually acquired. Capture the subscribed element inside the effect instead of reading a possibly changed `ref.current` during cleanup. A stable ref object does not announce node replacement; preserve the project's mechanism for observing target changes. Verify setup, cleanup, and setup again under Strict Mode.

## Separate cancellation from permission to commit a result

Keep the existing router or query layer in charge of fetching, caching, and server rendering. For an existing client effect, make request ownership visible. Cancellation saves work where supported; a completion guard prevents obsolete work from changing current state.

These alternatives sit inside a component with `query`, a stable `loadItems(query, signal?)` returning `Promise<readonly Item[]>`, and state initialized as `{ query, status: "loading" }`. The loader reports failures by rejection. Use the union above, with its query attached:

```ts
type SearchState = ResultState & { query: string };

function toError(error: unknown): Error {
  return error instanceof Error ? error : new Error("Unable to load items");
}
```

**Bad — an earlier request can overwrite a later result.**

```tsx
useEffect(() => {
  setState({ query, status: "loading" });

  void loadItems(query).then(
    items => {
      setState({
        query,
        status: "ready",
        items,
      });
    },
    error => {
      setState({
        query,
        status: "failed",
        error: toError(error),
      });
    }
  );
}, [query, loadItems]);
```

**Good — superseded and unmounted effects cannot commit.**

```tsx
useEffect(() => {
  let active = true;
  setState({ query, status: "loading" });

  void loadItems(query).then(
    items => {
      if (active) {
        setState({
          query,
          status: "ready",
          items,
        });
      }
    },
    error => {
      if (active) {
        setState({
          query,
          status: "failed",
          error: toError(error),
        });
      }
    }
  );

  return () => {
    active = false;
  };
}, [query, loadItems]);
```

**Great — cleanup also requests cancellation without trusting the loader to obey.**

```tsx
useEffect(() => {
  const controller = new AbortController();
  let active = true;
  setState({ query, status: "loading" });

  void loadItems(query, controller.signal).then(
    items => {
      if (active) {
        setState({
          query,
          status: "ready",
          items,
        });
      }
    },
    error => {
      if (active) {
        setState({
          query,
          status: "failed",
          error: toError(error),
        });
      }
    }
  );

  return () => {
    active = false;
    controller.abort();
  };
}, [query, loadItems]);
```

Use good when the loader cannot cancel. Both settlement paths need the guard. Keep previous-query results from appearing under a new query before the effect runs; here the view renders a loading state when `state.query !== query`. If stale results are intentionally displayed, preserve and label that policy. Request identity must include every input that determines the result.

Test completion in both orders, failure, query replacement, and unmount for changes to this logic. Include a loader that resolves after cancellation. Do not turn this excerpt into a new fetching framework or add a ref that defeats Strict Mode's cleanup check.

## Compose around meaningful interactions

Prefer components and hooks that own a coherent responsibility. Pass semantic values and explicit children rather than making callers decode DOM details. Extract components at module scope; defining them during rendering can reset their state. Use stable domain keys when list identity matters.

Here, removing an item is an ordinary button action with a contextual accessible name.

**Bad — a pointer handler does not provide button semantics.**

```tsx
<div onClick={() => onRemove(item.id)}>Remove</div>
```

**Good — the native control supplies the expected interaction.**

```tsx
<button
  type="button"
  aria-label={`Remove ${item.name}`}
  onClick={() => onRemove(item.id)}
>
  Remove
</button>
```

**Great — a recurring action has one clear, typed contract.**

```tsx
type RemoveItemButtonProps = {
  item: Item;
  onRemove: (id: Item["id"]) => void;
};

function RemoveItemButton({ item, onRemove }: RemoveItemButtonProps) {
  return (
    <button
      type="button"
      aria-label={`Remove ${item.name}`}
      onClick={() => onRemove(item.id)}
    >
      Remove
    </button>
  );
}
```

Keep good when the inline action is already clear. Reuse the application's existing accessible primitive where appropriate. Preserve form submission, focus, disabled and pending behavior, accessible names, refs, and event ordering. `aria-disabled` alone does not suppress activation. Blind prop spreading can overwrite those contracts; retain deliberate handler composition and precedence.

## Verify behavior and readability separately

Read every selected source and test file in its final form, including unchanged portions. Check whether a maintainer can identify each function's purpose, follow its branches and effects, inspect object/schema fields, and understand each test's scenario without unpacking dense lines or hidden setup. Improve remaining reading obstacles within scope. Do not force edits where this standard is already met.

Let names, types and composition explain what happens. Remove comments that narrate statements or compensate for unclear code. Keep comments only for necessary, established business rationale the code cannot express; never invent a policy. Preserve required license notices and machine-interpreted directives.

Preserve module conventions, public APIs, callback timing, ownership, error handling and resource lifetimes. For React, also preserve component identity and client/server boundaries. Avoid casts, lint suppressions, speculative memoization and architectural migrations introduced solely to make a rewrite pass.

Run authorized type checks, relevant lint rules and affected tests. For changed interactions, check accessible role and name, keyboard activation, focus and the observable result. For changed lifetimes, check replacement and cleanup. Add tests only for a concrete behavioral risk or correction; do not mirror the implementation with tests of private helpers. These checks establish behavior, not readability.

Compare the final code with the starting point. Check that clearer local steps did not turn into a maze of helpers and that no contract changed along with the layout. Report the complete scope inspected, representative readability improvements, behavioral verification and remaining limits. For unchanged files, explain briefly why their flow, names and data shapes are already clear. Reading files, passing tests or staying under a line budget alone is not completion evidence.
