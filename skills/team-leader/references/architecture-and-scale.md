# Architecture, Data, and Scale

Documented guidance for reasoning about system boundaries, data integrity, and behavior
under high request volume — the "hundreds of millions of requests" half of principal
judgment. Read this when a design touches data, capacity, or cross-component boundaries.

Back to `../SKILL.md`.

---

## 1. Boundaries and coupling

- Name the components, their responsibilities, and the seams between them. A good boundary
  makes change local: if a small feature forces edits across many modules, the boundary is
  wrong, not the feature.
- Depend on abstractions at the seams (SOLID's dependency inversion as a means, not
  ceremony). Concretely: a caller should depend on a stable contract, not on a concrete
  collaborator's internals, so either side can change independently.
- Prefer a **modular monolith with enforced boundaries** over premature distribution; a
  distributed system trades local complexity for network, consistency, and operational
  complexity. Distribution is a response to a measured need (independent scaling, team
  autonomy, fault isolation), not a default.

---

## 2. Data integrity before performance

Model the data and its invariants first; performance follows from a correct shape.

- State invariants as **constraints the database enforces** (nullability, uniqueness,
  foreign keys, checks), not as application hope — correctness must survive races and
  non-app writers. (See rails-engineer's `references/rails-concurrency-and-safety.md`.)
- Model cardinality and lifecycle honestly: what grows, what is retained, what is archived
  or deleted, and what the retention/compliance policy is.
- Decide the consistency requirement per operation: which reads must be strongly
  consistent (read-your-write) and which tolerate staleness.

---

## 3. Reason about scale explicitly (Little's Law and the throughput triangle)

The bridge between throughput, latency, and concurrency is **Little's Law**:

```
L = λ × W      concurrency = (requests/sec) × (avg latency in sec)
```

(source: [Little's Law — Wikipedia](https://en.wikipedia.org/wiki/Little%27s_law),
[INFORMS](https://pubsonline.informs.org/doi/abs/10.1287/opre.1110.0940?journalCode=opre))

Worked example: 2,000 req/s at 100 ms average latency ⇒ `L = 2000 × 0.1 = 200`
concurrent in-flight requests. Double the latency and you double the concurrency needed
for the same throughput.

**Caveats** (source: [INFORMS](https://pubsonline.informs.org/doi/abs/10.1287/opre.1110.0940?journalCode=opre)):

- Applies to a **stable system** on long-run averages. If arrival rate exceeds service
  capacity, queues grow and latency rises unboundedly — the system is not stable.
- Plan to **percentile latency** (p95/p99), not just the mean, and add headroom for
  burstiness and variance.

**Rule.** Before claiming a design scales, compute the concurrency and resource
(connection, worker, lock) requirement at the target request rate. This is the same
connection-pool math the rails-engineer request-critical-path section uses
(`references/jobs-runtime.md`).

---

## 4. Scale the right layer, in the right order

Fix the cheapest, highest-leverage bottleneck before scaling infrastructure (decision
order synthesized from [AWS RDS Proxy best practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy-best-practices.usage-scenarios.html),
[AWS read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_MultiAZDBCluster_ReadRepl.html),
[Azure Sharding pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/sharding),
[MongoDB scaling strategies](https://www.mongodb.com/docs/v8.0/core/sharding-scaling-strategies/)):

1. **Fix N+1 and query shape first** — multiplying queries per request masks whether the
   problem is the app or the database.
2. **Connection pooling / proxying** for high connection churn (many short-lived or bursty
   connections); reduces connection overhead.
3. **Read replicas** for read-heavy workloads — but replication is **asynchronous** and lag
   varies, so replicas are wrong for strongly consistent reads immediately after a write.
4. **Sharding / partitioning** only when a single database cannot handle data size or write
   throughput; it adds routing and cross-shard complexity, so it is a last resort.

Rule of thumb: high connection churn → pool; too many queries/request → fix N+1;
read-heavy → replica; single DB can't handle size/writes → shard.

---

## 5. Reliability: design for the failure, not the happy path

At scale, "unlikely" failures are certainties. Design each operation for its failure mode:

- **Timeouts and retries** on every network call, with **exponential backoff and jitter**;
  retries without idempotency and a bounded limit become a retry storm.
- **Idempotency** for any retried or replayed operation (webhooks, jobs, client retries) —
  enforce with a unique key / durable intent.
- **Backpressure and bounded queues** — an unbounded queue turns a slowdown into an outage;
  shed load deliberately.
- **Cascading failure** — a slow downstream must not exhaust your connections/threads;
  isolate with bulkheads (separate pools) and circuit breakers. (Source:
  [Addressing Cascading Failures — Google SRE](https://sre.google/sre-book/addressing-cascading-failures/).)

---

## 6. Observability is a design input

You cannot operate what you cannot see. Decide at design time, not after launch:

- What **metrics** prove the system is healthy (RED: rate, errors, duration; and the
  resource saturations behind them)?
- What **logs** are emitted, with secrets/PII redacted (see rails-engineer
  `references/rails-concurrency-and-safety.md#22`)?
- What **traces** connect a request across components so you can find the slow span?
- What **SLO** defines "good enough," and what error budget does it leave?

**Rule.** A design that cannot be observed, measured, and alerted on is not finished. Make
the SLO and the instrumentation part of the acceptance criteria.
