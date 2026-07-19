# Rails Framework Contribution Reference

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference when the target is `rails/rails` or a major Rails framework or engine and the work must meet the upstream merge bar.

## Contribution posture

When the target is `rails/rails` or a major engine (turbo-rails, stimulus-rails, solid_queue, kamal), the merge bar is different from app work. The reviewer is a core maintainer whose scarcest resource is review time, and the change lands in a codebase used by millions of apps, so compatibility and restraint matter more than cleverness.

## Contribution workflow

- Anchor bug reports on an **executable test case** built from the official bug-report templates (`guides/bug_report_templates/*.rb`: `active_record.rb`, `action_controller.rb`, `action_view.rb`, `active_job.rb`, `active_storage.rb`, `action_mailer.rb`, `generic.rb`, and `benchmark.rb` for performance claims). These run standalone with `ruby file.rb`.
- One concern per pull request. No drive-by refactors, renames, or formatting sweeps. Purely cosmetic patches that add nothing to stability, functionality, or testability are rejected upstream.
- Include a test that **fails without the change and passes with it**. This is non-negotiable for a mergeable fix.
- For new features, get feedback first (rubyonrails-core forum / an issue) before large implementation. Active Support core-extension changes are generally rejected and belong in Ruby itself.
- Prefer a single squashed commit with a clear message: short summary (~50 chars), body wrapped at 72, the *why* self-contained without needing to visit a link.

## Tests, warnings, and benchmarks

- Active Record changes must pass across the adapter matrix, not just SQLite: run `cd activerecord && bundle exec rake test:sqlite3` and, when the change is adapter-sensitive, `test:mysql2`, `test:trilogy`, and `test:postgresql` (build DBs first with `rake db:postgresql:build` / `db:mysql:build`).
- Run the component suite for the framework you touched (`cd actionpack && bin/test`, etc.) and use the seed/line filters for focused runs.
- Do not introduce new Ruby warnings; CI runs with strict warnings. Reproduce locally with `RAILS_STRICT_WARNINGS=1`.
- For performance-sensitive changes, benchmark with `benchmark-ips` (use the `benchmark.rb` template) and share the script and results in the commit message.
- Run RuboCop on the files you modified before submitting, and follow the surrounding source's style (two-space indent, `{ a: :b }`, `&&`/`||` over `and`/`or`, `class << self`, `assert_not` over `refute`).

## Compatibility, deprecations, and changelog

- Never break existing applications without a deprecation cycle. To remove behavior, first warn while keeping it: `ActiveRecord.deprecator.warn(<<-MSG.squish)` (use the owning framework's deprecator), then remove in a later release.
- To change default behavior, add a **framework default**: a config accessor on the framework (defaulting to the old behavior), wire the new value into `Configuration#load_defaults` for the target version, and add a commented entry to the `new_framework_defaults_X_Y.rb.tt` template.
- Add a CHANGELOG entry **to the top** of the modified framework's CHANGELOG when adding/removing a feature or adding a deprecation, ending with your name. Bug fixes and refactorings generally do not get an entry.
- Update the surrounding API docs and the relevant guide when behavior changes.

## API boundaries

- Rails is a framework of public contracts. Methods marked `:nodoc:` or nested under `private` are internal and free to change; the documented public API is not. Do not expand the public surface casually, and do not treat internal helpers as stable extension points for apps.
- Keep changes minimal and idiomatic. The best upstream patch is usually the smallest one that a maintainer can merge with confidence and backport cleanly.

## Current documentation

- Rails Guides: https://guides.rubyonrails.org/
- Rails API: https://api.rubyonrails.org/
- Rails Doctrine: https://rubyonrails.org/doctrine
- Rails Release Notes: https://guides.rubyonrails.org/releases.html
- Active Record Querying: https://guides.rubyonrails.org/active_record_querying.html
- Active Record Migrations: https://guides.rubyonrails.org/active_record_migrations.html
- Rails Security Guide: https://guides.rubyonrails.org/security.html
- Autoloading/Zeitwerk: https://guides.rubyonrails.org/autoloading_and_reloading_constants.html
- Ruby Docs: https://docs.ruby-lang.org/
