# Rails Concurrency, Data Integrity, and Input-Safety Reference

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Deep, concrete guidance for the highest-severity production defect classes. Read this
when a change touches money, inventory, uniqueness, deletion, bulk writes, time,
untrusted input, webhooks, outbound fetching, custom threads, or large-scale querying.
Each class gives the failure mode, a realistic example, and the expert rule.

This is the detailed companion to the one-liners in `SKILL.md`. Current as of Rails 8.1.

---

## 1. Transaction isolation and "a transaction is not serial execution"

**Failure mode.** Two concurrent transactions at the default PostgreSQL `READ COMMITTED`
both read a predicate ("9 of 10 seats taken"), both decide they can proceed, both insert,
and both commit. Each individual transaction was valid; together they oversell. This is a
phantom / write-skew anomaly, and wrapping code in `transaction` does not prevent it.

**Rule.** Identify the anomaly before reaching for `transaction`. Prefer, in order:
1. A **database constraint** (unique index, exclusion constraint, check) — correctness
   that survives every code path.
2. An **atomic conditional write** — one statement whose `WHERE` encodes the invariant
   (`UPDATE accounts SET balance = balance - 100 WHERE id = ? AND balance >= 100`) and a
   required affected-row count.
3. A **stronger isolation level** the adapter actually supports (`SERIALIZABLE` on
   PostgreSQL) with **bounded retries** for `ActiveRecord::SerializationFailure`.

Do not assume `transaction { ... }` serializes concurrent requests; it does not.

---

## 2. Deadlocks and lock ordering

**Failure mode.** Transfer A→B locks account 10 then 20; the reversal locks 20 then 10.
Each holds one lock and waits for the other. PostgreSQL aborts one with
`ActiveRecord::Deadlocked`; naive immediate retries cause a retry storm.

**Rule.** Acquire rows in one **globally deterministic order** (e.g. sort ids before
locking), lock only what you need, keep the transaction short, and retry
`ActiveRecord::Deadlocked` only at an idempotent outer boundary with a strict attempt
limit and jitter. Never hold a row lock across external I/O.

---

## 3. Optimistic vs pessimistic locking

- **Optimistic** (`lock_version` column): for *rare, human* edit conflicts. Two agents load
  the same record; the second save raises `ActiveRecord::StaleObjectError`. **Rule:**
  surface/reload/re-evaluate the stale object — do not blindly retry, because the
  underlying state changed materially.
- **Pessimistic** (`with_lock` / `.lock` / `SELECT ... FOR UPDATE`): for *short,
  high-contention* state transitions. **Rule:** keep the critical section tiny and never
  span a network call inside it.

---

## 4. Read-your-writes across replicas

**Failure mode.** A POST writes to the primary and redirects to a GET that the router sends
to a lagging replica; the GET 404s, the user retries, and a duplicate record is created.

**Rule.** Any correctness-dependent post-write read must stay on the writer — explicit
`connected_to(role: :writing)` or verified writer-stickiness (e.g. the
`DatabaseSelector`/session delay) — until the replication window is safe. Treat
`:reading` connections as **stale by design**. See
`references/database-patterns.md` for replica config.

---

## 5. Atomic creation: `find_or_create_by` is not atomic

**Failure mode.** Two webhook workers run `find_or_create_by(provider_event_id:)` with no
unique index; both find nothing, both insert, and the account is credited twice.

**Rule.** Back every dedup key with a **unique constraint** and choose the atomic API
deliberately:
- `create_or_find_by(unique_key:)` — tries the insert, rescues `RecordNotUnique`, returns
  the existing row. (Rails implements `find_or_create_by` as `find_by || create_or_find_by`,
  so the plain form still has a read-then-create window when the unique constraint is the
  only guard.)
- `upsert_all(rows, unique_by: ..., on_duplicate: ..., update_only: ...)` for bulk
  idempotent writes. **There is no `on_conflict:` Ruby keyword** — that is the underlying
  SQL; the Rails API is `unique_by`/`on_duplicate`/`update_only`. Bulk upserts skip
  validations/callbacks, so enumerate required defaults/timestamps first.

---

## 6. Money representation

**Failure mode.** `19.99 * 100` in binary `Float` rounds differently at different pipeline
stages; invoice lines slowly diverge from gateway and ledger totals by cents, at scale.

**Rule.** Represent currency as **integer minor units** (cents) or a database
`decimal`/Ruby `BigDecimal`. Define **one** domain rounding mode and **one** rounding
stage. Never introduce `Float` into currency arithmetic, comparison, or storage.

---

## 7. Counter caches and atomic counters

**Failure mode.** A cleanup runs `Comment.where(...).delete_all`; child destroy callbacks
never run, so `posts.comments_count` stays inflated and quota/ranking logic goes wrong.

