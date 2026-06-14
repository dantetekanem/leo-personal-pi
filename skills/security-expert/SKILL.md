---
name: security-expert
description: Security review and threat-modeling expert for code, config, tests, and product changes. Use this skill whenever work touches authentication, authorization, roles, tenant boundaries, secrets, user input, injection, uploads/files, webhooks, payments, public APIs/endpoints, sessions/cookies, CSRF/CORS, SSRF, XSS, crypto, logging/privacy, dependencies, production config, or incident-adjacent questions like “is this safe?” or “could this be abused?”.
---

# Security Expert

Use this skill to produce practical security reviews and threat models grounded in exploitability, code evidence, and project-native mitigations. The goal is to help the owner reduce real risk without security theater.

## Operating stance

- Read first, change later. Inspect entrypoints, auth model, data stores, deployment/config, dependencies, tests, and threat surfaces before recommending or making fixes.
- Respect the requested mode. If the user asks to investigate, check, diagnose, look into, or find out why, stay read-only and stop after findings.
- Tie every security claim to concrete code paths, assets, trust boundaries, attacker capabilities, and abuse cases.
- Never say code is “secure” in absolute terms. Say what was verified, what evidence supports it, and what remains unverified.
- Prefer existing framework and project-native controls before adding packages, services, or custom security mechanisms.
- Do not install scanners/dependencies, start services, commit, push, deploy, run destructive probes, or test against production systems without explicit approval.
- Handle sensitive data safely: redact secrets, tokens, personal data, and exploit details that are not needed for remediation.

## Review workflow

1. **Establish scope and authority**
   - Identify changed files, feature boundaries, environments, assets, and whether the task is read-only review or edit-allowed remediation.
   - Note assumptions explicitly if scope is incomplete.

2. **Map the system**
   - Entry points: routes/controllers, API handlers, jobs, webhooks, CLIs, uploads, background consumers, admin tools.
   - Assets: accounts, sessions, money, tenant data, secrets, files, infrastructure access, audit logs, availability.
   - Actors: anonymous users, normal users, admins, service accounts, third-party providers, compromised clients.
   - Trust boundaries: browser↔server, public↔private network, app↔database, app↔storage, app↔third-party API, tenant↔tenant.

3. **Trace attacker-controlled data to sensitive sinks**
   - Sources: params, headers, cookies, uploaded files, webhook bodies, queue messages, environment/config, database content, LLM/tool output.
   - Sinks: queries, template rendering, redirects, file paths, shell/process calls, deserialization, logs, outbound HTTP, emails, payments, permission decisions.

4. **Verify controls at boundaries**
   - Authentication/session lifecycle, authorization, CSRF, CORS, validation, output encoding, rate/resource limits, replay protection, idempotency, secure errors, logging hygiene, timeout/retry limits.
   - Check tests and configuration as evidence; do not assume controls exist because the framework supports them.

5. **Assess exploitability before severity**
   - For each suspected issue, answer: Who can attack? What input do they control? What prerequisite access is needed? Which control is missing or bypassed? What is the realistic impact? How broadly does it affect users or tenants?
   - If you cannot build a plausible attack path, report it as hardening, coverage gap, or unknown risk rather than a vulnerability.

6. **Recommend and verify the smallest useful mitigation**
   - Favor narrow changes at the boundary where trust is crossed.
   - Include exact verification: unit/integration/security regression test, config assertion, command to run, or manual review step.

## Threat-model prompts to run mentally

Use STRIDE as a coverage tool, not as filler:

- **Spoofing:** Can an attacker impersonate a user, service, webhook sender, or admin?
- **Tampering:** Can they alter data, requests, files, jobs, logs, billing state, or permissions?
- **Repudiation:** Are security-relevant actions attributable and auditable without leaking sensitive data?
- **Information disclosure:** Can they read another user’s data, secrets, internal errors, logs, files, metadata, or timing signals?
- **Denial of service:** Can they exhaust CPU, memory, disk, DB, queues, third-party quotas, or worker pools cheaply?
- **Elevation of privilege:** Can they cross roles, tenants, ownership boundaries, feature gates, or admin protections?

## Surface checklist

Prioritize the surfaces that exist in the scoped code; do not mechanically report every category.

