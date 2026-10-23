---
name: ruby-post-processing
description: Post-process completed Ruby and Rails implementation changes for expressive naming, coherent methods and mixins, idiomatic flow, and comments limited to necessary business rationale. Preserve behavior and the application's architecture.
---

# Ruby post-processing

*Draft for review*

Apply this skill after implementation. Work on the selected Ruby changes, using callers, nearby code, tests, and the formatter as context. Improve how the implementation reads while preserving its behavior and public contracts. Test-style changes are a separate task.

The comparisons show **bad** code with avoidable friction, **good** code that states its intention, and **great** code whose composition makes that intention easier to follow. “Great” depends on context: keep the good version when another abstraction would add work for the reader.

## Name the operation precisely

Let the receiver supply context and the method describe its action. Distinguish selection, construction, persistence, and scheduling. Use the application's vocabulary and retain words that explain a meaningful difference.

**Bad — the names conceal both selection and scheduling.**

```ruby
def deliver
  get_data.each do |u|
    handle(u)
  end
end

private
  def get_data
    account.users.active.where(digest_enabled: true)
  end

  def handle(user)
    DigestMailer.daily(user).deliver_later
  end
```

**Good — the action is explicit.**

```ruby
def deliver
  recipients = account.users.active.where(digest_enabled: true)

  recipients.each do |recipient|
    DigestMailer.daily(recipient).deliver_later
  end
end
```

**Great — meaningful private names make the public method read as intent.**

```ruby
def deliver
  digest_recipients.each do |recipient|
    enqueue_digest_for(recipient)
  end
end

private
  def digest_recipients
    account.users.active.where(digest_enabled: true)
  end

  def enqueue_digest_for(recipient)
    DigestMailer.daily(recipient).deliver_later
  end
```

The query, iteration, public method, and return contract stay intact. Prefer the great version when recipient selection and scheduling are useful concepts in the surrounding class. Before renaming or removing private methods, check direct, symbolic, and reflective callers.

## Compose methods around meaningful steps

Keep a method at a coherent level of detail. Extract a helper when its name expresses a useful concept and its implementation distracts from the caller. Keep obvious sequences together; method length is not a target.

**Bad — nested branches obscure one combined condition.**

```ruby
def acceptable_response?(response)
  if response.code == "200"
    if response.content_type == "text/html"
      response.content_length.to_i <= MAX_BYTES
    else
      false
    end
  else
    false
  end
end
```

**Good — the condition reads directly.**

```ruby
def acceptable_response?(response)
  response.code == "200" &&
    response.content_type == "text/html" &&
    response.content_length.to_i <= MAX_BYTES
end
```

**Great — a larger response-handling class gains a vocabulary for its checks.**

```ruby
def acceptable_response?(response)
  successful_response?(response) &&
    html_response?(response) &&
    acceptable_size?(response)
end

private
  def successful_response?(response)
    response.code == "200"
  end

  def html_response?(response)
    response.content_type == "text/html"
  end

  def acceptable_size?(response)
    response.content_length.to_i <= MAX_BYTES
  end
```

Evaluation order and short-circuiting remain unchanged. Use the good version for an isolated check; the great version earns its helpers when those concepts clarify the class. Changing the treatment of a missing content length would be a separate behavioral change.

## Give mixins a cohesive capability

A mixin should describe one capability and read naturally through its receiving object. It may serve one class. Reuse and line-count reduction are insufficient reasons to combine unrelated behavior.

These excerpts assume the host already defines an `archived` scope and an `archived?` predicate. The great version gathers those existing pieces into their capability; it does not introduce new behavior.

**Bad — the module's name says nothing about its responsibility.**

```ruby
module Report::Helpers
  extend ActiveSupport::Concern

  def archive
    update! archived_at: Time.current
  end
end
```

**Good — a focused name and only the machinery the module needs.**

```ruby
module Report::Archivable
  def archive
    update! archived_at: Time.current
  end
end
```

**Great — related declarations and behavior live together.**

```ruby
module Report::Archivable
  extend ActiveSupport::Concern

  included do
    scope :archived, -> { where.not(archived_at: nil) }
  end

  def archive
    update! archived_at: Time.current
  end

  def archived?
    archived_at.present?
  end
end
```

