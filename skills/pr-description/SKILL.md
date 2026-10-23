---
name: pr-description
description: Write, rewrite, or refresh pull request titles and descriptions from a diff, branch, issue, notes, or existing draft. Use when asked to write a PR body, fill a PR template, summarize changes for reviewers, or prepare the description while opening a PR. Produces concise, evidence-backed Markdown adapted to repository conventions. Does not review code, implement changes, or authorize publishing.
---

# PR descriptions

Give reviewers enough context to understand the change and decide where to look. Write for the next maintainer as well as today's reviewer. Explain what the diff cannot explain on its own.

## Establish the evidence

1. Identify the requested source: pasted material, an existing PR, a committed branch, or uncommitted work. For a prose-only rewrite, use the supplied text without requiring GitHub access. Preserve technical meaning; do not fill factual gaps with plausible details.
2. In a repository, read its contribution guidance and applicable PR template before choosing a structure. Preserve required sections and checklists. Use recent accepted PRs as style examples when available, not as proof about this change.
3. For an existing PR, inspect its current title, body, actual base/head, and full diff. For a new branch, establish the intended base rather than assuming `main`. A stacked PR normally compares against its parent, not the repository default branch.
4. Inspect the full intended change, not just the latest commit or diff statistics. For a committed branch, `git log <base>..HEAD --oneline` and `git diff <base>...HEAD` provide context. Read changed code where needed to understand the behavior. If output is truncated, retrieve the remainder before claiming full coverage.
5. Keep staged, unstaged, and untracked work distinct from committed branch changes. Include them only when they belong to the requested description; inspect relevant untracked files directly. Do not silently mix unrelated work into a PR.
6. Reuse available test results, CI status, screenshots, benchmarks, and issue discussions. A test file proves that a test exists, not that it passed. A diff may establish behavior but not the author's motivation, operational safety, or measured impact.

If the repository, base, or intended scope is materially ambiguous, ask one focused question. If only evidence is missing, state the specific gap rather than blocking a useful draft. Treat authentication or network failures as unavailable evidence, not proof that no PR exists. A branch name alone is insufficient for factual implementation claims.

## Write the title and body

Use a specific, action-oriented title naming the changed behavior or outcome. Follow the repository's title convention; Conventional Commits prefixes are not universal. Avoid titles such as "Fix bug", "Improvements", "Phase 2", or "Address feedback" without identifying the actual change.

Choose the smallest useful body:

- For a small change, one short paragraph can explain the problem and result.
- For a typical bug fix or feature, explain the problem, observable before/after behavior, and the approach when it is not obvious. Add a short testing section when evidence or a verification gap affects review.
- For a risky or complex change, add only the applicable compatibility, migration, rollout, failure-mode, or review-order details. Do not bury a breaking change to meet a length target.

Without a repository template, this is a starting point, not a mandatory form:

```markdown
<Problem or motivation, followed by what changes for the user or maintainer.>

<Non-obvious approach or tradeoff, only if it helps review.>

## Testing
- <Observed check and result, or explicit missing verification.>
```

Delete unused scaffolding. Combine related points rather than repeating them under Summary, Changes, and Implementation. Prefer a short paragraph or a few focused bullets over a file-by-file inventory. Name files only when they direct review or explain responsibility.

Keep the main explanation understandable without opening a ticket. Link verified issues and design decisions for detail. Use closing keywords only when the PR actually completes the issue and closure is intended; otherwise use a neutral reference.

For this user's durable-issue workflow, start the body with `Issue ID: <project> <issue-id>` when that ID is supplied. Never expose local task-file paths. Do not invent an ID for unrelated PRs.

## Include evidence that changes the review

- Distinguish completed checks from proposed checks. Report a concise command or scenario and its observed result when useful. Keep failures, skips, pending CI, and coverage limits visible. Do not say "all tests pass" based on a focused run.
- If execution status is unknown, say "Test results not provided" or "Not verified here", not "Tests not run". Use the latter only when that fact is known. Check a checklist item only with supporting evidence.
- For bug fixes, describe the failing condition and the regression coverage that addresses it. For behavior-preserving refactors, name the contract intended to remain unchanged and the available evidence; do not assert equivalence merely because it is called a refactor.
- For performance claims, give the measured before/after values and enough workload/environment context to interpret them. Without measurements, describe the mechanism or intended effect without promising a speedup.
- For visual changes, include an existing screenshot or recording when it helps comparison. For non-obvious flows, a small diagram can help. Neither is mandatory; do not invent artifacts or turn logs into images for decoration.
- For breaking changes, name the affected consumer contract and required action. Distinguish a proposed rollout or rollback plan from one already executed or verified. Do not prescribe an automatic rollback for irreversible data changes.
- For stacked work, describe this PR's own problem, delta, and verification. Keep stack relationships in native PR metadata; mention a dependency in prose only when it explains a concrete integration or deployment constraint. Do not narrate internal plan IDs, slice numbers, replacement sequences, delivery budgets, or closed PRs as the rationale. State meaningful exclusions without presenting planned work as delivered.

## Keep the prose direct

Use plain English, concrete verbs, and sentence-case headings. Remove marketing claims, agent/process narration, repeated summaries, decorative emojis, and unneeded jargon. Preserve the user's voice and requested language. Do not add a generic checklist or a "no risks" claim to make the description look complete.

On refresh, describe the current resulting change, not the chronology of fixes and review rounds. Preserve useful author context and required issue references. Remove stale claims superseded by the new diff, but do not overwrite unexplained conflicting facts without checking them.

Do not expose secrets, personal data, private customer details, local absolute paths, or inaccessible local evidence links. Use repository-relative paths and approved shareable references. Describe sensitive changes at a safe level; drafting is not permission to disclose private material.

## Return and stop

Return the proposed title separately from the copy-ready Markdown body, unless the user asked for only one. Keep unresolved questions outside the body; retain a material testing or safety gap inside it. Use placeholders only when the user explicitly wants a template or incomplete scaffold.

Before returning, check:

- Does it explain why the change exists and what actually changes?
- Does each factual claim have support in the inspected evidence or supplied context?
- Does it describe the intended diff, including meaningful limits, without padding?
- Are completed tests distinguishable from plans and unknowns?
- Are repository conventions, issue references, and relevant risks preserved?
- Can a reviewer find the important information without reconstructing the work session?

This skill drafts text. It does not authorize edits to code, branch creation, commits, pushes, test execution, service startup, uploads, or creating/updating a remote PR. Those actions require their own applicable authorization. Do not run them just to fill a description. If publishing is separately authorized, follow the active review and publication workflow rather than treating this skill as approval.
