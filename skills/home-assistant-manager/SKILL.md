---
name: home-assistant-manager
description: Home Assistant configuration, automation, log, deployment, and Lovelace dashboard management. Use when working on Home Assistant YAML, .storage Lovelace dashboards, hass-cli, Home Assistant SSH/HA CLI workflows, reload-vs-restart decisions, automation verification, or tablet dashboard optimization.
---

# Home Assistant Manager

Expert Home Assistant configuration management for pi. This skill adapts the Claude Home Assistant skill from https://github.com/komal-SkyNET/claude-skill-homeassistant/blob/main/SKILL.md to pi workflows, safety rules, and verification habits.

## Core Rules

- Treat Home Assistant work as production-impacting unless the user says otherwise.
- If the user asks to investigate, check, diagnose, or look into something, stay read-only: inspect files, logs, states, and configs only. Do not edit, deploy, reload, restart, install, commit, or push.
- Ask before any write or operational change unless the user explicitly requested that change in the current turn.
- Ask before committing, pushing, restarting Home Assistant, changing remote files, or deploying to the Home Assistant instance.
- Always verify after changes. Do not say something should work without a test result or an explicit statement that it could not be verified.
- Prefer the smallest safe reload over a full restart.
- Use rapid scp iteration only for temporary testing when the user authorizes remote writes. Commit only final, verified changes when the user authorizes commits.
- Use current Home Assistant documentation for unfamiliar or version-sensitive features before implementing.

## Capabilities

- Remote Home Assistant instance management via SSH, HA CLI, and hass-cli.
- Configuration validation and safe reload or restart planning.
- Automation creation, testing, manual triggering, and log verification.
- Log analysis and error diagnosis.
- Lovelace dashboard development, including .storage dashboards and tablet-optimized UIs.
- Template syntax patterns, debugging, and type safety.
- Deployment workflow selection between git and rapid scp iteration.

## Prerequisites To Verify

Before making operational changes, verify the relevant access and context:

1. SSH access to the Home Assistant instance, commonly root@homeassistant.local.
2. hass-cli installed locally when REST API access is needed.
3. HASS_SERVER and HASS_TOKEN loaded when using hass-cli.
4. Local git repository maps to the Home Assistant /config directory when using git workflow.
5. Any dashboard custom cards are installed in the target Home Assistant instance.
6. Current Home Assistant docs are available through web search, code search, or MCP if needed.

## Preferred Local CLI

Use the globally installed `ha` helper before writing any ad hoc script. Do not build inline Node.js, Ruby, Python, or curl wrappers for normal Home Assistant REST work. The helper reads the bearer token from `/Users/leonardopereira/.pi/agent/mcp.json` by default and is installed at `/Users/leonardopereira/.pi/agent/bin/ha` with a copy in `/Users/leonardopereira/.local/bin/ha`.

Use `HASS_TOKEN` only when an explicit token override is needed. Ambient `HA_TOKEN` is intentionally ignored because it may be stale or refer to a different Home Assistant endpoint.

The helper resolves `homeassistant.local` to a cached local IP before REST calls because Ruby mDNS resolution can hang. Use `HA_LOCAL_IP` to override the fallback IP, `HA_RESOLVE_LOCAL=0` to disable this behavior, and `--debug` or `HA_DEBUG=1` to print connection diagnostics to stderr without exposing the token. `HA_TIMEOUT` applies to REST and WebSocket operations. The helper includes raw `ha api` and `ha ws` commands for Home Assistant endpoints that are not exposed as regular services.

Common read-only commands:

```bash
ha ping
ha --debug ping
ha config
ha states everything_presence_one_28d74c
ha state sensor.everything_presence_one_28d74c_mmwave_target_distance
ha state sensor.one sensor.two sensor.three
ha attrs sensor.everything_presence_one_28d74c_mmwave_target_distance
ha services select
ha events
ha ws input_boolean/list
ha api GET /api/config/automation/config
```

