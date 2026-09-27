# `Computer`

`Computer` and its siblings are the infallible members of the
[handler family](../../concepts/handlers.md): components that turn an `Input` into an `Output` under
a phantom `Code` tag, in synchronous and async forms, taking the input by value or by reference.

## Purpose

The computer components are for computations that always succeed. Adding two numbers, formatting a
value, or projecting a field never fails, so returning a `Result` and requiring the context's error
type would be noise. A `Computer` provider names an `Output` type and produces it from the context,
a `Code` tag, and an `Input`, with no failure path.

It is the member a provider author reaches for first, because promotion runs one way. The
[promotion providers](../providers/handler_combinators.md) lift an infallible computer into the
fallible and async members by wrapping its output in `Ok` or its call in a future, but nothing
lowers a fallible provider back to an infallible one.

The four computer components differ along two axes:

| | owned `Input` | borrowed `&Input` |
| --- | --- | --- |
| **synchronous** | `Computer` (`CanCompute`) | `ComputerRef` (`CanComputeRef`) |
| **async** | `AsyncComputer` (`CanComputeAsync`) | `AsyncComputerRef` (`CanComputeAsyncRef`) |

The async members suit a computation that must await, such as reading a socket, and still cannot
fail. The by-reference members suit a computation that only reads its input.

## Definition

Each computer component is a `#[cgp_component]`. The synchronous, owned-input one is:

```rust
#[cgp_component(Computer)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
#[derive_delegate(UseInputDelegate<Input>)]
pub trait CanCompute<Code, Input> {
    type Output;

    fn compute(&self, _code: PhantomData<Code>, input: Input) -> Self::Output;
}
```

The parts are these:

- **`compute`** takes the context as `&self`, a `PhantomData<Code>` naming which computation is
  wanted, and the `Input` by value, and returns the associated `Output`. The provider trait
  `Computer<Context, Code, Input>` has the same method with the context as an explicit first
  argument, and `ComputerComponent` is its key.
- **The two `#[derive_delegate(...)]` attributes** generate the `UseDelegate` and `UseInputDelegate`
  impls for the legacy delegation tables that dispatch on `Code` and on `Input`. See
  [dispatching](../../concepts/dispatching.md).
- **`#[prefix(@cgp.extra.handler in DefaultNamespace)]`** registers the component in
  `DefaultNamespace` under `@cgp.extra.handler`, as every handler-family component is.

`CanComputeRef` is identical except that `compute_ref` takes `input: &Input`.

The async members declare an `async` method under [`#[async_trait]`](../macros/async_trait.md),
which rewrites it to return `impl Future<Output = Self::Output>` without boxing:

```rust
#[async_trait]
#[cgp_component(AsyncComputer)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
#[derive_delegate(UseInputDelegate<Input>)]
pub trait CanComputeAsync<Code, Input> {
    type Output;

    async fn compute_async(&self, _code: PhantomData<Code>, input: Input) -> Self::Output;
}
```

`CanComputeAsyncRef` is its by-reference counterpart, with `compute_async_ref` taking
`input: &Input`. None of the four imports `HasErrorType`, because none can fail.

The prelude exports the provider traits `Computer` and `AsyncComputer` and the keys
`ComputerComponent`, `ComputerRefComponent`, `AsyncComputerComponent`, and
`AsyncComputerRefComponent`. The consumer traits `CanCompute`, `CanComputeRef`, `CanComputeAsync`,
and `CanComputeAsyncRef`, and the provider traits `ComputerRef` and `AsyncComputerRef`, are imported
from `cgp::extra::handler`.

## Implementations

A computer provider is an ordinary provider: a zero-sized struct implementing the provider trait for
a generic context, with `Output` chosen per `Code` and `Input`. Three sources supply them:

- **`UseField<Tag>`** is the one provider the crate defines next to the components. It forwards to
  the value stored in the context's `Tag` field, for `Computer` and `AsyncComputer`:

```rust
#[cgp_provider]
impl<Context, Code, Input, Tag, Output> Computer<Context, Code, Input> for UseField<Tag>
where
    Context: HasField<Tag>,
    Context::Value: CanCompute<Code, Input, Output = Output>,
{
    type Output = Output;

    fn compute(context: &Context, code: PhantomData<Code>, input: Input) -> Output {
        context.get_field(PhantomData).compute(code, input)
    }
}
```

- **The [handler combinators](../providers/handler_combinators.md)** build computers from other
  handlers. `ReturnInput` returns its input, `ComposeHandlers` feeds one handler's output into the
  next, and the promotion providers lift one member of the family into others.
