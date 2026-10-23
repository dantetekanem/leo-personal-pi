---
name: prompt-cost-auditor
description: Analyze Pi session token and prompt overhead from session logs, runtime settings, tool catalogs, extension prompt injections, skills, and context files. Use whenever User asks why a Pi turn cost many tokens, what was sent in the first prompt, which prompt/tool sources are responsible, or how to optimize prompt context. Produce a numbers-first report with token counts, percentages, source paths, confidence levels, and usefulness classifications; do not give generic disable/split-profile opinions.
---

# Prompt Cost Auditor

Use this skill to audit Pi prompt/token overhead with evidence. The output is a report, not a vibe-based recommendation list. The goal is to show what was sent, how much it cost, where it came from, and whether each source is useful enough to stay always-on or should be loaded differently.

## Operating stance

- Report measured facts first: token counts, percentages, source files, commands used, model/settings, and exact log entries.
- Separate exact measurements from reconstruction and estimates. Label every row with a confidence level.
- Do not frame optimization as “disable things” by default. Classify usefulness: keep always-on, lazy-load/trigger, shorten, merge/dedupe, justify as worth the cost, or investigate further.
- Do not throw generic opinions into the report. Every recommendation needs evidence: token impact, usage frequency signal, source path, overlap, or user workflow relevance.
- If raw provider request bodies are not persisted, say that plainly. Do not claim byte-for-byte prompt reconstruction when only logs/settings/source files are available.

## When to write and render a report

If the user asks for a report file, write Markdown to the requested or temporary path. For an investigation/check, stay read-only and present the report without writing a file unless requested. Render only with a suitable available tool; otherwise return Markdown or the authorized file path.

Good default path for rendered reports:

`/tmp/pi-prompt-cost-report-<session-id-or-timestamp>.md`

## Evidence tiers

Use these labels in every table:

- Exact: directly from session JSONL usage fields, settings JSON, file existence, file byte counts, or command output.
- Reconstructed: derived from Pi source/config behavior, active package settings, extension prompt injection code, or prompt builder code.
- Estimated: inferred because the raw provider payload or provider-side tokenization is unavailable. Include the method.
- Unknown: cannot determine from available logs/files. State what would be needed.

## Procedure

### 1. Locate the session and target turn

Use the current working directory to locate the matching session folder under `~/.pi/agent/sessions/`. Pi encodes path separators in folder names, so inspect the sessions directory and choose the folder matching the cwd.

Useful commands:

```bash
ls ~/.pi/agent/sessions
ls ~/.pi/agent/sessions/<encoded-cwd-folder>
```

Read the session header and identify the target user message plus the first assistant response after it.

Useful command:

```bash
jq -r 'select(.type=="session" or .type=="model_change" or .type=="thinking_level_change" or (.type=="message" and (.message.role=="user" or .message.role=="assistant"))) | if .type=="session" then "session\t"+.id+"\t"+.cwd elif .type=="model_change" then "model\t"+.provider+"/"+.modelId elif .type=="thinking_level_change" then "thinking\t"+.thinkingLevel elif .message.role=="user" then "user\t"+.timestamp+"\t"+(.message.content[0].text // "") else "assistant\t"+.timestamp+"\tinput="+((.message.usage.input//0)|tostring)+"\tcacheRead="+((.message.usage.cacheRead//0)|tostring)+"\toutput="+((.message.usage.output//0)|tostring)+"\ttotal="+((.message.usage.totalTokens//0)|tostring)+"\tstop="+(.message.stopReason//"") end' <session.jsonl>
```

### 2. Extract exact usage and cache math

For the target assistant request, capture:

- provider/model
- thinking level
- input tokens
- output tokens
- cacheRead tokens
- cacheWrite tokens, if present
- totalTokens
- cost fields, if present
- stopReason
- tool calls made

Keep provider-reported usage fields separate. Confirm whether `input` includes cached tokens before calculating request input; never double-count them.