Service and reload commands:

```bash
ha call select.select_option entity_id=select.everything_presence_one_28d74c_mmwave_mode option='Distance and Speed'
ha call light.turn_on entity_id=light.kitchen brightness=128
ha call domain.service '{"entity_id":"light.kitchen"}'
ha ws input_boolean/create name='Office Desk' icon=mdi:desk
ha api POST /api/config/automation/config/example_id @automation.json
ha trigger automation.name
ha reload automations
ha reload scripts
ha reload templates
```

Polling and sampling commands:

```bash
ha sample sensor.everything_presence_one_28d74c_mmwave_target_distance sensor.everything_presence_one_28d74c_mmwave_target_count sensor.everything_presence_one_28d74c_mmwave_target_speed -n 20 -i 1
ha sample sensor.temperature -n 10 -i 2 --summary sensor.temperature
```

Remote Home Assistant CLI commands:

```bash
ha check
ha logs --tail 50
ha logs --errors --tail 20
ha core check
ha core logs
ha cli supervisor info
ha ssh 'ha core logs | tail -20'
```

For wait-then-check flows, use ordinary shell composition instead of scripting:

```bash
ha call select.select_option entity_id=select.everything_presence_one_28d74c_mmwave_mode option='Distance and Speed'
sleep 9
ha state select.everything_presence_one_28d74c_mmwave_mode switch.everything_presence_one_28d74c_uart_target_output sensor.everything_presence_one_28d74c_mmwave_target_distance sensor.everything_presence_one_28d74c_mmwave_target_count binary_sensor.everything_presence_one_28d74c_mmwave binary_sensor.everything_presence_one_28d74c_occupancy
```

If `ha` is missing, fails to authenticate, or lacks a common Home Assistant API capability, fix or extend the CLI installation first. Do not fall back to inline Node.js, Ruby, Python, or curl wrappers unless the user explicitly asks for a one-off script.

## Remote Access Patterns

### ha Helper Through The REST API

Prefer the local `ha` helper for REST API reads and service calls:

```bash
ha states
ha states kitchen
ha state sensor.entity_name
ha call automation.trigger entity_id=automation.name
ha reload automations
```

### hass-cli Through The REST API

hass-cli uses HASS_SERVER and HASS_TOKEN environment variables when configured.

```bash
hass-cli state list
hass-cli state get sensor.entity_name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name
```

### SSH For HA CLI

```bash
ssh root@homeassistant.local "ha core check"
ssh root@homeassistant.local "ha core restart"
ssh root@homeassistant.local "ha core logs"
ssh root@homeassistant.local "ha core logs | grep -i error | tail -20"
```

## Deployment Workflows

### Standard Git Workflow For Final Changes

Use only when the user authorizes committing and pushing final, verified changes.

```bash
# 1. Make local changes.
# 2. Validate configuration.
ssh root@homeassistant.local "ha core check"

# 3. Commit and push only with explicit user authorization.
git add file.yaml
git commit -m "Description"
git push

# 4. Pull on the Home Assistant instance.
ssh root@homeassistant.local "cd /config && git pull"

# 5. Prefer targeted reload when sufficient.
ha reload automations
# Or restart only when required and authorized.
ssh root@homeassistant.local "ha core restart"

# 6. Verify state and logs.
ha state sensor.new_entity
ha logs --errors --tail 20
```

### Rapid Development Workflow For Authorized Testing

Use scp for quick testing before committing only when the user authorizes remote writes.

```bash
# 1. Make changes locally.
# 2. Quick deploy for testing.
scp automations.yaml root@homeassistant.local:/config/

# 3. Reload when sufficient.
ha reload automations

# 4. Test and iterate.

# 5. Commit final tested changes only with explicit user authorization.
git add automations.yaml
git commit -m "Final tested changes"
git push
```

Use scp for rapid iteration, frequent small adjustments, experimental changes, and dashboard UI testing. Use git for final, stable, version-controlled changes.

