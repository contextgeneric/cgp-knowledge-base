# CGP v0.4.1 Release: new cgp-handler crate, improved preset macros, and more

A short release note introducing the `cgp-handler` crate — the `Handler`, `Computer`, and `Producer`
components that the whole computation family grew from — together with preset and `UseDelegate`
improvements made to support Hypershell.

- **URL** — <https://contextgeneric.dev/blog/v0-4-1-release>
- **Source** — [blog/2025-06-14-v0.4.1-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-06-14-v0.4.1-release.md)
- **Published** — 14 June 2025, tagged `release`
- **Release** — [v0.4.1](../../releases/v0-4-1.md)
- **Status** — Historical

## What it covers

The post is brief and covers three things. The first and most consequential is the **`cgp-handler`
crate**, introducing three components with a shared shape: `Handler` for asynchronous fallible
operations, `Computer` for pure synchronous transforms, and `Producer` for input-free production of a
value. All three carry a phantom `Code` parameter, which the post explains is for building type-level
DSLs and for dispatching in API handlers — the mechanism that
[Hypershell](hypershell-release.md) is built on, and the reason the crate was written.

The second is preset support for `#[wrap_provider]`, letting a preset's `Provider` type be wrapped in
`UseDelegate` so that a mapping table becomes a valid delegation target. The third is `derive_delegate`
in `#[cgp_component]`, which auto-generates the `UseDelegate` dispatcher impl for a component generic
over a parameter, shown on `CanRaiseError<SourceError>`. The post closes with minor items: inline
Rustdoc for common constructs, static `Char` formatting without a `self` value, and two macro-hygiene
fixes.

## How it relates to the knowledge base

The three components introduced here are the root of the whole
[handler family](../../cgp/concepts/handlers.md), documented per component as
[`Handler` / `CanHandle`](../../cgp/reference/components/handler.md),
[`Computer` / `CanCompute`](../../cgp/reference/components/computer.md), and
[`Producer` / `CanProduce`](../../cgp/reference/components/producer.md). The `Code` parameter's role
in encoding a language as types is [type-level DSLs](../../cgp/concepts/type-level-dsls.md), worked
end to end in the [shell-scripting DSL](../../examples/shell-scripting-dsl.md) example.
`derive_delegate` and the provider it generates are
[`#[derive_delegate]`](../../cgp/reference/attributes/derive_delegate.md) and
[`UseDelegate`](../../cgp/reference/providers/use_delegate.md). Static formatting of a type-level
string is [`StaticFormat` / `StaticString`](../../cgp/reference/traits/static_format.md).

## Where it diverges from CGP v0.8.0

- **`CanHandle`'s definition changed.** The post shows
  `CanHandle<Code: Send, Input: Send>: HasAsyncErrorType`. `HasAsyncErrorType` and the `Async` trait
  were removed in v0.5.0; the current component imports its error type with
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md) and the `Send` guarantee is recovered
  where it is actually needed, per [send-bounds](../../cgp/concepts/send-bounds.md).
- **The handler family grew well past three.** `TryComputer`, `ComputerRef`, `AsyncComputer`, and the
  runner components all arrived later; see [handlers](../../cgp/concepts/handlers.md) for the current
  set and the axes that organize it.
- **Presets and `#[wrap_provider]` no longer exist**, replaced by
  [namespaces](../../cgp/concepts/namespaces.md).
- **`derive_delegate` is now the legacy dispatch path.** It still works and CGP's own error and
  handler components are still defined with it, but new code should dispatch on a generic parameter
  with the `open` statement of
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`Char` is now [`Chars`](../../cgp/reference/types/chars.md)**, renamed in v0.5.0 to reflect that
  it is a list rather than a single character.
- **Every provider snippet is in the inside-out `#[cgp_provider]` form** that
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) replaced in v0.6.0.

## Maintaining it

Leave it alone. Its one enduring contribution is the framing of `Handler`/`Computer`/`Producer` as a
family distinguished by whether a computation is async, fallible, and input-taking — an idea that
survived intact and is now stated properly in [handlers](../../cgp/concepts/handlers.md), which is
where a piece needing that explanation should draw from.
