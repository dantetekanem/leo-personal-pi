# Repository Instructions

## Scope

These instructions apply to `leo-personal-pi` and all nested skill directories unless a nearer `AGENTS.md` overrides them.
This repository is the source of truth for its managed Pi skills.

## Managed Skill Source of Truth

- Edit managed skills only under `skills/<name>/` in this repository.
- Never edit a managed skill through its installed symlink under `~/.pi/agent/skills/`.
- Treat installed symlinks as views of repository content, not independent copies.
- Treat real directories under `~/.pi/agent/skills/` as unmanaged local skills. Never vendor, replace, overwrite, or delete them.
- Keep `SKILLS.md` as the canonical index of repository-managed skills.

## Skill Lifecycle

For a new managed skill:

1. Preserve the chosen skill name across its directory, metadata, index entry, and installed link.
2. Follow the installed `skill-creator` guidance without duplicating its full workflow here.
3. Create `skills/<name>/SKILL.md` and any narrowly necessary bundled resources.
4. If the install path is missing, link it with:
   `ln -s ~/Poetry/leo-personal-pi/skills/<name> ~/.pi/agent/skills/<name>`
5. If the install path already exists, inspect it first. Never overwrite an unmanaged real directory.
6. Add the managed skill to `SKILLS.md`.

For an existing managed skill, make modifications in `skills/<name>/` first.
For removal, remove the repository skill and its `SKILLS.md` entry first; remove the installed symlink only as the direct consequence.
Never remove or rewrite unrelated installed entries.

## Skill Content

- Keep each skill focused on a clear capability and avoid broad generic rules.
- Prefer a `SKILL.md` under 500 lines.
- Move deep references, reusable scripts, and supporting assets into bundled resources when that keeps the main instructions concise.
- Preserve an existing skill's name when improving or reorganizing it.

## Change Safety

- Preserve existing dirty work and restrict edits to the authorized paths.
- Do not create or use worktrees unless the user explicitly authorizes them.
- Require exact side-effect authorization before committing, pushing, installing packages, or changing installed links.
- Use pnpm for all JavaScript or TypeScript package operations.

## Verification

Run the checks relevant to the authorized change:

```sh
git status --short
git diff --check
git diff --name-only
```

Inspect every changed or untracked path directly. Note that `git diff --check` does not inspect an untracked file until it is staged.
When an installed managed link is created, changed, or removed, verify the relevant state with `test -L` and `readlink`.
Do not create broad tests or evaluation suites unless requested or included in an approved skill-improvement workflow.
