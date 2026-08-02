# Summary of every document

This file lists **every markdown file in the knowledge base**, deeply nested ones included, with a
one-line summary of what each holds. Read it first: it is the fastest way to learn the whole contents
at once and to pick the few documents a task actually needs, without opening a directory at a time.
The section `README.md` files carry the fuller framing and the reasoning behind each grouping — this
is an index, not a second set of introductions.

Every document added, removed, renamed, or repurposed is reflected here in the same change, per
[AGENTS.md](AGENTS.md). An entry that no longer matches its document is a bug in the change that made
it stale.

## Top level

- [README.md](README.md) — what the knowledge base is, why the ecosystem's documentation is
  consolidated here, and a summary of every top-level directory.
- [AGENTS.md](AGENTS.md) — the authoring and maintenance rules for the whole base: the
  synchronization rule, verifying against the source, document-the-present, the rules that follow from
  this repository being public, how links are written, registering a document, the prose mechanics, and
  the committing rule.
- [summary.md](summary.md) — this file.
- [sibling-projects.md](sibling-projects.md) — the member projects, their repositories, the revision
  of each to read, and the rules for finding a sibling locally versus linking to it.

## `cgp/` — the CGP library

- [cgp/README.md](cgp/README.md) — what this member section documents, why prose beats reading the
  proc-macro source, and how its five parts divide.
- [cgp/AGENTS.md](cgp/AGENTS.md) — the rules for documenting `cgp`: what the synchronization rule
  lands on here (including propagating a change to the skill), the authoring conventions, which rules
  govern which directory, the reference document template and its syntax-grammar notation, the rule
  that a reference document covers every form its parser accepts, what a concept and a guide each owe,
  the rule that a document says which context shape its examples wire, and how to review a document.

### `cgp/reference/` — one document per construct

- [cgp/reference/README.md](cgp/reference/README.md) — the construct index: a grouped summary of
  every documented construct, the directory layout, and where a new document goes.
- [cgp/reference/cargo-cgp.md](cgp/reference/cargo-cgp.md) — CGP's error toolchain from a user's
  side: what `cargo cgp check` rewrites, how to read its `[CGP-Exxx]` output, and the `expand`
  command.

#### `cgp/reference/macros/`

- [async_trait.md](cgp/reference/macros/async_trait.md) — rewrite a trait's `async fn` declarations
  into the lint-clean `-> impl Future` form CGP's async methods use.
- [blanket_trait.md](cgp/reference/macros/blanket_trait.md) — generate a blanket impl from a trait
  with default methods and supertrait dependencies.
- [cgp_auto_dispatch.md](cgp/reference/macros/cgp_auto_dispatch.md) — generate a handler that
  dispatches over an extensible-data input from a per-type trait.
- [cgp_auto_getter.md](cgp/reference/macros/cgp_auto_getter.md) — define a getter as a blanket impl
  over `HasField`, keyed by the method name.
- [cgp_component.md](cgp/reference/macros/cgp_component.md) — the foundational macro: turn one trait
  into a component (consumer trait, provider trait, marker, blanket impls).
- [cgp_computer.md](cgp/reference/macros/cgp_computer.md) — define a `Computer` provider from a
  function, with the promotion tables that answer the rest of the handler family.
- [cgp_fn.md](cgp/reference/macros/cgp_fn.md) — define a single-implementation capability as a
  blanket-impl trait straight from a function; also documents `#[impl_generics]`.
- [cgp_getter.md](cgp/reference/macros/cgp_getter.md) — define a getter as a full component, so its
  source field is chosen by wiring.
- [cgp_impl.md](cgp/reference/macros/cgp_impl.md) — write a provider in consumer-trait shape, the
  idiomatic form; includes the `#[cgp_impl(Self)]` direct-impl form.
- [cgp_namespace.md](cgp/reference/macros/cgp_namespace.md) — define a reusable, inheritable wiring
  table; also documents the `#[prefix(...)]` registration attribute, and which of
  `delegate_components!`'s shared body forms mean something here.
- [cgp_new_provider.md](cgp/reference/macros/cgp_new_provider.md) — `#[cgp_provider]` that also
  declares the provider struct.
- [cgp_producer.md](cgp/reference/macros/cgp_producer.md) — define a `Producer` provider from an
  input-free function.
- [cgp_provider.md](cgp/reference/macros/cgp_provider.md) — write a provider by implementing the
  provider trait directly, with `IsProviderFor` derived from the same bounds.
- [cgp_type.md](cgp/reference/macros/cgp_type.md) — define an abstract-type component, layering a
  `UseType` impl over `#[cgp_component]`.
- [check_components.md](cgp/reference/macros/check_components.md) — assert at compile time that a
  context can use each listed component; covers `#[check_providers]` and `#[check_trait]`.
- [delegate_and_check_components.md](cgp/reference/macros/delegate_and_check_components.md) — wire
  and check in one macro, which of the shared syntax forms the check derivation reads, the
  `#[check_params]`/`#[skip_check]` per-entry attributes and how they merge on a list key, and why the
  macro is wrong for an aggregate provider.
- [delegate_components.md](cgp/reference/macros/delegate_components.md) — build a context's wiring
  table, exhaustively: the `new` aggregate form and generic lists, the three operators (`:`, `->`,
  `=>`), the three key forms with the `[…]`/`{…}` path groups, the two value forms, the three
  statements (`open`, `namespace`, `for`), and how they all combine in one block.
- [path.md](cgp/reference/macros/path.md) — the type-level path macro behind namespaces and
  redirected lookups.
- [product.md](cgp/reference/macros/product.md) — the type-level list type `Product!` and its
  value-level `product!`.
- [sum.md](cgp/reference/macros/sum.md) — the type-level sum `Sum!`, the dual of `Product!`.
- [symbol.md](cgp/reference/macros/symbol.md) — the type-level string used as a field-name tag.

#### `cgp/reference/attributes/`

- [derive_delegate.md](cgp/reference/attributes/derive_delegate.md) — generate the `UseDelegate`
  dispatcher impl for a component generic over a parameter (the legacy dispatch path).
- [extend.md](cgp/reference/attributes/extend.md) — add supertrait bounds to a generated trait, the
  preferred way to import a capability supertrait.
- [extend_where.md](cgp/reference/attributes/extend_where.md) — add `where` predicates to a
  `#[cgp_fn]` trait's own definition rather than only its impl.
- [implicit.md](cgp/reference/attributes/implicit.md) — source a function argument from a same-named
  context field, with the clone/`as_str`/option/slice/`MRef`/mutable access rules.
- [use_provider.md](cgp/reference/attributes/use_provider.md) — complete an inner provider's bound in
  a higher-order provider by filling in the context argument.
- [uses.md](cgp/reference/attributes/uses.md) — import `Self` capability bounds, reading like a `use`
  statement.
- [use_type.md](cgp/reference/attributes/use_type.md) — import an abstract associated type as a bare
  alias, including the equality form that pins it to a concrete type.

#### `cgp/reference/derives/`

- [derive_build_field.md](cgp/reference/derives/derive_build_field.md) — builder support for a record.
- [derive_cgp_data.md](cgp/reference/derives/derive_cgp_data.md) — the umbrella extensible-data
  derive.
