---
name: prove-it-runs
description: "Prove with logs that any work on a server runs through its whole lifecycle. Call the real code on a running local server, like an end-to-end test without the rest of the system. The only change to the code is breadcrumb log lines: silly, greppable log lines added for the local run at each step the code passes through, from the trigger to the end. Following them in the logs, where the human watches, is the proof. The code being proved keeps its behavior. Only in extreme need, mock a missing service or project, as little as possible. Breadcrumbs and mocks stay local and never reach a remote or production. Use for HTTP endpoints, webhooks, background jobs, message consumers, scheduled tasks, maintenance and one-off tasks, scripts, and service code run from a console. Use it when the user says 'prove it works', 'prove it runs', 'prove we can run it', 'show me in the logs', 'run it locally end to end', 'simulate the workers', or asks for a silly text to track in the logs."
---

# Prove it runs

Prove with logs that any work on a server runs, from the trigger to the end. Call it for real on a running local server, like an end-to-end test without the rest of the system. Add breadcrumb log lines along the path, then follow them in the logs where the human watches. The breadcrumbs are the only proof.

A breadcrumb log line, or breadcrumb, is a custom log line added for the local run at a step the code must pass through. When it shows up in the logs, the code passed that step. A breadcrumb at every step, from the trigger to the end, proves the whole lifecycle ran.

## When to use it

- Use it for any work that runs on a server: HTTP endpoints, webhooks, background jobs, message consumers, scheduled tasks, maintenance and one-off tasks, scripts, and service code called from a console or runner.
- Use it when someone needs to see the code run, or when it has never run end to end. A start script that refuses to boot until a missing piece exists is one sign.
- Stop and ask when the only way to run it reaches production, shared data or real people, such as real messages, emails or payments.

## Breadcrumbs never ship

The breadcrumbs, any mock, the caller scripts and the local process entries exist only for this run. They never reach a remote, a pull request or production.

- Keep them in one commit on a clearly named local branch, such as `banana-phone-demo`. Write "LOCAL DEMO ONLY, never push" in the commit message, so the check below can find it. Make that commit only when the user's request covers it; otherwise ask first.
- Never push the demo branch, the demo commit or any of its files to any remote. Never set an upstream for the demo branch.
- Never commit breadcrumbs or mocks to a branch you ship. Never cherry-pick, merge or rebase the demo commit into one.
- Gate every breadcrumb and mock twice: an environment variable set only on the demo processes, and a local-environment check such as `Rails.env.development?` or `NODE_ENV=development`. If one leaves the checkout by mistake, it stays silent and changes nothing. Check the gate on and off with one command each.
- Before any later push from that checkout, list the outgoing commits and files: `git log --format='%h %s' <remote>/<branch>..HEAD` and `git diff --name-only <remote>/<branch>..HEAD`. Stop if a demo commit or file is among them.
- When the human is done with the demo, switch the checkout back to its base, so no breadcrumb or mock stays checked out.
- If a breadcrumb or mock ever reaches a remote, stop and tell the user right away. Do not rewrite shared history yourself.

## Plan the proof

1. Check memory notes and project docs for a recipe for this environment: how to start the server, where its output goes, how to reach its database, cache or broker. Do not rediscover what a note already says.
2. Write the claim in one sentence. Example: "A refund request enqueues the refund job, and the worker runs it and marks the order refunded."
3. List the cases the claim covers. The main path is always one. Add each edge the claim or the user names, such as an invalid payload, a duplicate or a retry. The claim sets the cases, not the full list of branches in the code.
4. Pick the trigger: the way the work starts in production, such as a request, an enqueue, an event, a schedule or a command.
5. List the lifecycle steps from the trigger to the end, such as trigger, boot, receive, decode, validate, handoff, downstream and completion. Each step gets a breadcrumb.
6. List what the path needs that is not running locally. Each item is a blocker or, in extreme need, a minimal mock. See "Change only the logs".
7. Find out where the human watches: the pane or log they named, or else the terminal that runs the dev server. Plan to put the breadcrumbs there.

## Change only the logs

Keep the server real, with its real start command and config. Keep the code being proved and the local resources the server already has, such as its database, cache, queue backend or broker. Leave out the rest of the system.

The only change to the code being proved is breadcrumb log lines. It keeps doing exactly what it did: no stubs, no stand-ins, no overridden checks and no early returns. Starting and calling the work is not a change to the code: a start command, a local process entry, `curl`, a publish, an enqueue or a caller script.