`cacheRead` measures reused tokens, which may include user messages, conversation, and tool results. It cannot establish an exact static/dynamic split, and later cache reads may exceed the first request's input.

Only call component attribution exact when the actual request components and matching tokenization are available. Otherwise use source-based estimates, label their method, and leave unknown categories unallocated. Compute component percentages against the first request's total input, not just its uncached portion.

### 3. Identify what was set

Read the settings and report only relevant fields:

```bash
jq -r '{defaultProvider, defaultModel, defaultThinkingLevel, followUpMode, steeringMode, treeFilterMode, extensions, skills, packageCount:(.packages|length)}' ~/.pi/agent/settings.json
```

Also report:

- cwd from the session header
- current date injected by Pi
- loaded model and thinking from session log
- active package count
- explicitly enabled/disabled extensions from settings

### 4. Measure source files and prompt injections

Measure known prompt/context sources with byte counts. Token counts from bytes are estimates unless the provider exposes tokenization.

Common sources:

```bash
wc -c ~/.pi/agent/AGENTS.md ~/.pi/agent/settings.json
```

For extension prompt injections, search active extension source for `before_agent_start`, `systemPrompt`, and prompt modules. Read source files before assigning blame.

Useful command:

```bash
rg -n "before_agent_start|systemPrompt|prompt" ~/.pi/agent /path/to/local/pi/packages -g '*.ts' -g '*.js' -g '*.md'
```

Known examples to check when active:

- Friday communications prompt, often in `~/.pi/agent/extensions/friday/prompt.ts` or the package source.
- Chrome bridge primer, often in the `pi-chrome` extension source.
- Memory-policy or other extension-injected blocks if present in the runtime prompt.

### 5. Build the tool catalog inventory

Tool schema overhead comes from callable tool definitions sent to the provider: tool name, description, parameters JSON schema, nested object/array shapes, enum values, and sometimes long usage descriptions.

Because Pi session logs usually do not persist the raw provider request body, tool-schema token counts are often reconstructed or estimated. Be precise about this.

Inventory tool families from the active tool list available in the session and from enabled packages/extensions. Group them by domain rather than listing only raw names.

Recommended families:

- Core file/edit/search: `read`, `bash`, `edit`, `write`, `agentic_search`, `ls`, `grep`, `find` if present.
- Friday/comms/todo: `communicate`, `friday_control`, `todo`.
- ADA/artifacts: `ada_create`, `ada_update`, `ada_checkpoint`, `ada_get`, `ada_read`.
- Teams/agents/tasks: `team_create`, `spawn_teammate`, inbox, shared memory, file claims, team tasks, shutdown tools.
- Memory/session/skill management: `memory`, `memory_search`, `session_search`, `skill_manage`.
- Chrome/browser control: `chrome_*` tools.
- Web/ask/review/render: `web_search`, `web_fetch`, `ask_user`, `open_code_diff`, `submit_pr_review`, and any available renderer.
- Loops/monitors/tasks: `Loop*`, `Monitor*`, `Task*`.
- Domain tools: French learning, Home Assistant, project-specific tools, or other package-specific tools.
- Wrapper/meta tools: `multi_tool_use.parallel` or similar.

For each family, record:

- tool count
- representative tool names
- likely source package/extension
- why the schema is heavy, if it is heavy
- confidence level

### 6. Estimate categories carefully

Use exact measurements where possible, then estimate only what cannot be measured.

A safe method:

1. Start with the first request's total input, interpreting cache fields according to provider semantics.
2. Attribute exact components only with actual request and tokenization evidence; otherwise label reconstruction or estimates.
3. Estimate visible text prompt components from source byte counts and loaded prompt snippets.
4. Leave unmeasured tool schemas and remaining overhead unallocated, or report a clearly labeled estimated remainder.
5. Do not label a remainder as tool cost alone; it can also include harness instructions, memory, and other context.

Do not overfit estimates. Prefer ranges when data is weak.

