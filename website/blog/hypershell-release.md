# Hypershell: A Type-Level DSL for Shell-Scripting in Rust

The longest post on the site — roughly 16,500 words — announcing [Hypershell](../../projects/hypershell/README.md)
and using it to teach, in one pass, both the type-level DSL technique and CGP's whole wiring model. It
remains the fullest written account of building a DSL whose programs are Rust types, and its
self-contained CGP introduction is still one of the best on the site, but its wiring code is two
breaking releases out of date.

- **URL** — <https://contextgeneric.dev/blog/hypershell-release>
- **Source** — [blog/2025-06-14-hypershell-release/index.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2025-06-14-hypershell-release/index.md)
- **Published** — 14 June 2025, tagged `release` and `deepdive`
- **Status** — Historical

## What it covers

The post has five parts, and its own table of contents estimates one to two hours of reading.

The **overview** teaches Hypershell by example. A program is a Rust *type* written with the
`hypershell!` macro, whose shell-like surface syntax — a pipe operator, bracketed variadic argument
lists, bare string literals — desugars into `Pipe<Product![...]>` over `Symbol!` type-level strings.
It works through hello world, then variable parameters via `FieldArg<"name">` read from a custom
context, then streaming execution that pipes one child process's `STDOUT` into the next's `STDIN`,
then a native `reqwest`-backed HTTP handler replacing `curl` in the same pipeline, and finally JSON
encoding and decoding around an HTTP request to the Rust Playground API.

The **CGP introduction** is a self-contained primer: the consumer/provider trait split, why a unique
`Self` type escapes coherence, and how `delegate_components!` builds a type-level lookup table. Its
distinctive move is a sustained comparison to **JavaScript prototypal inheritance**, with side-by-side
diagrams, arguing that CGP's wiring is prototype lookup resolved at compile time.

The **implementation** section is the technical core. A syntax type like
`SimpleExec<CommandPath, Args>` is a bare `PhantomData` struct with no impls — abstract syntax, wholly
decoupled from how it is interpreted. A provider then implements `Handler` for that shape,
pattern-matching the `Code` parameter to destructure it, and pulls everything it needs from the
context by dependency injection: `CanExtractCommandArg` for the command path, `CanUpdateCommand` for
the arguments, `CanRaiseError<std::io::Error>` and `CanWrapError<CommandNotFound>` for failures. The
section makes an argument about crate structure that generalizes well beyond DSLs: because CGP starts
from abstract implementations and names concrete types last, the dependency graph inverts, and
`hypershell-tokio-components` can build without `reqwest` in its tree.

The **extension** section adds two new syntaxes — `Checksum<Hasher>` and `BytesToHex` — with their
providers and a preset that layers them onto the base language, making the point that a language
extension needs no upstream coordination and no fork.

The **discussion** section is unusually candid. It names the steep learning curve, the poor error
messages, the impossibility of dynamic loading, and slow compilation of executables as real costs;
compares the approach to [tagless final](https://okmij.org/ftp/tagless-final/) and to Haskell's
[Servant](https://www.servant.dev/posts/2018-07-12-servant-dsl-typelevel.html); and sketches future
DSLs for lambda calculus, HTML, parsers, and monadic computation.

## How it relates to the knowledge base

The technique the post teaches is [type-level DSLs](../../cgp/concepts/type-level-dsls.md), and the
running scenario is re-derived in current syntax as the
[shell-scripting DSL example](../../examples/shell-scripting-dsl.md) — **that example, not this post,
is the source to quote from.** The project itself is documented in
[projects/hypershell/](../../projects/hypershell/README.md).

On the CGP side the post touches most of the base:
[consumer and provider traits](../../cgp/concepts/consumer-and-provider-traits.md) and
[coherence](../../cgp/concepts/coherence.md) for the split;
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md) and
[`DelegateComponent`](../../cgp/reference/traits/delegate_component.md) for the table;
[`Handler`](../../cgp/reference/components/handler.md) and the
[handler family](../../cgp/concepts/handlers.md) for the component;
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md) for the `where`-clause
injection; [modular error handling](../../cgp/concepts/modular-error-handling.md) with
[`CanRaiseError` / `CanWrapError`](../../cgp/reference/components/can_raise_error.md);
[dispatching](../../cgp/concepts/dispatching.md) with
[`UseDelegate`](../../cgp/reference/providers/use_delegate.md); and
[`PipeHandlers`](../../cgp/reference/providers/handler_combinators.md) for the composed pipeline.
`Symbol!` and `Product!` are [`Symbol!`](../../cgp/reference/macros/symbol.md) and
[`Product!`](../../cgp/reference/macros/product.md).

