---
name: rails-test-post-processing
description: Post-process existing Rails tests after implementation to keep the smallest clear set that protects agreed behavior and material risks. Use to reduce redundant or unfocused tests, assess test necessity, and improve assertions and isolation. Preserve the test framework and production behavior.
---

# Rails test post-processing

*Draft for review*

Work on the selected tests after implementation and before final code review. Read the user's requirement and changed behavior before treating the tests as a specification. Inspect nearby existing coverage, relevant production code, fixtures, and helpers. Keep the existing framework; production changes belong to a separate task. Limit edits to the selected change and directly affected tests, not a repository-wide cleanup.

## Decide which tests earn their place

Select first, simplify second, and strengthen only where evidence requires it. Aim for the smallest clear set that protects agreed behavior and material risks, not the fewest test methods or assertions. No finite suite covers everything.

For each selected test, identify its triggering condition, observable outcome, and plausible failure. Ask what protection or useful failure diagnosis would disappear if it were removed. Use a short working map when needed; do not create a separate report for every test.

| Decision | Evidence needed |
| --- | --- |
| Keep | A distinct required behavior, meaningful input boundary, regression, integration failure, or useful diagnostic distinction. |
| Consolidate | The same condition, boundary, and promised outcome, with no distinct failure lost. Keep the surviving scenario readable and independently diagnosable. |
| Rewrite | A real contract obscured by private wiring assertions, configuration mirrors, incidental object fields, or mocks that hide the behavior. Observe the promised result instead. |
| Delete | An obsolete or non-contractual expectation, or duplicate protection demonstrably retained elsewhere. Name the removed requirement or surviving check. |
| Add | A concrete gap in the current requirement or regression that existing tests miss. Prefer strengthening a suitable test before adding an overlapping one. |
| Leave alone | Tests outside the selected change. Do not turn post-processing into speculative hardening or unrelated cleanup. |

Prefer the least costly stable test boundary that can expose the failure. Preserve overlap across levels when it catches different failures: a model test can prove a rule while a request test proves authorization and persistence. Shared code execution alone does not make tests duplicates. Do not replace a real integration boundary with mocks that conceal its failures.

Choose representative inputs from genuinely equivalent cases; keep boundaries where the promised behavior changes. Do not generate a Cartesian product of nil, empty, invalid, flag, timing, and permission variations without a distinct contractual reason. Retain relevant denied-access, forbidden-side-effect, retry, and concurrency cases.

Keep each test about one coherent behavior, which may require several actions and assertions. Do not combine unrelated scenarios into a giant test or hide meaningful differences in parameter tables to reduce the count. Small explicit repetition is preferable to helpers that obscure why a case matters.

Remove assertions for removed behavior. Do not replace them with assertions that old output or files stay absent unless that absence is itself a durable requirement not already protected by positive behavior. Do not create executable tests solely for static prose, labels, markup, CSS, or source-string matching; inspect those directly or through a rendered check. Observable application output remains valid behavioral evidence.

Keep one-off environment and framework diagnostics as investigation evidence unless they provide a stable, needed regression check. A diagnostic that depends on private framework internals or a personal installation is not automatically suitable for the permanent suite.

Stop when the agreed behavior and material risks have credible checks and no concrete in-scope gap remains. Unchanged tests are a valid result. Do not target a coverage percentage, test count, assertion quota, or deletion quota. If the test diff is large because the change bundles several product outcomes, report that scope problem rather than deleting protection to disguise it.

## Improve the retained tests

The comparisons show **bad** tests with misleading or incomplete evidence, **good** tests that establish the main outcome, and **great** tests that distinguish a meaningful competing failure. They are alternatives, not required upgrades. Keep good when it fully expresses the contract. More assertions, abstraction, or setup do not make a test better.

Examples are alternative test bodies using standard Rails test helpers. The sample application has pending and completed export fixtures, a completion operation, a queued export job, and a ready-notification mailer. Where a body does not initialize `export`, use the fixture appropriate to that scenario. Use the target project's actual contracts and supported helper versions.

## Make the distinguishing condition visible

Name the behavior and the condition that matters: `rejects an export without a format` tells the reader more than `validations work`. Use fixtures for common valid data and local setup for the unusual case. Keep genuinely shared setup; avoid helpers whose defaults conceal why the test passes.

Here, a format is required and the pending fixture is otherwise valid.

**Bad — unrelated missing fields could explain the failure.**

```ruby
export = Export.new(format: nil)

assert_not export.valid?
```

**Good — the test changes one relevant condition.**