### 7. Classify usefulness instead of defaulting to removal

Use this decision table for every costly source:

| Classification | Use when | Report wording |
|---|---|---|
| Keep always-on | High-frequency, safety-critical, or cheap relative to value | “Keep always-on; cost is justified by...” |
| Lazy-load/trigger | Valuable but domain-specific or rarely needed | “Move behind command/skill/first-use registration; not because useless, because not always relevant.” |
| Shorten | Useful but verbose descriptions/policies inflate schema/prompt | “Keep capability; shorten prompt/schema text.” |
| Merge/dedupe | Multiple tools or prompts overlap in function | “Consolidate overlapping surfaces; preserve behavior.” |
| Explain/justify | Expensive but intentionally central to workflow | “Cost is real; leave it and document why.” |
| Investigate further | Source or usage frequency unclear | “Need more data before changing.” |
| Remove | Obsolete, broken, duplicate with no unique value, and User agrees | “Candidate for removal only if User confirms it is not used.” |

Use measured or observable evidence for classification:

- token or byte size
- number of tools added
- activation frequency from recent session logs if checked
- overlap with other tools
- source path and package owner
- whether the feature is central to User workflow
- whether command-based or first-use registration is technically feasible

### 8. Produce the report

Use this structure:

```markdown
# Pi Prompt Cost Audit: <session or turn>

## Executive summary
- First request input (including any cached portion): N tokens
- Static/dynamic split: measured with request-component evidence, or unknown
- Model/thinking: provider/model, thinking
- Main cost drivers: concise ranked list with confidence

## Exact usage from session log
| Turn | Timestamp | Input | Cache read | Output | Total | Stop | Tool calls | Cost |

## What was set
| Setting | Value | Source | Confidence |

## Prompt/source attribution
| Category | Tokens | % of first input | Confidence | Method | Source |

## Tool catalog inventory
| Family | Tool count | Est. tokens or range | % | Source package/path | Usefulness classification | Evidence |

## High-impact findings
Numbered findings, each with evidence and source path.

## Optimization guide
| Item | Current behavior | Cost signal | Usefulness | Classification | Proposed change | Risk/tradeoff | Verification |

## Unknowns and limits
List missing raw payloads, tokenizer limitations, or unavailable source data.

## Commands run
List commands used to produce the report.
```

Numbers matter. Percentages should use the first request's total input count as denominator unless the table says otherwise.

### 9. Render with available tools

If a Markdown file was authorized and created, use an available renderer when requested. If none is available, return the path and say that it was not rendered. Do not require a named renderer or start/install one without explicit permission.

## Pitfalls

- Do not say “exactly what was sent” if the raw provider request body is not logged. Say “exact from log” and “reconstructed from runtime sources.”
- Do not use `totalTokens` as request input: it includes output. Interpret `usage.input`, `cacheRead`, and `cacheWrite` using the provider's field semantics; show each separately.
- Do not count cached tokens as free. They are part of displayed total and may be billed differently by provider.
- Do not blame the user message when static prompt/tool prefix dominates.
- Do not recommend split profiles or disabling as a default answer. The report should analyze usefulness and loading strategy.
- Do not use memory search unless the user asks about preferences or prior decisions; it can inflate the very prompt under investigation.
- Do not let a large tool result pollute the next model turn. Use narrow `jq`, `wc`, `rg`, and `read` offsets.
- Do not use banned file-discovery patterns. Use `rg`/`fd` via shell where needed, and `read` for file contents.

## Verification checklist

Before finalizing, confirm the report contains:

- First request input token count with provider/cache semantics stated.
- Exact model and thinking level.
- Exact target session path.
- Static/dynamic split only with request-component evidence; otherwise explicitly unknown.
- At least one table with tokens and percentages.
- Source paths for every major category.
- Confidence labels for exact/reconstructed/estimated/unknown values.
- A usefulness classification for each optimization target.
- No generic “disable it” or split-profile advice unless User explicitly requested that framing.