Two of its arguments are strategy assets rather than technical ones. The prototypal-inheritance
comparison is a genuine teaching bridge for the OOP-background reader in
[readers.md](../../communication-strategy/readers.md), and belongs in the toolkit
[readers.md](../../communication-strategy/readers.md#the-comprehension-barriers) assembles — with the
caveat the post itself states, that the lookup is compile-time and zero-cost, which
[vocabulary.md](../../communication-strategy/vocabulary.md) requires be said explicitly whenever a
runtime-flavored analogy is used. The candid disadvantages section is a model of the
concede-the-costs discipline [message.md](../../communication-strategy/message.md#the-objections-readers-bring) prescribes,
and the compile-time observations in it are among the few concrete statements the project has made on
that topic.

## Where it diverges from CGP v0.8.0

The post's *ideas* are current; its *wiring code* is uniformly stale. It was written against CGP
v0.4.1 and predates three breaking releases.

- **`#[cgp_context(MyAppComponents: HypershellPreset)]` no longer exists.** Both the macro and the
  `HasProvider`/`HasCgpProvider` trait it generated were removed. A context now carries its own
  wiring table, and namespace inheritance replaces preset inheritance. Every context definition in
  the post — `MyApp`, `HypershellCli`, `HypershellHttp` — is dead syntax.
- **The whole preset system is gone.** `cgp_preset!`, `#[cgp::re_export_imports]`, `override`,
  `#[wrap_provider(UseDelegate)]`, and `Preset::Provider` were replaced by
  [namespaces](../../cgp/concepts/namespaces.md). The post's four-level preset delegation trace —
  `HypershellPreset` → `HypershellHandlerPreset` → `TokioHandlerPreset` → `HandleSimpleExec` — is an
  accurate description of a mechanism that no longer exists.
- **`HasAsyncErrorType` and the `Async` trait were removed** in v0.5.0. `CanHandle`'s `Send` bounds
  come from elsewhere now; see [send-bounds](../../cgp/concepts/send-bounds.md).
- **Every provider is written inside-out** with `#[cgp_new_provider]` and an explicit
  `context: &Context` first parameter. The current form is
  [`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md) with `self`.
- **Dependencies are hand-written `where` bounds.** `Context: CanExtractCommandArg<CommandPath> + ...`
  would today be [`#[uses(...)]`](../../cgp/reference/attributes/uses.md), and context fields would be
  read with [`#[implicit]`](../../cgp/reference/attributes/implicit.md) arguments rather than getter
  traits.
- **`UseDelegate` tables are the legacy dispatch form**, superseded by the `open` statement per
  [dispatching-per-type](../../cgp/guides/dispatching-per-type.md).
- **The install snippet pins `cgp = "0.4.1"` and `hypershell = "0.1.0"`.** Hypershell itself now
  tracks `cgp` 0.8.0-alpha.
- **One claim has been overtaken.** The post says AI editors "are getting pretty good at deciphering
  the error messages" as the practical answer to CGP's diagnostics. That is now the second-best
  answer: [`cargo-cgp`](../../cargo-cgp/README.md) rewrites the common wiring errors directly.
- **The "no simple tutorials" caveat is obsolete.** The post explains at length that tutorials are
  not the priority because CGP's benefits only show past 5,000 lines. Two tutorial series now exist;
  see [tutorials/](../tutorials/README.md).

## Maintaining it

Leave it alone, and do not attempt a syntax refresh — the preset architecture it traces in detail is
not translatable line-by-line into namespaces, so a partial update would be worse than none. When
current material on this subject is needed, write from the
[shell-scripting DSL example](../../examples/shell-scripting-dsl.md) and
[type-level DSLs](../../cgp/concepts/type-level-dsls.md) instead.

If the project ever wants a current Hypershell article, the honest framing is a new post rather than a
revision, and the [conference talk and deep-dive playbooks](../../communication-strategy/formats.md)
apply. Two things from this post are worth carrying into any successor: the prototypal-inheritance
bridge, and the disadvantages section, which is the reason readers trust the rest of it.