- [derive_cgp_record.md](cgp/reference/derives/derive_cgp_record.md) — the struct-specific extensible-
  data derive.
- [derive_cgp_variant.md](cgp/reference/derives/derive_cgp_variant.md) — the enum-specific extensible-
  data derive.
- [derive_extract_field.md](cgp/reference/derives/derive_extract_field.md) — extractor support for a
  variant.
- [derive_from_variant.md](cgp/reference/derives/derive_from_variant.md) — generic construction of an
  enum from a named variant.
- [derive_has_field.md](cgp/reference/derives/derive_has_field.md) — per-field accessors keyed by
  `Symbol!`/`Index`.
- [derive_has_fields.md](cgp/reference/derives/derive_has_fields.md) — the whole-struct or whole-enum
  field-list view.

#### `cgp/reference/components/`

- [can_raise_error.md](cgp/reference/components/can_raise_error.md) — raising and wrapping a source
  error into the context's abstract error type.
- [computer.md](cgp/reference/components/computer.md) — the synchronous, infallible transform and its
  by-reference and async variants.
- [handler.md](cgp/reference/components/handler.md) — the general async, fallible, error-aware
  computation component.
- [has_error_type.md](cgp/reference/components/has_error_type.md) — the abstract error type every
  fallible CGP capability names.
- [has_runtime.md](cgp/reference/components/has_runtime.md) — the abstract runtime type and its
  accessor.
- [has_type.md](cgp/reference/components/has_type.md) — CGP's built-in abstract-type component.
- [producer.md](cgp/reference/components/producer.md) — the input-free production component.
- [runner.md](cgp/reference/components/runner.md) — the task-running components `CanRun`/`CanSendRun`.
- [try_computer.md](cgp/reference/components/try_computer.md) — the fallible computer.

#### `cgp/reference/providers/`

- [chain_getters.md](cgp/reference/providers/chain_getters.md) — compose getters to reach a field on a
  nested context.
- [dispatch_combinators.md](cgp/reference/providers/dispatch_combinators.md) — the variant-matching
  and record-assembling routing providers.
- [error_providers.md](cgp/reference/providers/error_providers.md) — `RaiseFrom`, `ReturnError`,
  `DebugError`, and the other error-component backends.
- [handler_combinators.md](cgp/reference/providers/handler_combinators.md) — `ComposeHandlers`,
  `PipeHandlers`, `ReturnInput`, and the `Promote*` lifts.
- [monad_providers.md](cgp/reference/providers/monad_providers.md) — `PipeMonadic`, `BindOk`,
  `BindErr`, and the identity/ok/err monad markers.
- [redirect_lookup.md](cgp/reference/providers/redirect_lookup.md) — re-route a component lookup along
  a type-level path; the namespace mechanism.
- [use_context.md](cgp/reference/providers/use_context.md) — satisfy a provider trait through the
  context's own consumer impl, and its circular-dependency trap.
- [use_default.md](cgp/reference/providers/use_default.md) — select a component's default method
  bodies.
- [use_delegated_type.md](cgp/reference/providers/use_delegated_type.md) — resolve an abstract type
  through a lookup table.
- [use_delegate.md](cgp/reference/providers/use_delegate.md) — dispatch on a generic parameter through
  an inner table (the legacy form of `open`).
- [use_field.md](cgp/reference/providers/use_field.md) — implement a getter by reading a named context
  field.
- [use_field_ref.md](cgp/reference/providers/use_field_ref.md) — the `AsRef`/`AsMut` variant of
  `UseField`.
- [use_fields.md](cgp/reference/providers/use_fields.md) — the getter provider keyed by the method
  name.
- [use_type.md](cgp/reference/providers/use_type.md) — supply a concrete type for an abstract-type
  component.
- [with_provider.md](cgp/reference/providers/with_provider.md) — adapt a foundational provider into a
  named component, with the `WithType`/`WithField`/`WithContext` aliases.

#### `cgp/reference/traits/`

- [can_use_component.md](cgp/reference/traits/can_use_component.md) — the context-side check that a
  context both delegates a component and satisfies its provider's dependencies.
- [cast.md](cgp/reference/traits/cast.md) — the structural casts `CanUpcast`, `CanDowncast`, and
  `CanBuildFrom`.
- [default_namespace.md](cgp/reference/traits/default_namespace.md) — the namespace default-resolution
  traits; also documents `#[default_impl(...)]`.
- [delegate_component.md](cgp/reference/traits/delegate_component.md) — the per-context type-level
  table mapping a component key to a provider.
- [extract_field.md](cgp/reference/traits/extract_field.md) — the incremental-extractor trait family.
- [from_variant.md](cgp/reference/traits/from_variant.md) — generic construction of an enum from a
  named variant.
- [has_builder.md](cgp/reference/traits/has_builder.md) — the incremental-builder trait family.
- [has_field.md](cgp/reference/traits/has_field.md) — tag-keyed field access, with `HasFieldMut` and
  the provider-side `FieldGetter`.
- [has_fields.md](cgp/reference/traits/has_fields.md) — the whole-shape field representation and its
  conversions.
- [is_provider_for.md](cgp/reference/traits/is_provider_for.md) — the marker supertrait that surfaces
  a provider's missing dependency by name.
- [map_type.md](cgp/reference/traits/map_type.md) — the present/absent/void type-mapping markers and
  transforms.
- [monad.md](cgp/reference/traits/monad.md) — the trait layer behind monadic handler composition.
- [optional_fields.md](cgp/reference/traits/optional_fields.md) — the builder/extractor traits for
  optional and defaulted fields.
- [product_ops.md](cgp/reference/traits/product_ops.md) — the type-level product operations
  `AppendProduct`, `ConcatProduct`, and `MapFields`.
- [static_format.md](cgp/reference/traits/static_format.md) — recovering type-level strings and paths
  back into runtime data.

#### `cgp/reference/types/`

- [chars.md](cgp/reference/types/chars.md) — the type-level character list behind `Symbol`.
- [cons.md](cgp/reference/types/cons.md) — the `Cons`/`Nil` product (record) list spine.
- [either.md](cgp/reference/types/either.md) — the `Either`/`Void` sum (variant) list spine.
- [field.md](cgp/reference/types/field.md) — a value paired with its type-level name tag.
- [index.md](cgp/reference/types/index.md) — a type-level natural number, tagging tuple-struct fields.
- [life.md](cgp/reference/types/life.md) — a lifetime lifted into a type.
- [mref.md](cgp/reference/types/mref.md) — an owned-or-borrowed getter value.
- [path_cons.md](cgp/reference/types/path_cons.md) — the type-level path list behind `Path!`.

### `cgp/concepts/` — cross-cutting overviews

- [README.md](cgp/concepts/README.md) — the concept catalog, and how a concept differs from a
  reference document, an example, and a guide.
- [abstract-types.md](cgp/concepts/abstract-types.md) — associated types each context chooses for
  itself, and why a determined type propagates nowhere while a parameter propagates everywhere.
