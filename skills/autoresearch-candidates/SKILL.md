---
name: autoresearch-candidates
description: Find high-value autoresearch opportunities for a repo, project, or product area by combining user-provided context, docs, source code, and history such as PRs or commits. Use when the user wants candidate places to run autoresearch, benchmark ideas, measurable optimization targets, or an issue-ready list of ranked experiment opportunities.
---

# Autoresearch Candidates

Use this skill to find and rank places where autoresearch could bring real value. The output is a researched list of candidates, not an autoresearch run.

The skill must answer one question: where can an autoresearch loop improve a measurable number with enough guardrails that the result would matter?

## Required input

The user must provide context for where to look. If any of these are missing and cannot be inferred, ask before starting:

- Target repo or local path.
- Product area, project, feature, subsystem, or theme.
- Context sources to inspect: docs, issues, PRs, commits, local code, saved reports, dashboards, or user-provided links.
- History window if relevant: recent PRs, open PRs, open issues, last N commits, last N weeks, or a specific branch/range.
- Known exclusions or prior work that must not be proposed again.
- Desired output: markdown research file, main-screen summary, issue draft, or all of these.

If the user says something like "current repo" or "this project", infer the current working directory but still confirm if the repo or scope is ambiguous.

## Hard rules

- Do not run autoresearch. This skill only finds candidates.
- Do not create GitHub issues, project draft issues, Slack messages, PRs, comments, or any external post unless the user explicitly approves the exact final text and target.
- If the user asks for an issue, create a draft file first and show it. Confirm whether they want a real repo issue or a project draft item before posting.
- Exclude prior work. If the user, memory, commits, PRs, or docs show an area was already used for autoresearch or recently exhausted, remove it entirely instead of demoting it.
- Do not pad the list. If fewer than the requested number are genuinely good, say so.
- Prefer measurable, repeatable candidates over interesting but vague engineering ideas.
- Penalize correctness-only work, one-off migrations, stale issues, deployment topology, and anything that requires production-only validation unless it has a clear local benchmark.
- No code changes. Only write report/draft files requested by the user.

## What qualifies as a good candidate

A candidate is good when it has all of these:

- A numeric primary metric: wall time, SQL count, external call count, jobs enqueued, rows scanned, memory, allocations, test runtime, queue latency, error count, retry count, or another measurable number.
- A repeatable benchmark plan: local test, runner, script outline, SQL plan, seeded data, or CI command.
- Multiple plausible variants autoresearch can try.
- Guardrails that prove behavior did not regress.
- Evidence from context, code, docs, PRs, commits, issues, logs, or prior reports.
- A plausible path to value if the metric improves.

A candidate is weak when:

- The only evidence is an old issue with no current code signal.
- It is mainly product/correctness work.
- The benchmark would measure a fake local model of a production-only problem.
- It has only one obvious implementation rather than a space of variants.
- It cannot be guarded without human judgment.

## Workflow

### 1. Set up the work area

For multi-step investigations, use an ADA artifact if one is active or create one only when ADA state is empty. Save generated reports in the artifact folder unless the user explicitly asks for repo-root files.

Create a short task list only if the work has multiple steps.

### 2. Capture scope and exclusions

Write down:

- Target repo/path and branch.
- Context sources to inspect.
- History window.
- Candidate count requested.
- Known exclusions and prior work.
- Output path and format.

Before ranking anything, search memory for prior work in the same area. Past autoresearch work, shipped optimizations, and user corrections must affect the candidate list.

### 3. Gather evidence from three angles

Use separate focused passes. For complex repos, spawn agents so the lead does not mix evidence collection with judgment.

Context/docs pass:

- Read docs, project briefs, user-provided links, ADRs, README files, existing reports, and relevant memory.
- Extract product or operational pain, known constraints, success metrics, and explicit exclusions.

Code pass:

- Inspect local source for batch jobs, expensive loops, N+1-prone paths, external client fanout, repeated setup, slow tests, query-heavy dashboards, polling loops, retry loops, and high-cardinality processing.
- Prefer source evidence with file paths and test anchors.

History pass:

- Inspect open issues, open PRs, recently closed PRs, and relevant commits.
- Look for performance pain, review churn, production failures, query kills, retries, flaky/slow tests, large migrations, or repeated refactors.
- Separate active current pain from stale historical noise.

If using spawned agents, give each one a narrow output file and a strict "do not post externally" instruction. Use `openai/gpt-5.5` for `team_spawn` unless the user explicitly says otherwise, and verify with `team_status` immediately.

### 4. Build raw candidate inventory

For every possible candidate, record:

- Title.
- Source evidence.
- Metric.
- Benchmark plan.
- Variants autoresearch could try.
- Expected gain.
- Confidence.
- Guardrails.
- Weaknesses.

Keep this raw list separate from the final ranked list.

### 5. Run a critic pass

Before presenting results, run a filtering pass that tries to kill candidates.

The critic pass must reject:

- Prior/exhausted work.
- Vague ideas without a benchmark.
- Correctness-only items pretending to be optimization work.
- One-off migrations or cleanup with low value.
- Production-topology ideas that cannot be represented locally.
- Candidates with no safe variants.

The critic pass must produce:

- Survivors, ranked by expected benefit.
- Rejected candidates, with reasons.
- Any conditional candidates with clear kill criteria.

### 6. Final report format

Produce a markdown file with this structure:

```markdown
# Autoresearch candidates for <scope>

## Scope

<What was inspected: docs, code, PRs, commits, issues, branches, dates.>

## Top candidates

### 1. <Candidate title>

What: <What area/path/process this targets.>

Why: <Why it is likely worth autoresearch.>

Potential gains: <Numbers that could improve and why they matter.>

Benchmark: <Concrete local/CI/script measurement plan.>

Variants: <What the loop could safely try.>

Guardrails: <Tests/checks/semantic constraints.>

Confidence: <High/medium/low with one sentence.>
```

For issue-ready output, use a simpler format:

```markdown
# <Title>

## What

This is a list of the best current candidates for running autoresearch in <scope>. Each one has a measurable baseline we can try to improve.

## Candidates

### 1. <Candidate title>

What: <short paragraph>

Why: <short paragraph>

Potential gains: <short paragraph>

Benchmark: <short paragraph>
```

Do not use a table for the issue body unless the user asks for one.

### 7. Present results

Show the best options on the main screen when visual comparison is useful. Keep user-facing summary concise:

- Output file path.
- Candidate count.
- Top five.
- Important exclusions.
- Whether any requested count was not met.

## Scoring guidance

Rank candidates by:

1. Expected benefit if improved.
2. Evidence strength from multiple sources.
3. Benchmark stability.
4. Variant richness.
5. Guardrail strength.
6. Confidence that the result is not already known or exhausted.

Do not let strong evidence override an exclusion. Prior work that is already exhausted is not a candidate.

## Issue creation guidance

If the user wants a GitHub issue:

1. Draft the exact issue title and body in a local markdown file.
2. Show the exact text to the user.
3. Ask whether the target is a real repo issue or a project draft item.
4. For a real repo issue, confirm the repository.
5. For a project draft item, state plainly that it will be a draft item, not a repo issue.
6. Only create after explicit approval.
7. After creation, provide the verified URL. Do not guess project pane URLs.

## Common mistakes to avoid

- Recommending the obvious prior autoresearch target again.
- Treating "open in a project" as "create a draft issue" without confirming.
- Padding to hit a requested number.
- Ranking source-obvious ideas above higher-impact cross-source evidence without thinking.
- Hiding weak candidates in a table where they look equally valid.
- Producing a giant report when the user asked for an issue-ready summary.
