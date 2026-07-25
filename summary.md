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
  synchronization rule, verifying against the source, document-the-present, how links are written,
  registering a document, the prose mechanics, and the committing rule.
- [summary.md](summary.md) — this file.
- [sibling-projects.md](sibling-projects.md) — the member projects, their repositories, the revision
  of each to read, and the rules for finding a sibling locally versus linking to it.

## `cgp/` — the CGP library

- [cgp/README.md](cgp/README.md) — what this member section documents, why prose beats reading the
  proc-macro source, and how its five parts divide.
- [cgp/AGENTS.md](cgp/AGENTS.md) — the rules for documenting `cgp`: what the synchronization rule
  lands on here, the authoring conventions, the per-directory rules, the reference document template,
  the syntax-grammar notation, and how to review a document.

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
  table; also documents the `#[prefix(...)]` registration attribute.
- [cgp_new_provider.md](cgp/reference/macros/cgp_new_provider.md) — `#[cgp_provider]` that also
  declares the provider struct.
- [cgp_producer.md](cgp/reference/macros/cgp_producer.md) — define a `Producer` provider from an
  input-free function.
- [cgp_provider.md](cgp/reference/macros/cgp_provider.md) — write a provider by implementing the
  provider trait directly, with `IsProviderFor` derived from the same bounds.
- [cgp_type.md](cgp/reference/macros/cgp_type.md) — define an abstract-type component, layering a
  `UseType` impl over `#[cgp_component]`.
- [check_components.md](cgp/reference/macros/check_components.md) — assert at compile time that a
  context can use each listed component; covers `#[check_providers]` and `#[check_params]`.
- [delegate_and_check_components.md](cgp/reference/macros/delegate_and_check_components.md) — wire
  and check in one macro, and why it is wrong for an aggregate provider.
- [delegate_components.md](cgp/reference/macros/delegate_components.md) — build a context's wiring
  table: array keys, generic lists, the `new` aggregate form, `open` dispatch, and namespace
  statements.
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
  context field, with the clone/`as_str`/option/slice/mutable access rules.
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
  itself.
- [aggregate-providers.md](cgp/concepts/aggregate-providers.md) — bundling component wirings into a
  reusable provider, and why such a bundle is a provider rather than a context.
- [check-traits.md](cgp/concepts/check-traits.md) — why wiring is lazy and how a compile-time
  assertion makes its failures readable.
- [coherence.md](cgp/concepts/coherence.md) — what Rust's coherence rules forbid and the
  incoherent-impl-plus-local-wiring strategy CGP uses.
- [consumer-and-provider-traits.md](cgp/concepts/consumer-and-provider-traits.md) — the trait duality
  at the heart of CGP.
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
  blanket impl's `where` clause.
- [implicit-arguments.md](cgp/concepts/implicit-arguments.md) — writing providers as ordinary
  functions whose arguments come from context fields.
- [modular-error-handling.md](cgp/concepts/modular-error-handling.md) — the error type, its
  construction, and its detail as three independent wiring decisions.
- [modularity-hierarchy.md](cgp/concepts/modularity-hierarchy.md) — the ladder from one blanket impl
  to per-type-per-provider wiring, and how to pick the lowest rung.
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
- [error_codes/e0277.md](cgp/errors/error_codes/e0277.md) — a trait bound is not satisfied, including
  the `Sized` form.
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

- [README.md](examples/README.md) — the example catalog, and how an example differs from a reference
  document.
- [AGENTS.md](examples/AGENTS.md) — the rules: leave the mechanics to the reference, re-derive rather
  than cite an outside source, the document shape, and where a missing concept belongs.
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

- [README.md](communication-strategy/README.md) — the catalog, the marketing-naive expert this section
  writes for, and the principles of marketing, public communication, and developer relations it rests
  on.
- [AGENTS.md](communication-strategy/AGENTS.md) — the rules: the marketing-director and devrel roles,
  what every document must do, honesty as the strategy, and the section's three sync targets.
- [attention-and-engagement.md](communication-strategy/attention-and-engagement.md) — the evidence base
  for where the Rust community's attention sits and how CGP has been received.
- [formats.md](communication-strategy/formats.md) — per-artifact playbooks for the launch post,
  tutorial, README, talk, thread, and comparison, plus the conversion ladder.
- [glossary.md](communication-strategy/glossary.md) — plain-language definitions of the non-technical
  terms of art, each anchored to a programmer's intuition.
- [key-features.md](communication-strategy/key-features.md) — the short headline feature set for a
  front page, with titles and one-line copy.
- [positioning.md](communication-strategy/positioning.md) — the honest decision guide for when to reach
  for CGP and when a plainer tool wins.
- [problems-solved.md](communication-strategy/problems-solved.md) — the concrete pains CGP removes,
  written as short before-and-after stories.
- [reader-profiles.md](communication-strategy/reader-profiles.md) — the audience model: who reads about
  CGP, what each already knows, and what each needs.
- [selling-points.md](communication-strategy/selling-points.md) — the true capabilities to advertise,
  with the phrasings that land and the ones that backfire.
- [skepticism.md](communication-strategy/skepticism.md) — the objections readers bring, whether each is
  justified, and wording that answers without provoking.
- [tag-lines.md](communication-strategy/tag-lines.md) — CGP's one-line description analyzed word by
  word, plus model introductions.
- [technical-barriers.md](communication-strategy/technical-barriers.md) — the comprehension barriers a
  learner hits and the teaching moves that lower each.
- [vocabulary.md](communication-strategy/vocabulary.md) — the canonical word list for public writing:
  which term to use, which to defer, which to avoid.
- [worked-examples.md](communication-strategy/worked-examples.md) — finished annotated drafts of a
  launch post, a README, and a social thread, each move traced to the document that argues for it.

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
