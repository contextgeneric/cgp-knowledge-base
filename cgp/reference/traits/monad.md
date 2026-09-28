# Monad traits

The monad traits `MonadicTrans`, `MonadicBind`, `LiftValue`, and `ContainsValue` are the type-level
interface that defines what a monad is for
[monadic handler composition](../../concepts/monadic-handlers.md): which branch of an output value
continues a pipeline, which branch short-circuits, and how values move between those branches.

## Purpose

These four traits factor a monad into the distinct operations the monadic pipeline machinery needs
from it. A monad in CGP is a zero-sized marker type (`IdentMonadic`, `OkMonadic`, `ErrMonadic`, and
their transformer forms), and these traits are what give that marker meaning. They are plain traits
rather than CGP components: they have no provider trait or component key and are not wired. Instead,
the [`PipeMonadic`](../providers/monad_providers.md) provider and the per-step `BindOk` / `BindErr`
providers consume them as ordinary trait bounds while building a pipeline at compile time.

The split exists because building a monadic pipeline requires three separable decisions. Composing a
list of handlers under a monad needs to know how to turn a continuation provider into a bind step,
that is `MonadicBind`. Each bind step needs to know, for a given output type, what the underlying
value beneath the monad's wrapper is, and how to put a value back into that output type, that is
`ContainsValue` and `LiftValue`. Stacking one monad on top of another needs to apply a monad as a
transformer over a base monad, that is `MonadicTrans`. Keeping these as separate traits lets the
same marker serve all three roles and lets monads stack by composing their implementations.

They are imported from `cgp::extra::monad::traits`.

## Definition

`MonadicBind` maps a continuation provider to the provider that runs one bind step of the monad:

```rust
pub trait MonadicBind<Provider> {
    type Provider;
}
```

The `Provider` parameter is the continuation, the handler that should run on the monad's continue
branch, and the `Provider` associated type is the bind provider that wraps it. For `ErrMonadic` it is
`BindErr<IdentMonadic, Provider>` and for `OkMonadic` it is `BindOk<IdentMonadic, Provider>`, each
bind provider named for the branch it stops on; for `IdentMonadic` it is the continuation unchanged.
`PipeMonadic` folds its list with a private `BindProviders` helper that recurses into the rest of the
list first and sets each cell to `ComposeHandlers<ProviderA, <M as MonadicBind<Rest>>::Provider>`, so
the first handler runs plainly and hands its output to a bind step over everything after it.

`MonadicTrans` applies a monad as a transformer onto a base monad:

```rust
pub trait MonadicTrans<M> {
    type M;
}
```

`Self` is the monad applied as a transformer, the `M` parameter is the base monad it is applied to,
and the `M` associated type is the stacked result. `OkMonadic: MonadicTrans<ErrMonadic>` gives
`OkMonadicTrans<ErrMonadic>`, in which the err monad handles the outer `Result` of each output and
the ok layer the `Result` inside it. `PipeMonadic`'s fallible bridge uses this to stack the user's
monad over `ErrMonadic`.

`ContainsValue` reads, for a given monadic output type, the value type that sits beneath this
monad's wrapper:

```rust
pub trait ContainsValue<Output> {
    type Value;
}
```

The `Output` parameter is the full output type a step produces; the `Value` associated type is the
type carried in the branch the monad threads through, which a deeper monad layer unwraps further.
In the bind providers it is a bound on the *continuation's* output rather than the means of
unwrapping the input, which the step matches itself. `BindErr<M, Cont>` over an input
`Result<T1, E>` requires `M: ContainsValue<Cont::Output, Value = Result<T2, E>>` and
`M: LiftValue<Result<T2, E>, Cont::Output>`, where `M` is the monad the step sits inside
(`IdentMonadic` for a single layer); its body forwards `Ok(value)` to the continuation and lifts the
result with `M::lift_output`, and lifts `Err(err)` with `M::lift_value`. The bound is what lets the
short-circuit branch produce the same output type as the continue branch.

`LiftValue` moves values into a step's output type, in two directions:

```rust
pub trait LiftValue<Value, Output> {
    type Output;

    fn lift_value(value: Value) -> Self::Output;

    fn lift_output(output: Output) -> Self::Output;
}
```

The associated `Output` is the final output type of the lift. `lift_value` takes a bare value from
the continue or short-circuit branch and wraps it into that output type, and `lift_output` takes a
value already in the inner `Output` shape and re-wraps it. The two methods correspond to the two
branches a bind step takes: one lifts the short-circuit value back out as the result, the other
forwards a continuation's already-computed output.

## Implementations

`IdentMonadic` implements all four traits as identities, which is what makes it thread every value
forward without ever short-circuiting. `MonadicTrans<M>` returns `M` unchanged,
`MonadicBind<Provider>` returns `Provider` unchanged, `ContainsValue<T>::Value` is `T`, and
`LiftValue<T, T>` is the identity on `T` for both methods.

