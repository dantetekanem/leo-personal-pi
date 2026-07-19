# TypeScript Craft Reference

> Return to [SKILL.md](../SKILL.md) for core workflow, boundaries, and reference-selection rules.

Use these defect classes for compiler configuration, boundary types, narrowing, generics, declaration output, and escape hatches. Match the repository's installed TypeScript version because flag behavior and library declarations evolve.

---

## 1. Strictness enabled partially and assumed complete

**Failure mode.** A project says it is “strict” because one flag is on, while implicit `any`, nullable values, unsafe function parameters, or unchecked indexed reads remain accepted. Different packages inherit different effective configs.

**Concrete example.** The root has `"strict": true`, but a leaf `tsconfig` sets `strictNullChecks: false`; exported code returns `undefined` where callers expect `User`.

**Expert rule.** Inspect the *effective* config for the package being changed. Use `strict` as the baseline because it enables the strict-family checks, then audit explicit overrides and version-sensitive additions such as `noUncheckedIndexedAccess` and `exactOptionalPropertyTypes`. Tightening flags in an established repository is a compatibility change: scope it deliberately and fix contracts rather than scattering casts.

**Evidence.** TypeScript Handbook, [Everyday Types — Strictness](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#strictness), and TSConfig reference, [`strict`](https://www.typescriptlang.org/tsconfig/strict.html), [`noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html), and [`exactOptionalPropertyTypes`](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html).

## 2. Implicit or explicit `any` erases a boundary

**Failure mode.** An untyped parameter, parsed payload, or third-party value becomes `any`; unsafe property access and calls then propagate without further compiler evidence.

**Concrete example.** `function handle(payload) { return payload.user.id.toFixed() }` compiles with implicit `any`, and a malformed JSON payload fails deep in UI rendering.

**Expert rule.** Enable `noImplicitAny`, type exported parameters and returns, and receive untrusted values as `unknown`. Narrow or parse once near ingress, then pass a precise domain type inward. Use `any` only at a proven interop seam where operations truly cannot be modeled, keep the seam tiny, and document the lost guarantee. `any` is not a flexible object type; it disables checking.

**Evidence.** TypeScript Handbook, [Everyday Types — `any`](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#any), [Functions — Parameter Type Annotations](https://www.typescriptlang.org/docs/handbook/2/functions.html#parameter-type-annotations), and TSConfig reference, [`noImplicitAny`](https://www.typescriptlang.org/tsconfig/noImplicitAny.html).

## 3. Absence represented ambiguously

**Failure mode.** `null`, `undefined`, missing property, and a present property whose value is `undefined` are treated as interchangeable. Callers cannot tell whether a field may be omitted, cleared, or not loaded.

**Concrete example.** `PatchUser` uses `nickname?: string | undefined`; spreading it into persistence clears a nickname when the caller intended “leave unchanged.” An indexed lookup is typed `User` even when the key is missing.

**Expert rule.** With `strictNullChecks`, model absence explicitly and narrow before use. Use optional properties for omission and unions for explicit nullable states. Consider `exactOptionalPropertyTypes` when omission and `undefined` differ in the domain, and `noUncheckedIndexedAccess` when dictionary misses must be handled. The domain decides whether `null` and `undefined` are distinct; TypeScript should preserve that decision.

**Evidence.** TypeScript Handbook, [Everyday Types — `strictNullChecks` on](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#strictnullchecks-on), [Object Types — Optional Properties](https://www.typescriptlang.org/docs/handbook/2/objects.html#optional-properties), and TSConfig reference, [`exactOptionalPropertyTypes`](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html).

## 4. Narrowing replaced by a cast

**Failure mode.** Code receives `unknown` or a union and immediately asserts the desired type. The compiler becomes quiet without runtime evidence.

**Concrete example.** `const user = JSON.parse(body) as User` is followed by `user.roles.includes('admin')`; an object with no `roles` passes compile time and crashes.

**Expert rule.** Narrow using runtime facts: `typeof`, equality, truthiness with care, `in`, `instanceof`, discriminants, or a user-defined predicate whose implementation actually checks the claimed shape. Parse at system boundaries and return a validated type or a typed failure. Reserve `as` for facts the runtime or library guarantees but TypeScript cannot express, and keep the assertion adjacent to that evidence.

**Evidence.** TypeScript Handbook, [Narrowing — `typeof` type guards](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#typeof-type-guards), [`in` operator narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#the-in-operator-narrowing), [`instanceof` narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#instanceof-narrowing), and [Using type predicates](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates).

## 5. Truthiness narrowing drops valid domain values

**Failure mode.** `if (value)` is used to mean “present,” but the domain permits `0`, `false`, or `""`. A valid value follows the absent branch.

**Concrete example.** `if (discount) apply(discount)` skips a legitimate zero discount, or `if (message)` hides an intentionally empty controlled-input value.

**Expert rule.** Narrow the condition the domain actually means. Use `value != null` when excluding both `null` and `undefined`, an explicit discriminant for state, or a dedicated predicate. Truthiness is correct only when all falsy members are semantically absent. TypeScript documents that truthiness narrowing follows JavaScript's falsy set; it cannot infer your product meaning.

**Evidence.** TypeScript Handbook, [Narrowing — Truthiness narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#truthiness-narrowing) and [Equality narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#equality-narrowing).

## 6. Union variants overlap and invalid states remain expressible

**Failure mode.** Several optional booleans describe one lifecycle. Impossible combinations compile, and render logic forgets a state.

**Concrete example.** `{isLoading?: boolean, data?: User, error?: Error}` permits loading with data and error simultaneously. UI branches disagree about which flag wins.

**Expert rule.** Use a discriminated union with one literal tag and variant-specific fields, such as `{status: 'loading'}` | `{status: 'success'; data: User}` | `{status: 'error'; error: Error}`. Switch on the discriminant and use `never` in the default branch when exhaustive handling is part of the contract. Keep discriminants stable at API boundaries.

**Evidence.** TypeScript Handbook, [Narrowing — Discriminated unions](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#discriminated-unions) and [Exhaustiveness checking](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#exhaustiveness-checking).

## 7. Generic parameter does not express a relationship

**Failure mode.** A function adds `<T>` to look reusable, but `T` appears only once or does not connect inputs to output. Callers gain no information and inference becomes misleading.

**Concrete example.** `function parse<T>(text: string): T` promises any caller-selected type without validation. `parse<User>('null')` compiles even though implementation returns arbitrary JSON.

**Expert rule.** Introduce a type parameter only when it relates two or more positions or preserves a caller's specific type. Prefer `unknown` for arbitrary parsed data and require a decoder/guard to produce `T`. Use the fewest type parameters possible and push them down to the member being related. A generic is a quantified contract, not a cast supplied by the caller.

**Evidence.** TypeScript Handbook, [Functions — Type Parameters](https://www.typescriptlang.org/docs/handbook/2/functions.html#type-parameters), [Guidelines for Writing Good Generic Functions — Push Type Parameters Down](https://www.typescriptlang.org/docs/handbook/2/functions.html#push-type-parameters-down), and [Use Fewer Type Parameters](https://www.typescriptlang.org/docs/handbook/2/functions.html#use-fewer-type-parameters).

## 8. Generic constraints wider or narrower than the operation

**Failure mode.** An unconstrained generic performs property access that is not valid for all `T`, or a constraint requires an entire object shape when the implementation needs only one key.

**Concrete example.** A picker accepts `key: string` and indexes `obj`, losing the relationship between valid keys and returned values. Another helper constrains to a large `Entity` interface merely to read `id`.

**Expert rule.** Encode the exact capability required. Use `K extends keyof T` for keyed access so `obj[key]` returns `T[K]`; constrain to `{id: string}` when only `id` is needed. Let inference recover the narrow caller type. Avoid default generic arguments that silently widen inference unless the default is part of the public API design.

**Evidence.** TypeScript Handbook, [Generics — Generic Constraints](https://www.typescriptlang.org/docs/handbook/2/generics.html#generic-constraints) and [Using Type Parameters in Generic Constraints](https://www.typescriptlang.org/docs/handbook/2/generics.html#using-type-parameters-in-generic-constraints).

## 9. Callback variance hides an input-safety bug

**Failure mode.** A callback that accepts only a subtype is assigned where callers may pass the full base type. Runtime receives a value the callback cannot handle.

**Concrete example.** A handler expecting `Dog` is accepted as `(animal: Animal) => void`; the producer later invokes it with a `Cat` and the handler calls `bark()`.

**Expert rule.** Keep `strictFunctionTypes` enabled and design callback parameter types from the producer's right to call them. Do not “fix” a variance error by casting the callback. Methods have different compatibility behavior for historical reasons, so inspect whether the API uses method syntax or function properties. Explicit `in`/`out` variance annotations are advanced tools for exceptional recursive comparisons; TypeScript says never write them merely to force structural matching.

**Evidence.** TypeScript Handbook, [Type Compatibility — Comparing two functions](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#comparing-two-functions), [Generics — Variance Annotations](https://www.typescriptlang.org/docs/handbook/2/generics.html#variance-annotations), and TSConfig reference, [`strictFunctionTypes`](https://www.typescriptlang.org/tsconfig/strictFunctionTypes.html).

## 10. Public API inferred from incidental implementation

**Failure mode.** An exported function or component leaks private classes, overly wide literals, environment-specific globals, or a complex inferred conditional type. A harmless internal refactor becomes a consumer type break.

**Concrete example.** An exported factory's inferred return includes a private helper class. Declaration emit names an inaccessible internal type or changes substantially when implementation is reorganized.

**Expert rule.** Annotate exported parameters and return types when they define a supported boundary. Prefer domain names and minimal structural contracts over exposing internal storage. Use overloads only when callers truly receive different relationships that a union cannot express, and keep the implementation signature hidden from consumers. The exact annotation threshold is engineering judgment: favor explicitness at package/public boundaries and inference inside cohesive modules.

**Evidence.** TypeScript Handbook, [Functions — Function Overloads](https://www.typescriptlang.org/docs/handbook/2/functions.html#function-overloads), [Overload Signatures and the Implementation Signature](https://www.typescriptlang.org/docs/handbook/2/functions.html#overload-signatures-and-the-implementation-signature), and [Declaration Files — Library Structures](https://www.typescriptlang.org/docs/handbook/declaration-files/library-structures.html).

## 11. Declaration output treated as an incidental build artifact

**Failure mode.** Source typechecks internally but emitted `.d.ts` files are missing, reference private paths, or expose a shape different from package exports. JavaScript consumers run, while TypeScript consumers cannot import the supported API.

**Concrete example.** `declaration: true` emits declarations under `dist/src`, but `package.json` points `types` to `dist/index.d.ts`. A barrel exports runtime values without exporting the corresponding public types.

**Expert rule.** For a library, treat declaration emit as a product surface. Align `declaration`, `declarationDir`, `rootDir`, package `types`/`exports`, and source entry points. Build declarations and inspect the emitted public files, not only the compiler exit code. Use `emitDeclarationOnly` when another tool emits JavaScript. Test a consumer import when export maps or module modes are involved.

**Evidence.** TypeScript Handbook, [Creating `.d.ts` Files from `.js` files](https://www.typescriptlang.org/docs/handbook/declaration-files/dts-from-js.html), [Publishing — Including declarations in your npm package](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html#including-declarations-in-your-npm-package), and TSConfig reference, [`declaration`](https://www.typescriptlang.org/tsconfig/declaration.html) and [`emitDeclarationOnly`](https://www.typescriptlang.org/tsconfig/emitDeclarationOnly.html).

## 12. Type assertion used to redesign the value

**Failure mode.** `as` claims two weakly related shapes are equivalent, or a double assertion (`as unknown as T`) crosses an impossible conversion. Runtime representation never changed.

**Concrete example.** A DOM element is asserted to `HTMLCanvasElement` without checking which selector matched, or an API object is asserted from `{id: number}` to `{id: string}`.

**Expert rule.** Remember that assertions are removed at compile time and perform no validation or conversion. Prefer control-flow narrowing, checked parsing, or an actual transform. If a DOM/query contract cannot be expressed, assert the narrowest fact after checking existence and expected kind. Treat double assertions as a named, reviewed interop debt with evidence outside the type system.

**Evidence.** TypeScript Handbook, [Everyday Types — Type Assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions) and [Narrowing — Control flow analysis](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#control-flow-analysis).

## 13. Compiler suppression outlives the defect

**Failure mode.** `@ts-ignore` hides a line forever, even after the underlying error changes or disappears. Future incompatible operations accumulate under the same comment.

**Concrete example.** A library typing bug is suppressed with `@ts-ignore`; after upgrading, the original mismatch is fixed but a new wrong argument is also ignored.

**Expert rule.** Fix the contract first. If a temporary compiler escape hatch is unavoidable, prefer `@ts-expect-error` with a short reason and an issue/version reference because it reports when no error remains. Scope it to one line and add a removal trigger. Do not use a suppression to avoid modeling untrusted input or to make a public declaration emit.

**Evidence.** TypeScript Handbook release notes, [TypeScript 3.9 — `// @ts-expect-error` Comments](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-9.html#ts-expect-error-comments) and [Choosing `ts-ignore` or `ts-expect-error`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-9.html#ts-ignore-or-ts-expect-error).

## 14. Structural compatibility mistaken for domain equivalence

**Failure mode.** Two unrelated domain values with the same properties are freely assignable. A value from the wrong tenant, unit, or lifecycle crosses a boundary because TypeScript compares members rather than declared names.

**Concrete example.** `UserId` and `InvoiceId` are both strings, so a function accepts the wrong ID. Two classes with the same public members are compatible despite different semantic ownership.

**Expert rule.** Use structural typing where shape compatibility is intended. For semantically distinct primitives at critical boundaries, introduce opaque/branded types or constructors that validate and brand them; this is an engineering judgment layered on TypeScript's documented structural model. Remember that private/protected members affect class compatibility and that object-literal excess-property checks are not general nominal typing.

**Evidence.** TypeScript Handbook, [Type Compatibility — Starting out](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#starting-out), [Private and protected members in classes](https://www.typescriptlang.org/docs/handbook/type-compatibility.html#private-and-protected-members-in-classes), and [Object Types — Excess Property Checks](https://www.typescriptlang.org/docs/handbook/2/objects.html#excess-property-checks).

## 15. Compile-time type confused with runtime validation

**Failure mode.** An API payload, environment variable, local-storage value, or message event is declared as a domain type and trusted. TypeScript types vanish at runtime, so the external producer is never checked.

**Concrete example.** `await response.json() as CheckoutSuccess` makes the success path compile; a server error object reaches code that assumes `orderId` exists.

**Expert rule.** Treat every untyped runtime boundary as `unknown`, validate its discriminants and required values, and return a typed success/error result. Keep compile-time types synchronized with the validator or parser already used by the repository. TypeScript's narrowing can use the runtime facts after validation, but the annotation itself creates no facts.

**Evidence.** TypeScript Handbook, [Narrowing — Using type predicates](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates) and [Everyday Types — Type Assertions](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#type-assertions).

## 16. Type-system mismatch in a host repository

**Failure mode.** A contributor adds TypeScript to a Flow-owned source file or rewrites annotations because TypeScript is familiar, creating an unrelated migration and bypassing local gates.

**Concrete example.** A change to React core converts `ReactHooks.js` to `.ts` even though neighboring modules and the reconciler use Flow types.

**Expert rule.** Match the host's type system, compiler version, and conventions. React core uses Flow annotations; contribute Flow there and run the repository's Flow checks. Use TypeScript craft for TypeScript-owned applications and packages, but never impose it across a framework boundary without an approved migration. This is an explicit engineering rule derived from repository ownership, not a claim that one type system is universally superior.

**Evidence.** React source, [`ReactHooks.js` uses Flow syntax](https://github.com/facebook/react/blob/172742b419bad2a79ac375c0d5ee15c7ac66bff2/packages/react/src/ReactHooks.js#L9-L31), and TypeScript Handbook, [TypeScript for the New Programmer — Erased Types](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html#erased-types).