- Mock only in extreme need: a dependency from another service or project that is not there, such as a handoff another team will deliver or an external service the run cannot reach. Make the mock as small as possible, just enough for the flow to pass through, and give it a breadcrumb. Never mock the code being proved. List every mock in the report.
- If a missing piece stops the run and no mock is justified, put a breadcrumb at the last point the code reaches. Report the blocker and how far the path got. Ask the user before you change anything beyond logs.

## Call it

Make each call a command the human can run again, and make one call per case.

- HTTP endpoint or webhook: `curl` the running server with the real method, path, headers, body and local credentials. Sign a webhook payload with the local secret. Add `-w 'PURPLE PENGUIN trigger: %{http_code}\n'` so curl prints its own breadcrumb.
- Background job: enqueue through the real enqueue path into the real queue backend, and run the real worker on its own queue. Running the job inline skips the queue and the worker.
- Message consumer: publish to the local broker with a small caller script that sends the real wire format, with the same envelope, schema version, destination and key. Build payloads from the schemas or contracts the project bundles, not from memory. Let the script wait for a warm-up, then send a round on an interval, both read from env. A new consumer group that starts reading at the end misses everything sent before it joins.
- Scheduled task: run the real scheduler with a short schedule set through config or env. Calling the job directly skips the scheduler.
- Maintenance task, one-off task or script: run the real command with real arguments and env against the local database. Capture stdout, stderr and the exit code.
- Service code: call it from the project's console or runner, such as `bin/rails runner`, with real arguments.

## Add the breadcrumbs

- Put one breadcrumb at each lifecycle step and at the outcome of each case. When an outcome only counts a metric or reports an error, add the breadcrumb beside that call.
- Use a unique, silly, greppable prefix, such as `PURPLE PENGUIN` or `BANANA PHONE`. Silly text does not collide with real log lines, and a human can spot it in a busy pane.
- Name the step with one stage word, such as `trigger`, `boot`, `received`, `decoded`, `validated`, `handoff`, `started` or `done`. Outcomes get their own, such as `dropped`, `rejected` or `retried`. The first missing stage word names the step that broke.
- Put a correlation ID on every breadcrumb, such as an order ID or a message ID, so one call can be traced across processes. Build it from the case name, a round number and a short random suffix, such as `ord-main-1-7f3a`, so cases and repeated calls stay apart.
- Print one breadcrumb per step per call to stdout, and flush it. Piped output is often buffered (`$stdout.sync = true` in Ruby, `PYTHONUNBUFFERED=1` in Python).
- Let the caller script print the `trigger` breadcrumb. It shows that the call left the source.

For the refund claim above, the worker boot and one call could print:

```text
worker | PURPLE PENGUIN boot: listening on queue refunds-demo
web    | PURPLE PENGUIN received: POST /refunds order=ord-main-1-7f3a
web    | PURPLE PENGUIN handoff: enqueued RefundJob order=ord-main-1-7f3a
worker | PURPLE PENGUIN started: RefundJob order=ord-main-1-7f3a
worker | PURPLE PENGUIN done: order=ord-main-1-7f3a marked refunded
```

The process manager adds the process name to each line. Keep that prefix in the evidence, because it shows which process printed each breadcrumb. The `trigger` breadcrumb from curl shows up in the terminal that ran it.

## Find where the output goes

"Running" in a process manager is not proof. A dev runner can show every process as running while it sends their output to `/dev/null`.

- Before the run, read the dev runner script and the process manager config, such as `bin/dev` and `Procfile.dev`. Find where stdout and stderr go for each process: the terminal, a log file, `/dev/null`, a hidden tmux pane or a container log.
- Read hidden panes directly. Overmind runs its processes as windows of one tmux session on a private socket. The socket name starts with `overmind-<app>-`; look under `$TMPDIR`. This prints the last 200 lines of one process: `tmux -L <socket> capture-pane -p -J -S -200 -t <app>:<process>`.
- Route the breadcrumbs to where the human watches. Check the dev runner for a verbose flag first, such as `VERBOSE=1`. Do not make the human dig through hidden panes.

## Contain the demo