`OkMonadic` and `ErrMonadic` implement the traits to branch on a `Result`, in mirror image of each
other. For `ErrMonadic`, `ContainsValue<Result<T, E>>::Value` is `T`, the `Ok` payload is the value
threaded forward, and `LiftValue<T, Result<T, E>>::lift_value` is `Ok`, so the continue branch is
`Ok` and an `Err` short-circuits. For `OkMonadic` the roles are swapped:
`ContainsValue<Result<T, E>>::Value` is `E`, and `lift_value` is `Err`, so the continue branch is
`Err` and an `Ok` short-circuits. The `MonadicBind` impl of each base monad produces the
corresponding `BindOk` or `BindErr` step over `IdentMonadic`, and the `MonadicTrans` impl wraps the
marker in its transformer form (`OkMonadicTrans`, `ErrMonadicTrans`).

The transformer forms `OkMonadicTrans<M>` and `ErrMonadicTrans<M>` implement the same traits by
delegating one layer down to the base monad `M`. Their `ContainsValue` and `LiftValue` impls require
`M: ContainsValue<V, Value = Result<…>>`, peeling their own `Result` layer and handing the rest to
`M`; their `MonadicTrans` impl composes transformers so a stack like `OkMonadicTrans<ErrMonadic>`
resolves layer by layer. This delegation is what allows monads to stack to arbitrary depth over
nested result types.

## Using them

These traits are named only when defining a monad of one's own; using the shipped ones means wiring
`PipeMonadic` with a marker and a handler list. A new monad (short-circuiting over an `Option`, or
over a custom two-branch enum) implements all four, with the transformer form as well if it should
stack or be used with a fallible pipeline, since `PipeMonadic` stacks the chosen monad over
`ErrMonadic` for `TryComputer` and `Handler`. Implementing `MonadicBind` alone yields a marker that
folds a pipeline and then fails to resolve when a step runs, and `lift_value` and `lift_output` must
stay distinct: implementing one as the other collapses the two branches and silently changes what a
short-circuit produces. The mirror-image `OkMonadic`/`ErrMonadic` pair is the model to copy.

The naming reads backwards until learned: `OkMonadic` stops on `Ok` and continues on `Err`, so its
`ContainsValue` value is the error and it lifts with `Err`, which makes it the fallback-chain monad,
while `ErrMonadic` behaves like `?`. A stack is written in layer order, and
`OkMonadicTrans<ErrMonadic>` and `ErrMonadicTrans<OkMonadic>` unwrap their `Result` layers in
opposite orders. `MonadicTrans`'s parameter and associated type are both named `M`, which makes a
projection such as `<Self as MonadicTrans<M>>::M` easy to misread. When every step should run
unconditionally, the handler combinators `ComposeHandlers` and `PipeHandlers` need no monad, and a
chain inside one provider body is clearer with Rust's own `?`.

## Related constructs

These traits are consumed by the monad providers in
[monad providers](../providers/monad_providers.md): `PipeMonadic` uses `MonadicTrans` and
`MonadicBind` to fold a handler list into a single pipeline provider, while `BindOk` and `BindErr`
use `ContainsValue` and `LiftValue` in their `Computer` and `AsyncComputer` implementations to split
and re-lift each step's output. The high-level picture of how the pieces fit, why a pipeline
short-circuits and how the monads compose, is in
[monadic handlers](../../concepts/monadic-handlers.md). The pipelines built from these traits
implement the [`Computer`](../components/computer.md) family, so they slot into the same wiring as
the [handler combinators](../providers/handler_combinators.md) `ComposeHandlers` and `PipeHandlers`,
which compose handlers without the short-circuiting branch.

## Source

- The traits are defined in
  [crates/extra/cgp-monad/src/traits/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-monad/src/traits/):
  `monadic_trans.rs`, `bind.rs`, `lift.rs`, and `value.rs`.
- Their implementations for each monad marker are in
  [crates/extra/cgp-monad/src/monadic/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-monad/src/monadic/)
  (`ident.rs`, `ok.rs`, `err.rs`).

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds **4 pages**
rather than one:
[`monadic_bind`](https://contextgeneric.dev/docs/reference/traits/monad/monadic_bind),
[`contains_value`](https://contextgeneric.dev/docs/reference/traits/monad/contains_value),
[`lift_value`](https://contextgeneric.dev/docs/reference/traits/monad/lift_value),
[`monadic_trans`](https://contextgeneric.dev/docs/reference/traits/monad/monadic_trans). A change
here is propagated to each of them, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule); the mapping and the granularity
rule behind it are recorded in [website/site-structure.md](../../../website/site-structure.md).
