# Handler combinators

The handler combinators are the provider structs of `cgp-handler` that build, sequence, and adapt
handlers: they compose providers end to end, thread a list of providers through a pipeline, return
the input unchanged, and lift a provider written for one member of the handler family into another.

## Purpose

The combinators let a provider written for one handler trait be used wherever another is wanted, and
let small providers be glued into larger ones. The handler family is several related traits,
[`Computer`](../components/computer.md), [`TryComputer`](../components/try_computer.md),
`AsyncComputer`, [`Handler`](../components/handler.md), and [`Producer`](../components/producer.md),
most with a `…Ref` variant. An author writes whichever shape is natural for the computation, and the
combinators supply the rest without reimplementing it for every trait.

They do three jobs:

- **Composition.** `ComposeHandlers` and `PipeHandlers` sequence handlers, so the output of one
  becomes the input of the next.
- **Identity.** `ReturnInput` passes its input straight through, the neutral element of composition.
- **Promotion.** `Promote`, `PromoteAsync`, `PromoteRef`, `TryPromote`, and the promotion bundles
  lift a provider from one handler trait to another.

Every combinator is a zero-sized provider whose type parameters are inner providers held in
`PhantomData`. The work happens at the type level through delegation, so the combinators nest
freely.

## The handler family

Every member shares one method shape: a context reference, a `PhantomData<Code>` tag selecting the
operation, and an input, producing an associated `Output`. The members differ in fallibility and
asynchrony:

| | infallible | fallible (`Result<Output, Context::Error>`) |
| --- | --- | --- |
| **synchronous** | `Computer` | `TryComputer` |
| **async** | `AsyncComputer` | `Handler` |

Each of the four has a `…Ref` companion whose method takes `&Input`. `Producer` takes no input at
all.

Promotion follows the natural inclusions among these. An infallible provider is a fallible one that
always returns `Ok`, and a synchronous provider is an async one whose future is ready at once. A
by-reference provider serves an owned-input slot by dereferencing the input, and an owned-input
provider serves a by-reference slot only if it accepts a borrow as its input. Nothing goes the other
way: a fallible or async provider cannot be lowered.

## Composing handlers in sequence

`ComposeHandlers<ProviderA, ProviderB>` runs two handlers back to back, feeding the first one's
output to the second as its input:

```rust
pub struct ComposeHandlers<ProviderA, ProviderB>(pub PhantomData<(ProviderA, ProviderB)>);
```

For `Computer`, it requires `ProviderA: Computer<Context, Code, Input>` and
`ProviderB: Computer<Context, Code, ProviderA::Output>`, and its `Output` is `ProviderB::Output`:

```rust
#[cgp_provider]
impl<Context, Code, Input, ProviderA, ProviderB> Computer<Context, Code, Input>
    for ComposeHandlers<ProviderA, ProviderB>
where
    ProviderA: Computer<Context, Code, Input>,
    ProviderB: Computer<Context, Code, ProviderA::Output>,
{
    type Output = ProviderB::Output;

    fn compute(context: &Context, code: PhantomData<Code>, input: Input) -> Self::Output {
        let intermediary = ProviderA::compute(context, code, input);
        ProviderB::compute(context, code, intermediary)
    }
}
```

The same impl exists for `TryComputer`, `AsyncComputer`, and `Handler`, and for no other member:
`ComposeHandlers` has no `…Ref` or `Producer` impl. The fallible impls short-circuit on the first
error with `?` and require `Context: HasErrorType`, and the async impls `.await` each step. Both
providers always share one context and one `Code`; only the value between them changes type.

## Composing a list of handlers

`PipeHandlers<Providers>` extends `ComposeHandlers` to a [`Product!`](../macros/product.md) list of
providers:

```rust
pub struct PipeHandlers<Providers>(pub PhantomData<Providers>);
```

It has no handler impls of its own. Instead it delegates every component to the single provider its
list folds to:

```rust
delegate_components! {
    <Component, Provider, Providers: ComposeProviders<Provider = Provider>>
    PipeHandlers<Providers> {
        Component: Provider,
    }
}
```