- [aggregate-providers.md](cgp/concepts/aggregate-providers.md) — bundling component wirings into a
  reusable provider, and why such a bundle is a provider rather than a context.
- [check-traits.md](cgp/concepts/check-traits.md) — why wiring is lazy and how a compile-time
  assertion makes its failures readable.
- [coherence.md](cgp/concepts/coherence.md) — what Rust's coherence rules forbid, the
  incoherent-impl-plus-local-wiring strategy CGP uses, and why the number of independent choices
  available depends on who owns the wired type.
- [consumer-and-provider-traits.md](cgp/concepts/consumer-and-provider-traits.md) — the trait duality
  at the heart of CGP, and why its worked example is a value context rather than the more common
  environmental one.
- [dispatching.md](cgp/concepts/dispatching.md) — routing extensible-data inputs to per-field and
  per-variant handlers.
- [extensible-records.md](cgp/concepts/extensible-records.md) — building and reading a struct by its
  named fields, and the extensible builder pattern.
- [extensible-variants.md](cgp/concepts/extensible-variants.md) — constructing and deconstructing an
  enum by its named variants, and the extensible visitor pattern.
- [handlers.md](cgp/concepts/handlers.md) — the computation family and its sync/async, fallible, and
  input-passing axes.
- [higher-order-providers.md](cgp/concepts/higher-order-providers.md) — providers parameterized by
  other providers.
- [impl-side-dependencies.md](cgp/concepts/impl-side-dependencies.md) — dependency injection through a
  blanket impl's `where` clause, in its three legs: capabilities, values, and types — the last being why
  an abstract type needs no generic parameter.
- [implicit-arguments.md](cgp/concepts/implicit-arguments.md) — writing providers as ordinary
  functions whose arguments come from context fields.
- [modular-error-handling.md](cgp/concepts/modular-error-handling.md) — the error type, its
  construction, and its detail as three independent wiring decisions.
- [modularity-hierarchy.md](cgp/concepts/modularity-hierarchy.md) — the ladder from one blanket impl
  to per-type-per-provider wiring, the value-versus-environmental context and self-versus-parameter
  target axes that decide a rung, why vanilla Rust idiomatically supports only one of the three shapes,
  and how to pick the lowest rung.
- [monadic-handlers.md](cgp/concepts/monadic-handlers.md) — chaining handlers that short-circuit
  through a monad.
- [namespaces.md](cgp/concepts/namespaces.md) — reusable, inheritable wiring tables as CGP's preset
  mechanism.
- [send-bounds.md](cgp/concepts/send-bounds.md) — restoring the `Send` guarantee an async trait method
  drops.
- [type-level-dsls.md](cgp/concepts/type-level-dsls.md) — encoding a small language as types and
  interpreting it at compile time.

### `cgp/guides/` — which construct to choose

- [README.md](cgp/guides/README.md) — the guide catalog plus a summary table condensing every
  recommendation into one cheat-sheet.
- [choosing-a-component-shape.md](cgp/guides/choosing-a-component-shape.md) — what goes in `Self` and
  whether the capability targets `Self` or a parameter, with the promotion refactoring worked and the
  two traps: a parameter is not always a target, and per-application choice needs no parameter.
- [sizing-a-component.md](cgp/guides/sizing-a-component.md) — group the items one provider choice decides
  together, the two cases where several belong, the three costs of grouping unrelated decisions, and
  splitting a trait that has along the axis its contexts differ on.
- [capability-supertraits.md](cgp/guides/capability-supertraits.md) — prefer `#[extend]` over native
  `:` supertrait syntax.
- [debugging.md](cgp/guides/debugging.md) — reach for `cargo-cgp` first, then trace a wiring failure
  by hand: reading the error's shape, moving it to the wiring site, reducing it, and a decoder table.
- [declaring-dependencies.md](cgp/guides/declaring-dependencies.md) — prefer `#[uses]` and
  `#[use_provider]` over hand-written `where` bounds.
- [dispatching-per-type.md](cgp/guides/dispatching-per-type.md) — prefer the `open` statement or a
  namespace over a `UseDelegate` table.
- [importing-abstract-types.md](cgp/guides/importing-abstract-types.md) — prefer `#[use_type]` aliases
  over a supertrait plus `Self::Type`.
- [naming-a-type-dependency.md](cgp/guides/naming-a-type-dependency.md) — infer a needed type from a
  field with `#[impl_generics]`, climb to an abstract type when it must be named or two types must
  agree, and never thread it as a generic parameter on the capability.
- [namespaces-and-prefixes.md](cgp/guides/namespaces-and-prefixes.md) — keep a growing wiring table
  short with prefixes, namespaces, and per-type defaults, worked as a refactoring.
- [reading-context-fields.md](cgp/guides/reading-context-fields.md) — prefer an `#[implicit]` argument
  over a getter trait.
- [writing-providers.md](cgp/guides/writing-providers.md) — prefer `#[cgp_impl]` in consumer-trait
  shape over the inside-out provider forms.

### `cgp/errors/` — post-codegen compile errors, by class

- [README.md](cgp/errors/README.md) — the catalog: why these errors are hard, the hidden-versus-
  surfaced axis it is built around, what belongs here, and the index of every class.
- [AGENTS.md](cgp/errors/AGENTS.md) — the rules: never paste verbatim output, record the three facts a
  tool needs, the document template, backing every class with a fixture, and gathering an error with a
  sub-agent.
- [hidden/unsatisfied-dependency.md](cgp/errors/hidden/unsatisfied-dependency.md) — an unmet
  impl-side dependency reached by a direct consumer-method call, where the compiler hides the cause
  behind `E0599`.
- [checks/check-trait-failure.md](cgp/errors/checks/check-trait-failure.md) — the same unmet
  dependency forced through a check, where `IsProviderFor` surfaces the concrete missing bound.
- [checks/higher-order-provider-layer.md](cgp/errors/checks/higher-order-provider-layer.md) — a
  checked higher-order provider, and how the diagnostic's shape names the failing layer.
- [checks/ordinary-trait-bound.md](cgp/errors/checks/ordinary-trait-bound.md) — an impl-side
  dependency that is an ordinary Rust trait, unmet by the concrete type a context supplies.
- [checks/unregistered-namespace-path.md](cgp/errors/checks/unregistered-namespace-path.md) — a
  component routed through a namespace to a path nothing binds.
- [checks/verbose-cascade.md](cgp/errors/checks/verbose-cascade.md) — one deep mistake reported at
  every dependent provider, and how to find the single root cause.
- [wiring/conflicting-wiring.md](cgp/errors/wiring/conflicting-wiring.md) — the same key or name wired
  twice, producing `E0119` or `E0428`.
- [wiring/namespace-forwarding-conflict.md](cgp/errors/wiring/namespace-forwarding-conflict.md) — two
  blanket forwarding impls that each cover every key.
- [wiring/namespace-inheritance-cycle.md](cgp/errors/wiring/namespace-inheritance-cycle.md) — a
  namespace parent chain that loops, caught eagerly at the definitions.
- [wiring/namespace-override-conflict.md](cgp/errors/wiring/namespace-override-conflict.md) — an entry
  overriding a key its namespace already claims.
