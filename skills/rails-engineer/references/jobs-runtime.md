# Rails Jobs and Runtime Reference

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference when work touches request critical paths, deferred side effects, jobs, mailers, cache, cable, storage, credentials, instrumentation, or production runtime behavior.

## Request Critical Path and Deferred Work

A Rails master treats every request as a budget of scarce resources — round trips, wall clock, DB connections, locks — and designs the critical path to spend as little of each as possible. Query count is only the visible symptom; the real units are below. Reach for this analysis by default on any endpoint that does non-trivial work, and prove it with measurement, not intuition.

### Critical path vs. deferred

- Define the critical path from what the *response* and *data integrity* require, not from where code happens to run. If the response is `{ account_id, user_id }`, only the work that must be committed to return those IDs correctly belongs in the request transaction. Everything slow, external, retryable, or unrelated to the response moves behind a job.
- Never perform network I/O inside a request transaction. A transaction held open across an external API/SMTP/search call blocks a DB connection and its locks for the entire round trip, turning a 5ms local commit into a 1.5s connection-hog. External calls belong after commit, in a job.
- For work that must happen but not now, enqueue after commit — and know that after-commit enqueue still has a gap (the process can die after commit, before publish). Close it with a durable intent/outbox row written in the same transaction, then dispatched after commit and reconciled later. Do not rely on a callback firing at the right moment.
- Move work off the request, but do not pretend it vanished. Count the deferred work separately and bound its concurrency (provider rate limits, DB/queue pools, worker capacity). Moving work is not permission to create an unbounded queue.

### Measure the real resources

- **Round trips.** Count each SQL statement, each external HTTP call, each cache operation as a trip. Distinguish app↔DB trips from app↔external trips. Know where a bulk statement (`insert_all`, `upsert_all`, `write_multi`) collapses N trips into 1 — that is the difference between 40 INSERTs and 1.
- **Wall clock, decomposed.** Split request latency into time-in-SQL, time-in-external-HTTP, time-in-cache, and time-in-app-CPU. A 1.5s request that is 10ms of SQL and 1.4s of external HTTP is an I/O-placement bug, not a database problem.
- **DB connections and pool pressure.** A request checks out a connection for as long as its transaction is open. Model connection-hold-time, not just request latency: at R requests/sec with a connection held H seconds, you need ~R×H concurrent connections (Little's Law). Holding one connection across 1.5s and 9 external calls at 5 signups/sec needs ~8 connections for that endpoint alone; holding it for 5ms of pure SQL needs a tiny fraction of one. Pool exhaustion under load is how endpoints start returning 5xx.
- **Transaction duration and lock exposure.** Know which rows/locks are held and for how long. Shorten the critical section: do the minimum local, atomic work inside the transaction and nothing else.

### HTTP and side effects in callbacks

- An HTTP call (or any external side effect) inside an Active Record callback is a defect, and inside `after_create` it is worse than a stylistic smell: the record is not committed yet, so the call runs inside the transaction (holding the connection), fires even if the transaction later rolls back (ghost email/webhook/analytics), and cannot be safely retried. Use `after_create_commit` / `after_commit` for anything that must observe committed data — and prefer enqueueing a job over doing the I/O inline even there.
- Callbacks that hide product workflows — network calls, mail, payments, many jobs, persistence of unrelated records — are a structural smell regardless of timing. If saving a record sends mail, hits an API, or writes 30 unrelated rows, that behavior belongs in an explicit domain method the caller can see, not in a persistence callback. See "Concerns, Callbacks, and Deviations" in `SKILL.md`.
- Prefer `deliver_later` for mail in request paths; `deliver_now` inside a request is an external HTTP call on the critical path.

## Jobs, Mailers, Cache, Cable, Storage, and Runtime

### Jobs and Solid Queue

- Jobs must be idempotent under retries, duplicate enqueues, process death, deploy interruption, and partial completion.
- Choose `retry_on`/`discard_on` by error class and business semantics. Do not blanket-retry permanent failures.
- GlobalID arguments can fail deserialization when records disappear. Handle intentionally.
- Enqueue after commit when the job observes committed records.
- If Solid Queue is present, inspect `config/queue.yml`, queue DB, supervisor/worker/dispatcher topology, queue order, priority, concurrency controls, recurring tasks, failed-job tooling, and DB pool impact.
- In Solid Queue, queue order can dominate priority. Wildcard queues can have performance cost. Version-gate continuations and other new APIs.
- Bulk enqueue APIs may skip per-job enqueue callbacks. Verify instrumentation and callback semantics.

### Mail, Cache, Cable, Storage

- Mailers need full URLs (`*_url`) with configured `default_url_options`; paths are usually wrong in email. Use previews as verification.
- Use `deliver_later` for request latency when a worker is running; `deliver_now` can be right for scripts/tasks.
- Cache primitives, IDs, or rendered fragments; avoid caching Active Record instances.
- Cache keys must include tenant/account/user/permission/locale/feature-flag dimensions when content differs.
- Prefer fixing query/data shape before caching. Low-level `Rails.cache.fetch` needs invalidation, expiration, and stampede thinking.
- Authenticate Action Cable connections; authorize subscriptions/actions. Stream names must encode tenant/account/permission boundaries.
- Broadcasts are online-only and not durable. Use DB records/jobs for durable notifications.
- Active Storage default routes use signed URLs that may be effectively permanent. Sensitive files need authenticated controllers and possibly disabled default routes.
- Inspect storage service config, credentials, CORS, bucket permissions, timeouts, retries, and environment separation before claiming behavior.
- User-controlled transformations are unsafe. Prefer named variants. Direct uploads can leave unattached blobs.

### Credentials, Instrumentation, and Production Evidence

- Credentials live in encrypted files; master keys must not be committed. Use bang accessors when missing secrets should fail fast.
- Rotating `secret_key_base` can invalidate sessions/cookies and affect signed/encrypted data.
- Use Rails logs, request IDs, tagged logging, query logs, app error reporting, and `ActiveSupport::Notifications` before claiming production behavior.
- Use `Rails.error` APIs where supported. Know whether a call reports-and-swallows, reports-and-reraises, or behaves differently by environment.
- Production claims require observed logs, metrics, traces, queue/cache/cable/storage state, or runtime config.
