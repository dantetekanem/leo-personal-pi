# Ruby Craft for Rails

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference when correctness depends on Ruby's object model, language semantics, metaprogramming, performance, concurrency, or durable object design.

Rails is Ruby, and the framework's elegance is a direct product of Ruby's design. An elite Rails engineer is first an elite Ruby engineer: fluent in the object model, precise about semantics, able to read the DSL-heavy style the Rails codebase is written in, and able to write code that survives for years. Write Ruby the way the Rails and Ruby core teams write it: plain, expressive, and built to last.

## Object Model and Semantics

Correctness depends on Ruby semantics. Master these before reaching for framework features:

- Everything is an object, including classes and modules. Know the difference between a class, a module, an eigenclass (singleton class), and a `Class`/`Module` instance, and where a method actually lives. Use `owner`, `ancestors`, `instance_method`, and `source_location` to find the real definition instead of guessing.
- Understand method lookup and `self` at every point: instance vs. class body, `class_eval` vs. `class << self`, `include` vs. `prepend` vs. `extend`, and how `super` walks the ancestor chain. Reach for `prepend` over alias-method chains when wrapping behavior.
- Blocks, procs, and lambdas differ in arity checking and `return`/`break`/`next` behavior. Prefer lambdas for strict arity and local return semantics; capture blocks with `&blk` only when forwarding or storing.
- Preserve keywords and blocks when wrapping APIs; Ruby 3 separated positional from keyword arguments, so use `ruby2_keywords` or explicit `**kwargs` forwarding and never splat-merge a hash into a keywords-expecting call blindly.
- Know the cost model: object allocation, frozen string literals, symbol vs. string identity, and when `Enumerable` chains allocate intermediate arrays. Use `# frozen_string_literal: true` and avoid wasteful intermediate collections on hot paths.
- A Ruby master never reasons about micro-performance from folklore — they measure with `benchmark/ips` and scale the conclusion to real traffic before acting. An allocation that is noise on a cold path is real GC and latency cost at high request volume, and an in-place form that looks like a premature optimization is often the deliberate choice on a measured hot path. They know modern Ruby optimizes many functional-looking forms (destructuring, slicing, iteration) far better than intuition suggests, while conveniences that feel free (block dispatch, `Symbol#to_proc`, chained `Enumerable` intermediate arrays) often carry hidden cost. The decision is always ownership plus a benchmark at representative load — never a reflex, immutable or mutating.
- Truthiness is only `nil` and `false`. Empty strings, zero, and empty collections are truthy. Handle `nil` deliberately; avoid `rescue nil` and blanket `&.` chains that hide the shape of your data.
- Rescue the narrowest exception at the boundary that can handle it. Never rescue `Exception` or `StandardError` to silence; rescue the specific class, and re-raise or report what you cannot actually handle.

## Idiomatic Ruby and Language Preference

Prefer the idiom the language and the community already chose:

- Favor `map`, `select`, `reject`, `reduce`/`inject`, `each_with_object`, `flat_map`, `partition`, `tally`, and `filter_map` over manual loops with accumulator arrays. Use `Enumerable` over hand-rolled iteration, and `Symbol#to_proc` (`map(&:name)`) where it reads cleanly.
- Use predicate (`empty?`, `any?`, `none?`, `present?`/`blank?` in Rails) and bang conventions honestly: predicates answer truth without side effects; bang methods signal the dangerous/raising/destructive variant. Know the concrete bang semantics, not just the naming convention: the in-place collection mutators (`uniq!`, `sort!`, `reverse!`, `gsub!`, `map!`, `compact!`) return `nil` when they made no change, so they corrupt any pipeline that uses their return value (`transform_values!(&:uniq!)`, `tap`, method chains). Reach for the non-bang form when the value flows onward, and the bang form only as a terminal statement on an owned receiver.
- Prefer `case`/`when`, pattern matching (`in`), and guard clauses over deep `if/else` nesting. Return early; keep the happy path unindented. Reach for the language's structural features — destructuring, pattern matching, splats, safe navigation — to express a value's shape directly, rather than building a result through mutation, index arithmetic, or a side-effecting chain the reader must decode.
- Use Ruby >= 1.9 hash syntax `{ a: :b }`, `&&`/`||` over `and`/`or`, safe navigation `&.` for a single optional hop, and `then`/`yield_self` to keep transformation chains readable.
- Reach for the standard library before a gem: `Set`, `Date`/`Time`, `Digest`, `SecureRandom`, `CSV`, `JSON`, `Forwardable` (for `def_delegators`), `SimpleDelegator`, `Comparable`, and `Data.define` / `Struct` for small immutable value objects. Trust the data-structure semantics CRuby actually guarantees: `Hash` (and therefore `Set`, which wraps one) is insertion-ordered, so deduplicating with a `Set` preserves first-seen order — that is dependable behavior, not an implementation accident. When you need membership testing inside a loop, use a `Set` or hash lookup (O(1)); a linear `Array#include?` scan per element turns the loop quadratic. (`Set` needs `require "set"` before Ruby 3.2.)
- Make objects comparable, enumerable, or printable by including `Comparable`/`Enumerable` and defining `<=>`/`each`, and by implementing `to_s`/`inspect`, `==`/`eql?`/`hash` for value semantics, and `dup`/`freeze` where immutability matters.

