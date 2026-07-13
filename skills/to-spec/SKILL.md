---
name: to-spec
description: Synthesize an approved Plan artifact, its Grill critique/decision tree, user notes, conversation, and relevant codebase context into the final implementation specification. Use whenever Pi Prompt enters To Spec, or when the user asks to turn settled planning decisions into an agent-ready spec. Do not interview, publish issues, or implement; preserve references back to the source artifacts so ambiguity can be audited.
---

# To Spec

Turn the supplied planning record into an implementation specification. Synthesize what is already known; do not restart discovery or interview the user.

## Inputs and authority

Use these sources in descending authority:

1. The user's latest explicit decisions and notes.
2. The durable Plan artifact.
3. The Grill decision tree and generated critique annotations.
4. Earlier conversation context.
5. Narrow, relevant repository evidence when already available or explicitly authorized.

The Plan remains a durable artifact. The final spec must reference its plan/session ID, artifact path, and revision. It must also reference the decision-tree artifact so the implementing agent can inspect the reasoning when ambiguity remains.

Never silently resolve an open material decision. Record it under unresolved decisions with the available branches and consequences.

## Process

1. Read the Plan, Grill critique, decision tree, and all user-authored notes.
2. Resolve critique items that the user answered. Preserve unresolved material branches explicitly.
3. Prefer existing testing seams and the highest useful external-behavior seam. Avoid proliferating seams.
4. Produce the complete spec below.
5. Do not publish to an issue tracker, add labels, implement code, commit, push, or deploy. Pi Prompt owns review and final delivery to the current agent.

## Specification format

# [Specification title]

## Artifact References

- Plan session ID
- Plan artifact path and revision
- Grill decision-tree path and revision
- Any other durable inputs required to audit a decision

## Problem Statement

Describe the problem from the user's perspective.

## Solution

Describe the intended result from the user's perspective.

## User Stories

Provide a thorough numbered list using: `As a ..., I want ..., so that ...`.

## Implementation Decisions

Record modules or boundaries affected, interfaces/contracts, architectural decisions, schema or API decisions, interactions, failure behavior, and relevant ADR/glossary outcomes. Avoid brittle file paths and full code snippets unless a compact decision-rich prototype expresses a settled state machine or schema more precisely than prose.

## Testing Decisions

Describe externally observable behavior, selected test seams, modules/contracts requiring coverage, and relevant prior test patterns.

## Decision Trace

Summarize each material Grill branch, the chosen outcome and source of that choice, or its unresolved status. Reference the decision-tree artifact instead of duplicating every detail.

## Unresolved Decisions

List only ambiguities that could materially change implementation. Include alternatives and consequences. If none remain, say so explicitly.

## Out of Scope

State excluded work and boundaries.

## Acceptance Criteria

List observable conditions that make the implementation complete.

## Further Notes

Include remaining context useful to the implementing agent.

## Upstream attribution

Adapted for Pi from Matt Pocock's `to-spec` skill at commit `391a2701dd948f94f56a39f7533f8eea9a859c87`. This adaptation removes automatic issue-tracker publication and requires durable Plan/decision-tree references for Pi Prompt's reviewed workflow. See `UPSTREAM_LICENSE.md`.