- If a process or tree belongs to someone else, such as another agent session or a teammate, inspect it first: the command and uptime (`ps`), `git status`, the branch and the SHA. If the tree has uncommitted work, stop and ask. Restart a process only when the request needs it, and record its original start command.
- Record SHAs for the undo: the base and the demo commit. Do not create backup branches or refs. Git already keeps the old commits.
- Run the proof on the same base as the branch you ship. If you have to use an older base, name what it lacks and which steps or cases that leaves unproven.
- Give the demo its own queues, consumer groups or job names, so it never takes real work or moves real offsets.
- Note infrastructure you create, such as topics, queues or seeded rows. Switching branches does not remove it.

## Pre-flight

Run cheap checks that fail in seconds before a slow boot that fails in minutes.

- The server and its local resources answer: `curl -fsS <health URL>` or `nc -z <host> <port>`.
- The routes, queues or topics exist. Create missing ones locally with the admin client the project already bundles, then list them again (for Kafka, `kcat -b <host>:<port> -L`).
- The schema or contract versions you send exist locally.
- A one-off in-process call to the code that receives the trigger prints the breadcrumbs you expect.
- You know where each process's output goes and, for consumers, where each one starts reading.

## Confirm and report

- Start the processes, then make the calls. Wait for the `done` breadcrumb of the last case, not for a fixed time. Use one bounded wait, sized to the warm-up plus two rounds when a caller repeats (about 2 minutes in the run that shaped this skill). For a log file, start `tail -n 0 -F <log> | rg -m 1 'PURPLE PENGUIN done'` under a command timeout before the call. For a pane, capture it once after that time and search the capture. Do not loop on sleep.
- A timeout means you did not see the breadcrumb. It does not mean it was not printed. A longer wait does not help when the output goes somewhere else. Check where the output goes before you call any step broken.
- When breadcrumbs are missing, find the first missing stage word and debug that step.
- A step or case with no breadcrumb in the logs is unproven. It is not a pass. If a step prints the wrong breadcrumb, report it. Fix the code only when the user asks, on the branch you ship, then call that case again. The fix is proven when its breadcrumb shows up.

Copy every breadcrumb verbatim from where the human watches, with its process name. Do not retype or trim it. Then report in this shape:

```text
Where to look: <pane or log>, and how often new breadcrumbs show up
Proof: <for each case, the breadcrumbs from trigger to end, verbatim>
Real: <the server, processes, code and local resources that ran>
Mocks: <each mock and the missing service or project it stands for, or none>
What changed: <demo branch and commit, the gate variable, created infrastructure, restarted processes and their new start commands>
Not pushed: <the demo branch has no upstream, and `git ls-remote --heads <remote> <demo-branch>` returns nothing>
Unproven: <steps or cases with no breadcrumb, and why. For a blocker, name it and give the last breadcrumb reached>
Undo: <exact commands: stop the processes, switch back to the base SHA, delete or keep the demo branch, restart the original command>
```

Leave the demo running while the human watches. Give the undo steps instead of tearing it down yourself.

Save new environment facts, such as how to start a process locally or where its output goes, to a memory note. Keep this skill generic.

## Example: the run that shaped this skill

The claim: three new consumers read messaging events (a message received, a reply sent, a reply delivered) and hand each event off. The handoff belonged to another project and did not exist yet, so the start script refused to boot.

- Real: the dev server, the three consumer processes on their own consumer groups, the local broker and the schemas the project bundles.
- Caller: a publisher script sent real wire-format events after a 60-second warm-up, then about every 26 seconds.
- Mock, behind `BANANA_PHONE=1` on the demo process entries only: a minimal handoff that printed a breadcrumb and let each event pass through. The gate check: the mock's `installed?` printed `true` with the gate and `false` without it.
- A one-off script printed all three consumer breadcrumbs before anything booted.
- The first wait timed out after 6 minutes while every process showed as running. The dev runner sent their output to `/dev/null`. The process manager's hidden tmux panes held 13 complete rounds. `VERBOSE=1` put the breadcrumbs in the main pane.

One round, with generic process names:

```text
banana-phone-publisher     | BANANA PHONE publisher: ring 1, US.banana1 says "is this thing on?"
consumer-message-received  | BANANA PHONE received: US.banana1 says "is this thing on?" (banana-in-1-cb4e75)
consumer-message-sent      | BANANA PHONE sent: reply banana-out-1-948d5e to US.banana1 left the building
consumer-message-delivered | BANANA PHONE delivered: reply banana-out-1-948d5e to US.banana1 landed on the buyer's phone
```

The buyer ID links all four breadcrumbs, and the publisher's own breadcrumb shows that each round left the source.
