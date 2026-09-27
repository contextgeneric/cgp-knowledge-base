# `TryComputer`

`TryComputer` and `TryComputerRef` are the fallible synchronous members of the [handler family](../../concepts/handlers.md): components that turn an `Input` into an `Output` under a phantom `Code` tag and return a `Result` in the context's abstract error type.

## Purpose

`TryComputer` is for synchronous computations that can fail. Parsing a string, looking up a key, or checking an invariant may not produce an output, so the method returns `Result<Output, Error>` instead of the bare `Output` of [`Computer`](computer.md). It sits between `Computer`, which cannot fail, and [`Handler`](handler.md), which is also async.

The error is the context's abstract error, not a concrete type, which keeps a provider generic. A provider returns `Self::Error`, and the context decides the concrete type when it wires an error type. Because every fallible component in the context names the same [`HasErrorType`](has_error_type.md) error, their results compose with `?`.

## Definition

`TryComputer` is a `#[cgp_component]` that imports the abstract error with [`#[use_type(HasErrorType.Error)]`](../attributes/use_type.md):

```rust
#[cgp_component(TryComputer)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
#[derive_delegate(UseInputDelegate<Input>)]
#[use_type(HasErrorType.Error)]
pub trait CanTryCompute<Code, Input> {
    type Output;

    fn try_compute(&self, _code: PhantomData<Code>, input: Input) -> Result<Self::Output, Error>;
}
```

The parts are these:

- **`try_compute`** takes `&self`, a `PhantomData<Code>` naming the computation, and the `Input` by value, and returns the `Output` or the context's error. The provider trait is `TryComputer<Context, Code, Input>`, wired with `TryComputerComponent`.
- **`#[use_type(HasErrorType.Error)]`** adds `HasErrorType` as a supertrait and rewrites the bare `Error` to `<Self as HasErrorType>::Error`. The trait's own `Output` stays written as `Self::Output`.
- **The `#[derive_delegate(...)]` and `#[prefix(...)]` attributes** are the same as on every handler-family component: legacy delegation tables on `Code` and `Input`, and registration under `@cgp.extra.handler` in `DefaultNamespace`.

`TryComputerRef`, with consumer trait `CanTryComputeRef`, is identical except that `try_compute_ref` takes `input: &Input`.

The prelude exports the provider trait `TryComputer` and the keys `TryComputerComponent` and `TryComputerRefComponent`. The consumer traits `CanTryCompute` and `CanTryComputeRef` and the provider trait `TryComputerRef` are imported from `cgp::extra::handler`.

## Implementations

A `TryComputer` provider implements the provider trait for a generic context that has an error type, so its `where` clause carries `Context: HasErrorType`. The crate's `ReturnInput` shows the minimal shape, succeeding with its input:

```rust
#[cgp_provider]
impl<Context, Code, Input> TryComputer<Context, Code, Input> for ReturnInput
where
    Context: HasErrorType,
{
    type Output = Input;

    fn try_compute(
        _context: &Context,
        _code: PhantomData<Code>,
        input: Input,
    ) -> Result<Self::Output, Context::Error> {
        Ok(input)
    }
}
```

The [promotion providers](../providers/handler_combinators.md) connect `TryComputer` to its neighbors:

- **`Promote<P>`** makes a `TryComputer` from an infallible `Computer` by wrapping its output in `Ok`.
- **`TryPromote<P>`** converts in both directions between a `TryComputer` and a `Computer` whose `Output` is `Result<T, Context::Error>`. As a `TryComputer` it passes the computer's result through, and as a `Computer` it returns the fallible provider's result as a plain value.
- **`PromoteAsync<P>`** makes an async `Handler` from a `TryComputer` by running it inside an `async` method.

## Examples

This provider parses a `String` into a `u64` and raises the parse error into the context's error:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::core::error::{ErrorRaiserComponent, ErrorTypeProviderComponent};
use cgp::extra::error::RaiseFrom;
use cgp::extra::handler::{CanTryCompute, TryComputerComponent};

#[cgp_impl(new ParseU64)]
#[uses(CanRaiseError<core::num::ParseIntError>)]
#[use_type(HasErrorType.Error)]
impl<Code> TryComputer<Code, String> {
    type Output = u64;

    fn try_compute(
        &self,
        _code: PhantomData<Code>,
        input: String,
    ) -> Result<Self::Output, Error> {
        input.parse().map_err(|e| Self::raise_error(e))
    }
}

#[derive(Debug)]
pub struct AppError(String);

impl From<core::num::ParseIntError> for AppError {
    fn from(e: core::num::ParseIntError) -> Self {
        AppError(e.to_string())
    }
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<AppError>,
        ErrorRaiserComponent: RaiseFrom,
        TryComputerComponent: ParseU64,
    }
}
```

`ParseU64` names neither the context nor its error type. `App` supplies both: its error type is `AppError`, and `RaiseFrom` raises the `ParseIntError` through `AppError`'s `From` impl. So `App.try_compute(PhantomData::<()>, "12".to_owned())` returns `Ok(12)`, and a non-numeric input returns `Err(AppError(...))`.

A function returning `Result<u64, String>` becomes a similar provider through [`#[cgp_computer]`](../macros/cgp_computer.md). The generated provider implements `Computer` with the `Result` as its output, and its `PromoteTryComputer` bundle derives `TryComputer` from it through `TryPromote`.

## Related constructs

These constructs are the ones `TryComputer` works with:

- [`Computer`](computer.md) and [`Handler`](handler.md) — its infallible counterpart and its async generalization, in the [handler family](../../concepts/handlers.md).
- [`HasErrorType`](has_error_type.md) and [`CanRaiseError`](can_raise_error.md) — the error it returns and the usual way to build that error.
- [Handler combinators](../providers/handler_combinators.md) — `Promote`, `TryPromote`, `PromoteAsync`, and the promotion bundles.
- [`#[cgp_computer]`](../macros/cgp_computer.md) — builds a provider from a fallible function.
- [`delegate_components!`](../macros/delegate_components.md) — its `open` statement dispatches on `Code` or `Input`, replacing the legacy [`UseDelegate`](../providers/use_delegate.md) and `UseInputDelegate` tables described in the [dispatching-per-type](../../guides/dispatching-per-type.md) guide.

## Source

- `TryComputer` and `TryComputerRef` are defined in [crates/extra/cgp-handler/src/components/try_compute.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/try_compute.rs).
- The `ReturnInput` provider is in [crates/extra/cgp-handler/src/providers/return_input.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/return_input.rs), and the promotion combinators in [crates/extra/cgp-handler/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/).
- The components are re-exported through `cgp::extra::handler`.
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/cgp_computer](../../implementation/entrypoints/cgp_computer.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **2 pages** under the handler family: [`try_computer`](https://contextgeneric.dev/docs/reference/components/handler/try_computer) for `TryComputer` and [`try_computer_ref`](https://contextgeneric.dev/docs/reference/components/handler/try_computer_ref) for its by-reference variant `TryComputerRef`. A change here is propagated to both, per the [synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the split is recorded in [website/site-structure.md](../../../website/site-structure.md).
