# Hypershell: A Type-Level DSL for Shell-Scripting in Rust

The longest post on the site, announcing [Hypershell](../../projects/hypershell/README.md) and using it
to teach both the type-level DSL technique and CGP's whole wiring model. It is still the fullest
account of building a DSL whose programs are Rust types, and its CGP introduction is one of the best
on the site, but its wiring code is four breaking releases out of date.

- **URL**: <https://contextgeneric.dev/blog/hypershell-release>
- **Source**: [blog/2025-06-14-hypershell-release/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-06-14-hypershell-release/index.md)
- **Published**: 14 June 2025, tagged `release` and `deepdive`
- **Status**: Historical
- **Notice**: a note at the top of the post, written on the website's `v0.8.0` branch, links the [Hypershell pages](https://contextgeneric.dev/docs/projects/hypershell/), per [projects/hypershell.md](../projects/hypershell.md); it is the sanctioned edit in [../AGENTS.md](../AGENTS.md#do-not-rewrite-history) and changes no claim

## What it covers

Five parts, estimated by the post at one to two hours of reading:

- **Overview:** a program is a Rust *type* written with the `hypershell!` macro, whose shell-like
  syntax (a pipe operator, bracketed variadic argument lists, bare string literals) desugars into
  `Pipe<Product![...]>` over `Symbol!` strings. It works through hello world, variable parameters via
  `FieldArg<"name">` read from a custom context, streaming one child process's `STDOUT` into the
  next's `STDIN`, a `reqwest`-backed HTTP handler replacing `curl`, and JSON around a request to the
  Rust Playground API.
- **CGP introduction:** a self-contained primer on the consumer/provider split, why a unique `Self`
  type escapes coherence, and how `delegate_components!` builds a type-level lookup table, compared at
  length, with diagrams, to **JavaScript prototypal inheritance** resolved at compile time.
- **Implementation:** a syntax type such as `SimpleExec<CommandPath, Args>` is a bare `PhantomData`
  struct with no impls, abstract syntax decoupled from its interpretation. A provider implements
  `Handler` for that shape, destructuring the `Code` parameter, and injects what it needs from the
  context: `CanExtractCommandArg`, `CanUpdateCommand`, `CanRaiseError<std::io::Error>`, and
  `CanWrapError<CommandNotFound>`. Because CGP names concrete types last, the dependency graph inverts,
  and `hypershell-tokio-components` builds without `reqwest` in its tree.
- **Extension:** `Checksum<Hasher>` and `BytesToHex` with their providers and a preset layering them
  onto the base language, showing an extension needs no upstream coordination or fork.
