---
name: home-assistant-manager
description: Expert Home Assistant operations for User's local setup. Use whenever the user asks to inspect, fix, automate, analyze, tune, or manage Home Assistant, Proxmox-hosted HA services, the local ha helper CLI, Node-RED flows, device/entity state, dashboards, logs, recorder/history data, or long-range local HA data collection. Trigger even when the user only mentions HA, hass, homeassistant.local, Node-RED, automations, sensors, events/history, Proxmox, or the ha command.
---

# Home Assistant Manager

Expert Home Assistant management for User's local Home Assistant and Proxmox environment. This skill favors safe local control, Node-RED automation ownership, evidence-backed verification, and durable improvements to the `ha` helper over one-off API scripts.

## Operating stance

- Treat Home Assistant as production-impacting local infrastructure. Lights, locks, presence, sensors, dashboards, and recorder data can affect real people and devices.
- When User asks to investigate, check, diagnose, look into, or find out why, stay read-only. Inspect states, flows, logs, configs, history, and Proxmox status only; do not edit, deploy, reload, restart, install, or create files on the target.
- Make only the change User requested. Ask before restarts, reloads, flow deploys, remote file writes, DB copies, backups beyond the requested workflow, commits, pushes, installs, or production-impacting operations.
- Verify every claim with tool output. Do not say something works unless it was checked. If verification needs a physical observation, say exactly what User must check.
- Prefer local, bounded, repeatable tooling over ad hoc scripts. If a custom Home Assistant API/WebSocket call becomes a repeated workflow, extend the `ha` helper instead of continuing to make bespoke calls.

## Local environment facts

- Preferred CLI: `ha` at `~/.pi/agent/bin/ha`, copied to `~/.local/bin/ha`.
- Token source: `~/.pi/agent/mcp.json` by default. Use `HASS_TOKEN` only for an explicit token override. Do not rely on ambient `HA_TOKEN`.
- Home Assistant API default: `homeassistant.local:8123`; the helper resolves `homeassistant.local` to a cached local IP to avoid Ruby mDNS hangs. Overrides: `HA_LOCAL_IP`, `HA_RESOLVE_LOCAL=0`, `HA_TIMEOUT`, `HA_DEBUG=1`, `--debug`.
- Proxmox host SSH alias: `proxmox` -> `root@10.0.0.5:22` with `~/.ssh/proxmox_control`.
- Docker LXC SSH aliases: `proxmox-lxc` and `10.0.0.5` -> `root@10.0.0.5:2222`; Proxmox container `101`, name `docker`.
- Node-RED add-on access defaults through Proxmox to `http://10.10.10.100:1880`. Use `ha nodered ...`; do not call Node-RED add-on ingress manually unless the helper lacks a capability and User explicitly approved the exception.

## First checks

Use the smallest read-only checks that answer the question:

```bash
ha ping
ha config
ha states <query>
ha state sensor.one sensor.two
ha attrs sensor.entity
ha services <domain>
ha events
ha logs --errors --tail 50
ha check
```

For Proxmox context, stay read-only unless User asked for operations:

```bash
ssh -o BatchMode=yes proxmox true
ssh -o BatchMode=yes proxmox-lxc true
ssh proxmox "qm list"
ssh proxmox "pct list"
ssh proxmox-lxc "docker ps"
```

Use `--debug` when connection behavior is unclear; it must not expose tokens:

```bash
ha --debug ping
HA_DEBUG=1 ha state sensor.example
```

## Automations belong in Node-RED

User's durable convention: create and manage Home Assistant automations in Node-RED unless User explicitly asks for native HA YAML/UI automation.

Read-only inspection:

```bash
ha nodered settings
ha nodered tabs
ha nodered nodes <query>
ha nodered configs <query>
ha nodered flow <tab-or-id>
ha nodered connections <query>
ha nodered search <query>
ha nodered flows -j
```

Write workflow, only when User requested a flow change:

1. Inspect existing tabs, nodes, config nodes, connections, and relevant HA states.
2. Run `ha nodered backup` before any deploy. Keep the backup path for rollback.
3. Export full flows with `ha nodered flows -j` and generate a full replacement JSON. Preserve existing node IDs and tab IDs unless intentionally adding nodes.
4. Validate JSON with `jq empty FILE`.
5. Deploy with `ha nodered deploy @FILE --force` only after a backup exists.
6. Verify by re-reading targeted `ha nodered flow`, `ha nodered nodes`, and `ha nodered connections` output.
7. Verify affected HA entities with `ha state` and logs. For device behavior, ask User for physical confirmation when needed.
8. If migrating an old native HA automation into Node-RED, disable the original only after the Node-RED flow is deployed and verified. Do not delete it unless User asks.

Prefer idempotent Node-RED designs: current-state checks before service calls, explicit entity IDs, clear node names, comments documenting migrated automations, and separate trigger/condition/action nodes over opaque function blobs when native nodes can do the work.

## The `ha` helper is the abstraction boundary

Use `ha` before writing any Node/Ruby/Python/curl wrapper for common Home Assistant work.

Existing capabilities include:

