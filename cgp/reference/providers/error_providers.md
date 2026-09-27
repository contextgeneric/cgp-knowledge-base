# In-tree error providers

The in-tree error providers are the zero-sized provider structs in `cgp-error-extra` that implement the error-raising and error-wrapping components for any context, whatever concrete error type the context chose.

## Purpose

These providers give a context common error-handling strategies without depending on an error library. [`CanRaiseError`](../components/can_raise_error.md) and `CanWrapError` say what a context can do with errors, raise a foreign error into its abstract `Self::Error` or attach detail to one, but not how. The providers here supply the how for cases that need no particular backend. Each is generic over the context, so it works with whatever error type the context's [`HasErrorType`](../components/has_error_type.md) names.

They complement the standalone [error backends](../../../projects/error/README.md) `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`, whose providers are specialized to one concrete error type. A context typically wires a backend for its error type and these providers for strategies that cut across types. What a backend adds over these providers, and why `DebugError` cannot be the provider for `String` itself, is set out in the backends' [architecture](../../../projects/error/architecture.md#what-a-backend-adds-over-the-generic-providers).

All seven are reached through `cgp::extra::error`, and none is in the prelude. Their provider traits `ErrorRaiser` and `ErrorWrapper`, and the keys `ErrorRaiserComponent` and `ErrorWrapperComponent`, are imported from `cgp::core::error`.

## Providers

The seven providers fall into three groups:

| Provider | Implements | Accepts | Effect |
| --- | --- | --- | --- |
| `RaiseFrom` | `ErrorRaiser` | any `E` with `Context::Error: From<E>` | converts with `into()` |
| `ReturnError` | `ErrorRaiser` | `E` equal to `Context::Error` | returns the error unchanged |
| `RaiseInfallible` | `ErrorRaiser` | `Infallible` only | cannot be called |
| `PanicOnError` | `ErrorRaiser` | any `E: Debug` | panics with the error |
| `DiscardDetail` | `ErrorWrapper` | any detail | drops the detail |
| `DebugError` | both | any `Debug` value | formats with `{:?}` and forwards as a `String` |
| `DisplayError` | both | any `Display` value | formats with `to_string()` and forwards as a `String` |

### `RaiseFrom`: convert through `From`

`RaiseFrom` is the `ErrorRaiser` provider that raises a source error by converting it into the context's error type with the standard `From` trait. It implements `ErrorRaiser<Context, E>` for any context whose abstract `Error` implements `From<E>`:

```rust
#[cgp_new_provider]
impl<Context, E> ErrorRaiser<Context, E> for RaiseFrom
where
    Context: HasErrorType,
    Context::Error: From<E>,
{
    fn raise_error(e: E) -> Context::Error {
        e.into()
    }
}
```

This is the default choice whenever the abstract error already knows how to absorb the source error through `From`. Because the bound is `Context::Error: From<E>`, a single wiring of `RaiseFrom` covers every source error type the context's error has a `From` impl for.

### `ReturnError`: the source is already the abstract error

`ReturnError` is the `ErrorRaiser` provider for the case where the source error *is* the context's abstract error, so raising is the identity. It implements `ErrorRaiser<Context, E>` only when the context's `Error` is exactly `E`:

```rust
#[cgp_new_provider]
impl<Context, E> ErrorRaiser<Context, E> for ReturnError
where
    Context: HasErrorType<Error = E>,
{
    fn raise_error(e: E) -> E {
        e
    }
}
```

The `HasErrorType<Error = E>` bound ties the source type to the abstract error, so `raise_error` returns its argument untouched. A context uses this when generic code raises a value that is already of the context's chosen error type.

### `RaiseInfallible`: absorb an impossible error

`RaiseInfallible` is the `ErrorRaiser` provider for `core::convert::Infallible`, the error type that can never be constructed. It implements `ErrorRaiser<Context, Infallible>` for any context with an error type, producing the abstract error by matching on the uninhabited value:

```rust
#[cgp_new_provider]
impl<Context> ErrorRaiser<Context, Infallible> for RaiseInfallible
where
    Context: HasErrorType,
{
    fn raise_error(e: Infallible) -> Context::Error {
        match e {}
    }
}
```

Since an `Infallible` value cannot exist, the empty `match` is total and the function is never actually called at runtime. This provider lets generic code that is parameterized over a fallible operation be wired uniformly even when the operation chosen for a given context cannot fail.

### `DiscardDetail`: wrap by ignoring the detail

`DiscardDetail` is the `ErrorWrapper` provider that throws away whatever detail is attached and returns the error unchanged. It implements `ErrorWrapper<Context, Detail>` for any context and any detail type:

```rust
#[cgp_new_provider]
impl<Context, Detail> ErrorWrapper<Context, Detail> for DiscardDetail
where
    Context: HasErrorType,
{
    fn wrap_error(error: Context::Error, _detail: Detail) -> Context::Error {
        error
    }
}
```

This satisfies the `CanWrapError` trait without actually enriching the error, which is useful when a context's error type cannot carry extra context, or when the wrapping detail is deliberately not retained. It is the wrapping counterpart to a no-op: the error propagates as-is.

### `PanicOnError`: abort instead of producing an error

`PanicOnError` is the `ErrorRaiser` provider that panics with the source error's debug representation rather than returning an abstract error. It implements `ErrorRaiser<Context, E>` for any context whose error type exists, requiring only that the source error is `Debug`:

```rust
#[cgp_new_provider]
impl<Context, E> ErrorRaiser<Context, E> for PanicOnError
where
    Context: HasErrorType,
    E: Debug,
{
    fn raise_error(e: E) -> Context::Error {
        panic!("{e:?}")
    }
}
```

