---
name: theme-switcher
description: "Switch Leo's coordinated Ghostty > Herdr > Pi appearance. Use whenever Leo says 'theme to dracula', 'theme to lumon', asks to restore his terminal theme, or asks to change the theme across his terminal stack. Execute the switch for him instead of giving manual instructions."
compatibility: "macOS with Ghostty, Herdr, and Pi"
---

# Theme Switcher

Switch Leo's full terminal stack as one unit:

1. Ghostty owns the terminal background and ANSI palette.
2. Herdr either uses its Dracula theme or follows Ghostty through its `terminal` theme.
3. Pi uses the matching `dracula` or `lumon` theme.

Supported presets are `dracula` and `lumon`. Read [references/presets.md](references/presets.md) before changing anything.

## Trigger interpretation

Treat these as direct execution requests:

- `theme to dracula`
- `theme to lumon`
- `switch the terminal theme to dracula`
- `restore my Dracula theme`

Do not respond with steps for Leo to perform. Apply the named preset, validate it, reload what can reload safely, and report the result.

If Leo requests another theme, research and design it as a separate theme addition. Do not guess a preset or silently approximate one of the two supported themes.

## Live and replicated files

Theme switching may touch only the theme-related portions of:

- `~/.config/ghostty/local.ghostty`
- `~/.config/herdr/config.toml`
- `~/.pi/agent/settings.json`
- `~/.pi/agent/themes/lumon.json`
- `~/Poetry/leo-personal-pi/configs/ghostty/local.ghostty`
- `~/Poetry/leo-personal/herdr/config.toml`, when that replication snapshot exists

The managed Lumon Pi theme source is `assets/pi-lumon.json` inside this skill.

Preserve commands, keybindings, shell behavior, opacity, blur, padding, notifications, sidebar layout, status commands, plugins, models, packages, and every unrelated setting. Do not replace an entire live config with a preset fragment.

## Switching workflow

### 1. Read and classify current state

Read the live Ghostty, Herdr, and Pi config files. Check whether the replicated files exist. Note drift, but do not clean up unrelated differences.

### 2. Apply the selected Ghostty palette

Use the selected Ghostty values from `references/presets.md`. Replace only:

- ANSI `palette = 0` through `palette = 15`
- `background`
- `foreground`
- `cursor-color`
- `cursor-text`
- `selection-background`
- `selection-foreground`

Keep `background-opacity`, `background-blur`, padding, commands, and keybindings unchanged.

Apply the same palette-only replacement to `~/Poetry/leo-personal-pi/configs/ghostty/local.ghostty`. Its non-theme settings may intentionally differ from the live file, so never copy the whole live file over it.

### 3. Apply the selected Herdr theme

Patch only `[theme]` and `[theme.custom]` using the selected preset.

- Dracula removes the Lumon `[theme.custom]` table.
- Lumon uses Herdr's `terminal` theme so the host ANSI palette stays authoritative, then adds the documented UI and semantic-status overrides.

If `~/Poetry/leo-personal/herdr/config.toml` exists, synchronize it to the fully validated live Herdr config after the live change succeeds. This file is an exact replication snapshot, unlike the palette-only Ghostty backup.

### 4. Apply the selected Pi theme

For Lumon, ensure `~/.pi/agent/themes/lumon.json` is byte-for-byte equivalent to this skill's `assets/pi-lumon.json`, then set `theme` to `lumon` in `~/.pi/agent/settings.json`.

For Dracula, leave the Lumon theme file available and set `theme` to `dracula`.

Do not restart, terminate, or replace the active Pi session. A running Pi instance keeps its loaded theme; the saved selection applies to the next Pi session.

### 5. Validate before reloading

Validate all changed surfaces:

- Parse the Pi settings and Lumon theme as JSON.
- Confirm the Lumon theme still defines all 51 required Pi color tokens when Lumon is selected.
- Run `ghostty +show-config --changes-only` and verify the selected background, foreground, palette, cursor, and selection values appear.
- Run `herdr config check`.
- When the Herdr replication snapshot exists, run `HERDR_CONFIG_PATH=<snapshot> herdr config check` and confirm it matches the live config exactly.

Stop on validation failure. Do not reload a broken config or partially switch the remaining layers.

### 6. Reload safely

After every validation passes:

- Trigger Ghostty's configured reload shortcut on macOS with System Events: `Cmd+Shift+,`.
- When running inside Herdr (`HERDR_ENV=1`), run `herdr server reload-config` and require `status: applied` with no diagnostics.
- Outside Herdr, do not control another Herdr session. Report that its validated config will apply on the next launch or authorized reload.

Never stop the Herdr server for a theme change because that would terminate pane processes.

## Completion report

Report the active preset and these three layers:

- Ghostty: loaded live or validated for next launch
- Herdr: applied live or validated for next launch
- Pi: saved for the next session, with the current-session limitation stated when relevant

Mention any replication files synchronized. Keep the report short.
