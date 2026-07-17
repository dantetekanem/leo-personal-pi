---
name: to-spec
description: Synthesize an approved Plan, its Adversarial Review decision tree and findings, and user-authored notes into a direct implementation specification. Use whenever Pi Prompt enters To Spec, or when the user asks to turn settled planning decisions into an agent-ready handoff. Keep the Spec bounded, reference the durable source artifacts, require observable pass/fail acceptance criteria, and do not interview, rediscover, publish, or implement.
---

# To Spec

Turn the supplied planning record into a concise implementation handoff. Synthesize only what is already settled; do not restart discovery, restate the Plan, or invent detail.

## Source boundary and authority

Use only the exact durable inputs supplied by Pi Prompt, in this order:

1. The user's explicit decisions and selected notes.
2. The durable Plan artifact.
3. The Adversarial Review decision tree and generated findings.
4. The existing Spec only when revising it.

The final Spec must reference the Plan session ID, artifact path, and revision, plus the Adversarial Review artifact path, pointer, and revision. References make the reasoning auditable; they are not permission to copy the source documents into the Spec.

Never inspect unrelated repository content, draw from ambient conversation, introduce a requirement absent from the approved sources, or silently resolve an open material decision. When sources conflict, follow the latest explicit user decision and record any remaining material conflict under unresolved decisions.

## Directness rules

- Write the shortest Spec that gives an implementing agent an unambiguous completion contract.
- Do not repeat Plan background, task lists, rationale, findings, or decision-tree branches. Reference them.
- Include only decisions that materially constrain implementation.
- Prefer compact bullets over narrative prose.
- Do not add User Stories, a Further Notes section, speculative improvements, optional enhancements, or generic best practices.
- Keep Out of Scope explicit so implementation cannot silently expand.
- Omit empty detail; only `Unresolved Decisions` may say `None` when there are no material open branches.

## Process

1. Read the supplied Plan, annotations, Adversarial Review artifact, and selected Spec comments when revising.
2. Apply answered findings and preserve unresolved material branches without choosing for the user.
3. Select the smallest useful external-behavior testing seams already supported by the sources.
4. Produce exactly the direct Spec structure below.
5. Do not publish issues, implement code, modify source artifacts, commit, push, deploy, install, or start services.

## Required Spec structure

```markdown
# [Specification title]

## Artifact References
- Plan: [session ID, artifact path, document revision/state]
- Adversarial Review: [artifact path, decision-tree pointer, based-on revision/state]

## Intended Outcome
[One concise paragraph describing the observable result.]

## Implementation Decisions
- [Only settled boundaries, contracts, interactions, data/API decisions, and material failure behavior.]

## Testing Approach
- [Externally observable seams and essential coverage implied by the approved sources.]

## Unresolved Decisions
- [Only open choices that could materially change implementation, with alternatives and consequences; otherwise `None`.]

## Out of Scope
- [Explicit exclusions and boundaries.]

## Acceptance Criteria
1. [Binary, independently observable pass/fail condition.]
```

## Acceptance-criteria quality gate

Every acceptance criterion must:

- describe an externally observable result or a verifiable contract;
- be independently pass/fail, without words such as `appropriate`, `properly`, `works`, or `handles` unless the exact observable result follows;
- trace to the approved Plan outcome or a settled Adversarial Review decision;
- identify the relevant failure, denied, empty, retry, or rollback behavior when that behavior is material;
- avoid prescribing implementation details unless the source artifacts already settled them.

Remove criteria that merely say a file exists, a library is installed, tests pass in general, or code is clean. Acceptance proves the requested outcome, not implementation activity.

## Upstream attribution

Adapted for Pi from Matt Pocock's `to-spec` skill at commit `391a2701dd948f94f56a39f7533f8eea9a859c87`. This adaptation removes automatic issue-tracker publication and requires a direct, source-bounded Spec with durable Plan/Adversarial Review references and observable acceptance criteria. See `UPSTREAM_LICENSE.md`.
