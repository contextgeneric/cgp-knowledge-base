# CGP v0.5.0 Release: Auto dispatchers, extensible datatype improvements, monadic computation, RTN emulation, modular serde, and more

A large release with equally large breaking changes. It adds `#[derive(CgpData)]`,
`#[cgp_auto_dispatch]`, the optional builder, and monadic computation; and it removes the `Async`
trait, replacing it with the `Send`-recovery proxy pattern that CGP still uses today.

- **URL** — <https://contextgeneric.dev/blog/v0-5-0-release>
- **Source** — [blog/2025-10-12-v0.5.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-10-12-v0.5.0-release.md)
- **Published** — 12 October 2025, tagged `release`
- **Release** — [v0.5.0](../../releases/v0-5-0.md)
- **Status** — Historical

## What it covers

The new features cluster around extensible data. `#[derive(CgpData)]` becomes the umbrella derive,
replacing the previous need to list `HasField`, `HasFields`, `BuildField`, `FromVariant`, and
`ExtractField` individually. `#[cgp_auto_dispatch]` lifts a plain per-type trait onto an enum whose
variants all implement it, so `HasArea` implemented for `Circle` and `Rectangle` is automatically
implemented for `Shape` — and does so across crate boundaries, with neither the trait nor the enum
knowing about the other. `UpdateField` generalizes field mutation on a partial record, with
`BuildField` becoming a blanket impl over it. Two builder extensions follow: `finalize_with_default`
fills uninitialized fields from `Default`, and the new `IsOptional` marker gives a builder whose type
does not change as fields are set, so a partial record can be filled dynamically — the form
`cgp-serde` uses for deserialization. The visitor dispatchers grow to six, adding mutable and
tuple-input variants. `AsyncComputer` arrives as the async counterpart of `Computer`, making `Handler`
the async counterpart of `TryComputer`. The `cgp-monad` crate lands, with a retroactive treatment of
monads that lets `Result` and `Option` be used as monads without implementing anything on them. And
`Symbol!` gains the ability to produce a real `&'static str` at compile time through `StaticString`.

The breaking changes are led by the **removal of `Async`**, and the post's explanation of it is the
most important thing in it. `Async` had been an alias for `Send + Sync`, sprinkled through CGP so that
futures returned by generic async methods would be `Send` enough for `tokio::spawn`. Return Type
Notation would have solved this properly but is not close to stabilizing. The alternative CGP found is
to define a *proxy trait* — `CanSendRun` alongside `CanRun` — whose method promises a `Send` future,
implement it by hand on the concrete context, and let the trait solver see through to the concrete
types. Providers stay free of `Send` bounds; the guarantee is recovered exactly where it is needed.

The remaining breaking changes: `symbol!` becomes `Symbol!` and desugars differently, gaining a length
prefix so `StaticString` can reconstruct the string, with `ι` replaced by `ζ` to avoid a
`confusable_idents` warning and `Char` renamed `Chars`; `cgp-field` exports are reorganized into
submodules; partial data types gain the `__Partial` prefix; `CanRun` gains a `Code` parameter; and
`HasInner` is removed in favor of `UseField`.

The post closes with two announcements: the RustLab talk, and a preview of `cgp-serde` including the
arena-allocator deserialization example.

## How it relates to the knowledge base

The `Send`-recovery pattern is the durable contribution and is documented as
[recovering `Send` bounds](../../cgp/concepts/send-bounds.md), with the components at
[`CanRun` / `CanSendRun`](../../cgp/reference/components/runner.md). The derive is
[`#[derive(CgpData)]`](../../cgp/reference/derives/derive_cgp_data.md); the auto-dispatch macro is
[`#[cgp_auto_dispatch]`](../../cgp/reference/macros/cgp_auto_dispatch.md), worked in the
[extensible shapes example](../../examples/extensible-shapes.md). The builder extensions are
[optional fields](../../cgp/reference/traits/optional_fields.md) over
[`MapType`](../../cgp/reference/traits/map_type.md) and
[`HasBuilder`](../../cgp/reference/traits/has_builder.md). The dispatchers are the
[dispatch combinators](../../cgp/reference/providers/dispatch_combinators.md); the monad layer is
[monadic handlers](../../cgp/concepts/monadic-handlers.md) over the
[monad traits](../../cgp/reference/traits/monad.md) and
[monad providers](../../cgp/reference/providers/monad_providers.md). `StaticString` is
[`StaticFormat`](../../cgp/reference/traits/static_format.md), and the symbol desugaring is
[`Symbol!`](../../cgp/reference/macros/symbol.md) over [`Chars`](../../cgp/reference/types/chars.md).
Lifetimes in component parameters are [`Life`](../../cgp/reference/types/life.md).

The `cgp-serde` preview is superseded by the [release post](cgp-serde-release.md) and the
[modular serialization example](../../examples/modular-serialization.md); the project itself is
documented at [projects/cgp-serde/](../../projects/cgp-serde/README.md).

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
  transitional advice for a version-old codebase and should not be read as a recommendation for new
  code.
- **The `#[cgp_component { provider: ..., derive_delegate: ... }]` brace form is still valid** but is
  now the long way round; the positional `#[cgp_component(Handler)]` form is idiomatic.
- **Two notes on the RTN discussion.** The post's claim that RTN "does not appear to be close to
  stabilization" was accurate at the time and should be re-checked before being repeated anywhere
  public. And the proxy-trait workaround the post calls temporary is still in use, so it should be
  presented as CGP's current answer rather than as a stopgap awaiting removal.

## Maintaining it

Leave it alone. The `Async`-removal section is the most substantive prose the project has published on
the `Send`-bound problem in async Rust, and the reasoning transfers cleanly even though its code does
not — [send-bounds](../../cgp/concepts/send-bounds.md) is where that reasoning now lives in current
form. Anything written publicly about CGP and async should be checked against the survey evidence in
[attention-and-engagement.md](../../communication-strategy/attention-and-engagement.md), which warns
that async and function coloring is a high-attention topic where the honest attachment is narrow.