## Reload Vs Restart Decision Making

Always assess whether a reload is sufficient before requiring a full restart.

Usually reloadable:

- Automations: ha reload automations
- Scripts: ha reload scripts
- Scenes: ha reload scenes
- Template entities: ha reload templates
- Groups: ha reload groups
- Themes: ha reload themes

Usually requires full restart:

- Min/max sensors and some platform-based sensors.
- New integrations in configuration.yaml.
- Core configuration changes.
- MQTT sensor and binary_sensor platform configuration.
- Dashboard registry changes in .storage/lovelace_dashboards.

## Automation Verification Workflow

After an authorized automation change:

1. Validate configuration.

```bash
ssh root@homeassistant.local "ha core check"
```

2. Reload automations if configuration is valid.

```bash
ha reload automations
```

3. Manually trigger the automation for instant feedback.

```bash
ha trigger automation.name
```

4. Check logs after a short delay.

```bash
sleep 3
ssh root@homeassistant.local "ha core logs | grep -i 'automation_name' | tail -20"
```

5. Verify the actual outcome.

For notifications, ask the user whether they received it and check logs for mobile_app messages. For device control, inspect the controlled device state. For sensors, verify the entity exists and has the expected state.

```bash
ha state switch.device_name
ha state sensor.new_sensor
```

Success indicators include initialized triggers, automation action execution, and no error or warning messages. Error indicators include Error executing script, Invalid data for call_service, TypeError, or Template variable warning.

## Dashboard Management

### Dashboard Fundamentals

Lovelace dashboards are often JSON files in .storage, such as .storage/lovelace.control_center. Creating the dashboard file is not enough; new dashboards must also be registered in .storage/lovelace_dashboards. Dashboard content changes usually only require a browser refresh. Dashboard registry changes usually require a Home Assistant restart.

### Dashboard Development Workflow

Use this workflow only when authorized to write to the remote Home Assistant instance.

```bash
# 1. Make local changes.
vim .storage/lovelace.control_center

# 2. Deploy for immediate visual testing.
scp .storage/lovelace.control_center root@homeassistant.local:/config/.storage/

# 3. Refresh browser with Ctrl+F5 or Cmd+Shift+R.
# 4. Iterate until stable.
# 5. Commit final stable changes only when authorized.
git add .storage/lovelace.control_center
git commit -m "Update dashboard layout"
git push
ssh root@homeassistant.local "cd /config && git pull"
```

### Creating A New Dashboard

```bash
# Step 1: Create dashboard file.
cp .storage/lovelace.my_home .storage/lovelace.new_dashboard

# Step 2: Register in .storage/lovelace_dashboards.
# Add an entry like this:
```

```json
{
  "id": "new_dashboard",
  "show_in_sidebar": true,
  "icon": "mdi:tablet-dashboard",
  "title": "New Dashboard",
  "require_admin": false,
  "mode": "storage",
  "url_path": "new-dashboard"
}
```

```bash
# Step 3: Deploy both files.
scp .storage/lovelace.new_dashboard root@homeassistant.local:/config/.storage/
scp .storage/lovelace_dashboards root@homeassistant.local:/config/.storage/

# Step 4: Restart Home Assistant only when authorized.
ssh root@homeassistant.local "ha core restart"
```

Track dashboard files in git intentionally. If .storage is ignored by default, add explicit exceptions for dashboard files and .storage/lovelace_dashboards when appropriate.

## View Type Decision Matrix

Use panel view when displaying full-screen maps or cameras, a single large full-width card, zero-margin layouts, or minimizing scrolling.

Use sections view when organizing multiple cards, building responsive grids, or presenting multi-section dashboards.

```json
{
  "type": "panel",
  "title": "Vacuum Map",
  "path": "map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "entity": "vacuum.dusty"
    }
  ]
}
```

