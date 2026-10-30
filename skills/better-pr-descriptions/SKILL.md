---
name: better-pr-descriptions
description: Draft or revise pull request descriptions in Leo's What / Context / Validation format. Use when writing or updating a PR body, summarizing a PR for reviewers, or turning implementation details into a description a person can review and test.
---

# PR descriptions

Every PR body has three sections, in this order: What, Context and Validation. What says what the PR does and why it matters. Context gives the facts from outside the diff that a reviewer needs. Validation shows that the idea is right and how a person can see it work.

```markdown
## What

<What changes, in one sentence.> <The reasons that matter.>

Closes [<issue title> - #<n>](<url>).

## Context

- <A fact from outside the diff, with its link.>
- <Another one.>

## Validation

- <Claim.> Test: `<exact test name>`.
- <Claim.> <Code fact, real run or linked document.>
- Not proven yet: <gap>. <What would prove it.>

To see it work:

1. <Setup.>
2. <Action.> <What you should see.>
3. <Control action.> <What you should see instead.>
```

Leave Context out when there's nothing to say. What and Validation are always there. For a docs-only or mechanical PR, Validation can be one line that says where to see the result.

## Hard rules

- Never add a complexity rating, reason or section.
- No other sections: no Problem, Solution, How to test, Q&As, rollout, risk, reviewers, CI or implementation notes. Their useful content goes into the three sections.
- A format Leo set for a specific repo, stack or PR wins over this one. Search memory for it before drafting.
- Keep fields a repository template requires, after the three sections.
- In a public repository, leave out internal names, hosts, channels and links.
- Writing the body to the PR is an external post. Show Leo the exact body and wait for his go.

## What

What changes and why, in one or two short paragraphs.

- The first sentence says what changes for the user or the system, in plain words: "The app now emails a receipt after every refund", not "Adds RefundReceiptMailer".
- Then only the reasons a reviewer needs to agree it should merge: the bad state it prevents, the need it meets, or the rule it sets.
- End with the issue link: `Closes [<title> - #<n>](<url>)` or `Part of [...](...)`. A cleanup PR uses `Cleanup of: [...](...)` and doesn't close the issue.
- No file walkthrough, no list of methods, no list of fields.

## Context

Facts from outside the diff that change how someone reads it. One short bullet per fact.

- Merge order: what to review first, what has to ship before this one.
- A decision made outside this PR that limits it, with the link to where it was made.
- An outside constraint: another team's contract, a vendor rule, an approval the deploy needs.
- What's left out on purpose, and where it lives.
- What happens at merge or deploy, and how to undo it, when that isn't obvious.

Leave out what the diff already shows, the story of how you got here, and anything that repeats What.

If a deploy needs a named approval, Context says who approves and links the approval once it exists. Don't deploy before the link is there.

## Validation

Two parts: why the idea is right, then how to see it work.

### Why it's right

Write the claims the change rests on, the ones a careful reviewer would question. Usually two to five, one bullet each: the claim in one or two plain sentences, then its proof.

Start with the approach when a reviewer could ask "why this way?". State the choice and the evidence that settled it. Then the behavior claims.

A proof is something the reviewer can check for themselves:

- the test that fails if the claim breaks, written as `Test: <exact test name>`,
- the place in the code that makes it true,
- a real run or production signal: what was seen, and where,
- a contract, document or brief, linked,
- a step below, when a step shows it: "(steps 2 and 3)".

If a claim has no proof yet, keep it and say so: "Not proven yet: <gap>. <What would prove it>." Never present a gap as a result.

### How to see it work

After the claims, a line that starts `To see it work`, then numbered steps a person can follow without asking you anything. The line may say where the steps run and why, such as "from `bin/rails console`, because there's no local Kafka".

- Step 1 is the setup, unless the `To see it work` line already says it: the flag, account, plan, branch, config or command that puts them in the right state.
- Every later step says where to go, what to do and what they should see: the exact page, command, request or input, then the exact text, output or state.
- For long input, point at something that already builds it, such as a test helper, instead of pasting it.
- Add a control step when it shows the change matters: the refused case, the old path, the error that doesn't retry.
- A step that only works in production, or after deploy or enable, says so, says where to look (dashboard, log, command) and says what normal looks like. If it uses something up, such as a test contract, say that too.
- Write only steps you ran or traced line by line against the code. If you ran them, say where in one line.

### Never in Validation

- Test counts, pass tallies, coverage numbers, "N new tests", "covers nine outcomes".
- Lists of what the tests cover. Name a test only when it's the proof of one claim.
- CI commands as validation: `bin/rails test`, `rubocop`, `pnpm test`, `pnpm typecheck`, `tsc`. CI shows those.
- Verbs with no visible result: verify, ensure, confirm it works, make sure, check the behavior, observe, monitor, record, inspect.
- A step that ends without what the person should see.

Before and after, for calibration:

- Not this: "The tests cover parsing, retries, malformed input and handler failures."
- This: "A failed write raises, so the consumer retries the message instead of acknowledging it. Test: `retries the message when the write fails`."
- Not this: "`pnpm typecheck`, `pnpm test` (1302 tests, 5 new), and `pnpm check:package` pass."
- This: nothing. CI already says it.
- Not this: "Before: the config renders correctly."
- This: "In `deploy/production.yaml`, find the `worker-0` Deployment. It has `replicas: 0` and `QUEUE: billing`."

## Writing

Write like Leo talks: direct, plain, with contractions. These rules draw on the humanizer skill, anti-slop writing guidance and ASD-STE100 principles, settled where they disagree.

- One idea per sentence. Join cause and effect inside the sentence with because, so, until or unless. Don't stack short fragments for effect.
- Active voice. Name who acts: "the worker retries", "the importer skips", "the billing service refuses".
- One term per thing. If it's "the handoff" once, it's "the handoff" every time.
- Name code only when the reader has to find or type it: flags, topics, metrics, config keys, commands, public APIs. Otherwise say what the code does.
- Keep a number when it's part of the behavior: a timeout, a window, a version, a retry cap. Drop numbers that only show effort.
- Say the rule instead of listing items: "everything the delivery handler needs to match a message", not six field names.
- Colons and commas, never em or en dashes. Semicolons rarely.
- No bold mini-headings, no bold for emphasis, no emoji, no title case.
- No stock AI words: crucial, robust, seamless, leverage, comprehensive, enhance, key as an adjective, significant, additionally, notably, importantly, essentially.
- No reason tacked on with an -ing tail ("..., ensuring the message is kept").
- No "This PR", no "not X but Y", no closing summary, no sign-off.
- Hedge only real uncertainty, and then say what's unknown.
- Links are markdown with readable text. Link a PR on the host where it lives. Links to other repos are full URLs.

## Length

- What: under 30 seconds of reading, about 100 words.
- What and Context together: under a minute.
- Validation: about a minute of reading. If the proof needs much more, the PR is probably doing too much.

## Before posting

1. Read the current body, the linked issue, any brief it links, and the diff at the PR head.
2. Check every fact about state or time against today: stacked on, merged, draft, flag on or off, enabled, replicas, and whether a linked issue or PR is still open. Bodies go stale after every push, and after every merge they mention.
3. Write the claims first and find the proof for each. Drop or mark what you can't prove.
4. Write the steps. Run them if you can. Otherwise trace each one against the code.
5. Write What and Context.
6. Read the body once against Writing and once against Never in Validation. Search it for `—`, `–`, `**` and the stock words.
7. Show Leo the exact body and wait for his go.
