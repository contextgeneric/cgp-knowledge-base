# Control

The control family composes other programs: a pipeline, an inline provider, a conversion, a boxed
sub-program, and the `Call` provider that turns one piece of syntax into another. Everything here is
in `hypershell-components`. How the pieces fit is in
[interpretation](../architecture/interpretation.md#control-syntax).

## `Pipe` and `HandlePipe`

`Pipe<Handlers>` runs a `Product!` list of stages end to end, feeding each stage's output to the
next. It is what `hypershell!` builds from `|`.

### Definition

```rust
pub struct Pipe<Handlers>(pub PhantomData<Handlers>);

delegate_components! {
    new HandlePipe {
        HandlerComponent: UseDelegate<new RunPipeHandler {
            <Handlers: WrapCall> Pipe<Handlers>:
                PipeHandlers<Handlers::Wrapped>,
        }>,
    }
}

pub trait WrapCall {
    type Wrapped;
}
// Cons<Head, Tail> ↦ Cons<Call<Head>, Tail::Wrapped>, and Nil ↦ Nil
```

### Behavior

`WrapCall` wraps each stage in `Call`, and CGP's
[`PipeHandlers`](../../../cgp/reference/providers/handler_combinators.md) composes the wrapped list,
so every stage is resolved through the context. The pipeline's input is the first stage's input and
its output is the last stage's output, with each intermediate type computed by the compiler. A stage
whose input bound the previous stage's output does not meet fails to compile at the pipeline.

### Known issues

The nested table uses the legacy [`UseDelegate`](../../../cgp/reference/providers/use_delegate.md)
form, which the [dispatching-per-type](../../../cgp/guides/dispatching-per-type.md) guide replaces
with `open`. A probe confirmed `open` accepts the bounded key; see
[issues.md](../issues.md#housekeeping).

## `Call`

`Call<InCode>` is a `Handler` provider that answers for any syntax by handling `InCode` on the
context.

### Definition

```rust
#[cgp_impl(new Call<InCode>)]
impl<OutCode, InCode, Input, Output> Handler<OutCode, Input>
where
    Self: CanHandle<InCode, Input, Output = Output>,
{
    type Output = Output;
    // ...
}
```

### Behavior

It re-enters the context's wiring for `InCode`. `HandlePipe` uses it for each stage, the WebSocket
bundle uses `Call<BytesToStream>` to convert a byte input, and the base bundle uses it inside
`BoxHandler<Call<Code>>`. A wiring that uses `Call<X>` depends on the context routing `X`.

## `Use` and `HandleUseProvider`

`Use<Provider, Code>` runs a named provider inline instead of the context's wiring for that stage.

### Definition

```rust
pub struct Use<Provider, Code = ()>(pub PhantomData<(Provider, Code)>);

#[cgp_impl(new HandleUseProvider)]
impl<Context, Provider, Code, Input> Handler<Use<Provider, Code>, Input> for Context
where
    Context: HasErrorType,
    Provider: Handler<Context, Code, Input>,
{ ... }
```

### Behavior

The provider calls `Provider::handle` with `Code` as the tag, so `Use<HandleBytesToHex>` runs that
provider for one stage even in a context whose namespace does not route `BytesToHex`. No program or
test in the repository uses it.

## `ConvertTo` and `HandleConvert`

`ConvertTo<T>` converts its input with `Into<T>`.

### Definition

```rust
pub struct ConvertTo<T>(pub PhantomData<T>);

#[cgp_impl(new HandleConvert)]
impl<Input, Output> Computer<ConvertTo<Output>, Input>
where
    Input: Into<Output>,
{ ... }
```

### Behavior

`HandleConvert` is a synchronous [`Computer`](../../../cgp/reference/components/computer.md), so the
base bundle lifts it twice and wires the syntax as `Promote<PromoteAsync<HandleConvert>>`:
`PromoteAsync` makes it an `AsyncComputer`, and `Promote` makes that a `Handler`; see the
[handler combinators](../../../cgp/reference/providers/handler_combinators.md). A probe ran
`ConvertTo<String>` on `HypershellCli` with a `&str` input and got the `String` back.

## `Box` and `BoxHandler`

`Box<Code>`, the standard library's `Box` used as syntax, runs `Code` with its future boxed.

### Definition

```rust
#[cgp_impl(new BoxHandler<InHandler>)]
#[use_type(HasErrorType.Error)]
#[use_provider(InHandler: Handler<Code, Input>)]
impl<Code, Input, InHandler> Handler<Code, Input>
where
    InHandler: 'static,
    Code: 'static,
    Input: 'static,
{
    type Output = InHandler::Output;

    fn handle(
        &self,
        code: PhantomData<Code>,
        input: Input,
    ) -> impl Future<Output = Result<Self::Output, Error>> { ... }
}
```

### Behavior

`BoxHandler` pins the inner provider's future as `Pin<Box<dyn Future<…>>>` and returns it, erasing
the future's type. The base bundle maps `Box<Code>` to `BoxHandler<Call<Code>>`, so
`Box<hypershell!{ … }>` is a sub-program run behind a box. A probe ran one successfully. The examples
crate wires its `Compare` syntax to `BoxHandler<HandleCompare>` directly, noting that the comparison
is much slower otherwise. The boxed future is not `Send`, since the `dyn Future` carries no `Send`
bound.

## `ReturnInput`

`ReturnInput` is an identity handler: its output is its input.

### Definition

```rust
#[cgp_impl(new ReturnInput)]
impl<Context, Code, Input> Handler<Code, Input> for Context
where
    Context: HasErrorType,
{
    type Output = Input;
    // ...
}
```

### Behavior

`HandleToTokioAsyncRead` uses it to pass a `TokioAsyncReadStream` through unchanged.

### Known issues

It duplicates `cgp::extra::handler::ReturnInput`, which implements `Handler` with the same bound, and
the two share a name; see [issues.md](../issues.md#housekeeping).

## Source

- [crates/hypershell-components/src/dsl/pipe.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/pipe.rs), [use.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/use.rs), and [convert.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/convert.rs)
- [crates/hypershell-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/providers): `pipe.rs`, `call.rs`, `use.rs`, `convert.rs`, `box_async.rs`, `return.rs`
- [crates/hypershell-components/src/traits/wrap_call.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/traits/wrap_call.rs)

## Public material derived from this

Rustdoc for the control items.