```bash
ha states [query] [-j]
ha state ENTITY [ENTITY ...] [-j]
ha sample ENTITY [ENTITY ...] -n 20 -i 1 --summary all
ha attrs ENTITY
ha services [domain] [-j]
ha events [-j]
ha api GET|POST|DELETE /api/path [JSON|key=value ...]
ha ws MESSAGE_TYPE [JSON|key=value ...]
ha call domain.service key=value
ha trigger automation.entity_id
ha reload automations|scripts|scenes|templates|groups|themes|all
ha logs [--tail N] [--errors] [pattern]
ha core check
ha ssh <command>
ha nodered ...
```

If `ha` is missing a repeated workflow, upgrade `ha` instead of making custom calls forever:

1. Confirm the missing capability with `ha help` and the current helper source.
2. Add a small, documented subcommand with safe defaults, bounded output, token redaction, and clear errors.
3. Prefer command names that encode the workflow, such as `ha history`, `ha logbook`, `ha recorder`, `ha entities`, or a focused `ha nodered` subcommand.
4. Update help text and examples.
5. Copy the updated executable to both `~/.pi/agent/bin/ha` and `~/.local/bin/ha` if the source is not already symlinked.
6. Verify with `ha help`, one read-only happy-path command, and one safe error/empty-result case.
7. Document the new usage in the skill or durable memory only if it will matter in future sessions.

Do not use inline scripts as a shortcut for missing helper behavior unless User asks for a one-off script or the helper cannot reasonably be changed in the current scope.

## Historical data and local analysis

For current or short-window observation, prefer `ha state`, `ha attrs`, and `ha sample`.

For days or months of history, first define the exact question, entity IDs, date range, and aggregation needed. Never pull broad recorder data just to explore.

Safe REST history pattern:

```bash
ha api GET '/api/history/period/2026-06-01T00:00:00-04:00?end_time=2026-06-02T00:00:00-04:00&filter_entity_id=sensor.example,binary_sensor.example&minimal_response&no_attributes&significant_changes_only'
```

Use these controls by default:

- Always provide `filter_entity_id`; never query all entities over a long period.
- Use `minimal_response` and `no_attributes` unless attributes are the point of the analysis.
- Use `significant_changes_only` for high-frequency sensors unless raw updates are required.
- Chunk long ranges by day or week, one focused entity set at a time.
- Store raw outputs under a local temp/workspace path and summarize locally with `jq`, `rg`, `wc`, or purpose-built tooling. Do not paste huge JSON into the model context.
- Check byte size and row/event counts before loading data. If output is large, reduce the range, entity set, or fields.
- Throttle requests and keep them sequential unless there is a measured need for parallelism.
- Remember recorder retention may not contain months of data. Verify the oldest available data before promising long-range analysis.

For logbook-style questions, prefer entity-filtered logbook windows:

```bash
ha api GET '/api/logbook/2026-06-01T00:00:00-04:00?end_time=2026-06-02T00:00:00-04:00&entity=binary_sensor.example'
```

For event-type discovery, `ha events` lists current event types/listeners; it is not months of event history. If User truly needs recorder event history across months, avoid hammering the live system. Prefer a bounded helper command or an offline/local database analysis path, and ask before copying or querying large recorder databases.

Good local analysis outputs are small: counts per day/hour, transitions, durations, first/last occurrence, anomaly windows, and specific examples. Avoid returning raw months of state rows unless User explicitly asks.

## Reload and restart choices

Prefer the smallest safe operation:

- Node-RED flow changes: `ha nodered deploy @FILE --force` after backup, then verify flows and entities.
- Automations/scripts/scenes/templates/groups/themes: `ha reload <target>` when applicable.
- Configuration check: `ha check` or `ha core check` before restart-worthy changes.
- Full Home Assistant restart only when required and explicitly authorized.
- Proxmox VM/LXC/container operations only when explicitly authorized and after identifying the correct VM/container with read-only commands.

## Dashboards and UI

For Lovelace/dashboard work, inspect before editing. Validate JSON/YAML locally before deploy. Dashboard file changes may only need browser refresh, while dashboard registry changes often require a Home Assistant restart. Ask before remote writes and restarts.

Keep dashboard output tablet-friendly: large touch targets, minimal scrolling, clear status colors, and simple cards unless custom cards are already installed and verified.

## Verification checklist

After an authorized change, report concrete evidence:

- What was changed and where.
- Backup path, if a Node-RED deploy occurred.
- Validation command result, such as `jq empty`, `ha check`, or `ha core check`.
- Reload/deploy command result.
- Read-back evidence from `ha nodered ...`, `ha state`, `ha attrs`, and/or `ha logs`.
- Remaining physical verification User must perform, if device behavior cannot be observed locally.

## Common pitfalls

- Do not create native Home Assistant automations when Node-RED is the expected automation layer.
- Do not deploy Node-RED without `ha nodered backup`; POST `/flows` replaces the full flow set.
- Do not restart Home Assistant or Proxmox guests to “be safe.” Ask first and use targeted reloads when possible.
- Do not dump unfiltered history/logbook/recorder data for months. Narrow, chunk, summarize, and keep raw data local.
- Do not expose Home Assistant bearer tokens in debug output, logs, commands, or reports.
- Do not trust entity names from memory. Confirm current entity IDs with `ha states`, Node-RED nodes, or registry/config inspection.
- Do not declare presence, lighting, or device automation success from config alone. Verify state transitions or get User confirmation.