- **[`#[cgp_computer]`](../macros/cgp_computer.md)** turns a plain function into a `Computer`
  provider and wires the promotions for it.

Promotion lets one `Computer` impl answer the other members, with one limit. Lifting to
`AsyncComputer` runs the computation inside an `async` method, and lifting to `TryComputer` or
`Handler` wraps the output in `Ok`. Lifting to a `…Ref` member passes the borrow through as the
input, so it works only when the provider accepts `&'a Input` for every lifetime `'a`. A computer
written for an owned `u64` answers `compute`, `try_compute`, and `compute_async` through promotion,
but not `compute_ref`.

The promotion bundles such as `PromoteComputer<P>` expect `P` to be wired to the same bundle, as
[`#[cgp_computer]`](../macros/cgp_computer.md) wires its provider to `PromoteComputer<Self>`. Some
bundle entries take one step from a sibling rather than from the base: the `Handler` entry is
`PromoteAsync<P>`, which needs `P` to be a `TryComputer`. So wiring a context's `HandlerComponent`
to `PromoteComputer<Double>`, for a `Double` that implements only `Computer`, fails, while
`PromoteAsync<Promote<Double>>` spells both steps and works.

## Examples

This provider doubles a `u64`, and a context calls it through `CanCompute` and, by promotion,
through `CanTryCompute`:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;
use cgp::extra::handler::{CanCompute, CanTryCompute, TryComputerComponent};

#[cgp_new_provider]
impl<Context, Code> Computer<Context, Code, u64> for Double {
    type Output = u64;

    fn compute(_context: &Context, _code: PhantomData<Code>, input: u64) -> u64 {
        input * 2
    }
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
        ComputerComponent: Double,
        TryComputerComponent: PromoteComputer<Double>,
    }
}

fn run(app: &App) -> (u64, Result<u64, String>) {
    (
        app.compute(PhantomData::<()>, 21),
        app.try_compute(PhantomData::<()>, 21),
    )
}
```

`Double` implements `Computer` for any context and any `Code`, with `u64` as both input and output.
`App` wires `ComputerComponent` to it, so `compute` returns `42`, and wires `TryComputerComponent`
through the `PromoteComputer` bundle, so `try_compute` returns `Ok(42)`. The fallible member needs
the context's error type, which `App` sets to `String`. In practice
[`#[cgp_computer]`](../macros/cgp_computer.md) writes such a provider from
`fn double(input: u64) -> u64` and wires every promotion itself.

## Related constructs

These constructs are the ones the computer components work with:

- [The handler family](../../concepts/handlers.md): the axes that separate these components from the
  fallible and general members.
- [`TryComputer`](try_computer.md), [`Handler`](handler.md), and [`Producer`](producer.md): the
  fallible counterpart, the general async-and-fallible member, and the no-input member.
- [Handler combinators](../providers/handler_combinators.md): promotion, composition, and
  `ReturnInput`.
- [`#[cgp_computer]`](../macros/cgp_computer.md): turns a function into a computer provider.
- [`UseField`](../providers/use_field.md): the general provider whose computer impl is shown above.
- [`delegate_components!`](../macros/delegate_components.md): its `open` statement dispatches on
  `Code`, `Input`, or both, replacing the legacy `UseDelegate` and `UseInputDelegate` tables
  described in the [dispatching-per-type](../../guides/dispatching-per-type.md) guide.

## Source

- The synchronous computers `Computer`/`ComputerRef` are defined in
  [crates/extra/cgp-handler/src/components/computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/computer.rs),
  and the async computers `AsyncComputer`/`AsyncComputerRef` in
  [crates/extra/cgp-handler/src/components/async_computer.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/async_computer.rs).
- The `UseInputDelegate` dispatch type is in
  [crates/extra/cgp-handler/src/types.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/types.rs).
- The components are re-exported through `cgp::extra::handler`.
- For how it is generated and the index of tests, see the implementation document
  [implementation/entrypoints/cgp_computer](../../implementation/entrypoints/cgp_computer.md).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **4 pages**,
all under the handler family:
[`computer`](https://contextgeneric.dev/docs/reference/components/handler/computer) for `Computer`,
and its variant pages
[`computer_ref`](https://contextgeneric.dev/docs/reference/components/handler/computer_ref) for
`ComputerRef`,
[`async_computer`](https://contextgeneric.dev/docs/reference/components/handler/async_computer) for
`AsyncComputer`, and
[`async_computer_ref`](https://contextgeneric.dev/docs/reference/components/handler/async_computer_ref)
for `AsyncComputerRef`. A change here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the
split is recorded in [website/site-structure.md](../../../website/site-structure.md).
