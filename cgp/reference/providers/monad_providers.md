# Monad providers

The monad providers compose a list of handlers under a chosen monad into one handler that short-circuits on the monad's stop case. `PipeMonadic` builds the pipeline, the markers `IdentMonadic`, `OkMonadic`, and `ErrMonadic` (with their transformer forms) name the monad, and `BindOk` and `BindErr` implement one branching step.

## Purpose

These providers implement [monadic handler composition](../../concepts/monadic-handlers.md) on the [`Computer`](../components/computer.md) family. They chain handlers whose outputs carry a "continue" case and a "stop" case, such as `Ok` and `Err`, without matching on each step by hand: the monad decides which case feeds the next handler and which ends the pipeline. A built pipeline is itself a provider of `Computer`, `AsyncComputer`, `TryComputer`, and `Handler`, so it wires into a context like any other handler.

The providers form three groups:

- **`PipeMonadic`**, the entry point a user wires or calls.
- **The monad markers**, zero-sized types that select the short-circuiting behavior.
- **The bind providers**, the per-step building blocks `PipeMonadic` composes, also usable directly inside a plain [`PipeHandlers`](handler_combinators.md) list.

None is in the prelude. `PipeMonadic` is imported from `cgp::extra::monad::providers`, and the markers and binds from `cgp::extra::monad::monadic::{ident, ok, err}`.

## The pipeline provider

`PipeMonadic<M, Providers>` composes the handler list `Providers` under the monad `M`:

```rust
pub struct PipeMonadic<M, Providers>(pub PhantomData<(M, Providers)>);
```

`Providers` is a [`Product!`](../macros/product.md) list. For `ComputerComponent` and `AsyncComputerComponent`, `PipeMonadic` delegates to the provider that a private `BindProviders<M>` fold builds from the list. Writing `Bind<P>` for `<M as MonadicBind<P>>::Provider`, the bind step `M` produces (such as `BindErr<IdentMonadic, P>` for `ErrMonadic`), the fold of `[A, B, C]` is `ComposeHandlers<A, Bind<ComposeHandlers<B, Bind<C>>>>`. Each handler after the first runs only on the previous step's continue case. A one-element list is its only provider, and an empty list builds nothing.

For `TryComputerComponent` and `HandlerComponent`, `PipeMonadic` bridges through the err monad:

1. Each provider in the list is wrapped in `TryPromote<Provider>`, turning a fallible handler into a `Computer` whose output is `Result<Output, Context::Error>`.
2. `M` is applied as a transformer over `ErrMonadic`, so the err monad handles the outer `Result` that carries the context's error and `M` handles the value inside it. With `M = IdentMonadic` this is plain `ErrMonadic`; with `M = OkMonadic` it is `OkMonadicTrans<ErrMonadic>`.
3. The wrapped list is composed under that monad, and the result is wrapped in `TryPromote` again to restore the fallible interface.

So a fallible pipeline stops at the first context error, in addition to whatever `M` stops on.

## Monad markers

The markers decide which case of a step's output continues:

| Marker | Continues on | Stops on |
| --- | --- | --- |
| `IdentMonadic` | every value | never |
| `ErrMonadic` | `Ok(value)` | `Err`, the familiar early return on error |
| `OkMonadic` | `Err(value)` | `Ok`, stopping at the first success |

```rust
pub struct IdentMonadic;
pub struct OkMonadic;
pub struct ErrMonadic;
```

`PipeMonadic<IdentMonadic, …>` is the same as `PipeHandlers`.

The two `Result` markers have transformer forms that stack a layer over another monad:

```rust
pub struct OkMonadicTrans<M>(pub PhantomData<M>);
pub struct ErrMonadicTrans<M>(pub PhantomData<M>);
```

In `OkMonadicTrans<M>`, the monad `M` handles the outer structure of each output, and the ok layer applies to the `Result` that `M` exposes as its value. So `OkMonadicTrans<ErrMonadic>` over outputs of type `Result<Result<T, E1>, E2>` stops on an outer `Err`, stops on an inner `Ok`, and continues with the `E1` of an `Ok(Err(e1))`. `ErrMonadicTrans<M>` mirrors it. Applied as a transformer to a monad `M`, the bare `OkMonadic` gives `OkMonadicTrans<M>` and `ErrMonadic` gives `ErrMonadicTrans<M>`. Used on its own, each binds as its transformer over `IdentMonadic`.

