# `Handler`

`Handler` and `HandlerRef` are the most general members of the
[handler family](../../concepts/handlers.md): async, fallible components that turn an `Input` into
an `Output` under a phantom `Code` tag and return a `Result` in the context's abstract error type.

## Purpose

`Handler` is for computations that must both await and fail, such as a call to a remote service.
Every other member of the family drops one of these properties: without failure a `Handler` is an
[`AsyncComputer`](computer.md), without asynchrony it is a [`TryComputer`](try_computer.md), and
without both it is a [`Computer`](computer.md).

That generality makes `Handler` the bound for generic code that should accept any computation. Every
simpler provider can be promoted to a `Handler`: a computer becomes a handler that neither awaits
nor fails, a fallible computer becomes one that does not await, and an async computer becomes one
that never fails. The reverse is impossible, because a general computation cannot be assumed
synchronous or infallible. So a provider author implements the weakest member that fits, and the
wiring lifts it to `Handler` where a handler is needed.

## Definition

`Handler` is a `#[cgp_component]` under [`#[async_trait]`](../macros/async_trait.md) that imports
the abstract error with [`#[use_type(HasErrorType.Error)]`](../attributes/use_type.md):

```rust
#[async_trait]
#[cgp_component(Handler)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
#[derive_delegate(UseInputDelegate<Input>)]
#[use_type(HasErrorType.Error)]
pub trait CanHandle<Code, Input> {
    type Output;

    async fn handle(&self, _tag: PhantomData<Code>, input: Input) -> Result<Self::Output, Error>;
}
```

The parts are these:

- **`handle`** is the async counterpart of `try_compute` and the fallible counterpart of
  `compute_async`. `#[async_trait]` rewrites it to return
  `impl Future<Output = Result<Self::Output, Error>>`, with no boxing and no added `Send` bound. The
  provider trait is `Handler<Context, Code, Input>`, wired with `HandlerComponent`.
- **`#[use_type(HasErrorType.Error)]`** adds `HasErrorType` as a supertrait and rewrites the bare
  `Error` to `<Self as HasErrorType>::Error`.
- **The `#[derive_delegate(...)]` and [`#[prefix(...)]`](../attributes/prefix.md) attributes** are
  the same as on every handler-family component: legacy delegation tables on `Code` and `Input`, and
  registration under `@cgp.extra.handler` in `DefaultNamespace`.

`HandlerRef`, with consumer trait `CanHandleRef`, is identical except that `handle_ref` takes
`input: &Input`.

The prelude exports the provider trait `Handler` and the keys `HandlerComponent` and
`HandlerRefComponent`. The consumer traits `CanHandle` and `CanHandleRef`, the provider trait
`HandlerRef`, and the one-step promotion providers are imported from `cgp::extra::handler`.

## Implementations

A `Handler` provider implements the provider trait for a generic context with an error type. The
crate's `ReturnInput` shows the minimal shape, awaiting nothing and succeeding with its input:

```rust
#[cgp_provider]
impl<Context, Code, Input> Handler<Context, Code, Input> for ReturnInput
where
    Context: HasErrorType,
{
    type Output = Input;

    async fn handle(
        _context: &Context,
        _code: PhantomData<Code>,
        input: Input,
    ) -> Result<Self::Output, Context::Error> {
        Ok(input)
    }
}
```

Most `Handler` impls come from the [promotion providers](../providers/handler_combinators.md) rather
than from hand-written code. Each promotion takes one step:

- **`PromoteAsync<P>`** makes a `Handler` from a `TryComputer` by running it inside an `async`
  method.
- **`Promote<P>`** makes a `Handler` from an `AsyncComputer` by wrapping its awaited output in `Ok`.
- **`TryPromote<P>`** makes a `Handler` from an `AsyncComputer` whose `Output` is already
  `Result<T, Context::Error>`.
- **`PromoteRef<P>`** converts between `Handler` and `HandlerRef`, dereferencing an owned input or
  passing a borrow through. The borrow direction needs a `Handler` written for `&'a Input` at every
  lifetime, and it is the `HandlerRefComponent` entry every promotion bundle ends in.

A plain `Computer` takes two steps, as `PromoteAsync<Promote<P>>`. The promotion bundles and
[`#[cgp_computer]`](../macros/cgp_computer.md) chain these steps for the author; a provider that
`#[cgp_computer]` or [`#[cgp_producer]`](../macros/cgp_producer.md) generates is wired to its own
bundle, so a context wires `HandlerComponent` to it directly.

## Examples

A generic function bounded by `CanHandle` accepts any handler the context wires:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::extra::handler::CanHandle;