The private `ComposeProviders` trait does the fold. A one-element list folds to its only provider,
and `Cons<A, Cons<B, Rest>>` folds to `ComposeHandlers<A, fold(Cons<B, Rest>)>`. An empty list has
no fold, so `PipeHandlers<Product![]>` provides nothing.

So `PipeHandlers<Product![A, B, C]>` is `ComposeHandlers<A, ComposeHandlers<B, C>>`: the input
passes through `A`, then `B`, then `C`. Because the delegation is generic over the component key,
the same pipeline serves whichever of `Computer`, `TryComputer`, `AsyncComputer`, or `Handler` the
wiring asks for, provided every stage supports that member.

## Returning the input unchanged

`ReturnInput` is the identity handler, a unit struct that ignores the context and `Code` and returns
its input:

```rust
pub struct ReturnInput;
```

It implements `Computer`, `TryComputer`, `AsyncComputer`, and `Handler` with `Output = Input`,
wrapping the input in `Ok` for the fallible members, which therefore require
`Context: HasErrorType`. Composing it before or after a handler leaves that handler unchanged, so it
serves as a placeholder stage or as the base case of a pipeline built step by step.

## Promoting a provider to another member

Each promotion combinator takes one inner `Provider` and implements some target traits in terms of
the provider's source trait. Each takes exactly one step:

| Combinator | Implements | From an inner provider that is | By |
| --- | --- | --- | --- |
| `Promote<P>` | `Computer` | `Producer` | ignoring the input |
| `Promote<P>` | `TryComputer` | `Computer` | wrapping the output in `Ok` |
| `Promote<P>` | `Handler` | `AsyncComputer` | wrapping the awaited output in `Ok` |
| `PromoteAsync<P>` | `AsyncComputer` | `Computer` | running it inside an `async` method |
| `PromoteAsync<P>` | `Handler` | `TryComputer` | running it inside an `async` method |
| `TryPromote<P>` | `TryComputer` | `Computer` with `Output = Result<T, Context::Error>` | passing the result through |
| `TryPromote<P>` | `Computer` | `TryComputer` | returning the result as a plain value |
| `TryPromote<P>` | `Handler` | `AsyncComputer` with `Output = Result<T, Context::Error>` | passing the result through |
| `TryPromote<P>` | `AsyncComputer` | `Handler` | returning the result as a plain value |
| `PromoteRef<P>` | each owned-input member | its `…Ref` companion | dereferencing the input |
| `PromoteRef<P>` | each `…Ref` member | its owned-input companion, for every `&'a Input` | passing the borrow as the input |

Every `TryPromote` impl, and every impl whose target or source is fallible, requires
`Context: HasErrorType`.

`PromoteRef` covers `Computer`, `TryComputer`, `AsyncComputer`, and `Handler`, in both directions.
The owned-input direction requires `Input: Deref<Target = Target>` and calls the inner `…Ref`
provider on `input.deref()`, so a provider written for `&T` serves a slot that hands it a `Box<T>`
or another smart pointer. The by-reference direction requires
`P: for<'a> Computer<Context, Code, &'a Input>` (or the matching trait) and passes the borrow
through. A provider written for an owned `u64` does not meet that bound, so it cannot answer
`compute_ref` through `PromoteRef`.

A lift that takes two steps chains the combinators. A plain `Computer` becomes a `Handler` as
`PromoteAsync<Promote<P>>`: `Promote` makes the `TryComputer`, and `PromoteAsync` makes the
`Handler` from it.

## Promotion bundles

A promotion bundle is a delegation table, defined with
[`delegate_components!`](../macros/delegate_components.md), that wires every other member of the
family to the right one-step combinator for a given base. It lets an author implement one trait and
have the bundle answer the rest. [`#[cgp_computer]`](../macros/cgp_computer.md) and
[`#[cgp_producer]`](../macros/cgp_producer.md) wire their generated providers into one.

`PromoteComputer<Provider>` fills in the family from a `Computer` base:

```rust
delegate_components! {
    <Provider>
    new PromoteComputer<Provider> {
        ComputerRefComponent: PromoteRef<Provider>,
        TryComputerComponent: Promote<Provider>,
        TryComputerRefComponent: PromoteRef<Provider>,
        AsyncComputerComponent: PromoteAsync<Provider>,
        AsyncComputerRefComponent: PromoteRef<Provider>,
        HandlerComponent: PromoteAsync<Provider>,
        HandlerRefComponent: PromoteRef<Provider>,
    }
}
```