Update the host's include and remove relocated definitions when applying this extraction. Preserve declaration timing, overrides, and callback behavior. This operation refreshes the timestamp on repeated calls; retain the application's actual contract.

Use plain modules for behavior that needs no inclusion machinery. Use `ActiveSupport::Concern` when hooks, class-method composition, or concern dependencies help. Make host dependencies understandable through names, arguments, and inclusion structure. Check collisions, visibility, `super`, and inclusion order before changing composition. Keep broader architectural changes outside this pass.

## Express a result directly

Prefer expressions that show the transformation without procedural bookkeeping. Retain an intermediate variable when its name explains a useful concept. This example assumes `heading_parts` returns an array and blank elements should be omitted.

**Bad — bookkeeping dominates a simple transformation.**

```ruby
def heading
  parts = []

  heading_parts.each do |part|
    unless part.blank?
      parts << part
    end
  end

  parts.join(" — ")
end
```

**Good — the transformation is visible.**

```ruby
def heading
  parts = heading_parts.reject(&:blank?)
  parts.join(" — ")
end
```

**Great — the idiom expresses the same policy directly.**

```ruby
def heading
  heading_parts.compact_blank.join(" — ")
end
```

Here the original code already removes blank values. Replacing `compact` with `compact_blank` elsewhere would change behavior. Use the project's supported Ruby and Rails APIs.

Let `if` and `case` return their selected value when a temporary exists only to hold the result. Use guards for preconditions and `if/else` for meaningful alternatives. Keep ternaries and modifier conditions short; avoid nested cleverness.

## Choose blocks by their return contract

Use `tap` when retaining the receiver is the intention and `then` when returning a transformation. Keep explicit steps when the intermediate object deserves a name.

**Bad — a vague local and redundant return obscure the object being built.**

```ruby
def create_preview(attributes)
  result = previews.create!(attributes)
  result.prepare
  return result
end
```

**Good — the sequence and return value are clear.**

```ruby
def create_preview(attributes)
  preview = previews.create!(attributes)
  preview.prepare
  preview
end
```

**Great — construction, preparation, and the retained result form one expression.**

```ruby
def create_preview(attributes)
  previews.create!(attributes).tap(&:prepare)
end
```

Prefer the good version if the operation grows into several meaningful steps. `then(&:prepare)` would return the preparation result and is not equivalent. Choose shorthand and parentheses for clarity, preserving block binding and precedence.

## Let code explain what; comment on necessary business reasons

Improve names and structure before adding explanation. Remove comments that narrate statements, repeat names, or compensate for unclear expressions. Keep a comment only when it explains established business intent or the reason for a domain constraint that the code cannot adequately communicate.

**Bad — the comment repeats the condition.**

```ruby
# Return if the invoice is settled.
return if invoice.settled?
```

**Good — the code explains the operation itself.**

```ruby
return if invoice.settled?
```

**Great — when the business rule needs preserving, explain its reason.**

```ruby
# Issued amounts remain fixed; corrections use credit notes.
return if invoice.settled?
```

Use the great version only if that policy is established and relevant here. Otherwise, the good version is complete. Never invent a business reason to justify a comment. Keep necessary rationale brief and adjacent to the rule; preserve machine-interpreted directives as executable configuration.

## Review the whole change

Group related methods and use blank lines where the thought changes. Follow the project's formatter instead of creating unrelated formatting churn. Preserve declaration order where callbacks, inclusion hooks, aliases, or visibility depend on it.

Check substantive rewrites for return values, truthiness, evaluation order, mutation, exceptions, and block control flow. Preserve query loading, ordering, callbacks, and transaction boundaries. For example, memoizing false instead of recomputing it, replacing `destroy_all` with `delete_all`, or changing `map(&:id)` to `pluck(:id)` can alter behavior despite looking cleaner.

Run relevant existing tests for method and expression changes, plus targeted lint checks where available. Keep verification proportionate; whitespace does not need new tests. If equivalence is uncertain, retain the original code and flag the issue.

Read the final diff for edits that add navigation without meaning. Leave already clear code alone. Report the meaningful improvements and verification briefly, including any execution limits.