## DSL and Metaprogramming Design

Rails is a collection of internal DSLs (`has_many`, `validates`, `scope`, `before_action`, `attr_accessor`, `mattr_accessor`). Design your own with the same restraint:

- Build DSLs as thin, declarative class-level declarations that read as statements of fact about the domain. The declaration should gather intent; a small amount of well-tested machinery should execute it. Never let DSL sugar hide business logic.
- Keep metaprogramming in service of a clear public API. Accept `method_missing`, `define_method`, `class_eval`/`instance_eval`, `const_missing`, and runtime constant creation only behind an established extension point, with strong tests and explicit load-order awareness. Prefer ordinary methods whenever they communicate as well.
- Prefer `define_method` with a closure over `class_eval` string interpolation, which is hard to read and easy to inject into. Use `respond_to_missing?` alongside `method_missing` so reflection keeps working.
- Use module hooks (`included`, `prepended`, `extended`) and `ActiveSupport::Concern` for host capabilities, `class_attribute`/`mattr_accessor`/`thread_mattr_accessor` for configuration, and `ActiveSupport::DescendantsTracker`-style tracking only when you truly need subclass registration.
- Match file paths to constants and respect Zeitwerk. Do not paper over naming/load-order issues with ad hoc `require`s, and do not cache reloadable classes in long-lived objects or initializers (use `to_prepare` hooks instead).

## Durable, SOLID Ruby

Write code that is easy to delete, easy to change, and safe to run for years:

- Single responsibility at the object level: one reason to change per class/module, a small public API, and intention-revealing names in the language of the domain. Hide orchestration only when the caller should not wire internals.
- Depend on abstractions and duck types, not concrete collaborators. Inject what an object needs; program to protocols (`call`, `each`, `to_model`, `to_param`, `to_h`, `as_json`) rather than specific classes.
- Prefer composition (modules, delegation, small collaborating objects) over deep inheritance hierarchies. Inheritance is for a true "is-a" with shared implementation; reach for `Forwardable`/`SimpleDelegator` and mixins first.
- A Ruby master decides mutation by ownership and measurement, never by habit. Mutate in place when you own the object — no live aliases, the caller discards it — and a measured hot path justifies avoiding the allocation; return a new value when ownership is shared, unclear, or the path is cold. When you mutate a receiver you did not create, that ownership is part of the contract, so make it explicit. Freeze shared constants and configuration, and avoid mutable default arguments, class variables, and memoized class state, which are process-wide hazards under threaded servers and parallel workers.
- Make concurrency a design input, not an afterthought: CRuby's GVL does not remove races, so shared mutable state needs immutability, isolation, or database-enforced invariants, never hope.
- Choose the boring, readable solution. The clever one-liner that the next maintainer must decode is a liability; the plain method that reads like prose is an asset. But readable is not the same as naive: a clean chain that allocates several intermediate collections or scans linearly on a hot path is its own kind of cleverness tax. Readability, correctness, and cost are weighed together, at representative load.