```json
{
  "type": "sections",
  "title": "Home",
  "sections": [
    {
      "type": "grid",
      "cards": []
    }
  ]
}
```

## Card Types Quick Reference

### Mushroom Light Card

```json
{
  "type": "custom:mushroom-light-card",
  "entity": "light.living_room",
  "use_light_color": true,
  "show_brightness_control": true,
  "collapsible_controls": true,
  "fill_container": true
}
```

Use for modern, touch-optimized light controls.

### Mushroom Template Card

```json
{
  "type": "custom:mushroom-template-card",
  "primary": "All Doors",
  "secondary": "{% set sensors = ['binary_sensor.front_door'] %}\n{% set open = sensors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ sensors | length }} open",
  "icon": "mdi:door",
  "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
}
```

Use Jinja2 templates for dynamic content. Multi-line templates inside JSON need escaped newlines.

### Built-In Tile Card

```json
{
  "type": "tile",
  "entity": "climate.thermostat",
  "features": [
    {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
    {"type": "target-temperature"}
  ]
}
```

Use when custom cards are not required.

## Common Template Patterns

### Counting Open Doors

```jinja2
{% set door_sensors = [
  'binary_sensor.front_door',
  'binary_sensor.back_door'
] %}
{% set open = door_sensors | select('is_state', 'on') | list | length %}
{{ open }} / {{ door_sensors | length }} open
```

### Color-Coded Days Until

```jinja2
{% set days = state_attr('sensor.bin_collection', 'daysTo') | int %}
{% if days <= 1 %}red
{% elif days <= 3 %}amber
{% elif days <= 7 %}yellow
{% else %}grey
{% endif %}
```

### Conditional Display

```jinja2
{% set bins = [] %}
{% if days and days | int <= 7 %}
  {% set bins = bins + ['Recycling'] %}
{% endif %}
{% if bins %}This week: {{ bins | join(', ') }}{% else %}None this week{% endif %}
```

Always use int or float filters before numeric comparisons to avoid template type errors.

## Tablet Optimization

- 11-inch tablets typically fit three to four columns.
- Touch targets should be at least 44 by 44 pixels.
- Minimize scrolling, especially for wall tablets.
- Use panel view for full-screen maps and cameras.
- Color-code status for fast scanning with red, green, amber, yellow, and grey.

```json
{
  "type": "grid",
  "columns": 3,
  "square": false,
  "cards": [
    {"type": "custom:mushroom-light-card", "entity": "light.living_room"},
    {"type": "custom:mushroom-light-card", "entity": "light.bedroom"}
  ]
}
```

## Common Dashboard Pitfalls

### Dashboard Not In Sidebar

Cause: file was created but not registered. Fix by adding it to .storage/lovelace_dashboards and restarting Home Assistant when authorized.

### Configuration Error In Card

Cause: custom card missing, wrong syntax, or template error. Check HACS installation, browser console, and Developer Tools > Template.

### Auto-Entities Fails

Cause: card_param is not supported by the card type. Use cards that accept an entities parameter such as entities, vertical-stack, or horizontal-stack. Grid and glance often need different syntax.

### Vacuum Map Has Margins Or Scrolling

Cause: sections view adds margins. Use panel view for full-width map layouts.

### Template Type Errors

Error example: TypeError: '<' not supported between instances of 'str' and 'int'. Fix by using type filters such as states('sensor.days') | int < 7.

## Dashboard Debugging

```bash
python3 -m json.tool .storage/lovelace.control_center > /dev/null
hass-cli state get binary_sensor.front_door
```

Also check the browser console for custom element or card errors, test templates in Home Assistant Developer Tools > Template, and clear the browser cache with a hard refresh or incognito window.

## Real-World Examples

### Quick Controls Dashboard Section

