# JavaScript Runtime Reference

> Return to [SKILL.md](../SKILL.md) for core workflow, boundaries, and reference-selection rules.

Use these defect classes when behavior depends on tasks, microtasks, promises, cancellation, module formats, server execution, cloning, fetch, or streams. Verify the actual browser/Node versions and bundler because support and interop details are version-sensitive.

---

## 1. Task and microtask ordering guessed from source order

**Failure mode.** A timer callback is expected to run before a resolved Promise because `setTimeout` appears first. Tests become timing-dependent and state commits in an unexpected order.

**Concrete example.** Code schedules `setTimeout(logTimer, 0)`, then `Promise.resolve().then(logPromise)`. `logPromise` runs first: after the current task completes, the runtime drains the microtask queue before the next task.

**Expert rule.** Trace scheduling by queue, not textual order. The current call stack completes; queued microtasks run until the microtask queue is empty; then the event loop can take another task and render/update as the host permits. Promise reactions and `queueMicrotask` use microtasks; timers enqueue tasks. Write tests around observable completion, not guessed wall-clock gaps.

**Evidence.** MDN, [Microtask guide — Tasks vs. microtasks](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide#tasks_vs._microtasks) and [Using microtasks in JavaScript with `queueMicrotask()`](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide).

## 2. Recursive microtasks starve the host

**Failure mode.** A microtask queues another microtask indefinitely. Timers, input, networking callbacks, and browser rendering do not get a turn.

**Concrete example.** `function flush() { queueMicrotask(flush) }` keeps the microtask queue non-empty. A zero-delay timeout never runs and the page appears frozen.

**Expert rule.** Keep microtasks bounded and short. When work can grow, process a finite chunk and yield through a task/scheduler primitive appropriate to the host. The chunk size and yielding primitive are engineering judgments that require latency measurements; the documented fact is that newly added microtasks run before the event loop proceeds to the next task, creating starvation risk.

**Evidence.** MDN, [Microtask guide — Warning about endlessly processing microtasks](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide#warning).

## 3. Promise callbacks assumed to run synchronously

**Failure mode.** Code expects `.then` to mutate a variable before the next line, or a callback API conditionally returns synchronously while its Promise path returns asynchronously, creating inconsistent ordering.

**Concrete example.** `let ready = false; Promise.resolve().then(() => { ready = true }); console.log(ready)` prints `false`.

**Expert rule.** Promise fulfillment/rejection handlers run asynchronously as microtasks, including handlers attached to an already-settled Promise. Keep APIs consistently asynchronous when ordering is part of their contract. Return from `.then` to transform a chain; throw to reject it; return a Promise/thenable to make the next step adopt its eventual state. Do not nest a Promise without returning or awaiting it.

**Evidence.** MDN, [Using Promises — Timing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises#timing), [Chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises#chaining), and [`Promise.prototype.then()` — Return value](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then#return_value).

## 4. `async`/`await` mistaken for blocking execution

**Failure mode.** A caller treats an `async` function's return as a value, or expects code after `await` to remain in the same synchronous turn. Thrown errors escape the intended handling path as rejected Promises.

**Concrete example.** `const user = loadUser(); user.name` reads a Promise. Inside `loadUser`, a thrown parse error rejects the returned Promise; an outer synchronous `try` that did not `await` it cannot catch the rejection.

**Expert rule.** Every `async` call returns a Promise. `await` pauses only that async function and schedules its continuation; it does not block the thread. `return value` fulfills the returned Promise, while an uncaught throw rejects it. At each call boundary, either `await` inside `try`/`catch`, return the Promise to a caller responsible for it, or attach a terminal rejection handler.

**Evidence.** MDN, [`async function` — Description](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function#description) and [`await` — Description](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await#description).

## 5. Floating Promise produces an unhandled rejection

**Failure mode.** A Promise is created and ignored. When it rejects, the browser emits `unhandledrejection` or Node reports an unhandled rejection according to its runtime policy; the intended request/job boundary never records failure.

**Concrete example.** An event handler calls `saveDraft()` without `await`, `return`, or `.catch`. A network rejection occurs after the handler returns and bypasses UI error state.

**Expert rule.** Make Promise ownership explicit. Await it, return it to a framework that documents ownership, or deliberately detach it with an immediate rejection handler that reports context. Global browser/Node unhandled-rejection hooks are last-resort observability, not local recovery. Never assume attaching a handler much later is equivalent; hosts detect the period in which a rejection has no handler.

**Evidence.** MDN, [`Window: unhandledrejection` event](https://developer.mozilla.org/en-US/docs/Web/API/Window/unhandledrejection_event), and Node.js, [`process` event: `unhandledRejection`](https://nodejs.org/api/process.html#event-unhandledrejection).

## 6. Cancellation modeled as forced Promise termination

**Failure mode.** Code assumes a Promise can be killed after creation. The caller stops awaiting it, but network, stream, timer, or CPU work continues and may still perform side effects.

**Concrete example.** A route changes and drops a fetch Promise, but the request remains in flight and its completion writes to a cache associated with the old route.

**Expert rule.** Cancellation is cooperative. The operation must accept a cancellation capability such as `AbortSignal`, observe it, and stop or reject according to its API. Define who owns the `AbortController`, when ownership ends, and whether one signal cancels one operation or a group. Reject immediately when passed an already-aborted signal, and remove abort listeners when a long-lived custom operation settles.

**Evidence.** MDN, [`AbortController`](https://developer.mozilla.org/en-US/docs/Web/API/AbortController), [`AbortSignal`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal), and [Implementing an abortable API](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal#implementing_an_abortable_api).

## 7. Aborted or superseded fetch still commits stale UI

**Failure mode.** Several requests race and an older response updates state after the query or component changed. Aborting transport is omitted or failure handling treats `AbortError` as a user-visible server failure.

**Concrete example.** Search for `re`, then `react`; the first response arrives last and replaces the current results. Navigation aborts a request and displays “Something went wrong.”

**Expert rule.** Create a controller per request ownership period, pass `signal` to `fetch`, and abort on supersession/teardown. Also gate commits by request identity when work beyond fetch is not abortable. Handle abort separately from timeout/network/server failures. When composing signals or timeouts, preserve enough reason/context to report the actual failure class.

**Evidence.** MDN, [Using Fetch — Canceling a request](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#canceling_a_request), [`AbortSignal.timeout()`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static), and [`AbortSignal.any()`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/any_static).

## 8. Fetch fulfillment mistaken for HTTP success

**Failure mode.** Code expects `fetch` to reject on 404 or 500 and immediately parses a success payload. Error HTML or an error JSON shape is treated as domain data.

**Concrete example.** `fetch('/orders/1').then(r => r.json()).then(showOrder)` runs `showOrder` for a 500 JSON response because HTTP error status does not itself reject the fetch Promise.

**Expert rule.** Separate transport failure from HTTP status. Check `response.ok` or the exact acceptable statuses before parsing the success schema; parse and report an error schema deliberately. Validate content type when the server contract requires JSON. Remember that a response body is a stream and generally can be consumed only once unless cloned first.

**Evidence.** MDN, [Using Fetch — Checking response status](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#checking_response_status), [Checking the response type](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#checking_the_response_type), and [Locked and disturbed streams](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#locked_and_disturbed_streams).

## 9. ESM and CommonJS semantics conflated

**Failure mode.** `require`, `module.exports`, `__dirname`, default imports, and named imports are assumed to behave identically across module systems. Code works through one transpiler but fails in Node or a test runner.

**Concrete example.** An ESM file uses `__dirname`, or `import {readFile} from './cjs-wrapper.cjs'` relies on named exports that Node cannot reliably infer from a dynamic CommonJS shape.

**Expert rule.** Determine the module format from file extension, nearest `package.json` `type`, entry point, and tool configuration. In Node ESM, use `import`/`export`, `import.meta.url`/`import.meta.dirname` where supported, and `module.createRequire()` only at a deliberate interop seam. CommonJS imported into ESM always exposes a `default` pointing at `module.exports`; static named exports are best-effort analysis, so prefer the default namespace when the CJS package does not document named ESM interop.

**Evidence.** Node.js, [ECMAScript modules — Interoperability with CommonJS](https://nodejs.org/api/esm.html#interoperability-with-commonjs), [Differences between ES modules and CommonJS](https://nodejs.org/api/esm.html#differences-between-es-modules-and-commonjs), and [Packages — Determining module system](https://nodejs.org/api/packages.html#determining-module-system).

## 10. Import resolution assumed to be bundler magic everywhere

**Failure mode.** Extensionless relative imports, directory indexes, aliases, or deep package paths work in a bundler but fail under Node ESM, tests, declaration emit, or SSR.

**Concrete example.** `import './utils'` resolves to `utils/index.ts` in development bundling but Node ESM requires the fully specified path. A consumer imports `pkg/internal` even though `exports` exposes only `.`.

**Expert rule.** Trace resolution in every host that executes or analyzes the module: Node, bundler, TypeScript, test runner, and SSR tool. Node ESM requires file extensions for relative/absolute file imports and does not perform CommonJS-style folder-main resolution. Respect package `exports`; it defines public subpaths and can encapsulate internals. Align TypeScript `module`/`moduleResolution` with the runtime rather than adding aliases to one tool only.

**Evidence.** Node.js, [ECMAScript modules — Mandatory file extensions](https://nodejs.org/api/esm.html#mandatory-file-extensions), [Resolution algorithm](https://nodejs.org/api/esm.html#resolution-algorithm-specification), and [Packages — Package entry points](https://nodejs.org/api/packages.html#package-entry-points).

## 11. Barrel module hides cycles and side effects

**Failure mode.** A wide `index.ts` re-exports modules that import back through the barrel. Evaluation encounters an uninitialized live binding, or importing one symbol executes unrelated side-effectful modules.

**Concrete example.** `feature/index.ts` exports `store` and `selectors`; `store.ts` imports `selectCurrent` from `./index.js`. The cycle reads a lexical binding before initialization and throws.

**Expert rule.** Trace the concrete module graph, not only the public import. Modules have live bindings and cyclic evaluation can expose uninitialized values. Inside a package/feature, import the owning module directly rather than routing back through its public barrel. Keep barrels shallow and free of initialization side effects. This barrel policy is explicit engineering judgment: MDN documents cycles and evaluation; direct internal imports reduce graph ambiguity and accidental execution.

**Evidence.** MDN, [JavaScript modules — Cyclic imports](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#cyclic_imports), [Imported values can only be modified by the exporter](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#imported_values_can_only_be_modified_by_the_exporter), and [`export` — Re-exporting / aggregating](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/export#re-exporting_aggregating).

## 12. Browser-only globals evaluated during SSR or import

**Failure mode.** `window`, `document`, `localStorage`, `navigator`, or layout APIs are read at module top level or during server render. Importing the module on Node throws before the client can hydrate.

**Concrete example.** `const theme = localStorage.getItem('theme')` runs when an SSR server imports the component. Node has no `localStorage`, and the request fails.

**Expert rule.** Identify every environment in which the module is imported and rendered. Keep browser-only access in a client entry point, event handler, or client-side Effect after mount, according to the framework's boundary model. A `typeof window` branch inside render avoids a reference error but can create different server/client markup and a hydration mismatch. This placement rule is engineering judgment derived from the documented browser scope of `Window` and Node's distinct global object.

**Evidence.** MDN, [`Window`](https://developer.mozilla.org/en-US/docs/Web/API/Window), and Node.js, [Global objects](https://nodejs.org/api/globals.html), plus React, [`hydrateRoot` — server and client output must be identical](https://react.dev/reference/react-dom/client/hydrateRoot#pitfall).

## 13. Top-level side effects make imports order-dependent

**Failure mode.** Importing a module starts timers, registers listeners, reads environment state, or mutates a singleton. Tests and SSR requests affect one another based on cache and evaluation order.

**Concrete example.** `analytics.ts` installs a global listener at import time. Hot reload and isolated test environments import it repeatedly or in a different order, duplicating delivery.

**Expert rule.** Keep ordinary modules declarative at top level: definitions, immutable configuration, and intentional singleton construction only when import-once semantics are the contract. Expose explicit `start`/`stop` or `connect`/`disconnect` for owned resources and make teardown testable. This is an explicit engineering judgment; MDN documents that module code executes only once per resolved module, which is why hidden import effects become cached global state.

**Evidence.** MDN, [JavaScript modules — Modules are only executed once](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules#modules_are_only_executed_once).

## 14. `structuredClone` treated as JSON stringify/parse

**Failure mode.** Code expects cloning to preserve prototypes, functions, DOM nodes, or property descriptors, or uses JSON as a “deep clone” and silently loses `Date`, `Map`, `Set`, circular references, `undefined`, and typed data.

**Concrete example.** An object containing a `Map`, `Date`, and self-reference fails or changes shape through JSON round-tripping; switching to `structuredClone` preserves supported data but a function property raises `DataCloneError`.

**Expert rule.** Use `structuredClone` only for values supported by the structured clone algorithm and handle `DataCloneError` at untrusted boundaries. Do not assume custom class prototypes or descriptors survive as domain objects; reconstruct domain instances explicitly when behavior matters. Use the `transfer` option for transferable buffers only when invalidating the original is intended and owned.

**Evidence.** MDN, [`structuredClone()`](https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone), [The structured clone algorithm — Supported types](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm#supported_types), and [Things that don't work with structured clone](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm#things_that_dont_work_with_structured_clone).

## 15. Stream body buffered unintentionally

**Failure mode.** A large response or file is converted to `text()`, `json()`, or one giant buffer before processing. Memory scales with payload size and useful work waits for the full body.

**Concrete example.** A 2 GB newline-delimited export calls `await response.text()` and splits lines, causing a large allocation and long delay before the first record is handled.

**Expert rule.** When the contract permits incremental processing, read `response.body` as a `ReadableStream`, decode through `TextDecoderStream`, and parse across chunk boundaries. Bound retained buffers and define cancellation/error cleanup. Streaming adds parser and lifecycle complexity, so choosing it is engineering judgment based on measured payload size and latency—not a default for small JSON.

**Evidence.** MDN, [Using Fetch — Streaming the response body](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#streaming_the_response_body) and [Processing a text file line by line](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#processing_a_text_file_line_by_line).

## 16. Backpressure ignored in a stream pipeline

**Failure mode.** A producer writes faster than downstream can process and keeps buffering. Memory grows without bound even though each individual chunk is small.

**Concrete example.** A custom `ReadableStream` enqueues chunks in a tight loop without consulting demand, while a network sink processes one chunk at a time.

**Expert rule.** Build pipelines around the Streams API's demand and backpressure signals. In custom underlying sources, enqueue according to controller demand and stop/slow production when desired size indicates pressure. Use `pipeThrough`/`pipeTo` where their propagation of backpressure, errors, and cancellation matches ownership. In Node, distinguish Web Streams from classic Node streams and use documented adapters when crossing the boundary.

**Evidence.** MDN, [Streams API concepts and usage](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API#concepts_and_usage) and [Using readable streams — Enqueueing chunks](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams#the_readablestream_constructor), plus Node.js, [Web Streams API](https://nodejs.org/api/webstreams.html).

## 17. Stream/resource lifecycle left open on failure

**Failure mode.** A reader lock, file handle, socket, interval, or response body remains owned after an exception or cancellation. The process stays alive or later work cannot acquire the resource.

**Concrete example.** Code calls `const reader = stream.getReader()` and throws while parsing; it never cancels the reader or releases the lock, so another consumer cannot read the stream.

**Expert rule.** Make ownership and teardown explicit with `try`/`finally`. Cancel a stream when remaining data is unwanted, release reader/writer locks where required, clear timers, and close handles at the outer boundary that acquired them. Do not call `process.exit()` to hide outstanding resources; let the event loop drain after deterministic cleanup. Exact teardown calls are API-specific, so follow the resource's documented contract.

**Evidence.** MDN, [`ReadableStream.getReader()`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream/getReader), [`ReadableStreamDefaultReader.releaseLock()`](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStreamDefaultReader/releaseLock), and Node.js, [Process — `process.exit()` warning](https://nodejs.org/api/process.html#processexitcode).
