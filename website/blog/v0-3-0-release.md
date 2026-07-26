# CGP Updates: v0.3.0 Release and New Chapters

The first release announcement after launch, introducing abstract types, the getter macros, error
wrapping, and the standalone error and runtime crates — almost all of it through syntax that has since
been replaced.

- **URL** — <https://contextgeneric.dev/blog/v0-3-0-release>
- **Source** — [blog/2025-01-09-v0.3.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-01-09-v0.3.0-release.md)
- **Published** — 9 January 2025, tagged `release`
- **Release** — [v0.3.0](../../releases/v0-3-0.md)
- **Status** — Historical

## What it covers

The post is split between new book chapters and new library features. The book half summarizes three
chapters — associated types, error handling, and field accessors — and is mainly of interest now as a
record of what the [CGP Patterns book](https://patterns.contextgeneric.dev/) covers.

The library half introduces five things. The `cgp_type!` **function-like macro** collapsed an
abstract-type trait into one line, expanding to a `#[cgp_component]` trait plus a `UseType` blanket
impl. `#[cgp_auto_getter]` generated a getter trait's blanket impl over `HasField`, and
`#[cgp_getter]` did the same while also making the getter a full component wired through
`delegate_components!`. `CanWrapError` was added as a cleaner alternative to the previous idiom of
raising a tuple, `CanRaiseError<(Self::Error, Detail)>`. And two crates shipped:
[`cgp-error-anyhow`](https://docs.rs/cgp-error-anyhow), completing the set alongside `cgp-error-eyre`
and `cgp-error-std`, and `cgp-runtime`, standardizing an abstract runtime interface.

The post closes by acknowledging that the getter macros were motivated by user feedback that direct
use of `HasField` was too complex for beginners — an early instance of the ergonomics pressure that
shaped every release since.

## How it relates to the knowledge base

Every construct the post introduces is documented in current form. Abstract types are
[`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) over the
[abstract types](../../cgp/concepts/abstract-types.md) concept, with
[`UseType`](../../cgp/reference/providers/use_type.md) as the provider that binds one. The getters are
[`#[cgp_auto_getter]`](../../cgp/reference/macros/cgp_auto_getter.md) and
[`#[cgp_getter]`](../../cgp/reference/macros/cgp_getter.md), resting on
[`HasField`](../../cgp/reference/traits/has_field.md). Error wrapping is
[`CanWrapError`](../../cgp/reference/components/can_raise_error.md) within
[modular error handling](../../cgp/concepts/modular-error-handling.md). The runtime interface is
[`HasRuntime` / `HasRuntimeType`](../../cgp/reference/components/has_runtime.md).

The post's own framing — that the launch audience read CGP as "primarily a dependency injection
framework in Rust," and that abstract types were the answer — is a documented reception fact worth
knowing, and it matches the DI-framework objection recorded in
[message.md](../../communication-strategy/message.md#the-objections-readers-bring).

## Where it diverges from CGP v0.8.0

Nearly all of the post's code is dead syntax. The specifics:

- **`cgp_type!( Error: Debug )` no longer exists.** The function-like macro became the attribute
  [`#[cgp_type]`](../../cgp/reference/macros/cgp_type.md) in v0.4.0, so an abstract type is now
  declared by annotating an ordinary trait.
- **The generated names changed.** The post shows `ErrorTypeComponent` and `ProvideErrorType`; the
  current convention produces `{Type}TypeProvider` and `{Type}TypeProviderComponent`, and the
  built-in `ProvideType` was renamed to
  [`TypeProvider`](../../cgp/reference/components/has_type.md) in v0.7.0.
- **`HasComponents` is gone.** The `#[cgp_getter]` example implements `HasComponents for Person` with
  a `PersonComponents` provider struct. That trait was renamed `HasCgpProvider` in v0.4.0 and removed
  entirely in v0.6.0; a context now carries its own
  [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) table directly.
- **`UseFields` is no longer the idiomatic getter wiring.** The post wires
  `NameGetterComponent: UseFields`; [`UseFields`](../../cgp/reference/providers/use_fields.md) still
  exists, but the modern default for reading a context's own field is an
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) argument, with a getter trait reserved
  for the narrow cases [reading-context-fields](../../cgp/guides/reading-context-fields.md) names.
- **The component key/value syntax changed.** `#[cgp_component { name: ..., provider: ... }]` and
  `#[cgp_getter { provider: ... }]` still parse, but the short positional form
  `#[cgp_component(Greeter)]` arrived in v0.4.0 and is now idiomatic.
- **`CanWrapError`'s definition drifted.** The post shows `CanWrapError<Detail>: HasErrorType`; the
  current component imports its error type with
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) rather than a native supertrait, per
  [importing-abstract-types](../../cgp/guides/importing-abstract-types.md).

## Maintaining it

Leave it alone. This is a release note for a version nobody should be running, and its only remaining
function is historical. The one fact in it that stays useful is the motivation behind the getter
macros, and that reasoning is already carried forward in
[reading-context-fields](../../cgp/guides/reading-context-fields.md).
