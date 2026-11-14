# CGP Updates: v0.3.0 Release and New Chapters

The first release announcement after launch: abstract types, the getter macros, error wrapping, and
the standalone error and runtime crates, almost all in syntax since replaced.

- **URL**: <https://contextgeneric.dev/blog/v0-3-0-release>
- **Source**: [blog/2025-01-09-v0.3.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-01-09-v0.3.0-release.md)
- **Published**: 9 January 2025, tagged `release`
- **Release**: [v0.3.0](../../releases/v0-3-0.md)
- **Status**: Historical

## What it covers

The first half summarizes three new chapters of the
[CGP Patterns book](https://patterns.contextgeneric.dev/): associated types, error handling, and
field accessors. The second introduces five library features:

- **`cgp_type!`:** a function-like macro collapsing an abstract-type trait into one line, expanding to
  a `#[cgp_component]` trait and a `UseType` blanket impl.
- **The getter macros:** `#[cgp_auto_getter]`, a getter trait's blanket impl over `HasField`, and
  `#[cgp_getter]`, which also makes the getter a component wired through `delegate_components!`. The
  post says user feedback that `HasField` was too complex for beginners motivated them.
- **`CanWrapError`:** replacing the idiom of raising a tuple, `CanRaiseError<(Self::Error, Detail)>`.
- **Two crates:** [`cgp-error-anyhow`](https://docs.rs/cgp-error-anyhow), completing the set with
  `cgp-error-eyre` and `cgp-error-std`, and `cgp-runtime`, an abstract runtime interface.

The post records that the launch audience read CGP as "primarily a dependency injection framework in
Rust", with abstract types as the answer; it matches the DI-framework objection in
[message.md](../../communication-strategy/message.md#the-objections-readers-bring).

## How it relates to the knowledge base

- **Abstract types:** [`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) over
  [abstract types](../../cgp/concepts/abstract-types.md), bound with
  [`UseType`](../../cgp/reference/providers/use_type.md).
- **Getters:** [`#[cgp_auto_getter]`](../../cgp/reference/macros/cgp_auto_getter.md) and
  [`#[cgp_getter]`](../../cgp/reference/macros/cgp_getter.md), over
  [`HasField`](../../cgp/reference/traits/has_field.md); the getter macros' motivation is carried in
  [reading-context-fields](../../cgp/guides/reading-context-fields.md).
- **Error wrapping:** [`CanWrapError`](../../cgp/reference/components/can_raise_error.md) within
  [modular error handling](../../cgp/concepts/modular-error-handling.md).
- **Runtime:** [`HasRuntime` / `HasRuntimeType`](../../cgp/reference/components/has_runtime.md).

## Where it diverges from CGP v0.8.0

Nearly all of the post's code is dead syntax:

- **`cgp_type!( Error: Debug )` no longer exists.** The function-like macro became the attribute
  [`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) in v0.4.0, so an abstract type is declared
  by annotating an ordinary trait.
- **The generated names changed.** The post shows `ErrorTypeComponent` and `ProvideErrorType`; the
  convention is now `{Type}TypeProvider` and `{Type}TypeProviderComponent`, and the built-in
  `ProvideType` was renamed [`TypeProvider`](../../cgp/reference/components/has_type.md) in v0.7.0.
- **`HasComponents` is gone.** The `#[cgp_getter]` example implements `HasComponents for Person` with
  a `PersonComponents` provider struct. The trait was renamed `HasCgpProvider` in v0.4.0 and removed
  in v0.6.0; a context now carries its own
  [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) table.
- **`UseFields` is no longer the idiomatic getter wiring.** The post wires
  `NameGetterComponent: UseFields`; [`UseFields`](../../cgp/reference/providers/use_fields.md) still
  exists, but a context's own field is read with an
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) argument, and a getter trait is kept
  for the cases [reading-context-fields](../../cgp/guides/reading-context-fields.md) names.
- **The component key/value syntax changed.** `#[cgp_component { name: ..., provider: ... }]` and
  `#[cgp_getter { provider: ... }]` still parse, but the positional `#[cgp_component(Greeter)]`,
  added in v0.4.0, is idiomatic.
- **`CanWrapError`'s definition drifted.** The post shows `CanWrapError<Detail>: HasErrorType`; the
  component now imports its error type with
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) rather than a native supertrait, per
  [importing-abstract-types](../../cgp/guides/importing-abstract-types.md).

## Maintaining it

Leave it alone; it records a version nobody should run, and nothing in it is a source for current
writing.