- [wiring/orphan-rule.md](cgp/errors/wiring/orphan-rule.md) — registering into a foreign namespace
  with no local type (`E0210`/`E0117`).
- [wiring/unconstrained-generic.md](cgp/errors/wiring/unconstrained-generic.md) — a per-entry generic
  that never reaches the key (`E0207`).
- [wiring/wiring-cycle.md](cgp/errors/wiring/wiring-cycle.md) — a delegation that chases its own tail,
  overflowing the solver.
- [lowering/ill-formed-generated-type.md](cgp/errors/lowering/ill-formed-generated-type.md) — a
  shorthand lowered into a bound naming an unsized type.
- [lowering/unresolved-imported-type.md](cgp/errors/lowering/unresolved-imported-type.md) — a
  `#[use_type]` import naming an associated type its trait does not declare (`E0576`).
- [lowering/out-of-scope-generated-name.md](cgp/errors/lowering/out-of-scope-generated-name.md) — an
  `#[impl_generics]` parameter named in the capability's own signature, where only the generated impl
  declares it (`E0433`), plus the abstract type shadowing its own bound (`E0404`).
- [error_codes/README.md](cgp/errors/error_codes/README.md) — the forward index from a `rustc` error
  code to its meaning and the CGP classes that emit it.
- [error_codes/cargo-cgp-codes.md](cgp/errors/error_codes/cargo-cgp-codes.md) — a pointer entry for
  `cargo-cgp`'s own `[CGP-Exxx]` codes and where they are defined.
- [error_codes/e0117.md](cgp/errors/error_codes/e0117.md) — the orphan rule for a wholly foreign impl.
- [error_codes/e0119.md](cgp/errors/error_codes/e0119.md) — conflicting implementations (coherence).
- [error_codes/e0207.md](cgp/errors/error_codes/e0207.md) — an unconstrained type parameter on an impl.
- [error_codes/e0210.md](cgp/errors/error_codes/e0210.md) — the orphan rule for an uncovered type
  parameter.
- [error_codes/e0275.md](cgp/errors/error_codes/e0275.md) — overflow evaluating a requirement.
- [error_codes/e0271.md](cgp/errors/error_codes/e0271.md) — a type mismatch resolving an
  associated-type projection.
- [error_codes/e0277.md](cgp/errors/error_codes/e0277.md) — a trait bound is not satisfied, including
  the `Sized` form.
- [error_codes/e0404.md](cgp/errors/error_codes/e0404.md) — a trait was expected in a bound position
  but the name resolved to something else.
- [error_codes/e0425.md](cgp/errors/error_codes/e0425.md) — an identifier is not found in this scope.
- [error_codes/e0433.md](cgp/errors/error_codes/e0433.md) — a path's leading segment names an
  undeclared type, crate, or module.
- [error_codes/e0428.md](cgp/errors/error_codes/e0428.md) — a name defined more than once in one scope.
- [error_codes/e0576.md](cgp/errors/error_codes/e0576.md) — an associated item the trait does not
  declare.
- [error_codes/e0599.md](cgp/errors/error_codes/e0599.md) — a method exists but its trait bounds were
  not satisfied.

### `cgp/implementation/` — how the macros are built

- [README.md](cgp/implementation/README.md) — the implementation catalog plus the cross-cutting notes
  every reviewer needs: leading-generic insertion and lifetime ordering, keeping the generic kinds
  apart, spans for the compiler and the IDE, parsing with `parse_internal!`, and hygiene.
- [AGENTS.md](cgp/implementation/AGENTS.md) — the rules for this tree: what an implementation document
  is for, the per-kind document templates, the Tests and Snapshots sections, Known issues, and how to
  document the ways an expansion can fail to compile.

#### `cgp/implementation/entrypoints/` — one document per macro

- [async_trait.md](cgp/implementation/entrypoints/async_trait.md) — the `async fn` → `-> impl Future`
  rewrite.
- [blanket_trait.md](cgp/implementation/entrypoints/blanket_trait.md) — the blanket impl generated
  from a trait with default methods.
- [cgp_auto_dispatch.md](cgp/implementation/entrypoints/cgp_auto_dispatch.md) — generating a
  dispatching handler from a per-type trait.
- [cgp_auto_getter.md](cgp/implementation/entrypoints/cgp_auto_getter.md) — a getter as a blanket impl
  over `HasField`.
- [cgp_component.md](cgp/implementation/entrypoints/cgp_component.md) — the foundational
  component-definition macro and its `preprocess → eval → to_items` pipeline.
- [cgp_computer.md](cgp/implementation/entrypoints/cgp_computer.md) — a `Computer` provider from a
  function.
- [cgp_fn.md](cgp/implementation/entrypoints/cgp_fn.md) — a blanket-impl trait from a function, with
  `#[implicit]` argument lowering.
- [cgp_getter.md](cgp/implementation/entrypoints/cgp_getter.md) — a getter component, adding the
  `UseField`/`UseFields` provider impls.
- [cgp_impl.md](cgp/implementation/entrypoints/cgp_impl.md) — lowering consumer-style syntax into a
  provider impl.
- [cgp_namespace.md](cgp/implementation/entrypoints/cgp_namespace.md) — reusable, inheritable wiring
  tables via `RedirectLookup`.
- [cgp_new_provider.md](cgp/implementation/entrypoints/cgp_new_provider.md) — `#[cgp_provider]` with
  the provider struct also declared.
- [cgp_producer.md](cgp/implementation/entrypoints/cgp_producer.md) — a `Producer` provider from a
  function.
- [cgp_provider.md](cgp/implementation/entrypoints/cgp_provider.md) — passing a provider-trait impl
  through and deriving its `IsProviderFor`.
- [cgp_type.md](cgp/implementation/entrypoints/cgp_type.md) — an abstract-type component, reusing the
  `cgp_component` pipeline and adding `UseType`.
- [check_components.md](cgp/implementation/entrypoints/check_components.md) — the compile-time wiring
  assertions.
- [delegate_and_check_components.md](cgp/implementation/entrypoints/delegate_and_check_components.md)
  — wiring and checking in one macro.
- [delegate_components.md](cgp/implementation/entrypoints/delegate_components.md) — the context wiring
  table and its mapping and statement grammar.
- [derive_build_field.md](cgp/implementation/entrypoints/derive_build_field.md) — the record-builder
  derive.
- [derive_cgp_data.md](cgp/implementation/entrypoints/derive_cgp_data.md) — the umbrella
  extensible-data derive.
- [derive_cgp_record.md](cgp/implementation/entrypoints/derive_cgp_record.md) — the struct-side
  extensible-data derive.
- [derive_cgp_variant.md](cgp/implementation/entrypoints/derive_cgp_variant.md) — the enum-side
  extensible-data derive.
- [derive_extract_field.md](cgp/implementation/entrypoints/derive_extract_field.md) — the
  variant-extractor derive.
- [derive_from_variant.md](cgp/implementation/entrypoints/derive_from_variant.md) — the
  variant-construction derive.
- [derive_has_field.md](cgp/implementation/entrypoints/derive_has_field.md) — the per-field accessor
  derive.
