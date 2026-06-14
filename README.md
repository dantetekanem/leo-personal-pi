# leo-personal-pi

My personal collection of Pi agent skills — the **source of truth** for the skills I use day to day.

Repo: <https://github.com/dantetekanem/leo-personal-pi> · Skill index: [SKILLS.md](./SKILLS.md)

## What this is

This repo holds my hand-picked skills under `skills/`, each a plain folder (with a `SKILL.md` and/or `skill.yaml`). Pi loads skills from `~/.pi/agent/skills/`, where each managed skill is a **symlink** back into this repo. That means:

- I edit, version, and back up my skills here in git.
- Changes show up in Pi instantly through the symlinks — no copy step.
- I can still keep local-only, unmanaged skills as real folders in `~/.pi/agent/skills/`; those aren't tracked here.

Some skills (e.g. `frontend-design`, `skill-creator`) come from [anthropics/skills](https://github.com/anthropics/skills) and are intentionally **not** vendored here — they're listed in [SKILLS.md](./SKILLS.md) with links to their upstream source.

## Layout

```
leo-personal-pi/
  README.md
  SKILLS.md          # index of all skills, with links
  skills/
    <skill-name>/
      SKILL.md       # the skill prompt / instructions
      skill.yaml     # optional skill metadata
```

## Workflow

- **Edit a skill:** change it under `skills/`, then `git commit` & `git push`.
- **Add a new skill:** create `~/Poetry/leo-personal-pi/skills/<skill>/`, then link it into Pi:
  ```sh
  ln -s ~/Poetry/leo-personal-pi/skills/<skill> ~/.pi/agent/skills/<skill>
  ```
  then commit & push.
- **Remove a managed skill:** delete the symlink in `~/.pi/agent/skills/` and the folder under `skills/`, then commit & push.

## Configs

Terminal/multiplexer dotfiles backed up under `configs/` (kept as **plain copies**, not symlinked — update them here when I change the live files).

| File in repo | Installs to | What it does |
|--------------|-------------|--------------|
| `configs/tmux.conf` | `~/.tmux.conf` | Mouse on, extended/CSI-u key reporting, image-protocol passthrough. Ghostty titles (`#S · #W`), auto-rename windows to the running command, `destroy-unattached` so sessions die with their last tab. |
| `configs/ghostty/config.ghostty` | `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty` | Entry point — just `config-file` points at `local.ghostty`. |
| `configs/ghostty/local.ghostty` | `~/.config/ghostty/local.ghostty` | The real Ghostty config: launches a new tmux session on start (inherits cwd), keybinds `cmd+s` → tmux save-buffer and `cmd+b` → tmux zoom toggle, Tokyo Night palette, `background-opacity = 0.85`, `background-blur = 16`, 10px padding, `confirm-close-surface = false`, shell integration (no-title). |
| `configs/ghostty/new-tmux-session` | `~/.config/ghostty/new-tmux-session` | Helper script Ghostty runs on launch — starts a tmux session rooted at the active pane's directory (falls back to `$PWD`/`$HOME`). |

> Note: `config.ghostty` and `local.ghostty` reference each other and the helper script by absolute path under `/Users/leonardopereira/…`; adjust if restoring on a different machine/user.

## Source of truth

`~/Poetry/leo-personal-pi` is canonical. Never edit skills through the symlinks under `~/.pi/agent/skills/` — always edit here.
