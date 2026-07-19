# Principal Engineering Judgment

Deep, documented guidance for the judgment pillar of the team-leader skill. Read this
when a task involves architecture, design trade-offs, scale, technical strategy, or any
decision whose cost of being wrong is high. Each class gives the principle, the reasoning,
and the documented source.

Back to `../SKILL.md`.

---

## 1. How staff/principal engineers operate

Principal-level impact comes from leverage, not personal output. The four documented
Staff-plus archetypes describe the modes (source: [Staff archetypes — StaffEng](https://staffeng.com/guides/staff-archetypes/)):

- **Tech Lead** — guides the approach and execution of one team or a cluster.
- **Architect** — owns direction, quality, and approach within a critical, enduring domain,
  grounded in an intimate understanding of business needs, user goals, and technical
  constraints (not designing in isolation).
- **Solver** — digs deep into arbitrarily complex, high-execution-risk problems.
- **Right Hand** — extends an executive's scope and authority in large organizations.

The common operating model (source: [Operating at Staff — StaffEng](https://staffeng.com/guides/operating-at-staff/),
[What do Staff engineers actually do?](https://staffeng.com/guides/what-do-staff-engineers-actually-do/)):

- **Own an important problem space**, not a backlog of tickets.
- **Translate business goals into engineering strategy** — architecture, technology choices.
- **Influence through alignment and technical direction**, not authority.
- **Scale others** by delegating, unblocking, and shaping execution.
- Apply **systems thinking**: see the whole system and its feedback loops, not just the
  component you are editing (source: [Systems thinking — StaffEng](https://staffeng.com/guides/systems-thinking/)).

**Rule.** Match the operating mode to the problem. Measure your impact by the leverage you
create and the problems that stop recurring, not by lines of code or agents spawned.

---

## 2. Extend software toward its local maximum

A local maximum is the best design reachable from the current system without a rewrite:
the architecture, boundaries, and data model that satisfy today's real requirements plus
scale headroom with the least accidental complexity, and that keep the obvious next steps
cheap.

- Distinguish **essential complexity** (the domain requires it) from **accidental
  complexity** (history, copy-paste, premature abstraction). Extend the former; delete the
  latter. (Concept from "No Silver Bullet," Brooks, 1986.)
- Prefer **deepening a good existing structure** over bolting on a parallel one. Ask:
  "what would this look like if it were designed well for its actual job?" and move toward
  that incrementally.
- Recognize when the local maximum is **exhausted** — when the next requirement cannot be
  met without structural change — and say so with evidence instead of piling a workaround
  onto a spent design.

---

## 3. Decide with documented trade-offs (design docs / ADRs)

For ambiguous or contentious designs, decide in writing. The point is not documentation for
its own sake; it is finding issues while change is still cheap and forcing the trade-offs
into the open.

Design-doc structure (source: [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)):

- **Context and scope** — objective facts only.
- **Goals and non-goals** — non-goals are things that *could* be goals but are explicitly
  excluded (e.g. "ACID compliance"), not negated goals like "shouldn't crash."
- **The design** — the trade-offs you made, and why this option best satisfies the goals.
- **Alternatives considered** — often the most valuable section; shows why the rejected
  options' trade-offs are less desirable.
- **Cross-cutting concerns** — security, privacy, observability, always considered.

When a full doc is overhead, an **Architecture Decision Record** captures a single
significant decision: context, options, decision, consequences (source:
[Architecture Decision Records — Martin Fowler](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html),
[adr.github.io](https://adr.github.io/)). List the **serious alternatives with pros and
cons** and the **trade-offs** behind the choice.

**Rule.** Write a design doc when the solution is ambiguous or contentious and the cost of
being wrong is high; write an ADR for a single consequential decision. If a "design doc"
contains no trade-offs or alternatives, the design was obvious — just build it.

---

## 4. Work backwards from the customer / outcome

Before designing, force clarity about what you are actually building and for whom. Amazon's
Working Backwards process (source: [Working Backwards — Werner Vogels](https://www.allthingsdistributed.com/2006/11/working_backwards.html)):

1. Write the **press release** — what the thing does and why it exists, in plain language.
2. Write the **FAQ** — the questions that surface the real scope.
3. Define the **customer experience** — precise use cases.
4. Write the **user manual**.

**Rule.** Start from the outcome and the customer, and work back to the minimum technology
that satisfies it. If you cannot write the one-paragraph "press release," you do not yet
understand the problem — and that gap will surface later as scope creep and rework.

---

## 5. Ask the other whys and find what's missing

The highest-leverage principal contributions are the questions nobody else asked. Before
committing to a design, interrogate it:

- Why this requirement, and what is it actually for? What breaks if we don't build it?
- What is the **failure mode**? Retry, partial failure, concurrent access, process death,
  bad input, a slow or down downstream?
- What is **missing**: authorization, tenancy, idempotency, observability, rollback, data
  retention, a migration path, the error state, the empty state, the second region?
- What does this **couple to**, and what does it make expensive later? What are we
  implicitly promising callers?

**Rule.** Enumerate the hard cases and decide each deliberately. Do not leave gaps to be
discovered in production. Surfacing hidden complexity and naming trade-offs explicitly is
the job, not a distraction from it.

---

## 6. Choose work that matters

Senior time is the scarcest resource; spend it where it moves the outcome (source:
[Work on what matters — StaffEng](https://staffeng.com/guides/work-on-what-matters)):

- **Avoid snacking** (easy, low-impact work), **preening** (low-impact, high-visibility),
  and **chasing ghosts** (re-fighting your last company's battles in a new context).
- **Swarm existential issues**; otherwise work where there is room and attention, where you
  can do great work ahead of time.
- **Edit** — small, well-placed changes and conversations that shift a project's outcome.
- **Finish things** — value is realized only when work crosses the finish line.
- Do **what only you can do** — the intersection of what you are best at and what won't
  happen without you.

**Rule.** Track honestly how much of your effort is high-impact versus low-impact. Delegating
work that merely offloads effort, or spawning agents to inflate activity, is snacking at
the orchestration layer.

---

## 7. Learn from failure, blamelessly

Incidents are inevitable at scale; the discipline is learning from them so they do not
recur (source: [Postmortem Culture — Google SRE](https://sre.google/sre-book/postmortem-culture/),
[Blameless postmortems — Google SRE Workbook](https://sre.google/workbook/postmortem-culture/)):

- Focus on **what failed in the system and process**, not who to blame.
- Find the **root cause(s) and contributing factors**, not just the triggering event.
- Produce **action items** that are specific, preventative/mitigative, measurable, owned,
  and tracked to completion.

**Rule.** Every material failure gets a blameless review with root causes and tracked
actions. An action item without an owner and a measurable done-state will not get done.