Several entries take their one step from a sibling rather than from the base.
`HandlerComponent: PromoteAsync<Provider>` needs `Provider: TryComputer`, and each
`PromoteRef<Provider>` entry needs `Provider` to answer the matching owned-input member. So a bundle
expects its parameter to be a provider wired to that same bundle, which is what the macros do by
passing `Self`: the generated provider delegates `TryComputerComponent` to `Promote<Self>`, and
`PromoteAsync<Self>` then finds that `TryComputer`. Wiring a context's `HandlerComponent` to
`PromoteComputer<MyComputer>`, for a provider that implements only `Computer`, fails; the
hand-written form is `PromoteAsync<Promote<MyComputer>>`.

The other bundles follow the same pattern from other bases:

- **`PromoteTryComputer<Provider>`** starts from a `Computer` whose `Output` is a `Result`, the base
  `#[cgp_computer]` generates for a function returning `Result`. It routes `TryComputerComponent` to
  `TryPromote<Provider>` and the rest to `PromoteComputer<Provider>`.
- **`PromoteProducer<Provider>`** starts from a `Producer`. It routes `ComputerComponent` to
  `Promote<Provider>`, which ignores the input, and the rest to `PromoteComputer<Provider>`.
- **`PromoteAsyncComputer<Provider>`** starts from an `AsyncComputer`. It routes `HandlerComponent`
  to `Promote<Provider>` and `AsyncComputerRefComponent` and `HandlerRefComponent` to
  `PromoteRef<Provider>`.
- **`PromoteHandler<Provider>`** starts from an `AsyncComputer` whose `Output` is a `Result`. It
  routes `HandlerComponent` to `TryPromote<Provider>` and `AsyncComputerRefComponent` and
  `HandlerRefComponent` to `PromoteAsyncComputer<Provider>`.

The async bundles fill in only the async members, because the synchronous ones cannot be derived
from an async base.

## Dispatching on the input type

The recommended way to choose a handler by its input type is the `open` statement with a two-segment
path key. The [`RedirectLookup`](redirect_lookup.md) impl behind `open` appends every type parameter
of the consumer trait to the lookup path, so a handler component's path is `Code` then `Input`, and
a per-entry generic first segment dispatches on the input alone:

```rust
delegate_components! {
    Interpreter {
        open ComputerComponent;

        @ComputerComponent.<Code> Code.MathExpr: DispatchEval,
        @ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd,
        @ComputerComponent.<Code> Code.Literal<Value>: EvalLiteral,
    }
}
```

Replacing `<Code> Code` with a concrete code dispatches on both parameters, as in
`@ComputerComponent.Eval.Plus<MathExpr>: EvalAdd`. The same form works inside an aggregate provider,
which is how a reusable input dispatcher is packaged. The key forms, and the restriction that a key
cannot share a table with a longer key beneath it, are in the `open` section of
[`delegate_components!`](../macros/delegate_components.md).

### The legacy form: `UseInputDelegate`

`UseInputDelegate<Components>` is the older, table-based dispatcher for the same job, still common
in existing code and in the [dispatch combinators](dispatch_combinators.md):

```rust
pub struct UseInputDelegate<Components>(pub PhantomData<Components>);
```

It is the `Input`-keyed sibling of [`UseDelegate`](use_delegate.md), which keys on `Code`. Every
handler component except `Producer` declares both `#[derive_delegate(UseDelegate<Code>)]` and
`#[derive_delegate(UseInputDelegate<Input>)]`, and the second generates an impl that looks the
`Input` type up in `Components` and forwards to the delegate found there:

```rust
impl<Context, Code, Input, Components, Delegate> Computer<Context, Code, Input>
    for UseInputDelegate<Components>
where
    Components: DelegateComponent<Input, Delegate = Delegate>,
    Delegate: Computer<Context, Code, Input>,
{
    type Output = Delegate::Output;

    fn compute(context: &Context, code: PhantomData<Code>, input: Input) -> Self::Output {
        Delegate::compute(context, code, input)
    }
}
```