## Bind providers

`BindOk` and `BindErr` implement one bind step. `PipeMonadic` composes them, and they can also be placed in a `PipeHandlers` list by hand:

```rust
pub struct BindOk<M, Cont>(pub PhantomData<(M, Cont)>);
pub struct BindErr<M, Cont>(pub PhantomData<(M, Cont)>);
```

`M` is the monad layer beneath this bind, `IdentMonadic` for a single layer, and `Cont` is the provider to run on the continue case. `BindErr<M, Cont>` implements `Computer` and `AsyncComputer` for an input of `Result<T1, E>`: on `Ok(value)` it runs `Cont` on `value` and passes the output through `M`, and on `Err(err)` it skips `Cont` and lifts the error into the output through `M`. `BindOk<M, Cont>` is the mirror: it runs `Cont` on the `Err` payload and stops on `Ok`.

## The `TryPromoteProviders` mapper

`TryPromoteProviders` is the type-level mapper `PipeMonadic` uses to wrap every provider of a list in `TryPromote`:

```rust
pub struct TryPromoteProviders;

impl MapType for TryPromoteProviders {
    type Map<Provider> = TryPromote<Provider>;
}
```

It implements [`MapType`](../traits/map_type.md), so `MapFields` applies it to each element of the handler list. [`TryPromote`](handler_combinators.md) converts between a fallible handler and a `Computer` returning `Result`, in both directions.

## Examples

These examples come from the `monadic_handlers` tests. `Increment` is built from a function returning `Result`:

```rust
use cgp::prelude::*;
use cgp::extra::handler::PipeHandlers;
use cgp::extra::monad::monadic::err::{BindErr, ErrMonadic};
use cgp::extra::monad::monadic::ident::IdentMonadic;
use cgp::extra::monad::providers::PipeMonadic;

#[cgp_computer]
pub fn increment(value: u8) -> Result<u8, &'static str> {
    value.checked_add(1).ok_or("overflow")
}
```

Composing three under `ErrMonadic` continues on each `Ok` and stops at the first `Err`, so starting from `253` it returns `Err("overflow")`:

```rust
let context = ();
let code = PhantomData::<()>;

PipeMonadic::<ErrMonadic, Product![Increment, Increment, Increment]>::compute(&context, code, 253)
// 253 -> Ok(254) -> Ok(255) -> Err("overflow")
```

The same step can be built by hand, which is what `PipeMonadic` does for a two-element list:

```rust
PipeHandlers::<Product![Increment, BindErr<IdentMonadic, Increment>]>::compute(&context, code, 1)
// Ok(3)
```

For handlers returning `Result<Result<(), u8>, &'static str>`, `OkMonadicTrans<ErrMonadic>` stops on an outer `Err` or an inner `Ok`. The same handlers composed under plain `OkMonadic` can be driven through `try_compute` and `handle`, because the fallible bridge stacks `OkMonadic` over `ErrMonadic` itself, taking the context's error from the outer `Result`.

## Related constructs

These constructs are the ones the monad providers work with:

- [Handler combinators](handler_combinators.md) — `PipeHandlers`, `ComposeHandlers`, and `TryPromote`, which these providers build on.
- [Monad traits](../traits/monad.md) — `MonadicTrans`, `MonadicBind`, `ContainsValue`, and `LiftValue`, which define the monads.
- [Monadic handlers](../../concepts/monadic-handlers.md) — why a monadic pipeline short-circuits.
- [`MapType`](../traits/map_type.md) — the mapping behind `TryPromoteProviders`.
- [Dispatch combinators](dispatch_combinators.md) — selecting one handler by a key instead of running several in sequence.

## Source

- The pipeline provider, `TryPromoteProviders`, and the internal `BindProviders` fold are in [crates/extra/cgp-monad/src/providers/pipe_monadic.rs](https://github.com/contextgeneric/cgp/blob/main/crates/extra/cgp-monad/src/providers/pipe_monadic.rs).
- The monad markers and bind providers are in [crates/extra/cgp-monad/src/monadic/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-monad/src/monadic/): `ident.rs` for `IdentMonadic`, `ok.rs` for `OkMonadic` / `OkMonadicTrans` / `BindOk`, and `err.rs` for `ErrMonadic` / `ErrMonadicTrans` / `BindErr`.