- [derive_has_fields.md](cgp/implementation/entrypoints/derive_has_fields.md) — the whole-shape
  field-list derive.
- [path.md](cgp/implementation/entrypoints/path.md) — the `Path!` type-level path macro.
- [product.md](cgp/implementation/entrypoints/product.md) — the `Product!`/`product!` list macros.
- [snapshot_macros.md](cgp/implementation/entrypoints/snapshot_macros.md) — the `snapshot_*!` family
  that pins macro expansions as `insta` snapshots.
- [sum.md](cgp/implementation/entrypoints/sum.md) — the `Sum!` type-level sum macro.
- [symbol.md](cgp/implementation/entrypoints/symbol.md) — the `Symbol!` type-level string macro.

#### `cgp/implementation/asts/` — one document per evaluation stack

- [attributes/README.md](cgp/implementation/asts/attributes/README.md) — what the attribute modifiers
  share: how a host collects them, and which host accepts which.
- [attributes/default_impl.md](cgp/implementation/asts/attributes/default_impl.md) — registering a
  provider as a namespace's per-path default.
- [attributes/derive_delegate.md](cgp/implementation/asts/attributes/derive_delegate.md) — generating
  a `UseDelegate` dispatcher impl for a component.
- [attributes/extend.md](cgp/implementation/asts/attributes/extend.md) — adding supertrait bounds to a
  generated trait.
- [attributes/extend_where.md](cgp/implementation/asts/attributes/extend_where.md) — adding `where`
  predicates to a generated trait definition.
- [attributes/use_provider.md](cgp/implementation/asts/attributes/use_provider.md) — completing an
  inner provider's bound for a higher-order provider.
- [attributes/uses.md](cgp/implementation/asts/attributes/uses.md) — importing `Self` trait bounds
  onto a provider's impl.
- [attributes/use_type.md](cgp/implementation/asts/attributes/use_type.md) — importing an abstract
  associated type and rewriting its bare alias.
- [blanket_trait.md](cgp/implementation/asts/blanket_trait.md) — the single-type stack behind
  `#[blanket_trait]`.
- [cgp_component.md](cgp/implementation/asts/cgp_component.md) — the item → preprocessed → evaluated
  sequence behind `#[cgp_component]`.
- [cgp_data.md](cgp/implementation/asts/cgp_data.md) — the AST family every extensible-data derive
  parses into.
- [cgp_fn.md](cgp/implementation/asts/cgp_fn.md) — the stack behind `#[cgp_fn]`.
- [cgp_getter.md](cgp/implementation/asts/cgp_getter.md) — the shared stack behind `#[cgp_getter]` and
  `#[cgp_auto_getter]`.
- [cgp_impl.md](cgp/implementation/asts/cgp_impl.md) — the stack that lowers consumer-style syntax to
  a provider impl.
- [cgp_provider.md](cgp/implementation/asts/cgp_provider.md) — the stack shared by `#[cgp_provider]`
  and `#[cgp_new_provider]`.
- [cgp_type.md](cgp/implementation/asts/cgp_type.md) — the thin wrapper that adds the abstract-type
  provider impls.
- [check_components.md](cgp/implementation/asts/check_components.md) — the check-table stacks behind
  both checking macros.
- [delegate_component.md](cgp/implementation/asts/delegate_component.md) — the wiring-table AST types
  and the impls they lower to.
- [namespace.md](cgp/implementation/asts/namespace.md) — the namespace table and its evaluated form.
- [path.md](cgp/implementation/asts/path.md) — the AST family that parses and emits type-level paths.
- [product.md](cgp/implementation/asts/product.md) — the type- and value-level product AST pair.
- [sum.md](cgp/implementation/asts/sum.md) — the single AST type behind `Sum!`.
- [symbol.md](cgp/implementation/asts/symbol.md) — the single AST type behind `Symbol!`.

#### `cgp/implementation/functions/` and `macros/`

- [functions/derive/delegated_impls.md](cgp/implementation/functions/derive/delegated_impls.md) — the
  forwarding-impl machinery shared by the component impls.
- [functions/derive/generics.md](cgp/implementation/functions/derive/generics.md) — `merge_generics`,
  combining two `Generics` into one without collision.
- [functions/derive/idents.md](cgp/implementation/functions/derive/idents.md) — the
  PascalCase/snake_case and reserved-name helpers.
- [functions/parse/is_provider_params.md](cgp/implementation/functions/parse/is_provider_params.md) —
  building the `IsProviderFor` params tuple from a trait's generics.
- [macros/define_keyword.md](cgp/implementation/macros/define_keyword.md) — declaring a custom-keyword
  marker type for the parsers.
- [macros/export_constructs.md](cgp/implementation/macros/export_constructs.md) — the hygienic markers
  that expand to fully-qualified CGP paths.
- [macros/parse_internal.md](cgp/implementation/macros/parse_internal.md) — building a `syn` node from
  quoted tokens with a descriptive parse error.

## `examples/` — worked examples

- [README.md](examples/README.md) — the example catalog with the context shape each one wires, and how
  an example differs from a reference document.
- [AGENTS.md](examples/AGENTS.md) — the rules: leave the mechanics to the reference, re-derive rather
  than cite an outside source, the document shape, naming the context shape the example wires, and where
  a missing concept belongs.
- [application-builder.md](examples/application-builder.md) — assembling an application context from
  independent per-subsystem builder providers via the extensible builder pattern.
- [area-calculation.md](examples/area-calculation.md) — computing shape areas, from field-driven
  functions to a wireable component with composable higher-order providers.
- [expression-interpreter.md](examples/expression-interpreter.md) — a modular arithmetic interpreter
  that solves the expression problem with the extensible visitor pattern.
- [extensible-shapes.md](examples/extensible-shapes.md) — operations over shapes modeled as enum
  variants, from auto-dispatch to context-wired visitor combinators.
- [modular-serialization.md](examples/modular-serialization.md) — Serde's `Serialize`/`Deserialize`
  rebuilt as CGP components, two contexts encoding the same data differently.
- [money-transfer-api.md](examples/money-transfer-api.md) — a balance-and-transfer web backend, from
  abstract domain types to a namespace-organized wiring served over HTTP.
- [profile-picture.md](examples/profile-picture.md) — a profile-picture lookup across a database query
  and an object-storage download.
- [shell-scripting-dsl.md](examples/shell-scripting-dsl.md) — a type-level DSL whose programs are
  types interpreted at compile time.
- [social-media-app.md](examples/social-media-app.md) — a users-and-posts CRUD backend, from coarse
  manager traits to provider bundles and namespace-grouped wiring.

## `related-work/` — CGP against the ideas it resembles

- [README.md](related-work/README.md) — the catalog, why honesty is the section's whole value, and how
  related work differs from the inward-looking sections.
- [AGENTS.md](related-work/AGENTS.md) — the rules: what every document must cover, the sourcing and
  citation obligation, the CGP side's synchronization duty, and the document template.
- [algebraic-effects.md](related-work/algebraic-effects.md) — the operations-and-handlers model of
  Koka, OCaml, Flix, and Eff, and the exactly-once fragment CGP reproduces statically.
