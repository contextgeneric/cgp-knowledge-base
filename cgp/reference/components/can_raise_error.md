# `CanRaiseError`

`CanRaiseError<SourceError>` turns a concrete source error into a context's abstract `Self::Error`,
and its companion `CanWrapError<Detail>` adds detail to an existing abstract error. Both build on
[`HasErrorType`](has_error_type.md).

## Purpose

`CanRaiseError` lets generic code produce its context's abstract error from whatever concrete error
it meets. A provider that calls a fallible operation gets back a specific error, such as a parse
error, an I/O error, or a message string, but it must return `Self::Error`, whose concrete type it
does not know. `Context::raise_error(source)` converts the source error, and the context decides
how. Because the trait is generic over `SourceError`, one context can raise many unrelated source
errors into its one abstract error.

`CanWrapError` enriches an error as it propagates. It takes an error the context already holds and
attaches a `Detail`, such as a message, a span, or a path. Together the two traits cover the common
motions: raise a foreign error into the abstract one, then wrap context onto it on the way up.

## Definition

Both traits are `#[cgp_component]`s that import the abstract error with
[`#[use_type(HasErrorType.Error)]`](../attributes/use_type.md), which adds `HasErrorType` as a
supertrait and lets the signatures write a bare `Error` for `<Self as HasErrorType>::Error`:

```rust
#[cgp_component(ErrorRaiser)]
#[prefix(@cgp.core.error in DefaultNamespace)]
#[derive_delegate(UseDelegate<SourceError>)]
#[use_type(HasErrorType.Error)]
pub trait CanRaiseError<SourceError> {
    #[track_caller]
    fn raise_error(error: SourceError) -> Error;
}

#[cgp_component(ErrorWrapper)]
#[prefix(@cgp.core.error in DefaultNamespace)]
#[derive_delegate(UseDelegate<Detail>)]
#[use_type(HasErrorType.Error)]
pub trait CanWrapError<Detail> {
    #[track_caller]
    fn wrap_error(error: Error, detail: Detail) -> Error;
}
```

The two traits share one shape:

- **The methods are associated functions**, with no `self` receiver, because building an error
  depends on the context type, not on a context value. Generic code calls
  `Context::raise_error(source)` or `Self::wrap_error(error, detail)` where only the type parameter
  is in scope. On a concrete context with the provider trait also imported, the bare
  `App::raise_error(…)` is ambiguous (`E0034 multiple applicable items in scope`), because the
  context implements `ErrorRaiser` too through the provider blanket impl; name the consumer trait,
  as `<App as CanRaiseError<String>>::raise_error(…)`.
- **The provider traits are `ErrorRaiser` and `ErrorWrapper`**, wired with the keys
  `ErrorRaiserComponent` and `ErrorWrapperComponent`.
- **[`#[derive_delegate(UseDelegate<...>)]`](../attributes/derive_delegate.md)** generates the
  `UseDelegate` impl for the legacy delegation table that picks a provider per `SourceError` or per
  `Detail`.
- **[`#[prefix(@cgp.core.error in DefaultNamespace)]`](../attributes/prefix.md)** registers both
  components in `DefaultNamespace` under `@cgp.core.error`.

`CanRaiseError` and `CanWrapError` are in the prelude. The provider traits and component keys are
not, and are imported from `cgp::core::error`.

## Behavior

A context gains these operations by wiring `ErrorRaiserComponent` and `ErrorWrapperComponent` to
providers. Most contexts wire ready-made ones rather than writing their own:

- **The [error backends](../../../projects/error/README.md)** `cgp-error-anyhow`, `cgp-error-eyre`,
  and `cgp-error-std` provide raisers and wrappers for their concrete error types, such as
  `RaiseAnyhowError`.
- **The [in-tree error providers](../providers/error_providers.md)** in `cgp-error-extra` capture
  strategies independent of the error type, such as `RaiseFrom`, which converts with `Into`.

Different source errors often need different providers, and a context dispatches on the source type
in either of two ways. The recommended form is `open ErrorRaiserComponent;` followed by one entry
per source type, such as `@ErrorRaiserComponent.String: DisplayEyreError`. The legacy form is a
`UseDelegate` table keyed by source type. A context that joins `DefaultNamespace` writes the same
entries under the prefix, as `@cgp.core.error.ErrorRaiserComponent.io::Error: RaiseEyreError`.

Both methods are `#[track_caller]`, and the attribute survives every layer of CGP forwarding. Rust
applies `#[track_caller]` on a trait method declaration to every impl of that method, and
`#[cgp_component]` keeps it on the provider trait's declaration. It therefore covers the consumer
blanket impl, the delegation impl, the `UseDelegate` and `RedirectLookup` impls, and every provider.
An error library that records `Location::caller()`, such as eyre with its `track-caller` feature,
records the line that called `raise_error`, whether the component is wired directly, with `open`, through
a namespace path, or through a `UseDelegate` table. The location survives only while every call between the caller and the
library is `#[track_caller]`. `Into::into` and eyre's constructors are, but a helper function inside
a provider needs the attribute too, or the library records the helper's line.

## Examples

A provider raises a message into the abstract error and wraps context onto it:

```rust
use cgp::prelude::*;

#[cgp_component(Loader)]
#[use_type(HasErrorType.Error)]
pub trait CanLoad {
    fn load(&self, path: &str) -> Result<String, Error>;
}

#[cgp_impl(new LoadOrFail)]
#[uses(CanRaiseError<String>, CanWrapError<String>)]
#[use_type(HasErrorType.Error)]
impl Loader {
    fn load(&self, path: &str) -> Result<String, Error> {
        if path.is_empty() {
            let err = Self::raise_error("empty path".to_owned());
            return Err(Self::wrap_error(err, format!("while loading {path}")));
        }
        Ok(format!("contents of {path}"))
    }
}
```

The provider names neither the context nor its error type. It requires `CanRaiseError<String>` to
turn a message into the abstract error and `CanWrapError<String>` to attach context. Any context
that meets both bounds, typically by wiring an error backend, makes `load` fail with that context's
own error type.

## Related constructs

These constructs are the ones `CanRaiseError` and `CanWrapError` work with:

- [`HasErrorType`](has_error_type.md): the supertrait whose abstract `Error` they produce and
  enrich.
- [`#[derive_delegate]`](../attributes/derive_delegate.md) and
  [`delegate_components!`](../macros/delegate_components.md): the legacy and the `open` forms of
  per-type dispatch.
- [In-tree error providers](../providers/error_providers.md) and the
  [error backends](../../../projects/error/README.md): ready-made providers.
- [Modular error handling](../../concepts/modular-error-handling.md): how these components combine
  into CGP's error strategy.

## Source

- `CanRaiseError` is defined in
  [crates/core/cgp-error/src/traits/can_raise_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-error/src/traits/can_raise_error.rs)
  and `CanWrapError` in
  [crates/core/cgp-error/src/traits/can_wrap_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-error/src/traits/can_wrap_error.rs).
- Both build on `HasErrorType` from
  [crates/core/cgp-error/src/traits/has_error_type.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-error/src/traits/has_error_type.rs).
- The pluggable providers that implement them live in
  [crates/standalone/error/](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/),
  documented in [projects/error/](../../../projects/error/README.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **2 pages**:
[`can_raise_error`](https://contextgeneric.dev/docs/reference/components/can_raise_error) for
`CanRaiseError` and
[`can_wrap_error`](https://contextgeneric.dev/docs/reference/components/can_wrap_error) for its
companion `CanWrapError`. A change here is propagated to both, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the
split is recorded in [website/site-structure.md](../../../website/site-structure.md).