```ruby
export = exports(:pending).dup
assert export.valid?

export.format = nil

assert_not export.valid?
```

**Great — the assertion identifies the violated rule.**

```ruby
export = exports(:pending).dup
assert export.valid?

export.format = nil

assert_not export.valid?
assert export.errors.of_kind?(:format, :blank)
```

Assert localized wording only when that wording is part of the contract. Preserve cases for defaults and explicit overrides when they exercise different behavior. Parameterize interchangeable cases; keep scenarios separate when a table would hide their reasons or failure diagnostics.

## Observe the state the operation promises to change

Choose an observation that would fail if the implementation skipped its work. Prefer expected/actual assertions over boolean comparisons. When persistence matters, query persisted state rather than trusting the object already in memory.

The completion operation must persist the transition from pending to completed.

**Bad — an assignment without a database write could pass.**

```ruby
export = exports(:pending)

export.complete!

assert_equal "completed", export.status
```

**Good — the database contains the expected result.**

```ruby
export = exports(:pending)

export.complete!

assert_equal "completed", export.reload.status
```

**Great — the test proves the promised transition.**

```ruby
export = exports(:pending)

assert_changes -> { export.reload.status },
    from: "pending", to: "completed" do
  export.complete!
end
```

Keep good when only the destination matters. Observe a scalar or a fresh snapshot: `assert_changes -> { export.reload }` does not snapshot attributes, and record equality can conceal changes. Use `assert_difference` for a numerical delta and `assert_no_changes` for a value invariant. A net count cannot prove that no row was replaced.

## Prove the forbidden action did not happen

A negative test should fail for the intended reason and protect the relevant invariant. Keep the action inside the narrow exception assertion, and place that assertion inside any surrounding change or job assertions.

A completed export cannot be canceled: the operation must raise `Export::Locked`, retain its status, and enqueue no work.

**Bad — any application error can satisfy the test.**

```ruby
export = exports(:completed)

assert_raises(StandardError) { export.cancel! }
```

**Good — the expected failure is explicit.**

```ruby
export = exports(:completed)

assert_raises(Export::Locked) { export.cancel! }
```

**Great — raising after a prohibited side effect also fails.**

```ruby
export = exports(:completed)

assert_no_changes -> { export.reload.status }, from: "completed" do
  assert_no_enqueued_jobs do
    assert_raises(Export::Locked) { export.cancel! }
  end
end
```

Execute the action once. Check only invariants that belong to this contract; do not surround every failure with unrelated count assertions. For request tests, retain the application's configured error-response behavior instead of changing exception handling to fit an assertion.

## Separate scheduling from execution

An enqueue test establishes which work was requested. A job test establishes its result. Keep those claims distinct so a scheduling assertion does not accidentally perform the work it observes.

Here, `enqueue` must schedule exactly one `ExportJob` for this record on the exports queue.

**Bad — an unrelated job would satisfy the count.**

```ruby
assert_enqueued_jobs 1 do
  export.enqueue
end
```

**Good — the intended job, argument, and queue are present.**

```ruby
assert_enqueued_with job: ExportJob, args: [export], queue: "exports" do
  export.enqueue
end
```

**Great — duplicate jobs also fail.**

```ruby
assert_enqueued_jobs 1, only: ExportJob do
  assert_enqueued_with job: ExportJob, args: [export], queue: "exports" do
    export.enqueue
  end
end
```

The filtered count permits other job classes; use an unfiltered count only if total work is contractual. Block assertions isolate newly enqueued jobs. A matching job alone does not establish cardinality.

Use the project's test adapter and existing queue cleanup. Exercise jobs through enqueue-and-perform when serialization, callbacks, or retries matter; direct invocation tests a narrower boundary. Filter performed jobs to the scenario. Scheduled jobs may run immediately under `perform_enqueued_jobs` unless a cutoff restricts execution.

For mail scheduling, use `assert_enqueued_email_with` with meaningful parameters and arguments. Block-form `assert_emails` captures delivery by executing queued mail; it is not an equivalent enqueue assertion. Check recipients and relevant content in delivery tests. For exact scheduling requirements, inspect the installed helper's precision: a time-like `at:` expectation may allow a tolerance.

## Test the boundary with a controlled clock

Use time helpers instead of elapsed real time. Choose instants that distinguish the business rule, and use the application's time zone and stored timestamp precision.

An export is downloadable strictly before `expires_at`, and unavailable at that instant. These bodies use an otherwise downloadable export.

**Bad — waiting slows the suite and leaves timing to the machine.**