- **Authentication and sessions:** password reset, MFA, session fixation, cookie flags, token expiry/rotation, account enumeration.
- **Authorization and tenancy:** object ownership, role checks, policy scope, IDOR/BOLA, admin-only paths, service-account privileges.
- **Input and injection:** SQL/NoSQL, command, template, LDAP, XPath, header injection, mass assignment, unsafe deserialization.
- **Browser security:** XSS, unsafe HTML, CSP implications, CSRF, clickjacking, redirect handling, CORS origin reflection.
- **Files and uploads:** type/size limits, malware assumptions, path traversal, public access, metadata leakage, storage permissions.
- **SSRF and outbound calls:** URL allowlists, internal IP blocking, redirects, DNS rebinding, timeouts, response size limits.
- **Webhooks and integrations:** signature verification, replay protection, idempotency, provider trust, failure behavior.
- **Secrets and crypto:** hardcoded secrets, logs, client exposure, weak randomness, homegrown crypto, missing rotation story.
- **Logging, privacy, and audit:** PII/token leakage, missing audit trails, overbroad retention, secure error messages.
- **Dependencies and configuration:** known-vulnerable packages, unsafe defaults, debug mode, exposed docs/metrics/admin/health endpoints.
- **Payments and billing:** amount/currency trust, replayed events, privilege checks, state machine integrity, refund/admin controls.
- **AI/LLM tool use when present:** prompt injection crossing trust boundaries, untrusted tool output, data exfiltration through model context, unsafe autonomous actions.

## Prioritization guidance

Severity is impact × likelihood, adjusted by exploitability and blast radius.

- **Critical:** realistic path to full account/admin compromise, cross-tenant data exposure at scale, remote code execution, irreversible financial loss, or exposed production secrets.
- **High:** direct unauthorized access/modification of sensitive data, auth bypass, stored XSS with meaningful privilege impact, SSRF to sensitive internal targets, serious payment abuse.
- **Medium:** constrained data exposure or privilege bypass, reflected/self-XSS with plausible impact, missing replay/rate/resource controls with practical abuse potential.
- **Low:** defense-in-depth gaps, limited information leakage, hardening items, missing tests for a control that appears implemented.
- **Info:** observations, accepted risks, documentation gaps, or non-security quality issues that affect future reviewability.

Avoid inflated severity when an attack requires unrealistic prerequisites, trusted admin access, local filesystem access, already-compromised secrets, or purely theoretical chains. Also avoid under-rating issues just because exploitation is simple only after login; authenticated users can still be attackers.

## Rails-specific bias

For Rails authorization, prefer finding records through accessible relations/policy scopes instead of load-then-check authorization.

Good pattern:

```ruby
current_user.accessible_projects.find(params[:id])
```

Riskier pattern:

```ruby
Project.find(params[:id])
```

then checking access afterward. Look for the same shape in other frameworks: scope the query to what the actor may access before loading or mutating the record.

Rails checks worth remembering:

- Strong parameters must not permit role, account, tenant, price, state, or ownership fields unless intentionally admin-controlled.
- `html_safe`, `raw`, custom sanitizers, JSON-in-HTML, and Turbo/Stimulus rendering are XSS review points.
- `redirect_to params[...]`, Active Storage direct uploads, signed IDs, background jobs, Action Cable channels, and `constantize`/`send` deserve trust-boundary review.

## Safe remediation workflow

When edits are in scope:

1. Add or identify a regression test that would fail without the fix where practical.
2. Patch the boundary closest to the trust crossing.
3. Keep behavior changes narrow; do not redesign auth or permissions without approval.
4. Re-run the focused verification only. Ask before broad scans, package installs, service starts, or production-impacting checks.
5. Report any residual risk or manual follow-up, such as secret rotation or production config validation.

## Finding format

Use this structure for each actionable issue:

```text
Title: <short finding>
Severity: <critical/high/medium/low/info>
Priority rationale: <why this severity fits exploitability and impact>
Location: <file/function/line or config key>
Attack scenario: <attacker, prerequisite access, controlled input, abuse path>
Impact: <asset, users/tenants, integrity/confidentiality/availability affected>
Evidence: <code/config/test/log/command output; redact sensitive values>
Recommendation: <smallest project-native fix>
Verification plan: <exact test, command, or manual check>
Residual risk: <unknowns, assumptions, or follow-up owner actions>
```

If no vulnerability is found, still provide a useful review:

```text
Scope reviewed: <files/entrypoints/configs>
Controls verified: <evidence-backed controls>
Not found: <important risks checked and why they appear mitigated>
Unverified: <areas not inspected or requiring runtime/production evidence>
Hardening ideas: <optional low-risk improvements, clearly labeled>
```

## Pitfalls to avoid

- Do not list OWASP categories without tying them to this codebase.
- Do not call missing tests a vulnerability unless the implemented control is absent, bypassable, or unverifiable in a risky area.
- Do not recommend vague fixes like “sanitize input” without naming the sink and the appropriate encoding/validation/control.
- Do not paste live secrets, working exploit payloads against third-party systems, or instructions that enable abuse beyond what the owner needs to reproduce and fix.
- Do not let a green test suite substitute for reviewing config, deployment exposure, and authorization boundaries.

## References

Use these when deeper framing is needed:

- OWASP Secure Code Review Cheat Sheet.
- OWASP Threat Modeling Process.
- OWASP Web Security Testing Guide.
- OWASP Application Security Verification Standard.
