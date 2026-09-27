# `Producer`

`Producer` is the no-input member of the [handler family](../../concepts/handlers.md): a synchronous, infallible component that produces an `Output` from the context and a phantom `Code` tag alone.

## Purpose

`Producer` is for computations that take no input and yield a value, such as a default configuration, a constant, or a value read entirely from the context. The rest of the family threads an `Input` through every method; `Producer` is the case where that input is absent. It is the simplest member: synchronous, infallible, and inputless.

A producer still feeds the rest of the family. Promotion turns it into any computer or handler by ignoring the input that member supplies, which is how a constant or a context-derived value enters a pipeline of input-taking handlers.

## Definition

`Producer` is a `#[cgp_component]` whose consumer trait `CanProduce` has no `Input` parameter:

```rust
#[cgp_component(Producer)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
pub trait CanProduce<Code> {
    type Output;

    fn produce(&self, _code: PhantomData<Code>) -> Self::Output;
}
```

The parts are these:

- **`produce`** takes the context as `&self` and a `PhantomData<Code>` naming which value to produce, and returns the associated `Output`. The provider trait is `Producer<Context, Code>`, wired with `ProducerComponent`.
- **`#[derive_delegate(UseDelegate<Code>)]`** generates the `UseDelegate` impl for the legacy table that dispatches on `Code`. There is no `UseInputDelegate`, since there is no input.
- **`#[prefix(@cgp.extra.handler in DefaultNamespace)]`** registers the component under `@cgp.extra.handler`, like the rest of the family.

`Producer` does not import `HasErrorType`, because it cannot fail. The prelude exports `Producer` and `ProducerComponent`; the consumer trait `CanProduce` is imported from `cgp::extra::handler`.

## Implementations

A `Producer` provider implements the provider trait for a generic context and chooses its `Output`. A constant producer has the minimal shape:

```rust
#[cgp_new_provider]
impl<Context, Code> Producer<Context, Code> for MagicNumber {
    type Output = u64;

    fn produce(_context: &Context, _code: PhantomData<Code>) -> u64 {
        42
    }
}
```

Promotion lifts a producer into the input-taking members. `Promote<P>` makes a [`Computer`](computer.md) from a producer: it accepts an input of any type, ignores it, and returns `P::produce(context, code)`. The `PromoteProducer<P>` bundle wires `ComputerComponent` to `Promote<P>` and every other handler component to `PromoteComputer<P>`, which derives them from that computer. Because the promoted computer accepts any input type, including a borrow, the `…Ref` members work too.

Like the other bundles, `PromoteProducer<P>` expects `P` to be wired to the bundle itself, as [`#[cgp_producer]`](../macros/cgp_producer.md) wires its provider to `PromoteProducer<Self>`. Its `ComputerComponent` entry works for any producer, but its fallible and async entries reach `P` through the other components and fail if `P` answers only `Producer`. The promotions are documented in [handler combinators](../providers/handler_combinators.md).

## Examples

A context wires a producer and calls it:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::extra::handler::CanProduce;

#[cgp_new_provider]
impl<Context, Code> Producer<Context, Code> for MagicNumber {
    type Output = u64;

    fn produce(_context: &Context, _code: PhantomData<Code>) -> u64 {
        42
    }
}

pub struct App;

delegate_components! {
    App {
        ProducerComponent: MagicNumber,
    }
}

fn run(app: &App) -> u64 {
    app.produce(PhantomData::<()>)
}
```

`App` delegates `ProducerComponent` to `MagicNumber`, so it implements `CanProduce<(), Output = u64>` and `run` returns `42`. The [`#[cgp_producer]`](../macros/cgp_producer.md) macro writes this provider from `fn magic_number() -> u64 { 42 }` and also wires `PromoteProducer<Self>`, so the generated `MagicNumber` answers `compute`, `compute_ref`, and the rest of the family with `42`, whatever input it is given.

## Related constructs

These constructs are the ones `Producer` works with:

- [`Computer`](computer.md), [`TryComputer`](try_computer.md), and [`Handler`](handler.md) — the input-taking members a producer promotes into, in the [handler family](../../concepts/handlers.md).
- [Handler combinators](../providers/handler_combinators.md) — `Promote` and the `PromoteProducer` bundle.
- [`#[cgp_producer]`](../macros/cgp_producer.md) — builds a producer from a zero-argument function.
- [`delegate_components!`](../macros/delegate_components.md) — its `open` statement dispatches on `Code`, replacing the legacy [`UseDelegate`](../providers/use_delegate.md) table described in [dispatching](../../concepts/dispatching.md).

## Source

- `Producer` is defined in [crates/extra/cgp-handler/src/components/produce.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/components/produce.rs).
- The `Promote` combinator that lifts it into a `Computer` is in [crates/extra/cgp-handler/src/providers/promote.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/promote.rs), and the `PromoteProducer` table in [crates/extra/cgp-handler/src/providers/promote_all.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/providers/promote_all.rs).
- The component is re-exported through `cgp::extra::handler`.
- For how it is generated and the index of tests, see the implementation document [implementation/entrypoints/cgp_producer](../../implementation/entrypoints/cgp_producer.md).