```json
{
  "type": "grid",
  "title": "Quick Controls",
  "cards": [
    {
      "type": "custom:mushroom-template-card",
      "primary": "All Doors",
      "secondary": "{% set doors = ['binary_sensor.front_door', 'binary_sensor.back_door'] %}\n{% set open = doors | select('is_state', 'on') | list | length %}\n{{ open }} / {{ doors | length }} open",
      "icon": "mdi:door",
      "icon_color": "{% if open > 0 %}red{% else %}green{% endif %}"
    },
    {
      "type": "tile",
      "entity": "climate.thermostat",
      "features": [
        {"type": "climate-hvac-modes", "hvac_modes": ["heat", "cool", "fan_only", "off"]},
        {"type": "target-temperature"}
      ]
    }
  ]
}
```

### Individual Light Cards

```json
{
  "type": "grid",
  "title": "Lights",
  "columns": 3,
  "cards": [
    {
      "type": "custom:mushroom-light-card",
      "entity": "light.office_studio",
      "name": "Office",
      "use_light_color": true,
      "show_brightness_control": true,
      "collapsible_controls": true
    }
  ]
}
```

### Full-Screen Vacuum Map

```json
{
  "type": "panel",
  "title": "Vacuum",
  "path": "vacuum-map",
  "cards": [
    {
      "type": "custom:xiaomi-vacuum-map-card",
      "vacuum_platform": "Tasshack/dreame-vacuum",
      "entity": "vacuum.dusty"
    }
  ]
}
```

## Common Commands Quick Reference

```bash
# Configuration
ha check
ssh root@homeassistant.local "ha core restart"

# Logs
ha logs --tail 50
ha logs --errors --tail 20

# State and services, preferred local helper
ha states
ha states everything_presence_one_28d74c
ha state entity.name
ha state entity.one entity.two
ha sample sensor.distance sensor.count sensor.speed -n 20 -i 1
ha call automation.trigger entity_id=automation.name
ha reload automations

# State and services, hass-cli fallback
hass-cli state list
hass-cli state get entity.name
hass-cli service call automation.reload
hass-cli service call automation.trigger --arguments entity_id=automation.name

# Deployment, only when authorized
git add . && git commit -m "..." && git push
ssh root@homeassistant.local "cd /config && git pull"
scp file.yaml root@homeassistant.local:/config/

# Dashboard deployment
scp .storage/lovelace.my_dashboard root@homeassistant.local:/config/.storage/
python3 -m json.tool .storage/lovelace.my_dashboard > /dev/null

# Quick authorized test cycle
scp automations.yaml root@homeassistant.local:/config/
ha reload automations
ha trigger automation.name
ha logs automation --tail 10
```

## Best Practices Summary

1. Check configuration before restart with ha core check.
2. Prefer reload over restart when possible.
3. Test automations manually after deployment.
4. Check logs for errors after every change.
5. Use scp for authorized rapid iteration and git for authorized final changes.
6. Verify outcomes; never assume success.
7. Use current docs for unfamiliar Home Assistant features.
8. Test templates in Developer Tools before adding to dashboards.
9. Validate JSON syntax before deploying dashboards.
10. Test on the actual target device for tablet dashboards.
11. Color-code dashboard status for fast visual scanning.
12. Commit only stable versions and only with explicit user authorization.

## Workflow Decision Tree

```text
Configuration change needed
├─ Is this investigation only?
│  ├─ Yes: read-only inspection only
│  └─ No: continue only within explicit user authorization
├─ Is this final and tested?
│  ├─ Yes: use authorized git workflow
│  └─ No: use authorized scp workflow
├─ Check configuration validity
├─ Deploy via authorized git pull or scp
├─ Needs restart?
│  ├─ Yes: restart only when authorized
│  └─ No: use targeted reload
├─ Verify logs
└─ Test outcome

Dashboard change needed
├─ Make local changes
├─ Validate JSON when applicable
├─ Deploy via scp only when authorized
├─ Refresh browser
├─ Test on target device
├─ Iterate until correct
└─ Commit only when stable and authorized
```
