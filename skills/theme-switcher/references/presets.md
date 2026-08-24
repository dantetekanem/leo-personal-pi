# Theme presets

These are the exact supported palettes. Patch only the named theme keys in live configs.

## Dracula preset

This deliberately combines Ghostty's Tokyo Night palette with Dracula in Herdr and Pi. Leo approved this combination as the rollback baseline.

### Ghostty

```ini
palette = 0=#15161e
palette = 1=#f7768e
palette = 2=#9ece6a
palette = 3=#e0af68
palette = 4=#7aa2f7
palette = 5=#bb9af7
palette = 6=#7dcfff
palette = 7=#a9b1d6
palette = 8=#414868
palette = 9=#f7768e
palette = 10=#9ece6a
palette = 11=#e0af68
palette = 12=#7aa2f7
palette = 13=#bb9af7
palette = 14=#7dcfff
palette = 15=#c0caf5
background = #1a1b26
foreground = #c0caf5
cursor-color = #c0caf5
cursor-text = #15161e
selection-background = #33467c
selection-foreground = #c0caf5
```

Expected loaded values include `background = #1a1b26`, `foreground = #c0caf5`, and `palette = 4=#7aa2f7`.

### Herdr

```toml
[theme]
name = "dracula"
auto_switch = false
```

Remove the Lumon `[theme.custom]` table when selecting Dracula.

### Pi

Set the top-level `theme` setting to `dracula`.

## Lumon preset

The base palette comes from Basecamp Omarchy's Lumon theme:
https://github.com/basecamp/omarchy/blob/master/themes/lumon/colors.toml

The warm semantic colors used for errors, success, and warnings are deliberate accessibility exceptions to the otherwise monochromatic Lumon palette.

### Ghostty

```ini
palette = 0=#1b2d40
palette = 1=#4d86b0
palette = 2=#5e95bc
palette = 3=#6fa4c9
palette = 4=#6fb8e3
palette = 5=#8bc9eb
palette = 6=#b4e4f6
palette = 7=#d6e2ee
palette = 8=#304860
palette = 9=#73a6cb
palette = 10=#86b7d8
palette = 11=#9dcae5
palette = 12=#f2fcff
palette = 13=#b1d8ee
palette = 14=#d1eef8
palette = 15=#ffffff
background = #16242d
foreground = #d6e2ee
cursor-color = #f2fcff
cursor-text = #1b2d40
selection-background = #4d9ed3
selection-foreground = #1b2d40
```

Expected loaded values include `background = #16242d`, `foreground = #d6e2ee`, and `palette = 4=#6fb8e3`.

### Herdr

```toml
[theme]
name = "terminal"
auto_switch = false

[theme.custom]
sidebar_bg = "#16242d"
active_row_bg = "#1b2d40"
selection_bg = "#304860"
panel_bg = "#16242d"
accent = "#8bc9eb"
red = "#ff8f9b"
green = "#8fd8b5"
yellow = "#f0d38a"
blue = "#6fb8e3"
```

Do not add unsupported `theme.custom.cyan` or `theme.custom.magenta` keys.

### Pi

Copy `../assets/pi-lumon.json` to `~/.pi/agent/themes/lumon.json` and set the top-level `theme` setting to `lumon`.
