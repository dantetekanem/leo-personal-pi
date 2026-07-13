---
name: grill-with-docs
description: Relentlessly critique and sharpen an existing plan while preserving it as the primary artifact. Use whenever Pi Prompt enters its Grill stage, or when the user asks to grill, pressure-test, challenge, red-team, or annotate a plan/design. Produce concrete critique notes, decisions, ADR candidates, glossary terms, and a decision tree without rewriting or implementing the plan.
---

# Grill With Docs

Treat the supplied Plan as immutable source material. Your job is to expose ambiguity and risk, not to replace the Plan or start implementation.

## Process

1. Read the complete Plan and any existing user notes.
2. Challenge assumptions, boundaries, dependencies, failure modes, data ownership, security, operability, testing seams, rollout, and acceptance criteria only where relevant.
3. Prefer a small number of high-value findings over generic review commentary.
4. Attach every finding to the narrowest relevant Plan range or element. Use a plan-level finding only when no narrower target is honest.
5. Classify each finding as one of:
   - `risk`
   - `ambiguity`
   - `missing-decision`
   - `contradiction`
   - `test-gap`
   - `adr-candidate`
   - `glossary`
6. For an ambiguity that could materially change implementation, add a decision node with concrete alternatives and consequences. Do not invent a decision when the existing Plan or conversation already resolves it.
7. Preserve user-authored notes exactly. Generated critique is separate evidence and must remain distinguishable from user feedback.
8. Do not inspect unrelated files, implement code, publish issues, commit, push, deploy, or broaden scope.

## Output contract

Return structured critique annotations plus a compact decision tree. Each critique annotation needs:

- a stable local identifier;
- its classification;
- the exact Plan target or range;
- concise but actionable body text;
- optional alternatives and consequences when a decision is genuinely open.

The decision tree should include only material branches:

- question or ambiguity;
- known context;
- viable options;
- trade-offs;
- chosen answer when already decided;
- unresolved status when user input is still required.

The Pi Prompt browser renders generated critique in very light red and user-authored notes in light yellow. Never encode presentation colors into the content itself.

## Documentation outcomes

Capture ADR candidates and glossary terms as Grill findings so To Spec can synthesize them. Do not create or modify repository documentation unless the user separately authorizes that side effect.

## Upstream attribution

Adapted for Pi from Matt Pocock's `grill-with-docs` skill at commit `391a2701dd948f94f56a39f7533f8eea9a859c87`. The upstream wrapper delegates to `/grilling` and `/domain-modeling`; this standalone adaptation incorporates the needed behavior directly. See `UPSTREAM_LICENSE.md`.
