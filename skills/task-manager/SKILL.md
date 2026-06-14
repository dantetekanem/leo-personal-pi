---
name: task-manager
description: Durable project task tracking with simple folder organization and formatted markdown files under ~/Poetry/_projects-tasks.
---

# Task Manager

Use this skill to manage durable project tasks as folders and markdown files under `~/Poetry/_projects-tasks`.

## Folder organization

Each project has one folder:

```text
~/Poetry/_projects-tasks/<project>/
├── stats.json
├── p0/
├── p1/
├── p2/
└── p3/
```

Priority folders:

- `p0`: urgent or blocking work.
- `p1`: high-priority work.
- `p2`: useful but not urgent.
- `p3`: someday work.

Task files:

```text
issue-001.md
issue-002.md
issue-003.md
```

Completed task files:

```text
issue-001.done.md
```

Use `ls -la ~/Poetry/_projects-tasks/<project>/<priority>/` to inspect a priority folder.

## File format

Every task file uses this format:

```text
{TITLE}

--

What: Describe the reason to get this task done.
Context: Extra information about the task.
Acceptance Criteria:
- [ ] First concrete criterion.
- [ ] Second concrete criterion.

--
```

Acceptance criteria use `[ ]` while open and `[x]` after verified completion.

## Creating a task

1. Choose the project and priority folder.
2. List the priority folders with `ls -la`.
3. Pick the next unused `issue-NNN.md` number.
4. Create the markdown file using the file format above.
5. Update `stats.json` to match the folder contents.

## Completing a task

1. Verify the acceptance criteria.
2. Update completed criteria to `[x]`.
3. Rename `issue-NNN.md` to `issue-NNN.done.md` in the same priority folder.
4. Update `stats.json` to match the folder contents.

## Reprioritizing a task

1. Move the task file to the new priority folder.
2. Keep the same issue number and filename.
3. Update `stats.json` to match the folder contents.

## stats.json

`stats.json` records the project name, task root, open count, done count, total count, counts per priority folder, next issue number, and last update time.