```ruby
export.update!(expires_at: 1.second.from_now)

sleep 2

assert_not export.downloadable?
```

**Good — the expired case has a deterministic clock.**

```ruby
cutoff = Time.zone.local(2026, 1, 1, 12)
export.update!(expires_at: cutoff)

travel_to cutoff + 1.second do
  assert_not export.downloadable?
end
```

**Great — the test distinguishes the exact expiration rule.**

```ruby
cutoff = Time.zone.local(2026, 1, 1, 12)
export.update!(expires_at: cutoff)

travel_to cutoff - 1.second do
  assert export.downloadable?
end

travel_to cutoff do
  assert_not export.downloadable?
end
```

These are sequential clock scopes. Avoid nested `travel_to` blocks. Helpers remove microseconds by default; preserve them only when the contract and storage support that precision. Test calendar and daylight-saving boundaries when the rule depends on them, not as ritual coverage.

## Assert the useful public response

Use the selected request, job, model, or system boundary to observe the promised behavior. An HTTP status alone cannot establish that the response describes the right record. Assert the relevant public fields without binding the test to unrelated output.

This endpoint promises HTTP 200 and the requested export's identifier and status.

**Bad — every successful status passes.**

```ruby
get export_url(export, format: :json)

assert_response :success
```

**Good — the promised status is precise.**

```ruby
get export_url(export, format: :json)

assert_response :ok
```

**Great — the response must identify the requested record and state.**

```ruby
get export_url(export, format: :json)

assert_response :ok
assert_equal({ "id" => export.id, "status" => export.status },
  response.parsed_body.slice("id", "status"))
```

Assert a whole payload when its entire shape is contractual. For HTML, prefer targeted DOM assertions over formatting-sensitive strings. Preserve meaningful redirect destinations, ownership boundaries, and denied-access cases. In system tests, use waiting assertions for observable UI state instead of sleeps or immediate negative element lookups.

## Restore temporary state even when a test fails

Database rollback does not restore configuration, clocks, queues, environment variables, or external files. Keep ownership of temporary state visible and restoration exception-safe.

The application displays expiry in the current zone. This fixture expires at 12:00 UTC in January.

**Bad — an assertion failure skips restoration.**

```ruby
previous = Time.zone
Time.zone = "Pacific Time (US & Canada)"

assert_equal "04:00", export.expiration_label

Time.zone = previous
```

**Good — restoration survives failure.**

```ruby
previous = Time.zone

begin
  Time.zone = "Pacific Time (US & Canada)"
  assert_equal "04:00", export.expiration_label
ensure
  Time.zone = previous
end
```

**Great — an available scoped helper expresses the same lifetime.**

```ruby
Time.use_zone "Pacific Time (US & Canada)" do
  assert_equal "04:00", export.expiration_label
end
```

Use the receiver's actual scoped API; methods named `with` can have unrelated meanings. For ordinary public attributes, `Object#with` may replace an `ensure` when available. It restores assigned values without deep-copying them or isolating parallel threads. Keep the suite's established strategy for shared configuration.

Use doubles at unstable or external boundaries while retaining assertions about the tested behavior. Do not stub the operation the test claims to prove, or copy private framework test helpers into application tests for convenience.

## Finish with evidence

Let test names, setup, and assertions explain what happens. Remove narrative comments and redundant assertion messages. Keep comments only for necessary, established business rationale the code cannot communicate. Preserve required license notices and machine-interpreted directives.

Review the diff for lost cases, weakened expectations, hidden fixture dependencies, and changed execution boundaries. If an existing expectation conflicts with the implementation, investigate the contract; do not rewrite the expectation merely to make it pass.

For deleted or consolidated protection, identify the surviving check that rejects the original regression or plausible failure, or the authorized removal of the requirement. Compare conditions, execution boundaries, and assertions, not just covered lines. Reuse recorded regression evidence where applicable. If equivalence remains uncertain, keep the test and report the uncertainty; do not claim that a green suite or unchanged coverage proves safe deletion.

Run the affected tests and relevant lint checks. For materially strengthened assertions, verify that the plausible failure they target is rejected. Check a different execution order when shared-state changes create an isolation risk. Keep verification proportionate: broad suites, new dependencies, services, or a mutation-testing pipeline require separate authorization. Never weaken expectations, add retries, or skip failures to make the reduced suite pass.

Report the meaningful keep, consolidate, rewrite, delete, and add decisions briefly, with the behavior still protected, actual checks, and remaining uncertainty. When reporting size, count total added plus deleted lines, including helpers and documentation. Distinguish newly authored cases from existing tests rerun.
