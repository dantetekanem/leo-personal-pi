---
name: adversarial-review
description: Adversarially review and sharpen an existing plan while preserving it as the immutable primary artifact. Use whenever Pi Prompt enters Adversarial Review, or when the user asks to pressure-test, challenge, red-team, audit, or annotate a plan or design. Produce a bounded set of material, evidence-backed findings plus a compact decision tree without rewriting or implementing the plan.
---

# Adversarial Review

Treat the supplied Plan as immutable source material. Expose material gaps between its intended outcome and its executable tasks; do not replace the Plan or start implementation.

## Inputs and invariants

- Read the complete Plan and any supplied user-authored notes.
- When Pi Prompt supplies a canonical public anchor map, use only its document and element IDs. Attach every finding to the narrowest honest Plan range or element; use a plan-level target only when no narrower target is accurate.
- Preserve user-authored notes exactly. Generated findings are separate, immutable evidence and must remain distinguishable from user feedback.
- The Plan and supplied context are authoritative. Do not invent requirements, reopen resolved decisions, or treat ambient repository content as scope.

## Bounded goal-backward gates

Apply these gates in order, then retain at most eight material, evidence-backed findings:

1. **Observable outcome truths:** Derive concise statements that must be observably true for the Plan's intended outcome to be achieved. Derive them from the Plan; do not add product goals.
2. **Substantive coverage:** Check that each truth has substantive planned artifacts or actions, not merely names, placeholders, setup, or stubs.
3. **Critical wiring:** Check that the Plan explicitly connects the relevant artifacts and actions end to end. Creating pieces without planning how data, control, ownership, or user flow connects them is incomplete.
4. **Task quality:** Check task atomicity, completeness, concrete actionability, acceptance criteria, and ordering after real dependencies.
5. **Integrity and confidence:** Detect silent scope reduction or expansion, contradictions, vague or unverifiable acceptance, and missing relevant failure, rollback, operability, or test coverage.
6. **Decision and context compliance:** Detect conflicts with decisions, constraints, definitions, or deferred scope already stated in the Plan or supplied context.

Prefer no finding over generic commentary. Do not report style preferences, praise, low-impact speculation, or a concern without Plan evidence and a concrete correction or decision.

## Existing classifications

Map each retained finding to exactly one existing classification:

- `risk`
- `ambiguity`
- `missing-decision`
- `contradiction`
- `test-gap`
- `adr-candidate`
- `glossary`

Pi Prompt's compatibility schema has no classification field. Encode the classification in a stable annotation key such as `risk-auth-boundary` or `test-gap-rollback`, and do not add result fields. The annotation body states the Plan evidence, why it is material, and the concrete correction or decision needed.

Use `adr-candidate` only for a consequential architectural choice worth preserving. Use `glossary` only when an undefined or inconsistently used domain term can materially change implementation.

## Exact Pi Prompt output contract

For Pi Prompt, output only one JSON object in the existing artifact format:

```json
{
  "kind": "grill",
  "basedOnDocumentRevision": 1,
  "annotations": {
    "risk-example": {
      "target": {
        "kind": "range",
        "elementId": "anchor-id",
        "field": "body",
        "start": 0,
        "end": 4
      },
      "body": "Plan evidence and the material correction needed."
    }
  },
  "decisionTree": {
    "nodes": [
      {
        "id": "root",
        "question": "Material findings",
        "annotationKeys": ["risk-example"],
        "options": []
      }
    ]
  }
}
```

The lowercase `grill` value and existing field names are immutable compatibility tokens, not product wording. Do not add classification, severity, rationale, truths, artifacts, wiring, or any other fields.

Range offsets are zero-based, half-open Unicode code points. Use the controller's accepted flat range target or canonical selector target exactly as instructed; never invent anchors. Every annotation key must appear exactly once in `decisionTree`. Keep the tree compact. A node's `options` may be empty or contain a single option; never fabricate alternatives to satisfy a cardinality. Add multiple options only for genuine unresolved choices that materially change implementation, with concrete consequences. If there are no material findings, return `"annotations": {}` and `"decisionTree": {"nodes": []}`.

Do not reveal chain-of-thought or analysis. Output only the structured findings.

## Explicit non-adoption of Open GSD artifacts

The goal-backward checks above adapt a bounded review technique; they do not adopt Open GSD's planning system. Do not create or require:

- `.planning` directories;
- `ROADMAP`, `CONTEXT`, `REQUIREMENTS`, or `VERIFICATION` files;
- `must_haves`;
- requirement IDs;
- waves or frontmatter;
- XML task blocks;
- GSD report formats.

## Scope boundaries

Do not inspect unrelated files, rewrite the Plan, implement code, create or modify documentation, publish issues, commit, push, deploy, install dependencies, or start services. Capture ADR candidates and glossary terms as findings so To Spec can synthesize them; repository documentation requires separate user authorization.

## Upstream attribution

### Matt Pocock — MIT

Adapted for Pi from Matt Pocock's `grill-with-docs` skill at commit `391a2701dd948f94f56a39f7533f8eea9a859c87`. The upstream wrapper delegates to `/grilling` and `/domain-modeling`; this standalone adaptation incorporates the needed behavior directly.

### Open GSD — MIT

The bounded goal-backward review gates adapt concepts from Open GSD's plan checker and PLAN format. Official sources:

- https://github.com/open-gsd/gsd-core
- https://github.com/open-gsd/gsd-core/blob/next/docs/how-to/plan-a-phase.md
- https://github.com/open-gsd/gsd-core/blob/next/docs/reference/plan-md.md