**Rule.** Treat counter caches as **denormalized data**. Use atomic counter SQL
(`update_counters`, which issues one `UPDATE ... SET col = COALESCE(col,0) + n`) but
remember it **bypasses validations/callbacks/timestamps**. Ensure every create/delete path
maintains the counter, and provide an observable, concurrency-safe reconciliation
(`reset_counters`) run deliberately, not casually on a hot path.

---

## 8. Deletion semantics: `delete` vs `destroy` and `dependent:`

**Failure mode.** `Account.where(id:).delete_all` skips `dependent:` and cleanup callbacks,
leaving orphans; swapping to `destroy_all` over 10M children holds connections/locks for
hours.

**Rule.** Choose explicitly:
- `delete` / `delete_all` — SQL only, **no callbacks, no `dependent:` work**.
- `destroy` / `destroy_all` — instantiates and runs callbacks per row (slow at scale).
- Large cascades belong in **database constraints** (`ON DELETE CASCADE`) or bounded,
  resumable operational choreography — never a request-time loop.

---

## 9. Time zones, DST, and temporal boundaries

**Failure mode.** A billing cutoff built on `Time.now.beginning_of_day` runs in server UTC
instead of the account zone; on a DST transition it charges/expires early or late, and an
inclusive end range double-counts the boundary.

**Rule.** Use `Time.current`/`Time.zone` and `Date.current` for business time; persist
instants in UTC; model date-only values as `date`, not `datetime`; derive zone-aware
**half-open ranges** (`start...finish`) so boundaries are never double-counted; test both
DST gaps (spring forward) and folds (fall back).

---

## 10. Batching and large-relation memory

**Failure mode.** A backfill calls `order(:created_at).find_each`, unaware the scoped order
is ignored; a mutable or non-unique cursor skips/repeats rows under concurrent writes.

**Rule.** For large relations, project only needed columns (`pluck`/`select`) and batch
with a **static, unique cursor** (default primary key, ascending). Know that `find_each`
**ignores scoped order** (and honors limits), `in_batches` yields **unloaded** relations by
default (`load: false`), and concurrent mutation can skip/duplicate work — for correctness-
critical sweeps, snapshot or reconcile.

---

## 11. Exact counts/aggregates on huge tables

**Failure mode.** Every page render does `events.count` over hundreds of millions of rows
to show a total; traffic saturates DB CPU and the app falls over.

**Rule.** Never put an unbounded exact `COUNT`/`SUM` on a hot path without plan-and-latency
proof. Use bounded/cached/pre-aggregated counters, or explicitly approximate
database-specific estimates (e.g. PostgreSQL `reltuples`) when exactness is not a product
requirement. See `references/database-patterns.md#efficient-counting`.

---

## 12. N+1 outside controllers

**Failure mode.** A serializer calls `order.customer.plan` and `order.line_items.sum` for
5,000 orders; the controller looks fine but rendering emits 10,001 queries and exhausts the
pool.

**Rule.** Trace SQL through the **entire render/job path** — serializers, views, helpers,
batch jobs — not just the controller. Preload the exact graph used, and enable
`strict_loading` on critical boundaries (or in focused tests) to make lazy loads raise.

---

## 13. Single-record update APIs that bypass invariants

**Failure mode.** A repair path calls `user.update_columns(role: "admin")`, skipping audit
and normalization callbacks; the privilege change is invisible to monitoring.

**Rule.** Know the exact bypass semantics (Rails 8.1):
- `update_all`, `update_column(s)` — **skip validations AND callbacks** (timestamps only
  via `touch:` where supported). Direct writes.
- `update_attribute` — **skips validations but RUNS callbacks and timestamps**, and saves
  *all* dirty attributes. Different animal; do not confuse it with `update_column`.

---

## 14. Serialization allowlists and PII leaks

**Failure mode.** `render json: user` was safe until a migration added `tax_id` or an
internal risk flag; default model serialization now leaks it to every client.

**Rule.** Never serialize sensitive AR objects implicitly. Use an explicit serializer /
Jbuilder shape with an **output allowlist** (`only:`, not an `except:` denylist), and
regression-test both the exposed fields and the authorization context.

---

## 15. Strong params: deep-open and nested mass assignment

**Failure mode.** `params.require(:user).permit!` or `settings: {}` accepts a newly added
nested `role`, `account_id`, or `credit_limit` — privilege escalation with no controller
change.

**Rule.** Allowlist scalar and nested leaves **per action**; never call `permit!` on
untrusted input; never permit ownership/role fields just because the model accepts them.
`params.expect` validates **shape, not authorization**.

---

## 16. Webhook authenticity, replay, and idempotency

**Failure mode.** An attacker posts a forged `payment_succeeded`, or replays a captured
one, and the app credits an account repeatedly.

**Rule.** Verify the provider **signature over the raw body** plus its **timestamp/replay
window** *before* parsing or acting; persist a uniquely-constrained provider event ID; make
the resulting state transition transactionally idempotent. Treat the webhook payload as
untrusted until the signature check passes.

---

## 17. SSRF and unsafe server-side URL fetching