- [dependency-injection.md](related-work/dependency-injection.md) — the IoC-container model of Spring,
  Guice, and Dagger, and injection without a container or reflection.
- [dynamic-dispatch.md](related-work/dynamic-dispatch.md) — late binding, vtables, duck typing, and
  prototypal delegation, all resolved statically by CGP.
- [implicit-parameters.md](related-work/implicit-parameters.md) — Scala's `given`/`using` and Haskell's
  `ImplicitParams`, and per-context choice in place of global coherence.
- [ml-modules.md](related-work/ml-modules.md) — signatures, structures, functors, and modular
  implicits, mapped onto components, providers, and higher-order providers.
- [reflection.md](related-work/reflection.md) — Bevy's runtime reflection, Zig's `comptime`, and Rust's
  reflection MVP against CGP's type-level shapes.
- [row-polymorphism.md](related-work/row-polymorphism.md) — PureScript rows, polymorphic variants, and
  row theory against CGP's derived type-level shapes in nominal Rust.
- [type-classes.md](related-work/type-classes.md) — dictionary passing, coherence, and overlapping
  instances, and CGP as a type-class system without global coherence.

## `communication-strategy/` — writing about CGP in public

- [README.md](communication-strategy/README.md) — the catalog and reading order, the marketing-naive
  expert this section writes for, the voicelessness failure mode it exists to prevent, the two things
  the section deliberately does not cover, and the principles of marketing, public communication, and
  developer relations it rests on.
- [AGENTS.md](communication-strategy/AGENTS.md) — the rules: write for the author's voice first, the
  marketing-director and devrel roles, what every document must do, honesty as the strategy and its
  three guardrails including distilling reaction to CGP rather than citing it, the consolidation rule,
  and the four sync targets.
- [author-personality.md](communication-strategy/author-personality.md) — who CGP's author is as a
  writer, the habits his published work evidences, and the preferences he has stated; the document every
  other one here is downstream of.
- [voice-and-register.md](communication-strategy/voice-and-register.md) — the layered voice (project on
  the site, author on the blog), the sentence-level register, the four structural moves that make CGP
  prose work, and the habits that mark a draft as machine-written.
- [identity.md](communication-strategy/identity.md) — the settled tag line analyzed word by word, the
  enhances-not-replaces frame, the layered pitch that follows the line, and the curated headline feature
  set for a front page.
- [readers.md](communication-strategy/readers.md) — the audience model by Rust experience, imported
  mental model, and role — the last including the language-design reader, who is unreachable through the
  general channels — plus the comprehension barriers a willing reader hits, including the
  application-context shape vanilla Rust gives them no reason to imagine, and the teaching move that
  lowers each.
- [message.md](communication-strategy/message.md) — everything a piece says about CGP: the pains it
  removes, the capabilities worth advertising, the objections readers bring, and the boundary where a
  plainer tool wins — four views of one reader.
- [vocabulary.md](communication-strategy/vocabulary.md) — the canonical word list for public writing
  (use, defer, avoid), the value/environmental/application context and self/parameter target qualifiers
  with the case that they are not jargon and the four misreadings they prevent, plus the glossary of the
  non-technical craft; the authority that resolves any phrasing disagreement.
- [formats.md](communication-strategy/formats.md) — per-artifact playbooks for the launch post,
  deep-dive, README, talk, thread, and comparison, the ready thread answers, the conversion ladder, and
  annotated model drafts.
- [evidence.md](communication-strategy/evidence.md) — the citable facts: what the Rust community
  worries about and rewards, which conversations draw attention, and the distilled patterns in how CGP's
  own posts and talk were received; the section's single home for external citations, and the rule that
  reaction to CGP is summarized rather than linked.
- [ai-disclosure.md](communication-strategy/ai-disclosure.md) — how the project discloses its own use of
  AI: the reach-and-verifiability principle behind the gradient, the four levels from agent-written
  documentation through revised drafts and non-imported code to the hand-written core library, the
  wording rules, the non-uniform-review claim that is easiest to get wrong, the site's disclosure page,
  and the rule that only new pages link to it.

## `cargo-cgp/` — the CGP toolchain

- [README.md](cargo-cgp/README.md) — what this member section documents, why the tool's design needs
  prose, and how its categories divide.
- [AGENTS.md](cargo-cgp/AGENTS.md) — the rules for documenting the tool: what the synchronization rule
  covers here, the read-only external references, showing the example behind an error message, and
  registering a document.
- [error-code.md](cargo-cgp/error-code.md) — the catalog of the `[CGP-Exxx]` codes the tool stamps on
  a rewritten message: what each means, what triggers it, and how to fix it.

### `cargo-cgp/reference/` — using the tool

- [README.md](cargo-cgp/reference/README.md) — the usage index and the two phases it covers, getting
  the tool installed and running it.
- [installation.md](cargo-cgp/reference/installation.md) — every install, update, and uninstall path,
  through cargo or Nix, and the pinned nightly each needs.
- [troubleshooting.md](cargo-cgp/reference/troubleshooting.md) — diagnosing a tool that will not run,
  seam by seam, with the exact message each failure prints.
- [usage.md](cargo-cgp/reference/usage.md) — running `check` and `expand`, reading the output and its
  codes, editor integration, and the environment variables that override behavior.

### `cargo-cgp/implementation/` — how the tool is built

- [README.md](cargo-cgp/implementation/README.md) — the implementation catalog and what each document
  covers.
- [AGENTS.md](cargo-cgp/implementation/AGENTS.md) — the rules for this tree: design rationale, the
  comparison-with-related-tools section, the document shape, and recording known gaps.
- [executable-structure.md](cargo-cgp/implementation/executable-structure.md) — the two-executable
  split, the cargo wrapping, and the environment contract between front-end and driver.
- [driver.md](cargo-cgp/implementation/driver.md) — the deep dive into the rustc wrapper: argument
  preparation, compiler-API access, the injected flags, and every diagnostic transform.
- [error-pipeline.md](cargo-cgp/implementation/error-pipeline.md) — how the stages fit together to
  turn raw diagnostics into readable CGP errors, all inside the driver.
- [error-processing.md](cargo-cgp/implementation/error-processing.md) — the rustc-free crate holding
  the post-processing transforms, the wiring rewrite, the diagnosis model, and the wording.
- [typed-root-cause-resolution.md](cargo-cgp/implementation/typed-root-cause-resolution.md) — the
  pipeline overview for resolving a check failure's root cause by asking the trait solver.
- [typed-resolution-anchors.md](cargo-cgp/implementation/typed-resolution-anchors.md) — the
  span-matching anchors that recover the real consumer obligation.
- [typed-resolution-call-site.md](cargo-cgp/implementation/typed-resolution-call-site.md) — the
  last-resort HIR re-read of the failing call expression.
- [typed-resolution-walk.md](cargo-cgp/implementation/typed-resolution-walk.md) — the descent to every
  terminal unmet bound, and each leaf's decoding and classification.