`Context` and `Code` pass through unchanged. A context wires it with a nested table: the outer entry
routes a handler component to `UseInputDelegate<SomeTable>`, and the inner table maps each input
type to its provider.

## Examples

This pipeline of computers reads a factor or an addend from context fields at each stage:

```rust
use core::marker::PhantomData;
use cgp::prelude::*;
use cgp::extra::handler::{CanCompute, PipeHandlers};

#[cgp_new_provider]
impl<Context, Tag, Field> Computer<Context, Tag, u64> for Multiply<Field>
where
    Context: HasField<Field, Value = u64>,
{
    type Output = u64;

    fn compute(context: &Context, _tag: PhantomData<Tag>, input: u64) -> u64 {
        input * context.get_field(PhantomData)
    }
}

#[cgp_new_provider]
impl<Context, Tag, Field> Computer<Context, Tag, u64> for Add<Field>
where
    Context: HasField<Field, Value = u64>,
{
    type Output = u64;

    fn compute(context: &Context, _tag: PhantomData<Tag>, input: u64) -> u64 {
        input + context.get_field(PhantomData)
    }
}

#[derive(HasField)]
pub struct MyContext {
    pub foo: u64,
    pub bar: u64,
    pub baz: u64,
}

delegate_components! {
    MyContext {
        ComputerComponent:
            PipeHandlers<Product![
                Multiply<Symbol!("foo")>,
                Add<Symbol!("bar")>,
                Multiply<Symbol!("baz")>,
            ]>,
    }
}
```

The pipeline is `ComposeHandlers<Multiply<…>, ComposeHandlers<Add<…>, Multiply<…>>>`. With
`foo = 2`, `bar = 3`, and `baz = 4`, `context.compute(PhantomData::<()>, 5)` returns
`((5 * 2) + 3) * 4`. To wire the same stages to `HandlerComponent`, lift each `Computer` stage with
`PromoteAsync<Promote<…>>`, as in `PromoteAsync<Promote<Add<Symbol!("bar")>>>`, and give the context
an error type.

## Related constructs

These constructs are the ones the handler combinators work with:

- [`Computer`](../components/computer.md), [`TryComputer`](../components/try_computer.md),
  [`Handler`](../components/handler.md), and [`Producer`](../components/producer.md): the traits
  they implement, with the overview in [handlers](../../concepts/handlers.md).
- [`#[cgp_computer]`](../macros/cgp_computer.md) and [`#[cgp_producer]`](../macros/cgp_producer.md):
  generate a one-trait provider and wire it into a promotion bundle.
- [`UseDelegate`](use_delegate.md) and [`#[derive_delegate]`](../attributes/derive_delegate.md): the
  `Code`-keyed sibling of `UseInputDelegate`, and the attribute that generates both.
- [`delegate_components!`](../macros/delegate_components.md) and
  [`RedirectLookup`](redirect_lookup.md): the `open` form of input dispatch.
- [Monad providers](monad_providers.md): `PipeMonadic` and the bind combinators that extend
  `PipeHandlers` with short-circuiting.

## Source

- The combinators are defined in `cgp-handler` under
  [crates/extra/cgp-handler/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/providers/):
  `compose.rs` (`ComposeHandlers`), `pipe.rs` (`PipeHandlers` and the internal `ComposeProviders`
  fold), `return_input.rs` (`ReturnInput`), `promote.rs` (`Promote`), `promote_async.rs`
  (`PromoteAsync`), `promote_ref.rs` (`PromoteRef`), `try_promote.rs` (`TryPromote`), and
  `promote_all.rs` (the `PromoteComputer`, `PromoteTryComputer`, `PromoteProducer`,
  `PromoteAsyncComputer`, and `PromoteHandler` bundles).
- `UseInputDelegate` is defined in
  [crates/extra/cgp-handler/src/types.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-handler/src/types.rs),
  and its provider impls are generated from the `#[derive_delegate(UseInputDelegate<Input>)]`
  directive on the handler component traits in
  [crates/extra/cgp-handler/src/components/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/components/).