async fn run_with<Context, Code>(
    context: &Context,
    input: String,
) -> Result<Context::Output, Context::Error>
where
    Context: CanHandle<Code, String>,
{
    context.handle(PhantomData::<Code>, input).await
}
```

`run_with` works for any context whose `HandlerComponent` answers the given `Code` with a `String`
input. The provider behind it may be a genuine `Handler` or a simpler provider lifted by promotion,
such as a `Computer` wired as `PromoteAsync<Promote<MyComputer>>`, or one generated by
[`#[cgp_computer]`](../macros/cgp_computer.md) or [`#[cgp_producer]`](../macros/cgp_producer.md),
which wire their own promotions.

A context answers that bound with a synchronous computer lifted in two steps:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::core::error::ErrorTypeProviderComponent;
use cgp::extra::handler::{CanHandle, Promote, PromoteAsync};

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
        HandlerComponent: PromoteAsync<Promote<Double>>,
    }
}

check_components! {
    App {
        HandlerComponent: ((), u64),
    }
}
```

`App.handle(PhantomData::<()>, 21).await` returns `Ok(42)`.

A `HandlerRef` provider awaits and may fail over a borrowed input. This one raises a `String`
message into a context whose error type is `String`, so `RaiseFrom` raises it through the identity
`From` impl:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::core::error::{ErrorRaiserComponent, ErrorTypeProviderComponent};
use cgp::extra::error::RaiseFrom;
use cgp::extra::handler::{CanHandleRef, HandlerRef};

#[cgp_impl(new NonEmptyLength)]
#[uses(CanRaiseError<String>)]
#[use_type(HasErrorType.Error)]
impl<Code> HandlerRef<Code, String> {
    type Output = usize;

    async fn handle_ref(
        &self,
        _code: PhantomData<Code>,
        input: &String,
    ) -> Result<Self::Output, Error> {
        if input.is_empty() {
            return Err(Self::raise_error("empty request".to_owned()));
        }

        Ok(input.len())
    }
}

pub struct App;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>,
        ErrorRaiserComponent: RaiseFrom,
        HandlerRefComponent: NonEmptyLength,
    }
}
```

`App.handle_ref(PhantomData::<()>, &request).await` returns `Ok(request.len())` for a non-empty
request and `Err("empty request".to_owned())` for an empty one.

## Related constructs

These constructs are the ones `Handler` works with:

- [`Computer`, `AsyncComputer`](computer.md), and [`TryComputer`](try_computer.md): the simpler
  members it generalizes, and [`Producer`](producer.md), the no-input member.
- [`HasErrorType`](has_error_type.md): the supertrait whose error it returns.
- [Handler combinators](../providers/handler_combinators.md): promotion, composition, and piping.
- [Monadic handlers](../../concepts/monadic-handlers.md): chaining handlers into pipelines.
- [`delegate_components!`](../macros/delegate_components.md): its `open` statement dispatches on
  `Code` or `Input`, replacing the legacy [`UseDelegate`](../providers/use_delegate.md) and
  `UseInputDelegate` tables described in the
  [dispatching-per-type](../../guides/dispatching-per-type.md) guide.

## Known issues

**A promotion bundle wired on a context expects its provider to be wired to the same bundle.** The
`HandlerComponent` entry of `PromoteComputer<P>` is `PromoteAsync<P>`, which needs `P` to be a
`TryComputer`. Wiring a context's `HandlerComponent` to `PromoteComputer<Double>`, for a
hand-written `Double` that implements only `Computer`, fails at the check with
``error[E0277]: the trait bound `Double: DelegateComponent<TryComputerComponent>` is not satisfied``
and the note ``required for `Double` to implement `TryComputer<App, (), u64>` ``. The hand-written
form is `PromoteAsync<Promote<Double>>`; a `#[cgp_computer]` provider needs neither, since it is
wired to `PromoteComputer<Self>`.

A concrete context calling `App::handle(…)` by bare name is ambiguous (`E0034`) when the `Handler`
provider trait is in scope, as it is through the prelude, for the reason given in
[`Computer`'s Known issues](computer.md#known-issues).

## Source

- `Handler` and `HandlerRef` are defined in
  [crates/extra/cgp-handler/src/components/handler.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/handler.rs).
- The `ReturnInput` provider is in
  [crates/extra/cgp-handler/src/providers/return_input.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/return_input.rs),
  and the promotion combinators that lift simpler providers into `Handler` are in
  [crates/extra/cgp-handler/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/).
- The components are re-exported through `cgp::extra::handler`.

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **2 pages**
under the handler family:
[`handler`](https://contextgeneric.dev/docs/reference/components/handler/handler) for `Handler` and
[`handler_ref`](https://contextgeneric.dev/docs/reference/components/handler/handler_ref) for its
by-reference variant `HandlerRef`. A change here is propagated to both, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the granularity rule behind the
split is recorded in [website/site-structure.md](../../../website/site-structure.md).