- [typed-resolution-output.md](cargo-cgp/implementation/typed-resolution-output.md) — the coded
  headline classes, the single root-cause note, and applying the rustc-free plan.
- [cached-dependency-resolution.md](cargo-cgp/implementation/cached-dependency-resolution.md) — the
  per-node resolver cache, its soundness reasoning, and why cacheability is a statelessness proof.
- [dependency-graph-rendering.md](cargo-cgp/implementation/dependency-graph-rendering.md) — folding
  per-cause paths into one DAG and rendering it `cargo tree`-style with shared subtrees.
- [resolve-context.md](cargo-cgp/implementation/resolve-context.md) — the planned `ResolveCtx` hosting
  the caches, config, and compiler access behind a mockable interface.
- [resugaring.md](cargo-cgp/implementation/resugaring.md) — reversing CGP's type-level expansions
  across three inputs (typed, text, syntax tree) that must agree.
- [expand-command.md](cargo-cgp/implementation/expand-command.md) — `cargo cgp expand`: the cargo
  launch, why the driver prints from `after_expansion`, and the deferred selective un-expansion.
- [rustc-diagnostic-internals.md](cargo-cgp/implementation/rustc-diagnostic-internals.md) — where the
  compiler builds and *suppresses* diagnostic information, and the panic hazards of re-entering it.
- [testing.md](cargo-cgp/implementation/testing.md) — the argument tests and the UI snapshot suite,
  its three passes and bless workflow, and how it compares to Clippy's harness.
- [distribution.md](cargo-cgp/implementation/distribution.md) — packaging both binaries with a pinned
  nightly, the version preflight, and the `setup`/`update` flow.

### `cargo-cgp/issues/` — the gaps still open

- [README.md](cargo-cgp/issues/README.md) — how pending issues are organized, and the rule that every
  issue is backed by a reproducing fixture.
- [hidden-root-cause.md](cargo-cgp/issues/hidden-root-cause.md) — the cases where no downstream
  consumer could recover the cause from the output, currently with no reproduced case.
- [usability.md](cargo-cgp/issues/usability.md) — output that carries the cause but buries it, the
  readability gaps that remain.

## `website/` — the public website, page by page

- [website/README.md](website/README.md) — what this section documents, the one-way link asymmetry
  that makes it necessary, how the Docusaurus site is organized, and its catalog.
- [website/AGENTS.md](website/AGENTS.md) — the rules: the one-way link rule and its two exceptions,
  the published agent skill as a pinned snapshot that agents never edit, bump, or read from, consulting
  communication-strategy before writing public prose, covering every supported form by layering the
  depth rather than omitting the advanced material, never taking current syntax from a blog post,
  the prohibition on rewriting published history, the release-branch model the redesign lands through,
  who drafts a page and who reads it before it publishes, disclosing AI use on a page, the document
  template, the status vocabulary, and how a ported catalog registers as one entry rather than one
  document per page.
- [website/information-architecture.md](website/information-architecture.md) — the site as intended:
  why most readers never see the homepage, the four routes in and why three fail, what each surface is
  for, the target page inventory including unwritten pages, the sidebar order, and each reader
  profile's path through the site.
- [website/redesign-queue.md](website/redesign-queue.md) — the consolidated list of what is wrong with
  or missing from the site, grouped into cheap corrections, page rewrites, and new pages; deleted when
  empty.
- [website/tasks.md](website/tasks.md) — the redesign's work plan: that the whole site relaunches with
  the v0.8.0 release from one branch, the four standing obligations every page-adding task carries,
  every remaining task with its repository, dependencies, and done-condition — including the AI
  disclosure page — which of them the release waits for, and the ordering; deleted when empty.
- [website/site-structure.md](website/site-structure.md) — the site's build, navigation, announcement
  bar, deployment, release-branch workflow, the three settings that depart from stock Docusaurus to
  publish the agent skill from its own repository, and the `example-code/` crate that holds the compiled
  counterparts of the code the site shows, plus one entry each for the front page, Introduction,
  Overview, Resources, Contribute, the `cargo-cgp` tooling section, the AI skills section and its
  `cgp-skills` submodule, the Concepts section, the Reference section, and the AI disclaimer.

### `website/writing-guides/` — how new pages should be written

- [README.md](website/writing-guides/README.md) — what a writing guide is, how it differs from a
  per-page document, the three decisions every guide assumes, and the catalog.
- [homepage.md](website/writing-guides/homepage.md) — the landing page: its two-tier structure, the
  settled before/after example with the copy that sells it and the six properties a replacement must
  keep, the six-section bounded essay, the offload rule and the dedicated explanation pages it offloads
  to, and what must never appear on the page.
- [explanation.md](website/writing-guides/explanation.md) — the understanding-oriented `Concepts`
  tier, one page per idea: what every explanation page owes, what Diátaxis gives the tier and where CGP
  diverges, how a concept document is rewritten into one, the fixed page shape, specs for the four
  pages the homepage offloads to, and where the section sits in the docs tree.
- [tutorial.md](website/writing-guides/tutorial.md) — the tutorials: independent outcome-named pages,
  the first-principles and applied registers, the six obligations taken from Diátaxis and the two rules
  rejected, the problem-before-construct and explicit-before-sugar orderings, and the checking and
  tooling every tutorial owes.
- [release-announcement.md](website/writing-guides/release-announcement.md) — the blog's most repeated
  artifact and the only page type specified in the author's voice: the two readers it serves, the
  one-change rule, the seven-part shape, the breaking-changes obligation from the removal ledger, and
  the five mechanical items publication fixes.
- [deep-dive.md](website/writing-guides/deep-dive.md) — the multi-page living documents grown from the
  longest blog posts: why they are new artifacts rather than edits, converting the author's voice to
  the project's without losing the concessions, the page split, and tracking the live code base.
- [tooling.md](website/writing-guides/tooling.md) — the pages documenting a program the reader runs
  rather than a construct they write: why a tool's page fails differently, the five-page section shape,
  quoting real output rather than remembered output, and the version concession.
- [reference.md](website/writing-guides/reference.md) — the canonical per-construct reference ported
  from the internal one: why the site rather than docs.rs is canonical, the six-section layered descent
  serving beginner to advanced on one page, the obligation to cover every form the parser accepts and
  to enumerate against it, near-one-page-per-construct with four consolidations, the replacement for
  every internal link target, and the external Rust documentation table.

### `website/blog/` — one document per published post

- [README.md](website/blog/README.md) — the chronological catalog, why drift matters most here, the
  five breaking changes that account for it, and the site's publication conventions.
- [early-preview-announcement.md](website/blog/early-preview-announcement.md) — the launch post, CGP's
  origin in the Hermes relayer, and a 2025 plan since resolved by other means.
- [v0-3-0-release.md](website/blog/v0-3-0-release.md) — abstract types via the removed `cgp_type!`,
  the first getter macros, `CanWrapError`, and the error and runtime crates.
- [v0-4-0-release.md](website/blog/v0-4-0-release.md) — the release that made CGP debuggable:
  `IsProviderFor`, `check_components!`, plus `#[cgp_context]` and the preset system.
