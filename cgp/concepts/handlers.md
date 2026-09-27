# Handlers

The handler family is a group of CGP components that share one shape, turning an `Input` into an
`Output` under a phantom `Code` tag, and vary along three axes: synchronous or async, infallible or
fallible, and owned or borrowed input.

## The idea

A handler is a provider that maps `(context, Code, Input)` to an `Output`. The consumer method takes
a `PhantomData<Code>` to say which computation is wanted and the `Input` to compute over, and
returns an associated `Output` type. The `Code` tag carries no data. It exists so one context can
host many handlers, one per tag, and so wiring can dispatch on it.

`Output` is an associated type chosen by the provider, not a parameter the caller fixes, so the
provider decides what it returns for a given `Code` and `Input`, and downstream code reads that
choice back. The fallible and async members refine this signature, wrapping `Output` in a `Result`
or returning it from a future, without changing the correspondence.

The family exists because real computations differ along independent dimensions. Adding two numbers
needs nothing from the context; reading a file may fail and needs the context's error type; talking
to the network must be async. Instead of forcing every computation into the most general signature,
CGP gives each combination its own component, and combinators promote a provider written for a
simple member into the more capable ones. An author writes the weakest member that fits.

## The three axes of variation

A component's name encodes its position on each axis:

| | infallible | fallible (`Result<Output, Error>`) |
| --- | --- | --- |
| **synchronous** | [`Computer`](../reference/components/computer.md) | [`TryComputer`](../reference/components/try_computer.md) |
| **async** | `AsyncComputer` (in [`Computer`](../reference/components/computer.md)) | [`Handler`](../reference/components/handler.md) |

- **Synchronous or async.** An async member's method is declared `async` and returns a future.
  `AsyncComputer` carries the `Async` prefix; `Handler` is async by definition and needs none.
- **Infallible or fallible.** A fallible member returns `Result<Output, Error>` in the context's
  abstract error type, and so has [`HasErrorType`](../reference/components/has_error_type.md) as a
  supertrait. `TryComputer` marks the fallible synchronous corner with its `Try` prefix.
- **Owned or borrowed input.** Each of the four has a `…Ref` sibling, `ComputerRef`,
  `AsyncComputerRef`, `TryComputerRef`, and `HandlerRef`, whose method takes `&Input` instead of
  `Input`.

A fifth component, [`Producer`](../reference/components/producer.md), stands apart: it takes no
input at all and produces a value from the context and a `Code` tag alone.

## Wiring like any component

Each handler component is an ordinary `#[cgp_component]`. A context calls a consumer trait, such as
`CanCompute`, `CanTryCompute`, `CanHandle`, or `CanProduce`, and a provider implements the matching
provider trait, such as `Computer`, `TryComputer`, `Handler`, or `Producer`. The context picks the
provider in its [`delegate_components!`](../reference/macros/delegate_components.md) table under the
component key, such as `ComputerComponent`. Every component key is in the prelude, and so are the
provider traits apart from `ComputerRef`, `TryComputerRef`, and `HandlerRef`; those three and all
the consumer traits are imported from `cgp::extra::handler`.

Because `Code` and `Input` are type parameters, a context can dispatch a handler on either or both.
The recommended form is the `open` statement, whose redirect appends both parameters to the lookup
path:

- `@ComputerComponent.Eval: EvalProvider` routes one `Code` whatever the input.
- `@ComputerComponent.<Code> Code.Plus<MathExpr>: EvalAdd` routes one input type whatever the code.
- A key with two concrete segments routes one pair.

The components also keep the legacy dispatchers: each input-taking component declares
`#[derive_delegate(UseDelegate<Code>)]` and `#[derive_delegate(UseInputDelegate<Input>)]`, and
`Producer`, which has no input, declares the first alone. So wiring through an inner
[`UseDelegate`](../reference/providers/use_delegate.md) or `UseInputDelegate` table still works. The
[dispatching-per-type](../guides/dispatching-per-type.md) guide converts one form to the other.

## Promoting providers between members

Promotion lifts a provider along the natural inclusions between the axes:

- An infallible computation is a fallible one that always returns `Ok`.
- A synchronous computation is an async one whose future is ready at once.
- An input-free producer is a computer that ignores its input.
- A by-reference computation serves an owned-input slot by dereferencing the input. The reverse
  holds only for a computation that accepts a borrow as its input, since `PromoteRef` passes
  `&Input` through and needs the provider to work for `&'a Input` at every lifetime.

Each inclusion is a one-step combinator provider:

- `Promote` makes an infallible member fallible (`Computer` to `TryComputer`, `AsyncComputer` to
  `Handler`) and a `Producer` into a `Computer`.
- `PromoteAsync` makes a synchronous member async (`Computer` to `AsyncComputer`, `TryComputer` to
  `Handler`).
- `PromoteRef` moves between owned and borrowed input.
- `TryPromote` converts in both directions between a fallible member and the infallible member whose
  `Output` is a `Result` over the context's error type.

A lift of two steps chains them, as `PromoteAsync<Promote<P>>` makes a `Handler` from a `Computer`.

The promotion bundles, such as `PromoteComputer<P>`, `PromoteTryComputer<P>`, and
`PromoteProducer<P>`, are delegation tables that route every other handler component to the right
one-step combinator, so one provider answers the whole family. A bundle expects `P` to be wired to
that same bundle, because some entries reach the base through a sibling component.
[`#[cgp_computer]`](../reference/macros/cgp_computer.md) and
[`#[cgp_producer]`](../reference/macros/cgp_producer.md) do exactly this: they turn a plain function
into a provider for the narrowest fitting member and wire that provider to the bundle with `Self`.
The full catalogue, with `ReturnInput`, `ComposeHandlers`, and `PipeHandlers`, is in
[handler combinators](../reference/providers/handler_combinators.md).

## Related constructs

These constructs are the ones the handler family works with:

- [`Computer`](../reference/components/computer.md),
  [`TryComputer`](../reference/components/try_computer.md),
  [`Handler`](../reference/components/handler.md), and
  [`Producer`](../reference/components/producer.md): the components, one document per corner.
- [`HasErrorType`](../reference/components/has_error_type.md): the supertrait of the fallible
  members.
- [Handler combinators](../reference/providers/handler_combinators.md): promotion and composition.
- [`#[cgp_computer]`](../reference/macros/cgp_computer.md) and
  [`#[cgp_producer]`](../reference/macros/cgp_producer.md): generate handler providers from
  functions.
- [Dispatching per type](../guides/dispatching-per-type.md): routing a handler on its `Code` or
  `Input`.
- [Monadic handlers](monadic-handlers.md): chaining handlers with short-circuiting.

## Source

The handler components are defined in
[crates/extra/cgp-handler/src/components/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/components/),
with one module per corner: `computer.rs`, `async_computer.rs`, `try_compute.rs`, `handler.rs`, and
`produce.rs`. The promotion combinators and the `UseInputDelegate` dispatch type live in
[crates/extra/cgp-handler/src/providers/](https://github.com/contextgeneric/cgp/tree/main/crates/extra/cgp-handler/src/providers/)
and `types.rs`. The family is re-exported through `cgp::extra::handler`. Behavioral tests covering
the full promotion surface are in
[crates/tests/cgp-tests/tests/handlers/](https://github.com/contextgeneric/cgp/tree/main/crates/tests/cgp-tests/tests/handlers/).
