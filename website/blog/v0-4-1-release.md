# CGP v0.4.1 Release: new cgp-handler crate, improved preset macros, and more

A short release note introducing the `cgp-handler` crate, whose `Handler`, `Computer`, and `Producer`
components the whole computation family grew from, with preset and `UseDelegate` improvements made for
Hypershell.

- **URL**: <https://contextgeneric.dev/blog/v0-4-1-release>
- **Source**: [blog/2025-06-14-v0.4.1-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-06-14-v0.4.1-release.md)
- **Published**: 14 June 2025, tagged `release`
- **Release**: [v0.4.1](../../releases/v0-4-1.md)
- **Status**: Historical

## What it covers

- **The `cgp-handler` crate:** three components of one shape, `Handler` for asynchronous fallible
  operations, `Computer` for pure synchronous transforms, and `Producer` for input-free production. Each
  carries a phantom `Code` parameter, which the post explains is for type-level DSLs and for
  dispatching in API handlers, the mechanism [Hypershell](hypershell-release.md) is built on.
- **`#[wrap_provider]` in presets:** a preset's `Provider` type wrapped in `UseDelegate`, so a mapping
  table becomes a delegation target.
- **`derive_delegate` in `#[cgp_component]`:** the `UseDelegate` dispatcher impl generated for a
  component generic over a parameter, shown on `CanRaiseError<SourceError>`.
- **Minor items:** inline Rustdoc for common constructs, static `Char` formatting without a `self`
  value, and two macro-hygiene fixes.

## How it relates to the knowledge base

- **Handlers:** the root of the [handler family](../../cgp/concepts/handlers.md), per component
  [`Handler` / `CanHandle`](../../cgp/reference/components/handler.md),
  [`Computer` / `CanCompute`](../../cgp/reference/components/computer.md), and
  [`Producer` / `CanProduce`](../../cgp/reference/components/producer.md). The family's framing by
  whether a computation is async, fallible, and input-taking survives in the concept.
- **The `Code` parameter:** [type-level DSLs](../../cgp/concepts/type-level-dsls.md), worked in the
  [shell-scripting DSL](../../examples/shell-scripting-dsl.md) example.
- **Dispatch:** [`#[derive_delegate]`](../../cgp/reference/attributes/derive_delegate.md) and
  [`UseDelegate`](../../cgp/reference/providers/use_delegate.md).
- **Static formatting:** [`StaticFormat` / `StaticString`](../../cgp/reference/traits/static_format.md).

## Where it diverges from CGP v0.8.0

- **`CanHandle`'s definition changed.** The post shows
  `CanHandle<Code: Send, Input: Send>: HasAsyncErrorType`. `HasAsyncErrorType` and the `Async` trait
  were removed in v0.5.0; the component imports its error type with
  [`#[use_type]`](../../cgp/reference/attributes/use_type.md), and the `Send` guarantee is recovered
  where it is needed, per [send-bounds](../../cgp/concepts/send-bounds.md).
- **The handler family grew well past three.** `TryComputer`, `ComputerRef`, `AsyncComputer`, and the
  runner components arrived later; see [handlers](../../cgp/concepts/handlers.md).
- **Presets and `#[wrap_provider]` no longer exist**, replaced by
  [namespaces](../../cgp/concepts/namespaces.md).
- **`derive_delegate` is the legacy dispatch path.** It still works, and CGP's own error and handler
  components are defined with it, but new code dispatches on a generic parameter with the `open`
  statement of [`delegate_components!`](../../cgp/reference/macros/delegate_components.md), per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **`Char` is now [`Chars`](../../cgp/reference/types/chars.md)**, renamed in v0.5.0 because it is a
  list rather than a single character.
- **Every provider snippet is in the inside-out `#[cgp_provider]` form** that
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) replaced in v0.6.0.

## Maintaining it

Leave it alone; draw any explanation of the handler family from
[handlers](../../cgp/concepts/handlers.md).
