# CGP v0.5.0 Release: Auto dispatchers, extensible datatype improvements, monadic computation, RTN emulation, modular serde, and more

A large release with large breaking changes: it adds `#[derive(CgpData)]`, `#[cgp_auto_dispatch]`, the
optional builder, and monadic computation, and removes the `Async` trait for the `Send`-recovery proxy
pattern CGP still uses.

- **URL**: <https://contextgeneric.dev/blog/v0-5-0-release>
- **Source**: [blog/2025-10-12-v0.5.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-10-12-v0.5.0-release.md)
- **Published**: 12 October 2025, tagged `release`
- **Release**: [v0.5.0](../../releases/v0-5-0.md)
- **Status**: Historical

## What it covers

The new features cluster around extensible data:

- **`#[derive(CgpData)]`:** one derive in place of `HasField`, `HasFields`, `BuildField`,
  `FromVariant`, and `ExtractField`.
- **`#[cgp_auto_dispatch]`:** lifts a per-type trait onto an enum whose variants implement it, so
  `HasArea` for `Circle` and `Rectangle` holds for `Shape`, across crates, with neither the trait nor
  the enum knowing about the other.
- **Builders:** `UpdateField` generalizes field mutation on a partial record, with `BuildField` a
  blanket impl over it; `finalize_with_default` fills unset fields from `Default`; and the `IsOptional`
  marker gives a builder whose type does not change as fields are set, the form `cgp-serde`
  deserializes with.
- **Dispatchers and handlers:** the visitor dispatchers grow to six, with mutable and tuple-input
  variants; `AsyncComputer` arrives, making `Handler` the async counterpart of `TryComputer`.
- **`cgp-monad`:** a retroactive treatment of monads that uses `Result` and `Option` without
  implementing anything on them.
- **`Symbol!`:** produces a `&'static str` at compile time through `StaticString`.

**The removal of `Async` leads the breaking changes, and its explanation is the post's most important
part.** `Async` aliased `Send + Sync`, spread through CGP so generic async methods' futures were `Send`
enough for `tokio::spawn`. Return Type Notation would solve this but is not close to stabilizing. CGP's
alternative is a proxy trait (`CanSendRun` beside `CanRun`) whose method promises a `Send` future,
implemented by hand on the concrete context so the trait solver sees the concrete types. Providers stay
free of `Send` bounds, and the guarantee is recovered where it is needed.

The other breaking changes: `symbol!` becomes `Symbol!` with a length prefix so `StaticString` can
rebuild the string, `ι` becomes `ζ` to avoid a `confusable_idents` warning, and `Char` becomes
`Chars`; `cgp-field`'s exports move into submodules; partial data types gain the `__Partial` prefix;
`CanRun` gains a `Code` parameter; and `HasInner` is removed in favor of `UseField`. The post closes
announcing the RustLab talk and previewing `cgp-serde` with the arena-allocator deserialization example.

## How it relates to the knowledge base

- **`Send` recovery:** [recovering `Send` bounds](../../cgp/concepts/send-bounds.md), with
  [`CanRun` / `CanSendRun`](../../cgp/reference/components/runner.md). The post's second example links
  an older commit of `cgp-examples`' `transfer/src/contexts/app.rs`; its two `CanHandleApiSend` impls
  are unchanged, documented with the
  [`transfer` HTTP layer](../../projects/cgp-examples/transfer/reference/http-layer.md#canhandleapisend).
- **Data:** [`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md);
  [`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md), worked in the
  [extensible shapes example](../../examples/extensible-shapes.md);
  [optional fields](../../cgp/reference/traits/optional_fields.md) over
  [`MapType`](../../cgp/reference/traits/map_type.md) and
  [`HasBuilder`](../../cgp/reference/traits/has_builder.md); the
  [dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md).
- **Monads:** [monadic handlers](../../cgp/concepts/monadic-handlers.md) over the
  [monad traits](../../cgp/reference/traits/monad.md) and
  [monad providers](../../cgp/reference/providers/monad_providers.md).
- **Type-level strings:** [`StaticFormat`](../../cgp/reference/traits/static_format.md) and
  [`Symbol!`](../../cgp/reference/macros/symbol.md) over [`Chars`](../../cgp/reference/types/chars.md);
  lifetimes in component parameters are [`Life`](../../cgp/reference/types/life.md).
- **The `cgp-serde` preview:** superseded by the [release post](cgp-serde-release.md), the
  [modular serialization example](../../examples/modular-serialization.md), and
  [projects/cgp-serde/](../../projects/cgp-serde/README.md).

## Where it diverges from CGP v0.8.0

- **`#[cgp_context]` and `{Context}Components` appear throughout and no longer exist**, removed in
  v0.7.0.
- **Every provider is inside-out**, written with `#[cgp_provider]`/`#[cgp_new_provider]` rather than
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md), which arrived two weeks later in v0.6.0.
- **`derive_delegate: UseDelegate<Code>` and nested `UseDelegate` tables are the legacy dispatch
  form**, superseded by the `open` statement per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`check_components!` still uses the `CanDeserializeApp for App` form**, replaced in v0.7.0 by an
  optional `#[check_trait(...)]` attribute.
- **The migration advice to copy `Async` and `HasAsyncErrorType` locally still works**, but it is
  transitional advice for a version-old codebase, not a recommendation for new code.
- **The `#[cgp_component { provider: ..., derive_delegate: ... }]` brace form no longer parses.** The
  brace form takes only `name`, `provider`, and `context`, so `derive_delegate` is a separate
  `#[derive_delegate(...)]` attribute. The positional `#[cgp_component(Handler)]` form is idiomatic.
- **Two notes on the RTN discussion.** The claim that RTN "does not appear to be close to
  stabilization" was accurate then and must be re-checked before it is repeated publicly. The
  proxy-trait workaround the post calls temporary is still in use, so present it as CGP's current
  answer, not a stopgap.

## Maintaining it

Leave it alone. Its `Async`-removal section is the project's most substantive published prose on the
`Send`-bound problem; [send-bounds](../../cgp/concepts/send-bounds.md) holds that reasoning in current
form. Check public writing on CGP and async against
[evidence.md](../../communication-strategy/evidence.md), which warns that async and function coloring
draw high attention while the honest attachment is narrow.
