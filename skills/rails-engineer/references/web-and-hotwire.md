# Rails Web and Hotwire Reference

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference when work touches controllers, routing, params, response semantics, server-rendered views, forms, Turbo, Stimulus, or Rails-integrated JavaScript.

## Controllers and HTTP

- Prefer resourceful routes and conventional actions. Custom member/collection routes should express real domain verbs.
- Controllers may call model/domain APIs directly when behavior is clear. That is normal Rails.
- Controllers should make scoped loading, authorization, mutation, and response obvious.
- Load records through authorized/account/tenant scopes: `current_account.projects.find(params[:id])`, not global fetch then check.
- Nested routes imply ownership. Verify the parent actually scopes the child.
- Use strong params or `params.expect` according to installed Rails version and app convention. Broad empty hashes remain dangerous.
- Params are strings unless cast. Hidden fields and JS validation are untrusted.
- Destructive actions should not be GET. Prefer forms/`button_to` for method and CSRF semantics.
- Use `flash.now` for render, `flash` for redirect, and status codes consistent with nearby controllers.
- API behavior must preserve auth, error shape, serialization, pagination, status codes, and rate limits.

## Views, Forms, Turbo, and Stimulus

- Prefer server-rendered HTML and Rails helpers before client-side state machinery.
- Turbo Drive is navigation. Turbo Frames are scoped replacement/lazy-loading/in-place flows. Turbo Streams are server-rendered fragment updates and broadcasts.
- Debug Turbo by checking request format, response status, content type, frame ID, stream action/target, DOM ID, redirects, and valid HTML/stream content.
- Turbo form failures usually need appropriate failure status such as unprocessable entity and response targeting the expected frame/stream.
- Use `turbo_frame_tag`, `.turbo_stream.erb`, `render turbo_stream:`, `turbo_stream_from`, and broadcasts when they match app convention.
- Stimulus should remain small DOM behavior: actions, targets, values, classes. Do not move domain state into JavaScript because it feels easier.
- Preserve progressive enhancement and accessibility where feasible.
- Custom `fetch`/XHR must send the Rails CSRF token. Use existing helpers or `@rails/request.js` if present.
- Import maps, jsbundling, TypeScript, JSX, and bundlers are app-stack decisions. Inspect before advising.