- **Discussion:** the steep learning curve, poor error messages, no dynamic loading, and slow
  compilation of executables named as costs; comparisons to
  [tagless final](https://okmij.org/ftp/tagless-final/) and Haskell's
  [Servant](https://www.servant.dev/posts/2018-07-12-servant-dsl-typelevel.html); and future DSLs for
  lambda calculus, HTML, parsers, and monadic computation.

## How it relates to the knowledge base

- **The source to quote:** the [shell-scripting DSL example](../../examples/shell-scripting-dsl.md),
  which re-derives the scenario in current syntax, over
  [type-level DSLs](../../cgp/concepts/type-level-dsls.md). Facts about the project come from
  [projects/hypershell/](../../projects/hypershell/README.md), verified against its source.
- **CGP constructs:** [consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md)
  and [coherence](../../cgp/concepts/coherence.md);
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md) and
  [`DelegateComponent`](../../cgp/reference/traits/delegate_component.md);
  [`Handler`](../../cgp/reference/components/handler.md) in the
  [handler family](../../cgp/concepts/handlers.md);
  [impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md);
  [modular error handling](../../cgp/concepts/modular-error-handling.md) with
  [`CanRaiseError` / `CanWrapError`](../../cgp/reference/components/can_raise_error.md);
  [dispatching](../../cgp/concepts/dispatching.md) with
  [`UseDelegate`](../../cgp/reference/providers/use_delegate.md);
  [`PipeHandlers`](../../cgp/reference/providers/handler_combinators.md); and
  [`Symbol!`](../../cgp/reference/macros/symbol.md) and
  [`Product!`](../../cgp/reference/macros/product.md).
- **Strategy assets:** the prototypal-inheritance comparison is a bridge for the OOP-background reader
  in [readers.md](../../communication-strategy/readers.md#the-comprehension-barriers), with the
  caveat the post states, that the lookup is compile-time and zero-cost, which
  [vocabulary.md](../../communication-strategy/vocabulary.md) requires beside any runtime-flavored
  analogy. The disadvantages section models the concede-the-costs discipline of
  [message.md](../../communication-strategy/message.md#the-objections-readers-bring), and its
  compile-time observations are among the project's few concrete statements on that topic.

## Where it diverges from CGP v0.8.0

The ideas are current; the wiring code is uniformly stale. It was written against CGP v0.4.1 and
predates four breaking releases, v0.5.0 through v0.8.0, each removing something it uses:

- **`#[cgp_context(MyAppComponents: HypershellPreset)]` no longer exists.** The macro and the
  `HasProvider`/`HasCgpProvider` trait it generated were removed. A context carries its own wiring
  table, and namespace inheritance replaces preset inheritance, so every context definition in the
  post (`MyApp`, `HypershellCli`, `HypershellHttp`) is dead syntax.
- **The whole preset system is gone.** `cgp_preset!`, `#[cgp::re_export_imports]`, `override`,
  `#[wrap_provider(UseDelegate)]`, and `Preset::Provider` were replaced by
  [namespaces](../../cgp/concepts/namespaces.md). The four-level preset delegation trace
  (`HypershellPreset` → `HypershellHandlerPreset` → `TokioHandlerPreset` → `HandleSimpleExec`)
  describes a mechanism that no longer exists.
- **`HasAsyncErrorType` and the `Async` trait were removed** in v0.5.0. `CanHandle` carries no `Send`
  bounds, and a caller that needs one recovers it; see [send-bounds](../../cgp/concepts/send-bounds.md).
- **Every provider is inside-out**, with `#[cgp_new_provider]` and an explicit `context: &Context`
  first parameter; the current form is [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) with
  `self`.
- **Dependencies are hand-written `where` bounds.** `Context: CanExtractCommandArg<CommandPath> + ...`
  would be [`#[uses(...)]`](../../cgp/reference/attributes/uses.md). Most field reads cannot become
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments, because `FieldArg` reads a
  field the program names; the one candidate is the HTTP client getter, and whether to convert it is
  open, per the project's [issues](../../projects/hypershell/issues.md#housekeeping).
- **`UseDelegate` tables are the legacy dispatch form**, superseded by the `open` statement per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md). The same holds for the input
  axis: the "Input-Based Dispatch" exercise points at `UseInputDelegate`, while Hypershell dispatches
  on the input with two-segment path keys, and its `Checksum` wiring starts with the
  `HandleToFuturesStream` dispatcher rather than the post's fixed adapter pipeline; see
  [streams and input dispatch](../../projects/hypershell/architecture/streams-and-input-dispatch.md).
- **The crate graph is drawn flatter than it is.** The post lists `hypershell-reqwest-components` as
  depending only on `cgp`, `hypershell-components`, and `reqwest`; it also depends on
  `hypershell-tokio-components`, for the stream wrappers and input dispatchers; see
  [crate layout](../../projects/hypershell/architecture/crate-layout.md). The inversion argument holds.
- **The install snippet pins `cgp = "0.4.1"` and `hypershell = "0.1.0"`.** Hypershell tracks `cgp`
  0.8.0.
- **One claim has been overtaken.** The post offers AI editors "getting pretty good at deciphering the
  error messages" as the practical answer to CGP's diagnostics;
  [`cargo-cgp`](../../cargo-cgp/README.md), which rewrites the common wiring errors, is now the better
  one.
- **The "no simple tutorials" caveat is obsolete.** The post argues tutorials are not the priority
  because CGP's benefits only show past 5,000 lines; two tutorial series now exist, in
  [tutorials/](../tutorials/README.md).

## Maintaining it

Leave it alone, and do not attempt a syntax refresh: the preset architecture it traces does not
translate line by line into namespaces, so a partial update would be worse than none. A current
Hypershell article would be a new post, under the
[conference talk and deep-dive playbooks](../../communication-strategy/formats.md), carrying forward
the prototypal-inheritance bridge and the disadvantages section, the reason readers trust the rest.