**Failure mode.** An "import avatar from URL" feature follows a redirect to
`169.254.169.254` (cloud metadata) or an internal admin host, leaking credentials.

**Rule.** Do not fetch arbitrary user URLs. If unavoidable, allowlist scheme/host/port,
resolve the host and block private/link-local/reserved ranges **on every redirect**,
disable unsafe protocols, and enforce strict size/time limits at the egress boundary.

---

## 18. Unsafe deserialization

**Failure mode.** `Marshal.load(Base64.decode64(params[:data]))` or unsafe `YAML.load` on
attacker-influenced bytes constructs arbitrary objects — potential remote code execution.

**Rule.** Never `Marshal.load` or unsafely YAML-load untrusted bytes. Prefer JSON plus an
explicit primitive schema. If YAML is unavoidable, use `YAML.safe_load` / a minimal
permitted-class list **after** authenticating the payload.

---

## 19. Atomic state transitions (no lost updates, no double effects)

**Failure mode.** Two workers both read `order.pending?`, both charge the card, both set
`paid` — the DB looks consistent but the customer was charged twice.

**Rule.** Claim the state with **one conditional write** (`UPDATE orders SET state =
'processing' WHERE id = ? AND state = 'pending'`) and require **exactly one** affected row;
the loser backs off. Drive the external effect through an idempotency key / durable intent,
and never hold the DB lock across the network call.

---

## 20. Connection ownership, custom threads, and pool exhaustion

**Failure mode.** A job spawns 20 raw threads; each touches AR and holds a connection while
waiting on HTTP. The 10-connection pool is exhausted and unrelated requests time out.
Sharing one connection across threads is also unsafe.

**Rule.** Prefer Rails-managed concurrency (jobs, `load_async`). In custom threads use the
Rails executor and `connection_pool.with_connection`; never share a connection, never
manually `checkout` without a guaranteed `checkin`, and size each role/shard pool to the
process's total concurrency.

---

## 21. Unbounded input / query complexity (application-layer DoS)

**Failure mode.** A public endpoint accepts 500,000 ids or `per_page=1000000`, producing
huge SQL, bind lists, allocations, and serialized output; modest traffic takes down the
fleet.

**Rule.** Bound array size, nesting depth, page size, export scope, regex/input length, and
upload expansion **at the boundary**. Rate limiting does not replace per-request resource
limits.

---

## 22. Sensitive data in logs

**Failure mode.** Password-reset tokens, bearer headers, webhook secrets, or job arguments
land in centralized logs — account-takeover material for anyone with log access.

**Rule.** Configure and test `config.filter_parameters`, redact sensitive headers and job
arguments, and log explicit safe fields rather than raw params, payloads, records, or
credentials.

---

## Cross-cutting security boundary checklist

- Authorization scope belongs in the relation that fetches the record. Post-fetch checks are often too late.
- `Current.user`, `Current.account`, signed IDs, UUIDs, slugs, and friendly IDs are not authorization.
- Check unauthenticated, authenticated-but-unauthorized, cross-tenant/account, role downgrade, and admin escape-hatch paths for sensitive changes.
- Jobs, mailers, cache keys, broadcasts, blobs, and background tasks need tenant/account/permission dimensions too.
- XSS bypasses CSRF. Rely on Rails escaping, sanitize user HTML with allowlists, and avoid unsafe rendering.
- Preserve CSRF for forms, Turbo, and custom JS.
- Reset session on login for auth/session flows.
- Use signed/encrypted tokens for tamper-sensitive values, but still authorize access.
- Validate redirect targets to prevent open redirects.
- For regex validation of whole strings, use `\A` and `\z`, not line anchors.
- Validate uploads by size, content type, access rules, storage visibility, and processing safety.
- Store secrets in encrypted credentials or approved secret stores. Never hardcode secrets.
- Consider throttling/rate limiting for login, password reset, invite, public write, webhook, and abuse-prone endpoints when supported by the installed Rails/app stack.
- Allowlist scalar and nested leaves per action; never `permit!` on untrusted input; never permit ownership/role fields just because the model accepts them. `params.expect` validates shape, not authorization.
- Never serialize sensitive records implicitly (`render json: user` leaks any column a later migration adds). Use an explicit serializer with an output allowlist (`only:`, not `except:`).
- Verify webhook provider signatures over the raw body plus timestamp/replay window before acting; persist a uniquely-constrained provider event id; make the transition idempotent.
- Do not fetch arbitrary user URLs (SSRF): allowlist scheme/host/port, block private/link-local ranges on every redirect, cap size/time. Never `Marshal.load` or unsafe-`YAML.load` untrusted bytes (RCE); prefer JSON.
- Bound input/query complexity at the boundary (array size, page size, nesting, export scope); rate limits do not replace per-request resource limits.
- Keep secrets, tokens, and PII out of logs: configure `config.filter_parameters`, redact headers/job args, log safe explicit fields.
- For depth on these and atomic state transitions, use the numbered defect classes above.
