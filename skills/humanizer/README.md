# Humanizer for Pi

This directory vendors [blader/humanizer](https://github.com/blader/humanizer) as a managed Pi skill.

- Upstream version: `2.11.2`
- Upstream commit: `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5`
- License: MIT, preserved in [LICENSE](./LICENSE)

`SKILL.md` is the portable upstream skill prompt. Pi loads it through the managed link at `~/.pi/agent/skills/humanizer`.

## Use in Pi

Invoke it directly:

```text
/skill:humanizer [text or file path]
```

Pi can also load it when a request asks to humanize prose, remove AI-writing patterns, or preserve a writer's voice while editing.

## Update from upstream

Review the upstream changes, replace `SKILL.md` and `LICENSE`, then update the version and commit recorded here. Keep the installed Pi path as a symlink to this directory.