Although the signature promises a `Context::Error`, the body never returns one, because `panic!` diverges. This provider is for contexts where an error is treated as a programming fault that should abort rather than be handled, such as tests or fail-fast tooling.

### `DebugError` and `DisplayError`: format through a string

`DebugError` and `DisplayError` implement *both* error components by redirecting through the context's string-based error handling. Each formats the source error or detail into a `String` and forwards it to the context's own `CanRaiseError<String>` or `CanWrapError<String>`, so the final step is done by whatever string provider the context wires. `DebugError` formats with the `Debug` trait:

```rust
#[cgp_provider]
impl<Context, E> ErrorRaiser<Context, E> for DebugError
where
    Context: CanRaiseError<String>,
    E: Debug,
{
    fn raise_error(e: E) -> Context::Error {
        Context::raise_error(format!("{e:?}"))
    }
}

#[cgp_provider]
impl<Context, Detail> ErrorWrapper<Context, Detail> for DebugError
where
    Context: CanWrapError<String>,
    Detail: Debug,
{
    fn wrap_error(error: Context::Error, detail: Detail) -> Context::Error {
        Context::wrap_error(error, format!("{detail:?}"))
    }
}
```

`DisplayError` is identical in shape but formats with the `Display` trait and `to_string()` instead, raising `Context::raise_error(e.to_string())` and wrapping `Context::wrap_error(error, detail.to_string())`. Both require the context to already raise and wrap `String`, which is the indirection that lets them reduce any `Debug` or `Display` error to the string case the context knows how to handle. Because they allocate a `String`, both sit behind the crate's `alloc` feature, which is on by default.

## Behavior

A context wires these providers to `ErrorRaiserComponent` or `ErrorWrapperComponent` like any other provider, and each provider's `where` clause decides which source errors the wiring accepts. Because a context usually meets several source error types, it dispatches on the source type, one provider per type. The recommended form is `open ErrorRaiserComponent;` with entries such as `@ErrorRaiserComponent.String: RaiseFrom`; the legacy form is a `UseDelegate` table keyed by source type.

The string-formatting providers compose with the others rather than replacing them. `DebugError` and `DisplayError` do not know the context's error type; they turn a value into a `String` and hand it to the context's own `String` raiser or wrapper. So the context wires one concrete rule for `String`, such as `RaiseFrom` or a backend provider, and routes other source types through the formatting providers to reach it.

## Examples

This context uses `String` as its error type, raises `String` directly, formats a `ParseIntError` into a `String`, and ignores wrapping detail:

```rust
use core::num::ParseIntError;
use cgp::prelude::*;
use cgp::core::error::{ErrorRaiserComponent, ErrorTypeProviderComponent, ErrorWrapperComponent};
use cgp::extra::error::{DebugError, DiscardDetail, RaiseFrom};

pub struct App;

delegate_components! {
    App {
        open ErrorRaiserComponent;

        ErrorTypeProviderComponent: UseType<String>,
        ErrorWrapperComponent: DiscardDetail,
        @ErrorRaiserComponent.String: RaiseFrom,
        @ErrorRaiserComponent.ParseIntError: DebugError,
    }
}

fn parse<Context>(input: &str) -> Result<u64, Context::Error>
where
    Context: CanRaiseError<ParseIntError> + CanWrapError<&'static str>,
{
    input
        .parse()
        .map_err(|e| Context::wrap_error(Context::raise_error(e), "while parsing"))
}
```

A raised `String` goes through `RaiseFrom`, using the reflexive `From<String> for String`. A raised `ParseIntError` goes through `DebugError`, which formats it and raises the result through the `String` entry. So `parse::<App>("x")` returns `Err("ParseIntError { kind: InvalidDigit }")`, with the `"while parsing"` detail dropped by `DiscardDetail`.

## Related constructs

These constructs are the ones the error providers work with:

- [`CanRaiseError` and `CanWrapError`](../components/can_raise_error.md) — the components they implement, through `ErrorRaiser` and `ErrorWrapper`.
- [`HasErrorType`](../components/has_error_type.md) — the abstract error they produce.
- [`delegate_components!`](../macros/delegate_components.md) and [`UseDelegate`](use_delegate.md) — the `open` and legacy forms of per-source dispatch.
- The [error backends](../../../projects/error/README.md) — library-specific counterparts.
- [Modular error handling](../../concepts/modular-error-handling.md) — how these providers fit CGP's error strategy.

## Source

- The providers are defined in `cgp-error-extra`: `RaiseFrom` in [crates/extra/cgp-error-extra/src/impls/raise_from.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/raise_from.rs), `ReturnError` in [return_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/return_error.rs), `RaiseInfallible` in [infallible.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/infallible.rs), `DiscardDetail` in [discard_detail.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/discard_detail.rs), `PanicOnError` in [panic_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/panic_error.rs), and `DebugError`/`DisplayError` (behind the `alloc` feature) in [impls/alloc/debug_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/alloc/debug_error.rs) and [display_error.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-error-extra/src/impls/alloc/display_error.rs).
- The `ErrorRaiser`/`ErrorWrapper` provider traits and the `CanRaiseError`/`CanWrapError`/`HasErrorType` consumer traits they build on are in [crates/core/cgp-error/src/](https://github.com/contextgeneric/cgp/tree/main/crates/core/cgp-error/src/).
- The standalone backend counterparts are in [crates/standalone/error/](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error/), documented in [projects/error/](../../../projects/error/README.md).