- [v0-4-1-release.md](website/blog/v0-4-1-release.md) — the `cgp-handler` crate introducing
  `Handler`, `Computer`, and `Producer`.
- [hypershell-release.md](website/blog/hypershell-release.md) — the site's longest post: building a
  type-level DSL, with a self-contained CGP primer and a candid disadvantages section.
- [extensible-datatypes-part-1.md](website/blog/extensible-datatypes-part-1.md) — extensible records,
  enum casts, and modular application construction from independent builder providers.
- [extensible-datatypes-part-2.md](website/blog/extensible-datatypes-part-2.md) — extensible variants
  applied to the expression problem, with the `serde::Visitor` motivation.
- [extensible-datatypes-part-3.md](website/blog/extensible-datatypes-part-3.md) — the record
  internals: constraint propagation, partial records, and the builder dispatchers.
- [extensible-datatypes-part-4.md](website/blog/extensible-datatypes-part-4.md) — the variant
  internals: `Void`, exhaustive extraction, the casts, and the monadic visitor dispatchers.
- [v0-5-0-release.md](website/blog/v0-5-0-release.md) — `#[derive(CgpData)]`, `#[cgp_auto_dispatch]`,
  monadic computation, and the removal of `Async` for the `Send`-recovery pattern.
- [v0-6-0-release.md](website/blog/v0-6-0-release.md) — `#[cgp_impl]`, direct delegation on the
  context, and the removal of `HasCgpProvider`.
- [cgp-serde-release.md](website/blog/cgp-serde-release.md) — Serde as CGP components, two apps
  encoding the same data differently, and arena-allocating deserialization.
- [v0-6-1-release.md](website/blog/v0-6-1-release.md) — implicit context types, `#[check_providers]`,
  and associated types in getter traits.
- [new-website.md](website/blog/new-website.md) — the Zola-to-Docusaurus migration, the stock-install
  policy, and the project's disclosed use of LLM assistance.
- [v0-7-0-release.md](website/blog/v0-7-0-release.md) — the attribute suite (`#[cgp_fn]`,
  `#[implicit]`, `#[uses]`, `#[use_provider]`, `#[use_type]`) and the removal of `#[cgp_context]`.
- [rustlab-2025-coherence.md](website/blog/rustlab-2025-coherence.md) — the conference talk
  transcript, and the clearest published account of why coherence exists and why specialization
  cannot replace it.
- [v0-8-0-release.md](website/blog/v0-8-0-release.md) — the namespace announcement for the
  unreleased v0.8.0, an unfinished draft begun under the abandoned v0.7.1 number.
- [incoherent-rust-today.md](website/blog/incoherent-rust-today.md) — an unpublished draft on the
  `incoherent-rust` branch reading CGP against the dictionary-passing and incoherent-traits discussion,
  and what it needs before it can be published.

### `website/deep-dives/` — one document per planned deep dive

- [README.md](website/deep-dives/README.md) — why a deep dive rather than a revised blog post, the fact
  that the tracked code bases are ahead of the posts, the catalog, and the document shape.
- [hypershell.md](website/deep-dives/hypershell.md) — the type-level DSL: a six-page split, the embedded
  CGP primer removed in favour of the explanation tier, presets replaced by namespaces, and the
  `#[uses]`/`#[implicit]` adoption the repository still needs.
- [extensible-datatypes.md](website/deep-dives/extensible-datatypes.md) — records and variants from four
  posts and two example crates: a seven-page pattern-then-internals split, and why the expression
  crate's `UseInputDelegate` tables are *not* `open` candidates.
- [cgp-serde.md](website/deep-dives/cgp-serde.md) — Serde as components: a five-page split, the release
  framing removed, and the missing `CgpSerdeNamespace` that would make the two-application payoff land.

### `website/tutorials/` — one document per tutorial series

- [README.md](website/tutorials/README.md) — why a tutorial needs a teaching-contract document rather
  than a drift record, the catalog, and the document shape.
- [hello-world.md](website/tutorials/hello-world.md) — the single-page first contact: one CGP
  function, two contexts, and an optional desugaring appendix.
- [area-calculation.md](website/tutorials/area-calculation.md) — the three-part series from plain
  functions to higher-order providers, its two load-bearing orderings, and the checking gap in it.

## `releases/` — the version history

- [releases/README.md](releases/README.md) — why the base keeps one historical section, the **removal
  ledger** dating every renamed or deleted construct, the catalog of releases, and the two places the
  upstream changelog disagrees with the tags.
- [v0-1-0.md](releases/v0-1-0.md) — 2024-09-02, the first crates.io publication, predating the public
  announcement; every idea present, almost every name since changed.
- [v0-2-0.md](releases/v0-2-0.md) — 2024-12-08, the pre-launch cleanup: `#[cgp_component]`, and the
  type-level vocabulary in essentially its final form.
- [v0-3-0.md](releases/v0-3-0.md) — 2025-01-08, abstract types, the getter macros, `CanWrapError`,
  and the error and runtime crates.
- [v0-3-1.md](releases/v0-3-1.md) — 2025-01-16, a patch release whose async error aliases were all
  removed two releases later.
- [v0-4-0.md](releases/v0-4-0.md) — 2025-05-09, the debuggability release: `IsProviderFor`,
  `check_components!`, presets, `#[cgp_context]`, and the first datatype-generic support.
- [v0-4-1.md](releases/v0-4-1.md) — 2025-06-14, the `cgp-handler` crate and the computation family
  everything later is built on.
- [v0-4-2.md](releases/v0-4-2.md) — 2025-07-07, extensible records and variants, the builder and
  visitor patterns, and safe enum casting.
- [v0-5-0.md](releases/v0-5-0.md) — 2025-10-12, the stabilization release: `#[derive(CgpData)]`,
  `#[cgp_auto_dispatch]`, monads, `StaticString`, and the removal of `Async`.
- [v0-6-0.md](releases/v0-6-0.md) — 2025-10-26, `#[cgp_impl]`, direct delegation on the context, and
  the removal of `HasCgpProvider`.
- [v0-6-1.md](releases/v0-6-1.md) — 2026-02-01, implicit context types, `#[check_providers]`, and
  associated types in getter traits; all three still current.
- [v0-7-0.md](releases/v0-7-0.md) — 2026-02-28, the most recent shipped release: the attribute suite
  and the removal of `#[cgp_context]`; its changelog entry is mislabelled v0.6.2.
- [v0-8-0.md](releases/v0-8-0.md) — **unreleased**, in development at `0.8.0-alpha`: namespaces and
  paths, the `open` statement, the removal of presets, and why it is not v0.7.1.

## `projects/` — the libraries built with CGP

- [projects/README.md](projects/README.md) — what qualifies as an ecosystem project, why these
  documents stay brief, and how each connects to an example, an announcement post, and a set of
  constructs.
- [projects/hypershell/README.md](projects/hypershell/README.md) — the type-level shell-scripting
  DSL: its crate layout, its namespace-based assembly, and the CGP it exercises.
- [projects/cgp-serde/README.md](projects/cgp-serde/README.md) — Serde rebuilt as CGP components:
  its provider set, derive-free struct handling, lifetime-carrying components, and open gaps.
