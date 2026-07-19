# Rails Debugging and Verification Playbooks

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference when diagnosing a concrete Rails failure or choosing focused verification for an implementation change.

## Request/Controller Bug

1. Confirm route, verb, format, params, controller/action, middleware/session assumptions.
2. Trace before actions, auth, tenant scope, record loading, mutation, response path, and status/flash/redirect/Turbo/JSON behavior.
3. Inspect views/partials/helpers/locals and validation failure paths.
4. Reproduce with the narrowest request/integration/system path available.

## Active Record/Data Bug

1. Inspect schema, constraints, indexes, associations, validations, callbacks, scopes, default scopes, enum/state columns, and relevant migrations.
2. Reproduce the relation and emitted SQL.
3. Check NULL semantics, time zones, ordering, duplicated rows from joins, `distinct`, eager loading, partial selects, and transactions.
4. Verify database constraints for invariants the app relies on. For performance, use logs and query plans.

## Ruby/Autoloading Bug

1. Identify receiver, `self`, method owner, ancestors, visibility, and `source_location` where possible.
2. Check constant name, file path, namespace, autoloading, reloadability, and initializer timing.
3. Inspect mixins/prepends/concerns/callback registration and generated methods.
4. Avoid load-order guesses; use Zeitwerk checks or constant source inspection when allowed.

## Hotwire Bug

1. Determine whether the contract is navigation, frame replacement, stream response, broadcast, or Stimulus behavior.
2. Check request headers/format, response status, content type, frame ID, stream target, DOM ID, redirect behavior, and generated HTML.
3. For broadcasts, inspect callback/job timing, stream subscription, tenant scope, and adapter config.

## Job/Mailer/Async Bug

1. Confirm what enqueues work and whether it happens after commit.
2. Inspect adapter config, queue names, priority, retries/discards, serialization, and arguments.
3. Check idempotency, duplicate execution, missing records, process death, and partial side effects.
4. Separate enqueueing contract from performed-work contract.

## Testing Coordination and Verification

Implementation work should leave evidence, not just a plausible patch.

- If changing behavior and scope permits edits, add or update the smallest focused regression test in the layer that proves the behavior. Read existing test helpers, fixtures/factories, and nearby tests first.
- If the task is broad testing strategy, fixture-heavy suite design, flaky-test triage, or primarily about test performance, coordinate with `test-expert`. When assigned Rails implementation, still read/write focused Rails-native tests and verification details within scope.
- Use the app's existing test stack. Do not introduce RSpec, FactoryBot, browser drivers, testing gems, or JS packages without approval.
- Prefer behavior-visible tests over private-method or internal-call assertions.
- For security-sensitive changes, cover unauthenticated, unauthorized, cross-tenant/account, role boundary, unsafe params, CSRF/open redirect/upload/token paths as relevant.
- If tests are out of scope, too expensive, blocked by services, or not run, state exactly why and what risk remains.

### Verification examples, narrow first

- Route/helper shape: `bin/rails routes`.
- Model/domain/query: targeted model test or relation/SQL inspection through tests/logs.
- Controller/API/Turbo response: targeted integration/request test.
- Browser-only Stimulus/Capybara behavior: targeted system test.
- Job/mailer: targeted job/mailer test and queue/mail assertions.
- Migration status: `bin/rails db:migrate:status`; migration-specific checks when the project has them.
- Performance/query/index claim: emitted SQL plus EXPLAIN/ANALYZE where safe.
- Ruby/autoloading claim: method owner/source, ancestors, constant source, Zeitwerk check where appropriate.
- Broad regression: `bin/rails test`, `bin/rails test:all`, `bin/ci`, or project-specific CI only when risk/scope warrants it or the user asks.

Report exact commands, results, failures, skipped verification, and why broader verification was not run.
